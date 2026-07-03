"""Blender headless: PROCEDURAL TD Gunboat for the C&C Remaster camera — no GLB import.

Builds the boat from primitives + a custom hull-plan mesh (the render_helideck.py
approach) so every facing is geometrically exact: no image-gen rotation drift, no
Tripo "toy" mesh, and the gun is a SEPARATE model by construction (no extraction
from the fused TD sprite).

Look is matched to the TD-Assets HD gunboat frames (white hull, green team-colour
gunwale + bridge, grey boxy 3x2 missile-tube launcher on the foredeck). Team-colour
greens sampled from boat-0000.tga: bright (61,195,82) / mid (41,128,52) sRGB.

Modes:
  body    16 facings, hull only (turret spot left as a flat pedestal ring)
  turret  32 facings, launcher box only, same camera/scale as body (composite-ready)

Camera: orthographic, 54 deg elevation, FIXED ortho scale (no auto-fit) so body and
turret renders share px-per-unit = RES/ORTHO. Facing 0 = bow NORTH (screen up),
headings clockwise — direct Dir_To_16/32 frame indexing (VESSEL_TDGUNBOAT convention).
Turret plan spot = +0.52 units from hull centre toward the bow, deck top at z=0.315.

Run: ~/blender-portable/blender --background --python scripts/render_tdgunboat.py -- <mode> <out_dir>
License: GPL v3.
"""
import bpy, sys, math, os

argv = sys.argv[sys.argv.index("--") + 1:]
MODE = argv[0]            # body | turret
OUT  = argv[1]
assert MODE in ("body", "turret"), MODE

ELEV_DEG = 54.0
RES = 512
ORTHO = 2.9               # world units across the frame; px/unit = RES/ORTHO
N_FACINGS = 16 if MODE == "body" else 32
BOW_DEG = 90.0            # model bow = +X; +90 puts the bow at screen NORTH for facing 0
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)

def srgb(r, g, b):
    """sRGB 0-255 -> linear floats for Principled base colour."""
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (lin(r), lin(g), lin(b))

def mat(name, rgb255, rough=0.6, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*srgb(*rgb255), 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m

HULLW = mat("hull",  (205, 206, 208), 0.65)   # white hull sides
DECKW = mat("deck",  (192, 193, 195), 0.75)   # deck, a half-step darker
WLINE = mat("wline", (58, 60, 64),   0.6)     # dark waterline / lower hull
GREEN = mat("team",  (48, 150, 62),  0.55)    # team-colour green (ref-sampled mid ramp)
GREEND= mat("teamd", (30, 96, 36),   0.6)     # dark green accents
GREY  = mat("grey",  (132, 133, 136), 0.55)   # launcher / fittings
DARK  = mat("dark",  (40, 41, 44),   0.5)     # tubes / mast

def box(sx, sy, sz, loc, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.scale = (sx / 2, sy / 2, sz / 2); o.rotation_euler = rot
    o.data.materials.append(m); return o

def cyl(r, depth, loc, m, rot=(0, 0, 0), verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, vertices=verts, location=loc)
    o = bpy.context.active_object
    o.rotation_euler = rot; o.data.materials.append(m); return o

# Hull plan half-outline (+y side), bow at +X, stern rounded. CCW when mirrored.
HALF = [(1.20, 0.000), (1.05, 0.060), (0.85, 0.115), (0.60, 0.160), (0.30, 0.190),
        (0.00, 0.205), (-0.40, 0.205), (-0.75, 0.198), (-0.95, 0.170), (-1.08, 0.120),
        (-1.15, 0.050)]
OUTLINE = HALF + [(-1.17, 0.0)] + [(x, -y) for x, y in reversed(HALF) if y != 0.0]

def hull_prism(scale_xy, z0, z1, m):
    """Extruded hull-plan prism between z0..z1, plan scaled about the origin."""
    sx, sy = scale_xy
    n = len(OUTLINE)
    verts = [(x * sx, y * sy, z0) for x, y in OUTLINE] + \
            [(x * sx, y * sy, z1) for x, y in OUTLINE]
    faces = [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    faces += [list(range(n - 1, -1, -1)), list(range(n, 2 * n))]
    mesh = bpy.data.meshes.new("hullplan"); mesh.from_pydata(verts, [], faces)
    mesh.validate(); mesh.update()
    o = bpy.data.objects.new("hullplan", mesh)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(m); return o

if MODE == "body":
    hull_prism((0.985, 0.94), -0.03, 0.06, WLINE)   # dark lower hull / waterline
    hull_prism((1.0, 1.0), 0.05, 0.26, HULLW)       # white hull sides
    hull_prism((1.035, 1.10), 0.26, 0.30, GREEN)    # green gunwale lip
    hull_prism((0.94, 0.86), 0.30, 0.315, DECKW)    # inset deck

    # bridge (green, team colour) — midship-aft, stepped, with mast
    box(0.52, 0.30, 0.18, (-0.38, 0, 0.405), GREEN)
    box(0.38, 0.24, 0.12, (-0.34, 0, 0.55), GREEN)
    box(0.10, 0.26, 0.04, (-0.16, 0, 0.44), GREEND)           # front detail band
    box(0.16, 0.10, 0.06, (-0.60, -0.06, 0.525), GREEND)      # aft bridge box
    cyl(0.014, 0.42, (-0.30, 0.05, 0.80), DARK, verts=12)     # mast
    box(0.035, 0.28, 0.028, (-0.30, 0, 0.94), DARK)           # yardarm

    # deck fittings: turret pedestal ring (bare — turret renders separately),
    # foredeck hatch, aft vents, bow bullnose
    cyl(0.095, 0.022, (0.52, 0, 0.322), GREY)                 # pedestal ring at gun spot
    box(0.18, 0.13, 0.035, (0.14, 0, 0.33), GREY)             # foredeck hatch
    box(0.08, 0.10, 0.05, (-0.80, 0.06, 0.34), GREY)          # aft vents
    box(0.08, 0.10, 0.05, (-0.95, -0.05, 0.34), GREY)
    box(0.07, 0.05, 0.03, (1.02, 0, 0.325), GREY)             # bow bullnose

else:  # turret — the boxy 3x2 Tomahawk tube launcher, centred at origin
    cyl(0.085, 0.05, (0, 0, 0.025), DARK)                     # pedestal
    box(0.42, 0.27, 0.18, (0.0, 0, 0.15), GREY)              # launcher box
    box(0.40, 0.25, 0.022, (0.01, 0, 0.25), GREY)             # top plate
    # 6 tube muzzles, 3 across x 2 high, on the +X face
    for yy in (-0.078, 0.0, 0.078):
        for zz in (0.11, 0.19):
            cyl(0.033, 0.06, (0.21, yy, zz), DARK, rot=(0, math.pi / 2, 0), verts=16)
    box(0.06, 0.27, 0.035, (-0.20, 0, 0.10), DARK)            # rear counterweight sill

# --- group under pivot ---
pivot = bpy.data.objects.new("PIVOT", None)
bpy.context.scene.collection.objects.link(pivot)
for o in [o for o in bpy.context.scene.objects if o.type == "MESH"]:
    o.parent = pivot

# --- camera / light / render rig (matches render_gunboat_facings.py) ---
cam_data = bpy.data.cameras.new("cam"); cam_data.type = "ORTHO"; cam_data.ortho_scale = ORTHO
cam = bpy.data.objects.new("cam", cam_data); bpy.context.scene.collection.objects.link(cam)
el = math.radians(ELEV_DEG); dist = 10.0
cam.location = (0.0, -dist * math.cos(el), dist * math.sin(el))
cam.rotation_euler = (math.radians(90.0 - ELEV_DEG), 0.0, 0.0)
bpy.context.scene.camera = cam

sun_data = bpy.data.lights.new("sun", "SUN"); sun_data.energy = 4.2
sun = bpy.data.objects.new("sun", sun_data); bpy.context.scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), 0, math.radians(35))
world = bpy.data.worlds.new("w"); bpy.context.scene.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.25, 0.25, 0.28, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.6

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
    print(f"rendered {MODE} facing {s}")
print("DONE", MODE, OUT)
