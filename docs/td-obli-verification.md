# TDOBLI: the Obelisk of Light

**Status:** Reference; shipped before 1.0.0. TDOBLI is fully separated and binds
`Primary=TDOblsLaser`, with TD's charge timing.
**Open:** the laser's origin: TF's vertical offset is `0x00C8` against TD's `0x00A8`, and TD's `0x0018` west shift
has no `Fire_Coord` case. Check the beam against the crystal tip in game before changing either.

Live stats are in `rules.ini` and `balance-deep-dive.md`. TD entities run TD's own building, weapon and projectile
code, ported from `reference/vanilla-conquer/tiberiandawn/`, never RA's nearest equivalent (`td-port-playbook.md`).

The game-level facts (TD's charge, the Tesla-only tests in RA's `Charging_AI`, `Shape_Number` and `Animation_AI`,
`Charges=yes` and the lightning, the beam as launcher lines, the muzzle offsets) are in the field manual's
[Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#the-obelisk-charge-then-a-laser),
The Obelisk: charge, then a laser.

---

## TD's source

### `STRUCT_OBELISK` (`tiberiandawn/bdata.cpp:424-473`)

```cpp
static BuildingTypeClass const ClassObelisk(STRUCT_OBELISK,
    /* ... */
    true,   // IsCloakable             (detects adjacent cloaked units)
    false,  // IsRegulated
    false,  // IsBibbed
    false,  // IsNominal
    false,  // IsWall
    false,  // IsFactory
    false,  // IsCaptureable
    false,  // IsFireCharged ("does it catch fire", not the charging flag)
    false,  // IsSimpleDamage
    false,  // IsInvisible
    true,   // IsSelectable
    true,   // IsLegalTarget
    false,  // IsInsignificant
    false,  // IsImmune
    false,  // IsTheater
    false,  // IsTurretEquipped        (fixed structure, no rotation)
    false,  // IsTwoShooter
    true,   // IsRepairable
    true,   // IsBuildable
    true,   // IsCrew
    false,  // (concrete placement)
    RTTI_NONE,
    DIR_N,                  // Initial facing
    200,                    // Strength
    5,                      // Sight
    1500,                   // Cost
    11, 100, 35,            // Scenario / risk / reward
    HOUSEF_MULTI* | HOUSEF_JP | HOUSEF_BAD,
    WEAPON_OBELISK_LASER,
    WEAPON_NONE,
    ARMOR_ALUMINUM,
    0, 0, 0, 150,           // CanEnter / Capacity / Power / Drain
    BSIZE_12,
    NULL,
    (short const*)List12,
    (short const*)OList12);
```

### Its dispatch sites in `building.cpp`

| Line | Function | What |
|---|---|---|
| 531-541 | `Shape_Number` | `IsCharged` → shape 3; `IsCharging` → `Fetch_Stage()`; else 0 |
| 852-857 | `Fire_At`, the `BULLET_LASER` case | clears `IsCharging` and `IsCharged` (the flags are TD `building.h:115-116`) |
| 909 | `AI` | excluded from the animation step: the charge drives its stage |
| 1066-1095 | `AI` (the charge) | powered and with a target: `Set_Stage(0); Set_Rate(OBELISK_ANIMATION_RATE)`, `VOC_LASER_POWER`; charged at `Fetch_Stage() >= 4` (line 1072); reset on losing the target or power |
| 2789-2792 | `Fire_Data` | `coord += DIR_N 0x00A8; coord += DIR_W 0x0018;` |
| 2822-2826 | `Fire_Coord` | the same offsets |
| 4132 | `Mission_Deconstruction` | Vanilla Conquer's TD only: a sold ATOWER's or OBELISK's crew one cell south, onto its footprint cell |

`OBELISK_ANIMATION_RATE` is 15 ticks a frame (TD `defines.h:323`), used by `Init_Anim` for `BSTATE_ACTIVE` and by
the charge's `Set_Rate`.

### The weapon, projectile, warhead and sounds

```cpp
{BULLET_LASER, 200, 90, 0x0780, VOC_LASER, ANIM_NONE},  // WEAPON_OBELISK_LASER (const.cpp:90)
```

200 damage, ROF 90, 7.5 cells, `VOC_LASER` (`OBELRAY1`), no animation: the beam is the visual.

```cpp
static BulletTypeClass const ClassLaser(BULLET_LASER,      // bbdata.cpp:329-349
    "Laser",         // Image
    true,            // High (over walls)
    false,           // Homes
    false,           // Arcs
    false,           // Drops
    true,            // Invisible
    false,           // Proximity arm
    false,           // Animates flame
    false,           // Has fuel
    true,            // No facing variation
    false,           // Inaccurate
    false,           // Translucent
    false,           // AA-capable
    0, 0,
    MPH_LIGHT_SPEED, // Speed
    0,               // ROT
    WARHEAD_LASER,
    ANIM_NONE);
```

`WARHEAD_LASER` (`const.cpp:125-129`) is spread 4, destroys no walls, wood or Tiberium, and does `0x100` (100%)
against every armour. The sounds (`audio.cpp:137-138`) are `OBELRAY1` (`VOC_LASER`, firing) and `OBELPOWR`
(`VOC_LASER_POWER`, charging).

---

## What TF ships

### The building

`ClassObelisk` (`redalert/bdata.cpp:2331`, registered at 5216) keeps TD's class name; every other separated TD
building is `ClassTd<Name>`. It matches TD's `ClassObelisk` on `IsSimpleDamage` (false), `IsTurretEquipped`
(false), `DIR_N`, `BSIZE_12` and `List12`, with vertical offset `0x00C8` and no primary offset (the open item
above). `Init_Anim` gives it TD's `{STRUCT_TDOBLI, BSTATE_ACTIVE, 0, 4, 15}` (`bdata.cpp:5385`).

`[TDOBLI]` holds TD's values: `Strength=200` (doubled in code, playbook §3.21), `Cost=1500`, `Power=-150`,
`Sight=5`, `Armor=aluminum`, `Crewed=true`, `Repairable=yes`, `Owner=BadGuy`, `TechLevel=4` (TD's build level 11
in RA's tree), `Prerequisite=TDHQ` (TD's `STRUCTF_RADAR`),
`Points=35`, `Sensors=yes`, `ActiveAnimCount=4`, `ActiveAnimRate=15`, and a 20-frame build-up at rate 2.

### The charge (`BuildingClass::Charging_AI`, `building.cpp:8820`)

RA's `Charging_AI`, made type-aware for TDOBLI: `Set_Rate(15)` and `VOC_TD_LASER_POWER`, where the Tesla Coil
keeps 3 and `VOC_TESLA_POWER_UP`. The charge completes at the ACTIVE animation's `Count` for TDOBLI (stage 4,
TD's `>= 4`, one past its last frame) and at `Count - 1` for every other charging building (stage 9 for the Tesla
Coil's 10 frames, as stock); a fixed stage 9 would run the Obelisk into its damaged frames.

| | `Set_Rate` | Charged at stage | Ticks | At 15 ticks a second |
|---|---|---|---|---|
| RA's Tesla Coil | 3 | 9 | 27 | about 1.8 s |
| TDOBLI on RA's rate, charged on its last frame | 3 | 3 | 9 | about 0.6 s |
| TD's Obelisk, and TF's TDOBLI | 15 | 4 | 60 | about 4 s |

The slow charge is what makes the Obelisk a defence that can be counter-attacked rather than an instant kill.

The other Tesla tests also name `STRUCT_TDOBLI`: the charge frame in `Shape_Number` (`building.cpp:1234`) and the
`Animation_AI` exclusion (`building.cpp:8973`). Sharing RA's Tesla machinery is an extension, not an alias: one
state machine of the same shape, guarded by type at each site.

### The beam

`Charges=yes` on `[TDOblsLaser]` sets `IsElectric`, which runs the charge and the bullet's logic at once.
`TechnoClass::Fire_At` (`techno.cpp:3915`) skips the Tesla's lightning for a `BULLET_LASER` and the beam is drawn as
lines through TF's port of TD's `DLL_Draw_Line_Intercept` (`dllinterface.cpp:6296`, drawn from `conquer.cpp:2810`).
How the launcher draws the lines is in `launcher-render-contracts.md`.

```ini
[TDOblsLaser]
Damage=200
ROF=90
Range=7.5
Projectile=TDLaser
Speed=255          ; MPH_LIGHT_SPEED
Warhead=TDLaser
Report=OBELRAY1    ; TD VOC_LASER
Charges=yes
```

`[TDLaser]` is both the projectile and the warhead: the bullet and warhead parsers read different keys from the one
section. Bullet keys: `Warhead=TDLaser` (a TD-port bullet detonates with its own, playbook §3.38), `Inviso=yes`, `High=yes`, `Shadow=no`, `AA=no`, `AG=yes`, `ROT=0`, `Rotates=no`, `Image=none`.
Warhead keys: `Spread=4`, `Wall=no`, `Wood=no`, `Ore=no`, `Verses=100%,100%,100%,100%,100%` and `Explosion=0`, all
TD's `WARHEAD_LASER`, and `InfDeath=5`, RA's death selector.

### Sounds and the crew

`VOC_TD_LASER` (`OBELRAY1`) and `VOC_TD_LASER_POWER` (`OBELPOWR`) are `audio.cpp:254-255`. A sold Obelisk's crew
steps a cell south, onto the footprint's lower cell, in RA's Tesla Coil branch of `Mission_Deconstruction` (`building.cpp:5927`, shared with
TDATWR: `td-atwr-deep-dive.md`).

---

## Checks after a change

1. TDOBLI takes about four seconds to charge and fires at stage 4; the Tesla Coil's charge is unchanged.
2. The beam leaves the crystal tip (the open item).
3. With the house below full power it doesn't charge.
4. Sold, its crew appears on the footprint's lower cell, not in the overlap cell above it.

Related: `td-sam-deep-dive.md`, `td-atwr-deep-dive.md`, `td-gtwr-gun-verification.md`.
