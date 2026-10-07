Tiberian Sun Dropship Bay (GADROP, art GTDROP; TSDROP in the mod) rebuilt for Red Alert Remastered (HD) from
TS's own art: Westwood cut the building, but its SHPs stayed in the game files (GTDROP, GTDROPMK, GTDROP_A, GTDROP_B,
GBAYICON). This replaces v1, which was the Service Depot's pad standing in for it.

One 3D model, its shapes from your high-res picture of the bay and TS's frames, fitted to GTDROP 00 in TS's own camera
(silhouette 0.92), rendered on RA's square grid with the same renderer as the Construction Yard, Power Plant and the
rest: same materials, light, shadow (baked in at ~75% black) and outline.

v4 (Luke, 7 Oct 2026, from the game: "dropship bay is the upgrade center with attached buildings to the left"): its
east half is now the Upgrade Center's current model - the east end straightened as the Upgrade Center's (an upright end
wall, flush front to back, three straight pipes turning into it, the light down an upright post) - and the roof's west
end hips down like its east end ("the roof on the left is a hard cutoff"). The overhang over the guard stays, now on a
support pillar at its front-left corner. RA grid only, as you asked: no ts-angle/ folder; the .glb carries TS's camera
("camera-ts-angle") and src's gdropfinal.py renders that view (iso) if it is ever wanted.

TS reused the bay's east half for the Upgrade Center: GTPLUG sits on GTDROP 59 px left and 18 px up, the same block
(the house-green slope, the purple band, the roof and its dish, the brown ramp with three pipes, the deck on its feet)
to within a shade of TS's pixels, and the same damage. So that half IS the signed-off Upgrade Center model, moved into
place, its deck stretched to the bay's; GTDROP_A is GTPLUG_A's dish four frames on.

ra-grid/   On RA's square grid: RA's camera (orthographic, 32 degrees above the ground, looking north), TS's way round:
           the ramp to the south (the camera), the pad, the guard and the house-green slope facing you. CANVAS 768x512 with the
           3x3 plot at x 192-576, y 64-448, centred, the foundation's south edge on the plot's.
COLOUR     Green = house colour (TS's red remap): the slope's panes, the tower's south gable face and the lean-to behind
           it, the ramp's stripes, and B's light strips when they flash house colour (the picture's yellow). Exactly the yard's green. Every frame
           has a -trim.png (white = house colour, antialiased).

What it is (the picture's parts, placed and sized to GTDROP 00 and GTDROPMK):
  deck       a grey concrete landing deck raised on square feet, a thick tan beam along its south-west edges (TS's bright
             beam), its west end out past the deck on a thick column
  pad        the landing pad: a dark metal plate on the deck, a hexagon long east-west and pointed at both ends: a light
             rim with B's four light strips (the tips' edges west and east, the middle of the long edges north and south),
             tan lines from its corners into a centre square outlined dull red, darker panel seams
  guard      the jet blast guard between the tower and the pad (the dropship lands on the pad): an L-shaped dark metal plate
             standing in a slot in the deck, running north-south, its back wall leaning back to the west, its floor
             sloping down to a lip on the east, ribs across both, end plates (TS: the dark ribbed trough)
  ramp       from the deck's south edge down to the ground: a dark blue-grey plate between raised rails, a hinge beam
             along its top, house-green hazard stripes across its middle
  tower      on the deck's west strip: its tan body with TS's blue-grey band under the eaves, the tall console on it with
             its sloped east face (the picture has GDI's emblem there: left off, no logos), two raised blocks on its ridge
             with a notch between, a louvred vent on the south one; the south gable face and the lean-to north of it house
             green (TS's), a steel pipe down the gable
  notch      TS's grey concrete slope in the deck's north-west notch, rising to a ledge at the back, a low dark parapet
             along it
  block      the Upgrade Center's: the long block on the deck's north part, its house-green slope to the south, the
             purple band, the roof with the radar dish (GTDROP_A) hipped down at both ends, the upright end wall at the
             east end with three pipes and the light post; two antennas on its east end, two on the tower; a pillar
             under the roof's overhang at its front-left corner

Every frame is on the RA grid's full canvas, in place, with a -trim.png.

building/dropbay-00, -01          healthy and damaged, as GTDROP 0 and 1 (GTDROP 2 is the heavier wreck: RA has healthy
                                  and damaged only); the mod's TSDROP.ZIP has 2 frames. Healthy: the dish's box without
                                  the dish (A-dish draws it turning). Damaged, as TS breaks it: the console's sloped face
                                  burnt open over its south and middle part (char, bare beams across; its gable and the
                                  ridge's north end standing); the block's roof burnt over its east half with bare beams,
                                  its band broken along it, the nearer east antenna knocked off, two pipes broken off low with
                                  their tops hanging and the broken length leaning on the third (the Upgrade Center's); the ramp broken through at its
                                  west middle; soot, chunks. The dish stands still (TS's A has no damaged half). Greys and
                                  browns only.
A-dish/dropbay-dish-00..39        GTDROP_A, the radar dish turning once (00-19) over the healthy building; 20-39 empty, as
                                  TS's (the damaged one's dish stands still in building-01).
B-lights/dropbay-lights-00..39    GTDROP_B, the pad's four light strips: 00-19 over the healthy building (a flash: white,
                                  house colour, fading; then a softer one, TS's levels per strip), 20-39 over the damaged
                                  one: the north strip half smashed, the south one a stub, as TS's damaged half.
build-up/dropbay-build-00..18     19 frames, as the mod's TSDROPMAKE.ZIP has, in GTDROPMK's order (TS draws 17): the deck
                                  grows out from its middle (00-03), its outlines, the ledge and the pad plate (04), the
                                  tower's body and the block rise (05-07), the console's roof and the lean-to (06-08), the
                                  antennas (08-10), the guard's slot (10), the dish (10-11), the slope in the notch
                                  (11-13), the ramp reaches the ground and the guard rises out of its slot (13-15), its ribs
                                  (15), the pipes and grey panes (16-17), the house colour (18 = the healthy building +
                                  A-dish 00). The dish goes up at its A frame 00 angle and stays there, so nothing jumps
                                  when A's loop starts (TS's MK draws it at the sprite's angle).

How the layers stack: bib-less; building-00/01, then A-dish and B-lights over it (the same frame number in both loops
of 20). The mod's TSDROP.ZIP has no overlays now: A and B are new.

previews/  the bay on its own; both states next to TS's; next to the Construction Yard, the Power Plant, the Component
           Tower and a GDI wall run; the house colour next to the yard's; the build-up as a strip and a GIF next to GTDROPMK; the idle
           loop (A + B, healthy and damaged) next to TS's.
3d/        dropship-bay.glb (glTF 2.0 .glb), in its own frame (TS's way round, as on the RA grid). Meshes: "dropship-bay"
           and "dropship-bay-damaged" (the dish at its A frame 00). Markers: "pad-centre", "ramp-foot", "dish-pivot",
           "light-west/-north/-east/-south", "guard" (for the dropship's landing later). Cameras: "camera-ra-grid" (768x512) and "camera-ts-angle" (TS's
           camera on the mod's 768x512 TS-angle canvas: render it to rebuild the TS angle). Axes: x east, y up, z south; 1.0 = one cell = 128 px on the RA grid; origin the foundation's centre on the ground.
           COLOR_0 = the materials' colours, COLOR_1 = house colour (white). stl/: print-ready STLs.
src/       Python 3 (numpy, scipy, Pillow, scikit-image for the 3D export). hd.py is the renderer, brender.py the views.
           gdrop.py (the model: the bay's parts, the Upgrade Center's half via plug.py, the build-up controls, the
           damage), gdropmat.py (materials, B's lights), gdropdamage.py, gdropbuild.py (GTDROPMK's order), gdroprender.py
           (views), gdropfinal.py (frames), gdropexport.py (3d), gdropspec.py; tsshp.py (TS's SHPs decoded),
           gdropgeo.py / gdropfit.py / gdropscore.py (reading TS's frames, the fit).
             python3 gdropfinal.py states|dish|build ra [ss]   the frames (ss 4 used; iso = the TS angle)

My calls (each easy to change):
  - Shapes from your high-res picture where TS's sprite is too small to read them: the tower's console with its raised
    blocks, vent and pipe; the jet blast guard; the pad plate with its rim, lines and centre square; the ramp's rails,
    hinge beam and diagonal hazard stripes; the ledge and its column. Sizes and places from TS's sprite.
  - Colours from TS where the picture differs: the deck grey concrete (the picture's is tan), house green where TS has
    house colour (the picture is all tan; its yellow hazard stripes are TS's green), TS's blue-grey band on the tower.
  - TS's grey slope in the deck's north-west notch kept (the picture shows a low parapet there instead), with the
    picture's parapet along its back.
  - GDI's emblem on the console's face left off (no logos).
  - TS-angle scale: the Upgrade Center's, so the shared block is the same size; the foundation's centre on the canvas
    centre (the mod's v1 pad was drawn 2.36x bigger and has no placement for this building to match).
  - The build-up at the mod's 19 frames.
