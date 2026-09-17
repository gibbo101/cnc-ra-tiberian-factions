#!/usr/bin/env python3
"""Blender: model and render the TS component tower with its connectors on N/E/S/W.

TS's GACTWR is drawn for an isometric grid, so its four wall connectors point along
the screen diagonals. This mod's grid needs them on north, east, south and west. The
tower is therefore rebuilt as geometry and rendered at the mod's camera, keeping TS's
own design rather than inventing one:

  - a flared tan concrete body, narrow at the platform and splayed at the base, with
    a dark recess running down each diagonal between the legs
  - four wall connectors on the cardinals. These are WALL-ENDS: TS paints them in the
    wall's own greys (face 129, cap 161) because they are a stub of wall, which is why
    a run meets them seamlessly. Ours are the same cross-section as ts_blender_walls.py
  - a service ladder recessed into the south face
  - a bluish-grey platform on top with four bolt sockets, ringed by the team colour

Colours are sampled from GTCTWR/GTWALL decoded with UNITTEM.PAL.

Camera: orthographic from the south at 32 degrees, the mod's TS vehicle camera. At
that elevation a flat circle projects to a 0.53 ellipse, which is TS's own 2:1 ground
squash, so the render needs no re-projection and sits in the same space as every other
TS building the mod ships. Output therefore feeds ts_pack_towers.py directly as a
body directory, NOT ts_pack_blender.py (which is for the grid-aligned walls).

Run:
  blender -b -P scripts/ts_blender_tower.py -- --out <dir> [--samples N] [--px N]
Writes frame-0000.png (healthy) and frame-0001.png (damaged); point the packer at it:
  TS_ART_DIR=<parent> TS_BODY_DIR=<dirname> python3 scripts/ts_pack_towers.py
License: GPL v3.
"""
import math, os, sys
import bpy, bmesh
from mathutils import Vector

ELEV = 32.0
LIGHT_DIR = Vector((-0.5, 0.6, 0.75)).normalized()
SUN_STRENGTH = 3.0
AMBIENT = 0.55

# Proportions in cells (1.0 = one 128 px cell), measured off GTCTWR (34 x 33 px):
# the platform's green ring spans 19 of the 34 px width, so the platform is a little
# over half the body's width; the body stands about 0.47 of the width tall once the
# round base's own iso depth is taken out of the sprite's 33 px height.
BASE_R, TOP_R = 0.40, 0.24        # body radius at the ground and at the platform
BODY_H = 0.36                     # body height
PLAT_R, PLAT_H = 0.215, 0.035     # platform disc: ~0.56 of the body's width across
RING_W = 0.040                    # team-colour ring around the platform rim
CONN_W, CONN_H, CONN_OUT = 0.15, 0.26, 0.56   # connector width, height, outer reach
CONN_Z = 0.055                    # connector sits just off the ground, like the wall
CAP_H = 0.030                     # the wall's lighter cap along the connector top
GROOVE_W, GROOVE_D = 0.055, 0.035 # the recesses between the legs: grooves, not holes
LADDER_W = 0.070

# sampled from the sprites
C_TAN       = (157, 141, 89)
C_TAN_LIGHT = (190, 165, 105)
C_TAN_DARK  = (121, 105, 64)
C_RECESS    = (74, 68, 56)
C_WALL      = (129, 129, 129)     # connector face = the wall's own face grey
C_WALL_CAP  = (161, 161, 161)     # connector cap  = the wall's own cap grey
C_PLATFORM  = (113, 113, 137)
C_BOLT      = (40, 40, 52)
C_TEAM      = (0, 200, 0)


def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


_M = {}


# The sampled colours are what TS's LIT faces look like, so the albedo has to sit
# above them or the render comes out muddy: divide by roughly the shade a mid-facing
# surface receives here (the wall script does the same, per face).
ALBEDO_LIFT = 0.78


def mat(name, rgb, rough=0.88, emission=0.0):
    if name in _M:
        return _M[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    lin = tuple(min(1.0, srgb_to_linear(min(255, c / ALBEDO_LIFT))) for c in rgb) + (1.0,)
    b.inputs["Base Color"].default_value = lin
    b.inputs["Roughness"].default_value = rough
    if emission:
        b.inputs["Emission Color"].default_value = lin
        b.inputs["Emission Strength"].default_value = emission
    _M[name] = m
    return m


def setup(samples, px):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = False
    sc.render.resolution_x = sc.render.resolution_y = px
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Standard"
    cam_d = bpy.data.cameras.new("cam"); cam_d.type = "ORTHO"; cam_d.ortho_scale = 1.5
    cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam)
    e = math.radians(ELEV)
    cam.location = (0.0, -20.0 * math.cos(e), 20.0 * math.sin(e))
    cam.rotation_euler = (math.radians(90.0 - ELEV), 0.0, 0.0)
    sc.camera = cam
    sun_d = bpy.data.lights.new("sun", type="SUN"); sun_d.energy = SUN_STRENGTH
    sun = bpy.data.objects.new("sun", sun_d); sc.collection.objects.link(sun)
    sun.rotation_euler = (-LIGHT_DIR).to_track_quat("-Z", "Y").to_euler()
    w = bpy.data.worlds.new("w"); w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    # the default world colour is near-black, so setting strength alone leaves the
    # scene lit by the sun only and everything facing away renders black
    bg.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    bg.inputs["Strength"].default_value = AMBIENT
    sc.world = w
    return cam


def link(o):
    bpy.context.scene.collection.objects.link(o)
    return o


def box(name, cx, cy, cz, sx, sy, sz, material, bevel=0.0):
    # the size is baked into the mesh rather than left on the object: a bevel on a
    # non-uniformly scaled object produces degenerate geometry that renders black
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector((sx, sy, sz)), verts=bm.verts)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me)
    o.location = (cx, cy, cz + sz / 2.0)
    o.data.materials.append(material)
    if bevel:
        m = o.modifiers.new("b", "BEVEL"); m.width = bevel; m.segments = 2; m.limit_method = "ANGLE"
    return link(o)


def cone(name, cz, r1, r2, h, material, verts=40, smooth=True):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=verts,
                                            radius1=r1, radius2=r2, depth=h)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.location = (0, 0, cz + h / 2.0)
    o.data.materials.append(material)
    if smooth:
        for p in o.data.polygons:
            p.use_smooth = True
    return link(o)


def ring(name, cz, r_out, r_in, h, material, verts=48):
    """A flat annulus: the team-colour band round the platform rim."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r_out, radius2=r_out, depth=h)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.location = (0, 0, cz + h / 2.0)
    o.data.materials.append(material)
    for p in o.data.polygons:
        p.use_smooth = True
    link(o)
    inner = cone(name + "_cut", cz - 0.01, r_in, r_in, h + 0.02, material, verts=verts)
    m = o.modifiers.new("cut", "BOOLEAN"); m.operation = "DIFFERENCE"; m.object = inner; m.solver = "EXACT"
    inner.hide_render = True
    return o


def build(damaged=False):
    tan = mat("tan", C_TAN_DARK if damaged else C_TAN)
    tan_l = mat("tan_l", C_TAN_LIGHT, 0.8)
    recess = mat("recess", C_RECESS, 0.95)
    wall = mat("wall", C_WALL, 0.9)
    wall_cap = mat("wall_cap", C_WALL_CAP, 0.85)
    plat = mat("plat", C_PLATFORM, 0.6)
    bolt = mat("bolt", C_BOLT, 0.9)
    team = mat("team", C_TEAM, 0.7, emission=0.25)

    # flared body, plus a light collar where it meets the platform
    body = cone("body", 0.0, BASE_R, TOP_R, BODY_H, tan, verts=16, smooth=False)
    cone("collar", BODY_H - 0.03, TOP_R + 0.012, TOP_R + 0.012, 0.03, tan_l)

    # dark recesses down each diagonal, cut into the body
    for k in range(4):
        a = math.radians(45 + 90 * k)
        gx, gy = math.sin(a) * (BASE_R - GROOVE_D * 0.4), math.cos(a) * (BASE_R - GROOVE_D * 0.4)
        g = box(f"groove{k}", gx, gy, -0.01, GROOVE_W, GROOVE_W, BODY_H + 0.02, recess)
        g.rotation_euler = (0, 0, a)
        g.hide_render = True          # a cutter, not geometry: without this it renders as a dark block
        m = body.modifiers.new(f"g{k}", "BOOLEAN"); m.operation = "DIFFERENCE"; m.object = g; m.solver = "EXACT"

    # four wall-end connectors on the cardinals: the wall's own cross-section
    for k in range(4):
        a = math.radians(90 * k)
        mid = (TOP_R + CONN_OUT) / 2.0
        cx, cy = math.sin(a) * mid, math.cos(a) * mid
        length = CONN_OUT - TOP_R + 0.10
        sx, sy = (CONN_W, length) if k % 2 == 0 else (length, CONN_W)
        # the cap SITS ON the shaft rather than overlapping it: coplanar top faces
        # z-fight and render as black patches
        box(f"conn{k}", cx, cy, CONN_Z, sx, sy, CONN_H - CAP_H, wall, bevel=0.010)
        box(f"conncap{k}", cx, cy, CONN_Z + CONN_H - CAP_H, sx, sy, CAP_H, wall_cap)

    # service ladder, recessed into the south face
    channel = box("ladder_cut", 0, -(BASE_R * 0.95), -0.01, LADDER_W * 1.8, 0.18, BODY_H + 0.02, recess)
    channel.hide_render = True
    mc = body.modifiers.new("ladder", "BOOLEAN"); mc.operation = "DIFFERENCE"
    mc.object = channel; mc.solver = "EXACT"
    box("ladder_back", 0, -(BASE_R * 0.62), 0.0, LADDER_W * 1.8, 0.03, BODY_H - 0.02, recess)
    for i in range(6):
        box(f"rung{i}", 0, -(BASE_R * 0.66), 0.03 + i * (BODY_H - 0.08) / 6.0,
            LADDER_W * 1.4, 0.02, 0.013, wall_cap)

    # platform, bolts, team ring
    cone("platform", BODY_H, PLAT_R, PLAT_R, PLAT_H, plat)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cone_o = cone(f"bolt{sx}{sy}", BODY_H + PLAT_H - 0.006, 0.032, 0.032, 0.01, bolt, verts=12)
            cone_o.location = (sx * 0.12, sy * 0.10, BODY_H + PLAT_H - 0.001)
    ring("team_ring", BODY_H + PLAT_H * 0.35, PLAT_R + RING_W, PLAT_R - 0.005, PLAT_H * 0.9, team)

    if damaged:
        tex = bpy.data.textures.new("chip", type="CLOUDS"); tex.noise_scale = 0.13
        for o in list(bpy.context.scene.objects):
            if o.type == "MESH" and o.name.startswith(("body", "conn")):
                m = o.modifiers.new("chip", "DISPLACE")
                m.texture = tex; m.strength = -0.035; m.mid_level = 0.42


def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def main():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out, samples, px = "renders", 96, 900
    i = 0
    while i < len(a):
        if a[i] == "--out": out = a[i + 1]; i += 2
        elif a[i] == "--samples": samples = int(a[i + 1]); i += 2
        elif a[i] == "--px": px = int(a[i + 1]); i += 2
        else: i += 1
    os.makedirs(out, exist_ok=True)
    for idx, dmg in ((0, False), (1, True)):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        _M.clear()
        setup(samples, px)
        build(damaged=dmg)
        render(f"{out}/frame-{idx:04d}.png")
    print(f"wrote {out}/frame-0000.png and frame-0001.png")


if __name__ == "__main__":
    main()
