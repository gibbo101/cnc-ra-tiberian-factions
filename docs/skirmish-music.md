# Skirmish music

**Status:** Reference. The mod's skirmish, jukebox and menu music: TF's playlists, music by faction, and the
optional TS-Music folder (Tiberian Sun and Firestorm's in-game themes), withdrawn from the Workshop and to be
built from the player's own Tiberian Sun (`ts-music-import.md`).
**Open:** a Random lobby pick plays Mix whatever the faction's choice.

## What ships

- **Menu:** the Hell March Retaliation remix, fading in after the startup intro.
- **Skirmish, Mix (every faction's default):** the mod's RA and TD rotation for the player's audio setting, randomised. On
  Remastered that is every remastered RA track and the remastered TD tracks minus menu cues and score stingers;
  Classic and Bonus keep their own rotations. With TS-Music enabled, its 26 tracks join.
- **Skirmish, by faction:** each faction plays its own choice of Mix, Red Alert only, Tiberian Dawn only or
  Tiberian Sun only, so Allies can play Red Alert's tracks while GDI plays Tiberian Dawn's. In a LAN game each
  player hears their own faction's choice, from their own settings (each machine's pick at `0x20E0CF8`).
- **Jukebox:** TS-Music's tracks listed as "(Tiberian Sun) <title>" and "(Firestorm) <title>", under the
  Red Alert game and Remastered track filters. They are listed only while TS-Music is enabled.

Any choice that needs TS-Music while it is off plays the Mix rotation without it. A match needs every player on
the same enabled mods, so in multiplayer TS-Music is on for everyone or no one (`pack-panel.md`).

## Files

| File | Built by | Holds |
|---|---|---|
| `Data/XML/AUDIO/MUSICEVENTS.XML` (loose) | `musicevents_build.py loose` | the mod's music events plus `<RAR\|RAC\|RAB>_TF_MUS_<RA\|TD\|TS\|MIX>` |
| `Data/XML/AUDIO/AUDIO_SYSTEM_CONSTANTS.XML` (loose) | `music_jukebox_build.py` | the stock jukebox list plus the TS-Music entries |
| `Data/ModText.csv` | `music_jukebox_build.py` | `TEXT_MUSIC_TS_MUS_<TITLE>`, the jukebox titles |
| `asset-packs/TS-Music/tracks.json` | `ts_music_build.py` | each track's file, title, game, side and length |
| `asset-packs/TS-Music/Data/AUDIO/MUSIC/*.WAV` (gitignored) | `ts_music_build.py` | the tracks, checked by `scripts/ts_music_work/music.md5` |

`scripts/build_config_meg.sh` writes both loose XML files beside CONFIG.MEG. `scripts/ts_music_preview.py` draws the
Workshop item's preview. `ts_music_build.py` extracts the
themes from an installed Tiberian Sun (`SCORES.MIX`, `SCORES01.MIX`, titles from `THEME.INI` and
`THEME01.INI`), skips the menu and score themes (`Normal=no`), and converts each to the format Remastered's
music uses: 44.1 kHz stereo MS-ADPCM. The tracks already sit at the stock tracks' level, so none is adjusted.

## Settings

TIBERIAN FACTIONS SETTINGS, under REPLAY / OBSERVER on the main menu, sets the music. `TF_SETTINGS.BUI`
(`scripts/bui_settings_build.py`) is the CAMPAIGNS page run by `SplashScreen`, opened and bound by
`redalert/tf_launcher.cpp` as the ADD-ONS screen is (`pack-panel.md`):

- **AUDIO** has a tab per faction under the game banners, the faction's crest, and four rows: MIX, RED ALERT, TIBERIAN
  DAWN and TIBERIAN SUN, the saved one ticked. A click saves it at once; it plays from the next track. While the
  TS-Music tracks are missing, TIBERIAN SUN reads "Not installed" and can't be picked. DEFAULTS puts every faction
  back on MIX.
- **GAME RULES** shows COMING SOON.

The page writes `Documents/CnCRemastered/tf_music.ini`, which the hook reads at every skirmish track:

```ini
[Music]
; each faction plays MIX, RA, TD or TS
ALLIES=RA
SOVIETS=RA
GDI=TD
NOD=TD
TSGDI=TS
```

An unset faction plays MIX, and an inline `;` comment after a value is ignored.

## How the launcher picks the music

The skirmish event, its audio prefix and the lookup that runs at match start and after each track are on the field
manual's [Music by faction, and the jukebox](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/sound-and-music/music-by-faction-and-the-jukebox.md#how-the-launcher-picks-skirmish-music), How the launcher picks skirmish music and Addresses in this client.

`redalert/tf_music.cpp` redirects that one lookup (the call at `0x169D018`). For a skirmish event it asks for
`<prefix>_TF_MUS_<LIST>`, and returns the stock event when that is missing. The lobby faction is read from
`0x20E0CF8`: the picker row plus two (GDI 2, Nod 3, Soviets 4, Allies 5, TS GDI 7; 6, 8 and 9 are the
duplicate rows).

TS-Music counts as present when `Data\AUDIO\MUSIC\TS_MUS_VALVES.WAV` exists under any enabled mod's folder
(the launcher's mod roots, `0x1FE4C28`), which is where the launcher would open it.

### The jukebox

Without TS-Music, `tf_music.cpp` drops the `TS_MUS_` entries from the parsed vector before the jukebox
manager's setup. How the list is parsed, the addresses and the filters are on the field manual's
[Music by faction, and the jukebox](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/sound-and-music/music-by-faction-and-the-jukebox.md#the-jukebox), The jukebox.

## Traps

One copy of each list wins and `RandomizePlayList` shuffles the first track: see the field manual's
[Music by faction, and the jukebox](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/sound-and-music/music-by-faction-and-the-jukebox.md#traps), Traps. The unused `<MusicMap>` and the DLL's
inert theme player are in its [How the launcher picks skirmish music](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/sound-and-music/music-by-faction-and-the-jukebox.md#how-the-launcher-picks-skirmish-music) section.

- **TF owns the lists.** Only one copy is read, so TS-Music ships only the WAVs.
- **Classic and Bonus playlists carry mod edits.** The skirmish builder's base is the `MUSICEVENTS.XML` already
  in the mod's CONFIG.MEG; rebasing on the stock file reverts them. The CONFIG.MEG copy keeps its exact byte
  length (`config-meg-mod-delivery.md`); the loose copy has no such limit.
- **When testing a music change**, check the deployed files' md5s: another session's deploy can replace them.

## Cross-references
- `asset-packs.md`: the TS-Music pack among the others.
- `config-meg-mod-delivery.md`: shipping the mod's own CONFIG.MEG.
- `launcher-vs-dll-ownership.md`: what the launcher owns.
