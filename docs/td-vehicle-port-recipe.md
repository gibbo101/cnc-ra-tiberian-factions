# TD Vehicle Port Recipe

**Status:** Reference. The pipeline for porting a TD vehicle; every TD vehicle ships this way.

**Worked example:** `UNIT_TDMTNK`, the **GDI Medium Tank**, the model for every turreted combat vehicle, as TDE1 is
for infantry and TDATWR for buildings. (TDMCV and TDHARV are turret-less utility units, ported with the buildings.)

**Read first:** `td-port-playbook.md` (architecture and traps) and `td-infantry-port-recipe.md` (the bundling
pipeline this shares). This doc is the vehicle-specific companion.

---

## What's different about vehicles (vs infantry)

1. **Source files:** `tiberiandawn/udata.cpp` (the `UnitTypeClass` ctor — speed/armor/strength/turret/squash/explosion), `const.cpp` `Weapons[]`/`Warheads[]`, `bbdata.cpp` the bullet. **The catalogue/our docs are NOT the spec** (playbook §2.1): the Medium Tank fires `WEAPON_105MM`, not 90mm.
2. **RA's `UnitTypeClass` ctor has geometry TD lacks** (the legitimate "schema bridge" exception): see the field manual's [Porting Tiberian Dawn units](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-units.md#fill-in-what-red-alert-needs-and-td-never-had), Fill in what Red Alert needs and TD never had, and [Adding a unit](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/adding-a-unit.md#1-the-enum-and-the-constructor), section 1. TD's constructor (TD `UDATA.CPP:1406-1452`) also has no `RemapType`, no rotation-stage count (RA's 32) and no `is_jammer`/`is_gapper`: fill them from RA's, as that listing shows. Map TD's flags by **meaning** (turret/crusher/gigundo/goodie); start the weapon offsets from a same-size RA tank (`2TNK` for a medium tank) and tune by screenshot until the flash sits on the TD barrel; keep TD's `toffset` (0).
3. **`Speed` in rules.ini = `round(MPHType × 100 / 256)`**, from TD's `MPH_*` constant every time, never RA's same-role tank (`2TNK`'s `Speed=8`): see the field manual's [Porting Tiberian Dawn units](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-units.md), Speed. TF's values: `[TDMTNK]` 7 (`MPH_MEDIUM` 18), `[TDMCV]` 5 (`MPH_MEDIUM_SLOW` 12). The harvester is the exception: TD's is `MPH_MEDIUM_SLOW` (5), but `[TDHARV]` ships `Speed=6`, RA `[HARV]`'s, so no faction's trucks run slower than another's. The `// Speed=N` legend on `MPHType` in `defines.h` gives each MPH's value.
4. **Rendering = classic SHP (TFASSETS.MIX) + HD tileset (RA_UNITS.XML)** — both, unlike infantry (which use a donor-ImageData). `UnitTypeClass::One_Time` loads `<Image>.SHP` for `ImageData`; a TD-prefixed unit needs `TD<NAME>.SHP` packed into `TFASSETS.MIX` (add to `build_tfassets.sh`, source `<NAME>.SHP` from `CONQUER.MIX`). `ShapeSize=48,48` in rules.ini sets `MaxSize`. Classic mode is locked out, so the SHP is never drawn: it gives `ImageData` and the selection box. The HD tileset (`bundle_unit.py`) renders the Remaster; staging (`scripts/td_base_art.py`) points every unchanged TD tile at the base game's ZIP, so the copy `bundle_unit.py` makes doesn't ship (`td-base-art.md`).
5. **Tileset donor = a same-frame-count turreted RA tank.** A turreted tank is 64 frames (32 body + 32 turret). RA's `2TNK` is exactly 64 → `bundle_unit.py MTNK TDMTNK --tileset-donor 2TNK`. (The `frame_count` slicer handles mismatches.)
6. **Cameo/text:** `<BuildIcon>` references a vanilla `BuildIcon_TD_*` region (in `CNCBUILDABLES.XML`); `--text-name TEXT_UNIT_TITLE_GDI_<X>` / `--text-desc` likewise. Nothing shipped.

---

## Step-by-step (GDI Medium Tank worked example)

1. **Source dig.** `udata.cpp:264` `UnitMTank` (GDI-only `HOUSEF_GOOD`, turret, Str 400, Sight 3, Cost 800, `ARMOR_STEEL`, `MPH_MEDIUM`, ROT 5, `ANIM_FRAG2` death, `WEAPON_105MM`). `const.cpp:80` `WEAPON_105MM = {BULLET_APDS, 30, 50, 0x04C0=4.75, VOC_TANK3, ANIM_MUZZLE_FLASH}`. `bbdata.cpp:109` `ClassAPDS` (visible, **faceless** → no §3.25 white-box, `MPH_VERY_FAST`, `WARHEAD_AP`).
2. **Chain audit / TD→TD reuse.** Both `WEAPON_105MM` and `WEAPON_TURRET_GUN` fire `BULLET_APDS` in source → **reuse the already-ported `BULLET_TDAPDS` + `WARHEAD_TDAP`** (TD→TD, the same shell the Nod Turret fires). New: `WEAPON_TD105MM` (own stats), `VOC_TD_TANK3` (=`TNKFIRE4`; Nod Turret uses `TNKFIRE6`).
3. **Enums** (`defines.h`): `UNIT_TDMTNK` (before `UNIT_COUNT`; heap has `MAX_UNIT_TYPES = UNIT_COUNT+50`), `WEAPON_TD105MM`, `VOC_TD_TANK3`.
4. **Ctor** (`udata.cpp`): clone `UnitTdMcv`'s shape, map TD flags (turret/crusher/gigundo/goodie = true), geometry from `2TNK`, `ANIM_TDFRAG2` explosion (see §FRAG), `MISSION_HUNT`. Register in `Init_Heap` (enum order).
5. **Weapon** (`rules.cpp` register `"TD105mm"` — **non-IsTDPort**, like `TDTurretGun`). `rules.ini [TD105mm]`: Damage 30 / ROF 50 / Range 4.75 / `Projectile=TDAPDS` / `Speed=40` / `Warhead=TDAP` / `Report=TNKFIRE4` / `Anim=GUNFIRE`. `audio.cpp` `VOC_TD_TANK3="TNKFIRE4"`; `RAC/RAR_SFX_TNKFIRE4` route (base WAVs exist).
6. **Unit `rules.ini [TDMTNK]`:** `Image=TDMTNK`, `ShapeSize=48,48`, `Name=GDI Medium Tank`, `Primary=TD105mm`, Strength 400, `Armor=heavy`, TechLevel 3, Sight 3, `Speed=7` (`MPH_MEDIUM` → `round(18×100/256)`; see §3 — **not** `9`), `Tracked=yes` (TD `SPEED_TRACK` — see trap table), `Owner=GoodGuy`, Cost 800, Points 62, ROT 5, `Crewed=yes`, `Prerequisite=weap` (GDI war factory `TDWEAP` shadows `STRUCT_WEAP`).
7. **Bundle:** `bundle_unit.py MTNK TDMTNK --tileset-donor 2TNK --build-icon BuildIcon_TD_MediumTank --text-name TEXT_UNIT_TITLE_GDI_MED_TANK --text-desc TEXT_UNIT_DESC_GDI_MED_TANK` (HD tileset + cameo). `build_tfassets.sh` `MTNK.SHP:TDMTNK.SHP` (classic) + rebuild TFASSETS.MIX.
8. **Build / deploy / smoke-test.**

---

## Vehicle-specific traps

Speed, tracks and wheels, effects RA lacks, the crew and the muzzle flash are in the field manual's [Porting Tiberian Dawn units](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-units.md) (Speed, Fill in, Traps); the sidebar name is in [New text strings](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/launcher-data/new-text-strings.md#traps), Traps. TF's side:
- `Tracked=yes` on all four TD tanks; the wheeled Recon Bike and Buggy stay un-tracked.
- `GUNFIRE` (muzzle) and `VEH-HIT3` (impact) are reused, as on the Nod Turret; FRAG2 is ported (§FRAG).
- `UnitClass::Crew_Type` sends a `TD` IniName to `INFANTRY_TDE1` before the unarmed-civilian branch, so the MCV and harvester are covered too. It mirrors `BuildingClass::Crew_Type`.
- The faction yards and war factories point `ObjectNameTextID` at IDs of their own in the loose `Data/ModText.csv`.

---

## §FRAG — porting a TD death/effect anim RA lacks (`ANIM_FRAG2`)

TD's vehicle death uses `ANIM_FRAG2`; **RA only has `ANIM_FRAG1`**. Port it as its own TD anim (the `ANIM_TD_ION_CANNON` single-anim pattern, *not* the directional `bundle_anim.py`):
1. **The SHP name ≠ the enum name.** TD's `ANIM_FRAG2` ctor uses the data name **`"FRAG3"`** (`tiberiandawn/adata.cpp:866`, var `Frag3`). IniName = `TDFRAG3` (TD prefix).
2. **`defines.h`:** `ANIM_TDFRAG2` (after `ANIM_TD_ION_CANNON`, before the `#ifdef` anims); `VOC_TD_XPLOBIG6` (the TD sound; base `TDC/TDR_SFX_XPLOBIG6` WAVs exist).
3. **`adata.cpp`:** clone RA's `Frag1` ctor (23 params, no virtual-scale — the ION's 24-param overload adds it) with TD's FRAG2 values (max-dim 41, 3 stages, crater, ground-level, sound `VOC_TD_XPLOBIG6`, 29 virtual stages). Register after `TdIonCannon` in `Init_Heap`.
4. **HD art:** single-anim bundle (FRAG3 has 29 frames, non-directional) — re-pack `FRAG3.ZIP`→`TDFRAG3.ZIP` (TD-prefixed frames) + `bundle_anim.patch_ra_vfx_xml("TDFRAG3", "tdfrag3", 29)`. `bundle_anim.py` itself is directional-only; call its helpers for a single anim.
5. **Classic SHP:** `build_tfassets.sh` `FRAG3.SHP:TDFRAG3.SHP`.
6. **Sound route:** `RAC/RAR_SFX_XPLOBIG6` (nonlocalized) → base `TDC/TDR_SFX_XPLOBIG6.WAV`.
7. **Use it:** the unit ctor's `Explosion=ANIM_TDFRAG2`.

---

## §DUAL — a dual-weapon vehicle with an anti-air secondary (Mammoth)

The Mammoth Tank carries TWO weapons (cannon + AA tusk missiles). See the field manual's [Porting Tiberian Dawn units](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-units.md#special-cases-at-method-level), Special cases (two weapons and the `4TNK` offsets, anti-air from the secondary, `Burst=2`, a per-type prerequisite remap). TF's mapping:
- `Primary=<cannon>` + `Secondary=<AA weapon>`, offsets from `4TNK`.
- The Mammoth Tusk fires `TDSSM` (`AA=yes,AG=yes`, already ported for the Guard Tower), so the unit engages aircraft with the secondary.
- `Burst=2` on both cannon and tusks (like `[TDTowTwo]`).
- TD's Mammoth needs `STRUCTF_REPAIR`: a `STRUCT_REPAIR → TDFIX` remap in `house.cpp::Can_Build` (like the existing STRUCT_WEAP/REFINERY/ADVANCED_TECH ones) lets the GDI service depot satisfy `Prerequisite=fix`.

---

## §FLAME — a turret-less flame-jet vehicle (Flame Tank)

The Nod Flame Tank (`UNIT_TDFTNK`, TD `UnitFTank`) fires `WEAPON_FLAME_TONGUE` — a flame
jet, not a projectile. **Highest-reuse vehicle so far**: the E4 Flamethrower already built
every flame primitive — `BULLET_TDFLAME` (invisible round), `WARHEAD_TDFIRE`, the 8 directional
`ANIM_FLAME_N..NW` muzzle jets, `VOC_TD_FLAMER`. The tank weapon differs from the E4 weapon
only in **damage (50 vs 35)** — same bullet/warhead/anim/range/ROF/sound. Whole port = one new
weapon + one ctor + assets.

- **NO techno.cpp change.** The flame-jet dispatch is **anim-keyed**, not weapon-keyed:
  `techno.cpp` `case ANIM_FLAME_N: a = ANIM_FLAME_N + Dir_Facing(Fire_Direction())` fires for
  *any* weapon whose rules.ini `Anim=TDFLAME-N`. There is no `switch(weapon)` to add the weapon to; set
  `Anim=TDFLAME-N`.
- **Turret-less = zero offset tuning.** `is_turret_equipped=false` → no muzzle-flash geometry to
  screenshot-tune (the §traps "muzzle-flash mis-positioned" trap doesn't apply). The jet draws from
  the body's `Fire_Coord`; the body rotates to face target (TD tracked-vehicle rule, the non-turret
  branch of `UnitClass::Rotation_AI`).
- **`Burst=2`** = TD FTANK's two-shooter (twin flame jets), as for the Mammoth (§DUAL).
- **New weapon `WEAPON_TDFLAMETONGUE` / `[TDFlameTongue]`** (Dmg50, ROF50, Range2, Projectile=TDFlame,
  Speed=40, Warhead=TDFire, Report=FLAMER2, Anim=TDFLAME-N, Burst=2); `IsTDPort=true` in rules.cpp
  (identical treatment to `TDFlamethrower`).
- **Explosion** `ANIM_NAPALM3` (TD FTANK death; RA has it — a large napalm burst, fitting).
- **Internal name** `TXT_LTANK` (RA has no Flame Tank string); real "Flame Tank" name from rules.ini
  `Name=`. Cameo `BuildIcon_TD_FlameTank` + `TEXT_UNIT_TITLE_NOD_FLAME_TANK` (both in the base launcher
  PAK; nothing shipped).
- **Assets:** classic `FTNK.SHP:TDFTNK.SHP` in `build_tfassets.sh`; HD via
  `bundle_unit.py FTNK TDFTNK --tileset-donor APC ...` — a turret-less hull is **32 frames** (half a
  turreted tank's 64), so the donor is RA's **APC** (38 tiles: 32 body + 6 door) sliced to 32, not 2TNK.

## §BIKE — a pure-reuse wheeled rocket unit (Recon Bike)

The Nod Recon Bike (`UNIT_TDBIKE`, TD `UnitBike`, udata.cpp:797) is the **highest-reuse vehicle
yet** — **zero** new weapon/bullet/warhead/sound/anim. The whole port is one enum + one ctor + one
rules.ini section + two asset lines. The lesson: **always chain-audit the TD weapon against what's
already shipped before assuming new work** — the Bike fires `WEAPON_DRAGON`, which we already ship as
`[TDDragon]` from the E3 Rocket Soldier (the `BULLET_TDTOW` homing rocket + `WARHEAD_TDAP` + Report
`BAZOOK1`). The whole chain is reused verbatim; the E3 already proved that missile renders clean.

- **`ANIM_FRAG1` is TD-authentic, NOT a leak.** TD's BIKE literally uses `ANIM_FRAG1` (the *light*-
  vehicle death), unlike the tanks' `ANIM_FRAG2` (§FRAG). RA has `FRAG1` natively, so — unlike the
  Medium Tank — there's **no death-anim to port**. Confirm the TD ctor's explosion field before
  reaching for §FRAG.
- **Wheeled — NO `Tracked=`.** TD BIKE is `SPEED_WHEEL` (genuinely wheeled, the authentic 60%/40%
  terrain modifier), so it gets **no** `Tracked=yes` (that's tracks-only, the four TD tanks). This
  is the un-tracked half of the trap-table locomotion row.
- **All-zero weapon offsets** (vertical/primary/secondary all `0x0000`), following RA's own wheeled
  turret-less rocket unit **`UnitV2Launcher`** — the rocket launches from the hull, there's no turret
  geometry to screenshot-tune. (Don't copy the Flame Tank's `0x30`/`0x20` offsets — those carry the
  twin flame nozzles forward; a single-rocket bike doesn't need them.)
- **NOT a crusher, NOT gigundo** (`is_crusher=false`, `is_gigundo=false`) — a light scout bike can't
  squash and isn't a big unit. (The V2 Launcher template has *both* true; flip them.)
- **Strength 160, `Points=45`, `Speed=16`:** TD's retail branch (`ADVANCED` is off, `tiberiandawn/defines.h:44`), the reward half of TD's `80, 45` (the Medium Tank's `80, 62` gives `Points=62`), and `MPH_FAST` 40. See the field manual's [Porting Tiberian Dawn units](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-units.md#read-tds-own-source-first), Read TD's own source first, Rate of fire, scatter and AI value, and Speed.
- **Nod-only** (`HOUSEF_BAD`) → `Owner=BadGuy`, `Prerequisite=weap` (TDAFLD airstrip satisfies it via
  the house.cpp `STRUCT_WEAP` remap, same as Light/Flame Tank). `TechLevel=2` (TD build level 2 — the
  earliest TD vehicle).
- **Assets:** classic `BIKE.SHP:TDBIKE.SHP`; HD `bundle_unit.py BIKE TDBIKE --tileset-donor APC ...`
  (32-frame turret-less hull, same APC-sliced-to-32 donor as the Flame Tank — the script auto-derives
  the frame count from the ZIP, no `--frame-count` flag). Cameo `BuildIcon_TD_ReconBike`, text
  `TEXT_UNIT_TITLE_NOD_RECON_BIKE` / `_DESC_` — all already in the base launcher PAK (`TD_BIKE` is a
  defined buildable in the base `CNCBUILDABLES.XML`; nothing shipped). Internal `Name=TXT_LTANK`
  placeholder (RA has no Recon Bike string; rules.ini `Name=Recon Bike` drives display).

## §APC — a transport vehicle (the first non-combat-role unit)

The GDI APC (`UNIT_TDAPC`, TD `UnitAPC` udata.cpp:907) is the first **transport**. Pure-reuse weapon
(`TDM60mg`, already shipped for the Hum-vee/Buggy), but transport adds engine work the tanks didn't need.

- **GDI-only by faction-canon, not source.** TD's APC ctor sets BOTH `HOUSEF_GOOD` *and* `HOUSEF_BAD` (a
  permissive TD-multiplayer quirk — unlike `LTANK`[BAD-only]/`MTANK`[GOOD-only], which are clean). The APC
  is iconically GDI in gameplay (Nod's mobility = Buggy/Bike/Stealth Tank), so `Owner=GoodGuy`. **Check the
  ownable bits against faction-canon, not just the raw flags.**
- **`Passengers=N` is the whole switch, but four behaviours are keyed on `UNIT_APC`:** see the field manual's [Porting Tiberian Dawn units](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-units.md#special-cases-at-method-level), Special cases ("Transports"). TF adds `UNIT_TDAPC` at each (`grep -n UNIT_APC redalert/*.cpp`; the `case UNIT_MCV:`/`case UNIT_TDMCV:` precedent shows the pattern), in both the `#ifdef FIXIT_PHASETRANSPORT` and `#else` door branches. The player's unload is the generic `ACTION_SELF` → `MISSION_UNLOAD` (unit.cpp:3805).
- **No turret (`is_turret_equipped=false`):** the M60 is hull-mounted and the body turns to aim. Tileset donor = the APC's own 38-frame block (no slicing).
- **`Crewed=no`** (TD source "crew inside? false") — the 5 passengers spill on death, no extra survivor; the
  §traps Crew_Type trap doesn't apply.
- **Deploy/unload key:** works for any unit whose self-click deploys or unloads (playbook §3.23); the
  DLL reads the key and runs the self-action, so a new transport needs no key work.

> ⚠️ **A rebuilt `TFASSETS.MIX` needs a full `deploy.sh`.** `deploy.sh --no-build` ships `build/` as it stands
> (see the box at the end), so a MIX rebuilt after the last staging stays old there. Symptom: the unit builds with
> the right name, prerequisite and cameo but is **invisible**: `One_Time`'s `MFCD::Retrieve("TD<NAME>.SHP")`
> returns NULL, so `ImageData` is 0 and its width 0 (`tf_objlist.log` shows `ImageData=00000000 ow=0` against a
> working unit's `ImageData=<ptr> ow=48`). Run `build_tfassets.sh`, then `deploy.sh` without `--no-build`.

## §STEALTH — a cloaking unit (Stealth Tank), and stealth detection

The Nod Stealth Tank (`UNIT_TDSTNK`, TD `UnitSTank`, IniName **`STNK`**) is the **lowest-engine-effort
combat vehicle yet** — cloaking is *free*. The whole port = enum + ctor + one new weapon + assets + a
small audio dispatch.

**(a) Cloak is pure data.** A TD cloaker is rules.ini **`Cloakable=yes`** alone (parsed in `techno.cpp` `Read_INI`; firing uncloaks it through `FIRE_CLOAKED` → `Do_Uncloak`): no `_TD()` port, no engine code. See the field manual's [Porting Tiberian Dawn units](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-units.md#cloak-and-stealth-detection-one-system-in-both-games), Cloak and stealth detection, and [A stealth generator](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/behaviours/stealth-generator.md#what-the-engine-gives-you) (the export carries the raw `Cloak` state). RA's own Phase Transport (`UNIT_PHASE`, Aftermath, `Cloakable=yes`) is the cloaking-*vehicle* precedent.

**(b) Stealth detection is the same system in TD and RA,** pure rules.ini `Sensors=`, no DLL rebuild: see the same section, and [A stealth generator](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/behaviours/stealth-generator.md#the-engine-gaps-you-have-to-fill) ("Detection only runs one way"). TD's detecting defences map to ours: GDI **TDGTWR/TDATWR**, Nod **TDGUN/TDOBLI**, all with `Sensors=yes`. Allied (`PBOX/HBOX/GUN/DOME`) and Soviet (`TSLA/FTUR/DOME`) defences already had it from vanilla RA, so the 4-faction web is symmetric.

**(c) The 2-shooter needs its OWN weapon when the base weapon is shared** (the field manual's [Porting Tiberian Dawn units](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-units.md#special-cases-at-method-level), Special cases). TD STANK fires `WEAPON_DRAGON`, *shared* with the single-shot E3 Rocket Soldier + Recon Bike, so `TDStnkDragon` = TDDragon's stats/bullet/warhead + `Burst=2`, with its own `WEAPON_` enum, `rules.cpp` registration and `IsTDPort`. General rule: clone-with-tweak any shared weapon rather than mutate the shared one.

**(d) TD cloak audio.** TD and RA cloak with different sounds (the field manual's [Porting Tiberian Dawn units](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-units.md#cloak-and-stealth-detection-one-system-in-both-games), Cloak and stealth detection). To use TD's for TD units without disturbing RA cloakers (Phase Transport/Submarine): add `VOC_TD_CLOAK`→`"TRANS1"` (`audio.cpp`), route `RAC/RAR_SFX_TRANS1` →
base `TDC/TDR_SFX_TRANS1.WAV` (`SFXEVENTSNONLOCALIZED.XML`, BAZOOK1 pattern, no WAV bundling), and in
`Do_Cloak`/`Do_Uncloak` branch on the **`TD` IniName prefix** → `VOC_TD_CLOAK` else the stock RA sound.

**(e) Other STANK specifics.** Turret-less (all-zero weapon offsets, like the Bike); the ctor's
invisible-to-radar param is `true`, as in TD, but it changes nothing: the `is_stealthy` field
(`ObjectTypeClass::IsStealthy`) is set and never read in either game's source. Whether the launcher's minimap
shows a cloaked or `Invisible=` unit to an enemy is untested. `ANIM_TDFRAG2` death; `Prerequisite=weap,TDHQ` (the Nod
airstrip and the communications centre, TD's `STRUCTF_RADAR`); Speed 12 (`MPH_MEDIUM_FAST`, = Hum-vee/Buggy — TD-authentic, kept).

**Compile traps hit:** `TXT_STANK` (the field manual's [Porting Tiberian Dawn units](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/units/porting-td-units.md#traps), Traps) → TF uses the `TXT_LTANK` placeholder; `Techno_Type_Class()` returns a **pointer** not a reference → `->IniName`.

## The roster

**Shipped:** turreted-tank trio — GDI Medium Tank (`TDMTNK`), NOD Light Tank (`TDLTNK`), GDI Mammoth
Tank (`TDHTNK` — dual weapon + AA, §DUAL); Nod Flame Tank (`TDFTNK` — turret-less flame jet, §FLAME);
Nod Recon Bike (`TDBIKE` — wheeled rocket scout, §BIKE — pure E3-TDDragon reuse); GDI Hum-vee (`TDJEEP`)
+ Nod Buggy (`TDBGGY` — wheeled MG turret); GDI APC (`TDAPC` — tracked transport, §APC);
**Nod Stealth Tank (`TDSTNK` — cloaking, §STEALTH).**
Naming convention: faction-prefix any TD unit whose name collides with an RA one. The MLRS, Artillery and
SSM Launcher followed with their own weapon ports (`td-mlrs-deep-dive.md`), and the aircraft on the helipad
and the TDCARGO plumbing.

> **deploy.sh and `POST_BUILD`:** the build's repackage is a **RedAlert POST_BUILD step**
> (`redalert/CMakeLists.txt:222`) that only fires when the DLL relinks (the field manual's
> [Building the DLL on Linux](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/getting-started/building-the-dll-on-linux.md#traps)), so `deploy.sh` restages
> `build/remaster/Vanilla_RA/` from scratch after every build and copies the linked DLL in from
> `build/remaster/RelWithDebInfo/RedAlert.dll` (playbook §3.9). Only `--no-build` ships `build/` as it stands.
