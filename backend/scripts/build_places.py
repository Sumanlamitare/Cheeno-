"""Regenerate kundali/inputs/data/cities.json.gz from the GeoNames data in the
`geonamescache` package (development-only dependency).

    pip install geonamescache==3.0.2 && python scripts/build_places.py

Keeping a compact extract (instead of the full package, ~180 MB installed)
keeps the deployment small enough for serverless platforms.
"""
import gzip
import json
import os
import unicodedata

import geonamescache


def is_latin(text):
    return all(ord(c) < 0x250 for c in text)


def main():
    gc = geonamescache.GeonamesCache()
    countries = {cc: c["name"] for cc, c in gc.get_countries().items()}
    us_states = {code: s["name"] for code, s in gc.get_us_states().items()}
    cities = []
    for c in gc.get_cities().values():
        alts = sorted({a for a in (c.get("alternatenames") or []) if a and is_latin(a) and len(a) <= 40 and a != c["name"]})
        cities.append([
            c["geonameid"], c["name"], c["countrycode"], c.get("admin1code", ""),
            round(float(c["latitude"]), 5), round(float(c["longitude"]), 5),
            c["timezone"], int(c.get("population") or 0), alts,
        ])
    cities.sort(key=lambda r: r[0])
    out = os.path.join(os.path.dirname(__file__), "..", "kundali", "inputs", "data", "cities.json.gz")
    with gzip.open(out, "wt", encoding="utf-8", compresslevel=9) as f:
        json.dump({"source": "GeoNames cities15000 (CC BY 4.0) via geonamescache 3.0.2",
                   "countries": countries, "usStates": us_states, "cities": cities}, f, ensure_ascii=False,
                  separators=(",", ":"))
    print(len(cities), "cities ->", os.path.getsize(out) // 1024, "KB")


if __name__ == "__main__":
    main()
