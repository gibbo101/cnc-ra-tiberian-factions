Mammoth Mk. II (TS [HMEC]) in HD for Tiberian Factions: TSHMEC  -  v3
=====================================================================

frames/     tshmec-0000.png ... tshmec-0255.png, the mod's 256 frames on its 576 x 576 canvas, each with a -trim.png
            (white = house colour, antialiased).  frame = facing x 8 + step: 32 facings counter-clockwise from north
            (0 N, 8 W, 16 S, 24 E), 8 walk steps (TS's HVA frames 0, 2, 4, 6, 8, 11, 13, 15), 8 ticks a step.
previews/   8-facings.png              the mod's current frames (TS's voxel as the mod draws it now) beside HD, step 0,
                                       every 4th facing
            32-facings.png             all 32 facings at step 0
            turn.gif                   all 32 facings in turn, the mod's current frames beside HD
            walk-east-southeast.gif, walk-south-northwest.gif   the walk, the mod's current frames beside HD
            scale.png                  next to the HD harvester, the HD Titan and EA's Mammoth, as the game draws them
            shape-8-facings.png        the model drawn flat (a colour per part) in the mod's camera beside the mod's
                                       frame, with the silhouette overlap per facing
ts-hmec-hd-3d/   the 3D model, in its own zip (ts-hmec-hd-3d.zip) next to this folder:
            tshmec.glb                 the model (vertex colours), a node per TS section, the walk as an animation,
                                       the mod's camera
src/        the model, the renderer and the checks (see Rebuilding below)

v3 replaces v1 and v2 throughout: same canvas, place, frame layout, walk and shadow.  v2 rebuilt the model; v3
(Luke: no black box on the front, more detail, as Westwood's art) rebuilds its front from Westwood's rain-and-lightning
FMV and render - two stacked bays with lit blue window bands in place of v2's dark face - with a lamp on each top
corner, a ball turret for the chin gun, and TS's grey on the front hip bearings.


What changed from v1
--------------------
v1 copied TS's voxel step by step, so it still read as voxels.  v3 is built the way the Titan, the Wolverine and
the MCV are: TS's voxel is the blueprint (where every part is and how big), and each part is modelled clean - flat
plates, true slopes, round pins and tubes, bevelled edges - in one paint colour per part, TS's own.  The details the
voxel loses come from Westwood's own art of the Mk. II (the render, the FMV stills and the sidebar icon Luke sent).
It still walks with TS's own walk: every section is posed by HMEC.HVA as TS poses it, except that the body keeps
only 40% of TS's side-to-side roll (BODY_ROLL_SCALE in src/hmec2.py), so the hull stays level as it walks.

The Mk. II, part by part:
- Hull: the wide middle, its top crowned (TS's steps as a curve), two plated panels each side of the rails with bolts
  and a joint across, an inset panel on its back and front faces each side of the middle.
- The railgun: two light grey rails along the top on a brown bed with a row of bolts, TS's dark groove between them,
  running back over the breech (TS's grey block where the rails end behind the hull).  The long front block (TS's
  housing, 7 voxels wide, half a voxel left of the body's middle as TS has it): plate joints down its sides, a collar
  round its middle (TS's flange), TS's dark slot along its top, a louvred vent at its front top (the render's), TS's
  grey recess low on each side (with ribs), its top sloping down to the front.  Its front (Westwood's FMVs and
  render): TS's ochre frame as a hood round two stacked bays, each with a visor plate sloping down to the front and a
  lit blue window band along its top, where TS has its light band over grey; a lamp on each top corner (the FMV's
  searchlight).
- The chin gun under the front: a grey ball turret (the render's and the FMVs'; TS's grey there), its barrel pointing
  down and forward as TS's, a sleeve at its root.
- The keel under the hull with TS's belly, rising at the back into the spine's tail (TS's middle column behind the
  hull) and running on under the front hips.
- The missile pods (house colour): the two side pods are tube blocks open at both ends, with two round tube mouths
  stacked in each end (the render's twin "lenses"), on a mount against the hull; the two rear pods sit on the rear
  corner boxes, with six tube mouths each (two rows of three, as the render's pod) set in a frame on their fronts.
  Inset panels, seams and bolts on top.
- The side bays (TS's grey, between the rear boxes and the side pods) with a khaki hatch and handle, TS's ochre post
  at their back; the rear corner boxes with inset panels and bolts.
- The hips: the front legs' in TS's house-colour covers, outside each TS's grey bearing plate in a dark rim with a
  ring of bolts round a light grey axle cap; the rear legs' in TS's grey housings, a cap outside each.
- The legs, each from its own TS sections (TS's four legs differ: the right front and the left rear thigh slant
  forward, the other two back; the HVA's hip, knee and ankle are fixed in each, so every thigh, shin and foot spans
  its own joints): brown thighs (TS's outline) with TS's darker ochre at the knee end as a round plate, a dark pin
  through each knee; light grey shins (TS's outline) with a grille on the front and a dark pin at the ankle; TS's
  house-colour guards on the front shins and its ochre plate on the right rear shin; TS's plus-shaped feet, ochre
  with treads across the toes, a hub, and two pistons from the front and back toes up to the ankle (TS's grey struts,
  the render's pistons).

The model's silhouette overlaps the mod's frames by 0.94 drawn flat in the mod's camera
(shape-8-facings.png); the finished frames by 0.939 (src/hmec2check.py).


Look
----
- Camera: orthographic, 35 degrees above the ground (your choice for this unit), looking north; 6.8 canvas px per
  voxel, the unit's position (TS's HVA origin, on the ground) at canvas (287.5, 374): the size and place the mod's
  frames have, so the body sits centred on the canvas.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides
  facing the camera as on the Titan, the Wolverine and the MCV (the legs keep more of it under the body, as TS's
  read light there); plate edges are bevelled in the shading.  The game draws this canvas at two thirds, so the
  outline, the shadow's blur and the contact shadow are 1.5 times as wide on the canvas.
- Paint: TS's colours, one per part - ochre (TS 144-147, the walkers' yellow-brown) on the hull, the front block, the
  rear boxes, the keel and the toes; brown thighs (TS 153-156) with darker ochre knee plates (TS 148-152); light
  grey shins; grey bays, hips, breech, chin and recesses; light grey rails with white tops; dark bearings, pins and
  tube mouths; the buildings' grain, grime rising from the ground (lighter on the feet, which TS keeps bright).
- House colour is pure green 0,214,0 x (1 + 1.1 grain) on the four pods, their mounts, the front hip covers and the
  front shins' guards (TS's remap voxels), detail only as thin seams and bolts; the -trim masks cover exactly those
  parts.


Shadow
------
Every frame carries the unit's shadow, black at alpha 191 (75%), blurred, falling to the right (east) and a little
towards the camera, 62% as long as the buildings' (the walkers' length, as the Titan's and the Wolverine's), so it
stays on the canvas.  Within 14 px of the canvas edge it fades out.


Fire points
-----------
The layout is TS's (same sections, same places), so TS's PrimaryFireFLH=80,100,158 and SecondaryFireFLH=
-60,100,158 still point where they did.


3D model (ts-hmec-hd-3d/tshmec.glb)
-----------------------------------
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.
- Nodes: MammothMk2 > unit_facing_east (the mod's facing 24) > one node per TS section (body, thigh_right_front,
  shin_right_front, foot_right_front, ...), each holding its parts (hull, rail, spod, thigh, kneepin, piston, ...).
  The meshes are exact (each part cut from its own planes and curved surfaces).
- Animation "walk": the mod's 8 steps (TS's HVA frames 0, 2, 4, 6, 8, 11, 13, 15), 0.533 s each (8 ticks at 15 a
  second), looping.
- Camera "camera_mod": orthographic, 35 degrees above the ground, looking north; it frames the 576 canvas exactly
  (checked by drawing the mesh through it over frame 192: overlap 0.987).
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).
- Khronos's glTF validator: errors 0, warnings 0, infos 0, hints 0.


Judgement calls (each one easy to change)
-----------------------------------------
- One paint colour per part (TS's), rather than TS's voxel-by-voxel speckle (v1).
- TS's left half (pods, rear boxes, bays, the hull's edge) sits a voxel higher than its right: both halves are
  built level, half a voxel over the right's.
- TS has its ochre shin plate on the right rear leg only, not the left: kept as TS.
- From Westwood's art: the front's two bays with their lit blue window bands and the lamps on its top corners (TS
  shows a grey face, lighter at the top, and no lamps), the chin's ball turret, the side pods' twin round tube
  mouths, the rear pods' six, the vent, the feet's pistons.  Left out because TS doesn't have them: the render's red
  missile tips and its "17".  Say if you want them.
- The shadow at the walkers' length (62% of the buildings'), alpha 191 (the mod ships about 150; at least 128).
- The legs carry the body's shadow where the body hangs over them (TS's renderer casts no shadows on the unit).


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are (TS's voxel
and HVA, the mod's frames, the harvester, EA's Mammoth and the Titan's frames for the previews).
  rc.py, rcrender.py      a ray caster for models made of convex parts, with the buildings' look
  rcexport.py             convex parts to meshes (exact), for the .glb
  hmec2.py                the model's parts per TS section (the voxel as the blueprint), posed by TS's HVA
  hmec2mat.py             materials;  hmec2cam.py  canvas, camera, frame layout
  hmec2render.py          one frame;  hmec2final.py  all 256
  hmec2export.py          the .glb;  glbcheck.py  draws the .glb through its camera to check it
  hmec2check.py           checks the finished frames (sizes, trims, house green, shadow, against the mod's)
  hmec2previews.py, hmec2shape.py, cmpsheet.py   the previews, the shape check, TS | v1 | v3 sheets
  hface.py, hcomp.py, hdumpcls.py, hposed.py, hview.py   reading TS's voxel (faces, colour parts, slices, posed views)
    PKG=out python3 hmec2final.py 0 1      renders frames/
    python3 hmec2export.py tshmec.glb
