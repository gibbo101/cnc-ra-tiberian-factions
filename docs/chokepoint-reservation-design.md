# Chokepoint give-way + reservation — design & checkpoint (2026-06-15)

---

## ⭐ CHECKPOINT 2026-06-16 — READ THIS FIRST (supersedes everything below)

Big session. The reservation deployed on 2026-06-15 turned out to be a **net regression** in a fresh
AI stress test, was root-caused, fixed, and the fix **committed**. A second cooperative fix was added,
and the remaining gap was pinned down precisely. Diagnosis method all session: live AI skirmish +
10s `tf_astar.log` polling + Luke's screenshots (correlate cell coords ↔ on-screen units).

### What shipped to the repo — COMMITTED `6f35ea9` (local only, NO release/push)
1. **Claim-on-crossing fix** (`drive.cpp`/`drive.h`, `mutable CELL LastClaimCell`). **Root cause of the
   regression:** a stalled unit re-stamped its `ChokeClaim` *every tick* in `Give_Way_Decision`, so the
   TTL never expired — one stuck unit held the lane forever and the queue behind it locked up; with the
   AI stress-testing a pinch this cascaded into progressive **whole-map gridlock** (frozen-lead count
   grew 3→7→9, nothing clearing). Fix: only (re)stamp the claim when the unit has actually crossed into
   a new cell (`here != LastClaimCell`), so a halted unit's claim ages out. **Validated**: no frozen
   leads, one-off fallbacks, no 2-minute collapse — across a full ~30k-line late-game match.
2. **Deadlock-breaker scatter** (`drive.cpp`/`drive.h`, `unsigned short StuckFrames`). In
   `Start_Of_Move`'s no-path patient branch: after `STUCK_SCATTER_TRIES=8` straight blocked retry
   cycles, force-scatter into an id-seeded free neighbour (`Assign_Destination(escape)` +
   `Queue_Navigation_List(original)`), reset on cell-advance. Lockstep-safe (no RNG, per-unit int).
   Logs `SCATTER-deadlock`. Confirmed firing + doesn't over-fire — but see the GAP below.
3. (Also in the commit: the `findpath.cpp` A* wait-on-claim — part of the validated working set; it is
   self-releasing now that claims age out.)

### Uncommitted in the tree on top of `6f35ea9` (built + deployed + soak-tested healthy)
- **Infantry-shove** inside the breaker: a stuck vehicle force-`Scatter`s a friendly **idle infantry**
  parked on its path-ahead (give-way is `DriveClass`-only, so infantry never yield on their own — the
  man-blocks-harvester / `APC`-blocked-by-`E1` cases). `Scatter(threat,true,true)` is deterministic and
  only moves genuinely idle infantry. Ran in tonight's healthy test but not *specifically* observed
  firing — validate next session.
- The 2 dev TEST TOGGLES were reverted for the clean commit, then **re-applied** (Luke: "put the toggles
  back") for continued AI testing: AI-logging (`House->IsHuman`→`House`, drive.cpp×7 + unit.cpp×1) and
  AI insta-build (techno.cpp dropped `hptr->IsHuman`). **Revert before the next commit.**

### ⭐ THE KEY NEXT-SESSION FIX (most actionable thing found) — breaker is in the WRONG BRANCH
The deadlock-breaker lives in `Start_Of_Move`'s **no-path** branch (`Basic_Path` *failed*). But the
commonest deadlock — two units nose-to-nose — usually has a **valid path**: `Basic_Path` succeeds and
the unit blocks at **execution**, hitting the vanilla head-on `MOVE_NO` (`unit.cpp:3699`) at
`drive.cpp ~1882` (`cando != MOVE_OK`), stopping/retrying without ever reaching the patient branch. So
`StuckFrames` never increments and the breaker stays blind. **Proof:** a GDI/Nod `TDLTNK` pinned at
`(90,63)` sat at **383 `HEADON` events**, zero `HOLD-claim`, zero `CHOKE`, zero `SCATTER`; likewise an
Allied `APC(123,65)`↔`2TNK(122,66)` at 155 each. Both breaker-blind. **This is why the breaker only
fired ~once all match.**

**FIX (left for next session — fresh mind + immediate test; it's lockstep/desync-critical and the
skirmish quit so it couldn't be tested tonight; NOT a one-liner):**
1. **Gate head-on vs terrain.** At `drive.cpp ~1882`, `MOVE_NO` is *both* a friendly head-on (transient,
   scatter helps) *and* terrain/cliff (permanent — scattering = units jiggle against walls = NEW bug).
   Only increment / scatter when `destcell` holds a friendly **allied unit** (`Cell_Techno()` is
   `RTTI_UNIT` && `House->Is_Ally`). **Never** on bare `MOVE_NO` terrain.
2. **Extract a helper** `bool DriveClass::Try_Deadlock_Scatter()` holding the current inline breaker body
   (infantry-shove + id-seeded self-scatter + log), called from **both** the no-path branch and the new
   execution-blocked head-on case. One source of truth.
3. Increment `StuckFrames` in both blocked paths; reset stays on cell-advance. Keep `STUCK_SCATTER_TRIES=8`.
4. **Two ready test specimens** from tonight: west `TDLTNK(90,63)` and Allied `APC(123,65)`↔`2TNK(122,66)`
   — after the fix, expect `SCATTER-deadlock` to fire and the knots to clear.

### Spun off to SEPARATE workstreams (NOT chokepoint pathfinding — do not fix with give-way/scatter)
- **Harvester logic** (the big one): how harvesters target ore/Tiberium, path to it, and **claim a
  target** + detect **unreachability** and give up / re-select. Symptoms seen: harvesters spin forever
  on an unreachable resource (AI walled its own gems field with buildings → no path → `ABANDON-giveup`
  loop, 256 fallbacks); a tank did the same toward a base-blocked cell (`towardNav=OK` but `Basic_Path`
  fails); 2 Nod harvesters jammed at a refinery (dock contention). **Plus the economy-balance idea**
  (Luke): give RA + GDI/Nod the same unload dwell — dwell on the RA harvester's *tilted-bucket* unload
  frame (confirmed it exists) and drip credits over a matched time `T`; equalises economy and slightly
  slows overall pace (intended). **Diagnostic blind spot for this work:** an idle/abandoned harvester
  emits NOTHING to `tf_astar.log`, so it needs its own instrument (log idle harvesters holding cargo).
- **Recon Bike (`TDBIKE`) won't turn to fire** at off-axis targets — combat/facing bug, not pathfinding;
  check `IsTurretEquipped` / fire-arc vs TD source.

### Soft spots noted (not deadlocks)
- Recurring west map pinch at ~`x90,y63` (units congest there repeatedly, never escalates to gridlock).
- The breaker can leave a unit micro-churning if it scatters then re-paths back (a 2TNK did 67×
  `src==dst`); consider capping re-scatter on a returner. Minor.

### Late-game verdict
The committed + uncommitted set held up under sustained load: no map-wide gridlock, no frozen leads,
clusters self-resolve, breaker as a rare backstop. A real step up from the progressive gridlock the
night started with. Remaining stuck cases are either the breaker-branch gap (above) or the harvester
workstream.

> Diagnostic helper script: `/tmp/cnc_stuck_digest.sh` (parked / frozen-lead / HEADON-knot / SCATTER /
> clear-detection digest off `tf_astar.log`; anchors to the latest `session start` marker). NOTE it
> CANNOT see idle/abandoned units (they stop logging) and mistakes a *docked* harvester for a stuck one.

---

> **UPDATE 2026-06-15 (later):** the targeted reservation described under "NEXT JOB" below is now
> **IMPLEMENTED, built, and deployed to the desktop prefix — awaiting playtest.** Per-cell claim on
> `CellClass` (`ChokeClaimFrame` + `ChokeClaimDir`, TTL=24 frames self-healing, COMMIT_DIST=3),
> read+stamped in `Give_Way_Decision`, layered over the kept id-tiebreak fallback. New `CLAIM:` /
> `HOLD-claim:` / `HOLD-unit:` diagnostics. Decided to keep the live-unit id-rule as the pre-claim
> window resolver rather than rip it out. All uncommitted on v2.2.3-dev. See the cross-session memory
> `project-cfe-port-plan` for the implementation summary and the playtest recipe.

**Status:** the heuristic "give-way" layer (uncommitted, in `redalert/drive.cpp`) is a large
improvement over vanilla — it turns *every-time total deadlock* on a 1-wide bridge into *clean
whenever one column claims the corridor first; stuck only on near-simultaneous entry*. It has hit
its ceiling. **NEXT JOB (decided with Luke 2026-06-15): replace the ownership heuristic with a
TARGETED chokepoint reservation** (not a full WHCA\* space-time grid). This doc is the handoff.

The deployed desktop DLL is the **regression-reverted** build (see "current code state"). All the
give-way code is **uncommitted** on top of the v2.2.3-dev tree.

---

## The problem (confirmed, not theorised)

Two vehicle columns cross a **1-tile-wide × 3-tile-high terrain pinch** (snow map: gap between the
frozen lake/rocks and the map edge, around cell `x126`, `y50-53`) in **opposite directions** at the
same time. Vehicles are one-per-cell and the engine's head-on rule makes them undeadlockable by
threshold escalation, so they jam nose-to-nose. (Infantry are exempt — `InfantryClass::Can_Enter_Cell`
has no head-on rule and they stack 5 sub-cell, so they slip past; this is **vehicles only**.)

### The engine mechanism (root, verified by the `HEADON` diagnostic, 1000s of hits)
`UnitClass::Can_Enter_Cell` (`unit.cpp:~3649-3678`): for an allied blocker,
- **moving** ally → `MOVE_MOVING_BLOCK` (enum 2) — A\* routes through it (it'll clear).
- **stationary** ally → `MOVE_TEMP` (enum 4).
- **moving ally facing exactly opposite, within `0x1FF` (~1.25 cells)** → `MOVE_NO` (enum 5) — the
  head-on rule (`face == techface && Distance <= 0x1FF`). `MOVE_NO` is the one threshold A\* can
  **never** escalate past, so on a 1-wide pinch with no way around → A\* fails → legacy crash-and-turn
  → can't get around either → permanent oscillation at the pinch.

> ⚠️ The earlier memory note had `MOVE_TEMP` backwards ("the friendly that will clear"). It's the
> opposite: `MOVE_TEMP` = a **stationary** friendly; the **moving** one is `MOVE_MOVING_BLOCK`.

---

## What we built (the heuristic give-way — `redalert/drive.cpp`, UNCOMMITTED)

All in `DriveClass`. Vehicles only. Lockstep-safe (synced `As_Target()` ids, no `Random_Pick`).

- **`Give_Way_Decision(TechnoClass** winner_out)`** → `0` proceed / `1` hold / `2` retreat. The core
  predictive scan:
  - Walks the unit's **actual `Path[]`** through the terrain (NOT a straight line to NavCom — a route
    to an off-axis/inland goal bends down the pinch first, and a straight-line scan walks diagonally
    off the corridor and misses it. This was a real bug; path-following fixed it).
  - Finds the 1-wide corridor on the route (`narrow` = both perpendicular cells impassable terrain),
    tracks `corridor_start` (our distance to the near mouth) and `corridor_end` (far mouth).
  - **Occupancy rule:** an opposing allied vehicle **inside** the corridor → we yield (it owns it).
  - **Far-approach rule:** an opposing vehicle on the far approach (past `corridor_end`, up to
    `FAR_APPROACH=6` cells) with nobody inside yet → **lower id stands down** so the other claims it.
    (Was a *distance* tiebreak — that **flapped** every tick as columns jostled, causing
    advance/backtrack churn. Switched to **id** = stable owner. Id is fine because each group's units
    share a contiguous id range, so a whole column yields together.)
  - **Opposing-direction test uses each unit's QUEUED destination (`NavQueue[0]`), not its momentary
    heading** — otherwise a unit mid-retreat reads its own same-direction followers as oncoming
    traffic (the "APC giving way to the tank behind it" wedge). The **scan direction** uses current
    NavCom (so a retreat actually executes); the **opposing test** uses intent. Conflating these two
    caused a 903-event retreat storm — they MUST stay separate.
  - **Form:** HOLD on open ground (`!here_narrow`) = "stop before the bridge"; RETREAT if caught
    inside the pinch (`here_narrow`) = back out via `Find_Give_Way_Cell`, then it flips to HOLD on
    open ground.
- **`Find_Give_Way_Cell(blocker)`** — nearest **MOVE_OK** cell that increases distance from the
  blocker (radius ≤ 2). Requiring MOVE_OK is what stops the reverted-attempt failure of reversing into
  your own follower; boxed-in → returns 0 → hold.
- **`Start_Of_Move` top:** acts on the decision (hold → Stop_Driver+return; retreat → Assign yield
  cell + `Queue_Navigation_List(original)` to auto-resume).
- **No-path sidestep (safety net)** lower in the no-path branch, opposing-guarded.
- **Diagnostics (`TF_DEV_BUILD`, → `tf_astar.log`):** `HEADON:` (every head-on MOVE_NO),
  `CHOKE:` (every no-path branch: branch taken + `towardNav`/`aheadFacing` MoveType + try count),
  `GIVEWAY-retreat:`. There is **no HOLD log** — a gap; add one when resuming.

### Why it can't be finished as a heuristic (the ceiling)
Every remaining failure is **near-simultaneous entry → boxed-column reversal**: both leads enter the
pinch before either is established as owner; the losing column must fully reverse, but the front unit
can't back up until its own followers do, cascading from the rear. Stateless units have **no shared
truth about who owns the corridor** at the instant they both commit — so it races. Tuning thresholds
is whack-a-mole. (Dead ends proven tonight: one-side-yields-on-collision is WORSE than both-back-out —
it wedges a boxed loser while the winner shoves; reverted. Distance tiebreak flaps; reverted to id.)

---

## NEXT JOB: targeted chokepoint reservation

**Decision (Luke, 2026-06-15): do the reservation, but scoped to the chokepoint — NOT a full WHCA\*
space-time grid.** The full grid was rejected not for MP reasons but for invasiveness/perf (space-time
cell×tick structure, rewriting `Find_Path` to consult it + emit explicit waits, untangling legacy
fallback / harvesters / production exits). OpenRA itself isn't a pure WHCA\* grid — it's
occupancy + local avoidance + repath in the synced sim.

**The idea:** make corridor ownership **explicit, atomic, and sticky** instead of inferred per-tick.
When the first vehicle commits to a 1-wide corridor, it **claims** that corridor's cells with a
direction + in-flight count; opposing vehicles see the claim and hold on open ground; the claim
releases when the last same-direction unit exits. This is literally "make the engine's existing
cell-occupation bit sticky and direction-aware for pinch cells" — it gives the one thing the heuristic
lacks: **race-free ownership at the moment of commitment**.

- Likely home: a small field on `CellClass` (CFE left a dangling **`CellClass::ReservingVehicle`**
  stub — natural hook), or a tiny per-corridor token keyed off the pinch cells. Set/cleared in the
  deterministic logic pass, exactly where occupation bits are maintained.
- The give-way HOLD machinery we already built becomes the *consumer* of the claim (hold if the
  corridor is claimed by the opposing direction) — so most of tonight's code stays; we replace only the
  per-tick ownership *inference* with a read of the explicit claim.

### MP-determinism is NOT the blocker (the key realisation)
This engine is lockstep: every client runs the identical sim from identical orders. The **occupation
bits are already deterministic shared cell state across all clients** — a reservation is just more of
that. Put it in the sim, update it deterministically, and it's synced for free (no separate "sync the
table" step). Desyncs come only from a short, auditable foot-gun list:

1. **No RNG** in the reservation/decision path (`Random_Pick` with unsynced seed). (Already avoided.)
2. **Prefer int over float.** Our A\* uses `float` costs — fine on the identical 32-bit Windows DLL all
   clients run, but the reservation logic should be int to be safe. Original engine used fixed-point
   partly for this.
3. **No dependence on `unordered_map`/hash iteration order** for any synced result. (Our A\* uses it
   only for lookups, not result order — keep it that way.)
4. **Initialise all memory; no pointer-address-order comparisons.**

### Save/load
The claim must be either saved with the cell state or recomputed on load. Decide deliberately; a
recompute-on-load (claims are transient, rebuilt as units re-path) is likely simplest and avoids save
format growth.

---

## Current code state (for resumption)
- Deployed desktop DLL = **regression-reverted** build: collision rule is "both sides back out"
  (`opposing && narrow → yield`, unconditional). This was better than the one-side-yields variant.
- Tree: all give-way code uncommitted, on v2.2.3-dev (`ccmod.json` version_low 23). `TF_DEV_BUILD=1`
  local (diagnostics + cheats on). Build: `CMAKE_TOOLCHAIN_FILE=cmake/i686-mingw-w64-toolchain.cmake
  VC_CXX_FLAGS="-w;-fpermissive" cmake --workflow --preset remaster`; deploy = rsync
  `build/remaster/Vanilla_RA/` → desktop prefix `Mods/Red_Alert/Vanilla_RA/`.
- ⚠️ **Not committed and not shipped.** v2.2.3 is still unreleased. Decide before release whether to
  ship the heuristic give-way as an interim or wait for the reservation.

---

## DEFERRED ITEM (2026-06-15): A* fallback "cliff-hugging" when crossing a busy pinch

**Status:** known, low-harm, deliberately left for a later pathfinding-refinement pass (Luke's call).
The deadlock / give-ups / entrance-blocking are all FIXED and committed (`cdedd6c` + `4acaf94`); this is
the one residual.

**Symptom.** A vehicle ordered to cross a chokepoint while the pinch is momentarily busy/claimed by the
opposing direction is seen to "lose its pathfinding" and hug the cliff (take a long way around the
lake), then recover. It is cosmetic-ish: the unit still reaches its destination, it just takes an ugly
detour for a moment. It does NOT strand or deadlock.

**Root cause.** Pathing and give-way are separate layers. `FootClass::Find_Path` runs A* first; A* will
not route through a cell that is friendly-occupied head-on (`MOVE_NO` from an opposing moving ally) or
otherwise blocked, so when the only route is the busy pinch, A* FAILS and `Find_Path` falls back to the
legacy crash-and-turn edge-follower, which traces around the obstacle (the cliff/lake). The unit then
follows that legacy path; `Give_Way_Decision` does not redirect it because its route now goes AROUND the
pinch, not through it, so the give-way never engages to make it simply wait.

**Playtest metrics (the AI-test log, 2026-06-15).** ~211 A* fallbacks / 901 paths (~23%), BUT: the bulk
is infantry (`E6` 236, `E1` 66, `TDE6` 32, ...) which is the harmless sub-cell destination-contention
(infantry never deadlock); vehicle fallbacks (`2TNK`/`APC`/`1TNK`/`ARTY`/`JEEP`/`V2RL`/`TDHARV`/`3TNK`)
are almost all ONE-OFF (a single fallback then the unit proceeds). Only one unit repeated the same
src→dst (a `2TNK`, twice). So it is brief and self-correcting, not a stuck loop. AI faction units
(TD-prefixed) show the same one-off behaviour — no AI-specific deadlock.

**Proposed fix (for the later pass).** Make the unit WAIT for the pinch instead of taking a legacy
detour, when A* failed ONLY because of temporary traffic. Two candidate approaches:
1. *Clairvoyant A* probe* — when A* fails at the normal threshold, retry treating temporary blockers
   (ally `MOVE_TEMP`, ally-head-on `MOVE_NO`, and active `ChokeClaim` cells) as passable-but-costly. If
   that probe finds a path through the pinch but the real one did not, the route is traffic-blocked:
   return no-path (skip the legacy detour) so `Start_Of_Move`'s no-path branch + the patient-queue holds
   the unit, and it re-paths cleanly once the lane clears. If the probe also fails, it is genuine no-path
   → keep the legacy fallback.
2. *Let A* route through temp-blocked cells at high cost* so the unit heads INTO the pinch and the
   existing give-way HOLD then makes it wait there — simpler but broader blast radius (units routing
   through each other elsewhere); needs care.
Code: `redalert/foot.cpp` `FootClass::Find_Path` (the A*→legacy chain, ~line 365-478, `maxtype`
escalation), `redalert/findpath.cpp` `Find_Path_AStar`. The patient-queue + no-path branch that the fix
would hand off to is already in `redalert/drive.cpp` `Start_Of_Move` (the `traffic_blocked` 8-neighbour
scan). Diagnostic: the `A* FALLBACK -> legacy` tally line in `tf_astar.log` (gated `TF_DEV_BUILD`).

## Side question: what's left in the CFE first-wave after pathfinding?
First wave (docs/cfe-port-plan.md §1) is otherwise **complete**: Pixel-Perfect Zoom ✅, A\* ✅,
Attack-Move ✅, Rally Points ✅, Harvester Queue-Jump ✅, Harvester Optimization ✅, Smarter Repair Bay ✅.
**The only remaining first-wave item is #7 Infantry Tiberium Aversion** — small, and now unblocked
(it required A\*, which shipped). Port against our `OVERLAY_TIB01` fields; exempt visceroids; ore stays
harmless (Tiberium-only aversion).

After that, everything left is **second wave (§2, undecided candidates)** — Q-Move Overhaul, TS/RA2
wall building, Smarter Aircraft, Commando/Tanya Guard, Safe Sabotage, Suspend Building Repairs,
Smarter Chrono/Sonar, Building Capture Announcements, Smarter SAMs, Harvester Self-Repair, Smarter
Mammoths (audit — may already do it), Better Ore Growth, Meaner Visceroids — **plus the bugfix
inventory port candidates** (§3.3 CFE-original engine fixes, §3.4 optional feature-flagged, §3.5
unreleased v1.9, §3.6 TD-side fixes that touch our content). None are committed scope yet.
