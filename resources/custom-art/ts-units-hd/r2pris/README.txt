Prism Tank (RA2 [SREF]) in HD for Tiberian Factions: R2PRIS  -  v2
==================================================================

frames/     r2pris-0000.png ... r2pris-0063.png, the mod's 64 frames on its 384 x 384 canvas, each with a -trim.png
            (white = house colour, antialiased):
              0-31    the hull with its shadow, 32 facings counter-clockwise from north (0 N, 8 W, 16 S, 24 E)
              32-63   the prism turret (its post, the fan, the emitter), no shadow, 32 facings, drawn at the hull's
                      canvas centre (RA2's turret sits on the unit's position)
previews/   8-facings.png            hull and turret facing the same way, the mod's frames beside HD
            hull-8-facings.png, turret-8-facings.png   each set on its own, every 4th facing
            turn.gif                 all 32 facings in turn, the mod's frames beside HD
            turret-turning.gif       the turret turning on the hull facing east
            scale.png                next to the HD harvester and EA's medium tank, as the game draws them
            shape-8-facings.png      the model drawn flat (a colour per part) in the mod's cameras beside the mod's
                                     frames, the hull's and the turret's every 4th facing, with the silhouette overlap
            closeup.png              the assembled tank at 2x in four facings
ts-pris-hd-3d/   the 3D model, in its own zip (ts-pris-hd-3d.zip) next to this folder:
            r2pris.glb   the hull and the turret (vertex colours), the turret under its own node, with the mod's camera
src/        the model, the renderer and the checks (see Rebuilding below)

v2 replaces v1: v1 copied RA2's voxels box by box, so it still read as voxels.


What it is
----------
v2 is built the way the Titan, the Wolverine, the Disruptor and the Apocalypse are: RA2's voxels (SREF.VXL the
hull, SREFTUR.VXL the prism) are the blueprint - where every part is and how big - and each part is modelled clean
(flat plates, true slopes, round wheels, drums and rings, bevelled edges) in RA2's own colours, with panel joints,
bolts, vision slots and fins to the Titan's and the Wolverine's standard.  The voxels are the source of truth: every
part, step and colour below was read from them slice by slice.  Westwood's art of the Prism Tank (Luke sent the FMV
model's renders, the in-game model and two scale models) is the guide to how RA2's parts read in HD where the voxels
have the part: the finned engine coolers and the round fan on the rear deck, the buttresses round the turret ring,
the commander's cupola, the fan's ribbed back, the round hubs at its sides and the emitter's lens.

The Prism Tank, part by part (RA2's layout; q = the voxels' coordinates, x back to front, y right to left, z up):
- Two tracks (q y 0..7 and 26..33, x 5..44): black belts with grousers, five big road wheels each (RA2's wheels reach
  z 0..6), the sprocket and the idler at the ends, mudguards at both ends (RA2's black, z 7..9).
- The fender plate over each track (z 10..11, x 5..45), and at the back the raised sponson on it (x 1..32, y 0..8,
  z 11..14): banded in house colour all round (RA2's green), its front cut on the slant (x 28 at its outer edge to 32);
  the dark armour plate on top (x 6..26, y 2..8, z 14..16), bolted along its edges, its nose sweeping down in house
  colour to the turret ring (RA2's green swoosh).
- The hull between the tracks (y 8..25): its floor at z 8, its deck at z 14, the glacis down to the nose at x 50, the
  rear face sloping in below z 11; light blue-grey (RA2 88), the front deck and the glacis darker (RA2 90-94), with a
  hatch on the glacis (RA2's grey), joints and bolts.
- The rear deck plate (x 0..21) with the round fan let into it (RA2's round pit, x 4..15; Westwood's fan: its blades
  under a ringed guard) and four finned coolers lying along it (RA2's dark blocks x 4..10 and 15..21, y 7..10 and
  23..26, z 15..19; Westwood's "6 coolers" on the engine deck), each on a cradle.
- The turret ring: a house-colour drum rising through the deck (RA2's green, radius 8.6, z 7..16), six house-colour
  buttresses round it (Westwood's arches), stepped dark rings above (z 16..19) bolted round their tops, and the olive
  bearing on top (RA2's 70/73, z 19..20).
- The front deck: a periscope block on the right (RA2's x 38..44, y 10..15) with its glass, and the commander's cupola
  on the left (x 38..46, y 18..23, its top at z 16) with vision slots round it (Westwood's).
- The prism (SREFTUR): the post (RA2's dark column, z 0..9) and its collar, the cradle on it with an arm forward under
  the emitter; the fan - a quarter disc of house colour standing across it (RA2's green sides, from its foot at the
  back round to its top) - with its ribbed dark back (RA2's dark band, 4 voxels deep: seven ribs, gaps between them);
  a round hub each side (RA2's discs, bolted), and the emitter at the front: its dark housing in a house-colour frame
  (RA2's green at its sides and top), its face glowing white (RA2's white, x 16..17, y 2..6, z 13..20), bluer at its
  edges, three bars across it (Westwood's lens).  The face is drawn at its own glow whatever light falls on it; no
  light from it falls on anything (no glow RA2 doesn't have).

The model's silhouette overlaps the mod's frames drawn flat in the mod's cameras (shape-8-facings.png): the hull by
0.95, the turret by 0.87.  The finished frames: the hull's by 0.943 against the mod's (src/vcheck.py),
the turret's by 0.864.


Placement
---------
- The canvas, the sizes and the places are v1's (the mod's): the hull at 5.03 canvas px per voxel unit, the unit's
  position at canvas (191.5, 191.02); the turret at the mod's turret size (4.9 px per unit, 0.974 of the hull's).
- The whole unit is raised 0.18 onto the ground (SREF's lowest voxels sit that far below its HVA origin) and the hull
  camera moved to match, so every hull pixel stays where the mod's frames have it.
- The turret is drawn at its size about its base (the post's foot), its pivot where the hull frames put the unit's
  position, and as high as the mod's frames draw it: 0.8 voxel unit above where RA2's HVA puts it (the post's foot is
  hidden in the ring either way), so the prism's head stands where it does in the game now; the 3D model has it there
  too.  Against the mod's turret frames: 0.0 px right and 0.0 px lower.
- Each section is centred side to side on the unit's position (as the Disruptor's and the Apocalypse's): RA2's hull
  sits 0.05 voxel right of it and the prism 0.16 voxel left of its pivot.  So the prism turns on its own middle.

Fire point
----------
The beam starts at the emitter's face, where the model puts it; the turret frames keep the mod's size and place.  From
the turret's pivot (on the ground under the unit's position), in leptons (256 a cell), facing east:
  the emitter's face (its middle)   50 forward, 0 across, 212 up


Look
----
- Camera: the RA-grid camera, orthographic, 32 degrees above the ground, looking north.
- Light, sky, ambient, outline and supersampling are the buildings' (hd.py), with the camera fill on the sides facing
  the camera as on the other units.  The game draws this canvas at two thirds (8 canvas px per classic pixel), so the
  outline, the shadow's blur and the contact shadow are 1.5 times as wide on the canvas.
- Colours: RA2's (UNITTEM.PAL), lifted so the lit model is as light as the mod's frames draw the Prism Tank: the light
  blue-grey (RA2 88) 150,150,184, the darker blue-greys (RA2 90-94) 104,104,134 and 70,70,98, the post's dark grey,
  black belts and mudguards, the olive bearing 176,176,146.  House colour: pure green 0,214,0 x (1 + 1.1 grain) on the
  sponsons' bands and the swoosh, the ring's drum and buttresses, the prism's fan and the emitter's frame, plain (no
  grilles, fine detail or black lines on it); the -trim masks cover exactly that.  A little grime rising from the
  ground on the lower hull.


Shadow
------
Every hull frame carries the unit's shadow, black at alpha 191 (75%), blurred, falling to the right and a little
towards the camera, as long as the buildings' and the harvester's.  Within 14 px of the canvas edge it fades out.
The turret frames carry none, as the mod's.


3D model (ts-pris-hd-3d/r2pris.glb)
-----------------------------------
- Nodes: PrismTank > unit_facing_east > hull, turret > prism.  The turret node sits on the unit's position, scaled 0.974
  about the turret's base (the mod's turret frames' size), and turns about its own local z axis.
- Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
  Origin: the unit's position on the ground.  The unit faces east (the mod's facing 24).
- The meshes are exact (cut from each part's planes and curved surfaces), the paint as vertex colours.
- Camera "camera_mod": orthographic, the mod's camera, framing the canvas exactly (checked by drawing the mesh
  through it over hull frame 24 with turret frame 56 on it: overlap 0.989).
- Khronos's glTF validator: errors 0, warnings 0, infos 0, hints 0.
- Vertex colours: COLOR_0 albedo (no light or shadow; the emitter's face its glow), COLOR_1 house colour (white = house
  colour).


Judgement calls (each one easy to change)
-----------------------------------------
- The four dark blocks on the rear deck are finned coolers lying along it (RA2's voxels draw each as a hollow block;
  Westwood's engine deck carries finned coolers there).
- The round pit in the rear deck is a fan under a ringed guard (Westwood's).
- Six house-colour buttresses round the turret ring's drum (Westwood's arches; RA2's voxels draw the drum plain).
- The front deck's two dark blocks are a periscope (right) and the commander's cupola (left), from Westwood's.
- The emitter's face is lit from inside: drawn at its own glow, bluer at its edges, three bars across it.
- Five road wheels a side, evenly spaced (RA2's voxels show big wheels at z 0..6 but not one by one).
- The turret stands as high as the mod's frames draw it, 0.8 voxel unit above RA2's HVA place (Placement).
- Each section centred side to side on the unit's position (Placement).


Rebuilding
----------
src/ holds everything: the model (prismodel.py), the cameras (priscam.py), the materials (prismat.py), the renderer
(prisrender.py, rcrender.py, rc.py, qparts.py, and the buildings' hd.py, walls2.py, wnoise.py), the .glb export
(prisexport.py, rcexport.py, glbtools.py, export3d.py), the checks (prisshape.py, shapediff.py, vcheck.py, glbcheck.py),
the fire point (flh.py) and the voxel readers (vxl.py, pvox.py, pdump.py).  Set TS_HANDOFF to the hand-off's root folder
(the one holding 28-R2PRIS/, 00-TSHARV-example/ and renderer/).
    python3 prisrender.py 0,1,...,63 4 frames 1        the frames
    python3 prisexport.py r2pris.glb                    the 3D model
    python3 prisshape.py shape.png                      the shape check
    python3 pdump.py tur y 2                            a slice of RA2's voxels as text
