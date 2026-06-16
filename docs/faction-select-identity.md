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

⚠️ **Edit SAME-LENGTH, IN-PLACE only.** Overwrite the value's bytes, pad shorter names with trailing spaces, keep `valLen` and total file size **unchanged**. A size-changing **rebuild crashes the launcher** even though it's structurally self-consistent — do not resize the `.LOC`. (Trailing spaces render invisibly.) The bonus strings are long (16–53 chars) so any faction name fits; the `NAME_FACTION_5`="USSR" slot is only 4 chars so "Soviet" won't fit *there* — but the overlay you actually see is `BONUS_RUSSIA` (43 chars), which fits "Soviet" fine.

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
| `.LOC` size-changing rebuild | startup crash |
| `.LOC` **same-length** in-place edit | ✅ safe |
| `FACTIONS.XML` `CampaignType` change | startup crash (genuine-faction route) |
| loose `Data/ART/TEXTURES` override for the front-end | ignored (in-game only) |

## Status / open items

> **SHIPPED (39e069b).** GDI/Nod emblems + names ship via the mod `Data/CONFIG.MEG`. The wiring
> item below is DONE — the CONFIG.MEG is in the build, not `/tmp`. The only genuinely-open item is
> the texture-only surfaces (Allies/Soviet emblems, marker/loading flags) which need the negative-
> resolved front-end texture MEG route — see `front-end-texture-meg-spike.md`. ⚠ The 184MB crest
> atlas is gitignored; regen `scripts/frontend_atlas_build.py` before deploy (see [[project-faction-select-shipped]]).

- **All 8 relabeled (DONE 2026-05-29):** Spain→GDI, Turkey→Nod, Greece/England/Germany/France→Allies, USSR/Ukraine→Soviet — across `NAME_FACTION_NN` + `BONUS_<C>` + `REDALERT_<C>` (22 same-length edits in one pass). The redundant 4 can't be *hidden* (no data flag; `CampaignType` crashes), so the picker is 8 entries reading as the 4 factions (dupes accepted). **USSR caveat:** `NAME_FACTION_5` and `REDALERT_RUSSIA` are only 4-char slots, so "Soviet" (6) won't fit same-length — they stay "USSR" (the lobby overlay `BONUS_RUSSIA`, 43 chars, *does* show "Soviet"). "Soviet" everywhere would need the size-changing rebuild (crashes) — deferred as not worth it.
- **All remaining icon/flag surfaces are texture-only (CONFIG.MEG can't reach them — confirmed: FACTIONS.XML has only `SmallIconName`, no map/loading field):** Allies/Soviet picker emblems (vs flags), the **map position-select** marker flag, the **loading-screen** flag, and bespoke GDI/Nod art. The launcher picks all of these from the atlas **by the player's country**, so they show e.g. the Spain flag for GDI. One fix for all → `front-end-texture-meg-spike.md`.
- **Wiring (DONE):** the CONFIG.MEG is built into the mod and ships in releases (was a `/tmp` build during the spike).
