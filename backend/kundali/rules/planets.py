"""Per-planet traditional significance for the expandable planetary table."""

from __future__ import annotations

from ..jyotish.constants import NAKSHATRAS, PLANETS, RASHIS, ordinal
from ..jyotish.drishti import aspected_signs
from .data.houses import HOUSE_TOPICS
from .data.planets import COMBUST_TEXT, DIGNITY_TEXT, KARAKA, PLANET_IN_HOUSE, RETRO_TEXT, VARGOTTAMA_TEXT
from .engine import ChartContext


def planet_detail(ctx: ChartContext, p: str) -> dict:
    c = ctx.chart
    pl = c.planets[p]
    items = []
    pol, text = PLANET_IN_HOUSE[p][pl.house]
    items.append({"text": text, "polarity": pol, "why": [f"{p} occupies the {ordinal(pl.house)} house ({RASHIS[pl.sign]})"],
                  "ruleId": f"planet_{p}_in_{pl.house}"})
    if p not in ("Rahu", "Ketu"):
        items.append({"text": DIGNITY_TEXT[pl.dignity].format(p=p),
                      "polarity": "positive" if pl.dignity in ("exalted", "moolatrikona", "own", "great friend", "friend")
                      else "negative" if pl.dignity in ("debilitated", "great enemy", "enemy") else "neutral",
                      "why": [f"{p} in {RASHIS[pl.sign]} at {pl.degree:.2f}° is {pl.dignity}"],
                      "ruleId": f"planet_{p}_dignity_{pl.dignity.replace(' ', '_')}"})
    else:
        items.append({"text": f"{p} acts largely through its dispositor, {c.house_lord(pl.house)}, the lord of "
                              f"{RASHIS[pl.sign]}, and through the planets it joins.",
                      "polarity": "neutral", "why": [f"{p} is in {RASHIS[pl.sign]}"], "ruleId": f"planet_{p}_dispositor"})
    owned = c.houses_ruled_by(p)
    if owned:
        items.append({"text": f"As lord of the {', '.join(ordinal(h) for h in owned)} house"
                              f"{'s' if len(owned) > 1 else ''}, {p} carries the matters of "
                              + "; ".join(HOUSE_TOPICS[h].lower() for h in owned)
                              + f" into the {ordinal(pl.house)} house.",
                      "polarity": "neutral",
                      "why": [f"{RASHIS[c.house_sign(h)]} on the {ordinal(h)} house is ruled by {p}" for h in owned],
                      "ruleId": f"planet_{p}_lordship"})
    if pl.retrograde and p not in ("Rahu", "Ketu"):
        items.append({"text": RETRO_TEXT.format(p=p), "polarity": "mixed", "why": [f"{p}'s daily motion is "
                      f"{pl.speed:.3f}°"], "ruleId": f"planet_{p}_retro"})
    if pl.combust:
        items.append({"text": COMBUST_TEXT.format(p=p, d=pl.sun_distance), "polarity": "negative",
                      "why": [f"{p} is {pl.sun_distance:.2f}° from the Sun"], "ruleId": f"planet_{p}_combust"})
    if pl.vargas["9"]["sign"] == pl.sign:
        items.append({"text": VARGOTTAMA_TEXT.format(p=p), "polarity": "positive",
                      "why": [f"{p} is in {RASHIS[pl.sign]} in both D1 and D9"], "ruleId": f"planet_{p}_vargottama"})
    aspects = [ordinal(((s - c.lagna_sign) % 12) + 1) for s in aspected_signs(p, pl.sign)]
    sb = ctx.shadbala["planets"].get(p) if ctx.shadbala else None
    return {
        "planet": p,
        "karaka": KARAKA[p],
        "items": items,
        "aspectsHouses": aspects,
        "nakshatraNote": f"In {NAKSHATRAS[pl.nakshatra]} nakshatra, pada {pl.pada}, ruled by {pl.nakshatra_lord}.",
        "navamsa": {"sign": pl.vargas["9"]["signName"], "dignity": pl.vargas["9"]["dignity"]},
        "shadbala": sb,
        "relationships": _relationships(c, p),
    }


def _relationships(c, p):
    from ..jyotish.dignity import compound_relation, natural_relation
    out = []
    for q in PLANETS:
        if q == p or q in ("Rahu", "Ketu") or p in ("Rahu", "Ketu"):
            continue
        out.append({"planet": q, "natural": natural_relation(p, q),
                    "compound": compound_relation(p, q, c.planets[p].sign, c.planets[q].sign)})
    return out


def analyze(ctx: ChartContext) -> dict:
    return {p: planet_detail(ctx, p) for p in PLANETS}
