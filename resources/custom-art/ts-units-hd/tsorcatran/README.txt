Orca Transport (TS [ORCATRAN]) in HD for Tiberian Factions: TSORCATRAN  -  v2.1
===============================================================================

frames/     tsorcatran-0000.png ... tsorcatran-0031.png, 32 frames on v1's 496 x 496 canvas, each with a -trim.png
            (white = house colour, antialiased), no shadow; 32 facings counter-clockwise from north (0 N, 8 W, 16 S,
            24 E)
previews/   8-facings.png            TS's voxel drawn in the mod's camera beside HD, every 4th facing (the mod has no
                                     frames of the Orca Transport yet)
            turn.gif                 all 32 facings in turn, TS's voxel beside HD
            scale.png                next to the HD harvester, the HD Orca Fighter, the HD Carryall and EA's RA
                                     Chinook, as the game draws them
            shape-8-facings.png      the model drawn flat (a colour per part) in the mod's camera beside TS's voxel,
                                     every 4th facing, with the silhouette overlap
            back-vents.png           the back's vents: TS's voxel beside HD at 3x, facings 0, 4 and 28
            closeups.png             the back and the middle at 3x
            front-closeup.png        the intake block, the nose and the front fans at 3x in four facings
ts-orcatran-hd-3d/  the 3D model, in its own zip (ts-orcatran-hd-3d.zip) next to this folder:
            tsorcatran.glb  the aircraft (vertex colours), with the mod's camera and a door marker
src/        the model, the renderer and the checks (see Rebuilding below)

v2.1 replaces v2: the back's three vents redrawn as TS's triangles (v2 had them as squares) and made the engines'
exhausts (Luke's notes on v2).  v2 replaced v1, keeping v1's canvas, scale, place, facings and frame layout with a new
model and paint.


What changed from v1
--------------------
v1 (from the Nod units chat) was a box model in three house-shaped lengths, with grey wheel-like fans, a black canopy
and its own colours x 1.25.  v2.1 is built the way the Titan, the Wolverine, the Orcas and the Carryall are: TS's
voxel (ORCATRAN.VXL) is the blueprint - where every part is and how big - and each part is modelled clean (flat
plates, true slopes, round fans, bevelled edges) in TS's own colours, with panel joints and bolts.  The voxel is the
source of truth: every part, step and colour below was read from it slice by slice, and each section's outline is the
line through the middle of TS's voxel steps.  The references Luke sent (a still from TS's FMV and two mod renders) are
the guide to how TS's parts read in HD where TS's voxel has the part: the nose's panes as framed glass, the fans as
drums with a recessed fan.  House colour stays where TS paints it.

The Orca Transport, part by part (TS's layout; q = TS's voxel coordinates, x back to front 0..70, y right to left
0..39, z up 0..14; the model is symmetric about y 19.0, w the distance out from it):
- The rear block (x 0..10): 30 wide (w 15 either side) up to z 8.5, its shoulders sloping in to the roof (w 10 at
  z 11); between the rear fans (x 10..19.6) 22 wide.  Its back is one slope through TS's steps (x 0.8 at z 5 to 4.6 at
  z 11) over a khaki bumper (x 0..1.3, z 3..5); in the slope, under its khaki band along the slope's top (z 9..11),
  TS's three black vents as the engines' exhausts, in TS's shapes: a triangle either side (its upright edge outboard
  at w 8.5, its top along the band, its slant from w 2.5 at the band down and out to w 7.2 at z 5.1) and one pointing
  up between them (w 4.4 either side at z 5.1, its tip at z 8.95), TS's ochre struts between them in an inverted V.
  Each exhaust is TS's black with dark vanes across it, a heat-darkened lip, and soot fading out round it over the
  struts and down onto the bumper (where TS has dark browns); the slope's outer ends in TS's browns.  Its sides are ochre with TS's darker, browner lowest rows; TS's amber marks on its shoulders
  (x 7.5, z 9.5) as small lamps.
- The raised roof panel on it (x 4.5..19, z 11..13): 16 wide behind x 10, 14 wide ahead, its back sloping as the back
  does, TS's darker bevels; a hatch in its top.
- The wing through the hull just ahead of the rear block (x 18..23.6): flat underneath at z 3 across the whole width
  (w 19 either side), its tips upright to z 4.75, its tops curving up to the deck (TS: w 18 at z 5.5, 17 at 6.5, 16 at
  7.5, 15 at 8.5, 13 at 9.5, 11 at 10.5).  House colour from x 19 on its tops, tips and underneath (TS's belly band);
  its back edge ochre and brown; TS's dark olive leg mounts in its tips (z 4..5).
- The hull (x 19.6..43): 24 wide to z 8.3, its shoulders in to the deck (w 10, z 9.3..11) in TS's dark khaki; a
  strake along each side (x 23.4..28.6 out to w 14 at z 5..7, then on to x 36 out to w 13); its sides' lowest row
  house colour from x 28, where TS's house-colour belly strips run underneath (x 28..44, w 8..12, z 2..3); TS's amber
  marks on its flanks (x 36..39, z 8..9) as small lamps.
- On the deck: TS's grey hatch (x 19..29, w 5.5 either side) in a dark grey frame; the hump (x 29..44, w 7.2 at z 11
  to 3.6 at its top, z 14), its front sloping down (x 40 at z 14 to 44 at z 12) in TS's dark grey; TS's dark grey rails
  along the deck's edges (w 8.1..9.95), between the rear fans (x 10..18) and along the hull (x 22..43), and on along the
  front section's shoulders to the face plate (w 8.9..10.1).
- The intake block on the front section's deck (x 41..53, w 6 either side, z 11..12), notched at its front (x 50..53,
  w 3): TS's two black slots (w 1..3.6 either side) run down the hump's dark front and along its top to x 48.5, a grey
  bar between them and grey strips beside them; the rest of it TS's dark grey.
- The front section (x 42.8..54): 26 wide at z 4.6..7.5, sloping in to its deck (w 6.5 at z 11); house colour on its
  flanks, underneath and round its front, its deck ochre; TS's dark olive front-leg mounts low on its sides
  (x 50..54, z 3..5).  The dark grey face plate in front of it (x 54..55, w 11, z 5..11), with TS's grey frame posts
  (x 55..56, w 8..10.8) and the struts out to the front fans (x 55..59.8, w 3.6..6.4, z 5..10).
- The nose (x 54..70): an octagon (w 2.5 at z 3, 5.5 at z 5.3..6.8, 2.6 at its top, z 11), its front a slope from z 11
  at x 65.4 to 7.6 at x 70, its chin rising to z 5.2 at x 69.4; house colour, with TS's two lavender panes across the
  front slope (x 65.6..66.5 and 67..69) as blue-grey glass, each with a thin bar down its middle, green bars round them.
- Four lift fans: at the back (centres x 14, w 14.65 either side) set into the rear block's notches, at the front (x
  60.5, w 9.65) beside the nose.  Each a khaki drum as TS's: a cup narrower at its bottom (r 3.5 at z 5, flaring to
  4.7..4.8 by z 9) with TS's dark olive foot, a band of bolts under a dark olive-brown lip on top (r 3.3 to the drum's
  edge, z 9.6..11); inside, a recessed fan a voxel below the lip (TS's light khaki-grey disc as nine light khaki-grey
  blades over a dark floor) round a grey hub with a dark centre (TS's).
- Six landing legs, where TS has them (feet at x 5..11 w 12.25, x 18..24 w 16, x 49..55 w 9.75): a dark olive foot pad,
  a strut and a drag rod, a knuckle up to the body.
- TS's ochre door box under the right side between the rear fans (x 9..20, y 8..12, z 2..3), with TS's amber strip
  (x 12..16).

The model's silhouette overlaps TS's voxel by 0.97 drawn flat in the mod's camera (shape-8-facings.png), and
by 0.98 drawn flat from the same camera with TS's voxels as cubes (facing 24); the finished frames overlap TS's
voxel drawn in the mod's camera by 0.960 (src/vcheck.py).


Look
----
- Camera: v1's: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 6.25 canvas px per voxel
  (the Orca Fighter's), the unit's position (TS's HVA origin) at canvas (248.0, 247.04) on the 496 canvas (grown from
  384 so every facing fits).
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides facing
  the camera as on the other units; plate edges are bevelled in the shading, the fans' drums and lips shaded round.
  The key light's shadow is tested a little off each face (further off faces the light only grazes) and the sky's
  occlusion weighted by how squarely each direction meets the face, so no face carries stripes from the light maps
  (as the Carryall's).  The game draws this canvas at two thirds (8 canvas px per classic pixel), so the outline is
  1.5 times as wide on the canvas.
- Paint: TS's colours - GDI's ochre (TS 144-147, the Dropship's, the Orcas' and the Carryall's) on the body, TS's
  darker ochre and browns (148-163) on the bevels, the lowest rows and the back slope's outer ends, TS's light khaki
  (129-131) on the bumper and the back slope's band, TS's dark khaki (138-139) on the hull's shoulders, TS's khaki
  (135-136) drums with dark olive feet (77-79) and dark olive-brown lips (118-120), light khaki-grey blades (69-71),
  grey hubs, hatch and struts (44-51), dark grey rails, face plate and intake block (53-56), black exhausts and slots
  (57-62) with soot round the exhausts, TS's lavender panes (90) as blue-grey glass, TS's amber (183-184) on the lamps,
  dark olive legs (78).
- House colour is pure green 0,214,0 x (1 + 1.1 grain) where TS paints house colour - the wing's tops, tips and
  underneath, the front section's flanks, front and underneath, the nose, the belly strips and the hull's lowest row
  beside them - with thin joints as detail; the -trim masks cover exactly the green.
- It flies: no grime from the ground, no ground occlusion.


Shadow
------
None baked: in flight the game lifts the frame by the aircraft's height and draws its shadow from the same frame,
darkened, on the ground.  The outline is the units' dark outline, so the silhouette reads as a shadow too.


3D model (ts-orcatran-hd-3d/tsorcatran.glb)
-------------------------------------------
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position (TS's HVA origin), as the frames draw it.  The aircraft faces east (the mod's facing
  24); in flight the game lifts it.
- Nodes: OrcaTransport > unit_facing_east > hull (its parts: rear_block, rear_core, bumper, roof_panel, wing, hull,
  hull_deck, strake, hatch, hump, rail, front, cockpit (the intake block), face_plate, nose, fan_drum, fan_lip,
  fan_floor, fan_hub, fan_spinner, fan_blade, fan_strut, face_post, face_bar, leg_foot, leg_strut, leg_rod,
  leg_knuckle, leg_mount, belly_strip, door...).  The meshes are exact (each part cut from its own planes and curved
  surfaces).  The empty node "door" marks the middle of TS's belly door (under the right side between the rear fans),
  in case unloading wants a point (v1's marker was at the nose).
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 496 canvas exactly
  (checked by drawing the mesh through it over frame 24: overlap 0.991).
- Vertex colours: COLOR_0 albedo (no light or shadow; the paint's areas - its joints and bolts are finer than the
  mesh), COLOR_1 house colour (white = house colour).
- Khronos's glTF validator: errors 0, warnings 0, infos 1, hints 0 (the info is the empty marker node).


Judgement calls (each one easy to change)
-----------------------------------------
- One paint colour per area (TS's), rather than TS's voxel-by-voxel speckle.
- Symmetric about y 19.0 where TS is a voxel off: TS's nose is a voxel wider on its left at mid-height, its left wing
  tip a voxel shorter, its hatch's two halves a voxel apart, its left strake runs on along the hull at z 6 to x 52.
- TS's black slots behind the nose read as two intake slots, not windows: the FMV's crew sit in the glazed nose (v1
  made them a black canopy).
- The nose's panes: TS's two lavender bands as blue-grey glass, each with a thin bar down its middle (the FMV's glazing
  is framed; TS's bands are plain).
- The rails along the front section's shoulders on both sides: TS has the raised rail on its left side only (its right
  has a dark strip by the intake block instead).
- The fans: TS's lip ring (r 2.8..4.8) opened to r 3.3 so the blades read; TS's light khaki-grey disc as blades
  over a dark floor.
- The back's vents as the engines' exhausts (Luke): TS's black openings with dark vanes across them, heat-darkened
  lips and soot round them (TS paints dark browns round them).
- TS's amber marks kept as small amber lamps where TS has them in pairs (the rear block's shoulders, the hull's flanks)
  and as the strip on the belly door; TS's other amber voxels, scattered under the belly, left out as speckle.
- TS's door box under the belly kept on the right side only, as TS has it.
- TS's small holes at the wing's roots (one to three voxels down to the belly at x 20..21) left out.
- The legs: TS's blocky legs as a foot pad, a strut, a drag rod and a knuckle, at TS's places and sizes.
- Left out (not in TS's voxel): the FMV's light rail under the nose, and the references' eagles and lettering.


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are (TS_HANDOFF;
OT_D for ORCATRAN.VXL, from the Orca Transport's handover).
  otmodel.py             the model: every part, in TS's voxel section's own frame, posed by its HVA
  otmat.py               the paint and the detail (joints, bolts, vents, slots, lamps, the panes' glass), per pixel
                         from each hit's q
  otcam.py               the canvas, the camera and the facings
  otrender.py            one frame:  python3 otrender.py 0,12,24 [ss] [outdir]  (a 5th argument 1 paints TS's own
                         voxel colours onto the model instead, to check where the paint goes: otproj.py)
  otspec.py              the frames, previews and checks for vdeliver.py
  otexport.py            the .glb;  glbcheck.py  draws the .glb through its camera to check it
  otshape.py             the shape sheet;  otcomp.py  TS's voxels against the model drawn flat, from any facing;
                         otqdiff.py  the same in TS's own axes;  otclose.py  close-ups of any frame at any scale;
                         otvents.py  TS's back vents beside HD's
  otvoxd.py, otvox.py, otdump.py, hcls.py   TS's voxel as data, drawn, sliced as text, and its palette classes
  ref/                   TS's voxel drawn in the mod's camera, every facing (v1's drawing, from its tsvox.py): the
                         previews' left column and the checks' reference
  otpkg.py, ottab.py     the package (checks, previews, README, 3D model, zips) and the review page's tab
  rc.py, rcrender.py, qparts.py, rcexport.py, glbtools.py, frameio.py   the ray caster, the buildings' look for
                         models made of convex parts, the .glb writer
  vdeliver.py, vcheck.py    renders, previews and checks a unit from its spec
    PKG=out python3 vdeliver.py otspec render 0 1      renders frames/
