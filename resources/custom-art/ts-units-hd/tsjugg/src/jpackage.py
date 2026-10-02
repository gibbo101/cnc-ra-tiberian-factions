"""
jpackage.py - the Juggernaut's package after the frames (jfinal.py), previews (jpreviews.py, jshapecheck.py), models
(jexport.py) and barrel tips (jtips.py) are made: the READMEs, src/ with relative paths (checked by rendering from a
copy), smaller PNGs, and the two zips (ts-jugg-hd.zip, ts-jugg-hd-3d.zip).

    python3 jpackage.py PKG          (PKG = .../ts-jugg-hd; its 3D folder ts-jugg-hd-3d sits beside it)
"""
import json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.abspath(sys.argv[1])
D3 = PKG + '-3d'
VOX = '/home/claude/units/work/vox/'
RENDERER = HANDOFF + '/renderer/'

SRC = ['jugg.py', 'jrender.py', 'jdeprender.py', 'jdeployed.py', 'jdeploy.py', 'jbase.py', 'jbase2.py', 'jfit.py',
       'jfitcabin.py', 'jfithatch.py', 'jfitwalk.py', 'jfitwalker.py', 'jbarfit.py', 'jmap.py', 'jclass.py', 'jpal.py',
       'jfinal.py', 'jpreviews.py', 'jexport.py', 'jtips.py', 'jcheck.py', 'jshapecheck.py', 'jpackage.py', 'paths.py',
       'fit_walker_e.json', 'fit_walk_e.json', 'fit_cabin_a.json', 'fit_hatch_a.json', 'fit_base2_a.json',
       'fit_bar_rest.json', 'fit_bar_aim.json']
SHARED = [VOX + f for f in ('rc.py', 'rcrender.py', 'rcexport.py', 'frameio.py', 'glbcheck.py', 'vexport.py',
                            'voxrender.py', 'vxlunit.py', 'tsnormals.py', 'ra2normals.py')]
REN = [RENDERER + f for f in ('hd.py', 'walls2.py', 'wnoise.py', 'export3d.py', 'vxl.py')]

# the few paths that are not the hand-off's: made relative to the script's own folder
FIXES = [("HERE = os.path.dirname(os.path.abspath(__file__)) + '/'", "HERE = os.path.dirname(os.path.abspath(__file__)) + '/'"),
         ("WALK = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fit_walk_e.json')",
          "WALK = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fit_walk_e.json')"),
         ("TITAN = os.environ.get('TITAN_FRAMES', os.path.join(HANDOFF, '..', 'ts-titan-hd', 'frames')) + '/tstitn-%04d.png'      # the HD Titan's frames, for scale.png",
          "TITAN = os.environ.get('TITAN_FRAMES', os.path.join(HANDOFF, '..', 'ts-titan-hd', 'frames')) + "
          "'/tstitn-%04d.png'      # the HD Titan's frames, for scale.png")]


def package_src():
    Sd = PKG + '/src'
    shutil.rmtree(Sd, ignore_errors=True); os.makedirs(Sd)
    for f in SRC:
        shutil.copy(os.path.join(HERE, f), Sd)
    for f in SHARED + REN:
        shutil.copy(f, Sd)
    left = []
    for f in sorted(os.listdir(Sd)):
        if not f.endswith('.py') or f == 'paths.py':
            continue
        p = os.path.join(Sd, f); s = open(p).read()
        s = re.sub(r"^[ \t]*sys\.path\.insert\(0, ['\"]/home/claude/units/[^'\"]*['\"]\)\n", '', s, flags=re.M)
        for a, b in FIXES:
            s = s.replace(a, b)
        if "HANDOFF + '/" in s or 'HANDOFF' in s:
            s = s.replace("HANDOFF + '/", "HANDOFF + '/")
            if 'from paths import HANDOFF' not in s:
                lines = s.split('\n')
                i = max(i for i, l in enumerate(lines) if l.startswith('import ') or l.startswith('from ')) + 1
                lines.insert(i, 'from paths import HANDOFF')
                s = '\n'.join(lines)
        if 'os.path' in s and not re.search(r'^import .*\bos\b', s, re.M):
            s = 'import os\n' + s if not s.startswith('"""') else s.replace('"""\n', '"""\nimport os\n', 1) \
                if s.count('"""') < 2 else s[:s.index('"""', 3) + 4] + 'import os\n' + s[s.index('"""', 3) + 4:]
        open(p, 'w').write(s)
        if '/home/claude' in s and f != 'jpackage.py':
            left.append(f)
    # render a walk frame, a deployed frame and a deploy frame from a copy, at 1 ray a pixel
    test = tempfile.mkdtemp()
    shutil.copytree(Sd, test + '/src')
    code = ('import jrender as JR, jdeprender as DR, jdeploy as JD\n'
            'm = JR.load("fit_walk_e.json"); a = JR.frame(45, m, 1, False)[0]\n'
            'd = DR.load(); b = DR.frame(132, d, 1, False)[0]\n'
            'c = JD.frame(190, JD.setup(), 1, False)[0]\n'
            'print("src ok", a.size, b.size, c.size)')
    run = subprocess.run([sys.executable, '-c', code], cwd=test + '/src', capture_output=True, text=True,
                         env=dict(os.environ, TS_HANDOFF='/home/claude/units/ts-units-hd-handoff', PYTHONPATH=''))
    shutil.rmtree(test)
    out = run.stdout.strip() or (run.stderr.strip().splitlines() or ['?'])[-1]
    return left, out


README = """Juggernaut (Firestorm [JUGG]) in HD for Tiberian Factions: TSJUGG
=================================================================

frames/     tsjugg-0000.png ... tsjugg-0201.png, the mod's 202 frames on its 448 x 448 canvas, each with a -trim.png
            (white = house colour, antialiased):
              0-119    the walk: frame = facing x 15 + step, facings counter-clockwise from north
                       (0 N, 1 NW, 2 W, 3 SW, 4 S, 5 SE, 6 E, 7 NE), 3 ticks a step
              120-151  deployed at rest, 32 facings counter-clockwise from north (120 N, 128 W, 136 S, 144 E)
              152-183  deployed and aiming: the barrels raised 45 degrees about their breech
              184-201  the deploy, 18 frames facing south-west, 2 ticks a frame (played backwards to pack up);
                       184 is walk frame 45 and 201 rest frame 132, copied, so nothing pops either end
previews/   walk-east.gif, walk-south.gif   the walk, the mod's frames beside HD
            deploy.gif                the deploy, the mod's frames beside HD, held at both ends
            turn.gif                  the deployed cabin turning through its 32 facings at rest, beside the mod's
            walk-8-facings.png        TS's sprite, the mod's frame and HD, walk step 0 in each facing
            rest-8-facings.png, aim-8-facings.png   the deployed piece, the mod's frames beside HD
            scale.png                 next to the HD harvester and the HD Titan, as the game draws them
            shape-walker.png, shape-cabin.png, shape-base.png   TS's sprites as colour classes beside the model's,
                                      in TS's own camera
ts-jugg-hd-3d/   the 3D models and the barrel tips, in their own zip (ts-jugg-hd-3d.zip) next to this folder
src/        the model, its fits, the renderers and the checks (see Rebuilding below)


What it is
----------
One 3D model of the walker and one of the deployed piece, fitted to TS's own art and drawn the way the HD buildings and
the other units are:
- the walker fitted to all 120 of TS's JUGGER frames (8 facings x 15 steps): its shape to the standing frames, then
  each step's pose to that step's 8 facings.  At step 0 its silhouette overlaps TS's by {walker:.2f} on average in TS's
  own camera ({wmin:.2f} to {wmax:.2f} by facing; TS's legs are a few pixels wide, so a pixel counts for a lot);
- the cabin fitted to DJUGG_A's 32 facings (overlap {cabin:.2f}), the base to DJUGG frame 0 ({base:.2f});
- the barrels are TS's own DJUGGBAR.VXL, voxel by voxel, in its colours and normals, at the size and place the mod's
  deployed frames draw them, hinged at the breech.
Walker: the house-green body with the light grey hatch on its roof (its dark slot, the slit across its front, the dark
panel in its top), the sensor on the roof's back corner with its dark core, the two green hoops over the roof, the
three khaki barrel housings side by side with the steel muzzle brakes and their two slots, the olive hips, and the
two ochre legs with their joints.
Deployed: the walker's two legs planted as TS's base draws them (TS's front limb is the walker's near leg, pixel for
pixel) with the pivot column, its rim and the two side limbs; the cabin turning on the column; the three barrels.
The deploy follows TS's DJUGGMK frame by frame, what moves when measured off TS's frames: the west limb slides out
(frames 1-5), the east limb (4-12), the body slides back onto the column (6-10), the housings telescope forward
(10-11) and the barrels slide out of them (12-16).

Against the mod's current frames the silhouettes overlap by {ov_all:.2f}: walk {ov_walk:.2f}, at rest {ov_rest:.2f},
aiming {ov_aim:.2f}, the deploy {ov_deploy:.2f}.  Those frames are TS's sprites scaled up 6.3 times, so this is mostly
the difference above in TS's own camera, scaled up with them.


Keep (from the hand-off README)
-------------------------------
- The 448 canvas, 202 frames in the 120 / 32 / 32 / 18 split.
- One ground line: the lowest body pixel is at canvas y {ground} in every deployed and deploy frame (and the walk's
  ground point is the same; the walk's lowest pixel moves with the feet, {wlo}-{whi} by facing, as the mod's
  {mlo}-{mhi}).
- Deploy frame 184 = walk frame 45 and 201 = rest frame 132, exactly.
- The barrel tips where the model puts them: ts-jugg-hd-3d/muzzle.txt lists each barrel's tip and their mean on the
  canvas for every rest and aim frame (120-183), for the fire points.
- Shadows: black at alpha {shadow} (75%), blurred, as the buildings'; within 14 px of the canvas edge they fade out.


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.33 canvas px per TS pixel,
  the size the mod has now.  TS's sprite point (x, y) sits at canvas (6.33 x - 76.72, 6.33 y + 4.33): the mod's frames
  matched to TS's (overlap 0.97), then 5 px up, because the 32-degree camera draws ground in front of the unit about
  3 px lower than TS's 30 degrees and the ground line must stay at y {ground}.
- The deployed piece stands where TS's deploy puts it against the walker (DJUGGMK's frame 0 is JUGGER's CW5 frame
  moved by (1, 14) TS px).
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides facing
  the camera as on the other units.  The game draws this canvas at two thirds (8 canvas px per classic pixel), so the
  outline, the shadow's blur and the grain are 1.5 times as wide on the canvas, as on the Titan's.
- The shadow falls as the other walkers' do (62% as long as the buildings'), so it stays on the canvas.
- Colours read from TS's frames: house green 0,214,0 x (1 + 1.1 grain) on the body, the sensor and the hoops (the
  -trim masks cover exactly those); the hatch light grey with dark slots; khaki housings and barrels; steel muzzles;
  the legs in the Titan's yellow-brown (TS's ochre ramp), olive hips, grey joints.
- Facing east the barrels reach the canvas's right edge in three rest frames, as they do in six of the mod's: the
  canvas is the mod's.


3D models (ts-jugg-hd-3d/)
-------------------------
tsjugg-walker.glb     the walker facing east, its walk as a glTF animation ("walk": 15 steps, 0.2 s each, looping)
tsjugg-deployed.glb   the deployed piece: the base (as TS draws it, deployed facing south-west), the cabin turned east
                      with the barrels at their rest pitch on a hinge node (animation "aim": raised to 45 degrees and
                      back) and markers at the three muzzles
muzzle.txt            the barrel tips on the canvas for every rest and aim frame (120-183)
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground (the walker's ground point; the deployed piece stands where the deploy
  leaves it).
- Camera "camera_mod" in each: orthographic, 32 degrees above the ground, looking north; it frames the 448 canvas
  exactly (checked by drawing each mesh through it over a frame: walker over frame 90, overlap {glb_w}; deployed over
  frame 144, {glb_d}).
- Both pass Khronos's glTF validator with no errors or warnings (the infos are the empty marker nodes).
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
- After the shape check (signed off): the arches as two thin hoops either side of the roof, as TS's diagonal and side
  views draw them (the silhouette fit had shrunk them to a stub); the muzzle brakes' two slots (JUGGER CW2); the legs
  in the Titan's yellow-brown, a little brighter than at the shape check.
- The hatch refitted with TS's white sides told apart from its grey top: it came out taller and narrower than the
  silhouette fit had it.
- The three barrel housings are three cylinders side by side, as TS's front view draws them (the silhouette fit had
  merged them into one block; both fit TS's frames as well).
- The barrels at rest are pitched 5.3 degrees, as the mod's rest frames have them (TS starts the voxel pitched);
  aiming is 45 degrees, as the hand-off README says (the fit to the mod's aim frames gave 46).
- The thin black rod rising back from each barrel's breech in DJUGGBAR.VXL is left out: the mod's deployed frames
  never show it.
- The deploy's last frame carries the barrels (TS's own last DJUGGMK frame leaves them to the engine's voxel), so the
  turn to the deployed frames doesn't pop.


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy, Pillow and cma.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are (TS_HANDOFF:
the folder holding 04-TSJUGG/, 00-TSHARV-example/ and renderer/).
  jugg.py                the walker as convex parts;  jfitwalker.py, jfitwalk.py  its fit and its walk
                         (fit_walker_e.json, fit_walk_e.json)
  jfitcabin.py, jfithatch.py   the deployed cabin's fit (fit_cabin_a.json, then the hatch: fit_hatch_a.json)
  jbase2.py              the deployed base (fit_base2_a.json);  jbarfit.py  the barrels' size, mount and pitches
                         (fit_bar_rest.json, fit_bar_aim.json);  jmap.py  how the mod scales and places TS's sprites
  jrender.py             a walk frame;  jdeprender.py, jdeployed.py  a deployed frame;  jdeploy.py  a deploy frame
  jfinal.py              all 202 frames;  jcheck.py  the checks above;  jtips.py  muzzle.txt
  jpreviews.py, jshapecheck.py   the previews;  jexport.py  the .glb files;  glbcheck.py  draws a .glb through its
                         camera to check it;  jpackage.py  this README, src/ and the zips
  rc.py, rcrender.py     the ray caster and the buildings' look for models made of convex parts;  rcexport.py,
                         vexport.py  the .glb;  voxrender.py, vxlunit.py, tsnormals.py  the barrel voxel
    PKG=out python3 jfinal.py 0 1       renders frames/ (two workers: 0 2 and 1 2), then: python3 jfinal.py copies
"""


def write_readmes():
    ck = json.load(open(os.path.join(os.path.dirname(PKG), 'check.json')))
    st = json.load(open(os.path.join(os.path.dirname(PKG), 'shape.json')))
    vals = dict(walker=st['walker'], wmin=st['wmin'], wmax=st['wmax'], cabin=st['cabin'], base=st['base'],
                ov_all=ck['overlap_all'], ov_walk=ck['walk']['overlap'], ov_rest=ck['rest']['overlap'],
                ov_aim=ck['aim']['overlap'], ov_deploy=ck['deploy']['overlap'],
                ground=ck['rest']['lowest_max'], wlo=ck['walk']['lowest_min'], whi=ck['walk']['lowest_max'],
                mlo=ck['walk']['mod_lowest_min'], mhi=ck['walk']['mod_lowest_max'], shadow=ck['rest']['shadow_alpha'],
                glb_w=st['glb_walker'], glb_d=st['glb_deployed'])
    txt = README.format(**vals)
    open(PKG + '/README.txt', 'w').write(txt)
    i = txt.index('3D models (ts-jugg-hd-3d/)'); j = txt.index('Judgement calls')
    open(D3 + '/README.txt', 'w').write('Juggernaut (Firestorm [JUGG]) in HD: the 3D models\n'
                                        '==================================================\n\n' + txt[i:j].rstrip() + '\n')
    return txt


def zips():
    sys.path.insert(0, VOX)
    import pngopt
    pngopt.optimize_folder(PKG)
    shutil.rmtree(PKG + '/src/__pycache__', ignore_errors=True)
    parent = os.path.dirname(PKG)
    out = {}
    for name in (os.path.basename(PKG), os.path.basename(D3)):
        z = os.path.join(parent, name + '.zip')
        if os.path.exists(z):
            os.remove(z)
        subprocess.run(['zip', '-qr', name + '.zip', name], cwd=parent)
        out[name] = os.path.getsize(z)
    return out


if __name__ == '__main__':
    left, srcok = package_src()
    write_readmes()
    sizes = zips()
    print('local paths left', left, '|', srcok, '|', {k: '%.1f MiB' % (v / 2 ** 20) for k, v in sizes.items()})
