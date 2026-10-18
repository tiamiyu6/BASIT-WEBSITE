"""Original soundtrack + sound effects for the Danfo Delivers proof video (all synthesized, free to give away).

usage: python3 svgator/sound.py VIDEO_IN VIDEO_OUT
Timings follow the proof video: segment 1 at 0 s, "same template" card at 6.733 s, segment 2 at 8.733 s.
"""
import subprocess, sys
import numpy as np
import soundfile as sf

SR = 44100
rng = np.random.default_rng(7)
SEG, CARD = 6.733, 2.0


def t_(d):
    return np.arange(int(d * SR)) / SR


def env(n, a=0.005, r=0.1):
    e = np.ones(n)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e


def add(buf, sig, at):
    i = int(at * SR)
    if i >= len(buf):
        return
    sig = sig[:len(buf) - i]
    buf[i:i + len(sig)] += sig


def lp(x, a):  # one-pole low-pass
    y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x):
        s += a * (v - s); y[i] = s
    return y


# ---------------------------------------------------------------- music: bright afro-pop groove, 112 BPM, C major pentatonic
BPM = 112
BEAT = 60 / BPM


def kick():
    t = t_(0.35); f = 50 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def shaker():
    t = t_(0.06); return rng.standard_normal(len(t)) * np.exp(-t * 70) * 0.12


def clap():
    t = t_(0.18); n = rng.standard_normal(len(t))
    e = np.exp(-t * 25) * (1 + 0.6 * (np.sin(2 * np.pi * 90 * t) > 0))
    return lp(np.diff(np.concatenate([[0], n])), 0.5) * e * 0.5


def logdrum(f):
    t = t_(0.45); fr = f * (1 + 0.6 * np.exp(-t * 40))
    s = np.sin(2 * np.pi * np.cumsum(fr) / SR)
    return np.tanh(2.2 * s) * np.exp(-t * 6) * 0.5


def pluck(f, d=0.35):
    t = t_(d)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.12 * np.sin(2 * np.pi * 3 * f * t)
    return s * np.exp(-t * 9) * env(len(t), 0.002, 0.05) * 0.22


def pad(fs, d):
    t = t_(d)
    s = sum(np.sin(2 * np.pi * f * t + i) + 0.3 * np.sin(2 * np.pi * f * 1.003 * t) for i, f in enumerate(fs))
    return s * env(len(t), 0.3, 0.6) * 0.035


C, D, E, G, A = 261.63, 293.66, 329.63, 392.0, 440.0
CHORDS = [(C, E, G), (A / 2, C, E), (349.23 / 1, A, C * 2), (G / 2, D, G)]   # C  Am  F  G
BASS = [65.41, 55.0, 87.31, 98.0]
MEL = [[E * 2, G * 2, A * 2, G * 2, E * 2, D * 2, C * 2, D * 2],
       [C * 2, E * 2, A, C * 2, E * 2, G * 2, E * 2, C * 2],
       [A * 2, G * 2, E * 2, G * 2, A * 2, C * 4, A * 2, G * 2],
       [G * 2, E * 2, D * 2, E * 2, G * 2, A * 2, G * 2, D * 2]]


def music(total):
    m = np.zeros(int(total * SR) + SR)
    bars = int(total / (4 * BEAT)) + 1
    for b in range(bars):
        t0 = b * 4 * BEAT; ch = b % 4
        add(m, pad(CHORDS[ch], 4 * BEAT + 0.3), t0)
        for k in range(4):
            add(m, kick() * 0.7, t0 + k * BEAT)
        for k in (1, 3):
            add(m, clap(), t0 + k * BEAT)
        for k in range(16):
            add(m, shaker() * (1.0 if k % 2 else 0.55), t0 + k * BEAT / 4)
        for k, off in enumerate((0, 1.5, 2.5, 3.25)):                      # log-drum bass pattern
            add(m, logdrum(BASS[ch] * (2 if k == 3 else 1)), t0 + off * BEAT)
        for k, f in enumerate(MEL[ch]):
            add(m, pluck(f), t0 + k * BEAT / 2 + (0.03 if k % 2 else 0))   # slight swing
    return m


# ---------------------------------------------------------------- sound effects
def engine(d=1.4):
    t = t_(d)
    f = 38 + 55 * np.clip(1 - t / 1.3, 0, 1) ** 1.5 + 4 * np.sin(2 * np.pi * 1.7 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.tanh(3 * (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3.01 * ph))) * 0.5
    s += lp(rng.standard_normal(len(t)), 0.05) * 0.6
    return s * env(len(t), 0.05, 0.35) * 0.35


def idle(d):
    t = t_(d); ph = 2 * np.pi * np.cumsum(32 + 2 * np.sin(2 * np.pi * 3 * t)) / SR
    return np.tanh(2 * np.sin(ph)) * env(len(t), 0.1, 0.4) * 0.06


def brake():
    t = t_(0.35); f = 2400 + 300 * np.sin(2 * np.pi * 23 * t) - 600 * t
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.6 + rng.standard_normal(len(t)) * 0.15
    return s * env(len(t), 0.02, 0.15) * 0.10


def horn(d=0.18):
    t = t_(d)
    s = sum(np.sign(np.sin(2 * np.pi * f * t)) * a for f, a in ((349, 0.5), (440, 0.4)))
    return lp(s, 0.25) * env(len(t), 0.01, 0.04) * 0.22


def pop(f=600):
    t = t_(0.14); fr = f * (1 + 1.4 * np.exp(-t * 60))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 28) * 0.35


def whoosh(d=0.55):
    t = t_(d); n = rng.standard_normal(len(t))
    a = 0.02 + 0.25 * (t / d) ** 2
    out = np.empty_like(n); s = 0.0
    for i, v in enumerate(n):
        s += a[i] * (v - s); out[i] = s
    return out * np.sin(np.pi * t / d) ** 1.5 * 0.45


def thud():
    t = t_(0.3); f = 70 + 80 * np.exp(-t * 35)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14)
    s += lp(rng.standard_normal(len(t)), 0.3) * np.exp(-t * 50) * 0.4
    return s * 0.55


def ding():
    t = t_(0.9)
    s = sum(np.sin(2 * np.pi * f * t) * a * np.exp(-t * k) for f, a, k in ((1046.5, 1, 4), (1568, 0.6, 5), (2093, 0.3, 7)))
    return s * env(len(t), 0.002, 0.2) * 0.16


def sparkle(d=1.2):
    out = np.zeros(int(d * SR))
    notes = [C * 4, E * 4, G * 4, C * 8, G * 4, E * 8]
    for i, f in enumerate(notes):
        tt = t_(0.5); add(out, np.sin(2 * np.pi * f * tt) * np.exp(-tt * 9) * 0.07, i * 0.09)
    return out


def segment_sfx(buf, o):
    add(buf, engine(), o)
    add(buf, brake(), o + 1.12)
    add(buf, horn(0.14), o + 1.36); add(buf, horn(0.22), o + 1.56)
    add(buf, idle(SEG - 1.4), o + 1.3)
    for k, f in enumerate((620, 760, 900)):
        add(buf, pop(f), o + 1.55 + 0.25 * k)
    add(buf, whoosh(0.55), o + 1.72)
    add(buf, thud(), o + 2.28); add(buf, thud() * 0.35, o + 2.48)
    add(buf, pop(1100) * 0.7, o + 2.72); add(buf, ding(), o + 2.78)


def main():
    vin, vout = sys.argv[1], sys.argv[2]
    total = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", vin]))
    n = int(total * SR)
    mus = music(total)[:n]
    sfx = np.zeros(n)
    segment_sfx(sfx, 0.0)
    add(sfx, whoosh(0.6) * 0.8, SEG - 0.15); add(sfx, sparkle(), SEG + 0.35)
    segment_sfx(sfx, SEG + CARD)
    # duck music a little under the effects, fade in/out
    e = np.abs(sfx); k = int(0.08 * SR)
    sm = np.convolve(e, np.ones(k) / k, mode="same")
    duck = 1 - 0.45 * np.clip(sm / (sm.max() + 1e-9) * 3, 0, 1)
    fade = np.ones(n); fade[:int(0.3 * SR)] = np.linspace(0, 1, int(0.3 * SR)); fade[-int(0.8 * SR):] = np.linspace(1, 0, int(0.8 * SR))
    mix = (mus * 0.55 * duck + sfx) * fade
    mix = np.tanh(mix * 1.4) / np.tanh(1.4)
    mix /= np.abs(mix).max() / 0.9
    st = np.stack([mix, mix], 1)
    wav = vout + ".wav"
    sf.write(wav, st, SR)
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", vin, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", vout])
    print("done", vout)


if __name__ == "__main__":
    main()
