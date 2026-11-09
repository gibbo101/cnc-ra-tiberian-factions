# TDATWR: the Advanced Guard Tower

**Status:** Reference; shipped before 1.0.0. TDATWR runs its own `ClassTdAtwr` path and binds
`Primary=TDTowTwo`, a wholesale port of TD's `STRUCT_ATOWER`.
**Open:** TD's `TechnoClass::Fire_At` and `BuildingClass::Mission_Attack` have not been diffed against TF's for
this tower.

Live stats are in `rules.ini` and `balance-deep-dive.md`. TD entities run TD's own building, weapon and projectile
code, ported from `reference/vanilla-conquer/tiberiandawn/`, never RA's nearest equivalent (`td-port-playbook.md`).

---

## What TD's ATOWER is

A 1×2 GDI defensive tower with a *fixed* missile rack on top. The rack does not rotate: the launched missiles
(`BULLET_SSM`, the "DRAGON" sprite) do the tracking after launch. It holds fire below full power, and has a
crew. There is no state machine and no special render path.

### TD source: `bdata.cpp:372-422`

```cpp
static BuildingTypeClass const ClassATower(STRUCT_ATOWER,
    TXT_AGUARD_TOWER,
    "ATWR",
    XYP_COORD(0, 0),
    4,                       // Build level
    STRUCTF_RADAR,           // Prerequisite
    true,                    // IsCloakable (detects adjacent cloaked)
    false,                   // IsRegulated
    false,                   // IsBibbed
    false,                   // IsNominal
    false,                   // IsWall
    false,                   // IsFactory
    false,                   // IsCaptureable
    false,                   // IsFireCharged
    true,                    // IsSimpleDamage
    false,                   // IsInvisible
    true,                    // IsSelectable
    true,                    // IsLegalTarget
    false,                   // IsInsignificant
    false,                   // IsImmune
    false,                   // IsTheater
    false,                   // IsTurretEquipped
    true,                    // IsTwoShooter
    true,                    // IsRepairable
    true,                    // IsBuildable
    true,                    // IsCrew
    false,                   // (concrete placement)
    RTTI_NONE,
    DIR_N,                   // Initial facing
    300,                     // Strength
    4,                       // Sight
    1000,                    // Cost
    13, 100, 30,             // Scenario / risk / reward
    HOUSEF_MULTI* | HOUSEF_JP | HOUSEF_GOOD,  // Ownable
    WEAPON_TOW_TWO,          // Primary
    WEAPON_NONE,             // Secondary
    ARMOR_ALUMINUM,
    0, 0, 0, 20,             // CanEnter / Capacity / Power / Drain
    BSIZE_12,                // 1×2
    NULL,
    (short const*)List12,
    (short const*)OList12);
```

### TD's dispatch sites in `building.cpp`

| Line | Function | What it does |
|---|---|---|
| 2784-2785 | `Fire_Data` | Muzzle data: `coord = Coord_Move(coord, DIR_N, 0x0030); dist = 0x0040;` |
| 2815-2816 | `Fire_Coord` | Muzzle coord: up `0x30`, then, `if (Target_Legal(TarCom))`, `0x40` towards the target |
| 3522 | `Can_Fire` | `if (*this == STRUCT_ATOWER && House->Power_Fraction() < 1) return (FIRE_BUSY);` |
| 4132 | `Mission_Deconstruction` | Vanilla Conquer's TD only: a sold ATOWER's or OBELISK's crew one cell south, onto its footprint cell |

No `Mission_Attack`, `Shape_Number` or `AI` branch.

### `WEAPON_TOW_TWO` (`const.cpp:88`) and `BULLET_SSM` (`bbdata.cpp:153`)

```cpp
{BULLET_SSM, 60, 40, 0x0680, VOC_ROCKET2, ANIM_NONE},  // WEAPON_TOW_TWO: {Fires, Attack, ROF, Range, Sound, Anim}
```

Range `0x0680` is 6.5 cells. The field order is TD's `type.h:50-91`.

```cpp
static BulletTypeClass const ClassMissile(BULLET_SSM,
    "DRAGON",      // Image
    true,          // High (over walls)
    true,          // Homes
    false,         // Arcs
    false,         // Drops
    false,         // Invisible
    true,          // Proximity arm
    true,          // Animates flame
    true,          // Has fuel (can run out)
    false,         // No facing variation
    true,          // Inaccurate
    true,          // Translucent
    true,          // AA-capable
    7,             // Arming time
    0,             // Range override
    MPH_ROCKET,    // Speed
    5,             // ROT (turn rate)
    WARHEAD_HE,
    ANIM_FRAG1);   // Impact explosion
```

The tower takes TD's generic building `Fire_At` branch, not the SAM's: `VOC_ROCKET2` at `Coord` and
`ANIM_MUZZLE_FLASH` at `Fire_Coord`. See the field manual's
[Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#weapons-muzzle-flashes-and-offsets),
Weapons, muzzle flashes and offsets.

---

## What TF ships

### `ClassTdAtwr` (`redalert/bdata.cpp:828`)

Set from TD's `ClassATower`, with no RA donor: vertical offset `0x0030`, primary offset `0x0040`,
`IsSimpleDamage` true, `IsTurretEquipped` false, initial facing `DIR_N`, `BSIZE_12` on `List12`/`OList12`. Registered
at `bdata.cpp:5222`.

`IsTurretEquipped` must stay false: `TDATWR.ZIP` has three frames (healthy, damaged, a spare), mapped in TF's
`RA_STRUCTURES.XML` from line 24299. See the field
manual's [Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#the-flags-that-decide-the-frames),
The flags that decide the frames ("`IsTurretEquipped` means 32 facings"), which uses this tower as its example. TF
saw the tower frozen on one frame and slow to fire with the flag set. The flag also points the muzzle the wrong way:
for a turret building RA's `Turret_Facing` and `BuildingClass::Fire_Direction` (`building.cpp:7410`) both return
`PrimaryFacing.Current()`, not the direction to the target, so a tower whose facing never turns fires along a fixed
line. The two offsets are TD's `Fire_Coord` pair as
RA's vertical and primary offsets.

### `rules.ini`

`[TDATWR]` matches TD's `ClassATower`: `Strength=300` (doubled in code, `td-port-playbook.md` §3.21), `Cost=1000`,
`Power=-20`, `Sight=4`, `Armor=aluminum`, `Crewed=true`, `Prerequisite=TDHQ`, `TechLevel=4`, `Points=30`,
`Sensors=yes`. TD's power gate is data: `Powered=true` (see the field manual's
[Silos, barracks and the rest](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#silos-barracks-and-the-rest),
"Power"), so there is no `STRUCT_TDATWR` branch in `Can_Fire`. `TDATWRMAKE.ZIP` has 14 build-up frames
(`BuildupAnimCount=14`).

```ini
[TDTowTwo]
Damage=60          ; TD Attack
ROF=40             ; TD ROF
Range=6.5          ; TD Range 0x0680
Projectile=TDSSM
Speed=60           ; IsTDPort: TD's raw MPH_ROCKET, not RA's percentage
Warhead=TDAGT      ; the tower's own copy of TDHE, to tune apart
Report=ROCKET2     ; TD VOC_ROCKET2
Anim=GUNFIRE       ; ANIM_MUZZLE_FLASH, TD's Fire_At default for BULLET_SSM
Burst=2            ; TD's two-shooter
```

```ini
[TDSSM]
Arm=7
High=yes
Shadow=no
Proximity=yes
Animates=yes
Ranged=yes
AA=yes
AG=yes
Image=TDDRAGON
ROT=5
Rotates=yes
Inaccurate=no
Translucent=yes
Homing=yes
Warhead=TDHE
ImpactAnim=FRAG1
```

RA's projectile keys are in the field manual's
[Porting Tiberian Dawn units](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-units.md#projectiles-and-their-impacts),
Projectiles and their impacts. Where `[TDSSM]` departs from TD's `ClassMissile`:

| TD field | TD value | `[TDSSM]` | Why |
|---|---|---|---|
| Image | "DRAGON" | `Image=TDDRAGON` | RA's own `DRAGON` tile draws differently (below) |
| Homes | true | `Homing=yes` | TF's own key (`IsHoming`, `bbdata.cpp`), read by `AI_TD` |
| Inaccurate | true | `Inaccurate=no` | TF's choice (commit `c878c0248`): no scatter by type, as RA plays its missiles; it still scatters at infantry and cells (below) |
| AA-capable | true | `AA=yes`, `AG=yes` | TD also fires it at ground targets |
| Speed | `MPH_ROCKET` | the weapon's `Speed=60` | RA's projectiles have no speed key |
| Warhead | `WARHEAD_HE` | `Warhead=TDHE` (for `AI_TD`); the weapon's `TDAGT` | the weapon's warhead is tuned apart |

Every other field matches TD's.

`Speed=60` is read raw because `TDTowTwo` is flagged `IsTDPort` (`rules.cpp:793`); written as RA's percentage it
flew at 153 and overshot every target in its 7-frame arming window (playbook §3.1). `Burst=2` gives two missiles per
engagement, and `Rearm_Delay`'s TD-port branch gives TD's cadence (playbook §3.5 and §3.6).

### The TD-port projectile code

`[TDSSM]` is `BULLET_SSM`, flagged `IsTDPort` in `bbdata.cpp:212`, so it runs TD's own `BulletClass::Unlimbo` and
`BulletClass::AI` as `Unlimbo_TD` (`bullet.cpp:1556`) and `AI_TD` (`bullet.cpp:1652`), dispatched from the top of
RA's. `BulletTypeClass` carries the TD fields they read: `IsTDPort`, `IsHoming`, `ClassWarhead`, `ImpactAnim`,
`BulletRange`, parsed from `Homing=`, `Warhead=`, `ImpactAnim=` and `BulletRange=`. The symbol renames are the
playbook's §2.8.

From TD's `Unlimbo` (`tiberiandawn/bullet.cpp:631`): the scatter, and the clamp that pulls a scattered target
coordinate back inside the firer's weapon range. The scatter's test (`bullet.cpp:1574-1576`, TD's 656-658) is
`IsInaccurate || Class->IsInaccurate || ((Is_Target_Cell || Is_Target_Infantry) && (ClassWarhead == WARHEAD_AP ||
Class->IsFueled))`, so a fuelled shot scatters at infantry and cells whatever its `Inaccurate=`: `[TDSSM]` is
`Ranged=yes` and still lands up to `Distance/3` off (at most `0x0200`, the homing and arcing case) at infantry and
walls. In play its proximity hits landed 24 to 89 leptons from the target, inside the blast.

TF's `Unlimbo_TD` adds the RA-side plumbing TD's body lacks: `Height = 0` for a bullet that isn't `High=`, and
`Map.Remove` and `Map.Submit` around the set-up (`bullet.cpp:1561-1566`, `1641`), since RA's layers file a bullet by
`Height`. From
TD's `AI` (`tiberiandawn/bullet.cpp:293`): the explicit `IsHoming` test, the `ANIM_SMOKE_PUFF` trail (with no `FB1` special case, which RA's `AI` has), the AA
proximity bonus (TD's `BULLET_TOW` test reads `BULLET_SSM`), and the impact animation spawned from the bullet's own
`ImpactAnim`.

### Art

`TDDRAGON.ZIP` is TD's 32-frame `DRAGON.ZIP` from `TEXTURES_TD_SRGB.MEG`, repacked with `td`-prefixed TGAs
(`bundle_assets.py:repack_zip_with_prefix`) and registered as 32 shapes in TF's `RA_VFX.XML`. Under the stock name
it drew RA's art: see the field manual's
[HD tilesets and ZIPs](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/hd-tilesets-and-zips.md#traps),
Traps ("Don't reuse a stock tile name"). The bullet has no classic shape, so
`BulletTypeClass::One_Time` (`bbdata.cpp:267`) lends it `BULLET_HEAT_SEEKER`'s `ImageData`, as it does `TDLaser` and
`TDAPDS` (playbook §2.7).

### The crew

RA's sale path (`BuildingClass::Mission_Deconstruction`, `building.cpp:5927`) moves the survivor a cell south for
the Tesla Coil; TF adds `STRUCT_TDOBLI` and `STRUCT_TDATWR`, as all three are 1x2. Centre minus 12 pixels is the
middle of the upper, overlap-only cell (`CenterOffset[BSIZE_12]`, `building.cpp:201`), so the step south puts the
crew on the lower cell, the whole footprint (`List12`), not south of the building: so seen in play for all three. See the field manual's
[Silos, barracks and the rest](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#silos-barracks-and-the-rest),
"Where the crew appears". Two TD buildings sharing one branch for identical behaviour is allowed (the shared-branch
rule in `td-sam-deep-dive.md`).

### Sound

`VOC_TD_ROCKET2` (`audio.cpp:252`), routed by `RAC_SFX_ROCKET2`/`RAR_SFX_ROCKET2` in `SFXEVENTSNONLOCALIZED.XML` (from line 6072).

### The buildings manifest

`scripts/buildings_manifest.py`'s `TDATWR` entry feeds `add_building.py`, which emits `[TDATWR]`. It has drifted
from `rules.ini` (no `Sensors=yes`, no `Powered=true`): fix the manifest before re-emitting the block.

---

## Decisions

- **No donor.** `ClassTdAtwr`'s arguments come from TD's source, not from RA's AGUN or PBOX.
- **`[TDTowTwo]` is TD's weapon.** RA has no `[TowTwo]`, and its TOW-like weapons differ.
- **`[TDSSM]` is TD's projectile, not RA's `[AAMissile]`.** TD's `BULLET_SAM` is `MPH_VERY_FAST` with `ROT=10`;
  `BULLET_SSM` is `MPH_ROCKET` with `ROT=5`.

## Checks after a change

1. The rack doesn't turn, and fires within a tick of acquiring a target.
2. The missile leaves the rack tip, with `ROCKET2` and the `GUNFIRE` flash, homes, and hits a wall one cell away.
3. Below half strength the art shows frame 1.
4. With the house below full power it holds fire, and fires again once power is back.
5. Sold, its crew appears on the footprint's lower cell, not in the overlap cell above it.
6. Against aircraft, the missile tracks and bursts near them.
7. RA's AGUN, GUN and PBOX are unchanged.
