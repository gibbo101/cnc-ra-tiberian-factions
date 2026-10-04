# TD terrain tiles in HD

**Status:** Reference; shipped in 2.0.0. How TD terrain tiles render in HD on RA maps, and the
launcher wall that rules out loose art for new template names.

## How TD tiles render

The engine keeps real TD templates (ids 401 and up). Their land types and classic art come from
TD `.tem` files converted to RA's format in TFASSETS.MIX: TD's 32-byte iconset header must become
RA's 40-byte layout, or `Land_Type` crashes on a divide by zero. `CellClass::Get_Template_Info`
reports those cells to the launcher as CLEAR, so the atlas lookup never misses, and
`DLLExportClass::Cell_Class_Draw_It` synthesises a dynamic-map entry per cell (AssetName = the
template IniName, ShapeIndex = the logical TIcon, Type = OVERLAY_V12). The launcher resolves that
through the loose ZIP and tileset XML, the same pipeline as TIB01.

The whole shore family (sh1 to sh18) and bridge1/2 render this way. RA redrew its own same-named
shores, so matching by name and size is never art-safe for `sh*`. The map transcoder is
`scripts/td_map_to_ra.py` (`td-skirmish-map-import.md`).

## The wall: no loose art for a new template name

The launcher renders terrain templates only from its preloaded base-MEG atlas. A new template
AssetName with loose art crashes ClientG (`0xC0000005`, a NULL write at RVA `0x56A539`) the moment a
placed tile renders; the tileset XML alone loads fine. Ruled out as causes: the DDS format (a
known-good DXT5 from another mod still crashed), the mod's CONFIG.MEG (removed, still crashed), and
the load path. EMC has no terrain or template mechanism: its `CDATA.CPP` and `TDATA.CPP` are
unchanged from EA's. Mods that seem to reskin terrain with loose art are overriding civilian
buildings (`V20`–`V37`), which are objects.

The DLL can't fix it: it hands each cell over by template name (`Get_Template_Info`), and the HD
atlas is ClientG's. The DLL's template heap grows with `TEMPLATE_COUNT`, so there is no cap to raise.

## Loose overrides that do work

- **Existing template names take loose DDS overrides:**
  `DATA/ART/TEXTURES/SRGB/RED_ALERT/TERRAIN/<THEATRE>/<NAME>.<SNO|TEM>/...DDS` shadows the same-path
  MEG entry, no EMC needed (the Desert Biome mod, item 2833233740, is pure data). This changes the
  pixels of known names only and cannot add names, so new TD templates still need the dynamic-map
  route above. The radar samples the overridden textures, so a theatre reskin gets a matching
  radar.
- **TILEPATCHES:** `DATA/XML/TILEPATCHES/` holds per-map cell placements
  (`MAPS/<game>/<MAP>_MAPPATCHES.XML`) and animated multi-cell texture blocks
  (`PATCHES/<name>_PATCH.XML`, with an FPS field). Loose copies override with no same-size lock.
- **New HD asset names render** as loose VFX or tile ZIPs plus XML registration (TDFLAME, TDCHEM,
  the SAM and gun flashes). Adding a new name to an already-installed mod mid-iteration can fall back
  to the donor sprite: the launcher appears to cache the name set at install. Check new-name art with
  a clean reinstall; a Workshop install is always fresh.

## Engine facts

- RA `[MapPack]` = base64 (UUBlock) of LCW-block-framed `16384 × TType (u16 LE)` followed by
  `16384 × TIcon (u8)`; `[OverlayPack]` is the same over 16384 signed-char overlays. A clear template
  is `0xFFFF`. An LCW block frame is `[CompCount u16 LE][UncompCount u16 LE][data]` in 8192-byte
  blocks; UUBlock is base64 in 70-character numbered lines, CRLF.
- `TEMPLATE_COUNT` is 401, matching the editor (FIXIT_ANTS on: HILL01 = 400). New templates append
  at 401 and up, and `Init_Heap` (with `_Watcom_Ugh_Hack`) must register them in enum order (heap
  index = type id).
- The engine reads each template's width, height and land type from its classic `.tem` through
  `MFCD::Retrieve("<NAME>.TEM")`. Missing classic art doesn't crash the engine
  (`Get_IconSet_MapWidth(NULL)` = 0).
- A TD `.bin` map is 64 × 64 cells of 2 bytes (template id u8, icon u8), `0xFF` = clear. TD template
  HD art ships per icon, some animated over 8 frames, in `TEXTURES_TD_SRGB.MEG`.
