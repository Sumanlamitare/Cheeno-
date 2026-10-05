"""Thin wrapper around the Swiss Ephemeris (pyswisseph).

All astronomy comes from the Swiss Ephemeris. This module never implements
planetary theory itself; it only selects flags, converts units and offers
small root-finding helpers built on top of Swiss Ephemeris positions.
"""

from __future__ import annotations

import datetime as dt
import os
import threading
from dataclasses import dataclass

import swisseph as swe

from ..config import CalculationSettings

EPHE_PATH = os.environ.get(
    "KUNDALI_EPHE_PATH",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ephe"),
)

# The Swiss Ephemeris keeps global state (sidereal mode, ephemeris path).
# Guard calculations with a lock so concurrent API requests stay consistent.
LOCK = threading.RLock()

_BODY = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
}

AYANAMSHA_MODES = {
    "lahiri": swe.SIDM_LAHIRI,
    "raman": swe.SIDM_RAMAN,
    "krishnamurti": swe.SIDM_KRISHNAMURTI,
}

AYANAMSHA_LABELS = {
    "lahiri": "Lahiri / Chitrapaksha",
    "raman": "B. V. Raman",
    "krishnamurti": "Krishnamurti (KP)",
}

MIN_YEAR = 1800
MAX_YEAR = 2399

swe.set_ephe_path(EPHE_PATH)


class EphemerisError(RuntimeError):
    pass


@dataclass(frozen=True)
class BodyPosition:
    name: str
    longitude: float  # sidereal ecliptic longitude, degrees [0, 360)
    latitude: float  # ecliptic latitude, degrees
    speed: float  # degrees per day in longitude
    declination: float  # degrees
    ephemeris: str  # "Swiss Ephemeris" or "Moshier"


def julian_day(utc: dt.datetime) -> float:
    if utc.tzinfo is not None:
        utc = utc.astimezone(dt.timezone.utc).replace(tzinfo=None)
    if not MIN_YEAR <= utc.year <= MAX_YEAR:
        raise EphemerisError(
            f"Dates between {MIN_YEAR} and {MAX_YEAR} are supported by the bundled ephemeris."
        )
    hour = utc.hour + utc.minute / 60 + (utc.second + utc.microsecond / 1e6) / 3600
    return swe.julday(utc.year, utc.month, utc.day, hour, swe.GREG_CAL)


def jd_to_datetime(jd: float) -> dt.datetime:
    y, m, d, h = swe.revjul(jd, swe.GREG_CAL)
    base = dt.datetime(y, m, d, tzinfo=dt.timezone.utc)
    return base + dt.timedelta(hours=h)


def _configure(settings: CalculationSettings) -> None:
    swe.set_sid_mode(AYANAMSHA_MODES[settings.ayanamsha], 0, 0)


def _flags() -> int:
    return swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED


def ayanamsha(jd: float, settings: CalculationSettings) -> float:
    with LOCK:
        _configure(settings)
        return swe.get_ayanamsa_ut(jd)


def body_position(jd: float, name: str, settings: CalculationSettings) -> BodyPosition:
    with LOCK:
        _configure(settings)
        if name in ("Rahu", "Ketu"):
            node = swe.TRUE_NODE if settings.node_type == "true" else swe.MEAN_NODE
            xx, ret = swe.calc_ut(jd, node, _flags())
            eq, _ = swe.calc_ut(jd, node, _flags() | swe.FLG_EQUATORIAL)
            lon, lat, speed, dec = xx[0], xx[1], xx[3], eq[1]
            if name == "Ketu":
                lon, lat, dec = (lon + 180.0) % 360.0, -lat, -dec
        else:
            xx, ret = swe.calc_ut(jd, _BODY[name], _flags())
            eq, _ = swe.calc_ut(jd, _BODY[name], _flags() | swe.FLG_EQUATORIAL)
            lon, lat, speed, dec = xx[0], xx[1], xx[3], eq[1]
        source = "Swiss Ephemeris" if ret & swe.FLG_SWIEPH else "Moshier"
        return BodyPosition(name, lon % 360.0, lat, speed, dec, source)


def sidereal_longitude(jd: float, name: str, settings: CalculationSettings) -> float:
    return body_position(jd, name, settings).longitude


def angles(jd: float, lat: float, lon: float, settings: CalculationSettings) -> dict:
    """Sidereal ascendant and midheaven (MC)."""
    with LOCK:
        _configure(settings)
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b"W", swe.FLG_SIDEREAL)
        return {"ascendant": ascmc[0] % 360.0, "mc": ascmc[1] % 360.0, "armc": ascmc[2]}


def sun_rise_set(jd_start: float, lat: float, lon: float, rise: bool) -> float | None:
    """Next sunrise/sunset after jd_start (Hindu rising: centre of the disc,
    without refraction). Returns None at polar latitudes when there is none."""
    flag = (swe.CALC_RISE if rise else swe.CALC_SET) | swe.BIT_HINDU_RISING
    with LOCK:
        try:
            res, tret = swe.rise_trans(jd_start, swe.SUN, flag, (lon, lat, 0.0), 0.0, 0.0, swe.FLG_SWIEPH)
        except swe.Error:
            return None
    if res != 0:
        return None
    return tret[0]


def equation_of_time(jd: float) -> float:
    """Equation of time in days (apparent - mean solar time)."""
    with LOCK:
        return swe.time_equ(jd)


def find_crossing(func, target: float, jd_lo: float, jd_hi: float, tol_days: float = 1e-5) -> float:
    """Bisection for the time where an angular function crosses `target`.

    `func(jd)` must return degrees; the angular difference to the target is
    assumed to change sign exactly once inside [jd_lo, jd_hi].
    """

    def diff(jd):
        return (func(jd) - target + 180.0) % 360.0 - 180.0

    d_lo = diff(jd_lo)
    for _ in range(80):
        mid = (jd_lo + jd_hi) / 2
        d_mid = diff(mid)
        if (d_lo < 0) == (d_mid < 0):
            jd_lo, d_lo = mid, d_mid
        else:
            jd_hi = mid
        if jd_hi - jd_lo < tol_days:
            break
    return (jd_lo + jd_hi) / 2


def sign_ingresses(name: str, jd_start: float, jd_end: float, settings: CalculationSettings,
                   step: float | None = None) -> list[dict]:
    """All sidereal sign changes of a body between two dates, including
    retrograde re-entries. Returns [{jd, fromSign, toSign}] in time order."""
    if step is None:
        step = {"Moon": 0.5, "Sun": 2.0, "Mercury": 1.0, "Venus": 1.0, "Mars": 2.0}.get(name, 4.0)
    events = []
    prev_jd = jd_start
    prev_sign = int(sidereal_longitude(prev_jd, name, settings) // 30)
    jd = jd_start
    while jd < jd_end:
        jd = min(jd + step, jd_end)
        sign = int(sidereal_longitude(jd, name, settings) // 30)
        if sign != prev_sign:
            forward = (sign - prev_sign) % 12 == 1
            boundary = (sign * 30.0) if forward else (prev_sign * 30.0)
            t = find_crossing(lambda x: sidereal_longitude(x, name, settings), boundary, prev_jd, jd)
            events.append({"jd": t, "fromSign": prev_sign, "toSign": sign})
        prev_jd, prev_sign = jd, sign
    return events


def heliocentric_longitude(jd: float, name: str, settings: CalculationSettings) -> float:
    """Sidereal heliocentric longitude (used as Seeghrocha / mean planet in
    the Chesta Kendra method of Shadbala)."""
    with LOCK:
        _configure(settings)
        xx, _ = swe.calc_ut(jd, _BODY[name], swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_HELCTR)
        return xx[0] % 360.0


def mean_sun_longitude(jd: float, settings: CalculationSettings) -> float:
    """Sidereal mean longitude of the Sun (standard polynomial, Meeus 25.2)."""
    t = (jd - 2451545.0) / 36525.0
    tropical = (280.46646 + 36000.76983 * t + 0.0003032 * t * t) % 360.0
    return (tropical - ayanamsha(jd, settings)) % 360.0
