# TD-to-RA Port Playbook

**Audience:** future-self and future-claude starting a new TD-entity port. Read this *first* — it covers every dead end we hit during the TDATWR session (2026-05-22) so you don't repeat them.

**Scope:** porting a TD building, weapon, bullet, warhead, anim, or aircraft into our RA-based mod as a fully separated `TDxxxx` entity with TD-faithful runtime behavior and visuals.

**Companion deep-dives:**
- `docs/td-atwr-deep-dive.md` — TDATWR worked example end-to-end
- `docs/td-building-separation-recipe.md` — building-specific separation steps
- `docs/td-audio-routing-recipe.md` — audio MERGE pattern + SFXEVENTSNONLOCALIZED.XML

---

## 1. The architecture (Option A)

**One sentence:** TD-prefixed entities are still instances of RA's classes (`BuildingClass`, `BulletClass`, etc.) and live in the same heaps for interop, **but every method with TD-vs-RA behavior difference dispatches to a verbatim TD port (`Method_TD()`) gated by an `IsTDPort` flag**.

**Why:** the project aims for 4-faction play (GDI/Nod/Allies/Soviet). Fully parallel TDxxxxClass hierarchies would force shim code for every cross-faction interaction. Option A keeps interop free (everything's still a normal `BuildingClass`/`BulletClass`) while making TD behavior bit-exact.

**What's shared (NOT a leak):** class memory layout, heaps, targeting, save/load, sidebar UI, multiplayer sync, damage application across factions.

**What's NOT shared (must be TD-ported per entity):**
- `BulletClass::AI`, `BulletClass::Unlimbo` (homing, scatter, arming, trail spawn)
- `TechnoClass::Fire_At`, `TechnoClass::Rearm_Delay`, `TechnoClass::Can_Fire` where TD differs
- `BuildingClass::Mission_Attack`, `Mission_Guard`, `Shape_Number`, `Drop_Debris`
- Constructor field semantics that exist in TD but not in RA

**The gate:** add `IsTDPort` flag to the relevant base TypeClass(es) and dispatch at the top of every overridden method:

```cpp
void BulletClass::AI(void) {
    if (Class->IsTDPort) { AI_TD(); return; }
    // existing RA logic continues
}
```

---

## 2. End-to-end recipe (numbered, in order)

For a generic TD entity (adjust for what you're porting — building, bullet, weapon, etc.):

### 2.1 — Read TD source FIRST

Before writing any code, find and read the TD source for:
- The class declaration (`reference/vanilla-conquer/tiberiandawn/<type>.h`)
- The type instantiation (`reference/vanilla-conquer/tiberiandawn/<x>data.cpp` — `bdata.cpp` for buildings, `bbdata.cpp` for bullets, etc.)
- The dispatch sites in code (`reference/vanilla-conquer/tiberiandawn/<x>.cpp` — `building.cpp`, `bullet.cpp`, etc.)

Per [[feedback-review-td-source-first]]: TD source is the spec. Don't reverse-engineer from RA half-implementations.

### 2.2 — Run the chain audit (MANDATORY before any rules.ini edit)

Per [[feedback-td-building-chain-audit-ritual]], dump the full chain visibly:

```
Chain audit — [TDXXXX]:
  Primary=<Weapon>                     [TD-prefixed ✓ / RA-vanilla LEAK]
    Projectile=<Bullet>                [TD-prefixed ✓ / LEAK]
    Warhead=<Warhead>                  [TD-prefixed ✓ / LEAK]
    Report=<Audio>                     [TD-prefixed ✓ / shared/LEAK]
    Anim=<Anim>                        [TD-prefixed ✓ / LEAK]
    Burst=<n>                          [matches TD IsTwoShooter? ✓ / leak]
  Secondary=...                        [same audit if present]
```

Any RA-vanilla section in the chain = must port (don't ship leaks).

### 2.3 — Add enum + heap registration (DLL-side)

Adding a new `[TDSection]` is **never pure rules.ini**. The heap allocator silently fails for unregistered types (per [[project-mod-type-heap-sizing]]). Each new entity needs:

| Section type | Enum entry | Explicit registration |
|---|---|---|
| Bullet `[TDxxx]` | `BULLET_TDxxx` before `BULLET_COUNT` in `defines.h` | `new BulletTypeClass("TDxxx")` in `bbdata.cpp::Init_Heap` |
| Warhead `[TDxxx]` | `WARHEAD_TDxxx` before `WARHEAD_COUNT` in `defines.h` | `new WarheadTypeClass("TDxxx")` in `rules.cpp:~651` |
| Weapon `[TDxxx]` | `WEAPON_TDxxx` before `WEAPON_COUNT` in `defines.h` | `new WeaponTypeClass("TDxxx")` in `rules.cpp:~710` |
| Building `[TDxxx]` | `STRUCT_TDxxx` before `STRUCT_COUNT` in `defines.h` | `static BuildingTypeClass const ClassTdXxx(...)` in `bdata.cpp` + heap registration; `MAX_BUILDING_TYPES = STRUCT_COUNT + 50` already covers this |
| Unit | `UNIT_TDxxx` before `UNIT_COUNT` | `static UnitTypeClass const ClassTdXxx(...)` in `udata.cpp` |
| Aircraft | `AIRCRAFT_TDxxx` before `AIRCRAFT_COUNT` | `static AircraftTypeClass const ClassTdXxx(...)` in `aadata.cpp` |
| Anim | `ANIM_TDxxx` before `ANIM_COUNT` | `static AnimTypeClass const ClassTdXxx(...)` in `adata.cpp` |
| Infantry | `INFANTRY_TDxxx` before `INFANTRY_COUNT` | `static InfantryTypeClass const ClassTdXxx(...)` in `idata.cpp` |

**Symptom of forgetting:** placement crashes (NULL pointer in WarheadPtr / BulletPtr / weapon binding on first deref).

### 2.4 — Set `IsTDPort = true` on the TD entity

For bullets/weapons (and any future class with the flag), set this after the `new` call in the registration block:

```cpp
// In bbdata.cpp::Init_Heap after the registrations
BulletTypes.Ptr((int)BULLET_TDxxx)->IsTDPort = true;
```

```cpp
// In rules.cpp after the new WeaponTypeClass("TDxxx") calls
WeaponTypeClass::As_Pointer(Weapon_From_Name("TDxxx"))->IsTDPort = true;
```

`IsTDPort` is **not** parseable from rules.ini — it's an engine-level dispatch gate, not a tunable.

### 2.5 — Author rules.ini with TD-source raw values

For TD-port weapons: **`Speed=` is raw MPHType** when the weapon is `IsTDPort=true` (see §3.1). Use values directly from TD source:
- `MPH_ROCKET = 60` → `Speed=60`
- `MPH_VERY_FAST = 100` → `Speed=100`
- `MPH_LIGHT_SPEED = 255` → `Speed=255`

For non-TD-port (RA-vanilla) weapons: `Speed=` is a 0-100 percentage, convert via `raw * 100 / 256`.

Add a comment in rules.ini citing the TD source location so the value is traceable:

```ini
; Speed=60 is TD's raw MPH_ROCKET (tiberiandawn/defines.h:627).
; TDTowTwo is flagged IsTDPort=true in rules.cpp so WeaponTypeClass::Read_INI
; parses this as raw MPHType (TD source convention).
Speed=60
```

### 2.6 — Bundle the assets via the vanilla MEG pipeline

Don't use TD-Assets workshop content as the source — our mod must be self-contained. Use vanilla MEG extraction:

**For buildings** (use `scripts/bundle_assets.py`):
```bash
scripts/bundle_assets.py TDxxx
```
Handles ZIP extraction, TD-prefix internal rename, RA_STRUCTURES.XML patch, RABUILDABLES.XML cameo block.

**For bullets** (manual — no bundler script yet):
```bash
# 1. Extract from vanilla MEG
python3 scripts/meg_extract.py extract \
  ~/.steam/steam/steamapps/common/CnCRemastered/Data/TEXTURES_TD_SRGB.MEG \
  "<NAME>" /tmp/td-extract/

# 2. Repack with TD-prefixed internal TGAs
python3 -c "
import sys; sys.path.insert(0, 'scripts')
from bundle_assets import repack_zip_with_prefix
repack_zip_with_prefix(
    '/tmp/td-extract/<NAME>.ZIP',
    'resources/remaster_mods/Vanilla_RA/Data/ART/TEXTURES/SRGB/RED_ALERT/VFX/TD<NAME>.ZIP',
    '<name>', 'td<name>')
"

# 3. Patch RA_VFX.XML with 32 shape entries (use the patching pattern from
#    bundle_assets.py:215-241 as the model)
```

**For all entities**, the registration XML must be in CONFIG.MEG-override format (full `<Tilesets><TilesetTypeClass name="RA_VFX">...</TilesetTypeClass></Tilesets>` envelope). Mod-additions format (`<Tiles>` only) **doesn't get loaded by the launcher** — confirmed empirically. Always patch the existing `RA_VFX.XML` / `RA_STRUCTURES.XML` / `RA_UNITS.XML` (extracted from CONFIG.MEG) rather than creating standalone XMLs.

### 2.7 — Apply the donor-ImageData pattern (CRITICAL for bullets/anims/aircraft)

Per [[reference-mfcd-donor-imagedata-pattern]] — without this, the missile/anim/plane will be invisible even with the tileset registered correctly.

In the relevant `One_Time()` after the standard SHP-loading loop, copy a vanilla donor's `ImageData` pointer:

```cpp
// bbdata.cpp::BulletTypeClass::One_Time, after the standard loop
BulletTypeClass const& donor = As_Reference(BULLET_HEAT_SEEKER);  // any visible vanilla bullet
BulletTypeClass& tdxxx = As_Reference(BULLET_TDxxx);
if (tdxxx.ImageData == NULL) {
    ((void const*&)tdxxx.ImageData) = donor.ImageData;
}
```

Same for `aadata.cpp` (aircraft, donor `AIRCRAFT_BADGER`), `adata.cpp` (anims, donor `ANIM_FBALL1`).

**Buildings DON'T need this** — they bypass the SHP path entirely in Remastered mode.

### 2.8 — Port TD's verbatim function bodies

For every method on the entity's class that has TD-vs-RA divergence:
1. Read TD's body in `reference/vanilla-conquer/tiberiandawn/<file>.cpp`
2. Create `Method_TD()` next to RA's `Method()`
3. Port TD's body line-for-line, with **inline comments** at every symbol rename or RA-plumbing addition
4. Dispatch from `Method()`: `if (Class->IsTDPort) { Method_TD(); return; }` at the top

**Common symbol renames TD→RA** (record in port doc):
- `Class->Warhead` (TD class-level) → `Class->ClassWarhead` (we added this field to avoid RA collision)
- `Class->Explosion` → `Class->ImpactAnim` (we added — RA's `Explosion=` is on warheads not bullets)
- `Class->Range` (TD bullet field) → `Class->BulletRange` (avoid weapon `Range=` collision)
- `Class->MaxSpeed` (TD class-level) → instance `MaxSpeed` (RA stores per-instance from weapon)
- `Altitude` (TD) → `Height` (RA)
- `GRAVITY` (TD #define) → `Rule.Gravity` (RA runtime-config)
- `Delete_This()` (TD method) → `delete this` (RA idiom)
- `MIN/MAX` macros → `min/max` (RA's std-style)
- TD's `BULLET_TOW` enum value → `BULLET_SSM` (our TD-port BulletType)
- TD's `BULLET_BULLET` / `BULLET_GRENADE` / `BULLET_NAPALM` — commented placeholders (no TD-port for these)

### 2.9 — Audio routing (if needed)

Per [[project-td-audio-routing-recipe]]: MERGE the base `SFXEVENTSNONLOCALIZED.XML`, never replace. Add VOC_TD_* enum entries. Bundle WAVs in `Data/AUDIO/`.

### 2.10 — Verify with the chain-audit ritual repeated

After all changes, run the chain audit again. Every line should show `[TD-prefixed ✓]`. Zero LEAKs.

### 2.11 — Build, deploy, smoke-test

- Build: `cmake --workflow --preset remaster` (with toolchain env per CLAUDE.md)
- Deploy: `./deploy.sh --yes`
- Smoke-test by placing the entity in-game on the Deck

### 2.12 — Side-by-side verification vs actual TD

Place the entity on our Deck. Run actual TD on the second Deck. Compare:
- Build animation sequence
- Idle visual
- Firing visual (sprite, sound, salvo count, salvo cadence)
- Damage / impact behavior
- Death / sell sequence
- Any state-machine animations (charge-up, recoil, etc.)

---

## 3. The N traps that will catch you (with fixes)

### 3.1 — `Speed=` parsing convention differs TD vs RA

**Trap:** TD source has `MaxSpeed = MPH_ROCKET = 60` (raw 0-255 value). RA's `Get_MPHType` interprets `Speed=N` from rules.ini as a 0-100 *percentage* scaled to 0-256. Copying `Speed=60` from TD source into a vanilla RA-style weapon gives MaxSpeed=153 (= 60% × 255), **not** 60.

**Symptom (moderate raw values like 60):** missiles 2.5× too fast, overshoot during arming, fail to hit close-range targets (Timer expires before proximity fuse triggers).

**Symptom (raw value of 100, intending MPH_VERY_FAST):** *Worse and very misleading.* `Speed=100` parses as 100% → MaxSpeed=255=MPH_LIGHT_SPEED. In `Unlimbo_TD` (bullet.cpp:1022-1023) this triggers `if (speed == MPH_LIGHT_SPEED) speed = MPH_IMMOBILE;` — bullet velocity becomes 0. Bullet sits at the launcher, fuse expires after a few frames, the AA-distance damage branch (bullet.cpp:1268, `Distance(TarCom) < 0x80`) is skipped because the bullet is nowhere near the aircraft, and the impact anim plays on top of the firer. Player sees: missile emerges from turret, vanishes immediately, 0 damage. Looks like a rendering or warhead bug; is actually this Speed= bug. TDSAM/TDNike hit this 2026-05-25.

**Fix:** add `IsTDPort` flag on `WeaponTypeClass`. In `Read_INI`, branch:
```cpp
if (IsTDPort) {
    MaxSpeed = (MPHType)ini.Get_Int(Name(), "Speed", (int)MaxSpeed);  // raw
} else {
    MaxSpeed = ini.Get_MPHType(Name(), "Speed", MaxSpeed);  // percentage
}
```

Already implemented in `weapon.cpp:202-210`. Just flag your new TD weapon and write the raw TD-source value.

See [[reference-ra-mphtype-ini-format]].

### 3.2 — Type-heap registration silently fails

**Trap:** Adding `[TDxxx]` to rules.ini without adding the enum + explicit `new XxxTypeClass("TDxxx")` registration in the right `data.cpp` or `rules.cpp`.

**Symptom:** crash on placement (NULL pointer when the weapon/bullet/warhead is dereferenced).

**Fix:** §2.3 table above. Every section type needs enum entry + explicit registration.

See [[project-mod-type-heap-sizing]].

### 3.3 — Donor ImageData pattern for non-building entities

**Trap:** Bullets / anims / aircraft with TGA-only assets (no `.SHP` in any MIX file) have `Class->ImageData == NULL` after `One_Time` runs. `Draw_It` bails at `if (!shapeptr) return;` and the entity is invisible.

**Symptom:** entity behaves correctly (audio, damage, animation trail), but its body sprite is invisible. For bullets specifically: smoke trail visible, missile body absent.

**Fix:** Copy a vanilla donor's `ImageData` pointer in `One_Time` after the loop (§2.7).

See [[reference-mfcd-donor-imagedata-pattern]].

### 3.4 — Tileset XML format and location

**Trap:** Standalone `TDxxx.XML` files in `TILESETS/<KIND>/` subdirs **are not loaded** by the launcher. Mod-additions format (`<Tiles>...</Tiles>` without `<Tilesets><TilesetTypeClass>` envelope) **also not loaded** as standalone files.

**Symptom:** asset registration appears correct but the entity's sprite/visual doesn't render.

**Fix:** Always patch the CONFIG.MEG-extracted base XML (`RA_VFX.XML`, `RA_STRUCTURES.XML`, `RA_UNITS.XML`) and ship the patched copy in `resources/.../Data/XML/TILESETS/`. The launcher overrides the CONFIG.MEG version with the mod's. Full `<Tilesets><TilesetTypeClass name="RA_VFX"><RootTexturePath>Red_Alert\VFX</RootTexturePath><Tiles>...` envelope required.

### 3.5 — Buildings don't have `IsTwoShooter` field

**Trap:** TD's `STRUCT_ATOWER` has `IsTwoShooter=true` in its constructor. RA's `BuildingTypeClass` constructor has no such field. Naive ports leave salvo count as 1.

**Fix:** Use `Burst=2` on the weapon (RA's mechanism — `WeaponTypeClass.Burst > 1` makes `Is_Two_Shooter()` return true, which triggers the `IsSecondShot` toggle in `Fire_At`). Engine path works correctly; just set the weapon flag instead of building flag.

**Verified working** for TDATWR via `[TDTowTwo] Burst=2` — produces 2 missiles per engagement, 2 audio pings.

### 3.6 — `Rearm_Delay` timing TD-vs-RA

**Trap:** TD's `Rearm_Delay` returns 9 (short, first-shot-in-salvo) and ROF+3 (long, between salvos). RA's returns 3 and ROF respectively. Naive ports get tighter salvo cadence than TD.

**Fix:** Already implemented in `techno.cpp:3096-3119` — `Rearm_Delay` branches on `weapon->IsTDPort` and uses TD's 9 / ROF+3 timing for TD-port weapons.

### 3.7 — Smoke trail vs missile sprite

**Trap:** TD bullets with `Animates=yes` spawn `ANIM_SMOKE_PUFF` as the trail. This happens in `BulletClass::AI` regardless of whether `ImageData` is set. So the trail can be visible while the sprite is invisible (per §3.3).

**Don't confuse:** trail visible ≠ sprite visible. Test both independently.

### 3.8 — RA-only enum values in TD-port code

**Trap:** TD's `bullet.cpp::AI` references `BULLET_TOW`, `BULLET_SAM`, `BULLET_BULLET`, `BULLET_GRENADE`, `BULLET_NAPALM` for special-case behavior. RA's enum has different names.

**Fix:** Map TD enum values to closest RA equivalent (or comment as placeholder if no equivalent exists). Common mappings:
- `BULLET_TOW` → `BULLET_SSM` (our TDSSM is the TD-port equivalent)
- `BULLET_SAM` → `BULLET_AAMISSILE` (closest RA equivalent)
- `BULLET_BULLET` → comment-only (no TD-port for small-arms invisible bullet yet)

### 3.9 — Build pipeline: POST_BUILD copy skipped on incremental builds

**Trap:** `./deploy.sh --no-build` skips the build entirely AND skips the `resources/` → `build/` copy step. Pure rules.ini edits don't make it to the deploy bundle.

**Trap variant:** running `./deploy.sh --yes` (with build) AFTER recent successful build: ninja considers the DLL up-to-date, skips relink, and the CMake `POST_BUILD` resources-copy step doesn't fire because it's tied to the DLL link.

**Fix:** `touch redalert/<any>.cpp` before deploy to force a relink and trigger the staging step.

### 3.10 — No RA-engine logic for TD entities

**Trap:** When debugging TD-port behavior, falling back to "tune the rules.ini value harder" or "find which RA flag/scatter constant gets us close." Drift.

**Fix:** Per [[feedback-no-donor-for-td-separation]] / [[feedback-td-building-chain-audit-ritual]]: when TD-port runtime behavior differs from TD, the answer is **port TD's engine code body** into a `_TD()` variant. Patching RA's native function with TD-flavored tweaks is the donor anti-pattern at the engine level.

The exception is plumbing the launcher requires (e.g. `Map.Submit` for layer system, `Height` init for flight altitude tracking). Flag those inline with comments.

### 3.11 — Separated TD building doesn't satisfy vanilla-RA prerequisites

**Trap:** Aircraft/units that require a vanilla RA building (e.g. helicopters require `STRUCT_HELIPAD`, RA Allied/Soviet infantry require `STRUCT_TENT` / `STRUCT_BARRACKS`, vehicles require `STRUCT_WEAP`) silently disappear from the sidebar when the player builds the TD-separated equivalent (TDHPAD, TDPYLE, TDHAND, TDWEAP/TDAFLD) instead of the vanilla one. The TD building has its own `Type` enum past `STRUCT_COUNT`, so the prereq check `Has_Building_Active(STRUCT_HELIPAD)` returns false even though semantically the player has a helipad.

**Symptom:** Build a TDHPAD, get the free helicopter — but the helicopter cameos never appear in the sidebar. (Or: GDI builds TDPYLE, the Allied infantry roster never unlocks. Etc.)

**Fix:** Extend `HouseClass::Can_Build`'s prerequisite-equivalence block at `house.cpp:986+`. Add a cached IniName→Type lookup for the new TD building plus a `if (t == STRUCT_VANILLA_NAME && tdNNNN_type >= 0 && Has_Building_Active(tdNNNN_type)) continue;` branch. The existing TDPYLE/TDHAND/TDWEAP/TDAFLD/TDHPAD entries are the worked examples.

**Why it's silent:** No engine error, no warning — `Can_Build` just returns false. The cameo is conditionally hidden by the sidebar, so you only notice via "thing I expected to be buildable isn't there."

This will eventually be replaced by a `BehavesLike=` rules.ini field in D2; until then, every new separated TD building that shadows a vanilla RA factory needs one entry here.

### 3.11b — Audio override mechanics (mod XML vs WAV-file replacement)

Two distinct override paths, validated 2026-05-26 during TD EVA + radar SFX work:

| Asset class | Override mechanism | Side-conditional? |
|---|---|---|
| **VOC sound effects** fired via DLL `Sound_Effect(VOC_TD_*)` | Mod-side `SFXEVENTSNONLOCALIZED.XML` adds new `RAC_SFX_<NAME>` / `RAR_SFX_<NAME>` entries pointing at TD assets. | **Yes** — DLL chooses which VOC enum to fire based on `PlayerPtr->ActLike`. |
| **VOX EVA speech** fired via `Speak(VOX_*)` → `On_Speech` | Mod-side `SFXEVENTSLOCALIZED.XML` adds `LocalizedSFXEvent` entries (engine sends TD-prefixed name; launcher resolves). | **Yes** — `On_Speech` chooses Speech[]→SpeechTD[] based on `player_ptr->ActLike`. See §3.12 routing recipe below. |
| **Launcher-owned SFX** (radar on/off, ambient UI) | Mod-side WAV with same filename as launcher's hardcoded sample (case-insensitive) in `DATA/AUDIO/`. Reillsss CnCinRA precedent. | **No.** Launcher's state-driven SFX dispatch happens entirely client-side; DLL's `Radar_Activate()` isn't called in REMASTER_BUILD. SFXEvent XML override of existing same-named entries doesn't load either — mod XML is additive-only for SFXEvents. The WAV-file swap is global (all sides). Side-conditional requires launcher source modification. |

**Test sequence** to identify which class you're dealing with: drop a diagnostic `fprintf` into the DLL hook (Sound_Effect call site, Speak call site, or the state-change function). If the log fires → DLL-driven, side-conditional is achievable. If silent → launcher-driven, WAV-file replacement is your only mod-side lever.

### 3.12 — `Who_Can_Build_Me` evicts cameos right after `Can_Build` adds them

**Trap:** §3.11's prereq equivalence makes `Can_Build` return true and `Update_Buildables` calls `Sidebar_Glyphx_Add` successfully — but the cameo still doesn't appear (or appears for one frame then vanishes). The next `Sidebar_Glyphx_Recalc` tick (called every `Glyphx_Queue_AI` from `dllinterface.cpp:1990`) runs `StripClass::Recalc` → `tech->Who_Can_Build_Me(true, false, house) != NULL`. If that returns NULL, the entry is evicted.

`ObjectTypeClass::Who_Can_Build_Me` (`object.cpp:2403+`) iterates buildings and checks `building->Class->ToBuild == RTTI`. That check passes for TD-separated factories. **But** the function then has a "HACK ALERT" branch at `object.cpp:2436-2443` that hardcodes `STRUCT_HELIPAD` and `STRUCT_AIRSTRIP` to restrict aircraft to the matching factory kind:

```cpp
if (What_Am_I() == RTTI_AIRCRAFTTYPE) {
    AircraftTypeClass* air = (AircraftTypeClass*)this;
    if ((*building == STRUCT_HELIPAD && !air->IsFixedWing)
        || (*building == STRUCT_AIRSTRIP && air->IsFixedWing)) {
        ...
    }
}
```

A separated `STRUCT_TDHPAD` fails the `*building == STRUCT_HELIPAD` test — Recalc evicts every rotary cameo.

**Symptom:** Cameos appear briefly then disappear, OR (in practice) never visible because Recalc fires before the first paint. Logs show `Sidebar_Glyphx_Add` reporting `added=1` for HELI but the launcher's sidebar stays empty.

**Fix:** Extend the hardcoded check to include the separated equivalent:
```cpp
if (((*building == STRUCT_HELIPAD || *building == STRUCT_TDHPAD) && !air->IsFixedWing)
    || (*building == STRUCT_AIRSTRIP && air->IsFixedWing)) {
```

**Why it's a sister-bug to §3.11:** Two hardcoded RA-side paths gate cameo visibility — `HouseClass::Can_Build` (add) and `ObjectTypeClass::Who_Can_Build_Me` (don't evict). Adding §3.11's equivalence without §3.12's fix gives you cameos that get added then immediately stripped. Always patch both whenever a TD-separated building shadows a vanilla RA factory role (helipad, airstrip, future barracks/weapon-factory equivalents). TDAFLD hit the same shape of bug and resolved it via `Find_Docking_Bay`'s IniName fallback — the underlying lesson is identical.

---

## 4. Templates to copy

### 4.1 — Bullet TD-port: add field, set on registration, dispatch

**Step 1:** In `redalert/type.h`, add to `BulletTypeClass`:
```cpp
unsigned IsTDPort : 1;
```
plus any TD-source-specific fields the TD code references (we added `IsHoming`, `ClassWarhead`, `ImpactAnim`, `BulletRange`).

**Step 2:** In `redalert/bbdata.cpp`, constructor init:
```cpp
, IsTDPort(false)
, IsHoming(false)
, ClassWarhead(WARHEAD_NONE)
, ImpactAnim(ANIM_NONE)
, BulletRange(0)
```

**Step 3:** In `Read_INI`, parse the new fields:
```cpp
IsHoming = ini.Get_Bool(Name(), "Homing", IsHoming);
ClassWarhead = ini.Get_WarheadType(Name(), "Warhead", ClassWarhead);
ImpactAnim = ini.Get_AnimType(Name(), "ImpactAnim", ImpactAnim);
BulletRange = ini.Get_Int(Name(), "BulletRange", BulletRange);
```

**Step 4:** In `bbdata.cpp::Init_Heap` after the registrations:
```cpp
BulletTypes.Ptr((int)BULLET_TDxxx)->IsTDPort = true;
```

**Step 5:** In `bullet.cpp::AI` and `bullet.cpp::Unlimbo`, dispatch at top:
```cpp
if (Class->IsTDPort) { AI_TD(); return; }
// existing RA logic
```

**Step 6:** Port TD's body verbatim as `AI_TD()` / `Unlimbo_TD()` per §2.8 symbol renames.

**Step 7:** Donor ImageData per §2.7.

### 4.2 — Weapon TD-port: add field, set on registration, dispatch parse

**Step 1:** In `redalert/weapon.h`, add `unsigned IsTDPort : 1;` to `WeaponTypeClass`.

**Step 2:** In `redalert/weapon.cpp` constructor, `IsTDPort(false)`.

**Step 3:** In `WeaponTypeClass::Read_INI`, dispatch on IsTDPort for `Speed=` parsing:
```cpp
if (IsTDPort) {
    MaxSpeed = (MPHType)ini.Get_Int(Name(), "Speed", (int)MaxSpeed);
} else {
    MaxSpeed = ini.Get_MPHType(Name(), "Speed", MaxSpeed);
}
```

**Step 4:** In `rules.cpp` after `new WeaponTypeClass("TDxxx")`:
```cpp
WeaponTypeClass::As_Pointer(Weapon_From_Name("TDxxx"))->IsTDPort = true;
```

### 4.3 — `Rearm_Delay` already does the right thing

Once the weapon is `IsTDPort=true`, the existing branch in `techno.cpp:3096-3119` returns TD's timing automatically. Nothing else to do.

---

## 5. Final verification checklist

Before declaring a TD-entity port "100% authentic":

- [ ] Chain audit shows zero LEAKs (all sections TD-prefixed)
- [ ] Enum entries added to `defines.h` before the `_COUNT` sentinel
- [ ] Explicit `new XxxTypeClass(...)` registration in the right `data.cpp` / `rules.cpp`
- [ ] `IsTDPort = true` set after registration (for classes that have the flag)
- [ ] Donor `ImageData` pointer copied if not a building (bullet/anim/aircraft)
- [ ] Rules.ini values are TD-source raw values (with conversion comments if non-IsTDPort)
- [ ] Tileset XML patched into the CONFIG.MEG-extracted base file (full envelope)
- [ ] Asset ZIP extracted from vanilla MEG (not TD-Assets workshop), repacked with TD-prefix internals
- [ ] TD method bodies ported verbatim into `Method_TD()` variants, dispatch added at top of `Method()`
- [ ] Build succeeds (mingw cross-compile, no warnings on the ported code)
- [ ] Deploy bundles all files (~10MB+ rsync indicates fresh DLL; ~2KB indicates skipped staging — see §3.9)
- [ ] In-game smoke test: build the entity, observe firing/damage/visual/audio/death
- [ ] Side-by-side vs actual TD: behavior matches frame-by-frame

---

## 6. Cross-reference

**Memory entries (load automatically per session):**
- [[project-td-port-architecture]] — Option A architecture, why it was chosen
- [[feedback-td-building-chain-audit-ritual]] — mandatory output ritual before any TD change
- [[feedback-no-donor-for-td-separation]] — no RA-implementation reuse principle
- [[reference-ra-mphtype-ini-format]] — Speed unit conversion
- [[reference-mfcd-donor-imagedata-pattern]] — donor ImageData for non-building TD entities
- [[project-mod-type-heap-sizing]] — enum + heap registration requirement
- [[project-td-audio-routing-recipe]] — SFXEVENTSNONLOCALIZED MERGE pattern
- [[project-td-prefix-convention]] — every TD entity gets TD prefix

**TD source paths (read these as the spec):**
- `reference/vanilla-conquer/tiberiandawn/bdata.cpp` — building Class declarations
- `reference/vanilla-conquer/tiberiandawn/bbdata.cpp` — bullet Class declarations
- `reference/vanilla-conquer/tiberiandawn/udata.cpp` — unit Class declarations
- `reference/vanilla-conquer/tiberiandawn/aadata.cpp` — aircraft Class declarations
- `reference/vanilla-conquer/tiberiandawn/adata.cpp` — anim Class declarations
- `reference/vanilla-conquer/tiberiandawn/idata.cpp` — infantry Class declarations
- `reference/vanilla-conquer/tiberiandawn/const.cpp` — `Weapons[]`, `Warheads[]` tables
- `reference/vanilla-conquer/tiberiandawn/audio.cpp` — `SoundEffectName[]` table
- `reference/vanilla-conquer/tiberiandawn/defines.h` — `MPHType` constants, `STRUCT_*`, `BULLET_*`, `WEAPON_*`, `WARHEAD_*`, `ANIM_*` enums
- `reference/vanilla-conquer/tiberiandawn/building.cpp`, `bullet.cpp`, `techno.cpp`, etc. — dispatch site bodies to port verbatim

**Working examples in our codebase:**
- TDATWR (full port, 2026-05-22): `docs/td-atwr-deep-dive.md`
- TDOBLI (M5 vertical slice, 2026-05-21): `docs/td-obli-verification.md`
- TDC17 (cargo plane with donor-ImageData pattern): `aadata.cpp:442-459`
- M3 separated buildings: `docs/building-separation-plan.md`

---

## 7. When to update this playbook

Every time we discover a new trap or refine a pattern, append it to §3 (the traps section) with:
- **Trap:** one-sentence description
- **Symptom:** what you observe in-game
- **Fix:** the code/data change

Living document — keep it ahead of the implementation, not behind.
