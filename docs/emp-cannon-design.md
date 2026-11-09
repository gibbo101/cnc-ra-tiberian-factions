# EMP Pulse Cannon

**Status:** Reference; shipped in 5.0.0.

The EMP Cannon (`STRUCT_TSPULS`, superweapon `SPC_TS_EMP`) and the Mobile EMP stun for 30 s and
10 s within 3 cells under TS rules, and a stunned digger surfaces at the nearest ground or is
destroyed if there is none. The out-of-range targeting cursor can't be shown from the DLL (the field manual's
[EMP and stun](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/behaviours/emp-and-stun.md#traps), traps). This doc also records the Mobile
Sensor Array and the Mobile War Factory, built in the same arc. Pairs with
`subterranean-design.md`.

## What ships

- **The pulse** is `TF_EMPulse` (`house.cpp`), a port of OpenTS `empulse.cpp` Create, called by
  the cannon's bullet (`EMP_CANNON_SPREAD` = 3, `TechnoClass::EMP_STUN_FRAMES` = 450) and the
  Mobile EMP (`EMP_MOBILE_SPREAD` = 3, `EMP_MOBILE_STUN_FRAMES` = 150). Aircraft between 0 and 104
  Height crash; a cell's building (only, when it has one) is stunned, or destroyed if it is a
  Limpet Mine; otherwise its vehicles, ships and grounded aircraft are stunned, their navigation
  cleared and sparks attached (`ANIM_TS_EMPFX`, EMP_FX01). Infantry are untouched (TS stuns
  cyborgs only, and we have none).
- **Stun gates:** the field manual's
  [EMP and stun](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/behaviours/emp-and-stun.md#the-method-in-red-alerts-dll)
  item 3, in TF's event handling, `Can_Fire` (`FIRE_CANT`), `Can_Player_Move`, `DriveClass::AI`, `Try_To_Deploy`
  and `Process_Take_Off`; a stunned cannon also can't be the launch site.
- **TS rules kept:** a stunned power plant, yard and factory keep working (the field manual's
  [EMP and stun](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/behaviours/emp-and-stun.md#the-method-in-red-alerts-dll), item 4).
  Pad-parked aircraft are spared because a building's cell skips the occupant pass: a TF rule, since
  OpenTS's aircraft pass has no building test.
- **Building sparks differ from TS:** TF sparks only construction yards (`Is_Construction_Yard`);
  TS sparks only deployed mobile units, never the yard (the manual's TS section lists them).
- **Hover units carry split shadows** (TSHVR shapes 64-95, TSLIMP 10-19, packed by
  `ts_pack_hd_buildings.py`). The shadow bobs with the hull; only a stun settles the hull 3 px
  onto a still shadow over ~0.8 s, lifting back over the stun's last ~0.8 s.
- **Diggers (stage D):** a stunned digger reroutes to `Find_Emerge_Cell` (OpenTS `empulse.cpp` +
  `tunnel.cpp` Stop_Moving), explodes if there is none, and carries on if it is within a cell's
  diagonal of its destination; it keeps moving (TS's tunnel `Process` ignores power) but ignores
  new dig orders. Sparks start on surfacing.
- **Audio:** PLSECAN2 on fire; EVA "E.M. pulse cannon ready" (`00-I158`) only, as in TS. Dev
  builds recharge superweapons in 5 s (`SuperClass::Cap_Recharge`); the Mobile EMP stays on its
  real timer.
- ⚠️ Rebuilding TFASSETS.MIX in a fresh worktree needs the gitignored `scripts/_td_tems`: run
  `scripts/td_templates.py` first, since `build_tfassets.sh` refuses to pack while any of its 438 TD iconsets is
  missing.

## Decisions

**EMP Cannon:** blast radius **3 cells** (TS says 11; 11 swallowed a whole RA base, and 3 is what
the PULSEFX ring covers on screen: what the ring covers is what gets stunned). Stun **30 s**.
Charging and not-ready stay silent, as in TS.

**Mobile EMP (`UNIT_TSMEMP`):** radius **3** (its MEMPFX blast art), stun **10 s**, charge **87 s** = TS's real time (FS MaxCharge 1800 at TS Medium speed). Friendly fire
kept. No pre-charged variant. The AI doesn't build it until it has discharge logic.

**Mobile Sensor Array (`UNIT_TSLPST` -> `STRUCT_TSDPSA`):** radius 25 (TS, may need tuning like
the EMP). Cloaked and buried enemies in range are shown to the sensor's owner as ghost copies,
**never decloaked**, by the method in the field manual's
[EMP and stun](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/behaviours/emp-and-stun.md#showing-hidden-enemies-without-decloaking-them). EVA "cloaked unit detected" / "subterranean unit
detected" with a radar ping, 15 s apart per line. Deployed: not repairable, drag-selectable,
box 35x36, PLACE2 on deploy and pack-up. Fallback if ghosts ever misbehave: decloak everything
in range, buildings too.

**Mobile War Factory (`UNIT_TSMWAR` -> `STRUCT_TSDWEAP`):** one at a time,
deployed or not, locked cameo with the red X. Deployed = a TS war factory to the code
(`Is_TS_War_Factory`) on the War Factory's 3x3 plot; satisfies War Factory
prerequisites (Firestorm PrerequisiteFactory). Pack-up is the deploy key only; self-click =
primary, move = rally point. The doorway layering is verified in play.

**Art habits:** a labelled facings sheet is reviewed before a unit goes in game; building geometry
is settled on a sheet first. Dark-remap TS hulls need a stronger team
green (MWF 0,560,0, LPST 0,380,0; they plateau near 160 against the APC's 185).

## TS ground truth (live-extracted TIBSUN.MIX rules/art + OpenTS)

**Building `[NAPULS]`** (rules.ini 4827): Strength 500, Armor heavy, Prerequisite Radar,
TechLevel 6, Sight 8, Adjacent 2, Owner Nod+GDI, Cost 1000, Turret=yes, ROT 12, Power -150,
Sensors=yes, Crewed, Points 50, `EMPulseCannon=yes`, `SuperWeapon=EMPulseSpecial`,
`Primary=EMPulseWeapon`, TurretAnim=PULSCAN (voxel, TurretAnimX=1 Y=7 ZAdjust=-100).
Art (art.ini 1074): Foundation 2x2, Cameo EMPICON, `PrimaryFireFLH=0,0,80`,
PBarrelLength 110, Buildup NAPULSMK.

**Superweapon `[EMPulseSpecial]`**: RechargeTime 4.5 (minutes), IsPowered, RechargeVoice
`00-I158`, Type=EMPulse, SidebarImage PulsIcon.

**Weapon `[EMPulseWeapon]`**: Damage 1200 (= DURATION of the pulse in frames), ROF 1, Speed 25,
Range 40, Lobber, Projectile `PulsPr` (High, Image PULSBALL), Warhead `EMPuls` (Spread 11 =
radius in cells, `EMEffect=yes`, AnimList PULSEFX1,PULSEFX2), Report PLSECAN2.
`[AudioVisual] EMPulseSparkles=EMP_FX01`.

**The pulse** is OpenTS `empulse.cpp` `EMPulseClass::Create`; the field manual's
[EMP and stun](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/behaviours/emp-and-stun.md#how-tiberian-sun-does-it) has what it does
(the circle, the aircraft pass, underground units, buildings, occupants, the exempt firer, no lingering field).
Each `LAYER_UNDERGROUND` object and each cell occupant gets locomotor `Power_Off`, `Stop_Moving` and
`StunDuration = Duration`; a stunned building also recalculates radar; the pulse object dies after Duration frames
(`Update_All`). Ours follows it except where What ships says otherwise.

**Stun consumers (OpenTS)** -- `TechnoClass::StunDuration` counts down in `TechnoClass::AI`;
at 0 a building `Power_On`s and radar recalcs. Gates: every locomotor's `Move_To`/`Process`
(no movement), `Is_Immobilized()`, `BuildingClass::Can_Player_Move`, `BuildingClass::Turn_On`
(refuses while stunned, building.cpp 7931), `Is_Powered_On` (false while stunned, 9218), `What_Action`'s
set-primary-factory branch (refused while stunned, 3837), the DEPLOY event, `house.cpp` base
AI skips stunned buildings. Production isn't gated: a stunned factory keeps producing, since the factory
tests read `IsOn`, which the pulse leaves set, and never `Is_Powered_On`.

## How it is built

### The building (STRUCT_TSPULS, "TSPULS")
- **Art** (`scripts/ts_pack_emp.py`, TS_ART_DIR = the EMP extraction):
  - Base NAPULS.SHP 6 frames (**snow theatre only** -- SNOW.MIX/ISOSNOW.MIX; decode with
    UNITSNO.PAL) + NAPULS_A 122 frames (idle anim; cannon-head motion on the dome) via
    `build_structure` in `ts_pack_tree.py` (2x2, the TSPOWR pattern, 256 canvas, stub 48x48). Buildup NAPULSMK 40 frames.
  - **Turret = PULSCAN.VXL** rendered 32 facings at the fleet camera (`--yaw0 90
    --px-per-voxel 12 --elev 32 --hva PULSCAN.HVA`, the lighting of `launcher-render-contracts.md` §11), packed as a
    **sub-object layer** `TSPULST` (32 shapes; the TSPROC fireball-layer mechanism:
    `Techno_Draw_Object_Virtual(shapefile, BodyShape[facing], x, y, ..., "TSPULST")`,
    stub in TFASSETS, tiles in RA_STRUCTURES.XML). Seat = the dome top (TS TurretAnimX=1
    Y=7 ZAdjust=-100, dialled by eye from a sheet).
  - Cameo EMPICON (CAMEO.PAL, hq4x, no remap) -> BuildIcon_TS_EMPCannon.
- **Engine:** enum inside the TS tree block (move `STRUCT_TS_TREE_LAST`), `ClassTsPuls`
  cloned from `ClassTsPowr` (2x2, `IsTurretEquipped=false` -- the turret is our layer, RA's
  turret path expects turret frames in the building tileset), `_td_bdonors` -> STRUCT_POWER
  (2x2 donor), `_anims[]` idle line, TF_Building_Scan_Bit, `TsPulseTurret` shapefile
  loaded like `TsRefineryFlame`. Turret facing = `PrimaryFacing`, rotated by the building
  AI at ROT 12 toward `TarCom`/the pending EMP target; idle = DIR_N.
- **Data:** rules.ini [TSPULS] (TS stats; Prerequisite TSRADR; Owner as the TS tree; `Bib=yes`, the
  TSPOWR pattern),
  RABUILDABLES entry before the BEGIN marker, ModText rows, `ts_stub_dims.json` merge
  (⚠ `ts_pack_tree.py` REWRITES the manifest with only this run's buildings -- load the
  existing file first).

### The superweapon (SPC_TS_EMP)
- `SuperClass` slot: recharge `TICKS_PER_MINUTE * 4.5` (4 min 30 s), powered; EVA is TS's one
  line, `00-I158`.
- House AI: enable when a TSPULS is active (Ion pattern house.cpp 2481-2520), remove when
  gone, `Special_Weapon_AI` picks the densest enemy vehicle/base cluster.
- Launcher routing (`dllinterface.cpp` Convert_Special_Weapon_Type, as in the field manual's
  [Air delivery and fleets](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/behaviours/air-delivery-and-fleets.md#support-powers)):
  `SW_ION_CANNON`; `AssetName "SW_TSEmp"` -> RABUILDABLES `RA_SW_TSEMP` with BuildIcon_TS_EMP
  (PulsIcon art) and TS text "E.M. Pulse".
- Discharge (`house.cpp` Place_Special_Blast case): find the house's TSPULS in range
  (Range 40 cells ~ map-wide; TS picks the nearest powered cannon), set its `EMPDest`,
  building turns its turret to the target and fires `WEAPON_TSEMP` -> `BULLET_TSPULSBALL`
  (Arcing, High, PULSBALL 23 frames animated, Speed 25) at the cell; on impact the
  warhead `WARHEAD_EMPULS` (TF `IsEMP` flag) creates the pulse instead of damage, over 3 cells
  (`EMP_CANNON_SPREAD` in `bullet.cpp`; TS's Spread is 11).

### The pulse, the stun and diggers
- What ships has the pulse and stun. `TF_EMPulse` stuns every tunnelling unit in the spread and calls
  `Tunnel_Stop`, which does what What ships describes (diggers).

### Audio
- PLSECAN2 (cannon fire) and 00-I158 (EVA) extracted from TS and shipped under their own names
  (`td-audio-routing-recipe.md`, `scripts/ts_eva_build.py`).

## Art inventory (scratch `subterranean/emp/`)
NAPULS.SHP 6f 96x96, NAPULS_A.SHP 122f, NAPULSMK.SHP 40f (ISOSNOW), PULSCAN.VXL/HVA (LOCAL),
EMPICON.SHP (SIDEC01/02), PULSEFX1.SHP 21f 302x175, PULSEFX2.SHP 15f, EMP_FX01.SHP 27f
36x35, PULSBALL.SHP 23f 14x14, UNITSNO.PAL, PLSECAN2.AUD, 00-I158.AUD. No PULSCANBARL voxel
exists (PBarrelLength is a fire-origin offset only). Re-extract via tools/ts_extract.py.
