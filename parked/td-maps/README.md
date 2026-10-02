# Parked: the Tiberian Dawn maps and their terrain

The 31 converted Tiberian Dawn skirmish maps and the TD terrain they need sit here, outside the
mod. Nothing in this folder is staged into the build. They are meant to come back as their own
Workshop item, so players who want the maps can add them and everyone else keeps the lower
memory use.

## What is here

| Path | What it is |
|---|---|
| `CustomMaps/` | The 31 maps as `mpr`+`tga`+`json` triplets under synthetic names `UGC_F1BE0000000000NN_00000000000000NN_MAPDATA.*` (`scripts/build_map_bundle.py`). |
| `Data/ART/TEXTURES/SRGB/RED_ALERT/TERRAIN/TEMPERATE/` | HD art for the TD temperate tiles (`TD*`), the TD winter tiles (`TDW*`) and the snowy trees for winter maps (`TDWT*`). |
| `Data/ART/TEXTURES/SRGB/RED_ALERT/TERRAIN/INTERIOR/` | HD art for the TD desert tiles, plus the desert overrides of Red Alert's interior art (`CLEAR1.INT`, `ARRO0001-4.INT`, `BIB1-3.ZIP`: desert sand, water, coast, river, rock and bibs; `scripts/build_desert_radar_palette.py`). `TDBIB1-3.ZIP` are unused. |
| `tileset-fragments/` | The `<Tile>` blocks cut from the mod's `RA_TERRAIN_TEMPERATE.XML` and `RA_TERRAIN_INTERIOR.XML`. Each file is the content that goes back between the empty `TF_TD_TILES` / `TF_WINTER_TREES` markers still in those XMLs. |

The mod keeps everything the rest of the game needs: Tiberium (`TIB01`) in every theatre, the
blossom trees (a building, `STRUCT_TDBLOSSOM`), the 151 official maps in `CCDATA/`, and the TD
template types in the DLL. The classic iconsets in `TFASSETS.MIX` stay too; HD mode never draws
them.

## How the DLL behaves without them

`TF_TD_MAPS` (`redalert/defines.h`) is 0: the DLL installs no maps, deletes the 31 synthetic map
names from `Local_Custom_Maps/Red_Alert/` (copies an earlier version installed), and ignores the
`[TFTDTiles]` section, so a converted map that turns up anyway loads its vanilla-safe `[MapPack]`.

## Bringing them back inside the mod

1. Move `CustomMaps/` and the `TERRAIN` folders back under `resources/remaster_mods/Vanilla_RA/`.
2. Paste each fragment back between its markers in the matching tileset XML.
3. Build with `TF_TD_MAPS` at 1.

Rerunning `scripts/build_td_tiles.py`, `scripts/build_winter_trees.py` or
`scripts/build_map_bundle.py` also writes into `resources/` again, not here.

## As a separate Workshop item

A second mod cannot simply ship its own copy of the tileset XMLs: the launcher takes one copy of
each file, last in load order wins, so the add-on's copy would have to carry everything in the
mod's copy as well. Work that out, and how the DLL learns where the add-on's `CustomMaps/` is,
before publishing it.
