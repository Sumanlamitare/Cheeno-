"""Planetary dignity, relationships and combustion."""

from __future__ import annotations

from .constants import (
    COMBUSTION_ORB,
    DEBILITATION,
    EXALTATION,
    MOOLATRIKONA,
    NATURAL_ENEMIES,
    NATURAL_FRIENDS,
    OWN_SIGNS,
    RASHI_LORDS,
    house_from,
)

DIGNITY_ORDER = [
    "exalted", "moolatrikona", "own", "great friend", "friend",
    "neutral", "enemy", "great enemy", "debilitated",
]

# Rough ordinal used ONLY for comparisons inside rule conditions
# (e.g. "dignity at least friend"); not a strength score.
DIGNITY_RANK = {d: len(DIGNITY_ORDER) - i for i, d in enumerate(DIGNITY_ORDER)}


def natural_relation(planet: str, other: str) -> str:
    if planet == other:
        return "self"
    if other in NATURAL_FRIENDS.get(planet, set()):
        return "friend"
    if other in NATURAL_ENEMIES.get(planet, set()):
        return "enemy"
    return "neutral"


def temporal_relation(planet_sign: int, other_sign: int) -> str:
    """Tatkalika relationship: planets in the 2nd, 3rd, 4th, 10th, 11th and
    12th from each other are temporary friends; all others temporary enemies."""
    return "friend" if house_from(planet_sign, other_sign) in {2, 3, 4, 10, 11, 12} else "enemy"


_COMPOUND = {
    ("friend", "friend"): "great friend",
    ("friend", "enemy"): "neutral",
    ("neutral", "friend"): "friend",
    ("neutral", "enemy"): "enemy",
    ("enemy", "friend"): "neutral",
    ("enemy", "enemy"): "great enemy",
}


def compound_relation(planet: str, other: str, planet_sign: int, other_sign: int) -> str:
    """Panchadha (five-fold) relationship of `planet` towards `other`."""
    if planet == other:
        return "self"
    return _COMPOUND[(natural_relation(planet, other), temporal_relation(planet_sign, other_sign))]


def sign_dignity(planet: str, longitude: float, planet_signs: dict[str, int]) -> str:
    """Dignity of a planet in its rashi.

    Order of precedence: exaltation, debilitation, moolatrikona, own sign,
    then the compound relationship with the sign lord. Where the exaltation
    sign is also the moolatrikona sign (Moon in Taurus, Mercury in Virgo),
    the exaltation applies up to the deep-exaltation degree.
    """
    sign = int(longitude // 30)
    deg = longitude % 30
    ex_sign, ex_deg = EXALTATION[planet]
    mt = MOOLATRIKONA.get(planet)
    if sign == ex_sign:
        if mt and mt[0] == sign:
            if deg <= ex_deg:
                return "exalted"
            if mt[1] <= deg < mt[2]:
                return "moolatrikona"
            return "own" if sign in OWN_SIGNS[planet] else "exalted"
        return "exalted"
    if sign == DEBILITATION[planet][0]:
        return "debilitated"
    if mt and mt[0] == sign and mt[1] <= deg < mt[2]:
        return "moolatrikona"
    if sign in OWN_SIGNS[planet]:
        return "own"
    lord = RASHI_LORDS[sign]
    if lord == planet:
        return "own"
    lord_sign = planet_signs.get(lord)
    if lord_sign is None:
        return natural_relation(planet, lord)
    return compound_relation(planet, lord, sign, lord_sign)


def varga_dignity(planet: str, varga_sign: int, planet_varga_signs: dict[str, int]) -> str:
    """Dignity inside a divisional chart (sign-level only; no moolatrikona)."""
    if varga_sign == EXALTATION[planet][0]:
        return "exalted"
    if varga_sign == DEBILITATION[planet][0]:
        return "debilitated"
    if varga_sign in OWN_SIGNS[planet]:
        return "own"
    lord = RASHI_LORDS[varga_sign]
    lord_sign = planet_varga_signs.get(lord)
    if lord_sign is None:
        return natural_relation(planet, lord)
    return compound_relation(planet, lord, varga_sign, lord_sign)


def angular_distance(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return 360.0 - d if d > 180 else d


def combustion(planet: str, longitude: float, sun_longitude: float, retrograde: bool) -> tuple[bool, float]:
    if planet not in COMBUSTION_ORB:
        return False, angular_distance(longitude, sun_longitude)
    orb = COMBUSTION_ORB[planet][1 if retrograde else 0]
    dist = angular_distance(longitude, sun_longitude)
    return dist <= orb, dist


def moon_is_benefic(moon_lon: float, sun_lon: float) -> bool:
    """Application convention: the Moon is treated as a benefic from Shukla
    Ashtami to Krishna Ashtami (elongation 90°-270°), malefic otherwise."""
    elong = (moon_lon - sun_lon) % 360.0
    return 90.0 <= elong <= 270.0


def mercury_is_benefic(mercury_sign: int, planet_signs: dict[str, int]) -> bool:
    """Mercury is benefic unless it shares a sign with a natural malefic."""
    for p in ("Sun", "Mars", "Saturn", "Rahu", "Ketu"):
        if planet_signs.get(p) == mercury_sign:
            return False
    return True
