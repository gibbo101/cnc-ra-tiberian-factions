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
6. **`Lines[3][5]` laser-beam render** on TechnoClass — port of TD's render path. Reusable for any future `BULLET_LASER`-firing weapon (none planned in catalogue yet, but available).
7. **`DLL_Draw_Line_Intercept`** exported — RA's DLL didn't expose this before TDOBLI; now does.
8. **`CC_Draw_Line`** wrapper — routes Remastered → launcher, classic → LogicPage.
9. **`scripts/mix_tools.py`** — Westwood MIX reader/writer for extracting TD assets and packing into our mod-shipped `TFASSETS.MIX`.
10. **Per-building dispatch precedent** in building.cpp lines 656 / 4093 / 6244 — Tesla-pattern checks extended with `STRUCT_TDOBLI`. Same pattern applies to any future TD building that needs Tesla-style charge-fire.

---

## The recipe

### Step 1 — Add the STRUCT_TDxxxx enum

`redalert/defines.h`, alongside the existing TD entries (currently just `STRUCT_TDOBLI`):

```cpp
// Tiberian Factions mod buildings — fully separated STRUCT_TDxxxx entries.
STRUCT_TDOBLI,
STRUCT_TD<NEW>,   // <-- new entry, before STRUCT_COUNT
```

Keep the enum and `Init_Heap()` (step 3) in the same order: see the field manual's [Adding a unit](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/adding-a-unit.md#2-registration-keep-heap-order-and-enum-order-the-same), section 2.

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
- `"TSLA"` → `"TD<NEW>"` (IniName — the TD prefix, gotcha 9)

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

See the field manual's [TD sounds from the base game](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-sounds-from-the-base-game.md#the-method), The method. TF names them `VOC_TD_*` (`redalert/defines.h`, `SoundEffectName[]` in `redalert/audio.cpp`), and its merged file is `Vanilla_RA/Data/XML/AUDIO/SFXEVENTSNONLOCALIZED.XML`. If a routed sound stays silent, extract its samples with `scripts/meg_extract.py` and ship them in `resources/.../Data/AUDIO/` (`td-audio-routing-recipe.md`).

For sounds tied to BSTATE transitions (e.g. OBELPOWR on charge-start): hook the `Sound_Effect` call in the appropriate engine path. TDOBLI uses `BuildingClass::Charging_AI` at building.cpp:6131 with a per-Type branch. Future: a per-weapon `ChargeSound=` field on `WeaponTypeClass` would eliminate the type check.

### Step 6 — Per-building behavior dispatch (when needed)

For buildings sharing a vanilla pattern (e.g. Tesla charge, SAM rising), extend the existing `*this == STRUCT_X` checks in building.cpp to include the new STRUCT_TDxxxx. **This is the vanilla pattern**, not a shortcut — see `STRUCT_SAM` checks at lines 6232/668, `STRUCT_TESLA` at 656/4093/6244, `STRUCT_CAMOPILLBOX` at 6283.

Tesla-pattern buildings additionally need `Charges=yes` on their weapon (drives `Charging_AI` state machine).

### Step 7 — Classic-mode SHP shipping

Extract the TD building's SHPs from `CNCDATA/TIBERIAN_DAWN/CD1/CONQUER.MIX`:

```bash
python3 scripts/mix_tools.py extract \
  "$(python3 scripts/steam_library.py path common/CnCRemastered)/Data/CNCDATA/TIBERIAN_DAWN/CD1/CONQUER.MIX" \
  OBLI.SHP /tmp/td_extract
python3 scripts/mix_tools.py extract \
  "$(python3 scripts/steam_library.py path common/CnCRemastered)/Data/CNCDATA/TIBERIAN_DAWN/CD1/CONQUER.MIX" \
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

**Classic mode is locked out, but the classic SHP is still needed.** Nobody sees it drawn: it gives the building a non-NULL `ImageData` and `BuildupData` and the dimensions of its box (gotcha 1). Add it as one line in `scripts/build_tfassets.sh` rather than packing by hand. A building with no TD SHP takes a stub (`scripts/gen_stub_shp.py`, as `build_tfassets.sh` does for the TS walkers) or a donor in `bdata.cpp`'s `_td_bdonors` table, which lends a counterpart's `ImageData`, `BuildupData` and `CameoData`. (Palette-remap technique record: `classic-mode-palette-remap.md`.)

**Overlay SHPs (war-factory-style door layers):** if the building renders in two layers (body + animated overlay like WEAP+WEAP2), ship BOTH SHPs into TFASSETS.MIX (e.g. `WEAP2.SHP:TDWEAP2.SHP`) **and** add a TD-specific static pointer (`BuildingTypeClass::WarFactoryOverlayTd` or similar) loaded in `One_Time`. RA's existing `WarFactoryOverlay` static is hardcoded to load `WEAP2.SHP` and is drawn for every STRUCT_WEAP-style building — without a per-type dispatch in `Draw_It`, RA's overlay renders on top of TD's body. Plus: the TGA tileset XML for the overlay must have shape entries matching TD's `Open_Door(rate, stages)` call (see playbook §3.15). Worked example: TDWEAP2 in `5c0c17e`.

### Step 8 — TGA tileset for Remastered mode

If the building's TGA assets aren't already in `RA_STRUCTURES.XML`:

```bash
python3 scripts/add_building.py <name> --skip-assets    # rules.ini regen
python3 scripts/bundle_assets.py                          # MEG extract + XML patch
```

### Step 9 — Build / deploy / test

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

1. **`ImageData` / `BuildupData` must be non-NULL**: `BuildingClass::Draw_It` returns at once on a NULL `Get_Image_Data()`, so the building is invisible. Shipping an SHP via TFASSETS.MIX (step 7), a stub SHP, or a `_td_bdonors` donor in `bdata.cpp` populates them.

2. **`_anims[]` overrides apply AFTER rules.ini parsing.** See the field manual's [Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#build-ups-overlays-and-loading-order), Build-ups, overlays and loading order.

3. **Charges=yes on the weapon** wires the wielder into `BuildingClass::Charging_AI` (`building.cpp:6094`), the Tesla Coil's wind-up-then-fire state machine: the authentic mechanism, not a shortcut. See the field manual's [Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#the-obelisk-charge-then-a-laser), The Obelisk: charge, then a laser. (TD's flags: `tiberiandawn/building.h:115-116`, reset at `tiberiandawn/building.cpp:852-857` in the BULLET_LASER case.)

4. **Per-type dispatch checks in building.cpp** (e.g. shape selection at line 656, crew spawn at line 4093, animation guard at line 6244) are the vanilla pattern. Extending Tesla-keyed checks to include `STRUCT_TDOBLI` for shared charge-fire behavior is correct, not a hack. Future cleanup is to refactor these to per-`BuildingTypeClass` flags, but the type-check pattern is the engine's existing idiom.

5. **`Electric_Zap` suppression** for laser-type weapons is bullet-type-keyed (`techno.cpp:3414-3433`): `if (weapon->Bullet->Type == BULLET_LASER)` → skip lightning, the laser-line beam renders instead. Future TD weapons firing BULLET_LASER auto-inherit this; no per-building code needed.

6. **TD drives `IsCharging/IsCharged` from its own Obelisk block in `BuildingClass::AI` (its "Obelisk charging logic"; TD has no separate `Charging_AI`); RA's `Charging_AI` drives the same flags for the Tesla Coil.** See the field manual's [Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#the-obelisk-charge-then-a-laser), The Obelisk: charge, then a laser. Which one TF's Obelisk runs is in `td-obli-verification.md`.

7. **Classic mode is locked out.** TF is HD-only (gotcha 1 for why the classic SHP still ships). See the field manual's [HD-only mods](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/getting-started/hd-only-mods.md#the-switch), The switch.

8. **Save format:** new STRUCT_TDxxxx types change the save version. See the field manual's [Save versions](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/save-versions.md).

9. **IniName collisions break an entry silently.** An IniName matching a vanilla building (HPAD, GUN, SAM, AFLD, WEAP, FIX, PROC, SILO, FACT) shares its rules.ini section with it. Prefix every TD IniName with `TD`. See the field manual's [Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#give-each-port-its-own-type), Give each port its own type ("The INI name shares one namespace").
10. **The damaged shape is derived from the animation count.** See the field manual's [Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#the-flags-that-decide-the-frames), The flags that decide the frames.
11. **`Points=` is mandatory, or the AI ignores the building.** See the field manual's [Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#placement-and-the-ai), Placement and the AI. TF's values: `catalogue.md`'s Points column.
12. **A MAKE tileset's shape 0 must be `<Frame />`.** See the field manual's [Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#build-ups-overlays-and-loading-order), Build-ups, overlays and loading order.
13. **The launcher picks the ZIP from the frame path's first segment.** See the field manual's [HD tilesets and ZIPs](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/hd-tilesets-and-zips.md#the-pieces-by-example), The pieces, by example.
14. **`Owner=` needs `GoodGuy` / `BadGuy` explicitly.** HOUSE_GOOD and HOUSE_BAD are detached from `HOUSEF_ALLIES` / `HOUSEF_SOVIET`, so `Owner=allies` grants GDI nothing.
15. **`aftrmath.ini` overrides `rules.ini`;** patch both (E3 once stayed unbuildable for GDI because aftrmath.ini's `[E3] Owner=allies` won). See the field manual's [Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#build-ups-overlays-and-loading-order), Build-ups, overlays and loading order.
16. **`ShapeSize=` must match the footprint at 24 px a cell:** 1x1 `24,24`, 2x1 `48,24`, 1x2 `24,48`, 2x2 `48,48`, 3x2 `72,48`, 3x3 `72,72`, 4x2 `96,48`. The wrong ratio stretches the sprite into the wrong box (TDFACT shipped as `72,72` on a 3x2 and bulged off its pad). Count the cells in the `List**` array.
17. **RA's `Track13` drives pure south.** See the field manual's [Units leaving buildings: exits and rails](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/exits-and-rails.md#how-red-alert-does-it), How Red Alert does it. TD-style vehicle factories exit on `Track14` (the SW variant, `OUT_OF_WEAPON_FACTORY_TD`), forced from `BuildingClass::Mission_Unload` with the destination at `Adjacent_Cell(Center_Coord(), FACING_SW)` so the track starts exactly at the spawn; a follow-up `Assign_Destination` keeps the unit moving after the track ends.
18. **Separating a shared RA production building:** never owner-open the RA one (`naval-and-air-units.md`). Copy its art into `TD*`-named files (`scripts/bundle_ra_building.py`), never share frames. The engine hardcodes `STRUCT_SHIP_YARD` / `SUB_PEN` / `AIRSTRIP` in about 30 sites (vessel exit, dock, repair, fixed-wing landing, the `STRUCTF_AIRSTRIP` BScan flag); add the new type to each that applies (`TDAFLD` is the airstrip precedent). Units keep the RA prerequisite token (`syrd`, `spen`, `afld`) plus a `Can_Build` equivalence, because `BuildingTypeClass::From_Name` resolves only below `STRUCT_COUNT`, so a `tdgyard` token silently fails.
19. **`Occupy_List` must match the `BSIZE_*`.** See the field manual's [Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#placement-and-the-ai), Placement and the AI.
20. **Era tests are range tests.** TD and TS buildings sit in one run of the enum ending at
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
