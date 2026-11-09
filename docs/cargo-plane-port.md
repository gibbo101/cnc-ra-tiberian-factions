# Cargo-plane delivery (TDAFLD / TDC17)

**Status:** Reference; shipped in 1.0.0. The Nod Airstrip's cargo-plane delivery (TDAFLD, TDC17).

A vehicle built at the Nod Airstrip (`STRUCT_TDAFLD`) isn't driven out: a TDC17 cargo plane flies in from the east
edge with it, sets it down beside the strip, and leaves west. TD's source is the spec: `tiberiandawn/reinf.cpp`'s
`Do_Reinforcements` `SOURCE_AIR` path and `tiberiandawn/aircraft.cpp`'s fixed-wing `Mission_Unload`.

What RA lacks and the steps a port needs are in the field manual's
[Air delivery, fleets and support powers](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/behaviours/air-delivery-and-fleets.md#cargo-plane-delivery),
Cargo-plane delivery and Traps. This doc is TF's implementation of each. Back-to-back deliveries need three more
fixes, in `td-port-playbook.md` §3.19.

---

## The spawn (`BuildingClass::Exit_Object`, `redalert/building.cpp:3547`)

`case STRUCT_TDAFLD:` calls TD's `Create_Special_Reinforcement(House, TDCARGO, ttype, TMISSION_UNLOAD,
As_Target())` and deletes the factory's vehicle, since the reinforcement spawns its own copy. In
`Do_Reinforcements` (`reinf.cpp:468`) the cargo plane enters at the east edge
(`Cell_To_Lepton(MapCellX + MapCellWidth) | 0x80`), level with its strip's `Docking_Coord()`, facing west, and the
team's first mission points at the strip. With every strip busy (`Find_Docking_Bay` returns NULL) it takes any
TDAFLD or airstrip the house owns from `Buildings`, so later planes still fly in convoy.

Don't set the plane's `NavCom` or radio contact before `Mission_Unload`'s `PICK_AIRSTRIP` runs:
`AircraftClass::Assign_Destination` resets `Status` to 0 (`aircraft.cpp:5179`) and `Enter_Idle_Mode` reassigns the
mission every tick, and together they flew the plane in a 580-tick orbit before it delivered. `PICK_AIRSTRIP` owns
that set-up.

## What TF adds

### 1. The `AIRCRAFT_TDCARGO` type

`redalert/defines.h` and `aadata.cpp:211`: `AIRCRAFT_TDCARGO` in the enum after `AIRCRAFT_HIND`, with an
`AIRCRAFTF_TDCARGO` bit, and a `TDCargoPlane` constructor from TD's `CargoPlane`. RA's `AircraftTypeClass`
constructor takes 19 arguments to TD's 36; build level, cost, strength, armour, weapons and owners come from
`rules.ini` instead. The heap grows with the enum (the field manual's
[Raising the limits](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/raising-the-limits.md#the-limits)).

### 2. `[TDC17]` in `rules.ini`

Without it the plane sits frozen at the edge: `TechnoTypeClass`'s constructor defaults `MaxSpeed` to
`MPH_IMMOBILE`. `Speed=16` (`MPH_FAST`, 40), `Strength=25`, `Armor=light`, `TechLevel=-1` (never in the sidebar),
`Owner=allies,soviet,GoodGuy,BadGuy`, `Cost=10`, `Points=1`, `ROT=5`, `Passengers=1`.

### 3. A donor image

`AircraftTypeClass::One_Time` (`aadata.cpp:656`) copies the Badger's `ImageData` and `CameoData` to TDC17, past
`AircraftClass::Draw_It`'s `if (!shapefile)` return. The plane isn't buildable, so the cameo only keeps the
pointer non-NULL. The art is `TDC17.ZIP`.

### 4. Its own box (`Dimensions`, `aadata.cpp:904`)

`256x160`, for art that peaks at 245x156 across its facings.

### 5. The landing run (`Mission_Unload`, `aircraft.cpp:1251`)

TD's fixed-wing state machine (`tiberiandawn/aircraft.cpp:1044-1180`), gated to `AIRCRAFT_TDCARGO`, so the Badger,
U2, MiG and Yak keep RA's hunt:

- **`PICK_AIRSTRIP`:** the strip from `NavCom`, else `Find_Docking_Bay(STRUCT_TDAFLD)`, else any TDAFLD or airstrip
  the house owns; fly at it at full speed, facing it, and retry `RADIO_HELLO` each tick until it answers, then
  `FLY_TO_AIRSTRIP`. Straight in, never circling (playbook §3.19). With no strip at all, `MISSION_RETREAT`.
- **`FLY_TO_AIRSTRIP`:** face `NavCom` each tick, and within `0x0600` leptons bring `Height` down from
  `FLIGHT_LEVEL` (`Fixed_To_Cardinal(FLIGHT_LEVEL, Cardinal_To_Fixed(0x0600, navdist))`). At `navdist < 0x0200`
  (`aircraft.cpp:1322`) set the vehicle down: `Detach_Object`, then `Unlimbo` at
  `Contact_With_Whom()->Find_Exit_Cell(unit)`. TD's `0x0080` is too tight at about 8 leptons a tick. The vehicle
  never passes the factory's `RADIO_UNLOADED` exit hook, so the strip's rally point is applied here, with a
  scatter if that fails. Then `BUG_OUT`.
- **`BUG_OUT`:** `MISSION_RETREAT`, off the map.

### 6. The idle branch

TD's `Enter_Idle_Mode` (`tiberiandawn/aircraft.cpp:1869-1876`) starts the unload; without the branch the engine
replaces `MISSION_UNLOAD` on the next tick. TF's is the first test in the in-air case of RA's fixed-wing
`Enter_Idle_Mode`:

```cpp
if (Is_Something_Attached() && IsALoaner) {
    mission = MISSION_UNLOAD;
} else if (...) { /* existing weapon-empty hunt path */ }
```

Once the cargo is down the branch falls through, and the plane gets `MISSION_RETREAT`.

### 7. Leaving the map (`Edge_Of_World_AI`, `aircraft.cpp:5007`)

The commented-out cargo clause, restored for `AIRCRAFT_TDCARGO`: an empty TDC17 leaving the map is deleted instead
of looping back to hunt.

### 8. `Find_Docking_Bay` (`redalert/techno.cpp`)

A request for RA's airstrip counts every faction's (`STRUCT_AIRSTRIP`, `STRUCT_TDAFLD`, `STRUCT_TDGAFLD`), in both
the early-out count and the per-building match, so `PICK_AIRSTRIP` finds the TD strip.

### 9. `Docking_Coord` (`redalert/building.cpp`)

`STRUCT_TDAFLD` has its own docking offset, so the plane lands at the visual middle-front of the 4x2 strip, not its
geometric centre.

### 10. Never a target (`What_Action`, `techno.cpp:4405`)

The cargo plane is never a target, even for a force-attack while landed, as TD leaves out its cargo plane
(`*aircraft != AIRCRAFT_CARGO`, `tiberiandawn/techno.cpp:2646`).

## Checks after a change

1. The plane enters at the east edge and flies west in a straight line at constant speed, with no orbit.
2. It descends from `FLIGHT_LEVEL` within about six cells of the dock.
3. The vehicle is set down beside the strip as `navdist` crosses `0x0200`, and heads for the rally point.
4. The plane carries on west and is deleted at the edge.
5. Two vehicles queued back to back arrive one plane after the other (playbook §3.19).

## Scope

Cargo-plane delivery is Nod's alone. GDI's airfield (`TDGAFLD`) builds the A-10 (`naval-and-air-units.md`);
another delivery airstrip would reuse all of the above with its own type in `Find_Docking_Bay` and `Docking_Coord`.
