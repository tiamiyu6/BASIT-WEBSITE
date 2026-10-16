"""Vertical short-form cuts (Facebook Reels / Shorts / TikTok) built from the same engine.

Each short opens on a hook in the first second, cuts on every sentence with a slam word,
and ends on a line that runs straight back into the opening line so the video loops.

Build:  SHORT=who ./documentary/build_shorts.sh   (who | lekki | uturn)
"""


def sc(id, plate, text="", trans="flash", mood="epic", hold=0.3, broll=(), speed=1.04, lead=0.15,
       clip_slam=None, hit=True):
    return dict(id=id, chapter="", plate=plate, title="", sub="", text=text, trans=trans, mood=mood, hit=hit,
                hold=hold, slam=None, broll=list(broll), speed=speed, lead=lead, broll_frac=1.0 if broll else None,
                clip_slam=clip_slam)


SHORTS = {
    # 1 ------------------------------------------------------------------ WHO IS TINUBU, REALLY?
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
               "Then he told his party: "
               "It is my turn. "
               "In twenty twenty-three, he won with thirty-seven percent of the vote. "
               "The lowest winning share of the Fourth Republic. "
               "And on day one, he said: "
               "Fuel subsidy is gone. "
               "So who is Bola Tinubu, really?",
               broll=[("chatham-house-2011.jpg", "", "", "Chatham House, CC BY 2.0", "THE GODFATHER", (0, 0.0)),
                      ("mogaji-with-son.jpg", "", "", "archive photo", "IYALOJA'S SON", (1, 0.0)),
                      ("tinubu-young-sepia.jpg", "", "", "archive photo", "CHICAGO", (2, 0.0)),
                      ("abacha-portrait.jpg", "", "", "archive photo", "EXILE", (3, 0.45)),
                      ("tinubu-governor-archive.jpg", "", "", "archive photo", "GOVERNOR", (4, 0.0)),
                      ("tinubu-lagos-allies-award.jpg", "", "", "archive photo", "THE MACHINE", (4, 0.55)),
                      ("tinubu-lagos-allies-retreat.jpg", "", "", "archive photo", "KINGMAKER", (5, 0.0)),
                      ("tinubu-buhari-hands-raised.jpg", "", "", "archive photo", "BUHARI", (6, 0.0)),
                      ("@quote_emilokan", "", "", "", "", (7, 0.0)),
                      ("@results", "", "", "", "36.6%", (9, 0.0)),
                      ("@results", "", "", "", "LOWEST EVER", (10, 0.0)),
                      ("official-portrait-2023.jpg", "", "", "Nosa Asemota, CC BY-SA 4.0", "DAY ONE", (11, 0.0)),
                      ("@quote_subsidy", "", "", "", "", (12, 0.0)),
                      ("official-portrait-2023.jpg", "", "", "Nosa Asemota, CC BY-SA 4.0", "WHO IS HE?", (13, 0.0))]),
        ]),
    # 2 ------------------------------------------------------------------ LEKKI 20.10.2020
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
               trans="fade", mood="dark", lead=0.1,
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
                      ("@memorial", "", "", "", "", (11, 0.0))]),
        ]),
    # 3 ------------------------------------------------------------------ THE U-TURN
    "uturn": dict(
        headline=("HE SAID THIS", "IN 2012…"),
        scenes=lambda: [
            sc("uturn_short", "uturn",
               "In twenty twelve, he opposed removing the fuel subsidy. "
               "He said it tossed Nigerians into the depths of the midnight sea. "
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
               "And it all goes back to what he said",
               trans="fade", mood="tension", lead=0.1,
               broll=[("occupy-nigeria-nyc-2012.jpg", "", "", "Michael Fleshman, CC BY-SA 2.0", "2012", (0, 0.0)),
                      ("@uturn", "", "", "", "", (1, 0.0)),
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
                      ("@uturn", "", "", "", "", (13, 0.0))]),
        ]),
}


def build_short(name):
    return SHORTS[name]["scenes"]()
