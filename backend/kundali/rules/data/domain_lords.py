"""Domain-focused readings of house-lord placements (classical Bhavesha
results restated for the specific life area). (polarity, text)."""

P, N, M = "positive", "negative", "mixed"

# Lord of the 5th (intelligence, learning) placed in house y - education focus.
EDU_L5 = {
    1: (P, "The 5th lord in the Lagna is traditionally associated with natural intelligence and a person whose learning is part of their identity."),
    2: (P, "The 5th lord in the 2nd is associated with learning that turns into skill with words, numbers or teaching, and earning through knowledge."),
    3: (M, "The 5th lord in the 3rd is associated with a practical, hands-on learner who does well in communication, media, writing or skills-based study."),
    4: (P, "The 5th lord in the 4th is associated with a supportive learning environment at home and success in formal education."),
    5: (P, "The 5th lord in its own house is a classical indication of sharp intelligence, good memory and success in studies."),
    6: (N, "The 5th lord in the 6th is associated with studies that meet obstacles or competition; disciplined routines help, and competitive exams can suit this placement."),
    7: (M, "The 5th lord in the 7th is associated with learning best through discussion, mentors and study partners, and an interest in subjects involving people, trade or law."),
    8: (N, "The 5th lord in the 8th is associated with interrupted or non-linear studies and a mind drawn to research, deep or hidden subjects."),
    9: (P, "The 5th lord in the 9th is a classical indication of success in higher education, good teachers and philosophical depth."),
    10: (P, "The 5th lord in the 10th is associated with education that leads directly to profession and recognition for knowledge."),
    11: (P, "The 5th lord in the 11th is associated with fulfilment of academic goals and gains through one's education."),
    12: (M, "The 5th lord in the 12th is associated with study away from home or abroad, and an imaginative or contemplative mind; focus may need effort."),
}

# Lord of the 4th (foundational education, schooling environment) - education focus.
EDU_L4 = {
    1: (P, "The 4th lord in the Lagna is associated with a good educational foundation and comfort in learning environments."),
    2: (P, "The 4th lord in the 2nd is associated with family support for schooling."),
    3: (M, "The 4th lord in the 3rd is associated with schooling that may involve moves or changes, and learning through effort."),
    4: (P, "The 4th lord in its own house is associated with a strong educational foundation."),
    5: (P, "The 4th lord in the 5th joins foundational and higher learning, a classical support for education."),
    6: (N, "The 4th lord in the 6th is associated with disturbances in early schooling that are overcome with effort."),
    7: (M, "The 4th lord in the 7th is associated with learning shaped by others and study connected with public dealings."),
    8: (N, "The 4th lord in the 8th is associated with breaks or changes in early education."),
    9: (P, "The 4th lord in the 9th is associated with good teachers and a smooth path to higher learning."),
    10: (P, "The 4th lord in the 10th is associated with education that supports one's career."),
    11: (P, "The 4th lord in the 11th is associated with academic goals being fulfilled."),
    12: (M, "The 4th lord in the 12th is associated with schooling away from home."),
}

# Lord of the 5th placed in house y - children focus (non-medical, symbolic).
CHILD_L5 = {
    1: (P, "The 5th lord in the Lagna is traditionally associated with close, affectionate bonds with children."),
    2: (P, "The 5th lord in the 2nd is associated with children who are part of a supportive family life."),
    3: (M, "The 5th lord in the 3rd is associated with active, independent children and effort in raising them."),
    4: (P, "The 5th lord in the 4th is associated with happiness from children at home."),
    5: (P, "The 5th lord in its own house is a classical blessing for children."),
    6: (N, "The 5th lord in the 6th is traditionally associated with patience being needed in matters of children."),
    7: (P, "The 5th lord in the 7th is associated with children connected closely with the partnership and family harmony."),
    8: (N, "The 5th lord in the 8th is traditionally associated with patience and care in matters of children."),
    9: (P, "The 5th lord in the 9th is a classical indication of fortunate, well-guided children."),
    10: (P, "The 5th lord in the 10th is associated with children who bring recognition."),
    11: (P, "The 5th lord in the 11th is associated with fulfilment through children."),
    12: (M, "The 5th lord in the 12th is associated with children living at a distance or expenses on their behalf."),
}

# Lord of the 9th (higher learning, teachers) - education focus.
EDU_L9 = {
    1: (P, "The 9th lord in the Lagna is associated with a love of higher learning and respect for teachers."),
    2: (P, "The 9th lord in the 2nd is associated with higher learning supported by the family and skill in speech or teaching."),
    3: (M, "The 9th lord in the 3rd is associated with higher learning through self-study, writing or travel."),
    4: (P, "The 9th lord in the 4th is associated with a smooth path from schooling to higher education."),
    5: (P, "The 9th lord in the 5th unites wisdom and intelligence, a classical support for advanced studies."),
    6: (N, "The 9th lord in the 6th is associated with obstacles to higher studies that are overcome through persistence."),
    7: (P, "The 9th lord in the 7th is associated with higher learning through mentors, partners or study abroad."),
    8: (M, "The 9th lord in the 8th is associated with interrupted higher studies and an interest in research or esoteric subjects."),
    9: (P, "The 9th lord in its own house is a classical indication of success in higher learning and good teachers."),
    10: (P, "The 9th lord in the 10th is associated with higher education that shapes an honourable career."),
    11: (P, "The 9th lord in the 11th is associated with fulfilment of academic ambitions."),
    12: (M, "The 9th lord in the 12th is associated with higher studies abroad or in spiritual subjects."),
}
