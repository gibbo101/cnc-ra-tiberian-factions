# Classic-mode palette remap (TD sprites + Obelisk laser)

> ⚠️ **HISTORICAL — classic graphics mode is DROPPED.** Once the TD theatre tilesets
> were added there is no classic art path for the mod's content, so classic renders
> broken and is unsupported (HD-only). The SHP palette-remap described below no longer
> ships/matters for new work — do **not** palette-remap or ship classic SHPs for new
> entities. **Exception that is still live:** the Obelisk-laser index fix (§ below,
> `techno.cpp` `0x7D/0x7F → 0xD8/0xE6`) also feeds the **HD** launcher line-intercept
> (both modes draw the beam through RA's palette), so that one value is still needed.
> Kept as a record of the technique + the LUT + the laser fix. See memory
> `feedback-classic-graphics-unsupported`.

**Status (historical): SOLVED and shipped 2026-05-28**, later dropped when the TD
tilesets landed. It fixed the classic-graphics-mode palette mismatch that earlier notes
called "deferred", "~95% right", or unavoidable.

## The problem

TD-sourced SHPs ship in `TFASSETS.MIX` for classic-graphics-mode rendering. In
classic mode the engine draws them through **RA's** palette, but the pixels carry
**TD's** palette indices — so colours were wrong, and worst of all the TD
house-colour pixels never followed the player (they sit in TD's remap range,
which RA's engine doesn't recolour).

Reilsss's CnCinRA mod and EMC never solved this — their own changelog lists it as
a permanent known bug. We can, because we own both the DLL and an offline
asset-build pipeline.

## The remap rule

Verified against TD `CONST.CPP` (rows 306/420, `DISPLAY.CPP:248`) and RA's
`PALETTE.CPS` row 0 (`init.cpp` `Init_Color_Remaps`):

| | House-colour "unity" range | Action |
|---|---|---|
| TD | **176–191** (0xB0–0xBF) | map → RA 80–95 *positionally* (`i → i-96`) |
| RA | **80–95** (0x50–0x5F) | RA engine recolours these per player |

- **Index 0** stays 0 (transparent).
- **Every other index** → closest-colour match (Euclidean RGB) from TD's
  `TEMPERAT.PAL` into RA's `TEMPERAT.PAL`, **excluding** 0 and 80–95 as targets
  (so a non-house pixel can never accidentally become house-coloured).

## The tooling (offline, pack-time — no runtime cost)

- **`scripts/ra_mix_extract.py`** — reads RA's encrypted/nested `REDALERT.MIX` to
  pull `TEMPERAT.PAL`. See the encrypted-mix-reader notes; WW pubkey →
  Blowfish → recursive container search.
- **`scripts/shptools.py`** — Westwood LCW (Format80) codec + XOR-delta SHP
  decoder (ported from VC `lcw.cpp` / `keyframe.cpp` / `xordelta.cpp`),
  `build_remap_lut()`, and `remap` CLI. Every frame is decoded to a full bitmap,
  remapped, and re-encoded as a **standalone Format80 keyframe** (no delta chains
  in output). `shptools.py` self-tests the LCW round-trip.
- **`scripts/build_tfassets.sh`** — extract each TD SHP from `CONQUER.MIX`,
  remap via `shptools.py`, repack `TFASSETS.MIX`. Adding a new separated
  building = add a line here; it's auto-remapped.

## Drawn colours (the Obelisk laser)

The Obelisk laser is a **drawn line**, not a SHP, so it bypasses `TFASSETS.MIX`
— but it has the *same* root cause. `redalert/techno.cpp` hardcoded TD's beam
indices `0x7D`/`0x7F` (red in TD's palette, **green** in RA's). Fixed by remapping
through the same LUT: `0x7D → 0xD8`, `0x7F → 0xE6`. Both the classic `LogicPage`
draw and the Remastered launcher line-intercept (`DLL_Draw_Line_Intercept`) use
RA's palette, so one value fixes both modes.

**General rule for any new TD-sourced drawn colour:** look up the TD index's RGB
in TD `TEMPERAT.PAL`, find the closest RA index (the LUT in `shptools.py` does
this), hardcode the RA index. Don't reuse the raw TD index.

## Verifying

`build_tfassets.sh` rebuilds `TFASSETS.MIX`; deploy with `deploy.sh`. In-game
(Deck), classic graphics: TD buildings render correct colours with house colour
following the player; Obelisk laser is red. Remastered mode is unaffected
(launcher uses the TGA tileset, not these SHPs).
