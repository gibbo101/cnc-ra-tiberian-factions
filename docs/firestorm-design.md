# Firestorm Defense

**Status:** Reference; shipped in 5.0.0.
**Open:** the line-fill placement preview, the TS Service Depot pad seat (waits for the HD depot),
damaged section art, and the enemy-side checks, which need a LAN game (`todo.md`).

TS GDI's Firestorm Generator (`STRUCT_TSFGEN`) and Firestorm Wall Sections (`STRUCT_TSFSDF`)
follow TS rules: one left click on the cameo raises the field, another drops it and banks what is
left. Engine reference: OpenTS (`reference/OpenTS/code/`); data: TS's own `RULES.INI` / `ART.INI`
(TIBSUN.MIX), which OpenTS does not carry. The roster is in `ts-gdi-tree-plan.md`.

## What ships

- **The generator** (`TSFGEN`; `TSFIRE` is the Devil's Tongue fire-stream particle's art name): TS
  stats, prerequisite TSTECH, power −200, grants `SPC_TS_FIRESTORM`. Idle anims at TS's speeds (`Rate=`
  read as the field manual's
  [Porting art from other C&C games](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/porting-art-from-other-games.md#tiberian-sun)
  says). The AI
  doesn't build it (TS's AI never raises the field either).
- **Sections** (`TSFSDF`): 1x1, not selectable, insignificant, no build-up, $250, power −2, 200 HP
  concrete, prerequisite TSFGEN, `BaseNormal=no`, `Adjacent=3`. HD art from
  `scripts/ts_pack_hd_buildings.py`, cameo from `scripts/ts_pack_fsdf.py`: frame = own neighbour
  sections (N1 E2 S4 W8), +16 damaged, +32 live (`BuildingClass::Shape_Number`; the damaged groups
  repeat the undamaged art). Walkable while `HouseClass::IsFirestormLive` is false
  (the mine and Limpet pattern in `Can_Enter_Cell` and `What_Action`); sorts under units; doesn't keep
  a player alive. Sections chain only from other own sections (`TF_Section_Chains_To` in
  `display.cpp`, and the placement ghost's distance map, `Calculate_Placement_Distances` in
  `dllinterface.cpp`, which is the real gate). Sell only while the field is down: removed at once,
  no refund.
- **Line fill for every wall** (`TF_Wall_Line_Fill` in `house.cpp`, from `Place_Object`): placing a
  wall within 5 cells in a straight line of another of the house's walls of the same type fills the
  gap when every cell between is clear, charging each section; it stops when the money runs out.
  Sandbags, concrete, barbed wire, wood, chain link, fence, the TS wall and the Firestorm sections.
  For the placement ghost, see the field manual's [Firestorm Defense](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/behaviours/firestorm-defense.md#line-fill-for-every-wall), line fill.
- **The superweapon** (`SPC_TS_FIRESTORM`, the targeted `SW_ION_CANNON` route, AssetName
  `SW_TSFire`, TS's FSTDICON cameo) runs on a charge-drain `SuperClass`: a full charge buys a minute
  of field; the sidebar clock runs back down while draining. The field drops when the drain runs out,
  the power falls short or the last generator goes, then charges from zero.
- **Control is TS's:** the cameo's left click is patched in ClientG to arrive as a build request
  (`TF_Patch_ClientG_Click_Specials`, `launcher-vs-dll-ownership.md`), and `CNC_Handle_Sidebar_Request`
  turns it into `SPECIAL_PLACE` (clicks within a third of a second count once).
  `Place_Special_Blast` toggles: draining → `SuperClass::Stop_Drain(3)` (OpenTS `super.cpp:327`:
  leftover drain x3 back as charge, `IsPartCharged` keeps it usable while it charges on);
  otherwise `Start_Drain(Charge() / 3)`, so a part charge buys a shorter field. It stays in the
  superweapon tab.
- **The field** (`TF_Firestorm_Burn` in `house.cpp`, every frame): anything on the house's live
  sections dies (own units too, `WARHEAD_TSFLAMEHIT`, forced), and any aircraft over one, the Hunter
  Seeker excepted. Airborne damage is doubled (see the field manual's
  [Firestorm Defense](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/behaviours/firestorm-defense.md#traps), traps). A live
  section takes no damage; each hit drains damage/10 frames. Live sections block everyone
  (`Is_Open_Firestorm_Section`).
- **Shots:** `BulletClass::AI` deletes any projectile in a hostile live cell with a spark; instant
  shots are cut at the first hostile live cell on their path at launch (`TF_Firestorm_On_Path`). An
  eaten shot doesn't drain the field (TS).
- **Visuals and sound** (`scripts/ts_pack_firestorm_fx.py`): `ANIM_TS_FSIDLE` columns flicker up from
  hubs (every 8th frame, 1 in 16, never on straight runs), `ANIM_TS_FSGRND` at the wall and
  `ANIM_TS_FSAIR` at an aircraft's height on every crossing, each playing TS's FIRSTRM1
  (`VOC_TS_FIRSTRM1`). EVA: 00-I162 ready, 00-I170 offline (`scripts/ts_eva_build.py`).

## Rules chosen

- **Friendly fire is TS's:** a live section kills your own units that stand on or walk into it,
  and eats allies' shots; only the owner's shots pass.
- **Aircraft die at any height** over a live section, as in TS.
- **A section costs $250,** what TS players paid (OpenTS's hardcoded value), not the rules' $50.
- **Pad art is TS's pixels rebuilt for RA's grid:** a square 64 px hub centred in the cell with TS's
  dish in it, rails 64 px thick both ways with rungs 21 px apart, TS's beam on both sides of every
  rail, chamfered hub corners where no rail joins, one outline round the shape, no support legs.
  Rejected: rotating TS's sprite as it is (lopsided lighting, dish off-centre), the 32° squash of the
  hub and east-west rails, a generated flat rim, Blender geometry.
- **No screen-position click readers:** the click comes through the patched launcher handler.

## Traps

- **Wall-section seam:** an odd classic stub width lands a piece ~2.7 HD px east of its neighbours (why: the field
  manual's [Gates](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/behaviours/gates.md#joining-walls),
  joining walls). Wall pieces keep even stubs: sections
  256x256 (stub 48, `build_tfassets.sh`), TS walls 128x128 (stub 24), towers 256x384 (stub 48).
- **TS Service Depot pad seat:** the depot's 3x3 is solid, so a vehicle on it may
  cross its cells to leave; the gantry cells (west column, top two: `TF_Depot_Is_Gantry`) stay
  closed to every vehicle; exits are two cells out. The pad glow is `TSDEPTRP` (GTDEPT_D frames
  0-13, drawn while BSTATE_ACTIVE; GADEPT_C1-C3 are ART.INI sections that draw the one `GADEPT_C` SHP). The pad ring's centre is 6 px
  east and 9 px south of the middle cell, and `DriveClass::Start_Of_Move` drives the last step onto
  it (`Rail_To`), but only some approaches get there. Once the HD depot's ring is centred on the
  middle cell, `TS_DEPOT_SEAT_EAST_PX` / `_SOUTH_PX` (`building.h`) go to 0 and the drive-on rail
  comes out. Glide approaches were rejected.

## TS ground truth

### Rules (TIBSUN.MIX RULES.INI)

| Key | Value |
|---|---|
| `[GAFIRE]` | Fire Storm Generator: Strength 800, heavy, Cost 2000, Power -200, TechLevel 9, Prerequisite GATECH, Adjacent 2, Sight 5, Capturable, Crewed, SuperWeapon=FirestormSpecial. Art: Foundation 3x2, ActiveAnim GAFIRE_C + ActiveAnimTwo GAFIRE_B, Buildup GAFIREMK, cameo FSDICON |
| `[GAFSDF]` | Firestorm Wall Section: Strength 200, concrete, Cost 50, Power -2, Prerequisite GAFIRE, not repairable, not capturable, Selectable=no, IsBase=no, BaseNormal=no, FirestormWall=yes. Art: 1x1, cameo FSPICON |
| `[FirestormSpecial]` | Type=Firestorm, RechargeTime=3 (minutes), IsPowered, UseChargeDrain, RechargeVoice=00-I162, sidebar FSTDICON |
| `[General]` | ChargeToDrainRatio=.333 (drain = charge x .333: a full charge = 1 minute of field), DamageToFirestormDamageCoefficient=.1 |
| `[CombatDamage]` | FirestormWarhead=FirestormWH (100% vs every armour), DefaultFirestormExplosionSystem=FirestormSparkSys |
| `[AudioVisual]` | FirestormActiveAnim=GAFSDF_A, FirestormIdleAnim=FSIDLE, FirestormGroundAnim=FSGRND, FirestormAirAnim=FSAIR |
| `IgnoresFirestorm=yes` | the two hunter seekers |

### Mechanics (OpenTS, `reference/OpenTS/code/`)

See the field manual's [Firestorm Defense](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/behaviours/firestorm-defense.md#how-tiberian-sun-does-it)
for TS's model: the four charge-drain states, computer houses, the live field and the 5x5 kill, jumpjets, eaten
shots, the drain on hits, the spark bursts, the frames, `GAFSDF_A` and `FSIDLE`, the sounds, the EVA lines, the free
line fill, switching generators off, and selling sections. Beyond it:

- READY -> ON calls `House->Activate_Firestorm()`; TS's rules set `ChargeToDrainRatio` to .333, overriding
  OpenTS's default of 3 (`rules.cpp`).
- Capturing a generator does nothing special.
- The field is the house flag `FirestormDefenseActivated`. A live section is `PASSABLE_NO` plus a zone reset. The
  standing kill is a full-strength `FirestormWarhead`, forced, with no friend-or-foe test.
- An eaten shot is deleted with a flare (`Crossing_Firestorm`, then `Delete_Me`), and `FSGRND` / `FSAIR` play on
  every crossing, not only on a death. A projectile whose own type has `IgnoresFirestorm` passes (the test is
  `Class_Of()->IsIgnoresFirestorm`, the bullet's type, not the firer's).

Line refs, by claim:

| Claim | OpenTS |
|---|---|
| The four states | `super.h` 119-125 |
| Placeable in any state but CHARGING | `super.cpp` 582 |
| Drain time = charge x ratio | `super.cpp` 335 |
| Off early: leftover drain back to charge | `super.cpp` 328-330 |
| READY keeps charging | `super.cpp` 389 |
| Drain runs out: CHARGING from zero | `super.cpp` 397-401 |
| Low power or switched off: SUSPENDED | `house.cpp` 8688-8750, `super.cpp` 168-186 |
| Last generator gone: field drops | `house.cpp` 6586-6603 |
| The field going live | `house.cpp` 6535-6577, `building.cpp` 9336-9433 |
| Passable while inactive | `unit.cpp` 3881, `infantry.cpp` 1695, `cell.cpp` 4516 |
| Aircraft and jumpjets die at any altitude | `fly.cpp` 767 |
| Shots eaten | `bullet.cpp` 800-813 |
| Instant weapons stop at the first hostile live cell | `map.cpp` 12335 |
| Hits drain damage x 0.1 | `building.cpp` 2261-2268 |
| Frame = neighbour bits, +32 live | `building.cpp` 9314-9346 |
| `FSIDLE` spawn rule | `building.cpp` 1756-1762 |
| Free line fill | `map.cpp` 12419-12446 |
| The $250 section | `techtype.cpp` 553 |

**Not in TS:** subterranean units ignore the field; EMP has no special case (it can knock power
out, which suspends the field and resets its charge).
