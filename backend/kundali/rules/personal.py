"""Personal Answers: direct, graded answers to common life questions.

Each answer is a transparent points score over explicit classical factors.
Every factor that contributed is returned with its points, so the person can
see exactly why they got the answer. Tier thresholds are application
conventions (calibrated so that the top tier is uncommon), not astrological
certainties.
"""

from __future__ import annotations

from ..jyotish.constants import DUSTHANAS, KENDRAS, PLANETS, ordinal
from .data.planets import CAREER_FIELDS
from .engine import ChartContext

GOOD_HOUSES = KENDRAS | {5, 9, 11}
MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

STUDY_FIELDS = {
    "Sun": ["political science and public administration", "medicine", "management"],
    "Moon": ["psychology", "nursing and healthcare", "hospitality and nutrition"],
    "Mars": ["engineering", "surgery and medical sciences", "defence and sports science"],
    "Mercury": ["commerce, accounting and economics", "computer science and IT", "mathematics, languages and journalism"],
    "Jupiter": ["law", "finance and banking", "teaching, philosophy and religious studies"],
    "Venus": ["fine arts, music and design", "fashion, film and media", "hotel management"],
    "Saturn": ["civil and structural engineering", "history, geology and agriculture", "public policy and labour law"],
    "Rahu": ["computer science and emerging technology", "aviation and electronics", "foreign languages and international studies"],
    "Ketu": ["mathematics and coding", "research sciences", "philosophy and spiritual studies"],
}

WEALTH_SOURCE = {
    1: "your own effort and personal reputation", 2: "savings, family resources or a family business",
    3: "your skills, media, communication or self-employment", 4: "property, land, vehicles or real estate",
    5: "investments, intelligence and creative work", 6: "service, competitive jobs or lending",
    7: "business, trade and partnerships (including through your spouse)",
    8: "inheritance, insurance, joint funds or research", 9: "good fortune, your father, teaching or long-distance work",
    10: "your career, salary and professional status", 11: "networks, large organisations and multiple income streams",
    12: "foreign income, exports or work abroad",
}


class Score:
    def __init__(self) -> None:
        self.points = 0
        self.factors: list[dict] = []

    def add(self, pts: int, why: str) -> None:
        if pts == 0:
            return
        self.points += pts
        self.factors.append({"points": pts, "why": why})


def _pl(ctx, p):
    return ctx.chart.planets[p]


def _lord(ctx, h):
    return ctx.chart.house_lord(h)


def _yogas(ctx, *ids):
    return [y for y in ctx.yogas if y.id in ids]


def _name(planet: str, label: str) -> str:
    """'9th lord (higher learning)' + Moon -> '9th lord Moon (higher learning)'."""
    base, _, role = label.partition(" (")
    if base.startswith(planet):
        return base
    return f"{base} {planet}" + (f" ({role.rstrip(')')})" if role else "")


def _strength(ctx, s: Score, planet: str, label: str, strong: int = 2, weak: int = -2) -> None:
    if ctx.is_strong(planet):
        s.add(strong, f"{_name(planet, label)} is strong")
    elif ctx.is_weak(planet):
        s.add(weak, f"{_name(planet, label)} is weak")


def _placement(ctx, s: Score, planet: str, label: str, good: int = 1, bad: int = -1) -> None:
    h = _pl(ctx, planet).house
    if h in GOOD_HOUSES:
        s.add(good, f"{_name(planet, label)} is well placed in the {ordinal(h)} house")
    elif h in DUSTHANAS:
        s.add(bad, f"{_name(planet, label)} sits in the {ordinal(h)} house (a difficult house)")


def _aspect_or_in(ctx, planet: str, house: int) -> bool:
    if _pl(ctx, planet).house == house:
        return True
    return any(a["planet"] == planet for a in ctx.chart.aspects_on_house(house))


def _tier(points: int, tiers: list[tuple[int, str, str]]) -> dict:
    for threshold, label, text in tiers:
        if points >= threshold:
            return {"level": label, "text": text}
    return {"level": tiers[-1][1], "text": tiers[-1][2]}


def _influencers(ctx, houses, extra_specs=()) -> list[str]:
    """Planets influencing given houses (lords, occupants) plus extras, ranked."""
    tally: dict[str, int] = {}
    for h in houses:
        tally[_lord(ctx, h)] = tally.get(_lord(ctx, h), 0) + 3
        for p in ctx.chart.occupants(h):
            tally[p] = tally.get(p, 0) + 2
    for spec in extra_specs:
        p = ctx.resolve(spec)
        if p:
            tally[p] = tally.get(p, 0) + 2
    for p in list(tally):
        if ctx.is_strong(p):
            tally[p] += 1
    return [p for p, _ in sorted(tally.items(), key=lambda kv: (-kv[1], PLANETS.index(kv[0])))]


# ---------------------------------------------------------------------------
# Education
# ---------------------------------------------------------------------------

def education(ctx: ChartContext) -> dict:
    s = Score()
    _strength(ctx, s, _lord(ctx, 5), "5th lord (intelligence)")
    _placement(ctx, s, _lord(ctx, 5), "5th lord")
    _strength(ctx, s, _lord(ctx, 9), "9th lord (higher learning)")
    _placement(ctx, s, _lord(ctx, 9), "9th lord")
    _placement(ctx, s, _lord(ctx, 4), "4th lord (foundational education)")
    _strength(ctx, s, "Jupiter", "Jupiter, significator of knowledge", 2, -1)
    _strength(ctx, s, "Mercury", "Mercury, significator of intellect", 2, -1)
    if _aspect_or_in(ctx, "Jupiter", 5) or _aspect_or_in(ctx, "Jupiter", 9):
        s.add(1, "Jupiter influences the 5th or 9th house")
    d24 = ctx.resolve("D24L1")
    d24h = _pl(ctx, d24).vargas["24"]["house"]
    if d24h in GOOD_HOUSES:
        s.add(1, f"In the chart of learning (D24) the Lagna lord {d24} is well placed")
    elif d24h in DUSTHANAS:
        s.add(-1, f"In the chart of learning (D24) the Lagna lord {d24} is in a difficult house")
    if _yogas(ctx, "saraswati"):
        s.add(2, "Saraswati Yoga (learning and scholarship)")
    if any(y.strength != "Weak" for y in _yogas(ctx, "budha_aditya")):
        s.add(1, "Budha-Aditya Yoga (intelligence)")
    if _yogas(ctx, "hamsa", "bhadra"):
        s.add(1, "Hamsa or Bhadra Yoga (wisdom or intellect)")
    mal5 = [p for p in ctx.chart.occupants(5) if p in ("Saturn", "Rahu", "Ketu", "Mars")]
    if mal5 and not _aspect_or_in(ctx, "Jupiter", 5):
        s.add(-1, f"{', '.join(mal5)} in the 5th house without Jupiter's support (interruptions)")

    tier = _tier(s.points, [
        (9, "Advanced", "Your chart traditionally indicates advanced education: a master's degree, professional "
                        "qualification or doctoral-level study is well within reach."),
        (5, "Higher", "Your chart traditionally indicates a university degree, with postgraduate study possible if "
                      "you pursue it."),
        (1, "Graduate with effort", "Your chart traditionally indicates graduate-level education achieved through "
                                    "steady effort; further study is possible with persistence."),
        (-99, "Practical", "Your chart favours practical, skills-based or vocational learning; formal academic "
                           "study is possible but needs extra persistence."),
    ])
    infl = _influencers(ctx, [5, 9], ["D24L1"])
    for p in ("Mercury", "Jupiter"):
        if ctx.is_strong(p) and p not in infl[:2]:
            infl.insert(1, p)
    fields = []
    for p in infl[:3]:
        for f in STUDY_FIELDS[p][:2]:
            if f not in fields:
                fields.append(f)
    abroad = (_pl(ctx, _lord(ctx, 9)).house == 12 or _pl(ctx, _lord(ctx, 5)).house == 12
              or _pl(ctx, "Rahu").house in (5, 9))
    return {
        "question": "What is the highest level of education I will achieve, and what should I study?",
        "answer": tier["text"],
        "level": tier["level"],
        "score": s.points,
        "detailTitle": "Subjects that suit you",
        "details": fields[:5],
        "notes": (["Study abroad is traditionally indicated in your chart."] if abroad else []),
        "basis": f"Subjects come from the planets that most influence your 5th and 9th houses: {', '.join(infl[:3])}.",
        "factors": s.factors,
    }


# ---------------------------------------------------------------------------
# Wealth
# ---------------------------------------------------------------------------

def wealth(ctx: ChartContext) -> dict:
    s = Score()
    dhana = [y for y in _yogas(ctx, "dhana") if y.strength != "Weak"]
    if dhana:
        s.add(min(3, 1 + len(dhana)), f"{len(dhana)} Dhana Yoga combination(s) (wealth yogas)")
    if _yogas(ctx, "lakshmi"):
        s.add(3, "Lakshmi Yoga (prosperity)")
    if _yogas(ctx, "chandra_mangala"):
        s.add(1, "Chandra-Mangala Yoga (earning through enterprise)")
    if _yogas(ctx, "vasumati", "sunapha", "durudhara"):
        s.add(1, "A lunar wealth yoga (Vasumati / Sunapha / Durudhara)")
    if _yogas(ctx, "raja_kendra_trikona", "yogakaraka", "dharma_karmadhipati"):
        s.add(1, "Raja Yoga (status that brings resources)")
    _strength(ctx, s, _lord(ctx, 2), "2nd lord (savings)")
    _strength(ctx, s, _lord(ctx, 11), "11th lord (income)")
    _placement(ctx, s, _lord(ctx, 2), "2nd lord")
    _placement(ctx, s, _lord(ctx, 11), "11th lord")
    _strength(ctx, s, "Jupiter", "Jupiter, significator of wealth", 1, -1)
    _strength(ctx, s, "Venus", "Venus, significator of comfort", 1, 0)
    ben = [p for p in ctx.chart.occupants(2) + ctx.chart.occupants(11) if p in ("Jupiter", "Venus", "Mercury", "Moon")
           and ctx.chart.planets[p].benefic]
    if ben:
        s.add(1, f"{', '.join(ben)} in the 2nd or 11th house")
    if _aspect_or_in(ctx, "Jupiter", 2) or _aspect_or_in(ctx, "Jupiter", 11):
        s.add(1, "Jupiter influences the 2nd or 11th house")
    if _pl(ctx, _lord(ctx, 12)).house == 2:
        s.add(-1, "12th lord (expenses) sits in the 2nd house of savings")
    if _yogas(ctx, "shakata"):
        s.add(-1, "Shakata Yoga (ups and downs of fortune)")

    tier = _tier(s.points, [
        (11, "Wealthy", "Yes. Your chart carries strong classical wealth indications. Traditionally this points to "
                       "real affluence, well above average, especially in the favourable periods."),
        (7, "Prosperous", "Your chart traditionally indicates above-average prosperity: you are likely to become "
                          "financially well-off through the sources below."),
        (3, "Comfortable", "Your chart traditionally indicates a comfortable life built steadily: solid financial "
                           "security rather than great riches."),
        (-99, "Modest", "Your chart traditionally indicates that wealth comes through discipline and effort; "
                        "careful saving matters more for you than for most."),
    ])
    sources, seen = [], set()
    for p in [_lord(ctx, 11), _lord(ctx, 2)] + ctx.chart.occupants(11) + ctx.chart.occupants(2):
        h = _pl(ctx, p).house
        if h not in seen:
            seen.add(h)
            sources.append(WEALTH_SOURCE[h])
    infl = _influencers(ctx, [2, 11, 10])
    fields = []
    for p in infl[:3]:
        for f in CAREER_FIELDS[p][:2]:
            if f not in fields:
                fields.append(f)
    return {
        "question": "Will I be rich? How, and in which fields?",
        "answer": tier["text"],
        "level": tier["level"],
        "score": s.points,
        "detailTitle": "How your wealth is likely to come",
        "details": sources[:3],
        "secondaryTitle": "Fields traditionally linked to your wealth",
        "secondary": fields[:5],
        "basis": (f"Sources come from where your 2nd and 11th lords sit; fields come from the planets influencing "
                  f"your 2nd, 10th and 11th houses ({', '.join(infl[:3])})."),
        "notes": [],
        "factors": s.factors,
        "disclaimer": "Traditional indication only, not financial advice. No amount of wealth is guaranteed.",
    }


# ---------------------------------------------------------------------------
# Marriage
# ---------------------------------------------------------------------------

def marriage(ctx: ChartContext) -> dict:
    l7 = _lord(ctx, 7)
    h = Score()  # harmony
    _strength(ctx, h, l7, "7th lord (marriage)")
    _placement(ctx, h, l7, "7th lord")
    if _aspect_or_in(ctx, "Jupiter", 7) or (l7 != "Jupiter" and ctx.chart.is_aspected_by(l7, "Jupiter")) or _pl(ctx, "Jupiter").sign == _pl(ctx, l7).sign:
        h.add(2, "Jupiter protects the 7th house or its lord")
    _strength(ctx, h, "Venus", "Venus, significator of love", 1, -1)
    if _pl(ctx, l7).vargas["9"]["dignity"] in ("exalted", "own"):
        h.add(1, "7th lord is dignified in the Navamsa (marriage chart)")
    if _pl(ctx, "Venus").vargas["9"]["dignity"] in ("exalted", "own"):
        h.add(1, "Venus is dignified in the Navamsa")
    if _pl(ctx, "Venus").vargas["9"]["dignity"] == "debilitated":
        h.add(-1, "Venus is debilitated in the Navamsa")
    d9_7 = [p for p in PLANETS if ctx.chart.planets[p].vargas["9"]["house"] == 7]
    if any(p in ("Jupiter", "Venus", "Mercury", "Moon") for p in d9_7):
        h.add(1, "A benefic occupies the 7th house of the Navamsa")
    if any(p in ("Saturn", "Mars", "Rahu", "Ketu") for p in d9_7):
        h.add(-1, "A malefic occupies the 7th house of the Navamsa")

    r = Score()  # separation-risk indicators (counted only when present)
    if _pl(ctx, l7).house in DUSTHANAS:
        r.add(1, f"7th lord {l7} sits in the {ordinal(_pl(ctx, l7).house)} house")
    if _pl(ctx, l7).dignity == "debilitated":
        r.add(1, f"7th lord {l7} is debilitated")
    mal7 = [p for p in ctx.chart.occupants(7) if p in MALEFICS]
    if mal7 and not _aspect_or_in(ctx, "Jupiter", 7):
        r.add(1, f"{', '.join(mal7)} in the 7th house without Jupiter's protection")
    vmal = [p for p in ("Mars", "Rahu", "Saturn", "Ketu") if _pl(ctx, p).sign == _pl(ctx, "Venus").sign]
    if vmal:
        r.add(1, f"Venus is joined by {', '.join(vmal)}")
    mangal = ctx.dosha("mangal")
    if mangal and mangal["detected"] and not mangal["mitigations"]:
        r.add(1, "Mangal Dosha without mitigating factors")
    if _pl(ctx, "Rahu").house in (1, 7):
        r.add(1, "Rahu-Ketu across the 1st and 7th houses")
    if _pl(ctx, ctx.resolve("D9L7")).vargas["9"]["house"] in DUSTHANAS:
        r.add(1, "Navamsa 7th lord in a difficult house")
    if _pl(ctx, _lord(ctx, 12)).house == 7 or _pl(ctx, _lord(ctx, 6)).house == 7:
        r.add(1, "6th or 12th lord occupies the 7th house")

    happy = _tier(h.points, [
        (6, "Very happy", "Your marriage is traditionally indicated as happy and well supported: affection, "
                          "respect and a caring partner."),
        (3, "Happy", "Your marriage is traditionally indicated as happy overall, with ordinary ups and downs."),
        (0, "Mixed", "Your marriage is traditionally indicated as mixed: real happiness is possible, and it grows "
                     "with patience and communication."),
        (-99, "Needs work", "Your chart traditionally indicates that marital happiness takes conscious effort and "
                            "careful choice of partner."),
    ])
    risk_level = "Low" if r.points <= 1 else ("Moderate" if r.points <= 3 else "Elevated")
    if h.points >= 5 and risk_level == "Elevated":
        risk_level = "Moderate"
    risk_text = {
        "Low": "Traditional indicators of separation or divorce are low in your chart. The marriage is "
               "indicated as stable.",
        "Moderate": "Some traditional indicators of strain appear in your chart. This is common and does not mean "
                    "divorce; it points to periods that need patience, honest communication and fairness.",
        "Elevated": "Several traditional indicators of marital strain appear in your chart. Tradition does not take "
                    "this as a sentence: choosing a compatible partner, Kundali matching and steady communication are "
                    "traditionally advised, and many such charts have lasting marriages.",
    }[risk_level]
    healthy = ("The relationship is traditionally indicated as healthy and mutually supportive."
               if h.points >= 3 and risk_level == "Low" else
               "The relationship is traditionally indicated as fundamentally sound, with areas to nurture."
               if h.points >= 0 else
               "Building a healthy relationship is traditionally indicated as a growth area: clear communication and "
               "shared values matter a lot for you.")
    return {
        "question": "Will my marriage be happy and healthy? Is divorce indicated?",
        "answer": f"{happy['text']} {risk_text}",
        "level": happy["level"],
        "score": h.points,
        "detailTitle": "Your marriage at a glance",
        "details": [f"Happiness: {happy['level']}", f"Separation-risk indicators: {risk_level}", f"Health: {healthy}"],
        "basis": "Happiness uses the 7th house and its lord, Venus, Jupiter and the Navamsa; separation risk counts "
                 "specific classical affliction factors.",
        "notes": ["No chart can decide whether a marriage will end; that depends on two people's choices."],
        "factors": h.factors + [{"points": -f["points"], "why": f"Risk factor: {f['why']}"} for f in r.factors],
    }


# ---------------------------------------------------------------------------
# Career
# ---------------------------------------------------------------------------

def career(ctx: ChartContext, career_themes: dict) -> dict:
    s = Score()
    raja = _yogas(ctx, "raja_kendra_trikona", "yogakaraka")
    if raja:
        best = "Strong" if any(y.strength == "Strong" for y in raja) else "Moderate"
        s.add(3 if best == "Strong" else 2, f"Raja Yoga ({best.lower()})")
    if _yogas(ctx, "dharma_karmadhipati"):
        s.add(2, "Dharma-Karmadhipati Yoga (purposeful, respected career)")
    mp = _yogas(ctx, "ruchaka", "bhadra", "hamsa", "malavya", "sasa")
    if mp:
        s.add(2, f"{mp[0].name} (distinction in its field)")
    if _yogas(ctx, "amala"):
        s.add(1, "Amala Yoga (reputation)")
    if _yogas(ctx, "neecha_bhanga"):
        s.add(1, "Neecha Bhanga Raja Yoga (rise after early difficulty)")
    _strength(ctx, s, _lord(ctx, 10), "10th lord (career)")
    _placement(ctx, s, _lord(ctx, 10), "10th lord")
    if ctx.is_strong("Sun") and _pl(ctx, "Sun").house in KENDRAS:
        s.add(2, "Strong Sun in a kendra (authority)")
    if ctx.is_strong("Saturn"):
        s.add(1, "Strong Saturn (endurance, large organisations)")
    dig10 = [p for p in ctx.chart.occupants(10) if _pl(ctx, p).dignity in ("exalted", "moolatrikona", "own")]
    if dig10:
        s.add(1, f"Dignified {', '.join(dig10)} in the 10th house")
    if _pl(ctx, _lord(ctx, 10)).vargas["10"]["dignity"] in ("exalted", "own"):
        s.add(1, "10th lord dignified in the career chart (D10)")
    d10h = _pl(ctx, ctx.resolve("D10L1")).vargas["10"]["house"]
    if d10h in GOOD_HOUSES:
        s.add(1, "D10 Lagna lord well placed")
    elif d10h in DUSTHANAS:
        s.add(-1, "D10 Lagna lord in a difficult house")
    _strength(ctx, s, _lord(ctx, 1), "Lagna lord (self)", 1, -1)

    tier = _tier(s.points, [
        (12, "Top of field", "Your chart carries strong classical indications for reaching the top of your field: "
                             "heading an organisation, senior leadership or recognised authority."),
        (7, "Senior leadership", "Your chart traditionally indicates rising to senior or management level, leading "
                                 "teams or departments and being well known in your field."),
        (3, "Established professional", "Your chart traditionally indicates a solid, established career at a "
                                        "mid-to-senior level, respected for your competence."),
        (-99, "Steady rise", "Your chart traditionally indicates a steady career where advancement comes gradually "
                             "through persistence; your rise tends to come later rather than early."),
    ])
    fields = []
    for d in career_themes["dominantPlanets"]:
        for f in d["fields"][:2]:
            if f not in fields:
                fields.append(f)
    styles = career_themes["workStyles"]
    return {
        "question": "What field suits me, and how high am I likely to go?",
        "answer": tier["text"],
        "level": tier["level"],
        "score": s.points,
        "detailTitle": "Fields that suit you",
        "details": fields[:6],
        "secondaryTitle": "Work style",
        "secondary": styles,
        "basis": "Fields come from the planets most influencing your 10th house and career chart (D10): "
                 + ", ".join(d["planet"] for d in career_themes["dominantPlanets"]) + ".",
        "notes": ["These are tendencies, not a guaranteed profession or position."],
        "factors": s.factors,
    }


# ---------------------------------------------------------------------------
# Children
# ---------------------------------------------------------------------------

def children(ctx: ChartContext, reading: dict) -> dict:
    s = Score()
    _strength(ctx, s, _lord(ctx, 5), "5th lord (children)")
    _placement(ctx, s, _lord(ctx, 5), "5th lord")
    _strength(ctx, s, "Jupiter", "Jupiter, significator of children", 2, -1)
    if _aspect_or_in(ctx, "Jupiter", 5):
        s.add(1, "Jupiter influences the 5th house")
    d7 = ctx.resolve("D7L1")
    d7h = _pl(ctx, d7).vargas["7"]["house"]
    if d7h in GOOD_HOUSES:
        s.add(1, "Saptamsha (D7) Lagna lord well placed")
    elif d7h in DUSTHANAS:
        s.add(-1, "Saptamsha (D7) Lagna lord in a difficult house")
    tier = _tier(s.points, [
        (3, "Well supported", "Children are traditionally well supported in your chart and are indicated as a "
                              "source of joy."),
        (0, "Supported", "Children are traditionally supported in your chart, with ordinary responsibilities."),
        (-99, "Patience advised", "Tradition advises patience in matters of children. This is a symbolic indication, "
                                  "not a medical one."),
    ])
    timing = [f"{w['mahadasha']}–{w['antardasha']}" for w in (reading.get("timing") or {}).get("windows", [])[:3]]
    return {
        "question": "Will I have children? How many, boys or girls?",
        "answer": tier["text"],
        "level": tier["level"],
        "score": s.points,
        "detailTitle": "What this app does and does not say",
        "details": [
            "This app does not predict the number or sex of children.",
            "Classical counting rules for children contradict each other, and they amount to a fertility prediction.",
            "We deliberately do not predict a child's sex, because such predictions have been linked to "
            "sex-selection and harm.",
            "For any concern about having children, please consult a qualified doctor.",
        ],
        "basis": "Based on the 5th house and its lord, Jupiter and the Saptamsha (D7).",
        "notes": [],
        "factors": s.factors,
    }


def personal_answers(ctx: ChartContext, interp: dict) -> dict:
    return {
        "intro": ("Direct answers to the questions people most often ask. Each answer is a score over explicit "
                  "classical factors, shown under 'Why this answer'. These are traditional indications, not "
                  "guarantees: effort, choices and circumstances shape how they unfold."),
        "answers": [
            {"key": "education", "title": "Education", **education(ctx)},
            {"key": "wealth", "title": "Wealth", **wealth(ctx)},
            {"key": "marriage", "title": "Marriage", **marriage(ctx)},
            {"key": "career", "title": "Career", **career(ctx, interp["career"]["themes"])},
            {"key": "children", "title": "Children", **children(ctx, interp["children"])},
        ],
        "method": ("Scores add the points listed for each factor. Tier thresholds are application conventions "
                   "calibrated on 1,000 random charts so that the top tier is reached by only about one chart in ten."),
    }
