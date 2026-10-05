"""Birth time parsing and historical timezone resolution.

Historical UTC offsets come from the IANA tz database (via `zoneinfo` and the
`tzdata` package). When the database only knows Local Mean Time for a zone
(births before a region adopted standard time), the LMT of the actual
birthplace longitude is used, because the tz database's LMT belongs to the
zone's reference city, not to the birthplace.
"""

from __future__ import annotations

import datetime as dt
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

UTC = dt.timezone.utc

# Before 1906 the tz database assigns South Asian zones the mean time of a
# reference city (Howrah, Madras, ...), but birth times were recorded in the
# local time of the birthplace. For these zones the birthplace LMT is used.
SOUTH_ASIA_LOCAL_TIME_ZONES = {
    "Asia/Kolkata", "Asia/Calcutta", "Asia/Karachi", "Asia/Dhaka", "Asia/Colombo",
    "Asia/Kathmandu", "Asia/Katmandu", "Asia/Thimphu",
}


class TimeInputError(ValueError):
    pass


_TIME_RE = re.compile(r"^\s*(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?\s*$")


def parse_time(value: str, meridiem: str | None = None) -> dt.time:
    """Parse HH:MM[:SS]. If meridiem ('AM'/'PM') is given, HH is 1-12."""
    if not value:
        raise TimeInputError("An exact birth time is required for an accurate Lagna and house calculation.")
    m = _TIME_RE.match(value)
    if not m:
        raise TimeInputError("Birth time must be entered as HH:MM or HH:MM:SS.")
    h, mi = int(m.group(1)), int(m.group(2))
    s = int(m.group(3)) if m.group(3) else 0
    if mi > 59 or s > 59:
        raise TimeInputError("Minutes and seconds must be between 00 and 59.")
    if meridiem:
        mer = meridiem.upper()
        if mer not in ("AM", "PM"):
            raise TimeInputError("AM/PM indicator must be AM or PM.")
        if not 1 <= h <= 12:
            raise TimeInputError("With AM/PM, the hour must be between 1 and 12.")
        if mer == "AM":
            h = 0 if h == 12 else h
        else:
            h = 12 if h == 12 else h + 12
    elif h > 23:
        raise TimeInputError("Hour must be between 00 and 23 in 24-hour format.")
    return dt.time(h, mi, s)


def _fmt_offset(hours: float) -> str:
    sign = "+" if hours >= 0 else "-"
    total = round(abs(hours) * 3600)
    hh, rem = divmod(total, 3600)
    mm, ss = divmod(rem, 60)
    out = f"UTC{sign}{hh:02d}:{mm:02d}"
    if ss:
        out += f":{ss:02d}"
    return out


def localize(
    date: dt.date,
    time: dt.time,
    tz_name: str | None,
    longitude: float,
    utc_offset_override: float | None = None,
) -> dict:
    """Convert a civil birth date/time at a place into UTC.

    Returns a dict containing the UTC datetime and a transparent description
    of how the offset was established, plus any warnings.
    """
    naive = dt.datetime.combine(date, time)
    warnings: list[str] = []

    if utc_offset_override is not None:
        if not -14 <= utc_offset_override <= 14:
            raise TimeInputError("UTC offset override must be between -14 and +14 hours.")
        offset = dt.timedelta(hours=utc_offset_override)
        utc = (naive - offset).replace(tzinfo=UTC)
        return {
            "utc": utc,
            "local": naive,
            "offsetHours": utc_offset_override,
            "offsetLabel": _fmt_offset(utc_offset_override),
            "tzName": tz_name or "Manual offset",
            "abbreviation": None,
            "dst": None,
            "method": "manual",
            "warnings": ["UTC offset was entered manually; historical timezone rules were not applied."],
        }

    if not tz_name:
        raise TimeInputError("Historical timezone information could not be established for this place.")
    try:
        zone = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError as exc:
        raise TimeInputError(f"Unknown timezone '{tz_name}'.") from exc

    first = naive.replace(tzinfo=zone, fold=0)
    second = naive.replace(tzinfo=zone, fold=1)
    abbr = first.tzname()

    offset0 = first.utcoffset() or dt.timedelta(0)
    non_quarter_hour = offset0.total_seconds() % 900 != 0
    use_lmt = abbr == "LMT" or (
        tz_name in SOUTH_ASIA_LOCAL_TIME_ZONES and date.year < 1906 and non_quarter_hour
    )
    if use_lmt:
        lmt_hours = longitude / 15.0
        offset = dt.timedelta(hours=lmt_hours)
        utc = (naive - offset).replace(tzinfo=UTC)
        warnings.append(
            "No standard time existed at this place on the birth date. Local Mean Time "
            f"of the birthplace longitude ({_fmt_offset(lmt_hours)}) has been used. "
            "Please confirm that the recorded birth time was local (solar) time."
        )
        return {
            "utc": utc,
            "local": naive,
            "offsetHours": lmt_hours,
            "offsetLabel": _fmt_offset(lmt_hours),
            "tzName": tz_name,
            "abbreviation": "LMT",
            "dst": False,
            "method": "local-mean-time",
            "warnings": warnings,
        }

    # Detect non-existent local times (spring-forward gap).
    roundtrip = first.astimezone(UTC).astimezone(zone).replace(tzinfo=None)
    if roundtrip != naive:
        warnings.append(
            "The entered local time does not exist on this date because clocks were moved "
            "forward (daylight saving transition). The pre-transition offset has been applied; "
            "please verify the birth time."
        )
    elif first.utcoffset() != second.utcoffset():
        warnings.append(
            "The entered local time occurred twice on this date because clocks were moved back "
            "(daylight saving transition). The first occurrence (daylight time) has been used."
        )

    offset = first.utcoffset() or dt.timedelta(0)
    dst = bool(first.dst()) if first.dst() is not None else False
    utc = first.astimezone(UTC)
    hours = offset.total_seconds() / 3600.0
    if date.year < 1900:
        warnings.append(
            "Historical timezone records before 1900 may be incomplete for many regions."
        )
    return {
        "utc": utc,
        "local": naive,
        "offsetHours": hours,
        "offsetLabel": _fmt_offset(hours),
        "tzName": tz_name,
        "abbreviation": abbr,
        "dst": dst,
        "method": "tz-database",
        "warnings": warnings,
    }
