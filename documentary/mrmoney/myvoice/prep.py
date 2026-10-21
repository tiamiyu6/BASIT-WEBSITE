"""Step 1 of the own-voice narration: clean each phone recording (generator hum) and transcribe it word by word.

usage (from documentary/): python3 mrmoney/myvoice/prep.py RAW_DIR WORK_DIR
RAW_DIR holds rec2.wav ... rec8.wav (48 kHz mono). Writes WORK_DIR/clean<n>.wav and WORK_DIR/words<n>.json.
"""
import json, os, sys
import numpy as np, soundfile as sf, noisereduce as nr
from scipy.signal import butter, sosfiltfilt, resample_poly
from faster_whisper import WhisperModel

RAW, WORK = sys.argv[1], sys.argv[2]
os.makedirs(WORK, exist_ok=True)
HINT = ("Asake, Ololade, Lagos, WAEC, JAMB, Giran, Yoruba, Lala, Obafemi Awolowo University, OAU, Ile-Ife, TFT Records, Kanipe, "
        "Olamide, YBNL, Omo Ope, Sungba, Burna Boy, Peace Be Unto You, Terminator, danfos, Mr Money with the Vibe, Apple Music, "
        "Billboard 200, Audiomack, Brixton, O2 Academy, Rebecca Ikumelo, Gaby Hutchinson, Amapiano, Work of Art, Barclays Center, "
        "Lungu Boy, Central Cee, Stormzy, Wizkid, MMS, Why Love, Giran Republic, Drury Lane, Fuji, Ramadan, Naija Untold, parlour")
model = WhisperModel("medium", device="cpu", compute_type="int8")
for n in range(2, 9):
    if os.path.exists(f"{WORK}/words{n}.json"):
        continue
    a, sr = sf.read(f"{RAW}/rec{n}.wav", dtype="float32")
    a = sosfiltfilt(butter(4, 85, "hp", fs=sr, output="sos"), a).astype(np.float32)
    f = a[:len(a) // 2400 * 2400].reshape(-1, 2400)
    r = np.sqrt((f ** 2).mean(1))
    a = nr.reduce_noise(y=a, sr=sr, y_noise=f[r < np.percentile(r, 10)].ravel(), stationary=True, prop_decrease=0.9).astype(np.float32)
    sf.write(f"{WORK}/clean{n}.wav", a, sr)
    segs, _ = model.transcribe(resample_poly(a, 1, 3).astype(np.float32), language="en", initial_prompt=HINT,
                               beam_size=5, word_timestamps=True, vad_filter=True)
    words = [[w.word.strip(), round(w.start, 3), round(w.end, 3)] for s in segs for w in s.words]
    json.dump(words, open(f"{WORK}/words{n}.json", "w"))
    print("rec", n, len(words), "words", flush=True)
