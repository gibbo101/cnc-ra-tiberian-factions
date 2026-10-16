# Unit values survey for tf_rules.ini (Tiberian Factions, main 58788a2f)

Read-only survey. "Proven" = read in source; "inferred" = reasoned from it.

## 1. Keys each Read_INI reads

Every Get_* passes the current value as default, so a key absent from a file leaves the value as it was (proven).

**TechnoTypeClass::Read_INI** (redalert/techno.cpp:7956-8050), shared by every unit, infantry, vessel, aircraft and building:
Name, DoubleOwned, GuardRange, Explodes, Primary, Secondary, Cloakable, Crushable, Sensors, Armor, Prerequisite,
Strength, Sight, TechLevel, Speed, Cost, Ammo, Points (sets Risk, Reward and Points), Owner, Crewed, Repairable,
Invisible, SelfHealing, ROT, Passengers, Image. Then IsLeader and MZone are derived from Primary (8034-8052).
VesselTypeClass and AircraftTypeClass have no Read_INI of their own (proven: none in vdata.cpp/aadata.cpp; type.h).

**UnitTypeClass** (udata.cpp:2783): NoMovingFire, WalkFrames, WalkFacings, DeployToFire, DeployFrames, DeployRate,
FiringFrames, WalkRate, Tracked, TF Amphibious, TF Hover.
**InfantryTypeClass** (idata.cpp:2100): Fraidycat, Fearless, Infiltrate, C4, IsCanine.
**BuildingTypeClass** (bdata.cpp:6254-6371): WaterBound, Storage, Adjacent, Capturable, Powered, Bib, Unsellable,
BaseNormal, Power, TF Footprint, ShapeSize, IdleAnim*/ActiveAnim*/BuildupAnim* (Count/Start/Rate).
**WeaponTypeClass** (weapon.cpp:200): Supress, Burst, Damage, Speed, ROF, Range, MinimumRange, Report, Anim, Camera,
Charges, TurboBoost, IsRailgun, IsSonic, IsPrismBeam, AmbientDamage, Warhead, Projectile.
**WarheadTypeClass** (warhead.cpp:161): Spread, LimpetFactor, Wall, Wood, Ore, Explosion, InfDeath, ProneDamage, Verses.
**BulletTypeClass** (bbdata.cpp:354): Arm, ROT, Frames, High, Shadow, Arcing, Dropping, Inviso, Proximity, Animates,
Ranged, Inaccuate/Inaccurate, AA, AG, ASW, Degenerates, UnderWater, Parachuted, Rotates, Translucent, Gigundo,
TF Homing, Warhead, ImpactAnim, BulletRange, Image.

### Proposed player-facing set
- All technos: Cost, Strength, Armor (none/wood/light/heavy/concrete picker), Sight, Points (AI value only, optional).
- Mobile (unit/infantry/vessel/aircraft): Speed, ROT (not infantry), Passengers only where it is already non-zero.
- Aircraft: Ammo.
- Buildings: Power (signed), Storage (refineries/silos only).
- Weapon (via the unit's Primary/Secondary, shown read-only by name): Damage, ROF, Range, Burst; AmbientDamage for the
  IsRailgun/IsSonic/IsPrismBeam weapons (they deal AmbientDamage, not Damage: techno.cpp:4062, 4097-4130).
- Warhead (advanced tab only): Verses, Spread.

### Bounds the UI must enforce (proven unless noted)
- Strength >= 10: Repair_Cost divides by MaxStrength / RepairStep(7) or URepairStep(10) (techno.cpp:7860-7862);
  a smaller value divides by zero. MaxStrength is unsigned short but ObjectClass::Strength is short (object.h:128),
  so cap at 32767, and at 16383 for TD* buildings (doubled, see section 2).
- Sight 1..10: MapClass::Sight_From returns early for 0 or > 10 (map.cpp:590), so 11+ reveals nothing. TD* buildings get +3, so 1..7.
- Speed 0..100: _Scale_To_256 clamps (techno.cpp:7930).
- Weapon ROF >= 1: AI threat code divides by ROF (techno.cpp:7332, 7373, 7415). Weapon Speed >= 1 (bullet.cpp:1476, 1605 divide by it).
- Verses must hold all 5 values; a missing one parses as 0% (fixed(NULL) = 0, common/fixed.cpp:89), and steel 0% flips IsOrganic (warhead.cpp:185).
- Power: Read_INI sets Drain only when Power < 0 and never clears it (bdata.cpp:6276, 6369-6372). Flipping a drain building to
  positive leaves both Power and the old Drain (proven by reading; not run). The editor should write a sign-preserving value.

### Dangerous keys (do not expose)
- Primary / Secondary / Warhead / Projectile: pointer swaps. An unknown weapon name resolves to WEAPON_NONE and strips the
  weapon (ccini.cpp:650, weapon.cpp:263); MZone is raised to DESTROYER and never lowered (techno.cpp:8044).
- Owner, TechLevel, Prerequisite, DoubleOwned: tech tree, faction gating, TechLevel=99 hides cameos.
- Image, Name, ShapeSize, Footprint, *Anim*, WalkFrames etc., Bib, Report, Anim: art/launcher contracts.
- Tracked, Hover, Amphibious, WaterBound, Cloakable, Invisible, Sensors, C4, Infiltrate, IsCanine, IsRailgun/IsSonic/IsPrismBeam, Charges, Camera.
- Heaps: no lookup allocates. Heap_Maximums (rules.cpp:599) runs only from Rule.Process at init (init.cpp:283, 291) and creates
  every weapon/warhead/bullet by code; Get_WeaponType/Get_WarheadType/Get_BulletType only search (ccini.cpp:650, 705, 818).
  A [Maximums] section in tf_rules.ini would be ignored per match (Objects pass doesn't call Heap_Maximums).

## 2. C++ that writes type stats after rules load
- bdata.cpp:6262-6267 TD* buildings: MaxStrength *= 2, SightRange += 3 on EVERY Read_INI pass where the section is present.
  rules.ini gives all 116 TD* sections Strength and Sight, so the rules pass re-bases them; a tf_rules.ini section for a TD
  building doubles again: Strength=800 becomes 1600, and a section without Strength gives 4x listed and Sight +6. Same for a map INI naming one.
- bdata.cpp:6258 TDBLOSSOM IsImmune = true.
- scenario.cpp:2722 Sniper Burst = 2 for scu35ea/scu47ea (EA, after rules; overrides a player Burst there).
- scenario.cpp:2347-2359 EA fixups (Flamer sound, Spy weapons NULL, ant Levels) run BEFORE the rules passes, so rules win.
- techno.cpp:3513-3519 IsTDPort weapons: the first shot of a salvo waits 9 frames whatever ROF says; ROF applies only after the second shot.
- weapon.cpp:207 IsTDPort weapons read Speed as raw MPHType (0-255), RA weapons as a percentage: the UI must know which.
- anim.cpp:1223-1231 Ion Cannon (TD and TS): hardcoded 600 damage (300 adjacent for TS), TDPB warhead.
- bullet.cpp:961 failed drop pod: 100 HE. map.cpp:590 sight cap 10. techno.cpp PRISM_FORK_RANGE constant.
- bdata.cpp:6152-6171 Raw_Cost of refineries subtracts the harvester's Cost (RA/TD/TS), and helipads the Hind/Longbow;
  techno.cpp:7676-7695 GDI/Nod build time uses that net cost. Editing a harvester's Cost changes refinery price/sell/build time (coupling, not override).
- house.cpp:285-289 per-house FirepowerBias/ArmorBias/ROFBias/GroundspeedBias from HouseType and difficulty multiply on top (expected).
# Unit values survey (Tiberian Factions, main 58788a2f)

Merged view: rules.ini overlaid by aftrmath.ini. Types = sections whose name matches an IniName in bdata/udata/idata/vdata/aadata.cpp. Format TYPE(kind[,sec];Owner).

## Weapons shared by more than one type

- **DepthCharge** [Damage=80 ROF=60 Range=5 WH=AP] used by 5: DD(V,sec;allies), PT(V,sec;allies), TDBOAT(V,sec;GoodGuy), TDDD(V,sec;GoodGuy), TDPT(V,sec;GoodGuy)
- **Pistol** [Damage=1 ROF=7 Range=1.75 WH=SA] used by 4: C1(I;allies,soviet), C7(I;allies,soviet), DELPHI(I;allies,soviet), GNRL(I;allies,soviet)
- **8Inch** [Damage=500 ROF=160 Range=22 WH=HE] used by 4: CA(V;allies), CA(V,sec;allies), TDCA(V;GoodGuy), TDCA(V,sec;GoodGuy)
- **ChainGun** [Damage=40 ROF=3 Range=5 WH=SA] used by 3: HIND(A;soviet), YAK(A;soviet), YAK(A,sec;soviet)
- **TDM60mg** [Damage=15 ROF=30 Range=4 WH=TDSA] used by 3: TDAPC(U;GoodGuy), TDBGGY(U;BadGuy), TDJEEP(U;GoodGuy)
- **105mm** [Damage=30 ROF=70 Range=4.75 WH=AP] used by 2: 3TNK(U;soviet), 3TNK(U,sec;soviet)
- **ZSU-23** [Damage=25 ROF=10 Range=6 WH=AP] used by 2: AGUN(B;allies), AGUN(B,sec;allies)
- **M60mg** [Damage=15 ROF=20 Range=4 WH=SA] used by 2: APC(U;allies), JEEP(U;allies)
- **APTusk** [Damage=75 ROF=80 Range=5 WH=AP] used by 2: CTNK(U;allies), STNK(U;allies,soviet)
- **Stinger** [Damage=30 ROF=60 Range=9 WH=AP] used by 2: DD(V;allies), TDDD(V;GoodGuy)
- **Colt45** [Damage=75 ROF=5 Range=5.75 WH=HollowPoint] used by 2: E7(I;allies,soviet), E7(I,sec;allies,soviet)
- **Vulcan** [Damage=40 ROF=40 Range=5 WH=SA] used by 2: HBOX(B;allies), PBOX(B;allies)
- **Hellfire** [Damage=40 ROF=60 Range=4 WH=AP] used by 2: HELI(A;allies), HELI(A,sec;allies)
- **Maverick** [Damage=50 ROF=3 Range=6 WH=AP] used by 2: MIG(A;soviet), MIG(A,sec;soviet)
- **SubSCUD** [Damage=400 ROF=120 Range=14 WH=HE] used by 2: MSUB(V;soviet), TDMSUB(V;BadGuy)
- **2Inch** [Damage=25 ROF=60 Range=5.5 WH=AP] used by 2: PT(V;allies), TDPT(V;GoodGuy)
- **TorpTube** [Damage=90 ROF=60 Range=9 WH=AP] used by 2: SS(V;soviet), TDNSUB(V;BadGuy)
- **TDA10Napalm** [Damage=100 ROF=20 Range=4.5 WH=TDFire] used by 2: TDA10(A;GoodGuy), TDA10(A,sec;GoodGuy)
- **TDDragon** [Damage=30 ROF=60 Range=4 WH=TDAP] used by 2: TDBIKE(U;BadGuy), TDE3(I;GoodGuy,BadGuy)
- **TDChemspray** [Damage=80 ROF=70 Range=2 WH=TDChemWar] used by 2: TDE5(I;BadGuy), TDVICE(U;GoodGuy,BadGuy,Neutral)
- **TDStnkDragon** [Damage=30 ROF=60 Range=4 WH=TDAP] used by 2: TDORCA(A;GoodGuy), TDSTNK(U;BadGuy)
- **TS90mm** [Damage=36 ROF=50 Range=6.75 WH=TSAP] used by 2: TSTICK(B;allies,soviet,GoodGuy,BadGuy,Germany), TSTTNK(U;allies,soviet,GoodGuy,BadGuy,Germany)

## Weapons used by exactly one type

- 120mm: 4TNK(U;soviet)
- 155mm: ARTY(U;allies)
- 75mm: 1TNK(U;allies)
- 90mm: 2TNK(U;allies)
- AirAssault: CARR(V;GoodGuy)
- AssaultCannon: TSSMEC(U;allies,soviet,GoodGuy,BadGuy,Germany)
- C3Mk3Cannon: C3MK3(U;allies,soviet,GoodGuy,BadGuy,Germany)
- C3Mk3Pods: C3MK3(U,sec;allies,soviet,GoodGuy,BadGuy,Germany)
- C3PredCannon: C3PRED(U;allies,soviet,GoodGuy,BadGuy,Germany)
- Camera: U2(A;soviet)
- Democharge: DTRK(U;allies,soviet)
- DogJaw: DOG(I;soviet)
- Dragon: E3(I,sec;allies,soviet)
- FireballLauncher: FTUR(B;soviet)
- Flamer: E4(I;soviet)
- GoodWrench: MECH(I;allies)
- Grenade: E2(I;soviet)
- Heal: MEDI(I;allies)
- M1Carbine: E1(I;allies,soviet)
- MammothTusk: 4TNK(U,sec;soviet)
- MechRailgun: TSHMEC(U;allies,soviet,GoodGuy,BadGuy,Germany)
- Nike: SAM(B;soviet)
- ParaBomb: BADR(A;soviet)
- PortaTesla: SHOK(I;soviet)
- R2ApocCannon: R2APOC(U;allies,soviet,GoodGuy,BadGuy,Germany)
- R2ApocTusk: R2APOC(U,sec;allies,soviet,GoodGuy,BadGuy,Germany)
- R2PrismBeam: R2PRIS(U;allies,soviet,GoodGuy,BadGuy,Germany)
- RedEye: E3(I;allies,soviet)
- SCUD: V2RL(U;soviet)
- SonicZap: TSSONIC(U;allies,soviet,GoodGuy,BadGuy,Germany)
- TD105mm: TDMTNK(U;GoodGuy)
- TD120mm: TDHTNK(U;GoodGuy)
- TD155mm: TDARTY(U;BadGuy)
- TD75mm: TDLTNK(U;BadGuy)
- TDApacheGun: TDHELI(A;BadGuy)
- TDChainGun: TDGTWR(B;GoodGuy)
- TDFlameBunker: TDFBNK(B;BadGuy)
- TDFlameTongue: TDFTNK(U;BadGuy)
- TDFlamethrower: TDE4(I;BadGuy)
- TDGrenade: TDE2(I;GoodGuy)
- TDHonestJohn: TDMSAM(U;BadGuy)
- TDM16: TDE1(I;GoodGuy,BadGuy)
- TDMlrsRocket: TDMLRS(U;GoodGuy)
- TDNike: TDSAM(B;BadGuy)
- TDObeliskSubLaser: TDOBLISUB(V;BadGuy)
- TDOblsLaser: TDOBLI(B;BadGuy)
- TDRifle: TDRMBO(I;GoodGuy,BadGuy)
- TDTomahawk: TDBOAT(V;GoodGuy)
- TDTowTwo: TDATWR(B;GoodGuy)
- TDTurretGun: TDGUN(B;BadGuy)
- TDTusk: TDHTNK(U,sec;GoodGuy)
- TS120mm: TSTITN(U;allies,soviet,GoodGuy,BadGuy,Germany)
- TS120mmx: TS4TNK(U;allies,soviet,GoodGuy,BadGuy,Germany)
- TS4TNKTusk: TS4TNK(U,sec;allies,soviet,GoodGuy,BadGuy,Germany)
- TSBazooka: TSE3(I;allies,soviet,GoodGuy,BadGuy,Germany)
- TSBomb: TSORCAB(A;allies,soviet,GoodGuy,BadGuy,Germany)
- TSFireball: TSSUBTANK(U;allies,soviet,GoodGuy,BadGuy,Germany)
- TSGrenade: TSE2(I;allies,soviet,GoodGuy,BadGuy,Germany)
- TSHeal: TSMEDIC(I;allies,soviet,GoodGuy,BadGuy,Germany)
- TSHellfire: TSORCA(A;allies,soviet,GoodGuy,BadGuy,Germany)
- TSHoverMissile: TSHVR(U;allies,soviet,GoodGuy,BadGuy,Germany)
- TSJugg90mm: TSJUGG(U;allies,soviet,GoodGuy,BadGuy,Germany)
- TSJumpCannon: TSJUMPJET(I;allies,soviet,GoodGuy,BadGuy,Germany)
- TSLimpet: TSDLIMP(B;allies,soviet,GoodGuy,BadGuy,Germany)
- TSLtRail: TSGHOST(I;allies,soviet,GoodGuy,BadGuy,Germany)
- TSMammothTusk: TSHMEC(U,sec;allies,soviet,GoodGuy,BadGuy,Germany)
- TSMinigun: TSE1(I;allies,soviet,GoodGuy,BadGuy,Germany)
- TSRPGTower: TSROCK(B;allies,soviet,GoodGuy,BadGuy,Germany)
- TSRedEye2: TSCSAM(B;allies,soviet,GoodGuy,BadGuy,Germany)
- TSSuicide: TSHUNT(A;GoodGuy,Germany)
- TSVulcanTower: TSVULC(B;allies,soviet,GoodGuy,BadGuy,Germany)
- TTankZap: TTNK(U;soviet)
- TeslaZap: TSLA(B;soviet)
- TurretGun: GUN(B;allies)

## Heap weapons no type names as Primary/Secondary (used from C++ or unused)

Sniper, Napalm, Mandible

## Warheads shared by more than one weapon

- **AP** (21): ZSU-23, Maverick, Dragon, Hellfire, 75mm, 90mm, 105mm, 120mm, TurretGun, Nike, Stinger, TorpTube, 2Inch, DepthCharge, RedEye, APTusk, TSMammothTusk, TS4TNKTusk, R2ApocTusk, C3Mk3Cannon, C3PredCannon
- **TDAP** (11): TDTurretGun, TDNike, TDDragon, TD105mm, TD75mm, TD120mm, TDStnkDragon, TDTomahawk, TSHoverMissile, TS120mm, TS120mmx
- **HE** (8): Grenade, MammothTusk, 155mm, 8Inch, ParaBomb, SCUD, SubSCUD, C3Mk3Pods
- **Super** (6): Camera, TeslaZap, PortaTesla, TTankZap, AirAssault, TSSuicide
- **TDHE** (6): TDChainGun, TDGrenade, TDTusk, TDMlrsRocket, TD155mm, TDApacheGun
- **SA** (5): Vulcan, ChainGun, Pistol, M1Carbine, M60mg
- **TDFire** (4): TDFlamethrower, TDFlameTongue, TDA10Napalm, TDFlameBunker
- **TSSA** (4): AssaultCannon, TSVulcanTower, TSMinigun, TSJumpCannon
- **Fire** (3): FireballLauncher, Napalm, Flamer
- **Organic** (3): DogJaw, Heal, TSHeal
- **HollowPoint** (2): Colt45, Sniper
- **TDLaser** (2): TDOblsLaser, TDObeliskSubLaser
- **TDSA** (2): TDM16, TDM60mg
- **TSAP** (2): TS90mm, TSBazooka

## Primary/Secondary naming a weapon not in the heap (resolves to WEAPON_NONE)

none

## 4. Keys absent from merged rules.ini+aftrmath.ini (an override of these leaks into the next match)
Rule.Objects only rewrites keys present in the file; nothing restores constructor defaults (rules.cpp:1070-1110, all Get_* default to the current value).
- Secondary: missing on 54 units, 37 infantry, 13 aircraft, 8 vessels, 159 buildings.
- Ammo: missing on 59 units, 37 infantry, all 15 vessels, 3 aircraft (TDC17, TDC17P, TRAN).
- GuardRange: missing almost everywhere. ROT: missing on all infantry. Power: missing on 50 buildings (walls, civilians, MISS...).
- Cost missing on 44 buildings (civilian V*, barrels, mines, MISS, TDBLOSSOM); Sight missing on 42 buildings (same group).
- Weapons: Burst missing on 72, MinimumRange on 96, AmbientDamage on 94. Damage/ROF/Range present on all coded weapons except Mandible (no section).
- Present on every type: Strength, Armor (bar 7 civil objects), Speed (mobile), Sight (mobile), Cost (buildable), Primary on armed types.
