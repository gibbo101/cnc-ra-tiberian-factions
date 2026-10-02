Amphibious APC (TS [APC]) in HD for Tiberian Factions: TSAPC
============================================================

frames/     tsapc-0000.png ... tsapc-0063.png, the mod's 64 frames on its 384 x 384 canvas, each with a -trim.png
            (white = house colour, antialiased):
              0-31    on land, with its shadow, 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E)
              32-63   on water: the water hull TS swaps in (APCW.VXL), no shadow, 32 facings
previews/   land-8-facings.png, water-8-facings.png   the mod's frames beside HD, every 4th facing
            turn-land.gif, turn-water.gif   all 32 facings in turn, the mod's frames beside HD
            scale.png                next to the HD harvester and EA's APC, as the game draws them
ts-apc-hd-3d/   the 3D model, in its own zip (ts-apc-hd-3d.zip) next to this folder:
            tsapc.glb, tsapc-water.glb   the land hull and the water hull, each in TS's own colours,
                                         with the mod's camera
src/        the model builder, the renderer and the checks (see Rebuilding below)


What it is
----------
One 3D model rebuilt straight from TS's own voxels (APC.VXL (on land) and APCW.VXL (on water), each posed by its own
HVA), drawn the way the HD buildings and units are.
- Shape: every voxel's step is TS's.  Each voxel section's voxels are merged into boxes and cut at 45 degrees along
  the solid's convex edges (so its corners read as pressed plate); where two boxes of a section meet, nothing
  shows.  The shading rounds every edge that faces the air, and carries TS's own voxel normals as a layer of detail
  (the bevels, seams, vents and slots TS shades into its voxels).
- Colours: TS's own.  Every surface takes the palette colour (UNITTEM.PAL) of the voxels just inside it; TS's single
  voxels of darker or lighter speckle are held near the colour round them, while its near-black and near-white
  voxels (slots, hatches, highlights) keep their colour.  House colour is pure green 0,214,0 x (1 + 1.1 grain)
  wherever TS's remap voxels are, with TS's remap shades kept as darker and lighter seams; the -trim masks cover
  exactly that.
The finished frames cover the mod's frames with a silhouette overlap of 0.94 (src/vcheck.py).


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.25 canvas px per voxel.
  The land hull's position (TS's HVA origin) at canvas (191, 190.35), the water hull's at (191.5, 158): where the
  mod's frames have them (found by matching TS's voxels to them: overlap 0.98 on land, 0.91 on water, where the
  mod's water frames have gaps in their hull).
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


3D model (ts-apc-hd-3d/)
------------------------
- Nodes: AmphibiousAPC > unit_facing_east > land_hull; AmphibiousAPC_water > unit_facing_east > water_hull.
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.  The unit faces east (the mod's facing 24).
- The meshes are exact (each voxel section's boxes), subdivided so the vertex colours carry TS's colours.
- Camera "camera_mod": orthographic, the mod's camera, framing the canvas exactly (checked by drawing the mesh
  through it over frame 24: overlap 0.989).
- The file passes Khronos's glTF validator with no errors or warnings.
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
- Built straight from TS's voxels (above), not hand-modelled: nothing is interpreted, every detail is where TS
  has it.
- TS's single-voxel speckle held near the colour round it (its paint is speckled voxel by voxel).
- Most of the APC is house colour in TS; TS's remap shades on it are kept as darker and lighter seams.
- The water hull drawn complete (the mod's current water frames show gaps through it).


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are.
  vxlunit.py, tsnormals.py   a voxel section as boxes, its convex edges, TS's colours and normals across its faces
  voxrender.py           one frame of a voxel unit with the buildings' look
  rc.py, rcrender.py     the ray caster and the buildings' look for models made of convex parts
  vexport.py, rcexport.py   the .glb;  glbcheck.py  draws the .glb through its camera to check it
  vdeliver.py, vcheck.py    renders, previews and checks a unit from its spec
  arender.py             the APC's frame layout and cameras;  apcspec.py  its frames, previews and README
  aexport.py             the .glb;  aplace.py  the placement search against in-mod/
    PKG=out python3 vdeliver.py apcspec render 0 1      renders frames/

