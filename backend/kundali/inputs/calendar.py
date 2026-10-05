"""Bikram Sambat <-> Gregorian conversion.

Uses the `nepali-datetime` package, which ships the official month-length
tables of the Nepali calendar (BS 1975 - 2100). Conversions outside that
range are refused rather than guessed.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

import nepali_datetime as ndt

from ..jyotish.constants import BS_MONTHS, BS_MONTHS_DEVANAGARI

BS_MIN_YEAR = ndt.MINYEAR
BS_MAX_YEAR = ndt.MAXYEAR


class CalendarError(ValueError):
    pass


@dataclass(frozen=True)
class DualDate:
    ad: dt.date
    bs_year: int
    bs_month: int
    bs_day: int

    @property
    def bs_iso(self) -> str:
        return f"{self.bs_year:04d}-{self.bs_month:02d}-{self.bs_day:02d}"

    @property
    def bs_label(self) -> str:
        return f"{self.bs_year} {BS_MONTHS[self.bs_month - 1]} {self.bs_day} BS"

    @property
    def bs_label_devanagari(self) -> str:
        return f"{self.bs_year} {BS_MONTHS_DEVANAGARI[self.bs_month - 1]} {self.bs_day}"

    @property
    def ad_label(self) -> str:
        return f"{self.ad.strftime('%B')} {self.ad.day}, {self.ad.year} AD"

    def to_dict(self) -> dict:
        return {
            "ad": self.ad.isoformat(),
            "adLabel": self.ad_label,
            "bs": self.bs_iso,
            "bsLabel": self.bs_label,
            "bsLabelDevanagari": self.bs_label_devanagari,
            "bsAvailable": True,
        }


def _parse_iso(value: str) -> tuple[int, int, int]:
    parts = value.strip().replace("/", "-").split("-")
    if len(parts) != 3 or not all(p.strip().isdigit() for p in parts):
        raise CalendarError("Date must be in YYYY-MM-DD format.")
    return int(parts[0]), int(parts[1]), int(parts[2])


def bs_to_ad(year: int, month: int, day: int) -> DualDate:
    if not (BS_MIN_YEAR <= year <= BS_MAX_YEAR):
        raise CalendarError(
            f"Bikram Sambat year {year} is outside the supported range "
            f"({BS_MIN_YEAR}-{BS_MAX_YEAR} BS). Please enter the date in AD instead."
        )
    if not 1 <= month <= 12:
        raise CalendarError("Bikram Sambat month must be between 1 (Baisakh) and 12 (Chaitra).")
    try:
        nd = ndt.date(year, month, day)
    except (ValueError, OverflowError) as exc:
        raise CalendarError(
            f"{year} {BS_MONTHS[month - 1]} does not have a day {day}."
        ) from exc
    return DualDate(nd.to_datetime_date(), year, month, day)


def ad_to_bs(date: dt.date) -> DualDate | None:
    """Return the dual date, or None if the date is outside the BS table range."""
    try:
        nd = ndt.date.from_datetime_date(date)
    except (ValueError, OverflowError, IndexError):
        return None
    if not (BS_MIN_YEAR <= nd.year <= BS_MAX_YEAR):
        return None
    return DualDate(date, nd.year, nd.month, nd.day)


def resolve_date(calendar: str, value: str) -> dict:
    """Resolve a user-entered date into both calendars.

    Returns a dict with `ad` (datetime.date) and `display` (serialisable).
    """
    y, m, d = _parse_iso(value)
    cal = calendar.upper()
    if cal == "BS":
        dual = bs_to_ad(y, m, d)
        return {"ad": dual.ad, "display": dual.to_dict(), "inputCalendar": "BS"}
    if cal != "AD":
        raise CalendarError("Calendar must be AD or BS.")
    try:
        ad = dt.date(y, m, d)
    except ValueError as exc:
        raise CalendarError(f"{value} is not a valid Gregorian date.") from exc
    dual = ad_to_bs(ad)
    if dual is None:
        display = {
            "ad": ad.isoformat(),
            "adLabel": f"{ad.strftime('%B')} {ad.day}, {ad.year} AD",
            "bs": None,
            "bsLabel": None,
            "bsLabelDevanagari": None,
            "bsAvailable": False,
        }
    else:
        display = dual.to_dict()
    return {"ad": ad, "display": display, "inputCalendar": "AD"}
