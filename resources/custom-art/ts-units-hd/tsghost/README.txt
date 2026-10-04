Ghost Stalker (TS [GHOST]) in HD for Tiberian Factions: TSGHOST
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
            death-1-sheet.png, death-2-sheet.png, crawl-sheet.png, fire-sheet.png
                                  the frame-by-frame check sheets: each frame as the mod draws it now (TS's
                                  sprite and shadow) beside HD
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
  Overlap with TS's frames in TS's camera: 0.78.
- The run is one smooth loop: every joint follows a short smooth curve (a Fourier series) through the 6 steps, so
  step 5 runs into step 0 like any step into the next and nothing jumps back to a start pose (your note on the
  soldiers' run).  The loop is fitted to TS's 48 run frames together; each facing's arms, railgun and head then get
  their own smooth loop on top, held close to the shared one.  Overlap 0.72; the furthest any landmark (muzzle,
  railgun's back end, hands, head, feet) moves from one step to the next is 26.0 TS px.
- The crawl is rebuilt from TS's own crawl frames (your notes: "view how og is doing it", "research how a body crawls
  prone"). It is a real prone crawl, done the way the army's low crawl and the leopard crawl are: flat and low on his
  front, up on his forearms with his head up to see. One forearm goes forward with the opposite knee, which is drawn
  up while the other leg lies straight back, and his body rolls a little towards that knee; then the other pair. TS
  drew it in all 8 facings, and all 8 are fitted together. The railgun goes forward in both hands with each stroke
  and draws back. One stroke drives every joint, so the loop runs on with nothing jumping back. How far he is propped
  up, where he looks and how far each part moves are fitted to TS's crawl frames. Overlap 0.72, landmarks
  at most 23.3 TS px a step.
- Fire and fire prone: TS holds one pose through each facing's 6 frames (only the flash comes and goes), so each
  facing has one pose for all 6: fitted to the 8 facings' flash-free frames together, then each facing's arms, railgun
  and head to its own.  Overlap 0.84 and 0.78.
- Lying down: the two in-betweens fitted to TS's frames on the way down through kneeling on all fours (TS's second
  frame), from the standing pose to the prone one (the crawl's first step), so standing, down and prone run as one movement (0.78); getting up is the same two
  poses backwards, as TS's get-up frames are its lie-down frames backwards, pixel for pixel.
- The idles and deaths: each frame fitted to its TS frame starting from the one before, then the whole run of poses
  relaxed together (every frame pulled towards the middle of its neighbours), so they move smoothly; the idles start
  from the standing pose and come back to it.  Overlap: idles 0.91 and 0.85, deaths 0.70 and 0.71.
- The railgun in the deaths follows TS's: TS keeps it in plain view as he falls (flung up over his head, then lying
  out beside him; in death 2 swung out in one hand while the other arm flies up), so from the first falling frame
  it is in his right hand alone, his left arm free, and each frame also starts from the railgun laid along TS's own
  (the longest straight run of its green pixels in that frame); the frames are held together less tightly for the
  gun and his right arm than for his body, so it can swing as far as TS's does from one frame to the next.
- Effects, frame by frame from TS's own pixels: the railgun's flash (TS's yellows, its shape kept, drawn smooth and
  hot: a white-yellow core, amber, orange edges) at the HD railgun's muzzle, hidden where he stands in front of it;
  the blood in TS's red (255,0,0, as TS and the mod draw it), each red pixel drawn on the ground it covers in TS's
  view, so a pool stays put as the body falls on it.
Against the mod's current frames the silhouettes overlap by 0.50 (standing 0.47, run 0.48, crawl 0.48, fire
0.50): those frames are TS's sprites scaled up 3.0769 times, so this is the difference in TS's own camera above,
scaled up with them (a soldier's limbs are a few TS pixels wide, so a pixel counts for a lot), plus the 32-degree camera.


Keep (from the hand-off README)
-------------------------------
- The 267 x 208 canvas; every frame of the layout in TS's order (85, unused, included).
- The feet: the soldier's ground point lands where the mod's frames put TS's (TS's sprite x 3.0769 at (37.70, 10.86));
  standing, the boots' lowest pixel is on canvas row 104-113 by facing, as the mod's own frames have it
  on 105-118 (the README: feet on 111).
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
- Nodes: GhostStalker > pelvis, belt, abdomen, chest, vest, roll, roll_end_l, roll_end_r, hood, hood_top,
  face, rifle (the railgun), receiver, and left_/right_ thigh, shin, knee, boot, shoulder_pad, upper_arm,
  forearm, hand.
  Marker "muzzle": a marker on the railgun where the flash comes from.
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
  exactly (checked by drawing the mesh through it over frame 6: overlap 0.884).
- The file passes Khronos's glTF validator: errors 0 warnings 0 infos 1 hints 0.
- Vertex colours: COLOR_0 albedo (no light or shadow; the skin in TS's mean flesh tones), COLOR_1 house colour
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
  frame (deathshadow.py; the lengths and strengths are in src/ghost_shadow_w.json).  Once he is down only a faint
  shadow hugs him, which the game drops (under alpha 128), as TS has none.
- His forearms and hands are drawn in his upper arms' skin tone.  TS draws them darker (its shading), and drawn that
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
- Frame 85 (unused) is a copy of 84.


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
  tsshadow.py            TS's own shadow, read off the mod's frames, and its light (ts_light.json: fitted on
                         all six units' standing frames); the fits count it with SHADOW=w
  ground.py              how far a soldier TS shows on the ground floats off it (deaths, crawl, prone)
  deathfit2.py           a death fitted to TS's frames and shadow, from its last frame back to its first
  deathshadow.py         a death's shadow drawn in and faded as TS's own frames have it (UNIT_shadow_w.json)
  firepair.py, gunpass.py, gunline.py   fire as TS's alternating poses; a gun laid along TS's gun
  fitcheck.py, checksheet.py   the check sheets: a fit and its shadow in TS's camera; TS beside HD
e.g.  python3 infall.py ghost ghost_shape.json out/          (every frame; or a list: out/ 8,9,10)
