"""Deterministic rule engine.

A Rule is pure data: an id, a category, a theme (used to group and
de-duplicate similar statements), a priority tier, a polarity, a list of
declarative conditions and the interpretation text. The engine evaluates the
conditions against a ChartContext, produces "Why?" reasons directly from the
calculated chart, weights each match deterministically and synthesises a
structured reading. No text is generated other than by filling named
placeholders with calculated values.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any, Callable

from ..config import DEFAULT_WEIGHTS, InterpretationWeights
from ..jyotish.chart import NatalChart
from ..jyotish.constants import (
    DUSTHANAS,
    NAKSHATRAS,
    PLANETS,
    RASHI_ELEMENT,
    RASHI_LORDS,
    RASHIS,
    house_from,
    ordinal,
)
from ..jyotish.drishti import aspect_type

POSITIVE, NEGATIVE, MIXED, NEUTRAL = "positive", "negative", "mixed", "neutral"
STRONG_DIGNITIES = ("exalted", "moolatrikona", "own")


@dataclass(frozen=True)
class Rule:
    id: str
    category: str
    theme: str
    tier: str
    polarity: str
    when: tuple
    text: str
    source: str
    subject: str | None = None
    explanation: str = ""

    def derive(self, **changes) -> "Rule":
        return dataclasses.replace(self, **changes)


def rule(id, category, theme, tier, polarity, when, text, source, subject=None, explanation=""):
    return Rule(id, category, theme, tier, polarity, tuple(when), text, source, subject, explanation)


# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------

class _SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


@dataclass
class ChartContext:
    chart: NatalChart
    yogas: list = field(default_factory=list)  # list[YogaMatch]
    doshas: list = field(default_factory=list)  # list[dict]
    shadbala: dict | None = None
    dasha: dict = field(default_factory=dict)  # {"MD": lord, "AD": lord, "PD": lord}
    gochar: dict | None = None

    # ---- planet specification resolution --------------------------------
    def resolve(self, spec: str) -> str | None:
        c = self.chart
        if spec in PLANETS:
            return spec
        if spec.startswith("L") and spec[1:].isdigit():
            return c.house_lord(int(spec[1:]))
        if spec.startswith("D") and "L" in spec:
            div, house = spec[1:].split("L")
            v_lagna = c.ascendant.vargas[div]["sign"]
            return RASHI_LORDS[(v_lagna + int(house) - 1) % 12]
        if spec in self.dasha:
            return self.dasha[spec]
        return None

    def describe(self, spec: str) -> str:
        p = self.resolve(spec)
        if spec in PLANETS:
            return spec
        if spec.startswith("L") and spec[1:].isdigit():
            h = int(spec[1:])
            return f"Lagna lord {p}" if h == 1 else f"{ordinal(h)} lord {p}"
        if spec.startswith("D") and "L" in spec:
            div, house = spec[1:].split("L")
            label = {"9": "Navamsa", "10": "Dashamsha", "7": "Saptamsha", "24": "Chaturvimshamsha"}.get(div, f"D{div}")
            return f"{label} Lagna lord {p}" if house == "1" else f"{label} {ordinal(int(house))} lord {p}"
        if spec in ("MD", "AD", "PD"):
            return {"MD": "Mahadasha lord", "AD": "Antardasha lord", "PD": "Pratyantardasha lord"}[spec] + f" {p}"
        return str(p)

    # ---- strength convention ---------------------------------------------
    def shadbala_ratio(self, planet: str) -> float | None:
        if not self.shadbala or planet not in self.shadbala["planets"]:
            return None
        return self.shadbala["planets"][planet]["ratio"]

    def is_strong(self, planet: str) -> bool:
        """Application convention: strong = own/moolatrikona/exalted sign, or
        Shadbala at least 1.25 x the required minimum while not debilitated,
        combust or in a great enemy's sign."""
        pl = self.chart.planets[planet]
        if pl.dignity in STRONG_DIGNITIES:
            return True
        r = self.shadbala_ratio(planet)
        return (r is not None and r >= 1.25 and pl.dignity not in ("debilitated", "great enemy")
                and not pl.combust)

    def is_weak(self, planet: str) -> bool:
        """Application convention: weak = debilitated, combust, or Shadbala
        clearly below the required minimum (under 0.9x, so planets sitting at
        the threshold are not labelled weak) while not in own/exaltation sign."""
        pl = self.chart.planets[planet]
        if pl.dignity == "debilitated" or pl.combust:
            return True
        r = self.shadbala_ratio(planet)
        return r is not None and r < 0.9 and pl.dignity not in STRONG_DIGNITIES

    def yoga_ids(self) -> set[str]:
        return {y.id for y in self.yogas}

    def dosha(self, did: str) -> dict | None:
        return next((d for d in self.doshas if d["id"] == did), None)

    # ---- placeholders ----------------------------------------------------
    def tokens(self) -> dict:
        c = self.chart
        t = {
            "lagna": RASHIS[c.lagna_sign],
            "moon_sign": RASHIS[c.planets["Moon"].sign],
            "moon_nakshatra": NAKSHATRAS[c.planets["Moon"].nakshatra],
        }
        for h in range(1, 13):
            lord = c.house_lord(h)
            t[f"L{h}"] = lord
            t[f"L{h}_house"] = ordinal(c.house_of(lord))
            t[f"L{h}_sign"] = RASHIS[c.planets[lord].sign]
            t[f"H{h}_sign"] = RASHIS[c.house_sign(h)]
        for p in PLANETS:
            t[f"{p}_house"] = ordinal(c.house_of(p))
            t[f"{p}_sign"] = RASHIS[c.planets[p].sign]
        for k, v in self.dasha.items():
            t[k] = v
        return t

    def fmt(self, text: str) -> str:
        return text.format_map(_SafeDict(self.tokens()))


# ---------------------------------------------------------------------------
# Conditions
# ---------------------------------------------------------------------------

def _as_list(v):
    return v if isinstance(v, (list, tuple, set)) else [v]


def _loc(ctx, p):
    pl = ctx.chart.planets[p]
    return f"the {ordinal(pl.house)} house ({RASHIS[pl.sign]})"


def c_in_house(ctx, p, h):
    planet = ctx.resolve(p)
    pl = ctx.chart.planets[planet]
    if pl.house in _as_list(h):
        return True, [f"{ctx.describe(p)} is placed in {_loc(ctx, planet)}"]
    return False, []


def c_in_sign(ctx, p, s):
    planet = ctx.resolve(p)
    pl = ctx.chart.planets[planet]
    if pl.sign in _as_list(s):
        return True, [f"{ctx.describe(p)} is in {RASHIS[pl.sign]}"]
    return False, []


def c_dignity(ctx, p, values):
    planet = ctx.resolve(p)
    pl = ctx.chart.planets[planet]
    if pl.dignity in _as_list(values):
        d = "its own sign" if pl.dignity == "own" else (
            f"a {pl.dignity}'s sign" if "friend" in pl.dignity or "enemy" in pl.dignity else
            "a neutral sign" if pl.dignity == "neutral" else pl.dignity)
        return True, [f"{ctx.describe(p)} is {('in ' + d) if 'sign' in d else d} ({RASHIS[pl.sign]})"]
    return False, []


def c_strong(ctx, p):
    planet = ctx.resolve(p)
    if ctx.is_strong(planet):
        pl = ctx.chart.planets[planet]
        why = (f"{ctx.describe(p)} is strong ({'own sign' if pl.dignity == 'own' else pl.dignity})"
               if pl.dignity in STRONG_DIGNITIES else
               f"{ctx.describe(p)} is strong (Shadbala {ctx.shadbala_ratio(planet):.2f}× the required minimum)")
        return True, [why]
    return False, []


def c_weak(ctx, p):
    planet = ctx.resolve(p)
    if ctx.is_weak(planet):
        pl = ctx.chart.planets[planet]
        parts = []
        if pl.dignity == "debilitated":
            parts.append("debilitated")
        if pl.combust:
            parts.append("combust")
        if not parts:
            parts.append(f"Shadbala {ctx.shadbala_ratio(planet):.2f}× the required minimum")
        return True, [f"{ctx.describe(p)} is weak ({', '.join(parts)})"]
    return False, []


def c_retro(ctx, p):
    planet = ctx.resolve(p)
    if planet in ("Rahu", "Ketu"):
        return False, []
    if ctx.chart.planets[planet].retrograde:
        return True, [f"{ctx.describe(p)} is retrograde"]
    return False, []


def c_combust(ctx, p):
    planet = ctx.resolve(p)
    pl = ctx.chart.planets[planet]
    if pl.combust:
        return True, [f"{ctx.describe(p)} is combust ({pl.sun_distance:.1f}° from the Sun)"]
    return False, []


def c_occupied(ctx, h, by=None, benefic=None):
    occ = ctx.chart.occupants(h)
    if by:
        occ = [p for p in occ if p in _as_list(by)]
    if benefic is True:
        occ = [p for p in occ if ctx.chart.planets[p].benefic]
    elif benefic is False:
        occ = [p for p in occ if not ctx.chart.planets[p].benefic]
    if occ:
        return True, [f"{', '.join(occ)} {'occupies' if len(occ) == 1 else 'occupy'} the {ordinal(h)} house "
                      f"({RASHIS[ctx.chart.house_sign(h)]})"]
    return False, []


def c_empty(ctx, h):
    if not ctx.chart.occupants(h):
        return True, [f"The {ordinal(h)} house has no occupants"]
    return False, []


def c_aspected(ctx, h, by=None, benefic=None):
    asp = ctx.chart.aspects_on_house(h)
    names = [a["planet"] for a in asp if a["planet"] != "Rahu" and a["planet"] != "Ketu"]
    if by:
        names = [n for n in names if n in _as_list(by)]
    if benefic is True:
        names = [n for n in names if ctx.chart.planets[n].benefic]
    elif benefic is False:
        names = [n for n in names if not ctx.chart.planets[n].benefic]
    if names:
        details = ", ".join(f"{n} ({ordinal(next(a['aspect'] for a in asp if a['planet'] == n))} aspect)" for n in names)
        return True, [f"The {ordinal(h)} house receives drishti from {details}"]
    return False, []


def c_aspects_planet(ctx, p, by):
    planet = ctx.resolve(p)
    hits = []
    for b in _as_list(by):
        b_p = ctx.resolve(b) or b
        if b_p == planet:
            continue
        a = aspect_type(b_p, ctx.chart.planets[b_p].sign, ctx.chart.planets[planet].sign)
        if a and b_p not in ("Rahu", "Ketu"):
            hits.append(f"{b_p} aspects {ctx.describe(p)} ({ordinal(a)} aspect)")
    return (True, hits) if hits else (False, [])


def c_conj(ctx, a, b):
    pa, pb = ctx.resolve(a), ctx.resolve(b)
    if pa != pb and ctx.chart.planets[pa].sign == ctx.chart.planets[pb].sign:
        return True, [f"{ctx.describe(a)} is conjunct {ctx.describe(b)} in {RASHIS[ctx.chart.planets[pa].sign]}"]
    return False, []


def c_with(ctx, p, any_of):
    planet = ctx.resolve(p)
    s = ctx.chart.planets[planet].sign
    hits = [q for q in _as_list(any_of) if q != planet and ctx.chart.planets[q].sign == s]
    if hits:
        return True, [f"{ctx.describe(p)} is conjunct {', '.join(hits)}"]
    return False, []


def c_yoga(ctx, id):
    ids = _as_list(id)
    hits = [y for y in ctx.yogas if y.id in ids]
    if hits:
        return True, [f"{y.name} is present ({y.strength.lower()})" for y in hits[:3]]
    return False, []


def c_dosha(ctx, id):
    d = ctx.dosha(id)
    if d and d["detected"]:
        return True, [f"{d['name']}: {d['status'].lower()}"]
    return False, []


def c_lagna(ctx, s):
    if ctx.chart.lagna_sign in _as_list(s):
        return True, [f"The Lagna is {RASHIS[ctx.chart.lagna_sign]}"]
    return False, []


def c_moon_sign(ctx, s):
    ms = ctx.chart.planets["Moon"].sign
    if ms in _as_list(s):
        return True, [f"The Moon is in {RASHIS[ms]}"]
    return False, []


def c_from_moon(ctx, p, h):
    planet = ctx.resolve(p)
    hh = ctx.chart.house_from_moon(planet)
    if hh in _as_list(h):
        return True, [f"{ctx.describe(p)} is in the {ordinal(hh)} house from the Moon"]
    return False, []


def c_from_planet(ctx, p, ref, h):
    planet, rp = ctx.resolve(p), ctx.resolve(ref)
    hh = house_from(ctx.chart.planets[rp].sign, ctx.chart.planets[planet].sign)
    if hh in _as_list(h):
        return True, [f"{ctx.describe(p)} is in the {ordinal(hh)} house from {ctx.describe(ref)}"]
    return False, []


_VARGA_LABEL = {"9": "Navamsa (D9)", "10": "Dashamsha (D10)", "7": "Saptamsha (D7)", "24": "Chaturvimshamsha (D24)",
                "4": "Chaturthamsha (D4)", "2": "Hora (D2)"}


def c_varga_house(ctx, d, p, h):
    planet = ctx.resolve(p)
    info = ctx.chart.planets[planet].vargas[str(d)]
    if info["house"] in _as_list(h):
        return True, [f"In the {_VARGA_LABEL.get(str(d), f'D{d}')}, {ctx.describe(p)} is in the "
                      f"{ordinal(info['house'])} house ({info['signName']})"]
    return False, []


def c_varga_dignity(ctx, d, p, values):
    planet = ctx.resolve(p)
    info = ctx.chart.planets[planet].vargas[str(d)]
    if info["dignity"] in _as_list(values):
        dig = info["dignity"]
        phrase = ("in its own sign" if dig == "own" else dig if dig in ("exalted", "debilitated") else
                  f"in a {dig}'s sign" if ("friend" in dig or "enemy" in dig) else "in a neutral sign")
        return True, [f"In the {_VARGA_LABEL.get(str(d), f'D{d}')}, {ctx.describe(p)} is {phrase} ({info['signName']})"]
    return False, []


def c_varga_lagna(ctx, d, s):
    vs = ctx.chart.ascendant.vargas[str(d)]["sign"]
    if vs in _as_list(s):
        return True, [f"The {_VARGA_LABEL.get(str(d), f'D{d}')} Lagna is {RASHIS[vs]}"]
    return False, []


def c_varga_occupied(ctx, d, h, by=None):
    occ = [p for p in PLANETS if ctx.chart.planets[p].vargas[str(d)]["house"] == h]
    if by:
        occ = [p for p in occ if p in _as_list(by)]
    if occ:
        return True, [f"In the {_VARGA_LABEL.get(str(d), f'D{d}')}, {', '.join(occ)} "
                      f"{'occupies' if len(occ) == 1 else 'occupy'} the {ordinal(h)} house"]
    return False, []


def c_vargottama(ctx, p):
    planet = ctx.resolve(p)
    pl = ctx.chart.planets[planet]
    if pl.vargas["9"]["sign"] == pl.sign:
        return True, [f"{ctx.describe(p)} is Vargottama (same sign, {RASHIS[pl.sign]}, in D1 and D9)"]
    return False, []


def c_house_element(ctx, h, e):
    sign = ctx.chart.house_sign(h)
    if RASHI_ELEMENT[sign] in _as_list(e):
        return True, [f"The {ordinal(h)} house falls in {RASHIS[sign]}, a {RASHI_ELEMENT[sign]} sign"]
    return False, []


def c_house_modality(ctx, h, m):
    from ..jyotish.constants import RASHI_MODALITY
    sign = ctx.chart.house_sign(h)
    if RASHI_MODALITY[sign] in _as_list(m):
        return True, [f"The {ordinal(h)} house falls in {RASHIS[sign]}, a {RASHI_MODALITY[sign]} sign"]
    return False, []


def c_lord_is(ctx, h, p):
    lord = ctx.chart.house_lord(h)
    if lord in _as_list(p):
        return True, [f"The {ordinal(h)} house is ruled by {lord}"]
    return False, []


def c_same(ctx, a, b):
    pa, pb = ctx.resolve(a), ctx.resolve(b)
    if pa == pb:
        return True, [f"{ctx.describe(a)} is also the {ctx.describe(b).rsplit(' ', 1)[0]}"]
    return False, []


def c_nakshatra(ctx, p, n):
    planet = ctx.resolve(p)
    nk = ctx.chart.planets[planet].nakshatra
    if nk in _as_list(n):
        return True, [f"{ctx.describe(p)} is in {NAKSHATRAS[nk]} nakshatra"]
    return False, []


def c_dasha_lord_owns(ctx, level, h):
    planet = ctx.dasha.get(level)
    if not planet:
        return False, []
    owned = [x for x in ctx.chart.houses_ruled_by(planet) if x in _as_list(h)]
    if owned:
        return True, [f"{ctx.describe(level)} rules the {', '.join(ordinal(x) for x in owned)} house"]
    return False, []


def c_dusthana_lord(ctx, p):
    planet = ctx.resolve(p)
    owned = [x for x in ctx.chart.houses_ruled_by(planet) if x in DUSTHANAS]
    if owned:
        return True, [f"{ctx.describe(p)} rules the {', '.join(ordinal(x) for x in owned)} house"]
    return False, []


def c_in_yoga(ctx, p, exclude_groups=("adverse",)):
    planet = ctx.resolve(p)
    hits = [y for y in ctx.yogas if planet in y.planets and y.group not in exclude_groups]
    if hits:
        names = list(dict.fromkeys(y.name for y in hits))
        return True, [f"{ctx.describe(p)} participates in {', '.join(names[:3])}"]
    return False, []


def c_not(ctx, c):
    ok, _ = evaluate(ctx, c)
    return (not ok), []


def c_any(ctx, c):
    reasons = []
    hit = False
    for sub in c:
        ok, r = evaluate(ctx, sub)
        if ok:
            hit = True
            reasons += r
    return hit, reasons


def c_all(ctx, c):
    reasons = []
    for sub in c:
        ok, r = evaluate(ctx, sub)
        if not ok:
            return False, []
        reasons += r
    return True, reasons


CONDITIONS: dict[str, Callable[..., tuple[bool, list[str]]]] = {
    "in_house": c_in_house, "in_sign": c_in_sign, "dignity": c_dignity, "strong": c_strong, "weak": c_weak,
    "retro": c_retro, "combust": c_combust, "occupied": c_occupied, "empty": c_empty, "aspected": c_aspected,
    "aspects_planet": c_aspects_planet, "conj": c_conj, "with": c_with, "yoga": c_yoga, "dosha": c_dosha,
    "lagna": c_lagna, "moon_sign": c_moon_sign, "from_moon": c_from_moon, "from_planet": c_from_planet,
    "varga_house": c_varga_house, "varga_dignity": c_varga_dignity, "varga_lagna": c_varga_lagna,
    "varga_occupied": c_varga_occupied, "vargottama": c_vargottama, "house_element": c_house_element,
    "house_modality": c_house_modality, "lord_is": c_lord_is, "same": c_same, "nakshatra": c_nakshatra,
    "dasha_lord_owns": c_dasha_lord_owns, "in_yoga": c_in_yoga, "dusthana_lord": c_dusthana_lord,
    "not": c_not, "any": c_any, "all": c_all,
}


def evaluate(ctx: ChartContext, cond: dict) -> tuple[bool, list[str]]:
    params = {k: v for k, v in cond.items() if k != "t"}
    fn = CONDITIONS[cond["t"]]
    return fn(ctx, **params)


# ---------------------------------------------------------------------------
# Matching and synthesis
# ---------------------------------------------------------------------------

@dataclass
class Match:
    rule: Rule
    weight: float
    strength: str
    text: str
    reasons: list[str]
    modifiers: list[str]

    def to_dict(self) -> dict:
        return {
            "ruleId": self.rule.id,
            "category": self.rule.category,
            "theme": self.rule.theme,
            "polarity": self.rule.polarity,
            "tier": self.rule.tier,
            "matched": True,
            "strength": self.strength,
            "weight": round(self.weight, 1),
            "text": self.text,
            "reason": "; ".join(self.reasons),
            "reasons": self.reasons,
            "modifiers": self.modifiers,
            "sourceConcept": self.rule.source,
            "explanation": self.rule.explanation,
        }


def _strength_label(weight: float) -> str:
    if weight >= 90:
        return "strong"
    if weight >= 45:
        return "moderate"
    return "mild"


def match_rule(ctx: ChartContext, r: Rule, weights: InterpretationWeights = DEFAULT_WEIGHTS) -> Match | None:
    reasons: list[str] = []
    for cond in r.when:
        ok, why = evaluate(ctx, cond)
        if not ok:
            return None
        reasons += why
    weight = float(weights.tiers[r.tier])
    modifiers = []
    if r.subject:
        planet = ctx.resolve(r.subject)
        if planet and planet not in ("Rahu", "Ketu"):
            strong, weak = ctx.is_strong(planet), ctx.is_weak(planet)
            if r.polarity == POSITIVE:
                if strong:
                    weight *= 1.25
                    modifiers.append(f"Strengthened: {planet} is strong")
                elif weak:
                    weight *= 0.6
                    modifiers.append(f"Reduced: {planet} is weak")
            elif r.polarity == NEGATIVE:
                if strong:
                    weight *= 0.75
                    modifiers.append(f"Mitigated: {planet} is strong")
                elif weak:
                    weight *= 1.2
                    modifiers.append(f"Intensified: {planet} is weak")
    # Unique, ordered reasons.
    reasons = list(dict.fromkeys(reasons))
    return Match(r, weight, _strength_label(weight), ctx.fmt(r.text), reasons, modifiers)


def run_rules(ctx: ChartContext, rules: list[Rule], weights=DEFAULT_WEIGHTS) -> list[Match]:
    seen = set()
    out = []
    for r in rules:
        if r.id in seen:
            continue
        m = match_rule(ctx, r, weights)
        if m:
            seen.add(r.id)
            out.append(m)
    return out


def _group(matches: list[Match]) -> list[dict]:
    """Group matches by (theme, polarity); the highest-weight match supplies the
    primary statement and the others become supporting statements."""
    groups: dict[tuple, list[Match]] = {}
    for m in matches:
        groups.setdefault((m.rule.theme, m.rule.polarity), []).append(m)
    out = []
    for (theme, polarity), ms in groups.items():
        ms.sort(key=lambda m: (-m.weight, m.rule.id))
        primary = ms[0]
        # Diminishing returns for repeated, similar indications.
        weight = primary.weight + 0.5 * sum(m.weight for m in ms[1:])
        why = []
        for m in ms:
            why.extend(m.reasons)
        out.append({
            "theme": theme,
            "polarity": polarity,
            "weight": round(weight, 1),
            "strength": _strength_label(weight),
            "text": primary.text,
            "supporting": [m.text for m in ms[1:] if m.text != primary.text],
            "why": list(dict.fromkeys(why)),
            "modifiers": list(dict.fromkeys(x for m in ms for x in m.modifiers)),
            "ruleIds": [m.rule.id for m in ms],
            "sources": list(dict.fromkeys(m.rule.source for m in ms)),
        })
    out.sort(key=lambda g: (-g["weight"], g["theme"]))
    return out


BALANCE_TEXT = [
    (0.75, "Traditional indicators for {topic} in this chart are predominantly supportive."),
    (0.55, "Supportive indicators for {topic} outweigh the challenging ones, although the challenges noted are "
           "real and deserve attention."),
    (0.45, "Supportive and challenging indicators for {topic} are closely balanced; traditionally, results then "
           "depend on effort and on the timing of planetary periods."),
    (0.25, "Challenging indicators for {topic} are more prominent than supportive ones; traditional texts advise "
           "patience, steady effort and attention to the favourable periods."),
    (0.0, "Several challenging indicators for {topic} appear in this chart; tradition treats these as areas that "
          "call for conscious effort rather than as fixed outcomes."),
]


def synthesize(topic: str, matches: list[Match], theme_labels: dict[str, str],
               weights: InterpretationWeights = DEFAULT_WEIGHTS) -> dict:
    groups = _group(matches)
    for g in groups:
        g["label"] = theme_labels.get(g["theme"], g["theme"].split(".")[-1].replace("_", " ").capitalize())
    strengths = [g for g in groups if g["polarity"] == POSITIVE]
    challenges = [g for g in groups if g["polarity"] == NEGATIVE]
    mixed = [g for g in groups if g["polarity"] in (MIXED, NEUTRAL)]
    pos = sum(g["weight"] for g in strengths) + 0.5 * sum(g["weight"] for g in mixed if g["polarity"] == MIXED)
    neg = sum(g["weight"] for g in challenges) + 0.5 * sum(g["weight"] for g in mixed if g["polarity"] == MIXED)
    total = pos + neg
    if total == 0:
        overall = f"No specific classical indicators for {topic} were triggered beyond the general house analysis."
        balance = None
    else:
        balance = pos / total
        overall = next(t for thr, t in BALANCE_TEXT if balance >= thr).format(topic=topic)
    top = list(dict.fromkeys(g["label"] for g in groups))[:3]
    if top:
        overall += " The most emphasised themes are: " + ", ".join(top) + "."
    emphasis = ("strongly emphasised" if total >= weights.emphasis_threshold * 2.5 else
                "clearly emphasised" if total >= weights.emphasis_threshold * 1.25 else
                "moderately emphasised" if total >= weights.emphasis_threshold * 0.5 else "lightly emphasised")
    overall_why = []
    for g in (strengths[:2] + challenges[:2]):
        overall_why.extend(g["why"][:2])
    return {
        "topic": topic,
        "emphasis": emphasis,
        "balance": None if balance is None else round(balance, 3),
        "positiveWeight": round(pos, 1),
        "negativeWeight": round(neg, 1),
        "overall": overall,
        "overallWhy": list(dict.fromkeys(overall_why)),
        "strengths": strengths,
        "challenges": challenges,
        "notes": mixed,
        "matches": [m.to_dict() for m in matches],
    }


def chart_tokens(chart: NatalChart) -> dict[str, Any]:
    return ChartContext(chart).tokens()
