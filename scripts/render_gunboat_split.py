"""Render the GDI gunboat as BODY (gun removed, 16 facings) + TURRET (gun only,
32 facings) from the same GLB, at a SHARED scale so the turret overlays the hull
at the right size. The turret spins about its own vertical axis, centred on the
gun's rotation ring, so the engine can draw it as a normal RA vessel turret.

Run:
  blender -b -P scripts/render_gunboat_split.py -- <model.glb> body   <outdir>
  blender -b -P scripts/render_gunboat_split.py -- <model.glb> turret <outdir>

Gun region (from gunboat_ymap.py analysis): Y in [0.11,0.34], z > -0.02.
Camera = ortho 54deg elevation, BOW_DEG=0 PITCH=0 (validated vs deployed body).
"""
import bpy, sys, math, mathutils, os, bmesh

argv = sys.argv[sys.argv.index("--")+1:]
MODEL, MODE, OUT = argv[0], argv[1], argv[2]
GYLO, GYHI, GZTHR = 0.11, 0.34, -0.02     # gun bounding region (world)
ELEV = 54.0
RES = 512
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=MODEL)
o = [x for x in bpy.context.scene.objects if x.type == "MESH"][0]
M = o.matrix_world

def in_gun(p): return (GYLO < p.y < GYHI) and p.z > GZTHR

# --- whole-model bounds (= hull) -> shared fit scale, shared for body+turret ---
allp = [M @ v.co for v in o.data.vertices]
mn = mathutils.Vector((min(p[i] for p in allp) for i in range(3)))
mx = mathutils.Vector((max(p[i] for p in allp) for i in range(3)))
hull_center = (mn + mx) / 2
size = max((mx - mn).x, (mx - mn).y, (mx - mn).z) or 1.0
FIT = 2.0 / size

# --- gun centroid (rotation axis for the turret) ---
gunp = [p for p in allp if in_gun(p)]
gc = mathutils.Vector((sum(p[i] for p in gunp)/len(gunp) for i in range(3)))
gun_minz = min(p.z for p in gunp)
print(f"FIT={FIT:.4f} hull_center={tuple(round(c,3) for c in hull_center)} "
      f"gun_centroid={tuple(round(c,3) for c in gc)} gun_minz={gun_minz:.3f} ngun={len(gunp)}")

# --- delete to the chosen subset ---
bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
if MODE == "body":
    td = [v for v in bm.verts if in_gun(M @ v.co)]
else:
    td = [v for v in bm.verts if not in_gun(M @ v.co)]
bmesh.ops.delete(bm, geom=td, context='VERTS'); bm.to_mesh(o.data); bm.free()
print(f"MODE={MODE} deleted {len(td)} verts; kept {len(o.data.vertices)}")

# --- pivot: body spins about hull centre; turret spins about gun axis ---
pivot = bpy.data.objects.new("PIVOT", None)
bpy.context.scene.collection.objects.link(pivot)
o.parent = pivot
if MODE == "body":
    pivot.location = -hull_center
    N = 16
else:
    # centre the gun ring (X,Y) on origin; put deck level (gun_minz) at origin Z
    pivot.location = mathutils.Vector((-gc.x, -gc.y, -gun_minz))
    N = 32
pivot.scale = (FIT, FIT, FIT)

# --- camera, light, world (match render_gunboat_facings.py) ---
cam_d = bpy.data.cameras.new("c"); cam_d.type = "ORTHO"; cam_d.ortho_scale = 2.6
cam = bpy.data.objects.new("c", cam_d); bpy.context.scene.collection.objects.link(cam)
el = math.radians(ELEV)
cam.location = (0.0, -10*math.cos(el), 10*math.sin(el))
cam.rotation_euler = (math.radians(90-ELEV), 0, 0)
bpy.context.scene.camera = cam
sun = bpy.data.objects.new("s", bpy.data.lights.new("s", "SUN")); sun.data.energy = 4.0
bpy.context.scene.collection.objects.link(sun); sun.rotation_euler = (math.radians(50), 0, math.radians(35))
w = bpy.data.worlds.new("w"); bpy.context.scene.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.25, 0.25, 0.28, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
scn = bpy.context.scene
engs = [e.identifier for e in type(scn.render).bl_rna.properties['engine'].enum_items]
scn.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engs else "BLENDER_EEVEE"
scn.render.resolution_x = scn.render.resolution_y = RES
scn.render.film_transparent = True
scn.render.image_settings.file_format = "PNG"; scn.render.image_settings.color_mode = "RGBA"

prefix = "facing" if MODE == "body" else "turret"
for s in range(N):
    heading = s * (360.0 / N)
    pivot.rotation_euler = (0, 0, math.radians(-heading))
    scn.render.filepath = os.path.join(OUT, f"{prefix}-{s:02d}.png")
    bpy.ops.render.render(write_still=True)
print("DONE", MODE, OUT)
