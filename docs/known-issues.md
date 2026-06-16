# Known issues

Canonical in-repo tracker for known bugs and limitations. Started 2026-06-16.

Each entry: **severity** (blocker / major / minor / cosmetic), **status**, and a pointer to detail.
Player-facing limitations that cannot be fixed from a mod are listed too, so we stop re-investigating
them. When an issue is fixed, move it to the "Resolved" section with the fix commit.

---

## Combat / units

### Recon Bike (TDBIKE) won't turn to fire at off-axis targets — ✅ FIXED 2026-06-16
- **Severity:** major (unit was much less effective; affected Nod harass doctrine).
- **Status:** RESOLVED — `UnitClass::Rotation_AI` (unit.cpp:601).
- **Root cause:** for turretless vehicles, RA only rotates the hull to face a target if the unit is
  **tracked** ("wheeled vehicles never rotate to face the target — not maneuverable enough"). TDBIKE is
  wheeled, so it never turned and only fired at whatever it already faced. TD's source special-cases its
  wheeled bike to rotate anyway (`tiberiandawn/tarcom.cpp:166`, `|| *this == UNIT_BIKE`); RA left that
  clause commented out (vanilla RA has no bike). Fix = restore the exemption for `UNIT_TDBIKE`. Now uses
  the same body-rotate-in-place path as the (tracked, turretless) Artillery, which always worked.

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
- **Status:** OPEN — own workstream (deferred to a dedicated segment, Luke 2026-06-16). Targeting /
  pathing / claiming / reachability.
- **Detail:** when ore/Tiberium is unreachable (e.g. the AI walls its own gems field with buildings) a
  harvester A*-fails → `ABANDON-giveup` → AI re-orders → loops forever instead of re-selecting a
  reachable field. Same root hit a tank ordered into a base-blocked cell. Also: 2 harvesters jammed at a
  refinery dock (contention). **Diagnostic note:** an idle/abandoned harvester emits NOTHING to
  `tf_astar.log` — this workstream needs its own instrument. See `docs/chokepoint-reservation-design.md`
  CHECKPOINT 2026-06-16 (spun-off workstreams) + memory `project-cfe-port-plan`.
- **ROOT CAUSE FOUND + FIXED for the walled-field loop (2026-06-16):** the autonomous scan
  `UnitClass::Tiberium_Check` (unit.cpp:2519) ALREADY zone-filters (`Map[Coord].Zones[MZone] !=
  Map[center].Zones[MZone] → 0`), so `Goto_Tiberium` correctly finds "no reachable tiberium" when the
  only field is walled off. The infinite spin was the **`ArchiveTarget` fallback** in `Mission_Harvest`
  LOOKING (unit.cpp:3291): it re-dispatches the harvester to its last-mined cell **with no reachability
  check** and (unlike the sibling site at 3256) never clears it. So path-fail → NavCom clears → re-scan
  finds nothing reachable → archive still legal → re-dispatch to the same unreachable cell → loop (the
  "256 fallbacks"). **FIX (commit pending):** guard that reassignment with
  `Is_In_Same_Zone(As_Cell(ArchiveTarget))`; if the archive is gone/unreachable, clear it and fall to
  GOINGTOIDLE instead of charging it forever. Surgical — only changes behaviour in the exact failure
  case (archive in a different zone), identical in normal harvesting. **STILL FOR THE SEGMENT:** target
  CLAIMING (two harvesters picking the same patch), refinery dock contention, the same-zone-but-
  dynamically-blocked case (a partial wall / unit blocking a reachable-by-zone route), and finding a
  reachable field beyond TiberiumLongScan range. This fix only kills the walled-off-field spin.

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
