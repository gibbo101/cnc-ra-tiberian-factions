# AI Improvements — Research Findings

Investigation of three long-standing AI behaviour gaps in vanilla Red Alert
Remastered skirmish. All three trace back to the same architectural issue and
all are **pure DLL changes** — no INI path exists for any of them.

**Status:** Research complete. Implementation deferred until four-faction core
(GDI/Nod buildings) is landed and stable.

---

## Root cause (shared)

The AI production code was written assuming `Session.Type == GAME_NORMAL`
(single-player campaign with hand-authored BaseNode lists and TeamTypes).
Remastered skirmish runs as `GAME_GLYPHX_MULTIPLAYER`
(`dllinterface.cpp:1565`, `1660`; enum at `session.h:121-130`), so the
campaign code paths are skipped and the AI relies on thin dynamic fallback
logic. That fallback has gaps and bugs which manifest as the three symptoms
below.

---

## Problem 1 — AI never builds a Radar Dome (and so never reaches tech)

### Symptom
Computer opponents skip the Radar Dome unless the human player builds an
aircraft. No dome → tech center prereq fails → no Chronosphere, Iron Curtain,
MSLO, GPS, MIG, Longbow.

### Root cause
In `HouseClass::AI_Building` (`house.cpp:5761`), `STRUCT_RADAR` is **only**
queued from inside the air-defence block (`house.cpp:5944-5980`), and that
block only runs when `airthreat == true` — which requires an enemy house to
own at least one aircraft.

```cpp
// house.cpp ~5970
if (airthreat) {
    if (BQuantity[STRUCT_RADAR] == 0) {
        b = &BuildingTypeClass::As_Reference(STRUCT_RADAR);
        if (Can_Build(b, ActLike) && (b->Cost_Of() < money || hasincome)) {
            choiceptr = BuildChoice.Alloc();
            if (choiceptr != NULL) {
                *choiceptr = BuildChoiceClass(URGENCY_HIGH, b->Type);
            }
        }
    }
    ...
```

The campaign BaseNode path at `house.cpp:5768-5773` is gated on
`Session.Type == GAME_NORMAL` and is therefore skipped in skirmish — leaving
the dynamic block as the **only** producer of build choices.

### Fix
Hoist the dome queue out of the `airthreat` conditional. Queue it once the
base has power + refinery + barracks + war factory. Smallest surgical change
with the biggest downstream unlock — every higher-tier building and
super-weapon becomes reachable.

---

## Problem 2 — AI never builds naval units

### Symptom
On water maps, the AI never produces destroyers, cruisers, subs, or
missile-subs even when it owns a sub pen or naval yard.

### Root cause
`HouseClass::AI_Vessel` (`house.cpp:6265`) wraps its **entire body** in
`if (Session.Type == GAME_NORMAL)`. In skirmish, nothing inside ever runs,
so `BuildVessel` stays `VESSEL_NONE` permanently. A belt-and-braces clear at
`house.cpp:6369-6371` resets it whenever `IsBaseBuilding` is true anyway.

```cpp
// house.cpp:6265
int HouseClass::AI_Vessel(void)
{
    ...
    if (Session.Type == GAME_NORMAL) {        // entire body gated on campaign
        ...
    }

    if (IsBaseBuilding) {
        BuildVessel = VESSEL_NONE;
    }

    return (TICKS_PER_SECOND);
}
```

Unlike `AI_Unit`, `AI_Infantry`, `AI_Aircraft`, `AI_Building` — all of which
have dynamic skirmish branches — `AI_Vessel` has **no dynamic path at all**.
Vessel production is entirely TeamType-driven, and skirmish has no
hand-authored TeamTypes containing vessels.

### Fix
Add a skirmish branch to `AI_Vessel` modelled on `AI_Unit`'s structure:
scan for `STRUCT_SUB_PEN` ownership (and optionally nearby water cells), then
queue `VESSEL_SS` / `VESSEL_DD` / `VESSEL_CA` / `VESSEL_MISSILESUB` based on
tech level and money.

---

## Problem 3 — AI never builds or uses super-weapons

Compound problem with four sub-causes.

### 3a — Downstream of Problem 1
MSLO, Chronosphere, Iron Curtain, GPS all require the tech center → which
requires the Radar Dome. Until Problem 1 is fixed, the AI literally cannot
build any of these structures. **Fix Problem 1 first; this becomes mostly
moot.**

### 3b — Half the supers have no AI fire dispatch
In `HouseClass::Super_Weapon_Handler` (`house.cpp:1523`), only four supers
have the `if (Is_Ready() && !IsHuman) Special_Weapon_AI(...)` pattern:

- NUKE — `house.cpp:1835`
- SPY — `house.cpp:1881`
- PARABOMB — `house.cpp:1913`
- PARAINF — `house.cpp:1945`

The Iron Curtain block (`1731-1776`), Chronosphere block (`1662-1724`), and
Sonar Pulse block (`1783-1807`) handle availability and removal but contain
**no AI-fire call**. Even if the AI builds and charges these supers, nothing
fires them.

### 3c — Iron Curtain & Chronosphere targeting reads the mouse
Even if you patched 3b in, the `Place_Special_Blast` cases at
`house.cpp:2997-3030` (Iron Curtain) and `3032-3073` (Chronosphere) read
`Keyboard->MouseQX` / `MouseQY` to pick targets:

```cpp
// house.cpp:2999
case SPC_IRON_CURTAIN:
    if (SuperWeapon[SPC_IRON_CURTAIN].Is_Ready()) {
        int x = Keyboard->MouseQX - Map.TacPixelX;
        int y = Keyboard->MouseQY - Map.TacPixelY;
        TechnoClass* tech = Map[cell].Cell_Techno(x, y);
        ...
```

For an AI fire there's no mouse — the AI would target whatever happens to be
under the human's cursor, or nothing. These cases need an AI-aware code path
that picks the unit/cell directly without consulting `Keyboard`.

The nuke's AI target picker at `house.cpp:2787-2817` (random weighted by
enemy building value, 90% chance) is the template the others should follow.

### 3d — Parabomb gated to campaign
`house.cpp:1918-1919` includes `&& Session.Type == GAME_NORMAL` on the enable
check. AI cannot acquire the parabomb super in skirmish at all, regardless of
whether it has an airstrip. One-line fix.

### 3e — IQ floor (informational)
All AI super-weapon acquisition checks include
`(IsHuman || IQ >= Rule.IQSuperWeapons)`. Default is `IQSuperWeapons = 4`
(`rules.cpp:138`), with `IQ` ramping over time. Not a blocker but worth
tuning for difficulty.

### Fix
- 3a: fix Problem 1.
- 3b: add `Special_Weapon_AI(SPC_IRON_CURTAIN)` and
  `Special_Weapon_AI(SPC_CHRONOSPHERE)` calls into their
  `Super_Weapon_Handler` blocks, mirroring the nuke pattern.
- 3c: rewrite the Iron Curtain / Chronosphere `Place_Special_Blast` cases to
  accept an AI-supplied cell directly. Don't read `Keyboard` when `!IsHuman`.
- 3d: drop the `Session.Type == GAME_NORMAL` gate from line 1919 (and
  arguably from the Chronosphere `Session.Type != GAME_NORMAL` check at
  line 1700).

---

## Suggested implementation order

1. **Problem 1** — hoist dome queue out of `airthreat` block
   (`house.cpp:5970`). Smallest change, biggest unlock.
2. **Problem 2** — add skirmish branch to `AI_Vessel` (`house.cpp:6275`).
3. **Problem 3b/c** — add Iron Curtain + Chronosphere AI dispatch, rewrite
   their `Place_Special_Blast` cases to not read `Keyboard` when `!IsHuman`.
4. **Problem 3d** — drop `GAME_NORMAL` gate on parabomb (line 1919).

---

## Reference — key files & functions

- `redalert/house.cpp`
  - `HouseClass::AI()` — `house.cpp:1040`
  - `HouseClass::Super_Weapon_Handler()` — `house.cpp:1523`
  - `HouseClass::Special_Weapon_AI()` — `house.cpp:2787`
  - `HouseClass::Place_Special_Blast()` — `house.cpp:2842`
  - `HouseClass::Expert_AI()` — `house.cpp:4939`
  - `HouseClass::AI_Base_Defense()` — `house.cpp:5678`
  - `HouseClass::AI_Building()` — `house.cpp:5761`
  - `HouseClass::AI_Unit()` — `house.cpp:6127`
  - `HouseClass::AI_Vessel()` — `house.cpp:6265`
  - `HouseClass::AI_Infantry()` — `house.cpp:6391`
  - `HouseClass::AI_Aircraft()` — `house.cpp:6598`
- `redalert/base.cpp` — BaseNode mechanism; `Next_Buildable()` at `base.cpp:377`
  (only consulted in `GAME_NORMAL`)
- `redalert/session.h:121` — `GameEnum` confirming `GAME_GLYPHX_MULTIPLAYER`
- `redalert/dllinterface.cpp:1565,1660` — where skirmish is typed as
  `GAME_GLYPHX_MULTIPLAYER`
- `redalert/rules.cpp:138` — `IQSuperWeapons = 4` default

---

# Harvester logic improvements

Investigation of harvester ("ore truck") behaviour — both AI and player-owned.
Symptoms observed: harvesters get stuck near refineries, wander to dangerous
ore patches near enemy bases, and queue up at one refinery while another sits
idle.

**Status:** Research complete. Implementation deferred until four-faction
core lands.

## Problem 4 — Harvesters get permanently stuck

### Symptom
Harvester sits idle near a refinery or in the field. Not docking, not
collecting. Sometimes after finishing unload, sometimes after another
harvester takes its dock slot, sometimes after returning from a depleted
patch.

### Root cause
The per-house latch `HouseClass::IsTiberiumShort` is set to `true` at
`unit.cpp:2977` whenever a harvester's expanding-ring scan fails to find
ore — **and is never reset to `false` anywhere in the codebase** (verified
across `house.cpp`, `house.h`, `unit.cpp`).

```cpp
// unit.cpp:2964-2979 (state LOOKING, nothing found, no ArchiveTarget)
} else {
    Status = GOINGTOIDLE;
    IsUseless = true;
    House->IsTiberiumShort = true;   // latch — never reset
    return (TICKS_PER_SECOND * 7);
}
```

The AI's only auto-re-queue path is gated on the latch — `unit.cpp:3814`:

```cpp
if (!House->IsHuman && Class->IsToHarvest && House->Get_Quantity(STRUCT_REFINERY) > 0
    && !House->IsTiberiumShort) {
    Assign_Mission(MISSION_HARVEST);
```

Once the latch trips:
- AI harvesters never auto-re-queue from `Mission_Guard`.
- AI harvester replacement is disabled (`house.cpp:6140`, `IQHarvester` path).
- AI refinery building is disabled (`house.cpp:5797, 5831`).

**Human harvesters are even worse off:** the auto-re-queue at `unit.cpp:3814`
is also gated on `!House->IsHuman`. A player-owned harvester that hits
`GOINGTOIDLE` and gets shoved into `MISSION_GUARD` just sits there until the
player manually issues a move order.

### Other stuck modes
- **Refinery contention loop** in FINDHOME (`unit.cpp:3023-3050`): if
  `Find_Best_Refinery` returns NULL and the `ScenarioInit++` retry also
  fails, the harvester sits in FINDHOME with no NavCom — silent stuck state.
- **`GOINGTOIDLE` fall-through bug** at `unit.cpp:3065-3074`: the
  `if (IsUseless)` branch sets `MISSION_REPAIR` or `MISSION_HUNT`, then
  **falls through** to an unconditional `Assign_Mission(MISSION_GUARD)` two
  lines later that immediately overwrites it. Missing `return` or `else`.
  Free bug-fix sitting there — REPAIR/HUNT from this path currently never
  fire.
- **Unload-pad clear-out** (`unit.cpp:1759-1774`): after unloading, if
  `ArchiveTarget` is invalid, the harvester just `Scatter()`s and falls out
  of the harvest mission with no re-queue.

### Fix
Pure DLL change.
- Reset `IsTiberiumShort` periodically in `HouseClass::AI` (e.g. when
  `Map.Total_Tiberium() > 0` and a refinery exists). ~5 lines.
- Drop the `!House->IsHuman` gate at `unit.cpp:3814` so player harvesters
  also auto-re-queue. One token.
- Fix the `GOINGTOIDLE` fall-through with a `return` or `else`. One line.

---

## Problem 5 — Harvesters drive into enemy territory

### Symptom
Harvesters cheerfully drive to an ore patch deep in enemy base territory,
get shot up, and either die or limp home — often while closer safer patches
exist.

### Root cause
**There is zero threat-awareness code in any harvester path.** The
expanding-ring ore search (`Goto_Tiberium` at `unit.cpp:2302-2372`) and the
cell scoring (`Tiberium_Check` at `unit.cpp:2240-2283`) consider only land
type, overlay type, fog-of-war, and movement zone. Enemy positions are not
consulted.

```cpp
// unit.cpp:2240 — only inputs are terrain/overlay/zone/fog
int UnitClass::Tiberium_Check(CELL& center, int x, int y) const
{
    ...
    if (Map[cell].Land_Type() == LAND_TIBERIUM
        && Map[cell].Zones[Class->MZone] == Map[center].Zones[Class->MZone]
        && Map[center].Is_Mapped(PlayerPtr)
        && !Map[cell].Cell_Techno()) {
        return (Map[cell].OverlayData + 1) * value;
    }
    return 0;
}
```

The `ArchiveTarget` cache at `unit.cpp:2945` makes it worse: it pushes the
last-harvested cell onto NavCom *before* the ring scan runs, so a harvester
that successfully harvested deep in enemy territory once will keep going
right back there.

The only "danger" reactions in the codebase are post-hoc damage responses
(`unit.cpp:1179-1193`, flee to refinery when below `ConditionYellow` with
ore on board) and the AI alert call (`unit.cpp:1200-1202`,
`Base_Is_Attacked`). Nothing biases path selection *away* from danger.

### Fix
Pure DLL change. Cleanest injection point is `Tiberium_Check`:

```cpp
// Pseudocode for proposed change in Tiberium_Check
int base_value = (Map[cell].OverlayData + 1) * value;
int threat_penalty = Compute_Enemy_Proximity_Penalty(cell);
return base_value * threat_penalty;  // fixed 0.0–1.0
```

Compute `threat_penalty` by scanning each enemy house's known structures
(respecting fog via `Is_Mapped`), measure distance to the candidate cell,
and scale down when within an "avoid radius."

Proposed new INI knobs under `[AI]`:
- `OreAvoidRadius=` — cells around enemy structures to penalise (e.g. 12)
- `OreThreatWeight=` — fixed 0.0–1.0 scaling factor inside avoid radius

This composes cleanly with the existing best-on-ring picker because it's
just a weight adjustment — closer-safer patches naturally outscore
farther-dangerous ones without restructuring the search.

---

## Problem 6 — Refinery selection has a sticky cache and no idle-awareness

### Symptom
Two harvesters queue at refinery A while refinery B sits idle. Harvesters
return to their previous refinery even when a closer/idle alternative
exists.

### Root cause
`Find_Best_Refinery` (`unit.cpp:4464-4485`) has a one-slot cache
(`TiberiumUnloadRefinery`) that bias-locks to the previous unload site:

```cpp
if (Target_Legal(TiberiumUnloadRefinery)) {
    BuildingClass* refinery = As_Building(TiberiumUnloadRefinery);
    if (refinery != NULL && refinery->House == House && !refinery->IsInLimbo
        && refinery->Mission != MISSION_DECONSTRUCTION
        && *refinery == STRUCT_REFINERY
        && Map[refinery->Center_Coord()].Zones[...] == Map[Center_Coord()].Zones[...]) {
        return refinery;   // stick with last one regardless of distance/busy
    }
}
```

Fallback is `Find_Docking_Bay` (`techno.cpp:6332-6376`) which picks closest
with a non-busy radio — but if all refineries are busy, returns NULL.
`Mission_Harvest` FINDHOME then sets `ScenarioInit++` to force a ROGER, but
only at the *closest* refinery, not the next-closest. So two harvesters can
pile up at refinery A while refinery B sits empty.

### Fix
Pure DLL change.
- Break distance ties in `Find_Docking_Bay` (`techno.cpp:6368`) in favour of
  idle refineries. ~15 lines.
- Add a sanity check to the cache lookup in `Find_Best_Refinery`: invalidate
  if cached refinery is busy and another is closer/idle.

---

## rules.ini tunables (existing — informational)

| INI key | Section | Default | Effect |
|---|---|---|---|
| `OreNearScan` | `[AI]` | 6 cells | Search radius when current patch depleted |
| `OreFarScan` | `[AI]` | 32 cells | Search radius on initial search from refinery |
| `BailCount` | `[General]` | 28 | Bails per full load |
| `OreTruckRate` | `[General]` | 2 | Harvest/dump animation speed |
| `GoldValue` | `[General]` | 35 | Credits per gold bail (also patch weight) |
| `GemValue` | `[General]` | 110 | Credits per gem bail (×4 in patch weight) |
| `IQHarvester` | `[IQ]` | (varies) | IQ floor for AI auto-replace harvesters |
| `RefineryRatio` | `[AI]` | (varies) | AI refinery build ratio |

**No INI knob exists for**: threat-avoidance, latch reset, contention
behaviour, or cache freshness. All harvester fixes are DLL changes.

---

## Suggested implementation order (harvesters)

Ranked by impact-vs-effort.

1. **Reset `IsTiberiumShort` periodically** — TINY effort, HIGH impact.
   ~5 lines in `HouseClass::AI`. Fixes "AI suddenly stopped harvesting
   forever" failure mode.
2. **Drop the `!House->IsHuman` gate at `unit.cpp:3814`** — TINY effort,
   HIGH impact. One-token change. Combined with #1, addresses ~90% of "my
   harvester is just sitting there" complaints.
3. **Fix the `GOINGTOIDLE` fall-through bug** at `unit.cpp:3065-3074` —
   TINY effort, LOW-MEDIUM impact. Add `return` or `else`.
4. **Idle-aware refinery selection** in `Find_Docking_Bay` — SMALL effort,
   MEDIUM impact. ~15 lines. Eliminates "two harvesters queue at A while B
   sits empty" pattern.
5. **Threat-aware ore scoring** in `Tiberium_Check` — MEDIUM effort,
   MEDIUM-HIGH impact. ~40 lines + 2 new INI knobs. Directly addresses
   "harvester wanders to ore patches near enemy bases" gripe.

---

## Reference — key files & functions (harvesters)

- `redalert/unit.cpp`
  - `UnitClass::Mission_Harvest()` state machine — `unit.cpp:~2900`
  - `UnitClass::Tiberium_Check()` — `unit.cpp:2240`
  - `UnitClass::Goto_Tiberium()` — `unit.cpp:2302`
  - `UnitClass::Find_Best_Refinery()` — `unit.cpp:4464`
  - `GOINGTOIDLE` case with fall-through bug — `unit.cpp:3065-3074`
  - Mission_Guard auto-re-queue — `unit.cpp:3814`
  - LOOKING-with-nothing-found latch set — `unit.cpp:2964-2979`
  - Post-damage flee-to-refinery — `unit.cpp:1179-1193`
- `redalert/techno.cpp`
  - `TechnoClass::Find_Docking_Bay()` — `techno.cpp:6332`
- `redalert/house.cpp`
  - `HouseClass::IsTiberiumShort` initialised — `house.cpp:586`
  - AI harvester replacement gate — `house.cpp:6140`

---

# Pathfinding — options considered

Separate concern from the AI behaviour fixes above. Harvesters (and other
units) get stuck around chokepoints — most visibly at refinery docks — when
friendly units block the planned path. This is a **traffic/cooperation
problem, not a path-search problem**. A* alone does not fix it.

**Status:** Background research only. Not on the implementation roadmap
yet — too large a lift to attempt before the four-faction core is stable.
This section is a reference for when we revisit pathfinding properly.

## The real problem

The existing pathfinder (greedy iterative search in `findpath.cpp`) finds
a route at the moment the move starts. The bug fires *after* the path is
committed:

- Another unit moves into a cell along the planned path.
- The harvester arrives at the cell, finds it occupied, and **doesn't
  re-path** — it stops, scatters, or waits for the cell to clear.
- Around a refinery dock, multiple units hit this state simultaneously and
  deadlock.

Swapping in a better path-search algorithm gives prettier routes but
doesn't change the per-cell collision behaviour.

## Search algorithms (find *a* route)

| Approach | What it gives you | Relevance for RA |
|---|---|---|
| **A\*** | Optimal baseline. | The yardstick. |
| **JPS** (Jump Point Search, Harabor 2011) | 10–30× faster than A\* on uniform grids by skipping symmetric paths. Drop-in replacement. | **High** — RA is a uniform grid. Clean win for path quality + perf. |
| **JPS+** (~2014) | Precomputed JPS, ~100× A\*. Needs map preprocessing. | Medium — perf is fine without it for RA-sized maps. |
| **HPA\*** (Botea 2004) | Formalised hierarchical pathfinding — the TS approach done properly. | Medium — overkill unless maps get huge. |
| **Flow fields** (SupCom 2 / Planetary Annihilation, ~2007) | Compute one gradient field per destination; all units follow it for free. | **High for harvester fleets** — N harvesters → same ore field is the textbook flow-field case. |
| **NavMesh** (Recast/Detour, 2009) | Industry standard for non-grid 3D games. | Low — RA is grid-based. Wrong fit. |

## Collision / cooperation (resolve *who goes where*)

This is the layer that actually fixes the dock-stuck bug.

| Approach | What it does |
|---|---|
| **Reservation tables** (TS shipped this) | Each unit publishes its path; others route around. |
| **WHCA\*** (Windowed Hierarchical Cooperative A\*, Silver 2005) | Modern formalisation of reservation tables. Path search aware of N future ticks of other units' plans. |
| **ORCA / RVO** | Each agent predicts collisions and adjusts velocity. Standard in modern games for fluid crowd movement. Assumes continuous motion — needs adapting for grid-stepped units. |
| **Cooperative yield/push** (TS shipped this too) | Idle blockers get asked to step aside. Simple and effective. |

## Realistic picks for an RA Remastered mod

Ranked by impact-vs-effort for *our specific complaints* (dock-stuck,
chokepoint deadlock):

1. **Reservation table + scatter-the-blocker** — the TS retrofit, applied
   surgically. Maintain a map-sized array of "cell reserved at tick T by
   unit X." Pathfinder treats reserved cells as soft obstacles. When
   blocked by a stationary friendly, trigger that unit's `Scatter()`
   instead of waiting. **~1–2 weeks. Highest value for lowest risk. Solves
   the dock-stuck bug directly.**
2. **JPS** — replace the current path search wholesale. Cleaner routes,
   faster pathing. Does **not** fix the dock-stuck bug on its own. ~1–2
   weeks. Pairs well with #1.
3. **Flow fields for harvester fleets** — when 4–5 harvesters are all going
   to the same ore field, one flow field beats 5 independent paths. Niche
   but elegant. ~1 week.
4. **WHCA\*** — the "do it properly" option. Replaces both path search and
   collision system. ~1 month, high risk. Probably overkill for a mod.
5. **ORCA-style local avoidance** — beautiful in motion but assumes
   sub-cell movement. RA moves cell-by-cell. Adapting it means fighting
   the engine. Skip.

## Reference implementations

- **OpenRA** (open-source C&C reimplementation) already implements a
  WHCA\*-style cooperative pathfinder with reservation tables, specifically
  because they hit the same dock-stuck problem. MIT-licensed. Relevant
  code is in `OpenRA.Mods.Common/Traits/World/PathFinder*.cs`. **Closest
  existing reference for "what would good pathfinding look like in this
  exact game."**
- **0 A.D.** — hybrid long-range (JPS-like) + short-range custom.
- **Spring/BAR** — flow fields + per-unit local avoidance.

## Recommendation

For when we revisit this: read OpenRA's pathfinder for ideas, then
implement the minimum viable port — **reservation table + scatter-the-
blocker**, optionally with **JPS** as a perf bonus. That's the TS
philosophy applied with 25 years of hindsight, and directly addresses
the observed bugs without rewriting half the engine.

The full modern stack (JPS+ + WHCA\* + flow fields + ORCA) is what AAA
RTS use. Not needed for a 1996 game with ~50 units on screen. The real
bottleneck isn't algorithmic quality — it's that the current code commits
to a path and doesn't replan when reality changes.

---

# Option to pursue — AI attack teams use attack-move (added 2026-06-11)

Our attack-move port (CFE Patch Redux) is purely player-input driven: it enters the
game only through `What_Action()` and the click handlers, travels as a player event
(`MISSION_ATTACKMOVE` → converted in `event.cpp` to `MISSION_MOVE` + the per-unit
`AttackMove` flag + `RememberedNavCom`), and nothing in the AI's mission-assignment
code ever issues it. The skirmish AI's rough equivalent today is `MISSION_HUNT` /
guard-area behaviour.

**The option:** have AI attack teams use true attack-move — "fight your way to the
target instead of beelining, then resume the journey after each fight." The plumbing
is now in place per-unit; an AI house could set `AttackMove = 1` +
`RememberedNavCom` directly on team members when dispatching an attack wave (no
event needed — AI assigns missions directly, and the flag+target pair is the whole
state machine). Candidate hook points: TeamClass mission scripts (`TMISSION_ATTACK`
dispatch) or `HouseClass::AI` raid assembly. Benefits: attack waves that don't
ignore harassment en route, and that regroup toward the original objective after a
skirmish instead of scattering into hunt mode. Risks: interacts with team
coordination logic (`Coordinate_Attack`), so needs its own playtest soak; keep it
behavioural per the difficulty philosophy (no stat biases).

**Why this matters for difficulty (Luke, 2026-06-13):** the player-facing attack-move
got a threat-response layer during playtest — a unit hammering a passive building
disengages to deal with defences / enemy units that come into range, then resumes
(docs/cfe-port-plan.md §1.2). Today the AI's big weakness is the opposite: an AI raid
that locks onto a building at the back of your base beelines there and soaks every
turret and counter-attack on the way, so it's trivial to pick off. Reusing the SAME
`AttackMove` + threat-response machinery for AI raids fixes exactly that — the wave
fights through your defences instead of feeding itself to them. This is a behavioural
difficulty win (no stat biases), so it fits the difficulty philosophy cleanly. The
per-unit plumbing AND the threat-response are already built and player-verified; the
only new work is the AI dispatch hook.

Status: idea logged at Luke's direction (2026-06-11), reinforced 2026-06-13 after the
threat-response landed. Not scheduled. Pairs well with the A*-stage-2 reservation-layer
work since both touch movement cooperation.

# Broad-sweep findings (combat, strategy, difficulty, misc)

Open-ended audit of the AI engine beyond the targeted topics above. These
findings range from "single-token critical fixes" to "entire systems
compiled out via `#ifdef NEVER`."

**Status:** Research complete. Implementation deferred.

## Problem 7 — `Greatest_Threat` area-scan never updates `bestval`

### Symptom
AI units consistently pick odd targets — often the last legal target
evaluated in their scan range, not the highest-value one. Manifests as "AI
feels dumb at target selection."

### Root cause
In `TechnoClass::Greatest_Threat` (`techno.cpp:2126`), the four expanding-
ring scan branches (top row, bottom row, left col, right col) all do:

```cpp
// techno.cpp:2271-2274 (and similar at 2287, 2315, 2330)
if (Evaluate_Cell(method, mask, newcell, range, &object, value, zone)) {
    if (bestval < value) {
        bestobject = object;
        // bestval = value;  <-- MISSING
    }
}
```

**`bestval` is never assigned inside the area-scan branch.** It stays at its
initial `-1`. Every subsequent successful `Evaluate_Cell` whose `value > -1`
(all of them) updates `bestobject`, regardless of whether that target is
actually worse than the last one. The whole-map fallback path
(`techno.cpp:~2350+`) does update `bestval` correctly — so the bug only
fires on area-limited scans, which is what most units use via
`Threat_Range`.

### Fix
Four-token fix: add `bestval = value;` inside each of the four
`if (bestval < value)` blocks. Pure DLL change. Probably the single
highest-leverage change in this entire document.

---

## Problem 8 — `Expert_AI` strategy layer is mostly stubs

### Symptom
AI's "strategic" tier evaluates the situation every 5 game seconds and
dispatches to strategy handlers — but almost nothing happens.

### Root cause
`HouseClass::Expert_AI` (`house.cpp:4939`) runs 10 Check/Act strategy pairs.
Findings from auditing each:

| Strategy | `Check_*` returns | `AI_Build_*` action |
|---|---|---|
| BUILD_POWER  | computed correctly | **`return false;`** stub (`house.cpp:5466`) |
| BUILD_DEFENSE| **`URGENCY_NONE`** stub (`house.cpp:5272`) | **`return false;`** stub (`5477`) |
| BUILD_OFFENSE| **`URGENCY_NONE`** stub (`5284`) | **`return false;`** stub (`5488`) |
| BUILD_INCOME | **`URGENCY_NONE`** stub (`5314`) | **`return false;`** stub (`5499`) |
| BUILD_ENGINEER | **`URGENCY_NONE`** stub (`5342`) | **`return false;`** stub (`5521`) |
| FIRE_SALE    | functional | functional |
| RAISE_MONEY  | functional | functional |
| RAISE_POWER  | functional | functional |
| LOWER_POWER  | functional | functional |
| ATTACK       | functional | functional (`AI_Attack` at `5402`) |

Of ten strategy slots, **four (DEFENSE, OFFENSE, INCOME, ENGINEER) never
urgency-trigger because their `Check_*` is hardcoded to `URGENCY_NONE`**,
and **five `AI_Build_*` callbacks are `return false` stubs.** The
"strategic AI layer" effectively does: fire-sale, sell-to-raise-resources,
and attack. Everything adaptive is missing.

### Fix
Pure DLL changes. Each stub is ~10-30 lines of real implementation.
Biggest leverage from filling in Check_Build_Defense + AI_Build_Defense
(see Problem 9).

---

## Problem 9 — `AI_Base_Defense` is compiled out

### Symptom
AI builds defensive structures (pillbox, turret, tesla, SAM, AA gun)
according to static `Rule.DefenseRatio` ratios — with zero awareness of
where attacks are coming from. Tank-rush from the south? AI builds the
next pillbox wherever the placement code feels like it.

### Root cause
`HouseClass::AI_Base_Defense` (`house.cpp:5678`) is wrapped in
`#ifdef NEVER` (lines 5662 and 5744). The function body is incomplete and
**never compiled or called from anywhere** (grep confirms only doc-comment
refs and the dead body). The only actual defensive-structure logic lives
inside `AI_Building`'s static ratio code.

### Fix
Pure DLL change. Three parts:
1. Remove the `#ifdef NEVER` wrapper.
2. Complete the function body (it's incomplete — computes `nothreat` but
   never acts on it).
3. Wire it into `AI()`'s scheduler, paired with implemented
   Check_Build_Defense + AI_Build_Defense (Problem 8).

Largest lift in this document — ~100-300 lines total — but the biggest
behavioural improvement.

---

## Problem 10 — Difficulty selector is a complete no-op in skirmish

### Symptom
Easy / Normal / Hard difficulty in the skirmish launcher has no effect.
Every game plays identically.

### Root cause
**Smoking gun at `dllinterface.cpp:2143-2148`:**

```cpp
extern "C" __declspec(dllexport) void __cdecl CNC_Set_Difficulty(int difficulty)
{
    if (GAME_TO_PLAY == GAME_NORMAL) {
        Set_Scenario_Difficulty(difficulty);
    }
}
```

Skirmish runs as `GAME_GLYPHX_MULTIPLAYER`, not `GAME_NORMAL`, so the
launcher's difficulty value is **silently dropped**. `Scen.Difficulty`
keeps its initialization value (`DIFF_NORMAL` from `init.cpp:507-508`).

Then at `dllinterface.cpp:1290`, every skirmish house — player and AIs
alike — gets:

```cpp
housep->Assign_Handicap(Scen.Difficulty);  // always DIFF_NORMAL in skirmish
```

So every house in every skirmish game gets `DIFF_NORMAL` handicap
regardless of launcher choice. All `DifficultyClass` bias multipliers
(firepower, speed, armor, ROF, cost, build speed) come out as 1.0× for
everyone.

### Compounding bug — Hard AI disables harvester replacement
Even if you fix the gate above, there's a second problem at
`house.cpp:6140`:

```cpp
if (IQ >= Rule.IQHarvester && !IsTiberiumShort && !IsHuman
    && BQuantity[STRUCT_REFINERY] > UQuantity[UNIT_HARVESTER]
    && Difficulty != DIFF_HARD) {                    // <-- inverted intuition
    BuildUnit = UNIT_HARVESTER;
```

**Hard difficulty AI has harvester auto-replace explicitly disabled.**
Combined with the never-reset `IsTiberiumShort` latch (Problem 4), a
Hard-difficulty AI that loses a harvester or has the latch trip is
permanently unable to recover its economy. Easy/Normal AI auto-replaces.

This bug is currently latent because of the launcher gate (no AI ever gets
DIFF_HARD in skirmish), but it'd surface immediately on fixing Problem 10.

### Fix — design preference: behavioural difficulty only
**Project design philosophy:** difficulty levels differ in AI **behaviour**
(smarter, more aggressive on hard; dumber, docile on easy), **not in stat
multipliers** (firepower, speed, armor, ROF, cost, build speed). Symmetric
unit performance preserves the game's tactical identity across difficulty
levels.

This means the current skirmish baseline (every house gets `DIFF_NORMAL`,
all `DifficultyClass` bias multipliers = 1.0×) is **actually correct and
should be preserved**. Do **not** port the campaign `CDifficulty` /
`Difficulty` inversion from `init.cpp:683-750` — that's exactly the
stat-multiplier path we want to avoid.

Instead, the difficulty selector should drive **behavioural levers**:

- **IQ thresholds** — `Rule.IQ*` (IQSuperWeapons, IQHarvester, IQProduction,
  IQGuardArea, etc.) already gate AI behaviours throughout the codebase.
  Easy = low IQ ceiling, Hard = high IQ ceiling. Infrastructure exists.
- **AttackInterval / AttackDelay** (INI-tunable already) — Hard AI attacks
  more often.
- **Build priorities / urgency** — Hard AI rushes toward tech-center; Easy
  AI lingers on basic units.
- **Strategy enablement** — naval production, super-weapon use, adaptive
  base defense placement only kick in above certain difficulty thresholds.
- **Map awareness** — Hard AI scouts actively; Easy AI sits in base.

Pure DLL changes:
- Drop `if (GAME_TO_PLAY == GAME_NORMAL)` from `CNC_Set_Difficulty`
  (`dllinterface.cpp:2145`) so the launcher value reaches the engine.
- **Don't** call `Assign_Handicap(Scen.Difficulty)` for skirmish houses —
  leave them at `DIFF_NORMAL` so stat biases stay symmetric.
- Plumb the difficulty value to a new behavioural-tuning layer (most
  naturally hooked into the `Expert_AI` strategy handlers from Problem 8).
- Drop `&& Difficulty != DIFF_HARD` from `house.cpp:6141` since the
  `DiffType` value should no longer be the lever — but this becomes a
  no-op once handicap assignment is removed for skirmish.

This composes naturally with Problem 8 (Expert_AI stub fill) — the
strategy handlers are the right place to gate behaviours on difficulty
tier.

---

## Problem 11 — `Computer_Paranoid` (AI gang-up) disabled in skirmish

### Symptom
In 1-vs-many skirmish games, AI opponents fight each other instead of
ganging up on the human. `Rule.IsComputerParanoid = true` does nothing.

### Root cause
`HouseClass::Computer_Paranoid` (`house.cpp:7886`) — the function that
makes all AIs ally vs the human when one is defeated — has its entire body
wrapped in:

```cpp
if (Session.Type != GAME_GLYPHX_MULTIPLAYER) {
    // Re-enable this for multiplayer if we support classic team/ally mode.
```

The comment confirms intent. The function effectively does nothing in
skirmish.

### Fix
Pure DLL change. Drop the gate (or guard behind a new INI knob).

---

## Problem 12 — Spatial threat map dead in skirmish

### Symptom
Teams pick poor regroup routes; any future threat-aware code (e.g. harvester
threat avoidance from Problem 5) has no per-cell threat data to consult.

### Root cause
`MapClass::Cell_Threat` (`map.cpp:1467`) looks up
`HouseClass::Regions[].Threat_Value()` to score cells. But the only
population mechanism, `Adjust_Threat`, is gated:

```cpp
// object.cpp:1858 (and 1871)
if (tark && Session.Type == GAME_NORMAL && In_Which_Layer() == LAYER_GROUND) {
    Map[cell].Adjust_Threat(house, threat);
}
```

In skirmish the region threat table stays empty. `Cell_Threat()` returns
just the visibility flag.

### Fix
Pure DLL change. Drop the `GAME_NORMAL` gate at both lines.

---

## Problem 13 — AI never builds Repair Bay / Sub Pen / Shipyard

### Symptom
AI vehicles can't auto-repair (no Service Depot ever built); AI never
fields naval forces (no Sub Pen or Shipyard ever built — even after fixing
the documented vessel gate).

### Root cause
`AI_Building` (`house.cpp:5775+`) queues power → refinery → barracks →
kennel → gap-gen → war-factory → defenses → tech-center → helipad →
airstrip. Conspicuously missing:

- **`STRUCT_REPAIR`** — the queue block exists but is wrapped in
  `#ifdef OLD` at `house.cpp:6078-6092`. Compiled out. AI vehicles can
  never heal up.
- **`STRUCT_SUB_PEN` / `STRUCT_SHIP_YARD`** — no skirmish-branch queue at
  all. The BaseNode path that would queue these is `GAME_NORMAL`-only.

### Fix
Pure DLL changes.
- Un-`#ifdef OLD` the Repair Bay queue. ~5-line block.
- Add Sub Pen / Shipyard queue blocks modelled on the Helipad/Airstrip
  block. Necessary prerequisite for Problem 2's vessel fix to actually
  matter.

---

## Problem 14 — TeamType `Recruit` gated to campaign

### Symptom
In skirmish, the AI's team scheduler creates suggested team instances but
never fills them with units. Empty teams accumulate, consume cycles, then
self-destroy. No actual squad-based behaviour.

### Root cause
`TeamClass::AI` runs in skirmish and successfully reaches `Suggested_New_Team`,
but the recruitment step is gated:

```cpp
// team.cpp:666
if ((!IsMoving || (!IsFullStrength && Class->IsReinforcable))
    && ((!House->IsHuman || !IsHasBeen) && Session.Type == GAME_NORMAL)) {
    for (int index = 0; index < Class->ClassCount; index++) {
        if (Quantity[index] < Class->Members[index].Quantity) {
            Recruit(index);
        }
    }
}
```

The team-destroy condition at `team.cpp:541` is also `GAME_NORMAL`-gated.

### Fix
Pure DLL change. Drop the gate to enable TeamType behaviour in skirmish.
Downstream effects need care — TeamTypes were authored for campaign and
may not behave sensibly without map-specific definitions.

---

## Problem 15 — Friendly-fire avoidance only protects buildings

### Symptom
AI artillery / V2 / cruiser splashes its own infantry and tanks. Only
suppresses fire near friendly buildings.

### Root cause
`TechnoClass::Area_Modify` (`techno.cpp:1443-1510`) — the function that
reduces target weight when allies are nearby — only checks
`Cell_Building()`, not `Cell_Occupier()`:

```cpp
BuildingClass const* building = Map[newcell].Cell_Building();
if (building != NULL && House->Is_Ally(building)) odds /= 2;
```

No equivalent check for friendly units / infantry in the four scan-box
locations.

### Fix
Pure DLL change. Extend the cell scan to also check `Cell_Occupier()` for
allied techno. ~15 lines.

---

## Problem 16 — AI fixates on first picked Enemy

### Symptom
In 4-player FFAs, AIs lock onto whoever they engaged first and ignore
later threats from other opponents even when the original enemy is much
weaker.

### Root cause
`Expert_AI` (`house.cpp:4965`) only re-picks `Enemy` if `Attack == 0`.
`Attack` is reset every time the AI launches an attack
(`Rule.AttackInterval * Random_Pick(...)` at line 5454), which is
frequent — so `Attack == 0` rarely fires after game start. The clear
condition at line 4955 (Enemy defeated / allied / vanished) handles
total defeat but not "this other guy is now more dangerous."

### Fix
Pure DLL change. Drop the `Attack == 0` gate, or run an Enemy re-evaluation
on a separate periodic timer.

---

## Problem 17 — Minor bugs and dead code

These are small but worth fixing while in the area.

- **Bitwise `|` instead of `&`** in power urgency check (`house.cpp:5255`):
  `if (BScan | (STRUCTF_CHRONOSPHERE))` is always true. Meant `&`. One-char
  fix.
- **`IsScanLimited` is a dead flag** (`foot.cpp:2013, 2044`): read and
  cleared, never set. The "constrain scan to weapon range" path is dead
  code. Either implement the setter or remove the read.
- **Sophisticated unused selection logic**: `Suggest_New_Object`
  (`house.cpp:3562`) and `Suggest_New_Building` (`house.cpp:4612`) are
  well-developed selection functions called only from legacy production
  paths that are mostly inert in skirmish. Worth knowing if we wanted to
  rebuild skirmish AI by re-routing entry points.

---

## Informational findings (not bugs)

- **AI aircraft preferentially target harvesters** (`aircraft.cpp:722, 901`)
  — this is actually a feature; eco harassment is good AI. The
  `THREAT_TIBERIUM` scan in `Mission_Hunt` is one of the few
  `Session.Type != GAME_NORMAL` gates that *helps* skirmish.
- **AI bypasses unarmed-building targeting filter**: `Evaluate_Object`
  (`techno.cpp:1717-1719`) only skips unarmed allied buildings for human
  players, allowing AI to target enemy silos / kennels / gap gens freely.
  Correct behaviour.

---

## Cross-cutting observation

The dominant pattern across **all** documented findings — radar gate,
vessel production, super-weapons, harvester latch, threat map, paranoid,
TeamType, Adjust_Threat — is the same:

> **The AI was designed for campaign (`GAME_NORMAL` with hand-authored
> BaseNodes, TeamTypes, Triggers). Skirmish was bolted on with thin
> dynamic fallbacks.**

Roughly half the `Session.Type` gates in the AI code either correctly
disable campaign-only logic in skirmish *or* incorrectly disable shared
logic. Auditing every `Session.Type` site in `house.cpp`, `team.cpp`,
`object.cpp`, `building.cpp` would catch additional cases. ~80 hits in
`house.cpp` alone — each is either correct, harmless, or a finding.

---

# Consolidated implementation order

All problems ranked by impact-vs-effort. Pick from the top when ready to
work on AI polish post-four-faction-core.

## Tier 1 — Highest impact, lowest effort (do first)

1. **Fix `Greatest_Threat` `bestval` bug** (Problem 7) — ~4-token fix in
   `techno.cpp:2271-2342`. Repairs basic target selection across all units.
2. **Reset `IsTiberiumShort` periodically** (Problem 4) — ~5-line change
   in `HouseClass::AI`. Fixes "AI stopped harvesting forever."
3. **Drop `!House->IsHuman` gate at `unit.cpp:3814`** (Problem 4) —
   one-token change. Player harvesters auto-recover from stuck states.
4. **Hoist Radar Dome queue out of `airthreat` block** (Problem 1) — small
   change in `house.cpp:5970`. Unlocks entire tech tree.
5. **Fix difficulty selector gate** (Problem 10) — drop
   `if (GAME_TO_PLAY == GAME_NORMAL)` at `dllinterface.cpp:2145`. Easy/Hard
   actually do something. **Also** drop `&& Difficulty != DIFF_HARD` at
   `house.cpp:6141`.
6. **Un-`#ifdef OLD` the Repair Bay queue** (Problem 13) — 5-line block in
   `house.cpp:6078-6092`. AI vehicles can finally auto-repair.
7. **Drop `Computer_Paranoid` skirmish gate** (Problem 11) — one-line
   change in `house.cpp:7888`. AIs gang up on the human as `Rule` intends.
8. **Drop `Adjust_Threat` GAME_NORMAL gate** (Problem 12) — at
   `object.cpp:1858, 1871`. Revives spatial threat map for skirmish.
9. **Fix `GOINGTOIDLE` fall-through bug** (Problem 4) — add `return` or
   `else` at `unit.cpp:3065-3074`. Free bug fix.
10. **Fix `BScan | STRUCTF_CHRONOSPHERE` typo** (Problem 17) — one-char
    fix in `house.cpp:5255`.

## Tier 2 — Larger but high-value

11. **Implement Check_Build_Defense + AI_Build_Defense + revive
    AI_Base_Defense** (Problems 8, 9) — ~100-300 lines. Adaptive base
    defense.
12. **Add skirmish branch to `AI_Vessel`** (Problem 2) — model on
    `AI_Unit`. Pair with adding Sub Pen / Shipyard queues to `AI_Building`
    (Problem 13).
13. **Per-AI difficulty plumbing** (Problem 10 follow-up) — port campaign
    CDifficulty/Difficulty inversion logic from `init.cpp:683-750` to
    skirmish.
14. **Threat-aware ore scoring** (Problem 5) — ~40 lines + 2 INI knobs in
    `Tiberium_Check`.
15. **Idle-aware refinery selection** (Problem 6) — ~15 lines in
    `Find_Docking_Bay`.

## Tier 3 — Polish

16. **Implement Check_Build_Income + AI_Build_Income** (Problem 8) —
    adaptive refinery building when ore depletes.
17. **Extend `Area_Modify` to scan allied units** (Problem 15) — ~15
    lines. AI artillery stops splashing its own troops.
18. **Drop `Attack == 0` gate on Enemy re-evaluation** (Problem 16) — FFA
    AIs adapt to current threats.
19. **Add Iron Curtain + Chronosphere AI dispatch + rewrite their
    `Place_Special_Blast` cases** (Problem 3b/c) — only meaningful after
    Tier 1 #4 unlocks tech tree.
20. **Drop parabomb `GAME_NORMAL` gate** (Problem 3d) — one-line change.

## Tier 4 — Major rework (defer until everything above is done)

21. **Reservation table + scatter-the-blocker pathfinding** — ~1-2 weeks.
    Solves dock-stuck deadlock.
22. **JPS path search replacement** — ~1-2 weeks. Cleaner routes, faster.
23. **TeamType Recruit gate removal** (Problem 14) — only meaningful if
    we're going to author skirmish-friendly TeamTypes.
24. **Flow fields for harvester fleets** — ~1 week. Niche but elegant.

---

# Pass 3 — Cheating audit, special-unit AI, tactical micro

Open-ended audit covering three concerns: does the AI cheat, how does it
handle non-standard units, and how does it handle individual unit-level
combat decisions. As with the previous passes, the dominant pattern is
"campaign code path with a thin dynamic skirmish fallback" — most of the
nuance lives in TeamType-driven code that never fires in
`GAME_GLYPHX_MULTIPLAYER`.

**Status:** Research complete. Implementation deferred.

---

## Topic A — AI cheating audit

Definitive answer: **the AI cheats in two material ways, and gets a third
"start-up convenience" that's debatably a cheat**. Stat biases
(firepower / armor / cost / ROF / speed / build-speed) are currently
symmetric in skirmish — every house including the human gets the
`DIFF_NORMAL` handicap with all multipliers at 1.0× (per Problem 10).
Starting credits, starting MCV count, and initial unit setup are all
symmetric (`scenario.cpp:2849-2910`, `scenario.cpp:3318` — both human and
AI get `Session.Options.Credits` and one MCV when Bases are ON).

### A-Cheat 1 — Fog-of-war is invisible to the AI's target picker

**Severity: HIGH. Fix surface: DLL.**

`TechnoClass::Evaluate_Object` (`techno.cpp:1635-1639`):

```cpp
if (!object->IsOwnedByPlayer && !object->IsDiscoveredByPlayer
    && Session.Type == GAME_NORMAL
    && object->What_Am_I() != RTTI_AIRCRAFT) {
    return (false);
}
```

The fog-of-war filter is **only applied in `GAME_NORMAL`**. In skirmish
(`GAME_GLYPHX_MULTIPLAYER`), AI units evaluating targets ignore
`IsDiscoveredByPlayer` entirely — they can see and target any non-cloaked,
non-limbo enemy regardless of fog. A human player walking past the same
fog-covered cell can't see/target what the AI freely targets.

Practical impact is bounded by `Greatest_Threat`'s expanding-ring scan —
the AI doesn't whole-map-scan from each unit's position — but the moment
an AI unit gets within `crange` of a fog-hidden enemy, that enemy is a
legal target. AI scout units effectively have x-ray vision.

**This is downstream of nothing in prior passes — it's a separate
session-type gate bug, same family as Problems 11/12/14.** Fix: drop the
`Session.Type == GAME_NORMAL` clause (or invert it to
`!= GAME_GLYPHX_MULTIPLAYER`). One-line change.

### A-Cheat 2 — AI super-weapon target picker ignores fog entirely

**Severity: HIGH. Fix surface: DLL.**

`HouseClass::Special_Weapon_AI` (`house.cpp:2787-2817`):

```cpp
for (int index = 0; index < Buildings.Count(); index++) {
    BuildingClass* b = Buildings.Ptr(index);
    if (b != NULL && !b->IsInLimbo && b->Strength && !Is_Ally(b)) {
        if (Percent_Chance(90) && (b->Value() > best || best == -1)) {
            best = b->Value();
            bestptr = b;
        }
    }
}
```

The loop iterates **every building on the map** with no `Is_Discovered_By_Player(this)` or `Map[..].Is_Mapped(this)` filter. The AI can nuke the most valuable enemy building it has never seen. A human player must scout the target first.

Currently only fires for `SPC_NUCLEAR_BOMB`, `SPC_SPY_MISSION`, `SPC_PARA_BOMB`, `SPC_PARA_INFANTRY` (the four supers wired into `Super_Weapon_Handler` — see Problem 3b). Once Iron Curtain / Chronosphere dispatch is fixed (Problem 3b/c), this same fog-blind picker would extend to them.

**Downstream of Problem 1** (AI rarely builds the tech to acquire nukes in the first place) — but the moment Problem 1 is fixed, this becomes a frequent, ugly experience. Fix: add a `Is_Discovered_By_Player(this) || Map[Coord_Cell(b->Center_Coord())].Is_Mapped(this)` gate inside the loop.

### A-Cheat 3 — AI MCV deploy can shove its own units out of the way

**Severity: LOW (cosmetic, not gameplay-tilting). Fix surface: DLL.**

`UnitClass::Try_To_Deploy` (`unit.cpp:1550-1552`):

```cpp
if (!House->IsHuman) {
    BuildingTypeClass::As_Reference(STRUCT_CONST).Flush_For_Placement(cell, House);
}
```

When an AI MCV picks a deploy spot blocked by one of its own units, it calls `Flush_For_Placement` to scatter the obstruction. Humans get a "no-deploy" voice cue and must move the unit manually. This isn't really a cheat — it's UI compensation (no human is clicking around in the AI's base) — but it does asymmetrically benefit the AI in cramped maps.

### Where we explicitly checked and found NO cheating

- **Income / Credits.** `Session.Options.Credits` is applied identically to AI and human in `Init_Data` (`scenario.cpp:2849, 2910`, `dllinterface.cpp:1264-1266`). No `IsHuman` branches in any of `house.cpp:2045` (`Harvested`), `2069` (stolen credits), `2119` (`Spend_Money`), `2149` (`Refund_Money`), or refinery dump logic. AI gets credits the same way humans do — by harvesting ore.
- **Build prerequisites.** `HouseClass::Can_Build` does have an AI bypass — `house.cpp:921` — `if (!IsHuman && Session.Type == GAME_NORMAL) return(true)`. But it's **gated on `GAME_NORMAL`**, so in skirmish the AI walks the same prereq + level + ownability checks as the player. No prereq cheat in skirmish.
- **Build speed.** `BuildSpeedBias = 1.0×` for every skirmish house per Problem 10. The `FactoryClass::Start` line at `factory.cpp:432` (`if (House->IsHuman || House->Available_Money() >= Cost_Per_Tick())`) lets the AI start construction without money on hand — but the per-tick spending loop at `factory.cpp:213-218` still pauses if money runs out. Effectively no speed cheat; just a different startup gate that doesn't matter.
- **Power consumption.** `Power_Fraction()`, `Adjust_Power()`, `Adjust_Drain()` (`house.cpp:4488, 7934, 7956`) have no `IsHuman` branches. Symmetric.
- **Starting map awareness.** Per-house bitmask in `CellClass::IsMappedByPlayerMask` (`cell.cpp:3292`). AI houses start with the same shrouded map a human gets. No `Reveal_Map` call in the AI-init path (`dllinterface.cpp:1252-1280`).
- **Starting units / buildings.** `Create_Units` (`scenario.cpp:3024+`) and the `Bases ON` branch (`scenario.cpp:3308-3331`) use the same `utable` / `itable` and the same single `UNIT_MCV` for both AI and human. Identical handicap (`Scen.Difficulty == DIFF_NORMAL` in skirmish per Problem 10, modulo `IsCompEasyBonus` at `scenario.cpp:2916` which is an *easier* AI when humans outnumber AI).
- **Cell-level threat distribution.** `cell.cpp:2090` does have an `IsHuman`-gated branch in `Adjust_Threat` propagation — but it's restricting threat distribution to non-allied enemies (it skips allied humans). Not a cheat.
- **`HouseClass::Suggest_New_Object` / `Suggest_New_Building`** — paths exist (`house.cpp:3562, 4612`) but as noted in Problem 17 are mostly inert in skirmish. No cheat surface.

---

## Topic B — Special-unit AI

### MCV (`UNIT_MCV`)

**Auto-deploy works.** `Mission_Guard` at `unit.cpp:3821-3823` auto-issues `MISSION_UNLOAD` when an AI MCV idles with `House->IsBaseBuilding` true. `IsBaseBuilding` flips to `true` for any skirmish AI with `IQ >= Rule.IQProduction` (`house.cpp:1052-1056`). MCV picks a deploy location via `Try_To_Deploy` (`unit.cpp:1532+`); if blocked, falls back to `Flush_For_Placement` (A-Cheat 3 above).

**No redeploy after CY loss.** AI rebuilds buildings via `AI_Building`'s structure queue (Problem 1 family) — never via a second MCV. The unit picker in `AI_Unit` (`house.cpp:6231-6259`) gives every armed unit weight 20 and every unarmed unit (including `UNIT_MCV`) weight 1, so an AI *might* roll an MCV via random pick, but it's heavily down-weighted vs combat vehicles. **Severity: MEDIUM** — an AI that loses its Construction Yard is permanently crippled. Fix surface: DLL. Smart fix is detecting CY loss and biasing MCV production upward when no `STRUCT_CONST` is present.

### Engineer (`INFANTRY_RENOVATOR`)

**Used offensively, with a hack.** `InfantryClass::Greatest_Threat` (`infantry.cpp:2464-2469`) overrides target picking for AI engineers: if `House->ToCapture != TARGET_NONE && Distance < 0x0F00`, head straight there. Otherwise OR `THREAT_CAPTURE` into the threat mask. So AI engineers do try to capture nearby enemy buildings.

**Production is throttled.** `AI_Infantry` (`house.cpp:6540-6544`) only assigns the engineer slot a non-zero weight when `CurInfantry > 5`, and the weight is `1 - max(IQuantity[index], 0)` — i.e. one at a time, no spam. Reasonable.

**Damaged engineer auto-flees forward.** `infantry.cpp:435-438` — an AI engineer with `Mission == MISSION_GUARD/GUARD_AREA` taking damage gets reassigned to `MISSION_HUNT`. Not a flee — it charges. Cute design choice.

**No defensive recapture.** Nothing in the AI scans for captured-by-enemy buildings to win them back. `ToCapture` is set by the engineer when it picks its own target; no team-level orchestration.

### Spy (`INFANTRY_SPY`)

**Never produced by the skirmish AI.** `AI_Infantry`'s skirmish branch (`house.cpp:6523-6553`) explicitly lists E1/E2/E3/E4/RENOVATOR/TANYA — `INFANTRY_SPY` falls into the `default: Value = 0;` case. AI builds zero spies.

**Spy ability would work if produced.** Infiltration logic at `infantry.cpp:687-744` is fully wired — spy gives radar, sub pen → sonar, airstrip → parabomb. But none of it fires for AI because no AI spies exist.

**Severity: LOW-MEDIUM.** Fix surface: DLL. Add `INFANTRY_SPY` (and `INFANTRY_DOG` indirectly — same gap) to the picker with appropriate values. Spy might want a value of 1-2 once enemy has tech, gated on `IQ >= Rule.IQSuperWeapons` to scope to harder AIs.

### Thief (`INFANTRY_THIEF`)

**Never produced by the skirmish AI.** Same gap as spy — defaults to value 0 in `AI_Infantry`. Thief ability itself is fully wired at `infantry.cpp:750-779` (steals half the enemy's available money), gated only on whether the building has `Capacity > 0`.

**Greatest_Threat already handles thief targeting.** `infantry.cpp:2518-2521` — thieves get `THREAT_CAPTURE | THREAT_TIBERIUM` mask, so if produced they'd home in on refineries / silos.

**Severity: LOW.** RA's Allied thief is a relatively rare unit and human players don't lean on it heavily; restoring AI thief usage is nice-to-have. Fix surface: DLL.

### Tanya (`INFANTRY_TANYA`)

**Produced by skirmish AI.** Weight 1 in `AI_Infantry` (`house.cpp:6546-6548`), one at a time.

**Auto-fires when AI-owned.** `Greatest_Threat` at `infantry.cpp:2481-2483` has a special hack — Tanya doesn't auto-fire when **human**-owned, but AI Tanya targets normally via `FootClass::Greatest_Threat`. So an AI Tanya behaves like an elite commando under MISSION_HUNT — wanders into combat range, single-shots infantry.

**No special anti-building handling.** Tanya's C4 → building demolition isn't hooked into AI target-picking. AI Tanya shoots infantry but doesn't suicide-plant C4 on buildings the way a skilled human does.

**Severity: LOW-MEDIUM.** Fix surface: DLL. Adding building-target preference to AI Tanya would meaningfully upgrade Allied AI offence.

### Chrono tank (`UNIT_CHRONOTANK`)

**Produced incidentally** — `AI_Unit` (`house.cpp:6238-6243`) assigns weight 20 to any unit with a primary weapon, including the chrono tank. AI builds them.

**Chrono ability never fires for AI.** `Mission_Unload` for `UNIT_CHRONOTANK` (`unit.cpp:2856-2872`) handles the player teleport flow — opens `IsTargettingMode = SPC_CHRONO2`, sets `House->UnitToTeleport`, then waits for the player to click a destination. There's **no AI dispatch** that picks a target cell and triggers the deploy. AI chrono tanks behave exactly like regular medium tanks — drive, shoot, die.

**Severity: LOW.** Fix surface: DLL. Composes with Problem 3b/c (Iron Curtain / Chronosphere AI dispatch) — same pattern (AI-picks-cell vs mouse-read).

### Demo truck (`UNIT_DEMOTRUCK`)

**Produced incidentally** — armed (suicide blast as primary weapon), so weight 20 in `AI_Unit`.

**Functional as a unit but used poorly.** `Fire_At` at `unit.cpp:4402-4404` `delete this` on first weapon use — i.e. the truck explodes on attack. Under `MISSION_HUNT` it pathfinds toward `TarCom` and detonates on contact. No targeting bias toward high-value buildings or clustered enemies — the demo truck picks the same `Greatest_Threat` target any tank would, then explodes there. So a single Tesla / pillbox can pick it off long before it reaches anything valuable.

**Severity: MEDIUM.** Fix surface: DLL. Add `UNIT_DEMOTRUCK` target bias in `Greatest_Threat` toward construction yards / refineries / war factories — the natural human use case.

### Attack dog (`INFANTRY_DOG`)

**Never produced by the skirmish AI.** Same gap as spy/thief — `default: Value = 0` in the `AI_Infantry` picker. `IScan & INFANTRYF_DOG` gating at `house.cpp:6469` is in the campaign branch only.

**Functional if produced.** `IsDog` and `IsOrganic` flags drive correct anti-infantry-only targeting via the `IsOrganic` filter at `infantry.cpp:2496-2498`.

**Severity: LOW-MEDIUM.** Fix surface: DLL. Same one-liner fix as spy/thief — add `INFANTRY_DOG` case with weight 1-2 (gated on Kennel existence).

### MAD tank (`UNIT_MAD`)

**Produced incidentally** — armed/has-weapon under `Mission_Unload` semantics, weight 20.

**Deploy never fires for AI.** `Mission_Unload` for `UNIT_MAD` (`unit.cpp:2792-2855`) implements the quake mechanic, but it only runs once the unit is assigned `MISSION_UNLOAD`. Nothing in AI ever issues `MISSION_UNLOAD` to a MAD tank. AI MAD tanks roll out with the attack wave, shoot enemies with their primary weapon (if any — depends on rules.ini definition), die.

**Severity: LOW.** RA's MAD tank is a niche Counterstrike unit. Fix surface: DLL. Same pattern as chrono tank — needs AI dispatch logic to trigger deploy when surrounded by enemy units.

### Minelayer (`UNIT_MINELAYER`)

**Unarmed → weight 1 in `AI_Unit`** — built occasionally.

**Deploy never fires for AI.** `Mission_Unload` for `UNIT_MINELAYER` (`unit.cpp:2715-2790`) lays a mine and re-guards. But again, no AI path issues `MISSION_UNLOAD`. AI mine layers wander as unarmed "scouts" until killed.

**Severity: LOW.** Fix surface: DLL.

### Cross-cutting pattern

Every deploy-mechanic unit (chrono tank, MAD tank, mine layer, demo truck for use-aware targeting) has the same gap: `Mission_Unload` implements the deploy correctly, but **no AI dispatch issues `MISSION_UNLOAD`** in the absence of TeamType orchestration. This is the same shape as Problem 3b/c (super-weapon dispatch gaps). A unified "AI special-action dispatcher" in `Expert_AI` or `AI_Unit` could feed all of these.

---

## Topic C — Tactical micro

### Retreat / fleeing

**No damage-based retreat for non-fraidy units.** `FootClass::Mission_Retreat` (`foot.cpp:2605`) is "walk to map edge" for team-leaving — not a panic flee. Combat units below `ConditionRed` / `ConditionYellow` keep fighting until destroyed.

**`IsFraidyCat` units (civilians, dog targets) do flee.** `infantry.cpp:1905-1965` — Fear escalates and triggers `Scatter`. But this is for civvies, not combat infantry.

**Harvesters do flee under damage** with ore on board (`unit.cpp:1179-1193`). That's a unit-class-specific path, not a general AI behaviour.

**Severity: MEDIUM.** Fix surface: DLL. A general "AI units below `ConditionRed` retreat toward base or repair bay" mission would be a meaningful upgrade. Composes naturally with the Repair Bay queue fix from Problem 13 (an AI vehicle that flees needs somewhere to flee *to*).

### Kiting

**No kiting code anywhere.** AI long-range units (V2, artillery, cruiser) approach to `In_Range` and stop — they don't try to maintain a stand-off distance vs shorter-range enemies. `Approach_Target` (`foot.cpp` core mission_hunt → drive) just closes the gap.

**Severity: LOW.** Kiting is hard to implement well and the vanilla unit roster's range delta is small enough that it's not a glaring omission. Fix surface: DLL.

### Focus fire

**No coordination.** `HouseClass::AI_Attack` (`house.cpp:5402-5455`) assigns `MISSION_HUNT` to every armed unit en masse. Each unit then independently calls `Target_Something_Nearby(THREAT_NORMAL)` → `Greatest_Threat` → picks the closest legal target. Two AI tanks side-by-side often pick different targets simply because their position differs by a cell.

**Greatest_Threat `bestval` bug** (Problem 7) compounds this — the AI's target picks are already arbitrary; adding coordination on top of broken picks would be premature.

**Severity: MEDIUM (after Problem 7 fix).** Fix surface: DLL. The natural place is a post-`AI_Attack` consolidation pass: scan all units assigned to `MISSION_HUNT`, group by zone, share the highest-value target within each group.

### Formation movement

**No formation support.** Units move independently along the path returned by `Findpath`. The cooperative-pathing gaps from the pathfinding section above are the same shortfall.

**Severity: LOW for AI specifically** (it's actually a player UX gripe more than an AI gripe). Fix surface: DLL.

### Counter-attack response

**`Base_Is_Attacked` works.** `techno.cpp:5276-5444` pulls infantry and units from the field back to defend an attacked building, with `Suspend_Teams` so TeamType activity pauses during the response. Gated on `!House->IsHuman` (line 5295) — correct. Reasonably sophisticated weighting by `Risk()`, threat capability, and zone-of-attacked-building.

**Triggered correctly in skirmish.** Called from `building.cpp:1288` and `unit.cpp:1201` (harvester being attacked). Both paths fire in skirmish.

**Caveat from Problem 14** — `Suspend_Teams` is somewhat moot because TeamType `Recruit` is gated to campaign, so the AI rarely has teams to suspend. But the unit-rerouting half still works.

### Repair behaviour

**Already documented in Problem 13.** AI never builds `STRUCT_REPAIR` (queue `#ifdef OLD`), so AI vehicles can't auto-repair regardless of micro. The harvester `GOINGTOIDLE → MISSION_REPAIR` path (`unit.cpp:3067-3068`) is dead in practice because `STRUCTF_REPAIR & ActiveBScan` is never true.

**Even if Repair Bay queue is fixed:** there's no general "vehicle below `ConditionRed` heads to Service Depot" logic. The `Find_Docking_Bay(STRUCT_REPAIR)` lookups all live in player-action code paths (`unit.cpp:4776`, `foot.cpp:1667`).

**Severity: MEDIUM.** Pairs with Problem 13. Fix surface: DLL. Once an AI can build a Repair Bay, add an AI-side `MISSION_REPAIR` self-assignment when a vehicle drops below `ConditionRed` and a `STRUCT_REPAIR` exists and isn't busy.

### Reinforcement / regrouping

**No regrouping logic.** `AI_Attack` shuffles guards 20% of the time (`house.cpp:5430-5432`) but otherwise the rule is "everyone goes hunt." There's no "wait for N tanks before attacking" or "fall back if outnumbered" path.

The `Attack` timer (`house.cpp:5454`, `Rule.AttackInterval * Random_Pick`) controls the *interval* between waves, not the *composition* — so an AI with one tank and an AI with twelve tanks both attack on the same cadence. Piecemeal pressure rather than waves.

**Severity: MEDIUM.** Fix surface: DLL. Adding a `min_force_size` check before triggering `AI_Attack` would produce more wave-like behaviour.

### Bunkering / garrison

**Garrison feature does not exist in RA Remastered.** Civilian-building garrison (the TS / Generals-style "infantry climb into a building and shoot from windows") was never implemented in RA. Confirmed via grep — `Garrison` token absent from the entire codebase.

The closest analogue is `MISSION_AMBUSH` (`mission.cpp:344`, `foot.cpp:1191`) — infantry hold position with elevated awareness. The AI sets it via `Try_To_Deploy` / scenario triggers but doesn't dynamically assign it in skirmish.

**Severity: N/A** — this is a design feature gap (no garrison feature exists to use), not an AI gap. Out of scope.

---

## Top fixes from this pass — ranked tiers

Slotted into the existing tier ranking from prior passes. Effort estimates
are conservative.

### Tier 1 — Highest impact, lowest effort

Inserting into the existing Tier 1:

11. **Drop `GAME_NORMAL` gate on fog-of-war filter in `Evaluate_Object`**
    (A-Cheat 1) — one-line change at `techno.cpp:1635`. Eliminates AI
    x-ray-vision target selection. Probably the most impactful single-line
    fix in this entire document after Problem 7's `bestval` bug.
12. **Add fog-of-war filter to `Special_Weapon_AI`** (A-Cheat 2) — ~3-line
    addition inside the `Buildings` loop at `house.cpp:2798-2811`. Stops
    AI nuking buildings it has never scouted. Composes with Problem 1
    (without which the AI rarely has nukes anyway).
13. **Add `INFANTRY_SPY` / `INFANTRY_THIEF` / `INFANTRY_DOG` to
    `AI_Infantry` picker** (Topic B — Spy, Thief, Dog) — ~12 lines
    inserting three `case` entries at `house.cpp:6549`. Tiny effort,
    restores three full unit categories to AI rotation.

### Tier 2 — Larger but high-value

14. **Add CY-loss MCV-bias to `AI_Unit`** (Topic B — MCV) — ~10 lines.
    Detect `BQuantity[STRUCT_CONST] == 0` and bias `UNIT_MCV` weight high.
    Stops "kill CY → AI is permanently crippled" outcomes.
15. **Demo truck target bias in `Greatest_Threat`** (Topic B — Demo
    truck) — ~15 lines. AI demo trucks aim at high-value structures, not
    nearest tank.
16. **Damage-based retreat / repair-bay flee** (Topic C — Retreat +
    Repair) — composes with Problem 13. ~30-50 lines. Vehicles below
    `ConditionRed` head to a `STRUCT_REPAIR` if one exists. Major
    behavioural upgrade.
17. **AI chrono tank dispatch** (Topic B — Chrono tank) — composes with
    Problem 3b/c. Pick an AI-friendly destination cell, trigger the
    teleport. ~30-50 lines.
18. **`min_force_size` gate on `AI_Attack`** (Topic C — Regrouping) — ~10
    lines. Don't trigger waves until N tanks ready. Wave-like pressure
    instead of trickle.

### Tier 3 — Polish

19. **AI MAD tank deploy dispatch** (Topic B — MAD tank) — niche unit.
    ~20 lines. Detect surround-by-enemy and trigger `MISSION_UNLOAD`.
20. **AI Tanya anti-building bias** (Topic B — Tanya) — ~15 lines in
    `InfantryClass::Greatest_Threat`. AI Tanya prefers building targets
    when nothing infantry-shaped is in range.
21. **Focus-fire consolidation pass after `AI_Attack`** (Topic C — Focus
    fire) — meaningful only after Problem 7 is fixed. ~40 lines. Group
    by zone and share highest-value target.
22. **AI minelayer deploy dispatch** (Topic B — Minelayer) — niche unit.
    ~20 lines. Lay mines on approaches to base.

### Tier 4 — Deferred or out of scope

- **Kiting** — not implemented anywhere, large lift, low return given
  RA's small range deltas.
- **Formation movement** — falls out of the cooperative pathfinder rework
  (Tier 4 #21 in the prior pass), not a separate item.
- **Garrison** — design feature gap, not an AI gap. Out of scope.

### Cross-cutting note

A-Cheat 1 + A-Cheat 2 + the `Mission_Unload` dispatch gaps (chrono tank,
MAD tank, minelayer) are all the **same shape** as the existing `Session.Type
== GAME_NORMAL` / TeamType-orchestration gates documented in prior passes.
The AI was authored for `GAME_NORMAL` with hand-built triggers; skirmish
fallback is a thin layer with gaps wherever the original code paths
assumed "the campaign designer set this up." A `grep -n "Session.Type ==
GAME_NORMAL" *.cpp` over the redalert/ tree (already done — ~80 hits in
`house.cpp` alone) remains a high-yield future audit.

---

# Next research steps

Outstanding research not yet performed. Each item is a self-contained
investigation suitable for a future session. Prompts are intentionally
written so a fresh Claude instance can pick them up cold — point it at this
doc, give it the topic, and it should have enough context.

## Topic 1 — Building placement algorithm  *(high priority)*

**Question:** When the AI decides to build, say, a power plant, *where
exactly* does it place it? Vanilla RA is notorious for placing buildings in
dumb spots — power plants exposed at the base edge, refineries far from
ore, defenses in random corners.

**Investigate:**
- Find the placement function. Candidates: `Find_Build_Location`,
  `Where_To_Build`, `Suggest_Building_Location`, `Coord_Of_Best_Place`.
  Likely in `house.cpp`, `base.cpp`, or `building.cpp`.
- What's the algorithm? Spiral from base center? Closest existing building?
  Random valid cell? Cost function?
- Does it consider distance-to-ore (refineries), edge-of-base (defenses),
  power coverage (tesla coils), adjacency rule, direction of known threats?
- Is there per-building-type special-casing?
- Same code path for AI vs player, or AI-specific?
- Campaign BaseNode-driven vs skirmish dynamic?

**Expected output:** Section in this doc as "Problem 18 — Building
placement" with file:line citations, severity rating, fix surface, and
proposed improvements.

## Topic 2 — Trigger / TeamType system in skirmish  *(medium priority)*

**Question:** RA's trigger system is a powerful scripting layer (events
fire actions on conditions). What works in skirmish, what doesn't, and
could we use it as a tool for adding behaviours without C++ changes?

**Investigate:**
- Files: `trigger.cpp`, `trigtype.cpp`, `triggertypeclass.h`. Search
  `TriggerClass`, `TriggerTypeClass`.
- Which trigger paths are `GAME_NORMAL`-gated? Do any fire in skirmish?
- TeamType beyond the documented recruit-gate (Problem 14) — other places
  team behaviour is campaign-only?
- Do AI players ever generate their own TeamTypes in skirmish, or only
  consume hand-authored ones?
- Could triggers be a useful abstraction for behaviour tweaks (e.g. "at
  game time T do X"), or would we need new C++ hooks?
- Any dead/broken trigger handlers — actions/events in the enum but not
  implemented?

**Expected output:** Section as "Problem 19 — Trigger system in skirmish."
Include a verdict on whether triggers are a useful tool for the mod, or
just historical baggage to be aware of.

## Topic 3 — Full `Session.Type == GAME_NORMAL` audit  *(systematic sweep)*

**Question:** The dominant pattern across every finding so far is the
same: code paths designed for campaign that are silently bypassed in
skirmish. ~80 hits in `house.cpp` alone, more in `team.cpp`, `object.cpp`,
`building.cpp`, `cell.cpp`, `techno.cpp`. Some are correct (campaign-only
features), many are bugs.

**Investigate:**
- `grep -rn "Session\.Type" redalert/*.cpp` — categorise every hit:
  - **Correct:** disables genuinely campaign-only logic (e.g. BaseNode
    lookups, hand-authored Triggers)
  - **Bug:** disables shared logic that should run in skirmish
  - **Cosmetic:** UI/audio/scoreboard differences, low impact
- Cross-reference against findings already documented (don't duplicate
  Problems 1, 2, 3d, 4-6, 10-14, A1, A2).
- Surface the remaining bugs as new Problems.

**Expected output:** New "Problem 20 — Remaining Session.Type bugs"
section listing each new finding with severity/fix-surface. May produce
several sub-problems.

## Topic 4 — IQ system audit  *(targeted)*

**Question:** `Rule.IQ*` thresholds gate AI behaviours throughout the
code. The defaults are in `rules.cpp:138+`. With the difficulty selector
broken (Problem 10), all AIs run at the same fixed IQ. What does each IQ
gate actually unlock?

**Investigate:**
- Enumerate every `IQ >=` / `IQ <` check in the codebase.
- For each, what behaviour does it gate? Is the threshold reasonable?
- Does IQ actually ramp during a game, or is it set once?
- Could the IQ system be the primary lever for behavioural difficulty
  (per [[feedback-difficulty-philosophy]])?

**Expected output:** Section as "IQ system map" — a table of each IQ
threshold, what it gates, the default value, and proposed difficulty-tier
values (Easy / Normal / Hard).

## Topic 5 — Aircraft AI deep dive  *(targeted, lower priority)*

**Question:** Prior passes touched `AI_Aircraft` (`house.cpp:6598`) but
didn't go deep. How do AI MiGs / Yaks / Badgers / longbows / hinds /
choppers behave?

**Investigate:**
- Target selection (already noted — they prefer harvesters in skirmish via
  `THREAT_TIBERIUM` scan).
- Return-to-airstrip behaviour.
- Helicopter hover-fire-retreat patterns.
- Paradrop dispatching.
- Aircraft as part of `AI_Attack` waves vs independent.

**Expected output:** Section as "Aircraft AI behaviour."

## Suggested ordering

If picking up cold and limited on session time:

1. **Topic 1 (Building placement)** — most user-visible, big effect on AI
   feel. ~15-20 min.
2. **Topic 2 (Triggers)** — clarifies whether we have a scripting tool
   available. ~10-15 min.
3. **Topic 3 (`Session.Type` audit)** — high-yield systematic pass. Run
   only after Topics 1-2 to avoid duplication. ~20-25 min.
4. **Topic 4 (IQ system)** — composes with the difficulty rework (Problem
   10 + Problem 8). ~10-15 min.
5. **Topic 5 (Aircraft)** — niche polish. ~10 min.

All five together: ~75-90 minutes of agent time. Do not run in parallel —
Topics 1-3 share file targets and would duplicate exploration.

## Cross-cutting items still pending

- **Validation of every finding under build + smoke test.** All findings
  in this doc are static-analysis only. Several rely on the same file
  references (`house.cpp:5970`, `unit.cpp:2977`, `techno.cpp:2271`, etc.)
  being current. Worth a sanity-check grep before implementation.
- **`#ifdef` audit.** We've found two compiled-out blocks
  (`#ifdef NEVER` around `AI_Base_Defense`, `#ifdef OLD` around the
  Repair Bay queue). Could be more. A `grep -n "#ifdef NEVER\|#ifdef OLD"
  redalert/*.cpp` would surface them.
- **Implementation order assumes one engineer.** If we ever parallelise
  AI work, the tier list needs dependency annotations (e.g. Problem 17
  focus-fire requires Problem 7 first).
