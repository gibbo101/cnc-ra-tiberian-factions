Wolverine (TS [SMECH]) in HD for Tiberian Factions: TSSMEC
=========================================================

frames/     tssmec-0000.png ... tssmec-0127.png, the mod's 128 frames on its 384 x 384 canvas, each with a
            -trim.png (white = house colour, antialiased).
              0-95    the walk: frame = facing x 12 + step, facings counter-clockwise from north
                      (0 N, 1 NW, 2 W, 3 SW, 4 S, 5 SE, 6 E, 7 NE); standing shows step 0.  2 ticks a step.
              96-127  firing: frame = 96 + facing x 4 + step, standing as TS stands to fire; the muzzle flash on
                      steps 0 and 2 (both guns at once, as TS), none on 1 and 3.
previews/   standing-8-facings.png   TS's sprite, the mod's current frames and HD, walk step 0 in all 8 facings
            walk-east-south.gif, walk-southeast-northwest.gif   the walk, the mod's current frames beside HD
            fire-south-east.gif, fire-southwest-northeast.gif   firing, the mod's current frames beside HD
            scale.png                next to the HD harvester and the HD Titan, as the game draws them
            shape-walk-step0.png, shape-standing-to-fire.png   TS's sprite beside the model drawn flat in TS's
                                     own camera, with the silhouette overlap per facing
3d/         tssmec.glb   the model in vertex colours, the walk and the firing stance as animations, the muzzles
                         as marker nodes, the RA-grid camera
            muzzle.txt   both muzzles on the canvas for each firing frame (96-127)
src/        the model, the renderer and the fitting scripts (see Rebuilding below)


What it is
----------
One 3D model fitted to TS's own art (SMECH, all 136 frames), with the detail of Westwood's own render of the
same model (the picture Luke sent: TS's sprite was rendered from it), drawn the way the HD buildings, the
harvester and the Titan are:
- the body and the firing stance fitted to TS's 8 standing frames (96-103): silhouette overlap 0.85 on average;
- the walk fitted to all 96 of TS's walk frames (8 facings x 12 steps), the two legs half a stride apart as TS
  has them, then smoothed into one walk: overlap 0.88 on average.  TS's Wolverine is about 19 x 30 TS pixels,
  so a pixel's difference round the outline costs about 0.07;
- the muzzles where TS's flashes are.
Body (from TS's frames, detail from Westwood's render): a squat armoured cab, its roof sloping down to the front
(TS's bright face) with two grab handles at the back; the pilot's black window slit across the front under the
roof's edge; the front plate below it with yellow-and-black hazard stripes along its top and bottom; a vent grille
low on each side; the house-colour back panel and shoulder pads; the small orange lamp at the cab's front right
corner and the black antenna at its right rear; the arms hanging clear of the chest, each carrying a gatling: a
dark housing, a drum, six steel barrels with a clamp ring, and a brass ammo belt looping under it.
Legs: armour plates over the thighs, grey knee and ankle joints, scuffed and dirty shins, clawed three-toed feet.
The knees bend forward (TS's frames fit that way round better than reverse knees: 0.19 against 0.22 on the
swing).  The body bobs twice a stride.


Look
----
- Camera: a true orthographic view 32 degrees above the ground, looking north; 6.4 canvas px per TS pixel (the
  size the mod has now, 8 canvas px per classic pixel).  The ground sits where TS's sprite has it (TS's point
  (47.5, 53) at canvas (192, 307), as in-mod/): the ground under the unit at canvas y 278.  (The ground line was
  fitted again once the feet stood on it: half a TS pixel higher than the first fit, so the HD feet sit where
  TS's do; the HD unit's top stands about half a TS pixel lower than TS's, as the 32-degree camera shows heights
  a little shorter than TS's 30.)
- Turning point: the canvas centre, the unit's position.  TS's sprite turns about a point 0.8 TS px right of its
  frame's centre, so the mod's current frames stand about 5 canvas px right of the HD ones.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides
  facing the camera as on the harvester and the Titan; the plates' edges are softened in the shading (as the
  Titan's shell) so they read as pressed metal.  The game draws this canvas at two thirds, so the outline, the
  shadow's blur and the contact shadow are 1.5 times as wide on the canvas (as the Titan's).
- Colours: the Titan's yellow-brown paint (TS's ochre ramp) on the cab, arms, thighs, shins and feet, a shade
  darker on the chest under the cab (TS draws it darker in every facing); dark olive pelvis; gunmetal guns with
  steel barrels; steel joints; a black antenna; the orange lamp; near-black glass in the window.  House colour is
  pure green 0,214,0 x (1 + 1.1 grain) on the back panel and the shoulder pads, with detail only as thin ribs and
  grooves; the -trim masks cover exactly those parts (the hazard stripes are not house colour).


Shadow
------
Every frame carries the unit's shadow, black at alpha 191 (75%), blurred, falling to the right and a little
towards the camera, 62% as long as the buildings' (the Titan's length, so the TS units' shadows match).  Within
14 px of the canvas edge it fades out.


Walk
----
TS's own 12 walk frames are the mod's 12 steps (2 ticks a step), and the HD walk follows them step for step: the
legs half a stride apart, each step lifted so its lower foot stands on the ground, the body bobbing about one TS
pixel twice a stride.


Firing and fire points
----------------------
The four firing steps stand in TS's firing stance (one foot a little forward, both on the ground).  On steps 0 and
2 both guns flash: TS's star bursts (a white core, yellow, orange rays with red tips), the long rays across the
screen as TS draws them, the second burst throwing one long streak; the burst is hidden where the unit is in front
of the muzzle, and its light falls on the gun and arm beside it.  3d/muzzle.txt lists both muzzles per firing
frame: regenerate the fire points from it.


War Factory seat
----------------
The registration is the mod's (the canvas centre on the unit's position, the ground line where TS has it), so the
seat dialled for the Titan applies.


3D model (3d/tssmec.glb)
------------------------
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.
- Nodes: Wolverine > unit_facing_east > body (cab, chest, waist, window, back panel, shoulder pads, arms, guns
  with their drums, barrels, clamp rings and ammo belts, antenna, lamp, handles, pelvis, hip joints; the
  muzzle_left and muzzle_right markers) and legs (each leg's thigh, knee, shin, ankle, foot and toes).
- Animations: "walk", the 12 walk steps, 0.133 s each (2 ticks at 15 a second), looping; "stance", the firing
  stance.
- Camera "camera_ra_grid": orthographic, 32 degrees above the ground, looking north; it frames the 384 canvas
  exactly (checked by drawing the mesh through it over frame 72: overlap 0.98).  The file passes Khronos's glTF
  validator with no errors or warnings.
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
- Westwood's render's detail added where TS's sprite is too small to show it (Luke asked for it): the hazard
  stripes, the gatlings' six barrels, the ammo belts (kept short so the outline stays TS's), the clawed feet, the
  roof's grab handles, the side vents.  The "7" on the render's front plate is left off: every Wolverine would carry
  the same number.
- The window slit where TS draws its black line: right under the roof's front edge (the render has it in the
  roof's front face).
- The turning point at the canvas centre (above).
- The shadow 62% as long as the buildings' (the Titan's).
- The chest under the cab a shade darker than the cab (TS shows it dark in every facing).
- The knees bending forward (above).
- The flash's long rays across the screen, as TS draws them, rather than along the barrels.


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy, Pillow and cma.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) are included.
  rc.py, rcrender.py      a ray caster for models made of convex parts, with the buildings' look (the Titan's)
  rcexport.py             convex parts to meshes (exact), for the .glb
  wolf.py                 the fitted model's parts;  wolfhd.py  Westwood's detail and the mod's frame layout
  wolfmat.py              materials;  wflash.py  the muzzle flash;  wolfrender.py  one frame;  wfinal.py  all 128
  wexport.py              the .glb;  glbcheck.py  draws the .glb through its camera to check it;  wmuzzle.py  the
                          muzzle table
  wpreviews.py, wshape.py the previews and the shape check
  wolf_final.json         the fitted model (shape, firing stance, the 12 walk poses, the smooth gait)
  wfit.py, wfitstand.py, wfitwalk.py, wfitsym.py, wfitlegs.py, wfitgait.py, wfitstance.py, gait.py, wclass.py,
  wpal.py                 the fitting, from TS's frames (paths.py: where the hand-off folders are)
  wcheck.py               checks the finished frames (sizes, trims, house green, shadow, flash, feet)
    MODEL=wolf_final.json PKG=out python3 wfinal.py 0 1      renders frames/
    python3 wexport.py wolf_final.json tssmec.glb
