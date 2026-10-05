"""Yoga detection engine.

Each yoga is a structured rule: an identifier, a precise definition of the
conditions used by this application, and an evaluator that checks those
conditions against the calculated chart. A yoga is reported only when its
defined conditions are actually satisfied. Strength is graded with the
documented convention in relations.strength_points.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .chart import NatalChart
from .constants import (
    DEBILITATION,
    DUSTHANAS,
    EXALTATION,
    KENDRAS,
    RASHI_LORDS,
    RASHIS,
    house_from,
    ordinal,
)
from .relations import (
    describe_sambandha,
    grade,
    is_own_or_exalted,
    sambandha,
    strength_points,
)


@dataclass
class YogaMatch:
    id: str
    name: str
    group: str
    planets: list[str]
    houses: list[int]
    strength: str
    conditions: list[str]
    modifiers: list[str] = field(default_factory=list)
    key: str = ""  # distinguishes multiple instances of the same yoga

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "group": self.group,
            "planets": self.planets,
            "houses": self.houses,
            "strength": self.strength,
            "conditions": self.conditions,
            "modifiers": self.modifiers,
            "key": self.key or self.id,
        }


@dataclass(frozen=True)
class YogaRule:
    id: str
    name: str
    group: str
    definition: str
    evaluate: Callable[[NatalChart], list[YogaMatch]]


def _grade_planets(chart, planets):
    pts, notes = 0, []
    for p in planets:
        p_pts, p_notes = strength_points(chart, p)
        pts += p_pts
        notes += p_notes
    # Normalise for multi-planet yogas: average, rounded toward zero.
    if len(planets) > 1:
        pts = int(pts / len(planets)) if pts >= 0 else -int(-pts / len(planets))
    return grade(pts), notes


def _loc(chart, p):
    pl = chart.planets[p]
    return f"{p} in {RASHIS[pl.sign]} ({ordinal(pl.house)} house)"


# ---------------------------------------------------------------------------
# Lunar yogas
# ---------------------------------------------------------------------------

def gaja_kesari(chart: NatalChart):
    h = chart.house_from_moon("Jupiter")
    if h not in KENDRAS:
        return []
    strength, notes = _grade_planets(chart, ["Jupiter", "Moon"])
    return [YogaMatch(
        "gaja_kesari", "Gaja Kesari Yoga", "lunar", ["Jupiter", "Moon"],
        [chart.house_of("Jupiter"), chart.house_of("Moon")], strength,
        [f"Jupiter is in the {ordinal(h)} house from the Moon (a kendra)",
         _loc(chart, "Jupiter"), _loc(chart, "Moon")], notes)]


def chandra_mangala(chart: NatalChart):
    kinds = sambandha(chart, "Moon", "Mars")
    kinds = [k for k in kinds if k in ("conjunction", "mutual aspect")]
    if not kinds:
        return []
    strength, notes = _grade_planets(chart, ["Moon", "Mars"])
    if "conjunction" not in kinds:
        strength = "Moderate" if strength == "Strong" else strength
        notes.append("Formed by mutual aspect rather than conjunction")
    return [YogaMatch(
        "chandra_mangala", "Chandra-Mangala Yoga", "lunar", ["Moon", "Mars"],
        [chart.house_of("Moon"), chart.house_of("Mars")], strength,
        [f"Moon and Mars are related by {describe_sambandha(kinds)}", _loc(chart, "Moon"), _loc(chart, "Mars")],
        notes)]


def _lunar_neighbours(chart):
    moon = chart.planets["Moon"].sign
    second = [p for p in ("Mars", "Mercury", "Jupiter", "Venus", "Saturn") if chart.planets[p].sign == (moon + 1) % 12]
    twelfth = [p for p in ("Mars", "Mercury", "Jupiter", "Venus", "Saturn") if chart.planets[p].sign == (moon - 1) % 12]
    return second, twelfth


def sunapha_anapha_durudhara(chart: NatalChart):
    second, twelfth = _lunar_neighbours(chart)
    if second and twelfth:
        strength, notes = _grade_planets(chart, second + twelfth)
        return [YogaMatch("durudhara", "Durudhara Yoga", "lunar", second + twelfth, [], strength,
                          [f"{', '.join(second)} in the 2nd from the Moon",
                           f"{', '.join(twelfth)} in the 12th from the Moon",
                           "Sun, Rahu and Ketu are excluded by rule"], notes)]
    if second:
        strength, notes = _grade_planets(chart, second)
        return [YogaMatch("sunapha", "Sunapha Yoga", "lunar", second, [], strength,
                          [f"{', '.join(second)} in the 2nd from the Moon (Sun, Rahu, Ketu excluded)"], notes)]
    if twelfth:
        strength, notes = _grade_planets(chart, twelfth)
        return [YogaMatch("anapha", "Anapha Yoga", "lunar", twelfth, [], strength,
                          [f"{', '.join(twelfth)} in the 12th from the Moon (Sun, Rahu, Ketu excluded)"], notes)]
    return []


def adhi_yoga(chart: NatalChart):
    benefics = [p for p in ("Mercury", "Jupiter", "Venus") if chart.house_from_moon(p) in (6, 7, 8)]
    if p_merc_malefic := (not chart.planets["Mercury"].benefic):
        benefics = [b for b in benefics if b != "Mercury"]
    if len(benefics) < 2:
        return []
    houses = sorted({chart.house_from_moon(b) for b in benefics})
    strength, notes = _grade_planets(chart, benefics)
    if len(houses) == 3:
        notes.append("Benefics occupy all three of the 6th, 7th and 8th from the Moon")
    if p_merc_malefic:
        notes.append("Mercury is associated with a malefic and is not counted")
    return [YogaMatch("adhi", "Adhi Yoga", "lunar", benefics, [], strength,
                      [f"{b} in the {ordinal(chart.house_from_moon(b))} from the Moon" for b in benefics], notes)]


def amala(chart: NatalChart):
    out = []
    for ref, ref_name in ((chart.lagna_sign, "Lagna"), (chart.planets["Moon"].sign, "Moon")):
        tenth = (ref + 9) % 12
        occ = [p for p in ("Jupiter", "Venus", "Mercury") if chart.planets[p].sign == tenth
               and chart.planets[p].benefic]
        if occ:
            strength, notes = _grade_planets(chart, occ)
            out.append(YogaMatch("amala", "Amala Yoga", "other", occ, [], strength,
                                 [f"{', '.join(occ)} in the 10th from the {ref_name}"], notes, key=f"amala_{ref_name}"))
            break
    return out


def vasumati(chart: NatalChart):
    benefics = ["Jupiter", "Venus"] + (["Mercury"] if chart.planets["Mercury"].benefic else [])
    if all(chart.house_from_moon(b) in (3, 6, 10, 11) for b in benefics):
        strength, notes = _grade_planets(chart, benefics)
        return [YogaMatch("vasumati", "Vasumati Yoga", "dhana", benefics, [], strength,
                          [f"{b} in the {ordinal(chart.house_from_moon(b))} from the Moon (upachaya)" for b in benefics],
                          notes)]
    return []


# ---------------------------------------------------------------------------
# Solar yogas
# ---------------------------------------------------------------------------

def budha_aditya(chart: NatalChart):
    if chart.planets["Sun"].sign != chart.planets["Mercury"].sign:
        return []
    merc = chart.planets["Mercury"]
    strength, notes = _grade_planets(chart, ["Sun", "Mercury"])
    if merc.sun_distance < 3:
        strength = "Weak"
        notes.append(f"Mercury is within {merc.sun_distance:.1f}° of the Sun (deeply combust)")
    return [YogaMatch("budha_aditya", "Budha-Aditya Yoga", "solar", ["Sun", "Mercury"],
                      [chart.house_of("Sun")], strength,
                      [f"Sun and Mercury are together in {RASHIS[merc.sign]} ({ordinal(merc.house)} house)"],
                      notes)]


def vesi_vasi(chart: NatalChart):
    sun = chart.planets["Sun"].sign
    cands = ("Mars", "Mercury", "Jupiter", "Venus", "Saturn")
    second = [p for p in cands if chart.planets[p].sign == (sun + 1) % 12]
    twelfth = [p for p in cands if chart.planets[p].sign == (sun - 1) % 12]
    if second and twelfth:
        strength, notes = _grade_planets(chart, second + twelfth)
        return [YogaMatch("ubhayachari", "Ubhayachari Yoga", "solar", second + twelfth, [], strength,
                          [f"{', '.join(second)} in the 2nd and {', '.join(twelfth)} in the 12th from the Sun"], notes)]
    if second:
        strength, notes = _grade_planets(chart, second)
        return [YogaMatch("vesi", "Vesi Yoga", "solar", second, [], strength,
                          [f"{', '.join(second)} in the 2nd from the Sun (Moon, Rahu, Ketu excluded)"], notes)]
    if twelfth:
        strength, notes = _grade_planets(chart, twelfth)
        return [YogaMatch("vasi", "Vasi Yoga", "solar", twelfth, [], strength,
                          [f"{', '.join(twelfth)} in the 12th from the Sun (Moon, Rahu, Ketu excluded)"], notes)]
    return []


# ---------------------------------------------------------------------------
# Pancha Mahapurusha
# ---------------------------------------------------------------------------

MAHAPURUSHA = {
    "Mars": ("ruchaka", "Ruchaka Yoga"),
    "Mercury": ("bhadra", "Bhadra Yoga"),
    "Jupiter": ("hamsa", "Hamsa Yoga"),
    "Venus": ("malavya", "Malavya Yoga"),
    "Saturn": ("sasa", "Sasa Yoga"),
}


def pancha_mahapurusha(chart: NatalChart):
    out = []
    for p, (yid, name) in MAHAPURUSHA.items():
        pl = chart.planets[p]
        if pl.house in KENDRAS and pl.dignity in ("exalted", "moolatrikona", "own"):
            strength, notes = _grade_planets(chart, [p])
            if pl.combust:
                notes.append("Combustion reduces the yoga's expression")
            out.append(YogaMatch(yid, name, "mahapurusha", [p], [pl.house], strength,
                                 [f"{p} is in its {'exaltation' if pl.dignity == 'exalted' else 'own'} sign "
                                  f"{RASHIS[pl.sign]}", f"{p} occupies the {ordinal(pl.house)} house, a kendra"],
                                 notes))
    return out


# ---------------------------------------------------------------------------
# Raja / Dhana yogas
# ---------------------------------------------------------------------------

def _lord_pairs(chart, group_a, group_b):
    pairs = {}
    for ha in group_a:
        for hb in group_b:
            if ha == hb:
                continue
            la, lb = chart.house_lord(ha), chart.house_lord(hb)
            if la == lb:
                continue
            key = tuple(sorted((la, lb)))
            kinds = sambandha(chart, la, lb)
            if not kinds:
                continue
            entry = pairs.setdefault(key, {"houses": set(), "kinds": kinds, "planets": [la, lb], "roles": []})
            entry["houses"].update({ha, hb})
            entry["roles"].append(f"{ordinal(ha)} lord {la} and {ordinal(hb)} lord {lb}")
    return pairs


def kendra_trikona_raja(chart: NatalChart):
    out = []
    pairs = _lord_pairs(chart, [1, 4, 7, 10], [1, 5, 9])
    for key, e in pairs.items():
        strength, notes = _grade_planets(chart, e["planets"])
        roles = sorted(set(e["roles"]))
        out.append(YogaMatch(
            "raja_kendra_trikona", "Raja Yoga (Kendra-Trikona)", "raja", list(key), sorted(e["houses"]), strength,
            [f"{r} are related by {describe_sambandha(e['kinds'])}" for r in roles], notes,
            key=f"raja_{'_'.join(key)}"))
    return out


def yogakaraka(chart: NatalChart):
    out = []
    for p in ("Mars", "Venus", "Saturn", "Mercury", "Jupiter", "Moon", "Sun"):
        owned = chart.houses_ruled_by(p)
        k = [h for h in owned if h in (4, 7, 10)]
        t = [h for h in owned if h in (5, 9)]
        if k and t:
            strength, notes = _grade_planets(chart, [p])
            out.append(YogaMatch(
                "yogakaraka", f"Yogakaraka {p}", "raja", [p], owned, strength,
                [f"{p} rules both the {ordinal(k[0])} house (kendra) and the {ordinal(t[0])} house (trikona)",
                 _loc(chart, p)], notes, key=f"yogakaraka_{p}"))
    return out


def dharma_karmadhipati(chart: NatalChart):
    l9, l10 = chart.house_lord(9), chart.house_lord(10)
    if l9 == l10:
        return []  # covered by Yogakaraka
    kinds = sambandha(chart, l9, l10)
    if not kinds:
        return []
    strength, notes = _grade_planets(chart, [l9, l10])
    return [YogaMatch("dharma_karmadhipati", "Dharma-Karmadhipati Yoga", "raja", [l9, l10], [9, 10], strength,
                      [f"9th lord {l9} and 10th lord {l10} are related by {describe_sambandha(kinds)}",
                       _loc(chart, l9), _loc(chart, l10)], notes)]


def dhana_yogas(chart: NatalChart):
    out = []
    pairs = _lord_pairs(chart, [2, 11], [1, 5, 9])
    for key, e in pairs.items():
        strength, notes = _grade_planets(chart, e["planets"])
        out.append(YogaMatch("dhana", "Dhana Yoga", "dhana", list(key), sorted(e["houses"]), strength,
                             [f"{r} are related by {describe_sambandha(e['kinds'])}" for r in sorted(set(e["roles"]))],
                             notes, key=f"dhana_{'_'.join(key)}"))
    l2, l11 = chart.house_lord(2), chart.house_lord(11)
    if l2 != l11:
        kinds = sambandha(chart, l2, l11)
        if kinds:
            strength, notes = _grade_planets(chart, [l2, l11])
            out.append(YogaMatch("dhana", "Dhana Yoga", "dhana", [l2, l11], [2, 11], strength,
                                 [f"2nd lord {l2} and 11th lord {l11} are related by {describe_sambandha(kinds)}"],
                                 notes, key="dhana_2_11"))
    return out


def lakshmi(chart: NatalChart):
    l9, l1 = chart.house_lord(9), chart.house_lord(1)
    p9 = chart.planets[l9]
    if p9.dignity not in ("exalted", "moolatrikona", "own"):
        return []
    if p9.house not in (1, 4, 5, 7, 9, 10):
        return []
    p1 = chart.planets[l1]
    if p1.dignity == "debilitated" or p1.house in DUSTHANAS or p1.combust:
        return []
    strength, notes = _grade_planets(chart, [l9, l1])
    return [YogaMatch("lakshmi", "Lakshmi Yoga", "dhana", sorted({l9, l1}), [9, 1], strength,
                      [f"9th lord {l9} is {p9.dignity}{' sign' if p9.dignity == 'own' else ''} in the "
                       f"{ordinal(p9.house)} house (kendra/trikona)",
                       f"Lagna lord {l1} is not debilitated, combust or in a dusthana"], notes)]


def saraswati(chart: NatalChart):
    good = {1, 2, 4, 5, 7, 9, 10}
    trio = ["Jupiter", "Venus", "Mercury"]
    if not all(chart.house_of(p) in good for p in trio):
        return []
    if chart.planets["Jupiter"].dignity not in ("exalted", "moolatrikona", "own", "great friend", "friend"):
        return []
    strength, notes = _grade_planets(chart, trio)
    return [YogaMatch("saraswati", "Saraswati Yoga", "other", trio, sorted({chart.house_of(p) for p in trio}),
                      strength,
                      [f"{p} in the {ordinal(chart.house_of(p))} house" for p in trio] +
                      [f"Jupiter is in a {chart.planets['Jupiter'].dignity} sign"], notes)]


# ---------------------------------------------------------------------------
# Viparita Raja
# ---------------------------------------------------------------------------

def viparita_raja(chart: NatalChart):
    out = []
    names = {6: ("harsha", "Harsha Yoga (Viparita Raja)"), 8: ("sarala", "Sarala Yoga (Viparita Raja)"),
             12: ("vimala", "Vimala Yoga (Viparita Raja)")}
    lagna_lord = chart.house_lord(1)
    for h, (yid, name) in names.items():
        lord = chart.house_lord(h)
        if lord == lagna_lord:
            continue
        pl = chart.planets[lord]
        if pl.house in DUSTHANAS:
            mods = []
            others = [x for x in chart.houses_ruled_by(lord) if x != h and x not in DUSTHANAS]
            if others:
                mods.append(f"{lord} also rules the {', '.join(ordinal(x) for x in others)} house, which mixes the results")
            strength = "Moderate" if others else "Strong"
            if pl.dignity == "debilitated":
                strength = "Weak"
            out.append(YogaMatch(yid, name, "viparita", [lord], [h, pl.house], strength,
                                 [f"{ordinal(h)} lord {lord} is placed in the {ordinal(pl.house)} house (a dusthana)"],
                                 mods, key=yid))
    return out


# ---------------------------------------------------------------------------
# Neecha Bhanga
# ---------------------------------------------------------------------------

def neecha_bhanga(chart: NatalChart):
    out = []
    moon_sign = chart.planets["Moon"].sign
    for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        pl = chart.planets[p]
        if pl.dignity != "debilitated":
            continue
        deb_sign = DEBILITATION[p][0]
        dispositor = RASHI_LORDS[deb_sign]
        exalt_in_deb = [q for q, (s, _) in EXALTATION.items() if s == deb_sign and q not in ("Rahu", "Ketu")]
        exalt_lord = RASHI_LORDS[EXALTATION[p][0]]
        reasons = []

        def kendra_from_lagna_or_moon(q):
            qs = chart.planets[q].sign
            return house_from(chart.lagna_sign, qs) in KENDRAS or house_from(moon_sign, qs) in KENDRAS

        if dispositor != p and kendra_from_lagna_or_moon(dispositor):
            reasons.append(f"{dispositor}, lord of the debilitation sign {RASHIS[deb_sign]}, is in a kendra "
                           "from the Lagna or the Moon")
        for q in exalt_in_deb:
            if q != p and kendra_from_lagna_or_moon(q):
                reasons.append(f"{q}, which is exalted in {RASHIS[deb_sign]}, is in a kendra from the Lagna or the Moon")
        if exalt_lord != p and kendra_from_lagna_or_moon(exalt_lord):
            reasons.append(f"{exalt_lord}, lord of {p}'s exaltation sign, is in a kendra from the Lagna or the Moon")
        if dispositor != p and (chart.planets[dispositor].sign == pl.sign or
                                chart.is_aspected_by(p, dispositor)):
            reasons.append(f"The dispositor {dispositor} joins or aspects the debilitated {p}")
        if pl.vargas["9"]["dignity"] == "exalted":
            reasons.append(f"{p} is exalted in the Navamsa (D9)")
        if dispositor != p and RASHI_LORDS[chart.planets[dispositor].sign] == p:
            reasons.append(f"{p} and {dispositor} exchange signs")
        if reasons:
            strength = "Strong" if len(reasons) >= 2 else "Moderate"
            if pl.house in KENDRAS and len(reasons) >= 1:
                reasons.append(f"The debilitated {p} itself occupies a kendra")
            out.append(YogaMatch("neecha_bhanga", "Neecha Bhanga Raja Yoga", "neecha_bhanga", [p], [pl.house],
                                 strength, [f"{p} is debilitated in {RASHIS[deb_sign]}"] + reasons, [],
                                 key=f"neecha_bhanga_{p}"))
    return out


# ---------------------------------------------------------------------------
# Parivartana
# ---------------------------------------------------------------------------

def parivartana(chart: NatalChart):
    out = []
    seven = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    for i, a in enumerate(seven):
        for b in seven[i + 1:]:
            if RASHI_LORDS[chart.planets[a].sign] == b and RASHI_LORDS[chart.planets[b].sign] == a:
                ha, hb = chart.house_of(a), chart.house_of(b)
                houses = {ha, hb}
                if houses & DUSTHANAS:
                    yid, name, strength = "dainya_parivartana", "Dainya Parivartana Yoga", "Weak"
                elif 3 in houses:
                    yid, name, strength = "khala_parivartana", "Khala Parivartana Yoga", "Moderate"
                else:
                    yid, name, strength = "maha_parivartana", "Maha Parivartana Yoga", "Strong"
                out.append(YogaMatch(yid, name, "parivartana", [a, b], sorted(houses), strength,
                                     [f"{a} is in {RASHIS[chart.planets[a].sign]} (owned by {b}) and {b} is in "
                                      f"{RASHIS[chart.planets[b].sign]} (owned by {a})",
                                      f"Houses exchanged: {ordinal(ha)} and {ordinal(hb)}"], [],
                                     key=f"parivartana_{a}_{b}"))
    return out


# ---------------------------------------------------------------------------
# Adverse lunar combination
# ---------------------------------------------------------------------------

def shakata(chart: NatalChart):
    h = house_from(chart.planets["Jupiter"].sign, chart.planets["Moon"].sign)
    if h not in (6, 8, 12):
        return []
    mods = []
    if chart.house_of("Moon") in KENDRAS:
        return []  # cancelled: Moon in a kendra from the Lagna
    return [YogaMatch("shakata", "Shakata Yoga", "adverse", ["Moon", "Jupiter"], [], "Moderate",
                      [f"The Moon is in the {ordinal(h)} house from Jupiter",
                       "The Moon is not in a kendra from the Lagna (which would cancel it)"], mods)]


YOGA_RULES: list[YogaRule] = [
    YogaRule("gaja_kesari", "Gaja Kesari Yoga", "lunar",
             "Jupiter occupies a kendra (1st, 4th, 7th or 10th) counted from the Moon.", gaja_kesari),
    YogaRule("budha_aditya", "Budha-Aditya Yoga", "solar",
             "Sun and Mercury occupy the same sign. Graded weak when Mercury is within 3° of the Sun.", budha_aditya),
    YogaRule("chandra_mangala", "Chandra-Mangala Yoga", "lunar",
             "Moon and Mars are conjunct (same sign) or in mutual aspect.", chandra_mangala),
    YogaRule("pancha_mahapurusha", "Pancha Mahapurusha Yogas", "mahapurusha",
             "Mars, Mercury, Jupiter, Venus or Saturn in its own, moolatrikona or exaltation sign while occupying "
             "a kendra from the Lagna (Ruchaka, Bhadra, Hamsa, Malavya, Sasa).", pancha_mahapurusha),
    YogaRule("raja_kendra_trikona", "Raja Yoga (Kendra-Trikona)", "raja",
             "The lord of a kendra (1, 4, 7, 10) and the lord of a trikona (1, 5, 9), being different planets, are "
             "related by conjunction, mutual aspect or exchange of signs.", kendra_trikona_raja),
    YogaRule("yogakaraka", "Yogakaraka", "raja",
             "A single planet rules both a kendra (4, 7, 10) and a trikona (5, 9) from the Lagna.", yogakaraka),
    YogaRule("dharma_karmadhipati", "Dharma-Karmadhipati Yoga", "raja",
             "The 9th lord and 10th lord are related by conjunction, mutual aspect or exchange.", dharma_karmadhipati),
    YogaRule("dhana", "Dhana Yoga", "dhana",
             "A lord of a wealth house (2nd or 11th) is related to a lord of the 1st, 5th or 9th, or the 2nd and 11th "
             "lords are related (conjunction, mutual aspect or exchange).", dhana_yogas),
    YogaRule("lakshmi", "Lakshmi Yoga", "dhana",
             "The 9th lord is in its own, moolatrikona or exaltation sign in a kendra or trikona, and the Lagna lord "
             "is not debilitated, combust or in a dusthana.", lakshmi),
    YogaRule("viparita_raja", "Viparita Raja Yogas", "viparita",
             "The lord of the 6th (Harsha), 8th (Sarala) or 12th (Vimala) occupies a dusthana (6th, 8th or 12th). "
             "Not applied when that planet also rules the Lagna.", viparita_raja),
    YogaRule("neecha_bhanga", "Neecha Bhanga Raja Yoga", "neecha_bhanga",
             "A debilitated planet whose debilitation is cancelled by at least one classical condition: dispositor, "
             "the planet exalted in that sign, or the lord of its exaltation sign in a kendra from Lagna or Moon; the "
             "dispositor joining or aspecting it; exaltation in Navamsa; or exchange with its dispositor.",
             neecha_bhanga),
    YogaRule("adhi", "Adhi Yoga", "lunar",
             "At least two natural benefics (Mercury, Jupiter, Venus) occupy the 6th, 7th or 8th from the Moon.",
             adhi_yoga),
    YogaRule("lunar_flanking", "Sunapha / Anapha / Durudhara", "lunar",
             "Planets other than the Sun, Rahu and Ketu in the 2nd (Sunapha), 12th (Anapha) or both (Durudhara) "
             "from the Moon.", sunapha_anapha_durudhara),
    YogaRule("solar_flanking", "Vesi / Vasi / Ubhayachari", "solar",
             "Planets other than the Moon, Rahu and Ketu in the 2nd (Vesi), 12th (Vasi) or both (Ubhayachari) from "
             "the Sun.", vesi_vasi),
    YogaRule("amala", "Amala Yoga", "other",
             "A benefic (Jupiter, Venus or benefic Mercury) occupies the 10th from the Lagna or the Moon.", amala),
    YogaRule("vasumati", "Vasumati Yoga", "dhana",
             "All natural benefics occupy upachaya houses (3, 6, 10, 11) from the Moon.", vasumati),
    YogaRule("saraswati", "Saraswati Yoga", "other",
             "Jupiter, Venus and Mercury all occupy kendras, trikonas or the 2nd house, with Jupiter in its own, "
             "exaltation or a friendly sign.", saraswati),
    YogaRule("parivartana", "Parivartana Yogas", "parivartana",
             "Two planets occupy each other's signs: Maha (good houses), Khala (involving the 3rd), Dainya "
             "(involving the 6th, 8th or 12th).", parivartana),
    YogaRule("shakata", "Shakata Yoga", "adverse",
             "The Moon is in the 6th, 8th or 12th from Jupiter, unless the Moon occupies a kendra from the Lagna.",
             shakata),
]


def detect_yogas(chart: NatalChart) -> list[YogaMatch]:
    out = []
    for rule in YOGA_RULES:
        out.extend(rule.evaluate(chart))
    return out


def yoga_definitions() -> list[dict]:
    return [{"id": r.id, "name": r.name, "group": r.group, "definition": r.definition} for r in YOGA_RULES]
