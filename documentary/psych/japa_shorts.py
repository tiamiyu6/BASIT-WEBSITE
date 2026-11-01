"""Vertical Shorts (1080x1920) cut from the Japa film's voice + illustrations.

usage (from documentary/): python3 psych/japa_shorts.py IMG_DIR BUILD_DIR OUT_DIR
BUILD_DIR is the japa_full.py build (voice/NN.wav + voice.json).
"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
IMGS, BUILD, OUTD = sys.argv[1:4]
sys.argv = ["x", "m", IMGS, BUILD, "o"]
sys.path.insert(0, HERE)
import japa_full as jf
os.makedirs(OUTD, exist_ok=True)
W, H, FPS, SR = 1080, 1920, 30, jf.SR
GREEN, INK, CREAM = jf.GREEN, jf.INK, jf.CREAM
FONT = lambda s: ImageFont.truetype(os.path.join(HERE, "fonts", "LilitaOne-Regular.ttf"), s)
CAP, CAPB, TAG = FONT(96), FONT(118), FONT(54)

line2pic = {}
for s in jf.PICS:
    if not isinstance(s, str) and not isinstance(s[0], str):
        for n in s[1]:
            line2pic[n] = s[0]
items = json.load(open(os.path.join(BUILD, "voice.json")))["items"]

# name, hook title (top pill), first line, last line
SHORTS = [("japa_short1_hook", "WHY NIGERIANS JAPA", 1, 7),
          ("japa_short2_comparison", "THE REAL REASON PEOPLE LEAVE", 16, 22),
          ("japa_short3_ceiling", "IT'S NOT JUST THE MONEY", 26, 33),
          ("japa_short4_ending", "IS JAPA ABOUT MONEY?", 65, 71)]


def bg_fg(img, p):
    big = img.resize((W, H), Image.BILINEAR) if False else None
    sc = H / img.height
    cover = img.resize((int(img.width * sc), H), Image.BILINEAR)
    x0 = (cover.width - W) // 2
    bg = cover.crop((x0, 0, x0 + W, H)).filter(ImageFilter.GaussianBlur(28))
    bg = Image.eval(bg, lambda v: int(v * 0.55))
    z = 1.0 + 0.07 * p
    fw = int(W * z)
    fg = img.resize((fw, int(fw * img.height / img.width)), Image.BICUBIC)
    cx = (fg.width - W) // 2
    fg = fg.crop((cx, 0, cx + W, fg.height))
    bg.paste(fg, (0, 560 - fg.height // 2 + 330))
    return bg


def caption(im, words, t):
    for ch in jf.chunks(words):
        if ch[0][1] - 0.05 <= t < ch[-1][2] + 0.15:
            break
    else:
        return
    d = ImageDraw.Draw(im)
    parts = []
    for w, a, b in ch:
        on = a <= t < b + 0.08 or (w is ch[-1][0] and t >= a)
        parts.append((w.upper().strip(".,?:;"), CAPB if on else CAP, GREEN if on else (255, 255, 255)))
    lines, cur, cw = [], [], 0
    for s, f, c in parts:                      # wrap to two lines when too wide
        wd = d.textlength(s, font=f) + 24
        if cur and cw + wd > W - 100:
            lines.append(cur); cur, cw = [], 0
        cur.append((s, f, c, wd)); cw += wd
    lines.append(cur)
    y = 1330
    for ln in lines:
        x = W / 2 - sum(i[3] for i in ln) / 2
        for s, f, c, wd in ln:
            d.text((x + 5, y + 6), s, font=f, fill=INK, anchor="ls", stroke_width=9, stroke_fill=INK)
            d.text((x, y), s, font=f, fill=c, anchor="ls", stroke_width=8, stroke_fill=(35, 28, 24))
            x += wd
        y += 135


def overlays(im, title, t, total):
    d = ImageDraw.Draw(im)
    wd = d.textlength(title, font=TAG) + 80
    d.rounded_rectangle((W / 2 - wd / 2, 150, W / 2 + wd / 2, 250), 28, fill=CREAM, outline=INK, width=6)
    d.text((W / 2, 220), title, font=TAG, fill=INK, anchor="ms")
    if t > total - 3.0:
        a = min(1, (t - (total - 3.0)) / 0.4)
        s = Image.new("RGBA", (W, 260), (0, 0, 0, 0))
        sd = ImageDraw.Draw(s)
        sd.rounded_rectangle((90, 20, W - 90, 230), 30, fill=CREAM + (int(240 * a),), outline=INK + (int(255 * a),), width=6)
        sd.text((W / 2, 105), "FULL VIDEO ON MY CHANNEL", font=FONT(62), fill=INK + (int(255 * a),), anchor="mm")
        sd.text((W / 2, 185), "NAIJA UNTOLD", font=FONT(52), fill=(60, 120, 110, int(255 * a)), anchor="mm")
        im.paste(s, (0, 1500), s)


for name, title, a, b in SHORTS:
    t, segs, clips = 0.5, [], []
    cur = None
    for n in range(a, b + 1):
        it = items[str(n)]
        pic = line2pic[n]
        if cur is None or cur["pic"] != pic:
            cur = dict(pic=pic, t0=t, words=[])
            segs.append(cur)
        cur["words"] += [(w, t + x, t + y) for w, x, y in it["words"]]
        clips.append((t, os.path.join(BUILD, "voice", f"{n:02d}.wav")))
        t += it["dur"] + 0.4
        cur["t1"] = t
    total = t + 3.0
    mix = np.zeros(int(total * SR))
    for st, p in clips:
        x, _ = sf.read(p, dtype="float32")
        i = int(st * SR)
        mix[i:i + len(x)] += x[:len(mix) - i]
    mix += jf.music(total) * 1.2
    wav = os.path.join(OUTD, name + ".wav")
    sf.write(wav, np.clip(mix, -1, 1), SR)
    out = os.path.join(OUTD, name + ".mp4")
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-i", wav, "-c:v", "libx264", "-crf", "22", "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
                            "-af", "loudnorm=I=-14:TP=-1.5", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    imgs = {}
    for f in range(int(total * FPS)):
        tt = f / FPS
        k = max([i for i, s in enumerate(segs) if s["t0"] - 0.2 <= tt] or [0])
        sg = segs[k]
        if sg["pic"] not in imgs:
            imgs[sg["pic"]] = Image.open(os.path.join(IMGS, f"{sg['pic']:02d}.png")).convert("RGB")
        p = min(1, max(0, (tt - sg["t0"]) / max(0.5, sg["t1"] - sg["t0"])))
        im = bg_fg(imgs[sg["pic"]], p)
        caption(im, sg["words"], tt)
        overlays(im, title, tt, total)
        enc.stdin.write(im.tobytes())
    enc.stdin.close(); enc.wait()
    os.remove(wav)
    print("SHORT", name, round(total, 1), "s", flush=True)
