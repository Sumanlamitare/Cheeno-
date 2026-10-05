"""Sade Sati and Saturn's Dhaiya (Kantaka / Ashtama Shani).

Sade Sati is the period during which transiting Saturn moves through the
12th, 1st and 2nd signs from the natal Moon sign. Phases:
  first  - Saturn in the 12th from the Moon
  second - Saturn over the natal Moon sign (peak)
  third  - Saturn in the 2nd from the Moon
Brief retrograde exits during a cycle (gaps of less than about a year) are
treated as part of the same cycle; exact phase boundaries are reported.
"""

from __future__ import annotations

import datetime as dt

from ..astro import ephemeris as eph
from .chart import NatalChart
from .constants import RASHIS

MERGE_GAP_DAYS = 400


def _sign_spans(jd0: float, jd1: float, settings) -> list[tuple[float, float, int]]:
    events = eph.sign_ingresses("Saturn", jd0, jd1, settings, step=4.0)
    spans = []
    cur_sign = int(eph.sidereal_longitude(jd0, "Saturn", settings) // 30)
    cur_start = jd0
    for e in events:
        spans.append((cur_start, e["jd"], cur_sign))
        cur_sign, cur_start = e["toSign"], e["jd"]
    spans.append((cur_start, jd1, cur_sign))
    return spans


def _merge(spans, gap_days):
    merged = []
    for a, b, s in spans:
        if merged and a - merged[-1][1] <= gap_days:
            merged[-1] = (merged[-1][0], b, merged[-1][2] + [(a, b, s)])
        else:
            merged.append((a, b, [(a, b, s)]))
    return merged


def compute_sadesati(chart: NatalChart, now: dt.datetime, years_after: int = 100) -> dict:
    s = chart.settings
    moon = chart.planets["Moon"].sign
    jd0 = chart.jd - 3 * 365.25  # catch a cycle already running at birth
    jd1 = min(chart.jd + years_after * 365.25, eph.julian_day(dt.datetime(eph.MAX_YEAR, 1, 1)))
    spans = _sign_spans(jd0, jd1, s)
    jd_now = eph.julian_day(now)

    phase_of = {(moon - 1) % 12: 1, moon: 2, (moon + 1) % 12: 3}
    ss_spans = [sp for sp in spans if sp[2] in phase_of]
    cycles = []
    for a, b, parts in _merge(ss_spans, MERGE_GAP_DAYS):
        phases = {}
        for pa, pb, sign in parts:
            ph = phase_of[sign]
            if ph in phases:
                phases[ph] = (min(phases[ph][0], pa), max(phases[ph][1], pb))
            else:
                phases[ph] = (pa, pb)
        truncated_start = a <= jd0 + 1
        truncated_end = b >= jd1 - 1
        cycles.append({
            "start": eph.jd_to_datetime(a).isoformat(),
            "end": eph.jd_to_datetime(b).isoformat(),
            "startsBeforeRange": truncated_start,
            "endsAfterRange": truncated_end,
            "status": "current" if a <= jd_now < b else ("past" if b <= jd_now else "upcoming"),
            "phases": [
                {
                    "phase": ph,
                    "name": {1: "First phase (Rising)", 2: "Second phase (Peak)", 3: "Third phase (Setting)"}[ph],
                    "saturnSign": RASHIS[{1: (moon - 1) % 12, 2: moon, 3: (moon + 1) % 12}[ph]],
                    "start": eph.jd_to_datetime(pa).isoformat(),
                    "end": eph.jd_to_datetime(pb).isoformat(),
                    "status": "current" if pa <= jd_now < pb else ("past" if pb <= jd_now else "upcoming"),
                }
                for ph, (pa, pb) in sorted(phases.items())
            ],
            "_jd": (a, b),
        })
    # Drop cycles that ended before birth.
    cycles = [c for c in cycles if c["_jd"][1] > chart.jd]

    current_sign = int(eph.sidereal_longitude(jd_now, "Saturn", s) // 30)
    current_phase = phase_of.get(current_sign)
    active_cycle = next((c for c in cycles if c["status"] == "current"), None)
    if current_phase is None and active_cycle:
        # Saturn has briefly retrograded out of the three signs inside a cycle.
        status = "Active (Saturn temporarily outside the Sade Sati signs)"
    elif current_phase:
        status = {1: "First phase", 2: "Second / peak phase", 3: "Third phase"}[current_phase]
    else:
        status = "Not active"

    # Dhaiya / small panoti: Saturn in the 4th (Kantaka) or 8th (Ashtama) from Moon.
    dhaiya = []
    for target, name in (((moon + 3) % 12, "Kantaka Shani (4th from Moon)"),
                         ((moon + 7) % 12, "Ashtama Shani (8th from Moon)")):
        d_spans = [sp for sp in spans if sp[2] == target]
        for a, b, _ in _merge(d_spans, MERGE_GAP_DAYS):
            if b < jd_now - 365 or a > jd_now + 365.25 * 30:
                continue
            dhaiya.append({
                "name": name,
                "start": eph.jd_to_datetime(a).isoformat(),
                "end": eph.jd_to_datetime(b).isoformat(),
                "status": "current" if a <= jd_now < b else ("past" if b <= jd_now else "upcoming"),
            })
    dhaiya.sort(key=lambda x: x["start"])

    for c in cycles:
        c.pop("_jd", None)
    return {
        "moonSign": RASHIS[moon],
        "saturnSignNow": RASHIS[current_sign],
        "status": status,
        "active": active_cycle is not None,
        "currentPhase": current_phase,
        "currentCycle": active_cycle,
        "cycles": cycles,
        "dhaiya": dhaiya,
    }
