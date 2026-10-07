"""
npackage.py - the package for a voxel unit new to the mod: README.txt, frames/, previews/, muzzle.txt, src/ (runs on its
own), <pkg>.zip, and the 3D model in <pkg>-3d/ with its own README, zipped as <pkg>-3d.zip.  The README text comes
from the spec's README dict (see bggyspec.py) laid into the template below.

    python3 npackage.py SPEC PKG REF_DIR UNIT_DIR
"""
import os, sys, re, shutil, zipfile, importlib, subprocess, json
import numpy as np
from PIL import Image

VOX = os.path.dirname(os.path.abspath(__file__))
SHARED = ['vxl.py', 'vxlunit.py', 'voxrender.py', 'tsnormals.py', 'tsvox.py', 'rc.py', 'rcrender.py', 'hd.py', 'walls2.py',
          'wnoise.py', 'frameio.py', 'vexport.py', 'rcexport.py', 'export3d.py', 'glbcheck.py', 'ndeliver.py',
          'npackage.py', 'vplace.py', 'nvox.py']

TEMPLATE = """{title} (TS [{ts_name}]) in HD for Tiberian Factions: {mod_name}
{rule}

{frames}
{muzzle_line}{previews}
{pkg3d}/   the 3D model, in its own zip ({pkg3d}.zip) next to this folder:
            {glb_name}   the model in TS's own colours, with the mod's camera
src/        the model builder, the renderer and the checks (see Rebuilding below)


What it is
----------
{what}

Look
----
{look}
{common_look}


Shadow
------
{shadow}
{extra}

3D model ({pkg3d}/)
{rule3d}
- {glb_nodes}
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.  The unit faces east (the mod's facing 24).
- {glb_mesh}
- Camera "camera_mod": orthographic, the mod's camera, framing the canvas exactly (checked by drawing the mesh
  through it over {glb_ref}: overlap {glb_iou}).
- The file passes Khronos's glTF validator with no errors or warnings{glb_infos}.
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
{judgement_head}{judgement}

Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folder is (TS_HANDOFF: the
folder holding {folder}/ and examples/).
{shared_lines}
{src}
"""

WHAT_VOXEL = """One 3D model rebuilt straight from TS's own voxels ({vxl}), drawn the way the HD buildings and the
GDI units are.
- Shape: every voxel's step is TS's.  Each voxel section's voxels are merged into boxes and cut at 45 degrees along
  the solid's convex edges (so its corners read as pressed plate); where two boxes of a section meet, nothing
  shows.  The shading rounds every edge that faces the air, and carries TS's own voxel normals as a layer of detail
  (the bevels, seams, vents and slots TS shades into its voxels).
- Colours: TS's own.  Every surface takes the palette colour (UNITTEM.PAL) of the voxels just inside it; TS's single
  voxels of darker or lighter speckle are held near the colour round them, while its near-black and near-white
  voxels (slots, hatches, highlights) keep their colour.  House colour is pure green 0,214,0 x (1 + 1.1 grain)
  wherever TS's remap voxels are, with TS's remap shades kept as darker and lighter seams; the -trim masks cover
  exactly that.
It is new to the mod, so there are no in-mod frames to match: the previews put TS's own voxels, drawn as they are
(every voxel a square in its palette colour, lit by its own TS normal, through the same camera), beside the HD frames.
The HD frames cover those with a silhouette overlap of {iou} (src/ndeliver.py check)."""

SHARED_VOXEL = """  vxlunit.py, tsnormals.py   a voxel section as boxes, its convex edges, TS's colours and normals across its faces
  voxrender.py           one frame of a voxel unit with the buildings' look
  rc.py, rcrender.py     the ray caster and the buildings' look for models made of convex parts
  tsvox.py               TS's voxels drawn as they are (the previews' left column)
  vexport.py, rcexport.py   the .glb;  glbcheck.py  draws the .glb through its camera to check it
  ndeliver.py            renders, previews and checks a unit from its spec;  npackage.py  this package"""
SHARED_HD = """  rc.py, rcrender.py     the ray caster and the buildings' look for models made of convex parts
  tsvox.py               TS's voxels drawn as they are (the previews' left column)
  vexport.py, rcexport.py   the .glb;  glbcheck.py  draws the .glb through its camera to check it
  ndeliver.py            renders, previews and checks a unit from its spec;  npackage.py  this package
  (vxlunit.py, tsnormals.py and voxrender.py, the voxel builder the GDI units used, come with the shared files; this
  unit's HD model doesn't use them)"""

COMMON_GROUND = """- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides
  facing the camera as on the other units.  The game draws this canvas at two thirds (8 canvas px per classic
  pixel), so the outline, the shadow's blur and the contact shadow are 1.5 times as wide on the canvas.
- Colours brightened by 1.25 from TS's palette so its ochre comes out as the HD buildings' ochre; whites held at white
  paint; grime rising from the ground on the lower hull."""
COMMON_AIR = """- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides
  facing the camera as on the other units.  The game draws this canvas at two thirds (8 canvas px per classic
  pixel), so the outline is 1.5 times as wide on the canvas.
- Colours brightened by 1.25 from TS's palette so its ochre comes out as the HD buildings' ochre; whites held at white
  paint.  It flies, so none of the ground's grime or occlusion that the ground units carry low on the hull."""

README3D = """{title} (TS [{ts_name}]): the 3D model ({mod_name})
{rule}

{glb_name}   {glb_what}
{glb_nodes_long}
Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (128 px in the game; 192 px on the mod's 384 canvas).
Origin: the unit's position on the ground.  The unit faces east (the mod's facing 24); to draw facing f (counter-
clockwise from north, 32), turn unit_facing_east about y by (f - 24) x 11.25 degrees.

Camera "camera_mod": orthographic, 32 degrees above the ground, looking north, framing the {canvas} canvas exactly
(xmag {xmag:.4f}, ymag {ymag:.4f} cells): the frames' camera.
Drawn through it the mesh covers {glb_ref} with an overlap of {glb_iou}.
Other suggested angles: TS's own view is orthographic, 30 degrees above the ground, looking north-west (with the
unit's facing turned to match).

{glb_mesh3d}
Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour, pure green 0,214,0
in COLOR_0).
The file passes Khronos's glTF validator with no errors or warnings{glb_infos}.
"""


def zipdir(folder, zpath):
    if os.path.exists(zpath):
        os.remove(zpath)
    base = os.path.dirname(folder)
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(folder):
            dirs[:] = sorted(d for d in dirs if d != '__pycache__')
            for f in sorted(files):
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, base))


def oxipng_all(folder):
    import oxipng
    before = after = 0
    for root, _, files in os.walk(folder):
        for f in files:
            if f.endswith('.png'):
                p = os.path.join(root, f)
                a0 = np.array(Image.open(p)); m0 = Image.open(p).mode
                before += os.path.getsize(p)
                oxipng.optimize(p, level=3, strip=oxipng.StripChunks.safe(), bit_depth_reduction=False,
                                color_type_reduction=False, palette_reduction=False, grayscale_reduction=False)
                assert Image.open(p).mode == m0 and np.array_equal(np.array(Image.open(p)), a0), p
                after += os.path.getsize(p)
    return before, after


def package_src(spec, pkg, unit_dir):
    S = pkg + '/src'
    if os.path.exists(S):
        shutil.rmtree(S)
    os.makedirs(S)
    for f in SHARED + getattr(spec, 'SHARED_EXTRA', []):
        shutil.copy(os.path.join(VOX, f), S)
    for f in spec.SRC:
        shutil.copy(os.path.join(unit_dir, f), S)
    open(os.path.join(S, 'paths.py'), 'w').write(
        '"""where the scripts find things: this folder and the hand-off folder (TS\'s voxels, the examples).  Set\n'
        'TS_HANDOFF to the hand-off\'s root folder (the one holding %s/ and examples/)."""\n'
        'import os\n'
        'HERE = os.path.dirname(os.path.abspath(__file__))\n'
        "HANDOFF = os.environ.get('TS_HANDOFF', os.path.join(HERE, '..', '..', 'ts-nod-units-hd-handoff'))\n"
        "EA_UNITS = os.environ.get('EA_UNITS', os.path.join(HERE, '..', '..', 'RA + TD HD Units'))\n" % spec.FOLDER)
    left = []
    for f in os.listdir(S):
        s = open(os.path.join(S, f)).read()
        if f != 'npackage.py' and '/home/' + 'claude' in s:
            left.append(f)
    return left


def selftest_src(spec, pkg, handoff, k=24):
    """copy src/ somewhere else, put only the hand-off on the path, draw frame k at full quality and compare it with the
    delivered frame."""
    import tempfile
    tmp = tempfile.mkdtemp(prefix='srctest-')
    shutil.copytree(pkg + '/src', tmp + '/src')
    env = dict(os.environ, TS_HANDOFF=handoff, PYTHONPATH='')
    args = getattr(spec, 'RENDER_ARGS', [spec.RENDER_SCRIPT if hasattr(spec, 'RENDER_SCRIPT') else 'nvox.py'])
    if args == ['nvox.py']:
        args = ['nvox.py', spec.__name__]
    r = subprocess.run([sys.executable] + list(args) + ['frames', str(k), '4', tmp + '/out'], cwd=tmp + '/src',
                       env=env, capture_output=True, text=True)
    if r.returncode:
        return 'FAILED: ' + r.stderr[-800:]
    a = np.array(Image.open('%s/out/%s-%04d.png' % (tmp, spec.NAME, k))).astype(int)
    b = np.array(Image.open('%s/frames/%s-%04d.png' % (pkg, spec.NAME, k))).astype(int)
    return 'frame %d redrawn from a copy of src/: max difference %d' % (k, np.abs(a - b).max())


def build(spec, pkg, ref_dir, unit_dir, iou, glb_iou, glb_infos):
    R = dict(spec.README)
    name = os.path.basename(pkg.rstrip('/'))
    R.update(rule='=' * len('%s (TS [%s]) in HD for Tiberian Factions: %s' % (R['title'], R['ts_name'], R['mod_name'])),
             pkg3d=name + '-3d', glb_name=spec.GLB_NAME, iou=iou, glb_iou=glb_iou, glb_infos=glb_infos,
             folder=spec.FOLDER, rule3d='-' * len('3D model (%s-3d/)' % name))
    R.setdefault('common_look', COMMON_AIR if getattr(spec, 'AIRCRAFT', False) else COMMON_GROUND)
    R.setdefault('what', WHAT_VOXEL)
    R.setdefault('glb_mesh', "The meshes are exact (each voxel section's boxes), subdivided so the vertex colours carry TS's colours.")
    R.setdefault('muzzle_line', '')
    hd_model = 'hdv.py' in getattr(spec, 'SHARED_EXTRA', [])
    R.setdefault('judgement_head', '' if hd_model else
                 "- Built straight from TS's voxels (above), not hand-modelled: nothing is interpreted, every detail is where TS\n"
                 "  has it.\n"
                 "- TS's single-voxel speckle held near the colour round it (its paint is speckled voxel by voxel).\n")
    R.setdefault('shared_lines', SHARED_HD if hd_model else SHARED_VOXEL)
    R.setdefault('extra', '')
    R.setdefault('judgement', '')
    R.setdefault('glb_ref', 'frame 24')
    R['what'] = R['what'].format(**R)
    open(pkg + '/README.txt', 'w').write(TEMPLATE.format(**R))
    left = package_src(spec, pkg, unit_dir)
    return left


if __name__ == '__main__':
    sys.path.insert(0, os.getcwd())
    spec = importlib.import_module(sys.argv[1])
    pkg, ref_dir, unit_dir = sys.argv[2], sys.argv[3], sys.argv[4]
    import ndeliver, glbcheck
    from paths import HANDOFF
    name = os.path.basename(pkg.rstrip('/'))
    pkg3d = pkg.rstrip('/') + '-3d'
    # the checks the README quotes
    bad, ious = ndeliver.check(spec, pkg, ref_dir)
    assert not bad, bad
    iou = '%.2f' % np.mean(ious)
    os.makedirs(pkg3d, exist_ok=True)
    glb = os.path.join(pkg3d, spec.GLB_NAME)
    spec.GLB(glb)
    js, binb = glbcheck.load_glb(glb)
    W, H = spec.CANVAS
    meshes = glbcheck.world_meshes(js, binb)
    skip = tuple(getattr(spec, 'GLB_CHECK_SKIP', ()))
    if skip:
        meshes = [mm for mm in meshes if not mm[0].startswith(skip)]
    img, m = glbcheck.raster(meshes, glbcheck.camera(js), W, H)
    k = spec.GLB_FRAMES[0]
    ref = np.zeros((H, W), bool)
    for kk in getattr(spec, 'GLB_REF_LAYERS', [k]):          # a turret's frames laid over the hull's
        ref |= np.array(Image.open('%s/frames/%s-%04d.png' % (pkg, spec.NAME, kk)))[..., 3] > 250
    glb_iou = '%.3f' % ((m & ref).sum() / (m | ref).sum())
    # Khronos's glTF validator (npm gltf-validator) through a small node script: VALIDATOR=path/to/validate.js
    vjs = os.environ.get('VALIDATOR', os.path.join(VOX, '..', 'tools', 'validate.js'))
    val = subprocess.run(['node', vjs, glb], capture_output=True, text=True)
    rep = json.loads(val.stdout)
    assert rep['errors'] == 0 and rep['warnings'] == 0, rep
    glb_infos = '' if not rep['infos'] else (' (its note is the empty marker node)' if rep['infos'] == 1 else
                                             ' (its %d notes are the empty marker nodes)' % rep['infos'])
    if hasattr(spec, 'muzzle_text'):
        open(pkg + '/muzzle.txt', 'w').write(spec.muzzle_text())
    left = build(spec, pkg, ref_dir, unit_dir, iou, glb_iou, glb_infos)
    assert not left, left
    R = dict(spec.README)
    cam = js['cameras'][0]['orthographic']
    R.update(rule='=' * len('%s (TS [%s]): the 3D model (%s)' % (R['title'], R['ts_name'], R['mod_name'])),
             glb_name=spec.GLB_NAME, glb_iou=glb_iou, glb_infos=glb_infos, canvas='%d x %d' % (W, H),
             xmag=cam['xmag'], ymag=cam['ymag'])
    R.setdefault('glb_what', "the model rebuilt straight from TS's %s, in TS's own colours, with the mod's camera." % R['vxl'])
    R.setdefault('glb_ref', 'frame 24')
    R.setdefault('glb_mesh3d', "The meshes are exact (each voxel section's boxes, cut at 45 degrees along the solid's convex edges), subdivided so the\nvertex colours carry TS's colours.")
    open(pkg3d + '/README.txt', 'w').write(README3D.format(**R))
    print(selftest_src(spec, pkg, HANDOFF, spec.GLB_FRAMES[0]))
    b, a = oxipng_all(pkg)
    print('pngs %.1f MB -> %.1f MB (lossless)' % (b / 1e6, a / 1e6))
    zipdir(pkg, pkg.rstrip('/') + '.zip'); zipdir(pkg3d, pkg3d + '.zip')
    for z in (pkg.rstrip('/') + '.zip', pkg3d + '.zip'):
        zz = zipfile.ZipFile(z)
        print(z, '%.1f MB' % (os.path.getsize(z) / 1e6), len(zz.namelist()), 'files', 'ok' if zz.testzip() is None else 'BAD')
