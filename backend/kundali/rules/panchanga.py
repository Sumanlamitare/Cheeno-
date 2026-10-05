"""Traditional explanation of the birth Panchanga."""

from __future__ import annotations

from .data.panchanga import (KARANA_TEXT, PAKSHA_TEXT, SPECIAL_TITHI_TEXT, TITHI_GROUP_TEXT, VARA_TEXT,
                             YOGA_TEXT)
from .data.nakshatras import NAKSHATRA_DATA
from ..jyotish.constants import INAUSPICIOUS_NITYA_YOGAS


def explain(p: dict) -> dict:
    t = p["tithi"]
    tithi_text = [PAKSHA_TEXT[t["paksha"]], TITHI_GROUP_TEXT[t["group"]]]
    if t["name"] in SPECIAL_TITHI_TEXT:
        tithi_text.append(SPECIAL_TITHI_TEXT[t["name"]])
    y = p["yoga"]["name"]
    return {
        "tithi": " ".join(tithi_text),
        "vara": VARA_TEXT[p["vara"]["lord"]],
        "nakshatra": NAKSHATRA_DATA[p["nakshatra"]["index"]]["characteristics"],
        "yoga": f"{y} yoga is {YOGA_TEXT[y]}" + (" Traditional remedies are customarily suggested only in "
                                                  "consultation with a family priest." if y in INAUSPICIOUS_NITYA_YOGAS else ""),
        "karana": KARANA_TEXT[p["karana"]["name"]],
    }
