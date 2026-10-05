"""Calculation and interpretation settings.

Defaults follow the conventions most commonly used for Nepali Janma Kundali:
sidereal zodiac, Lahiri (Chitrapaksha) ayanamsha and whole-sign houses.
The settings object is passed explicitly through the engine so alternate
methods can be added later without touching the calculation code.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CalculationSettings:
    ayanamsha: str = "lahiri"
    house_system: str = "whole_sign"
    node_type: str = "mean"  # "mean" or "true" lunar node for Rahu/Ketu
    dasha_year_days: float = 365.25  # length of a Vimshottari year in days

    def describe(self) -> dict:
        return {
            "zodiac": "Sidereal / Nirayana",
            "ayanamsha": {"lahiri": "Lahiri / Chitrapaksha"}.get(self.ayanamsha, self.ayanamsha),
            "houseSystem": {"whole_sign": "Whole Sign"}.get(self.house_system, self.house_system),
            "nodes": "Mean lunar node" if self.node_type == "mean" else "True lunar node",
            "dashaYear": f"{self.dasha_year_days} days",
            "ephemeris": "Swiss Ephemeris",
        }


@dataclass(frozen=True)
class InterpretationWeights:
    """Deterministic weights for rule priority tiers.

    These are implementation constants used to rank and synthesise rules,
    not astrological truths. Adjust them here to tune the synthesis.
    """

    # A theme is reported as "emphasised" when its net weight reaches this.
    emphasis_threshold: int = 120
    tiers: dict = field(default_factory=lambda: {"major": 100, "strong": 70, "moderate": 40, "minor": 20})


DEFAULT_SETTINGS = CalculationSettings()
DEFAULT_WEIGHTS = InterpretationWeights()
