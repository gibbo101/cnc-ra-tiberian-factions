Titan (TS [MMCH]) in HD for Tiberian Factions: TSTITN
======================================================

frames/     tstitn-0000.png ... tstitn-0127.png, the mod's 128 frames on its 448 x 448 canvas, each with a
            -trim.png (white = house colour, antialiased).
              0-95    the legs: frame = facing x 12 + step, facings counter-clockwise from north
                      (0 N, 1 NW, 2 W, 3 SW, 4 S, 5 SE, 6 E, 7 NE); standing shows step 0.
              96-127  the upper body with the cannon, 32 facings counter-clockwise from north (96 N, 104 W,
                      112 S, 120 E).
            Legs and upper body laid over each other at the same canvas position give the assembled Titan.
bay/        tstitn-bay-0000.png, the upper body facing south (frame 112) without the antenna: drawn while the
            Titan waits deep in a TS war factory's bay, where the antenna would show over the roof
previews/   standing-8-facings.png   TS's sprite, the mod's current frames and HD, the 8 facings
            walk-east.gif, walk-south.gif   the walk, the mod's current frames beside HD (3 ticks a step)
            turn.gif                 the upper body turning through its 32 facings over the standing legs
            scale.png                next to EA's HD Mammoth and the HD harvester, as the game draws them
            shape-legs.png, shape-upper-body.png   TS's sprite beside the model drawn in TS's own camera,
                                     with the silhouette overlap per facing
            head-waist-closeup.png   the head's boss and the waist, after review
3d/         tstitn.glb   the model in vertex colours, the walk as an animation, the RA-grid camera
            muzzle.txt   the cannon's muzzle on the canvas for each upper-body frame (96-127)
src/        the model, the renderer and the fitting scripts (see Rebuilding below)


What it is
----------
One 3D model fitted to TS's own art, rendered the way the HD buildings and the harvester are:
- the upper body fitted to TS's 32 upper-body frames (MMCH 120-151): its silhouette overlaps TS's by 0.89
  on average (0.86 to 0.92);
- the legs fitted to all 120 of TS's walk frames (8 facings x 15 steps) as one smooth walk: overlap 0.83 on
  average. TS's legs are only a few pixels wide; TS's own frames shifted by one pixel score 0.83 against
  themselves, so the difference left is about one TS pixel;
- the cannon built voxel by voxel from MMCHBARL.VXL and mounted where TS's own drawing code puts it: two
  voxel units behind the turning point (TurretOffset -16), at the voxel origin (the sprite's centre), with
  the HVA's offset.
Legs: reverse knees with a spur behind each, the shins and long split-toed feet carrying the stride (as in
Luke's in-game video). Upper body: the shell rising to the rear, the rounded boss on its front top, the green
band with its pods and the front pods' lamps, the box with its vent at the rear left, the antenna, the
cannon on the right flank.


Look
----
- Camera: a true orthographic view 32 degrees above the ground, looking north; 6.4 canvas px per TS pixel
  (the size the mod has now). The ground under the unit sits where TS's sprite has it (canvas 224, 364).
  The feet come within about one TS pixel of TS's own (in most facings up to 6 canvas px lower, where a
  foot reaches towards the camera), and the upper body's outline within a few px of the current frames.
- Turning point: legs and upper body both turn about the canvas centre (TS's upper-body sprite turned about
  a point about half a TS pixel off its legs' axis).
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the
  sides facing the camera as on the harvester.
- The game draws this canvas at two thirds (8 canvas px per classic pixel against EA's 5.33), so the
  outline, the shadow's blur, the contact shadow and the surface grain are 1.5 times as wide on the canvas:
  in the game they match the buildings.
- Colours: the Titan's own yellow-brown paint on the shell, thighs, shins, feet and waist (TS's ochre ramp;
  not house colour); steel joints, knee spurs, bracket and tube; a black antenna. House colour is pure green
  0,214,0 x (1 + 1.1 grain) on the band, the pods, the box and the cannon's breech, housing and taper, with
  detail only as thin seams and ribs; the -trim masks cover exactly those parts.
- The waist sits under the upper body and takes its shadow, so it reads dark as TS's does. The legs below
  are lit on their own, as TS's leg sprite is.


Shadow
------
- The leg frames carry the whole Titan's shadow (legs, and the upper body facing the same way as the legs),
  black at alpha 191 (75%), blurred. It falls the way the buildings' and the harvester's do (to the right
  and a little towards the camera), 62% as long, so the Titan's shadow stays on the 448 canvas. Within
  14 px of the canvas edge it fades out.
- The upper-body frames carry no shadow. As in TS, the shadow does not follow the upper body when it turns
  away from the legs.


Walk
----
- The 12 steps are spaced evenly through TS's stride (TS's 15 frames). The mod's current frames use TS's
  frames 0 1 2 4 5 6 8 9 10 11 13 14, which skip a frame in three places; the evenly spaced steps keep the
  stride smooth at 3 ticks a step. The order is the same: step 0 is TS's frame 0 (standing).
- The two legs swing half a stride apart (TS's walk is symmetric), one foot always on the ground; the
  hips bob twice a stride.


Cannon and fire points
----------------------
3d/muzzle.txt lists the tube's tip on the canvas for each upper-body frame: where TS's model puts it
(MMCHBARL.VXL's last voxel), on the tube's centre line. Against the current composite frames the tip has
moved by 4 to 31 px (15 on average; the most facing west). The current composite does not follow one 3D
mounting from facing to facing; this follows TS's drawing code at every facing. Regenerate the fire
points from muzzle.txt or from the art.


War Factory seat
----------------
The registration is the current frames' (the hip at the canvas centre, the ground under the unit where
TS's sprite has it), so the seat dialled for the door should still apply; the outline differs from the
current frames by a few px at most.


3D model (3d/tstitn.glb)
------------------------
- Axes: glTF's own (y up): x east, y up, z south. 1.0 = one cell (192 px on this canvas, 128 px in the
  game). Origin: the unit's position on the ground.
- Nodes: Titan > legs (facing east) > the hip parts and each leg part; Titan > upper_body (facing east, mod
  frame 120) > shell, band, boss, pods, box, antenna, mount, and cannon > its parts and the muzzle marker.
- Animation "walk": the 12 walk steps, 0.2 s each (3 ticks at 15 a second), looping.
- Camera "camera_ra_grid": orthographic, 32 degrees above the ground, looking north; it frames the 448
  canvas exactly (checked by drawing the mesh through it over the frames: overlap 0.97). The file passes
  Khronos's glTF validator with no errors or warnings.
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
- The 12 walk steps evenly spaced (above).
- The shadow 62% as long as the buildings' (above).
- One turning point for legs and upper body (above).
- The waist built as a pelvis, a ring and a dome under the upper body, in its shadow (after review: TS's
  dark mass there is the body's shadow).
- The head's boss an upright rounded dome with a rim (after review).


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy, Pillow and cma. The renderer files from the buildings (hd.py, walls2.py,
wnoise.py, pfinal.py, export3d.py) are included.
  rc.py, rcrender.py      a ray caster for models made of convex parts, with the buildings' look
  rcexport.py             convex parts to meshes (exact), for the .glb
  legfit.py, gait.py      the legs and their walk;  torso2.py  the upper body;  barrel.py  the cannon
  titan.py                the assembled Titan, the mod's frame layout
  titanmat.py             materials;  titanrender.py  one frame;  finalrender.py  all 128 frames
  bayrender.py            bay/, the upper body facing south without the antenna
  titanexport.py          the .glb;  glbcheck.py  draws the .glb through its camera to check it
  makepreviews.py         the previews;  paths.py  where the hand-off folders are (TITAN_HANDOFF)
  legs_final.json, torso_final.json, shell_planes28.npy   the fitted model
  fitlegs2.py, fitlegs4.py, fitgait.py, torso2fit.py, carve.py ...   the fitting, from TS's frames
    python3 finalrender.py 0 1          renders frames/ (PKG= sets the output folder)
    python3 titanexport.py out.glb
