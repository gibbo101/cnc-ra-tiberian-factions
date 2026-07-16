# AI targeting of Logic-aliased buildings

> **OBE (re-audit 2026-07-16).** The Logic= aliasing this doc analyzes no longer governs any TD
> building — all are first-class engine StructTypes now — and the recommended Option-A fix
> (per-building `Points=` in rules.ini, TD-authentic values) is implemented (e.g. `[TDNUKE]
> Points=50`; loader at techno.cpp:7846). Retained as a how-to reference for future buildings.

Findings doc for the v0.3.0 thread: **"AI doesn't target TDNUKE for destruction."**
Investigation date: 2026-05-19. Code references are paths under `redalert/` on `feature/emc-integration` at `0accffb`.

---

## TL;DR

**Root cause: missing `Points=` field in `rules.ini`.**

`TechnoTypeClass::Read_INI` (`redalert/techno.cpp:7067`) populates `Risk`, `Reward`, and
`Points` from a single INI key:

```cpp
Risk = Reward = Points = ini.Get_Int(Name(), "Points", Points);
```

For a mod-defined building, the default is whatever the constructor left in `Points`,
which is **0** (`redalert/techno.cpp:6686-6687` initialises both `Risk(0)` and `Reward(0)`).
The `Logic=POWR` aliasing in `BuildingTypeClass::Read_INI` (`redalert/bdata.cpp:3731-3759`)
copies the donor's Type/Size/Anims/Buildup/etc., but **does not copy `Risk`/`Reward`/`Points`**.

So `[TDNUKE]` with no `Points=` line ends up with `Risk = Reward = 0`, which makes
`TechnoClass::Value()` (`redalert/techno.cpp:5171`) return 0:

```cpp
return Risk() + Techno_Type_Class()->Reward + value;   // 0 + 0 + 0
```

`Evaluate_Object` (`redalert/techno.cpp:1768-1883`) sets `value = rawval + Crew.Kills`, applies
threat-type and zone modifiers, then bails at the bottom:

```cpp
if (value) { return true; }
value = 0;
return false;     // candidate rejected
```

For generic `THREAT_BUILDINGS` / `THREAT_NORMAL` scans (the auto-target / hunt path), there is
no threat-type bonus that would resurrect a zero-value candidate. The enemy-house and
outside-base-zone modifiers multiply, so they cannot turn 0 into non-zero either. **The
candidate is silently dropped before any target ranking.**

POWR works because its rules.ini block has `Points=40` (rules.ini:1633), so its `Value()` returns
80, the rest of the scoring builds on that, and it survives the `if (value)` gate.

**Fix:** add `Points=N` to every TD-prefixed building in rules.ini, using the donor's vanilla
Points value as the starting point.

---

## What we ruled out

These were the original suspects from `docs/catalogue.md:15`. None of them is the bug:

- **`STRUCTF_*` filters in target selection.** `STRUCTF_*` is only used as a possession
  bitmask (`HouseClass::ActiveBScan`, `BScan`) for special-ability gating (radar, GPS,
  chronosphere, etc.) — see `redalert/house.cpp:881-1900`. No target-selection code path
  filters on `STRUCTF_*`.
- **`STRUCT_COUNT`-bounded loops.** The few STRUCT_COUNT loops we found
  (`redalert/house.cpp:1239`, `house.cpp:258` for `BuildChoice`) are statistics/sonar-trigger
  / build-list code, never target evaluation. Target scans iterate the actual ground layer
  (`Map.Layer[LAYER_GROUND]`) or `Buildings.Count()` heap, which include mod entries.
- **`IsLegalTarget`.** Mod buildings get `is_legal_target=true` from the dynamic constructor
  (`redalert/bdata.cpp:2858`). Confirmed; not relevant.
- **Quarry → ThreatType translation.** `redalert/team.cpp:2687-2725` cleanly maps QUARRY_BUILDINGS
  → THREAT_BUILDINGS, QUARRY_POWER → THREAT_POWER, etc. No mod-vs-vanilla split.
- **`IsDiscoveredByPlayer`.** Bypassed in skirmish (`Session.Type != GAME_NORMAL`), so the
  symptom would not be visibility (`redalert/techno.cpp:1635`).

---

## The full AI-targeting code map

For future TD building debugging, here are the call sites that matter:

### Entry points that ask the AI "what should I shoot?"

| Caller | Threat flags | Location |
|---|---|---|
| Team mission `TMISSION_ATTACK` (per-Quarry) | `THREAT_BUILDINGS` / `THREAT_POWER` / `THREAT_FACTORIES` / `THREAT_BASE_DEFENSE` / `THREAT_TIBERIUM` / `THREAT_FAKES` / `THREAT_INFANTRY` / `THREAT_VEHICLES` / `THREAT_NORMAL` | `redalert/team.cpp:2687-2725` |
| Leader picking team target | `THREAT_NORMAL \| THREAT_RANGE` | `redalert/team.cpp:2932` |
| `HouseClass::AI_Attack` → unit `MISSION_HUNT` → unit's own scan | (unit-internal `Greatest_Threat` call) | `redalert/house.cpp:5337-5391` |

### The scoring pipeline (all routes converge here)

1. `TechnoClass::Greatest_Threat(threat)` — `redalert/techno.cpp:2126-2419`
   builds RTTI mask, picks scan area (range-limited radial scan or whole-map sweep), then
   calls `Evaluate_Cell` / `Evaluate_Object` on every candidate.
2. `TechnoClass::Evaluate_Object` — `redalert/techno.cpp:1554-1884`
   the gatekeeper. Filters in order:
   - **RTTI mask** (line 1646)
   - **`IsLegalTarget`** (line 1656)
   - **Civilians-only / Capturable-only / sub special cases** (1686-1710)
   - **Human-controlled units skip unarmed buildings** (1717-1726) — this is why human
     players don't auto-fire on enemy power plants. AI houses (`!IsHuman`) bypass this.
   - **`THREAT_TIBERIUM` requires `Capacity` or harvester** (1741-1760)
   - `rawval = object->Value()` ← **THE 0-VALUE GATE STARTS HERE** (1768)
   - Enemy-house +500 then ×3 (1776-1779)
   - Outside-base-zone ×2 (1785-1787)
   - **THREAT_FAKES** zeroes value for non-fake buildings (1793-1813)
   - **THREAT_POWER** adds `Power*1000` if `Power>0`, else zeroes (1820-1826) ← resurrects 0
   - **THREAT_FACTORIES** zeroes for `ToBuild==RTTI_NONE` (1832-1836)
   - **THREAT_BASE_DEFENSE** zeroes for no `PrimaryWeapon` (1842-1846)
   - Nervous-zone bias and distance scaling (1853-1874)
   - `if (value) return true; else return false;` (1870-1883)
3. `BuildingClass::Value()` — `redalert/building.cpp:6084-6113`
   special-cases fakes to look up the real building's Risk+Reward, then falls through to
   `TechnoClass::Value()`.
4. `TechnoClass::Value()` — `redalert/techno.cpp:5138-5172`
   `return Risk() + Techno_Type_Class()->Reward + transport_contents;`
5. `TechnoClass::Risk()` — `redalert/techno.cpp:5728-5732`
   `return (Techno_Type_Class()->Risk);` — straight field read.

### Where Risk/Reward come from

- Initialised to **0** in the dynamic TechnoTypeClass constructor (`redalert/techno.cpp:6686-6687`).
- Loaded from `Points=` in rules.ini for both `Risk` and `Reward` (`redalert/techno.cpp:7067`).
- **NOT** copied by the Logic= aliasing in `bdata.cpp:3731-3759`.

---

## Affected buildings — TD-authentic Points values

Every TD-prefixed building added via Logic= without a `Points=` line in rules.ini will
have the same problem. The values below come from `tiberiandawn/bdata.cpp` — the
constructor argument commented `// RISK/RWRD: Risk/reward rating values` in each TD
class definition. Cross-references are also in `docs/catalogue.md`'s master table.

| TD-prefixed | TD donor class | TD source line | RISK/RWRD |
|---|---|---|---|
| TDNUKE | ClassPower (NUKE) | `tiberiandawn/bdata.cpp:926` | 50 |
| TDNUK2 | ClassAdvancedPower (NUK2) | `tiberiandawn/bdata.cpp:978` | 75 |
| TDPROC | ClassRefinery (PROC) | `tiberiandawn/bdata.cpp:620` | 55 |
| TDSILO | ClassStorage (SILO) | `tiberiandawn/bdata.cpp:672` | 16 |
| TDPYLE | ClassBarracks (PYLE) | `tiberiandawn/bdata.cpp:1132` | 60 |
| TDHAND | ClassHand (HAND) | `tiberiandawn/bdata.cpp:1182` | 61 |
| TDWEAP | ClassWeapon (WEAP) | `tiberiandawn/bdata.cpp:304` | 86 |
| TDAFLD | ClassAirStrip (AFLD) | `tiberiandawn/bdata.cpp:875` | 86 |
| TDHQ | ClassCommand (HQ/RADAR) | `tiberiandawn/bdata.cpp:773` | 20 |
| TDEYE | ClassEye (EYE) | `tiberiandawn/bdata.cpp:247` | 100 |
| TDTMPL | ClassTemple (TMPL) | `tiberiandawn/bdata.cpp:196` | 20 |
| TDFIX | ClassRepair (FIX) | `tiberiandawn/bdata.cpp:1284` | 46 |
| TDHPAD | ClassHelipad (HPAD) | `tiberiandawn/bdata.cpp:722` | 65 |
| TDGTWR | ClassGTower (GTWR) | `tiberiandawn/bdata.cpp:354` | 25 |
| TDATWR | ClassATower (ATWR) | `tiberiandawn/bdata.cpp:406` | 30 |
| TDOBLI | ClassObelisk (OBLI) | `tiberiandawn/bdata.cpp:458` | 35 |
| TDGUN | ClassTurret (GUN) | `tiberiandawn/bdata.cpp:517` | 26 |
| TDSAM | ClassSAM (SAM) | `tiberiandawn/bdata.cpp:824` | 40 |
| TDFACT | ClassConst (FACT) | `tiberiandawn/bdata.cpp:568` | 70 |

*(The TD Risk/Reward values are the engine-baked priorities Westwood tuned for TD's AI.
Reusing them here keeps the AI's relative-target preference TD-faithful, which is
preferable to using the RA donor's RA-tuned values — e.g., TD's superweapon EYE = 100
beats anything except a maxed factory, matching TD player intuition.)*

The TDHQ value (20) is the one notable downgrade from the RA donor (DOME = 30). Watch
for HQ being de-prioritised in skirmish; bump to 30 if it becomes a problem.

---

## Recommended fix

Two viable approaches. Pick one; document the choice in the catalogue.

### Option A — INI field per building (lowest-risk, most explicit)

For each TD entry, add `Points=N` to its rules.ini section. Use the donor's value as a
floor (see table above). The next session's `scripts/add_building.py` should make this
mandatory — the manifest table already has cost/power columns; add Points there too.

**Pro:** zero engine change; matches vanilla pattern; per-building tunable.
**Con:** easy to forget when adding manually; every new entry needs verification.

### Option B — Extend Logic= to copy Risk/Reward/Points from donor

In `redalert/bdata.cpp` Logic= block (after line 3758, before the closing `}`):

```cpp
// Threat scoring — Risk/Reward/Points feed TechnoClass::Value() and
// the AI's Evaluate_Object value gate (techno.cpp:1870). Without these,
// any Logic-aliased entry without an explicit Points= line scores 0 and
// is invisible to generic THREAT_BUILDINGS / THREAT_NORMAL scans.
// rules.ini Points= still overrides via TechnoTypeClass::Read_INI.
Risk = donor->Risk;
Reward = donor->Reward;
Points = donor->Points;
```

Critical: this assignment must happen **before** `TechnoTypeClass::Read_INI` runs, which
means it has to happen inside `BuildingTypeClass::Read_INI` **before** the parent
`TechnoTypeClass::Read_INI` already ran (it didn't — `BuildingTypeClass::Read_INI` calls
`TechnoTypeClass::Read_INI` first at `bdata.cpp:3709`, then does its own work). So the
fields here would be overwriting whatever TechnoTypeClass::Read_INI just loaded.
Order:

1. `TechnoTypeClass::Read_INI` → reads `Points=` (default `Points`, which is 0 for mod
   entries since the ctor sets it to 0). For mod entries without `Points=`, leaves 0.
2. `BuildingTypeClass::Read_INI` Logic= block runs → would overwrite with donor's values.
3. Later edits to `Points=` in rules.ini would no longer apply unless we re-read after
   the alias. **This is the trap.**

Cleaner version: in step 2, only copy donor's values **if rules.ini didn't set Points
explicitly**. Sentinel approach:

```cpp
// Run Logic= aliasing first (Step 2 above) using a sentinel,
// then in TechnoTypeClass::Read_INI use the sentinel as default.
```

Or simpler: do it in the Logic= block, but read `Points` from INI first; only fall
back to donor if INI was silent:

```cpp
if (Risk == 0 && Reward == 0 && Points == 0) {
    Risk = donor->Risk;
    Reward = donor->Reward;
    Points = donor->Points;
}
```

**Pro:** new TD entries "just work" out of the box.
**Con:** silent inheritance — easier to miss tuning intent; engine change adds another
property to the Logic= surface area.

### Recommendation

**Start with Option A.** It's the smallest change, keeps tuning explicit, and the
catalogue master table already lists Points alongside the other tunables. Revisit Option
B if we end up with 20+ buildings and per-entry duplication starts to feel like noise.

---

## Verification plan

Once `Points=40` is added to `[TDNUKE]`:

1. **Build the DLL** (`cmake --workflow --preset remaster`).
2. **Deploy to Deck** via the standard scp.
3. **In-game test:** start a skirmish vs a Brutal AI. Place TDNUKE in the player's base
   isolated from other structures. Watch whether enemy units engage it during their
   first attack wave.
4. **Quantitative check:** compare time-to-target between a vanilla POWR and TDNUKE
   placed side-by-side. Should be comparable.
5. **Edge case:** test with the building completely surrounded by other buildings to
   confirm the value gate (not just proximity) was the bug.

If the AI still ignores TDNUKE after Points is set, the next suspects in priority order:
- `Ownable` / `Owner=GoodGuy,BadGuy` resolution — confirm the building is recognised as
  enemy-owned (search `Get_Owners` handling).
- `BaseNormal=yes` interaction — verify it doesn't accidentally tag the building as a
  protected base structure that AI treats specially.
- Distance scaling math at `techno.cpp:1873` — confirm not overflowing for unusual
  positions.

---

## How to use this doc for future buildings

When adding a TD building:

1. Look up the donor's `Points=` value in the vanilla rules.ini.
2. Add `Points=N` to the new TD entry — pick a value equal to or slightly higher than
   the donor's, depending on tactical priority.
3. Verify in-game that the AI targets it.
4. If a building uniquely needs to be HIGHER priority (e.g., superweapon host), set
   Points well above its donor.

This is **the canonical place** to look when an AI targeting bug recurs. Update the
"Affected buildings" table as the catalogue grows.
