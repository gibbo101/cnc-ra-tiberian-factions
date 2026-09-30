# Firestorm Defense — TS port design + arc tracker

Branch `firestorm` (off `main` @ f78d056b), worktree `../tf-subterranean-worktree`. TS GDI's
Firestorm Generator (`GAFIRE`) and Firestorm Wall Sections (`GAFSDF`) for the TS GDI tree.
Roster entry: `ts-gdi-tree-plan.md` 19b. Engine reference: OpenTS (`reference/OpenTS/code/`);
data: TS's own `RULES.INI` / `ART.INI` (TIBSUN.MIX), which OpenTS does not carry.

## RESUME HERE (2026-09-30 evening)

Stages A-E are DONE and verified in play on the Deck, and LAN parity for every launcher patch is done
(click specials, crest, tab icons, EVA, deploy and select-all keys; `launcher-vs-dll-ownership.md`).
`firestorm` = main + stage E + LAN work, local, not pushed.

Open, in order:
1. ~~Hunter Seeker on the same click route~~ DONE (5a7fb2a9, LAN-verified).
2. ~~LAN~~ DONE (5a7fb2a9, 8f85c28e, 4a447d6c, LAN-verified).
3. **Placement-preview probe** for the line fill (can the DLL see the cursor cell while a wall
   is placed; `INPUT_REQUEST_MOUSE_MOVE` returns early without legacy rendering).
4. Enemy-side checks are on main's LAN test list (`docs/todo.md` item 2).
5. **TS Service Depot (Luke, LAN test 2026-09-30):** units do not sit on the bay's centre and there
   is no repair animation. TS (OpenTS building.cpp:5490-5690): the unit docks within a quarter cell
   of Center_Coord (hover 0x96) and powers off; repair start = GADEPT_A lights off, GADEPT_C1 (gantry
   down) + GADEPT_D (repair) with C2 during; end = D and C2 stop, C3 (gantry up), lights back, EVA
   "unit repaired". Ours has only the idle _A/_B. Needs the four anims packed (sheet first) and the
   sequence in Mission_Repair; dock offset from a screenshot.
6. **Light orange selection box on a limpeted unit (Luke):** TS draws a limpeted object's bracket
   from another frame set (OpenTS techno.cpp:1455). The launcher tints CNC_SELECT_BOX.TGA (white,
   atlas 3027,4088 128x128) per draw; no data lever (SpiedByFlags draws the spy panel frame, not a
   box). Route: find the tint in ClientG and patch it, keyed on a field the DLL sets.

## Decisions (Luke)

- **Pad art = round C** (2026-09-29, "go with c!"): TS's pixels rebuilt for RA's grid. Square
  64 px hub centred in the cell with TS's dish centred in it (a clean octagon), rails 64 px thick
  in BOTH directions with the rungs 21 px apart both ways, TS's beam on both sides of every rail
  (symmetrical borders), chamfered hub corners where no rail joins, one outline round the whole
  shape, open where a rail crosses into the next cell. No support legs. Built by
  `fsdf_build8.py` (currently in `~/Desktop/firestorm/overnight/build-files/`, moves into
  `scripts/` with stage B). Dead ends, not to re-offer: rotating TS's sprite as-is (lopsided
  lighting, dish off-centre), the 32-deg squash of hub/east-west rails (hub not square, rails
  unequal), a generated flat rim, Blender geometry.
- **Control = TS's** (2026-09-30): left click the cameo, the field goes up at once (no cursor, no
  "select target"); left click again while it is up, it drops and what is left comes back as
  charge, and the weapon stays usable while it charges on. Must stay in the superweapon tab.
  Screen-position click readers are ruled out ("we own the source").

## Status

- **Stage E (control) VERIFIED in play 2026-09-30 (Deck, all five checks):** the launcher's
  cameo left-click handler is patched in memory at match start (`TF_Patch_ClientG_Click_Specials`,
  dllinterface.cpp; mechanism and ClientG addresses in `launcher-vs-dll-ownership.md`), so a left
  click on the Firestorm arrives as a build request. `CNC_Handle_Sidebar_Request` turns it into
  `SPECIAL_PLACE` (clicks within a third of a second count once). `Place_Special_Blast` toggles:
  draining -> `SuperClass::Stop_Drain(3)` (OpenTS super.cpp:327: leftover drain x3 back as charge,
  `IsPartCharged` keeps it usable while it charges on, no "ready" line when it tops up); otherwise
  `Start_Drain(Charge() / 3)`, so a part charge buys a shorter field. Runs out, low power or no
  generator: charging from zero, not usable, as before. Dev builds spawn the player a Firestorm
  Generator and three TS Power Plants at skirmish start (`scenario.cpp`, `TF_Dev_Cheats`).

- **Stage A (generator) VERIFIED and committed** (c4edb724): STRUCT_TSFGEN "TSFGEN" (TSFIRE is the
  Devil's Tongue fire-stream particle's art name). Idle anims at TS's speeds: TS Rate is frames per
  MINUTE (OpenTS animtype.cpp delay = TICKS_PER_MINUTE / Rate), _B every step, _C every 2nd, rate 2.
- **Stage B (sections) VERIFIED in play 2026-09-29:** STRUCT_TSFSDF
  "TSFSDF" 1x1, not selectable, insignificant, no build-up, $250, power -2, 200 HP concrete, prereq
  TSFGEN, BaseNormal=no, Adjacent=3 (TS's default reach; GAFSDF sets none). Art `scripts/ts_pack_fsdf.py` (round C, pixel-identical to the approved
  stills; damaged groups repeat the undamaged art for now). Frame = own neighbour sections +16
  damaged +32 live (BuildingClass::Shape_Number). Walkable while `HouseClass::IsFirestormLive` is false
  (the mine/Limpet pattern: Unit/Infantry Can_Enter_Cell + What_Action), sorts under units, doesn't
  keep a player alive. Sections chain from other own sections (display.cpp TF_Section_Chains_To, and the launcher ghost's distance map in
  dllinterface.cpp Calculate_Placement_Distances -- the ghost is the real gate); nothing else may use them
  for adjacency. Sell: only while the field is down, removed at once, no
  refund.
- **Line fill for all walls VERIFIED in play 2026-09-29** (house.cpp TF_Wall_Line_Fill,
  called from Place_Object): sandbags, concrete, barbed wire, wood, chain link, fence, TS wall and
  the Firestorm sections; 5 cells; charged per section at Cost_Of x CostBias; stops when money runs out.
- **Stage C VERIFIED in play 2026-09-29 (all 9 checks):** SPC_TS_FIRESTORM (targeted
  SW_ION_CANNON route, AssetName "SW_TSFire", TS FSTDICON cameo). SuperClass charge-drain (Start_Drain /
  End_Drain / Drain / Restart_Charge; the sidebar clock runs back down while draining; the dev 5 s recharge
  cap and the low-power suspend skip a draining weapon). Full charge -> 1 minute of field; the field drops
  when the drain runs out, the power falls short or the last generator goes, then charges from zero; a
  charge interrupted by low power restarts from zero. A live section takes no damage, each hit drains
  damage/10 frames. EVA 00-I162 ready, 00-I170 offline (scripts/ts_eva_build.py). Live sections draw +32
  and block everyone (Is_Open_Firestorm_Section); killing and projectile stops are stage D.
- **Stage D VERIFIED in play 2026-09-30 (everything not needing an enemy; the enemy-side checks are on the LAN
  test list in main's docs/todo.md):** TF_Firestorm_Burn (house.cpp) each frame kills anything on the house's
  live sections (own units too, WARHEAD_TSFLAMEHIT, forced) and any aircraft over one, the Hunter Seeker
  excepted -- airborne damage is doubled because AircraftClass::Take_Damage halves it (it crept to 1 HP
  otherwise). Shots: BulletClass::AI deletes any projectile in a hostile live cell with a spark, instant
  shots are cut at the first hostile live cell on their path at launch (TF_Firestorm_On_Path); eaten shots
  do not drain (TS). Visuals (scripts/ts_pack_firestorm_fx.py): ANIM_TS_FSIDLE columns flicker up from hubs
  (every 8th frame, 1 in 16, never on straight runs), ANIM_TS_FSGRND at the wall / ANIM_TS_FSAIR at an
  aircraft's height on every crossing. Sound (3c92441f, VERIFIED in play 2026-09-30): every column and crossing plays TS's
  FIRSTRM1 (Report= of FSIDLE/FSGRND/FSAIR), VOC_TS_FIRSTRM1. Next: stage E, correct control, designed with Luke.

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
against the rules' 50 -- see open questions.

**Not in TS:** subterranean units ignore the field; EMP has no special case (it can knock power
out, which suspends the field and resets its charge).

## RA port plan

### Stage A -- the generator (STRUCT_TSFGEN, "TSFGEN")
TS building pipeline (`ts_pack_tree.py`): GTFIRE 3x2 with the _B/_C anims baked into the idle
cycle, GTFIREMK build-up, damaged frame. TS stats; prerequisite TSTECH; power -200; grants
SPC_TS_FIRESTORM. Cameo: TS's FSDICON, TS-badged. Excluded from AI production at first.

### Stage B -- the pads (STRUCT_TSFSDF, "TSFSDF")
1x1 building, one per cell, round C art: 0-15 normal, 16-31 damaged, 32-47 live, 48-63 live
damaged (the damaged sets still to build, as a still for sign-off first). Frame = neighbour bits
over own sections, +32 while live. Passable while inactive (the engine's building-occupies-cell
rule needs a TSFSDF exception), not selectable, not repairable, sell only while inactive.
Prerequisite TSFIRE, cost / power per the open question.

### Stage C -- the superweapon and charge-drain (SPC_TS_FIRESTORM)
RA's SuperClass has charge and power-suspend but no drain: add a drain phase for this special
only (READY -> ON spends the charge over a third of the recharge time, runs out -> charge from zero; power loss or generator loss drops
the field and resets). Activation through the targeted route (click anywhere). Sidebar shows the
drain as the clock running back down. EVA 00-I162 ready, 00-I170 offline (TS SPEECH01).
Hits on a live section drain charge x 0.1 instead of damaging it.

### Stage D -- the field
Live sections: impassable to all (zone recompute on toggle), occupants and entrants die
(FirestormWarhead), aircraft crossing die, hostile projectiles deleted at the wall
(IgnoresFirestorm: the Hunter Seeker), FirestormSparkSys-style death effect. Visuals: +32 frames,
GAFSDF_A on hub pieces, FSIDLE columns at TS's rate, FSGRND/FSAIR on crossings.

### Stage E -- correct control, then the Hunter Seeker
Done: see Status. The Hunter Seeker takes the same click route next.

## Answered (Luke, 2026-09-29)

1. **Friendly fire: TS's rule.** A live section kills your own units that stand on or walk into it,
   and eats allies' shots; only the owner's shots pass.
2. **Aircraft: TS's rule.** Aircraft whose cell is a live section die at any height.
3. **Section cost: $250**, what TS players actually paid (OpenTS's hardcoded value), not the rules'
   $50.
4. **Line fill for ALL walls** (the Modern Wall Building / RA2 / TS behaviour): placing a wall within
   **5 cells** in a straight line of another of your walls of the same type fills the gap when every
   cell between is clear, **charging per section**. Covers sandbags, concrete, TD walls, the TS wall
   and the Firestorm sections. The launcher owns the placement ghost, so the line appears on placing
   the second end (no drag preview). Built after the Firestorm arc, with the gate.
5. **AI:** the generator stays out of AI production for now (TS's AI never raises the field either).

## Queued after this arc

- **Line fill for all walls** (above).
- **Gates for ALL SIX factions** (Luke, 2026-09-29: "all factions can have gates now"). Art v2 in
  `~/Downloads/cnc-gates-hd-v2/cnc-gates-hd/` (same author as the TS GDI wall; README there): TS GDI,
  TS Nod, RA Allies (Gap-Generator pylons, status lights), RA Soviets (Tesla arcs + idle crackle
  frames), TD GDI (quonset barrier + silo towers), TD Nod (laser beams); horizontal 384x128 and
  vertical 128x384, open stages + damaged + destroyed, house-colour trim masks. End pieces join a gate
  to the TS GDI wall or RA's concrete wall (BRIK). Engine: a gate building type per faction and
  orientation (blocks enemies, opens for own units, closes behind), walls count a gate's end cells as
  neighbours and the matching end piece is drawn, trim converted to the remap range. Planned with
  the TS Nod wall (art being drawn from `~/Desktop/ts-nod-walls`).
