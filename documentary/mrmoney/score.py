"""MR MONEY: original score (synthesized here, free to use) + sound design + narration mix.

Cues follow each scene's `mood`: night, build, hit, groove (amapiano), fuji, lament, rise, tender, anthem.
usage (from documentary/):  python3 mrmoney/score.py BUILD_DIR   -> BUILD_DIR/mix.wav
"""
import json, os, sys
import numpy as np
import soundfile as sf
from pedalboard import Pedalboard, Reverb, Limiter, HighpassFilter, LowpassFilter, Compressor

SR = 44100
BUILD = sys.argv[1]
TL = json.load(open(os.path.join(BUILD, "timeline.json")))
TOTAL = max(e["end"] for e in TL)
rng = np.random.default_rng(3)
MUSIC = "/tmp/claude-0/-home-user-BASIT-WEBSITE/555a1255-6634-5fee-9091-b296a9cf2a9b/scratchpad/music"


def T(d):
    return np.arange(int(d * SR)) / SR


def add(buf, sig, at, gain=1.0):
    i = int(at * SR)
    if i < 0:
        sig, i = sig[-i:], 0
    if i >= len(buf):
        return
    sig = sig[:len(buf) - i]
    buf[i:i + len(sig)] += sig * gain


def env(n, a=0.005, r=0.05):
    e = np.ones(n)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e


def lp1(x, a):
    from scipy.signal import lfilter
    return lfilter([a], [1, a - 1], x)


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ------------------------------------------------------------------ instruments
def kick(g=1.0):
    t = T(0.45)
    f = 46 + 110 * np.exp(-t * 32)
    return np.tanh(1.6 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t * 7) * g


def log_drum(m, d=0.55):
    """amapiano log drum: pitched, slightly saturated, with a downward glide"""
    t = T(d)
    f = hz(m) * (1 + 0.5 * np.exp(-t * 28))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
    return np.tanh(2.4 * s) * np.exp(-t * 5.5) * env(len(t), 0.002, 0.05) * 0.5


def shaker(g=1.0):
    t = T(0.07)
    n = rng.standard_normal(len(t))
    n = n - lp1(n, 0.35)
    return n * np.exp(-t * 60) * 0.10 * g


def hat(open_=False):
    t = T(0.25 if open_ else 0.05)
    n = rng.standard_normal(len(t))
    n = n - lp1(n, 0.2)
    return n * np.exp(-t * (14 if open_ else 80)) * 0.08


def clap():
    t = T(0.22)
    n = rng.standard_normal(len(t))
    n = n - lp1(n, 0.15)
    e = np.exp(-t * 22) * (1 + 0.8 * ((t < 0.01) | ((t > 0.015) & (t < 0.022))))
    return n * e * 0.22


def rim():
    t = T(0.06)
    return (np.sin(2 * np.pi * 1700 * t) * 0.6 + rng.standard_normal(len(t)) * 0.3) * np.exp(-t * 90) * 0.18


def bell(m=79):
    """agogo / cowbell for fuji"""
    t = T(0.25)
    f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * f * 1.48 * t)
    return s * np.exp(-t * 18) * 0.10


def talking_drum(m=50, up=True, d=0.32):
    t = T(d)
    glide = (1.35 if up else 0.75)
    f = hz(m) * (1 + (glide - 1) * (1 - np.exp(-t * 14)))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.4 * np.sin(2.01 * ph) + 0.15 * np.sin(3.3 * ph)
    s += rng.standard_normal(len(t)) * 0.15 * np.exp(-t * 60)
    return s * np.exp(-t * 9) * 0.32


def keys(m, d=0.9, v=1.0):
    """soft Rhodes-like electric piano (FM)"""
    t = T(d)
    f = hz(m)
    mod = np.sin(2 * np.pi * f * 1.0 * t) * 1.4 * np.exp(-t * 6)
    s = np.sin(2 * np.pi * f * t + mod) + 0.2 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 4)
    return s * np.exp(-t * 2.4) * env(len(t), 0.003, 0.15) * 0.085 * v


def pad(ms, d, bright=0.3):
    t = T(d)
    s = np.zeros(len(t))
    for m in ms:
        for det in (-0.08, 0.0, 0.07):
            f = hz(m + det)
            ph = 2 * np.pi * f * t + rng.random() * 6
            s += np.sin(ph) + bright * 0.5 * np.sin(2 * ph) + bright * 0.25 * np.sin(3 * ph)
    s = lp1(s, 0.08 + 0.1 * bright)
    return s * env(len(t), min(0.8, d / 3), min(1.0, d / 3)) * 0.018


def choir(ms, d, vowel="a"):
    """'ahh' choir: additive voices shaped by vowel formants, with vibrato"""
    t = T(d)
    s = np.zeros(len(t))
    form = {"a": [(730, 1.0), (1090, 0.5), (2440, 0.25)], "o": [(570, 1.0), (840, 0.45), (2410, 0.18)]}[vowel]
    for vi, m in enumerate(ms):
        for v in range(3):
            f0 = hz(m) * (1 + 0.004 * (v - 1))
            vib = 1 + 0.006 * np.sin(2 * np.pi * (5.0 + 0.4 * v) * t + vi + v)
            ph = 2 * np.pi * np.cumsum(f0 * vib) / SR
            for h in range(1, 14):
                fh = f0 * h
                w = sum(a * np.exp(-((fh - F) / 160.0) ** 2) for F, a in form) + 0.02
                s += np.sin(h * ph) * w / h ** 0.3
    s = lp1(s, 0.25)
    return s * env(len(t), min(1.2, d / 3), min(1.2, d / 3)) * 0.004


def sub_boom(d=2.5):
    t = T(d)
    f = 34 + 40 * np.exp(-t * 6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2) * 0.8


def whoosh(d=0.8, up=True):
    t = T(d)
    n = rng.standard_normal(len(t))
    a = 0.02 + 0.3 * ((t / d) if up else (1 - t / d)) ** 2
    out = np.empty_like(n)
    s = 0.0
    for i in range(len(n)):
        s += a[i] * (n[i] - s)
        out[i] = s
    return out * np.sin(np.pi * t / d) ** 1.5 * 0.5


def riser(d=3.0):
    t = T(d)
    n = rng.standard_normal(len(t))
    out = np.empty_like(n)
    s = 0.0
    a = 0.01 + 0.25 * (t / d) ** 2
    for i in range(len(n)):
        s += a[i] * (n[i] - s)
        out[i] = s
    tone = np.sin(2 * np.pi * np.cumsum(200 + 900 * (t / d) ** 2) / SR) * 0.15
    return (out * 0.6 + tone) * (t / d) ** 2 * 0.6


def pop(f=900):
    t = T(0.12)
    fr = f * (1 + 1.2 * np.exp(-t * 50))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 30) * 0.25


def thud():
    t = T(0.4)
    f = 60 + 70 * np.exp(-t * 30)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 10)
    n = rng.standard_normal(len(t))
    return (s + lp1(n, 0.2) * np.exp(-t * 40) * 0.5) * 0.7


def tick():
    t = T(0.03)
    return np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 200) * 0.06


# ------------------------------------------------------------------ cues (loopable patterns)
AM = [57, 60, 64, 67, 71]          # Am9
FM = [53, 57, 60, 64, 67]          # Fmaj9
DM = [50, 53, 57, 60, 64]          # Dm9
EM = [52, 55, 59, 62, 64]          # Em7(11)
PROG = [AM, FM, DM, EM]
BASS = [45, 41, 38, 40]
C_, G_, A_, F_ = [48, 55, 60, 64, 67], [43, 55, 59, 62, 67], [45, 57, 60, 64, 69], [41, 53, 57, 60, 65]


def bars(fn, dur, bpm):
    beat = 60 / bpm
    out = np.zeros(int((dur + 4) * SR))
    nb = int(dur / (4 * beat)) + 2
    for b in range(nb):
        fn(out, b, b * 4 * beat, beat)
    return out[:int(dur * SR)]


def cue_groove(dur, intensity=1.0, choirs=False, prog=PROG, bass=BASS):
    def bar(o, b, t0, beat):
        ch = b % 4
        add(o, pad(prog[ch], 4 * beat + 0.5, 0.25), t0)
        for k in range(4):
            add(o, kick(0.9), t0 + k * beat)
        for k in (1, 3):
            add(o, clap(), t0 + k * beat)
        for k in range(16):
            add(o, shaker(1.0 if k % 2 else 0.5), t0 + k * beat / 4 + (0.012 if k % 2 else 0))
        for k in (0.5, 1.5, 2.5, 3.5):
            add(o, hat(True), t0 + k * beat, 0.5)
        # log drum pattern (the amapiano signature)
        for off, oc in ((0, 0), (0.75, 0), (1.5, 12), (2.5, 0), (3.25, 7)):
            add(o, log_drum(bass[ch] + oc - 12), t0 + off * beat, 0.9 * intensity)
        # keys stabs
        for off in (0, 1.5, 3):
            for m in prog[ch][1:4]:
                add(o, keys(m + 12, 0.7, 0.8), t0 + off * beat)
        if choirs:
            add(o, choir(prog[ch][1:4], 4 * beat + 0.4), t0)
    return bars(bar, dur, 112)


def cue_night(dur):
    def bar(o, b, t0, beat):
        ch = b % 2
        chord = [AM, FM][ch]
        add(o, pad(chord, 4 * beat + 1.0, 0.15), t0, 1.2)
        add(o, log_drum(BASS[[0, 1][ch]] - 12, 1.2), t0, 0.6)
        for k, m in enumerate((chord[3] + 12, chord[2] + 12, chord[4] + 12)):
            add(o, keys(m, 1.6, 0.7), t0 + k * beat * 1.33)
        for k in range(8):
            add(o, shaker(0.35), t0 + k * beat / 2)
    return bars(bar, dur, 84)


def cue_fuji(dur):
    def bar(o, b, t0, beat):
        ch = b % 2
        add(o, pad([AM, DM][ch], 4 * beat + 0.3, 0.2), t0, 0.8)
        for k in range(4):
            add(o, kick(0.8), t0 + k * beat)
        pat = [(0, 55, True), (0.75, 50, False), (1.5, 57, True), (2, 52, False), (2.75, 55, True), (3.5, 48, False)]
        for off, m, up in pat:
            add(o, talking_drum(m, up), t0 + off * beat)
        for k in (0, 1, 1.5, 2.5, 3):
            add(o, bell(81 if k % 1 else 76), t0 + k * beat)
        for k in range(16):
            add(o, shaker(0.9), t0 + k * beat / 4)
        add(o, clap(), t0 + 1 * beat, 0.8)
        add(o, clap(), t0 + 3 * beat, 0.8)
        for off, oc in ((0, 0), (2.5, 7)):
            add(o, log_drum([45, 38][ch] + oc - 12, 0.5), t0 + off * beat, 0.7)
    return bars(bar, dur, 118)


def cue_tender(dur):
    def bar(o, b, t0, beat):
        ch = b % 4
        chord = [C_, A_, F_, G_][ch]
        add(o, pad(chord, 4 * beat + 1.0, 0.12), t0)
        add(o, choir(chord[1:4], 4 * beat + 0.8, "o"), t0, 0.8)
        for k, m in enumerate((chord[2] + 12, chord[3] + 12, chord[4] + 12, chord[3] + 12)):
            add(o, keys(m, 1.4, 0.7), t0 + k * beat)
    return bars(bar, dur, 76)


def cue_anthem(dur):
    def bar(o, b, t0, beat):
        ch = b % 4
        chord = [C_, G_, A_, F_][ch]
        add(o, pad(chord, 4 * beat + 0.5, 0.3), t0)
        add(o, choir(chord[1:4], 4 * beat + 0.5), t0, 1.2)
        for k in range(4):
            add(o, kick(0.9), t0 + k * beat)
        for k in (1, 3):
            add(o, clap(), t0 + k * beat)
        for k in range(16):
            add(o, shaker(1.0 if k % 2 else 0.5), t0 + k * beat / 4)
        root = chord[0] - 12 if chord[0] > 44 else chord[0]
        for off, oc in ((0, 0), (0.75, 0), (1.5, 12), (2.5, 0), (3.25, 7)):
            add(o, log_drum(root + oc - 12 if root > 40 else root + oc), t0 + off * beat, 0.8)
        for off in (0, 1.5, 3):
            for m in chord[2:5]:
                add(o, keys(m + 12, 0.8, 0.9), t0 + off * beat)
    return bars(bar, dur, 108)


def cue_lament(dur):
    path = os.path.join(MUSIC, "Long Note Four.mp3")
    a, sr = sf.read(path) if path.endswith(".wav") else (None, None)
    if a is None:
        import subprocess, io
        raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
        a = np.frombuffer(raw, np.float32).astype(np.float64)
    a = a[int(4 * SR):]
    if len(a) < dur * SR:
        a = np.concatenate([a, np.zeros(int(dur * SR) - len(a))])
    a = a[:int(dur * SR)]
    return a / (np.sqrt(np.mean(a[:int(min(len(a), 30 * SR))] ** 2)) + 1e-9) * 0.08


CUES = {"night": cue_night, "build": lambda d: cue_night(d) * 0.8, "groove": cue_groove, "fuji": cue_fuji,
        "rise": lambda d: cue_groove(d, 1.0, True), "tender": cue_tender, "anthem": cue_anthem, "lament": cue_lament}


def rms(x):
    return np.sqrt(np.mean(x ** 2) + 1e-12)


def main():
    n = int((TOTAL + 1) * SR)
    voice = np.zeros(n)
    music = np.zeros(n)
    sfx = np.zeros(n)
    vdir = os.path.join(BUILD, "voice")
    for e in TL:
        if e.get("voice_at") is not None and os.path.exists(os.path.join(vdir, e["id"] + ".wav")):
            v, sr = sf.read(os.path.join(vdir, e["id"] + ".wav"))
            if v.ndim > 1:
                v = v.mean(1)
            if sr != SR:
                from scipy.signal import resample_poly
                from math import gcd
                g = gcd(SR, sr)
                v = resample_poly(v, SR // g, sr // g)
            add(voice, v, e["start"] + e["voice_at"])
    # ---- music sections (consecutive scenes with the same mood; cards/logo take the next scene's mood)
    moods = []
    for i, e in enumerate(TL):
        m = e.get("mood")
        if m is None:
            m = next((x.get("mood") for x in TL[i + 1:] if x.get("mood")), "groove")
        moods.append(m)
    secs = []
    for e, m in zip(TL, moods):
        if m == "hit":
            continue
        if secs and secs[-1][0] == m and e["start"] <= secs[-1][2] + 0.1:
            secs[-1][2] = e["end"]
        else:
            secs.append([m, e["start"], e["end"]])
    XF = 1.5
    for m, a, b in secs:
        d = b - a + XF
        cue = CUES[m](d)
        cue = cue / (rms(cue) + 1e-9) * {"night": 0.05, "build": 0.05, "groove": 0.07, "fuji": 0.07, "rise": 0.075,
                                          "tender": 0.05, "anthem": 0.08, "lament": 0.06}[m]
        fade = np.ones(len(cue))
        k = int(XF * SR)
        fade[:k] = np.linspace(0, 1, k) ** 0.8
        fade[-k:] *= np.linspace(1, 0, k) ** 0.8
        add(music, cue * fade, a - (XF / 2 if a > 0 else 0))
    # ---- sound design
    for e in TL:
        s = e["start"]
        if e.get("card"):
            add(sfx, whoosh(0.7, True), s - 0.45, 0.5)
            add(sfx, sub_boom(2.2), s + 0.12, 0.7)
            add(sfx, thud(), s + 0.12, 0.6)
        if e.get("logo"):
            add(sfx, riser(3.0), s - 2.8, 0.8)
            add(sfx, sub_boom(3.5), s + 0.25, 1.0)
            add(sfx, choir(AM[1:4], 4.5), s + 0.25, 1.8)
        for sh in e.get("shots", []):
            t0 = s + sh["t0"]
            if sh["kind"] == "kin" and sh["style"] == "stamp":
                for _, ta in sh["tl"]:
                    add(sfx, thud(), s + ta, 0.8)
            if sh["kind"] == "kin" and sh["style"] in ("big", "define", "promise", "name", "name1", "final", "reveal"):
                for _, ta in sh["tl"][:1]:
                    add(sfx, whoosh(0.5, False), s + ta - 0.1, 0.35)
            if sh["kind"] == "kin" and sh["style"] in ("tick", "list", "stack", "recipe"):
                for _, ta in sh["tl"]:
                    add(sfx, pop(700), s + ta, 0.35)
            if sh["kind"] == "kin" and sh["style"] == "album":
                add(sfx, whoosh(0.9, True), t0, 0.45)
            if sh["kind"] == "stat" and sh.get("count", True):
                for k in range(22):
                    add(sfx, tick(), t0 + 0.15 + 2.2 * (1 - (1 - k / 22) ** 0.25), 1.0)
                add(sfx, pop(1200), t0 + 2.4, 0.5)
            if sh["kind"] == "phone":
                for side, _, _, ta in sh["tl"]:
                    add(sfx, pop(1500 if side == "out" else 900), s + ta, 0.5 if side == "out" else 0.8)
    # ---- duck music under the voice
    ve = np.abs(voice)
    k = int(0.25 * SR)
    c = np.cumsum(np.concatenate([[0], ve]))
    sm = (c[k:] - c[:-k]) / k
    sm = np.concatenate([np.zeros(k // 2), sm, np.zeros(len(ve) - len(sm) - k // 2)])
    duck = 1 - 0.45 * np.clip(sm / (np.percentile(sm[sm > 0], 90) + 1e-9), 0, 1)
    v_r = rms(voice[voice != 0]) if np.any(voice) else 0.1
    mus_gain = float(os.environ.get("MUS_GAIN", "1.0"))
    music = music * duck * mus_gain * (v_r / 0.1)
    sfx = sfx * (v_r / 0.1) * 0.8
    # ---- stereo: music gets reverb width, voice centred
    board = Pedalboard([HighpassFilter(40), Reverb(room_size=0.35, wet_level=0.12, dry_level=0.9, width=1.0)])
    ms = board(np.stack([music, np.roll(music, 9)]).astype(np.float32), SR)
    fx = Pedalboard([Reverb(room_size=0.5, wet_level=0.18, dry_level=0.85)])(np.stack([sfx, sfx]).astype(np.float32), SR)
    vv = np.stack([voice, voice]).astype(np.float32)
    mix = vv + ms[:, :vv.shape[1]] + fx[:, :vv.shape[1]]
    mix = Pedalboard([Limiter(threshold_db=-1.5, release_ms=120)])(mix.astype(np.float32), SR)
    sf.write(os.path.join(BUILD, "mix.wav"), mix.T, SR)
    print("mix done", round(TOTAL, 1), "s; music sections:", [(m, round(a), round(b)) for m, a, b in secs])


if __name__ == "__main__":
    main()
