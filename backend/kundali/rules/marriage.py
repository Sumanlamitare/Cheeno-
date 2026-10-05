"""Love and marriage rules: 7th house and lord, Venus, Jupiter, Moon, D9,
Dashas and Jupiter's transit. Timing windows are traditional indications
only; no marriage date is predicted."""

from __future__ import annotations

import datetime as dt

from ..jyotish.constants import RASHIS, ordinal
from ..jyotish.gochar import planet_sign_periods
from .engine import ChartContext, rule, run_rules, synthesize
from .library import bhavesha_rules, planet_house_rules, significator_set, timing_windows

C = "marriage"
THEMES = {
    "marriage.harmony": "Harmony and support in partnership",
    "marriage.partner": "Nature of the partner",
    "marriage.delay": "Delays, maturity and timing",
    "marriage.friction": "Friction and the need for patience",
    "marriage.fortune": "Fortune through partnership",
    "marriage.distance": "Distance, travel or cross-cultural factors",
    "marriage.d9": "Navamsa (D9) confirmation",
    "marriage.venus": "Venus (significator of relationships)",
    "marriage.dosha": "Mangal Dosha consideration",
}


def _theme_7(y, pol):
    if y in (1, 2, 4, 5, 7, 11):
        return "marriage.harmony"
    if y in (9, 10):
        return "marriage.fortune"
    if y in (6, 8):
        return "marriage.friction"
    if y == 12:
        return "marriage.distance"
    return "marriage.partner"


_P7 = {"Sun": "partner", "Moon": "harmony", "Mars": "friction", "Mercury": "partner", "Jupiter": "harmony",
       "Venus": "partner", "Saturn": "delay", "Rahu": "distance", "Ketu": "friction"}


def build_rules():
    rules = bhavesha_rules(7, C, _theme_7, "major")
    rules += planet_house_rules(7, C, lambda p, pol: f"marriage.{_P7[p]}", "strong")
    rules += [
        rule("marriage_L7_strong", C, "marriage.harmony", "strong", "positive", [{"t": "strong", "p": "L7"}],
             "The 7th lord {L7} is strong, which tradition regards as support for a stable partnership.",
             "Strength of the 7th lord", subject="L7"),
        rule("marriage_L7_weak", C, "marriage.friction", "moderate", "negative", [{"t": "weak", "p": "L7"}],
             "The 7th lord {L7} is weak; tradition advises patience and mutual understanding in partnerships.",
             "Weakness of the 7th lord", subject="L7"),
        rule("marriage_jup_aspect_7", C, "marriage.harmony", "strong", "positive",
             [{"t": "aspected", "h": 7, "by": "Jupiter"}],
             "Jupiter's aspect on the 7th house is a classical protection for marriage, associated with a principled "
             "partner and goodwill in the relationship.", "Jupiter aspects 7th"),
        rule("marriage_jup_aspect_L7", C, "marriage.harmony", "moderate", "positive",
             [{"t": "aspects_planet", "p": "L7", "by": ["Jupiter"]}],
             "Jupiter aspects the 7th lord, a protective factor for partnership.", "Jupiter aspects 7th lord"),
        rule("marriage_sat_aspect_7", C, "marriage.delay", "moderate", "mixed",
             [{"t": "aspected", "h": 7, "by": "Saturn"}],
             "Saturn's aspect on the 7th house is traditionally associated with a later or carefully considered "
             "commitment that becomes durable.", "Saturn aspects 7th"),
        rule("marriage_mars_aspect_7", C, "marriage.friction", "minor", "negative",
             [{"t": "aspected", "h": 7, "by": "Mars"}],
             "Mars's aspect on the 7th house adds passion and assertiveness; tradition advises restraint in "
             "disagreements.", "Mars aspects 7th"),
        rule("marriage_venus_strong", C, "marriage.venus", "strong", "positive", [{"t": "strong", "p": "Venus"}],
             "Venus, the natural significator of marriage, is strong, traditionally supporting affection and harmony.",
             "Strength of Venus", subject="Venus"),
        rule("marriage_venus_weak", C, "marriage.venus", "moderate", "negative", [{"t": "weak", "p": "Venus"}],
             "Venus is weak; tradition associates this with effort needed to sustain harmony and mutual "
             "appreciation.", "Weakness of Venus", subject="Venus"),
        rule("marriage_venus_dusthana", C, "marriage.friction", "minor", "negative",
             [{"t": "in_house", "p": "Venus", "h": [6, 8]}],
             "Venus in the 6th or 8th is traditionally associated with complexities in relationships.",
             "Venus in 6th/8th"),
        rule("marriage_venus_with_malefic", C, "marriage.friction", "minor", "negative",
             [{"t": "with", "p": "Venus", "any_of": ["Saturn", "Mars", "Rahu", "Ketu"]}],
             "Venus is joined by a malefic, which tradition associates with tests in relationships.",
             "Venus with a malefic"),
        rule("marriage_moon_strong", C, "marriage.harmony", "minor", "positive",
             [{"t": "strong", "p": "Moon"}],
             "A strong Moon supports emotional stability in relationships.", "Strength of the Moon", subject="Moon"),
        rule("marriage_L7_L1_conj", C, "marriage.harmony", "moderate", "positive",
             [{"t": "not", "c": {"t": "same", "a": "L1", "b": "L7"}}, {"t": "conj", "a": "L1", "b": "L7"}],
             "The Lagna lord and 7th lord are together, traditionally associated with closeness between self and "
             "partner.", "Lagna lord with 7th lord"),
        # D9
        rule("marriage_d9_L7_dignified", C, "marriage.d9", "strong", "positive",
             [{"t": "varga_dignity", "d": 9, "p": "L7", "values": ["exalted", "own"]}],
             "The Rashi 7th lord is dignified in the Navamsa, which tradition reads as confirmation of partnership "
             "promise.", "D1 7th lord dignified in D9", subject="L7"),
        rule("marriage_d9_L7_debil", C, "marriage.d9", "moderate", "negative",
             [{"t": "varga_dignity", "d": 9, "p": "L7", "values": ["debilitated"]}],
             "The Rashi 7th lord is debilitated in the Navamsa; tradition advises patience in partnership matters.",
             "D1 7th lord debilitated in D9"),
        rule("marriage_d9_venus_dignified", C, "marriage.d9", "strong", "positive",
             [{"t": "varga_dignity", "d": 9, "p": "Venus", "values": ["exalted", "own"]}],
             "Venus is dignified in the Navamsa, a classical support for marital happiness.",
             "Venus dignified in D9", subject="Venus"),
        rule("marriage_d9_venus_debil", C, "marriage.d9", "moderate", "negative",
             [{"t": "varga_dignity", "d": 9, "p": "Venus", "values": ["debilitated"]}],
             "Venus is debilitated in the Navamsa; tradition associates this with effort required in relationships.",
             "Venus debilitated in D9"),
        rule("marriage_d9_7th_benefic", C, "marriage.d9", "moderate", "positive",
             [{"t": "varga_occupied", "d": 9, "h": 7, "by": ["Jupiter", "Venus", "Mercury", "Moon"]}],
             "A benefic occupies the 7th house of the Navamsa, supporting the partnership.", "Benefic in D9 7th"),
        rule("marriage_d9_7th_malefic", C, "marriage.d9", "minor", "negative",
             [{"t": "varga_occupied", "d": 9, "h": 7, "by": ["Saturn", "Mars", "Rahu", "Ketu", "Sun"]}],
             "A malefic occupies the 7th house of the Navamsa; tradition advises patience and clear communication.",
             "Malefic in D9 7th"),
        rule("marriage_d9_L7_good", C, "marriage.d9", "moderate", "positive",
             [{"t": "varga_house", "d": 9, "p": "D9L7", "h": [1, 4, 5, 7, 9, 10, 11]}],
             "The Navamsa 7th lord is well placed in the D9.", "D9 7th lord well placed"),
        rule("marriage_d9_L7_dusthana", C, "marriage.d9", "minor", "negative",
             [{"t": "varga_house", "d": 9, "p": "D9L7", "h": [6, 8, 12]}],
             "The Navamsa 7th lord falls in a dusthana of the D9.", "D9 7th lord in dusthana"),
        rule("marriage_vargottama_venus", C, "marriage.venus", "moderate", "positive", [{"t": "vargottama", "p": "Venus"}],
             "Venus is Vargottama, giving steadiness to relationship matters.", "Vargottama Venus"),
        rule("marriage_mangal", C, "marriage.dosha", "moderate", "mixed", [{"t": "dosha", "id": "mangal"}],
             "Mangal Dosha is present under this application's rule; tradition weighs it together with the partner's "
             "chart during Kundali matching.", "Mangal Dosha"),
        rule("marriage_malavya", C, "marriage.venus", "moderate", "positive", [{"t": "yoga", "id": "malavya"}],
             "Malavya Yoga is associated with harmony and refinement in married life.", "Malavya Yoga"),
    ]
    return rules


RULES = build_rules()


def analyze(ctx: ChartContext, dasha_tree: list[dict], now: dt.datetime, birth: dt.datetime) -> dict:
    out = synthesize("love and marriage", run_rules(ctx, RULES), THEMES)
    c = ctx.chart
    age_now = (now - birth).days / 365.25
    start = max(now, birth + dt.timedelta(days=365.25 * 21))
    end = max(birth + dt.timedelta(days=365.25 * 40), now + dt.timedelta(days=365.25 * 5))
    end = min(end, now + dt.timedelta(days=365.25 * 25))
    sig = significator_set(ctx, ["L7", "Venus", "D9L1", "D9L7"], occupied_houses=[7])
    windows = timing_windows(dasha_tree, sig, start, end, limit=8) if start < end else []
    # Jupiter's transit over the 7th from Lagna or Moon - a classical supporting factor.
    jup = []
    for ref_name, ref_sign in (("Lagna", c.lagna_sign), ("Moon", c.planets["Moon"].sign)):
        sign7 = (ref_sign + 6) % 12
        for per in planet_sign_periods("Jupiter", sign7, start, end, c.settings) if start < end else []:
            jup.append({"ref": ref_name, "sign": RASHIS[sign7], "start": per["start"], "end": per["end"]})
    for w in windows:
        ws, we = dt.datetime.fromisoformat(w["start"]), dt.datetime.fromisoformat(w["end"])
        overlaps = [j for j in jup if j["start"] < we and j["end"] > ws]
        if overlaps:
            j = overlaps[0]
            w["why"].append(f"Jupiter transits the 7th from the {j['ref']} ({j['sign']}) during part of this period")
            w["jupiterSupport"] = True
    out["timing"] = {
        "windows": windows,
        "jupiterTransits7th": [{"ref": j["ref"], "sign": j["sign"], "start": j["start"].isoformat(),
                                "end": j["end"].isoformat()} for j in jup],
        "method": ("Antardasha periods (from age 21, or from today if later) whose lord signifies marriage: the 7th "
                   "lord, Venus, the Navamsa Lagna lord or 7th lord, or a planet in the 7th. Jupiter's transit over "
                   "the 7th from the Lagna or Moon is noted as a classical supporting factor. These are traditional "
                   "windows, not predicted dates."),
        "ageNow": round(age_now, 1),
    }
    out["keyFactors"] = [
        {"label": "7th house", "value": RASHIS[c.house_sign(7)]},
        {"label": "7th lord", "value": f"{c.house_lord(7)} in the {ordinal(c.house_of(c.house_lord(7)))} house "
                                       f"({c.planets[c.house_lord(7)].dignity})"},
        {"label": "Planets in 7th", "value": ", ".join(c.occupants(7)) or "None"},
        {"label": "Venus", "value": f"{RASHIS[c.planets['Venus'].sign]}, {ordinal(c.house_of('Venus'))} house; "
                                    f"D9 {c.planets['Venus'].vargas['9']['signName']}"},
        {"label": "D9 Lagna", "value": RASHIS[c.ascendant.vargas["9"]["sign"]]},
        {"label": "D9 7th lord", "value": f"{ctx.resolve('D9L7')} in D9 house "
                                          f"{c.planets[ctx.resolve('D9L7')].vargas['9']['house']}"},
    ]
    return out
