"""
infpackage.py - an infantry unit's package (E1 first): the frames (infall.py), previews (infpreview.py and the shape
sheets), the 3D model (infexport.py), the READMEs with the numbers (infreport.py), src/ with relative paths (checked
by rendering from a copy), and the two zips.

    python3 infpackage.py UNIT PKG          (PKG = .../ts-e1-hd; its 3D folder ts-e1-hd-3d sits beside it)
        env SKIP=frames,previews,glb  to reuse what's there
"""
import json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
VOX = '/home/claude/units/work/vox/'
RENDERER = HANDOFF + '/renderer/'
VALIDATOR = os.environ.get('GLTF_VALIDATOR', 'validate.js')      # Khronos's glTF validator (node)

CODE = ['inf.py', 'inffit.py', 'infunit.py', 'infseq.py', 'infcycle.py', 'infstatic.py', 'infrefine.py',
        'infsmooth.py', 'infliedown.py', 'infsubfit.py', 'infcalib.py', 'infrender.py', 'infall.py', 'infx.py',
        'infexport.py', 'infpreview.py', 'infreport.py', 'infcheck.py', 'infmasks.py', 'infgif.py', 'hdgrid.py',
        'cyclesheet.py', 'infshow.py', 'motion.py', 'infmap.py', 'infpackage.py', 'casepost.py', 'casespot.py',
        'crawlbio.py', 'wriggle.py', 'inflook.py', 'inflook_e2.py', 'inflook_eng.py', 'crawlfit.py', 'crawlgif.py', 'tsview.py',
        # (TS's shadow and the ground; the deaths fitted to them; fire's two poses; the railgun laid along TS's)
        'tsshadow.py', 'ground.py', 'deathfit2.py', 'deathback.py', 'deathshadow.py', 'gunline.py', 'firepair.py', 'animsheet.py',
        'gunpass.py',
        'fitcheck.py', 'checksheet.py', 'e2pack.py', 'pickside.py',
        # (the run's start step per facing; a death's frames refitted; the crawl's key poses; a few sizes refitted)
        'infphase.py', 'deathfix.py', 'infkey.py', 'e2_subfit.py']
# data every package carries (TS's shadow light, read off all six units' standing frames)
COMMON_DATA = ['ts_light.json']
# every unit's fitted data (each package takes the ones its unit has)
DATA = ['%s_shape.json', '%s_stand_frames.json', '%s_walk_cycF.json', '%s_walk_cyc.json', '%s_walk_faces.json',
        '%s_walk_frames.json', '%s_crawlfit.json', '%s_crawl_frames.json',
        '%s_fire_start.json', '%s_fire_pose.json', '%s_fire_cyc.json', '%s_fire_faces.json', '%s_fire_frames.json',
        '%s_prone_fire_start.json', '%s_prone_fire_pose.json', '%s_prone_fire_cyc.json', '%s_prone_fire_faces.json',
        '%s_prone_fire_frames.json', '%s_lie_down_frames.json', '%s_get_up_frames.json', '%s_idle1_frames.json',
        '%s_idle2_frames.json', '%s_death1_frames.json', '%s_death2_frames.json',
        # (the Jumpjet's flight, the Medic's heal and where he sets his case down)
        '%s_fly_frames.json', '%s_fire_fly_frames.json', '%s_tumble_frames.json', '%s_heal_frames.json',
        '%s_idle2_case.json', '%s_heal_case.json', '%s_death1_case.json', '%s_death2_case.json',
        # (the deaths' shadows: deathshadow.py)
        '%s_shadow_w.json']
EXTRA = {'e1': [('sc/e1-standing-8-facings.png', 'standing-8-facings.png'), ('sc/e1-masks.png', 'masks.png'),
                ('sc/e1-run-before-now.png', 'run-before-now.png')],
         'e2': [('sc/e2-standing-8-facings.png', 'standing-8-facings.png'), ('sc/e2-masks.png', 'masks.png')],
         'eng': [('sc/eng-standing-8-facings.png', 'standing-8-facings.png'), ('sc/eng-masks.png', 'masks.png')],
         'ghost': [('sc/ghost-standing-8-facings.png', 'standing-8-facings.png'), ('sc/ghost-masks.png', 'masks.png')],
         'jj': [('sc/jj-standing-8-facings.png', 'standing-8-facings.png'), ('sc/jj-masks.png', 'masks.png')],
         'medic': [('sc/medic-standing-8-facings.png', 'standing-8-facings.png'), ('sc/medic-masks.png', 'masks.png')]}
SHARED = [VOX + f for f in ('rc.py', 'rcrender.py', 'rcexport.py', 'glbcheck.py', 'vexport.py', 'voxrender.py',
                            'pngopt.py')]
REN = [RENDERER + f for f in ('hd.py', 'walls2.py', 'wnoise.py', 'export3d.py', 'vxl.py')]


def package_src(unit, pkg):
    Sd = pkg + '/src'
    shutil.rmtree(Sd, ignore_errors=True); os.makedirs(Sd)
    for f in CODE:
        shutil.copy(os.path.join(HERE, f), Sd)
    for f in DATA:
        if os.path.exists(os.path.join(HERE, f % unit)):
            shutil.copy(os.path.join(HERE, f % unit), Sd)
    for f in COMMON_DATA:
        shutil.copy(os.path.join(HERE, f), Sd)
    for f in SHARED + REN:
        shutil.copy(f, Sd)
    open(Sd + '/paths.py', 'w').write(
        '"""where the scripts find Luke\'s hand-off folders: set TS_HANDOFF to the hand-off\'s root folder (the one\n'
        'holding 17-TSE1/, the other units\' folders and renderer/)."""\nimport os\n'
        "HANDOFF = os.environ.get('TS_HANDOFF', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', "
        "'ts-units-hd-handoff'))\n")
    left = []
    for f in sorted(os.listdir(Sd)):
        if not f.endswith('.py') or f == 'paths.py':
            continue
        p = os.path.join(Sd, f); s = open(p).read()
        s = re.sub(r"^[ \t]*sys\.path\.insert\(0, ['\"]/home/claude/units/[^'\"]*['\"]\)\n", '', s, flags=re.M)
        if "HANDOFF + '/" in s:
            s = s.replace("HANDOFF + '/", "HANDOFF + '/")
            if 'from paths import HANDOFF' not in s:
                # (right after the first import: a module can import more further down, after HANDOFF's first use -
                # tsshadow.py's ROOT)
                lines = s.split('\n')
                import ast
                i = min(n.end_lineno for n in ast.parse(s).body if isinstance(n, (ast.Import, ast.ImportFrom)))
                lines.insert(i, 'from paths import HANDOFF')
                s = '\n'.join(lines)
        s = s.replace("VALIDATOR = os.environ.get('GLTF_VALIDATOR', 'validate.js')      # Khronos's glTF validator (node)",
                      "VALIDATOR = os.environ.get('GLTF_VALIDATOR', 'validate.js')      # Khronos's glTF validator (node)")
        open(p, 'w').write(s)
        if '/home/claude' in s and f != 'infpackage.py':
            left.append(f)
    # render a run frame and a fire frame (with its flash; the unarmed Engineer: a death frame) from a copy, at 1 ray a
    # pixel
    second = 140 if unit in ('eng', 'medic') else 176      # (a frame each unit draws: their fire frames are empty)
    test = tempfile.mkdtemp()
    shutil.copytree(Sd, test + '/src')
    code = ('import json, infunit, inf as I, infall as AL\n'
            'infunit.use("%s")\n'
            'js = json.load(open("%s_shape.json"))\n'
            'S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js["S"].items()})\n'
            'tab = AL.pose_table("%s", dict(js["Q"]))\n'
            'a = AL.render_frame("%s", S, js, 20, *tab[20], ss=1)[0]\n'
            'b = AL.render_frame("%s", S, js, %d, *tab[%d], ss=1)[0]\n'
            'print("src ok", a.size, b.size)') % (unit, unit, unit, unit, unit, second, second)
    run = subprocess.run([sys.executable, '-c', code], cwd=test + '/src', capture_output=True, text=True,
                         env=dict(os.environ, PYTHONPATH='', TS_HANDOFF=os.environ.get('TS_HANDOFF', '/home/claude/units/ts-units-hd-handoff')))
    shutil.rmtree(test)
    out = run.stdout.strip() or (run.stderr.strip().splitlines() or ['?'])[-1]
    return left, out


def F_UNITS_NAME(unit):
    import inffit as F
    return F.UNITS[unit][1].lower()


def zipdir(src, dst):
    if os.path.exists(dst):
        os.remove(dst)
    subprocess.run(['zip', '-qr9', os.path.abspath(dst), os.path.basename(src)], cwd=os.path.dirname(src), check=True)
    return os.path.getsize(dst) / 2 ** 20


def main():
    unit, pkg = sys.argv[1], os.path.abspath(sys.argv[2])
    import infunit; infunit.use(unit)
    skip = os.environ.get('SKIP', '').split(',')
    d3 = pkg + '-3d'
    frames, previews = pkg + '/frames', pkg + '/previews'
    for p in (frames, previews, d3):
        os.makedirs(p, exist_ok=True)
    env = dict(os.environ)
    if 'frames' not in skip:
        subprocess.run([sys.executable, 'infall.py', unit, '%s_shape.json' % unit, frames], cwd=HERE, check=True,
                       stdout=subprocess.DEVNULL)
    if 'previews' not in skip:
        subprocess.run([sys.executable, 'infpreview.py', unit, frames, previews], cwd=HERE, check=True)
    rep = json.load(open(os.path.join(HERE, '%s_report.json' % unit))) if 'report' in skip else None
    if rep is None:
        subprocess.run([sys.executable, 'infreport.py', unit, '%s_shape.json' % unit, frames, '%s_report.json' % unit],
                       cwd=HERE, check=True, stdout=subprocess.DEVNULL)
        rep = json.load(open(os.path.join(HERE, '%s_report.json' % unit)))
    glb = os.path.join(d3, 'ts%s.glb' % F_UNITS_NAME(unit))
    import infexport as EX
    path, info = EX.export(unit, os.path.join(HERE, '%s_shape.json' % unit), glb)
    try:
        val = subprocess.run(['node', VALIDATOR, glb], capture_output=True, text=True).stdout.strip()
    except OSError:
        val = ''
    val = (val or 'not run (no glTF validator: set GLTF_VALIDATOR)').splitlines()[0]
    chk = subprocess.run([sys.executable, VOX + 'glbcheck.py', glb, frames + '/ts%s-0006.png' % F_UNITS_NAME(unit),
                          os.path.join(tempfile.gettempdir(), 'inf-glbcheck.png'), '267x208'],
                         capture_output=True, text=True).stdout
    glb_ov = [l for l in chk.splitlines() if 'overlap' in l][-1].split(':')[-1].strip()
    # the previews made along the way
    for src, name in EXTRA.get(unit, []):
        if os.path.exists(os.path.join(HERE, src)):      # (queue/post2.sh UNIT PKG standing makes them)
            shutil.copy(os.path.join(HERE, src), os.path.join(previews, name))
    # (the frame-by-frame check sheets against TS, when made: queue/post2.sh)
    SPD = os.environ.get('SHEETS', '/tmp/claude-0/-home-claude/25343c56-d27f-5b76-9102-de86ff0460c2/scratchpad') + '/'
    for sheet, name in (('death1', 'death-1-sheet.png'), ('death2', 'death-2-sheet.png'), ('crawl', 'crawl-sheet.png'),
                        ('fire', 'fire-sheet.png'), ('anim', 'animation-sheet.png')):
        p = SPD + '%s_%s_sheet.png' % (unit, sheet)
        if os.path.exists(p):
            shutil.copy(p, os.path.join(previews, name))
    for seq, name in (('walk', 'shape-run.png'), ('crawl', 'shape-crawl.png')) + ((('fire', 'shape-throw.png'),)
                                                                                   if unit == 'e2' else ()):
        subprocess.run([sys.executable, 'cyclesheet.py', unit, '%s_shape.json' % unit, '%s_%s_frames.json' % (unit, seq),
                        seq, os.path.join(previews, name), '-', '4'], cwd=HERE, check=True, stdout=subprocess.DEVNULL)
    write_readmes(unit, pkg, rep, info, val.replace('errors', 'errors').strip(), glb_ov)
    left, src_ok = package_src(unit, pkg)
    print('src', src_ok, 'paths left in', left)
    print('glb', val, glb_ov)
    import pngopt as PO
    PO.optimize_folder(frames); PO.optimize_folder(previews)
    z1 = zipdir(pkg, pkg + '.zip'); z2 = zipdir(d3, d3 + '.zip')
    print('zips %.1f MiB, %.1f MiB' % (z1, z2))
    json.dump(dict(rep, glb_validator=val, glb_overlap=glb_ov, src=src_ok, zips=[z1, z2]),
              open(pkg + '/../%s_pkg.json' % unit, 'w'), indent=1)


README = """Light Infantry (TS [E1]) in HD for Tiberian Factions: TSE1
==========================================================

frames/     tse1-0000.png ... tse1-0291.png, the mod's 292 frames on its 267 x 208 canvas, each with a -trim.png
            (white = house colour, antialiased), numbered as TS's own E1Sequence (the mod keeps it):
              0-7      standing, one a facing; facings counter-clockwise from north (0 N, 1 NW, 2 W, 3 SW, 4 S, 5 SE,
                       6 E, 7 NE)
              8-55     the run: 6 steps a facing (frame = 8 + facing x 6 + step), 2 ticks a step, looping
              56-70    idle 1 (TS draws it facing east);  71-84  idle 2 (facing south);  85 (unused) = 84
              86-133   the crawl: 6 steps a facing, looping; its first step is the prone pose
              134-148  death 1 (facing south-west);  149-163  death 2 (facing east); both end lying flat
              164-211  fire: 6 frames a facing, 1 tick a frame, the muzzle flash where TS has it
              212-259  fire prone, the same
              260-275  lying down, 2 frames a facing;  276-291  getting up: the same two backwards (TS's are)
previews/   run-8-facings.gif, crawl-8-facings.gif, fire-8-facings.gif, fire-prone-8-facings.gif
                                  every facing at once, TS's sprite (as the mod scales it) above HD
            run-west.gif, run-south.gif, crawl-west.gif, crawl-south.gif, fire-west.gif, fire-south.gif
                                  TS's sprite | the mod's frame | HD, at the game's speed
            idle-1.gif, idle-2.gif, death-1.gif, death-2.gif      the same for the one-facing sequences
            lie-down-get-up-W.gif, lie-down-get-up-SE.gif         standing -> down -> prone -> up -> standing
            standing-8-facings.png    TS's sprite, the mod's frame, HD and EA's HD Minigunner, each facing
            masks.png                 the head close up in 7 facings: TS, the mod, HD
            run-before-now.png        the run as the shape check had it, and now
            shape-run.png, shape-crawl.png    TS's frames as colour classes beside the model's, in TS's own camera
ts-e1-hd-3d/   the 3D model in its own zip (ts-e1-hd-3d.zip) next to this folder
src/        the model, its fits, the renderer and the checks (see Rebuilding below)


What it is
----------
One posable soldier built from simple solids (inf.py, shared by the six infantry units, each with its own sizes, gear
and colours), fitted to TS's own E1 frames in TS's camera (silhouette and colour classes, TS's muzzle flashes and
blood left out) and drawn the way the HD buildings and the other units are.
- The look (your makeover, after the ArtStation GDI infantry turnaround you sent; TS's sprite still sets where every
  part is and its colour; inflook.py): the same skeleton, poses and fitted sizes built as armour.  Angular shoulder
  plates sit on the shoulders, a second plate on each upper arm; the arms narrow to a dark elbow (the undersuit
  between the plates), a green bracer on each forearm, gloves.  A chest plate and back plate over the dark undersuit,
  pouches across the belly and on the belt; the pack with its flap, the pouch under it.  Green thigh plates on the
  thighs' outer fronts, knee plates, light grey greaves down the shins, boots with soles.  The helmet's visor in a
  dark frame, a round ear piece each side.  The rifle in parts: stock, pistol grip, receiver with a sight on top,
  magazine, handguard, barrel and muzzle.  House colour stays plain: its plates read by their shape alone.
- The shape is fitted to the 8 standing frames together.  The helmet is a rounded box (TS: the head 4 px across, its
  sides upright); the mask is a faceplate set in its front, glowing TS's brightest light blue (TS: 178,178,255 and
  149,149,230 with a near-white glint, in every facing), a dark jaw guard under it, as the references' full helmets
  with big blue visors; the glint TS puts on the helmet's top left is the glossy helmet's highlight.  The torso is a
  dark vest all round (TS's dark greys); the shoulder pads, arms, hips and thighs are house green (TS's remap areas);
  the shins and the plate on his back light grey, the boots dark, the rifle black (TS draws it 0-28).
- Standing: one pose fitted to the 8 standing frames together, then each facing's arms, rifle and head to its own
  frame (TS doesn't draw one pose turned: its soldier holds the rifle up in one facing and down in the next).
  Overlap with TS's frames in TS's camera: {ts_stand:.2f}.
- The run is one smooth loop: every joint follows a short smooth curve (a Fourier series) through the 6 steps, so
  step 5 runs into step 0 like any step into the next and nothing jumps back to a start pose.  The legs follow one
  curve half a cycle apart (a real stride: each thigh swings once a cycle); the body stays on its spot with a steady
  bob and a lean of 20-30 degrees (TS's south view stands 2-5 px shorter than its standing soldier: that lean), the
  head level so the visor shows; the hands stay on the rifle, which swings from across his left side (TS's steps 0-2)
  to pointing ahead (3-5) and back.  The loop is fitted to TS's 48 run frames together; TS doesn't draw the rifle the
  same way in every facing (facing south it swings side to side), so each facing's arms, rifle and head then get their
  own smooth loop on top, held close to the shared one.  Overlap {ts_walk:.2f}; the furthest any landmark (muzzle, rifle
  butt, hands, head, feet) moves from one step to the next is {mo_walk:.1f} TS px (the rifle is 12 long).
- The crawl is rebuilt from TS's own crawl frames (your notes: "view how og is doing it", "research how a body crawls
  prone"). It is a real prone crawl, done the way the army's low crawl and the leopard crawl are: flat and low on his
  front, up on his forearms with his head up to see. One forearm goes forward with the opposite knee, which is drawn
  up while the other leg lies straight back, and his body rolls a little towards that knee; then the other pair. TS
  drew it in all 8 facings, and all 8 are fitted together. The rifle goes forward in both hands with each stroke and
  draws back. One stroke drives every joint, so the loop runs on with nothing jumping back. How far he is propped up,
  where he looks and how far each part moves are fitted to TS's crawl frames. Overlap {ts_crawl:.2f}, landmarks at
  most {mo_crawl:.1f} TS px a step.
  His whole body moves as TS's does (your notes: "the body stays stiff as a board", "their whole body really
  moves").  The skeleton has a two-piece spine (lower and upper back), so the body curves rather than angling at the
  hips; shoulders that reach forward and pull back; hips that hitch up as each knee draws in; and the pelvis turning
  about its long axis.  Each step's body is fitted to that step's TS frames in all 8 facings (with how the head moves
  against the body as a term of its own), the 6 steps joined into one smooth loop, and the movement drawn at 1.5
  times what that fit gives (judged by eye: at TS's 14 px a lying soldier, the pixels alone can't tell the
  shoulders' and hips' movement apart).  The arms hold the rifle out in front of his head (your notes: "he has no
  elbows", the right arm "still under the body and not out in front"): both hands up the rifle 1-5 TS px ahead of
  his shoulders, both elbows on the ground, each forearm reaching forward in turn (the left with the right knee, the
  right with the left), where the hands sit, the elbows point and the rifle lies fitted to TS's frames step by step.
  The arms narrow from shoulder to elbow and from elbow to wrist with a round elbow between (every sequence).
- Fire and fire prone: TS holds one pose through each facing's 6 frames (only the flash comes and goes), so each facing
  has one pose for all 6: fitted to the 8 facings' flash-free frames together, then each facing's arms, rifle and head
  to its own.  Overlap {ts_fire:.2f} and {ts_prone:.2f}.
- Lying down: the two in-betweens fitted to TS's frames on the way down through kneeling on all fours (TS's second
  frame), from the standing pose to the prone one (the crawl's first step), so standing, down and prone run as one movement ({ts_lie:.2f}); getting up is the same two
  poses backwards, as TS's get-up frames are its lie-down frames backwards, pixel for pixel.
- The idles and deaths: each frame fitted to its TS frame starting from the one before, then the whole run of poses
  relaxed together (every frame pulled towards the middle of its neighbours), so they move smoothly; the idles start
  from the standing pose and come back to it.  Overlap: idles {ts_idle1:.2f} and {ts_idle2:.2f}, deaths {ts_death1:.2f} and {ts_death2:.2f}.
- Effects, frame by frame from TS's own pixels: the muzzle flash (TS's three yellows, its shape kept, drawn smooth and
  hot: a white-yellow core, amber, orange edges) at the HD rifle's muzzle, hidden where the soldier stands in front of
  it; the blood in TS's red (255,0,0, as TS and the mod draw it), each red pixel drawn on the ground it covers in TS's
  view, so a pool stays put as the body falls on it.
Against the mod's current frames the silhouettes overlap by {mod_all:.2f} (standing {mod_stand:.2f}, run {mod_walk:.2f}, crawl {mod_crawl:.2f}, fire
{mod_fire:.2f}): those frames are TS's sprites scaled up 3.068 times, so this is the difference in TS's own camera above,
scaled up with them (a soldier's limbs are a few TS pixels wide, so a pixel counts for a lot), plus the 32-degree camera.


Keep (from the hand-off README)
-------------------------------
- The 267 x 208 canvas; every frame of the layout in TS's order (85, unused, included).
- The feet: the soldier's ground point lands where the mod's frames put TS's (TS's sprite x 3.068 at (38.06, 10.57));
  standing, the boots' lowest pixel is on canvas row {feet_lo}-{feet_hi} by facing, as the mod's own frames have it
  on {mfeet_lo}-{mfeet_hi} (the README: feet on 111).
- EA's infantry height: he stands 60 px tall on average over his 8 standing facings, as EA's rifleman does in TD and
  RA (61 px; their infantry run 60-65; see standing-8-facings.png).  His armour makes him bulkier than EA's rifleman,
  about as bulky as EA's Grenadier and Engineer.
- The shadow baked in at alpha 128 (50% black, blurred): the README's minimum, lighter than the buildings' 75%, as
  the mod's frames carry TS's at about 25% (your note: at 75% the falling deaths looked like floating).


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 3.068 canvas px per TS pixel
  (the mod's frames are TS's sprite x 3.068), the soldier drawn 3.7% bigger about his feet, so he stands as tall as EA's
  rifleman (your note: the Light Infantry must match TD's and RA's infantry sizes).
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with a stronger camera fill than the
  vehicles' (EA's HD infantry are lit from the front); none on the rifle, which stays black as TS's.
- House colour: exactly 0,214,0 x (1 + 1.1 grain) on the shoulder pads, arms, hips and thighs; the -trim masks cover
  exactly those.


3D model (ts-e1-hd-3d/)
-----------------------
tse1.glb   the soldier in vertex colours, every sequence as a glTF animation, the mod's camera
- Nodes: LightInfantry > pelvis, belt, abdomen, chest, vest, pack, pouch, helmet, mask, jaw, rifle, receiver, and
  left_/right_ thigh, shin, knee, boot, shoulder_pad, upper_arm, forearm, hand; "muzzle" (a marker on the rifle,
  where the flash comes from).  Each part is one rigid solid, posed per frame by its node's translation and rotation.
- Animations, facing east (the 8-facing sequences use the east facing's frames), at the game's speed (15 ticks a
  second); the looping ones end on their first frame again, so they loop without a seam:
{anims}
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (30.3 TS px, as the other TS units' models).
  Origin: the soldier's position on the ground.  He faces east (the mod's facing 6).
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 267 x 208 canvas
  exactly (checked by drawing the mesh through it over frame 6: overlap {glb_ov}).
- The file passes Khronos's glTF validator: {glb_val}.
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
{calls}
- The run moves smoothly where TS's own run jumps (its rifle snaps from his left side to the front and back between
  steps 2 and 3 and 5 and 0): your note, "fluid movements and not teleport back to start position".  The rifle swings
  on one path instead; each facing's loop still follows that facing's TS frames.
- The run's lean is held to 20-30 degrees and the head kept level: a free fit hunched him over (a 45-degree lean, the
  visor hidden), which TS's frames don't show.
- TS draws idle 1 facing east and idle 2 facing south (their first frames match those standing frames); the hand-off
  README says west and east.  They're drawn as TS's frames are.
- Fire and fire prone hold one pose a facing through all 6 frames, as TS's do; frame 85 (unused) is a copy of 84.
- His hands stay on the rifle through both deaths; TS's soldier lets it drop in death 2 (frames 154-157).
- The blood is TS's own red (255,0,0), as the mod has it now; no darker shade was added.


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy, Pillow and cma.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are (TS_HANDOFF: the
folder holding 17-TSE1/ and renderer/).
  inf.py                 the posable soldier (shape S, pose Q) as convex solids;  rc.py  the ray caster
  inffit.py              the fit's loss in TS's camera, and the shape + standing fit (e1_shape.json); infrefine.py
                         each facing's own arms and rifle (e1_stand_frames.json); infmap.py  how the mod scales TS's
  infcycle.py            the run as a smooth loop: the shared cycle (e1_walk_cycF.json), each facing's own loop
                         (e1_walk_faces.json) and every frame's pose (e1_walk_frames.json)
  crawlbio.py            the crawl, a real prone crawl fitted to TS's crawl frames (e1_crawlfit.json,
                         e1_crawl_frames.json); crawlfit.py  which facings TS drew, and the mirror for flipped ones
  infstatic.py           fire and fire prone, one pose a facing (e1_fire_pose.json, e1_fire_frames.json, ...)
  infliedown.py          lying down and getting up;  infsmooth.py  the idles and deaths
  infrender.py           an HD frame;  infx.py  the muzzle flash;  infall.py  all 292 frames with flash and blood
  infexport.py           the .glb;  infpreview.py  the previews;  infreport.py  the numbers above
  infcheck.py, infgif.py, hdgrid.py, cyclesheet.py, infshow.py, motion.py   the checks used along the way
  infpackage.py          this package (frames, previews, model, src)
e.g.  python3 infall.py e1 e1_shape.json out/          (every frame; or a list: out/ 8,9,10)
      python3 infcycle.py e1 e1_shape.json walk cyc.json 300            (refit the run's shared cycle)
"""


README_E2 = """Disc Thrower (TS [E2]) in HD for Tiberian Factions: TSE2
=======================================================

frames/     tse2-0000.png ... tse2-0291.png, the mod's 292 frames on its 267 x 208 canvas, each with a -trim.png
            (white = house colour, antialiased), numbered as TS's own sequence (the mod keeps it):
              0-7      standing, one a facing; facings counter-clockwise from north (0 N, 1 NW, 2 W, 3 SW, 4 S, 5 SE,
                       6 E, 7 NE)
              8-55     the run: 6 steps a facing (frame = 8 + facing x 6 + step), 2 ticks a step, looping
              56-70    idle 1 (TS draws it facing south-west);  71-84  idle 2 (facing north-east);  85 (unused) = 84
              86-133   the crawl: 6 steps a facing, looping; its first step is the prone pose
              134-148  death 1 (facing south-west);  149-163  death 2 (facing north-east); both end lying flat
              164-211  the throw: 6 frames a facing, 1 tick a frame, from the ready stance and back to it
              212-259  the throw lying down, the same
              260-275  lying down, 2 frames a facing;  276-291  getting up: the same two backwards (TS's are)
previews/   run-8-facings.gif, crawl-8-facings.gif, throw-8-facings.gif, throw-prone-8-facings.gif
                                  every facing at once, TS's sprite (as the mod scales it) above HD
            run-west.gif, run-south.gif, crawl-west.gif, crawl-south.gif, throw-west.gif, throw-south.gif
                                  TS's sprite | the mod's frame | HD, at the game's speed
            idle-1.gif, idle-2.gif, death-1.gif, death-2.gif      the same for the one-facing sequences
            lie-down-get-up-W.gif, lie-down-get-up-SE.gif         standing -> down -> prone -> up -> standing
            standing-8-facings.png    TS's sprite, the mod's frame, HD and EA's HD Grenadier, each facing
            masks.png                 the head close up in 7 facings: TS, the mod, HD
            shape-run.png, shape-crawl.png, shape-throw.png    TS's frames as colour classes beside the model's, in
                                  TS's own camera
ts-e2-hd-3d/   the 3D model in its own zip (ts-e2-hd-3d.zip) next to this folder
src/        the model, its fits, the renderer and the checks (see Rebuilding below)


What it is
----------
The posable soldier of the Light Infantry (inf.py, shared by the six infantry units) with the Disc Thrower's own
sizes, gear and colours (infunit.py), fitted to TS's own E2 frames in TS's camera (silhouette and colour classes,
TS's blood left out) and drawn the way the HD buildings and the other units are.
- His gear, read from TS's frames: no rifle; one big blue rucksack on his back, from his shoulders to his belt (TS's
  back view: blue-grey 8-9 px across from the shoulders down; its side views: 3-4 px proud of his back; your note: "the
  big blue rucksack of og"); orange patches on the backs of his trouser legs at the top (TS's back views: orange right
  across his seat, 3 rows tall; your note: patches on the back of his trousers, not a bag); orange knee pads (TS's
  front views).  Dark armour all over (TS's dark greys); the shoulder pads, arms, hips and thighs house green
  (TS's remap areas); the helmet navy with a light-blue faceplate across the lower half of its front and round its
  sides (TS shows it in every facing that sees his face, 2 px at the front edge in the side views), a dark jaw guard
  under it, the glossy helmet's glint on its top left.
- The look (your makeover, after the Westwood renders you sent - the throwing render, the FMV still kneeling by the
  wreck - and the Tiberian Aftermath turnaround; in the Light Infantry makeover's style; TS's sprite still sets where
  every part is and its colour; inflook_e2.py): the same skeleton, poses and fitted sizes built as armour.  The box
  pack as before (TS's blue-grey, its lid band) with the radio's whip antenna from its top corner (not in TS's sprite:
  from the renders; it springs upright when he lies down) and a slatted panel on its back.  The two disc drums low on
  his back, one above the other across his hips under the pack, sticking out either side, with dark end caps and hubs:
  TS's orange across his seat and at the backs of his hips is where they sit, so they replace the orange patches and
  take TS's orange ramp.  The full helmet with the big visor in a dark frame, an ear piece each side, the respirator
  under the visor and its hose down to his chest (TS's navy line down his chest).  A segmented chest: the chest plate,
  three plates down the belly with the dark suit between, a gorget.  Shoulder pads of three plates in plain house green
  (the renders' stripes as the plates' edges only).  Green upper arms, dark elbows, long dark gauntlets (TS draws his
  forearms dark).  Green thighs with a plate on their outer front, the backs of the legs dark (TS's back view), dark
  orange knee pads (TS's front views), greaves, boots with soles and two straps.  You signed it off.
- The shape is fitted to the 8 standing frames together, then the rucksack and the orange patches, and the faceplate,
  on their own (each a few
  pixels a frame, which a fit of the whole soldier gives up for a pixel of silhouette elsewhere), then each facing's
  arms and head to its own frame.  Overlap with TS's frames in TS's camera: {ts_stand:.2f}.
- The orange is drawn on TS's own orange ramp (its frames' eleven oranges, dark red-orange to light yellow-orange),
  as light on average as TS draws it: the HD light (the buildings', from the north-west) leaves the patches on the
  backs of his legs in his own shadow, where a plain orange came out brown.  TS draws them about as light standing,
  running and crawling, whichever way they face, so they keep only half their HD shading.
- The run is one smooth loop: every joint follows a short smooth curve (a Fourier series) through the 6 steps, so
  step 5 runs into step 0 like any step into the next and nothing jumps back to a start pose.  The legs follow one
  curve half a cycle apart (each thigh swings once a cycle), the arms swing in turn.  The loop is fitted to TS's 48 run
  frames together; each facing's arms and head then get their own smooth loop on top, held close to the shared one.
  Overlap {ts_walk:.2f}; the furthest any landmark (hands, head, feet) moves from one step to the next is {mo_walk:.1f} TS px.
- The crawl is rebuilt from TS's own crawl frames (your notes: "view how og is doing it", "research how a body crawls
  prone"). It is a real prone crawl, done the way the army's low crawl and the leopard crawl are: flat and low on his
  front, up on his forearms with his head up to see. One forearm goes forward with the opposite knee, which is drawn
  up while the other leg lies straight back, and his body rolls a little towards that knee; then the other pair. TS
  drew this crawl only facing N, NW, W, SW and S, and its NE, E and SE crawl frames are those sprites flipped, pixel
  for pixel. One pose can't match both sides, which is what made the earlier crawls flail, so the crawl is fitted to
  the five facings TS drew and the flipped facings get the same pose mirrored, as TS's do. One stroke drives every
  joint, so the loop runs on with nothing jumping back. How far he is propped up, where he looks and how far each
  part moves are fitted to TS's crawl frames. Overlap {ts_crawl:.2f}, landmarks at most {mo_crawl:.1f} TS px a step.
  His whole body moves as the Light Infantry's does (your notes on its crawl: "stiff as a board", "their whole body
  really moves"), on the infantry's new skeleton: a two-piece spine, so the body curves; shoulders that reach and
  pull back; hips that hitch up as each knee draws in.  Each step's body is fitted to that step's TS frames (the
  facings TS drew; the flipped ones get the mirror), the 6 steps joined into one smooth loop and the movement drawn at
  1.5 times the fit, as the Light Infantry's accepted crawl.  His arms reach out in front along the ground, one
  forearm then the other (the left with the right knee, the right with the left), his hands 1-3 TS px ahead of his
  shoulders and his elbows down by his chest - fitted to TS's frames step by step, then made one alternating stroke.
  His arms narrow from shoulder to elbow and elbow to wrist with a round elbow between (every sequence).
- The throw: TS's six frames a facing are one throw from the ready stance and back to it (the throwing arm drawn
  back and over, out forward, the follow-through and the recovery), so it is one smooth loop like the run, step for
  step with TS's frames: overlap {ts_fire:.2f}.  A throw is quick: the throwing hand travels up to {mo_fire:.1f} TS px in a
  step, the body far less, and no step jumps out of line with the rest.  The disc leaves at the end of the throw (step
  6, as the hand-off README has it); the disc in flight is the game's effect.  The throw lying down the same: overlap
  {ts_prone:.2f}, the hand at most {mo_prone:.1f} TS px a step.
- Lying down: the two in-betweens fitted to TS's frames on the way down through kneeling on all fours (TS's second
  frame), from the standing pose to the prone one (the crawl's first step), so standing, down and prone run as one movement ({ts_lie:.2f}); getting up is the same two
  poses backwards, as TS's get-up frames are its lie-down frames backwards, pixel for pixel.
- The idles and deaths: each frame fitted to its TS frame starting from the one before, then the whole run of poses
  relaxed together (every frame pulled towards the middle of its neighbours), so they move smoothly; the idles start
  from the standing pose and come back to it.  Overlap: idles {ts_idle1:.2f} and {ts_idle2:.2f}, deaths {ts_death1:.2f} and {ts_death2:.2f}.
- The blood, frame by frame from TS's own pixels: TS's red (255,0,0, as TS and the mod draw it), each red pixel drawn on
  the ground it covers in TS's view, so a pool stays put as the body falls on it.
Against the mod's current frames the silhouettes overlap by {mod_all:.2f} (standing {mod_stand:.2f}, run {mod_walk:.2f}, crawl {mod_crawl:.2f}, throw
{mod_fire:.2f}): those frames are TS's sprites scaled up 3.071 times, so this is the difference in TS's own camera above,
scaled up with them (a soldier's limbs are a few TS pixels wide, so a pixel counts for a lot), plus the 32-degree camera.


Keep (from the hand-off README)
-------------------------------
- The 267 x 208 canvas; every frame of the layout in TS's order (85, unused, included).
- The feet: the soldier's ground point lands where the mod's frames put TS's (TS's sprite x 3.071 at (38.68, 10.60));
  standing, the boots' lowest pixel is on canvas row {feet_lo}-{feet_hi} by facing, as the mod's own frames have it
  on {mfeet_lo}-{mfeet_hi} (the README: feet on 111).
- He stands as tall as EA's Grenadier (63 px on average over his 8 standing facings; your note: the infantry must
  match TD's and RA's sizes; see standing-8-facings.png).
- The shadow baked in at alpha 128 (50% black, blurred): the README's minimum, lighter than the buildings' 75%, as
  the mod's frames carry TS's at about 25% (your note: at 75% the falling deaths looked like floating).
- The release read on the last throw frame: the throw runs step for step with TS's, ending as TS's ends.


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 3.071 canvas px per TS pixel
  (the mod's frames are TS's sprite x 3.071), the soldier drawn at EA's Grenadier's height about his feet.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the units' camera fill (EA's HD
  infantry are lit from the front); each part as light as TS draws it under that light (infcalib.py), the orange on
  TS's ramp (above).
- House colour: exactly 0,214,0 x (1 + 1.1 grain) on the shoulder pads, arms, hips and thighs; the -trim masks cover
  exactly those.


3D model (ts-e2-hd-3d/)
-----------------------
tse2.glb   the soldier in vertex colours, every sequence as a glTF animation, the mod's camera
- Nodes: {model} > {nodes}.
  Marker "{marker_name}": {marker}.
  Each part is one rigid solid, posed per frame by its node's translation and rotation.
- Animations, facing east (the 8-facing sequences use the east facing's frames; the idles and deaths play facing east
  too), at the game's speed (15 ticks a second); the looping ones end on their first frame again, so they loop without
  a seam:
{anims}
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (30.3 TS px, as the other TS units' models).
  Origin: the soldier's position on the ground.  He faces east (the mod's facing 6).
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 267 x 208 canvas
  exactly (checked by drawing the mesh through it over frame 6: overlap {glb_ov}).
- The file passes Khronos's glTF validator: {glb_val}.
- Vertex colours: COLOR_0 albedo (no light or shadow; the orange parts in TS's mean orange), COLOR_1 house colour
  (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
{calls}


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy, Pillow and cma.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are (TS_HANDOFF: the
folder holding 18-TSE2/ and renderer/).
  inf.py                 the posable soldier (shape S, pose Q) as convex solids;  rc.py  the ray caster
  infunit.py             each unit's own data (E2: the kit, colour classes, sizes, colours, the orange ramp)
  inffit.py              the fit's loss in TS's camera, and the shape + standing fit (e2_shape.json); infsubfit.py
                         the rucksack, the orange patches and the faceplate on their own; infrefine.py  each facing's own arms and head
                         (e2_stand_frames.json); infcalib.py  the colours read off TS's frames
  crawlbio.py            the crawl, a real prone crawl fitted to TS's crawl frames (e2_crawlfit.json,
                         e2_crawl_frames.json); crawlfit.py  which facings TS drew, and the mirror for flipped ones
  infcycle.py            the run, throw and throw lying down as smooth loops: the shared cycle
                         (e2_SEQ_cyc.json), each facing's own loop (e2_SEQ_faces.json) and every frame's pose
                         (e2_SEQ_frames.json)
  infliedown.py          lying down and getting up;  infsmooth.py  the idles and deaths
  infrender.py           an HD frame;  infall.py  all 292 frames with the blood
  infexport.py           the .glb;  infpreview.py  the previews;  infreport.py  the numbers above
  infcheck.py, infmasks.py, infgif.py, hdgrid.py, cyclesheet.py, infshow.py, motion.py   the checks used along the way
  infpackage.py          this package (frames, previews, model, src)
e.g.  python3 infall.py e2 e2_shape.json out/          (every frame; or a list: out/ 8,9,10)
      python3 infcycle.py e2 e2_shape.json fire cyc.json 300            (refit the throw's shared cycle)
"""


README_ENG = """Engineer (TS [ENGINEER]) in HD for Tiberian Factions: TSENGINEER
==================================================================

frames/     tsengineer-0000.png ... tsengineer-0291.png, the mod's 292 frames on its 267 x 208 canvas, each with a
            -trim.png (white = house colour, antialiased), numbered as TS's own sequence (the mod keeps it):
              0-7      standing, one a facing; facings counter-clockwise from north (0 N, 1 NW, 2 W, 3 SW, 4 S, 5 SE,
                       6 E, 7 NE)
              8-55     the run: 6 steps a facing (frame = 8 + facing x 6 + step), 2 ticks a step, looping
              56-70    idle 1 (TS draws it facing south-west);  71-84  idle 2 (facing south-east);  85 (unused) = 84
              86-133   the crawl: 6 steps a facing, looping; its first step is the prone pose
              134-148  death 1 (facing south-west);  149-163  death 2 (facing south-east); both end lying flat
              164-259  fire and fire prone: empty.  He is unarmed: TS's frames there are a single pixel and the
                       game never shows them (the hand-off README)
              260-275  lying down, 2 frames a facing;  276-291  getting up: the same two backwards (TS's are)
previews/   run-8-facings.gif, crawl-8-facings.gif      every facing at once, TS's sprite (as the mod scales it) above
                                  HD
            run-west.gif, run-south.gif, crawl-west.gif, crawl-south.gif
                                  TS's sprite | the mod's frame | HD, at the game's speed
            idle-1.gif, idle-2.gif, death-1.gif, death-2.gif      the same for the one-facing sequences
            lie-down-get-up-W.gif, lie-down-get-up-SE.gif         standing -> down -> prone -> up -> standing
            standing-8-facings.png    TS's sprite, the mod's frame, HD and EA's HD Engineer, each facing
            masks.png                 the head close up in 7 facings: TS, the mod, HD
            shape-run.png, shape-crawl.png    TS's frames as colour classes beside the model's, in TS's own camera
ts-engineer-hd-3d/   the 3D model in its own zip (ts-engineer-hd-3d.zip) next to this folder
src/        the model, its fits, the renderer and the checks (see Rebuilding below)


What it is
----------
The posable soldier of the Light Infantry (inf.py, shared by the six infantry units) with the Engineer's own sizes,
gear and colours (infunit.py), fitted to TS's own ENGINEER frames in TS's camera (silhouette and colour classes, TS's
blood left out) and drawn the way the HD buildings and the other units are.
- His gear, read from TS's frames: a yellow hood with two dark goggle lenses a row above a light grey respirator (TS's
  front view: a dark pixel either side, the respirator 2 px across at the bottom of his face; its side views: the
  respirator at the front edge); a tall yellow pack on his back (TS's back views: yellow from his hood down to a light
  grey belt); a toolbox in his right hand (TS's east view: a yellow box with a light grey lid hanging at his side,
  7 px long and 5 rows tall).  The shoulder pads, upper arms and thighs house green (TS's remap areas); the forearms,
  gloves and shins yellow; the body, hips and boots dark.
- The look (your makeover): the C&C Reborn "GDI Engineer (Old)" you picked, with the hazard-striped case of TS's
  own cameo, its stripes house colour (your note), and off TS's bright yellow onto the Reborn suit's dark ochre (your
  note: "depart from the bright yellow"; the GDI ochre of the HD buildings' collars; inflook_eng.py, its colours
  infunit.MAT_ENG_LOOK2).  The same skeleton, poses and fitted sizes.  The ochre helmet with a glowing visor smaller
  than the soldiers' (your note), grey ear pieces, a low ridge and a short whip antenna; the flat box pack with dark
  edging, a round gauge and a slot; a segmented ochre chest on the dark suit, a dark belt with a light grey buckle;
  dark shoulder plates with house-green hazard stripes, ochre plates under them; green upper arms and thighs (TS's
  remap areas, so he shows his side as TS's does); ochre gauntlets, dark gloves; ochre knee pads and boot covers with
  light grey shin guards, dark boots; the dark case with house-green stripes on both faces, a light grey lid band and
  handle.  The goggles, respirator and bright yellow below are TS's sprite as the fit read it, kept for the record.
- His suit is bulkier than the soldiers' armour: the fit has room for wider hips and a bigger hood and body.  TS drew
  its sprites on black, so the edge pixels of a bright part come out dark; the fit counts the soldier's own edge
  pixels as dark, as TS's are, and his yellow parts are fitted to TS's yellow inside them.
- The shape is fitted to the 8 standing frames together, then the respirator and goggles on their own, then each
  facing's arms and head to its own frame.  Overlap with TS's frames in TS's camera: {ts_stand:.2f}.
- The yellow is drawn on TS's own yellow ramp (its frames' ten yellows, orange-yellow to pale yellow), each part as
  light on average as TS draws it: the HD light (the buildings', from the north-west) leaves much of him in shadow,
  where a plain yellow went olive.
- The run is one smooth loop: every joint follows a short smooth curve (a Fourier series) through the 6 steps, so
  step 5 runs into step 0 like any step into the next and nothing jumps back to a start pose.  It is a sprint, as
  TS draws it (its side views, frames 20-25 and 44-49: the trailing leg thrown back level behind the hip, one leg then
  the other, the front foot reaching well ahead): the legs follow one curve half a cycle apart; the left arm swings
  against them, the right carries the toolbox with a short swing.  The loop is fitted to TS's 48 run frames together;
  each facing's arms and head then get their own smooth loop on top, held close to the shared one.  Overlap
  {ts_walk:.2f}; the furthest any landmark (hands, head, feet) moves from one step to the next is {mo_walk:.1f} TS px.
- The crawl is rebuilt from TS's own crawl frames (your notes: "view how og is doing it", "research how a body crawls
  prone"). It is a real prone crawl, done the way the army's low crawl and the leopard crawl are: flat and low on his
  front, up on his forearms with his head up to see. One forearm goes forward with the opposite knee, which is drawn
  up while the other leg lies straight back, and his body rolls a little towards that knee; then the other pair. TS
  drew this crawl only facing N, NW, W, SW and S, and its NE, E and SE crawl frames are those sprites flipped, pixel
  for pixel. One pose can't match both sides, which is what made the earlier crawls flail, so the crawl is fitted to
  the five facings TS drew and the flipped facings get the same pose mirrored, as TS's do. The toolbox stays in his
  right hand, standing on the ground square to him, and only moves when his hand does. One stroke drives every joint,
  so the loop runs on with nothing jumping back. How far he is propped up, where he looks and how far each part moves
  are fitted to TS's crawl frames. Overlap {ts_crawl:.2f}, landmarks at most {mo_crawl:.1f} TS px a step.
  On the infantry's new skeleton (as the Light Infantry's): a two-piece spine, so the body curves; shoulders that reach
  and hips that hitch with the stroke. His body was fitted step by step to TS's crawl, then calmed: the movement at half
  the fit, and the sideways movements (roll, side bend, twist, the hip turn) centred, so he lies flat and square. (His
  hood pulled the fit over onto one side; drawn at the Light Infantry's x1.5 he heaved half on his side.) His free arms
  reach out in front in turn, hands ahead of his shoulders, his arms narrowing to a round elbow.
- Lying down: the two in-betweens fitted to TS's frames on the way down through kneeling on all fours (TS's second
  frame), from the standing pose to the prone one (the crawl's first step), so standing, down and prone run as one movement ({ts_lie:.2f}); getting up is the same two
  poses backwards, as TS's get-up frames are its lie-down frames backwards, pixel for pixel.
- The idles and deaths: each frame fitted to its TS frame starting from the one before, then the whole run of poses
  relaxed together (every frame pulled towards the middle of its neighbours), so they move smoothly; the idles start
  from the standing pose and come back to it.  Overlap: idles {ts_idle1:.2f} and {ts_idle2:.2f}, deaths {ts_death1:.2f} and {ts_death2:.2f}.
- The blood, frame by frame from TS's own pixels: TS's red (255,0,0, as TS and the mod draw it), each red pixel drawn on
  the ground it covers in TS's view, so a pool stays put as the body falls on it.
Against the mod's current frames the silhouettes overlap by {mod_all:.2f} (standing {mod_stand:.2f}, run {mod_walk:.2f}, crawl {mod_crawl:.2f}): those frames
are TS's sprites scaled up 3.0755 times, so this is the difference in TS's own camera above, scaled up with them (a
soldier's limbs are a few TS pixels wide, so a pixel counts for a lot), plus the 32-degree camera.


Keep (from the hand-off README)
-------------------------------
- The 267 x 208 canvas; every frame of the layout in TS's order (85, unused, and the empty fire frames included).
- The feet: the soldier's ground point lands where the mod's frames put TS's (TS's sprite x 3.0755 at (37.91, 10.46));
  standing, the boots' lowest pixel is on canvas row {feet_lo}-{feet_hi} by facing, as the mod's own frames have it
  on {mfeet_lo}-{mfeet_hi} (the README: feet on 111).
- He stands as tall as EA's Engineer (65 px on average over his 8 standing facings; your note: the infantry must
  match TD's and RA's sizes; see standing-8-facings.png).
- The shadow baked in at alpha 128 (50% black, blurred): the README's minimum, lighter than the buildings' 75%, as
  the mod's frames carry TS's at about 25% (your note: at 75% the falling deaths looked like floating).


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 3.0755 canvas px per TS pixel
  (the mod's frames are TS's sprite x 3.0755), the soldier drawn at EA's Engineer's height about his feet.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the units' camera fill (EA's HD
  infantry are lit from the front); each part as light as TS draws it under that light (infcalib.py), the yellow on
  TS's ramp (above).
- House colour: exactly 0,214,0 x (1 + 1.1 grain) on the shoulder pads, upper arms and thighs; the -trim masks cover
  exactly those.


3D model (ts-engineer-hd-3d/)
-----------------------------
tsengineer.glb   the soldier in vertex colours, every sequence as a glTF animation, the mod's camera
- Nodes: {model} > {nodes}.
  Each part is one rigid solid, posed per frame by its node's translation and rotation; the toolbox and its lid
  are posed with his right hand.
- Animations, facing east (the 8-facing sequences use the east facing's frames; the idles and deaths play facing east
  too), at the game's speed (15 ticks a second); the looping ones end on their first frame again, so they loop without
  a seam (no fire animations: he has none):
{anims}
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (30.3 TS px, as the other TS units' models).
  Origin: the soldier's position on the ground.  He faces east (the mod's facing 6).
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 267 x 208 canvas
  exactly (checked by drawing the mesh through it over frame 6: overlap {glb_ov}).
- The file passes Khronos's glTF validator: {glb_val}.
- Vertex colours: COLOR_0 albedo (no light or shadow; the yellow parts in TS's mean yellows), COLOR_1 house colour
  (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
{calls}


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy, Pillow and cma.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are (TS_HANDOFF: the
folder holding 19-TSENGINEER/ and renderer/).
  inf.py                 the posable soldier (shape S, pose Q) as convex solids;  rc.py  the ray caster
  infunit.py             each unit's own data (the Engineer: his kit, colour classes, sizes, colours, the yellow ramp)
  inffit.py              the fit's loss in TS's camera, and the shape + standing fit (eng_shape.json); infsubfit.py
                         the respirator and goggles on their own; infrefine.py  each facing's own arms and head
                         (eng_stand_frames.json); infcalib.py  the colours read off TS's frames
  infcycle.py            the run as a smooth loop: the shared cycle (eng_walk_cyc.json), each facing's own loop
                         (eng_walk_faces.json) and every frame's pose (eng_walk_frames.json)
  crawlbio.py            the crawl, a real prone crawl fitted to TS's crawl frames (eng_crawlfit.json,
                         eng_crawl_frames.json); crawlfit.py  which facings TS drew, and the mirror for flipped ones
  infliedown.py          lying down and getting up;  infsmooth.py  the idles and deaths
  infrender.py           an HD frame;  infall.py  all 292 frames with the blood (and the empty fire frames)
  infexport.py           the .glb;  infpreview.py  the previews;  infreport.py  the numbers above
  infcheck.py, infmasks.py, infgif.py, hdgrid.py, cyclesheet.py, infshow.py, motion.py   the checks used along the way
  infpackage.py          this package (frames, previews, model, src)
e.g.  python3 infall.py eng eng_shape.json out/          (every frame; or a list: out/ 8,9,10)
"""


README_GHOST = """Ghost Stalker (TS [GHOST]) in HD for Tiberian Factions: TSGHOST
==============================================================

frames/     tsghost-0000.png ... tsghost-0291.png, the mod's 292 frames on its 267 x 208 canvas, each with a -trim.png
            (white = house colour, antialiased), numbered as TS's own sequence (the mod keeps it):
              0-7      standing, one a facing; facings counter-clockwise from north (0 N, 1 NW, 2 W, 3 SW, 4 S, 5 SE,
                       6 E, 7 NE)
              8-55     the run: 6 steps a facing (frame = 8 + facing x 6 + step), 2 ticks a step, looping
              56-70    idle 1 (TS draws it facing south-west);  71-84  idle 2 (facing south-east);  85 (unused) = 84
              86-133   the crawl: 6 steps a facing, looping; its first step is the prone pose
              134-148  death 1 (facing south-west);  149-163  death 2 (facing south-east); both end lying flat
              164-211  fire: 6 frames a facing, 1 tick a frame, the railgun's flash on every other frame, as TS's
              212-259  fire prone, the same
              260-275  lying down, 2 frames a facing;  276-291  getting up: the same two backwards (TS's are)
previews/   run-8-facings.gif, crawl-8-facings.gif, fire-8-facings.gif, fire-prone-8-facings.gif
                                  every facing at once, TS's sprite (as the mod scales it) above HD
            run-west.gif, run-south.gif, crawl-west.gif, crawl-south.gif, fire-west.gif, fire-south.gif
                                  TS's sprite | the mod's frame | HD, at the game's speed
            idle-1.gif, idle-2.gif, death-1.gif, death-2.gif      the same for the one-facing sequences
            lie-down-get-up-W.gif, lie-down-get-up-SE.gif         standing -> down -> prone -> up -> standing
            standing-8-facings.png    TS's sprite, the mod's frame, HD and EA's HD Commando, each facing
            masks.png                 the head close up in 8 facings: TS, the mod, HD
            shape-run.png, shape-crawl.png    TS's frames as colour classes beside the model's, in TS's own camera
ts-ghost-hd-3d/   the 3D model in its own zip (ts-ghost-hd-3d.zip) next to this folder
src/        the model, its fits, the renderer and the checks (see Rebuilding below)


What it is
----------
The posable soldier of the Light Infantry (inf.py, shared by the six infantry units) with the Ghost Stalker's own
sizes, gear and colours (infunit.py), fitted to TS's own GHOST frames in TS's camera (silhouette and colour classes,
TS's flash and blood left out) and drawn the way the HD buildings and the other units are.
- His head, read from TS's frames: a blue-grey hood over the top and back of his head, his bare face in front of it
  (TS's front view: the face 2 px across and 2 rows tall under two rows of blue-grey, blue-grey either side of it;
  its side views: the face the front half of his head).  The hood is the head's box behind the face and above the
  brow; the face is the box's front below the brow, narrower than the hood and standing a little proud of it.
- Across his upper back at his head's height, a roll (TS: a dark band behind his head in every facing, 9-10 px
  across in the front and back views, wider than his shoulders, 2 rows thick, a light grey pixel a pixel in from
  either end; from the side its end just behind his head): near-black, its ends light grey.
- The railgun, as long as TS draws it (6-7 px out past his body in the north-west and south-east views), held at his
  hip pointing ahead and down, in house green as TS's is.  His shoulder pads house green too: those are TS's only remap
  areas.  His top is TS's olive and natural greens (not remap colours), so it is a dark olive green, not house colour;
  his arms are bare (TS's flesh tones), his trousers and boots near-black with grey at the knees.
- His skin is drawn on TS's own flesh ramp (its sixteen tones, dark red-brown to light pink), each part as light on
  average as TS draws it: the face lightest, the forearms darkest, as TS's are.
- Standing: one pose fitted to the 8 standing frames together (TS draws him in a wide stance with his knees bent),
  then each facing's arms, railgun and head to its own frame (TS holds the railgun a different way in every facing).
  Overlap with TS's frames in TS's camera: {ts_stand:.2f}.
- The run is one smooth loop: every joint follows a short smooth curve (a Fourier series) through the 6 steps, so
  step 5 runs into step 0 like any step into the next and nothing jumps back to a start pose (your note on the
  soldiers' run).  The loop is fitted to TS's 48 run frames together; each facing's arms, railgun and head then get
  their own smooth loop on top, held close to the shared one.  Overlap {ts_walk:.2f}; the furthest any landmark (muzzle,
  railgun's back end, hands, head, feet) moves from one step to the next is {mo_walk:.1f} TS px.
- The crawl is rebuilt from TS's own crawl frames (your notes: "view how og is doing it", "research how a body crawls
  prone"). It is a real prone crawl, done the way the army's low crawl and the leopard crawl are: flat and low on his
  front, up on his forearms with his head up to see. One forearm goes forward with the opposite knee, which is drawn
  up while the other leg lies straight back, and his body rolls a little towards that knee; then the other pair. TS
  drew it in all 8 facings, and all 8 are fitted together. The railgun goes forward in both hands with each stroke
  and draws back. One stroke drives every joint, so the loop runs on with nothing jumping back. How far he is propped
  up, where he looks and how far each part moves are fitted to TS's crawl frames. Overlap {ts_crawl:.2f}, landmarks
  at most {mo_crawl:.1f} TS px a step.
- Fire and fire prone: TS holds one pose through each facing's 6 frames (only the flash comes and goes), so each
  facing has one pose for all 6: fitted to the 8 facings' flash-free frames together, then each facing's arms, railgun
  and head to its own.  Overlap {ts_fire:.2f} and {ts_prone:.2f}.
- Lying down: the two in-betweens fitted to TS's frames on the way down through kneeling on all fours (TS's second
  frame), from the standing pose to the prone one (the crawl's first step), so standing, down and prone run as one movement ({ts_lie:.2f}); getting up is the same two
  poses backwards, as TS's get-up frames are its lie-down frames backwards, pixel for pixel.
- The idles and deaths: each frame fitted to its TS frame starting from the one before, then the whole run of poses
  relaxed together (every frame pulled towards the middle of its neighbours), so they move smoothly; the idles start
  from the standing pose and come back to it.  Overlap: idles {ts_idle1:.2f} and {ts_idle2:.2f}, deaths {ts_death1:.2f} and {ts_death2:.2f}.
- The railgun in the deaths follows TS's: TS keeps it in plain view as he falls (flung up over his head, then lying
  out beside him; in death 2 swung out in one hand while the other arm flies up), so from the first falling frame
  it is in his right hand alone, his left arm free, and each frame also starts from the railgun laid along TS's own
  (the longest straight run of its green pixels in that frame); the frames are held together less tightly for the
  gun and his right arm than for his body, so it can swing as far as TS's does from one frame to the next.
- Effects, frame by frame from TS's own pixels: the railgun's flash (TS's yellows, its shape kept, drawn smooth and
  hot: a white-yellow core, amber, orange edges) at the HD railgun's muzzle, hidden where he stands in front of it;
  the blood in TS's red (255,0,0, as TS and the mod draw it), each red pixel drawn on the ground it covers in TS's
  view, so a pool stays put as the body falls on it.
Against the mod's current frames the silhouettes overlap by {mod_all:.2f} (standing {mod_stand:.2f}, run {mod_walk:.2f}, crawl {mod_crawl:.2f}, fire
{mod_fire:.2f}): those frames are TS's sprites scaled up 3.0769 times, so this is the difference in TS's own camera above,
scaled up with them (a soldier's limbs are a few TS pixels wide, so a pixel counts for a lot), plus the 32-degree camera.


Keep (from the hand-off README)
-------------------------------
- The 267 x 208 canvas; every frame of the layout in TS's order (85, unused, included).
- The feet: the soldier's ground point lands where the mod's frames put TS's (TS's sprite x 3.0769 at (37.70, 10.86));
  standing, the boots' lowest pixel is on canvas row {feet_lo}-{feet_hi} by facing, as the mod's own frames have it
  on {mfeet_lo}-{mfeet_hi} (the README: feet on 111).
- He stands as tall as the mod's frames (EA's Commando: see standing-8-facings.png).
- The shadow baked in at alpha 128 (50% black, blurred): the README's minimum, lighter than the buildings' 75%, as
  the mod's frames carry TS's at about 25% (your note: at 75% the falling deaths looked like floating).
- The bright yellow flash on every other fire frame, standing and prone, where TS has it, and nothing else in those
  frames as bright (his skin, the house green and the roll's grey ends are all well off it), so the muzzle can be
  measured from it.


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 3.0769 canvas px per TS pixel
  (the mod's frames are TS's sprite x 3.0769), the soldier drawn 8% bigger about his feet, as E1.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the units' camera fill (EA's HD
  infantry are lit from the front); each part as light as TS draws it under that light (infcalib.py), the skin on
  TS's ramp (above).
- House colour: exactly 0,214,0 x (1 + 1.1 grain) on the shoulder pads and the railgun; the -trim masks cover exactly
  those.


3D model (ts-ghost-hd-3d/)
--------------------------
tsghost.glb   the soldier in vertex colours, every sequence as a glTF animation, the mod's camera
- Nodes: {model} > {nodes}.
  {marker_line}Each part is one rigid solid, posed per frame by its node's translation and rotation.
- Animations, facing east (the 8-facing sequences use the east facing's frames; the idles and deaths play facing east
  too), at the game's speed (15 ticks a second); the looping ones end on their first frame again, so they loop without
  a seam:
{anims}
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (30.3 TS px, as the other TS units' models).
  Origin: the soldier's position on the ground.  He faces east (the mod's facing 6).
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 267 x 208 canvas
  exactly (checked by drawing the mesh through it over frame 6: overlap {glb_ov}).
- The file passes Khronos's glTF validator: {glb_val}.
- Vertex colours: COLOR_0 albedo (no light or shadow; the skin in TS's mean flesh tones), COLOR_1 house colour
  (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
{calls}


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy, Pillow and cma.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are (TS_HANDOFF: the
folder holding 20-TSGHOST/ and renderer/).
  inf.py                 the posable soldier (shape S, pose Q) as convex solids (the Ghost's hood, face and roll:
                         kit 'ghost');  rc.py  the ray caster
  infunit.py             each unit's own data (the Ghost: his kit, colour classes, sizes, colours, the flesh ramp)
  inffit.py              the fit's loss in TS's camera, and the shape + standing fit (ghost_shape.json); infsubfit.py
                         the hood, face and roll on their own; infrefine.py  each facing's own arms, railgun and head
                         (ghost_stand_frames.json); infcalib.py  the colours read off TS's frames
  infcycle.py            the run as a smooth loop: the shared cycle (ghost_walk_cyc.json), each facing's own loop
                         (ghost_walk_faces.json) and every frame's pose (ghost_walk_frames.json)
  crawlbio.py            the crawl, a real prone crawl fitted to TS's crawl frames (ghost_crawlfit.json,
                         ghost_crawl_frames.json); crawlfit.py  which facings TS drew
  infstatic.py           fire and fire prone, one pose a facing (ghost_fire_pose.json, ghost_fire_frames.json, ...)
  infliedown.py          lying down and getting up;  infsmooth.py  the idles and deaths
  infrender.py           an HD frame;  infx.py  the flash;  infall.py  all 292 frames with flash and blood
  infexport.py           the .glb;  infpreview.py  the previews;  infreport.py  the numbers above
  infcheck.py, infmasks.py, infgif.py, hdgrid.py, cyclesheet.py, infshow.py, motion.py   the checks used along the way
  infpackage.py          this package (frames, previews, model, src)
e.g.  python3 infall.py ghost ghost_shape.json out/          (every frame; or a list: out/ 8,9,10)
"""

README_JJ = """Jumpjet Infantry (TS [JUMPJET]) in HD for Tiberian Factions: TSJUMPJET
=====================================================================

frames/     tsjumpjet-0000.png ... tsjumpjet-0450.png, the mod's 451 frames on its 267 x 208 canvas, each with a
            -trim.png (white = house colour, antialiased), numbered as TS's own sequence (the mod keeps it):
              0-7      standing, one a facing; facings counter-clockwise from north (0 N, 1 NW, 2 W, 3 SW, 4 S, 5 SE,
                       6 E, 7 NE)
              8-55     the run: 6 steps a facing (frame = 8 + facing x 6 + step), 2 ticks a step, looping
              56-70    idle 1 (TS draws it facing south-west);  71-85  idle 2 (facing south-east; 85 its last frame)
              86-133   the crawl: his run frames (8-55), as TS's are - he doesn't lie down in TS
              134-163  deaths: empty, as TS's are (he dies by the tumble, 436-450)
              164-211  fire: 6 frames a facing, 1 tick a frame, the muzzle flash where TS has it
              212-259  fire prone: his fire frames (164-211), as TS's are
              260-291  lying down and getting up: his standing frame in each facing, as TS's are
              292-339  flying: 6 frames a facing      340-387  hovering: 6 a facing
              388-435  firing in the air: 6 a facing  436-450  the tumble (15, drawn once; the game doesn't show it)
            The flight frames (292-450) stand his feet on the same ground point as the standing frames (not lifted)
            and have no shadow: the game lifts the frame by his height and draws his shadow from it.
previews/   run-8-facings.gif, crawl-8-facings.gif, fire-8-facings.gif, fire-prone-8-facings.gif, fly-8-facings.gif,
            hover-8-facings.gif, fire-fly-8-facings.gif     every facing at once, TS's sprite above HD
            run-west.gif, run-south.gif, crawl-west.gif, crawl-south.gif, fire-west.gif, fire-south.gif, fly-west.gif,
            fly-south.gif, fire-fly-west.gif, hover-south.gif      TS's sprite | the mod's frame | HD, at the game's speed
            idle-1.gif, idle-2.gif, tumble.gif      the same for the one-facing sequences
            lie-down-get-up-W.gif, lie-down-get-up-SE.gif         standing -> down -> prone -> up -> standing
            standing-8-facings.png    TS's sprite, the mod's frame, HD and EA's HD Minigunner, each facing
            masks.png                 the helmet and visor close up in 8 facings: TS, the mod, HD
            shape-run.png, shape-crawl.png    TS's frames as colour classes beside the model's, in TS's own camera
ts-jumpjet-hd-3d/   the 3D model in its own zip (ts-jumpjet-hd-3d.zip) next to this folder
src/        the model, its fits, the renderer and the checks (see Rebuilding below)


What it is
----------
The posable soldier of the Light Infantry (inf.py, shared by the six infantry units) with the Jumpjet's own sizes,
gear and colours (infunit.py), fitted to TS's own JUMPJET frames in TS's camera (silhouette and colour classes, TS's
flames, flashes and blood left out) and drawn the way the HD buildings and the other units are.
- His gear, read from TS's frames: a jetpack on his back (TS's back view: a grey column from his shoulders to his
  hips, a light grey nozzle either side of its lower half); two wings from the jetpack's upper sides, swept back and
  set up a little (TS: house green, spread wide behind him in every facing, as broad seen from behind as from the
  side); a dark grey helmet with the soldiers' light-blue visor; grey armour; the legs house green; a black rifle.
  House colour on the wings, thighs, knees and shins (TS's remap areas).
- The shape is fitted to the 8 standing frames together, the wings again round the jetpack, then each facing's arms,
  rifle and head to its own frame.  TS draws him with his chest turned about 20 degrees to his right in every facing
  (the wings sit higher on one side in its front and back views); the fit has that too.  Overlap with TS's frames in
  TS's camera: {ts_stand:.2f}.
- The wings stand 6-8 px higher than TS's in four facings (SW, SE, E, NE): you liked them as they are (4 Oct), so
  they stay.
- The run is one smooth loop (every joint on a short smooth curve through the 6 steps, nothing jumps back to a start
  pose), fitted to TS's 48 run frames together, each facing's arms, rifle and head on their own smooth loop on top.
  Overlap {ts_walk:.2f}; the furthest any landmark moves from one step to the next is {mo_walk:.1f} TS px.
- TS never lays the Jumpjet down. His crawl frames are his run frames, his fire-prone frames are his fire frames, and
  his lying-down and getting-up frames are his standing frames, pixel for pixel. HD does the same: 86-133 are the
  run, 212-259 the fire and 260-291 his standing pose in each facing.
- Fire and fire prone: TS holds one pose through each facing's 6 frames (only the flash comes and goes), so each
  facing has one pose for all 6.  Overlap {ts_fire:.2f} and {ts_prone:.2f}.
- Flying: TS holds one pose a facing through its 6 flying frames, leaning into the flight, only the jet flames
  changing; so does HD: fitted to the 8 facings together, then each facing's arms, rifle and head.  Overlap {ts_fly:.2f}.
  Hovering is TS's standing pose with the jets lit ({ts_hover:.2f}); firing in the air the flying pose firing ({ts_fire_fly:.2f}).
- The jet flames, frame by frame from TS's own pixels (its three flame yellows), drawn smooth and hot (a white-yellow
  core, amber, orange edges) at the HD nozzles, hidden where he is in front of them; firing in the air, the pixels
  nearer his rifle than his nozzles are the muzzle flash, drawn at the muzzle.  The muzzle flash keeps TS's red tips.
- The tumble: hit in the air, he tumbles and falls, ending on the ground in TS's blood; each frame fitted to its TS
  frame from the one before, then the run of poses relaxed together ({ts_tumble:.2f}).
- The idles: as the other infantry ({ts_idle1:.2f} and {ts_idle2:.2f}).
Against the mod's current frames the silhouettes overlap by {mod_all:.2f} (standing {mod_stand:.2f}, run {mod_walk:.2f}, crawl {mod_crawl:.2f}, fire
{mod_fire:.2f}): those frames are TS's sprites scaled up 3.116 times, so this is the difference in TS's own camera above,
scaled up with them, plus the 32-degree camera.


Keep (from the hand-off README)
-------------------------------
- The 267 x 208 canvas; every frame of the layout in TS's order (the empty deaths and the tumble included).
- The feet: the soldier's ground point lands where the mod's frames put TS's (TS's sprite x 3.116 at (36.93, 9.54));
  standing, the boots' lowest pixel is on canvas row {feet_lo}-{feet_hi} by facing, as the mod's own frames have it
  on {mfeet_lo}-{mfeet_hi} (the README: feet on 111).
- The flight frames with his feet on the same ground point and no shadow.
- He stands as tall as the mod's frames (EA's Minigunner: see standing-8-facings.png).
- The shadow baked in at alpha 128 (50% black, blurred): the README's minimum, lighter than the buildings' 75%, as
  the mod's frames carry TS's at about 25% (your note: at 75% the falling deaths looked like floating), on the ground
  frames.


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 3.116 canvas px per TS pixel
  (the mod's frames are TS's sprite x 3.116), the soldier drawn 8% bigger about his feet, as E1.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the units' camera fill; each part
  as light as TS draws it under that light (infcalib.py).
- House colour: exactly 0,214,0 x (1 + 1.1 grain) on the wings, thighs, knees and shins; the -trim masks cover exactly
  those (the flames over them left out).


3D model (ts-jumpjet-hd-3d/)
----------------------------
tsjumpjet.glb   the soldier in vertex colours, every sequence as a glTF animation (the flight ones too), the mod's camera
- Nodes: {model} > {nodes}.
  {marker_line}Markers "nozzle_left", "nozzle_right": the jets' mouths, where the flames come out.
  Each part is one rigid solid, posed per frame by its node's translation and rotation.
- Animations, facing east (the 8-facing sequences use the east facing's frames; the idles and the tumble play facing
  east too), at the game's speed (15 ticks a second); the looping ones end on their first frame again:
{anims}
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (30.3 TS px, as the other TS units' models).
  Origin: the soldier's position on the ground.  He faces east (the mod's facing 6).
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 267 x 208 canvas
  exactly (checked by drawing the mesh through it over frame 6: overlap {glb_ov}).
- The file passes Khronos's glTF validator: {glb_val}.
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
{calls}


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy, Pillow and cma.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are (TS_HANDOFF: the
folder holding 21-TSJUMPJET/ and renderer/).
  inf.py                 the posable soldier (shape S, pose Q) as convex solids (the Jumpjet's jetpack, nozzles and
                         wings: kit 'jj');  rc.py  the ray caster
  infunit.py             each unit's own data (the Jumpjet: his kit, colour classes, sizes, colours)
  inffit.py              the fit's loss in TS's camera, and the shape + standing fit (jj_shape.json); infsubfit.py
                         the wings on their own; infrefine.py  each facing's own arms, rifle and head (jj_stand_frames.json)
  infcycle.py            the run as a smooth loop (jj_walk_cyc.json, jj_walk_faces.json, jj_walk_frames.json)
  infstatic.py           fire, fire prone, flying and firing in the air, one pose a facing (jj_SEQ_pose.json,
                         jj_SEQ_frames.json)
  infliedown.py          lying down and getting up;  infsmooth.py  the idles and the tumble
  infrender.py           an HD frame;  infx.py  the flames and flashes;  infall.py  all 451 frames with flames, flash
                         and blood (no shadow in the air)
  infexport.py           the .glb;  infpreview.py  the previews;  infreport.py  the numbers above
  infcheck.py, infmasks.py, infgif.py, hdgrid.py, cyclesheet.py, infshow.py, motion.py   the checks used along the way
  infpackage.py          this package (frames, previews, model, src)
e.g.  python3 infall.py jj jj_shape.json out/          (every frame; or a list: out/ 8,9,10)
"""

README_MEDIC = """Medic (TS [MEDIC]) in HD for Tiberian Factions: TSMEDIC
=======================================================

frames/     tsmedic-0000.png ... tsmedic-0306.png, the mod's 307 frames on its 267 x 208 canvas, each with a -trim.png
            (white = house colour, antialiased), numbered as TS's own sequence (the mod keeps it):
              0-7      standing, one a facing; facings counter-clockwise from north (0 N, 1 NW, 2 W, 3 SW, 4 S, 5 SE,
                       6 E, 7 NE)
              8-55     the run: 6 steps a facing (frame = 8 + facing x 6 + step), 2 ticks a step, looping
              56-70    idle 1 (TS draws it facing south-west);  71-84  idle 2 (facing south-east);  85 (unused by
                       the game): TS's own frame 85, him taking his case up again
              86-133   the crawl: 6 steps a facing, looping; its first step is the prone pose
              134-148  death 1;  149-163  death 2; both end lying flat
              164-259  fire and fire prone: empty.  He is unarmed: TS's frames there are empty and his fire is the heal
              260-275  lying down, 2 frames a facing;  276-291  getting up: the same two backwards (TS's are)
              292-306  the heal: one strip whatever the facing (TS draws it facing south-east), 2 ticks a frame
previews/   run-8-facings.gif, crawl-8-facings.gif      every facing at once, TS's sprite (as the mod scales it) above
                                  HD
            run-west.gif, run-south.gif, crawl-west.gif, crawl-south.gif
                                  TS's sprite | the mod's frame | HD, at the game's speed
            heal.gif, idle-1.gif, idle-2.gif, death-1.gif, death-2.gif      the same for the one-facing sequences
            lie-down-get-up-W.gif, lie-down-get-up-SE.gif         standing -> down -> prone -> up -> standing
            standing-8-facings.png    TS's sprite, the mod's frame, HD and EA's HD Field Medic, each facing
            masks.png                 the head close up in 8 facings: TS, the mod, HD
            shape-run.png, shape-crawl.png    TS's frames as colour classes beside the model's, in TS's own camera
ts-medic-hd-3d/   the 3D model in its own zip (ts-medic-hd-3d.zip) next to this folder
src/        the model, its fits, the renderer and the checks (see Rebuilding below)


What it is
----------
The posable soldier of the Light Infantry (inf.py, shared by the six infantry units) with the Medic's own sizes,
gear and colours (infunit.py), fitted to TS's own MEDIC frames in TS's camera (silhouette and colour classes, the red
crosses and blood left out) and drawn the way the HD buildings and the other units are.
- His gear, read from TS's frames: a grey helmet with a red cross on its crown and a dark glass faceplate; grey
  armour, darker at the front; house green shoulder pads and thigh fronts (TS's remap areas); orange armbands and knee
  pads; his hips and the backs of his thighs orange (TS's back views: orange across the hips and down both thighs;
  its front view: green thighs, orange knees); a grey medical case in his right hand (TS's south and east views: a
  grey box at his side) with a red cross on each broad face; a red cross on his upper back (TS's back view: 3 x 3 px
  between the shoulder blades).  The crosses are TS's pure red, painted flat (lit only a little, as TS draws them
  bright).
- The helmet's cross: TS draws its red blurred into the helmet's grey (flesh-coloured pixels, as round his other
  crosses' edges) on the crown in every facing, standing, running and crawling; it goes edge-on and out of sight when
  he lies on his back and shows more as he bends over to heal, so it lies flat on the crown.
- The faceplate: TS draws it dark grey looking ahead and blue-grey lying face up, so it is dark glass that shows the
  sky as it turns up.
- The orange is drawn on TS's own orange ramp, as E2's.
- Standing: one pose fitted to the 8 standing frames together, then each facing's arms and head to its own frame.
  Overlap with TS's frames in TS's camera: {ts_stand:.2f}.
- The run is one smooth loop (every joint on a short smooth curve through the 6 steps, nothing jumps back to a start
  pose), fitted to TS's 48 run frames together, each facing's arms and head on their own smooth loop on top.  Overlap
  {ts_walk:.2f}; the furthest any landmark moves from one step to the next is {mo_walk:.1f} TS px.
- The crawl is rebuilt from TS's own crawl frames (your notes: "view how og is doing it", "research how a body crawls
  prone"). It is a real prone crawl, done the way the army's low crawl and the leopard crawl are: flat and low on his
  front, up on his forearms with his head up to see. One forearm goes forward with the opposite knee, which is drawn
  up while the other leg lies straight back, and his body rolls a little towards that knee; then the other pair. TS
  drew this crawl only facing N, NW, W, SW and S, and its NE, E and SE crawl frames are those sprites flipped, pixel
  for pixel. One pose can't match both sides, which is what made the earlier crawls flail, so the crawl is fitted to
  the five facings TS drew and the flipped facings get the same pose mirrored, as TS's do. The case stays in his
  right hand, standing on the ground square to him, and only moves when his hand does (lying down and getting up
  carry it from his hand to the ground and back). One stroke drives every joint, so the loop runs on with nothing
  jumping back. How far he is propped up, where he looks and how far each part moves are fitted to TS's crawl frames.
  Overlap {ts_crawl:.2f}, landmarks at most {mo_crawl:.1f} TS px a step.
- The heal: each frame fitted to its TS frame starting from the one before, then the whole run of poses relaxed
  together, starting and ending on his standing pose facing south-east, as TS's does ({ts_heal:.2f}).
- His case: in his hand standing, running and in idle 1 (TS: he turns it to look at it); upright on the ground ahead
  of his hand as he crawls, pushed along; set down beside him for idle 2 and the heal and taken up again at the end
  (TS: frames 72-84 and 294-304 it stands still on the ground, its cross to the camera); dropped in the deaths, where
  it then stays (death 1 from frame 137, death 2 from 156).  Where it stands is read off TS's frames: the model's case
  and its cross put where TS's cross is in every one of those frames (casespot.py).
- Lying down, getting up, the idles and deaths: as the other infantry ({ts_lie:.2f}; idles {ts_idle1:.2f} and
  {ts_idle2:.2f}, deaths {ts_death1:.2f} and {ts_death2:.2f}).
- The blood in TS's red (255,0,0), each red pixel drawn on the ground it covers in TS's view.  TS's crosses are the
  same red: red where the fitted soldier shows a cross, his case or his back is the cross (drawn by the model), the
  rest is blood.
Against the mod's current frames the silhouettes overlap by {mod_all:.2f} (standing {mod_stand:.2f}, run {mod_walk:.2f}, crawl {mod_crawl:.2f}): those frames
are TS's sprites scaled up 3.085 times, so this is the difference in TS's own camera above, scaled up with them, plus
the 32-degree camera.


Keep (from the hand-off README)
-------------------------------
- The 267 x 208 canvas; every frame of the layout in TS's order (85, unused, and the empty fire frames included).
- The feet: the soldier's ground point lands where the mod's frames put TS's (TS's sprite x 3.085 at (37.53, 11.06));
  standing, the boots' lowest pixel is on canvas row {feet_lo}-{feet_hi} by facing, as the mod's own frames have it
  on {mfeet_lo}-{mfeet_hi} (the README: feet on 111).
- The heal strip at 292-306.
- He stands as tall as the mod's frames (EA's Field Medic: see standing-8-facings.png).
- The shadow baked in at alpha 128 (50% black, blurred): the README's minimum, lighter than the buildings' 75%, as
  the mod's frames carry TS's at about 25% (your note: at 75% the falling deaths looked like floating).


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 3.085 canvas px per TS pixel
  (the mod's frames are TS's sprite x 3.085), the soldier drawn 8% bigger about his feet, as E1.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the units' camera fill; each part
  as light as TS draws it under that light (infcalib.py).
- House colour: exactly 0,214,0 x (1 + 1.1 grain) on the shoulder pads and thighs; the -trim masks cover exactly those.


3D model (ts-medic-hd-3d/)
--------------------------
tsmedic.glb   the soldier in vertex colours, every sequence as a glTF animation (the heal too), the mod's camera
- Nodes: {model} > {nodes}.
  Each part is one rigid solid, posed per frame by its node's translation and rotation; the case and its crosses are
  posed with his right hand.
- Animations, facing east (the 8-facing sequences use the east facing's frames; the idles, deaths and the heal play
  facing east too), at the game's speed (15 ticks a second); the looping ones end on their first frame again (no fire
  animations: he has none):
{anims}
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (30.3 TS px, as the other TS units' models).
  Origin: the soldier's position on the ground.  He faces east (the mod's facing 6).
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 267 x 208 canvas
  exactly (checked by drawing the mesh through it over frame 6: overlap {glb_ov}).
- The file passes Khronos's glTF validator: {glb_val}.
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
{calls}


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy, Pillow and cma.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are (TS_HANDOFF: the
folder holding 22-TSMEDIC/ and renderer/).
  inf.py                 the posable soldier (shape S, pose Q) as convex solids (the Medic's case, crosses and pouch:
                         kit 'medic');  rc.py  the ray caster
  infunit.py             each unit's own data (the Medic: his kit, colour classes, sizes, colours, the ramps)
  inffit.py              the fit's loss in TS's camera, and the shape + standing fit (medic_shape.json); infrefine.py
                         each facing's own arms and head (medic_stand_frames.json); infcalib.py  the colours
  infcycle.py            the run as a smooth loop (medic_walk_cyc.json, medic_walk_faces.json, medic_walk_frames.json)
  crawlbio.py            the crawl, a real prone crawl fitted to TS's crawl frames (medic_crawlfit.json,
                         medic_crawl_frames.json); crawlfit.py  which facings TS drew, and the mirror
  infliedown.py          lying down and getting up;  infsmooth.py  the idles, deaths and the heal
  infrender.py           an HD frame;  infall.py  all 307 frames with the blood (and the empty fire frames)
  infexport.py           the .glb;  infpreview.py  the previews;  infreport.py  the numbers above
  infcheck.py, infmasks.py, infgif.py, hdgrid.py, cyclesheet.py, infshow.py, motion.py   the checks used along the way
  infpackage.py          this package (frames, previews, model, src)
e.g.  python3 infall.py medic medic_shape.json out/          (every frame; or a list: out/ 8,9,10)
"""

README_3D = """{title} (TS [{code}]) for Tiberian Factions: the 3D model
=============================================================

{stem}.glb   the soldier, every sequence as a glTF animation, and the mod's camera
           (see {pkgname}/README.txt for how the model was made and fitted to TS's frames)

- Nodes: {model} > {nodes}.
  {marker_line}Each part is one rigid solid (an exact mesh of the convex solid the renderer draws), posed per frame by
  its node's translation and rotation.
- Animations, facing east (the 8-facing sequences use the east facing's frames; the ones TS draws in one facing,
  the idles and deaths, play facing east too), at the game's speed (15 ticks a second); the looping ones end on their
  first frame again, so they loop without a seam:
{anims}
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (30.3 TS px, as the other TS units' models).
  Origin: the soldier's position on the ground.  He faces east (the mod's facing 6).
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the mod's 267 x 208
  canvas exactly (checked by drawing the mesh through it over frame 6: overlap {glb_ov}).
- Khronos's glTF validator: {glb_val}.
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).
"""


# per unit: the 3D model's nodes and marker, and the judgement calls (E1's are written into its README)
NODES = {'e1': ('pelvis, belt, abdomen, chest, vest, pack, pouch, helmet, mask, jaw, rifle, receiver, and\n  left_/right_ '
                'thigh, shin, knee, boot, shoulder_pad, upper_arm, forearm, hand', 'muzzle',
                'a marker on the rifle where the flash comes from'),
         'e2': ('pelvis, hips, belt, abdomen, chest, vest, rucksack, helmet, mask, jaw, and\n  left_/right_ '
                'thigh, thigh_back, thigh_low, shin, knee, boot, shoulder_pad, upper_arm, forearm, hand', 'throw',
                'a marker in the right hand\'s palm, where the disc leaves it'),
         'eng': ('pelvis, belt, abdomen, chest, vest, pack, toolbox, lid, helmet, mask (the\n  respirator), jaw, '
                 'goggle_l, goggle_r, and left_/right_ thigh, shin, knee, boot, shoulder_pad, upper_arm, forearm, hand',
                 '', ''),
         'ghost': ('pelvis, belt, abdomen, chest, vest, roll, roll_end_l, roll_end_r, hood, hood_top,\n  face, rifle (the '
                   'railgun), receiver, and left_/right_ thigh, shin, knee, boot, shoulder_pad, upper_arm,\n  forearm, '
                   'hand', 'muzzle', 'a marker on the railgun where the flash comes from'),
         'jj': ('pelvis, belt, abdomen, chest, vest, jetpack, left_nozzle, right_nozzle, left_wing,\n  right_wing, helmet, '
                'mask, jaw, rifle, receiver, and left_/right_ thigh, shin, knee, boot, shoulder_pad,\n  upper_arm, forearm, '
                'hand', 'muzzle', 'a marker on the rifle where the flash comes from'),
         'medic': ('pelvis, belt, abdomen, chest, vest, back_cross_v, back_cross_h, pouch, medkit,\n  case_cross_r_v, '
                   'case_cross_r_h, case_cross_l_v, case_cross_l_h, helmet, mask (his face), jaw,\n  and left_/right_ '
                   'thigh, shin, knee, boot, shoulder_pad, upper_arm, forearm, hand', '', '')}
CALLS = {'e2': """- TS drew his crawl only facing N, NW, W, SW and S; its NE, E and SE crawl frames are those sprites flipped, pixel
  for pixel.  The HD crawl there is the same pose mirrored (his left and right swapped), as TS's is.
- No disc in his hand: TS draws none (at most a grey pixel or two in the throw), and the disc in flight is the game's
  effect (the hand-off README); the 3D model has a "throw" marker in the right hand for it.
- His back is one big blue rucksack, and the orange under it is patches on the backs of his trousers (your notes).  It
  was first read as a dark plate with two magazines across it and a pouch on his belt; TS's two light bands across the
  rucksack are its shading.  It is a soft bag, not a box (your notes: TS's "has a rounded curve", "STILL has a big
  rectangular backpack"): rounded over its top, back and sides, flat where it sits on his back, nearly upright, with a
  lid flap over its top - TS's light band across the top of the pack and the dark crease under it.  Its size, how far
  it stands off his back and how round it is are fitted to TS's 8 standing frames and 16 of its run frames together.
  Its colours are TS's own tones (your note: "pack is good!"): seen from behind, half of TS's pack is near-black navy
  and a quarter bright lavender where it catches the light, so the pack's shading is mapped onto those tones, quantile
  for quantile (infunit.py, the pack's tone curve) - it was one flat mid grey-blue, and before that a light lavender
  box, which read as a thin board.
- His crawl pushes along the ground with his legs, a knee drawn up to the side in turn and the leg driving back (your
  note: the crawl "isnt kicking their legs against the floor").  The first crawl's legs were bent up in the air: the
  fit could only turn the thigh out a little at the hip, so every bend of the knee lifted the foot off the ground.
  With the thigh turned out, the knee bends along the ground; the stroke is fitted to TS's crawl frames, lying on the
  ground.  In v5 that fit had settled on a stroke too small to see (your note: "hes not using his legs to push and
  move"); refitted from a full stroke - each knee drawn well up to the side (30 degrees and more), then the leg driven
  straight back - it fits TS's crawl frames closer than either earlier crawl.
- The faceplate is bigger than a fit of the whole soldier made it (fitted again on its own, the light blue counted
  three times over): TS shows it in every facing that sees his face, 2 px at the front edge in the side views.
- The orange is on TS's own ramp rather than one colour (see What it is): a plain orange could not be as light as
  TS's in HD's light and stay orange.
- In the throw his arms reach out where TS's do.  TS draws them there as lines a pixel or two wide flung out from his
  body, which count for little against his body's outline, and the first fits tucked them in; now each thin line TS
  flings out from his upper body is fitted with one of his arms along it, shoulder to hand (gunline.py, ARM_LINE).
  Where TS shows both arms out and his body hides one from this camera, the one in view is drawn.  The turn of his
  body, his back to the target at the wind-up and his front at the follow-through, is TS's.
- Throwing from prone he lies flat, his chest down and the rucksack along his back, as TS draws him (the old fits had
  him pushed up on his arms, the pack standing up off his back); crawling, his chest is up on his forearms a little
  (at most 15 degrees: TS's crawl is a closer fit further up, but the pack then stood up like a box).
- TS's run facing west starts a step later than its other seven facings (its frames match the run one step on, in
  every fit of the run); the HD run follows each facing's own TS frames, so its west loop starts a step on too.
- TS draws idle 1 and death 1 facing south-west, idle 2 and death 2 facing north-east (their first frames match those
  standing frames); the hand-off README says west and east.  They're drawn as TS's frames are.
- Frame 85 (unused) is a copy of 84."""}
CALLS['eng'] = """- TS drew his crawl only facing N, NW, W, SW and S; its NE, E and SE crawl frames are those sprites flipped, pixel
  for pixel.  The HD crawl there is the same pose mirrored (his left and right swapped, so the toolbox is in his
  left hand there), as TS's is.
- His fire and fire-prone frames (164-259) are empty: he is unarmed, TS's frames there are a single pixel and the game
  never shows them (the hand-off README).
- TS's faceplate is read as goggles and a respirator (two dark pixels a row above two light grey ones in its front
  view, the light grey at the front edge in its side views); EA's Engineer wears a hard hat instead.
- The yellow is on TS's own ramp rather than one colour (see What it is), each part as light as TS draws it.
- His suit is fitted with more room than the soldiers' (wider hips, bigger hood and body): in their ranges the fit
  stopped at the widest of each.
- TS draws idle 1 and death 1 facing south-west, idle 2 and death 2 facing south-east (their first frames match those
  standing frames); the hand-off README says west and east.  They're drawn as TS's frames are.
- Frame 85 (unused) is a copy of 84."""
CALLS['ghost'] = """- His forearms and hands are drawn in his upper arms' skin tone.  TS draws them darker (its shading), and drawn that
  dark in HD they vanished against his black clothes, so he looked like an amputee (your note).
- The railgun is kept out ahead of his body: wherever its hold would pass it through his hips, belly or chest, it is
  pushed forward until clear and his hands follow it (your note: it clipped into his stomach).
- The railgun is TS's thickness: 1 TS px along its barrel, 2 at its receiver by his hands (TS's side views); it was
  drawn about half that (your note: TS's gun is bigger).  Its length (15 TS px, stock to muzzle) is TS's.
- Fire and fire prone follow TS's two poses in each facing (your note: "og moving his gun as firing and pointing in
  right direction"): between shots he holds the railgun at his hip angled across to his left; on each shot he swings
  it round to point along his facing, the flash at its muzzle.  Each pose is fitted to its own frames, the gun laid
  along TS's gun and its muzzle where TS's flash starts (they were one pose a facing, which left the gun pointing down
  between the two).
- In the run the railgun is laid where TS draws it in every frame: TS swings it about from facing to facing and step
  to step (running south it is up across his chest, then down at his side, then across again).
- The band TS draws behind his head is drawn as a roll across his shoulders: in every facing TS has it behind his head at
  his head's height, wider than his shoulders and 2 rows thick, near-black with a light grey pixel a pixel in from
  either end (read as light ends).  TS draws it close in behind his head (from the side, a pixel or two of it shows
  behind the head), so in the 3D model it passes through the back of his hood.
- His head is read as a blue-grey hood (TS's colour is the soldiers' helmet blue-grey; it covers the top and back of
  his head with his face in front); EA's Commando wears a beret instead.  TS puts a light blue-grey pixel on its top;
  the HD hood is lit by the buildings' light rather than given a glossy highlight.
- His top is not house colour: TS draws it in its olive and natural greens, not its remap greens.  House colour is on
  the shoulder pads and the railgun only.
- He stands with his knees bent in a wide stance, as TS draws him (the fit was allowed bent knees for it).
- TS draws idle 1 and death 1 facing south-west, idle 2 and death 2 facing south-east (their first frames match those
  standing frames); the hand-off README says west and east.  They're drawn as TS's frames are.
- In the crawl the railgun is held ahead in both hands and pushed forward a little with each stroke.  TS's crawl frames
  swing it about from step to step (pointing down at the ground, then ahead, then across him); following that made it
  flail, so it keeps one hold, TS's average.
- Frame 85 (unused) is a copy of 84."""
CALLS['jj'] = """- TS never lays him down: his crawl frames are his run frames, fire prone his fire frames, lying down and getting up
  his standing frames, pixel for pixel.  HD's are the same copies (86-133, 212-259, 260-291).
- His deaths (134-163) are empty, as TS's are: he dies by the tumble (436-450), which the game doesn't show; it is
  drawn anyway, as TS draws it, ending on the ground in TS's blood.
- The jetpack is TS's grey column on his back, narrower than a free fit of the whole soldier made it (that fit filled
  TS's black outlines between the wings with a wide dark pack, a slab taller than his head); the wings then fitted
  again round it.
- The wings are flat panels swept back and set up a little; TS's few pixels don't show their thickness or how they
  fold, so they keep one set in every pose, flying or standing.
- The tumble's poses are as near as one stiff body can come to TS's: TS draws him spinning through angles a fit near
  the frame before can't follow everywhere, and the game never shows these frames.
- TS draws idle 1 facing south-west and idle 2 facing south-east (their first frames match those standing frames);
  the hand-off README says west and east.  They're drawn as TS's frames are.  Frame 85 is idle 2's last frame."""
CALLS['medic'] = """- TS drew his crawl only facing N, NW, W, SW and S; its NE, E and SE crawl frames are those sprites flipped, pixel
  for pixel.  The HD crawl there is the same pose mirrored (his left and right swapped, so the case is in his
  left hand there), as TS's is.
- His fire and fire-prone frames (164-259) are empty: he is unarmed, TS's frames there are empty and his fire is the
  heal (292-306, the hand-off README).
- TS's orange across the backs of his hips and down the backs of his thighs is read as his hips' and thighs' own
  colour behind (green plates on the thighs' fronts), not a pouch; the orange on his upper arms as armbands (EA's
  Field Medic wears white ones).
- The red cross on his helmet's crown is read from TS's blurred red there (see What it is); at TS's size it is a pixel
  or two of flesh colour, so its size is read off that (its arms a half of the helmet's width).
- His armour's greys are matched to all of TS's grey and dark pixels on each part (TS shades the front of his armour
  dark: matched to the light greys alone, he came out nearly white).
- The red crosses are drawn on the model where TS has them (his upper back, the case's faces) in TS's pure red, lit
  only a little.
- TS draws idle 1 facing south-west and idle 2 facing south-east, the heal facing south-east (their first frames match
  those standing frames); the hand-off README says west and east for the idles.  They're drawn as TS's frames are.
- Frame 85 (unused) is a copy of 84."""
# (every unit TS lays down: deaths, crawl and prone fitted to TS's shadow too, lying on the ground)
GROUND_CALL = """- The deaths, crawl and prone frames are fitted to TS's shadow as well as its outline (your notes: "leg in the air
  way above the shadow", "ours are hovering above the ground").  From TS's camera a leg raised in the air and a leg
  lying further back look the same, and the first fits took the floating one.  TS's own shadow, which the mod's
  frames carry, tells them apart: its light (from the north-north-west, 50 degrees up) is read off all six units' standing
  frames, and each frame's shadow is fitted to TS's.  Wherever TS shows him down, his hips, chest, knees and feet lie
  on the ground (propped on his forearms when prone), and each death is fitted from its last frame, lying flat,
  back to its first, so he falls the way TS's does.
- A dying soldier's shadow follows TS's, frame by frame (your note: "on the og's the shadow disappears as the unit
  falls"): TS's shrinks as he goes down and is all but gone once he lies on the ground.  Each death frame's shadow is
  drawn in under him (its light raised, so it shortens) and then faded, to show as much of it as TS shows round its
  frame (deathshadow.py; the lengths and strengths are in src/{lc}_shadow_w.json).  Once he is down only a faint
  shadow hugs him, which the game drops (under alpha 128), as TS has none."""
CALLS.setdefault('e1', '')
for _u in ('e1', 'e2', 'eng', 'ghost', 'medic'):
    if _u in CALLS:
        CALLS[_u] = (GROUND_CALL.replace('{lc}', _u) + '\n' + CALLS[_u]).rstrip('\n')
# (the crawls refitted with the thigh free to turn out at the hip: CRAWL_FROG lists the units done so)
CRAWL_FROG = ('e1', 'eng', 'medic')
CRAWL_CALL = """- His crawl pushes along the ground with his legs, a knee drawn up to the side in turn and the leg driving back
  (your note on the Disc Thrower's crawl: "isnt kicking their legs against the floor").  The first crawls' legs were
  bent up in the air: the fit could only turn the thigh out a little at the hip, so every bend of the knee lifted the
  foot off the ground.  With the thigh turned out, the knee bends along the ground; the stroke is fitted to TS's crawl
  frames, lying on the ground."""
for _u in CRAWL_FROG:
    if _u in CALLS:
        CALLS[_u] = (CRAWL_CALL + '\n' + CALLS[_u]).rstrip('\n')
CALLS['jj'] = CALLS['jj'] + """
- The tumble ends lying flat on the ground where TS's does, fitted to TS's shadow as well as its outline (it ended
  half sitting with a leg up)."""
READMES = {'e1': 'README', 'e2': 'README_E2', 'eng': 'README_ENG', 'ghost': 'README_GHOST', 'jj': 'README_JJ',
           'medic': 'README_MEDIC'}


EA_NAME = {'ra-e1': "RA's Rifle Infantry (E1)", 'ra-e2': "RA's Grenadier (E2)", 'ra-e6': "RA's Engineer (E6)",
           'ra-medi': "RA's Medic (MEDI)", 'td-rmbo': "TD's Commando (RMBO)"}


def ea_note(unit):
    """the movement's source, when it follows EA's own HD infantry (wrig/ealib.py) rather than TS's frames."""
    seqs = []
    code = None
    for s, nm in (('walk', 'the run'), ('lie_down', 'lying down'), ('get_up', 'getting up'), ('idle1', 'idle 1'),
                  ('idle2', 'idle 2'), ('death1', 'death 1'), ('death2', 'death 2'), ('fire', 'the attack'),
                  ('prone_fire', 'the attack lying down'), ('heal', 'the heal')):
        p = '%s_%s_frames.json' % (unit, s)
        if os.path.exists(p):
            d = json.load(open(p))
            if 'ea_code' in d or any(isinstance(v, dict) and 'ea_frame' in v for v in d.values()) or \
                    (s == 'walk' and os.path.exists('wrig/%s_walk_ea.json' % unit)) or (s == 'walk' and unit == 'e2'):
                seqs.append(nm); code = d.get('ea_code', code)
    cf = json.load(open('%s_crawlfit.json' % unit)) if os.path.exists('%s_crawlfit.json' % unit) else {}
    if cf.get('ea_code'):
        seqs.insert(1, 'the crawl'); code = cf['ea_code']
    if not seqs:
        return ''
    ea = EA_NAME.get(code, code or "EA's counterpart")
    seqs[0] = seqs[0][0].upper() + seqs[0][1:]
    return ('Movement: EA\'s own (your note: "follow ea")\n'
            '----------------------------------------------\n'
            '%s follow %s HD frames from the Remastered install (same 267 x 208 canvas, scale and 32-degree camera), '
            'not TS\'s: each pose fitted to EA\'s outline and colours (skin, dark kit) on the shared skeleton, a body part '
            'at a time, the crawl as EA\'s leopard crawl read off its frames (one arm reaching straight out along the '
            'ground, the knee on that side drawn up and out) with its timing, lean and place fitted, and the run as EA\'s '
            'stride.  EA\'s timing is spread over TS\'s frame counts (the mod keeps TS\'s layout).  The deaths\' blood is '
            'drawn where EA\'s pools land.  Where the notes below describe fitting the movement to TS\'s frames, EA\'s '
            'now replaces it; the soldier\'s sizes and kit are still read off TS.') % (
        ', '.join(seqs[:-1]) + ' and ' + seqs[-1] if len(seqs) > 1 else seqs[0], ea + "'s")


def write_readmes(unit, pkg, rep, info, val, ov):
    import infunit
    u = infunit.UNITS[unit]
    ts, mod = rep['ts'], rep['mod']
    anims = '\n'.join('    %-12s %s' % ('"%s"' % k, v) for k, v in info.items())
    allm = [mod[k] for k in mod]
    nodes, mname, marker = NODES[unit]
    fields = dict(ts_stand=ts['stand'], ts_walk=ts['walk'], mo_walk=rep['motion']['walk'], ts_crawl=ts['crawl'],
                  mo_crawl=rep['motion']['crawl'], ts_fire=ts.get('fire', 0.0), ts_prone=ts.get('prone_fire', 0.0),
                  ts_lie=ts.get('lie_down', 0.0), ts_fly=ts.get('fly', 0.0), ts_hover=ts.get('hover', 0.0),
                  ts_fire_fly=ts.get('fire_fly', 0.0), ts_tumble=ts.get('tumble', 0.0), ts_heal=ts.get('heal', 0.0),
                  mo_fire=rep['motion'].get('fire', 0.0), mo_prone=rep['motion'].get('prone_fire', 0.0),
                  ts_idle1=ts.get('idle1', 0.0), ts_idle2=ts.get('idle2', 0.0), ts_death1=ts.get('death1', 0.0),
                  ts_death2=ts.get('death2', 0.0),
                  mod_all=sum(allm) / len(allm), mod_stand=mod['stand'], mod_walk=mod['walk'], mod_crawl=mod['crawl'],
                  mod_fire=mod.get('fire', 0.0), feet_lo=min(rep['feet']), feet_hi=max(rep['feet']), anims=anims,
                  mfeet_lo=min(rep['feet_mod']), mfeet_hi=max(rep['feet_mod']),
                  glb_ov=ov, glb_val=val, title=u['title'], code=u['name'], lc=unit, model=u['model'], nodes=nodes,
                  marker_name=mname, marker=marker, calls=CALLS.get(unit, ''),
                  marker_line=('Marker "%s": %s.\n  ' % (mname, marker)) if mname else '',
                  stem='ts' + u['name'].lower(), pkgname=os.path.basename(pkg))
    text = globals()[READMES[unit]].format(**fields)
    note = ea_note(unit)
    if note:
        i = text.index('\n\n') + 2
        text = text[:i] + note + '\n\n' + text[i:]
    # (the scripts the shadow pass added, listed with the others)
    extra = ('  tsshadow.py            TS\'s own shadow, read off the mod\'s frames, and its light (ts_light.json: fitted on\n'
             '                         all six units\' standing frames); the fits count it with SHADOW=w\n'
             '  ground.py              how far a soldier TS shows on the ground floats off it (deaths, crawl, prone)\n'
             '  deathfit2.py           a death fitted to TS\'s frames and shadow, from its last frame back to its first\n'
             '  deathshadow.py         a death\'s shadow drawn in and faded as TS\'s own frames have it (UNIT_shadow_w.json)\n'
             '  firepair.py, gunpass.py, gunline.py   fire as TS\'s alternating poses; a gun laid along TS\'s gun\n'
             '  fitcheck.py, checksheet.py   the check sheets: a fit and its shadow in TS\'s camera; TS beside HD\n')
    # (the check sheets, when the package has them)
    sheets = [n for n in ('animation-sheet.png', 'death-1-sheet.png', 'death-2-sheet.png', 'crawl-sheet.png', 'fire-sheet.png')
              if os.path.exists(os.path.join(pkg, 'previews', n))]
    if sheets and 'ts-' in text:
        i = text.find('\n', text.find('masks.png'))
        if i > 0:
            text = (text[:i + 1] + '            %s\n                                  the frame-by-frame check sheets: each frame '
                    'as the mod draws it now (TS\'s\n                                  sprite and shadow) beside HD\n'
                    % ', '.join(sheets) + text[i + 1:])
    if 'e.g.  python3 infall.py' in text:
        i = text.index('e.g.  python3 infall.py')
        text = text[:i] + extra + text[i:]
    open(pkg + '/README.txt', 'w').write(text)
    open(pkg + '-3d/README.txt', 'w').write(README_3D.format(**fields))


if __name__ == '__main__':
    main()
