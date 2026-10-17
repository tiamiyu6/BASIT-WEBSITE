"""JUNE 12: THE ELECTION NIGERIA STOLE: scene list.

Every shot is real material: a photo, a newspaper, an archive clip, or a typed document.
A scene is either an archive clip with its own sound (`clip`) or narration (`text`) with shots.
Shot timing: `at` = sentence index (int) or (sentence index, fraction into that sentence).

Shot kinds
  photo(file)        photograph; full-frame when it is wide and sharp enough, otherwise a print on the desk
  paper(file)        newspaper page dropped onto the desk, camera pushes toward `focus`
  typed(lines)       typewriter on paper; a line starting with ~ is typed then struck through,
                     a line starting with ! is stamped in red; (line, at) pairs appear at that sentence
  footage(file, a, b)  silent archive footage under the narration
  tally()            the 1993 result sheet with counting numbers
"""

PH = "june12/photos/"
BR = "photos/broll/"
CL = "june12/clips/"


def photo(file, at=0, focus=(0.5, 0.42), move="in", label=None, credit=None, grade=None):
    return dict(kind="photo", file=file, at=at, focus=focus, move=move, label=label, credit=credit, grade=grade)


def paper(file, at=0, focus=(0.5, 0.3), label=None, credit=None):
    return dict(kind="paper", file=file, at=at, focus=focus, label=label, credit=credit)


def typed(lines, at=0, big=False):
    return dict(kind="typed", lines=lines, at=at, big=big)


def footage(file, a, b, at=0, label=None):
    return dict(kind="footage", file=file, a=a, b=b, at=at, label=label)


def tally(at=0):
    return dict(kind="tally", at=at)


def chapter(n, name):
    return dict(id=f"ch{n}", chapter=name, card=(f"CHAPTER {n}", name), text="", shots=[])


def clip(id, file, a, b, label, chapter=""):
    return dict(id=id, chapter=chapter, clip=(CL + file, a, b), label=label, text="", shots=[])


def sc(id, text, shots, chapter="", hold=0.9, mood=None):
    return dict(id=id, chapter=chapter, text=text, shots=shots, hold=hold, mood=mood)


S = [
    # ------------------------------------------------------------------ COLD OPEN
    clip("c0_ibb", "ibb_annulment_1993.mp4", 0.45, 8.9, "General Ibrahim Babangida · national broadcast, June 1993"),
    sc("c0_free", "Free. Fair. Peaceful. Those were his words.",
       [photo(PH + "ibb-broadcast-1993.jpg", 0, focus=(0.55, 0.45), grade="bw")], mood="cold"),
    sc("c0_vote", "Fourteen million Nigerians voted that day. Muslims and Christians. North and South. "
                  "And for once, they all chose the same man. His name was Moshood Kashimawo Olawale Abiola.",
       [photo(PH + "open-ballot-queue-1993.jpg", 0, focus=(0.5, 0.45), label="Voters queue in the open, 1993"),
        photo(PH + "mko-votes-june12.jpg", 3, focus=(0.6, 0.35)),
        photo(BR + "abiola-portrait.jpg", 4, focus=(0.5, 0.35), label="Chief M.K.O. Abiola")], mood="cold"),
    sc("c0_tease", "What came next would break a nation's heart. An election, cancelled by one man in uniform. "
                   "A wife, shot dead in her car on a Lagos road. A dictator who died in his own palace. "
                   "And a prisoner who collapsed one month later, after a cup of tea.",
       [paper(PH + "paper-court-stops-election-1993.jpg", 1, focus=(0.3, 0.25)),
        photo(PH + "kudirat-car-1996.jpg", 2, focus=(0.5, 0.5)),
        paper(PH + "paper-abacha-dies-1998.jpg", 3, focus=(0.5, 0.12)),
        paper(PH + "paper-abiola-poisoned-1998.jpg", 4, focus=(0.3, 0.45))], mood="tension"),
    sc("c0_this", "This is the story of June 12. The day Nigeria got it right, and the men who made sure it didn't count.",
       [photo(PH + "mko-votes-june12.jpg", 0, focus=(0.6, 0.3), move="in")], mood="tension", hold=0.4),
    dict(id="logo", chapter="", logo=True, text="", shots=[]),

    # ------------------------------------------------------------------ 1
    chapter(1, "KASHIMAWO"),
    sc("c1_birth", "In nineteen thirty-seven, in the town of Abeokuta, a woman gave birth to her twenty-third child. "
                   "None of the twenty-two before him had survived.",
       [photo(PH + "abeokuta-panorama.jpg", 0, focus=(0.5, 0.5), move="right", label="Abeokuta, Ogun State"),
        photo(PH + "olumo-boulders.jpg", 1, focus=(0.5, 0.5), move="left")], "KASHIMAWO", mood="home"),
    sc("c1_name", "So his parents gave him a name that was half a prayer. Kashimawo. Let us wait and see.",
       [typed(["KASHIMAWO", "", "“let us wait and see”"], 0, big=True)], "KASHIMAWO", mood="home"),
    sc("c1_work", "He lived. And he worked. As a boy, he gathered firewood to sell before school. "
                  "At fifteen, he started a band, and sang at parties, for food and for money.",
       [photo(PH + "abeokuta-street-rock.jpg", 0, focus=(0.5, 0.4), label="Abeokuta today"),
        photo(PH + "young-mko-portrait.jpg", 2, focus=(0.5, 0.3), label="A young Moshood Abiola")], "KASHIMAWO", mood="home"),
    sc("c1_school", "A scholarship took him to Baptist Boys' High School in Abeokuta, and from there to the University of Glasgow, "
                    "where he qualified as an accountant.",
       [photo(PH + "young-mko-portrait.jpg", 0, focus=(0.5, 0.25), move="out")], "KASHIMAWO", mood="home"),
    sc("c1_empire", "He came home, and rose to run the African business of the American giant, ITT. "
                    "Then he built an empire of his own. Newspapers. An airline. Farms. Bakeries. Shipping. "
                    "By the nineteen-eighties, he was one of the richest men in Africa.",
       [photo(PH + "mko-laughing-bw.jpg", 0, focus=(0.35, 0.3)),
        paper(PH + "national-concord-1982.jpg", 2, focus=(0.3, 0.12), label="National Concord, founded by Abiola in 1980"),
        photo(BR + "abiola-portrait.jpg", 7, focus=(0.5, 0.35))], "KASHIMAWO", mood="rise"),
    sc("c1_give", "And he gave it away, in public. Schools, mosques and churches. Scholarships. Football clubs. "
                  "In nineteen eighty-eight, he was crowned Aare Ona Kakanfo of Yorubaland, its highest war title.",
       [photo(BR + "abiola-advert-1993.jpg", 0, focus=(0.5, 0.3)),
        typed(["AARE ONA KAKANFO", "OF YORUBALAND", "", "1988"], 4, big=True)], "KASHIMAWO", mood="rise"),
    sc("c1_end", "Money can buy many things in Nigeria. In nineteen ninety-three, MKO Abiola wanted the one thing it cannot buy. A mandate.",
       [photo(BR + "abiola-victory-1993.jpg", 0, focus=(0.5, 0.35), move="in")], "KASHIMAWO", mood="rise", hold=0.5),

    # ------------------------------------------------------------------ 2
    chapter(2, "TWO PARTIES BUILT BY SOLDIERS"),
    sc("c2_ibb", "General Ibrahim Babangida took power in a coup in nineteen eighty-five. He promised to hand over to civilians. "
                 "Then he moved the date. Then he moved it again.",
       [photo(PH + "ibb-broadcast-1993.jpg", 0, focus=(0.55, 0.45), label="General Ibrahim Babangida, military president 1985–1993"),
        typed([("HANDOVER TO CIVILIAN RULE:", 1), ("~1990", 2), ("~1992", 3), ("~JANUARY 1993", 3), ("27 AUGUST 1993", 3)], 1)],
       "TWO PARTIES", mood="tension"),
    sc("c2_parties", "Instead of letting Nigerians form their own parties, the military created two. "
                     "It wrote their manifestos, built their offices, and paid their bills. "
                     "One was a little to the left. The other, a little to the right.",
       [typed([("FEDERAL MILITARY GOVERNMENT", 0), ("REGISTERED POLITICAL PARTIES", 0), ("", 0),
               ("1. SOCIAL DEMOCRATIC PARTY (SDP)", 2), ("   “a little to the left”", 2), ("", 2),
               ("2. NATIONAL REPUBLICAN CONVENTION (NRC)", 3), ("   “a little to the right”", 3)], 0)],
       "TWO PARTIES", mood="tension"),
    sc("c2_banned", "In nineteen ninety-two, the presidential primaries were cancelled, and all twenty-three aspirants were banned.",
       [typed([("1992 PRESIDENTIAL PRIMARIES", 0), ("23 ASPIRANTS", 0), ("!CANCELLED", 0)], 0)], "TWO PARTIES", mood="tension"),
    sc("c2_a4", "Then came a new system, called Option A4. There was no secret ballot. "
                "Voters lined up behind the poster of the candidate they wanted, in full view, and were counted one by one.",
       [photo(PH + "open-ballot-queue-1993.jpg", 0, focus=(0.5, 0.45), label="Option A4: the open-ballot queue",
              credit="Citizen magazine, 1992")], "TWO PARTIES", mood="build"),
    sc("c2_jos", "At the party convention in Jos, in March nineteen ninety-three, Abiola defeated Babagana Kingibe. "
                 "Then he did something nobody expected. He chose Kingibe, a Muslim from Borno, as his running mate.",
       [photo(PH + "sdp-mko-poster-1993.jpg", 0, focus=(0.5, 0.35), label="SDP campaign advertisement, 1993"),
        photo(PH + "kingibe-portrait.jpg", 2, focus=(0.5, 0.35), label="Babagana Kingibe, running mate")], "TWO PARTIES", mood="build"),
    sc("c2_mm", "A Muslim-Muslim ticket. In a country where religion decides almost everything, Nigerians looked at it, and shrugged.",
       [typed([("SDP PRESIDENTIAL TICKET, 1993", 0), ("", 0), ("M.K.O. ABIOLA . . . . . . MUSLIM", 0),
               ("BABAGANA KINGIBE . . . . MUSLIM", 0)], 0)], "TWO PARTIES", mood="build"),
    sc("c2_hope", "His campaign was called Hope '93. His promise: farewell to poverty.",
       [photo(BR + "abiola-advert-1993.jpg", 0, focus=(0.5, 0.25), move="out")], "TWO PARTIES", mood="build"),
    sc("c2_tofa", "Against him stood Bashir Tofa, a businessman from Kano, for the NRC.",
       [photo(PH + "tofa-portrait.jpg", 0, focus=(0.5, 0.4), label="Bashir Tofa (1947–2022), NRC candidate")], "TWO PARTIES", mood="build"),

    # ------------------------------------------------------------------ 3
    chapter(3, "12 JUNE 1993"),
    sc("c3_court", "Two nights before the vote, a group called the Association for Better Nigeria went to court, late at night, "
                   "and got an order to stop the election.",
       [paper(PH + "paper-court-stops-election-1993.jpg", 0, focus=(0.3, 0.3))], "12 JUNE 1993", mood="tension"),
    sc("c3_vote", "The electoral commission ignored it. On Saturday, the twelfth of June, Nigeria voted.",
       [paper(PH + "concord-dday-1993.jpg", 0, focus=(0.5, 0.25), label="Weekend Concord, June 1993"),
        typed(["SATURDAY", "12 JUNE 1993"], 1, big=True)], "12 JUNE 1993", mood="hope"),
    sc("c3_peace", "There was no major violence. In town after town, voters stood in the open, in long, patient lines, "
                   "for the man they wanted.",
       [photo(PH + "open-ballot-queue-1993.jpg", 0, focus=(0.7, 0.4), move="left"),
        photo(PH + "mko-votes-june12.jpg", 1, focus=(0.55, 0.3), label="Abiola casts his vote, 12 June 1993")], "12 JUNE 1993", mood="hope"),
    sc("c3_count", "When the counting began, Nigeria saw something it had never seen before. "
                   "Abiola was winning in the South, and in the North. He won nineteen of thirty states, and Abuja. "
                   "He even won Kano, his opponent's home state.",
       [tally(0)], "12 JUNE 1993", mood="hope"),
    sc("c3_free", "Local and international observers called it peaceful and credible. "
                  "To this day, many call it the freest and fairest election in Nigeria's history.",
       [photo(PH + "mko-votes-june12.jpg", 0, focus=(0.55, 0.35), move="out")], "12 JUNE 1993", mood="hope"),
    sc("c3_wait", "Then, the announcements stopped. And Nigeria waited.",
       [typed([("NATIONAL ELECTORAL COMMISSION", 0), ("16 JUNE 1993", 0), ("", 0), ("!RESULTS SUSPENDED", 0)], 0)],
       "12 JUNE 1993", mood="cold", hold=1.4),

    # ------------------------------------------------------------------ 4
    chapter(4, "BAD FAITH"),
    sc("c4_annul", "On the twenty-third of June, nineteen ninety-three, the military government annulled the election. All of it.",
       [typed([("23 JUNE 1993", 0), ("PRESIDENTIAL ELECTION OF 12 JUNE", 0), ("", 0), ("!ANNULLED", 0)], 0)],
       "BAD FAITH", mood="dark"),
    clip("c4_ibb", "ibb_annulment_1993.mp4", 9.0, 18.1, "General Ibrahim Babangida · national broadcast, June 1993", "BAD FAITH"),
    clip("c4_mko", "mko_bad_faith_1993.mp4", 1.4, 27.2, "Chief M.K.O. Abiola responds, 1993", "BAD FAITH"),
    sc("c4_streets", "Lagos exploded. Students, market women and workers poured into the streets. "
                     "A young student union leader named Omoyele Sowore led marches against the annulment. "
                     "Soldiers and police opened fire. Human Rights Watch reported more than a hundred people killed.",
       [footage(CL + "protest_1993.mp4", 0, 4.9, 0, label="Protests in Lagos, 1993"),
        footage(CL + "sowore_protest_1993.mp4", 2.0, 25.0, 2, label="Student leader Omoyele Sowore, 1993"),
        photo(PH + "abacha-guard-inspection.jpg", 3, focus=(0.6, 0.3), grade="bw")], "BAD FAITH", mood="dark"),
    sc("c4_shonekan", "In August, Babangida stepped aside, and left an unelected interim government in charge. "
                      "In November, a Lagos court declared that government illegal. "
                      "One week later, the man who had stood quietly beside Babangida through it all, took power.",
       [typed([("26 AUG 1993 — BABANGIDA STEPS ASIDE", 0), ("10 NOV 1993 — COURT: INTERIM GOVT ILLEGAL", 1),
               ("17 NOV 1993 —", 2)], 0),
        photo(PH + "abacha-broadcast-1993.jpg", (2, 0.55), focus=(0.5, 0.4), grade="bw")], "BAD FAITH", mood="dark"),
    sc("c4_abacha", "General Sani Abacha.",
       [photo(PH + "abacha-uniform-portrait.jpg", 0, focus=(0.5, 0.35), label="General Sani Abacha, head of state 1993–1998")],
       "BAD FAITH", mood="dark", hold=1.6),

    # ------------------------------------------------------------------ 5
    chapter(5, "EPETEDO"),
    sc("c5_decl", "One year after the vote, on the eleventh of June, nineteen ninety-four, at Epetedo on Lagos Island, "
                  "Abiola stood before his supporters, and declared himself President of Nigeria.",
       [typed(["11 JUNE 1994", "EPETEDO, LAGOS ISLAND"], 0, big=True),
        photo(PH + "mko-response-1993.jpg", (0, 0.6), focus=(0.5, 0.4))], "EPETEDO", mood="resolve"),
    sc("c5_arrest", "Twelve days later, he was arrested, and charged with treason. "
                    "Two months after that, the regime banned his Concord newspapers. He was held in solitary confinement. "
                    "The regime offered him his freedom, on one condition. Give up the mandate. He refused. For four years, he refused.",
       [photo(PH + "mko-response-1993.jpg", 0, focus=(0.5, 0.4), grade="bw"),
        paper(PH + "concord-abiola-playing-with-fire.jpg", 1, focus=(0.5, 0.5), label="Concord newspapers: banned, August 1994"),
        photo(BR + "abiola-portrait.jpg", 4, focus=(0.5, 0.35), grade="bw")], "EPETEDO", mood="resolve"),
    sc("c5_kingibe", "His own running mate, Babagana Kingibe, had already joined Abacha's government, as foreign minister.",
       [photo(PH + "kingibe-portrait.jpg", 0, focus=(0.5, 0.35), label="Babagana Kingibe, Minister of Foreign Affairs 1993–1995")],
       "EPETEDO", mood="resolve"),
    sc("c5_nadeco", "Outside, a new coalition rose against the regime. NADECO, the National Democratic Coalition. "
                    "Old warriors like Chief Anthony Enahoro and Pa Abraham Adesanya. And a young senator from Lagos, named Bola Tinubu.",
       [photo(PH + "nadeco-key-figures.jpg", 0, focus=(0.5, 0.5), label="NADECO leaders"),
        photo(BR + "tinubu-young-sepia.jpg", 3, focus=(0.5, 0.35), label="Senator Bola Tinubu, 1990s")], "EPETEDO", mood="resolve"),
    sc("c5_strike", "Oil workers went on strike for Abiola, and brought the economy to its knees. "
                    "The regime broke the strike, and jailed its leaders.",
       [photo(PH + "abacha-broadcast.jpg", 0, focus=(0.5, 0.4), grade="bw"),
        photo(PH + "abacha-guard-inspection.jpg", 1, focus=(0.6, 0.35))], "EPETEDO", mood="dark"),
    sc("c5_soyinka", "The Nobel laureate Wole Soyinka escaped into exile, and from there, told the world what was happening in Nigeria. "
                     "In nineteen ninety-seven, the regime charged him with treason, in his absence.",
       [photo(PH + "soyinka-portrait.jpg", 0, focus=(0.5, 0.35), label="Wole Soyinka, Nobel laureate")], "EPETEDO", mood="resolve"),

    # ------------------------------------------------------------------ 6
    chapter(6, "KUDIRAT"),
    sc("c6_fight", "With her husband in a cell, Kudirat Abiola took up the fight. She supported the strikers. "
                   "She spoke to foreign journalists. She refused to be quiet.",
       [photo(PH + "kudirat-portrait.jpg", 0, focus=(0.5, 0.4), label="Alhaja Kudirat Abiola")], "KUDIRAT", mood="lament"),
    sc("c6_ambush", "On the fourth of June, nineteen ninety-six, her car was ambushed on a Lagos road. Gunmen opened fire. She was killed.",
       [typed(["4 JUNE 1996", "LAGOS"], 0, big=True),
        photo(PH + "kudirat-car-1996.jpg", 1, focus=(0.5, 0.5), grade="bw")], "KUDIRAT", mood="lament", hold=2.6),
    sc("c6_bury", "Thousands came to bury her.",
       [photo(PH + "kudirat-coffin-1996.jpg", 0, focus=(0.5, 0.4), grade="bw")], "KUDIRAT", mood="lament", hold=1.4),
    sc("c6_justice", "Years later, a soldier known as Sergeant Rogers confessed to firing the shots, and said he had acted on orders. "
                     "Abacha's chief security officer, Hamza al-Mustapha, was sentenced to death for her murder in twenty twelve. "
                     "In twenty thirteen, he was freed on appeal.",
       [typed([("SGT. BARNABAS JABILA (“ROGERS”)", 0), ("confessed to the shooting", 0), ("", 1),
               ("HAMZA AL-MUSTAPHA", 1), ("2012 — sentenced to death", 1), ("2013 — freed on appeal", 2)], 0)],
       "KUDIRAT", mood="lament"),
    sc("c6_end", "No one is in prison today, for the killing of Kudirat Abiola.",
       [photo(PH + "kudirat-portrait.jpg", 0, focus=(0.47, 0.42), move="in")], "KUDIRAT", mood="lament", hold=1.8),

    # ------------------------------------------------------------------ 7
    chapter(7, "JULY 1998"),
    sc("c7_abacha", "On the eighth of June, nineteen ninety-eight, Sani Abacha died suddenly, inside Aso Rock. "
                    "He was fifty-four. Officially, it was a heart attack.",
       [paper(PH + "paper-abacha-dies-1998.jpg", 0, focus=(0.5, 0.12), label="The Guardian, 9 June 1998"),
        photo(PH + "abacha-uniform-large.jpg", 1, focus=(0.5, 0.3), grade="bw")], "JULY 1998", mood="tension"),
    sc("c7_loot", "Behind him, he left billions of dollars in looted money. Nigeria is still recovering it today.",
       [paper(PH + "paper-abacha-son-n2bn-1998.jpg", 0, focus=(0.4, 0.3), label="P.M. News, July 1998")], "JULY 1998", mood="tension"),
    sc("c7_wait", "General Abdulsalami Abubakar took over. And Nigeria waited for Abiola to walk free.",
       [paper(PH + "paper-abacha-dies-1998.jpg", 0, focus=(0.4, 0.88))], "JULY 1998", mood="tension"),
    sc("c7_tea", "On the seventh of July, nineteen ninety-eight, Abiola met an American delegation, led by Under Secretary of State "
                 "Thomas Pickering, with a young diplomat named Susan Rice. Tea was served. He took a sip. "
                 "Moments later, he collapsed, and he died. He was sixty years old.",
       [typed([("7 JULY 1998", 0), ("", 0), ("U.S. DELEGATION:", 0), ("THOMAS PICKERING", 0), ("SUSAN RICE", 0)], 0),
        photo(PH + "mko-response-1993.jpg", 1, focus=(0.5, 0.4), grade="bw", move="in")], "JULY 1998", mood="lament", hold=1.6),
    sc("c7_autopsy", "A team of international pathologists said he died of heart disease. "
                     "Many Nigerians, and many in his own family, never believed it.",
       [paper(PH + "paper-abiola-poisoned-1998.jpg", 0, focus=(0.3, 0.45), label="P.M. News, August 1998")], "JULY 1998", mood="lament"),
    clip("c7_burial", "mko_burial_1998.mp4", 0.8, 25.4, "BBC-style news report on Abiola's burial, July 1998", "JULY 1998"),

    # ------------------------------------------------------------------ 8
    chapter(8, "VINDICATION"),
    sc("c8_return", "The exiles came home. In nineteen ninety-nine, the soldiers finally handed power back to civilians.",
       [photo(PH + "soyinka-welcome-home-1998.jpg", 0, focus=(0.5, 0.4), label="“Welcome Home Kongi”: Soyinka returns, 1998")],
       "VINDICATION", mood="dawn"),
    sc("c8_2018", "In June twenty eighteen, twenty-five years after the election, President Muhammadu Buhari made the twelfth of June "
                  "Nigeria's Democracy Day. He awarded Abiola the GCFR, the country's highest honour, normally reserved for presidents. "
                  "The national stadium in Abuja now carries his name.",
       [photo(PH + "democracy-day-2018-honours.jpg", 0, focus=(0.5, 0.4), label="June 12 honours, Abuja, 2018", credit="Premium Times / NAN"),
        typed(["GCFR", "Grand Commander of the Order", "of the Federal Republic", "", "CHIEF M.K.O. ABIOLA", "(posthumous)"], 1),
        typed(["MOSHOOD ABIOLA", "NATIONAL STADIUM", "ABUJA"], 2, big=True)], "VINDICATION", mood="dawn"),
    sc("c8_ibb", "And in February twenty twenty-five, launching his memoir, Ibrahim Babangida finally admitted what Nigeria had known "
                 "for thirty-two years. Abiola won. June 12 happened under my watch, he said. I accept full responsibility. "
                 "In the same book, he claimed the annulment was announced without his permission. "
                 "The Abiola family said the book reopened old wounds.",
       [photo(PH + "ibb-broadcast-1993.jpg", 0, focus=(0.55, 0.45), grade="bw"),
        typed(["“June 12 happened under my watch.", "I accept full responsibility.”", "",
               "— Ibrahim Babangida, February 2025"], 2)], "VINDICATION", mood="dawn"),
    sc("c8_today", "Today, the young NADECO senator from Lagos is the President of Nigeria.",
       [photo(BR + "blinken-tinubu-2024.jpg", 0, focus=(0.5, 0.35), label="President Bola Tinubu")], "VINDICATION", mood="dawn"),
    sc("c8_close", "The results of June 12 were never officially completed. Abiola was never sworn in. "
                   "But every year, on the twelfth of June, Nigeria stops to remember the one time it chose, together.",
       [photo(PH + "mko-votes-june12.jpg", 0, focus=(0.6, 0.3)),
        photo(PH + "open-ballot-queue-1993.jpg", 2, focus=(0.5, 0.45), move="out")], "VINDICATION", mood="dawn"),
    sc("c8_final", "Kashimawo. Let us wait and see. Nigeria is still waiting.",
       [photo(PH + "young-mko-portrait.jpg", 0, focus=(0.5, 0.3), move="in")], "VINDICATION", mood="dawn", hold=2.0),
    sc("c8_cta", "Was June 12 the closest Nigeria ever came? Tell me what you think in the comments. "
                 "And if you haven't seen it yet, watch our documentary on Bola Tinubu. Jagaban.",
       [dict(kind="endcard", at=0)], "", mood="dawn", hold=4.0),
]
