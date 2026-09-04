#!/usr/bin/env python3
"""Blender scene + renderer for the TS wall / component tower family.

Proper meshes instead of voxel splats: the wall slab with its rounded crest,
seam and recessed panels, piers straddling every joined cell edge, sloped end
caps; the tower drum with four buttresses on the grid axes, ladder, platform
and team-colour ring; a twin-barrel Vulcan turret. Everything is built
procedurally in the TS palette and rendered with an orthographic camera at the
TS ground vehicles' 32-degree elevation and their light vector.

World units: 1 Blender unit = 1 cell (128 HD px). The camera looks from the
south (+Y = north = screen up). Renders are square-pixel at 2x and the packers
stretch them by 1/sin(32) so the ground plane is 1:1 (the base game's own HD
wall cheat), then downsample to the 176x320 canvas.

Run headless:
  blender -b -P scripts/ts_blender_walls.py -- --out <dir> [--only calib|walls|towers]
                                                 [--samples N] [--frames a,b,c]
Outputs PNGs named the way ts_pack_walls.py / ts_pack_towers.py --from-renders expect:
  wall_j{joins:02d}_d{stage}.png              16 joins x 3 damage stages
  tower_d{stage}.png                          bare tower healthy / damaged
  tower_make_{k:02d}.png                      rising buildup, 17 frames
  {vulc|rpg|sam}_f{facing:02d}_s{state}.png   32 facings x {0 idle,1 recoil,2 dmg,3 dmg recoil}
License: GPL v3.
"""
import math, os, sys
import bpy, bmesh
from mathutils import Vector

# ---------------------------------------------------------------- constants
CELL = 1.0
PX_PER_CELL = 128
CANVAS_W, CANVAS_H = 176, 320           # the packers' canvas (post-stretch)
ELEV = 32.0
STRETCH = 1.0 / math.sin(math.radians(ELEV))
SS = 2                                  # supersample
RENDER_W = CANVAS_W * SS
RENDER_H = int(round(CANVAS_H / STRETCH)) * SS
FACE_PX = PX_PER_CELL * math.cos(math.radians(ELEV)) * STRETCH   # screen px per world unit of height (~205)

# TS proportions per cell (from the TS screenshot): wall ~53 px tall / 32 thick;
# tower body ~90 px wide / 67 tall.
WALL_T = 0.25
WALL_H = 53.0 / FACE_PX
WALL_OVERSHOOT = 8.0 / 48.0
PIER_T, PIER_D, PIER_H = 0.33, 0.10, 62.0 / FACE_PX
CAP_LEN = 0.28
SEAM_W = 0.012
TOWER_R = 0.35
TOWER_H = 67.0 / FACE_PX
BUTTRESS_REACH = 0.50
BUTTRESS_H = 0.62 * TOWER_H
PLATFORM_H = 0.03

# TS light vector (vxl_render.py LIGHT, x east / y north / z up), ambient from the VPL ramp floor
LIGHT_DIR = Vector((-0.5, 0.6, 0.75)).normalized()
SUN_STRENGTH = 3.2
AMBIENT = 0.42

TEAM_GREEN = (0, 200, 0)


def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


_MATS = {}


def mat(name, rgb, roughness=0.85, emission=0.0):
    """Principled material whose albedo is the given sRGB colour."""
    key = (name, rgb)
    if key in _MATS:
        return _MATS[key]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    lin = tuple(srgb_to_linear(c) for c in rgb) + (1.0,)
    bsdf.inputs["Base Color"].default_value = lin
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Specular IOR Level"].default_value = 0.15 if "Specular IOR Level" in bsdf.inputs else 0.15
    if emission:
        bsdf.inputs["Emission Color"].default_value = lin
        bsdf.inputs["Emission Strength"].default_value = emission
    _MATS[key] = m
    return m


# TS colours (GTWALL / GTCTWR decoded with UNITTEM.PAL)
M_CONCRETE = lambda: mat("concrete", (150, 150, 150), 0.9)
M_CONCRETE_DK = lambda: mat("concrete_dk", (112, 112, 112), 0.9)
M_SEAM = lambda: mat("seam", (58, 58, 58), 0.95)
M_PIER = lambda: mat("pier", (150, 150, 150), 0.9)
M_PIER_CAP = lambda: mat("pier_cap", (170, 152, 96), 0.8)
M_TAN = lambda: mat("tan", (178, 160, 104), 0.85)
M_TAN_DK = lambda: mat("tan_dk", (128, 112, 66), 0.9)
M_FOOT = lambda: mat("foot", (128, 128, 128), 0.9)
M_PLATE = lambda: mat("plate", (150, 150, 168), 0.6)
M_PLATE_LT = lambda: mat("plate_lt", (168, 168, 166), 0.9)
M_RUBBLE = lambda: mat("rubble", (96, 94, 90), 1.0)
M_GUN = lambda: mat("gun", (118, 120, 118), 0.7)
M_GUN_DK = lambda: mat("gun_dk", (70, 72, 70), 0.8)
M_TEAM = lambda: mat("team", TEAM_GREEN, 0.7, emission=0.35)


# ---------------------------------------------------------------- scene
def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for m in list(bpy.data.materials):
        bpy.data.materials.remove(m)
    _MATS.clear()


def setup_scene(samples):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = False   # the Ubuntu build ships without OpenImageDenoise
    sc.cycles.use_adaptive_sampling = True
    sc.render.resolution_x = RENDER_W
    sc.render.resolution_y = RENDER_H
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    sc.view_settings.gamma = 1.0
    # camera: orthographic, from the south, 32 deg above the ground, aimed at the cell centre
    cam_data = bpy.data.cameras.new("cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = CANVAS_W / PX_PER_CELL       # frame width in cells (width is the larger dimension)
    cam_data.clip_start = 0.01
    cam_data.clip_end = 100.0
    cam = bpy.data.objects.new("cam", cam_data)
    sc.collection.objects.link(cam)
    d = 20.0
    e = math.radians(ELEV)
    cam.location = (0.0, -d * math.cos(e), d * math.sin(e))
    cam.rotation_euler = (math.radians(90.0 - ELEV), 0.0, 0.0)
    sc.camera = cam
    # frame height check: RENDER_H/RENDER_W of the width must cover the canvas after the stretch
    # sun along the TS light vector
    sun_data = bpy.data.lights.new("sun", type="SUN")
    sun_data.energy = SUN_STRENGTH
    sun_data.angle = math.radians(2.0)
    sun = bpy.data.objects.new("sun", sun_data)
    sc.collection.objects.link(sun)
    sun.rotation_euler = (-LIGHT_DIR).to_track_quat("-Z", "Y").to_euler()
    # ambient
    world = bpy.data.worlds.new("world")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    bg.inputs["Strength"].default_value = AMBIENT
    sc.world = world


def _link(obj):
    bpy.context.scene.collection.objects.link(obj)
    return obj


def box(name, cx, cy, cz, sx, sy, sz, material, bevel=0.0):
    """Axis-aligned box centred at (cx,cy) with its base at cz, size sx,sy,sz."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.scale = (sx, sy, sz)
    obj.location = (cx, cy, cz + sz / 2.0)
    obj.data.materials.append(material)
    if bevel > 0:
        mod = obj.modifiers.new("bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        mod.limit_method = "NONE"
    _link(obj)
    return obj


def prism(name, verts, faces, material):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    obj = bpy.data.objects.new(name, me)
    obj.data.materials.append(material)
    _link(obj)
    return obj


def ramp(name, along, sign, start, length, half_w, h_start, material):
    """A wedge that slopes from h_start at `start` down to the ground `length` further along `along`
    (x or y) in direction `sign`; centred on the other axis at 0."""
    a0, a1 = start, start + sign * length
    if along == "x":
        v = [(a0, -half_w, 0), (a0, half_w, 0), (a1, half_w, 0), (a1, -half_w, 0),
             (a0, -half_w, h_start), (a0, half_w, h_start), (a1, half_w, 0.01), (a1, -half_w, 0.01)]
    else:
        v = [(-half_w, a0, 0), (half_w, a0, 0), (half_w, a1, 0), (-half_w, a1, 0),
             (-half_w, a0, h_start), (half_w, a0, h_start), (half_w, a1, 0.01), (-half_w, a1, 0.01)]
    f = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    return prism(name, v, f, material)


def cylinder(name, cx, cy, cz, r, h, material, verts=48, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r, depth=h)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = (cx, cy, cz + h / 2.0)
    obj.data.materials.append(material)
    if bevel > 0:
        mod = obj.modifiers.new("bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        mod.limit_method = "ANGLE"
        mod.angle_limit = math.radians(60)
    for p in obj.data.polygons:
        p.use_smooth = True
    _link(obj)
    return obj


def torus(name, cx, cy, cz, R, r, material):
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=False, segments=48, radius=R)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.location = (cx, cy, cz)
    obj.data.materials.append(material)
    mod = obj.modifiers.new("skin", "SKIN")
    for v in obj.data.skin_vertices[0].data:
        v.radius = (r, r)
    sub = obj.modifiers.new("sub", "SUBSURF"); sub.levels = 2; sub.render_levels = 2
    _link(obj)
    return obj


# ---------------------------------------------------------------- wall
def wall_arm(along, sign, joined, junction, stage):
    """One arm from the cell centre toward an edge. joined: runs past the edge and
    carries a pier; otherwise it ends in a sloped cap. At a junction the arm
    starts outside the centre block so no two boxes share a top plane."""
    half = WALL_T / 2.0
    conc = M_CONCRETE() if stage < 2 else M_CONCRETE_DK()
    inner = half if junction else 0.0
    if joined:
        outer = CELL / 2.0 + WALL_OVERSHOOT
        length = outer - inner
        c = sign * (inner + length / 2.0)
        if along == "x":
            box(f"arm_{along}{sign}", c, 0, 0, length, WALL_T, WALL_H, conc, bevel=0.035)
        else:
            box(f"arm_{along}{sign}", 0, c, 0, WALL_T, length, WALL_H, conc, bevel=0.035)
        e = sign * CELL / 2.0
        if along == "x":
            box("pier", e, 0, 0, PIER_D, PIER_T, PIER_H, M_PIER(), bevel=0.02)
            box("pier_cap", e, 0, PIER_H, PIER_D + 0.02, PIER_T + 0.02, 0.018, M_PIER_CAP())
        else:
            box("pier", 0, e, 0, PIER_T, PIER_D, PIER_H, M_PIER(), bevel=0.02)
            box("pier_cap", 0, e, PIER_H, PIER_T + 0.02, PIER_D + 0.02, 0.018, M_PIER_CAP())
        # raised plates on both faces of the run, a shade lighter
        if stage == 0:
            pc = sign * (inner + 0.24)
            if along == "x":
                box("plate", pc, -half - 0.004, 0.04, 0.22, 0.008, WALL_H * 0.5, M_PLATE_LT())
                box("plate", pc, half + 0.004, 0.04, 0.22, 0.008, WALL_H * 0.5, M_PLATE_LT())
            else:
                box("plate", -half - 0.004, pc, 0.04, 0.008, 0.22, WALL_H * 0.5, M_PLATE_LT())
                box("plate", half + 0.004, pc, 0.04, 0.008, 0.22, WALL_H * 0.5, M_PLATE_LT())
    else:
        ramp(f"cap_{along}{sign}", along, sign, sign * inner, CAP_LEN, half, WALL_H * 0.92, conc)


def build_wall(joins, stage):
    n, e, s, w = joins & 1, joins & 2, joins & 4, joins & 8
    conc = M_CONCRETE() if stage < 2 else M_CONCRETE_DK()
    if joins == 0:
        box("lone", 0, 0, 0, 0.34, WALL_T, WALL_H, conc, bevel=0.035)
        ramp("cap_e", "x", 1, 0.17, 0.22, WALL_T / 2.0, WALL_H * 0.92, conc)
        ramp("cap_w", "x", -1, -0.17, 0.22, WALL_T / 2.0, WALL_H * 0.92, conc)
        return
    ns, ew = bool(n or s), bool(e or w)
    junction = ns and ew
    if ns:
        wall_arm("y", 1, n, junction, stage)
        wall_arm("y", -1, s, junction, stage)
    if ew:
        wall_arm("x", 1, e, junction, stage)
        wall_arm("x", -1, w, junction, stage)
    if junction:
        box("centre", 0, 0, 0, WALL_T, WALL_T, WALL_H, conc, bevel=0.035)
    if stage >= 1:
        # damage = chunks CUT OUT of the crest (boolean difference), plus rubble at the foot
        import random
        rnd = random.Random(joins * 7 + stage)
        bm = bmesh.new()
        for k in range(3 if stage == 1 else 7):
            px, py = rnd.uniform(-0.45, 0.45), rnd.uniform(-0.45, 0.45)
            if ns and not ew: px = rnd.uniform(-WALL_T / 2, WALL_T / 2)
            if ew and not ns: py = rnd.uniform(-WALL_T / 2, WALL_T / 2)
            size = rnd.uniform(0.06, 0.12)
            depth = WALL_H * (0.35 if stage == 1 else 0.6)
            r = bmesh.ops.create_cube(bm, size=1.0)
            for v in r["verts"]:
                v.co = (px + v.co.x * size, py + v.co.y * size, WALL_H + 0.02 + (v.co.z - 0.5) * depth * 2)
            box("rubble", px + rnd.uniform(-0.25, 0.25), py + rnd.uniform(-0.25, 0.25), 0,
                rnd.uniform(0.04, 0.08), rnd.uniform(0.04, 0.07), 0.03, M_RUBBLE())
        me = bpy.data.meshes.new("cutter")
        bm.to_mesh(me); bm.free()
        cutter = bpy.data.objects.new("cutter", me)
        _link(cutter)
        cutter.hide_render = True
        for obj in list(bpy.context.scene.objects):
            if obj.type == "MESH" and obj.name.split(".")[0] in ("arm_x1", "arm_x-1", "arm_y1", "arm_y-1", "centre", "lone", "pier"):
                mod = obj.modifiers.new("damage", "BOOLEAN")
                mod.operation = "DIFFERENCE"
                mod.object = cutter
                mod.solver = "EXACT"


# ---------------------------------------------------------------- tower
def build_tower(stage=0, height_frac=1.0, with_buttresses=True):
    h = TOWER_H * height_frac
    tan = M_TAN() if stage == 0 else M_TAN_DK()
    drum = cylinder("drum", 0, 0, 0, TOWER_R, h, tan, bevel=0.02)
    # base flare and two dark bands
    cylinder("flare", 0, 0, 0, TOWER_R + 0.04, min(0.03, h), M_TAN_DK())
    for z in (0.35, 0.68):
        if h * z < h:
            cylinder("band", 0, 0, h * z, TOWER_R + 0.006, 0.014, M_TAN_DK())
    if with_buttresses:
        bh = min(BUTTRESS_H, h)
        for (along, sign) in (("x", 1), ("x", -1), ("y", 1), ("y", -1)):
            # a wedge from inside the drum out to the reach, sloping from bh down to the wall height
            a0, a1 = TOWER_R - 0.08, BUTTRESS_REACH
            hw = WALL_T * 0.4
            top_far = min(WALL_H * 1.0, bh)
            if along == "x":
                v = [(sign * a0, -hw, 0), (sign * a0, hw, 0), (sign * a1, hw, 0), (sign * a1, -hw, 0),
                     (sign * a0, -hw, bh), (sign * a0, hw, bh), (sign * a1, hw, top_far), (sign * a1, -hw, top_far)]
            else:
                v = [(-hw, sign * a0, 0), (hw, sign * a0, 0), (hw, sign * a1, 0), (-hw, sign * a1, 0),
                     (-hw, sign * a0, bh), (hw, sign * a0, bh), (hw, sign * a1, top_far), (-hw, sign * a1, top_far)]
            f = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
            if sign < 0:
                f = [tuple(reversed(x)) for x in f]
            prism(f"buttress_{along}{sign}", v, f, M_FOOT())
    # ladder recess on the south face: dark strip + rungs
    if height_frac >= 0.6:
        box("ladder", 0, -TOWER_R + 0.005, 0.03, 0.09, 0.02, h * 0.8, M_SEAM())
        for k in range(5):
            box("rung", 0, -TOWER_R - 0.006, 0.06 + k * (h * 0.7 / 5), 0.07, 0.012, 0.012, M_GUN())
    if height_frac >= 0.98:
        cylinder("platform", 0, 0, h, TOWER_R + 0.02, PLATFORM_H, M_PLATE(), bevel=0.01)
        torus("ring", 0, 0, h + PLATFORM_H, TOWER_R + 0.005, 0.022, M_TEAM())
        cylinder("hatch", 0, 0, h + PLATFORM_H, TOWER_R * 0.55, 0.01, M_GUN_DK())
    if stage >= 1:
        import random
        rnd = random.Random(11)
        for k in range(5):
            ang = rnd.uniform(0, math.pi * 2)
            box("scar", TOWER_R * math.cos(ang), TOWER_R * math.sin(ang), rnd.uniform(0.05, h * 0.8), 0.05, 0.05, 0.06, M_SEAM())


def _spin(objs, facing):
    """Rotate turret parts about the tower axis: engine frame 0 = north, anticlockwise."""
    ang = math.radians(facing * 11.25)
    for o in objs:
        x, y, z = o.location
        o.location = (x * math.cos(ang) - y * math.sin(ang), x * math.sin(ang) + y * math.cos(ang), z)
        o.rotation_euler = (o.rotation_euler[0], o.rotation_euler[1], o.rotation_euler[2] + ang)


def build_turret(facing, recoil=False, stage=0, kind="vulc"):
    """Plug turret on the platform. vulc = twin-barrel Vulcan, rpg = four-tube
    rocket pod, sam = twin-missile rack angled skyward. facing = engine frame."""
    z0 = TOWER_H + PLATFORM_H
    objs = []
    body = M_GUN() if stage == 0 else M_GUN_DK()
    objs.append(box("mount", 0, 0, z0, 0.16, 0.16, 0.05, M_GUN_DK(), bevel=0.01))
    back = -0.03 if recoil else 0.0
    if kind == "vulc":
        objs.append(box("turret_body", 0, 0.02, z0 + 0.05, 0.20, 0.24, 0.10, body, bevel=0.015))
        objs.append(box("turret_top", 0, -0.02, z0 + 0.15, 0.14, 0.14, 0.03, M_GUN_DK(), bevel=0.01))
        for sx in (-0.045, 0.045):
            b = cylinder("barrel", 0, 0, 0, 0.022, 0.30, M_GUN_DK(), verts=16)
            b.rotation_euler = (math.radians(90), 0, 0)
            b.location = (sx, 0.29 + back, z0 + 0.10)
            objs.append(b)
            objs.append(box("brake", sx, 0.42 + back, z0 + 0.085, 0.05, 0.03, 0.03, M_GUN()))
    elif kind == "rpg":
        objs.append(box("turret_body", 0, 0.0, z0 + 0.05, 0.22, 0.20, 0.09, body, bevel=0.015))
        # a 2x2 pod of launch tubes, angled slightly up
        pod = box("pod", 0, 0.16 + back, z0 + 0.10, 0.18, 0.22, 0.12, M_GUN_DK(), bevel=0.012)
        pod.rotation_euler = (math.radians(-12), 0, 0)
        objs.append(pod)
        for sx in (-0.045, 0.045):
            for sz in (0.075, 0.13):
                t = cylinder("tube", 0, 0, 0, 0.026, 0.06, M_GUN(), verts=16)
                t.rotation_euler = (math.radians(90 - 12), 0, 0)
                t.location = (sx, 0.29 + back, z0 + sz + 0.04)
                objs.append(t)
    else:  # sam
        objs.append(box("turret_body", 0, 0.0, z0 + 0.05, 0.20, 0.18, 0.07, body, bevel=0.015))
        arm = box("rack_arm", 0, -0.02, z0 + 0.12, 0.06, 0.12, 0.12, M_GUN_DK(), bevel=0.008)
        objs.append(arm)
        for sx in (-0.07, 0.07):
            rail = box("rail", sx, 0.04 + back, z0 + 0.20, 0.03, 0.34, 0.03, M_GUN_DK())
            rail.rotation_euler = (math.radians(-35), 0, 0)
            objs.append(rail)
            m = cylinder("missile", 0, 0, 0, 0.028, 0.34, M_PLATE(), verts=16)
            m.rotation_euler = (math.radians(90 - 35), 0, 0)
            m.location = (sx, 0.08 + back, z0 + 0.27)
            objs.append(m)
            tip = cylinder("tip", 0, 0, 0, 0.028, 0.06, M_SEAM(), verts=16)
            tip.rotation_euler = (math.radians(90 - 35), 0, 0)
            tip.location = (sx, 0.08 + back + 0.18 * math.cos(math.radians(35)), z0 + 0.27 + 0.18 * math.sin(math.radians(35)))
            objs.append(tip)
    _spin(objs, facing)


# ---------------------------------------------------------------- render
def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def fresh(samples):
    clear_scene()
    setup_scene(samples)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = "renders"
    only = "all"
    samples = 48
    frames = None
    i = 0
    while i < len(argv):
        if argv[i] == "--out": out = argv[i + 1]; i += 2
        elif argv[i] == "--only": only = argv[i + 1]; i += 2
        elif argv[i] == "--samples": samples = int(argv[i + 1]); i += 2
        elif argv[i] == "--frames": frames = argv[i + 1].split(","); i += 2
        else: i += 1
    os.makedirs(out, exist_ok=True)

    def want(name):
        return frames is None or name in frames

    if only in ("calib", "all"):
        # one straight E-W run, one N-S, a corner, a lone piece, the bare tower and a Vulcan tower
        for joins, tag in ((10, "ew"), (5, "ns"), (6, "corner"), (0, "lone")):
            if want(f"calib_{tag}"):
                fresh(samples); build_wall(joins, 0); render(f"{out}/calib_{tag}.png")
        if want("calib_tower"):
            fresh(samples); build_tower(0); render(f"{out}/calib_tower.png")
        for kind in ("vulc", "rpg", "sam"):
            if want(f"calib_{kind}"):
                fresh(samples); build_tower(0); build_turret(4, kind=kind); render(f"{out}/calib_{kind}.png")
    if only in ("walls", "all"):
        for stage in range(3):
            for joins in range(16):
                name = f"wall_j{joins:02d}_d{stage}"
                if want(name):
                    fresh(samples); build_wall(joins, stage); render(f"{out}/{name}.png")
    if only in ("towers", "all"):
        for stage in range(2):
            fresh(samples); build_tower(stage); render(f"{out}/tower_d{stage}.png")
        for k in range(17):
            fresh(samples); build_tower(0, height_frac=(k + 1) / 17.0); render(f"{out}/tower_make_{k:02d}.png")
        for kind in ("vulc", "rpg", "sam"):
            for state in range(4):
                for facing in range(32):
                    name = f"{kind}_f{facing:02d}_s{state}"
                    if want(name):
                        fresh(samples)
                        build_tower(1 if state >= 2 else 0)
                        build_turret(facing, recoil=bool(state % 2), stage=1 if state >= 2 else 0, kind=kind)
                        render(f"{out}/{name}.png")


if __name__ == "__main__":
    main()
