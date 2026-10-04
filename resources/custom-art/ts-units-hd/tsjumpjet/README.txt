Jumpjet Infantry (TS [JUMPJET]) in HD for Tiberian Factions: TSJUMPJET
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
            animation-sheet.png
                                  the frame-by-frame check sheets: each frame as the mod draws it now (TS's
                                  sprite and shadow) beside HD
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
  TS's camera: 0.77.
- The run is one smooth loop (every joint on a short smooth curve through the 6 steps, nothing jumps back to a start
  pose), fitted to TS's 48 run frames together, each facing's arms, rifle and head on their own smooth loop on top.
  Overlap 0.69; the furthest any landmark moves from one step to the next is 10.2 TS px.
- TS never lays the Jumpjet down. His crawl frames are his run frames, his fire-prone frames are his fire frames, and
  his lying-down and getting-up frames are his standing frames, pixel for pixel. HD does the same: 86-133 are the
  run, 212-259 the fire and 260-291 his standing pose in each facing.
- Fire and fire prone: TS holds one pose through each facing's 6 frames (only the flash comes and goes), so each
  facing has one pose for all 6.  Overlap 0.72 and 0.72.
- Flying: TS holds one pose a facing through its 6 flying frames, leaning into the flight, only the jet flames
  changing; so does HD: fitted to the 8 facings together, then each facing's arms, rifle and head.  Overlap 0.72.
  Hovering is TS's standing pose with the jets lit (0.73); firing in the air the flying pose firing (0.69).
- The jet flames, frame by frame from TS's own pixels (its three flame yellows), drawn smooth and hot (a white-yellow
  core, amber, orange edges) at the HD nozzles, hidden where he is in front of them; firing in the air, the pixels
  nearer his rifle than his nozzles are the muzzle flash, drawn at the muzzle.  The muzzle flash keeps TS's red tips.
- The tumble: hit in the air, he tumbles and falls, ending on the ground in TS's blood; each frame fitted to its TS
  frame from the one before, then the run of poses relaxed together (0.68).
- The idles: as the other infantry (0.83 and 0.81).
Against the mod's current frames the silhouettes overlap by 0.61 (standing 0.62, run 0.58, crawl 0.58, fire
0.60): those frames are TS's sprites scaled up 3.116 times, so this is the difference in TS's own camera above,
scaled up with them, plus the 32-degree camera.


Keep (from the hand-off README)
-------------------------------
- The 267 x 208 canvas; every frame of the layout in TS's order (the empty deaths and the tumble included).
- The feet: the soldier's ground point lands where the mod's frames put TS's (TS's sprite x 3.116 at (36.93, 9.54));
  standing, the boots' lowest pixel is on canvas row 106-109 by facing, as the mod's own frames have it
  on 108-108 (the README: feet on 111).
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
- Nodes: JumpjetInfantry > pelvis, belt, abdomen, chest, vest, jetpack, left_nozzle, right_nozzle, left_wing,
  right_wing, helmet, mask, jaw, rifle, receiver, and left_/right_ thigh, shin, knee, boot, shoulder_pad,
  upper_arm, forearm, hand.
  Marker "muzzle": a marker on the rifle where the flash comes from.
  Markers "nozzle_left", "nozzle_right": the jets' mouths, where the flames come out.
  Each part is one rigid solid, posed per frame by its node's translation and rotation.
- Animations, facing east (the 8-facing sequences use the east facing's frames; the idles and the tumble play facing
  east too), at the game's speed (15 ticks a second); the looping ones end on their first frame again:
    "stand"      frame 6
    "walk"       frames 44-49, 2 ticks a frame, loops
    "idle1"      frames 56-70, 2 ticks a frame
    "idle2"      frames 71-85, 2 ticks a frame
    "crawl"      frames 122-127, 2 ticks a frame, loops
    "fire"       frames 200-205, 1 tick a frame, loops
    "prone_fire" frames 248-253, 1 tick a frame, loops
    "lie_down"   frames 272-273, 2 ticks a frame
    "get_up"     frames 288-289, 3 ticks a frame
    "fly"        frames 328-333, 2 ticks a frame, loops
    "hover"      frames 376-381, 2 ticks a frame, loops
    "fire_fly"   frames 424-429, 1 tick a frame, loops
    "tumble"     frames 436-450, 2 ticks a frame
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (30.3 TS px, as the other TS units' models).
  Origin: the soldier's position on the ground.  He faces east (the mod's facing 6).
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 267 x 208 canvas
  exactly (checked by drawing the mesh through it over frame 6: overlap 0.852).
- The file passes Khronos's glTF validator: errors 0 warnings 0 infos 3 hints 0.
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
- TS never lays him down: his crawl frames are his run frames, fire prone his fire frames, lying down and getting up
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
  the hand-off README says west and east.  They're drawn as TS's frames are.  Frame 85 is idle 2's last frame.
- The tumble ends lying flat on the ground where TS's does, fitted to TS's shadow as well as its outline (it ended
  half sitting with a leg up).


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
  tsshadow.py            TS's own shadow, read off the mod's frames, and its light (ts_light.json: fitted on
                         all six units' standing frames); the fits count it with SHADOW=w
  ground.py              how far a soldier TS shows on the ground floats off it (deaths, crawl, prone)
  deathfit2.py           a death fitted to TS's frames and shadow, from its last frame back to its first
  deathshadow.py         a death's shadow drawn in and faded as TS's own frames have it (UNIT_shadow_w.json)
  firepair.py, gunpass.py, gunline.py   fire as TS's alternating poses; a gun laid along TS's gun
  fitcheck.py, checksheet.py   the check sheets: a fit and its shadow in TS's camera; TS beside HD
e.g.  python3 infall.py jj jj_shape.json out/          (every frame; or a list: out/ 8,9,10)
