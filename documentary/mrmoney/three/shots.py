"""Mr Money 3D shots. Each shot renders a PNG sequence (1280x720) that engine.py plays back.

usage:  python3 three/shots.py SHOT OUT_DIR [args]        (render the whole sequence, resumable)
        python3 three/shots.py SHOT OUT.png --still FRAME [args]
shots:  mm | chapter WORD COLOR | phone | slips | passport | naira | vinyl | mic | candles
"""
import math, os, random, sys
import bpy
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib
from lib import key, linear

TEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tex")
os.makedirs(TEX, exist_ok=True)
PH = os.path.join(lib.MM, "photos")


def pf(name, s):
    return ImageFont.truetype(os.path.join(lib.MM, "fonts", name), s)


def ease(ob, path, frames_vals):
    for f, v in frames_vals:
        setattr(ob, path, v)
        ob.keyframe_insert(path, frame=f)


# ------------------------------------------------------------------ MM title
def shot_mm():
    sc = lib.reset(170, res=(1280, 720))
    lib.world(strength=0.6)
    g = lib.gold()
    t = lib.text("MM", size=1.9, extrude=0.2, bevel=0.03, material=g, spacing=0.92)
    ease(t, "rotation_euler", [(1, (math.radians(90), 0, math.radians(-75))), (58, (math.radians(90), 0, math.radians(4))),
                               (80, (math.radians(90), 0, 0)), (170, (math.radians(90), 0, math.radians(-3)))])
    ease(t, "location", [(1, (0, 0.6, -0.9)), (58, (0, 0, 0.12)), (170, (0, 0, 0.12))])
    lib.floor(z=-0.72, rough=0.08)
    c, tg = lib.camera((0, -8.0, 0.25), target=(0, 0, 0.05), lens=55)
    ease(c, "location", [(1, (0.9, -8.0, 0.0)), (170, (0, -5.2, 0.3))])
    lib.area((-3, -3, 4), (40, 0, -35), 900, 3, (1, 0.86, 0.66))
    lib.area((3.5, -1.5, 1.5), (70, 0, 60), 300, 2, (0.75, 0.82, 1))
    lib.area((0, 3, 2.5), (-60, 0, 0), 700, 4, (1, 0.7, 0.35))          # rim from behind
    lib.strip((0, -3.5, 3.2), (-30, 0, 0), 9, 0.25, (1, 0.9, 0.7), 18)
    lib.strip((-4, -2, 0.4), (90, 0, -60), 0.25, 3, (1, 0.85, 0.6), 12)
    sw = lib.strip((-7, -3, 1.6), (90, 0, 0), 0.5, 4, (1, 0.95, 0.85), 60)  # light sweep across the metal
    ease(sw, "location", [(1, (-7, -3, 1.6)), (75, (-7, -3, 1.6)), (130, (7, -3, 1.6))])
    random.seed(7)
    cm = lib.gold()
    for i in range(46):
        x, y = random.uniform(-3.6, 3.6), random.uniform(-1.8, 2.8)
        if abs(x) < 1.4 and y < 0.4:
            y += 1.6                                      # keep coins off the letters' face
        f0 = random.randint(-20, 120)
        dur = random.randint(34, 48)
        co = lib.coin((x, y, 3.6), r=random.uniform(0.11, 0.17), mat_=cm)
        rx, ry = random.uniform(-1, 1), random.uniform(-1, 1)
        ease(co, "location", [(f0, (x, y, 3.6)), (f0 + dur, (x + random.uniform(-0.3, 0.3), y, -1.4))])
        ease(co, "rotation_euler", [(f0, (rx, ry, 0)), (f0 + dur, (rx + random.uniform(4, 9), ry + random.uniform(2, 6), 0))])
        for fc in lib._fcurves(co):
            if fc.data_path == "location":
                fc.keyframe_points[0].interpolation = "QUAD"
                fc.keyframe_points[0].easing = "EASE_IN"
    lib.dust(70, [(-4, 4), (-2, 3), (-0.7, 2.6)], seed=3, frames=170)
    lib.panels()
    return sc


# ------------------------------------------------------------------ 3D chapter word
def shot_chapter(word, color="gold"):
    sc = lib.reset(96, samples=8)
    sc.render.use_motion_blur = False
    lib.world(strength=0.5)
    if color == "red":
        m = lib.mat("red", (0.55, 0.02, 0.02), metal=0.4, rough=0.22, coat=1.0)
    elif color == "white":
        m = lib.mat("white", (0.8, 0.78, 0.74), metal=0.0, rough=0.35, coat=0.6)
    else:
        m = lib.gold()
    t = lib.text(word, size=1.0, extrude=0.16, bevel=0.022, material=m, spacing=1.04)
    bpy.context.view_layer.update()
    s = min(2.7 / max(t.dimensions.x, 0.01), 1.3 / max(t.dimensions.y, 0.01))
    t.scale = (s, s, s)
    ease(t, "rotation_euler", [(1, (math.radians(90), 0, math.radians(22))), (40, (math.radians(90), 0, math.radians(-2))),
                               (96, (math.radians(90), 0, math.radians(-6)))])
    ease(t, "location", [(1, (0, 0.8, -0.05)), (40, (0, 0, 0.05)), (96, (0, 0, 0.05))])
    lib.floor(z=-0.62, rough=0.1)
    c, tg = lib.camera((0.7, -6.2, 0.1), target=(0, 0, 0.0), lens=52)
    ease(c, "location", [(1, (0.7, -6.4, 0.05)), (96, (-0.15, -5.4, 0.28))])
    warm = (1, 0.82, 0.6) if color != "white" else (0.9, 0.92, 1)
    lib.area((-3, -3, 4), (40, 0, -35), 700, 3, warm)
    lib.area((0, 3, 2.5), (-60, 0, 0), 600, 4, (1, 0.6, 0.3) if color != "white" else (0.7, 0.8, 1))
    lib.strip((0, -3.5, 3.2), (-30, 0, 0), 9, 0.22, (1, 0.9, 0.75), 16)
    sw = lib.strip((-7, -3, 1.4), (90, 0, 0), 0.5, 4, (1, 0.95, 0.85), 55)
    ease(sw, "location", [(1, (-7, -3, 1.4)), (30, (-7, -3, 1.4)), (80, (7, -3, 1.4))])
    lib.dust(55, [(-4, 4), (-2, 3), (-0.5, 2.2)], seed=sum(map(ord, word)), frames=96)
    lib.panels((0.85, 0.9, 1) if color == "white" else (1, 0.8, 0.55))
    return sc


# ------------------------------------------------------------------ the parlour floor: phone + earphones, fan shadow
def screen_tex():
    p = os.path.join(TEX, "screen.png")
    W, H = 540, 1140
    im = Image.new("RGB", (W, H), (8, 10, 18))
    d = ImageDraw.Draw(im)
    for y in range(H):                                   # soft gradient
        k = y / H
        d.line([(0, y), (W, y)], fill=(int(20 + 40 * (1 - k)), int(18 + 26 * (1 - k)), int(30 + 30 * (1 - k))))
    d.rounded_rectangle([60, 210, W - 60, 210 + W - 120], 26, fill=(36, 30, 22))
    for i in range(46):                                  # abstract "now playing" waveform art, no album art
        h = 20 + 140 * abs(math.sin(i * 0.53) * math.cos(i * 0.21))
        x = 90 + i * 8
        d.rectangle([x, 210 + (W - 120) / 2 - h / 2, x + 4, 210 + (W - 120) / 2 + h / 2], fill=(232, 184, 74))
    d.rounded_rectangle([70, 850, W - 70, 858], 4, fill=(70, 66, 60))
    d.rounded_rectangle([70, 850, 70 + (W - 140) * 0.37, 858], 4, fill=(232, 184, 74))
    d.rectangle([W / 2 - 26, 930, W / 2 - 10, 990], fill=(240, 236, 228))      # pause: reads the same either way up
    d.rectangle([W / 2 + 10, 930, W / 2 + 26, 990], fill=(240, 236, 228))
    im.rotate(180).save(p)
    return p


def tile_tex():
    p = os.path.join(TEX, "tiles.png")
    W = 1024
    im = Image.new("RGB", (W, W))
    d = ImageDraw.Draw(im)
    rng = random.Random(4)
    n = 4
    s = W // n
    for i in range(n):
        for j in range(n):
            base = (150, 118, 88) if (i + j) % 2 == 0 else (196, 168, 132)
            d.rectangle([i * s, j * s, i * s + s, j * s + s], fill=base)
            for _ in range(500):                         # terrazzo specks
                x, y = rng.randint(i * s, i * s + s), rng.randint(j * s, j * s + s)
                c = rng.choice([(90, 70, 50), (230, 214, 190), (120, 96, 70)])
                d.ellipse([x, y, x + rng.randint(2, 7), y + rng.randint(2, 6)], fill=c)
            d.rectangle([i * s, j * s, i * s + s, j * s + s], outline=(70, 60, 50), width=5)
    im.filter(ImageFilter.GaussianBlur(0.8)).save(p)
    return p


def shot_phone():
    sc = lib.reset(150)
    lib.world((0.004, 0.005, 0.009), strength=1, studio=False)
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0))
    fl = bpy.context.object
    fm = lib.image_mat("tiles", tile_tex(), rough=0.35)
    fl.data.materials.append(fm)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.uv.smart_project()
    bpy.ops.object.mode_set(mode="OBJECT")
    for uv in fl.data.uv_layers.active.data:
        uv.uv = (uv.uv[0] * 3, uv.uv[1] * 3)
    # phone
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.05, 0.0, 0.022))
    ph = bpy.context.object
    ph.scale = (0.36, 0.76, 0.04)
    ph.rotation_euler = (0, 0, math.radians(-18))
    bv = ph.modifiers.new("b", "BEVEL")
    bv.width, bv.segments = 0.05, 4
    ph.data.materials.append(lib.mat("body", (0.02, 0.02, 0.025), metal=0.6, rough=0.25))
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0.05, 0.0, 0.0425))
    scr = bpy.context.object
    scr.scale = (0.33, 0.7, 1)
    scr.rotation_euler = (0, 0, math.radians(-18))
    scr.data.materials.append(lib.image_mat("screen", screen_tex(), rough=0.1, emit=2.2))
    # earphone cable from the bottom of the phone, snaking across the floor
    cu = bpy.data.curves.new("cable", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 0.006
    cu.bevel_resolution = 3
    sp = cu.splines.new("BEZIER")
    pts = [(-0.06, -0.37, 0.01), (-0.3, -0.7, 0.006), (-0.1, -1.05, 0.006), (0.35, -0.95, 0.006), (0.6, -0.6, 0.006)]
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    cab = bpy.data.objects.new("cable", cu)
    bpy.context.collection.objects.link(cab)
    wm = lib.mat("white", (0.85, 0.85, 0.83), rough=0.35)
    cu.materials.append(wm)
    for loc in [(0.62, -0.56, 0.02), (0.68, -0.64, 0.02)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, location=loc)
        bpy.context.object.scale = (1, 1, 0.7)
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.materials.append(wm)
    # ceiling fan: blades between a light and the floor, so their shadow sweeps the room
    bpy.ops.object.empty_add(location=(0.2, 0.3, 2.0))
    hub = bpy.context.object
    bm = lib.mat("blade", (0.05, 0.05, 0.05))
    for k in range(3):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
        b = bpy.context.object
        b.scale = (0.9, 0.14, 0.01)
        b.location = (0.45 * math.cos(k * 2.094), 0.45 * math.sin(k * 2.094), 0)
        b.rotation_euler = (0, 0, k * 2.094)
        b.parent = hub
        b.data.materials.append(bm)
        b.visible_camera = False
    ease(hub, "rotation_euler", [(1, (0, 0, 0)), (150, (0, 0, math.radians(-900)))])
    linear(hub)
    lib.spot((0.2, 0.3, 3.6), (0, 0, 0), 520, angle=70, color=(1, 0.83, 0.62), blend=0.6)
    lib.area((-3, 1.5, 1.4), (70, 0, -110), 220, 2.5, (0.45, 0.6, 1))    # cool window light
    c, tg = lib.camera((0.9, -1.5, 1.6), target=(0.05, -0.15, 0), lens=40, dof=2.2)
    ease(c, "location", [(1, (1.1, -1.7, 1.9)), (150, (0.55, -1.1, 1.25))])
    return sc


# ------------------------------------------------------------------ WAEC / JAMB papers
def paper_tex(kind):
    p = os.path.join(TEX, f"paper_{kind}.png")
    W, H = 850, 1100
    im = Image.new("RGB", (W, H), (236, 230, 214))
    d = ImageDraw.Draw(im)
    rng = random.Random(len(kind))
    for _ in range(2500):
        x, y = rng.randint(0, W), rng.randint(0, H)
        d.point((x, y), fill=(215, 207, 188))
    big, mid, sm = pf("Anton-Regular.ttf", 64), pf("SpaceMono-Bold.ttf", 28), pf("SpaceMono-Regular.ttf", 24)
    ink = (30, 40, 70)
    if kind == "waec":
        d.text((W / 2, 90), "WASSCE", font=big, fill=(20, 90, 50), anchor="mm")
        d.text((W / 2, 160), "STATEMENT OF RESULT", font=mid, fill=ink, anchor="mm")
        rows = [("ENGLISH LANGUAGE", "C4"), ("MATHEMATICS", "B3"), ("LITERATURE IN ENG.", "B2"), ("GOVERNMENT", "C5"),
                ("YORUBA", "A1"), ("CIVIC EDUCATION", "B3"), ("ECONOMICS", "C6"), ("CRS / IRS", "B3")]
        d.text((70, 230), "CANDIDATE:  ****** ******", font=sm, fill=ink)
        d.text((70, 270), "EXAM YEAR:  2022", font=sm, fill=ink)
        for i, (s, g) in enumerate(rows):
            y = 360 + i * 70
            d.line([(60, y - 18), (W - 60, y - 18)], fill=(180, 170, 150), width=2)
            d.text((70, y), s, font=sm, fill=ink)
            d.text((W - 120, y), g, font=mid, fill=ink)
    else:
        d.text((W / 2, 90), "UTME", font=big, fill=(30, 60, 140), anchor="mm")
        d.text((W / 2, 160), "RESULT SLIP  ·  2022", font=mid, fill=ink, anchor="mm")
        d.text((70, 230), "CANDIDATE:  ****** ******", font=sm, fill=ink)
        rows = [("USE OF ENGLISH", "62"), ("LITERATURE", "58"), ("GOVERNMENT", "55"), ("C.R.S. / I.R.S.", "61")]
        for i, (s, g) in enumerate(rows):
            y = 340 + i * 80
            d.line([(60, y - 22), (W - 60, y - 22)], fill=(180, 170, 150), width=2)
            d.text((70, y), s, font=sm, fill=ink)
            d.text((W - 130, y), g, font=mid, fill=ink)
        d.text((70, 700), "AGGREGATE", font=mid, fill=ink)
        d.text((W - 150, 700), "236", font=big, fill=(150, 30, 30))
        d.rectangle([W - 260, 860, W - 70, 1040], outline=(60, 60, 60), width=3)
        d.text((W - 165, 950), "PHOTO", font=sm, fill=(140, 140, 140), anchor="mm")
    im.save(p)
    return p


def wood_mat():
    m = lib.mat("wood", (0.25, 0.13, 0.06), rough=0.45)
    nt = m.node_tree
    w = nt.nodes.new("ShaderNodeTexWave")
    w.inputs["Scale"].default_value = 3.5
    w.inputs["Distortion"].default_value = 6
    w.inputs["Detail"].default_value = 4
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.elements[0].color = (0.12, 0.05, 0.02, 1)
    r.color_ramp.elements[1].color = (0.36, 0.19, 0.08, 1)
    nt.links.new(w.outputs["Fac"], r.inputs["Fac"])
    nt.links.new(r.outputs[0], nt.nodes["Principled BSDF"].inputs["Base Color"])
    return m


def paper(path, loc, size=(0.85, 1.1)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc)
    p = bpy.context.object
    p.scale = (size[0], size[1], 1)
    p.data.materials.append(lib.image_mat("paper", path, rough=0.7))
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.subdivide(number_cuts=10)
    bpy.ops.object.mode_set(mode="OBJECT")
    return p


def shot_slips():
    sc = lib.reset(120, samples=8)
    lib.world((0.01, 0.009, 0.008), studio=False)
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0))
    bpy.context.object.data.materials.append(wood_mat())
    a = paper(paper_tex("waec"), (0, 0, 0))
    b = paper(paper_tex("jamb"), (0, 0, 0))
    ease(a, "location", [(1, (-0.6, 0.3, 2.2)), (34, (-0.38, 0.05, 0.004))])
    ease(a, "rotation_euler", [(1, (0.6, -0.4, 1.2)), (34, (0, 0, math.radians(8)))])
    ease(b, "location", [(14, (0.9, -0.4, 2.4)), (50, (0.42, -0.12, 0.008))])
    ease(b, "rotation_euler", [(14, (-0.5, 0.7, -1.4)), (50, (0, 0, math.radians(-11)))])
    lib.area((-1.5, -1, 3), (25, -20, 0), 380, 2, (1, 0.85, 0.65))
    lib.area((2, 1, 2), (-40, 40, 0), 90, 2, (0.6, 0.7, 1))
    c, tg = lib.camera((0.1, -0.6, 2.8), target=(0, 0, 0), lens=38, dof=2.8)
    ease(c, "location", [(1, (0.15, -0.7, 3.0)), (120, (0.0, -0.45, 2.35))])
    return sc


# ------------------------------------------------------------------ passport + boarding pass
def passport_tex():
    p = os.path.join(TEX, "passport.png")
    W, H = 700, 980
    im = Image.new("RGB", (W, H), (14, 68, 40))
    d = ImageDraw.Draw(im)
    gold = (214, 172, 84)
    d.text((W / 2, 140), "FEDERAL REPUBLIC", font=pf("DMSerifDisplay-Regular.ttf", 50), fill=gold, anchor="mm")
    d.text((W / 2, 205), "OF NIGERIA", font=pf("DMSerifDisplay-Regular.ttf", 50), fill=gold, anchor="mm")
    d.ellipse([W / 2 - 120, 330, W / 2 + 120, 570], outline=gold, width=8)       # generic emblem, not the real arms
    d.polygon([(W / 2, 370), (W / 2 + 70, 520), (W / 2 - 70, 520)], outline=gold, width=8)
    d.text((W / 2, 720), "PASSPORT", font=pf("DMSerifDisplay-Regular.ttf", 76), fill=gold, anchor="mm")
    im.save(p)
    return p


def ticket_tex():
    p = os.path.join(TEX, "ticket.png")
    W, H = 1100, 420
    im = Image.new("RGB", (W, H), (238, 234, 224))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 70], fill=(20, 40, 90))
    d.text((30, 35), "BOARDING PASS", font=pf("SpaceMono-Bold.ttf", 34), fill=(240, 240, 240), anchor="lm")
    d.text((60, 150), "LOS", font=pf("Anton-Regular.ttf", 120), fill=(20, 30, 50))
    d.text((390, 200), "→", font=pf("SpaceMono-Bold.ttf", 90), fill=(20, 30, 50))
    d.text((560, 150), "LHR", font=pf("Anton-Regular.ttf", 120), fill=(20, 30, 50))
    d.text((60, 330), "LAGOS          LONDON          SEAT 14A", font=pf("SpaceMono-Regular.ttf", 28), fill=(80, 80, 90))
    d.line([(860, 80), (860, 410)], fill=(150, 150, 150), width=3)
    im.save(p)
    return p


def shot_passport():
    sc = lib.reset(120, samples=8)
    sc.render.use_motion_blur = False
    lib.world((0.01, 0.009, 0.008), studio=False)
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0))
    bpy.context.object.data.materials.append(wood_mat())
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.15, 0.05, 0.03))
    bk = bpy.context.object
    bk.scale = (0.62, 0.88, 0.05)
    bv = bk.modifiers.new("b", "BEVEL")
    bv.width, bv.segments = 0.02, 3
    bk.data.materials.append(lib.mat("green", (0.02, 0.12, 0.06), rough=0.55))
    bpy.ops.mesh.primitive_plane_add(size=1, location=(-0.15, 0.05, 0.0555))
    cv = bpy.context.object
    cv.scale = (0.6, 0.86, 1)
    m = lib.image_mat("cover", passport_tex(), rough=0.5)
    m.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.25
    cv.data.materials.append(m)
    for o in (bk, cv):
        o.parent = None
    tk = paper(ticket_tex(), (0.55, -0.35, 0.002), size=(1.1, 0.42))
    tk.rotation_euler = (0, 0, math.radians(14))
    for i in range(6):                                   # a few pound coins scattered
        lib.coin((0.62 + 0.13 * math.cos(i * 1.7), 0.42 + 0.1 * math.sin(i * 2.3), 0.012 + 0.012 * i), r=0.07,
                 mat_=lib.mat("coin", (0.8, 0.6, 0.25), metal=1, rough=0.25))
    lib.area((-1.5, -1, 2.5), (25, -25, 0), 320, 2, (1, 0.86, 0.66))
    sw = lib.strip((-3, -0.5, 1.0), (60, 0, -90), 0.3, 2, (1, 0.95, 0.8), 30)
    ease(sw, "location", [(1, (-3, -1.5, 1.0)), (120, (3, -1.5, 1.0))])
    c, tg = lib.camera((-0.8, -2.2, 1.7), target=(0.1, 0, 0), lens=45, dof=2.6)
    ease(c, "location", [(1, (-1.0, -2.4, 1.9)), (120, (-0.3, -1.8, 1.35))])
    return sc


# ------------------------------------------------------------------ falling naira (transparent overlay)
def note_tex(f, box):
    p = os.path.join(TEX, os.path.basename(f).replace(".jpg", ".png"))
    Image.open(os.path.join(PH, f)).convert("RGB").crop(box).save(p)
    return p


def shot_naira():
    sc = lib.reset(150, transparent=True, samples=8)
    sc.render.use_motion_blur = True
    lib.world((0.3, 0.27, 0.22), strength=0.6, studio=False)
    mats = [lib.image_mat("n1000", note_tex("naira_1000.jpg", (90, 54, 954, 488)), rough=0.6),
            lib.image_mat("n500", note_tex("naira_500.jpg", (100, 52, 940, 470)), rough=0.6)]
    random.seed(11)
    for i in range(30):
        bpy.ops.mesh.primitive_plane_add(size=1)
        n = bpy.context.object
        n.scale = (1.3, 0.65, 1)
        n.data.materials.append(mats[i % 2])
        bend = n.modifiers.new("bend", "SIMPLE_DEFORM")
        bend.deform_method, bend.angle = "BEND", math.radians(random.uniform(-40, 40))
        x, y = random.uniform(-3.4, 3.4), random.uniform(-1.5, 2.5)
        f0 = random.randint(-90, 110)
        dur = random.randint(90, 130)
        sway = random.uniform(0.3, 0.8)
        steps = 6
        for s in range(steps + 1):
            k = s / steps
            n.location = (x + sway * math.sin(k * 6 + i), y, 3.0 - 6.2 * k)
            n.rotation_euler = (random.uniform(-1.4, 1.4), random.uniform(-1.4, 1.4), random.uniform(-3, 3))
            n.keyframe_insert("location", frame=f0 + dur * k)
            n.keyframe_insert("rotation_euler", frame=f0 + dur * k)
    lib.area((-2, -4, 4), (45, 0, -25), 1200, 4, (1, 0.9, 0.75))
    lib.area((3, -2, -1), (110, 0, 60), 300, 3, (1, 0.8, 0.5))
    lib.camera((0, -7, 0), target=(0, 0, 0), lens=40)
    return sc


# ------------------------------------------------------------------ vinyl on a turntable
def label_tex():
    p = os.path.join(TEX, "label.png")
    W = 800
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, W, W], fill=(214, 160, 60))
    d.ellipse([20, 20, W - 20, W - 20], outline=(120, 80, 20), width=4)
    d.text((W / 2, 220), "MR. MONEY", font=pf("Anton-Regular.ttf", 110), fill=(20, 14, 8), anchor="mm")
    d.text((W / 2, 320), "WITH THE VIBE", font=pf("SpaceMono-Bold.ttf", 52), fill=(20, 14, 8), anchor="mm")
    d.text((W / 2, 560), "ASAKE  ·  2022", font=pf("SpaceMono-Bold.ttf", 44), fill=(20, 14, 8), anchor="mm")
    d.text((W / 2, 630), "SIDE A  ·  33⅓", font=pf("SpaceMono-Regular.ttf", 32), fill=(60, 40, 10), anchor="mm")
    d.ellipse([W / 2 - 22, W / 2 - 22, W / 2 + 22, W / 2 + 22], fill=(10, 10, 10))
    im.save(p)
    return p


def shot_vinyl():
    sc = lib.reset(150)
    lib.world(strength=0.4)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.08))
    base = bpy.context.object
    base.scale = (2.6, 2.0, 0.16)
    base.data.materials.append(wood_mat())
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=0.86, depth=0.03, location=(-0.3, 0, 0.015))
    bpy.context.object.data.materials.append(lib.mat("platter", (0.6, 0.6, 0.62), metal=1, rough=0.3))
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=0.8, depth=0.012, location=(-0.3, 0, 0.036))
    rec = bpy.context.object
    vm = lib.mat("vinyl", (0.01, 0.01, 0.012), rough=0.18, coat=0.5)
    nt = vm.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    wv = nt.nodes.new("ShaderNodeTexWave")
    wv.wave_type = "RINGS"
    wv.inputs["Scale"].default_value = 60
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.15
    nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
    nt.links.new(wv.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], nt.nodes["Principled BSDF"].inputs["Normal"])
    rec.data.materials.append(vm)
    bpy.ops.mesh.primitive_plane_add(size=0.6, location=(-0.3, 0, 0.0425))
    lab = bpy.context.object
    lab.data.materials.append(lib.image_mat("label", label_tex(), rough=0.5, alpha=True))
    lab.active_material.blend_method = "HASHED" if hasattr(lab.active_material, "blend_method") else None
    lab.parent = rec
    lab.matrix_parent_inverse = rec.matrix_world.inverted()
    ease(rec, "rotation_euler", [(1, (0, 0, 0)), (150, (0, 0, math.radians(-360 * 2.75)))])
    linear(rec)
    # tonearm
    am = lib.mat("arm", (0.75, 0.75, 0.78), metal=1, rough=0.2)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.2, location=(0.85, 0.75, 0.1))
    bpy.context.object.data.materials.append(am)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=1.25, location=(0.55, 0.25, 0.16), rotation=(0, math.radians(90), math.radians(58)))
    bpy.context.object.data.materials.append(am)
    bpy.ops.mesh.primitive_cube_add(size=0.08, location=(0.22, -0.28, 0.08))
    bpy.context.object.data.materials.append(lib.mat("head", (0.05, 0.05, 0.05), rough=0.3))
    lib.spot((-0.6, -0.8, 3.0), (15, 0, 0), 600, angle=50, color=(1, 0.82, 0.6))
    lib.area((2, 2, 1.5), (-50, 40, 0), 250, 2, (0.6, 0.7, 1))
    lib.strip((-1, -2.5, 1.6), (60, 0, 0), 3, 0.2, (1, 0.9, 0.8), 14)
    c, tg = lib.camera((-1.6, -2.2, 0.75), target=(-0.3, 0.05, 0.05), lens=42, dof=2.0)
    ease(c, "location", [(1, (-1.9, -2.0, 0.85)), (150, (-0.7, -2.3, 0.55))])
    return sc


# ------------------------------------------------------------------ mic in a spotlight
def shot_mic():
    sc = lib.reset(120)
    lib.world((0.003, 0.003, 0.004), studio=False)
    lib.floor(z=0, color=(0.01, 0.01, 0.012), rough=0.2)
    chrome = lib.mat("chrome", (0.85, 0.85, 0.87), metal=1, rough=0.1)
    black = lib.mat("blk", (0.012, 0.012, 0.012), metal=0.6, rough=0.28)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.03, location=(0, 0, 0.015))
    bpy.context.object.data.materials.append(black)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.016, depth=1.62, location=(0, 0, 0.81))
    bpy.context.object.data.materials.append(chrome)
    bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=0.028, radius2=0.045, depth=0.3, location=(0, -0.04, 1.74), rotation=(math.radians(-14), 0, 0))
    bpy.ops.object.shade_smooth()
    bpy.context.object.data.materials.append(black)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.072, location=(0, -0.08, 1.93))
    bpy.ops.object.shade_smooth()
    bpy.context.object.data.materials.append(lib.mat("inner", (0.02, 0.02, 0.02), rough=0.6))
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=0.078, location=(0, -0.08, 1.93))
    grill = bpy.context.object
    wf = grill.modifiers.new("w", "WIREFRAME")
    wf.thickness = 0.0022
    grill.data.materials.append(chrome)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.074, minor_radius=0.008, location=(0, -0.08, 1.9), rotation=(math.radians(76), 0, 0))
    bpy.context.object.data.materials.append(chrome)
    # haze inside the beam only: a cone of thin volume
    bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=1.5, radius2=0.08, depth=4.6, location=(0, 0.25, 2.3))
    cone = bpy.context.object
    vm = bpy.data.materials.new("haze")
    vm.use_nodes = True
    nt = vm.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    v = nt.nodes.new("ShaderNodeVolumeScatter")
    v.inputs["Density"].default_value = 0.022
    nt.links.new(v.outputs[0], o.inputs["Volume"])
    cone.data.materials.append(vm)
    cone.visible_shadow = False
    lib.spot((0, 0.25, 4.6), (0, 0, 0), 3500, angle=34, color=(1, 0.84, 0.6), blend=0.35)
    lib.area((-2, -2, 2), (50, 0, -45), 25, 2, (0.5, 0.6, 1))
    lib.strip((1.5, -2.5, 2.2), (70, 0, 30), 1.2, 0.15, (1, 0.9, 0.8), 25)
    lib.dust(45, [(-0.9, 0.9), (-0.5, 1.0), (0.3, 3.5)], seed=9, frames=120, drift=(0.1, 0, 0.15))
    c, tg = lib.camera((0.9, -1.9, 1.75), target=(0, -0.05, 1.82), lens=60, dof=1.8)
    ease(c, "location", [(1, (1.1, -2.1, 1.6)), (120, (0.25, -1.55, 1.95))])
    return sc


# ------------------------------------------------------------------ candles (Brixton)
def flame(x, y, base, s=1.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.004 * s, depth=0.05 * s, location=(x, y, base + 0.02 * s))
    bpy.context.object.data.materials.append(lib.mat("wick", (0.01, 0.01, 0.01)))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03 * s, location=(x, y, base + 0.07 * s))
    fl = bpy.context.object
    bpy.ops.object.shade_smooth()
    fl.scale = (1, 1, 2.6)
    tp = fl.modifiers.new("t", "SIMPLE_DEFORM")
    tp.deform_method, tp.factor, tp.deform_axis = "TAPER", -1.2, "Z"
    fl.data.materials.append(lib.emission("flame", (1, 0.5, 0.12), 14))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.014 * s, location=(x, y, base + 0.06 * s))
    core = bpy.context.object
    core.scale = (1, 1, 2.2)
    core.data.materials.append(lib.emission("core", (1, 0.9, 0.7), 45))
    return fl


def shot_candles():
    sc = lib.reset(180)
    lib.world((0.003, 0.003, 0.004), studio=False)
    lib.floor(z=0, color=(0.03, 0.025, 0.02), rough=0.25)
    wax = lib.mat("wax", (0.92, 0.88, 0.8), rough=0.45)
    b = wax.node_tree.nodes["Principled BSDF"]
    b.inputs["Subsurface Weight"].default_value = 0.7
    b.inputs["Subsurface Radius"].default_value = (0.4, 0.2, 0.08)
    random.seed(5)
    lights = []
    for x, h in [(-0.32, 0.62), (0.32, 0.5)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.11, depth=h, location=(x, 0, h / 2))
        bpy.ops.object.shade_smooth()
        bpy.context.object.data.materials.append(wax)
        fl = flame(x, 0, h)
        lights.append((lib.point((x, 0, h + 0.08), 18, (1, 0.55, 0.2), radius=0.02), fl))
    for i in range(9):                                     # tea lights far behind: soft bokeh
        x, y = random.uniform(-2.2, 2.2), random.uniform(1.5, 3.5)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.05, location=(x, y, 0.025))
        bpy.context.object.data.materials.append(wax)
        flame(x, y, 0.05, 0.7)
        lights.append((lib.point((x, y, 0.12), 4, (1, 0.55, 0.2), radius=0.02), None))
    for L, fl in lights:
        e0 = L.data.energy
        for f in range(1, 181, 5):
            k = 0.78 + 0.22 * random.random()
            L.data.energy = e0 * k
            L.data.keyframe_insert("energy", frame=f)
            if fl:
                fl.scale = (1 + 0.08 * random.uniform(-1, 1), 1, 2.6 * (0.9 + 0.1 * k))
                fl.keyframe_insert("scale", frame=f)
    lib.area((0, -2.5, 0.6), (80, 0, 0), 6, 3, (1, 0.7, 0.45))
    c, tg = lib.camera((0, -2.4, 0.7), target=(0, 0, 0.55), lens=60, dof=1.4)
    ease(c, "location", [(1, (0.35, -2.6, 0.62)), (180, (-0.1, -2.05, 0.75))])
    return sc


SHOTS = {"mm": shot_mm, "chapter": shot_chapter, "phone": shot_phone, "slips": shot_slips, "passport": shot_passport,
         "naira": shot_naira, "vinyl": shot_vinyl, "mic": shot_mic, "candles": shot_candles}

if __name__ == "__main__":
    a = sys.argv[1:]
    name, out = a[0], a[1]
    rest = a[2:]
    frame = None
    if "--still" in rest:
        i = rest.index("--still")
        frame = int(rest[i + 1])
        rest = rest[:i] + rest[i + 2:]
    SHOTS[name](*rest)
    if frame:
        lib.still(out, frame)
    else:
        lib.render(out)
