Mobile War Factory (Firestorm [MOBWARG]) in HD for Tiberian Factions: TSMWAR  -  v4
===================================================================================

frames/     tsmwar-0000.png ... tsmwar-0031.png, the mod's 32 frames on its 384 x 384 canvas, each with a -trim.png
            (white = house colour, antialiased), with the unit's shadow; 32 facings counter-clockwise from north
            (0 N, 8 W, 16 S, 24 E)
previews/   8-facings.png            the mod's frames beside HD, every 4th facing
            turn.gif                 all 32 facings in turn, the mod's frames beside HD
            scale.png                next to the HD harvester and EA's MCV, as the game draws them
            shape-8-facings.png      the model drawn flat (a colour per part) in the mod's camera beside the mod's
                                     frames, with the silhouette overlap per frame
ts-mwar-hd-3d/   the 3D model, in its own zip (ts-mwar-hd-3d.zip) next to this folder:
            tsmwar.glb   the model (vertex colours), with the mod's camera
src/        the model, the renderer and the checks (see Rebuilding below)

v4 replaces v3 (and v2, v1): same canvas, place, size, ground line and shadow; frame 12 (facing south-west) where
the mod has it, so it still meets the deployed War Factory's build-up frame 0.


What changed from v3
--------------------
Luke: where's the front window?  Use the MCV as a guide (v3's stepped grey nose read as steps).  So in v4 TS's
nose, sloping down from under the canopy's front edge to the bumper (TS: its top 13 at x 36, 9 at x 43), is the cab's
front, as the MCV's cockpit is:
- the windscreen raked down its upper slope from under the canopy's front edge (q x 35.6, z 14.5 down to x 40.6,
  z 10.9), dark glass in two panes, framed by the cab's bodywork - a pillar each side and one in the middle, the sill
  along its foot - the glass a little below that frame;
- the bonnet below it sloping gently down to a bevelled front edge (TS's lower steps), a joint down its middle;
- the grille in the bonnet's front face, dark behind its slats, framed, over the chrome bumper;
- gone: the slats down the slope, and v3's glass in the slot under the canopy (the windscreen fills that slot now).
Everything else as v3: the side windows high in the cab's walls, the doors, the roof hatch and the rest of v3's
detail; TS's shape and paint.


What changed from v2 (in v3)
----------------------------
Luke: more detail, to the Titan's and the Wolverine's standard, and a window in the cab as the other units have.  So
in v4 (the shape and TS's paint are v2's; each detail is listed under Judgement calls):
- the cab's windows: a windscreen in TS's slot under the canopy's front edge (v4 moved it down the nose's slope,
  above) and a side window high in each of the cab's walls, ahead of its door.  Dark glass as the MCV's, the sky's
  reflection lighter towards the top, a soft sheen;
- the cab's doors (a joint round each, two hinges, a handle) and a hatch in its roof ahead of the crane's support;
- a louvred vent in each house-colour block's sides, framed, and the blocks' joints (down their tops, across their
  sides at z 8 and 16);
- the black bar behind the middle section's top: louvres across its top, slats down its sides (TS's alternating
  near-black and dark grey there);
- rivets along the middle section's joints, bolts along its black rails;
- the rear hatch's joints (round its back and at TS's steps) and its handle;
- a louvred vent in the nose's right side (TS's light voxels there) and a joint along the nose's sides;
- the crane: a round pivot in each blue-grey clamp, bolts along the side plates' feet and on the support;
- the wheels' hubs: a rim, six wheel nuts round a cap; the olive boxes: their lids, two straps and a handle each.


What changed from v1
--------------------
v1 copied TS's voxel box by box, so it still read as voxels.  v2 (and v4) is built the way the Titan, the
Wolverine, the MCV, the Mammoths, the APC and the sensor array are: TS's voxel (MWAR_NOD.VXL) is the blueprint (where
every part is and how big), and each part is modelled clean - flat plates, true slopes, round wheels, bevelled edges -
in TS's own colours.  The voxel is the source of truth: every part, step and colour below was read from it slice by
slice.  Westwood's Firestorm cameo of the War Factory (Luke sent it) is the guide to how TS's parts read in HD: the
boom on top as a round tube, the fenders curved and chrome, the slatted grille in the nose's front; and from it the
one part TS doesn't have, a chrome bumper across the nose's foot (see Judgement calls).  Its khaki paint is left out
(Luke: stay grey, as TS's voxel).

The Mobile War Factory, part by part (TS's layout, back to front; q = TS's voxel coordinates, x back to front,
y right to left, z up):
- Six wheels a side (TS's): two pairs outboard under the back half (TS: x 3..12 and 18..27), each pair under a curved
  chrome fender (TS's grey fenders, z 5..6, their ends stepping down), and a pair inboard under the nose (TS: y 7..10
  and 15..18); treaded tyres with dark grey hubs; TS's dark grey chassis between them and a black bumper across the
  back; TS's olive boxes on the sides before the front wheels (TS: x 28..33, z 2..6).
- The rear frame: TS's two grey corner blocks with their black slots, the black rail across them (TS: z 9..11) and
  above it TS's dark grey hatch (TS 52, z 14..19), its back top edge stepped down (TS's).
- TS's two house-colour blocks the full width and height (TS: x 4..10 and 19..25, z 4..19), a seam where TS's remap
  shades change.
- The middle section between them: grey sides with TS's two black rails along each side (z 6..8 and 9..11, a voxel
  proud), panel joints; its top a house-colour box (TS: up to z 18) with TS's grey panels low on its sides, and
  behind it TS's black bar across, as high as the blocks (TS: x 10..14, black 63, up to z 19).
- The front tower, the cab's back (TS: x 24..33): TS's grey side walls, cut away diagonally at the front, over a
  house-colour core whose sides are cut away again two voxels further on (TS's green band between the two cuts), on
  a grey floor (TS: z 5); a grey face high on its front (TS: z 10..14); the house-colour roof in plates running
  forward over the nose's back as a canopy, its sides hanging down to the nose, their lower edges carrying on the
  core's cut (TS's).  A side window high in each wall, a door under it; a hatch in the roof.
- The nose, the cab's front (TS: x 33..44, y 7..16): TS's grey nose sloping down from under the canopy's front edge
  (TS: its front at x 43, stepping back a voxel every voxel up from z 9), as the MCV's cockpit (Luke): the windscreen
  raked down its upper slope in the cab's frame (pillars each side and in the middle, the sill), the bonnet below it,
  the grille in its front face (the cameo's slatted front) over the cameo's chrome bumper; the keel under it, its
  narrower back reaching in under the tower's front (TS: x 31..33, y 9..15); TS's olive box stepped down its left
  side.
- The crane folded on top (TS's): its pedestal at the back (TS: x 13..17, z 16..20); its two dark grey side plates
  rising to TS's height (z 24) with TS's blue-grey clamps at their tops (TS: x 15..17, z 21..23), a pivot in each;
  the boom lying
  between them as a banded tube (the cameo's), its back end dark grey, falling as TS's does from z 24 at the back
  down onto the roof; its front support on the roof (TS: x 25..30).

The model's silhouette overlaps the mod's frames by 0.96 drawn flat in the mod's camera
(shape-8-facings.png); the finished frames by 0.951 (src/vcheck.py).


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.26 canvas px per voxel,
  the unit's position (TS's HVA origin) at canvas (191.65, 190.24), as v1 and the mod's frames have it.  TS's hull
  sits 1.04 voxels above its HVA origin, so the model is lowered onto the ground and the camera raised to match:
  every pixel stays where the mod's frames have it, and the shadow meets the wheels.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides
  facing the camera as on the other units; plate edges are bevelled in the shading.  The game draws this canvas at
  two thirds (8 canvas px per classic pixel), so the outline, the shadow's blur and the contact shadow are 1.5 times
  as wide on the canvas.
- Paint: TS's colours, one per part - TS's grey (TS 47-49) on the body, the tower's walls and the nose; dark grey
  chassis, crane and rear hatch (TS 52-56); black tyres, rails, the bar behind the middle top and openings (TS
  59-63); olive boxes (TS 73-76, 117-121); blue-grey clamps (TS 90-92); the cab's glass dark, as the MCV's.  The
  fenders and bumper chrome and the boom light grey, as the cameo has them (TS's fenders grey 51-52, its boom dark
  grey 53).  Grime rises from the ground on the running gear.
- House colour is pure green 0,214,0 x (1 + 1.1 grain) on TS's house-colour parts (the two blocks, the middle
  section's top, the tower's core and roof), detail only as thin seams; the -trim masks cover exactly those.


Shadow
------
Every frame carries the unit's shadow, black at alpha 191 (75%), blurred, falling to the right and a little towards
the camera, as long as the buildings' and the harvester's (v1's).  Within 14 px of the canvas edge it fades out.


3D model (ts-mwar-hd-3d/tsmwar.glb)
-----------------------------------
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.  The unit faces east (the mod's facing 24).
- Nodes: MobileWarFactory > unit_facing_east > body, holding its parts (green_block, middle, middle_top,
  middle_bar, rear_hatch, tower_core, tower_wall, roof, roof_hatch, cab, bonnet, windscreen, ws_pillar, ws_sill,
  side_window, tube, crane_bracket, pivot, fender, tyre, hub, olive_box, ...).  The glass is its own parts
  (windscreen, side_window).
  The meshes are exact (each part cut from its own planes and curved surfaces).
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 384 canvas exactly
  (checked by drawing the mesh through it over frame 24: overlap 0.990).
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).
- Khronos's glTF validator: errors 0, warnings 0, infos 0, hints 0.


Judgement calls (each one easy to change)
-----------------------------------------
- One paint colour per part (TS's), rather than TS's voxel-by-voxel speckle (v1).
- Grey, as TS's voxel, not the cameo's khaki (Luke's call).
- The cameo where TS's voxel has the part: the boom as a round tube with bands (TS: a dark grey box beam, 6 voxels
  wide and 3 to 4 high), light grey toward the cameo's white; the fenders curved and chrome (TS: stepped, grey
  51-52); the slatted grille in the nose's front face.
- The chrome bumper across the nose's foot is the cameo's only: TS has no bumper there (its nose's foot is set back
  a voxel).  It is one part (bumper in mwarmodel.py), easy to take off.
- The cab's windows (Luke: the front window as the MCV's).  TS paints the cab grey all over: the windscreen is on
  the upper half of TS's nose slope, raked a little steeper than TS's steps (35 degrees against TS's 27, so it fills
  TS's slot under the canopy's edge); the bonnet keeps TS's lower steps.  The side windows are new, high in the
  walls ahead of the doors (side_window in mwarmodel.py, one part each, easy to take off).
- The detail (Luke: the Titan's and the Wolverine's standard) is surface only - joints, louvres, rivets, bolts,
  hinges, handles, straps, the roof hatch and the pivots - placed where TS's voxel has the part and, where TS marks
  something (the bar's slats, the nose's light voxels, the hatch's steps), where TS marks it; TS's paint is kept (the
  louvres on the house-colour blocks are thin ribs only).
- Round wheels with dark grey hubs (TS's wheels are black all over): they touch the ground where TS's do, but TS's
  square wheels' near corners reach lower on the canvas, so the frames' lowest pixel sits 1 to 6 px (4.5 on average)
  above the mod's (src/vcheck.py).
- The shadow as v1's: the buildings' length, alpha 191 (the mod ships about 150; at least 128).


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are (TS's voxel,
the mod's frames, the harvester and EA's MCV for the previews).
  rc.py, rcrender.py      a ray caster for models made of convex parts, with the buildings' look
  rcexport.py             convex parts to meshes (exact), for the .glb;  glbtools.py  the .glb writer
  qparts.py               parts built in a voxel section's own frame
  mwarmodel.py            the model's parts (the voxel as the blueprint), posed by TS's HVA
  mwarmat.py              materials;  mwarcam.py  canvas, camera, frame layout
  mwarrender.py           one frame;  mwarspec.py  the frames, previews and checks for vdeliver.py
  mwarexport.py           the .glb;  glbcheck.py  draws the .glb through its camera to check it
  vdeliver.py, vcheck.py  renders, previews and checks a unit from its spec
  mwarshape.py            the shape check;  vcomp.py  the model against TS's voxel drawn flat
  vpaint.py               the paint check: TS's colours against the model's, pixel by pixel;  vaudit.py  per part
  mvox.py, mwarlook.py, hcls.py   TS's voxel as cubes and as text, sheets
  mwarpkg.py              builds this package
    PKG=out python3 vdeliver.py mwarspec render 0 1      renders frames/
    python3 mwarexport.py tsmwar.glb
