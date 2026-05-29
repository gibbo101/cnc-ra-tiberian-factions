# TDATWR port — TD-source-grounded deep dive

> **RESOLVED — separated + shipped (v0.50).** TDATWR now runs its own `ClassTdAtwr` code path and binds `Primary=TDTowTwo` in rules.ini — wholesale TD port, no RA `ClassAAGun` shaping. The body below is retained as TD-source reference / the plan that was executed.

**Status:** STRUCT_TDATWR shipped in M3 Tier 2 separation but is functionally incomplete. The current `ClassTdAtwr` was copy-shaped from RA's `ClassAAGun` — that mismatch is the source of every visible bug. This doc replaces the donor-shaped port with a wholesale port of TD's `STRUCT_ATOWER`.

**Session that produced it:** 2026-05-22, max-effort deep dive paired with [[td-sam-deep-dive]].

**Guiding principle (this session's pushback from Luke):** the *whole point* of full STRUCT_TD-prefixed separation is that TD entities run TD's own building, weapon, and projectile code paths — not RA's nearest-shaped equivalent dressed up to look TD. No donor. No "modeled on PBOX." Port wholesale from `reference/vanilla-conquer/tiberiandawn/`. Per [[feedback-no-donor-for-td-separation]] / [[project-building-separation-committed]].

---

## What TD's ATOWER actually is

A 1×2 GDI defensive tower with a *fixed* missile rack on top. The rack does not rotate — the launched missiles (BULLET_SSM, the "DRAGON" sprite) do the tracking after launch. Powered building: stops firing under power outage. Crew=true: spawns an infantry one cell south on death.

Mechanically there is **no state machine and no special render path** — it's the simplest possible defensive building. The pile of "issues" comes entirely from `ClassTdAtwr` having the wrong flags (because it was shaped after RA's AGUN, a different beast).

### 1. TD source — `bdata.cpp:372-422`

```cpp
static BuildingTypeClass const ClassATower(STRUCT_ATOWER,
    TXT_AGUARD_TOWER,
    "ATWR",
    XYP_COORD(0, 0),
    4,                       // Build level
    STRUCTF_RADAR,           // Prerequisite
    true,                    // IsCloakable (detects adjacent cloaked)
    false,                   // IsRegulated
    false,                   // IsBibbed
    false,                   // IsNominal
    false,                   // IsWall
    false,                   // IsFactory
    false,                   // IsCaptureable
    false,                   // IsFireCharged
    true,                    // IsSimpleDamage      ← matters
    false,                   // IsInvisible
    true,                    // IsSelectable
    true,                    // IsLegalTarget
    false,                   // IsInsignificant
    false,                   // IsImmune
    false,                   // IsTheater
    false,                   // IsTurretEquipped    ← matters most
    true,                    // IsTwoShooter
    true,                    // IsRepairable
    true,                    // IsBuildable
    true,                    // IsCrew              ← matters
    false,                   // (concrete placement)
    RTTI_NONE,
    DIR_N,                   // Initial facing
    300,                     // Strength
    4,                       // Sight
    1000,                    // Cost
    13, 100, 30,             // Scenario / risk / reward
    HOUSEF_MULTI* | HOUSEF_JP | HOUSEF_GOOD,  // Ownable
    WEAPON_TOW_TWO,          // Primary
    WEAPON_NONE,             // Secondary
    ARMOR_ALUMINUM,
    0, 0, 0, 20,             // CanEnter / Capacity / Power / Drain
    BSIZE_12,                // 1×2
    NULL,
    (short const*)List12,
    (short const*)OList12);
```

### 2. TD's 4 dispatch sites in `building.cpp`

| Line | Function | What it does |
|---|---|---|
| 2784-2785 | `Fire_Data` | Muzzle data: `coord = Coord_Move(coord, DIR_N, 0x0030); dist = 0x0040;` |
| 2815-2816 | `Fire_Coord` | Muzzle coord: `coord = Coord_Move(coord, DIR_N, 0x0030); if (Target_Legal(TarCom)) coord = Coord_Move(coord, ::Direction(coord, As_Coord(TarCom)), 0x0040);` |
| 3522 | `Can_Fire` | `if (*this == STRUCT_ATOWER && House->Power_Fraction() < 1) return (FIRE_BUSY);` |
| 4132 | Crew-on-death spawn | If ATOWER or OBELISK, spawn the surviving infantry one cell SOUTH of foundation center. |

That's it. No `Mission_Attack` branch, no `Shape_Number` branch, no `AI` branch.

### 3. TD's `WEAPON_TOW_TWO` — `const.cpp:88`

```cpp
{BULLET_SSM, 60, 40, 0x0680, VOC_ROCKET2, ANIM_NONE},  // WEAPON_TOW_TWO
```

Per `type.h:50-91` field order — `{Fires, Attack, ROF, Range, Sound, Anim}`:
- Fires: `BULLET_SSM` (the "DRAGON" homing missile)
- Damage: 60
- ROF: 40
- Range: 0x0680 leptons = 1664 leptons = **6.5 cells**
- Sound: `VOC_ROCKET2`
- Anim: `ANIM_NONE` (TD's `Fire_At` adds `ANIM_MUZZLE_FLASH` as a default for non-bullet weapons)

### 4. TD's `BULLET_SSM` — `bbdata.cpp:153`

```cpp
static BulletTypeClass const ClassMissile(BULLET_SSM,
    "DRAGON",      // Image
    true,          // High (over walls)
    true,          // Homes
    false,         // Arcs
    false,         // Drops
    false,         // Invisible
    true,          // Proximity arm
    true,          // Animates flame
    true,          // Has fuel (can run out)
    false,         // No facing variation
    true,          // Inaccurate
    true,          // Translucent
    true,          // AA-capable
    7,             // Arming time
    0,             // Range override
    MPH_ROCKET,    // Speed
    5,             // ROT (turn rate)
    WARHEAD_HE,
    ANIM_FRAG1);   // Impact explosion
```

### 5. The firing render path (TD `building.cpp:Fire_At` general branch)

ATOWER is not in TD's SAM-specific branch. It takes the generic non-SAM path:

```cpp
Sound_Effect(weapon->Sound, Coord);                              // VOC_ROCKET2
AnimClass* anim = NULL;
if (weapon->Fires == BULLET_BULLET) {
    anim = new AnimClass(ANIM_GUN_N + Dir_Facing(PrimaryFacing.Current()), Fire_Coord(which));
} else {
    switch (weapon->Fires) {
    case BULLET_SPREADFIRE: case BULLET_LASER:
        break;
    default:
        anim = new AnimClass(ANIM_MUZZLE_FLASH, Fire_Coord(which));   // BULLET_SSM lands here
        break;
    }
}
```

Two visual effects per shot: the sound + the muzzle flash at `Fire_Coord`. The actual missile is the `BULLET_SSM` projectile that homes after launch.

---

## Why our current ClassTdAtwr is wrong

`redalert/bdata.cpp:737-764` — the four constructor args that diverge from TD:

| Field | Our value | TD value | Symptom |
|---|---|---|---|
| `VerticalOffset` | `0x0000` | `0x0030` | Missile spawns at building's base, not at the rack top |
| `PrimaryOffset` | `0x0000` | `0x0040` | Missile spawns at center, not extended out from rack |
| `IsSimpleDamage` | `false` | `true` | Damaged-frame indexing falls through to broken math |
| `IsTurretEquipped` | `true` | `false` | **The load-bearing bug** — every downstream issue |

The `IsTurretEquipped` cascade:

- **Shape_Number** (`building.cpp:669-693`) does `shapenum = BodyShape[Dir_To_32(PrimaryFacing.Current())]` then adds 32 (recoil) or 64 (damaged) offsets. That assumes a 32-frame rotation set. TDATWR has **3 frames** (healthy / damaged / extra) per `RA_STRUCTURES.XML:24300-24322` and `TDATWR.ZIP`. So the engine looks up frame indices that don't exist.
- **Can_Fire** (our `building.cpp:3358-3368`) gates on `PrimaryFacing` being within ±8° of target. With nothing visually rotating but the flag set true, the building rotates an invisible PrimaryFacing through 256 directions while looking frozen.
- **Turret_Facing** (`building.cpp:2790-2793`) returns `PrimaryFacing.Current()` instead of `Direction(TarCom)`. `Fire_Coord` then uses that for the muzzle direction.
- **Fire_Direction** (`building.cpp:5105-5114`) same logic — returns `PrimaryFacing.Current()` not `Direction(TarCom)`.

The historical comment at `bdata.cpp:4244-4256` (Logic-alias era) explicitly warned about exactly this: setting `IsTurretEquipped=true` on a TD building causes "firing logic to gate on `PrimaryFacing.Current() == direction-to-target` (which is never satisfied since nothing rotates `PrimaryFacing`)." That warning got lost in the full-separation migration.

---

## Symptoms → root cause map

Every observable issue traces to either the four-field flag mismatch (M1) or to RA not having TD's general-branch defaults (M3/M4).

| Symptom | Root cause | Step |
|---|---|---|
| Tower visual stuck on frame 0 (no rotation, no damage flip) | `IsTurretEquipped=true` + only 3 SHP frames; engine queries shapes 0-127 that don't exist | M1 |
| Delay before firing on target | `Can_Fire` gates on `PrimaryFacing` ±8° match | M1 |
| Missile spawns from middle of foundation | `VerticalOffset=0, PrimaryOffset=0` and Fire_Coord uses (wrong) PrimaryFacing direction | M1 |
| Damaged building stays on healthy frame | `IsSimpleDamage=false` → wrong damaged-shape math | M1 |
| No muzzle flash | RA's `Fire_At` doesn't fall back to `ANIM_MUZZLE_FLASH` like TD's does; `[TDTowTwo]` has no `Anim=` field | M4 |
| Fires while owning house is power-starved | No `STRUCT_TDATWR` `FIRE_BUSY` check in `Can_Fire` | M3 |
| Crew infantry on death spawns inside foundation (or fails to spawn) | No `STRUCT_TDATWR` south-offset branch in death-spawn site | M5 |

---

## Port plan — direct TD port, no RA donor

### M1 — Match `ClassTdAtwr` to TD's `ClassATower` field-for-field

`redalert/bdata.cpp:737-764`. Four constructor args change:

```cpp
static BuildingTypeClass const ClassTdAtwr(STRUCT_TDATWR,
    TXT_NONE,
    "TDATWR",
    FACING_S,
    XYP_COORD(0, 0),
    REMAP_ALTERNATE,
    0x0030,          // VerticalOffset       (was 0x0000) — TD ClassATower
    0x0040,          // PrimaryOffset        (was 0x0000) — TD ClassATower
    0x0000,          // PrimaryLateral
    false,           // IsFake
    false,           // IsRegulated
    false,           // IsNominal
    false,           // IsWall
    true,            // IsSimpleDamage       (was false)  — TD ClassATower
    false,           // IsInvisible
    true,            // IsSelectable
    true,            // IsLegalTarget
    false,           // IsInsignificant
    false,           // IsTheater
    false,           // IsTurretEquipped     (was true)   — TD ClassATower — load-bearing
    true,            // IsRemap
    RTTI_NONE,
    DIR_N,           // Initial facing       (was DIR_NE) — TD ClassATower
    BSIZE_12,
    NULL,
    (short const*)List12,
    (short const*)OList12);
```

Update the comment block at `bdata.cpp:694-704` to drop the "Modeled on ClassAAGun (AGUN)" line and point at this doc. The whole TDATWR block stops referencing any RA building.

### M2 — Delete the stale Logic-alias-era comment

`bdata.cpp:4244-4256` is a warning about the Logic-alias workaround. With full separation done correctly (M1's `IsTurretEquipped=false` matches TD), the warning's premise is gone. Replace the 13 lines with a one-line pointer:

```cpp
// IsTurretEquipped and related flags are set directly per TD source on
// each ClassTd<Name>. See docs/td-atwr-deep-dive.md / td-sam-deep-dive.md.
```

### M3 — Port TD's `STRUCT_ATOWER` power-fraction gate

`redalert/building.cpp` `Can_Fire`. Find where other building-specific Can_Fire branches live (the same place RA gates AAGUN's `if (Class->IsPowered && House->Power_Fraction() < 1)`). Add a dedicated `STRUCT_TDATWR` branch with TD's exact logic from `building.cpp:3520-3524`:

```cpp
// Direct port from tiberiandawn/building.cpp:3522.
// "Advanced guard towers need power to fire." Not aliased to STRUCT_ATOWER
// (RA's vanilla heap has no ATOWER) and not aliased to RA's AAGUN (RA's
// AAGUN gates on Class->IsPowered which is rules-ini-driven; TD's is
// hard-coded for the building).
if (*this == STRUCT_TDATWR && House->Power_Fraction() < 1) {
    return (FIRE_BUSY);
}
```

### M4 — Verify `[TDTowTwo]` matches TD's `WEAPON_TOW_TWO` field-for-field

Current `[TDTowTwo]`:
```ini
[TDTowTwo]
Damage=60       ; TD Attack
ROF=40          ; TD ROF
Range=6.5       ; TD Range 0x0680 leptons = 6.5 cells
Projectile=TDSSM
Speed=30
Warhead=HE      ; TD's BULLET_SSM has WARHEAD_HE
Report=ROCKET2  ; TD VOC_ROCKET2
```

Missing: `Anim=GUNFIRE` (binds `ANIM_MUZZLE_FLASH` in RA per `adata.cpp:1075`). TD's source-level `ANIM_NONE` in the weapon table is a *fallback*; the general `Fire_At` branch in TD spawns `ANIM_MUZZLE_FLASH` automatically for `BULLET_SSM`. RA's `Fire_At` (techno.cpp:3386-3411) doesn't have that fallback. Add the `Anim=` explicitly:

```ini
Anim=GUNFIRE   ; ANIM_MUZZLE_FLASH — TD's Fire_At general-branch default for BULLET_SSM
```

### M5 — Verify `[TDSSM]` matches TD's `BULLET_SSM` field-for-field

Current `[TDSSM]`:
```ini
[TDSSM]
Arm=7
High=yes
Shadow=no
Proximity=yes
Animates=yes
Ranged=yes
AA=yes
AG=yes
Image=DRAGON
ROT=5
Rotates=yes
Inaccurate=yes
```

Cross-check against TD's `ClassMissile` (`bbdata.cpp:153`):

| TD field | TD value | Our [TDSSM] | Status |
|---|---|---|---|
| Image (NAME) | "DRAGON" | `Image=DRAGON` | match |
| High (over walls) | true | `High=yes` | match |
| Homes | **true** | (no field) | **need to verify RA equivalent — likely `Homing=yes`?** |
| Arcs | false | (not set, default no) | OK |
| Drops | false | (n/a) | OK |
| Invisible | false | (n/a) | OK |
| Proximity arm | true | `Proximity=yes` | match |
| Animates flame | true | `Animates=yes` | match |
| Has fuel | true | `Ranged=yes`? | **possibly match — verify** |
| No facing variation | false | (not set) | OK |
| Inaccurate | true | `Inaccurate=yes` | match |
| Translucent | true | (no field) | **may need `Translucent=yes` if RA supports** |
| AA-capable | true | `AA=yes` | match (but TD also fires this against ground via TOW_TWO's HE warhead — we also have `AG=yes` which is correct intent) |
| Arming time | 7 | `Arm=7` | match |
| Speed | MPH_ROCKET | `Speed=` (not set, falls back to default — need explicit) | **needs explicit Speed** |
| ROT | 5 | `ROT=5` | match |
| Warhead | WARHEAD_HE | (controlled by weapon, not projectile) | OK |
| Impact anim | ANIM_FRAG1 | (default per RA explosion table) | check |

Action: add `Homing=yes` (or RA's equivalent — verify against an existing RA homing-missile projectile like `[Heat-Seeker]`), explicit `Speed=`, and check if RA supports `Translucent=yes`.

### M6 — Port TD's `STRUCT_ATOWER` crew-spawn-spot adjustment

`redalert/building.cpp` `Drop_Debris` or wherever RA spawns surviving infantry. Find TD's logic at `building.cpp:4112-4148`. The relevant snippet (we already saw lines 4128-4134):

```cpp
COORDINATE coord = Coord_Add(Center_Coord(), XYP_COORD(0, -12));
if (*this == STRUCT_ATOWER || *this == STRUCT_OBELISK) {
    coord = Map[Coord_Cell(coord)].Adjacent_Cell(FACING_S)->Cell_Coord();
}
```

Port to RA as a dedicated `STRUCT_TDATWR` branch (and `STRUCT_TDOBLI` since we already separated it):

```cpp
COORDINATE coord = Coord_Add(Center_Coord(), XYP_COORD(0, -12));
if (*this == STRUCT_TDATWR || *this == STRUCT_TDOBLI) {
    coord = Map[Coord_Cell(coord)].Adjacent_Cell(FACING_S)->Cell_Coord();
}
```

(The TD source aliases `STRUCT_ATOWER || STRUCT_OBELISK` because both buildings share the south-offset rule. Our port aliases `STRUCT_TDATWR || STRUCT_TDOBLI` for the same reason. This is a *positive-dispatch* alias that's identical behavior for two TD buildings — acceptable per the M6 rule in [[td-sam-deep-dive]]: identical behavior across two TD entities can share a comment-tagged branch.)

If RA's `Drop_Debris` already has the south-offset adjustment for some vanilla buildings, slot ours into that same place. If not, add the check before the `Unlimbo` call for the crew infantry.

### M7 — Manifest sync (`scripts/buildings_manifest.py`)

The `TDATWR` dict already has `"primary": None` (rules.ini emits the binding); update the `notes` field:

```python
"notes": "TD GDI Advanced Guard Tower (1x2 fixed missile rack — NOT a "
         "rotating turret). Wholesale port of tiberiandawn/ STRUCT_ATOWER "
         "per docs/td-atwr-deep-dive.md. Weapon=TDTowTwo (TD WEAPON_TOW_TWO), "
         "projectile=TDSSM (TD BULLET_SSM/'DRAGON').",
```

No structural manifest changes.

---

## What's already right (don't touch)

- `STRUCT_TDATWR` enum in `defines.h` and heap registration in `bdata.cpp:3323`.
- `TDATWR.ZIP` 3-frame asset and `RA_STRUCTURES.XML` mapping — matches `IsSimpleDamage=true` layout (frame 0 healthy, frame 1 damaged, extra frame for safety).
- `TDATWRMAKE.ZIP` 14-frame construction animation and rules.ini `BuildupAnim*` settings.
- `[TDATWR]` rules.ini fields: `Strength=300`, `Cost=1000`, `Power=-20`, `Sight=4`, `Armor=aluminum`, `Crewed=true`, `Prerequisite=TDHQ`, `TechLevel=4`. All match TD's `ClassATower`.
- `[TDTowTwo]` Damage/ROF/Range/Warhead/Report — TD-authentic.
- Audio routing: `VOC_TD_ROCKET2` in `audio.cpp:253` + `RAC_SFX_ROCKET2`/`RAR_SFX_ROCKET2` in `SFXEVENTSNONLOCALIZED.XML:6047-6061`. Already there from prior TD ports.

---

## Test plan

Single-Deck smoke test covers everything except the AA aspect:

1. Build TDATWR. Visual should be fixed missile rack, no rotation.
2. Send ground enemies into range:
   - Tower fires within one game tick (no facing-rotation delay)
   - Missile spawns from rack tip (visible offset up-and-out from foundation)
   - `ROCKET2` audio + `GUNFIRE` muzzle flash visible
   - Missile homes and hits target
3. Damage tower below 50% strength. Visual flips to frame 1 (damaged). Still functional.
4. Sell a power plant on the owning house. Tower stops firing immediately even with enemies in range. Build/repair power; tower resumes firing.
5. Kill the tower. Crew infantry spawns one cell south of the foundation (not inside it).

MP smoke (deferred — pair with SAM testing on 2-Deck setup): Longbow approach over a TDATWR. AA aspect: TDATWR fires `[TDSSM]` on aircraft (`AA=yes` in projectile). Verify the missile tracks and detonates near the aircraft.

---

## Acceptance criteria

- [ ] `ClassTdAtwr` matches TD's `ClassATower` on `IsTurretEquipped`, `IsSimpleDamage`, `VerticalOffset`, `PrimaryOffset`, initial facing.
- [ ] TDATWR renders frame 0 healthy, frame 1 damaged. No frozen-rotation symptom.
- [ ] TDATWR fires within one tick of acquiring a target.
- [ ] Missile spawns from the rack tip with TD-authentic offsets.
- [ ] `ROCKET2` audio + `GUNFIRE` muzzle flash on each shot.
- [ ] Power-out → `FIRE_BUSY`. Power restored → fires.
- [ ] Death → infantry spawns one cell south.
- [ ] `[TDSSM]` projectile config matches TD's `ClassMissile` BULLET_SSM where RA supports the fields.
- [ ] RA's vanilla AAGUN, GUN, PBOX continue to work unchanged.

---

## Decisions

- **No donor.** `ClassTdAtwr` constructor args are set from TD source values, not copied from RA's AGUN/PBOX/anything. Per [[feedback-no-donor-for-td-separation]] / [[project-building-separation-committed]].
- **`[TDTowTwo]` stays the TD weapon port.** Not aliased to RA's vanilla `[TowTwo]` (which doesn't exist; RA's TOW equivalents are different).
- **`[TDSSM]` stays the TD projectile port.** Not aliased to RA's `[AAMissile]` (TD's BULLET_SAM uses MPH_VERY_FAST + ROT=10, BULLET_SSM uses MPH_ROCKET + ROT=5 — different missiles).
- **Crew-spawn south-offset aliased between TDATWR and TDOBLI.** Both TD buildings need the same south-offset rule. The alias here is two TD entities sharing identical behavior, not TD borrowing from RA — that's the legitimate aliasing pattern per [[project-building-separation-committed]].

---

## Cargo order

M1 alone fixes the user-visible visual + firing issues. Suggested commit shape:
- **PR 1**: M1 (flag fix) + M2 (stale comment cleanup). Smallest possible change, highest payoff. Build, deploy, smoke-test.
- **PR 2**: M3 (power gate) + M4 (`Anim=GUNFIRE`) + M5 ([TDSSM] field cross-check) + M6 (crew south-offset) + M7 (manifest notes). TD-authenticity polish.

Both PRs are TDATWR-only; don't pull TDSAM into this commit cargo.

---

## Session 2026-05-22 — TDATWR full TD port (Option A architecture)

The 2026-05-22 session expanded scope from the M1-M7 polish into a **complete TD-port of TDATWR's runtime behavior** per the Option A architecture committed in [[project-td-port-architecture]] (shared class shells, separated `_TD()` code paths gated by `IsTDPort` flag).

### What got built

**`BulletTypeClass` extended** (`redalert/type.h`, `bbdata.cpp`):
- Added fields: `IsTDPort`, `IsHoming`, `ClassWarhead`, `ImpactAnim`, `BulletRange`
- TD's `BulletClass::AI`/`Unlimbo` reference these by name; without them the verbatim port doesn't compile
- Parsed from rules.ini: `Homing=`, `Warhead=`, `ImpactAnim=`, `BulletRange=` for bullet sections
- `IsTDPort` set in `bbdata.cpp` via `BulletTypes.Ptr((int)BULLET_SSM)->IsTDPort = true` after registration (not parseable from rules.ini — it's an engine-level dispatch gate)

**`BulletClass::Unlimbo_TD()`** (`redalert/bullet.cpp`):
- Verbatim port of `reference/vanilla-conquer/tiberiandawn/bullet.cpp:631` (TD's `BulletClass::Unlimbo`)
- Dispatched from `BulletClass::Unlimbo()`: `if (Class->IsTDPort) return Unlimbo_TD(coord, dir);`
- Key TD-vs-RA differences captured: TD's wider scatter (`Distance/3` cap'd at 0x0200) for homing bullets, firer-range clamp (clamps scattered tcoord back into firer's weapon range — fixes close-range targeting), TD's `Class->Range`/`Class->Arming` direct fields
- Engine-plumbing additions (`Map.Remove`/`Map.Submit`, `Height` init, `IsFalling`) are RA-side requirements flagged inline

**`BulletClass::AI_TD()`** (`redalert/bullet.cpp`):
- Verbatim port of `reference/vanilla-conquer/tiberiandawn/bullet.cpp:293` (TD's `BulletClass::AI`)
- Key TD-vs-RA differences captured: TD's explicit `IsHoming` check (not derived from `ROT != 0`), `ANIM_SMOKE_PUFF` trail spawn (no `FB1` special-case), AA proximity strength bonus (BULLET_TOW → BULLET_SSM in our enum), TD's `Class->Explosion` direct spawn (no warhead-driven Combat_Anim classifier)
- Symbol renames: `Class->Warhead` → `Class->ClassWarhead`, `Class->Explosion` → `Class->ImpactAnim`, `Altitude` → `Height`, `GRAVITY` → `Rule.Gravity`, `Delete_This()` → `delete this`

**`WeaponTypeClass` extended** (`redalert/weapon.h`, `weapon.cpp`):
- Added `IsTDPort` field
- `Read_INI` branches on `IsTDPort`: TD weapons parse `Speed=` as raw `MPHType` (TD source convention, 0-255) via `Get_Int`; RA weapons keep `Get_MPHType` (0-100 percentage scaled to 0-256)
- `TDTowTwo` flagged `IsTDPort = true` in `rules.cpp` after registration

### The Speed unit-conversion gotcha (root cause of "missiles fly too fast / can't hit walls")

**Symptom:** TDATWR fired missiles that overshot every target — could not hit walls 1 cell away, even with 4-cell separation.

**Root cause:** RA's `Get_MPHType` interprets `Speed=N` as a 0-100 *percentage* and scales via `_Scale_To_256` (val * 256 / 100). TD's source stores `MaxSpeed = MPH_ROCKET` etc. as raw `MPHType` (0-255). We copied TD's source values directly: `[TDTowTwo] Speed=60` → RA parsed as `60% of 255 = raw 153`. Missile moved 2.5× too fast, overshot during the 7-frame arming window, never triggered proximity fuse, detonated harmlessly past target on timer timeout.

**Diagnosed via** `tf_tdport_bullet.log` (per-frame TDSSM flight trace) showing `MaxSpeed=153` at SPAWN and bullets reaching `dist=82` from target at frame 6 while still arming. Fix: `IsTDPort` flag on WeaponTypeClass + raw-int Speed parse → `Speed=60` stays as raw 60 → missile flies at TD-authentic speed → proximity fuse triggers near target (24-89 lepton scatter, all hits).

This conversion catch is captured in [[reference-ra-mphtype-ini-format]].

### TDDRAGON asset port

**Issue:** `[TDSSM] Image=DRAGON` was resolving to RA's vanilla `DRAGON.ZIP` (a different visual than TD's actual `DRAGON.SHP`).

**Fix (asset side):** Extracted vanilla TD's `DRAGON.ZIP` from `~/.steam/.../Data/TEXTURES_TD_SRGB.MEG` via `scripts/meg_extract.py`, repacked with TD-prefixed internal TGAs via `scripts/bundle_assets.py:repack_zip_with_prefix(dragon → tddragon)`. Outputs:
- `resources/.../Data/ART/TEXTURES/SRGB/RED_ALERT/VFX/TDDRAGON.ZIP` (32 frames, TD-prefixed internally)
- 32 TDDRAGON shape entries patched into `resources/.../Data/XML/TILESETS/RA_VFX.XML` (CONFIG.MEG-override format, same pattern as `RA_STRUCTURES.XML`)
- `[TDSSM] Image=TDDRAGON`

This is the vanilla-MEG pipeline pattern used for buildings, applied to bullets. **Did NOT use the TD-Assets workshop content** — our mod is self-contained.

**The hidden trap (engine side):** The asset port above is necessary but NOT sufficient. Bullets / anims / aircraft in RA's gameplay DLL use the legacy `MFCD::Retrieve("<GraphicName>.SHP")` path in `<Type>Class::One_Time` to populate `ImageData`. For a TGA-only TD entity (no `.SHP` in any MIX file), `MFCD::Retrieve` returns `NULL`, and `Draw_It` bails at `if (!shapeptr) return;` — even though the tileset XML is correctly registered. **Symptom**: smoke trail visible (anim spawn happens before render), audio works, damage works, but the missile body is invisible.

**Fix (engine side):** copy a vanilla donor's `ImageData` pointer to the TD entity's `ImageData` slot. The pointer is just a non-NULL placeholder so `Draw_It` proceeds; the launcher's `CC_Draw_Shape` overlay then resolves the actual sprite by name via the tileset XML. Same pattern already in place for `AIRCRAFT_TDCARGO` (TDC17) at `aadata.cpp:442-459`; mirrored for bullets in `bbdata.cpp::BulletTypeClass::One_Time` post-loop:

```cpp
BulletTypeClass const& donor = As_Reference(BULLET_HEAT_SEEKER);
BulletTypeClass& tdssm = As_Reference(BULLET_SSM);
if (tdssm.ImageData == NULL) {
    ((void const*&)tdssm.ImageData) = donor.ImageData;
}
// + TDLaser, TDAPDS
```

Captured in [[reference-mfcd-donor-imagedata-pattern]] — applies to every new TD-prefixed bullet/anim/aircraft.

### Two-shooter salvo verification

Diagnostic logs confirmed `Burst=2` on `[TDTowTwo]` produces 2 missiles per engagement via RA's `Is_Two_Shooter()` derivation (`PrimaryWeapon->Burst > 1`) + `IsSecondShot` toggle. Salvo timing is ~3-frame gap intra-salvo vs TD's 9 (RA's `Rearm_Delay` returns 3 for short delay; TD's returns 9). Functionally correct, slightly tighter cadence than TD.

### What's still gap

- **`Rearm_Delay` TD-port** — for fully TD-authentic salvo cadence (9 frames between salvo shots, ROF+3 between salvos). Belongs in cargo E full implementation.
- **`TechnoClass::Fire_At` TD-port** — for any TD-vs-RA divergence in the fire-bullet creation path. Cargo E full.
- **`BuildingClass::Mission_Attack` sweep** — verify TD parity in mission state machine. Cargo F.

### What's right now (TDATWR runtime)

- TD-source raw values in rules.ini for the TD-port weapon (`Speed=60` reads literally as TD MPH_ROCKET=60)
- Verbatim TD `BulletClass::AI`/`Unlimbo` for TDSSM (cargo D)
- TDHE warhead, TD-correct ImpactAnim, IsHoming, etc. all set per TD source
- TDDRAGON sprite from vanilla TD MEG (no RA fallback)
- 2-missile salvo via Burst=2 (functionally correct)
- Close-range targeting works (walls take damage at 1-cell range)
- Missile damage application at 24-89 lepton scatter (TD-Inaccurate-true scatter, well-within explosion radius)

### Diagnostic logging (to remove)

Per-frame TDSSM/TDLaser/TDAPDS flight trace is currently active in `BulletClass::Unlimbo_TD` and `AI_TD`, writing to `tf_tdport_bullet.log`. Per [[feedback-keep-diagnostics-until-v1]], stub under `#if 0` after final verification rather than deleting — one-line re-enable for future debug.

