# Chokepoint give-way + reservation — design & checkpoint (2026-06-15)

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
