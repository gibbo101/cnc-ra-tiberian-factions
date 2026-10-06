Juggernaut (Firestorm [JUGG]) in HD for Tiberian Factions: TSJUGG  (v2.1: on the Titan's legs)
===================================================================================================

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
            titan-legs.png            TS's sprite, HD and the HD Titan's leg frame, walk step 0 in each facing
            rest-8-facings.png, aim-8-facings.png   the deployed piece, the mod's frames beside HD
            scale.png                 next to the HD harvester and the HD Titan, as the game draws them
            shape-walker.png, shape-cabin.png, shape-base.png   TS's sprites as colour classes beside the model's,
                                      in TS's own camera
ts-jugg-hd-3d/   the 3D models and the barrel tips, in their own zip (ts-jugg-hd-3d.zip) next to this folder
src/        the model, its fits, the renderers and the checks (see Rebuilding below)


v2: the Titan's legs (Luke: "use the Titan's legs")
----------------------------------------------------
TS draws the Juggernaut on the Titan's own legs, and v2 follows it:
- Walking: below the body, every pixel of TS's JUGGER walk frames is a pixel of MMCH's (the Titan's leg sprite), the
  same frame for frame, 3 TS px higher.  So the walker stands on the HD Titan's legs as signed off: their shape, their
  paint and their walk (the Titan's gait, fitted to all 120 of TS's walk frames, here at TS's 15 steps), the feet on
  the Juggernaut's ground.  The Titan's waist (pelvis, bearing ring, dome) takes the place of v1's olive hip block,
  under the body; the body rides the gait's bob (JUGGER's own bob, which v1 fitted step by step, follows the same
  curve).
- Deployed: TS's base frame (DJUGG 0) is MMCH's pixels too.  Its front limb is the walker's near leg where the walker
  stands, and the pivot the cabin turns on is MMCH's dome, moved 3 px right and 3 px down: onto the cabin's turning
  axis (it lands 0.1 px from it).  So the base is the Titan's two legs planted where the walker stands and the
  Titan's waist on the cabin's axis, the cabin turning on its dome as the Titan's upper body does, with the two side
  limbs as fitted.  v1's pivot column and rim were the fit's reading of those dome pixels.
- The deploy: the legs stay planted; under the sliding body the waist moves onto the cabin's axis in frames 7-8, as
  TS's dome pixels do (DJUGGMK frames 0-6 have them where the walker carries them, 7 two thirds of the way, 8-16 on the
  axis).
- The legs are lit as the HD Titan's are: on their own, as TS lights its leg sprite (they take shadow and sky cover
  only from themselves), the waist in the body's shadow and cover so it reads dark, as TS's does.  The cabin, body
  and side limbs are lit as in v1.
- The whole unit sits a quarter of a canvas pixel lower than v1 (see Look: it keeps the lowest body pixel at y 363
  on the Titan's toes), so the barrel tips in muzzle.txt are a quarter of a pixel lower too.
Everything else is as v1 (signed off at the shape check): the body, the cabin, the barrels, the deploy's timing.


v2.1: the antenna (Luke: "remove the box and go for a Titan-esque antenna")
---------------------------------------------------------------------------
The house-colour box TS draws on the roof's back corner is gone; in its place stands the HD Titan's antenna: a plain
black rod 0.45 px in radius, standing 16 px above the roof as the Titan's stands above its shell.  The deployed cabin
has it too (TS's cabin is the same body).  It is not house colour, so the -trim masks no longer have the box.


What it is
----------
One 3D model of the walker and one of the deployed piece, fitted to TS's own art and drawn the way the HD buildings and
the other units are:
- the walker's body fitted to all 120 of TS's JUGGER frames (8 facings x 15 steps), on the HD Titan's legs and walk
  (above).  At step 0 its silhouette overlaps TS's by 0.79 on average in TS's own camera (0.74 to 0.83 by
  facing; TS's legs are a few pixels wide, so a pixel counts for a lot; v1's legs, fitted to JUGGER itself, 0.82);
- the cabin fitted to DJUGG_A's 32 facings (overlap 0.85); the base, the Titan's legs and waist and the two side
  limbs, against DJUGG frame 0: 0.86 (v1's column, fitted to that frame, 0.89);
- the barrels are TS's own DJUGGBAR.VXL, voxel by voxel, in its colours and normals, at the size and place the mod's
  deployed frames draw them, hinged at the breech.
Walker: the house-green body with the light grey hatch on its roof (its dark slot, the slit across its front, the dark
panel in its top), the Titan's black antenna on the roof's back corner, the three khaki barrel housings side by side
with the steel muzzle brakes and their two slots; under it the Titan's waist
and its two legs: gold thighs with their armour plates' edges, steel knee spurs with dark tips, gold shins and
split-toed feet, steel joints, round hip joints.
Deployed: the Titan's two legs planted as TS's base draws them (TS's front limb is the walker's near leg, pixel for
pixel), its waist on the cabin's axis, the two side limbs; the cabin turning on the dome; the three barrels.
The deploy follows TS's DJUGGMK frame by frame, what moves when measured off TS's frames: the west limb slides out
(frames 1-5), the east limb (4-12), the body slides back onto the pivot (6-10) and the waist moves under it (7-8), the
housings telescope forward (10-11) and the barrels slide out of them (12-16).

Against the mod's current frames the silhouettes overlap by 0.72: walk 0.72, at rest 0.74,
aiming 0.72, the deploy 0.71.  Those frames are TS's sprites scaled up 6.3 times, so this is mostly
the difference above in TS's own camera, scaled up with them.


Keep (from the hand-off README)
-------------------------------
- The 448 canvas, 202 frames in the 120 / 32 / 32 / 18 split.
- One ground line: the lowest body pixel is at canvas y 363 in every deployed and deploy frame (and the walk's
  ground point is the same; the walk's lowest pixel moves with the feet, 308-363 by facing, as the mod's
  310-361).
- Deploy frame 184 = walk frame 45 and 201 = rest frame 132, exactly.
- The barrel tips where the model puts them: ts-jugg-hd-3d/muzzle.txt lists each barrel's tip and their mean on the
  canvas for every rest and aim frame (120-183), for the fire points.
- Shadows: black at alpha 191 (75%), blurred, as the buildings'; within 14 px of the canvas edge they fade out.


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.33 canvas px per TS pixel,
  the size the mod has now.  TS's sprite point (x, y) sits at canvas (6.33 x - 76.72, 6.33 y + 4.58): the mod's frames
  matched to TS's (overlap 0.97), then 4.75 px up, because the 32-degree camera draws ground in front of the unit
  about 3 px lower than TS's 30 degrees and the ground line must stay at y 363 (v1 was 5 px up: the Titan's toes
  end a little short of v1's feet, so v2 sits a quarter of a canvas pixel lower to keep the lowest body pixel there).
  The HD Titan's canvas is 6.4 px per TS pixel, so the legs are 1% smaller here, each at its own canvas's scale.
- The deployed piece stands where TS's deploy puts it against the walker (DJUGGMK's frame 0 is JUGGER's CW5 frame
  moved by (1, 14) TS px).
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides facing
  the camera as on the other units.  The game draws this canvas at two thirds (8 canvas px per classic pixel), so the
  outline, the shadow's blur and the grain are 1.5 times as wide on the canvas, as on the Titan's.
- The shadow falls as the other walkers' do (62% as long as the buildings'), so it stays on the canvas.
- Colours read from TS's frames: house green 0,214,0 x (1 + 1.1 grain) on the body (the -trim masks cover exactly
  that); the antenna the HD Titan's black; the hatch light grey with dark slots; khaki housings and barrels; steel muzzles;
  the legs and waist the HD Titan's (its yellow-brown paint, TS's ochre ramp; steel joints and spurs).
- Facing east the barrels reach the canvas's right edge in three rest frames, as they do in six of the mod's: the
  canvas is the mod's.


3D models (ts-jugg-hd-3d/)
-------------------------
tsjugg-walker.glb     the walker facing east on the Titan's legs, its walk as a glTF animation ("walk": 15 steps,
                      0.2 s each, looping)
tsjugg-deployed.glb   the deployed piece: the base (the Titan's legs as TS draws them deployed facing south-west, the
                      waist on the cabin's axis, the side limbs), the cabin turned east with the barrels at their rest
                      pitch on a hinge node (animation "aim": raised to 45 degrees and back) and markers at the three
                      muzzles
muzzle.txt            the barrel tips on the canvas for every rest and aim frame (120-183)
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground (the walker's ground point; the deployed piece stands where the deploy
  leaves it).
- Camera "camera_mod" in each: orthographic, 32 degrees above the ground, looking north; it frames the 448 canvas
  exactly (checked by drawing each mesh through it over a frame: walker over frame 90, overlap 0.982; deployed over
  frame 144, 0.981).
- Both pass Khronos's glTF validator with no errors or warnings (the infos are the empty marker nodes).
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
v2.1:
- The antenna is the Titan's as it is: its radius, its black and its height above the body (16 px; jugg.ANT_R,
  ANT_L), standing where TS's box stood (P['sensor'] = 0 puts TS's box back).
v2:
- No hoops over the roof (Luke: they are not in his reference art or the voxel, and TS's deployed cabin, DJUGG_A, has
  none).  TS's walker sprite draws only a thin 1 px green arc each side between the hatch and the barrel housings,
  which v1 had built into two hoops; it is left out (jrender.load: P['arch'] = 1 puts the hoops back).
- The legs' height: the Titan's fit and the Juggernaut's put the ground a third of a TS pixel apart (the same legs
  would stand 0.39 px lower by the pixels); they stand on the Juggernaut's ground.  The walk's overlap with TS's is
  the same either way (0.81).
- The deployed waist moves 3.5 px back, 0.9 left and 4.7 down from where the walker carries it, so the thighs' tops
  come to its top corners: the near hip joint stays on its thigh there (TS's moved dome pixels cover that corner), the
  far one goes with the waist (where the walker carries it, it would stand out past the dome, where TS's base has
  nothing).
- The side limbs keep v1's paint (the same yellow-brown) and shape: they are TS's base's own, not the Titan's.
- Not taken from the reference renders: their chrome pistons and flat oval feet (neither TS's legs nor the HD
  Titan's have them).
From v1 (signed off at the shape check):
- The muzzle brakes' two slots (JUGGER CW2).
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
  jugg.py                the walker's body as convex parts;  jfitwalker.py, jfitwalk.py  its fit and v1's walk
                         (fit_walker_e.json, fit_walk_e.json)
  jtlegs.py              the HD Titan's legs, waist, gait and paint (from the Titan's src: legfit.py, gait.py,
                         titanmat.py; its fit and gait in titan_legs.json);  jtwalker.py  the walker on them
  jfitcabin.py, jfithatch.py   the deployed cabin's fit (fit_cabin_a.json, then the hatch: fit_hatch_a.json)
  jtbase.py              the deployed base on the Titan's legs;  jbase2.py  the base fit (fit_base2_a.json: the side
                         limbs and the base's place);  jbarfit.py  the barrels' size, mount and pitches
                         (fit_bar_rest.json, fit_bar_aim.json);  jmap.py  how the mod scales and places TS's sprites
  jtrender.py            a walk frame, and the Titan legs' lighting in every frame;  jrender.py  the camera, the
                         body's materials;  jdeprender.py, jdeployed.py  a deployed frame;  jdeploy.py  a deploy frame
  jfinal.py              all 202 frames;  jcheck.py  the checks above;  jtips.py  muzzle.txt
  jpreviews.py, jshapecheck.py   the previews;  jexport.py  the .glb files;  glbcheck.py  draws a .glb through its
                         camera to check it;  jpackage.py  this README, src/ and the zips
  rc.py, rcrender.py     the ray caster and the buildings' look for models made of convex parts;  rcexport.py,
                         vexport.py  the .glb;  voxrender.py, vxlunit.py, tsnormals.py  the barrel voxel
    PKG=out python3 jfinal.py 0 1       renders frames/ (two workers: 0 2 and 1 2), then: python3 jfinal.py copies
