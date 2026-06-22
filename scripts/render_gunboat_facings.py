"""Blender headless: render a gunboat .glb at the C&C Remaster camera, 16 facings.

Run:
  ~/blender-portable/blender --background --python scripts/render_gunboat_facings.py -- \
      <model.glb> <out_dir> [bow_deg] [pitch_deg] [scale]

Camera = orthographic at 54deg elevation (measured from the Allied Destroyer's
foreshortening) so the renders sit at the same angle as every other RA unit.
The model is spun about the vertical axis for each facing; camera + light stay
fixed so lighting is consistent frame-to-frame.

Knobs (calibrated after the first render — GLB up/forward axes vary per tool):
  bow_deg   extra Z spin so the bow points screen-east at facing 4 (default 0)
  pitch_deg extra tilt if the tool exported the boat lying flat/upright (default 0)
  scale     uniform scale before fitting (default auto-fit to frame)
"""
import bpy, sys, math, os

argv = sys.argv[sys.argv.index("--") + 1:]
MODEL   = argv[0]
OUT     = argv[1]
BOW_DEG = float(argv[2]) if len(argv) > 2 else 0.0
PITCH   = float(argv[3]) if len(argv) > 3 else 0.0
USCALE  = float(argv[4]) if len(argv) > 4 else 0.0   # 0 = auto

ELEV_DEG = 54.0          # camera elevation above horizontal (measured from DD)
N_FACINGS = 16
RES = 512

os.makedirs(OUT, exist_ok=True)

# --- clean scene ---
bpy.ops.wm.read_factory_settings(use_empty=True)

# --- import model ---
ext = os.path.splitext(MODEL)[1].lower()
if ext in (".glb", ".gltf"):
    bpy.ops.import_scene.gltf(filepath=MODEL)
elif ext == ".obj":
    bpy.ops.wm.obj_import(filepath=MODEL)
elif ext == ".fbx":
    bpy.ops.import_scene.fbx(filepath=MODEL)
else:
    raise SystemExit(f"unsupported model type: {ext}")

# --- group all meshes under one empty pivot at origin, centred + fit ---
meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
if not meshes:
    raise SystemExit("no meshes imported")

pivot = bpy.data.objects.new("PIVOT", None)
bpy.context.scene.collection.objects.link(pivot)
for m in meshes:
    m.parent = pivot

# world-space bounds
import mathutils
mn = mathutils.Vector((1e9, 1e9, 1e9))
mx = mathutils.Vector((-1e9, -1e9, -1e9))
for m in meshes:
    for corner in m.bound_box:
        w = m.matrix_world @ mathutils.Vector(corner)
        mn = mathutils.Vector((min(mn[i], w[i]) for i in range(3)))
        mx = mathutils.Vector((max(mx[i], w[i]) for i in range(3)))
center = (mn + mx) / 2
size = max((mx - mn).x, (mx - mn).y, (mx - mn).z) or 1.0
pivot.location = -center * (1.0)            # bring centre to origin
# apply pitch + bow correction on the pivot
pivot.rotation_euler = (math.radians(PITCH), 0.0, math.radians(BOW_DEG))

fit = (USCALE if USCALE > 0 else (2.0 / size))
pivot.scale = (fit, fit, fit)

# --- orthographic camera at ELEV above horizontal, looking at origin ---
cam_data = bpy.data.cameras.new("cam"); cam_data.type = "ORTHO"; cam_data.ortho_scale = 2.6
cam = bpy.data.objects.new("cam", cam_data)
bpy.context.scene.collection.objects.link(cam)
el = math.radians(ELEV_DEG)
dist = 10.0
cam.location = (0.0, -dist * math.cos(el), dist * math.sin(el))
cam.rotation_euler = (math.radians(90.0 - ELEV_DEG), 0.0, 0.0)   # look down at origin from -Y
bpy.context.scene.camera = cam

# --- lighting: a sun from upper-front-left, fixed ---
sun_data = bpy.data.lights.new("sun", "SUN"); sun_data.energy = 4.0
sun = bpy.data.objects.new("sun", sun_data)
bpy.context.scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), 0, math.radians(35))
# soft fill via world
world = bpy.data.worlds.new("w"); bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.25, 0.25, 0.28, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.6

# --- render settings: transparent PNG, EEVEE ---
scn = bpy.context.scene
scn.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in type(scn.render).bl_rna.properties['engine'].enum_items] else "BLENDER_EEVEE"
scn.render.resolution_x = RES
scn.render.resolution_y = RES
scn.render.film_transparent = True
scn.render.image_settings.file_format = "PNG"
scn.render.image_settings.color_mode = "RGBA"

# --- render 16 facings: spin the pivot about Z ---
# facing s heading (compass, 0=N clockwise). bow base points where BOW_DEG sets it.
for s in range(N_FACINGS):
    heading = s * (360.0 / N_FACINGS)
    pivot.rotation_euler = (math.radians(PITCH), 0.0, math.radians(BOW_DEG - heading))
    scn.render.filepath = os.path.join(OUT, f"facing-{s:02d}.png")
    bpy.ops.render.render(write_still=True)
    print(f"rendered facing {s} (heading {heading:.0f})")

print("DONE", OUT)
