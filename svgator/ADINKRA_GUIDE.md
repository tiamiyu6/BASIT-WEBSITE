# ADINKRA LOADERS: SVGator × Contra challenge, entry 2

Six loaders built on West African symbols (Adinkra from Ghana, the Nigerian gángan talking drum, kente weave), ready for any app or website.
Use the whole board as a loading screen, or delete five tiles and keep one. Rebranding takes **1 logo + 2 texts + 2 colours, about 5 minutes**.

## Files (`svgator/out2/`)
| File | What it is |
|---|---|
| `adinkra_adire.svg` | **Import this into SVGator.** Content set 1, "Adire Studio" (dark indigo + gold). |
| `adinkra_lumo.svg` | Same template, content set 2, "Lumo Pay" (light + green). Use it to check your swap. |
| `logos/adire.png`, `logos/lumo.png` | The two logos (original art, free to give away) |
| `preview_adire.mp4`, `preview_lumo.mp4` | **Motion reference:** copy these timings. |
| `proof_adinkra.mp4` | Reference proof edit: set 1 → "Same template" card → set 2 |
| `../adinkra.py` | The script that draws everything (all art is original, made in code) |

The font is **Poppins** (Open Font License). It's embedded in the SVG, and all text is live `<text>`, so it stays editable.

---

## 1. Import (2 min)
1. In SVGator: **New project → Import → `adinkra_adire.svg`**. The canvas is 1080×1080.
2. Check the Elements panel:
   - `background` (with `pattern`)
   - `header`: `logo`, `text-brand`, `text-tagline`, `text-kit`
   - `tiles`: `tile-1` … `tile-6`. Each tile has `tile-bg-N`, `loader-<name>`, `text-name-N` and `text-meaning-N`.
3. Click `text-brand` and retype a letter to check it's live text. If it imported as a path, re-import with "Convert text to path" OFF.
4. **Animation length: 2.4 s. Turn Loop ON.** Every loader is made to loop seamlessly at 2.4 s.

> **Tip:** each loader's centre is its tile centre moved up 38 px. Tile centres are (195, 420), (540, 420), (885, 420), (195, 790), (540, 790), (885, 790). Set every transform origin at the loader's centre unless the table says otherwise.

## 2. Animate the six loaders
Times are in seconds inside the 2.4 s loop. "Ease In Out" is SVGator's *Ease In Out Cubic*.

### Loader 1: `loader-adinkrahene` (rings breathe outward)
| Element | Property | Keyframes | Easing |
|---|---|---|---|
| `ring-1` | Scale | 0 s 100% → 0.6 s 112% → 1.2 s 100% | Ease In Out |
| `ring-1` | Opacity | 0 s 35% → 0.6 s 100% → 1.2 s 35% | Ease In Out |
| `ring-2` | same as ring-1, **start 0.29 s later** | | |
| `ring-3` | same as ring-1, **start 0.58 s later** | | |
| `logo-mark` | Rotate | 0 s 0° → 2.4 s 360° | Ease In Out |
Origin for all: (195, 382).

### Loader 2: `loader-nkyinkyim` (the twisting path draws itself)
| Element | Property | Keyframes | Easing |
|---|---|---|---|
| `zigzag` | **Stroke → Draw** (stroke offset) | 0 s: draw 0% → 1.2 s: 100% (drawn from the start) → 2.4 s: erased from the start | Ease In Out |
| `zigzag-dot` | **Motion path** along the zigzag | 0 → 1.2 s travels to the end, then waits there | Ease In Out |

In SVGator: select `zigzag` → Animate → **Stroke** → *Draw* (start 0 → end 100), then for the second half animate *start* 0 → 100. If motion path is fiddly, skip the dot. The drawing line alone already works.

### Loader 3: `loader-akoma` (heartbeat)
| Element | Property | Keyframes | Easing |
|---|---|---|---|
| `akoma-heart` | Scale | 0 s 100% → 0.17 s 114% → 0.34 s 100% → 0.6 s 114% → 0.77 s 100% (then rest until 2.4) | Ease Out |
| `akoma-ripple` | Scale | 0 s 100% → 1.44 s 145% | Ease Out |
| `akoma-ripple` | Opacity | 0 s 80% → 1.44 s 0% | Ease Out |
Origin: (885, 398), the middle of the heart.

### Loader 4: `loader-dwennimmen` (the ram's horns curl in)
| Element | Property | Keyframes | Easing |
|---|---|---|---|
| `horn-left`, `horn-right` | **Stroke → Draw** | 0 s 0% → 1.08 s 100% → hold → 1.68 s 100% → 2.4 s 0% | Ease In Out |
| `horns` | Rotate | 0 s 0° → 0.6 s 10° → 1.8 s −10° → 2.4 s 0° | Ease In Out |
Origin: (195, 752).

### Loader 5: `loader-kente` (the weave slides through the bar)
| Element | Property | Keyframes | Easing |
|---|---|---|---|
| `kente-weave` | Position X | 0 s 0 → 2.4 s +80 | **Linear** (this makes the loop seamless) |
`text-percent` (72%) is editable text. Change the number, or delete it for an endless loader.

### Loader 6: `loader-gangan` (the talking drum hits twice)
| Element | Property | Keyframes | Easing |
|---|---|---|---|
| `drum` | Scale | 0 s 100% → 0.14 s 94% → 0.29 s 100%, and again 1.2 → 1.34 → 1.49 s | Ease Out |
| `drum` | Rotate | same times: 0° → −4° → 0° | Ease Out |
| `wave-1`, `wave-2`, `wave-3` | Opacity | 0% → 100% → 0% over 1.2 s, then repeat. Start each wave 0.12 s after the previous one. | Ease In Out |
| `wave-1..3` | Position X | 0 → +10 over the same 1.2 s | Ease Out |
Drum origin: (885, 752).

### Optional intro (only if you have time)
`tile-1` … `tile-6`: Scale 0 → 100% (Ease Out Back) over 0.45 s, each tile starting 0.08 s after the one before. **Skip this if the loop starts to look odd.** The loaders are the entry.

## 3. Make the proof (the "second content set")
Do the swap inside the same SVGator project:
1. **Export** the animation (Export → Video/MP4 or GIF) in the Adire colours. That's clip 1.
2. **Swap the content:**
   - `logo` → right-click → **Replace image** → `logos/lumo.png`. Do the same for the small logo inside `logo-mark`.
   - `text-brand` → `LUMO PAY`
   - `text-tagline` → `securing your payment`
   - **Colours:** gold `#E8B84A` → green `#00A86B`, terracotta `#E2603A` → navy `#0B2545`, background `#15112B` → `#EEF4F1`, tiles `#1E1838` → `#FFFFFF`, text `#F5EEE0` → `#0B2545`.
   - **Fast way:** select all → Fill → change the swatch. SVGator lists the colours used in the project.
3. Export again. That's clip 2.
4. Put them together as clip 1 → a "Same template" card → clip 2. `proof_adinkra.mp4` shows exactly this cut.

## 4. Submission text
**The story (2–3 sentences)**
> Adinkra Loaders is a loading-screen kit of six loaders drawn from West African symbols: Adinkrahene (greatness), Nkyinkyim (life's twists), Akoma (patience), Dwennimmen (strength), a sliding kente weave and the Nigerian gángan talking drum. Each loader is a separately named group with live text and a replaceable logo, so a fintech, store or app can drop in its brand and two colours in about five minutes. Built for apps, checkouts and splash screens that want their waiting time to feel like home.

**X post** (tag @SVGatorApp)
> Waiting can carry meaning too. ✨
> Adinkra Loaders: 6 loading animations built on West African symbols (Adinkra, kente, the talking drum). Drop in your logo + 2 colours and ship it.
> Made in @SVGatorApp for the #SVGatorChallenge with @contra
> [video]

## Checklist
- [ ] Text is live (not outlined)
- [ ] All the names above are kept (don't regroup and lose the names)
- [ ] The logo is an image element you can replace
- [ ] Loop ON, 2.4 s
- [ ] Public link ON (Share → Public link)
- [ ] Proof video: set 1 → set 2
- [ ] X post with the video, tagging @SVGatorApp, linked in the submission
