"""Find the exact loop point for a short.

A looping short ends on one continuous sentence, e.g. "Because back in 2012, he said it would toss
Nigerians into the depths of the midnight sea." The finished video is rotated so it STARTS at the
loop phrase ("he said ...") - the seam then sits inside a single spoken sentence and is inaudible.
This script finds the phrase's start time with Whisper word timestamps and writes BUILD/loop.json.

usage: SHORT=uturn python3 loopfix.py BUILD_DIR
"""
import json, re, sys
import numpy as np, soundfile as sf
from scipy.signal import resample_poly
from timeline import build

B = sys.argv[1]
tl, T = build(f"{B}/timing.json")


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


for e in tl:
    ph = e.get("loop_phrase")
    if not ph:
        continue
    a, sr = sf.read(f"{B}/voice/{e['id']}.wav", dtype="float32")
    a16 = resample_poly(a, 16000, sr).astype("float32")
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=4)
    segs, _ = m.transcribe(a16, language="en", word_timestamps=True)
    words = [(w.start, norm(w.word)) for s in segs for w in s.words]
    target = [norm(x) for x in ph.split()]
    hit = None
    for i in range(len(words) - len(target) + 1):
        if [w for _, w in words[i:i + len(target)]] == target:
            hit = words[i][0]  # keep the LAST occurrence
    if hit is None:  # fallback: proportional position inside the final subtitle sentence
        a0, a1, s = e["subs"][-1]
        frac = s.lower().rfind(ph.lower()) / max(len(s), 1)
        hit = (a0 - e["voice_at"]) + frac * (a1 - a0)
        print("loopfix: phrase not heard, using estimate")
    R = e["voice_at"] + hit - 0.05
    json.dump(dict(R=round(R, 3), scene=e["id"], phrase=ph), open(f"{B}/loop.json", "w"))
    print("loop point", round(R, 2), "s at", repr(ph))
