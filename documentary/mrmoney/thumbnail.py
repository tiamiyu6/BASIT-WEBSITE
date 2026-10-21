"""YouTube thumbnail for MR MONEY (1280x720).  usage (from documentary/): python3 mrmoney/thumbnail.py OUT.jpg"""
import sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

W, H = 1280, 720
F = "mrmoney/fonts/"
GOLD, RED = (240, 190, 60), (225, 40, 40)
bg = Image.new("RGB", (W, H), (14, 10, 8))
glow = Image.new("L", (W, H), 0)
ImageDraw.Draw(glow).ellipse((620, -120, 1400, 820), fill=150)
bg = Image.composite(Image.new("RGB", (W, H), (120, 60, 30)), bg, glow.filter(ImageFilter.GaussianBlur(160)))
p = Image.open("mrmoney/photos/asake_toronto_1.png").convert("RGB")
p = ImageEnhance.Contrast(p).enhance(1.12)
p = p.resize((int(p.width * H * 1.08 / p.height), int(H * 1.08)))
mask = Image.new("L", p.size, 255)
d = ImageDraw.Draw(mask)
for x in range(220):                                    # soft left edge so he melts into the dark
    d.line([(x, 0), (x, p.height)], fill=int(255 * x / 220))
bg.paste(p, (W - p.width + 60, -10), mask)
d = ImageDraw.Draw(bg)


def text(xy, s, size, fill, stroke=6, font="Anton-Regular.ttf"):
    f = ImageFont.truetype(F + font, size)
    d.text((xy[0] + 6, xy[1] + 8), s, font=f, fill=(0, 0, 0), stroke_width=stroke, stroke_fill=(0, 0, 0))
    d.text(xy, s, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


# red "rejected" stamp
st = Image.new("RGBA", (560, 120), (0, 0, 0, 0))
sd = ImageDraw.Draw(st)
sd.rounded_rectangle((4, 4, 556, 116), 10, outline=RED, width=8)
sd.text((280, 60), "HIS FATHER SAID NO", font=ImageFont.truetype(F + "Anton-Regular.ttf", 62), fill=RED, anchor="mm")
st = st.rotate(-5, expand=True, resample=Image.BICUBIC)
bg.paste(st, (40, 70), st)
text((50, 230), "MR", 150, (255, 255, 255), 7)
text((50, 380), "MONEY", 200, GOLD, 8)
text((56, 620), "THE ASAKE STORY", 50, (255, 255, 255), 4)
bg.save(sys.argv[1], quality=92)
