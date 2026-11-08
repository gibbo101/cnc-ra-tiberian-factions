# TD terrain tiles in HD

**Status:** Reference. The launcher's rules for terrain template art: what loose art can and can't
add. TD's own templates draw from TD's tilesets on the TD theatres (`td-base-art.md`).

## The wall: no loose art for a new template name

The launcher renders terrain templates only from its preloaded base-MEG atlas, so a new template AssetName with
loose art crashes ClientG: see the field manual's
[Adding a theatre of your own](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/maps-and-lobby/custom-theatres.md#the-wall-no-new-terrain-template-names),
the wall, which says why the DLL can't fix it. The same page has the `S02` repoint test under what works, and
what EMC and Reilsss's mods really do under how it was verified (his Snow to Desert ships 8,304 loose DDS frames
at stock template paths).

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
- Where new templates go (401 up, registered in enum order) and how their classic iconsets set their size: the
  field manual's [Adding a theatre of your own](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/maps-and-lobby/custom-theatres.md#the-theatre-itself),
  the theatre itself (`Get_IconSet_MapWidth(NULL)` = 0 is why missing art gives a 0 by 0 template).
- TD's `.bin` maps and its per-icon HD terrain art: the field manual's
  [TD theatres in Red Alert](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-theatres-in-red-alert.md#tds-own-map-files).
