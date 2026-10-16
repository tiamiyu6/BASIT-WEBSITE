"""Scene list for "JAGABAN: The Story of Bola Ahmed Tinubu".

Each scene has:
  id        - unique key; drop a real photo at documentary/photos/<id>.jpg to replace the illustration
  chapter   - chapter label shown top-right
  plate     - illustration key in visuals.py
  title/sub - on-screen caption (lower third) describing exactly what the picture shows
  text      - narration (spoken + burned-in subtitles). Empty = no voice (title / chapter cards)
  trans     - transition INTO this scene: fade | flash | glitch | dip | zoom
  mood      - music cue for this scene
  hit       - True = impact sound + camera shake when the scene lands
  hold      - extra seconds after narration
  broll     - real photos shown at the start of the scene before the graphic:
              [(file in photos/broll/, caption title, caption sub, photo credit), ...]
  slam      - a narration sentence that lands with a big sound-design hit, flash and shake
"""

S = []


def scene(id, chapter, plate, title, sub, text="", trans="fade", mood=None, hit=False, hold=1.0, slam=None, broll=(),
          speed=None, lead=None, broll_frac=None, clip_slam=None):
    S.append(dict(id=id, chapter=chapter, plate=plate, title=title, sub=sub, text=text,
                  trans=trans, mood=mood, hit=hit, hold=hold, slam=slam, broll=list(broll),
                  speed=speed, lead=lead, broll_frac=broll_frac, clip_slam=clip_slam))


def chapter_card(num, name, mood):
    scene(f"ch{num}", name, "chapter", f"CHAPTER {num}", name, trans="dip", mood=mood, hit=True, hold=3.2)


# ---------------------------------------------------------------- cold open
# Starts on his portrait and pushes into his eye; the story "begins" inside it.
# Real photo: documentary/photos/portrait.jpg (+ optional photos/portrait.json {"eye": [x, y]} in 0..1 coords)
# Very first seconds: his real voice, then the shock line and the promise.
scene("tease", "", "tease", "", "",
      "In nineteen ninety-three, he forfeited four hundred and sixty thousand dollars in a US case over alleged drug money, without ever being charged. "
      "Thirty years later, he became president of Nigeria. "
      "How? "
      "Stay to the end, and you'll know exactly how he did it.",
      trans="fade", mood="tension", hit=True, speed=1.04, lead=0.1, hold=0.4, clip_slam="EMI LO KAN")
# Cold open: rapid-fire real photos cut on the narrator's words, each with a slam word + impact.
# broll item: (file or @plate, title, sub, credit, SLAM TEXT, (sentence index, fraction into sentence))
scene("hook", "", "open", "", "",
      "He has been called the godfather of Lagos. "
      "The kingmaker. "
      "The Jagaban. "
      "He survived exile, a US money case, and questions about his past. "
      "When young Nigerians rose against police brutality, the bullets came at night. "
      "Then he declared: "
      "It is my turn. "
      "On his first day in power, he made a decision that shook every home in Nigeria. "
      "To his supporters, a master builder. "
      "To his critics, the ultimate godfather. "
      "This is his story. "
      "And the story of the people who live with his choices.",
      trans="flash", mood="epic", hold=0.8, speed=1.04, lead=0.25, broll_frac=1.0,
      broll=[("chatham-house-2011.jpg", "", "", "Chatham House, CC BY 2.0", "THE GODFATHER", (0, 0.0)),
             ("eagle-square-2015.jpg", "", "", "U.S. Dept. of State", "THE KINGMAKER", (1, 0.0)),
             ("victoria-island-2014.jpg", "", "", "OpenUpEd, CC BY 2.0", "JAGABAN", (2, 0.0)),
             ("@case1993", "", "", "", "$460,000", (3, 0.0)),
             ("@certificate", "", "", "", "THE CERTIFICATES", (3, 0.55)),
             ("endsars-lagos-2020.jpg", "", "", "Jerry Jallo / Böll Stiftung, CC BY-SA 2.0", "#ENDSARS", (4, 0.0)),
             ("lekki-night-injured-2020.jpg", "", "", "Adetona Omokanye / Getty", "20 · 10 · 2020", (4, 0.55)),
             ("@quote_emilokan", "", "", "", "", (5, 0.0)),
             ("official-portrait-2023.jpg", "", "", "Nosa Asemota, CC BY-SA 4.0", "PRESIDENT", (7, 0.0)),
             ("@quote_subsidy", "", "", "", "", (7, 0.6)),
             ("brt-third-mainland-2012.jpg", "", "", "dotun55, CC BY-SA 2.0", "MASTER BUILDER", (8, 0.0)),
             ("@bullion", "", "", "", "GODFATHER?", (9, 0.0)),
             ("lagos-lagoon-dawn.jpg", "", "", "dotun55, CC BY-SA 2.0", "", (10, 0.0)),
             ("lekki-toll-gate-protest-2020.jpg", "", "", "via Foreign Policy", "THE PEOPLE", (11, 0.0))])
scene("portrait", "", "portrait", "", "", trans="flash", mood="intro", hold=5.5)
scene("title", "", "title", "", "", trans="flash", mood="intro", hit=True, hold=5.5)

# ---------------------------------------------------------------- 1  (the land and its peoples)
chapter_card(1, "THE LAND OF MANY PEOPLES", "warm")
scene("peoples", "THE LAND OF MANY PEOPLES", "peoples", "The peoples of Nigeria", "More than 250 ethnic groups · over 500 languages",
      "To understand Tinubu, you have to understand the country that made him. "
      "Nigeria is one of the most diverse nations on earth, home to more than two hundred and fifty ethnic groups, and over five hundred languages. "
      "In the north, the Hausa and the Fulani, heirs to the Sokoto Caliphate and to ancient trading cities like Kano. "
      "In the north-east, the Kanuri, of the old Kanem-Bornu empire. "
      "In the south-east, the Igbo, known for enterprise and a tradition of village self-government. "
      "In the south-west, the Yoruba, whose kingdoms of Ife and Oyo shaped art, faith and politics across West Africa. "
      "And many more: the Tiv, the Edo, the Ijaw, the Ibibio, the Nupe, and hundreds of others.")
scene("eko", "THE LAND OF MANY PEOPLES", "eko", "Eko — Lagos", "From Awori settlement to colonial port",
      "Tinubu's Lagos has its own deep story. Its people call it Eko. "
      "It grew from a settlement of the Awori, a Yoruba people, into a kingdom whose royal line is tied to the great Kingdom of Benin. "
      "By the nineteenth century, it was one of West Africa's busiest ports, a trade that tragically included enslaved people. "
      "In eighteen sixty-one, Britain annexed Lagos as a colony. "
      "One of the city's best-known squares still carries the name Tinubu, after Madam Efunroye Tinubu, "
      "a powerful nineteenth-century merchant and political figure in Lagos and Abeokuta.", trans="zoom",
      broll=[('lagos-lagoon-dawn.jpg', 'The Lagos Lagoon at dawn', 'Fishermen below the Third Mainland Bridge', 'dotun55 / Flickr, CC BY-SA 2.0'), ('tinubu-square-lagos.jpg', 'Tinubu Square, Lagos Island', 'Named after 19th-century merchant Efunroye Tinubu', 'Jeremy Weate / Flickr, CC BY 2.0')])
scene("amalgamation", "THE LAND OF MANY PEOPLES", "amalgamation", "Amalgamation, 1914", "Northern and Southern Protectorates joined",
      "In nineteen fourteen, the British merged their Northern and Southern Protectorates into one colony, called Nigeria, "
      "a name first suggested by the journalist Flora Shaw. "
      "Peoples with different languages, faiths and histories were bound into a single state, with Lagos as its capital, and its commercial heart.")
scene("independence", "THE LAND OF MANY PEOPLES", "independence", "Independence", "1 October 1960",
      "On the first of October, nineteen sixty, Nigeria became independent. "
      "By his official birth date, Bola Tinubu was eight years old, growing up in a Lagos alive with hope.", trans="flash", hit=True)
scene("civilwar", "THE LAND OF MANY PEOPLES", "civilwar", "The Nigerian Civil War", "1967 – 1970",
      "That hope was soon tested. Two military coups in nineteen sixty-six were followed by civil war, when the Eastern Region declared itself the Republic of Biafra. "
      "Between nineteen sixty-seven and nineteen seventy, estimates of the dead range from half a million to more than two million, many from famine. "
      "The war left wounds that still shape every debate about unity, fairness and the sharing of power between regions and religions.",
      trans="dip", mood="dark")
scene("military", "THE LAND OF MANY PEOPLES", "military", "Military rule", "1966 – 1979 · 1983 – 1999",
      "For most of the next three decades, soldiers ruled Nigeria. "
      "It was into this country, rich in oil, rich in people, and hungry for democracy, that Bola Tinubu's political life would be born.",
      mood="tension", hit=True)

# ---------------------------------------------------------------- 2
chapter_card(2, "ORIGINS", "warm")
scene("born", "ORIGINS", "map_lagos", "Lagos, Nigeria", "Official birth date: 29 March 1952",
      "Lagos, the early nineteen-fifties. A colonial port city of lagoons and canoes, of crowded markets and the call to prayer drifting over Lagos Island. "
      "According to his official biography, Bola Ahmed Adekunle Tinubu was born here on the twenty-ninth of March, nineteen fifty-two, into a Yoruba Muslim family.",
      broll=[("tinubu-square-lagos.jpg", "Lagos Island", "Old commercial heart of Lagos", "Jeremy Weate / Flickr, CC BY 2.0")])
scene("mother", "ORIGINS", "mother", "Alhaja Abibatu Mogaji", "Iyaloja of Lagos · 1916 – 2013",
      "To understand his power, start with his mother. Alhaja Abibatu Mogaji was a trader who rose to lead the market women of Lagos as their Iyaloja, "
      "and later headed the Association of Nigerian Market Women and Men. "
      "In a city where markets are run by women, she commanded thousands of traders, and the votes and networks that came with them. "
      "She lived to ninety-six. Her son learned early that real power is built on the ground, one market stall at a time.",
      broll=[('mogaji-with-son.jpg', 'Tinubu with his mother', 'Alhaja Abibatu Mogaji, Iyaloja of Lagos', 'archive photo'), ('mogaji-blessing.jpg', "A mother's blessing", 'Alhaja Abibatu Mogaji prays over her son', 'archive photo')])
scene("roots", "ORIGINS", "roots", "Where is Tinubu from?", "Lagos (official) · Iragbiji, Osun State (ancestral claim)",
      "But where exactly is Tinubu from? Officially, Lagos. "
      "Yet his roots have long been debated. Allies, including a traditional chief of Iragbiji in Osun State, say his ancestral home is Iragbiji. "
      "Critics have gone further, questioning his original name and parentage, claims Tinubu has never accepted. "
      "Even the Tinubu name carries history in Lagos, shared with Madam Efunroye Tinubu, the nineteenth-century merchant honoured by Tinubu Square, "
      "though no family link between them has ever been established.")
scene("chicago", "ORIGINS", "chicago", "Chicago, United States", "Studied accounting · graduated Chicago State University, 1979",
      "In the mid nineteen-seventies he travelled to the United States. "
      "He studied at Richard J. Daley College, then at Chicago State University, graduating in nineteen seventy-nine with a degree in accounting. "
      "He worked for firms including Arthur Andersen and Deloitte, before returning home to join Mobil Oil Nigeria, where he rose to become a senior finance executive. "
      "But the records from these years would come back to haunt him, decades later.",
      broll=[('tinubu-young-sepia.jpg', 'Young Bola Tinubu', 'The accountant years', 'archive photo')])
scene("family", "ORIGINS", "family", "The Tinubu family", "Wife, children and the market-women dynasty",
      "Family has stayed close to the centre of his power. "
      "His wife, Oluremi Tinubu, a pastor in the Redeemed Christian Church of God, served three terms as senator for Lagos Central, and became First Lady in twenty twenty-three. "
      "Their daughter, Folashade Tinubu-Ojo, succeeded her grandmother as Iyaloja of Lagos in twenty thirteen, carrying the market women's network into a third generation. "
      "His eldest son, Jide, died in London in twenty seventeen, a loss Tinubu called grave. "
      "And his son Seyi has become one of the most visible faces around the presidency.")
scene("questions", "ORIGINS", "questions", "Disputed records", "Age, early schooling and documents questioned by critics",
      "Yet even these early chapters are contested. "
      "Over the years, critics have questioned his age, his schooling in Nigeria, and documents he submitted to electoral authorities. "
      "Tinubu has consistently rejected these claims, and no court has disqualified him over them.",
      trans="glitch", mood="tension")

# ---------------------------------------------------------------- 3
chapter_card(3, "DEMOCRACY & EXILE", "tension")
scene("senate", "DEMOCRACY & EXILE", "senate", "Senator, Lagos West", "Social Democratic Party (SDP) · 1992",
      "His political career began in nineteen ninety-two, when he won a Senate seat for Lagos West under the Social Democratic Party, "
      "during General Ibrahim Babangida's promised transition to civilian rule.",
      broll=[('tinubu-early-archive.jpg', 'Bola Tinubu', 'Early political years', 'archive photo')])
scene("june12", "DEMOCRACY & EXILE", "june12", "12 June 1993", "Presidential election annulled by the military",
      "That transition collapsed. The June twelfth, nineteen ninety-three presidential election, widely seen as won by Moshood Abiola, was annulled by the military. "
      "Months later, General Sani Abacha seized power, and dissolved the Senate.", trans="flash", hit=True,
      broll=[('abiola-advert-1993.jpg', 'M.K.O. Abiola', '1993 newspaper advert: “Not by my power, but the strength of your collective support”', 'archive'), ('abiola-victory-1993.jpg', 'Moshood Abiola', 'Widely seen as the winner of 12 June 1993', 'Getty Images, via BBC')])
scene("abacha", "DEMOCRACY & EXILE", "abacha", "General Sani Abacha", "Military ruler · 1993 – 1998",
      "Abacha's Nigeria was a country of fear. Journalists were jailed, activists disappeared, and in nineteen ninety-five the writer Ken Saro-Wiwa and eight other Ogoni activists were hanged. "
      "Tinubu chose a side. He helped found the National Democratic Coalition, NADECO, demanding that Abiola's mandate be restored.", trans="glitch", mood="dark",
      broll=[('abacha-portrait.jpg', 'General Sani Abacha', 'Head of state, November 1993 – June 1998', 'archive photo'), ('abacha-glasses.jpg', 'General Sani Abacha', 'His trademark dark glasses', 'archive photo')])
scene("exile", "DEMOCRACY & EXILE", "exile", "Exile", "NADECO pro-democracy campaign · 1994 – 1998",
      "In June nineteen ninety-four, Abiola declared himself president, and was arrested. The regime turned on his allies. "
      "Tinubu was detained, and his home in Victoria Island was bombed. "
      "He went into hiding, then slipped across the border into Benin Republic, and on into exile. "
      "From abroad, NADECO backed Radio Kudirat, a pirate station that broadcast against the junta, and Tinubu helped fund the struggle.",
      broll=[('abiola-portrait.jpg', 'Moshood Abiola', 'Arrested in June 1994 after declaring himself president', 'archive photo')])
scene("kudirat", "DEMOCRACY & EXILE", "kudirat", "Kudirat Abiola", "1951 – 1996",
      "The station was named after a woman. Kudirat Abiola, Moshood Abiola's wife, led the campaign to free her jailed husband. "
      "On the fourth of June, nineteen ninety-six, she was shot dead in her car on a Lagos street. "
      "Tinubu's supporters say he had urged her to leave Lagos for her safety, and that she refused, an account that has never been independently confirmed. "
      "Two years later, Abacha died suddenly in office. Within weeks, Abiola too was dead, still in detention. "
      "The road to civilian rule was open, and Tinubu came home.", mood="dark", hold=1.6)

# ---------------------------------------------------------------- 4
chapter_card(4, "GOVERNOR OF LAGOS", "warm")
scene("gov", "GOVERNOR OF LAGOS", "lagos", "Governor of Lagos State", "Alliance for Democracy · 1999 – 2007",
      "In nineteen ninety-nine, as Nigeria returned to civilian rule, he was elected Governor of Lagos State on the platform of the Alliance for Democracy. "
      "He was re-elected in two thousand and three.", trans="zoom", hit=True,
      broll=[('tinubu-governor-archive.jpg', 'Bola Tinubu', 'Governorship era', 'archive photo'), ('victoria-island-2014.jpg', 'Lagos', 'Victoria Island and the lagoon, 2014', 'OpenUpEd / Flickr, CC BY 2.0')])
scene("revenue", "GOVERNOR OF LAGOS", "revenue", "Revenue & transport reforms", "Tax overhaul · LAMATA transport authority (2002)",
      "His supporters point to a revenue revolution. His administration overhauled tax collection, and Lagos's internally generated revenue grew many times over, "
      "giving the state a financial independence few others could match. "
      "He also created the Lagos Metropolitan Area Transport Authority, the body behind the city's later bus rapid transit system.",
      broll=[('brt-third-mainland-2012.jpg', 'Lagos BRT bus', 'On the Third Mainland Bridge, 2012', 'dotun55 / Flickr, CC BY-SA 2.0')])
scene("lcda", "GOVERNOR OF LAGOS", "lcda", "Lagos vs. the Federal Government", "Dispute over 37 new council areas · Supreme Court, 2004",
      "He was not afraid of confrontation. When Lagos created thirty-seven new local council development areas, "
      "President Olusegun Obasanjo's government withheld the state's local government funds. "
      "The battle went to the Supreme Court, which ruled that the federal government had no power to withhold the money.")

# ---------------------------------------------------------------- 5
chapter_card(5, "THE KINGMAKER", "epic")
scene("machine", "THE KINGMAKER", "network", "The Lagos political machine", "Successors and allies backed by Tinubu",
      "After leaving office in two thousand and seven, Tinubu never really left power. He built one of the most formidable political machines in the country. "
      "His successors in Lagos, Babatunde Fashola, Akinwunmi Ambode and Babajide Sanwo-Olu, all emerged with his backing. "
      "Ambode, who fell out of favour, lost his bid for a second term. "
      "Tinubu carries the traditional title, Jagaban of Borgu. To many, he is simply: the godfather.",
      broll=[('tinubu-lagos-allies-award.jpg', 'Tinubu with Lagos political allies', 'At a Lagos State event', 'archive photo'), ('tinubu-lagos-allies-retreat.jpg', 'Tinubu with Lagos political allies', 'At a Lagos strategy retreat', 'archive photo')])
scene("occupy", "THE KINGMAKER", "occupy", "Occupy Nigeria", "Fuel subsidy protests · January 2012",
      "In January twenty twelve, President Goodluck Jonathan removed the fuel subsidy. Petrol prices more than doubled overnight, "
      "from sixty-five to one hundred and forty-one naira a litre. "
      "Lagos ground to a halt as the Occupy Nigeria protests and a nationwide strike filled the streets. "
      "Tinubu and his party stood against the removal. In an article, he accused Jonathan of breaking the social contract, "
      "writing that the government had tossed the people into the depths of the midnight sea. "
      "After more than a week of protests, the price was cut back to ninety-seven naira.", trans="glitch", hit=True,
      broll=[('occupy-nigeria-nyc-2012.jpg', 'Occupy Nigeria', 'Solidarity protest, New York, 10 January 2012', 'Michael Fleshman / Flickr, CC BY-SA 2.0')])
scene("apc", "THE KINGMAKER", "merger", "Birth of the APC", "2013 merger · 2015 opposition victory",
      "In two thousand and thirteen, he helped engineer one of the most important mergers in Nigerian history. "
      "His Action Congress of Nigeria joined Muhammadu Buhari's party and others to form the All Progressives Congress. "
      "In two thousand and fifteen, the APC did what no opposition had done before: it defeated a sitting president at the ballot box. "
      "Tinubu's former Attorney General in Lagos, Yemi Osinbajo, became Vice President. "
      "But before his own turn came, the questions about his money would only grow louder.", trans="flash", hit=True,
      broll=[('chatham-house-2011.jpg', 'Tinubu at Chatham House, London', '“Democracy in Nigeria and the Rebirth of Opposition”, 18 July 2011', 'Chatham House, CC BY 2.0'), ('tinubu-buhari-alliance.jpg', 'Tinubu and Buhari', 'The alliance behind the APC', 'via Daily Post Nigeria'), ('eagle-square-2015.jpg', 'Eagle Square, Abuja, 29 May 2015', 'Goodluck Jonathan hands over to Muhammadu Buhari', 'U.S. Department of State, public domain'), ('tinubu-buhari-hands-raised.jpg', 'Tinubu and Buhari', 'Hands raised at an APC rally', 'archive photo')])

# ---------------------------------------------------------------- 6
chapter_card(6, "THE CONTROVERSIES", "tension")
scene("case1993", "THE CONTROVERSIES", "case1993", "U.S. civil forfeiture case, 1993", "Settled · $460,000 forfeited · no criminal charge",
      "But alongside the rise came persistent questions about money. "
      "In nineteen ninety-three, United States federal prosecutors in Chicago alleged that funds in bank accounts linked to Tinubu were connected to proceeds of heroin trafficking. "
      "Tinubu was never charged with a crime. The case ended in a settlement, in which four hundred and sixty thousand dollars was forfeited. "
      "He has always denied any wrongdoing.", trans="glitch")
scene("certificate", "THE CONTROVERSIES", "certificate", "The certificate dispute", "1999 election form · 2023 Chicago State University records",
      "In nineteen ninety-nine, his election papers listed the University of Chicago, which said it had no record of him. He blamed the error on aides. "
      "During the twenty twenty-three election dispute, rival candidate Atiku Abubakar obtained records from Chicago State University through a U.S. court. "
      "The university confirmed that Tinubu graduated, but questions over the certificate he submitted to the electoral commission fuelled fierce debate. "
      "The Supreme Court declined to consider the new evidence.", trans="glitch")
scene("cct", "THE CONTROVERSIES", "cct", "Tribunal & consultancy allegations", "Code of Conduct Tribunal, 2011 · Alpha Beta Consulting",
      "In two thousand and eleven, he was tried before the Code of Conduct Tribunal over allegations of operating foreign bank accounts while governor. The tribunal discharged him. "
      "Critics have also pointed to Alpha Beta Consulting, a private firm that handled revenue work for Lagos State, alleging links to Tinubu. He denies having any stake in it.")
scene("bullion", "THE CONTROVERSIES", "bullion", "Bullion vans at his Lagos residence", "Eve of the 2019 general election",
      "And on the eve of the twenty nineteen general election, cameras filmed bullion vans entering his Lagos residence. "
      "Asked about it, Tinubu said that if he had money to spend, it was his own money, not the government's.", trans="glitch", hit=True)

# ---------------------------------------------------------------- 7
chapter_card(7, "#ENDSARS", "dark")
scene("endsars", "#ENDSARS", "endsars", "#EndSARS protests", "Nationwide, October 2020 · against police brutality",
      "In October twenty twenty, young Nigerians filled the streets in the #EndSARS protests, demanding an end to brutality by the police Special Anti-Robbery Squad. "
      "Lagos, Tinubu's political home, became the centre of the movement.", trans="dip",
      broll=[('endsars-lagos-2020.jpg', '#EndSARS protest, Lagos', '12 October 2020', 'Jerry Jallo / Heinrich Böll Stiftung, CC BY-SA 2.0'), ('endsars-protest-2020.jpg', '#EndSARS protesters', '“#WeSayNoToPoliceBrutality”, October 2020', 'via Al Jazeera')])
scene("lekki", "#ENDSARS", "lekki", "Lekki Toll Gate, Lagos", "Night of 20 October 2020",
      "On the night of the twentieth of October, soldiers opened fire on protesters gathered at the Lekki toll gate. "
      "A judicial panel set up by the Lagos State government later described it as a massacre. "
      "The army and the federal government rejected that finding, and the exact number of victims is still disputed.", trans="flash", hit=True,
      broll=[('lekki-tollgate-afp-2020.jpg', 'Lekki toll gate, Lagos', 'About 2,000 protesters blocked one of the main roads into Lagos', 'Pius Utomi Ekpei / AFP / Getty'), ('lekki-toll-gate-protest-2020.jpg', 'Protesters at the Lekki toll gate', 'Lagos, October 2020', 'via Foreign Policy'), ('lekki-night-injured-2020.jpg', 'Lekki toll gate, night of 20 October 2020', 'People try to help a man injured when security forces opened fire', 'Adetona Omokanye / Getty')])
scene("witness", "#ENDSARS", "witness", "A survivor's account", "Agbeze Ifeanyi Matthew, 35, from Ondo State",
      "Agbeze Ifeanyi Matthew, a thirty-five-year-old from Ondo State, was at the toll gate that night. "
      "He later told The Guardian: "
      "What happened was the worst memory I can never forget. When they got to the toll gate, they immediately started shooting. "
      "He was shot in the chest, and survived.", trans="dip", mood="dark", hold=1.8,
      broll=[('agbeze-ifeanyi-matthew.jpg', 'Agbeze Ifeanyi Matthew', 'Shot in the chest at Lekki toll gate, 20 October 2020', 'Handout, via The Guardian')])
scene("witness2", "#ENDSARS", "witness2", "A survivor's account", "Isaiah Ekabo, 32, from Lagos",
      "Isaiah Ekabo, a thirty-two-year-old from Lagos, joined the protests from the first day. "
      "In Nigeria, in a so-called democracy, he said, I was running from police who were trying to end my life, because of protests. "
      "A year later, the architecture graduate told The Guardian that just surviving in Nigeria was too much: no light, no roads, few jobs, bad water. "
      "Like many young Nigerians, he hoped to leave.", mood="dark", hold=1.6,
      broll=[('endsars-cake-reuters.jpg', 'A cake made for an #EndSARS protest', 'Lagos, October 2020', 'Temilade Adelaja / Reuters')])
scene("memorial", "#ENDSARS", "memorial", "", "", trans="dip", mood="outro", hold=7.5)
scene("tvc", "#ENDSARS", "fire", "Aftermath in Lagos", "Media houses linked to Tinubu set ablaze",
      "In the chaos that followed, the TVC television station and The Nation newspaper, both linked to Tinubu, were set on fire. "
      "Protesters had seen him as a symbol of the Lagos establishment. Tinubu denied owning the Lekki toll gate, and called for calm. "
      "For many young Nigerians, the events of that night still shape how they see the political class. "
      "And two years later, the man many protesters saw as the face of the establishment would be on the ballot.", hold=1.6,
      broll=[('nigeria-is-bleeding-2020.jpg', '“Nigeria is bleeding”', '#EndSARS protest, October 2020', 'via Marie Claire UK'), ('end-sars-now-flag.jpg', '“End SARS Now”', 'A protester with a Nigerian flag, Lagos, 2020', 'Pius Utomi Ekpei / AFP / Getty')])

# ---------------------------------------------------------------- 8
chapter_card(8, "\"IT'S MY TURN\"", "epic")
scene("emilokan", "\"IT'S MY TURN\"", "quote_emilokan", "Abeokuta, Ogun State", "June 2022",
      "That was Tinubu in Abeokuta, in June twenty twenty-two, speaking to party delegates in Yoruba. "
      "Emi lo kan. It is my turn. "
      "He reminded them that he had helped make Buhari president, and said he had never begged for anything in return. "
      "Days later, he won the APC primary, beating Vice President Osinbajo and others.",
      trans="flash", hit=True, slam="Emi lo kan.")
scene("ticket", "\"IT'S MY TURN\"", "ticket", "The Muslim–Muslim ticket", "Running mate: Kashim Shettima",
      "His choice of running mate, Kashim Shettima, who like Tinubu is a Muslim, broke an unwritten convention of balancing the ticket between Christians and Muslims, "
      "and drew strong criticism, particularly from Christian leaders.",
      broll=[('tinubu-shettima-campaign.jpg', 'Tinubu and Shettima', 'On the campaign trail', 'via Leadership Newspaper')])
scene("results", "\"IT'S MY TURN\"", "results", "2023 presidential election", "Official INEC results · 25 February 2023",
      "On February twenty-fifth, twenty twenty-three, Nigerians voted. The electoral commission declared Tinubu the winner, with about eight point eight million votes, roughly thirty-seven percent, "
      "ahead of Atiku Abubakar and Peter Obi. It was the lowest winning share of Nigeria's Fourth Republic, on a turnout of under thirty percent. "
      "He even lost his own stronghold, Lagos, to Peter Obi.", trans="zoom", hit=True)
scene("court", "\"IT'S MY TURN\"", "court", "Supreme Court, Abuja", "26 October 2023 · victory upheld",
      "His rivals alleged rigging and failures in the electronic transmission of results. The tribunal dismissed their petitions, "
      "and on October twenty-sixth, twenty twenty-three, the Supreme Court upheld his victory. "
      "But by then, his first day in office had already delivered one sentence that would change everything.")

# ---------------------------------------------------------------- 9
chapter_card(9, "THE PRESIDENCY", "epic")
scene("sworn", "THE PRESIDENCY", "quote_subsidy", "Eagle Square, Abuja", "Inauguration · 29 May 2023",
      "On May twenty-ninth, twenty twenty-three, Tinubu was sworn in as Nigeria's sixteenth president. "
      "In his inaugural speech, he made a declaration that shook the economy: Fuel subsidy is gone.", trans="flash", hit=True,
      hold=3.0, slam="Fuel subsidy is gone.",
      broll=[('official-portrait-2023.jpg', 'President Bola Ahmed Tinubu', 'Official pre-inauguration portrait, May 2023', 'Nosa Asemota, CC BY-SA 4.0')])
scene("uturn", "THE PRESIDENCY", "uturn", "Then and now", "Tinubu on fuel subsidy removal · 2012 vs 2023",
      "For many Nigerians, the irony was impossible to miss. "
      "Eleven years earlier, the same man had condemned the very same policy, when it was Goodluck Jonathan's. "
      "His allies argue that the subsidy had become unaffordable, and that only a leader with his political strength could finally end it. "
      "His critics call it the ultimate U-turn.", trans="glitch", hit=True, mood="tension")
scene("economy", "THE PRESIDENCY", "economy", "Economic shock", "Petrol · exchange rate · inflation, 2023 – 2024",
      "Petrol prices nearly tripled almost overnight. Weeks later, his government unified the exchange rates, and the naira lost more than two thirds of its value against the dollar. "
      "Inflation climbed above thirty percent, its highest level in nearly three decades, with food prices rising even faster.", trans="glitch", mood="tension",
      broll=[('@fuelprice', 'Price at the pump', 'Petrol per litre, 1999 – 2024', 'chart: official / NNPC pump prices')])
scene("protest", "THE PRESIDENCY", "protest", "#EndBadGovernance protests", "August 2024",
      "Supporters call these painful but necessary reforms, long avoided by previous governments, and welcomed by investors and international lenders. "
      "But for millions of ordinary Nigerians, the cost of living became a crisis. "
      "In August twenty twenty-four, young people took to the streets again, under the banner: End Bad Governance. Amnesty International later reported that at least twenty-four people were killed, and more than twelve hundred detained. "
      "For a man who began his career in the pro-democracy struggle, and who once stood against subsidy removal alongside the protesters of twenty twelve, "
      "the roles had now been reversed.",
      mood="dark",
      broll=[('endbadgovernance-march-2024.jpg', '#EndBadGovernance march', 'August 2024', 'via Amnesty International')])
scene("record", "THE PRESIDENCY", "ledger", "The record so far", "Reforms and criticisms",
      "His government raised the national minimum wage to seventy thousand naira, launched a student loan scheme, and pushed through sweeping tax reforms. "
      "It also faced criticism over a new presidential jet, the cost of the Lagos–Calabar coastal highway, "
      "and, in March twenty twenty-five, a state of emergency in Rivers State that suspended an elected governor.", mood="warm",
      broll=[('abuja-2024-lammy.jpg', 'State House, Abuja', 'With UK Foreign Secretary David Lammy, 4 November 2024', 'FCDO, CC BY 2.0'), ('blinken-tinubu-2024.jpg', 'State House, Abuja', 'With U.S. Secretary of State Antony Blinken, 23 January 2024', 'U.S. Department of State, public domain')])

# ---------------------------------------------------------------- outro
scene("next", "LEGACY", "ticket", "The road to 2027", "Nomination submitted, July 2026",
      "And the story is not over. In July twenty twenty-six, Tinubu kept Kashim Shettima as his running mate, "
      "and submitted his nomination to run again in twenty twenty-seven. "
      "The man who once said it was his turn now wants another one.", trans="flash", hit=True, mood="epic",
      broll=[('tinubu-shettima-2027.jpg', 'Tinubu and Shettima', 'Running together again for 2027', 'via Arise News')])
scene("rise", "LEGACY", "rise", "How he rose", "From market woman's son to president",
      "So how did he do it? Step by step. "
      "A market woman's son who learned the power of networks. "
      "An accountant who learned how money moves. "
      "A senator, and then an exile, who earned credibility fighting a dictator. "
      "A governor who rebuilt Lagos's finances, and with them, a war chest and a machine. "
      "A kingmaker who made others governor, vice president, and president. "
      "And finally, a candidate who told his party: it is my turn. "
      "Every step built the next. That is how Bola Ahmed Tinubu rose to power.", trans="dip", mood="epic", hold=1.4)
scene("legacy", "LEGACY", "legacy", "", "",
      "So who is Bola Ahmed Tinubu? A democrat who resisted military rule, or a godfather who mastered the system? "
      "A reformer making hard choices, or a leader whose decisions have deepened hardship? "
      "The answer depends on who you ask. What is certain is that, for more than three decades, few people have shaped Nigeria's politics more. "
      "And the final verdict on his legacy, is still being written.", trans="dip", mood="outro", hold=2.5)
scene("people", "", "people", "", "",
      "But this story was never only about one man. "
      "It is the story of the fishermen on the lagoon at dawn, of the market women of Lagos, of a nation of more than two hundred and fifty peoples, "
      "still learning how to live as one. "
      "It is the story of the young Nigerians who filled the streets in twenty twenty, and of the ones who never came home. "
      "At the Lekki toll gate, one protester held up a cardboard sign. "
      "It read: The power of the people is stronger than the people in power.", trans="dip", mood="outro", hold=4.0,
      broll=[('lagos-lagoon-dawn.jpg', 'The Lagos Lagoon at dawn', '', 'dotun55 / Flickr, CC BY-SA 2.0'),
             ('endsars-lagos-2020.jpg', '#EndSARS, Lagos', '12 October 2020', 'Jerry Jallo / Heinrich Böll Stiftung, CC BY-SA 2.0'),
             ('lekki-toll-gate-protest-2020.jpg', 'Lekki toll gate', 'October 2020', 'via Foreign Policy')])
scene("credits", "", "credits", "", "", trans="dip", mood="outro", hold=9.0)
