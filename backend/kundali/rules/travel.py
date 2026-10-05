"""Foreign travel and relocation rules: 3rd, 9th and 12th houses and lords,
Rahu, movable signs, Dashas and transits. Migration is never guaranteed."""

from __future__ import annotations

import datetime as dt

from ..jyotish.constants import RASHIS, ordinal
from .engine import ChartContext, rule, run_rules, synthesize
from .library import significator_set, timing_windows

C = "travel"
THEMES = {
    "travel.foreign": "Foreign lands and international connections",
    "travel.relocation": "Living away from the birthplace",
    "travel.journeys": "Journeys and pilgrimage",
    "travel.rooted": "Rootedness near the birthplace",
}


def build_rules():
    return [
        rule("travel_L12_in_9_12", C, "travel.foreign", "major", "positive", [{"t": "in_house", "p": "L12", "h": [9, 12, 1, 7, 10]}],
             "The 12th lord, ruler of foreign lands, is placed in the {L12_house} house, which tradition associates "
             "with connections abroad or travel linked with that area of life.", "12th lord placement"),
        rule("travel_L9_in_12", C, "travel.foreign", "strong", "positive", [{"t": "in_house", "p": "L9", "h": 12}],
             "The 9th lord in the 12th is a classical indication of fortune connected with distant or foreign lands.",
             "9th lord in 12th"),
        rule("travel_L1_in_12", C, "travel.relocation", "major", "positive", [{"t": "in_house", "p": "L1", "h": [12, 9]}],
             "The Lagna lord is placed in the {L1_house} house, traditionally associated with living or working away "
             "from the birthplace.", "Lagna lord in 9th/12th"),
        rule("travel_L4_in_12_or_dusthana", C, "travel.relocation", "strong", "positive",
             [{"t": "in_house", "p": "L4", "h": [12, 8, 6, 3, 9]}],
             "The 4th lord (homeland) is placed in the {L4_house} house, traditionally associated with residence away "
             "from the place of birth.", "4th lord away from home houses"),
        rule("travel_4th_malefic", C, "travel.relocation", "moderate", "positive",
             [{"t": "occupied", "h": 4, "by": ["Rahu", "Ketu", "Saturn", "Mars"]}],
             "A malefic in the 4th house is traditionally associated with leaving the ancestral home.",
             "Malefic in 4th"),
        rule("travel_rahu_foreign_houses", C, "travel.foreign", "strong", "positive",
             [{"t": "in_house", "p": "Rahu", "h": [1, 7, 9, 10, 12]}],
             "Rahu, significator of foreign elements, occupies the {Rahu_house} house, traditionally linked with "
             "international connections.", "Rahu placement"),
        rule("travel_planets_12", C, "travel.foreign", "moderate", "positive",
             [{"t": "occupied", "h": 12, "by": ["Moon", "Rahu", "Saturn", "Jupiter", "Venus", "Mercury", "Sun", "Mars", "Ketu"]}],
             "Planets in the 12th house draw attention to foreign lands, retreat and distant places.",
             "Planets in 12th"),
        rule("travel_moon_12_9", C, "travel.journeys", "moderate", "positive", [{"t": "in_house", "p": "Moon", "h": [3, 9, 12]}],
             "The Moon in a travel house is traditionally associated with a love of journeys.", "Moon in 3rd/9th/12th"),
        rule("travel_L9_strong", C, "travel.journeys", "minor", "positive", [{"t": "strong", "p": "L9"}],
             "A strong 9th lord supports long-distance travel and pilgrimage.", "Strength of the 9th lord"),
        rule("travel_L3_in_9_12", C, "travel.journeys", "minor", "positive", [{"t": "in_house", "p": "L3", "h": [9, 12]}],
             "The 3rd lord in the {L3_house} links short journeys with long-distance travel.", "3rd lord in 9th/12th"),
        rule("travel_movable_lagna_moon", C, "travel.journeys", "minor", "positive",
             [{"t": "house_modality", "h": 1, "m": "movable"}, {"t": "moon_sign", "s": [0, 3, 6, 9]}],
             "Both the Lagna and the Moon are in movable signs, traditionally associated with mobility.",
             "Movable Lagna and Moon"),
        rule("travel_rooted_L4_4", C, "travel.rooted", "strong", "neutral",
             [{"t": "in_house", "p": "L4", "h": [4, 1]}, {"t": "strong", "p": "L4"}],
             "A strong 4th lord in the 1st or 4th house is traditionally associated with strong roots at home; travel "
             "tends to be followed by return.", "Strong 4th lord at home"),
        rule("travel_fixed_lagna_moon", C, "travel.rooted", "minor", "neutral",
             [{"t": "house_modality", "h": 1, "m": "fixed"}, {"t": "moon_sign", "s": [1, 4, 7, 10]}],
             "Both the Lagna and the Moon are in fixed signs, traditionally associated with a preference for stability "
             "of place.", "Fixed Lagna and Moon"),
    ]


RULES = build_rules()


def analyze(ctx: ChartContext, dasha_tree, now: dt.datetime) -> dict:
    out = synthesize("travel and relocation", run_rules(ctx, RULES), THEMES)
    sig = significator_set(ctx, ["L12", "L9", "Rahu"], occupied_houses=[12])
    out["timing"] = {"windows": timing_windows(dasha_tree, sig, now, now + dt.timedelta(days=365.25 * 20), limit=6),
                     "method": "Antardasha periods whose lord is the 12th or 9th lord, Rahu, or a planet in the 12th."}
    c = ctx.chart
    out["keyFactors"] = [
        {"label": f"{ordinal(h)} lord", "value": f"{c.house_lord(h)} in the {ordinal(c.house_of(c.house_lord(h)))} house"}
        for h in (3, 9, 12, 4)
    ] + [{"label": "Rahu", "value": f"{RASHIS[c.planets['Rahu'].sign]}, {ordinal(c.house_of('Rahu'))} house"}]
    out["disclaimer"] = "Traditional indicators of travel and relocation; migration is not guaranteed."
    return out
