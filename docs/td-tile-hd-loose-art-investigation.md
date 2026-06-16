> **UPDATE 2026-06-09 (same day, later): ROUTED AROUND — TD tiles now render in HD.**
> The wall below is real but only blocks the launcher's *template-name atlas* path, which we
> no longer use. Working architecture: the engine keeps real TD templates (ids 401+, land-type
> + classic art from RA-format-converted `.tem` in TFASSETS.MIX — TD's 32-byte iconset header
> must be converted to RA's 40-byte layout or `Land_Type` div-zero-crashes);
> `CellClass::Get_Template_Info` reports those cells to the launcher as CLEAR (no atlas miss);
> `DLLExportClass::Cell_Class_Draw_It` synthesizes a dynamic-map entry per cell (AssetName =
> template IniName, ShapeIndex = logical TIcon, Type = OVERLAY_V12) which the launcher resolves
> through the loose ZIP + tileset XML — the proven TIB01 pipeline. Full shore family sh1–sh18 +
> bridge1/2 ported this way (RA *redrew* same-named shores, so name+size matching is never
> art-safe for `sh*`). Render-verified on desktop, SCG30 converts 0-unmapped with crossable
> bridges. Details: memory `project-td-skirmish-map-import-findings`.

# TD-tile HD terrain — loose-art investigation (2026-06-09)

Goal of the session: make converted TD skirmish maps render with TD's own tile art so
shores/bridges look right (the auto-transcoder already nails ~90% of tiles via RA's base
art, but RA re-laid-out shores/bridges so those came out as white squares / coast-on-land).

## TL;DR — the wall is real and conclusive
**The launcher renders terrain TEMPLATES only from a fixed, preloaded base-MEG atlas. It will
not load loose template textures from a mod (neither a new AssetName nor an override of an
existing one).** Every attempt crashes ClientG.exe at the same address. There is no mod-side
fix for HD *template* art short of replacing the whole 2.4 GB `TEXTURES_RA_SRGB.MEG` (not
Workshop-shippable). OBJECTS and OVERLAYS *do* take loose art (that's why TIB01, TD buildings,
and the blossom-as-building all work) — TEMPLATES are the exception.

## The crash signature
ClientG.exe, `0xC0000005` ACCESS_VIOLATION, NULL write, code `0x0096A539` = image-base
`0x400000` + RVA **`0x56A539`**. Identical across:
- a NEW terrain template AssetName (`TDSH1`…`TDBRIDGE2`, ids 401-407) placed on a map;
- a Reilsss-style OVERRIDE of an existing template name (`S02` → repointed `<Frame>` to loose);
- the override using Reilsss's OWN known-good 256×256 DXT5 DDS.
It is the SAME address as the 2026-06-08 blossom terrain-art crash. The unplaced spike loaded
fine because the launcher only *reads the tileset XML* up front; it doesn't fault until it
*renders* a placed tile whose texture isn't in the atlas.

## What we ruled out (and how)
1. **DDS format** — both TD-MEG art and Reilsss's are DXT5. Using Reilsss's exact file still
   crashed. Not the format.
2. **Our CONFIG.MEG** — removed the mod's CONFIG.MEG entirely; still crashed. Not CONFIG.MEG
   (this corrects the old blossom-era guess).
3. **EMC** — Reilsss "Requires EMC", so we cloned EMC source
   (github.com/JohnnyJigglez/CnC_Remastered_Collection_ModUtils, Workshop branch = shipped v27)
   and diffed vs the EA source. **`CDATA.CPP` (templates) and `TDATA.CPP` (terrain) have ZERO
   real changes** (the huge raw diff was pure CRLF noise). EMC's real work is in `RULES.CPP`
   (warheads/prereqs), `DLLInterface.cpp` (custom unit/building instances), `INIT.CPP`. EMC has
   **no terrain/template mechanism** — nothing to port. The "Loose" string in EMC's DLL is a
   data-table entry (`CONST.CPP:173`), not a loose-loader.
4. **Reilsss doesn't override templates at all** — his loose art is ONLY `V20`–`V37`, which are
   `STRUCT_V*` (civilian *buildings* = objects, placed via `[STRUCTURES]`, rendered through the
   object path that takes loose art). He overrides ZERO real templates (`s*`/`d*`/`p*`/`sh*`/
   `bridge*`/`w*`/`rv*`). So his "terrain" reskin is object art, not template art.
5. **Load path (Workshop vs dev `Mods/`)** — mirrored the current build into our subscribed
   Workshop copy + injected the S02 override + disabled the dev copy; still crashed at
   `0x56A539`. (Caveat: the launcher's enabled-mod list is in the wine registry
   `EnabledModsPatch2`, so the dev mod may not have been fully deselected — but #4 already
   explains the crash without invoking load-path.)

## Why the DLL can't fix it
The DLL hands each cell to the launcher by template NAME string (`dllinterface.cpp` ~3004/3500,
`CellClass::Get_Template_Info` returns IniName + classic ImageData). The launcher resolves the
HD texture by that name from its preloaded terrain atlas (base MEG). The DLL-side template heap
auto-grows with `TEMPLATE_COUNT` (no cap to raise — answers the "is it a cap like buildings/
units?" question: no). The atlas is ClientG-side and only ingests base MEG + (for objects/
overlays) loose art; templates don't get the loose path.

## Engine facts learned (reusable)
- RA `[MapPack]` = base64(UUBlock) of LCW-block-framed `16384×TType(u16 LE)` ++ `16384×TIcon(u8)`;
  `[OverlayPack]` = same over `16384` signed-char overlay-per-cell. Clear template = `0xFFFF`.
  LCW block frame = `[CompCount u16 LE][UncompCount u16 LE][data]`, 8192-byte blocks. UUBlock =
  base64 in 70-char numbered lines, CRLF. (Validated against COMMUNITY/SCMC1EA.INI.)
- DLL `TEMPLATE_COUNT` = 401, aligned with the editor's 401 (FIXIT_ANTS on → HILL01=400). New
  templates append at id 401+. Template registration order in `Init_Heap` (+ `_Watcom_Ugh_Hack`)
  must match enum id order (heap index == type id).
- Engine reads each template's Width/Height + land-type from its classic `.tem` via
  `MFCD::Retrieve("<NAME>.TEM")`; `Get_IconSet_MapWidth(NULL)=0` (safe, no crash) so missing
  classic art doesn't crash — HD render still fails separately at the launcher.
- TD `.bin` = 64×64 cells × 2 bytes (template-id u8 + icon u8), `0xFF`=clear. TD template HD art
  ships per-icon (some animated 8-frame) in `TEXTURES_TD_SRGB.MEG`.

## Paths forward (no loose templates)
- **A. Curated TD→RA remap onto RA's EXISTING shore/bridge templates** — map TD shore/bridge
  tiles to the nearest existing RA template (renders from base MEG, no crash). RA's shores are
  re-laid-out so it's approximate, but clean + HD. Automatable.
- **B. Editor finish** — transcode the ~90% automatically, fix shores/bridges per map in the
  Mobius editor (RA tiles render fine). Best fidelity-with-RA-tiles, manual.
- **C. Curate inland source maps** — many TD temperate maps are inland (rivers `rv*` already
  transcode perfectly); ship those ~100% auto, defer coastline/bridge maps.
- **D. Render bridges (maybe shores) as OBJECTS** — objects take loose art (proven: blossom-as-
  building, TD buildings). A bridge placed as a structure/object with loose TD HD art would
  render. Fits "objects work, templates don't." Bigger design; best fit for bridges (functional
  crossings), awkward for full coastlines.
- **E. Luke's new idea** — TBD, to explore next session.

## Outcome (SHIPPED v2.0.0)

The work-in-progress tree this section once tracked has all shipped or been superseded:
- The TD→RA map transcoder (`scripts/td_map_to_ra.py`) shipped the 31-map TD pack via
  `<mod>/CustomMaps/` — see [[project-td-skirmish-map-import-findings]] and `td-skirmish-map-import.md`.
- The whole Tiberium ecosystem shipped in v2.0.0 (TIB01 overlay, visceroids, HD blossom tree).
- Dev cheat toggles are no longer hand-flipped per session — they're gated on the `TF_DEV_BUILD`
  macro (see the Dev-build switch in the workspace CLAUDE.md / `[[project-dev-build-switch]]`).

The durable takeaway is the **rendering architecture above the banner** (real TD templates +
dynamic-map synthesis = HD TD tiles, no atlas-name path) plus the forward-looking options A–E for
the still-open coastline/bridge/desert work.
