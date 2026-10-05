"""Divisional charts (Shodasavarga) according to Parashara (BPHS ch. 6).

Each function maps a sidereal longitude to the sign index (0 = Aries) it
occupies in the divisional chart. All sixteen Parashari vargas are
implemented and individually unit-tested; the UI exposes D1, D9 and D10 by
default and the rest under "Advanced".
"""

from __future__ import annotations

from .constants import is_odd_sign

VARGA_NAMES = {
    1: ("Rashi", "Body and overall life"),
    2: ("Hora", "Wealth"),
    3: ("Drekkana", "Siblings and courage"),
    4: ("Chaturthamsha", "Fortune, home and property"),
    7: ("Saptamsha", "Children and progeny"),
    9: ("Navamsha", "Marriage, dharma and inner strength of planets"),
    10: ("Dashamsha", "Career and public life"),
    12: ("Dwadashamsha", "Parents"),
    16: ("Shodashamsha", "Vehicles, comforts and happiness"),
    20: ("Vimshamsha", "Spiritual practice"),
    24: ("Chaturvimshamsha", "Education and learning"),
    27: ("Saptavimshamsha (Bhamsha)", "Strengths and weaknesses"),
    30: ("Trimshamsha", "Misfortunes and character"),
    40: ("Khavedamsha", "Auspicious and inauspicious effects"),
    45: ("Akshavedamsha", "General character and conduct"),
    60: ("Shashtiamsha", "Past karma; overall results"),
}

SUPPORTED_VARGAS = sorted(VARGA_NAMES)


def _parts(longitude: float, n: int) -> tuple[int, int]:
    sign = int(longitude // 30) % 12
    part = int((longitude % 30) / (30.0 / n))
    return sign, min(part, n - 1)


def _modality(sign: int) -> int:
    return sign % 3  # 0 movable, 1 fixed, 2 dual


def d1(lon: float) -> int:
    return int(lon // 30) % 12


def d2(lon: float) -> int:
    sign, part = _parts(lon, 2)
    # Parashari Hora: odd signs - Sun's hora (Leo) then Moon's (Cancer);
    # even signs - Moon's hora (Cancer) then Sun's (Leo).
    if is_odd_sign(sign):
        return 4 if part == 0 else 3
    return 3 if part == 0 else 4


def d3(lon: float) -> int:
    sign, part = _parts(lon, 3)
    return (sign + 4 * part) % 12  # same, 5th, 9th


def d4(lon: float) -> int:
    sign, part = _parts(lon, 4)
    return (sign + 3 * part) % 12  # same, 4th, 7th, 10th


def d7(lon: float) -> int:
    sign, part = _parts(lon, 7)
    start = sign if is_odd_sign(sign) else (sign + 6) % 12
    return (start + part) % 12


def d9(lon: float) -> int:
    sign, part = _parts(lon, 9)
    start = {0: sign, 1: (sign + 8) % 12, 2: (sign + 4) % 12}[_modality(sign)]
    return (start + part) % 12


def d10(lon: float) -> int:
    sign, part = _parts(lon, 10)
    start = sign if is_odd_sign(sign) else (sign + 8) % 12
    return (start + part) % 12


def d12(lon: float) -> int:
    sign, part = _parts(lon, 12)
    return (sign + part) % 12


def d16(lon: float) -> int:
    sign, part = _parts(lon, 16)
    start = {0: 0, 1: 4, 2: 8}[_modality(sign)]  # Aries, Leo, Sagittarius
    return (start + part) % 12


def d20(lon: float) -> int:
    sign, part = _parts(lon, 20)
    start = {0: 0, 1: 8, 2: 4}[_modality(sign)]  # Aries, Sagittarius, Leo
    return (start + part) % 12


def d24(lon: float) -> int:
    sign, part = _parts(lon, 24)
    start = 4 if is_odd_sign(sign) else 3  # Leo for odd, Cancer for even
    return (start + part) % 12


def d27(lon: float) -> int:
    sign, part = _parts(lon, 27)
    start = {0: 0, 1: 3, 2: 6, 3: 9}[sign % 4]  # fire Aries, earth Cancer, air Libra, water Capricorn
    return (start + part) % 12


def d30(lon: float) -> int:
    sign = int(lon // 30) % 12
    deg = lon % 30
    if is_odd_sign(sign):
        # Mars 5°, Saturn 5°, Jupiter 8°, Mercury 7°, Venus 5°
        bounds = [(5, 0), (10, 10), (18, 8), (25, 2), (30, 6)]
    else:
        # Venus 5°, Mercury 7°, Jupiter 8°, Saturn 5°, Mars 5°
        bounds = [(5, 1), (12, 5), (20, 11), (25, 9), (30, 7)]
    for limit, target in bounds:
        if deg < limit:
            return target
    return bounds[-1][1]


def d40(lon: float) -> int:
    sign, part = _parts(lon, 40)
    start = 0 if is_odd_sign(sign) else 6  # Aries for odd, Libra for even
    return (start + part) % 12


def d45(lon: float) -> int:
    sign, part = _parts(lon, 45)
    start = {0: 0, 1: 4, 2: 8}[_modality(sign)]  # Aries, Leo, Sagittarius
    return (start + part) % 12


def d60(lon: float) -> int:
    sign, part = _parts(lon, 60)
    return (sign + part) % 12


VARGA_FUNCTIONS = {
    1: d1, 2: d2, 3: d3, 4: d4, 7: d7, 9: d9, 10: d10, 12: d12,
    16: d16, 20: d20, 24: d24, 27: d27, 30: d30, 40: d40, 45: d45, 60: d60,
}


def varga_sign(lon: float, division: int) -> int:
    return VARGA_FUNCTIONS[division](lon % 360.0)
