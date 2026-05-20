# Session handoff — GDI TDMCV + TDFACT for son-playtest

> **STATUS: ✅ COMPLETED 2026-05-20 (v0.3.0-phase5e/f).** All 4 scope pieces
> landed. TDFACT + TDMCV + scenario-spawn intercept + deploy intercept all
> work end-to-end on the Deck. TD-authentic build times also wired up.
> See `memory/project-next-session-mcv-conyard.md` (now retitled
> Workshop-publish goal) for what's next.



**Goal:** GDI house starts a skirmish with a TD-style MCV that deploys into a TD-style Construction Yard. Authentic "wake up as GDI" feel. Target audience: kids playtest on Steam Deck.

**Previous session (this file written at end of):** GDI building bug round closed — TDPROC/TDSILO storage, TDSILO footprint, TDEYE sprite+buildup, TDATWR weapon (Hellfire) + force-fire fix, Logic= alias weapon copy. See `docs/catalogue.md` "Building bugs found during 2026-05-20 playtest" section for the historical context.

## Scope — 4 pieces

### 1. TDFACT building (Construction Yard)
- Already in the master flag table at `docs/catalogue.md:290` — `TDFACT, both, FACT, 5000 cost, -30 power, 400 HP, 3 sight, 1 adj, wood, yes/yes/yes/yes, 0/4/3 idle, 70 points, TD lvl 99`.
- Use the existing pipeline: add a `TDFACT` entry to `scripts/buildings_manifest.py`, then `python3 scripts/add_building.py --all`. Asset side: bundle TDFACT.ZIP + TDFACTMAKE.ZIP via `scripts/bundle_assets.py` (already covers prior entries).
- Logic=FACT. RA FACT is `BSIZE_33`; TD FACT in `tiberiandawn/bdata.cpp` ClassConst is also `BSIZE_33` — so no Footprint preset needed unless visual scale forces a `ShapeSize=` tweak (will know at first deploy).
- Bib=yes, Crew=yes (TD-authentic, crew spawns 5 minigunners on sell).

### 2. TDMCV vehicle (the first vehicle in the mod)
- **No add-vehicle script exists yet.** Two paths:
  - **Extend `scripts/add_building.py`** to also handle RTTI_UNITTYPE — generalize the FIELD_SPEC list. Probably the right long-term move but adds complexity to the script.
  - **One-off the rules.ini emit** for TDMCV by hand. Faster for v1 entry; bake it into a script later when we have 3+ vehicles to amortize.
- Manifest fields needed: ininame, logic="MCV", td_asset="MCV", shape_size (probably 48,48), cost, hp, armor, sight, speed, prereq=TDFACT (so it can be built from the warfact after losing your starting one), owner=GoodGuy initially.
- Logic=MCV inheritance: vanilla RA MCV is STRUCT_NONE / RTTI_UNITTYPE, UnitTypeClass not BuildingTypeClass. **The Logic= alias mechanism currently only exists in BuildingTypeClass::Read_INI** (`redalert/bdata.cpp:3820-3868`). Need to mirror it in UnitTypeClass::Read_INI (`redalert/udata.cpp`) — donor copy of stats, ImageData, weapon pointers etc.

### 3. TDMCV → TDFACT deploy
- `UnitTypeClass::ToBuild` is the field that determines what building the unit produces on deploy.
- For vanilla MCV: `ToBuild = STRUCT_CONST` (line in `udata.cpp` ClassMCV constructor).
- For TDMCV: set ToBuild to TDFACT's heap index. Mod entries are past STRUCT_COUNT — TDFACT's index assigned dynamically by `new BuildingTypeClass(int rtti, char const* ininame)` in rules parsing.
- Resolution mechanism: Read_INI for unit could read `ToBuild=TDFACT` from rules.ini and call `BuildingTypeClass::As_Pointer("TDFACT")` to get the index. Mirrors the prereq parser fix from `v0.3.0-phase4a` (commit cddc856).
- **Test path:** deploy via right-click on selected TDMCV → should produce TDFACT not STRUCT_CONST.

### 4. GDI scenario-start spawn swap
- Skirmish/multiplayer engine spawns each house with a vanilla MCV at scenario start.
- Code path: probably `redalert/scenario.cpp` or `redalert/house.cpp` `Create_Unit_If_Possible` / similar. Search for `UNIT_MCV` to find spawn sites.
- Intercept: if `House->Class->House == HOUSE_GOOD` (and later HOUSE_BAD for Nod), spawn TDMCV instead. TDMCV's heap UnitType index lookup via `UnitTypeClass::As_Pointer("TDMCV")`.
- Save-load: if TDMCV index serializes by index, save format may break across catalogue churn. Probably fine for v0.3 since saves aren't a v1 feature yet.

## Gotchas already known (don't re-walk these)

- **Logic= alias is BuildingTypeClass-only currently.** Mirroring for units requires reading `redalert/udata.cpp` UnitTypeClass::Read_INI carefully — the field set differs from buildings (no Adjacent, no Capacity, no Storage; has Speed, ROT, Crew, etc.).
- **Theater-specific donors lazy-load ImageData via Init(theater).** Our Init(theater) refresh hook at `bdata.cpp:Init` covers BuildingTypeClass. If TDMCV's donor (vanilla MCV — UNIT_MCV) is theater-specific (probably yes for snow theaters), need an equivalent refresh for units.
- **AAGUN force-fire pattern from this session** (`building.cpp:3061` made weapon-capability-based) is a precedent for not breaking vanilla while unlocking mod entries — same pattern may apply to UnitClass Type-based dispatches.
- **Anims[BSTATE_CONSTRUCTION] copy timing**: see `bdata.cpp:Init(theater)` end-of-loop mod-refresh block. Units don't have buildup animations (they don't BSTATE_CONSTRUCTION) but they DO have body shape arrays per direction — different inheritance concern.
- **Diagnostic logging convention**: `tf_*.log` under `%USERPROFILE%/Documents/CnCRemastered/`. Add `tf_mcv_deploy.log` if needed. See `[[reference-diagnostic-paths.md]]`.
- **Asset names in XML**: TDMCV will need entries in `RA_UNITS.XML` (similar to RA_STRUCTURES.XML pattern). Verify the path is wired in `scripts/bundle_assets.py`.

## Where to start in the new session

1. `git log --oneline -5` to confirm clean state.
2. Read `docs/catalogue.md:108-200` for the parked-bugs + immediate-next-work context (most of which is now resolved — this handoff supersedes the MCV/vehicle notes).
3. Read `redalert/udata.cpp` to understand UnitTypeClass::Read_INI and where to hook the Logic= alias.
4. Search for `UNIT_MCV` to find the scenario-start spawn site.
5. Build TDFACT first (cheapest piece, validates the pipeline). Deploy, screenshot, confirm visual. Then tackle TDMCV.

## Test scenario for son-playtest

- Skirmish, GDI vs Soviet AI, single map (winter theater to exercise theater-specific donor refresh path).
- Expected at start: GDI player has TDMCV. Right-click ground → deploys into TDFACT. From TDFACT, full GDI tech tree is buildable.
- If TDMCV doesn't appear: check `tf_*.log` for spawn intercept failure. If deploy produces vanilla STRUCT_CONST instead of TDFACT: check ToBuild resolution.

## Deployed binary state at handoff

DLL on Deck includes:
- Logic= alias weapon copy (PrimaryWeapon/SecondaryWeapon if NULL)
- Theater-specific donor refresh in Init(theater) for mod entries (ImageData, BuildupData, Anims[BSTATE_CONSTRUCTION])
- AAGUN force-fire weapon-capability check
- Diagnostic log includes Primary/Secondary/TurretEq/Armor/TarCom for TD-prefixed buildings

rules.ini on Deck includes:
- All current TD entries (TDNUKE, TDNUK2, TDPYLE, TDHQ, TDPROC, TDSILO, TDFIX, TDWEAP, TDHPAD, TDGTWR, TDATWR, TDEYE)
- TDATWR: Primary=Hellfire (anti-armor + anti-air via HeatSeeker projectile)
- Vanilla PROC=2000, SILO=1500 (NightFalcon's MODERATE_WARFARE patch reverted)
