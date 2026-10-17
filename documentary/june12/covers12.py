"""TikTok covers (1080x1920). Text stays inside the centre 3:4 area that TikTok shows on the profile grid.
usage: python3 june12/covers12.py OUT_DIR   (run from documentary/)"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

W, H = 1080, 1920
FONT = "june12/fonts/Oswald-VF.ttf"


def oswald(s):
    f = ImageFont.truetype(FONT, s)
    f.set_variation_by_name("Bold")
    return f


def stamp(text, w=620):
    f = oswald(86)
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    tw = int(tmp.textlength(text, font=f))
    im = Image.new("RGBA", (tw + 70, 140), (241, 233, 214, 255))      # cream paper label behind the ink
    d = ImageDraw.Draw(im)
    d.rectangle([5, 5, im.width - 6, 134], outline=(205, 28, 28, 255), width=10)
    d.text((im.width / 2, 72), text, font=f, fill=(205, 28, 28, 255), anchor="mm")
    a = np.asarray(im).copy()
    ink = (a[..., 0] > 150) & (a[..., 1] < 80)
    speck = np.random.default_rng(4).random(a.shape[:2]) < 0.15
    a[ink & speck, :3] = (241, 233, 214)                                # worn rubber-stamp texture
    return Image.fromarray(a).rotate(-5, expand=True, resample=Image.BICUBIC)


def cover(photo, lines, stamp_text, out, focus=(0.5, 0.35), bw=False):
    p = Image.open(photo).convert("RGB")
    if bw:
        p = ImageOps.grayscale(p).convert("RGB")
    bg = ImageOps.fit(p, (W, H), Image.LANCZOS, centering=focus).filter(ImageFilter.GaussianBlur(28))
    bg = ImageEnhance.Brightness(bg).enhance(0.35)
    # sharp photo band in the middle
    band = ImageOps.fit(p, (W, 860), Image.LANCZOS, centering=focus)
    band = ImageEnhance.Contrast(band).enhance(1.1)
    bg.paste(band, (0, 700))
    d = ImageDraw.Draw(bg)
    d.line([0, 698, W, 698], fill=(214, 172, 84), width=6)
    d.line([0, 1562, W, 1562], fill=(214, 172, 84), width=6)
    y = 300
    for txt, col, size in lines:
        s = size
        while s > 60 and d.textlength(txt, font=oswald(s)) > 960:
            s -= 4
        d.text((W / 2, y), txt, font=oswald(s), fill=col, anchor="mm", stroke_width=7, stroke_fill="black")
        y += int(s * 1.08)
    st = stamp(stamp_text)
    bg.paste(st, (int(W / 2 - st.width / 2), 1380), st)
    logo = Image.open("channel_logo.png").convert("RGBA").resize((120, 120), Image.LANCZOS)
    m = Image.new("L", logo.size, 0)
    ImageDraw.Draw(m).ellipse([2, 2, 118, 118], fill=255)
    logo.putalpha(m)
    bg.paste(logo, (W // 2 - 60, 1610), logo)
    bg.save(out, quality=93)


OUT = sys.argv[1]
WHITE, GOLD = (255, 255, 255), (255, 206, 60)
cover("june12/photos/mko-votes-june12.jpg", [("HE WON.", WHITE, 190), ("THEY CANCELLED IT.", GOLD, 120)],
      "JUNE 12, 1993", os.path.join(OUT, "cover_mko_won.jpg"), focus=(0.6, 0.3))
cover("photos/broll/abiola-portrait.jpg", [("HE TOOK", WHITE, 170), ("ONE SIP...", GOLD, 170)],
      "7 JULY 1998", os.path.join(OUT, "cover_mko_tea.jpg"), focus=(0.5, 0.35), bw=True)
cover("photos/broll/abiola-victory-1993.jpg", [("THEY OFFERED HIM", WHITE, 120), ("FREEDOM.", WHITE, 150), ("HE SAID NO.", GOLD, 150)],
      "4 YEARS IN A CELL", os.path.join(OUT, "cover_mko_offer.jpg"), focus=(0.5, 0.35))
cover("photos/broll/official-portrait-2023.jpg", [("2012: HE FOUGHT IT.", WHITE, 130), ("2023: HE DID IT.", GOLD, 130)],
      "FUEL SUBSIDY", os.path.join(OUT, "cover_uturn.jpg"), focus=(0.5, 0.3))
print("covers done")
