"""YouTube thumbnail: python3 thumbnail.py thumbnail.jpg (run from documentary/)."""
import sys; sys.path.insert(0, ".")
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import visuals as V
W, H = 1280, 720
p = Image.open("photos/portrait.jpg").convert("RGB")
# background: blurred dark portrait
bg = p.resize((W, int(p.height * W / p.width))).crop((0, 0, W, H)).filter(ImageFilter.GaussianBlur(18))
bg = ImageEnhance.Brightness(bg).enhance(0.35)
# portrait on the right, full height
ph = H + 40
pw = int(p.width * ph / p.height)
face = ImageEnhance.Contrast(p.resize((pw, ph), Image.LANCZOS)).enhance(1.15)
mask = Image.new("L", (pw, ph), 255)
md = ImageDraw.Draw(mask)
for i in range(160):  # fade the left edge
    md.line([(i, 0), (i, ph)], fill=int(255 * i / 160))
bg.paste(face, (W - pw + 40, -20), mask)
# left gradient for text
grad = Image.new("L", (W, H))
gd = ImageDraw.Draw(grad)
for x in range(W):
    gd.line([(x, 0), (x, H)], fill=max(0, int(230 * (1 - x / 760))))
bg = Image.composite(Image.new("RGB", (W, H), (8, 6, 4)), bg, grad)
d = ImageDraw.Draw(bg)
GOLD = (255, 200, 40)
d.rectangle([48, 70, 372, 122], fill=(200, 20, 20))
d.text((210, 96), "FULL DOCUMENTARY", font=V.F(30, "Black"), fill="white", anchor="mm")
d.text((44, 150), "JAGABAN", font=V.F(150, "Black"), fill=GOLD, stroke_width=6, stroke_fill="black")
d.text((50, 330), "HOW HE REALLY", font=V.F(64, "Black"), fill="white", stroke_width=4, stroke_fill="black")
d.text((50, 405), "ROSE TO POWER", font=V.F(64, "Black"), fill="white", stroke_width=4, stroke_fill="black")
d.text((50, 520), "#ENDSARS · ABACHA · $460K · FUEL", font=V.F(34, "Bold"), fill=(230, 220, 200), stroke_width=3, stroke_fill="black")
d.rectangle([48, 600, 300, 608], fill=GOLD)
bg.save(sys.argv[1], quality=92)
