#!/usr/bin/env python3
"""Blender headless: render a 3D component tower model into the frames the packer wants.

A generated model (Tripo / Hunyuan3D-2 / TRELLIS) arrives with its lighting baked into
its texture, which is what spoiled the gunboat: our sun then lights an image that is
already lit, and turning off the render shadow does nothing. A concrete tower is only
three materials, so this discards the imported texture entirely and paints the model
by geometry instead -- tan concrete, grey steel buttresses, and a pure-green platform
ring the launcher recolours per house. Lighting is then ours alone.

Camera and light match scripts/ts_blender_walls.py (and the mod's TS vehicles):
orthographic, from the south, 32 degrees above the ground, ground restored to 1:1
afterwards by the packer.

Run:
  blender -b -P scripts/ts_render_tower_glb.py -- <model.glb> <out_dir>
      [--spin DEG] [--pitch DEG] [--samples N] [--ring-frac F] [--foot-frac F]

  --spin        extra rotation about the vertical axis. Use 45 if the model's
                connectors came out on the diagonals instead of N/E/S/W.
  --pitch       stand the model up. Printable STLs often arrive lying down; the
                Cults GDI component tower needs 90.
  --ring-frac   height above which geometry is the platform ring (default 0.90)
  --foot-frac   radius beyond which geometry is a buttress (default 0.62 of the
                model's horizontal half-extent)

Writes the names scripts/ts_pack_towers.py reads as a body directory:
  frame-0000.png  healthy      frame-0001.png  damaged
plus frame-0002.. as construction stages if --make is given.
License: GPL v3.
"""
import math, os, sys
import bpy
from mathutils import Vector

ELEV = 32.0
LIGHT_DIR = Vector((-0.5, 0.6, 0.75)).normalized()
SUN_STRENGTH = 3.2
AMBIENT = 0.42
RENDER_PX = 1024          # square; the packer scales the body to its own target width


def argv():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    opt = {"model": a[0] if a else "", "out": a[1] if len(a) > 1 else "renders",
           "spin": 0.0, "pitch": 0.0, "samples": 64, "ring": 0.88, "foot": 0.80, "make": 0}
    i = 2
    while i < len(a):
        k = a[i].lstrip("-")
        if k in ("spin", "pitch", "ring-frac", "foot-frac"):
            opt({"ring-frac": "ring", "foot-frac": "foot"}.get(k, k)) if False else None
            opt[{"ring-frac": "ring", "foot-frac": "foot"}.get(k, k)] = float(a[i + 1]); i += 2
        elif k in ("samples", "make"):
            opt[k] = int(a[i + 1]); i += 2
        else:
            i += 1
    return opt


def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def mat(name, rgb, roughness=0.85, emission=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    lin = tuple(srgb_to_linear(c) for c in rgb) + (1.0,)
    b.inputs["Base Color"].default_value = lin
    b.inputs["Roughness"].default_value = roughness
    if emission:
        b.inputs["Emission Color"].default_value = lin
        b.inputs["Emission Strength"].default_value = emission
    return m


def setup(samples):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = False
    sc.render.resolution_x = sc.render.resolution_y = RENDER_PX
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Standard"
    cam_d = bpy.data.cameras.new("cam"); cam_d.type = "ORTHO"
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
    # the default world colour is near-black: setting strength alone leaves everything
    # facing away from the sun rendering black
    bg.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    bg.inputs["Strength"].default_value = AMBIENT
    sc.world = w
    return cam


def import_model(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".glb" or ext == ".gltf":
        bpy.ops.import_scene.gltf(filepath=path)
    elif ext == ".obj":
        bpy.ops.wm.obj_import(filepath=path)
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=path)
    elif ext == ".stl":
        try:
            bpy.ops.wm.stl_import(filepath=path)      # Blender 4.1+
        except AttributeError:
            bpy.ops.import_mesh.stl(filepath=path)    # Blender 4.0
    else:
        raise SystemExit(f"unsupported model format: {ext}")
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not objs:
        raise SystemExit("no mesh in the imported model")
    return objs


def normalise(objs, spin, pitch):
    """Sit the model on z=0, centre it on the origin, unit height, spin as asked."""
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    bpy.ops.object.make_single_user(object=True, obdata=True)   # imported meshes arrive shared
    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (math.radians(pitch), 0.0, math.radians(spin))
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    lo = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
    hi = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    size = hi - lo
    s = 1.0 / max(size.z, 1e-6)
    obj.scale = (s, s, s)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    lo = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
    hi = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    obj.location = (obj.location.x - (lo.x + hi.x) / 2, obj.location.y - (lo.y + hi.y) / 2,
                    obj.location.z - lo.z)
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    return obj


def repaint(obj, ring_frac, foot_frac):
    """Throw the baked texture away and paint by geometry: ring on top, buttresses out
    at the rim, concrete everywhere else."""
    obj.data.materials.clear()
    # colours sampled from GTCTWR / GTWALL (UNITTEM.PAL); lifted so the LIT faces
    # land on the sampled values rather than under them
    lift = 0.78
    concrete = mat("tan_concrete", tuple(min(255, int(c / lift)) for c in (157, 141, 89)), 0.9)
    steel = mat("grey_steel", tuple(min(255, int(c / lift)) for c in (129, 129, 129)), 0.85)
    ring = mat("team_ring", (0, 200, 0), 0.7, emission=0.25)
    deck = mat("platform", tuple(min(255, int(c / lift)) for c in (113, 113, 137)), 0.6)
    for m in (concrete, steel, ring, deck):
        obj.data.materials.append(m)
    me = obj.data
    xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]
    half = max(max(map(abs, xs)), max(map(abs, ys))) or 1.0
    zmax = max(v.co.z for v in me.vertices) or 1.0
    # the platform's own radius, measured from the geometry sitting above ring_frac,
    # so the team band can be limited to its rim instead of catching the bolt sockets
    top_r = max([math.hypot(v.co.x, v.co.y) / half for v in me.vertices
                 if v.co.z >= ring_frac * zmax] or [1.0])
    for poly in me.polygons:
        c = poly.center
        r = math.hypot(c.x, c.y) / half
        upward = abs(poly.normal.z) > 0.5
        # how close this face's bearing is to a cardinal: the connectors are the only
        # geometry that reaches out along N/E/S/W, so a radius test alone would paint
        # the whole octagonal body as steel
        ang = math.degrees(math.atan2(c.y, c.x)) % 90.0
        cardinal = min(ang, 90.0 - ang) <= 26.0
        if c.z >= ring_frac * zmax and not upward and r >= 0.72 * top_r:
            poly.material_index = 2          # the platform's rim: the team-colour band
        elif c.z >= ring_frac * zmax:
            poly.material_index = 3          # the platform's decking and its bolt sockets
        elif r >= foot_frac and cardinal:
            poly.material_index = 1          # the four connectors: the wall's own grey
        else:
            poly.material_index = 0          # tan concrete body
    me.update()


def fit_camera(cam, obj, margin=1.15):
    """Frame the model squarely: centre it horizontally, and centre it along the
    camera's own up axis so nothing is cropped."""
    bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    e = math.radians(ELEV)
    us = [v.x for v in bb]
    vs = [v.y * math.sin(e) + v.z * math.cos(e) for v in bb]
    span = max(max(us) - min(us), max(vs) - min(vs))
    cam.data.ortho_scale = span * margin
    cam.location.x += (max(us) + min(us)) / 2
    up = Vector((0.0, math.cos(math.radians(90.0 - ELEV)), math.sin(math.radians(90.0 - ELEV))))
    cam_v = cam.location.y * math.sin(e) + cam.location.z * math.cos(e)
    cam.location += up * ((max(vs) + min(vs)) / 2 - cam_v)
    return span


def damage(obj, seed=7):
    """Chip the silhouette: a displace on a low-detail noise, plus a downward tilt."""
    tex = bpy.data.textures.new("chip", type="CLOUDS")
    tex.noise_scale = 0.18
    m = obj.modifiers.new("chip", "DISPLACE")
    m.texture = tex
    m.strength = -0.06
    m.mid_level = 0.35


def render(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def main():
    o = argv()
    if not o["model"]:
        raise SystemExit("usage: blender -b -P scripts/ts_render_tower_glb.py -- <model.glb> <out_dir> [--spin 45]")
    os.makedirs(o["out"], exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    cam = setup(o["samples"])
    obj = normalise(import_model(o["model"]), o["spin"], o["pitch"])
    repaint(obj, o["ring"], o["foot"])
    fit_camera(cam, obj)
    render(f"{o['out']}/frame-0000.png")
    damage(obj)
    render(f"{o['out']}/frame-0001.png")
    print(f"wrote {o['out']}/frame-0000.png and frame-0001.png")
    print("next: TS_ART_DIR=<parent> TS_BODY_DIR=<dirname> python3 scripts/ts_pack_towers.py")


if __name__ == "__main__":
    main()
