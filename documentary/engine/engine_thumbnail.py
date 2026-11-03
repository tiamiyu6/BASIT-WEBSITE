"""Thumbnail in the 'FIRST ___?' format: big yellow outlined words across the top, picture below.
usage: python3 engine/engine_thumbnail.py PICTURE.png "FIRST ENGINE?" OUT.jpg"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "psych")
pic, words, out = sys.argv[1:4]
F = lambda s: ImageFont.truetype(os.path.join(HERE, "fonts", "LilitaOne-Regular.ttf"), s)
im = Image.open(pic).convert("RGB").resize((1280, 720), Image.LANCZOS)
d = ImageDraw.Draw(im)
size = 190
while d.textlength(words, font=F(size)) > 1180 and size > 80:
    size -= 6
f = F(size)
d.text((640, 110), words, font=f, fill=(255, 214, 40), anchor="mm", stroke_width=16, stroke_fill=(10, 10, 10))
im.save(out, quality=93)
