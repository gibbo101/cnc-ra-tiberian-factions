# CFE Patch Redux port plan

**Status:** Reference. The first wave shipped in 2.1.0 to 2.4.0: pixel-perfect zoom, rally points,
harvester queue-jump and optimisation, smarter repair bay, attack-move, A*, infantry Tiberium
aversion. Smarter SAMs and harvester self-repair shipped in 2.4.0; line-fill walls shipped in 5.0.0
as our own build. Since 5.7.0 each ported feature that changes play has a switch (`player-settings.md`), except the data-only
harvester self-repair.
**Open:** the second wave (§2) and the bugfix inventory (§3) are candidates.

TF's ports of QoL features and bugfixes from **CFE Patch Redux** by ChthonVII.

- **Source and licence:** see the field manual's [Porting CFE Patch Redux into your DLL](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/cfe-patch-ports.md#cfe-patch-redux-in-brief),
  CFE Patch Redux in brief. Local clone `reference/cfe-patch-redux/` (full history; RA and TD 1.9 test builds
  through 2025-04). We already publish source; keep attribution and source publication in order (§6).
- **Their RA changelog files:** `Documentation/Changelogs/1.7/RA_Changelog_1.7.txt` and
  `1.8/RA_Changelog_1.8.txt`. Pre-1.7 fixes are only in git history.
- **Their feature toggles:** everything is INI-gated: defaults in `Mod Data RA/CCDATA/DEFAULT.CFEPATCHREDUX_RA.INI`
  (TD: `DEFAULT.CFEPATCHREDUX.INI`), overridden by the player's `CFEPATCHREDUX_RA.INI` — useful for
  locating each feature's code (grep the INI key name). TF doesn't reproduce their settings system (§4).

## Porting ground rules

1. **Method:** see the field manual's [Porting CFE Patch Redux into your DLL](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/cfe-patch-ports.md#how-to-port-a-change)
   (transplant by hand, take the LAN-safe post-1.7 code, check what Vanilla Conquer already has). §3.1 lists
   the fixes already in our base, §3.2 the two disputed ones.
2. Per workspace rules: TD-authentic stats stay untouched. CFE's balance content (TD Balance
   Patch, veterancy, OpenRA supers, instant capture, etc.) is **out of scope** — see §5.
3. Each ported feature gets its own commit citing the CFE source commit(s)/files, and a
   CHANGELOG entry.

---

## 1. QoL first wave (shipped)

| # | Feature | CFE INI key (locator) | Notes on our port |
|---|---|---|---|
| 0 | **Pixel-Perfect Zoom** | none (static; data-only) | No DLL code. Ours sits in `Data/XML/GameConstants_Mod.xml`, which ClientG merges over the base GameConstants (`config-meg-lever-audit.md`); CFE commit `ea2dde5`. See the field manual's [Pixel-perfect zoom](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/cfe-patch-ports.md#pixel-perfect-zoom). |
| 1 | **A\* Pathing** | `ASTAR_PATHING` | Replaces "crash and turn" (`FootClass::Find_Path_AStar`, `findpath.cpp`), with EA's edge-follower as the fallback; the 1.8 version, which fixed the crash on paths over 200 cells. §1.1. |
| 2 | **Attack-Move** (Shift+Click) | `ATTACK_MOVE` | Post-1.7 LAN-safe rework with all special cases (aircraft RTB on empty ammo, boats brief-attack, minelayers, chronotanks; §1.4). Q-attack-move rides VANILLA's queue (CFE's queue rewrite NOT taken — fallback if flaky: stop converting ATTACKMOVE→QATTACKMOVE). One build fix: `AircraftClass::IsLanding/IsTakingOff` made public. **One deliberate deviation from CFE — §1.2 (passive-building targeting).** |
| 3 | **Rally Points** | `RALLY_POINTS` | Desktop-verified all factions. Incl. v1.9 long-line crash fix + two improvements over CFE: rally to "unplaceable" cells (their Can_Enter_Cell placement-legality dead zones near cliffs/shore/ore) and DOTGDI/DOTNOD faction end-dots. Repair bays (FIX, TDFIX, TSDEPT) take a rally point too, through the Smarter Repair Bay exit (`BuildingClass::Can_Have_Rally_Point`). The `DLL_Draw_Intercept` ShapeSize-override trap it hit (building-attributed named draws inflate to building size for TD buildings) is fixed. |
| 4 | **Harvester Queue Jumping** | `HARVY_QUEUE_JUMP` | Independent toggle in CFE; works with #5. Trap for any harvester count: `UQuantity` can't count TD or TS harvesters, because types past `UNIT_RA_COUNT` fold onto vanilla slots and it has only `UNIT_RA_COUNT - 3` entries; TF counts harvesters through the Units heap instead (`TF_Harvesters_Owned`). |
| 5 | **Harvester Optimization** | `HARVY_OPTIMIZE` | Nearest-refinery with per-inbound-harvester distance penalty. CFE's recommended choice over the older Load Balancing (which auto-disables when both are on), so Load Balancing isn't ported. |
| 6 | **Smarter Repair Bay** | `SMARTER_REPAIRBAY` | Queue for occupied bay + fixed RA bay rally + exit logic (§1.3). Includes their fix for units ignoring collision on the bay. Covers STRUCT_TDFIX alongside RA's FIX. |
| 7 | **Infantry Tiberium Aversion** | `INFANTRY_TIBERIUM_AVERSION` under `[SETTINGS]` (TD side) | In our A* (`FootClass::Find_Path_AStar`, findpath.cpp): +`TIB_AVERSION_COST`=2 cells per Tiberium cell, gated on `What_Am_I()==RTTI_INFANTRY`. **Two deliberate RA deviations from CFE:** (1) keyed on `Overlay==OVERLAY_TIB01` NOT `Land_Type()==LAND_TIBERIUM` — in RA, Ore/Gems share LAND_TIBERIUM but are harmless, so the land-type test would repel infantry from ore (same lesson as the infantry.cpp damage hook); (2) NO chem-warrior (E5) exemption — unlike TD/CFE, OUR Tiberium damages ALL infantry, so all infantry avoid it (aversion tracks damage). Finite penalty = infantry still cross a wide field with no detour. |
| 8 | **Smarter SAMs** (TD-only in CFE) | `SMARTER_SAMS` | Our own code for our own TD SAM, not a port of CFE's (`TIBERIANDAWN/BUILDING.CPP` ~5120–5290 in the reference clone): a TDSAM that loses its target part-way through a surfacing, volley not yet spent, rescans for another airborne target and stays up to engage it before retracting, instead of wasting the rise/lower reload cycle. `BuildingClass::TDSAM_Try_Reacquire` (building.cpp) is called from the four target-lost TDSAM states (READY/FIRING → re-rotate from READY; READY2/FIRING2 → READY2, 1 shot left). The hardwired 2-shot volley equals CFE's default `SMARTER_SAM_AMMO=2`; CFE's `SmarterSAMAmmo`/`SmarterSAMBalanceDelay` knobs are not reproduced. |
| 9 | **Harvester Self-Repair** (TD-only in CFE) | `HARVY_SELF_REPAIR` | Data-only: `SelfHealing=yes` on `[TDHARV]`, so GDI/Nod harvesters heal to 50% at the same rate and cap as RA's `[HARV]` (`TechnoClass::AI`; the field manual's [Harvester self-repair](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/cfe-patch-ports.md#harvester-self-repair)). A frame-based heal block in `UnitClass::AI` double-healed HARV at a far faster rate; CFE's veterancy-entangled code is the wrong model, and the engine flag the right one. |

### 1.1 Pathfinding: A* first, cooperation on top

The dock and chokepoint jams are a traffic/cooperation problem, not a path-search problem, so a better search alone
doesn't fix them (`ai-improvements.md`, Pathfinding: the alternatives considered). CFE's A\* replaced the search
layer: battle-tested in this exact engine, LAN-safe, its >200-cell crash fixed. JPS's edge over A\* is mostly speed,
which RA-sized maps don't need. The layer on top is ours: spread group moves (below) and the chokepoint layers
(§1.1.1). WHCA\*/ORCA stay rejected as overkill or engine-hostile; OpenRA's pathfinder remains the reference.

**What the A\* playtest showed.** The release carried a `TF_DEV_BUILD` diagnostic (`tf_astar.log`: per-fallback
detail and a running success/fallback tally, appended per match). On a snow map A\* succeeded about 74% of the time
with **zero genuine long-path search failures**: every fallback to the legacy search was "the destination cell I
was told to enter is occupied by a friendly". In one match 78% of fallbacks (252 of 325) targeted one cell,
`(111,88)`; another magnet, `(30,32)`, was hit by 6+ unit types. Seen in play as the 1-wide jam, units running up
and down, tanks tracing a cliff. Why a group move sends every unit to one cell, why the edge-follower hid it and why
A\* gives up on it: the field manual's
[Group moves aim every unit at one cell](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/ai/pathfinding.md#group-moves-aim-every-unit-at-one-cell).
In the Remaster build the click reaches `DisplayClass::Mouse_Left_Release` through
`INPUT_REQUEST_COMMAND_AT_POSITION` → `TacButton.Command_Object(LEFTRELEASE)`, and a formation move needs every
selected unit in one control group with a stored `XFormOffset != INVALID_FORMATION`, set only by the formation toggle
(control group + F-key, `DLLExportClass::Team_Units_Formation_Toggle_On`), which `foot->Adjust_Dest(cell)`
(`foot.cpp`) then offsets. The contention is vanilla behaviour, not a regression from the A\* port.

**Destination spread, shipped in 2.2.2:** for a plain move or attack-move of two or more foot units,
`Mouse_Left_Release`'s `do_spread` gate gives each a distinct cell from `FootClass::Find_Spread_Cell`
(`findpath.cpp`): the nearest cell to the click, within 8 cells, that the unit can enter now, that no earlier unit
claimed, and in the clicked cell's `Zones[MZone]`; the click itself when none is free. Formation moves still use
`Adjust_Dest`. Verified in play on a tight same-zone clump: the fallback rate fell from about 26% to 12%. The
spread search runs its own ring. The destination is set at click time and travels in each unit's `MEGAMISSION`
event, so the synced loop is unchanged. Not built: preferring, for each unit, the free cell nearest its own position
to cut path-crossing.

**Still worth a look:** `Find_Path_AStar`'s close-impassable bail (straight-line distance ≤3 → give up,
`impassableCloseEnough`) may do more harm than good now that spread and the chokepoint layers exist. The test cells
are `(30,32)` and `(111,88)` on the snow map: watch the tally and the per-cell fallback concentration.

### 1.1.1 Chokepoints (shipped in 2.3.0)

Give-way, corridor claims and the deadlock-breaker scatter: `chokepoint-reservation-design.md`. The reservation
table with soft A\* costs (the `Passable_Cell` cost hook Tiberium aversion uses) is still planned
(`ai-upgrade-plan.md` W1.4).
**Dead route:** a cooperative yield that backs a unit away from its blocker reverses it into the
unit behind it, because the common jam is a same-direction single-file queue
(`DriveClass::Try_Cooperative_Yield`, never shipped).

### 1.2 Attack-move deviation from CFE: passive-building targeting

**Deliberate one-feature departure from CFE attack-move behaviour**, logged here because the
porting rule is "document deviations".

- **CFE / vanilla behaviour:** a human player's units never auto-target an enemy building with no weapon, and CFE
  keeps that filter, so its attack-move drives past passive buildings (the field manual's
  [Attack-move](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/cfe-patch-ports.md#attack-move),
  Weaponless buildings). The filter is `TechnoClass::Evaluate_Object`'s `tclass->PrimaryWeapon == NULL` "not
  aggressive" test; CFE's `Evaluate_Object` is byte-identical to ours there, with no attack-move special case.
  Defensive structures (turrets, Tesla, Obelisk, SAM, gun towers) carry weapons, so both fight them.
- **The goal:** classic-C&C / StarCraft a-move — attack-move shells *everything* in
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
- **Threat response:** the two-pass priority applies only at *initial* acquisition, so a tank locked on an in-range
  passive building would keep shelling it while a Tesla coil or enemy units chewed it up. A block in the
  `TechnoClass::AI` attack-move retarget runs each tick: if the current target is a weaponless building, an
  armed-only `Greatest_Threat(THREAT_RANGE)` scan runs and, if anything armed is in range, the unit disengages and
  switches to it. It fires only when there's a real threat to switch to (never swaps one passive building for
  another); aircraft + move-locked boats are exempt. It never switches between two armed targets (no dithering).
  Verified in play.

### 1.3 Repair-bay exits and the minelayer

- **`DoSmarterRunAway`** picks the cell a repaired unit leaves to. The RA repair pad is a plus
  shape, so its cardinal exits are two cells out; the TS Service Depot is solid, so every exit is two
  cells out and never through the gantry. Units on the chosen cell and just beyond are asked to
  scatter, because the movement code treats the leaving unit as close enough and won't move them.
- **`MinelayerFindSpot`** steers round cloaked enemy mines (the field manual's
  [Attack-move](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/cfe-patch-ports.md#attack-move), The minelayer sees hidden mines). TF
  carries the leak; it came with the port.

### 1.4 Attack-move special cases (`TechnoClass::AI`)

- **Chrono Tank:** when charged it teleports toward `RememberedNavCom`. `Teleport_To` resets
  attack-move, so the state is saved and restored, only while `NavQueue` still holds movement. This
  replaces CFE's `SkipNavQueueUpdate`, which is not ported.
- **Boats:** `AttackMoveBoatClock` is set to 180 on engaging and, for its last 90 frames, forces the
  boat back to moving. Boats drop out-of-range targets rather than chase them (turning, jams,
  beaching). Subs are exempt from the lock, missile subs from the give-up.
- **Dogs and aircraft** never retarget mid-fight.
- **Aircraft out of ammo** always abort an attack-move; CFE does so only with its Smarter-Aircraft
  option.

## 2. QoL second wave (candidates, not yet decided)

- **Q-Move Overhaul** (1.8) — queued-waypoint system rework; optional loops + aircraft q-move.
- **Configurable Build Distance** — TD-style 0-gap base spacing is thematically interesting for our TD factions.
  CFE's TS/RA2-style wall building isn't needed: TF's line-fill walls are its own (`house.cpp`,
  `TF_Is_Line_Fill_Type`).
- **Smarter Aircraft** — no-ammo aircraft ignore attack orders; helicopters re-path on target
  move; fly-in on helipad Y. Touches our Orca/Apache.
- **Commando/Tanya Guard** — guard-mode infantry attacks; covers our TD Commando. v1.9 HEAD
  has a `Target_Legal()` fix for this — take it.
- **Safe Sabotage** — no survivors from C4. CFE demoted default to SP-only (MP-overpowered).
- **Suspend Building Repairs** — pause instead of cancel when broke.
- **Smarter Chrono / Smarter Sonar / Building Capture Announcements** — RA-side polish.
- **Smarter Mammoths** (TD-only) — missiles vs infantry. AUDIT FIRST: our TD-ported Mammoth
  may already do this via RA's secondary-weapon convention.
- **Better Tiberium/Ore Growth** — we have our own growth; compare algorithms. The
  blossom-tree-spawns-visceroid flavor is adoptable standalone.
- **Meaner Visceroids** (TD-only) — threat buffs for our visceroids.

## 3. Bugfix inventory

### 3.1 Already in our base (no action — listed to prevent re-porting)

From Vanilla Conquer: memory/UB cleanup (delete-on-void*, virtual destructors, overlapping strcpy/memcpy,
List_Copy/MemCopy), radar signed/unsigned + missing IsActive checks, harvest-via-radar,
Ukraine general using Stavros voice, mobile gap generator not updating in motion, off-by-one
waypoint error, Monster Tank Madness mission-critical units invisible, infinite "new
construction options" announcement (captured-MCV aircraft buildings), building off stale
proximity of a destroyed building, MIG pip display, building occupy-list OOB read, MIX-file
open failure leak, savegame Nod radar colour (legacy-only), helipads counted toward the fixed-wing
aircraft limit (`362b2a52a`), reshroud hiding allies despite `IsAllyReveal` (`2bfee4fd6`), and the
reveal crate blocked after a reveal→darkness sequence (`e57652a54`).

TF's own: the sidebar off-by-one crash (EA repo issue #105; columns hold 120 since 5.0.0); per-house "discovered"
flags, done as the per-house intel layer for fair-fog AI (`ai-upgrade-plan.md` W1.2); MCV ActLike across
undeploy→redeploy (moot: every faction's MCV and yard are their own types, so the type carries the faction).

### 3.2 Audits — ChthonVII says VC's fix is WRONG (check our copies vs his)

CFE's own words on both: the field manual's [Already in Vanilla Conquer](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/cfe-patch-ports.md#already-in-vanilla-conquer), Two fixes disagree.

- [ ] `Base_Is_Attacked()` defender selection by strength (VC `c608b48`).
- [ ] `MISSION_NONE` used as an array index, OOB reads (VC `624e391`), and its one memcpy→memmove.
- [ ] The overlapping copy in the sidebar the Remastered DLL runs: `StripClass::Recalc` in `sidebarglyphx.cpp`
      (~L543) still closes the gap with `memcpy` over overlapping ranges, undefined behaviour; `sidebar.cpp` already
      has the `memmove` CFE and VC made, which neither applied here. Make it a `memmove`.

### 3.3 CFE-original engine fixes, RA-relevant (port candidates)

Crashes / UB:
- [ ] Crash loading custom map with invalid mission string in INI (UB in stricmp)
- [ ] Crash when infantry move into a building during their death animation
- [ ] Crash when a unit death animation overlaps a building (missing IsActive)
- [ ] Multiple MAD Tanks detonating on same/consecutive ticks
- [ ] Chain lightning: MISSION_NONE segfault + force-fired-at-ground misbehavior
- [ ] Building placement map-wrapping bug
- [ ] **Mod variables reset to 0 on savegame load in RA** — high relevance: we carry
      Tiberium/visceroid/blossom state. Audit our save path regardless of whether we take
      their fix.

Multiplayer correctness (matters for LAN play):
- [ ] MP sound routing — "HUGE number" of sounds playing for wrong player / not playing for
      right player
- [ ] Unit flash effect shown to wrong players
- [ ] Hand/Barracks/Factory/Airstrip wrongly flagged "captured" when built in MP → reduced
      crew spawns

Gameplay logic:
- [ ] Fixed-wing planes fire 1 extra shot after expending ammo (pair with optional MIG Ammo
      Fudge if we care about preserving 4-shot MIG feel)
- [ ] MISSION_AMBUSH did nothing
- [ ] Gunboats not firing when spawned off-map
- [ ] Units ignoring collision detection on the repair bay (folds into first-wave #6)
- [ ] Custom missions using wrong AI building-repair threshold (matters for our campaign arc)
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

- [ ] Crate outcomes that may kill the opener postponed past the AI loop (use-after-free +
      permanently-reserved cell). TD-only, author-flagged "needs ported to RA".
- [ ] Search-range fix excluding pre-placed/CPU units until activated. TD-only, same flag.
- The rally-point long-line crash fix is in, with first-wave #3.

### 3.6 TD-side CFE fixes that land on OUR content (we have these systems in RA)

- [ ] AI houses wrongly consider HOUSE_NEUTRAL and **HOUSE_JP** when picking an enemy to
      fixate on — our visceroids are HOUSE_JP. Check RA's house-selection equivalent even if
      the TD fix doesn't transplant directly.
- [ ] Neutral "kill structures" objective insta-kills visceroids (HOUSE_NEUTRAL owns no
      structures) — relevant if our campaign/co-op missions use such objectives.
- [ ] Players can one-way ally with visceroids.
- [ ] AI overweights proximity when picking a target house in MP (RA's own pick has the same bias,
      `ai-improvements.md` Problem 16).

## 4. Settings policy

CFE gates everything behind its INI (`DEFAULT.CFEPATCHREDUX_RA.INI`, overridden by `CFEPATCHREDUX_RA.INI`). Ours:

- **No CFE-style INI.** Each ported feature that changes play is a switch on TF's settings page, saved in
  `tf_settings.ini` (`player-settings.md`): attack-move, rally points, A\*, the harvester fixes, the smarter repair
  bay and the SAMs. Off is vanilla's own code path. Pure bugfixes, and the data-only harvester self-repair, have no
  switch.
- **Gameplay-affecting fixes (§3.4):** decide per item; if adopted, they're documented in the CHANGELOG and get a
  switch like the rest.
- Dev-time toggles, if needed during bring-up, sit behind `TF_DEV_BUILD` or `#if 0` and are never
  flipped without a deliberate decision.

## 5. Explicitly out of scope (balance/flavor — conflicts with TD-authentic rule)

Veterancy system, TD Balance Patch, OpenRA Wide/Quick Supers, Chrono Disaster Overhaul
(beyond the Timequake bugfix), Instant Capture (clashes with our TD-authentic engineer),
Tiberium/Ore Growth Scale + Silo/Refinery Capacity dials, Nuke Tank, Turkey-bonus selector,
Jozef's Silver Funpark, Red USSR Flag art, Megamap/8-player (TD-side), Building Death
Announcements (TD), GDI9 Fix / MP Preplaced Unit Order / Disable MP Neutral Attacks
(TD campaign/MP-map specifics), Dr. Moebius idle quote.

Revisit any of these only as a deliberate decision, most plausibly during a balance
pass (veterancy) or the campaign arc (mission-side fixes).

## 6. Credits / attribution to carry

Credit in README/Workshop description per GPL + courtesy:
**cfehunter** (original CFE Patch), **Root-Core** (RA port), **ChthonVII** (CFE Patch Redux —
the bulk of what we're porting), plus feature-specific credits they carry (screaming_chicken
for several fixes, bleid for Pixel-Perfect Zoom).
