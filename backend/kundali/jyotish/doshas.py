"""Dosha engine. Each dosha states the exact rule applied, because
traditions differ; disputed doshas are labelled as such."""

from __future__ import annotations

from .chart import NatalChart
from .constants import GANDAMULA_NAKSHATRAS, NAKSHATRAS, PADA_SPAN, RASHIS, house_from, ordinal

MANGAL_HOUSES = {1, 2, 4, 7, 8, 12}

# Commonly cited house-sign exceptions for Mangal Dosha.
MANGAL_HOUSE_SIGN_EXCEPTIONS = {
    1: {0},          # Aries
    2: {2, 5},       # Gemini, Virgo
    4: {0, 7},       # Aries, Scorpio
    7: {3, 9},       # Cancer, Capricorn
    8: {8, 11},      # Sagittarius, Pisces
    12: {1, 6},      # Taurus, Libra
}

KAAL_SARP_NAMES = {
    1: "Anant", 2: "Kulik", 3: "Vasuki", 4: "Shankhapal", 5: "Padma", 6: "Mahapadma",
    7: "Takshak", 8: "Karkotak", 9: "Shankhachud", 10: "Ghatak", 11: "Vishdhar", 12: "Sheshnag",
}


def mangal_dosha(chart: NatalChart) -> dict:
    mars = chart.planets["Mars"]
    refs = {
        "Lagna": chart.lagna_sign,
        "Moon": chart.planets["Moon"].sign,
        "Venus": chart.planets["Venus"].sign,
    }
    from_refs = {name: house_from(sign, mars.sign) for name, sign in refs.items()}
    hits = [name for name, h in from_refs.items() if h in MANGAL_HOUSES]

    mitigations = []
    if mars.sign in (0, 7):
        mitigations.append(f"Mars is in its own sign {RASHIS[mars.sign]}")
    if mars.sign == 9:
        mitigations.append("Mars is exalted in Capricorn")
    if chart.planets["Jupiter"].sign == mars.sign:
        mitigations.append("Jupiter is conjunct Mars")
    elif chart.is_aspected_by("Mars", "Jupiter"):
        mitigations.append("Jupiter aspects Mars")
    h_lagna = from_refs["Lagna"]
    if h_lagna in MANGAL_HOUSE_SIGN_EXCEPTIONS and mars.sign in MANGAL_HOUSE_SIGN_EXCEPTIONS[h_lagna]:
        mitigations.append(f"Mars in the {ordinal(h_lagna)} house in {RASHIS[mars.sign]} is a commonly cited exception")
    mitigations = list(dict.fromkeys(mitigations))

    detected = bool(hits)
    if not detected:
        severity = "Not detected"
    elif "Lagna" in hits and len(hits) >= 2:
        severity = "Pronounced"
    elif "Lagna" in hits:
        severity = "Present"
    else:
        severity = "Mild (only from Moon/Venus)"
    if detected and mitigations:
        status = "Detected, with mitigating factors"
    elif detected:
        status = "Detected"
    else:
        status = "Not detected"
    return {
        "id": "mangal",
        "name": "Mangal (Manglik / Kuja) Dosha",
        "detected": detected,
        "status": status,
        "severity": severity,
        "placements": [f"Mars is in the {ordinal(h)} house from the {name}" for name, h in from_refs.items()],
        "triggeredFrom": hits,
        "mitigations": mitigations if detected else [],
        "rule": ("Mars in the 1st, 2nd, 4th, 7th, 8th or 12th house counted from the Lagna, and separately from the "
                 "Moon and Venus. Severity: pronounced when it occurs from the Lagna and at least one other "
                 "reference; mitigation by own/exaltation sign, Jupiter's conjunction or aspect, and commonly cited "
                 "house-sign exceptions."),
        "disputed": False,
        "note": ("Traditionally Mangal Dosha is assessed together with the partner's chart during Kundali matching; "
                 "a single chart cannot settle the matter."),
    }


def kaal_sarp(chart: NatalChart) -> dict:
    rahu = chart.planets["Rahu"].longitude
    seven = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    offsets = [(chart.planets[p].longitude - rahu) % 360.0 for p in seven]
    rahu_to_ketu = all(0 < o < 180 for o in offsets)
    ketu_to_rahu = all(180 < o < 360 for o in offsets)
    detected = rahu_to_ketu or ketu_to_rahu
    rahu_house = chart.planets["Rahu"].house
    variant = None
    if rahu_to_ketu:
        variant = "Rahu-to-Ketu hemisphere"
    elif ketu_to_rahu:
        variant = "Ketu-to-Rahu hemisphere (some authors call this Kaal Amrita)"
    in_first_half = sum(1 for o in offsets if 0 < o < 180)
    near_miss = (not detected) and in_first_half in (1, 6)
    return {
        "id": "kaal_sarp",
        "name": "Kaal Sarp Yoga / Dosha",
        "detected": detected,
        "status": "Detected" if detected else ("Not detected (partial: one planet outside the axis)" if near_miss
                                               else "Not detected"),
        "type": f"{KAAL_SARP_NAMES[rahu_house]} Kaal Sarp" if detected else None,
        "variant": variant,
        "placements": [f"Rahu in the {ordinal(rahu_house)} house, Ketu in the {ordinal(chart.planets['Ketu'].house)} house"],
        "rule": ("Calculated according to the application's defined traditional rule: all seven grahas (Sun to "
                 "Saturn) lie strictly within one half of the zodiac bounded by Rahu and Ketu, by longitude. The "
                 "type is named from Rahu's house."),
        "disputed": True,
        "note": ("Kaal Sarp is not described in the classical texts such as Brihat Parashara Hora Shastra and its "
                 "importance is disputed among practitioners."),
        "mitigations": [],
    }


def kemadruma(chart: NatalChart) -> dict:
    moon = chart.planets["Moon"].sign
    cands = ("Mars", "Mercury", "Jupiter", "Venus", "Saturn")
    neighbours = [p for p in cands if chart.planets[p].sign in ((moon + 1) % 12, (moon - 1) % 12)]
    conj = [p for p in cands if chart.planets[p].sign == moon]
    raw = not neighbours
    cancellations = []
    if raw:
        if conj:
            cancellations.append(f"{', '.join(conj)} conjunct the Moon")
        kendra_lagna = [p for p in cands if chart.house_of(p) in (1, 4, 7, 10)]
        if kendra_lagna:
            cancellations.append(f"{', '.join(kendra_lagna)} in a kendra from the Lagna")
        kendra_moon = [p for p in cands if house_from(moon, chart.planets[p].sign) in (4, 7, 10)]
        if kendra_moon:
            cancellations.append(f"{', '.join(kendra_moon)} in a kendra from the Moon")
        if chart.house_of("Moon") in (1, 4, 7, 10):
            cancellations.append("The Moon itself occupies a kendra from the Lagna")
    detected = raw and not cancellations
    return {
        "id": "kemadruma",
        "name": "Kemadruma Yoga",
        "detected": detected,
        "status": ("Detected" if detected else
                   "Formed but cancelled" if raw else "Not formed"),
        "placements": ([f"No planet (other than Sun, Rahu, Ketu) in the 2nd or 12th from the Moon"] if raw else
                       [f"{', '.join(neighbours)} adjacent to the Moon"]),
        "mitigations": cancellations,
        "rule": ("No planet other than the Sun, Rahu and Ketu in the 2nd or 12th from the Moon. Cancelled when a "
                 "planet joins the Moon, any planet occupies a kendra from the Lagna or the Moon, or the Moon is in "
                 "a kendra from the Lagna."),
        "disputed": False,
        "note": None,
    }


def gandamula(chart: NatalChart) -> dict:
    moon = chart.planets["Moon"]
    nak = moon.nakshatra
    detected = nak in GANDAMULA_NAKSHATRAS
    # Gandanta: last pada of a water sign or first pada of the following fire sign.
    deg = moon.longitude % 120.0
    gandanta = deg < PADA_SPAN or deg >= 120.0 - PADA_SPAN
    return {
        "id": "gandamula",
        "name": "Gandamula Nakshatra",
        "detected": detected,
        "status": ("Detected (Gandanta pada)" if detected and gandanta else "Detected" if detected else "Not detected"),
        "placements": [f"Moon in {NAKSHATRAS[nak]} pada {moon.pada}"],
        "gandanta": gandanta,
        "rule": ("The Moon at birth in Ashwini, Ashlesha, Magha, Jyeshtha, Mula or Revati (the nakshatras at the "
                 "junctions of water and fire signs). The junction padas themselves are called Gandanta."),
        "disputed": False,
        "mitigations": [],
        "note": ("In Nepali tradition a Mula Shanti / Gandamula Shanti puja is customarily performed; this is a "
                 "ritual observance, not a prediction of harm."),
    }


def grahana(chart: NatalChart) -> dict:
    hits = []
    for lum in ("Sun", "Moon"):
        for node in ("Rahu", "Ketu"):
            if chart.planets[lum].sign == chart.planets[node].sign:
                hits.append(f"{lum} with {node} in {RASHIS[chart.planets[lum].sign]}")
    return {
        "id": "grahana",
        "name": "Grahana Yoga",
        "detected": bool(hits),
        "status": "Detected" if hits else "Not detected",
        "placements": hits,
        "rule": "The Sun or the Moon occupies the same sign as Rahu or Ketu.",
        "disputed": True,
        "mitigations": [],
        "note": "Grahana Yoga is a later, non-Parashari combination; its weight differs between traditions.",
    }


def detect_doshas(chart: NatalChart) -> list[dict]:
    return [mangal_dosha(chart), kaal_sarp(chart), kemadruma(chart), gandamula(chart), grahana(chart)]
