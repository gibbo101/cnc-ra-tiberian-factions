# TDGTWR and TDGUN: the Guard Tower and the Gun Turret

**Status:** Reference; shipped before 1.0.0. TDGTWR binds `Primary=TDChainGun` (TD's Damage 25, ROF 50); TDGUN
binds `Primary=TDTurretGun` on its own `[TDAPDS]` projectile.
**Open:** `[TDTurretGun]`'s `Speed=40` reads as 102; `Speed=39` (99) is the closest to TD's `MPH_VERY_FAST` (100).

Live stats are in `rules.ini` and `balance-deep-dive.md`. TD entities run TD's own building, weapon and projectile
code, ported from `reference/vanilla-conquer/tiberiandawn/`, never RA's nearest equivalent (`td-port-playbook.md`).
The muzzle offsets, the turret's frames and turn rate, and the flash by projectile are in the field manual's
[Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#weapons-muzzle-flashes-and-offsets),
Weapons, muzzle flashes and offsets, and The flags that decide the frames.

---

## TD's source

### TDGTWR is TD's `STRUCT_GTOWER` (`tiberiandawn/bdata.cpp:320-370`)

```cpp
static BuildingTypeClass const ClassGTower(STRUCT_GTOWER,
    /* ... */
    true,   // IsSimpleDamage
    /* ... */
    false,  // IsTurretEquipped
    false,  // IsTwoShooter
    true,   // IsRepairable
    true,   // IsBuildable
    true,   // IsCrew
    /* ... */
    DIR_N,
    200,    // Strength
    3,      // Sight
    500,    // Cost
    /* ... */
    WEAPON_CHAIN_GUN,
    WEAPON_NONE,
    ARMOR_WOOD,
    0, 0, 0, 10,   // CanEnter/Capacity/Power/Drain
    BSIZE_11,
    /* ... */);
```

TD tests `STRUCT_GTOWER` only in `Fire_Data` and `Fire_Coord` (`building.cpp:2784-2787`, `2815-2821`): no
`Mission_Attack`, `Shape_Number`, `AI`, power or crew case.

### TDGUN is TD's `STRUCT_TURRET` (`tiberiandawn/bdata.cpp:475-530`)

```cpp
static BuildingTypeClass const ClassTurret(STRUCT_TURRET,
    /* ... */
    false,  // IsSimpleDamage
    /* ... */
    true,   // IsTurretEquipped
    false,  // IsTwoShooter
    true,   // IsRepairable
    true,   // IsBuildable
    true,   // IsCrew
    /* ... */
    (DirType)208,   // Starting facing, west-north-west (DIR_W 192, DIR_NW 224)
    200,    // Strength
    5,      // Sight
    600,    // Cost (250 before TD's patch)
    /* ... */
    WEAPON_TURRET_GUN,
    WEAPON_NONE,
    ARMOR_STEEL,
    0, 0, 0, 20,
    BSIZE_11,
    /* ... */);
```

| TD `building.cpp` | What |
|---|---|
| 2784-2787 | `Fire_Data`, the default case |
| 2795-2798 | `Fire_Data`, the SAM/TURRET branch |
| 2829-2832 | `Fire_Coord`, the SAM/TURRET branch |

And TD's `bdata.cpp:4553` and `4580`: `BuildingTypeClass::Raw_Cost` and `Cost_Of`, under `#ifdef PATCH`, return 250
for `IsV107 && STRUCT_TURRET && GameToPlay != GAME_NORMAL`, the cost of version-1.07 multiplayer games behind the
constructor's "250 before TD's patch". Not ported.

The turret turns in the generic `AI` rotation block (TD `building.cpp:1281-1290`).

### The weapons and projectiles (`const.cpp`, `bbdata.cpp`)

```cpp
{BULLET_SPREADFIRE, 25, 50, 0x0400, VOC_MINI, ANIM_GUN_N},        // WEAPON_CHAIN_GUN (const.cpp:71)
{BULLET_APDS, 40, 60, 0x0600, VOC_TANK4, ANIM_MUZZLE_FLASH},      // WEAPON_TURRET_GUN (const.cpp:82)
```

The chain gun: 25 damage, ROF 50, 4 cells, `VOC_MINI` (`GUN8`, `audio.cpp:128`), the 8-direction gun flash. The
turret gun: 40 damage, ROF 60, 6 cells, `VOC_TANK4` (`TNKFIRE6`), the muzzle flash. Both rows read
`{Fires, Attack, ROF, Range, Sound, Anim}`, TD's `type.h:50-91`.

```cpp
static BulletTypeClass const ClassSpreadfire(BULLET_SPREADFIRE,   // bbdata.cpp:87
    "50cal",         // Image
    true,            // High
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
    WARHEAD_HE,
    ANIM_PIFFPIFF);  // Impact

static BulletTypeClass const ClassAPDS(BULLET_APDS,               // bbdata.cpp:109
    "120mm",         // Image
    false,           // High
    false,           // Homes
    false,           // Arcs
    false,           // Drops
    false,           // Invisible
    false,           // Proximity arm
    false,           // Animates flame
    false,           // Has fuel
    true,            // No facing variation
    false,           // Inaccurate
    false,           // Translucent
    false,           // AA-capable
    0, 0,
    MPH_VERY_FAST,   // Speed
    0,               // ROT
    WARHEAD_AP,
    ANIM_VEH_HIT3);  // Impact
```

---

## What TF ships

### The constructors

| | `ClassTdGtwr` (`redalert/bdata.cpp:797`, registered at 5221) | `ClassTdGun` (`bdata.cpp:857`, registered at 5223) |
|---|---|---|
| Vertical offset | `0x0030` | `0x0030` |
| Primary offset | `0x0040` | `0x0080` |
| `IsSimpleDamage` | true | false |
| `IsTurretEquipped` | false | true |
| Initial facing | `DIR_N` | `(DirType)208` |
| Size, footprint | `BSIZE_11`, `List1` | `BSIZE_11`, `List1` |

Both match TD's constructors and `Fire_Coord`. `TDGTWR.ZIP` has 3 frames (simple damage); `TDGUN.ZIP` has 128 (32
facings in four sets). The turret turns at `ROT=12` through RA's `Rotation_AI`.

### `rules.ini`

`[TDGTWR]` is TD's: `Strength=200` (doubled in code, playbook §3.21), `Cost=500`, `Power=-10`, `Sight=3`,
`Armor=wood`, `Crewed=true`, plus `Points=25` and `Sensors=yes`. `[TDGUN]` likewise: `Strength=200`, `Cost=600`,
`Power=-20`, `Sight=5`, `Armor=steel`, `ROT=12`, `Crewed=true`, `Points=26`, `Sensors=yes`.

```ini
[TDChainGun]
Damage=25
ROF=50
Range=4
Projectile=TDSpreadfire
Speed=100          ; RA's percentage: 255, MPH_LIGHT_SPEED, so the invisible round lands at once
Warhead=TDHE
Report=GUN8        ; TD VOC_MINI
Anim=GUNFIRE

[TDSpreadfire]
Warhead=TDHE
ImpactAnim=PIFFPIFF
Inviso=yes
Image=none
High=yes

[TDTurretGun]
Damage=40
ROF=50             ; the Allied turret's rate of fire (TD: 60) (balance-deep-dive.md)
Range=6
Projectile=TDAPDS
Speed=40           ; the open item
Warhead=TDAP
Report=TNKFIRE6    ; TD VOC_TANK4
Anim=GUNFIRE

[TDAPDS]
Warhead=TDAP
ImpactAnim=VEH-HIT3
Image=120MM
```

`TDChainGun` and `TDTurretGun` aren't `IsTDPort` weapons (`rules.cpp:735`, `737`), so their `Speed=` is RA's
percentage; `TDSpreadfire` and `TDAPDS` are `IsTDPort` bullets (`bbdata.cpp:214-215`), detonating with their own
`Warhead=` and `ImpactAnim=`. The chain gun flashes with `Anim=GUNFIRE`, the plain muzzle flash (RA's `ANIM_MUZZLE_FLASH`, `adata.cpp:1130`), chosen over
`MINIGUN` (TD's 8-direction `ANIM_GUN_N`; see the field manual's
[Weapons, muzzle flashes and offsets](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#weapons-muzzle-flashes-and-offsets)).

The sounds are `VOC_TD_MINI` (`GUN8`, `audio.cpp:257`) and `VOC_TD_TANK4` (`TNKFIRE6`, `audio.cpp:253`).

---

## Decisions

- **No donor.** Every value comes from TD's source, not from the RA building of the same shape.
- **Own sections.** `[TDChainGun]`, `[TDSpreadfire]` and `[TDAPDS]` are TD ports, never RA's `[Vulcan]`,
  `[Invisible]` or `[Cannon]`. RA's `[Vulcan]` (40 damage, ROF 40, 5 cells, `SA`, `GUN13`) would make the tower far
  stronger than TD's. `[TDAPDS]` matched RA's `[Cannon]` value for value when it was split off; its own section
  stops RA balance changes to `[Cannon]` moving TDGUN.
- **TD's stats even where weaker.** A tower that feels weak is balanced through TD levers (range, ROF,
  `Strength=`), never by binding a non-TD weapon.

## Checks after a change

1. TDGTWR fires `GUN8` from the top of the tower, 25 a shot on light infantry, at 4 cells.
2. TDGUN turns at `ROT=12` and fires `TNKFIRE6` with the muzzle flash from the barrel, 40 a shot with `TDAP`.
3. Below half strength each shows its damaged frame.

Related: `td-sam-deep-dive.md`, `td-atwr-deep-dive.md`, `td-obli-verification.md`.
