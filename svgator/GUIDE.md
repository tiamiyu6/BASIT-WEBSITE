# DANFO DELIVERS — SVGator × Contra challenge entry

A Lagos danfo bus drives in and a signboard drops with your offer. Your 3 products pop out of the roof and your button pulses. Then the bus drives off and the loop starts again.
Rebranding takes **1 colour + 4 texts + 3 images**, about 5 minutes.

## Files
| File | What it is |
|---|---|
| `out/danfo_kitchen.svg` | Template, content set 1 (Mama's Kitchen). **Import this into SVGator.** |
| `out/danfo_ankara.svg` | Same template, content set 2 (Ankara Threads). Use it to check your swap. |
| `out/products/*.png` | The 6 product pictures (original art, free to give away) |
| `out/proof_video.mp4` | Motion reference: set 1, then "same template", then set 2 |
| `danfo.py` | Script that draws everything (all art is original, made in code) |

Font: **Poppins** (Google Fonts, Open Font License, so it can be redistributed). All text stays live `<text>` and is never outlined.

---

## 1. Import (2 min)
1. Open SVGator using the challenge access link (free month of Pro).
2. **New project → Import → `danfo_kitchen.svg`**. The canvas is 1080×1080.
3. In the Elements panel you should see these named groups:
   `background` (sky, sun, skyline, road, road-lines) · `signboard` (text-headline, text-subline) · `image-1`, `image-2`, `image-3` · `danfo` (body, windows, stripes, brand-panel, text-brand, wheels) · `cta` (text-cta)
4. Click a text and check that you can retype it. If it shows as a path, re-import and make sure "Convert text to path" is OFF.
5. Set the animation length to **6.4 s** and turn **Loop** on.

## 2. Animate (follow the proof video)
Use the Animate panel: select the group, add the property, and set keyframes.

| Time | Group | Property | Keyframes | Easing |
|---|---|---|---|---|
| 0.0 → 1.2 s | `danfo` | Position X | −1150 → 0 | Ease Out Back |
| 0.0 → 1.2 s | `wheel-back`, `wheel-front` | Rotate | 0° → 900° | Ease Out |
| 1.2 → 1.6 s | `danfo` | Position Y | 0 → 8 → 0 (bounce) | Ease In Out |
| 1.25 → 1.95 s | `signboard` | Position Y | −430 → 0 | Ease Out Bounce |
| 1.90 → 2.30 s | `image-1` | Scale | 0 → 1 | Ease Out Back |
| 2.08 → 2.48 s | `image-2` | Scale | 0 → 1 | Ease Out Back |
| 2.26 → 2.66 s | `image-3` | Scale | 0 → 1 | Ease Out Back |
| 2.6 → 3.0 s | `cta` | Scale + Opacity | 0 → 1 | Ease Out Back |
| 3.0 → 5.0 s | `cta` | Scale | 1 → 1.08 → 1 → 1.08 → 1 (pulse) | Ease In Out |
| 5.0 → 5.4 s | `signboard`, `image-1..3`, `cta` | Opacity | 1 → 0 | Ease In |
| 5.2 → 6.2 s | `danfo` | Position X | 0 → +1300 | Ease In |
| 5.2 → 6.2 s | wheels | Rotate | 900° → 1800° | Ease In |

Tip: set each image's **transform origin to its centre** before you animate Scale, so it pops in place.

## 3. Share (submission)
- **Export → Share link (public)**: this is "the template".
- Record the proof: play set 1, then swap to set 2 (step 4), play again, and screen-record both. You can also use `out/proof_video.mp4` as the motion reference.

## 4. How anyone rebrands it in 5 minutes
1. **Colour**: select one `brand-colour` element (signboard border, brand panel, CTA button, image rings) and change its fill. Use SVGator's colour swatch / "select same fill" to change all of them at once.
2. **Text**: double-click and retype:
   - `text-brand` (on the bus): your business name
   - `text-headline`: your offer
   - `text-subline`: one short line
   - `text-cta`: the button text
3. **Images**: select `photo-1/2/3` inside `image-1..3` and replace the image (square pictures work best). The circular frame crops them automatically.
4. Press play. The animation is untouched.

## 5. The story (paste into the submission)
> Danfo Delivers is a 6-second looping promo for small businesses, built around the yellow Lagos danfo bus that everyone in Nigeria knows. A food vendor, fashion seller or any shop owner can swap one colour, four lines of text and three product photos and have a ready-to-post WhatsApp status, Instagram post or ad in five minutes. The art, the bus and the motion stay fixed, so every rebrand still looks finished.

## 6. Post for the 100-likes bonus (X / Instagram / LinkedIn)
> I built an animated template for small businesses in Nigeria 🇳🇬🚌
>
> The danfo drives in, your offer drops, your products pop out, and it loops.
> Swap 1 colour, 4 texts and 3 photos and you have a new brand in 5 minutes.
>
> Made for the @SVGator × @contra challenge. Which business should ride the danfo next? 👇
>
> #SVGator #Contra #MotionDesign #Lagos #SmallBusiness

Attach `proof_video.mp4`. Post it in the evening (7–9 pm WAT) and ask friends to like and comment in the first hour.
