"""Vertical short-form cuts (Facebook Reels / Shorts / TikTok) built from the same engine.

Each short opens on a hook in the first second, cuts on every sentence with a slam word, and
ends on a half-sentence over the SAME picture it opened on, so the last line runs straight into
the first and the video loops seamlessly.

Build:  ./documentary/build_shorts.sh who lekki uturn
"""


def sc(id, plate, text="", trans="flash", mood="epic", hold=0.3, broll=(), speed=1.04, lead=0.15,
       clip_slam=None, hit=True):
    return dict(id=id, chapter="", plate=plate, title="", sub="", text=text, trans=trans, mood=mood, hit=hit,
                hold=hold, slam=None, broll=list(broll), speed=speed, lead=lead, broll_frac=1.0 if broll else None,
                clip_slam=clip_slam)


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
    # loop: "...Nigerians remember the night" -> "The lights went off at the Lekki toll gate."
    "lekki": dict(
        headline=("WHAT HAPPENED", "AT LEKKI?"),
        scenes=lambda: [
            sc("lekki_short", "memorial",
               "The lights went off at the Lekki toll gate. "
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
               "And every October, Nigerians remember the night",
               trans="fade", mood="dark", lead=0.05, hold=0.05,
               broll=[("@lekki", "", "", "", "LIGHTS OUT", (0, 0.0)),
                      ("lekki-night-injured-2020.jpg", "", "", "Adetona Omokanye / Getty", "20 · 10 · 2020", (1, 0.0)),
                      ("endsars-lagos-2020.jpg", "", "", "Jerry Jallo / Böll Stiftung, CC BY-SA 2.0", "#ENDSARS", (2, 0.0)),
                      ("endsars-protest-2020.jpg", "", "", "via Al Jazeera", "END SARS NOW", (3, 0.0)),
                      ("lekki-tollgate-afp-2020.jpg", "", "", "Pius Utomi Ekpei / AFP / Getty", "LEKKI TOLL GATE", (4, 0.0)),
                      ("nigeria-is-bleeding-2020.jpg", "", "", "via Marie Claire UK", "“MASSACRE”", (5, 0.0)),
                      ("end-sars-now-flag.jpg", "", "", "Pius Utomi Ekpei / AFP / Getty", "DENIED", (6, 0.0)),
                      ("agbeze-ifeanyi-matthew.jpg", "", "", "Handout, via The Guardian", "SHOT", (7, 0.0)),
                      ("@witness", "", "", "", "", (9, 0.0)),
                      ("official-portrait-2023.jpg", "", "", "Nosa Asemota, CC BY-SA 4.0", "PRESIDENT", (10, 0.0)),
                      ("@lekki", "", "", "", "", (11, 0.4))]),  # = opening picture
        ]),
    # 3 ------------------------------------------------------------------ THE U-TURN
    # loop: "...Because back in twenty twelve," -> "He said it would toss Nigerians into the depths of the midnight sea."
    "uturn": dict(
        headline=("HE CALLED IT", "THE MIDNIGHT SEA"),
        scenes=lambda: [
            sc("uturn_short", "uturn",
               "He said it would toss Nigerians into the depths of the midnight sea. "
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
               "Because back in twenty twelve,",
               trans="fade", mood="tension", lead=0.05, hold=0.05,
               broll=[("occupy-nigeria-nyc-2012.jpg", "", "", "Michael Fleshman, CC BY-SA 2.0", "“MIDNIGHT SEA”", (0, 0.0)),
                      ("official-portrait-2023.jpg", "", "", "Nosa Asemota, CC BY-SA 4.0", "THEN HE DID IT", (1, 0.0)),
                      ("@uturn", "", "", "", "2012", (2, 0.0)),
                      ("official-portrait-2023.jpg", "", "", "Nosa Asemota, CC BY-SA 4.0", "2023", (3, 0.0)),
                      ("@quote_subsidy", "", "", "", "", (4, 0.0)),
                      ("@fuelprice", "", "", "", "₦185 → ₦617", (5, 0.0)),
                      ("@fuelprice", "", "", "", "~₦1,000", (6, 0.0)),
                      ("@economy", "", "", "", "NAIRA −⅔", (7, 0.0)),
                      ("@economy", "", "", "", "34% INFLATION", (8, 0.0)),
                      ("endbadgovernance-march-2024.jpg", "", "", "via Amnesty International", "#ENDBADGOVERNANCE", (9, 0.0)),
                      ("@protest", "", "", "", "24 KILLED", (11, 0.0)),
                      ("tinubu-shettima-2027.jpg", "", "", "via Arise News", "REFORM?", (12, 0.0)),
                      ("@uturn", "", "", "", "U-TURN", (13, 0.0)),
                      ("occupy-nigeria-nyc-2012.jpg", "", "", "Michael Fleshman, CC BY-SA 2.0", "", (14, 0.0))]),  # = opening
        ]),
    # ------------------------------------------------------------------ WhatsApp Status cuts (<30 s, tight loops)
    "wa_turn": dict(
        headline=("IT WAS", "HIS TURN"),
        scenes=lambda: [
            sc("tease", "quote_emilokan", trans="fade", lead=0.0, clip_slam="EMI LO KAN", hold=0.2),
            sc("wa_turn", "open",
               "He made governors. "
               "He made a president. "
               "Then he took the crown himself. "
               "And on day one, he said: "
               "Fuel subsidy is gone. "
               "It all started when he told his party",
               speed=1.08, hold=0.05,
               broll=[("tinubu-lagos-allies-award.jpg", "", "", "archive photo", "KINGMAKER", (0, 0.0)),
                      ("tinubu-buhari-hands-raised.jpg", "", "", "archive photo", "BUHARI", (1, 0.0)),
                      ("official-portrait-2023.jpg", "", "", "Nosa Asemota, CC BY-SA 4.0", "PRESIDENT", (2, 0.0)),
                      ("@quote_subsidy", "", "", "", "", (3, 0.5)),
                      ("abeokuta-podium.jpg", "", "", "", "", (5, 0.3))]),
        ]),
    "wa_lekki": dict(
        headline=("NEVER", "FORGET"),
        scenes=lambda: [
            sc("wa_lekki", "memorial",
               "The lights went off at the Lekki toll gate. "
               "Then the shooting started. "
               "A Lagos panel called it a massacre. "
               "The army denied it. "
               "And every October, Nigerians still remember the night",
               trans="fade", mood="dark", lead=0.05, hold=0.05, speed=1.06,
               broll=[("@lekki", "", "", "", "LIGHTS OUT", (0, 0.0)),
                      ("lekki-night-injured-2020.jpg", "", "", "Adetona Omokanye / Getty", "20 · 10 · 2020", (1, 0.0)),
                      ("nigeria-is-bleeding-2020.jpg", "", "", "via Marie Claire UK", "“MASSACRE”", (2, 0.0)),
                      ("end-sars-now-flag.jpg", "", "", "Pius Utomi Ekpei / AFP / Getty", "DENIED", (3, 0.0)),
                      ("@lekki", "", "", "", "", (4, 0.4))]),
        ]),
    "wa_sea": dict(
        headline=("THE MIDNIGHT", "SEA"),
        scenes=lambda: [
            sc("wa_sea", "uturn",
               "He said it would toss Nigerians into the depths of the midnight sea. "
               "Then he did it himself. "
               "Petrol went from one hundred and eighty-five naira, to six hundred and seventeen, to about a thousand. "
               "His critics call it a U-turn. "
               "Because back in twenty twelve,",
               trans="fade", mood="tension", lead=0.05, hold=0.05, speed=1.08,
               broll=[("occupy-nigeria-nyc-2012.jpg", "", "", "Michael Fleshman, CC BY-SA 2.0", "“MIDNIGHT SEA”", (0, 0.0)),
                      ("official-portrait-2023.jpg", "", "", "Nosa Asemota, CC BY-SA 4.0", "THEN HE DID IT", (1, 0.0)),
                      ("@fuelprice", "", "", "", "₦185 → ₦617", (2, 0.0)),
                      ("@fuelprice", "", "", "", "~₦1,000", (3, 0.0)),
                      ("@uturn", "", "", "", "U-TURN", (4, 0.0)),
                      ("occupy-nigeria-nyc-2012.jpg", "", "", "Michael Fleshman, CC BY-SA 2.0", "", (5, 0.0))]),
        ]),
}


def build_short(name):
    return SHORTS[name]["scenes"]()
