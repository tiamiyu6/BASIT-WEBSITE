"""Channel logo (800x800) and banner (2560x1440, text inside the 1546x423 safe area).
usage: python3 channel_art.py "NAIJA UNTOLD"   (run from documentary/)"""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import visuals as V
NAME = (sys.argv[1] if len(sys.argv) > 1 else "NAIJA UNTOLD").upper()
GOLD, GREEN, RED = (255, 200, 40), (0, 135, 81), (200, 20, 20)
w1, w2 = NAME.split(" ", 1) if " " in NAME else (NAME, "")

# logo: gold ring, green field, two-line name
L = Image.new("RGB", (800, 800), (10, 8, 6))
d = ImageDraw.Draw(L)
d.ellipse([20, 20, 780, 780], fill=GOLD)
d.ellipse([46, 46, 754, 754], fill=(12, 40, 28))
d.ellipse([60, 60, 740, 740], outline=GREEN, width=10)
d.text((400, 330), w1, font=V.F(170 if len(w1) <= 5 else 130, "Black"), fill=GOLD, anchor="mm")
d.text((400, 480), w2, font=V.F(120 if len(w2) <= 6 else 90, "Black"), fill="white", anchor="mm")
d.rectangle([300, 570, 500, 580], fill=RED)
L.save("channel_logo.png")

# banner: dark Lagos photo backdrop, name + tagline centred in the safe area
B = Image.new("RGB", (2560, 1440), (8, 6, 4))
import numpy as np
y, x = np.mgrid[0:1440, 0:2560]
glow = np.exp(-(((x - 1280) / 1100) ** 2 + ((y - 700) / 520) ** 2))
arr = np.stack([12 + 30 * glow, 30 + 60 * glow, 22 + 40 * glow], -1).clip(0, 255).astype("uint8")
B = Image.fromarray(arr)
dd = ImageDraw.Draw(B)
for k in range(-1440, 2560, 90):  # faint adire-style diagonal pattern
    dd.line([(k, 0), (k + 1440, 1440)], fill=(40, 70, 50), width=2)
d = ImageDraw.Draw(B)
for i, c in enumerate((GREEN, (240, 240, 240), GREEN)):  # flag stripe
    d.rectangle([1280 - 120 + i * 80, 540, 1280 - 40 + i * 80, 552], fill=c)
d.text((1280, 650), NAME, font=V.F(170, "Black"), fill=GOLD, anchor="mm", stroke_width=6, stroke_fill="black")
d.text((1280, 790), "THE STORIES BEHIND NIGERIA'S POWER", font=V.F(58, "Bold"), fill="white", anchor="mm",
       stroke_width=3, stroke_fill="black")
d.text((1280, 870), "NEW DOCUMENTARY: JAGABAN", font=V.F(40, "Bold"), fill=GOLD, anchor="mm")
B.save("channel_banner.jpg", quality=90)
