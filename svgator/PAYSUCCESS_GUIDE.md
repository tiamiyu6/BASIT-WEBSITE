# PAYMENT SUCCESS: SVGator × Contra challenge, entry 3

A tap-to-pay checkout microinteraction: **tap the card → processing → success tick with confetti → receipt → button.**
It works for any shop, restaurant, fintech or app. Rebranding takes **2 images (logo, product) + the texts + 1 brand colour, about 5 minutes.**

## Files (`svgator/out3/`)
| File | What it is |
|---|---|
| `paysuccess_kitchen.svg` | **Import this into SVGator.** Content set 1, Mama's Kitchen (orange). |
| `paysuccess_ankara.svg` | Same template, content set 2, Ankara Threads (teal). |
| `images/*_logo.png`, `images/*_product.png` | Logos and product pictures (original art, free to give away) |
| `preview_pay_kitchen.mp4`, `preview_pay_ankara.mp4` | **Motion reference:** copy these timings. |
| `proof_pay.mp4` | Reference proof edit: set 1 → "Same template" card → set 2 |
| `../paysuccess.py` | The script that draws everything |

The SVG opens on the **finished "success" screen**, so it looks complete as a template. The parts that appear only during the animation start at **opacity 0**: `bank-card`, `contactless`, `text-tap`, `text-processing`, `spinner`, `tap-ripple`, `burst`, `confetti` and `cta-shine`. Your keyframes bring them in.

## 1. Import
1. **New project → Import → `paysuccess_kitchen.svg`**. The canvas is 1080×1080.
2. Elements:
   - `background`
   - `screen`:
     - `header`: `logo`, `text-merchant`, `text-order`
     - `status-icon`: `contactless`, `tap-ripple`, `spinner`, `burst`, `confetti` (`confetti-1..17`), `success-circle`, `tick`
     - `text-tap`, `text-processing`, `status` (`text-status`), `amount` (`text-amount`)
     - `receipt`: `receipt-bg`, `row-1` (`product-image`, `text-item`), `row-2..4` (label + value texts)
     - `cta` (`text-cta`, `cta-shine`)
   - `bank-card`
3. **Animation length 6 s, Loop ON.** The status icon centre is **(540, 330)**. Use it as the origin for everything in `status-icon` and for `bank-card`.

## 2. Animate (match the preview)
| Time (s) | Element | Property | Keyframes | Easing |
|---|---|---|---|---|
| 0 → 0.5 | `screen` | Position Y + Opacity | +60 → 0, 0 → 100% | Ease Out Cubic |
| **Stage 1: tap** | | | | |
| 0.3 → 0.5 / 1.3 → 1.5 | `contactless`, `text-tap` | Opacity | 0 → 100% … 100% → 0 | Ease In Out |
| 0.3 → 1.5 | `contactless` | Scale | 100 → 106 → 100%, repeated (2 pulses per second) | Ease In Out |
| 0.6 → 1.2 | `bank-card` | Position (+520, +160) → (0, 0), Rotate −14° → 0, Opacity 0 → 100% | slides in | Ease Out Cubic |
| 1.2 → 1.4 | `bank-card` | Scale | 100 → 94 → 100% (the tap) | Ease In Out |
| 1.25 → 1.85 | `tap-ripple` | Scale 80 → 150%, Opacity 90 → 0% | | Ease Out |
| 1.4 → 1.75 | `bank-card` | Position (0, 0) → (+360, +380), Rotate 0 → 10°, Opacity → 0 | leaves | Ease In |
| **Stage 2: processing** | | | | |
| 1.5 → 2.75 | `spinner` | Rotate 0 → 600°; Opacity 0 → 100% (fast) … → 0% at 2.75 | | Ease In Out |
| 1.55 → 2.8 | `text-processing` | Opacity | 0 → 100% … → 0% | Ease In Out |
| **Stage 3: success** | | | | |
| 2.6 → 3.0 | `success-circle` | Scale | 0 → 100% | **Ease Out Back** |
| 2.85 → 3.2 | `tick` | **Stroke → Draw** | 0 → 100% | Ease Out Cubic |
| 2.85 → 3.3 | `burst` | Scale 70 → 120%, Opacity 100 → 0% | | Ease Out |
| 2.85 → 4.05 | `confetti-1..17` | Position: move each piece outward from the centre by about 100–160 px, plus 90 px down; Rotate ±200°; Opacity 100 → 0% in the last 0.5 s | | Ease Out Cubic |
| 2.95 → 3.3 | `status` | Opacity 0 → 100%, Position Y +18 → 0 | | Ease Out Cubic |
| 3.05 → 3.45 | `amount` | Opacity 0 → 100%, Scale 86 → 100% | | Ease Out Back |
| 3.15 → 3.5 | `receipt-bg` | Opacity 0 → 100%, Scale 94 → 100% | | Ease Out Cubic |
| 3.30 / 3.42 / 3.54 / 3.66 | `row-1` … `row-4` | Opacity 0 → 100%, Position X −34 → 0 (0.35 s each) | | Ease Out Cubic |
| 3.9 → 4.3 | `cta` | Scale | 0 → 100% | Ease Out Back · origin (540, 932) |
| 4.6 → 5.2 | `cta-shine` | Position X 0 → +560, Opacity 100% while moving | | Ease In Out |
| 5.6 → 6.0 | `screen` | Opacity | 100 → 0% (clean loop) | Ease In |

**Short on time?** Animate the confetti as one group (`confetti`: Scale 60 → 140% and Opacity 100 → 0%) instead of 17 pieces. It still reads as a burst.

## 3. Proof (second content set)
1. Export set 1 (Mama's Kitchen).
2. Swap the content:
   - `logo` → Replace image → `images/ankara_logo.png`
   - `product-image` → `images/ankara_product.png`
   - **Texts:** merchant `Ankara Threads`, order `Order #AT-0915`, amount `$64.00`, item `1 × Ankara Sneaker`, card `•••• 7303` (in both the receipt and `text-card-number`), date `19 Oct 2026, 9:15 am`, reference `AT-3QX7-08`, button `View receipt`
   - **Colour:** orange `#E4572E` → teal `#1F7A8C` (circle, spinner, button, contactless, ripple, burst, confetti). The background gradient goes `#FFF1E8 / #FFD3BD` → `#E6F4F6 / #BFE3E9`.
3. Export set 2. Cut set 1 → "Same template" card → set 2 (`proof_pay.mp4` shows the cut).

Note: Poppins has no ₦ sign, so the amount uses `NGN 25,000`. That keeps the text live and editable in every font.

## 4. Submission text
**The story**
> Payment Success is a tap-to-pay checkout animation: the card taps, the payment processes, a success tick lands with confetti, and the receipt and button slide in. Every piece is a named layer with live text and replaceable logo and product images, so any shop, restaurant or fintech can drop in its brand in about five minutes. It's best for checkout screens, payment confirmations and app demos.

**X post** (tag @SVGatorApp)
> That "payment successful" feeling, animated. 💳✅
> A tap-to-pay checkout microinteraction: swap the logo, product, amount and one colour, and it's yours.
> Made in @SVGatorApp for the #SVGatorChallenge with @contra
> [video]

## Checklist
- [ ] Live text, the names above kept, logo and product are replaceable images
- [ ] 6 s loop, public link ON
- [ ] Proof video: set 1 → set 2
- [ ] X post tagging @SVGatorApp, linked in the submission. **Submit as a separate entry** from Danfo Delivers and Adinkra Loaders (multiple entries are allowed).
