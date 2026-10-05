"""Family and home rules: 2nd and 4th houses and lords, Moon and planetary
influences."""

from __future__ import annotations

from ..jyotish.constants import RASHIS, ordinal
from .engine import ChartContext, rule, run_rules, synthesize
from .library import bhavesha_rules, planet_house_rules

C = "family"
THEMES = {
    "family.home": "Home, comfort and property",
    "family.mother": "Mother and emotional foundation",
    "family.kin": "Family ties and speech",
    "family.unsettled": "Changes and responsibilities at home",
    "family.father": "Father and elders",
}


def build_rules():
    rules = bhavesha_rules(4, C, lambda y, pol: "family.unsettled" if pol == "negative" else "family.home", "major")
    rules += bhavesha_rules(2, C, lambda y, pol: "family.unsettled" if pol == "negative" else "family.kin", "strong",
                            prefix="family_2")
    rules += planet_house_rules(4, C, lambda p, pol: "family.unsettled" if pol == "negative" else "family.home", "strong")
    rules += planet_house_rules(2, C, lambda p, pol: "family.unsettled" if pol == "negative" else "family.kin",
                                "moderate", prefix="family_2")
    rules += [
        rule("family_moon_strong", C, "family.mother", "strong", "positive", [{"t": "strong", "p": "Moon"}],
             "The Moon, significator of the mother and the mind, is strong, traditionally supporting emotional "
             "security and maternal care.", "Strength of the Moon", subject="Moon"),
        rule("family_moon_weak", C, "family.mother", "moderate", "negative", [{"t": "weak", "p": "Moon"}],
             "The Moon is weak; tradition advises attention to emotional wellbeing and to the mother's welfare.",
             "Weakness of the Moon", subject="Moon"),
        rule("family_moon_afflicted", C, "family.unsettled", "minor", "negative",
             [{"t": "with", "p": "Moon", "any_of": ["Saturn", "Rahu", "Ketu", "Mars"]}],
             "The Moon is joined by a malefic, traditionally associated with emotional intensity within the family.",
             "Moon with a malefic"),
        rule("family_jup_aspect_4", C, "family.home", "moderate", "positive", [{"t": "aspected", "h": 4, "by": "Jupiter"}],
             "Jupiter aspects the 4th house, a classical blessing for home and contentment.", "Jupiter aspects 4th"),
        rule("family_jup_aspect_2", C, "family.kin", "moderate", "positive", [{"t": "aspected", "h": 2, "by": "Jupiter"}],
             "Jupiter aspects the 2nd house, supporting family harmony and gentle speech.", "Jupiter aspects 2nd"),
        rule("family_mars_sat_aspect_4", C, "family.unsettled", "minor", "negative",
             [{"t": "aspected", "h": 4, "by": ["Saturn", "Mars"]}],
             "A malefic aspect on the 4th house is traditionally associated with responsibilities or changes at home.",
             "Malefic aspect on 4th"),
        rule("family_L4_strong", C, "family.home", "strong", "positive", [{"t": "strong", "p": "L4"}],
             "The 4th lord {L4} is strong, supporting a settled home and property.", "Strength of the 4th lord",
             subject="L4"),
        rule("family_venus_4", C, "family.home", "minor", "positive", [{"t": "strong", "p": "Venus"}, {"t": "in_house", "p": "Venus", "h": [4, 2, 1]}],
             "A strong Venus in a personal house supports domestic comforts and vehicles.", "Strong Venus"),
        rule("family_sun_9", C, "family.father", "moderate", "positive", [{"t": "strong", "p": "Sun"}],
             "A strong Sun, significator of the father, supports paternal guidance and respect from elders.",
             "Strength of the Sun", subject="Sun"),
        rule("family_L9_strong", C, "family.father", "minor", "positive", [{"t": "strong", "p": "L9"}],
             "A strong 9th lord supports the father and elders.", "Strength of the 9th lord"),
    ]
    return rules


RULES = build_rules()


def analyze(ctx: ChartContext) -> dict:
    out = synthesize("family and home", run_rules(ctx, RULES), THEMES)
    c = ctx.chart
    out["keyFactors"] = [
        {"label": "4th house", "value": f"{RASHIS[c.house_sign(4)]}; occupants: {', '.join(c.occupants(4)) or 'none'}"},
        {"label": "4th lord", "value": f"{c.house_lord(4)} in the {ordinal(c.house_of(c.house_lord(4)))} house"},
        {"label": "2nd lord", "value": f"{c.house_lord(2)} in the {ordinal(c.house_of(c.house_lord(2)))} house"},
        {"label": "Moon", "value": f"{RASHIS[c.planets['Moon'].sign]}, {ordinal(c.house_of('Moon'))} house, {c.planets['Moon'].dignity}"},
    ]
    return out
