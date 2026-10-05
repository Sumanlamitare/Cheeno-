"""Lagna (ascendant) and Janma Rashi (Moon sign) descriptions.

These are one input among many: the Lagna/Core Nature reading combines the
Lagna sign with the Lagna lord's placement and dignity, planets in and
aspecting the 1st house, and the Lagna nakshatra.
"""

LAGNA = [
    {  # Aries
        "personality": "Mesha Lagna is traditionally associated with an active, pioneering and direct personality, quick to initiate.",
        "temperament": "Energetic and enthusiastic, with a quick temper that usually passes quickly.",
        "behaviour": "Prefers action to deliberation and is comfortable taking the lead.",
        "orientation": "Life is oriented towards challenges, independence and personal achievement.",
        "strengths": "Courage, initiative, frankness and resilience.",
        "challenges": "Impatience, impulsiveness and difficulty completing what was started.",
    },
    {  # Taurus
        "personality": "Vrishabha Lagna is associated with a steady, patient and grounded personality that values comfort and beauty.",
        "temperament": "Calm and enduring, slow to anger but firm once decided.",
        "behaviour": "Practical, loyal and consistent, preferring security to risk.",
        "orientation": "Life is oriented towards stability, material security and enjoyment of refined things.",
        "strengths": "Reliability, patience, artistic taste and perseverance.",
        "challenges": "Stubbornness, possessiveness and resistance to change.",
    },
    {  # Gemini
        "personality": "Mithuna Lagna is associated with a curious, communicative and versatile personality.",
        "temperament": "Lively, witty and restless, with a mind that seeks variety.",
        "behaviour": "Sociable and adaptable, at ease with ideas, words and networks.",
        "orientation": "Life is oriented towards learning, communication and exchange.",
        "strengths": "Intelligence, adaptability, humour and skill with language.",
        "challenges": "Scattered focus, nervousness and inconsistency.",
    },
    {  # Cancer
        "personality": "Karka Lagna is associated with a caring, sensitive and protective personality.",
        "temperament": "Emotional and intuitive, with moods that change like the Moon.",
        "behaviour": "Nurturing and loyal, attached to family, home and familiar surroundings.",
        "orientation": "Life is oriented towards emotional security, family and belonging.",
        "strengths": "Empathy, imagination, devotion and tenacity.",
        "challenges": "Over-sensitivity, worry and holding on to the past.",
    },
    {  # Leo
        "personality": "Simha Lagna is associated with a dignified, confident and generous personality.",
        "temperament": "Warm and proud, with a natural sense of authority.",
        "behaviour": "Takes responsibility, seeks respect and protects those in their care.",
        "orientation": "Life is oriented towards leadership, recognition and creative self-expression.",
        "strengths": "Leadership, generosity, courage and loyalty.",
        "challenges": "Pride, a need for recognition and difficulty accepting criticism.",
    },
    {  # Virgo
        "personality": "Kanya Lagna is associated with an analytical, precise and service-minded personality.",
        "temperament": "Modest and discerning, with a tendency to think carefully before acting.",
        "behaviour": "Methodical, practical and helpful, with attention to detail.",
        "orientation": "Life is oriented towards improvement, usefulness and skill.",
        "strengths": "Analysis, diligence, reliability and practical intelligence.",
        "challenges": "Over-criticism, anxiety and perfectionism.",
    },
    {  # Libra
        "personality": "Tula Lagna is associated with a balanced, diplomatic and refined personality.",
        "temperament": "Courteous and harmonious, seeking fairness in all dealings.",
        "behaviour": "Cooperative and sociable, skilled at negotiation and partnership.",
        "orientation": "Life is oriented towards relationships, justice and aesthetic harmony.",
        "strengths": "Diplomacy, fairness, charm and artistic sense.",
        "challenges": "Indecision, dependence on others' approval and avoidance of conflict.",
    },
    {  # Scorpio
        "personality": "Vrishchika Lagna is associated with an intense, determined and private personality.",
        "temperament": "Deep and emotionally strong, with powerful convictions.",
        "behaviour": "Strategic and perceptive, loyal to a few and guarded with many.",
        "orientation": "Life is oriented towards depth, transformation and mastery of difficult situations.",
        "strengths": "Determination, perception, resilience and courage.",
        "challenges": "Secrecy, suspicion and holding grudges.",
    },
    {  # Sagittarius
        "personality": "Dhanu Lagna is associated with an optimistic, principled and freedom-loving personality.",
        "temperament": "Enthusiastic and straightforward, guided by ideals.",
        "behaviour": "Generous and adventurous, drawn to teaching, travel and philosophy.",
        "orientation": "Life is oriented towards dharma, higher learning and broad horizons.",
        "strengths": "Honesty, optimism, wisdom and generosity.",
        "challenges": "Bluntness, restlessness and over-confidence.",
    },
    {  # Capricorn
        "personality": "Makara Lagna is associated with a disciplined, practical and ambitious personality.",
        "temperament": "Reserved and patient, maturing with age.",
        "behaviour": "Responsible and hard-working, respectful of structure and tradition.",
        "orientation": "Life is oriented towards duty, achievement and long-term goals.",
        "strengths": "Discipline, endurance, organisation and practicality.",
        "challenges": "Pessimism, rigidity and over-emphasis on work.",
    },
    {  # Aquarius
        "personality": "Kumbha Lagna is associated with a thoughtful, humanitarian and independent personality.",
        "temperament": "Detached yet friendly, with an original way of thinking.",
        "behaviour": "Principled and community-minded, interested in ideas that serve many.",
        "orientation": "Life is oriented towards society, knowledge and progressive causes.",
        "strengths": "Originality, perseverance, fairness and loyalty to ideals.",
        "challenges": "Aloofness, stubborn opinions and unpredictability.",
    },
    {  # Pisces
        "personality": "Meena Lagna is associated with a compassionate, imaginative and spiritually inclined personality.",
        "temperament": "Gentle, intuitive and emotionally receptive.",
        "behaviour": "Kind and adaptable, drawn to art, service and devotion.",
        "orientation": "Life is oriented towards compassion, inner growth and creativity.",
        "strengths": "Empathy, imagination, devotion and generosity.",
        "challenges": "Escapism, indecision and difficulty setting boundaries.",
    },
]

MOON_SIGN = [
    "With the Moon in Mesha, the mind is traditionally described as quick, enthusiastic and courageous, eager for new experiences but prone to impatience.",
    "With the Moon in Vrishabha (its sign of exaltation), the mind is traditionally described as steady, contented and appreciative of comfort and beauty.",
    "With the Moon in Mithuna, the mind is traditionally described as curious, communicative and versatile, needing intellectual stimulation.",
    "With the Moon in Karka (its own sign), the mind is traditionally described as caring, sensitive and strongly attached to home and family.",
    "With the Moon in Simha, the mind is traditionally described as proud, generous and warm-hearted, seeking dignity and appreciation.",
    "With the Moon in Kanya, the mind is traditionally described as analytical, careful and service-oriented, with a tendency to worry over details.",
    "With the Moon in Tula, the mind is traditionally described as balanced, sociable and fair-minded, seeking harmony in relationships.",
    "With the Moon in Vrishchika (its sign of debilitation), the mind is traditionally described as intense, private and emotionally deep, capable of great resilience once its sensitivity is understood.",
    "With the Moon in Dhanu, the mind is traditionally described as optimistic, principled and philosophical, valuing freedom and truth.",
    "With the Moon in Makara, the mind is traditionally described as practical, disciplined and reserved, steady under responsibility.",
    "With the Moon in Kumbha, the mind is traditionally described as independent, humanitarian and thoughtful, interested in ideas and society.",
    "With the Moon in Meena, the mind is traditionally described as compassionate, imaginative and intuitive, drawn to devotion and the arts.",
]

NAVAMSA_SIGN_QUALITY = [
    "energy and initiative", "steadiness and enjoyment", "communication and learning", "care and sensitivity",
    "dignity and leadership", "analysis and service", "balance and partnership", "depth and intensity",
    "principle and wisdom", "discipline and duty", "independence and ideals", "compassion and devotion",
]
