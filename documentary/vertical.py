"""Compose a rendered 16:9 short into a 9:16 Reel: blurred backdrop, framed video, headline,
and big word-by-word captions (spoken word highlighted).

usage: SHORT=who python3 vertical.py BUILD_DIR OUT.mp4
"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import visuals as V
from timeline import build, FPS
from shorts import SHORTS

BUILD, OUT = sys.argv[1], sys.argv[2]
NAME = os.environ["SHORT"]
VW, VH = 1080, 1920
IW, IH = 1280, 720
TL, TOTAL = build(f"{BUILD}/timing.json")
HEAD = SHORTS[NAME]["headline"]

# word timings: spread each subtitle chunk's time across its words by length
WORDS = []
for e in TL:
    for a0, a1, s in e["subs"]:
        ws = s.split()
        tot = sum(len(w) + 1 for w in ws)
        t = a0
        for w in ws:
            d = (a1 - a0) * (len(w) + 1) / tot
            WORDS.append((t, t + d, w))
            t += d
# group into caption lines of up to 3 words that stay within one subtitle chunk
LINES = []
for e in TL:
    for a0, a1, s in e["subs"]:
        ws = [w for w in WORDS if a0 - 1e-6 <= w[0] < a1 - 1e-6]
        for i in range(0, len(ws), 3):
            LINES.append(ws[i:i + 3])

F_CAP = V.F(86, "Black")
F_HEAD = V.F(92, "Black")
F_TAG = V.F(30, "Bold")


def headline_layer():
    im = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, (txt, col) in enumerate(((HEAD[0], (255, 255, 255)), (HEAD[1], (255, 214, 64)))):
        y = 215 + i * 115
        d.text((VW / 2, y), txt, font=F_HEAD, fill=col + (255,), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0, 255))
    d.text((VW / 2, 1810), "JAGABAN  ·  FULL DOCUMENTARY", font=F_TAG, fill=(230, 220, 200, 200), anchor="mm")
    return im


HEADL = headline_layer()


def caption(t):
    line = next((ln for ln in LINES if ln and ln[0][0] - 0.05 <= t < ln[-1][1] + 0.15), None)
    if not line:
        return None
    im = Image.new("RGBA", (VW, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    words = [w for _, _, w in line]
    gap = 28
    base = sum(d.textlength(w.upper(), font=F_CAP) for w in words) + gap * (len(words) - 1)
    scale = min(1.0, (VW - 90) / max(base, 1))
    fonts = []
    for w0, w1, w in line:
        active = w0 <= t < w1 + 0.05
        fonts.append((V.F(int(86 * scale * (1.1 if active else 1.0)), "Black"), active))
    widths = [d.textlength(w.upper(), font=f) for w, (f, _) in zip(words, fonts)]
    total = sum(widths) + gap * scale * (len(words) - 1)
    x = VW / 2 - total / 2
    for w, (font, active), wd in zip(words, fonts, widths):
        col = (255, 214, 64) if active else (255, 255, 255)
        d.text((x, 130), w.upper(), font=font, fill=col + (255,), anchor="lm", stroke_width=7, stroke_fill=(0, 0, 0, 255))
        x += wd + gap * scale
    return im


def compose(fr, i):
    t = i / FPS
    src = Image.frombytes("RGB", (IW, IH), fr)
    bg = src.resize((54, 96), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3)).resize((VW, VH), Image.BICUBIC)
    bg = Image.blend(bg, Image.new("RGB", (VW, VH), (0, 0, 0)), 0.5)
    cw = IH * 4 // 3  # 4:3 centre crop: bigger picture on a phone
    vid = src.crop(((IW - cw) // 2, 0, (IW + cw) // 2, IH)).resize((VW, VW * 3 // 4), Image.LANCZOS)
    y0 = 500
    bg.paste(vid, (0, y0))
    canvas = bg.convert("RGBA")
    d = ImageDraw.Draw(canvas)
    d.line([0, y0 - 3, VW, y0 - 3], fill=V.GOLD + (255,), width=4)
    d.line([0, y0 + vid.height + 2, VW, y0 + vid.height + 2], fill=V.GOLD + (255,), width=4)
    canvas = Image.alpha_composite(canvas, HEADL)
    cap = caption(t)
    if cap is not None:
        canvas.alpha_composite(cap, (0, y0 + vid.height + 40))
    return canvas.convert("RGB").tobytes()


def main():
    dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", f"{BUILD}/picture.mp4", "-f", "rawvideo",
                            "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{VW}x{VH}", "-r", str(FPS), "-i", "-", "-i", f"{BUILD}/mix.wav",
                            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "libx264", "-preset", "medium",
                            "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest",
                            "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    n = IW * IH * 3
    i = 0
    while True:
        fr = dec.stdout.read(n)
        if len(fr) < n:
            break
        enc.stdin.write(compose(fr, i))
        i += 1
    enc.stdin.close()
    enc.wait()
    print("vertical done", i, "frames")


if __name__ == "__main__":
    main()
