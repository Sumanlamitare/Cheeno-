"""Graha Drishti (Parashari sign-based planetary aspects).

Every graha casts a full aspect on the 7th sign from itself. Mars additionally
aspects the 4th and 8th, Jupiter the 5th and 9th, and Saturn the 3rd and 10th
(counted inclusively from the sign the planet occupies). These are Jyotish
drishtis, not Western angular aspects.
"""

from __future__ import annotations

from .constants import SPECIAL_ASPECTS


def aspect_houses(planet: str) -> list[int]:
    return sorted({7, *SPECIAL_ASPECTS.get(planet, [])})


def aspected_signs(planet: str, sign: int) -> list[int]:
    return [(sign + h - 1) % 12 for h in aspect_houses(planet)]


def aspects_sign(planet: str, planet_sign: int, target_sign: int) -> bool:
    return target_sign in aspected_signs(planet, planet_sign)


def aspect_type(planet: str, planet_sign: int, target_sign: int) -> int | None:
    """Return the house count (3, 4, 5, 7, 8, 9, 10) of the aspect, or None."""
    for h in aspect_houses(planet):
        if (planet_sign + h - 1) % 12 == target_sign:
            return h
    return None


def sphuta_drishti(aspecting: str, aspecting_lon: float, aspected_lon: float) -> float:
    """Numerical aspect value in virupas (0-60) used for Drik Bala.

    Formula as given in BPHS ch. 26 and B. V. Raman, "Graha and Bhava
    Balas", based on the angular distance of the aspected body from the
    aspecting body, with the special aspects of Mars, Jupiter and Saturn.
    """
    d = (aspected_lon - aspecting_lon) % 360.0
    if d < 30:
        v = 0.0
    elif d < 60:
        v = (d - 30) / 2
    elif d < 90:
        v = d - 60 + 15
    elif d < 120:
        v = (120 - d) / 2 + 30
    elif d < 150:
        v = 150 - d
    elif d < 180:
        v = (d - 150) * 2
    elif d < 300:
        v = (300 - d) / 2
    else:
        v = 0.0
    if aspecting == "Saturn" and (60 <= d < 90 or 270 <= d < 300):
        v += 45
    elif aspecting == "Jupiter" and (120 <= d < 150 or 240 <= d < 270):
        v += 30
    elif aspecting == "Mars" and (90 <= d < 120 or 210 <= d < 240):
        v += 15
    return min(v, 60.0)
