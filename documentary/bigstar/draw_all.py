"""Draws all 14 Bigstar pictures in code (flat illustration). usage: python3 bigstar/draw_all.py OUT_DIR"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
S = 2
W, H = 1672 * S, 941 * S
SKIN, SKIN_D = (92, 56, 36), (70, 42, 28)
GOLD, DGOLD = (240, 190, 50), (190, 140, 30)
rng = np.random.default_rng(3)


def P(pts): return [(x * S, y * S) for x, y in pts]
def ell(d, cx, cy, rx, ry, fill, outline=None, w=0): d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=fill, outline=outline, width=w * S)
def rr(d, x0, y0, x1, y1, r, fill, outline=None, w=0): d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], r * S, fill=fill, outline=outline, width=w * S)
def ln(d, pts, fill, w): d.line(P(pts), fill=fill, width=int(w * S), joint="curve")


def grad(top, bot):
    a = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array(top)[None, None, :] * (1 - a) + np.array(bot)[None, None, :] * a) * np.ones((H, W, 3))
    return Image.fromarray(arr.astype(np.uint8))


def finish(im, name):
    a = np.asarray(im).astype(np.int16)
    n = (rng.standard_normal((H // 3 + 1, W // 3 + 1)) * 5).astype(np.int16)
    n = np.kron(n, np.ones((3, 3), np.int16))[:H, :W, None]
    Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8)).resize((1672, 941), Image.LANCZOS).save(os.path.join(OUT, name))


def skyline(d, y, col, seed=1, lit=(255, 214, 120), night=False):
    r = np.random.default_rng(seed); x = 0
    while x < 1672:
        w = int(r.integers(70, 150)); h = int(r.integers(150, 420))
        d.rectangle(P([(x, y - h), (x + w, y)]), fill=col)
        for yy in range(y - h + 20, y - 20, 34):
            for xx in range(x + 14, x + w - 14, 28):
                if r.random() < (0.55 if night else 0.25): d.rectangle(P([(xx, yy), (xx + 14, yy + 18)]), fill=lit)
        x += w + 6


def star(d, cx, base, s=1.0, flip=1, shades=True, back=False, arms_up=False, smirk=True):
    f = lambda x: cx + x * s * flip
    g = lambda y: base + y * s
    tank = (30, 30, 36)
    # torso / muscular shoulders
    d.polygon(P([(f(-260), g(0)), (f(-235), g(-110)), (f(-170), g(-175)), (f(170), g(-175)), (f(235), g(-110)), (f(260), g(0))]), fill=tank)
    ell(d, f(-215), g(-100), 62 * s, 78 * s, SKIN); ell(d, f(215), g(-100), 62 * s, 78 * s, SKIN)       # delts
    d.polygon(P([(f(-70), g(-175)), (f(70), g(-175)), (f(40), g(-260)), (f(-40), g(-260))]), fill=SKIN_D)  # neck
    if not back:
        for i, rad in enumerate((70, 95, 120)):                                                           # chains
            d.arc([f(-rad) * S if flip == 1 else f(rad) * S, g(-215 + i * 14) * S, f(rad) * S if flip == 1 else f(-rad) * S, g(-215 + i * 14 + rad * 1.2) * S], 10, 170, fill=GOLD, width=int((9 - i * 1.5) * S * s))
        ell(d, f(0), g(-120), 22 * s, 26 * s, GOLD, DGOLD, 3)
    if arms_up:
        ln(d, [(f(-215), g(-130)), (f(-300), g(-330)), (f(-290), g(-470))], SKIN, 70 * s)
        ln(d, [(f(215), g(-130)), (f(300), g(-330)), (f(290), g(-470))], SKIN, 70 * s)
    # head
    ell(d, f(0), g(-340), 98 * s, 112 * s, SKIN)
    if back:
        ell(d, f(0), g(-350), 100 * s, 112 * s, (24, 18, 18))
    # dreads
    for k in range(-8, 9):
        x0 = k * 11.5; ln(d, [(f(x0), g(-440)), (f(x0 * 1.45), g(-370)), (f(x0 * 1.7 + (8 if k > 0 else -8)), g(-250 - abs(k) * -6))], (22, 16, 16), 17 * s)
    ell(d, f(0), g(-440), 100 * s, 38 * s, (22, 16, 16))
    if not back:
        if shades:
            rr(d, f(-80) if flip == 1 else f(0), g(-358), f(0) if flip == 1 else f(80), g(-318), 14 * s, (10, 10, 12))
            rr(d, f(2) if flip == 1 else f(-80), g(-358), f(80) if flip == 1 else f(-2), g(-318), 14 * s, (10, 10, 12))
            ln(d, [(f(-84), g(-340)), (f(84), g(-340))], (10, 10, 12), 6 * s)
        else:
            for ex in (-40, 40):
                ell(d, f(ex), g(-340), 12 * s, 9 * s, (250, 240, 225)); ell(d, f(ex + 3), g(-340), 6 * s, 6 * s, (20, 14, 14))
        d.line(P([(f(4), g(-320)), (f(-4), g(-292)), (f(10), g(-288))]), fill=SKIN_D, width=int(6 * S * s))
        if smirk:
            d.arc([f(-30) * S, g(-300) * S, f(40) * S, g(-262) * S] if flip == 1 else [f(40) * S, g(-300) * S, f(-30) * S, g(-262) * S], 15, 150, fill=(40, 12, 12), width=int(8 * S * s))
        ell(d, f(-96), g(-330), 10 * s, 10 * s, GOLD)


def person(d, cx, base, s=0.7, top=(60, 90, 140), skin=(150, 90, 56), hair=(22, 16, 16), flip=1, face="neutral"):
    f = lambda x: cx + x * s * flip
    g = lambda y: base + y * s
    d.polygon(P([(f(-190), g(0)), (f(-165), g(-100)), (f(-70), g(-140)), (f(70), g(-140)), (f(165), g(-100)), (f(190), g(0))]), fill=top)
    d.polygon(P([(f(-30), g(-140)), (f(30), g(-140)), (f(26), g(-190)), (f(-26), g(-190))]), fill=skin)
    ell(d, f(0), g(-250), 82 * s, 96 * s, hair); ell(d, f(0), g(-235), 76 * s, 90 * s, skin); ell(d, f(0), g(-320), 82 * s, 36 * s, hair)
    for ex in (-30, 30): ell(d, f(ex), g(-246), 9 * s, 7 * s, (250, 240, 225)); ell(d, f(ex + 2), g(-246), 5 * s, 5 * s, (20, 14, 14))
    if face == "worried": ln(d, [(f(-24), g(-196)), (f(0), g(-204)), (f(24), g(-196))], (80, 20, 20), 6 * s)
    elif face == "smile": d.arc([f(-26) * S, g(-215) * S, f(26) * S, g(-178) * S], 20, 160, fill=(120, 30, 30), width=int(7 * S * s))
    else: ln(d, [(f(-18), g(-196)), (f(18), g(-196))], (100, 30, 30), 6 * s)


def phone(d, x, y, w, h, glow=True, rot=0):
    if glow:
        for k in range(6): rr(d, x - 14 - k * 14, y - 14 - k * 14, x + w + 14 + k * 14, y + h + 14 + k * 14, 40, (255, 240, 200) if k > 4 else (250, 230, 170))
    rr(d, x, y, x + w, y + h, 24, (28, 28, 32)); rr(d, x + 10, y + 10, x + w - 10, y + h - 10, 16, (240, 246, 255))


def car(d, x, y, col, s=1.0):
    d.polygon(P([(x, y), (x + 60 * s, y - 70 * s), (x + 230 * s, y - 110 * s), (x + 420 * s, y - 100 * s), (x + 520 * s, y - 40 * s), (x + 560 * s, y)]), fill=col)
    rr(d, x - 10, y - 10 * s, x + 570 * s, y + 40 * s, 14, tuple(int(c * 0.7) for c in col))
    d.polygon(P([(x + 130 * s, y - 70 * s), (x + 235 * s, y - 100 * s), (x + 330 * s, y - 96 * s), (x + 360 * s, y - 70 * s)]), fill=(180, 220, 245))
    for wx in (x + 120 * s, x + 440 * s): ell(d, wx, y + 40 * s, 52 * s, 52 * s, (20, 20, 22)); ell(d, wx, y + 40 * s, 26 * s, 26 * s, (190, 190, 200))


# 01 POV bedroom
im = grad((255, 214, 150), (255, 240, 220)); d = ImageDraw.Draw(im)
rr(d, 160, 80, 1512, 640, 20, (255, 200, 120)); ell(d, 836, 360, 120, 120, (255, 240, 170))
skyline(d, 640, (110, 120, 150), 2); rr(d, 160, 80, 1512, 640, 20, None, (60, 50, 40), 14)
d.rectangle(P([(0, 640), (1672, 941)]), fill=(250, 248, 244))
for i in range(6): ln(d, [(0, 700 + i * 40), (1672, 690 + i * 44)], (232, 228, 224), 10)
phone(d, 1250, 680, 150, 240, glow=True)
ln(d, [(-40, 900), (300, 780), (620, 700)], SKIN, 120); ell(d, 640, 696, 62, 52, SKIN)
for k in range(4): ell(d, 360 + k * 30, 805 - k * 24, 28, 14, GOLD, DGOLD, 3)
finish(im, "01.png")
# 02 sitting on bed
im = grad((255, 224, 170), (255, 245, 232)); d = ImageDraw.Draw(im)
rr(d, 1000, 120, 1560, 560, 14, (255, 210, 130)); ell(d, 1280, 340, 80, 80, (255, 240, 170)); skyline(d, 560, (120, 130, 160), 4)
d.rectangle(P([(0, 700), (1672, 941)]), fill=(252, 250, 246)); rr(d, 100, 640, 1000, 941, 30, (250, 246, 240), (225, 220, 215), 6)
star(d, 520, 880, 1.45, 1, shades=True)
finish(im, "02.png")
# 03 penthouse back view
im = grad((24, 30, 70), (250, 160, 90)); d = ImageDraw.Draw(im)
ell(d, 840, 560, 110, 110, (255, 214, 130)); skyline(d, 760, (30, 36, 64), 6, night=True)
d.rectangle(P([(0, 760), (1672, 941)]), fill=(214, 206, 196)); rr(d, 0, 0, 1672, 760, 0, None, (60, 52, 44), 16)
for x in (420, 1250): ln(d, [(x, 0), (x, 760)], (60, 52, 44), 14)
star(d, 840, 941, 1.7, 1, back=True)
finish(im, "03.png")
# 04 driveway cars
im = grad((255, 200, 140), (255, 236, 200)); d = ImageDraw.Draw(im)
ell(d, 1400, 190, 100, 100, (255, 240, 170))
for x in (120, 1560): ln(d, [(x, 760), (x, 300)], (92, 70, 40), 22); [ell(d, x + dx, 280 + dy, 80, 38, (60, 130, 60)) for dx, dy in ((-60, 30), (40, 0), (0, 40), (80, 30))]
d.rectangle(P([(0, 700), (1672, 941)]), fill=(204, 198, 190))
car(d, 140, 760, (200, 40, 40), 1.25); car(d, 900, 800, (30, 70, 150), 1.25)
person(d, 760, 941, 0.95, top=(250, 250, 250), skin=(110, 70, 44))
for k in range(18): ell(d, 560 + (k * 53) % 480, 640 + (k * 37) % 150, 14 + k % 5 * 4, 14 + k % 5 * 4, (245, 250, 255), (210, 225, 240), 2)
finish(im, "04.png")
# 05 hallway
im = grad((250, 244, 232), (236, 226, 210)); d = ImageDraw.Draw(im)
d.polygon(P([(0, 0), (1672, 0), (1672, 760), (0, 760)]), fill=(246, 238, 224))
for x in range(160, 1672, 340): rr(d, x, 140, x + 200, 560, 10, (160, 210, 240), (80, 70, 60), 10)
d.rectangle(P([(0, 760), (1672, 941)]), fill=(182, 156, 126))
star(d, 520, 941, 1.45, 1, shades=False)
person(d, 1180, 941, 1.15, top=(26, 26, 34), skin=(120, 76, 48))
phone(d, 1330, 740, 90, 150, glow=False); rr(d, 1020, 770, 1140, 860, 10, (210, 214, 224))
finish(im, "05.png")
# 06 phone close-up
im = grad((24, 22, 36), (50, 40, 60)); d = ImageDraw.Draw(im)
phone(d, 640, 140, 400, 760, glow=True)
ell(d, 840, 420, 100, 100, (255, 90, 80)); rr(d, 740, 400, 940, 440, 12, (255, 255, 255))
for y in (560, 640, 720): rr(d, 710, y, 970, y + 28, 12, (200, 210, 230))
ln(d, [(300, 941), (500, 740), (700, 640)], SKIN, 150)
for k in range(4): ell(d, 560 + k * 28, 760 - k * 28, 26, 14, GOLD, DGOLD, 3)
finish(im, "06.png")
# 07 city night phones
im = grad((10, 14, 40), (30, 30, 70)); d = ImageDraw.Draw(im)
skyline(d, 941, (20, 24, 56), 9, night=True); skyline(d, 941, (30, 34, 72), 11, night=True)
for k in range(40):
    x = int(rng.integers(40, 1630)); y = int(rng.integers(120, 760))
    for r_ in range(5, 0, -1): ell(d, x, y, r_ * 14, r_ * 14, (60 + r_ * 20, 90 + r_ * 22, 160 + r_ * 18))
    rr(d, x - 14, y - 24, x + 14, y + 24, 5, (230, 240, 255))
finish(im, "07.png")
# 08 woman by SUV at dusk
im = grad((70, 40, 90), (255, 150, 90)); d = ImageDraw.Draw(im)
skyline(d, 700, (50, 36, 70), 12, night=True); d.rectangle(P([(0, 700), (1672, 941)]), fill=(70, 66, 76))
car(d, 780, 800, (36, 36, 46), 1.45)
for x in (180, 520): ln(d, [(x, 700), (x, 260)], (40, 36, 40), 14); ell(d, x, 250, 40, 24, (255, 230, 150))
person(d, 520, 941, 1.15, top=(190, 70, 120), skin=(130, 80, 50), face="worried")
ln(d, [(380, 820), (520, 790), (650, 820)], (190, 70, 120), 30)
finish(im, "08.png")
# 09 woman with ring light
im = grad((240, 230, 220), (214, 200, 186)); d = ImageDraw.Draw(im)
rr(d, 160, 120, 640, 560, 14, (190, 140, 100)); ell(d, 1330, 330, 150, 150, (255, 250, 235), (230, 220, 200), 20); ell(d, 1330, 330, 90, 90, (200, 196, 190))
rr(d, 1290, 300, 1370, 440, 10, (30, 30, 36)); ln(d, [(1330, 480), (1330, 900)], (60, 60, 66), 14)
d.rectangle(P([(0, 800), (1672, 941)]), fill=(176, 150, 124))
person(d, 760, 941, 1.45, top=(230, 190, 60), skin=(140, 86, 54), face="neutral")
finish(im, "09.png")
# 10 chaos room
im = grad((236, 226, 210), (214, 196, 170)); d = ImageDraw.Draw(im)
rr(d, 160, 100, 1512, 520, 16, (190, 220, 245), (90, 80, 70), 12); skyline(d, 520, (150, 160, 190), 14)
d.rectangle(P([(0, 780), (1672, 941)]), fill=(170, 140, 110))
person(d, 230, 941, 1.0, top=(60, 90, 140), face="worried"); person(d, 620, 941, 1.0, top=(150, 60, 60), skin=(120, 76, 48), face="worried"); person(d, 1450, 941, 1.0, top=(60, 120, 90), face="worried")
for x in (330, 720, 1350): phone(d, x - 40, 720, 70, 120, glow=False)
star(d, 1000, 941, 1.3, 1, shades=False, smirk=False)
finish(im, "10.png")
# 11 typing smirk
im = grad((236, 222, 200), (200, 176, 150)); d = ImageDraw.Draw(im)
rr(d, 1100, 80, 1600, 640, 14, (190, 220, 245), (90, 80, 70), 10); skyline(d, 640, (150, 160, 190), 15)
star(d, 640, 941, 1.65, 1, shades=False)
phone(d, 940, 640, 190, 300, glow=True)
finish(im, "11.png")
# 12 wall of phones
im = grad((40, 30, 70), (240, 130, 100)); d = ImageDraw.Draw(im)
k = 0
for yy in range(60, 900, 270):
    for xx in range(80, 1640, 280):
        phone(d, xx, yy, 190, 240, glow=False); cx, cy = xx + 95, yy + 120
        ell(d, cx, cy, 52, 52, (255, 210, 60), (200, 150, 30), 4); ell(d, cx - 18, cy - 12, 7, 9, (40, 30, 20)); ell(d, cx + 18, cy - 12, 7, 9, (40, 30, 20))
        d.arc([(cx - 30) * S, (cy - 6) * S, (cx + 30) * S, (cy + 34) * S], 10, 170, fill=(120, 40, 30), width=6 * S)
        if (k := k + 1) % 3 == 0: ell(d, xx + 160, yy + 40, 20, 20, (240, 70, 90))
finish(im, "12.png")
# 13 stage crowd back view
im = grad((16, 12, 40), (120, 40, 110)); d = ImageDraw.Draw(im)
for x in (300, 836, 1372): d.polygon(P([(x, 0), (x - 160, 760), (x + 160, 760)]), fill=(190, 150, 230))
d.rectangle(P([(0, 700), (1672, 941)]), fill=(14, 10, 24))
for k in range(150):
    x = int(rng.integers(0, 1672)); y = int(rng.integers(560, 930)); ell(d, x, y, 7, 7, (255, 240, 190)); ell(d, x, y + 24, 20, 14, (18, 14, 28))
star(d, 836, 700, 1.1, 1, back=True)
finish(im, "13.png")
# 14 finale confetti
im = grad((10, 10, 40), (200, 80, 90)); d = ImageDraw.Draw(im)
for k in range(260):
    x = int(rng.integers(0, 1672)); y = int(rng.integers(0, 941)); c = [(255, 210, 60), (255, 90, 120), (90, 200, 255), (130, 255, 150), (255, 255, 255)][k % 5]
    d.polygon(P([(x, y), (x + 14, y + 6), (x + 6, y + 20)]), fill=c)
for x, y in ((300, 360), (1380, 300), (840, 220)):
    for a in range(0, 360, 20): ln(d, [(x, y), (x + math.cos(math.radians(a)) * 150, y + math.sin(math.radians(a)) * 150)], (255, 210, 90), 8)
d.rectangle(P([(0, 760), (1672, 941)]), fill=(10, 8, 20))
for k in range(120):
    x = int(rng.integers(0, 1672)); y = int(rng.integers(780, 930)); ell(d, x, y, 7, 7, (255, 240, 190))
star(d, 836, 780, 1.1, 1, back=True, arms_up=True)
finish(im, "14.png")
print("drawn 14")
