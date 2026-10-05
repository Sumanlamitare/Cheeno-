"""Ephemeris-level checks against known astronomical events (all times UTC)."""
import pytest
import swisseph as swe

from kundali.astro import ephemeris as eph
from kundali.jyotish.panchanga import tithi_index

from .conftest import utc


def lon(name, when, settings):
    return eph.sidereal_longitude(eph.julian_day(when), name, settings)


def test_lahiri_ayanamsha_j2000(settings):
    # Lahiri ayanamsha at J2000.0 is about 23°51'
    assert eph.ayanamsha(2451545.0, settings) == pytest.approx(23.85, abs=0.02)


def test_sidereal_equals_tropical_minus_ayanamsha(settings):
    jd = eph.julian_day(utc(2010, 6, 1, 12))
    trop, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)
    expected = (trop[0] - eph.ayanamsha(jd, settings)) % 360
    # Swiss Ephemeris sidereal mode differs from (true tropical - mean ayanamsha) only by nutation (< 20").
    assert lon("Sun", utc(2010, 6, 1, 12), settings) == pytest.approx(expected, abs=0.006)


def test_sun_j2000(settings):
    # Apparent tropical Sun at J2000 ~280.37°, sidereal ~256.5° (Sagittarius ~16.5°)
    s = lon("Sun", utc(2000, 1, 1, 12), settings)
    assert s == pytest.approx(256.52, abs=0.1)


def test_makar_sankranti_2024(settings):
    # Sun enters sidereal Capricorn on the night of 14/15 Jan 2024 (IST)
    assert lon("Sun", utc(2024, 1, 14, 12), settings) < 270
    assert lon("Sun", utc(2024, 1, 15, 6), settings) > 270


def test_mesh_sankranti_2024_nepali_new_year(settings):
    # Sun enters sidereal Aries on 13 April 2024 (Nepali New Year 2081)
    assert lon("Sun", utc(2024, 4, 13, 6), settings) > 350
    assert lon("Sun", utc(2024, 4, 14, 6), settings) < 10


def test_full_moon_2024_01_25(settings):
    # Full Moon 2024-01-25 17:54 UTC: tithi changes from 15 to 16
    def tithi(t):
        jd = eph.julian_day(t)
        return tithi_index(eph.sidereal_longitude(jd, "Sun", settings), eph.sidereal_longitude(jd, "Moon", settings))[0]
    assert tithi(utc(2024, 1, 25, 17, 30)) == 15
    assert tithi(utc(2024, 1, 25, 18, 20)) == 16


def test_new_moon_eclipse_2024_04_08(settings):
    jd = eph.julian_day(utc(2024, 4, 8, 18, 21))
    el = (eph.sidereal_longitude(jd, "Moon", settings) - eph.sidereal_longitude(jd, "Sun", settings)) % 360
    assert min(el, 360 - el) < 0.3


def test_mercury_retrograde_dec_2023(settings):
    assert eph.body_position(eph.julian_day(utc(2023, 12, 20)), "Mercury", settings).speed < 0
    assert eph.body_position(eph.julian_day(utc(2024, 1, 10)), "Mercury", settings).speed > 0


def test_jupiter_retrograde_2023(settings):
    assert eph.body_position(eph.julian_day(utc(2023, 10, 15)), "Jupiter", settings).speed < 0


def test_rahu_ketu_axis(settings):
    jd = eph.julian_day(utc(2024, 6, 1))
    r = eph.body_position(jd, "Rahu", settings)
    k = eph.body_position(jd, "Ketu", settings)
    assert (k.longitude - r.longitude) % 360 == pytest.approx(180, abs=1e-9)
    assert int(r.longitude // 30) == 11  # Rahu in Pisces in 2024
    assert int(k.longitude // 30) == 5   # Ketu in Virgo
    assert r.speed < 0


def test_saturn_ingresses(settings):
    # Saturn entered sidereal Aquarius 17 Jan 2023 and Pisces 29 Mar 2025
    assert int(lon("Saturn", utc(2023, 1, 10), settings) // 30) == 9
    assert int(lon("Saturn", utc(2023, 1, 25), settings) // 30) == 10
    assert int(lon("Saturn", utc(2025, 3, 20), settings) // 30) == 10
    assert int(lon("Saturn", utc(2025, 4, 5), settings) // 30) == 11


def test_jupiter_taurus_2024(settings):
    assert int(lon("Jupiter", utc(2024, 4, 25), settings) // 30) == 0
    assert int(lon("Jupiter", utc(2024, 5, 5), settings) // 30) == 1


def test_swiss_ephemeris_files_in_use(settings):
    assert eph.body_position(eph.julian_day(utc(2000, 1, 1)), "Moon", settings).ephemeris == "Swiss Ephemeris"


def test_sunrise_kathmandu():
    # Sunrise in Kathmandu on 2024-06-21 is about 05:08 NPT (23:23 UTC previous day)
    jd = eph.sun_rise_set(eph.julian_day(utc(2024, 6, 20, 12)), 27.7172, 85.324, rise=True)
    t = eph.jd_to_datetime(jd)
    assert t.date().isoformat() == "2024-06-20"
    assert 23 * 60 + 5 <= t.hour * 60 + t.minute <= 23 * 60 + 35
