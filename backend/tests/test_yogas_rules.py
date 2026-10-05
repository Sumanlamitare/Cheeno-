"""Yoga/Dosha detection and the rule engine. Property tests check that each
yoga is reported if and only if its defined conditions hold, across many
deterministic pseudo-random birth charts."""
import datetime as dt
import random

import pytest

from kundali.config import DEFAULT_SETTINGS
from kundali.jyotish.chart import build_chart
from kundali.jyotish.constants import KENDRAS, RASHI_LORDS, house_from
from kundali.jyotish.doshas import detect_doshas
from kundali.jyotish.relations import sambandha
from kundali.jyotish.yogas import detect_yogas
from kundali.rules import career, children, dasha, education, family, health, lagna, marriage, travel, vargas, wealth
from kundali.rules.data.houses import BHAVESHA
from kundali.rules.data.nakshatras import NAKSHATRA_DATA
from kundali.rules.data.planets import PLANET_IN_HOUSE
from kundali.rules.engine import CONDITIONS, ChartContext, run_rules


def random_charts(n=150, seed=7):
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        t = dt.datetime(1950, 1, 1, tzinfo=dt.timezone.utc) + dt.timedelta(minutes=rng.randrange(0, 70 * 525600))
        lat = rng.uniform(-50, 60)
        lon = rng.uniform(-170, 170)
        out.append(build_chart(t, lat, lon, DEFAULT_SETTINGS))
    return out


CHARTS = random_charts()


def ids(chart):
    return {y.id for y in detect_yogas(chart)}


@pytest.mark.parametrize("i", range(len(CHARTS)))
def test_yoga_conditions_iff(i):
    c = CHARTS[i]
    found = ids(c)
    # Gaja Kesari: Jupiter in a kendra from the Moon
    assert ("gaja_kesari" in found) == (house_from(c.planets["Moon"].sign, c.planets["Jupiter"].sign) in KENDRAS)
    # Budha-Aditya: Sun and Mercury in the same sign
    assert ("budha_aditya" in found) == (c.planets["Sun"].sign == c.planets["Mercury"].sign)
    # Pancha Mahapurusha
    for p, yid in (("Mars", "ruchaka"), ("Mercury", "bhadra"), ("Jupiter", "hamsa"), ("Venus", "malavya"),
                   ("Saturn", "sasa")):
        pl = c.planets[p]
        expected = pl.house in KENDRAS and pl.dignity in ("exalted", "moolatrikona", "own")
        assert (yid in found) == expected
    # Dharma-Karmadhipati
    l9, l10 = c.house_lord(9), c.house_lord(10)
    assert ("dharma_karmadhipati" in found) == (l9 != l10 and bool(sambandha(c, l9, l10)))
    # Viparita Raja: 6th lord in dusthana (and not Lagna lord)
    l6 = c.house_lord(6)
    assert ("harsha" in found) == (l6 != c.house_lord(1) and c.planets[l6].house in (6, 8, 12))
    # Chandra-Mangala
    cm = c.planets["Moon"].sign == c.planets["Mars"].sign or "mutual aspect" in sambandha(c, "Moon", "Mars")
    assert ("chandra_mangala" in found) == cm
    # Neecha Bhanga only for debilitated planets
    for y in detect_yogas(c):
        if y.id == "neecha_bhanga":
            assert c.planets[y.planets[0]].dignity == "debilitated"


@pytest.mark.parametrize("i", range(0, len(CHARTS), 3))
def test_dosha_rules(i):
    c = CHARTS[i]
    d = {x["id"]: x for x in detect_doshas(c)}
    mars_from_lagna = c.planets["Mars"].house
    if mars_from_lagna in (1, 2, 4, 7, 8, 12):
        assert d["mangal"]["detected"] and "Lagna" in d["mangal"]["triggeredFrom"]
    rahu = c.planets["Rahu"].longitude
    offs = [(c.planets[p].longitude - rahu) % 360 for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")]
    expected = all(0 < o < 180 for o in offs) or all(180 < o < 360 for o in offs)
    assert d["kaal_sarp"]["detected"] == expected
    assert d["gandamula"]["detected"] == (c.planets["Moon"].nakshatra in {0, 8, 9, 17, 18, 26})


def test_meaning_tables_complete():
    from kundali.rules.data.meaning import LORD_YOU, PLANET_YOU, THEME_YOU
    for area, table in LORD_YOU.items():
        assert set(table) == set(range(1, 13)), area
    for rules in ALL_RULE_MODULES[:8]:
        for r in rules:
            if r.polarity in ("positive", "negative", "mixed"):
                assert r.polarity in THEME_YOU.get(r.theme, {}), (r.theme, r.polarity)
    for p, t in PLANET_YOU.items():
        assert "steady" in t


def test_rule_tables_complete():
    for h in range(1, 13):
        assert set(BHAVESHA[h]) == set(range(1, 13))
        for y in range(1, 13):
            pol, text = BHAVESHA[h][y]
            assert pol in ("positive", "negative", "mixed") and len(text) > 40
    for p, table in PLANET_IN_HOUSE.items():
        assert set(table) == set(range(1, 13))
    assert len(NAKSHATRA_DATA) == 27


ALL_RULE_MODULES = [career.RULES, wealth.RULES, marriage.RULES, education.RULES, family.RULES, travel.RULES,
                    children.RULES, health.RULES, lagna.RULES, dasha.RULES, vargas.D9_RULES, vargas.D10_RULES]


def test_rule_ids_unique_and_conditions_known():
    seen = set()
    for rules in ALL_RULE_MODULES:
        for r in rules:
            assert r.id not in seen, r.id
            seen.add(r.id)
            assert r.tier in ("major", "strong", "moderate", "minor")
            assert r.polarity in ("positive", "negative", "mixed", "neutral")
            for c in r.when:
                assert c["t"] in CONDITIONS
    assert len(seen) > 450


@pytest.mark.parametrize("i", range(0, len(CHARTS), 10))
def test_every_match_has_reasons(i):
    c = CHARTS[i]
    ctx = ChartContext(chart=c, yogas=detect_yogas(c), doshas=detect_doshas(c), dasha={"MD": "Saturn", "AD": "Mercury"})
    for rules in ALL_RULE_MODULES:
        for m in run_rules(ctx, rules):
            assert m.reasons, m.rule.id
            assert "{" not in m.text, (m.rule.id, m.text)


def test_bhavesha_rule_matches_actual_placement():
    c = CHARTS[0]
    ctx = ChartContext(chart=c)
    matched = [m.rule.id for m in run_rules(ctx, career.RULES) if m.rule.id.startswith("career_L10_in_")]
    assert matched == [f"career_L10_in_{c.house_of(c.house_lord(10))}"]


def test_same_moon_sign_different_readings():
    # Two charts with the same Moon sign but different Lagnas must yield different readings.
    by_moon = {}
    for c in CHARTS:
        by_moon.setdefault(c.planets["Moon"].sign, []).append(c)
    pair = next(v for v in by_moon.values() if len(v) >= 2 and v[0].lagna_sign != v[1].lagna_sign)
    a, b = (lagna.analyze(ChartContext(chart=x)) for x in pair[:2])
    assert [g["text"] for g in a["strengths"] + a["challenges"]] != [g["text"] for g in b["strengths"] + b["challenges"]]
