# TD Rocket Launcher (MLRS) and SSM Launcher

**Status:** Reference; shipped in 1.0.0 as `UNIT_TDMLRS` (GDI, `Prerequisite=weap,TDEYE`) and `UNIT_TDMSAM` (Nod,
`Prerequisite=weap,TDTMPL`). `TDSSM2` ports `BULLET_SSM2` value for value except its accuracy: TD's scatters by type, TF's is `Inaccurate=no`. Read alongside
`td-vehicle-port-recipe.md`.

Live stats are in `rules.ini` and `balance-deep-dive.md`.

---

## The crossed art

TD's two rocket launchers wear each other's art: see the field manual's
[The same pass for TD's rocket launchers and aircraft](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#the-same-pass-for-tds-rocket-launchers-and-aircraft).
Display names and weapons are coherent; only the art is crossed.

| | `UNIT_MLRS` (TD `udata.cpp:854`) | `UNIT_MSAM` (TD `udata.cpp:477`) |
|---|---|---|
| Display name | `TXT_MLRS`, "Rocket Launcher" | `TXT_MSAM`, "S.S.M. Launcher" |
| Art | `"MSAM"` | `"MLRS"` |
| Weapon | `WEAPON_MLRS` → `BULLET_SSM2` | `WEAPON_HONEST_JOHN` → `BULLET_HONEST_JOHN` |
| Prerequisite | `STRUCTF_EYE` | `STRUCTF_ATOWER` |
| Ownable | `GOOD｜BAD` | `BAD` only (GOOD commented out) |
| Death explosion | `ANIM_ART_EXP1` | `ANIM_FRAG2` |
| Turret, locked while moving | yes, yes | yes, yes |
| Two-shooter | yes | no |
| Strength, cost, sight | 100, 800, 4 | 120, 750, 4 |
| Speed, armour, locomotion | `MPH_MEDIUM`, aluminium, track | `MPH_MEDIUM`, aluminium, track |
| Default order | `MISSION_GUARD` | `MISSION_HUNT` |
| Build level | 7 | 7 |

TF's `UNIT_TDMLRS` (INI name `TDMLRS`) carries the `MSAM` art (`MSAM.SHP:TDMLRS.SHP` in `build_tfassets.sh`,
`MSAM.ZIP`), and `UNIT_TDMSAM` the `MLRS` art (`MLRS.SHP:TDMSAM.SHP`). The names lie: follow the constructor.

---

## The Rocket Launcher (`UNIT_TDMLRS`)

### Faction and tier

TD sets both ownable bits, but `STRUCTF_EYE` (the Advanced Communications Center, TF's GDI-only `TDEYE`) means only
GDI can build it, so TF's is `Owner=GoodGuy`. Build level 7 behind the Eye makes it TD's late-game GDI siege unit;
TF keeps the gate as `Prerequisite=weap,TDEYE`. The artillery roster splits as GDI's Rocket Launcher against Nod's
Artillery and SSM Launcher.

### Weapon and missile

TD's `WEAPON_MLRS` (`const.cpp:84`) is `{BULLET_SSM2, 75, 80, 0x0600, VOC_ROCKET1, ANIM_NONE}`. `BULLET_SSM2`
(`ClassMissile2`, `bbdata.cpp:175`) is `BULLET_SSM` with arming 9 and `ROT` 7 for 7 and 5: `DRAGON` art, homing,
anti-aircraft, proximity, flame, fuel, inaccurate, translucent, `MPH_ROCKET`, `WARHEAD_HE`, `ANIM_FRAG1`.

TF ports it as `[TDSSM2]` (`BULLET_TDSSM2`, `IsTDPort`, on the `TDDRAGON` art and its donor `ImageData`): `[TDSSM]`
with `Arm=9` and `ROT=7`, and `Inaccurate=no` as TF's `[TDSSM]` has: TD's `ClassMissile2` is inaccurate, and TF made both
missiles accurate by choice (`balance-deep-dive.md`). Reusing `[TDSSM]` would have been near, not
byte-identical, and the playbook ports rather than reuses a near match.

The weapon is `[TDMlrsRocket]`, named apart from the `[TDMLRS]` unit (playbook §3.33): 75 damage, ROF 80, `Range=7`
(TD: 6; a cell short of the cannon artillery, still outranging the turrets and the Advanced Guard Tower),
`Speed=60` raw (`IsTDPort`), `Warhead=TDHE`, `Report=ROCKET1` (`VOC_TD_ROCKET1`, the Mammoth's), and `Burst=2` for
TD's two-shooter.

```
Primary=TDMlrsRocket   dmg 75 / ROF 80 / range 7 / Burst=2 / ROCKET1
  Projectile=TDSSM2    TDSSM with Arm=9 / ROT=7, TDDRAGON art
  Warhead=TDHE
Explosion=ANIM_ART_EXP1 (RA's own)
```

### Constructor and section

`UnitTdMlrs` (`redalert/udata.cpp:707`): turret, locked while moving, no crushing, not gigundo, `ANIM_ART_EXP1`, 32
facings, `MISSION_GUARD`, vertical offset `0x0010` and no weapon offset (the rear launcher, tuned by screenshot;
TD gives no muzzle value).

`[TDMLRS]`: `Image=TDMLRS`, `ShapeSize=48,48`, `Name=MLRS`, `Tracked=yes`, `Strength=100`, `Armor=light`,
`TechLevel=7`, `Speed=7` (`MPH_MEDIUM` 18, by the manual's formula), `Cost=800`, `Points=72`, `ROT=5`,
`Crewed=yes`.

### The 96-frame art

`MSAM.ZIP` holds 96 frames, not a turreted vehicle's 64, and no RA vehicle tileset has that many (V2RL's 80 is the
most), so the usual `--tileset-donor <vehicle>` slice doesn't reach it. TF's `RA_UNITS.XML` maps all 96 shapes for
`TDMLRS`. What the third run of 32 is for (a raised launcher, perhaps) is unconfirmed.

---

## The SSM Launcher (`UNIT_TDMSAM`)

`UnitTdMsam` (`udata.cpp:738`) is the MLRS's constructor with `ANIM_TDFRAG2` (TF's port of TD's `ANIM_FRAG2`) and
`MISSION_HUNT`. It fires `[TDHonestJohn]`, TD's `{BULLET_HONEST_JOHN, 100, 200, 0x0A00, VOC_ROCKET1, ANIM_NONE}`:
100 damage, ROF 200, 10 cells, `Speed=40` raw (TD's `MPH_FAST`), on the non-homing `TDMissile` napalm rocket with
`Warhead=TDFIRE`. `[TDMSAM]` is `Owner=BadGuy` behind the Temple (`Prerequisite=weap,TDTMPL`), not TD's Advanced
Guard Tower; `RA_UNITS.XML` maps 128 shapes for its art.
