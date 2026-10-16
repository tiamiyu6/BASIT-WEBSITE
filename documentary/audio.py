"""Original score + sound design + narration mix -> build/mix.wav (48 kHz stereo).

Everything is synthesised here: pads, plucked arpeggios, taiko-style drums, talking drum,
risers, whooshes, impacts, glitches and crowd ambience. Music is side-chain ducked under the voice.
"""
import json, sys
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve, resample_poly
from timeline import build

ARCHIVAL = {"map_lagos", "chicago", "senate", "june12", "exile", "amalgamation", "independence", "civilwar", "military"}

SR = 48000
BUILD = sys.argv[1]
rng = np.random.default_rng(7)


def T(d):
    return np.arange(int(d * SR)) / SR


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x, axis=0)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x, axis=0)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x, axis=0)


def env(n, a, r, sus=1.0):
    e = np.ones(n) * sus
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, sus, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def hz(note):  # midi -> Hz
    return 440 * 2 ** ((note - 69) / 12)


def stereo(x, pan=0.0):
    return np.stack([x * np.sqrt(0.5 * (1 - pan)), x * np.sqrt(0.5 * (1 + pan))], 1)


def add(buf, x, at):
    i = int(at * SR)
    if i >= len(buf) or i + len(x) <= 0:
        return
    if i < 0:
        x, i = x[-i:], 0
    n = min(len(x), len(buf) - i)
    buf[i:i + n] += x[:n]


# ------------------------------------------------------------------ instruments
def pad(notes, d, bright=1800, amp=0.08):
    t = T(d)
    out = np.zeros((len(t), 2))
    for k, n in enumerate(notes):
        for det, pan in ((-0.09, -0.7), (0.0, 0.0), (0.11, 0.7)):
            f = hz(n + det)
            ph = rng.uniform(0, 1)
            saw = 2 * ((f * t + ph) % 1) - 1
            out += stereo(saw, pan)
    out = lp(out, bright, 2) * amp / len(notes)
    return out * env(len(t), min(1.2, d / 3), min(1.5, d / 3))[:, None]


def pluck(n, d=1.6, amp=0.12, pan=0.0, bright=1.0):
    t = T(d)
    f = hz(n)
    x = sum(np.sin(2 * np.pi * k * f * t) * np.exp(-t * (2.5 + k * 1.8 / bright)) / k for k in range(1, 9))
    x *= env(len(t), 0.003, 0.05)
    return stereo(x * amp, pan)


def piano(n, d=3.0, amp=0.14, pan=0.0):
    t = T(d)
    f = hz(n)
    x = sum(np.sin(2 * np.pi * k * f * t * (1 + 0.0004 * k * k)) * np.exp(-t * (0.9 + k * 0.7)) / k ** 1.3
            for k in range(1, 10))
    x *= env(len(t), 0.004, 0.3)
    return stereo(x * amp, pan)


def kick(amp=0.5):
    t = T(0.6)
    f = 45 + 90 * np.exp(-t * 28)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    return stereo(x * amp)


def taiko(amp=0.45, pitch=1.0):
    t = T(1.2)
    f = (70 + 50 * np.exp(-t * 15)) * pitch
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
    skin = lp(rng.normal(0, 1, len(t)), 900) * np.exp(-t * 30) * 0.6
    return stereo((body + skin) * amp)


def talking_drum(shape, amp=0.3, pan=0.25):
    """shape: (start_hz, peak_hz, end_hz). The pitch bends like a squeezed dùndún."""
    t = T(0.45)
    s, p, e = shape
    f = np.interp(t, [0, 0.06, 0.45], [s, p, e])
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    x += lp(rng.normal(0, 1, len(t)), 2500) * np.exp(-t * 60) * 0.3
    return stereo(x * amp, pan)


def shaker(amp=0.05, pan=0.3):
    t = T(0.08)
    return stereo(hp(rng.normal(0, 1, len(t)), 6000) * np.exp(-t * 60) * amp, pan)


def tick(amp=0.06):
    t = T(0.04)
    return stereo(hp(rng.normal(0, 1, len(t)), 3500) * np.exp(-t * 150) * amp, 0.4)


def sub_pulse(amp=0.35):
    t = T(0.9)
    return stereo(np.sin(2 * np.pi * 42 * t) * np.exp(-t * 5) * env(len(t), 0.01, 0.1) * amp)


# ------------------------------------------------------------------ sound effects
def whoosh(d=1.0, amp=0.35, up=True):
    n = int(d * SR)
    t = np.linspace(0, 1, n)
    noise = rng.normal(0, 1, n)
    out = np.zeros(n)
    bands = [(300, 900), (900, 2500), (2500, 7000)]
    for i, (lo, hi) in enumerate(bands):
        c = (i + 0.5) / len(bands)
        w = np.exp(-((t - (c if up else 1 - c)) ** 2) / 0.04)
        out += bp(noise, lo, hi) * w
    e = np.sin(np.pi * t) ** 2
    x = out * e * amp
    pan = np.linspace(-0.8, 0.8, n)
    return np.stack([x * np.sqrt(0.5 * (1 - pan)), x * np.sqrt(0.5 * (1 + pan))], 1)


def impact(amp=0.8):
    t = T(3.0)
    f = 28 + 70 * np.exp(-t * 9)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)
    crack = lp(rng.normal(0, 1, len(t)), 4000) * np.exp(-t * 18)
    x = boom * 0.9 + crack * 0.35
    return stereo(x * amp)


def riser(d=2.5, amp=0.25):
    t = T(d)
    f = np.geomspace(150, 1800, len(t))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3
    noise = hp(rng.normal(0, 1, len(t)), 1500) * 0.6
    e = (t / d) ** 2.2
    x = (tone + noise) * e * amp
    return np.stack([x, np.roll(x, 300)], 1)


def glitch_sfx(d=0.5, amp=0.22):
    n = int(d * SR)
    x = np.zeros(n)
    i = 0
    while i < n:
        L = min(int(rng.uniform(0.01, 0.06) * SR), n - i)
        kind = rng.integers(3)
        seg = np.arange(L) / SR
        if kind == 0:
            x[i:i + L] = np.sign(np.sin(2 * np.pi * rng.uniform(80, 1500) * seg))
        elif kind == 1:
            x[i:i + L] = np.round(rng.normal(0, 1, L) * 3) / 3
        i += L + int(rng.uniform(0, 0.03) * SR)
    x = x[:n] * amp
    return np.stack([x, np.roll(x, 120)], 1)


def crowd_amb(d, amp=0.06):
    n = int(d * SR)
    base = bp(rng.normal(0, 1, (n, 2)), 250, 2200)
    mod = lp(np.abs(rng.normal(0, 1, n)), 3)
    mod = 0.6 + 0.8 * mod / (mod.max() + 1e-9)
    return base * mod[:, None] * amp * env(n, 1.5, 1.5)[:, None]


def wind(d, amp=0.05):
    n = int(d * SR)
    x = lp(rng.normal(0, 1, (n, 2)), 500)
    mod = 0.5 + 0.5 * np.sin(2 * np.pi * T(d) * 0.13)[:, None]
    return x * mod * amp * env(n, 2, 2)[:, None]


def fire_amb(d, amp=0.08):
    n = int(d * SR)
    x = lp(rng.normal(0, 1, (n, 2)), 300) * 0.5
    for _ in range(int(d * 14)):
        add(x, stereo(hp(rng.normal(0, 1, 400), 2000) * np.exp(-np.arange(400) / 60), rng.uniform(-1, 1)),
            rng.uniform(0, d))
    return x * amp * env(n, 1, 1)[:, None]


def heartbeat(amp=0.6):
    t = T(0.5)
    x = np.sin(2 * np.pi * 50 * t) * np.exp(-t * 14)
    x2 = np.sin(2 * np.pi * 44 * t) * np.exp(-t * 16)
    out = np.zeros(int(0.75 * SR))
    out[: len(x)] += x
    out[int(0.22 * SR): int(0.22 * SR) + len(x2)] += x2 * 0.7
    return stereo(lp(out, 200) * amp)


def reverse_swell(d=1.6, amp=0.35):
    t = T(d)
    cym = hp(rng.normal(0, 1, len(t)), 3000) * np.exp(-t * 3.0) * 0.7
    tone = sum(np.sin(2 * np.pi * f * t) for f in (110, 165, 220)) * np.exp(-t * 2.2) * 0.25
    x = (cym + tone)[::-1] * amp
    return np.stack([x, np.roll(x, 200)], 1)


def shatter(amp=0.3):
    t = T(1.4)
    x = hp(rng.normal(0, 1, len(t)), 2500) * np.exp(-t * 7)
    for _ in range(40):
        f, a0 = rng.uniform(2500, 9000), rng.uniform(0, 0.25)
        seg = np.sin(2 * np.pi * f * t) * np.exp(-np.clip(t - a0, 0, None) * 18) * (t >= a0)
        x += seg * 0.15
    return stereo(x * amp)


def power_down(d=2.4, amp=0.3):
    t = T(d)
    f = np.geomspace(380, 30, len(t))
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5 + np.sin(2 * np.pi * np.cumsum(f * 0.5) / SR)
    x = lp(x, 900) * (1 - t / d) * amp
    return stereo(x)


def projector(d, amp=0.03):
    n = int(d * SR)
    x = lp(rng.normal(0, 1, (n, 2)), 3000) * 0.25
    clk = hp(rng.normal(0, 1, 300), 1500) * np.exp(-np.arange(300) / 40)
    for k in range(int(d * 24)):
        add(x, stereo(clk * rng.uniform(0.6, 1.0)), k / 24)
    return x * amp * env(n, 0.8, 0.8)[:, None]


# ------------------------------------------------------------------ score
BEAT = 0.75  # 80 bpm
PROG = {
    "intro":   [[50, 57, 62, 65], [46, 53, 58, 62], [41, 53, 57, 60], [48, 55, 60, 64]],
    "warm":    [[48, 55, 60, 64], [43, 55, 59, 62], [45, 57, 60, 64], [41, 57, 60, 65]],
    "tension": [[38, 50, 57, 63], [38, 50, 56, 62], [37, 49, 56, 62], [38, 50, 57, 63]],
    "epic":    [[38, 50, 57, 62, 65], [34, 46, 58, 62, 65], [41, 53, 57, 60, 65], [36, 48, 55, 60, 64]],
    "dark":    [[38, 50, 53, 57], [37, 49, 53, 56], [38, 50, 53, 57], [34, 46, 53, 58]],
    "outro":   [[41, 53, 57, 60], [36, 48, 55, 60], [38, 50, 57, 62], [34, 50, 58, 62]],
}


def score_section(mood, d, seed):
    r = np.random.default_rng(seed)
    n = int(d * SR)
    out = np.zeros((n + SR * 4, 2))
    bar = BEAT * 4
    prog = PROG[mood]
    nb = int(np.ceil(d / bar))
    for b in range(nb):
        t0 = b * bar
        ch = prog[b % 4]
        bright = {"intro": 900, "warm": 1600, "tension": 700, "epic": 2400, "dark": 500, "outro": 1200}[mood]
        add(out, pad(ch, bar + 1.2, bright, 0.09 if mood != "epic" else 0.11), t0)
        add(out, stereo(np.sin(2 * np.pi * hz(ch[0] - 12) * T(bar)) * env(int(bar * SR), 0.3, 0.6) * 0.12), t0)
        if mood == "warm":
            arp = [ch[1] + 12, ch[2] + 12, ch[3] + 12, ch[2] + 12]
            for k in range(8):
                add(out, pluck(arp[k % 4], 1.4, 0.07, pan=-0.4 + 0.8 * (k % 2)), t0 + k * BEAT / 2)
            for k in range(16):
                add(out, shaker(0.035 if k % 2 else 0.05), t0 + k * BEAT / 4)
            if b % 4 == 3:
                for k, sh in enumerate([(140, 210, 150), (150, 230, 120), (120, 180, 100)]):
                    add(out, talking_drum(sh, 0.22), t0 + 2 * BEAT + k * BEAT / 2)
        elif mood == "epic":
            for k in (0, 2):
                add(out, taiko(0.5), t0 + k * BEAT)
            add(out, taiko(0.32, 1.4), t0 + 3.5 * BEAT)
            for k in range(8):
                add(out, pluck(ch[-1] + 12 - (k % 3) * 5, 0.9, 0.05, pan=0.5 - (k % 2)), t0 + k * BEAT / 2)
            pat = [(130, 200, 140), (160, 240, 150), (120, 170, 110), (150, 220, 130)]
            for k in range(4):
                add(out, talking_drum(pat[(k + b) % 4], 0.2, pan=-0.3), t0 + (k + 0.5) * BEAT)
        elif mood == "tension":
            for k in range(8):
                add(out, sub_pulse(0.22), t0 + k * BEAT / 2)
            for k in range(4):
                add(out, tick(0.07), t0 + k * BEAT)
            if b % 2 == 1:
                add(out, piano(ch[-1] + 12, 2.5, 0.07, 0.3), t0 + BEAT)
        elif mood == "intro":
            add(out, sub_pulse(0.35), t0)
            add(out, sub_pulse(0.25), t0 + BEAT * 0.4)
            add(out, piano(ch[-1] + 12 if b % 2 else ch[-2] + 12, 3.0, 0.08, -0.2), t0 + BEAT * 2)
        elif mood == "dark":
            if b % 2 == 0:
                add(out, piano(ch[0], 4.0, 0.12), t0)
            add(out, piano(ch[2] + 12, 3.0, 0.05, 0.4), t0 + 2.5 * BEAT)
        elif mood == "outro":
            for k, nn in enumerate([ch[1] + 12, ch[2] + 12, ch[3] + 12, ch[2] + 24]):
                add(out, piano(nn, 3.0, 0.07, -0.3 + 0.2 * k), t0 + k * BEAT)
    return out[:n]


def shutter(amp=0.25):
    t = T(0.25)
    x = np.zeros(len(t))
    for at, g in ((0.0, 1.0), (0.07, 0.7)):
        i = int(at * SR)
        n = int(0.03 * SR)
        x[i:i + n] += hp(rng.normal(0, 1, n), 2500) * np.exp(-np.arange(n) / (0.006 * SR)) * g
    return stereo(x * amp, -0.2)


def reverb(x, secs=2.6, wet=0.25):
    n = int(secs * SR)
    t = np.arange(n) / SR
    ir = np.stack([rng.normal(0, 1, n), rng.normal(0, 1, n)], 1) * np.exp(-t * 6.9 / secs)[:, None]
    ir = lp(ir, 5000) / np.sqrt(np.sum(ir ** 2) / 2)
    w = np.stack([fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return x + w * wet


def main():
    tl, total = build(f"{BUILD}/timing.json")
    total += 1.0
    N = int(total * SR)
    music, sfx, voice = np.zeros((N, 2)), np.zeros((N, 2)), np.zeros((N, 2))

    # --- music: one section per run of scenes sharing a mood, crossfaded
    runs, cur = [], None
    for e in tl:
        mood = e["mood"] or (cur["mood"] if cur else "intro")
        if not cur or mood != cur["mood"]:
            cur = dict(mood=mood, start=e["start"], end=e["end"])
            runs.append(cur)
        cur["end"] = e["end"]
    for i, r in enumerate(runs):
        a, b = max(0, r["start"] - 1.5), min(total, r["end"] + 1.5)
        seg = score_section(r["mood"], b - a, i)
        seg *= env(len(seg), 1.5, 1.5)[:, None]
        add(music, seg, a)
    music = reverb(music, 2.8, 0.35)

    # --- real footage sound (his own voice etc.) plays before the narrator
    for e in tl:
        if e["clip"] and e["clip"][2]:
            import subprocess
            p = f"{BUILD}/clip_{e['id']}.wav"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", e["clip"][0], "-vn", "-ac", "2", "-ar",
                            str(SR), p], check=True)
            c, _ = sf.read(p)
            c = c / (np.max(np.abs(c)) + 1e-9) * 0.8
            add(voice, c * env(len(c), 0.05, 0.4)[:, None], e["start"])

    # --- narration
    for e in tl:
        if e["voice_at"] is None:
            continue
        v, sr = sf.read(f"{BUILD}/voice/{e['id']}.wav")
        v = resample_poly(v, SR, sr)
        add(voice, stereo(v) * 1.25, e["voice_at"])
    voice = reverb(voice, 0.6, 0.06)

    # --- sound design per scene / transition
    for e in tl:
        s, tr = e["start"], e["trans"]
        if tr in ("fade", "zoom"):
            add(sfx, whoosh(1.1, 0.22 if tr == "fade" else 0.35), s - 0.45 + e["ov"] / 2)
        if tr == "glitch":
            add(sfx, glitch_sfx(0.55, 0.2), s)
            add(sfx, whoosh(0.6, 0.18), s - 0.1)
        if tr == "flash":
            add(sfx, riser(1.6, 0.16), s - 1.6)
        if tr == "dip" and e["plate"] == "chapter":
            add(sfx, riser(2.2, 0.2), s - 1.8)
        if e["hit"]:
            add(sfx, impact(0.75 if e["plate"] in ("chapter", "title") else 0.55), s + (0.25 if tr == "dip" else 0.0))
        if e["plate"] in ("endsars", "protest"):
            add(sfx, crowd_amb(e["dur"] + 1, 0.07), s)
        if e["plate"] == "lekki":
            add(sfx, wind(e["dur"] + 1, 0.06), s)
        if e["plate"] == "fire":
            add(sfx, fire_amb(e["dur"] + 1, 0.11), s)
        if e["plate"] in ("exile", "legacy", "open"):
            add(sfx, wind(e["dur"] + 1, 0.035), s)
        hook = any(len(b) >= 5 and b[4] is not None for b in (e.get("broll") or []))
        for k, b in enumerate(e.get("broll") or []):  # shutter on each real photo; impact + whoosh on hook cuts
            at = e["start"] + e["broll_times"][k]
            if hook:
                add(sfx, whoosh(0.35, 0.2), at - 0.3)
                add(sfx, impact(0.42 if b[4] else 0.25), at)
                add(sfx, taiko(0.35, 1.0 + 0.1 * (k % 3)), at)
            else:
                add(sfx, shutter(0.3), at)
        if e.get("broll") and not hook:
            add(sfx, whoosh(1.0, 0.18), e["start"] + e["broll_end"] - 0.3)
        if e["plate"] in ARCHIVAL:
            add(sfx, projector(e["dur"] + 0.5), e["start"])
        if e["plate"] == "portrait":
            # heartbeat that speeds up while we push into the eye, drone + riser, then the flash
            tt, gap = e["start"] + 0.6, 1.25
            while tt < e["end"] - 0.4:
                add(sfx, heartbeat(0.55 + 0.4 * (tt - e["start"]) / e["dur"]), tt)
                tt += gap
                gap = max(0.42, gap * 0.86)
            dr = T(e["dur"])
            add(sfx, stereo(lp(np.sin(2 * np.pi * 36.7 * dr) + 0.5 * np.sin(2 * np.pi * 55 * dr), 300)
                            * env(len(dr), 2.0, 0.2) * 0.18), e["start"])
            add(sfx, riser(3.2, 0.3), e["end"] - 3.2)
            add(sfx, reverse_swell(1.2, 0.3), e["end"] - 1.2)
            add(sfx, impact(0.9), e["end"])
        if e["slam_at"] is not None:
            add(sfx, reverse_swell(1.6, 0.4), e["slam_at"] - 1.6)
            add(sfx, impact(1.0), e["slam_end"] + 0.05)
            add(sfx, taiko(0.7, 0.8), e["slam_end"] + 0.05)
            add(sfx, shatter(0.28), e["slam_end"] + 0.08)
            if "subsidy" in (e.get("slam") or ""):
                add(sfx, power_down(2.6, 0.22), e["slam_end"] + 0.5)
    sfx = reverb(sfx, 1.8, 0.2)

    # --- side-chain duck music + ambience under narration
    venv = np.abs(voice[:, 0])
    venv = lp(venv, 4, 1)
    venv = np.clip(venv / 0.04, 0, 1)
    k = int(0.35 * SR)  # release smoothing
    cs = np.concatenate([[0], np.cumsum(venv)])
    idx = np.arange(len(venv))
    lo, hi = np.clip(idx - k // 2, 0, len(venv)), np.clip(idx + k // 2, 0, len(venv))
    venv = (cs[hi] - cs[lo]) / np.maximum(hi - lo, 1)
    duck = 1 - 0.62 * np.clip(venv * 1.4, 0, 1)
    for e in tl:
        if e["slam_at"] is not None:
            g = np.ones(N)
            a, b, c = int((e["slam_at"] - 1.6) * SR), int(e["slam_at"] * SR), int((e["slam_end"] + 0.05) * SR)
            g[a:b] = np.linspace(1, 0.04, b - a)
            g[b:c] = 0.04
            r = int(2.5 * SR)
            g[c:c + r] = np.linspace(0.04, 1, len(g[c:c + r]))
            duck *= g
        if e["plate"] == "portrait":  # score enters after the eye push-in
            duck[: int(e["end"] * SR)] *= 0.35
    mix = music * duck[:, None] * 0.95 + sfx * (1 - 0.35 * np.clip(venv, 0, 1))[:, None] + voice
    mix = np.tanh(mix * 1.1) / 1.1
    sf.write(f"{BUILD}/mix.wav", mix.astype(np.float32), SR, subtype="FLOAT")
    print("audio", round(total, 1), "s")


if __name__ == "__main__":
    main()
