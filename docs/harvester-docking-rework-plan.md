# Harvester docking

**Status:** Reference; shipped in 3.0.0, the TS harvester pairings in 5.0.0.

Every harvester docks at every refinery, and the unload style follows the **harvester**, not the
refinery. A TD harvester at a TD refinery attaches as cargo and the building animates; every other
pairing keeps the harvester visible and radio-tethered for the whole unload, so capturing the
refinery takes the unloading harvester. Dock time is equal across pairings
(`HARV_DOCK_BAILS_PER_CYCLE` = 2 in `unit.h`, half the TD-matched time). The TS refinery dock and the
TS harvester's seats are in `ts-gdi-tree-plan.md`. Walled-field recovery is
`harvester-recovery-design.md`.

## The pairings

| Harvester | Refinery | Unload |
|---|---|---|
| TD (`UNIT_TDHARV`) | TD (`STRUCT_TDPROC`) | TD's own: limbo'd as cargo, the building's ACTIVE/AUX1/AUX2 cycle banks a bail per cycle (`Mission_Harvest_TD`); capture takes it via `Attached_Object` |
| RA (`UNIT_HARVESTER`) | any | the visible dust loop below, at that refinery's dock cell; the TD refinery's animation never fires |
| TD | RA (`STRUCT_REFINERY`) | parks on the south apron, timer-driven offload (`TD_DOCK_OFFLOAD_DELAY`) under one green `ANIM_TIB_FUMES` plume attached to the refinery |
| TS (`UNIT_TSHARV`) | RA or TD | the TD harvester's park-offload path (no dump frames on the voxel sprite); at a TD refinery it is diverted from the attach path |

**Never fire the TD refinery's dock animation for another harvester:** `PROC.SHP` has a TD
harvester drawn into its docking frames (12–29), so the bay would show two trucks.

## The RA dust loop

The RA refinery has no docking animation (no `STRUCT_REFINERY` anim rows in `bdata.cpp`), so the
cadence runs off the harvester. Over the dump frames (SHP index = dump-list value + 96):
1. **Tip-up, once:** SHP 96 → 103.
2. **Unload loop:** SHP 104 → 109, banking `HARV_DOCK_BAILS_PER_CYCLE` bails per wrap
   (`Offload_Tiberium_Bail`) until the load is empty, at `DOCK_DUMP_RATE` = 3 ticks a frame
   (decoupled from `Rule.OreDumpRate`).
3. **Undock, once:** SHP 110, then 102 → 96; `RADIO_OVER_OUT`, back to `MISSION_HARVEST`.

Traps:
- **The loop wrap and per-bail offload live in `UnitClass::AI`**, every frame. `Mission_Unload`
  runs only every `Normal_Delay` ticks, so a stage there overshoots into the down-ramp and the
  bucket bobs.
- **The RA dump animation is one fixed west-facing pose**, so every RA harvester dumps facing west
  whatever the dock.
- **Capture needs the radio tether for the whole unload.** `RADIO_UNLOADED` is sent at Phase 3, not
  at backup time; `BuildingClass::Captured` then takes the radio-contact harvester, gated on
  `IsDumping` so one still approaching is not taken. Don't reach for a position scan.

## The two vanilla mechanics, side by side

| Aspect | RA: UNIT_HARVESTER → STRUCT_REFINERY (vanilla) | TD: UNIT_TDHARV → STRUCT_TDPROC |
|---|---|---|
| Dock cell | DIR_S of center — `building.cpp:435-437` | DIR_SW of center — `building.cpp:439-452` |
| Drive-in | turn DIR_W, stay on dock cell, tether — `unit.cpp:901-915` | turn DIR_SW, `Force_Track(BACKUP_INTO_REFINERY, Adjacent_Cell(Center,FACING_N))` drives INTO footprint — `unit.cpp:876-899` |
| Attach trigger | none — harvester stays visible on the dock cell | `Per_Cell_Process` cell-match → `RADIO_IM_IN` → `RADIO_ATTACH` → `Mark(MARK_UP); Limbo(); whom->Attach(this)` — `unit.cpp:1962-1996` |
| Building RADIO_IM_IN | `from->Assign_Mission(MISSION_UNLOAD); return RADIO_ROGER` — `building.cpp:326-329` | `Begin_Mode(BSTATE_ACTIVE); Assign_Mission(MISSION_HARVEST); return RADIO_ATTACH` — `building.cpp:331-345` |
| Who unloads | the **harvester** runs `Mission_Unload` — `unit.cpp:2947-2974` | the **building** runs `Mission_Harvest_TD` — `building.cpp:5400-5492` |
| Unload model | one-shot: `House->Harvested(Credit_Load())` when dump anim ends | bail-by-bail: `Offload_Tiberium_Bail()` per cycle — `unit.cpp:5530-5586` |
| Cadence driver | harvester dump anim (`Rule.OreDumpRate`, 22-frame `Harvester_Dump_List`) | **building animation** reaching its last frame sets `IsReadyToCommence` — `building.cpp:7560-7590` |
| Refinery anim | **NONE** — only static `BSTATE_IDLE` (1 frame) + `BSTATE_FULL` flashing lights. No ACTIVE/AUX1/AUX2 rows in `bdata.cpp` (`ClassRefinery`, line 1491). | full cycle — `bdata.cpp:3944-3948` (ACTIVE 12,7,4 / AUX1 19,5,4 / AUX2 24,6,4 / IDLE / FULL) |
| Harvester during unload | **visible**, animated tip-up | **invisible** (Limbo'd, attached cargo) |
| Capture grabs harvester? | NO — radio contact only, distance-gated path may eject it — `building.cpp:4260-4271` | YES — `Attached_Object()` → `tech->Captured(newowner)` — `building.cpp:4251-4253` |
| Exit | instant respawn at dock cell | `Exit_Object(Detach_Object())` → `Unlimbo` + `Force_Track(OUT_OF_REFINERY)` — `building.cpp:2720-2754` |

## Dock time

Vanilla RA dumped a full load in one shot. Every path was first tuned to the ~588-tick TD dock time
(28 bails), then `HARV_DOCK_BAILS_PER_CYCLE` = 2 halved all four pairings together: animation cadence
unchanged, fewer cycles, credits per load unchanged. Keeping the same value on every pairing keeps
the RA and TD economies equal, which is what makes cross-faction unit balance tractable. 1 =
TD-matched, 4 = close to RA's instant dump.

## Recovery lessons that apply to docking
- **Two detectors, and only one blacklists.** The ore no-progress detector owns field blacklisting
  (A* reachability); the position watchdog owns physical un-sticking and idle restart and must not
  blacklist, because it can't tell an unreachable field from a wedged harvester (it poisoned good
  fields: 151 skips, down to 4 once it stopped).
- **Most "stuck" harvesters on the shipped maps are terrain** (cliff- or water-separated ore, narrow
  gaps), not infantry pins.
- **A* can report a short path a harvester can't physically thread** through a packed base, which
  is why the watchdog and blacklist retry are the recovery, not a smarter pick.
