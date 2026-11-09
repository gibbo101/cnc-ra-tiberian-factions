# TDSAM: the SAM site

**Status:** Reference; shipped before 1.0.0. TDSAM runs its own state machine and binds
`Primary=TDNike` (→ `Projectile=TDPatriot`, `Warhead=TDAP`).

Live stats are in `rules.ini` and `balance-deep-dive.md`. TD entities run TD's own building, weapon and projectile
code, ported from `reference/vanilla-conquer/tiberiandawn/`, never RA's nearest equivalent (`td-port-playbook.md`).

The game-level facts (TD's eight states, its frames, half damage underground, the rotation rate, the firing arc,
the launch flash, the muzzle offset, the air-only threat scan, no `_anims` entry) are in the field manual's
[Porting TD buildings and defences](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#the-sam-site-rise-fire-twice-lower),
The SAM site, and its Weapons, muzzle flashes and offsets. This doc holds TD's transitions in full and what TF
ships.

---

## TD's state machine (`tiberiandawn/building.cpp:105-116, 4281-4439`)

```cpp
enum SAMState {
    SAM_NONE = -1,
    SAM_UNDERGROUND, // hidden, awaiting target
    SAM_RISING,      // frames 0-15, driven by Set_Stage
    SAM_READY,       // up, rotating to face TarCom
    SAM_FIRING,      // first shot
    SAM_READY2,      // re-rotate after shot 1
    SAM_FIRING2,     // second shot
    SAM_LOCKING,     // rotating back to DIR_N
    SAM_LOWERING,    // frames 48-63
};
```

| From | When | To | Notes |
|---|---|---|---|
| `SAM_UNDERGROUND` | `Target_Legal(TarCom)` | `SAM_RISING` | `Set_Rate(2); Set_Stage(0);` |
| `SAM_UNDERGROUND` | no target | (stays, returns to `MISSION_GUARD`) | |
| `SAM_RISING` | `Fetch_Stage() == 15` | `SAM_READY` or `SAM_LOWERING` | `Set_Rate(0); PrimaryFacing = DIR_N;` |
| `SAM_READY` | target alive, an aircraft, altitude > 0 | rotate via `Set_Desired`, then `SAM_FIRING` | |
| `SAM_READY` | target lost | `SAM_LOCKING` | one-second pause |
| `SAM_FIRING` | `Can_Fire == FIRE_OK` | `Fire_At(TarCom, 0); SAM_READY2` | |
| `SAM_FIRING` | `FIRE_FACING` | `SAM_READY` | re-rotate |
| `SAM_READY2` | target re-acquired | rotate, then `SAM_FIRING2` | |
| `SAM_FIRING2` | `Can_Fire == FIRE_OK` | `Fire_At(TarCom, 0); SAM_LOCKING` | `return TICKS_PER_SECOND * 3`, the cooldown |
| `SAM_LOCKING` | `PrimaryFacing == DIR_N` | `SAM_LOWERING` | `Set_Rate(2); Set_Stage(48);` |
| `SAM_LOCKING` | not yet at N | `PrimaryFacing.Set_Desired(DIR_N)` | |
| `SAM_LOWERING` | `Fetch_Stage() >= 63` | `SAM_UNDERGROUND` | `Set_Rate(0); Set_Stage(0); return TICKS_PER_SECOND` |

Both shots are `Fire_At(TarCom, 0)`, the primary: the second is a refire after `SAM_READY2`, not a secondary
weapon. TD's SAM has none. The state is `Status`, a `char` on `MissionClass` (TD `mission.h:62`).

TD's other SAM sites:

| TD source | What |
|---|---|
| `building.cpp:548-571` | `Shape_Number`: the stage while rising or lowering, `+16` on the facing frame while raised (558-560), `+64` damaged |
| `building.cpp:1281-1289` | `AI`'s turn: `Rotation_Adjust(15)` for the SAM, 12 for the gun turret |
| `building.cpp:1492-1495` | `Take_Damage`: half damage underground, never less than one |
| `building.cpp:828-836` | `Fire_At`'s SAM branch: the launch flash at the centre, attached, then the sound |
| `building.cpp:2804-2836` | `Fire_Data`/`Fire_Coord`; the SAM/turret branch at 2828-2832 |
| `building.cpp:2838` | `Greatest_Threat`: `THREAT_AIR` from the bullet's `IsAntiAircraft` |
| `building.cpp:4291-4317` | the rise in `Mission_Attack` |
| `bdata.cpp:790` | `ClassSAM` |
| `bdata.cpp:3786-3816` | `_anims`, with no SAM entry |

The flash is made at the centre, not at `Fire_Coord`, because the `SAMFIRE` frames already place the muzzle for each
direction.

---

## What TF ships

### The states and the frames

`TdSamState` (`redalert/building.cpp:166`) is TD's enum for `STRUCT_TDSAM` only; RA's two-state `SAMState` is
untouched. Both live in the one `Status` byte (`SAM_READY` and `TDSAM_UNDERGROUND` are both 0), so every dispatch
site tests the type first. A new TDSAM starts at 0, underground.

`Shape_Number`'s `STRUCT_TDSAM` branch (`building.cpp:1264`) is TD's: the 32 raised facings at
`BodyShape[Dir_To_32(...)] + 16` in the five raised states, the stage otherwise, and `+64` at
`Health_Ratio() <= Rule.ConditionYellow` (TD's `< 0x0080` rewritten, playbook §3.16). RA's `Dir_To_32` stands in
for TD's `Facing_To_32`. `TDSAM.ZIP` has 129 frames, mapped as shapes 0 to 128 in TF's `RA_STRUCTURES.XML` from
line 28358; the 129th (128) is unexplained, perhaps a bib or construction tail. Drawn under RA's indexing, TF's SAM
showed half-risen frames and seemed to fire from the back of the launcher. That was the render (rising frames 0 to
15 drawn where the raised facings 16 on belong), not the muzzle offset: fix the frames and the muzzle lines up.

### The cycle (`Mission_Attack`, `building.cpp:6208`)

A port of TD's eight states, with one change: after the second shot TF's SAM goes back to `TDSAM_READY` while an
air target remains (`TF_SAM_Air_Target`, `TDSAM_Try_Reacquire` at `building.cpp:4166`), instead of TD's
three-second cooldown, lock and lower. TD's full cycle (rise about 32 ticks, two shots, the 45-tick cooldown, the
turn, lower about 32, 15 ticks underground) dealt about a quarter of the Soviet SAM's damage per tick; staying up
matches it. The site still turns north and lowers once nothing is left to shoot, and still takes half damage while
underground, so it is hard to kill shut and vulnerable in a fight.

### The other TD rules

- **Half damage underground:** `Take_Damage` (`building.cpp:2386`), TD's `building.cpp:1492-1495`.
- **Rotation:** data, `ROT=15` in `[TDSAM]`; there is no `STRUCT_TDSAM` rotation branch.
- **Threats:** `Greatest_Threat`'s `STRUCT_TDSAM` branch (`building.cpp:4133`) scans `THREAT_AREA`, plus
  `THREAT_AIR` from the anti-aircraft bullet, so the site starts rising while an aircraft is still inbound.
- **Animation ranges:** `[TDSAM]`'s `IdleAnim*` and `ActiveAnim*` stay `(0,1,0)`; `Mission_Attack` drives the rise
  and lower. The build-up is 30 frames at rate 2 (`TDSAMMAKE.ZIP`).
- **Constructor:** `ClassTdSam` (`bdata.cpp:886`), registered at `bdata.cpp:5224`: offsets `0x0030`/`0x0080` (TD's
  `Fire_Coord`), `BSIZE_21`, `IsTurretEquipped` true, `DIR_N`, as TD's `ClassSAM`.

### Aliased sites: the shared-branch rule

A *positive* dispatch that drives distinct behaviour (`Mission_Attack`, `Shape_Number`, `Take_Damage`,
`Greatest_Threat`) gets its own `STRUCT_TDSAM` branch. A site where RA's SAM and TD's behave identically may name both
in one test, with a comment. The shared sites:

| Site | What both SAMs share |
|---|---|
| `building.cpp:1727` | jammed by a mobile radar jammer |
| `building.cpp:2687` | no auto-retaliation |
| `building.cpp:3207` | the assign-target range bypass |
| `building.cpp:4572` | `What_Action`'s attack test |
| `building.cpp:4785` | `Can_Fire`'s firing arc of 64 |
| `building.cpp:8969` | redraw on a stage change |
| `techno.cpp:1926` | landed aircraft aren't targets |

Two TD buildings sharing one branch for identical behaviour follow the same rule (the crew step in
`td-atwr-deep-dive.md`).

### The weapon and the projectile

TD's `WEAPON_NIKE` (`const.cpp:91`) is `{BULLET_SAM, 50, 50, 0x0780, VOC_ROCKET2, ANIM_NONE}`, and `BULLET_SAM`
(TD's `ClassPatriot`, `bbdata.cpp:197`):

```cpp
static BulletTypeClass const ClassPatriot(BULLET_SAM,
    "MISSILE",     // Image
    true,          // High (over walls)
    true,          // Homes
    false,         // Arcs
    false,         // Drops
    false,         // Invisible
    true,          // Proximity arm
    true,          // Animates flame
    true,          // Has fuel
    false,         // No facing variation
    false,         // Inaccurate
    false,         // Translucent
    true,          // AA-capable
    0,             // Arming
    0,             // Range override
    MPH_VERY_FAST, // Speed
    10,            // ROT (turn rate)
    WARHEAD_AP,
    ANIM_VEH_HIT1);
```

TF ports both as its own sections, never RA's `[Nike]` or `[AAMissile]`:

```ini
[TDNike]
Damage=50
ROF=20            ; RA's Nike rate of fire (TD: 50) (balance-deep-dive.md)
Range=7.5         ; TD 0x0780
Projectile=TDPatriot
Speed=100         ; MPH_VERY_FAST, read raw (IsTDPort)
Warhead=TDAP      ; TD WARHEAD_AP
Report=ROCKET2    ; TD VOC_ROCKET2
Anim=SAMFIRE      ; ANIM_SAM_N, turned by PrimaryFacing

[TDPatriot]
Image=MISSILE
High=yes
Homing=yes
Shadow=no
Proximity=yes
Animates=yes
Ranged=yes
AA=yes
AG=no
ROT=20            ; RA's AAMissile turn rate (TD: 10), to turn onto RA's faster aircraft
Rotates=yes
Warhead=TDAP
ImpactAnim=VEH-HIT1
```

`Anim=SAMFIRE` gives TD's launch flash with no code: see the field manual's
[Weapons, muzzle flashes and offsets](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#weapons-muzzle-flashes-and-offsets).
TF's `TechnoClass::Fire_At` turns it by `PrimaryFacing` (`techno.cpp:3870-3871`), over RA's eight `SAMN` to `SAMNE`
entries (`adata.cpp:197-351`), the same as TD's.
`Speed=100` is raw only because `TDNike` is `IsTDPort` (`rules.cpp:794`); as RA's percentage it stops the missile
dead (playbook §3.1). `Homing=` is TF's own key (`IsHoming`). `TDPatriot` is accurate against aircraft, as TD's `BULLET_SAM` is. It is
`Ranged=yes` (fuelled), and `Unlimbo_TD` scatters a fuelled shot at an infantry target (`td-atwr-deep-dive.md`), so
it does scatter at an airborne jumpjet, which `TF_SAM_Air_Target` (`building.cpp:183`) counts as an air target. The
sound is `VOC_TD_ROCKET2`, shared with the Advanced Guard Tower.

---

## Decisions

- **No donor.** The constructor, the states, the frames, `[TDNike]` and `[TDPatriot]` come from TD's source, not
  from RA's SAM.
- **Armour:** TD's 200 strength on steel. Fragile when up, by design; half damage underground gives it durability
  where it matters.
- **Two enums** in the one `Status` byte, as above.

## Checks after a change

Skirmish rarely brings aircraft to a SAM, so test against a second player's aircraft. Force-fire on a friendly
aircraft shows the rise, turn, fire and lower, but not the second shot.

1. Placed, it sits underground on frame 0.
2. An aircraft in range: it rises through 16 frames, turns at `ROT=15`, and fires `TDNike` twice, each with
   `ROCKET2` and the launch flash at the raised launcher.
3. While an air target remains it stays up; with none left it turns to north, lowers and goes underground.
4. Underground it takes half damage: strafe the idle site with a Yak, or fire on it from the ground.
5. Every frame drawn is a `tdsam-NNNN` tile, none of RA's SAM.
6. RA's own SAM is unchanged against a Yak in an RA-against-RA skirmish.
