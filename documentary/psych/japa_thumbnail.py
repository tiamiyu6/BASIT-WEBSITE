"""Japa thumbnail 1280x720 JPG: python3 psych/japa_thumbnail.py IMG_DIR OUT.jpg"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
IMGS, OUT = sys.argv[1:3]
F = lambda s: ImageFont.truetype(os.path.join(HERE, "fonts", "LilitaOne-Regular.ttf"), s)
im = Image.open(os.path.join(IMGS, "28.png")).convert("RGB").resize((1280, 720), Image.LANCZOS)
sh = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
d = ImageDraw.Draw(sh)
for y in range(330, 720):                                  # dark fade at the bottom for the text
    d.line((0, y, 1280, y), fill=(20, 12, 8, int(225 * (y - 330) / 390)))
im = Image.alpha_composite(im.convert("RGBA"), sh).convert("RGB")
d = ImageDraw.Draw(im)
def t(xy, s, f, fill, st=9):
    d.text((xy[0] + 5, xy[1] + 6), s, font=f, fill=(20, 12, 8), anchor="mm", stroke_width=st, stroke_fill=(20, 12, 8))
    d.text(xy, s, font=f, fill=fill, anchor="mm", stroke_width=st, stroke_fill=(20, 12, 8))
t((640, 470), "WHY NIGERIANS", F(100), (255, 255, 255))
t((640, 595), "REALLY JAPA", F(120), (255, 205, 60))
b = Image.new("RGBA", (1280, 720), (0, 0, 0, 0)); bd = ImageDraw.Draw(b)
bd.rounded_rectangle((20, 20, 420, 92), 18, fill=(244, 232, 208, 235), outline=(40, 30, 25), width=4)
bd.text((220, 57), "THE PSYCHOLOGY", font=F(46), fill=(40, 30, 25), anchor="mm")
im = Image.alpha_composite(im.convert("RGBA"), b).convert("RGB")
im.save(OUT, quality=92)
