# CFE Patch Redux port plan

Plan for adopting QoL features and bugfixes from **CFE Patch Redux** by ChthonVII.

- **Source of truth:** `reference/cfe-patch-redux/` — clone of
  [ChthonVII/CnC_Remastered_Collection](https://github.com/ChthonVII/CnC_Remastered_Collection),
  full history fetched. Last release is **1.8**; there is unreleased **v1.9 testbuild work
  through 2025-04** (tags `v1.9-RA_testbuild0x` / `v1.9-TD_testbuild0x`), so the GitHub repo
  supersedes the Workshop builds.
- **Licence:** GPL v3 both sides. Copying their code is fine; we already publish source.
  ChthonVII's README explicitly invites GPL-compliant reuse (and explicitly threatens DMCA
  against non-compliant reuse, so keep attribution + source publication in order).
- **Their RA changelog files:** `Documentation/Changelogs/1.7/RA_Changelog_1.7.txt` and
  `1.8/RA_Changelog_1.8.txt`. Pre-1.7 fixes are only in git history.
- **Their feature toggles:** everything is INI-gated via `CFEPATCHREDUX_RA.INI` — useful for
  locating each feature's code (grep the INI key name). We will generally hard-enable rather
  than reproduce their settings system, unless a feature is gameplay-affecting (see §4).

## Porting ground rules

1. **CFE diffs against EA's raw source; we are a Vanilla Conquer fork.** Same ancestry but
   every port is a manual transplant, not a cherry-pick. Expect drift in exactly the files VC
   refactored.
2. **Many CFE "vanilla bugfixes" were lifted FROM vanilla-conquer** (commit messages say so)
   — those are already in our base. §3.1 lists them so nobody re-ports them. Two exceptions
   where ChthonVII claims VC's fix is *wrong* are audit items (§3.2).
3. Per workspace rules: TD-authentic stats stay untouched. CFE's balance content (TD Balance
   Patch, veterancy, OpenRA supers, instant capture, etc.) is **out of scope** — see §5.
4. Each ported feature gets its own commit citing the CFE source commit(s)/files, and a
   CHANGELOG entry. Attack-Move and A* are big enough to be their own releases.
5. Multiplayer note: CFE 1.7's headline was making all of this LAN-safe. When porting, take
   their LAN-safe version (post-1.7 code), not the earlier SP-only logic.

---

## 1. QoL first wave (DECIDED 2026-06-11 — this is the work queue)

| # | Feature | CFE INI key (locator) | Size | Notes for our port |
|---|---|---|---|---|
| 0 | **Pixel-Perfect Zoom** | none (static; data-only) | TINY | **PRIORITY 1 (Luke, 2026-06-11).** No DLL code: loose `Data/XML/GAMECONSTANTS.XML` in the mod folder, `<CNCZoomFactors network="client" overwrite="true">` block — 11 factors 0.246875–1.975 (vanilla: 8 factors 1.0–2.0, so this also zooms OUT further). CFE commit `ea2dde5`. Port = extract BASE GAMECONSTANTS.XML from our install, swap in the zoom block only, ship in our `Data/XML/`. Bonus intel: same file carries `CNCTDTheaterTilesets` (theatre→tileset map, relevant to desert) + many other mod-reachable client constants. |
| 1 | **A\* Pathing** | `ASTAR_PATHING` | LARGE | Replaces "crash and turn" pathfinder. **Stage 1 of the two-stage pathfinding plan — see §1.1.** Foundation for #6. 1.8 fixed a crash on paths >200 cells — take the fixed version. Touches core movement; needs the biggest playtest soak. |
| 2 | **Attack-Move** (Shift+Click) | `ATTACK_MOVE` | ✅ CODE-COMPLETE 2026-06-13 (in playtest) | Post-1.7 LAN-safe rework, hard-enabled, all special cases (aircraft RTB on empty ammo, boats brief-attack, minelayers, chronotanks). Hard-enabled q-attack-move rides VANILLA's queue (CFE's queue rewrite NOT taken — fallback if flaky: stop converting ATTACKMOVE→QATTACKMOVE). One build fix: `AircraftClass::IsLanding/IsTakingOff` made public. **One deliberate deviation from CFE — see §1.2 (passive-building targeting).** |
| 3 | **Rally Points** | `RALLY_POINTS` | ✅ DONE 2026-06-11 | Desktop-verified all factions. Incl. v1.9 long-line crash fix + two improvements over CFE: rally to "unplaceable" cells (their Can_Enter_Cell placement-legality dead zones near cliffs/shore/ore) and DOTGDI/DOTNOD faction end-dots. Found + fixed our DLL_Draw_Intercept ShapeSize-override trap (building-attributed named draws inflate to building size for TD buildings). Repair-bay rally (FIX/TDFIX) deferred to #6 as CFE gates it on Smarter Repair Bay exit logic. |
| 4 | **Harvester Queue Jumping** | `HARV_QUEUE_JUMP` | SMALL | Independent toggle in CFE; works with #5. Verify against our TDPROC/TDHARV Limbo+Attach dock plumbing — our harvester counting bug (docked harvesters leave UQuantity) is exactly the kind of state this code reads. |
| 5 | **Harvester Optimization** | `HARV_OPTIMIZATION` | SMALL | Nearest-refinery with per-inbound-harvester distance penalty. CFE's recommended choice over the older Load Balancing (which auto-disables when both are on — we just don't port Load Balancing). Same TDPROC caveat as #4. |
| 6 | **Smarter Repair Bay** | `SMARTER_REPAIR_BAY` | MEDIUM | Queue for occupied bay + fixed RA bay rally + exit logic. Includes their fix for units ignoring collision on the bay. Must cover STRUCT_TDFIX alongside RA's FIX. |
| 7 | **Infantry Tiberium Aversion** | `TIB_AVERSION` (TD side) | SMALL once #1 lands | TD-only in CFE; we port it against OUR `OVERLAY_TIB01` fields in RA. Requires A*. Exempt visceroids (and decide: do TD-faction infantry path around ore too? No — Tiberium only, ore is harmless). |

Suggested order: 0 first (decided priority 1), then 3 → 4+5 → 6 (independent,
small-to-medium, immediately felt) while reading in for 1; then 1, then 2, then 7. A* and
Attack-Move are the two rewrites; everything else is bounded.

### 1.1 Pathfinding strategy (DECIDED 2026-06-11: A* first, refine later)

Reconciled with `docs/ai-improvements.md` §"Pathfinding — options considered", which
correctly argues the dock-stuck/chokepoint problem is a **traffic/cooperation problem, not a
path-search problem** — a better search algorithm alone doesn't fix it.

- **Stage 1 (this plan): port CFE's A\*.** Replaces the search layer (`findpath.cpp` greedy
  "crash and turn"). Battle-tested in this exact engine, LAN-safe, >200-cell crash already
  fixed. Supersedes ai-improvements.md's "implement JPS" idea — JPS's edge over A* is mostly
  speed, which RA-sized maps don't need.
- **Stage 2 (later, ours): reservation table + scatter-the-blocker** on top, per
  ai-improvements.md's recommendation — reserved cells as soft cost penalties in the A* grid
  (same mechanism CFE's Tiberium Aversion uses for Tiberium cells, so stage 1 builds the
  hook). This is the layer that actually fixes dock deadlocks. OpenRA's cooperative
  pathfinder remains the reference. WHCA*/ORCA stay rejected as overkill/engine-hostile.

#### Stage 2 — refined by the v2.2.1 A* playtest (2026-06-14)

The stage-1 A* release shipped with a `TF_DEV_BUILD` diagnostic (`tf_astar.log`: per-fallback
detail + running success/fallback tally; gated on `TF_DEV_BUILD`, appends per match). Two
playtests on a snow map produced the concrete spec for stage 2:

- **A* is healthy.** ~74% path success, **zero genuine long-path search failures**. Every single
  fallback-to-legacy was "the destination cell I was told to enter is occupied by a friendly."
- **The dominant failure is DESTINATION CONTENTION, not through-traffic.** In one match **78% of
  fallbacks (252 of 325) targeted a single cell** (`dst=(111,88)`); another magnet was `(30,32)`
  hit by 6+ distinct unit types. Symptom = the 1-wide jam, units running up/down, tanks tracing a
  cliff. Root: a whole group is ordered onto **the same cell**; the first unit occupies it, then
  for every other unit the target is impassable + within 3 cells, so A* bails (`return 0`,
  Find_Path_AStar's close-impassable rule) → legacy → can't enter the occupied cell → re-path next
  tick → repeat.
- **So stage 2 = TWO mechanisms, and destination-spread is the bigger lever here:**
  1. **Destination spread / formation** — when a group move (or attack-move) is issued, assign each
     unit a DISTINCT nearby cell instead of all the same cell.
     **INVESTIGATION RESOLVED (2026-06-14):** the group-move dispatch is
     `DisplayClass::Mouse_Left_Release` (display.cpp:3920-4047), active in the Remaster build via
     `INPUT_REQUEST_COMMAND_AT_POSITION` → `TacButton.Command_Object(LEFTRELEASE)`. Vanilla applies
     spread ONLY for true formation moves — every selected unit in the SAME control group with a
     stored `XFormOffset != INVALID_FORMATION` (set only by the explicit formation toggle:
     control-group + F-key, `DLLExportClass::Team_Units_Formation_Toggle_On`). Then
     `foot->Adjust_Dest(cell)` (foot.cpp:2347) offsets each unit. For an ordinary (non-formation)
     group move — the overwhelmingly common case — `FormMove == false`, so the loop sets
     `CELL newmove = cell` for EVERY unit: identical clicked cell, NO spread. So **the contention is
     inherent vanilla behaviour, NOT a regression our A* introduced.** The legacy crash-and-turn
     follower MASKED it (it never "fails" — bumps the occupied cell and settles in a neighbour);
     A* explicitly bails on a close-impassable destination → re-paths every tick → the visible jam.
     **Implementation hook is clean:** the per-unit destination is computed at click time
     (display.cpp:4034) and travels inside each unit's MEGAMISSION event, so spreading HERE is
     multiplayer-safe with zero changes to the synced logic loop. Building blocks already present:
     `Adjust_Dest` (formation offset) + our ported `FootClass::Find_Passable_Position_Near` (spiral
     ring search). Plan: in the non-formation branch, for N>1 FootClass units assign each a distinct
     passable+unclaimed cell from an expanding ring around the clicked cell (track claims in a local
     set; prefer the free cell nearest each unit's own position to minimise path-crossing).
  2. **Reservation table + scatter-the-blocker** — the originally-planned through-traffic fix:
     publish reserved cells as soft cost penalties in the A* grid (the Passable_Cell cost hook
     stage 1 already exposes), and trigger a stationary friendly blocker's `Scatter()` when it
     holds a needed cell. Also reconsider Find_Path_AStar's close-impassable bail (straight-line
     distance ≤3 → give up) — with reservation/spread in place this bail may be doing more harm
     than good.
- **Test cases** from the playtest: the contended cells `(30,32)` and `(111,88)` on the snow map;
  watch the tally drop and the per-cell fallback concentration disappear. Ships as **v2.3.0**.

### 1.2 Attack-move deviation from CFE: passive-building targeting (Luke, 2026-06-13)

**Deliberate one-feature departure from CFE attack-move behaviour.** Logged here because the
porting rule is "document deviations."

- **CFE / vanilla behaviour:** the engine hard-codes that a human player's units never
  auto-target an enemy building with no weapon (`TechnoClass::Evaluate_Object`, the
  `tclass->PrimaryWeapon == NULL` "not aggressive" filter). CFE kept this filter, so CFE
  attack-move engages enemy *units* and *defensive structures* (turrets, Tesla, Obelisk, SAM,
  gun towers — they carry weapons) but drives straight past *passive* buildings (power,
  refinery, barracks, factory, con yard). Verified: CFE's `Evaluate_Object` is byte-identical
  to ours here — no attack-move special-casing.
- **What Luke wanted:** classic-C&C / StarCraft a-move — attack-move shells *everything* in
  range, **but** prioritises armed threats so a tank engages the Tesla coil rather than
  plinking a kennel while the coil kills it.
- **Our implementation (techno.cpp):**
  1. `Evaluate_Object` weaponless-building filter gains `&& !(AttackMove &&
     _AttackMoveIncludePassiveBuildings)` so passive buildings become valid targets on the
     "passive pass" only.
  2. **Two-pass scan** in `Target_Something_Nearby`: when `AttackMove` is set, scan first for
     armed targets only (vanilla filter active → defensive structures + enemy units); only if
     nothing armed is in range, flip `_AttackMoveIncludePassiveBuildings` and scan again
     including passive buildings. Strict tiering, so armed threats always win when in range.
  3. `_AttackMoveIncludePassiveBuildings` is a file-scope static (single-threaded engine; set
     and cleared within one scan) — no class-layout / savegame growth.
- **Why two-pass and not a value boost:** the final target score is distance-weighted
  (`value * 32000 / (dist+1)`), so a close kennel out-scores a farther Tesla under any
  additive boost, and a multiplier large enough to fix that overflows the 32-bit score. Two
  passes sidestep both. Gated entirely on `AttackMove`, so plain Guard behaviour is untouched
  (guarding units still ignore passive buildings, as vanilla intends).
- **Threat response (added same day, after Luke saw tanks tunnel-vision a building while a
  Tesla coil / enemy units chewed them up):** the two-pass priority above only applied at
  *initial* acquisition — once locked on an in-range passive building, nothing re-evaluated.
  Added a block to the `TechnoClass::AI` attack-move retarget: each tick, if the current
  target is a weaponless building, run an armed-only `Greatest_Threat(THREAT_RANGE)` scan and,
  if anything armed is in range, disengage and switch to it. Fires only when there's a real
  threat to switch to (never swaps one passive building for another); aircraft + move-locked
  boats exempt. Deliberately does *not* switch between two armed targets (avoids dithering) —
  it only breaks passive-building tunnel-vision. **Luke-verified "attack move is great"
  2026-06-13.**

## 2. QoL second wave (candidates, not yet decided)

- **Q-Move Overhaul** (1.8) — queued-waypoint system rework; optional loops + aircraft q-move.
- **TS/RA2-style Wall Building** + Configurable Build Distance — line-fill walls; TD-style
  0-gap base spacing is thematically interesting for our TD factions.
- **Smarter Aircraft** — no-ammo aircraft ignore attack orders; helicopters re-path on target
  move; fly-in on helipad Y. Touches our Orca/Apache.
- **Commando/Tanya Guard** — guard-mode infantry attacks; covers our TD Commando. v1.9 HEAD
  has a `Target_Legal()` fix for this — take it.
- **Safe Sabotage** — no survivors from C4. CFE demoted default to SP-only (MP-overpowered).
- **Suspend Building Repairs** — pause instead of cancel when broke.
- **Smarter Chrono / Smarter Sonar / Building Capture Announcements** — RA-side polish.
- **Pixel-Perfect Zoom** — static feature, pure client-side feel.
- **Smarter SAMs** (TD-only in CFE) — maps 1:1 onto our TDSAM.
- **Harvester Self-Repair** (TD-only) — regen to 50%; candidate for TDHARV.
- **Smarter Mammoths** (TD-only) — missiles vs infantry. AUDIT FIRST: our TD-ported Mammoth
  may already do this via RA's secondary-weapon convention.
- **Better Tiberium/Ore Growth** — we have our own growth; compare algorithms. The
  blossom-tree-spawns-visceroid flavor is adoptable standalone.
- **Meaner Visceroids** (TD-only) — threat buffs for our visceroids.

## 3. Bugfix inventory

### 3.1 Already in our VC base (no action — listed to prevent re-porting)

Memory/UB cleanup (delete-on-void*, virtual destructors, overlapping strcpy/memcpy,
List_Copy/MemCopy), radar signed/unsigned + missing IsActive checks, harvest-via-radar,
Ukraine general using Stavros voice, mobile gap generator not updating in motion, off-by-one
waypoint error, Monster Tank Madness mission-critical units invisible, infinite "new
construction options" announcement (captured-MCV aircraft buildings), building off stale
proximity of a destroyed building, MIG pip display, building occupy-list OOB read, MIX-file
open failure leak, savegame Nod radar colour (legacy-only).

### 3.2 Audits — ChthonVII says VC's fix is WRONG (check our copies vs his)

- [ ] `Base_Is_Attacked()` defender-selection-by-strength — "Vanilla-Conquer commit c608b48
      has this totally wrong."
- [ ] `MISSION_NONE` used as array index (OOB reads) — "inspired by VC's 624e391, but I think
      they have the logic wrong in places." Also one memcpy→memmove.

### 3.3 CFE-original engine fixes, RA-relevant (port candidates)

Crashes / UB:
- [ ] Crash loading custom map with invalid mission string in INI (UB in stricmp)
- [ ] Crash when infantry move into a building during their death animation
- [ ] Crash when a unit death animation overlaps a building (missing IsActive)
- [ ] Sidebar off-by-one crash (EA repo issue #105)
- [ ] Multiple MAD Tanks detonating on same/consecutive ticks
- [ ] Chain lightning: MISSION_NONE segfault + force-fired-at-ground misbehavior
- [ ] Building placement map-wrapping bug
- [ ] **Mod variables reset to 0 on savegame load in RA** — high relevance: we carry
      Tiberium/visceroid/blossom state. Audit our save path regardless of whether we take
      their fix.

Multiplayer correctness (matters for LAN play with the kids, and any future MP story):
- [ ] MP sound routing — "HUGE number" of sounds playing for wrong player / not playing for
      right player
- [ ] Unit flash effect shown to wrong players
- [ ] Per-house "discovered" flag system overhaul — fixes shroud-reveal from under-shroud
      fire; foundational for shroud-respecting AI (ties into our AI roadmap)
- [ ] Hand/Barracks/Factory/Airstrip wrongly flagged "captured" when built in MP → reduced
      crew spawns

Gameplay logic:
- [ ] Helipads counted toward RA fixed-wing aircraft limit
- [ ] Fixed-wing planes fire 1 extra shot after expending ammo (pair with optional MIG Ammo
      Fudge if we care about preserving 4-shot MIG feel)
- [ ] MISSION_AMBUSH did nothing
- [ ] Gunboats not firing when spawned off-map
- [ ] Units ignoring collision detection on the repair bay (folds into first-wave #6)
- [ ] Custom missions using wrong AI building-repair threshold (matters for our campaign arc)
- [ ] Darkness crate hides allied units despite IsAllyReveal; reveal crate blocked after
      reveal→darkness sequence
- [ ] Ore-growth fixes: mine head spawns ore around wrong cell / ore on top of mine head /
      new ore flashes wrong growth stage / `GOLD01.SNO-0000.DDS` is mistakenly a copy of the
      max-growth texture (HD asset fix)

### 3.4 Optional feature-flagged bugfixes (gameplay-changing — decide deliberately)

- [ ] **Inaccuracy Bugfix** — RA weapon inaccuracy never worked at all. Big feel change;
      CFE pairs it with MIG Ammo Fudge.
- [ ] **Timequake Fix** — Aftermath timequakes never worked.
- [ ] **Ore Index Bugfix** — 0-vs-1-indexed cluster; harvesters scoop without gaining bails.
      Economics-affecting. Check whether OUR Tiberium overlay inherited this bug class.
- [ ] **Gem Overload Fix** — excess gem bails vanish; fix dumps ore back to make room.
- [ ] **Long Building Gap Bugfix** — unify placement-proximity logic across building types.
- [ ] **Distance Calc Fix** (v1.9, unreleased) — exact distance vs the fast integer
      approximation. Subtle global behavior change; low priority.

### 3.5 Unreleased v1.9 fixes (post-1.8 commits)

- [ ] Rally-point lines crash GlyphX client when very long (take with first-wave #3)
- [ ] Crate outcomes that may kill the opener postponed past the AI loop (use-after-free +
      permanently-reserved cell). TD-only, author-flagged "needs ported to RA".
- [ ] Search-range fix excluding pre-placed/CPU units until activated. TD-only, same flag.
- [ ] MCV preserves ActLike/capture state across undeploy→redeploy — touches our shared
      UNIT_TDMCV/STRUCT_TDFACT; cross-check [[project-mcv-conyard-sharing]] guard.

### 3.6 TD-side CFE fixes that land on OUR content (we have these systems in RA)

- [ ] AI houses wrongly consider HOUSE_NEUTRAL and **HOUSE_JP** when picking an enemy to
      fixate on — our visceroids are HOUSE_JP. Check RA's house-selection equivalent even if
      the TD fix doesn't transplant directly.
- [ ] Neutral "kill structures" objective insta-kills visceroids (HOUSE_NEUTRAL owns no
      structures) — relevant if our campaign/co-op missions use such objectives.
- [ ] Players can one-way ally with visceroids.
- [ ] AI overweights proximity when picking a target house in MP.

## 4. Settings policy

CFE gates everything behind `CFEPATCHREDUX_RA.INI`. Our policy:

- **Pure QoL / pure bugfix:** hard-enable, no toggle. Fewer codepaths, less drift.
- **Gameplay-affecting fixes (§3.4):** decide per-item with Luke; if adopted, they're just ON
  and documented in the CHANGELOG (we don't ship a user-facing settings file).
- Dev-time toggles, if needed during bring-up, follow our `#if 0` diagnostic convention
  ([[feedback-keep-diagnostics-until-v1]]) and Luke owns flipping them
  ([[feedback-never-touch-dev-toggles]]).

## 5. Explicitly out of scope (balance/flavor — conflicts with TD-authentic rule)

Veterancy system, TD Balance Patch, OpenRA Wide/Quick Supers, Chrono Disaster Overhaul
(beyond the Timequake bugfix), Instant Capture (clashes with our TD-authentic engineer),
Tiberium/Ore Growth Scale + Silo/Refinery Capacity dials, Nuke Tank, Turkey-bonus selector,
Jozef's Silver Funpark, Red USSR Flag art, Megamap/8-player (TD-side), Building Death
Announcements (TD), GDI9 Fix / MP Preplaced Unit Order / Disable MP Neutral Attacks
(TD campaign/MP-map specifics), Dr. Moebius idle quote.

Revisit any of these only at Luke's direction, most plausibly during the post-2.0 balance
pass (veterancy) or the campaign arc (mission-side fixes).

## 6. Credits / attribution to carry

When we ship ported features, credit in README/Workshop description per GPL + courtesy:
**cfehunter** (original CFE Patch), **Root-Core** (RA port), **ChthonVII** (CFE Patch Redux —
the bulk of what we're porting), plus feature-specific credits they carry (screaming_chicken
for several fixes, bleid for Pixel-Perfect Zoom if we take it).
