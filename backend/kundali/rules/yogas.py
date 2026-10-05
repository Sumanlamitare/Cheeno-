"""Yoga interpretation: attaches traditional text to each detected yoga and
lists the definitions of all yogas checked (including those not formed)."""

from __future__ import annotations

from ..jyotish.yogas import yoga_definitions
from .data.yogas_doshas import YOGA_TEXT
from .engine import ChartContext

GROUP_LABEL = {
    "raja": "Raja Yogas", "dhana": "Dhana Yogas", "mahapurusha": "Pancha Mahapurusha Yogas",
    "lunar": "Lunar Yogas", "solar": "Solar Yogas", "viparita": "Viparita Raja Yogas",
    "neecha_bhanga": "Neecha Bhanga", "parivartana": "Parivartana (Exchange) Yogas", "other": "Other Yogas",
    "adverse": "Challenging Combinations",
}


def analyze(ctx: ChartContext) -> dict:
    detected = []
    order = {"Strong": 0, "Moderate": 1, "Weak": 2}
    for y in ctx.yogas:
        d = y.to_dict()
        d["text"] = YOGA_TEXT.get(y.id, "")
        d["groupLabel"] = GROUP_LABEL.get(y.group, y.group)
        d["why"] = y.conditions + y.modifiers
        detected.append(d)
    detected.sort(key=lambda d: (d["group"] == "adverse", order.get(d["strength"], 3), d["name"]))
    found_rule_ids = set()
    for y in ctx.yogas:
        found_rule_ids.add(y.id)
    defs = yoga_definitions()
    return {
        "detected": detected,
        "checked": defs,
        "note": "A yoga is listed only when every condition of its stated definition is satisfied in this chart.",
    }
