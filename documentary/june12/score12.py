"""JUNE 12 sound: original score by chapter mood, object sound effects (typewriter, stamps, newspapers),
archive-clip audio and narration, with the music ducked under every voice.  -> BUILD/mix.wav

usage (from documentary/):  python3 june12/score12.py BUILD_DIR
"""
import os, subprocess, sys
import numpy as np, soundfile as sf
from scipy.signal import resample_poly

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = sys.argv[1]
sys.path.insert(0, os.path.dirname(HERE))
import audio as A                      # instruments and effects from the JAGABAN score
sys.path.insert(0, HERE)
sys.argv = [sys.argv[0], BUILD]
import engine12 as E                   # same timeline as the picture

SR = A.SR
rng = np.random.default_rng(12)
T, add, stereo, lp, hp, bp, env, hz = A.T, A.add, A.stereo, A.lp, A.hp, A.bp, A.env, A.hz


# ------------------------------------------------------------------ object sounds
def key_click(amp=0.13):
    t = T(0.07)
    x = bp(rng.normal(0, 1, len(t)), 1200, 5200) * np.exp(-t * 160) * rng.uniform(0.7, 1.0)
    x += np.sin(2 * np.pi * rng.uniform(140, 190) * t) * np.exp(-t * 70) * 0.55      # the thock of the type bar
    return stereo(x * amp, rng.uniform(-0.25, 0.25))


def carriage(amp=0.08):
    t = T(0.35)
    x = bp(rng.normal(0, 1, len(t)), 600, 3000) * np.exp(-t * 9) * 0.5
    x += np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 14) * 0.35                        # margin bell
    return stereo(x * amp, 0.3)


def stamp_hit(amp=0.5):
    t = T(0.45)
    x = np.sin(2 * np.pi * np.cumsum(90 + 60 * np.exp(-t * 40)) / SR) * np.exp(-t * 22)
    x += lp(rng.normal(0, 1, len(t)), 2500) * np.exp(-t * 55) * 0.6
    return stereo(x * amp)


def paper_drop(amp=0.32):
    t = T(0.6)
    rustle = bp(rng.normal(0, 1, len(t)), 900, 7000) * np.exp(-((t - 0.12) / 0.12) ** 2) * 0.6
    slap = lp(rng.normal(0, 1, len(t)), 1800) * np.exp(-np.clip(t - 0.4, 0, None) * 40) * (t >= 0.4) * 1.2
    thud = np.sin(2 * np.pi * 70 * t) * np.exp(-np.clip(t - 0.4, 0, None) * 18) * (t >= 0.4) * 0.6
    return stereo((rustle + slap + thud) * amp, -0.1)


def clock_tick(amp=0.12):
    t = T(0.05)
    x = hp(rng.normal(0, 1, len(t)), 2500) * np.exp(-t * 250) + np.sin(2 * np.pi * 3100 * t) * np.exp(-t * 180) * 0.4
    return stereo(x * amp, 0.2)


def teacup(amp=0.16):
    t = T(1.6)
    x = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) * g for f, d, g in
            ((2093, 4.0, 1.0), (3320, 5.5, 0.6), (4870, 7.0, 0.4), (6260, 9.0, 0.25)))
    x += hp(rng.normal(0, 1, len(t)), 3000) * np.exp(-t * 120) * 0.5
    return stereo(x * amp, 0.15)


def crt_on(amp=0.12):
    t = T(0.9)
    x = hp(rng.normal(0, 1, len(t)), 3000) * np.exp(-t * 30) * 0.5
    x += np.sin(2 * np.pi * 15734 * t) * env(len(t), 0.05, 0.6) * 0.05
    x += np.sin(2 * np.pi * 60 * t) * env(len(t), 0.02, 0.5) * 0.4
    return stereo(x * amp)


def log_drum(note=40, amp=0.22):
    """Amapiano-style log drum: a round, gliding sub-bass hit."""
    t = T(0.6)
    f = hz(note) * (1 + 0.5 * np.exp(-t * 30))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5.5)
    x = np.tanh(x * 1.6) * 0.8
    return stereo(lp(x, 900) * amp)


def hum(notes, d, amp=0.06):
    """A lone humming voice: one formant-filtered line with slow vibrato."""
    t = T(d)
    f = np.interp(t, np.linspace(0, d, len(notes)), [hz(n) for n in notes])
    f = f * (1 + 0.012 * np.sin(2 * np.pi * 5.2 * t))
    src = 2 * ((np.cumsum(f) / SR) % 1) - 1
    v = bp(src, 250, 700) + 0.4 * bp(src, 900, 1300)
    return stereo(v * amp * env(len(t), 1.2, 1.6), -0.1)


# ------------------------------------------------------------------ score by mood
BEAT = 0.75


def section(mood, d, seed):
    """mood -> stereo buffer of length d."""
    r = np.random.default_rng(seed)
    n = int(d * SR)
    out = np.zeros((n + SR * 6, 2))
    bar = BEAT * 4
    nb = int(np.ceil(d / bar))
    base = {"cold": "dark", "tension": "tension", "home": "warm", "rise": "warm", "build": "warm",
            "hope": "outro", "dark": "dark", "resolve": "dark", "lament": "dark", "dawn": "outro"}[mood]
    if mood in ("cold", "dark", "tension", "lament", "resolve"):
        x = A.score_section(base, d, seed)
        out[:len(x)] += x * (0.75 if mood == "lament" else 0.9)
    else:
        x = A.score_section(base, d, seed)
        out[:len(x)] += x * 0.85
    prog = A.PROG[base]
    for b in range(nb):
        t0 = b * bar
        ch = prog[b % 4]
        if mood in ("rise", "build", "hope"):
            # log drum, amapiano-style syncopation, kept low under the narration
            for k, (pos, dn) in enumerate(((0, 0), (1.5, 0), (2.5, 7), (3.25, 5))):
                add(out, log_drum(ch[0] + dn - 12 + 24, 0.16 if mood != "hope" else 0.12), t0 + pos * BEAT)
            for k in range(8):
                add(out, A.shaker(0.03), t0 + (k + 0.5) * BEAT / 2)
        if mood == "home" and b % 2 == 0:
            add(out, A.talking_phrase(0.16), t0 + 2 * BEAT)
        if mood == "hope" and b % 4 == 0:
            add(out, A.choir([ch[1] + 12, ch[2] + 12, ch[3] + 12], bar * 2, 0.045), t0)
        if mood == "lament" and b % 3 == 0:
            line = [ch[2] + 12, ch[3] + 12, ch[2] + 12, ch[1] + 12]
            add(out, hum(line, bar * 2.6, 0.07), t0 + 0.5)
        if mood == "resolve" and b % 2 == 0:
            add(out, A.dundun(0.3), t0)
        if mood == "dawn":
            if b % 2 == 0:
                add(out, A.brass([ch[1] + 12, ch[2] + 12, ch[3] + 12], 1.4, 0.06), t0)
            if b % 4 == 2:
                add(out, A.talking_phrase(0.14), t0 + BEAT)
    out = out[:n]
    out *= env(n, 1.5, 2.0)[:, None]
    return out


def movavg(x, k):
    """Centred moving average via cumulative sums (np.convolve is far too slow at this length)."""
    c = np.cumsum(np.concatenate([np.zeros(k // 2 + 1), x, np.full(k, x[-1])]))
    return (c[k:k + len(x)] - c[:len(x)]) / k


def load_voice(path):
    a, sr = sf.read(path, dtype="float32")
    if a.ndim > 1:
        a = a.mean(1)
    if sr != SR:
        a = resample_poly(a, SR, sr).astype(np.float32)
    return a


def clip_audio(file, a, b):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", file, "-ac", "2", "-ar",
                          str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
    x = A.hp(x, 90)
    peak = np.percentile(np.abs(x), 99.5) + 1e-9
    return x * (0.5 / peak)


def main():
    TL, TOTAL = E.TL, E.TOTAL
    n = int((TOTAL + 2) * SR)
    music = np.zeros((n, 2))
    sfx = np.zeros((n, 2))
    voice = np.zeros((n, 2))
    archive = np.zeros((n, 2))
    duck_extra = np.ones(n)                      # silences the music for chosen moments

    # music: consecutive scenes with the same mood play as one continuous section
    groups, cur = [], None
    for e in TL:
        m = e.get("mood")
        if e.get("clip"):
            m = None
        if e.get("card"):
            m = cur[0] if cur else None
        if cur and m == cur[0]:
            cur[2] = e["end"]
        else:
            if cur and cur[0]:
                groups.append(cur)
            cur = [m, e["start"], e["end"]]
    if cur and cur[0]:
        groups.append(cur)
    for k, (m, a, b) in enumerate(groups):
        d = b - a + 2.0
        add(music, section(m, d, 100 + k) * 0.9, a - 0.5)
        print("music", m, round(a, 1), round(d, 1), flush=True)

    for e in TL:
        s0 = e["start"]
        if e.get("clip"):
            x = clip_audio(*e["clip"])
            add(archive, x, s0)
            add(sfx, crt_on(0.1), s0 - 0.2)
            i0, i1 = int((s0 - 0.4) * SR), int((e["end"] + 0.2) * SR)
            duck_extra[max(i0, 0):i1] = np.minimum(duck_extra[max(i0, 0):i1], 0.12)
            continue
        if e.get("logo"):
            add(sfx, A.projector(6.0, 0.05), s0)
            add(sfx, A.film_pop(0.18), s0 + 0.3)
            add(sfx, A.talking_phrase(0.2), s0 + 1.0)
            for c in range(len("THE ELECTION NIGERIA STOLE")):
                add(sfx, key_click(0.1), s0 + 2.9 + 0.4 + c * 1.3 / 26)
            add(sfx, stamp_hit(0.55), s0 + 2.9 + 2.0)
            add(sfx, A.impact(0.35), s0 + 2.9 + 2.0)
            continue
        if e.get("card"):
            add(sfx, paper_drop(0.18), s0 - 0.1)
            name = e["card"][1]
            for c in range(len(name)):
                add(sfx, key_click(0.11), s0 + 0.4 + c * 1.4 / max(len(name), 1))
            add(sfx, A.talking_phrase(0.12), s0 + 1.9)
            continue
        if e.get("voice_at") is not None and os.path.exists(f"{BUILD}/voice/{e['id']}.wav"):
            v = load_voice(f"{BUILD}/voice/{e['id']}.wav")
            add(voice, stereo(v), s0 + e["voice_at"])
        for k, sh in enumerate(e["shots"]):
            t0 = s0 + sh["t0"]
            if sh["kind"] == "paper":
                add(sfx, paper_drop(0.3), t0 - 0.02)
            elif sh["kind"] == "typed":
                for ln in sh["tl"]:
                    if ln["stamp"]:
                        add(sfx, stamp_hit(0.5), s0 + ln["t"])
                        continue
                    for c in range(len(ln["text"])):
                        if ln["text"][c] != " ":
                            add(sfx, key_click(0.12), s0 + ln["t"] + c * ln["d"] / max(len(ln["text"]), 1))
                    if ln["text"]:
                        add(sfx, carriage(0.05), s0 + ln["t"] + ln["d"] + 0.02)
                    if ln["strike"]:
                        add(sfx, A.flick(0.08), s0 + ln["t"] + ln["d"] + 0.15)
            elif sh["kind"] == "tally":
                for q in range(60):
                    add(sfx, clock_tick(0.035), t0 + 0.6 + q * 0.11)
                if len(e["sents"]) > 3:
                    add(sfx, stamp_hit(0.45), s0 + e["sents"][3][0])
        # story moments
        if e["id"] == "c3_wait":
            for q in range(int((e["dur"] + 1.5) / 1.0)):
                add(sfx, clock_tick(0.14), s0 + 0.3 + q * 1.0)
        if e["id"] == "c7_tea":
            a, b = e["sents"][1]                       # "Tea was served."
            add(sfx, teacup(0.18), s0 + b - 0.1)
            ha, hb = e["sents"][3]                     # "Moments later, he collapsed, and he died."
            for q in range(3):
                add(sfx, A.heartbeat(0.45 - q * 0.12), s0 + ha + q * 0.85)
            i0 = int((s0 + hb - 0.2) * SR)
            duck_extra[i0:i0 + int(2.2 * SR)] = np.minimum(duck_extra[i0:i0 + int(2.2 * SR)], 0.0)
        if e["id"] == "c6_ambush":
            a, b = e["sents"][-1]
            i0 = int((s0 + b + 0.1) * SR)
            ramp = int(0.4 * SR)
            duck_extra[i0 - ramp:i0] = np.minimum(duck_extra[i0 - ramp:i0], np.linspace(1, 0, ramp))
            duck_extra[i0:i0 + int(2.4 * SR)] = 0.0                       # silence instead of a gunshot
        if e["id"] == "c4_abacha":
            add(sfx, A.impact(0.3), s0 + 0.4)
        if e["id"] == "c0_free":
            i0 = int(s0 * SR)
            duck_extra[i0:i0 + int(e["dur"] * SR)] = np.minimum(duck_extra[i0:i0 + int(e["dur"] * SR)], 0.35)

    # duck music (and soften sfx) under the narrator
    def envelope(x, win=0.25):
        p = np.abs(x).mean(1)
        k = int(win * SR)
        c = np.cumsum(np.concatenate([[0], p]))
        m = (c[k:] - c[:-k]) / k
        return np.concatenate([m, np.full(len(p) - len(m), m[-1] if len(m) else 0)])
    venv = envelope(voice)
    duck = 1 - 0.8 * np.clip(venv * 9, 0, 1)
    duck = movavg(duck, int(0.12 * SR))
    de = movavg(duck_extra, int(0.3 * SR))
    music *= (duck * de)[:, None]
    sfx *= (1 - 0.35 * np.clip(venv * 9, 0, 1))[:, None]
    music = A.reverb(music, 2.2, 0.18)
    mix = music * 0.55 + sfx * 0.9 + voice * 1.5 + archive * 1.25
    peak = np.abs(mix).max() + 1e-9
    mix = mix / peak * 0.95
    sf.write(f"{BUILD}/mix.wav", mix.astype(np.float32), SR, subtype="PCM_16")
    print("mix done", round(len(mix) / SR, 1), flush=True)


if __name__ == "__main__":
    main()
