Orca Bomber (TS [ORCAB]) in HD for Tiberian Factions: TSORCAB  -  v3
====================================================================

frames/     tsorcab-0000.png ... tsorcab-0031.png, the mod's 32 frames on its 384 x 384 canvas, each with a -trim.png
            (white = house colour, antialiased), no shadow; 32 facings counter-clockwise from north (0 N, 8 W, 16 S,
            24 E)
previews/   8-facings.png            the mod's frames beside HD, every 4th facing
            turn.gif                 all 32 facings in turn, the mod's frames beside HD
            scale.png                next to the HD harvester, the HD Orca Fighter and EA's Hind, as the game draws
                                     them
            shape-8-facings.png      the model drawn flat (a colour per part) in the mod's camera beside the mod's
                                     frames, every 4th facing, with the silhouette overlap
            closeups.png             the body, the fans and the bays at 3x in two facings
            nose-closeup.png         the nose and the canopy at 4x in four facings
ts-orcab-hd-3d/  the 3D model, in its own zip (ts-orcab-hd-3d.zip) next to this folder:
            tsorcab.glb  the aircraft (vertex colours), with the mod's camera
src/        the model, the renderer and the checks (see Rebuilding below)

v3 replaces v2 (and v1): v2's canvas, size, place, facings, frame layout, model and paint, with TS's red lamp
made a beacon.


What changed from v2
--------------------
- TS's red lamp behind the canopy (Luke: the pink blob is meant to be a light): v2 had it as a red block the size of
  TS's voxels (x 34..36, y 18..21, z 9..11), which read as a blob.  v3 makes it a beacon on the spine's front end:
  a red glass dome (1.6 voxels across, 0.8 high) on a dark ring, deep red lit brighter towards its top with a
  highlight, glowing a little (TS paints it its bright red, TS 6).
- Nothing else changed: the shape, the canopy, the fans, the rest of the paint and the house colour are v2's.


What changed from v1 (in v2)
----------------------------
v1 was TS's voxels drawn box by box, so it still read as voxels.  v2 on are built the way the Titan, the Wolverine,
the Dropship and the Orca Fighter are: TS's voxel (ORCAB.VXL) is the blueprint - where every part is and how big - and
each part is modelled clean (flat plates, true slopes, round fans and booms, bevelled edges) in TS's own colours, with
panel joints, vents and bolts.  The voxel is the source of truth: every part, step and colour below was read from it
slice by slice.  The two renders Luke sent are the guide to how TS's parts read in HD where TS's voxel has the part:
the faceted canopy over TS's glazed nose, the fans' blades, the booms' segments, bombs in TS's black bays.  House
colour stays where TS paints it.

The Orca Bomber, part by part (TS's layout; q = TS's voxel coordinates, x back to front 0..44, y right to left 0..40,
z up 0..16; the model is symmetric about y 20, TS's fans' and booms' centre line):
- Two big lift fans at the wingtips (TS: x 20..32, y 0..11 and 29..40): TS's brown rims (z 6..10, radius 5.75), round,
  with joints round them; inside each, twelve light grey blades (TS's light grey) on a dark hub with a spinner; under
  the rim TS's black throat, its foot lower on the side towards the body as TS's (z 4 there, 5 further out).
- The body between the fans (TS: x 18..35, y 10..30, z 3..10): its back a wedge (z 5..6 at x 18), its top flat at z 10
  to x 28, then the front blocks either side of the nose sloping down to z 8 at their fronts (TS's steps); joints
  across and down its sides, louvres in its back.  On the top TS's house-colour panels either side of the spine (y
  15..19 and 20..25, x 23..33) and strips along its outer edges (y 12 and 26..29), a joint across them; TS's two small
  blocks by the booms (x 26..28), slatted; the spine to the canopy (TS: y 18..21, z 10..11, x 25..35) with joints and
  bolts.
- TS's black bays in the front blocks' faces (two rows, z 3..5 and 6..8, y 13..17 and 22..27), set in, with two bombs'
  noses in each (olive drab), framed; TS's black blocks at the fans' inner front corners (x 32..34, z 4..8): racks,
  slotted across their fronts.
- The nose: the keel under the canopy (TS: y 17..22, x 26..44), its bottom from z 3 at x 26.5 down to z 0 at x 33..40
  and up to the tip at x 44, an access panel with bolts on each side; the canopy over TS's blue glazed nose (x 35..44,
  its top at z 10, its front a 45 degree slope down to z 4 at the tip), faceted, TS's blue as blue glass, grey frames;
  TS's red lamp behind it (x 34..36, z 9..11) a beacon: a red glass dome on a ring, glowing a little (v3).
- The booms (TS: y 12..15 and 25..28, z 7..10, x 0..20): octagonal, a voxel wider at their roots (x 12..20, as TS's),
  segment joints along them (the renders'), TS's dark band at x 15..18.
- The tail: the fins on the booms' ends (TS: x 1..7, z 6..16), canted out at the top, in house colour as TS paints
  them; between the booms the tail fan's housing (TS: its rim at z 10..11, x 2..10), brown, its walls dark olive, a
  small fan in it (TS's grey centre), on a plate joining it to the booms (x 3..9, z 8..10) and a keel through it (x
  1..12).

The model's silhouette overlaps the mod's frames by 0.89 drawn flat in the mod's camera
(shape-8-facings.png), and TS's voxels by 0.93 drawn flat from the same camera (facing 24); the finished frames
overlap the mod's by 0.898 (src/vcheck.py).


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.26 canvas px per voxel, the
  unit's position (TS's HVA origin) at canvas (191.5, 190.72): v1's size and place (found by matching TS's voxel to
  the mod's frames).
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides facing
  the camera as on the other units; plate edges are bevelled in the shading, the fans' rims shaded round.  The game
  draws this canvas at two thirds (8 canvas px per classic pixel), so the outline is 1.5 times as wide on the canvas.
- Paint: TS's colours, one per part - GDI's ochre (TS 144-147, the Dropship's), TS's browns on the fans' rims and the
  tail fan's housing (TS 153-161), light grey blades (TS 41-50) on dark hubs, near-black throats and bays (TS 57-62),
  olive drab bombs, the glazed nose in TS's blue (TS 197) as blue glass lighter towards its top, TS's red lamp (TS 6)
  as the beacon's red glass.
- House colour is pure green 0,214,0 x (1 + 1.1 grain) where TS paints house colour - the fins and the panels and
  strips on the body's top - with thin joints as detail; the -trim masks cover exactly the green.
- It flies: no grime from the ground, no ground occlusion.


Shadow
------
None baked: in flight the game lifts the frame by the aircraft's height and draws its shadow from the same frame,
darkened, on the ground.  The outline is the units' dark outline, so the silhouette reads as a shadow too.


3D model (ts-orcab-hd-3d/tsorcab.glb)
-------------------------------------
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position (TS's HVA origin), as the frames draw it.  The aircraft faces east (the mod's facing
  24); in flight the game lifts it.
- Nodes: OrcaBomber > unit_facing_east > hull (its parts: fan_rim, fan_throat, fan_hub, fan_spinner, fan_blade,
  fan_stator, body, spine, top_panel, top_strip, top_block, bay, bomb, bomb_nose, rack, keel, canopy, beacon, beacon_base, boom,
  boom_root, boom_collar, fin, tailplane, tail_keel, tail_housing, tail_fan_hub, tail_fan_blade...).  The meshes are
  exact (each part cut from its own planes and curved surfaces).
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 384 canvas exactly
  (checked by drawing the mesh through it over frame 24: overlap 0.982).
- Vertex colours: COLOR_0 albedo (no light or shadow; the paint's areas - its joints, slots and bolts are finer than
  the mesh), COLOR_1 house colour (white = house colour).
- Khronos's glTF validator: errors 0, warnings 0, infos 0, hints 0.


Judgement calls (each one easy to change)
-----------------------------------------
- One paint colour per part (TS's), rather than TS's voxel-by-voxel speckle (v1).
- Symmetric about y 20, TS's fans' and booms' centre line; TS's nose, spine, body and tail fan sit half a voxel to the
  right of it.
- The canopy: TS's blue glazed nose made faceted glass (the renders'), kept TS's blue rather than the renders' dark
  glass; its top flat and its front one slope where TS's steps curve.
- The fans: twelve light grey blades on a dark hub in each of TS's brown rims (TS's light grey interior); the renders'
  fans are body-coloured.
- TS's black bays in the front blocks: two bombs' noses in each (the renders show bombs hanging under the front
  blocks; TS's bays are plain black); TS's black blocks by the fans as slotted racks.
- The booms' segment joints (the renders'); TS's dark band kept.
- The fins flat, canted out at the top (TS's bend in and out along their height smoothed).
- The chin one slope from z 3 at x 26.5 to the keel's bottom at x 33 (TS: three steps).
- TS's red lamp a beacon dome (Luke: a light), its top 0.8 voxel over the spine (TS's lamp is flush with it).
- The renders' round lamps on the front blocks and the eagle decals are left off (not in TS's voxel).


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are.
  obmodel.py             the model: every part, in TS's voxel section's own frame, posed by its HVA
  obmat.py               the paint and the detail (joints, bolts, louvres, the canopy's glass), per pixel from each
                         hit's q
  obcam.py               the canvas, the camera and the facings
  obrender.py            one frame:  python3 obrender.py 0,12,24 [ss] [outdir]
  obspec.py              the frames, previews and checks for vdeliver.py
  obexport.py            the .glb;  glbcheck.py  draws the .glb through its camera to check it
  obshape.py             the shape sheet;  obcomp.py  TS's voxels against the model drawn flat, from any facing;
                         obclose.py  close-ups of any frame at any scale
  obvoxd.py, obvox.py, obdump.py, hcls.py   TS's voxel as data, drawn, sliced as text, and its palette classes
  obpkg.py, obtab.py     the package (checks, previews, README, 3D model, zips) and the review page's tab
  rc.py, rcrender.py, qparts.py, rcexport.py, glbtools.py, frameio.py   the ray caster, the buildings' look for
                         models made of convex parts, the .glb writer
  vdeliver.py, vcheck.py    renders, previews and checks a unit from its spec
    PKG=out python3 vdeliver.py obspec render 0 1      renders frames/
