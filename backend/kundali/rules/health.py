"""Health tendencies (traditional only). Never diagnoses, never predicts
death or illness with certainty, never advises on treatment."""

from __future__ import annotations

from ..jyotish.constants import RASHIS, ordinal
from .engine import ChartContext, rule, run_rules, synthesize

C = "health"
THEMES = {
    "health.vitality": "Vitality and constitution",
    "health.attention": "Areas for attention (traditional)",
    "health.resilience": "Resilience and recovery",
}

# Kalapurusha: body regions traditionally associated with each sign.
SIGN_BODY = ["head", "face and throat", "shoulders, arms and lungs", "chest", "heart and upper abdomen",
             "digestive system", "lower abdomen and kidneys", "reproductive and excretory organs",
             "hips and thighs", "knees and joints", "calves and circulation", "feet"]


def build_rules():
    return [
        rule("health_L1_strong", C, "health.vitality", "major", "positive", [{"t": "strong", "p": "L1"}],
             "Traditional Jyotish associates a strong Lagna lord ({L1}) with good vitality and recuperative capacity.",
             "Strength of the Lagna lord", subject="L1"),
        rule("health_L1_weak", C, "health.attention", "strong", "negative", [{"t": "weak", "p": "L1"}],
             "Traditional Jyotish associates a weak Lagna lord with the need for regular care of health and energy.",
             "Weakness of the Lagna lord", subject="L1"),
        rule("health_L1_dusthana", C, "health.attention", "moderate", "negative", [{"t": "in_house", "p": "L1", "h": [6, 8, 12]}],
             "The Lagna lord in the {L1_house} house is traditionally associated with the need for attention to "
             "health and rest.", "Lagna lord in a dusthana"),
        rule("health_sun_strong", C, "health.vitality", "moderate", "positive", [{"t": "strong", "p": "Sun"}],
             "A strong Sun is traditionally associated with vitality and a robust constitution.", "Strength of the Sun"),
        rule("health_moon_strong", C, "health.vitality", "moderate", "positive", [{"t": "strong", "p": "Moon"}],
             "A strong Moon is traditionally associated with emotional and physical balance.", "Strength of the Moon"),
        rule("health_moon_weak", C, "health.attention", "minor", "negative", [{"t": "weak", "p": "Moon"}],
             "A weak Moon is traditionally associated with sensitivity to stress; rest and routine are advised.",
             "Weakness of the Moon"),
        rule("health_jup_aspect_lagna", C, "health.resilience", "strong", "positive",
             [{"t": "any", "c": [{"t": "aspected", "h": 1, "by": "Jupiter"}, {"t": "in_house", "p": "Jupiter", "h": 1}]}],
             "Jupiter's influence on the Lagna is traditionally considered protective of health.", "Jupiter on the Lagna"),
        rule("health_malefic_lagna", C, "health.attention", "moderate", "negative",
             [{"t": "occupied", "h": 1, "by": ["Saturn", "Mars", "Rahu", "Ketu"]}],
             "A malefic in the Lagna is traditionally associated with the need for care of the body, especially of the "
             "{H1_sign}-ruled regions in Kalapurusha symbolism.", "Malefic in Lagna"),
        rule("health_6_8_malefics", C, "health.attention", "minor", "negative",
             [{"t": "occupied", "h": 8, "by": ["Saturn", "Mars", "Rahu", "Sun"]}],
             "A malefic in the 8th house is traditionally associated with the need for caution against accidents and "
             "chronic strain.", "Malefic in 8th"),
        rule("health_harsha", C, "health.resilience", "moderate", "positive", [{"t": "yoga", "id": "harsha"}],
             "Harsha Yoga is traditionally associated with good resistance and recovery.", "Harsha Yoga"),
        rule("health_malefic_6_upachaya", C, "health.resilience", "minor", "positive",
             [{"t": "occupied", "h": 6, "by": ["Saturn", "Mars", "Rahu", "Ketu", "Sun"]}],
             "A malefic in the 6th house (an upachaya) is traditionally associated with strong resistance to illness and "
             "opponents.", "Malefic in 6th"),
        rule("health_L6_L8_in_1", C, "health.attention", "minor", "negative", [{"t": "in_house", "p": "L6", "h": 1}],
             "The 6th lord in the Lagna is traditionally associated with periodic health concerns that respond to care.",
             "6th lord in Lagna"),
    ]


RULES = build_rules()


def analyze(ctx: ChartContext) -> dict:
    out = synthesize("health", run_rules(ctx, RULES), THEMES)
    c = ctx.chart
    attention = []
    for h in (1, 6, 8):
        sign = c.house_sign(h)
        afflicted = [p for p in c.occupants(h) if p in ("Saturn", "Mars", "Rahu", "Ketu")]
        if afflicted:
            attention.append({"house": h, "sign": RASHIS[sign], "region": SIGN_BODY[sign],
                              "why": f"{', '.join(afflicted)} in the {ordinal(h)} house ({RASHIS[sign]})"})
    out["bodyAreas"] = attention
    out["disclaimer"] = ("Traditional astrological tendencies only. This is not medical advice and does not diagnose "
                         "or predict illness. Please consult qualified medical professionals for any health concern.")
    return out
