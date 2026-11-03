"""Fast-cut explainer builder: grids -> 4 panels each -> 3 to 4 shots per panel, cut every ~1.8 s, voice + soft music.

usage (from documentary/): python3 engine/engine_build.py MODELS IMG_DIR BUILD OUT.mp4
IMG_DIR holds the grids 01.png ... NN.png (ChatGPT pictures, 2 by 2 panels). Panels are cut into IMG_DIR/../panels.
Missing grids are skipped (PARTIAL preview). Env: CAPTIONS=1 burns word captions (TikTok version), default off like the studied format.
"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf
from PIL import Image

MODELS, IMGS, BUILD, OUT = sys.argv[1:5]
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import importlib.util
spec = importlib.util.spec_from_file_location("ef", os.path.join(HERE, "dangote2_full.py"))
ef = importlib.util.module_from_spec(spec); spec.loader.exec_module(ef)
W, H, FPS, SR = 1920, 1080, 30, ef.SR
CAPTIONS = os.environ.get("CAPTIONS") == "1"
SHOT = float(os.environ.get("SHOT", "1.8"))          # target seconds per shot
rng = np.random.default_rng(11)


def slice_grid(path):
    im = Image.open(path).convert("RGB"); w, h = im.size
    a = np.asarray(im).astype(int)
    cx = w // 2 + int(np.argmax(a[:, w // 2 - 25:w // 2 + 25, :].mean(axis=(0, 2)))) - 25
    cy = h // 2 + int(np.argmax(a[h // 2 - 25:h // 2 + 25, :, :].mean(axis=(1, 2)))) - 25
    m = 10
    return [im.crop(b) for b in [(m, m, cx - m, cy - m), (cx + m, m, w - m, cy - m), (m, cy + m, cx - m, h - m), (cx + m, cy + m, w - m, h - m)]]


def main():
    lines = ef.script_lines()
    items, vdir = ef.narrate(lines)
    sl = json.load(open(os.path.join(HERE, "scene_lines.json")))
    panels = {}
    if os.environ.get('INDIVIDUAL') == '1':                                          # one full-size picture per scene
        for sc in range(1, 77):
            q = os.path.join(IMGS, f'{sc:02d}.png')
            if os.path.exists(q):
                panels[sc] = Image.open(q).convert('RGB')
    for g in range(1, 1 if os.environ.get('INDIVIDUAL') == '1' else 20):
        p = os.path.join(IMGS, f"{g:02d}.png")
        if os.path.exists(p):
            for k, pn in enumerate(slice_grid(p)):
                panels[(g - 1) * 4 + k + 1] = pn
    if not panels:
        sys.exit("no grids found")
    for g in range(1, 20):                                                          # a missing grid reuses the previous grid's panels
        for k in range(4):
            n = (g - 1) * 4 + k + 1
            if n not in panels:
                panels[n] = panels[max(x for x in panels if x < n)] if any(x < n for x in panels) else panels[min(panels)]
    last = 76
    GAP = 0.45
    t = 0.6; scenes = []; clips = []; words = []
    for s in range(1, last + 1):
        t0 = t
        for n in sl[str(s)]:
            it = items[str(n)]
            clips.append((t, os.path.join(vdir, f"{n:02d}.wav")))
            words += [(w_, t + a, t + b) for w_, a, b in it["words"]]
            t += it["dur"] + GAP
        scenes.append((s, t0, t))
    total = t + (10.0 if last == 76 else 1.5)
    # shots
    shots = []
    for s, t0, t1 in scenes:
        end = t1 if s < last or last < 64 else total
        n = max(1, round((end - t0) / SHOT)); d = (end - t0) / n
        kinds = [("wide", 1.0, 1.10, 0.5, 0.5), ("zoom", 1.25, 1.38, 0.30, 0.45), ("zoom", 1.25, 1.38, 0.70, 0.5), ("zoom", 1.2, 1.32, 0.5, 0.35)]
        order = [0] + list(rng.permutation([1, 2, 3]))
        for i in range(n):
            k = kinds[order[i % 4]]
            shots.append((s, t0 + i * d, t0 + (i + 1) * d, k))
    mix = np.zeros(int(total * SR))
    for st, p in clips:
        a, _ = sf.read(p, dtype="float32"); i = int(st * SR); mix[i:i + len(a)] += a[:len(mix) - i]
    mix += ef.music(total)
    sf.write(os.path.join(BUILD, "mix.wav"), np.clip(mix, -1, 1), SR)
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-i", os.path.join(BUILD, "mix.wav"), "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
                            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    si = 0
    for f in range(int(total * FPS)):
        tt = f / FPS
        while si + 1 < len(shots) and shots[si][2] <= tt:
            si += 1
        s, a, b, (kind, z0, z1, fx, fy) = shots[si]
        p = min(1.0, max(0.0, (tt - a) / max(0.2, b - a)))
        z = z0 + (z1 - z0) * p
        src = panels[s]; sw, sh = src.size
        bw, bh = sw / z, sh / z
        cx = min(max(fx * sw, bw / 2), sw - bw / 2); cy = min(max(fy * sh, bh / 2), sh - bh / 2)
        img = src.resize((W, H), Image.BICUBIC, box=(cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2))
        if CAPTIONS:
            ef.caption(img, words, tt)
        enc.stdin.write(img.tobytes())
    enc.stdin.close(); enc.wait()
    print("JAPA DONE", round(total, 1), "s", "scenes", last, "shots", len(shots), OUT)


if __name__ == "__main__":
    main()
