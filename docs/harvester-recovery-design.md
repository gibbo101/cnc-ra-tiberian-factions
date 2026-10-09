# Harvester unreachable-ore recovery

**Status:** Reference; shipped in 2.4.0, extended by the 3.0.0 watchdog.

A harvester that stops closing on its ore for 5 s blacklists the whole contiguous field and pulls
back toward its refinery to rescan. Movement zones ignore buildings by design, so a zone-based check
cannot see a walled field, and adding `Zone_Reset` to building placement does not fix it (below).
Docking is `harvester-docking-rework-plan.md`.

## What ships

- **The no-progress detector** (`UnitClass::AI`): while a harvester pursues an ore `NavCom` it
  tracks the closest distance reached (`HarvBestDist`, 1-cell margin). No improvement for
  `HARV_STALL_FRAMES` (5 s), after up to `HARV_MAX_REACHABLE_RESETS` (3) free windows while A* still
  finds a path, blacklists the target. It is pathfinder-agnostic, so it also catches a same-zone
  cell blocked by a parked unit.
- **Field blacklist** (`Blacklist_Harvest_Cell`, `Is_Harvest_Blacklisted`): an 8-connected flood
  fill of `LAND_TIBERIUM` from the failed cell (capped at `HARV_FLOOD_CAP` = 256) stores the field's
  bounding box (`HarvBadMin` / `HarvBadMax`, `HARV_BLACKLIST_MAX` = 4 slots, 1-cell margin), so the
  harvester can't give up on one cell and re-pick another of the same dead field.
  `Goto_Tiberium` skips blacklisted cells; a slot expires after `HARV_BLACKLIST_TTL` (15 s).
- **Retreat:** in `Mission_Harvest` LOOKING, a harvester more than 4 cells from its refinery heads
  for `Nearby_Location(Find_Best_Refinery())` and rescans from there; near base it waits and
  rescans. It stays in `MISSION_HARVEST`, for humans and AI alike.
- **The `ArchiveTarget` zone gate** (`Mission_Harvest`): a harvester returns to its last-mined
  field only if that field is in its own zone. A walled-off last field stays a legal target but
  unreachable: A* fails, which clears `NavCom`, the rescan finds nothing, and without the gate the
  cycle repeats forever.
- **The anti-stuck watchdog** (3.0.0, `UnitClass::AI`): a harvester that stops moving shoves
  blocking infantry after 3 s, scatters itself after 6 s, and re-decides after 12 s. It never
  blacklists: it can't tell an unreachable field from a wedged harvester, so field blacklisting
  belongs to the detector alone.
  Its nudge direction uses `Path[0]` first: the straight-line bearing can round to the wrong eighth
  and miss a blocker just off-axis.
- **The field pick** (`Goto_Tiberium`, pathcost mode): the candidates are each ring's nearest ore
  cell, chosen by distance, not density (picking the densest gave every slot to distant untouched
  fields). Reachability uses `MOVE_MOVING_BLOCK`, so units parked on the route don't count as walls.
  The threat penalty enters only the nearest-distance comparison, never the reachability gate
  (`plen`) or the richness sum; defensive buildings count as threats on purpose. With nothing
  reachable it falls back to the straight-line nearest candidate.

## The bug
A harvester ordered/heading to an ore patch that has been **walled off by a BUILDING** (a turret,
or the AI fencing its own gems) gets stuck forever: it never reaches the ore, burns A* fallbacks,
and its economy is dead. Reproduced reliably by building a turret across the only approach to an
ore patch while a harvester is en route.

## Two root causes

1. **Building placement does NOT recompute movement zones.** `MapClass::Zone_Reset` (map.cpp:1801)
   is the full-map flood-fill that rebuilds `CellClass::Zones[MZONE_*]` (the connected-region map all
   reachability checks use). Its callers are: **walls** (overlay.cpp:179 place, cell.cpp:1938 +
   house.cpp:5017 destroy), **terrain/trees** (terrain.cpp:577), **bridges** (map.cpp:2227/2311/2374),
   and **scenario load** (scenario.cpp:725/860). **Ordinary buildings are NOT in that list.** So when
   you wall an ore patch with a turret, the zone map is never updated — those ore cells keep their old
   "connected" zone id. Every zone-based reachability check therefore reads STALE data and believes the
   patch is reachable: `Tiberium_Check`'s zone filter (unit.cpp:2519), `Is_In_Same_Zone`
   (techno.cpp:5781), `Find_Path_AStar`'s zone gate (findpath.cpp:533). **This is the core bug.**

2. **The legacy pathfinder always "succeeds."** When A* fails (it correctly refuses the blocked
   cell), `FootClass::Find_Path` falls back to the legacy crash-and-turn edge-follower, which returns
   *some* wandering path that heads toward the wall and never arrives. So `Basic_Path` rarely returns
   "no path", the drive no-path/ABANDON branch rarely fires, and **any fix hooked to a failure EVENT
   can't see the stuck state.** Only the *symptom* — "not getting closer to the ore" — is reliable.
   (Three event-hooked detectors missed for this reason: LOOKING-only, NavCom-goes-clear and
   no-path-branch.)

## ❌ Dead route: calling `Zone_Reset` on building placement
The whole "make buildings call `Zone_Reset` → every zone check just works" plan rested on an
assumption that turned out to be **false**: that the zone flood-fill counts building cells as
impassable. **It does not — by deliberate design.**

- `Zone_Reset` → `Zone_Span` (map.cpp:1895) tests each cell with
  `Is_Clear_To_Move(SPEED_TRACK, ignoreinfantry=true, **ignorevehicles=true**, -1, check)`
  (map.cpp:1917).
- In `Is_Clear_To_Move` (cell.cpp:3091), `ignorevehicles` runs `composite &= 0x5F` — and the
  original devs commented it **"Drop the vehicle/building bit."** The **Building** occupy bit is
  `0x80` (cell.h:228, little-endian); `0x5F` clears it. A building footprint cell also keeps its
  normal land type, so `Ground[land].Cost` is non-zero → the cell reads **clear**.
- Net: **the zone flood walks straight through building footprints.** Even if buildings called
  `Zone_Reset` on every place/sell, a building-walled ore patch stays in the **same zone** — zones
  never disconnect it. (Walls work because they're *overlay*, checked separately at cell.cpp:3145
  via `overlay->IsWall`, not via the occupy bits.)
- **Why the original design does this:** zones are a *coarse* terrain+wall connectivity map. Buildings
  are meant to be dynamic obstacles that fine-grained A* routes around at the cell level, so they're
  intentionally not zone-dividers (else every structure would shatter the map into tiny zones needing
  a rebuild on every build/sell). The harvester bug is exactly this mismatch: **A* respects buildings,
  zones don't.**
- **The bib is not the reason:** a building's bib is a separate passable `SmudgeClass`
  apron on cells *outside* the `Occupy_List`; it sets no occupy bits. The footprint cells themselves
  are fully blocked (`Occupy_Down` sets `Flag.Occupy.Building`, cell.cpp:650). Buildings are ignored
  in zones because of the `0x5F` mask, full stop.

**Consequence:** making the zone fix actually work would *also* require making the flood honor the
Building bit (a `Zone_Span`-only variant of `Is_Clear_To_Move` that keeps `0x80`). That changes the
global meaning of `Zones[]` and touches **every** consumer — AI target selection, the A* zone gate,
`Is_In_Same_Zone`, base placement — i.e. an MP-determinism-sensitive, regression-prone change needing
a full playtest cycle. **Too big for the payoff vs. the proven symptom-patch.**

## Diagnostic instrument
`tf_astar.log` (TF_DEV_BUILD): `HARV-BLACKLIST` (harvester recovery), `CHOKE: ... mission=N
status=M` (drive no-path branch, now with mission/status), `A* FALLBACK` tally. An idle harvester that
has stopped pathing emits nothing — the no-progress detector in `UnitClass::AI` is the instrument that
sees it.
