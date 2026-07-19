# Known issues

Canonical in-repo tracker for known bugs and limitations. Started 2026-06-16.

Each entry: **severity** (blocker / major / minor / cosmetic), **status**, and a pointer to detail.
Player-facing limitations that cannot be fixed from a mod are listed too, so we stop re-investigating
them. When an issue is fixed, move it to the "Resolved" section with the fix commit.

---

## AI difficulty

### Per-slot difficulty goes stale or fails when lobby difficulties change within a session — OPEN 2026-07-19
- **Severity:** minor (either a wrong difficulty tier or a clean fall back to global Hard; no crash,
  and no desync is possible — only the host simulates a LAN match).
- **Repro: the FIRST LAN lobby after launching the game reads correctly; later ones may not.**
  A LAN match cannot be returned to a lobby — when it ends you re-host, and the new lobby starts
  blank (host player, open slots, no AI). So every subsequent match in a session is a freshly
  built lobby, and that is where the bad reads appear. Playing two LAN matches back to back can
  give correct difficulties in the first and stale-or-none in the second.
- **Cause:** the scanner requires every validated `AIPLAYERn` candidate array in client memory to
  agree. Each re-hosted lobby builds fresh records while the previous lobby's copies linger in the
  process, so the candidates disagree and the read either takes stale values or bails with
  `ram_slots=0`. Both observed 2026-07-19 in re-hosted lobbies: one read the previous lobby's
  `2,2,3,1` (stale, applied), the next produced `ram_slots=0`. The lobby run immediately after a
  game launch read `1,1,1,3` correctly.
- **Failure is graceful:** `ram_slots=0` falls back to global Hard, which is shipped v4.0 behaviour.
  Worst case is "no per-slot difficulty", never a broken or desynced match.
- **Workaround:** relaunch the game between LAN matches, so each match runs in the session's first
  lobby (verified: Easy/Easy/Easy/Hard → IQ 3/3/3/5 with 2 humans, immediately after a launch).
- **Fix path:** stop demanding unanimity — prefer the newest/most-specific candidate array. The
  `PHASEB-CAND` raw dump shows what the competing arrays hold; it was removed in `06ca30a` and
  should be restored from history to do this work.
- **Superseded reasoning:** this entry previously blamed the `humans < 2` apply gate and described
  the records as the account's saved skirmish config. Both are wrong — the gate is gone
  (`bb69419`) and the records do track the live lobby on a fresh launch. See
  `docs/lobby-difficulty-ram-spike.md` status block.
- **Scope update (overnight desktop session 2026-07-19): the stale record also hits the FIRST
  SOLO SKIRMISH after a LAN session, then self-corrects.** Match 1 of the night launched with the
  rig-night roster in `CNC_Set_Multiplayer_Data` (8 slots: 2 human Steam IDs incl. a ghost second
  human, 6 AIPLAYERs vs the actual 1+5 lobby) → `humans=2` tripped the determinism guard,
  `ram_slots=0`, my Medium slot pick ignored, ALL 6 AIs default-Hard, and 6 AI houses spawned
  (one more than the lobby had). Matches 3–4 the same night were clean (`humans=1 ram_slots=5`,
  per-slot Medium+Hard applied correctly) — so the poisoned record is served once and refreshed
  by the next lobby write. Evidence: scratchpad `MOD_DEBUG_AI.overnight.txt` (slot dumps + HELLO
  lines per match).

### Hiding a cloaked building's bib frees its cell for enemy placement — ✅ FIXED 2026-07-15
- **Severity:** minor (placement exploit; enemy could build one row into a cloaked base's bib strip).
- **Root cause:** the `TF_Sync_Bib` bib-hide (building.cpp) `Disown`ed the bib `SmudgeClass`, but a bib
  smudge also **blocks placement** (`CellClass::Is_Clear_To_Build`, cell.cpp:494). Removing it both
  hid the bib AND opened the cell for the (blind) enemy.
- **Fix:** removed `TF_Sync_Bib` entirely — it was redundant. A **render-time** bib-hide already exists
  in the Remaster draw path (`dllinterface.cpp` `tf_hide_bib`, from the original stealth-gen commit
  `cd8bd17`): it keeps the smudge (placement stays blocked) and suppresses only the *draw* when the
  covering building is `VISUAL_HIDDEN` (enemy view) — transparent to the enemy, bib still shown to the
  owner. Now that the cloak driver settles buildings to `CLOAKED` reliably, this handles the hide.
  Playtest-confirmed (Luke, 2026-07-16): enemy-side bibs stay hidden.

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
- **✅ LARGELY FIXED 2026-06-17 (symptom-patch hardened + playtest-validated; canonical write-up
  `docs/harvester-recovery-design.md`).** The "fix it properly via zone recompute on building events"
  plan was **REJECTED** after reading the code: `Zone_Span` ignores buildings *by design* (the
  `ignorevehicles` mask `0x5F` drops the Building occupy bit `0x80`, cell.cpp:3125), so making buildings
  call `Zone_Reset` is a no-op, and the building-aware variant that would be needed changes the global
  meaning of `Zones[]` (AI targeting / A* gate / `Is_In_Same_Zone` / base placement) — MP-determinism-
  risky, not worth it. **Chosen instead = harden the proven pathfinder-agnostic no-progress detector:**
  (1) `Blacklist_Harvest_Cell` flood-fills the whole contiguous ore field and blacklists its bounding
  box (was a single cell ±3, which let big walled fields keep re-spinning); (2) on no reachable ore the
  harvester pulls back toward a refinery + re-scans instead of idling at the wall. Playtest 2026-06-17:
  whole-field bboxes captured (28/66/45 cells) and harvesters redirected to a different reachable patch
  — Luke accepted as-is. Detector is a robust safety net for *any* unreachable-target case (not just
  buildings). Logs `HARV-BLACKLIST`/`HARV-WAIT` are `TF_DEV_BUILD`-gated (compiled out of release).
- **✅ FIELD SELECTION + BLACKLIST OVER-FIRING 2026-06-18 (commits `2465ae9` + the follow-up, on `main`,
  v3.0-gated). Desktop-validated across several AI matches.** Three linked fixes to `Goto_Tiberium` /
  the no-progress detector:
  1. **Travel-distance field pick.** The ring search returned the densest cell in the FIRST crow-flies
     ring with ore, so a field near in a straight line but only reachable the long way around water/cliff
     beat a closer-by-road one (Luke's SS #1). The LOOKING-state pick now gathers the NEAREST ore cell of
     each of the closest `HARV_FIELD_CANDIDATES`=10 rings and chooses the shortest ACTUAL A* path
     (`Find_Path_AStar`, null `resultPath` = cheap length-only query), density only a tiebreak.
  2. **Candidates by PROXIMITY, not density.** First cut picked each ring's *densest* cell — but a thin
     near field (low value) loses to a thick far/contested one, so harvesters drove across the map past
     close ore (the "ignored the field by the refinery, went south" reports). Proximity + A*-min-path
     fixed it; density-as-primary was the bug, NOT depletion (the near fields were full, just lower-value).
  3. **A* threshold = `MOVE_MOVING_BLOCK`, and the blacklist gated on real reachability.** The v2.4.0
     no-progress detector blacklisted any field a harvester couldn't approach for 5s — but base traffic /
     parked vehicles / friendly infantry produce that same symptom, so reachable home fields got
     blacklisted and harvesters fled (343 blacklists/session). Now the 5s stall consults A*: a path exists
     (congestion) → don't blacklist, grant up to 3 windows (~15s) then a bounded backstop; A* returns 0
     (genuinely walled) → blacklist as before. Querying at `MOVE_MOVING_BLOCK` (not the strict
     `PathThreshhold`) treats units-on-the-route as passable (they move / give-way pushes them) while
     walls/buildings/water still block — so unit-blocked near fields stop reading `apath=0`. Result:
     **343 → ~3 blacklists/session, all legitimate** (AI walling its own field with buildings; 1-cell
     remnant patches). New member `HarvReachableResets` (serialized with the unit). TF_DEV `HARV-FIELD`
     dumps each candidate's zone/value/apath + the nearest-ore/blacklist state.
  ⬜ STILL OPEN (follow-ups, not blockers): **exponential blacklist backoff** (a persistently building-
  walled field un-blacklists every 15s and gets re-poked — give repeat failures a longer TTL);
  **threat-aware selection** (don't route through enemy fire).
- **✅ ADDRESSED 2026-06-18 — harvester stuck/idle recovery + dock contention (#5, #6, dock).** Shipped
  (committed, v3.0-gated): `525910b`/`2d46def`/`49f8157`. See `harvester-docking-session-handover.md`
  (⭐ 2026-06-18 section) for the full write-up. Summary:
  - **Anti-stuck watchdog** (`UnitClass::AI`, position-stagnation, any mission): recovers wedged AND
    gave-up/idle harvesters (3s shove infantry → 6s `Try_Deadlock_Scatter` → 12s restart). Exempts only a
    HUMAN's manual MOVE/GUARD park. **Field-blacklisting stays owned by the ore-pursuit detector** (the
    watchdog must NOT blacklist — it can't tell "field walled" from "harvester wedged"; that poisoned
    good fields, `blskips=151`). Validated 83→4 blacklists, no loops.
  - **Field-richness gate** (`Goto_Tiberium`): prefer a field with ≥ half a load over a closer lone
    regrown block; tier-2 fallback = richest reachable. `Field_Tiberium_Value` + `HARV_FIELD_LOAD_DIVISOR`.
  - **Layer B harvester-only dock pad** + **dock staging** (per-harvester `Nearby_Location` locationmod).
  - **Corrected belief:** on the real maps the dominant "stuck" cause is **terrain** (cliff/water-split
    ore + narrow gaps) and **the AI walling its own ore/harvester with buildings**, NOT idle infantry
    (the 2026-06-17 "scatter friendly infantry" hypothesis was wrong — a 91-event sample was
    terrain/building-dominated, ally-infantry pins ≈ 0). A genuinely AI-box-in harvester (turret placed
    trapping it against the refinery+water) is OUT OF SCOPE — an AI placement problem.
  ⬜ STILL OPEN: **threat-aware field selection** (don't route through enemy fire). ⚠ BLOCKER: the engine
  region-threat map (`Cell_Threat`) is `Session.Type==GAME_NORMAL`-gated (`object.cpp:1859`) so it is
  INERT in skirmish — must build on a custom enemy-proximity scan instead. Design in the handover doc.
- **(earlier) ROOT CAUSE FOUND + partial fix for the walled-field loop (2026-06-16):** the autonomous scan
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

### Classic graphics mode dropped (HD-only)
- **Severity:** by-design, player-facing.
- **Status:** WON'T FIX — classic completely dropped once the TD theatre tilesets were added (no classic
  art path → terrain/units render broken). HD is the only supported mode. The classic spacebar toggle
  can't be locked from the mod side (launcher-owned; clean lockout is network-games-only). Memory
  `feedback-classic-graphics-unsupported`.

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
- TD temperate coastal tiles rendered as white squares (shores/bridges) — FIXED `ede7ca1`.
  The `TDSH*`/`TDBRIDGE*` `<Tile>` blocks were missing from `RA_TERRAIN_TEMPERATE.XML` so the
  launcher couldn't resolve their AssetNames. Cause: `build_td_tiles.py` spliced the shared
  `TF_TD_TILES` marker once **per theatre letter**, but `T` (temperate) and `S` (winter) both
  target the temperate XML and `splice()` replaces the whole block — the winter pass (added with
  the winter/desert theatres, `7c80fde`) overwrote the temperate shore/bridge block. Only visible
  on TD temperate coastal maps (e.g. TD Lost Arena); winter/desert maps were unaffected, so it
  shipped unnoticed. Fix: group the XML splice by destination file + restore the dropped blocks.

---

## Skirmish setup

### GDI/Nod skirmish "starting units" bonus gives RA units, not TD
- **Severity:** minor.
- **Status:** OPEN (post-1.0, unverified since; migrated from memory 2026-07-15).
- **Detail:** with UnitCount>0, the MCV spawn is faction-correct (Create_Units spawns UNIT_TDMCV) but
  the bonus combat units (tot_units = UnitCount*2/3; tot_infantry = remainder, scenario.cpp:3023) fill
  from RA's unit-selection logic with no TD-faction branch -> GDI/Nod get RA vehicles/infantry. Fix: add
  a TD-faction branch to the bonus-unit picker, mirroring AI_Unit/AI_Infantry's Can_Build approach.
