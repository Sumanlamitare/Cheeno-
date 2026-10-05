"""Jyotish calculations: chart, nakshatra, houses, drishti, vargas,
panchanga, dasha, sade sati and shadbala."""
import datetime as dt

import pytest

from kundali.inputs.timeutil import localize
from kundali.jyotish import vargas
from kundali.jyotish.chart import build_chart, nakshatra_of
from kundali.jyotish.constants import DASHA_YEARS
from kundali.jyotish.dasha import find_active, vimshottari
from kundali.jyotish.dignity import compound_relation, sign_dignity
from kundali.jyotish.drishti import aspected_signs, sphuta_drishti
from kundali.jyotish.panchanga import compute_panchanga, karana_name, tithi_index, tithi_name, yoga_index
from kundali.jyotish.sadesati import compute_sadesati
from kundali.jyotish.shadbala import compute_shadbala

from .conftest import utc


@pytest.fixture(scope="module")
def ktm_chart():
    from kundali.config import DEFAULT_SETTINGS
    r = localize(dt.date(2000, 10, 5), dt.time(10, 30), "Asia/Kathmandu", 85.324)
    return build_chart(r["utc"], 27.7172, 85.324, DEFAULT_SETTINGS)


def test_gandhi_lagna_and_moon(settings):
    # M. K. Gandhi: 2 Oct 1869, 07:11 local mean time, Porbandar. Widely published: Libra Lagna, Moon in Cancer.
    r = localize(dt.date(1869, 10, 2), dt.time(7, 11), "Asia/Kolkata", 69.6293)
    c = build_chart(r["utc"], 21.6417, 69.6293, settings)
    assert c.ascendant.sign_name == "Libra"
    assert c.planets["Moon"].sign_name == "Cancer"
    assert c.planets["Sun"].sign_name == "Virgo"


@pytest.mark.parametrize("lon,nak,pada", [
    (0.0, 0, 1), (3.34, 0, 2), (13.3334, 1, 1), (359.99, 26, 4), (120.0, 9, 1), (119.99, 8, 4),
    (200.0, 15, 1),
])
def test_nakshatra_pada(lon, nak, pada):
    assert nakshatra_of(lon) == (nak, pada)


def test_whole_sign_houses(ktm_chart):
    c = ktm_chart
    for p, pl in c.planets.items():
        assert pl.house == (pl.sign - c.lagna_sign) % 12 + 1
    assert [c.house_sign(h) for h in range(1, 13)] == [(c.lagna_sign + i) % 12 for i in range(12)]


def test_ketu_opposite_rahu(ktm_chart):
    r, k = ktm_chart.planets["Rahu"], ktm_chart.planets["Ketu"]
    assert (k.longitude - r.longitude) % 360 == pytest.approx(180)
    assert (k.house - r.house) % 12 == 6


def test_drishti_rules():
    assert sorted(aspected_signs("Mars", 0)) == [3, 6, 7]       # 4th, 7th, 8th from Aries
    assert sorted(aspected_signs("Jupiter", 0)) == [4, 6, 8]    # 5th, 7th, 9th
    assert sorted(aspected_signs("Saturn", 0)) == [2, 6, 9]     # 3rd, 7th, 10th
    assert aspected_signs("Venus", 3) == [9]                    # 7th only
    assert aspected_signs("Rahu", 0) == [6]


def test_sphuta_drishti_full_aspects():
    assert sphuta_drishti("Venus", 0, 180) == 60
    assert sphuta_drishti("Saturn", 0, 60) == 60
    assert sphuta_drishti("Saturn", 0, 270) == 60
    assert sphuta_drishti("Jupiter", 0, 120) == 60
    assert sphuta_drishti("Mars", 0, 90) == 60
    assert sphuta_drishti("Venus", 0, 10) == 0


@pytest.mark.parametrize("planet,lon,expected", [
    ("Sun", 10.0, "exalted"), ("Sun", 190.0, "debilitated"), ("Sun", 125.0, "moolatrikona"),
    ("Sun", 145.0, "own"), ("Moon", 32.0, "exalted"), ("Moon", 40.0, "moolatrikona"),
    ("Mercury", 160.0, "exalted"), ("Mercury", 167.0, "moolatrikona"), ("Mercury", 175.0, "own"),
    ("Saturn", 310.0, "moolatrikona"), ("Saturn", 290.0, "own"), ("Jupiter", 95.0, "exalted"),
    ("Mars", 280.0, "exalted"), ("Venus", 345.0, "exalted"), ("Venus", 170.0, "debilitated"),
])
def test_dignity(planet, lon, expected):
    assert sign_dignity(planet, lon, {}) == expected


def test_compound_relationship():
    # Sun & Moon natural friends; Moon 2nd from Sun -> temporal friend -> great friend
    assert compound_relation("Sun", "Moon", 0, 1) == "great friend"
    # Sun & Saturn natural enemies; same sign -> temporal enemy -> great enemy
    assert compound_relation("Sun", "Saturn", 0, 0) == "great enemy"


@pytest.mark.parametrize("lon,d,expected", [
    (0.0, 9, 0), (3.34, 9, 1), (30.0, 9, 9), (60.0, 9, 6), (90.0, 9, 3), (359.99, 9, 11),
    (0.0, 10, 0), (30.0, 10, 9), (59.9, 10, 6),
    (10.0, 2, 4), (20.0, 2, 3), (40.0, 2, 3), (50.0, 2, 4),
    (15.0, 3, 4), (25.0, 3, 8),
    (8.0, 4, 3),
    (0.0, 7, 0), (30.0, 7, 7),
    (29.0, 12, 11),
    (3.0, 30, 0), (7.0, 30, 10), (12.0, 30, 8), (20.0, 30, 2), (27.0, 30, 6),
    (33.0, 30, 1), (38.0, 30, 5), (45.0, 30, 11), (52.0, 30, 9), (58.0, 30, 7),
    (0.6, 60, 1), (0.0, 16, 0), (30.0, 16, 4), (60.0, 16, 8),
    (0.0, 20, 0), (30.0, 20, 8), (60.0, 20, 4),
    (0.0, 24, 4), (30.0, 24, 3),
    (0.0, 27, 0), (30.0, 27, 3), (60.0, 27, 6), (90.0, 27, 9),
    (0.0, 40, 0), (30.0, 40, 6), (0.0, 45, 0), (30.0, 45, 4),
])
def test_vargas(lon, d, expected):
    assert vargas.varga_sign(lon, d) == expected


def test_d9_matches_absolute_formula():
    for i in range(3600):
        lon = i * 0.1
        assert vargas.d9(lon) == int(lon * 9 / 30) % 12
        assert vargas.d27(lon) == int(lon * 27 / 30) % 12


def test_panchanga_formulas():
    assert tithi_index(0, 11.9)[0] == 1
    assert tithi_index(0, 180.1)[0] == 16
    assert tithi_name(15) == ("Shukla", "Purnima")
    assert tithi_name(30) == ("Krishna", "Amavasya")
    assert yoga_index(0, 13.34) == 1
    assert karana_name(0, 1) == "Kimstughna"
    assert karana_name(0, 7) == "Bava"
    assert karana_name(0, 345) == "Shakuni"
    assert karana_name(0, 350) == "Chatushpada"
    assert karana_name(0, 359) == "Naga"
    assert karana_name(0, 20) == "Kaulava"


def test_birth_panchanga_durga_ashtami_2000(ktm_chart):
    # 5 Oct 2000 was Durga Ashtami (Ashwin Shukla Ashtami), a Thursday.
    p = compute_panchanga(ktm_chart)
    assert p["tithi"]["label"] == "Shukla Ashtami"
    assert p["vara"]["english"] == "Thursday"
    assert p["lunarMonth"]["purnimanta"] == "Ashwin"
    assert p["ishtaKala"]["ghati"] == 11


def test_vara_before_sunrise_is_previous_day(settings):
    # 04:00 NPT on a Friday is still Thursday's Hindu day (before sunrise).
    r = localize(dt.date(2000, 10, 6), dt.time(4, 0), "Asia/Kathmandu", 85.324)
    c = build_chart(r["utc"], 27.7172, 85.324, settings)
    assert compute_panchanga(c)["vara"]["english"] == "Thursday"


def test_vimshottari_balance_and_totals():
    birth = utc(2000, 1, 1)
    d = vimshottari(0.0, birth)
    assert d["startingLord"] == "Ketu"
    assert d["balanceYears"] == pytest.approx(7.0)
    half = vimshottari(360 / 27 / 2, birth)
    assert half["balanceYears"] == pytest.approx(3.5)
    bharani = vimshottari(360 / 27 * 1.25, birth)
    assert bharani["startingLord"] == "Venus" and bharani["balanceYears"] == pytest.approx(15.0)
    total = sum((p["end"] - p["start"]).total_seconds() for p in d["periods"])
    assert total / 86400 / 365.25 == pytest.approx(120.0)


def test_antardasha_proportions():
    d = vimshottari(360 / 27 * 1.0, utc(2000, 1, 1))  # start of Bharani -> full Venus MD
    venus = d["periods"][0]
    assert venus["lord"] == "Venus"
    ads = venus["children"]
    assert [a["lord"] for a in ads][:3] == ["Venus", "Sun", "Moon"]
    first = (ads[0]["end"] - ads[0]["start"]).total_seconds() / 86400 / 365.25
    assert first == pytest.approx(20 * 20 / 120)
    assert ads[-1]["end"] == venus["end"]
    pds = ads[0]["children"]
    assert (pds[0]["end"] - pds[0]["start"]).total_seconds() / 86400 / 365.25 == pytest.approx(20 * 20 / 120 * 20 / 120)
    for md in d["periods"]:
        assert (md["end"] - md["start"]).total_seconds() / 86400 / 365.25 == pytest.approx(DASHA_YEARS[md["lord"]])


def test_find_active_chain():
    d = vimshottari(100.0, utc(1990, 1, 1))
    chain = find_active(d["periods"], utc(2026, 1, 1))
    assert len(chain) == 3
    assert chain[0]["start"] <= utc(2026, 1, 1) < chain[0]["end"]
    assert chain[1] in chain[0]["children"] and chain[2] in chain[1]["children"]


def test_sade_sati_aquarius_moon(settings):
    # Natal Moon in Aquarius: Saturn entered Capricorn 24 Jan 2020 and finally leaves Pisces in Feb 2028.
    r = localize(dt.date(1995, 3, 1), dt.time(12), "UTC", 0)
    c = build_chart(r["utc"], 0.0, 0.0, settings)
    assert c.planets["Moon"].sign == 10
    ss = compute_sadesati(c, utc(2024, 1, 1))
    cur = ss["currentCycle"]
    assert cur is not None
    assert cur["start"][:7] == "2020-01"
    assert cur["end"][:7] in ("2028-02", "2028-03")
    assert ss["currentPhase"] == 2  # Saturn over Aquarius in 2024


def test_sade_sati_sagittarius_moon_ended_2023(ktm_chart):
    ss = compute_sadesati(ktm_chart, utc(2026, 1, 1))
    assert ss["status"] == "Not active"
    past = [c for c in ss["cycles"] if c["status"] == "past"]
    assert past[-1]["end"][:10] == "2023-01-17"


def test_shadbala_reasonable(ktm_chart):
    p = compute_panchanga(ktm_chart)
    sb = compute_shadbala(ktm_chart, p["_sun"])
    for planet, v in sb["planets"].items():
        assert 2.0 < v["rupas"] < 14.0, planet
        c = v["components"]
        assert 0 <= c["sthana"]["uccha"] <= 60
        assert 0 <= c["dig"] <= 60
        assert 0 <= c["chesta"] <= 60
    assert sb["planets"]["Sun"]["components"]["naisargika"] == 60.0
