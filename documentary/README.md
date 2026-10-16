# JAGABAN — The Story of Bola Ahmed Tinubu

A ~10-minute documentary rendered entirely from code: script → AI narration → original score and sound design → animated picture → mastered MP4.
It plays on the site at `documentary.html`.

| File | What it does |
|---|---|
| `script.py` | The film: every scene's narration, on-screen caption, transition, music mood and sound hits |
| `narrate.py` | Narrator voice (Kokoro TTS, one sentence per take) + broadcast voice chain |
| `visuals.py` | The illustrated scenes (maps, charts, quote cards, timelines, silhouettes) |
| `audio.py` | Original score, talking drum, risers, impacts, whooshes, glitches, crowd/fire ambience, ducking |
| `render.py` | Ken Burns moves, eye push-in, flash/glitch/zoom/dip transitions, captions, subtitles, film look |
| `build.sh` | Rebuilds everything → `jagaban.mp4`, `poster.jpg`, `chapters.json` |

## Adding real photos, video and his real voice

The build session could not reach any photo or video sites, so every picture is an illustration for now.
Add your own media and run `./documentary/build.sh`, and the film uses it automatically.

**Photos** go in `documentary/photos/<scene id>.jpg`. They replace that scene's illustration and get the same slow camera move:

| Scene id | Good photo |
|---|---|
| `portrait` | **Close-up portrait of Tinubu.** The film opens on it and pushes into his eye. Add `portrait.json` with `{"eye": [x, y]}` (0–1 position of the eye in the photo) |
| `born` | Old Lagos, 1950s–60s |
| `chicago` | Chicago State University or the Chicago skyline |
| `june12` | MKO Abiola / June 12 1993 |
| `gov` | Tinubu as Governor of Lagos (1999–2007) |
| `revenue` | Lagos BRT bus |
| `machine` | Tinubu with Fashola / Sanwo-Olu |
| `occupy` | Occupy Nigeria, Gani Fawehinmi Park, Ojota, January 2012 |
| `apc` | APC merger, 2013 |
| `endsars`, `lekki` | #EndSARS protests / Lekki toll gate, October 2020 |
| `emilokan` | Abeokuta speech, June 2022 |
| `results`, `court` | INEC declaration / Supreme Court |
| `sworn` | Inauguration at Eagle Square, 29 May 2023 |
| `protest` | #EndBadGovernance, August 2024 |

**Video with his real voice** goes in `documentary/clips/<scene id>.mp4`. The clip plays first with its own sound (marked "ARCHIVE FOOTAGE"), then the narrator continues.
The strongest picks are the real moments the film quotes:
- `clips/emilokan.mp4`: "Emi lo kan", Abeokuta, June 2022
- `clips/sworn.mp4`: "Fuel subsidy is gone", inaugural speech, 29 May 2023
- `clips/occupy.mp4`: Occupy Nigeria, 2012

Keep clips short (5–15 s). Use footage you have the right to use. Short news excerpts in a commentary documentary are usually fair use, but check before you publish.

## Accuracy notes
Allegations are attributed and paired with Tinubu's denial. Figures come from INEC (2023 results), NBS (inflation) and CBN (exchange rate).
The 2012 quote, "The government has tossed the people into the depths of the midnight sea", comes from Tinubu's January 2012 article opposing President Jonathan's removal of the subsidy.
