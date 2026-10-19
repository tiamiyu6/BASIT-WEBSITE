"""Write the YouTube title, description (with chapter timestamps from the real timeline), tags and credits.

usage (from documentary/):  python3 mrmoney/publish.py BUILD_DIR  -> mrmoney/YOUTUBE.md
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from archive import CLIPS

TL = json.load(open(os.path.join(sys.argv[1], "timeline.json")))


def ts(t):
    t = int(t)
    return f"{t // 60}:{t % 60:02d}"


chapters = [("0:00", "A boy on the parlour floor")]
for e in TL:
    if e.get("card"):
        chapters.append((ts(e["start"]), e["card"]["word"].title() if e["card"]["word"] not in ("M$NEY",) else "M$NEY"))
end = next(e for e in TL if e["id"] == "e1")
chapters.append((ts(end["start"]), "He made this documentary"))

credits = open(os.path.join(HERE, "photos", "CREDITS.txt")).read().strip() if os.path.exists(os.path.join(HERE, "photos", "CREDITS.txt")) else ""
sources = sorted({c["credit"] for c in CLIPS.values()})

md = f"""# MR MONEY: The Asake Story · YouTube upload sheet

## Title (pick one)
1. **He Was Told NO By His Own Father. Now He's Mr Money | The Asake Story**
2. How A Stubborn Boy From Lagos Became Mr Money (Asake Documentary)
3. Asake: The Stubborn Boy Who Became Mr Money | Naija Untold

## Description
September 2022. A boy is lying on the floor of his father's parlour in Lagos. WAEC is finished. JAMB is finished. Then a song comes on.

This is the story of Ahmed Ololade, "Giran", the stubborn one: the boy who left home at fifteen for music, refused a UK passport, studied theatre at OAU, begged Olamide for a reply for two years, and became Mr Money. Brixton, the O2, Barclays Center, Lungu Boy, Giran Republic, M$NEY and Drury Lane.

Which Asake song found you when you needed it? Tell us in the comments.

**Chapters**
""" + "\n".join(f"{a} {b}" for a, b in chapters) + f"""

**Sources & credits**
- Archive excerpts (short, credited, used for commentary and documentary purposes): {"; ".join(sources)}
- Photos under Creative Commons licences, credited on screen. Full list below.
- Original score, sound design and 3D animation: Naija Untold.
- Lament cue: "Long Note Four" by Kevin MacLeod (incompetech.com), licensed under Creative Commons: By Attribution 4.0.

{credits}

#Asake #MrMoney #Documentary #Afrobeats #NaijaUntold #Giran #YBNL

## Tags
Asake, Asake documentary, Mr Money, Mr Money with the Vibe, Asake story, Ahmed Ololade, Giran Republic, Asake Olamide, YBNL, Lungu Boy, Work of Art, M$NEY, Afrobeats documentary, Naija Untold, Asake Brixton, Asake O2, Asake Barclays, Nigerian music documentary

## Settings
- Category: Music (or Film & Animation). Made for kids: No. Altered/synthetic content: the narration voice is synthetic, so tick **Yes**.
- End screen: subscribe button + the best-performing Naija Untold video, from {ts(TL[-1]["start"])}.
- Pinned comment: "Which Asake song found you when you needed it? 👇"
"""
open(os.path.join(HERE, "YOUTUBE.md"), "w").write(md)
print(md[:1500])
