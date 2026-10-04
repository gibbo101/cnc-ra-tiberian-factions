Disc Thrower (TS [E2]) in HD for Tiberian Factions: TSE2
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
            animation-sheet.png, death-1-sheet.png, death-2-sheet.png, crawl-sheet.png, fire-sheet.png
                                  the frame-by-frame check sheets: each frame as the mod draws it now (TS's
                                  sprite and shadow) beside HD
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
- The shape is fitted to the 8 standing frames together, then the rucksack and the orange patches, and the faceplate,
  on their own (each a few
  pixels a frame, which a fit of the whole soldier gives up for a pixel of silhouette elsewhere), then each facing's
  arms and head to its own frame.  Overlap with TS's frames in TS's camera: 0.84.
- The orange is drawn on TS's own orange ramp (its frames' eleven oranges, dark red-orange to light yellow-orange),
  as light on average as TS draws it: the HD light (the buildings', from the north-west) leaves the patches on the
  backs of his legs in his own shadow, where a plain orange came out brown.  TS draws them about as light standing,
  running and crawling, whichever way they face, so they keep only half their HD shading.
- The run is one smooth loop: every joint follows a short smooth curve (a Fourier series) through the 6 steps, so
  step 5 runs into step 0 like any step into the next and nothing jumps back to a start pose.  The legs follow one
  curve half a cycle apart (each thigh swings once a cycle), the arms swing in turn.  The loop is fitted to TS's 48 run
  frames together; each facing's arms and head then get their own smooth loop on top, held close to the shared one.
  Overlap 0.70; the furthest any landmark (hands, head, feet) moves from one step to the next is 6.4 TS px.
- The crawl is rebuilt from TS's own crawl frames (your notes: "view how og is doing it", "research how a body crawls
  prone"). It is a real prone crawl, done the way the army's low crawl and the leopard crawl are: flat and low on his
  front, up on his forearms with his head up to see. One forearm goes forward with the opposite knee, which is drawn
  up while the other leg lies straight back, and his body rolls a little towards that knee; then the other pair. TS
  drew this crawl only facing N, NW, W, SW and S, and its NE, E and SE crawl frames are those sprites flipped, pixel
  for pixel. One pose can't match both sides, which is what made the earlier crawls flail, so the crawl is fitted to
  the five facings TS drew and the flipped facings get the same pose mirrored, as TS's do. One stroke drives every
  joint, so the loop runs on with nothing jumping back. How far he is propped up, where he looks and how far each
  part moves are fitted to TS's crawl frames. Overlap 0.56, landmarks at most 4.5 TS px a step.
- The throw: TS's six frames a facing are one throw from the ready stance and back to it (the throwing arm drawn
  back and over, out forward, the follow-through and the recovery), so it is one smooth loop like the run, step for
  step with TS's frames: overlap 0.76.  A throw is quick: the throwing hand travels up to 18.9 TS px in a
  step, the body far less, and no step jumps out of line with the rest.  The disc leaves at the end of the throw (step
  6, as the hand-off README has it); the disc in flight is the game's effect.  The throw lying down the same: overlap
  0.64, the hand at most 14.6 TS px a step.
- Lying down: the two in-betweens fitted to TS's frames on the way down through kneeling on all fours (TS's second
  frame), from the standing pose to the prone one (the crawl's first step), so standing, down and prone run as one movement (0.79); getting up is the same two
  poses backwards, as TS's get-up frames are its lie-down frames backwards, pixel for pixel.
- The idles and deaths: each frame fitted to its TS frame starting from the one before, then the whole run of poses
  relaxed together (every frame pulled towards the middle of its neighbours), so they move smoothly; the idles start
  from the standing pose and come back to it.  Overlap: idles 0.84 and 0.82, deaths 0.69 and 0.62.
- The blood, frame by frame from TS's own pixels: TS's red (255,0,0, as TS and the mod draw it), each red pixel drawn on
  the ground it covers in TS's view, so a pool stays put as the body falls on it.
Against the mod's current frames the silhouettes overlap by 0.53 (standing 0.58, run 0.54, crawl 0.46, throw
0.51): those frames are TS's sprites scaled up 3.071 times, so this is the difference in TS's own camera above,
scaled up with them (a soldier's limbs are a few TS pixels wide, so a pixel counts for a lot), plus the 32-degree camera.


Keep (from the hand-off README)
-------------------------------
- The 267 x 208 canvas; every frame of the layout in TS's order (85, unused, included).
- The feet: the soldier's ground point lands where the mod's frames put TS's (TS's sprite x 3.071 at (38.68, 10.60));
  standing, the boots' lowest pixel is on canvas row 106-111 by facing, as the mod's own frames have it
  on 108-113 (the README: feet on 111).
- He stands as tall as the mod's frames (EA's Grenadier: see standing-8-facings.png).
- The shadow baked in at alpha 128 (50% black, blurred): the README's minimum, lighter than the buildings' 75%, as
  the mod's frames carry TS's at about 25% (your note: at 75% the falling deaths looked like floating).
- The release read on the last throw frame: the throw runs step for step with TS's, ending as TS's ends.


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 3.071 canvas px per TS pixel
  (the mod's frames are TS's sprite x 3.071), the soldier drawn 8% bigger about his feet, as E1: TS's sprite draws
  every pixel the soldier touches, so the model fitted to it is a little shorter and slimmer than the mod's frames.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the units' camera fill (EA's HD
  infantry are lit from the front); each part as light as TS draws it under that light (infcalib.py), the orange on
  TS's ramp (above).
- House colour: exactly 0,214,0 x (1 + 1.1 grain) on the shoulder pads, arms, hips and thighs; the -trim masks cover
  exactly those.


3D model (ts-e2-hd-3d/)
-----------------------
tse2.glb   the soldier in vertex colours, every sequence as a glTF animation, the mod's camera
- Nodes: DiscThrower > pelvis, hips, belt, abdomen, chest, vest, rucksack, helmet, mask, jaw, and
  left_/right_ thigh, thigh_back, thigh_low, shin, knee, boot, shoulder_pad, upper_arm, forearm, hand.
  Marker "throw": a marker in the right hand's palm, where the disc leaves it.
  Each part is one rigid solid, posed per frame by its node's translation and rotation.
- Animations, facing east (the 8-facing sequences use the east facing's frames; the idles and deaths play facing east
  too), at the game's speed (15 ticks a second); the looping ones end on their first frame again, so they loop without
  a seam:
    "stand"      frame 6
    "walk"       frames 44-49, 2 ticks a frame, loops
    "idle1"      frames 56-70, 2 ticks a frame
    "idle2"      frames 71-84, 2 ticks a frame
    "crawl"      frames 122-127, 2 ticks a frame, loops
    "death1"     frames 134-148, 2 ticks a frame
    "death2"     frames 149-163, 2 ticks a frame
    "fire"       frames 200-205, 1 tick a frame, loops
    "prone_fire" frames 248-253, 1 tick a frame, loops
    "lie_down"   frames 272-273, 2 ticks a frame
    "get_up"     frames 288-289, 3 ticks a frame
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (30.3 TS px, as the other TS units' models).
  Origin: the soldier's position on the ground.  He faces east (the mod's facing 6).
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 267 x 208 canvas
  exactly (checked by drawing the mesh through it over frame 6: overlap 0.925).
- The file passes Khronos's glTF validator: errors 0 warnings 0 infos 1 hints 0.
- Vertex colours: COLOR_0 albedo (no light or shadow; the orange parts in TS's mean orange), COLOR_1 house colour
  (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
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
  frame (deathshadow.py; the lengths and strengths are in src/e2_shadow_w.json).  Once he is down only a faint
  shadow hugs him, which the game drops (under alpha 128), as TS has none.
- TS drew his crawl only facing N, NW, W, SW and S; its NE, E and SE crawl frames are those sprites flipped, pixel
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
- Frame 85 (unused) is a copy of 84.


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
  tsshadow.py            TS's own shadow, read off the mod's frames, and its light (ts_light.json: fitted on
                         all six units' standing frames); the fits count it with SHADOW=w
  ground.py              how far a soldier TS shows on the ground floats off it (deaths, crawl, prone)
  deathfit2.py           a death fitted to TS's frames and shadow, from its last frame back to its first
  deathshadow.py         a death's shadow drawn in and faded as TS's own frames have it (UNIT_shadow_w.json)
  firepair.py, gunpass.py, gunline.py   fire as TS's alternating poses; a gun laid along TS's gun
  fitcheck.py, checksheet.py   the check sheets: a fit and its shadow in TS's camera; TS beside HD
e.g.  python3 infall.py e2 e2_shape.json out/          (every frame; or a list: out/ 8,9,10)
      python3 infcycle.py e2 e2_shape.json fire cyc.json 300            (refit the throw's shared cycle)
