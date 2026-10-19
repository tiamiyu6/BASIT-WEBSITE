"""Mr Money sound effects, synthesized here (free to use): nostalgia beds, Foley and big-moment hits."""
import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100
rng = np.random.default_rng(21)


def T(d):
    return np.arange(int(d * SR)) / SR


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "bandpass", fs=SR, output="sos"), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "lowpass", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "highpass", fs=SR, output="sos"), x)


def norm(x, peak=1.0):
    return x / (np.abs(x).max() + 1e-9) * peak


def fade(x, a=0.01, r=0.05):
    n = len(x)
    e = np.ones(n)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return x * e


# ------------------------------------------------------------------ nostalgia beds
def crackle(d, density=9.0, hiss=0.08):
    """vinyl surface: tiny clicks, the odd pop, a little hiss"""
    n = int(d * SR)
    x = hp(rng.standard_normal(n), 3000) * hiss * 0.15
    k = rng.poisson(density * d)
    for i in rng.integers(0, n - 200, k):
        L = rng.integers(8, 60)
        x[i:i + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 4)) * rng.uniform(0.15, 0.6)
    for i in rng.integers(0, n - 2000, max(1, int(d / 3))):          # pops
        L = 900
        x[i:i + L] += lp(rng.standard_normal(L), 900) * np.exp(-np.arange(L) / 180) * 1.6
    return hp(x, 120)


def tape_hiss(d):
    return lp(hp(rng.standard_normal(int(d * SR)), 2500), 9000) * 0.05


def projector(d, rate=24.0):
    """film projector rattle"""
    t = T(d)
    x = np.zeros(len(t))
    period = int(SR / rate)
    click = hp(rng.standard_normal(220), 1500) * np.exp(-np.arange(220) / 40)
    for i in range(0, len(t) - 220, period):
        x[i:i + 220] += click * rng.uniform(0.6, 1.0)
    motor = np.sin(2 * np.pi * 96 * t) * 0.08 + np.sin(2 * np.pi * 192 * t) * 0.03
    return fade(x * 0.5 + motor, 0.3, 0.4)


def room_tone(d):
    return lp(rng.standard_normal(int(d * SR)), 400) * 0.25


# ------------------------------------------------------------------ the parlour
def fan(d, rpm_hz=2.6):
    """ceiling fan: motor hum + the air chopped by the blades"""
    t = T(d)
    hum = np.sin(2 * np.pi * 100 * t) * 0.05 + np.sin(2 * np.pi * 50 * t) * 0.07
    air = bp(rng.standard_normal(len(t)), 200, 1400) * (0.55 + 0.45 * np.sin(2 * np.pi * rpm_hz * 3 * t) ** 2) * 0.5
    return fade(hum + air, 0.8, 0.8)


def clock(d):
    x = np.zeros(int(d * SR))
    tk = hp(rng.standard_normal(400), 2500) * np.exp(-np.arange(400) / 60)
    for k in range(int(d)):
        i = int(k * SR)
        x[i:i + 400] += tk * (1.0 if k % 2 else 0.7)
    return x * 0.6


def phone_buzz(n=2):
    """phone vibrating on a tiled floor"""
    out = []
    for _ in range(n):
        t = T(0.42)
        motor = np.sign(np.sin(2 * np.pi * 172 * t)) * 0.4 + np.sin(2 * np.pi * 344 * t) * 0.3
        rattle = bp(rng.standard_normal(len(t)), 1500, 5000) * 0.35
        out.append(fade((motor + rattle) * (0.8 + 0.2 * np.sin(2 * np.pi * 30 * t)), 0.01, 0.03))
        out.append(np.zeros(int(0.22 * SR)))
    return np.concatenate(out) * 0.7


def ping():
    t = T(0.9)
    s = np.sin(2 * np.pi * 1318.5 * t) * np.exp(-t * 6) + np.sin(2 * np.pi * 1760 * t) * np.exp(-(t - 0.12).clip(0) * 6) * (t > 0.12)
    return s * 0.45


# ------------------------------------------------------------------ paper, coins, money
def paper_flutter(d=1.4):
    t = T(d)
    n = bp(rng.standard_normal(len(t)), 800, 6000)
    am = np.abs(np.sin(2 * np.pi * (9 + 6 * rng.random()) * t + rng.random())) ** 3
    return fade(n * am * 0.5 * np.sin(np.pi * t / d), 0.05, 0.1)


def paper_slap():
    t = T(0.25)
    return (bp(rng.standard_normal(len(t)), 300, 4000) * np.exp(-t * 30) + np.sin(2 * np.pi * 120 * t) * np.exp(-t * 40) * 0.6) * 0.9


def coin(f=None):
    t = T(0.6)
    f = f or rng.uniform(2600, 4200)
    s = sum(np.sin(2 * np.pi * f * r * t + rng.random()) * np.exp(-t * (8 + 6 * k)) / (k + 1)
            for k, r in enumerate((1.0, 1.52, 2.21, 2.93)))
    hit = hp(rng.standard_normal(len(t)), 4000) * np.exp(-t * 300) * 0.4
    return (s * 0.35 + hit)


def coins(d=2.5, n=14):
    x = np.zeros(int(d * SR) + SR)
    for _ in range(n):
        i = int(rng.uniform(0, d) * SR)
        c = coin()
        x[i:i + len(c)] += c * rng.uniform(0.3, 1.0)
    return x


def cash_flutter(d=3.0):
    """notes riffling through the air"""
    return _cash(d)


def _cash(d):
    x = np.zeros(int(d * SR))
    for _ in range(int(d * 3)):
        f = paper_flutter(rng.uniform(0.5, 1.2)) * rng.uniform(0.3, 0.8)
        i = int(rng.uniform(0, max(0.01, d - 1.2)) * SR)
        x[i:i + len(f)] += f[:len(x) - i]
    return x


# ------------------------------------------------------------------ crowds, places, machines
def crowd(d, size=1.0, cheer=True):
    t = T(d)
    walla = bp(rng.standard_normal(len(t)), 250, 2500, 3)
    walla *= 0.6 + 0.4 * lp(np.abs(rng.standard_normal(len(t))), 3)
    x = walla * 0.9
    if cheer:
        for _ in range(int(d * 6 * size)):                  # whistles and "woo"s
            dd = rng.uniform(0.3, 0.9)
            tt = T(dd)
            f0 = rng.uniform(1600, 2800)
            w = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.15 * np.sin(np.pi * tt / dd))) / SR) * np.sin(np.pi * tt / dd) * 0.15
            i = int(rng.uniform(0, max(0.01, d - dd)) * SR)
            w = w[:max(0, len(x) - i)]
            x[i:i + len(w)] += w
        claps = np.zeros(len(t))
        for i in rng.integers(0, len(t) - 400, int(d * 120 * size)):
            claps[i:i + 300] += hp(rng.standard_normal(300), 900) * np.exp(-np.arange(300) / 50) * 0.25
        x += claps
    env = np.minimum(1, t / 0.8) * np.minimum(1, (d - t) / 1.2)
    return x * env * size


def helicopter(d=5.0):
    t = T(d)
    blade = np.zeros(len(t))
    slap = lp(rng.standard_normal(1600), 300) * np.exp(-np.arange(1600) / 400)
    for i in range(0, len(t) - 1600, int(SR / 5.6)):
        blade[i:i + 1600] += slap
    turbine = np.sin(2 * np.pi * np.cumsum(1150 + 30 * np.sin(2 * np.pi * 0.3 * t)) / SR) * 0.03
    near = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 1.5           # flies over
    return (norm(blade) * 0.9 + turbine) * near


def heartbeat(d, bpm=62):
    x = np.zeros(int(d * SR))
    beat = 60 / bpm
    def thump(f, g):
        tt = T(0.25)
        return np.sin(2 * np.pi * np.cumsum(f * (1 + 0.6 * np.exp(-tt * 30))) / SR) * np.exp(-tt * 14) * g
    k = 0
    while k * beat < d - 0.5:
        i = int(k * beat * SR)
        a, b = thump(55, 1.0), thump(48, 0.7)
        x[i:i + len(a)] += a
        j = i + int(0.24 * SR)
        x[j:j + len(b)] += b[:len(x) - j]
        k += 1
    return lp(x, 160) * 1.4


def siren_far(d=6.0):
    t = T(d)
    f = 700 + 250 * np.sin(2 * np.pi * 0.35 * t)
    return lp(np.sin(2 * np.pi * np.cumsum(f) / SR), 1500) * 0.08 * np.sin(np.pi * t / d)


def match_strike():
    t = T(1.4)
    scratch = bp(rng.standard_normal(len(t)), 1500, 7000) * np.exp(-t * 18) * 1.2
    flare = lp(rng.standard_normal(len(t)), 900) * np.clip(t - 0.08, 0, None) ** 0.3 * np.exp(-t * 2.5) * 0.6
    return scratch + flare


def needle_drop():
    t = T(1.2)
    thump = np.sin(2 * np.pi * 70 * t) * np.exp(-t * 25)
    return thump * 0.9 + crackle(1.2, 40, 0.4) * np.exp(-t * 1.5) * 1.5


def crt_on():
    t = T(0.9)
    whine = np.sin(2 * np.pi * 7800 * t) * 0.04 * np.exp(-t * 2)
    static = bp(rng.standard_normal(len(t)), 500, 8000) * np.exp(-t * 4) * 0.6
    pop = np.sin(2 * np.pi * 90 * t) * np.exp(-t * 30) * 0.8
    return whine + static + pop


def shutter():
    t = T(0.18)
    a = hp(rng.standard_normal(len(t)), 2000) * (np.exp(-t * 120) + 0.6 * np.exp(-np.clip(t - 0.07, 0, None) * 140) * (t > 0.07))
    return a * 0.8


def slide_click():
    """old slide projector advancing"""
    t = T(0.5)
    clunk = lp(rng.standard_normal(len(t)), 700) * np.exp(-t * 35) * 1.2
    click = hp(rng.standard_normal(len(t)), 2500) * np.exp(-np.clip(t - 0.16, 0, None) * 160) * (t > 0.16) * 0.7
    return clunk + click


def typewriter(n, gap=0.06):
    x = np.zeros(int((n * gap + 0.4) * SR))
    for k in range(n):
        tt = T(0.05)
        c = hp(rng.standard_normal(len(tt)), 1800) * np.exp(-tt * 140) * rng.uniform(0.5, 1.0)
        i = int(k * gap * SR)
        x[i:i + len(c)] += c
    return x * 0.8


def mic_tap():
    t = T(1.0)
    one = lp(rng.standard_normal(len(t)), 500) * np.exp(-t * 18) + np.sin(2 * np.pi * 110 * t) * np.exp(-t * 12) * 0.5
    two = np.concatenate([np.zeros(int(0.45 * SR)), one[:len(t) - int(0.45 * SR)]])
    return (one + two) * 0.8


def impact():
    """trailer hit: sub drop + noise crack + metal ring"""
    t = T(2.6)
    sub = np.sin(2 * np.pi * np.cumsum(30 + 70 * np.exp(-t * 7)) / SR) * np.exp(-t * 1.6)
    crack = bp(rng.standard_normal(len(t)), 400, 6000) * np.exp(-t * 14) * 0.7
    ring = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 3) for f in (220, 331, 587)) * 0.05
    return np.tanh((sub + crack + ring) * 1.4)


def whoosh_big(d=1.0):
    t = T(d)
    n = rng.standard_normal(len(t))
    sweep = np.zeros(len(t))
    for lo, seg in zip(np.linspace(300, 3000, 8), np.array_split(np.arange(len(t)), 8)):
        sweep[seg] = bp(n[seg], lo, min(lo * 3, 18000))
    return sweep * np.sin(np.pi * t / d) ** 2 * 1.2


def reverse_swell(d=1.6):
    t = T(d)
    s = bp(rng.standard_normal(len(t)), 200, 5000) * (t / d) ** 3
    return s * 1.4
