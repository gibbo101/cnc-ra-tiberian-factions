Apocalypse Tank (TS [APOC, Red Alert 2]) in HD for Tiberian Factions: R2APOC
============================================================================

frames/     r2apoc-0000.png ... r2apoc-0063.png, the mod's 64 frames on its 448 x 448 canvas, each with a -trim.png
            (white = house colour, antialiased):
              0-31    the hull with its shadow, 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E)
              32-63   the turret with its twin cannons and tusk launchers (MTNKTUR and MTNKBARL), no shadow, 32 facings, drawn at the hull's canvas centre
previews/   8-facings.png            hull and turret facing the same way, the mod's frames beside HD
            hull-8-facings.png, turret-8-facings.png   each set on its own, every 4th facing
            turn.gif                 all 32 facings in turn, the mod's frames beside HD
            turret-turning.gif       the turret turning on the hull facing east
            scale.png                next to the HD harvester and EA's Mammoth, as the game draws them
ts-apoc-hd-3d/   the 3D model, in its own zip (ts-apoc-hd-3d.zip) next to this folder:
            r2apoc.glb   the hull and the turret in RA2's own colours, the turret under its own node; the mod's camera
src/        the model builder, the renderer and the checks (see Rebuilding below)


What it is
----------
One 3D model rebuilt straight from TS's own voxels (Red Alert 2's MTNK.VXL, MTNKTUR.VXL, MTNKBARL.VXL, each posed by
its own HVA, with RA2's UNITTEM.PAL), drawn the way the HD buildings and units are.
- Shape: every voxel's step is TS's.  Each voxel section's voxels are merged into boxes and cut at 45 degrees along
  the solid's convex edges (so its corners read as pressed plate); where two boxes of a section meet, nothing
  shows.  The shading rounds every edge that faces the air, and carries TS's own voxel normals as a layer of detail
  (the bevels, seams, vents and slots TS shades into its voxels).
- Colours: TS's own.  Every surface takes the palette colour (UNITTEM.PAL) of the voxels just inside it; TS's single
  voxels of darker or lighter speckle are held near the colour round them, while its near-black and near-white
  voxels (slots, hatches, highlights) keep their colour.  House colour is pure green 0,214,0 x (1 + 1.1 grain)
  wherever TS's remap voxels are, with TS's remap shades kept as darker and lighter seams; the -trim masks cover
  exactly that.
The finished frames cover the mod's frames with a silhouette overlap of 0.93 (src/vcheck.py).


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north.  The hull at 5.03 canvas px per
  voxel with the unit's position at canvas (223.66, 223.09), the turret at 4.92 with its pivot at (223.5, 221.32):
  the sizes and places the mod's frames have (found by matching RA2's voxels to them: overlap 0.98 for the hull,
  0.93 for the turret).  RA2's voxels are drawn at RA2's cell size against TS's (0.8 of the TS units' scale), as
  in-mod/ has them.
- RA2's voxels carry RA2's own normals (244 of them, not TS's 36): estimated from the voxels the same way as TS's
  (src/ra2normals.py, src/estnormals.py) and used for the same layer of detail.
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
The model is RA2's voxels exactly (same sections, same places), so the weapon tips you project from RA2's fire
points still land on the cannon and tusk tips: the turret frames keep the mod's size and place.


3D model (ts-apoc-hd-3d/)
-------------------------
- Nodes: ApocalypseTank > unit_facing_east > hull, turret (at RA2's HVA place and one scale; the mod draws the turret
  frames a little smaller, so the check below draws the hull alone over the hull frame).
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.  The unit faces east (the mod's facing 24).
- The meshes are exact (each voxel section's boxes), subdivided so the vertex colours carry TS's colours.
- Camera "camera_mod": orthographic, the mod's camera, framing the canvas exactly (checked by drawing the mesh
  through it over frame 24: overlap 0.984).
- The file passes Khronos's glTF validator with no errors or warnings.
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
- Built straight from TS's voxels (above), not hand-modelled: nothing is interpreted, every detail is where TS
  has it.
- TS's single-voxel speckle held near the colour round it (its paint is speckled voxel by voxel).
- The turret at its own fitted size (4.92 px per voxel against the hull's 5.03): the mod's turret frames are
  drawn that much smaller, and the turret frames keep their size and place so your weapon tips still line up.


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are.
  vxlunit.py, tsnormals.py   a voxel section as boxes, its convex edges, TS's colours and normals across its faces
  voxrender.py           one frame of a voxel unit with the buildings' look
  rc.py, rcrender.py     the ray caster and the buildings' look for models made of convex parts
  vexport.py, rcexport.py   the .glb;  glbcheck.py  draws the .glb through its camera to check it
  vdeliver.py, vcheck.py    renders, previews and checks a unit from its spec
  apocrender.py          the frame layout and cameras;  apocspec.py  its frames, previews and README
  apocexport.py          the .glb
    PKG=out python3 vdeliver.py apocspec render 0 1      renders frames/

