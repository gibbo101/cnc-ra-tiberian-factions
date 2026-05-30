# TD Vehicle Port Recipe

**Worked example (shipped 2026-05-30):** `UNIT_TDMTNK` — **GDI Medium Tank**, the first combat vehicle. Establishes the vehicle pipeline the way TDE1 established infantry and TDATWR established buildings. (TDMCV + TDHARV were ported earlier in the building-separation arc but are turret-less utility units; the Medium Tank is the first turreted combat vehicle.)

**Read first:** `docs/td-port-playbook.md` (architecture + traps) and `docs/td-infantry-port-recipe.md` (the bundling pipeline this shares). This doc is the vehicle-specific companion.

---

## What's different about vehicles (vs infantry)

1. **Source files:** `tiberiandawn/udata.cpp` (the `UnitTypeClass` ctor — speed/armor/strength/turret/squash/explosion), `const.cpp` `Weapons[]`/`Warheads[]`, `bbdata.cpp` the bullet. **The catalogue/our docs are NOT the spec** (playbook §2.1): the Medium Tank fires `WEAPON_105MM`, not 90mm.
2. **RA's `UnitTypeClass` ctor has RA-only geometry fields TD lacks** (the legitimate "schema bridge" exception): `RemapType`, `verticaloffset`, `primaryoffset`/`primarylateral`, `secondaryoffset`/`secondarylateral`, `rotation` (32), `is_jammer`/`is_gapper`. Map TD's flags by **meaning** (turret/crusher/gigundo/goodie); for the **weapon-offset geometry** (where the muzzle flash draws on the turret) there is **no TD value** — start from a same-size RA tank (`2TNK` for a medium tank: vert `0x0030`, primary `0x00C0`) and **tune by screenshot** until the flash sits on the TD gun barrel. `toffset` (turret-center) IS a TD field — use TD's value (0).
3. **`Speed` in rules.ini = MaxSpeed ÷ 2**, NOT RA's tank's value. TD gives an `MPHType` constant (`MPH_MEDIUM`); the `MPHType` enum value (`MPH_MEDIUM = 18`) halves to the rules.ini `Speed` (9). Proven by the shipped `[TDMCV]`: TD MCV is `MPH_MEDIUM_SLOW` (=12) and ships `Speed=6`. **Do NOT copy RA's medium tank `Speed=8`** — RA's is `MPHType 16`, genuinely slower than TD's. (Luke caught this — derive from the TD constant, every time.)
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
6. **Unit `rules.ini [TDMTNK]`:** `Image=TDMTNK`, `ShapeSize=48,48`, `Name=GDI Medium Tank`, `Primary=TD105mm`, Strength 400, `Armor=heavy`, TechLevel 3, Sight 3, `Speed=9`, `Owner=GoodGuy`, Cost 800, Points 62, ROT 5, `Crewed=yes`, `Prerequisite=weap` (GDI war factory `TDWEAP` shadows `STRUCT_WEAP`).
7. **Bundle:** `bundle_unit.py MTNK TDMTNK --tileset-donor 2TNK --build-icon BuildIcon_TD_MediumTank --text-name TEXT_UNIT_TITLE_GDI_MED_TANK --text-desc TEXT_UNIT_DESC_GDI_MED_TANK` (HD tileset + cameo). `build_tfassets.sh` `MTNK.SHP:TDMTNK.SHP` (classic) + rebuild TFASSETS.MIX.
8. **Build / deploy / smoke-test.**

---

## Vehicle-specific traps

| Trap | Symptom | Fix |
|---|---|---|
| **`Speed` copied from RA's tank** | Tank too slow/fast (TD-inauthentic) | `Speed = MPHType_value / 2`; derive from TD's `MPH_*` constant, never RA's same-role unit |
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

## The roster

**Shipped (turreted-tank trio — establishes the pipeline):** GDI Medium Tank (`TDMTNK`), NOD Light Tank (`TDLTNK`), GDI Mammoth Tank (`TDHTNK` — dual weapon + AA, §DUAL). Naming convention (Luke): faction-prefix any TD tank colliding with an RA name. **Next:** Nod Flame Tank / Stealth Tank / Recon Bike / Buggy (turret-less — simpler, no turret offset), MLRS, APC, Artillery.
