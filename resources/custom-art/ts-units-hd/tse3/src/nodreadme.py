"""
nodreadme.py - the Nod infantry's delivery README (infpackage.py writes it with the numbers of the unit's fits): one
template for the seven, each unit's own look, gear and judgement calls below it.
"""
import os
import numpy as np

NOD = ('e3', 'cyborg', 'cyc2', 'mhijack', 'chamspy', 'elcad', 'umagon')

README = """{title} (TS [{code}], Nod) in HD for Tiberian Factions: {modname}
==============================================================

{frames_block}previews/   run-8-facings.gif, crawl-8-facings.gif, fire-8-facings.gif, fire-prone-8-facings.gif
                                  every facing at once, TS's sprite above HD
            run-west.gif, run-south.gif, crawl-west.gif, crawl-south.gif, fire-west.gif, fire-south.gif
                                  TS's sprite | TS's sprite scaled onto the canvas | HD, at the game's speed
            idle-1.gif, idle-2.gif, death-1.gif, death-2.gif      the same for the one-facing sequences
            lie-down-get-up-W.gif, lie-down-get-up-SE.gif         standing -> down -> prone -> up -> standing
            standing-8-facings.png    TS's sprite, scaled, HD and {ref_name}, each facing
            masks.png                 the head close up in 8 facings: TS, scaled, HD
            shape-run.png, shape-crawl.png    TS's frames as colour classes beside the model's, in TS's own camera
{pkgname}-3d/   the 3D model in its own zip ({pkgname}-3d.zip) next to this folder
src/        the model, its fits, the renderer and the checks (see Rebuilding below)

Nod never had frames in the mod, so where the GDI infantry's previews show the mod's current frame, these show TS's
sprite scaled onto the canvas the way the mod scales the GDI Light Infantry's (3.068 times, nearest pixel, at the same
place).


What it is
----------
The posable soldier the six GDI infantry are made from (inf.py), with the {title}'s own sizes, gear and colours
(infunit.py), fitted to TS's own {code} frames in TS's camera (silhouette and colour classes, TS's flash and blood left
out) and drawn the way the GDI infantry are.
{what}
- Standing: one pose fitted to the 8 standing frames together, then each facing's arms, {gun} and head to its own
  frame.  Overlap with TS's frames in TS's camera: {ts_stand:.2f}.
- The run is one smooth loop: every joint follows a short smooth curve (a Fourier series) through the {walk_n} steps, so
  step {walk_last} runs into step 0 like any step into the next.  The loop is fitted to TS's {walk_frames} run frames together; each
  facing's arms, {gun} and head then get their own smooth loop on top, held close to the shared one.  Overlap
  {ts_walk:.2f}; the furthest any landmark ({landmarks}) moves from one step to the next is {mo_walk:.1f} TS px.
{crawl_bullet}  Overlap {ts_crawl:.2f}, landmarks at most {mo_crawl:.1f} TS px a step.
{fire_bullet}
{lie_bullet}{deaths_bullet}  Overlap: idles {ts_idle1:.2f} and {ts_idle2:.2f}, deaths {ts_death1:.2f} and {ts_death2:.2f}.
{effects_bullet}
Against TS's sprite scaled onto the canvas the silhouettes overlap by {mod_all:.2f} (standing {mod_stand:.2f}, run
{mod_walk:.2f}, crawl {mod_crawl:.2f}, fire {mod_fire:.2f}): the scaled sprite is TS's own camera above, blown up, so this is
that difference scaled up with it (a soldier's limbs are a few TS pixels wide, so a pixel counts for a lot), plus the
32-degree camera.


Keep (from the hand-off README)
-------------------------------
- The 267 x 208 canvas; every frame of {keep_frames} in TS's order.
- The feet: on the GDI infantry's feet point; standing, the boots' lowest pixel is on canvas row {feet_lo}-{feet_hi}
  by facing (the README: (133.5, 111), EA's Minigunner's).
- The size: the GDI infantry's scale (3.068 canvas px a TS px, the soldier drawn 8% bigger about the feet: 3.31), so
  {he} stands beside them as TS has {him} beside the Light Infantry, and as tall as EA's HD infantry (your note: "standard
  infantry should match the RA / TD inf for size"): {height_line}  standing-8-facings.png has {ref_name} beside {him}.
- The shadow baked in at alpha 128 (50% black, blurred), as the GDI infantry's.  TS's decoded sprite has no shadow
  frames, so it is the HD soldier's own, cast by the buildings' light.  In the deaths it draws in under {him} and fades
  as {he} goes down, as the GDI infantry's do (your note on them: "on the og's the shadow disappears as the unit falls"):
  with no TS shadow to read, how much it shows in each frame is how much shadow the fitted body casts under TS's own
  light (read off the GDI units' frames), against the standing frames (deathshadow.py; the lengths and strengths are
  in src/{lc}_shadow_w.json).
- House colour pure green on {house}; the -trim masks cover exactly those.
{flash_keep}


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north, as the GDI infantry's.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the units' camera fill (EA's HD
  infantry are lit from the front), as bright as the GDI infantry; each part as light as TS draws it under that light
  (infcalib.py){ramp_note}.
- House colour: exactly 0,214,0 x (1 + 1.1 grain) on {house}.


3D model ({pkgname}-3d/)
--------------------------
{stem}.glb   the soldier in vertex colours, every sequence as a glTF animation, the mod's camera
- Nodes: {model} > {nodes}.
  {marker_line}Each part is one rigid solid, posed per frame by its node's translation and rotation.{legless_line}
- Animations, facing east (the 8-facing sequences use the east facing's frames; the idles and deaths play facing east
  too), at the game's speed (15 ticks a second); the looping ones end on their first frame again, so they loop without
  a seam:
{anims}
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (30.3 TS px, as the other TS units' models).
  Origin: the soldier's position on the ground.  {He} faces east (the mod's facing 6).
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
export3d.py) and the voxel reader (vxl.py) are included.  The scripts read the GDI hand-off's folder layout:
nodmirror.py lays the Nod hand-off out that way (TS's sprite, the sprite scaled onto the canvas, EA's reference
strips): NOD_HANDOFF=<the Nod hand-off> EA_UNITS=<RA + TD HD Units> TS_HANDOFF=<out> python3 nodmirror.py {lc}, then
the rest with TS_HANDOFF=<out>.
  inf.py                 the posable soldier (shape S, pose Q) as convex solids ({kit_line});  rc.py  the ray caster
  infunit.py             each unit's own data (the {title}: its kit, colour classes, sizes, colours)
  inffit.py              the fit's loss in TS's camera, and the shape + standing fit ({lc}_shape.json); infrefine.py
                         each facing's own arms, {gun} and head ({lc}_stand_frames.json); infcalib.py  the colours
                         read off TS's frames
  infcycle.py            the run as a smooth loop: the shared cycle ({lc}_walk_cyc.json), each facing's own loop
                         ({lc}_walk_faces.json) and every frame's pose ({lc}_walk_frames.json); infphase.py  each
                         facing's start step; gunpass.py  a weapon laid along TS's, frame by frame
  crawlbio.py            the crawl, a real prone crawl fitted to TS's crawl frames ({lc}_crawlfit.json,
                         {lc}_crawl_frames.json); crawlfit.py  every crawl frame
  infstatic.py, firepair.py   fire and fire prone ({lc}_fire_frames.json, {lc}_prone_fire_frames.json)
  infliedown.py          lying down and getting up;  infsmooth.py, deathfit2.py  the idles and deaths
  infrender.py           an HD frame;  infx.py  the flash;  infall.py  all 292 frames with flash and blood;
                         deathshadow.py  the deaths' shadows
  infexport.py           the .glb;  infpreview.py  the previews;  infreport.py  the numbers above
  infcheck.py, infmasks.py, checksheet.py, animsheet.py, cyclesheet.py, motion.py   the checks
  infpackage.py, nodreadme.py   this package (frames, previews, model, src, this README)
e.g.  python3 infall.py {lc} {lc}_shape.json out/          (every frame; or a list: out/ 8,9,10)
"""

DIRS = {0: 'north', 1: 'north-west', 2: 'west', 3: 'south-west', 4: 'south', 5: 'south-east', 6: 'east',
        7: 'north-east'}

# per unit: the facings TS draws its one-facing sequences in (tools/startfacing.py: their first frames against the
# standing frames), and what it is
INFO = {
    'e3': dict(
        facings=(3, 5, 3, 4), gun='launcher', kit_line="the launcher: kit 'e3'",
        landmarks="the launcher's mouth and back end, hands, head, feet",
        house='the shoulder pads, upper arms and thighs',
        ramp_note='',
        what="""- The look (your makeover, from your Nod rocket trooper concept, in the soldiers' armour style): a full dark
  helmet with the soldiers' glowing light-blue visor across the eyes in a dark frame (TS's light blue-grey faceplate -
  you: "Lets stay ts accurate", not the concept's red), ear pieces, an antenna on the left and a small house-colour lamp
  on the crown; segmented dark plates (chest, back, belly, gorget) over a black suit, a box pack with a flap, four belt
  pouches and a holster on the right thigh; house-colour shoulder pads with a lame below each, upper arms and thighs
  (TS's remap areas), dark elbows and forearms; light grey knee plates with a house-colour chevron, light grey greaves
  and dark boots with soles.  The launcher stays TS's light grey (the concept's is dark) with a yellow band near the
  mouth and a sight on its left (inflook_e3.py, its colours infunit.MAT_E3_LOOK2).  The concept's red trim is house
  colour.  The notes below are TS's sprite as the fit read it, kept for the record.
- His head: a near-black helmet over a light blue-grey faceplate (TS: the head near-black, its faceplate a pixel or
  two of light blue-grey at the front in the views that see his face), as E1's helmet and faceplate.
- The launcher: a light grey tube {gl:.1f} TS px long and {gt:.1f} thick (TS's side views), dark rims at either end, on
  his right shoulder and held there by both hands under it (a dark grip block between them and the tube), as TS draws
  it in every standing frame: pointing up and ahead over his shoulder.
- His body: near-black and dark grey (TS: his helmet, chest, back and belt), a dark pack and pouch on his back; house
  green on the shoulder pads, upper arms and thighs (TS's remap areas); light grey knees and lower legs, dark boots.""",
        nodes=('pelvis, belt, abdomen, chest, vest, pack, pouch, helmet, mask, jaw, launcher, launcher_back,\n  '
               'launcher_mouth, launcher_grip, and left_/right_ thigh, shin, knee, boot, shoulder_pad, upper_arm,\n  '
               'forearm, hand'),
        marker=('muzzle', "a marker at the launcher's mouth, where the flash comes from"),
    ),
    'elcad': dict(
        facings=(3, 5, 3, 4), gun='rifle', kit_line="his hood, face and open jacket: kit 'elcad'",
        landmarks="the rifle's muzzle and back end, hands, head, feet",
        house="his shoulder pads, his jacket's sleeves and the fronts of his thighs",
        ramp_note=", his skin on TS's own flesh ramp",
        what="""- He is made from the sprite TS draws him with, Slavik's (SLAV), as the hand-off README says.
- His head: a light grey hood over the top and back of his head (TS: near white on top in every facing), his face
  under it in front.
- An open jacket: house green shoulders and sleeves, dark behind; his chest and belly bare in front (TS's front views:
  its darker flesh browns); black hips; trousers house green in front and dark behind, brown knee pads, dark lower
  legs, grey boots.
- A light grey rifle ({gl:.1f} TS px), held at his hip pointing ahead as TS draws him standing, raised level to fire.
- His skin is drawn on TS's own flesh ramp (its sixteen tones, dark red-brown to light pink), each part as dark as
  TS draws it: his face lighter, his chest and belly the darker browns.""",
        nodes=('pelvis, belt, abdomen, abdomen_back, chest, vest (his bare chest), pack, pouch, hood, hood_top, face,\n  '
               'rifle, receiver, and left_/right_ thigh, thigh_back, shin, knee, boot, shoulder_pad, upper_arm, forearm,\n  '
               'hand'),
        marker=('muzzle', 'a marker on the rifle where the flash comes from'),
    ),
    'chamspy': dict(
        facings=(3, 5, 3, 3), gun='hands', armed=False, kit_line="his goggles and belt band: kit 'chamspy'",
        landmarks="hands, head, feet",
        house="his shoulder pads, upper arms and thighs",
        ramp_note='',
        what="""- His head: a light grey hood-helmet with orange goggles across his face (TS: an orange row at the front of his
  head in the views that see his face), dark under them.
- A near-black suit: house green on the shoulders, upper arms and thighs (TS's remap areas), TS's pale non-remap greens
  (camouflage) on his forearms and shins, and a lavender band round the back of his belt (TS's back views).
- He carries nothing; his hands are gloved dark.""",
        nodes=('pelvis, belt, abdomen, chest, vest, pouch (the lavender band), helmet, mask (the goggles), jaw, and\n  '
               'left_/right_ thigh, shin, knee, boot, shoulder_pad, upper_arm, forearm, hand'),
        marker=('', ''),
    ),
    'mhijack': dict(
        facings=(4, 4, 4, 4), gun='hands', armed=False, kit_line="his coat and hood: kit 'mhijack'",
        landmarks="hands, head, feet",
        house="his shoulder pads",
        ramp_note=", his skin on TS's own flesh ramp",
        what="""- His head: bald (TS's flesh tones on his crown, from behind too), an olive hood down round its back and sides.
- A long olive coat (TS's olive darks and greys) over his body and arms and down past his knees, its tails hanging
  round each leg, so they swing as he runs; house green shoulder pads (TS's only remap areas); his bare hands.
- Dark trousers, grey lower legs, dark boots.  He carries nothing.""",
        nodes=('pelvis, belt, abdomen, chest, vest, head, hood, and left_/right_ thigh, coat_tail, shin, knee, boot,\n  '
               'shoulder_pad, upper_arm, forearm, hand'),
        marker=('', ''),
    ),
    'cyborg': dict(
        facings=(3, 5, 3, 5), gun='gun arm', kit_line="the gun arm, red lights, legless crawl and bursting: kit 'cyborg'",
        landmarks="the gun's muzzle and back end, the free hand, head, feet",
        house="its chest and back plate, its shoulder pads and its thighs",
        ramp_note='',
        crawl_line=('the crawl: a crippled cyborg (TS: no legs) dragging itself along on its arms, 6 steps a facing, '
                    'looping; its first step is the prone pose'),
        death_end='it bursts apart in both, the pieces lying on the ground at the end',
        prone_note=' (legless, as the crawl)',
        lie_line='lying down and 276-291 getting up: empty, as TS\'s are (a single stray pixel each)',
        what="""- A third bigger than the soldiers all over (TS: 26-29 px tall to their 20), heavier built: a bone-pale skull with
  a dark face; a house green armour plate over its chest and back and big green shoulder pads, a grey plate on its
  chest's front, a dark waist; grey metal arms; house green thighs, grey metal shins, dark feet; TS's red lights at its
  knees and ankles, drawn glowing red.
- Its gun is built into its right forearm (TS: a grey barrel out past the elbow where the hand would be, {gl:.1f} TS px
  long, {gt:.1f} thick), a dark ring at its muzzle; its left arm is free.
- Crawling and firing prone it has no legs: TS draws a crippled cyborg dragging itself along on its arms (TS's crawl
  frames are a torso and arms, no legs), so the HD one has only stumps of its thighs there.""",
        nodes=('pelvis, belt, abdomen, chest, vest, helmet (its skull), mask (its face), jaw, gun, gun_muzzle,\n  '
               'and left_/right_ thigh, shin, knee, boot, knee_light, ankle_light, shoulder_pad, upper_arm, forearm,\n  '
               'left_hand'),
        marker=('muzzle', 'a marker on the gun where the flash comes from'),
    ),
    'cyc2': dict(
        facings=(1, 5, 3, 7), gun='plasma cannon', kit_line="the cannon arm and legless crawl: kit 'cyc2'",
        landmarks="the cannon's muzzle and back end, the free hand, head, feet",
        house="its shoulder pads, chest and belly",
        ramp_note='',
        crawl_line=('the crawl: a crippled cyborg (TS: no legs) dragging itself along on its arms, 9 steps a facing, '
                    'looping; its first step is the prone pose'),
        death_end='each falls flat over its last 5 frames (TS\'s stay standing: see the calls)',
        prone_note=' (legless, as the crawl)',
        what="""- About 27 TS px tall (the hand-off README), lean and long-legged: a dark grey helmet with a light grey faceplate;
  house green over its shoulders, chest and belly (TS's darker remap greens); dark grey metal arms and legs, lighter
  grey shins.
- Its plasma cannon is built into its right forearm ({gl:.1f} TS px long, {gt:.1f} thick: TS's dark barrel, held
  level ahead at its chest as it stands), a darker ring at the muzzle; its left arm is free.
- Crawling and firing prone it has no legs, as the Cyborg: TS draws a crippled cyborg dragging itself along on its
  arms.""",
        nodes=('pelvis, belt, abdomen, chest, vest, helmet, mask (its faceplate), jaw, gun (the plasma cannon),\n  '
               'gun_muzzle, and left_/right_ thigh, shin, knee, boot, shoulder_pad, upper_arm, forearm, left_hand'),
        marker=('muzzle', 'a marker on the cannon where the flash comes from'),
    ),
    'umagon': dict(
        facings=(3, 5, 3, 5), gun='rifle', kit_line="her hair and face: kit 'umagon'",
        landmarks="the rifle's muzzle and back end, hands, head, feet",
        house="her top's shoulders and sides, its shoulder straps and the fronts of her thighs",
        ramp_note=", her skin and hair on TS's own flesh ramp",
        what="""- Her head, read from TS's frames: her dark red-brown hair over the top and back of her head and hanging down her
  back between her shoulder blades (TS's back view: 2 px wide, down past her shoulders), her face in front of it.
- A house green top (its shoulders, straps and sides: TS's remap greens), her arms bare; black hips; trousers house
  green in front and dark behind (TS's front and back views), light grey lower legs, dark boots.
- A long black rifle ({gl:.1f} TS px), held at her hip pointing ahead as TS draws her standing, raised to her
  shoulder to fire.
- Her skin and hair are drawn on TS's own flesh ramp (its sixteen tones, dark red-brown to light pink), each part as
  light on average as TS draws it: her face lightest, her hair near black.""",
        nodes=('pelvis, belt, abdomen, chest, vest, hood (her hair over her head), hood_top, face, hair (down her\n  '
               'back), rifle, receiver, and left_/right_ thigh, thigh_back, shin, knee, boot, shoulder_pad, upper_arm,\n  '
               'forearm, hand'),
        marker=('muzzle', 'a marker on the rifle where the flash comes from'),
    ),
}


CRAWL_SOLDIER = """- The crawl is a real prone crawl, as the GDI infantry's: flat and low on {his} front, up on {his} forearms with {his}
  head up, one forearm going forward with the opposite knee drawn up to the side while the other leg lies straight
  back, then the other pair, the legs pushing against the ground.  All 8 facings are fitted together to TS's crawl
  frames; one stroke drives every joint, so the loop runs on with nothing jumping back."""
CRAWL_CYBORG = """- The crawl is legless, as TS's (a crippled cyborg drags itself along): flat on its front, its chest up a little,
  its head up, the free arm reaching ahead along the ground and pulling it on, the gun arm out ahead, worked forward a
  little with each pull.  Every joint follows one smooth loop, fitted to TS's crawl frames in all 8 facings together,
  then each facing's own turn of the head and shoulders."""
LIE_SOLDIER = """- Lying down: the two in-betweens fitted to TS's frames on the way down, from the standing pose to the prone one (the
  crawl's first step), so standing, down and prone run as one movement ({ts_lie:.2f}); getting up is the same two
  poses backwards, as TS's get-up frames are its lie-down frames backwards.
"""
DEATHS_SOLDIER = """- The idles and deaths: each frame fitted to its TS frame starting from the one before, then the whole run of poses
  relaxed together (every frame pulled towards the middle of its neighbours), so they move smoothly; the idles start
  from the standing pose and come back to it.  Each death is then fitted again from its last frame, lying on the
  ground, back to its first, so {he} falls the way TS's does."""
DEATHS_CYBORG = """- The idles: each frame fitted to its TS frame starting from the one before, then the whole run relaxed together
  (every frame pulled towards the middle of its neighbours), starting from the standing pose and coming back to it.
- The deaths: it bursts apart, as TS's does - its body as rigid pieces (the gun arm, the free arm, the head, the torso,
  each leg, the hips), each frame fitted to TS's from the one before carried on at the speed the pieces had; no piece
  under the ground, and every piece lying on it once TS has them all down (see the calls)."""
DEATHS_CYC2 = """- The idles and deaths: each frame fitted to its TS frame starting from the one before, then the whole run relaxed
  together (every frame pulled towards the middle of its neighbours); the idles start from the standing pose and come
  back to it.  TS's deaths stay standing; over their last five frames it falls flat (see the calls)."""
FRAMES_E1 = """frames/     {stem}-0000.png ... {stem}-0291.png: 292 frames on the infantry canvas (267 x 208), each
            with a -trim.png (white = house colour, antialiased), numbered as TS's own sequence (E1Sequence, which
            the mod keeps):
              0-7      standing, one a facing; facings counter-clockwise from north (0 N, 1 NW, 2 W, 3 SW, 4 S, 5 SE,
                       6 E, 7 NE)
              8-55     the run: 6 steps a facing (frame = 8 + facing x 6 + step), 2 ticks a step, looping
              56-70    idle 1 (TS draws it facing {idle1_dir});  71-84  idle 2 (facing {idle2_dir});  85 (unused) = 84
              86-133   {crawl_line}
              134-148  death 1 (facing {death1_dir});  149-163  death 2 (facing {death2_dir}); {death_end}
              164-211  {fire_line}
              212-259  fire prone, the same{prone_note}
              260-275  {lie_line}
"""
FRAMES_CYC2 = """frames/     {stem}-0000.png ... {stem}-0307.png: 308 frames on the infantry canvas (267 x 208), each
            with a -trim.png (white = house colour, antialiased), numbered as TS's own sequence (CyborgSequence,
            which the mod keeps):
              0-7      standing, one a facing; facings counter-clockwise from north (0 N, 1 NW, 2 W, 3 SW, 4 S, 5 SE,
                       6 E, 7 NE)
              8-79     the run: 9 steps a facing (frame = 8 + facing x 9 + step), 2 ticks a step, looping
              80-94    idle 1 (TS draws it facing {idle1_dir});  95-109  idle 2 (facing {idle2_dir})
              110-181  {crawl_line}
              182-196  death 1 (facing {death1_dir});  197-211  death 2 (facing {death2_dir}); {death_end}
              212-259  {fire_line}
              260-307  fire prone, the same{prone_note}
            (no lying down or getting up in CyborgSequence)
"""


def SQ_N(unit):
    import infseq as SQ
    return SQ.SEQ[unit]['walk'][1]


def standing_heights(unit, S, js):
    """the standing frames' height in canvas px, the boots to the top of the head (no weapon), per facing."""
    import inf as I
    import infall as AL
    import infrender as R
    tab = AL.pose_table(unit, dict(js['Q']))
    out = []
    for k in range(8):
        Q, f = tab[k]
        parts, dz = I.grounded(S, Q, I.facing_angle(f), rifle=False)
        img, trim = R.render(parts, ss=1, ground=(js['ax'], js['y0']), shadow=False)
        a = np.asarray(img)
        ys = np.nonzero((a[..., 3] > 128).any(1))[0]
        out.append(int(ys.max() - ys.min() + 1))
    return out


def fields(unit, S, js, rep):
    import infunit
    u = infunit.UNITS[unit]
    info = INFO[unit]
    f1, f2, d1, d2 = info['facings']
    hs = standing_heights(unit, S, js)
    P = PRONOUNS.get(unit, PRONOUNS['e3'])
    ts_h = HAND_OFF_HEIGHT.get(unit, '')
    out = dict(
        modname='TS' + u['name'], ref_name=u.get('ref_name', "EA's nearest HD unit"),
        idle1_dir=DIRS[f1], idle2_dir=DIRS[f2], death1_dir=DIRS[d1], death2_dir=DIRS[d2],
        gun=info['gun'], landmarks=info['landmarks'], house=info['house'], ramp_note=info['ramp_note'],
        kit_line=info['kit_line'],
        what=info['what'].format(**{k: (v if not isinstance(v, (list, tuple)) else v[0]) for k, v in S.items()
                                    if isinstance(v, (int, float, list, tuple))}),
        legless_line=('\n  In the crawl and fire prone its legs are scaled away as the frames have them: the shins, knees, boots and'
                      '\n  lights to nothing, the thighs to stumps (a scale channel on those nodes).'
                      if unit in ('cyborg', 'cyc2') else ''),
        fire_bullet=(('- Fire and fire prone: TS\'s own poses in each facing, fitted to its frames, the %s %s and its\n'
                      '  muzzle where TS\'s flash starts.  Overlap %.2f and %.2f.') % (
                          info['gun'], 'laid along TS\'s' if infunit.GUN_CLASS.get(unit, 1) is not None
                          else 'on TS\'s outline', rep['ts'].get('fire', 0.0), rep['ts'].get('prone_fire', 0.0))
                     if info.get('armed', True) else
                     '- No fire or fire prone: %s is unarmed; TS\'s frames there are a single pixel and the game never shows them,\n'
                     '  so they are empty.' % P['he']),
        effects_bullet=(('- Effects, frame by frame from TS\'s own pixels: the flash (TS\'s yellows and reds, its shape kept, drawn\n'
                         '  smooth and hot) at the HD %s\'s muzzle, hidden where %s stands in front of it; the blood in TS\'s red\n'
                         '  (255,0,0), each red pixel drawn on the ground it covers in TS\'s view, so a pool stays put as the body\n'
                         '  falls on it.') % (info['gun'], P['he'])
                        if info.get('armed', True) else
                        ('- Effects, frame by frame from TS\'s own pixels: the blood in TS\'s red (255,0,0), each red pixel drawn on the\n'
                         '  ground it covers in TS\'s view, so a pool stays put as the body falls on it.')),
        walk_n=SQ_N(unit), walk_last=SQ_N(unit) - 1, walk_frames=8 * SQ_N(unit),
        keep_frames=('CyborgSequence (308 frames)' if unit == 'cyc2' else 'E1Sequence (292 frames, 85 unused included)'),
        crawl_bullet=(CRAWL_CYBORG if unit in ('cyborg', 'cyc2') else CRAWL_SOLDIER).format(**P),
        lie_bullet=('' if unit == 'cyc2' else
                    '- Lying down and getting up: empty, as TS\'s are (a single stray pixel each).\n' if unit == 'cyborg' else
                    LIE_SOLDIER.format(ts_lie=rep['ts'].get('lie_down', 0.0))),
        deaths_bullet=(DEATHS_CYBORG if unit == 'cyborg' else DEATHS_CYC2 if unit == 'cyc2' else
                       DEATHS_SOLDIER.format(**P)),
        frames_block=(FRAMES_CYC2 if unit == 'cyc2' else FRAMES_E1).format(
            stem='ts' + u['name'].lower(), idle1_dir=DIRS[f1], idle2_dir=DIRS[f2], death1_dir=DIRS[d1],
            death2_dir=DIRS[d2],
            crawl_line=info.get('crawl_line', 'the crawl: 6 steps a facing, looping; its first step is the prone pose'),
            death_end=info.get('death_end', 'both end lying flat'), prone_note=info.get('prone_note', ''),
            lie_line=info.get('lie_line', 'lying down, 2 frames a facing;  276-291  getting up: the same two backwards (TS\'s are)'),
            fire_line=('fire: 6 frames a facing, 1 tick a frame, the flash where TS has it'
                       if info.get('armed', True) else
                       'fire: empty (unarmed: TS\'s frames there are a single pixel and the game never shows them)')),
        fire_line=('fire: 6 frames a facing, 1 tick a frame, the flash on every other frame, as TS\'s'
                   if info.get('armed', True) else
                   'fire: empty (unarmed: TS\'s frames there are a single pixel and the game never shows them)'),
        flash_keep=('- The bright yellow flash on the fire frames where TS has it, standing and prone, and nothing else '
                    'in those\n  frames as bright, so the muzzle can be measured from it.'
                    if info.get('armed', True) else ''),
        height_line=('standing %s is %d-%d px from %s feet to the top of %s head by facing (%s).' % (
            P['he'], min(hs), max(hs), P['his'], P['his'], ts_h)),
        **P)
    return out


PRONOUNS = {'e3': dict(he='he', He='He', his='his', him='him'), 'elcad': dict(he='he', He='He', his='his', him='him'),
            'chamspy': dict(he='he', He='He', his='his', him='him'), 'mhijack': dict(he='he', He='He', his='his', him='him'),
            'umagon': dict(he='she', He='She', his='her', him='her'),
            'cyborg': dict(he='it', He='It', his='its', him='it'),
            'cyc2': dict(he='it', He='It', his='its', him='it')}
# the hand-off README's heights
HAND_OFF_HEIGHT = {'e3': 'the hand-off README: about 21 TS px, about 68 px at its 3.25',
                   'elcad': 'the hand-off README: about 21 TS px, about 68 px at its 3.25',
                   'umagon': 'the hand-off README: 20-22 TS px, about 65-71 px at its 3.25',
                   'chamspy': 'the hand-off README: about 21 TS px, about 68 px at its 3.25',
                   'mhijack': 'the hand-off README: about 18 TS px, about 59 px at its 3.25',
                   'cyborg': 'the hand-off README: 26-29 TS px, about 85-94 px at its 3.25',
                   'cyc2': 'the hand-off README: about 27 TS px, about 88 px at its 3.25'}

# every Nod unit: no TS shadow to fit the ground poses to
GROUND_CALL = """- No TS shadow: Nod never made it into the mod, so its units have no in-mod frames with TS's shadow in them (the
  GDI infantry's deaths, crawl and prone were fitted to TS's shadow as well as its outline).  These are fitted to
  TS's outline and colours alone, with the ground holding the body down: wherever TS shows it down, its hips, chest,
  knees and feet lie on the ground (propped on its forearms when prone), and each death is fitted from its last
  frame, lying flat, back to its first."""

CALLS = {
    'e3': """- The launcher rides on his right shoulder in every standing facing, as TS draws it (pointing up and ahead over the
  shoulder); EA's Rocket Soldier carries his at his hip instead.
- In the run the launcher stays where each facing's smooth loop holds it, steady on his shoulder as TS's is.  The GDI
  pipeline's last pass lays the gun along TS's own gun frame by frame; TS's launcher is a straight grey bar with no
  front or back, and that pass turned it end for end between steps, so it isn't used for him.
- TS draws idle 1 and death 1 facing south-west, idle 2 facing south-east and death 2 facing south (their first
  frames match those standing frames); the hand-off README says west and east.  They're drawn as TS's frames are.
- Frame 85 (unused) is a copy of 84.""",
}
CALLS['elcad'] = """- His face and bare chest count twice over in the fit: TS shows them as a few pixels of flesh among the hood's grey
  and the jacket's green, and counted once the fit kept his face under the hood and his chest covered.
- The brown on his knees is read as knee pads (TS's flesh browns, below the green fronts of his trousers), his boots
  grey.
- In the run his rifle stays where each facing's smooth loop holds it.  The GDI pipeline's last pass lays the gun along
  TS's own gun frame by frame, finding it as the longest straight run of the gun's colour; in TS's run frames the grey
  down his legs and his grey boots line up as long as his light grey rifle as often as not, so that pass isn't used
  for his run.
  His fire and fire-prone frames, where the rifle stands clear of him, do use it.
- TS draws idle 1 and death 1 facing south-west, idle 2 facing south-east and death 2 facing south (their first frames
  match those standing frames); the hand-off README says west and east.  They're drawn as TS's frames are.
- Frame 85 (unused) is a copy of 84."""
CALLS['chamspy'] = """- He carries nothing: TS's fire and fire-prone frames (164-259) are a single pixel each and the game never shows
  them (the hand-off README), so they are empty.
- TS's faceplate is read as orange goggles (an orange row across the front of his head under the hood's grey), as the
  Engineer's are; EA's Spy, beside him in standing-8-facings.png, wears a suit.
- The lavender TS draws across the small of his back is a band round the back of his belt.
- TS draws idle 1 and both deaths facing south-west and idle 2 facing south-east (their first frames match those
  standing frames); the hand-off README says west and east.  They're drawn as TS's frames are.
- Frame 85 (unused) is a copy of 84."""
CALLS['mhijack'] = """- He carries nothing: TS's fire and fire-prone frames (164-259) are a single pixel each and the game never shows
  them (the hand-off README), so they are empty.
- His coat is one olive in HD, as light as TS's on average: TS mottles it with its olive darks and greys, which at
  TS's size reads as one worn cloth.
- The coat's tails hang round each thigh to past the knee, so they part as he strides, as TS's coat does in its run.
- TS draws both idles and both deaths facing south (their first frames match that standing frame); the hand-off
  README says west and east.  They're drawn as TS's frames are.
- Frame 85 (unused) is a copy of 84."""
CALLS['cyborg'] = """- Its deaths are TS's: it bursts apart.  Its arms fly off either side, its head pops up, its torso bursts into
  TS's red and its legs fold where it stood; the pieces come down and lie there.  The body is cut into pieces (the gun
  arm, the free arm, the head, the torso, each leg, the hips), each a rigid piece with its own motion, fitted frame by
  frame to TS's death frames, each frame from the one before carried on at the speed the pieces had; no piece goes
  under the ground and, once TS has them all down, every piece lies on it.  The torso shrinks away as TS's turns to
  red (cybdeath.py).
- Its crawl and fire prone are legless, as TS's: the arms pull it along, the gun arm out ahead.
- Its gun arm is placed by TS's outline and colours alone.  The GDI pipeline's passes that lay the gun along TS's own
  find it as the longest straight run of the gun's colour, and TS draws its gun the same grey as its metal limbs, so
  that run is a leg as often as the gun.
- Its lying down and getting up (260-291) are empty: TS's are a single stray pixel each (the hand-off README: leave
  them empty).  TS's optional frames past 291 (a burning death, being blown apart, running on fire) are not made.
- TS draws idle 1 and death 1 facing south-west, idle 2 and death 2 facing south-east (their first frames match those
  standing frames); the hand-off README says west and east.  They're drawn as TS's frames are.
- Frame 85 (unused) is a copy of 84."""
CALLS['cyc2'] = """- TS's two deaths keep it standing to the end (electrocuted, blue-white arcs crackling over it; burst open on its
  chest), but the hand-off README asks for every death's last frame lying flat, the game's own corpse following it.
  So each death follows TS's frames up to its last five, and over those it goes down onto its back, falling faster
  as it goes (cyc2fall.py); TS's arcs and sparks go on over it as it falls.  Easy to change: without the fall it ends
  standing, as TS's does.
- TS's arcs are drawn as thin blue-white glowing lines where TS has them, frame by frame, moving with its chest; the
  burst in death 2 as the flash is drawn (TS's yellows, oranges and reds), on its chest.
- Its own sequence (CyborgSequence): 9 steps a facing walking and crawling, no lying down or getting up.
- Crawling it lies well behind where it stands, as TS draws it (8-14 TS px back, its cannon reaching back towards its
  position): the whole crawl is moved back along its facing, the same in every facing.
- Its plasma cannon is placed by TS's outline and colours alone.  The GDI pipeline's passes that lay the gun along
  TS's own find it as the longest straight run of the gun's colour, and TS draws its cannon the same dark grey as its
  metal limbs, so that run is a leg as often as the cannon.
- TS draws idle 1 facing north-west, idle 2 south-east, death 1 south-west and death 2 north-east (their first frames
  match those standing frames); the hand-off README says west and east for the idles.  They're drawn as TS's are."""
CALLS['umagon'] = """- Her hair is one long lock down her back from behind her head (TS's back view), lying on her shoulder blades; it
  follows her back, not her head, so it hangs as she bends.  EA's Tanya, beside her in standing-8-facings.png, wears
  hers loose to the shoulders.
- Her top's pale front (TS: a few light olive pixels in the middle of her chest in the front views) is drawn as a
  light olive panel on the front of her top; the house green is TS's remap areas only.
- Her rifle is placed by TS's outline and colours alone.  The GDI pipeline's passes that lay the gun along TS's own
  find it as the longest straight run of the gun's colour, and her black rifle can't be told that way from her dark
  clothes and TS's black outlines.
- TS draws idle 1 and death 1 facing south-west, idle 2 and death 2 facing south-east (their first frames match those
  standing frames); the hand-off README says west and east.  They're drawn as TS's frames are.
- Frame 85 (unused) is a copy of 84."""
GROUND_CALL_CYB = """- No TS shadow: Nod never made it into the mod, so its units have no in-mod frames with TS's shadow in them (the
  GDI infantry's ground poses were fitted to TS's shadow as well as its outline).  These are fitted to TS's outline
  and colours alone, with the ground holding the body down."""
for _u in list(CALLS):
    CALLS[_u] = (GROUND_CALL_CYB if _u in ('cyborg', 'cyc2') else GROUND_CALL) + '\n' + CALLS[_u]

NODES = {u: (v['nodes'],) + tuple(v['marker']) for u, v in INFO.items()}


def _fill(words, width, first, rest):
    """words (keeping a double space after a full stop) filled to width: the first line after first, the rest after rest."""
    lines, cur = [], first
    for w in words:
        sep = '' if cur in (first, rest) and cur.strip() == '' or cur.endswith(('- ',)) and cur.strip() == '-' else ' '
        cand = cur + ('' if cur == first or cur == rest else sep) + w
        if len(cand) > width and cur.strip():
            lines.append(cur.rstrip())
            cur = rest + w
        else:
            cur = cand
    lines.append(cur.rstrip())
    return lines


def tidy(text, width=120):
    """the README's paragraphs refilled to width: its bullets ('- ' and their two-space continuation lines) as
    paragraphs; any other line over the width broken under its own hanging indent."""
    import re
    out = []
    L = text.split('\n')
    i = 0
    while i < len(L):
        line = L[i]
        if line.startswith('- '):
            para = [line[2:]]
            j = i + 1
            while j < len(L) and L[j].startswith('  ') and not L[j].startswith('   ') and L[j].strip():
                para.append(L[j][2:]); j += 1
            if any(len(x) > width for x in [line] + L[i + 1:j]):
                body = ' '.join(x.strip() for x in para)
                words = re.split(r'(?<=[.!?:;)"]) {2}| ', body)
                # (a full stop's double space kept: rejoin with two spaces where the source had them)
                toks = []
                for part in re.split(r'(?<=\.)  ', body):
                    ws = part.split(' ')
                    if toks:
                        ws[0] = ' ' + ws[0]
                    toks += ws
                out += _fill(toks, width, '- ', '  ')
            else:
                out += L[i:j]
            i = j
            continue
        if len(line) > width:
            m = re.match(r'^(\s*\S+(?:\s\S+)*?\s{2,})', line)
            indent = ' ' * (len(m.group(1)) if m and len(m.group(1)) < 40 else len(line) - len(line.lstrip()) + 2)
            lead = len(line) - len(line.lstrip())
            out += _fill(line.strip().split(' '), width, ' ' * lead, indent)
            i += 1
            continue
        out.append(line)
        i += 1
    return '\n'.join(out)
