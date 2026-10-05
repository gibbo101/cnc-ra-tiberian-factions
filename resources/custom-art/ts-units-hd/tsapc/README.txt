Amphibious APC (TS [APC]) in HD for Tiberian Factions: TSAPC  -  v2
===================================================================

frames/     tsapc-0000.png ... tsapc-0063.png, the mod's 64 frames on its 384 x 384 canvas, each with a -trim.png
            (white = house colour, antialiased):
              0-31    on land, with its shadow, 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E)
              32-63   on water: the water hull TS swaps in (APCW.VXL), no shadow, 32 facings
previews/   land-8-facings.png, water-8-facings.png   the mod's frames beside HD, every 4th facing
            turn-land.gif, turn-water.gif   all 32 facings in turn, the mod's frames beside HD
            scale.png                next to the HD harvester and EA's APC, as the game draws them
            shape-8-facings.png      the model drawn flat (a colour per part) in the mod's camera beside the mod's
                                     frames, land and water, with the silhouette overlap per frame
ts-apc-hd-3d/   the 3D models, in their own zip (ts-apc-hd-3d.zip) next to this folder:
            tsapc.glb, tsapc-water.glb   the land hull and the water hull (vertex colours), with the mod's camera
src/        the model, the renderer and the checks (see Rebuilding below)

v2 replaces v1: same canvas, place, frame layout and shadow.


What changed from v1
--------------------
v1 copied TS's voxels box by box, so it still read as voxels.  v2 is built the way the Titan, the Wolverine, the
MCV and the Mammoths are: TS's voxels are the blueprint (where every part is and how big), and each part is modelled
clean - flat plates, true slopes, round wheels, bevelled edges - in TS's own colours.  The detail the voxels lose
comes from Westwood's own art of the APC (the Beachhead FMV Luke sent: swimming, and landed with the troops coming
out at the front) and, where the FMV doesn't show a part, from the fan-made HD APC Luke sent (ArtStation), always
where TS's voxel has the part.

The APC, part by part:
- The upper hull (TS's): upright sides overhanging the wheels, its shoulders stepping in to a flat roof, its back's
  top edge chamfered, its bow sloping above and below to the stem (TS: a boat's bow, for the water).  TS's panel lines
  (its darker remap shades) as seams: joints across the roof and down the sides; the rear door between TS's lines
  across the back, its handle, TS's two dark lamps at its top corners, the dark bumper below it.  A row of small
  plates along the top of the sides (Westwood's FMV).
- The roof: TS's cupola - a raised ring of dark periscope blocks round a hatch, open at the back; TS's louvred vents
  on the rear shoulders over the rear wheels; the driver's cab at the front (TS's dark block and slot there): a raised
  box with TS's dark hatch on top and a two-pane windscreen in its sloping front (Westwood's FMV, the fan model), a
  searchlight on its front corner (Westwood's FMV).
- The bow: a plain panel across its front between TS's lines, two lamps in square housings on its left half, lit
  (Westwood's FMV); the troop ramp in its sloping underside, ribbed, hinged at its foot (Westwood's FMV: the troops
  come out at the front).
- The sides: the door between the rear wheel pair and the front wheel (TS's darker shade there) with a ladder of
  rungs (Westwood's FMV, the fan model), the panel over the front wheel as a mesh grille (TS's darker shade there,
  Westwood's FMV).
- Six wheels (TS's: a pair at the back, one at the front): treaded tyres, TS's grey hubs, lighter in the middle, with
  six wheel nuts.
- On water (APCW.VXL, TS's upper hull alone sunk to its waterline): the same upper hull and roof.

The model's silhouette overlaps the mod's frames by 0.91 drawn flat in the mod's camera (land 0.94,
water 0.89: the mod's water frames have gaps through their hull) (shape-8-facings.png); the finished frames
by 0.918 (src/vcheck.py).


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.25 canvas px per voxel.
  The land hull's position (TS's HVA origin) at canvas (191, 190.35), the water hull's at (191.5, 158), as v1 and the
  mod's frames have them.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides
  facing the camera as on the other units; plate edges are bevelled in the shading.  The game draws this canvas at
  two thirds (8 canvas px per classic pixel), so the outline, the shadow's blur and the contact shadow are 1.5 times
  as wide on the canvas.
- House colour is pure green 0,214,0 x (1 + 1.1 grain) over the whole body, as TS has it (its remap voxels), detail
  only as thin seams, plates and rungs; the -trim masks cover exactly that (not the windscreen, the mesh grille or
  the lamps).
- The rest in TS's colours: dark periscopes, hatch, lamps and bumper, black tyres on grey hubs; the windscreen's dark
  glass, the lamps' amber; grime rising from the ground on the running gear.


Shadow
------
The land frames (0-31) carry the unit's shadow, black at alpha 191 (75%), blurred, falling to the right and a little
towards the camera, as long as the buildings' and the harvester's (v1's).  Within 14 px of the canvas edge it fades
out.  The water frames (32-63) carry none.


3D models (ts-apc-hd-3d/)
-------------------------
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.  The unit faces east (the mod's facing 24).
- Nodes: AmphibiousAPC > unit_facing_east > land_hull; AmphibiousAPC_water > unit_facing_east > water_hull, each
  holding its parts (hull, cab, cupola, periscope, vent, tyre, hub, ...).  The meshes are exact (each part cut from
  its own planes and curved surfaces).
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 384 canvas exactly
  (checked by drawing the land mesh through it over frame 24: overlap 0.990).
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).
- Khronos's glTF validator: errors 0, warnings 0, infos 0, hints 0 (both files).


Judgement calls (each one easy to change)
-----------------------------------------
- One paint colour per part (TS's), rather than TS's voxel-by-voxel speckle (v1).
- Westwood's FMV first, the fan model where the FMV doesn't show a part, and only where TS's voxel has the part:
  left out are the fan model's antennas, exhaust stack and side windows, and the FMV's markings ("D2EG12", the
  triangle), which TS's voxel doesn't have.
- The bow's two lamps on its left half only, as Westwood's FMV shows them.
- The cab raised a voxel over the roof (TS: its dark block raised, the slot in front of it flush), so the windscreen
  slopes as the FMV's and the fan model's do.
- The water hull drawn complete (the mod's current water frames show gaps through it), placed where the mod's water
  frames have it.
- The shadow as v1's: the buildings' length, alpha 191 (the mod ships about 150; at least 128).


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are (TS's voxels,
the mod's frames, the harvester and EA's APC for the previews).
  rc.py, rcrender.py      a ray caster for models made of convex parts, with the buildings' look
  rcexport.py             convex parts to meshes (exact), for the .glb;  glbtools.py  the .glb writer
  qparts.py               parts built in a voxel section's own frame
  apcmodel.py             the model's parts (the voxels as the blueprint), posed by TS's HVAs, land and water
  apcmat.py               materials;  apccam.py  canvas, camera, frame layout
  apcrender.py            one frame;  apcspec.py  the frames, previews and checks for vdeliver.py
  apcexport.py            the .glb files;  glbcheck.py  draws a .glb through its camera to check it
  vdeliver.py, vcheck.py  renders, previews and checks a unit from its spec
  apcshape.py             the shape check;  avox.py, apclook.py, hcls.py  TS's voxels, sheets
    PKG=out python3 vdeliver.py apcspec render 0 1      renders frames/
    python3 apcexport.py tsapc.glb tsapc-water.glb
