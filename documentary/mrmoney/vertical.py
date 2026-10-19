"""Cut a 9:16 TikTok/Reels clip out of the finished Mr Money film.

The music is kept very low on purpose: add the real Asake song from TikTok's own (licensed) sound library at ~20%.
usage (from documentary/):  python3 mrmoney/vertical.py BUILD START END "HEADLINE 1" "HEADLINE 2" OUT.mp4
"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BUILD, T0, T1, H1, H2, OUT = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5], sys.argv[6]
HERE = os.path.dirname(os.path.abspath(__file__))
VW, VH, FPS = 1080, 1920, 30
IW, IH = 1920, 1080
CW = 1600                                   # centre crop of the 16:9 frame (keeps the graphics' text)
GOLD, CREAM = (232, 184, 74), (245, 238, 224)
F = lambda n, s: ImageFont.truetype(os.path.join(HERE, "fonts", n), s)
TL = json.load(open(os.path.join(BUILD, "timeline.json")))

# word timings from the narration subtitles
WORDS = []
for e in TL:
    for a0, a1, s in e.get("subs") or []:
        a0, a1 = e["start"] + a0, e["start"] + a1
        ws = s.split()
        tot = sum(len(w) + 1 for w in ws)
        t = a0
        for w in ws:
            d = (a1 - a0) * (len(w) + 1) / tot
            WORDS.append((t, t + d, w))
            t += d
LINES = []
cur = []
for w in WORDS:
    cur.append(w)
    if len(cur) == 3 or w[2].endswith((".", ",", "?")):
        LINES.append(cur)
        cur = []
if cur:
    LINES.append(cur)


def headline():
    im = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, (txt, col) in enumerate(((H1, CREAM), (H2, GOLD))):
        size = 110
        while size > 50 and d.textlength(txt, font=F("Anton-Regular.ttf", size)) > 940:
            size -= 4
        d.text((VW / 2, 300 + i * 130), txt, font=F("Anton-Regular.ttf", size), fill=col, anchor="mm",
               stroke_width=6, stroke_fill=(0, 0, 0))
    return im


HEAD = headline()
FCAP = F("Anton-Regular.ttf", 92)


def caption(t):
    ln = next((l for l in LINES if l[0][0] - 0.05 <= t < l[-1][1] + 0.12), None)
    if not ln:
        return None
    im = Image.new("RGBA", (VW, 220), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    words = [w for _, _, w in ln]
    gap = 26
    widths = [d.textlength(w.upper(), font=FCAP) for w in words]
    total = sum(widths) + gap * (len(words) - 1)
    sc = min(1.0, 900 / total)
    f = F("Anton-Regular.ttf", int(92 * sc))
    widths = [d.textlength(w.upper(), font=f) for w in words]
    x = VW / 2 - (sum(widths) + gap * sc * (len(words) - 1)) / 2
    for (w0, w1, w), wd in zip(ln, widths):
        on = w0 <= t < w1 + 0.05
        d.text((x, 110), w.upper(), font=f, fill=GOLD if on else (255, 255, 255), anchor="lm", stroke_width=7, stroke_fill=(0, 0, 0))
        x += wd + gap * sc
    return im


def compose(fr, i):
    t = T0 + i / FPS
    src = Image.frombytes("RGB", (IW, IH), fr)
    bg = src.resize((96, 54), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2)).resize((VW * 2, VH), Image.BICUBIC)
    bg = bg.crop((VW // 2, 0, VW // 2 + VW, VH))
    bg = Image.blend(bg, Image.new("RGB", (VW, VH), (0, 0, 0)), 0.55)
    vid = src.crop(((IW - CW) // 2, 0, (IW + CW) // 2, IH)).resize((VW, int(VW * IH / CW)), Image.LANCZOS)
    y0 = 600
    bg.paste(vid, (0, y0))
    c = bg.convert("RGBA")
    d = ImageDraw.Draw(c)
    d.line([0, y0 - 3, VW, y0 - 3], fill=GOLD, width=4)
    d.line([0, y0 + vid.height + 2, VW, y0 + vid.height + 2], fill=GOLD, width=4)
    k = i / FPS
    if k < 0.45:
        s = 1 + 0.25 * np.exp(-k * 10)
        h = HEAD.resize((int(VW * s), int(VH * s)), Image.BILINEAR)
        c.alpha_composite(h.crop(((h.width - VW) // 2, int(360 * s - 360), (h.width - VW) // 2 + VW, int(360 * s - 360) + VH)))
    else:
        c.alpha_composite(HEAD)
    cap = caption(t)
    if cap:
        c.alpha_composite(cap, (0, y0 + vid.height + 50))
    return c.convert("RGB").tobytes()


def main():
    dur = T1 - T0
    vo = os.path.join(BUILD, "stem_voice.wav")
    fx = os.path.join(BUILD, "stem_sfx.wav")
    mu = os.path.join(BUILD, "stem_music.wav")
    af = (f"[1:a]atrim={T0}:{T1},asetpts=PTS-STARTPTS[v];[2:a]atrim={T0}:{T1},asetpts=PTS-STARTPTS,volume=0.6[x];"
          f"[3:a]atrim={T0}:{T1},asetpts=PTS-STARTPTS,volume=0.35[m];[v][x][m]amix=inputs=3:normalize=0,"
          f"afade=t=in:d=0.15,afade=t=out:st={dur - 0.4}:d=0.4,loudnorm=I=-14:TP=-1.5[a]")
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}",
                            "-r", str(FPS), "-i", "-", "-i", vo, "-i", fx, "-i", mu, "-filter_complex", af, "-map", "0:v", "-map", "[a]",
                            "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest",
                            "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-ss", f"{T0:.3f}", "-t", f"{dur:.3f}", "-i",
                            os.path.join(BUILD, "picture.mp4"), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
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
    print("vertical done", OUT, i)


if __name__ == "__main__":
    main()
