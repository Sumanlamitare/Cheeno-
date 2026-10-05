"""Offline birthplace resolution.

Sources
-------
* GeoNames "cities15000" data (~34,000 cities worldwide with coordinates and
  IANA timezone), stored as a compact extract in data/cities.json.gz
  (regenerate with scripts/build_places.py).
* A supplementary list of Nepal district headquarters and towns that are below
  the GeoNames population threshold (approximate town-centre coordinates).
* `timezonefinder` for resolving the IANA timezone of manually entered
  coordinates.

No network calls are made at runtime.
"""

from __future__ import annotations

import gzip
import json
import math
import os
import unicodedata
from dataclasses import dataclass
from functools import lru_cache

from timezonefinder import TimezoneFinder


class PlaceError(ValueError):
    pass


# (name, latitude, longitude) - Nepal district headquarters / towns not present
# in the GeoNames 15k dataset. Coordinates are approximate town centres.
NEPAL_SUPPLEMENT = [
    ("Bhaktapur", 27.6710, 85.4298),
    ("Gorkha", 28.0000, 84.6300),
    ("Besisahar", 28.2330, 84.3770),
    ("Jomsom", 28.7800, 83.7300),
    ("Beni", 28.3500, 83.5650),
    ("Kusma", 28.2230, 83.6880),
    ("Putalibazar", 28.1000, 83.8700),
    ("Damauli", 27.9800, 84.2670),
    ("Dhading Besi", 27.9070, 84.9000),
    ("Bidur", 27.9000, 85.1500),
    ("Dhunche", 28.1100, 85.3000),
    ("Chautara", 27.7800, 85.7100),
    ("Charikot", 27.6680, 86.0300),
    ("Manthali", 27.3950, 86.0590),
    ("Sindhuli Madhi", 27.2050, 85.9100),
    ("Okhaldhunga", 27.3160, 86.5040),
    ("Salleri", 27.5040, 86.5840),
    ("Diktel", 27.2130, 86.7960),
    ("Bhojpur", 27.1720, 87.0500),
    ("Taplejung", 27.3510, 87.6690),
    ("Phidim", 27.1500, 87.7600),
    ("Myanglung", 27.1300, 87.4300),
    ("Kalaiya", 27.0330, 85.0000),
    ("Tamghas", 28.0700, 83.2500),
    ("Sandhikharka", 27.9700, 83.1200),
    ("Taulihawa", 27.5500, 83.0500),
    ("Parasi", 27.5300, 83.6700),
    ("Ghorahi", 28.0400, 82.4900),
    ("Libang", 28.3000, 82.6300),
    ("Musikot", 28.6300, 82.4800),
    ("Salyan Khalanga", 28.3800, 82.1700),
    ("Pyuthan Khalanga", 28.1000, 82.8500),
    ("Jajarkot Khalanga", 28.7000, 82.2000),
    ("Jumla", 29.2750, 82.1830),
    ("Manma", 29.1400, 81.6200),
    ("Gamgadhi", 29.5500, 82.1500),
    ("Dunai", 28.9300, 82.9000),
    ("Simikot", 29.9700, 81.8300),
    ("Martadi", 29.4500, 81.4700),
    ("Chainpur (Bajhang)", 29.5500, 81.2000),
    ("Mangalsen", 29.1500, 81.2900),
    ("Silgadhi", 29.2700, 80.9800),
    ("Baitadi", 29.5300, 80.4700),
    ("Chame", 28.5500, 84.2400),
    ("Gaighat", 26.7900, 86.7000),
    ("Lumbini", 27.4840, 83.2760),
    ("Namche Bazaar", 27.8050, 86.7140),
]


def _norm(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return " ".join(stripped.lower().replace("-", " ").replace("'", "").split())


@dataclass(frozen=True)
class Place:
    id: str
    name: str
    country: str
    country_code: str
    region: str | None
    latitude: float
    longitude: float
    timezone: str
    population: int
    source: str

    @property
    def label(self) -> str:
        parts = [self.name]
        if self.region:
            parts.append(self.region)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "label": self.label,
            "country": self.country,
            "countryCode": self.country_code,
            "region": self.region,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone,
            "population": self.population,
            "source": self.source,
        }


def _haversine_km(a_lat, a_lon, b_lat, b_lon) -> float:
    r = 6371.0
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dphi = p2 - p1
    dl = math.radians(b_lon - a_lon)
    h = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


class PlaceIndex:
    def __init__(self) -> None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "cities.json.gz")
        with gzip.open(path, "rt", encoding="utf-8") as f:
            data = json.load(f)
        us_states = data["usStates"]
        self.country_names = data["countries"]
        self.places: dict[str, Place] = {}
        self._tokens: dict[str, list[tuple[str, str]]] = {}

        for gid, raw_name, cc, admin1, lat, lon, tz, pop, alts in data["cities"]:
            region = us_states.get(admin1) if cc == "US" else None
            name = raw_name
            if cc == "NP":
                # GeoNames uses IAST-like diacritics for Nepal; show plain names.
                name = unicodedata.normalize("NFKD", name)
                name = "".join(c for c in name if not unicodedata.combining(c))
            place = Place(
                id=f"gn-{gid}",
                name=name,
                country=self.country_names.get(cc, cc),
                country_code=cc,
                region=region,
                latitude=float(lat),
                longitude=float(lon),
                timezone=tz,
                population=int(pop),
                source="GeoNames",
            )
            variants = {_norm(raw_name)} | {_norm(a) for a in alts}
            self._add(place, variants)

        nepal_existing = [p for p in self.places.values() if p.country_code == "NP"]
        for i, (name, lat, lon) in enumerate(NEPAL_SUPPLEMENT):
            if any(_haversine_km(lat, lon, p.latitude, p.longitude) < 4 for p in nepal_existing):
                continue
            place = Place(
                id=f"np-{i}",
                name=name,
                country="Nepal",
                country_code="NP",
                region=None,
                latitude=lat,
                longitude=lon,
                timezone="Asia/Kathmandu",
                population=0,
                source="Nepal supplement (approximate town centre)",
            )
            self._add(place, {_norm(name)})

    def _add(self, place: Place, variants: set[str]) -> None:
        self.places[place.id] = place
        for v in variants:
            if len(v) >= 2:
                self._tokens.setdefault(v[:2], []).append((v, place.id))

    def search(self, query: str, limit: int = 10) -> list[Place]:
        q = query.strip()
        country_filter = None
        if "," in q:
            q, _, rest = q.partition(",")
            country_filter = _norm(rest.split(",")[-1]) or None
        nq = _norm(q)
        if len(nq) < 2:
            return []
        scored: dict[str, tuple] = {}
        for variant, pid in self._tokens.get(nq[:2], []):
            if not variant.startswith(nq):
                continue
            place = self.places[pid]
            if country_filter:
                cname = _norm(place.country)
                region = _norm(place.region or "")
                if not (cname.startswith(country_filter) or region.startswith(country_filter)
                        or place.country_code.lower() == country_filter):
                    continue
            exact = variant == nq
            primary = _norm(place.name) == variant
            key = (0 if primary else 1, 0 if exact else 1, -place.population, place.name)
            if pid not in scored or key < scored[pid]:
                scored[pid] = key
        ranked = sorted(scored.items(), key=lambda kv: kv[1])
        return [self.places[pid] for pid, _ in ranked[:limit]]

    def get(self, place_id: str) -> Place:
        try:
            return self.places[place_id]
        except KeyError as exc:
            raise PlaceError("Please select a specific city or location.") from exc


@lru_cache(maxsize=1)
def get_index() -> PlaceIndex:
    return PlaceIndex()


@lru_cache(maxsize=1)
def _tf() -> TimezoneFinder:
    return TimezoneFinder()


def place_from_coordinates(lat: float, lon: float, label: str | None = None) -> Place:
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise PlaceError("Latitude must be between -90 and 90 and longitude between -180 and 180.")
    if abs(lat) > 66.5:
        # Whole-sign houses still work, but sunrise-based Panchanga may not.
        pass
    tz = _tf().timezone_at(lng=lon, lat=lat)
    if not tz:
        raise PlaceError(
            "Historical timezone information could not be established for these coordinates. "
            "Please choose a nearby city or enter a UTC offset manually."
        )
    return Place(
        id=f"coord-{lat:.4f},{lon:.4f}",
        name=label or f"{abs(lat):.4f}°{'N' if lat >= 0 else 'S'}, {abs(lon):.4f}°{'E' if lon >= 0 else 'W'}",
        country="",
        country_code="",
        region=None,
        latitude=lat,
        longitude=lon,
        timezone=tz,
        population=0,
        source="Manual coordinates",
    )
