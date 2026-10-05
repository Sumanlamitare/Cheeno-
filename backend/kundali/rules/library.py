"""Shared rule families built from the classical data tables, plus helpers
for timing windows used by the domain modules."""

from __future__ import annotations

import datetime as dt

from ..jyotish.constants import DUSTHANAS, KENDRAS, PLANETS, ordinal
from .data.houses import BHAVESHA
from .data.planets import PLANET_IN_HOUSE
from .engine import ChartContext, Rule, rule

DEFAULT_PLACEMENT_THEME = {1: "status", 4: "status", 7: "status", 10: "status", 5: "fortune", 9: "fortune",
                           2: "gains", 11: "gains", 3: "effort", 6: "effort", 8: "change", 12: "change"}


def bhavesha_rules(house: int, category: str, theme_for, tier: str = "major", prefix: str | None = None) -> list[Rule]:
    """Rules for the lord of `house` placed in each of the 12 houses."""
    out = []
    for y in range(1, 13):
        pol, text = BHAVESHA[house][y]
        out.append(rule(
            f"{prefix or category}_L{house}_in_{y}", category, theme_for(y, pol), tier, pol,
            [{"t": "in_house", "p": f"L{house}", "h": y}], text,
            f"{ordinal(house)} lord in {ordinal(y)} house", subject=f"L{house}",
            explanation="Bhavesha Phala (BPHS ch. 24)",
        ))
    return out


def planet_house_rules(house: int, category: str, theme_for, tier: str = "strong",
                       planets=PLANETS, prefix: str | None = None) -> list[Rule]:
    out = []
    for p in planets:
        pol, text = PLANET_IN_HOUSE[p][house]
        out.append(rule(
            f"{prefix or category}_{p}_in_{house}", category, theme_for(p, pol), tier, pol,
            [{"t": "in_house", "p": p, "h": house}], text,
            f"{p} in {ordinal(house)} house", subject=p, explanation="Graha-Bhava Phala",
        ))
    return out


def yoga_rule(category: str, yoga_ids, theme: str, text: str, tier: str = "strong", rid: str | None = None) -> Rule:
    ids = list(yoga_ids) if isinstance(yoga_ids, (list, tuple)) else [yoga_ids]
    return rule(rid or f"{category}_yoga_{'_'.join(ids)}", category, theme, tier, "positive",
                [{"t": "yoga", "id": ids}], text, "Yoga: " + ", ".join(ids))


def significator_set(ctx: ChartContext, specs: list[str], occupied_houses: list[int] = ()) -> dict[str, list[str]]:
    """Map planet -> reasons why it signifies the domain."""
    out: dict[str, list[str]] = {}
    for s in specs:
        p = ctx.resolve(s)
        if p:
            out.setdefault(p, []).append(ctx.describe(s))
    for h in occupied_houses:
        for p in ctx.chart.occupants(h):
            out.setdefault(p, []).append(f"occupant of the {ordinal(h)} house")
    return out


def timing_windows(dasha_tree: list[dict], significators: dict[str, list[str]], start: dt.datetime,
                   end: dt.datetime, limit: int = 8) -> list[dict]:
    """Antardasha periods in [start, end] whose Mahadasha and/or Antardasha
    lord is a significator. Primary = both lords are significators."""
    out = []
    for md in dasha_tree:
        if md["end"] <= start or md["start"] >= end:
            continue
        for ad in md["children"]:
            if ad["end"] <= start or ad["start"] >= end:
                continue
            md_sig = md["lord"] in significators
            ad_sig = ad["lord"] in significators
            if not (md_sig or ad_sig):
                continue
            if not ad_sig:
                continue  # require the sub-period lord to be involved
            why = []
            if md_sig:
                why.append(f"Mahadasha lord {md['lord']}: {', '.join(significators[md['lord']])}")
            why.append(f"Antardasha lord {ad['lord']}: {', '.join(significators[ad['lord']])}")
            out.append({
                "mahadasha": md["lord"],
                "antardasha": ad["lord"],
                "start": max(ad["start"], start).isoformat(),
                "end": ad["end"].isoformat(),
                "level": "primary" if md_sig and ad_sig else "secondary",
                "why": why,
            })
    out.sort(key=lambda w: (0 if w["level"] == "primary" else 1, w["start"]))
    selected = out[:limit]
    selected.sort(key=lambda w: w["start"])
    return selected


def placement_quality(ctx: ChartContext, planet: str) -> str:
    pl = ctx.chart.planets[planet]
    if pl.house in KENDRAS or pl.house in (5, 9):
        return "well placed"
    if pl.house in DUSTHANAS:
        return "in a dusthana"
    return "neutrally placed"
