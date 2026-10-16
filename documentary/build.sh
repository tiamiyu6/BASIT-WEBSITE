#!/usr/bin/env bash
# Rebuild the documentary end to end.
#   ./documentary/build.sh            -> documentary/jagaban.mp4
# Real photos: put them in documentary/photos/ named after the scene id (see script.py), e.g.
#   photos/portrait.jpg (+ photos/portrait.json {"eye": [0.47, 0.38]})  photos/gov.jpg  photos/lekki.jpg ...
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="${WORK:-$HERE/.build}"
MODELS="$WORK/models"
mkdir -p "$WORK/plates" "$MODELS"

pip install -q kokoro-onnx soundfile scipy pedalboard "geopandas==0.14.4" pyshp numpy pillow
REL=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
[ -f "$MODELS/kokoro.onnx" ] || curl -sL -o "$MODELS/kokoro.onnx" "$REL/kokoro-v1.0.int8.onnx"
[ -f "$MODELS/voices.bin" ] || curl -sL -o "$MODELS/voices.bin" "$REL/voices-v1.0.bin"

cd "$HERE"
rm -f "$WORK"/plates/*.png
python3 narrate.py "$MODELS" "$WORK"
python3 audio.py "$WORK"
python3 render.py "$WORK" "$WORK/picture.mp4"
# master: loudness-normalise to YouTube's -14 LUFS, true-peak limit, mux with picture
ffmpeg -y -loglevel error -i "$WORK/picture.mp4" -i "$WORK/mix.wav" \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest \
  -movflags +faststart "$HERE/jagaban.mp4"
python3 -c "
import json, sys; from timeline import build
tl, _ = build('$WORK/timing.json')
json.dump([dict(t=round(e['start'], 1), name=e['sub'].title()) for e in tl if e['plate'] == 'chapter'],
          open('chapters.json', 'w'), indent=1)"
ffmpeg -y -loglevel error -ss 75 -i "$HERE/jagaban.mp4" -frames:v 1 -q:v 3 "$HERE/poster.jpg"
echo "done -> $HERE/jagaban.mp4"
