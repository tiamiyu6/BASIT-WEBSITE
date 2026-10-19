#!/bin/bash
# Full build: narration -> picture -> score -> mux.   usage (from documentary/): bash mrmoney/build.sh MODELS BUILD OUT.mp4
set -e
M=$1; B=$2; OUT=$3
python3 mrmoney/narrate.py "$M" "$B"
python3 mrmoney/archive.py "$B"
python3 mrmoney/engine.py "$B" "$B/picture.mp4"
STEMS=1 python3 mrmoney/score.py "$B"
ffmpeg -y -loglevel error -i "$B/picture.mp4" -i "$B/mix.wav" -map 0:v -map 1:a -c:v copy \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart "$OUT"
echo "BUILD DONE $OUT"
