"""Career analysis rules: Lagna lord, 10th house and lord, planets in and
aspecting the 10th, 6th/2nd/11th houses, D10, yogas, Dasha timing."""

from __future__ import annotations

import datetime as dt
from collections import Counter

from ..jyotish.constants import PLANETS, RASHI_ELEMENT, RASHIS, ordinal
from .data.planets import CAREER_FIELDS, WORK_STYLE, WORK_STYLE_TEXT
from .engine import ChartContext, rule, run_rules, synthesize
from .library import bhavesha_rules, planet_house_rules, significator_set, timing_windows, yoga_rule

C = "career"
THEMES = {
    "career.status": "Professional standing and recognition",
    "career.fortune": "Ethics, mentors and fortune through work",
    "career.gains": "Earnings and fulfilment of professional goals",
    "career.effort": "Growth through effort, skill and persistence",
    "career.service": "Service, problem-solving and competition",
    "career.change": "Changes, interruptions and hidden factors",
    "career.foreign": "Foreign, institutional or behind-the-scenes work",
    "career.leadership": "Leadership and authority",
    "career.d10": "Dashamsha (D10) confirmation",
    "career.yoga": "Raja and career yogas",
    "career.style": "Working style",
}

_L10_THEME = {1: "status", 4: "status", 7: "status", 10: "status", 5: "fortune", 9: "fortune", 2: "gains",
              11: "gains", 3: "effort", 6: "service", 8: "change", 12: "foreign"}
_P10_THEME = {"Sun": "leadership", "Mars": "leadership", "Moon": "status", "Mercury": "status", "Jupiter": "status",
              "Venus": "status", "Saturn": "effort", "Rahu": "foreign", "Ketu": "change"}


def build_rules():
    rules = bhavesha_rules(10, C, lambda y, pol: f"career.{_L10_THEME[y]}", "major")
    rules += planet_house_rules(10, C, lambda p, pol: f"career.{_P10_THEME[p]}", "strong")
    rules += bhavesha_rules(1, C, lambda y, pol: "career.status" if y in (10, 11, 1, 9) else
                            ("career.change" if pol == "negative" else "career.effort"), "moderate", prefix="career_lagna")
    rules += bhavesha_rules(6, C, lambda y, pol: "career.service", "minor", prefix="career_6")
    rules += [
        rule("career_L10_strong", C, "career.status", "major", "positive", [{"t": "strong", "p": "L10"}],
             "The 10th lord {L10} is strong, which tradition regards as a pillar of professional stability and "
             "recognition.", "Strength of the 10th lord", subject="L10"),
        rule("career_L10_weak", C, "career.change", "strong", "negative", [{"t": "weak", "p": "L10"}],
             "The 10th lord {L10} is weak, which tradition associates with effort being needed to secure "
             "professional stability and recognition.", "Weakness of the 10th lord", subject="L10"),
        rule("career_L10_retro", C, "career.change", "minor", "mixed", [{"t": "retro", "p": "L10"}],
             "With the 10th lord retrograde, tradition describes a career direction that is revisited and refined "
             "before it settles.", "Retrograde 10th lord"),
        rule("career_L1_L10_conj", C, "career.status", "strong", "positive",
             [{"t": "not", "c": {"t": "same", "a": "L1", "b": "L10"}}, {"t": "conj", "a": "L1", "b": "L10"}],
             "The Lagna lord and 10th lord are together, uniting personal identity with profession; tradition "
             "associates this with a self-directed career.", "Lagna lord with 10th lord"),
        rule("career_10_jup_aspect", C, "career.fortune", "moderate", "positive",
             [{"t": "aspected", "h": 10, "by": "Jupiter"}],
             "Jupiter's aspect on the 10th house is traditionally regarded as protecting the career and bringing "
             "good counsel and ethical standing.", "Jupiter's aspect on the 10th"),
        rule("career_10_sat_aspect", C, "career.effort", "moderate", "mixed",
             [{"t": "aspected", "h": 10, "by": "Saturn"}],
             "Saturn's aspect on the 10th house is traditionally associated with a slow, steady rise through "
             "responsibility and hard work.", "Saturn's aspect on the 10th"),
        rule("career_10_mars_aspect", C, "career.leadership", "minor", "positive",
             [{"t": "aspected", "h": 10, "by": "Mars"}],
             "Mars's aspect on the 10th house adds drive, executive energy and a competitive edge to the career.",
             "Mars's aspect on the 10th"),
        rule("career_sun_strong_angular", C, "career.leadership", "strong", "positive",
             [{"t": "strong", "p": "Sun"}, {"t": "in_house", "p": "Sun", "h": [1, 4, 7, 10]}],
             "A strong Sun in a kendra is traditionally associated with leadership, authority and recognition from "
             "superiors or government.", "Strong Sun in a kendra", subject="Sun"),
        rule("career_saturn_strong", C, "career.effort", "moderate", "positive", [{"t": "strong", "p": "Saturn"}],
             "A strong Saturn is traditionally associated with endurance, organisational ability and longevity in "
             "one's profession.", "Strong Saturn", subject="Saturn"),
        rule("career_L10_combust", C, "career.change", "minor", "negative", [{"t": "combust", "p": "L10"}],
             "The 10th lord is combust; tradition associates this with one's work being overshadowed by others "
             "until one's own authority is established.", "Combust 10th lord"),
        rule("career_L10_rahu", C, "career.foreign", "moderate", "mixed", [{"t": "with", "p": "L10", "any_of": ["Rahu"]}],
             "The 10th lord is joined by Rahu, which tradition links with unconventional, foreign or "
             "technology-related directions and sudden turns in career.", "10th lord with Rahu"),
        rule("career_6L_strong_service", C, "career.service", "minor", "positive",
             [{"t": "strong", "p": "L6"}, {"t": "in_house", "p": "L6", "h": [3, 6, 10, 11]}],
             "A strong 6th lord in an upachaya house is associated with success in competitive and service-oriented "
             "work.", "Strong 6th lord in upachaya"),
        rule("career_L2_L11_strong", C, "career.gains", "moderate", "positive",
             [{"t": "strong", "p": "L11"}, {"t": "not", "c": {"t": "in_house", "p": "L11", "h": [6, 8, 12]}}],
             "A strong 11th lord {L11} supports earnings and the fulfilment of professional goals.",
             "Strength of the 11th lord", subject="L11"),
        # D10
        rule("career_d10_L10_dignified", C, "career.d10", "strong", "positive",
             [{"t": "varga_dignity", "d": 10, "p": "L10", "values": ["exalted", "own"]}],
             "The Rashi 10th lord is dignified in the Dashamsha, which tradition reads as confirmation of "
             "professional strength.", "D1 10th lord dignified in D10", subject="L10"),
        rule("career_d10_L10_debilitated", C, "career.d10", "moderate", "negative",
             [{"t": "varga_dignity", "d": 10, "p": "L10", "values": ["debilitated"]}],
             "The Rashi 10th lord is debilitated in the Dashamsha; tradition advises patience in establishing a "
             "settled professional path.", "D1 10th lord debilitated in D10"),
        rule("career_d10_lagnalord_good", C, "career.d10", "moderate", "positive",
             [{"t": "varga_house", "d": 10, "p": "D10L1", "h": [1, 4, 5, 7, 9, 10, 11]}],
             "The Dashamsha Lagna lord is well placed in the D10, supporting career growth.",
             "D10 Lagna lord in a good house"),
        rule("career_d10_lagnalord_dusthana", C, "career.d10", "moderate", "negative",
             [{"t": "varga_house", "d": 10, "p": "D10L1", "h": [6, 8, 12]}],
             "The Dashamsha Lagna lord falls in a dusthana of the D10; tradition associates this with obstacles or "
             "changes before the career stabilises.", "D10 Lagna lord in a dusthana"),
        rule("career_d10_10th_occupied_strong", C, "career.d10", "moderate", "positive",
             [{"t": "varga_occupied", "d": 10, "h": 10, "by": ["Sun", "Mars", "Jupiter", "Saturn", "Mercury", "Venus", "Moon"]}],
             "Planets occupy the 10th house of the Dashamsha, giving the career clear visibility in the chart of "
             "profession.", "Planets in the D10 10th house"),
        rule("career_d10_10th_lord_kendra", C, "career.d10", "minor", "positive",
             [{"t": "varga_house", "d": 10, "p": "D10L10", "h": [1, 4, 7, 10]}],
             "The 10th lord of the Dashamsha occupies a kendra in the D10, a supportive factor for professional "
             "standing.", "D10 10th lord in a kendra"),
        # Yogas
        yoga_rule(C, ["raja_kendra_trikona", "yogakaraka"], "career.yoga",
                  "Raja Yoga factors in this chart are traditionally associated with rise in status, especially during "
                  "the periods of the planets that form them.", "major"),
        yoga_rule(C, ["dharma_karmadhipati"], "career.yoga",
                  "Dharma-Karmadhipati Yoga links fortune with profession, associated with a respected, purposeful "
                  "career.", "major"),
        yoga_rule(C, ["ruchaka", "bhadra", "hamsa", "malavya", "sasa"], "career.yoga",
                  "A Pancha Mahapurusha Yoga gives a dignified planet in a kendra, traditionally associated with "
                  "distinction in the field that planet signifies.", "strong"),
        yoga_rule(C, ["amala"], "career.yoga",
                  "Amala Yoga is associated with an ethical reputation in one's work.", "moderate"),
        yoga_rule(C, ["neecha_bhanga"], "career.yoga",
                  "Neecha Bhanga Raja Yoga is associated with rising after early difficulties.", "moderate"),
    ]
    for element, text in (
        ("fire", "The 10th house is in a fire sign, which tradition links with initiative, leadership and a desire "
                 "for independence in work."),
        ("earth", "The 10th house is in an earth sign, which tradition links with practical, structured and "
                  "tangible work."),
        ("air", "The 10th house is in an air sign, which tradition links with communication, ideas, trade and "
                "networks."),
        ("water", "The 10th house is in a water sign, which tradition links with care, public service, emotional "
                  "intelligence and changing environments."),
    ):
        rules.append(rule(f"career_10_{element}", C, "career.style", "minor", "neutral",
                          [{"t": "house_element", "h": 10, "e": element}], text, f"10th house in a {element} sign"))
    return rules


RULES = build_rules()


def career_themes(ctx: ChartContext) -> dict:
    """Tally which grahas influence the 10th house complex to identify
    traditional career themes. Each influence is listed with its reason."""
    c = ctx.chart
    tally: Counter = Counter()
    reasons: dict[str, list[str]] = {}

    def add(p, w, why):
        tally[p] += w
        reasons.setdefault(p, []).append(why)

    add(c.house_lord(10), 3, "10th lord")
    for p in c.occupants(10):
        add(p, 3, "occupies the 10th house")
    for a in c.aspects_on_house(10):
        if a["planet"] not in ("Rahu", "Ketu"):
            add(a["planet"], 1, "aspects the 10th house")
    d10_l1 = ctx.resolve("D10L1")
    add(d10_l1, 2, "Dashamsha Lagna lord")
    d10_l10 = ctx.resolve("D10L10")
    add(d10_l10, 1, "Dashamsha 10th lord")
    for p in PLANETS:
        if c.planets[p].vargas["10"]["house"] == 10:
            add(p, 2, "occupies the 10th house of the Dashamsha")
    add(c.house_lord(1), 1, "Lagna lord")
    ranked = [p for p, _ in sorted(tally.items(), key=lambda kv: (-kv[1], PLANETS.index(kv[0])))][:3]
    styles = []
    for p in ranked:
        s = WORK_STYLE[p]
        if s not in styles:
            styles.append(s)
    return {
        "dominantPlanets": [{"planet": p, "score": tally[p], "why": reasons[p], "fields": CAREER_FIELDS[p]}
                            for p in ranked],
        "workStyles": [WORK_STYLE_TEXT[s] for s in styles],
        "note": ("These fields are traditional significations of the planets that most influence the 10th house "
                 "complex. They indicate themes, not a guaranteed profession."),
    }


def analyze(ctx: ChartContext, dasha_tree: list[dict], now: dt.datetime) -> dict:
    matches = run_rules(ctx, RULES)
    out = synthesize("career", matches, THEMES)
    out["themes"] = career_themes(ctx)
    sig = significator_set(ctx, ["L10", "L1", "D10L1"], occupied_houses=[10])
    out["timing"] = {
        "windows": timing_windows(dasha_tree, sig, now, now + dt.timedelta(days=365.25 * 20)),
        "method": ("Antardasha periods in the next 20 years whose lord is a career significator (10th lord, Lagna "
                   "lord, Dashamsha Lagna lord or a planet in the 10th). 'Primary' periods have significators as both "
                   "Mahadasha and Antardasha lord."),
    }
    c = ctx.chart
    out["keyFactors"] = [
        {"label": "10th house", "value": f"{RASHIS[c.house_sign(10)]} ({RASHI_ELEMENT[c.house_sign(10)]})"},
        {"label": "10th lord", "value": f"{c.house_lord(10)} in the {ordinal(c.house_of(c.house_lord(10)))} house, "
                                        f"{c.planets[c.house_lord(10)].dignity}"},
        {"label": "Planets in 10th", "value": ", ".join(c.occupants(10)) or "None"},
        {"label": "Aspects on 10th", "value": ", ".join(a["planet"] for a in c.aspects_on_house(10)) or "None"},
        {"label": "D10 Lagna", "value": RASHIS[c.ascendant.vargas["10"]["sign"]]},
        {"label": "D10 Lagna lord", "value": f"{ctx.resolve('D10L1')} in D10 house "
                                             f"{c.planets[ctx.resolve('D10L1')].vargas['10']['house']}"},
    ]
    return out

