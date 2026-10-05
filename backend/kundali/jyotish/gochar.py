"""Gochar (transits) counted from the natal Moon sign, with Vedha.

Favourable houses from the Moon and their Vedha (obstruction) points follow
Phaladeepika ch. 26 / Muhurta Chintamani. A favourable transit is obstructed
when another planet simultaneously transits the corresponding Vedha house.
By tradition there is no Vedha between the Sun and Saturn, nor between the
Moon and Mercury.
"""

from __future__ import annotations

import datetime as dt

from ..astro import ephemeris as eph
from ..config import CalculationSettings
from .chart import NatalChart, nakshatra_of
from .constants import NAKSHATRAS, PLANETS, RASHIS, house_from

# planet -> {favourable house: vedha house}
GOCHAR_VEDHA = {
    "Sun": {3: 9, 6: 12, 10: 4, 11: 5},
    "Moon": {1: 5, 3: 9, 6: 12, 7: 2, 10: 4, 11: 8},
    "Mars": {3: 12, 6: 9, 11: 5},
    "Mercury": {2: 5, 4: 3, 6: 9, 8: 1, 10: 8, 11: 12},
    "Jupiter": {2: 12, 5: 4, 7: 3, 9: 10, 11: 8},
    "Venus": {1: 8, 2: 7, 3: 1, 4: 10, 5: 9, 8: 5, 9: 11, 11: 6, 12: 3},
    "Saturn": {3: 12, 6: 9, 11: 5},
    "Rahu": {3: 12, 6: 9, 11: 5},
    "Ketu": {3: 12, 6: 9, 11: 5},
}
NO_VEDHA_PAIRS = {frozenset({"Sun", "Saturn"}), frozenset({"Moon", "Mercury"})}

MAJOR_TRANSIT_PLANETS = ["Saturn", "Jupiter", "Rahu", "Ketu"]


def transit_positions(moment: dt.datetime, settings: CalculationSettings) -> dict:
    jd = eph.julian_day(moment)
    out = {}
    for p in PLANETS:
        pos = eph.body_position(jd, p, settings)
        nak, pada = nakshatra_of(pos.longitude)
        out[p] = {
            "longitude": pos.longitude,
            "sign": int(pos.longitude // 30),
            "degree": pos.longitude % 30,
            "retrograde": pos.speed < 0 if p not in ("Rahu", "Ketu") else True,
            "nakshatra": nak,
            "pada": pada,
        }
    return {"jd": jd, "positions": out}


def compute_gochar(chart: NatalChart, moment: dt.datetime) -> dict:
    settings = chart.settings
    tp = transit_positions(moment, settings)
    pos = tp["positions"]
    moon_sign = chart.planets["Moon"].sign
    from_moon = {p: house_from(moon_sign, pos[p]["sign"]) for p in PLANETS}

    rows = []
    for p in PLANETS:
        h_moon = from_moon[p]
        h_lagna = house_from(chart.lagna_sign, pos[p]["sign"])
        fav_map = GOCHAR_VEDHA[p]
        favourable = h_moon in fav_map
        vedha_by = []
        if favourable:
            vh = fav_map[h_moon]
            for q in PLANETS:
                if q == p or frozenset({p, q}) in NO_VEDHA_PAIRS:
                    continue
                if from_moon[q] == vh:
                    vedha_by.append(q)
        # Natal planets conjoined by transit (same sign).
        natal_in_sign = [q for q in PLANETS if chart.planets[q].sign == pos[p]["sign"]]
        rows.append({
            "planet": p,
            "sign": pos[p]["sign"],
            "signName": RASHIS[pos[p]["sign"]],
            "degree": round(pos[p]["degree"], 4),
            "longitude": round(pos[p]["longitude"], 4),
            "retrograde": pos[p]["retrograde"],
            "nakshatra": NAKSHATRAS[pos[p]["nakshatra"]],
            "pada": pos[p]["pada"],
            "houseFromMoon": h_moon,
            "houseFromLagna": h_lagna,
            "favourable": favourable,
            "vedhaBy": vedha_by,
            "result": ("favourable" if favourable and not vedha_by
                       else "obstructed" if favourable else "challenging"),
            "natalPlanetsInSign": natal_in_sign,
            "major": p in MAJOR_TRANSIT_PLANETS,
        })

    # Upcoming sign changes of the slow planets (next ~3 years).
    upcoming = []
    for p in ("Jupiter", "Saturn", "Rahu"):
        events = eph.sign_ingresses(p, tp["jd"], tp["jd"] + 365.25 * 3, settings)
        for e in events[:4]:
            to_sign = e["toSign"]
            upcoming.append({
                "planet": p,
                "date": eph.jd_to_datetime(e["jd"]).isoformat(),
                "toSign": to_sign,
                "toSignName": RASHIS[to_sign],
                "houseFromMoon": house_from(moon_sign, to_sign),
                "houseFromLagna": house_from(chart.lagna_sign, to_sign),
            })
            if p == "Rahu":
                k_sign = (to_sign + 6) % 12
                upcoming.append({
                    "planet": "Ketu",
                    "date": eph.jd_to_datetime(e["jd"]).isoformat(),
                    "toSign": k_sign,
                    "toSignName": RASHIS[k_sign],
                    "houseFromMoon": house_from(moon_sign, k_sign),
                    "houseFromLagna": house_from(chart.lagna_sign, k_sign),
                })
    upcoming.sort(key=lambda x: x["date"])
    return {"asOf": moment.isoformat(), "rows": rows, "upcomingIngresses": upcoming}


def planet_sign_periods(planet: str, sign: int, start: dt.datetime, end: dt.datetime,
                        settings: CalculationSettings) -> list[dict]:
    """Periods during [start, end] when a transiting planet occupies `sign`."""
    jd0, jd1 = eph.julian_day(start), eph.julian_day(end)
    events = eph.sign_ingresses(planet, jd0, jd1, settings)
    periods = []
    cur_in = int(eph.sidereal_longitude(jd0, planet, settings) // 30) == sign
    cur_start = jd0 if cur_in else None
    for e in events:
        if e["toSign"] == sign:
            cur_start = e["jd"]
        elif e["fromSign"] == sign and cur_start is not None:
            periods.append((cur_start, e["jd"]))
            cur_start = None
    if cur_start is not None:
        periods.append((cur_start, jd1))
    return [{"start": eph.jd_to_datetime(a), "end": eph.jd_to_datetime(b)} for a, b in periods]
