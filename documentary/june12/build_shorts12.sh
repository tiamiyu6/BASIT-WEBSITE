#!/usr/bin/env bash
# June 12 TikToks:  ./june12/build_shorts12.sh MODELS_DIR WORK_DIR tea won offer   (run from documentary/)
set -euo pipefail
MODELS="$1"; WORK="$2"; shift 2
export J12_SCRIPT=shorts12 J12_MUSIC="${J12_MUSIC:-$(dirname "$WORK")/music}"
for NAME in "$@"; do
  B="$WORK/j12short_$NAME"; mkdir -p "$B"
  export SHORT12="$NAME"
  python3 june12/narrate12.py "$MODELS" "$B"
  python3 june12/score12.py "$B"
  NOSUBS=1 python3 june12/engine12.py "$B" "$B/picture.mp4"
  python3 june12/vertical12.py "$B" "tiktok_mko_$NAME.mp4"
  echo "done -> tiktok_mko_$NAME.mp4"
done
