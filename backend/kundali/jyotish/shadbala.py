"""Shadbala - six-fold planetary strength (BPHS ch. 27; B. V. Raman,
"Graha and Bhava Balas").

All values are in virupas (60 virupas = 1 rupa). Methodology choices that
vary between authorities are documented inline and in METHOD_NOTES so the
calculation remains transparent.
"""

from __future__ import annotations

import math

from ..astro import ephemeris as eph
from . import vargas
from .chart import NatalChart
from .constants import (
    DEBILITATION,
    MOOLATRIKONA,
    NAISARGIKA_BALA,
    OWN_SIGNS,
    RASHI_LORDS,
    SEVEN_PLANETS,
    SHADBALA_REQUIRED_RUPAS,
    VARA_LORDS,
    is_odd_sign,
)
from .dignity import angular_distance, compound_relation
from .drishti import sphuta_drishti

METHOD_NOTES = [
    "Uccha Bala: arc from the debilitation point divided by 3 (max 60).",
    "Saptavargaja Bala over D1, D2, D3, D7, D9, D12, D30 using BPHS values "
    "(moolatrikona 45 in D1 only, own 30, great friend 20, friend 15, neutral 10, enemy 4, great enemy 2), "
    "with the compound relationship taken from the Rashi chart.",
    "Dig Bala: arc from the point of weakness divided by 3, using the actual Ascendant and Midheaven.",
    "Nathonnata Bala uses local apparent solar time; Paksha Bala of the Moon is doubled.",
    "Abda and Masa lords are the weekday lords beginning the current 360-day and 30-day periods "
    "counted from the Kali Yuga epoch (JD 588465.5, a Friday); Hora uses equal hours from sunrise.",
    "Ayana Bala: (24° ± declination) / 48° × 60; the Sun's Ayana Bala is doubled.",
    "Chesta Bala: Chesta Kendra = Seeghrocha − (mean + true longitude)/2, using the mean Sun and "
    "heliocentric positions from the Swiss Ephemeris; the Sun's Chesta Bala equals its Ayana Bala and "
    "the Moon's equals its Paksha Bala.",
    "Drik Bala: one quarter of (benefic − malefic) Sphuta Drishti received from the seven grahas.",
    "Yuddha Bala is applied when Mars, Mercury, Jupiter, Venus or Saturn are within 1° of longitude; "
    "the planet with the greater northern latitude wins.",
]

SAPTAVARGA = [1, 2, 3, 7, 9, 12, 30]
SAPTAVARGA_VALUES = {
    "moolatrikona": 45.0, "own": 30.0, "great friend": 20.0, "friend": 15.0,
    "neutral": 10.0, "enemy": 4.0, "great enemy": 2.0,
}
CHALDEAN = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
KALI_EPOCH_JD = 588465.5
KALI_EPOCH_WEEKDAY = 5  # Friday (0 = Sunday)
MALE = {"Sun", "Mars", "Jupiter"}
NEUTER = {"Mercury", "Saturn"}
FEMALE = {"Moon", "Venus"}


def _uccha(planet, lon):
    deb = DEBILITATION[planet][0] * 30 + DEBILITATION[planet][1]
    return angular_distance(lon, deb) / 3.0


def _saptavargaja(chart: NatalChart, planet: str) -> tuple[float, dict]:
    pl = chart.planets[planet]
    d1_signs = chart.planet_signs()
    total = 0.0
    detail = {}
    for div in SAPTAVARGA:
        vsign = vargas.varga_sign(pl.longitude, div)
        mt = MOOLATRIKONA.get(planet)
        if div == 1 and mt and mt[0] == pl.sign and mt[1] <= pl.degree < mt[2]:
            rel = "moolatrikona"
        elif vsign in OWN_SIGNS[planet]:
            rel = "own"
        else:
            lord = RASHI_LORDS[vsign]
            rel = compound_relation(planet, lord, d1_signs[planet], d1_signs[lord])
        total += SAPTAVARGA_VALUES[rel]
        detail[f"D{div}"] = rel
    return total, detail


def _ojayugma(planet, sign, navamsa_sign):
    want_even = planet in ("Moon", "Venus")
    v = 0.0
    for s in (sign, navamsa_sign):
        if is_odd_sign(s) != want_even:
            v += 15.0
    return v


def _kendradi(house):
    if house in (1, 4, 7, 10):
        return 60.0
    if house in (2, 5, 8, 11):
        return 30.0
    return 15.0


def _drekkana(planet, degree):
    dk = int(degree // 10)
    if planet in MALE and dk == 0:
        return 15.0
    if planet in NEUTER and dk == 1:
        return 15.0
    if planet in FEMALE and dk == 2:
        return 15.0
    return 0.0


def _dig(chart: NatalChart, planet: str) -> float:
    asc, mc = chart.ascendant.longitude, chart.mc
    weak = {
        "Sun": (mc + 180) % 360, "Mars": (mc + 180) % 360,
        "Jupiter": (asc + 180) % 360, "Mercury": (asc + 180) % 360,
        "Moon": mc, "Venus": mc,
        "Saturn": asc,
    }[planet]
    return angular_distance(chart.planets[planet].longitude, weak) / 3.0


def _weekday(jd_local):
    return int((math.floor(jd_local + 0.5) + 1) % 7)


def compute_shadbala(chart: NatalChart, sun_info: dict | None) -> dict | None:
    if sun_info is None:
        return None
    s = chart.settings
    jd = chart.jd
    planets = chart.planets
    sun_lon, moon_lon = planets["Sun"].longitude, planets["Moon"].longitude

    # ---- time-based inputs ---------------------------------------------
    eot_days = eph.equation_of_time(jd)
    lat_hours = ((jd + 0.5) % 1.0) * 24 + chart.longitude / 15.0 + eot_days * 24
    lat_hours %= 24
    from_midnight = lat_hours if lat_hours <= 12 else 24 - lat_hours  # 0..12

    elong = angular_distance(moon_lon, sun_lon)  # 0..180

    sunrise, sunset, next_sr = sun_info["sunrise"], sun_info["sunset"], sun_info["nextSunrise"]
    is_day = sunrise <= jd < sunset
    if is_day:
        third = int((jd - sunrise) / ((sunset - sunrise) / 3))
        tribhaga_lord = ["Mercury", "Sun", "Saturn"][min(third, 2)]
    else:
        third = int((jd - sunset) / ((next_sr - sunset) / 3))
        tribhaga_lord = ["Moon", "Venus", "Mars"][min(third, 2)]

    local_sr = sunrise + chart.longitude / 360.0
    vara_lord = VARA_LORDS[_weekday(local_sr)]
    hora_n = int((jd - sunrise) * 24)
    hora_lord = CHALDEAN[(CHALDEAN.index(vara_lord) + hora_n) % 7]
    ahargana = math.floor(local_sr + 0.5) - math.floor(KALI_EPOCH_JD + 0.5)
    abda_lord = VARA_LORDS[(KALI_EPOCH_WEEKDAY + 360 * (ahargana // 360)) % 7]
    masa_lord = VARA_LORDS[(KALI_EPOCH_WEEKDAY + 30 * (ahargana // 30)) % 7]

    mean_sun = eph.mean_sun_longitude(jd, s)

    signs = chart.planet_signs()
    is_benefic = {p: planets[p].benefic for p in SEVEN_PLANETS}

    results = {}
    for p in SEVEN_PLANETS:
        pl = planets[p]
        uccha = _uccha(p, pl.longitude)
        sapta, sapta_detail = _saptavargaja(chart, p)
        oja = _ojayugma(p, pl.sign, vargas.varga_sign(pl.longitude, 9))
        kendra = _kendradi(pl.house)
        drek = _drekkana(p, pl.degree)
        sthana = uccha + sapta + oja + kendra + drek

        dig = _dig(chart, p)

        if p == "Mercury":
            natonnata = 60.0
        elif p in ("Sun", "Jupiter", "Venus"):
            natonnata = from_midnight * 5.0
        else:
            natonnata = 60.0 - from_midnight * 5.0

        if p == "Moon":
            paksha = 2 * elong / 3.0
        elif is_benefic[p]:
            paksha = elong / 3.0
        else:
            paksha = (180.0 - elong) / 3.0

        tribhaga = 60.0 if (p == "Jupiter" or p == tribhaga_lord) else 0.0
        abda = 15.0 if p == abda_lord else 0.0
        masa = 30.0 if p == masa_lord else 0.0
        vara = 45.0 if p == vara_lord else 0.0
        hora = 60.0 if p == hora_lord else 0.0

        dec = pl.declination
        if p in ("Sun", "Mars", "Jupiter", "Venus"):
            ayana = (24.0 + dec) / 48.0 * 60.0
        elif p in ("Moon", "Saturn"):
            ayana = (24.0 - dec) / 48.0 * 60.0
        else:
            ayana = (24.0 + abs(dec)) / 48.0 * 60.0
        ayana = max(0.0, min(ayana, 60.0))
        if p == "Sun":
            ayana *= 2

        kala = natonnata + paksha + tribhaga + abda + masa + vara + hora + ayana

        if p == "Sun":
            chesta = ayana / 2  # Sun's chesta equals its (undoubled) Ayana Bala
        elif p == "Moon":
            chesta = paksha / 2  # Moon's chesta equals its (undoubled) Paksha Bala
        else:
            helio = eph.heliocentric_longitude(jd, p, s)
            if p in ("Mercury", "Venus"):
                mean, seeghrocha = mean_sun, helio
            else:
                mean, seeghrocha = helio, mean_sun
            true = pl.longitude
            avg = (mean + ((true - mean + 180) % 360 - 180) / 2) % 360
            ck = (seeghrocha - avg) % 360
            if ck > 180:
                ck = 360 - ck
            chesta = ck / 3.0

        naisargika = NAISARGIKA_BALA[p]

        drik_sum = 0.0
        for q in SEVEN_PLANETS:
            if q == p:
                continue
            v = sphuta_drishti(q, planets[q].longitude, pl.longitude)
            drik_sum += v if is_benefic[q] else -v
        drik = drik_sum / 4.0

        results[p] = {
            "sthana": {"total": sthana, "uccha": uccha, "saptavargaja": sapta, "ojayugma": oja,
                       "kendradi": kendra, "drekkana": drek, "saptavargaDetail": sapta_detail},
            "dig": dig,
            "kala": {"total": kala, "natonnata": natonnata, "paksha": paksha, "tribhaga": tribhaga,
                     "abda": abda, "masa": masa, "vara": vara, "hora": hora, "ayana": ayana, "yuddha": 0.0},
            "chesta": chesta,
            "naisargika": naisargika,
            "drik": drik,
        }

    # ---- Yuddha (planetary war) ------------------------------------------
    war = []
    combatants = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    for i, a in enumerate(combatants):
        for b in combatants[i + 1:]:
            if angular_distance(planets[a].longitude, planets[b].longitude) < 1.0:
                winner, loser = (a, b) if planets[a].latitude > planets[b].latitude else (b, a)

                def partial(x):
                    r = results[x]
                    return r["sthana"]["total"] + r["dig"] + r["kala"]["total"]

                diff = abs(partial(winner) - partial(loser))
                results[winner]["kala"]["yuddha"] += diff
                results[winner]["kala"]["total"] += diff
                results[loser]["kala"]["yuddha"] -= diff
                results[loser]["kala"]["total"] -= diff
                war.append({"winner": winner, "loser": loser})

    out = {}
    for p, r in results.items():
        total = r["sthana"]["total"] + r["dig"] + r["kala"]["total"] + r["chesta"] + r["naisargika"] + r["drik"]
        rupas = total / 60.0
        required = SHADBALA_REQUIRED_RUPAS[p]
        out[p] = {
            "components": _round(r),
            "totalVirupas": round(total, 2),
            "rupas": round(rupas, 2),
            "requiredRupas": required,
            "ratio": round(rupas / required, 3),
            "sufficient": rupas >= required,
        }
    ranking = sorted(out, key=lambda p: -out[p]["ratio"])
    return {
        "planets": out,
        "ranking": ranking,
        "planetaryWar": war,
        "inputs": {
            "varaLord": vara_lord, "horaLord": hora_lord, "abdaLord": abda_lord, "masaLord": masa_lord,
            "tribhagaLord": tribhaga_lord, "dayBirth": is_day,
        },
        "methodNotes": METHOD_NOTES,
    }


def _round(obj):
    if isinstance(obj, dict):
        return {k: _round(v) for k, v in obj.items()}
    if isinstance(obj, float):
        return round(obj, 2)
    return obj
