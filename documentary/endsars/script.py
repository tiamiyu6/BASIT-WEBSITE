"""#ENDSARS: The Night Nigeria Can't Forget. Scene list for the Naija Untold documentary (6th anniversary, 20 Oct 2026).

Facts and how they are attributed are in SOURCES.md. Contested points are always attributed, never asserted.
Shot kinds: photo, kin, quote, stat, names, three (3D). Scene kinds without narration: card, logo, end.
"""
TITLE, SUBTITLE = "", "THE NIGHT NIGERIA CAN'T FORGET"   # the 3D title already says #ENDSARS
END_Q = "Where were you on 20 October 2020?"
DEFINE_SUB = "/ shaw-raw shaw-keh /   Yorùbá"

P = "endsars/photos/"
BR = "photos/broll/"
TOBI, KZ, ABK = "TobiJamesCandids / CC BY-SA 4.0", "Kaizenify / CC BY-SA 4.0", "Asokeretope / CC BY 4.0"
BOLL = "Jerry Jallo / Heinrich Böll Stiftung / CC BY-SA 2.0"


def photo(f, at=0, focus=(0.5, 0.45), grade=None, move="in", tag=None, credit=None, strip=None):
    return dict(kind="photo", file=f, at=at, focus=focus, grade=grade, move=move, tag=tag, credit=credit, strip=strip)


def kin(words, at=0, style="stack", bg=None, fx=None):
    return dict(kind="kin", words=words, at=at, style=style, bg=bg, fx=fx)


def quote(text, who, at=0, bg=None):
    return dict(kind="quote", text=text, who=who, at=at, bg=bg)


def stat(value, label, at=0, prefix="", suffix="", count=True, bg=None, fx=None):
    return dict(kind="stat", value=value, label=label, at=at, prefix=prefix, suffix=suffix, count=count, bg=bg, fx=fx)


def three(name, at=0, start=0.0, tag=None, speed=1.0):
    return dict(kind="three", name=name, at=at, start=start, tag=tag, speed=speed)


def sc(id, text, shots, mood="night", hold=0.7, **kw):
    return dict(id=id, text=text, shots=shots, mood=mood, hold=hold, **kw)


def card(id, word, sub, mood=None, color="white"):
    return dict(id=id, card=dict(word=word, sub=sub, color=color), mood=mood)


S = [
    # ---------------------------------------------------------------- COLD OPEN
    sc("o1", "Lagos. The twentieth of October, 2020. A Tuesday night.",
       [photo(P + "lekki_gate2.jpg", focus=(0.5, 0.5), grade="night", tag="Lekki toll gate  ·  Lagos", credit="S.aderogba / CC BY-SA 4.0")],
       mood="night", hold=0.5),
    sc("o2", "Hundreds of young Nigerians are sitting on the road at the Lekki toll gate. They are waving the green-white-green flag. They are singing the national anthem.",
       [photo(P + "tobi_sars.jpg", focus=(0.5, 0.5), grade="night", credit=TOBI)], mood="night", hold=0.4),
    sc("o3", "One of them is streaming it live on Instagram. More than a hundred thousand people are watching.",
       [photo(P + "tobi_sars.jpg", focus=(0.6, 0.4), grade="night", credit=TOBI), kin([("LIVE NOW", 0), ("100,000+ WATCHING", 1)], style="tick")], mood="night", hold=0.4),
    sc("o4", "Then the soldiers arrive.",
       [photo(P + "lekki_gate.jpg", focus=(0.5, 0.5), grade="bw", move="out", credit="Kaizen Photography / CC BY-SA 4.0")],
       mood="lament", hold=1.4, heartbeat=True),
    sc("o5", "Six years later, Nigeria still cannot agree on what happened that night. This is the story of how a hashtag became a movement, and how a movement met the army. This is #EndSARS.",
       [photo(P + "tobi_youths.jpg", focus=(0.5, 0.5), grade="bw", credit=TOBI)], mood="build", hold=0.3),
    dict(id="logo", logo=True, mood="hit"),

    # ---------------------------------------------------------------- 1 SARS
    card("c1", "SARS", "Lagos  ·  1992", mood="night", color="white"),
    sc("s1", "The story starts in 1992. A police commissioner in Lagos, Simeon Danladi Midenda, set up a small unit to fight armed robbery.",
       [photo(BR + "lagos-lagoon-dawn.jpg", focus=(0.5, 0.5), grade="bw", tag="Lagos  ·  1992", credit="dotun55 / CC BY-SA 2.0"),
        kin([("SPECIAL", 1), ("ANTI-ROBBERY", 1), ("SQUAD", 1)], style="stack")], mood="night"),
    sc("s2", "He called it the Special Anti-Robbery Squad. SARS. Its officers worked in plain clothes, and drove unmarked cars.",
       [photo(BR + "lagos-lagoon-dawn.jpg", focus=(0.3, 0.5), grade="bw", credit="dotun55 / CC BY-SA 2.0"), kin([("S · A · R · S", 0), ("PLAIN CLOTHES", 1), ("UNMARKED CARS", 1)], style="tick")], mood="night"),
    sc("s3", "Over the years, the unit spread across the country. And for many young Nigerians, it became something to fear.",
       [photo(P + "tobi_protesting.jpg", focus=(0.5, 0.4), grade="warm", credit=TOBI)], mood="night"),
    sc("s4", "Young people said they were stopped and searched for their dreadlocks, their tattoos, their laptops, or an expensive phone.",
       [photo(P + "tobi_protesting.jpg", focus=(0.3, 0.4), grade="bw", credit=TOBI), kin([("DREADLOCKS", 0), ("TATTOOS", 0), ("LAPTOP", 0), ("IPHONE", 0)], style="list")], mood="night"),
    sc("s5", "In June 2020, Amnesty International said it had documented at least eighty-two cases of torture, ill-treatment and extrajudicial execution by SARS, between 2017 and 2020.",
       [photo(P + "abk1.jpg", focus=(0.3, 0.4), grade="bw", credit=ABK), stat(82, "CASES OF TORTURE, ILL-TREATMENT AND EXTRAJUDICIAL EXECUTION  ·  AMNESTY INTERNATIONAL, 2017–2020", prefix="AT LEAST ")], mood="night"),
    sc("s6", "And, Amnesty said, not a single SARS officer had been held accountable. The hashtag #EndSARS had been trending on and off since 2017. In October 2020, it exploded.",
       [photo(P + "tobi_advocacy.jpg", focus=(0.5, 0.4), grade="bw", credit=TOBI), kin([("0", 0), ("OFFICERS HELD ACCOUNTABLE", 0)], style="tick"), kin([("#ENDSARS", 2)], style="big")], mood="build", hold=0.6),

    # ---------------------------------------------------------------- 2 SORO SOKE
    card("c2", "SORO SOKE", "October 2020", mood="groove", color="green"),
    sc("k1", "In early October, a video from Ughelli, in Delta State, spread across Nigerian Twitter. It appeared to show a young man left on the roadside after an encounter with SARS officers.",
       [photo(P + "abk1.jpg", focus=(0.4, 0.4), grade="warm", tag="October 2020", credit=ABK)], mood="build"),
    sc("k2", "The government disputed parts of the story. But it no longer mattered. Within days, young people were on the streets.",
       [photo(P + "kz04.jpg", focus=(0.5, 0.5), grade="warm", tag="Lagos  ·  October 2020", credit=KZ)], mood="groove"),
    sc("k3", "On the eighth of October, protesters gathered at the Lagos State House of Assembly. Some of them slept there overnight.",
       [photo(P + "tobi_advocacy.jpg", focus=(0.5, 0.5), grade="warm", tag="Alausa, Ikeja", credit=TOBI)], mood="groove"),
    sc("k4", "Then it spread. Abuja. Abeokuta. Ibadan. Port Harcourt. London. New York.",
       [photo(P + "abk3.jpg", focus=(0.5, 0.4), grade="warm", credit=ABK), kin([("LAGOS", 0), ("ABUJA", 0), ("ABEOKUTA", 0), ("IBADAN", 0), ("PORT HARCOURT", 0), ("LONDON", 0), ("NEW YORK", 0)], style="list")], mood="groove"),
    sc("k5", "Their cry was two Yoruba words. Soro Soke. Speak up.",
       [photo(P + "abk2.jpg", focus=(0.5, 0.35), grade="warm", credit=ABK),
        kin([("SORO SOKE", 1), ("= SPEAK UP", (1, 0.6))], style="define")], mood="groove"),
    sc("k6", "There was no single leader. Instead, strangers organised. The Feminist Coalition raised tens of millions of naira, for food, medical care, legal aid and security.",
       [photo(P + "kz61.jpg", focus=(0.5, 0.4), grade="warm", credit=KZ),
        kin([("FOOD", 2), ("MEDICAL CARE", 2), ("LEGAL AID", 2), ("SECURITY", 2)], style="stack")], mood="groove"),
    sc("k7", "Volunteer lawyers got arrested protesters released. Doctors treated the injured. For two weeks, it felt like a country inside a country.",
       [photo(P + "abk3.jpg", focus=(0.5, 0.4), grade="warm", credit=ABK)], mood="groove", hold=0.6),

    # ---------------------------------------------------------------- 3 5 FOR 5
    card("c3", "5 FOR 5", "The demands", mood="build", color="gold"),
    sc("f1", "On the eleventh of October, the Inspector General of Police announced that SARS was dissolved.",
       [photo(P + "kz38.jpg", focus=(0.5, 0.4), grade="bw", credit=KZ), kin([("SARS", 0), ("DISSOLVED", (0, 0.6))], style="promise")], mood="build"),
    sc("f2", "Two days later, he announced a new unit to replace it. SWAT. To the protesters, it looked like the same thing with a new name.",
       [photo(P + "kz04.jpg", focus=(0.5, 0.5), grade="bw", credit=KZ), kin([("SARS", 0), ("→ SWAT", 1)], style="promise")], mood="build"),
    sc("f3", "So they wrote down five demands. Release every arrested protester. Justice, and compensation, for the families of victims. An independent body to investigate police abuse. Psychological evaluation and retraining of former SARS officers. And better pay for the police.",
       [photo(P + "tobi_advocacy.jpg", focus=(0.3, 0.6), grade="warm", credit=TOBI), kin([("FREE ARRESTED PROTESTERS", 1), ("JUSTICE + COMPENSATION", 2), ("INDEPENDENT INVESTIGATION", 3), ("EVALUATE EX-SARS OFFICERS", 4), ("BETTER POLICE PAY", 5)], style="list")],
       mood="build"),
    sc("f4", "They called it five for five. And they said they would stay on the streets until the demands were met.",
       [photo(P + "kz88.jpg", focus=(0.5, 0.4), grade="warm", credit=KZ)], mood="build"),
    sc("f5", "In Lagos, the biggest crowd gathered at one place. A toll plaza on the road to Lekki. And the government was running out of patience.",
       [photo(P + "lekki_gate.jpg", focus=(0.5, 0.5), grade="warm", tag="Lekki toll gate", credit="Kaizen Photography / CC BY-SA 4.0")], mood="night", hold=0.8),

    # ---------------------------------------------------------------- 4 20.10.20
    card("c4", "20.10.20", "Lekki toll gate", mood="lament", color="red"),
    sc("l1", "On the twentieth of October, the Lagos State government announced a twenty-four hour curfew.",
       [photo(P + "lekki_gate2.jpg", focus=(0.6, 0.5), grade="night", credit="S.aderogba / CC BY-SA 4.0"), kin([("24-HOUR", 0), ("CURFEW", 0)], style="tick")], mood="lament"),
    sc("l2", "At the Lekki toll gate, the protesters stayed. They sat down on the road. They raised the flag. They sang the anthem.",
       [photo(P + "tobi_sars.jpg", focus=(0.5, 0.5), grade="night", move="out", credit=TOBI)], mood="lament"),
    sc("l3", "That evening, soldiers arrived. Witnesses say the lights went off. And then, they say, the shooting began.",
       [photo(P + "lekki_gate2.jpg", focus=(0.5, 0.5), grade="bw", credit="S.aderogba / CC BY-SA 4.0")], mood="lament", hold=1.6, heartbeat=True),
    sc("l4", "A disc jockey, DJ Switch, kept her phone recording on Instagram Live. Much of the world watched it happen in real time.",
       [photo(P + "tobi_sars.jpg", focus=(0.3, 0.6), grade="bw", credit=TOBI), kin([("LIVE", 0), ("ON INSTAGRAM", 0)], style="tick")], mood="lament", heartbeat=True),
    sc("l5", "Amnesty International later said that the army and the police killed at least twelve protesters that night, at Lekki and at Alausa.",
       [photo(P + "tobi_youths.jpg", focus=(0.6, 0.5), grade="bw", credit=TOBI), stat(12, "PROTESTERS KILLED AT LEKKI AND ALAUSA  ·  AMNESTY INTERNATIONAL", prefix="AT LEAST ")], mood="lament"),
    sc("l6", "The army first denied that its soldiers were there at all. Later, it said its soldiers had fired only blank ammunition.",
       [photo(P + "lekki_gate.jpg", focus=(0.5, 0.5), grade="bw", credit="Kaizen Photography / CC BY-SA 4.0"), kin([("FIRST:", 0), ("“WE WERE NOT THERE”", 0), ("LATER:", 1), ("“ONLY BLANKS”", 1)], style="stack")], mood="lament", hold=1.0, siren=True),

    # ---------------------------------------------------------------- 5 AFTERMATH
    card("c5", "AFTERMATH", "October 2020", mood="night", color="white"),
    sc("a1", "In the days that followed, Lagos burned. Shops were looted. Police stations, government buildings and media houses were set on fire.",
       [photo(BR + "endsars-lagos-2020.jpg", focus=(0.5, 0.5), grade="bw", credit=BOLL)], mood="night"),
    sc("a2", "President Muhammadu Buhari said fifty-one civilians, eleven police officers and seven soldiers had been killed in the unrest. His national address did not mention the shooting at Lekki.",
       [photo(BR + "endsars-lagos-2020.jpg", focus=(0.3, 0.5), grade="bw", credit=BOLL), kin([("51 CIVILIANS", 0), ("11 POLICE OFFICERS", 0), ("7 SOLDIERS", 0)], style="list")], mood="night"),
    sc("a3", "Then the money was frozen. The Central Bank of Nigeria froze the bank accounts of about twenty people and groups linked to the protests.",
       [photo(P + "abk5.jpg", focus=(0.5, 0.4), grade="bw", credit=ABK),
        kin([("ACCOUNTS", 1), ("FROZEN", (1, 0.4))], style="promise")], mood="night"),
    sc("a4", "A lawyer who had helped arrested protesters, Modupe Odele, said immigration officers seized her passport as she tried to leave the country.",
       [photo(P + "kz61.jpg", focus=(0.5, 0.4), grade="bw", credit=KZ), kin([("PASSPORT", 0), ("SEIZED", 0)], style="tick")], mood="night", hold=0.8),

    # ---------------------------------------------------------------- 6 THE PANEL
    card("c6", "THE PANEL", "Lagos judicial panel of inquiry", mood="tender", color="gold"),
    sc("p1", "Lagos State set up a judicial panel to investigate, led by a retired judge, Justice Doris Okuwobi. It heard witnesses for about a year.",
       [photo(P + "lekki_gate.jpg", focus=(0.3, 0.5), grade="warm", credit="Kaizen Photography / CC BY-SA 4.0"), kin([("JUSTICE DORIS OKUWOBI", 0), ("~1 YEAR OF HEARINGS", 1)], style="stack")], mood="tender"),
    sc("p2", "In November 2021, its report became public. It found that soldiers fired live and blank bullets at unarmed protesters, and that the army refused to let ambulances help the wounded.",
       [photo(P + "lekki_gate2.jpg", focus=(0.4, 0.5), grade="bw", credit="S.aderogba / CC BY-SA 4.0"), kin([("LIVE BULLETS", 1), ("NO AMBULANCES", 1)], style="tick")], mood="tender"),
    sc("p3", "It listed forty-eight casualties. Eleven people killed. Four more missing, and presumed dead. And it used one word to describe what happened. A massacre.",
       [photo(P + "tobi_sars.jpg", focus=(0.5, 0.5), grade="bw", credit=TOBI), stat(48, "CASUALTIES LISTED BY THE LAGOS PANEL  ·  11 KILLED, 4 MISSING PRESUMED DEAD"),
        kin([("MASSACRE", 2)], style="big")], mood="tender", hold=0.9),
    sc("p4", "The Lagos State government rejected the panel's key findings. The federal information minister, Lai Mohammed, called it a massacre without bodies.",
       [photo(P + "lekki_gate2.jpg", focus=(0.5, 0.5), grade="bw", credit="S.aderogba / CC BY-SA 4.0"), quote("A massacre without bodies.", "LAI MOHAMMED  ·  FEDERAL INFORMATION MINISTER", at=1)], mood="tender"),
    sc("p5", "Six years on, the families of the dead and the missing say they are still waiting for justice.",
       [three("candles", speed=0.8)], mood="lament", hold=1.6),

    # ---------------------------------------------------------------- 7 AFTER LEKKI
    card("c7", "AFTER LEKKI", "What changed", mood="rise", color="green"),
    sc("v1", "So did #EndSARS fail? SARS is gone. But many Nigerians say police abuse is not.",
       [photo(P + "tobi_youths.jpg", focus=(0.5, 0.5), grade="bw", credit=TOBI)], mood="rise"),
    sc("v2", "What changed was a generation. For two weeks in 2020, young Nigerians discovered that they could organise without a leader, fund themselves, and be heard around the world.",
       [photo(P + "abk5.jpg", focus=(0.5, 0.4), grade="warm", credit=ABK)], mood="rise"),
    sc("v3", "On the anniversaries since, people have returned to Lekki to remember. With flags. With car horns. With candles.",
       [photo(P + "lekki_gate.jpg", focus=(0.5, 0.5), grade="warm", credit="Kaizen Photography / CC BY-SA 4.0")], mood="anthem"),
    sc("v4", "Whatever you believe happened at the toll gate, one thing is not in dispute. A generation stood up, sang its national anthem, and asked to be treated like citizens.",
       [photo(P + "abk3.jpg", focus=(0.5, 0.4), grade="warm", credit=ABK)], mood="anthem", hold=0.8),
    sc("v5", "Soro soke. Speak up. They did.",
       [photo(P + "abk2.jpg", focus=(0.5, 0.4), grade="warm", credit=ABK), kin([("SORO SOKE.", 0), ("SPEAK UP.", 1), ("THEY DID.", 2)], style="final")], mood="anthem", hold=1.4),
    sc("e1", "If this story matters to you, subscribe to Naija Untold. And tell us in the comments: where were you on the twentieth of October, 2020?",
       [dict(kind="end", at=0)], mood="anthem", hold=2.5),
]
