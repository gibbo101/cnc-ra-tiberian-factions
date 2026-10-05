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
  stats, prerequisite TSTECH, power −200, grants `SPC_TS_FIRESTORM`. Idle anims at TS's speeds (TS
  `Rate=` is frames per minute: OpenTS `animtype.cpp` delay = TICKS_PER_MINUTE / Rate). The AI
  doesn't build it (TS's AI never raises the field either).
- **Sections** (`TSFSDF`): 1x1, not selectable, insignificant, no build-up, $250, power −2, 200 HP
  concrete, prerequisite TSFGEN, `BaseNormal=no`, `Adjacent=3`. Art from `scripts/ts_pack_fsdf.py`:
  frame = own neighbour sections (N1 E2 S4 W8), +16 damaged, +32 live (`BuildingClass::Shape_Number`;
  the damaged groups repeat the undamaged art). Walkable while `HouseClass::IsFirestormLive` is false
  (the mine and Limpet pattern in `Can_Enter_Cell` and `What_Action`); sorts under units; doesn't keep
  a player alive. Sections chain only from other own sections (`TF_Section_Chains_To` in
  `display.cpp`, and the placement ghost's distance map, `Calculate_Placement_Distances` in
  `dllinterface.cpp`, which is the real gate). Sell only while the field is down: removed at once,
  no refund.
- **Line fill for every wall** (`TF_Wall_Line_Fill` in `house.cpp`, from `Place_Object`): placing a
  wall within 5 cells in a straight line of another of the house's walls of the same type fills the
  gap when every cell between is clear, charging each section; it stops when the money runs out.
  Sandbags, concrete, barbed wire, wood, chain link, fence, the TS wall and the Firestorm sections.
  The launcher owns the placement ghost, so the line appears on placing the second end.
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
  Seeker excepted. Airborne damage is doubled because `AircraftClass::Take_Damage` halves it. A live
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
  Dead ends: rotating TS's sprite as it is (lopsided lighting, dish off-centre), the 32° squash of the
  hub and east-west rails, a generated flat rim, Blender geometry.
- **No screen-position click readers:** the click comes through the patched launcher handler.

## Traps

- **Wall-section seam:** the launcher places a sprite half its classic stub width from its centre,
  so an odd stub width lands ~2.7 HD px east. TSFSDF's stub is 33x60 (`build_tfassets.sh`). If a
  section ever shows a seam beside an even-stub piece (gates, BRIK), pad it to an even width, as the
  TS walls and towers were (192-wide canvases, stub 36).
- **TS Service Depot pad seat** (built in this arc): the depot's 3x3 is solid, so a vehicle on it may
  cross its cells to leave; the gantry cells (west column, top two: `TF_Depot_Is_Gantry`) stay
  closed to every vehicle; exits are two cells out. The pad glow is `TSDEPTRP` (GTDEPT_D frames
  0-13, drawn while BSTATE_ACTIVE; GADEPT_C1-C3 exist in no TS mix). The pad ring's centre is 6 px
  east and 9 px south of the middle cell, and `DriveClass::Start_Of_Move` drives the last step onto
  it (`Rail_To`), but only some approaches get there. Once the HD depot's ring is centred on the
  middle cell, `TS_DEPOT_SEAT_EAST_PX` / `_SOUTH_PX` (`building.h`) go to 0 and the drive-on rail
  comes out. Glide approaches (`Roll_On_Seat`) were rejected.

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

### Mechanics (OpenTS; file:line in `reference/OpenTS/code/`)

**Charge-drain superweapon** (super.cpp, super.h:119-125). States SUSPENDED / CHARGING / READY /
FIRESTORM_ON; placeable in any state but CHARGING (super.cpp:582).
- READY -> ON: drain time = current charge x ChargeToDrainRatio (:335); TS's rules set it to .333, so a full 3-minute charge buys 1 minute of field (OpenTS's default of 3 is overridden); `House->Activate_Firestorm()`.
- ON -> off early (click again): leftover drain turns back into charge (:328-330).
- READY keeps charging, so a partial charge can be used (:389).
- Drain runs out: wall drops, state CHARGING from zero (:397-401).
- Low power or generator switched off: SUSPENDED, wall drops; power back = charge from zero
  (house.cpp:8688-8750, super.cpp:168-186).
- Generator destroyed/sold/limbo'd with no other generator standing: wall drops
  (house.cpp:6586-6603). Capture: nothing special.
- Computer houses toggle without drain (only map triggers raise it; the AI never does).

**The field** (house.cpp:6535-6577; building.cpp:9336-9433). House flag
`FirestormDefenseActivated`. Every section the house owns goes live, anywhere on the map (no link
to the generator, no range).
- Active section = impassable to everyone, own units included (PASSABLE_NO + zone reset).
  Inactive = passable to everyone (unit.cpp:3881, infantry.cpp:1695, cell.cpp:4516).
- On activation: anything standing on a section dies (full-Strength FirestormWarhead, forced, no
  friend/foe test), except `IgnoresFirestorm`. Anything moving INTO a section in the 5x5 around it
  dies too (C4 warhead).
- Aircraft (and jumpjets) whose cell is a live section die, at any altitude (fly.cpp:767).
- Projectiles entering a live cell are deleted with a flare unless fired by the wall's owner or
  `IgnoresFirestorm` (bullet.cpp:800-813; allies' shots are eaten too); instant weapons stop at
  the first hostile live cell (map.cpp:12335).
- A live section takes no damage; each hit drains the field instead: charge -= damage x 0.1
  (building.cpp:2261-2268).
- Firestorm deaths spawn 7-9 FirestormSparkSys bursts instead of the normal explosion.

**Visuals.** Section frame = neighbour bits N1 E2 S4 W8, +32 while live (building.cpp:9314-9346).
GAFSDF_A (8 frames) plays on live non-straight sections. FSIDLE: every 8 frames each live
non-straight section with no column showing has a 1-in-16 chance to spawn one, a one-shot,
50% translucent (building.cpp:1756-1762) -- the field is flickering columns, not a steady wall.
FSGRND at the wall / FSAIR at the victim (height > 100) on every crossing.

**Audio/EVA.** 00-I162 "Firestorm defense ready" (RechargeVoice), 00-I170 "Firestorm defense
offline" on deactivation. No hardcoded sounds; the anims' Report= carry any.

**Sections as buildings.** Placed like a building; TS also fills the gap to another own section
up to 5 cells away in a straight line if every cell between is clear (map.cpp:12419-12446), fill
sections free. Neighbours refresh on Unlimbo/Limbo. Sell only while inactive, no refund.
Power up/down ignores sections. OpenTS hardcodes the section's cost to 250 (techtype.cpp:553)
against the rules' 50; ours charges 250.

**Not in TS:** subterranean units ignore the field; EMP has no special case (it can knock power
out, which suspends the field and resets its charge).
