"""June 12 TikToks: each short is rendered as one story whose LAST sentence is the hook.
The vertical video then starts at that hook sentence and wraps around, so the end of the
video runs straight back into its own opening line (a seamless loop).

usage: SHORT12=<name> J12_SCRIPT=shorts12 ...   names: tea, won, offer
"""
import os
from script12 import photo, paper, typed, footage, sc, clip, PH, BR, CL

SHORTS = {
    # hook: "He took a sip."  ->  loops back into "Moments later, he collapsed."
    "tea": dict(
        headline=("HE TOOK", "ONE SIP..."),
        scenes=[
            sc("t1", "Moments later, he collapsed. And the man Nigerians elected as president was dead.",
               [paper(PH + "paper-abiola-poisoned-1998.jpg", 0, focus=(0.3, 0.45))], mood="lament", hold=0.3),
            sc("t2", "His name was MKO Abiola. On June 12, 1993, fourteen million Nigerians voted, and he won.",
               [photo(PH + "mko-votes-june12.jpg", 0, focus=(0.6, 0.3))], mood="lament", hold=0.3),
            sc("t3", "The soldiers cancelled the election. When he declared himself president, they arrested him.",
               [typed([("23 JUNE 1993", 0), ("", 0), ("!ANNULLED", 0)], 0, big=True)], mood="lament", hold=0.3),
            sc("t4", "His wife, Kudirat, was shot dead on a Lagos road. He spent four years in solitary confinement.",
               [photo(PH + "kudirat-portrait.jpg", 0, focus=(0.5, 0.4))], mood="lament", hold=0.3),
            sc("t5", "Then the dictator died. And in July 1998, in a room with American diplomats, they poured MKO Abiola a cup of tea.",
               [typed(["7 JULY 1998"], 0, big=True), photo(PH + "abacha-uniform-portrait.jpg", 0, focus=(0.5, 0.35), grade="bw")],
               mood="lament", hold=0.15, teacup=True),
            sc("hook", "He took a sip.",
               [photo(BR + "abiola-portrait.jpg", 0, focus=(0.5, 0.35), grade="bw", move="in")], mood="lament", hold=0.35, xf=0.15),
        ],
    ),
    # hook: "He won."  ->  loops back into "Fourteen million Nigerians..."
    "won": dict(
        headline=("HE WON.", "THEY CANCELLED IT."),
        scenes=[
            sc("w1", "Fourteen million Nigerians, Muslims and Christians, North and South, chose the same man.",
               [photo(PH + "open-ballot-queue-1993.jpg", 0, focus=(0.5, 0.45))], mood="dark", hold=0.2),
            clip("w2", "ibb_annulment_1993.mp4", 0.45, 8.9, "General Ibrahim Babangida, June 1993"),
            sc("w3", "Free, fair and peaceful. Then the general cancelled it anyway.",
               [typed([("12 JUNE 1993 ELECTION", 0), ("", 0), ("!ANNULLED", 1)], 0, big=True)], mood="dark", hold=0.3),
            sc("w4", "The winner was jailed. His wife was shot dead. He died in custody, five years after the vote.",
               [photo(PH + "kudirat-car-1996.jpg", 1, focus=(0.5, 0.5), grade="bw"),
                photo(BR + "abiola-portrait.jpg", 0, focus=(0.5, 0.35), grade="bw")], mood="dark", hold=0.3),
            sc("w5", "Thirty-two years later, that same general finally admitted what Nigeria always knew. MKO Abiola?",
               [photo(PH + "ibb-broadcast-1993.jpg", 0, focus=(0.55, 0.45), grade="bw")], mood="dark", hold=0.1),
            sc("hook", "He won.",
               [photo(PH + "mko-votes-june12.jpg", 0, focus=(0.6, 0.3), move="in")], mood="dark", hold=0.35, xf=0.15),
        ],
    ),
    # hook: "Give up the mandate, and you can go home."  ->  loops into "That was the offer."
    "offer": dict(
        headline=("THEY OFFERED HIM", "FREEDOM. HE SAID NO."),
        scenes=[
            sc("o1", "That was the offer. MKO Abiola, one of the richest men in Africa, said no.",
               [photo(BR + "abiola-portrait.jpg", 0, focus=(0.5, 0.35), grade="bw")], mood="resolve", hold=0.2),
            sc("o2", "He had built schools, mosques and churches across twenty-four states. And he had just won the freest election in Nigeria's history.",
               [typed(["63  schools", "41  libraries", "121 mosques & churches"], 0, big=True),
                photo(PH + "mko-votes-june12.jpg", 1, focus=(0.6, 0.3))], mood="resolve", hold=0.2),
            sc("o3", "The soldiers cancelled it, and locked him in solitary confinement.",
               [paper(PH + "concord-abiola-playing-with-fire.jpg", 0, focus=(0.5, 0.5))], mood="resolve", hold=0.2),
            sc("o4", "His wife was murdered fighting for him. He died in custody in 1998. He never gave in.",
               [photo(PH + "kudirat-portrait.jpg", 0, focus=(0.5, 0.4)), photo(PH + "kudirat-coffin-1996.jpg", 1, focus=(0.5, 0.4), grade="bw")],
               mood="resolve", hold=0.2),
            sc("o5", "Because for four years, again and again, the soldiers made him the same offer.",
               [photo(PH + "abacha-uniform-portrait.jpg", 0, focus=(0.5, 0.35))], mood="resolve", hold=0.1),
            sc("hook", "Give up the mandate, and you can go home.",
               [photo(BR + "abiola-victory-1993.jpg", 0, focus=(0.5, 0.35), move="in")], mood="resolve", hold=0.35, xf=0.15),
        ],
    ),
}

NAME = os.environ.get("SHORT12", "tea")
S = SHORTS[NAME]["scenes"]
HEADLINE = SHORTS[NAME]["headline"]
