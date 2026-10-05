"""Lagna and core nature. Combines the Lagna sign with the Lagna lord's
house, sign, dignity and nakshatra, planets in and aspecting the 1st house
and the Lagna nakshatra - so two people with the same Lagna sign receive
different readings when the rest of the chart differs."""

from __future__ import annotations

from ..jyotish.constants import NAKSHATRAS, RASHIS, format_dms, nakshatra_lord, ordinal
from .data.nakshatras import NAKSHATRA_DATA
from .data.signs import LAGNA
from .engine import ChartContext, rule, run_rules, synthesize
from .library import bhavesha_rules, planet_house_rules

C = "lagna"
THEMES = {
    "lagna.self": "Self-direction and life orientation",
    "lagna.fortune": "Fortune and support",
    "lagna.relations": "Orientation towards others",
    "lagna.struggle": "Tests and resilience",
    "lagna.presence": "Presence and temperament",
    "lagna.strength": "Strength of the Lagna lord",
}


def _t(y, pol):
    if y in (5, 9, 11, 2):
        return "lagna.fortune"
    if y in (7, 4):
        return "lagna.relations"
    if pol == "negative" or y in (6, 8, 12):
        return "lagna.struggle"
    return "lagna.self"


def build_rules():
    rules = bhavesha_rules(1, C, _t, "major")
    rules += planet_house_rules(1, C, lambda p, pol: "lagna.struggle" if pol == "negative" else "lagna.presence", "strong")
    rules += [
        rule("lagna_lord_strong", C, "lagna.strength", "major", "positive", [{"t": "strong", "p": "L1"}],
             "The Lagna lord {L1} is strong, which tradition regards as the foundation of a resilient, self-assured "
             "personality and good vitality.", "Strength of the Lagna lord", subject="L1"),
        rule("lagna_lord_weak", C, "lagna.struggle", "strong", "negative", [{"t": "weak", "p": "L1"}],
             "The Lagna lord {L1} is weak, which tradition associates with confidence and vitality that grow through "
             "conscious effort and supportive routines.", "Weakness of the Lagna lord", subject="L1"),
        rule("lagna_jup_aspect", C, "lagna.fortune", "strong", "positive", [{"t": "aspected", "h": 1, "by": "Jupiter"}],
             "Jupiter aspects the Lagna, traditionally associated with good character, optimism and protection.",
             "Jupiter aspects the Lagna"),
        rule("lagna_benefic_aspect", C, "lagna.presence", "moderate", "positive",
             [{"t": "aspected", "h": 1, "by": ["Venus", "Mercury", "Moon"], "benefic": True}],
             "A benefic aspects the Lagna, adding gentleness and pleasant manners to the personality.",
             "Benefic aspect on the Lagna"),
        rule("lagna_saturn_aspect", C, "lagna.struggle", "moderate", "mixed", [{"t": "aspected", "h": 1, "by": "Saturn"}],
             "Saturn aspects the Lagna, traditionally associated with seriousness, responsibility and maturity that "
             "deepens with age.", "Saturn aspects the Lagna"),
        rule("lagna_mars_aspect", C, "lagna.presence", "minor", "mixed", [{"t": "aspected", "h": 1, "by": "Mars"}],
             "Mars aspects the Lagna, adding energy, courage and a quick temper.", "Mars aspects the Lagna"),
        rule("lagna_lord_retro", C, "lagna.self", "minor", "mixed", [{"t": "retro", "p": "L1"}],
             "The Lagna lord is retrograde, traditionally associated with an introspective nature that revisits "
             "decisions before acting.", "Retrograde Lagna lord"),
        rule("lagna_lord_combust", C, "lagna.struggle", "minor", "negative", [{"t": "combust", "p": "L1"}],
             "The Lagna lord is combust, traditionally associated with self-expression that may be overshadowed by "
             "others or by authority until it matures.", "Combust Lagna lord"),
        rule("lagna_lord_vargottama", C, "lagna.strength", "moderate", "positive", [{"t": "vargottama", "p": "L1"}],
             "The Lagna lord is Vargottama, traditionally associated with consistency of character.",
             "Vargottama Lagna lord"),
        rule("lagna_lord_kendra_moon", C, "lagna.self", "minor", "positive", [{"t": "from_moon", "p": "L1", "h": [1, 4, 7, 10]}],
             "The Lagna lord is in a kendra from the Moon, harmonising mind and body.", "Lagna lord in kendra from Moon"),
        rule("lagna_yoga_mahapurusha", C, "lagna.strength", "strong", "positive",
             [{"t": "yoga", "id": ["ruchaka", "bhadra", "hamsa", "malavya", "sasa"]}],
             "A Pancha Mahapurusha Yoga is present, traditionally associated with a distinctive, capable personality.",
             "Pancha Mahapurusha Yoga"),
    ]
    return rules


RULES = build_rules()


def analyze(ctx: ChartContext) -> dict:
    c = ctx.chart
    asc = c.ascendant
    lord = c.house_lord(1)
    lpl = c.planets[lord]
    base = LAGNA[c.lagna_sign]
    nak = asc.nakshatra
    out = synthesize("the personality and life direction", run_rules(ctx, RULES), THEMES)
    out["facts"] = {
        "ascendantLongitude": round(asc.longitude, 6),
        "lagnaSign": RASHIS[c.lagna_sign],
        "lagnaDegree": format_dms(asc.degree),
        "lagnaNakshatra": NAKSHATRAS[nak],
        "lagnaPada": asc.pada,
        "lagnaNakshatraLord": nakshatra_lord(nak),
        "lagnaLord": lord,
        "lagnaLordHouse": lpl.house,
        "lagnaLordSign": RASHIS[lpl.sign],
        "lagnaLordNakshatra": NAKSHATRAS[lpl.nakshatra],
        "lagnaLordDignity": lpl.dignity,
    }
    out["signProfile"] = {**base, "why": [f"The Lagna rises in {RASHIS[c.lagna_sign]} at {format_dms(asc.degree)}"]}
    out["nakshatraNote"] = {
        "text": f"The Lagna falls in {NAKSHATRAS[nak]} nakshatra (ruled by {nakshatra_lord(nak)}): "
                + NAKSHATRA_DATA[nak]["characteristics"],
        "why": [f"Ascendant at {format_dms(asc.degree)} {RASHIS[c.lagna_sign]} lies in {NAKSHATRAS[nak]} pada {asc.pada}"],
    }
    out["lordNote"] = {
        "text": (f"The Lagna lord {lord} is in the {ordinal(lpl.house)} house in {RASHIS[lpl.sign]} "
                 f"({lpl.dignity}), in {NAKSHATRAS[lpl.nakshatra]} nakshatra. Its condition colours how the "
                 f"{RASHIS[c.lagna_sign]} qualities above are expressed."),
        "why": [f"{RASHIS[c.lagna_sign]} is ruled by {lord}"],
    }
    return out
