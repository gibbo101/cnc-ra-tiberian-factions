# TD attack helicopters: the Apache and the Orca

**Status:** Reference; shipped in 1.0.0. The Apache (`TDHELI`, `AIRCRAFT_TDAPACHE`) and the Orca (`TDORCA`,
`AIRCRAFT_TDORCA`) fly RA's own attack-aircraft loop. Both have 225 strength for $1200, RA's helicopters' numbers
(`balance-deep-dive.md`). Read with `td-vehicle-port-recipe.md`.

---

## TD's two units

| | Apache (`AIRCRAFT_HELICOPTER`, "HELI") | Orca (`AIRCRAFT_ORCA`, "ORCA") |
|---|---|---|
| Display | `TXT_HELI`, "Apache" | `TXT_ORCA`, "Orca" |
| Faction | Nod (`HOUSEF_BAD`) | GDI (`HOUSEF_GOOD`) |
| Weapon | `WEAPON_CHAIN_GUN` | `WEAPON_DRAGON` |
| Rotor | yes, single | no: a VTOL with jets |
| Two-shooter | yes | yes |
| Ammo | 15 | 6 |
| Strength, cost | 125, 1200 | 125, 1200 |
| Armour, speed, ROT | steel, `MPH_FAST`, 4 | steel, `MPH_FAST`, 4 |
| Build level, prerequisite | 6, helipad | 6, helipad |
| Lands on clear ground | no, returns to a helipad | no |

`WEAPON_CHAIN_GUN` is `{BULLET_SPREADFIRE, 25, 50, 0x0400, VOC_MINI, ANIM_GUN_N}`, TF's Guard Tower `TDChainGun`;
`WEAPON_DRAGON` is `{BULLET_TOW, 30, 60, 0x0400, VOC_BAZOOKA}`, TF's `TDDragon` (the Rocket Soldier's and the Recon
Bike's). Both of those fire one shot, so each helicopter takes a `Burst=2` variant for TD's two-shooter:

- **Apache:** `[TDApacheGun]`, `TDChainGun` with `Burst=2` and `Anim=MINIGUN` (TD's small directional gun flash;
  `GUNFIRE` read as an explosion on the nose).
- **Orca:** `[TDStnkDragon]`, the Stealth Tank's `TDDragon` with `Burst=2`, the same two-shot `WEAPON_DRAGON`.

---

## The loop is RA's

Fly to the target, strafe in pairs, fly back to a helipad when `Ammo` runs out, reload, repeat: RA's
`AircraftClass` runs all of it for any type built like its Hind. See the field manual's
[The same pass for TD's rocket launchers and aircraft](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-buildings-and-defences.md#the-same-pass-for-tds-rocket-launchers-and-aircraft).
The flight back to reload is `MISSION_ENTER`, set in `AircraftClass::Mission_Move` (`aircraft.cpp:2142`) and
`Enter_Idle_Mode` (`aircraft.cpp:2422`, `2542`). There is no `_TD()` port, unlike the ground units' missions. The helipad plumbing for a separated `TDHPAD` is the
playbook's §3.11 and §3.12.

## The constructors (`redalert/aadata.cpp`)

Both are RA's Hind (`AIRCRAFT_HIND`): not fixed-wing, no custom rotor sets, not landing on clear ground, landing on
`STRUCT_HELIPAD` at `0xFF`, primary offset `0x0040`, 32 facings, `MISSION_HUNT`.

- **`TdApacheHeli`** (`aadata.cpp:372`): one rotor, drawn by `Draw_Rotors`' generic single-rotor branch at the body
  centre, as RA's Hind and Longbow are, not the Chinook's two-rotor branch.
- **`TdOrca`** (`aadata.cpp:395`): no rotor, so it draws its body alone (see the manual's "The Orca has no rotor").
  RA has no rotorless attack aircraft; the Hind with the rotor off is all it needs.

Ported aircraft art can disagree with offsets RA hardcodes per type: on the Chinook, the two-rotor branch drew the
rotors off the TD-Assets art, and its facing 0 pointed diagonally. Check a new aircraft's facing 0 and rotor in game
first.

`AircraftTypeClass::One_Time` (`aadata.cpp:671`, `679`) lends each the Hind's `ImageData` and `CameoData`. With its
classic stub missing from TFASSETS, a donor must have at least as many frames as the type draws (TDORCA 0-31, TSHUNT
0-7), and the Hind's 32 cover both. The HD art is TD's `HELI` (32 frames) and `ORCA` (64).

## `rules.ini`

`[TDHELI]` and `[TDORCA]`: `Strength=225`, `Armor=heavy`, `Cost=1200`, `TechLevel=6`, `Speed=16` (`MPH_FAST`),
`ROT=4`, `Sight=0`, `Points=80`, `Crewed=yes`, `Prerequisite=hpad`; the Apache `Ammo=15`, `Owner=BadGuy`; the Orca
`Ammo=6`, `Owner=GoodGuy`.

## Names and cameos

The Apache's sidebar label is `TEXT_UNIT_TITLE_NOD_HELICOPTER` ("Attack Helicopter") with `Name=Apache` in its
popup; the Orca uses the base game's `TEXT_UNIT_TITLE_GDI_ORCA`. Neither needs a CONFIG.MEG edit. The cameos are the
base game's `BuildIcon_TD_Apache` and `BuildIcon_TD_Orca`. Both constructors pass RA's `TXT_ORCA` as a placeholder
text ID; the names come from `Name=` and the launcher's text.
