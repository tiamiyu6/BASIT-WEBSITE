"""Hand-drawn look in code: cream paper, wobbly pencil lines, soft watercolour washes, simple blob characters.

Everything draws onto a PIL RGB canvas ("plate"), usually 2240x1260 so the edit can push in slowly.
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
PW, PH = 2240, 1260
LEAD = (78, 66, 58)                    # pencil
SKIN = (196, 158, 122)                 # the blob people
PAPER = (248, 241, 226)


def font(name, size):
    return ImageFont.truetype(os.path.join(HERE, "fonts", name), size)


HAND = lambda s: font("Caveat.ttf", s)


class Sketch:
    def __init__(self, seed=1, w=PW, h=PH):
        self.rng = np.random.default_rng(seed)
        self.w, self.h = w, h
        self.img = paper(w, h, seed)

    # ---------------------------------------------------------- strokes
    def wobble(self, pts, amp=2.2):
        pts = np.asarray(pts, np.float64)
        n = len(pts)
        if n < 2:
            return pts
        f = self.rng.random(2) * 6.28
        k = np.linspace(0, 1, n)
        dx = amp * (np.sin(k * 7 + f[0]) + 0.5 * np.sin(k * 17 + f[1]))
        dy = amp * (np.cos(k * 6 + f[1]) + 0.5 * np.sin(k * 13 + f[0]))
        return pts + np.stack([dx, dy], 1)

    def line(self, pts, width=4, color=LEAD, passes=2, closed=False, amp=1.8, alpha=230):
        pts = np.asarray(pts, np.float64)
        if closed:
            pts = np.vstack([pts, pts[:1]])
        lay = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        for p in range(passes):
            q = self.wobble(pts, amp * (1 + p * 0.6))
            a = int(alpha * (1.0 if p == 0 else 0.45))
            d.line([tuple(x) for x in q], fill=color + (a,), width=max(1, int(width * (1 if p == 0 else 0.6))), joint="curve")
        lay = lay.filter(ImageFilter.GaussianBlur(0.6))
        self.img.paste(lay, (0, 0), lay)

    def wash(self, poly, color, strength=0.85, hatch=True, edge=True):
        """watercolour fill: soft edges, uneven pigment, darker rim, light pencil hatching"""
        m = Image.new("L", (self.w, self.h), 0)
        ImageDraw.Draw(m).polygon([tuple(p) for p in np.asarray(poly)], fill=255)
        m = m.filter(ImageFilter.GaussianBlur(2.5))
        a = np.asarray(m, np.float32) / 255
        x0, y0, x1, y1 = bbox(poly, self.w, self.h)
        n = noise(self.w, self.h, int(self.rng.integers(1e6)), 28)
        a = a * (0.72 + 0.28 * n) * strength
        if edge:
            ring = a - np.asarray(m.filter(ImageFilter.GaussianBlur(8)), np.float32) / 255 * strength
            a = np.clip(a + np.clip(ring, 0, 1) * 0.5, 0, 1)
        base = np.asarray(self.img, np.float32)
        col = np.array(color, np.float32)
        out = base * (1 - a[..., None]) + (base * col / 255) * a[..., None]   # multiply, like pigment
        self.img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
        if hatch:
            self.hatch(poly, tuple(int(c * 0.55) for c in color))

    def hatch(self, poly, color, gap=14, ang=-60, alpha=70):
        m = Image.new("L", (self.w, self.h), 0)
        ImageDraw.Draw(m).polygon([tuple(p) for p in np.asarray(poly)], fill=255)
        lay = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        x0, y0, x1, y1 = bbox(poly, self.w, self.h)
        t = math.tan(math.radians(ang))
        L = (y1 - y0) + 40
        for x in range(int(x0 - L), int(x1 + L), gap):
            if self.rng.random() < 0.35:
                continue
            d.line([(x, y1 + 20), (x - L / t, y0 - 20)], fill=color + (int(alpha * self.rng.uniform(0.5, 1)),), width=2)
        lay.putalpha(ImageChops.multiply(lay.getchannel("A"), m))
        self.img.paste(lay, (0, 0), lay)

    def shape(self, poly, fill=None, width=4, closed=True, hatch=True):
        if fill:
            self.wash(poly, fill, hatch=hatch)
        self.line(poly, width=width, closed=closed)

    def text(self, xy, s, size=90, color=LEAD, angle=0, anchor="mm"):
        f = HAND(size)
        lay = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text(xy, s, font=f, fill=color + (235,), anchor=anchor)
        if angle:
            lay = lay.rotate(angle, center=xy, resample=Image.BICUBIC)
        self.img.paste(lay, (0, 0), lay)

    def ground(self, y, x0=None, x1=None):
        x0 = self.w * 0.18 if x0 is None else x0
        x1 = self.w * 0.82 if x1 is None else x1
        xs = np.linspace(x0, x1, 40)
        self.line(np.stack([xs, np.full_like(xs, y)], 1), width=3, passes=2, amp=1.2, alpha=170)
        for k in range(10):                       # a few loose grass/shade flicks
            x = self.rng.uniform(x0, x1)
            self.line([(x, y + 2), (x + 26, y + 2)], width=2, passes=1, alpha=110)

    # ---------------------------------------------------------- people
    def person(self, x, y, h=420, mood="neutral", look=0, arms=("down", "down"), color=SKIN, lean=0.0, item=None, legs="stand", flip=1):
        """a blob person standing with feet at (x, y). arms: down | up | out | hold | wave | face"""
        s = h / 420
        cx = x + lean * 40 * s
        # body: a bean, head and torso in one
        ts = np.linspace(0, 2 * math.pi, 60, endpoint=False)
        w_top, w_bot = 78 * s, 104 * s
        top, bot = y - h, y - 70 * s
        pts = []
        for t in ts:
            u = (1 - math.cos(t)) / 2                       # 0 at top, 1 at bottom
            r = w_top + (w_bot - w_top) * u ** 1.3
            px = cx + math.sin(t) * r * (1 - 0.08 * math.sin(3 * t) ** 2)
            py = top + (bot - top) * u + (14 * s if u > 0.98 else 0)
            pts.append((px - lean * 60 * s * (1 - u), py))
        pts = np.array(pts)
        # legs
        for side in (-1, 1):
            lx = cx + side * 42 * s
            if legs == "walk":
                k = 1 if side * flip > 0 else -1
                leg = capsule((lx, y - 80 * s), (lx + k * 34 * s, y - 6 * s), 30 * s)
            elif legs == "sit":
                leg = capsule((lx, y - 70 * s), (lx + side * 20 * s + 70 * s * flip, y - 40 * s), 30 * s)
            else:
                leg = capsule((lx, y - 80 * s), (lx + side * 6 * s, y - 8 * s), 31 * s)
            self.shape(leg, color, width=4)
        self.shape(pts, color, width=4)
        # arms (shoulder at 45% height)
        sy = top + (bot - top) * 0.48
        for side, mode in zip((-1, 1), arms):
            sx = cx + side * (w_top + 12 * s)
            ang = {"down": 100, "out": 25, "up": -60, "wave": -75, "hold": 55, "face": -110, "chin": -120}[mode]
            ln = 150 * s if mode not in ("face", "chin") else 120 * s
            a = math.radians(ang)
            ex, ey = sx + side * math.cos(a) * ln, sy + math.sin(a) * ln
            if mode in ("face", "chin"):
                ex, ey = cx + side * 26 * s, top + (bot - top) * (0.30 if mode == "face" else 0.38)
            self.shape(capsule((sx, sy), (ex, ey), 25 * s), color, width=4)
        # face
        hy = top + 120 * s
        fx = cx + look * 22 * s - lean * 40 * s
        for side in (-1, 1):
            ex = fx + side * 26 * s
            d = ImageDraw.Draw(self.img)
            d.ellipse([ex - 7 * s, hy - 9 * s, ex + 7 * s, hy + 9 * s], fill=(52, 42, 36))
            if mood in ("sad", "worried"):
                self.line([(ex - side * 18 * s, hy - 34 * s), (ex + side * 10 * s, hy - 24 * s)], width=3, passes=1)
            if mood == "angry":
                self.line([(ex - side * 16 * s, hy - 24 * s), (ex + side * 12 * s, hy - 34 * s)], width=3, passes=1)
        my = hy + 40 * s
        if mood == "happy":
            arc = [(fx + 22 * s * math.cos(t), my - 8 * s + 14 * s * math.sin(t)) for t in np.linspace(0.3, 2.8, 12)]
        elif mood in ("sad", "worried"):
            arc = [(fx + 18 * s * math.cos(t), my + 12 * s - 12 * s * math.sin(t)) for t in np.linspace(0.3, 2.8, 12)]
        elif mood == "shock":
            arc = [(fx + 9 * s * math.cos(t), my + 11 * s * math.sin(t)) for t in np.linspace(0, 6.28, 16)]
        else:
            arc = [(fx - 14 * s, my), (fx + 14 * s, my + 2 * s)]
        self.line(arc, width=3, passes=1, closed=(mood == "shock"))
        return dict(cx=cx, top=top, hand_l=None, s=s, sy=sy, w=w_top)

    # ---------------------------------------------------------- props
    def phone(self, x, y, s=1.0, glow=(170, 205, 235), angle=0):
        w, h = 70 * s, 130 * s
        body = rot_rect(x, y, w, h, angle, r=14 * s)
        self.shape(body, (90, 90, 100), width=4, hatch=False)
        self.wash(rot_rect(x, y, w * 0.8, h * 0.8, angle, r=8 * s), glow, hatch=False)

    def suitcase(self, x, y, s=1.0, color=(170, 80, 60), tag=None):
        w, h = 190 * s, 140 * s
        self.shape(rect(x - w / 2, y - h, w, h, 16 * s), color, width=4)
        self.line([(x - 35 * s, y - h), (x - 35 * s, y - h - 30 * s), (x + 35 * s, y - h - 30 * s), (x + 35 * s, y - h)], width=5)
        for k in (-1, 1):
            self.line([(x + k * 45 * s, y - h + 6 * s), (x + k * 45 * s, y - 6 * s)], width=3, passes=1)
        if tag:
            self.text((x, y - h / 2), tag, size=int(44 * s), color=(250, 245, 235))

    def passport(self, x, y, s=1.0, angle=-8):
        self.shape(rot_rect(x, y, 120 * s, 165 * s, angle, r=8 * s), (60, 120, 80), width=4)
        self.text((x, y + 6 * s), "PASSPORT", size=int(30 * s), color=(232, 208, 140), angle=angle)

    def plane(self, x, y, s=1.0, color=(150, 175, 200)):
        body = [(x - 170 * s, y), (x + 150 * s, y - 14 * s), (x + 190 * s, y), (x + 150 * s, y + 14 * s)]
        self.shape(body, color, width=4, hatch=False)
        self.shape([(x - 10 * s, y - 6 * s), (x - 70 * s, y - 90 * s), (x - 40 * s, y - 90 * s), (x + 40 * s, y - 6 * s)], color, width=4, hatch=False)
        self.shape([(x - 10 * s, y + 8 * s), (x - 70 * s, y + 80 * s), (x - 40 * s, y + 80 * s), (x + 40 * s, y + 8 * s)], color, width=4, hatch=False)
        self.shape([(x - 150 * s, y - 2 * s), (x - 180 * s, y - 50 * s), (x - 160 * s, y - 50 * s), (x - 120 * s, y - 4 * s)], color, width=4, hatch=False)
        for k in range(5):
            xx = x + (20 + 24 * k) * s
            ImageDraw.Draw(self.img).ellipse([xx - 4 * s, y - 6 * s, xx + 4 * s, y + 2 * s], fill=LEAD)

    def bubble(self, x, y, w, h, tail=(0, 1), think=False):
        ts = np.linspace(0, 2 * math.pi, 50)
        pts = [(x + w / 2 * math.cos(t) * (1 + 0.04 * math.sin(5 * t)), y + h / 2 * math.sin(t)) for t in ts]
        self.line(pts, width=4, closed=True)
        if think:
            for k, r in enumerate((14, 10, 7)):
                cx, cy = x + tail[0] * (w / 2 + 20 + 26 * k), y + tail[1] * (h / 2 + 20 + 26 * k)
                self.line([(cx + r * math.cos(t), cy + r * math.sin(t)) for t in np.linspace(0, 6.3, 14)], width=3, passes=1)
        else:
            bx, by = x + tail[0] * w * 0.2, y + h / 2 - 4
            self.line([(bx - 20, by), (bx + tail[0] * 50, by + 60), (bx + 20, by)], width=4)

    def scribble(self, x, y, r=160, loops=9):
        pts = []
        for k in range(loops * 40):
            t = k / 40 * 2 * math.pi
            rr = r * (0.4 + 0.6 * abs(math.sin(k * 0.037)))
            pts.append((x + rr * math.cos(t * 1.07) + 40 * math.sin(t * 0.3), y + rr * 0.6 * math.sin(t)))
        self.line(pts, width=3, passes=1, amp=4)

    def clock(self, x, y, r=110):
        ts = np.linspace(0, 6.3, 50)
        self.shape([(x + r * math.cos(t), y + r * math.sin(t)) for t in ts], (235, 225, 200), width=5, hatch=False)
        for k in range(12):
            a = k * math.pi / 6
            self.line([(x + r * 0.82 * math.cos(a), y + r * 0.82 * math.sin(a)), (x + r * 0.92 * math.cos(a), y + r * 0.92 * math.sin(a))], width=3, passes=1)
        self.line([(x, y), (x, y - r * 0.6)], width=5, passes=1)
        self.line([(x, y), (x + r * 0.45, y + r * 0.15)], width=5, passes=1)

    def calendar(self, x, y, s=1.0, crossed=11):
        w, h = 300 * s, 260 * s
        self.shape(rect(x - w / 2, y - h / 2, w, h, 10 * s), (240, 236, 226), width=4, hatch=False)
        self.wash(rect(x - w / 2, y - h / 2, w, 50 * s, 10 * s), (200, 90, 70), hatch=False)
        for i in range(4):
            for j in range(5):
                cx, cy = x - w / 2 + 34 * s + j * 58 * s, y - h / 2 + 86 * s + i * 50 * s
                if i * 5 + j < crossed:
                    self.line([(cx - 14 * s, cy - 14 * s), (cx + 14 * s, cy + 14 * s)], width=3, passes=1, color=(170, 60, 50))
                    self.line([(cx + 14 * s, cy - 14 * s), (cx - 14 * s, cy + 14 * s)], width=3, passes=1, color=(170, 60, 50))
                else:
                    ImageDraw.Draw(self.img).ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=LEAD)

    def cap(self, x, y, s=1.0):
        self.shape([(x - 90 * s, y), (x, y - 40 * s), (x + 90 * s, y), (x, y + 40 * s)], (60, 60, 70), width=4, hatch=False)
        self.line([(x + 60 * s, y + 6 * s), (x + 70 * s, y + 70 * s)], width=4, passes=1)

    def note(self, x, y, s=1.0, angle=0):
        self.shape(rot_rect(x, y, 200 * s, 96 * s, angle, r=6 * s), (150, 170, 120), width=4)
        self.text((x, y), "₦", size=int(70 * s), color=(70, 90, 60), angle=angle)

    def door(self, x, y, s=1.0, open_=True):
        w, h = 200 * s, 380 * s
        self.shape(rect(x - w / 2, y - h, w, h, 4), (230, 215, 190), width=5, hatch=False)
        if open_:
            self.wash(rect(x - w / 2 + 14, y - h + 14, w - 28, h - 14, 2), (255, 236, 170), hatch=False)
            self.shape([(x + w / 2, y - h), (x + w / 2 + 80 * s, y - h + 40 * s), (x + w / 2 + 80 * s, y - 20 * s), (x + w / 2, y)], (170, 120, 80), width=4)


# ------------------------------------------------------------------ helpers
def paper(w, h, seed):
    r = np.random.default_rng(seed)
    base = np.ones((h, w, 3), np.float32) * np.array(PAPER, np.float32)
    n = noise(w, h, seed, 6) - 0.5
    fib = noise(w, h, seed + 1, 2) - 0.5
    base += (n * 10 + fib * 6)[..., None]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    v = 1 - 0.10 * (((xx - w / 2) / (w * 0.6)) ** 2 + ((yy - h / 2) / (h * 0.7)) ** 2)
    base *= v[..., None]
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))


_noise_cache = {}


def noise(w, h, seed, scale):
    k = (w, h, seed % 50, scale)
    if k not in _noise_cache:
        r = np.random.default_rng(seed % 50)
        small = (r.random((max(2, h // scale), max(2, w // scale))) * 255).astype(np.uint8)
        _noise_cache[k] = np.asarray(Image.fromarray(small).resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(scale / 3)), np.float32) / 255
    return _noise_cache[k]


def bbox(poly, w, h):
    p = np.asarray(poly)
    return max(0, p[:, 0].min()), max(0, p[:, 1].min()), min(w, p[:, 0].max()), min(h, p[:, 1].max())


def capsule(p0, p1, r, n=14):
    (x0, y0), (x1, y1) = p0, p1
    a = math.atan2(y1 - y0, x1 - x0)
    pts = [(x1 + r * math.cos(a + t), y1 + r * math.sin(a + t)) for t in np.linspace(-math.pi / 2, math.pi / 2, n)]
    pts += [(x0 + r * math.cos(a + t), y0 + r * math.sin(a + t)) for t in np.linspace(math.pi / 2, 3 * math.pi / 2, n)]
    return pts


def rect(x, y, w, h, r=0):
    if r <= 0:
        return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    pts = []
    for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)):
        pts += [(cx + r * math.cos(math.radians(a0 + t)), cy + r * math.sin(math.radians(a0 + t))) for t in range(0, 91, 15)]
    return pts


def rot_rect(cx, cy, w, h, angle, r=0):
    pts = rect(cx - w / 2, cy - h / 2, w, h, r)
    a = math.radians(angle)
    return [(cx + (px - cx) * math.cos(a) - (py - cy) * math.sin(a), cy + (px - cx) * math.sin(a) + (py - cy) * math.cos(a)) for px, py in pts]
