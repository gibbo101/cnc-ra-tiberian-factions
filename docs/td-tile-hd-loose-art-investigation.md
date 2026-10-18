# TD terrain tiles in HD

**Status:** Reference. The launcher's rules for terrain template art: what loose art can and can't
add. TD's own templates draw from TD's tilesets on the TD theatres (`td-base-art.md`).

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
  pixels of known names only and cannot add names; a new name needs a base tileset that draws it,
  which is how TD's templates draw on the TD theatres. The radar samples the overridden textures, so a theatre reskin gets a matching
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
- RA's templates end at HILL01 = 400, matching the editor (FIXIT_ANTS on). New templates append
  at 401 and up, and `Init_Heap` (with `_Watcom_Ugh_Hack`) must register them in enum order (heap
  index = type id).
- The engine reads each template's width, height and land type from its classic iconset through
  `MFCD::Retrieve("<NAME>.<theatre suffix>")`. Missing classic art doesn't crash the engine
  (`Get_IconSet_MapWidth(NULL)` = 0).
- A TD `.bin` map is 64 × 64 cells of 2 bytes (template id u8, icon u8), `0xFF` = clear. TD template
  HD art ships per icon, some animated over 8 frames, in `TEXTURES_TD_SRGB.MEG`.
