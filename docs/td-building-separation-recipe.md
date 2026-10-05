# TD building separation recipe — STRUCT_TDxxxx per-building port

**Status:** Reference. The canonical recipe for porting a TD building as its own `STRUCT_TDxxxx`
engine type; every TD building ships this way. Production buildings also need the traps in
`td-port-playbook.md` §3.13–§3.19.

**Recipe scope:** porting a TD building as a fully separated `STRUCT_TDxxxx` heap entry with its own `BuildingTypeClass`, own `_anims[]`, own assets, own behavior. Zero engine-time inheritance from vanilla RA donors; vanilla code paths never reach the TD entity.

Companion docs:
- `docs/td-audio-routing-recipe.md` — the SFXEvent alias recipe for TD sounds (step 5)
- `docs/cargo-plane-port.md` — the TDAFLD cargo-plane delivery

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
- `"TSLA"` → `"TD<NEW>"` (IniName — the TD prefix, gotcha 10)

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

**Classic mode is DROPPED (do NOT do classic SHP work for new buildings).** Since the TD tilesets were added there is no classic art path for the mod's content — classic renders broken and is unsupported (HD-only). Skip the `build_tfassets.sh` palette-remap / classic-SHP step entirely; ship only the HD TGA tileset. (Historical technique record: `classic-mode-palette-remap.md`.)

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
- [ ] ~~Classic graphics mode renders the sprite~~ — N/A, classic mode dropped (HD-only)

---

## Common gotchas (learned from TDOBLI)

1. **`ImageData` / `BuildupData` must be non-NULL** or the engine bails on Draw_It with width=height=0. Shipping SHPs via TFASSETS.MIX (step 7) is what populates these — without that the engine falls back to invisible.

2. **`_anims[]` overrides apply AFTER rules.ini parsing.** If rules.ini has `ActiveAnimStart=0 Count=4 Rate=15` and `_anims[]` has different values for the same `{Type, Stage}`, the `_anims[]` table wins (it runs in `One_Time()` after `Rule.Process()`).

3. **The `Logic=` block's weapon fallback** (`bdata.cpp:3885-3893`) only fires when the section *doesn't mention* Primary=/Secondary= at all (Is_Present check). Setting `Primary=none` doesn't trigger the fallback (the parsed result is NULL, but the key was present). This matters when migrating from alias to separation — if you forget to remove `Logic=` from rules.ini, the donor's weapon could still leak in.

4. **Charges=yes on the weapon** wires the wielder into `BuildingClass::Charging_AI` (`building.cpp:6094`). This is the engine's "wind up then fire" state machine — same one Tesla Coil uses. Not a shortcut; it's the authentic mechanism (TD's source has the same `IsCharging/IsCharged` fields in `tiberiandawn/building.h:115-116` and resets them at `tiberiandawn/building.cpp:852-857` in the BULLET_LASER case).

5. **Per-type dispatch checks in building.cpp** (e.g. shape selection at line 656, crew spawn at line 4093, animation guard at line 6244) are the vanilla pattern. Extending Tesla-keyed checks to include `STRUCT_TDOBLI` for shared charge-fire behavior is correct, not a hack. Future cleanup is to refactor these to per-`BuildingTypeClass` flags, but the type-check pattern is the engine's existing idiom.

6. **`Electric_Zap` suppression** for laser-type weapons is bullet-type-keyed (`techno.cpp:3414-3433`): `if (weapon->Bullet->Type == BULLET_LASER)` → skip lightning, the laser-line beam renders instead. Future TD weapons firing BULLET_LASER auto-inherit this; no per-building code needed.

7. **TD's `IsCharging/IsCharged` flags exist in `tiberiandawn/building.h` but aren't driven by TD's source** (no Charging_AI in TD). The flags are vestigial in TD; RA's Charging_AI drives them. We use RA's mechanism because it works correctly with the BSTATE_ACTIVE animation, same outcome as TD-source behavior would produce if implemented.

8. **Classic mode is unsupported and locked out** by `CNCDisableLegacyGraphicsOption` in `Data/XML/GameConstants_Mod.xml`; new entities need no classic art (`launcher-vs-dll-ownership.md`).

9. **Save format**: new STRUCT_TDxxxx enum values change `sizeof(BuildingTypeClass)` array indices. Mid-campaign saves from a previous build will not load. We're not shipping campaigns yet so blast radius is skirmish-only, but worth flagging for any future campaign work.

10. **IniName collisions break an entry silently.** Registration creates a type only when `As_Pointer(name)` is NULL, so an IniName matching a vanilla building (HPAD, GUN, SAM, AFLD, WEAP, FIX, PROC, SILO, FACT) overrides the vanilla one instead. INI sections share one namespace too: `NUKE` is a vanilla warhead, so a building named NUKE reads the warhead's fields and never builds. Prefix every TD IniName with `TD`; `Image=` and the ZIPs keep TD's own names.
11. **The damaged shape is derived from the animation count.** At `ConditionYellow`, `Shape_Number()` shifts by the largest `Start + Count` across IDLE/ACTIVE/AUX1/AUX2: shape 1 for a static building, shape N for an N-frame idle. Lay frames out 0..N-1 healthy, N..2N-1 damaged.
12. **`Points=` is mandatory, or the AI ignores the building.** `Read_INI` sets Risk = Reward = Points; without it `TechnoClass::Value()` is 0 and `Evaluate_Object` rejects the building, so enemies walk past it and the AI never targets it. Use TD's RISK/RWRD value (`catalogue.md`'s flag table).
13. **A MAKE tileset's shape 0 must be `<Frame />`.** TD's MAKE ZIPs start at frame 0001; pointing shape 0 at a missing 0000 flashes the missing-asset placeholder for a frame on placement.
14. **The launcher picks the ZIP from the frame path's first segment,** not the tileset `<Name>`: `<Frame>tdpyle\tdpyle-0000.tga</Frame>` opens `TDPYLE.ZIP` and looks for `tdpyle-0000.tga` inside. The ZIP name, the first segment and the internal filenames must all match.
15. **`Owner=` needs `GoodGuy` / `BadGuy` explicitly.** HOUSE_GOOD and HOUSE_BAD are detached from `HOUSEF_ALLIES` / `HOUSEF_SOVIET`, so `Owner=allies` grants GDI nothing.
16. **`aftrmath.ini` overrides `rules.ini`,** field by field, `Owner=` included; patch both (E3 once stayed unbuildable for GDI because aftrmath.ini's `[E3] Owner=allies` won).
17. **`ShapeSize=` must match the footprint at 24 px a cell:** 1x1 `24,24`, 2x1 `48,24`, 1x2 `24,48`, 2x2 `48,48`, 3x2 `72,48`, 3x3 `72,72`, 4x2 `96,48`. The wrong ratio stretches the sprite into the wrong box (TDFACT shipped as `72,72` on a 3x2 and bulged off its pad). Count the cells in the `List**` array.
18. **RA's `Track13` is overridden to pure south** (`drive.cpp`, the `#if (1)` block), against `TrackControl`'s declared `DIR_SW` final facing. TD-style vehicle factories exit on `Track14` (the SW variant, `OUT_OF_WEAPON_FACTORY_TD`), forced from `BuildingClass::Mission_Unload` with the destination at `Adjacent_Cell(Center_Coord(), FACING_SW)` so the track starts exactly at the spawn; a follow-up `Assign_Destination` keeps the unit moving after the track ends. `Exit_Object`'s `STRUCT_WEAP` case (spawn at `Exit_Coord()`, `RADIO_TETHER`, the building on `MISSION_UNLOAD`) is the model for any new vehicle factory.
19. **Separating a shared RA production building:** never owner-open the RA one (`naval-and-air-units.md`). Copy its art into `TD*`-named files (`scripts/bundle_ra_building.py`), never share frames. The engine hardcodes `STRUCT_SHIP_YARD` / `SUB_PEN` / `AIRSTRIP` in about 30 sites (vessel exit, dock, repair, fixed-wing landing, the `STRUCTF_AIRSTRIP` BScan flag); add the new type to each that applies (`TDAFLD` is the airstrip precedent). Units keep the RA prerequisite token (`syrd`, `spen`, `afld`) plus a `Can_Build` equivalence, because `BuildingTypeClass::From_Name` resolves only below `STRUCT_COUNT`, so a `tdgyard` token silently fails.
20. **`Occupy_List` must match the `BSIZE_*`.** It feeds the launcher's ghost placement grid,
    `Legal_Placement` and the placement proximity check. The placement preview also draws the bib
    row, so a 2x2 with a bib previews three rows tall: size the building from its `BSIZE_*`, not
    from the preview.
21. **Era tests are range tests.** TD and TS buildings sit in one run of the enum ending at
    `STRUCT_TIBERIAN_LAST` (plus the TS tree block), and `Is_Tiberian_Era` tests that range. A
    "TD"/"TS" IniName prefix test would catch the RA Tesla Coil (`TSLA`, `known-issues.md`). A new
    Tiberian-era building goes inside the run; move the marker if it becomes the last.

---

## Related recipes

- Units: `td-infantry-port-recipe.md`, `td-vehicle-port-recipe.md`; aircraft and bullets in
  `td-port-playbook.md` (§2.7, the donor-ImageData pattern).
- The AI's build choices for a new building: `ai-upgrade-plan.md` (W2, the faction yards and
  `Can_Build`).
- EVA lines: `td-audio-routing-recipe.md` (EVA voice faction routing).
