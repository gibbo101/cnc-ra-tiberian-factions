# Faction-select identity in the RA lobby — the CONFIG.MEG recipe (PROVEN 2026-05-29)

How to give the RA skirmish **faction picker** custom **icons**, **names**, and **bonus-overlay text** for GDI / Nod / Allies / Soviet — shipped via a mod `Data/CONFIG.MEG`, **no EMC, no texture MEG**. Companion to `config-meg-mod-delivery.md` (the delivery mechanism) and `ui-atlas-modding.md` (why loose textures don't reach the front-end).

**Proven on the Deck:** Spain→GDI emblem + "GDI"; Turkey→Nod emblem + "Nod"; Greece→flag + "Allies"; USSR→flag + "Soviet". No bonus lines. No crash.

---

## The three levers

### 1. Picker ICON — `FACTIONS.XML` → `SmallIconName`
Each faction's emblem is `EncyclopediaComponent/DefaultIcons/SmallIconName` = `UI_Multiplayer_PlayerSlot_Faction_NN.tga`. **Repoint** it to a *different* region.

⚠️ **You may only point at a region the front-end PRELOADS.** That set is exactly the player-slot icons:
- `_00` = GDI eagle, `_01` = Nod cobra, `_03`–`_10` = the 8 RA country flags. (`_02` doesn't exist.)
- Pointing at **anything else** (`UI_SIDEBAR_FACTIONLOGO_*`, `RA_UI_MULTIPLAYER_*_LOGO`) → **hard crash at launcher startup.** Confirmed repeatedly.

So with pure CONFIG.MEG you can only **re-use the existing emblems/flags**: Spain→`_00` and Turkey→`_01` give real GDI/Nod emblems; Allies/Soviet have no stock emblem so they keep their country flag. Custom pixels (Allied/Soviet emblems, bespoke GDI/Nod art) require the texture-MEG route — see `front-end-texture-meg-spike.md`.

**Faction# → country → icon:** F1=GDI(`_00`), F2=Nod(`_01`), F3=Spain(`_03`), F4=Greece(`_04`), F5=USSR(`_05`), F6=UK(`_06`), F7=Ukraine(`_07`), F8=Germany(`_08`), F9=France(`_09`), F10=Turkey(`_10`).

### 2. Picker NAME + bonus-OVERLAY — `MASTERTEXTFILE_<lang>.LOC`
The **visible overlay** when you hover/select a faction is the bonus string **`TEXT_FACTION_BONUS_<COUNTRY>`** (e.g. `..._SPAIN` = "Spain: 10% more armor, damage, and speed for infantry"). Collapse it to just the faction name to get "no bonus, just GDI".
The faction display name is **`TEXT_FACTION_NAME_FACTION_NN`**, and the **in-game (in-match) sidebar** name is a *third* string — **`TEXT_FACTION_REDALERT_<COUNTRY>`**. Relabel all three to cover lobby-name + lobby-overlay + in-match sidebar. (PROVEN: the in-game sidebar read "Spain" until `REDALERT_SPAIN` was edited → "GDI"; the lobby uses `BONUS_`/`NAME_`, the in-match sidebar uses `REDALERT_`.)

Country→keys: SPAIN/GREECE/RUSSIA(=USSR)/TURKEY/ENGLAND/GERMANY/FRANCE/UKRAINE for `_BONUS_`; `_NAME_FACTION_3/4/5/6/7/8/9/10` for the names.

⚠️ **The FILE's size is fixed; an individual string's is not (corrected 2026-07-21).** Keep the total byte length unchanged — resizing the `.LOC` crashes the launcher at boot. But a value may **outgrow its slot** provided the length table is rewritten and the bytes are taken back from another string in the same file: the format locates each value by summing the lengths ahead of it, so a byte-neutral redistribution stays consistent. **Proven in-game 2026-07-21** (a 14-char slot grew to hold "Unholy Alliance", one character reclaimed from a neighbouring tooltip). `scripts/loc_relabel.py` does this: values that still fit keep their slot, one that outgrows it is stored at its true length, and a nominated slack string absorbs the difference. The older tooling (`loc_edit.py`) only does the in-place path. (Trailing spaces render invisibly.) The bonus strings are long (16–53 chars) so any faction name fits; the `NAME_FACTION_5`="USSR" slot is only 4 chars so "Soviet" won't fit *there* — but the overlay you actually see is `BONUS_RUSSIA` (43 chars), which fits "Soviet" fine.

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
- **Same-length edit = overwrite value bytes in place** (keeps every offset valid). Helper: `/tmp/edit_loc_samelen.py` this session.

## Crash log — what NOT to do
| Action | Result |
|---|---|
| `SmallIconName` → a non-preloaded region (FACTIONLOGO / MP-LOGO) | startup crash |
| `.LOC` rebuild that CHANGES THE FILE SIZE | startup crash |
| `.LOC` **same-length** in-place edit | ✅ safe |
| `.LOC` table rewrite, file size unchanged (a string grows, another gives bytes back) | ✅ safe, proven 2026-07-21 |
| `FACTIONS.XML` `CampaignType` change | startup crash (genuine-faction route) |
| loose `Data/ART/TEXTURES` override for the front-end | ignored (in-game only) |

## Status / open items

> **SHIPPED (39e069b).** GDI/Nod emblems + names ship via the mod `Data/CONFIG.MEG`. The wiring
> item below is DONE — the CONFIG.MEG is in the build, not `/tmp`. The only genuinely-open item is
> the texture-only surfaces (Allies/Soviet emblems, marker/loading flags) which need the negative-
> resolved front-end texture MEG route — see `front-end-texture-meg-spike.md`. ⚠ The 184MB crest
> atlas is gitignored; regen `scripts/frontend_atlas_build.py` before deploy (see [[project-faction-select-shipped]]).

- **All 8 relabeled (DONE 2026-05-29):** Spain→GDI, Turkey→Nod, Greece/England/Germany/France→Allies, USSR/Ukraine→Soviet — across `NAME_FACTION_NN` + `BONUS_<C>` + `REDALERT_<C>` (22 same-length edits in one pass). The redundant 4 can't be *hidden* (no data flag; `CampaignType` crashes), so the picker is 8 entries reading as the 4 factions (dupes accepted). **USSR caveat:** `NAME_FACTION_5` and `REDALERT_RUSSIA` are only 4-char slots, so "Soviet" (6) won't fit same-length — they stay "USSR" (the lobby overlay `BONUS_RUSSIA`, 43 chars, *does* show "Soviet"). "Soviet" everywhere was deferred as needing a size-changing rebuild; that reasoning is now wrong — `loc_relabel.py` can grow those two slots byte-neutrally (2026-07-21). Cheap to finish if it ever matters.
- **All remaining icon/flag surfaces are texture-only (CONFIG.MEG can't reach them — confirmed: FACTIONS.XML has only `SmallIconName`, no map/loading field):** Allies/Soviet picker emblems (vs flags), the **map position-select** marker flag, the **loading-screen** flag, and bespoke GDI/Nod art. The launcher picks all of these from the atlas **by the player's country**, so they show e.g. the Spain flag for GDI. One fix for all → `front-end-texture-meg-spike.md`.
- **Wiring (DONE):** the CONFIG.MEG is built into the mod and ships in releases (was a `/tmp` build during the spike).

---

## ⛔ ADDING new master-text strings is IMPOSSIBLE — confirmed via crash dump (2026-06-21)

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
Tool kept for the legit same-length path: `scripts/loc_edit.py`.

---

## ✅ CORRECTION 2026-06-22 — custom NAMES *are* possible via Data/ModText.csv (NOT .LOC)

The "adding master-text strings is impossible" conclusion above was chasing the WRONG mechanism
(editing MASTERTEXTFILE_*.LOC, which the launcher size-pins). The **official, supported way** to add
custom text is a loose **`Data/ModText.csv`** — proven by DontCryJustDie's official "Nuke Tank Sample
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

**For OUR mod:** ship a `Data/ModText.csv` to give the gunboat/hovercraft/separated buildings REAL
sidebar names (GDI Naval Yard, Nod Sub Pen, GDI Airfield, etc.) + LOOSE `BuildIcon_*.tga` cameos
rendered from 3D models. Retires the "borrow a resolving string" workaround entirely. ModText.csv is
LAUNCHER-side, so it works regardless of our DLL fork. ⭐ Do this for the naval units next session.

---

## Deploy hazard (migrated from memory 2026-07-15)
The ~184MB front-end crest atlas `Data/ART/TEXTURES/SRGB/MT_COMMANDBAR_COMMON.TGA` is gitignored and
generated by `scripts/frontend_atlas_build.py`. Regenerate it before any `rsync -a --delete` deploy —
otherwise `--delete` wipes it from the target prefix/Deck and the front-end emblems vanish.
