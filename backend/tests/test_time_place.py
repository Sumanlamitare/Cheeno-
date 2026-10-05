"""Time parsing, historical timezones and place resolution."""
import datetime as dt

import pytest

from kundali.inputs.places import PlaceError, get_index, place_from_coordinates
from kundali.inputs.timeutil import TimeInputError, localize, parse_time


def test_parse_24h_and_ampm():
    assert parse_time("14:05") == dt.time(14, 5)
    assert parse_time("14:05:09") == dt.time(14, 5, 9)
    assert parse_time("2:05", "PM") == dt.time(14, 5)
    assert parse_time("12:00", "AM") == dt.time(0, 0)
    assert parse_time("12:30", "PM") == dt.time(12, 30)


@pytest.mark.parametrize("bad", ["", "24:00", "10:60", "abc", "10"])
def test_parse_invalid(bad):
    with pytest.raises(TimeInputError):
        parse_time(bad)


def test_ampm_hour_range():
    with pytest.raises(TimeInputError):
        parse_time("13:00", "PM")


@pytest.mark.parametrize("zone,date,offset,dst", [
    ("Asia/Kathmandu", dt.date(1985, 6, 1), 5.5, False),     # before 1986: +05:30
    ("Asia/Kathmandu", dt.date(1990, 6, 1), 5.75, False),    # after 1986: +05:45
    ("America/New_York", dt.date(2000, 7, 1), -4.0, True),
    ("America/New_York", dt.date(2000, 1, 15), -5.0, False),
    ("Australia/Sydney", dt.date(2000, 1, 15), 11.0, True),
    ("Australia/Sydney", dt.date(2000, 7, 15), 10.0, False),
    ("Asia/Kolkata", dt.date(1943, 6, 1), 6.5, True),        # wartime IST+1
    ("Europe/London", dt.date(1990, 7, 1), 1.0, True),
])
def test_historical_offsets(zone, date, offset, dst):
    r = localize(date, dt.time(12, 0), zone, 0.0)
    assert r["offsetHours"] == pytest.approx(offset)
    assert r["dst"] == dst
    assert r["utc"] == (dt.datetime.combine(date, dt.time(12)) - dt.timedelta(hours=offset)).replace(tzinfo=dt.timezone.utc)


def test_lmt_used_before_standard_time():
    r = localize(dt.date(1915, 1, 1), dt.time(12), "Asia/Kathmandu", 85.32)
    assert r["method"] == "local-mean-time"
    assert r["offsetHours"] == pytest.approx(85.32 / 15)
    assert r["warnings"]


def test_nonexistent_dst_time_warns():
    r = localize(dt.date(2021, 3, 14), dt.time(2, 30), "America/New_York", -74)
    assert any("does not exist" in w for w in r["warnings"])


def test_ambiguous_dst_time_warns():
    r = localize(dt.date(2021, 11, 7), dt.time(1, 30), "America/New_York", -74)
    assert any("occurred twice" in w for w in r["warnings"])


def test_manual_offset():
    r = localize(dt.date(2000, 1, 1), dt.time(12), None, 0, utc_offset_override=5.75)
    assert r["utc"].hour == 6 and r["utc"].minute == 15


def test_place_search_and_coordinates():
    ix = get_index()
    ktm = ix.search("Kathmandu")[0]
    assert ktm.country == "Nepal" and ktm.timezone == "Asia/Kathmandu"
    assert ktm.latitude == pytest.approx(27.70, abs=0.05) and ktm.longitude == pytest.approx(85.32, abs=0.05)
    ny = ix.search("New York")[0]
    assert ny.timezone == "America/New_York"
    syd = ix.search("Sydney, Australia")[0]
    assert syd.timezone == "Australia/Sydney"


def test_unknown_place_id():
    with pytest.raises(PlaceError):
        get_index().get("gn-does-not-exist")


def test_coordinates_timezone():
    assert place_from_coordinates(27.7, 85.3).timezone == "Asia/Kathmandu"
    assert place_from_coordinates(-33.87, 151.21).timezone == "Australia/Sydney"
    with pytest.raises(PlaceError):
        place_from_coordinates(100, 0)
