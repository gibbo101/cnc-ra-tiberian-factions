# Known issues

Canonical in-repo tracker for known bugs and limitations. Started 2026-06-16.

Each entry: **severity** (blocker / major / minor / cosmetic), **status**, and a pointer to detail.
Player-facing limitations that cannot be fixed from a mod are listed too, so we stop re-investigating
them. When an issue is fixed, move it to the "Resolved" section with the fix commit.

---

## Combat / units

### Recon Bike (TDBIKE) won't turn to fire at off-axis targets
- **Severity:** major (unit is much less effective; affects Nod harass doctrine).
- **Status:** OPEN, logged 2026-06-16, fix next session.
- **Detail:** the bike does not fire at an enemy unless already facing it, and won't rotate the chassis
  to bring its (turretless, forward-firing) weapon to bear. Suspects: `IsTurretEquipped` / fire-arc /
  `Rot` config for TDBIKE, or the rotate-to-fire path not engaging for a hull-mounted weapon. Compare to
  TD's BIKE per the TD-port chain-audit ritual; cross-check other hull-fixed TD vehicles (buggy, flame
  tank) to see if it's bike-specific. NOT visible in `tf_astar.log` (that only logs movement). See
  cross-session memory `project-bug-recon-bike-no-turn-to-fire`.

---

## Pathfinding / AI cooperation

### Vehicle-vs-vehicle head-on in a 1-tile gap with no escape cell (breaker unreachable from gw==2)
- **Severity:** minor (self-resolves — the boxed unit eventually dies/clears; never escalates to gridlock).
- **Status:** OPEN — remaining give-way loose end after v2.3.0.
- **Detail:** when `Give_Way_Decision` returns gw==2 (RETREAT) but `Find_Give_Way_Cell` finds no free
  escape cell, the unit holds and never reaches `Try_Deadlock_Scatter`, so the breaker can't fire on
  that case. Fix = make the breaker reachable from the gw==2 path. NOTE: the original "breaker is in the
  WRONG BRANCH" issue (it only lived in the no-path branch, missing execution-time head-on `MOVE_NO`
  clumps) was FIXED in v2.3.0 — `Try_Deadlock_Scatter` is now called from the execution head-on path
  (`drive.cpp ~2301`) as well as the no-path branch. See `docs/chokepoint-reservation-design.md`.

### Deadlock-breaker micro-churn on returners
- **Severity:** minor (cosmetic jiggle; unit not lost).
- **Status:** OPEN — noted 2026-06-16.
- **Detail:** a unit can scatter then re-path straight back into the stuck spot and spin (observed a
  `2TNK` doing 67× `src==dst`). Consider capping re-scatter when a unit keeps returning (likely an
  unreachable goal, not a breakable deadlock). See the checkpoint doc.

### Recurring west map pinch (~cell x90, y63 on the test snow map)
- **Severity:** minor (units congest there repeatedly; never escalates to map-wide gridlock).
- **Status:** OPEN — noted 2026-06-16; watch whether the breaker-branch fix resolves it.

---

## Harvester logic / economy (own workstream)

### Harvesters spin forever on an unreachable resource
- **Severity:** major (idle harvesters = dead economy for those units).
- **Status:** OPEN — own workstream (targeting / pathing / claiming / reachability).
- **Detail:** when ore/Tiberium is unreachable (e.g. the AI walls its own gems field with buildings) a
  harvester A*-fails → `ABANDON-giveup` → AI re-orders → loops forever instead of re-selecting a
  reachable field. Same root hit a tank ordered into a base-blocked cell. Also: 2 harvesters jammed at a
  refinery dock (contention). **Diagnostic note:** an idle/abandoned harvester emits NOTHING to
  `tf_astar.log` — this workstream needs its own instrument. See `docs/chokepoint-reservation-design.md`
  CHECKPOINT 2026-06-16 (spun-off workstreams) + memory `project-cfe-port-plan`.

### Economy asymmetry: GDI/Nod dock (slow) vs RA auto-dump (fast)
- **Severity:** balance (intended TD-authentic behaviour, not a bug — but a candidate to equalise).
- **Status:** PROPOSAL — make RA also dock (dwell on the tilted-bucket unload frame) for a matched time.
- **Detail + balance interaction:** see `docs/balance-deep-dive.md` (economy asymmetry section) — note
  equalising removes the GDI/Nod slower-economy counterweight to their cheaper army + the Mammoth.

---

## Launcher / engine limitations (cannot be fixed from a mod — do not re-investigate)

### Select-all (A) and Deploy (/) hotkeys ignore GDI/Nod harvester + MCV
- **Severity:** minor, player-facing.
- **Status:** WON'T FIX (launcher-hardcoded unit identity; not reachable from the DLL/mod).
- **Workaround:** drag-box to select army; click the MCV with the deploy cursor to deploy. Documented in
  the Workshop "Known limitations". MCV deploy hotkey spike resolved-negative (memory
  `project-mcv-deploy-hotkey-spike`).

### Classic graphics mode unsupported (HD-only)
- **Severity:** by-design, player-facing.
- **Status:** WON'T FIX — official since v2.0.0 (new theatre tiles / some units don't render correctly in
  Classic). HD is the supported mode. Memory `feedback-classic-graphics-unsupported`.

---

## Localization

### Localized SFX file clobbers DE/FR voice dub
- **Severity:** minor, non-fatal (German/French players hear English voices).
- **Status:** OPEN backlog.
- **Detail:** our `SFXEVENTSLOCALIZED.XML` is a 981-event all-`_EN-US` file overriding every player's
  localized voices. Fix = trim to TD-only events. Memory `project-localized-sfx-clobbers-dub`.

---

## Multiplayer / LAN

### LAN crashes with crates enabled
- **Severity:** major for LAN (single-player skirmish unaffected).
- **Status:** OPEN, uninvestigated.
- **Workaround:** turn crates off for LAN play (per the Workshop "Known limitations"). Not yet root-caused.

---

## Resolved
<!-- Move fixed issues here with the fix commit, e.g.:
- Immortal-claim whole-map gridlock — FIXED 6f35ea9 (claim-on-crossing). -->
- Immortal-claim whole-map chokepoint gridlock — FIXED `6f35ea9` (claim-on-crossing). See
  `docs/chokepoint-reservation-design.md` CHECKPOINT 2026-06-16.
