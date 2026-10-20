# Tiberian Sun music, imported from the player's own copy

**Status:** Design. Replaces the TS-Music Workshop pack, withdrawn because EA's C&C modding guidelines don't let a
mod include music files from C&C games.
**Open:** a guidelines reread with this design in hand; a spike converting one track in the DLL.

The mod ships no music. The ADD-ONS screen finds the player's Tiberian Sun and converts its soundtrack on the
player's machine into a local TS-Music mod, laid out as the withdrawn pack was, so the Settings page and the
playlists (`skirmish-music.md`) work unchanged. Tiberian Sun is a free download, so every player can have it.

## Where Tiberian Sun can be

Looked for in this order; the first folder holding `TIBSUN.MIX` and `SCORES.MIX` wins:

1. Steam: Tiberian Sun on its own and as part of The Ultimate Collection, through every library in
   `libraryfolders.vdf` (`steamapps/common/Command & Conquer Tiberian Sun`).
2. The CnCNet download of the 2010 freeware release.
3. The EA app's install.
4. The original install's registry entry (Westwood's `InstallPath`).

Firestorm's themes come from `expand01.mix` and `SCORES01.MIX` in the same folder when present; without them
only Tiberian Sun's own themes are imported.

## The conversion

A C++ port of `scripts/ts_music_build.py`, run by the DLL inside the launcher:

- read `THEME.INI` from `LOCAL.MIX` inside `TIBSUN.MIX` (and `THEME01.INI` from `expand01.mix`) for the themes a
  player hears in game, their titles and sides;
- read each theme's `.AUD` from the scores archive and decode Westwood's IMA ADPCM;
- write it as the Remastered music WAV the pack shipped (44.1 kHz stereo), under the pack's names
  (`TS_MUS_<TITLE>.WAV`), with the pack's `ccmod.json`, `CCDATA` marker and music XML beside them, into
  `Mods/Red_Alert/TS-Music/` in the player's Documents.

The output matches what `ts_music_build.py` writes byte for byte where the formats allow, so the build script
stays the reference and its checksums (`scripts/ts_music_work/music.md5`) test the port.

## The ADD-ONS entry

TIBERIAN SUN MUSIC stays on the ADD-ONS screen. Its row's status line, where other add-ons show LOADED, follows
the import:

| State | Status line | Detail panel button |
|---|---|---|
| Not found | NO TIBERIAN SUN INSTALL DETECTED | none; the panel says Tiberian Sun is a free download |
| Found, not imported | READY TO IMPORT | IMPORT |
| Imported | LOADED, as any add-on | the usual on/off tick |

IMPORT converts the themes with a progress bar, switches the mod on and restarts the game, as switching on any
add-on does.
