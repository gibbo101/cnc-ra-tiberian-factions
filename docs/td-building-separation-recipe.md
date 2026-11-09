# TD building separation recipe: one STRUCT_TDxxxx type per building

**Status:** Reference. The canonical recipe for porting a TD building as its own `STRUCT_TDxxxx`
engine type; every TD building ships this way. Production buildings also need the traps in
`td-port-playbook.md` §3.11–§3.22.

**Recipe scope:** porting a TD building as a fully separated `STRUCT_TDxxxx` heap entry with its own `BuildingTypeClass`, own `_anims[]`, own assets, own behavior. Zero engine-time inheritance from vanilla RA donors; vanilla code paths never reach the TD entity.

Companion docs: `td-audio-routing-recipe.md` (the TD sounds, step 5), `cargo-plane-port.md` (the TDAFLD
delivery).

---

## The engine infrastructure every building reuses

1. **`MAX_BUILDING_TYPES = STRUCT_COUNT + 50`** (`defines.h`): heap headroom for new enum slots.
2. **Heap-sized `BQuantity` / `ActiveBQuantity` / `Prerequisite[]` arrays** on `HouseClass`.
3. **`HouseClass::Has_Building_Active(int type)`** (`house.h`): prerequisite checks per type, past the 32 bits
   `ActiveBScan` holds.
4. **Four-side dispatch,** `HOUSE_GOOD` and `HOUSE_BAD` aware, in `dllinterface.cpp`; the campaign houses are
   untouched.
5. **The TD audio routing** (`td-audio-routing-recipe.md`).
6. **The `Lines[3][5]` laser beam** on `TechnoClass`, TD's line render: `DLL_Draw_Line_Intercept`
   (`dllinterface.cpp`), drawn through the `CC_Draw_Line` wrapper (`conquer.cpp`: the launcher in Remastered,
   `LogicPage` in classic). Any `BULLET_LASER` weapon gets it.
7. **`scripts/mix_tools.py`:** the Westwood MIX reader and writer for TD's assets and `TFASSETS.MIX`.
8. **The Tesla-pattern checks** (`Shape_Number`'s charge frame, the sale crew step, the `Animation_AI` exclusion)
   extended with `STRUCT_TDOBLI`, the precedent for any charge-then-fire building.

---

## The recipe

### Step 1 — Add the STRUCT_TDxxxx enum

`redalert/defines.h`, inside the Tiberian-era run (gotcha 20):

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
| TDOBLI | ClassTesla (TSLA) | charge-then-fire pattern |
| TDSAM | ClassSAM (SAM) | rotating launcher animation |
| TDHQ | ClassCommand (RADAR) | radar dome |
| TDEYE | ClassAdvancedTech (ATEK) | superweapon host |
| TDTMPL | ClassMissileSilo (MSLO) | nuke superweapon host |

The donor gives the argument layout; every value then comes from TD's constructor (`td-atwr-deep-dive.md`: a
tower copied from AGUN kept its turret flag). Copy the donor's constructor, then change:
- `STRUCT_TESLA` → `STRUCT_TD<NEW>`
- `TXT_TESLA` → `TXT_NONE` (rules.ini `Name=` overrides)
- `"TSLA"` → `"TD<NEW>"` (IniName — the TD prefix, gotcha 9)

**Before copying, run the donor parity check (playbook §3.13).** RA's donor and TD's source can have **different `BSIZE_*` + footprint arrays** even when they're conceptually the same building (TDWEAP hit this — RA BSIZE_32 vs TD BSIZE_33 with row-0 overlap). If they differ, define `TdList<N>`/`TdOList<N>`/`TdExitList<N>` arrays locally mirroring TD source verbatim, and use TD's `BSIZE_*` value.

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

Refer to `tiberiandawn/bdata.cpp:3786-3816` (the TD `_anims[]` table) for authoritative per-building values.

### Step 5 — Audio (sounds tied to weapons or anim states)

See the field manual's [TD sounds from the base game](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/using-what-the-player-owns/td-sounds-from-the-base-game.md#the-method), The method. TF names them `VOC_TD_*` (`redalert/defines.h`, `SoundEffectName[]` in `redalert/audio.cpp`), and its merged file is `Vanilla_RA/Data/XML/AUDIO/SFXEVENTSNONLOCALIZED.XML`. If a routed sound stays silent, extract its samples with `scripts/meg_extract.py` and ship them in `resources/.../Data/AUDIO/` (`td-audio-routing-recipe.md`).

For sounds tied to BSTATE transitions (OBELPOWR on charge start), hook the `Sound_Effect` call in the engine path
that makes the transition: TDOBLI's is a per-type branch in `BuildingClass::Charging_AI`. A per-weapon
`ChargeSound=` on `WeaponTypeClass` would remove the type check.

### Step 6 — Per-building behavior dispatch (when needed)

For buildings sharing a vanilla pattern (the Tesla charge, the SAM), extend the existing `*this == STRUCT_X` checks
in `building.cpp` to include the new `STRUCT_TDxxxx`. That is the engine's own idiom, as the `STRUCT_SAM`,
`STRUCT_TESLA` and `STRUCT_CAMOPILLBOX` tests in `Shape_Number`, `Mission_Attack` and `Animation_AI` show.

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

`mix_tools.py pack` doesn't merge with an existing MIX: it rebuilds from scratch, so pass every existing file plus
the new one. `scripts/build_tfassets.sh` holds the whole list; add the new SHP there as one line and rebuild.

`MFCD::Retrieve` finds the new SHPs in `One_Time`'s standard load loop. No engine change per building.

**Classic mode is locked out, but the classic SHP is still needed.** Nobody sees it drawn: it gives the building a non-NULL `ImageData` and `BuildupData` and the dimensions of its box (gotcha 1). A building with no TD SHP takes a stub (`scripts/gen_stub_shp.py`, as `build_tfassets.sh` does for the TS walkers) or a donor in `bdata.cpp`'s `_td_bdonors` table, which lends a counterpart's `ImageData`, `BuildupData` and `CameoData`. (Palette-remap technique record: `classic-mode-palette-remap.md`.)

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
./deploy.sh --yes
```

`deploy.sh` builds and restages; `--no-build` ships `build/` as it stands and is only safe straight after a full
`deploy.sh` run. Restart the game in full: a new enum value is a new save format.

**Per-building test checklist:**
- [ ] Sidebar cameo visible
- [ ] Build queue advances correctly
- [ ] Construction sound plays (TD's CONSTRU2 for every `STRUCT_TDxxxx`, `MISSION_CONSTRUCTION`'s range check)
- [ ] Buildup animation cycles through TDxxxxMAKE TGA frames
- [ ] Idle sprite renders correctly
- [ ] Per-building-specific behaviors (e.g. for turrets: rotates and fires; for refinery: harvester docks; for power plant: contributes power)
- [ ] Sell works, refunds correctly
- [ ] Save/load preserves the building
- [ ] AI builds it when appropriate

---

## Common gotchas

1. **`ImageData` / `BuildupData` must be non-NULL**, or the building is invisible: see the field manual's [Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#build-ups-overlays-and-loading-order), Build-ups, overlays and loading order ("A building with no classic image is invisible"). Shipping an SHP via TFASSETS.MIX (step 7), a stub SHP, or a `_td_bdonors` donor in `bdata.cpp` populates them.

2. **`_anims[]` overrides apply AFTER rules.ini parsing.** See the field manual's [Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#build-ups-overlays-and-loading-order), Build-ups, overlays and loading order.

3. **Charges=yes on the weapon** wires the wielder into `BuildingClass::Charging_AI`, the Tesla Coil's wind-up-then-fire state machine: the authentic mechanism, not a shortcut. See the field manual's [Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#the-obelisk-charge-then-a-laser), The Obelisk: charge, then a laser. (TD's flags: `tiberiandawn/building.h:115-116`, reset at `tiberiandawn/building.cpp:852-857` in the BULLET_LASER case.)

4. **Per-type dispatch checks in `building.cpp`** (the charge frame in `Shape_Number`, the sale crew in
   `Mission_Deconstruction`, the `Animation_AI` guard) are the engine's own pattern. Extending the Tesla-keyed
   checks with `STRUCT_TDOBLI` for shared charge-fire behaviour is correct, not a hack. Per-`BuildingTypeClass`
   flags would be cleaner.

5. **`Electric_Zap` suppression** for laser-type weapons is bullet-type-keyed (`TechnoClass::Fire_At`, `techno.cpp:3915`): `if (weapon->Bullet->Type == BULLET_LASER)` → skip lightning, the laser-line beam renders instead. Future TD weapons firing BULLET_LASER auto-inherit this; no per-building code needed.

6. **TD drives `IsCharging/IsCharged` from its own Obelisk block in `BuildingClass::AI` (its "Obelisk charging logic"; TD has no separate `Charging_AI`); RA's `Charging_AI` drives the same flags for the Tesla Coil.** See the field manual's [Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#the-obelisk-charge-then-a-laser), The Obelisk: charge, then a laser. Which one TF's Obelisk runs is in `td-obli-verification.md`.

7. **Classic mode is locked out.** TF is HD-only (gotcha 1 for why the classic SHP still ships). See the field manual's [HD-only mods](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/getting-started/hd-only-mods.md#the-switch), The switch.

8. **Save format:** new STRUCT_TDxxxx types change the save version. See the field manual's [Save versions](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/save-versions.md).

9. **IniName collisions break an entry silently.** An IniName matching a vanilla building (HPAD, GUN, SAM, AFLD, WEAP, FIX, PROC, SILO, FACT) shares its rules.ini section with it. Prefix every TD IniName with `TD`. See the field manual's [Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#give-each-port-its-own-type), Give each port its own type ("The INI name shares one namespace").
10. **The damaged shape is derived from the animation count.** See the field manual's [Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#the-flags-that-decide-the-frames), The flags that decide the frames.
11. **`Points=` is mandatory, or the AI ignores the building.** See the field manual's [Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#placement-and-the-ai), Placement and the AI. TF's values: `catalogue.md`'s Points column.
12. **A MAKE tileset's shape 0 must be `<Frame />`.** See the field manual's [Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#build-ups-overlays-and-loading-order), Build-ups, overlays and loading order.
13. **The launcher picks the ZIP from the frame path's first segment.** See the field manual's [HD tilesets and ZIPs](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/hd-tilesets-and-zips.md#the-pieces-by-example), The pieces, by example.
14. **`Owner=` needs `GoodGuy` / `BadGuy` explicitly.** HOUSE_GOOD and HOUSE_BAD are detached from `HOUSEF_ALLIES` / `HOUSEF_SOVIET`, so `Owner=allies` grants GDI nothing.
15. **`aftrmath.ini` overrides `rules.ini`;** patch both (`aftrmath.ini`'s `[E3] Owner=allies` kept E3 from GDI). See the field manual's [Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#build-ups-overlays-and-loading-order), Build-ups, overlays and loading order.
16. **`ShapeSize=` must match the footprint at 24 px a cell:** 1x1 `24,24`, 2x1 `48,24`, 1x2 `24,48`, 2x2 `48,48`, 3x2 `72,48`, 3x3 `72,72`, 4x2 `96,48`. The wrong ratio stretches the sprite into the wrong box (TDFACT at `72,72` on a 3x2 bulged off its pad). Count the cells in the `List**` array.
17. **RA's `Track13` drives pure south.** See the field manual's [Units leaving buildings: exits and rails](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/exits-and-rails.md#how-red-alert-does-it), How Red Alert does it. TD-style vehicle factories exit on `Track14` (the SW variant, `OUT_OF_WEAPON_FACTORY_TD`), forced from `BuildingClass::Mission_Unload` with the destination at `Adjacent_Cell(Center_Coord(), FACING_SW)` so the track starts exactly at the spawn; a follow-up `Assign_Destination` keeps the unit moving after the track ends.
18. **Separating a shared RA production building:** never owner-open the RA one (`naval-and-air-units.md`). Copy its art into `TD*`-named files (`scripts/bundle_ra_building.py`), never share frames. The engine hardcodes `STRUCT_SHIP_YARD`, `STRUCT_SUB_PEN` and `STRUCT_AIRSTRIP` (the counts are in the field manual's [Give each port its own type](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#give-each-port-its-own-type); vessel exit, dock, repair, fixed-wing landing, the `STRUCTF_AIRSTRIP` BScan flag); add the new type to each that applies (`TDAFLD` is the airstrip precedent). Units keep the RA prerequisite token (`syrd`, `spen`, `afld`), and a `Can_Build` equivalence lets the new building meet it for its own faction's types.
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
