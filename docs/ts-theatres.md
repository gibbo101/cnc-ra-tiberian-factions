# Tiberian Sun theatres and maps

**Status:** Design, parked. A converter lays TS's multiplayer maps on Red Alert's grid, and probes draw
them with TS's own art. Nothing ships yet.
**Open:** run the tileset video-memory test, which picks the art route; dark notches on rare ramp
shapes and a lake's diamond edge; six maps with a pass the conversion closes; the engine work (theatre
slots 6 and 7, templates, the height rule); an end-to-end map.

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
- **Art:** heights show as TS lights them (`[Lighting]` `Ambient` plus `Level` per level), with ramps
  drawn into the cells and cliffs drawn over them (below). Units draw at their cell, not lifted.
- **Lifted drawing**, units raised on plateaus as in TS, is possible from the DLL (every draw
  position, click and cursor cell goes through it) but needs terrain baked per map, shroud and
  placement remapped and cliff faces as sorted sprites. It is not planned; a test of how the
  launcher's selection boxes and health bars follow a moved draw position would decide it.

## Art

The map should look as TS draws it. Two routes, and the tileset video-memory test (below) picks one.

**TS's own tiles, one piece per RA cell** (`scripts/probes/ts_ground_sample.py`,
`scripts/probes/ts_cliff_sprites_sample.py`, which writes `*_whole_ts_exact.png`):

- **Ground, water, roads and TS's own transitions:** each RA cell is cut from TS's art drawn flat, its
  centre diamond and the quarters of its four corner cells, un-projected (y stretched twice, rotated
  45 degrees).
- **Ramps** are warped back to level: a ramp's diamond and extra image are mapped bilinearly from its
  raised corners (OpenTS's ramp table, corners top, right, bottom, left) lowered 13 pixels per level.
- **Cliffs are objects over the ground**, not ground tiles. A cell is cliff when its tileset is named
  for cliffs, or it is rock with an extra image. Each piece keeps its plateau top on its own cells and
  hangs its face south, at TS's height or half of it.
- **Firestorm's tilesets first:** `expand01.mix`'s `TEMPERAT.INI` and `ISOTEMP.MIX` replace TS's and add
  tiles 960 and up (crystal, swamp, blue mold), which TS's own multiplayer maps use.
- **Cost:** across the 23 maps that fit, about 35,000 different Temperate pieces with light left to the
  engine (ground 6,103, water 8,728, ramps 17,317, roads 3,206), and 64,637 with each map's lighting
  baked in; Snow 31,391 with lighting. This works only if the launcher loads the tiles a map draws.
- **Flaws:** small dark notches from rare ramp shapes, a lake's diamond edge, and softness at 128 pixels
  a cell (Lanczos; an ESRGAN upscale needs a torch install).

**A square autotile set made from TS's art** (`scripts/probes/ts_autotile_sample.py`), if whole
tilesets load:

- **Ground textures** from TS's tiles, repeated on their lattice, stretched to top-down and cut on
  lattice points, so they tile seamlessly at 48 source pixels to the RA cell. TS Temperate has a single
  clear tile; mirrored centre diamonds give four variants.
- **Transitions** per corner: a class covers the cell where the corners' bilinear field, plus noise
  with a period of one cell, passes one half, so any two pieces meet. Classes go by tile family (TS's
  sand and green tiles have rough's land type).
- **Cliffs and ramps** step where each level's corner field passes one half, steep for cliffs and
  gentle at ramps, lit from TS's north-west. Cliffs drawn this way lose TS's look; TS's cliff objects
  above go over this ground too.

A 14 by 10 cell region of Tiers of Sorrow takes 84 pieces.

**A curated TS tileset for new maps** is the third piece: the ground, transition, ramp and cliff pieces
a mapper paints with, small enough for either route. It needs map editor support.

## The tileset video-memory test

The launcher holds every texture it draws in video memory (`sprite-memory.md`). Whether a terrain
tileset costs memory whole or per tile drawn is untested.

`scripts/probes/tileset_vram_probe.py` builds `TFTilesetProbe`, a data-only Red Alert mod: RA's own
`RA_TERRAIN_TEMPERATE.XML` from `CONFIG.MEG` (2,053 tiles) plus 4,000 tiles no map uses, each a loose
256 by 256 DXT5 frame (334 MiB).

1. Copy it into its own folder, `Mods/Red_Alert/TFTilesetProbe/`, with the game closed.
2. Disable Tiberian Factions, which overrides the same tileset.
3. Play one RA Temperate skirmish map with the probe off, then on, from the same view, and read
   video memory in the match (`nvidia-smi --query-gpu=memory.used` on the desktop).

About 330 MiB more means whole tilesets load and the autotile route stands; no change means the
launcher loads only drawn tiles and TS's own tiles can be used.

## Engine plan

- **Two theatres**, TS Temperate and TS Snow, in the launcher's slots 6 and 7 after TD's three
  (`td-base-art.md`), each with its own terrain tileset.
- **DLL templates** for the pieces. The launcher draws a cell by the template name and icon number the
  DLL exports for it, and RA templates hold up to 256 icons.
- **Terrain frames can be loose DDS:** the mod already ships `T17.TEM`'s frames that way.
- **The add-on:** theatres, templates and the height rule are DLL code in the mod; the art, tileset
  XML, classic data and converted maps can be an asset pack.

## Red Alert 2

RA2 is the same engine: the same tile files, `IsoMapPack5`, map INI and autotiling. `ts_map.py` reads
a tile's diamond size from its file (60x30 in RA2), so RA2's theatres would convert the same way, at
60 source pixels to the RA cell. RA2's maps are larger, so fewer fit.
