# Path-failure livelock — root cause & design (2026-07-19)

**Status (2026-08-01): FIX IMPLEMENTED — no-progress detector in both give-up branches
(`FootClass::TF_Path_No_Progress`), verification in progress.** Root cause was CONFIRMED from
live logs + source 2026-07-19. One earlier fix attempt CRASHED the game and was reverted (see
"Failed attempt" below — read it before touching this code).

**The 2026-08-01 DOCKLANDS stack-overflow crash was NOT this bug.** The strong test's
`EXCEPTION_STACK_OVERFLOW` was initially pinned on the livelock's legacy-fallback retry storm;
walking the minidump disproved that (the legacy pathfinder is iterative). The real defect was
unbounded mutual recursion in the v2.2.3 give-way RETREAT: `Start_Of_Move` → gw==2 →
`Assign_Destination(back)` → nested `Start_Of_Move` (the engine re-enters it for a stationary
unit) → RETREAT again, ~1,500 frames deep in the dump. Fixed the same day with a call-stack
re-entrancy guard in `Start_Of_Move` (`giveway_retreat_depth`): while a retreat assignment is on
the stack, the nested pass skips give-way evaluation and paths straight to the retreat cell.
The livelock still FED that crash (the retry storm piles units into the jammed pinch), so the
detector below is congestion relief for it as well as the livelock cure.

## Implemented fix (2026-08-01)

Exactly the recommended shape below. `FootClass` tracks the failing (current cell, `NavCom`)
pair plus the frame it started failing (`TF_NoProgSrc/Dst/Frame`, reset on any successful path,
any movement, or any new destination — savegame-breaking growth, accepted):

- **Infantry** (`infantry.cpp` give-up branch, entered every post-exhaustion failure): after
  **8 s** of zero progress on the same pair, abort `NavCom` regardless of zone; also drop a
  `TarCom` we cannot reach AND cannot already shoot (`!In_Range`). A target in range is kept —
  movement is not needed to be useful.
- **Vehicles** (`drive.cpp` give-up branch): the patient queue keeps priority, but after
  **60 s** at the SAME cell pursuing the SAME destination the "queued behind traffic" reading is
  falsified and the engine's own abandon branch runs (scan-limit handling included). A genuinely
  queued column advances a cell now and then, restarting the window, as does a deadlock-breaker
  scatter.
- Both aborts are **caller-side** — never from inside `Basic_Path()` (see the failed attempt).
- `TF_DEV_BUILD` diag: `NOPROG abort (inf|veh): unit=... src=... dst=... stuck=...f` in
  `tf_astar.log`.

Open-question answers: N is a frame window, not a retry count (cadence-independent); the patient
queue is distinguished from permanent boxing by *zero cell movement for a full minute*; scope is
both infantry and vehicles; a tripped unit goes idle and its mission/team logic re-tasks it
(the AI hunt path already had its own abort).

## Live finding (2026-08-01 verification run): pair-keying is blind to TARGET ROTATION

First fixed-build DOCKLANDS run (4 AIs vs isolated human): recursion guard HELD far past the
crash point, but `NOPROG abort` fired **zero** times against a 200k+ fallback storm. The live
tuple stream shows why — the dominant livelock is not one frozen (src,dst) pair but a
**rotation**: a wedged 3TNK cycles dst=(121,37) → (113,91) → (112,58) every 4-8 attempts (hunt
logic re-picks among unreachable targets, each re-pick resets the pair window). Even the
self-cell TDE6 runs are interleaved (runs of ~5). The design doc's "598x same tuple" figures
were per-match TOTALS, not consecutive runs — the pair-keyed window can essentially never trip
on AI units. (It may still catch human-ordered units, which don't rotate targets.)

**Iteration 2 (shipped same day):** key on the SOURCE CELL only — a unit accumulating
Basic_Path failures from the same cell for a sustained window is stuck regardless of which
doomed destination the mission logic is currently offering. On trip: abort destination AND
apply the engine's own scan-limit throttle (`IsScanLimited` / `Team->Scan_Limit()`).

## FINAL VERDICT (2026-08-01, live Luke-played Docklands match) — workstream CLOSED

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
  ever-cleverer surrender. Luke's call, 2026-08-01: park this until the AI can use naval.
  The storm's costs after the crash fix are CPU + dev-log volume only.

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

## Recommended shape of the fix (implemented 2026-08-01 as described — see top of doc)

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
