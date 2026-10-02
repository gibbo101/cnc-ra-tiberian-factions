Tiberian Sun Sensor Array (GADPSA, art GTDPSA; TSDPSA in the mod: the Mobile Sensor Array deployed) rebuilt for
Red Alert Remastered (HD).

One 3D model fitted to TS's own sprites (GTDPSA, GTDPSAMK, GTDPSA_A), rendered two ways with the same renderer as the
Construction Yard, Power Plant, Barracks, Silo, Tech Center, Refinery, War Factory, Radar, Helipad, Service Depot and
Component Tower: same materials, light, shadow (baked in at ~75% black) and outline. Fit to TS's frame in TS's own
camera: silhouette 0.93, house green 0.89; the build-up's poses fitted frame by frame (the mast's angle in each of
GTDPSAMK 15-28). Not on last night's list: made while you were away, my calls are listed at the end.

ts-angle/  TS's own camera, lit from TS's side so it reads like the sprite. CANVAS 256x416: the canvas, scale and place
           the array has in the mod now (TS's frame x4.225, TS px (0, 0) at canvas (-75, -54), fitted to
           in-mod/tsdpsamake-0018.png, IoU 0.98). Drops in over the current frames.
ra-grid/   On RA's square grid: RA's camera (orthographic, 32 degrees above the ground, looking north), TS's way round
           (not turned: the vehicle broadside, the mast at its west end, the cab at its east end).
           CANVAS 256x416 (the mod's): the 1x1 plot is x 64-192, y 144-272, centred, the foundation's south edge on the
           plot's. The vehicle (123 long, 92 wide) fits the plot; its outriggers' pads reach a few px past it. The mast's
           shadow runs to the canvas's right edge (faded over its last px, as on the other buildings).
COLOUR     Green = house colour: the panel up the mast's south face and the light panel on the cab's east face (TS's remap
           green there). Exactly the yard's green. Every frame has a -trim.png (white = house colour, antialiased).

What it is (read from TS's frames; GTDPSAMK shows the vehicle deploying):
  tracks     two track units along the vehicle (east-west), their ends raised over the idlers, five road wheels a side
  hull       GDI tan-ochre, the deck at about a third of a cell up, a yellow stripe along its long top edges; a tread-plate
             patch where the mast lies when it is down
  cab        a raised block at the east end, north side: a house-green light panel on its east face, a window on its south
  housing    a brown block north of the mast, tall beside it and sloping down to the deck at the east (TS draws it brown
             in every frame), a white-topped pod at its foot
  mast       a tan cylinder on a pivot near the vehicle's west end (steel brackets either side of its foot), a house-green
             panel up its south face, a dark channel up its east side
  head       a radar dish on a turntable at the mast's top, facing east-south-east and up, a feed on a tripod at its
             focus; GTDPSA_A flashes a light bar up its hollow
  outriggers four yellow legs from the hull's corners down to pads on the ground
  antenna    a thin black whip behind the mast (TS shows it while the mast is down)

Each view has the same folders. Every frame is on the view's full canvas, in place, with a -trim.png.

building/sensor-array-00, -01   healthy and damaged. TS's GTDPSA has 3 frames, all the same picture: TS draws no damage.
                                Damaged here (my call, light, greys and browns): soot over the deck and up the mast,
                                paint chipped off edges and the stripe, the cab's north-east corner stoved in and its
                                window smashed, a bite out of the dish's rim, a few chunks by the tracks.
A-flash/sensor-array-flash-00..09
                                GTDPSA_A: 00-04 the light bar up the dish's hollow flashes white-blue and fades back to
                                the dish's grey (TS's five levels, the outer end brightest), cut against the healthy
                                building; 05-09 empty, as TS's damaged half (the damaged array's light is out).
loop/sensor-array-loop-00..09   the mod's TSDPSA.ZIP layout (0000 healthy with the flash, 0005 damaged): 5 healthy + 5
                                damaged, straight renders.
build-up/sensor-array-build-00..35
                                36 frames in GTDPSAMK's order (TS's 36; TSDPSAMAKE.ZIP has 19: take 00, 02 .. 34, 35, or
                                play all 36 faster): the vehicle drives up with its mast down along the deck (00); the
                                outriggers swing out level, the east pair (01-06) then the west (07-10), and come down onto
                                their pads (11-14); the mast swings up about its pivot (15-28, its angle fitted to each of
                                TS's frames: 10 .. 90 degrees); the radar dish, folded down to the east on its post (28),
                                swings up and opens (29-35); 35 is the finished array.

Stacking: building, then A-flash (healthy t = 00-04; damaged 05-09). With A frame t that matches loop frame t.

previews/  the array on its own; both states next to TS's; the mod's frames (tsdpsa-0000, -0005, tsdpsamake-0018) next to
           the same HD frames; next to the Construction Yard, the Power Plant, the Component Tower and a GDI wall run (RA
           grid); the house colour next to the yard's; the build-up as a strip and a GIF against GTDPSAMK; the flash loop
           against TS's; shape-check.png (the model in TS's own camera over TS's frames, and the RA grid both ways round).
3d/        sensor-array.glb (glTF 2.0 .glb), in its own frame (TS's way round, as the RA grid version). Meshes:
           "sensor-array" / "sensor-array-damaged" (deployed), "sensor-array-stowed" (as it drives up: the mast down, the
           outriggers in). Markers: "mast-pivot" (the pivot; the mast swings about the north-south axis through it),
           "dish-centre". Cameras: "camera-ts-angle" and "camera-ra-grid" (256x416 each = the delivered frames). Axes:
           x east, y up, z south; 1.0 = one cell = 128 px on the RA grid; origin the foundation's centre on the ground.
           COLOR_0 = the materials' colours, COLOR_1 = house colour (white).
src/       Python 3 (numpy, scipy, Pillow, scikit-image for the 3D export). hd.py is the renderer, brender.py the views.
           dpsa.py (the model, its poses), dpsamat.py (materials, the flash), dpsadamage.py, dpsabuild.py (GTDPSAMK's
           order), dpsarender.py (views), dpsafinal.py (frames), dpsaexport.py (3d), dpsaspec.py, dpsageo.py /
           dpsafit.py / dpsaplace.py (reading TS's frames, the fit, the mod's placement).
             python3 dpsafinal.py states|build iso|ra [ss]   the frames (ss 4 used)

My calls (made while you were away; each easy to change):
  - TS draws no damage for it (GTDPSA's three frames are the same picture), so the damaged state is mine, kept light.
    If you'd rather it stays as TS has it, the damaged frames become copies of the healthy ones.
  - RA grid: TS's way round (broadside: the mast at the west end, its green panel facing the camera). Turned a quarter
    (the cab to the camera, the mast at the back) is in shape-check.png.
  - The build-up keeps TS's 36 frames (the mod's MAKE has 19).
  - TS's sprite can't show depth: the mast stands on the vehicle's south half (where its foot shows above the deck's
    edge), pivoting 26 units up its length, so that down it lies along the deck as TS draws it.
  - The head is a radar dish (your note: the first version's plate read as a funnel): on a turntable, facing
    east-south-east and up, so it reads as a dish from both cameras; TS's dark cap with a lighter edge to its east.
