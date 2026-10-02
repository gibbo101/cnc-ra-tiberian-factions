Hover MLRS (TS [HVR]) in HD for Tiberian Factions: TSHVR
========================================================

frames/     tshvr-0000.png ... tshvr-0095.png, the mod's 96 frames on its 192 x 192 canvas (4 canvas px per classic
            pixel, as the mod has it), each with a -trim.png (white = house colour, antialiased):
              0-31    the hull, no shadow, 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E)
              32-63   the missile rack, no shadow, 32 facings: each frame's content centred where the mod's current
                      rack frame has it, so the seat tables you dialled still hold
              64-95   the hull's shadow on its own, drawn first under the hull: the HD hull's silhouette, offset as
                      now (5 px right, 17 px down: it hovers), black at alpha 191, softened
previews/   8-facings.png            the assembled unit (shadow, hull and rack laid over each other on one canvas;
                                     the engine's seat for the rack not applied), the mod's frames beside HD
            hull-8-facings.png, rack-8-facings.png, shadow-8-facings.png   the three sheets, every 4th facing
            turn.gif                 all 32 facings in turn, the mod's frames beside HD
            scale.png                next to the HD harvester, as the game draws them
ts-hvr-hd-3d/   the 3D model, in its own zip (ts-hvr-hd-3d.zip) next to this folder:
            tshvr.glb    the hull and the rack in TS's own colours, each under its own node; the mod's camera
src/        the model builder, the renderer and the checks (see Rebuilding below)


What it is
----------
One 3D model rebuilt straight from TS's own voxels (HVR.VXL (the hull) and HVRTUR.VXL (the rack), each posed by its
own HVA), drawn the way the HD buildings and units are.
- Shape: every voxel's step is TS's.  Each voxel section's voxels are merged into boxes and cut at 45 degrees along
  the solid's convex edges (so its corners read as pressed plate); where two boxes of a section meet, nothing
  shows.  The shading rounds every edge that faces the air, and carries TS's own voxel normals as a layer of detail
  (the bevels, seams, vents and slots TS shades into its voxels).
- Colours: TS's own.  Every surface takes the palette colour (UNITTEM.PAL) of the voxels just inside it; TS's single
  voxels of darker or lighter speckle are held near the colour round them, while its near-black and near-white
  voxels (slots, hatches, highlights) keep their colour.  House colour is pure green 0,214,0 x (1 + 1.1 grain)
  wherever TS's remap voxels are, with TS's remap shades kept as darker and lighter seams; the -trim masks cover
  exactly that.
The finished frames cover the mod's frames with a silhouette overlap of 0.89 (src/vcheck.py).


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 2.95 canvas px per voxel,
  the hull's position (TS's HVA origin) at canvas (95.5, 106): the size and place the mod's frames have (found by
  matching TS's voxels to them: overlap 0.95).  This canvas has half the other units' density, so the game draws it
  at 4/3: the outline is 0.75 canvas px wide here, so it comes out as wide in the game as on the other units.
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
The rack is TS's voxels exactly; its frames keep the mod's content centres, so TurretOffset=-64 and
PrimaryFireFLH=64,32,128 stand with the seats as dialled.


3D model (ts-hvr-hd-3d/)
------------------------
- Nodes: HoverMLRS > unit_facing_east > hull, rack (the rack at TS's HVA place; the mod seats it per facing by its own
  tables, so the check below draws the hull alone over the hull frame).
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.  The unit faces east (the mod's facing 24).
- The meshes are exact (each voxel section's boxes), subdivided so the vertex colours carry TS's colours.
- Camera "camera_mod": orthographic, the mod's camera, framing the canvas exactly (checked by drawing the mesh
  through it over frame 24: overlap 0.977).
- The file passes Khronos's glTF validator with no errors or warnings.
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
- Built straight from TS's voxels (above), not hand-modelled: nothing is interpreted, every detail is where TS
  has it.
- TS's single-voxel speckle held near the colour round it (its paint is speckled voxel by voxel).
- The shadow frames are the HD hull's own silhouette at the mod's offset (TS draws a hovering unit's shadow as a
  flat shape under it), softened like the other units' shadows.
- The rack's base ring (HVRTUR.VXL's five lowest voxel layers, the part that sits down in the hull's turret ring) is
  left off the rack frames, as the mod's rack frames have it: drawn over the hull, it would cover the deck, and it
  would pull each frame's centring 3-7 px off the pods.  The .glb leaves it off too.


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are.
  vxlunit.py, tsnormals.py   a voxel section as boxes, its convex edges, TS's colours and normals across its faces
  voxrender.py           one frame of a voxel unit with the buildings' look
  rc.py, rcrender.py     the ray caster and the buildings' look for models made of convex parts
  vexport.py, rcexport.py   the .glb;  glbcheck.py  draws the .glb through its camera to check it
  vdeliver.py, vcheck.py    renders, previews and checks a unit from its spec
  hvrrender.py           the frame layout, the rack's centring and the shadow frames;  hvrspec.py  previews, README
    PKG=out python3 vdeliver.py hvrspec render 0 1      renders frames/

