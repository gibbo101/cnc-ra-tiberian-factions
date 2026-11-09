# CONFIG.MEG mod delivery

**Status:** Reference. A mod ships its own `Data/CONFIG.MEG` and the launcher loads it over the
base; every front-end data edit in the mod rides on it.

The routes (a replacement archive, loose files, `GameConstants_Mod.xml`), the same-size rule and what none of them
reach are game-level: see the field manual's
[Overriding the launcher's data](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/launcher-data/overriding-launcher-data.md#three-ways-in)
(Three ways in, [A replacement `CONFIG.MEG`](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/launcher-data/overriding-launcher-data.md#a-replacement-configmeg)
and [Traps](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/launcher-data/overriding-launcher-data.md#traps)), and [MEG and MIX archives](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/formats/meg-and-mix-archives.md#meg).
Before calling a launcher feature locked, follow
[What the launcher owns](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/what-the-launcher-owns.md#search-in-this-order),
Search in this order. This doc is TF's data-delivery lever; `launcher-vs-dll-ownership.md` is TF's code-ownership
map, and `config-meg-lever-audit.md` lists the levers.

## What TF ships

TF ships the full archive (44,201,888 bytes) in every release, at `resources/remaster_mods/Vanilla_RA/Data/CONFIG.MEG`,
and loose files beside it (`campaigns-page.md` ships its screens loose). `scripts/build_config_meg.sh` rebuilds every
edit in it idempotently from the pristine base, each by its own script (the `python3` calls in the script's body):
- **Inside CONFIG.MEG:** the main menu (`RA_MAIN_MENU.BUI`), the HUD's side label hidden (`RA_TACTICAL_UI.BUI`,
  `hud_label_hide_build.py`), the confirmation box, the loading screen, the lobbies, the faction combo box and the
  custom-map entry, the font styles (`FONTLIBRARY.BFD`), the music events (`MUSICEVENTS.XML`), the master text
  (`MASTERTEXTFILE_EN-US.LOC`, `loc_relabel.py`), `FACTIONS.XML`, and `GUITEXTURESETS.XML`
  (`gui_texturesets_build.py`).
- **Loose beside it:** the main menu with its added rows, the ADD-ONS screen and its art, the Settings page, the TF
  playlists (`MUSICEVENTS.XML`), the jukebox list (`AUDIO_SYSTEM_CONSTANTS.XML`) and its titles in `ModText.csv`.

The script's header comment leaves out the HUD label, the music, the master text and `GUITEXTURESETS.XML`, and
still describes a `GAMECONSTANTS.XML` bake: its `GAMECONSTANTS` and `INPUTTRANSLATORCONFIGURATIONS` variables are set
but unused, and no loose copy of either ships. `TF_MEG_TARGET` points it at the packager's staged copy. TF pads each edited member back to size from
its XML comments, then checks the member and the archive total against the base. A repack can't corrupt the base
install or trip Steam's file check, since it ships in the mod folder; one that changes any member's size crashes
the launcher at boot under the mod
([Crash triage](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/troubleshooting/crash-triage.md#4-a-clientg-crash-at-rva-0x56a539-is-an-assert)
reads that crash).

## The recipe for a one-off edit

```bash
# 1. extract the inner file you want to change
python3 scripts/meg_extract.py extract <base CONFIG.MEG> <innerPathFragment> /tmp/out/

# 2. edit it, keeping every member at its exact base size.
#    XML: pad back to size from comments. .LOC: the file total is fixed, but a string may
#    grow if it takes bytes from another (byte-neutral redistribution, scripts/loc_relabel.py).

# 3. repack (replaces the inner file whose stored path ENDS WITH the given suffix)
python3 scripts/meg_pack.py repack <base CONFIG.MEG> /tmp/CONFIG.MEG \
    "<innerSuffix>=/tmp/edited_file"

# 4. ship it in the MOD folder (NOT the base install), then deploy
cp /tmp/CONFIG.MEG build/remaster/Vanilla_RA/Data/CONFIG.MEG
./deploy.sh --no-build --yes
```

`meg_pack.py verify a.meg b.meg` confirms identical file tables (name and size); use it to check a repack. List
what the archive holds with `meg_extract.py list <CONFIG.MEG> | grep -i <feature>`. Not in CONFIG.MEG isn't locked:
check the UI atlas too (`ui-atlas-modding.md`), where the radar crest is `UI_SIDEBAR_FACTIONLOGO_ALLIES`/`_SOVIET`.

**How it was verified:** `MASTERTEXTFILE_EN-US.LOC` extracted from the base archive, the country name `Turkey`
changed to `Nod   ` (UTF-16LE, 12 bytes for 12, so no string-table offset moves), repacked to the base's exact
size, shipped as `<mod>/Data/CONFIG.MEG` with the base install untouched. On the Steam Deck the lobby's country
picker showed "Nod : No bonus" and the in-game sidebar read "Nod".

## What it reaches

- **Faction display names:** `MASTERTEXTFILE` `TEXT_FACTION_NAME_FACTION_*` (`faction-select-identity.md`).
- **Faction colours and lobby icons:** `FACTIONS.XML`, whose entries are laid out on the field manual's
  [Adding a faction](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/adding-a-faction.md).
  Each entry's `FactionObjects` is empty (EA ties it to the structure breakdown screen), and its `CampaignType` is
  the TD/RA gate.
- **The Mission Select roster:** `INSTANCES.XML` (`campaign-tabs-research.md`).
- **Any other CONFIG.MEG XML or table:** theatres and tilesets, audio-faction maps, GUI scene lists. If the data is
  in CONFIG.MEG, this reaches it.

It feeds the ClientG front end only. `InstanceServerG` resolves instances, map files and the lobby preview from the
base game's data; why a new entry lists but won't start, the carrier that starts it, and where map INIs are read
from (a mod's `CCDATA/`, never its own `Data/CNCDATA/`) are on the field manual's
[New maps in the skirmish Official list](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/maps-and-lobby/new-maps-in-the-skirmish-list.md#why-a-listed-map-wont-start),
Why a listed map won't start, and its [Converting the map](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/maps-and-lobby/new-maps-in-the-skirmish-list.md#converting-the-map) (the `CCDATA/` rule).
TF's own tests: the assert at `serveripcmessagehandler.cpp(268)`, and a hijacked `Community_2` that still loaded
`SCMC1EA`. TF launches its new entries through Hastings' `D6` (`td-base-art.md`, "TD maps in the Official list");
`campaign-tabs-research.md` covers TF's campaign maps. Workshop map items (the custom-maps tab, the native pipeline,
previews from the shipped TGA) remain the plain route.

## Related

- `campaign-tabs-research.md`: the Mission Select display model, distributed through this archive.
- `mix-file-format.md`: the `meg_extract.py` and `meg_pack.py` tooling and the format detail.
- `launcher-vs-dll-ownership.md`: the code-side boundary, which this does not change.
