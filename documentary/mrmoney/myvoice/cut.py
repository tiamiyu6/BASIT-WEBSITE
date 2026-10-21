"""Step 2 of the own-voice narration: cut Basit's best take of every line, tidy it, and write the build's voice files.

For each scene in lines.py: find the best-matching stretch of words in its recording (the last good take wins, since
re-reads come after slips), apply the start/end trims, shorten hesitations, run the broadcast voice chain, and match
the loudness of the old narration. Writes BUILD/voice/<id>.wav and BUILD/timing.json in the same format as narrate.py,
so the rest of the build (engine, score, mix) runs unchanged.

usage (from documentary/): python3 mrmoney/myvoice/cut.py WORK_DIR BUILD_DIR
"""
import difflib, json, os, re, sys
import numpy as np, soundfile as sf
from scipy.signal import resample_poly

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import narrate as N
from lines import L

WORK, BUILD = sys.argv[1], sys.argv[2]
SR_IN, SR = 48000, N.SR
TARGET_DB = -13.4          # active-speech RMS of the previous narration, so the mix keeps its balance
MAX_GAP = 0.75             # longest pause kept inside a line (hesitations get shortened to this)
NUM = {"15": "fifteen", "2:30": "two thirty", "3": "three", "4": "four", "1": "one", "1st": "first", "40": "forty"}


def norm(w):
    w = w.lower().replace("$", "o")
    w = NUM.get(w.strip(".,?!:"), w)
    return re.sub(r"[^a-z0-9]", "", w)


def tokens(text):
    return [t for t in (norm(w) for w in text.replace("-", " ").split()) if t]


def score(a, b):
    return difflib.SequenceMatcher(None, " ".join(a), " ".join(b), autojunk=False).ratio()


def find_take(words, line, need=None):
    toks = [norm(w[0]) for w in words]
    want = tokens(line)
    n, best = len(want), []
    for i in range(len(toks)):
        if not toks[i]:
            continue
        for ln in range(max(1, int(n * 0.6)), int(n * 1.5) + 2):
            j = i + ln
            if j > len(toks):
                break
            if need and not any(need in t for t in toks[i:j]):
                continue
            best.append((score(toks[i:j], want), i, j))
    top = max(s for s, _, _ in best)
    good = [c for c in best if c[0] >= top - 0.06]
    # the last good take; within it, the best-scoring window
    last_start = max(i for _, i, _ in good)
    region = [c for c in good if c[1] >= last_start - n]
    return max(region, key=lambda c: (c[0], -abs(c[2] - c[1] - n)))


def main():
    os.makedirs(f"{BUILD}/voice", exist_ok=True)
    recs, words, timing, report = {}, {}, {}, []
    for sid, entry in L.items():
        rec, text = entry[0], entry[1]
        opt = entry[2] if len(entry) > 2 else {}
        if rec not in recs:
            recs[rec], _ = sf.read(f"{WORK}/clean{rec}.wav", dtype="float32")
            words[rec] = json.load(open(f"{WORK}/words{rec}.json"))
        W = words[rec]
        sc, i, j = find_take(W, text, opt.get("need"))
        if opt.get("start"):
            i = next(k for k in range(i, j) if opt["start"] in norm(W[k][0]))
        if opt.get("end"):
            j = next(k for k in range(i, j) if opt["end"] in norm(W[k][0])) + 1
        seg = W[i:j]
        # build the line word-group by word-group, shortening long pauses
        a = recs[rec]
        lead = max(0.0, seg[0][1] - 0.12)
        tail = min(len(a) / SR_IN, seg[-1][2] + 0.28, W[j][1] - 0.04 if j < len(W) else 1e9)
        pieces, newt, t_out, cur0 = [], [], 0.0, lead
        for k, (w, s, e) in enumerate(seg):
            if k and s - seg[k - 1][2] > MAX_GAP:                      # close a group at the long pause
                cut = seg[k - 1][2] + 0.2
                pieces.append(a[int(cur0 * SR_IN):int(cut * SR_IN)])
                t_out += cut - cur0
                pieces.append(np.zeros(int((MAX_GAP - 0.4) * SR_IN), np.float32))
                t_out += MAX_GAP - 0.4
                cur0 = s - 0.2
            newt.append((w, t_out + s - cur0, t_out + e - cur0))
        pieces.append(a[int(cur0 * SR_IN):int(tail * SR_IN)])
        x = np.concatenate(pieces)
        ramp = int(0.01 * SR_IN)
        x[:ramp] *= np.linspace(0, 1, ramp)
        x[-ramp * 4:] *= np.linspace(1, 0, ramp * 4)
        x = resample_poly(x, SR, SR_IN).astype(np.float32)
        x = N.CHAIN(x[None, :], SR)[0]
        f = x[:len(x) // 480 * 480].reshape(-1, 480)
        r = np.sqrt((f ** 2).mean(1))
        act = r[r > r.max() * 0.1]
        x = x * 10 ** ((TARGET_DB - 20 * np.log10(np.sqrt((act ** 2).mean()) + 1e-9)) / 20)
        x = np.clip(x, -0.98, 0.98).astype(np.float32)
        dur = len(x) / SR
        sf.write(f"{BUILD}/voice/{sid}.wav", x, SR)
        # captions + sentence times: map the script's words onto the spoken words
        sents = N.sentences(text)
        stoks, owner = [], []
        for si, s in enumerate(sents):
            for t in tokens(s):
                stoks.append(t)
                owner.append(si)
        heard = [norm(w) for w, _, _ in newt]
        m = {}
        for blk in difflib.SequenceMatcher(None, stoks, heard, autojunk=False).get_matching_blocks():
            for q in range(blk.size):
                m[blk.a + q] = blk.b + q
        st = []
        for si in range(len(sents)):
            idx = [k for k, o in enumerate(owner) if o == si]
            hit = [m[k] for k in idx if k in m]
            if hit:
                st.append([newt[min(hit)][1], newt[max(hit)][2]])
            else:                                                       # no word matched: share the gap evenly
                st.append(None)
        for si in range(len(st)):
            if st[si] is None:
                prev = st[si - 1][1] if si else 0.0
                nxt = next((v[0] for v in st[si + 1:] if v), dur)
                st[si] = [prev + 0.05, max(prev + 0.3, nxt - 0.05)]
        st[0][0] = min(st[0][0], 0.05)
        st = [[round(max(0.0, a0), 3), round(min(dur, a1), 3)] for a0, a1 in st]
        subs = []
        for (a0, a1), s in zip(st, sents):
            parts = N.sub_split(s)
            tot = sum(len(p) for p in parts)
            u = a0
            for p in parts:
                du = (a1 - a0) * len(p) / tot
                subs.append([round(u, 3), round(u + du, 3), p])
                u += du
        timing[sid] = dict(dur=dur, subs=subs, sents=st)
        json.dump(dict(key=["myvoice", text], timing=timing[sid]), open(f"{BUILD}/voice/{sid}.json", "w"))
        report.append(f"{sid} rec{rec} match {sc:.2f} {dur:5.1f}s | {' '.join(w for w, _, _ in newt)}")
    json.dump(timing, open(f"{BUILD}/timing.json", "w"), indent=1)
    open(f"{BUILD}/myvoice_report.txt", "w").write("\n".join(report) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    main()
