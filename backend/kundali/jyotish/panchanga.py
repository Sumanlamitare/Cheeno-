"""Birth Panchanga: Tithi, Vara, Nakshatra, Yoga, Karana, plus sunrise-based
Ishta Kala (birth time in ghati-pala from sunrise) and the lunar month."""

from __future__ import annotations

import math

from ..astro import ephemeris as eph
from .chart import NatalChart
from .constants import (
    LUNAR_MONTHS,
    MOVABLE_KARANAS,
    NAKSHATRA_SPAN,
    NAKSHATRAS,
    TITHIS,
    VARA_ENGLISH,
    VARA_LORDS,
    VARAS,
    YOGAS_27,
    nakshatra_lord,
)

TITHI_GROUPS = ["Nanda", "Bhadra", "Jaya", "Rikta", "Purna"]


def tithi_index(sun_lon: float, moon_lon: float) -> tuple[int, float]:
    """Tithi number 1..30 and the fraction of it elapsed."""
    elong = (moon_lon - sun_lon) % 360.0
    return int(elong // 12) + 1, (elong % 12) / 12


def tithi_name(n: int) -> tuple[str, str]:
    paksha = "Shukla" if n <= 15 else "Krishna"
    k = (n - 1) % 15
    if k == 14:
        name = "Purnima" if n == 15 else "Amavasya"
    else:
        name = TITHIS[k]
    return paksha, name


def yoga_index(sun_lon: float, moon_lon: float) -> int:
    return int(((sun_lon + moon_lon) % 360.0) // NAKSHATRA_SPAN)


def karana_name(sun_lon: float, moon_lon: float) -> str:
    k = int(((moon_lon - sun_lon) % 360.0) // 6)  # 0..59
    if k == 0:
        return "Kimstughna"
    if k == 57:
        return "Shakuni"
    if k == 58:
        return "Chatushpada"
    if k == 59:
        return "Naga"
    return MOVABLE_KARANAS[(k - 1) % 7]


def weekday_from_jd(jd_local: float) -> int:
    """0 = Sunday."""
    return int((math.floor(jd_local + 0.5) + 1) % 7)


def _elongation(jd, settings):
    return (eph.sidereal_longitude(jd, "Moon", settings) - eph.sidereal_longitude(jd, "Sun", settings)) % 360.0


def _new_moon_near(jd_guess: float, settings) -> float:
    return eph.find_crossing(lambda x: _elongation(x, settings), 0.0, jd_guess - 3, jd_guess + 3)


def lunar_month(chart: NatalChart) -> dict:
    s = chart.settings
    elong = _elongation(chart.jd, s)
    prev_nm = _new_moon_near(chart.jd - elong / 12.19, s)
    if prev_nm > chart.jd:
        prev_nm = _new_moon_near(prev_nm - 29.53, s)
    next_nm = _new_moon_near(prev_nm + 29.53, s)
    s1 = int(eph.sidereal_longitude(prev_nm, "Sun", s) // 30)
    s2 = int(eph.sidereal_longitude(next_nm, "Sun", s) // 30)
    amanta = (s1 + 1) % 12
    adhika = s1 == s2
    tithi, _ = tithi_index(chart.planets["Sun"].longitude, chart.planets["Moon"].longitude)
    # Purnimanta reckoning (used in Nepal): the dark fortnight is named after
    # the following month.
    purnimanta = amanta if tithi <= 15 else (amanta + 1) % 12
    prefix = "Adhika " if adhika else ""
    return {
        "amanta": prefix + LUNAR_MONTHS[amanta],
        "purnimanta": (prefix if tithi <= 15 else "") + LUNAR_MONTHS[purnimanta],
        "adhika": adhika,
    }


def sunrise_info(chart: NatalChart) -> dict | None:
    lat, lon, jd = chart.latitude, chart.longitude, chart.jd
    sr = eph.sun_rise_set(jd - 1.2, lat, lon, rise=True)
    if sr is None:
        return None
    if sr > jd:
        sr = eph.sun_rise_set(jd - 2.2, lat, lon, rise=True)
        if sr is None:
            return None
    nxt = eph.sun_rise_set(sr + 0.1, lat, lon, rise=True)
    while nxt is not None and nxt <= jd:
        sr, nxt = nxt, eph.sun_rise_set(nxt + 0.1, lat, lon, rise=True)
    ss = eph.sun_rise_set(sr, lat, lon, rise=False)
    if nxt is None or ss is None:
        return None
    return {"sunrise": sr, "sunset": ss, "nextSunrise": nxt, "isDay": sr <= jd < ss}


def compute_panchanga(chart: NatalChart) -> dict:
    sun = chart.planets["Sun"].longitude
    moon = chart.planets["Moon"].longitude
    t, frac = tithi_index(sun, moon)
    paksha, tname = tithi_name(t)
    y = yoga_index(sun, moon)
    nak = chart.planets["Moon"].nakshatra
    sun_info = sunrise_info(chart)
    warnings = []
    if sun_info:
        wd = weekday_from_jd(sun_info["sunrise"] + chart.longitude / 360.0)
        ishta = (chart.jd - sun_info["sunrise"]) * 60.0  # ghati
        gh = int(ishta)
        pala_f = (ishta - gh) * 60
        pala = int(pala_f)
        vipala = int((pala_f - pala) * 60)
        ishta_kala = {"ghati": gh, "pala": pala, "vipala": vipala,
                      "label": f"{gh} ghati {pala} pala {vipala} vipala"}
        sunrise_utc = eph.jd_to_datetime(sun_info["sunrise"]).isoformat()
        sunset_utc = eph.jd_to_datetime(sun_info["sunset"]).isoformat()
        day_birth = sun_info["isDay"]
    else:
        wd = weekday_from_jd(chart.jd + chart.longitude / 360.0)
        ishta_kala = None
        sunrise_utc = sunset_utc = None
        day_birth = None
        warnings.append("Sunrise could not be determined at this latitude; the civil weekday is used for Vara.")
    month = lunar_month(chart)
    return {
        "tithi": {
            "number": t,
            "paksha": paksha,
            "name": tname,
            "label": f"{paksha} {tname}",
            "elapsed": round(frac, 4),
            "group": TITHI_GROUPS[(t - 1) % 5] if (t - 1) % 15 != 14 else "Purna",
        },
        "vara": {
            "index": wd,
            "name": VARAS[wd],
            "english": VARA_ENGLISH[wd],
            "lord": VARA_LORDS[wd],
        },
        "nakshatra": {
            "index": nak,
            "name": NAKSHATRAS[nak],
            "pada": chart.planets["Moon"].pada,
            "lord": nakshatra_lord(nak),
        },
        "yoga": {"index": y, "name": YOGAS_27[y]},
        "karana": {"name": karana_name(sun, moon)},
        "lunarMonth": month,
        "sunriseUtc": sunrise_utc,
        "sunsetUtc": sunset_utc,
        "dayBirth": day_birth,
        "ishtaKala": ishta_kala,
        "warnings": warnings,
        "_sun": sun_info,
    }
