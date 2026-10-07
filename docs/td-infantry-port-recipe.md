# TD Infantry Port Recipe

**Status:** Reference. The pipeline for porting a TD infantry unit; every TD infantry unit ships
this way.

**Worked examples** (all shipped 2026-05-29): `INFANTRY_TDE1` Minigunner — first port, establishes the infantry pipeline the way TDATWR established buildings; `INFANTRY_TDE2` Grenadier (GDI-only) — its visible 8-frame tumbling-bomb bullet white-boxed, so it reuses RA's shared `Projectile=Lobbed`; `INFANTRY_TDE3` Rocket Soldier (GDI+Nod) — its **homing rotating missile is the first own-bullet visible projectile to render clean** (`Image=TDDRAGON`, reuses TDSSM's sprite, no bundling), confirming the playbook §3.25 rotating-renders / tumbling-white-boxes rule; `INFANTRY_TDE4` Flamethrower (Nod-only) — first **directional muzzle-anim** weapon: the flame jet is 8 facing-specific `ANIM_FLAME_*` anims (not a projectile), and **HD-only anims render a green placeholder until given a donor `ImageData`** — full sub-recipe in playbook **§3.26**; `INFANTRY_TDE5` Chem Warrior (Nod-only, Temple-gated) — the flamethrower's **reskinned twin** (byte-identical DO table + 660-frame layout → reuses `TdFlamethrowerDoControls` + `bundle_unit.py --tileset-donor E4`), and the unit that surfaced the **muzzle-weapon impact-explosion leak** + **classic-SHP parity** fixes (playbook §3.26 (d)/(e)).

**Read first:** `docs/td-port-playbook.md` (architecture + traps). This doc is the infantry-specific companion to `docs/td-building-separation-recipe.md`.

---

## What's different about infantry (vs buildings / vehicles)

1. **Infantry live in the UNITS tileset (`RA_UNITS.XML`).** There is **no** separate infantry tileset XML — CONFIG.MEG ships `RA_UNITS`/`TD_UNITS`, `RA_STRUCTURES`/`TD_STRUCTURES`, `RA_VFX`/`TD_VFX`, terrain/radar/UI, and infantry are `<Tile>` entries inside `*_UNITS.XML` alongside vehicles. Sprite bundling targets `RA_UNITS.XML`.
2. **`InfantryTypeClass` ctor is the short form** (18 params; `type, name, ininame, verticaloffset, primaryoffset, is_female, is_crawling, is_civilian, is_remap_override, is_nominal, is_theater, pip, controls, virtual_controls, firelaunch, pronelaunch, override_remap`). Cost/strength/weapon/owner/techlevel come from rules.ini `[section]` — same as vehicles. **Clone RA's `E1` ctor** for a rifleman-class unit.
3. **DO animation table.** `InfantryTypeClass` takes two `DoInfoStruct const*` tables — `DoControls` (classic) and `DoControlsVirtual` (GlyphX HD). `DoInfoStruct = {Frame, Count, Jump}`, same 3 ints as TD's `int[DO_COUNT][3]`. **But RA's `DoType` enum has only 21 actions; TD's had 34.** The extra 13 are the hand-to-hand set (`DO_ON_GUARD`/`DO_PUNCH`/`DO_KICK`/…) — TD declared them with sprite frames but **never triggered them in gameplay** (0 refs outside TD's enum/table; dead scaffolding). So use **RA's 21-action order with TD's frame offsets** — which is exactly what RA's own `E1DoControlsVirtual` already is, because RA's E1 *is* the TD minigunner. Pass the same table for both `controls` and `virtual` (TD's HD assets share the layout).
4. **THE KEY TRAP — donor ImageData (or the unit is invisible).** See §8. This is the one that bit TDE1.
5. **Cameo is a reference, not a bundle.** `<BuildIcon>` points at a vanilla TD `BuildIcon_TD_*` region already in the launcher PAK (defined in `CNCBUILDABLES.XML`). Nothing is shipped. All TD infantry/vehicle icons exist: `BuildIcon_TD_Minigunner/Grenadier/RocketSoldier/Flamethrower/ChemWarrior/Engineer/Commando/FlameTank/RocketLauncher`.
6. **Crew:** TD buildings spawn the minigunner as survivors (`BuildingClass::Crew_Type`, TD IniName → `INFANTRY_TDE1`).
7. **Voices: free.** GDI/Nod response VOCs are already routed to TD voices (2026-05-28 work). Any TD infantry that fires standard `Response_*` VOCs speaks TD voices automatically when `ActLike` is `HOUSE_GOOD`/`HOUSE_BAD`.

---

## Step-by-step (TDE1 worked example)

### 1. Read TD source
- `tiberiandawn/idata.cpp` — the `E1` ctor (build level, strength, sight, cost, risk/reward, ownable, weapon, speed) + the `MiniGunnerDos[DO_COUNT][3]` table.
- `tiberiandawn/const.cpp` — `Weapons[]` (`WEAPON_M16 = {BULLET_BULLET, 15, 20, 0x0200, VOC_MGUN2, ANIM_NONE}`) + `Warheads[]` (`WARHEAD_SA = {Spread 2, no wall/wood/tib, verses {0x100,0x80,0x90,0x40,0x40}}`).
- `tiberiandawn/bbdata.cpp` — the bullet (`BULLET_BULLET` = invisible, no homing/arc, `MPH_LIGHT_SPEED`, `WARHEAD_SA`, `ANIM_PIFF`).

### 2. Chain audit (MANDATORY) — do NOT borrow RA weapons
"RA has a weapon by that name" ≠ "it's TD-authentic." TD `M16` vs RA `[M1Carbine]`: Range `0x0200` (2 cells) vs `3`; Report `MGUN2` vs `GUN11`; warhead `SA` verses differ on light armor (56.25% vs RA's 60%). RA's engine doesn't even have `MGUN2`. → **full TD chain port** (`TDM16` weapon + `TDSA` warhead + `TD50cal` bullet + `MGUN2` sound), not a reuse.

### 3. Enums + heap registration
- `defines.h`: `INFANTRY_TDxx` before `INFANTRY_COUNT`; plus `WEAPON_`/`BULLET_`/`WARHEAD_`/`VOC_` entries as the chain needs.
- `idata.cpp`: `static InfantryTypeClass const TdXx(...)` (clone RA's E1) + the DO-table + `new InfantryTypeClass(TdXx)` in `Init_Heap` **last** (heap order = enum order).
- `rules.cpp` / `bbdata.cpp` / `audio.cpp`: register the weapon/warhead/bullet/VOC (enum order).
- **Heap sizing:** `InfantryTypes.Set_Heap(INFANTRY_COUNT)` (init.cpp) auto-grows with the enum — no `MAX_` bump. Weapons/warheads use rules.ini `[Maximums]` (already `Weapon=100`, `Warhead=100`); bullets use `BULLET_COUNT` (auto). All have headroom.

### 4. `IsTDPort` on the weapon (fire cadence)
`Fire_At` never toggles `IsSecondShot` for a single-shot weapon (it stays `true`), so `Rearm_Delay(true)` runs every shot. With `IsTDPort` that returns **ROF+3** (TD's single-shooter cadence) vs RA's flat **ROF**. Flag the weapon in `rules.cpp` (also makes `Speed=` parse as raw MPHType). The invisible bullet stays **non-`IsTDPort`** (no divergent flight to port; avoids the `MPH_LIGHT_SPEED`→`MPH_IMMOBILE` `Unlimbo_TD` trap, playbook §3.1).

### 5. rules.ini chain (TD-authentic values)
`[TDxx]` unit (`Strength`/`Cost`/`Sight`/`Speed`/`Owner=GoodGuy,BadGuy`/`Points`/`Primary`) + `[weapon]` + `[warhead]` + `[bullet]`. TD infantry **`Sight` is small** (E1 = 1 vs RA's 4) — TD-authentic, same as the TD buildings. `0x90`→`56%` per the existing TDHE verses rounding convention.

### 6. Audio route
Add `RAC_SFX_<ASSET>` + `RAR_SFX_<ASSET>` SFXEvents to `SFXEVENTSNONLOCALIZED.XML` (MERGE, no `--` in comments), pointing at the base-game `TDC_/TDR_SFX_<ASSET>.WAV` (the launcher resolves engine VOCs via the `RAC_`/`RAR_` prefix; TD WAVs ship in SFX3D.MEG — nothing to bundle).

### 7. Bundle sprite + cameo — `scripts/bundle_unit.py`
```
scripts/bundle_unit.py E1 TDE1 \
  --build-icon BuildIcon_TD_Minigunner \
  --text-name  TEXT_UNIT_TITLE_GDI_MINIGUNNER \
  --text-desc  TEXT_UNIT_DESC_GDI_MINIGUNNER
```
Extracts `<ASSET>.ZIP` from `TEXTURES_TD_SRGB.MEG`, repacks TD-prefixed → `UNITS/<ININAME>.ZIP`; clones the `<ASSET>` tile run in `RA_UNITS.XML` → `<ININAME>` (verbatim format, frame paths re-pointed); wires the `RABUILDABLES.XML` cameo via the documented `patch_rabuildables_xml`. (Find the build-icon name + text IDs in CONFIG.MEG's `CNCBUILDABLES.XML`.)

### 8. ⚠️ THE DONOR-IMAGEDATA FIX — do this or the unit is INVISIBLE
`InfantryTypeClass::One_Time` (idata.cpp) loads each SHP via `MFCD::Retrieve`. TD-prefixed infantry have **no SHP in any MIX** (only the TGA tileset), so `ImageData` stays `NULL` → `InfantryClass::Draw_It` bails at its NULL-shape guard → the unit **builds, is selectable, plays voices, but renders nothing**. Unlike buildings (which bypass the SHP path in Remaster), infantry need the same donor fallback as **aircraft (`aadata.cpp`) and units (`udata.cpp`)** — but `idata.cpp` shipped without one. Add after the load loop:
```cpp
InfantryTypeClass& tdxx = As_Reference(INFANTRY_TDxx);
if (tdxx.ImageData == NULL) ((void const*&)tdxx.ImageData) = As_Reference(INFANTRY_E1).ImageData;
if (tdxx.CameoData == NULL) ((void const*&)tdxx.CameoData) = As_Reference(INFANTRY_E1).CameoData;
```
The launcher's `Techno_Draw_Object` overlay then renders the real `TDxx` sprite by IniName from the tileset. **`E1` is the exact donor for any minigunner-sized infantry — it also supplies the correct render dimensions, so no `ShapeSize=` is needed** (a vehicle would need its own donor + likely `ShapeSize`).

### 9. Crew spawn
`BuildingClass::Crew_Type`: catch the `"TD"` IniName prefix → `INFANTRY_TDE1` (TD's generic building survivor is the minigunner). `STRUCT_TDFACT` keeps its 25% Engineer roll first.

### 10. Build / deploy / smoke-test
- Build: mingw remaster preset (CLAUDE.md recipe).
- Deploy: the 184 MB front-end crest atlas (`MT_COMMANDBAR_COMMON.TGA`) **must live in `resources/.../ART/TEXTURES/SRGB/`** (gitignored, `.gitignore` line 15) — then *both* rebuilds and `deploy.sh` repackage it and `rsync --delete` keeps it. **If it's only in `build/` and not in `resources/`, any rebuild drops it and `deploy.sh --delete` then wipes it off the Deck** (this bit E2 2026-05-29 — restored from `/tmp/atlas_v3.tga`). Always `ls -la resources/.../MT_COMMANDBAR_COMMON.TGA` (≈177 MB) before deploying; regen via `scripts/frontend_atlas_build.py` if absent.
- Smoke: builds from the barracks (TDPYLE/TDHAND), **renders at correct scale**, fires the TD weapon (sound/range/damage), TD voice on select/move, crew spawn on building death.

---

## Infantry-specific traps (summary)

| Trap | Symptom | Fix |
|---|---|---|
| **No donor ImageData** | Builds, selectable, voiced — but **invisible** | §8: copy `E1`'s `ImageData`/`CameoData` in `One_Time` |
| **DO_COUNT mismatch** | Compile error / mis-mapped animations | RA's `DoType` = 21 actions, not TD's 34 (hand-to-hand was dead in TD); use RA's order + TD frames |
| **Borrowed RA weapon** | Wrong range / sound / armor curve | Chain-audit from TD source; port `TDxx` weapon+warhead+bullet+sound |
| **Visible custom bullet** | Projectile renders as a **white box** | 32-frame rotating missiles port as own bullets; tumbling/arcing bombs reuse RA's `Projectile=Lobbed` (playbook §3.25) |
| **Muzzle-anim weapon (flame)** | Green placeholder box where the jet should be | HD-only anims have NULL `ImageData` → donor-ImageData in `AnimTypeClass::One_Time`; dispatch directional anim via `Fire_Direction()`; TD-prefix the names (playbook §3.26) |
| **Atlas only in `build/`** | Crest atlas wiped off Deck on rebuild+deploy | Keep `MT_COMMANDBAR_COMMON.TGA` in `resources/` (gitignored), not just `build/` |

**EA's HD frames as a reference.** `scripts/ea_infantry_extract.py` packages an EA infantry unit's HD frames
from the texture MEGs (PNG plus META, as shipped), a contact sheet, one strip per sequence and its DO table
quoted from EA's source, with the ranges checked, for fitting new infantry art against.

---

## The roster — COMPLETE (2026-05-30)

**Shipped:** E1 Minigunner, E2 Grenadier, E3 Rocket Soldier, **E4 Flamethrower** (first muzzle-anim weapon — §3.26), **E5 Chem Warrior** (Nod, Temple-gated; flamethrower's reskinned twin — §3.26 d/e), **E6 Engineer** (no weapon; faction-conditional capture — §3.27), **Commando** (125-dmg sniper + C4 + the iconic RAMBO voices). The full TD infantry roster is ported.

**Commando (`INFANTRY_TDRMBO`) — key facts:**
- Weapon is **`WEAPON_RIFLE`** (125-dmg `BULLET_SNIPER`), **NOT M16** — our own roster doc had it wrong (playbook §2.1). Reuses the invisible `BULLET_TD50cal`; new `WARHEAD_TDHollow` (`{1.0,0.03,0.03,0.03,0.03}`) one-shots infantry / ~nil vs armor. Sound `RAMGUN2` (base asset, `RAC/RAR_SFX_RAMGUN2`).
- **C4 building-destroy = `C4=yes` → `IsBomber`.** TD hardcodes C4 to `INFANTRY_RAMBO`; RA generalised it to the flag — same mechanic, **zero runtime code**. (`IsBomber` also implies `IsCapture`, but `What_Action` routes a bomber to ACTION_SABOTAGE, so it never hits the engineer-capture path.)
- **Both factions build it** via `Prerequisite=atek` — the existing Eye(GDI)/Temple(Nod) `STRUCT_ADVANCED_TECH` remap (house.cpp), same idiom as TDMCV and RA's Tanya. RA's `Prerequisite=` is an AND-list, so this is the only way to OR two faction tech-centres.
- **RAMBO one-liners already ship in the base `SFX2D_EN-US.MEG`** (`TDC/TDR_SFX_CMD_<NAME>_EN-US`). Wired as `RAC/RAR_SFX_TD<NAME>` localized SFXEvents (IN_NOVAR → no `.V0x` suffix, name passes through clean) + a `*this == INFANTRY_TDRMBO` case in `Response_Select/Move/Attack` **before** the GDI/Nod intercept. `PIP_COMMANDO`. No new asset bundling for voices.
- **468-frame sprite has no exact-count RA donor** → `bundle_unit.py` now slices a larger donor (E1, 532) down to the ZIP frame count (new `frame_count` param). Generalises to any future unit without a matching donor.

**Engineer (`INFANTRY_TDE6`) — key facts:**
- No weapon; `Infiltrate=yes` → `IsCapture`. **BUT capture is `INFANTRY_RENOVATOR`-gated** across ~15 sites — a new engine type must be added at the **execution** (`infantry.cpp` Per_Cell_Process), the **cursor** (`What_Action`), and **AI capture-targeting** (`foot.cpp`) or it does not capture *at all*. See §3.27.
- **Faction-conditional capture:** GDI/Nod (`House->ActLike` GOOD/BAD) capture **single** (one engineer, any building health = TD); Allied/Soviet keep RA's Aftermath **multi**-engineer (damage to ConditionRed, then take). Gate is on the engineer's owner.
- **Capture-only** — the RA engineer's friendly mega-repair is gated to RENOVATOR, so TDE6 has no repair action (TD-authentic).
