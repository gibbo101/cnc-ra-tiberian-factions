Devil's Tongue (TS [SUBTANK]) in HD for Tiberian Factions: TSSUBTANK
====================================================================

frames/     tssubtank-0000.png ... tssubtank-0112.png, the mod's 113 frames on its 384 x 384 canvas, each
            with a -trim.png (white = house colour, antialiased):
              0-31     driving, with its shadow, 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E)
              32-71    diving: 8 facings x 5 steps (frame = 32 + facing x 5 + step; facing 0 N, 1 NW ... 7 NE, each
                       facing the driving frame facing x 4), nose pitched down 8, 16, 24, 32, 40 degrees; no shadow
              72-111   emerging: the same, nose pitched up 40, 32, 24, 16, 8 degrees; no shadow
              112      the disturbed-earth marker, the mod's own (already smooth), as it is
previews/   8-driving-facings.png    the mod's frames beside HD, every 4th facing
            dive-east.png            the dive and the emerge facing east, step by step
            dive-east.gif, dive-southwest.gif, emerge-south.gif   a dive and an emerge, the mod's frames beside HD
            turn.gif                 the 32 driving facings in turn
            scale.png                next to the HD harvester, as the game draws them
ts-subtank-hd-3d/   the 3D model, in its own zip (ts-subtank-hd-3d.zip) next to this folder:
            tssubtank.glb   the model in TS's own colours, with the mod's camera
src/        the model builder, the renderer and the checks (see Rebuilding below)


What it is
----------
One 3D model rebuilt straight from TS's own voxels (SUBTANK.VXL, posed by its HVA), drawn the way the HD buildings
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
The finished frames cover the mod's frames with a silhouette overlap of 0.96 (src/vcheck.py).


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.256 canvas px per voxel, the
  unit's position (TS's HVA origin) at canvas (192.0, 190.8): the size, place and ground line the mod's frames have
  (found by matching TS's voxels to them).  The dive and emerge frames pitch the model about the unit's position on
  the ground, as the mod's frames do (the same match on the dive frames: overlap 0.97).
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides
  facing the camera as on the other units.  The game draws this canvas at two thirds (8 canvas px per classic
  pixel), so the outline, the shadow's blur and the contact shadow are 1.5 times as wide on the canvas.
- Colours brightened by 1.25 from TS's palette so its ochre comes out as the HD buildings' ochre; whites held at white
  paint; grime rising from the ground on the lower hull.


Shadow
------
Every frame that carries a shadow has the unit's shadow, black at alpha 191 (75%), blurred, falling to the
right and a little towards the camera, as long as the buildings' and the harvester's.  Within 14 px of the canvas
edge it fades out.


Fire point
----------
The model is TS's voxels exactly, so PrimaryFireFLH=128,0,40 still points at the flame nozzles.


3D model (ts-subtank-hd-3d/)
----------------------------
- Nodes: DevilsTongue > unit_facing_east > hull.  (The dive and emerge are the same model pitched about its position.)
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.  The unit faces east (the mod's facing 24).
- The meshes are exact (each voxel section's boxes), subdivided so the vertex colours carry TS's colours.
- Camera "camera_mod": orthographic, the mod's camera, framing the canvas exactly (checked by drawing the mesh
  through it over frame 24: overlap 0.988).
- The file passes Khronos's glTF validator with no errors or warnings.
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
- Built straight from TS's voxels (above), not hand-modelled: nothing is interpreted, every detail is where TS
  has it.
- TS's single-voxel speckle held near the colour round it (its paint is speckled voxel by voxel).
- The marker (frame 112) kept as the mod draws it: it is already a smooth drawing, not TS art.


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are.
  vxlunit.py, tsnormals.py   a voxel section as boxes, its convex edges, TS's colours and normals across its faces
  voxrender.py           one frame of a voxel unit with the buildings' look
  rc.py, rcrender.py     the ray caster and the buildings' look for models made of convex parts
  vexport.py, rcexport.py   the .glb;  glbcheck.py  draws the .glb through its camera to check it
  vdeliver.py, vcheck.py    renders, previews and checks a unit from its spec
  subrender.py          the frame layout (driving, dive, emerge, marker) and camera;  subspec.py  previews, README
    PKG=out python3 vdeliver.py subspec render 0 1      renders frames/

