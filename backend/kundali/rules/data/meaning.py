"""Personal, practical meaning ("what this means for you").

Second-person restatements of the classical indications, each paired with
practical advice. Keyed by the same themes and placements the rule engine
uses, so every statement shown to a person traces back to a matched rule.
Language is deliberately hedged: tendencies, not certainties.
"""

# theme -> polarity -> (what it means for you, what you can do)
THEME_YOU = {
    # ---------------- Career ----------------
    "career.status": {
        "positive": ("You are likely to be noticed and respected for your work. Over time you can reach positions "
                     "with real responsibility and a recognised name in your field.",
                     "Aim for roles with visibility and responsibility rather than staying behind the scenes."),
    },
    "career.gains": {
        "positive": ("Your work tends to pay off through people: contacts, clients, teams and networks bring many "
                     "of your best opportunities, and your career is likely to reward you financially.",
                     "Invest in your professional network and keep in touch with colleagues and clients."),
    },
    "career.effort": {
        "positive": ("Your progress comes from persistence. You may not rise overnight, but steady effort and skill "
                     "keep building on each other, and you can last a long time in your field.",
                     "Choose a path you can commit to for years; consistency is your advantage."),
        "mixed": ("Recognition may come more slowly than you would like, but what you build through hard work "
                  "tends to last.",
                  "Measure your progress over years, not months, and avoid giving up too early."),
    },
    "career.fortune": {
        "positive": ("Good mentors, ethical choices and a bit of luck support your career. People in senior "
                     "positions are inclined to help you.",
                     "Seek out a mentor and stay on the right side of ethics; your reputation is an asset."),
    },
    "career.service": {
        "positive": ("You do well in competitive or problem-solving work, where you handle difficulties others avoid.",
                     "Consider fields like law, healthcare, administration, consulting or anything competitive."),
        "mixed": ("Your career may involve service, problem-solving or dealing with difficulties. You earn "
                  "recognition by handling what others find hard.",
                  "Fields such as law, healthcare, administration or troubleshooting may suit you."),
        "negative": ("Workplace rivalry or demanding conditions may be a recurring theme.",
                     "Document your work, avoid office politics and build allies."),
    },
    "career.change": {
        "negative": ("Your career path may not be a straight line. Expect changes of direction, interruptions or "
                     "periods where things feel uncertain before they settle.",
                     "Keep your skills portable and build savings so changes become opportunities rather than crises."),
        "mixed": ("You may revisit or rethink your career direction more than once before it settles.",
                  "Treat early jobs as experiments; it is fine to change course."),
    },
    "career.foreign": {
        "negative": ("Your work may take you abroad, into large institutions or into behind-the-scenes roles, and "
                     "visibility may come in phases.",
                     "Look at international companies, foreign postings or institutional roles."),
        "mixed": ("Unconventional, foreign or technology-related directions may attract you, with some sudden turns.",
                  "Stay open to unusual opportunities, but check them carefully before committing."),
    },
    "career.leadership": {
        "positive": ("You have natural drive and leadership energy. You are likely to do well when you are in charge, "
                     "making decisions or leading technical or executive work.",
                     "Take on leadership roles early, even small ones, to build that strength."),
    },
    "career.d10": {
        "positive": ("The chart that refines your career (D10) backs up your main chart, which tradition takes as a "
                     "sign that your professional promise holds.",
                     "Trust your long-term career direction."),
        "negative": ("The career chart (D10) suggests your professional path takes extra patience to settle.",
                     "Be patient in your twenties and early career; stability tends to come with time."),
    },
    "career.yoga": {
        "positive": ("Your chart has combinations traditionally linked with rising in status, especially during "
                     "certain planetary periods (listed below).",
                     "Use the favourable periods below to push for promotions, launches or big moves."),
    },

    # ---------------- Wealth ----------------
    "wealth.accumulation": {
        "positive": ("You have a good capacity to build savings and family resources over time.",
                     "Automate saving; your chart rewards steady accumulation."),
        "mixed": ("Savings can grow, but they tend to rise and fall with circumstances.",
                  "Keep an emergency fund so dips do not undo your progress."),
    },
    "wealth.income": {
        "positive": ("Your income potential is good: gains can come through your work, contacts and ambitions.",
                     "Pursue income growth actively; ask for raises and take on paying opportunities."),
    },
    "wealth.fortune": {
        "positive": ("Luck and good judgement support your finances; opportunities tend to appear when you need them.",
                     "Say yes to well-researched opportunities rather than playing it too safe."),
        "mixed": ("Fortune helps, but it comes with some ups and downs.",
                  "Diversify rather than betting on a single source of luck."),
    },
    "wealth.effort": {
        "mixed": ("Money comes mostly through your own effort, enterprise and initiative rather than inheritance or luck.",
                  "Side projects, business ideas or skill-based work can add to your income."),
    },
    "wealth.fluctuation": {
        "negative": ("Your finances may go through ups and downs, including unexpected expenses or irregular income.",
                     "Avoid heavy debt and speculation; keep a buffer for lean periods."),
    },
    "wealth.discipline": {
        "negative": ("Money can slip through your fingers. You may earn reasonably well but find it harder to hold on "
                     "to it, through spending, family obligations or expenses abroad.",
                     "Budget deliberately, track spending and save before you spend."),
    },
    "wealth.karaka": {
        "positive": ("The planets of wealth and comfort (Jupiter and Venus) support you, so you are likely to enjoy "
                     "comforts and have the means for them.",
                     "Balance enjoyment with saving so comfort lasts."),
        "negative": ("The natural planet of wealth is weaker in your chart, so good financial advice matters more for you.",
                     "Get sound financial advice before large decisions and avoid impulsive investments."),
    },
    "wealth.yoga": {
        "positive": ("Your chart contains classical wealth combinations, which tradition links with good earning "
                     "capacity, especially in certain periods.",
                     "Use the favourable periods below for investments, business moves or career changes."),
    },

    # ---------------- Education ----------------
    "education.foundation": {
        "positive": ("You are likely to have, or to build, a solid educational foundation, and you learn well in a "
                     "stable environment.",
                     "A quiet, consistent study routine at home suits you."),
        "mixed": ("Your early schooling may involve changes, but you can make up ground through effort.",
                  "Fill early gaps deliberately; they close quickly once you focus."),
    },
    "education.intellect": {
        "positive": ("You have good natural intelligence and can do well academically.",
                     "Take on challenging subjects; you are capable of more than you may assume."),
        "mixed": ("You learn best through discussion, mentors and applying ideas, rather than studying alone.",
                  "Join study groups, find a mentor and learn by doing."),
    },
    "education.obstacles": {
        "negative": ("Your studies may meet interruptions, distractions or obstacles at times.",
                     "Use structure (fixed timetables, deadlines and revision) to stay on track."),
    },
    "education.higher": {
        "positive": ("Higher education and good teachers are well supported for you; further study can open doors.",
                     "Seriously consider postgraduate study, certifications or training abroad."),
        "mixed": ("Higher studies may happen in an unusual way: abroad, later in life, or in deep or specialised subjects.",
                  "Do not worry if your path is non-linear; returning to study later can work well for you."),
    },
    "education.analytical": {
        "positive": ("You have a sharp, analytical mind, with strengths in language, logic, numbers or communication.",
                     "Subjects involving analysis, writing, commerce, technology or languages suit you."),
    },
    "education.wisdom": {
        "positive": ("You have depth of understanding and good judgement, not just quick learning.",
                     "Subjects like law, philosophy, finance, teaching or anything requiring judgement suit you."),
    },
    "education.yoga": {
        "positive": ("Your chart has combinations traditionally linked with learning and intelligence.",
                     "Invest in your education; it is one of your strongest assets."),
    },

    # ---------------- Marriage ----------------
    "marriage.harmony": {
        "positive": ("Partnership is well supported in your chart; you are likely to find a supportive, caring "
                     "relationship.",
                     "Choose a partner who shares your values; your chart rewards commitment."),
        "mixed": ("Relationships matter a great deal to you and shape much of your life.",
                  "Keep your own identity within the relationship."),
    },
    "marriage.partner": {
        "positive": ("You are likely to attract an attractive, intelligent or capable partner.",
                     "Look beyond surface attraction to long-term compatibility."),
        "mixed": ("Your partner is likely to be strong-willed or distinctive, and you may want both closeness and independence.",
                  "Talk openly about how much independence each of you needs."),
    },
    "marriage.friction": {
        "negative": ("Relationships may involve disagreements, strong emotions or tests at times.",
                     "Practise patience and clear communication; avoid deciding things in anger."),
    },
    "marriage.fortune": {
        "positive": ("Your life may improve after marriage; partnership can bring fortune and support to your career.",
                     "Treat your partner as a real teammate in your plans."),
    },
    "marriage.distance": {
        "negative": ("Your partner may come from a distant place or different background, or there may be periods of "
                     "physical distance or extra expense in the relationship.",
                     "Plan finances together and make time for each other, especially when apart."),
    },
    "marriage.delay": {
        "mixed": ("Marriage may come later, or after careful consideration, but the commitment tends to be durable.",
                  "There is no need to rush; a later or carefully chosen match suits your chart."),
    },
    "marriage.venus": {
        "positive": ("Venus, the planet of love, is strong for you, which supports affection, attraction and harmony.",
                     "Express appreciation openly; it strengthens your relationships."),
        "negative": ("Venus is weaker for you, so keeping romance and appreciation alive may take conscious effort.",
                     "Make deliberate time for affection and shared enjoyment."),
    },
    "marriage.d9": {
        "positive": ("Your marriage chart (Navamsa) supports your main chart, a traditional sign of a sound partnership.",
                     "Trust a relationship that feels steady and right."),
        "negative": ("Your marriage chart (Navamsa) suggests partnership needs patience and good communication.",
                     "Invest in communication skills early in the relationship."),
    },
    "marriage.dosha": {
        "mixed": ("You have Mangal Dosha under the rule used here. Traditionally this is compared with the partner's "
                  "chart during matching, and is often balanced by it.",
                  "If matching is important to your family, compare charts with a trusted astrologer."),
    },

    # ---------------- Family ----------------
    "family.home": {
        "positive": ("Home and family are a source of comfort for you, and property or a settled home is well supported.",
                     "Owning or building a home is a realistic, supported goal for you."),
        "mixed": ("Home life is important to you but may change shape over time.",
                  "Create stability through routines and relationships, wherever you live."),
    },
    "family.kin": {
        "positive": ("Family ties are supportive, and you are likely to be valued within your family.",
                     "Stay connected with family; they are a real resource for you."),
        "mixed": ("Your family relationships have both warmth and complexity.",
                  "Set clear boundaries while staying connected."),
    },
    "family.unsettled": {
        "negative": ("Home or family life may involve responsibilities, tension or changes of residence at times.",
                     "Keep communication open at home and avoid letting small issues build up."),
    },
    "family.mother": {
        "positive": ("Your bond with your mother, and your own emotional security, are well supported.",
                     "Lean on that emotional foundation when life gets busy."),
        "negative": ("Your emotional wellbeing, and your mother's welfare, deserve extra attention.",
                     "Look after your mental rest and stay close to your mother."),
    },
    "family.father": {
        "positive": ("Your father and elders are likely to be a source of guidance and support.",
                     "Seek your father's or elders' advice on big decisions."),
    },

    # ---------------- Travel ----------------
    "travel.foreign": {
        "positive": ("Foreign connections are strong in your chart: travel, work or life abroad, or international "
                     "dealings are likely to feature.",
                     "Keep your passport ready and seriously consider opportunities abroad."),
    },
    "travel.relocation": {
        "positive": ("You are likely to live away from your birthplace at some point, possibly for a long time.",
                     "Moving for study or work is supported; plan it rather than resisting it."),
    },
    "travel.journeys": {
        "positive": ("You enjoy travel and are likely to travel often, including pilgrimages or long journeys.",
                     "Use travel for learning and growth."),
    },
    "travel.rooted": {
        "neutral": ("You have strong roots; even if you travel, you are likely to return home or stay connected to it.",
                    "Travel freely; home will remain your anchor."),
    },

    # ---------------- Children ----------------
    "children.blessing": {
        "positive": ("Matters of children are traditionally well supported, and children can bring you joy.",
                     "Enjoy the role of parent or mentor; it suits you."),
        "mixed": ("Children may be independent or active, and raising them takes effort.",
                  "Give children both freedom and structure."),
    },
    "children.patience": {
        "negative": ("Tradition advises patience in matters of children. This is not a medical prediction.",
                     "If this matters to you, take it as a reminder to plan and to seek proper medical advice, not astrology."),
    },
    "children.d7": {
        "positive": ("Your children's chart (D7) is supportive.", "No special action is needed."),
        "negative": ("Your children's chart (D7) suggests patience. This is a traditional, symbolic indication only.",
                     "Treat it as a gentle note, not a worry."),
    },

    # ---------------- Health ----------------
    "health.vitality": {
        "positive": ("You have good vitality and recover well.", "Keep active; your body responds well to exercise."),
    },
    "health.attention": {
        "negative": ("Tradition suggests paying more attention to your health and energy.",
                     "Prioritise sleep, regular check-ups and a steady routine. This is not medical advice."),
    },
    "health.resilience": {
        "positive": ("You have good resilience and resistance; you tend to bounce back.",
                     "Build on it with healthy habits."),
    },
}

# Where the main house lord of each area sits -> what it means for you.
LORD_YOU = {
    "career": {  # 10th lord
        1: "Your career is closely tied to who you are. You do best in work you can shape yourself, and you are likely to become known personally for what you do.",
        2: "Your career is closely linked to earning, family and speech. Finance, food, teaching, sales or family business may suit you.",
        3: "Your career benefits from initiative, communication and skills. Media, writing, sales, marketing, travel or your own enterprise suit you, and you may change jobs more than most.",
        4: "Your work is linked to home, property, education, land or vehicles, and you may prefer work close to home or in your homeland.",
        5: "Your career grows through intelligence and creativity. Teaching, advising, finance, creative fields or strategy suit you.",
        6: "Your career involves service, competition or problem-solving. Healthcare, law, administration, defence or consulting suit you.",
        7: "Your career grows through partnerships and dealing with the public. Business, trade, client-facing roles or partnerships suit you, and work may involve travel.",
        8: "Your career may have sudden turns. Research, investigation, insurance, finance, crisis work or anything involving hidden or deep matters can suit you.",
        9: "Your career is connected to ethics, higher learning and mentors. Law, teaching, advisory, religious or international work suit you, and good fortune supports your work.",
        10: "Your career is a strong and stable pillar of your life. You can build authority and recognition in your chosen field.",
        11: "Your career is strongly linked to income, networks and achieving your goals. Large organisations, networks and client relationships help you rise.",
        12: "Your work may take you abroad, into foreign companies or into institutions such as hospitals, NGOs or research. Some of your best work may happen behind the scenes.",
    },
    "wealth": {  # 2nd lord
        1: "You build wealth mainly through your own effort and personality.",
        2: "You have a natural ability to save and build family wealth.",
        3: "Your money comes through your skills, communication and initiative.",
        4: "Property, land and family assets are important parts of your wealth.",
        5: "Your intelligence and education are your main sources of wealth; careful investments can work for you.",
        6: "You earn through service or competitive work. Be careful with loans and lending.",
        7: "Your finances are tied to your partner or business partnerships, so choose partners carefully.",
        8: "Your savings may rise and fall; inheritance or joint money may play a role. Keep good financial discipline.",
        9: "Luck, your father or mentors help your finances; wealth tends to come through right action.",
        10: "Your career is your main source of wealth.",
        11: "Your savings and income support each other, a good combination for steady wealth.",
        12: "Spending can easily exceed saving, possibly on family, travel or causes. Income from abroad is also possible.",
    },
    "marriage": {  # 7th lord
        1: "Your partner is likely to have a big influence on your life direction; relationships shape who you become.",
        2: "Marriage is connected with family and finances, and your partner may support your wealth.",
        3: "Your partner is likely to be energetic and enterprising, and you may meet through communication, travel or siblings.",
        4: "Marriage is likely to bring domestic happiness, and you may build a home together.",
        5: "Love and romance play a strong role; you may marry for love, and your partner is likely to be intelligent.",
        6: "Partnership asks for patience and fairness; small misunderstandings need to be handled early.",
        7: "Marriage is a strong, stable area for you, and you are likely to find a capable partner.",
        8: "Marriage may bring big changes; joint finances and trust need careful handling.",
        9: "Your fortune is likely to grow after marriage, and your partner may be principled or come from a respected background.",
        10: "Your partner may support or share in your career; you could even work together.",
        11: "Marriage brings gains and a wide social circle.",
        12: "Your partner may come from a distant place or culture, or you may live abroad together; there may be periods of distance.",
    },
    "education": {  # 5th lord
        1: "Learning is part of who you are; you are naturally curious and intelligent.",
        2: "Your education is likely to turn into skill with words, numbers or teaching.",
        3: "You are a hands-on learner who does well in practical, skills-based or communication subjects.",
        4: "You learn best in a stable, supportive environment, and formal education suits you.",
        5: "You have a sharp intelligence and a good memory, with natural academic ability.",
        6: "Studies may meet obstacles, but you do well in competitive exams and disciplined preparation.",
        7: "You learn best through discussion, mentors and study partners; subjects involving people, business or law suit you.",
        8: "Your education may be non-linear, and you may be drawn to research or deep subjects.",
        9: "Higher education and good teachers are strongly supported; you could study to an advanced level.",
        10: "Your education is likely to lead directly to your profession.",
        11: "You are likely to achieve your academic goals and benefit from your education.",
        12: "You may study abroad or away from home; you have an imaginative mind that needs focus.",
    },
    "family": {  # 4th lord
        1: "Home and comfort are central to your identity, and you are likely to be close to your mother.",
        2: "You come from, or will build, a supportive family with shared resources.",
        3: "You may move home a few times and build your comfort through your own effort.",
        4: "You have a strong foundation at home, with property and contentment well supported.",
        5: "Home life is connected with learning and children; a happy family home is supported.",
        6: "Home life may involve some disputes or responsibilities, which can be handled with patience.",
        7: "Your partner brings comfort to your home, and property may come through partnership.",
        8: "You may change residence several times, and domestic peace needs care.",
        9: "Your parents' blessings and good fortune support your home life.",
        10: "Your home and career are connected; you may work from home or in a family field.",
        11: "Property and family bring gains.",
        12: "You are likely to live away from your birthplace and to spend on your home.",
    },
    "travel": {  # 12th lord
        1: "Travel and foreign experiences shape who you are; you have a restless, exploring side.",
        2: "Spending on family or travel may affect savings; foreign income is possible.",
        3: "You are likely to make frequent short trips, and siblings may live far away.",
        4: "You are likely to live away from your birthplace at some stage.",
        5: "You may study abroad or have children who live abroad.",
        6: "Foreign work in service or competitive fields is possible.",
        7: "Your partner may be from abroad, or you may live abroad together.",
        8: "You have an interest in deep, hidden or spiritual subjects, and foreign matters may involve sudden changes.",
        9: "You are likely to travel far, including pilgrimage, foreign study or long journeys.",
        10: "Your career may take you abroad or into foreign companies.",
        11: "You may gain through foreign connections and international networks.",
        12: "Foreign lands, retreat and spiritual life are strongly linked to your life path.",
    },
    "health": {  # 1st lord
        1: "Your health and energy are largely in your own hands, and you have a resilient constitution.",
        2: "Diet and family habits strongly affect your health.",
        3: "Activity and effort keep you healthy; you have good stamina.",
        4: "Emotional peace and a calm home are key to your wellbeing.",
        5: "A positive mind and creative outlets support your health.",
        6: "Healthy daily routines matter a lot for you; you can overcome illness with discipline.",
        7: "Your partner and relationships affect your wellbeing.",
        8: "You need to look after your health and avoid unnecessary risks; regular check-ups are wise.",
        9: "Good fortune and a principled life support your wellbeing.",
        10: "Work stress can affect your health, so balance ambition with rest.",
        11: "You generally have good recovery and a supportive social life.",
        12: "Rest, sleep and quiet time are essential for your health.",
    },
}

AREA_LORD_HOUSE = {"career": 10, "wealth": 2, "marriage": 7, "education": 5, "family": 4, "travel": 12, "health": 1}

PLANET_YOU = {
    "Sun": {
        "strong": "You have a strong sense of self and natural authority. People tend to look to you to lead, and recognition comes more easily to you than to most.",
        "steady": "Your confidence is steady. You can lead when needed, though you may not always seek the spotlight.",
        "needs support": "Confidence and self-belief may need conscious building. You may sometimes feel overshadowed or doubt yourself. Small wins and responsibility help.",
    },
    "Moon": {
        "strong": "You are emotionally steady and nurturing, and people feel comfortable around you.",
        "steady": "Your emotions are generally balanced, with normal ups and downs.",
        "needs support": "You can be emotionally sensitive and may take things to heart or feel anxious at times. Rest, routine and supportive people make a big difference for you.",
    },
    "Mars": {
        "strong": "You have plenty of drive, courage and energy. You act decisively and can push through obstacles.",
        "steady": "You have a good level of energy and courage when it counts.",
        "needs support": "Energy and assertiveness may come and go; you may avoid conflict or struggle to push for what you want. Exercise and clear goals help.",
    },
    "Mercury": {
        "strong": "You have a quick, sharp mind and communicate well, a real advantage in study, business and work.",
        "steady": "Your thinking and communication are solid and practical.",
        "needs support": "You may overthink, worry or find it harder to express yourself at times. Writing things down and structured learning help.",
    },
    "Jupiter": {
        "strong": "You are blessed with wisdom, optimism and good fortune. Teachers and mentors help you, and you tend to make good decisions.",
        "steady": "You have sound judgement and receive reasonable support from teachers and elders.",
        "needs support": "Good advice and guidance matter more for you. Seek out mentors and be careful with over-optimism or poor counsel.",
    },
    "Venus": {
        "strong": "You enjoy beauty, comfort and relationships, and attract affection easily. Life's pleasures come to you readily.",
        "steady": "You have a balanced approach to love, comfort and enjoyment.",
        "needs support": "Relationships and enjoyment may need more conscious effort; you may feel unappreciated at times. Make time for joy and affection.",
    },
    "Saturn": {
        "strong": "You are disciplined, patient and hard-working, and what you build lasts. Responsibility suits you.",
        "steady": "You can be disciplined when needed. Results come with steady effort.",
        "needs support": "Delays, pressure or heavy responsibilities may feel frequent. Patience is your key lesson; things improve with time and consistency.",
    },
    "Rahu": {
        "steady": "You have strong ambitions and are drawn to the new, the foreign or the unconventional, especially in the area of life where Rahu sits.",
    },
    "Ketu": {
        "steady": "You have a natural, almost effortless ability in some area, and some detachment from it; spiritual or research interests may appear.",
    },
}

# Plain short phrase for how each planet's energy expresses in a house.
PLANET_ENERGY = {
    "Sun": "your confidence and need for recognition", "Moon": "your emotions and need for comfort",
    "Mars": "your drive and ambition", "Mercury": "your thinking and communication",
    "Jupiter": "your luck, wisdom and growth", "Venus": "your love, pleasure and creativity",
    "Saturn": "your hard work and responsibilities", "Rahu": "your strongest ambitions and cravings",
    "Ketu": "your detachment and natural, past-life skills",
}

HOUSE_LIFE = {
    1: "your personality and how you present yourself", 2: "money, family and the way you speak",
    3: "your courage, hobbies, communication and siblings", 4: "your home, mother and emotional base",
    5: "your studies, creativity, romance and children", 6: "your daily work, health routines and competition",
    7: "your marriage and partnerships", 8: "change, research, shared money and hidden matters",
    9: "your beliefs, luck, teachers and long journeys", 10: "your career and public reputation",
    11: "your income, friends and ambitions", 12: "spending, foreign lands, rest and spirituality",
}

# For the running Dasha: what an activated house means for you right now.
PERIOD_HOUSE_YOU = {
    1: "a focus on yourself: your health, image and personal direction",
    2: "a focus on money, savings and family matters",
    3: "a focus on effort, communication, short travel, courage and new initiatives",
    4: "a focus on home, property, your mother and emotional security",
    5: "a focus on studies, creativity, romance, children and good decisions",
    6: "a focus on work, competition, health routines and solving problems",
    7: "a focus on marriage, partnerships and dealing with others",
    8: "a period of change, research or unexpected events, and shared finances",
    9: "a focus on luck, higher learning, travel, teachers and your beliefs",
    10: "a focus on career, responsibility and your public standing",
    11: "a focus on income, gains, friendships and achieving goals",
    12: "a focus on expenses, travel abroad, rest and inner life",
}

TONE_ADVICE = {
    "supportive": "Tradition sees this as a supportive time: a good period to take initiative in these areas.",
    "mixed": "Tradition sees this as a mixed time: progress is possible with steady, careful effort.",
    "demanding": "Tradition sees this as a demanding time: be patient, avoid big risks and focus on consolidating.",
}

LAGNA_YOU = [
    "You are at your best when you can take initiative and act. You get bored with routine, so choose paths with challenge and movement.",
    "You are at your best with stability and time to build things properly. You value comfort and loyalty; avoid letting stubbornness block change.",
    "You are at your best when your mind is engaged and you can talk, learn and connect. Variety keeps you motivated; focus is the skill to build.",
    "You are at your best when you feel emotionally secure and can care for others. Protect your energy and do not hold on to old hurts.",
    "You are at your best when you can lead, create and be appreciated. Generosity is your strength; be open to feedback.",
    "You are at your best when you can improve things, solve problems and be useful. Watch out for over-worrying and perfectionism.",
    "You are at your best in partnership and when things feel fair and harmonious. Make decisions without waiting for everyone's approval.",
    "You are at your best when you can go deep and transform difficult situations. Trust a few people fully rather than guarding against everyone.",
    "You are at your best when you have freedom, a purpose and room to learn and explore. Temper bluntness with tact.",
    "You are at your best with clear goals, structure and responsibility; you mature into success. Remember to rest and enjoy the journey.",
    "You are at your best working on ideas that matter and with like-minded people. Let others in emotionally.",
    "You are at your best when you can be compassionate, creative and connected to something larger. Set boundaries so you do not get drained.",
]
