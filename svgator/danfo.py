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
                    sub="Hot jollof, straight to your door", cta="ORDER NOW", bubble="Food don land!", products=["jollof", "puffpuff", "zobo"]),
    "ankara": dict(brand="#1F7A8C", name="ANKARA THREADS", headline="NEW DROP IS HERE",
                   sub="Fresh prints, delivered across Lagos", cta="SHOP NOW", bubble="Oya, come see!", products=["shirt", "sneaker", "tote"]),
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
SKIN, SHIRT, PANTS = "#6B3E26", "#3E8E5E", "#2E3A59"
IMG_POS = ((340, 392), (540, 372), (740, 392))
WHEELS = (("wheel-back", 300), ("wheel-front", 830))
WHEEL_Y, WHEEL_R = 800, 58


def skyline_far():
    out = []
    for x, top, w in [(0, 560, 80), (70, 470, 60), (140, 520, 90), (250, 430, 70), (330, 500, 100), (450, 455, 60),
                      (520, 540, 90), (620, 410, 66), (700, 490, 110), (820, 450, 80), (910, 520, 70), (990, 430, 90)]:
        out.append(f'<rect x="{x}" y="{top}" width="{w}" height="{820 - top}" fill="#E8A07E"/>')
    out.append('<rect x="650" y="370" width="6" height="42" fill="#E8A07E"/>')          # antenna on the tallest tower
    return "".join(out)


def skyline_near():
    import random
    r = random.Random(7)
    out = []
    for x, top, w in [(-10, 610, 120), (120, 650, 90), (220, 590, 130), (365, 640, 100), (480, 600, 120),
                      (615, 660, 90), (720, 580, 140), (875, 630, 100), (985, 600, 110)]:
        out.append(f'<rect x="{x}" y="{top}" width="{w}" height="{820 - top}" fill="#C46E57"/>'
                   f'<rect x="{x}" y="{top}" width="{w}" height="8" fill="#B25F4A"/>')
        for wy in range(top + 22, 800, 34):
            for wx in range(x + 14, x + w - 18, 26):
                out.append(f'<rect x="{wx}" y="{wy}" width="12" height="16" rx="2" fill="{"#FFD98A" if r.random() < 0.35 else "#A9563F"}"/>')
    return "".join(out)


def palm(id, x, y, flip=1):
    fronds = ""
    for ang, ln, c in ((-160, 120, "#2E6B4F"), (-130, 110, "#3D8360"), (-95, 80, "#2E6B4F"), (-55, 110, "#3D8360"), (-20, 120, "#2E6B4F"),
                       (170, 95, "#3D8360"), (10, 95, "#3D8360")):
        a = math.radians(ang if flip == 1 else 180 - ang)
        ex, ey = x + ln * math.cos(a), y + ln * math.sin(a) + 55          # leaf tip droops below the crown
        mx, my = x + ln * 0.55 * math.cos(a), y + ln * 0.55 * math.sin(a) - 22
        fronds += (f'<path d="M{x} {y} Q{mx:.0f} {my - 14:.0f} {ex:.0f} {ey:.0f} Q{mx:.0f} {my + 16:.0f} {x} {y + 6} Z" fill="{c}"/>'
                   f'<path d="M{x} {y + 2} Q{mx:.0f} {my:.0f} {ex:.0f} {ey:.0f}" stroke="#1F4D38" stroke-width="2" fill="none"/>')
    trunk = f'<path d="M{x - 9} 830 Q{x - 30 * flip} {(830 + y) / 2:.0f} {x - 4} {y} L{x + 6} {y} Q{x - 18 * flip} {(830 + y) / 2:.0f} {x + 9} 830 Z" fill="#7A5134"/>'
    rings = "".join(f'<path d="M{x - 12 - flip * 12 * math.sin(k / 8 * math.pi):.0f} {830 - k * (830 - y) / 9:.0f} h18" stroke="#5E3D27" stroke-width="3"/>' for k in range(1, 9))
    return f'<g id="{id}">{trunk}{rings}{fronds}<circle cx="{x}" cy="{y + 6}" r="9" fill="#5E3D27"/></g>'


def cloud(id, x, y, s=1.0):
    blobs = "".join(f'<circle cx="{x + dx * s:.0f}" cy="{y + dy * s:.0f}" r="{rr * s:.0f}" fill="#FFF6EA"/>'
                    for dx, dy, rr in ((0, 0, 34), (40, -18, 42), (86, 0, 32), (44, 12, 36)))
    return f'<g id="{id}" opacity="0.85">{blobs}</g>'


def wheel(id, cx, cy, ang=0):
    spokes = "".join(f'<path d="M{cx} {cy} L{cx + 27 * math.cos(math.radians(a)):.1f} {cy + 27 * math.sin(math.radians(a)):.1f}" '
                     f'stroke="#9AA0A8" stroke-width="7" stroke-linecap="round"/>' for a in range(0, 360, 60))
    tread = "".join(f'<path d="M{cx + 52 * math.cos(math.radians(a)):.1f} {cy + 52 * math.sin(math.radians(a)):.1f} '
                    f'L{cx + 58 * math.cos(math.radians(a)):.1f} {cy + 58 * math.sin(math.radians(a)):.1f}" stroke="#3A3A40" stroke-width="5"/>'
                    for a in range(0, 360, 20))
    return (f'<g id="{id}" transform="rotate({ang:.1f} {cx} {cy})"><circle cx="{cx}" cy="{cy}" r="{WHEEL_R}" fill="#1E1E22"/>{tread}'
            f'<circle cx="{cx}" cy="{cy}" r="34" fill="url(#chrome)"/>{spokes}<circle cx="{cx}" cy="{cy}" r="11" fill="#4A4E55"/>'
            f'<circle cx="{cx - 4}" cy="{cy - 4}" r="4" fill="#FFFFFF" opacity="0.6"/></g>')


def ghana_must_go(x, y, w, h):
    lines = "".join(f'<path d="M{x + i} {y} V{y + h}" stroke="{c}" stroke-width="5"/>' for i, c in zip(range(8, w, 16), ["#C8303A", "#2F5FA8"] * 20))
    lines += "".join(f'<path d="M{x} {y + j} H{x + w}" stroke="{c}" stroke-width="5" opacity="0.8"/>' for j, c in zip(range(8, h, 14), ["#2F5FA8", "#C8303A"] * 10))
    return (f'<clipPath id="gmg"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7"/></clipPath>'
            f'<g clip-path="url(#gmg)"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#F4F1EA"/>{lines}</g>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="none" stroke="#2A2A30" stroke-width="3"/>'
            f'<path d="M{x + 6} {y + h / 2} H{x + w - 6}" stroke="#2A2A30" stroke-width="3" stroke-dasharray="2 4"/>')


def scene(s, imgs, tf=None):
    """tf: optional per-layer transforms / opacities (only used to render the motion preview)."""
    tf = tf or {}

    def G(id, body, extra=""):
        a = f' transform="{tf[id]}"' if id in tf else ""
        hidden = id.startswith(("sparkle-", "dust-", "speed-lines"))   # effects start invisible; the animation reveals them
        o = f' opacity="{tf[id + "_op"]:.3f}"' if id + "_op" in tf else (' opacity="0"' if hidden else "")
        return f'<g id="{id}"{a}{o}{extra}>{body}</g>'

    b = s["brand"]
    BC = f'fill="{b}" class="brand-colour"'

    # ---- background
    rays = "".join(f'<path d="M860 470 L{860 + 330 * math.cos(math.radians(a - 4)):.0f} {470 + 330 * math.sin(math.radians(a - 4)):.0f} '
                   f'L{860 + 330 * math.cos(math.radians(a + 4)):.0f} {470 + 330 * math.sin(math.radians(a + 4)):.0f} Z" fill="#FFF1C9" opacity="0.28"/>'
                   for a in range(0, 360, 30))
    road_marks = "".join(f'<rect x="{x}" y="902" width="74" height="10" rx="5" fill="#ECE7DF"/>' for x in range(-90, 1170, 130))
    kerb = "".join(f'<rect x="{x}" y="816" width="65" height="14" fill="{"#F2F0EA" if (x // 65) % 2 else "#2A2A30"}"/>' for x in range(0, 1080, 65))
    background = (
        f'<rect id="sky" width="{W}" height="{H}" fill="url(#sky)"/>'
        + G("sun-rays", rays) +
        '<circle cx="860" cy="470" r="190" fill="url(#glow)"/><circle id="sun" cx="860" cy="470" r="76" fill="#FFD35C"/>'
        + G("cloud-1", cloud("c1", 70, 360, 1.0)) + G("cloud-2", cloud("c2", 930, 250, 0.8)) + G("cloud-3", cloud("c3", 600, 330, 0.6))
        + G("skyline-far", skyline_far()) + G("beacon", '<circle cx="653" cy="368" r="6" fill="#FF3B3B"/>')
        + G("skyline-near", skyline_near())
        + G("palm-1", palm("p1", 70, 650, 1)) + G("palm-2", palm("p2", 1010, 640, -1))
        + f'<rect id="road" x="0" y="820" width="{W}" height="260" fill="url(#asphalt)"/>{kerb}'
        + G("road-lines", road_marks)
    )

    # ---- signboard with marquee bulbs
    bulbs = [(x, y) for y in (88, 282) for x in range(232, 860, 52)]
    bulbs_a = "".join(f'<circle cx="{x}" cy="{y}" r="7" fill="#FFE27A" stroke="#E0A800" stroke-width="2"/>' for i, (x, y) in enumerate(bulbs) if i % 2 == 0)
    bulbs_b = "".join(f'<circle cx="{x}" cy="{y}" r="7" fill="#FFE27A" stroke="#E0A800" stroke-width="2"/>' for i, (x, y) in enumerate(bulbs) if i % 2)
    signboard = (
        f'<path d="M300 0 V74 M780 0 V74" stroke="{INK}" stroke-width="6"/>'
        f'<circle cx="300" cy="74" r="9" fill="{INK}"/><circle cx="780" cy="74" r="9" fill="{INK}"/>'
        f'<rect x="196" y="78" width="700" height="230" rx="26" fill="#000000" opacity="0.18"/>'
        f'<rect x="190" y="70" width="700" height="230" rx="26" {BC}/>'
        f'<rect x="204" y="84" width="672" height="202" rx="16" fill="#FFFFFF"/>'
        + G("bulbs-a", bulbs_a) + G("bulbs-b", bulbs_b) +
        f'<text id="text-headline" x="540" y="186" text-anchor="middle" font-family="{FONT}" font-weight="800" font-size="62" fill="{INK}">{s["headline"]}</text>'
        f'<text id="text-subline" x="540" y="244" text-anchor="middle" font-family="{FONT}" font-weight="600" font-size="31" fill="#5B5B66">{s["sub"]}</text>'
    )

    # ---- product images with sparkle bursts
    images = ""
    for i, (cx, cy) in enumerate(IMG_POS, 1):
        sp = "".join(f'<path d="M{cx + 104 * math.cos(math.radians(a)):.0f} {cy + 104 * math.sin(math.radians(a)):.0f} '
                     f'L{cx + 128 * math.cos(math.radians(a)):.0f} {cy + 128 * math.sin(math.radians(a)):.0f}" '
                     f'stroke="{"#FFD23F" if k % 2 else "#FFFFFF"}" stroke-width="7" stroke-linecap="round"/>' for k, a in enumerate(range(0, 360, 36)))
        images += G(f"sparkle-{i}", sp)
        images += G(f"image-{i}",
                    f'<circle cx="{cx + 5}" cy="{cy + 9}" r="92" fill="#000000" opacity="0.2"/>'
                    f'<circle cx="{cx}" cy="{cy}" r="92" fill="#FFFFFF"/><circle cx="{cx}" cy="{cy}" r="86" {BC}/>'
                    f'<clipPath id="clip-{i}"><circle cx="{cx}" cy="{cy}" r="79"/></clipPath>'
                    f'<image id="photo-{i}" x="{cx - 79}" y="{cy - 79}" width="158" height="158" clip-path="url(#clip-{i})" '
                    f'href="{imgs[i - 1]}" xlink:href="{imgs[i - 1]}" preserveAspectRatio="xMidYMid slice"/>'
                    f'<path d="M{cx - 58} {cy - 50} A78 78 0 0 1 {cx + 10} {cy - 78}" stroke="#FFFFFF" stroke-width="6" fill="none" opacity="0.55" stroke-linecap="round"/>')

    # ---- the danfo
    windows = ""
    heads = {0: [(222, 0)], 1: [(318, 1), (356, 0)], 2: [(452, 1)], 3: [(545, 0), (585, 1)]}
    for k, x in enumerate((172, 286, 400, 514)):
        windows += f'<rect x="{x}" y="548" width="100" height="88" rx="10" fill="url(#glass)" stroke="{INK}" stroke-width="5"/>'
        for hx, big in heads[k]:
            windows += (f'<circle cx="{hx}" cy="{596 - 4 * big}" r="{15 + 2 * big}" fill="#151B2B"/>'
                        f'<path d="M{hx - 26} 636 Q{hx - 24} {612 - 4 * big} {hx} {612 - 4 * big} Q{hx + 24} {612 - 4 * big} {hx + 26} 636 Z" fill="#151B2B"/>')
        windows += f'<path d="M{x + 18} 552 L{x + 44} 552 L{x + 14} 632 L{x + 4} 632 L{x + 4} 586 Z" fill="#FFFFFF" opacity="0.16"/>'
    conductor = (
        f'<path d="M682 788 L690 704 L716 704 L722 788 Z" fill="{PANTS}"/>'
        f'<path d="M676 788 h26 v-8 h-20 z M708 788 h26 v-8 h-20 z" fill="#1A1A1E"/>'
        f'<path d="M684 708 Q688 664 712 630 L756 644 Q746 684 720 710 Z" fill="{SHIRT}"/>'
        f'<path d="M698 690 l10 -40 M714 700 l14 -50 M730 702 l12 -44" stroke="#FFFFFF" stroke-width="4" opacity="0.35"/>'
        f'<path d="M718 640 L700 604" stroke="{SKIN}" stroke-width="13" stroke-linecap="round"/>'
        f'<rect x="732" y="616" width="16" height="16" fill="{SKIN}"/>'
        f'<circle cx="752" cy="598" r="23" fill="{SKIN}"/>'
        f'<path d="M729 594 Q731 570 754 570 Q777 570 777 592 Z" {BC}/><rect x="768" y="586" width="26" height="7" rx="3" {BC}/>'
        f'<circle cx="762" cy="596" r="3" fill="#1A1A1E"/><path d="M754 609 Q762 616 770 608" stroke="#FFFFFF" stroke-width="3" fill="none" stroke-linecap="round"/>'
        + G("conductor-arm", f'<path d="M748 642 L790 616" stroke="{SHIRT}" stroke-width="16" stroke-linecap="round"/>'
                             f'<path d="M790 616 L802 566" stroke="{SKIN}" stroke-width="13" stroke-linecap="round"/>'
                             f'<circle cx="803" cy="558" r="11" fill="{SKIN}"/>')
    )
    body = (
        f'<path d="M190 500 H840 M200 500 V520 M380 500 V520 M560 500 V520 M760 500 V520" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
        + G("luggage", ghana_must_go(232, 458, 140, 42)
            + '<rect x="404" y="474" width="128" height="26" rx="13" fill="#D9A55B"/>'
            + "".join(f'<path d="M{x} 476 v22" stroke="#B07D3A" stroke-width="4"/>' for x in range(420, 530, 18))
            + '<path d="M566 500 L576 466 L650 466 L660 500 Z" fill="#B5793A"/>'
            + "".join(f'<path d="M{x} 468 l-6 30" stroke="#8C5A26" stroke-width="3"/>' for x in range(586, 656, 14))) +
        '<path id="body" d="M178 520 H846 Q884 520 898 548 L944 640 Q956 662 956 690 V790 Q956 800 946 800 H160 Q150 800 150 790 V548 Q150 520 178 520 Z" fill="url(#bodygrad)"/>'
        '<rect x="168" y="526" width="676" height="7" rx="3" fill="#FFFFFF" opacity="0.4"/>'
        + windows +
        '<path id="windscreen" d="M776 548 H880 L926 636 H776 Z" fill="url(#glass)" stroke="#1D1D22" stroke-width="5" stroke-linejoin="round"/>'
        '<path d="M800 552 L826 552 L790 632 L780 632 Z" fill="#FFFFFF" opacity="0.18"/>'
        '<path d="M896 600 L934 588 M930 578 h16 v22 h-16 z" stroke="#1D1D22" stroke-width="5" fill="#1D1D22"/>'
        f'<rect id="doorway" x="632" y="548" width="128" height="242" rx="8" fill="#26262C"/>'
        '<rect x="636" y="760" width="120" height="14" fill="#55555E"/>'
        f'<path d="M700 556 V700" stroke="#9AA0A8" stroke-width="6"/>'
        + G("conductor", conductor) +
        f'<rect id="stripe-top" x="150" y="648" width="482" height="11" fill="{INK}"/><rect x="760" y="648" width="196" height="11" fill="{INK}"/>'
        f'<rect id="stripe-bottom" x="150" y="756" width="482" height="11" fill="{INK}"/><rect x="760" y="756" width="196" height="11" fill="{INK}"/>'
        f'<rect id="brand-panel" x="176" y="668" width="440" height="78" rx="12" {BC}/>'
        f'<rect x="184" y="674" width="424" height="10" rx="5" fill="#FFFFFF" opacity="0.18"/>'
        f'<text id="text-brand" x="396" y="720" text-anchor="middle" font-family="{FONT}" font-weight="800" font-size="38" fill="#FFFFFF">{s["name"]}</text>'
        f'<text id="text-slogan" x="490" y="783" text-anchor="middle" font-family="{FONT}" font-weight="800" font-size="15" fill="{INK}" letter-spacing="1">NO FOOD FOR LAZY MAN</text>'
        '<circle cx="610" cy="700" r="6" fill="#B78A00"/><circle cx="240" cy="784" r="5" fill="#B78A00"/>'
        + G("headlight-beam", '<path d="M950 700 L1080 650 L1080 760 Z" fill="url(#beam)"/>') +
        '<circle id="headlight" cx="944" cy="702" r="14" fill="#FFF7CF" stroke="#1D1D22" stroke-width="4"/>'
        '<rect x="938" y="728" width="14" height="10" rx="3" fill="#FF9A1F"/>'
        '<rect x="150" y="684" width="10" height="44" rx="3" fill="#E23B2E"/>'
        '<path d="M250 800 A60 60 0 0 1 350 800 Z M780 800 A60 60 0 0 1 880 800 Z" fill="#1E1E22"/>'
        '<rect id="bumper" x="138" y="786" width="832" height="20" rx="10" fill="url(#chrome)"/>'
        '<rect x="118" y="792" width="34" height="9" rx="4" fill="#55555E"/>'
    )
    puffs = "".join(G(f"puff-{i}", f'<circle cx="104" cy="796" r="16" fill="#D8D4CC"/>') for i in range(3))
    dust = "".join(G(f"dust-{i}", f'<circle cx="{c}" cy="852" r="18" fill="#C9B9A1"/>') for i, c in enumerate((900, 870, 250)))
    speed = G("speed-lines", "".join(f'<rect x="{x}" y="{y}" width="{w}" height="9" rx="4" fill="#FFFFFF" opacity="0.7"/>'
                                     for x, y, w in ((40, 590, 80), (10, 660, 100), (50, 730, 70))))
    danfo = (
        '<ellipse id="shadow" cx="555" cy="858" rx="430" ry="24" fill="url(#shade)"/>'
        + speed + G("exhaust", puffs) + G("danfo-body", body)
        + "".join(wheel(n, x, WHEEL_Y, tf.get(n + "_ang", 0)) for n, x in WHEELS)
    )

    bubble = (
        '<path d="M864 514 L816 556 L892 520 Z" fill="#FFFFFF"/>'
        '<rect x="842" y="452" width="226" height="66" rx="33" fill="#FFFFFF" stroke="#1D1D22" stroke-width="4"/>'
        '<path d="M866 516 L822 552 L890 518" fill="#FFFFFF" stroke="#1D1D22" stroke-width="4" stroke-linejoin="round"/>'
        '<rect x="862" y="508" width="34" height="8" fill="#FFFFFF"/>'
        f'<text id="text-bubble" x="955" y="494" text-anchor="middle" font-family="{FONT}" font-weight="800" font-size="24" fill="{INK}">{s["bubble"]}</text>'
    )
    cta = (
        G("cta-ripple", f'<rect x="350" y="936" width="380" height="86" rx="43" fill="none" stroke="{b}" stroke-width="6" class="brand-colour"/>')
        + '<rect x="356" y="946" width="380" height="86" rx="43" fill="#000000" opacity="0.25"/>'
        + f'<rect x="350" y="936" width="380" height="86" rx="43" {BC}/>'
        + '<rect x="372" y="944" width="290" height="12" rx="6" fill="#FFFFFF" opacity="0.2"/>'
        + f'<text id="text-cta" x="510" y="993" text-anchor="middle" font-family="{FONT}" font-weight="800" font-size="38" fill="#FFFFFF">{s["cta"]}</text>'
        + G("cta-arrow", f'<circle cx="684" cy="979" r="30" fill="#FFFFFF"/><path d="M670 979 H696 M686 967 L698 979 L686 991" stroke="{b}" '
                         f'stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round" class="brand-colour"/>')
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF8F5E"/><stop offset="0.45" stop-color="#FFC27A"/><stop offset="0.75" stop-color="#FFE3B5"/></linearGradient>
<radialGradient id="glow"><stop offset="0.3" stop-color="#FFE9A8" stop-opacity="0.9"/><stop offset="1" stop-color="#FFE9A8" stop-opacity="0"/></radialGradient>
<linearGradient id="asphalt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3D3B45"/><stop offset="1" stop-color="#26252B"/></linearGradient>
<linearGradient id="bodygrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFD43D"/><stop offset="0.55" stop-color="{YELLOW}"/><stop offset="1" stop-color="#DDA300"/></linearGradient>
<linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4A6087"/><stop offset="1" stop-color="#22304A"/></linearGradient>
<linearGradient id="chrome" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EEF0F3"/><stop offset="1" stop-color="#8E949C"/></linearGradient>
<linearGradient id="beam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFF7CF" stop-opacity="0.75"/><stop offset="1" stop-color="#FFF7CF" stop-opacity="0"/></linearGradient>
<radialGradient id="shade"><stop offset="0" stop-color="#000000" stop-opacity="0.45"/><stop offset="1" stop-color="#000000" stop-opacity="0"/></radialGradient>
</defs>
{G("background", background)}
{G("signboard", signboard)}
{images}
{G("danfo", danfo)}
{G("dust", dust)}
{G("bubble", bubble)}
{G("cta", cta)}
</svg>'''


# ------------------------------------------------------------------ motion preview (reference for the SVGator timeline)
def clamp(x):
    return min(max(x, 0.0), 1.0)


def ease_out_back(x, k=1.70158):
    x = clamp(x)
    return 1 + (k + 1) * (x - 1) ** 3 + k * (x - 1) ** 2


def ease_out_cubic(x):
    return 1 - (1 - clamp(x)) ** 3


def ease_out_bounce(x):
    x = clamp(x)
    n, d = 7.5625, 2.75
    if x < 1 / d:
        return n * x * x
    if x < 2 / d:
        x -= 1.5 / d; return n * x * x + 0.75
    if x < 2.5 / d:
        x -= 2.25 / d; return n * x * x + 0.9375
    x -= 2.625 / d; return n * x * x + 0.984375


DUR = 6.8
ABOUT = lambda cx, cy, sc=1.0, rot=0.0, dx=0.0, dy=0.0: f"translate({cx + dx:.1f} {cy + dy:.1f}) rotate({rot:.2f}) scale({max(sc, 0.0001):.3f}) translate({-cx} {-cy})"


def transforms(t):
    tf = {}
    # danfo: drive in (0-1.3), brake, idle, drive out (5.6-6.8). Wheels roll by the distance travelled.
    if t < 1.3:
        dx = -1250 * (1 - ease_out_cubic(t / 1.3))
    elif t < 5.6:
        dx = 0.0
    else:
        dx = 1350 * clamp((t - 5.6) / 1.2) ** 2.2
    for n, _ in WHEELS:
        tf[n + "_ang"] = (dx + 1250 if t < 5.6 else 1250 + dx) / WHEEL_R * 180 / math.pi
    tf["danfo"] = f"translate({dx:.1f} 0)"
    tilt = 2.2 * math.sin(math.pi * (t - 1.3) / 0.3) * math.exp(-(t - 1.3) * 4.5) if 1.3 <= t < 2.6 else 0
    if 5.6 <= t < 6.0:
        tilt = -1.4 * math.sin(math.pi * (t - 5.6) / 0.4)
    idle = 1.2 * math.sin(2 * math.pi * t * 9) if 1.6 < t < 5.6 else 0
    tf["danfo-body"] = ABOUT(830, 858, rot=tilt, dy=idle)
    moving = 1 - clamp((t - 0.9) / 0.4) if t < 1.3 else clamp((t - 5.7) / 0.3)
    tf["speed-lines_op"] = moving
    tf["speed-lines"] = f"translate({-30 * (t % 0.3) / 0.3:.1f} 0)"
    for i in range(3):   # exhaust puffs cycle every 0.9 s
        q = ((t + i * 0.3) % 0.9) / 0.9
        tf[f"puff-{i}"] = ABOUT(104, 796, sc=0.5 + 1.2 * q, dx=-70 * q, dy=-26 * q)
        tf[f"puff-{i}_op"] = 0.7 * (1 - q)
    for i in range(3):   # brake dust
        q = clamp((t - 1.25 - 0.05 * i) / 0.6)
        tf[f"dust-{i}"] = ABOUT((900, 870, 250)[i], 852, sc=0.4 + 1.6 * q, dx=(-50, 40, -40)[i] * q, dy=-30 * q)
        tf[f"dust-{i}_op"] = 0.8 * (1 - q) if 0 < q < 1 else 0
    tf["headlight-beam_op"] = 1.0 if (1.3 < t < 1.42 or 1.52 < t < 1.64) else (0.35 if t < 5.6 else 0.6)
    # conductor leans out and waves
    lean = -18 * (1 - ease_out_back((t - 1.45) / 0.45, 2.2))
    tf["conductor"] = ABOUT(700, 788, rot=lean)
    tf["conductor-arm"] = ABOUT(748, 642, rot=16 * math.sin(2 * math.pi * (t - 1.9) * 1.8) if t > 1.9 else -40 * (1 - clamp((t - 1.5) / 0.4)))
    # signboard drops, bounces, then swings to rest; marquee bulbs chase
    sy = -440 * (1 - ease_out_bounce((t - 1.5) / 0.75))
    swing = 3.0 * math.sin(2 * math.pi * (t - 2.25) / 1.1) * math.exp(-(t - 2.25) * 1.3) if t > 2.25 else 0
    tf["signboard"] = ABOUT(540, 0, rot=swing, dy=sy)
    on = int(t / 0.22) % 2
    tf["bulbs-a_op"] = 1.0 if t < 2.2 else (1.0 if on else 0.25)
    tf["bulbs-b_op"] = 1.0 if t < 2.2 else (0.25 if on else 1.0)
    # products pop out of the luggage, sparkle, then float
    for i, (cx, cy) in enumerate(IMG_POS, 1):
        t0 = 2.3 + 0.16 * (i - 1)
        p = ease_out_back((t - t0) / 0.5, 2.4)
        lift = 90 * (1 - ease_out_cubic((t - t0) / 0.5))
        float_y = 6 * math.sin(2 * math.pi * (t - t0) / 1.6 + i) if t > t0 + 0.5 else 0
        tf[f"image-{i}"] = ABOUT(cx, cy, sc=p, dy=lift + float_y)
        q = clamp((t - t0 - 0.12) / 0.5)
        tf[f"sparkle-{i}"] = ABOUT(cx, cy, sc=0.6 + 0.6 * q)
        tf[f"sparkle-{i}_op"] = (1 - q) if 0 < q < 1 else 0
    # speech bubble
    tf["bubble"] = ABOUT(820, 552, sc=ease_out_back((t - 2.0) / 0.4, 2.5))
    # CTA pops, then ripples and nudges its arrow
    tf["cta"] = ABOUT(540, 979, sc=ease_out_back((t - 3.0) / 0.45, 2.2))
    if t > 3.4:
        q = ((t - 3.4) % 1.0) / 1.0
        tf["cta-ripple"] = ABOUT(540, 979, sc=1 + 0.22 * q)
        tf["cta-ripple_op"] = 0.8 * (1 - q)
    else:
        tf["cta-ripple_op"] = 0
    tf["cta-arrow"] = f"translate({5 * max(0, math.sin(2 * math.pi * t * 1.6)):.1f} 0)"
    # everything but the bus fades before it drives away
    fade = 1 - clamp((t - 5.2) / 0.4)
    for k in ("signboard", "image-1", "image-2", "image-3", "bubble", "cta"):
        tf[k + "_op"] = fade
    # ambient life: loops cleanly every DUR seconds
    ph = 2 * math.pi * t / DUR
    tf["sun-rays"] = f"rotate({30 * t / DUR:.2f} 860 470)"
    for i, a in enumerate((26, 18, 14), 1):
        tf[f"cloud-{i}"] = f"translate({a * math.sin(ph + i):.1f} 0)"
    tf["palm-1"] = f"rotate({2 * math.sin(ph * 3):.2f} 70 830)"
    tf["palm-2"] = f"rotate({-2 * math.sin(ph * 3 + 1):.2f} 1010 830)"
    tf["beacon_op"] = 1.0 if (t % 1.0) < 0.5 else 0.2
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
                enc.stdin.write(cairosvg.svg2png(bytestring=scene(s, imgs, transforms(f / fps)).encode(), output_width=1080))
            enc.stdin.close()
            enc.wait()
        print("done", name, flush=True)


if __name__ == "__main__":
    main()
