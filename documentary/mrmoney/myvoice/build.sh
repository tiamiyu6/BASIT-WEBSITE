#!/bin/bash
# Full build with Basit's own narration instead of the AI voice.
# usage (from documentary/): bash mrmoney/myvoice/build.sh RAW_DIR WORK_DIR BUILD OUT.mp4
set -e
RAW=$1; WORK=$2; B=$3; OUT=$4
python3 mrmoney/myvoice/prep.py "$RAW" "$WORK"
python3 mrmoney/myvoice/cut.py "$WORK" "$B"
python3 mrmoney/archive.py "$B"
rm -f "$B"/part_*.mp4
python3 mrmoney/engine.py "$B" "$B/picture.mp4"
STEMS=1 python3 mrmoney/score.py "$B"
ffmpeg -y -loglevel error -i "$B/picture.mp4" -i "$B/mix.wav" -map 0:v -map 1:a -c:v copy \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart "$OUT"
echo "BUILD DONE $OUT"
