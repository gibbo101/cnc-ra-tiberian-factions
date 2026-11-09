# TDNUKE, TDNUK2, TDPYLE and TDSILO: power plants, barracks and silo

**Status:** Reference; shipped before 1.0.0. TDNUKE, TDNUK2, TDPYLE and TDSILO are separated `STRUCT_TD*` types
with TD's stats, TDPYLE's infantry exit, TD crews, and TDSILO's Tiberium fill.
**Open:** TDPYLE's exit point is RA's tent's `XYP_COORD(24, 47)`, not TD's `(30, 33)`; `Find_Exit_Cell` walks the
infantry out either way.

Live stats are in `rules.ini` and `balance-deep-dive.md`. TD entities run TD's own building code, ported from
`reference/vanilla-conquer/tiberiandawn/`, never RA's nearest equivalent (`td-port-playbook.md`). The silo's fill,
the barracks' exit, the crews and TD's strength doubling are in the field manual's
[Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#silos-barracks-and-the-rest),
Silos, barracks and the rest, and Read TD's constructor and TD's per-type code.

The other separated TD buildings (TDHQ, TDPROC, TDFIX, TDWEAP, TDHPAD, TDEYE, TDFACT) follow
`td-building-separation-recipe.md`.

---

## TD's source

| Building | TD class | `bdata.cpp` | Key fields |
|---|---|---|---|
| Power Plant (NUKE) | `ClassPower` | 892 | Strength 200, Sight 2, Cost 300, Power 100, Drain 0, wood, `BSIZE_22`, crew, simple damage |
| Advanced Power (NUK2) | `ClassAdvancedPower` | 944 | Strength 300, Sight 2, Cost 700, Power 200, Drain 0, wood, `BSIZE_22`, crew, simple damage, needs `STRUCTF_POWER` |
| Barracks (PYLE) | `ClassBarracks` | 1098 | Strength 400, Sight 3, Cost 300, Drain 20, wood, `BSIZE_22`, crew, factory for `RTTI_INFANTRYTYPE`, needs `STRUCTF_POWER`, `HOUSEF_GOOD` only, exit point `XYP_COORD(30, 33)` |
| Silo (SILO) | `ClassStorage` | 637 | Strength 150, Sight 2, Cost 150, Capacity 1500, Drain 10, wood, `BSIZE_21`, no crew, simple damage, needs `STRUCTF_REFINERY` |

The strengths are as listed; TD's constructor doubles them in play.

TD's `_anims[]` (`bdata.cpp:3786-3816`):

```cpp
{STRUCT_ADVANCED_POWER, BSTATE_IDLE, 0, 4, 15},
{STRUCT_BARRACKS,       BSTATE_ACTIVE, 0, 10, 3},
{STRUCT_BARRACKS,       BSTATE_IDLE,   0, 10, 3},
{STRUCT_POWER,          BSTATE_IDLE,   0, 4, 15},
// STRUCT_STORAGE has no entry: the default (0, 1, 0)
```

TD's `STRUCT_BARRACKS` sites:

| TD line | Site | What |
|---|---|---|
| `building.cpp:1882` | constructor | `ActLike` forced to `HOUSE_GOOD` when the owner isn't GDI |
| `building.cpp:2288-2289` | `Exit_Object`, `case STRUCT_BARRACKS: case STRUCT_HAND:` | `Find_Exit_Cell`, then `Coord_Add(Coord, ExitPoint)` |
| `building.cpp:3807` | `Sort_Y` | the barracks sorts by its centre |
| `bdata.cpp:4284-4293` | `Occupy_List` | with `Special.IsRoad`, the barracks always counts a bib (`SMUDGE_BIB3`) for placement |

The power plants have no per-type code beyond the building lifecycle. The silo's fill is TD's `Shape_Number`
(`building.cpp:594`).

---

## What TF ships

### Constructors and animations

`ClassTdNuke`, `ClassTdNuk2`, `ClassTdPyle` and `ClassTdSilo` (`redalert/bdata.cpp:679`, `708`, `737`, `766`) match
TD's on regulation, simple damage, no turret, `DIR_N`, size (`BSIZE_22` for both power plants, not APWR's 3x3;
`BSIZE_21` on `StoreList` for the silo) and `Produces=RTTI_INFANTRYTYPE` with `ExitPyle` for the barracks. Their
`_anims` entries are TD's (`bdata.cpp:5386-5389`); the silo has none. The frame counts: `TDNUKE.ZIP` 9, `TDNUK2.ZIP`
9, `TDPYLE.ZIP` 21, `TDSILO.ZIP` 11.

### `rules.ini`

Each section lists TD's values: strength, sight, cost, power or drain, armour, crew, bib, storage, and
`Capturable=true` on all four. TD prerequisites
map to TF's types (`STRUCTF_POWER` → `TDNUKE`, `STRUCTF_REFINERY` → `TDPROC`); TDPYLE is `Owner=GoodGuy`.

`BuildingTypeClass::Read_INI` (`bdata.cpp:6262-6267`) transforms every building whose INI name starts `TD`:

- **Strength doubled,** as TD's constructor does, so `rules.ini` holds TD's listed numbers: the silo's 150 plays
  as TD's 300 (playbook §3.21).
- **Sight plus 3,** because TD's sight ranges read short at RA's scale: a power plant listed at 2 sees 5, the
  barracks 6. Balance sight there, not per building.

### TDPYLE

- **The exit:** `case STRUCT_TDPYLE:` in `Exit_Object` (`building.cpp:3596`), beside RA's barracks, tent and
  kennel and TF's TDHAND and TSPILE, as TD's `case STRUCT_BARRACKS: case STRUCT_HAND:`.
- **The crew:** `BuildingClass::Crew_Type` (`building.cpp:8033`) gives any TD building TD's rifleman, `INFANTRY_TDE1`,
  through `TF_Side_Rifleman` (`techno.cpp:5881`; TS buildings get `INFANTRY_TSE1`), so a TD barracks never leaves
  RA's rifleman or a civilian.

### TDSILO

`Shape_Number` runs RA's silo branch for `STRUCT_STORAGE || STRUCT_TDSILO` (`building.cpp:1303`): the fill as five
levels, plus 5 below half health, over `TDSILO.ZIP`'s 11 frames (five fill levels, five damaged, one spare). Two buildings with identical
behaviour share one branch (the shared-branch rule in `td-sam-deep-dive.md`).

### Construction sound

`BuildingClass::Mission_Construction` (`building.cpp:5780-5788`) plays the build-up sound only for a human owner's
building. It is keyed on the type's era: `Is_TS_Era()` first, so TS buildings rise in silence; then
`Is_Tiberian_Era()` (`bdata.cpp:5035`: the TD run, the TS tree block, `STRUCT_TSTICK` and the non-RA gates) gives
`VOC_TD_CONSTRUCTION`; every other building plays RA's `VOC_CONSTRUCTION`.

---

## Checks after a change

1. A power plant reveals five cells (TD's 2 plus 3).
2. A TDPYLE's infantry walk out through `Find_Exit_Cell`; sold, it leaves a GDI minigunner.
3. With TDPROC filling, the silo steps through frames 0 to 4; below half health with full storage it shows 9.
4. The silo has 300 strength in play.
