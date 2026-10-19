"""PAYMENT SUCCESS: an SVGator template entry (SVGator x Contra challenge, entry 3).

A tap-to-pay checkout microinteraction: tap card -> processing -> success tick + confetti -> receipt -> button.
Rebranding: 2 images (logo, product) + 8 texts + 1 brand colour.

The static SVG shows the finished "success" screen. The parts that only appear during the animation
(bank card, contactless icon, spinner, ripple, burst, confetti and the tap/processing texts) start at opacity 0.

usage: python3 svgator/paysuccess.py OUT_DIR [--preview]
"""
import base64, math, os, random, subprocess, sys
import cairosvg

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import danfo

W = H = 1080
FONT = "Poppins, 'Arial Black', Arial, Helvetica, sans-serif"
DUR = 6.0
CX, SY = 540, 330          # status icon centre
INK, MUTED, LINE = "#1D1D22", "#8A8A93", "#ECEAE6"

SETS = {
    "kitchen": dict(brand="#E4572E", bg1="#FFF1E8", bg2="#FFD3BD", merchant="Mama's Kitchen", order="Order #MK-2048",
                    amount="NGN 25,000", item="1 × Jollof Special", product="jollof", last4="4821",
                    date="19 Oct 2026, 7:42 pm", ref="MK-8F2K-19", cta="Track order", logo="pot"),
    "ankara": dict(brand="#1F7A8C", bg1="#E6F4F6", bg2="#BFE3E9", merchant="Ankara Threads", order="Order #AT-0915",
                   amount="$64.00", item="1 × Ankara Sneaker", product="sneaker", last4="7303",
                   date="19 Oct 2026, 9:15 am", ref="AT-3QX7-08", cta="View receipt", logo="diamond"),
}


def logo_svg(kind, brand):
    if kind == "pot":
        icon = ('<path d="M52 92 H148 V118 C148 146 126 160 100 160 C74 160 52 146 52 118 Z" fill="#FFFFFF"/>'
                '<rect x="40" y="84" width="120" height="14" rx="7" fill="#FFFFFF"/>'
                '<path d="M80 70 C76 58 88 54 84 42 M100 70 C96 58 108 54 104 42 M120 70 C116 58 128 54 124 42" fill="none" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round"/>')
    else:
        icon = "".join(f'<path d="M{x} {y - 26} L{x + 26} {y} L{x} {y + 26} L{x - 26} {y} Z" fill="{c}"/>'
                       for x, y, c in ((100, 62, "#FFFFFF"), (62, 100, "#F2C14E"), (138, 100, "#F2C14E"), (100, 138, "#FFFFFF")))
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200"><circle cx="100" cy="100" r="100" fill="{brand}"/>{icon}</svg>'


def png_uri(svg, path, w=200):
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=w)
    open(path, "wb").write(png)
    return "data:image/png;base64," + base64.b64encode(png).decode()


random.seed(4)
CONFETTI = [(math.radians(a + random.uniform(-10, 10)), random.uniform(150, 230), random.choice((0, 1, 2)), random.choice(("r", "c")),
             random.uniform(-200, 200)) for a in range(0, 360, 22)]


def scene(s, logo, product, tf=None):
    tf = tf or {}
    hidden = {"bank-card", "contactless", "text-tap", "text-processing", "spinner", "tap-ripple", "burst", "confetti", "cta-shine"}

    def G(id, body, extra=""):
        a = f' transform="{tf[id]}"' if id in tf else ""
        if id + "_op" in tf:
            o = f' opacity="{tf[id + "_op"]:.3f}"'
        else:
            o = ' opacity="0"' if id in hidden else ""
        return f'<g id="{id}"{a}{o}{extra}>{body}</g>'

    def T(id, x, y, text, size, weight=600, fill=INK, anchor="start", extra=""):
        return (f'<text id="{id}" x="{x}" y="{y}" font-family="{FONT}" font-weight="{weight}" font-size="{size}" fill="{fill}"'
                f'{"" if anchor == "start" else f" text-anchor=\"{anchor}\""}{extra}>{text}</text>')

    b = s["brand"]
    x0, y0, cw, ch = 240, 60, 600, 960
    defs = (f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{s["bg1"]}"/><stop offset="1" stop-color="{s["bg2"]}"/></linearGradient>'
            f'<linearGradient id="cardg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2A2A35"/><stop offset="1" stop-color="#0E0E14"/></linearGradient>'
            f'<clipPath id="logoclip"><circle cx="{x0 + 76}" cy="{y0 + 76}" r="36"/></clipPath>'
            f'<clipPath id="prodclip"><rect x="{x0 + 40}" y="{y0 + 590}" width="64" height="64" rx="16"/></clipPath>'
            f'<clipPath id="ctaclip"><rect x="{x0 + 40}" y="{y0 + 830}" width="{cw - 80}" height="86" rx="43"/></clipPath></defs>')
    bgdots = "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="{b}" opacity="0.10"/>' for x in range(30, W, 60) for y in range(30, H, 60))
    background = f'<rect width="{W}" height="{H}" fill="url(#bg)"/>' + G("background-dots", bgdots)

    # ---- the phone screen
    head = (G("logo", f'<image href="{logo}" x="{x0 + 40}" y="{y0 + 40}" width="72" height="72" clip-path="url(#logoclip)"/>')
            + T("text-merchant", x0 + 132, y0 + 72, s["merchant"], 30, 800)
            + T("text-order", x0 + 133, y0 + 104, s["order"], 21, 600, MUTED)
            + f'<rect x="{x0 + 40}" y="{y0 + 140}" width="{cw - 80}" height="2" fill="{LINE}"/>')
    ticks = f'M{CX - 40} {SY + 2} L{CX - 10} {SY + 32} L{CX + 44} {SY - 28}'
    tick_len = math.dist((CX - 40, SY + 2), (CX - 10, SY + 32)) + math.dist((CX - 10, SY + 32), (CX + 44, SY - 28))
    tick_dash = ""
    if "tick_draw" in tf:
        tick_dash = f' stroke-dasharray="{tf["tick_draw"] * tick_len:.1f} {tick_len + 10:.1f}"'
    burst = "".join(f'<line x1="{CX + 104 * math.cos(math.radians(a)):.1f}" y1="{SY + 104 * math.sin(math.radians(a)):.1f}" '
                    f'x2="{CX + 132 * math.cos(math.radians(a)):.1f}" y2="{SY + 132 * math.sin(math.radians(a)):.1f}" stroke="{b}" stroke-width="8" stroke-linecap="round"/>'
                    for a in range(0, 360, 45))
    conf = ""
    cols = (b, "#F2C14E", "#2FA36B")
    for k, (a, r, ci, shape, rot) in enumerate(CONFETTI):
        x, y = CX + 70 * math.cos(a), SY + 70 * math.sin(a)
        piece = (f'<rect x="{x - 7:.1f}" y="{y - 4:.1f}" width="14" height="8" rx="2" fill="{cols[ci]}"/>' if shape == "r"
                 else f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="{cols[ci]}"/>')
        conf += G(f"confetti-{k + 1}", piece)
    arc_r = 86
    spinner = (f'<circle cx="{CX}" cy="{SY}" r="{arc_r}" fill="none" stroke="{LINE}" stroke-width="14"/>'
               f'<path d="M{CX} {SY - arc_r} A{arc_r} {arc_r} 0 0 1 {CX + arc_r} {SY}" fill="none" stroke="{b}" stroke-width="14" stroke-linecap="round"/>')
    contactless = "".join(f'<path d="M{CX - 30 + 22 * k} {SY - 22 - 14 * k} Q{CX - 8 + 30 * k} {SY} {CX - 30 + 22 * k} {SY + 22 + 14 * k}" fill="none" stroke="{b}" stroke-width="10" stroke-linecap="round"/>'
                          for k in range(4))
    status = (G("contactless", contactless) + G("tap-ripple", f'<circle cx="{CX}" cy="{SY}" r="90" fill="none" stroke="{b}" stroke-width="6"/>')
              + G("spinner", spinner) + G("burst", burst) + G("confetti", conf)
              + G("success-circle", f'<circle cx="{CX}" cy="{SY}" r="{arc_r}" fill="{b}"/>')
              + G("tick", f'<path d="{ticks}" fill="none" stroke="#FFFFFF" stroke-width="17" stroke-linecap="round" stroke-linejoin="round"{tick_dash}/>'))
    texts = (G("text-tap", T("text-tap-label", CX, y0 + 432, "Hold your card near the phone", 26, 600, MUTED, "middle"))
             + G("text-processing", T("text-processing-label", CX, y0 + 432, "Processing payment…", 28, 600, MUTED, "middle"))
             + G("status", T("text-status", CX, y0 + 432, "Payment successful", 34, 800, INK, "middle"))
             + G("amount", T("text-amount", CX, y0 + 510, s["amount"], 62, 800, INK, "middle")))
    rows = [("row-1", None, s["item"], ""), ("row-2", "Paid with", f"•••• {s['last4']}", ""),
            ("row-3", "Date", s["date"], ""), ("row-4", "Reference", s["ref"], "")]
    receipt = G("receipt-bg", f'<rect x="{x0 + 24}" y="{y0 + 570}" width="{cw - 48}" height="234" rx="28" fill="#F7F5F2"/>')
    for i, (rid, lab, val, _) in enumerate(rows):
        if lab is None:
            r = (G("product-image", f'<image href="{product}" x="{x0 + 40}" y="{y0 + 590}" width="64" height="64" clip-path="url(#prodclip)"/>')
                 + T("text-item", x0 + 122, y0 + 630, val, 26, 800))
        else:
            yy = y0 + 676 + 44 * (i - 1)
            r = (T(f"text-{rid}-label", x0 + 48, yy, lab, 22, 600, MUTED)
                 + T(f"text-{rid}-value", x0 + cw - 48, yy, val, 22, 800, INK, "end"))
        receipt += G(rid, r)
    cta = (G("cta", f'<rect x="{x0 + 40}" y="{y0 + 830}" width="{cw - 80}" height="86" rx="43" fill="{b}"/>'
                    + T("text-cta", CX, y0 + 884, s["cta"], 30, 800, "#FFFFFF", "middle")
                    + G("cta-shine", f'<g clip-path="url(#ctaclip)"><path d="M{x0 + 40} {y0 + 830} h60 l-50 86 h-60 Z" fill="#FFFFFF" opacity="0.35"/></g>')))
    screen = (f'<rect x="{x0 + 10}" y="{y0 + 26}" width="{cw}" height="{ch}" rx="56" fill="{b}" opacity="0.18"/>'
              f'<rect x="{x0}" y="{y0}" width="{cw}" height="{ch}" rx="56" fill="#FFFFFF"/>'
              + G("header", head) + G("status-icon", status) + texts + G("receipt", receipt) + cta)

    # ---- the bank card that taps (animation only)
    card = (f'<rect x="{CX - 150}" y="{SY - 95}" width="300" height="190" rx="22" fill="url(#cardg)"/>'
            f'<rect x="{CX - 118}" y="{SY - 50}" width="46" height="36" rx="7" fill="#E8C66A"/>'
            f'<path d="M{CX + 96} {SY - 64} q10 14 0 28 M{CX + 108} {SY - 72} q14 22 0 44" fill="none" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" opacity="0.8"/>'
            + T("text-card-number", CX - 118, SY + 40, f"•••• {s['last4']}", 24, 600, "#FFFFFF")
            + f'<circle cx="{CX + 98}" cy="{SY + 56}" r="16" fill="{b}" opacity="0.9"/><circle cx="{CX + 118}" cy="{SY + 56}" r="16" fill="#F2C14E" opacity="0.9"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<style>{danfo.FONT_CSS}</style>{defs}'
            + G("background", background) + G("screen", screen) + G("bank-card", card) + "</svg>")


# ------------------------------------------------------------------ motion reference
def clamp(x):
    return min(max(x, 0.0), 1.0)


def eo(x):
    return 1 - (1 - clamp(x)) ** 3


def eio(x):
    x = clamp(x)
    return 3 * x * x - 2 * x ** 3


def eob(x, k=1.9):
    x = clamp(x)
    return 1 + (k + 1) * (x - 1) ** 3 + k * (x - 1) ** 2


AB = lambda cx, cy, sc=1.0, rot=0.0, dx=0.0, dy=0.0: f"translate({cx + dx:.1f} {cy + dy:.1f}) rotate({rot:.2f}) scale({max(sc, 0.0001):.3f}) translate({-cx} {-cy})"


def window(t, a, b, fade=0.2):
    """1 inside [a, b], fading in/out over `fade` seconds"""
    return clamp((t - a) / fade) * (1 - clamp((t - (b - fade)) / fade))


def transforms(t):
    tf = {}
    # screen rises in; everything fades at the end so the loop restarts cleanly
    tf["screen"] = AB(CX, 540, dy=60 * (1 - eo(t / 0.5)))
    tf["screen_op"] = clamp(t / 0.35) * (1 - clamp((t - 5.6) / 0.4))
    # stage 1: tap
    tf["contactless_op"] = window(t, 0.3, 1.5)
    tf["contactless"] = AB(CX, SY, sc=1 + 0.06 * math.sin(2 * math.pi * t * 2))
    tf["text-tap_op"] = window(t, 0.3, 1.5)
    if t < 1.2:
        q = eo((t - 0.6) / 0.6)
        tf["bank-card"] = AB(CX, SY, rot=-14 * (1 - q), dx=520 * (1 - q), dy=160 * (1 - q))
    elif t < 1.4:
        tf["bank-card"] = AB(CX, SY, sc=1 - 0.06 * math.sin(math.pi * (t - 1.2) / 0.2))
    else:
        q = clamp((t - 1.4) / 0.35) ** 2
        tf["bank-card"] = AB(CX, SY, rot=10 * q, dx=360 * q, dy=380 * q)
    tf["bank-card_op"] = clamp((t - 0.6) / 0.15) * (1 - clamp((t - 1.55) / 0.2))
    rq = clamp((t - 1.25) / 0.6)
    tf["tap-ripple"] = AB(CX, SY, sc=0.8 + 0.7 * rq)
    tf["tap-ripple_op"] = 0.9 * (1 - rq) if rq > 0 else 0
    # stage 2: processing
    tf["spinner_op"] = window(t, 1.5, 2.75, 0.15)
    tf["spinner"] = AB(CX, SY, rot=600 * eio((t - 1.5) / 1.25))
    tf["text-processing_op"] = window(t, 1.55, 2.8, 0.2)
    # stage 3: success
    tf["success-circle"] = AB(CX, SY, sc=eob((t - 2.6) / 0.4))
    tf["success-circle_op"] = 1.0 if t >= 2.6 else 0.0
    tf["tick_draw"] = max(0.001, eo((t - 2.85) / 0.35))
    tf["tick_op"] = 1.0 if t >= 2.85 else 0.0
    bq = clamp((t - 2.85) / 0.45)
    tf["burst"] = AB(CX, SY, sc=0.7 + 0.5 * eo(bq))
    tf["burst_op"] = (1 - bq) if 0 < bq < 1 else 0.0
    tf["confetti_op"] = 1.0 if 2.85 <= t < 4.4 else 0.0
    for k, (a, r, ci, shape, rot) in enumerate(CONFETTI):
        q = clamp((t - 2.85) / 1.2)
        d = r * eo(q) - 70 * eo(q)
        x0, y0 = CX + 70 * math.cos(a), SY + 70 * math.sin(a)
        tf[f"confetti-{k + 1}"] = AB(x0, y0, rot=rot * q, dx=d * math.cos(a), dy=d * math.sin(a) + 90 * q * q)
        tf[f"confetti-{k + 1}_op"] = 1 - clamp((q - 0.6) / 0.4)
    tf["status_op"] = clamp((t - 2.95) / 0.3)
    tf["status"] = AB(CX, 490, dy=18 * (1 - eo((t - 2.95) / 0.35)))
    tf["amount_op"] = clamp((t - 3.05) / 0.3)
    tf["amount"] = AB(CX, 560, sc=0.86 + 0.14 * eob((t - 3.05) / 0.4))
    tf["receipt-bg_op"] = clamp((t - 3.15) / 0.3)
    tf["receipt-bg"] = AB(CX, 747, sc=0.94 + 0.06 * eo((t - 3.15) / 0.35))
    for i in range(1, 5):
        a0 = 3.3 + 0.12 * (i - 1)
        tf[f"row-{i}"] = f"translate({-34 * (1 - eo((t - a0) / 0.35)):.1f} 0)"
        tf[f"row-{i}_op"] = clamp((t - a0) / 0.3)
    tf["cta"] = AB(CX, 932, sc=eob((t - 3.9) / 0.4))
    sh = clamp((t - 4.6) / 0.6)
    tf["cta-shine"] = f"translate({560 * sh:.1f} 0)"
    tf["cta-shine_op"] = 1.0 if 0 < sh < 1 else 0.0
    return tf


def main():
    danfo.FONT_CSS = danfo.font_css()
    out = sys.argv[1]
    os.makedirs(os.path.join(out, "images"), exist_ok=True)
    for name, s in SETS.items():
        logo = png_uri(logo_svg(s["logo"], s["brand"]), os.path.join(out, "images", f"{name}_logo.png"))
        product = danfo.product_png(s["product"], s["brand"], os.path.join(out, "images", f"{name}_product.png"))
        svg = scene(s, logo, product)
        open(os.path.join(out, f"paysuccess_{name}.svg"), "w").write(svg)
        cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(out, f"paysuccess_{name}.png"), output_width=1080)
        if "--preview" in sys.argv:
            fps = 30
            enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-i", "-",
                                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", os.path.join(out, f"preview_pay_{name}.mp4")],
                                   stdin=subprocess.PIPE)
            for f in range(int(DUR * fps)):
                enc.stdin.write(cairosvg.svg2png(bytestring=scene(s, logo, product, transforms(f / fps)).encode(), output_width=1080))
            enc.stdin.close()
            enc.wait()
        print("done", name, flush=True)


if __name__ == "__main__":
    main()
