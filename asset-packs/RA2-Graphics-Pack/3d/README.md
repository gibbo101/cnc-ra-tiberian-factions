# RA2 3D models

The 3D models of the RA2 tanks' HD art, rebuilt from Red Alert 2's own voxels. Each tank's HD art is rendered from
its model here. The game does not use this folder: it is here for anyone who wants the models themselves, to render
new angles or to use them in another engine.

All files are glTF 2.0 binary (`.glb`), which Blender, Godot and most engines open.

| File | Red Alert 2 | In Tiberian Factions | Parts |
|---|---|---|---|
| `apocalypse-tank.glb` | APOC | R2APOC | hull; turret (with the twin cannons and tusk launchers) |
| `prism-tank.glb` | SREF | R2PRIS | hull; turret (the prism) |

## Conventions

- **Axes:** x east, y up, z south (toward the Red Alert camera). The tanks face east (+x) with their position at the
  origin, on the ground. For a sprite in 32 facings (0 north, 8 west, 16 south, 24 east), facing f is the model
  turned (f - 24) x 11.25 degrees counter-clockwise seen from above.
- **Scale:** 1.0 = one cell (128 px on the Red Alert Remastered grid).
- **Meshes:** exact: each voxel section's boxes, cut at 45 degrees along its convex edges and subdivided so the
  vertex colours carry RA2's colours.
- **Colours:** vertex colours. COLOR_0 holds the materials' own colours (albedo: no light or shadow). COLOR_1 is the
  house-colour mask: white where the house colour goes.
- **Camera:** `camera_mod`, Red Alert Remastered's view (orthographic, 32 degrees above the ground, looking north),
  frames the tank's own canvas exactly.

## Credits

Red Alert 2 and its designs: Westwood Studios / Electronic Arts. Models built from Red Alert 2's voxels by gibbo101 for
[Tiberian Factions](https://github.com/gibbo101/cnc-ra-tiberian-factions).
