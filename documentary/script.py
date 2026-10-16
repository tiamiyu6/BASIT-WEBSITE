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


def scene(id, chapter, plate, title, sub, text="", trans="fade", mood=None, hit=False, hold=1.0, slam=None, broll=()):
    S.append(dict(id=id, chapter=chapter, plate=plate, title=title, sub=sub, text=text,
                  trans=trans, mood=mood, hit=hit, hold=hold, slam=slam, broll=list(broll)))


def chapter_card(num, name, mood):
    scene(f"ch{num}", name, "chapter", f"CHAPTER {num}", name, trans="dip", mood=mood, hit=True, hold=3.2)


# ---------------------------------------------------------------- cold open
# Starts on his portrait and pushes into his eye; the story "begins" inside it.
# Real photo: documentary/photos/portrait.jpg (+ optional photos/portrait.json {"eye": [x, y]} in 0..1 coords)
scene("portrait", "", "portrait", "", "", trans="dip", mood="intro", hold=7.0)
scene("open", "", "open", "", "",
      "In Nigerian politics, few names carry as much weight, or as many questions, as Bola Ahmed Tinubu. "
      "To his supporters, he is a master builder: the architect of modern Lagos, and the kingmaker who finally claimed the crown. "
      "To his critics, he is the ultimate political godfather, whose wealth and past have never been fully explained. "
      "This is his story.",
      trans="flash", mood="intro", hold=0.6)
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
      "According to his official biography, Bola Ahmed Adekunle Tinubu was born on the twenty-ninth of March, nineteen fifty-two, in Lagos, into a Yoruba Muslim family. "
      "His mother, Abibatu Mogaji, would become a powerful leader of the Lagos market women. "
      "An early lesson in how grassroots networks turn into power.")
scene("chicago", "ORIGINS", "chicago", "Chicago, United States", "Studied accounting · graduated Chicago State University, 1979",
      "In the mid nineteen-seventies he travelled to the United States. "
      "He studied at Richard J. Daley College, then at Chicago State University, graduating in nineteen seventy-nine with a degree in accounting. "
      "He worked for firms including Arthur Andersen and Deloitte, before returning home to join Mobil Oil Nigeria, where he rose to become a senior finance executive.")
scene("questions", "ORIGINS", "questions", "Disputed records", "Age, early schooling and documents questioned by critics",
      "Yet even these early chapters are contested. "
      "Over the years, critics have questioned his age, his schooling in Nigeria, and documents he submitted to electoral authorities. "
      "Tinubu has consistently rejected these claims, and no court has disqualified him over them.",
      trans="glitch", mood="tension")

# ---------------------------------------------------------------- 3
chapter_card(3, "DEMOCRACY & EXILE", "tension")
scene("senate", "DEMOCRACY & EXILE", "senate", "Senator, Lagos West", "Social Democratic Party (SDP) · 1992",
      "His political career began in nineteen ninety-two, when he won a Senate seat for Lagos West under the Social Democratic Party, "
      "during General Ibrahim Babangida's promised transition to civilian rule.")
scene("june12", "DEMOCRACY & EXILE", "june12", "12 June 1993", "Presidential election annulled by the military",
      "That transition collapsed. The June twelfth, nineteen ninety-three presidential election, widely seen as won by Moshood Abiola, was annulled by the military. "
      "Months later, General Sani Abacha seized power, and dissolved the Senate.", trans="flash", hit=True)
scene("exile", "DEMOCRACY & EXILE", "exile", "Exile", "NADECO pro-democracy campaign · 1994 – 1998",
      "Tinubu joined the National Democratic Coalition, NADECO, which campaigned for a return to democracy. "
      "Facing threats under Abacha's regime, he fled into exile in nineteen ninety-four, returning only after Abacha's death in nineteen ninety-eight.")

# ---------------------------------------------------------------- 4
chapter_card(4, "GOVERNOR OF LAGOS", "warm")
scene("gov", "GOVERNOR OF LAGOS", "lagos", "Governor of Lagos State", "Alliance for Democracy · 1999 – 2007",
      "In nineteen ninety-nine, as Nigeria returned to civilian rule, he was elected Governor of Lagos State on the platform of the Alliance for Democracy. "
      "He was re-elected in two thousand and three.", trans="zoom", hit=True,
      broll=[('victoria-island-2014.jpg', 'Lagos', 'Victoria Island and the lagoon, 2014', 'OpenUpEd / Flickr, CC BY 2.0')])
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
      "Tinubu carries the traditional title, Jagaban of Borgu. To many, he is simply: the godfather.")
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
      "Tinubu's former Attorney General in Lagos, Yemi Osinbajo, became Vice President.", trans="flash", hit=True,
      broll=[('chatham-house-2011.jpg', 'Tinubu at Chatham House, London', '“Democracy in Nigeria and the Rebirth of Opposition”, 18 July 2011', 'Chatham House, CC BY 2.0'), ('eagle-square-2015.jpg', 'Eagle Square, Abuja, 29 May 2015', 'Goodluck Jonathan hands over to Muhammadu Buhari', 'U.S. Department of State, public domain')])

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
      broll=[('lekki-toll-gate-protest-2020.jpg', 'Protesters at the Lekki toll gate', 'Lagos, October 2020', 'via Foreign Policy')])
scene("tvc", "#ENDSARS", "fire", "Aftermath in Lagos", "Media houses linked to Tinubu set ablaze",
      "In the chaos that followed, the TVC television station and The Nation newspaper, both linked to Tinubu, were set on fire. "
      "Protesters had seen him as a symbol of the Lagos establishment. Tinubu denied owning the Lekki toll gate, and called for calm. "
      "For many young Nigerians, the events of that night still shape how they see the political class.", hold=1.6,
      broll=[('nigeria-is-bleeding-2020.jpg', '“Nigeria is bleeding”', '#EndSARS protest, October 2020', 'via Marie Claire UK')])

# ---------------------------------------------------------------- 8
chapter_card(8, "\"IT'S MY TURN\"", "epic")
scene("emilokan", "\"IT'S MY TURN\"", "quote_emilokan", "Abeokuta, Ogun State", "June 2022",
      "By twenty twenty-two, Tinubu was ready to claim the prize. In a now famous speech in Abeokuta, he declared, in Yoruba: "
      "Emi lo kan. It is my turn. "
      "He argued that he had helped make others president, and deserved his chance. He then won the APC primary against Vice President Osinbajo and others.",
      trans="flash", hit=True, slam="Emi lo kan.")
scene("ticket", "\"IT'S MY TURN\"", "ticket", "The Muslim–Muslim ticket", "Running mate: Kashim Shettima",
      "His choice of running mate, Kashim Shettima, who like Tinubu is a Muslim, broke an unwritten convention of balancing the ticket between Christians and Muslims, "
      "and drew strong criticism, particularly from Christian leaders.")
scene("results", "\"IT'S MY TURN\"", "results", "2023 presidential election", "Official INEC results · 25 February 2023",
      "On February twenty-fifth, twenty twenty-three, Nigerians voted. The electoral commission declared Tinubu the winner, with about eight point eight million votes, roughly thirty-seven percent, "
      "ahead of Atiku Abubakar and Peter Obi. It was the lowest winning share of Nigeria's Fourth Republic, on a turnout of under thirty percent. "
      "He even lost his own stronghold, Lagos, to Peter Obi.", trans="zoom", hit=True)
scene("court", "\"IT'S MY TURN\"", "court", "Supreme Court, Abuja", "26 October 2023 · victory upheld",
      "His rivals alleged rigging and failures in the electronic transmission of results. The tribunal dismissed their petitions, "
      "and on October twenty-sixth, twenty twenty-three, the Supreme Court upheld his victory.")

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
      "Inflation climbed above thirty percent, its highest level in nearly three decades, with food prices rising even faster.", trans="glitch", mood="tension")
scene("protest", "THE PRESIDENCY", "protest", "#EndBadGovernance protests", "August 2024",
      "Supporters call these painful but necessary reforms, long avoided by previous governments, and welcomed by investors and international lenders. "
      "But for millions of ordinary Nigerians, the cost of living became a crisis. "
      "In August twenty twenty-four, young people took to the streets again, under the banner: End Bad Governance. Rights groups reported that several protesters were killed. "
      "For a man who began his career in the pro-democracy struggle, and who once stood against subsidy removal alongside the protesters of twenty twelve, "
      "the roles had now been reversed.",
      mood="dark")
scene("record", "THE PRESIDENCY", "ledger", "The record so far", "Reforms and criticisms",
      "His government raised the national minimum wage to seventy thousand naira, launched a student loan scheme, and pushed through sweeping tax reforms. "
      "It also faced criticism over a new presidential jet, the cost of the Lagos–Calabar coastal highway, "
      "and, in March twenty twenty-five, a state of emergency in Rivers State that suspended an elected governor.", mood="warm",
      broll=[('abuja-2024-lammy.jpg', 'State House, Abuja', 'With UK Foreign Secretary David Lammy, 4 November 2024', 'FCDO, CC BY 2.0'), ('blinken-tinubu-2024.jpg', 'State House, Abuja', 'With U.S. Secretary of State Antony Blinken, 23 January 2024', 'U.S. Department of State, public domain')])

# ---------------------------------------------------------------- outro
scene("legacy", "LEGACY", "legacy", "", "",
      "So who is Bola Ahmed Tinubu? A democrat who resisted military rule, or a godfather who mastered the system? "
      "A reformer making hard choices, or a leader whose decisions have deepened hardship? "
      "The answer depends on who you ask. What is certain is that, for more than three decades, few people have shaped Nigeria's politics more. "
      "And the final verdict on his legacy, is still being written.", trans="dip", mood="outro", hold=2.5)
scene("credits", "", "credits", "", "", trans="dip", mood="outro", hold=9.0)
