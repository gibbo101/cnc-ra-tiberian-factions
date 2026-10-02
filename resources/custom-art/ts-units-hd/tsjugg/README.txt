Juggernaut (Firestorm [JUGG]) in HD for Tiberian Factions: TSJUGG
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
  each step's pose to that step's 8 facings.  At step 0 its silhouette overlaps TS's by 0.81 on average in TS's
  own camera (0.74 to 0.86 by facing; TS's legs are a few pixels wide, so a pixel counts for a lot);
- the cabin fitted to DJUGG_A's 32 facings (overlap 0.89), the base to DJUGG frame 0 (0.89);
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

Against the mod's current frames the silhouettes overlap by 0.72: walk 0.71, at rest 0.74,
aiming 0.71, the deploy 0.70.  Those frames are TS's sprites scaled up 6.3 times, so this is mostly
the difference above in TS's own camera, scaled up with them.


Keep (from the hand-off README)
-------------------------------
- The 448 canvas, 202 frames in the 120 / 32 / 32 / 18 split.
- One ground line: the lowest body pixel is at canvas y 363 in every deployed and deploy frame (and the walk's
  ground point is the same; the walk's lowest pixel moves with the feet, 311-363 by facing, as the mod's
  310-361).
- Deploy frame 184 = walk frame 45 and 201 = rest frame 132, exactly.
- The barrel tips where the model puts them: ts-jugg-hd-3d/muzzle.txt lists each barrel's tip and their mean on the
  canvas for every rest and aim frame (120-183), for the fire points.
- Shadows: black at alpha 191 (75%), blurred, as the buildings'; within 14 px of the canvas edge they fade out.


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.33 canvas px per TS pixel,
  the size the mod has now.  TS's sprite point (x, y) sits at canvas (6.33 x - 76.72, 6.33 y + 4.33): the mod's frames
  matched to TS's (overlap 0.97), then 5 px up, because the 32-degree camera draws ground in front of the unit about
  3 px lower than TS's 30 degrees and the ground line must stay at y 363.
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
  exactly (checked by drawing each mesh through it over a frame: walker over frame 90, overlap 0.979; deployed over
  frame 144, 0.982).
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
