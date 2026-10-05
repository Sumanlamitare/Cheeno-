"""BS <-> AD conversion against published Nepali calendar anchors."""
import datetime as dt

import pytest

from kundali.inputs.calendar import CalendarError, ad_to_bs, bs_to_ad, resolve_date


@pytest.mark.parametrize("bs,ad", [
    ((2000, 1, 1), dt.date(1943, 4, 14)),   # BS 2000 Baisakh 1
    ((2080, 1, 1), dt.date(2023, 4, 14)),   # Nepali New Year 2080
    ((2081, 1, 1), dt.date(2024, 4, 13)),   # Nepali New Year 2081
    ((2082, 1, 1), dt.date(2025, 4, 14)),   # Nepali New Year 2082
    ((2057, 6, 19), dt.date(2000, 10, 5)),
    ((2080, 6, 19), dt.date(2023, 10, 6)),
])
def test_bs_to_ad_anchors(bs, ad):
    assert bs_to_ad(*bs).ad == ad


def test_ad_to_bs_roundtrip():
    d = dt.date(1990, 1, 1)
    for i in range(0, 18000, 37):  # BS table ends at 2100 BS (April 2044 AD)
        day = d + dt.timedelta(days=i)
        dual = ad_to_bs(day)
        assert bs_to_ad(dual.bs_year, dual.bs_month, dual.bs_day).ad == day


def test_ad_to_bs_label():
    dual = ad_to_bs(dt.date(2023, 4, 14))
    assert dual.bs_label == "2080 Baisakh 1 BS"


def test_ad_beyond_bs_table_is_none():
    assert ad_to_bs(dt.date(2044, 4, 19)) is None


def test_invalid_bs_day():
    with pytest.raises(CalendarError):
        bs_to_ad(2080, 1, 33)


def test_bs_out_of_range_refused():
    with pytest.raises(CalendarError):
        bs_to_ad(2150, 1, 1)
    with pytest.raises(CalendarError):
        bs_to_ad(1960, 1, 1)


def test_not_simplistic_offset():
    # Dates in the same AD year map to two different BS years around mid-April.
    assert bs_to_ad(2080, 12, 30).ad.year == 2024
    assert bs_to_ad(2081, 1, 1).ad.year == 2024


def test_resolve_ad_outside_bs_range_still_works():
    info = resolve_date("AD", "1900-05-01")
    assert info["display"]["bsAvailable"] is False


def test_invalid_ad():
    with pytest.raises(CalendarError):
        resolve_date("AD", "2023-02-30")
