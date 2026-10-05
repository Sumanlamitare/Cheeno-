"""Vimshottari Dasha (BPHS ch. 46).

The starting Mahadasha is ruled by the lord of the Moon's natal nakshatra.
The balance at birth is the unelapsed fraction of that nakshatra multiplied
by the Mahadasha length. Sub-periods (Antardasha, Pratyantardasha) are
proportional: sub = parent * years(sub-lord) / 120, beginning with the
parent's own lord and continuing in Vimshottari order.
"""

from __future__ import annotations

import datetime as dt

from .constants import DASHA_ORDER, DASHA_YEARS, NAKSHATRA_SPAN, VIMSHOTTARI_TOTAL


def _sequence_from(lord: str) -> list[str]:
    i = DASHA_ORDER.index(lord)
    return DASHA_ORDER[i:] + DASHA_ORDER[:i]


def _period(lord, start, end, level, children=None):
    return {
        "lord": lord,
        "start": start,
        "end": end,
        "level": level,
        "children": children or [],
    }


def vimshottari(moon_longitude: float, birth_utc: dt.datetime, year_days: float = 365.25,
                levels: int = 3, cycles: int = 1) -> dict:
    nak = int(moon_longitude // NAKSHATRA_SPAN) % 27
    lord = DASHA_ORDER[nak % 9]
    traversed = (moon_longitude % NAKSHATRA_SPAN) / NAKSHATRA_SPAN
    md_years = DASHA_YEARS[lord]
    balance_years = (1 - traversed) * md_years
    year = dt.timedelta(days=year_days)
    # Notional start of the first mahadasha (before birth).
    first_start = birth_utc - year * (traversed * md_years)

    mahadashas = []
    start = first_start
    for c in range(cycles):
        for md_lord in _sequence_from(lord):
            length = year * DASHA_YEARS[md_lord]
            end = start + length
            md = _period(md_lord, start, end, 1)
            if levels >= 2:
                md["children"] = _subperiods(md_lord, start, length, 2, levels)
            mahadashas.append(md)
            start = end
    return {
        "startingLord": lord,
        "nakshatraIndex": nak,
        "traversedFraction": traversed,
        "balanceYears": balance_years,
        "balance": _ymd(balance_years, year_days),
        "periods": mahadashas,
        "yearDays": year_days,
    }


def _subperiods(parent_lord: str, start: dt.datetime, length: dt.timedelta, level: int, max_level: int):
    out = []
    cur = start
    for sub in _sequence_from(parent_lord):
        sub_len = length * (DASHA_YEARS[sub] / VIMSHOTTARI_TOTAL)
        end = cur + sub_len
        p = _period(sub, cur, end, level)
        if level < max_level:
            p["children"] = _subperiods(sub, cur, sub_len, level + 1, max_level)
        out.append(p)
        cur = end
    return out


def _ymd(years: float, year_days: float) -> dict:
    y = int(years)
    rem_days = (years - y) * year_days
    m = int(rem_days // (year_days / 12))
    d = int(round(rem_days - m * (year_days / 12)))
    if d >= 30:
        m, d = m + 1, 0
    if m >= 12:
        y, m = y + 1, 0
    return {"years": y, "months": m, "days": d}


def find_active(periods: list[dict], moment: dt.datetime) -> list[dict]:
    """Return the chain [mahadasha, antardasha, pratyantardasha] active at a moment."""
    chain = []
    level = periods
    while level:
        hit = next((p for p in level if p["start"] <= moment < p["end"]), None)
        if hit is None:
            break
        chain.append(hit)
        level = hit["children"]
    return chain


def serialize(periods: list[dict], now: dt.datetime, birth: dt.datetime, year_days: float = 365.25) -> list[dict]:
    out = []
    for p in periods:
        status = "current" if p["start"] <= now < p["end"] else ("past" if p["end"] <= now else "upcoming")
        item = {
            "lord": p["lord"],
            "start": p["start"].isoformat(),
            "end": p["end"].isoformat(),
            "durationYears": round((p["end"] - p["start"]).total_seconds() / 86400 / year_days, 4),
            "status": status,
            "level": p["level"],
            "beforeBirth": p["start"] < birth,
        }
        if p["children"]:
            item["children"] = serialize(p["children"], now, birth, year_days)
        out.append(item)
    return out
