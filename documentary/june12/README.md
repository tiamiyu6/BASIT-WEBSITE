# JUNE 12: The Election Nigeria Stole (Naija Untold #2)

Realistic "evidence desk" engine: every shot is a real photo, archive clip, newspaper, or a typed page.

Build (from `documentary/`):
```
B=path/to/build
python3 june12/narrate12.py MODELS_DIR $B     # Kokoro narration + sentence timings
python3 june12/score12.py $B                  # score, object sound effects, archive audio, ducking -> mix.wav
python3 june12/engine12.py $B $B/picture.mp4  # picture
ffmpeg -i $B/picture.mp4 -i $B/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k june12.mp4
```
`script12.py` holds the scenes, `SCRIPT.md` the approved script, `YOUTUBE12.md` the upload kit.
`photos/` and `clips/` (news/archive material supplied for this film) are not committed.

Assets: textures from ambientCG (CC0). Fonts: Special Elite (Apache 2.0), Playfair Display, Oswald,
Libre Baskerville, Courier Prime (SIL Open Font License), all from github.com/google/fonts.
