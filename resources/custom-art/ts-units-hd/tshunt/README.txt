Hunter-Seeker (TS [GHUNTER]) in HD for Tiberian Factions: TSHUNT
================================================================

frames/     tshunt-0000.png ... tshunt-0007.png, the mod's 8 frames on its 384 x 384 canvas, each with a -trim.png (all
            black: it never takes house colour), one facing, 3 ticks a frame, no shadow (the game draws it from the
            frame)
previews/   spin.gif                 the 8 frames, the mod's beside HD
            droid.png                TS's sprite (x 4, as the mod has it), the mod's frame and HD
            scale.png                next to the HD harvester and EA's TD Orca, as the game draws them
            shape.png                TS's sprite as colour classes beside the model's, in TS's own camera
ts-hunt-hd-3d/   the 3D model, in its own zip (ts-hunt-hd-3d.zip) next to this folder:
            tshunt.glb   the droid in vertex colours, a marker at the star's light, the mod's camera
src/        the model, its fit, the renderer and the checks (see Rebuilding below)


What it is
----------
One 3D model built from TS's own sprite (GGHUNT: TS draws the droid from one side only; its 8 frames differ just in
the star's light and the fins' flash), every part read off TS's pixels (frame 4) and then fitted to them in TS's own
camera (30 degrees; silhouette and colour classes, overlap 0.98), drawn the way the HD buildings and units are.
Top to bottom, with the pixels each part comes from (columns and rows of TS's 73 x 73 frame):
- the mast: 1 px, blue-grey (rows 8-9), with a bronze band (row 7) and a grey tip (row 6)
- the star (rows 10-12): a blue core 3 px across with a spike either side (columns 34 and 38); its light on the centre
  pixel (36, 11), and the dark grey stub just under the light (36, 12)
- the neck (columns 35-37): bronze, with a dark collar under its top (row 16)
- the strut (row 19): a steel bar from column 32 to 40, behind the neck, between the wings' inner edges
- the wings (rows 16-20, columns 27-32 and 40-45): thin steel blades, wider at the bottom and leaning in at the top,
  each with a dark slot one pixel in from its outer edge ((30, 17)-(29, 18) and (42, 17)-(43, 18)); a red-brown mark on
  the left one's inner top corner (32, 16)
- the shoulder (rows 21-24): 13 px across but only 3-4 rows tall, so a bar across the body, not a disc (a disc that
  wide would stand 7 rows tall in TS's camera, and its back half would show over the bar); its ends rise into two
  rounded lobes (their tops on row 21 at columns 31 and 41, the row empty between them and the middle)
- the chest: TS's highlight (white at (35, 23)-(36, 23), yellow at (35, 22), pink round them) sits on the shoulder's
  middle where the surface faces the camera, so the body's top there is a round mass standing out in front of the bar
- the body: 7 px across (columns 33-39) from row 25 down, a lug either side at rows 27-28 (columns 32 and 40), the blue
  strip down its front (column 36, rows 27-29), its bottom on row 34
- three steel fins round the bottom, alike: one towards the camera (columns 35-37, rows 32-35: 1 px at its top and 3
  below, so a ridged wedge) and two to the sides (columns 31-33 and 39-41, rows 31-34), with red-brown marks at their
  roots ((33, 31), its twin (39, 31) in shadow)
The frames differ as TS's do: the star's light pulses blue to white (frame 3) and back, in TS's colours; at frame 0 the
fins' upper faces flash white (their undersides stay as they are, as in TS's frame 0) and they stay a little brighter
through frames 1-3, as TS's shades there are.
The finished frames cover the mod's with a silhouette overlap of 0.87.


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 4 canvas px per TS pixel, the
  size the mod has now (its frames are TS's sprite x 4 exactly), placed by matching the HD droid to frame 4.  The
  README said to keep this size unless you say to grow it: one number (PPU in hsrender.py) and the place follows.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides facing
  the camera as on the other units.
- The bronze shines as TS's does: TS's sprite has a white highlight on the shoulder's front, so the bronze takes a
  highlight from the light TS lit its sprites with (front left of the camera, hd.py's L_CAM_TS); it lands on the chest,
  as TS's does.
- Colours: TS's bronze on the body (its be913c lit, a58538 mid); the mod's steel on TS's remap parts (wings, strut,
  fins: as light on average as the mod's frames have them, 148, 153, 166 on the wings); TS's blues on the star and the
  strip and its blue-grey on the mast and collar (each as dark on average as TS's pixels for it); TS's red-brown marks.
  No house colour (the -trim masks are black).


3D model (ts-hunt-hd-3d/)
------------------------
tshunt.glb   the droid in its own colours, with the mod's camera
- Nodes: HunterSeeker > body, chest, shoulder and lobes, lugs, neck and collar, mast, band and tip, the star with its
  spikes and stub, strut, wings and their slots, fins, strip, marks, and star_light (a marker at the star's light).
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (30.3 TS px, as the other TS units' models; 121 px
  on this canvas, which draws the droid at 4 px a TS px).  Origin: the body's bottom on its axis.
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 384 canvas exactly
  (checked by drawing the mesh through it over frame 4: overlap 0.923).
- The file passes Khronos's glTF validator with no errors or warnings (errors 0 warnings 0 infos 1 hints 0; the info is the empty marker node).
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (none).


Judgement calls (each one easy to change)
-----------------------------------------
- This is the second version.  The first read the droid as round all the way (a disc for a shoulder, a drum for a
  belt): from 32 degrees those showed as a saucer and a second rim TS doesn't have.  Now every part is read off TS's
  pixels first (the list above) and the fit only moves them a pixel or so.  A fit with the camera height left free came
  back to 28-29 degrees, so TS did draw it from its usual 30.
- TS's single view can't show depth.  The shoulder bar and its lobes are as deep as they are tall.  The wings are thin
  blades lying back (85 degrees from upright): from TS's camera any lean looks the same, and lying back they catch the
  light the way TS's do (its brightest remap shade).  The side fins sit 101 degrees round from the front one, as the
  fit put them.
- The red-brown marks are where TS has them: the left wing only (the right wing's corner is plain remap), and both fin
  roots.
- Kept at the mod's current size (4 canvas px a TS pixel, smaller than the other TS units' 6.4), as the README said.


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy, Pillow and cma.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are (TS_HANDOFF).
  hseek.py               the droid as convex parts, with the pixels each part is read from;  fit_h.json  its fit
  hsfit.py               the fit to TS's sprite;  hsmap.py  how the mod scales and places TS's sprite (x 4 at 46, 108)
  hsrender.py            one frame;  hsplace.py  places it as the mod has it -> place.json
  rc.py, rcrender.py     the ray caster and the buildings' look for models made of convex parts
  rcexport.py, vexport.py   the .glb;  glbcheck.py  draws the .glb through its camera to check it
  hsfinish.py            renders, checks, previews and packages it all
    python3 hsrender.py frames 0,3 4 out      renders frames
