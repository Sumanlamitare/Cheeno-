"""Twelve Bhavas: for every house - sign, lord, occupants, aspects, the
lord's placement, a transparent strength assessment, related yogas and the
matching classical interpretations."""

from __future__ import annotations

from ..jyotish.constants import DUSTHANAS, KENDRAS, RASHI_LORDS, RASHIS, UPACHAYAS, ordinal
from .data.houses import BHAVESHA, HOUSE_NAMES, HOUSE_TOPICS
from .data.planets import PLANET_IN_HOUSE
from .engine import ChartContext

ASSESSMENT_METHOD = (
    "House assessment (application convention): lord in exaltation/moolatrikona/own sign +2, friendly sign +1, "
    "enemy sign -1, great enemy/debilitated -2; lord in a kendra or trikona +1, in a dusthana -1 (not applied to "
    "dusthana lords); lord combust -1; each natural benefic occupant +1; each malefic occupant -1 (+1 in upachaya "
    "houses 3, 6, 10, 11); Jupiter's aspect +1; other benefic aspects +0.5; malefic aspects -0.5 (not in upachayas). "
    "Total of 3 or more = Strong, 0 to 2.5 = Moderate, below 0 = Weak."
)

MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}


def assess(ctx: ChartContext, h: int) -> tuple[str, float, list[str]]:
    c = ctx.chart
    lord = c.house_lord(h)
    pl = c.planets[lord]
    score = 0.0
    why = []
    dig = pl.dignity
    if dig in ("exalted", "moolatrikona", "own"):
        score += 2
        why.append(f"+2: lord {lord} is {'in its own sign' if dig == 'own' else dig}")
    elif dig in ("great friend", "friend"):
        score += 1
        why.append(f"+1: lord {lord} is in a {dig}'s sign")
    elif dig == "enemy":
        score -= 1
        why.append(f"-1: lord {lord} is in an enemy's sign")
    elif dig in ("great enemy", "debilitated"):
        score -= 2
        why.append(f"-2: lord {lord} is {'debilitated' if dig == 'debilitated' else 'in a great enemy sign'}")
    if pl.house in KENDRAS or pl.house in (5, 9):
        score += 1
        why.append(f"+1: lord placed in the {ordinal(pl.house)} (kendra/trikona)")
    elif pl.house in DUSTHANAS and h not in DUSTHANAS:
        score -= 1
        why.append(f"-1: lord placed in the {ordinal(pl.house)} (dusthana)")
    if pl.combust:
        score -= 1
        why.append(f"-1: lord {lord} is combust")
    for p in c.occupants(h):
        if p in MALEFICS or not c.planets[p].benefic:
            if h in UPACHAYAS:
                score += 1
                why.append(f"+1: malefic {p} in an upachaya house")
            else:
                score -= 1
                why.append(f"-1: malefic {p} occupies the house")
        else:
            score += 1
            why.append(f"+1: benefic {p} occupies the house")
    for a in c.aspects_on_house(h):
        p = a["planet"]
        if p in ("Rahu", "Ketu"):
            continue
        if p == "Jupiter":
            score += 1
            why.append("+1: Jupiter's aspect")
        elif c.planets[p].benefic:
            score += 0.5
            why.append(f"+0.5: benefic aspect of {p}")
        elif h not in UPACHAYAS:
            score -= 0.5
            why.append(f"-0.5: malefic aspect of {p}")
    label = "Strong" if score >= 3 else ("Moderate" if score >= 0 else "Weak")
    return label, score, why


def analyze(ctx: ChartContext) -> list[dict]:
    c = ctx.chart
    out = []
    for h in range(1, 13):
        sign = c.house_sign(h)
        lord = RASHI_LORDS[sign]
        lpl = c.planets[lord]
        label, score, why = assess(ctx, h)
        interp = []
        pol, text = BHAVESHA[h][lpl.house]
        interp.append({"text": text, "polarity": pol, "ruleId": f"house_L{h}_in_{lpl.house}",
                       "why": [f"{ordinal(h)} lord {lord} is in the {ordinal(lpl.house)} house ({RASHIS[lpl.sign]})"],
                       "sourceConcept": f"{ordinal(h)} lord in {ordinal(lpl.house)} house"})
        for p in c.occupants(h):
            pol, text = PLANET_IN_HOUSE[p][h]
            interp.append({"text": text, "polarity": pol, "ruleId": f"house_{p}_in_{h}",
                           "why": [f"{p} occupies the {ordinal(h)} house"], "sourceConcept": f"{p} in {ordinal(h)} house"})
        aspects = c.aspects_on_house(h)
        yogas = [y.to_dict() for y in ctx.yogas if h in y.houses]
        out.append({
            "house": h,
            "name": HOUSE_NAMES[h],
            "topics": HOUSE_TOPICS[h],
            "sign": sign,
            "signName": RASHIS[sign],
            "lord": lord,
            "lordHouse": lpl.house,
            "lordSign": RASHIS[lpl.sign],
            "lordDignity": lpl.dignity,
            "occupants": c.occupants(h),
            "aspects": [{"planet": a["planet"], "aspect": a["aspect"]} for a in aspects],
            "strength": label,
            "strengthScore": score,
            "strengthWhy": why,
            "yogas": [{"name": y["name"], "strength": y["strength"]} for y in yogas],
            "interpretation": interp,
        })
    return out
