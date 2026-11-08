# TD audio routing recipe — playing TD .WAV assets in RA mod mode

**Status:** Reference. How a sound reaches the launcher from the DLL, with the Obelisk laser
(`OBELRAY1`) as the worked example; every TD and TS sound in the mod ships this way.

See the field manual's [TD sounds from the base game](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-sounds-from-the-base-game.md#the-method), The method.
TF's files: the `VOC_TD_*` entries in `redalert/defines.h`, the `SoundEffectName[]` entries in
`redalert/audio.cpp`, and the merged `resources/remaster_mods/Vanilla_RA/Data/XML/AUDIO/SFXEVENTSNONLOCALIZED.XML`.
Base files come out with `scripts/meg_extract.py`. TF ships no WAV for a routed TD sample, apart from copies of a
few early ones (the Obelisk's laser among them); its own new sounds ship in
`resources/remaster_mods/Vanilla_RA/Data/AUDIO/` under their own names.

---

## How the launcher resolves audio

What the launcher does with the name the DLL sends, and the variant suffix a unit response gets, are on the field
manual's [TD sounds from the base game](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-sounds-from-the-base-game.md#how-a-sound-gets-from-the-dll-to-the-speakers), How a sound gets from the DLL to the speakers.
TF's copy is `On_Sound_Effect` in `redalert/dllinterface.cpp`; besides the name, the event carries
`SoundEffectPriority` and `SoundEffectContext`, copied from the table entry's `Priority` and `Where`.

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

The Remastered Workshop mod **Reilsss's CnCinRA** (workshop ID `2853520457`) was the breakthrough source for this recipe. Their `DATA/XML/AUDIO/SFXEVENTSNONLOCALIZED.XML` already had `RAC_SFX_OBELRAY1` / `RAR_SFX_OBELRAY1` SFXEvents routing to `TDC_/TDR_SFX_OBELRAY1.WAV` — proving the pattern works in production. They ship 88 `.WAV` files this way, mostly TD assets re-aliased into RA mode.

Their mod folder structure (at `<Steam library>/steamapps/workshop/content/1213210/2853520457/ReilsssCnCinRA/`; `scripts/steam_library.py` finds the library):

```
ReilsssCnCinRA/
├── ccmod.json
├── CCDATA/
│   ├── a_rules.ini
│   ├── aftrmath.ini
│   ├── mplayer.ini
│   └── EXPAND2.MIX
└── DATA/
    ├── ART/...
    ├── XML/
    │   ├── OBJECTS/
    │   ├── TILESETS/
    │   └── AUDIO/
    │       └── SFXEVENTSNONLOCALIZED.XML
    └── AUDIO/
        ├── RAC_SFX_*.WAV  (88 files — TD audio re-aliased)
        ├── EN-US/
        ├── DE-DE/
        └── FR-FR/
```

Their pattern names files with the RA prefix directly (`RAC_SFX_OBELRAY1.WAV`) rather than keeping TD names. Both approaches work — our pattern keeps `.WAV` filenames as TD originals and uses the SFXEvent `<SampleNamesList>` to bridge, which makes provenance clearer in the file tree.

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
44-voice catalogue, GDI+Nod share. Speak(VOX_X) -> On_Speech (dllinterface.cpp) consults `SpeechTD[]`
(audio.cpp): if `player_ptr->ActLike == HOUSE_GOOD||HOUSE_BAD` and `SpeechTD[X]!=NULL`, send the
TD-prefixed name (e.g. TDIONCHRG1); else Speech[X]. Launcher resolves `RAC_SFX_TD<NAME>` /
`RAR_SFX_TD<NAME>` in mod SFXEVENTSLOCALIZED.XML -> base-shipped `TDC_/TDR_SFX_EVA_<NAME>_EN-US.MP3`
(no WAV reship). Shared semantic VOX: keep enum, set SpeechTD[]. TD-only events: new VOX_TD_* enums,
Speech[]="TD<NAME>". VoxType backing bumped char->short (>127 entries).
