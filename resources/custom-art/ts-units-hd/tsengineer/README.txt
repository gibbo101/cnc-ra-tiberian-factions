Engineer (TS [ENGINEER]) in HD for Tiberian Factions: TSENGINEER
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
            animation-sheet.png, death-1-sheet.png, death-2-sheet.png, crawl-sheet.png
                                  the frame-by-frame check sheets: each frame as the mod draws it now (TS's
                                  sprite and shadow) beside HD
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
- His suit is bulkier than the soldiers' armour: the fit has room for wider hips and a bigger hood and body.  TS drew
  its sprites on black, so the edge pixels of a bright part come out dark; the fit counts the soldier's own edge
  pixels as dark, as TS's are, and his yellow parts are fitted to TS's yellow inside them.
- The shape is fitted to the 8 standing frames together, then the respirator and goggles on their own, then each
  facing's arms and head to its own frame.  Overlap with TS's frames in TS's camera: 0.83.
- The yellow is drawn on TS's own yellow ramp (its frames' ten yellows, orange-yellow to pale yellow), each part as
  light on average as TS draws it: the HD light (the buildings', from the north-west) leaves much of him in shadow,
  where a plain yellow went olive.
- The run is one smooth loop: every joint follows a short smooth curve (a Fourier series) through the 6 steps, so
  step 5 runs into step 0 like any step into the next and nothing jumps back to a start pose.  It is a sprint, as
  TS draws it (its side views, frames 20-25 and 44-49: the trailing leg thrown back level behind the hip, one leg then
  the other, the front foot reaching well ahead): the legs follow one curve half a cycle apart; the left arm swings
  against them, the right carries the toolbox with a short swing.  The loop is fitted to TS's 48 run frames together;
  each facing's arms and head then get their own smooth loop on top, held close to the shared one.  Overlap
  0.67; the furthest any landmark (hands, head, feet) moves from one step to the next is 5.6 TS px.
- The crawl is rebuilt from TS's own crawl frames (your notes: "view how og is doing it", "research how a body crawls
  prone"). It is a real prone crawl, done the way the army's low crawl and the leopard crawl are: flat and low on his
  front, up on his forearms with his head up to see. One forearm goes forward with the opposite knee, which is drawn
  up while the other leg lies straight back, and his body rolls a little towards that knee; then the other pair. TS
  drew this crawl only facing N, NW, W, SW and S, and its NE, E and SE crawl frames are those sprites flipped, pixel
  for pixel. One pose can't match both sides, which is what made the earlier crawls flail, so the crawl is fitted to
  the five facings TS drew and the flipped facings get the same pose mirrored, as TS's do. The toolbox stays in his
  right hand, standing on the ground square to him, and only moves when his hand does. One stroke drives every joint,
  so the loop runs on with nothing jumping back. How far he is propped up, where he looks and how far each part moves
  are fitted to TS's crawl frames. Overlap 0.68, landmarks at most 3.1 TS px a step.
- Lying down: the two in-betweens fitted to TS's frames on the way down through kneeling on all fours (TS's second
  frame), from the standing pose to the prone one (the crawl's first step), so standing, down and prone run as one movement (0.73); getting up is the same two
  poses backwards, as TS's get-up frames are its lie-down frames backwards, pixel for pixel.
- The idles and deaths: each frame fitted to its TS frame starting from the one before, then the whole run of poses
  relaxed together (every frame pulled towards the middle of its neighbours), so they move smoothly; the idles start
  from the standing pose and come back to it.  Overlap: idles 0.84 and 0.81, deaths 0.71 and 0.64.
- The blood, frame by frame from TS's own pixels: TS's red (255,0,0, as TS and the mod draw it), each red pixel drawn on
  the ground it covers in TS's view, so a pool stays put as the body falls on it.
Against the mod's current frames the silhouettes overlap by 0.58 (standing 0.61, run 0.52, crawl 0.57): those frames
are TS's sprites scaled up 3.0755 times, so this is the difference in TS's own camera above, scaled up with them (a
soldier's limbs are a few TS pixels wide, so a pixel counts for a lot), plus the 32-degree camera.


Keep (from the hand-off README)
-------------------------------
- The 267 x 208 canvas; every frame of the layout in TS's order (85, unused, and the empty fire frames included).
- The feet: the soldier's ground point lands where the mod's frames put TS's (TS's sprite x 3.0755 at (37.91, 10.46));
  standing, the boots' lowest pixel is on canvas row 107-112 by facing, as the mod's own frames have it
  on 105-112 (the README: feet on 111).
- He stands as tall as the mod's frames (EA's Engineer: see standing-8-facings.png).
- The shadow baked in at alpha 128 (50% black, blurred): the README's minimum, lighter than the buildings' 75%, as
  the mod's frames carry TS's at about 25% (your note: at 75% the falling deaths looked like floating).


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 3.0755 canvas px per TS pixel
  (the mod's frames are TS's sprite x 3.0755), the soldier drawn 8% bigger about his feet, as E1.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the units' camera fill (EA's HD
  infantry are lit from the front); each part as light as TS draws it under that light (infcalib.py), the yellow on
  TS's ramp (above).
- House colour: exactly 0,214,0 x (1 + 1.1 grain) on the shoulder pads, upper arms and thighs; the -trim masks cover
  exactly those.


3D model (ts-engineer-hd-3d/)
-----------------------------
tsengineer.glb   the soldier in vertex colours, every sequence as a glTF animation, the mod's camera
- Nodes: Engineer > pelvis, belt, abdomen, chest, vest, pack, toolbox, lid, helmet, mask (the
  respirator), jaw, goggle_l, goggle_r, and left_/right_ thigh, shin, knee, boot, shoulder_pad, upper_arm, forearm, hand.
  Each part is one rigid solid, posed per frame by its node's translation and rotation; the toolbox and its lid
  are posed with his right hand.
- Animations, facing east (the 8-facing sequences use the east facing's frames; the idles and deaths play facing east
  too), at the game's speed (15 ticks a second); the looping ones end on their first frame again, so they loop without
  a seam (no fire animations: he has none):
    "stand"      frame 6
    "walk"       frames 44-49, 2 ticks a frame, loops
    "idle1"      frames 56-70, 2 ticks a frame
    "idle2"      frames 71-84, 2 ticks a frame
    "crawl"      frames 122-127, 2 ticks a frame, loops
    "death1"     frames 134-148, 2 ticks a frame
    "death2"     frames 149-163, 2 ticks a frame
    "lie_down"   frames 272-273, 2 ticks a frame
    "get_up"     frames 288-289, 3 ticks a frame
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (30.3 TS px, as the other TS units' models).
  Origin: the soldier's position on the ground.  He faces east (the mod's facing 6).
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 267 x 208 canvas
  exactly (checked by drawing the mesh through it over frame 6: overlap 0.930).
- The file passes Khronos's glTF validator: errors 0 warnings 0 infos 0 hints 0.
- Vertex colours: COLOR_0 albedo (no light or shadow; the yellow parts in TS's mean yellows), COLOR_1 house colour
  (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
- His crawl pushes along the ground with his legs, a knee drawn up to the side in turn and the leg driving back
  (your note on the Disc Thrower's crawl: "isnt kicking their legs against the floor").  The first crawls' legs were
  bent up in the air: the fit could only turn the thigh out a little at the hip, so every bend of the knee lifted the
  foot off the ground.  With the thigh turned out, the knee bends along the ground; the stroke is fitted to TS's crawl
  frames, lying on the ground.
- The deaths, crawl and prone frames are fitted to TS's shadow as well as its outline (your notes: "leg in the air
  way above the shadow", "ours are hovering above the ground").  From TS's camera a leg raised in the air and a leg
  lying further back look the same, and the first fits took the floating one.  TS's own shadow, which the mod's
  frames carry, tells them apart: its light (from the north-north-west, 50 degrees up) is read off all six units' standing
  frames, and each frame's shadow is fitted to TS's.  Wherever TS shows him down, his hips, chest, knees and feet lie
  on the ground (propped on his forearms when prone), and each death is fitted from its last frame, lying flat,
  back to its first, so he falls the way TS's does.
- A dying soldier's shadow follows TS's, frame by frame (your note: "on the og's the shadow disappears as the unit
  falls"): TS's shrinks as he goes down and is all but gone once he lies on the ground.  Each death frame's shadow is
  drawn in under him (its light raised, so it shortens) and then faded, to show as much of it as TS shows round its
  frame (deathshadow.py; the lengths and strengths are in src/eng_shadow_w.json).  Once he is down only a faint
  shadow hugs him, which the game drops (under alpha 128), as TS has none.
- TS drew his crawl only facing N, NW, W, SW and S; its NE, E and SE crawl frames are those sprites flipped, pixel
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
- Frame 85 (unused) is a copy of 84.


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
  tsshadow.py            TS's own shadow, read off the mod's frames, and its light (ts_light.json: fitted on
                         all six units' standing frames); the fits count it with SHADOW=w
  ground.py              how far a soldier TS shows on the ground floats off it (deaths, crawl, prone)
  deathfit2.py           a death fitted to TS's frames and shadow, from its last frame back to its first
  deathshadow.py         a death's shadow drawn in and faded as TS's own frames have it (UNIT_shadow_w.json)
  firepair.py, gunpass.py, gunline.py   fire as TS's alternating poses; a gun laid along TS's gun
  fitcheck.py, checksheet.py   the check sheets: a fit and its shadow in TS's camera; TS beside HD
e.g.  python3 infall.py eng eng_shape.json out/          (every frame; or a list: out/ 8,9,10)
