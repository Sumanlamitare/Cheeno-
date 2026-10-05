"""Natal chart model: converts ephemeris output into Jyotish placements."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

from ..astro import ephemeris as eph
from ..config import CalculationSettings
from . import vargas
from .constants import (
    NAKSHATRAS,
    PLANET_INFO,
    PLANETS,
    RASHI_LORDS,
    RASHIS,
    format_dms,
    house_from,
    nakshatra_lord,
)
from .dignity import combustion, mercury_is_benefic, moon_is_benefic, sign_dignity, varga_dignity
from .drishti import aspect_type


def nakshatra_of(lon: float) -> tuple[int, int]:
    # Work in arc-seconds rounded to 1e-6" so exact boundaries (e.g. 120°) are
    # not misplaced by binary floating point. 13°20' = 48000", 3°20' = 12000".
    arcsec = round((lon % 360.0) * 3600.0, 6)
    idx = int(arcsec // 48000) % 27
    pada = int((arcsec % 48000) // 12000) + 1
    return idx, min(pada, 4)


@dataclass
class Placement:
    name: str
    longitude: float
    latitude: float = 0.0
    speed: float = 0.0
    declination: float = 0.0
    sign: int = 0
    degree: float = 0.0
    nakshatra: int = 0
    pada: int = 1
    house: int = 1
    retrograde: bool = False
    combust: bool = False
    sun_distance: float = 0.0
    dignity: str = "neutral"
    benefic: bool = False
    vargas: dict = field(default_factory=dict)

    @property
    def sign_name(self) -> str:
        return RASHIS[self.sign]

    @property
    def nakshatra_name(self) -> str:
        return NAKSHATRAS[self.nakshatra]

    @property
    def nakshatra_lord(self) -> str:
        return nakshatra_lord(self.nakshatra)

    def to_dict(self) -> dict:
        out = {
            "name": self.name,
            "sanskrit": PLANET_INFO.get(self.name, {}).get("sanskrit", self.name),
            "abbr": PLANET_INFO.get(self.name, {}).get("abbr", self.name[:2]),
            "longitude": round(self.longitude, 6),
            "sign": self.sign,
            "signName": self.sign_name,
            "degree": round(self.degree, 6),
            "degreeLabel": format_dms(self.degree),
            "nakshatra": self.nakshatra,
            "nakshatraName": self.nakshatra_name,
            "nakshatraLord": self.nakshatra_lord,
            "pada": self.pada,
            "house": self.house,
            "retrograde": self.retrograde,
            "motion": "Retrograde" if self.retrograde else "Direct",
            "speed": round(self.speed, 6),
            "combust": self.combust,
            "sunDistance": round(self.sun_distance, 3),
            "dignity": self.dignity,
            "benefic": self.benefic,
            "declination": round(self.declination, 4),
            "vargas": self.vargas,
        }
        return out


@dataclass
class NatalChart:
    utc: dt.datetime
    jd: float
    latitude: float
    longitude: float
    settings: CalculationSettings
    ayanamsha: float
    ascendant: Placement
    mc: float
    planets: dict[str, Placement]
    ephemeris_source: str

    # ---- convenience accessors used throughout the engine -----------------
    @property
    def lagna_sign(self) -> int:
        return self.ascendant.sign

    def house_sign(self, house: int) -> int:
        return (self.lagna_sign + house - 1) % 12

    def house_lord(self, house: int) -> str:
        return RASHI_LORDS[self.house_sign(house)]

    def houses_ruled_by(self, planet: str) -> list[int]:
        return [h for h in range(1, 13) if self.house_lord(h) == planet]

    def occupants(self, house: int) -> list[str]:
        return [p for p in PLANETS if self.planets[p].house == house]

    def occupants_of_sign(self, sign: int) -> list[str]:
        return [p for p in PLANETS if self.planets[p].sign == sign]

    def planet_signs(self) -> dict[str, int]:
        return {p: pl.sign for p, pl in self.planets.items()}

    def aspects_on_house(self, house: int) -> list[dict]:
        target = self.house_sign(house)
        out = []
        for p in PLANETS:
            pl = self.planets[p]
            h = aspect_type(p, pl.sign, target)
            if h is not None:
                out.append({"planet": p, "aspect": h})
        return out

    def aspects_on_planet(self, planet: str) -> list[dict]:
        target = self.planets[planet].sign
        out = []
        for p in PLANETS:
            if p == planet:
                continue
            pl = self.planets[p]
            h = aspect_type(p, pl.sign, target)
            if h is not None:
                out.append({"planet": p, "aspect": h})
        return out

    def is_aspected_by(self, planet: str, by: str) -> bool:
        return any(a["planet"] == by for a in self.aspects_on_planet(planet))

    def house_of(self, planet: str) -> int:
        return self.planets[planet].house

    def house_from_moon(self, planet: str) -> int:
        return house_from(self.planets["Moon"].sign, self.planets[planet].sign)

    def varga_sign(self, planet: str, division: int) -> int:
        if planet == "Lagna":
            return self.ascendant.vargas[str(division)]["sign"]
        return self.planets[planet].vargas[str(division)]["sign"]


def _placement(name: str, lon: float, lagna_sign: int) -> Placement:
    sign = int(lon // 30) % 12
    nak, pada = nakshatra_of(lon)
    return Placement(
        name=name,
        longitude=lon,
        sign=sign,
        degree=lon % 30,
        nakshatra=nak,
        pada=pada,
        house=house_from(lagna_sign, sign),
    )


def build_chart(utc: dt.datetime, latitude: float, longitude: float,
                settings: CalculationSettings) -> NatalChart:
    jd = eph.julian_day(utc)
    ang = eph.angles(jd, latitude, longitude, settings)
    asc_lon = ang["ascendant"]
    lagna_sign = int(asc_lon // 30)
    asc = _placement("Lagna", asc_lon, lagna_sign)

    positions = {p: eph.body_position(jd, p, settings) for p in PLANETS}
    planets: dict[str, Placement] = {}
    for p, pos in positions.items():
        pl = _placement(p, pos.longitude, lagna_sign)
        pl.latitude = pos.latitude
        pl.speed = pos.speed
        pl.declination = pos.declination
        # The nodes always move retrograde in mean motion; true node may wobble.
        pl.retrograde = pos.speed < 0 if p not in ("Rahu", "Ketu") else True
        planets[p] = pl

    sun_lon = planets["Sun"].longitude
    signs = {p: pl.sign for p, pl in planets.items()}
    for p, pl in planets.items():
        pl.combust, pl.sun_distance = combustion(p, pl.longitude, sun_lon, pl.retrograde)
        pl.dignity = sign_dignity(p, pl.longitude, signs)
        if p in ("Jupiter", "Venus"):
            pl.benefic = True
        elif p == "Moon":
            pl.benefic = moon_is_benefic(pl.longitude, sun_lon)
        elif p == "Mercury":
            pl.benefic = mercury_is_benefic(pl.sign, signs)
        else:
            pl.benefic = False

    # Divisional charts
    for division in vargas.SUPPORTED_VARGAS:
        v_signs = {p: vargas.varga_sign(pl.longitude, division) for p, pl in planets.items()}
        v_lagna = vargas.varga_sign(asc_lon, division)
        asc.vargas[str(division)] = {"sign": v_lagna, "signName": RASHIS[v_lagna]}
        for p, pl in planets.items():
            vs = v_signs[p]
            pl.vargas[str(division)] = {
                "sign": vs,
                "signName": RASHIS[vs],
                "house": house_from(v_lagna, vs),
                "dignity": varga_dignity(p, vs, v_signs),
            }

    sources = {pos.ephemeris for pos in positions.values()}
    return NatalChart(
        utc=utc,
        jd=jd,
        latitude=latitude,
        longitude=longitude,
        settings=settings,
        ayanamsha=eph.ayanamsha(jd, settings),
        ascendant=asc,
        mc=ang["mc"],
        planets=planets,
        ephemeris_source="Swiss Ephemeris" if sources == {"Swiss Ephemeris"} else "Moshier (fallback)",
    )
