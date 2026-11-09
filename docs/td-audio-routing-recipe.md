# TD audio routing recipe — playing TD .WAV assets in RA mod mode

**Status:** Reference. How a sound reaches the launcher from the DLL, with the Obelisk laser
(`OBELRAY1`) as the worked example; every TD and TS sound in the mod ships this way. The launcher's own EVA lines
follow the faction by a RAM patch of ClientG's cached samples (shipped in 5.0.0).

See the field manual's [TD sounds from the base game](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-sounds-from-the-base-game.md#the-method), The method.
TF's files: the `VOC_TD_*` entries in `redalert/defines.h`, the `SoundEffectName[]` entries in
`redalert/audio.cpp`, and the merged `resources/remaster_mods/Vanilla_RA/Data/XML/AUDIO/SFXEVENTSNONLOCALIZED.XML`.
Base files come out with `scripts/meg_extract.py`. TF ships no WAV for a routed TD sample, apart from copies of a
few early ones (the Obelisk's laser and power-up, `OBELRAY1` and `OBELPOWR`); its own new sounds ship in
`resources/remaster_mods/Vanilla_RA/Data/AUDIO/` under their own names.

---

## How the launcher resolves audio

What the launcher does with the name the DLL sends, and the variant suffix a unit response gets, are on the field
manual's [TD sounds from the base game](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-sounds-from-the-base-game.md#how-a-sound-gets-from-the-dll-to-the-speakers), How a sound gets from the DLL to the speakers (the
event's priority and context fields included). TF's copy is `On_Sound_Effect` in `redalert/dllinterface.cpp`.

---

## The worked example: the Obelisk laser

The manual's worked example is TF's Obelisk laser (`VOC_TD_LASER`, `{"OBELRAY1", 1, IN_NOVAR}`). TF ships copies of
its two samples, extracted unchanged from the base game:

```bash
python3 scripts/meg_extract.py extract \
  "$(python3 scripts/steam_library.py path common/CnCRemastered)/Data/SFX3D.MEG" \
  OBELRAY1 \
  /tmp/extract/
```

This yields `TDC_SFX_OBELRAY1.WAV` (classic, about 14 KB) and `TDR_SFX_OBELRAY1.WAV` (remastered, about 36 KB),
shipped as `resources/remaster_mods/Vanilla_RA/Data/AUDIO/TD?_SFX_OBELRAY1.WAV`. The base
`SFXEVENTSNONLOCALIZED.XML` comes out of `Data/CONFIG.MEG` the same way. The weapon names the sound:

```ini
[TDOblsLaser]
Report=OBELRAY1     ; ← VOC_TD_LASER → RAR_SFX_OBELRAY1 alias → TDR_SFX_OBELRAY1.WAV
```

---

## Critical gotchas

See the field manual's [TD sounds from the base game](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-sounds-from-the-base-game.md#traps), Traps, and [Credit tick and radar sounds by faction](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/sound-and-music/credit-tick-and-radar-by-faction.md#traps), Traps.
Check a merged XML with `python3 -c "import xml.etree.ElementTree as ET; ET.parse('path/to/SFXEVENTSNONLOCALIZED.XML')"`.
The player switches classic and remastered sound at runtime in Options → Audio. TF's silenced radar events point at
44-byte header-only WAVs, and the DLL plays the faction's pair (`building-sound-routing.md`).

---

## Reference precedent

Reilsss's CnCinRA (Workshop item `2853520457`, folder `ReilsssCnCinRA/` in the Workshop cache, which
`scripts/steam_library.py` finds) routes TD sounds the same way: its `DATA/XML/AUDIO/SFXEVENTSNONLOCALIZED.XML` has
`RAC_SFX_OBELRAY1` and `RAR_SFX_OBELRAY1` pointing at `TDC_/TDR_SFX_OBELRAY1.WAV`. It ships its other sounds as loose
WAVs under RA's own stock sample names (`DATA/AUDIO/RAC_SFX_*.WAV` and `RAR_SFX_*.WAV`, about 85, such as `BUILD5`,
`CASHUP1`, `RADARON2` and the `DEDMAN` deaths, beside `EN-US/`, `DE-DE/` and `FR-FR/`), so each replaces RA's sample
everywhere it plays. They are mostly TD audio, by an earlier survey not rechecked sample by sample. Beside them sit `DATA/ART/` (`MOVIES/`, `TEXTURES/`), `DATA/XML/OBJECTS/` and `TILESETS/`,
`DATA/ModText.csv`, and `CCDATA/` holding `a_rules.ini`, `aftrmath.ini`, `mplayer.ini` and `EXPAND2.MIX`. TF
instead keeps TD's own sample names and bridges them in `<SampleNamesList>`, so a file's origin shows in its name.

---

## Sample names and formats

New sounds, their format and the traps (the plain-PCM crash, the rates, `.MP3` names that are WAVs, a loose file
replacing a base sample) are on the field manual's [TD sounds from the base game](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-sounds-from-the-base-game.md#samples-of-your-own), Samples of your own and Traps; never test a sound through the
credit tick (its [Credit tick and radar sounds by faction](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/sound-and-music/credit-tick-and-radar-by-faction.md#traps), Traps).
TF encodes its sound effects with `ffmpeg -c:a adpcm_ms -ar 22050 -ac 1` and its EVA lines at 44,077 Hz stereo
(`ffmpeg -ac 2 -ar 44077 -c:a adpcm_ms`, the default 1024 block). Check a new file's md5 and fmt chunk against a
base sample on the same channel. Every TF sound ships under its own new name, so none replaces a base TD sample.

---

## EVA voice (VoxType) faction routing

The launcher side (`RAC_SFX_TD<NAME>` and `RAR_SFX_TD<NAME>` events in the mod's `SFXEVENTSLOCALIZED.XML`, pointing
at the base game's `TDC_/TDR_SFX_EVA_<NAME>_EN-US.MP3`, so no WAV ships) and the widened enum are on the field manual's
[TD sounds from the base game](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-sounds-from-the-base-game.md#the-method), The method.
TF's `VoxType` is `: short` (`redalert/defines.h`), for its `VOX_TD_*` and `VOX_TS_*` entries.

The DLL picks the name in `On_Speech` (`redalert/dllinterface.cpp`) by the player's `ActLike`:
- **TS GDI** sends `SpeechTS[X]` (`Init_SpeechTS`, `redalert/audio.cpp`), or nothing if that slot is NULL.
- **GDI and Nod** (`HOUSE_GOOD`, `HOUSE_BAD`) send `SpeechTD[X]` (`Init_SpeechTD`, such as `TDACCOM1`) when it is set,
  `Speech[X]` when that name already starts with `TD`, and nothing otherwise.
- **Allies and Soviets** send `Speech[X]`, or `SpeechRAO[X]` (`Init_SpeechRAO`, such as `RAOSTRUSLD1`): the name of an
  audible loose copy, for a line whose stock sample TF ships as a silent stub to mute the launcher's own auto-fire.

A line both eras share keeps its RA enum and gets a `SpeechTD[]` slot. A TD-only line gets a new `VOX_TD_*` enum whose
`Speech[]` name is `TD<NAME>`.

### EVA lines the launcher plays

The nine launcher-owned EVA lines in `tf_eva_mailbox.h` (`BCT1`, `MISNLST1`, `MISNWON1`, `NODEPLY1`, `NOPOWR1`,
`PROGRES1`, `REPAIR1`, `SAVE1`, `SLCTTGT1`, each on both audio channels) follow the picked faction, across a faction
switch within one session too: at match start the DLL writes the faction's recording over the seed files and over
ClientG's cached copy of each. Structure-sold is not one of them: the DLL routes it (`SpeechTD` / `SpeechTS` in
`audio.cpp`). Verified in play in both directions on cannot-deploy, mission-accomplished, mission-failed and
battle-control-terminated. It runs in release builds; its logging is `TF_DEV_BUILD`-only. Code:
`TF_Patch_ClientG_Cache` / `TF_Replace_File_In_Process`, `dllinterface.cpp`.

#### How the cache patch works

The method (seed files at launch, the cached copy as the whole WAV in ClientG's read-write heap, a 20-byte needle
per recording, the whole-recording compare before each write) and its traps are on the field manual's
[EVA voice lines the launcher plays](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/sound-and-music/launcher-eva-lines-by-faction.md#part-two-overwrite-the-cached-copy), Part one, Part two and Traps. The cross-process
calls are on its [Re-pointing launcher UI art in memory](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/clientg-ram/repointing-atlas-regions.md#the-method), The method.
In TF, `TF_Replace_File_In_Process` does the compare and the write, the same cross-process shape as the
lobby resolver (`lobby-ambiguity-findings.md`). Why Linux's `ptrace_scope` doesn't block it is on the same
method section.

#### The findings, as TF applies them

1. **The cache holds raw file bytes**, so the patch overwrites in place.
2. **Same size or crash.** Each line's payloads are built to one byte length.
3. **The teardown loader wants `block_align` 70.** `NODEPLY`, `MISNWON` and `MISNLST` play mid-match, so their
   re-encoded payloads (mono, 44,100 Hz, equal length) are fine. `BCT` plays only at teardown, so every payload of
   it keeps `block_align` 70: the base file padded with trailing zeros to the common length, or
   `scripts/msadpcm.py`'s encode (`ts-gdi-faction.md`).
4. **ClientG picks loose or MEG at launch, and caches at first play.** TF ships static seeds on both channels
   (`Data/AUDIO/EN-US/RA{C,R}_SFX_EVA_*_EN-US.WAV`, seeded from the RA payloads): the nine lines plus
   structure-sold (`STRUSLD1`), which the DLL routes, so a fresh install
   caches TF's bytes. A deploy must never `--delete` them.
5. **A line is cacheable only after it has played.** `BCT` is fixed at the next match start.
6. **Never write on a needle alone.** Where the stale copies come from is on the EVA page's Traps; the patch
   zeroes its own buffers before freeing them. Without the whole-recording compare, the TD write of
   `TF_MBX_TD_NODEPLY_R.WAV` after a TS GDI match landed across a freed heap block (at `+976` into the write), and
   ClientG's heap failed on the next skirmish load.

#### Shipping notes

- When the process, a needle or a whole payload is not found, or a write is refused, the patch leaves memory alone
  and the line keeps the seed-file voice (right on its first play in a session, stale after a switch).
  Diagnostic logging (`Documents/CnCRemastered/tf_cache_probe.log`) is `TF_DEV_BUILD`-only: `PATCH OK` = replaced,
  `PATCH FAIL` = left alone.
- `scripts/eva_mailbox_payload.py` builds one TD + RA payload pair and prints its needle lines.
- Needles and offsets are regenerated whenever a payload is re-padded (the re-encode or pad changes the bytes). The
  generator picks a high-entropy 20-byte slice from the real audio (never the leading silence) and records its file
  offset.
- Cross-process `WriteProcessMemory` in a shipped mod could in principle trip aggressive AV or anti-cheat, but it
  targets only positively identified sample blobs in the sibling game process the DLL already reads. No report of it.
