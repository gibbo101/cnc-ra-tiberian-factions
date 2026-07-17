# AI Upgrade Plan — the post-v4.0 milestone

**Status: DESIGN + RESEARCH COMPLETE (2026-07-17). Not yet started.** This is the master plan
for the AI-focus milestone, assembled from Luke's wishlist session (2026-07-16/17), the
re-audit of `ai-improvements.md` (all statuses verified against HEAD), six targeted research
agents, and the AI Boost 3.2 reference source (`reference/ai-boost2/`, GPL, licence verified).

Companion docs: `ai-improvements.md` (problem inventory + re-audit banner),
`chokepoint-reservation-design.md` (pathfinding record), `feedback-difficulty-philosophy`
(memory: behavioural difficulty only, never stat/economy multipliers).

---

## 1. Vision and principles

1. **One AI brain.** The AI is not "a Soviet AI"; it is a brain that asks *what do my
   buildings let me build* (capability from ownership) and *what have I seen* (intel from
   scouting). Faction identity lives in the building lineage, not the house.
2. **Behavioural difficulty, never cheats.** Easy/Medium/Hard = per-AI IQ + behaviour gates.
   No stat multipliers, no economy boosts, no production hacks (explicitly rejecting AI
   Boost's levers). Removing existing AI cheats (fog x-ray, all-factories parallel build) is
   part of the milestone.
3. **Fairness pays for smartness.** Every cheat removed is compensated by a real capability
   (scouting replaces x-ray; better strategy replaces parallel production).
4. **Tunable dials.** New mechanics (directional armour, staging thresholds, attack cadence)
   ship with rules.ini dials so playtest tuning needs no rebuilds.
5. **Deviations from TD-authentic are documented** in `balance-deep-dive.md` as they land.

## 2. Locked design decisions (Luke, 2026-07-16/17)

### 2.1 Faction-specific buildings + heritable capture-tech (the enabler)
- **Faction-specific (produces units):** Construction Yard + MCV (Allied/Soviet/GDI/Nod — 4
  each), War Factory (4), Helipad (4), plus the already-split barracks, naval yards, tech
  centers, airfields.
- **Side-pair shared (unlocks tech, no cross-substitution):** Radar Dome (Allies/Soviets) vs
  TD Comm Center (GDI/Nod). A captured TDHQ does NOT satisfy the Allied radar prereq.
- **Fully generic (any faction's version satisfies the prereq):** power plants, refineries
  (RA and TD interchangeable — a GDI refinery unlocks the Allied WF), repair bay, ore silos,
  Missile Silo, and the transport helicopter (buildable at any helipad).
- **Heritable lineage:** a captured building produces ITS faction's things — including its
  faction's buildings (captured Allied ConYard → Allied building tree → Allied WF → Allied
  units + Allied MCV). Vanilla already keeps a *captured* factory producing its side; the
  split makes the lineage survive new construction.
- **Helipads:** production is faction-specific, operations universal — ANY helicopter may
  land/rearm/repair at ANY pad (dock dispatch = one equivalence class).
- **Prereq liveness:** a unit is buildable iff its prereq buildings EXIST RIGHT NOW (alive,
  powered or not). Selling or losing a prereq revokes sidebar entries immediately (fixes the
  sell-the-tech-center exploit). In-production items finish and deliver.
- **Owner= side-gating on units effectively retires** in favour of prereq-building gating.
- Hover/sidebar names ("GDI Construction Yard", "Soviet War Factory") via ModText.csv (proven).

### 2.2 Difficulty frame
- **Easy = today's AI** + all universal capability additions (naval, transports, pathfinding,
  eco fix — they're mod features, not smartness).
- **Medium/Hard = IQ-driven behaviour tiers** (see §5). Tactical smarts (attack-move waves,
  blob staging, adaptive defence placement) start at Medium; gang-up, counter-building,
  multi-pronged attacks, transport invasions, flanking micro at Hard. (Straw-man split —
  final per-behaviour tiering happens during implementation review.)
- **Fog x-ray removal is universal** (all tiers) — see §3 W1.

### 2.3 Directional armour
- Vehicles take bonus damage from rear-arc hits (design intent: pay Nod's mobility — bikes,
  stealth tanks — against heavies; synergises with Stealth Generator ambushes).
- Ships as a `[DirectionalArmor]` rules block: Enabled, RearArcDegrees, RearMultiplier,
  optional Side tier, FrontMultiplier, AffectVessels, ExemptUnits. Numbers are playtest-tuned,
  NOT fixed at design time (Luke: "important to tune this right").
- **Reverse move is a decision-gated companion** — revisit AFTER directional-armour playtests;
  trigger = "retreat feels too punishing at sane dials". It's locomotion surgery (drive.cpp
  facing/travel decoupling) + modifier-click input (no new launcher hotkeys — W5 wall), so it
  is NOT bundled.

### 2.4 Wishlist behaviours (all in scope)
- AI attacks stage + advance as a blob with attack-move (not a unit stream).
- Smart defence placement (threat-direction-aware; no corner spam); refineries near ore;
  power in core.
- Proactive radar (shipped f8351de) and proactive naval — but naval only after a WATER
  EVALUATION (pond → don't bother).
- GDI/Nod early-eco fix (comm center/repair bay arrive too early; Temple starvation bug —
  see todo.md 2026-07-16 entry).
- Stage-aware unit values: light/fast units score as scouts early, decay as combat picks
  later; composition scored against SCOUTED enemy composition (no hardcoded faction doctrine).
- Sea transports: AI ferries ground forces across water, smartly.
- Allied AI coordination (scope = Claude's call, see §3 W6).
- Chokepoint reservation pathfinding ("TS retrofit"): reservation table + scatter-the-blocker,
  JPS optional follow-on, OpenRA cooperative pathfinder as reference. Subsumes the open gw==2
  head-on and stuck-in-base loose ends.

## 3. Workstreams

### W1 — Foundations: fairness + engine fixes *(everything else builds on this)*
1. **Engine bug fixes** (Tier-1 quick wins, all verified OPEN at re-audit):
   `Greatest_Threat` bestval never updated (techno.cpp:2359-2421 — broken target scoring
   engine-wide); power-urgency `|` typo (house.cpp:5762); GOINGTOIDLE fall-through
   (unit.cpp:4334); A-New-1 reinforcement idle (unit.cpp:6737 pattern, low).
   **STATUS 2026-07-17: first three DONE** (build-verified, awaiting soak). Power-urgency
   check rewritten, not just `|`→`&`: chronosphere test was meaningless either way (AI never
   builds one; no STRUCTF bits exist past 32 anyway) — now a generic "armed IsPowered
   building owned" scan over ActiveBQuantity (catches Tesla today; auto-extends, see §9.5). GOINGTOIDLE
   resolved (dead REPAIR/HUNT branch deleted, NOT enabled: HUNT = weaponless suicide order,
   and our reworked unit Mission_Repair docks refineries not repair bays) then upgraded
   (Luke, same day): idle harvesters now retreat to guard beside Find_Best_Refinery
   (Nearby_Location spread, 4-cell already-home guard) instead of parking in the open;
   no-refinery fallback = guard in place. Human + AI both; any order overrides. A-New-1 SKIPPED for now: original audit detail not preserved,
   pattern also in infantry/vessel Read_INI, zero impact on current map pool (skirmish maps
   carry no pre-placed units) — re-derive intent before touching.
2. **Per-house INTEL LAYER** — "what has this house discovered + where last seen". Remaster
   already tracks per-player shroud; route ALL AI reads through it: target evaluation
   (techno.cpp:1713 fog gate), superweapon aiming (house.cpp:3180 — currently fog-blind, and
   our TD Ion/Nuke dispatch inherits it), attack-destination picking, and every NEW system
   (counter-building, naval-war detection) so they are born fair. Last-seen memory: nuking
   where the WF *was* is smart, not cheap.
3. **Scouting behaviour** — cheap fast units get a scout job (the stage-aware value model
   feeds this); IQ-gated intensity (Easy lazy, Hard keeps the map warm).
4. **Reservation-table pathfinding** — cell reservations at tick T + scatter-the-blocker;
   treat reserved cells as soft obstacles; JPS follow-on optional. Read OpenRA
   (`OpenRA.Mods.Common/Traits/World/PathFinder*.cs`, MIT) before implementing. Closes the
   gw==2 + stuck-in-base threads.
5. **Primary-factory production (AI Boost port + generalize)** — AI builds one order per
   category through a primary factory (like humans) instead of parallel-building from every
   factory. Removes a vanilla cheat AND fixes the FactoryMax=20 heap exhaustion behind
   late-game "sidebar can't build" (rules.cpp:237). Real AI nerf → pairs with W3.

### W2 — Faction separation + buildability rework *(the one-brain enabler)*
Engineering survey COMPLETE (2026-07-17). Load-bearing findings:
1. **Capture inheritance is already free.** The sidebar buildable list is computed per
   FACTORY BUILDING via `Update_Buildables` (building.cpp:3390) calling
   `Can_Build(type, this->ActLike)` — the BUILDING's ActLike, not the owner's. A captured
   faction building already offers its faction's roster (today's TDWEAP/TDHPAD prove it).
   Faction-tagged types with pinned ActLike (building.cpp:2008-2022 Unlimbo pinning; 4
   factions map cleanly onto GREECE/USSR/GOOD/BAD placeholders) make lineage automatic —
   NO capture-specific code.
2. **The prereq-liveness gap is ONE SITE:** `sidebarglyphx.cpp:474` — the every-frame
   sidebar Recalc evicts via `Who_Can_Build_Me(intheory=true, legal=false, …)`, and
   `legal=false` short-circuits the prereq check (object.cpp:2411). Fix = make eviction
   prereq-aware (pass legal or add a Can_Build gate with the BUILDING-side ActLike so
   capture-offered cameos aren't wrongly evicted). Verify the re-offer path sets
   IsRecalcNeeded on prereq re-acquisition. NOTE: this changes behaviour for ALL existing
   units too (players will notice — desired, it's the exploit fix).
3. **Owner= is not deleted — it's widened.** Keep Ownable broad (all four factions on
   units); the faction-specific PREREQ building is the sole discriminator. Every new
   faction prereq token needs an explicit Can_Build remap `continue` (house.cpp:1036-1196
   is the template; the generic any-of clauses for power/refinery/repair are already
   there). Forgetting one = silently unbuildable (known trap).
4. **Site fan-out:** ~100 hardcoded dispatch sites across CONST(27+27)/WEAP(24+22)/
   HELIPAD(37+28)/MCV(26+17) enum pairs. RECOMMENDATION: refactor the hottest paths to
   role flags (IsConstructionYard/IsWarFactory/IsHelipad/IsMCV) during Phase 2 — with 4×
   enums the refactor pays for itself vs N-way lists. MCV→ConYard mapping is already
   centralized in `MCV_Deploy_Building` (unit.cpp:124).
5. **Helipad dual nature:** universal landing = extend the `Find_Docking_Bay` shadow-match
   (techno.cpp:6899) to all 4 pads (+ aircraft.cpp:4338); faction production = the
   per-pad Update_Buildables/Who_Can_Build_Me gates stay specific. Only place needing
   two-headed handling.
6. **Also:** bump `Rule.FactoryMax` (captured multi-faction bases run more concurrent
   factories); skirmish MCV spawn 4-way switch at scenario.cpp:3530 + fold in the
   known-issues "starting-units bonus gives RA units" fix (same region); heap headroom
   exists (STRUCT_COUNT+50); mid-game saves break per enum addition (skirmish-only risk).
**Internal phasing:** (a) prereq-liveness fix FIRST, standalone + testable; (b) ConYard+MCV
split (re-split shared TDFACT/TDMCV into GDI/Nod + add Allied/Soviet, incl. spawn work);
(c) War Factory; (d) Helipad last (dual-nature). Role-flag refactor lands with (b).

### W3 — The brain: build planner + placement
1. **Staged build planner** replacing the shouting-urgency-slots model: coherent opening
   (economy first — fixes GDI/Nod eco passivity), then production, tech when affordable
   (fixes Temple starvation: power-gate + MEDIUM-starvation, house.cpp:6815/6607), defence
   budgeted by threat.
2. **Placement intelligence** (research complete — agent report, §7):
   - Threat-aware defence placement: bias zonerating toward LAZone (last-attacked zone —
     tracked at building.cpp:2071, never consulted!) + enemy-direction octant. ~30-50 lines
     in Find_Build_Location (house.cpp:5191). Kills corner spam (random-zone fallback at
     house.cpp:5267 is the culprit — armed buildings only ever rate zones; unarmed buildings
     place RANDOMLY).
   - Refinery-near-ore: new tiberium-proximity scan, special-case before the zone loop.
   - Power/economy in ZONE_CORE instead of Random_Pick.
   - Optionally revive AI_Base_Defense (#ifdef NEVER, house.cpp:6169) for defence rebalancing.
   - **Own-unit ring stunts the base (Luke live observation, confirmed in code 2026-07-17):**
     Flush_For_Placement (building.cpp:3349 call, bdata.cpp impl) only scatters allied foot
     units with NO NavCom (stuck-while-pathing units never flushed), does nothing for other
     occupiers (retaliation commented out), and ANY occupied footprint cell defers the whole
     placement to a retry — dense unit rings make the footprint never simultaneously clear →
     placement starves. Fix here: scatter own units regardless of NavCom, and fall back to an
     alternate Find_Build_Location after N failed flushes. Scatter-on-launch (Phase 0) thins
     the ring incidentally; watch during soak whether the GUARD_AREA garrison worsens it.
   - NOTE: AI Boost's placement is byte-identical to vanilla — this would be a first for the
     Remastered ecosystem.
3. **Stage-aware unit valuation + counter-composition** (vs scouted intel only).
4. **Counter-building** (AI Boost mechanism, generalized 4-faction, intel-filtered).
5. **Power management** (sell-excess / build-ahead margins — AI Boost pattern).

### W4 — Attack quality
Research complete (agent report, §7). Two routes for staging-then-blob:
- **Route A (preferred, higher fidelity):** revive the TeamClass campaign machinery — the
  gather/formation/blob logic ALREADY EXISTS (Coordinate_Regroup team.cpp:1729, full-strength
  gate team.cpp:626, lagger-wait Coordinate_Move team.cpp:1862, Coordinate_Attack
  team.cpp:1626). Drop the GAME_NORMAL recruit gate (team.cpp:665, P14), synthesize skirmish
  attack-TeamTypes with computed staging waypoints (near enemy base — skirmish has no
  authored waypoints; this is the new work). Aircraft fold in automatically (aircraft.cpp:724
  team guard).
- **Route B (fallback, coarser):** staging inside AI_Attack (house.cpp:5909): MOVE to staging
  cell → GUARD_AREA until threshold → release as attack-move.
- **AI attack-move:** set `AttackMove=1` + `RememberedNavCom` on dispatch — the whole player
  state machine (CFE port) is input-agnostic (techno.cpp:8073+). Audit stray IsHuman guards
  (infantry.cpp:2659).
- **AI Boost borrowings:** scatter-on-launch (unsticks waves), defence-gated send-percentage,
  target-variety rolls, special-unit handling in waves (medics guard, spies always go).
- **Enemy re-evaluation** (P16, house.cpp:5472) so the brain retargets.
- Decision point: spike Route A first; fall back to B if campaign TeamTypes misbehave in
  skirmish soak.

### W5 — Capabilities
1. **Naval AI + water evaluation** — research COMPLETE (2026-07-17):
   - **Build-out is unblocked and low-risk:** all production plumbing (BuildVessel →
     Suggest_New_Object → yard factory tick) already works; the ONLY missing piece is a
     skirmish branch in AI_Vessel (replace the IsBaseBuilding clear at house.cpp:7195 —
     model on AI_Unit's weighted-random block + the A-10 per-airfield gate; Can_Build gives
     faction rosters automatically). AI Boost filled the exact same empty block — proven
     pattern.
   - **Water evaluation is cheap + novel:** reuse `Zones[MZONE_WATER]` connected-region ids
     (stable all match — zones ignore buildings); add a per-zone SIZE histogram (Zone_Span
     already computes the count and discards it) + a one-pass building→water-zone touch
     bitmask ("which houses are coastal on this water"). Pond test + does-it-reach-the-enemy
     test = two lookups. Refresh with Zone_Reset. Nobody has this (AI Boost's detection is
     building-count only, and fog-blind — ours goes through the W1 intel layer).
   - **Yard placement gap:** Find_Cell_In_Zone already honours Legal_Placement (WaterBound →
     coastal water cells only) but searches rings around the LAND base center — on maps
     where the base isn't near shore it can silently fail. Bias yard placement toward the
     nearest coastal cell of a water zone the house borders (W3.2 companion).
   - Naval build gates: don't out-build the enemy navy (intel-filtered), naval-war detection
     rescales limits (AI Boost tiers as reference).
2. **Sea transport ferrying** — research COMPLETE: the whole mechanism exists as campaign
   primitives — TMISSION_LOAD's MISSION_ENTER + RADIO_DOCKING boarding handshake
   (team.cpp:2185, foot.cpp:1811, vessel.cpp:1514), Desired_Load_Dir as the "can I
   load/land here" oracle (vessel.cpp:1722), MISSION_UNLOAD state machine (vessel.cpp:1868).
   Minimal skirmish ferry controller = hand-rolled sequence (pick LST + units → ENTER →
   sail to landing cell chosen via the water-zone touch data → UNLOAD), hooked like our
   existing custom controllers (harvester watchdog, Obelisk-sub charge). No reference
   precedent (AI Boost wishlisted it, never built it) — original work. NOTE: the shared
   transport is the RA LST (VESSEL_TRANSPORT, fully wired); the parked TDLST hull is NOT
   wired into the transport switches (vessel.cpp:357/1613/1885) — wire it only if revived.
3. **Superweapons for RA factions:** Iron Curtain + Chronosphere AI dispatch + AI-aware
   targeting (P3b/3c — currently reads the mouse; AI Boost has working IC/Chrono usage as
   reference); parabomb ungate (P3d) — delivers the MISSED Soviet parabombs item from v4.0.
4. **Special units:** Spy/Thief/Dog AI production + usage (currently Value=0, never built);
   AI Boost engineer/spy/MAD-tank handling as reference.

### W6 — Team coordination (v1 scope, Claude's call)
All four items need ZERO new inter-house plumbing (read surface verified: Enemy, Center,
Attack timers, LATime/LAEnemy, IsAlerted all public):
1. Gang-up: Computer_Paranoid skirmish ungate behind a lobby-respecting knob (P11).
2. Shared targeting: allied AIs bias Enemy toward a common target (Expert_AI tick).
3. Aligned timing: allies read each other's Attack countdown, nudge waves to land together.
4. Help a sieged ally: redirect next wave to ally's Center/LAEnemy on distress.
Team INTEL sharing rides the W1 intel layer (allies union their discovered sets — mirrors
human ally shared vision). Pincers/role-splitting = Hard-tier follow-on, not v1.

### W7 — Difficulty plumbing
Research complete (IQ map, §7): per-AI IQ from lobby at dllinterface.cpp:1272 (+ mirror sites
queue.cpp:3273, scenario.cpp:3016, saveload.cpp:1587); do NOT route through Assign_Handicap
(stat biases). **Critical prerequisite: lower Rule.IQProduction below 5** or sub-max AIs stop
base-building entirely (house.cpp:1262). Tier map: Easy=IQ3 (no supers/aircraft-AI/roam),
Medium=IQ4 (+supers, aircraft, guard-area, content-scan), Hard=IQ5 + the new smart behaviours.
New behaviours get their own IQ thresholds. IQSellBack quirk: it's actually a TechLevel gate
(building.cpp:7949) — don't treat as IQ tier.

### W8 — Combat mechanics
Directional armour per §2.3 (research complete: hook techno.cpp:4576 after ArmorBias, before
Modify_Damage; ~70-110 lines, 3 files, no per-object state, lockstep-PASS; directionless
damage auto-excluded via source==NULL/forced gates + warhead opt-outs). Reverse move:
decision-gated (§2.3).

## 4. What's already fixed (do not redo)
Radar/tech progression (f8351de), harvester intelligence arc (threat-aware fields 2f80f76,
load-balanced refineries 5e14772, anti-stuck watchdog, IsTiberiumShort reset), Repair Bay
queue (TDFIX), TD Ion/Nuke auto-fire, building Points targeting values (ai-targeting.md OBE),
A*/attack-move/chokepoint give-way/group-spread (v2.2-2.3), Session.Type sweep confirmed NO
undiscovered high-severity gates (audit 2026-07-17).

## 5. Difficulty tier matrix (initial)

| Behaviour | Easy | Medium | Hard |
|---|---|---|---|
| Base-building, economy, army (current) | ✓ | ✓ | ✓ |
| Universal capabilities (naval+water eval, transports, eco fix, pathfinding, fair fog) | ✓ | ✓ | ✓ |
| IQ gates (supers, aircraft AI, guard-area roam, content-scan) | ✗ (IQ3) | ✓ (IQ4) | ✓ (IQ5) |
| Attack-move waves + blob staging | ✗ | ✓ | ✓ |
| Threat-aware defence placement | ✗ (random, as today) | ✓ | ✓ |
| Counter-composition / counter-building | ✗ | partial | ✓ |
| Scouting intensity | lazy | moderate | active |
| Gang-up, aligned waves, help-ally | ✗ | ✗ | ✓ |
| Multi-pronged attacks, transport invasions, flank micro | ✗ | ✗ | ✓ |

## 6. Sequencing

- **Phase 0 (small, ships early):** W1.1 bug fixes + AI Boost cheap borrowings (scatter-on-
  launch, send-percentage) + Temple-starvation/eco build-order fix (verify with dev-build
  diagnostics first — todo.md bug entry).
  **STATUS 2026-07-17: code COMPLETE, all build-verified.** W1.1 done (see status note in
  §3 W1.1). Scatter-on-launch + send-percentage ported into AI_Attack (harvesters exempt
  from scatter — dock-approach hazard; defences counted generically via armed-building scan;
  thresholds 4/8 → 80/95/100%, internal constants not user INI; unsent armed units stand
  GUARD_AREA home guard; TDE6 joins RENOVATOR in the engineer hunt clause — faction parity).
  Build-choice diagnostic upgraded to TF_AI_DIAG v3 (TDTMPL/TDEYE/TDSTEAL watch-list,
  PF<1 gate flag, per-cycle candidate POOL + WIN dump in MOD_DEBUG_AI.txt). REMAINING:
  run the Temple-starvation diagnostic session + Phase 0 soak/playtest gate.
- **Phase 1 (infrastructure):** W1.2 intel layer + W1.3 scouting; W7 difficulty plumbing +
  IQProduction retune; W1.5 primary-factory.
  **STATUS 2026-07-17: code COMPLETE on branch `ai-phase1`, all build-verified, UNSOAKED.**
  Four commits, one per workstream. W7: lobby difficulty -> IQ tier (Easy=3/Normal=4/
  Hard=MaxIQ) via TF_AI_IQ_From_Difficulty; CNC_Set_Difficulty un-gated for skirmish
  (stores Scen.CDifficulty + retro-applies, TF_AI_DIAG-logged); falls back to vanilla
  MaxIQ until the client actually sends a value; stat handicaps stay 1.0x; IQProduction
  5->3 (engine + rules.ini). W1.5: Factory_AI gate = one AI order per factory category
  (kills the parallel-build cheat, which was quadratic - Time_To_Build already divides
  by Factory_Count - and the FactoryMax heap exhaustion). W1.2: per-house discovery
  recorded for AI houses in IsDiscoveredByPlayerMask (Revealed rework); Evaluate_Object
  + Special_Weapon_AI (all six supers) gated on own-house discovery; Take_Damage reveals
  the attacker to the victim's house. Residual: once-seen enemy UNITS stay evaluable
  while fogged (mask is positionless; buildings fully fair). W1.3: blind Mission_Hunt
  ground units probe start-location waypoints (unmapped-first, nearest-first; Easy stops
  after first enemy-building contact). VERIFY NEXT: desktop diagnostic run must confirm
  (a) the client sends CNC_Set_Difficulty in skirmish (grep MOD_DEBUG_AI.txt for it,
  else Hard/Easy tiers never engage and everything runs vanilla-MaxIQ), (b) AI still
  finds + attacks the enemy under fair fog, (c) no early-game stall.
- **Phase 2 (the enabler):** W2 faction separation + buildability (big, independent of 0/1 —
  can run in parallel if sessions allow).
- **Phase 3 (the brain):** W3 build planner + placement; W4 attack quality (Route A spike
  first).
- **Phase 4 (capabilities):** W5 naval → transports → RA supers → special units; W6
  coordination; W8 directional armour (can land any time after Phase 0 — independent).
- **Pathfinding (W1.4 reservation table):** its own track; schedule around the behaviour
  phases (highest-risk drive.cpp work — don't overlap with W4 soak).
- Every phase: dev-build diagnostic logging in from day one (logs-first rule), desktop
  soak matches, playtest gates before the next phase.

## 7. Research reports (agent findings, 2026-07-17)
All six research agents complete; findings integrated with anchors into the workstream
sections above: building placement (W3.2), Session.Type + IQ audit (W1.1, W7, §4),
attack/coordination/attack-move (W4, W6), directional armour (W8), naval/transports/water
(W5.1/W5.2), faction-separation engineering survey (W2).

## 8. References + attribution
- `reference/ai-boost2/` — AI Boost 3.2 (Bast75 & xXMini FrankiXx, GPL v3 + EA terms,
  licence verified 2026-07-16). Port sources: scatter-on-launch, send-percentage, IC/Chrono
  usage, special-unit handling, counter-building, naval-war detection, primary-factory.
  **Credit both authors in Workshop acknowledgements when the first port ships** (CFE authors
  already credited; their fork bundles CFE 1.8 — attribute per-feature).
- OpenRA pathfinder (MIT) — design reference for W1.4.
- `AIBOOST.INI` — reference for which dials modders/players expect; our policy remains lobby
  difficulty + rules.ini dials, no separate user INI.

## 9. Open decisions
1. Blob route A vs B — after the Route-A spike.
2. Reverse move — after directional-armour playtests.
3. Free-helicopter-with-pad rule under faction pads — trivially "pad's own faction's bird".
4. Per-behaviour difficulty tier assignments — review pass during implementation.
5. ~~Should TD defences be `Powered=true`?~~ **RESOLVED 2026-07-17** (TD-source-verified,
   Luke correctly refuted the "no shutdown in TD" claim): TD hard-gates AGT fire
   (building.cpp:3128 STRUCT_ATOWER check) and Obelisk charging (building.cpp:1022, charge
   dumped on power loss) at Power_Fraction < 1; SAM has no gate. Our TDOBLI was ALREADY
   TD-correct via Charges=yes → Charging_AI (identical gate + charge-dump semantics);
   fix applied = `Powered=true` on [TDATWR] only; TDSAM stays unpowered (TD-authentic).
   Do NOT add Powered to TDOBLI: TD gates only the charge chain, and doubling the gate
   adds nothing. AI note: Check_Build_Power's armed-powered-building scan now fires for
   GDI (AGT) and Soviets (Tesla) once W3 revives the strategy layer.
5. Milestone version: presumably v5.0 (major). Confirm with Luke before first release from
   this line.
