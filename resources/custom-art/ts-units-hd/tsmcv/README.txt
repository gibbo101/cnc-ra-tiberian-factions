MCV (TS [MCV]) in HD for Tiberian Factions: TSMCV  -  v4
=========================================================

frames/     tsmcv-0000.png ... tsmcv-0031.png, the mod's 32 frames on its 384 x 384 canvas, each with a -trim.png
            (white = house colour, antialiased).  Facings counter-clockwise from north: 0 N, 8 W, 16 S, 24 E.
previews/   8-facings.png        the mod's current frames (TS's voxel as the mod draws it now) beside HD, every
                                 4th facing
            32-facings.png       all 32 facings
            turn.gif             all 32 facings in turn, the mod's current frames beside HD
            scale.png            next to the HD harvester and EA's RA and TD MCVs, as the game draws them
            shape-8-facings.png  the model drawn flat (a colour per part) in the camera of the mod's voxel render,
                                 beside that render, with the silhouette overlap per facing
ts-mcv-hd-3d/   tsmcv.glb            the model (vertex colours) with the RA-grid camera
src/        the model, the renderer and the checks (see Rebuilding below)

v4 replaces v1-v3 throughout: same canvas, place, frame layout and shadow.  v2 rebuilt the model; v3 made the part
sticking out at the left front the cockpit, with a windscreen, and framed the grilles and vents; v4 (Luke) sets one
windscreen pane into the cabin - the cabin's own bodywork frames it - and lets the bonnet flow on from it to the nose.


What changed from v1
--------------------
v1 copied TS's voxel step by step, so it still read as voxels.  v2 on are built the way the Titan and the
Wolverine are: TS's voxel is the blueprint (where every part is and how big), and each part is modelled clean -
flat plates, true slopes, round wheels, bevelled edges - in one paint colour per part, TS's own.  The shapes and
details the voxel loses come from Westwood's own renders of the MCV (the GDI pair and the Nod concept Luke sent).

The MCV, part by part:
- Tracks: four pods.  Each track is a proper belt loop round a sprocket (back) and an idler (front), with three or
  four road wheels between, its links across the running faces; TS's tan bits on the track sides are the wheels'
  hubs.  Over it the house-colour cover: an inset panel on top with a bolt at each corner (as the renders' pods),
  the mudguard sloping down at the front, a small apron at the back, the outer skirt with TS's gaps, the inner skirt.
- Hull: the lower hull on a dark underside; steel bumpers front and back with vent teeth.
- Right deck: deck plates with seams and a tread; the outer rail and the inner wall; the rear block (TS paints its
  back third orange) with its house-colour panel on top, the olive hatch at its outer back corner, louvres on its
  outer side and the opening under its front; the house-colour panel block (cross seams) and strip held a voxel
  above the deck; the front block at the right front, at TS's size (its top at 10, TS's step to 9 and the nose
  to 7, each edge bevelled): a louvred vent in an orange frame across the step, where TS alternates orange and
  ochre, TS's orange band under it, the nose's louvred grille in an orange frame between TS's two orange bands, an
  orange roof panel and the hatch at its edge, a door on its outer side, foot steps.
- Spine (TS's light grey "boom"): the cap, the grey housing with a dark hatch on top, two white ribs, the long
  section (grey, then white) in segments, a collar with a slot through its top, the narrower front section with a
  grey band and a dark tip, the pulley block under it; it sits on the pedestal (tapered at its foot) and saddle, its
  front over the ramp - TS's dark cradle, drawn as one louvred slope.
- Crate rack (left deck): five crates on the rack's frame, each with an orange lid (an inset, handles), dark
  dividers between them, lamps where TS has its bright yellow and white voxels; the short rail pieces along the
  deck's outer edge.
- The cockpit at the left front (TS's block there and the part sticking out ahead of it; TS's dark voxels there
  are its glass): the body, the cabin on it with TS's orange roof and its two yellow lamps, one big sloping
  windscreen of dark glass set into the cabin's front - the cabin's pillars, header and sill frame it - and the
  bonnet flowing on from the windscreen's sill, sloping gently to a bevelled edge, the nose's front (TS's orange
  chin) sticking out ahead of the hull with a louvred grille set into it (TS's orange and ochre alternating there).

The model's silhouette overlaps the mod's voxel render by 0.91 drawn flat in that render's own camera
(shape-8-facings.png; v1 0.90).


Look
----
- Camera: a true orthographic view 32 degrees above the ground, looking north; 6.1 canvas px per voxel, the size the
  mod has now (8 canvas px per classic pixel).  The unit's position (the voxel's HVA origin, on the ground) at canvas
  (192, 194), where the mod's frames have it, so the ground line is in-mod/'s and meets the Construction Yard's.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides
  facing the camera as on the harvester, the Titan and the Wolverine; plate edges are bevelled in the shading.  The
  game draws this canvas at two thirds, so the outline, the shadow's blur and the contact shadow are 1.5 times as
  wide on the canvas (as the Titan's and the Wolverine's).
- Paint: TS's colours, one per part - ochre (TS 144-147) on the hull, decks, front block, cockpit and pedestal, a
  touch lighter than the walkers' as TS draws the MCV; orange (TS 184-185) on the rear block's back, the front
  block's roof and bands, the grille and vent frames, the crate lids, the cockpit's roof and chin; dark glass in
  the windscreen; the spine's grey housing, white top and light grey sides; dark steel on the tracks, bumpers and
  ramp; the buildings' grain, grime rising from the ground.
- House colour is pure green 0,214,0 x (1 + 1.1 grain) on the four track covers and the three deck panels (TS's
  remap voxels), detail only as thin seams and bolts; the -trim masks cover exactly those parts.


Shadow
------
Every frame carries the unit's shadow, black at alpha 191 (75%), blurred, falling to the right and a little towards
the camera, as long as the buildings' and the harvester's (the MCV is low).  Within 14 px of the canvas edge it
fades out.


3D model (ts-mcv-hd-3d/tsmcv.glb)
---------------------------------
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.
- Nodes: MCV > unit_facing_east (the mod's frame 24) > tracks, hull, right_deck, front_block, spine, crate_rack,
  cockpit, each holding its parts.  The meshes are exact (each part cut from its own planes and curved surfaces).
- Camera "camera_ra_grid": orthographic, 32 degrees above the ground, looking north; it frames the 384 canvas
  exactly (checked by drawing the mesh through it over frame 24: overlap 0.991).
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).
- Khronos's glTF validator: errors 0, warnings 0, infos 0, hints 0.


Judgement calls (each one easy to change)
-----------------------------------------
- One paint colour per part (TS's), rather than TS's voxel-by-voxel speckle (v1): where TS paints a part two
  colours (the rear block's orange back, the front block's orange band and the nose's bands, the vent's alternating
  orange, the chin's grille), so does v4.
- The cockpit (Luke: it's the part sticking out at the left front, as in the renders): TS's dark voxels there
  drawn as one windscreen pane set into the cabin, sloping from its roof down to the bonnet, which flows on to the
  nose (Luke: one pane, no bars, and sitting in the nose rather than on it); the cabin and nose a touch fuller
  than TS's blocky steps.  The grilles and the vent are set in orange frames.
- The front block's front: TS's alternating orange and ochre as a framed louvred vent (not glass); TS's dark
  cradle as a louvred ramp (the renders' louvred ramp at the front).
- The road wheels: TS's tan bits on the track sides read as wheel hubs; three or four road wheels per track.
- Left out because TS doesn't have them (the renders do): lamps on the pods' fronts and backs, side windows in the
  cockpit, hazard stripes.  Say if you want any.
- The deck panels: house colour with seams only; TS's stripes on the middle panel come from its remap shades.
- The shadow at the buildings' length (the MCV is low).


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are (TS's voxel
and palette, the mod's frames, the harvester and EA's MCVs for the previews).
  rc.py, rcrender.py      a ray caster for models made of convex parts, with the buildings' look
  rcexport.py             convex parts to meshes (exact), for the .glb
  mcv2.py                 the model's parts (the voxel as the blueprint);  mcv2mat.py  materials
  mcv2cam.py              canvas, camera, facings;  mcv2render.py  one frame;  mcv2final.py  all 32
  mcv2export.py           the .glb;  glbcheck.py  draws the .glb through its camera to check it
  mcv2check.py            checks the finished frames (sizes, trims, house green, shadow, against the mod's)
  mcv2previews.py, mcv2shape.py, cmpsheet.py   the previews, the shape check, TS | v1 | v4 sheets
    PKG=out python3 mcv2final.py 0 1      renders frames/
    python3 mcv2export.py tsmcv.glb
