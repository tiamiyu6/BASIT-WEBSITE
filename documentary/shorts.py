"""Vertical short-form cuts (Facebook Reels / Shorts / TikTok) built from the same engine.

Each short opens on a hook in the first second, cuts on every sentence with a slam word, and
ends on a half-sentence over the SAME picture it opened on, so the last line runs straight into
the first and the video loops seamlessly.

Build:  ./documentary/build_shorts.sh who lekki uturn
"""


def sc(id, plate, text="", trans="flash", mood="epic", hold=0.3, broll=(), speed=1.04, lead=0.15,
       clip_slam=None, hit=True, loop_phrase=None):
    return dict(id=id, chapter="", plate=plate, title="", sub="", text=text, trans=trans, mood=mood, hit=hit,
                hold=hold, slam=None, broll=list(broll), speed=speed, lead=lead, broll_frac=1.0 if broll else None,
                clip_slam=clip_slam, loop_phrase=loop_phrase)


SHORTS = {
    # 1 ------------------------------------------------------------------ WHO IS TINUBU, REALLY?
    # loop: "...when he stood before his party and said" -> [his real voice] "Even then, it is my turn!"
    "who": dict(
        headline=("WHO IS", "TINUBU REALLY?"),
        scenes=lambda: [
            sc("tease", "quote_emilokan", trans="fade", lead=0.0, clip_slam="EMI LO KAN", hold=0.2),
            sc("who", "open",
               "He has been called the godfather of Lagos. "
               "A market woman's son. "
               "An accountant in Chicago. "
               "A senator, then an exile who fought a dictator. "
               "As governor, he rebuilt the finances of Lagos, and built a political machine. "
               "He made governors. "
               "He helped make a president. "
               "In twenty twenty-three, he won with thirty-seven percent of the vote. "
               "And on day one, he said: "
               "Fuel subsidy is gone. "
               "But it all started in Abeokuta, when he stood before his party and said",
               hold=0.05,
               broll=[("chatham-house-2011.jpg", "", "", "Chatham House, CC BY 2.0", "THE GODFATHER", (0, 0.0)),
                      ("mogaji-with-son.jpg", "", "", "archive photo", "IYALOJA'S SON", (1, 0.0)),
                      ("tinubu-young-sepia.jpg", "", "", "archive photo", "CHICAGO", (2, 0.0)),
                      ("abacha-portrait.jpg", "", "", "archive photo", "EXILE", (3, 0.45)),
                      ("tinubu-governor-archive.jpg", "", "", "archive photo", "GOVERNOR", (4, 0.0)),
                      ("tinubu-lagos-allies-award.jpg", "", "", "archive photo", "THE MACHINE", (4, 0.55)),
                      ("tinubu-lagos-allies-retreat.jpg", "", "", "archive photo", "KINGMAKER", (5, 0.0)),
                      ("tinubu-buhari-hands-raised.jpg", "", "", "archive photo", "BUHARI", (6, 0.0)),
                      ("@results", "", "", "", "36.6%", (7, 0.0)),
                      ("official-portrait-2023.jpg", "", "", "Nosa Asemota, CC BY-SA 4.0", "DAY ONE", (8, 0.0)),
                      ("@quote_subsidy", "", "", "", "", (9, 0.0)),
                      ("abeokuta-podium.jpg", "", "", "", "", (10, 0.3))]),  # = first frame of the opening clip
        ]),
    # 2 ------------------------------------------------------------------ LEKKI 20.10.2020
    # video is rotated to begin at "the lights went off at the Lekki toll gate" inside the final sentence
    "lekki": dict(
        headline=("WHAT HAPPENED", "AT LEKKI?"),
        scenes=lambda: [
            sc("lekki_short", "memorial",
               "Then the shooting started. "
               "It was October, twenty twenty. "
               "Young Nigerians had filled the streets to end police brutality. "
               "At the toll gate, they waved the flag and sang the national anthem. "
               "A judicial panel set up by Lagos State later called it a massacre. "
               "The army rejected that finding. "
               "Agbeze Ifeanyi Matthew was shot in the chest. "
               "He survived. "
               "When they got to the toll gate, he said, they immediately started shooting. "
               "Two years later, the man many saw as the face of the establishment became president. "
               "And every October, Nigerians remember the night the lights went off at the Lekki toll gate.",
               trans="fade", mood="dark", lead=0.05, hold=0.15, loop_phrase="the lights went off",
               broll=[("lekki-night-injured-2020.jpg", "", "", "Adetona Omokanye / Getty", "20 · 10 · 2020", (0, 0.0)),
                      ("endsars-lagos-2020.jpg", "", "", "Jerry Jallo / Böll Stiftung, CC BY-SA 2.0", "#ENDSARS", (1, 0.0)),
                      ("endsars-protest-2020.jpg", "", "", "via Al Jazeera", "END SARS NOW", (2, 0.0)),
                      ("lekki-tollgate-afp-2020.jpg", "", "", "Pius Utomi Ekpei / AFP / Getty", "LEKKI TOLL GATE", (3, 0.0)),
                      ("nigeria-is-bleeding-2020.jpg", "", "", "via Marie Claire UK", "“MASSACRE”", (4, 0.0)),
                      ("end-sars-now-flag.jpg", "", "", "Pius Utomi Ekpei / AFP / Getty", "DENIED", (5, 0.0)),
                      ("agbeze-ifeanyi-matthew.jpg", "", "", "Handout, via The Guardian", "SHOT", (6, 0.0)),
                      ("@witness", "", "", "", "", (8, 0.0)),
                      ("official-portrait-2023.jpg", "", "", "Nosa Asemota, CC BY-SA 4.0", "PRESIDENT", (9, 0.0)),
                      ("@memorial", "", "", "", "", (10, 0.0)),
                      ("@lekki", "", "", "", "LIGHTS OUT", "loop")]),
        ]),
    # 3 ------------------------------------------------------------------ THE U-TURN (starts at "he said it would toss...")
    "uturn": dict(
        headline=("HE CALLED IT", "THE MIDNIGHT SEA"),
        scenes=lambda: [
            sc("uturn_short", "uturn",
               "Then he did it himself. "
               "In twenty twelve, he opposed removing the fuel subsidy. "
               "Eleven years later, in his first speech as president, he declared: "
               "Fuel subsidy is gone. "
               "Petrol nearly tripled almost overnight. "
               "By late twenty twenty-four, it was around a thousand naira a litre. "
               "The naira lost more than two thirds of its value. "
               "Inflation hit thirty-four percent, the highest in nearly three decades. "
               "Young Nigerians marched again. End bad governance. "
               "Amnesty International says at least twenty-four were killed. "
               "His supporters call it brave, necessary reform. "
               "His critics call it the ultimate U-turn. "
               "Because back in twenty twelve, he said it would toss Nigerians into the depths of the midnight sea.",
               trans="fade", mood="tension", lead=0.05, hold=0.15, loop_phrase="he said it would",
               broll=[("official-portrait-2023.jpg", "", "", "Nosa Asemota, CC BY-SA 4.0", "THEN HE DID IT", (0, 0.0)),
                      ("@uturn", "", "", "", "2012", (1, 0.0)),
                      ("official-portrait-2023.jpg", "", "", "Nosa Asemota, CC BY-SA 4.0", "2023", (2, 0.0)),
                      ("@quote_subsidy", "", "", "", "", (3, 0.0)),
                      ("@fuelprice", "", "", "", "₦185 → ₦617", (4, 0.0)),
                      ("@fuelprice", "", "", "", "~₦1,000", (5, 0.0)),
                      ("@economy", "", "", "", "NAIRA −⅔", (6, 0.0)),
                      ("@economy", "", "", "", "34% INFLATION", (7, 0.0)),
                      ("endbadgovernance-march-2024.jpg", "", "", "via Amnesty International", "#ENDBADGOVERNANCE", (8, 0.0)),
                      ("@protest", "", "", "", "24 KILLED", (10, 0.0)),
                      ("tinubu-shettima-2027.jpg", "", "", "via Arise News", "REFORM?", (11, 0.0)),
                      ("@uturn", "", "", "", "U-TURN", (12, 0.0)),
                      ("occupy-nigeria-nyc-2012.jpg", "", "", "Michael Fleshman, CC BY-SA 2.0", "", (13, 0.0)),
                      ("occupy-nigeria-nyc-2012.jpg", "", "", "Michael Fleshman, CC BY-SA 2.0", "“MIDNIGHT SEA”", "loop")]),
        ]),
    # ------------------------------------------------------------------ TikTok stories
    "tt_money": dict(
        headline=("THE $460,000", "QUESTION"),
        scenes=lambda: [
            sc("tt_money", "case1993",
               "He was never charged with a crime. "
               "He settled, and four hundred and sixty thousand dollars was forfeited. "
               "He has always denied any wrongdoing. "
               "Six years later, he was governor of Lagos. "
               "He built a political machine that made governors, and helped make a president. "
               "In twenty twenty-three, he became president himself. "
               "Critics still ask where his fortune came from. "
               "His supporters point out that he was never convicted of anything. "
               "And it all goes back to Chicago, in nineteen ninety-three, "
               "when US prosecutors alleged that money in accounts linked to him came from heroin trafficking.",
               trans="fade", mood="tension", lead=0.05, hold=0.15, loop_phrase="when us prosecutors",
               broll=[("@case1993", "", "", "", "NEVER CHARGED", (0, 0.0)),
                      ("@case1993", "", "", "", "$460,000", (1, 0.0)),
                      ("official-portrait-2023.jpg", "", "", "Nosa Asemota, CC BY-SA 4.0", "DENIES IT", (2, 0.0)),
                      ("tinubu-governor-archive.jpg", "", "", "archive photo", "GOVERNOR", (3, 0.0)),
                      ("tinubu-lagos-allies-award.jpg", "", "", "archive photo", "KINGMAKER", (4, 0.0)),
                      ("official-portrait-2023.jpg", "", "", "Nosa Asemota, CC BY-SA 4.0", "PRESIDENT", (5, 0.0)),
                      ("@bullion", "", "", "", "THE MONEY?", (6, 0.0)),
                      ("tinubu-lagos-allies-retreat.jpg", "", "", "archive photo", "NEVER CONVICTED", (7, 0.0)),
                      ("tinubu-young-sepia.jpg", "", "", "archive photo", "CHICAGO", (8, 0.0)),
                      ("@case1993", "", "", "", "DRUG MONEY?", "loop")]),
        ]),
    "tt_mother": dict(
        headline=("THE IYALOJA'S", "SON"),
        scenes=lambda: [
            sc("tt_mother", "mother",
               "Alhaja Abibatu Mogaji led the Lagos market women as their Iyaloja. "
               "Thousands of traders, and the votes that came with them. "
               "Her son learned early that power is built on the ground. "
               "He became governor of Lagos, then the kingmaker of Nigeria. "
               "When she died in twenty thirteen, her title passed to his daughter, Folashade. "
               "And today, the son of the Iyaloja is president of Nigeria. "
               "And it all began with his mother, the woman who ruled the markets of Lagos.",
               trans="fade", mood="warm", lead=0.05, hold=0.15, loop_phrase="the woman who ruled",
               broll=[("mogaji-blessing.jpg", "", "", "archive photo", "IYALOJA", (0, 0.0)),
                      ("@mother", "", "", "", "THOUSANDS", (1, 0.0)),
                      ("tinubu-young-sepia.jpg", "", "", "archive photo", "HER SON", (2, 0.0)),
                      ("tinubu-governor-archive.jpg", "", "", "archive photo", "GOVERNOR", (3, 0.0)),
                      ("@family", "", "", "", "3 GENERATIONS", (4, 0.0)),
                      ("official-portrait-2023.jpg", "", "", "Nosa Asemota, CC BY-SA 4.0", "PRESIDENT", (5, 0.0)),
                      ("mogaji-with-son.jpg", "", "", "archive photo", "", (6, 0.0)),
                      ("mogaji-with-son.jpg", "", "", "archive photo", "THE IYALOJA'S SON", "loop")]),
        ]),
    "tt_exile": dict(
        headline=("HE FLED", "A DICTATOR"),
        scenes=lambda: [
            sc("tt_exile", "abacha",
               "He went into hiding, then slipped across the border into Benin Republic. "
               "General Sani Abacha ruled Nigeria by fear. "
               "The man widely seen as the winner of June twelfth, Moshood Abiola, was in jail. "
               "His wife Kudirat was shot dead on a Lagos street. "
               "From exile, Tinubu helped fund the pro-democracy struggle. "
               "In nineteen ninety-eight, Abacha died suddenly. "
               "Tinubu came home, and within a year he was governor of Lagos. "
               "Twenty-five years later, he was president. "
               "But it all started under Abacha, when his home in Victoria Island was bombed.",
               trans="fade", mood="dark", lead=0.05, hold=0.15, loop_phrase="when his home",
               broll=[("@exile", "", "", "", "EXILE", (0, 0.0)),
                      ("abacha-portrait.jpg", "", "", "archive photo", "ABACHA", (1, 0.0)),
                      ("abiola-portrait.jpg", "", "", "archive photo", "M.K.O. ABIOLA", (2, 0.0)),
                      ("@kudirat", "", "", "", "KUDIRAT", (3, 0.0)),
                      ("@exile", "", "", "", "NADECO", (4, 0.0)),
                      ("abacha-glasses.jpg", "", "", "archive photo", "1998", (5, 0.0)),
                      ("tinubu-governor-archive.jpg", "", "", "archive photo", "GOVERNOR", (6, 0.0)),
                      ("official-portrait-2023.jpg", "", "", "Nosa Asemota, CC BY-SA 4.0", "PRESIDENT", (7, 0.0)),
                      ("abacha-glasses.jpg", "", "", "archive photo", "", (8, 0.0)),
                      ("@abacha", "", "", "", "BOMBED", "loop")]),
        ]),
    # ------------------------------------------------------------------ WhatsApp Status (<30 s): the midnight sea
    "wa_sea": dict(
        headline=("HE CALLED IT", "THE MIDNIGHT SEA"),
        scenes=lambda: [
            sc("wa_sea", "uturn",
               "Then he did it himself. "
               "Petrol went from one hundred and eighty-five naira, to six hundred and seventeen, to about a thousand. "
               "His critics call it a U-turn. "
               "Because back in twenty twelve, he said it would toss Nigerians into the depths of the midnight sea.",
               trans="fade", mood="tension", lead=0.05, hold=0.15, speed=1.08, loop_phrase="he said it would",
               broll=[("official-portrait-2023.jpg", "", "", "Nosa Asemota, CC BY-SA 4.0", "THEN HE DID IT", (0, 0.0)),
                      ("@fuelprice", "", "", "", "₦185 → ₦617", (1, 0.0)),
                      ("@fuelprice", "", "", "", "~₦1,000", (2, 0.0)),
                      ("@uturn", "", "", "", "U-TURN", (3, 0.0)),
                      ("occupy-nigeria-nyc-2012.jpg", "", "", "Michael Fleshman, CC BY-SA 2.0", "", (4, 0.0)),
                      ("occupy-nigeria-nyc-2012.jpg", "", "", "Michael Fleshman, CC BY-SA 2.0", "“MIDNIGHT SEA”", "loop")]),
        ]),
}


def build_short(name):
    return SHORTS[name]["scenes"]()
