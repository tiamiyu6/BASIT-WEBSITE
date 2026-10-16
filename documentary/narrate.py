"""Narration: Kokoro TTS, one full sentence per take for natural prosody, then a broadcast voice chain
(high-pass, warmth, presence, de-ess, compression, limiter).  -> build/voice/<id>.wav + build/timing.json

usage: python3 narrate.py MODELS_DIR BUILD_DIR
"""
import json, os, re, sys
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
from pedalboard import (Pedalboard, HighpassFilter, LowShelfFilter, PeakFilter, HighShelfFilter,
                        Compressor, Limiter, Gain)
from script import S

MODELS, BUILD = sys.argv[1], sys.argv[2]
VOICE, SPEED, SR = "bm_george", 0.92, 24000
# phonetic respellings so the narrator pronounces Nigerian names properly (display text is unchanged)
SAY = {"#EndSARS": "End SARS", "#EndBadGovernance": "End Bad Governance", "Emi lo kan": "Emmy law kahn",
       "Sanwo-Olu": "Sanwo Olu", "Lagos–Calabar": "Lagos Calabar", "Shettima": "Shetteema",
       "Abibatu": "Ah-bee-bah-too", "Tinubu": "Tinoobu", "Jagaban": "Jahgahbahn", "Abeokuta": "Ah-beh-oh-kootah",
       "Osinbajo": "Oh-sin-bah-joe", "Fashola": "Fah-show-lah", "Ambode": "Am-bo-day", "Akinwunmi": "Akin-woon-mi",
       "Babajide": "Bah-bah-jee-day", "Moshood": "Mo-shood", "Abiola": "Ah-bee-oh-lah", "Kwankwaso": "Kwan-kwah-so",
       "Fubara": "Foo-bah-rah", "Borgu": "Bor-goo", "Babatunde": "Bah-bah-toon-day", "Mogaji": "Mo-gah-jee",
       "naira": "nyra", "Agbeze": "Ag-beh-zeh", "Ifeanyi": "Ee-feh-ahn-yee", "Ondo": "On-doh", "Eko": "Eh-koh", "Awori": "Ah-wo-ree", "Oyo": "Oh-yo", "Ife": "Ee-feh",
       "Kanuri": "Kah-noo-ree", "Ibibio": "Ee-bee-bee-oh", "Kanem-Bornu": "Kah-nem Bor-noo", "Nupe": "Noo-peh",
       "Biafra": "Bee-ah-fra", "Sokoto": "So-ko-toe", "NADECO": "Nah-deh-co", "Atiku": "Ah-tee-koo"}

CHAIN = Pedalboard([
    HighpassFilter(80),
    LowShelfFilter(cutoff_frequency_hz=170, gain_db=3.0),     # chest / warmth
    PeakFilter(cutoff_frequency_hz=420, gain_db=-2.0, q=1.0),  # clear boxiness
    PeakFilter(cutoff_frequency_hz=3200, gain_db=2.5, q=0.8),  # presence / intelligibility
    PeakFilter(cutoff_frequency_hz=7000, gain_db=-3.0, q=2.5), # tame sibilance
    HighShelfFilter(cutoff_frequency_hz=11000, gain_db=1.5),   # air
    Compressor(threshold_db=-20, ratio=3.0, attack_ms=8, release_ms=120),
    Gain(4.0),
    Limiter(threshold_db=-1.5, release_ms=80),
])


def sentences(text):
    return [s for s in re.split(r"(?<=[.?:])\s+", text.strip()) if s]


def sub_split(sent):
    """Split a long sentence into subtitle-sized pieces at commas."""
    if len(sent) <= 95:
        return [sent]
    out, cur = [], ""
    for p in re.split(r"(?<=,)\s+", sent):
        if cur and len(cur) + len(p) > 95:
            out.append(cur)
            cur = p
        else:
            cur = (cur + " " + p).strip()
    return out + ([cur] if cur else [])


def trim(a, thr=0.008):
    idx = np.where(np.abs(a) > thr)[0]
    return a[max(0, idx[0] - 600): idx[-1] + 2400] if len(idx) else a


def main():
    k = Kokoro(os.path.join(MODELS, "kokoro.onnx"), os.path.join(MODELS, "voices.bin"))
    os.makedirs(f"{BUILD}/voice", exist_ok=True)
    timing = {}
    for sc in S:
        if not sc["text"]:
            continue
        meta = f"{BUILD}/voice/{sc['id']}.json"
        key = [sc["text"], VOICE, SPEED, 2]
        if os.path.exists(meta) and json.load(open(meta))["key"] == key:
            timing[sc["id"]] = json.load(open(meta))["timing"]
            continue
        pieces, subs, t = [], [], 0.0
        for sent in sentences(sc["text"]):
            spoken = sent
            for a, b in SAY.items():
                spoken = spoken.replace(a, b)
            a, _ = k.create(spoken, voice=VOICE, speed=SPEED, lang="en-gb")
            a = trim(a)
            d = len(a) / SR
            parts = sub_split(sent)
            total = sum(len(p) for p in parts)
            u = t
            for p in parts:  # subtitle timing proportional to text length within the sentence
                du = d * len(p) / total
                subs.append([round(u, 3), round(u + du, 3), p])
                u += du
            gap = 0.55 if sent.endswith((".", "?")) else 0.3
            pieces += [a, np.zeros(int(gap * SR), np.float32)]
            t += d + gap
        audio = np.concatenate(pieces).astype(np.float32)
        audio = CHAIN(audio[None, :], SR)[0]
        sf.write(f"{BUILD}/voice/{sc['id']}.wav", audio, SR)
        timing[sc["id"]] = dict(dur=len(audio) / SR, subs=subs)
        json.dump(dict(key=key, timing=timing[sc["id"]]), open(meta, "w"))
        print(sc["id"], round(len(audio) / SR, 1), flush=True)
    json.dump(timing, open(f"{BUILD}/timing.json", "w"), indent=1)


if __name__ == "__main__":
    main()
