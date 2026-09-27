# EMP Pulse Cannon — TS port design + arc tracker

> **⭐ RESUME HERE (2026-09-27 evening: STAGE C BUILT, desktop DLL `0e9d35fe`.)**
> **FIRST THING NEXT SESSION: remind Luke to test the hover settle** (he asked for this):
> fire E.M. Pulse at a Hover MLRS and a Limpet Drone and check (1) in normal hover the whole
> unit, shadow included, bobs smoothly as before; (2) when stunned the bob stops and the hull
> settles 3 px onto a still shadow over ~0.8 s, then lifts back over the last ~0.8 s of the
> 30 s stun. Then sign off stage C.
> Verified in play 2026-09-27: the PLSECAN2 fire sound; vehicles stun, spark and ignore orders;
> buildings stop firing; an Orca on open ground is grounded, one on its pad is untouched (TS),
> one taking off/landing/low crashes; the Pulse Cannon can be built off (`BaseNormal=yes`).
> **Luke's rulings: keep TS rules.** 30 s stun (450 frames, `TechnoClass::EMP_STUN_FRAMES`);
> TS tree only; a stunned power plant still produces power, a stunned (even only) conyard still
> builds, factories keep producing, only conyards spark among buildings, pad-parked aircraft
> are spared. Don't re-offer these as deviations.
> Pulse = `TF_EMPulse` (house.cpp), a port of OpenTS empulse.cpp Create; gates in event.cpp,
> Can_Fire, Can_Player_Move, DriveClass::AI, Try_To_Deploy, Process_Take_Off, radar
> (`Has_Working_Radar`, low-power style), gap/stealth generators, launch site. Sparks =
> `ANIM_TS_EMPFX` (EMP_FX01). Hover units carry split shadows (TSHVR 64-95 via
> `ts_hover_split_shadow.py`, TSLIMP 10-19 via `ts_pack_limpet.py`); the shadow bobs WITH the
> hull (a still shadow read as robotic), only the stun settle moves the hull onto it.
> **Next:** stage D (diggers). OpenTS stuns an underground unit and it makes for the nearest
> ground it can surface on, destroyed only if there is none -- gentler than our
> `Force_Emerge` (surface here or explode). Port TS's version; ask Luke first.
> **Play-testing is on the LINUX DESKTOP** (the local Proton prefix, as main's work uses). The
> branch carries main's work through `9bb430c3` plus the verified fixes also on main (sidebar
> construction-options, TS drop pod squad, bay build-up).
> ⚠️ Rebuilding TFASSETS.MIX in a fresh worktree needs `scripts/_td_tems` copied in first: it
> is gitignored, and `build_tfassets.sh` packs it only if the directory exists, so without it
> the archive silently loses 324 staged terrain iconsets.
> **Stages:** A = building ✓; B = superweapon ✓ verified; C = the pulse (built, hover settle to test: stun timer on
> TechnoClass, every gate, sparkles, aircraft crash); D = diggers
> (`Force_Emerge`, BOOM rule); E = sounds + EVA. Neither the subterranean pair nor this ships
> to the Workshop without the other.

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

**The pulse (OpenTS `empulse.cpp` `EMPulseClass::Create`)**, radius = Spread cells, circle
test `dx*dx+dy*dy <= spread*spread` on cell deltas:
- Aircraft on the ground (IsDown, !In_Air) within `Spread*CELL_LEPTON` of the centre:
  `Crash()`.
- Every object in `LAYER_UNDERGROUND` within the circle: locomotor `Power_Off`, `Stop_Moving`,
  `StunDuration = Duration`, sparkles attached. (Ours: `Force_Emerge()` -- surfaces + stunned
  on a legal cell, DESTROYED under water/rock/building. Luke's rule, overrides TS.)
- Buildings whose centre cell is in the circle: `Power_Off()`, `StunDuration = Duration`,
  radar recalc; limpet mines die; core defenders immune.
- Cell occupants: units and aircraft (any with a locomotor) except the source, plus cyborg
  infantry: locomotor `Power_Off`, `Stop_Moving`, `StunDuration = Duration`, sparkles
  (`EMP_FX01`, LoopCount -1, attached to the object). Visceroids immune. Plain infantry
  UNAFFECTED.
- The cannon itself is `source`, so it is exempt from its own pulse.
- `Update_All`: the pulse object dies after Duration frames (it only marks cells
  `IsAffectedByEMP`; nothing reads that flag in OpenTS -- no lingering field effect).

**Stun consumers (OpenTS)** -- `TechnoClass::StunDuration` counts down in `TechnoClass::AI`;
at 0 a building `Power_On`s and radar recalcs. Gates: every locomotor's `Move_To`/`Process`
(no movement), `Is_Immobilized()`, `BuildingClass::Can_Player_Move`, the building's fire /
production / repair gates (building.cpp 7931/9218/3837), the DEPLOY event, `house.cpp` base
AI skips stunned buildings.

## RA port plan

### Stage A -- building (STRUCT_TSPULS, "TSPULS")
- **Art** (`scripts/ts_pack_emp.py`, TS_ART_DIR = the EMP extraction):
  - Base NAPULS.SHP 6 frames (**snow theatre only** -- SNOW.MIX/ISOSNOW.MIX; decode with
    UNITSNO.PAL) + NAPULS_A 122 frames (idle anim; cannon-head motion on the dome) via
    `build_structure` in `ts_pack_tree.py` (2x2, TSPOWR pattern: TDNUKE donor, 256 canvas,
    stub 48x48). Buildup NAPULSMK 40 frames.
  - **Turret = PULSCAN.VXL** rendered 32 facings at the fleet camera (`--yaw0 90
    --px-per-voxel 12 --elev 32 --hva PULSCAN.HVA`, contract 11 lighting), packed as a
    **sub-object layer** `TSPULST` (32 shapes; the TSPROC fireball-layer mechanism:
    `Techno_Draw_Object_Virtual(shapefile, BodyShape[facing], x, y, ..., "TSPULST")`,
    stub in TFASSETS, tiles in RA_STRUCTURES.XML). Seat = the dome top (TS TurretAnimX=1
    Y=7 ZAdjust=-100 -> dial by eye on the Deck, Luke's sheet loop).
  - Cameo EMPICON (CAMEO.PAL, hq4x, no remap) -> BuildIcon_TS_EMPCannon.
- **Engine:** enum inside the TS tree block (move `STRUCT_TS_TREE_LAST`), `ClassTsPuls`
  cloned from `ClassTsPowr` (2x2, `IsTurretEquipped=false` -- the turret is our layer, RA's
  turret path expects turret frames in the building tileset), `_td_bdonors` -> STRUCT_POWER
  (2x2 donor), `_anims[]` idle line, TF_Building_Scan_Bit, `TsPulseTurret` shapefile
  loaded like `TsRefineryFlame`. Turret facing = `PrimaryFacing`, rotated by the building
  AI at ROT 12 toward `TarCom`/the pending EMP target; idle = DIR_N.
- **Data:** rules.ini [TSPULS] (TS stats; Prerequisite TSRADR; Owner as the TS tree; **Bib=yes --
  Luke: "ensure emp building has a bib"**, the TSPOWR pattern),
  RABUILDABLES entry before the BEGIN marker, ModText rows, `ts_stub_dims.json` merge
  (⚠ `ts_pack_tree.py` REWRITES the manifest with only this run's buildings -- load the
  existing file first).

### Stage B -- superweapon (SPC_TS_EMP)
- `SuperClass` slot: recharge `TICKS_PER_MINUTE * 4.5` (4 min 30 s), powered, voices
  VOX_TS_EMP_CHARGING (00-I158) / ready / not-ready / low-power (TS has only the recharge
  line; ready/others reuse RA's generic lines or stay silent -- exactness check).
- House AI: enable when a TSPULS is active (Ion pattern house.cpp 2481-2520), remove when
  gone, `Special_Weapon_AI` picks the densest enemy vehicle/base cluster.
- Launcher routing (`dllinterface.cpp` Convert_Special_Weapon_Type): `dll_weapon_type =
  SW_ION_CANNON` (targeting cursor); `AssetName "SW_TSEmp"` -> RABUILDABLES `RA_SW_TSEMP`
  with BuildIcon_TS_EMP (PulsIcon art) and TS text "E.M. Pulse". Cost-suppression caveat
  as the Ion Cannon.
- Discharge (`house.cpp` Place_Special_Blast case): find the house's TSPULS in range
  (Range 40 cells ~ map-wide; TS picks the nearest powered cannon), set its `EMPDest`,
  building turns its turret to the target and fires `WEAPON_TSEMP` -> `BULLET_TSPULSBALL`
  (Arcing, High, PULSBALL 23 frames animated, Speed 25) at the cell; on impact the
  warhead `WARHEAD_EMPULS` (Spread 11, TF `IsEMP` flag) creates the pulse instead of damage.

### Stage C -- the pulse + stun (built 2026-09-27, see the resume block)
- `TechnoClass::StunDuration` + `Is_Immobilized()`, counted down in `TechnoClass::AI`; at 0 the
  sparks end and a harvester goes back to harvesting (OpenTS techno.cpp AI).
- `TF_EMPulse(cell, source)` (house.cpp), OpenTS empulse.cpp Create: aircraft at
  0 < Height < 104 crash; within Spread 11 a cell's building (only, when it has one) is stunned
  or, if a Limpet Mine, destroyed; otherwise its vehicles, ships and height-0 aircraft are
  stunned, their navigation cleared, sparks attached. Infantry untouched (TS: cyborgs only, we
  have none). Underground units skipped until stage D.
- Gates: MEGAMISSION / IDLE / SCATTER / PRIMARY events ignored; `Can_Fire` FIRE_CANT;
  `Can_Player_Move` false; `DriveClass::AI` finishes the current cell then holds;
  `Try_To_Deploy` and `Process_Take_Off` refuse; radar off like low power; gap and stealth
  generators off; a stunned cannon can't be the launch site.
- TS rules kept (Luke): no power loss, construction and production carry on, only conyards
  spark, pad-parked aircraft spared.

### Stage D -- diggers
- Already built on `subterranean`: `UnitClass::Force_Emerge()` (legal cell -> surface +
  stun; water/rock/building -> `Tunnel_Explode`). Wire from the pulse sweep. DIRTEXPL
  (15 frames, 31x25, extracted) = the muffled underground death burst.

### Stage E -- audio
- PLSECAN2 (cannon fire) + 00-I158 (EVA recharge) extracted; dormant-host recipe as
  FLAMTNK1/SUBDRIL1 (docs/td-audio-routing-recipe.md; hosts census in the 08-28 session).

## Art inventory (extracted 2026-08-28, scratch `subterranean/emp/`)
NAPULS.SHP 6f 96x96, NAPULS_A.SHP 122f, NAPULSMK.SHP 40f (ISOSNOW), PULSCAN.VXL/HVA (LOCAL),
EMPICON.SHP (SIDEC01/02), PULSEFX1.SHP 21f 302x175, PULSEFX2.SHP 15f, EMP_FX01.SHP 27f
36x35, PULSBALL.SHP 23f 14x14, UNITSNO.PAL, PLSECAN2.AUD, 00-I158.AUD. No PULSCANBARL voxel
exists (PBarrelLength is a fire-origin offset only). Re-extract via tools/ts_extract.py.

## Open questions for Luke
- Tech placement: TS = Nod+GDI behind Radar; ours = TS tree behind TSRADR? Or Nod-faction
  (TD Nod) too?
- Stun duration feel (1200 frames = 80 s at RA's 15 fps; TS felt ~40-60 s).
- Plain infantry immune (TS) -- keep.
