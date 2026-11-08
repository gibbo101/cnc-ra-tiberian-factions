# TD art read from the base game

**Status:** Design; shipped in 5.6.0. Six theatres, TD art and TD maps from the base game, tested on the desktop and the
Deck, LAN included. The opener tiles need the splash preload, which the DLL keeps on (`sprite-memory.md`).

The mod copies TD's unit, building and effect ZIPs out of `TEXTURES_TD_SRGB.MEG` into
`Data/ART/TEXTURES/SRGB/RED_ALERT/`, renamed with a `TD` prefix. Every player already has those
files. This doc is how a Red Alert tileset reads them from the base game instead.

## How it works

How the launcher finds a tile's art, and the opener tile that makes a Red Alert tileset read the base game's
ZIP, are in the field manual's
[TD art from the base game](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-art-from-the-base-game.md#the-mechanism-an-opener-tile).
Our tiles keep the names the DLL asks for (`TDMTNK`) and point at the base game's frame names (`mtnk-0000.tga`,
not our `tdmtnk-0000.tga`); the GDI Medium Tank and MCV were the house-colour and turret check.

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

- **The launcher's slots.** The mod's `GameConstants_Mod.xml` gives `CNCRATheaterTilesets` six slots, TD's three
  in 3 to 5 (an empty slot is `RA_Terrain_Temperate`), as in the field manual's
  [TD theatres in Red Alert](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-theatres-in-red-alert.md#the-launcher-side-more-slots).
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
- **Desert terrain.** TD's desert trees and rocks are RA terrain types loaded from TD's shapes
  (`<name>.DES`), as in the field manual's
  [TD theatres in Red Alert](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-theatres-in-red-alert.md#the-dll-side-matching-theatres),
  step 6.
- **Memory.** The readings (Docklands, with and without 163 unused desert tiles; a TD map with TD's art from either
  source) and the open question of whole-or-per-tile cost are in the field manual's
  [Adding a theatre of your own](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/maps-and-lobby/custom-theatres.md#whats-open-video-memory)
  and [TD art from the base game](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-art-from-the-base-game.md#how-it-was-verified).

`scripts/td_catalogue_maps.py` writes one map per theatre with every template the DLL has
for it placed once; all six draw every template, and units spawn. Two dark cells are EA's data: RA
interior's `ARRO0003` is a dark tile, and RA temperate's `SH42` icon 3 points at a near-black stray
frame outside the shore's shape.

Terrain tilesets open no ZIP through an opener tile, so the mod's own terrain art (`TIB01`) stays a
ZIP under its RA root (the field manual's
[TD art from the base game](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-art-from-the-base-game.md#traps),
traps).

## TD maps in the Official list

Listing a map is data, and starting one needs a carrier entry the instance server knows: see the field manual's
[New maps in the skirmish Official list](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/maps-and-lobby/new-maps-in-the-skirmish-list.md#starting-it-launch-under-an-entry-the-server-knows),
which has the entries, preview data, thumbnails, hooks and addresses. Each entry also needs its own `Mission`
number. `PreviewLoadingTextureName` on an entry set neither the lobby's thumbnail nor the loading screen's.

Entry numbers: TD multiplayer map *n* is 9*nn* (Sand Trap, TD's 2, is 902), TD's community maps 1 to 7 are 980 to
986, and Hastings is 999. The set-texture hook asks for the base game's own thumbnail by that number: TD map *n*'s
for 9*nn*, TD community map *k*'s for 979+*k*, Hastings' D6 for 999, so no thumbnail ships.

TF's carrier is in `tf_launcher.cpp`. InstanceServerG reads the base `Instances.xml` before the DLL loads.
ClientG sends any entry from 900 up under Hastings' `D6`, whose own client entry is removed so it isn't listed
twice; the map file goes over in `tf_carrier_mission.txt`. The LAN and Steam lobby hooks rename only a 9*nn*
entry to D6. The thumbnail hook also records the entry the lobby last showed, which is how a joiner reads D6.
Hastings is listed again as 999, keeping `SCMD6EA.INI`, and a TD map's file is `TFTD<number>.INI`.

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

