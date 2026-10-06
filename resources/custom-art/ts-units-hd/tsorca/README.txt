Orca Fighter (TS [ORCA]) in HD for Tiberian Factions: TSORCA  -  v4
===================================================================

frames/     tsorca-0000.png ... tsorca-0031.png, the mod's 32 frames on its 384 x 384 canvas, each with a -trim.png
            (white = house colour, antialiased), no shadow; 32 facings counter-clockwise from north (0 N, 8 W, 16 S,
            24 E)
previews/   8-facings.png            the mod's frames beside HD, every 4th facing
            turn.gif                 all 32 facings in turn, the mod's frames beside HD
            scale.png                next to the HD harvester and EA's TD Orca, as the game draws them
            shape-8-facings.png      the model drawn flat (a colour per part) in the mod's camera beside the mod's
                                     frames, every 4th facing, with the silhouette overlap
            closeups.png             the pods, the fans and the body at 3x in two facings
            nose-closeup.png         the nose and the canopy at 4x in four facings
ts-orca-hd-3d/   the 3D model, in its own zip (ts-orca-hd-3d.zip) next to this folder:
            tsorca.glb   the aircraft (vertex colours), with the mod's camera
src/        the model, the renderer and the checks (see Rebuilding below)

v4 replaces v3 (and v2, v1): v3's canvas, size, place, facings, frame layout, model and paint, with a red
rocket nose in each rocket tube.


What changed from v3
--------------------
- The rocket tubes (Luke: "Add the red tips"): a rocket in each of the twelve tubes, its red nose cone seen in the
  tube's mouth (the FMV's red rocket tips; TS's tubes are black), shaded lighter towards its top with a small
  highlight, a dark ring of the bore round it and the tube's lower inner wall below it.
- Nothing else changed: the shape, the canopy, the fans, the rest of the paint and the house colour are v3's.


What changed from v2 (in v3)
----------------------------
- The nose's sides (Luke: "Do we need the house color on the sides of the cockpit? We could remove that"): TS paints
  the lower nose's sides house colour (x 33..38, z 1..5, under the canopy); v3 on paint them GDI's ochre like the rest
  of the nose, their panel joints kept, and the -trim masks no longer cover them.


What changed from v1 (in v2)
----------------------------
v1 was TS's voxels drawn box by box, so it still read as voxels.  v2 on are built the way the Titan, the Wolverine,
the Dropship and the Mobile EMP Cannon are: TS's voxel (ORCA.VXL) is the blueprint - where every part is and how big -
and each part is modelled clean (flat plates, true slopes, round fans and tubes, bevelled edges) in TS's own colours,
with panel joints, hatches, vents and bolts.  The voxel is the source of truth: every part, step and colour below was
read from it slice by slice.  Westwood's art Luke sent (the TS intro's FMV, TS's cameo) and a mod's render are the
guide to how TS's parts read in HD where TS's voxel has the part: the faceted canopy over TS's cockpit, the fans'
blades, the vents behind the canopy.  House colour stays where TS paints it, except the nose's sides (v3, Luke).

The Orca Fighter, part by part (TS's layout; q = TS's voxel coordinates, x back to front 0..41, y right to left 0..25,
z up 0..15; symmetric about y 12.5, TS's centre line):
- Two rocket pods either side of the body (TS: x 23..33, y 0..10 and 15..25, z 2..8), their corners cut as TS's
  steps; six rocket tubes in each front face where TS has its six black squares (y 1..3, 4..6, 7..9; two rows), round
  mouths with a rim round a dark bore, a rocket's red nose in each (the FMV's; Luke); joints round the pods, an access hatch with bolts and a louvred vent on each
  outer side.  On each pod's top TS's raised house-colour panel (x 24..33, y 3..9, z 8..9, its front lip down to z
  7), a joint across it.
- The body between the pods (TS: y 10..15): its belly sloping up from the chin (z 0 at x 31) to z 2.5 at x 23; its top
  TS's spine (y 11..14 at z 10 from x 23) widening to the full top at x 27, a grey hatch on the spine (TS's grey
  voxels at x 25..27), and the hump behind the cockpit (TS: x 27..31, z 10..11), rounded, with the FMV's two vent slots
  a side.  Behind the pods the rear body between the fans (TS: x 16..23, z 6..9), a louvred vent on its top, over a
  keel (TS: down to z 3 at x 19..23).
- The nose (TS: x 32..41): the lower nose (y 9..16, z 1..5), its sides ochre (Luke; TS paints them house colour),
  narrowing at its front to the tip where TS has black cheeks (x 36..38): slatted intakes; the tip (y 11..14,
  z 2..6) with TS's brown top; the chin under it (z 0..1.7).
- The canopy: TS's cockpit is a dark pit in the nose's top (x 32..36, y 11..14) with a slit forward to the tip (x
  36..39) and a dark step up to the body's top behind it (x 31..33).  Here it is the FMV's faceted canopy: dark glass
  over the pit and the slit, its sill on TS's walls, its ridge at most half a voxel over TS's nose, grey frames (the
  ridge, two bows), and TS's dark step behind it its rear pane, up to the hump.
- Two lift fans beside the body behind the pods (TS: x 16..23, y 4..10 and 15..21, z 6..9): TS's house-colour rings,
  round inside, a hub with a spinner and nine grey blades in each (TS: a dark hub and a grey cross).
- The boom to the tail (TS: x 6..17, y 11..14, z 7..9), octagonal, two joints, a fairing under its front (TS: z 6 at
  x 13..16).
- The tail: the tailplane (TS: x 2..7, y 5..20, z 7..9), the tail fan's housing round its duct (TS: the duct x 3..6,
  y 11..14, open through; its rim at z 9..10), its walls TS's dark olive, a small fan in it, a cone behind (TS: x 0..2);
  the two fins at the tailplane's tips (TS: y 4..5 and 20..21, x 0..5, z 5..15), raked back above and below it, in
  house colour as TS paints them.

The model's silhouette overlaps the mod's frames by 0.90 drawn flat in the mod's camera
(shape-8-facings.png), and TS's voxels by 0.92 drawn flat from the same camera (facing 24); the finished frames
overlap the mod's by 0.902 (src/vcheck.py).


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.25 canvas px per voxel, the
  unit's position (TS's HVA origin) at canvas (192.0, 191.04): v1's size and place (found by matching TS's voxel to
  the mod's frames).
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides facing
  the camera as on the other units; plate edges are bevelled in the shading, the fans' rings shaded round.  The game
  draws this canvas at two thirds (8 canvas px per classic pixel), so the outline is 1.5 times as wide on the canvas.
- Paint: TS's colours, one per part - GDI's ochre (TS 149, the Mobile EMP Cannon's), TS's brown on the tip's top
  (TS 154-157), the grey hatch (TS 51), near-black intakes (TS 61-62), the tail duct's dark olive (TS 77-79); grey fan
  blades on dark hubs; the canopy's glass the Dropship's, dark and lighter towards its top, with grey frames; the
  rockets' noses red (the FMV's).
- House colour is pure green 0,214,0 x (1 + 1.1 grain) where TS paints house colour - the fins, the fans' rings, the
  panels on the pods' tops - with thin joints as detail; the -trim masks cover exactly the green.  Not on the nose's
  sides (Luke), which TS paints house colour too: GDI's ochre there.
- It flies: no grime from the ground, no ground occlusion.


Shadow
------
None baked: in flight the game lifts the frame by the aircraft's height and draws its shadow from the same frame,
darkened, on the ground.  The outline is the units' dark outline, so the silhouette reads as a shadow too.


3D model (ts-orca-hd-3d/tsorca.glb)
-----------------------------------
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position (TS's HVA origin), as the frames draw it.  The aircraft faces east (the mod's facing
  24); in flight the game lifts it.
- Nodes: OrcaFighter > unit_facing_east > hull (its parts: pod, pod_cover, pod_cover_lip, rocket_tube, body, deck,
  bulkhead, hump, spine_hatch, rear_body, keel, nose_lower, nose_upper, nose_tip, chin, canopy, fan_ring, fan_hub,
  fan_spinner, fan_blade, fan_floor, boom, boom_fairing, tailplane, tail_housing, tail_fan_hub, tail_fan_blade,
  tail_cone, fin...).  The meshes are exact (each part cut from its own planes and curved surfaces).
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 384 canvas exactly
  (checked by drawing the mesh through it over frame 24: overlap 0.974).
- Vertex colours: COLOR_0 albedo (no light or shadow; the paint's areas - its joints, slots and bolts are finer than
  the mesh), COLOR_1 house colour (white = house colour).
- Khronos's glTF validator: errors 0, warnings 0, infos 0, hints 0.


Judgement calls (each one easy to change)
-----------------------------------------
- One paint colour per part (TS's), rather than TS's voxel-by-voxel speckle (v1).
- The nose's sides GDI's ochre (Luke); TS paints them house colour.
- The canopy: TS's open pit and slit made the FMV's faceted dark glass, its ridge at most half a voxel over TS's nose;
  TS's dark step behind it its rear pane.
- The fans: nine grey blades on a hub in each of TS's house-colour rings (TS: a dark hub and a grey cross); the tail
  fan the same, smaller, in TS's dark-walled duct.
- The rocket tubes: TS's six black squares a pod made round tube mouths with rims; the lower row raised half a voxel
  (TS: z 2..4) to sit on the face above its bevelled foot.  A red rocket nose in each (Luke; the FMV's red tips -
  TS's tubes are black).
- TS's black cheeks on the nose made slatted intakes.
- The FMV's two vent slots a side on the hump behind the canopy; louvres on the pods' outer sides and the rear body's
  top (TS's parts are plain there).
- The fins 1.45 voxels thick and flat (TS's are 2 voxels thick and bend half a voxel along their height).
- Westwood's shark mouth, the FMV's "12" and the eagle decals are left off (not in TS's voxel).


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are.
  orcamodel.py           the model: every part, in TS's voxel section's own frame, posed by its HVA
  orcamat.py             the paint and the detail (joints, bolts, louvres, the canopy's glass), per pixel from each
                         hit's q
  orcacam.py             the canvas, the camera and the facings
  orcarender.py          one frame:  python3 orcarender.py 0,12,24 [ss] [outdir]
  orcaspec.py            the frames, previews and checks for vdeliver.py
  orcaexport.py          the .glb;  glbcheck.py  draws the .glb through its camera to check it
  orcashape.py           the shape sheet;  ocomp.py  TS's voxels against the model drawn flat, from any facing;
                         orcaclose.py  close-ups of any frame at any scale
  orcavox.py, ovox.py, odump.py, hcls.py   TS's voxel as data, drawn, sliced as text, and its palette classes
  opkg.py, otab.py       the package (checks, previews, README, 3D model, zips) and the review page's tab
  rc.py, rcrender.py, qparts.py, rcexport.py, glbtools.py, frameio.py   the ray caster, the buildings' look for
                         models made of convex parts, the .glb writer
  vdeliver.py, vcheck.py    renders, previews and checks a unit from its spec
    PKG=out python3 vdeliver.py orcaspec render 0 1      renders frames/
