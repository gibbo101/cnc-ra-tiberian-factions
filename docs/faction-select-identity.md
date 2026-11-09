# Faction-select identity in the RA lobby: the CONFIG.MEG recipe

**Status:** Reference. The lobby picker's names, icons and HUD scenes, and the mod's
`ModText.csv` names.

The lobby picker, map markers and loading badges show five factions: Spain plays GDI, Greece Nod,
Germany TS GDI, England Allies and USSR Soviet, with the other countries as duplicates. Names
come from `scripts/loc_relabel.py` (`scripts/loc_work/mastertext.edits.txt`), entries and HUD
scenes from `scripts/factions_build.py`, both built into the mod's `Data/CONFIG.MEG` by
`build_config_meg.sh`; the crests are painted into the loose UI atlas by
`scripts/picker_emblems_paint.py` (`ui-atlas-modding.md`). No EMC, no texture MEG. Companion to
`config-meg-mod-delivery.md` (the delivery mechanism).

The launcher's data for a lobby row (the three strings, the `FACTIONS.XML` entries, the emblem, the colours and the
HUD scene) and the crashes to avoid are on the field manual's
[Adding a faction](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/adding-a-faction.md#the-launchers-data-for-the-row)
(The launcher's data for the row, and Traps); the `.LOC` table is on its
[New text strings](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/launcher-data/new-text-strings.md#relabel-strings-the-loc-table-at-its-exact-size)
(Relabel strings).

## The three levers

### 1. Picker icon: `FACTIONS.XML` `SmallIconName`
It may point only at the preloaded player-slot icons, whose pixels are repainted in the loose atlas
(`ui-atlas-modding.md`; the manual's
[Pick the right region](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/the-ui-atlas.md#pick-the-right-region)).
Pointing it at `UI_SIDEBAR_FACTIONLOGO_*` or `RA_UI_MULTIPLAYER_*_LOGO` crashes the launcher at startup.

### 2. Picker name and bonus overlay: `MASTERTEXTFILE_<lang>.LOC`
TF collapses each bonus overlay (`..._SPAIN` = "Spain: 10% more armor, damage, and speed for infantry") to just the
faction name.

Country to keys: SPAIN/GREECE/RUSSIA(=USSR)/TURKEY/ENGLAND/GERMANY/FRANCE/UKRAINE for `_BONUS_`;
`_NAME_FACTION_3/4/5/6/7/8/9/10` for the names.

The file keeps its total size; a value may outgrow its slot by taking bytes from another string. In TF a 14-character
slot holds "Unholy Alliance", one character reclaimed from a neighbouring tooltip. `scripts/loc_relabel.py` does
this: values that still fit keep their slot, one that outgrows it is stored at its true length, and a nominated
slack string absorbs the difference. `scripts/loc_edit.py` only overwrites values in place, and round-trips the base
file byte-identical. The bonus strings are long (16–53 characters), so any faction name fits; the
`NAME_FACTION_5`="USSR" slot is only 4 characters, so "Soviet" won't fit there, but the overlay the player sees is
`BONUS_RUSSIA` (43 characters), which fits "Soviet".

### 3. Delivery: the mod's `Data/CONFIG.MEG`
Repack the base CONFIG.MEG with the two edited files and ship it as the mod's `Data/CONFIG.MEG`:
```
python3 scripts/meg_pack.py repack <base CONFIG.MEG> <out> \
    "MISC/FACTIONS.XML=<edited factions.xml>" \
    "MASTERTEXTFILE_EN-US.LOC=<edited .loc>"
```
There is a `MASTERTEXTFILE_<lang>.LOC` per language (EN-US, FR-FR, DE-DE…); edit the ones you ship for (EN-US
covers English installs).

## Picker layout: one crest per row, launcher order

The picker's order is the launcher's, not data (the manual's
[Traps](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/adding-a-faction.md#traps)),
so the rows are assigned by position (DLL remap in `CNC_Set_Multiplayer_Data`, names in
`scripts/loc_work/mastertext.edits.txt`, plates painted by `scripts/picker_emblems_paint.py`):

| row | country | plays as | plate |
|---|---|---|---|
| 1 | Spain | GDI (`HOUSE_GOOD`) | `_03` GDI radar crest |
| 2 | Greece | Nod (`HOUSE_BAD`) | `_04` Nod radar crest |
| 3 | USSR | Soviet | `_05` Soviet crest |
| 4 | England | Allies | `_06` Allied crest |
| 5 | Ukraine | Soviet duplicate | `_07` Soviet crest |
| 6 | Germany | TS GDI (`HOUSEF_TSGDI`) | `_08` TS GDI crest |
| 7-8 | France / Turkey | Allied duplicates | `_09` / `_10` Allied crest |

All three hijacked countries are Allied-side to the launcher. Every row uses its country's own 150x80 plate, never
TD's 66x56 `_00`/`_01` icons, so every row is the same size: `scripts/factions_build.py` (`ICONS`, run by
`build_config_meg.sh`) sets Spain's and Turkey's `SmallIconName`s to `_03` and `_10` over the build's base copy,
which gives them `_00`/`_01`. Plates are the metallic radar crests alone on a transparent region, slightly softened
because the list draws them at about a third of their size with no mip filtering. The slot box fits the plate by
width (a 40x40 region pointed there draws as a 150x80 oval), so the crest is scaled to the plate's full height and
that is the box's limit.

**Map markers and loading screen:** the start-position badges on the lobby map and the player badges on the loading
screen both draw `UI_MAPSELECT_FACTION_NN` (40x40: `_01` GDI, `_02` Nod, `_03` Spain .. `_10` Turkey, so the
countries share the plates' numbers and only TD's two sit one above). The base flag sits in a 22px disc with the
launcher's player-colour ring behind it, so the crests are painted at 22px inside those regions
(`picker_emblems_paint.py` too). The plate is not involved: pointing it elsewhere in memory changed the lobby row and
nothing on the loading screen.

## TD HUD scene per faction: the sidebar is data

The scene swap is on the manual's
[The launcher's data for the row](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/adding-a-faction.md#the-launchers-data-for-the-row).
`factions_build.py` (`TD_HUD`) swaps the two scene names inside the GDI, Nod and TS GDI entries, so those factions
load TD's whole HUD scene: the wide sell/repair/map bar, TD's pip power meter, TD tab icons, green credits,
no side label. Allies and Soviets keep RA's scene.

Two consequences:
- TD's scene picks its faction logo by RA side (Allied the eagle, Soviet the scorpion), and Nod and TS GDI sit on the Allied side, so the crest RAM patch
  re-points the logo records at the scorpion for Nod and at TS GDI's eagle for TS GDI (`radar-crest-ram-spike.md`).
  TD's tab icons need the prefix patch in `launcher-vs-dll-ownership.md`.
- RA's scene shows no country name under the crest: `Text_FactionSelected` is hidden (tint alpha 0) by
  `scripts/bui_work/hud_label_hide_build.py`, run from `build_config_meg.sh`.

## Open

- The redundant countries can't be hidden (the manual's Traps), so the picker is eight rows reading as five
  factions.
- `NAME_FACTION_5` and `REDALERT_RUSSIA` still read "USSR" (4-character slots); the lobby overlay `BONUS_RUSSIA`
  shows "Soviet". `loc_relabel.py` can grow both slots byte-neutrally if it matters.

## Adding records to the `.LOC` crashes ClientG at boot

See the manual's
[Relabel strings](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/launcher-data/new-text-strings.md#relabel-strings-the-loc-table-at-its-exact-size)
and [Crash triage](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/troubleshooting/crash-triage.md#4-a-clientg-crash-at-rva-0x56a539-is-an-assert),
section 4. TF's test added 6 records (6,852→6,858, +755 B) and crashed ClientG at `0x0056A539` (`_Except_404.txt`);
3,973 of 3,974 members were byte-identical, with no region overlap and no companion index file, so it was not a
repacker bug. Inside the `.LOC`, a unique name can only take over a dead key whose value is already long enough. New
strings go in `Data/ModText.csv` (next section).

## Custom names: `Data/ModText.csv`

See the manual's
[Add strings](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/launcher-data/new-text-strings.md#add-strings-datamodtextcsv),
and [New units without a DLL of your own](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/structuring/units-without-a-dll.md)
(DontCryJustDie's Nuke Tank sample, every file).

The mod ships `resources/remaster_mods/Vanilla_RA/Data/ModText.csv` for its own unit and building
names, with loose `BuildIcon_*.tga` cameos.

**How a sidebar label resolves:** see the manual's
[Traps](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/launcher-data/new-text-strings.md#traps).
- Deleting the `ObjectTypeClass` entry empties the cameo slot: the entry carries the `BuildIcon`
  and is mandatory.
- A mod-owned object class name does not hand naming to the DLL.
- A pipeline-built entity's name works because the bundler's `--text-name` / `--text-desc` write its
  `ModText.csv` row; a hand-edited `RABUILDABLES` entry with no row shows whatever its ID resolves to
  in the base text (both MCV IDs resolve to "MCV").
- Give an entity a faction name only together with the `Owner=` narrowing that makes it true.
- The sidebar and the popup can differ: `[TDARTY]`'s sidebar shows the master text's
  `TEXT_UNIT_TITLE_NOD_ARTILLERY` ("Artillery"), its popup `Name=` "Nod Artillery".

## Deploy hazard

The gitignored UI atlas holds the picker crests. `deploy.sh` refuses a missing or stale atlas (`check_locked`,
against `scripts/campaigns_work/textures.md5`); a hand-run rsync from a worktree without main's copy still wipes the
front-end emblems (`ui-atlas-modding.md`, "What the shipped atlas holds").
