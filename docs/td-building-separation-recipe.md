# TD building separation recipe — STRUCT_TDxxxx per-building port

**Status:** **VALIDATED 2026-05-21** via TDOBLI; **M3 Tier 2 + M4 Tier 3 production buildings shipped 2026-05-27** (TDWEAP, TDAFLD with multi-plane convoy). Use this doc as the canonical reference for every subsequent STRUCT_TDxxxx port.

**TDWEAP/TDAFLD-discovered gotchas added to `docs/td-port-playbook.md` §3.13–§3.19** — read those before starting any production-building port. The recipe steps below assume a turret/static building; production buildings (factories, airstrips) layer on the new traps.

**Recipe scope:** taking a TD-themed mod entry from the v0.3-era Logic=alias model (where it rides on a vanilla RA donor type) to a fully-separated `STRUCT_TDxxxx` heap entry with its own `BuildingTypeClass`, own `_anims[]`, own assets, own behavior. Zero engine-time inheritance from vanilla RA donors; vanilla code paths never reach the TD entity.

Companion docs:
- `docs/building-separation-plan.md` — the M1-M6 milestone plan this recipe operates inside
- `docs/td-audio-routing-recipe.md` — the SFXEvent alias recipe for TD sounds (referenced step 5)
- `docs/cargo-plane-port.md` — TDAFLD reference (shipped pre-separation; will be migrated)
- `docs/adding-td-buildings.md` — the alias-mode recipe being superseded by this one

---

## Per-building cycle time

| Tier | Complexity | Buildings | Estimated per-building cycle |
|---|---|---|---|
| 1 | Pure data | TDNUKE, TDNUK2, TDSILO, TDPYLE | 1-2 hours |
| 2 | Defensive turrets | TDGTWR, TDATWR, TDGUN, TDSAM | 2-3 hours |
| 3 | Economy / production | TDPROC, TDWEAP, TDHPAD, TDFIX, TDAFLD | 3-4 hours |
| 4 | Superweapon hosts | TDHQ, TDEYE, TDTMPL | 3-4 hours |
| 5 | Unique mechanics | TDOBLI (charge+laser, **done**), TDHAND | 4-6 hours |

These are post-recipe-validation estimates. The first one (TDOBLI) took ~8 hours because we were *building* the recipe at the same time. Subsequent buildings should follow the steps without surprises.

---

## Prerequisites — engine infrastructure (already in place)

Built as part of the TDOBLI port. Every future building reuses these — don't re-implement:

1. **`MAX_BUILDING_TYPES = STRUCT_COUNT + 50`** — heap headroom for new enum slots (D1.2 Phase 1).
2. **Heap-aware `BQuantity` / `ActiveBQuantity` / `Prerequisite[]` arrays** on HouseClass (D1.2 Phase 1).
3. **`HouseClass::Has_Building_Active(int type)`** for prereq checks past STRUCT_COUNT.
4. **4-side dispatch** (HOUSE_GOOD / HOUSE_BAD aware) — `dllinterface.cpp:899-910`, vanilla campaign houses untouched.
5. **TD audio routing recipe** — proven and documented (`docs/td-audio-routing-recipe.md`).
6. **Logic= alias `Is_Present` check** — `bdata.cpp:3884-3893`. Mod entries can explicitly clear donor weapons via `Secondary=none`.
7. **`Lines[3][5]` laser-beam render** on TechnoClass — port of TD's render path. Reusable for any future `BULLET_LASER`-firing weapon (none planned in catalogue yet, but available).
8. **`DLL_Draw_Line_Intercept`** exported — RA's DLL didn't expose this before TDOBLI; now does.
9. **`CC_Draw_Line`** wrapper — routes Remastered → launcher, classic → LogicPage.
10. **`scripts/mix_tools.py`** — Westwood MIX reader/writer for extracting TD assets and packing into our mod-shipped `TFASSETS.MIX`.
11. **Per-building dispatch precedent** in building.cpp lines 656 / 4093 / 6244 — Tesla-pattern checks extended with `STRUCT_TDOBLI`. Same pattern applies to any future TD building that needs Tesla-style charge-fire.

---

## The recipe

### Step 1 — Add the STRUCT_TDxxxx enum

`redalert/defines.h`, alongside the existing TD entries (currently just `STRUCT_TDOBLI`):

```cpp
// Tiberian Factions mod buildings — fully separated STRUCT_TDxxxx entries.
STRUCT_TDOBLI,
STRUCT_TD<NEW>,   // <-- new entry, before STRUCT_COUNT
```

Enum order must match the order in `Init_Heap()` (step 3) because the heap-allocation block index doubles as the type number.

### Step 2 — Define the static `Class<Name>` BuildingTypeClass instance

`redalert/bdata.cpp`, modeled on the existing TDOBLI / a vanilla donor closest to your target. Pick a vanilla BuildingTypeClass that shares the target's footprint and turret/non-turret nature:

| TD building | Vanilla template to copy | Why |
|---|---|---|
| TDNUKE / TDNUK2 (power) | ClassPower (POWR) | 2x2 footprint, no turret, no special behavior |
| TDPYLE (GDI barracks) | ClassTent (TENT) | infantry factory, RTTI_INFANTRYTYPE producer |
| TDHAND (Nod barracks) | ClassBarracks (BARR) | infantry factory, 2x3 footprint |
| TDPROC (refinery) | ClassRefinery (PROC) | dock animation, ToBuild=UNIT_HARVESTER |
| TDWEAP (weapons factory) | ClassWeapon (WEAP) | vehicle exit logic |
| TDHPAD | ClassHelipad (HPAD) | helicopter dock |
| TDATWR | ClassAAGun (AGUN) | dual-role turret, missile sound |
| TDGUN | ClassTurret (GUN) | cannon turret |
| TDOBLI | ClassTesla (TSLA) | **done** — charge-then-fire pattern |
| TDSAM | ClassSAM (SAM) | rotating launcher animation |
| TDHQ | ClassCommand (RADAR) | radar dome |
| TDEYE | ClassAdvancedTech (ATEK) | superweapon host |
| TDTMPL | ClassMissileSilo (MSLO) | nuke superweapon host |

Copy the donor's constructor verbatim, then change:
- `STRUCT_TESLA` → `STRUCT_TD<NEW>`
- `TXT_TESLA` → `TXT_NONE` (rules.ini `Name=` overrides)
- `"TSLA"` → `"TD<NEW>"` (IniName — per `[[project-td-prefix-convention]]`)

**⚠️ BEFORE COPYING VERBATIM: run the donor parity check (playbook §3.13).** RA's donor and TD's source can have **different `BSIZE_*` + footprint arrays** even when they're conceptually the same building (TDWEAP hit this — RA BSIZE_32 vs TD BSIZE_33 with row-0 overlap). If they differ, define `TdList<N>`/`TdOList<N>`/`TdExitList<N>` arrays locally mirroring TD source verbatim, and use TD's `BSIZE_*` value.

### Step 3 — Register in `Init_Heap()`

`redalert/bdata.cpp`, after the existing TD entries:

```cpp
// Tiberian Factions mod buildings — keep in STRUCT_TD* enum order.
new BuildingTypeClass(ClassObelisk);   // STRUCT_TDOBLI
new BuildingTypeClass(Class<NEW>);     // STRUCT_TD<NEW>
```

### Step 4 — Per-state animation entries in `_anims[]`

`redalert/bdata.cpp` One_Time, mirror TD source's `_anims[]` entries from `tiberiandawn/bdata.cpp`. Format: `{StructType, BStateType, Start, Length, Rate}`.

Example (TDOBLI):

```cpp
{STRUCT_TDOBLI, BSTATE_ACTIVE, 0, 4, 15},   // 4-frame charge at TD-authentic OBELISK_ANIMATION_RATE
```

Refer to `tiberiandawn/bdata.cpp:3782-3805` (the TD `_anims[]` table) for authoritative per-building values.

### Step 5 — Audio (sounds tied to weapons or anim states)

Per `docs/td-audio-routing-recipe.md`. For each new sound:
1. Add `VOC_TD_*` enum to `redalert/defines.h` (before `VOC_COUNT`).
2. Add `SoundEffectName[]` entry in `redalert/audio.cpp` with the TD asset's bare name.
3. Extract `.WAV` from `SFX3D.MEG` via `scripts/meg_extract.py`.
4. Ship TDC_/TDR_ WAVs unchanged in `resources/.../Data/AUDIO/`.
5. Append `<SFXEvent Name="RAC_SFX_X">` and `<SFXEvent Name="RAR_SFX_X">` alias entries to the merged `Vanilla_RA/Data/XML/AUDIO/SFXEVENTSNONLOCALIZED.XML`.
6. Reference in rules.ini via `Report=X` on the weapon section.

For sounds tied to BSTATE transitions (e.g. OBELPOWR on charge-start): hook the `Sound_Effect` call in the appropriate engine path. TDOBLI uses `BuildingClass::Charging_AI` at building.cpp:6131 with a per-Type branch. Future: a per-weapon `ChargeSound=` field on `WeaponTypeClass` would eliminate the type check.

### Step 6 — Per-building behavior dispatch (when needed)

For buildings sharing a vanilla pattern (e.g. Tesla charge, SAM rising), extend the existing `*this == STRUCT_X` checks in building.cpp to include the new STRUCT_TDxxxx. **This is the vanilla pattern**, not a shortcut — see `STRUCT_SAM` checks at lines 6232/668, `STRUCT_TESLA` at 656/4093/6244, `STRUCT_CAMOPILLBOX` at 6283.

Tesla-pattern buildings additionally need `Charges=yes` on their weapon (drives `Charging_AI` state machine).

### Step 7 — Classic-mode SHP shipping

Extract the TD building's SHPs from `CNCDATA/TIBERIAN_DAWN/CD1/CONQUER.MIX`:

```bash
python3 scripts/mix_tools.py extract \
  ~/.steam/steam/steamapps/common/CnCRemastered/Data/CNCDATA/TIBERIAN_DAWN/CD1/CONQUER.MIX \
  OBLI.SHP /tmp/td_extract
python3 scripts/mix_tools.py extract \
  ~/.steam/steam/steamapps/common/CnCRemastered/Data/CNCDATA/TIBERIAN_DAWN/CD1/CONQUER.MIX \
  OBLIMAKE.SHP /tmp/td_extract
```

Then **re-pack** into the existing `resources/remaster_mods/Vanilla_RA/CCDATA/TFASSETS.MIX` with TD-prefix renames:

```bash
python3 scripts/mix_tools.py pack \
  resources/remaster_mods/Vanilla_RA/CCDATA/TFASSETS.MIX \
  /tmp/td_extract/OBLI.SHP:TDOBLI.SHP \
  /tmp/td_extract/OBLIMAKE.SHP:TDOBLIMAKE.SHP
  ... existing entries ...
```

(Note: `mix_pack.py` currently does NOT merge with existing — re-running rebuilds from scratch. Pass ALL the existing files plus the new one. Future enhancement: an `--append` mode.)

`MFCD::Retrieve` finds the new SHPs via `Init_Heap()`'s standard load loop (`bdata.cpp:3185-3187`). No engine changes per-building.

**Classic-mode caveat:** TD SHPs use TD's PALETTE.PAL color indices. Rendered with RA's PALETTE.PAL → mild color mismatch (looks ~95% right). Fix is a one-time `mix_tools.py` extension implementing Westwood Format80 codec + closest-color remap; deferred to a "classic-mode SHP polish" iteration. Remastered mode unaffected — launcher intercepts before SHP rendering and uses our TGA tileset.

**Overlay SHPs (war-factory-style door layers):** if the building renders in two layers (body + animated overlay like WEAP+WEAP2), ship BOTH SHPs into TFASSETS.MIX (e.g. `WEAP2.SHP:TDWEAP2.SHP`) **and** add a TD-specific static pointer (`BuildingTypeClass::WarFactoryOverlayTd` or similar) loaded in `One_Time`. RA's existing `WarFactoryOverlay` static is hardcoded to load `WEAP2.SHP` and is drawn for every STRUCT_WEAP-style building — without a per-type dispatch in `Draw_It`, RA's overlay renders on top of TD's body. Plus: the TGA tileset XML for the overlay must have shape entries matching TD's `Open_Door(rate, stages)` call (see playbook §3.15). Worked example: TDWEAP2 in `5c0c17e`.

### Step 8 — TGA tileset for Remastered mode

If the building's TGA assets aren't already in `RA_STRUCTURES.XML`:

```bash
python3 scripts/add_building.py <name> --skip-assets    # rules.ini regen
python3 scripts/bundle_assets.py                          # MEG extract + XML patch
```

(Or use the existing alias-mode manifest entry — most buildings already have TGA assets shipped from v0.3 work.)

### Step 9 — rules.ini cleanup

Drop the `Logic=X` line from the building's `[TD<NAME>]` section (no longer needed — we're not aliasing). Comment out the building's entry in `[NewBuildings]` (no longer needed — registered via Init_Heap now). The `[TD<NAME>]` section's other fields (Cost, Power, Strength, Sight, Owner, Armor, etc.) still get Read_INI'd into the heap entry.

### Step 10 — Manifest cleanup

`scripts/buildings_manifest.py`: set `"logic": None` on the entry. Add a comment that the building is now STRUCT_TD-separated. This prevents `scripts/add_building.py` from re-emitting Logic= or re-adding to [NewBuildings].

### Step 11 — Build / deploy / test

```bash
CMAKE_TOOLCHAIN_FILE=cmake/i686-mingw-w64-toolchain.cmake \
  VC_CXX_FLAGS="-w;-fpermissive" \
  cmake --workflow --preset remaster
./deploy.sh --no-build --yes
```

Full game restart on the Deck (DLL has new enum value → new save format).

**Per-building test checklist:**
- [ ] Sidebar cameo visible
- [ ] Build queue advances correctly
- [ ] Construction sound plays (TD's CONSTRU2 for any STRUCT_TDxxxx via the range check at `building.cpp:3940`)
- [ ] Buildup animation cycles through TDxxxxMAKE TGA frames
- [ ] Idle sprite renders correctly
- [ ] Per-building-specific behaviors (e.g. for turrets: rotates and fires; for refinery: harvester docks; for power plant: contributes power)
- [ ] Sell works, refunds correctly
- [ ] Save/load preserves the building
- [ ] AI builds it when appropriate
- [ ] Classic graphics mode renders the sprite (with documented palette imperfection)

---

## Common gotchas (learned from TDOBLI)

1. **`ImageData` / `BuildupData` must be non-NULL** or the engine bails on Draw_It with width=height=0. Shipping SHPs via TFASSETS.MIX (step 7) is what populates these — without that the engine falls back to invisible.

2. **`_anims[]` overrides apply AFTER rules.ini parsing.** If rules.ini has `ActiveAnimStart=0 Count=4 Rate=15` and `_anims[]` has different values for the same `{Type, Stage}`, the `_anims[]` table wins (it runs in `One_Time()` after `Rule.Process()`).

3. **The `Logic=` block's weapon fallback** (`bdata.cpp:3885-3893`) only fires when the section *doesn't mention* Primary=/Secondary= at all (Is_Present check). Setting `Primary=none` doesn't trigger the fallback (the parsed result is NULL, but the key was present). This matters when migrating from alias to separation — if you forget to remove `Logic=` from rules.ini, the donor's weapon could still leak in.

4. **Charges=yes on the weapon** wires the wielder into `BuildingClass::Charging_AI` (`building.cpp:6094`). This is the engine's "wind up then fire" state machine — same one Tesla Coil uses. Not a shortcut; it's the authentic mechanism (TD's source has the same `IsCharging/IsCharged` fields in `tiberiandawn/building.h:115-116` and resets them at `tiberiandawn/building.cpp:852-857` in the BULLET_LASER case).

5. **Per-type dispatch checks in building.cpp** (e.g. shape selection at line 656, crew spawn at line 4093, animation guard at line 6244) are the vanilla pattern. Extending Tesla-keyed checks to include `STRUCT_TDOBLI` for shared charge-fire behavior is correct, not a hack. Future cleanup is to refactor these to per-`BuildingTypeClass` flags, but the type-check pattern is the engine's existing idiom.

6. **`Electric_Zap` suppression** for laser-type weapons is bullet-type-keyed (`techno.cpp:3414-3433`): `if (weapon->Bullet->Type == BULLET_LASER)` → skip lightning, the laser-line beam renders instead. Future TD weapons firing BULLET_LASER auto-inherit this; no per-building code needed.

7. **TD's `IsCharging/IsCharged` flags exist in `tiberiandawn/building.h` but aren't driven by TD's source** (no Charging_AI in TD). The flags are vestigial in TD; RA's Charging_AI drives them. We use RA's mechanism because it works correctly with the BSTATE_ACTIVE animation, same outcome as TD-source behavior would produce if implemented.

8. **Classic-mode spacebar toggle CANNOT be disabled from the mod side.** Tried `Legacy_Render_Enabled` returning false (black screen on toggle) and overriding `DATA/XML/INPUTTRANSLATORCONFIGURATIONS.XML` (launcher ignores the mod XML for this binding). Player must rebind in Options → Controls if they want to disable the toggle. Mod README should document the palette-mismatch limitation in classic mode.

9. **Save format**: new STRUCT_TDxxxx enum values change `sizeof(BuildingTypeClass)` array indices. Mid-campaign saves from a previous build will not load. We're not shipping campaigns yet so blast radius is skirmish-only, but worth flagging for any future campaign work.

---

## What this recipe doesn't cover yet

These come up when the catalogue extends past TDOBLI:

- **Unit types (TD harvester, MCV, C-17, infantry, vehicles)** — same separation philosophy, parallel recipe needed for `UnitTypeClass` / `InfantryTypeClass` / `AircraftTypeClass`. Will fork a sibling recipe doc when unit work starts.
- **HouseClass build orders** — RA's AI base-build sequences are STRUCT_*-indexed. Adding STRUCT_TDxxxx entries needs parallel AI sequences for HOUSE_GOOD / HOUSE_BAD. Covered in `docs/building-separation-plan.md §3.1 H2`.
- **EVA voice routing** — faction-aware VoxType (parallel to VocType). Defer to dedicated work after first wave of buildings.
- **Format80 codec + palette remap** — pixel-perfect classic mode. Single one-shot iteration applied to every TD-sourced SHP at once.
- **Classic-mode TFASSETS.MIX append mode** — `mix_tools.py pack` currently rebuilds; future `--append` would add per-building incrementally.
