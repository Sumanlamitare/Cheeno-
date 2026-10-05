"""Gochar phala: traditional transit results counted from the natal Moon
(Phaladeepika ch. 26 and common practice). Major slow-moving planets have
individual texts; faster planets use their favourable / unfavourable
classification with their significations."""

GOCHAR_MAJOR = {
    "Saturn": {
        1: "Saturn over the natal Moon is the peak of Sade Sati: tradition associates it with heavier responsibilities, fatigue and emotional pressure, rewarding patience, health care and disciplined routine.",
        2: "Saturn in the 2nd from the Moon is the closing phase of Sade Sati: attention to family finances, speech and savings is traditionally advised as pressures gradually ease.",
        3: "Saturn in the 3rd from the Moon is classically favourable: success through persistence, courage, recovery of strength and gains from steady effort.",
        4: "Saturn in the 4th from the Moon (Kantaka Shani) is traditionally associated with domestic responsibilities, property matters and the need for emotional steadiness.",
        5: "Saturn in the 5th from the Moon is associated with seriousness in studies, children or speculation, and caution in judgement.",
        6: "Saturn in the 6th from the Moon is classically favourable: victory over obstacles and competitors, improved health through discipline and success in service.",
        7: "Saturn in the 7th from the Moon is associated with responsibilities and tests in partnerships and travel, calling for patience with others.",
        8: "Saturn in the 8th from the Moon (Ashtama Shani) is traditionally associated with obstacles, delays and the need for care in health and finances.",
        9: "Saturn in the 9th from the Moon is associated with reassessment of beliefs, duties towards elders and fortune that comes slowly.",
        10: "Saturn in the 10th from the Moon is associated with increased workload and responsibility in career; tradition considers results mixed, rewarding sincere effort.",
        11: "Saturn in the 11th from the Moon is classically favourable: steady gains, fulfilment of long-held goals and support from seniors.",
        12: "Saturn in the 12th from the Moon is the opening phase of Sade Sati: tradition associates it with increased expenses, travel and reduced rest, best met with planning.",
    },
    "Jupiter": {
        1: "Jupiter over the natal Moon is traditionally associated with mixed results: changes of place or role and expenditure, alongside wisdom and growth.",
        2: "Jupiter in the 2nd from the Moon is classically favourable for wealth, family harmony, pleasant speech and accumulation.",
        3: "Jupiter in the 3rd from the Moon is associated with obstacles to initiative and changes in position, best met with patience.",
        4: "Jupiter in the 4th from the Moon is associated with domestic concerns and the need for contentment; property matters require care.",
        5: "Jupiter in the 5th from the Moon is classically favourable for learning, children, creativity, good judgement and advancement.",
        6: "Jupiter in the 6th from the Moon is associated with competition, health care and obstacles that require effort.",
        7: "Jupiter in the 7th from the Moon is classically favourable for marriage, partnerships, travel and good company.",
        8: "Jupiter in the 8th from the Moon is traditionally associated with obstacles, delays and a need for caution in health and finances.",
        9: "Jupiter in the 9th from the Moon is classically favourable for fortune, dharma, higher learning and support from elders and teachers.",
        10: "Jupiter in the 10th from the Moon is associated with changes in career and responsibilities; results depend on the natal chart.",
        11: "Jupiter in the 11th from the Moon is classically favourable for gains, recognition, fulfilment of wishes and supportive friends.",
        12: "Jupiter in the 12th from the Moon is associated with expenditure, travel and spiritual or charitable pursuits.",
    },
    "Rahu": {
        1: "Rahu over the natal Moon is associated with mental restlessness, ambition and unusual experiences; tradition advises clarity of purpose.",
        2: "Rahu in the 2nd from the Moon is associated with fluctuating finances and the need for care in speech and family matters.",
        3: "Rahu in the 3rd from the Moon is classically favourable: courage, bold initiatives and success over rivals.",
        4: "Rahu in the 4th from the Moon is associated with restlessness at home and changes concerning residence.",
        5: "Rahu in the 5th from the Moon is associated with unconventional thinking and caution in speculation.",
        6: "Rahu in the 6th from the Moon is classically favourable for overcoming obstacles, competitors and illness.",
        7: "Rahu in the 7th from the Moon is associated with unusual developments in partnerships and the need for clear agreements.",
        8: "Rahu in the 8th from the Moon is associated with sudden changes and caution in health and risk-taking.",
        9: "Rahu in the 9th from the Moon is associated with questioning beliefs and long-distance travel.",
        10: "Rahu in the 10th from the Moon is associated with ambitious career moves and unconventional opportunities.",
        11: "Rahu in the 11th from the Moon is classically favourable for gains, ambitions and influential contacts.",
        12: "Rahu in the 12th from the Moon is associated with expenses, foreign connections and disturbed rest.",
    },
    "Ketu": {
        1: "Ketu over the natal Moon is associated with introspection, detachment and a search for meaning.",
        2: "Ketu in the 2nd from the Moon is associated with detachment from accumulation and care in speech.",
        3: "Ketu in the 3rd from the Moon is classically favourable for courage, focused effort and success.",
        4: "Ketu in the 4th from the Moon is associated with detachment from domestic comforts and changes at home.",
        5: "Ketu in the 5th from the Moon is associated with spiritual study and caution in decisions regarding children or speculation.",
        6: "Ketu in the 6th from the Moon is classically favourable for overcoming obstacles and opponents.",
        7: "Ketu in the 7th from the Moon is associated with detachment or misunderstandings in partnerships.",
        8: "Ketu in the 8th from the Moon is associated with research, spiritual insight and caution regarding sudden events.",
        9: "Ketu in the 9th from the Moon is associated with pilgrimage and spiritual inclination.",
        10: "Ketu in the 10th from the Moon is associated with changes or reassessment in career.",
        11: "Ketu in the 11th from the Moon is classically favourable for gains and fulfilment.",
        12: "Ketu in the 12th from the Moon is associated with spiritual practice, retreat and expenditure.",
    },
}

FAST_PLANET_THEME = {
    "Sun": "status, health and dealings with authority",
    "Moon": "mood, comfort and daily affairs",
    "Mars": "energy, initiative and disputes",
    "Mercury": "communication, trade and learning",
    "Venus": "relationships, comforts and enjoyment",
}

VEDHA_TEXT = ("Its favourable result is traditionally considered obstructed (Vedha) because {by} transits the "
              "corresponding Vedha house from the Moon.")
