"""Graha Sambandha (planetary relationships) used by the Yoga engine.

Parashari Sambandha recognised here:
  * conjunction  - both grahas occupy the same sign
  * mutual aspect - each graha aspects the other's sign
  * exchange     - Parivartana: each occupies a sign owned by the other
A one-way aspect is reported separately and is not counted as a full
Sambandha for Raja/Dhana yoga purposes.
"""

from __future__ import annotations

from .chart import NatalChart
from .constants import DUSTHANAS, OWN_SIGNS, RASHI_LORDS
from .drishti import aspects_sign


def conjunct(chart: NatalChart, a: str, b: str) -> bool:
    return chart.planets[a].sign == chart.planets[b].sign


def aspects(chart: NatalChart, a: str, b: str) -> bool:
    """True if graha a casts a full drishti on graha b's sign."""
    return aspects_sign(a, chart.planets[a].sign, chart.planets[b].sign)


def mutual_aspect(chart: NatalChart, a: str, b: str) -> bool:
    return aspects(chart, a, b) and aspects(chart, b, a)


def exchange(chart: NatalChart, a: str, b: str) -> bool:
    if a in ("Rahu", "Ketu") or b in ("Rahu", "Ketu"):
        return False
    return RASHI_LORDS[chart.planets[a].sign] == b and RASHI_LORDS[chart.planets[b].sign] == a


def sambandha(chart: NatalChart, a: str, b: str) -> list[str]:
    if a == b:
        return []
    out = []
    if conjunct(chart, a, b):
        out.append("conjunction")
    if mutual_aspect(chart, a, b):
        out.append("mutual aspect")
    if exchange(chart, a, b):
        out.append("exchange of signs")
    return out


def describe_sambandha(kinds: list[str]) -> str:
    return " and ".join(kinds)


def strength_points(chart: NatalChart, planet: str) -> tuple[int, list[str]]:
    """Points used to grade a yoga (application convention, documented):
    +1 exalted / moolatrikona / own sign, -1 debilitated, -1 combust,
    -1 placed in a dusthana (6th, 8th, 12th)."""
    pl = chart.planets[planet]
    pts = 0
    notes = []
    if pl.dignity in ("exalted", "moolatrikona", "own"):
        pts += 1
        notes.append(f"{planet} is in its own sign" if pl.dignity == "own" else
                     f"{planet} is in its moolatrikona sign" if pl.dignity == "moolatrikona" else f"{planet} is exalted")
    if pl.dignity == "debilitated":
        pts -= 1
        notes.append(f"{planet} is debilitated")
    if pl.combust:
        pts -= 1
        notes.append(f"{planet} is combust")
    if pl.house in DUSTHANAS:
        pts -= 1
        notes.append(f"{planet} occupies the {pl.house}th house (dusthana)")
    return pts, notes


def grade(points: int) -> str:
    if points >= 1:
        return "Strong"
    if points == 0:
        return "Moderate"
    return "Weak"


def is_own_or_exalted(chart: NatalChart, planet: str) -> bool:
    pl = chart.planets[planet]
    return pl.dignity in ("exalted", "moolatrikona", "own") or pl.sign in OWN_SIGNS.get(planet, [])
