"""Education rules: 4th, 5th and 9th houses and lords, Mercury, Jupiter,
D24 and Dashas."""

from __future__ import annotations

import datetime as dt

from ..jyotish.constants import RASHIS, ordinal
from .engine import ChartContext, rule, run_rules, synthesize
from .data.domain_lords import EDU_L4, EDU_L5, EDU_L9
from .library import domain_lord_rules, planet_house_rules, significator_set, timing_windows, yoga_rule

C = "education"
THEMES = {
    "education.intellect": "Intelligence and learning ability",
    "education.foundation": "Foundational education and environment",
    "education.higher": "Higher learning and teachers",
    "education.obstacles": "Interruptions and obstacles in studies",
    "education.analytical": "Analytical and communicative strengths",
    "education.wisdom": "Wisdom, philosophy and judgement",
    "education.yoga": "Yogas of learning",
}


def _t(y, pol):
    if pol == "negative":
        return "education.obstacles"
    if y in (9, 12):
        return "education.higher"
    if y in (4, 1, 2):
        return "education.foundation"
    return "education.intellect"


def build_rules():
    rules = domain_lord_rules(5, EDU_L5, C, _t, "major")
    rules += domain_lord_rules(4, EDU_L4, C, _t, "moderate", prefix="education_4")
    rules += domain_lord_rules(9, EDU_L9, C, lambda y, pol: "education.obstacles" if pol == "negative" else "education.higher",
                               "moderate", prefix="education_9")
    rules += planet_house_rules(5, C, lambda p, pol: "education.obstacles" if pol == "negative" else "education.intellect",
                                "strong")
    rules += planet_house_rules(4, C, lambda p, pol: "education.obstacles" if pol == "negative" else "education.foundation",
                                "minor", planets=["Mercury", "Jupiter", "Venus", "Moon", "Saturn", "Rahu", "Ketu", "Mars", "Sun"])
    rules += [
        rule("education_mercury_strong", C, "education.analytical", "strong", "positive", [{"t": "strong", "p": "Mercury"}],
             "Mercury, significator of intellect and speech, is strong, traditionally supporting analytical ability, "
             "language and quick learning.", "Strength of Mercury", subject="Mercury"),
        rule("education_mercury_weak", C, "education.obstacles", "moderate", "negative", [{"t": "weak", "p": "Mercury"}],
             "Mercury is weak; tradition associates this with learning that benefits from structure and repetition.",
             "Weakness of Mercury", subject="Mercury"),
        rule("education_jupiter_strong", C, "education.wisdom", "strong", "positive", [{"t": "strong", "p": "Jupiter"}],
             "Jupiter, significator of knowledge and teachers, is strong, traditionally supporting depth of learning "
             "and sound judgement.", "Strength of Jupiter", subject="Jupiter"),
        rule("education_jupiter_weak", C, "education.obstacles", "moderate", "negative", [{"t": "weak", "p": "Jupiter"}],
             "Jupiter is weak; tradition advises seeking good teachers and guidance.", "Weakness of Jupiter",
             subject="Jupiter"),
        rule("education_jup_aspect_5", C, "education.wisdom", "moderate", "positive", [{"t": "aspected", "h": 5, "by": "Jupiter"}],
             "Jupiter aspects the 5th house of intelligence, a classical support for education.", "Jupiter aspects 5th"),
        rule("education_mercury_jupiter_relation", C, "education.intellect", "moderate", "positive",
             [{"t": "any", "c": [{"t": "conj", "a": "Mercury", "b": "Jupiter"},
                                 {"t": "aspects_planet", "p": "Mercury", "by": ["Jupiter"]}]}],
             "Mercury is supported by Jupiter, joining analytical skill with wisdom.", "Mercury with/aspected by Jupiter"),
        rule("education_L5_strong", C, "education.intellect", "strong", "positive", [{"t": "strong", "p": "L5"}],
             "The 5th lord {L5} is strong, a classical indicator of intelligence and success in studies.",
             "Strength of the 5th lord", subject="L5"),
        rule("education_L5_weak", C, "education.obstacles", "moderate", "negative", [{"t": "weak", "p": "L5"}],
             "The 5th lord {L5} is weak; tradition associates this with studies requiring persistence.",
             "Weakness of the 5th lord", subject="L5"),
        rule("education_malefic_5", C, "education.obstacles", "minor", "negative",
             [{"t": "occupied", "h": 5, "by": ["Saturn", "Rahu", "Ketu", "Mars"]},
              {"t": "not", "c": {"t": "aspected", "h": 5, "by": "Jupiter"}}],
             "A malefic in the 5th without Jupiter's aspect is traditionally associated with interruptions or changes "
             "in the course of studies.", "Malefic in 5th"),
        rule("education_d24_lagnalord_good", C, "education.higher", "minor", "positive",
             [{"t": "varga_house", "d": 24, "p": "D24L1", "h": [1, 4, 5, 7, 9, 10]}],
             "In the Chaturvimshamsha (D24, the chart of learning) the Lagna lord is well placed.", "D24 Lagna lord"),
        rule("education_vargottama_mercury", C, "education.analytical", "moderate", "positive",
             [{"t": "vargottama", "p": "Mercury"}], "Mercury is Vargottama, steadying the intellect.", "Vargottama Mercury"),
        yoga_rule(C, ["saraswati"], "education.yoga", "Saraswati Yoga is classically associated with learning, "
                  "eloquence and scholarship.", "major"),
        yoga_rule(C, ["budha_aditya"], "education.yoga", "Budha-Aditya Yoga is associated with intelligence and "
                  "recognition for learning.", "moderate"),
        yoga_rule(C, ["bhadra", "hamsa"], "education.yoga", "Bhadra or Hamsa Yoga strengthens intellect or wisdom.",
                  "moderate"),
        yoga_rule(C, ["gaja_kesari"], "education.yoga", "Gaja Kesari Yoga supports intelligence and reputation.",
                  "minor"),
    ]
    return rules


RULES = build_rules()


def analyze(ctx: ChartContext, dasha_tree, now: dt.datetime) -> dict:
    out = synthesize("education", run_rules(ctx, RULES), THEMES)
    sig = significator_set(ctx, ["L4", "L5", "L9", "Mercury", "Jupiter"], occupied_houses=[5])
    out["timing"] = {"windows": timing_windows(dasha_tree, sig, now, now + dt.timedelta(days=365.25 * 15), limit=6),
                     "method": "Antardasha periods whose lord is the 4th, 5th or 9th lord, Mercury, Jupiter or a planet in the 5th."}
    c = ctx.chart
    out["keyFactors"] = [
        {"label": f"{ordinal(h)} lord", "value": f"{c.house_lord(h)} in the {ordinal(c.house_of(c.house_lord(h)))} house"}
        for h in (4, 5, 9)
    ] + [{"label": p, "value": f"{RASHIS[c.planets[p].sign]}, {ordinal(c.house_of(p))} house, {c.planets[p].dignity}"}
         for p in ("Mercury", "Jupiter")]
    return out
