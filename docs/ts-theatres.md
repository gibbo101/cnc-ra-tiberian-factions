# Tiberian Sun theatres and maps

**Status:** Design. A converter lays TS's multiplayer maps on Red Alert's grid; an art sample shows the
square TS Temperate tileset. Nothing ships yet.
**Open:** six maps with a pass the conversion closes; the art's upscale and tuning; the engine work
(theatre slots, templates, the height rule); an end-to-end map.

Tiberian Sun's Temperate and Snow theatres as two more Red Alert theatres, with TS's own maps converted
onto them. A mod that ports Red Alert and Tiberian Dawn tilesets into TS's isometric engine
(*The Dawn of the Tiberium Age*) remade those maps by hand; this goes the other way, by script.

## Geometry

TS's cells are squares like RA's: the isometric look is TS's camera, rotated 45 degrees and squashed
2:1. A TS map of `Size=W,H` holds about 2WH cells, and a cell `(x, y)` sits on screen at
`(x - y, x + y)` in half-diamond steps.

- **Orientation:** TS's screen up is RA's up, so a map reads as players know it and TS objects keep
  the camera the mod already renders them in. TS's cell axes become RA's diagonals.
- **Scale:** one RA cell per TS screen diamond, so each RA cell holds two TS cells: its centre cell and
  a quarter of each of four corner cells, which are the centre's four side neighbours. Distances
  shrink to 71%; TS buildings keep their own footprints, so bases are relatively larger.
- **Fit:** RA's map is at most 126 cells a side (`megamaps-feasibility.md`). The RA map is the TS
  map's `LocalSize` in diamonds, plus the rows a raised plateau needs.

| Mapping | RA cells per TS cell | TS multiplayer maps that fit (of 39) |
|---|---|---|
| Rotated, one RA cell per TS diamond | 1/2 | 23 |
| Rotated, true scale | 1 | 6 |
| Unrotated diamond | 1 | 2 |
| Rotated, TS's screen shape kept | 1/2 | 9 |

The 16 that don't fit are the 6 to 8 player maps, 130 to 160 diamonds wide.

## The converter

`scripts/ts_map_to_ra.py` reads a TS map from the installed game (`scripts/ts_map.py`: the map INI,
`IsoMapPack5` through `scripts/lzo1x.py`, `OverlayPack`, the theatre's tileset INI and tile files)
and writes, per map, a JSON of the RA grid and a preview image:

- **Land per cell** from the centre TS cell's tile, through TS's control-colour table
  (`IsometricTileTypeClass::Land_Type`): clear, rough, road, water, beach, rock. Ice reads as clear,
  tunnels and railways as rock and road.
- **Height and ramp per cell**, the centre cell's level and ramp type.
- **Closed diagonals.** RA's pathfinding cuts corners, and a TS cliff along a TS axis crosses RA's
  grid diagonally. Where two blocked cells touch only diagonally across a blocked TS corner cell, the
  more enclosed of the two open cells is blocked too, so the line becomes a staircase.
- **Objects:** start points, Tiberium and veins, walls, bridges, trees and structures, each on the RA
  cell its TS cell's centre falls in. TS's cell numbers are `y * 1000 + x`; overlay packs index
  `x + 512 * y`.
- **A route check.** The shortest land route between every pair of start points, in TS with TS's
  movement rules and on the RA grid with the same rules, both in TS cell widths. On 33 maps the RA
  route is 0.93 to 1.04 times TS's; nowhere is there a shortcut TS lacks. Grand Canyon, Crater,
  Stormy Valley, Tread Lightly, Night of the Mutants and River Raid have a pass the conversion
  closes, making some routes 1.14 to 3.9 times longer.

Opening a water cell wherever two corner cells are dry, as fords, opens shortcuts on four maps and
loses routes on one: rejected.

## Height

Height is a TS-map feature only: a converted map carries a height and ramp per cell, and the DLL's
height rules apply only on a map that has them.

- **Movement:** TS refuses a step between two cells unless they are level, or one level apart with the
  lower cell a ramp (`FootClass::Can_Reach`). A height step is a wall even on clear ground. The DLL
  applies the same rule on a TS map, so plateau edges hold without blocking cells; the route check
  above assumes it.
- **Art:** heights show as TS lights them (`[Lighting]` `Ambient` plus `Level` per level) and as
  cliffs and ramps drawn into the cells, the way RA's own cliffs are. Units draw at their cell, not
  lifted.
- **Lifted drawing**, units raised on plateaus as in TS, is possible from the DLL (every draw
  position, click and cursor cell goes through it) but needs terrain baked per map, shroud and
  placement remapped and cliff faces as sorted sprites. It is not planned; a test of how the
  launcher's selection boxes and health bars follow a moved draw position would decide it.

## Art

**Not TS's tiles cell by cell.** An RA cell's flat TS art depends on five TS cells' tiles and heights;
across the 23 maps that fit that is 64,637 different Temperate cells and 31,391 Snow, too many for a
tileset. `scripts/probes/ts_ground_sample.py` draws a region that way and counts them.

**A square autotile set made from TS's art** (`scripts/probes/ts_autotile_sample.py`):

- **Ground textures** from TS's own tiles: a tile repeated on its lattice, stretched to top-down and
  cut on lattice points tiles seamlessly, 48 source pixels to the RA cell. Clear, rough, sand, green,
  pavement and water. TS Temperate has a single clear tile; mirrored centre diamonds give four
  variants.
- **Transitions** per corner: a class covers the cell where the corners' bilinear field, plus noise
  with a period of one cell, passes one half. An edge then depends only on its two corners, so any
  two pieces meet. Classes are painted by tile family (TS's sand and green tiles have rough's land
  type) and layered over clear.
- **Cliffs and ramps** from the same corner fields: each height level steps where its field passes
  one half, steeply for cliffs and gently where a corner is a ramp, then is lit from TS's north-west
  with rock on the steep band. The face falls in the cells between high and low corners, which are
  TS's impassable cliff cells.

A 14 by 10 cell region of Tiers of Sorrow takes 84 pieces. TS's clear tile repeats visibly at 128
pixels a cell, and the textures need a better upscale than Lanczos.

## Engine plan

- **Two theatres**, TS Temperate and TS Snow, in the launcher's slots after TD's three, each with its
  own terrain tileset.
- **DLL templates** for the autotile pieces. The launcher draws a cell by the name and icon number the
  DLL exports for it, and RA templates hold up to 256 icons.
- **The add-on:** theatres, templates and the height rule are DLL code in the mod; the art, tileset
  XML, classic data and converted maps can be an asset pack.
- **To measure first:** whether the launcher takes slots past TD's, whether a terrain tileset costs
  video memory whole or per used tile, and whether terrain frames can be DDS.

## Red Alert 2

RA2 is the same engine: the same tile files, `IsoMapPack5`, map INI and autotiling. `ts_map.py` reads
a tile's diamond size from its file (60x30 in RA2), so RA2's theatres would convert the same way, at
60 source pixels to the RA cell. RA2's maps are larger, so fewer fit.
