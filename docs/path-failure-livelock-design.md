# Path-failure livelock

**Status:** Reference; closed in 5.0.0.

A unit that keeps failing to path from the same cell gives up: infantry after 8 s, vehicles after
a minute, both handled by the caller (`FootClass::TF_Path_No_Progress`). A re-entrancy guard on
the give-way retreat (`giveway_retreat_depth` in `DriveClass::Start_Of_Move`) ended the Docklands
stack overflow. Units with no ground route still produce a retry storm; not measured since the
ferry shipped. Read "Failed attempt" below before touching this code.

## The shipped fix

**The no-progress detector, keyed on the source cell.** `FootClass` keeps the cell a unit has been
failing from and when that started (`TF_NoProgSrc`, `TF_NoProgStart`, `TF_NoProgLast`).
`TF_Path_No_Progress(window)` is called once per `Basic_Path` failure and returns true once
failures from the same cell have run for `window` frames with no gap over 5 s. Any movement or a
successful path starts a fresh window, so a queued column that advances one cell never trips.

- **Why the source cell and not the (source, destination) pair:** a stuck AI unit's destination
  rotates (hunt logic re-picks among unreachable targets every few attempts), so a pair-keyed
  window never accumulated; the first version fired zero times against a 200k-fallback storm.
- **Infantry** (`infantry.cpp` give-up branch, 8 s): abort `NavCom` regardless of zone and drop a
  `TarCom` it can neither reach nor already shoot; an AI hunter is also scan-limited
  (`IsScanLimited`), so its next pick is an in-range target.
- **Vehicles** (`drive.cpp` give-up branch, 60 s): the patient queue keeps priority, but a unit
  still at the same cell after a minute runs the engine's own abandon branch.
- Both aborts are **caller-side**, never from inside `Basic_Path()` (see the failed attempt).
- `TF_DEV_BUILD` diag: `NOPROG abort (inf|veh)` lines in `tf_astar.log`.

**The Docklands stack overflow was a different bug.** Its `EXCEPTION_STACK_OVERFLOW` was unbounded
recursion in the give-way RETREAT: `Start_Of_Move` → gw==2 → `Assign_Destination(back)` → nested
`Start_Of_Move` → RETREAT again, ~1,500 frames deep. While a retreat assignment is on the stack,
the nested pass now skips give-way and paths straight to the retreat cell. The livelock fed it by
piling units into the jammed pinch.

## Verdict (live Docklands match, 2026-08-01)

- **The crash is fixed and verified** (the recursion guard; F51,760 and F40,300+ matches, no
  artifacts, under storms up to 427k fallbacks).
- **The in-base wedge livelock — the bug this doc was opened for — is cured**: short-range
  wedges (`TDLTNK (60,79)→(61,78)`, the v1 batch of 743 base-traffic aborts) now abort and
  re-task instead of retrying forever.
- **The unreachable-target storm is NOT collapsible by give-up logic, and we stop trying.**
  v2 + scan-limit measured 8.96 fallbacks/frame against the 8.4 baseline: `IsScanLimited`
  self-lifts by design, hunt re-picks immediately, and a cliff-parked unit re-trips its
  already-expired window every few frames (same unit logged `stuck=9796f` and climbing).
  The units mass on the shore because they genuinely have no ground route to the enemy —
  the correct cure is GIVING THEM A ROUTE (naval transports, `ai-upgrade-plan.md`), not
  ever-cleverer surrender. Parked until the AI can use naval transports (shipped in 5.0.0;
  the storm has not been re-measured since).
  The storm's costs after the crash fix are CPU + dev-log volume only.

Sibling doc: `harvester-recovery-design.md`. Same underlying engine truth (movement zones
ignore buildings), same recommended shape of cure (a no-progress detector, not a zone fix).

## Porting TS's pathfinder: no (coach-day dive, 2026-09-11)

TS's hierarchical A* (`reference/OpenTS`) would not fix what is left. Ours already has the heap
and the 4096-node cap, which never tripped live. TS's zones also ignore ordinary
buildings (only walls, the Firestorm and laser fences block them), so a walled destination stays
invisible to it too. A headless AI-vs-AI Docklands run counted 27,861 real-destination fallbacks,
the Titans, Wolverines and Disruptors of the unreachable-target storm above, and 1,352 self-cell
(`src==dst`) searches from the Amphibious APC (TSAPC). The APC's self-cell searches are the
cheap targeted fix still open.

---

## The bug

A unit that cannot path to its destination retries the identical failing request forever. It
never moves, never gives up, and never becomes available for other work. Measured on a live
desktop skirmish, single match:

```
598x  TDE1  src=(40,40) dst=(35,33)
313x  TDE2  src=(24,78) dst=(23,76)
261x  TDE2  src=(41,40) dst=(41,37)
260x  TDE6  src=(28,77) dst=(28,77)     <- destination == own cell
252x  TDE6  src=(39,35) dst=(39,35)     <- destination == own cell
```

Totals that match: `self-cell=790  real=2833` of ~3600 fallbacks. Reproduced independently on
the Deck on a different map. Present in pre-A*-heap logs too (1452 `E6` self-cell cases), so
this long predates the pathfinding work and is not a regression from it.

Retry cadence is `PathDelay` = `0.016 * 900` ≈ 14 ticks, so roughly 4 attempts/second/unit.

---

## Root cause (one condition explains every observed case)

`infantry.cpp:4346`, in the give-up branch reached once `TryTryAgain` is exhausted:

```cpp
/*
**	Abort the target and destination process since the path could not be found.
**	In such a case, processing should stop or else the game will bog down with
**	repeated path failures.
**	Only perform the abort of the target is in a different zone.
*/
if ((!IsZoneCheat || Can_Enter_Cell(Coord_Cell(Coord)) != MOVE_NO) && IsLocked
    && Target_Legal(NavCom)
    && Map[As_Cell(NavCom)].Zones[Class->MZone] != Map[Coord].Zones[Class->MZone]) {
    Assign_Destination(TARGET_NONE);
}
```

**The abort is gated on a zone MISMATCH.** A same-zone destination never clears `NavCom`, so
the unit re-enters the pathfinder with the identical request indefinitely. The original
authors anticipated the failure mode in the comment, then gated the cure too narrowly.

Why that gate is wrong in practice:

- **Movement zones ignore buildings by design** (established in `harvester-recovery-design.md`).
  A destination walled off by structures is therefore "same zone" but genuinely unreachable —
  permanent livelock. This is the walled-field problem wearing different clothes.
- **A cell is always in its own zone**, so a destination equal to the unit's own cell can
  *never* satisfy the mismatch test. Self-cell livelock is guaranteed by construction, not bad
  luck. It is a subtype of the general bug, not a separate one.

Vehicles have the same disease in a different spot — `drive.cpp:2180`:

```cpp
if (traffic_blocked) {
    TryTryAgain = PATH_RETRY;   // resets patience to 10, every time
```

`traffic_blocked` is true if **any** of 8 neighbours holds a stopped friendly, oncoming ally,
or an active choke claim. Inside a busy base that is ~always true, so patience resets forever
and the give-up branch below it (which *does* correctly call `Assign_Destination(TARGET_NONE)`)
is never reached.

### Where clearing the destination is legitimate

`drive.cpp:2192` — the engine's own give-up path — calls `Assign_Destination(TARGET_NONE)`
from the **caller**, after `Basic_Path()` has returned. That is the safe context. See below
for why this matters more than it looks.

---

## ❌ Failed attempt — CRASHED BOTH MACHINES (read before coding)

Two changes were made inside `FootClass::Basic_Path()`:

1. reject the object's own cell as a `Map.Nearby_Location()` substitute; and
2. on a destination equal to the current cell: `Stop_Driver(); Assign_Destination(TARGET_NONE); return false;`

Result: `self-cell` went to **0** (part 2 worked, mechanically), and the game crashed on the
desktop and the Deck within minutes. Reverted; both surfaces returned to the prior build.

**Why it crashed.** `Assign_Destination()` is **virtual**, and the derived overrides do far
more than assign a field:

```cpp
// UnitClass::Assign_Destination
if (In_Radio_Contact() && ...) Transmit_Message(RADIO_OVER_OUT);
if (Transmit_Message(RADIO_DOCKING, b) != RADIO_ROGER) Transmit_Message(RADIO_OVER_OUT);
// DriveClass::Assign_Destination
if (Transmit_Message(RADIO_HELLO, b) == RADIO_ROGER) { ... Assign_Mission(MISSION_ENTER); }
```

They run radio-contact protocols and reassign missions, and they assume an **order-issuing**
context. Called from inside the pathfinder, a unit can tear down a radio link (e.g. a
harvester's dock contact) or change its own mission while the movement code that invoked the
pathfind is still executing against the pre-call state.

**Rule for any fix: never call `Assign_Destination()` from inside `Basic_Path()`. Clear the
destination caller-side, where the engine already does it.**

### ❌ Also falsified: the `Nearby_Location` guard alone

Part 1 was shipped on its own afterwards, on the theory that it was the safe half doing the
real work. It is **not**: `self-cell` came back at **790** (vs 706 before). The degenerate
destination does not originate from `Nearby_Location`. Guard reverted; do not re-try it.

---

## Measurement recipe

`tf_astar.log`, isolating the current match by its session marker:

```bash
S=$(grep -an 'A\* log session start' tf_astar.log | tail -1 | cut -d: -f1)
# self-cell vs genuine failures
tail -n +$S tf_astar.log | grep -a 'A\* FALLBACK' | awk '{for(j=1;j<=NF;j++){if($j~/^src=/)s=$j;if($j~/^dst=/)d=$j}
  gsub("src=","",s); gsub("dst=","",d); if(s==d)a++; else b++} END{print "self-cell="a+0"  real="b+0}'
# livelock signature: the same (unit, src, dst) repeating
tail -n +$S tf_astar.log | grep -a 'A\* FALLBACK' \
  | grep -oE 'unit=[A-Z0-9]+ src=\([0-9,]+\) dst=\([0-9,]+\)' | sort | uniq -c | sort -rn | head
```

⚠️ **Sample a FULL match.** Early-match samples are not representative and point the opposite
way: at one point self-cell read as ~85% of all fallbacks, but over a whole match it plateaus
while genuine failures keep climbing. A share figure quoted from an early sample is wrong.

**Success signal for a fix:** the repeated-`(unit,src,dst)` counts collapse to single digits,
while total `real` failures stay near their baseline (~2800-3200/match desktop, ~1500 Deck).
