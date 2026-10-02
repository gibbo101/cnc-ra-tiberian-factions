Limpet Drone (Firestorm [LIMPET]) in HD for Tiberian Factions: TSLIMP
=====================================================================

frames/     tslimp-0000.png ... tslimp-0019.png, the mod's 20 frames on its 192 x 192 canvas, each with a -trim.png
            (white = house colour, antialiased):
              0-9     the drone, its light blinking as TS's LIMPED 0-9 (2 ticks a frame)
              10-19   its shadow, the same in every frame (TS's 10-19 are one shadow), drawn under drone 10+n as now
previews/   blink.gif                the drone over its shadow through the blink, the mod's frames beside HD
            drone.png                TS's sprite (scaled as the mod scales it), the mod's frame and HD
            scale.png                next to the HD harvester and EA's rifleman, as the game draws them
            shape.png                TS's sprite as colour classes beside the model's, in TS's own camera
ts-limp-hd-3d/   the 3D model, in its own zip (ts-limp-hd-3d.zip) next to this folder:
            tslimp.glb   the drone in vertex colours, the light's two halves as markers, the mod's camera
src/        the model, its fit, the renderer and the checks (see Rebuilding below)


What it is
----------
One 3D model fitted to Firestorm's own sprite (LIMPED: one shape, no facings), drawn the way the HD buildings and units
are.  TS draws the drone as a solid of revolution, so the model is one: a rounded dark nub standing in a thin grey ring
on top, the house-colour dome (an egg, widest across its middle), the grey band round its waist with its two dark
lenses towards the camera and a white lamp on each lens' left, and the house-colour cone tapering to its tip.  The
light sits on the dome's front two rows over the band, as in TS.
- Sizes: the band, the dome and the cone fitted to the sprite (silhouette and colour classes in TS's own camera,
  30 degrees: overlap 0.93); the nub, the ring, the lenses and the lamps read straight off TS's pixels.
- The blink: TS lights the two halves of its light in turn through white, yellow, orange, red and dark red, a half at
  a time going dark; each frame takes TS's colour for each half (frame 0: off and red ... frame 9: dark red and
  orange), unshaded, as small as TS's pixels.  TS's glint on the dome above the light in frames 3 and 4 (white, then
  pale blue) is there too, as small.
The drone frames cover the mod's with a silhouette overlap of 0.88.


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.2 canvas px per TS pixel,
  the size and place the mod's drone frames have (found by matching TS's sprite to them, overlap 0.97, and then the
  HD drone to frame 0).  The drone hovers with its tip 5.8 TS px over the ground, as TS's frames have it
  over its shadow.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides facing
  the camera as on the other units.  The game draws this canvas at two thirds (8 canvas px per classic pixel), so the
  outline and the shadow's blur are 1.5 times as wide on the canvas.
- House colour is pure green 0,214,0 x (1 + 1.1 grain) on the dome and the cone (TS's remap pixels), the light left
  out; the -trim masks cover exactly that.  The grey band and ring, the dark nub and lenses: TS's own greys.


Shadow (frames 10-19)
---------------------
The drone's footprint straight under it, as TS draws a hovering unit's shadow: a disc as wide as the drone's widest
part, black at alpha 191 (the buildings' 75%), blurred as theirs, where the mod's shadow frames have theirs (the
same ground line, about 93 px under the canvas centre).  The README asked for at least alpha 135: today's peak at 112
is now 191.


3D model (ts-limp-hd-3d/)
------------------------
tslimp.glb   the drone in its own colours, with the mod's camera
- Nodes: LimpetDrone > drone (lifted 5.8 TS px off the ground) > nub, cap, dome, band, cone, the lenses and
  lamps, and light_left / light_right (markers at the light's two halves).
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground, under the drone's axis.
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 192 canvas exactly
  (checked by drawing the mesh through it over frame 0: overlap 0.976).
- The file passes Khronos's glTF validator with no errors or warnings (errors 0 warnings 0 infos 2 hints 0; the infos are the two empty marker
  nodes).
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
- The shadow as the drone's footprint straight under it (TS's shape), not cast sideways by the buildings' light:
  a hovering unit's shadow in TS sits under it, and the game draws it under the drone as it bobs.
- The shadow at the buildings' alpha 191, over the README's minimum of 135.
- The dome an egg on the band (TS's dome is widest across its middle and narrows into the band).


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy, Pillow and cma.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are (TS_HANDOFF).
  limp.py                the drone as convex parts;  fit_c.json  its fitted sizes
  lfit.py                the fit to TS's sprite;  lmap.py  how the mod scales and places TS's sprite
  lrender.py             one frame (the drone with its light, or its shadow);  lplace.py  places them as the mod has
                         them -> place.json
  rc.py, rcrender.py     the ray caster and the buildings' look for models made of convex parts
  rcexport.py, vexport.py   the .glb;  glbcheck.py  draws the .glb through its camera to check it
  lfinish.py             renders, checks, previews and packages it all
    python3 lrender.py frames 0,10 4 out      renders frames
