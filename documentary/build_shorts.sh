#!/usr/bin/env bash
# Build vertical looping Reels:  ./documentary/build_shorts.sh who lekki uturn
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="${WORK:-$HERE/.build}"
MODELS="$WORK/models"
cd "$HERE"
for NAME in "${@:-who lekki uturn}"; do
  B="$WORK/short_$NAME"
  mkdir -p "$B/plates"
  export SHORT="$NAME"
  python3 narrate.py "$MODELS" "$B"
  python3 audio.py "$B"
  NOSUBS=1 python3 render.py "$B" "$B/picture.mp4"
  python3 vertical.py "$B" "$HERE/reel_$NAME.mp4"
  unset SHORT
  echo "done -> $HERE/reel_$NAME.mp4"
done
