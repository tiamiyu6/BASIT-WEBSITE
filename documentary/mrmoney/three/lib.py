"""Shared Blender helpers for the Mr Money 3D shots (Cycles, CPU, denoised)."""
import math, os, random
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
MM = os.path.dirname(HERE)
FONT = os.path.join(MM, "fonts", "Anton-Regular.ttf")
SERIF = os.path.join(MM, "fonts", "DMSerifDisplay-Regular.ttf")
MONO = os.path.join(MM, "fonts", "SpaceMono-Bold.ttf")


def reset(frames, res=None, samples=10, transparent=False):
    res = res or tuple(int(v) for v in os.environ.get("THREE_RES", "960x540").split("x"))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.cycles.glossy_bounces = 4
    sc.cycles.transparent_max_bounces = 8
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.fps = 30
    sc.frame_start, sc.frame_end = 1, frames
    sc.render.film_transparent = transparent
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = 0.4
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    try:
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - Punchy"
    except Exception:
        pass
    w = bpy.data.worlds.new("w")
    sc.world = w
    return sc


def world(color=(0.01, 0.009, 0.008), strength=1.0, studio=True):
    """dark world; with studio=True a warm/cool gradient so metal has something to reflect"""
    w = bpy.context.scene.world
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    if not studio:
        bg.inputs[0].default_value = (*color, 1)
        bg.inputs[1].default_value = strength
        return
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
    cr = ramp.color_ramp
    cr.elements[0].position, cr.elements[0].color = 0.45, (*color, 1)
    cr.elements[1].position, cr.elements[1].color = 0.75, (0.5, 0.38, 0.22, 1)
    e = cr.elements.new(0.55)
    e.color = (0.03, 0.025, 0.02, 1)
    nt.links.new(ramp.outputs[0], bg.inputs[0])
    bg.inputs[1].default_value = strength


def mat(name, color, metal=0.0, rough=0.4, emit=None, emit_strength=0.0, coat=0.0, alpha=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    if coat:
        b.inputs["Coat Weight"].default_value = coat
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = emit_strength
    return m


def gold():
    m = mat("gold", (1.0, 0.58, 0.14), metal=1.0, rough=0.16)
    # faint brushed variation so it isn't plastic-flat
    nt = m.node_tree
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = 6
    r = nt.nodes.new("ShaderNodeMapRange")
    r.inputs["To Min"].default_value, r.inputs["To Max"].default_value = 0.13, 0.2
    nt.links.new(n.outputs["Fac"], r.inputs["Value"])
    nt.links.new(r.outputs["Result"], nt.nodes["Principled BSDF"].inputs["Roughness"])
    return m


def emission(name, color, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs[0].default_value = (*color, 1)
    e.inputs[1].default_value = strength
    nt.links.new(e.outputs[0], o.inputs[0])
    return m


def image_mat(name, path, rough=0.5, alpha=False, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage")
    t.image = bpy.data.images.load(path)
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    if emit:
        nt.links.new(t.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emit
    if alpha:
        nt.links.new(t.outputs["Alpha"], b.inputs["Alpha"])
    b.inputs["Roughness"].default_value = rough
    return m


def text(body, font=FONT, size=1.0, extrude=0.12, bevel=0.018, material=None, spacing=1.0):
    cu = bpy.data.curves.new("txt", "FONT")
    cu.body = body
    cu.font = bpy.data.fonts.load(font)
    cu.size = size
    cu.extrude = extrude
    cu.bevel_depth = bevel
    cu.bevel_resolution = 3
    cu.resolution_u = 8
    cu.space_character = spacing
    cu.align_x, cu.align_y = "CENTER", "CENTER"
    ob = bpy.data.objects.new("txt", cu)
    bpy.context.collection.objects.link(ob)
    ob.rotation_euler = (math.radians(90), 0, 0)
    if material:
        cu.materials.append(material)
    return ob


def floor(z=-0.75, color=(0.006, 0.006, 0.007), rough=0.12, size=60):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z))
    f = bpy.context.object
    f.data.materials.append(mat("floor", color, rough=rough))
    return f


def area(loc, rot, energy, size=1.0, color=(1, 1, 1), shape="RECTANGLE", size_y=None):
    bpy.ops.object.light_add(type="AREA", location=loc, rotation=[math.radians(a) for a in rot])
    L = bpy.context.object
    L.data.energy = energy
    L.data.shape = shape
    L.data.size = size
    if size_y:
        L.data.size_y = size_y
    L.data.color = color
    return L


def point(loc, energy, color=(1, 1, 1), radius=0.1):
    bpy.ops.object.light_add(type="POINT", location=loc)
    L = bpy.context.object
    L.data.energy = energy
    L.data.color = color
    L.data.shadow_soft_size = radius
    return L


def spot(loc, rot, energy, angle=35, color=(1, 1, 1), blend=0.4):
    bpy.ops.object.light_add(type="SPOT", location=loc, rotation=[math.radians(a) for a in rot])
    L = bpy.context.object
    L.data.energy = energy
    L.data.spot_size = math.radians(angle)
    L.data.spot_blend = blend
    L.data.color = color
    return L


def strip(loc, rot, w, h, color, strength):
    """visible emissive panel: gives metal a crisp highlight to reflect"""
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=[math.radians(a) for a in rot])
    p = bpy.context.object
    p.scale = (w, h, 1)
    p.data.materials.append(emission("strip", color, strength))
    p.visible_camera = False
    return p


def camera(loc, target=(0, 0, 0), lens=50, dof=None):
    bpy.ops.object.camera_add(location=loc)
    c = bpy.context.object
    c.data.lens = lens
    bpy.context.scene.camera = c
    bpy.ops.object.empty_add(location=target)
    tg = bpy.context.object
    tr = c.constraints.new("TRACK_TO")
    tr.target = tg
    tr.track_axis, tr.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
    if dof:
        c.data.dof.use_dof = True
        c.data.dof.focus_object = tg
        c.data.dof.aperture_fstop = dof
    return c, tg


def key(ob, path, frame, value, interp=None):
    setattr(ob, path, value) if not isinstance(value, tuple) else setattr(ob, path, value)
    ob.keyframe_insert(data_path=path, frame=frame)
    if interp and ob.animation_data and ob.animation_data.action:
        for fc in _fcurves(ob):
            if fc.data_path == path:
                for kp in fc.keyframe_points:
                    kp.interpolation = interp


def _fcurves(ob):
    act = ob.animation_data.action
    if hasattr(act, "fcurves"):
        return act.fcurves
    out = []                                    # Blender 5 layered actions
    for layer in act.layers:
        for st in layer.strips:
            for cb in st.channelbags:
                out.extend(cb.fcurves)
    return out


def linear(ob):
    if ob.animation_data and ob.animation_data.action:
        for fc in _fcurves(ob):
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"


def coin(loc, r=0.16, mat_=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=r, depth=r * 0.16, location=loc)
    c = bpy.context.object
    bev = c.modifiers.new("b", "BEVEL")
    bev.width, bev.segments = r * 0.05, 2
    bpy.ops.object.shade_smooth()
    if mat_:
        c.data.materials.append(mat_)
    return c


def dust(n, box, seed=1, size=0.005, strength=2.2, color=(1, 0.85, 0.6), drift=(0, 0, 0.3), frames=120):
    """floating specks catching light"""
    random.seed(seed)
    m = emission("dust", color, strength)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=size)
    proto = bpy.context.object
    proto.data.materials.append(m)
    obs = []
    for i in range(n):
        o = proto.copy()
        bpy.context.collection.objects.link(o)
        p = [random.uniform(a, b) for a, b in box]
        o.location = p
        o.keyframe_insert("location", frame=1)
        o.location = (p[0] + drift[0] + random.uniform(-0.2, 0.2), p[1] + drift[1], p[2] + drift[2] + random.uniform(-0.1, 0.1))
        o.keyframe_insert("location", frame=frames)
        linear(o)
        o.scale = [random.uniform(0.5, 1.6)] * 3
        obs.append(o)
    bpy.data.objects.remove(proto)
    return obs


def render(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    sc = bpy.context.scene
    sc.render.filepath = os.path.join(out_dir, "f_")
    sc.render.use_overwrite = False             # resumable: frames already on disk are skipped
    sc.render.use_placeholder = True
    bpy.ops.render.render(animation=True)


def still(path, frame):
    sc = bpy.context.scene
    sc.frame_set(frame)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)


def panels(warm=(1, 0.8, 0.55)):
    """big soft sources behind the camera: what the front faces of metal letters reflect"""
    strip((0, -16, 1.5), (90, 0, 0), 22, 7, warm, 2.2)
    strip((0, -10, 6), (60, 0, 0), 14, 2, (1, 0.92, 0.8), 6)
