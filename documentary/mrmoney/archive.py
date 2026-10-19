"""Archive footage used in Mr Money: short credited excerpts from screen recordings the channel owner supplied.

Each entry: source file, in/out (seconds), crop box in the recording, credit line.
`python3 mrmoney/archive.py BUILD` cuts every clip to BUILD/clips/NAME/0001.jpg... (+ NAME.wav for clips with sound).
"""
import os, subprocess, sys

UP = os.environ.get("ARCHIVE_DIR", "/root/.claude/uploads/555a1255-6634-5fee-9091-b296a9cf2a9b")
UNF = "Asake Unfiltered  ·  Afrobeats Podcast / Adesope Live"
KOR = "I Met Asake, He's Very Stubborn  ·  Korty EO / Flow"
SCOPE = (696, 312, 77, 40)           # picture area inside the 848x384 recordings
KORTY = (384, 216, 0, 64)            # picture area inside the vertical recording

A1, A2, A3, A4 = "21251e27-asake1.MP4", "329307df-asake2.MP4", "585f4e35-asake3.MP4", "97caf128-asake4.MP4"
K = "e93479ac-asake_8.MP4"

CLIPS = {
    # picture + sound (played as their own moments, narration stops)
    "perfectionist": dict(src=A2, t=(0.0, 9.4), crop=SCOPE, credit=UNF, sound=True),
    "belief":        dict(src=A2, t=(32.7, 41.9), crop=SCOPE, credit=UNF, sound=True, ptrim=8.2),
    "grind":         dict(src=A1, t=(24.0, 28.6), crop=SCOPE, credit=UNF, sound=True, picture=False),
    "same":          dict(src=A4, t=(50.5, 55.4), crop=SCOPE, credit=UNF, sound=True, picture=(A4, 31.0)),
    # picture only (under narration)
    "convoy":        dict(src=A4, t=(16.0, 25.5), crop=SCOPE, credit=UNF),
    "portraits":     dict(src=A4, t=(31.0, 38.2), crop=SCOPE, credit=UNF),
    "rehearsal":     dict(src=A4, t=(0.2, 7.8), crop=SCOPE, credit=UNF),
    "fireworks":     dict(src=A2, t=(25.0, 33.0), crop=SCOPE, credit=UNF),
    "redstage":      dict(src=A2, t=(11.0, 19.8), crop=SCOPE, credit=UNF),
    "dance":         dict(src=A2, t=(5.6, 9.6), crop=SCOPE, credit=UNF),
    "stage":         dict(src=A3, t=(8.0, 19.9), crop=SCOPE, credit=UNF),
    "spot":          dict(src=A3, t=(24.4, 27.9), crop=SCOPE, credit=UNF),
    "hallway":       dict(src=A3, t=(21.0, 23.9), crop=SCOPE, credit=UNF),
    "band":          dict(src=A1, t=(5.0, 10.9), crop=SCOPE, credit=UNF),
    "beanie":        dict(src=K, t=(43.0, 47.6), crop=KORTY, credit=KOR),
    "stubborn":      dict(src=K, t=(50.2, 53.8), crop=KORTY, credit=KOR),
    "smile":         dict(src=K, t=(22.4, 23.4), crop=KORTY, credit=KOR),
}


def frames_dir(build, name):
    return os.path.join(build, "clips", name)


def cut(build):
    for name, c in CLIPS.items():
        d = frames_dir(build, name)
        t0, t1 = c["t"]
        src = os.path.join(UP, c["src"])
        if c.get("picture", True) is not False and not os.path.exists(os.path.join(d, "0001.jpg")):
            os.makedirs(d, exist_ok=True)
            psrc, pt0 = (os.path.join(UP, c["picture"][0]), c["picture"][1]) if isinstance(c.get("picture"), tuple) else (src, t0)
            w, h, x, y = c["crop"]
            subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-ss", f"{pt0}", "-t", f"{c.get('ptrim', t1 - t0)}", "-i", psrc,
                                   "-vf", f"crop={w}:{h}:{x}:{y},fps=30", "-q:v", "2", os.path.join(d, "%04d.jpg")])
        if c.get("sound"):
            wav = os.path.join(build, "clips", name + ".wav")
            if not os.path.exists(wav):
                os.makedirs(os.path.dirname(wav), exist_ok=True)
                subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0}", "-t", f"{t1 - t0}", "-i", src,
                                       "-ac", "2", "-ar", "48000", "-af", "afade=t=in:d=0.08,afade=t=out:st=%.2f:d=0.25" % (t1 - t0 - 0.25), wav])
    print("archive clips cut")


if __name__ == "__main__":
    cut(sys.argv[1])
