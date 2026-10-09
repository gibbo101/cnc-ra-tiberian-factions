Rocket Infantry (TS [E3], Nod) in HD for Tiberian Factions: TSE3
==============================================================

frames/     tse3-0000.png ... tse3-0291.png: 292 frames on the infantry canvas (267 x 208), each
            with a -trim.png (white = house colour, antialiased), numbered as TS's own sequence (E1Sequence, which
            the mod keeps):
              0-7      standing, one a facing; facings counter-clockwise from north (0 N, 1 NW, 2 W, 3 SW, 4 S, 5 SE,
                       6 E, 7 NE)
              8-55     the run: 6 steps a facing (frame = 8 + facing x 6 + step), 2 ticks a step, looping
              56-70    idle 1 (TS draws it facing south-west);  71-84  idle 2 (facing south-east);  85 (unused) = 84
              86-133   the crawl: 6 steps a facing, looping; its first step is the prone pose
              134-148  death 1 (facing south-west);  149-163  death 2 (facing south); both end lying flat
              164-211  fire: 6 frames a facing, 1 tick a frame, the flash where TS has it
              212-259  fire prone, the same
              260-275  lying down, 2 frames a facing;  276-291  getting up: the same two backwards (TS's are)
previews/   run-8-facings.gif, crawl-8-facings.gif, fire-8-facings.gif, fire-prone-8-facings.gif
                                  every facing at once, TS's sprite above HD
            run-west.gif, run-south.gif, crawl-west.gif, crawl-south.gif, fire-west.gif, fire-south.gif
                                  TS's sprite | TS's sprite scaled onto the canvas | HD, at the game's speed
            idle-1.gif, idle-2.gif, death-1.gif, death-2.gif      the same for the one-facing sequences
            lie-down-get-up-W.gif, lie-down-get-up-SE.gif         standing -> down -> prone -> up -> standing
            standing-8-facings.png    TS's sprite, scaled, HD and EA's Rocket Soldier, each facing
            masks.png                 the head close up in 8 facings: TS, scaled, HD
            animation-sheet.png, death-1-sheet.png, death-2-sheet.png, crawl-sheet.png, fire-sheet.png
                                  the frame-by-frame check sheets: each frame as the mod draws it now (TS's sprite
                                  scaled onto the canvas) beside HD
            shape-run.png, shape-crawl.png    TS's frames as colour classes beside the model's, in TS's own camera
ts-e3-hd-3d/   the 3D model in its own zip (ts-e3-hd-3d.zip) next to this folder
src/        the model, its fits, the renderer and the checks (see Rebuilding below)

Nod never had frames in the mod, so where the GDI infantry's previews show the mod's current frame, these show TS's
sprite scaled onto the canvas the way the mod scales the GDI Light Infantry's (3.068 times, nearest pixel, at the same
place).


What it is
----------
The posable soldier the six GDI infantry are made from (inf.py), with the Rocket Infantry's own sizes, gear and colours
(infunit.py), fitted to TS's own E3 frames in TS's camera (silhouette and colour classes, TS's flash and blood left
out) and drawn the way the GDI infantry are.
- The look (your makeover, from your Nod rocket trooper concept, in the soldiers' armour style): a full dark
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
- The launcher: a light grey tube 14.7 TS px long and 2.1 thick (TS's side views), dark rims at either end, on
  his right shoulder and held there by both hands under it (a dark grip block between them and the tube), as TS draws
  it in every standing frame: pointing up and ahead over his shoulder.
- His body: near-black and dark grey (TS: his helmet, chest, back and belt), a dark pack and pouch on his back; house
  green on the shoulder pads, upper arms and thighs (TS's remap areas); light grey knees and lower legs, dark boots.
- Standing: one pose fitted to the 8 standing frames together, then each facing's arms, launcher and head to its own
  frame.  Overlap with TS's frames in TS's camera: 0.76.
- The run is one smooth loop: every joint follows a short smooth curve (a Fourier series) through the 6 steps, so step 5
  runs into step 0 like any step into the next.  The loop is fitted to TS's 48 run frames together; each facing's arms,
  launcher and head then get their own smooth loop on top, held close to the shared one.  Overlap 0.62; the furthest any
  landmark (the launcher's mouth and back end, hands, head, feet) moves from one step to the next is 6.8 TS px.
- The crawl is a real prone crawl, as the GDI infantry's: flat and low on his front, up on his forearms with his head
  up, one forearm going forward with the opposite knee drawn up to the side while the other leg lies straight back, then
  the other pair, the legs pushing against the ground.  All 8 facings are fitted together to TS's crawl frames; one
  stroke drives every joint, so the loop runs on with nothing jumping back.  Overlap 0.62, landmarks at most 5.5 TS px a
  step.
- Fire and fire prone: TS's own poses in each facing, fitted to its frames, the launcher laid along TS's and its
  muzzle where TS's flash starts.  Overlap 0.79 and 0.67.
- Lying down: the two in-betweens fitted to TS's frames on the way down, from the standing pose to the prone one (the
  crawl's first step), so standing, down and prone run as one movement (0.76); getting up is the same two
  poses backwards, as TS's get-up frames are its lie-down frames backwards.
- The idles and deaths: each frame fitted to its TS frame starting from the one before, then the whole run of poses
  relaxed together (every frame pulled towards the middle of its neighbours), so they move smoothly; the idles start
  from the standing pose and come back to it.  Each death is then fitted again from its last frame, lying on the
  ground, back to its first, so he falls the way TS's does.  Overlap: idles 0.84 and 0.81, deaths 0.69 and 0.71.
- Effects, frame by frame from TS's own pixels: the flash (TS's yellows and reds, its shape kept, drawn
  smooth and hot) at the HD launcher's muzzle, hidden where he stands in front of it; the blood in TS's red
  (255,0,0), each red pixel drawn on the ground it covers in TS's view, so a pool stays put as the body
  falls on it.
Against TS's sprite scaled onto the canvas the silhouettes overlap by 0.60 (standing 0.60, run
0.55, crawl 0.58, fire 0.62): the scaled sprite is TS's own camera above, blown up, so this is
that difference scaled up with it (a soldier's limbs are a few TS pixels wide, so a pixel counts for a lot), plus the
32-degree camera.


Keep (from the hand-off README)
-------------------------------
- The 267 x 208 canvas; every frame of E1Sequence (292 frames, 85 unused included) in TS's order.
- The feet: on the GDI infantry's feet point; standing, the boots' lowest pixel is on canvas row 106-110
  by facing (the README: (133.5, 111), EA's Minigunner's).
- The size: the GDI infantry's scale (3.068 canvas px a TS px, the soldier drawn 8% bigger about the feet: 3.31), so he
  stands beside them as TS has him beside the Light Infantry, and as tall as EA's HD infantry (your note: "standard
  infantry should match the RA / TD inf for size"): standing he is 65-79 px from his feet to the top of his head by
  facing (the hand-off README: about 21 TS px, about 68 px at its 3.25).  standing-8-facings.png has EA's Rocket Soldier
  beside him.
- The shadow baked in at alpha 128 (50% black, blurred), as the GDI infantry's.  TS's decoded sprite has no shadow
  frames, so it is the HD soldier's own, cast by the buildings' light.  In the deaths it draws in under him and fades
  as he goes down, as the GDI infantry's do (your note on them: "on the og's the shadow disappears as the unit falls"):
  with no TS shadow to read, how much it shows in each frame is how much shadow the fitted body casts under TS's own
  light (read off the GDI units' frames), against the standing frames (deathshadow.py; the lengths and strengths are
  in src/e3_shadow_w.json).
- House colour pure green on the shoulder pads, upper arms and thighs; the -trim masks cover exactly those.
- The bright yellow flash on the fire frames where TS has it, standing and prone, and nothing else in those
  frames as bright, so the muzzle can be measured from it.


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north, as the GDI infantry's.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the units' camera fill (EA's HD
  infantry are lit from the front), as bright as the GDI infantry; each part as light as TS draws it under that light
  (infcalib.py).
- House colour: exactly 0,214,0 x (1 + 1.1 grain) on the shoulder pads, upper arms and thighs.


3D model (ts-e3-hd-3d/)
--------------------------
tse3.glb   the soldier in vertex colours, every sequence as a glTF animation, the mod's camera
- Nodes: RocketInfantry > pelvis, belt, abdomen, chest, vest, pack, pouch, helmet, mask, jaw, launcher, launcher_back,
  launcher_mouth, launcher_grip, and left_/right_ thigh, shin, knee, boot, shoulder_pad, upper_arm,
  forearm, hand.
  Marker "muzzle": a marker at the launcher's mouth, where the flash comes from.
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
  exactly (checked by drawing the mesh through it over frame 6: overlap 0.901).
- The file passes Khronos's glTF validator: errors 0 warnings 0 infos 1 hints 0.
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
- No TS shadow: Nod never made it into the mod, so its units have no in-mod frames with TS's shadow in them (the
  GDI infantry's deaths, crawl and prone were fitted to TS's shadow as well as its outline).  These are fitted to
  TS's outline and colours alone, with the ground holding the body down: wherever TS shows it down, its hips, chest,
  knees and feet lie on the ground (propped on its forearms when prone), and each death is fitted from its last
  frame, lying flat, back to its first.
- The launcher rides on his right shoulder in every standing facing, as TS draws it (pointing up and ahead over the
  shoulder); EA's Rocket Soldier carries his at his hip instead.
- In the run the launcher stays where each facing's smooth loop holds it, steady on his shoulder as TS's is.  The GDI
  pipeline's last pass lays the gun along TS's own gun frame by frame; TS's launcher is a straight grey bar with no
  front or back, and that pass turned it end for end between steps, so it isn't used for him.
- TS draws idle 1 and death 1 facing south-west, idle 2 facing south-east and death 2 facing south (their first
  frames match those standing frames); the hand-off README says west and east.  They're drawn as TS's frames are.
- Frame 85 (unused) is a copy of 84.


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy, Pillow and cma.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included.  The scripts read the GDI hand-off's folder layout:
nodmirror.py lays the Nod hand-off out that way (TS's sprite, the sprite scaled onto the canvas, EA's reference
strips): NOD_HANDOFF=<the Nod hand-off> EA_UNITS=<RA + TD HD Units> TS_HANDOFF=<out> python3 nodmirror.py e3, then
the rest with TS_HANDOFF=<out>.
  inf.py                 the posable soldier (shape S, pose Q) as convex solids (the launcher: kit 'e3');  rc.py  the
                         ray caster
  infunit.py             each unit's own data (the Rocket Infantry: its kit, colour classes, sizes, colours)
  inffit.py              the fit's loss in TS's camera, and the shape + standing fit (e3_shape.json); infrefine.py
                         each facing's own arms, launcher and head (e3_stand_frames.json); infcalib.py  the colours
                         read off TS's frames
  infcycle.py            the run as a smooth loop: the shared cycle (e3_walk_cyc.json), each facing's own loop
                         (e3_walk_faces.json) and every frame's pose (e3_walk_frames.json); infphase.py  each
                         facing's start step; gunpass.py  a weapon laid along TS's, frame by frame
  crawlbio.py            the crawl, a real prone crawl fitted to TS's crawl frames (e3_crawlfit.json,
                         e3_crawl_frames.json); crawlfit.py  every crawl frame
  infstatic.py, firepair.py   fire and fire prone (e3_fire_frames.json, e3_prone_fire_frames.json)
  infliedown.py          lying down and getting up;  infsmooth.py, deathfit2.py  the idles and deaths
  infrender.py           an HD frame;  infx.py  the flash;  infall.py  all 292 frames with flash and blood;
                         deathshadow.py  the deaths' shadows
  infexport.py           the .glb;  infpreview.py  the previews;  infreport.py  the numbers above
  infcheck.py, infmasks.py, checksheet.py, animsheet.py, cyclesheet.py, motion.py   the checks
  infpackage.py, nodreadme.py   this package (frames, previews, model, src, this README)
e.g.  python3 infall.py e3 e3_shape.json out/          (every frame; or a list: out/ 8,9,10)
