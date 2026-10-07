Tiberian Sun Tick Tank, dug in (GATICK; art GTTICK, GTTICKMK) for Tiberian Factions, in HD on RA's grid: v3
==============================================================================================================

The deployed Tick Tank, built from the same model as the unit (ts-ttnk-hd v3.5, src/ttnk3hd.py), so the unit, the
deploy and the dug-in building always match.  v1 and v2.1 were made in the buildings chat on the unit's v3.1/v3.2;
v3 (7 Oct) was designed with the unit in one flow here (Luke).

ra-grid/     the frames, RA's square grid only (since 6 Oct: no TS-angle frames; the .glb keeps TS's camera)
  building/  tick-tank-dug-in-00, -01            the tank dug in, no turret: healthy, damaged
  turret/    tick-tank-dug-in-turret-00 .. 31     the turret at the mod's 32 facings (00 north, anticlockwise: 08 west, 16 south,
                                        24 east), drawn in place, cut against the healthy base: its own pixels solid, the
                                        shadow it casts as black at the darkening's alpha, so one set lies over either state
  build-up/  tick-tank-dug-in-build-00 .. 24   the deploy, one frame per GTTICKMK frame: 00 is the unit exactly as its package
                                        draws it (hull 16 + turret 48, at two thirds; overlap 0.998); 01-04 the
                                        turret's shadow fading in; 24 is building-00 with turret-16.  Played
                                        backwards it is the undeploy.
  every frame has a -trim.png (white = house colour)
muzzle.txt   the gun's tip per turret facing, canvas px and leptons, and the turret's pivot
previews/    on its own; both states beside TS's GTTICK; the build-up strip beside GTTICKMK; deploy-vs-original.gif
             (dig in, the turret turning round, dig out); the 32 turret facings; deploy-vs-unit.png (build-up 00
             against the unit's own frames)
src/         everything that renders it (below)
3D           ts-nod-tick-tank-dug-in-hd-3d/ (zipped on its own): tick-tank-dug-in.glb

THE DESIGN (Luke, 7 Oct)
  - It digs in facing SOUTH, the nose toward the camera (the mod's facing 16): the game turns the tank to face
    south before it deploys.  Standing upright, the hull then shows the camera its wide top (the ramps, the groove,
    the pipes) and sits on its own cell; facing east it read as a thin tower with the turret overhanging it.
  - As TS's GTTICKMK does it (Luke: bury nose-first and go almost vertical): the drum and claws dig in, the tank pitches
    nose-down to 81 degrees, sinking 6.5 voxels and sliding 1 forward, until only its back end stands out
    of the ground.  The build-up's timing follows GTTICKMK's pitch frame by frame (src/mkfit.txt).
  - The turret runs back up the two ramps (its track) while the tank is still shallow, then goes over the back edge
    onto a short post on the ramps' tall flat back face, which is the top once the tank is upright (v3.5 raises the
    middle's back, as TS's tank has it, for that flat top; the side hulls stay lower).
  - The turret: v3.5's high dome in house colour, the gun on a trunnion in a slit so it can elevate.
  - Soil: dark loam heaped round the hull where it goes in, highest on the side the nose went in, spoil and clods
    (TS's desert sand left out, Luke); clods thrown up by the drum during the dig.
  - Damaged: shell holes in the exposed hull, soot, a snapped pipe and a corner box knocked to the ground (TS's
    GTTICK has no damage of its own; kept light).

PLACE AND CANVAS
  - Canvas 256 x 256, the 1x1 plot at x 64-192, y 64-192.  The tank stays where the unit stood: its position (the
    cell's centre) on the ground at canvas (128.0, 127.33), as the unit's frames have it at
    two thirds, so nothing jumps when it deploys (not the buildings' rule of the foundation's south edge on the plot's).
  - Everything, shadow included, lies within x 48-245, y 26-190.
  - The turret's pivot: 0 leptons west, 35 south of the cell's centre, 103 up.

LOOK
  The units' renderer (src/hdv.py, src/rcrender.py) at the buildings' scale (128 px a cell, 4.17 px a voxel): the
  RA-grid camera (orthographic, 32 degrees above the ground, looking north), the buildings' light, ~75% shadow baked
  in, house colour exactly (0, 214, 0) x (1 + 1.1 grain), damage in greys and browns.

3D MODEL (tick-tank-dug-in.glb)
  base, base-damaged (the dug-in hull, its post, the soil, the debris), turret (a node at its pivot, facing the hull's
  way; turn it about up to aim: the mod's facing = 16 + angle / 11.25 degrees), markers turret-pivot, muzzle (a
  child of turret), cell-centre; cameras camera-ra-grid (frames the canvas exactly: drawn through it the mesh covers
  frame 00 + turret 16 with an overlap of 0.969) and camera-ts-angle (TS's camera, to rebuild the TS angle
  if ever wanted).  Axes glTF's: x east, y up, z south; 1.0 = one cell; origin the cell's centre on the ground.
  Vertex colours: COLOR_0 albedo, COLOR_1 house colour; the painted detail (soot, holes, caked soil) is in the frames.

SRC
  Python 3 with numpy, scipy and Pillow.  ttnk3hd.py the tank (hull and turret, v3.5); tickm.py the dug-in model and
  the deploy (pose per build-up frame, the turret's run and swing, the post, the soil); tickdamage.py the damage;
  tickrender.py the canvas and place; tickfinal.py the frames; tickexport.py / tickglbcheck.py the .glb and its check;
  tickpack.py this package; fakeunit.py the tank's voxel frame; tickfit.py the TS fits (mkfit.txt).
    PKG=out python3 tickfinal.py states ra 4 && python3 tickfinal.py turret ra 4 && python3 tickfinal.py build ra 4
    PKG=out python3 tickexport.py;  PKG=out python3 tickpack.py UNITS_PACKAGE

JUDGEMENT CALLS
  - Facing south to deploy (Luke picked it from the east and south versions): the frames, the .glb and muzzle.txt
    follow the mod's facing 16; TICK_FACING=24 in tickm.py rebuilds the east version.
  - The build-up's pitch timing is GTTICKMK's (fitted facing east); the dug-in pose is v2.1's (81 degrees), which
    was fitted to GTTICK facing east.
  - No scale preview next to the GDI yard and plant this time: those scene files live in the buildings work.
