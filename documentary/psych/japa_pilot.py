"""THE PSYCHOLOGY OF JAPA: 60-second pilot in the hand-drawn psychology-explainer format.

One drawing per line, a calm narrator, 3-word karaoke captions with the spoken word in green.
usage (from documentary/):  python3 psych/japa_pilot.py MODELS_DIR BUILD_DIR OUT.mp4
"""
import json, math, os, subprocess, sys
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from sketch import Sketch, PW, PH, LEAD, SKIN, capsule, rect, rot_rect

MODELS, BUILD, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(BUILD, exist_ok=True)
W, H, FPS, SR = 1920, 1080, 30, 24000
VOICE = os.environ.get("VOICE", "am_michael")
GREEN = (61, 235, 61)
SKIN2 = (176, 140, 110)


# ------------------------------------------------------------------ the drawings
def sc_money(S):
    S.ground(1100)
    p = S.person(1120, 1100, h=560, mood="worried", look=1, arms=("down", "hold"))
    S.note(1330, 690, s=1.1, angle=-12)
    S.text((1480, 360), "?", size=200)


def sc_unsaid(S):
    S.ground(1100)
    S.person(900, 1100, h=560, mood="sad", arms=("down", "chin"))
    S.bubble(1430, 470, 420, 260)
    S.text((1430, 470), ". . .", size=150)


def sc_degree(S):
    S.ground(1100)
    p = S.person(820, 1100, h=560, mood="worried", look=1, arms=("down", "out"))
    S.cap(p["head"][0], p["top"] + 10, s=1.15)
    S.calendar(1440, 640, s=1.5, crossed=17)
    S.text((1440, 900), "plan: still loading...", size=70)


def sc_airport_post(S):
    S.ground(1150)
    S.person(700, 1150, h=500, mood="sad", look=1, arms=("down", "hold"))
    x, y = 1350, 620
    S.shape(rect(x - 230, y - 420, 460, 840, 50), (95, 95, 105), hatch=False)
    S.shape(rect(x - 200, y - 380, 400, 700, 20), (200, 225, 245), hatch=False)
    S.plane(x, y - 120, s=0.85)
    for k, (hx, hy) in enumerate(((x - 120, y + 180), (x, y + 210), (x + 120, y + 170))):
        heart(S, hx, hy, 34)
    S.text((x, y + 290), "new chapter ✈", size=60)


def sc_three(S):
    S.ground(1080)
    for x, tag, col in ((620, "CANADA", (175, 70, 60)), (1120, "UK", (70, 95, 150)), (1620, "GERMANY", (90, 120, 80))):
        S.suitcase(x, 1080, s=1.5, color=col, tag=tag)


def sc_voice(S):
    S.ground(1100)
    S.person(880, 1100, h=520, mood="worried", look=1, arms=("down", "down"), legs="sit")
    S.bubble(1450, 420, 520, 260, tail=(-1, 1), think=True)
    S.text((1450, 420), "why not me?", size=110)


def sc_japa(S):
    S.ground(1100)
    S.text((1120, 330), "JAPA", size=260)
    S.text((1120, 500), "(Yoruba: to run)", size=80)
    S.person(1000, 1100, h=470, mood="neutral", look=1, arms=("down", "out"), legs="walk", lean=0.25)
    S.suitcase(1240, 1100, s=1.0, color=(175, 70, 60))
    for k in range(3):
        S.line([(700 - k * 10, 800 + k * 70), (800 - k * 10, 800 + k * 70)], width=4, passes=1)


def sc_complicated(S):
    S.ground(1100)
    p = S.person(1120, 1100, h=520, mood="worried", arms=("face", "face"))
    S.scribble(1120, 420, r=200)


def sc_not_nothing(S):
    S.ground(1100)
    S.person(1120, 1100, h=560, mood="neutral", look=-1, arms=("hold", "down"))
    S.passport(900, 760, s=1.3)
    S.suitcase(1380, 1100, s=1.1, color=(70, 95, 150))
    S.text((1120, 300), "degrees · skills · savings", size=80)


def sc_professions(S):
    S.ground(1120)
    S.plane(1120, 240, s=1.2)
    for x, kind in ((620, "nurse"), (1120, "doctor"), (1620, "engineer")):
        p = S.person(x, 1120, h=480, mood="neutral", look=0, arms=("down", "down"))
        hx, top, s = p["head"][0], p["top"], p["s"]
        if kind == "nurse":
            S.shape([(hx - 50 * s, top + 22 * s), (hx - 40 * s, top - 26 * s), (hx + 40 * s, top - 26 * s), (hx + 50 * s, top + 22 * s)], (245, 245, 245), hatch=False)
            S.line([(hx - 10, top - 6 * s), (hx + 10, top - 6 * s)], width=5, color=(200, 60, 60), passes=1)
            S.line([(hx, top - 16 * s), (hx, top + 4 * s)], width=5, color=(200, 60, 60), passes=1)
        elif kind == "doctor":
            S.line([(hx - 40 * s, top + 150 * s), (hx - 30 * s, top + 230 * s), (hx, top + 260 * s), (hx + 30 * s, top + 230 * s), (hx + 40 * s, top + 150 * s)], width=5, passes=1)
            S.shape([(hx + c * 0 + 20 * math.cos(t), top + 270 * s + 20 * math.sin(t)) for c in [0] for t in np.linspace(0, 6.3, 20)], (160, 160, 170), hatch=False)
        else:
            S.shape([(hx - 78 * s, top + 40 * s), (hx - 70 * s, top - 10 * s), (hx, top - 30 * s), (hx + 70 * s, top - 10 * s), (hx + 78 * s, top + 40 * s)], (240, 190, 60))
    S.text((620, 1190), "nurses", size=70)
    S.text((1120, 1190), "doctors", size=70)
    S.text((1620, 1190), "engineers", size=70)


def sc_mind(S):
    S.ground(1100)
    S.door(1450, 1100, s=1.4)
    S.person(900, 1100, h=520, mood="neutral", look=1, arms=("down", "down"))
    S.text((1450, 420), "?", size=160, color=(200, 160, 60))


def sc_stay(S):
    S.ground(1100)
    S.plane(1600, 320, s=0.9)
    for k in range(4):
        S.line([(1360 - k * 70, 360 + k * 26), (1400 - k * 70, 350 + k * 26)], width=3, passes=1, alpha=150)
    S.person(800, 1100, h=520, mood="sad", look=1, arms=("down", "wave"))
    S.text((800, 300), "and the ones who stay...?", size=90)


def heart(S, x, y, r):
    pts = [(x + r * 16 * math.sin(t) ** 3 / 16, y - r * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16) for t in np.linspace(0, 6.28, 40)]
    S.shape(pts, (225, 90, 90), hatch=False)


LINES = [
    ("What if leaving Nigeria isn't really about money?", sc_money, "money"),
    ("What if it's about something much harder to say out loud?", sc_unsaid, "harder"),
    ("You're twenty-six. You have a degree, and a plan that keeps getting delayed.", sc_degree, "delayed"),
    ("Every week, someone you know posts a picture from an airport.", sc_airport_post, "airport"),
    ("Canada. The UK. Germany.", sc_three, None),
    ("And every time, a small voice asks... why not you?", sc_voice, "you"),
    ("They call it japa. In Yoruba, it means to run.", sc_japa, "japa"),
    ("But here's where things get complicated.", sc_complicated, "complicated"),
    ("The ones leaving are often not the ones with nothing.", sc_not_nothing, "nothing"),
    ("They're nurses. Doctors. Engineers. The people a country needs most.", sc_professions, "most"),
    ("So what is really happening inside the mind of someone who decides to go?", sc_mind, "mind"),
    ("And what happens to the ones who stay?", sc_stay, "stay"),
]
SAY = {"japa": "jah-pah", "Japa": "Jah-pah", "Yoruba": "Yoruba"}


# ------------------------------------------------------------------ voice + word timing
def narrate():
    from kokoro_onnx import Kokoro
    import narrate as N
    meta = os.path.join(BUILD, "voice.json")
    key = [[l[0] for l in LINES], VOICE]
    if os.path.exists(meta) and json.load(open(meta))["key"] == key:
        return json.load(open(meta))["lines"]
    k = Kokoro(os.path.join(MODELS, "kokoro.onnx"), os.path.join(MODELS, "voices.bin"))
    from faster_whisper import WhisperModel
    wm = WhisperModel("small", device="cpu", compute_type="int8")
    out, pieces, t = [], [], 0.6
    pieces.append(np.zeros(int(0.6 * SR), np.float32))
    for text, _, kw in LINES:
        spoken = text
        for a, b in SAY.items():
            spoken = spoken.replace(a, b)
        a, _ = k.create(spoken, voice=VOICE, speed=0.92, lang="en-us")
        a = N.trim(a)
        d = len(a) / SR
        # word timings: align the known words to whisper's timestamps
        a16 = np.interp(np.arange(0, len(a), SR / 16000), np.arange(len(a)), a).astype(np.float32)
        segs, _ = wm.transcribe(a16, language="en", word_timestamps=True)
        ww = [(w.start, w.end) for g in segs for w in g.words]
        words = text.split()
        if len(ww) >= 1:
            times = [ww[min(len(ww) - 1, int(i * len(ww) / len(words)))] for i in range(len(words))]
        else:
            times = [(d * i / len(words), d * (i + 1) / len(words)) for i in range(len(words))]
        out.append(dict(text=text, kw=kw, t0=t, t1=t + d, words=[(w, t + s0, t + s1) for w, (s0, s1) in zip(words, times)]))
        pieces += [a, np.zeros(int(0.55 * SR), np.float32)]
        t += d + 0.55
    audio = np.concatenate(pieces)
    audio = N.CHAIN(audio[None, :], SR)[0]
    sf.write(os.path.join(BUILD, "voice.wav"), audio, SR)
    json.dump(dict(key=key, lines=out), open(meta, "w"))
    return out


# ------------------------------------------------------------------ captions (3-word karaoke, spoken word in green)
CAP = ImageFont.truetype(os.path.join(HERE, "fonts", "LilitaOne-Regular.ttf"), 78)
CAPB = ImageFont.truetype(os.path.join(HERE, "fonts", "LilitaOne-Regular.ttf"), 96)


def chunks(words):
    out, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == 3 or w[0].endswith((".", ",", "?")):
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
        f = CAPB if on else CAP
        txt = w.upper().strip(".,?")
        items.append((txt, f, GREEN if on else (255, 255, 255)))
    gap = 22
    widths = [d.textlength(s, font=f) for s, f, _ in items]
    x = W / 2 - (sum(widths) + gap * (len(items) - 1)) / 2
    y = H - 135
    for (s, f, c), wd in zip(items, widths):
        d.text((x + 5, y + 6), s, font=f, fill=(40, 30, 25), anchor="ls", stroke_width=8, stroke_fill=(40, 30, 25))   # drop shadow
        d.text((x, y), s, font=f, fill=c, anchor="ls", stroke_width=7, stroke_fill=(35, 28, 24))
        x += wd + gap


# ------------------------------------------------------------------ music: soft felt piano + air
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
    out = out / (np.abs(out).max() + 1e-9) * 0.06
    fade = np.minimum(1, t / 1.5) * np.minimum(1, (dur - t) / 2.0)
    return out * fade


def whoosh_soft():
    n = int(0.5 * SR)
    x = np.random.default_rng(3).standard_normal(n)
    from scipy.signal import lfilter
    x = lfilter([0.05], [1, -0.95], x)
    return x * np.sin(np.pi * np.arange(n) / n) ** 2 * 0.25


def main():
    lines = narrate()
    total = lines[-1]["t1"] + 1.6
    # drawings (cached)
    plates = []
    for i, (_, fn, _) in enumerate(LINES):
        path = os.path.join(BUILD, f"plate_{i:02d}.png")
        if not os.path.exists(path) or os.environ.get("REDRAW"):
            S = Sketch(seed=11 + i)
            fn(S)
            S.img.save(path)
        plates.append(Image.open(path).convert("RGB"))
    words = [w for l in lines for w in l["words"]]
    # audio: voice + music + a soft page whoosh on each cut
    voice, _ = sf.read(os.path.join(BUILD, "voice.wav"))
    n = int(total * SR)
    mix = np.zeros(n)
    mix[:len(voice)] += voice[:n]
    mix += music(total)
    for l in lines[1:]:
        i = int((l["t0"] - 0.3) * SR)
        w = whoosh_soft()
        mix[i:i + len(w)] += w[:n - i]
    sf.write(os.path.join(BUILD, "mix.wav"), np.clip(mix, -1, 1), SR)
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-i", os.path.join(BUILD, "mix.wav"), "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                            "-af", "loudnorm=I=-14:TP=-1.5", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    starts = [0.0] + [l["t0"] - 0.25 for l in lines[1:]]
    for f in range(int(total * FPS)):
        t = f / FPS
        k = max(i for i, s in enumerate(starts) if s <= t)
        end = starts[k + 1] if k + 1 < len(starts) else total
        p = (t - starts[k]) / max(0.5, end - starts[k])
        z = 1.0 + 0.045 * p                                   # slow push-in
        cw, ch = PW / (PW / W) / z, PH / (PH / H) / z
        sx = PW / W
        box_w, box_h = W * sx / z, H * sx / z
        x0 = (PW - box_w) / 2 + (8 if k % 2 else -8) * p * sx
        y0 = (PH - box_h) / 2
        img = plates[k].transform((W, H), Image.EXTENT, (x0, y0, x0 + box_w, y0 + box_h), Image.BILINEAR)
        if k > 0 and t - starts[k] < 0.2:                     # quick dissolve between drawings
            q = (t - starts[k]) / 0.2
            prev = plates[k - 1].transform((W, H), Image.EXTENT, ((PW - W * sx / 1.045) / 2, (PH - H * sx / 1.045) / 2,
                                                                  (PW + W * sx / 1.045) / 2, (PH + H * sx / 1.045) / 2), Image.BILINEAR)
            img = Image.blend(prev, img, q)
        caption(img, words, t)
        enc.stdin.write(img.tobytes())
    enc.stdin.close()
    enc.wait()
    print("pilot done", round(total, 1), "s", OUT)


if __name__ == "__main__":
    main()
