"""Wealth analysis rules: 2nd, 5th, 9th, 11th houses and lords, Jupiter,
Venus, Dhana yogas and Dasha timing. No financial guarantees are made."""

from __future__ import annotations

import datetime as dt

from ..jyotish.constants import RASHIS, ordinal
from .engine import ChartContext, rule, run_rules, synthesize
from .library import bhavesha_rules, planet_house_rules, significator_set, timing_windows, yoga_rule

C = "wealth"
THEMES = {
    "wealth.accumulation": "Accumulation and family resources",
    "wealth.income": "Income and gains",
    "wealth.fortune": "Fortune and opportunity",
    "wealth.effort": "Earning through effort and enterprise",
    "wealth.discipline": "Financial discipline and expenditure",
    "wealth.fluctuation": "Fluctuations and joint resources",
    "wealth.yoga": "Dhana yogas",
    "wealth.karaka": "Jupiter and Venus (natural significators)",
}


def _theme_2(y, pol):
    if y in (2, 11, 1, 4, 10):
        return "wealth.accumulation"
    if y in (5, 9):
        return "wealth.fortune"
    if y in (3, 6, 7):
        return "wealth.effort"
    if y == 8:
        return "wealth.fluctuation"
    return "wealth.discipline"


def _theme_11(y, pol):
    if y in (2, 11, 10, 1, 4, 5, 7, 9, 3):
        return "wealth.income"
    if y == 8:
        return "wealth.fluctuation"
    if y == 12:
        return "wealth.discipline"
    return "wealth.effort"


def build_rules():
    rules = bhavesha_rules(2, C, _theme_2, "major")
    rules += bhavesha_rules(11, C, _theme_11, "major")
    rules += bhavesha_rules(9, C, lambda y, pol: "wealth.fortune" if pol != "negative" else "wealth.fluctuation",
                            "moderate", prefix="wealth_9")
    rules += bhavesha_rules(5, C, lambda y, pol: "wealth.fortune" if pol != "negative" else "wealth.fluctuation",
                            "minor", prefix="wealth_5")
    rules += planet_house_rules(2, C, lambda p, pol: "wealth.accumulation" if pol != "negative" else "wealth.discipline",
                                "strong")
    rules += planet_house_rules(11, C, lambda p, pol: "wealth.income", "strong")
    rules += [
        rule("wealth_L2_strong", C, "wealth.accumulation", "strong", "positive", [{"t": "strong", "p": "L2"}],
             "The 2nd lord {L2} is strong, traditionally supporting the ability to accumulate and preserve wealth.",
             "Strength of the 2nd lord", subject="L2"),
        rule("wealth_L11_strong", C, "wealth.income", "strong", "positive", [{"t": "strong", "p": "L11"}],
             "The 11th lord {L11} is strong, traditionally supporting steady income and gains.",
             "Strength of the 11th lord", subject="L11"),
        rule("wealth_L2_weak", C, "wealth.discipline", "moderate", "negative", [{"t": "weak", "p": "L2"}],
             "The 2nd lord {L2} is weak; tradition advises deliberate saving and caution with family finances.",
             "Weakness of the 2nd lord", subject="L2"),
        rule("wealth_L11_weak", C, "wealth.fluctuation", "moderate", "negative", [{"t": "weak", "p": "L11"}],
             "The 11th lord {L11} is weak; tradition associates this with gains that require persistence.",
             "Weakness of the 11th lord", subject="L11"),
        rule("wealth_jupiter_strong", C, "wealth.karaka", "strong", "positive", [{"t": "strong", "p": "Jupiter"}],
             "Jupiter, the natural significator of wealth (Dhana Karaka), is strong in this chart.",
             "Strength of Jupiter", subject="Jupiter"),
        rule("wealth_jupiter_weak", C, "wealth.karaka", "moderate", "negative", [{"t": "weak", "p": "Jupiter"}],
             "Jupiter, the natural significator of wealth, is weak; tradition advises prudence and sound advice in "
             "financial matters.", "Weakness of Jupiter", subject="Jupiter"),
        rule("wealth_venus_strong", C, "wealth.karaka", "moderate", "positive", [{"t": "strong", "p": "Venus"}],
             "A strong Venus is traditionally associated with comforts, luxuries and the means to enjoy them.",
             "Strength of Venus", subject="Venus"),
        rule("wealth_jup_aspect_2", C, "wealth.accumulation", "moderate", "positive",
             [{"t": "aspected", "h": 2, "by": "Jupiter"}],
             "Jupiter aspects the 2nd house of savings, a classical support for accumulation.", "Jupiter aspects 2nd"),
        rule("wealth_jup_aspect_11", C, "wealth.income", "moderate", "positive",
             [{"t": "aspected", "h": 11, "by": "Jupiter"}],
             "Jupiter aspects the 11th house of gains, a classical support for income.", "Jupiter aspects 11th"),
        rule("wealth_jup_in_2_11_from_moon", C, "wealth.karaka", "minor", "positive",
             [{"t": "from_moon", "p": "Jupiter", "h": [2, 5, 9, 11]}],
             "Jupiter's favourable position from the Moon supports prosperity in traditional assessment.",
             "Jupiter's house from the Moon"),
        rule("wealth_L2_L11_exchange_or_conj", C, "wealth.yoga", "strong", "positive",
             [{"t": "conj", "a": "L2", "b": "L11"}],
             "The lords of the 2nd and 11th are together, a classical wealth combination joining savings and income.",
             "2nd lord with 11th lord"),
        rule("wealth_12L_in_2", C, "wealth.discipline", "moderate", "negative", [{"t": "in_house", "p": "L12", "h": 2}],
             "The 12th lord occupies the 2nd house; tradition advises conscious control of expenditure.",
             "12th lord in 2nd house"),
        rule("wealth_malefic_2_unaspected", C, "wealth.discipline", "minor", "negative",
             [{"t": "occupied", "h": 2, "by": ["Saturn", "Mars", "Rahu", "Ketu"]},
              {"t": "not", "c": {"t": "aspected", "h": 2, "by": "Jupiter"}}],
             "A malefic in the 2nd without Jupiter's aspect is traditionally associated with effort being required to "
             "preserve savings.", "Malefic in the 2nd house"),
        rule("wealth_d2_note_sun_hora", C, "wealth.effort", "minor", "neutral",
             [{"t": "varga_lagna", "d": 2, "s": [4]}],
             "The Hora (D2) Lagna is in the Sun's hora, which tradition associates with wealth gained through effort, "
             "authority and enterprise.", "D2 Lagna in Leo (Sun's hora)"),
        rule("wealth_d2_note_moon_hora", C, "wealth.accumulation", "minor", "neutral",
             [{"t": "varga_lagna", "d": 2, "s": [3]}],
             "The Hora (D2) Lagna is in the Moon's hora, which tradition associates with wealth that grows through "
             "nurturing, trade and accumulation.", "D2 Lagna in Cancer (Moon's hora)"),
        yoga_rule(C, ["dhana"], "wealth.yoga",
                  "Dhana Yoga is present: the lords of wealth houses are linked with the lords of fortune or self, a "
                  "classical indicator of earning capacity.", "major"),
        yoga_rule(C, ["lakshmi"], "wealth.yoga", "Lakshmi Yoga is traditionally associated with prosperity and "
                  "generosity.", "major"),
        yoga_rule(C, ["chandra_mangala"], "wealth.yoga", "Chandra-Mangala Yoga is associated with resourcefulness "
                  "and earning through enterprise.", "moderate"),
        yoga_rule(C, ["vasumati", "durudhara", "sunapha"], "wealth.yoga",
                  "Lunar wealth yogas (Vasumati / Sunapha / Durudhara) support self-earned prosperity.", "moderate"),
        yoga_rule(C, ["malavya"], "wealth.yoga", "Malavya Yoga is associated with comforts and refined living.",
                  "moderate"),
        rule("wealth_shakata", C, "wealth.fluctuation", "moderate", "negative", [{"t": "yoga", "id": "shakata"}],
             "Shakata Yoga is associated with ups and downs in fortune; steady financial habits are traditionally "
             "advised.", "Shakata Yoga"),
    ]
    return rules


RULES = build_rules()


def analyze(ctx: ChartContext, dasha_tree: list[dict], now: dt.datetime) -> dict:
    out = synthesize("wealth", run_rules(ctx, RULES), THEMES)
    sig = significator_set(ctx, ["L2", "L11", "L9", "Jupiter"], occupied_houses=[2, 11])
    out["timing"] = {
        "windows": timing_windows(dasha_tree, sig, now, now + dt.timedelta(days=365.25 * 20)),
        "method": ("Antardasha periods in the next 20 years whose lord is a wealth significator (2nd, 11th or 9th "
                   "lord, Jupiter, or a planet in the 2nd or 11th)."),
    }
    c = ctx.chart
    out["keyFactors"] = [
        {"label": f"{ordinal(h)} lord", "value": f"{c.house_lord(h)} in the {ordinal(c.house_of(c.house_lord(h)))} "
                                                 f"house ({c.planets[c.house_lord(h)].dignity})"}
        for h in (2, 5, 9, 11)
    ] + [
        {"label": "Jupiter", "value": f"{RASHIS[c.planets['Jupiter'].sign]}, {ordinal(c.house_of('Jupiter'))} house, "
                                      f"{c.planets['Jupiter'].dignity}"},
        {"label": "Venus", "value": f"{RASHIS[c.planets['Venus'].sign]}, {ordinal(c.house_of('Venus'))} house, "
                                    f"{c.planets['Venus'].dignity}"},
    ]
    out["disclaimer"] = "Traditional indicators only; this is not financial advice and no outcome is guaranteed."
    return out
