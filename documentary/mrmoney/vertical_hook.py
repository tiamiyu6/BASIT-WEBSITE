"""Fast-cut TikTok hook in the "WHO IS TINUBU REALLY?" format: fixed headline, one big keyword per beat, word captions.

Every beat is one scene of the finished film (picture + the narrator's own line), so only our own material is used.
usage (from documentary/): python3 mrmoney/vertical_hook.py BUILD OUT.mp4 "HEAD 1" "HEAD 2" ID:KEYWORD[:MAXSEC] ...
"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw

BUILD, OUT, H1, H2 = sys.argv[1:5]
BEATS = sys.argv[5:]
sys.argv = ["x", BUILD, "0", "1", H1, H2, OUT]
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vertical as V
VW, VH, FPS, IW, IH = V.VW, V.VH, V.FPS, V.IW, V.IH
SR = 48000
TL = {e["id"]: e for e in V.TL}
KEY = V.F("Anton-Regular.ttf", 138)
FOOT = V.F("Anton-Regular.ttf", 40)


def keyword(im, text, k):
    d = ImageDraw.Draw(im)
    size = 112
    while size > 60 and d.textlength(text, font=V.F("Anton-Regular.ttf", size)) > 960:
        size -= 6
    f = V.F("Anton-Regular.ttf", size)
    y = 528
    d.text((VW / 2, y), text, font=f, fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=(0, 0, 0))
    w = d.textlength(text, font=f)


segs = []
for b in BEATS:
    p = b.split(":")
    e = TL[p[0]]
    mx = float(p[2]) if len(p) > 2 else 99
    t0 = e["start"] + (0.45 if e["start"] > 0 else 0)
    t1 = min(e["end"] - 0.1, t0 + mx)
    segs.append((t0, t1, p[1]))

# audio: the film's own stems, only the chosen stretches, music kept low
vo = [sf.read(os.path.join(BUILD, f"stem_{n}.wav"), dtype="float32") for n in ("voice", "sfx", "music")]
mix = vo[0][0] + 0.6 * vo[1][0] + 0.12 * vo[2][0]
if mix.ndim > 1:
    mix = mix.mean(1)
sr_in = vo[0][1]
parts = []
for t0, t1, _ in segs:
    a = mix[int(t0 * sr_in):int(t1 * sr_in)].copy()
    n = int(0.03 * sr_in)
    a[:n] *= np.linspace(0, 1, n)
    a[-n:] *= np.linspace(1, 0, n)
    parts.append(a)
wav = OUT + ".wav"
sf.write(wav, np.concatenate(parts), sr_in)

enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}", "-r", str(FPS), "-i", "-",
                        "-i", wav, "-af", "loudnorm=I=-14:TP=-1.5", "-c:v", "libx264", "-preset", "medium", "-b:v", "2200k", "-maxrate", "2800k",
                        "-bufsize", "5000k", "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1", "-c:a", "aac", "-b:a", "128k",
                        "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
n = IW * IH * 3
for t0, t1, kw in segs:
    V.T0 = t0
    dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-i", os.path.join(BUILD, "picture.mp4"),
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    i = 0
    while True:
        fr = dec.stdout.read(n)
        if len(fr) < n:
            break
        im = Image.frombytes("RGB", (VW, VH), V.compose(fr, i))
        keyword(im, kw, i / FPS)
        ImageDraw.Draw(im).text((VW / 2, 1840), "MR MONEY  ·  FULL DOCUMENTARY", font=FOOT, fill=(235, 235, 235), anchor="mm")
        enc.stdin.write(im.tobytes())
        i += 1
enc.stdin.close()
enc.wait()
os.remove(wav)
print("hook done", OUT, round(sum(b - a for a, b, _ in segs), 1), "s")
