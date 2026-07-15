# TD audio routing recipe — playing TD .WAV assets in RA mod mode

**Status:** PROVEN 2026-05-21 — Obelisk laser sound (`OBELRAY1.WAV`) plays end-to-end in our RA mod via this exact pipeline. Use this doc as the canonical reference for every TD audio asset we bring across (weapons, building construction loops, EVA voice eventually).

**TL;DR:**

1. Add `VOC_TD_*` enum entry to `redalert/defines.h` (before `VOC_COUNT`).
2. Add `SoundEffectName[]` entry in `redalert/audio.cpp` with the TD asset's bare name (e.g. `"OBELRAY1"`).
3. Extract `.WAV` from `~/.steam/.../Data/SFX3D.MEG` via `scripts/meg_extract.py`. Both `TDC_SFX_X.WAV` (classic mode) and `TDR_SFX_X.WAV` (remastered mode) need to ship.
4. Place the extracted WAVs **unchanged** in `resources/remaster_mods/Vanilla_RA/Data/AUDIO/`.
5. Merge — **don't replace** — the base `SFXEVENTSNONLOCALIZED.XML` from `CONFIG.MEG` with alias `SFXEvent` entries, then ship the merged file at `Vanilla_RA/Data/XML/AUDIO/SFXEVENTSNONLOCALIZED.XML`.
6. Reference the sound by its bare name in rules.ini (`Report=OBELRAY1`) — the DLL passes it via `SoundEffectName.Name` to the launcher; launcher prepends `RAR_SFX_` / `RAC_SFX_` and resolves the alias from our XML.

---

## How the launcher resolves audio

`dllinterface.cpp:2575-2581`:

```cpp
strncpy(new_event.SoundEffect.SoundEffectName, SoundEffectName[sound_effect_index].Name, 16);
if (extension != NULL) {
    strncat(new_event.SoundEffect.SoundEffectName, extension, 16);
}
new_event.SoundEffect.SoundEffectPriority = SoundEffectName[sound_effect_index].Priority;
new_event.SoundEffect.SoundEffectContext  = SoundEffectName[sound_effect_index].Where;
```

The DLL ships the `Name` field as a **string** (max 15 chars + null). The launcher then:

1. Prepends `RAR_SFX_` (remastered audio mode) or `RAC_SFX_` (classic audio mode) to the Name.
2. Looks up the resulting `RAR_SFX_X` / `RAC_SFX_X` as the `Name=` attribute of an `<SFXEvent>` in `Data/XML/AUDIO/SFXEVENTSNONLOCALIZED.XML`.
3. Reads the matched SFXEvent's `<SampleNamesList>` to find the actual `.WAV` file to play from `Data/AUDIO/`.

The crucial insight: the `<SFXEvent>`'s `Name=` attribute is what the launcher matches, but the `<SampleNamesList>` can point at ANY `.WAV` file. So we create **alias SFXEvents** that look like RA entries (RAR_/RAC_ prefix) but route to TD `.WAV` files (TDR_/TDC_).

The DLL stays clean — it knows nothing about which game the audio originated from. It just passes the bare name like `"OBELRAY1"`.

---

## Concrete walkthrough — adding Obelisk laser sound (the worked example)

### 1. DLL enum + sound table entry

`redalert/defines.h` — add before `VOC_COUNT`:

```cpp
VOC_TD_LASER, // Obelisk humming laser beam
```

`redalert/audio.cpp` — add to `SoundEffectName[]` array:

```cpp
{"OBELRAY1", 1, IN_NOVAR}, // VOC_TD_LASER (Obelisk humming laser beam)
```

### 2. Extract the .WAV files

```bash
python3 scripts/meg_extract.py extract \
  ~/.steam/steam/steamapps/common/CnCRemastered/Data/SFX3D.MEG \
  OBELRAY1 \
  /tmp/extract/
```

Yields:

- `TDC_SFX_OBELRAY1.WAV` (classic mode — DOS-era AUD-source recording, ~14KB)
- `TDR_SFX_OBELRAY1.WAV` (remastered mode — modern HD recording, ~36KB)

### 3. Ship the .WAV files

Place verbatim (no rename) at:

```
resources/remaster_mods/Vanilla_RA/Data/AUDIO/TDC_SFX_OBELRAY1.WAV
resources/remaster_mods/Vanilla_RA/Data/AUDIO/TDR_SFX_OBELRAY1.WAV
```

### 4. Merge base XML + alias SFXEvents

Extract the base XML from `CONFIG.MEG`:

```bash
python3 scripts/meg_extract.py extract \
  ~/.steam/steam/steamapps/common/CnCRemastered/Data/CONFIG.MEG \
  SFXEVENTSNONLOCALIZED \
  /tmp/sfx_extract/
```

Then inject alias entries before the closing `</SFXEvents>` tag:

```xml
  <SFXEvent Name="RAC_SFX_OBELRAY1" Preset="_PRESET_MD_MOBIUS_2D">
    <IsPreset> False </IsPreset>
    <MinPitch>100</MinPitch>
    <MaxPitch>100</MaxPitch>
    <SampleNamesList>
      <entry> TDC_SFX_OBELRAY1.WAV </entry>
    </SampleNamesList>
  </SFXEvent>

  <SFXEvent Name="RAR_SFX_OBELRAY1" Preset="_PRESET_MD_MOBIUS_2D">
    <IsPreset> False </IsPreset>
    <MinPitch>100</MinPitch>
    <MaxPitch>100</MaxPitch>
    <SampleNamesList>
      <entry> TDR_SFX_OBELRAY1.WAV </entry>
    </SampleNamesList>
  </SFXEvent>
```

Save merged file as:

```
resources/remaster_mods/Vanilla_RA/Data/XML/AUDIO/SFXEVENTSNONLOCALIZED.XML
```

### 5. Reference from rules.ini

```ini
[TDOblsLaser]
Damage=200
ROF=90
Range=7.5
Projectile=TDLaser
Speed=255
Warhead=TDLaser
Report=OBELRAY1     ; ← resolves to VOC_TD_LASER → RAR_SFX_OBELRAY1 alias → TDR_SFX_OBELRAY1.WAV
```

---

## Critical gotchas (learned the hard way 2026-05-21)

### Must MERGE, not REPLACE, the base XML

Shipping only our 5 entries (instead of base 578 + our 4 = 582) causes the launcher to crash because every base sound reference becomes a dangling lookup. Always extract from `CONFIG.MEG` first, append ours, ship the merged file.

### XML must be well-formed — no `--` inside comments

XML 1.0 spec forbids `--` inside comment blocks. Easy mistake when writing comments like `<!-- foo -- bar -->`. The launcher's XML parser will choke and crash the launcher between game-select and main-menu. Use `:` or em-dashes (`—`) instead.

Validate with:

```bash
python3 -c "import xml.etree.ElementTree as ET; ET.parse('path/to/SFXEVENTSNONLOCALIZED.XML')"
```

### Both RAC_ and RAR_ aliases needed

The launcher uses different prefixes per audio mode:

- `RAC_SFX_X` — classic audio mode
- `RAR_SFX_X` — remastered audio mode

User can toggle at runtime via Options → Audio. Without both aliases, one mode plays the right sound and the other is silent.

### File format hygiene

- **UTF-8 BOM**: keep the `ef bb bf` byte sequence at the file head. The base XML has it; preserve it through any merge tooling.
- **CRLF line endings**: base XML is CRLF. If you append with `\n` you get mixed line endings, which the launcher's XML parser may handle inconsistently. Use `\r\n` explicitly.

### Preset definitions

`_PRESET_MD_MOBIUS_2D` and other presets are defined in the base XML. When you merge base + additions, the references resolve. If you ever ship a standalone (non-merged) XML, you must include the preset definition block too — otherwise the launcher crashes resolving the reference.

### Whitespace inside `<entry>` tags

Reilsss's reference mod uses `<entry> TDC_SFX_OBELRAY1.WAV </entry>` with spaces inside. We've replicated this pattern for safety, though unclear if the launcher is whitespace-strict.

---

## Reference precedent

The Remastered Workshop mod **Reilsss's CnCinRA** (workshop ID `2853520457`) was the breakthrough source for this recipe. Their `DATA/XML/AUDIO/SFXEVENTSNONLOCALIZED.XML` already had `RAC_SFX_OBELRAY1` / `RAR_SFX_OBELRAY1` SFXEvents routing to `TDC_/TDR_SFX_OBELRAY1.WAV` — proving the pattern works in production. They ship 88 `.WAV` files this way, mostly TD assets re-aliased into RA mode.

Their mod folder structure (at `~/.steam/steam/steamapps/workshop/content/1213210/2853520457/ReilsssCnCinRA/`):

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

## What this unlocks

With the audio routing pipeline proven, every future TD asset port follows the same recipe:

- **Weapon sounds**: TowTwo (ROCKET2), TdTurretGun (TNKFIRE6), and all future weapon ports
- **Building construction loops**: TD's distinct construction "grinding" sound, building-complete chime, etc.
- **Unit responses**: TD voice acting for infantry/vehicles ("Reporting", "Yes sir", etc.) — uses `VoxType` table (different from `VocType`) but same overlay-and-alias mechanism via a different XML
- **EVA voice**: faction-aware ("New Construction Options", "Cannot Deploy Here", etc.) — also `VoxType`, faction routing decided in the DLL based on player house

The audio identity of TD becomes available in RA mode without launcher modification.

---

## EVA voice (VoxType) faction routing — VALIDATED (migrated from memory 2026-07-15)
44-voice catalogue, GDI+Nod share. Speak(VOX_X) -> On_Speech (dllinterface.cpp) consults `SpeechTD[]`
(audio.cpp): if `player_ptr->ActLike == HOUSE_GOOD||HOUSE_BAD` and `SpeechTD[X]!=NULL`, send the
TD-prefixed name (e.g. TDIONCHRG1); else Speech[X]. Launcher resolves `RAC_SFX_TD<NAME>` /
`RAR_SFX_TD<NAME>` in mod SFXEVENTSLOCALIZED.XML -> base-shipped `TDC_/TDR_SFX_EVA_<NAME>_EN-US.MP3`
(no WAV reship). Shared semantic VOX: keep enum, set SpeechTD[]. TD-only events: new VOX_TD_* enums,
Speech[]="TD<NAME>". VoxType backing bumped char->short (>127 entries).
