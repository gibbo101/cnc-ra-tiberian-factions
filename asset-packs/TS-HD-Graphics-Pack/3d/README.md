# TS-HD 3D models

The 3D models of the HD rebuilds: Tiberian Sun's GDI buildings and some of its units, each fitted to Tiberian
Sun's own sprites or voxels. Each building's and unit's HD art is rendered from its model here. The game does not use
this folder: it is here for anyone who wants the models themselves, to render new angles or to use them in another
engine.

All files are glTF 2.0 binary (`.glb`), which Blender, Godot and most engines open.

## Buildings

| File | Tiberian Sun | In Tiberian Factions | Meshes | Markers |
|---|---|---|---|---|
| `construction-yard.glb` | GACNST | TSFACT | construction-yard, -damaged | |
| `power-plant.glb` | GAPOWR | TSPOWR, TSTURB | power-plant (one pod), power-plant-3-pods, power-plant-damaged | |
| `barracks.glb` | GAPILE | TSPILE | barracks, -damaged | |
| `silo.glb` | GASILO | TSSILO | silo, -damaged | |
| `tech-center.glb` | GATECH | TSTECH | tech-center, -damaged (turned for the RA grid) | |
| `refinery.glb` | PROC | TSPROC | refinery, refinery-damaged, bib, bib-damaged | dock (where the harvester's origin goes, facing east), fire (the flare stack's mouth), lamp-north, lamp-south |
| `war-factory.glb` | GAWEAP (art GTWEAP) | TSWEAP | war-factory, war-factory-damaged (both without the door), door (shut), bib, bib-damaged | exit (the door's middle at the floor), bay-inside, jamb-left, jamb-right, lamp-a1..a5, lamp-b1..b3, fan-1, fan-2 |
| `radar.glb` | GARADR (art GTRADR) | TSRADR | radar, antennas, dish, each with -damaged | dish-pivot (the dish turns about its vertical axis), dish-centre |
| `helipad.glb` | GAHPAD (art GTHPAD) | TSHPAD | pad, helipad (the machinery), each with -damaged | landing (the landing circle's centre), light-1..17 |
| `service-depot.glb` | GADEPT (art GTDEPT) | TSDEPT | pad, depot (the gantry), each with -damaged; arm | arm-pivot, pad-centre |
| `dropship-bay.glb` | GADROP (cut from the game) | TSDROP | pad, pad-damaged | pad-centre |
| `sensor-array.glb` | GADPSA (art GTDPSA) | TSDPSA | sensor-array, -damaged (deployed), sensor-array-stowed (mast down, outriggers in) | mast-pivot (the mast swings about the north-south axis through it), dish-centre |
| `upgrade-center.glb` | GAPLUG (art GTPLUG) | TSPLUG, with TSPION, TSPODS, TSSEEK | upgrade-center, -damaged (with the dish); plug-drop-pod-node, plug-seeker-control, plug-ion-cannon-uplink (each in the east socket; 1.0 west for the west socket) | socket-west, socket-east, dish-pivot, slot-top, slot-bottom, lamp-low, lamp-high |

The war factory is Tiberian Sun's own shape, its door facing east (+x). The refinery's dock is on its east side,
as in Tiberian Sun. The dropship bay's deck carries GDI's weathered eagle in its vertex colours, where the game
draws it, across the deck inside the band; on the damaged pad it is burnt away in the blast. The radar's dish sweep and the war factory door's track (straight up 40 units, then a quarter
circle of radius 49 into the roof) are in each file's extras.

## Units

| File | Tiberian Sun | In Tiberian Factions | Parts | Animations |
|---|---|---|---|---|
| `harvester.glb` | HARV, HORV | TSHARV | harvester, harvester-unloading, tank (the lid: harvester = unloading + tank) | |
| `mcv.glb` | MCV | TSMCV | tracks, hull, right_deck, cab, crane, left_deck, hitch | |
| `titan.glb` | MMCH | TSTITN | legs; upper_body with the cannon and a muzzle marker | walk (12 steps, 0.2 s each, looping) |
| `wolverine.glb` | SMECH | TSSMEC | body (with muzzle_left and muzzle_right markers), legs | walk (12 steps, 0.133 s each, looping), stance (firing) |
| `mammoth-mk1.glb` | 4TNK | TS4TNK | hull; turret (with the barrels and tusk pods) | |
| `mammoth-mk2.glb` | HMEC | TSHMEC | body, four legs (upper, lower, foot each) | walk |
| `disruptor.glb` | SONIC | TSSONIC | hull; turret (seated 6 px aft, as the mod draws it) | |
| `hover-mlrs.glb` | HVR | TSHVR | hull; rack (at TS's place; the mod seats it per facing) | |
| `apc.glb`, `apc-water.glb` | APC | TSAPC | land hull; water hull (the hull TS swaps in on water) | |
| `subterranean-apc.glb` | SAPC | TSSAPC | hull | |
| `devils-tongue.glb` | SUBTANK | TSSUBTANK | hull | |
| `mobile-sensor-array.glb` | LPST | TSLPST | hull | |
| `mobile-emp-cannon.glb` | MOBILEMP | TSMEMP | hull | |
| `mobile-war-factory.glb` | MOBWARG | TSMWAR | hull | |
| `orca-fighter.glb` | ORCA | TSORCA | hull | |
| `orca-bomber.glb` | ORCAB | TSORCAB | hull | |
| `carryall.glb` | TRNSPORT | TSCARRY | hull | |
| `dropship.glb` | DSHP | TSDSHP | hull | |
| `juggernaut.glb` | JUGG (walking) | TSJUGG | body (with the barrel housings), legs | walk (15 steps, 0.2 s each, looping) |
| `juggernaut-deployed.glb` | JUGG (deployed) | TSJUGG | base (as deployed facing south-west), cabin turned east, barrels on a hinge; muzzle_left, muzzle_middle and muzzle_right markers | aim (the barrels raised to 45 degrees and back) |
| `hunter-seeker.glb` | GHUNTER | TSHUNT | the droid | |
| `limpet-drone.glb` | LIMPET | TSLIMP | the drone; light_left and light_right markers | |

Units face east (+x) with their position at the origin, on the ground; the aircraft's origin is the voxel's own. For a
sprite in 32 facings (0 north, 8 west, 16 south, 24 east), facing f is the model turned (f - 24) x 11.25 degrees
counter-clockwise seen from above. The units rebuilt from TS's voxels keep each voxel's step: every section is boxes
cut at 45 degrees along its convex edges.

## Conventions

- **Axes:** x east, y up, z south (toward the RA camera).
- **Scale:** 1.0 = one cell (128 px on the Red Alert Remastered grid).
- **Origin:** a building's is the centre of its foundation, on the ground; a unit's is its position, on the ground.
- **Colours:** vertex colours. COLOR_0 holds the materials' own colours (albedo: no light, shadow or outline baked
  in). COLOR_1 is the house-colour mask: white where the house colour goes. In the buildings, the house colour in
  COLOR_0 is green (0, 214, 0).
- **Moving parts** are in one pose: flags, fans, lamps and the yard's crane at rest, the radar's dish at the start
  of its sweep, the service depot's arm tipped 53 degrees toward the pad about arm-pivot.
- **Cameras:** buildings carry two orthographic cameras. `camera-ra-grid` is Red Alert Remastered's view (32 degrees
  above the ground, 128 px per cell) and frames the HD art's RA-grid canvas exactly. `camera-ts-angle` is
  Tiberian Sun's view (30 degrees above the ground, looking north-west). Units carry `camera_ra_grid` (the
  harvester `camera-unit`, the units rebuilt from TS's voxels `camera_mod`, which frames the unit's own canvas
  exactly). The pack's frames are lit from the north-west and above (direction toward the light:
  x -0.451, y 0.702, z -0.551).
- **Meshes:** the buildings were sampled on a 2-unit grid and meshed by marching cubes, with every vertex
  coloured by the building's materials. The MCV's parts are exact solids cut from their planes. The Titan's and
  Wolverine's parts are separate meshes under their own nodes, so the walk can move them. The units rebuilt from
  TS's voxels are exact: each voxel section's boxes, subdivided so the vertex colours carry TS's colours.

## Credits

Tiberian Sun and its designs: Westwood Studios / Electronic Arts. Models built from Tiberian Sun's sprites and
voxels by gibbo101 for [Tiberian Factions](https://github.com/gibbo101/cnc-ra-tiberian-factions).
