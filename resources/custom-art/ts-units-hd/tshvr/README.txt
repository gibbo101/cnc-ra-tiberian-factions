Hover MLRS (TS [HVR]) in HD for Tiberian Factions: TSHVR  -  v2
===============================================================

frames/     tshvr-0000.png ... tshvr-0095.png, the mod's 96 frames on its 192 x 192 canvas (4 canvas px per classic
            pixel, half the other units' density, as the mod has it), each with a -trim.png (white = house colour,
            antialiased):
              0-31    the hull, no shadow, 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E); it now
                      carries the pad the rack turns on (see The rack's seat below)
              32-63   the missile rack (its support and the two pods), no shadow, 32 facings, each turning about the
                      rack's pivot, which stands on the unit's position on the canvas (95.5, 106): the game seats it
                      on the pad's centre (see The rack's seat below - this replaces the seat tables)
              64-95   the hull's shadow on its own, drawn first under the hull: the HD hull's silhouette, offset as
                      now (5 px right, 17 px down: it hovers), black at alpha 191, softened
previews/   8-facings.png            the assembled unit: the mod's frames as they lie on their canvas (its seat
                                     tables not applied) beside HD with the rack seated on the pad
            hull-8-facings.png, rack-8-facings.png, shadow-8-facings.png   each set on its own, every 4th facing
            turn.gif                 all 32 facings in turn, the mod's frames beside HD (seated)
            rack-turn.gif            the hull still (facing 28), the rack turning through its 32 facings on the pad
            pad-closeup.png          hull and rack together at 5x in four facings: the pad between the pontoons
            rack-closeup.png         the rack at 5x in four facings: the pods' faces, the red-tipped missiles
            shape-8-facings.png      TS's voxels against the model, both drawn flat in the mod's camera (red: TS's
                                     only, blue: the model's only), the hull's and the rack's every 8th facing
            scale.png                next to the HD harvester, as the game draws them
ts-hvr-hd-3d/   the 3D model, in its own zip (ts-hvr-hd-3d.zip) next to this folder:
            tshvr.glb    the hull and the rack (vertex colours), the rack under its own node on the pad, with the
                         mod's camera
src/        the model, the renderer and the checks (see Rebuilding below)

v2 replaces v1: same canvas, size, hull origin, frame layout and shadow; the rack moves onto the hull's back
(Luke), so its seat changes (below).


What changed from v1
--------------------
v1 copied TS's voxels box by box, so it still read as voxels.  v2 is built the way the Titan, the Wolverine, the
Disruptor and the War Factory are: TS's voxels (HVR.VXL the hull, HVRTUR.VXL the rack) are the blueprint - where every
part is and how big - and each part is modelled clean (flat plates, true slopes, round tubes, bevelled edges) in TS's
own colours, with panel joints, hatches, louvres, grilles and bolts.  The voxels are the source of truth: every part,
step and colour below was read from them slice by slice.  Westwood's art of the Hover MLRS and the mods' renders Luke
sent are the guide to how TS's parts read in HD where TS's voxels have the part: the pods' missile tubes, the intakes in
the pontoons' fronts, the canopy's glass, the hover fans, the pad under the rack.  Where they show more than TS (the vents
on the humps), Luke asked for it.

Luke's notes on the way, all in v2:
- The red-tipped missiles (the references'): two rows of four in each pod's face.
- The rack on the back of the vehicle, almost touching its back end, centred across the hull, with no shadow between
  rack and hull.
- The pods lifted on a circular pad with a support holding them up, as the Disruptor's turret; the pad between the
  yellow sides, not over them.
- Pivot fixed: the rack's frames turn about its pivot; the game seats them (below).
- The vents: the intakes in the pontoons' fronts at the angle of the screenshots (each front face leaning back to the
  bottom, louvres across), and vents further back on the body, on the humps' fronts (Westwood's raised blocks and the
  mods' have them).
- The cockpit's window faces forward (TS's, Westwood's and the mods'), with no window behind the bar.
- Firing: the rack pivots, and only the pods move when it fires.  The pad is part of the hull's frames, so it never
  moves; the rack's frames hold only the support and the pods, so the game's recoil (it draws the turret frame a
  pixel back when the unit fires) moves the pods and their support and leaves the pad where it is.  TS has no
  firing animation of its own for the HVR, so v2 adds none.

The Hover MLRS, part by part (TS's layout; q = TS's voxel coordinates, x back to front, y right to left, z up):
- Two pontoons (TS: y 0..5 and 15..20, x 0..38) in GDI's ochre: their tops at z 7 over the back (x 0..25) with a
  raised hump (TS: x 13..25, z 8) carrying a louvred panel, stepping down to z 6 over the front; their bottoms at z 2,
  the back end rising (TS: z 3..4 at x 0..4).  TS's khaki end plates on their tops (back x 0..7, front x 31..38) and a
  khaki strip along the back half's inner edge (x 7..13); a hatch on each back plate; TS's brown band along their foot,
  joints along and down their sides, bolts along the band.
- A vent in each hump's front face (Luke; Westwood's raised blocks by the pods and the mods' have one): a dark slot in a
  raised frame, louvres across it.  TS's one-voxel ledge in front of the hump (x 25..27, z 7) comes down to the front
  deck's z 6, so the face is two voxels tall.
- Each pontoon's front end (TS: x 35..38) at the angle of Westwood's render and the mods' (Luke): its face leans back
  from the top's front edge (TS's x 38) to the bottom (TS: x 36 at z 2), with a big intake in it (TS's dark front and
  the opening under its lip) between two walls, framed above and below, three khaki louvres across it (the middle one
  at TS's khaki lip, z 4..5), dark inside.  TS's red-brown rubber skirt under the front (x 30..36, z 1..2), in
  sections; two black hover fans under each pontoon's outer half (TS: x 17..19 and 21..23), grilles down their sides.
- TS's light pink lamps: a lamp bar across each pontoon's back top edge, a lamp on top of each front end's outer
  corner.
- The body between the pontoons (TS: y 5..15): a blue-grey bar across its back (TS: x 1, z 5, bolted), the dark engine
  deck (TS: x 2..9, up to z 7) with a grille of slats in a frame, a slot across it (TS: x 9, down to z 4), the grey
  mid deck (TS: x 10..30, z 6) in plates with a hatch (TS's olive patch) and bolts, the front stepping down to z 5
  (TS: x 30..34) with louvres across its front, a blue-grey bar across the front (TS: x 34, z 4..5, bolted); TS's light
  grey plate beside the cockpit (TS: x 22..30, y 10..15) with a joint round it and a handle.
- The cockpit on the front right (TS: x 22..31, y 5..10): a house-colour frame, the canopy on it facing forward (TS:
  dark over its top, x 23..30, and down over its front edge; house colour at its back): dark glass from the bar
  forward with a steep windscreen, the sky's reflection lighter toward its top, a house-colour fairing behind the bar,
  the house-colour bar across it (TS: x 25..27, z 8).
- The pad (TS's ring - the five lowest layers of HVRTUR.VXL, a ring round the rack's pivot 6 voxels out and two
  high, sitting down in the hull - moved into the hull's frames): a light grey stepped circular pad on the back deck
  between the pontoons (Luke), its rim 4.45 voxels out (TS's 6 would lie over the pontoons), a step 4.0 out on top,
  bolts round the rim, a joint round its side; a base plate under its front half, flush with the engine deck.
- The rack (HVRTUR.VXL): two missile pods (TS: y 0..7 and 11..19, x 0..12, z 5..9) in house colour, TS's ochre band
  across their backs (x 0, z 7..9) and ochre collar round their fronts (x 10..11, bolted), access panels on their
  tops and outer sides; their dark faces (TS: x 11..12, z 6..9) with two rows of four missile tubes, each with a
  red-tipped missile in it; an antenna at each pod's back outer corner (TS: x 2..4, z 9..19) on a mount; the grey
  mount between the pods' feet (TS's dark block, x 3..7, y 7..12, z 5..6), bolted; under it the support (TS's two
  legs up from the ring under the pods' inner sides): a column under the mount and a leg under each pod's inner
  half, standing on the pad's step.

The model's silhouette overlaps TS's voxels by 0.95 (the hull) and 0.84 (the rack, its antennas
thinner than TS's one-voxel masts), drawn flat in the mod's camera (shape-8-facings.png); the finished hull frames
overlap the mod's by 0.92 (src/vcheck.py).  The rack's frames are drawn on the pivot now (below), so they no
longer lie where the mod's do.


The rack's seat
---------------
Luke: the rack sits on the back of the vehicle, almost touching its back end, centred across it - pivot fixed.  Every
rack frame (32 + g) is drawn turning about the rack's pivot (the support's and the pods' middle), which stands on the
unit's position on the canvas (95.5, 106).  The pad it turns on is drawn in the hull's frames, its centre 12.54
voxels aft of the unit's position along the hull's facing and 0.20 voxels to its left (TS's hull runs 0.2 voxels left
of its HVA origin; the rack is centred across the hull).  So the game draws rack frame 32 + g shifted by the hull's
facing f alone, whatever g is:

    dx = -2.95 (12.54 sin a + 0.20 cos a),   dy = 2.95 sin 32 (12.54 cos a - 0.20 sin a)   canvas px

for the hull's facing a measured clockwise from north (a = 360 x ((32 - f) mod 32) / 32 degrees): 37.0 canvas px aft
when the hull faces east or west, 19.6 px when it faces north or south.  In classic pixels (4 canvas px each) that is
9.2 and 4.9; in TS's terms about TurretOffset=-99 (TS's own -64 is 8.14 voxels), with the 0.2 voxels to the left on
top.  Per facing (canvas px, then classic px):

    facing  0   -0.60 +19.60  (-0.15, +4.90)      facing 16   +0.60 -19.60  (+0.15, -4.90)
    facing  1   +6.63 +19.28  (+1.66, +4.82)      facing 17   -6.63 -19.28  (-1.66, -4.82)
    facing  2  +13.60 +18.23  (+3.40, +4.56)      facing 18  -13.60 -18.23  (-3.40, -4.56)
    facing  3  +20.05 +16.47  (+5.01, +4.12)      facing 19  -20.05 -16.47  (-5.01, -4.12)
    facing  4  +25.73 +14.08  (+6.43, +3.52)      facing 20  -25.73 -14.08  (-6.43, -3.52)
    facing  5  +30.42 +11.15  (+7.60, +2.79)      facing 21  -30.42 -11.15  (-7.60, -2.79)
    facing  6  +33.94  +7.79  (+8.48, +1.95)      facing 22  -33.94  -7.79  (-8.48, -1.95)
    facing  7  +36.15  +4.13  (+9.04, +1.03)      facing 23  -36.15  -4.13  (-9.04, -1.03)
    facing  8  +36.98  +0.32  (+9.25, +0.08)      facing 24  -36.98  -0.32  (-9.25, -0.08)
    facing  9  +36.39  -3.51  (+9.10, -0.88)      facing 25  -36.39  +3.51  (-9.10, +0.88)
    facing 10  +34.40  -7.21  (+8.60, -1.80)      facing 26  -34.40  +7.21  (-8.60, +1.80)
    facing 11  +31.08 -10.62  (+7.77, -2.66)      facing 27  -31.08 +10.62  (-7.77, +2.66)
    facing 12  +26.57 -13.63  (+6.64, -3.41)      facing 28  -26.57 +13.63  (-6.64, +3.41)
    facing 13  +21.04 -16.12  (+5.26, -4.03)      facing 29  -21.04 +16.12  (-5.26, +4.03)
    facing 14  +14.71 -17.98  (+3.68, -4.50)      facing 30  -14.71 +17.98  (-3.68, +4.50)
    facing 15   +7.80 -19.16  (+1.95, -4.79)      facing 31   -7.80 +19.16  (-1.95, +4.79)

The rack's frames carry no offset of their own (the game turns the rack on its own), so these replace the seat
tables dialled for v1's frames; the previews draw the rack so.  A fire point measured from the turret's position
(TS's PrimaryFireFLH=64,32,128) moves aft with it.


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north; 2.95 canvas px per voxel, the
  hull's position (TS's HVA origin) at canvas (95.5, 106): the size and place v1 and the mod's frames have.  This
  canvas has half the other units' density, so the game draws it at 4/3: the outline is 0.75 canvas px wide here, so
  it comes out as wide in the game as on the other units.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides facing
  the camera as on the other units; plate edges are bevelled in the shading.  The rack's frames have no cast shadows
  and its support is lit as open to the sky (Luke: no shadow between the rack and the hull).
- Paint: TS's colours, one per part - GDI's ochre pontoons (TS 144-152) with TS's khaki end plates (TS 128-135), the
  red-brown skirts (TS 106-109), black fans and antennas (TS 59-61), the intakes and vents dark inside, the light pink
  lamps (TS 96), the grey
  deck (TS 44-56) with the dark engine deck (TS 52-58) and the light grey plate (TS 35-43), blue-grey bars (TS 92-95),
  the pods' ochre bands and collars, their dark faces (TS 57-60), the grey mount and support, the light grey pad.
  Grime rises from the ground on the pontoons' lower sides.
- House colour is pure green 0,214,0 x (1 + 1.1 grain) on TS's house-colour parts (the missile pods, the cockpit's
  frame and its bar), detail only as thin seams; the -trim masks cover exactly those.


Shadow
------
Frames 64-95 are the hull's shadow on its own, as the mod's: the HD hull's silhouette (with the pad), moved 5 px right
and 17 px down (it hovers), black at alpha 191 (75%), softened.  The hull's and the rack's frames have none.


3D model (ts-hvr-hd-3d/tshvr.glb)
---------------------------------
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (96 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.  The unit faces east (the mod's facing 24).
- Nodes: HoverMLRS > unit_facing_east > hull (its parts: pontoon, pontoon_hump, front_top, front_wall, intake_frame,
  intake, louvre, hump_vent, vent_frame, skirt, hover_fan, tail_lamp, head_lamp, rear_bar, engine_deck, slot,
  turret_base, mid_deck, front_deck, front_bar, front_plate, cockpit, canopy, canopy_fairing, canopy_bar, pad,
  pad_top) and rack, on the pad's centre (0.385 cell aft, 0.0062 cell left) and turning about its own local z axis > rack_body
  (pod, collar, face, tube, missile, antenna_mount, antenna, mount, column, leg).  The meshes are exact (each part
  cut from its own planes and curved surfaces).
- Camera "camera_mod": orthographic, 32 degrees above the ground, looking north; it frames the 192 canvas exactly
  (checked by drawing the mesh through it over hull frame 24 with rack frame 56 seated as above: overlap
  0.964).
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).
- Khronos's glTF validator: errors 0, warnings 0, infos 0, hints 0.


Judgement calls (each one easy to change)
-----------------------------------------
- One paint colour per part (TS's), rather than TS's voxel-by-voxel speckle (v1).
- The missiles' red tips (Luke; the references'): TS's faces are dark.
- The pad: TS's ring as a light grey pad (Westwood's white ring; TS's is near black, and Luke wants no dark band
  between rack and hull), 4.45 voxels out instead of TS's 6 so it sits between the pontoons (Luke), and drawn with the
  hull so it stays still when the pods move.  A base plate under its front half, flush with the engine deck (TS's
  slot and the mid deck's back edge are lower there).
- The rack 12.54 voxels aft (Luke: almost touching the back end), not TS's 8.14, and centred across the hull, 0.2
  voxels left of TS's place.  The pods centred on the rack's pivot (TS's are 0.25 voxels left of it), so the rack
  turns about its middle.
- The support: TS's two legs as a leg under each pod's inner half and a column under the mount, slimmed so they stay
  on the pad's step at every turn.
- The antennas as thin masts (TS: a one-voxel column each).
- The front ends after Westwood's render and the mods' (Luke: the vent angles): one face leaning back to the bottom
  with a louvred intake, rather than TS's stepped prow (forward-most at mid-height); TS's black strip on top of each
  front end is left off (the intake carries the dark).
- The vents on the humps' fronts (Luke; Westwood's and the mods' raised blocks; TS has none), with TS's ledge in front
  of each hump lowered to the front deck so the face is tall enough.  They sit mid-hull, as the humps do: the rack sits
  further back than in Westwood's render.
- The canopy's glass only from the bar forward (Luke: no window facing back); TS's dark top runs back behind the bar
  too (x 23..25), here house colour.
- The front lamps at both pontoons' outer front corners (TS has one at the right pontoon's inner corner and one at the
  left's outer corner).
- Westwood's eagle decal is left off (TS's voxels have none).


Rebuilding (src/)
-----------------
Python 3 with numpy, scipy and Pillow.  The renderer files from the buildings (hd.py, walls2.py, wnoise.py,
export3d.py) and the voxel reader (vxl.py) are included; paths.py says where the hand-off folders are.
  hvrmodel.py            the model: every part, in TS's voxel sections' own frames, posed by their HVAs; the rack's
                         place (RACK_SHIFT, RACK_AFT) and the pad
  hvrmat.py              the paint and the detail (joints, bolts, louvres, grilles, panels), per pixel from each hit's q
  hvrcam.py              the canvas, the camera and the frame layout
  hvrrender.py           one frame:  python3 hvrrender.py 0,24,56,88 [ss] [outdir];  renderall.py  all 96
  hvrseat.py             the rack's seat per facing:  python3 hvrseat.py
  hvrspec2.py            the frames, previews and checks for vdeliver.py
  hvrexport.py           the .glb;  glbcheck.py  draws the .glb through its camera to check it
  hvcomp.py              TS's voxels against the model, drawn flat (the shape sheet)
  hvrclose.py, hvrclose2.py   close-ups of any frame, or hull and rack together, at any scale
  hvrlook.py             the assembled unit against the mod's frames and v1
  hvrpkg.py, hvrtab.py   the package (checks, previews, README, 3D model, zips) and the review page's tab
  hvox.py, vdump.py, hcls.py   TS's voxels drawn, sliced as text, and their palette classes
  rc.py, rcrender.py, qparts.py, rcexport.py, glbtools.py, frameio.py   the ray caster, the buildings' look for
                         models made of convex parts, the .glb writer
  vdeliver.py, vcheck.py    renders, previews and checks a unit from its spec
    python3 renderall.py 0 1 PKG      renders PKG/frames/
