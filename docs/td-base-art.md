# TD art read from the base game

**Status:** Design. Six theatres, TD art and TD maps from the base game built and tested on the desktop and the Deck, LAN included; next release.

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
- Paths are never normalised: a frame or tile name containing `..\` finds nothing.
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

Staging applies this to the build (`scripts/td_base_art.py`).

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

## The build step

`scripts/td_base_art.py` runs at staging (`stage_asset_packs.py`, after `share_tileset_zips.py`). A
TD tile whose every frame is byte for byte a frame of a ZIP in `TEXTURES_TD_SRGB.MEG` (matched by
the frame's and its `.meta`'s CRC and size) moves into `RA_VFX`, with its frames naming the base
game's; `RA_VFX` is re-rooted at the texture root, its own frames gaining their old root, with an
opener per ZIP folder (a loose frame folder, such as the rally-point dots, needs none). A TD ZIP no
frame names any more stays out of the build: 89 TD tile names and 78 ZIPs, 126 MB, on this build.
A tile with frames of its own (`TDFLAME-*`, half of `TDMLRS`) keeps its ZIP. The source tree is
unchanged. TD buildings (yard, power plant, Hand of Nod and its build-up), the Nod MCV and the
rocket soldier's missile draw from the base game, and RA's own effects in `RA_VFX` (the frag
explosions) still draw.

**Open:** load time and memory on the Deck, measured.

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
  each TD theatre's row in `Theaters[]` (`const.cpp`) gives it from RA temperate's mix.
- **Classic data.** A TD template's game data (size, land type per icon) is TD's own iconset from
  `DESERT.MIX`, `TEMPERAT.MIX` or `WINTER.MIX`, converted to RA's format with TD's land types and
  packed in `TFASSETS.MIX` as `TD<name>.DES`, `.TEM` or `.WIN`; a river template's water is
  `LAND_RIVER`. RA's objects on a TD theatre (trees, bibs, smudges) use RA temperate's classic
  data and palette (`TF_Base_Theater` and the TD rows of `Theaters[]`).
- **Desert terrain.** TD's desert trees and rocks (`T04`, `T09`, `T18`, `ROCK1` to `ROCK7`) are
  RA terrain types with TD's footprints, loaded on desert from TD's shapes (`<name>.DES`).
- **Memory.** A theatre's tiles cost video memory only on a map that draws them. A TD map in a
  match uses 5,052 MiB on the desktop whether TD's unit art comes from the base game or the mod.

`scripts/td_catalogue_maps.py` writes one map per theatre with every template the DLL has
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
the entry sets neither the lobby's thumbnail nor the loading screen's. For the mod's TD entries the
carrier's hook on ClientG's set-texture call (`0xF604C0`) asks for the base game's own thumbnail
instead: TD map *n*'s for 9*nn*, TD community map *k*'s for 979+*k*, Hastings' D6 for 999, so no
thumbnail ships. Loose copies of both XMLs override CONFIG.MEG's.

InstanceServerG builds its instance list from the base `Instances.xml` before the DLL loads, so a
new entry launches through the carrier (`tf_launcher.cpp`): ClientG sends any entry from 900 up under
Hastings' `D6` entry, whose client entry is removed so it isn't listed, and hands its map file over in
`tf_carrier_mission.txt`; the DLL takes it ahead of `OverrideMapName` on a launch of D6 only, and
the carrier's key reads as the launched entry's, so the loading screen names it.

A skirmish launches through `SkirmishGameManagerClass::Host_Game`, which the carrier hooks by its
callers. A LAN or Steam matchmaking lobby builds its own launch message (`IPCLaunchInstanceMessage`,
its instance name the string at `+0x30`) and sends it straight to the server, so the carrier also
hooks those two sends and renames a 9*nn* entry to D6 in place. The server then tells every client
to load D6; a joiner launched nothing, so D6 reads on every client as the entry its lobby last showed
(the thumbnail hook records it) or it last launched, whichever came later.

Hastings itself is
listed through its own entry, keeping `SCMD6EA.INI`. A placeholder instance can't carry: the server
never starts it. Entry numbers: TD multiplayer map *n* is 9*nn* (Sand Trap, TD's 2, is 902), TD's
community maps 1 to 7 are 980 to 986, and Hastings is 999; a TD map's file is `TFTD<number>.INI`.

`scripts/td_official_maps.py` writes all 34 of TD's skirmish maps into the mod from TD's own
instances, preview data and map files: the entries in `INSTANCES.XML`, the preview data in a loose
`CNCMAPPREVIEWDATA.XML`, and each map converted as `CCDATA/TFTD<number>.INI` (384 KB in all). Video
memory at the menu is unchanged; a TD map in the match costs what any TD-terrain map does.

## Build plan

1. **TD's own classic data and the map pipeline.** Done: TD's templates and desert terrain on the
   TD theatres; `scripts/td_map_to_ra.py` writes a TD map in its own theatre, every template as the
   DLL's TD template; `editor_manifest.py` lists the templates. The native map editor doesn't know
   the TD theatres or the new terrain types yet.
2. **Ore on TD slots.** Ore (`GOLD01-04`, `GEM01-04`) is only in RA's terrain tilesets, so the
   mod ships TD's three terrain tileset XMLs with an empty root and RA's ore tiles added (data
   only). Ore mines are in `RA_VFX` and should draw on any slot.
3. **Blossom trees as terrain.** TD's terrain tilesets carry `SPLIT2` and `SPLIT3`; RA's would get
   those tiles pointing at TD's frames. `STRUCT_TDBLOSSOM` becomes a terrain type seeding Tiberium
   as the ore mine seeds ore. The 151 official-map hybrids (`official-map-hybrids.md`) and
   `td_map_to_ra.py` move their blossom trees from `[STRUCTURES]` to `[TERRAIN]`; their Tiberium
   stays `TIB01`. Its own commit: it touches `bdata.cpp`.
4. **The map list.** Done for TD's 34 skirmish maps (`td_official_maps.py`), thumbnails
   included. The mod's own maps go beside them through the same carrier, on numbers from 900 that
   TD leaves free (911 to 949, for one), each with a thumbnail of its own that the set-texture hook
   must then pass through.

