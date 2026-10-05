"""Graha significations and Graha-Bhava Phala (results of planets in houses),
paraphrased from classical sources (BPHS, Phaladeepika, Saravali) in a
balanced register.

PLANET_IN_HOUSE[planet][house] = (polarity, text)
"""

P, N, M = "positive", "negative", "mixed"

KARAKA = {
    "Sun": "the soul, vitality, father, authority, government and self-confidence",
    "Moon": "the mind, emotions, mother, nourishment, public and receptivity",
    "Mars": "energy, courage, siblings, land, technical skill and competition",
    "Mercury": "intellect, speech, commerce, analysis, writing and adaptability",
    "Jupiter": "wisdom, teachers, children, dharma, wealth and good counsel",
    "Venus": "relationships, marriage, art, beauty, comfort and refinement",
    "Saturn": "discipline, endurance, service, longevity, labour and time",
    "Rahu": "ambition, the unconventional, foreign elements, technology and obsession",
    "Ketu": "detachment, spirituality, research, intuition and past-life tendencies",
}

CAREER_FIELDS = {
    "Sun": ["government and public administration", "leadership and management roles", "politics",
            "medicine (traditional association)", "positions of authority"],
    "Moon": ["public-facing work", "hospitality and food", "nursing and care work", "trade with the public",
             "water, travel and shipping related work"],
    "Mars": ["engineering and technical work", "defence, police and security", "surgery", "sports",
             "land, construction and real estate"],
    "Mercury": ["commerce and trade", "accounting and finance", "writing, media and communication",
                "information technology and analytics", "teaching skills"],
    "Jupiter": ["teaching and academia", "law and justice", "banking and finance", "advisory and consulting",
                "religious and counselling roles"],
    "Venus": ["arts, music and design", "fashion and beauty", "entertainment and media", "hospitality and luxury goods",
              "vehicles and comforts"],
    "Saturn": ["administration of large organisations", "industry, mining and agriculture", "labour and service sectors",
               "law and justice", "infrastructure and long-term projects"],
    "Rahu": ["technology and innovation", "foreign or multinational organisations", "aviation and electronics",
             "media and mass communication", "unconventional fields"],
    "Ketu": ["research and investigation", "spiritual and healing traditions", "precise technical work and coding",
             "mathematics", "work requiring detachment"],
}

WORK_STYLE = {
    "Sun": "leadership", "Moon": "social", "Mars": "technical", "Mercury": "analytical",
    "Jupiter": "advisory", "Venus": "creative", "Saturn": "structured", "Rahu": "innovative", "Ketu": "research",
}

WORK_STYLE_TEXT = {
    "leadership": "leadership and positions of responsibility",
    "social": "people-oriented and public-facing work",
    "technical": "technical, practical and action-oriented work",
    "analytical": "analytical, commercial and communicative work",
    "advisory": "advisory, teaching and guidance roles",
    "creative": "creative, aesthetic and relationship-based work",
    "structured": "structured, disciplined and long-term work",
    "innovative": "innovative, unconventional or international work",
    "research": "research-oriented, specialised or behind-the-scenes work",
}

DIGNITY_TEXT = {
    "exalted": "{p} is exalted: tradition considers it at its most capable, giving its significations generously.",
    "moolatrikona": "{p} is in its moolatrikona sign: tradition considers it strong, steady and purposeful.",
    "own": "{p} is in its own sign: it acts with confidence and protects the houses it rules.",
    "great friend": "{p} is in a great friend's sign: it is comfortable and supported.",
    "friend": "{p} is in a friendly sign: it functions with ease.",
    "neutral": "{p} is in a neutral sign: its results depend largely on house placement and association.",
    "enemy": "{p} is in an enemy's sign: its significations may require more effort to express.",
    "great enemy": "{p} is in a great enemy's sign: tradition considers it uncomfortable, giving mixed results.",
    "debilitated": "{p} is debilitated: tradition considers its significations harder to access unless the debilitation is cancelled.",
}

PLANET_IN_HOUSE = {
    "Sun": {
        1: (P, "The Sun in the Lagna is associated with self-confidence, leadership, a dignified presence and strong vitality; pride may need moderation."),
        2: (M, "The Sun in the 2nd is associated with authoritative speech and earnings connected with government or status, with care needed in family relations."),
        3: (P, "The Sun in the 3rd is associated with courage, initiative and success through personal effort."),
        4: (M, "The Sun in the 4th is associated with a dignified home, property through authority and occasional restlessness in domestic life."),
        5: (M, "The Sun in the 5th is associated with sharp intelligence, leadership in creative or intellectual work and a proud heart."),
        6: (P, "The Sun in the 6th is a strong placement for overcoming opponents, success in competition and service in authority."),
        7: (M, "The Sun in the 7th is associated with a strong-willed partner and the need for balance between independence and partnership."),
        8: (N, "The Sun in the 8th is associated with interest in hidden matters, along with care needed for vitality and relations with authority."),
        9: (P, "The Sun in the 9th is associated with dharma, respect for tradition, a principled outlook and support from the father or mentors."),
        10: (P, "The Sun in the 10th is a classically strong placement for career, authority, recognition and leadership (directional strength)."),
        11: (P, "The Sun in the 11th is associated with gains through authority and influential friends, and fulfilment of ambitions."),
        12: (N, "The Sun in the 12th is associated with work behind the scenes or abroad, expenditure and a reflective, spiritual tendency."),
    },
    "Moon": {
        1: (P, "The Moon in the Lagna is associated with an emotionally responsive, approachable and popular nature, sensitive to surroundings."),
        2: (P, "The Moon in the 2nd is associated with a pleasant voice, family attachment and fluctuating but replenished wealth."),
        3: (M, "The Moon in the 3rd is associated with an active, communicative mind, travel and close ties with siblings."),
        4: (P, "The Moon in the 4th is a classically strong placement for contentment, a caring home and a close bond with the mother (directional strength)."),
        5: (P, "The Moon in the 5th is associated with imagination, emotional intelligence and affection for children."),
        6: (N, "The Moon in the 6th is associated with service-oriented work, along with a sensitive digestion and mental strain from conflicts."),
        7: (P, "The Moon in the 7th is associated with an attractive, caring partner and a strong need for companionship."),
        8: (N, "The Moon in the 8th is associated with emotional depth and intuition, and with periods of anxiety that benefit from stability."),
        9: (P, "The Moon in the 9th is associated with devotion, an interest in travel and philosophy, and fortune through the mother."),
        10: (P, "The Moon in the 10th is associated with public-facing work, popularity and a career with changing phases."),
        11: (P, "The Moon in the 11th is associated with gains through the public, many friends and fulfilment of wishes."),
        12: (N, "The Moon in the 12th is associated with a rich inner life, foreign residence or travel, and sensitivity to expenditure and sleep."),
    },
    "Mars": {
        1: (M, "Mars in the Lagna is associated with energy, courage and a direct, competitive temperament; impatience may need restraint."),
        2: (N, "Mars in the 2nd is associated with frank, sharp speech and earnings through effort, with care needed in family disagreements."),
        3: (P, "Mars in the 3rd is a classically strong placement for courage, enterprise, physical vigour and success over rivals."),
        4: (N, "Mars in the 4th is associated with property and land matters, along with restlessness or friction in the home."),
        5: (M, "Mars in the 5th is associated with sharp, technical intelligence and competitive drive, with impulsiveness in speculation."),
        6: (P, "Mars in the 6th is a strong placement for defeating opponents, competitive success and resilience."),
        7: (N, "Mars in the 7th is associated with a passionate, assertive partner and the need for patience in relationships."),
        8: (N, "Mars in the 8th is associated with sudden events and an interest in research, with care advised against accidents and conflict."),
        9: (M, "Mars in the 9th is associated with strong convictions and initiative in dharma, with occasional disagreement with elders."),
        10: (P, "Mars in the 10th is a classically strong placement for career drive, technical or executive ability and achievement (directional strength)."),
        11: (P, "Mars in the 11th is associated with gains through effort, land, technical work and energetic friends."),
        12: (N, "Mars in the 12th is associated with expenditure, hidden opponents and energy directed towards foreign or secluded pursuits."),
    },
    "Mercury": {
        1: (P, "Mercury in the Lagna is a strong placement for intelligence, wit, adaptability and youthful presence (directional strength)."),
        2: (P, "Mercury in the 2nd is associated with eloquent speech, skill with numbers and earnings through intellect or trade."),
        3: (P, "Mercury in the 3rd is associated with communication skills, writing, curiosity and supportive siblings."),
        4: (P, "Mercury in the 4th is associated with education, a home filled with learning and comfort through intellect."),
        5: (P, "Mercury in the 5th is associated with sharp intelligence, quick learning and skill in analysis or creative writing."),
        6: (M, "Mercury in the 6th is associated with analytical problem-solving at work and success in competition, with a tendency to worry."),
        7: (P, "Mercury in the 7th is associated with a youthful, intelligent partner and success in trade and negotiation."),
        8: (M, "Mercury in the 8th is associated with research ability and an investigative mind, with irregular gains."),
        9: (P, "Mercury in the 9th is associated with higher learning, philosophy, publishing and well-reasoned beliefs."),
        10: (P, "Mercury in the 10th is associated with a career in commerce, communication, analysis or writing, and versatility at work."),
        11: (P, "Mercury in the 11th is associated with gains through trade, intellect and a wide network."),
        12: (N, "Mercury in the 12th is associated with an imaginative, private mind and expenditure, with gains through foreign connections."),
    },
    "Jupiter": {
        1: (P, "Jupiter in the Lagna is a classically protective placement: wisdom, optimism, good character and respect from others (directional strength)."),
        2: (P, "Jupiter in the 2nd is associated with wealth, truthful and learned speech and a respected family."),
        3: (M, "Jupiter in the 3rd is associated with principled communication and supportive siblings, though initiative may be measured."),
        4: (P, "Jupiter in the 4th is associated with a happy home, education, property and a learned mother."),
        5: (P, "Jupiter in the 5th is associated with wisdom, good counsel, scholarship and blessings concerning children."),
        6: (M, "Jupiter in the 6th is associated with success in service and handling disputes, with care advised in health related to excess."),
        7: (P, "Jupiter in the 7th is associated with a wise, principled partner and success through partnerships and counsel."),
        8: (M, "Jupiter in the 8th is associated with longevity, interest in metaphysics and gains through inheritance or joint resources."),
        9: (P, "Jupiter in the 9th is a classically fortunate placement for dharma, higher learning, teachers and good fortune."),
        10: (P, "Jupiter in the 10th is associated with an honourable career, advisory or teaching roles and a good reputation."),
        11: (P, "Jupiter in the 11th is associated with abundant gains, influential friends and fulfilment of goals."),
        12: (M, "Jupiter in the 12th is associated with charity, spiritual growth and foreign connections, with expenditure on good causes."),
    },
    "Venus": {
        1: (P, "Venus in the Lagna is associated with charm, refinement, artistic sensibility and enjoyment of comfort."),
        2: (P, "Venus in the 2nd is associated with pleasant speech, wealth, fine food and a harmonious family."),
        3: (M, "Venus in the 3rd is associated with artistic communication and pleasant relations with siblings."),
        4: (P, "Venus in the 4th is a classically strong placement for a beautiful home, vehicles, comfort and contentment (directional strength)."),
        5: (P, "Venus in the 5th is associated with romance, creativity, artistic talent and enjoyment."),
        6: (N, "Venus in the 6th is associated with service in creative fields, along with complications in relationships or excess indulgence."),
        7: (M, "Venus in the 7th is associated with an attractive partner and strong desire for partnership; tradition advises balance in relationships."),
        8: (M, "Venus in the 8th is associated with gains through the partner or inheritance and an interest in hidden subjects."),
        9: (P, "Venus in the 9th is associated with fortune, refined beliefs and good relations with mentors."),
        10: (P, "Venus in the 10th is associated with careers in arts, design, luxury, hospitality or diplomacy, and a pleasant public image."),
        11: (P, "Venus in the 11th is associated with gains through arts, partnerships and pleasant social connections."),
        12: (M, "Venus in the 12th is associated with enjoyment of comfort and private pleasures, foreign travel and spending on luxuries; tradition considers it good for bed comforts."),
    },
    "Saturn": {
        1: (M, "Saturn in the Lagna is associated with a serious, disciplined and responsible nature; progress comes steadily and later in life."),
        2: (N, "Saturn in the 2nd is associated with measured speech, slow accumulation of wealth and responsibilities towards family."),
        3: (P, "Saturn in the 3rd is associated with perseverance, endurance and success through sustained effort."),
        4: (N, "Saturn in the 4th is associated with delays or responsibilities related to home and property, and a reserved emotional life."),
        5: (N, "Saturn in the 5th is associated with serious, practical intelligence and delays or responsibilities in matters of children."),
        6: (P, "Saturn in the 6th is a strong placement for defeating opponents, endurance in service and handling hard work."),
        7: (M, "Saturn in the 7th is associated with a mature or serious partner, delays in marriage and long-lasting commitments (directional strength)."),
        8: (M, "Saturn in the 8th is traditionally associated with longevity, along with chronic obstacles and a need for patience."),
        9: (M, "Saturn in the 9th is associated with a disciplined approach to dharma and traditional values, with fortune that matures over time."),
        10: (P, "Saturn in the 10th is associated with steady rise through hard work, responsibility and positions in large organisations."),
        11: (P, "Saturn in the 11th is associated with steady, long-term gains and reliable, often older, associates."),
        12: (N, "Saturn in the 12th is associated with expenditure, isolation or foreign residence and a capacity for spiritual discipline."),
    },
    "Rahu": {
        1: (M, "Rahu in the Lagna is associated with ambition, an unconventional personality and a strong drive for recognition."),
        2: (N, "Rahu in the 2nd is associated with unusual sources of income and unconventional speech, with family matters needing care."),
        3: (P, "Rahu in the 3rd is a classically favourable placement for courage, enterprise, media and success through bold effort."),
        4: (N, "Rahu in the 4th is associated with restlessness at home, changes of residence and foreign influence on domestic life."),
        5: (N, "Rahu in the 5th is associated with unconventional intelligence and speculative tendencies, with matters of children needing care."),
        6: (P, "Rahu in the 6th is a favourable placement for overcoming competition and succeeding in demanding environments."),
        7: (N, "Rahu in the 7th is associated with unconventional or cross-cultural partnerships and the need for clarity in relationships."),
        8: (N, "Rahu in the 8th is associated with sudden changes, interest in occult subjects and unexpected resources."),
        9: (N, "Rahu in the 9th is associated with unorthodox beliefs, foreign travel and questioning of tradition."),
        10: (M, "Rahu in the 10th is associated with strong career ambition and success in modern, foreign or technology-related fields."),
        11: (P, "Rahu in the 11th is a favourable placement for large gains, influential networks and fulfilment of ambitions."),
        12: (N, "Rahu in the 12th is associated with foreign residence or travel, expenditure and interest in spirituality or seclusion."),
    },
    "Ketu": {
        1: (M, "Ketu in the Lagna is associated with an introspective, intuitive and somewhat detached personality."),
        2: (N, "Ketu in the 2nd is associated with detachment from accumulation, blunt speech and irregular family ties."),
        3: (P, "Ketu in the 3rd is associated with courage, intuition and success through focused, independent effort."),
        4: (N, "Ketu in the 4th is associated with detachment from home comforts and changes of residence."),
        5: (M, "Ketu in the 5th is associated with deep, intuitive intelligence and interest in spiritual knowledge."),
        6: (P, "Ketu in the 6th is a favourable placement for overcoming opponents and resolving obstacles."),
        7: (N, "Ketu in the 7th is associated with detachment or misunderstanding in partnerships, calling for openness."),
        8: (M, "Ketu in the 8th is associated with research ability and insight into hidden matters, along with sudden changes."),
        9: (M, "Ketu in the 9th is associated with spiritual inclination and an independent approach to tradition."),
        10: (M, "Ketu in the 10th is associated with specialised or research-oriented work and changes in career direction."),
        11: (P, "Ketu in the 11th is associated with gains through specialised skills and fulfilment of desires without excessive attachment."),
        12: (P, "Ketu in the 12th is traditionally associated with spiritual inclination and liberation (moksha), with detachment from expenditure."),
    },
}

RETRO_TEXT = ("{p} is retrograde: tradition considers a retrograde planet strong in motion (Chesta Bala) and often "
              "describes its results as internalised, revisited or delayed before maturing.")
COMBUST_TEXT = ("{p} is combust (within {d:.1f}° of the Sun): its significations are traditionally considered "
                "overshadowed by the Sun and may need conscious effort to express.")
VARGOTTAMA_TEXT = ("{p} is Vargottama (same sign in the Rashi and Navamsa): tradition considers this a source of "
                   "steadiness and strength, as if the planet were in a dignified sign.")
