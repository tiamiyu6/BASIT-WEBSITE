"""WHAT IF YOU WOKE UP AS AFRICA'S BIGGEST SUPERSTAR: full film from SUPERSTAR_SCRIPT.md + 23 paper-cut illustrations.

usage (from documentary/):  python3 superstar/superstar_full.py MODELS_DIR IMG_DIR BUILD_DIR OUT.mp4   (NARRATE_ONLY=1 makes just the voice)
IMG_DIR holds 01.png ... 23.png (see SUPERSTAR_IMAGE_PROMPTS.md).
"""
import json, os, re, subprocess, sys
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PSY = os.path.join(os.path.dirname(HERE), "psych")
sys.path.insert(0, os.path.dirname(HERE))

MODELS, IMGS, BUILD, OUT = sys.argv[1:5]
os.makedirs(BUILD, exist_ok=True)
W, H, FPS, SR = 1920, 1080, 30, 24000
VOICE = os.environ.get("VOICE", "am_michael")
GREEN = (61, 235, 61)
CREAM, INK = (244, 232, 208), (40, 30, 25)

# picture number -> script lines it covers (SUPERSTAR_IMAGE_PROMPTS.md)
PICS = [(1, [1, 2]), (2, [3]), (3, [4]), "TITLE", 'CH:CHAPTER 1|THE MORNING', (4, [5]), (5, [6]), (6, [7, 8]), (7, [9]), 'CH:CHAPTER 2|THE PHONE', (8, [10]), (9, [11, 12]), (10, [13]), (11, [14]), (12, [15, 16]), 'CH:CHAPTER 3|THE CHOICE', (13, [17]), (14, [18]), (15, [19, 20]), (16, [21]), 'CH:CHAPTER 4|THE LESSON', (17, [22]), (18, [23, 24]), (19, [25]), (20, [26]), (21, [27]), 'CH:ENDING|', (22, [28, 29]), (23, [30]), "END"]
LABELS = {}
SAY = {"artiste": "ar-teest", "naira": "nye-rah"}
EDIT = {}


def script_lines():
    out = {}
    for m in re.finditer(r"^(\d+)\. \*\*(.*)\*\*\s*$", open(os.path.join(HERE, "SUPERSTAR_SCRIPT.md")).read(), re.M):
        t = m.group(2).replace("⚠", "").replace("—", ",").replace(" ,", ",").strip()
        out[int(m.group(1))] = t
    out.update(EDIT)
    return out


def narrate(lines):
    meta = os.path.join(BUILD, "voice.json")
    key = [lines, VOICE]
    if os.path.exists(meta) and json.load(open(meta))["key"] == key:
        return json.load(open(meta))["items"], os.path.join(BUILD, "voice")
    import narrate as N
    from kokoro_onnx import Kokoro
    from faster_whisper import WhisperModel
    os.makedirs(os.path.join(BUILD, "voice"), exist_ok=True)
    k = Kokoro(os.path.join(MODELS, "kokoro.onnx"), os.path.join(MODELS, "voices.bin"))
    wm = WhisperModel("small", device="cpu", compute_type="int8")
    items = {}
    for n, text in lines.items():
        spoken = text
        for a, b in SAY.items():
            spoken = spoken.replace(a, b)
        a, _ = k.create(spoken, voice=VOICE, speed=0.92, lang="en-us")
        a = N.trim(a)
        a = N.CHAIN(a[None, :], SR)[0]
        sf.write(os.path.join(BUILD, "voice", f"{n:02d}.wav"), a, SR)
        d = len(a) / SR
        a16 = np.interp(np.arange(0, len(a), SR / 16000), np.arange(len(a)), a).astype(np.float32)
        segs, _ = wm.transcribe(a16, language="en", word_timestamps=True)
        ww = [(w.start, w.end) for g in segs for w in g.words]
        words = text.split()
        if ww:
            times = [ww[min(len(ww) - 1, int(i * len(ww) / len(words)))] for i in range(len(words))]
        else:
            times = [(d * i / len(words), d * (i + 1) / len(words)) for i in range(len(words))]
        items[n] = dict(text=text, dur=d, words=[(w, s0, s1) for w, (s0, s1) in zip(words, times)])
        print("voice", n, round(d, 1), flush=True)
    json.dump(dict(key=key, items=items), open(meta, "w"))
    return items, os.path.join(BUILD, "voice")


CAP = ImageFont.truetype(os.path.join(PSY, "fonts", "LilitaOne-Regular.ttf"), 78)
CAPB = ImageFont.truetype(os.path.join(PSY, "fonts", "LilitaOne-Regular.ttf"), 96)
BIG = ImageFont.truetype(os.path.join(PSY, "fonts", "LilitaOne-Regular.ttf"), 150)
MID = ImageFont.truetype(os.path.join(PSY, "fonts", "LilitaOne-Regular.ttf"), 64)
LAB = ImageFont.truetype(os.path.join(PSY, "fonts", "LilitaOne-Regular.ttf"), 58)


def chunks(words):
    out, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == 3 or w[0].endswith((".", ",", "?", ":")):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def caption(img, words, t):
    for ch in chunks(words):
        if ch[0][1] - 0.05 <= t < ch[-1][2] + 0.15:
            break
    else:
        return
    d = ImageDraw.Draw(img)
    items = []
    for w, a, b in ch:
        on = a <= t < b + 0.08 or (w is ch[-1][0] and t >= a)
        items.append((w.upper().strip(".,?:;"), CAPB if on else CAP, GREEN if on else (255, 255, 255)))
    gap = 22
    widths = [d.textlength(s, font=f) for s, f, _ in items]
    x = W / 2 - (sum(widths) + gap * (len(items) - 1)) / 2
    y = H - 110
    for (s, f, c), wd in zip(items, widths):
        d.text((x + 5, y + 6), s, font=f, fill=INK, anchor="ls", stroke_width=8, stroke_fill=INK)
        d.text((x, y), s, font=f, fill=c, anchor="ls", stroke_width=7, stroke_fill=(35, 28, 24))
        x += wd + gap


def label(img, text, a):
    d = ImageDraw.Draw(img)
    wd = d.textlength(text, font=LAB) + 70
    x0, y0 = 70, 70
    s = Image.new("RGBA", (int(wd), 96), (0, 0, 0, 0))
    sd = ImageDraw.Draw(s)
    sd.rounded_rectangle((0, 0, wd, 96), 22, fill=CREAM + (int(235 * a),), outline=INK + (int(255 * a),), width=5)
    sd.text((35, 68), text, font=LAB, fill=INK + (int(255 * a),), anchor="ls")
    img.paste(s, (x0, y0), s)


def card(kind, p):
    """title / chapter / end cards on a cream paper background, p = 0..1 progress."""
    im = Image.new("RGB", (W, H), CREAM)
    rng = np.random.default_rng(5)
    g = (rng.standard_normal((H // 3, W // 3)) * 7).astype(np.int16)
    arr = np.clip(np.asarray(im).astype(np.int16) + np.kron(g, np.ones((3, 3), np.int16))[:H, :W, None], 0, 255).astype(np.uint8)
    im = Image.fromarray(arr)
    d = ImageDraw.Draw(im)
    a, b = kind
    c = lambda y, s, f, col=INK: d.text((W / 2, y), s, font=f, fill=col, anchor="mm")
    if a == "TITLE":
        c(380, "WHAT IF YOU WOKE UP AS", BIG)
        c(540, "AFRICA'S BIGGEST STAR?", BIG, (200, 90, 50))
        c(700, "A STORY FROM THE TOP", MID, (60, 120, 110))
        c(810, "NAIJA UNTOLD", MID, INK)
    elif a == "CH":
        top, name = b.split("|")
        if name:
            c(470, top, MID, (60, 120, 110))
            c(610, name, BIG)
        else:
            c(540, top, BIG)
    else:
        c(430, "WHAT WOULD YOU", BIG)
        c(580, "DO FIRST?", BIG, (200, 90, 50))
        c(760, "TELL US IN THE COMMENTS", MID, (60, 120, 110))
    return im


def music(dur):
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros(len(t))
    chords = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 55, 60, 64], [55, 59, 62, 67]]
    beat = 60 / 72
    k = 0
    while k * beat * 4 < dur:
        ch = chords[k % 4]
        for j, m in enumerate(ch + [ch[2] + 12]):
            st = k * beat * 4 + j * beat * 0.75
            n = int(min(3.5, dur - st) * SR)
            if n <= 0:
                continue
            tt = np.arange(n) / SR
            f = 440 * 2 ** ((m - 69) / 12)
            note = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt * 1.6)
            i = int(st * SR)
            out[i:i + n] += note[:len(out) - i] * 0.6
        k += 1
    out = out / (np.abs(out).max() + 1e-9) * 0.05
    return out * np.minimum(1, t / 2) * np.minimum(1, (dur - t) / 3)


def whoosh():
    from scipy.signal import lfilter
    n = int(0.5 * SR)
    x = lfilter([0.05], [1, -0.95], np.random.default_rng(3).standard_normal(n))
    return x * np.sin(np.pi * np.arange(n) / n) ** 2 * 0.22


def main():
    lines = script_lines()
    items, vdir = narrate(lines)
    if os.environ.get("NARRATE_ONLY"):
        print("NARRATION DONE")
        return
    # timeline: segments with start/end and (for pictures) the words and labels
    GAP, PAUSE = 0.5, 0.35
    t, segs, voice_clips = 0.8, [], []
    for s in PICS:
        if isinstance(s, str) or isinstance(s[0], str):
            kind = (s.split(":")[0], s.split(":", 1)[1] if ":" in s else "") if isinstance(s, str) else s
            dur = {"TITLE": 3.6, "CH": 2.4, "END": 6.0}[kind[0]]
            segs.append(dict(kind=kind, t0=t, t1=t + dur))
            t += dur
            continue
        pic, nums = s
        t0, words, labs = t, [], []
        for n in nums:
            it = items[str(n)] if str(n) in items else items[n]
            words += [(w, t + a, t + b) for w, a, b in it["words"]]
            if n in LABELS:
                labs.append((LABELS[n], t, t + it["dur"] + 0.6))
            voice_clips.append((t, os.path.join(vdir, f"{n:02d}.wav")))
            t += it["dur"] + GAP
        t -= GAP - PAUSE
        segs.append(dict(kind="PIC", pic=pic, t0=t0, t1=t, words=words, labels=labs))
    total = t + 1.2
    # audio
    mix = np.zeros(int(total * SR))
    for st, p in voice_clips:
        a, _ = sf.read(p, dtype="float32")
        i = int(st * SR)
        mix[i:i + len(a)] += a[:len(mix) - i]
    mix += music(total)
    for sg in segs[1:]:
        i = int((sg["t0"] - 0.25) * SR)
        w = whoosh()
        mix[i:i + len(w)] += w[:len(mix) - i]
    sf.write(os.path.join(BUILD, "mix.wav"), np.clip(mix, -1, 1), SR)
    imgs = {}
    for sg in segs:
        if sg["kind"] == "PIC" and sg["pic"] not in imgs:
            imgs[sg["pic"]] = Image.open(os.path.join(IMGS, f"{sg['pic']:02d}.png")).convert("RGB")
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-i", os.path.join(BUILD, "mix.wav"), "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
                            "-af", "loudnorm=I=-14:TP=-1.5", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    cache = {}
    for f in range(int(total * FPS)):
        tt = f / FPS
        k = max([i for i, sg in enumerate(segs) if sg["t0"] - 0.25 <= tt] or [0])
        sg = segs[k]
        p = min(1, max(0, (tt - sg["t0"]) / max(0.5, sg["t1"] - sg["t0"])))
        if sg["kind"] == "PIC":
            src = imgs[sg["pic"]]
            sw, sh = src.size
            z = 1.0 + 0.06 * p
            bw = sw / z
            bh = bw * H / W
            dx = (sw - bw) * (0.3 + 0.4 * p if k % 2 else 0.7 - 0.4 * p)
            dy = (sh - bh) / 2
            img = src.resize((W, H), Image.BICUBIC, box=(dx, dy, dx + bw, dy + bh))
            caption(img, sg["words"], tt)
            for text, a, b in sg["labels"]:
                if a <= tt < b:
                    label(img, text, min(1, (tt - a) / 0.3, (b - tt) / 0.3))
        else:
            kk = sg["kind"]
            base = cache.setdefault(kk, card(kk, 0))
            img = base
            if tt - sg["t0"] < 0.3 and tt >= sg["t0"]:
                img = Image.blend(Image.new("RGB", (W, H), CREAM), base, (tt - sg["t0"]) / 0.3)
        enc.stdin.write(img.tobytes())
    enc.stdin.close()
    enc.wait()
    print("JAPA DONE", round(total, 1), "s", OUT)


if __name__ == "__main__":
    main()
