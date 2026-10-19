"""MR MONEY: The Asake Story. Scene list for the Naija Untold documentary.

Every scene: id, narration text, shots (what is on screen), mood (music cue).
Shot kinds: photo, kin (kinetic words), quote, stat, phone, names, chart.
Scene kinds without narration: card (Korty-style chapter card), logo, end.
`at` = sentence index (or (index, fraction)) when a shot cuts in.
"""
P = "mrmoney/photos/"
BR = "photos/broll/"


def photo(f, at=0, focus=(0.5, 0.45), grade=None, move="in", tag=None, credit=None, strip=None):
    return dict(kind="photo", file=f, at=at, focus=focus, grade=grade, move=move, tag=tag, credit=credit, strip=strip)


def kin(words, at=0, style="stack", bg=None, fx=None):
    """words: list of str or (str, at). style: stack | big | list. fx="naira": money rain over it"""
    return dict(kind="kin", words=words, at=at, style=style, bg=bg, fx=fx)


def quote(text, who, at=0, bg=None):
    return dict(kind="quote", text=text, who=who, at=at, bg=bg)


def stat(value, label, at=0, prefix="", suffix="", count=True, bg=None, fx=None):
    return dict(kind="stat", value=value, label=label, at=at, prefix=prefix, suffix=suffix, count=count, bg=bg, fx=fx)


def phone(msgs, at=0):
    """msgs: list of (side, text, when, at). side 'out' = Asake, 'in' = reply. text None = unreadable bubble."""
    return dict(kind="phone", msgs=msgs, at=at)


def chart(rows, at=0, title=""):
    return dict(kind="chart", rows=rows, at=at, title=title)


def clip(name, at=0, mode="scope", tag=None, speed=1.0, start=0.0, dark=0.0):
    """archive footage (see archive.py). mode: scope (letterboxed, full width) | tv (old television in a dark room)"""
    return dict(kind="clip", name=name, at=at, mode=mode, tag=tag, speed=speed, start=start, dark=dark)


def three(name, at=0, start=0.0, tag=None, speed=1.0):
    """a rendered 3D sequence (three/shots.py)"""
    return dict(kind="three", name=name, at=at, start=start, tag=tag, speed=speed)


def arch(id, name, subs=(), mood=None, picture=None, who="FROM 'ASAKE UNFILTERED'"):
    """an archive moment: the clip plays with its own sound, the narrator steps back"""
    return dict(id=id, archive=name, subs=list(subs), mood=mood, picture=picture, who=who)


def sc(id, text, shots, mood="groove", hold=0.7, **kw):
    return dict(id=id, text=text, shots=shots, mood=mood, hold=hold, **kw)


def card(id, word, sub, mood=None, color="gold"):
    return dict(id=id, card=dict(word=word, sub=sub, color=color), mood=mood)


ASK1 = P + "asake_toronto_1.png"
ASK2 = P + "asake_toronto_2.png"
ASK3 = P + "asake_toronto_3.png"
ASK4 = P + "asake_toronto_4.png"
CR_ASK = "Mensah Memories / CC BY 3.0"

S = [
    # ---------------------------------------------------------------- COLD OPEN: the boy on the floor
    sc("o1", "September 2022. Somewhere in Lagos, a boy is lying on the floor of his father's parlour.",
       [three("phone")], mood="night", hold=0.4),
    sc("o2", "WAEC is finished. JAMB is finished. And he has no idea what comes next.",
       [three("slips")], mood="night", hold=0.5),
    sc("o3", "Then a song comes on. And for the first time in a long time, he feels something. Hope.",
       [three("phone", start=2.0, speed=0.6), clip("smile", at=2, mode="tv", speed=0.5)], mood="night", hold=0.8),
    sc("o4", "The album is called Mr Money with the Vibe. The man who made it was once told no, by his own father.",
       [three("vinyl"), photo(ASK1, at=1, focus=(0.5, 0.35), grade="bw", strip=True, credit=CR_ASK)], mood="build", hold=0.4),
    sc("o5", "This is the story of how a stubborn boy from Lagos became Mr Money. And why millions of people, like that boy on the floor, feel lifted by his music.",
       [clip("fireworks"), clip("stage", at=1, start=7.0)], mood="build", hold=0.3),
    dict(id="logo", logo=True, mood="hit"),

    # ---------------------------------------------------------------- 1 OLOLADE
    card("c1", "OLOLADE", "Lagos  ·  1995", mood="groove"),
    sc("a1", "He was born Ahmed Ololade, on the thirteenth of January, 1995, in Lagos.",
       [photo(BR + "victoria-island-2014.jpg", focus=(0.5, 0.5), grade="warm", tag="Lagos  ·  13 January 1995", credit="OpenUpEd / CC BY 2.0"),
        kin(["AHMED", "OLOLADE"], at=(0, 0.3), style="name")], mood="groove"),
    sc("a2", "In Yoruba, Ololade means wealth has arrived. Long before anyone called him Mr Money, his own name was already saying it.",
       [photo(P + "naira_1000.jpg", focus=(0.5, 0.5), grade="gold", credit="Shardayyy / CC BY 2.0"),
        kin([("OLÁ", (0, 0.2)), ("wealth", (0, 0.2)), ("DÉ", (0, 0.55)), ("has arrived", (0, 0.55))], style="meaning"),
        kin([("MR MONEY", 1)], style="big", fx="naira")], mood="groove"),
    sc("a3", "The name the world knows him by is Asake. To most Nigerians, that is a woman's name. Many reports say he took it from his mother.",
       [kin([("ASAKE", 0)], style="name1"), photo(ASK2, at=2, focus=(0.5, 0.35), grade="bw", strip=True, credit=CR_ASK)], mood="groove"),
    sc("a4", "He trained as a performer, a dancer and an actor. And from very early, the people around him noticed one thing about him. A thing that would one day cost him his home.",
       [clip("redstage", tag="On stage, before the fame"), clip("rehearsal", at=2)], mood="groove", hold=0.4),

    # ---------------------------------------------------------------- 2 GIRAN
    card("c2", "GIRAN", "In Yoruba: stubborn", mood="fuji", color="red"),
    sc("g1", "They called him Giran. In Yoruba, it means stubborn.",
       [clip("stubborn", mode="tv"), kin([("GIRAN", 1), ("= STUBBORN", (1, 0.5))], style="define")], mood="fuji"),
    sc("g2", "At fifteen, he wanted music. His father did not. So he left home.",
       [kin([("15", 0), ("MUSIC?", 0), ("NO.", 1), ("HE LEFT HOME.", 2)], style="tick")], mood="fuji", hold=0.5),
    sc("g3", "Years later, he would laugh about it. The father who gave birth to me, he said, is more stubborn than I am.",
       [clip("beanie", mode="tv"), quote("The father who gave birth to me is more stubborn than I am.", "ASAKE  ·  Flow With Korty, 2026 (translated)", at=1)], mood="fuji"),
    sc("g4", "His mother had a different plan. She gathered money, and got him an international passport, to study in the United Kingdom.",
       [three("passport")], mood="fuji"),
    sc("g5", "He said no. He wanted to stay in Nigeria. It took the Yoruba actor Lala to convince her to let him go to Obafemi Awolowo University instead. That one stubborn choice would set everything else in motion.",
       [kin([("NO.", 0)], style="big"),
        photo(P + "oau_gate.jpg", at=2, focus=(0.5, 0.5), grade="warm", tag="Obafemi Awolowo University  ·  Ile-Ife", credit="jollofandmalt / CC BY 2.0")], mood="fuji"),

    # ---------------------------------------------------------------- 3 ILE-IFE
    card("c3", "ILE-IFE", "Theatre & Performing Arts", mood="night"),
    sc("i1", "At OAU, he studied Theatre and Performing Arts. He learned the stage, long before the stage knew his name.",
       [photo(P + "oau_oduduwa.jpg", focus=(0.5, 0.5), grade="warm", tag="OAU campus  ·  Ile-Ife", credit="jollofandmalt / CC BY 2.0"),
        clip("spot", at=1)], mood="night"),
    sc("i2", "In 2018, he signed with a small label called TFT Records, and released songs like Kanipe. Almost nobody noticed.",
       [photo(P + "lagos_street2.jpg", grade="night", credit="oneVillage Initiative / CC BY-SA 2.0"), kin([("2018", 0), ("TFT RECORDS", 0), ("KANIPE", 0), ("· · ·", 1)], style="stack")], mood="night"),
    sc("i3", "Then, in 2020, he put out a song with a title that sounded more like a promise than a fact. Mr Money.",
       [photo(P + "naira_500.jpg", grade="gold", credit="Shardayyy / CC BY 2.0"), kin([("2020", 0), ("MR MONEY", (0, 0.5))], style="promise", fx="naira")], mood="night", hold=0.9),
    sc("i4", "That same year, he started sending messages to the one man he believed could change his life. Olamide, the boss of YBNL.",
       [photo(P + "lagos_traffic.jpg", focus=(0.5, 0.5), grade="night", tag="Lagos  ·  2020", credit="dolapo / CC BY-SA 2.0"), kin([("OLAMIDE", 1), ("BOSS OF YBNL", 1)], style="name")], mood="night"),
    sc("i5", "By Asake's own account, he texted, and he begged, for help. And for a long time, there was no reply. Until one song changed everything.",
       [phone([("out", None, "2020", 0), ("out", None, "2020", (0, 0.5)), ("out", None, "2021", 1), ("out", None, "2021", (1, 0.4))])],
       mood="night", hold=1.2),

    # ---------------------------------------------------------------- 4 2022
    card("c4", "2022", "The takeover", mood="groove"),
    sc("y1", "Then he made a song called Omo Ope. Olamide heard it before it came out, and jumped on it with a verse of his own.",
       [photo(P + "lagos_street2.jpg", grade="warm", credit="oneVillage Initiative / CC BY-SA 2.0"), kin([("OMO OPE", 0), ("feat. OLAMIDE", 1)], style="track")], mood="groove"),
    sc("y2", "And, as Asake tells it, the text finally came back. Asake, we have to see.",
       [phone([("out", None, "2020", 0), ("out", None, "2021", 0), ("in", "Asake, we have to see.", "2022", 1)])], mood="groove", hold=1.0),
    sc("y3", "In February 2022, Olamide told the world. Welcome to YBNL.",
       [photo(P + "crowd2.jpg", grade="bw", credit="Neon Tommy / CC BY-SA 2.0"), kin([("@asakemusic", 0), ("welcome to #YBNL", (0, 0.6))], style="post")], mood="groove"),
    arch("ar1", "belief", [(0.0, 3.5, "I will show you this guy when we present him to the world."),
                           (3.8, 9.2, "They will never have seen anything like him before. That's why my belief in him is crazy.")], who="HIS TEAM  ·  FROM 'ASAKE UNFILTERED'"),
    sc("y4", "What happened next was not a rise. It was a takeover.",
       [clip("convoy", tag="Lagos  ·  2022"), kin([("NOT A RISE.", 0), ("A TAKEOVER.", (0, 0.55))], style="tick")], mood="groove", hold=0.4),
    sc("y5", "Omo Ope. Sungba. Then a Sungba remix with Burna Boy. Peace Be Unto You. Terminator. Within months, his songs were everywhere, from the buses of Lagos to the clubs of London.",
       [kin([("OMO OPE", 0), ("SUNGBA", 1), ("SUNGBA (REMIX) ft. BURNA BOY", 2), ("PEACE BE UNTO YOU", 3), ("TERMINATOR", 4)], style="list"),
        photo(P + "burna_untold.jpg", at=(2, 0.2), focus=(0.7, 0.4), grade="gold", tag="Burna Boy", credit="Lucian Nuta / CC BY-SA 2.0"),
        photo(P + "lagos_street.jpg", at=5, focus=(0.5, 0.6), grade="warm", tag="Lagos", credit="oneVillage Initiative / CC BY-SA 2.0")], mood="groove"),
    sc("y6", "On the eighth of September, 2022, he released his debut album. Mr Money with the Vibe.",
       [three("vinyl", start=1.0), kin(["MR. MONEY", "WITH THE VIBE"], at=(0, 0.6), style="album")], mood="groove", drop=True, hold=0.9, stamp="SEP 08 2022"),
    sc("y7", "At the time, it broke the record for the biggest opening day for an African album on Apple Music. And it entered the Billboard 200 at number 66.",
       [stat("1", "BIGGEST OPENING DAY FOR AN AFRICAN ALBUM ON APPLE MUSIC", prefix="#", count=False),
        chart([("BILLBOARD 200", 66)], at=1, title="DEBUT POSITION")], mood="groove"),
    sc("y8", "By December, Audiomack named him artiste of the year, after the album passed 330 million streams.",
       [stat(330000000, "STREAMS ON AUDIOMACK  ·  2022", fx="naira")], mood="groove"),
    sc("y9", "And somewhere in Lagos, on a parlour floor, a boy with no plan pressed play.",
       [three("phone", start=1.0)], mood="night", hold=1.2, stamp="SEP 2022"),

    # ---------------------------------------------------------------- 5 BRIXTON
    card("c5", "BRIXTON", "London  ·  December 2022", mood="lament", color="white"),
    sc("b1", "But that December, his story met its darkest night.",
       [photo(P + "brixton_academy.jpg", focus=(0.5, 0.5), grade="bw", tag="O2 Academy Brixton  ·  London", credit="Ewan-M / CC BY-SA 2.0")], mood="lament"),
    sc("b2", "Asake sold out three nights at the O2 Academy Brixton. On the final night, a crowd crush at the venue left several people critically injured.",
       [photo(P + "brixton_academy2.jpg", focus=(0.5, 0.5), grade="bw", move="out", credit="Phil Sheard / CC BY 2.0")], mood="lament"),
    sc("b3", "Two of them later died. Rebecca Ikumelo, a 33-year-old who came to see him perform. And Gaby Hutchinson, a 23-year-old security guard working that night.",
       [dict(kind="names", names=[("REBECCA IKUMELO", "33"), ("GABY HUTCHINSON", "23")], at=0, bg3d="candles")], mood="lament", hold=2.2),

    # ---------------------------------------------------------------- 6 WORK OF ART
    card("c6", "WORK OF ART", "2023", mood="rise"),
    arch("ar2", "grind", [(0.0, 4.6, "Before the bright lights, before the thundering applause, there is the grind.")], picture="mic"),
    sc("w1", "In 2023, he kept moving. Yoga. 2:30. And Amapiano, with Olamide, which earned him his first Grammy nomination.",
       [clip("band", start=2.0), kin([("YOGA", 0), ("2:30", 0), ("AMAPIANO ft. OLAMIDE", 1)], style="list"),
        kin([("GRAMMY", (1, 0.5)), ("NOMINATION", (1, 0.5))], style="award")], mood="rise"),
    sc("w2", "His second album, Work of Art, landed on the sixteenth of June, 2023. It entered the Billboard 200 at number 66 again, and the UK albums chart at number 20.",
       [kin(["WORK", "OF ART"], style="album"), chart([("BILLBOARD 200", 66), ("UK ALBUMS", 20)], at=1, title="DEBUT POSITIONS")], mood="rise"),
    arch("ar3", "perfectionist", []),
    sc("w3", "In August, he came back to London and sold out the O2 Arena. He opened the night with a tribute to the two who died at Brixton. Then he arrived by helicopter.",
       [photo(P + "o2_arena2.jpg", focus=(0.5, 0.5), grade="gold", tag="The O2 Arena  ·  London", credit="rp72 / CC BY 2.0"),
        clip("fireworks", at=(0, 0.45), tag="Live"), kin([("SOLD OUT", (0, 0.6))], style="stamp"), kin([("REBECCA  ·  GABY", 1)], style="candle")], mood="rise", drop=True),
    sc("w4", "A month later, in New York, he became the first African artist to headline and sell out the Barclays Center.",
       [photo(P + "barclays_ext.jpg", focus=(0.5, 0.5), grade="gold", tag="Barclays Center  ·  Brooklyn, New York", credit="LunchboxLarry / CC BY 2.0"),
        clip("stage", at=(0, 0.45)), kin([("FIRST AFRICAN", (0, 0.6)), ("TO HEADLINE & SELL OUT", (0, 0.6))], style="stack")], mood="rise"),
    sc("w5", "The boy who refused to leave Nigeria was now filling the biggest rooms in the world. But the hardest test for a stubborn man was still ahead. Leaving the house that made him.",
       [clip("portraits")], mood="rise", hold=0.6),

    # ---------------------------------------------------------------- 7 LUNGU BOY
    card("c7", "LUNGU BOY", "2024", mood="groove"),
    sc("l1", "In 2024 came his third album, Lungu Boy. Travis Scott, Central Cee, Stormzy and Wizkid all came on board.",
       [clip("stage", start=2.0), kin([("LUNGU BOY", 0), ("TRAVIS SCOTT", 1), ("CENTRAL CEE", 1), ("STORMZY", 1), ("WIZKID", 1)], style="list"),
        ], mood="groove"),
    sc("l2", "It set a new record for the biggest opening day for a Nigerian album on Spotify. 9.2 million streams.",
       [stat(9200000, "STREAMS ON DAY ONE  ·  SPOTIFY  ·  NIGERIAN ALBUM RECORD", fx="naira")], mood="groove"),
    sc("l3", "His song with Wizkid, MMS, set a new record for first-day streams of a song on Spotify Nigeria. It brought him a second Grammy nomination.",
       [clip("spot"), kin([("MMS", 0), ("ft. WIZKID", 0)], style="track"), kin([("2nd GRAMMY", 1), ("NOMINATION", 1)], style="award")], mood="groove"),

    # ---------------------------------------------------------------- 8 WHY LOVE
    card("c8", "WHY LOVE", "Giran Republic  ·  2025", mood="tender", color="red"),
    sc("v1", "Then the stubborn boy did what he had always done. He chose his own road.",
       [clip("hallway", speed=0.6)], mood="tender"),
    sc("v2", "On the twelfth of February, 2025, he released a single called Why Love, on his own new label. Giran Republic. The stubborn republic.",
       [three("ch_GIRAN", start=2.0), kin([("WHY LOVE", 0)], style="track"), kin([("GIRAN", 1), ("REPUBLIC", 1)], style="name")], mood="tender"),
    sc("v3", "It marked his exit from YBNL, the house that first opened the door for him. But the bond held. Olamide later called him his brother for life.",
       [photo(P + "crowd.jpg", focus=(0.5, 0.5), grade="bw", credit="deadserpents / CC BY 2.0"),
        quote("He is my brother for life.", "OLAMIDE", at=2)], mood="tender"),
    sc("v4", "And with his father, after years of distance, Asake would say that the love is still the same.",
       [clip("beanie", mode="tv", start=2.0, speed=0.5), quote("The love is still the same.", "ASAKE  ·  2026", at=(0, 0.4))], mood="tender", hold=1.2),

    arch("ar4", "same", [(0.0, 3.0, "We work so hard to remain the same, you know?"), (3.0, 4.9, "Putting so much energy, so we can grow and grow.")]),

    # ---------------------------------------------------------------- 9 M$NEY
    card("c9", "M$NEY", "2026", mood="rise"),
    sc("m1", "And the stubborn bet paid off. In January 2026, he and Wizkid released Real, Volume One, together. It went straight to number one in Nigeria.",
       [clip("spot"), kin(["REAL", "VOL. 1"], style="album"), kin([("#1", 1)], style="big")], mood="rise"),
    sc("m2", "Then, on the first of May, 2026, came his fourth album. M$NEY.",
       [three("vinyl", start=2.5), kin(["M$NEY"], style="album")], mood="rise", drop=True, hold=0.8),
    sc("m3", "In its first week, it did 42.2 million streams on Spotify Nigeria. A record.",
       [stat(42200000, "FIRST-WEEK STREAMS  ·  SPOTIFY NIGERIA  ·  RECORD", fx="naira")], mood="rise"),
    sc("m4", "That July, he stood on the stage of the Theatre Royal, Drury Lane, in London, with a live orchestra and a forty-member choir. The first Afrobeats artist ever to headline it.",
       [clip("stage", start=6.0, speed=0.8), kin([("THEATRE ROYAL, DRURY LANE", (0, 0.5)), ("LIVE ORCHESTRA", 1), ("40-MEMBER CHOIR", 1), ("FIRST AFROBEATS HEADLINER", 2)], style="stack")], mood="rise"),

    # ---------------------------------------------------------------- 10 THE VIBE
    card("c10", "THE VIBE", "Why him?", mood="groove"),
    sc("t1", "So why him? Why does Asake land so differently?",
       [photo(ASK2, focus=(0.5, 0.35), grade="gold", strip=True, credit=CR_ASK)], mood="groove"),
    sc("t2", "Listen to what he mixes. Fuji, the sound that grew out of the songs that woke Lagos for Ramadan. Amapiano log drums from South Africa. Street pop. And behind it all, a choir.",
       [clip("band"), kin([("FUJI", 1), ("+ AMAPIANO", 2), ("+ STREET POP", 3), ("+ A CHOIR", 4)], style="recipe")], mood="groove"),
    sc("t3", "He sings mostly in Yoruba, with street slang and pidgin. He does not translate himself for anybody. And the world comes to him anyway.",
       [clip("stage", start=9.0), kin([("YORÙBÁ", 0), ("NO TRANSLATION", 1), ("THE WORLD CAME ANYWAY", 2)], style="stack")], mood="groove"),
    sc("t4", "He says very little. He gives few interviews. He lets the stage do the talking. A theatre student, still performing.",
       [three("mic"), clip("portraits", at=2, start=3.0)], mood="groove"),
    sc("t5", "And underneath the money, the chains and the helicopters, the story his fans hold on to is a simple one. A stubborn boy who believed in himself before anybody else did.",
       [photo(ASK1, focus=(0.5, 0.35), grade="gold", strip=True, credit=CR_ASK, move="in")], mood="anthem", hold=0.6),

    # ---------------------------------------------------------------- OUTRO
    sc("e1", "Remember the boy on the parlour floor in 2022? No plan. No idea what came next.",
       [three("phone", start=0.5)], mood="anthem", hold=0.5, stamp="2022"),
    sc("e2", "He made this documentary.",
       [three("phone", start=3.0), kin([("HE MADE THIS", 0), ("DOCUMENTARY.", 0)], style="reveal")], mood="anthem", hold=1.6),
    sc("e3", "Ololade. Wealth has arrived. Sometimes, before it arrives in your pocket, it has to arrive in your head. Stay stubborn.",
       [three("mm", start=5.2), kin([("OLOLADE", 0), ("wealth has arrived", 0), ("STAY STUBBORN.", 2)], style="final")], mood="anthem", hold=1.0),
    sc("e4", "If this story moved you, subscribe to Naija Untold. And tell us in the comments: which Asake song found you, when you needed it?",
       [dict(kind="end", at=0)], mood="anthem", hold=2.5),
]
