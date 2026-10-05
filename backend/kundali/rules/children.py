"""Children (Santana) rules: 5th house and lord, Jupiter and D7. Kept
respectful and non-medical; no fertility predictions are made."""

from __future__ import annotations

from ..jyotish.constants import RASHIS, ordinal
from .engine import ChartContext, rule, run_rules, synthesize
from .data.domain_lords import CHILD_L5
from .library import domain_lord_rules, planet_house_rules

C = "children"
THEMES = {
    "children.blessing": "Supportive indications for children",
    "children.patience": "Patience and responsibility",
    "children.d7": "Saptamsha (D7) confirmation",
}


def build_rules():
    t = lambda y, pol: "children.patience" if pol == "negative" else "children.blessing"
    rules = domain_lord_rules(5, CHILD_L5, C, t, "major")
    rules += planet_house_rules(5, C, lambda p, pol: "children.patience" if pol == "negative" else "children.blessing",
                                "strong")
    rules += [
        rule("children_jupiter_strong", C, "children.blessing", "strong", "positive", [{"t": "strong", "p": "Jupiter"}],
             "Jupiter, the natural significator of children (Putra Karaka), is strong.", "Strength of Jupiter",
             subject="Jupiter"),
        rule("children_jupiter_weak", C, "children.patience", "moderate", "negative", [{"t": "weak", "p": "Jupiter"}],
             "Jupiter, significator of children, is weak; tradition associates this with patience in matters of children.",
             "Weakness of Jupiter", subject="Jupiter"),
        rule("children_jup_aspect_5", C, "children.blessing", "strong", "positive", [{"t": "aspected", "h": 5, "by": "Jupiter"}],
             "Jupiter aspects the 5th house, a classical blessing for children.", "Jupiter aspects 5th"),
        rule("children_jup_5th_from_moon", C, "children.blessing", "minor", "positive",
             [{"t": "from_moon", "p": "Jupiter", "h": [1, 5, 9]}],
             "Jupiter is in a trikona from the Moon, a supportive classical factor.", "Jupiter in trikona from Moon"),
        rule("children_L5_strong", C, "children.blessing", "strong", "positive", [{"t": "strong", "p": "L5"}],
             "The 5th lord {L5} is strong.", "Strength of the 5th lord", subject="L5"),
        rule("children_L5_weak", C, "children.patience", "moderate", "negative", [{"t": "weak", "p": "L5"}],
             "The 5th lord {L5} is weak; tradition advises patience.", "Weakness of the 5th lord", subject="L5"),
        rule("children_d7_lagnalord_good", C, "children.d7", "moderate", "positive",
             [{"t": "varga_house", "d": 7, "p": "D7L1", "h": [1, 4, 5, 7, 9, 10, 11]}],
             "The Saptamsha (D7) Lagna lord is well placed.", "D7 Lagna lord well placed"),
        rule("children_d7_lagnalord_dusthana", C, "children.d7", "minor", "negative",
             [{"t": "varga_house", "d": 7, "p": "D7L1", "h": [6, 8, 12]}],
             "The Saptamsha (D7) Lagna lord falls in a dusthana.", "D7 Lagna lord in dusthana"),
        rule("children_d7_jupiter_dignified", C, "children.d7", "moderate", "positive",
             [{"t": "varga_dignity", "d": 7, "p": "Jupiter", "values": ["exalted", "own"]}],
             "Jupiter is dignified in the Saptamsha.", "Jupiter dignified in D7"),
    ]
    return rules


RULES = build_rules()


def analyze(ctx: ChartContext) -> dict:
    out = synthesize("children", run_rules(ctx, RULES), THEMES)
    c = ctx.chart
    out["keyFactors"] = [
        {"label": "5th house", "value": f"{RASHIS[c.house_sign(5)]}; occupants: {', '.join(c.occupants(5)) or 'none'}"},
        {"label": "5th lord", "value": f"{c.house_lord(5)} in the {ordinal(c.house_of(c.house_lord(5)))} house"},
        {"label": "Jupiter", "value": f"{RASHIS[c.planets['Jupiter'].sign]}, {ordinal(c.house_of('Jupiter'))} house"},
        {"label": "D7 Lagna", "value": RASHIS[c.ascendant.vargas["7"]["sign"]]},
    ]
    out["disclaimer"] = ("These are traditional, symbolic indications only. They are not medical or fertility "
                         "predictions.")
    return out
