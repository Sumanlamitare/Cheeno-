"""Assembles the complete Janma Kundali report.

Layer 1 (inputs) -> Layer 2 (Swiss Ephemeris) -> Layer 3 (Jyotish
calculations) -> Layer 4 (rule-based interpretation) -> JSON for Layer 5
(presentation). The function is pure: the same birth data and the same
reference moment always produce the same report.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from ..astro import ephemeris as eph
from ..config import DEFAULT_SETTINGS, CalculationSettings
from ..inputs.calendar import resolve_date
from ..inputs.places import get_index, place_from_coordinates
from ..inputs.timeutil import localize, parse_time
from ..jyotish import dasha as dasha_mod
from ..jyotish.chart import build_chart
from ..jyotish.constants import PLANETS, RASHI_LORDS, RASHIS, format_dms
from ..jyotish.doshas import detect_doshas
from ..jyotish.gochar import compute_gochar
from ..jyotish.panchanga import compute_panchanga
from ..jyotish.sadesati import compute_sadesati
from ..jyotish.shadbala import compute_shadbala
from ..jyotish.vargas import SUPPORTED_VARGAS, VARGA_NAMES
from ..jyotish.yogas import detect_yogas
from ..rules import (career, children, dasha as dasha_rules, doshas as dosha_rules, education, family, health,
                     houses, lagna, marriage, nakshatra, panchanga as panchanga_rules, planets as planet_rules,
                     transits, travel, vargas as varga_rules, wealth)
from ..rules import yogas as yoga_rules
from ..rules.engine import ChartContext
from .explain import explain
from ..rules.personal import personal_answers

DISCLAIMER = ("Jyotish is a traditional astrological system. Its interpretations are cultural and spiritual "
              "frameworks and are not scientifically validated predictions. This reading should not replace "
              "professional medical, financial, legal or other expert advice.")

ACCURACY_NOTE = ("Accuracy depends on correct birth information, correct location, the correct historical "
                 "timezone, the astronomical ephemeris, the chosen ayanamsha, the formulas used and the Jyotish "
                 "rules applied. No accuracy percentage is claimed.")


class InputError(ValueError):
    def __init__(self, field: str, message: str):
        super().__init__(message)
        self.field = field
        self.message = message


@dataclass
class BirthInput:
    date: str
    calendar: str
    time: str
    meridiem: str | None = None
    time_accuracy: str = "exact"
    name: str | None = None
    place_id: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    place_label: str | None = None
    utc_offset_override: float | None = None


def _iso(obj):
    if isinstance(obj, dict):
        return {k: _iso(v) for k, v in obj.items() if not k.startswith("_")}
    if isinstance(obj, list):
        return [_iso(v) for v in obj]
    if isinstance(obj, dt.datetime):
        return obj.isoformat()
    if isinstance(obj, dt.date):
        return obj.isoformat()
    if isinstance(obj, float):
        return round(obj, 6)
    return obj


def resolve_inputs(b: BirthInput) -> dict:
    from ..inputs.calendar import CalendarError
    from ..inputs.places import PlaceError
    from ..inputs.timeutil import TimeInputError

    try:
        date_info = resolve_date(b.calendar, b.date)
    except CalendarError as e:
        raise InputError("date", str(e)) from e
    try:
        time = parse_time(b.time, b.meridiem)
    except TimeInputError as e:
        raise InputError("time", str(e)) from e
    try:
        if b.place_id:
            place = get_index().get(b.place_id)
        elif b.latitude is not None and b.longitude is not None:
            place = place_from_coordinates(b.latitude, b.longitude, b.place_label)
        else:
            raise PlaceError("Please select a specific city or location.")
    except PlaceError as e:
        raise InputError("place", str(e)) from e
    try:
        tz = localize(date_info["ad"], time, place.timezone, place.longitude, b.utc_offset_override)
    except TimeInputError as e:
        raise InputError("place", str(e)) from e
    if not eph.MIN_YEAR <= date_info["ad"].year <= eph.MAX_YEAR:
        raise InputError("date", f"Birth dates between {eph.MIN_YEAR} and {eph.MAX_YEAR} AD are supported.")
    return {"date": date_info, "time": time, "place": place, "tz": tz}


def generate(b: BirthInput, now: dt.datetime | None = None,
             settings: CalculationSettings = DEFAULT_SETTINGS) -> dict:
    now = now or dt.datetime.now(dt.timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=dt.timezone.utc)
    inp = resolve_inputs(b)
    place, tz = inp["place"], inp["tz"]
    utc = tz["utc"]
    if utc > now:
        raise InputError("date", "The birth date and time are in the future.")

    # ---- Layer 2 + 3: calculations --------------------------------------
    chart = build_chart(utc, place.latitude, place.longitude, settings)
    panchanga = compute_panchanga(chart)
    shadbala = compute_shadbala(chart, panchanga.get("_sun"))
    yogas = detect_yogas(chart)
    doshas = detect_doshas(chart)
    vim = dasha_mod.vimshottari(chart.planets["Moon"].longitude, utc, settings.dasha_year_days, levels=3)
    chain = dasha_mod.find_active(vim["periods"], now)
    gochar = compute_gochar(chart, now)
    sadesati = compute_sadesati(chart, now)

    # ---- Layer 4: interpretation ----------------------------------------
    ctx = ChartContext(chart=chart, yogas=yogas, doshas=doshas, shadbala=shadbala,
                       dasha={k: p["lord"] for k, p in zip(("MD", "AD", "PD"), chain)}, gochar=gochar)
    tree = vim["periods"]
    interp = {
        "lagna": lagna.analyze(ctx),
        "moon": nakshatra.analyze(ctx),
        "planets": planet_rules.analyze(ctx),
        "houses": houses.analyze(ctx),
        "career": career.analyze(ctx, tree, now),
        "wealth": wealth.analyze(ctx, tree, now),
        "education": education.analyze(ctx, tree, now),
        "marriage": marriage.analyze(ctx, tree, now, utc),
        "family": family.analyze(ctx),
        "travel": travel.analyze(ctx, tree, now),
        "children": children.analyze(ctx),
        "health": health.analyze(ctx),
        "yogas": yoga_rules.analyze(ctx),
        "doshas": dosha_rules.analyze(ctx),
        "currentDasha": dasha_rules.analyze(ctx, gochar, sadesati) if chain else None,
        "gochar": transits.interpret_gochar(ctx, gochar),
        "sadesati": transits.interpret_sadesati(ctx, sadesati),
        "d9": varga_rules.analyze_d9(ctx),
        "d10": varga_rules.analyze_d10(ctx),
        "panchanga": panchanga_rules.explain(panchanga),
    }
    interp["personal"] = personal_answers(ctx, interp)

    # ---- Assemble -------------------------------------------------------
    moon = chart.planets["Moon"]
    asc = chart.ascendant
    current = [{"level": lvl, "lord": p["lord"], "start": p["start"].isoformat(), "end": p["end"].isoformat()}
               for lvl, p in zip(("Mahadasha", "Antardasha", "Pratyantardasha"), chain)]
    warnings = list(tz["warnings"]) + panchanga.get("warnings", [])
    if b.time_accuracy == "approximate":
        warnings.insert(0, "Birth time reported as approximate. The Lagna, houses, divisional charts and Dasha "
                           "dates may shift with the true birth time.")
    if chart.ephemeris_source != "Swiss Ephemeris":
        warnings.append("Swiss Ephemeris data files were not found; the built-in Moshier ephemeris was used.")
    if abs(place.latitude) > 60:
        warnings.append("At high latitudes the Ascendant changes very quickly and whole-sign houses are sensitive to "
                        "small errors in birth time.")

    asc_deg_to_edge = min(asc.degree, 30 - asc.degree)
    if asc_deg_to_edge < 1:
        warnings.append(f"The Ascendant is within {asc_deg_to_edge * 60:.0f} arc-minutes of a sign boundary; a small "
                        "error in birth time could change the Lagna.")

    report = {
        "meta": {
            "generatedAt": now.isoformat(),
            "application": "Janma Kundali (deterministic, rule-based)",
            "version": "1.0.0",
        },
        "birth": {
            "name": (b.name or "").strip() or None,
            "date": inp["date"]["display"],
            "inputCalendar": inp["date"]["inputCalendar"],
            "time": inp["time"].strftime("%H:%M:%S"),
            "time12": inp["time"].strftime("%I:%M:%S %p"),
            "timeAccuracy": b.time_accuracy,
            "place": place.to_dict(),
            "timezone": {k: v for k, v in tz.items() if k not in ("utc", "local")},
            "utc": utc.isoformat(),
            "julianDay": round(chart.jd, 6),
        },
        "summary": {
            "lagna": RASHIS[chart.lagna_sign],
            "lagnaDegree": format_dms(asc.degree),
            "lagnaLord": RASHI_LORDS[chart.lagna_sign],
            "janmaRashi": RASHIS[moon.sign],
            "nakshatra": moon.nakshatra_name,
            "pada": moon.pada,
            "nakshatraLord": moon.nakshatra_lord,
            "currentMahadasha": chain[0]["lord"] if chain else None,
            "currentAntardasha": chain[1]["lord"] if len(chain) > 1 else None,
            "currentPratyantardasha": chain[2]["lord"] if len(chain) > 2 else None,
            "sadeSati": sadesati["status"],
            "sunSign": RASHIS[chart.planets["Sun"].sign],
        },
        "chart": {
            "ascendant": asc.to_dict(),
            "planets": [chart.planets[p].to_dict() for p in PLANETS],
            "houses": [{"house": h, "sign": chart.house_sign(h), "signName": RASHIS[chart.house_sign(h)],
                        "lord": chart.house_lord(h), "occupants": chart.occupants(h)} for h in range(1, 13)],
            "ayanamsha": round(chart.ayanamsha, 6),
            "ayanamshaLabel": format_dms(chart.ayanamsha),
            "mc": round(chart.mc, 6),
            "vargas": {
                str(d): {
                    "division": d, "name": VARGA_NAMES[d][0], "purpose": VARGA_NAMES[d][1],
                    "lagna": asc.vargas[str(d)]["sign"],
                    "planets": {p: chart.planets[p].vargas[str(d)] for p in PLANETS},
                }
                for d in SUPPORTED_VARGAS
            },
        },
        "panchanga": panchanga,
        "shadbala": shadbala,
        "yogas": [y.to_dict() for y in yogas],
        "doshas": doshas,
        "dasha": {
            "system": "Vimshottari",
            "startingLord": vim["startingLord"],
            "balanceAtBirth": vim["balance"],
            "balanceYears": round(vim["balanceYears"], 4),
            "yearDays": vim["yearDays"],
            "current": current,
            "periods": dasha_mod.serialize(tree, now, utc, settings.dasha_year_days),
        },
        "gochar": gochar,
        "sadesati": sadesati,
        "interpretation": interp,
        "calculation": {
            **settings.describe(),
            "ephemeris": chart.ephemeris_source,
            "ayanamshaValue": format_dms(chart.ayanamsha),
            "location": place.label,
            "latitude": place.latitude,
            "longitude": place.longitude,
            "timezone": tz["tzName"],
            "utcOffset": tz["offsetLabel"],
            "dst": tz["dst"],
            "timezoneMethod": tz["method"],
            "sunrise": "Hindu sunrise (centre of the Sun's disc, no refraction)",
            "houseAssessment": houses.ASSESSMENT_METHOD,
            "accuracyNote": ACCURACY_NOTE,
        },
        "warnings": warnings,
        "disclaimer": DISCLAIMER,
    }
    out = _iso(report)
    out["explained"] = _iso(explain(out))
    return out
