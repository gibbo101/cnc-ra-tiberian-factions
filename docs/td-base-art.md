# TD art read from the base game

**Status:** Design. Six theatres and TD art from the base game proven on the desktop; nothing ships yet.
**Open:** the build plan below, an RA_VFX effects check, a Deck performance pass.

The mod copies TD's unit, building and effect ZIPs out of `TEXTURES_TD_SRGB.MEG` into
`Data/ART/TEXTURES/SRGB/RED_ALERT/`, renamed with a `TD` prefix. Every player already has those
files. This doc is how a Red Alert tileset reads them from the base game instead.

## How the launcher finds a tile's art

- `Data/MEGAFILES.XML` mounts every texture MEG at start-up, `TEXTURES_TD_SRGB.MEG` included,
  whichever game is played.
- `CNCRendererClass::Recreate_Tile_Maps` builds the tile maps from a fixed list. With Red Alert
  running that list is `RA_Units`, `RA_Structures`, `RA_VFX`, `RA_RadarMap`, `RA_Terrain_Shroud`,
  `Common_VFX`, `Common_UI` and `Common_Misc`. `TD_Units` and the other TD tilesets never load in RA.
- An object's tile is found by name in any of the world tilesets: a unit's tiles in
  `RA_Structures` draw normally.
- A tile opens `<RootTexturePath>\<tile name>.zip`. A tile name may hold a path (`SUB\TDAPC` opens
  `UNITS\SUB\TDAPC.ZIP`), and a frame `<folder>\<file>.tga` reads from the ZIP opened as `<folder>`.
- Paths are never normalised: a frame or tile name containing `..\` finds nothing (frog card).
- `Common_UI` and `RA_RadarMap` are not world tilesets: a unit tile placed in them draws as a white
  square, whatever ZIP it reads.

## The mechanism

A world tileset with an empty `RootTexturePath` reaches both trees:

```xml
<TilesetTypeClass name="RA_VFX">
    <RootTexturePath></RootTexturePath>
    <Tiles>
        <Tile><Key><Name>Tiberian_Dawn\Units\MTNK</Name><Shape>0</Shape></Key>
              <Value><Frames><Frame>Tiberian_Dawn\Units\mtnk\mtnk-0000.tga</Frame></Frames></Value></Tile>
        <Tile><Key><Name>TDMTNK</Name><Shape>0</Shape></Key>
              <Value><Frames><Frame>Tiberian_Dawn\Units\mtnk\mtnk-0000.tga</Frame></Frames></Value></Tile>
        ...
```

- The first tile is an opener: its name makes the launcher open the base game's `MTNK.ZIP`. It is
  never drawn.
- `TDMTNK`, the name the DLL asks for, keeps its own tiles. Their frames point into the opened ZIP
  by the base game's frame names (`mtnk-0000.tga`), not ours (`tdmtnk-0000.tga`).
- The tileset's own art moves with it: every frame gains the old root (`Red_Alert\VFX\120mm\...`),
  and each ZIP folder it names gets an opener (`Red_Alert\VFX\120MM`).
- House colours, shading and turrets draw as they do from our copies (GDI Medium Tank, GDI MCV).

`scripts/probes/td_empty_root_probe.py` applies this to a deployed build. `td_base_ref_probe.py`,
`td_common_root_probe.py` and `td_gateway_probe.py` are the probes that ruled out `..\` paths and
the non-world tilesets.

## What it can replace

Measured on the 5.5.0 build:

| Art | Files | Size | From the base game |
|---|---|---|---|
| `TD*` ZIPs byte-identical to a base ZIP | 76 | 129 MB | yes |
| `TD*` ZIPs whose frames are all in base ZIPs (`TDGFACT`, `TDGMCV`, `TDMLRS`...) | about 10 | about 35 MB | yes |
| `TD*` ZIPs partly ours (`TDFLAME-*`, half their frames) | 8 | 1.6 MB | the base half |
| `TD*` ZIPs that are ours (`TDCA`, `TDDD`, `TDPT`, subs, gates, turrets, `TDBOAT`...) | about 35 | about 50 MB | no |
| `BuildIcon_TD*` cameos | 157 | 49 MB | no: each carries the owner badge (`cameo-dds.md` shrinks them) |

The build already shares frames between tiles (`TDGFACT` and `TDNFACT` read `tdfact\`), so the
shipped saving is the base-identical part of the 169 MB of `TD*` ZIPs in the build.

## Open

- **Build step.** For TD's units, buildings and effects alike: generate the empty-rooted tilesets
  and their openers from the frame-to-base map (the md5 matching in `scripts/probes/td_compare.py`),
  and stop staging the replaced ZIPs.
- **RA_VFX effects.** The probe re-rooted `RA_VFX` but no combat ran, so RA's own effects are
  unchecked. A tileset with fewer of its own tiles is the lower-risk host.
- **Performance.** The same ZIPs open from a MEG instead of a loose file. Load time and memory on
  the Deck need a measured pass.

## Six theatres

Red Alert runs six theatres: its own three and TD's three, each drawing its own terrain tileset
from the base game.

- **The launcher's slots.** `GameConstants.xml`'s `CNCRATheaterTilesets` names the terrain tileset
  for each theatre number the DLL reports (an empty entry is `RA_Terrain_Temperate`). The mod's
  `GameConstants_Mod.xml` replaces it with `overwrite="true"`: slots 0 to 2 are RA's, 3 to 5
  `TD_Terrain_Desert`, `TD_Terrain_Temperate` and `TD_Terrain_Winter`. TD's terrain tilesets are
  loaded in RA too.
- **The DLL's theatres.** `TheaterType` carries `THEATER_DESERT`, `THEATER_TDTEMPERATE` and
  `THEATER_WINTER` (3 to 5, the slot numbers), and a map names them `Theater=Desert`, `TDTemperate`
  or `Winter`. TD's 210 drawn templates are DLL templates `TD<name>` (ids 401 to 610, written by
  `scripts/td_templates.py`), each flagged for the TD theatres whose tileset draws it, and load
  only there (`TemplateTypeClass::Init`). On a TD theatre `Get_Template_Info` sends TD's own name
  (`TDSH17` as `SH17`), and trees keep TD's names (`T01`).
- **What it gives.** Terrain, trees, bibs, smudges and the radar all come from TD's own tileset, as
  in TD. Smudges need the DLL's theatre to have the classic shape (`Get_Image_Data`), which
  `TF_Base_Theater` gives every TD theatre.
- **Classic data.** A TD template's game data (size, land type per icon) is TD's own iconset from
  `DESERT.MIX`, `TEMPERAT.MIX` or `WINTER.MIX`, converted to RA's format with TD's land types and
  packed in `TFASSETS.MIX` as `TD<name>.DES`, `.TEM` or `.WIN`; a river template's water is
  `LAND_RIVER`. RA's objects on a TD theatre (trees, bibs, smudges) use RA temperate's classic
  data and palette (`TF_Base_Theater`).
- **Desert terrain.** TD's desert trees and rocks (`T04`, `T09`, `T18`, `ROCK1` to `ROCK7`) are
  RA terrain types with TD's footprints, loaded on desert from TD's shapes (`<name>.DES`).
- **Memory.** Video memory on the desktop, one match each: Docklands 4796 MiB with the stock
  interior tileset and 4812 MiB with 163 desert tiles in it. A theatre's tiles cost memory only on a
  map that draws them.

`scripts/probes/td_catalogue_maps.py` writes one map per theatre with every template the DLL has
for it placed once; all six draw every template, and units spawn. Two dark cells are EA's data: RA
interior's `ARRO0003` is a dark tile, and RA temperate's `SH42` icon 3 points at a near-black stray
frame outside the shore's shape.

Terrain tilesets open no ZIP through an opener tile, so the mod's own terrain art (`TIB01`) stays a
ZIP under its RA root.

## TD maps in the Official list

The skirmish lobby's Official list shows every `INSTANCES.XML` entry on RA's multiplayer base
variant, whatever its name; a TD entry set to Red Alert is not listed. New entries are named like
RA's own (`Mobius_Red_Alert_Multiplayer_<n>_Map`). One needs its text, a `Mission` number, a
`CNCMAPPREVIEWDATA.XML` entry on RA's 128-cell grid with one waypoint per player, and a thumbnail
named after the entry (`MOBIUS_RED_ALERT_MULTIPLAYER_<n>_MAP.DDS`); `PreviewLoadingTextureName` on
the entry sets neither the lobby's thumbnail nor the loading screen's. Loose copies of both XMLs
override CONFIG.MEG's.

InstanceServerG builds its instance list from the base `Instances.xml` before the DLL loads, so a
new entry launches through the carrier (`tf_launcher.cpp`, dev builds): ClientG sends it under
Hastings' `D6` entry, whose client entry is removed so it isn't listed, and hands its map file over in
`tf_carrier_mission.txt`; the DLL takes the handoff ahead of the carrier's `OverrideMapName`, and
the carrier's key reads as the launched entry's, so the loading screen names it. Hastings itself is
listed through its own entry, keeping `SCMD6EA.INI`. A placeholder instance can't carry: the server
never starts it. Entry numbers: TD multiplayer map *n* is 9*nn* (Sand Trap, TD's 2, is 902), TD's
community maps 1 to 7 are 980 to 986, and Hastings is 999; a TD map's file is `TFTD<number>.INI`.

`scripts/probes/td_official_list_probe.py` sets this up on a deployed build for TD's Sand Trap
(entry 902, played on the desert theatre) and Hastings (999). Video memory at the menu is
unchanged; a TD map in the match costs what any TD-terrain map does.

## Build plan

1. **TD's own classic data and the map pipeline.** Done: TD's templates and desert terrain on the
   TD theatres; `scripts/td_map_to_ra.py` writes a TD map in its own theatre, every template as the
   DLL's TD template; `editor_manifest.py` lists the templates. The native map editor doesn't know
   the TD theatres or the new terrain types yet.
2. **Ore on TD slots.** Ore (`GOLD01-04`, `GEM01-04`) is only in RA's terrain tilesets, so the
   mod ships TD's three terrain tileset XMLs with an empty root and RA's ore tiles added (data
   only). Ore mines are in `RA_VFX` and should draw on any slot.
3. **Blossom trees as terrain.** TD's terrain tilesets carry `SPLIT2` and `SPLIT3`; RA's get those
   tiles pointing at TD's frames, as the winter trees proved. `STRUCT_TDBLOSSOM` becomes a terrain
   type seeding Tiberium as the ore mine seeds ore. The 151 official-map hybrids
   (`official-map-hybrids.md`), the transcoder and the parked maps move their blossom trees from
   `[STRUCTURES]` to `[TERRAIN]`; their Tiberium stays `TIB01`. Its own commit: it touches
   `bdata.cpp`.
4. **The map list.** TD's own skirmish maps in RA's official list, read from TD's files, and the
   mod's maps beside them.

