# Building-separation scope — porting TD building classes into the RA DLL

**Status:** **IN PROGRESS 2026-05-21** — TDOBLI (Nod Obelisk of Light) shipped as the first fully-separated building, validating the recipe end-to-end (audio routing, charge state machine, laser-beam render, classic-mode SHP via TFASSETS.MIX). Canonical recipe: `docs/td-building-separation-recipe.md`. Remaining 16 buildings + units use the same recipe; cycle time per building is now bounded engineering (1-6 hours per tier).

**Goal:** every TD-themed building (currently 17 entries: TDPYLE, TDNUKE, TDNUK2, TDPROC, TDSILO, TDFIX, TDWEAP, TDHPAD, TDGTWR, TDATWR, TDHQ, TDEYE, TDAFLD, TDHAND, TDGUN, TDSAM, TDOBLI, TDTMPL — note TDAFLD currently rides STRUCT_WEAP) becomes its own `STRUCT_TDxxxx` enum entry with its own `BuildingTypeClass` instance, `_anims[]` array, `_presets[]` footprint, and `Unlimbo()` dispatch. RA's STRUCT_* dispatch and behavior code is never reached for TD entities.

**Non-goal:** removing the Logic= alias mechanism itself. It stays as the mod's `[NewBuildings]` machinery for any future entries we *don't* want to fully separate (data-only mods, balance variants).

---

## 1. What we keep using from RA's engine

Stays untouched, called by both vanilla RA and our new TD types via inheritance:

- `TechnoClass`, `TechnoTypeClass` — the polymorphic base. Our TD types inherit `BuildingClass : TechnoClass` exactly as RA does.
- `HouseClass`, `ObjectClass`, `MissionClass`, `RadioClass`, `AnimClass` — all reused as-is.
- `CCINIClass` rules.ini reader, `MFCD` mix-file loader, `RawFileClass` asset paths.
- Sidebar / build-queue / cameo system — already heap-aware (per v0.3.0-phase3d). `[NewBuildings]` registration mechanism continues to enrol our types.
- Sort_Y / Center_Coord fixes for mod entries (`building.cpp:3505` ShapeSize-aware path) — still useful as a generic mod-entry fallback for any future Logic= aliased entry.
- D1.2 Phase 1 literal-prereqs work (Prerequisite[] arrays + ActiveBQuantity tracking) — already heap-aware, no change.

## 2. What gets ported from `tiberiandawn/` into `redalert/`

Per-building behavior that RA can't express cleanly. Source paths are TD source files in this repo; destinations are new files in `redalert/` to keep the namespace clean.

| TD source | RA destination | Scope |
|---|---|---|
| `tiberiandawn/bdata.cpp` | `redalert/td_bdata.cpp` (new ~1200 lines) | 17 `BuildingTypeClass` instances ported, 17 `_anims[]` arrays, ~10 `_presets[]` footprints. Owner masks adapt to RA's HOUSEF_* (GoodGuy/BadGuy already wired). |
| `tiberiandawn/building.cpp` selected functions | `redalert/td_building.cpp` (new ~600 lines) | `Exit_Object` per-type (TDWEAP/TDAFLD vehicle delivery), `Mission_Unload` state machines, `Receive_Message` dispatch (radio link to harvesters etc.), `Sort_Y` returns Center_Coord (we already do this). Most BuildingClass behavior remains in RA's `building.cpp` — only the per-type branches move. |
| `tiberiandawn/bbdata.cpp` (Bullet classes already RA-side per Phase W1) | — | Already handled by weapons-port work. |
| `tiberiandawn/anim.cpp` | merged into RA's `redalert/anim.cpp` | Any TD-only ANIM_* entries needed (muzzle flashes, hit anims, charge anims). Same enum-add + register pattern as weapons. |

**TD-only mechanics that come for free with the port:**

- TDPROC dock animation with harvester radio link (TD's `Receive_Message` + `BSTATE_AUX1` cycle) — supersedes [[project-td-harvester-dock-plan]] complexity.
- TDWEAP vehicle exit via Track-based door-open + Force_Track (no need for RA's Track14/SW-exit fork from gotchas #11-15; we use TD's original Track logic directly).
- TDAFLD cargo-plane delivery (already working in RA via gotchas, but cleaner via TD's `Exit_Object` state machine).
- TDOBLI laser charge-up animation (BSTATE_AUX1) — not feasible cleanly in alias model.
- TDHAND red-glow active state.
- AGT rotating radar dish (BSTATE_AUX1 idle cycle independent of damage-anim).
- TDGUN turret rotation (TD has its own multi-facing turret logic; RA's AGUN logic doesn't apply).

## 3. Adapter glue (new code, RA-side)

About 200-400 lines of bridging code that hooks the ported TD types into RA's runtime:

- **STRUCT_TD* enum extension** (`redalert/defines.h`) — 17 new enum values appended after STRUCT_COUNT-1. STRUCT_COUNT bumps; MAX_BUILDING_TYPES already `STRUCT_COUNT + 50` so no #define changes needed.
- **`BuildingTypeClass::Init_Heap` extension** — add 17 `new BuildingTypeClass(...)` calls in `redalert/bdata.cpp`'s init function, lifting TD's constructor args. Reuses RA's existing heap.
- **Unlimbo / dispatch routing** (`redalert/building.cpp`) — the existing 4-side dispatch (HOUSE_GOOD/HOUSE_BAD aware) gets new cases for STRUCT_TD* that route to `td_building.cpp`. Default falls through to RA's existing logic for vanilla STRUCT_*.
- **Bib/footprint table extension** (`redalert/bdata.cpp` `_presets[]`) — port TD's `List22_*` / `List21_*` / `List13_*` patterns. Each TD footprint becomes a new preset entry.
- **HouseClass build-order arrays** (`redalert/house.cpp`) — RA's AI base-build sequences are STRUCT_*-indexed. Add parallel arrays for HOUSE_GOOD / HOUSE_BAD that reference STRUCT_TD*. This is the bulk of the AI-tuning win. See §3.1 for the full house-work breakdown.
- **Cameo / sidebar wiring** (already heap-aware via `[NewBuildings]`) — no change beyond appending new entries to RABUILDABLES.XML, same as current pipeline.

### 3.1 House-side work breakdown

The good news: foundation is already in place from earlier sessions. The work is targeted, not a rewrite.

**Already done (no separation-driven work needed):**

| Component | Status |
|---|---|
| `HOUSE_GOOD` / `HOUSE_BAD` enum entries | Done (v0.2.0) |
| Spain→HOUSE_GOOD / Turkey→HOUSE_BAD launcher swap | Done (`dllinterface.cpp:905-910`) |
| `HouseClass::BQuantity[MAX_BUILDING_TYPES]` heap-sized array | Done (D1.2 Phase 1) |
| `HouseClass::ActiveBQuantity[MAX_BUILDING_TYPES]` heap-sized array | Done (D1.2 Phase 1) |
| `Prerequisite[]` heap-aware Type indices | Done (D1.2 Phase 1) |
| 4-side dispatch in `BuildingClass::Unlimbo` | Done (v0.2.0) |
| Vanilla campaign houses (`HOUSE_GREECE` / `HOUSE_USSR`) unchanged | Untouched |

**Will need work, folded into existing milestone estimates:**

| # | Work item | Lands in | Estimate |
|---|---|---|---|
| H1 | `HouseTypeClass` Allowed/Disallowed lists populated for GoodGuy/BadGuy with STRUCT_TD* entries. Small bookkeeping. | M1 | ~0.5 day |
| H2 | AI base-build order arrays — parallel sequences for HOUSE_GOOD (Pylon→Refinery→Helipad→Weapons→HQ) and HOUSE_BAD (Hand→Refinery→Airstrip→SAM→Temple), referencing STRUCT_TD*. Walking these requires extending `HouseClass::AI_Building` dispatch. | M3-M4 | ~1-2 days |
| H3 | STRUCTF_* bitmask checks → capability lookups. `house.cpp` has dozens of `if (BScan & STRUCTF_POWER)` / `Has_Building_Active(STRUCT_BARRACKS)` calls for "have radar / can queue aircraft / how much power / power surplus". Two paths: (a) per-call equivalences `STRUCT_POWER \|\| STRUCT_TDNUKE`; (b) generalised "provides X capability" lookup over ActiveBQuantity. The refactor (b) is the right long-term call and is already half-needed by D1.2 Phase 2 (delete BScan). Recommend (b). | M2-M3 | ~2-3 days |
| H4 | Side-aware `Can_Build` gates for cross-faction prerequisites (e.g. can a captured TDHQ let GoodGuy build vanilla Allied tech, and vice versa). Decision-required: do we allow tech-mixing or hard-walls per side? | M3 | ~0.5 day decision + ~1 day implementation |

**Total house-side work: ~4-6 days across M1-M3** — folded into existing milestone estimates, not additive to the 3-5 week total.

**What we don't touch:**

- HOUSE_GREECE (Allied campaign) and HOUSE_USSR (Soviet campaign) — vanilla campaign play is preserved end-to-end. Campaign scenarios (`scg*.ini` / `scu*.ini`) still resolve to vanilla houses with vanilla STRUCT_* entries. The mod's TD content is gated behind GoodGuy/BadGuy and never touches campaign code paths.
- HOUSE_UKRAINE, HOUSE_ENGLAND, HOUSE_GERMANY, HOUSE_FRANCE — vanilla country variants stay untouched. France's Phase Tank, Germany's Demolitionist, Ukraine's Parabombs etc. remain available to skirmish players choosing those countries. (Country stat modifiers themselves are slated for eventual removal per `project-country-modifiers-removal`, but that's orthogonal to the separation work.)
- HOUSE_SPAIN, HOUSE_TURKEY — the two hijacked countries swap to HOUSE_GOOD / HOUSE_BAD before any code path sees the original house, so no logic touches them. Cosmetic relabel to "GDI" / "Nod" already handled in string-table overrides.

## 4. Classic-mode SHP lookup payoff

Currently in classic graphics mode, mod entries fall back to the donor's SHP from REDALERT.MIX — so a Logic=POWR aliased TDNUKE shows RA's PWRR.SHP underneath. Post-separation:

- TDNUKE's ImageData lookup uses `"TDNUKE"` directly as the SHP filename.
- We bundle TD's NUKE.SHP from CONQUER.MIX into a mod mixfile under the name `TDNUKE.SHP`.
- Engine loads our SHP via standard MFCD::Retrieve path.

Still requires the mod-mixfile bundling step (~1 day), but the lookup itself is free — no engine patches to coerce IniName→SHP routing past the alias.

## 5. Per-building work breakdown (the 17 entries)

Group by porting complexity (= how much of TD's `bdata.cpp` constructor + ancillary state we lift):

**Tier 1 — pure data (4 entries, ~half a day each):** TDNUKE, TDNUK2, TDSILO, TDPYLE. Static buildings with idle anim + buildup, no per-type mission logic. Constructor port + footprint entry, done.

**Tier 2 — defensive turrets (4 entries, ~1 day each):** TDGTWR, TDATWR, TDGUN, TDSAM. Add turret-facing logic from `tiberiandawn/building.cpp` `Draw_It` turret path. TDGUN rotation bug resolves here.

**Tier 3 — production/economy buildings (5 entries, ~1.5 days each):** TDPROC (dock anim + harvester radio handshake), TDWEAP (Exit_Object + Track-based vehicle exit), TDHPAD (Helipad docking), TDFIX (repair-bay mission state), TDAFLD (cargo-plane delivery, mostly already working — just moves to clean home).

**Tier 4 — superweapon hosts (3 entries, ~2 days each):** TDHQ (radar), TDEYE (Ion Cannon binding + sprite-render fix), TDTMPL (Nuke binding + buildup-anim fix). TDEYE missing-sprite and TDTMPL buildup-snap bugs resolve here.

**Tier 5 — unique mechanics (1 entry, ~3 days):** TDOBLI — laser charge-up animation + **the laser-line render port itself lives here**. Phase W1 only ships the data piece for OBELISK_LASER (enum, BulletType, WarheadType, sounds); the render code (`Lines[3][5]` globals, per-frame draw loop, `Fire_At` BULLET_LASER branch, scorch smudge stamp from `tiberiandawn/techno.cpp:2481-2514`) lives on the `BuildingClass` override for STRUCT_TDOBLI rather than getting wedged into RA's shared `techno.cpp`. Cleaner architectural fit and avoids touching code paths that aren't TD-specific. TDHAND can move to Tier 1 if we skip the red-glow active state for v1, otherwise it's a small ~1-day add.

**Total point estimate:** 22-30 focused engineer-days = **3-5 weeks** depending on how many side-quests (asset bundling, AI tuning, regression playtests) we absorb into the same window.

This is bigger than my "1-2 weeks" earlier estimate. Being honest: a clean port of TD source isn't free even when you have the source — the adapter glue (HouseClass build orders, sidebar wiring, save-format compat, classic-mode mix bundling) adds substantial overhead per tier.

## 6. Milestone breakdown — incremental, never breaks v0.4

Land in vertical slices so the mod stays playable throughout. Each milestone ends in a tagged release.

- **M1 — Skeleton (~3 days).** Add STRUCT_TD* enum entries + 17 empty `BuildingTypeClass` instances + Init_Heap registration. Sidebar/cameos still wired via existing `[NewBuildings]`. At end of M1, TD entries exist twice (as Logic=alias AND as own type), gated by a `--tdtypes` runtime flag. Vanilla play unchanged.
- **M2 — Tier 1 buildings (~2 days).** TDNUKE/TDNUK2/TDSILO/TDPYLE switch to own types. Manifest emits `Logic=` for OFF and STRUCT_TD* mapping when flag ON. Playtest both paths.
- **M3 — Tier 2 defensive turrets (~4 days).** TDGUN rotation fix lands here. TDGTWR/TDATWR weapons (Phase W1 OBELISK_LASER + TOW_TWO already done by this point) plug in via their own type.
- **M4 — Tier 3 economy (~7-8 days).** TDPROC harvester dock anim lands — the harvester unit port from the unit catalogue plugs in here. TDWEAP exit logic moves to TD's native pattern; we revert RA's Track14 hack from gotcha #14.
- **M5 — Tier 4 superweapons + Tier 5 Obelisk (~5-7 days).** TDEYE sprite, TDTMPL buildup, TDOBLI laser charge. Classic-mode mix bundling lands as part of M5 (now that all 17 entries are own-types, the SHP lookup is uniform).
- **M6 — Cleanup (~2 days).** Remove the `--tdtypes` flag and the Logic= alias entries for TD buildings. Logic= alias mechanism stays for future use, but the 17 TD entries become STRUCT_TD*-only.

## 7. Risks / known unknowns

- **Save-format compatibility.** Adding STRUCT_TD* values changes `sizeof(BuildingTypeClass)` array indices in save files. Mid-campaign saves from v0.4 will not load post-M2. We're not shipping campaign mode yet so blast radius is skirmish-only.
- **Mission scenarios** (.ini files for campaign maps) — none yet. Future campaign work would need to use STRUCT_TD* names. Defer.
- **AI tuning regression.** Once GDI/Nod get their own base-build orders, current playtest balance changes. Plan extra playtest days at M3 and M5.
- **TD source GPL v3.** TD's source is GPL v3 (same as RA's per `LICENSE.TXT`), and we already inherit GPL v3 from Vanilla Conquer. Lifting TD code is license-clean. Attribution in comments is courtesy, not legal requirement.
- **Vanilla Conquer upstream contributions.** Some of this is generic enough to push upstream (heap-aware everything, separate-namespace buildings). Worth flagging to VC contributors after M3 lands — but downstream-first, upstream-later.

## 8. Decision points before starting

- **Confirm scope:** all 17 entries, or partial (e.g. only Tier 1-3 for v1, defer superweapons)?
- **Confirm timing:** start after Phase W1 weapons port completes, or interleave?
- **Confirm flag-gating in M1:** do we want a `--tdtypes` runtime flag, or just feature-branch the whole work and merge atomically at M6? Flag-gated lets us bisect regressions per tier; atomic merge is simpler but riskier.

## 9. Related memory and docs

- [[project-mod-type-heap-sizing]] — already-validated pattern; M1 piggybacks on this.
- [[project-td-harvester-dock-plan]] — superseded by M4's TDPROC port (becomes trivial).
- `docs/catalogue.md` "Building bugs found during 2026-05-20 playtest" — items #1 (TDPROC dock), #4 (TDEYE missing sprite + footprint), #6 (TDTMPL slow buildup) all become non-issues post-separation. Item #5 (TDGTWR/TDATWR weapons) resolved by Phase W1 independently.
- `docs/weapon-ports.md` — Phase W1 lands before M3.
- `docs/cargo-plane-port.md` — M4's TDAFLD port subsumes this; document gets archived once M4 lands.
- `docs/adding-td-buildings.md` — gotchas #11-15 (TDWEAP Track work) become obsolete post-M4 and should be marked archived.
