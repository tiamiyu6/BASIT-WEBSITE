"""DANFO DELIVERS: an SVGator template entry (SVGator x Contra challenge).

Writes, for each content set:
  danfo_<set>.svg        the static template artwork to drag into SVGator (named layers, live text, embedded images)
  products/<set>_<n>.png the product images (original illustrations)
and a preview video of the intended animation (preview_<set>.mp4) as a motion reference.

usage: python3 svgator/danfo.py OUT_DIR [--preview]
"""
import base64, io, math, os, subprocess, sys
import cairosvg
from PIL import Image

W = H = 1080
FONT = "Poppins"
YELLOW, INK, GLASS = "#F7C100", "#1D1D22", "#2B3A55"

SETS = {
    "kitchen": dict(brand="#E4572E", name="MAMA'S KITCHEN", headline="NOW DELIVERING",
                    sub="Hot jollof, straight to your door", cta="ORDER NOW", products=["jollof", "puffpuff", "zobo"]),
    "ankara": dict(brand="#1F7A8C", name="ANKARA THREADS", headline="NEW DROP IS HERE",
                   sub="Fresh prints, delivered across Lagos", cta="SHOP NOW", products=["shirt", "sneaker", "tote"]),
}


# ------------------------------------------------------------------ product illustrations (original artwork)
def product_svg(kind, brand):
    bg = '<circle cx="180" cy="180" r="180" fill="#FFF3DF"/>'
    if kind == "jollof":
        import random
        r = random.Random(1)
        rice = "".join(f'<ellipse cx="{180 + r.uniform(-95, 95):.0f}" cy="{180 + r.uniform(-70, 75):.0f}" rx="9" ry="4.5" '
                       f'transform="rotate({r.randint(0, 180)} {180} {180})" fill="{r.choice(["#E8742B", "#F08A3C", "#D9601F"])}"/>' for _ in range(260))
        peas = "".join(f'<circle cx="{180 + r.uniform(-80, 80):.0f}" cy="{180 + r.uniform(-60, 70):.0f}" r="7" fill="#5DA34A"/>' for _ in range(14))
        art = (f'<ellipse cx="180" cy="196" rx="150" ry="140" fill="#E9E2D6"/><ellipse cx="180" cy="188" rx="150" ry="140" fill="#FFFFFF"/>'
               f'<ellipse cx="180" cy="188" rx="118" ry="108" fill="#F4EEE4"/>{rice}{peas}'
               '<g transform="rotate(-25 230 150)"><ellipse cx="230" cy="150" rx="52" ry="36" fill="#9C4F1F"/>'
               '<ellipse cx="222" cy="142" rx="40" ry="24" fill="#B8642A"/><rect x="270" y="143" width="40" height="14" rx="7" fill="#F3E9D8"/>'
               '<circle cx="312" cy="143" r="11" fill="#F3E9D8"/><circle cx="312" cy="157" r="11" fill="#F3E9D8"/></g>'
               '<circle cx="118" cy="232" r="24" fill="#D93A2B"/><circle cx="118" cy="232" r="16" fill="#F26B5B"/>')
    elif kind == "puffpuff":
        balls = [(120, 170), (180, 150), (240, 170), (150, 215), (210, 215), (180, 185)]
        art = ('<defs><radialGradient id="pp" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="#F8C66A"/>'
               '<stop offset="1" stop-color="#B9701F"/></radialGradient></defs>'
               '<ellipse cx="180" cy="250" rx="150" ry="60" fill="#2F6690"/><ellipse cx="180" cy="232" rx="150" ry="44" fill="#3A7CA5"/>'
               + "".join(f'<circle cx="{x}" cy="{y}" r="48" fill="url(#pp)"/>' for x, y in balls)
               + "".join(f'<circle cx="{x + dx}" cy="{y + dy}" r="3" fill="#FFF8E7"/>' for x, y in balls for dx, dy in ((-14, -18), (10, -22), (-4, -8)))
               + '<path d="M30 232 Q180 330 330 232 L330 250 Q180 350 30 250 Z" fill="#2F6690"/>')
    elif kind == "zobo":
        art = ('<path d="M115 70 L245 70 L228 300 Q180 318 132 300 Z" fill="#E7EEF3" opacity="0.9"/>'
               '<path d="M122 120 L238 120 L226 292 Q180 308 134 292 Z" fill="#8E1B3A"/>'
               '<path d="M122 120 L238 120 L236 140 L124 140 Z" fill="#B3264E"/>'
               '<rect x="140" y="150" width="34" height="34" rx="6" fill="#FFFFFF" opacity="0.55" transform="rotate(12 157 167)"/>'
               '<rect x="186" y="176" width="30" height="30" rx="6" fill="#FFFFFF" opacity="0.5" transform="rotate(-10 201 191)"/>'
               '<rect x="205" y="30" width="10" height="150" rx="5" fill="#F4B942" transform="rotate(18 210 105)"/>'
               '<circle cx="250" cy="82" r="30" fill="#8BC34A"/><circle cx="250" cy="82" r="22" fill="#C5E1A5"/>'
               '<path d="M250 60 V104 M228 82 H272 M235 67 L265 97 M265 67 L235 97" stroke="#8BC34A" stroke-width="3"/>')
    elif kind == "shirt":
        pat = "".join(f'<circle cx="{x}" cy="{y}" r="14" fill="#F4A259"/><circle cx="{x}" cy="{y}" r="7" fill="{brand}"/>'
                      for x in range(70, 300, 46) for y in range(90, 320, 46))
        art = ('<defs><clipPath id="sh"><path d="M120 60 L150 50 Q180 80 210 50 L240 60 L310 110 L280 160 L250 140 L250 310 L110 310 L110 140 L80 160 L50 110 Z"/></clipPath></defs>'
               f'<g clip-path="url(#sh)"><rect width="360" height="360" fill="#FCE8C8"/>{pat}</g>'
               '<path d="M150 50 Q180 80 210 50" fill="none" stroke="#7A3E1D" stroke-width="5"/>')
    elif kind == "sneaker":
        art = ('<path d="M45 230 Q50 160 110 150 L170 140 Q210 120 240 150 Q290 170 315 200 Q330 222 318 240 L52 248 Z" fill="#FFFFFF" stroke="#2A2A2A" stroke-width="5"/>'
               f'<path d="M110 205 Q190 170 290 205" fill="none" stroke="{brand}" stroke-width="16" stroke-linecap="round"/>'
               '<path d="M40 248 L325 240 Q330 262 310 268 L52 272 Q36 268 40 248 Z" fill="#F4A259"/>'
               + "".join(f'<line x1="{150 + i * 16}" y1="{150 - i * 3}" x2="{162 + i * 16}" y2="{170 - i * 3}" stroke="#2A2A2A" stroke-width="4"/>' for i in range(4)))
    else:  # tote
        pat = "".join(f'<path d="M{x} {y} l18 -18 l18 18 l-18 18 z" fill="{brand}"/><circle cx="{x + 18}" cy="{y}" r="5" fill="#FCE8C8"/>'
                      for x in range(80, 290, 42) for y in range(150, 320, 42))
        art = ('<path d="M130 130 Q130 60 180 60 Q230 60 230 130" fill="none" stroke="#7A3E1D" stroke-width="12"/>'
               '<defs><clipPath id="tb"><path d="M80 125 L280 125 L300 320 L60 320 Z"/></clipPath></defs>'
               f'<g clip-path="url(#tb)"><rect width="360" height="360" fill="#F4A259"/>{pat}</g>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="360" height="360" viewBox="0 0 360 360">{bg}{art}</svg>'


def product_png(kind, brand, path):
    png = cairosvg.svg2png(bytestring=product_svg(kind, brand).encode(), output_width=360, output_height=360)
    open(path, "wb").write(png)
    return "data:image/png;base64," + base64.b64encode(png).decode()


# ------------------------------------------------------------------ the scene
def skyline():
    blocks = [(40, 520, 90), (140, 470, 70), (215, 560, 110), (330, 430, 80), (420, 500, 120),
              (560, 450, 70), (640, 540, 100), (750, 410, 90), (850, 520, 110), (965, 470, 90)]
    out = []
    for x, top, w in blocks:
        out.append(f'<rect x="{x}" y="{top}" width="{w}" height="{820 - top}" fill="#F1CF97"/>')
        for wy in range(top + 20, 790, 36):
            for wx in range(x + 12, x + w - 16, 26):
                out.append(f'<rect x="{wx}" y="{wy}" width="12" height="16" fill="#F8E2BB"/>')
    return "".join(out)


def wheel(id, cx, cy, ang=0):
    spokes = "".join(f'<line x1="{cx}" y1="{cy}" x2="{cx + 26 * math.cos(math.radians(a))}" y2="{cy + 26 * math.sin(math.radians(a))}" '
                     f'stroke="#8A8F98" stroke-width="6" stroke-linecap="round"/>' for a in range(0, 360, 72))
    return (f'<g id="{id}" transform="rotate({ang:.1f} {cx} {cy})"><circle cx="{cx}" cy="{cy}" r="56" fill="#222226"/>'
            f'<circle cx="{cx}" cy="{cy}" r="32" fill="#D6D9DE"/>{spokes}<circle cx="{cx}" cy="{cy}" r="10" fill="#55595F"/></g>')


def scene(s, imgs, tf=None):
    """tf: optional per-layer transforms (only used to render the motion preview)."""
    tf = tf or {}
    t = lambda k: f' transform="{tf[k]}"' if k in tf else ""
    op = lambda k: f' opacity="{tf[k + "_op"]:.3f}"' if k + "_op" in tf else ""
    b = s["brand"]
    img_layers = []
    for i, (cx, cy) in enumerate(((340, 420), (540, 398), (740, 420)), 1):
        img_layers.append(
            f'<g id="image-{i}"{t(f"image-{i}")}{op(f"image-{i}")}>'
            f'<circle cx="{cx}" cy="{cy}" r="92" fill="#FFFFFF"/><circle cx="{cx}" cy="{cy}" r="86" fill="{b}" class="brand-colour"/>'
            f'<clipPath id="clip-{i}"><circle cx="{cx}" cy="{cy}" r="80"/></clipPath>'
            f'<image id="photo-{i}" x="{cx - 80}" y="{cy - 80}" width="160" height="160" clip-path="url(#clip-{i})" '
            f'href="{imgs[i - 1]}" xlink:href="{imgs[i - 1]}" preserveAspectRatio="xMidYMid slice"/></g>')
    wa, wb = tf.get("wheel_angle", 0), tf.get("wheel_angle", 0)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFE3B0"/><stop offset="1" stop-color="#FFF5E1"/></linearGradient></defs>
<g id="background">
  <rect width="{W}" height="{H}" fill="url(#sky)"/>
  <circle id="sun" cx="900" cy="170" r="78" fill="#FFC94A"/>
  <g id="skyline">{skyline()}</g>
  <rect id="road" x="0" y="820" width="{W}" height="260" fill="#3B3B44"/>
  <g id="road-lines">{"".join(f'<rect x="{x}" y="900" width="70" height="10" rx="5" fill="#F2F2F2"/>' for x in range(20, 1080, 130))}</g>
</g>
<g id="signboard"{t("signboard")}{op("signboard")}>
  <line x1="300" y1="0" x2="300" y2="80" stroke="{INK}" stroke-width="6"/><line x1="780" y1="0" x2="780" y2="80" stroke="{INK}" stroke-width="6"/>
  <rect x="190" y="70" width="700" height="230" rx="26" fill="#FFFFFF" stroke="{b}" stroke-width="10" class="brand-colour"/>
  <text id="text-headline" x="540" y="172" text-anchor="middle" font-family="{FONT}" font-weight="800" font-size="64" fill="{INK}">{s["headline"]}</text>
  <text id="text-subline" x="540" y="240" text-anchor="middle" font-family="{FONT}" font-weight="600" font-size="32" fill="#5B5B66">{s["sub"]}</text>
</g>
{"".join(img_layers)}
<g id="danfo"{t("danfo")}>
  <ellipse id="shadow" cx="545" cy="852" rx="420" ry="22" fill="#000000" opacity="0.25"/>
  <rect x="200" y="508" width="600" height="14" rx="5" fill="{INK}"/>
  {"".join(f'<rect x="{x}" y="508" width="10" height="30" fill="{INK}"/>' for x in (230, 400, 570, 760))}
  <path id="body" d="M178 536 H880 Q912 536 924 566 L948 690 Q952 708 952 728 V796 H178 Q150 796 150 768 V564 Q150 536 178 536 Z" fill="{YELLOW}"/>
  <path id="windscreen" d="M884 566 L926 664 L884 664 Z" fill="{GLASS}"/>
  {"".join(f'<rect x="{x}" y="562" width="112" height="86" rx="10" fill="{GLASS}" stroke="{INK}" stroke-width="5"/>' for x in (182, 312, 442, 572))}
  <rect id="door" x="708" y="562" width="160" height="214" rx="10" fill="none" stroke="{INK}" stroke-width="5"/>
  <rect x="716" y="570" width="144" height="78" rx="8" fill="{GLASS}"/>
  <rect id="stripe-top" x="150" y="656" width="802" height="12" fill="{INK}"/>
  <rect id="stripe-bottom" x="150" y="754" width="802" height="12" fill="{INK}"/>
  <rect id="brand-panel" x="182" y="676" width="510" height="70" rx="12" fill="{b}" class="brand-colour"/>
  <text id="text-brand" x="437" y="726" text-anchor="middle" font-family="{FONT}" font-weight="800" font-size="40" fill="#FFFFFF">{s["name"]}</text>
  <circle id="headlight" cx="936" cy="716" r="13" fill="#FFF4C2" stroke="{INK}" stroke-width="4"/>
  <rect id="bumper" x="140" y="790" width="824" height="18" rx="9" fill="#33333A"/>
  <path d="M250 796 A70 70 0 0 1 390 796 Z M690 796 A70 70 0 0 1 830 796 Z" fill="#26262B"/>
  {wheel("wheel-back", 320, 806, wa)}
  {wheel("wheel-front", 760, 806, wb)}
</g>
<g id="cta"{t("cta")}{op("cta")}>
  <rect x="370" y="930" width="340" height="88" rx="44" fill="{b}" class="brand-colour"/>
  <text id="text-cta" x="540" y="988" text-anchor="middle" font-family="{FONT}" font-weight="800" font-size="40" fill="#FFFFFF">{s["cta"]}</text>
</g>
</svg>'''


# ------------------------------------------------------------------ motion preview (reference for the SVGator timeline)
def ease_out_back(x, k=1.5):
    x = min(max(x, 0), 1)
    return 1 + (k + 1) * (x - 1) ** 3 + k * (x - 1) ** 2


def ease_out_bounce(x):
    x = min(max(x, 0), 1)
    n, d = 7.5625, 2.75
    if x < 1 / d:
        return n * x * x
    if x < 2 / d:
        x -= 1.5 / d; return n * x * x + 0.75
    if x < 2.5 / d:
        x -= 2.25 / d; return n * x * x + 0.9375
    x -= 2.625 / d; return n * x * x + 0.984375


DUR = 6.4


def transforms(t):
    tf = {}
    if t < 1.2:
        dx = -1150 * (1 - ease_out_back(t / 1.2, 1.2))
        tf["wheel_angle"] = 900 * (t / 1.2) ** 0.6
    elif t < 5.2:
        dx = 0
        tf["wheel_angle"] = 900
    else:
        q = (t - 5.2) / 1.0
        dx = 1300 * q ** 2.2
        tf["wheel_angle"] = 900 + 900 * q ** 2
    dy = 7 * math.sin(math.pi * (t - 1.2) / 0.35) * math.exp(-(t - 1.2) * 5) if 1.2 <= t < 2.0 else 0
    tf["danfo"] = f"translate({dx:.1f} {dy:.1f})"
    sy = -430 * (1 - ease_out_bounce((t - 1.25) / 0.7)) if t < 1.95 else 0
    tf["signboard"] = f"translate(0 {sy:.1f})"
    for i, (cx, cy) in enumerate(((340, 420), (540, 398), (740, 420)), 1):
        p = ease_out_back((t - 1.9 - 0.18 * (i - 1)) / 0.45, 2.2)
        p = max(p, 0.0001)
        lift = 60 * (1 - min(max((t - 1.9 - 0.18 * (i - 1)) / 0.45, 0), 1))
        tf[f"image-{i}"] = f"translate({cx} {cy + lift:.1f}) scale({p:.3f}) translate({-cx} {-cy})"
    c = ease_out_back((t - 2.6) / 0.4, 2.0)
    pulse = 1 + 0.05 * math.sin(2 * math.pi * (t - 3.0) / 0.9) if t > 3.0 else 1
    s = max(c * pulse, 0.0001)
    tf["cta"] = f"translate(540 974) scale({s:.3f}) translate(-540 -974)"
    fade = 1 - min(max((t - 5.0) / 0.4, 0), 1)
    for k in ("signboard", "image-1", "image-2", "image-3", "cta"):
        tf[k + "_op"] = fade
    return tf


def main():
    out = sys.argv[1]
    os.makedirs(os.path.join(out, "products"), exist_ok=True)
    for name, s in SETS.items():
        imgs = [product_png(k, s["brand"], os.path.join(out, "products", f"{name}_{i + 1}.png")) for i, k in enumerate(s["products"])]
        open(os.path.join(out, f"danfo_{name}.svg"), "w").write(scene(s, imgs))
        cairosvg.svg2png(bytestring=scene(s, imgs).encode(), write_to=os.path.join(out, f"danfo_{name}.png"), output_width=1080)
        if "--preview" in sys.argv:
            fps = 30
            enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-i", "-",
                                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", os.path.join(out, f"preview_{name}.mp4")],
                                   stdin=subprocess.PIPE)
            for f in range(int(DUR * fps)):
                enc.stdin.write(cairosvg.svg2png(bytestring=scene(s, imgs, transforms(f / fps)).encode(), output_width=720))
            enc.stdin.close()
            enc.wait()
        print("done", name, flush=True)


if __name__ == "__main__":
    main()
