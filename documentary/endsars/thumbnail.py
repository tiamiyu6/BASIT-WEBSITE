"""YouTube thumbnail for #ENDSARS (1280x720).  usage (from documentary/): python3 endsars/thumbnail.py OUT.jpg"""
import sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

W, H = 1280, 720
F = "endsars/fonts/"
img = Image.open("endsars/photos/abk3.jpg").convert("RGB")
img = ImageOps.fit(img, (W, H), centering=(0.30, 0.35))
img = ImageEnhance.Color(img).enhance(0.55)
img = ImageEnhance.Brightness(img).enhance(0.75)
# keep the flag's green alive
src = ImageOps.fit(Image.open("endsars/photos/abk3.jpg").convert("RGB"), (W, H), centering=(0.30, 0.35))
px, sp = img.load(), src.load()
for y in range(0, H):
    for x in range(0, W):
        r, g, b = sp[x, y]
        if g > r + 35 and g > b + 25:
            px[x, y] = (int(r * 0.8), min(255, int(g * 1.1)), int(b * 0.8))
# dark on the right for the text
shade = Image.new("L", (W, H))
d = ImageDraw.Draw(shade)
for x in range(W):
    d.line([(x, 0), (x, H)], fill=int(max(0, min(235, (x - 520) * 0.55))))
img = Image.composite(Image.new("RGB", (W, H), (8, 8, 10)), img, shade)
vig = Image.new("L", (W, H), 0)
ImageDraw.Draw(vig).ellipse((-250, -200, W + 250, H + 200), fill=255)
img = Image.composite(img, Image.new("RGB", (W, H), (0, 0, 0)), vig.filter(ImageFilter.GaussianBlur(120)))
d = ImageDraw.Draw(img)


def text(xy, s, font, fill, stroke=6, anchor="ra"):
    d.text((xy[0] + 6, xy[1] + 8), s, font=font, fill=(0, 0, 0), anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))
    d.text(xy, s, font=font, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))


R = W - 50
text((R, 70), "#ENDSARS", ImageFont.truetype(F + "Anton-Regular.ttf", 64), (61, 200, 90), 4)
text((R, 150), "20.10.20", ImageFont.truetype(F + "Anton-Regular.ttf", 190), (235, 50, 45), 7)
text((R, 380), "THE NIGHT", ImageFont.truetype(F + "Anton-Regular.ttf", 92), (255, 255, 255), 5)
text((R, 485), "NIGERIA CAN'T FORGET", ImageFont.truetype(F + "Anton-Regular.ttf", 64), (255, 255, 255), 4)
f = ImageFont.truetype(F + "Anton-Regular.ttf", 40)
d.rounded_rectangle((R - 300, 600, R, 660), 8, fill=(235, 50, 45))
d.text((R - 150, 630), "6 YEARS LATER", font=f, fill=(255, 255, 255), anchor="mm")
img.save(sys.argv[1], quality=92)
