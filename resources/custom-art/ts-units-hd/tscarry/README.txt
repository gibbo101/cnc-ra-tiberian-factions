Carryall (TS [TRNSPORT]) in HD for Tiberian Factions: TSCARRY
=============================================================

frames/     tscarry-0000.png ... tscarry-0031.png, the mod's 32 frames on its 448 x 448 canvas, each with a -trim.png
            (white = house colour, antialiased), no shadow; 32 facings counter-clockwise from north (0 N, 8 W, 16 S,
            24 E)
previews/   8-facings.png            the mod's frames beside HD, every 4th facing
            turn.gif                 all 32 facings in turn, the mod's frames beside HD
            scale.png                next to the HD harvester and EA's RA Chinook, as the game draws them
ts-carry-hd-3d/   the 3D model, in its own zip (ts-carry-hd-3d.zip) next to this folder:
            tscarry.glb   the model in TS's own colours, with the mod's camera
src/        the model builder, the renderer and the checks (see Rebuilding below)


What it is
----------
One 3D model rebuilt straight from TS's own voxels (TRNSPORT.VXL, posed by its HVA), drawn the way the HD buildings
and units are.
- Shape: every voxel's step is TS's.  Each voxel section's voxels are merged into boxes and cut at 45 degrees along
  the solid's convex edges (so its corners read as pressed plate); where two boxes of a section meet, nothing
  shows.  The shading rounds every edge that faces the air, and carries TS's own voxel normals as a layer of detail
  (the bevels, seams, vents and slots TS shades into its voxels).
- Colours: TS's own.  Every surface takes the palette colour (UNITTEM.PAL) of the voxels just inside it; TS's single
  voxels of darker or lighter speckle are held near the colour round them, while its near-black and near-white
  voxels (slots, hatches, highlights) keep their colour.  House colour is pure green 0,214,0 x (1 + 1.1 grain)
  wherever TS's remap voxels are, with TS's remap shades kept as darker and lighter seams; the -trim masks cover
  exactly that.
The finished frames cover the mod's frames with a silhouette overlap of 0.95 (src/vcheck.py).


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.30 canvas px per voxel, the
  voxel's origin at canvas (223.5, 222.9): the size and place the mod's frames have (found by matching TS's voxels to
  them: overlap 0.92).
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides
  facing the camera as on the other units.  The game draws this canvas at two thirds (8 canvas px per classic
  pixel), so the outline is 1.5 times as wide on the canvas.
- Colours brightened by 1.25 from TS's palette so its ochre comes out as the HD buildings' ochre; whites held at white
  paint.  It flies, so none of the ground's grime or occlusion that the ground units carry low on the hull.


Shadow
------
None baked: in flight the game lifts the frame by the aircraft's height and draws its shadow from the same
frame, darkened, on the ground.  The outline is the units' dark outline, so the silhouette reads as a shadow too.


3D model (ts-carry-hd-3d/)
--------------------------
- Nodes: Carryall > unit_facing_east > hull.  The model's origin is the voxel's origin (TS's HVA origin), as the mod
  centres it.
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.  The unit faces east (the mod's facing 24).
- The meshes are exact (each voxel section's boxes), subdivided so the vertex colours carry TS's colours.
- Camera "camera_mod": orthographic, the mod's camera, framing the canvas exactly (checked by drawing the mesh
  through it over frame 24: overlap 0.985).
- The file passes Khronos's glTF validator with no errors or warnings.
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
- Built straight from TS's voxels (above), not hand-modelled: nothing is interpreted, every detail is where TS
  has it.
- TS's single-voxel speckle held near the colour round it (its paint is speckled voxel by voxel).



Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are.
  vxlunit.py, tsnormals.py   a voxel section as boxes, its convex edges, TS's colours and normals across its faces
  voxrender.py           one frame of a voxel unit with the buildings' look
  rc.py, rcrender.py     the ray caster and the buildings' look for models made of convex parts
  vexport.py, rcexport.py   the .glb;  glbcheck.py  draws the .glb through its camera to check it
  vdeliver.py, vcheck.py    renders, previews and checks a unit from its spec
  carryrender.py          the frame layout and camera;  carryspec.py  its frames, previews and README
  carryexport.py          the .glb
    PKG=out python3 vdeliver.py carryspec render 0 1      renders frames/

