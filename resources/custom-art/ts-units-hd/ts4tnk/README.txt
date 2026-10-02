Mammoth Mk. I (TS [4TNK]) in HD for Tiberian Factions: TS4TNK
=============================================================

frames/     ts4tnk-0000.png ... ts4tnk-0063.png, the mod's 64 frames on its 512 x 512 canvas, each with a -trim.png
            (white = house colour, antialiased):
              0-31    the hull with its shadow, 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E)
              32-63   the turret with its barrels and tusk pods, no shadow, 32 facings, drawn at the hull's canvas
                      centre
previews/   8-facings.png            the assembled tank (hull + turret facing the same way), the mod's frames beside HD
            hull-8-facings.png, turret-8-facings.png   each set on its own, every 4th facing
            turn.gif                 the assembled tank through all 32 facings, the mod's frames beside HD
            turret-turning.gif       the turret turning on the hull facing east
            scale.png                next to the HD harvester and EA's Mammoth, as the game draws them
ts-4tnk-hd-3d/   the 3D model, in its own zip (ts-4tnk-hd-3d.zip) next to this folder:
            ts4tnk.glb   the model in TS's own colours: the hull, and the turret with its barrels and tusk pods
                         under a 'turret' node that turns about the unit's position; the mod's camera
src/        the model builder, the renderer and the checks (see Rebuilding below)


What it is
----------
One 3D model rebuilt straight from TS's own voxels (4TNK.VXL, 4TNKTUR.VXL and 4TNKBARL.VXL, each posed by its own
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
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.23 canvas px per voxel, the
  unit's position (TS's HVA origin) at canvas (255.5, 254.7) for the hull and the turret alike: the size and place the
  mod's frames have (found by matching TS's voxels to them: overlap 0.99 for the hull).  TS's hull sits 1.24 voxels
  above its HVA origin (its tracks' lowest voxels), so the model is lowered onto the ground and the camera raised to
  match: every pixel stays where in-mod/ has it, and the shadow meets the tracks.
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


Fire points
-----------
The model is TS's voxels exactly (same sections, same places), so TS's PrimaryFireFLH=40,32,96,
SecondaryFireFLH=-32,80,120 and PBarrelLength=192 still point at the cannons' and the tusk pods' tips.


3D model (ts-4tnk-hd-3d/)
-------------------------
- Nodes: MammothMk1 > unit_facing_east > hull (its section), turret (the turret's section and the barrels').
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.  The unit faces east (the mod's facing 24).
- The meshes are exact (each voxel section's boxes), subdivided so the vertex colours carry TS's colours.
- Camera "camera_mod": orthographic, the mod's camera, framing the canvas exactly (checked by drawing the mesh
  through it over frames 24 and 56 laid over each other: overlap 0.983).
- The file passes Khronos's glTF validator with no errors or warnings.
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
- Built straight from TS's voxels (above), not hand-modelled: nothing is interpreted, every detail is where TS
  has it.
- TS's single-voxel speckle held near the colour round it (its paint is speckled voxel by voxel).
- Most of the Mk. I is house colour in TS (it was never finished as a GDI tank); TS's remap shades on it are kept
  as darker and lighter seams, so its panels, vents and edges read as in TS.


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are.
  vxlunit.py, tsnormals.py   a voxel section as boxes, its convex edges, TS's colours and normals across its faces
  voxrender.py           one frame of a voxel unit with the buildings' look
  rc.py, rcrender.py     the ray caster and the buildings' look for models made of convex parts
  vexport.py, rcexport.py   the .glb;  glbcheck.py  draws the .glb through its camera to check it
  vdeliver.py, vcheck.py    renders, previews and checks a unit from its spec
  t4render.py            the Mk. I's frame layout and camera;  t4spec.py  its frames, previews and README
  t4export.py            the .glb;  t4place.py  the placement search against in-mod/
    PKG=out python3 vdeliver.py t4spec render 0 1      renders frames/

