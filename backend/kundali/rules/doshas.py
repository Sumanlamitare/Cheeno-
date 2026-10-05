"""Dosha interpretation."""

from __future__ import annotations

from .data.yogas_doshas import DOSHA_TEXT
from .engine import ChartContext


def analyze(ctx: ChartContext) -> list[dict]:
    out = []
    for d in ctx.doshas:
        t = DOSHA_TEXT.get(d["id"], {})
        item = dict(d)
        item["text"] = t.get("detected" if d["detected"] else "not", "")
        if d["id"] == "kemadruma" and not d["detected"] and d["status"].startswith("Formed"):
            item["text"] = ("Kemadruma Yoga is formed but cancelled by the factors listed, so tradition does not apply "
                            "its results.")
        item["why"] = d.get("placements", []) + d.get("mitigations", [])
        out.append(item)
    return out
