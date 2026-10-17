# DANFO DELIVERS — SVGator × Contra challenge entry

A yellow Lagos danfo brakes into frame. The conductor leans out the door shouting in Pidgin, and a marquee sign drops with your offer. Your 3 products pop out of the luggage on the roof, your button pulses, then the bus drives off and the loop starts again.
Rebranding takes **1 colour + 4 texts + 3 images**, about 5 minutes.

## Files
| File | What it is |
|---|---|
| `out/danfo_kitchen.svg` | Template, content set 1 (Mama's Kitchen). **Import this into SVGator.** |
| `out/danfo_ankara.svg` | Same template, content set 2 (Ankara Threads). Use it to check your swap. |
| `out/products/*.png` | The 6 product pictures (original art, free to give away) |
| `out/proof_video.mp4` | Motion reference: set 1, then "same template", then set 2 |
| `danfo.py` | Script that draws everything (all art is original, made in code) |

Font: **Poppins** (Google Fonts, Open Font License, free to redistribute). It is embedded inside each SVG, so the text looks right in any browser or viewer. All text stays live `<text>` and is never outlined. In SVGator, if the text shows another font, select it → Font → Google Fonts → Poppins.

---

## 1. Import (2 min)
1. Open SVGator using the challenge access link (free month of Pro).
2. **New project → Import → `danfo_kitchen.svg`**. The canvas is 1080×1080.
3. Check the Elements panel. The main groups are:
   - `background`: sky, `sun-rays`, `cloud-1..3`, `skyline-far`, `beacon`, `skyline-near`, `palm-1/2`, road
   - `signboard`: `bulbs-a`, `bulbs-b`, `text-headline`, `text-subline`
   - `sparkle-1..3`, `image-1..3`
   - `danfo`: `speed-lines`, `exhaust` (`puff-0..2`), `danfo-body` (luggage, `conductor` with `conductor-arm`, `headlight-beam`, `text-brand`, `text-slogan`), `wheel-back`, `wheel-front`
   - `dust` (`dust-0..2`), `bubble` (`text-bubble`), `cta` (`cta-ripple`, `text-cta`, `cta-arrow`)
4. Click a text and check that you can retype it. If it shows as a path, re-import with "Convert text to path" OFF.
5. Set the animation length to **6.8 s** and turn **Loop** on.
6. Note: `sparkle-*`, `dust-*` and `speed-lines` start at opacity 0 on purpose. The animation reveals them.

## 2. Animate (match `out/proof_video.mp4`)
Select the element, set its transform origin, then add keyframes. **Do the main beats first. Add the "life" layers if you have time.** They make it feel alive, but the entry still works without them.

**Main beats**

| Time (s) | Element | Property | Keyframes | Easing / origin |
|---|---|---|---|---|
| 0 → 1.3 | `danfo` | Position X | −1250 → 0 | Ease Out Cubic |
| 0 → 1.3 | `wheel-back`, `wheel-front` | Rotate | 0° → 1235° | Ease Out Cubic · origin wheel centre |
| 1.3 → 1.9 | `danfo-body` | Rotate | 0 → 2.2° → −0.8° → 0 (brake nod) | Ease In Out · origin front wheel bottom (830, 858) |
| 1.45 → 1.9 | `conductor` | Rotate | −18° → 0 (leans out) | Ease Out Back · origin his feet (700, 788) |
| 1.5 → 2.25 | `signboard` | Position Y | −440 → 0 | Ease Out Bounce |
| 2.25 → 4.5 | `signboard` | Rotate | 3° → −2° → 1° → 0 (swing) | Ease In Out · origin top centre (540, 0) |
| 2.0 → 2.4 | `bubble` | Scale | 0 → 1 | Ease Out Back · origin tail tip (820, 552) |
| 2.30 / 2.46 / 2.62 (+0.5) | `image-1/2/3` | Scale 0 → 1 and Position Y +90 → 0 | | Ease Out Back · origin circle centre |
| same, +0.12 | `sparkle-1/2/3` | Scale 0.6 → 1.2 and Opacity 1 → 0 | | Ease Out |
| 3.0 → 3.45 | `cta` | Scale | 0 → 1 | Ease Out Back · origin button centre |
| 5.2 → 5.6 | `signboard`, `image-*`, `bubble`, `cta` | Opacity | 1 → 0 | Ease In |
| 5.6 → 6.8 | `danfo` | Position X | 0 → 1350 | Ease In |
| 5.6 → 6.8 | wheels | Rotate | 1235° → 2570° | Ease In |

**Life layers** (each one loops)

| Element | Property | Loop |
|---|---|---|
| `conductor-arm` | Rotate ±16° (origin shoulder 748, 642) | every 0.55 s from 1.9 s (waving) |
| `danfo-body` | Position Y ±1.2 | very fast, 1.6–5.6 s (engine idling) |
| `puff-0..2` | Scale 0.5 → 1.7, Position −70 / −26, Opacity 0.7 → 0 | every 0.9 s, offset 0.3 s each |
| `dust-0..2` | Scale 0.4 → 2, Opacity 0.8 → 0 | once at 1.25 s (brake dust) |
| `speed-lines` | Opacity 1 → 0 | 0–1.3 s, then back on 5.7–6.8 s |
| `headlight-beam` | Opacity 0.35 → 1 → 0.35 → 1 → 0.35 | 1.3–1.65 s (driver flashes the lights) |
| `bulbs-a` / `bulbs-b` | Opacity 1 ↔ 0.25, opposite phase | every 0.44 s from 2.2 s (marquee chase) |
| `image-1..3` | Position Y ±6 | every 1.6 s (floating) |
| `cta-ripple` | Scale 1 → 1.22, Opacity 0.8 → 0 | every 1.0 s from 3.4 s |
| `cta-arrow` | Position X 0 → 5 → 0 | every 0.6 s |
| `sun-rays` | Rotate 0 → 30° (origin 860, 470) | across the whole 6.8 s (rays repeat every 30°, so the loop is seamless) |
| `cloud-1..3` | Position X ±14–26 | slow drift |
| `palm-1/2` | Rotate ±2° (origin trunk base) | slow sway |
| `beacon` | Opacity 1 ↔ 0.2 | every 1 s |

## 3. Share (submission)
- **Export → Share link (public)**: this is "the template".
- Record the proof: play set 1, then swap to set 2 (step 4), play again, and screen-record both. `out/proof_video.mp4` shows exactly what it should look like.

## 4. How anyone rebrands it in 5 minutes
1. **Colour**: change one `brand-colour` element (sign frame, brand panel, image rings, CTA button and ripple, arrow, conductor's cap). Use "select same fill" to change all of them at once.
2. **Text**: double-click and retype:
   - `text-brand` (on the bus): your business name
   - `text-headline`: your offer
   - `text-subline`: one short line
   - `text-cta`: the button text
   - optional: `text-bubble` (the conductor's Pidgin call, e.g. "Oya, enter!") and `text-slogan` (bus slogan)
3. **Images**: replace `photo-1/2/3` inside `image-1..3` (square pictures work best). The circular frame crops them automatically.
4. Press play. The animation is untouched.

## 5. The story (paste into the submission)
> Danfo Delivers is a 6-second looping promo for small businesses, built around the yellow Lagos danfo bus that everyone in Nigeria knows, with the conductor's Pidgin call, the Ghana-must-go bag on the roof and the slogan painted on the side. A food vendor, fashion seller or any shop owner can swap one colour, four lines of text and three product photos and have a ready-to-post WhatsApp status, Instagram post or ad in five minutes. The art, the bus and the motion stay fixed, so every rebrand still looks finished.

## 6. The post (REQUIRED: public post on X, Instagram or LinkedIn tagging @SVGatorApp, linked in the submission; 100 likes = bonus)
> I built an animated template for small businesses in Nigeria 🇳🇬🚌
>
> The danfo drives in, your offer drops, your products pop out, and it loops.
> Swap 1 colour, 4 texts and 3 photos and you have a new brand in 5 minutes.
>
> Made for the @SVGatorApp × @contra challenge. Which business should ride the danfo next? 👇
>
> #SVGator #Contra #MotionDesign #Lagos #SmallBusiness

Attach `proof_video.mp4`. Post it in the evening (7–9 pm WAT) and ask friends to like and comment in the first hour.

## Submission status
- Template (public link): https://app.svgator.com/editor#/615395b232f04ccb9604477f1c5cbe73 (Public link: available to everyone with the link)
- Proof video: export kitchen version (MP4), then the Ankara swap, stitch both
- Story: section 5
- Post: section 6 (tag @SVGatorApp)
