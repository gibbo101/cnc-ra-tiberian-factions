# TD Vehicle Port Recipe

**Worked example (shipped 2026-05-30):** `UNIT_TDMTNK` — **GDI Medium Tank**, the first combat vehicle. Establishes the vehicle pipeline the way TDE1 established infantry and TDATWR established buildings. (TDMCV + TDHARV were ported earlier in the building-separation arc but are turret-less utility units; the Medium Tank is the first turreted combat vehicle.)

**Read first:** `docs/td-port-playbook.md` (architecture + traps) and `docs/td-infantry-port-recipe.md` (the bundling pipeline this shares). This doc is the vehicle-specific companion.

---

## What's different about vehicles (vs infantry)

1. **Source files:** `tiberiandawn/udata.cpp` (the `UnitTypeClass` ctor — speed/armor/strength/turret/squash/explosion), `const.cpp` `Weapons[]`/`Warheads[]`, `bbdata.cpp` the bullet. **The catalogue/our docs are NOT the spec** (playbook §2.1): the Medium Tank fires `WEAPON_105MM`, not 90mm.
2. **RA's `UnitTypeClass` ctor has RA-only geometry fields TD lacks** (the legitimate "schema bridge" exception): `RemapType`, `verticaloffset`, `primaryoffset`/`primarylateral`, `secondaryoffset`/`secondarylateral`, `rotation` (32), `is_jammer`/`is_gapper`. Map TD's flags by **meaning** (turret/crusher/gigundo/goodie); for the **weapon-offset geometry** (where the muzzle flash draws on the turret) there is **no TD value** — start from a same-size RA tank (`2TNK` for a medium tank: vert `0x0030`, primary `0x00C0`) and **tune by screenshot** until the flash sits on the TD gun barrel. `toffset` (turret-center) IS a TD field — use TD's value (0).
3. **`Speed` in rules.ini = `round(MPHType × 100 / 256)`**, NOT RA's tank's value and **NOT `MPHType ÷ 2`** (the ÷2 form was wrong — see ⚠️ below). TD gives an `MPHType` constant; the rules.ini `Speed=` is a **1–100 percentage** that the engine scales back to the 0–255 `MaxSpeed` via `_Scale_To_256` (`MaxSpeed = Speed × 256 / 100`). So invert it: `MPH_MEDIUM = 18` → `round(18 × 100 / 256)` = **`Speed=7`**; the shipped `[TDMCV]` (`MPH_MEDIUM_SLOW` = 12) → `round(12 × 100 / 256)` = `Speed=5`; the harvester (`MPH_MEDIUM` raw 18, but capped) ships `Speed=5`. **Do NOT copy RA's same-role tank `Speed=8`** — derive from the TD `MPH_*` constant, every time. (Luke caught both the RA-copy and the ÷2 errors.)

   > ⚠️ **The ÷2 convention this doc originally taught was wrong** (corrected commit `187fd66`, 2026-05-31). `Speed = MPHType / 2` ran **every one of the 13 TD ground units ~28% too fast**. A Light-vs-Flame playtest race exposed it. All units were recomputed to `round(MPHType × 100 / 256)` (e.g. `MPH_MEDIUM` tanks `9 → 7`, harvester `10 → 5`) and the `// Speed=N` comments in `defines.h` were corrected to match. Use the ×100/256 form.
4. **Rendering = classic SHP (TFASSETS.MIX) + HD tileset (RA_UNITS.XML)** — both, unlike infantry (which use a donor-ImageData). `UnitTypeClass::One_Time` loads `<Image>.SHP` for `ImageData`; a TD-prefixed unit needs `TD<NAME>.SHP` packed into `TFASSETS.MIX` (add to `build_tfassets.sh`, source `<NAME>.SHP` from `CONQUER.MIX`). `ShapeSize=48,48` in rules.ini sets `MaxSize`. The HD tileset (`bundle_unit.py`) renders the Remaster.
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

| Trap | Symptom | Fix |
|---|---|---|
| **`Speed` copied from RA's tank, or halved** | Tank too slow/fast (TD-inauthentic); the ÷2 form runs ~28% too fast | `Speed = round(MPHType × 100 / 256)` (it's a 1–100 % that `_Scale_To_256` expands to `MaxSpeed`); derive from TD's `MPH_*` constant, never RA's same-role unit, never ÷2. See §3 ⚠️ |
| **Tracked vehicle left wheeled** | TD tank moves too slow off-road (defaults to `SPEED_WHEEL` 60%/40% vs `SPEED_TRACK` 80%/70%) | Set `Tracked=yes` for TD `SPEED_TRACK` units (all four TD tanks). Genuinely wheeled TD units (`SPEED_WHEEL` — e.g. Recon Bike, Buggy) stay un-tracked. Exposed by a Light-vs-Flame race, commit `187fd66` |
| **Generic effect not in RA** | Compile error (e.g. `ANIM_FRAG2` undeclared) | RA lacks some TD anims/sounds. If it's a distinctive death visual, **port it** (see §FRAG); muzzle flash (`GUNFIRE`) + impact (`VEH-HIT3`) are generic and reused per the Nod Turret precedent |
| **Crew survivor is RA rifle** | Killed TD vehicle pops an `E1` rifleman | `UnitClass::Crew_Type` — add the `IniName[0..1]=="TD"` → `INFANTRY_TDE1` check **before** the unarmed-civilian branch (so MCV/Harvester are covered too). Mirrors `BuildingClass::Crew_Type` |
| **Sidebar name ≠ in-game name** | Hover shows "GDI Medium Tank", sidebar shows "Medium Tank" | rules.ini `Name=` drives the in-game/hover name; the sidebar cameo uses the master-text `TEXT_UNIT_TITLE_*` (`.LOC`, **same-length-in-place only** — a longer name needs the launcher-crashing resize). Accept the short sidebar name, or use a same-length abbreviation |
| **Muzzle-flash mis-positioned** | Flash floats off the gun | The weapon-offset geometry is RA-only; tune `verticaloffset`/`primaryoffset` against the TD sprite by screenshot |

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

The Mammoth Tank carries TWO weapons (cannon + AA tusk missiles). Mapping:
- **rules.ini:** `Primary=<cannon>` + `Secondary=<AA weapon>`. The RA `UnitTypeClass` ctor has separate primary + secondary weapon offsets (the lateral barrels) — reference RA's own dual-weapon Mammoth `4TNK` (primary `0x00C0/0x0028`, secondary `0x0008/0x0040`).
- **Anti-air is automatic** when the secondary weapon's bullet is AA-capable: the Mammoth Tusk fires `TDSSM` (`AA=yes,AG=yes`, already ported for the Guard Tower), so the unit engages aircraft with the secondary — RA's secondary-weapon-AA convention. No unit-level AA flag needed.
- **Multi-shot / double-tap = the weapon `Burst=N` field.** TD's "fires multiple shots in quick succession" (the Mammoth's dual-barrel double-tap) has **no RA unit-level flag** — set `Burst=2` on the weapon instead (like `[TDTowTwo]`). The Mammoth uses `Burst=2` on both cannon and tusks.
- **Repair-bay prereq:** TD's Mammoth needs `STRUCTF_REPAIR`. Add a `STRUCT_REPAIR → TDFIX` remap in `house.cpp::Can_Build` (the per-type prereq remap, like the existing STRUCT_WEAP/REFINERY/ADVANCED_TECH ones) so `Prerequisite=fix` is satisfied by the GDI service depot.

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
  *any* weapon whose rules.ini `Anim=TDFLAME-N`. (First instinct was to add the weapon enum to a
  `switch(weapon)` — wrong, there's no such switch. Just set `Anim=TDFLAME-N`.)
- **Turret-less = zero offset tuning.** `is_turret_equipped=false` → no muzzle-flash geometry to
  screenshot-tune (the §traps "muzzle-flash mis-positioned" trap doesn't apply). The jet draws from
  the body's `Fire_Coord`; the body rotates to face target (TD tracked-vehicle rule, the non-turret
  branch of `UnitClass::Rotation_AI`).
- **`Burst=2`** = TD FTANK's `is_twoshooter` "fires two shots in quick succession" (twin flame jets) —
  same RA mapping as the Mammoth double-tap (§DUAL); RA has no unit-level two-shooter flag.
- **New weapon `WEAPON_TDFLAMETONGUE` / `[TDFlameTongue]`** (Dmg50, ROF50, Range2, Projectile=TDFlame,
  Speed=40, Warhead=TDFire, Report=FLAMER2, Anim=TDFLAME-N, Burst=2); `IsTDPort=true` in rules.cpp
  (identical treatment to `TDFlamethrower`).
- **Explosion** `ANIM_NAPALM3` (TD FTANK death; RA has it — a large napalm burst, fitting).
- **Internal name** `TXT_LTANK` (RA has no Flame Tank string); real "Flame Tank" name from rules.ini
  `Name=`. Cameo `BuildIcon_TD_FlameTank` + `TEXT_UNIT_TITLE_NOD_FLAME_TANK` (both in the base launcher
  PAK; nothing shipped).
- **Assets:** classic `FTNK.SHP:TDFTNK.SHP` in `build_tfassets.sh`; HD via
  `bundle_unit.py FTNK TDFTNK --tileset-donor APC ...` — a turret-less hull is **32 frames** (half a
  turreted tank's 64), so the donor is the 32-frame **APC**, not 2TNK.

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
- **Strength 160** — TD BIKE has `#ifdef ADVANCED 90 #else 160`; `ADVANCED` is **`//#define`d out**
  (`tiberiandawn/defines.h:44`), so the retail value is the **`#else` (160)** branch. `Points=45` =
  the **reward** field (the *second* of the two-value `risk, reward` ctor pair — `80, 45`; same as the
  Medium Tank `80, 62` → `Points=62`).
- **Speed=16** — `MPH_FAST=40` → `round(40×100/256)` (the corrected formula, see §3). NOT ÷2.
- **Nod-only** (`HOUSEF_BAD`) → `Owner=BadGuy`, `Prerequisite=weap` (TDAFLD airstrip satisfies it via
  the house.cpp `STRUCT_WEAP` remap, same as Light/Flame Tank). `TechLevel=2` (TD build level 2 — the
  earliest TD vehicle).
- **Assets:** classic `BIKE.SHP:TDBIKE.SHP`; HD `bundle_unit.py BIKE TDBIKE --tileset-donor APC ...`
  (32-frame turret-less hull, same APC-sliced-to-32 donor as the Flame Tank — the script auto-derives
  the frame count from the ZIP, no `--frame-count` flag). Cameo `BuildIcon_TD_ReconBike`, text
  `TEXT_UNIT_TITLE_NOD_RECON_BIKE` / `_DESC_` — all already in the base launcher PAK (`TD_BIKE` is a
  defined buildable in the base `CNCBUILDABLES.XML`; nothing shipped). Internal `Name=TXT_LTANK`
  placeholder (RA has no Recon Bike string; rules.ini `Name=Recon Bike` drives display).

## The roster

**Shipped:** turreted-tank trio — GDI Medium Tank (`TDMTNK`), NOD Light Tank (`TDLTNK`), GDI Mammoth
Tank (`TDHTNK` — dual weapon + AA, §DUAL); **Nod Flame Tank (`TDFTNK` — turret-less flame jet, §FLAME);
Nod Recon Bike (`TDBIKE` — wheeled rocket scout, §BIKE — pure E3-TDDragon reuse).**
Naming convention (Luke): faction-prefix any TD tank colliding with an RA name. **Next:** Buggy / MLRS /
APC / Artillery / Stealth Tank (cloak — save for last). The Buggy is the next pure-reuse pick (chain gun
already shipped, also wheeled/turret-less — clone §BIKE swapping the weapon).

> **deploy.sh gotcha (hit 2026-05-30):** `deploy.sh` `rm -rf`s `build/remaster/Vanilla_RA/` then runs the
> workflow, but the repackage is a **RedAlert POST_BUILD step** (`redalert/CMakeLists.txt:213`) that only
> fires when the DLL *relinks*. If ninja sees the DLL up-to-date (e.g. you already built manually),
> POST_BUILD is skipped and `Vanilla_RA/` is never recreated → deploy aborts "RedAlert.dll not found".
> Fix: touch a source file to force a relink, OR manually run the 3 POST_BUILD `cmake -E` copies (note the
> linked DLL is at `build/remaster/RelWithDebInfo/RedAlert.dll`) then `deploy.sh --no-build`.
