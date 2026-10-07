Apocalypse Tank (RA2 [APOC], art MTNK) in HD for Tiberian Factions: R2APOC  -  v2.1
===================================================================================

frames/     r2apoc-0000.png ... r2apoc-0063.png, the mod's 64 frames on its 448 x 448 canvas, each with a -trim.png
            (white = house colour, antialiased):
              0-31    the hull with its shadow, 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E)
              32-63   the turret (its shell, hatch, antennas, rocket pods and the twin barrels), no shadow, 32 facings,
                      drawn at the hull's canvas centre (RA2's turret sits on the unit's position)
previews/   8-facings.png            hull and turret facing the same way, the mod's frames beside HD
            hull-8-facings.png, turret-8-facings.png   each set on its own, every 4th facing
            turn.gif                 all 32 facings in turn, the mod's frames beside HD
            turret-turning.gif       the turret turning on the hull facing east
            scale.png                next to the HD harvester and EA's Mammoth, as the game draws them
            shape-8-facings.png      the model drawn flat (a colour per part) in the mod's cameras beside the mod's
                                     frames, the hull's and the turret's every 4th facing, with the silhouette overlap
            closeup.png              the assembled tank at 2x in four facings
ts-apoc-hd-3d/   the 3D model, in its own zip (ts-apoc-hd-3d.zip) next to this folder:
            r2apoc.glb   the hull and the turret (vertex colours), the turret under its own node, with the mod's camera
src/        the model, the renderer and the checks (see Rebuilding below)

v2.1 replaces v2 (and v1): v2's model, canvas and look, with the plough at the nose remade sharp and menacing.


What changed from v2
--------------------
Luke: the front ramming bar should be sharp and menacing; v2's looked flat and dull, like a bumper bar.  The plough
keeps RA2's zig-zag across the nose (x 52..59, y 5..27) and its two rams, and is now:
- a chiselled blade: tall at its back (z 4.2..6.6), its top sloping down to a knife edge at its front (z 4.4..4.8);
- seven spikes off its front edge, tapering to points angled forward and down (Westwood's jagged black blade): the
  longest (3.3 voxels) at the middle, one at each end swept outward, two on each flank;
- dark gunmetal (Westwood's black blade, RA2's dark voxels), its upper faces worn a little lighter, with crisp edges
  that catch the light.
Only the hull frames (0-31) change; the turret frames are v2's.  v1 copied RA2's voxels box by box, so it still read as
voxels; v2 on are rebuilt clean.


What it is
----------
v2.1 is built the way the Titan, the Wolverine and the Disruptor are: RA2's voxels (MTNK.VXL the hull, MTNKTUR.VXL
the turret, MTNKBARL.VXL the barrels) are the blueprint - where every part is and how big - and each part is modelled
clean (flat plates, true slopes, round wheels, drums and tubes, bevelled edges) in RA2's own colours, with panel joints,
grilles, bolts and straps to the Titan's and the Wolverine's standard.  The voxels are the source of truth: every
part, step and colour below was read from them slice by slice.  Westwood's art of the Apocalypse (the FMV, the cameo
and the in-game model; Luke sent them) is the guide to how RA2's parts read in HD where the voxels have the part: the
fuel drums, the 4-tube rocket pods, the muzzle brakes, the mantlets at the barrels' roots, the round hatch on top and
the toothed plough.

The Apocalypse, part by part (RA2's layout; q = the voxels' coordinates, x back to front, y right to left, z up):
- Four track pods: the rear pair (q x 5..28, y 1..8 and 24..31) and the narrower front pair (x 30..49, y 3..8 and
  24..29): black belts with grousers, their bottom run under the grey road wheels (RA2's: four at the back, three at
  the front, z 2..4), the idlers rising to the fenders.
- The fenders over them: at the back full width (y 0..8, x 3..30), a low outer plate with a lip down to z 7 and the
  inner plate a step higher (RA2's); over the front pods narrower (y 2..8), sloping down at the front to a mudguard.
  In plates, bolted along their outer edges; three small dark fittings on each (RA2's dark voxels at x 23, 33, 43).
- The four fuel drums on the rear fenders (RA2's house colour, x 4..10 and 11..17, y 0..8, z 9..14), lying across the
  hull with their ends outward, two hoops round each (RA2's ridges; Westwood's drums).  Plain house colour.
- The hull between the pods (y 7..25): its deck at z 12 from x 6 to 45, the glacis down to the nose at x 53, the rear
  face at x 5; the deck in plates; two louvred engine grilles on the rear deck (RA2's dark panels, x 9..17) and the
  radiator grille across the rear face (x 5, z 7..11); two round hatches on the glacis (RA2's dark blocks, x 46..51;
  Westwood's round covers); bolts along the glacis' foot and the rear face's top.
- The toothed plough across the nose (RA2's zig-zag blade, z 4..6, x 52..59, y 5..27): a chiselled blade with a knife
  edge and seven spikes angled forward and down (What changed from v2), on two rams running forward under the hull
  from brackets at x 42..46 (RA2's y 11 and 21).
- The turret (MTNKTUR): the house-colour skirt (RA2's green, z 0..4.6), widest at z 1..3, its front sloping forward to
  x 25 and its back undercut (RA2's), under the light olive top (z 4.6..7, its front at x 22, its back at x 2), in
  plates, bolted along its edges; the round hatch on top (RA2's dark x 10..16; Westwood's notched ring round a lid);
  two whip antennas at the back corners leaning back (RA2's x 0..3, z 6..17) on mounts, two hooks below them.
- A 4-tube rocket pod each side (RA2's dark rings at y 0..5 and 19..25: a bundle of four tubes seen side on, its axis
  43 degrees up and forward, 8.5 voxels long; Westwood's 4-tube pods): the tubes' mouths black, two straps round each
  bundle, a back plate and the mount into the turret's side.
- The twin barrels (MTNKBARL, 27 voxels long): each from a mantlet block at the turret's front (Westwood's), a thicker
  root with a collar, the barrel, and a slotted muzzle brake (Westwood's) with the bore black.

The model's silhouette overlaps the mod's frames drawn flat in the mod's cameras (shape-8-facings.png): the hull by
0.93, the turret by 0.85 (its whip antennas are thin, as Westwood's, where RA2's voxels draw them a voxel or
two thick).  The finished frames: the hull's by 0.931 against the mod's (src/vcheck.py), the turret's by 0.832.


Placement
---------
- The canvas, the sizes and the places are v1's (the mod's): the hull at 5.03 canvas px per voxel unit, the unit's
  position at canvas (223.66, 223.09); the turret at the mod's turret size (4.92 px per unit, 0.978 of the hull's).
- The whole unit is lowered 0.34 onto the ground (MTNK's lowest voxels sit that far above its HVA origin) and the hull
  camera moved to match, so every hull pixel stays where the mod's frames have it.
- The turret is drawn at its size about its base (its foot on the deck), its pivot where the hull frames put the unit's
  position, so laid on the hull frame it sits on the deck exactly.  Against the mod's turret frames it is 0.2 px right
  and 0.7 px lower.
- Each section is centred side to side on the unit's position (as the Disruptor's): RA2's hull sits 0.1 voxel left of
  it and its barrels 0.1 left, and the turret's shell 0.4 right of the pivot it turns on (its rocket pods and barrels
  are centred on the pivot).  So the turret turns on its own middle.

Fire points
-----------
The weapon tips are where the model puts them, as before; the turret frames keep the mod's size and place.  From the
turret's pivot (on the ground under the unit's position), in leptons (256 a cell), facing east:
  the barrels' muzzles   223 forward, 28 right, 101 up  /  223 forward, 28 left, 101 up
  the rocket pods' mouths  1 forward, 63 right, 133 up  /  1 forward, 63 left, 133 up


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides facing
  the camera as on the other units.  The game draws this canvas at two thirds (8 canvas px per classic pixel), so the
  outline, the shadow's blur and the contact shadow are 1.5 times as wide on the canvas.
- Colours: RA2's (UNITTEM.PAL), lifted so the lit model is as light as the mod's frames draw the Apocalypse: the hull
  olive (RA2 73) 152,152,116, the turret's top (RA2 70) 212,212,174, dark grey for the grilles, hatches, pods and barrels
  (RA2 53-56), black belts and fittings, grey road wheels.  House colour: pure green 0,214,0 x (1 + 1.1 grain) on the
  drums and the turret's skirt, plain (no grilles, fine detail or black lines on it); the -trim masks cover exactly
  that.  A little grime rising from the ground on the lower hull.


Shadow
------
Every hull frame carries the unit's shadow, black at alpha 191 (75%), blurred, falling to the right and a little
towards the camera, as long as the buildings' and the harvester's.  Within 14 px of the canvas edge it fades out.
The turret frames carry none, as the mod's.


3D model (ts-apoc-hd-3d/r2apoc.glb)
-----------------------------------
- Nodes: ApocalypseTank > unit_facing_east > hull, turret > turret_body, barrels.  The turret node sits on the unit's
  position, scaled 0.978 about the turret's base (the mod's turret frames' size), and turns about its own local z axis.
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.  The unit faces east (the mod's facing 24).
- The meshes are exact (cut from each part's planes and curved surfaces), the paint as vertex colours.
- Camera "camera_mod": orthographic, the mod's camera, framing the canvas exactly (checked by drawing the mesh
  through it over hull frame 24 with turret frame 56 on it: overlap 0.977).
- Khronos's glTF validator: errors 0, warnings 0, infos 0, hints 0.
- Vertex colours: COLOR_0 albedo (no light or shadow), COLOR_1 house colour (white = house colour).


Judgement calls (each one easy to change)
-----------------------------------------
- The fuel drums lie across the hull, their ends outward (RA2's voxels draw each as a block rounded front to back
  with two ridges across its top; Westwood's drums lie that way).
- The rocket pods are four-tube bundles (Westwood's); RA2's voxels draw each as a hollow outline 43 degrees up.
- The whip antennas are thin (Westwood's), so the turret's flat overlap is lower than the hull's.
- The glacis' two dark blocks are round hatches (Westwood's round covers there).
- Each section centred side to side on the unit's position (Placement), moving RA2's turret shell 0.4 voxel.


Rebuilding
----------
src/ holds everything: the model (apocmodel.py), the cameras (apoccam.py), the materials (apocmat.py), the renderer
(apocrender.py, rcrender.py, rc.py, qparts.py, and the buildings' hd.py, walls2.py, wnoise.py), the .glb export
(apocexport.py, rcexport.py, glbtools.py, export3d.py), the checks (apocshape.py, vcheck.py, glbcheck.py) and the voxel
readers (vxl.py, avox.py, adump.py).  Set TS_HANDOFF to the hand-off's root folder (the one holding 27-R2APOC/,
00-TSHARV-example/ and renderer/).
    python3 apocrender.py 0,1,...,63 4 frames 1        the frames
    python3 apocexport.py r2apoc.glb                    the 3D model
    python3 apocshape.py shape.png                      the shape check
    python3 adump.py tur y 2                            a slice of RA2's voxels as text
