# AI problem inventory

**Status:** Reference. The stock skirmish AI's problems as found in EA's source, and what TF does about each.
The plan built on it is `ai-upgrade-plan.md`; every TF fix below can be switched back to vanilla
(`player-settings.md`).
**Fixed:** 1 (radar dome), 2 (naval), 3d (parabombs), 4's latch, idle order and FINDHOME queue, 5 (threat-aware ore), 6 (sticky
refinery), 7 (`Greatest_Threat`), 10 (difficulty), 13 (repair bay and naval yards), 17's power test, A-Cheat 1 and 2.
**Open:** 3a-3c (the Missile Silo, Iron Curtain and Chronosphere), 4's human re-queue and unload-pad clear-out, 8
(`Expert_AI` stubs), 9 (`AI_Base_Defense`), 11 (`Computer_Paranoid`), 12 (threat map), 14 (TeamType recruit), 15
(friendly fire), 16 (enemy pick), A-Cheat 3, the special units (Topic B) and the tactical micro (Topic C). The open
ones were found by reading the code, not tested in play.

Function names point into TF's `redalert/`; a line number is given only where it was checked against the current
tree. Every finding here is a DLL change: no INI path reaches any of them.

Every TD building is a first-class engine type with its own `Points=` (`td-building-separation-recipe.md`
gotcha 11), so the AI targets them.

**Reference source: AI Boost 3.2** (Bast75 and xXMini FrankiXx, GPL v3 with EA's terms, built on CFE 1.8) in
`reference/ai-boost2/`. It has working skirmish naval AI, Iron Curtain and Chronosphere use with AI-aware targeting,
special-unit AI, counter-building, MCV expansion, primary-factory production, power sell-off and scatter-on-launch.
Its difficulty levers (an economy multiplier and a production-speed hack) are cheats: study its mechanisms, never
port the boosts (difficulty is behavioural). Both authors are credited in the Workshop and ModDB text.

## Root cause (shared)

Skirmish skips every campaign path and leaves a thin fallback with gaps (the field manual's
[The skirmish AI and its IQ levels](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/skirmish-ai-and-iq.md#why-the-skirmish-ai-is-thin),
Why the skirmish AI is thin). Skirmish is typed `GAME_GLYPHX_MULTIPLAYER` in `dllinterface.cpp` (`GAME_TO_PLAY`,
lines 1688 and 1824; the enum in `session.h`). Roughly half the `Session.Type` gates in the AI code (55 lines in EA's
`HOUSE.CPP`, 69 in TF's `house.cpp`) rightly disable campaign-only logic and the rest wrongly disable shared logic; a sweep of every gate found no high-severity case
beyond those listed here (`ai-upgrade-plan.md` §4).

---

## Bases and production

### Problem 1: the AI never builds a Radar Dome, so never reaches tech (fixed)
The stock AI queues the dome only against an air threat (the field manual's
[The skirmish AI and its IQ levels](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/skirmish-ai-and-iq.md#stock-bugs-and-gaps),
Stock bugs and gaps: the radar dome row, with what the dome gates). The block sits in `HouseClass::AI_Building`'s
air-defence branch and queues only while `BQuantity[STRUCT_RADAR] == 0`; the campaign path builds from BaseNodes
(`base.cpp`, `Next_Buildable()`, consulted only in `GAME_NORMAL`). TF's early radar in `AI_Building` queues the dome
once the economy gate passes (`tf_economy_ready`: two standing refineries, or a Tiberium-short house, and a war
factory) and power is full (`Power_Fraction() >= 1`); there is no barracks test. GDI, Nod and TS GDI always queue it
this way; for Allies and Soviets it is the early-radar switch, and off they leave it to the stock air-defence branch.

### Problem 2: the AI never builds naval units (fixed in 5.0.0)
`AI_Vessel` wraps its whole body in `if (Session.Type == GAME_NORMAL)` (the field manual's
[stock bugs row](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/skirmish-ai-and-iq.md#stock-bugs-and-gaps)),
so `BuildVessel` stays `VESSEL_NONE`, and a clear after the block resets it whenever `IsBaseBuilding` is set anyway.
Unlike `AI_Unit`, `AI_Infantry`, `AI_Aircraft` and `AI_Building`, it has no dynamic branch at all: vessel production
is TeamType-driven, and skirmish has no TeamTypes with vessels. TF's skirmish branch is `ai-upgrade-plan.md` W5.1.

### Problem 3: superweapons
- **3a, open:** the AI never queues the Missile Silo, Iron Curtain or Chronosphere; only the GPS follows from
  Problem 1 (the field manual's
  [stock bugs](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/skirmish-ai-and-iq.md#stock-bugs-and-gaps),
  the building-list and three-powers rows). TF's `AI_Building` still has no `STRUCT_MSLO`, `STRUCT_IRON_CURTAIN` or
  `STRUCT_CHRONOSPHERE` entry; the silo's slot is planned in `ai-upgrade-plan.md` W5.3. Fix shape: add the three to
  `AI_Building`'s list.
- **3b, open:** in stock RA only the nuke, spy plane, parabombs and paratroopers have an AI fire call (the
  three-powers row). TF's `Super_Weapon_Handler` adds them for its own powers (TD Ion Cannon and nuke, TS Ion Cannon,
  EMP, drop pods, TD spy plane and paratroopers); the Iron Curtain, Chronosphere and Sonar Pulse blocks still have
  none. Fix shape: `Special_Weapon_AI(SPC_IRON_CURTAIN)` and `Special_Weapon_AI(SPC_CHRONOSPHERE)` in their blocks,
  as the nuke's is, once 3c gives them a target.
- **3c, open:** both need an AI-aware object pick and a target choice of their own (the superweapon-aim row). The
  cell comes from the caller; only the pick within it follows the mouse, through
  `Map[cell].Cell_Techno(Keyboard->MouseQX - Map.TacPixelX, Keyboard->MouseQY - Map.TacPixelY)`, so an AI fire picks
  by the human's last cursor position. The cases are `Place_Special_Blast`'s Iron Curtain and Chronosphere
  (`house.cpp:4266`); `Special_Weapon_AI`'s building picker (`house.cpp:4106`) is the template. Fix shape: accept an
  AI-supplied cell and never read `Keyboard` when `!IsHuman`; arguably drop the Chronosphere's
  `Session.Type != GAME_NORMAL` check too.
- **3d, fixed:** stock enables parabombs only in `GAME_NORMAL` (the three-powers row). TF grants them to any house
  with an active real airfield (`STRUCT_AIRSTRIP`, tested directly because the TD airfields shadow
  `STRUCTF_AIRSTRIP` in the scan) in every session type, and the AI fires them.
- **3e, informational:** the GPS, Chronosphere, Iron Curtain and nuke acquisition checks include
  `(IsHuman || IQ >= Rule.IQSuperWeapons)`; the spy plane, paratroopers, parabombs and sonar pulse have no IQ gate.
  `IQSuperWeapons` defaults to 4 (`rules.cpp`). TF sets IQ per AI from the lobby difficulty
  (`TF_AI_IQ_From_Difficulty`, `ai-upgrade-plan.md` W7).

### Problem 8: the `Expert_AI` strategy layer is mostly stubs (open)
Of `Expert_AI`'s ten strategies, four checks and five actions are stubs, so it fire-sells, raises money and power,
and attacks, and nothing adaptive happens (the field manual's
[How it chooses what to build](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/skirmish-ai-and-iq.md#how-it-chooses-what-to-build),
and the stubs row under Stock bugs and gaps). In TF: `Expert_AI` (`house.cpp:6766`); `Check_Build_Defense`,
`Check_Build_Offense`, `Check_Build_Income` and `Check_Build_Engineer` (`house.cpp:7294`-`7364`); `AI_Build_Power`,
`AI_Build_Defense`, `AI_Build_Offense`, `AI_Build_Income` and `AI_Build_Engineer` (`house.cpp:8188`-`8243`), all
still stubs; `AI_Attack` (`house.cpp:7884`). `Check_Build_Power` is rewritten (Problem 17). The most leverage is in
`Check_Build_Defense` and `AI_Build_Defense` with Problem 9.

### Problem 9: `AI_Base_Defense` is compiled out (open)
The AI builds pillboxes, turrets, Tesla coils, SAM sites and AA guns by static `Rule.DefenseRatio` ratios inside
`AI_Building`, with no sense of where attacks come from. `HouseClass::AI_Base_Defense` is wrapped in `#ifdef NEVER`
(EA `HOUSE.CPP`; TF `house.cpp:8420`), never compiled and never called: only doc comments name it. Its body is
incomplete (it computes `nothreat` and never acts on it). Fix shape: remove the wrapper, finish the body, and call it
from `AI()`'s scheduler with real `Check_Build_Defense` and `AI_Build_Defense` (Problem 8). The placement side is
`ai-upgrade-plan.md` W3.

### Problem 13: the repair bay and naval yards (fixed)
Stock `AI_Building` queues power, refinery, barracks, kennel, gap generator, war factory, defences, tech centre,
helipad and airstrip, in that order (the field manual's
[building-list row](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/skirmish-ai-and-iq.md#stock-bugs-and-gaps)):
the `STRUCT_REPAIR` queue is in `#ifdef OLD`, and no skirmish branch queues `STRUCT_SUB_PEN` or `STRUCT_SHIP_YARD`
(only the `GAME_NORMAL` BaseNode path would). So the harvester's `GOINGTOIDLE` to `MISSION_REPAIR` path is dead in
practice: `STRUCTF_REPAIR & ActiveBScan` is never true. TF's `AI_Building` queues a repair bay per faction role
(`TF_Skirmish_Pick(STRUCT_REPAIR, ...)`) and naval yards for its naval AI (`ai-upgrade-plan.md` W5.1).

### Problem 10: the difficulty selector does nothing in skirmish (fixed)
Every skirmish house plays at the Normal handicap and `MaxIQ` whatever the lobby says (the field manual's
[Difficulty](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/skirmish-ai-and-iq.md#difficulty)
and [IQ levels](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/skirmish-ai-and-iq.md#iq-levels)).
In TF: `CNC_Set_Difficulty`'s `GAME_NORMAL` gate (`dllinterface.cpp:3446`, calling `Set_Scenario_Difficulty` in
`scenario.cpp`), every house's `Assign_Handicap(Scen.Difficulty)` in `GlyphX_Assign_Houses`
(`dllinterface.cpp:1496`), so every `DifficultyClass` bias is 1.0x.

**A second trap behind it:** `AI_Unit`'s harvester replacement requires `Difficulty != DIFF_HARD`, so a Hard-handicap
AI never replaces harvesters (the field manual's
[Harvesters](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/harvesters.md#stock-problems)
table, with why it only bites in the campaign).

TF's difficulty is behavioural: each AI's IQ comes from the lobby (`TF_AI_IQ_From_Difficulty`, set at
`dllinterface.cpp:1464` and `3388`), stat handicaps stay at Normal for every house (so the `DIFF_HARD` test above
always passes), and the slider is never routed through `Assign_Handicap`. The campaign's `CDifficulty`/`Difficulty` inversion in `init.cpp` is the stat-bias path,
and is not ported. The tiers and the `Production` IQ trap are `ai-upgrade-plan.md` W7.

### Problem 17: minor bugs and dead code
- **The power check's `|`** is always true (the field manual's
  [power-check row](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/skirmish-ai-and-iq.md#stock-bugs-and-gaps)).
  TF replaces the whole check with a scan for an armed, powered building (`ai-upgrade-plan.md` W1.1).
- **`IsScanLimited` is live:** `DriveClass::Start_Of_Move` sets it when a unit has no path to a `TarCom` out of
  range, and `TeamClass::Scan_Limit` sets it for the whole team. `Greatest_Threat` then scans weapon range only, and
  clears the flag when that finds nothing.
- **Selection logic:** `Suggest_New_Object` is the live factory query: every AI factory calls it
  (`BuildingClass::Factory_AI`, `building.cpp:8703`) and it returns the house's
  `BuildUnit`/`BuildInfantry` pick. `Suggest_New_Building` has no caller at all, in EA or TF.

---

## Harvesters

Symptoms seen: harvesters stuck near refineries, wandering to ore near enemy bases, and queueing at one refinery while
another sits idle. The stock causes are on the field manual's
[Harvesters](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/harvesters.md#stock-problems)
page, with the `rules.ini` knobs (none of which touches them). The shipped recovery is
`harvester-recovery-design.md`.

### Problem 4: harvesters get permanently stuck
- **The latch (fixed):** `IsTiberiumShort` is set in `Mission_Harvest`'s LOOKING state when the ring scan finds
  nothing, and EA never resets it. Once set, AI harvesters never re-queue from `Mission_Guard`, harvester replacement
  stops (`AI_Unit`) and refinery building stops (`AI_Building`). TF clears it whenever a harvester finds ore
  (`Mission_Harvest`).
- **The idle order (fixed):** EA's `GOINGTOIDLE` case assigns repair or hunt, then always `MISSION_GUARD`. TF deletes
  the dead branch (hunt would be a weaponless suicide order, and TF's reworked `Mission_Repair` docks refineries, not
  repair bays) and, with the harvester switch on, sends an idle harvester to wait beside its best refinery
  (`Refinery_Waiting_Cell`), or guards in place when already within 4 cells of home (`ai-upgrade-plan.md` W1.1).
- **Human harvesters never re-queue (open):** `Mission_Guard`'s re-queue to `MISSION_HARVEST` is still gated on
  `!House->IsHuman` (`unit.cpp:5536`), so a player's idle harvester waits for an order. TF's walled-field retreat
  keeps a harvester in `MISSION_HARVEST`, for humans too, so this bites only when no ore was found at all.
- **Refinery contention in FINDHOME (fixed):** in EA, when `Find_Best_Refinery` returns NULL and the
  `ScenarioInit++` retry also fails, the harvester sits in FINDHOME with no `NavCom`, a silent stuck state. TF's
  FINDHOME has no retry: a harvester whose refinery is busy queues at its own `Refinery_Waiting_Cell`, and with the
  harvester switch on `Find_Best_Refinery` returns busy refineries too, so it waits in FINDHOME only when no refinery
  is in reach (`TF_Refinery_In_Reach`).
- **Unload-pad clear-out (open):** after unloading with an invalid `ArchiveTarget`, the harvester just `Scatter()`s
  and falls out of the harvest mission with no re-queue.

### Problem 5: harvesters drive into enemy territory (fixed)
`Tiberium_Check` scores only land type, overlay, fog and zone (a cell is worth `(OverlayData + 1) * value`, and the fog
test applies only to a player's harvester in `GAME_NORMAL`), and `ArchiveTarget` is pushed onto `NavCom` before the
ring scan runs, so a harvester that once mined in an enemy base goes back (the field manual's
[stock problems](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/harvesters.md#stock-problems),
ore picks ignore danger). The only danger reactions are after damage: a harvester below `ConditionYellow` with ore on
board flees to the refinery, and `Base_Is_Attacked` alerts the AI. TF's field pick weighs distance against nearby
enemy defences (`Goto_Tiberium`, `harvester-recovery-design.md`, The field pick); no `rules.ini` knob was added.

### Problem 6: the sticky refinery choice (fixed)
`Find_Best_Refinery`'s one-slot cache (`TiberiumUnloadRefinery`) returns the last refinery while it's still the
house's, out of limbo, not being sold, a `STRUCT_REFINERY` and in the same zone, whatever its distance or queue (the field manual's
[stock problems](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/harvesters.md#stock-problems)).
Its fallback, `Find_Docking_Bay` (`techno.cpp:7164`), picks the closest refinery with a free radio and returns NULL
when all are busy; FINDHOME then forces a ROGER with `ScenarioInit++`, but only at the closest. TF takes CFE's
Harvester Optimization and queue-jumping (`cfe-port-plan.md` §1).

---

## Combat and strategy

### Problem 7: `Greatest_Threat`'s ring scan keeps the last candidate (fixed in 4.1.0)
Range-limited scans keep the last candidate, not the best (the field manual's
[target-choice row](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/skirmish-ai-and-iq.md#stock-bugs-and-gaps)).
TF sets `bestval = value;` in each of the four ring blocks of `TechnoClass::Greatest_Threat` (`techno.cpp:2387`).

### Problem 11: `Computer_Paranoid` (AI gang-up) is off in skirmish (open)
In one-against-many games the AIs fight each other instead of ganging up on the human, and
`Rule.IsComputerParanoid = true` does nothing. `HouseClass::Computer_Paranoid` (`house.cpp:12696`), which allies
every AI against the humans once one is defeated, wraps its whole body in
`if (Session.Type != GAME_GLYPHX_MULTIPLAYER)`, with EA's comment "Re-enable this for multiplayer if we support
classic team/ally mode". Fix shape: drop the gate behind a lobby-respecting switch (`ai-upgrade-plan.md` W6).

### Problem 12: the spatial threat map is dead in skirmish (open)
`MapClass::Cell_Threat` (`map.cpp:1470`) scores cells from `HouseClass::Regions[].Threat_Value()`, but its only
feed, `Adjust_Threat`, is called from `ObjectClass::Mark` only when `Session.Type == GAME_NORMAL` (`object.cpp:1860`
and `1873`). In skirmish the region table stays empty and `Cell_Threat()` returns only the visibility flag, so teams
pick poor regroup routes and no threat-aware code has per-cell data. Fix shape: drop the gate at both lines.

### Problem 14: TeamType `Recruit` is gated to the campaign (open)
`TeamClass::AI` reaches `Suggested_New_Team` in skirmish, but the recruit step runs only when
`Session.Type == GAME_NORMAL` (`team.cpp:674`), so teams are created, never filled, and destroyed (EA's
team-destroy test also branches on `Session.Type`). No squad behaviour results. Dropping the gate is the first step of
`ai-upgrade-plan.md` W4 Route A; campaign TeamTypes may not behave sensibly without map-specific definitions.

### Problem 15: friendly-fire caution covers only buildings, and only `Supress=yes` weapons (open)
`TechnoClass::Area_Modify` (`techno.cpp:1664`) returns at once unless the firer's primary weapon `IsSupressed`; then it
halves a target's odds for each allied building within `FireSupress` cells, checking only `Cell_Building()` in its
four scan positions, never `Cell_Occupier()`. It applies to every house's target scans, not only the AI's (the field
manual's [friendly-fire row](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/skirmish-ai-and-iq.md#stock-bugs-and-gaps)). TF's only `Supress=yes` weapon is `[8Inch]` (`rules.ini`), as
in stock, so artillery and V2s get no friendly-fire caution at all, buildings included, and splash lands beside
their own infantry and tanks. Fix shape: set `Supress=yes` on the splash weapons that need it, and also check
`Cell_Occupier()` for allied technos.

### Problem 16: the AI's chosen enemy is almost never set (open)
`Expert_AI` re-picks `Enemy` whenever the `Attack` timer reaches 0, before `AI_Attack` resets it. Each candidate scores
`(MAP_CELL_W * 2 - Distance(Center, h->Center)) * 2` plus kills against this house (buildings x5, units x1),
base-size difference and +100 for the last attacker, and must beat `close = 0` (`house.cpp`, about lines 6991 and
7072). `Distance` is in leptons, 256 to a cell, so any base more than about a cell away scores far below zero and
the pick leaves `Enemy` at none (the field manual's [How it attacks](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/skirmish-ai-and-iq.md#how-it-attacks), with where `Enemy` is set
otherwise). Read from code, not watched in play. Fix shape: score distance in cells (or offset it) so a pick
happens, then let threat (kills, army size) compete with distance.

### Informational (not bugs)
- **AI aircraft prefer harvesters** (`aircraft.cpp`): the `THREAT_TIBERIUM` scan in `Mission_Hunt` is one of the few
  `Session.Type != GAME_NORMAL` gates that helps skirmish. Economic harassment is good AI.
- **The AI ignores the unarmed-building filter:** `Evaluate_Object` skips unarmed enemy buildings only for human
  players, so the AI targets silos, kennels and gap generators freely. Correct.

---

## Topic A: does the AI cheat?

Two material cheats and one start-up convenience. Stat biases are symmetric in skirmish (Problem 10), and starting
credits, MCVs and units are the same for every house (`Session.Options.Credits` and one MCV with Bases on, in
`scenario.cpp`).

### A-Cheat 1: target picks ignore fog (fixed in 4.1.0)
`TechnoClass::Evaluate_Object`'s "not discovered, bail" test runs only in `GAME_NORMAL` (the field manual's
[shroud row](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/skirmish-ai-and-iq.md#stock-bugs-and-gaps)).
`Greatest_Threat`'s ring scan bounds it to `crange` round each unit, but within that an AI scout has x-ray vision. TF
gates it on per-house discovery (`IsDiscoveredByPlayerMask`, `ai-upgrade-plan.md` W1.2, the fair-fog switch).

### A-Cheat 2: superweapon aim ignores fog (fixed in 4.1.0)
`Special_Weapon_AI` loops over every enemy building on the map with no discovery or `Is_Mapped` filter and aims at
the highest `Value()` (the same row). The stock AI aims its spy plane and paratroopers with it, and any nuke a mod
lets it build. TF filters the loop on the house's own discovery (W1.2).

### A-Cheat 3: an AI MCV shoves its own units out of the way (open, low)
In `UnitClass::Try_To_Deploy`, an AI MCV whose deploy spot is blocked by its own unit calls
`Flush_For_Placement(cell, House)` to scatter it (`unit.cpp:2212`, now through `MCV_Deploy_Building`); a human gets
the no-deploy cue and must move the unit. It is UI compensation more than a cheat, but helps the AI on cramped maps.

### Checked, no cheat
- **Income:** `Session.Options.Credits` is applied to AI and human alike (`Init_Data` in `scenario.cpp`, and
  `dllinterface.cpp`). `Harvested`, stolen credits, `Spend_Money`, `Refund_Money` and the refinery dump have no
  `IsHuman` branch.
- **Build prerequisites:** `HouseClass::Can_Build` returns true for an AI only when `Session.Type == GAME_NORMAL`
  (`if (!IsHuman && Session.Type == GAME_NORMAL) return(true)`), so in skirmish the AI walks the same prerequisite,
  level and ownership checks as the player.
- **Build speed:** `BuildSpeedBias` is 1.0x for every skirmish house. `FactoryClass::Start` starts a computer's build
  only if it can pay the first step (`if (House->IsHuman || House->Available_Money() >= Cost_Per_Tick())`), where a
  human's always starts, and every step is paid as it goes: if anything, the human has the edge.
- **Power:** `Power_Fraction()`, `Adjust_Power()` and `Adjust_Drain()` have no `IsHuman` branch.
- **Starting map awareness:** each house's shroud is a bit in `CellClass::IsMappedByPlayerMask`; AI houses start
  with the same shrouded map, and the AI set-up path calls no `Reveal_Map`.
- **Starting units and buildings:** `Create_Units` and the Bases-on branch use the same tables and one `UNIT_MCV` for
  everyone. `IsCompEasyBonus` doesn't apply: only the old `Assign_Houses` reads it, and the Remastered build calls
  `GlyphX_Assign_Houses` instead.
- **Cell threat spread:** `CellClass::Adjust_Threat`'s `IsHuman` branch only skips allied humans.

---

## Topic B: special units

Every deploy-mechanic unit has the same gap: `Mission_Unload` implements the deploy, but nothing issues the AI a
`MISSION_UNLOAD` without TeamType orchestration (the field manual's
[deploy row](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/skirmish-ai-and-iq.md#stock-bugs-and-gaps)),
the same shape as Problem 3b/3c. One special-action dispatcher in `Expert_AI` or `AI_Unit` could feed them all. All
open unless noted; the plan is `ai-upgrade-plan.md` W5.4.

- **MCV:** auto-deploy works (`Mission_Guard` issues `MISSION_UNLOAD` when an AI MCV idles with `IsBaseBuilding`
  set, which every skirmish AI with `IQ >= Rule.IQProduction` gets in `HouseClass::AI`; `Try_To_Deploy` picks the
  spot). There's no redeploy after losing the yard: `AI_Unit` rolls an unarmed MCV at weight 1 against weight 20 for
  armed units, so the AI is crippled for good (medium). TF's AI does queue an expansion MCV for a ferried beachhead
  (`TF_Ferry_Wants_MCV`), but not after losing its yard. Fix shape: bias `UNIT_MCV` up when no yard is owned.
- **Engineer:** used offensively. `InfantryClass::Greatest_Threat` sends an AI engineer straight to
  `House->ToCapture` within `0x0F00`, else adds `THREAT_CAPTURE`. `AI_Infantry` weights it only once it has more than
  five infantry, one at a time; in TF the TD and TS engineers join `AI_Attack`'s waves as `RENOVATOR` does, so
  `Mission_Hunt` can send them to capture. A damaged AI engineer on guard
  switches to `MISSION_HUNT` and charges. Nothing recaptures lost buildings.
- **Spy, thief and dog:** weight 0 in `AI_Infantry`'s skirmish picker, so never built; still true in TF. Their
  abilities are fully wired: the spy's infiltration (radar, sub pen to sonar, airstrip to parabombs), the thief's
  steal of half the enemy's money (any building with `Capacity > 0`), whose `Greatest_Threat` already adds
  `THREAT_CAPTURE | THREAT_TIBERIUM`, and the dog's `IsOrganic` targeting (the kennel test in `AI_Infantry` is in the
  campaign branch only). Fix shape: weight 1 to 2, the spy gated on `IQ >= Rule.IQSuperWeapons`, the dog on a
  kennel.
- **Tanya:** built at weight 1, one at a time. `InfantryClass::Greatest_Threat` stops a human's Tanya auto-firing,
  but an AI Tanya targets normally and hunts like a commando. She never plants C4 on buildings. Fix shape: prefer
  buildings when no infantry is in range.
- **Chrono tank:** built at weight 20 like any armed unit; `Mission_Unload` opens the player's teleport targeting
  (`SPC_CHRONO2`, `House->UnitToTeleport`) and waits for a click, with no AI dispatch, so AI chrono tanks drive and
  shoot like medium tanks.
- **Demo truck:** weight 20 (its blast is its primary weapon); `Fire_At` deletes the truck on first use, so it
  detonates on contact, but it picks the same `Greatest_Threat` target as any tank and dies to the first defence.
  Fix shape: bias it toward yards, refineries and factories (medium).
- **MAD tank:** weight 20; the quake runs only from `MISSION_UNLOAD`, which the AI never issues.
- **Minelayer:** weight 1; lays a mine and re-guards only from `MISSION_UNLOAD`, so AI minelayers wander unarmed
  (`todo.md`, Minelayer brain).
- **TF's own units the AI skips:** the Limpet Drone, Mobile EM-Pulse, Mobile Sensor Array and Mobile War Factory are
  left out of `AI_Unit`'s combat pick (`ai-upgrade-plan.md` W5.4).

---

## Topic C: tactical micro

All open unless noted.

- **Retreat:** no damage-based retreat. `FootClass::Mission_Retreat` walks to the map edge to leave a team; combat
  units fight on below `ConditionRed`. Only `IsFraidyCat` units (civilians) flee, through `Fear` and `Scatter`, and a
  harvester with ore flees when damaged. Fix shape (medium): an AI unit below `ConditionRed` heads to a repair bay if
  one exists.
- **Repair:** the `Find_Docking_Bay(STRUCT_REPAIR)` lookups are all in player-action paths, so even with a repair bay
  (Problem 13) no AI vehicle drives to it when damaged. Fix shape (medium): self-assign `MISSION_REPAIR` below
  `ConditionRed` when a free `STRUCT_REPAIR` exists.
- **Kiting:** none. Long-range units close to `In_Range` and stop (`Approach_Target`). Low priority given RA's small
  range differences.
- **Focus fire:** none. Each hunting unit calls `Target_Something_Nearby(THREAT_NORMAL)` and takes its own target,
  so two tanks side by side often pick different ones (the field manual's
  [How it attacks](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/skirmish-ai-and-iq.md#how-it-attacks)).
  Fix shape (medium): after `AI_Attack`, share the best target within each zone's hunters.
- **Formation movement:** none; units move on their own paths. TF spreads group moves (`cfe-port-plan.md` §1.1)
  but has no formations.
- **Regrouping (fixed for TF's AI):** the stock attack has no wave, no wait for a force and no fall-back, and its
  timer sets the interval, not the army's size (How it attacks). TF's waves have a value floor and gather at a
  staging cell (`ai-upgrade-plan.md` W4). A Hard house releases them on the CFE attack-move, so the wave fights
  through defences with the player's threat response (`cfe-port-plan.md` §1.2) instead of beelining to one building
  and soaking every turret on the way.
- **Counter-attack:** `TechnoClass::Base_Is_Attacked` (`techno.cpp:6098`) works in skirmish: it pulls infantry and
  units back to an attacked building, weighted by `Risk()`, threat capability and zone, gated on `!House->IsHuman`,
  and called from building damage and from a harvester under attack. Its `Suspend_Teams` is moot while TeamType
  recruit is gated (Problem 14), but the rerouting works.
- **Garrison:** RA has no garrison feature (no `Garrison` token anywhere in the source). The nearest is
  `MISSION_AMBUSH`, which the AI gets from `Try_To_Deploy` and scenario triggers, never dynamically in skirmish. Out
  of scope.

---

## Pathfinding: the alternatives considered

The dock and chokepoint jams were a traffic problem, not a search problem: a better search alone doesn't stop units
meeting in a cell after their paths are committed. What ships is CFE's A\*, spread group moves, give-way and corridor
claims (`cfe-port-plan.md` §1.1, `chokepoint-reservation-design.md`); the reservation table is still planned
(`ai-upgrade-plan.md` W1.4). The other options weighed:

| Approach | What it gives | Verdict for RA |
|---|---|---|
| JPS (Harabor 2011) | 10-30x faster than A\* on uniform grids by skipping symmetric paths | its edge is speed, which RA-sized maps don't need |
| JPS+ | precomputed JPS, about 100x A\*, needs map preprocessing | not needed |
| HPA\* (Botea 2004) | hierarchical pathfinding, TS's approach formalised | overkill below huge maps; TS's own is weighed in `path-failure-livelock-design.md` |
| Flow fields | one gradient per destination, every unit follows it | elegant for a harvester fleet on one field; not built |
| NavMesh | the standard for non-grid 3D games | wrong fit for a grid |
| Reservation tables / WHCA\* (Silver 2005) | units publish their paths; search aware of others' future ticks (TS is said to ship reservation tables; not checked in OpenTS) | the reservation table is W1.4; full WHCA\* rejected as invasive |
| ORCA / RVO | velocity-based local avoidance | assumes sub-cell motion; RA moves cell by cell |
| Cooperative yield and push | idle blockers asked to step aside (TS is said to do this too; not checked) | shipped as give-way and the deadlock breaker |

OpenRA (MIT) is the closest reference for this exact game: its pathfinder is said to be occupancy plus local
avoidance plus repath, with no space-time reservation (`OpenRA.Mods.Common/Traits/World/PathFinder*.cs`; not checked
against OpenRA's source). 0 A.D. mixes a long-range JPS-like search with a custom
short-range one; Spring and BAR use flow fields with per-unit avoidance.

---

## Not yet researched

- **Triggers in skirmish:** which trigger paths (`trigger.cpp`, `trigtype.cpp`) are `GAME_NORMAL`-gated, whether the
  AI ever makes its own TeamTypes, whether triggers could add behaviours without C++ changes, and which trigger
  actions or events are declared but not implemented.
- **Aircraft AI:** `AI_Aircraft`'s return-to-airstrip, helicopter hover-fire-retreat, paradrop dispatch, and aircraft
  in `AI_Attack` waves against acting alone.
- **Compiled-out blocks:** two found (`AI_Base_Defense` in `#ifdef NEVER`, the repair bay queue in `#ifdef OLD`);
  a grep for `#ifdef NEVER` and `#ifdef OLD` across `redalert/*.cpp` may find more.
- Building placement and the IQ map are researched: `ai-upgrade-plan.md` W3 and W7.
