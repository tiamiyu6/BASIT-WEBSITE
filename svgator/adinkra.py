"""ADINKRA LOADERS: an SVGator template entry (SVGator x Contra challenge, entry 2).

A loading-screen kit of 6 loaders built on West African symbols. Each loader is its own named group, so you can use the
whole board or keep one. Rebranding: 1 logo + 2 texts + 2 colours.

Writes, for each content set:
  adinkra_<set>.svg / .png   the static template to import into SVGator (named layers, live text, embedded logo)
  logos/<set>.png            the logo image (original art)
  preview_<set>.mp4          motion reference (with --preview)

usage: python3 svgator/adinkra.py OUT_DIR [--preview]
"""
import base64, math, os, subprocess, sys
import cairosvg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import danfo                                     # reuse the embedded Poppins font helper

W = H = 1080
FONT = "Poppins, 'Arial Black', Arial, Helvetica, sans-serif"
DUR = 2.4                                        # every loader loops cleanly in 2.4 s

SETS = {
    "adire": dict(name="ADIRE STUDIO", tag="loading your experience", bg="#15112B", bg2="#211A45", tile="#1E1838",
                  edge="#2E2752", ink="#F5EEE0", muted="#9C93C4", c1="#E8B84A", c2="#E2603A", c3="#2FA36B", logo="adire"),
    "lumo": dict(name="LUMO PAY", tag="securing your payment", bg="#EEF4F1", bg2="#DCEBE4", tile="#FFFFFF",
                 edge="#D3E3DB", ink="#0B2545", muted="#6B8299", c1="#00A86B", c2="#0B2545", c3="#F2A541", logo="lumo"),
}

TILES = [  # id, symbol, meaning, centre
    ("adinkrahene", "ADINKRAHENE", "greatness", (195, 420)),
    ("nkyinkyim", "NKYINKYIM", "life's twists", (540, 420)),
    ("akoma", "AKOMA", "patience", (885, 420)),
    ("dwennimmen", "DWENNIMMEN", "strength", (195, 790)),
    ("kente", "KENTE", "woven together", (540, 790)),
    ("gangan", "GÁNGAN", "the talking drum", (885, 790)),
]
LY = -38                                          # loader centre, relative to the tile centre


# ------------------------------------------------------------------ logos (original art)
def logo_svg(kind, s):
    if kind == "adire":    # indigo adire cloth roundel: concentric dye rings + a star
        pts = " ".join(f"{100 + (54 if k % 2 == 0 else 24) * math.cos(math.pi * k / 8 - math.pi / 2):.1f},"
                       f"{100 + (54 if k % 2 == 0 else 24) * math.sin(math.pi * k / 8 - math.pi / 2):.1f}" for k in range(16))
        body = (f'<circle cx="100" cy="100" r="98" fill="#2B3A8C"/><circle cx="100" cy="100" r="84" fill="none" stroke="#E8B84A" stroke-width="6" stroke-dasharray="10 8"/>'
                f'<polygon points="{pts}" fill="#F5EEE0"/><circle cx="100" cy="100" r="14" fill="#2B3A8C"/>')
    else:                  # lumo: green disc with a bright "L" spark
        body = ('<circle cx="100" cy="100" r="98" fill="#00A86B"/>'
                '<path d="M74 52 V140 H132" fill="none" stroke="#FFFFFF" stroke-width="22" stroke-linecap="round" stroke-linejoin="round"/>'
                '<circle cx="136" cy="62" r="13" fill="#F2A541"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">{body}</svg>'


def logo_png(kind, s, path):
    png = cairosvg.svg2png(bytestring=logo_svg(kind, s).encode(), output_width=200)
    open(path, "wb").write(png)
    return "data:image/png;base64," + base64.b64encode(png).decode()


# ------------------------------------------------------------------ symbol geometry (drawn here from the traditional forms)
def poly_len(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def path_d(pts):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def zigzag(cx, cy):
    """Nkyinkyim: the twisting path"""
    pts = []
    for k in range(7):
        x = cx + (-46 if k % 2 == 0 else 46)
        y = cy - 78 + k * 26
        pts.append((x, y))
    return pts


def spiral(cx, cy, r0, turns, sign):
    """one ram's horn of Dwennimmen: rises from the stem, rolls up and over, and curls in on itself"""
    pts = []
    n = 70
    ox, oy = cx + sign * r0, cy - 4                 # centre of the curl, out to the side
    for i in range(n + 1):
        t = i / n
        a = math.pi + turns * 2 * math.pi * t       # start at the stem side, go over the top
        r = r0 * (1 - 0.78 * t)
        pts.append((ox + sign * r * math.cos(a), oy + r * math.sin(a)))
    return pts


HEART = "M0 30 C-6 24 -58 -6 -58 -36 C-58 -62 -26 -72 0 -46 C26 -72 58 -62 58 -36 C58 -6 6 24 0 30 Z"


def heart(cx, cy, k):
    return f'<path d="{HEART}" transform="translate({cx} {cy + 16}) scale({k})"'


# ------------------------------------------------------------------ the board
def scene(s, logo, tf=None):
    tf = tf or {}

    def G(id, body, extra=""):
        a = f' transform="{tf[id]}"' if id in tf else ""
        o = f' opacity="{tf[id + "_op"]:.3f}"' if id + "_op" in tf else ""
        return f'<g id="{id}"{a}{o}{extra}>{body}</g>'

    def dash(id, length):
        """stroke-draw state for the preview (in SVGator: animate 'Stroke offset' / 'Draw')"""
        if id + "_draw" not in tf:
            return ""
        a, b = tf[id + "_draw"]          # visible window as fractions of the path, 0..1
        on = max(0.0, (b - a)) * length
        return f' stroke-dasharray="{on:.1f} {length + 10:.1f}" stroke-dashoffset="{-a * length:.1f}"'

    c1, c2, c3, ink, muted = s["c1"], s["c2"], s["c3"], s["ink"], s["muted"]

    # ---- background: soft cloth-dye pattern (circles and diamonds)
    motif = ""
    for gx in range(0, W + 120, 120):
        for gy in range(0, H + 120, 120):
            off = 60 if (gy // 120) % 2 else 0
            x = gx + off
            motif += (f'<circle cx="{x}" cy="{gy}" r="22" fill="none" stroke="{s["bg2"]}" stroke-width="3"/>'
                      f'<path d="M{x + 60} {gy - 14} L{x + 74} {gy} L{x + 60} {gy + 14} L{x + 46} {gy} Z" fill="{s["bg2"]}"/>')
    background = f'<rect width="{W}" height="{H}" fill="{s["bg"]}"/>' + G("pattern", motif)

    # ---- header: logo + brand + tagline
    header = (G("logo", f'<image href="{logo}" x="70" y="70" width="96" height="96"/>')
              + f'<text id="text-brand" x="190" y="112" font-family="{FONT}" font-weight="800" font-size="40" fill="{ink}">{s["name"]}</text>'
              + f'<text id="text-tagline" x="192" y="152" font-family="{FONT}" font-weight="600" font-size="24" fill="{muted}">{s["tag"]}</text>'
              + f'<text id="text-kit" x="1010" y="112" text-anchor="end" font-family="{FONT}" font-weight="600" font-size="20" fill="{muted}" letter-spacing="3">ADINKRA LOADERS</text>'
              + f'<rect x="958" y="128" width="52" height="6" rx="3" fill="{c1}"/>')

    tiles = ""
    for i, (tid, label, meaning, (cx, cy)) in enumerate(TILES, 1):
        lx, ly = cx, cy + LY
        if tid == "adinkrahene":
            rings = "".join(G(f"ring-{k}", f'<circle cx="{lx}" cy="{ly}" r="{r}" fill="none" stroke="{c1}" stroke-width="10"/>')
                            for k, r in enumerate((34, 58, 82), 1))
            body = rings + G("logo-mark", f'<clipPath id="lm"><circle cx="{lx}" cy="{ly}" r="22"/></clipPath>'
                                          f'<image href="{logo}" x="{lx - 22}" y="{ly - 22}" width="44" height="44" clip-path="url(#lm)"/>')
        elif tid == "nkyinkyim":
            pts = zigzag(lx, ly)
            L = poly_len(pts)
            body = (f'<path d="{path_d(pts)}" fill="none" stroke="{s["edge"]}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>'
                    + G("zigzag", f'<path d="{path_d(pts)}" fill="none" stroke="{c1}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"{dash("zigzag", L)}/>')
                    + G("zigzag-dot", f'<circle cx="{pts[0][0]:.1f}" cy="{pts[0][1]:.1f}" r="11" fill="{c2}"/>'))
        elif tid == "akoma":
            body = (G("akoma-ripple", heart(lx, ly, 1.0) + f' fill="none" stroke="{c2}" stroke-width="5"/>')
                    + G("akoma-heart", heart(lx, ly, 1.0) + f' fill="{c2}"/>' + heart(lx, ly, 0.52) + f' fill="none" stroke="{s["tile"]}" stroke-width="7"/>'))
        elif tid == "dwennimmen":
            parts = ""
            for side, sign in (("left", -1), ("right", 1)):
                pts = spiral(lx, ly - 6, 40, 1.15, sign)
                L = poly_len(pts)
                parts += G(f"horn-{side}", f'<path d="{path_d(pts)}" fill="none" stroke="{c1}" stroke-width="13" stroke-linecap="round"{dash("horn-" + side, L)}/>')
            parts += f'<rect x="{lx - 7}" y="{ly - 12}" width="14" height="74" rx="7" fill="{c2}"/>'
            body = G("horns", parts)
        elif tid == "kente":
            bw, bh = 236, 44
            x0, y0 = lx - bw / 2, ly - bh / 2 + 4
            stripes = ""
            cols = [c1, c2, c3, ink]
            for k in range(-12, 24):
                x = x0 + k * 20
                stripes += f'<rect x="{x:.0f}" y="{y0}" width="20" height="{bh}" fill="{cols[k % 4]}"/>'
                stripes += f'<rect x="{x:.0f}" y="{y0 + 14}" width="20" height="16" fill="{cols[(k + 2) % 4]}" opacity="0.85"/>'
            body = (f'<clipPath id="kclip"><rect x="{x0}" y="{y0}" width="{bw}" height="{bh}" rx="22"/></clipPath>'
                    f'<rect x="{x0 - 6}" y="{y0 - 6}" width="{bw + 12}" height="{bh + 12}" rx="28" fill="none" stroke="{s["edge"]}" stroke-width="4"/>'
                    f'<g clip-path="url(#kclip)">{G("kente-weave", stripes)}</g>'
                    f'<text id="text-percent" x="{lx}" y="{y0 + bh + 52}" text-anchor="middle" font-family="{FONT}" font-weight="800" font-size="30" fill="{ink}">72%</text>')
        else:  # gangan: hourglass talking drum with sound waves
            drum = (f'<path d="M{lx - 40} {ly - 54} L{lx + 40} {ly - 54} L{lx + 12} {ly} L{lx + 40} {ly + 54} L{lx - 40} {ly + 54} L{lx - 12} {ly} Z" fill="{c2}"/>'
                    + "".join(f'<line x1="{lx - 40 + k * 16}" y1="{ly - 54}" x2="{lx - 40 + k * 16}" y2="{ly + 54}" stroke="{c1}" stroke-width="3"/>' for k in range(1, 5))
                    + f'<rect x="{lx - 46}" y="{ly - 62}" width="92" height="12" rx="6" fill="{c1}"/><rect x="{lx - 46}" y="{ly + 50}" width="92" height="12" rx="6" fill="{c1}"/>')
            waves = "".join(G(f"wave-{k}", f'<path d="M{lx + 58 + 18 * k} {ly - 26 - 10 * k} Q{lx + 76 + 22 * k} {ly} {lx + 58 + 18 * k} {ly + 26 + 10 * k}" '
                                              f'fill="none" stroke="{c1}" stroke-width="7" stroke-linecap="round"/>') for k in range(1, 4))
            body = G("drum", drum) + waves
        tile = (f'<rect id="tile-bg-{i}" x="{cx - 160}" y="{cy - 170}" width="320" height="340" rx="34" fill="{s["tile"]}" stroke="{s["edge"]}" stroke-width="2"/>'
                + G(f"loader-{tid}", body)
                + f'<text id="text-name-{i}" x="{cx}" y="{cy + 112}" text-anchor="middle" font-family="{FONT}" font-weight="800" font-size="26" fill="{ink}" letter-spacing="2">{label}</text>'
                + f'<text id="text-meaning-{i}" x="{cx}" y="{cy + 142}" text-anchor="middle" font-family="{FONT}" font-weight="600" font-size="20" fill="{muted}">{meaning}</text>')
        tiles += G(f"tile-{i}", tile)

    footer = f'<text id="text-footer" x="540" y="1040" text-anchor="middle" font-family="{FONT}" font-weight="600" font-size="20" fill="{muted}">symbols from Ghana and Nigeria  ·  loops every {DUR:g} s</text>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<style>{danfo.FONT_CSS}</style>'
            + G("background", background) + G("header", header) + G("tiles", tiles) + footer + "</svg>")


# ------------------------------------------------------------------ motion (reference for the SVGator timeline)
def clamp(x):
    return min(max(x, 0.0), 1.0)


def ease_io(x):
    x = clamp(x)
    return 3 * x * x - 2 * x * x * x


ABOUT = lambda cx, cy, sc=1.0, rot=0.0, dx=0.0, dy=0.0, sx=None: (
    f"translate({cx + dx:.1f} {cy + dy:.1f}) rotate({rot:.2f}) scale({(sx if sx is not None else max(sc, 0.0001)):.3f} {max(sc, 0.0001):.3f}) translate({-cx} {-cy})")


def transforms(t, intro=True):
    """t in seconds. Every loop repeats exactly every DUR seconds."""
    tf = {}
    p = (t % DUR) / DUR                  # 0..1 loop phase
    # tiles pop in once at the start (only for the very first loop)
    for i, (tid, _, _, (cx, cy)) in enumerate(TILES, 1):
        if intro:
            q = clamp((t - 0.08 * i) / 0.45)
            k = 1 + 2.6 * (q - 1) ** 3 + 1.6 * (q - 1) ** 2
            tf[f"tile-{i}"] = ABOUT(cx, cy, sc=k)
            tf[f"tile-{i}_op"] = clamp(q * 2)
    # 1 adinkrahene: rings breathe outward one after another
    (cx, cy) = TILES[0][3]
    for k in range(1, 4):
        q = (p - (k - 1) * 0.12) % 1.0
        pulse = math.sin(math.pi * clamp(q / 0.5)) if q < 0.5 else 0
        tf[f"ring-{k}"] = ABOUT(cx, cy + LY, sc=1 + 0.12 * pulse)
        tf[f"ring-{k}_op"] = 0.35 + 0.65 * pulse
    tf["logo-mark"] = ABOUT(cx, cy + LY, rot=360 * ease_io(p))
    # 2 nkyinkyim: the path draws itself, then un-draws from the start; a bead runs ahead of the line
    pts = zigzag(TILES[1][3][0], TILES[1][3][1] + LY)
    if p < 0.5:
        a, b = 0.0, ease_io(p / 0.5)
    else:
        a, b = ease_io((p - 0.5) / 0.5), 1.0
    tf["zigzag_draw"] = (a, b)
    L = poly_len(pts)
    target, acc = b * L, 0.0
    bx, by = pts[0]
    for i in range(len(pts) - 1):
        seg = math.dist(pts[i], pts[i + 1])
        if acc + seg >= target:
            f = (target - acc) / seg if seg else 0
            bx, by = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f
            break
        acc += seg
        bx, by = pts[i + 1]
    tf["zigzag-dot"] = f"translate({bx - pts[0][0]:.1f} {by - pts[0][1]:.1f})"
    # 3 akoma: a double heartbeat, with a ripple on each beat
    (cx, cy) = TILES[2][3]
    beat = 0.0
    for b0 in (0.0, 0.18):
        q = (p - b0) / 0.14
        if 0 <= q <= 1:
            beat = max(beat, math.sin(math.pi * q))
    tf["akoma-heart"] = ABOUT(cx, cy + LY + 16, sc=1 + 0.14 * beat)
    rq = clamp(p / 0.6)
    tf["akoma-ripple"] = ABOUT(cx, cy + LY + 16, sc=1 + 0.45 * rq)
    tf["akoma-ripple_op"] = 0.8 * (1 - rq)
    # 4 dwennimmen: both horns curl in (draw), hold, then the pair turns and unwinds
    (cx, cy) = TILES[3][3]
    d = ease_io(p / 0.45) if p < 0.45 else (1.0 if p < 0.7 else 1 - ease_io((p - 0.7) / 0.3))
    tf["horn-left_draw"] = (0.0, max(d, 0.001))
    tf["horn-right_draw"] = (0.0, max(d, 0.001))
    tf["horns"] = ABOUT(cx, cy + LY, rot=(10 * math.sin(2 * math.pi * p)))
    # 5 kente: the weave slides through the bar (indeterminate progress), one full pattern repeat per loop
    tf["kente-weave"] = f"translate({80 * p:.1f} 0)"
    # 6 gangan: two drum hits per loop, each sends the waves out
    (cx, cy) = TILES[5][3]
    hit = 0.0
    for b0 in (0.0, 0.5):
        q = (p - b0) / 0.12
        if 0 <= q <= 1:
            hit = max(hit, math.sin(math.pi * q))
    tf["drum"] = ABOUT(cx, cy + LY, sc=1 - 0.06 * hit, rot=-4 * hit)
    for k in range(1, 4):
        q = ((p - 0.05 * k) % 0.5) / 0.5
        tf[f"wave-{k}"] = f"translate({10 * q:.1f} 0)"
        tf[f"wave-{k}_op"] = math.sin(math.pi * q)
    return tf


def main():
    danfo.FONT_CSS = danfo.font_css()
    out = sys.argv[1]
    os.makedirs(os.path.join(out, "logos"), exist_ok=True)
    for name, s in SETS.items():
        logo = logo_png(s["logo"], s, os.path.join(out, "logos", f"{name}.png"))
        svg = scene(s, logo)
        open(os.path.join(out, f"adinkra_{name}.svg"), "w").write(svg)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(out, f"adinkra_{name}.png"), output_width=1080)
        if "--preview" in sys.argv:
            fps = 30
            enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-i", "-",
                                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", os.path.join(out, f"preview_{name}.mp4")],
                                   stdin=subprocess.PIPE)
            for f in range(int(DUR * 3 * fps)):          # three loops: intro + two clean loops
                enc.stdin.write(cairosvg.svg2png(bytestring=scene(s, logo, transforms(f / fps)).encode(), output_width=1080))
            enc.stdin.close()
            enc.wait()
        print("done", name, flush=True)


if __name__ == "__main__":
    main()
