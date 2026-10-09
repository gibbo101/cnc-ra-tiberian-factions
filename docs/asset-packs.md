# Asset packs

**Status:** Reference. The TS, RA2 and C&C3 asset packs: layout, routing by name, staging into
the build, and publishing.

The mod's Tiberian Sun, Red Alert 2 and C&C3 assets live in `asset-packs/`, one folder per Steam
Workshop item, so other modders can take them. Tiberian Factions' own files stay in
`resources/remaster_mods/Vanilla_RA/`. The build stages both into one mod.

## Layout

Each `asset-packs/<Pack>/` folder is exactly what is uploaded to the Workshop, in the TD-Assets
layout:

```
asset-packs/TS-Graphics-Pack/
  ccmod.json                 (scripts/asset_pack_docs.py)
  README.md                  (scripts/asset_pack_docs.py: contents, how to use, credits)
  Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS|STRUCTURES|VFX|TERRAIN/<THEATRE>/<NAME>.ZIP
  Data/ART/TEXTURES/SRGB/BuildIcon_<name>.tga
  Data/AUDIO/<NAME>.WAV, Data/AUDIO/EN-US/<NAME>_EN-US.WAV
  Data/XML/TILESETS/TS_UNITS.XML ...          (entries for RA_UNITS.XML ...)
  Data/XML/OBJECTS/UNITS/TSBUILDABLES.XML      (entries for RABUILDABLES.XML)
  Data/XML/AUDIO/SFXEVENTS[NON]LOCALIZED_TS.XML (entries for SFXEVENTS[NON]LOCALIZED.XML)
  3d/<name>.glb, 3d/README.md                (TS-HD only: the HD rebuilds' glTF models, never staged)
```

| Pack | Holds |
|---|---|
| TS-Graphics-Pack | TS structure, effect and apron art; plain TS cameos |
| TS-HD-Graphics-Pack | HD rebuilds of TS objects (GDI buildings, units, infantry, walls, gates, component towers), their HD cameos and 3D models |
| TS-SFX-Pack, TS-EVA-eng, TS-Voices-eng | TS effects, EVA lines, unit voices |
| RA2-Graphics-Pack, RA2-SFX-Pack, RA2-Voices-eng | RA2 tanks, their weapon and engine sounds, their crews |
| CNC3-Graphics-Pack, CNC3-SFX-Pack, CNC3-Voices-eng | C&C3 tanks, their weapon takes, their crews |

The launcher never loads a pack's XML files: its tileset list (`TILESETS.XML` in CONFIG.MEG) names
only the `RA_` files. A pack's XML files are what a modder copies, and what the build merges.

## What belongs where

`scripts/asset_packs.py` decides from a file's name alone, so nothing needs registering:

- Art: `TS*` and `RAILFX` (not `TSLA*`, RA's Tesla Coil), `R2*`, `C3<letter>` (bare `C3` is RA's
  civilian). The HD-rebuilt TS objects in its `TS_HD` list go to TS-HD.
- Cameos: the plain `BuildIcon_` of those objects. An HD cameo (`scripts/ts_hd_cameos.py`) goes in
  TS-HD beside its classic one in TS-Graphics-Pack. Staging copies a file two packs carry from the
  later pack only, and the variant bakers read the HD one (`cameo_source`). The `_G`, `_LK` and `_<n>`
  variants and the `SW_`/`SG_` superweapon cameos drive the mod's sidebar and stay in
  `resources/`.
- Sounds: `TS_SFX_EVA_*` EVA, `TS_SFX_UNT_*` voices, other `TS*` effects; RA2 and C&C3 crew lines
  (`SE`/`MO`/`AT` takes) apart from their weapon and engine sounds. `TF_MBX_*` (the EVA mailbox)
  and `TSLACHG2R` stay. TS sounds bundled under TD sample names (`TDR_SFX_DINOATK1` and friends)
  stay with the events that play them.
- XML entries follow their object, cameo or samples. A sound event goes to a pack only when every
  sample it plays is in that pack.

## Working with it

- **Pack scripts** take every output and input path from `asset_packs` by name (`art_zip`,
  `tileset_xml`, `cameo_tga`, `buildables_xml`, `sound_wav`, `sfx_xml`). A new TS unit's art lands
  in TS-Graphics-Pack with no other change.
- **One copy of each frame:** a shape whose image matches an earlier one in its ZIP names that one
  in the tileset XML, and the copy leaves the ZIP. Run `scripts/dedupe_tileset_frames.py` after any
  packer that writes a ZIP; the packager refuses a build that still holds duplicates.
- **Shared copies:** a type whose ZIP copies another's (the tower plugs, the faction yards, gates and
  MCVs) keeps its own ZIP in the source tree, so a reskin touches one type. Staging draws its frames
  from the first identical ZIP and leaves the copy out of the build (`scripts/share_tileset_zips.py`;
  run it alone to list what it would leave out).
- **Cameos** stay uncompressed in the source; staging writes each `BuildIcon_*` TGA run-length
  encoded, the same pixels at about four fifths the size.
- **Build:** the CMake post-build step copies `resources/remaster_mods/Vanilla_RA`, then
  `scripts/stage_asset_packs.py` copies every pack's art and audio and writes the merged XML: each
  pack's entries replace the `<!-- asset-pack: <Pack> -->` marker in the mod's file. Staging always
  starts from the source XML, so it can run any number of times.
- **Data-only change** (no DLL relink, so the post-build step does not run):
  `python3 scripts/stage_asset_packs.py --full build/remaster/Vanilla_RA`.
- **Stray files:** the build stops when a pack file or entry sits in `resources/` (a script that still
  writes the old path, or a branch from before the packs). `python3 scripts/asset_packs.py split`
  moves them: a re-written object replaces its old entries, a generated BEGIN/END block replaces the
  block of the same name. `check` reports without moving.
- **After adding to a pack:** `python3 scripts/asset_pack_docs.py` refreshes its README and
  ccmod.json.
- **Publishing:** `python3 scripts/asset_pack_workshop.py` stages each pack for upload and writes
  its Workshop manifest and preview; the steps are in `docs/workshop-publish-runbook.md` (Asset
  packs).

## Not yet in the packs

- Classic-mode stub SHPs: they are built into `CCDATA/TFASSETS.MIX` with the mod's own TD art.
  The pack READMEs point modders at `scripts/gen_stub_shp.py`.
- The TS sounds bundled under TD sample names stay with the mod until their events are renamed.
- Only English audio exists, so there are no other language packs.
