"""Plain-language explanation of a finished report.

Builds a beginner-friendly walkthrough ("Your Kundali Explained") from the
already-calculated report. Every sentence is a fixed template filled with
calculated values or with matched rule results; nothing is generated freely.
"""

from __future__ import annotations

import datetime as dt
import re

from ..jyotish.constants import ordinal
from ..rules.data.meaning import (AREA_LORD_HOUSE, HOUSE_LIFE, LAGNA_YOU, LORD_YOU, PERIOD_HOUSE_YOU,
                                  PLANET_ENERGY, PLANET_YOU, THEME_YOU, TONE_ADVICE)
from ..jyotish.constants import RASHIS

HOUSE_PLAIN = {
    1: "self and body", 2: "money, family and speech", 3: "courage, effort and siblings",
    4: "home, mother and inner peace", 5: "intelligence, studies, creativity and children",
    6: "daily work, competition and health routines", 7: "marriage and partnerships",
    8: "sudden change, research and shared resources", 9: "luck, beliefs, teachers and father",
    10: "career and reputation", 11: "income, gains and friendships", 12: "expenses, foreign lands and rest",
}

PLANET_PLAIN = {
    "Sun": "your sense of self, confidence, authority and your father",
    "Moon": "your mind, emotions, comfort needs and your mother",
    "Mars": "your energy, courage, drive and how you handle conflict",
    "Mercury": "your thinking, speech, learning style and business sense",
    "Jupiter": "your wisdom, luck, teachers, growth and (traditionally) children",
    "Venus": "your relationships, love, beauty, comfort and enjoyment",
    "Saturn": "your discipline, patience, responsibilities and long-term effort",
    "Rahu": "your ambitions, cravings and attraction to the new or foreign",
    "Ketu": "your detachment, intuition, spirituality and what comes naturally from the past",
}

SIGN_FLAVOUR = {
    "Aries": "bold, quick and pioneering", "Taurus": "steady, patient and comfort-loving",
    "Gemini": "curious, talkative and adaptable", "Cancer": "caring, sensitive and protective",
    "Leo": "proud, warm and leadership-minded", "Virgo": "careful, analytical and helpful",
    "Libra": "fair, diplomatic and relationship-minded", "Scorpio": "intense, private and determined",
    "Sagittarius": "optimistic, principled and freedom-loving", "Capricorn": "disciplined, practical and ambitious",
    "Aquarius": "independent, thoughtful and idealistic", "Pisces": "gentle, imaginative and compassionate",
}

DIGNITY_PLAIN = {
    "exalted": "at its very best (exalted)", "moolatrikona": "very strong (in its moolatrikona sign)",
    "own": "at home and confident (its own sign)", "great friend": "very comfortable (a close friend's sign)",
    "friend": "comfortable (a friendly sign)", "neutral": "in neutral territory",
    "enemy": "somewhat uncomfortable (an unfriendly sign)", "great enemy": "uncomfortable (a hostile sign)",
    "debilitated": "at its weakest (debilitated)",
}

AREA_ORDER = [
    ("education", "Education and learning", [4, 5, 9]),
    ("career", "Career and work", [10, 6]),
    ("wealth", "Money and finances", [2, 11]),
    ("family", "Family and home", [2, 4]),
    ("marriage", "Love and marriage", [7]),
    ("children", "Children", [5]),
    ("travel", "Travel and living abroad", [9, 12]),
    ("health", "Health tendencies", [1, 6, 8]),
]

GLOSSARY = [
    ("Kundali / Janma Patrika / China", "A map of the sky at the exact moment and place of your birth, divided into 12 houses."),
    ("Graha", "One of the nine 'planets' of Jyotish: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn and the two lunar nodes Rahu and Ketu."),
    ("Rashi", "One of the 12 zodiac signs (Mesha/Aries … Meena/Pisces). Each graha sits in a sign, which colours how it behaves."),
    ("Lagna (Ascendant)", "The sign rising on the eastern horizon at birth. It becomes your 1st house and describes you as a person."),
    ("Bhava (House)", "One of the 12 areas of life, such as career (10th) or marriage (7th)."),
    ("House lord", "The graha that rules the sign on a house. Where that graha sits shows where that area of life is directed."),
    ("Janma Rashi", "The sign the Moon was in at birth: your 'Moon sign', used for your name syllable and for transits."),
    ("Nakshatra", "One of 27 star-segments of 13°20' each. Your birth nakshatra is the one the Moon occupied; each has 4 padas (quarters)."),
    ("Dasha", "A planetary period. Life is divided into periods ruled by different grahas (Mahadasha, with sub-periods called Antardasha)."),
    ("Gochar", "The current movement of the grahas (transits), read against your birth chart."),
    ("Sade Sati", "The roughly 7½ years when Saturn passes over and around your Moon sign; a time of responsibility and maturing."),
    ("Yoga", "A specific combination of grahas with a traditional meaning, e.g. Gaja Kesari Yoga."),
    ("Dosha", "A combination traditionally treated with caution, e.g. Mangal Dosha; often softened by other factors."),
    ("Drishti (Aspect)", "The 'glance' one graha casts on other houses; all grahas look at the 7th house from themselves, some at others too."),
    ("Navamsa (D9) / Dashamsha (D10)", "Divisional charts that zoom in on marriage/inner strength (D9) and career (D10)."),
    ("Exalted / Debilitated", "The sign where a graha is at its strongest / weakest."),
    ("Retrograde", "A graha that appears to move backwards from Earth; traditionally its results are inward or revisited."),
    ("Combust", "A graha so close to the Sun that its qualities are traditionally overshadowed."),
]


def _strength_word(report: dict, planet: str) -> str:
    sb = (report.get("shadbala") or {}).get("planets", {}).get(planet)
    pl = next(p for p in report["chart"]["planets"] if p["name"] == planet)
    if pl["dignity"] in ("exalted", "moolatrikona", "own") or (sb and sb["ratio"] >= 1.25):
        return "strong"
    if pl["dignity"] == "debilitated" or pl["combust"] or (sb and sb["ratio"] < 0.9):
        return "needs support"
    return "steady"


def _balance_phrase(balance: float | None) -> str:
    if balance is None:
        return "There are few specific indicators either way here."
    if balance >= 0.75:
        return "This area looks clearly supported in your chart."
    if balance >= 0.55:
        return "This area is supported overall, with a few things to watch."
    if balance >= 0.45:
        return "This area is mixed: good and difficult signs balance out, so effort and timing matter most."
    return "This area asks for more conscious effort; the chart shows more challenges than supports here."


_GENERIC = re.compile(r"_(L\d+|Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn|Rahu|Ketu)_in_\d+$")


def _pick(matches: list[dict], polarity: str, n: int) -> list[dict]:
    """Choose individual rule matches for the plain summary: domain-specific
    rules first (highest weight, one per theme); general house-lord /
    planet-in-house texts, which describe a whole house, only fill gaps."""
    pool = sorted((m for m in matches if m["polarity"] == polarity), key=lambda m: (-m["weight"], m["ruleId"]))
    specific = [m for m in pool if not _GENERIC.search(m["ruleId"])]
    generic = [m for m in pool if _GENERIC.search(m["ruleId"])]
    out, themes = [], set()
    for m in specific + generic:
        if m["theme"] in themes:
            continue
        themes.add(m["theme"])
        out.append(m)
        if len(out) == n:
            break
    return out


def _verdict(balance: float | None) -> str:
    if balance is None:
        return "Your chart has no strong indications either way here."
    if balance >= 0.75:
        return "This is one of the stronger areas of your life."
    if balance >= 0.55:
        return "This area works well for you overall, with a few things to manage."
    if balance >= 0.45:
        return "This area is mixed for you: results depend on your effort and timing."
    return "This area asks more of you. Expect to work harder here, and it pays off when you do."


def _personal(r: dict, key: str, chart: dict) -> tuple[list[dict], list[str]]:
    """What the area means for you (second person) and what you can do."""
    meaning, advice = [], []
    lord_house_num = AREA_LORD_HOUSE.get(key)
    if lord_house_num:
        lord = chart["houses"][lord_house_num - 1]["lord"]
        lp = next(p for p in chart["planets"] if p["name"] == lord)
        meaning.append({"text": LORD_YOU[key][lp["house"]],
                        "why": [f"The ruler of your {ordinal(lord_house_num)} house ({lord}) sits in your "
                                f"{ordinal(lp['house'])} house."]})
    groups = sorted(r["strengths"] + r["challenges"] + r["notes"], key=lambda g: -g["weight"])
    seen = set()
    for g in groups:
        entry = THEME_YOU.get(g["theme"], {}).get(g["polarity"])
        if not entry or g["theme"] in seen:
            continue
        # Skip themes led by the lord placement already explained above.
        if lord_house_num and re.search(rf"(^|_)L{lord_house_num}_in_\d+$", g["ruleIds"][0]):
            continue
        seen.add(g["theme"])
        meaning.append({"text": entry[0], "why": g["why"][:3], "tone": g["polarity"]})
        if entry[1] not in advice:
            advice.append(entry[1])
        if len(meaning) >= 5:
            break
    return meaning, advice[:4]


def _fmt(iso: str) -> str:
    return dt.datetime.fromisoformat(iso).strftime("%b %Y")


def explain(report: dict) -> dict:
    s = report["summary"]
    i = report["interpretation"]
    chart = report["chart"]
    name = report["birth"]["name"]

    # 1. Intro --------------------------------------------------------------
    intro = [
        "A Kundali is a map of the sky at the exact moment and place you were born. It has 12 'houses', each "
        "standing for an area of life, and nine grahas (planets) placed among them. Where each graha sits, and how "
        "comfortable it is there, is what Jyotish reads.",
        "Below is your chart in plain language. Each point is followed by a short reason so you can see which part "
        "of the chart it comes from. The detailed sections further down give the full classical reasoning.",
    ]

    # 2. Core identity ------------------------------------------------------
    lagna = s["lagna"]
    moon = s["janmaRashi"]
    lf = i["lagna"]["facts"]
    lord_house = lf["lagnaLordHouse"]
    m = i["moon"]
    core = [
        {"title": "How you come across (your Lagna)",
         "text": (f"Your rising sign is {lagna}, so your outer personality is traditionally {SIGN_FLAVOUR[lagna]}. "
                  f"{i['lagna']['signProfile']['temperament']} {i['lagna']['signProfile']['behaviour']}"),
         "forYou": LAGNA_YOU[RASHIS.index(lagna)],
         "why": [f"{lagna} was rising in the east at your birth time ({s['lagnaDegree']})."]},
        {"title": "Where your life energy goes",
         "text": (f"The ruler of your Lagna is {lf['lagnaLord']}, and it sits in your {ordinal(lord_house)} house, the "
                  f"area of {HOUSE_PLAIN[lord_house]}. Tradition reads this as a life that naturally turns towards "
                  f"{HOUSE_PLAIN[lord_house]}."),
         "why": [f"{lagna} is ruled by {lf['lagnaLord']}; {lf['lagnaLord']} is in the {ordinal(lord_house)} house."]},
        {"title": "Your inner self (your Moon sign)",
         "text": f"Your Moon sign (Janma Rashi) is {moon}. {m['items'][0]['text']}",
         "why": [f"The Moon was in {moon} at {m['moonDegree']}."]},
        {"title": "Your birth star (Nakshatra)",
         "text": (f"You were born in {m['nakshatra']} nakshatra, pada {m['pada']}, ruled by {m['nakshatraLord']}. "
                  f"{m['nakshatraInterpretation']}"),
         "why": [f"The Moon's position falls in {m['nakshatra']} (deity: {m['deity']}; symbol: {m['symbol']})."]},
    ]

    # 3. Grahas ---------------------------------------------------------------
    grahas = []
    for p in chart["planets"]:
        n = p["name"]
        detail = i["planets"][n]
        place_text = detail["items"][0]["text"]
        word = _strength_word(report, n)
        comfort = (DIGNITY_PLAIN.get(p["dignity"], p["dignity"]) if n not in ("Rahu", "Ketu")
                   else "read through the sign's ruler")
        extra = []
        if p["retrograde"] and n not in ("Rahu", "Ketu"):
            extra.append("It is retrograde, so its themes tend to be revisited and mature with time.")
        if p["combust"]:
            extra.append("It is very close to the Sun (combust), so its qualities may need conscious effort to shine.")
        you_tbl = PLANET_YOU[n]
        for_you = you_tbl.get(word) or you_tbl["steady"]
        for_you += (f" In your chart this plays out mainly through {HOUSE_LIFE[p['house']]}: that is where "
                    f"{PLANET_ENERGY[n]} gets directed.")
        grahas.append({
            "planet": n,
            "forYou": for_you,
            "headline": f"{n} in {p['signName']}, {ordinal(p['house'])} house: {word}",
            "strength": word,
            "text": (f"{n} stands for {PLANET_PLAIN[n]}. In your chart it sits in the {ordinal(p['house'])} house "
                     f"({HOUSE_PLAIN[p['house']]}) in {p['signName']}, where it is {comfort}. {place_text} "
                     + " ".join(extra)).strip(),
            "why": [f"{n} at {p['degreeLabel']} {p['signName']}, {ordinal(p['house'])} house, {p['nakshatraName']} "
                    f"nakshatra" + (f"; Shadbala {report['shadbala']['planets'][n]['ratio']}× the required minimum"
                                    if report.get("shadbala") and n in report["shadbala"]["planets"] else "")],
        })

    # 4. Life areas -----------------------------------------------------------
    areas = []
    for key, title, houses in AREA_ORDER:
        r = i[key]
        points = []
        for m in _pick(r["matches"], "positive", 2):
            points.append({"tone": "good", "text": m["text"], "why": m["reasons"][:3]})
        for m in _pick(r["matches"], "negative", 2):
            points.append({"tone": "watch", "text": m["text"], "why": m["reasons"][:3]})
        for m in _pick(r["matches"], "mixed", 1):
            points.append({"tone": "note", "text": m["text"], "why": m["reasons"][:3]})
        house_line = "; ".join(
            f"{ordinal(h)} house ({HOUSE_PLAIN[h]}) is in {chart['houses'][h - 1]['signName']}, ruled by "
            f"{chart['houses'][h - 1]['lord']}" for h in houses)
        timing = []
        for w in (r.get("timing") or {}).get("windows", [])[:3]:
            timing.append(f"{w['mahadasha']}–{w['antardasha']} period: {_fmt(w['start'])} to {_fmt(w['end'])}")
        extra = None
        if key == "career":
            th = r["themes"]
            fields = [f for d in th["dominantPlanets"][:2] for f in d["fields"][:3]]
            extra = ("Fields traditionally linked to your chart: " + ", ".join(fields) +
                     ". These are tendencies, not a guaranteed profession.")
        meaning, advice = _personal(r, key, chart)
        areas.append({
            "key": key,
            "title": title,
            "verdict": _verdict(r["balance"]),
            "meaning": meaning,
            "advice": advice,
            "balance": r["balance"],
            "summary": _balance_phrase(r["balance"]),
            "houses": house_line,
            "points": points,
            "extra": extra,
            "timing": timing,
            "disclaimer": r.get("disclaimer"),
        })

    # 5. Current period -------------------------------------------------------
    cur = report["dasha"]["current"]
    period = None
    if cur:
        md = cur[0]
        ad = cur[1] if len(cur) > 1 else None
        acts = (i.get("currentDasha") or {}).get("activations", [])
        text = (f"You are now in the {md['lord']} Mahadasha (major period) from {_fmt(md['start'])} to "
                f"{_fmt(md['end'])}" + (f", and within it the {ad['lord']} Antardasha (sub-period) until "
                                        f"{_fmt(ad['end'])}." if ad else "."))
        cd = i.get("currentDasha") or {}
        for_you = []
        for lvl in (md, ad):
            if not lvl:
                continue
            lord = lvl["lord"]
            owned = [h["house"] for h in chart["houses"] if h["lord"] == lord]
            lp = next(p for p in chart["planets"] if p["name"] == lord)
            focus = [PERIOD_HOUSE_YOU[lp["house"]]] + [PERIOD_HOUSE_YOU[h] for h in owned if h != lp["house"]]
            focus = [focus[0]] + [f.replace("a focus on ", "") for f in focus[1:3]]
            label = "major period" if lvl is md else "current sub-period"
            joined = focus[0] if len(focus) == 1 else ", ".join(focus[:-1]) + ", and also " + focus[-1]
            for_you.append(f"Your {lord} {label} ({_fmt(lvl['start'])} to {_fmt(lvl['end'])}) brings {joined}.")
        tone = acts[1]["tone"] if len(acts) > 1 else (acts[0]["tone"] if acts else "mixed")
        for_you.append(TONE_ADVICE.get(tone, TONE_ADVICE["mixed"]))
        upcoming = []
        md_full = next((p for p in report["dasha"]["periods"] if p["status"] == "current"), None)
        if md_full:
            subs = md_full.get("children", [])
            idx = next((k for k, x in enumerate(subs) if x["status"] == "current"), None)
            if idx is not None and idx + 1 < len(subs):
                nxt = subs[idx + 1]
                upcoming.append(f"From {_fmt(nxt['start'])}: {md_full['lord']}–{nxt['lord']} sub-period begins.")
            mdi = report["dasha"]["periods"].index(md_full)
            if mdi + 1 < len(report["dasha"]["periods"]):
                nmd = report["dasha"]["periods"][mdi + 1]
                upcoming.append(f"From {_fmt(nmd['start'])}: your {nmd['lord']} major period begins, a new chapter "
                                f"lasting about {round(nmd['durationYears'])} years.")
        nxt_ss = next((c for c in report["sadesati"]["cycles"] if c["status"] == "upcoming"), None)
        if report["sadesati"]["active"]:
            cyc = report["sadesati"]["currentCycle"]
            upcoming.append(f"Sade Sati is running until {_fmt(cyc['end'])}.")
        elif nxt_ss:
            upcoming.append(f"Your next Sade Sati begins around {_fmt(nxt_ss['start'])}.")
        period = {
            "forYou": for_you,
            "upcoming": upcoming,
            "text": text,
            "themes": [a["theme"] for a in acts[:2]],
            "activation": [a["activation"] for a in acts[:2]],
            "summary": _balance_phrase(cd.get("balance")).replace("This area", "This period"),
            "sadeSati": (f"Sade Sati: {s['sadeSati']}. " +
                         ("Saturn is passing near your Moon sign, a period tradition associates with responsibility "
                          "and maturing rather than simple misfortune." if report["sadesati"]["active"] else
                          "Saturn is not currently over your Moon sign.")),
        }

    # 6. Yogas & doshas -------------------------------------------------------
    yogas = [{"name": y["name"], "strength": y["strength"], "text": y["text"]}
             for y in i["yogas"]["detected"] if y["group"] != "adverse"][:6]
    doshas = [{"name": d["name"], "status": d["status"], "text": d["text"]}
              for d in i["doshas"] if d["detected"]]

    ranked = sorted((a for a in areas if a["balance"] is not None), key=lambda a: -a["balance"])
    strong = [a["title"].lower() for a in ranked if a["balance"] >= 0.6][:3]
    effort = [a["title"].lower() for a in reversed(ranked) if a["balance"] < 0.5][:2]
    glance = [LAGNA_YOU[RASHIS.index(lagna)]]
    glance.append(f"Your life energy naturally flows towards {HOUSE_LIFE[lord_house]}.")
    if strong:
        glance.append("Your strongest areas: " + "; ".join(strong) + ".")
    if effort:
        glance.append("Areas where effort pays off most: " + "; ".join(effort) + ".")
    best = next((g for g in grahas if g["strength"] == "strong"), None)
    weak = next((g for g in grahas if g["strength"] == "needs support"), None)
    if best:
        glance.append(f"Your strongest graha is {best['planet']}: {PLANET_YOU[best['planet']]['strong'].split('. ')[0]}.")
    if weak:
        glance.append(f"{weak['planet']} needs support: {PLANET_YOU[weak['planet']]['needs support'].split('. ')[0]}.")
    if period:
        glance.append(period["forYou"][0])

    return {
        "forName": name,
        "glance": glance,
        "intro": intro,
        "core": core,
        "grahas": grahas,
        "areas": areas,
        "period": period,
        "yogas": yogas,
        "doshas": doshas,
        "glossary": [{"term": t, "meaning": d} for t, d in GLOSSARY],
        "closing": ("Remember: Jyotish describes tendencies and timing in a traditional framework. Strong areas "
                    "show where things tend to flow; challenging areas show where effort pays off most. Nothing "
                    "here is fixed fate, and none of it replaces professional advice."),
    }
