# TDNUKE / TDNUK2 / TDPYLE / TDSILO — TD-source verification

> **RESOLVED — separated + shipped (v0.50).** All four are fully separated `STRUCT_TD*` types; the rules.ini stat fixes, the two TDPYLE engine dispatches, and the TDSILO tiberium-fill render branch all landed. The body below is retained as TD-source reference / the plan that was executed.

**Status:** All four M2 Tier 1 separated buildings (commit a8217c9) are mostly TD-authentic. Building class flags and constructor args match TD field-for-field. The deltas are in **rules.ini values** (4 sight/strength stat divergences) and **two missing STRUCT_TDPYLE engine dispatches** that affect infantry production/death. TDSILO has a third issue: missing tiberium-fill render branch.

**Session that produced it:** 2026-05-22, completion of the M2/M3 verification pass paired with `td-sam-deep-dive.md`, `td-atwr-deep-dive.md`, `td-gtwr-gun-verification.md`, `td-obli-verification.md`.

**Guiding principle:** wholesale port of TD source. No donor framing. Per [[feedback-no-donor-for-td-separation]] / [[project-building-separation-committed]].

---

## TD source values (verified)

| Building | TD Class | TD source (`bdata.cpp:`) | Key fields |
|---|---|---|---|
| Power Plant (NUKE) | `ClassPower` | 892 | Strength=200, Sight=2, Cost=300, Power=100, Drain=0, Armor=WOOD, BSIZE_22, IsCrew=true, IsSimpleDamage=true |
| Advanced Power (NUK2) | `ClassAdvancedPower` | 944 | Strength=300, Sight=2, Cost=700, Power=200, Drain=0, Armor=WOOD, BSIZE_22, IsCrew=true, IsSimpleDamage=true, Prerequisite=STRUCTF_POWER |
| Barracks (PYLE) | `ClassBarracks` | 1098 | Strength=400, Sight=3, Cost=300, Power=0, Drain=20, Armor=WOOD, BSIZE_22, IsCrew=true, IsSimpleDamage=false, IsFactory=true, Produces=RTTI_INFANTRYTYPE, Prerequisite=STRUCTF_POWER, **HOUSEF_GOOD-only** |
| Silo (SILO) | `ClassStorage` | 637 | Strength=**150**, Sight=2, Cost=150, Capacity=1500, Drain=10, Armor=WOOD, BSIZE_21, **IsCrew=false**, IsSimpleDamage=true, Prerequisite=STRUCTF_REFINERY |

TD `_anims[]` table entries (TD `bdata.cpp:3786-3816`):

```cpp
{STRUCT_ADVANCED_POWER, BSTATE_IDLE, 0, 4, 15},
{STRUCT_BARRACKS,       BSTATE_ACTIVE, 0, 10, 3},
{STRUCT_BARRACKS,       BSTATE_IDLE,   0, 10, 3},
{STRUCT_POWER,          BSTATE_IDLE,   0, 4, 15},
// STRUCT_STORAGE — NOT in _anims, uses default (0, 1, 0)
```

TD `STRUCT_STORAGE` render path (TD `building.cpp:594` — in Shape_Number, non-turret branch):

```cpp
if (*this == STRUCT_STORAGE) {
    int level = 0;
    if (House->Capacity) {
        level = (House->Tiberium * 5) / House->Capacity;
    }
    shapenum += Bound(level, 0, 4);    // 5 fill levels (0-4)
    if (Health_Ratio() < 0x0080) {
        shapenum += 5;                  // damaged variants at frames 5-9
    }
}
```

TD `STRUCT_BARRACKS` engine dispatch sites:

| TD line | Site | What |
|---|---|---|
| 1882 | Constructor `ActLike` reassignment | Force-houses `STRUCT_BARRACKS` to act like `HOUSE_GOOD` if owner isn't GDI |
| 2288-2289 | `Exit_Object` switch `case STRUCT_BARRACKS: case STRUCT_HAND:` | Find_Exit_Cell + dir + Coord_Add(Coord, ExitPoint) for infantry exit |
| 3807 | Place-on-road check | `if (*this == STRUCT_BARRACKS)` allows road placement |

`STRUCT_POWER` and `STRUCT_ADVANCED_POWER` have no special dispatch in TD beyond the standard building lifecycle.

---

## Diff against current state — TDNUKE

### `ClassTdNuke` (`redalert/bdata.cpp:579`)

| Field | Our | TD | Status |
|---|---|---|---|
| IniName | `TDNUKE` | `NUKE` (TD-prefix per convention) | match-by-convention |
| IsRegulated | `true` | `true` | match |
| IsSimpleDamage | `true` | `true` | match |
| IsTurretEquipped | `false` | `false` | match |
| Initial facing | `DIR_N` | `DIR_N` | match |
| Size | `BSIZE_22` | `BSIZE_22` | match |
| `_anims` entry | `{TDNUKE, BSTATE_IDLE, 0, 4, 15}` (our bdata.cpp:3404) | `{POWER, BSTATE_IDLE, 0, 4, 15}` | match |

### `[TDNUKE]` rules.ini (line 3208)

| Field | Our | TD | Status |
|---|---|---|---|
| Strength | 200 | 200 | match |
| **Sight** | **5** | **2** | ⚠ DIVERGES (player sees 2.5× further than TD) |
| Cost | 300 | 300 | match |
| Power | +100 | +100 | match |
| Power drain | 0 | 0 | match (no `Drain=` field needed) |
| Armor | wood | wood | match |
| Capturable | true | true | match |
| Crewed | true | true | match |
| Bib | yes | true | match |

---

## Diff against current state — TDNUK2

### `ClassTdNuk2` (`redalert/bdata.cpp:608`)

Constructor args identical pattern to TDNUKE. All TD-authentic.

Comment at our `bdata.cpp:631`: `BSIZE_22 // TD-authentic: 2x2 (not APWR's 3x3)` — good note, TD-correct.

`_anims` entry: `{TDNUK2, BSTATE_IDLE, 0, 4, 15}` (our bdata.cpp:3405). Matches TD's `{ADVANCED_POWER, BSTATE_IDLE, 0, 4, 15}`.

### `[TDNUK2]` rules.ini (line 3237)

| Field | Our | TD | Status |
|---|---|---|---|
| Strength | 300 | 300 | match |
| **Sight** | **5** | **2** | ⚠ DIVERGES (same as TDNUKE) |
| Cost | 700 | 700 | match |
| Power | +200 | +200 | match |
| Power drain | 0 | 0 | match |
| Armor | wood | wood | match |
| Prerequisite | TDNUKE | STRUCTF_POWER | match-by-mapping |

---

## Diff against current state — TDPYLE

### `ClassTdPyle` (`redalert/bdata.cpp:637`)

| Field | Our | TD | Status |
|---|---|---|---|
| Exit point | `XYP_COORD(24, 47)` | `XYP_COORD(30, 33)` | ⚠ DIVERGES — TD-authentic infantry-exit spawn position is `(30, 33)` |
| IsRegulated | `true` | `true` | match |
| IsSimpleDamage | `false` | `false` | match |
| IsTurretEquipped | `false` | `false` | match |
| Produces | `RTTI_INFANTRYTYPE` | `RTTI_INFANTRYTYPE` | match |
| Initial facing | `DIR_N` | `DIR_N` | match |
| Size | `BSIZE_22` | `BSIZE_22` | match |
| ExitList | `ExitPyle` | `ExitPyle` | match (same global symbol) |
| `_anims` BSTATE_ACTIVE | `{TDPYLE, 0, 10, 3}` | `{BARRACKS, 0, 10, 3}` | match |
| `_anims` BSTATE_IDLE | `{TDPYLE, 0, 10, 3}` | `{BARRACKS, 0, 10, 3}` | match |

Note: our comment at line 641 says "Match TENT" — TENT is RA's Allied Soviet barracks at `(24, 47)`. TD's PYLE has `(30, 33)`. Either we deliberately matched TENT (and accept the offset is RA-ish) or we should fix to TD-authentic. Minor cosmetic — the exit-cell mechanism handles the actual exit pathfinding once the infantry unlimbos.

### `[TDPYLE]` rules.ini (line 3267)

| Field | Our | TD | Status |
|---|---|---|---|
| Strength | 400 | 400 | match |
| **Sight** | **4** | **3** | ⚠ DIVERGES (player sees ~1.3× further than TD) |
| Cost | 300 | 300 | match |
| Power drain | -20 | Drain=20 | match |
| Armor | wood | wood | match |
| Owner | GoodGuy | HOUSEF_GOOD | match |
| Prerequisite | TDNUKE | STRUCTF_POWER | match-by-mapping |
| Crewed | true | true | match |
| Bib | yes | true | match |

### Missing engine dispatch for STRUCT_TDPYLE

**1. `Exit_Object` switch (`redalert/building.cpp:2297-2299`)**

```cpp
case STRUCT_BARRACKS:
case STRUCT_TENT:
case STRUCT_KENNEL:
    cell = Find_Exit_Cell(base);
    ...
```

`STRUCT_TDPYLE` is not in this list. Infantry produced by TDPYLE may unlimbo at `Exit_Coord()` but won't go through `Find_Exit_Cell` — they may spawn inside the footprint or fail to walk out cleanly. TD aliases `STRUCT_BARRACKS || STRUCT_HAND` at this site (TD `building.cpp:2288-2289`). Our port should add `STRUCT_TDPYLE`:

```cpp
case STRUCT_BARRACKS:
case STRUCT_TENT:
case STRUCT_KENNEL:
case STRUCT_TDPYLE:     // ← add
    cell = Find_Exit_Cell(base);
    ...
```

**2. `Crew_Type` switch (`redalert/building.cpp:5423-5425`)**

```cpp
case STRUCT_TENT:
case STRUCT_BARRACKS:
    return (INFANTRY_E1);
```

Returns the basic GDI rifleman as the infantry that spawns when the barracks is sold or destroyed. `STRUCT_TDPYLE` not in case — currently falls through to `default: break;` which leaves the return at `TechnoClass::Crew_Type()` (probably INFANTRY_NONE or a random one).

With `[TDPYLE] Crewed=true`, the building tries to spawn a crew infantry on death, but `Crew_Type()` returns nothing meaningful. Need to add:

```cpp
case STRUCT_TENT:
case STRUCT_BARRACKS:
case STRUCT_TDPYLE:     // ← add
    return (INFANTRY_E1);
```

(Or per separation principle, return `INFANTRY_E1` in a dedicated STRUCT_TDPYLE branch. The alias-with-vanilla is acceptable here because the behavior — return E1 — is identical across all three buildings. Same pattern as the negative-exclusion aliases in `td-sam-deep-dive.md` M6.)

---

## Diff against current state — TDSILO

### `ClassTdSilo` (`redalert/bdata.cpp:666`)

| Field | Our | TD | Status |
|---|---|---|---|
| IsRegulated | `false` | `false` | match |
| IsBibbed | (via rules.ini Bib=yes) | `true` | match |
| IsSimpleDamage | `true` | `true` | match |
| IsTurretEquipped | `false` | `false` | match |
| Initial facing | `DIR_N` | `DIR_N` | match |
| Size | `BSIZE_21` | `BSIZE_21` | match |
| OccupyList | `StoreList` | `StoreList` | match |
| `_anims` entry | not registered | not in TD `_anims[]` | match (both use default) |

### `[TDSILO]` rules.ini (line 3353)

| Field | Our | TD | Status |
|---|---|---|---|
| **Strength** | **300** | **150** | ⚠ DIVERGES (our silo is 2× tougher than TD's) |
| Sight | 2 | 2 | match |
| Cost | 150 | 150 | match |
| Storage | 1500 | 1500 | match |
| Power drain | -10 | Drain=10 | match |
| Armor | wood | wood | match |
| Crewed | false | false | match |
| Prerequisite | TDPROC | STRUCTF_REFINERY | match-by-mapping |

### Missing engine dispatch — tiberium fill-level rendering

**`Shape_Number` STRUCT_STORAGE branch (`redalert/building.cpp:712`)**

TD's STRUCT_STORAGE silo renders different frames based on how full the player's overall tiberium storage is — 5 fill levels (0-4) with 5 damaged variants (5-9). Our `Shape_Number`:

```cpp
if (*this == STRUCT_STORAGE) {
    int level = 0;
    if (House->Capacity) {
        level = (House->Tiberium * 5) / House->Capacity;
    }
    shapenum += Bound(level, 0, 4);
    if (Health_Ratio() <= Rule.ConditionYellow) {
        shapenum += 5;
    }
}
```

`STRUCT_TDSILO` doesn't hit this branch. **TDSILO.ZIP has 11 frames** (`tdsilo-0000.tga` through `tdsilo-0010.tga`) — exactly the layout the fill-render logic expects (5 healthy fill levels + 5 damaged + 1 spare). Currently TDSILO renders frame 0 only.

Fix — extend the dispatch:

```cpp
if (*this == STRUCT_STORAGE || *this == STRUCT_TDSILO) {
    int level = 0;
    if (House->Capacity) {
        level = (House->Tiberium * 5) / House->Capacity;
    }
    shapenum += Bound(level, 0, 4);
    if (Health_Ratio() <= Rule.ConditionYellow) {
        shapenum += 5;
    }
}
```

This is a positive-dispatch alias of two buildings with **identical** behavior (both are Tiberium silos with the same fill-render contract). The alias is legitimate per the `td-sam-deep-dive.md` M6 rule: "identical behavior across two TD entities can share a comment-tagged branch" — and here both TD and RA conceive of silos identically, so it's even more justified. Tag with a comment pointing at this doc.

---

## Symptoms → root cause map

| Symptom | Building | Root cause | Fix |
|---|---|---|---|
| Power Plant has unnaturally large sight radius (~5 cells) | TDNUKE, TDNUK2 | rules.ini Sight=5 vs TD's 2 | rules.ini |
| Barracks has 1 cell more sight than TD | TDPYLE | rules.ini Sight=4 vs TD's 3 | rules.ini |
| Silo takes 2× longer to destroy than TD-authentic | TDSILO | rules.ini Strength=300 vs TD's 150 | rules.ini |
| Silo always renders empty (frame 0) regardless of player's tiberium fill | TDSILO | Shape_Number STRUCT_STORAGE branch doesn't include STRUCT_TDSILO | engine |
| Barracks-produced infantry may spawn inside footprint / fail to exit cleanly | TDPYLE | Exit_Object switch missing STRUCT_TDPYLE case | engine |
| Barracks on-death doesn't spawn a crew infantry | TDPYLE | Crew_Type switch missing STRUCT_TDPYLE (Crewed=true but Crew_Type returns NONE) | engine |

---

## Port plan

### Rules.ini stat corrections (4 lines total)

```ini
[TDNUKE]
Sight=2          ; was 5 — TD POWER Sight=2

[TDNUK2]
Sight=2          ; was 5 — TD ADVANCED_POWER Sight=2

[TDPYLE]
Sight=3          ; was 4 — TD BARRACKS Sight=3

[TDSILO]
Strength=150     ; was 300 — TD STORAGE Strength=150
```

Pure data. Smallest possible diff. **TDSILO Strength=150 is balance-affecting** — silos become twice as fragile, which means a single shot from a heavy tank can kill them. This is TD-authentic but plays differently than current. Worth a playtest.

### Engine fixes — STRUCT_TDPYLE production (`redalert/building.cpp`)

**E1 — `Exit_Object` switch at line 2297-2299:**

Add `case STRUCT_TDPYLE:` alongside the existing STRUCT_BARRACKS / STRUCT_TENT / STRUCT_KENNEL cases. Identical body. Comment: `// TDPYLE shares the BARRACKS exit-cell pattern (TD building.cpp:2288 aliases STRUCT_BARRACKS || STRUCT_HAND; our port aliases STRUCT_TDPYLE here). See docs/td-tier1-verification.md.`

**E2 — `Crew_Type` switch at line 5423-5425:**

Add `case STRUCT_TDPYLE:` returning `INFANTRY_E1`. Same alias-with-comment pattern.

### Engine fix — STRUCT_TDSILO tiberium fill render (`redalert/building.cpp:712`)

**E3 — Extend Shape_Number STRUCT_STORAGE branch:**

```cpp
// TDSILO shares STRUCT_STORAGE's tiberium-fill render contract
// (TD building.cpp:594). TDSILO.ZIP has the same 5-level + damaged
// frame layout. See docs/td-tier1-verification.md.
if (*this == STRUCT_STORAGE || *this == STRUCT_TDSILO) {
    ...
}
```

### Manifest sync (`scripts/buildings_manifest.py`)

Update the four dict `"notes"` fields to reference this doc. No structural changes.

---

## What's already right (don't touch)

- All four `Class<Td>` constructor args for flags, sizes, foundation lists, and `Produces=` — TD-authentic field-for-field
- All four `_anims[]` entries — match TD's `OBELISK_ANIMATION_RATE`-style values exactly (rate=15 for power plants, rate=3 for barracks active/idle)
- TDNUKE/TDNUK2 Power, Cost, Drain, Armor, Strength values
- TDPYLE Strength, Cost, Drain, Armor, Owner, Prerequisite values
- TDSILO Storage(=Capacity), Cost, Sight, Drain, Armor, Crewed=false values
- All four asset bundles: TDNUKE.ZIP (9 frames), TDNUK2.ZIP (9 frames), TDPYLE.ZIP (21 frames), TDSILO.ZIP (11 frames) — counts match TD's expected frame layouts
- `STRUCT_TDxxxx` enum and heap registration
- `MISSION_CONSTRUCTION` plays `VOC_TD_CONSTRUCTION` (covered by the range check at building.cpp:3948)

---

## Acceptance criteria

**Rules.ini (5 min):**
- [ ] `[TDNUKE] Sight=2`, `[TDNUK2] Sight=2`, `[TDPYLE] Sight=3`, `[TDSILO] Strength=150`

**Engine (15 min):**
- [ ] `STRUCT_TDPYLE` added to `Exit_Object` switch at building.cpp:2297
- [ ] `STRUCT_TDPYLE` added to `Crew_Type` switch at building.cpp:5423
- [ ] `STRUCT_TDSILO` added to `Shape_Number` STRUCT_STORAGE branch at building.cpp:712

**Smoke tests:**
- [ ] Sell a Power Plant → mini-map fog re-grows to TD's 2-cell sight ring (not 5)
- [ ] Build a TDPYLE, train an infantry → infantry walks out via Find_Exit_Cell properly
- [ ] Sell a TDPYLE → INFANTRY_E1 (GDI minigunner) emerges
- [ ] Fill TDPROC, watch TDSILO frame progression: 0 (empty) → 1 → 2 → 3 → 4 (full)
- [ ] Damage TDSILO below 50% with a full storage → renders frame 4+5 = 9 (damaged full)
- [ ] TDSILO at 150 HP dies to one 75mm hit — verify the balance feels TD-correct or revert to 300

---

## Decisions

- **No donor.** All TD-source-grounded. The aliased dispatches (STRUCT_TDPYLE with STRUCT_BARRACKS; STRUCT_TDSILO with STRUCT_STORAGE) are *identical-behavior positive-dispatch aliases* between TD and RA buildings that conceive of barracks/silo the same way. This is the legitimate aliasing pattern per [[project-building-separation-committed]] / `td-sam-deep-dive.md` M6 — not "modeling on" RA.
- **TDSILO Strength=150 is the only balance-affecting change.** TD-authentic value. If playtest reveals silos die too easily, balance via warhead Verses table or armor type, never by reverting to a non-TD strength.
- **Sight value corrections are pure data.** No code change, no risk to other buildings.
- **TDPYLE exit-point `XYP_COORD(24, 47)` left alone for now.** TD uses `(30, 33)`. Difference is cosmetic in practice — Find_Exit_Cell handles the actual cell pathfinding. Worth fixing for full TD parity, but lower priority than the engine dispatch gaps.

---

## Cargo order

**Smallest (data only):** 4-line rules.ini diff. Pure stat correction. Smoke-test the sight changes feel right.

**Medium (TDPYLE engine):** E1 + E2 added in `building.cpp`. ~10-line engine diff. Fixes infantry-production and crew-on-death paths.

**Optional (TDSILO render):** E3 added in `building.cpp`. ~4-line engine diff. Cosmetic but TD-iconic — the empty-vs-full silo visual feedback is part of TD's economy UX.

All three independent — any order.

---

## Cross-reference

- TDSAM: `td-sam-deep-dive.md`
- TDATWR: `td-atwr-deep-dive.md`
- TDGTWR + TDGUN: `td-gtwr-gun-verification.md`
- TDOBLI: `td-obli-verification.md`

This doc closes the verification pass over all **9 fully-separated** STRUCT_TDxxxx buildings. The remaining 7 Logic=-aliased entries (TDHQ, TDPROC, TDFIX, TDWEAP, TDHPAD, TDEYE, TDFACT) are *known not separated* per [[project-building-separation-committed]] — verifying them produces redundant findings until they're individually separated through the M3-M5 plan.
