Light Infantry (TS [E1]) in HD for Tiberian Factions: TSE1
==========================================================

Movement: EA's own (your note: "follow ea")
----------------------------------------------
The run follow EA's counterpart's HD frames from the Remastered install (same 267 x 208 canvas, scale and 32-degree camera), not TS's: each pose fitted to EA's outline and colours (skin, dark kit) on the shared skeleton, a body part at a time, the crawl as EA's leopard crawl read off its frames (one arm reaching straight out along the ground, the knee on that side drawn up and out) with its timing, lean and place fitted, and the run as EA's stride.  EA's timing is spread over TS's frame counts (the mod keeps TS's layout).  The deaths' blood is drawn where EA's pools land.  Where the notes below describe fitting the movement to TS's frames, EA's now replaces it; the soldier's sizes and kit are still read off TS.

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
            animation-sheet.png, death-1-sheet.png, death-2-sheet.png, crawl-sheet.png, fire-sheet.png
                                  the frame-by-frame check sheets: each frame as the mod draws it now (TS's
                                  sprite and shadow) beside HD
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
  Overlap with TS's frames in TS's camera: 0.78.
- The run is one smooth loop: every joint follows a short smooth curve (a Fourier series) through the 6 steps, so
  step 5 runs into step 0 like any step into the next and nothing jumps back to a start pose.  The legs follow one
  curve half a cycle apart (a real stride: each thigh swings once a cycle); the body stays on its spot with a steady
  bob and a lean of 20-30 degrees (TS's south view stands 2-5 px shorter than its standing soldier: that lean), the
  head level so the visor shows; the hands stay on the rifle, which swings from across his left side (TS's steps 0-2)
  to pointing ahead (3-5) and back.  The loop is fitted to TS's 48 run frames together; TS doesn't draw the rifle the
  same way in every facing (facing south it swings side to side), so each facing's arms, rifle and head then get their
  own smooth loop on top, held close to the shared one.  Overlap 0.63; the furthest any landmark (muzzle, rifle
  butt, hands, head, feet) moves from one step to the next is 9.4 TS px (the rifle is 12 long).
- The crawl is rebuilt from TS's own crawl frames (your notes: "view how og is doing it", "research how a body crawls
  prone"). It is a real prone crawl, done the way the army's low crawl and the leopard crawl are: flat and low on his
  front, up on his forearms with his head up to see. One forearm goes forward with the opposite knee, which is drawn
  up while the other leg lies straight back, and his body rolls a little towards that knee; then the other pair. TS
  drew it in all 8 facings, and all 8 are fitted together. The rifle goes forward in both hands with each stroke and
  draws back. One stroke drives every joint, so the loop runs on with nothing jumping back. How far he is propped up,
  where he looks and how far each part moves are fitted to TS's crawl frames. Overlap 0.56, landmarks at
  most 5.4 TS px a step.
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
  to its own.  Overlap 0.72 and 0.71.
- Lying down: the two in-betweens fitted to TS's frames on the way down through kneeling on all fours (TS's second
  frame), from the standing pose to the prone one (the crawl's first step), so standing, down and prone run as one movement (0.72); getting up is the same two
  poses backwards, as TS's get-up frames are its lie-down frames backwards, pixel for pixel.
- The idles and deaths: each frame fitted to its TS frame starting from the one before, then the whole run of poses
  relaxed together (every frame pulled towards the middle of its neighbours), so they move smoothly; the idles start
  from the standing pose and come back to it.  Overlap: idles 0.83 and 0.89, deaths 0.56 and 0.58.
- Effects, frame by frame from TS's own pixels: the muzzle flash (TS's three yellows, its shape kept, drawn smooth and
  hot: a white-yellow core, amber, orange edges) at the HD rifle's muzzle, hidden where the soldier stands in front of
  it; the blood in TS's red (255,0,0, as TS and the mod draw it), each red pixel drawn on the ground it covers in TS's
  view, so a pool stays put as the body falls on it.
Against the mod's current frames the silhouettes overlap by 0.51 (standing 0.54, run 0.44, crawl 0.42, fire
0.50): those frames are TS's sprites scaled up 3.068 times, so this is the difference in TS's own camera above,
scaled up with them (a soldier's limbs are a few TS pixels wide, so a pixel counts for a lot), plus the 32-degree camera.


Keep (from the hand-off README)
-------------------------------
- The 267 x 208 canvas; every frame of the layout in TS's order (85, unused, included).
- The feet: the soldier's ground point lands where the mod's frames put TS's (TS's sprite x 3.068 at (38.06, 10.57));
  standing, the boots' lowest pixel is on canvas row 106-112 by facing, as the mod's own frames have it
  on 108-111 (the README: feet on 111).
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
  exactly (checked by drawing the mesh through it over frame 6: overlap 0.907).
- The file passes Khronos's glTF validator: errors 0 warnings 0 infos 0 hints 0.
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


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
  frame (deathshadow.py; the lengths and strengths are in src/e1_shadow_w.json).  Once he is down only a faint
  shadow hugs him, which the game drops (under alpha 128), as TS has none.
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
  tsshadow.py            TS's own shadow, read off the mod's frames, and its light (ts_light.json: fitted on
                         all six units' standing frames); the fits count it with SHADOW=w
  ground.py              how far a soldier TS shows on the ground floats off it (deaths, crawl, prone)
  deathfit2.py           a death fitted to TS's frames and shadow, from its last frame back to its first
  deathshadow.py         a death's shadow drawn in and faded as TS's own frames have it (UNIT_shadow_w.json)
  firepair.py, gunpass.py, gunline.py   fire as TS's alternating poses; a gun laid along TS's gun
  fitcheck.py, checksheet.py   the check sheets: a fit and its shadow in TS's camera; TS beside HD
e.g.  python3 infall.py e1 e1_shape.json out/          (every frame; or a list: out/ 8,9,10)
      python3 infcycle.py e1 e1_shape.json walk cyc.json 300            (refit the run's shared cycle)
