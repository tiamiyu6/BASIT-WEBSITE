"""Narration for JUNE 12: Kokoro TTS one sentence per take, broadcast voice chain.
Writes BUILD/voice/<id>.wav and BUILD/timing.json with sentence start times (for picture cuts) and subtitles.

usage: python3 june12/narrate12.py MODELS_DIR BUILD_DIR      (run from documentary/)
"""
import json, os, re, sys
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import narrate as N  # voice chain, respellings, trimming and subtitle splitting from JAGABAN
from script12 import S

MODELS, BUILD = sys.argv[1], sys.argv[2]
VOICE, SPEED, SR = N.VOICE, 0.95, N.SR
SAY = dict(N.SAY)
SAY.update({
    "June 12": "June twelve", "Kashimawo": "Kah-shee-mah-woe", "Olawale": "Oh-lah-wah-leh", "ITT": "I T T",
    "Aare Ona Kakanfo": "Ah-reh Oh-nah Kah-kahn-foh", "Yorubaland": "Yoruba land", "MKO": "M K O",
    "Babangida": "Bah-bahn-gee-dah", "Option A4": "Option A four", "Hope '93": "Hope ninety-three",
    "Babagana": "Bah-bah-gah-nah", "Kingibe": "King-ee-beh", "Borno": "Bor-no", "Tofa": "Toe-fah",
    "Bashir": "Bah-sheer", "NRC": "N R C", "Sowore": "Show-woh-reh", "Omoyele": "Oh-moh-yeh-leh",
    "Epetedo": "Eh-peh-teh-doh", "Enahoro": "Eh-nah-ho-ro", "Adesanya": "Ah-deh-sahn-yah",
    "Soyinka": "Shoy-in-kah", "Kudirat": "Koo-dee-raht", "Hamza al-Mustapha": "Ham-zah al Moos-tah-fah",
    "Aso Rock": "Ah-so Rock", "Abdulsalami": "Ab-dool-sah-lah-mee", "Muhammadu": "Moo-ham-mah-doo",
    "GCFR": "G C F R", "NADECO": "Nah-deh-co", "Jos": "Joss",
})


def main():
    k = Kokoro(os.path.join(MODELS, "kokoro.onnx"), os.path.join(MODELS, "voices.bin"))
    os.makedirs(f"{BUILD}/voice", exist_ok=True)
    timing = {}
    for sc in S:
        if not sc.get("text"):
            continue
        meta = f"{BUILD}/voice/{sc['id']}.json"
        key = [sc["text"], VOICE, SPEED, 3]
        if os.path.exists(meta) and json.load(open(meta))["key"] == key:
            timing[sc["id"]] = json.load(open(meta))["timing"]
            continue
        pieces, subs, sents, t = [], [], [], 0.0
        for sent in N.sentences(sc["text"]):
            spoken = sent
            for a, b in sorted(SAY.items(), key=lambda kv: -len(kv[0])):
                spoken = spoken.replace(a, b)
            a, _ = k.create(spoken, voice=VOICE, speed=SPEED, lang="en-gb")
            a = N.trim(a)
            d = len(a) / SR
            sents.append([round(t, 3), round(t + d, 3)])
            parts = N.sub_split(sent)
            total = sum(len(p) for p in parts)
            u = t
            for p in parts:
                du = d * len(p) / total
                subs.append([round(u, 3), round(u + du, 3), p])
                u += du
            gap = 0.5 if sent.endswith((".", "?")) else 0.28
            pieces += [a, np.zeros(int(gap * SR), np.float32)]
            t += d + gap
        audio = np.concatenate(pieces).astype(np.float32)
        audio = N.CHAIN(audio[None, :], SR)[0]
        sf.write(f"{BUILD}/voice/{sc['id']}.wav", audio, SR)
        timing[sc["id"]] = dict(dur=len(audio) / SR, subs=subs, sents=sents)
        json.dump(dict(key=key, timing=timing[sc["id"]]), open(meta, "w"))
        print(sc["id"], round(len(audio) / SR, 1), flush=True)
    json.dump(timing, open(f"{BUILD}/timing.json", "w"), indent=1)


if __name__ == "__main__":
    main()
