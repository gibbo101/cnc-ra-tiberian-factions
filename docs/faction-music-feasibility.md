# Skirmish music

**Status:** Reference. The mod's skirmish and menu music ship as data in the mod's `CONFIG.MEG`;
per-faction music is a dead end by every lever.

## What ships

`scripts/musicevents_build.py`, run by `scripts/build_config_meg.sh`, rebuilds `MUSICEVENTS.XML`:
- **Remastered audio** (`RAR_MUS_RA_MULTIPLAYER_MODE`): every remastered RA track, the remastered TD
  tracks minus excluded cues, and the RA and TD bonus tracks, randomised.
- **Classic and Bonus audio** (`RAC_`, `RAB_`): an even RA/TD rotation, passed through untouched.
  Any playlist edit covers all three variants, since the player's audio-mode toggle picks between
  them.
- **Main menu:** the Hell March Retaliation remix, fading in after the startup intro.

The builder's base is the `MUSICEVENTS.XML` already in the mod's CONFIG.MEG, not the stock file:
rebasing on stock silently reverts the Classic and Bonus edits.

## How the music system works

`DATA\XML\AUDIO\MUSICEVENTS.XML` defines every piece of music as a named `<MusicEvent>` with a
playlist (`<Entry>` tracks, `RandomizePlayList`, gaps, fades, looping). The launcher fires events by
game-state name: RA skirmish and multiplayer is `RA_MULTIPLAYER_MODE`, `RA_MAP_THEME` the menu theme,
`RA_CAMPAIGN` / `RA_EXPANSIONS` the campaigns. TD tracks play fine from an RA event. `Data/MUSIC.MEG`
holds both soundtracks, named `{RA,TD}{C,R,B}_MUS_<TRACK>` (Classic, Remastered, Bonus).

- **No event has a faction attribute.** RA has one in-game event; the per-side jukebox screens are
  only skins.
- **A fixed opener and a random remainder can't be had together.** `RandomizePlayList=True`
  randomises the first track as well; `False` plays the whole list in order.

## The same-size rule

**An edited CONFIG.MEG member must keep its exact byte length.** The launcher resolves a mod MEG's
members at the base archive's offsets, not the mod MEG's own table, so a size change shifts every
later member and the launcher crashes at startup (`XMLDatabase::Skip_XML_Header` on a later file,
`PlayerXPTable.xml` when the music file grew). The builder reclaims space from commented-out
`MusicEvent` blocks and pads the rest with a trailing comment. This holds for every CONFIG.MEG
member (`config-meg-mod-delivery.md`).

## Why per-faction music is dead

- **Data:** `FACTIONS.XML` points each faction at an `AudioTableName`, and `AUDIO_FACTIONS.XML`
  tables carry a `<MusicMap>` that EA's comment says TD and RA don't use. A probe gave GDI and Nod
  their own tables remapping `RAR_MUS_RA_MULTIPLAYER_MODE` to the TD GDI and Nod themes: GDI still
  played RA. C&C fires music events by name and never consults the map.
- **DLL:** the remaster build links `soundio_null.cpp`, so `ThemeClass` early-outs
  (`SampleType == 0`) and even its per-side `Owner` filter never runs. `EventCallbackType` has no
  music event.
- **A one-shot through the sound-effect callback** can't silence the launcher's own music or control
  the rotation.

When testing any music change, md5 the deployed CONFIG.MEG: a parallel deploy once overwrote a probe
and produced a false reading.

## Cross-references
- `config-meg-mod-delivery.md`: shipping the mod's own CONFIG.MEG.
- `mix-file-format.md`: `meg_pack.py`, the byte-clean repack.
- `launcher-vs-dll-ownership.md`: music is launcher- and data-owned.
- `td-audio-routing-recipe.md`: the sound-effect channel.
