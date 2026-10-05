"""Gochar and Sade Sati interpretation."""

from __future__ import annotations

from ..jyotish.constants import ordinal
from .data.houses import HOUSE_TOPICS
from .data.transits import FAST_PLANET_THEME, GOCHAR_MAJOR, VEDHA_TEXT
from .data.yogas_doshas import SADE_SATI_TEXT
from .engine import ChartContext


def interpret_gochar(ctx: ChartContext, gochar: dict) -> list[dict]:
    out = []
    for row in gochar["rows"]:
        p, h = row["planet"], row["houseFromMoon"]
        if p in GOCHAR_MAJOR:
            text = GOCHAR_MAJOR[p][h]
        else:
            text = (f"{p} in the {ordinal(h)} from the Moon is traditionally "
                    f"{'favourable' if row['favourable'] else 'unfavourable'} for {FAST_PLANET_THEME[p]}; being a "
                    "faster-moving planet, its influence is short-lived.")
        notes = []
        if row["vedhaBy"]:
            notes.append(VEDHA_TEXT.format(by=", ".join(row["vedhaBy"])))
        if row["natalPlanetsInSign"]:
            notes.append(f"It passes over natal {', '.join(row['natalPlanetsInSign'])}, activating "
                         f"{'their' if len(row['natalPlanetsInSign']) > 1 else 'its'} significations.")
        why = [f"{p} transits {row['signName']} ({row['degree']:.1f}°{' R' if row['retrograde'] and p not in ('Rahu', 'Ketu') else ''})",
               f"{row['signName']} is the {ordinal(h)} sign from the natal Moon and the {ordinal(row['houseFromLagna'])} "
               f"from the Lagna"]
        out.append({
            "planet": p,
            "major": row["major"],
            "houseFromMoon": h,
            "houseFromLagna": row["houseFromLagna"],
            "natalHouseTopic": HOUSE_TOPICS[row["houseFromLagna"]],
            "result": row["result"],
            "text": text,
            "notes": notes,
            "why": why,
        })
    out.sort(key=lambda x: (not x["major"], ["Saturn", "Jupiter", "Rahu", "Ketu", "Sun", "Mars", "Mercury", "Venus", "Moon"].index(x["planet"])))
    return out


def interpret_sadesati(ctx: ChartContext, ss: dict) -> dict:
    c = ctx.chart
    sat = c.planets["Saturn"]
    items = [{"text": SADE_SATI_TEXT["overview"], "why": [f"Natal Moon in {ss['moonSign']}"]}]
    if ss["currentPhase"]:
        items.append({"text": SADE_SATI_TEXT[ss["currentPhase"]], "why": [f"Saturn now transits {ss['saturnSignNow']}"]})
    yk = any(y.id == "yogakaraka" and "Saturn" in y.planets for y in ctx.yogas)
    if yk:
        items.append({"text": SADE_SATI_TEXT["yogakaraka_saturn"], "why": ["Saturn rules a kendra and a trikona"]})
    if ctx.is_strong("Saturn"):
        reason = f"{sat.dignity} in {sat.sign_name}" if sat.dignity in ("exalted", "own", "moolatrikona") else "high Shadbala"
        items.append({"text": SADE_SATI_TEXT["favourable_saturn"].format(reason=reason), "why": [f"Saturn: {reason}"]})
    elif ctx.is_weak("Saturn"):
        reason = "debilitated" if sat.dignity == "debilitated" else "combust" if sat.combust else "low Shadbala"
        items.append({"text": SADE_SATI_TEXT["weak_saturn"].format(reason=reason), "why": [f"Saturn: {reason}"]})
    if ss["dhaiya"]:
        items.append({"text": SADE_SATI_TEXT["dhaiya"], "why": [f"{d['name']}: {d['start'][:10]} to {d['end'][:10]}"
                                                                  for d in ss["dhaiya"][:3]]})
    return {"items": items}
