# Harvester unreachable-ore recovery

**Status:** Reference; shipped in 2.4.0, extended by the 3.0.0 watchdog; a switch since 5.7.0
(`player-settings.md`, Harvesters).

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

1. **Zones can't see a building-walled field.** Zones ignore buildings by design, and building placement never
   calls `Zone_Reset` (the field manual's
   [Movement zones, and what they ignore](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/pathfinding.md#movement-zones-and-what-they-ignore)).
   In TF's tree `Zone_Reset` runs for walls (`overlay.cpp:179` placing, `cell.cpp` and `house.cpp` destroying, and the
   component tower's joint walls in `building.cpp`), terrain (`terrain.cpp`), bridges (`map.cpp`, `infantry.cpp`)
   and scenario load (`scenario.cpp`), never for an ordinary building. So every zone-based reachability check reads
   the walled field as reachable: `Tiberium_Check`'s zone filter, `Is_In_Same_Zone` (`techno.cpp`) and
   `Find_Path_AStar`'s zone gate (`findpath.cpp`).
2. **The legacy pathfinder always "succeeds."** When A* fails (it correctly refuses the blocked cell),
   `FootClass::Find_Path` falls back to the edge-follower, which returns *some* path toward the wall that never
   arrives (the field manual's
   [The stock pathfinder](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/pathfinding.md#the-stock-pathfinder-edge-following-no-a)).
   So `Basic_Path` rarely returns "no path", the drive no-path/ABANDON branch rarely fires, and **any fix hooked to a
   failure EVENT can't see the stuck state**; only the *symptom*, "not getting closer to the ore", is reliable.
   Three event-hooked detectors missed it: LOOKING-only, NavCom-goes-clear and no-path-branch.

## ❌ Dead route: calling `Zone_Reset` on building placement
It doesn't help, because the flood walks straight through building footprints (the field manual's
[Harvesters](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/harvesters.md#traps), Traps).
The mechanism in TF's tree:

- `Zone_Reset` → `Zone_Span` (`map.cpp`) tests each cell with
  `Is_Clear_To_Move(SPEED_TRACK, ignoreinfantry=true, ignorevehicles=true, -1, check)`, and `ignorevehicles` runs
  `composite &= 0x5F` in `CellClass::Is_Clear_To_Move` (`cell.cpp`, "Drop the vehicle/building bit"). The building
  occupy bit is `0x80` (`cell.h`, little-endian), and a footprint cell keeps its land type, so `Ground[land].Cost` is non-zero and
  the cell reads **clear**.
- Walls do divide zones because they're *overlay*, tested separately through `overlay->IsWall`, not through the
  occupy bits.
- **The bib is not the reason:** a building's bib is a separate passable `SmudgeClass` apron on cells *outside* the
  `Occupy_List` and sets no occupy bits; the footprint cells themselves are blocked (`Occupy_Down` sets
  `Flag.Occupy.Building`). The `0x5F` mask alone is why buildings don't divide zones.
- **Why the design does this:** zones are a *coarse* terrain-and-wall connectivity map; buildings are dynamic
  obstacles that A* routes round cell by cell, or every structure would shatter the map into tiny zones needing a
  rebuild on every build or sell. **A* respects buildings, zones don't.**

Making the zone fix work would mean a `Zone_Span`-only variant of `Is_Clear_To_Move` that keeps `0x80`, which
changes the meaning of `Zones[]` for **every** consumer (AI target selection, the A* zone gate, `Is_In_Same_Zone`,
base placement): a determinism-sensitive, regression-prone change needing a full playtest cycle, too big for the
payoff against the symptom patch that ships.

## Diagnostic instrument
`tf_astar.log` (TF_DEV_BUILD): `HARV-BLACKLIST` (harvester recovery), `CHOKE: ... mission=N
status=M` (drive no-path branch, now with mission/status), `A* FALLBACK` tally. An idle harvester that
has stopped pathing emits nothing — the no-progress detector in `UnitClass::AI` is the instrument that
sees it.
