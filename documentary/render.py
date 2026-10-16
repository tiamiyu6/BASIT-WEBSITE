"""Render the picture: Ken Burns moves, transitions, captions, subtitles and film FX -> raw frames piped to ffmpeg.

usage: python3 render.py BUILD_DIR OUT.mp4 [start_sec end_sec]
"""
import math, os, subprocess, sys, zlib
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
import visuals as V
from timeline import build, FPS

OW, OH = 1280, 720
BUILD = sys.argv[1]
TL, TOTAL = build(f"{BUILD}/timing.json")
TLMAP = {e["id"]: e for e in TL}
CH_NUM = {e["chapter"]: e["title"].split()[-1] for e in TL if e["plate"] == "chapter"}

_cache = {}
ARCHIVAL = {"map_lagos", "chicago", "senate", "june12", "exile"}


def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------ cached assets
def plate(e):
    k = ("plate", e["id"] if os.path.exists(os.path.join(V.HERE, "photos", e["id"] + ".jpg")) else e["plate"])
    if k not in _cache:
        p = f"{BUILD}/plates/{k[1]}.png"
        if not os.path.exists(p):
            V.plate(e).resize((1440, 810), Image.LANCZOS).save(p)
        _cache[k] = Image.open(p).convert("RGB")
    return _cache[k]


def static_fx():
    if "fx" not in _cache:
        yy, xx = np.mgrid[0:OH, 0:OW]
        d = np.sqrt(((xx - OW / 2) / (OW / 2)) ** 2 + ((yy - OH / 2) / (OH / 2)) ** 2)
        vig = np.clip(1 - 0.42 * np.clip(d - 0.45, 0, None) ** 1.6, 0, 1)[..., None].astype(np.float32)
        rng = np.random.default_rng(3)
        grain = [rng.normal(0, 3.0, (OH, OW, 1)).astype(np.float32) for _ in range(6)]
        leak = np.zeros((OH * 2, OW * 2, 3), np.float32)
        for cx, cy, r, col in [(0.3, 0.4, 0.5, (255, 120, 30)), (1.4, 0.9, 0.6, (255, 60, 40)),
                               (0.9, 1.5, 0.45, (255, 190, 90)), (1.7, 0.2, 0.4, (255, 140, 60))]:
            y2, x2 = np.mgrid[0:OH * 2, 0:OW * 2]
            dd = np.sqrt(((x2 / OW - cx)) ** 2 + ((y2 / OH - cy)) ** 2) / r
            leak += np.clip(1 - dd, 0, 1)[..., None] ** 2 * np.array(col, np.float32)
        _cache["fx"] = (vig, grain, leak)
    return _cache["fx"]


def caption_img(e):
    k = ("cap", e["id"])
    if k not in _cache:
        if not e["title"] or e["plate"] == "chapter":
            _cache[k] = None
            return None
        kicker = f"CHAPTER {CH_NUM.get(e['chapter'], '')} · {e['chapter']}" if e["chapter"] in CH_NUM else e["chapter"]
        fk, ft, fs = V.F(14, "Bold"), V.F(26, "Bold"), V.F(17, "Medium")
        tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        w = int(max(tmp.textlength(e["title"], font=ft), tmp.textlength(e["sub"], font=fs),
                    tmp.textlength(kicker, font=fk) + len(kicker) * 2.5) + 56)
        h = 104
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, w - 1, h - 1], radius=10, fill=(8, 8, 10, 190))
        d.rectangle([0, 10, 5, h - 10], fill=V.GOLD)
        x = 24
        for c in kicker:
            d.text((x, 14), c, font=fk, fill=V.GOLD)
            x += tmp.textlength(c, font=fk) + 2.5
        d.text((24, 36), e["title"], font=ft, fill=V.CREAM)
        d.text((24, 72), e["sub"], font=fs, fill=(200, 192, 178))
        _cache[k] = np.asarray(im).astype(np.float32) / 255
    return _cache[k]


def sub_img(s):
    k = ("sub", s)
    if k not in _cache:
        f = V.F(30, "SemiBold")
        tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        words, lines, cur = s.split(), [], ""
        for wd in words:
            if cur and tmp.textlength(cur + " " + wd, font=f) > 1040:
                lines.append(cur)
                cur = wd
            else:
                cur = (cur + " " + wd).strip()
        lines.append(cur)
        w = int(max(tmp.textlength(l, font=f) for l in lines)) + 40
        h = 44 * len(lines) + 20
        im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([10, 10, w + 10, h + 10], radius=8, fill=(0, 0, 0, 150))
        im = im.filter(ImageFilter.GaussianBlur(4))
        d = ImageDraw.Draw(im)
        for i, l in enumerate(lines):
            d.text((w / 2 + 12, 22 + 22 + i * 44 + 2), l, font=f, fill=(0, 0, 0, 200), anchor="mm")
            d.text((w / 2 + 10, 22 + 22 + i * 44), l, font=f, fill=(255, 255, 255, 255), anchor="mm")
        _cache[k] = np.asarray(im).astype(np.float32) / 255
    return _cache[k]


def tag_img():
    if "tag" not in _cache:
        f = V.F(16, "Bold")
        im = Image.new("RGBA", (190, 34), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, 189, 33], radius=6, fill=(0, 0, 0, 170))
        d.ellipse([12, 11, 24, 23], fill=(220, 50, 40, 255))
        d.text((34, 17), "ARCHIVE FOOTAGE", font=f, fill=(255, 255, 255, 255), anchor="lm")
        _cache["tag"] = np.asarray(im).astype(np.float32) / 255
    return _cache["tag"]


def blend(frame, ov, x, y, alpha=1.0):
    h, w = ov.shape[:2]
    x, y = int(x), int(y)
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, OW), min(y + h, OH)
    if x1 <= x0 or y1 <= y0:
        return
    o = ov[y0 - y:y1 - y, x0 - x:x1 - x]
    a = o[..., 3:4] * alpha
    frame[y0:y1, x0:x1] = frame[y0:y1, x0:x1] * (1 - a) + o[..., :3] * 255 * a


# ------------------------------------------------------------------ per-scene picture
def broll_img(name):
    k = ("broll", name)
    if k not in _cache:
        p = f"{BUILD}/plates/broll_{name}.png"
        if not os.path.exists(p):
            src = Image.open(os.path.join(V.HERE, "photos", "broll", name)).convert("RGB")
            W2, H2 = 1440, 810
            if src.width / src.height >= 1.5:
                im = ImageOps.fit(src, (W2, H2), Image.LANCZOS, centering=(0.5, 0.4))
            else:  # portrait-orientation photo: blurred backdrop + full photo
                im = ImageOps.fit(src, (W2, H2), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))
                im = Image.blend(im, Image.new("RGB", im.size, (0, 0, 0)), 0.5)
                fw = int(src.width * H2 / src.height)
                im.paste(src.resize((fw, H2), Image.LANCZOS), ((W2 - fw) // 2, 0))
            # gentle documentary grade
            a = np.asarray(im).astype(np.float32)
            lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
            a = a * 0.85 + lum[..., None] * 0.15
            a = (a - 128) * 1.06 + 124
            Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(p)
        _cache[k] = Image.open(p).convert("RGB")
    return _cache[k]


def broll_caption(e, b):
    fake = dict(e, id=e["id"] + "#" + b[0], title=b[1], sub=f"{b[2]}  ·  Photo: {b[3]}" if b[2] else f"Photo: {b[3]}")
    return caption_img(fake)


def kenburns(e, lt, extra_zoom=1.0, shake=(0, 0), img=None, key=None):
    img = img or plate(e)
    h = zlib.crc32((key or e["id"]).encode())
    zin = (h % 2 == 0) or e["plate"] in ("title", "open", "quote_emilokan", "quote_subsidy", "legacy")
    p = smooth(lt / max(e["dur"], 0.1)) * 0.6 + (lt / max(e["dur"], 0.1)) * 0.4
    z0, z1 = (1.0, 1.085) if zin else (1.085, 1.0)
    z = (z0 + (z1 - z0) * p) * extra_zoom
    ang = (h % 360) * math.pi / 180
    pan = 0.022 if e["plate"] not in ("title", "chapter", "credits", "results", "economy") else 0.0
    cx = 720 + math.cos(ang) * pan * 1440 * (p - 0.5)
    cy = 405 + math.sin(ang) * pan * 810 * (p - 0.5)
    s = 1440 / (OW * z)
    # keep crop inside the plate
    hw, hh = OW * s / 2, OH * s / 2
    cx = min(max(cx, hw), 1440 - hw) + shake[0]
    cy = min(max(cy, hh), 810 - hh) + shake[1]
    out = img.transform((OW, OH), Image.AFFINE, (s, 0, cx - hw, 0, s, cy - hh), resample=Image.BICUBIC)
    return np.asarray(out).astype(np.float32)


def chapter_frame(e, lt):
    base = kenburns(e, lt)
    im = Image.fromarray(base.astype(np.uint8)).convert("RGBA")
    layer = Image.new("RGBA", (OW, OH), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    a_in = smooth((lt - 0.25) / 0.9)
    a_out = 1 - smooth((lt - (e["dur"] - 0.7)) / 0.6)
    a = a_in * a_out
    track = 4 + 26 * (1 - smooth((lt - 0.2) / 2.6))
    f1, f2 = V.F(24, "Bold"), V.SF(92)

    def spaced(y, s, font, fill, sp):
        tw = sum(d.textlength(c, font=font) + sp for c in s) - sp
        x = OW / 2 - tw / 2
        for c in s:
            d.text((x, y), c, font=font, fill=fill, anchor="lm")
            x += d.textlength(c, font=font) + sp

    spaced(290, e["title"], f1, V.GOLD + (int(255 * a),), 10)
    spaced(380, e["sub"], f2, V.CREAM + (int(255 * a),), track)
    lw = 380 * smooth((lt - 0.3) / 1.2) * a_out
    d.line([OW / 2 - lw, 450, OW / 2 + lw, 450], fill=V.GOLD + (int(220 * a),), width=2)
    g = layer.filter(ImageFilter.GaussianBlur(14))
    im = Image.alpha_composite(Image.alpha_composite(im, g), layer)
    return np.asarray(im.convert("RGB")).astype(np.float32)


def portrait_frame(e, lt):
    """Open on his portrait, push into his eye; the story begins inside it."""
    if "portrait" not in _cache:
        img, eye = V.portrait()
        _cache["portrait"] = (img, eye)
    img, (ex, ey) = _cache["portrait"]
    BW, BH = img.size
    hold = 1.6
    ZMAX = 28 if os.path.exists(os.path.join(V.HERE, "photos", "portrait.jpg")) else 45
    if lt < hold:
        z, q = 1.0 + 0.05 * lt / hold, 0.0
    else:
        q = min(1.0, (lt - hold) / (e["dur"] - hold))
        z = 1.05 * math.exp(math.log(ZMAX / 1.05) * q ** 2.3)
    k = smooth(min(1.0, q * 1.4))
    cx, cy = BW / 2 + (ex - BW / 2) * k, BH / 2 + (ey - BH / 2) * k
    acc = None
    taps = (1.0,) if q < 0.35 else (1.0, 0.985, 0.97)  # radial motion blur once the push speeds up
    for m in taps:
        s = BW / (OW * z * m)
        hw, hh = OW * s / 2, OH * s / 2
        fr = np.asarray(img.transform((OW, OH), Image.AFFINE, (s, 0, cx - hw, 0, s, cy - hh),
                                      resample=Image.BICUBIC)).astype(np.float32)
        acc = fr if acc is None else acc + fr
    f = acc / len(taps)
    f *= smooth(lt / 1.2)
    w = smooth((lt - (e["dur"] - 0.45)) / 0.45)
    return f + (255 - f) * w


def archival(f, i, t):
    """Nostalgic film look for the pre-1999 scenes: sepia, flicker, scratches, dust."""
    rng = np.random.default_rng(i)
    lum = f @ np.array([0.299, 0.587, 0.114], np.float32)
    sep = lum[..., None] * np.array([1.07, 0.93, 0.72], np.float32)
    f = f * 0.25 + sep * 0.75
    f *= 0.94 + 0.08 * rng.random()
    for _ in range(rng.integers(0, 3)):
        x = int(rng.integers(0, OW))
        f[:, x:x + 2] = f[:, x:x + 2] * 0.55 + 200 * 0.45
    for _ in range(rng.integers(3, 12)):
        x, y, r = int(rng.integers(0, OW)), int(rng.integers(0, OH)), int(rng.integers(1, 4))
        f[max(0, y - r):y + r, max(0, x - r):x + r] = 20 if rng.random() < 0.7 else 230
    return f


def title_frame(e, lt):
    f = kenburns(e, lt, extra_zoom=1.0 + 0.06 * (1 - smooth(lt / 3)))
    # light sweep across the title
    x = (lt - 0.6) / 2.2 * (OW + 600) - 300
    xx = np.arange(OW)[None, :] + np.arange(OH)[:, None] * 0.35
    band = np.exp(-((xx - x - 120) / 70.0) ** 2)[..., None]
    f = f + band * f * 1.4
    return f


def clip_frame(e, lt):
    d = f"{BUILD}/clips/{e['id']}"
    n = len(os.listdir(d))
    k = min(n, int(lt * FPS) + 1)
    return np.asarray(Image.open(f"{d}/{k:05d}.jpg").convert("RGB")).astype(np.float32)


def scene_frame(e, lt, extra_zoom=1.0, shake=(0, 0)):
    if e.get("clip") and lt < e["clip"][1] + 0.6:
        f = clip_frame(e, lt)
        if lt > e["clip"][1]:
            w = smooth((lt - e["clip"][1]) / 0.6)
            f = f * (1 - w) + kenburns(e, lt, extra_zoom, shake) * w
        else:
            blend(f, tag_img(), 28, 26, smooth(lt / 0.4))
        t = e["start"] + lt
        for a0, a1, s in e["subs"]:
            if a0 - 0.12 <= t <= a1 + 0.25:
                si = sub_img(s)
                blend(f, si, OW / 2 - si.shape[1] / 2, OH - si.shape[0] - 30, 1.0)
        return f
    if e["plate"] == "portrait":
        return portrait_frame(e, lt)
    br = e.get("broll") or []
    bs = e.get("broll_secs", 0)
    if br and lt < bs * len(br) + 0.8:
        XF = 0.8
        k = min(int(lt // bs), len(br) - 1)
        lk = lt - k * bs
        sub_e = dict(e, dur=bs + XF)
        f = kenburns(sub_e, lk, extra_zoom, shake, img=broll_img(br[k][0]), key=br[k][0])
        if k > 0 and lk < XF:  # dissolve from previous photo
            pf = kenburns(sub_e, lk + bs, extra_zoom, shake, img=broll_img(br[k - 1][0]), key=br[k - 1][0])
            f = pf * (1 - smooth(lk / XF)) + f * smooth(lk / XF)
        snap = math.exp(-lk * 14) if lk < 0.4 and (k > 0 or lt < 0.4) else 0
        if lt > bs * len(br):  # dissolve into the scene's graphic
            w = smooth((lt - bs * len(br)) / XF)
            g = scene_frame(dict(e, broll=[]), lt, extra_zoom, shake)
            return f * (1 - w) + g * w
        f = f + (255 - f) * snap * 0.35
        cap = broll_caption(e, br[k])
        a = smooth((lk - 0.3) / 0.6) * (1 - smooth((lk - bs + 0.5) / 0.4))
        blend(f, cap, 28 - 40 * (1 - smooth((lk - 0.3) / 0.6)), 26, a)
        t = e["start"] + lt
        for a0, a1, s in e["subs"]:
            if a0 - 0.12 <= t <= a1 + 0.25:
                si = sub_img(s)
                al = smooth((t - a0 + 0.12) / 0.15) * (1 - smooth((t - a1) / 0.25))
                blend(f, si, OW / 2 - si.shape[1] / 2, OH - si.shape[0] - 30, al)
        return f
    if e["plate"] == "chapter":
        f = chapter_frame(e, lt)
    elif e["plate"] == "title":
        f = title_frame(e, lt)
    else:
        f = kenburns(e, lt, extra_zoom, shake)
    t = e["start"] + lt
    if e["plate"] in ARCHIVAL:
        f = archival(f, int(t * FPS), t)
    cap = caption_img(e)
    lt_cap = lt
    if e.get("broll_secs") and not e.get("broll"):  # called from the b-roll dissolve
        lt_cap = lt - e["broll_secs"] * len([b for b in TLMAP[e["id"]]["broll"]])
    if cap is not None:
        a = smooth((lt_cap - 0.5) / 0.7) * (1 - smooth((lt - e["dur"] + 0.6) / 0.5))
        slide = 40 * (1 - smooth((lt_cap - 0.5) / 0.7))
        blend(f, cap, OW - cap.shape[1] - 28 + slide, 26, a)
    for a0, a1, s in e["subs"]:
        if a0 - 0.12 <= t <= a1 + 0.25:
            si = sub_img(s)
            al = smooth((t - a0 + 0.12) / 0.15) * (1 - smooth((t - a1) / 0.25))
            blend(f, si, OW / 2 - si.shape[1] / 2, OH - si.shape[0] - 30, al)
    if e["plate"] == "credits":
        f *= smooth((e["dur"] - lt) / 2.0)
    return f


# ------------------------------------------------------------------ transitions & global FX
def glitch(f, amount, seed):
    rng = np.random.default_rng(seed)
    out = f.copy()
    sh = int(18 * amount) + 1
    out[..., 0] = np.roll(f[..., 0], sh, axis=1)
    out[..., 2] = np.roll(f[..., 2], -sh, axis=1)
    for _ in range(int(14 * amount)):
        y = rng.integers(0, OH - 40)
        hgt = rng.integers(4, 40)
        out[y:y + hgt] = np.roll(out[y:y + hgt], rng.integers(-120, 120), axis=1)
    out[::3] *= 1 - 0.25 * amount
    return out


def frame_at(i):
    t = i / FPS
    vig, grain, leak = static_fx()
    act = [e for e in TL if e["start"] <= t < e["end"]]
    if not act:
        act = [TL[-1]]
    cur = act[-1]
    lt = t - cur["start"]
    shake = (0, 0)
    if cur["hit"] and lt < 0.7:
        k = math.exp(-lt * 7) * 9
        shake = (math.sin(lt * 90) * k, math.cos(lt * 77) * k)
    if cur["plate"] in ARCHIVAL:  # gate weave
        rng = np.random.default_rng(i)
        shake = (shake[0] + rng.normal(0, 0.8), shake[1] + rng.normal(0, 0.8))
    slam = None
    if cur.get("slam_end") is not None and 0 <= t - cur["slam_end"] < 0.9:
        slam = t - cur["slam_end"]
        k = math.exp(-slam * 6) * 14
        shake = (shake[0] + math.sin(slam * 95) * k, shake[1] + math.cos(slam * 81) * k)
    leak_amt = 0.04
    if len(act) == 2 and cur["trans"] in ("fade", "zoom", "glitch"):
        prev = act[0]
        p = (t - cur["start"]) / max(cur["ov"], 1e-3)
        ps = smooth(p)
        if cur["trans"] == "fade":
            f = scene_frame(prev, t - prev["start"]) * (1 - ps) + scene_frame(cur, lt) * ps
        elif cur["trans"] == "zoom":
            a = scene_frame(prev, t - prev["start"], extra_zoom=1 + 0.5 * ps ** 2)
            b = scene_frame(cur, lt, extra_zoom=1.25 - 0.25 * ps)
            f = a * (1 - ps) + b * ps
            f += 255 * 0.5 * math.sin(math.pi * p)
        else:
            f = scene_frame(prev if p < 0.5 else cur, t - (prev if p < 0.5 else cur)["start"])
            f = glitch(f, math.sin(math.pi * p), i)
        leak_amt = 0.04 + 0.4 * math.sin(math.pi * p)
    else:
        f = scene_frame(cur, lt, extra_zoom=1.0 + (0.07 * math.exp(-slam * 5) if slam is not None else 0),
                        shake=shake)
        if slam is not None:
            fl = math.exp(-slam * 10)
            f = f + (255 - f) * fl * 0.85
            if slam < 0.18:
                f = glitch(f, 1 - slam / 0.18, i)
            leak_amt = 0.04 + 0.5 * fl
        if cur["trans"] == "flash" and lt < 0.5:
            fl = math.exp(-lt * 9)
            f = f + (255 - f) * fl
            leak_amt = 0.04 + 0.5 * fl
        if cur["trans"] == "glitch" and lt < 0.12 and cur["ov"] == 0:
            f = glitch(f, 1 - lt / 0.12, i)
    # dip to black in/out
    nxt = next((e for e in TL if e["start"] > cur["start"]), None)
    if cur["trans"] == "dip":
        f *= smooth(lt / 0.7)
    if nxt and nxt["trans"] == "dip":
        f *= smooth((cur["end"] - t) / 0.6)
    if cur["plate"] in ("questions", "case1993", "certificate", "bullion", "economy") and int(t * 7) % 23 == 0:
        f = glitch(f, 0.35, i)  # occasional tension micro-glitch
    # light leak (drifting)
    ox = int((math.sin(t * 0.21) * 0.5 + 0.5) * OW)
    oy = int((math.cos(t * 0.17) * 0.5 + 0.5) * OH)
    f = f + leak[oy:oy + OH, ox:ox + OW] * leak_amt
    # film look: contrast curve, vignette, grain, bars of soft darkness top/bottom
    f = f * vig
    f = f + grain[(i // 5) % len(grain)]
    return np.clip(f, 0, 255).astype(np.uint8).tobytes()


def main():
    out = sys.argv[2]
    a = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    b = float(sys.argv[4]) if len(sys.argv) > 4 else TOTAL
    os.makedirs(f"{BUILD}/plates", exist_ok=True)
    frames = range(int(a * FPS), int(b * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-maxrate", "1800k", "-bufsize", "3600k",
           "-pix_fmt", "yuv420p", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    # warm the plate cache once so workers just read PNGs
    for e in TL:
        if e["plate"] != "portrait":
            plate(e)
        if e["clip"]:
            d = f"{BUILD}/clips/{e['id']}"
            os.makedirs(d, exist_ok=True)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", e["clip"][0], "-vf",
                            f"scale={OW}:{OH}:force_original_aspect_ratio=increase,crop={OW}:{OH},fps={FPS}",
                            "-q:v", "3", f"{d}/%05d.jpg"], check=True)
    with Pool(os.cpu_count()) as pool:
        for n, buf in enumerate(pool.imap(frame_at, frames, chunksize=6)):
            p.stdin.write(buf)
            if n % 600 == 0:
                print(f"frame {n}/{len(frames)}", flush=True)
    p.stdin.close()
    p.wait()
    print("video done", round(TOTAL, 1))


if __name__ == "__main__":
    main()
