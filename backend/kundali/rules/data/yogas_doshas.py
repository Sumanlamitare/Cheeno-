"""Traditional interpretations for detected yogas and doshas."""

YOGA_TEXT = {
    "gaja_kesari": "Gaja Kesari Yoga is traditionally associated with intelligence, reputation, the respect of others and the ability to overcome adversaries, its results depending on the strength of Jupiter and the Moon.",
    "budha_aditya": "Budha-Aditya Yoga is traditionally associated with intelligence, skill in communication and analysis, and recognition for learning.",
    "chandra_mangala": "Chandra-Mangala Yoga is traditionally associated with enterprise, earning capacity and a resourceful, determined mind.",
    "ruchaka": "Ruchaka Yoga (Mars) is traditionally associated with courage, physical strength, leadership and success in technical, executive or protective roles.",
    "bhadra": "Bhadra Yoga (Mercury) is traditionally associated with intelligence, eloquence, learning and success in commerce or scholarship.",
    "hamsa": "Hamsa Yoga (Jupiter) is traditionally associated with wisdom, righteousness, respect and good fortune.",
    "malavya": "Malavya Yoga (Venus) is traditionally associated with refinement, artistic ability, comforts, vehicles and a harmonious married life.",
    "sasa": "Sasa Yoga (Saturn) is traditionally associated with authority gained through discipline, organisational ability and influence over many people.",
    "raja_kendra_trikona": "This Raja Yoga links the pillars of the chart (kendras) with its sources of fortune (trikonas); tradition associates it with status, achievement and support, especially during the planetary periods of the planets involved.",
    "yogakaraka": "A Yogakaraka planet owns both a kendra and a trikona; tradition considers it the most beneficial planet for this Lagna, whose periods and condition carry special weight.",
    "dharma_karmadhipati": "Dharma-Karmadhipati Yoga connects the lords of dharma (9th) and karma (10th); tradition associates it with a purposeful, respected career and fortune through work.",
    "dhana": "This Dhana Yoga links the lords of wealth houses with the lords of fortune and self; tradition associates it with capacity for earning and accumulation, particularly in the periods of the planets involved.",
    "lakshmi": "Lakshmi Yoga is traditionally associated with prosperity, generosity and a dignified, fortunate life.",
    "harsha": "Harsha Yoga (6th lord in a dusthana) is traditionally associated with victory over opponents, good health and happiness after difficulties.",
    "sarala": "Sarala Yoga (8th lord in a dusthana) is traditionally associated with resilience, fearlessness and success in overcoming crises.",
    "vimala": "Vimala Yoga (12th lord in a dusthana) is traditionally associated with prudent expenditure, independence and good conduct.",
    "neecha_bhanga": "Neecha Bhanga Raja Yoga indicates that a debilitated planet's weakness is classically cancelled; tradition associates it with rising after initial difficulties in the matters of that planet.",
    "adhi": "Adhi Yoga is traditionally associated with leadership, comfort and the support of capable people.",
    "sunapha": "Sunapha Yoga is traditionally associated with self-earned wealth, intelligence and good reputation.",
    "anapha": "Anapha Yoga is traditionally associated with a well-formed character, good health and dignity.",
    "durudhara": "Durudhara Yoga is traditionally associated with comforts, generosity and wealth, with the Moon well supported on both sides.",
    "vesi": "Vesi Yoga is traditionally associated with truthfulness, balanced temperament and steady effort.",
    "vasi": "Vasi Yoga is traditionally associated with skill, generosity and recognition.",
    "ubhayachari": "Ubhayachari Yoga is traditionally associated with eloquence, balance and a well-supported sense of self.",
    "amala": "Amala Yoga is traditionally associated with a spotless reputation, ethical conduct and lasting recognition.",
    "vasumati": "Vasumati Yoga is traditionally associated with growing prosperity through one's own effort.",
    "saraswati": "Saraswati Yoga is traditionally associated with learning, eloquence, artistic and scholarly accomplishment.",
    "maha_parivartana": "Maha Parivartana Yoga joins the results of two good houses; tradition associates it with mutual support between those areas of life.",
    "khala_parivartana": "Khala Parivartana Yoga involves the 3rd house; tradition associates it with fluctuating results that improve through effort.",
    "dainya_parivartana": "Dainya Parivartana Yoga involves a dusthana; tradition associates it with challenges in the houses exchanged, which can turn favourable later in life.",
    "shakata": "Shakata Yoga is traditionally associated with fluctuations of fortune, like the turning of a cart wheel; Jupiter's and the Moon's overall strength moderate it.",
}

YOGA_CATEGORIES = {
    "gaja_kesari": ["general", "career"], "budha_aditya": ["education", "career"],
    "chandra_mangala": ["wealth"], "ruchaka": ["career"], "bhadra": ["education", "career"],
    "hamsa": ["general", "education"], "malavya": ["marriage", "wealth"], "sasa": ["career"],
    "raja_kendra_trikona": ["career", "general"], "yogakaraka": ["career", "general"],
    "dharma_karmadhipati": ["career"], "dhana": ["wealth"], "lakshmi": ["wealth"],
    "harsha": ["health"], "sarala": ["general"], "vimala": ["wealth"], "neecha_bhanga": ["general"],
    "adhi": ["career"], "sunapha": ["wealth"], "anapha": ["general"], "durudhara": ["wealth"],
    "vesi": ["general"], "vasi": ["general"], "ubhayachari": ["general"], "amala": ["career"],
    "vasumati": ["wealth"], "saraswati": ["education"], "maha_parivartana": ["general"],
    "khala_parivartana": ["general"], "dainya_parivartana": ["general"], "shakata": ["wealth"],
}

DOSHA_TEXT = {
    "mangal": {
        "detected": "Traditionally, Mangal Dosha is associated with intensity and assertiveness in married life, and it is customarily weighed during Kundali matching, where a similar placement in the partner's chart is considered balancing.",
        "not": "Mars does not occupy the houses that define Mangal Dosha under the rule used by this application.",
    },
    "kaal_sarp": {
        "detected": "Where it is accepted, Kaal Sarp is associated with periods of intense effort followed by breakthroughs, and with a life strongly shaped by the Rahu-Ketu axis. Its importance is disputed.",
        "not": "The seven grahas are not confined to one side of the Rahu-Ketu axis, so Kaal Sarp is not formed under this application's rule.",
    },
    "kemadruma": {
        "detected": "Kemadruma Yoga is traditionally associated with periods of feeling unsupported and fluctuating resources; classical texts stress that it is commonly cancelled, and here no cancelling factor was found.",
        "not": "Kemadruma Yoga is not in effect.",
    },
    "gandamula": {
        "detected": "Birth in a Gandamula nakshatra is customarily acknowledged in Nepal with a Mula Shanti puja, usually performed when the Moon returns to the birth nakshatra; tradition treats it as an observance rather than a prediction.",
        "not": "The Moon is not in a Gandamula nakshatra.",
    },
    "grahana": {
        "detected": "Where it is considered, Grahana Yoga is associated with emotional or confidence-related fluctuations in the significations of the luminary involved. It is a non-Parashari combination.",
        "not": "Neither luminary shares a sign with Rahu or Ketu.",
    },
}

SADE_SATI_TEXT = {
    "overview": ("Sade Sati is the roughly seven-and-a-half-year period during which Saturn transits the 12th, 1st "
                 "and 2nd signs from the natal Moon. Traditional texts do not describe it as uniformly unfavourable: "
                 "it is a period of maturation, responsibility and restructuring whose experience depends on "
                 "Saturn's condition in the natal chart and on the running Dasha."),
    1: ("In the first (rising) phase, Saturn transits the 12th from the Moon. Tradition associates this phase with "
        "increased expenses, travel or relocation, and reduced rest; planning and moderation are advised."),
    2: ("In the second (peak) phase, Saturn transits the natal Moon sign. Tradition associates this phase with "
        "emotional pressure, heavier responsibilities and attention to health, together with lasting maturity "
        "built through discipline."),
    3: ("In the third (setting) phase, Saturn transits the 2nd from the Moon. Tradition associates this phase with "
        "attention to family, finances and speech as pressures gradually lift."),
    "favourable_saturn": ("Saturn is well placed in this chart ({reason}), which tradition considers to soften "
                          "Sade Sati and to make it a period of constructive achievement."),
    "yogakaraka_saturn": ("Saturn is a Yogakaraka for this Lagna, so tradition considers its transits, including "
                          "Sade Sati, more constructive than usual."),
    "weak_saturn": ("Saturn is weak in this chart ({reason}), so tradition advises extra patience and care during "
                    "Saturn's transits."),
    "dhaiya": ("Saturn's transit of the 4th (Kantaka) or 8th (Ashtama) from the Moon, called Dhaiya or small Panoti, "
               "lasts about two and a half years and is treated in tradition as a lighter period of Saturnine "
               "responsibility."),
}
