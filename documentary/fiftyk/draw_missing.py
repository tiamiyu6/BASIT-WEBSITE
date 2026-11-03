"""Draws pictures 14, 15, 17 of the Fiftyk film in code (flat paper-cut look) when ChatGPT pictures are missing.
usage: python3 fiftyk/draw_missing.py OUT_DIR"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = sys.argv[1]
S = 2
W, H = 1672 * S, 941 * S
SKIN, SKIN_D, HAIR = (160, 92, 52), (132, 72, 40), (46, 28, 24)
ORANGE, GOLD, GREEN, DGREEN, CREAM, TERRA, BROWN = (232, 96, 32), (240, 182, 40), (96, 140, 52), (44, 100, 60), (246, 226, 190), (200, 90, 50), (110, 60, 34)
rng = np.random.default_rng(7)


def canvas(bg):
    return Image.new("RGB", (W, H), bg)


def P(pts):
    return [(x * S, y * S) for x, y in pts]


def ell(d, cx, cy, rx, ry, fill):
    d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=fill)


def rrect(d, x0, y0, x1, y1, r, fill, outline=None, w=0):
    d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], r * S, fill=fill, outline=outline, width=w * S)


def bush(d, cx, cy, r, col):
    for dx, dy, k in [(-0.7, 0.2, 0.7), (0, -0.3, 1), (0.8, 0.1, 0.75), (0.2, 0.5, 0.8)]:
        ell(d, cx + dx * r, cy + dy * r, r * k, r * k, col)


def sun(d, cx, cy, r):
    for a in range(0, 360, 30):
        x0, y0 = cx + math.cos(math.radians(a)) * r * 1.35, cy + math.sin(math.radians(a)) * r * 1.35
        x1, y1 = cx + math.cos(math.radians(a)) * r * 1.8, cy + math.sin(math.radians(a)) * r * 1.8
        d.line([x0 * S, y0 * S, x1 * S, y1 * S], fill=(250, 200, 70), width=14 * S)
    ell(d, cx, cy, r, r, (252, 206, 80))


def person(d, cx, base, s=1.0, flip=1, top=ORANGE, hair=HAIR, face="smile", earring=True, skin=SKIN):
    f = lambda x: cx + x * s * flip
    g = lambda y: base + y * s
    # shoulders
    d.polygon(P([(f(-230), g(0)), (f(-190), g(-90)), (f(-80), g(-130)), (f(80), g(-130)), (f(190), g(-90)), (f(230), g(0))]), fill=top)
    # neck
    d.polygon(P([(f(-38), g(-130)), (f(38), g(-130)), (f(32), g(-190)), (f(-32), g(-190))]), fill=SKIN_D if skin == SKIN else skin)
    # hair behind
    for dx, dy, r in [(-95, -300, 85), (-40, -345, 95), (35, -350, 95), (95, -305, 85), (-100, -240, 60), (100, -240, 60)]:
        ell(d, f(dx), g(dy), r * s, r * s, hair)
    # face
    ell(d, f(0), g(-250), 92 * s, 108 * s, skin)
    # hair front fringe
    ell(d, f(0), g(-340), 100 * s, 50 * s, hair)
    # eyes + brows
    for ex in (-34, 34):
        ell(d, f(ex), g(-255), 11 * s, 8 * s, (255, 245, 230))
        ell(d, f(ex + 3 * flip), g(-255), 6 * s, 6 * s, (30, 20, 20))
        d.line(P([(f(ex - 18), g(-282)), (f(ex + 18), g(-286))]), fill=hair, width=int(6 * S * s))
    # nose + mouth
    d.line(P([(f(2), g(-245)), (f(-4), g(-218)), (f(8), g(-216))]), fill=SKIN_D, width=int(5 * S * s))
    if face == "smile":
        d.arc([f(-30) * S - 0, g(-225) * S, f(30) * S, g(-185) * S] if flip == 1 else [f(30) * S, g(-225) * S, f(-30) * S, g(-185) * S], 20, 160, fill=(150, 40, 40), width=int(8 * S * s))
    elif face == "wow":
        ell(d, f(0), g(-200), 14 * s, 18 * s, (120, 30, 30))
    if earring:
        ell(d, f(-90), g(-235), 14 * s, 14 * s, GOLD)


def notes(d, x, y, w=120, h=60, n=3, col=(172, 138, 176)):
    for i in range(n):
        rrect(d, x + i * 7, y - i * 9, x + w + i * 7, y + h - i * 9, 8, col, (120, 90, 128), 3)
    rrect(d, x + w * 0.38, y - n * 9, x + w * 0.62 + n * 7, y + h - n * 9 + 2, 4, (230, 210, 150))


def coins(d, x, y, n=4, r=34):
    for i in range(n):
        yy = y - i * 13
        d.ellipse([(x - r) * S, (yy - r * 0.42) * S, (x + r) * S, (yy + r * 0.42) * S], fill=(212, 150, 24))
        d.ellipse([(x - r) * S, (yy - r * 0.42 - 8) * S, (x + r) * S, (yy + r * 0.42 - 8) * S], fill=GOLD, outline=(190, 130, 20), width=2 * S)


def safe(d, x, y, w, h, open_=True):
    rrect(d, x, y, x + w, y + h, 24, GOLD, (190, 130, 20), 6)
    rrect(d, x + 22, y + 22, x + w - 22, y + h - 22, 14, (150, 92, 20))
    if open_:
        d.polygon(P([(x + w - 30, y + 14), (x + w + 70, y - 26), (x + w + 70, y + h - 40), (x + w - 30, y + h - 14)]), fill=(222, 160, 34), outline=(190, 130, 20))
        ell(d, x + w + 28, y + h / 2 - 12, 22, 22, (190, 130, 20))
    ell(d, x + w * 0.5, y + h + 10, 4, 4, GOLD)
    for lx in (x + 20, x + w - 60):
        d.rectangle(P([(lx, y + h), (lx + 40, y + h + 20)]), fill=(120, 80, 20))


def grain(im):
    a = np.asarray(im).astype(np.int16)
    n = (rng.standard_normal((H // 3 + 1, W // 3 + 1)) * 7).astype(np.int16)
    n = np.kron(n, np.ones((3, 3), np.int16))[:H, :W, None]
    return Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8))


def finish(im, name):
    im = grain(im).resize((1672, 941), Image.LANCZOS)
    im.save(os.path.join(OUT, name))


def curved_arrow(d, p0, p1, p2, col=GOLD, w=22):
    pts = [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, 40)]
    d.line(P(pts), fill=col, width=w * S, joint="curve")
    ax, ay = pts[-1]
    ang = math.atan2(pts[-1][1] - pts[-4][1], pts[-1][0] - pts[-4][0])
    d.polygon(P([(ax + math.cos(ang) * 40, ay + math.sin(ang) * 40), (ax + math.cos(ang + 2.5) * 38, ay + math.sin(ang + 2.5) * 38), (ax + math.cos(ang - 2.5) * 38, ay + math.sin(ang - 2.5) * 38)]), fill=col)


# ---------------------------------------------------------------- 14: saved money into her own safe
im = canvas((246, 214, 160)); d = ImageDraw.Draw(im)
rrect(d, 560, 0, 1672, 941, 0, DGREEN)
d.polygon(P([(560, 0), (700, 0), (560, 330)]), fill=(246, 214, 160))
bush(d, 80, 160, 120, GREEN)
bush(d, 1560, 880, 140, (70, 120, 50))
d.rectangle(P([(0, 800), (1672, 941)]), fill=(150, 84, 46))
safe(d, 1000, 380, 360, 330)
notes(d, 780, 190, 150, 78, 3)
curved_arrow(d, (860, 280), (930, 150), (1060, 390), GOLD, 20)
# faded spending pile far left with stop mark
coins(d, 700, 790, 3, 44)
d.line(P([(630, 640), (770, 740)]), fill=(200, 50, 40), width=18 * S)
d.line(P([(770, 640), (630, 740)]), fill=(200, 50, 40), width=18 * S)
person(d, 250, 941, 1.25, 1, face="smile")
finish(im, "14.png")

# ---------------------------------------------------------------- 15: the scale, income tree heavier
im = canvas((248, 212, 150)); d = ImageDraw.Draw(im)
sun(d, 1380, 210, 100)
bush(d, 120, 820, 170, DGREEN); bush(d, 1560, 880, 190, GREEN)
d.rectangle(P([(0, 840), (1672, 941)]), fill=(150, 84, 46))
# stand
d.polygon(P([(780, 330), (890, 330), (930, 840), (740, 840)]), fill=BROWN)
ell(d, 835, 330, 52, 52, GOLD)
# beam tilted: left higher (small pile), right lower (tree)
lx, ly, rx, ry = 380, 300, 1290, 420
d.line(P([(lx, ly), (rx, ry)]), fill=(92, 50, 28), width=24 * S)
for (px, py) in ((lx, ly), (rx, ry)):
    d.line(P([(px, py), (px - 120, py + 230)]), fill=(120, 80, 40), width=8 * S)
    d.line(P([(px, py), (px + 120, py + 230)]), fill=(120, 80, 40), width=8 * S)
# left pan with a tight budget pile
d.pieslice(P([(lx - 150, ly + 130), (lx + 150, ly + 330)]), 0, 180, fill=GOLD)
notes(d, lx - 50, ly + 90, 100, 50, 2)
# right pan with big income tree
d.pieslice(P([(rx - 190, ry + 130), (rx + 190, ry + 330)]), 0, 180, fill=GOLD)
d.polygon(P([(rx - 18, ry + 240), (rx + 18, ry + 240), (rx + 10, ry - 20), (rx - 10, ry - 20)]), fill=BROWN)
for dx, dy, r in [(-110, -40, 85), (0, -130, 110), (115, -35, 90), (-40, -60, 90), (50, -70, 90)]:
    ell(d, rx + dx, ry + dy, r, r, GREEN if dx % 2 == 0 else (80, 130, 48))
for dx, dy in [(-90, -60), (30, -150), (110, -40), (-30, -100), (70, -100)]:
    coins(d, rx + dx, ry + dy, 1, 22)
person(d, 190, 941, 0.95, 1, face="smile")
finish(im, "15.png")

# ---------------------------------------------------------------- 17: showing her work, receiving a payment
im = canvas((242, 208, 150)); d = ImageDraw.Draw(im)
bush(d, 1500, 160, 150, GREEN); bush(d, 120, 120, 120, DGREEN)
d.rectangle(P([(0, 820), (1672, 941)]), fill=(150, 84, 46))
rrect(d, 560, 120, 1120, 380, 30, (232, 110, 44))              # stall awning
for i in range(7):
    d.polygon(P([(560 + i * 80, 380), (640 + i * 80, 380), (600 + i * 80, 430)]), fill=CREAM if i % 2 == 0 else TERRA)
# phone held by Amaka showing a design
rrect(d, 400, 560, 560, 820, 24, (40, 40, 44))
rrect(d, 414, 576, 546, 804, 14, (250, 238, 210))
d.polygon(P([(430, 760), (480, 640), (530, 760)]), fill=GREEN)
ell(d, 504, 610, 20, 20, GOLD)
# coins rising like steps
for i, (x, y) in enumerate([(930, 760), (1030, 700), (1130, 640), (1230, 580), (1330, 520)]):
    coins(d, x, y, 2 + i, 46)
person(d, 230, 941, 1.25, 1, face="smile")
person(d, 1430, 941, 1.2, -1, top=(60, 120, 150), hair=(30, 20, 18), earring=False, face="smile", skin=(122, 70, 40))
notes(d, 760, 800, 120, 60, 2)
finish(im, "17.png")
print("drawn")
