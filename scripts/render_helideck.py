"""Blender headless: build a GDI naval helideck (proper model, v2) and render it at
the C&C Remaster camera (54deg ortho), 16 facings, for the TDCADECK overlay.

Designed to READ at ~50px sprite size: bold oval deck + high-contrast helipad
markings (ring + H) + one distinct island (angled bridge + mast + crane) on the
aft edge. Camera/light/render rig matches render_gunboat_facings.py.

Run: ~/blender-portable/blender --background --python scripts/render_helideck.py -- <out_dir> [bow_deg]
License: GPL v3.
"""
import bpy, sys, math, os

argv = sys.argv[sys.argv.index("--") + 1:]
OUT     = argv[0]
BOW_DEG = float(argv[1]) if len(argv) > 1 else 0.0
ELEV_DEG = 54.0; N_FACINGS = 16; RES = 512
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, rgb, rough=0.55, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*rgb, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m

DECK   = mat("deck",   (0.30, 0.31, 0.35), 0.7)        # dark steel deck
RIM    = mat("rim",    (0.16, 0.40, 0.16), 0.6)        # green team-colour edge
PAINT  = mat("paint",  (0.88, 0.78, 0.12), 0.5)        # gold helipad markings (GDI)
HULLG  = mat("island", (0.46, 0.47, 0.52), 0.5)        # light steel island
DARK   = mat("dark",   (0.20, 0.21, 0.24), 0.6)        # mast/crane

def cyl(rx, ry, depth, z, m, verts=56):
    bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=depth, vertices=verts, location=(0,0,z))
    o = bpy.context.active_object; o.scale = (rx, ry, 1.0); o.data.materials.append(m); return o

def box(sx, sy, sz, loc, m, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object; o.scale = (sx/2, sy/2, sz/2); o.rotation_euler = rot
    o.data.materials.append(m); return o

def torus(maj, min_, z, m):
    bpy.ops.mesh.primitive_torus_add(location=(0,0,z), major_radius=maj, minor_radius=min_,
                                     major_segments=48, minor_segments=8)
    o = bpy.context.active_object; o.scale = (1,1,0.35); o.data.materials.append(m); return o

# --- deck: oval (long along X = the keel), raised green rim, dark surface ---
cyl(1.30, 1.00, 0.06, 0.13, RIM)           # rim/lip (slightly larger, green)
cyl(1.24, 0.94, 0.14, 0.10, DECK)          # deck surface
TOP = 0.175
# helipad ring + H, painted, just above the deck
torus(0.60, 0.05, TOP, PAINT)
box(0.10, 0.62, 0.03, ( 0.22,0,TOP), PAINT)   # H right post
box(0.10, 0.62, 0.03, (-0.22,0,TOP), PAINT)   # H left post
box(0.36, 0.10, 0.03, ( 0.00,0,TOP), PAINT)   # H crossbar

# --- island on the aft edge (-X side), set inboard of the rim ---
ix = -0.86
box(0.40, 0.70, 0.46, (ix, 0.0, 0.36), HULLG)                 # bridge block
box(0.40, 0.22, 0.20, (ix, -0.28, 0.66), HULLG, rot=(math.radians(12),0,0))  # stepped upper bridge
box(0.05, 0.05, 0.62, (ix, 0.22, 0.72), DARK)                 # mast
box(0.05, 0.34, 0.04, (ix, 0.10, 0.92), DARK)                 # yardarm
box(0.07, 0.46, 0.06, (ix+0.30, 0.0, 0.50), DARK, rot=(0,math.radians(18),0))  # crane arm out over deck

# --- group under pivot ---
pivot = bpy.data.objects.new("PIVOT", None); bpy.context.scene.collection.objects.link(pivot)
for o in [o for o in bpy.context.scene.objects if o.type == "MESH"]: o.parent = pivot

cam_data = bpy.data.cameras.new("cam"); cam_data.type = "ORTHO"; cam_data.ortho_scale = 3.0
cam = bpy.data.objects.new("cam", cam_data); bpy.context.scene.collection.objects.link(cam)
el = math.radians(ELEV_DEG); dist = 10.0
cam.location = (0.0, -dist*math.cos(el), dist*math.sin(el))
cam.rotation_euler = (math.radians(90.0 - ELEV_DEG), 0.0, 0.0)
bpy.context.scene.camera = cam

sun_data = bpy.data.lights.new("sun","SUN"); sun_data.energy = 4.5
sun = bpy.data.objects.new("sun", sun_data); bpy.context.scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(52), 0, math.radians(35))
world = bpy.data.worlds.new("w"); bpy.context.scene.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.25,0.25,0.28,1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.65

scn = bpy.context.scene
eng = [e.identifier for e in type(scn.render).bl_rna.properties['engine'].enum_items]
scn.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in eng else "BLENDER_EEVEE"
scn.render.resolution_x = RES; scn.render.resolution_y = RES
scn.render.film_transparent = True
scn.render.image_settings.file_format = "PNG"; scn.render.image_settings.color_mode = "RGBA"

for s in range(N_FACINGS):
    heading = s * (360.0 / N_FACINGS)
    pivot.rotation_euler = (0.0, 0.0, math.radians(BOW_DEG - heading))
    scn.render.filepath = os.path.join(OUT, f"facing-{s:02d}.png")
    bpy.ops.render.render(write_still=True)
    print(f"rendered facing {s}")
print("DONE", OUT)
