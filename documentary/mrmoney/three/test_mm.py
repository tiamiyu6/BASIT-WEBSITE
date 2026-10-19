import bpy, math, time, sys
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = 24
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.film_transparent = False
font = bpy.data.fonts.load("/home/user/BASIT-WEBSITE/documentary/mrmoney/fonts/Anton-Regular.ttf")
bpy.ops.object.text_add()
t = bpy.context.object
t.data.body = "MM"; t.data.font = font; t.data.extrude = 0.12; t.data.bevel_depth = 0.02; t.data.align_x = "CENTER"; t.data.align_y = "CENTER"
m = bpy.data.materials.new("gold"); m.use_nodes = True
b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (1.0, 0.72, 0.28, 1); b.inputs["Metallic"].default_value = 1.0; b.inputs["Roughness"].default_value = 0.22
t.data.materials.append(m)
t.rotation_euler = (math.radians(90), 0, 0)
bpy.ops.object.camera_add(location=(0, -4, 0.2), rotation=(math.radians(88), 0, 0)); sc.camera = bpy.context.object
bpy.ops.object.light_add(type="AREA", location=(2, -2, 2)); L = bpy.context.object; L.data.energy = 400; L.data.size = 2
bpy.ops.object.light_add(type="AREA", location=(-2.5, -1, 1)); L2 = bpy.context.object; L2.data.energy = 200; L2.data.color = (1, 0.8, 0.6)
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.018, 0.015, 1)
sc.render.filepath = sys.argv[-1]
t0 = time.time(); bpy.ops.render.render(write_still=True); print("RENDER SEC", round(time.time() - t0, 1))
