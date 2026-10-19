"""MR MONEY picture engine (1920x1080, 30 fps).

Look: dark cinematic film, warm gold accents, grain and vignette. Korty-style chapter cards (huge distressed word,
small mono subtitle), place tags, kinetic typography, counters, chart positions, a phone-text reconstruction,
and licensed photos with a "centre strip" treatment for small or vertical pictures.

usage (from documentary/):  python3 mrmoney/engine.py BUILD_DIR OUT.mp4 [start_sec end_sec]
"""
import hashlib, json, math, os, subprocess, sys
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageEnhance, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from script import S

OW, OH, FPS = 1920, 1080, 30
PW, PH = 2240, 1260                 # photo plate size (room for camera moves)
XF_SCENE, XF_SHOT = 0.6, 0.3
LEAD = 0.5
CARD_DUR, LOGO_DUR = 3.3, 5.6
F = lambda n: os.path.join(HERE, "fonts", n)
INTER = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
GOLD, GOLD2, CREAM, RED, INK, GREY = (232, 184, 74), (255, 214, 120), (245, 238, 224), (214, 48, 49), (10, 10, 12), (150, 146, 140)
NOSUBS = bool(os.environ.get("NOSUBS"))

_fonts = {}


def fnt(name, size):
    k = (name, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(name if name.startswith("/") else F(name), size)
    return _fonts[k]


ANTON = lambda s: fnt("Anton-Regular.ttf", s)
BEBAS = lambda s: fnt("BebasNeue-Regular.ttf", s)
SERIF = lambda s: fnt("DMSerifDisplay-Regular.ttf", s)
SERIFI = lambda s: fnt("DMSerifDisplay-Italic.ttf", s)
MONO = lambda s: fnt("SpaceMono-Regular.ttf", s)
MONOB = lambda s: fnt("SpaceMono-Bold.ttf", s)
SANS = lambda s, w="SemiBold": fnt(INTER.format(w), s)


def clamp(x, a=0.0, b=1.0):
    return min(max(x, a), b)


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    return 1 - (1 - clamp(x)) ** 3


def ease_back(x, k=1.6):
    x = clamp(x)
    return 1 + (k + 1) * (x - 1) ** 3 + k * (x - 1) ** 2


# ------------------------------------------------------------------ timeline
def at_time(at, sents):
    i, fr = (at if isinstance(at, tuple) else (at, 0.0))
    i = min(i, len(sents) - 1)
    a, b = sents[i]
    return a + (b - a) * fr


def build(timing_path):
    timing = json.load(open(timing_path)) if os.path.exists(timing_path) else {}
    out, t = [], 0.0
    for sc in S:
        e = dict(sc)
        if sc.get("card"):
            e["dur"] = CARD_DUR
        elif sc.get("logo"):
            e["dur"] = LOGO_DUR
        else:
            v = timing.get(sc["id"])
            vd = v["dur"] if v else 3.0
            e["dur"] = LEAD + vd + sc.get("hold", 0.7)
            e["voice_at"] = LEAD
            e["subs"] = [[LEAD + a, LEAD + b, s] for a, b, s in (v["subs"] if v else [])]
            e["sents"] = [[LEAD + a, LEAD + b] for a, b in (v["sents"] if v else [[0, vd]])]
        xf = XF_SCENE if out else 0.0
        e["start"] = max(0.0, t - xf)
        e["xf"] = xf
        e["end"] = e["start"] + e["dur"]
        shots = []
        for k, sh in enumerate(sc.get("shots") or []):
            at = sh["at"]
            if k > 0 and sh["kind"] == "kin" and at == 0:      # a later word block starts when its first word does
                ws = [w[1] for w in sh["words"] if isinstance(w, tuple)]
                at = min(ws, key=lambda x: at_time(x, e["sents"])) if ws else at
            s0 = 0.0 if k == 0 else max(0.0, at_time(at, e["sents"]) - 0.15)
            shots.append(dict(sh, t0=s0))
        for k, sh in enumerate(shots):
            sh["t1"] = shots[k + 1]["t0"] if k + 1 < len(shots) else e["dur"]
            # word / element appearance times
            if sh["kind"] in ("kin",):
                tl = []
                for w in sh["words"]:
                    txt, a = (w if isinstance(w, tuple) else (w, None))
                    ta = sh["t0"] + 0.25 if a is None else max(sh["t0"] + 0.15, at_time(a, e["sents"]) - 0.05)
                    tl.append((txt, ta))
                sh["tl"] = tl
            if sh["kind"] == "phone":
                sh["tl"] = [(side, txt, when, max(sh["t0"] + 0.3, at_time(a, e["sents"]))) for side, txt, when, a in sh["msgs"]]
            if sh["kind"] == "quote":
                sh["qt"] = max(sh["t0"] + 0.2, at_time(sh["at"], e["sents"]) if k == 0 else sh["t0"] + 0.2)
        e["shots"] = shots
        out.append(e)
        t = e["end"]
    return out, t


BUILD = sys.argv[1] if len(sys.argv) > 1 else "."
TL, TOTAL = build(os.path.join(BUILD, "timing.json"))


# ------------------------------------------------------------------ materials
_cache = {}


def cache_key(*a):
    return hashlib.md5(repr(a).encode()).hexdigest()[:16]


def plate_dir():
    d = os.path.join(BUILD, "plates")
    os.makedirs(d, exist_ok=True)
    return d


def noise_tex(w, h, seed, scale=3, blur=1.0):
    r = np.random.default_rng(seed)
    n = r.random((h // scale + 1, w // scale + 1)).astype(np.float32)
    im = Image.fromarray((n * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return im.filter(ImageFilter.GaussianBlur(blur)) if blur else im


def dark_bg(seed=0, tint=(26, 22, 20)):
    """textured near-black backdrop with a soft warm glow (not flat black)"""
    k = ("bg", seed, tint)
    if k not in _cache:
        n = np.asarray(noise_tex(OW, OH, seed, 6, 2.0), np.float32) / 255.0
        yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
        glow = np.exp(-(((xx - OW * 0.5) / (OW * 0.55)) ** 2 + ((yy - OH * 0.42) / (OH * 0.6)) ** 2))
        base = np.array(tint, np.float32)[None, None, :] * (0.55 + 0.65 * glow[..., None]) * (0.85 + 0.3 * n[..., None])
        _cache[k] = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    return _cache[k]


def grade(img, mode):
    img = img.convert("RGB")
    if mode == "bw":
        g = ImageOps.grayscale(img)
        g = ImageOps.autocontrast(g, cutoff=1)
        img = ImageOps.colorize(g, (8, 8, 10), (246, 238, 222), mid=(120, 112, 102))
        img = ImageEnhance.Contrast(img).enhance(1.12)
    elif mode == "gold":
        a = np.asarray(img, np.float32) / 255.0
        lum = a.mean(axis=2, keepdims=True)
        tone = np.array([1.08, 0.94, 0.70])
        a = a * 0.55 + lum * 0.45
        a = np.clip(a * tone * 1.18, 0, 1) ** 0.95
        img = Image.fromarray((a * 255).astype(np.uint8))
        img = ImageEnhance.Contrast(img).enhance(1.15)
    elif mode == "night":
        a = np.asarray(img, np.float32) / 255.0
        lum = a.mean(axis=2, keepdims=True)
        a = a * 0.6 + lum * 0.4
        a = np.clip(a * np.array([0.72, 0.86, 1.08]) * 0.78, 0, 1) ** 1.15
        img = Image.fromarray((a * 255).astype(np.uint8))
    elif mode == "warm":
        a = np.asarray(img, np.float32) / 255.0
        lum = a.mean(axis=2, keepdims=True)
        a = a * 0.8 + lum * 0.2
        a = np.clip(a * np.array([1.06, 0.98, 0.86]), 0, 1)
        img = Image.fromarray((a * 255).astype(np.uint8))
        img = ImageEnhance.Contrast(img).enhance(1.08)
    return img


def photo_plate(sh):
    key = cache_key("plate2", sh["file"], sh.get("grade"), sh.get("strip"), sh.get("focus"))
    path = os.path.join(plate_dir(), key + ".jpg")
    if key in _cache:
        return _cache[key]
    if os.path.exists(path):
        im = Image.open(path).convert("RGB")
    else:
        src = Image.open(sh["file"]).convert("RGB")
        src = grade(src, sh.get("grade"))
        ar = src.width / src.height
        strip = sh.get("strip")
        if strip is None:
            strip = ar < 1.3
        if strip:
            bg = ImageOps.fit(src, (PW, PH), Image.LANCZOS, centering=sh.get("focus", (0.5, 0.5)))
            bg = bg.resize((PW // 8, PH // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6)).resize((PW, PH), Image.BICUBIC)
            bg = ImageEnhance.Brightness(bg).enhance(0.42)
            fh = int(PH * 0.86)
            fw = int(fh * ar)
            if fw > PW * 0.62:                       # wide but small source: centre crop to a tall strip
                fw = int(PW * 0.5)
                fg = ImageOps.fit(src, (fw, fh), Image.LANCZOS, centering=sh.get("focus", (0.5, 0.5)))
            else:
                fg = src.resize((fw, fh), Image.LANCZOS)
            fg = ImageEnhance.Sharpness(fg).enhance(1.3)
            sh_ = Image.new("L", (fw + 120, fh + 120), 0)
            ImageDraw.Draw(sh_).rectangle([60, 60, fw + 60, fh + 60], fill=170)
            sh_ = sh_.filter(ImageFilter.GaussianBlur(28))
            x, y = (PW - fw) // 2, (PH - fh) // 2
            bg.paste((0, 0, 0), (x - 60 + 14, y - 60 + 22), sh_)
            bg.paste(fg, (x, y))
            line = ImageDraw.Draw(bg)
            line.rectangle([x - 2, y - 2, x + fw + 1, y + fh + 1], outline=(255, 255, 255, 40), width=1)
            im = bg
        else:
            im = ImageOps.fit(src, (PW, PH), Image.LANCZOS, centering=sh.get("focus", (0.5, 0.5)))
        im.save(path, quality=93)
    _cache[key] = im
    return im


def camera(img, z, cx, cy):
    """crop a window of size (OW, OH)*PW/OW/z centred on (cx, cy) in plate coords and scale to output"""
    w, h = PW / z, PH / z
    x0 = clamp(cx - w / 2, 0, PW - w)
    y0 = clamp(cy - h / 2, 0, PH - h)
    return img.transform((OW, OH), Image.EXTENT, (x0, y0, x0 + w, y0 + h), Image.BILINEAR)


def photo_frame(sh, lt):
    im = photo_plate(sh)
    d = max(sh["t1"] - sh["t0"], 0.5)
    p = smooth((lt - sh["t0"]) / (d + 0.6))
    fx, fy = sh.get("focus", (0.5, 0.5))
    if sh.get("strip") or im is None:
        fx, fy = 0.5, 0.5
    mv = sh.get("move", "in")
    z0, z1 = (1.0, 1.1) if mv == "in" else (1.1, 1.0)
    z = z0 + (z1 - z0) * p
    cx = PW / 2 + (fx - 0.5) * PW * 0.12 * p
    cy = PH / 2 + (fy - 0.5) * PH * 0.10 * p
    return camera(im, z, cx, cy)


# ------------------------------------------------------------------ text helpers
def text_layer(key, w, h, draw_fn):
    if key not in _cache:
        lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw_fn(ImageDraw.Draw(lay), lay)
        _cache[key] = lay
    return _cache[key]


def put(base, lay, x, y, alpha=1.0, scale=1.0):
    if alpha <= 0.01:
        return
    if scale != 1.0:
        w, h = lay.size
        lay = lay.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.BICUBIC)
        x, y = x - (lay.width - w) // 2, y - (lay.height - h) // 2
    if alpha < 0.999:
        a = lay.getchannel("A").point(lambda v: int(v * alpha))
        lay = lay.copy()
        lay.putalpha(a)
    base.alpha_composite(lay, (int(x), int(y)))


def word_img(txt, font, fill, stroke=0, stroke_fill=(0, 0, 0), shadow=True, distress=None, spacing=0):
    key = ("w", txt, font.path, font.size, fill, stroke, shadow, distress, spacing)
    if key in _cache:
        return _cache[key]
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    if spacing:
        widths = [d0.textlength(c, font=font) for c in txt]
        tw = int(sum(widths) + spacing * (len(txt) - 1))
    else:
        tw = int(d0.textlength(txt, font=font))
    asc, desc = font.getmetrics()
    pad = 40 + stroke
    W, H = tw + pad * 2, asc + desc + pad * 2
    mask = Image.new("L", (W, H), 0)
    dm = ImageDraw.Draw(mask)
    if spacing:
        x = pad
        for c, cw in zip(txt, widths):
            dm.text((x, pad), c, font=font, fill=255, stroke_width=stroke, stroke_fill=255)
            x += cw + spacing
    else:
        dm.text((pad, pad), txt, font=font, fill=255, stroke_width=stroke, stroke_fill=255)
    if distress:      # rough, printed-on-concrete letters (Korty style)
        n = np.asarray(noise_tex(W, H, distress, 2, 0.6), np.float32)
        n2 = np.asarray(noise_tex(W, H, distress + 7, 9, 1.5), np.float32)
        m = np.asarray(mask, np.float32)
        keep = ((n * 0.55 + n2 * 0.45) > 70).astype(np.float32)
        speck = (n > 238).astype(np.float32)
        m = m * (0.82 + 0.18 * keep) * (1 - 0.9 * speck)
        mask = Image.fromarray(np.clip(m, 0, 255).astype(np.uint8))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if shadow:
        sh = mask.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.65))
        lay.paste((0, 0, 0, 255), (0, 6), sh)
    col = Image.new("RGBA", (W, H), fill + (255,))
    lay = Image.alpha_composite(lay, Image.composite(col, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
    _cache[key] = (lay, pad)
    return lay, pad


def center_word(base, txt, font, fill, cy, alpha=1.0, scale=1.0, dx=0, **kw):
    lay, pad = word_img(txt, font, fill, **kw)
    asc, desc = font.getmetrics()
    x = OW / 2 - lay.width / 2 + dx
    y = cy - (asc + desc) / 2 - pad
    put(base, lay, x, y, alpha, scale)
    return lay.width - 2 * pad


def fit_font(maker, txt, maxw, start):
    s = start
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    while s > 20 and d0.textlength(txt, font=maker(s)) > maxw:
        s -= 4
    return maker(s)


def darken(img, amt):
    return Image.blend(img, Image.new("RGB", img.size, (0, 0, 0)), amt)


# ------------------------------------------------------------------ shot renderers
def base_for(e, k, lt):
    """background for a graphic shot: previous photo in the scene (darkened) or textured dark"""
    for j in range(k - 1, -1, -1):
        p = e["shots"][j]
        if p["kind"] == "photo":
            return darken(photo_frame(p, lt), 0.62).convert("RGBA")
    seed = int(hashlib.md5(e["id"].encode()).hexdigest()[:4], 16) % 5
    return dark_bg(seed).convert("RGBA")


def appear(lt, ta, d=0.45):
    return ease_out((lt - ta) / d)


def kin_frame(e, sh, k, lt):
    base = base_for(e, k, lt)
    st = sh["style"]
    tl = sh["tl"]
    vis = [(t, ta) for t, ta in tl]
    n = len(vis)
    if st in ("tick", "stack", "list", "recipe"):
        size = {"tick": 150, "stack": 124, "list": 100, "recipe": 140}[st]
        if st == "list" and n > 4:
            size = 78
        lh = size * 1.22
        y0 = OH / 2 - (n - 1) * lh / 2 - 30
        last_on = max([i for i, (_, ta) in enumerate(vis) if lt >= ta] or [-1])
        for i, (txt, ta) in enumerate(vis):
            a = appear(lt, ta)
            if a <= 0:
                continue
            fill = CREAM
            if st == "tick" and i == n - 1:
                fill = GOLD
            if st == "list":
                fill = GOLD if i == last_on else (CREAM if i < last_on else CREAM)
            if st == "recipe" and txt.startswith("+"):
                fill = GOLD
            font = fit_font(ANTON, txt, OW - 260, size)
            label = (f"{i + 1:02d}   " + txt) if st == "list" else txt
            if st == "list":
                font = fit_font(ANTON, label, OW - 260, size)
            dim = 0.45 if (st == "list" and i < last_on) else 1.0
            center_word(base, label, font, fill, y0 + i * lh + (1 - a) * 30, alpha=a * dim)
    elif st == "big":
        for txt, ta in vis:
            a = appear(lt, ta, 0.6)
            if a > 0:
                font = fit_font(ANTON, txt, OW - 200, 300)
                center_word(base, txt, font, GOLD, OH / 2 - 20, alpha=a, scale=1.25 - 0.25 * ease_out((lt - ta) / 0.7), distress=11)
    elif st in ("name", "name1"):
        words = [t for t, _ in vis]
        n = len(words)
        for i, (txt, ta) in enumerate(vis):
            a = appear(lt, ta + i * 0.25, 0.7)
            size = 230 if st == "name1" else 190
            font = fit_font(ANTON, txt, OW - 220, size)
            cy = OH / 2 - (n - 1) * 110 + i * 220 - 20
            center_word(base, txt, font, CREAM if i == 0 and n > 1 else GOLD, cy, alpha=a, distress=5 + i, spacing=int(18 * (1 - a)) + 6)
        a2 = appear(lt, vis[-1][1] + 0.8)
        if st == "name1" and a2 > 0:
            center_word(base, "a Yoruba name most Nigerians hear for a woman", SERIFI(52), CREAM, OH / 2 + 170, alpha=a2 * 0.9)
    elif st == "meaning":
        cols = [(vis[0], vis[1], -340), (vis[2], vis[3], 340)]
        for (w1, t1), (w2, t2), dx in cols:
            a = appear(lt, t1, 0.6)
            center_word(base, w1, ANTON(260), GOLD, OH / 2 - 60, alpha=a, dx=dx, distress=3)
            a2 = appear(lt, t2 + 0.25)
            center_word(base, w2, SERIFI(72), CREAM, OH / 2 + 130, alpha=a2, dx=dx)
        a3 = appear(lt, vis[2][1] + 0.6)
        center_word(base, "+", ANTON(150), CREAM, OH / 2 - 60, alpha=a3 * 0.6)
    elif st == "define":
        a = appear(lt, vis[0][1], 0.6)
        center_word(base, vis[0][0], ANTON(330), RED, OH / 2 - 80, alpha=a, distress=21, scale=1.15 - 0.15 * ease_out((lt - vis[0][1]) / 0.6))
        a2 = appear(lt, vis[1][1])
        center_word(base, "/ gi · ran /   Yorùbá   adj.", MONO(40), GREY, OH / 2 + 120, alpha=a2)
        center_word(base, vis[1][0], ANTON(110), CREAM, OH / 2 + 220, alpha=a2)
    elif st == "promise":
        a = appear(lt, vis[0][1])
        center_word(base, vis[0][0], MONOB(64), GREY, OH / 2 - 170, alpha=a)
        a2 = appear(lt, vis[1][1], 0.8)
        center_word(base, vis[1][0], ANTON(280), GOLD, OH / 2 + 30, alpha=a2, distress=31, spacing=int(30 * (1 - a2)) + 4)
    elif st == "track":
        track_ui(base, vis, lt)
    elif st == "post":
        a = appear(lt, vis[0][1])
        center_word(base, vis[0][0], MONOB(64), GOLD, OH / 2 - 110, alpha=a)
        a2 = appear(lt, vis[1][1], 0.6)
        center_word(base, vis[1][0], SERIF(130), CREAM, OH / 2 + 40, alpha=a2)
        center_word(base, "OLAMIDE  ·  INSTAGRAM  ·  FEBRUARY 2022", MONO(34), GREY, OH / 2 + 190, alpha=a2 * 0.9)
    elif st == "album":
        album_tile(base, [t for t, _ in vis], lt - sh["t0"], e)
    elif st == "stamp":
        for txt, ta in vis:
            p = (lt - ta) / 0.35
            if p > 0:
                sc_ = 1 + 1.4 * math.exp(-max(p, 0) * 4) if p < 1 else 1.0
                lay = stamp_layer(txt)
                rot = lay
                w, h = rot.size
                put(base, rot, OW / 2 - w / 2, OH / 2 - h / 2, alpha=min(1, p * 2), scale=sc_)
    elif st == "candle":
        for txt, ta in vis:
            a = appear(lt, ta, 0.8)
            center_word(base, "IN MEMORY OF", MONO(30), GREY, OH - 230, alpha=a)
            center_word(base, txt, SERIF(64), CREAM, OH - 170, alpha=a)
    elif st == "award":
        a = appear(lt, vis[0][1], 0.6)
        if a > 0:
            award_card(base, [t for t, _ in vis], a)
    elif st == "reveal":
        a = appear(lt, vis[0][1] + 0.3, 1.4)
        center_word(base, vis[0][0], ANTON(150), CREAM, OH / 2 - 80, alpha=a)
        center_word(base, vis[1][0], ANTON(190), GOLD, OH / 2 + 90, alpha=appear(lt, vis[1][1] + 1.0, 1.4), distress=41)
    elif st == "final":
        a = appear(lt, vis[0][1], 0.9)
        center_word(base, vis[0][0], ANTON(230), GOLD, OH / 2 - 120, alpha=a, distress=51, spacing=10)
        center_word(base, vis[1][0], SERIFI(66), CREAM, OH / 2 + 50, alpha=appear(lt, vis[1][1] + 0.6))
        a3 = appear(lt, vis[2][1], 0.8)
        center_word(base, vis[2][0], ANTON(120), CREAM, OH / 2 + 220, alpha=a3, scale=1.2 - 0.2 * ease_out((lt - vis[2][1]) / 0.8))
    return base


def stamp_layer(txt):
    key = ("stamp", txt)
    if key not in _cache:
        font = ANTON(190)
        d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
        tw = int(d0.textlength(txt, font=font))
        W, H = tw + 160, 360
        m = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(m)
        d.rounded_rectangle([20, 40, W - 20, H - 40], 26, outline=255, width=16)
        d.text((80, 55), txt, font=font, fill=255)
        n = np.asarray(noise_tex(W, H, 77, 2, 0.5), np.float32)
        mm = np.asarray(m, np.float32) * np.clip((n - 40) / 120, 0.25, 1)
        m = Image.fromarray(mm.astype(np.uint8)).rotate(-8, expand=True, resample=Image.BICUBIC)
        lay = Image.new("RGBA", m.size, RED + (0,))
        lay.putalpha(m.point(lambda v: int(v * 0.92)))
        _cache[key] = lay
    return _cache[key]


def track_ui(base, vis, lt):
    """'now playing' card: big title, feature line, progress bar and live waveform"""
    title, ta = vis[0]
    a = appear(lt, ta, 0.6)
    d = ImageDraw.Draw(base)
    cx, cy = OW / 2, OH / 2
    w = 1100
    x0 = cx - w / 2
    box = Image.new("RGBA", (w, 520), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle([0, 0, w - 1, 519], 36, fill=(18, 16, 15, int(225 * a)), outline=(232, 184, 74, int(120 * a)), width=2)
    base.alpha_composite(box, (int(x0), int(cy - 260 + (1 - a) * 40)))
    yy = cy - 260 + (1 - a) * 40
    center_word(base, "NOW PLAYING", MONO(30), GREY, yy + 70, alpha=a)
    font = fit_font(ANTON, title, w - 120, 150)
    center_word(base, title, font, GOLD, yy + 190, alpha=a, shadow=False)
    if len(vis) > 1:
        center_word(base, vis[1][0], SANS(46, "Medium"), CREAM, yy + 300, alpha=appear(lt, vis[1][1]))
    # waveform
    n = 48
    for i in range(n):
        h = 12 + 60 * abs(math.sin(lt * 7.3 + i * 0.7) * math.sin(lt * 2.1 + i * 0.31)) * a
        x = x0 + 120 + i * (w - 240) / n
        d.rectangle([x, yy + 400 - h / 2, x + 9, yy + 400 + h / 2], fill=GOLD if i < n * ((lt - ta) % 6) / 6 else (90, 84, 76))
    d.rounded_rectangle([x0 + 120, yy + 470, x0 + w - 120, yy + 476], 3, fill=(70, 66, 60))
    d.rounded_rectangle([x0 + 120, yy + 470, x0 + 120 + (w - 240) * clamp(((lt - ta) % 6) / 6), yy + 476], 3, fill=GOLD)


def album_tile(base, lines, t, e):
    """typographic album tile (our own design, not the real cover) sliding in like a record"""
    size = 700
    key = ("album", tuple(lines))
    if key not in _cache:
        tile = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        g = Image.new("RGB", (size, size), (16, 14, 13))
        gd = ImageDraw.Draw(g)
        for r in range(0, size, 3):
            gd.line([(0, r), (size, r)], fill=(20 + (r % 9), 17, 15))
        gd.rectangle([0, size - 150, size, size], fill=GOLD)
        tile.paste(g, (0, 0))
        dd = ImageDraw.Draw(tile)
        y = 90
        for ln in lines:
            f = fit_font(ANTON, ln, size - 100, 170)
            dd.text((50, y), ln, font=f, fill=GOLD if ln == lines[-1] else CREAM)
            y += f.size * 1.15
        dd.text((50, size - 118), "ASAKE", font=ANTON(80), fill=INK)
        yr = {"MR. MONEY": "2022", "WORK": "2023", "REAL": "2026", "M$NEY": "2026"}.get(lines[0], "")
        dd.text((size - 50 - dd.textlength(yr, font=MONOB(44)), size - 98), yr, font=MONOB(44), fill=INK)
        m = Image.new("L", (size, size), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], 18, fill=255)
        tile.putalpha(m)
        _cache[key] = tile
    tile = _cache[key]
    p = ease_out(t / 0.9)
    # vinyl peeking out
    vin = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vin)
    vd.ellipse([10, 10, size - 10, size - 10], fill=(12, 12, 12, 255))
    for r in range(40, size // 2 - 20, 14):
        vd.ellipse([size / 2 - r, size / 2 - r, size / 2 + r, size / 2 + r], outline=(34, 34, 34, 255), width=2)
    vd.ellipse([size / 2 - 90, size / 2 - 90, size / 2 + 90, size / 2 + 90], fill=GOLD + (255,))
    vin = vin.rotate(-t * 40, resample=Image.BICUBIC)
    x = OW / 2 - size / 2 - 120 * p + (1 - p) * 300
    y = OH / 2 - size / 2
    base.alpha_composite(vin, (int(x + 240 * p), int(y)))
    shadow = Image.new("RGBA", (size + 120, size + 120), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([60, 70, size + 60, size + 70], 18, fill=(0, 0, 0, 200))
    shadow = shadow.filter(ImageFilter.GaussianBlur(30))
    base.alpha_composite(shadow, (int(x - 60), int(y - 60)))
    put(base, tile, x, y, alpha=clamp(t / 0.4))


def award_card(base, lines, a):
    w, h = 900, 300
    y0 = OH / 2 + 120
    box = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(box)
    bd.rounded_rectangle([0, 0, w - 1, h - 1], 24, fill=(14, 12, 10, int(230 * a)), outline=GOLD + (int(255 * a),), width=3)
    base.alpha_composite(box, (int(OW / 2 - w / 2), int(y0 - h / 2 + (1 - a) * 30)))
    center_word(base, "★", SANS(60, "Bold"), GOLD, y0 - 80, alpha=a, shadow=False)
    center_word(base, lines[0], ANTON(96), GOLD, y0 - 5, alpha=a, shadow=False)
    if len(lines) > 1:
        center_word(base, lines[1], MONOB(40), CREAM, y0 + 85, alpha=a, shadow=False)


def quote_frame(e, sh, k, lt):
    base = base_for(e, k, lt)
    ov = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    ImageDraw.Draw(ov).rectangle([0, 0, OW, OH], fill=(0, 0, 0, 90))
    base.alpha_composite(ov)
    ta = sh["qt"]
    words = sh["text"].split()
    font = SERIF(100)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if d0.textlength(test, font=font) > OW - 420 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    lines.append(cur)
    lh = 124
    y0 = OH / 2 - len(lines) * lh / 2 - 30
    a = appear(lt, ta - 0.2, 0.6)
    center_word(base, "“", SERIF(260), GOLD, y0 - 40, alpha=a, shadow=False)
    per = 0.16
    wi = 0
    for li, ln in enumerate(lines):
        ws = ln.split()
        tw = d0.textlength(ln, font=font)
        x = OW / 2 - tw / 2
        for w in ws:
            aw = appear(lt, ta + wi * per, 0.35)
            if aw > 0:
                lay, pad = word_img(w, font, CREAM)
                put(base, lay, x - pad, y0 + li * lh + 40 - pad + (1 - aw) * 12, aw)
            x += d0.textlength(w + " ", font=font)
            wi += 1
    a2 = appear(lt, ta + wi * per + 0.2)
    center_word(base, "— " + sh["who"], MONO(36), GOLD, y0 + len(lines) * lh + 110, alpha=a2)
    return base


def stat_frame(e, sh, k, lt):
    base = base_for(e, k, lt)
    t = lt - sh["t0"]
    a = appear(lt, sh["t0"] + 0.1, 0.5)
    if sh.get("count", True):
        v = int(sh["value"] * (1 - (1 - clamp((t - 0.15) / 2.2)) ** 4))
        txt = sh["prefix"] + f"{v:,}" + sh["suffix"]
    else:
        txt = sh["prefix"] + str(sh["value"]) + sh["suffix"]
    font = ANTON(250)
    center_word(base, txt, font, GOLD, OH / 2 - 60, alpha=a, scale=(1.0 if sh.get("count", True) else 1.2 - 0.2 * ease_out(t / 0.6)))
    d = ImageDraw.Draw(base)
    lw = 700 * ease_out((t - 0.3) / 0.8)
    d.rectangle([OW / 2 - lw / 2, OH / 2 + 110, OW / 2 + lw / 2, OH / 2 + 114], fill=GOLD)
    lab = sh["label"]
    lf = fit_font(MONOB, lab, OW - 300, 40)
    center_word(base, lab, lf, CREAM, OH / 2 + 175, alpha=appear(lt, sh["t0"] + 0.5))
    return base


def chart_frame(e, sh, k, lt):
    base = base_for(e, k, lt)
    t = lt - sh["t0"]
    rows = sh["rows"]
    center_word(base, sh["title"], MONO(36), GREY, 190, alpha=appear(lt, sh["t0"]))
    n = len(rows)
    for i, (name, pos) in enumerate(rows):
        cx = OW / 2 + (i - (n - 1) / 2) * 720
        a = appear(lt, sh["t0"] + 0.2 + i * 0.6, 0.5)
        if a <= 0:
            continue
        p = ease_out((t - 0.2 - i * 0.6) / 1.6)
        shown = max(pos, int(200 - (200 - pos) * p)) if pos > 1 else pos
        lay, pad = word_img("#" + str(shown), ANTON(260), GOLD)
        put(base, lay, cx - lay.width / 2, OH / 2 - 210 - pad + 40, a)
        lay2, pad2 = word_img(name, MONOB(44), CREAM)
        put(base, lay2, cx - lay2.width / 2, OH / 2 + 160 - pad2, a)
        # ladder: ticks from 200 down to position
        d = ImageDraw.Draw(base)
        x0, x1 = cx - 260, cx + 260
        d.rectangle([x0, OH / 2 + 250, x1, OH / 2 + 254], fill=(80, 74, 66))
        mx = x1 - (x1 - x0) * (1 - shown / 200)
        d.rectangle([x0, OH / 2 + 250, mx, OH / 2 + 254], fill=GOLD)
        d.ellipse([mx - 10, OH / 2 + 242, mx + 10, OH / 2 + 262], fill=GOLD)
    return base


def phone_frame(e, sh, k, lt):
    base = dark_bg(3).convert("RGBA")
    pw, ph = 620, 940
    px, py = OW / 2 - pw / 2, OH / 2 - ph / 2 + 30
    lay = Image.new("RGBA", (pw + 200, ph + 200), (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle([100, 110, pw + 100, ph + 110], 70, fill=(0, 0, 0, 220))
    base.alpha_composite(lay.filter(ImageFilter.GaussianBlur(30)), (int(px - 100), int(py - 100)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([px, py, px + pw, py + ph], 64, fill=(16, 16, 18), outline=(70, 70, 74), width=4)
    d.rounded_rectangle([px + 14, py + 14, px + pw - 14, py + ph - 14], 54, fill=(8, 8, 10))
    d.rounded_rectangle([px + pw / 2 - 70, py + 30, px + pw / 2 + 70, py + 62], 16, fill=(0, 0, 0))
    # header
    d.ellipse([px + pw / 2 - 42, py + 95, px + pw / 2 + 42, py + 179], fill=(60, 58, 54))
    d.text((px + pw / 2, py + 137), "O", font=ANTON(48), fill=CREAM, anchor="mm")
    d.text((px + pw / 2, py + 210), "Olamide", font=SANS(34, "SemiBold"), fill=CREAM, anchor="mm")
    d.line([px + 40, py + 250, px + pw - 40, py + 250], fill=(40, 40, 44), width=2)
    y = py + 290
    for side, txt, when, ta in sh["tl"]:
        a = appear(lt, ta, 0.3)
        if a <= 0:
            continue
        if side == "out":
            bw, bh = 330, 74
            bx = px + pw - 50 - bw
            d.text((px + pw / 2, y + 2), when, font=MONO(22), fill=(110, 106, 100), anchor="mm")
            y += 22
            yy = y + (1 - a) * 20
            d.rounded_rectangle([bx, yy, bx + bw, yy + bh], 30, fill=(int(GOLD[0] * a), int(GOLD[1] * a), int(GOLD[2] * a)))
            for j, lw in enumerate((0.78, 0.5)):          # unreadable text: we do not know the words
                d.rounded_rectangle([bx + 26, yy + 18 + j * 22, bx + 26 + (bw - 52) * lw, yy + 30 + j * 22], 6, fill=(150, 112, 40))
            d.text((bx + bw, yy + bh + 16), "Delivered", font=SANS(20, "Medium"), fill=(120, 116, 110), anchor="rm")
            y += bh + 44
        else:
            font = SANS(36, "Medium")
            tw = d.textlength(txt, font=font)
            bw, bh = tw + 60, 80
            bx = px + 50
            d.text((px + pw / 2, y + 2), when, font=MONO(22), fill=(110, 106, 100), anchor="mm")
            y += 22
            yy = y + (1 - a) * 20
            d.rounded_rectangle([bx, yy, bx + bw, yy + bh], 30, fill=(58, 58, 62))
            d.text((bx + 30, yy + bh / 2), txt, font=font, fill=(255, 255, 255), anchor="lm")
            y += bh + 40
    d.text((OW - 60, OH - 50), "RECONSTRUCTION  ·  AS DESCRIBED BY ASAKE", font=MONO(22), fill=(120, 116, 110), anchor="rm")
    return base


def names_frame(e, sh, k, lt):
    base = Image.new("RGBA", (OW, OH), (6, 6, 7, 255))
    # candle glow
    t = lt
    fl = 0.85 + 0.15 * math.sin(t * 9.0) * math.sin(t * 3.3)
    glow = Image.new("L", (OW, OH), 0)
    ImageDraw.Draw(glow).ellipse([OW / 2 - 300, OH - 420, OW / 2 + 300, OH + 180], fill=int(70 * fl))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    base.paste((255, 180, 90, 255), (0, 0), glow)
    for i, (nm, age) in enumerate(sh["names"]):
        a = appear(lt, 0.8 + i * 2.2, 1.2)
        center_word(base, nm, SERIF(100), CREAM, OH / 2 - 160 + i * 220, alpha=a)
        center_word(base, age, MONO(34), GREY, OH / 2 - 75 + i * 220, alpha=a)
    center_word(base, "Rest in peace.", SERIFI(52), GOLD, OH - 150, alpha=appear(lt, 6.0, 1.5))
    return base


def end_frame(e, sh, k, lt):
    base = dark_bg(4).convert("RGBA")
    a = appear(lt, 0.3, 0.8)
    logo = os.path.join(os.path.dirname(HERE), "channel_logo.png")
    if os.path.exists(logo):
        L = Image.open(logo).convert("RGBA")
        L.thumbnail((260, 260))
        put(base, L, OW / 2 - L.width / 2, 170, a)
    center_word(base, "SUBSCRIBE TO NAIJA UNTOLD", ANTON(110), CREAM, OH / 2 + 30, alpha=a)
    center_word(base, "Which Asake song found you when you needed it?", SERIFI(58), GOLD, OH / 2 + 160, alpha=appear(lt, 2.5, 0.8))
    center_word(base, "Tell us in the comments  ↓", MONO(36), GREY, OH / 2 + 250, alpha=appear(lt, 4.0, 0.8))
    return base


# ------------------------------------------------------------------ scene-level cards
def card_frame(e, lt):
    c = e["card"]
    base = dark_bg(7, (20, 18, 17)).convert("RGBA")
    col = {"gold": GOLD, "red": RED, "white": CREAM}[c["color"]]
    word = c["word"]
    a = appear(lt, 0.15, 0.25)
    flick = 1.0 if lt > 0.6 else (0.3 + 0.7 * (math.sin(lt * 80) > -0.2))
    font = fit_font(ANTON, word, OW - 240, 330)
    sc_ = 1.08 - 0.08 * ease_out((lt - 0.15) / 2.5)
    center_word(base, word, font, col, OH / 2 - 40, alpha=a * flick, scale=sc_, distress=hash(word) % 1000 + 3, spacing=8)
    d = ImageDraw.Draw(base)
    lw = 520 * ease_out((lt - 0.5) / 0.8)
    d.rectangle([OW / 2 - lw / 2, OH / 2 + 150, OW / 2 + lw / 2, OH / 2 + 153], fill=col)
    sub = c["sub"]
    nch = int(len(sub) * clamp((lt - 0.7) / 0.9))
    center_word(base, sub[:nch] if nch else " ", MONO(40), CREAM, OH / 2 + 205, alpha=1.0)
    num = [x["id"] for x in TL if x.get("card")].index(e["id"]) + 1
    center_word(base, f"CHAPTER {num:02d}", MONO(28), GREY, OH / 2 - 260, alpha=appear(lt, 0.4))
    return base


def logo_frame(e, lt):
    base = dark_bg(9, (18, 15, 12)).convert("RGBA")
    a = appear(lt, 0.3, 1.0)
    # MM monogram
    mm = word_img("MM", ANTON(300), GOLD, distress=91, spacing=-30)[0]
    put(base, mm, OW / 2 - mm.width / 2, OH / 2 - 400 + (1 - a) * 30, a * 0.9, scale=1.05 - 0.05 * a)
    a2 = appear(lt, 1.0, 0.9)
    center_word(base, "MR MONEY", ANTON(200), CREAM, OH / 2 + 90, alpha=a2, spacing=int(40 * (1 - a2)) + 14, distress=93)
    center_word(base, "THE ASAKE STORY", MONOB(46), GOLD, OH / 2 + 230, alpha=appear(lt, 1.8))
    center_word(base, "A NAIJA UNTOLD DOCUMENTARY", MONO(28), GREY, OH - 90, alpha=appear(lt, 2.4))
    # light sweep across the title
    sw = (lt - 1.6) / 1.4
    if 0 < sw < 1:
        ov = Image.new("L", (OW, OH), 0)
        x = -300 + (OW + 600) * sw
        ImageDraw.Draw(ov).polygon([(x, 0), (x + 120, 0), (x - 180, OH), (x - 300, OH)], fill=70)
        ov = ov.filter(ImageFilter.GaussianBlur(40))
        base.paste((255, 230, 170, 255), (0, 0), ov)
    return base


# ------------------------------------------------------------------ overlays
def tag_layer(text):
    key = ("tag", text)
    if key not in _cache:
        f = MONO(34)
        d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
        tw = int(d0.textlength(text, font=f))
        lay = Image.new("RGBA", (tw + 80, 90), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        dd.rectangle([0, 18, 5, 72], fill=GOLD)
        dd.text((24, 24), text, font=f, fill=(0, 0, 0, 160))
        dd.text((22, 22), text, font=f, fill=CREAM)
        _cache[key] = lay
    return _cache[key]


def credit_layer(text):
    key = ("cr", text)
    if key not in _cache:
        f = SANS(20, "Regular")
        d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
        tw = int(d0.textlength(text, font=f))
        lay = Image.new("RGBA", (tw + 20, 34), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((10, 6), text, font=f, fill=(220, 214, 200, 150))
        _cache[key] = lay
    return _cache[key]


SHOW = [("three hundred and thirty million", "330 million")]


def show(s):
    return s.replace("M$NEY", "M$NEY")


def sub_layer(s):
    key = ("sub", s)
    if key not in _cache:
        f = SANS(44, "SemiBold")
        d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
        tw = d0.textlength(s, font=f)
        if tw > OW - 260:
            f = SANS(int(44 * (OW - 260) / tw), "SemiBold")
            tw = d0.textlength(s, font=f)
        W, H = int(tw) + 60, 80
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        dd.rounded_rectangle([0, 6, W - 1, H - 6], 14, fill=(0, 0, 0, 120))
        dd.text((30, H / 2), s, font=f, fill=(255, 255, 255), anchor="lm")
        _cache[key] = lay
    return _cache[key]


def vignette():
    if "vig" not in _cache:
        yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
        r = np.sqrt(((xx - OW / 2) / (OW * 0.62)) ** 2 + ((yy - OH / 2) / (OH * 0.62)) ** 2)
        _cache["vig"] = np.clip(1.0 - 0.42 * np.clip(r - 0.55, 0, 1) ** 1.6, 0.45, 1.0)[..., None]
    return _cache["vig"]


def grain(i):
    k = ("grain", i % 12)
    if k not in _cache:
        r = np.random.default_rng(1000 + i % 12)
        g = r.normal(0, 7.5, (OH // 2, OW // 2)).astype(np.float32)
        g = np.asarray(Image.fromarray(g + 128).resize((OW, OH), Image.BILINEAR), np.float32) - 128
        _cache[k] = g[..., None]
    return _cache[k]


# ------------------------------------------------------------------ frame assembly
RENDER = {"kin": kin_frame, "quote": quote_frame, "stat": stat_frame, "chart": chart_frame, "phone": phone_frame,
          "names": names_frame, "end": end_frame}


def shot_frame(e, k, lt):
    sh = e["shots"][k]
    if sh["kind"] == "photo":
        im = photo_frame(sh, lt).convert("RGBA")
        if sh.get("tag"):
            a = appear(lt, sh["t0"] + 0.5, 0.6) * (1 - appear(lt, sh["t1"] - 0.6, 0.5))
            put(im, tag_layer(sh["tag"]), 70, 70, a)
        if sh.get("credit"):
            cl = credit_layer(sh["credit"])
            put(im, cl, OW - cl.width - 24, OH - 40, 1.0)
        return im
    return RENDER[sh["kind"]](e, sh, k, lt)


def scene_frame(e, lt):
    if e.get("card"):
        return card_frame(e, lt)
    if e.get("logo"):
        return logo_frame(e, lt)
    shots = e["shots"]
    k = max([i for i, s in enumerate(shots) if s["t0"] <= lt] or [0])
    cur = shot_frame(e, k, lt)
    if k > 0 and lt - shots[k]["t0"] < XF_SHOT:
        prev = shot_frame(e, k - 1, lt)
        cur = Image.blend(prev, cur, smooth((lt - shots[k]["t0"]) / XF_SHOT))
    return cur


def frame_at(i):
    t = i / FPS
    act = [e for e in TL if e["start"] - 1e-6 <= t < e["end"]]
    if not act:
        act = [TL[-1]]
    e = act[-1]
    img = scene_frame(e, t - e["start"])
    if len(act) > 1 and t - e["start"] < e["xf"]:
        p = act[-2]
        img = Image.blend(scene_frame(p, t - p["start"]), img, smooth((t - e["start"]) / e["xf"]))
    img = img.convert("RGBA")
    if not NOSUBS:
        for a0, a1, s in e.get("subs") or []:
            if a0 - 0.05 <= t - e["start"] < a1 + 0.02:
                L = sub_layer(show(s))
                img.alpha_composite(L, (int(OW / 2 - L.width / 2), OH - 150))
                break
    a = np.asarray(img.convert("RGB"), np.float32)
    a = a * vignette() + grain(i)
    # gentle fade from/to black at the very start and end
    fade = min(1.0, t / 0.8, max(0.0, (TOTAL - t) / 1.5))
    a *= fade
    return np.clip(a, 0, 255).astype(np.uint8).tobytes()


def render_range(args):
    a, b, path = args
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", path],
                           stdin=subprocess.PIPE)
    for i in range(a, b):
        enc.stdin.write(frame_at(i))
    enc.stdin.close()
    enc.wait()
    return path


def main():
    out = sys.argv[2]
    t0 = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    t1 = float(sys.argv[4]) if len(sys.argv) > 4 else TOTAL
    json.dump(TL, open(os.path.join(BUILD, "timeline.json"), "w"), indent=0, default=str)
    n0, n1 = int(t0 * FPS), int(t1 * FPS)
    parts, step = [], 300
    for a in range(n0, n1, step):
        parts.append((a, min(a + step, n1), os.path.join(BUILD, f"part_{a:06d}.mp4")))
    todo = [x for x in parts if not (os.path.exists(x[2]) and os.path.getsize(x[2]) > 1000 and x[1] - x[0] == 300)]
    with Pool(int(os.environ.get("JOBS", "4"))) as p:
        for i, _ in enumerate(p.imap(render_range, todo)):
            print(f"\r{i + 1}/{len(parts)}", end="", flush=True)
    lst = os.path.join(BUILD, "parts.txt")
    open(lst, "w").write("".join(f"file '{os.path.abspath(x[2])}'\n" for x in parts))
    subprocess.check_call(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out])
    print("\npicture done", round(TOTAL, 1), "s")


if __name__ == "__main__":
    main()
