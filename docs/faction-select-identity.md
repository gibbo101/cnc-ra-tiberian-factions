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

---

## The three levers

### 1. Picker ICON — `FACTIONS.XML` → `SmallIconName`
Each faction's emblem is `EncyclopediaComponent/DefaultIcons/SmallIconName` = `UI_Multiplayer_PlayerSlot_Faction_NN.tga`. **Repoint** it to a *different* region.

⚠️ **You may only point at a region the front-end PRELOADS.** That set is exactly the player-slot icons:
- `_00` = GDI eagle, `_01` = Nod cobra, `_03`–`_10` = the 8 RA country flags. (`_02` doesn't exist.)
- Pointing at **anything else** (`UI_SIDEBAR_FACTIONLOGO_*`, `RA_UI_MULTIPLAYER_*_LOGO`) → **hard crash at launcher startup.** Confirmed repeatedly.

So CONFIG.MEG alone can only **re-use the existing emblems and flags**. Custom pixels come from repainting those preloaded regions in the loose atlas (`ui-atlas-modding.md`), which is how every picker row gets its crest.

**Faction# → country → icon:** F1=GDI(`_00`), F2=Nod(`_01`), F3=Spain(`_03`), F4=Greece(`_04`), F5=USSR(`_05`), F6=UK(`_06`), F7=Ukraine(`_07`), F8=Germany(`_08`), F9=France(`_09`), F10=Turkey(`_10`).

### 2. Picker NAME + bonus-OVERLAY — `MASTERTEXTFILE_<lang>.LOC`
The **visible overlay** when you hover/select a faction is the bonus string **`TEXT_FACTION_BONUS_<COUNTRY>`** (e.g. `..._SPAIN` = "Spain: 10% more armor, damage, and speed for infantry"). Collapse it to just the faction name to get "no bonus, just GDI".
The faction display name is **`TEXT_FACTION_NAME_FACTION_NN`**, and the **in-game (in-match) sidebar** name is a *third* string — **`TEXT_FACTION_REDALERT_<COUNTRY>`**. Relabel all three to cover lobby-name + lobby-overlay + in-match sidebar. (PROVEN: the in-game sidebar read "Spain" until `REDALERT_SPAIN` was edited → "GDI"; the lobby uses `BONUS_`/`NAME_`, the in-match sidebar uses `REDALERT_`.)

Country→keys: SPAIN/GREECE/RUSSIA(=USSR)/TURKEY/ENGLAND/GERMANY/FRANCE/UKRAINE for `_BONUS_`; `_NAME_FACTION_3/4/5/6/7/8/9/10` for the names.

⚠️ **The FILE's size is fixed; an individual string's is not.** Keep the total byte length unchanged — resizing the `.LOC` crashes the launcher at boot. But a value may **outgrow its slot** provided the length table is rewritten and the bytes are taken back from another string in the same file: the format locates each value by summing the lengths ahead of it, so a byte-neutral redistribution stays consistent. **Proven in-game 2026-07-21** (a 14-char slot grew to hold "Unholy Alliance", one character reclaimed from a neighbouring tooltip). `scripts/loc_relabel.py` does this: values that still fit keep their slot, one that outgrows it is stored at its true length, and a nominated slack string absorbs the difference. The older tooling (`loc_edit.py`) only does the in-place path. (Trailing spaces render invisibly.) The bonus strings are long (16–53 chars) so any faction name fits; the `NAME_FACTION_5`="USSR" slot is only 4 chars so "Soviet" won't fit *there* — but the overlay you actually see is `BONUS_RUSSIA` (43 chars), which fits "Soviet" fine.

### 3. Delivery — mod `Data/CONFIG.MEG`
Repack the base CONFIG.MEG with the two edited files and ship it as the mod's `Data/CONFIG.MEG`; the launcher loads it over base (front-end reads it — proven). No EMC.
```
python3 scripts/meg_pack.py repack <base CONFIG.MEG> <out> \
    "MISC/FACTIONS.XML=<edited factions.xml>" \
    "MASTERTEXTFILE_EN-US.LOC=<edited .loc>"
```
Per-language: there's a `MASTERTEXTFILE_<lang>.LOC` per language (EN-US, FR-FR, DE-DE…). Edit the ones you ship for (EN-US covers English installs).

---

## `MASTERTEXTFILE_<lang>.LOC` format (so we never re-RE it)
```
[u32 count]
[count × 12-byte records]   record = [keyHash:u32][valLen:u32 (chars)][keyLen:u32 (bytes)]
[value-blob]                UTF-16LE values, concatenated in record order, addressed by cumulative valLen
[key-blob]                  ASCII keys,  concatenated in record order, addressed by cumulative keyLen
```
- No absolute offsets anywhere — everything is length-addressed (cumulative). Records are sorted ascending by `keyHash`.
- Value-blob starts at `4 + 12*count`; key-blob right after the values; file ends exactly at end of key-blob.
- **Same-length edit = overwrite value bytes in place** (keeps every offset valid): `scripts/loc_edit.py`. A byte-neutral regrow: `scripts/loc_relabel.py`.

## Crash log — what NOT to do
| Action | Result |
|---|---|
| `SmallIconName` → a non-preloaded region (FACTIONLOGO / MP-LOGO) | startup crash |
| `.LOC` rebuild that CHANGES THE FILE SIZE | startup crash |
| `.LOC` **same-length** in-place edit | ✅ safe |
| `.LOC` table rewrite, file size unchanged (a string grows, another gives bytes back) | ✅ safe, proven 2026-07-21 |
| `FACTIONS.XML` `CampaignType` change | startup crash (genuine-faction route) |
| loose `Data/ART/TEXTURES` override for the front-end | ✅ renders (atlas and standalone DDS, `ui-atlas-modding.md`) |

## Picker layout: one crest per row, launcher order

The picker lists countries in the launcher's enum order and that order is not data: reordering
the `FACTIONS.XML` entries changes nothing, and a hidden entry leaves a blank row that still
selects the hidden country. So the rows are assigned by position instead (DLL remap in
`CNC_Set_Multiplayer_Data`, names in `scripts/loc_work/mastertext.edits.txt`, plates painted by
`scripts/picker_emblems_paint.py`):

| row | country | plays as | plate |
|---|---|---|---|
| 1 | Spain | GDI (`HOUSE_GOOD`) | `_03` GDI radar crest |
| 2 | Greece | Nod (`HOUSE_BAD`) | `_04` Nod radar crest |
| 3 | USSR | Soviet | `_05` Soviet crest |
| 4 | England | Allies | `_06` Allied crest |
| 5 | Ukraine | Soviet duplicate | `_07` Soviet crest |
| 6 | Germany | TS GDI (`HOUSEF_TSGDI`) | `_08` TS GDI crest |
| 7-8 | France / Turkey | Allied duplicates | `_09` / `_10` Allied crest |

All three hijacked countries are Allied-side to the launcher. GDI and Nod moved off the 66x56 `_00`/`_01` icons onto the full-size `_03`/`_10`-style
plates so every row is the same size (`scripts/factions_build.py` sets the `SmallIconName`s and is
run by `build_config_meg.sh`). Plates are the metallic radar crests alone on a transparent
region, slightly softened because the list draws them at about a third of their size with no
mip filtering. The slot box fits the plate by width (a 40x40 region pointed there draws as a
150x80 oval), so the crest is scaled to the plate's full height and that is the box's limit.

**Map markers and loading screen:** the start-position badges on the lobby map and the
player badges on the loading screen both draw `UI_MAPSELECT_FACTION_NN` (40x40, `_01` GDI, `_02`
Nod, `_03` Spain .. `_10` Turkey, one above the plate numbering). The base flag sits in a 22px
disc with the launcher's player-colour ring behind it, so the crests are painted at 22px inside
those regions (`picker_emblems_paint.py` too). The plate is not involved: pointing it elsewhere
in memory changed the lobby row and nothing on the loading screen.

## TD HUD scene per faction: the sidebar is data

Every `FACTIONS.XML` entry carries two tactical scene lists: `TopLevelGUIList` naming TD's
`Art/GUI/Tactical_UI.bui` and `TopLevelGUIListAlt` naming `Art/GUI/RA_Tactical_UI.bui`. The RA
launcher reads the alternate list, so **swapping the two scene names inside the GDI, Nod and TS GDI
entries** (`factions_build.py`, `TD_HUD`; same bytes, exchanged) makes those factions load TD's
whole HUD scene: the wide sell/repair/map bar, TD's pip power meter, TD tab icons, green credits,
no side label. Allies and Soviets keep RA's scene.

Two consequences:
- TD's scene picks its faction logo by RA side (Allied → eagle, Soviet → scorpion), and Nod and
  TS GDI sit on the Allied side, so the crest RAM patch re-points the logo records at the scorpion
  for Nod and at TS GDI's eagle for TS GDI (`radar-crest-ram-spike.md`). TD's tab icons need the
  prefix patch in `launcher-vs-dll-ownership.md`.
- RA's scene now shows no country name under the crest: `Text_FactionSelected` is hidden (tint
  alpha 0) by `scripts/bui_work/hud_label_hide_build.py`, run from `build_config_meg.sh`.

## Open

- The redundant countries can't be *hidden* (no data flag; `CampaignType` crashes; a commented-out
  entry leaves a blank row that still selects its country), so the picker is eight rows reading as
  five factions.
- `NAME_FACTION_5` and `REDALERT_RUSSIA` still read "USSR" (4-char slots); the lobby overlay
  `BONUS_RUSSIA` shows "Soviet". `loc_relabel.py` can grow both slots byte-neutrally if it matters.

---

## ⛔ Adding records to the `.LOC` crashes ClientG at boot

The `.LOC` format is now fully reverse-engineered (`scripts/loc_edit.py`):
`u32 count` → `count × [crc32(key):u32 sorted][valLen:u32 chars][keyLen:u32 bytes]`
→ all values (UTF-16LE, record order) → all keys (ASCII, record order). No offsets/terminators;
hash = `zlib.crc32(key)`. Serializer round-trips the base file **byte-identical**.

**Spike result: adding records (resizing the .LOC) HARD-CRASHES the launcher at boot.** Added 6
strings (count 6852→6858, +755 bytes), repacked, deployed → `ClientG.exe` `EXCEPTION_ACCESS_VIOLATION`
@ `0x0056A539` (`AppData/Roaming/CnCRemastered/_Except_404.txt` + `.dmp`). **Ruled out a repacker bug:**
diffed the resized MEG vs base — 3973/3974 files byte-identical, only the `.LOC` changed, no region
overlap, no companion index file exists. So the launcher itself pins the `.LOC` byte-size/layout.

**Therefore: master-text edits are SAME-LENGTH IN-PLACE VALUE OVERWRITES ONLY** (size + record count
must stay byte-identical). To give a custom building/unit a UNIQUE sidebar name you must hijack an
existing **dead** key whose value is already ≥ the target length and overwrite it in place (pad with
trailing spaces, which render invisibly). You cannot add a new key. Fixing this for real would need
Ghidra on `ClientG.exe` (closed launcher, un-shippable) — do NOT re-chase the add-a-string route.
New strings go in `Data/ModText.csv` instead (next section).

---

## Custom names: `Data/ModText.csv`

The **official, supported way** to add custom text is a loose **`Data/ModText.csv`** — proven by DontCryJustDie's official "Nuke Tank Sample
Mod" (Workshop 3497050142, NO DLL). The launcher MERGES this CSV into its string table at load.

Format: UTF-16 CSV, columns = `TEXT ID, AUDIO TAG, CHARACTER, ENGLISH, UNITED_KINGDOM, GERMAN, …`
(per-language). Comment rows put `//` in the TEXT ID field. Data row example:
`TEXT_UNIT_NUKE_TANK,,,Nuke Tank,,,…`  →  resolves the sidebar name.

Full data-only "add a buildable unit + name + cameo" recipe from that sample mod:
1. `Data/XML/Objects/Units/<X>Buildables.xml` — ObjectTypeClass with ObjectNameTextID /
   ObjectDescriptionTextID / `<BuildIcon>`.
2. `Data/ModText.csv` — defines those TEXT IDs (custom names/descriptions, no .LOC).
3. `Data/Art/Textures/SRGB/BuildIcon_<X>.tga` — LOOSE custom cameo, referenced by name.
4. `Rules/rules_mod.ini` `[VehicleTypes] 1=<X>` + `[<X>]` stat block (the stock Remaster DLL parses
   INI-defined vehicles — this sample ships no DLL).
5. `Data/XML/Tilesets/UNITS.XML` + `Data/Art/.../Units/<X>.ZIP` — unit sprite.

The mod ships `resources/remaster_mods/Vanilla_RA/Data/ModText.csv` for its own unit and building
names, with loose `BuildIcon_*.tga` cameos.

**How a sidebar label resolves:** the launcher looks the entry's `ObjectNameTextID` up in the base
`MASTERTEXTFILE` merged with `Data/ModText.csv`.
- rules.ini `Name=` drives only the in-world hover tooltip, never the sidebar.
- An ID found in neither renders raw (`TEXT_UNIT_TDGMCV`).
- Deleting the `ObjectTypeClass` entry empties the cameo slot: the entry carries the `BuildIcon`
  and is mandatory.
- A mod-owned object class name does not hand naming to the DLL.
- A pipeline-built entity's name works because the bundler's `--text-name` / `--text-desc` write its
  `ModText.csv` row; a hand-edited `RABUILDABLES` entry with no row shows whatever its ID resolves to
  in the base text (both MCV IDs resolve to "MCV").
- Give an entity a faction name only together with the `Owner=` narrowing that makes it true.
- The sidebar and the popup can differ: `[TDARTY]`'s sidebar shows the master text's
  `TEXT_UNIT_TITLE_NOD_ARTILLERY` ("Artillery"), its popup `Name=` "Nod Artillery".

---

## Deploy hazard
The ~184 MB UI atlas `Data/ART/TEXTURES/SRGB/MT_COMMANDBAR_COMMON.TGA` holds the picker crests and
is gitignored. Main's copy is canonical (`ui-atlas-modding.md`, "What the shipped atlas holds");
copy it into a worktree before an `rsync -a --delete` deploy, or the deploy wipes the front-end
emblems.
