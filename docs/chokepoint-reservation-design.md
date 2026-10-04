# Chokepoint give-way and corridor claims

**Status:** Reference; shipped in 2.3.0.
**Open:** a vehicle head-on in a one-cell gap with no escape cell, scatter churn on a unit that
re-paths straight back (`known-issues.md`), and the A* fallback detour around a busy pinch (below).

Vehicles crossing a 1-wide pinch in opposite directions no longer deadlock. Three layers, all in
`DriveClass` and lockstep-safe:
- **Give-way** (`Give_Way_Decision`, `Find_Give_Way_Cell`): a vehicle that would meet an opposing
  ally in a corridor holds on open ground, or backs out to a free cell if caught inside.
- **Corridor claims** on `CellClass` (`ChokeClaimFrame`, `ChokeClaimDir`): the first column to
  commit (from `COMMIT_DIST` = 18 cells out) claims the corridor's cells with its direction; the
  opposing column reads the claim and holds. A claim stays active for `CHOKE_CLAIM_TTL` = 75 frames
  after its last assertion, and a unit re-stamps it only when it crosses into a new cell
  (`LastClaimCell`), so a stalled unit's claim ages out. Re-stamping every tick kept one stuck
  unit's claim alive forever and spread into whole-map gridlock.
- **Deadlock-breaker scatter** (`Try_Deadlock_Scatter`, `StuckFrames`): after
  `STUCK_SCATTER_TRIES` = 8 blocked cycles, from either the no-path branch or the head-on branch,
  the unit shoves a friendly idle infantryman off its path (give-way is vehicles only, so infantry
  never yield on their own) or scatters itself to an id-seeded free neighbour, then resumes. The
  head-on case counts only when the blocking cell holds an allied unit, never bare terrain, or
  units would jiggle against cliffs.

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

> ⚠️ `MOVE_TEMP` is a **stationary** friendly; the **moving** one is `MOVE_MOVING_BLOCK`.

---

## The give-way layer (`redalert/drive.cpp`)

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
    (A *distance* tiebreak flapped every tick as columns jostled; the id is a stable owner. A
    column usually shares a contiguous id range and yields together, but with interleaved ids the id
    rule and the claim can pick opposite winners.)
  - **Opposing-direction test uses each unit's QUEUED destination (`NavQueue[0]`), not its momentary
    heading** — otherwise a unit mid-retreat reads its own same-direction followers as oncoming
    traffic (the "APC giving way to the tank behind it" wedge). The **scan direction** uses current
    NavCom (so a retreat actually executes); the **opposing test** uses intent. Conflating these two
    caused a 903-event retreat storm — they MUST stay separate.
  - **Form:** HOLD on open ground (`!here_narrow`) = "stop before the bridge"; RETREAT if caught
    inside the pinch (`here_narrow`) = back out via `Find_Give_Way_Cell`, then it flips to HOLD on
    open ground. A unit nose-to-nose with the winner (`head_on_ahead`) retreats even on open ground:
    it sits on the cell the winner must move into, so holding would keep blocking it.
  - **Claims:** a claim stamps every pinch cell and the two mouth cells, so an opposing column stops a
    cell back instead of parking on the mouth (which is why the read loop checks every scanned
    cell). Each cell's claim direction is the local step through the pinch, not the direction to the
    goal, so off-axis columns see each other and a bent pinch is followed. A unit already inside the
    pinch pushes through an opposing claim.
  - **Open-ground backstop:** two allies nose-to-nose outside any corridor make the lower id step
    aside (returns 2); corridor owners are exempt.
- **`Infantry_Give_Way`** runs first, because idle men are invisible to the claims. At the mouth the
  vehicle waits while friendly infantry are walking through the pinch (scattering a moving column
  caused a scramble and then a lock), and pushes idle men in the pinch on. **`Drain_Infantry_Along`**
  moves them in the forward arc only (straight away, then the two forward diagonals), skips men
  already walking within an eighth of straight away, never reissues the same destination, and drains
  a packed column front first.
- **`Find_Give_Way_Cell(blocker)`** — nearest **MOVE_OK** cell that increases distance from the
  blocker (radius ≤ 3). Requiring MOVE_OK is what stops the reverted-attempt failure of reversing into
  your own follower; boxed-in → returns 0 → hold.
- **`Start_Of_Move` top:** acts on the decision (hold → Stop_Driver+return; retreat → Assign yield
  cell + `Queue_Navigation_List(original)` to auto-resume). Past `HOLD_TIMEOUT` (60 straight holds)
  a unit stops yielding; `HoldFrames` resets on any non-hold and on a cell advance. The patient queue
  scans all 8 neighbours, because the cell toward an off-axis goal can be terrain while the busy
  pinch is off to the side.
  - ⚠️ **Recursion hazard:** `DriveClass::Assign_Destination` re-enters
    `Start_Of_Move` for a stationary unit, so a RETREAT whose nested evaluation again decides
    RETREAT recursed unboundedly — `EXCEPTION_STACK_OVERFLOW` at ~1,500 frames deep in a fully
    jammed pinch (2026-08-01 DOCKLANDS crash dump). Guarded by `giveway_retreat_depth`: the
    retreat-triggered nested pass skips give-way evaluation and paths straight to the yield cell.
    Give-way is stateless-per-tick, so the skipped evaluation costs nothing.
- **No-path sidestep (safety net)** lower in the no-path branch, opposing-guarded.
- **Diagnostics (`TF_DEV_BUILD`, → `tf_astar.log`):** `HEADON:` (every head-on MOVE_NO),
  `CHOKE:` (every no-path branch: branch taken + `towardNav`/`aheadFacing` MoveType + try count),
  `GIVEWAY-retreat:`, `CLAIM:`, `HOLD-claim:`, `HOLD-unit:`, `SCATTER-deadlock`.

### Why give-way alone was not enough
Every remaining failure is **near-simultaneous entry → boxed-column reversal**: both leads enter the
pinch before either is established as owner; the losing column must fully reverse, but the front unit
can't back up until its own followers do, cascading from the rear. Stateless units have **no shared
truth about who owns the corridor** at the instant they both commit — so it races. Tuning thresholds
is whack-a-mole. Dead ends: one side yielding on collision is worse than both backing out (it wedges a
boxed loser while the winner shoves), and a distance tiebreak flaps every tick (the id tiebreak is stable).

---

## Why a claim and not a space-time grid

A full WHCA\* space-time grid was rejected for invasiveness and cost (a cell×tick structure, `Find_Path`
rewritten to consult it and emit waits, the legacy fallback, harvesters and production exits all
untangled). OpenRA itself is occupancy plus local avoidance plus repath. The claim makes corridor
ownership explicit and atomic at the moment of commitment, the one thing per-tick inference lacked, and
the give-way HOLD machinery reads it.

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

Claims are transient: whatever a save holds ages out within the TTL.

---

## Open: the A* fallback detour around a busy pinch

Known and low-harm; left for a later pathfinding pass.

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

**Playtest metrics (an AI-test log).** ~211 A* fallbacks / 901 paths (~23%), BUT: the bulk
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
