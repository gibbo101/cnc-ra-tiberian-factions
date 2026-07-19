# Path-failure livelock — root cause & design (2026-07-19)

**Status:** root cause CONFIRMED from live logs + source. No fix written. One fix attempt
CRASHED the game and was reverted (see "Failed attempt" below — read it before coding).

Sibling doc: `harvester-recovery-design.md`. Same underlying engine truth (movement zones
ignore buildings), same recommended shape of cure (a no-progress detector, not a zone fix).

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

## Recommended shape of the fix (NOT yet implemented — needs review)

**A no-progress detector, not a zone test.** If a unit fails to path from the same cell to the
same destination N consecutive times, abort the destination regardless of zone.

Rationale:
- It targets the actual invariant that is broken (no progress), rather than a proxy (zone
  identity) that is known to be wrong because zones ignore buildings.
- It is the same pattern already shipped and proven in `harvester-recovery-design.md`, where
  the zone-recompute "proper fix" was explicitly rejected for the same reason.
- It cannot be fooled by the self-cell case, which no zone comparison can ever catch.

Sketch (caller-side, both `infantry.cpp` and `drive.cpp` give-up paths):
- track last-failed `(src, dst)` and a consecutive-failure count on the unit;
- on N consecutive identical failures, `Assign_Destination(TARGET_NONE)` in the caller;
- reset the counter on any successful path or any new destination.

### Open questions to settle BEFORE writing code

1. **What is N?** Too low and units abandon orders that were merely delayed by traffic that
   would have cleared — the exact regression the v2.2.3 patient-queue work exists to prevent
   (`drive.cpp:2180`). Too high and the livelock persists. `TryTryAgain` is already 10.
2. **Does this conflict with the patient queue?** That logic deliberately waits forever at a
   pinch. A no-progress detector must distinguish "queued behind traffic that will clear" from
   "boxed in permanently" — the patient queue currently assumes the former always.
3. **Scope: infantry only, or vehicles too?** The measured livelocks are all infantry
   (`TDE1`/`TDE2`/`TDE6`), but `drive.cpp:2180` has the same defect. Fixing only what is
   measured is defensible for a first pass.
4. **What should a unit that gives up actually do?** Clearing `NavCom` leaves it idle. For an
   AI engineer mid-capture that may be worse than useless — it should probably re-task. Out of
   scope for the livelock fix itself, but it decides whether this is a win in AI terms.

### Risk

`FootClass` / `DriveClass` / `InfantryClass` movement is used by **every ground unit, human and
AI**. Today's crash came from a four-line change in this area. Any fix here wants a design
review, a single-surface deploy (desktop first, never both at once), and a full match before it
is trusted.

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
