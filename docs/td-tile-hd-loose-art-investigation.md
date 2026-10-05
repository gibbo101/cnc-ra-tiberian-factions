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

Rules for these ground entries (`Cell_Class_Draw_It`):
- **No entry under an overlay or smudge.** Two dynamic entries on one cell z-fight, because the
  launcher's ordering is unstable (layer flags, pixel biases and CellY biases all failed); the static
  layer shows the vanilla twin template there, leaving a tone seam on clear ground.
- **Type `OVERLAY_V12`:** the launcher paints radar pips from the vanilla resource Type range whatever
  the flags say (GOLD1 painted shore cells as ore); V12 is decorative and gets no pip. Pip art is per
  Type: GOLD1-4 four gold shades, GEMS1-4 teal, magenta, green and red, which is why Tiberium goes
  out as GEMS3 (`tiberium-ecosystem.md`).
- **A constant ShapeIndex:** a churning value, even between identical frames, makes the launcher
  re-create the sprite, and it pops above the overlay.
- **Radar and static stand-ins** (`Get_Template_Info`) are chosen by the icon's art class, not its
  land type: 'W' gives W1, 'B' SH02 icon 9, 'R' RIVER13 icon 6, 'K' SLOPE01, anything else CLEAR1 (on
  interior: CLEAR1 for sand, ARRO0001-0004). Same-size vanilla twins keep road and river continuity,
  and water beside a river uses RIVER13 icon 6.
- **The overlay layer, not smudge:** the launcher skips smudge entries on building-occupied cells.
- **Bibs on TD ground** draw RA's per-theatre art: winter maps use the temperate slot, whose bib
  matches, and desert maps the interior slot, whose `BIB*.INT` is shadowed with TD desert bib pixels
  (`build_desert_radar_palette.py`). A per-cell BIB-to-TDBIB AssetName swap layered unreliably
  against the ground entry.

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
