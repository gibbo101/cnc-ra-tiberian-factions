# Harvester docking rework — economy-balance plan (2026-06-17)

> **STATUS: PLAN ONLY. No code written this session** (Luke: "we won't be doing the work this
> session"). This is the design for the **economy-balance docking workstream** — the priority chunk
> of the larger harvester workstream (see `known-issues.md` + the harvester backlog). Implementation
> is a future session. All file:line refs verified against the tree at commit `3b601fa` (v2.4.1-dev).

## Goal
Equalise + speed up the harvester economy by **converging the RA harvester onto the TD attach-dock
mechanic**, so both factions dock the same way:

- **B2.** *(lead build item)* Make the RA harvester **dock and unload visibly** — approach → tip-up →
  billowing **dust-loop** while it dumps its load → drive out. **Target dock time = match the CURRENT
  TD dock time** (decided 2026-06-17 — see "Dock-time decision" below). This is the refinery-agnostic
  RA unload routine everything else reuses.
- **B3.** An engineer capturing the ore refinery **also captures the docked harvester**.
- **B4 (future, separate).** Allow **any harvester to use any refinery** (RA harv → TD ref via the RA
  routine). Notes at the end.
- **Bonus / tail tuning dial — halve dock time.** Originally B1. **DEFERRED to the END** (Luke,
  2026-06-17): we ship full-TD-time first (single-variable change), and only halve later if playtest
  says the global economy pace drags or dock-queue contention bites. One-line dial when wanted —
  `bdata.cpp:3944-3946` TDPROC dock-phase `Rate 4→2` + the matching RA loop speed. See the tail section.

Why this shape: TD already Limbos + attaches the harvester as cargo during unload, which is *exactly*
why "truck disappears" (B2) and "capture grabs the harvester" (B3) come for free in the TD path. The
work is bringing the RA harvester/refinery onto that same mechanic — with one real complication (the
RA refinery has no docking animation; see the constraint below).

### 🏛️ GOVERNING RULE (Luke, 2026-06-17): TD harv → TD ref is the *special case*; everything else = RA logic
The RA dock routine we build in B2 (approach → visible dust-loop → dump load → leave) is the
**default path for all unloading**. The existing **TD attach mechanic** (harvester Limbo'd as cargo,
*building* animates `ACTIVE/AUX1/AUX2`) is a **single narrow special case**, gated on
`*this == UNIT_TDHARV && refinery == STRUCT_TDPROC`. Any pairing that doesn't match falls through to
the RA routine — so RA-harv→RA-ref AND RA-harv→TD-ref both use the one RA path. This quarantines all
TD-specific docking behaviour to exactly one harvester/refinery pairing and keeps one well-tested
unload path for everything else.

---

## The two current mechanics, side by side

| Aspect | RA: UNIT_HARVESTER → STRUCT_REFINERY (current) | TD: UNIT_TDHARV → STRUCT_TDPROC (target model) |
|---|---|---|
| Dock cell | DIR_S of center — `building.cpp:435-437` | DIR_SW of center — `building.cpp:439-452` |
| Drive-in | turn DIR_W, stay on dock cell, tether — `unit.cpp:901-915` | turn DIR_SW, `Force_Track(BACKUP_INTO_REFINERY, Adjacent_Cell(Center,FACING_N))` drives INTO footprint — `unit.cpp:876-899` |
| Attach trigger | none — harvester stays visible on the dock cell | `Per_Cell_Process` cell-match → `RADIO_IM_IN` → `RADIO_ATTACH` → `Mark(MARK_UP); Limbo(); whom->Attach(this)` — `unit.cpp:1962-1996` |
| Building RADIO_IM_IN | `from->Assign_Mission(MISSION_UNLOAD); return RADIO_ROGER` — `building.cpp:326-329` | `Begin_Mode(BSTATE_ACTIVE); Assign_Mission(MISSION_HARVEST); return RADIO_ATTACH` — `building.cpp:331-345` |
| Who unloads | the **harvester** runs `Mission_Unload` — `unit.cpp:2947-2974` | the **building** runs `Mission_Harvest_TD` — `building.cpp:5400-5492` |
| Unload model | one-shot: `House->Harvested(Credit_Load())` when dump anim ends | bail-by-bail: `Offload_Tiberium_Bail()` per cycle — `unit.cpp:5530-5586` |
| Cadence driver | harvester dump anim (`Rule.OreDumpRate`, 22-frame `Harvester_Dump_List`) | **building animation** reaching its last frame sets `IsReadyToCommence` — `building.cpp:7560-7590` |
| Refinery anim | **NONE** — only static `BSTATE_IDLE` (1 frame) + `BSTATE_FULL` flashing lights. No ACTIVE/AUX1/AUX2 rows in `bdata.cpp` (`ClassRefinery`, line 1491). | full cycle — `bdata.cpp:3944-3948` (ACTIVE 12,7,4 / AUX1 19,5,4 / AUX2 24,6,4 / IDLE / FULL) |
| Harvester during unload | **visible**, animated tip-up | **invisible** (Limbo'd, attached cargo) |
| Capture grabs harvester? | NO — radio contact only, distance-gated path may eject it — `building.cpp:4260-4271` | YES — `Attached_Object()` → `tech->Captured(newowner)` — `building.cpp:4251-4253` |
| Exit | instant respawn at dock cell | `Exit_Object(Detach_Object())` → `Unlimbo` + `Force_Track(OUT_OF_REFINERY)` — `building.cpp:2720-2754` |

### ⚠️ The load-bearing constraint
The TD offload **cadence is driven by the building animation** (`IsReadyToCommence` is set when the
building's current anim sequence hits its last frame — `building.cpp:7560-7590`). **The RA refinery
has no docking animation frames at all** (confirmed: `bdata.cpp` has zero `STRUCT_REFINERY` anim rows;
the building uses only the default static IDLE). So we **cannot** simply route the RA refinery through
`Mission_Harvest_TD` as-is — its `Begin_Mode(BSTATE_ACTIVE/AUX1/AUX2)` calls have no frames to play,
so `IsReadyToCommence` would never fire on an animation basis and the offload loop would stall.

**Consequence (as resolved by the dust-loop design):** the RA path drives the offload cadence off the
**harvester's own dust-loop cycle** (`Rule.OreDumpRate`), NOT the building animation and NOT an
arbitrary timer — exactly mirroring how TD gates a bail per `AUX1` cycle, just moved onto the
harvester. The refinery stays static (no anim needed, none exists). The harvester is **never Limbo'd**
— it stays visible and animates the dust-loop. (Authoring HD refinery docking animation is the
alternative, but this project has repeatedly found custom HD building art infeasible —
`front-end-texture-meg-spike.md`, `launcher-new-asset-name-deadend`. Don't block on art.)

---

## Dock-time decision (2026-06-17): RA matches the CURRENT TD time — do NOT halve (yet)
**Decided with Luke.** The original B1 ("halve TD dock time") is **deferred to the end** as a tuning
dial. Rationale: whichever speed we pick, both factions equalise to the same dock time, so halve-vs-match
is **not** an inter-faction balance lever (that shift comes from equalising at all — handled in the D1
counterweight review). Halve-vs-match only controls **global economy pace** + **how hard RA's
instant-dump gets nerfed**. Matching the current TD time is the **single-variable change** (only RA's
economy moves; GDI/Nod stay exactly as balanced today), keeps TD-authentic feel, and stays re-tunable.

So **B2's target dock duration = the current TD unload time** (`bdata.cpp` TDPROC `Rate 4`, all phases
unchanged). Tune the RA dust-loop speed / bails-per-loop so a full RA load takes ~the same wall-clock
as a full TD load today.

**Re-evaluate the halve once ALL harvester upgrades are in** (test the whole economy holistically),
not piecemeal. See the tail tuning section.

---

## B2 — RA harvester docks + unloads visibly (dust-loop)  *(the main work / lead build item)*

> ✅ **CORE IMPLEMENTED + VISUALLY VALIDATED 2026-06-17 (Luke: "absolute PERFECTION").** RA harvester
> tips up once, then holds the bucket up looping the dust frames (SHP 104-110) while banking one bail
> per cycle, then lowers and drives off. Two key implementation facts learned: (1) the loop wrap +
> per-bail offload MUST live in `UnitClass::AI` (every frame), NOT `Mission_Unload` (only called every
> `Normal_Delay` ticks → stage overshoots into the down-ramp = bucket bobbing). (2) Animation/offload
> speed is a dedicated `DOCK_DUMP_RATE` const (=**3** ticks/frame) decoupled from global
> `Rule.OreDumpRate` (=2); at 3 a full 28-bail load ≈ 588 ticks ≈ current TD dock time (parity).
> Uncommitted on `main` (release gated on the whole workstream → v3.0). STILL TODO: B3 capture,
> multi-harvester queue re-test, save/load-mid-dock sanity, economy parity check in the holistic pass.

Build the **refinery-agnostic RA visible-unload routine**: the harvester approaches a refinery, plays
the tip-up, runs the billowing **dust-loop** while it dumps its load (one bail per loop cycle), then
lowers and drives out. It is **never Limbo'd / attached** — it stays visible the whole time. This is
the default unload path for everything except TD-harv→TD-ref (see the governing rule above).

### ⭐ DESIGN DECISION (Luke, 2026-06-17): visible dust-loop, NOT disappear
Supersedes the earlier "truck disappears into the refinery (Limbo)" framing. The RA harvester
**stays visible** and animates a **billowing-dust unload loop**, mirroring how TD animates the
*building* — we just move the animation onto the *harvester* (since the RA refinery has no anim
frames). Confirmed against the extracted HARV.SHP frames + GIF (`~/Desktop/ra-harvester-unload-frames/`).

Phase scheme over the dump frames (SHP index = dumplist value + 96):
- **Phase A — dock-in (once):** SHP **96 → 103** — bucket tips up.
- **Phase B — unload (LOOP):** SHP **104 → 109** repeated — the dust cloud billows out the side;
  this is RA's equivalent of TD's `BSTATE_AUX1` siphon loop. **Gate one `Offload_Tiberium_Bail()`
  per loop cycle** (loop speed = `Rule.OreDumpRate`), exactly as TD gates a bail per `AUX1` cycle.
  Loop until the load is empty → total unload time scales with load, no arbitrary timer.
- **Phase C — undock (once):** SHP **110**, then the down-ramp **102 → 96** — bucket lowers; then
  drive out.

This **resolves open questions #1 and #2** (offload model = bail-per-dust-loop-cycle; cadence =
`OreDumpRate`, tunable for the economy-balance target). The harvester is **never Limbo'd**, so:
- the refinery stays static (no art needed — correct, it has none);
- **B3 capture** must use the radio-contact special-case (`building.cpp:4260-4271`), NOT the free
  `Attached_Object` path — the harvester is tethered, not cargo. Slightly more code; the visible
  pour is the better look (Luke's call).

### ⚙️ Build B2 refinery-type-agnostic (so B4 is nearly free) — Luke, 2026-06-17
Write the RA dock + dust-loop unload as ONE routine parameterised by the **dock cell + refinery
pointer**, NOT hardwired to `STRUCT_REFINERY`. The RA harvester then has a single unload behaviour
(approach → dust-loop → dump load → leave) that works at any refinery; B4 just allows `STRUCT_TDPROC`
as a target and supplies its dock cell (DIR_SW). No second unload path, no TD attach/animation reused.
Avoid `if (*this == STRUCT_REFINERY)` assumptions inside the dock state machine.

### Lifecycle (the dust-loop design — harvester stays visible throughout)
1. **Approach / dock cell.** Keep RA's existing **DIR_S tether-dock** (`building.cpp:435`) — harvester
   docks beside the refinery and tethers; no drive-into-footprint, no `Per_Cell_Process` attach. The
   refinery pointer + dock cell are the only refinery-specific inputs (so the routine is refinery-
   agnostic for B4). *(Verify the RA refinery footprint + the harvester's docked cell.)*
2. **Phase A — tip-up (once).** Drive the existing dump animation
   (`Harvester_Dump_List`, `udata.cpp:58`; rendered at `unit.cpp:2323`, gated `!= UNIT_TDHARV`):
   `IsDumping = true; Set_Stage(0); Set_Rate(Rule.OreDumpRate)`, advance SHP **96 → 103** (bucket
   rises), then enter the loop.
3. **Phase B — dust-loop (repeat).** Loop SHP **104 → 109** (the billowing dust). **Each loop wrap =
   one `Offload_Tiberium_Bail()`** (`unit.cpp:5530`) → `House->Harvested(bail)`. Loop until the load
   is empty. Cadence = `Rule.OreDumpRate` (the balance dial; set so a full RA load ≈ a full TD load
   today). This is RA's equivalent of TD's `AUX1` siphon loop, on the harvester.
4. **Phase C — drive out (once).** Play SHP **110** → down-ramp **102 → 96** (bucket lowers), clear
   `IsDumping`, `Transmit_Message(RADIO_OVER_OUT)`, `Assign_Mission(MISSION_HARVEST)`, drive off. **No
   `Detach_Object`/`Unlimbo`** — it was never Limbo'd; it just leaves the dock cell.

### Touch list (B2)
- `building.cpp:326-329` — `STRUCT_REFINERY` RADIO_IM_IN: keep `from->Assign_Mission(MISSION_UNLOAD)`
  but have `Mission_Unload` run the new 3-phase dust-loop instead of the one-shot dump. (Stays
  `RADIO_ROGER`; no `RADIO_ATTACH` for the RA path.)
- `unit.cpp:2947-2974` — `Mission_Unload` UNIT_HARVESTER: replace the one-shot
  (`House->Harvested(Credit_Load())` at anim end) with the **Phase A→B→C state machine**; offload one
  bail per dust-loop wrap; refinery-agnostic (take the refinery + dock cell, no `STRUCT_REFINERY`
  hardcode).
- `unit.cpp:2323` render path — add the **loop** behaviour for Phase B (cycle the 104→109 sub-range)
  and the one-shot ramps for A/C. Today it runs `Harvester_Dump_List` straight through once.
- `unit.h` — small dock-phase state (phase A/B/C + loop bookkeeping). **Must serialise** (save/load).
- **No `Mission_Harvest_TD` / `bdata.cpp` change** — cadence is harvester-driven, refinery stays static.
- `Offload_Tiberium_Bail` (`unit.cpp:5530`) — reuse as-is (already drains Gems-then-Gold per bail).

---

## B3 — Engineer capture grabs the docked harvester

> ✅ **DONE + VALIDATED 2026-06-17 (commit `0c5a040`), capture only while unloading.** Key finding:
> during the B2 dust-loop the RA harvester had **no link at all** to the refinery — not cargo, radio
> contact dropped at unload start (the RA flow fired `RADIO_UNLOADED` immediately at backup time), and
> the booking-cleanup cleared `TiberiumUnloadRefinery` every frame (diagnostic confirmed
> `attached=NULL contact=NULL`). A position-scan workaround was prototyped then rejected in favour of
> the **proper fix: keep the harvester radio-tethered through the whole unload** (defer `RADIO_UNLOADED`
> from backup time to `Mission_Unload` Phase C). Then `BuildingClass::Captured` captures the
> radio-contact harvester directly, **gated on `IsDumping`** so only an actively-unloading harvester
> transfers (an approaching one in contact does not — Luke's constraint). Bonus: the dock now reads as
> occupied for the whole unload (helps the B5 multi-harvester queue) and the refinery shows BSTATE_FULL.

### Original plan (below) — superseded by the radio-tether fix above
**Revised by the visible-dust-loop decision:** the harvester is **never Limbo'd/attached as cargo**
(it stays visible + radio-tethered during unload), so the free `Attached_Object` capture path does
NOT apply here. Instead:
- Hook the **radio-contact** path in `BuildingClass::Captured` (`building.cpp:4260-4271`). It already
  finds the docked harvester via `Contact_With_Whom()`, but a distance check + `RADIO_NEED_TO_MOVE`
  can eject rather than capture. Add a **refinery special-case** (`*this == STRUCT_REFINERY`) that
  calls `tech->Captured(newowner)` unconditionally for a docked harvester. Small, low-risk.
- *(For comparison: the TD refinery DOES use cargo-attach, so a TDPROC capture already grabs the
  harvester via `building.cpp:4251-4253`. The RA path needs the radio-contact hook instead.)*

---

## Risks / cross-cutting
- **MP / lockstep determinism.** The dust-loop cadence is driven by `StageClass`/`Rule.OreDumpRate`
  (already deterministic, no RNG/wall-clock) — same machinery the existing one-shot dump uses, so
  low new risk. Keep the bail-per-wrap logic in the sim path.
- **Save/load.** The new dock-phase state (A/B/C + loop bookkeeping) must be added to `UnitClass`
  Save/Load and restore cleanly mid-unload.
- **Visual.** The harvester carries the unload visual (dust-loop), so no "static refinery" gap. A
  refinery-side smoke puff is optional polish, not needed.
- **Dock geometry.** Confirm the RA refinery footprint + the harvester's DIR_S dock cell.
- **Recovery interactions.** The v2.4.0 walled-field recovery (`Mission_Harvest` LOOKING retreat,
  blacklist) and `Find_Best_Refinery` load-balancing act *before* docking, so should be unaffected —
  but re-test the queue case (multiple harvesters → one refinery) since the unload now takes time
  (RA used to be instant).

## Test plan (after impl)
1. RA harvester docks: tip-up → dust-loop while unloading → lowers → drives out (stays visible).
2. Credits land correctly; total dock time ≈ a full TD load today (economy parity check).
3. Resumes harvesting; no stuck state.
4. Engineer captures refinery mid-unload → docked harvester changes owner (not ejected/destroyed).
5. Multiple harvesters at one refinery don't jam (now that RA unload takes time).
6. Skirmish soak (4 AI) — no desync, no save/load corruption mid-dock.

## Open questions for Luke (resolve before coding)
- ~~Offload model~~ — RESOLVED: bail-per-dust-loop-cycle (see the design decision above).
- ~~Freeze frame / refinery visual~~ — RESOLVED: visible dust-loop (96→103 in, 104→109 loop, 110+down-ramp out); refinery stays static.
- ~~Target dock duration~~ — RESOLVED: **match the CURRENT TD unload time** (do NOT halve). Tune via
  `Rule.OreDumpRate` and/or bails-per-loop so a full RA load takes ~the same wall-clock as a full TD
  load today. (Halve is the tail tuning dial, re-evaluated after all harvester work — see end.)
1. **Dock geometry** (only remaining) — keep RA's DIR_S tether-dock, or adopt TD's DIR_SW
   drive-into-footprint? With no Limbo, the tether-dock approach is simpler — harvester sits on the
   dock cell and loops. *(Lean: keep DIR_S tether-dock.)*

---

## B4 — Any harvester → any refinery

> ✅ **RA harv → TD ref DONE + validated 2026-06-17 ("perfect"), committed `d923511`.**
> Opened three gates so a `UNIT_HARVESTER` docks + dust-loops at a `STRUCT_TDPROC`: `Find_Best_Refinery`
> (RA harv accepts either refinery), `RADIO_CAN_LOAD` (TDPROC accepts RA harv), `RADIO_IM_IN` TDPROC
> (RA harv → `MISSION_UNLOAD` not `RADIO_ATTACH`; TD building anim NOT fired). RA harvester pulls up to
> the DIR_SW ramp and runs its normal dust-loop. Plus a TF_DEV `Can_Build` test allowance so any house
> can build both refineries (test only). **Reverse case (TD harv → RA ref) NOT started** — design
> decided: back in (visible, no Limbo) + dust AnimType overlay ("pipe siphon"), fallback = pull up +
> dust. See `harvester-docking-session-handover.md` for the resume checklist.

### Guiding principle (Luke, 2026-06-17, REVISED): **unload style follows the HARVESTER, not the refinery.**
- **RA harvester** (`UNIT_HARVESTER`): always runs its **visible dust-loop** (B2), at *any* refinery.
  The refinery stays static — at a TD refinery we deliberately **do NOT fire** its
  `BSTATE_ACTIVE`/`AUX1` dock animation. **Why:** that anim is tuned to the TD harvester's sprite +
  dock timing, and RA harv ≠ TD harv, so playing it for a visible RA harvester looks wrong (Luke).
  Letting the RA harvester's own dust-loop carry the visual avoids the mismatch entirely.
  Capture-while-unloading = radio-contact special-case (B3), consistent everywhere.
- **TD harvester** (`UNIT_TDHARV`): keeps the building-animates / harvester-hidden style at its TD
  refinery (unchanged). Capture = free via `Attached_Object` (`building.cpp:4251`).

### RA harvester → TD refinery (Luke's case) = CLEAN, harvester-driven
Harvester drives to the TD refinery's dock cell, stays **visible**, dust-loops, offloads a bail per
loop cycle, drives out. **Skip** the Limbo/`Attach` and **skip** `Mission_Harvest_TD`, so the TD
building never enters its dock animation. Work to enable:
- Relax type gating: `Find_Best_Refinery` (`unit.cpp:5440`), `RADIO_HELLO`/`RADIO_CAN_LOAD`
  (`building.cpp:282-295`) — currently `UNIT_TDHARV→STRUCT_TDPROC` + `UNIT_HARVESTER→STRUCT_REFINERY`
  only — to let `UNIT_HARVESTER` dock at `STRUCT_TDPROC`.
- Route `UNIT_HARVESTER` at a TDPROC into the B2 dust-loop dock state (NOT the TD attach path), using
  the TDPROC dock cell. No `RADIO_BACKUP_NOW`/`Per_Cell_Process` TD-attach changes needed for this
  direction (we're not attaching).

### Reverse case (TD harvester → RA refinery) — the LAST/lowest-priority pairing (Luke: "then we think about" it)
The one awkward pairing: TD harvester has no unload frames AND the RA refinery has no building
animation → neither actor can carry the visual. Options when we get to it:
1. **Static/timer fallback (baseline):** TD harvester parks at the RA dock cell, no animation, a timer
   offloads the bails. Functional but visually flat.
2. **Dock-cell dust ANIM overlay (nicer):** spawn a small passive dust/smoke `AnimType` at the dock
   cell during offload — independent of both sprites. Gives unload feedback; could be a general
   fallback for any animation-less unload.
**Rarity note (don't over-invest):** in our faction setup this almost never happens — GDI/Nod field
TD harvesters + TD refineries, Allied/Soviet field RA + RA. A TD harvester only reaches an RA refinery
via capture or a mixed/allied scenario. Static/timer fallback is likely sufficient; dust overlay is
optional polish. Capture-while-unloading here = radio-contact special-case (same as B3), unless we
choose to Limbo it (then cargo path) — decide if/when we build it.

Then the dock-contention / queue-park improvements (backlog item B5) apply uniformly. Not in this chunk.

---

## TAIL TUNING DIAL — halve dock time (was B1; deferred to the END)
**Decision (Luke, 2026-06-17):** ship full-TD-time first; **re-evaluate halving only once ALL harvester
upgrades are in**, so the whole economy is tested holistically rather than piecemeal. If the global
pace drags or dock-queue contention bites, halve both sides in one pass:
- TD: `bdata.cpp:3944-3946` TDPROC `BSTATE_ACTIVE/AUX1/AUX2` `Rate 4→2` (AUX1 = dominant per-bail).
- RA: halve the dust-loop cadence to match (`Rule.OreDumpRate` and/or bails-per-loop).
Keep both in lockstep so the factions stay equal. Trivial, reversible, data-side.

---

## ⛴️ RELEASE PLAN — next release is v3.0, gated on the WHOLE harvester workstream (Luke, 2026-06-17)
**No more releases until all harvester work is done.** The full harvester overhaul (recovery already
shipped in 2.4.0, plus the docking rework B1–B4, target claiming / fleet spread, dock contention,
reachability edge cases, harvesters-not-blocked-by-infantry, universal idle rescan, economy balance)
ships together as a **major v3.0** — milestone-scale per the semver rule (`version_high = 3`). Local
dev stays on the 2.4.x dev bump until then; no interim Workshop pushes. Re-test the halve dial as part
of the pre-3.0 holistic economy pass.
