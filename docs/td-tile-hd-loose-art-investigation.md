# TD terrain tiles in HD

**Status:** Reference. The launcher's rules for terrain template art: what loose art can and can't
add. TD's own templates draw from TD's tilesets on the TD theatres (`td-base-art.md`).

## The wall: no loose art for a new template name

The launcher renders terrain templates only from its preloaded base-MEG atlas, so a new template AssetName with
loose art crashes ClientG: see the field manual's
[Adding a theatre of your own](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/maps-and-lobby/custom-theatres.md#the-wall-no-new-terrain-template-names),
the wall. A known-good DXT5 from another mod, put on an existing template's frame (`S02`), crashed the same way, so that test doesn't pin the wall on new names alone; the mod with its CONFIG.MEG removed crashed too. EMC has no terrain or template mechanism: its `CDATA.CPP` and `TDATA.CPP` are
unchanged from EA's. Reilsss's CnCinRA seems to reskin terrain with loose art but overrides civilian
buildings (`V20`–`V37`), which are objects; his Snow to Desert does ship loose terrain, 8,304 DDS
frames at stock template paths.

The DLL can't fix it: it hands each cell over by template name (`Get_Template_Info`), and the HD
atlas is ClientG's. The DLL's template heap grows with `TEMPLATE_COUNT`, so there is no cap to raise.

## Loose overrides that do work

- **Existing template names take loose DDS overrides, and TILEPATCHES:** see the field manual's
  [Adding a theatre of your own](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/maps-and-lobby/custom-theatres.md#what-works-new-art-under-existing-names),
  what works.
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
