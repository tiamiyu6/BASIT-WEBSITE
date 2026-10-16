"""Shared edit decision list: scene start/end times, voice offsets and transition windows."""
import json, os, subprocess
from script import S

FPS = 30
# overlap (seconds) between outgoing and incoming scene for each transition type
OVERLAP = {"fade": 1.0, "zoom": 0.6, "glitch": 0.5, "flash": 0.0, "dip": 0.0}
LEAD = {"dip": 1.1, "flash": 0.9}  # pause before narration starts


HERE = os.path.dirname(os.path.abspath(__file__))


def clip_info(sid):
    """Real footage for a scene: documentary/clips/<id>.mp4 -> (path, duration, has_audio) or None."""
    p = os.path.join(HERE, "clips", sid + ".mp4")
    if not os.path.exists(p):
        return None
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type",
                          "-of", "json", p], capture_output=True, text=True).stdout
    j = json.loads(out)
    return p, float(j["format"]["duration"]), any(s["codec_type"] == "audio" for s in j.get("streams", []))


def build(timing_path):
    timing = json.load(open(timing_path))
    out, t = [], 0.0
    for i, sc in enumerate(S):
        ov = OVERLAP[sc["trans"]] if i else 0.0
        start = max(0.0, t - ov)
        lead = LEAD.get(sc["trans"], 0.8)
        clip = clip_info(sc["id"])
        if clip:  # real footage plays first (with its own sound), then the narrator comes in
            lead += clip[1] + 0.3
        voice = timing.get(sc["id"])
        dur = (lead + voice["dur"] + sc["hold"]) if voice else sc["hold"]
        if sc["trans"] == "dip":
            dur += 0.4
        e = dict(sc, start=start, end=start + dur, dur=dur, ov=ov, voice_at=start + lead if voice else None,
                 subs=[[start + lead + a, start + lead + b, s] for a, b, s in voice["subs"]] if voice else [])
        if clip and not voice:
            e["dur"] = max(e["dur"], lead + 0.5)
            e["end"] = start + e["dur"]
        e["clip"] = clip
        e["slam_at"] = e["slam_end"] = None
        for a, b, s in e["subs"]:
            if sc.get("slam") and s.strip() == sc["slam"]:
                e["slam_at"], e["slam_end"] = a, b
        out.append(e)
        t = e["end"]
    return out, t
