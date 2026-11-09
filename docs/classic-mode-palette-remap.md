# Classic-mode palette remap (TD sprites + Obelisk laser)

**Status:** Reference. Classic graphics mode is unsupported: the mod's TD and TS content has no
classic art, so `GameConstants_Mod.xml` locks the mode out. `scripts/build_tfassets.sh` still
palette-remaps each TD SHP it packs into TFASSETS.MIX; that needs no attention, and new entities
need no classic SHPs. The Obelisk beam indices (`techno.cpp`, `0x7D/0x7F → 0xD8/0xE6`) also colour
the HD beam and must stay.

## The problem

TF ships its TD-sourced SHPs in `TFASSETS.MIX`. Drawn as they are, their colours are wrong and their house
colours never follow the player: see the field manual's
[HD-only mods](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/getting-started/hd-only-mods.md#porting-tds-classic-art-why-not-support-classic-mode-as-well),
porting TD's classic art.

Reilsss's CnCinRA mod and EMC never solved this; their own changelog lists it as a permanent known bug. TF's
remap works because it owns both the DLL and an offline asset-build pipeline.

## The remap rule

The rule (0 kept, 176–191 moved onto 80–95, every other index to the nearest RA colour by Euclidean RGB) is in
the field manual's
[HD-only mods](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/getting-started/hd-only-mods.md#porting-tds-classic-art-why-not-support-classic-mode-as-well).
It was checked against TD `CONST.CPP` (`RemapRed`, its 176..191 row at line 325; `DISPLAY.CPP:248`) and RA's
`PALETTE.CPS` row 0 (`init.cpp` `Init_Color_Remaps`).

## The tooling (offline, pack-time — no runtime cost)

- **`scripts/ra_mix_extract.py`** — reads RA's encrypted/nested `REDALERT.MIX` to
  pull `TEMPERAT.PAL` (`mix-file-format.md`).
- **`scripts/shptools.py`** — Westwood LCW (Format80) codec + XOR-delta SHP
  decoder (ported from VC `lcw.cpp` / `keyframe.cpp` / `xordelta.cpp`),
  `build_remap_lut()`, and `remap` CLI. Every frame is decoded to a full bitmap,
  remapped, and re-encoded as a **standalone Format80 keyframe** (no delta chains
  in output). `shptools.py` self-tests the LCW round-trip.
- **`scripts/build_tfassets.sh`** — extract each TD SHP from `CONQUER.MIX`,
  remap via `shptools.py`, repack `TFASSETS.MIX`. Adding a new separated
  building = add a line here; it's auto-remapped.

## Drawn colours (the Obelisk laser)

The Obelisk laser is a drawn line, not a SHP, so it bypasses `TFASSETS.MIX`; its indices and their RA
replacements are in the field manual's
[HD-only mods](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/getting-started/hd-only-mods.md#porting-tds-classic-art-why-not-support-classic-mode-as-well).
`redalert/techno.cpp` carries the remapped values, which both the classic `LogicPage` draw and the launcher's
line intercept (`DLL_Draw_Line_Intercept`) use. For any new TD-sourced drawn colour, take the RA index from the
LUT in `shptools.py`, never the raw TD index.

## Verifying

`build_tfassets.sh` rebuilds `TFASSETS.MIX`; deploy with `deploy.sh`. Classic graphics can be checked in game
only with `CNCDisableLegacyGraphicsOption` taken out of `GameConstants_Mod.xml`: TD buildings then render correct
colours with house colour following the player, and the Obelisk laser is red. Remastered mode draws the HD
tilesets, not these SHPs, but its Obelisk beam is red only through the `techno.cpp` indices.
