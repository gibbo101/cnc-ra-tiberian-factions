# Skirmish music

**Status:** Reference. The mod's skirmish, jukebox and menu music: TF's playlists, music by faction, and the
optional TS-Music pack (Tiberian Sun and Firestorm's in-game themes).
**Open:** the Settings page that writes `tf_music.ini`; a Random lobby pick plays the stock rotation.

## What ships

- **Menu:** the Hell March Retaliation remix, fading in after the startup intro.
- **Skirmish, Mix (the default):** every remastered RA track, the remastered TD tracks minus excluded cues,
  and the RA and TD bonus tracks, randomised; with TS-Music enabled, its 26 tracks join.
- **Skirmish, by setting:** Red Alert only, Tiberian Dawn only, Tiberian Sun only, or Faction, where each
  faction plays its own choice (by default RA for Allies and Soviets, TD for GDI and Nod, TS for TS GDI).
- **Jukebox:** TS-Music's tracks listed as "(Tiberian Sun) <title>" and "(Firestorm) <title>", under the
  Red Alert game and Remastered track filters. They are listed only while TS-Music is enabled.

Any choice that needs TS-Music while it is off plays the Mix rotation without it.

## Files

| File | Built by | Holds |
|---|---|---|
| `Data/XML/AUDIO/MUSICEVENTS.XML` (loose) | `musicevents_build.py loose` | the mod's music events plus `<RAR\|RAC\|RAB>_TF_MUS_<RA\|TD\|TS\|MIX>` |
| `Data/XML/AUDIO/AUDIO_SYSTEM_CONSTANTS.XML` (loose) | `music_jukebox_build.py` | the stock jukebox list plus the TS-Music entries |
| `Data/ModText.csv` | `music_jukebox_build.py` | `TEXT_MUSIC_TS_MUS_<TITLE>`, the jukebox titles |
| `asset-packs/TS-Music/tracks.json` | `ts_music_build.py` | each track's file, title, game, side and length |
| `asset-packs/TS-Music/Data/AUDIO/MUSIC/*.WAV` (gitignored) | `ts_music_build.py` | the tracks, checked by `scripts/ts_music_work/music.md5` |

`scripts/build_config_meg.sh` writes both loose XML files beside CONFIG.MEG. `ts_music_build.py` extracts the
themes from an installed Tiberian Sun (`SCORES.MIX`, `SCORES01.MIX`, titles from `THEME.INI` and
`THEME01.INI`), skips the menu and score themes (`Normal=no`), and converts each to the format Remastered's
music uses: 44.1 kHz stereo MS-ADPCM, at the stock tracks' level.

## Settings

`Documents/CnCRemastered/tf_music.ini`, read at every skirmish track:

```ini
[Music]
Soundtrack=MIX        ; MIX, FACTION, RA, TD or TS
Allies=RA
Soviets=RA
GDI=TD
Nod=TD
TSGDI=TS
```

An unset key keeps its default.

## How the launcher picks the music

The music events are defined in `MUSICEVENTS.XML` and fired by name. A skirmish instance names its ambient
music `MUS_RA_MULTIPLAYER_MODE` (`INSTANCES.XML`), and ClientG adds the audio prefix (`RAR`, `RAC` or `RAB`, by
the player's audio setting) in `0x169CF30`, then looks the name up with the music manager's find
(`0xE92A90`). That function runs at the start of the match and again whenever a track has ended and the gap
has run out, so a swap there holds for the whole match.

`redalert/tf_music.cpp` redirects that one lookup (the call at `0x169D018`). For a skirmish event it asks for
`<prefix>_TF_MUS_<LIST>`, and returns the stock event when that is missing. The lobby faction is read from
`0x20E0CF8`: the picker row plus two (GDI 2, Nod 3, Soviets 4, Allies 5, TS GDI 7; 6, 8 and 9 are the
duplicate rows).

TS-Music counts as present when `Data\AUDIO\MUSIC\TS_MUS_VALVES.WAV` exists under any enabled mod's folder
(the launcher's mod roots, `0x1FE4C28`), which is where the launcher would open it.

### The jukebox

The jukebox list comes from `AUDIO_SYSTEM_CONSTANTS.XML`'s `<MusicJukeboxTracksList>`, parsed into a vector of
0x5C-byte entries (begin and end at `0x2038734` / `0x2038738`). The jukebox manager's setup (`0xEA3530`, called
at `0x15CF40E`) then builds its own records from it. Without TS-Music, `tf_music.cpp` drops the `TS_MUS_`
entries from the parsed vector **before** that setup: the jukebox screen refuses to build unless the vector
and the records are the same length, so removing records afterwards breaks it. The screen shows an entry when
its `<Game>` and `<TrackType>` match the player's filter checkboxes, not their audio setting; an unknown
`<Game>` is never shown. A playing jukebox playlist overrides the skirmish music.

## Traps

- **One copy wins.** The launcher opens a loose file from the first mod folder that has it and never merges.
  An add-on can't carry its own `MUSICEVENTS.XML` or jukebox list beside Tiberian Factions', so TF owns the
  lists and TS-Music ships only the WAVs.
- **Classic and Bonus playlists carry mod edits.** The skirmish builder's base is the `MUSICEVENTS.XML` already
  in the mod's CONFIG.MEG; rebasing on the stock file reverts them. The CONFIG.MEG copy keeps its exact byte
  length (`config-meg-mod-delivery.md`); the loose copy has no such limit.
- **`RandomizePlayList=True` randomises the first track too**, so a fixed opener and a random remainder can't
  be had together.
- **The data route doesn't exist.** `AUDIO_FACTIONS.XML`'s `<MusicMap>` is never consulted for TD or RA, and the
  DLL's `ThemeClass` is inert in the remaster build (`soundio_null.cpp`). Music by faction needs the launcher
  hook.
- **When testing a music change**, check the deployed files' md5: a parallel deploy once overwrote a probe and
  gave a false reading.

## Cross-references
- `asset-packs.md`: the TS-Music pack among the others.
- `config-meg-mod-delivery.md`: shipping the mod's own CONFIG.MEG.
- `launcher-vs-dll-ownership.md`: what the launcher owns.
