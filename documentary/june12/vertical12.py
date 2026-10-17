"""June 12 version: compose a rendered 16:9 short into a 9:16 Reel: blurred backdrop, framed video, headline,
and big word-by-word captions (spoken word highlighted).

usage: SHORT=who [PLATFORM=tiktok] python3 vertical.py BUILD_DIR OUT.mp4

If BUILD_DIR/loop.json exists (see loopfix.py) the video is rotated to start at the loop phrase,
so the loop seam sits inside one spoken sentence.
PLATFORM=tiktok keeps headline and captions clear of TikTok's top tabs, side buttons and caption area.
"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import visuals as V
import engine12 as E
from shorts12 import HEADLINE

BUILD, OUT = sys.argv[1], sys.argv[2]
FPS = E.FPS
VW, VH = 1080, 1920
IW, IH = 1280, 720
TL, TOTAL = E.TL, E.TOTAL
HEAD = HEADLINE
TIKTOK = True
HEAD_Y = 290 if TIKTOK else 215          # TikTok's Following / For You tabs sit at the top
CAP_CX = 500 if TIKTOK else VW / 2      # keep captions left of TikTok's like / share column
CAP_MAXW = 820 if TIKTOK else VW - 90
VID_Y = 560 if TIKTOK else 500
TV = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                    f"{BUILD}/picture.mp4"]))
_hook = next(e for e in TL if e["id"] == "hook")
R = _hook["start"] + _hook["voice_at"] - 0.12   # the video opens on the hook line and loops back into it

# word timings: spread each subtitle chunk's time across its words by length
WORDS = []
for e in TL:
    for a0, a1, s in [(e["start"] + x, e["start"] + y, E.show(z)) for x, y, z in e.get("subs") or []]:
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
    for a0, a1, s in [(e["start"] + x, e["start"] + y, E.show(z)) for x, y, z in e.get("subs") or []]:
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
        y = HEAD_Y + i * 115
        size = 92
        while size > 56 and d.textlength(txt, font=V.F(size, "Black")) > 900:   # keep a safe margin at both edges
            size -= 4
        d.text((VW / 2, y), txt, font=V.F(size, "Black"), fill=col + (255,), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0, 255))
    if not TIKTOK:  # TikTok covers the bottom with its own caption / username
        d.text((VW / 2, 1810), "JAGABAN  ·  FULL DOCUMENTARY", font=F_TAG, fill=(230, 220, 200, 200), anchor="mm")
    return im


HEADL = headline_layer()


def caption(t):
    line = next((ln for ln in reversed(LINES) if ln and ln[0][0] - 0.05 <= t < ln[-1][1] + 0.15), None)
    if not line:
        return None
    im = Image.new("RGBA", (VW, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    words = [w for _, _, w in line]
    gap = 28
    base = sum(d.textlength(w.upper(), font=F_CAP) for w in words) + gap * (len(words) - 1)
    scale = min(1.0, CAP_MAXW / max(base, 1))
    fonts = []
    for w0, w1, w in line:
        active = w0 <= t < w1 + 0.05
        fonts.append((V.F(int(86 * scale * (1.1 if active else 1.0)), "Black"), active))
    widths = [d.textlength(w.upper(), font=f) for w, (f, _) in zip(words, fonts)]
    total = sum(widths) + gap * scale * (len(words) - 1)
    x = CAP_CX - total / 2
    for w, (font, active), wd in zip(words, fonts, widths):
        col = (255, 214, 64) if active else (255, 255, 255)
        d.text((x, 130), w.upper(), font=font, fill=col + (255,), anchor="lm", stroke_width=7, stroke_fill=(0, 0, 0, 255))
        x += wd + gap * scale
    return im


def compose(fr, i):
    t_out = i / FPS
    t = (t_out + R) % TV  # source time (rotated loops start at the loop phrase)
    src = Image.frombytes("RGB", (IW, IH), fr)
    bg = src.resize((54, 96), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3)).resize((VW, VH), Image.BICUBIC)
    bg = Image.blend(bg, Image.new("RGB", (VW, VH), (0, 0, 0)), 0.5)
    cw = IH * 4 // 3  # 4:3 centre crop: bigger picture on a phone
    vid = src.crop(((IW - cw) // 2, 0, (IW + cw) // 2, IH)).resize((VW, VW * 3 // 4), Image.LANCZOS)
    y0 = VID_Y
    bg.paste(vid, (0, y0))
    canvas = bg.convert("RGBA")
    d = ImageDraw.Draw(canvas)
    d.line([0, y0 - 3, VW, y0 - 3], fill=V.GOLD + (255,), width=4)
    d.line([0, y0 + vid.height + 2, VW, y0 + vid.height + 2], fill=V.GOLD + (255,), width=4)
    if t_out < 0.5:  # headline punches in on the first frames
        sc = 1.0 + 0.2 * np.exp(-t_out * 11)
        top = HEADL.crop((0, 0, VW, 540))
        big = top.resize((int(VW * sc), int(540 * sc)), Image.BILINEAR)
        layer = Image.new("RGBA", (VW, VH), (0, 0, 0, 0))
        cy = HEAD_Y + 57
        big = big.crop((max(0, (big.width - VW) // 2), max(0, int(cy * sc - cy)), max(0, (big.width - VW) // 2) + VW,
                        max(0, int(cy * sc - cy)) + 540))
        layer.alpha_composite(big, (0, 0))
        layer.alpha_composite(HEADL.crop((0, 540, VW, VH)), (0, 540))
        canvas = Image.alpha_composite(canvas, layer)
    else:
        canvas = Image.alpha_composite(canvas, HEADL)
    cap = caption(t)
    if cap is not None:
        canvas.alpha_composite(cap, (0, y0 + vid.height + 40))
    return canvas.convert("RGB").tobytes()


def main():
    def decoder(ss=None, to=None):
        cmd = ["ffmpeg", "-loglevel", "error"]
        if ss is not None:
            cmd += ["-ss", f"{ss:.3f}"]
        if to is not None:
            cmd += ["-t", f"{to:.3f}"]
        return cmd + ["-i", f"{BUILD}/picture.mp4", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    parts = [decoder(R, None), decoder(None, R)] if R > 0 else [decoder()]
    afilter = (f"[1:a]atrim=start={R:.3f}:end={TV:.3f},asetpts=PTS-STARTPTS,afade=t=out:st={TV - R - 0.25:.3f}:d=0.25[a1];"
               f"[1:a]atrim=end={R:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.25[a2];"
               f"[a1][a2]concat=n=2:v=0:a=1,loudnorm=I=-14:TP=-1.5:LRA=11[a]") if R > 0 else \
        "[1:a]atrim=end=%.3f,loudnorm=I=-14:TP=-1.5:LRA=11[a]" % TV
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{VW}x{VH}", "-r", str(FPS), "-i", "-", "-i", f"{BUILD}/mix.wav",
                            "-filter_complex", afilter, "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "medium",
                            "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest",
                            "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    n = IW * IH * 3
    i = 0
    for cmd in parts:
        dec = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        while True:
            fr = dec.stdout.read(n)
            if len(fr) < n:
                break
            enc.stdin.write(compose(fr, i))
            i += 1
        dec.wait()
    enc.stdin.close()
    enc.wait()
    print("vertical done", i, "frames")


if __name__ == "__main__":
    main()
