Carryall (TS [TRNSPORT]) in HD for Tiberian Factions: TSCARRY  -  v2
====================================================================

frames/     tscarry-0000.png ... tscarry-0031.png, the mod's 32 frames on its 448 x 448 canvas, each with a -trim.png
            (white = house colour, antialiased), no shadow; 32 facings counter-clockwise from north (0 N, 8 W, 16 S,
            24 E)
previews/   8-facings.png            the mod's frames beside HD, every 4th facing
            turn.gif                 all 32 facings in turn, the mod's frames beside HD
            carrying.png             carrying the HD harvester as the mod draws it (6 classic px below the
                                     Carryall's centre, drawn after it), every 4th facing
            scale.png                next to the HD harvester, the HD Orca Bomber and EA's RA Chinook, as the game
                                     draws them
            shape-8-facings.png      the model drawn flat (a colour per part) in the mod's camera beside the mod's
                                     frames, every 4th facing, with the silhouette overlap
            closeups.png             the pods, the hoist and its claws, and the tail at 3x
            cab-closeup.png          the cab and the engine under it at 3x in four facings
ts-carry-hd-3d/  the 3D model, in its own zip (ts-carry-hd-3d.zip) next to this folder:
            tscarry.glb  the aircraft (vertex colours), with the mod's camera
src/        the model, the renderer and the checks (see Rebuilding below)

v2 replaces v1: v1's canvas, size, place, facings and frame layout; a new model and paint.


What changed from v1
--------------------
v1 was TS's voxels drawn box by box, so it still read as voxels.  v2 is built the way the Titan, the Wolverine, the
Dropship and the Orcas are: TS's voxel (TRNSPORT.VXL) is the blueprint - where every part is and how big - and each part
is modelled clean (flat plates, true slopes, round fans, bevelled edges) in TS's own colours, with panel joints, vents
and bolts.  The voxel is the source of truth: every part, step and colour below was read from it slice by slice.  The
references Luke sent (TS's cameo, the "3D Render" mod Carryall, the Tiberium Essence render and two stills from TS's
FMV) are the guide to how TS's parts read in HD where TS's voxel has the part: the fans' straps and blades, the jointed
claws under the hoist, the round engine under the cab, the fan in the tail fin's duct.  House colour stays where TS
paints it.

The Carryall, part by part (TS's layout; q = TS's voxel coordinates, x back to front 0..52, y right to left 0..39, z up
0..19; the model is symmetric about y 19.25, w the distance out from it):
- Four ducted lift fans (TS: rims z 10..15): two at the back (centres x 7.4, w 13 either side) and two at the front
  (x 40.5, w 10.2), their rims 6.5 in radius.  TS's thick ochre rims (r 4.3..6.5), a darker row under them;
  TS's house colour on the outer quarter of each rim - from just past its outward point round to its end (the back
  fans' backs, the front fans' fronts), from the foot of the rim to under its top lip; ten straps round each rim (the
  renders'), two of them crossing the house colour where TS leaves two ochre gaps in it.  Inside, ten dark blades on a
  grey hub whose top is flush with the rim (TS: black inside, a grey hub with a light top), over a dark floor.
- The beam from the tail to the cab (TS: z 10..15): 6 wide at mid height with its top 3 wide as far as the pods (x
  5..31), a 5 wide box in front of them (x 31..43); joints across it, bolts along its top, a keel strip under its front
  (x 30..38, z 9..10).
- TS's house-colour pods along the beam's sides over the hoist (x 17..31.5, out to w 6.2 at x 21..25, z 11..15): their
  tops level with the beam's from x 21, bevelled down to their outer faces; TS's khaki patches on their tops as vents
  (x 20..23.5), a hatch on each outer face, and TS's three rust-red spots low on each outer face (x 18.5, 21.5, 24.5;
  TS 106) as small domes.
- The fans' arms: at the back to the tail block (x 4..11, z 11..13), at the front to the cab (x 37..43, z 12..14).
- The cab (x 39.5..52, w 3 either side, z 6..14): its roof a voxel under the beam's top (x 43..47), the windscreen one
  slope through TS's steps down to the nose (z 14 at x 47 to 11.2 at x 51.6), the nose's face (x 52, z 7..11).  TS's
  black windows - the roof's front (x 46..47.6), the windscreen (x 48.5..51.3) and the sides beside them (z 12..13.5) -
  as dark glass, blue as the cameo's; the frame behind the roof glass in TS's grey, the bar between it and the
  windscreen in TS's olive; a door on each side; TS's rust-red marks on its sides (x 40..41, z 9) as small lamps.
  Under it TS's house-colour engine (x 41.5..51, r 2.1, its bottom at z 4) with the intake in its front (TS's hole,
  brown inside), and TS's nose gear: a pad (x 40..48, z 1..2) on a post and a light grey strut.
- The hoist (TS: centre x 24.75): TS's grey bell under the beam, r 5 at its flat bottom (z 7) to 3.35 under the beam
  (z 10), panelled; four claws on its diagonals, as TS's: an ochre bracket under the pod (z 8..11), a black upper arm
  out and down to the knee (r 10 from the bell's centre, z 5), a grey finger down to z 1, its tip hooked in (the FMV's);
  pivots at the bracket and the knee.
- The tail: the fin (x 0..11, w 1.85 either side, its top at z 19 over x 1..4.6, its leading edge down to the beam at x
  11) with TS's round duct through it (centre x 3, z 15.75, r 1.7), a brown lip round it on each face and a small fan
  in it (TS's grey hub and black blades); the tail block under the fin (x 0..15, w 5 at z 7..10, its bottom at z 6, its
  back sloping from z 12 at x 0 to z 6 at x 4, its sides drawn in at both ends), TS's brown strip along its upper
  sides; a keel under its front (x 11..15, z 9).
- TS's landing gear under the tail block: a skid each side (x 4..14, w 3.75 either side, its front turned up) on a leg
  (x 6..10) with a light grey strut over it (z 3..5), posts up into the block.

The model's silhouette overlaps the mod's frames by 0.91 drawn flat in the mod's camera
(shape-8-facings.png), and TS's voxels by 0.93 drawn flat from the same camera (facing 24); the finished frames
overlap the mod's by 0.916 (src/vcheck.py).


Carrying
--------
The mod draws a carried vehicle after the Carryall, 6 classic px (48 canvas px here, 32 px in the game) below its
centre and lifted with it.  carrying.png draws the HD harvester (the hand-off's example frames, at the game's scale,
their ground shadow left out) that way under every 4th facing: the harvester covers the bell and the claws, as it
will in the game.  The claws stand where TS's do (their fingers 10 voxels out from the bell's centre on the
diagonals, down to z 1).


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.30 canvas px per voxel, the
  unit's position (TS's HVA origin) at canvas (223.5, 222.9): v1's size and place (found by matching TS's voxel to
  the mod's frames).
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides facing
  the camera as on the other units; plate edges are bevelled in the shading, the fans' rims, the bell, the engine and
  the tail's duct shaded round.  The key light's shadow is tested a little off each face and the sky's occlusion
  weighted by how squarely each direction meets the face, so the big flat faces (the fin's sides) carry no stripes
  from the light maps.  The game draws this canvas at two thirds (8 canvas px per classic pixel), so the outline is
  1.5 times as wide on the canvas.
- Paint: TS's colours, one per part - GDI's ochre (TS 144-147, the Dropship's and the Orcas'), TS's darker ochre and
  browns on the straps, the rims' undersides, the brackets and the duct's lip (TS 148-161), TS's grey bell, fingers
  and hubs (TS 44-51) with light grey hub tops and gear struts (TS 39-43), black upper arms and pivots (TS 57-62),
  dark grey gear (TS 52-56), TS's khaki vents (TS 133-137), TS's rust red (TS 106) on the domes and lamps, TS's black
  windows as dark glass with a blue reflection.
- House colour is pure green 0,214,0 x (1 + 1.1 grain) where TS paints house colour - the pods, the engine under the
  cab, the outer quarter of each fan's rim - with thin joints as detail; the -trim masks cover exactly the green.
- It flies: no grime from the ground, no ground occlusion.


Shadow
------
None baked: in flight the game lifts the frame by the aircraft's height and draws its shadow from the same frame,
darkened, on the ground.  The outline is the units' dark outline, so the silhouette reads as a shadow too.


3D model (ts-carry-hd-3d/tscarry.glb)
-------------------------------------
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position (TS's HVA origin), as the frames draw it.  The aircraft faces east (the mod's facing
  24); in flight the game lifts it.
- Nodes: Carryall > unit_facing_east > hull (its parts: fan_rim, fan_strap, fan_hub, fan_spinner, fan_blade,
  fan_floor, rear_arm, front_arm, spine, spine_front, keel, pod, pod_dome, cab, cab_chin, engine, cab_lamp, nose_pad,
  nose_post, nose_strut, hoist_bell, claw_bracket, claw_arm, claw_pivot, claw_finger, claw_tip, fin, duct_lip,
  tail_fan_hub, tail_fan_blade, tail_block, tail_keel, skid, skid_tip, leg, strut, strut_post...).  The meshes are
  exact (each part cut from its own planes and curved surfaces).
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 448 canvas exactly
  (checked by drawing the mesh through it over frame 24: overlap 0.976).
- Vertex colours: COLOR_0 albedo (no light or shadow; the paint's areas - its joints, slots and bolts are finer than
  the mesh), COLOR_1 house colour (white = house colour).
- Khronos's glTF validator: errors 0, warnings 0, infos 0, hints 0.


Judgement calls (each one easy to change)
-----------------------------------------
- One paint colour per part (TS's), rather than TS's voxel-by-voxel speckle (v1).
- Symmetric about y 19.25: TS's beam, cab, hoist and claws are centred on y 19.0, its fans on 19.35 and the beam's
  front box on 19.5; TS's left landing skid and pod are a voxel wider than its right.
- The fans' straps (the renders'; TS's rims are plain ochre outside the house colour, with two ochre gaps in it) and
  their blades (TS's inside is black with a grey hub; the FMV shows spokes).
- The house colour on each fan as one band over TS's patch (TS's edges are ragged voxel by voxel).
- The cab's windows: TS's black windows as dark glass with a blue reflection (the cameo's windows are blue).
- The tail's duct is a real duct through the fin with a small fan in it (TS paints the fan's hub and blades on both
  faces of a closed fin).
- The claws: TS's four claws as jointed arms (a bracket, a black upper arm, a pivot at the knee, a grey finger), a
  little slimmer than TS's voxels; their tips hooked in (the FMV's; TS's fingers end square).
- TS's rust-red spots (TS 106) kept in TS's colour as small domes: three low on each pod (where the FMV has white
  domes) and one each side of the cab (where the FMV has a small red light).
- TS's khaki patches on the pods as vents; the hatches on the pods, the cab's doors and the panel joints and bolts are
  detail on TS's parts.
- The tail block's sides drawn in at its back and front as one plane each (TS's steps), its bottom front one slope from
  z 6 to 9 (TS: three steps); TS's brown strip along its upper sides on its upper bevel.
- The windscreen one slope through TS's three steps; the engine's front leans back at its foot as TS's does.
- The landing gear as TS has it (the FMV's Carryall flies with its gear out of sight).
- Left out (not in TS's voxel): the FMV's lettering and logos.


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are.
  cmodel.py              the model: every part, in TS's voxel section's own frame, posed by its HVA
  cmat.py                the paint and the detail (joints, bolts, vents, the house-colour bands, the cab's glass),
                         per pixel from each hit's q
  ccam.py                the canvas, the camera and the facings
  crender.py             one frame:  python3 crender.py 0,12,24 [ss] [outdir]
  cspec.py               the frames, previews and checks for vdeliver.py
  cexport.py             the .glb;  glbcheck.py  draws the .glb through its camera to check it
  cshape.py              the shape sheet;  ccomp.py  TS's voxels against the model drawn flat, from any facing;
                         cqdiff.py  the same in TS's own axes;  cclose.py  close-ups of any frame at any scale
  ccarry.py              the Carryall carrying the HD harvester, as the mod draws it
  cvoxd.py, cvox.py, cdump.py, hcls.py   TS's voxel as data, drawn, sliced as text, and its palette classes
  cpkg.py, ctab.py       the package (checks, previews, README, 3D model, zips) and the review page's tab
  rc.py, rcrender.py, qparts.py, rcexport.py, glbtools.py, frameio.py   the ray caster, the buildings' look for
                         models made of convex parts, the .glb writer
  vdeliver.py, vcheck.py    renders, previews and checks a unit from its spec
    PKG=out python3 vdeliver.py cspec render 0 1      renders frames/
