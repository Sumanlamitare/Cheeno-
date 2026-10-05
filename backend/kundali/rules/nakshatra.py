"""Janma Rashi (Moon sign) and Janma Nakshatra interpretation."""

from __future__ import annotations

from ..jyotish.constants import NAKSHATRAS, RASHIS, format_dms, nakshatra_lord, ordinal
from ..jyotish.dignity import angular_distance
from .data.nakshatras import GANA_TEXT, NAKSHATRA_DATA
from .data.planets import PLANET_IN_HOUSE
from .data.signs import MOON_SIGN, NAVAMSA_SIGN_QUALITY
from .engine import ChartContext


def analyze(ctx: ChartContext) -> dict:
    c = ctx.chart
    moon = c.planets["Moon"]
    nak = moon.nakshatra
    data = NAKSHATRA_DATA[nak]
    lord = nakshatra_lord(nak)
    lord_pl = c.planets[lord]
    elong = angular_distance(moon.longitude, c.planets["Sun"].longitude)
    waxing = (moon.longitude - c.planets["Sun"].longitude) % 360 < 180
    nav = moon.vargas["9"]["sign"]
    items = [
        {"text": MOON_SIGN[moon.sign], "polarity": "neutral", "ruleId": f"moon_sign_{moon.sign}",
         "why": [f"The Moon is in {RASHIS[moon.sign]} at {format_dms(moon.degree)}"]},
        {"text": PLANET_IN_HOUSE["Moon"][moon.house][1], "polarity": PLANET_IN_HOUSE["Moon"][moon.house][0],
         "ruleId": f"moon_house_{moon.house}", "why": [f"The Moon occupies the {ordinal(moon.house)} house"]},
        {"text": (f"The Moon is {'waxing' if waxing else 'waning'} and {elong:.0f}° from the Sun; tradition considers "
                  + ("a Moon far from the Sun (bright) to be strong and supportive of emotional resilience."
                     if elong >= 72 else "a Moon close to the Sun to be weaker in Paksha Bala, so emotional steadiness "
                     "benefits from conscious routine.")),
         "polarity": "positive" if elong >= 72 else "mixed", "ruleId": "moon_paksha",
         "why": [f"Sun-Moon angular distance: {elong:.1f}°"]},
        {"text": f"The Moon's pada falls in {RASHIS[nav]} Navamsa, adding a note of {NAVAMSA_SIGN_QUALITY[nav]} to the "
                 f"nakshatra's expression.", "polarity": "neutral", "ruleId": f"moon_pada_navamsa_{nav}",
         "why": [f"{NAKSHATRAS[nak]} pada {moon.pada} corresponds to {RASHIS[nav]} Navamsa"]},
        {"text": (f"The nakshatra lord {lord} is in the {ordinal(lord_pl.house)} house ({RASHIS[lord_pl.sign]}, "
                  f"{lord_pl.dignity}); tradition holds that the nakshatra lord's condition colours the mind and sets "
                  f"the first Vimshottari Mahadasha."), "polarity": "neutral", "ruleId": "moon_nakshatra_lord",
         "why": [f"{NAKSHATRAS[nak]} is ruled by {lord}"]},
    ]
    if moon.dignity in ("exalted", "own", "moolatrikona"):
        items.append({"text": "The Moon is dignified, traditionally associated with emotional stability and contentment.",
                      "polarity": "positive", "ruleId": "moon_dignified",
                      "why": [f"Moon is {moon.dignity} in {RASHIS[moon.sign]}"]})
    if moon.dignity == "debilitated":
        items.append({"text": "The Moon is debilitated, traditionally associated with emotional depth and sensitivity that "
                              "benefit from supportive surroundings.", "polarity": "negative", "ruleId": "moon_debilitated",
                      "why": ["Moon in Scorpio is debilitated"]})
    return {
        "janmaRashi": RASHIS[moon.sign],
        "moonDegree": format_dms(moon.degree),
        "moonLongitude": round(moon.longitude, 6),
        "nakshatra": NAKSHATRAS[nak],
        "nakshatraIndex": nak,
        "pada": moon.pada,
        "nakshatraLord": lord,
        "deity": data["deity"],
        "symbol": data["symbol"],
        "gana": data["gana"],
        "ganaText": GANA_TEXT[data["gana"]],
        "nature": data["nature"],
        "characteristics": data["characteristics"],
        "nakshatraInterpretation": data["interpretation"],
        "span": {"start": nak * 360 / 27, "end": (nak + 1) * 360 / 27},
        "items": items,
    }


def nakshatra_catalogue() -> list[dict]:
    return [
        {"index": i, "name": NAKSHATRAS[i], "lord": nakshatra_lord(i), "startDegree": i * 360 / 27,
         **{k: v for k, v in NAKSHATRA_DATA[i].items()}}
        for i in range(27)
    ]
