"""Illustrated 1920x1080 plates for every scene (drawn with Pillow, no stock photos).

If documentary/photos/<scene id>.jpg exists it is used instead (cover-cropped + colour graded).
"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops, ImageOps

W, H = 1920, 1080
INTER = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
SERIF = "/usr/share/fonts/truetype/crosextra/Caladea-{}.ttf"
GOLD, CREAM, GREEN, RED, DIM = (226, 178, 84), (243, 235, 221), (31, 164, 99), (215, 68, 62), (150, 145, 135)
HERE = os.path.dirname(os.path.abspath(__file__))


def F(size, w="Bold"):
    return ImageFont.truetype(INTER.format(w), size)


def SF(size, w="Bold"):
    return ImageFont.truetype(SERIF.format(w), size)


# ------------------------------------------------------------------ helpers
def bg(top, bottom, glow=None, glow_xy=(0.5, 0.45), glow_r=0.6, seed=0):
    y = np.linspace(0, 1, H)[:, None, None]
    a = np.array(top, np.float32) * (1 - y) + np.array(bottom, np.float32) * y
    a = np.repeat(a, W, axis=1)
    if glow:
        yy, xx = np.mgrid[0:H, 0:W]
        d = np.sqrt(((xx / W - glow_xy[0]) * 1.6) ** 2 + (yy / H - glow_xy[1]) ** 2) / glow_r
        a += np.array(glow, np.float32)[None, None] * np.clip(1 - d, 0, 1)[..., None] ** 2
    rng = np.random.default_rng(seed)
    a += rng.normal(0, 2.2, (H, W, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def glow_layer(img, draw_fn, blur=18, strength=1.6):
    """draw_fn(draw) on a transparent layer; adds blurred glow + sharp layer."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    g = layer.filter(ImageFilter.GaussianBlur(blur))
    base = img.convert("RGBA")
    for _ in range(int(strength)):
        base = Image.alpha_composite(base, g)
    return Image.alpha_composite(base, layer).convert("RGB")


def text(d, xy, s, font, fill=CREAM, anchor="la", shadow=True, spacing=0):
    if spacing:
        x, y = xy
        total = sum(d.textlength(c, font=font) + spacing for c in s) - spacing
        if anchor[0] == "m":
            x -= total / 2
        elif anchor[0] == "r":
            x -= total
        for c in s:
            if shadow:
                d.text((x + 3, y + 4), c, font=font, fill=(0, 0, 0, 160), anchor="l" + anchor[1])
            d.text((x, y), c, font=font, fill=fill, anchor="l" + anchor[1])
            x += d.textlength(c, font=font) + spacing
        return
    if shadow:
        d.text((xy[0] + 3, xy[1] + 4), s, font=font, fill=(0, 0, 0, 170), anchor=anchor)
    d.text(xy, s, font=font, fill=fill, anchor=anchor)


def ghost(img, xy, s, font, alpha=36):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).text(xy, s, font=font, fill=(255, 255, 255, alpha), anchor="mm")
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


def particles(img, n=160, seed=1, color=GOLD, maxr=4):
    rng = random.Random(seed)

    def fn(d):
        for _ in range(n):
            x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0.8, maxr)
            a = rng.randint(40, 200)
            d.ellipse([x - r, y - r, x + r, y + r], fill=color + (a,))
    return glow_layer(img, fn, blur=6, strength=1)


def skyline(d, base_y, seed, color, n=40, hmin=80, hmax=420, x0=0, x1=W, windows=None, rng_w=(40, 110)):
    rng = random.Random(seed)
    x = x0
    rects = []
    while x < x1:
        w = rng.randint(*rng_w)
        h = rng.randint(hmin, hmax) * (1.6 if rng.random() < 0.12 else 1)
        d.rectangle([x, base_y - h, x + w, base_y], fill=color)
        if rng.random() < 0.25:
            d.rectangle([x + w * 0.4, base_y - h - 40, x + w * 0.45, base_y - h], fill=color)
        rects.append((x, base_y - h, w, h))
        x += w + rng.randint(-10, 6)
    if windows:
        for (bx, by, bw, bh) in rects:
            for wy in range(int(by + 14), int(base_y - 10), 22):
                for wx in range(int(bx + 8), int(bx + bw - 8), 16):
                    if rng.random() < 0.28:
                        c = windows if rng.random() < 0.8 else (255, 240, 200)
                        d.rectangle([wx, wy, wx + 6, wy + 9], fill=c + (rng.randint(120, 255),))
    return rects


def reflect(img, y0):
    top = img.crop((0, y0 - (H - y0), W, y0))
    r = ImageOps.flip(top).filter(ImageFilter.GaussianBlur(3))
    r = Image.blend(r, Image.new("RGB", r.size, (8, 14, 22)), 0.55)
    img.paste(r, (0, y0))
    d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(4)
    for _ in range(140):
        y = rng.randint(y0 + 4, H)
        x = rng.randint(0, W)
        d.line([x, y, x + rng.randint(30, 160), y], fill=(255, 220, 160, rng.randint(15, 60)), width=2)
    return img


def crowd(d, base_y, seed, color, n=70, scale=1.0, signs=(), flags=0, sign_fill=(235, 228, 210)):
    rng = random.Random(seed)
    heads = []
    for i in range(n):
        x = rng.uniform(-40, W + 40)
        s = rng.uniform(0.75, 1.25) * scale
        hy = base_y - 230 * s + rng.uniform(-30, 30)
        r = 26 * s
        d.ellipse([x - r, hy - r, x + r, hy + r], fill=color)
        d.rounded_rectangle([x - 62 * s, hy + r * 0.8, x + 62 * s, base_y + 50], radius=int(40 * s), fill=color)
        heads.append((x, hy, s))
        if rng.random() < 0.22:  # raised fist / arm
            side = rng.choice([-1, 1])
            ax = x + side * 48 * s
            d.line([ax, hy + 60 * s, ax + side * 18 * s, hy - 120 * s], fill=color, width=int(20 * s))
            d.ellipse([ax + side * 18 * s - 16 * s, hy - 150 * s, ax + side * 18 * s + 16 * s, hy - 116 * s], fill=color)
    for i in range(flags):
        x = rng.uniform(100, W - 100)
        top = base_y - rng.uniform(560, 680)
        d.line([x, top, x, top + 330], fill=color, width=8)
        fw, fh = 170, 110
        for k, c in enumerate([(0, 135, 81), (240, 240, 240), (0, 135, 81)]):
            pts = []
            for j in range(11):
                px = x + k * fw / 3 + j * (fw / 3) / 10
                py = top + 10 * math.sin((px - x) / 40 + i)
                pts.append((px, py))
            pts += [(p[0], p[1] + fh) for p in reversed(pts)]
            d.polygon(pts, fill=c)

    rng.shuffle(heads)
    font = F(34, "Black")
    for i, s_txt in enumerate(signs):
        x, hy, s = heads[i * 3 % len(heads)]
        x = (i + 0.5) * W / len(signs) + rng.uniform(-60, 60)
        tw = d.textlength(s_txt, font=font) + 50
        top = hy - 250 * s - rng.uniform(0, 60)
        d.line([x, top + 90, x, hy + 40], fill=color, width=10)
        d.rectangle([x - tw / 2, top, x + tw / 2, top + 92], fill=sign_fill)
        d.text((x, top + 46), s_txt, font=font, fill=(25, 25, 25), anchor="mm")

def card(d, box, title, lines, accent=GOLD, title_size=40, line_size=34):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=18, fill=(16, 18, 22, 225), outline=accent + (200,), width=3)
    d.rectangle([x0, y0 + 18, x0 + 8, y1 - 18], fill=accent)
    text(d, (x0 + 44, y0 + 40), title, F(title_size, "Black"), accent, shadow=False)
    y = y0 + 40 + title_size + 30
    for ln in lines:
        col = CREAM
        if isinstance(ln, tuple):
            ln, col = ln
        text(d, (x0 + 44, y), ln, F(line_size, "Medium"), col, shadow=False)
        y += line_size + 20


def nigeria_shape():
    import shapefile
    import geopandas
    p = geopandas.datasets.get_path("naturalearth_lowres")
    sf = shapefile.Reader(p)
    shapes = {}
    for rec, shp in zip(sf.records(), sf.shapes()):
        name = rec["name"]
        if name in ("Nigeria", "Benin", "Niger", "Chad", "Cameroon", "Togo", "Ghana", "Burkina Faso", "Mali",
                    "Central African Rep.", "Eq. Guinea", "Gabon"):
            parts = list(shp.parts) + [len(shp.points)]
            shapes[name] = [shp.points[parts[i]:parts[i + 1]] for i in range(len(parts) - 1)]
    return shapes


def map_plate(highlight_glow=True, pins=(("LAGOS", 3.38, 6.52, True), ("ABUJA", 7.49, 9.06, False)),
              extent=(-1.5, 17.5, 2.5, 15.5), cx=1040, scale=None):
    img = bg((6, 14, 18), (3, 6, 9), glow=(20, 60, 50), glow_xy=(0.55, 0.5))
    shapes = nigeria_shape()
    lon0, lon1, lat0, lat1 = extent
    sc = scale or min(W / (lon1 - lon0), H / (lat1 - lat0)) * 0.95
    mx, my = (lon0 + lon1) / 2, (lat0 + lat1) / 2

    def P(lon, lat):
        return (cx + (lon - mx) * sc, H / 2 - (lat - my) * sc)

    d = ImageDraw.Draw(img, "RGBA")
    for name, polys in shapes.items():
        if name == "Nigeria":
            continue
        for poly in polys:
            d.polygon([P(*p) for p in poly], fill=(28, 36, 40, 255), outline=(60, 72, 78, 255))

    def fn(dd):
        for poly in shapes["Nigeria"]:
            dd.polygon([P(*p) for p in poly], fill=(18, 92, 60, 235), outline=GOLD + (255,), width=5)
    img = glow_layer(img, fn, blur=22, strength=2 if highlight_glow else 1)
    d = ImageDraw.Draw(img, "RGBA")
    for name, lon, lat, big in pins:
        x, y = P(lon, lat)
        for r, a in ((60, 40), (38, 80), (16, 255)):
            d.ellipse([x - r, y - r, x + r, y + r], fill=(RED if big else CREAM) + (a,))
        text(d, (x + 34, y - 6), name, F(46 if big else 34, "Black"), CREAM, "lm")
    return img, P


# ------------------------------------------------------------------ plates
def p_open():
    img, _ = map_plate(pins=())
    img = Image.blend(img, Image.new("RGB", img.size, (0, 0, 0)), 0.35)
    return particles(img, 220, 3)


def p_title():
    img = bg((10, 10, 12), (0, 0, 0), glow=(70, 52, 20), glow_r=0.55)
    img = particles(img, 260, 7, maxr=3)

    def fn(d):
        f = SF(260)
        text(d, (W / 2, 470), "JAGABAN", f, GOLD, "mm", shadow=False, spacing=24)
    img = glow_layer(img, fn, blur=30, strength=2)
    d = ImageDraw.Draw(img, "RGBA")
    d.line([W / 2 - 520, 640, W / 2 + 520, 640], fill=GOLD + (200,), width=2)
    text(d, (W / 2, 700), "THE STORY OF BOLA AHMED TINUBU", F(52, "SemiBold"), CREAM, "mm", spacing=10)
    text(d, (W / 2, 790), "A DOCUMENTARY", F(28, "Medium"), DIM, "mm", spacing=14)
    return img


def p_chapter():
    img = bg((8, 9, 11), (0, 0, 0), glow=(40, 32, 14), glow_r=0.5, seed=5)
    return particles(img, 90, 11, maxr=2.5)


def p_map_lagos():
    img, P = map_plate()
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (110, 170), "LAGOS", SF(120), GOLD)
    text(d, (114, 300), "Born 29 March 1952 (official record)", F(38, "Medium"), CREAM)
    text(d, (114, 356), "Yoruba Muslim family", F(38, "Medium"), DIM)
    return img


def p_chicago():
    img = bg((10, 16, 40), (40, 26, 50), glow=(60, 40, 90), glow_xy=(0.7, 0.2))
    d = ImageDraw.Draw(img, "RGBA")
    img = ghost(img, (W / 2 + 300, 560), "1975 — 1983", SF(220))
    d = ImageDraw.Draw(img, "RGBA")
    skyline(d, 780, 21, (20, 22, 40), hmin=120, hmax=360, rng_w=(50, 120))
    skyline(d, 820, 22, (6, 8, 18), hmin=160, hmax=520, windows=(255, 205, 120), rng_w=(60, 140))
    img = reflect(img, 820)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (110, 150), "CHICAGO", SF(110), GOLD)
    text(d, (114, 270), "B.Sc. Accounting · Chicago State University · 1979", F(36, "Medium"), CREAM)
    text(d, (114, 322), "Arthur Andersen · Deloitte · Mobil Oil Nigeria", F(34, "Medium"), DIM)
    return img


def p_questions():
    img = bg((14, 12, 12), (4, 3, 3), glow=(60, 14, 12), glow_r=0.7, seed=2)
    rng = random.Random(9)
    labels = ["DATE OF BIRTH", "PRIMARY SCHOOL", "SECONDARY SCHOOL", "UNIVERSITY RECORDS", "CERTIFICATES", "HOMETOWN"]
    for i, lab in enumerate(labels):
        paper = Image.new("RGBA", (560, 330), (226, 216, 190, 255))
        pd = ImageDraw.Draw(paper)
        for y in range(110, 310, 34):
            pd.line([40, y, 520, y], fill=(150, 140, 120), width=3)
        pd.text((40, 40), lab, font=F(40, "Black"), fill=(40, 34, 28))
        pd.text((470, 200), "?", font=SF(200), fill=RED + (230,), anchor="mm")
        paper = paper.rotate(rng.uniform(-14, 14), expand=True, resample=Image.BICUBIC)
        x = 120 + (i % 3) * 590 + rng.randint(-30, 30)
        y = 140 + (i // 3) * 430 + rng.randint(-20, 40)
        sh = Image.new("RGBA", paper.size, (0, 0, 0, 0))
        sh.putalpha(paper.getchannel("A").point(lambda a: a * 0.6))
        img.paste((0, 0, 0), (x + 16, y + 20), sh.getchannel("A").filter(ImageFilter.GaussianBlur(10)))
        img.paste(paper, (x, y), paper)

    def fn(d):
        d.text((W / 2, H / 2), "?", font=SF(700), fill=RED + (120,), anchor="mm")
    return glow_layer(img, fn, blur=40, strength=1)


def p_senate():
    img = bg((30, 24, 18), (6, 5, 4), glow=(90, 64, 26), glow_xy=(0.5, 0.35))
    d = ImageDraw.Draw(img, "RGBA")
    img = ghost(img, (W / 2, 250), "1992", SF(300), 70)
    d = ImageDraw.Draw(img, "RGBA")
    c = (8, 7, 6)
    d.polygon([(460, 520), (W / 2, 380), (1460, 520)], fill=c)
    d.rectangle([440, 520, 1480, 560], fill=c)
    for i in range(8):
        x = 500 + i * 130
        d.rectangle([x, 570, x + 50, 900], fill=c)
    d.rectangle([420, 900, 1500, 960], fill=c)
    d.rectangle([380, 960, 1540, H], fill=c)
    text(d, (W / 2, 990), "SENATE  ·  LAGOS WEST  ·  SDP", F(44, "Bold"), GOLD, "mm", spacing=6)
    return img


def p_june12():
    img = bg((26, 26, 30), (6, 6, 8), glow=(40, 40, 50), seed=3)
    d = ImageDraw.Draw(img, "RGBA")
    # ballot box
    d.polygon([(660, 520), (1260, 520), (1200, 940), (720, 940)], fill=(200, 196, 186), outline=(90, 90, 90), width=4)
    d.rectangle([640, 470, 1280, 530], fill=(220, 216, 206), outline=(90, 90, 90), width=4)
    d.rectangle([860, 488, 1060, 506], fill=(40, 40, 40))
    paper = Image.new("RGBA", (180, 240), (250, 250, 245, 255))
    pd = ImageDraw.Draw(paper)
    pd.rectangle([20, 30, 160, 60], outline=(60, 60, 60), width=3)
    pd.rectangle([20, 90, 160, 120], outline=(60, 60, 60), width=3)
    pd.text((90, 105), "✓", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34),
            fill=(30, 30, 30), anchor="mm")
    paper = paper.rotate(-12, expand=True, resample=Image.BICUBIC)
    img.paste(paper, (880, 230), paper)
    text(d, (960, 740), "BALLOT", F(60, "Black"), (60, 60, 60), "mm", shadow=False)
    stamp = Image.new("RGBA", (1100, 260), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rounded_rectangle([10, 10, 1090, 250], radius=24, outline=RED + (235,), width=16)
    sd.text((550, 130), "ANNULLED", font=F(170, "Black"), fill=RED + (235,), anchor="mm")
    stamp = stamp.rotate(14, expand=True, resample=Image.BICUBIC)
    img.paste(stamp, (W // 2 - stamp.width // 2, 470 - stamp.height // 2 + 120), stamp)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (110, 120), "12 · 06 · 1993", SF(90), GOLD)
    return img


def p_exile():
    img = bg((40, 24, 40), (230, 120, 60), seed=4)
    a = np.array(img).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    sun = np.clip(1 - np.sqrt((xx - 1300) ** 2 + (yy - 700) ** 2) / 300, 0, 1)[..., None]
    a += sun * np.array([80, 60, 20])
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 760, W, H], fill=(20, 16, 30))
    img = reflect(img, 760)
    d = ImageDraw.Draw(img, "RGBA")
    # plane
    px, py = 620, 330
    c = (14, 10, 18)
    d.polygon([(px - 260, py + 20), (px + 260, py - 10), (px + 290, py), (px + 260, py + 18), (px - 250, py + 40)], fill=c)
    d.polygon([(px - 20, py + 10), (px + 80, py + 10), (px - 140, py + 160), (px - 190, py + 160)], fill=c)
    d.polygon([(px - 40, py + 10), (px + 40, py + 5), (px - 60, py - 110), (px - 100, py - 110)], fill=c)
    d.polygon([(px - 230, py + 20), (px - 190, py + 20), (px - 260, py - 70), (px - 280, py - 70)], fill=c)
    text(d, (110, 860), "EXILE  1994 — 1998", SF(96), CREAM)
    text(d, (114, 980), "National Democratic Coalition (NADECO)", F(36, "Medium"), (255, 225, 190))
    return img


def p_lagos():
    img = bg((255, 170, 90), (60, 40, 70), seed=6)
    img = Image.fromarray(np.array(img)[::-1].copy())
    d = ImageDraw.Draw(img, "RGBA")
    a = np.array(img).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    sun = np.clip(1 - np.sqrt((xx - 1450) ** 2 + (yy - 560) ** 2) / 160, 0, 1)[..., None] ** 0.5
    a += sun * np.array([60, 50, 30])
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img, "RGBA")
    skyline(d, 640, 31, (70, 40, 60), hmin=60, hmax=240, x0=900, x1=W, rng_w=(40, 90))
    skyline(d, 660, 32, (30, 16, 30), hmin=80, hmax=330, x0=1000, x1=W, windows=(255, 210, 140), rng_w=(50, 110))
    d.rectangle([0, 660, W, H], fill=(40, 26, 44))
    img = reflect(img, 660)
    d = ImageDraw.Draw(img, "RGBA")
    # Third Mainland-style bridge sweeping across the lagoon
    pts = [(x, 760 - 90 * math.sin(x / W * math.pi * 0.9)) for x in range(-50, W + 50, 10)]
    d.line(pts, fill=(25, 14, 26), width=26)
    for x, y in pts[::9]:
        d.line([x, y, x, H], fill=(25, 14, 26), width=10)
    text(d, (110, 150), "LAGOS  1999", SF(120), (40, 20, 30), shadow=False)
    text(d, (114, 290), "Elected Governor · re-elected 2003", F(40, "SemiBold"), (50, 26, 36), shadow=False)
    return img


def p_revenue():
    img = bg((10, 22, 18), (3, 8, 6), glow=(20, 70, 40), seed=8)
    d = ImageDraw.Draw(img, "RGBA")
    # coin stacks rising
    for i, n in enumerate([3, 5, 8, 12, 17]):
        x = 220 + i * 150
        for k in range(n):
            y = 900 - k * 34
            d.ellipse([x - 60, y - 16, x + 60, y + 16], fill=(170, 128, 40), outline=(90, 64, 20), width=3)
            d.ellipse([x - 60, y - 30, x + 60, y + 2], fill=GOLD, outline=(120, 90, 30), width=3)
    d.line([160, 980, 1000, 980], fill=DIM, width=3)
    text(d, (580, 1020), "INTERNALLY GENERATED REVENUE  ↑", F(30, "Bold"), DIM, "mm", spacing=3)
    # bus
    bx, by = 1180, 640
    d.rounded_rectangle([bx, by, bx + 620, by + 230], radius=36, fill=(30, 110, 170))
    d.rectangle([bx, by + 150, bx + 620, by + 175], fill=(250, 200, 40))
    for i in range(5):
        d.rounded_rectangle([bx + 30 + i * 115, by + 30, bx + 125 + i * 115, by + 120], radius=10, fill=(170, 210, 230))
    for wx in (bx + 120, bx + 500):
        d.ellipse([wx - 48, by + 190, wx + 48, by + 286], fill=(15, 15, 15))
        d.ellipse([wx - 20, by + 218, wx + 20, by + 258], fill=(120, 120, 120))
    text(d, (bx + 310, by - 60), "LAMATA  ·  2002", F(44, "Black"), CREAM, "mm")
    text(d, (110, 120), "REFORM", SF(120), GOLD)
    text(d, (114, 250), "Tax collection overhaul · transport authority", F(38, "Medium"), CREAM)
    return img


def p_lcda():
    img = bg((12, 12, 16), (4, 4, 6), seed=9)
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 0, W / 2 - 4, H], fill=(14, 60, 42, 200))
    d.rectangle([W / 2 + 4, 0, W, H], fill=(40, 40, 50, 200))
    text(d, (W / 4, 380), "LAGOS STATE", F(78, "Black"), CREAM, "mm")
    text(d, (W / 4, 470), "Created 37 new council areas", F(36, "Medium"), (210, 235, 220), "mm")
    text(d, (3 * W / 4, 380), "FEDERAL GOV'T", F(78, "Black"), CREAM, "mm")
    text(d, (3 * W / 4, 470), "Withheld local government funds", F(36, "Medium"), (220, 220, 230), "mm")

    def fn(dd):
        dd.ellipse([W / 2 - 110, 320, W / 2 + 110, 540], fill=(10, 10, 10, 255), outline=GOLD + (255,), width=6)
        dd.text((W / 2, 430), "VS", font=F(90, "Black"), fill=GOLD + (255,), anchor="mm")
    img = glow_layer(img, fn, 20, 2)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([360, 700, W - 360, 900], radius=20, fill=(0, 0, 0, 200), outline=GOLD + (220,), width=3)
    text(d, (W / 2, 760), "SUPREME COURT  ·  2004", F(46, "Black"), GOLD, "mm", spacing=4)
    text(d, (W / 2, 840), "Federal government had no power to withhold the funds", F(38, "Medium"), CREAM, "mm")
    return img


def p_network():
    img = bg((10, 10, 14), (2, 2, 4), glow=(50, 40, 16), seed=10)
    img = particles(img, 80, 12, maxr=2)
    cx, cy = W / 2, 560
    nodes = [("Babatunde Fashola", "Governor of Lagos 2007–2015", -560, -250),
             ("Akinwunmi Ambode", "Governor of Lagos 2015–2019", 560, -250),
             ("Babajide Sanwo-Olu", "Governor of Lagos 2019–", -560, 250),
             ("Yemi Osinbajo", "Vice President 2015–2023", 560, 250)]

    def fn(d):
        for _, _, dx, dy in nodes:
            d.line([cx, cy, cx + dx, cy + dy], fill=GOLD + (200,), width=5)
        d.ellipse([cx - 150, cy - 150, cx + 150, cy + 150], fill=(30, 22, 8, 255), outline=GOLD + (255,), width=8)
        d.text((cx, cy - 20), "TINUBU", font=F(58, "Black"), fill=GOLD + (255,), anchor="mm")
        d.text((cx, cy + 40), "“Jagaban of Borgu”", font=F(26, "Medium"), fill=CREAM + (255,), anchor="mm")
    img = glow_layer(img, fn, 16, 2)
    d = ImageDraw.Draw(img, "RGBA")
    for name, role, dx, dy in nodes:
        x, y = cx + dx, cy + dy
        d.rounded_rectangle([x - 300, y - 75, x + 300, y + 75], radius=18, fill=(20, 20, 26, 240), outline=(120, 110, 90), width=3)
        text(d, (x, y - 22), name, F(42, "Bold"), CREAM, "mm")
        text(d, (x, y + 30), role, F(30, "Medium"), DIM, "mm")
    text(d, (W / 2, 110), "THE MACHINE", SF(90), GOLD, "mm", spacing=8)
    return img


def p_merger():
    img = bg((8, 14, 20), (2, 4, 6), glow=(20, 50, 70), glow_xy=(0.7, 0.5), seed=11)
    d = ImageDraw.Draw(img, "RGBA")
    parts = [("ACN", "Tinubu"), ("CPC", "Buhari"), ("ANPP", ""), ("APGA", "faction")]
    for i, (p, sub) in enumerate(parts):
        x, y = 360, 220 + i * 210
        d.line([x + 100, y, 1180, 540], fill=(120, 140, 160, 160), width=4)
        d.ellipse([x - 90, y - 90, x + 90, y + 90], fill=(24, 34, 44), outline=GOLD if p == "ACN" else (140, 150, 160), width=5)
        text(d, (x, y - (12 if sub else 0)), p, F(46, "Black"), CREAM, "mm")
        if sub:
            text(d, (x, y + 38), sub, F(24, "Medium"), DIM, "mm")

    def fn(dd):
        dd.ellipse([1180, 340, 1580, 740], fill=(10, 60, 40, 255), outline=GOLD + (255,), width=10)
        dd.text((1380, 510), "APC", font=F(130, "Black"), fill=CREAM + (255,), anchor="mm")
        dd.text((1380, 620), "2013", font=F(46, "Bold"), fill=GOLD + (255,), anchor="mm")
    img = glow_layer(img, fn, 26, 2)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (1380, 860), "2015: first opposition win", F(44, "Bold"), GOLD, "mm")
    text(d, (1380, 920), "over a sitting president", F(36, "Medium"), CREAM, "mm")
    return img


def p_case1993():
    img = bg((20, 16, 12), (6, 4, 3), glow=(60, 40, 20), seed=12)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([300, 150, 1000, 230], radius=16, fill=(196, 160, 100))
    d.rounded_rectangle([260, 200, W - 260, 1000], radius=20, fill=(214, 180, 118))
    d.rounded_rectangle([320, 260, W - 320, 960], radius=8, fill=(244, 238, 222))
    text(d, (340, 160), "CASE BACKGROUND · 1993", F(36, "Black"), (70, 50, 20), shadow=False)
    rows = [("Venue", "U.S. federal court, Chicago (civil forfeiture)"),
            ("Allegation", "Funds linked to heroin-trafficking proceeds"),
            ("Outcome", "Settlement — $460,000 forfeited"),
            ("Criminal charge", "None"),
            ("Tinubu's position", "Denies any wrongdoing")]
    y = 330
    for k, v in rows:
        text(d, (400, y), k.upper(), F(30, "Black"), (140, 40, 30), shadow=False)
        text(d, (760, y), v, F(40, "Medium"), (30, 28, 24), shadow=False)
        d.line([400, y + 80, W - 400, y + 80], fill=(200, 190, 170), width=2)
        y += 120
    text(d, (W - 400, 900), "Summary graphic — not an original document", F(24, "Medium"), (120, 110, 90), "ra", shadow=False)
    return img


def p_certificate():
    img = bg((14, 14, 18), (4, 4, 6), glow=(50, 30, 20), seed=13)
    d = ImageDraw.Draw(img, "RGBA")
    d.line([W / 2, 160, W / 2, 940], fill=(90, 90, 100), width=3)
    card(d, (120, 200, W / 2 - 60, 880), "1999",
         ["Election form listed", "the University of Chicago", ("University: no record", (240, 140, 120)),
          ("Tinubu: error by aides", DIM)], accent=GOLD, title_size=90, line_size=40)
    card(d, (W / 2 + 60, 200, W - 120, 880), "2023",
         ["Chicago State University", "records released in U.S. court", ("Graduation confirmed", (150, 220, 170)),
          ("Certificate to INEC disputed", (240, 140, 120)), ("Supreme Court: not admitted", DIM)],
         accent=RED, title_size=90, line_size=40)
    return img


def p_cct():
    img = bg((12, 12, 16), (3, 3, 5), seed=14)
    d = ImageDraw.Draw(img, "RGBA")
    card(d, (120, 220, W / 2 - 40, 860), "CODE OF CONDUCT TRIBUNAL",
         ["2011", "Alleged foreign bank", "accounts while governor", ("Outcome: discharged", (150, 220, 170))],
         accent=GOLD, title_size=40, line_size=44)
    card(d, (W / 2 + 40, 220, W - 120, 860), "ALPHA BETA CONSULTING",
         ["Private firm doing revenue", "work for Lagos State", ("Critics allege links", (240, 140, 120)),
          ("Tinubu: denies any stake", DIM)], accent=RED, title_size=40, line_size=44)
    return img


def p_bullion():
    img = bg((6, 8, 14), (2, 2, 4), seed=15)
    d = ImageDraw.Draw(img, "RGBA")
    # wall + gate
    d.rectangle([0, 380, W, 860], fill=(20, 20, 26))
    d.rectangle([700, 360, 1360, 860], fill=(36, 36, 44))
    for x in range(720, 1350, 40):
        d.line([x, 380, x, 860], fill=(60, 60, 70), width=6)
    d.rectangle([0, 860, W, H], fill=(14, 14, 18))
    vans = [(150, 0.9), (1300, 1.05)]
    for vx, s in vans:
        vy = 980
        d.rounded_rectangle([vx, vy - 330 * s, vx + 520 * s, vy - 60 * s], radius=26, fill=(40, 44, 48))
        d.rectangle([vx + 380 * s, vy - 300 * s, vx + 500 * s, vy - 200 * s], fill=(70, 90, 100))
        for wx in (vx + 100 * s, vx + 420 * s):
            d.ellipse([wx - 50 * s, vy - 110 * s, wx + 50 * s, vy - 10 * s], fill=(8, 8, 8))
    img = glow_layer(img, lambda dd: [dd.ellipse([vx + 490 * s, 980 - 140 * s, vx + 540 * s, 980 - 100 * s],
                                                 fill=(255, 240, 200, 255)) for vx, s in vans], 40, 3)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (110, 110), "LAGOS · FEBRUARY 2019", SF(80), GOLD)
    text(d, (114, 220), "“It's my money … not government money”  (paraphrase)", F(36, "Medium"), CREAM)
    return img


def p_endsars():
    img = bg((40, 44, 52), (10, 10, 14), glow=(60, 60, 50), glow_xy=(0.5, 0.2), seed=16)
    d = ImageDraw.Draw(img, "RGBA")
    crowd(d, 1080, 41, (36, 38, 44), n=40, scale=0.8)
    crowd(d, 1120, 42, (12, 12, 16), n=46, scale=1.05, signs=("#EndSARS", "END POLICE BRUTALITY", "#EndSARS NOW"), flags=3)
    text(d, (110, 110), "#EndSARS", SF(130), GOLD)
    text(d, (114, 250), "October 2020", F(42, "SemiBold"), CREAM)
    return img


def p_lekki():
    img = bg((14, 10, 22), (2, 2, 4), glow=(90, 20, 20), glow_xy=(0.5, 0.65), seed=17)
    d = ImageDraw.Draw(img, "RGBA")
    c = (6, 6, 8)
    # toll plaza canopy and booths
    d.polygon([(240, 360), (W - 240, 360), (W - 200, 440), (200, 440)], fill=c)
    for i in range(7):
        x = 300 + i * 220
        d.rectangle([x, 440, x + 26, 800], fill=c)
        d.rounded_rectangle([x + 50, 600, x + 150, 800], radius=8, fill=c)
    d.rectangle([0, 800, W, H], fill=(10, 8, 10))
    img = glow_layer(img, lambda dd: [dd.rectangle([280 + i * 220, 444, 460 + i * 220, 452], fill=(255, 250, 230, 255))
                                      for i in range(7)], 30, 3)
    d = ImageDraw.Draw(img, "RGBA")
    crowd(d, 1150, 51, (4, 4, 6), n=36, scale=0.9, flags=4)
    text(d, (110, 110), "20 · 10 · 2020", SF(110), (240, 90, 80))
    text(d, (114, 250), "Lekki Toll Gate · Lagos", F(42, "SemiBold"), CREAM)
    return img


def p_fire():
    img = bg((30, 12, 6), (4, 2, 2), glow=(220, 90, 20), glow_xy=(0.5, 0.6), glow_r=0.8, seed=18)
    d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(5)
    for _ in range(60):  # smoke
        x, y, r = rng.uniform(400, 1500), rng.uniform(0, 500), rng.uniform(80, 240)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(30, 26, 26, 50))
    img = img.filter(ImageFilter.GaussianBlur(4))
    d = ImageDraw.Draw(img, "RGBA")
    c = (8, 6, 6)
    d.rectangle([520, 380, 1400, 1000], fill=c)
    for r in range(5):
        for k in range(9):
            x, y = 570 + k * 92, 430 + r * 100
            col = (255, rng.randint(120, 200), 40, 255) if rng.random() < 0.45 else (30, 20, 16, 255)
            d.rectangle([x, y, x + 52, y + 60], fill=col)
    img = glow_layer(img, lambda dd: [dd.polygon([(x, 390), (x + rng.uniform(30, 90), 390 - rng.uniform(120, 300)),
                                                  (x + rng.uniform(80, 140), 390)], fill=(255, 140, 30, 220))
                                      for x in range(520, 1380, 70)], 30, 2)
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 1000, W, H], fill=(6, 4, 4))
    text(d, (110, 110), "LAGOS · 21 OCTOBER 2020", SF(76), GOLD)
    text(d, (114, 210), "TVC  ·  The Nation", F(44, "SemiBold"), CREAM)
    return img


def quote_plate(big, small, attrib, accent=GOLD, seed=19, font_size=230):
    img = bg((12, 10, 8), (0, 0, 0), glow=(60, 44, 16), glow_r=0.6, seed=seed)
    img = particles(img, 120, seed, maxr=2.5)

    def fn(d):
        d.text((W / 2, 470), big, font=SF(font_size), fill=accent + (255,), anchor="mm")
    img = glow_layer(img, fn, 30, 2)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (W / 2 - 600, 260), "“", SF(260), accent + (120,), "mm", shadow=False)
    if small:
        text(d, (W / 2, 680), small, SF(80, "Italic"), CREAM, "mm")
    d.line([W / 2 - 200, 790, W / 2 + 200, 790], fill=accent, width=3)
    text(d, (W / 2, 850), attrib, F(36, "Medium"), DIM, "mm")
    return img


def p_quote_emilokan():
    return quote_plate("EMI LO KAN", "“It is my turn.”", "— Bola Ahmed Tinubu, Abeokuta, June 2022")


def p_quote_subsidy():
    return quote_plate("Fuel subsidy is gone.", "", "— President Tinubu, inaugural address, 29 May 2023", font_size=170)


def p_ticket():
    img = bg((10, 16, 14), (2, 4, 4), glow=(20, 60, 40), seed=20)
    d = ImageDraw.Draw(img, "RGBA")
    for i, (name, role) in enumerate([("BOLA AHMED TINUBU", "Presidential candidate · Muslim"),
                                      ("KASHIM SHETTIMA", "Running mate · Muslim")]):
        x = W / 2 + (i * 2 - 1) * 440
        d.rounded_rectangle([x - 380, 220, x + 380, 880], radius=30, fill=(18, 24, 22, 240), outline=GOLD, width=4)
        d.ellipse([x - 110, 290, x + 110, 510], fill=(60, 70, 66))
        d.chord([x - 200, 520, x + 200, 900], 180, 360, fill=(60, 70, 66))
        d.rectangle([x - 380, 700, x + 380, 880], fill=(18, 24, 22))
        text(d, (x, 750), name, F(44, "Black"), CREAM, "mm")
        text(d, (x, 815), role, F(32, "Medium"), DIM, "mm")
    text(d, (W / 2, 990), "APC 2023  ·  MUSLIM–MUSLIM TICKET", F(44, "Black"), GOLD, "mm", spacing=4)
    text(d, (W / 2, 560), "+", F(120, "Black"), GOLD, "mm")
    return img


def p_results():
    img = bg((10, 12, 16), (2, 3, 4), seed=21)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (120, 100), "2023 PRESIDENTIAL ELECTION", F(56, "Black"), CREAM)
    text(d, (124, 180), "Official results declared by INEC · turnout 26.7%", F(34, "Medium"), DIM)
    data = [("Bola Tinubu", "APC", 8794726, 36.6, GREEN), ("Atiku Abubakar", "PDP", 6984520, 29.1, (200, 60, 60)),
            ("Peter Obi", "LP", 6101533, 25.4, (80, 160, 210)), ("Rabiu Kwankwaso", "NNPP", 1496687, 6.2, (200, 160, 60))]
    y = 300
    for name, party, votes, pct, col in data:
        text(d, (120, y + 10), name, F(44, "Bold"), CREAM)
        text(d, (120, y + 66), party, F(30, "Bold"), DIM)
        bw = 860 * votes / 8794726
        d.rounded_rectangle([620, y, 620 + bw, y + 100], radius=12, fill=col)
        text(d, (640 + bw, y + 50), f"{votes:,}  ·  {pct}%", F(40, "Bold"), CREAM, "lm")
        y += 170
    text(d, (W - 120, 1000), "Source: Independent National Electoral Commission (INEC)", F(26, "Medium"), DIM, "ra")
    return img


def p_court():
    img = bg((26, 22, 18), (4, 3, 2), glow=(80, 60, 30), glow_xy=(0.3, 0.4), seed=22)
    d = ImageDraw.Draw(img, "RGBA")
    # gavel
    g = Image.new("RGBA", (900, 500), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    gd.rounded_rectangle([60, 60, 420, 220], radius=30, fill=(100, 56, 26))
    gd.rectangle([120, 50, 150, 230], fill=(200, 160, 80))
    gd.rectangle([330, 50, 360, 230], fill=(200, 160, 80))
    gd.rounded_rectangle([400, 115, 860, 165], radius=20, fill=(120, 70, 34))
    g = g.rotate(25, expand=True, resample=Image.BICUBIC)
    img.paste(g, (180, 260), g)
    d.ellipse([250, 820, 750, 900], fill=(70, 40, 20))
    d.rectangle([250, 780, 750, 860], fill=(90, 52, 24))
    d.ellipse([250, 740, 750, 820], fill=(120, 72, 36))
    text(d, (1450, 380), "26 OCT 2023", SF(110), GOLD, "mm")
    text(d, (1450, 500), "SUPREME COURT", F(56, "Black"), CREAM, "mm", spacing=6)
    text(d, (1450, 580), "Election victory upheld", F(40, "Medium"), DIM, "mm")
    text(d, (1450, 640), "Petitions by Atiku & Obi dismissed", F(40, "Medium"), DIM, "mm")
    return img


def p_economy():
    img = bg((14, 8, 8), (3, 2, 2), glow=(70, 20, 16), seed=23)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (W / 2, 140), "THE COST OF REFORM", SF(90), GOLD, "mm", spacing=4)
    stats = [("PETROL", "₦185 → ₦500+", "per litre · mid-2023"),
             ("NAIRA", "₦460 → ₦1,500+", "per US dollar · 2023–24"),
             ("INFLATION", "34.2%", "June 2024 · ~28-year high")]
    for i, (k, v, s) in enumerate(stats):
        x0 = 110 + i * 580
        d.rounded_rectangle([x0, 300, x0 + 540, 860], radius=24, fill=(24, 14, 14, 240), outline=RED, width=4)
        text(d, (x0 + 270, 400), k, F(44, "Black"), (240, 150, 140), "mm", spacing=6)
        text(d, (x0 + 270, 580), v, F(68 if len(v) > 6 else 120, "Black"), CREAM, "mm")
        text(d, (x0 + 270, 760), s, F(32, "Medium"), DIM, "mm")
    text(d, (W / 2, 960), "Figures rounded · sources: NNPC pump prices, CBN / NBS data", F(26, "Medium"), DIM, "mm")
    return img


def p_protest():
    img = bg((150, 120, 90), (40, 30, 26), seed=24)
    d = ImageDraw.Draw(img, "RGBA")
    crowd(d, 1060, 61, (90, 70, 60), n=50, scale=0.75)
    crowd(d, 1120, 62, (24, 18, 16), n=44, scale=1.1, signs=("#EndBadGovernance", "WE ARE HUNGRY", "#EndBadGovernance"),
          flags=2)
    text(d, (110, 110), "AUGUST 2024", SF(110), (30, 20, 16), shadow=False)
    text(d, (114, 240), "#EndBadGovernance protests", F(42, "SemiBold"), (40, 26, 20), shadow=False)
    return img


def p_ledger():
    img = bg((10, 12, 14), (2, 3, 4), seed=25)
    d = ImageDraw.Draw(img, "RGBA")
    card(d, (120, 180, W / 2 - 40, 900), "REFORMS",
         ["✓ Minimum wage ₦70,000 (2024)", "✓ Student loan scheme (2024)", "✓ Tax reform laws (2025)",
          "✓ Fuel subsidy & FX overhaul"], accent=GREEN, title_size=60, line_size=40)
    card(d, (W / 2 + 40, 180, W - 120, 900), "CRITICISMS",
         ["× New presidential jet", "× Cost of coastal highway", "× Rivers emergency rule (2025)",
          "× Cost-of-living crisis"], accent=RED, title_size=60, line_size=40)
    return img


def p_legacy():
    img = bg((6, 8, 8), (0, 0, 0), glow=(20, 50, 34), seed=26)
    img = particles(img, 200, 27, maxr=2.5)
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 0, W / 3, 14], fill=(0, 135, 81))
    d.rectangle([W / 3, 0, 2 * W / 3, 14], fill=(240, 240, 240))
    d.rectangle([2 * W / 3, 0, W, 14], fill=(0, 135, 81))
    for i, (wd, col) in enumerate([("DEMOCRAT?", CREAM), ("GODFATHER?", RED), ("REFORMER?", GREEN)]):
        text(d, (W / 2, 330 + i * 200), wd, SF(150), col, "mm", spacing=10)
    return img


def p_credits():
    img = bg((6, 6, 8), (0, 0, 0), seed=27)
    d = ImageDraw.Draw(img, "RGBA")
    text(d, (W / 2, 200), "JAGABAN", SF(110), GOLD, "mm", spacing=14)
    lines = [("Written & produced for", DIM), ("Basit Tiamiyu", CREAM),
             ("Narration: AI voice (Kokoro TTS)  ·  Score & sound design: original, generated", DIM),
             ("Photos via Wikimedia Commons: official portrait (Presidency of Nigeria, CC BY-SA 4.0);", DIM),
             ("Chatham House, 2011 (CC BY 2.0); FCDO, Abuja 2024 (CC BY 2.0). Other visuals are illustrations.", DIM),
             ("Allegations are reported as allegations. Tinubu has denied wrongdoing in each case,", DIM),
             ("and none of the controversies described has led to a criminal conviction.", DIM),
             ("Sources: INEC, NBS, CBN, Supreme Court of Nigeria judgment (Oct 2023),", DIM),
             ("Lagos State #EndSARS Judicial Panel report (2021), contemporaneous news reporting.", DIM)]
    y = 360
    for s, c in lines:
        text(d, (W / 2, y), s, F(44 if c == CREAM else 32, "Bold" if c == CREAM else "Medium"), c, "mm")
        y += 62
    return img


def load_photo(path):
    im = ImageOps.fit(Image.open(path).convert("RGB"), (W, H), Image.LANCZOS)
    a = np.array(im).astype(np.float32)
    a = a * np.array([1.04, 1.0, 0.92]) * 0.9  # warm, slightly darker documentary grade
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def plate(sc):
    photo = os.path.join(HERE, "photos", sc["id"] + ".jpg")
    if os.path.exists(photo):
        return load_photo(photo)
    return globals()["p_" + sc["plate"]]()


# ------------------------------------------------------------------ opening portrait (eye push-in)
def portrait():
    """Returns (3840x2160 image, (eye_x, eye_y) in pixels). Uses photos/portrait.jpg when present."""
    BW, BH = 3840, 2160
    photo = os.path.join(HERE, "photos", "portrait.jpg")
    if os.path.exists(photo):
        import json
        src = Image.open(photo).convert("RGB")
        meta = os.path.join(HERE, "photos", "portrait.json")
        ex, ey = json.load(open(meta))["eye"] if os.path.exists(meta) else (0.47, 0.38)
        # 16:9 canvas: blurred, darkened copy behind; the full portrait in front, eye kept on the canvas
        back = ImageOps.fit(src, (BW, BH), Image.LANCZOS).filter(ImageFilter.GaussianBlur(60))
        back = Image.blend(back, Image.new("RGB", back.size, (0, 0, 0)), 0.55)
        fh = BH
        fw = int(src.width * fh / src.height)
        front = src.resize((fw, fh), Image.LANCZOS)
        x0 = (BW - fw) // 2
        back.paste(front, (x0, 0))
        # soft edge where the portrait meets the backdrop
        edge = Image.new("L", (BW, BH), 0)
        ImageDraw.Draw(edge).rectangle([x0 + 40, 0, x0 + fw - 40, BH], fill=255)
        edge = edge.filter(ImageFilter.GaussianBlur(40))
        blurred = ImageOps.fit(src, (BW, BH), Image.LANCZOS).filter(ImageFilter.GaussianBlur(60))
        blurred = Image.blend(blurred, Image.new("RGB", blurred.size, (0, 0, 0)), 0.55)
        im = Image.composite(back, blurred, edge)
        return im, (x0 + ex * fw, ey * fh)
    # stylised silhouette in his trademark fila cap, rim-lit, with a glowing golden iris
    S = 2
    img = Image.new("RGB", (BW, BH), (4, 4, 6))
    a = np.array(img).astype(np.float32)
    yy, xx = np.mgrid[0:BH, 0:BW]
    rim = np.clip(1 - np.sqrt(((xx - 2500) / 1.3) ** 2 + (yy - 800) ** 2) / 1500, 0, 1)[..., None] ** 2
    a += rim * np.array([120, 84, 30])
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img, "RGBA")
    c = (10, 9, 9)
    cx, cy = 1920, 1080
    sil = Image.new("L", (BW, BH), 0)
    sd = ImageDraw.Draw(sil)
    sd.ellipse([cx - 440, cy - 560, cx + 440, cy + 520], fill=255)                  # head
    sd.ellipse([cx - 120, cy + 420, cx + 150, cy + 560], fill=255)                  # chin
    sd.rectangle([cx - 240, cy + 380, cx + 240, cy + 820], fill=255)                # neck
    sd.ellipse([cx - 1550, cy + 700, cx + 1550, cy + 2600], fill=255)               # shoulders / agbada
    sd.ellipse([cx - 520, cy - 120, cx - 380, cy + 160], fill=255)                  # ear
    # fila cap: band hugging the head, crown folded over to his left
    cap = [(cx - 470, cy - 330), (cx - 480, cy - 520), (cx - 400, cy - 760), (cx - 180, cy - 900),
           (cx + 120, cy - 960), (cx + 420, cy - 930), (cx + 640, cy - 860), (cx + 700, cy - 760),
           (cx + 560, cy - 640), (cx + 470, cy - 420)]
    sd.polygon(cap, fill=255)
    sil = sil.filter(ImageFilter.GaussianBlur(3))
    img.paste(Image.new("RGB", img.size, c), (0, 0), sil)
    # rim light: blurred edge of the silhouette on the lit (right) side
    edge = ImageChops.subtract(sil, sil.filter(ImageFilter.MinFilter(15)))
    mask = Image.fromarray((np.clip((xx - cx + 150) / 500, 0, 1) * 255).astype(np.uint8))
    edge = ImageChops.multiply(edge, mask)
    rim_layer = Image.new("RGBA", img.size, (255, 196, 110, 0))
    rim_layer.putalpha(edge)
    img = Image.alpha_composite(img.convert("RGBA"), Image.merge("RGBA", (*rim_layer.split()[:3], edge.filter(ImageFilter.GaussianBlur(20)))))
    img = Image.alpha_composite(img, rim_layer).convert("RGB")
    ex, ey = cx + 190, cy - 40
    a = np.array(img).astype(np.float32)
    r = np.sqrt((xx - ex) ** 2 + (yy - ey) ** 2)
    ang = np.arctan2(yy - ey, xx - ex)
    iris = np.clip(70.5 - r, 0, 1).astype(np.float32)
    fib = 0.65 + 0.35 * np.sin(ang * 48 + r * 0.25) * np.sin(ang * 13)
    col = np.stack([226 * fib, 160 * fib, 60 * fib], -1) * (1 - (r / 70) ** 3)[..., None]
    a = a * (1 - iris[..., None]) + col * iris[..., None]
    pupil = np.clip(24.5 - r, 0, 1)[..., None]
    a = a * (1 - pupil)
    a += np.clip(1 - r / 260, 0, 1)[..., None] ** 3 * np.array([90, 60, 20])          # glow
    cl = np.clip(8.5 - np.sqrt((xx - ex + 18) ** 2 + (yy - ey + 20) ** 2), 0, 1)[..., None]
    a = a * (1 - cl) + 255 * cl                                                           # catch-light
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img, "RGBA")
    d.text((240, 1880), "BOLA AHMED TINUBU", font=F(84, "Bold"), fill=CREAM + (220,))
    d.text((244, 1990), "Illustration", font=F(40, "Medium"), fill=DIM + (200,))
    return img, (ex, ey)


def p_portrait():
    return portrait()[0].resize((W, H), Image.LANCZOS)


def p_occupy():
    img = bg((190, 170, 140), (70, 60, 50), seed=28)
    d = ImageDraw.Draw(img, "RGBA")
    crowd(d, 1060, 71, (110, 96, 84), n=56, scale=0.72)
    crowd(d, 1120, 72, (30, 24, 20), n=48, scale=1.1,
          signs=("OCCUPY NIGERIA", "₦65 → ₦141 ?!", "NO TO SUBSIDY REMOVAL"), flags=3)
    text(d, (110, 110), "JANUARY 2012", SF(110), (40, 28, 20), shadow=False)
    text(d, (114, 240), "Occupy Nigeria · Lagos shuts down", F(42, "SemiBold"), (50, 34, 24), shadow=False)
    return img


def p_uturn():
    img = bg((10, 10, 12), (2, 2, 3), seed=29)
    a = np.array(img).astype(np.float32)
    left = np.zeros_like(a)
    left[:, : W // 2] = np.array([70, 52, 30])
    img = Image.fromarray(np.clip(a + left * 0.6, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img, "RGBA")
    d.line([W / 2, 120, W / 2, 960], fill=GOLD, width=3)
    text(d, (W / 4, 190), "2012", SF(150), (235, 210, 170), "mm")
    text(d, (W / 4, 300), "Tinubu, opposing Jonathan's removal", F(34, "Medium"), (210, 190, 160), "mm")
    for i, ln in enumerate(["“The government has", "tossed the people into", "the depths of the", "midnight sea.”"]):
        text(d, (W / 4, 470 + i * 92), ln, SF(70, "Italic"), (245, 232, 210), "mm")
    text(d, (3 * W / 4, 190), "2023", SF(150), GOLD, "mm")
    text(d, (3 * W / 4, 300), "President Tinubu, inaugural address", F(34, "Medium"), DIM, "mm")
    text(d, (3 * W / 4, 600), "“Fuel subsidy", SF(96), CREAM, "mm")
    text(d, (3 * W / 4, 710), "is gone.”", SF(96), CREAM, "mm")

    def fn(dd):
        dd.ellipse([W / 2 - 120, 880, W / 2 + 120, 1040], fill=(30, 8, 8, 255), outline=RED + (255,), width=6)
        dd.text((W / 2, 960), "U-TURN", font=F(50, "Black"), fill=RED + (255,), anchor="mm")
    return glow_layer(img, fn, 18, 2)
