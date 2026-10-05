"""Static Jyotish reference data.

Everything here is classical reference data (Brihat Parashara Hora Shastra and
standard commentaries). Where traditions differ, the convention used by this
application is stated explicitly next to the value.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Grahas
# ---------------------------------------------------------------------------

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
SEVEN_PLANETS = PLANETS[:7]  # the visible grahas (used for Shadbala, Kaal Sarp, etc.)

PLANET_INFO = {
    "Sun": {"sanskrit": "Surya", "abbr": "Su", "devanagari": "सूर्य"},
    "Moon": {"sanskrit": "Chandra", "abbr": "Mo", "devanagari": "चन्द्र"},
    "Mars": {"sanskrit": "Mangala", "abbr": "Ma", "devanagari": "मङ्गल"},
    "Mercury": {"sanskrit": "Budha", "abbr": "Me", "devanagari": "बुध"},
    "Jupiter": {"sanskrit": "Guru / Brihaspati", "abbr": "Ju", "devanagari": "गुरु"},
    "Venus": {"sanskrit": "Shukra", "abbr": "Ve", "devanagari": "शुक्र"},
    "Saturn": {"sanskrit": "Shani", "abbr": "Sa", "devanagari": "शनि"},
    "Rahu": {"sanskrit": "Rahu", "abbr": "Ra", "devanagari": "राहु"},
    "Ketu": {"sanskrit": "Ketu", "abbr": "Ke", "devanagari": "केतु"},
}

# Natural benefics / malefics (Naisargika). The Moon and Mercury are
# conditional; see dignity.functional_nature for the conditional rule.
NATURAL_BENEFICS = {"Jupiter", "Venus"}
NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

# ---------------------------------------------------------------------------
# Rashis
# ---------------------------------------------------------------------------

RASHIS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
RASHI_SANSKRIT = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena",
]
RASHI_DEVANAGARI = [
    "मेष", "वृष", "मिथुन", "कर्कट", "सिंह", "कन्या",
    "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन",
]
RASHI_LORDS = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter",
]
RASHI_ELEMENT = ["fire", "earth", "air", "water"] * 3
# Chara (movable), Sthira (fixed), Dvisvabhava (dual)
RASHI_MODALITY = ["movable", "fixed", "dual"] * 4


def is_odd_sign(sign: int) -> bool:
    """Odd signs (Aries, Gemini, ...) are index 0, 2, 4 ... (sign numbers 1, 3, 5 ...)."""
    return sign % 2 == 0


# ---------------------------------------------------------------------------
# Dignities
# ---------------------------------------------------------------------------

# Exaltation sign index and exact degree of deepest exaltation (BPHS ch. 3).
EXALTATION = {
    "Sun": (0, 10.0),
    "Moon": (1, 3.0),
    "Mars": (9, 28.0),
    "Mercury": (5, 15.0),
    "Jupiter": (3, 5.0),
    "Venus": (11, 27.0),
    "Saturn": (6, 20.0),
    # Nodes: traditions differ. This application follows the widely used
    # convention Rahu exalted in Taurus, Ketu exalted in Scorpio.
    "Rahu": (1, 20.0),
    "Ketu": (7, 20.0),
}
DEBILITATION = {p: ((s + 6) % 12, d) for p, (s, d) in EXALTATION.items()}

OWN_SIGNS = {
    "Sun": [4],
    "Moon": [3],
    "Mars": [0, 7],
    "Mercury": [2, 5],
    "Jupiter": [8, 11],
    "Venus": [1, 6],
    "Saturn": [9, 10],
    # Convention: Rahu co-rules Aquarius, Ketu co-rules Scorpio.
    "Rahu": [10],
    "Ketu": [7],
}

# Moolatrikona sign and degree range (BPHS ch. 3).
MOOLATRIKONA = {
    "Sun": (4, 0.0, 20.0),
    "Moon": (1, 4.0, 30.0),
    "Mars": (0, 0.0, 12.0),
    "Mercury": (5, 16.0, 20.0),
    "Jupiter": (8, 0.0, 10.0),
    "Venus": (6, 0.0, 15.0),
    "Saturn": (10, 0.0, 20.0),
}

# Naisargika (natural) relationships, BPHS ch. 3.
# The node relationships are a convention (Saturn-like for Rahu, Mars-like
# for Ketu is another view); this application uses the common
# "friends of Mercury/Venus/Saturn" convention for both nodes.
NATURAL_FRIENDS = {
    "Sun": {"Moon", "Mars", "Jupiter"},
    "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"},
    "Rahu": {"Mercury", "Venus", "Saturn"},
    "Ketu": {"Mercury", "Venus", "Saturn"},
}
NATURAL_ENEMIES = {
    "Sun": {"Venus", "Saturn"},
    "Moon": set(),
    "Mars": {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus": {"Sun", "Moon"},
    "Saturn": {"Sun", "Moon", "Mars"},
    "Rahu": {"Sun", "Moon", "Mars"},
    "Ketu": {"Sun", "Moon", "Mars"},
}

# Combustion orbs in degrees (Surya Siddhanta / common usage).
# Tuple = (direct, retrograde)
COMBUSTION_ORB = {
    "Moon": (12.0, 12.0),
    "Mars": (17.0, 17.0),
    "Mercury": (14.0, 12.0),
    "Jupiter": (11.0, 11.0),
    "Venus": (10.0, 8.0),
    "Saturn": (15.0, 15.0),
}

# Directional strength (Dig Bala): house in which each planet is strongest.
DIG_BALA_HOUSE = {
    "Sun": 10, "Mars": 10,
    "Jupiter": 1, "Mercury": 1,
    "Moon": 4, "Venus": 4,
    "Saturn": 7,
}

# Special aspects (Graha Drishti). Every graha aspects the 7th; these are the
# additional full aspects (counted inclusively from the planet's own sign).
SPECIAL_ASPECTS = {
    "Mars": [4, 8],
    "Jupiter": [5, 9],
    "Saturn": [3, 10],
}
# Convention: Rahu and Ketu are given only the 7th aspect in this application.
# (Some traditions give them Jupiter-like 5th/9th aspects; that view is not
# applied here.)

KENDRAS = {1, 4, 7, 10}
TRIKONAS = {1, 5, 9}
DUSTHANAS = {6, 8, 12}
UPACHAYAS = {3, 6, 10, 11}
PANAPARAS = {2, 5, 8, 11}
APOKLIMAS = {3, 6, 9, 12}
MARAKA_HOUSES = {2, 7}

# ---------------------------------------------------------------------------
# Nakshatras
# ---------------------------------------------------------------------------

NAKSHATRA_SPAN = 360.0 / 27.0  # 13°20'
PADA_SPAN = NAKSHATRA_SPAN / 4.0  # 3°20'

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]
NAKSHATRA_DEVANAGARI = [
    "अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशिरा", "आर्द्रा",
    "पुनर्वसु", "पुष्य", "आश्लेषा", "मघा", "पूर्वफाल्गुनी", "उत्तरफाल्गुनी",
    "हस्त", "चित्रा", "स्वाती", "विशाखा", "अनुराधा", "ज्येष्ठा",
    "मूल", "पूर्वाषाढा", "उत्तराषाढा", "श्रवण", "धनिष्ठा", "शतभिषा",
    "पूर्वभाद्रपद", "उत्तरभाद्रपद", "रेवती",
]

# Vimshottari sequence and mahadasha years.
DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17,
}
VIMSHOTTARI_TOTAL = 120


def nakshatra_lord(nak_index: int) -> str:
    return DASHA_ORDER[nak_index % 9]


# Gandamula nakshatras (junction nakshatras at water/fire sign boundaries).
GANDAMULA_NAKSHATRAS = {0, 8, 9, 17, 18, 26}

# ---------------------------------------------------------------------------
# Panchanga names
# ---------------------------------------------------------------------------

TITHIS = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi",
]  # 15th is Purnima (Shukla) or Amavasya (Krishna)

VARAS = ["Ravivara", "Somavara", "Mangalavara", "Budhavara", "Guruvara", "Shukravara", "Shanivara"]
VARA_ENGLISH = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
VARA_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

YOGAS_27 = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
    "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva",
    "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana",
    "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla",
    "Brahma", "Indra", "Vaidhriti",
]
INAUSPICIOUS_NITYA_YOGAS = {
    "Vishkambha", "Atiganda", "Shula", "Ganda", "Vyaghata", "Vajra",
    "Vyatipata", "Parigha", "Vaidhriti",
}

MOVABLE_KARANAS = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]

LUNAR_MONTHS = [
    "Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada",
    "Ashwin", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna",
]

# Nepali (Bikram Sambat) solar month names
BS_MONTHS = [
    "Baisakh", "Jestha", "Asar", "Shrawan", "Bhadra", "Ashwin",
    "Kartik", "Mangsir", "Poush", "Magh", "Falgun", "Chaitra",
]
BS_MONTHS_DEVANAGARI = [
    "बैशाख", "जेठ", "असार", "साउन", "भदौ", "असोज",
    "कात्तिक", "मंसिर", "पुस", "माघ", "फागुन", "चैत",
]

# Shadbala: required minimum (in rupas) per BPHS.
SHADBALA_REQUIRED_RUPAS = {
    "Sun": 6.5, "Moon": 6.0, "Mars": 5.0, "Mercury": 7.0,
    "Jupiter": 6.5, "Venus": 5.5, "Saturn": 5.0,
}
NAISARGIKA_BALA = {
    "Sun": 60.0, "Moon": 51.43, "Venus": 42.86, "Jupiter": 34.29,
    "Mercury": 25.71, "Mars": 17.14, "Saturn": 8.57,
}

# Mean daily motions (degrees/day), used to classify the eight kinds of
# planetary motion for Chesta Bala.
MEAN_DAILY_MOTION = {
    "Mars": 0.5240, "Mercury": 0.9856, "Jupiter": 0.0831,
    "Venus": 0.9856, "Saturn": 0.0335,
}


def ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suf = "th"
    else:
        suf = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


def house_from(reference_sign: int, sign: int) -> int:
    """Inclusive count of houses from reference_sign to sign (1..12)."""
    return (sign - reference_sign) % 12 + 1


def format_dms(deg: float, with_seconds: bool = True) -> str:
    """Format degrees within a sign as D°M'S"."""
    total_seconds = round(deg * 3600)
    d, rem = divmod(total_seconds, 3600)
    m, s = divmod(rem, 60)
    if with_seconds:
        return f"{d}°{m:02d}'{s:02d}\""
    return f"{d}°{m:02d}'"
