# AI Upgrade Plan

**Status:** Design, partly shipped. In 4.1.0: Phase 0 and 1 (engine fixes, fair fog, scouting, IQ tiers,
primary-factory production) and the W2 faction split. In 5.0.0: W2.9 role counting, W3 economy pacing and base
placement, the W4 value-and-stage wave floor with staging and Hard attack-move, W5.1 naval and W5.2 ferrying. In
5.7.0 the main TF AI behaviours (fair fog and scouting, attack waves, naval, early radar) got switches, and Classic
AI puts back Red Alert's own, base placement and selling included (`player-settings.md`).
**Open:** W2.9's cross-lineage builder and home-faction weight; W3 placement intelligence, tech ordering and
counter-play; W4 Route A; Red Alert superweapon AI and special units (W5.3, W5.4); W6 coordination; W8 directional
armour; the W1.4 reservation table. Staging and economy pacing have not been checked in a 1v1 Hard game against a
human (`todo.md`). The measured A/B behind the 5.0.0 work is `docs/ai-ab-2026-09-02/results.md`: economy was never
the regression; the count-only wave floor and starved defences were.

> **Timing note for every dial in this plan:** dials are written in sim ticks
> (`TICKS_PER_SECOND` = 15) but the Remastered sim runs ~33 frames per real second at the
> speed the game is played at, so "2 sim-minutes" is ~55 real seconds. Design in sim-minutes, read logs
> in frames, and do not expect a 20-minute decay to fire at real minute 20.

The plan for TF's AI. The problem inventory it builds on is `ai-improvements.md`; the pathfinding record is
`chokepoint-reservation-design.md`. The reference source is AI Boost 3.2 (`reference/ai-boost2/`, GPL, licence
checked). Difficulty stays behavioural: never stat or economy multipliers.

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

## 2. Locked design decisions

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
- **Easy = the base AI** + all universal capability additions (naval, transports, pathfinding,
  eco fix — they're mod features, not smartness).
- **Medium/Hard = IQ-driven behaviour tiers** (see §5). Tactical smarts (attack-move waves,
  blob staging, adaptive defence placement) start at Medium; gang-up, counter-building,
  multi-pronged attacks, transport invasions, flanking micro at Hard. This is a straw-man split;
  the final per-behaviour tiering is set as each lands (§8 item 4).
- **Fog x-ray removal is universal** (all tiers) — see §3 W1.

### 2.3 Directional armour
- Vehicles take bonus damage from rear-arc hits (design intent: pay Nod's mobility — bikes,
  stealth tanks — against heavies; synergises with Stealth Generator ambushes).
- Ships as a `[DirectionalArmor]` rules block: Enabled, RearArcDegrees, RearMultiplier,
  optional Side tier, FrontMultiplier, AffectVessels, ExemptUnits. Numbers are playtest-tuned,
  NOT fixed at design time.
- **Reverse move is a decision-gated companion** — revisit AFTER directional-armour playtests;
  trigger = "retreat feels too punishing at sane dials". It's locomotion surgery (drive.cpp
  facing/travel decoupling) + modifier-click input (no new launcher hotkeys — W5 wall), so it
  is NOT bundled.

### 2.4 Wishlist behaviours (all in scope)
- AI attacks stage + advance as a blob with attack-move (not a unit stream).
- Smart defence placement (threat-direction-aware; no corner spam); refineries near ore;
  power in core.
- Proactive radar (shipped) and proactive naval — but naval only after a WATER
  EVALUATION (pond → don't bother).
- GDI/Nod early-eco fix (comm center/repair bay arrive too early; the Temple starvation is fixed by
  starvation ageing in the build choice, Phase 0 in §6).
- Stage-aware unit values: light/fast units score as scouts early, decay as combat picks
  later; composition scored against SCOUTED enemy composition (no hardcoded faction doctrine).
- Sea transports: AI ferries ground forces across water, smartly.
- Allied AI coordination (scope in §3 W6).
- Chokepoint reservation pathfinding ("TS retrofit"): reservation table + scatter-the-blocker,
  JPS optional follow-on, OpenRA's pathfinder as reference (said to be occupancy plus local avoidance plus repath;
  not checked against OpenRA's source). Subsumes the open gw==2
  head-on and stuck-in-base loose ends (`known-issues.md`).

## 3. Workstreams

### W1 — Foundations: fairness + engine fixes *(everything else builds on this)*
1. **Engine bug fixes, shipped in 4.1.0:** `Greatest_Threat`'s `bestval` (broken target scoring engine-wide,
   `ai-improvements.md` Problem 7); the power-urgency `|`; the `GOINGTOIDLE` fall-through.
   - The power-urgency check is rewritten, not just `|`→`&`: the Chronosphere test was meaningless either way (the
     AI never builds one, and no `STRUCTF` bit exists past 32), so it is now a scan of `ActiveBQuantity` for an
     armed, powered building the house owns (the Tesla today; it extends itself, §8 item 5).
   - `GOINGTOIDLE`'s dead REPAIR/HUNT branch is deleted, not enabled: HUNT is a weaponless suicide order, and TF's
     reworked unit `Mission_Repair` docks refineries, not repair bays. An idle harvester instead retreats to guard
     beside `Find_Best_Refinery` (`Refinery_Waiting_Cell` spreads them; already within 4 cells it guards in place),
     and with no refinery it guards in place. Human and AI alike; any order overrides.
   - **A-New-1 (reinforcement idle) is skipped:** the original audit detail was not kept, the same pattern is in the
     unit, infantry and vessel `Read_INI`, and skirmish maps carry no pre-placed units, so it has no effect on the
     current map pool. Re-derive its intent before touching it.
2. **Per-house INTEL LAYER, shipped in 4.1.0** (Phase 1, §6): "what has this house discovered + where last seen".
   Remaster already tracks per-player shroud; ALL AI reads go through it: target evaluation (`Evaluate_Object`'s
   fog gate), superweapon aiming (`Special_Weapon_AI`, which TF's TD Ion and nuke dispatch use), attack-destination
   picking, and every NEW system (counter-building, naval-war detection) so they are born fair. Last-seen memory:
   nuking where the WF *was* is smart, not cheap.
3. **Scouting behaviour, shipped in 4.1.0** — cheap fast units get a scout job (the stage-aware value model
   feeds this); IQ-gated intensity (Easy lazy, Hard keeps the map warm).
4. **Reservation-table pathfinding (open)** — cell reservations at tick T + scatter-the-blocker;
   treat reserved cells as soft obstacles; JPS follow-on optional. Read OpenRA
   (`OpenRA.Mods.Common/Traits/World/PathFinder*.cs`, MIT) before implementing. Closes the
   gw==2 + stuck-in-base threads.
5. **Primary-factory production, shipped in 4.1.0 (AI Boost port + generalised)** — AI builds one order per
   category through a primary factory (like humans) instead of parallel-building from every
   factory. Removes a vanilla cheat AND fixes the `FactoryMax`=20 heap exhaustion behind
   late-game "sidebar can't build" (`rules.cpp`). A real AI nerf, so it pairs with W3.

### W2 — Faction separation + buildability rework *(the one-brain enabler)*

> **DESIGN CONSTRAINT: build for N factions, not 4.** TS GDI/Nod (and a
> possible multi-era spin-off: TD+RA+TS+RA2 = 8 factions) are design-feasible via
> decoupled country houses — see `ts-gdi-faction.md`. Anywhere W2 encodes
> "the four factions" (placeholder ActLike tables, prereq remap lists, role-flag
> dispatch), prefer data/loop-driven over 4-way literals. The role-flag refactor in
> finding 4 already points this way; this note makes it binding.

The engineering survey's findings:
1. **Capture inheritance is already free.** The sidebar buildable list is computed per
   FACTORY BUILDING via `Update_Buildables` calling
   `Can_Build(type, this->ActLike)` — the BUILDING's ActLike, not the owner's. A captured
   faction building already offers its faction's roster (TDWEAP and TDHPAD prove it).
   Faction-tagged types with pinned ActLike (the pinning in `BuildingClass::Unlimbo`; 4
   factions map cleanly onto GREECE/USSR/GOOD/BAD placeholders) make lineage automatic —
   NO capture-specific code. A building both TD factions can own (`Owner=GoodGuy,BadGuy`) keeps
   its owner's ActLike instead: the pinning branch tests GDI before Nod, so a pinned side would
   give a Nod yard the GDI sidebar and flag shared buildings as captured.
2. **The prereq-liveness gap is ONE SITE:** the every-frame sidebar Recalc in `sidebarglyphx.cpp` evicts through
   `Who_Can_Build_Me(intheory=true, legal, …)`, and `legal=false` short-circuits the prereq check. Fixed by making
   eviction prereq-aware: it now passes `legal=true`, so offer and eviction are symmetric (phase (a) below). This
   changes behaviour for ALL existing units too (players notice — desired, it's the exploit fix).
3. **Owner= is not deleted — it's widened** (open question: the yards and MCVs shipped with `Owner=` narrowed per
   faction, so which policy holds for the other units is undecided). Keep Ownable broad (all four factions on
   units); the faction-specific PREREQ building is the sole discriminator. Every new
   faction prereq token needs an explicit Can_Build remap `continue` (`HouseClass::Can_Build`'s remap clauses
   are the template; the generic any-of clauses for power/refinery/repair are already
   there). Forgetting one = silently unbuildable (known trap).
4. **Site fan-out, shipped with (b):** ~100 hardcoded dispatch sites across CONST(27+27)/WEAP(24+22)/
   HELIPAD(37+28)/MCV(26+17) enum pairs; the hottest paths go through role predicates instead of N-way lists
   (`Is_Construction_Yard`, `Is_Helipad`, `Is_MCV` in `type.h`). The MCV→ConYard mapping is centralised in
   `MCV_Deploy_Building` (`unit.cpp`).
5. **Helipad dual nature, shipped with (d):** universal landing — `Find_Docking_Bay` (`techno.cpp`) takes any
   `Is_Helipad()` building when a helicopter looks for `STRUCT_HELIPAD` (the shared, faction and TS pads); faction production = the per-pad
   Update_Buildables/Who_Can_Build_Me gates stay specific. Only place needing two-headed handling.
6. **Also:** `Rule.FactoryMax` is raised (`rules.ini` `[Maximums] Factory=100`; captured multi-faction bases run
   more concurrent factories); the skirmish MCV spawn's switch in `scenario.cpp` gives each faction its own MCV, and
   each faction's starting units come from its own column (fixed in 1.1.0); heap headroom exists (STRUCT_COUNT+50);
   mid-game saves break per enum addition (skirmish-only risk).

**Phasing.** (a) The eviction fix (finding 2), live-verified: prereq-gated AND capture-offered (`TDGAFLD`) cameos
withdraw on loss and return on rebuild, with zero spurious evictions in ~10k frames. Its capture-side effect stays
latent while narrow `Owner=` lists (`[TDMTNK] Owner=GoodGuy`) do the discriminating, which is why it landed first.
Its diagnostic stays live under `TF_DEV_BUILD`: `MOD_DEBUG_EVICT.txt`, where `rule=prereq` is changed behaviour and
`rule=factory` vanilla. (b) ConYard + MCV split, (c) War Factory, (d) Helipad last (dual nature); the role-flag
refactor landed with (b).

**(b)-(d) shipped in 4.1.0:** the yard role predicate and one scan-bit table; the eight faction yards and MCVs as
pipeline-built types (`STRUCT_AFACT/SFACT/TDGFACT/TDNFACT`, `UNIT_AMCV/SMCV/TDGMCV/TDNMCV`, all fresh entities,
not aliases) with `Owner=` narrowed per faction; the Allied/Soviet war factory split; the four-way helipad split.
Vanilla `FACT`/`MCV`/`TDFACT`/`TDMCV` keep their identities for stock-campaign content. How sidebar names resolve is
in `faction-select-identity.md`; the tileset-key trap is `td-port-playbook.md` §3.30. On the map the twin yards and
MCVs are told apart by a faction emblem baked onto their sprites (`scripts/badge_sprite_art.py`).

> **The MCV deploy dispatches on the UNIT's TYPE.** With 4 real MCV types the
> type itself carries the faction — an MCV built by a captured factory IS that faction's
> MCV type (factories produce their own roster via `Update_Buildables`' building-ActLike
> rule), so capture lineage propagates with no instance field. A `UnitClass::ActLike` field is not
> needed and does not exist.
> The launcher's own deploy command keys on vanilla identity, so the DLL reads the deploy key
> itself and every faction's MCV deploys by key (`launcher-vs-dll-ownership.md`).
> **Unlocks:** crates that hand out another faction's MCV type (`todo.md`, Features).

⚠️ **Survey claims that did NOT survive verification** — do not re-fix (line numbers as the survey gave them):
`house.cpp:6430` AI never suicide-sells its ConYard (`URGENCY_CRITICAL` means "only at max urgency",
`Check_Raise_Money` tops out at MEDIUM, and `Check_Fire_Sale`'s condition requires already having no yard);
`team.cpp:2968` unreachable (all 93 shipped maps have empty `[TeamTypes]`); `conquer.cpp:651` dead code (the launcher
owns input, `Keyboard_Process` is commented out in `dllinterface.cpp`). Also **units are NOT past bit
31** — `UNIT_MCV`=11, `UNIT_TDMCV`=22, first overflow is `UNIT_TDSTNK`=32; only BUILDINGS overflow
(`STRUCT_TDFACT`=102). Two real finds: the crate MCV was faction-blind, now fixed (`cell.cpp`:
`House_Has_MCV` scans the heap, and a skirmish comeback MCV is the recipient's own faction's); still open, the
`UScan` shift by unit type (`Tracking_Add`, `Recalc_Attributes`) has NO `< 32` guard, so `UNIT_TDSTNK`..`UNIT_TSHVR`
alias onto bits 0-5 — naively adding the guard risks a spurious defeat via the `!UScan` check, so it needs a unit
shadow table, not a one-liner (`known-issues.md`, scan bits past 31).

**Naming spec.** Every type W2 splits was a SHARED entry with no per-faction name, so a split silently produces
duplicate cameos. Rule: **the Allied/Soviet axis ALWAYS needs prefixing** — RA served both
sides from one entry, so the halves share a name *and* a sprite. The **GDI/Nod axis usually
does not** — TD gave them genuinely different buildings. Mechanism: the SIDEBAR label is
the RABUILDABLES `ObjectNameTextID` resolved through the launcher string table (base `.LOC`
merged with the mod's **`Data/ModText.csv`**, `faction-select-identity.md`); rules.ini `Name=` drives only
the in-world hover tooltip. Set BOTH at split time:

| Step | Shared entry | Split into | Names |
|---|---|---|---|
| (b) | `[FACT]` `allies,soviet` + `[TDFACT]` `GoodGuy,BadGuy`, all "Construction Yard" | 4 | Allied / Soviet / GDI / Nod Construction Yard |
| (b) | `[MCV]` `allies,soviet` + `[TDMCV]` `GoodGuy,BadGuy`, all "MCV" | 4 | Allied / Soviet / GDI / Nod MCV |
| (c) | `[WEAP]` `soviet,allies` "War Factory" | 2 | Allied / Soviet War Factory |
| (d) | `[HELIPAD]` `allies,soviet` + `[TDHPAD]` `GoodGuy,BadGuy`, all "Helipad" | 4 | Allied / Soviet / GDI / Nod Helipad |

- (c) is 2-way only: GDI's `[TDWEAP]` is already "Weapons Factory" and Nod builds
  `[TDAFLD]` "Airstrip" — distinct names AND distinct art, leave both alone.
- ConYard/Helipad/MCV are the four-way cases: within each pair the sprite is near-identical,
  so the name + badged cameo are the discriminators (MCV cameos carry the
  `dot{ally,ussr,gdi,nod}` faction badges — `BuildIcon_<IniName>.tga` loose files).
- The launcher's deploy command keys on vanilla enum identity; the DLL reads the deploy key
  itself, so the split costs nothing (playbook §3.23).
- **Harvesters stay as they are** — the same question was asked for the
  `a` select-all hotkey and the answer is different, because there the faction-varying part
  IS the entity: `[TDHARV]` carries `Image=TDHARV` and `Image=` is per-type, so merging to
  regain the hotkey would render GDI/Nod harvesters with RA art. Splitting is always
  art-safe (N types can share one `Image=`); MERGING is what costs a sprite.
- Faction-prefixed names DEVIATE from TD/RA-authentic naming (TD called them plain
  "Construction Yard"). A deliberate deviation, per the balance guardrails; this spec is where it is recorded.
- `[PROC]` and `[DOME]` are also shared `allies,soviet` but W2 does NOT split them; leave.

**Splitting DELETES Can_Build remaps, it doesn't only add them.** `HouseClass::Can_Build`'s
equivalence clauses exist partly because entities are shared: `[TDHPAD]`'s
`Prerequisite=TDPYLE` is why the TDPYLE↔TDHAND mutual-equivalence clause is load-bearing
(Nod owns a Hand of Nod, not a barracks). Per-faction pads take their own prereq directly,
retiring that need. Each split checks whether it removes a remap before adding one.

### W2.9 — Faction-agnostic base builder with a home-faction weight

**The AI half of the one-brain design.** There is one brain: every house runs `Expert_AI` then `AI_Building` /
`AI_Unit` / `AI_Infantry` / `AI_Aircraft` (`HouseClass::AI`), and faction enters only as vocabulary —
`TF_Skirmish_Pick(role, ActLike)` swaps the concrete type per base role. Ratios, urgency and timing are identical
for every faction. **Target: the builder stops asking "what am I?" and asks "which trees can I build from?", with
its own faction weighted slightly ahead.**

**Already free:** units, infantry and aircraft are never substituted — the AI walks the type
lists filtering on `Can_Build(type, ActLike)`. Mixed production appears the moment prereqs
exist. The building side is the whole job.

**Shipped in 5.0.0: role counting.** Capacity-role presence is counted across every lineage
(`TF_Role_Quantity` in `house.cpp`), so a captured factory counts against what the AI builds for itself instead of
being duplicated. **Still open:** `TF_Skirmish_Pick` names only the home faction's types, so an AI that captures a
war factory gets a tree it never builds into, and in Unholy Alliance three of its MCVs' trees go unused.

#### Counting rules

Role presence counts must aggregate across *all* lineages, or the AI builds one barracks per tree because each
type's count is zero. Applied to every role, that rule introduces a worse bug, so there are two kinds of role:

- **Capacity roles** (war factory, barracks, helipad, refinery, power): **aggregate across
  every lineage.** A captured factory is interchangeable throughput — `Time_To_Build` divides
  by `Factory_Count` — so it must count against what the AI builds for itself. This is the
  redundant-build fix (`TF_Role_Quantity`).
- **Unlock roles** (tech centres TDEYE/TDTMPL/atek/stek, radar TDHQ/dome): **count only types
  that satisfy this house's own prereq chain.** Prereq clauses are side-scoped on the owner
  mask (`Can_Build`, `(own & HOUSEF_GDI)` etc.) under the locked prereq policy, so
  a captured Nod Temple satisfies none of GDI's clauses. Aggregate it and the Temple fills the
  "tech centre" role, permanently suppressing the AI's own Eye — no Ion Cannon, no top tier,
  for the rest of the match. `TF_Role_Quantity` is never called for an unlock role.

The test for any role: **does a captured copy do the job I would have built mine for?**
Throughput yes; unlocking my own tree no.

**Per-lineage caps ("2 GDI + 2 Nod + 2 Allied + 2 Soviet") are rejected.** They
do not fix the bug at all — a GDI AI with 1 own factory that captures a Nod one still reads
"GDI 1, cap 2" and builds another. Separate buckets *are* the defect; four buckets is
still four buckets. They also discard the economy-aware `WarRatio * CurBuildings` target for a
fixed ceiling that does not care what the AI can afford.

**Frequency.** In ordinary skirmish captures are rare. In **Unholy Alliance** every house, AI included, starts with
an MCV of every faction (`scenario.cpp`), so every lineage is live from frame 0.

#### Where the cap comes from — AI Boost

AI Boost already solved the cap question; port its shape rather than inventing one
(`reference/ai-boost2/WorkshopContent/AIBoost/CCDATA/AIBOOST.INI`):

- **One limit per ROLE, not per faction** — `AIWarFactoryLimitBasic=4` is four war factories,
  whoever built them. Independent confirmation of aggregate counting.
- **×2 when a construction yard is built *or captured*** — capacity earned by holding more
  production bases. This is the "harder AI keeps redundancy" idea, scaled by what the house
  actually owns instead of a flat difficulty bonus.
- **`AIAllowDynamicBaseGrow`** — if the enemy average exceeds my cap, raise mine to match
  (barracks, war factory, naval, helipads, airfields, defences). Redundancy that answers the
  opponent, so a turtling human faces a bigger AI base.
- **`AIStrategyMode`** — a per-house strategy roll (naval / air / infantry / tank rush, or
  defender, which caps every factory at 1 and spends on defences). Directly serves the
  "personality/randomness per AI house" caution below.
- **`AllowTechStealing`** — their cross-side capture-tech switch; worth reading before
  extending ours, and it documents a human-side quirk (yard must be re-deployed to unlock).

**Difficulty attaches to the mechanism, not to a number:**
the tier decides whether dynamic growth engages at all — Easy pinned to a low fixed limit, Hard
scaling to the enemy average — rather than handing Hard +2 factories. The AI still pays full
price for every building; no cost/armour/firepower bias. Assign in W7.

The policy stays lobby difficulty + `rules.ini` dials: take AI Boost's mechanism, not its INI surface.

**The home-faction bias is a weight, not a gate** (keeps difficulty behavioural). With aggregate role counting the
AI fills each role *once*, and the weight decides which lineage fills it — so "GDI builds GDI
first" falls out without an explicit phase. Cross-tree picks then appear naturally at the
margins: second factories, defences it lacks, roles its own tree cannot fill.

**Two cautions:**
- **Do not let defences mix uniformly.** Best-of-four converges on the same Obelisk/AGT wall
  every match: variety dies, and a single-faction human cannot answer a best-of-four line.
  Per-role candidate weights with personality/randomness per AI house.
- **Gate tree expansion on economy.** Teching four trees is expensive and the urgency system
  does not know it. Use the existing pattern (`Power_Fraction() >= 1 && hasincome`, the Nod
  Stealth Generator branch) or the AI over-extends — a bigger version of the repair-bay-before-
  refinery bug.

**Build it for N lineages, not 4** (the standing constraint above). The ownership-gated TS
tree (`ts-gdi-tree-plan.md`) is the fifth lineage and the reason this matters: it is
what breaks 4-way literals, and it is inert to the AI until this lands.

### W3 — The brain: build planner + placement

**Base placement, fixed in 5.0.0.** GDI could hold thousands of credits and fail to place a refinery, war factory
or depot (12 `PLACE-FAIL` lines, all GDI). Three defects, all EA-original:
- `Recalc_Center` divided the unweighted distance sum by the cost-weighted count, so an expensive base got a Radius
  2-3x too small, and `Which_Zone` (which rejects past `Radius*4`) shrank the build search to a disc the base itself
  filled.
- `Find_Build_Location`'s fallback returned a raw `CELL` where a `COORDINATE` was expected, so a full preferred zone
  discarded the building. Broken in EA's source since 1996; worth upstreaming.
- A stalled factory scrapped its order instead of holding it.

`Find_Cell_In_Zone` also filters by its zone, so each pass of the try-any-zone fallback searches fresh ground.
Verified: 0 `PLACE-FAIL` to F11,944, radius 850-950 at 7 buildings. With yards far apart, each building joins the
cluster of its nearest yard (weighted by cost) and only the heaviest cluster feeds Center, Radius and the zone
ratings; a remote yard places its own products round itself (`TF_Find_Cell_Near_Yard` in `building.cpp`).
- **Diagnostic:** `PLACE-FAIL <type> reason=... | rejects radar= zone= legal= prox= ok= | center=
  radius=` in `MOD_DEBUG_AI.txt` (dev builds) names the predicate that rejected the cells.
- **Falsified, do not re-chase:** TD buildings as invalid proximity anchors (`IsBase` defaults true
  and they set `BaseNormal=yes`); infantry spam starving the expensive builds (the failures were
  placement, with healthy cash); a too-small search area; the in-limbo `BQuantity` count as the
  cause (a real bug, fixed: the economy gate counts `ActiveBQuantity`; it only decided which building thrashed).
- **Reading trap:** `PROD start` proves only that an order began, not that it completed; confirm against `CurB`, the
  `ROLE` counts or the screen. (`TDMTNK` is the GDI Medium Tank; the Mammoth is `TDHTNK`.)

**W3 economy-first, shipped in 5.0.0 (the first slice of item 1):** refinery target paced by
sim-minutes (2 @2.5, 3 @6, 4 @10; vanilla ratio kept as a floor; HIGH while below pace;
`TF_Eco_Refinery_Target`), harvester fleet per tier (Hard 2 per refinery, Medium 1.5, Easy 1), infantry and
combat-vehicle production yields while below target beyond a growing garrison (4 inf + 1/min, 2 veh + 1/2min),
hold lifted by a hit in the last two minutes and capped at four minutes. Defences claim HIGH
while under half the ratio, and the ratio is taken against the non-defence base. Watched
working in a 4-Hard-AI Docklands match (4 refineries / 8-9 harvesters / 30 buildings by 12
sim-min). **Still open in item 1:** tech ordering — tech centre / advanced comm / temple only
arrive via the starvation rescue; it waits until the pieces work together.
1. **Staged build planner** replacing the shouting-urgency-slots model: coherent opening
   (economy first — fixes GDI/Nod eco passivity), then production, tech when affordable
   (fixes Temple starvation: the power gate and MEDIUM-urgency starvation in `AI_Building`), defence
   budgeted by threat.
2. **Placement intelligence (open):**
   - Threat-aware defence placement: bias zonerating toward LAZone (the last-attacked zone,
     tracked in `building.cpp` and never consulted) + enemy-direction octant, in
     `Find_Build_Location`. Kills corner spam: the random-zone fallback is the culprit — armed buildings only ever
     rate zones, so unarmed buildings place RANDOMLY.
   - Refinery-near-ore: new tiberium-proximity scan, special-case before the zone loop.
   - Power/economy in ZONE_CORE instead of Random_Pick.
   - Optionally revive `AI_Base_Defense` (`#ifdef NEVER`, `ai-improvements.md` Problem 9) for defence rebalancing.
   - **Own-unit ring stunts the base (seen in play, confirmed in code):** `Flush_For_Placement` (called from
     `building.cpp`, implemented in `bdata.cpp`) only scatters allied foot units with NO NavCom (stuck-while-pathing
     units are never flushed), does nothing for other occupiers (retaliation commented out), and ANY occupied
     footprint cell defers the whole placement to a retry — dense unit rings make the footprint never
     simultaneously clear, and placement starves. Fix here: scatter own units regardless of NavCom, and fall back to
     an alternate Find_Build_Location after N failed flushes. Scatter-on-launch (Phase 0) thins
     the ring incidentally; watch during soak whether the GUARD_AREA garrison worsens it.
   - AI Boost's placement is byte-identical to vanilla, so this would be a first for the
     Remastered ecosystem.
3. **Stage-aware unit valuation + counter-composition** (vs scouted intel only).
4. **Counter-building** (AI Boost mechanism, generalized 4-faction, intel-filtered).
5. **Power management** (sell-excess / build-ahead margins — AI Boost pattern).
6. **The repair bay waits for the economy, shipped.** Every faction's service depot is queued only once
   `tf_economy_ready` passes (two standing refineries and a war factory, or a Tiberium-short house) and power is full
   (`AI_Building`), then at `URGENCY_HIGH` for GDI and `URGENCY_MEDIUM` otherwise. It gates the GDI Mammoth (TDFIX)
   and the RA MCV (FIX).
   - **Why a gate and not a lower urgency:** at `URGENCY_LOW` the depot was never built, fatal for GDI's Mammoth
     tier; promoted to HIGH without a gate, GDI built it before its first refinery and both TD sides before a second,
     and starvation ageing made it worse. The general W3 point stands: the build planner has urgency but no notion
     of *stage*, so any promotion becomes "build it first" unless eligibility is gated.

### W4 — Attack quality

**Why stock waves come late and small.** In an Unholy Alliance match with one GDI and one Nod AI at Medium (IQ 4),
both with armies (73 and 55 combat units) and aware of each other, nine consecutive attack opportunities logged
`WAVE-SHUFFLE (nothing sent)` and the first `WAVE-LAUNCH` came at frame ~27,500 (log: `git show
b6d3b52c:docs/todo.md`). The cause is arithmetic, all of it EA's (`REDALERT/HOUSE.CPP`):
`AttackDelay(5) × [450..1800]` in `HouseClass`'s constructor (line 682) seeds the first opportunity 2,250–9,000
frames in; each opportunity in `AI_Attack` is a flat `Percent_Chance(33)` (line 5295); and a declined roll resets the timer to the same full `AttackInterval(3) × [450..1800]`
a launch does (line 5343), so declining costs 1.5–6 minutes. The expected first wave is ≈ 12,400 frames with a fat tail — nine
straight declines is `0.67⁹ ≈ 2.7%` per house. Vanilla masks this with campaign TeamTypes that skirmish never gets.

**W4.1 cadence, shipped in 5.0.0** (`TF_Wave_Dials`, `AI_Attack`):
- **The decline is a reason, not a coin toss.** `TF_Committable_Army()` counts armed units,
  infantry and aircraft (harvesters, MCVs and engineers excluded) and their worth at list cost. Below the **floor**
  the house holds rather than feeding units in piecemeal; at or above the **ceiling** it must commit rather than
  hoard; only between the two does the roll decide. With no war factory it holds (a stage gate), and a house with
  no buildings left after the first minute always launches.
- **The floor is count AND value at every tier:** 10 units and 8,000 credits. A count-only floor of 10 launched 18
  tier-one units at four minutes and left nothing to defend with (`ai-ab-2026-09-02/`).
- **A decline costs seconds, not minutes** — the timer reset is split, full interval on launch,
  short recheck on decline. ⚠️ **This is only safe with the floor in place**: a fast recheck
  against a blind 33% roll launches almost immediately every time, which deletes the pacing
  rather than fixing it. Never port the recheck split without the band.

Difficulty rides on **frequency and responsiveness only**, and the floor is deliberately NOT a
difficulty dial — attacking with a token force is incompetence, not mercy, and since
rules.ini `[IQ] Production=3` means IQ does not gate production, every tier reaches a given army
size at much the same minute, so a lower floor on Easy would only make the easier AI attack *first*:

| IQ | floor (units, credits) | ceiling (units, credits) | mid-band | recheck | post-launch interval |
|---|---|---|---|---|---|
| 3 Easy | 10, 8,000 | 32, 26,000 | 25% | 90 s | 133% |
| 4 Medium | 10, 8,000 | 30, 22,000 | 40% | 60 s | 100% (vanilla) |
| 5 Hard | 10, 8,000 | 26, 18,000 | 60% | 30 s | 67% |

The ceiling is met by worth alone, or by its unit count with the floor's worth. Hard is more aggressive at every
stage rather than merely later and bigger. The interval stays keyed to `Rule.AttackInterval` so rules.ini keeps
authority. Two safety valves: a strangled house (Tiberium short, under two refineries or under two harvesters) loses
one unit of floor every 2 sim-minutes past the 20-minute mark, down to 4, with the floor's worth scaled to match;
and the idle guard reposition is rate-gated to about every 2 minutes whatever the recheck (it walks
`Nearby_Location` per unit and would otherwise jitter the home guard).

**W4 staging (Route B), shipped in 5.0.0:** committed ground units march to a cell `TF_WAVE_STAGE_BACK` (nine)
short of the nearest DISCOVERED enemy building on the house's own landmass (`TF_Wave_Stage_Cell`), gather (70% or
four sim-minutes), and release together, at every tier. Hard releases on the CFE attack-move (its objective is the
enemy building's cell, not the building, so destroying it mid-march doesn't cancel the order, `TF_Wave_AI`) with a
six-minute shepherd that converts arrivals to hunt; the other tiers release as hunt. No staging cell + Hard =
attack-move from home; a gathering wave blocks relaunch; the ferry draft exempts wave members. A launch also
scatters its units first (scatter-on-launch, harvesters exempt).

**Deferred, wanted:** per-house **personality** (`AIStrategyMode`, W2.9 borrowings) — roll each AI a character at
match start (pressure / balanced / massing) where a massing house raises its own floor and ceiling. Keep it OFF the
difficulty axis: difficulty says how well the AI plays, personality says how, so two Hard AIs in one match can
differ. Tune it against the measured W4.1 baseline.

The two routes for staging-then-blob:
- **Route A (higher fidelity, not attempted):** revive the TeamClass campaign machinery — the
  gather/formation/blob logic ALREADY EXISTS (`Coordinate_Regroup`, the full-strength
  gate in `TeamClass::AI`, the lagger wait in `Coordinate_Move`, `Coordinate_Attack`). Drop the GAME_NORMAL recruit
  gate (`ai-improvements.md` Problem 14), synthesize skirmish attack-TeamTypes with computed staging waypoints (near
  the enemy base — skirmish has no authored waypoints; this is the new work). Aircraft fold in automatically
  (`aircraft.cpp`'s team guard). Spike it before trusting campaign TeamTypes in a skirmish soak.
- **Route B (shipped, coarser):** staging inside `AI_Attack`: MOVE to the staging cell → GUARD_AREA until the
  threshold → release.
- **AI attack-move:** set `AttackMove=1` + `RememberedNavCom` on dispatch — the whole player
  state machine (CFE port) is input-agnostic (`TechnoClass::AI`). Audit stray `IsHuman` guards
  (`infantry.cpp`).
- **AI Boost borrowings:** scatter-on-launch (shipped, unsticks waves), defence-gated send-percentage (shipped),
  target-variety rolls, special-unit handling in waves (medics guard, spies always go).
- **Enemy re-pick weighting** (`ai-improvements.md` Problem 16): the enemy is already re-picked every attack cycle,
  but distance outweighs threat, so the brain rarely retargets.

### W5 — Capabilities
1. **Naval AI + water evaluation, shipped in 5.0.0.**
   - **Build-out:** all production plumbing (BuildVessel → Suggest_New_Object → yard factory tick) already worked;
     the ONLY missing piece was a skirmish branch in `AI_Vessel` (in place of the `IsBaseBuilding` clear — modelled
     on `AI_Unit`'s weighted-random block + the A-10 per-airfield gate; Can_Build gives faction rosters
     automatically). AI Boost filled the exact same empty block — proven pattern.
   - **Water evaluation:** reuses `Zones[MZONE_WATER]` connected-region ids (stable all match — zones ignore
     buildings), adds a per-zone SIZE (Zone_Span already computes the count and discarded it) and checks which
     houses are coastal on that water. Pond test + does-it-reach-the-enemy test = two lookups. AI Boost's detection
     is building-count only, and fog-blind; ours goes through the W1 intel layer. `Zone_Reset` records each water
     zone's cell count in `TF_WaterZoneSize` (`map.cpp`). `TF_Naval_Assessment` (`house.cpp`) keeps the
     largest zone within `TF_NAVAL_COAST_RADIUS` (20 cells) of the base that reaches
     `TF_NAVAL_POND_MIN` (80 cells), and reports whether a discovered enemy building is coastal on it.
   - **Yard placement gap (open):** Find_Cell_In_Zone already honours Legal_Placement (WaterBound →
     coastal water cells only) but searches rings around the LAND base center — on maps
     where the base isn't near shore it can silently fail. Bias yard placement toward the
     nearest coastal cell of a water zone the house borders (W3.2 companion).
   - Naval build gates: don't out-build the enemy navy (intel-filtered; Fleet size below), naval-war detection
     rescales limits (AI Boost tiers as reference).
2. **Sea transport ferrying, shipped in 5.0.0 (`TF_Ferry_AI`); invasions don't land yet (`todo.md`).** The
   mechanism exists as campaign primitives — TMISSION_LOAD's MISSION_ENTER + RADIO_DOCKING boarding handshake
   (`team.cpp`, `foot.cpp`, `vessel.cpp`), `Desired_Load_Dir` as the "can I load/land here" oracle (`vessel.cpp`),
   the vessel MISSION_UNLOAD state machine. The skirmish ferry controller is a hand-rolled sequence (pick LST +
   units → ENTER → sail to a landing cell chosen from the water-zone data → UNLOAD), hooked like TF's other custom
   controllers (harvester watchdog, Obelisk-sub charge). No reference precedent (AI Boost wishlisted it, never built
   it). The shared transport is the RA LST (VESSEL_TRANSPORT, fully wired); the parked TDLST hull is NOT wired into
   `vessel.cpp`'s transport switches — wire it only if revived.
   - **Traps the naval build hit (all fixed, shipped in 5.0.0).** Vanilla never ran a skirmish
     navy, so each of these sat dormant in EA's code:
     - `Exit_Object`'s vessel case returned "abort and refund" when the one-cell exit ring was
       occupied, so a finished ship at a blocked slipway was silently deleted (44 ship
       `PROD start`s made a 3-ship fleet). A blocked slipway now retries, and the house's own
       parked ships are moved off the ring.
     - `Can_Fire` returns `FIRE_MOVING` for any turretless hull with a NavCom, and a patrolling
       ship always has one, so subs never fought. AI ships drop the NavCom when a target is in
       range (`VesselClass::Combat_AI`).
     - `MISSION_HUNT` is terminal: a hunter with an unreachable target parks at the shore for
       good, the fleet count stays at the cap and production stops. Hunt supervision sends
       stalled hunters back to guard.
     - The vanilla sell table puts the naval yards at `URGENCY_LOW`, the top of the fire-sale
       order, and LOW fires on any dip under 100 credits: build, half-price sell, rebuild every
       90 s. Pool-rebuilt buildings can't sell at LOW (`EXPERT-SELL` diag).
     - Ferry and fleet statics survived into the next match of a session (a stale beach rally
       could satisfy the MCV gate); they reset in `HouseClass::Init`.
     - A naval yard and its parked fleet can seal their own channel, and zones ignore buildings,
       so no zone check sees it (the open harbour-seal item in `todo.md`).
   - **Ferry pipeline** (`TF_Ferry_AI`, `TF_Ferry_Eligible`): a Hard house never has idle teamless
     guards (team recruitment claims every new fighter), so drafting only spares sat at roster 0;
     hence the STAGING and DOOMED draft levels. The roster drafts nearest-first and sends draftees
     straight to a staging cell at the water's edge (heap-order drafting, or leaving draftees in
     place, ran the load timer out and shipped one-unit loads). PICKUP: a transport that stops
     short (harbour mouth blocked by its own yard and fleet) gets a fresh move order after 60
     frames and is never put into LOAD. SAIL: the drive layer waits behind any hull in the lane
     and an enemy ship never moves aside, so a parked transport re-paths after 60 frames, with the
     `TF_FERRY_SAIL_REPATH` distance watchdog for slower cases. UNLOAD: when `Desired_Load_Dir`
     finds no free beach cell, one retry re-plans toward the enemy base.
   - **Fleet size** (`TF_Naval_Fleet_Cap`) matches the strongest single enemy navy, not the sum,
     with no margin, so two AIs settle level; the floor keeps enough ships to bombard a navy-less
     enemy's shore, the ceiling stops a naval war eating the economy.
   - **Fleet doctrine** (Expert_AI): blind, idle warships patrol random cells of the assessed
     water zone (`TF_Naval_Patrol_Cell`); once the coast is known the first idle warship plants a
     rally and the others close on it; the fleet releases as MISSION_HUNT at
     max(3/4 of the cap, `TF_NAVAL_WAVE_MIN`) and the rally clears.
   - **The naval yard isn't gated on finding an enemy shore:** such a gate gives factions with
     recon specials (spy plane, recon flight) a standing naval head start.
   - **Testing:** `MOD_DEBUG_AI.txt` is written to `%USERPROFILE%`, which under Proton is
     `pfx/drive_c/users/steamuser/`, not `Documents/CnCRemastered/`. Before a
     deploy, wait for a full game exit with `pgrep 'InstanceServerG[.]exe'` (a bare
     `pgrep -f InstanceServer` matches itself). Restarting a match does not end InstanceServerG.
3. **Superweapons for RA factions (open):** Iron Curtain + Chronosphere AI dispatch + AI-aware
   targeting (`ai-improvements.md` Problem 3b/3c — the object in the target cell is picked by the mouse; AI Boost
   has working IC/Chrono usage as reference). Parabombs already go to any house with an active real airfield
   (`STRUCT_AIRSTRIP`).
   - **AI builds the Missile Silo (RA nuke host):** the firing path already exists and is
     fair-fog-aware (`Special_Weapon_AI(SPC_NUCLEAR_BOMB)`, gated on active MSLO +
     IQ >= Rule.IQSuperWeapons) — the AI just never queues the host, the same shape as the TDTMPL
     starvation was. Fix = one AI_Building pool entry modelled on the
     Stealth Generator slot (one silo, full power + income gates). Both RA sides can build
     it: a house holding an Allied yard satisfies `[MSLO] Prerequisite=stek` with its own
     Advanced Tech Center (`Can_Build` in `house.cpp`). Still open: the AI never queues it.
4. **Special units (open):** Spy/Thief/Dog AI production + usage (Value=0, never built). The
   AI's combat pick also excludes the Limpet Drone, Mobile EM-Pulse, Mobile Sensor Array and Mobile
   War Factory (`AI_Unit`): they are for human players and scripted events, until each has AI use;
   AI Boost engineer/spy/MAD-tank handling as reference.

### W6 — Team coordination (v1 scope, open)
All four items need ZERO new inter-house plumbing (read surface verified: Enemy, Center,
Attack timers, LATime/LAEnemy, IsAlerted all public):
1. Gang-up: Computer_Paranoid skirmish ungate behind a lobby-respecting knob (`ai-improvements.md` Problem 11).
2. Shared targeting: allied AIs bias Enemy toward a common target (Expert_AI tick).
3. Aligned timing: allies read each other's Attack countdown, nudge waves to land together.
4. Help a sieged ally: redirect next wave to ally's Center/LAEnemy on distress.
Team INTEL sharing rides the W1 intel layer (allies union their discovered sets — mirrors
human ally shared vision). Pincers/role-splitting = Hard-tier follow-on, not v1.

### W7 — Difficulty plumbing
Per-AI IQ comes from the lobby (`TF_AI_IQ_From_Difficulty`, set in `GlyphX_Assign_Houses` and its mirror sites in
`queue.cpp`, `scenario.cpp` and `saveload.cpp`); it is never routed through `Assign_Handicap` (stat biases).
**Prerequisite: `Rule.IQProduction` below 5** (TF's `rules.ini` sets 3; `HouseClass::AI` tests it in skirmish and
keeps `Rule.MaxIQ` in campaigns, so scripted enemies still wait for their trigger), and `IQSellBack` is a tech-level test,
not an IQ tier: both on the field manual's
[The skirmish AI and its IQ levels](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/skirmish-ai-and-iq.md#iq-levels), IQ levels.
Tier map: Easy=IQ3 (no supers/aircraft-AI/roam), Medium=IQ4 (+supers, aircraft, guard-area,
content-scan), Hard=IQ5 + the new smart behaviours. The per-slot lobby path is `TF_Apply_AI_Difficulties`
(`dllinterface.cpp`). New behaviours get their own IQ thresholds.

### W8 — Combat mechanics (open)
Directional armour per §2.3: hook `TechnoClass::Take_Damage` (`techno.cpp`) after ArmorBias, before
Modify_Damage; 3 files, no per-object state, deterministic; directionless
damage auto-excluded via source==NULL/forced gates + warhead opt-outs. Reverse move:
decision-gated (§2.3).

## 4. What's already fixed (do not redo)
Radar/tech progression, the harvester intelligence arc (threat-aware fields, load-balanced refineries, anti-stuck
watchdog, the `IsTiberiumShort` reset), the Repair Bay queue (TDFIX), TD Ion/Nuke auto-fire, building `Points`
targeting values (`td-building-separation-recipe.md` gotcha 11), A*/attack-move/chokepoint give-way/group-spread
(2.2.x-2.3.0). A sweep of every `Session.Type` gate found NO undiscovered high-severity gates.

## 5. Difficulty tier matrix

What ships and what is planned (§2.2):

| Behaviour | Easy | Medium | Hard |
|---|---|---|---|
| Base-building, economy, army | ✓ | ✓ | ✓ |
| Universal capabilities (naval+water eval, transports, eco fix, pathfinding, fair fog) | ✓ | ✓ | ✓ |
| IQ gates (supers, aircraft AI, guard-area roam, content-scan) | ✗ (IQ3) | ✓ (IQ4) | ✓ (IQ5) |
| Staged waves (shipped) | ✓ | ✓ | ✓ |
| Attack-move release (shipped) | ✗ | ✗ | ✓ |
| Threat-aware defence placement (planned) | ✗ (random) | ✓ | ✓ |
| Counter-composition / counter-building (planned) | ✗ | partial | ✓ |
| Scouting intensity | lazy | moderate | active |
| Gang-up, aligned waves, help-ally (planned) | ✗ | ✗ | ✓ |
| Multi-pronged attacks, transport invasions, flank micro (planned) | ✗ | ✗ | ✓ |

## 6. Sequencing

- **Phase 0, shipped in 4.1.0:** W1.1 bug fixes; AI Boost's scatter-on-launch and send-percentage
  ported into AI_Attack (harvesters exempt from scatter, a dock-approach hazard; defences counted
  by an armed-building scan; thresholds 80/95/100%, internal constants; unsent armed units stand
  GUARD_AREA at home; the TD and TS engineers join RENOVATOR in the engineer hunt clause); the build-choice
  diagnostic (TF_AI_DIAG: per-cycle candidate POOL and WIN in `MOD_DEBUG_AI.txt`). The Temple
  starvation (the first candidate at top urgency in scan order always won, so the Temple never did)
  is fixed by **frame-based starvation ageing** (5.0.0): the first top-urgency candidate
  in scan order still wins, unless one at top urgency has waited at least `STARVE_FRAMES` (7500)
  frames, when the longest-waiting wins. It is measured in frames, not decision cycles: with half a dozen
  candidates tied at MEDIUM, a cycle count let the late-scan defences jump the queue in turn. Ageing replaced a
  uniform random tie-break.
- **Phase 1, shipped in 4.1.0:** W7 maps each AI's difficulty to an IQ tier
  (Easy=3, Normal=4, Hard=MaxIQ, `TF_AI_IQ_From_Difficulty`) with stat handicaps left at 1.0x and
  IQProduction lowered 5→3; W1.5 allows one AI order per factory category, ending the
  parallel-build cheat and the FactoryMax heap exhaustion; W1.2 records per-house discovery for
  AI houses (`IsDiscoveredByPlayerMask`), gates `Evaluate_Object` and `Special_Weapon_AI` on it,
  and reveals an attacker to its victim; W1.3 sends blind hunters to probe start positions (least
  recently probed first, so scouts sent together fan out; distance only breaks ties,
  `TF_Scout_Destination`), and
  the Expert_AI blind-scout dispatcher keeps two scouts out while a house knows no enemy
  building (fair fog otherwise produced a four-way turtle). The client's `CNC_Set_Difficulty`
  always sends 1, so difficulty comes from the per-slot lobby read (`lobby-difficulty-ram-spike.md`)
  with `Documents/CnCRemastered/tf_ai_difficulty.txt` as the fallback. Residual (W1.2): once-seen
  enemy units stay evaluable while fogged; buildings fog correctly.
- **Phase 2 (the enabler):** W2 faction separation + buildability, independent of Phases 0 and 1.
- **Phase 3 (the brain):** W3 build planner + placement; W4 attack quality (Route A spike first).
- **Phase 4 (capabilities):** W5 naval → transports → RA supers → special units; W6
  coordination; W8 directional armour (can land any time after Phase 0 — independent).
- **Pathfinding (W1.4 reservation table):** its own track; schedule around the behaviour
  phases (highest-risk drive.cpp work — don't overlap with W4 soak).
- Every phase: dev-build diagnostic logging in from day one (logs-first rule), desktop
  soak matches, playtest gates before the next phase.

## 7. References + attribution
- `reference/ai-boost2/` — AI Boost 3.2 (Bast75 & xXMini FrankiXx, GPL v3 + EA terms,
  licence checked). Port sources: scatter-on-launch, send-percentage, IC/Chrono
  usage, special-unit handling, counter-building, naval-war detection, primary-factory.
  Both authors are credited in the Workshop and ModDB acknowledgements (their fork bundles
  CFE 1.8, so attribute per feature).
- OpenRA pathfinder (MIT) — design reference for W1.4.
- `AIBOOST.INI` — reference for which dials modders/players expect; the policy remains lobby
  difficulty + rules.ini dials, no separate user INI.

## 8. Open decisions
1. Blob route A vs B — after the Route-A spike.
2. Reverse move — after directional-armour playtests.
3. Free-helicopter-with-pad rule under faction pads — trivially "pad's own faction's bird".
4. Per-behaviour difficulty tier assignments — reviewed as each behaviour lands.
5. **Settled: TD's defences and power.** TD hard-gates the AGT's fire (TD `building.cpp:3128`, the STRUCT_ATOWER
   check) and the Obelisk's charging (TD `building.cpp:1022`, charge dumped on power loss) at
   `Power_Fraction < 1`; the SAM has no gate. TF's TDOBLI is TD-correct through its weapon's `Charges=yes` and
   `Charging_AI` (the same gate and charge-dump), so only `[TDATWR]` carries `Powered=true`; TDSAM stays unpowered
   (TD-authentic). Do NOT add Powered to TDOBLI: TD gates only the charge chain, and doubling the gate
   adds nothing. AI note: Check_Build_Power's armed-powered-building scan fires for
   GDI (AGT) and Soviets (Tesla) once W3 revives the strategy layer.
