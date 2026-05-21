# Cargo-plane delivery (TDAFLD / TDC17) — port notes

End-to-end recipe for landing TD's cargo-plane vehicle delivery in RA's
engine. Verified working 2026-05-21 (v0.3.1-phase2d).

The TD source is the spec. RA's port left several mechanics half-finished
or commented out; this doc enumerates each dormant slice and the
specific activation we made.

## The big picture

When a Nod player builds a vehicle at TDAFLD (the Nod airstrip),
`BuildingClass::Exit_Object` doesn't drive the vehicle out via a Track.
Instead it spawns a TDC17 cargo plane at the east map edge, attaches the
vehicle as cargo, and lets the engine drive a four-stage state machine
that flies the plane in, drops the vehicle on a strip-adjacent cell, and
exits the plane off the west edge.

Mirrors `tiberiandawn/reinf.cpp`'s `Do_Reinforcements` `SOURCE_AIR` path
plus `tiberiandawn/aircraft.cpp`'s fixed-wing `Mission_Unload`, with
adjustments where RA's surrounding infrastructure differs.

## The ten dormant mechanics

Each item is a piece of RA infrastructure that was missing, half-built,
or commented out, and what we did to activate it.

### 1. AIRCRAFT_TDCARGO type slot

`redalert/defines.h`, `redalert/aadata.cpp`. RA's aircraft heap had no
cargo-plane slot. Added `AIRCRAFT_TDCARGO` to the enum (post-HIND, pre-
COUNT) with matching `AIRCRAFTF_TDCARGO` bitmask, and a `TDCargoPlane`
static ctor in `aadata.cpp` mirroring TD's `CargoPlane`. RA's 18-param
`AircraftTypeClass` ctor (vs TD's 27-param) elides build_level / cost /
strength / armor / weapons / ownable — those come from rules.ini
instead.

Heap auto-sizes via `init.cpp:229 AircraftTypes.Set_Heap(AIRCRAFT_COUNT)`
— no `MAX_AIRCRAFT_TYPES` headroom needed since we're adding a hardcoded
entry, not a rules.ini `[NewAircraft]`.

### 2. `[TDC17]` rules.ini section

`resources/remaster_mods/Vanilla_RA/CCDATA/rules.ini`. Without a rules.ini
section the cargo plane's `MaxSpeed` defaults to `MPH_IMMOBILE` (0) per
`techno.cpp:6697` and the plane spawns frozen at the map edge. `Speed=16`
maps to `MPH_FAST=40` internally via `_Scale_To_256`. Also `Strength`,
`Armor`, `TechLevel=-1` (never appears in sidebar), `Owner=allies,soviet,
GoodGuy,BadGuy`, `Cost=10`, `Points=1`, `ROT=5`, `Passengers=1`.

### 3. ImageData fallback in `AircraftTypeClass::One_Time`

`redalert/aadata.cpp`. Mod-entry aircraft have no legacy SHP for
`MFCD::Retrieve` to find — only the TGA pack in
`resources/.../UNITS/TDC17.ZIP`. With `ImageData == NULL`,
`AircraftClass::Draw_It` bails at its
`if (!shapefile) return;` guard (`aircraft.cpp:416-418`) and the
plane is invisible.

Mirror the building/unit Logic= alias pattern (`bdata.cpp:3452`,
`udata.cpp:1391`) — copy `BadgerPlane.ImageData` into `TDCargoPlane`.
The launcher's `Techno_Draw_Object` overlay then resolves the actual
sprite by IniName via `RA_UNITS.XML`'s `TDC17` tileset, regardless of
which pointer was supplied.

Also copy `CameoData` from Badger as the cargo plane isn't sidebar-
buildable but we still want a non-NULL value to satisfy any downstream
NULL guard.

### 4. `Dimensions()` branch for AIRCRAFT_TDCARGO

`redalert/aadata.cpp`. Vanilla `Dimensions()` returns `21x20` for non-
Badger aircraft — way too small for the C-17 sprite (peaks at 245x156
across facings). Map-refresh bounding rect leaves ghost trails on
screen scroll. Added a third branch: `256x160`.

### 5. Fixed-wing `Mission_Unload` state machine

`redalert/aircraft.cpp`. RA's `AircraftClass::Mission_Unload` had
`if (Class->IsFixedWing) { Assign_Target(NavCom); return Mission_Hunt(); }`
— a stub because vanilla RA has no fixed-wing transport. Ported TD's
state machine from `tiberiandawn/aircraft.cpp:1044-1180` verbatim,
gated to `AIRCRAFT_TDCARGO` so Badger/U2/Mig/Yak keep their Hunt
short-circuit:

- `PICK_AIRSTRIP`: find airstrip via `Find_Docking_Bay(STRUCT_AIRSTRIP)`,
  `RADIO_HELLO` handshake, `Assign_Destination(building->As_Target())`,
  transition to `FLY_TO_AIRSTRIP`. Fallback `MISSION_RETREAT` + random
  direction on lookup failure.
- `FLY_TO_AIRSTRIP`: per-tick set PrimaryFacing toward NavCom, scale
  `Height` down from `FLIGHT_LEVEL` via `Fixed_To_Cardinal(FLIGHT_LEVEL,
  Cardinal_To_Fixed(0x0600, navdist))` when within 0x0600 leptons. Drop
  cargo at navdist < 0x0080 via `Detach_Object` + `Unlimbo` onto
  `Contact_With_Whom()->Find_Exit_Cell(unit)`. Transition to `BUG_OUT`.
- `BUG_OUT`: `Assign_Mission(MISSION_RETREAT)`, plane heads off-map.

### 6. `Enter_Idle_Mode` in-air cargo branch

`redalert/aircraft.cpp`. TD's `Enter_Idle_Mode`
(`tiberiandawn/aircraft.cpp:1869-1876`) sets `mission = MISSION_UNLOAD`
for in-air + cargo + IsALoaner + no team — the trigger that makes a
spawned cargo plane actually enter the unload state machine. RA never
ported it; fixed-wing IsALoaner defaulted to `MISSION_GUARD`. Without
this hook the engine resets our MISSION_UNLOAD assignment on the next
AI tick and the state machine never runs.

Added the missing branch as the first check inside the in-air case of
RA's fixed-wing `Enter_Idle_Mode`:

```cpp
if (Is_Something_Attached() && IsALoaner) {
    mission = MISSION_UNLOAD;
} else if (...) { /* existing weapon-empty hunt path */ }
```

Once cargo is dropped (`Is_Something_Attached() == false`) the branch
falls through to the existing logic and the plane gets MISSION_RETREAT.

### 7. Vestigial AIRCRAFT_CARGO clause in `Edge_Of_World_AI`

`redalert/aircraft.cpp:4283`. EA's RA port left a commented-out
`/*|| (*this == AIRCRAFT_CARGO && !Is_Something_Attached())*/` clause in
the off-map despawn check. Activated with our AIRCRAFT_TDCARGO enum so
empty TDC17s exiting west after delivery despawn cleanly. Without this
the plane would loop back to hunt (and re-enter the map) instead of
retiring at the edge.

### 8. `Find_Docking_Bay` recognises TDAFLD-as-airstrip

`redalert/techno.cpp`. The standard `Find_Docking_Bay(STRUCT_AIRSTRIP)`
checks (a) `House->Get_Quantity(STRUCT_AIRSTRIP) != 0` early-out and
(b) `*building == STRUCT_AIRSTRIP` per-building match. Our TDAFLD is
Logic=WEAP-aliased so `Class->Type == STRUCT_WEAP`, missing both
checks.

Patched: (a) relaxed early-out to also pass if STRUCTF_WEAP buildings
exist; (b) added IniName fallback so any STRUCT_WEAP building whose
IniName starts with "TDAFLD" counts as airstrip; (c) skipped the
`RADIO_CAN_LOAD` probe for TDAFLD matches — WEAP's inherited
`Receive_Message` rejects it (CAN_LOAD is helipad/refinery semantics),
but `RADIO_HELLO` in PICK_AIRSTRIP works fine. Without the CAN_LOAD
bypass, Find_Docking_Bay returns NULL and PICK_AIRSTRIP falls to its
retreat path, despawning the plane immediately.

### 9. `Docking_Coord` IniName check for TDAFLD

`redalert/building.cpp`. The existing STRUCT_AIRSTRIP docking-offset
case (`Coord + (ICON_PIXEL_W + ICON_PIXEL_W/2, 28)`) misses our TDAFLD
because of Logic=WEAP aliasing. IniName fallback so the plane lands at
the visual middle-front of the 4×2 strip instead of the building's
geometric centre.

### 10. `What_Action` force-attack guard

`redalert/techno.cpp`. `IsLegalTarget=false` on `TDCargoPlane` gates
the standard target-validity check, but `What_Action`'s `Height==0`
shortcut bypasses it — a landed TDC17 on the airstrip becomes ctrl-
clickable for attack. Added explicit guard mirroring TD's
`*aircraft != AIRCRAFT_CARGO` exclusion at
`tiberiandawn/techno.cpp:2646`.

## Spawn dispatch (`BuildingClass::Exit_Object` STRUCT_WEAP case)

`redalert/building.cpp`. For TDAFLD IniName, fork before the standard
WEAP exit path:

1. `new AircraftClass(AIRCRAFT_TDCARGO, House->Class->House)`.
2. Compute spawn position: east edge X
   (`Cell_To_Lepton(MapCellX + MapCellWidth) | 0x80`), Y-aligned with
   `Docking_Coord()` so the plane flies straight at the strip.
3. `Unlimbo(spawn, DIR_W)`.
4. `IsALoaner = true` (engine despawns at map edge after delivery).
5. `Attach((FootClass*)base)` — the produced unit becomes cargo.
6. `Set_Speed(0xFF)` — full speed throughout.
7. `Assign_Mission(MISSION_UNLOAD)` + `Commence()`.
8. Return 2 (success).

**NOT done from Exit_Object**: pre-assigning NavCom, pre-establishing
radio. Both attempts (early sessions) collided with engine state
transitions — `AircraftClass::Assign_Destination`'s `Status=0` reset
(`aircraft.cpp:4636`) plus the per-tick `Enter_Idle_Mode`
reassignment, producing a 580-tick orbit before delivery. Mission_Unload's
PICK_AIRSTRIP owns the setup; let it do its job.

## Verification

End-to-end on Deck 2026-05-21 (v0.3.1-phase2d):
- Plane spawns at east edge, no orbit.
- Flies west in a straight line at constant speed.
- Altitude scales down from FLIGHT_LEVEL when within ~6 cells of dock.
- Drops vehicle at strip-adjacent cell when navdist crosses 0x0080
  (~half cell).
- Plane continues west off map, despawns cleanly at edge via the
  activated AIRCRAFT_TDCARGO branch in `Edge_Of_World_AI`.

## Diagnostic logging

`tf_tdafld_exit.log` (per Exit_Object dispatch) and
`tf_tdcargo_unload.log` (per Mission_Unload tick, rate-limited to every
5 calls) are retained per the keep-diagnostics-until-v1 feedback rule.
Both write to `%USERPROFILE%\Documents\CnCRemastered\`. Re-enable is a
one-line flip — see inline diagnostic blocks in `building.cpp` and
`aircraft.cpp`.

## Future work

- **AI doesn't build aircraft naturally** ([[project-ai-no-aircraft-builds]])
  — Nod skirmish AI never produces vehicles via TDAFLD currently because
  the AI build-list logic for aircraft is broken in our mod. Cargo-plane
  delivery is end-to-end for player production only.
- **Multi-queue stress test** — building 2+ vehicles back-to-back has
  not been exercised. Each queue completion spawns a new plane;
  concurrent planes should be fine (each is IsALoaner), but visual
  collisions / strip-cell occupancy edge cases unexplored.
- **GDI airstrip** — currently Nod-only. Future GDI airstrip would
  reuse all of the above with a different IniName match in
  Find_Docking_Bay / Docking_Coord (e.g., "TDGAFL" or generalised flag).
