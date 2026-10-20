# Asset packs

**Status:** Reference. The TS, RA2 and C&C3 asset packs and the TS-Music pack: layout, routing by name,
staging into the build, and publishing. TS-Music is withdrawn from the Workshop (`ts-music-import.md`).

The mod's Tiberian Sun, Red Alert 2 and C&C3 assets live in `asset-packs/`, one source folder per pack.
`asset_packs.WORKSHOP` builds the Workshop items from them (`scripts/workshop_packs.py`): TS-HD-Assets,
RA2-HD-Assets and CNC3-Assets, each as a Red Alert item and a Tiberian Dawn one, and TS-Music for Red Alert, which
stays Private: EA's C&C modding guidelines don't allow a mod to include C&C music files. Tiberian Factions' own files stay
in `resources/remaster_mods/Vanilla_RA/`.

## Layout

Each `asset-packs/<Pack>/` source folder has the TD-Assets layout:

```
asset-packs/TS-HD-Graphics-Pack/
  ccmod.json                 (scripts/asset_pack_docs.py)
  README.md                  (scripts/asset_pack_docs.py: contents, how to use, credits)
  Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS|STRUCTURES|VFX|TERRAIN/<THEATRE>/<NAME>.ZIP
  Data/ART/TEXTURES/SRGB/BuildIcon_<name>.tga
  Data/AUDIO/<NAME>.WAV, Data/AUDIO/EN-US/<NAME>_EN-US.WAV
  Data/XML/TILESETS/TSHD_UNITS.XML ...          (entries for RA_UNITS.XML ...)
  Data/XML/OBJECTS/UNITS/TSHDBUILDABLES.XML      (entries for RABUILDABLES.XML)
  Data/XML/AUDIO/SFXEVENTS[NON]LOCALIZED_TSHD.XML (entries for SFXEVENTS[NON]LOCALIZED.XML)
  3d/<name>.glb, 3d/README.md                (TS-HD only: the HD rebuilds' glTF models, never staged;
                                              scripts/glb_to_stl.py makes print-ready STL files from them)
```

A Tiberian Dawn item's terrain ships as loose files, one folder per ZIP: TD's terrain never reads a mod's ZIP.

| Pack | Holds |
|---|---|
| TS-HD-Graphics-Pack | HD rebuilds of TS GDI's objects (buildings, units, infantry, walls, gates, component towers), their HD cameos and 3D models, and TS's effects |
| TS-Nod-Graphics-Pack | HD rebuilds of TS Nod's objects, held out of TS-HD-Assets until TS Nod ships whole; the mod carries them for its crate units |
| TS-SFX-Pack, TS-EVA-eng, TS-Voices-eng | TS effects, EVA lines, unit voices |
| RA2-Graphics-Pack, RA2-SFX-Pack, RA2-Voices-eng | RA2 tanks, their weapon and engine sounds, their crews |
| CNC3-Graphics-Pack, CNC3-SFX-Pack, CNC3-Voices-eng | C&C3 tanks, their weapon takes, their crews |

The launcher never loads a pack's XML files: its tileset list (`TILESETS.XML` in CONFIG.MEG) names
only the `RA_` files. A pack's XML files are what a modder copies, and what the build merges.

## What belongs where

`scripts/asset_packs.py` decides from a file's name alone, so nothing needs registering:

- Art: `TS*` (not `TSLA*`, RA's Tesla Coil), `R2*`, `C3<letter>` (bare `C3` is RA's
  civilian). TS art goes to TS-HD, TS Nod's (its `TS_NOD` lists) to TS-Nod.
- Cameos: the plain `BuildIcon_` of those objects (`scripts/ts_hd_cameos.py` installs the HD ones). A
  TS-named cameo of the mod's own object stays in `resources/` (`OWN_TS_CAMEOS`: TD Nod's Stealth
  Generator, drawn from TS art). The `_G`, `_LK` and `_<n>`
  variants and the `SW_`/`SG_` superweapon cameos drive the mod's sidebar and stay in
  `resources/`.
- Sounds: `TS_SFX_EVA_*` EVA, `TS_SFX_UNT_*` voices, other `TS*` effects; RA2 and C&C3 crew lines
  (`SE`/`MO`/`AT` takes) apart from their weapon and engine sounds. `TF_MBX_*` (the EVA mailbox)
  and `TSLACHG2R` stay. Every TS sound ships under its own `TS*` name, so its file and events go to
  the TS pack.
- XML entries follow their object, cameo or samples. A sound event goes to a pack only when every
  sample it plays is in that pack.

## Working with it

- **Pack scripts** take every output and input path from `asset_packs` by name (`art_zip`,
  `tileset_xml`, `cameo_tga`, `buildables_xml`, `sound_wav`, `sfx_xml`). A new TS unit's art lands
  in TS-HD-Graphics-Pack with no other change; a new TS Nod object needs its name in `TS_NOD`.
- **One copy of each frame:** in an object tileset (structures, units, effects), a shape whose image
  matches an earlier one in its ZIP names that one in the tileset XML, and the copy leaves the ZIP.
  TERRAIN tiles (bibs, smudges) stay one file per shape: the launcher draws a cell only from the frame
  its own shape names, and shows its placeholder for a shared one. Run `scripts/dedupe_tileset_frames.py` after any
  packer that writes a ZIP; the packager refuses a build that still holds duplicates.
- **Shared copies:** a type whose ZIP copies another's (the tower plugs, the faction yards, gates and
  MCVs) keeps its own ZIP in the source tree, so a reskin touches one type. Staging draws its frames
  from the first identical ZIP and leaves the copy out of the build (`scripts/share_tileset_zips.py`;
  run it alone to list what it would leave out).
- **Pack-only objects:** `asset_packs.PACK_ONLY` names art only the Workshop pack carries (the C&C3
  railgun tanks): staging leaves out their ZIPs and tiles, so the mod ships no art it never draws.
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
- **Publishing:** `python3 scripts/asset_pack_workshop.py` stages each Workshop item (a pack for
  Red Alert, or `<mod>-TD` for Tiberian Dawn) and writes its manifest and preview; the steps are in
  `docs/workshop-publish-runbook.md` (Asset packs).

## Required packs

`asset_packs.REQUIRED` lists the Workshop items the mod depends on: TS-HD-Assets, built from the TS source packs.
The mod keeps only their XML entries; their art and audio ship in the item.

- **Build and deploy:** staging builds each required item whole in the folder beside the mod
  (`build/remaster/TS-HD-Assets`), and `deploy.sh` mirrors both folders. `deploy.sh --mod-only` mirrors the mod
  alone, for testing the item subscribed from the Workshop.
- **Detection:** the item carries `CCDATA/TSHDPACK.INI` with its version. The DLL reads it from each enabled mod's
  CCDATA path (`tf_asset_pack.cpp`): without it, a TS GDI pick plays another side and crates skip TS units. The
  launcher finds the marker in its mod list for the main menu's add-ons notice and the lobby popup
  (`pack-panel.md`), and saves record whether the pack was on.
- **TS Nod:** TS-Nod-Graphics-Pack holds TS Nod's HD art (`asset_packs.TS_NOD`). It is in no Workshop item yet:
  staging copies it into the mod for the crate units, until TS Nod ships and joins TS-HD-Assets.
- **ModDB:** `package-for-workshop.sh` zips the mod with each required item beside it, and each item alone
  (`scripts/moddb_zips.py`).

## Used packs

`asset_packs.USED` adds the optional items the mod plays from when they are enabled: TS-Music, Tiberian Sun and
Firestorm's 26 in-game themes for Red Alert. Like a required item it stays its own folder beside the mod, so
staging builds it there (`build/remaster/TS-Music`) and `deploy.sh` mirrors it; unlike one, the mod runs without
it. Its WAVs are gitignored and rebuilt from an installed Tiberian Sun by `scripts/ts_music_build.py`; the
item carries `CCDATA/TSMUSIC.INI`. How the mod uses it is in `skirmish-music.md`. It is not published; players
will build the same folder from their own Tiberian Sun (`ts-music-import.md`).

## Not yet in the packs

- Classic-mode stub SHPs: they are built into `CCDATA/TFASSETS.MIX` with the mod's own TD art.
  The pack READMEs point modders at `scripts/gen_stub_shp.py`.
- Only English audio exists, so there are no other language packs.
