"""JUNE 12 picture engine: everything on screen is a real photo, real footage, or a real object
(photo prints and newspapers on a wooden desk, typewriter pages, rubber stamps, a result sheet).

usage (from documentary/):  python3 june12/engine12.py BUILD_DIR OUT.mp4 [start_sec end_sec]
"""
import hashlib, json, math, os, subprocess, sys, zlib
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from script12 import S

OW, OH, FPS = 1280, 720, 30
BW, BH = 1600, 900            # working canvas for every shot (room for camera moves)
XF_SHOT, XF_SCENE = 0.55, 0.7
LEAD = 0.55
TEX = os.path.join(HERE, "textures")
FONTS = os.path.join(HERE, "fonts")
INTER = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
GOLD, CREAM, INK, RED = (214, 172, 84), (244, 236, 220), (28, 26, 30), (176, 28, 30)


def font(name, size, var=None):
    f = ImageFont.truetype(name if name.startswith("/") else os.path.join(FONTS, name), size)
    if var:
        try:
            f.set_variation_by_name(var)
        except Exception:
            pass
    return f


TYPE = lambda s: font("SpecialElite-Regular.ttf", s)
SERIF = lambda s, v="Bold": font("PlayfairDisplay-VF.ttf", s, v)
STAMP = lambda s: font("Oswald-VF.ttf", s, "Bold")
SANS = lambda s, w="SemiBold": font(INTER.format(w), s)

# words heard in the archive clips (relative to the clip's in-point)
CLIPSUBS = {
    "c0_ibb": [(0.15, 4.4, "It is true that the presidential election was generally seen"),
               (4.4, 8.4, "to be free, fair and peaceful.")],
    "c4_ibb": [(0.2, 4.4, "However, there was in fact a huge array of electoral malpractices"),
               (4.4, 9.0, "virtually in all the states of the Federation before the actual voting began.")],
    "c4_mko": [(0.2, 4.6, "In view of all this, I have found the conclusion unfortunate"),
               (4.6, 11.0, "but inescapable, that the federal government is guilty of bad faith, pure and simple."),
               (11.5, 17.2, "No one has accused me of any offence against any known electoral law or regulation."),
               (17.5, 21.8, "The people of this country went to the polls on Saturday, June 12, 1993,"),
               (21.8, 25.7, "and without let or hindrance, chose me as their president.")],
    "c7_burial": [(0.3, 5.4, "After four years in detention, Chief MKO Abiola finally came home on Saturday."),
                  (5.8, 10.8, "But instead of the hero's welcome his supporters had hoped to give him when this day arrived,"),
                  (11.0, 14.9, "Chief Abiola was making this final journey in a coffin."),
                  (15.2, 22.1, "It was an emotional moment for his family and the small crowd of followers who were waiting to receive the body in the early morning."),
                  (22.4, 24.6, "For some, it was just too much.")],
}


def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


# ------------------------------------------------------------------ timeline
def at_time(at, sents):
    if isinstance(at, tuple):
        i, fr = at
    else:
        i, fr = at, 0.0
    i = min(i, len(sents) - 1)
    a, b = sents[i]
    return a + (b - a) * fr


def build(timing_path):
    timing = json.load(open(timing_path)) if os.path.exists(timing_path) else {}
    out, t = [], 0.0
    for sc in S:
        e = dict(sc)
        if sc.get("clip"):
            e["dur"] = sc["clip"][2] - sc["clip"][1]
            xf = 0.35
        elif sc.get("logo"):
            e["dur"], xf = 6.2, XF_SCENE
        elif sc.get("card"):
            e["dur"], xf = 3.4, XF_SCENE
        else:
            v = timing.get(sc["id"])
            vd = v["dur"] if v else 3.0
            e["dur"] = LEAD + vd + sc.get("hold", 0.9)
            e["voice_at"] = LEAD
            e["subs"] = [[LEAD + a, LEAD + b, s] for a, b, s in (v["subs"] if v else [])]
            e["sents"] = [[LEAD + a, LEAD + b] for a, b in (v["sents"] if v else [[0, vd]])]
            xf = XF_SCENE
        e["start"] = max(0.0, t - (xf if out else 0.0))
        e["xf"] = xf if out else 0.0
        e["end"] = e["start"] + e["dur"]
        if sc.get("clip"):
            e["subs"] = [[a, b, s] for a, b, s in CLIPSUBS.get(sc["id"], [])]
        shots = []
        for k, sh in enumerate(sc.get("shots") or []):
            s0 = 0.0 if k == 0 else max(0.0, at_time(sh["at"], e["sents"]) - 0.2)
            shots.append(dict(sh, t0=s0))
        for k, sh in enumerate(shots):
            sh["t1"] = shots[k + 1]["t0"] if k + 1 < len(shots) else e["dur"]
            if sh["kind"] == "typed":  # line appearance times
                lines = [l if isinstance(l, tuple) else (l, None) for l in sh["lines"]]
                tl, cur = [], sh["t0"] + 0.35
                for txt, a in lines:
                    if a is not None:
                        cur = max(cur, at_time(a, e["sents"]) - 0.1, sh["t0"] + 0.35)
                    cps = 11.0 if sh.get("big") else 19.0
                    body = txt.lstrip("~!")
                    dur = 0.18 if txt.startswith("!") else len(body) / cps
                    tl.append(dict(text=body, strike=txt.startswith("~"), stamp=txt.startswith("!"), t=cur, d=dur))
                    cur += dur + (0.1 if txt else 0.0)
                sh["tl"] = tl
        e["shots"] = shots
        out.append(e)
        t = e["end"]
    return out, t


# ------------------------------------------------------------------ material: desk, prints, papers
_cache = {}


def desk(seed=0, dark=False):
    k = ("desk", seed % 4, dark)
    if k not in _cache:
        w = Image.open(os.path.join(TEX, "Wood051.jpg" if dark else "Wood066.jpg")).convert("RGB")
        w = ImageOps.fit(w.rotate(90 * (seed % 2), expand=True), (BW, BH), Image.LANCZOS,
                         centering=((seed * 0.37) % 1, (seed * 0.61) % 1))
        a = np.asarray(w).astype(np.float32)
        yy, xx = np.mgrid[0:BH, 0:BW]
        # warm desk lamp from the upper left, falling off to the corners
        d = np.sqrt(((xx - BW * 0.38) / (BW * 0.75)) ** 2 + ((yy - BH * 0.32) / (BH * 0.85)) ** 2)
        light = np.clip(1.15 - d * 0.75, 0.32, 1.15)[..., None]
        a = a * light * np.array([1.05, 0.97, 0.86], np.float32) * (0.72 if dark else 0.85)
        _cache[k] = np.clip(a, 0, 255).astype(np.uint8)
    return Image.fromarray(_cache[k])


def grade(img, mode=None):
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    if mode == "bw":
        a = lum[..., None] * np.array([1.04, 0.98, 0.88], np.float32)
    else:
        a = a * 0.86 + lum[..., None] * 0.14
    a = (a - 128) * 1.05 + 126
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def shadowed(rgba, blur=18, off=(10, 16), opacity=0.55):
    """Return an RGBA canvas with a soft drop shadow under the object."""
    pad = blur * 3
    W, H = rgba.width + pad * 2, rgba.height + pad * 2
    sh = Image.new("L", (W, H), 0)
    sh.paste(rgba.split()[3].point(lambda v: int(v * opacity)), (pad + off[0], pad + off[1]))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.putalpha(sh)
    out.alpha_composite(rgba, (pad, pad))
    return out, pad


def as_print(src, max_w, max_h, border=0.035, old=False, seed=0):
    sc = min(max_w / src.width, max_h / src.height)
    ph = src.resize((max(1, int(src.width * sc)), max(1, int(src.height * sc))), Image.LANCZOS)
    ph = ph.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    b = int(max(ph.size) * border)
    col = (236, 226, 204) if old else (246, 243, 236)
    card = Image.new("RGBA", (ph.width + 2 * b, ph.height + 2 * b), col + (255,))
    card.paste(ph, (b, b))
    ang = ((zlib.crc32(str(seed).encode()) % 400) / 100.0 - 2.0)
    return card.rotate(ang, resample=Image.BICUBIC, expand=True), ang


def place_on_desk(obj, seed, dark=False, shadow=(18, (10, 16), 0.55)):
    base = desk(seed, dark).convert("RGBA")
    s, pad = shadowed(obj, *shadow)
    x, y = (BW - s.width) // 2, (BH - s.height) // 2
    base.alpha_composite(s, (x, y))
    return base.convert("RGB"), (x + pad, y + pad)


def prep_photo(sh, seed):
    src = Image.open(sh["file"]).convert("RGB")
    g = grade(src, sh.get("grade"))
    asp = src.width / src.height
    if src.width >= 560 and 1.25 <= asp <= 2.2:
        im = ImageOps.fit(g, (BW, BH), Image.LANCZOS, centering=sh["focus"])
        im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=50, threshold=2))
        # where the focus point lands on the canvas
        sc = max(BW / src.width, BH / src.height)
        cw, ch = src.width * sc, src.height * sc
        ox, oy = (cw - BW) * sh["focus"][0], (ch - BH) * sh["focus"][1]
        fx, fy = sh["focus"][0] * cw - ox, sh["focus"][1] * ch - oy
        return im, (fx, fy)
    card, ang = as_print(g, 1180, 760, old=sh.get("grade") == "bw" or src.width < 700, seed=seed)
    im, (x, y) = place_on_desk(card, seed)
    fx, fy = x + card.width * sh["focus"][0], y + card.height * sh["focus"][1]
    return im, (fx, fy)


def prep_paper(sh, seed):
    src = Image.open(sh["file"]).convert("RGB")
    g = grade(src)
    sc = min(1300 / g.width, 820 / g.height)
    pg = g.resize((int(g.width * sc), int(g.height * sc)), Image.LANCZOS)
    pg = pg.filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=2)).convert("RGBA")
    ang = ((zlib.crc32(sh["file"].encode()) % 300) / 100.0 - 1.5)
    pg = pg.rotate(ang, resample=Image.BICUBIC, expand=True)
    s, pad = shadowed(pg, 22, (12, 20), 0.6)
    bg = desk(seed + 1, dark=True)
    x, y = (BW - s.width) // 2, (BH - s.height) // 2
    fx, fy = x + pad + pg.width * sh["focus"][0], y + pad + pg.height * sh["focus"][1]
    return bg, s, (x, y), (fx, fy)


def paper_sheet(seed, kind="Paper001"):
    k = ("sheet", seed, kind)
    if k not in _cache:
        p = Image.open(os.path.join(TEX, kind + ".jpg")).convert("RGB")
        p = ImageOps.fit(p, (1240, 820), Image.LANCZOS)
        a = np.asarray(p).astype(np.float32)
        a = a * np.array([1.0, 0.965, 0.88], np.float32) * 0.97      # aged, warm
        yy, xx = np.mgrid[0:820, 0:1240]
        edge = np.minimum(np.minimum(xx, 1239 - xx), np.minimum(yy, 819 - yy))
        a *= (0.86 + 0.14 * np.clip(edge / 90.0, 0, 1))[..., None]      # darker, handled edges
        sheet = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
        ang = ((zlib.crc32(str(seed).encode()) % 240) / 100.0 - 1.2)
        sheet = sheet.rotate(ang, resample=Image.BICUBIC, expand=True)
        base, (x, y) = place_on_desk(sheet, seed, dark=True, shadow=(16, (8, 14), 0.5))
        _cache[k] = (base, (x + (sheet.width - 1240) // 2, y + (sheet.height - 820) // 2), ang)
    return _cache[k]


# ------------------------------------------------------------------ typewriter & stamps
def type_layer(sh, lt, scene_id):
    """Draw the typed lines (up to time lt) onto the paper. Returns RGB canvas."""
    seed = zlib.crc32(scene_id.encode()) % 997
    base, (px, py), ang = paper_sheet(seed)
    img = base.copy()
    lay = Image.new("RGBA", (1240, 820), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    big = sh.get("big")
    f = TYPE(92 if big else 58)
    lh = 112 if big else 82
    lines = sh["tl"]
    n = len(lines)
    y0 = 410 - (n * lh) / 2 + lh / 2
    rng = np.random.default_rng(seed)
    jit = rng.normal(0, 1.0, (n, 80, 3))
    for i, ln in enumerate(lines):
        y = y0 + i * lh
        if lt < ln["t"]:
            continue
        txt = ln["text"]
        if ln["stamp"]:
            continue
        nchar = len(txt) if lt >= ln["t"] + ln["d"] else int(len(txt) * (lt - ln["t"]) / max(ln["d"], 1e-3))
        tw = d.textlength(txt, font=f)
        lim = 1080 if big else 1010
        if tw > lim:  # shrink only this line so it stays on the page
            fsz = int((92 if big else 58) * lim / tw)
            if ("tf", fsz) not in _cache:
                _cache[("tf", fsz)] = TYPE(fsz)
            f_line = _cache[("tf", fsz)]
            tw = d.textlength(txt, font=f_line)
        else:
            f_line = f
        x = 620 - tw / 2 if big else 110
        for c in range(nchar):
            ch = txt[c]
            cw = d.textlength(ch, font=f_line)
            j = jit[i, c % 80]
            inkv = int(26 + abs(j[2]) * 18)
            d.text((x + j[0] * 0.8, y + j[1] * 0.8), ch, font=f_line, fill=(inkv, inkv - 2, inkv + 4, int(232 - abs(j[2]) * 30)), anchor="lm")
            x += cw
        if ln["strike"] and lt > ln["t"] + ln["d"] + 0.15:
            p = smooth((lt - ln["t"] - ln["d"] - 0.15) / 0.35)
            xs = 620 - tw / 2 if big else 110
            d.line([xs - 6, y + 2, xs - 6 + (tw + 12) * p, y - 1], fill=RED + (225,), width=5)
    lay = lay.filter(ImageFilter.GaussianBlur(0.45))
    # rubber stamps on top
    for i, ln in enumerate(lines):
        if not ln["stamp"] or lt < ln["t"]:
            continue
        st = stamp_img(ln["text"], seed + i)
        k = lt - ln["t"]
        sc = 1.0 + 0.35 * math.exp(-k * 22)
        if sc > 1.01:
            st = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
        y = y0 + i * lh
        lay.alpha_composite(st, (int(620 - st.width / 2), int(y - st.height / 2)))
    lay = lay.rotate(ang, resample=Image.BICUBIC)
    img = img.convert("RGBA")
    img.alpha_composite(lay, (px, py))
    return img.convert("RGB")


def stamp_img(text, seed):
    k = ("stamp", text)
    if k not in _cache:
        f = STAMP(92)
        tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
        tw = int(tmp.textlength(text, font=f))
        w, h = tw + 80, 150
        m = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(m)
        d.rectangle([6, 6, w - 7, h - 7], outline=255, width=9)
        d.text((w / 2, h / 2 + 2), text, font=f, fill=255, anchor="mm")
        rng = np.random.default_rng(seed)
        noise = rng.random((h, w))
        blot = np.asarray(Image.fromarray((rng.random((h // 6 + 1, w // 6 + 1)) * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR)) / 255
        a = np.asarray(m).astype(np.float32) / 255 * (noise > 0.18) * np.clip(0.55 + blot * 0.7, 0, 1)
        rgba = np.zeros((h, w, 4), np.uint8)
        rgba[..., 0], rgba[..., 1], rgba[..., 2] = RED
        rgba[..., 3] = (a * 225).astype(np.uint8)
        im = Image.fromarray(rgba).rotate(-6 + (seed % 5), resample=Image.BICUBIC, expand=True)
        _cache[k] = im
    return _cache[k]


def tally_layer(sh, lt, e):
    seed = 41
    base, (px, py), ang = paper_sheet(seed, "Paper003")
    img = base.convert("RGBA")
    lay = Image.new("RGBA", (1240, 820), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    fh, fb, fs = TYPE(34), TYPE(46), TYPE(30)
    ink = (34, 32, 38, 235)
    d.text((620, 70), "FEDERAL REPUBLIC OF NIGERIA", font=fh, fill=ink, anchor="mm")
    d.text((620, 118), "PRESIDENTIAL ELECTION  ·  12 JUNE 1993", font=fh, fill=ink, anchor="mm")
    d.text((620, 162), "RESULTS (UNOFFICIAL, AS REPORTED)", font=fs, fill=(60, 58, 64, 220), anchor="mm")
    d.line([110, 196, 1130, 196], fill=ink, width=3)
    s1 = e["sents"]
    p = smooth((lt - 0.6) / 6.5)
    rows = [("M.K.O. ABIOLA  (SDP)", 8341309, 58.4), ("BASHIR TOFA  (NRC)", 5952087, 41.6)]
    for i, (nm, v, pc) in enumerate(rows):
        y = 290 + i * 150
        d.text((120, y), nm, font=fb, fill=ink, anchor="lm")
        cur = int(v * p)
        d.text((1120, y), f"{cur:,}", font=fb, fill=ink, anchor="rm")
        bw = 980 * (pc / 100) * p
        d.rectangle([120, y + 42, 120 + bw, y + 58], fill=(70, 120, 70, 200) if i == 0 else (90, 90, 100, 190))
        if p > 0.98:
            d.text((120 + bw + 14, y + 50), f"{pc}%", font=fs, fill=ink, anchor="lm")
    t_states = s1[2][0] if len(s1) > 2 else 99
    if lt > t_states:
        q = smooth((lt - t_states) / 0.8)
        d.text((120, 610), "STATES WON:  ABIOLA 19 + FCT   ·   TOFA 11", font=fs, fill=ink[:3] + (int(235 * q),), anchor="lm")
    lay = lay.filter(ImageFilter.GaussianBlur(0.4))
    t_kano = s1[3][0] if len(s1) > 3 else 99
    if lt > t_kano:
        st = stamp_img("KANO: ABIOLA", 7)
        k = lt - t_kano
        sc = 1.0 + 0.35 * math.exp(-k * 22)
        st2 = st.resize((int(st.width * sc * 0.8), int(st.height * sc * 0.8)), Image.BILINEAR)
        lay.alpha_composite(st2, (int(860 - st2.width / 2), int(720 - st2.height / 2)))
    img.alpha_composite(lay.rotate(ang, resample=Image.BICUBIC), (px, py))
    return img.convert("RGB")


def chapter_canvas(e, lt):
    seed = zlib.crc32(e["id"].encode()) % 97
    base, (px, py), ang = paper_sheet(seed, "Paper006")
    lay = Image.new("RGBA", (1240, 820), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    kicker, name = e["card"]
    d.text((620, 300), kicker, font=TYPE(40), fill=(40, 34, 30, 220), anchor="mm")
    p = smooth((lt - 0.4) / 1.4)
    f = SERIF(96 if len(name) < 16 else 70)
    n = int(len(name) * p)
    d.text((620, 430), name[:n], font=f, fill=(24, 20, 18, 240), anchor="mm") if n else None
    tw = d.textlength(name, font=f)
    lw = tw / 2 * smooth((lt - 1.4) / 0.8)
    d.line([620 - lw, 510, 620 + lw, 510], fill=(120, 30, 28, 220), width=4)
    img = base.convert("RGBA")
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.4)).rotate(ang, resample=Image.BICUBIC), (px, py))
    return img.convert("RGB")


def logo_canvas(lt):
    """Archive-reel opening: the emblem on cream paper under a flickering projector, then the title."""
    base, (px, py), ang = paper_sheet(5, "Paper001")
    img = base.convert("RGBA")
    lay = Image.new("RGBA", (1240, 820), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if lt < 2.9:
        if "logo" not in _cache:
            lg = Image.open(os.path.join(os.path.dirname(HERE), "channel_logo.png")).convert("RGBA").resize((430, 430), Image.LANCZOS)
            a = np.asarray(lg).astype(np.float32)
            dark = (a[..., :3].mean(-1) < 22)
            a[..., 3] = np.where(dark, 0, a[..., 3])          # print only the emblem, not the black square
            _cache["logo"] = Image.fromarray(a.astype(np.uint8))
        q = smooth((lt - 0.3) / 0.9)
        lg = _cache["logo"].copy()
        lg.putalpha(lg.split()[3].point(lambda v: int(v * q)))
        lay.alpha_composite(lg, (620 - 215, 330 - 215))
        d.text((620, 640), "N A I J A   U N T O L D   P R E S E N T S", font=TYPE(34), fill=(40, 34, 30, int(220 * smooth((lt - 1.1) / 0.6))), anchor="mm")
    else:
        k = lt - 2.9
        d.text((620, 300), "JUNE 12", font=SERIF(150, "Black"), fill=(22, 18, 16, int(245 * smooth(k / 0.5))), anchor="mm")
        sub = "THE ELECTION NIGERIA STOLE"
        n = int(len(sub) * smooth((k - 0.4) / 1.3))
        d.text((620, 450), sub[:n], font=TYPE(50), fill=(30, 28, 30, 235), anchor="mm")
        if k > 2.0:
            st = stamp_img("ANNULLED", 3)
            sc = 1.0 + 0.4 * math.exp(-(k - 2.0) * 22)
            st = st.resize((int(st.width * sc * 0.95), int(st.height * sc * 0.95)), Image.BILINEAR)
            lay.alpha_composite(st, (int(860 - st.width / 2), int(600 - st.height / 2)))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.35)).rotate(ang, resample=Image.BICUBIC), (px, py))
    a = camera(img.convert("RGB"), 1.0 + 0.05 * smooth(lt / 6.2), BW / 2, BH / 2)
    rng = np.random.default_rng(int(lt * FPS))
    a *= (0.9 + 0.12 * rng.random()) * smooth(lt / 0.5)            # projector flicker, fade up
    return a


def endcard_canvas(lt):
    if "endcard" not in _cache:
        base = desk(9, dark=True).convert("RGBA")
        th = Image.open(os.path.join(os.path.dirname(HERE), "thumbnail.jpg")).convert("RGB")
        card, _ = as_print(th, 900, 506, border=0.03, seed=3)
        s, pad = shadowed(card, 18, (10, 16), 0.6)
        base.alpha_composite(s, (BW // 2 - s.width // 2 + 160, BH // 2 - s.height // 2 + 40))
        lg = Image.open(os.path.join(os.path.dirname(HERE), "channel_logo.png")).convert("RGBA").resize((260, 260), Image.LANCZOS)
        m = Image.new("L", lg.size, 0)
        ImageDraw.Draw(m).ellipse([6, 6, 254, 254], fill=255)
        lg.putalpha(m)
        s2, p2 = shadowed(lg, 12, (6, 10), 0.6)
        base.alpha_composite(s2, (150, 300))
        d = ImageDraw.Draw(base)
        d.text((290, 640), "SUBSCRIBE", font=SANS(44, "Bold"), fill=CREAM + (255,), anchor="mm")
        d.text((BW // 2 + 160, 150), "WATCH NEXT:  JAGABAN", font=SANS(46, "Bold"), fill=CREAM + (255,), anchor="mm")
        _cache["endcard"] = base.convert("RGB")
    return _cache["endcard"]


# ------------------------------------------------------------------ camera
def camera(img, z, cx, cy, out=(OW, OH)):
    s = (BW / OW) / z * (OW / out[0])
    hw, hh = out[0] * s / 2, out[1] * s / 2
    cx = min(max(cx, hw), img.width - hw)
    cy = min(max(cy, hh), img.height - hh)
    return np.asarray(img.transform(out, Image.AFFINE, (s, 0, cx - hw, 0, s, cy - hh), resample=Image.BICUBIC)).astype(np.float32)


def move_params(sh, p, focus):
    fx, fy = focus
    m = sh.get("move", "in")
    if m == "in":
        k = smooth(p) * 0.65 + p * 0.35
        return 1.0 + 0.13 * k, BW / 2 + (fx - BW / 2) * k * 0.8, BH / 2 + (fy - BH / 2) * k * 0.8
    if m == "out":
        k = 1 - (smooth(p) * 0.65 + p * 0.35)
        return 1.0 + 0.13 * k, BW / 2 + (fx - BW / 2) * k * 0.8, BH / 2 + (fy - BH / 2) * k * 0.8
    d = -1 if m == "left" else 1
    return 1.1, BW / 2 + d * (p - 0.5) * 150, BH / 2 + (fy - BH / 2) * 0.3


def plate_path(build, key):
    return os.path.join(build, "plates", hashlib.md5(key.encode()).hexdigest()[:16] + ".png")


def cached(build, key, fn):
    if key not in _cache:
        p = plate_path(build, key)
        if not os.path.exists(p):
            res = fn()
            res.save(p + ".tmp.png")
            os.replace(p + ".tmp.png", p)
        _cache[key] = Image.open(p).convert("RGB" if not key.startswith("paperobj") else "RGBA")
    return _cache[key]


def focus_of(build, sh, seed):
    k = ("focus", sh["file"], sh["kind"], seed)
    if k not in _cache:
        fp = plate_path(build, f"{sh['kind']}|{sh['file']}|{seed}|{sh['focus']}|{sh.get('grade')}") + ".json"
        if not os.path.exists(fp):
            prep_shot(build, sh, seed)
        _cache[k] = json.load(open(fp))
    return _cache[k]


def prep_shot(build, sh, seed):
    key = f"{sh['kind']}|{sh['file']}|{seed}|{sh['focus']}|{sh.get('grade')}"
    fp = plate_path(build, key) + ".json"
    if sh["kind"] == "photo":
        im, foc = prep_photo(sh, seed)
        im.save(plate_path(build, key) + ".tmp.png")
        os.replace(plate_path(build, key) + ".tmp.png", plate_path(build, key))
        json.dump(dict(focus=foc), open(fp, "w"))
    elif sh["kind"] == "paper":
        bg, obj, pos, foc = prep_paper(sh, seed)
        bg.save(plate_path(build, key) + ".tmp.png")
        os.replace(plate_path(build, key) + ".tmp.png", plate_path(build, key))
        obj.save(plate_path(build, "paperobj" + key) + ".tmp.png")
        os.replace(plate_path(build, "paperobj" + key) + ".tmp.png", plate_path(build, "paperobj" + key))
        json.dump(dict(focus=foc, pos=pos), open(fp, "w"))


def shot_frame(build, e, sh, k, lt):
    """lt: time since the shot started."""
    dur = max(sh["t1"] - sh["t0"] + XF_SHOT, 0.5)
    p = lt / dur
    seed = zlib.crc32((e["id"] + str(k)).encode()) % 1000
    kind = sh["kind"]
    if kind == "photo":
        key = f"photo|{sh['file']}|{seed}|{sh['focus']}|{sh.get('grade')}"
        foc = focus_of(build, sh, seed)["focus"]
        img = cached(build, key, lambda: None)
        z, cx, cy = move_params(sh, p, foc)
        return camera(img, z, cx, cy)
    if kind == "paper":
        key = f"paper|{sh['file']}|{seed}|{sh['focus']}|{sh.get('grade')}"
        meta = focus_of(build, sh, seed)
        bg = cached(build, key, lambda: None)
        obj = cached(build, "paperobj" + key, lambda: None)
        drop = 0.42
        if lt < drop + 0.05:
            q = ease_out(lt / drop)
            canvas = bg.convert("RGBA")
            sc = 1.12 - 0.12 * q
            o = obj.resize((int(obj.width * sc), int(obj.height * sc)), Image.BILINEAR).rotate(6 * (1 - q), resample=Image.BILINEAR)
            x = meta["pos"][0] + (obj.width - o.width) / 2
            y = meta["pos"][1] + (obj.height - o.height) / 2 - 420 * (1 - q)
            canvas.alpha_composite(o, (int(x), int(y)))
            return camera(canvas.convert("RGB"), 1.0, BW / 2, BH / 2)
        if "pcomp" + key not in _cache:
            c = bg.convert("RGBA")
            c.alpha_composite(obj, tuple(int(v) for v in meta["pos"]))
            _cache["pcomp" + key] = c.convert("RGB")
        q = smooth((lt - drop) / max(dur - drop, 0.5))
        fx, fy = meta["focus"]
        z = 1.0 + 0.42 * q
        return camera(_cache["pcomp" + key], z, BW / 2 + (fx - BW / 2) * q, BH / 2 + (fy - BH / 2) * q)
    if kind == "typed":
        img = type_layer_abs(sh, lt, e)
        z = (1.12 if not sh.get("big") else 1.06) + 0.06 * smooth(p)
        return camera(img, z, BW / 2, BH / 2 + 10)
    if kind == "tally":
        img = tally_layer(sh, lt + sh["t0"], e)
        return camera(img, 1.0 + 0.06 * smooth(p), BW / 2, BH / 2)
    if kind == "footage":
        return footage_frame(build, sh, lt)
    if kind == "endcard":
        return camera(endcard_canvas(lt), 1.0 + 0.04 * smooth(p), BW / 2, BH / 2)
    return np.zeros((OH, OW, 3), np.float32)


def type_layer_abs(sh, lt, e):
    # typed-line times are scene-relative; lt is shot-relative
    return type_layer(sh, lt + sh["t0"], e["id"])


def frames_dir(build, file, a, b):
    d = os.path.join(build, "clips", hashlib.md5(f"{file}|{a}|{b}".encode()).hexdigest()[:12])
    return d


def extract(build, file, a, b):
    d = frames_dir(build, file, a, b)
    if not os.path.exists(os.path.join(d, "done")):
        os.makedirs(d, exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", file, "-vf",
                        f"scale={OW}:{OH}:force_original_aspect_ratio=increase,crop={OW}:{OH},fps={FPS}",
                        "-q:v", "3", os.path.join(d, "%05d.jpg")], check=True)
        open(os.path.join(d, "done"), "w").close()
    return d


def footage_frame(build, sh, lt):
    d = frames_dir(build, sh["file"], sh["a"], sh["b"])
    n = len([f for f in os.listdir(d) if f.endswith(".jpg")])
    k = min(n, int(lt * FPS) + 1)
    f = np.asarray(Image.open(os.path.join(d, f"{k:05d}.jpg")).convert("RGB")).astype(np.float32)
    lum = f @ np.array([0.299, 0.587, 0.114], np.float32)
    return f * 0.6 + lum[..., None] * np.array([1.02, 0.97, 0.88], np.float32) * 0.4


# ------------------------------------------------------------------ overlays
def text_ov(key, draw_fn, size):
    if key not in _cache:
        im = Image.new("RGBA", size, (0, 0, 0, 0))
        draw_fn(ImageDraw.Draw(im), im)
        _cache[key] = np.asarray(im).astype(np.float32) / 255
    return _cache[key]


def blend(f, ov, x, y, alpha=1.0):
    h, w = ov.shape[:2]
    x, y = int(x), int(y)
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, OW), min(y + h, OH)
    if x1 <= x0 or y1 <= y0 or alpha <= 0:
        return
    o = ov[y0 - y:y1 - y, x0 - x:x1 - x]
    a = o[..., 3:4] * alpha
    f[y0:y1, x0:x1] = f[y0:y1, x0:x1] * (1 - a) + o[..., :3] * 255 * a


SHOW = [("nineteen thirty-seven", "1937"), ("nineteen eighty-five", "1985"), ("nineteen eighty-eight", "1988"),
        ("nineteen ninety-two", "1992"), ("nineteen ninety-three", "1993"), ("nineteen ninety-four", "1994"),
        ("nineteen ninety-six", "1996"), ("nineteen ninety-seven", "1997"), ("nineteen ninety-eight", "1998"),
        ("nineteen ninety-nine", "1999"), ("nineteen-eighties", "1980s"), ("twenty twelve", "2012"),
        ("twenty thirteen", "2013"), ("twenty eighteen", "2018"), ("twenty twenty-five", "2025"),
        ("Fourteen million", "14 million"), ("twenty-third", "23rd"), ("twenty-two", "22"), ("twenty-three", "23"),
        ("nineteen of thirty", "19 of 30"), ("thirty-two", "32"), ("twenty-five", "25"), ("fifty-four", "54"),
        ("sixty", "60")]


def show(s):
    for a, b in SHOW:
        s = s.replace(a, b)
    return s


def sub_ov(s):
    s = show(s)
    fnt = SANS(32, "SemiBold")
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    words, lines, cur = s.split(), [], ""
    for wd in words:
        if cur and tmp.textlength(cur + " " + wd, font=fnt) > 1000:
            lines.append(cur)
            cur = wd
        else:
            cur = (cur + " " + wd).strip()
    lines.append(cur)
    W, H = 1180, 46 * len(lines) + 24

    def dr(d, im):
        bw = max(tmp.textlength(l, font=fnt) for l in lines) + 44
        d.rounded_rectangle([W / 2 - bw / 2, 4, W / 2 + bw / 2, H - 4], radius=10, fill=(0, 0, 0, 135))
        for i, l in enumerate(lines):
            y = 22 + i * 46 + 12
            for dx, dy in ((2, 2), (0, 2), (2, 0), (-1, 1)):
                d.text((W / 2 + dx, y + dy), l, font=fnt, fill=(0, 0, 0, 170), anchor="mm")
        im2 = im.filter(ImageFilter.GaussianBlur(2.2))
        im.paste(im2)
        d = ImageDraw.Draw(im)
        for i, l in enumerate(lines):
            d.text((W / 2, 22 + i * 46 + 12), l, font=fnt, fill=(255, 255, 255, 255), anchor="mm")
    return text_ov(("sub", s), dr, (W, H))


def label_ov(label, credit=None):
    def dr(d, im):
        d.rectangle([0, 6, 4, 62], fill=GOLD + (255,))
        d.text((18, 14), label, font=SANS(25, "SemiBold"), fill=(250, 246, 238, 255), anchor="lt")
        if credit:
            d.text((18, 46), credit, font=SANS(16, "Medium"), fill=(220, 210, 190, 230), anchor="lt")
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    w = int(max(tmp.textlength(label, font=SANS(25, "SemiBold")), tmp.textlength(credit or "", font=SANS(16, "Medium")))) + 40
    return text_ov(("label", label, credit), dr, (w, 72))


def archive_tag(year):
    def dr(d, im):
        d.rounded_rectangle([0, 0, 199, 33], radius=5, fill=(0, 0, 0, 150))
        d.ellipse([12, 11, 24, 23], fill=(210, 40, 36, 255))
        d.text((34, 17), f"ARCHIVE  ·  {year}", font=SANS(16, "Bold"), fill=(255, 255, 255, 240), anchor="lm")
    return text_ov(("tag", year), dr, (200, 34))


# ------------------------------------------------------------------ frame assembly
BUILD = sys.argv[1] if len(sys.argv) > 1 else "."
TL, TOTAL = build(os.path.join(BUILD, "timing.json"))


def lower_gradient():
    if "grad" not in _cache:
        y = np.linspace(0, 1, OH)[:, None, None]
        _cache["grad"] = np.clip((y - 0.62) / 0.38, 0, 1) ** 1.6 * 0.55
    return _cache["grad"]


def scene_frame(e, lt):
    if e.get("clip"):
        d = frames_dir(BUILD, e["clip"][0], e["clip"][1], e["clip"][2])
        n = len([f for f in os.listdir(d) if f.endswith(".jpg")])
        k = min(n, int(lt * FPS) + 1)
        f = np.asarray(Image.open(os.path.join(d, f"{k:05d}.jpg")).convert("RGB")).astype(np.float32)
        lum = f @ np.array([0.299, 0.587, 0.114], np.float32)
        f = f * 0.7 + lum[..., None] * np.array([1.02, 0.97, 0.88], np.float32) * 0.3
        year = "1998" if "1998" in e["clip"][0] else "1993"
        blend(f, archive_tag(year), 28, 26, smooth(lt / 0.4))
        lab = label_ov(e["label"])
        f = f * (1 - lower_gradient() * smooth(lt / 0.5) * (1 - smooth((lt - 5.0) / 0.6)))
        blend(f, lab, 40, OH - 190, smooth((lt - 0.4) / 0.5) * (1 - smooth((lt - 5.0) / 0.6)))
        return f
    if e.get("logo"):
        return logo_canvas(lt)
    if e.get("card"):
        return camera(chapter_canvas(e, lt), 1.0 + 0.05 * smooth(lt / e["dur"]), BW / 2, BH / 2)
    shots = e["shots"]
    k = max([i for i, s in enumerate(shots) if s["t0"] <= lt] or [0])
    sh = shots[k]
    f = shot_frame(BUILD, e, sh, k, lt - sh["t0"])
    if k > 0 and lt - sh["t0"] < XF_SHOT and sh["kind"] != "paper":
        pv = shots[k - 1]
        w = smooth((lt - sh["t0"]) / XF_SHOT)
        f = shot_frame(BUILD, e, pv, k - 1, lt - pv["t0"]) * (1 - w) + f * w
    if sh.get("label"):
        ll = lt - sh["t0"]
        a = smooth((ll - 0.5) / 0.5) * (1 - smooth((ll - 5.0) / 0.5))
        if a > 0:
            f = f * (1 - lower_gradient() * a)
            blend(f, label_ov(sh["label"], sh.get("credit")), 40 - 30 * (1 - a), OH - 190, a)
    if sh["kind"] == "footage":
        blend(f, archive_tag("1993"), 28, 26, smooth((lt - sh["t0"]) / 0.4))
    return f


def grain():
    if "grain" not in _cache:
        rng = np.random.default_rng(7)
        _cache["grain"] = [rng.normal(0, 3.2, (OH, OW, 1)).astype(np.float32) for _ in range(8)]
        yy, xx = np.mgrid[0:OH, 0:OW]
        d = np.sqrt(((xx - OW / 2) / (OW / 2)) ** 2 + ((yy - OH / 2) / (OH / 2)) ** 2)
        _cache["vig"] = np.clip(1 - 0.38 * np.clip(d - 0.5, 0, None) ** 1.5, 0, 1)[..., None].astype(np.float32)
    return _cache["grain"], _cache["vig"]


def frame_at(i):
    t = i / FPS
    act = [e for e in TL if e["start"] <= t < e["end"]] or [TL[-1]]
    cur = act[-1]
    lt = t - cur["start"]
    f = scene_frame(cur, lt)
    if len(act) > 1 and lt < cur["xf"]:
        prev = act[-2]
        w = smooth(lt / cur["xf"])
        f = scene_frame(prev, t - prev["start"]) * (1 - w) + f * w
    if cur.get("logo") and lt < 0.6:
        pass
    # subtitles (current scene, or the outgoing one during a dissolve)
    for e in act:
        el = t - e["start"]
        for a0, a1, s in e.get("subs") or []:
            if a0 - 0.1 <= el <= a1 + 0.2:
                so = sub_ov(s)
                al = smooth((el - a0 + 0.1) / 0.15) * (1 - smooth((el - a1) / 0.2))
                blend(f, so, OW / 2 - so.shape[1] / 2, OH - so.shape[0] - 26, al)
    g, vig = grain()
    f = f * vig + g[(i // 2) % len(g)]
    # fade in at the very start, out at the very end
    f *= smooth(t / 0.8) * smooth((TOTAL - t) / 1.5)
    return np.clip(f, 0, 255).astype(np.uint8).tobytes()


def warm():
    os.makedirs(os.path.join(BUILD, "plates"), exist_ok=True)
    for e in TL:
        if e.get("clip"):
            extract(BUILD, *e["clip"])
        for k, sh in enumerate(e.get("shots") or []):
            seed = zlib.crc32((e["id"] + str(k)).encode()) % 1000
            if sh["kind"] in ("photo", "paper"):
                key = f"{sh['kind']}|{sh['file']}|{seed}|{sh['focus']}|{sh.get('grade')}"
                if not os.path.exists(plate_path(BUILD, key) + ".json"):
                    prep_shot(BUILD, sh, seed)
            if sh["kind"] == "footage":
                extract(BUILD, sh["file"], sh["a"], sh["b"])


def main():
    out = sys.argv[2]
    a = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    b = float(sys.argv[4]) if len(sys.argv) > 4 else TOTAL
    warm()
    frames = range(int(a * FPS), int(b * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "4000k", "-bufsize", "8000k",
           "-pix_fmt", "yuv420p", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(os.cpu_count()) as pool:
        for n, buf in enumerate(pool.imap(frame_at, frames, chunksize=8)):
            p.stdin.write(buf)
            if n % 900 == 0:
                print(f"frame {n}/{len(frames)}", flush=True)
    p.stdin.close()
    p.wait()
    print("video done", round(TOTAL, 1))


if __name__ == "__main__":
    main()
