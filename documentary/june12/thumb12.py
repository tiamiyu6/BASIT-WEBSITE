"""June 12 thumbnail: python3 june12/thumb12.py OUT.jpg (run from documentary/)."""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps, ImageFont
import numpy as np
W, H = 1280, 720
F = "june12/fonts/"
def oswald(s):
    f = ImageFont.truetype(F + "Oswald-VF.ttf", s); f.set_variation_by_name("Bold"); return f
mko = Image.open("june12/photos/mko-votes-june12.jpg").convert("RGB")
mko = ImageOps.fit(mko, (760, 720), Image.LANCZOS, centering=(0.62, 0.3))
mko = ImageEnhance.Contrast(mko).enhance(1.12)
mko = ImageEnhance.Color(mko).enhance(1.15)
bg = Image.open("june12/textures/Paper006.jpg").convert("RGB")
bg = ImageOps.fit(bg, (W, H), Image.LANCZOS)
bg = ImageEnhance.Brightness(bg).enhance(0.32)
img = bg.copy()
m = Image.new("L", (760, 720), 255)
md = ImageDraw.Draw(m)
for i in range(180):
    md.line([(i, 0), (i, 720)], fill=int(255 * i / 180))
img.paste(mko, (W - 760, 0), m)
d = ImageDraw.Draw(img)
def txt(xy, s, f, fill, sw=6):
    d.text(xy, s, font=f, fill=fill, stroke_width=sw, stroke_fill="black")
txt((46, 40), "HE WON.", oswald(190), (255, 255, 255))
txt((46, 270), "THEY", oswald(110), (255, 206, 60))
txt((46, 390), "CANCELLED IT.", oswald(110), (255, 206, 60))
# rubber stamp
st = Image.new("RGBA", (520, 140), (0, 0, 0, 0))
sd = ImageDraw.Draw(st)
sd.rectangle([5, 5, 514, 134], outline=(200, 26, 26, 255), width=10)
sd.text((260, 72), "JUNE 12, 1993", font=oswald(84), fill=(200, 26, 26, 255), anchor="mm")
a = np.asarray(st).copy()
rng = np.random.default_rng(3)
a[..., 3] = (a[..., 3] * (rng.random(a.shape[:2]) > 0.15)).astype(np.uint8)
st = Image.fromarray(a).rotate(-5, expand=True, resample=Image.BICUBIC)
img.paste(st, (40, 528), st)
img.save(sys.argv[1], quality=93)
