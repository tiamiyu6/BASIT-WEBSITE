#!/usr/bin/env bash
# Build vertical looping shorts.
#   ./documentary/build_shorts.sh who lekki uturn          -> reel_*.mp4      (Facebook Reels)
#   ./documentary/build_shorts.sh tt_money tt_mother tt_exile -> tiktok_*.mp4  (TikTok safe zones)
#   ./documentary/build_shorts.sh wa_sea                     -> whatsapp_*.mp4 (<30 s, 720p)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="${WORK:-$HERE/.build}"
MODELS="$WORK/models"
cd "$HERE"
for NAME in "$@"; do
  B="$WORK/short_$NAME"
  mkdir -p "$B/plates"
  rm -f "$B/loop.json"
  export SHORT="$NAME"
  case "$NAME" in
    tt_*) export PLATFORM=tiktok; OUT="$HERE/tiktok_${NAME#tt_}.mp4" ;;
    wa_*) export PLATFORM=whatsapp; OUT="$B/vertical.mp4" ;;
    *)    export PLATFORM=facebook; OUT="$HERE/reel_$NAME.mp4" ;;
  esac
  python3 narrate.py "$MODELS" "$B"
  python3 loopfix.py "$B"            # exact loop point (no-op for shorts without a loop phrase)
  python3 audio.py "$B"
  NOSUBS=1 python3 render.py "$B" "$B/picture.mp4"
  python3 vertical.py "$B" "$OUT"
  if [ "$PLATFORM" = whatsapp ]; then
    ffmpeg -y -loglevel error -i "$OUT" -t 29.9 -vf scale=720:1280 -c:v libx264 -crf 24 -preset slow \
      -c:a aac -b:a 128k -movflags +faststart "$HERE/whatsapp_${NAME#wa_}.mp4"
    OUT="$HERE/whatsapp_${NAME#wa_}.mp4"
  fi
  unset SHORT PLATFORM
  echo "done -> $OUT"
done
