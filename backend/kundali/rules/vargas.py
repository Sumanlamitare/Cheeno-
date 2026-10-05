"""Navamsa (D9) and Dashamsa (D10) interpretation, always read together
with the Rashi chart."""

from __future__ import annotations

from ..jyotish.constants import PLANETS, RASHIS
from ..jyotish.vargas import VARGA_NAMES
from .engine import ChartContext, rule, run_rules, synthesize

D9_THEMES = {
    "d9.strength": "Planets gaining inner strength",
    "d9.weakness": "Planets lacking inner strength",
    "d9.marriage": "Marriage and partnership (D9 with D1)",
    "d9.dharma": "Dharma and inner maturity",
}
D10_THEMES = {
    "d10.strength": "Professional strength",
    "d10.challenge": "Professional challenges",
    "d10.direction": "Career direction",
}


def _d9_rules():
    rules = []
    for p in PLANETS[:7]:
        rules.append(rule(f"d9_{p}_dignified", "d9", "d9.strength", "moderate", "positive",
                          [{"t": "varga_dignity", "d": 9, "p": p, "values": ["exalted", "own"]}],
                          f"{p} is dignified in the Navamsa; tradition holds that it matures well and gives fuller "
                          f"results of its Rashi placement.", f"{p} dignified in D9", subject=p))
        rules.append(rule(f"d9_{p}_debil", "d9", "d9.weakness", "moderate", "negative",
                          [{"t": "varga_dignity", "d": 9, "p": p, "values": ["debilitated"]}],
                          f"{p} is debilitated in the Navamsa; tradition holds that its Rashi promise needs more effort "
                          f"to mature.", f"{p} debilitated in D9", subject=p))
        rules.append(rule(f"d9_{p}_vargottama", "d9", "d9.strength", "moderate", "positive",
                          [{"t": "vargottama", "p": p}],
                          f"{p} is Vargottama, a classical mark of steadiness and strength.", f"Vargottama {p}"))
    rules += [
        rule("d9_lagnalord_good", "d9", "d9.dharma", "strong", "positive",
             [{"t": "varga_house", "d": 9, "p": "D9L1", "h": [1, 4, 5, 7, 9, 10, 11]}],
             "The Navamsa Lagna lord is well placed, supporting inner stability and the fruits of dharma.",
             "D9 Lagna lord well placed"),
        rule("d9_lagnalord_dusthana", "d9", "d9.dharma", "moderate", "negative",
             [{"t": "varga_house", "d": 9, "p": "D9L1", "h": [6, 8, 12]}],
             "The Navamsa Lagna lord falls in a dusthana of the D9, which tradition associates with inner tests that "
             "build maturity.", "D9 Lagna lord in dusthana"),
        rule("d9_L7_dignified", "d9", "d9.marriage", "strong", "positive",
             [{"t": "varga_dignity", "d": 9, "p": "L7", "values": ["exalted", "own"]}],
             "The Rashi 7th lord is dignified in the Navamsa, supporting partnership.", "D1 7th lord dignified in D9"),
        rule("d9_venus_7_9", "d9", "d9.marriage", "moderate", "positive",
             [{"t": "varga_house", "d": 9, "p": "Venus", "h": [1, 4, 5, 7, 9, 10, 11]}],
             "Venus is well placed in the Navamsa, supporting harmony in relationships.", "Venus well placed in D9"),
        rule("d9_jupiter_good", "d9", "d9.dharma", "moderate", "positive",
             [{"t": "varga_house", "d": 9, "p": "Jupiter", "h": [1, 4, 5, 7, 9, 10]}],
             "Jupiter is well placed in the Navamsa, supporting wisdom and dharma.", "Jupiter well placed in D9"),
        rule("d9_L9_good", "d9", "d9.dharma", "minor", "positive",
             [{"t": "varga_house", "d": 9, "p": "D9L9", "h": [1, 4, 5, 7, 9, 10, 11]}],
             "The Navamsa 9th lord is well placed, supporting fortune and faith.", "D9 9th lord well placed"),
    ]
    return rules


def _d10_rules():
    rules = [
        rule("d10_L10_dignified", "d10", "d10.strength", "strong", "positive",
             [{"t": "varga_dignity", "d": 10, "p": "L10", "values": ["exalted", "own"]}],
             "The Rashi 10th lord is dignified in the Dashamsha, confirming professional strength.",
             "D1 10th lord dignified in D10"),
        rule("d10_L10_debil", "d10", "d10.challenge", "moderate", "negative",
             [{"t": "varga_dignity", "d": 10, "p": "L10", "values": ["debilitated"]}],
             "The Rashi 10th lord is debilitated in the Dashamsha, calling for patience in career.",
             "D1 10th lord debilitated in D10"),
        rule("d10_lagnalord_good", "d10", "d10.strength", "strong", "positive",
             [{"t": "varga_house", "d": 10, "p": "D10L1", "h": [1, 4, 5, 7, 9, 10, 11]}],
             "The Dashamsha Lagna lord is well placed in the D10.", "D10 Lagna lord well placed"),
        rule("d10_lagnalord_dusthana", "d10", "d10.challenge", "moderate", "negative",
             [{"t": "varga_house", "d": 10, "p": "D10L1", "h": [6, 8, 12]}],
             "The Dashamsha Lagna lord falls in a dusthana of the D10.", "D10 Lagna lord in dusthana"),
        rule("d10_sun_dignified", "d10", "d10.strength", "moderate", "positive",
             [{"t": "varga_dignity", "d": 10, "p": "Sun", "values": ["exalted", "own"]}],
             "The Sun is dignified in the Dashamsha, associated with authority in work.", "Sun dignified in D10"),
        rule("d10_saturn_dignified", "d10", "d10.strength", "moderate", "positive",
             [{"t": "varga_dignity", "d": 10, "p": "Saturn", "values": ["exalted", "own"]}],
             "Saturn is dignified in the Dashamsha, associated with endurance and organisational capacity.",
             "Saturn dignified in D10"),
        rule("d10_10th_lord_good", "d10", "d10.direction", "moderate", "positive",
             [{"t": "varga_house", "d": 10, "p": "D10L10", "h": [1, 4, 5, 7, 9, 10, 11]}],
             "The Dashamsha 10th lord is well placed in the D10.", "D10 10th lord well placed"),
    ]
    for p in PLANETS:
        rules.append(rule(f"d10_{p}_in_10", "d10", "d10.direction", "moderate", "neutral",
                          [{"t": "varga_occupied", "d": 10, "h": 10, "by": [p]}],
                          f"{p} occupies the 10th house of the Dashamsha, adding its significations to the career.",
                          f"{p} in D10 10th house"))
        rules.append(rule(f"d10_{p}_in_1", "d10", "d10.direction", "minor", "neutral",
                          [{"t": "varga_occupied", "d": 10, "h": 1, "by": [p]}],
                          f"{p} occupies the Lagna of the Dashamsha, shaping one's professional persona.",
                          f"{p} in D10 Lagna"))
    return rules


D9_RULES = _d9_rules()
D10_RULES = _d10_rules()


def varga_table(ctx: ChartContext, division: int) -> dict:
    c = ctx.chart
    lagna = c.ascendant.vargas[str(division)]["sign"]
    planets = []
    for p in PLANETS:
        v = c.planets[p].vargas[str(division)]
        planets.append({"planet": p, "sign": v["sign"], "signName": v["signName"], "house": v["house"],
                        "dignity": v["dignity"], "vargottama": division == 9 and v["sign"] == c.planets[p].sign})
    name, purpose = VARGA_NAMES[division]
    return {"division": division, "name": name, "purpose": purpose, "lagna": lagna, "lagnaName": RASHIS[lagna],
            "planets": planets}


def analyze_d9(ctx: ChartContext) -> dict:
    out = synthesize("inner strength, dharma and partnership (Navamsa)", run_rules(ctx, D9_RULES), D9_THEMES)
    out["chart"] = varga_table(ctx, 9)
    out["vargottama"] = [p["planet"] for p in out["chart"]["planets"] if p["vargottama"]]
    out["note"] = "The Navamsa refines the Rashi chart and is never read in isolation from it."
    return out


def analyze_d10(ctx: ChartContext) -> dict:
    out = synthesize("profession (Dashamsha)", run_rules(ctx, D10_RULES), D10_THEMES)
    out["chart"] = varga_table(ctx, 10)
    out["note"] = "The Dashamsha refines the 10th house of the Rashi chart for career analysis."
    return out
