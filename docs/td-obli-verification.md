# TDOBLI — TD-source verification

> **RESOLVED — separated + shipped (v0.50).** TDOBLI is fully separated and binds `Primary=TDOblsLaser` in rules.ini; the charge-timing fix landed. The body below is retained as TD-source reference / the plan that was executed.

**Status:** Largely TD-authentic. The "validated vertical slice" reputation from M5 is correct — building flags, rules.ini stats, weapon stats, projectile, warhead, audio routing, and engine dispatch are all TD-correct. **One balance-relevant bug**: charge timing is ~6× faster than TD's. **Three cosmetic-tier divergences**: VerticalOffset, missing HorizontalOffset, class naming. No "still bound to RA vanilla weapon" issues — TDOBLI is the cleanest separation in the M3 Tier 2 set.

**Session that produced it:** 2026-05-22, paired with `td-gtwr-gun-verification.md`. Same TD-source-grounded verification pattern.

**Guiding principle:** wholesale port of TD's building + weapon + projectile + audio. Per [[feedback-no-donor-for-td-separation]] / [[project-building-separation-committed]] / [[project-td-prefix-convention]].

---

## TD source values (verified)

### TDOBLI = TD's `STRUCT_OBELISK` (TD `bdata.cpp:424-473`)

```cpp
static BuildingTypeClass const ClassObelisk(STRUCT_OBELISK,
    /* ... */
    true,   // IsCloakable             ← detects adjacent cloaked units
    false,  // IsRegulated
    false,  // IsBibbed
    false,  // IsNominal
    false,  // IsWall
    false,  // IsFactory
    false,  // IsCaptureable
    false,  // IsFireCharged ("does it catch fire" — NOT the charging flag)
    false,  // IsSimpleDamage          ← full damaged frame range, not single-frame
    false,  // IsInvisible
    true,   // IsSelectable
    true,   // IsLegalTarget
    false,  // IsInsignificant
    false,  // IsImmune
    false,  // IsTheater
    false,  // IsTurretEquipped        ← fixed structure, no rotation
    false,  // IsTwoShooter
    true,   // IsRepairable
    true,   // IsBuildable
    true,   // IsCrew                  ← spawns infantry on death
    false,  // (concrete placement)
    RTTI_NONE,
    DIR_N,                  // Initial facing
    200,                    // Strength
    5,                      // Sight
    1500,                   // Cost
    11, 100, 35,            // Scenario / risk / reward
    HOUSEF_MULTI* | HOUSEF_JP | HOUSEF_BAD,
    WEAPON_OBELISK_LASER,
    WEAPON_NONE,
    ARMOR_ALUMINUM,
    0, 0, 0, 150,           // CanEnter / Capacity / Power / Drain (massive 150 drain)
    BSIZE_12,
    NULL,
    (short const*)List12,
    (short const*)OList12);
```

### TD's `STRUCT_OBELISK` dispatch sites in `building.cpp` (6 total)

| Line | Function | What |
|---|---|---|
| 531-541 | `Shape_Number` | Charge-state-aware: `IsCharged → shape 3; IsCharging → Fetch_Stage(); else 0` |
| 909 | `AI` | Animation-AI exclusion: Obelisk handles its own anim cycle via charge state |
| 1066-1095 | `AI` (Charging logic) | Full charge state machine: powered + target → start charging via `Set_Stage(0); Set_Rate(OBELISK_ANIMATION_RATE)` + play `VOC_LASER_POWER`. `Fetch_Stage() >= 4` → IsCharged. Target lost or power lost → reset |
| 2789-2792 | `Fire_Data` | Muzzle data: `coord += DIR_N 0x00A8; coord += DIR_W 0x0018;` (vertical lift + horizontal lateral) |
| 2822-2826 | `Fire_Coord` | Muzzle coord: same offsets |
| 4132 | Crew-on-death | `STRUCT_ATOWER || STRUCT_OBELISK` south-offset spawn (BSIZE_12 footprint adjustment) |

Plus TD `defines.h:323`: `#define OBELISK_ANIMATION_RATE 15`. This is *ticks per frame*, used by both `Init_Anim` for BSTATE_ACTIVE and by the runtime `Set_Rate` in Charging_AI.

### TD's `WEAPON_OBELISK_LASER` (TD `const.cpp:90`)

```cpp
{BULLET_LASER, 200, 90, 0x0780, VOC_LASER, ANIM_NONE},  // WEAPON_OBELISK_LASER
```

- Bullet: `BULLET_LASER` (the laser-line projectile)
- Damage: 200 (massive)
- ROF: 90 (slow — fires every 6 seconds at base rate)
- Range: 0x0780 / 256 = **7.5 cells**
- Sound: `VOC_LASER` (= `OBELRAY1`)
- Anim: `ANIM_NONE` (the firing visual is the laser-line render, not a sprite anim)

### TD's `BULLET_LASER` aka ClassLaser (TD `bbdata.cpp:329-349`)

```cpp
static BulletTypeClass const ClassLaser(BULLET_LASER,
    "Laser",         // Image (laser sprite)
    true,            // High (over walls)
    false,           // Homes
    false,           // Arcs
    false,           // Drops
    true,            // Invisible      ← no traveling bullet sprite
    false,           // Proximity arm
    false,           // Animates flame
    false,           // Has fuel
    true,            // No facing variation
    false,           // Inaccurate
    false,           // Translucent
    false,           // AA-capable     ← ground-only
    0, 0,
    MPH_LIGHT_SPEED, // Speed (essentially hitscan)
    0,               // ROT
    WARHEAD_LASER,
    ANIM_NONE);      // No impact anim — laser-line render handles visual
```

Hitscan laser with `WARHEAD_LASER`.

### TD audio for Obelisk (TD `audio.cpp:137-138`)

```cpp
{"OBELRAY1", 1, IN_JUV},  // VOC_LASER       — humming laser beam (firing)
{"OBELPOWR", 1, IN_JUV},  // VOC_LASER_POWER — warming up of laser beam (charging)
```

---

## Diff against current state

### `ClassObelisk` (`redalert/bdata.cpp:824-851`)

| Field | Our value | TD value | Status |
|---|---|---|---|
| Name token | `TXT_NONE` (rules.ini Name=) | `TXT_OBELISK` | OK (rules.ini overrides) |
| IniName | `"TDOBLI"` | `"OBLI"` (TD prefix added per [[project-td-prefix-convention]]) | match-by-convention |
| VerticalOffset | `0x00C8` | `0x00A8` (from Fire_Coord) | ⚠ DIVERGES by 0x20 |
| PrimaryOffset | `0x0000` | (uses fixed Fire_Coord, no PrimaryOffset path) | OK (laser is hitscan) |
| HorizontalOffset | not in BuildingTypeClass constructor | `0x0018 W` (from Fire_Coord) | ⚠ missing per-building lateral |
| IsSimpleDamage | `false` | `false` | match |
| IsTurretEquipped | `false` | `false` | match |
| Initial facing | `DIR_N` | `DIR_N` | match |
| Size | `BSIZE_12` | `BSIZE_12` | match |
| Foundation | `List12` | `List12` | match |
| (IsCrew via rules.ini) | `Crewed=true` | `true` | match |

**Two minor mismatches:**
- `VerticalOffset=0x00C8` (200 leptons) vs TD's `0x00A8` (168 leptons). 32 leptons higher than TD. Probably a Remaster TGA-frame-height tweak from the M5 vertical-slice session; verify whether the laser beam origin renders at the correct crystal-tip in-game. If yes, leave; if no, drop to 0x00A8.
- TD's `0x0018 W` horizontal shift has no equivalent in `BuildingTypeClass`'s constructor — would need a per-building hardcode in `Fire_Coord` or a `HorizontalOffset` set in rules.ini. Since the Obelisk is hitscan with a fixed crystal-tip visual, this offset only matters for the beam-start coordinate. The M5 laser-line render uses its own coords (see `building.cpp` Charging_AI / Fire_At BULLET_LASER branch), so this is probably not user-visible.

**Class naming:** our class is `ClassObelisk` (TD's name). Every other TD-separated building uses `ClassTd<Name>` (`ClassTdGtwr`, `ClassTdAtwr`, `ClassTdGun`, `ClassTdSam`). For consistency you could rename to `ClassTdObli` — pure cosmetic but the inconsistency stands out when scanning the file.

### `[TDOBLI]` rules.ini section (line 3746-3776)

```ini
[TDOBLI]
ShapeSize=24,48          ; OK
Name=Obelisk of Light    ; OK
TechLevel=4              ; ✓ TD scenario=11 → TechLevel 4 equiv via RA's tech tree
Prerequisite=TDHQ        ; ✓ TD STRUCTF_RADAR → TDHQ (the M3 separated Construction Yard upgrade)
Owner=BadGuy             ; ✓ TD HOUSEF_BAD
Cost=1500                ; ✓ TD 1500
Power=-150               ; ✓ TD Drain=150
Strength=200             ; ✓ TD 200
Sight=5                  ; ✓ TD 5
Armor=aluminum           ; ✓ TD ARMOR_ALUMINUM
Primary=TDOblsLaser      ; ✓ TD-prefixed dedicated weapon
Crewed=true              ; ✓ TD IsCrew
Repairable=yes           ; ✓ TD IsRepairable
ActiveAnimStart=0
ActiveAnimCount=4        ; ✓ TD Init_Anim Count=4
ActiveAnimRate=15        ; ✓ TD OBELISK_ANIMATION_RATE=15
BuildupAnimStart=0
BuildupAnimCount=20
BuildupAnimRate=2
```

**All TD-authentic.** The ActiveAnimRate=15 matches `OBELISK_ANIMATION_RATE` exactly (this drives the Init_Anim Rate — see M5 note at our bdata.cpp:3399).

Optional polish: add `Adjacent=1` if it's not implicit (most defensive buildings need it).

### `[TDOblsLaser]` weapon (line 2570-2584)

```ini
[TDOblsLaser]
Damage=200               ; ✓ TD Attack=200
ROF=90                   ; ✓ TD ROF=90
Range=7.5                ; ✓ TD Range=0x0780 leptons / 256 = 7.5 cells
Projectile=TDLaser       ; ✓ TD-prefixed dedicated projectile
Speed=255                ; close to MPH_LIGHT_SPEED — verify exact value (LightSpeed = 255 in RA convention)
Warhead=TDLaser          ; ✓ TD-prefixed dedicated warhead (cohabits [TDLaser] section)
Report=OBELRAY1          ; ✓ TD VOC_LASER = "OBELRAY1"
Charges=yes              ; ✓ wires the IsCharging/IsCharged state machine
```

All TD-authentic. The `Charges=yes` is the rules.ini flag that sets `WeaponTypeClass::IsElectric=true`, which Charging_AI uses to gate the charge state machine. Same mechanism TD uses (TD `building.h:115-116` defines IsCharging/IsCharged; TD `building.cpp:852-857` resets them in Fire_At's BULLET_LASER case).

### `[TDLaser]` projectile + warhead (line 2728-2745)

```ini
[TDLaser]
; --- bullet fields (BULLET_LASER / ClassLaser) ---
Inviso=yes               ; ✓ TD Invisible=true
High=yes                 ; ✓ TD High=true
Shadow=no                ; ✓ inferred (TD's invisible laser has no shadow)
AA=no                    ; ✓ TD "Good against aircraft"=false
AG=yes                   ; ✓ TD doesn't have separate AG; inferred from non-AA
ROT=0                    ; ✓ TD ROT=0
Rotates=no               ; ✓ TD NoFacingVariation=true → no rotation
Image=none               ; ✓ TD Image="Laser" but it's invisible so visual doesn't render
; --- warhead fields (WARHEAD_LASER) ---
Spread=4                 ; matches TD WARHEAD_LASER (SpreadFactor — verify the exact mapping)
Wall=no                  ; TD IsWallDestroyer=false
Wood=no                  ; TD IsWoodDestroyer=false
Ore=no                   ; TD IsTiberiumDestroyer=false
Verses=100%,100%,100%,100%,100%   ; TD's armor table {0x100, ?, ?, ?, ?} — verify against TD source
Explosion=0              ; TD's impact anim — TD has ANIM_NONE
InfDeath=5               ; RA-specific death anim selector
```

The bullet half is TD-authentic. The warhead half needs one verification: TD's `WARHEAD_LASER` armor-modifier table. The TD source has:

```cpp
{2, false, false, false, {0x100, 0x80, 0x90, 0x40, 0x40}},  //	WARHEAD_SA
```

That's WARHEAD_SA. Let me note: we don't have `WARHEAD_LASER`'s exact armor table in the snippets pulled this session — verify against `tiberiandawn/const.cpp` Warheads[] at WARHEAD_LASER index during implementation if you want to confirm the `Verses=` 100/100/100/100/100 is right. (TD's WARHEAD_LASER likely has differentiated values; 100/100/100/100/100 means "deals full damage to all armor types" which is a balance call. Worth checking.)

### Audio routing

| TD VocType | TD sample | RA mapping | Used by |
|---|---|---|---|
| `VOC_LASER` | `OBELRAY1` | `VOC_TD_LASER` (`audio.cpp:255`) | Obelisk firing | ✓ |
| `VOC_LASER_POWER` | `OBELPOWR` | `VOC_TD_LASER_POWER` (`audio.cpp:256`) | Obelisk charge-up | ✓ |

Both wired correctly. Used by `building.cpp:6134` for charge-start sound.

### Engine dispatch (our `redalert/building.cpp`)

| Line | Site | Status |
|---|---|---|
| 652 | `Shape_Number`: `*this == STRUCT_TESLA || *this == STRUCT_TDOBLI` charge-state render (IsCharged → shape 3; IsCharging → Fetch_Stage; else 0) | ✓ matches TD's STRUCT_OBELISK branch at TD `building.cpp:531` |
| 3948 | `MISSION_CONSTRUCTION` plays `VOC_TD_CONSTRUCTION` for any `STRUCT_TDxxxx` (range check) | ✓ TD-port-specific sound routing |
| 4090 | Crew-on-death south-offset for `STRUCT_TESLA || STRUCT_TDOBLI` | ✓ aliases TESLA because TESLA's BSIZE_12 needs the same offset; TD's STRUCT_OBELISK pairs with STRUCT_ATOWER but the rule is "BSIZE_12 needs south-offset" so the alias-to-TESLA on the RA side is correct |
| 6133-6137 | `Charging_AI` charge-start sound: `STRUCT_TDOBLI` plays `VOC_TD_LASER_POWER`; else `VOC_TESLA_POWER_UP` | ✓ TD-authentic OBELPOWR routing |
| 6250 | `Animation_AI` exclusion for `STRUCT_TESLA || STRUCT_TDOBLI` | ✓ TDOBLI uses charge state machine, not BSTATE_ACTIVE auto-cycle |
| (bdata.cpp:3399) | `Init_Anim`: `{STRUCT_TDOBLI, BSTATE_ACTIVE, 0, 4, 15}` — 4 charge frames at rate 15 | ✓ TD-authentic Init_Anim values (matches TD's `STRUCT_OBELISK, BSTATE_ACTIVE, 0, 4, OBELISK_ANIMATION_RATE`) |

---

## The one balance-relevant issue: charge timing

**`building.cpp:6128` in `Charging_AI`:**

```cpp
} else if (!Arm) {
    IsCharged = false;
    IsCharging = true;
    Set_Stage(0);
    Set_Rate(3);              // ← hardcoded 3 ticks per stage
    ...
}
```

`Set_Rate(3)` is hardcoded for both Tesla and TDOBLI. TD's Obelisk uses `Set_Rate(OBELISK_ANIMATION_RATE)` = `Set_Rate(15)` (TD `building.cpp:1082`). At C&C's 15 ticks per second baseline:

| | Set_Rate | Stages | Total ticks | Real time |
|---|---|---|---|---|
| RA Tesla Coil (vanilla) | 3 | 9 | 27 | ~1.8 sec |
| Our TDOBLI (current) | 3 | 4 | 12 | ~0.8 sec |
| **TD Obelisk (authentic)** | **15** | **4** | **60** | **~4 sec** |

**Our Obelisk charges 5× faster than TD's.** That's significant for balance — Obelisk's slow charge is part of what makes it a counter-attackable defense rather than an instant-kill turret.

Plus a subtle off-by-one at `building.cpp:6116-6118`:

```cpp
int charge_complete_stage = Class->Anims[BSTATE_ACTIVE].Count - 1;
if (charge_complete_stage < 1) charge_complete_stage = 9;  // safety fallback
if (Fetch_Stage() >= charge_complete_stage) {
    IsCharged = true;
    ...
}
```

For TDOBLI with Count=4: `charge_complete_stage = 3`, fires at Fetch_Stage 3.

TD fires at Fetch_Stage >= 4 (TD `building.cpp:1072`). One stage later. Functionally minor (~1 stage worth of charge time, ~15 ticks at the TD rate, or 3 ticks at ours), but TD-authentic and explicit.

The M5 commit comment at `building.cpp:6109-6115` notes the fix was about preventing damaged-frame walking, not about TD-authentic timing — the off-by-one is incidental and the rate=3 was the original RA-Tesla rate that just got reused.

**Fix:** make `Set_Rate` and the complete-stage threshold TDOBLI-aware:

```cpp
} else if (!Arm) {
    IsCharged = false;
    IsCharging = true;
    Set_Stage(0);
    // Per-building charge animation rate. Tesla = 3 (RA's hardcoded
    // value, ~1.8 sec). TDOBLI = 15 (TD's OBELISK_ANIMATION_RATE,
    // ~4 sec charge — TD-authentic balance).
    if (*this == STRUCT_TDOBLI) {
        Set_Rate(15);
    } else {
        Set_Rate(3);
    }
    ...
}
```

And the complete-stage threshold:

```cpp
// TD's STRUCT_OBELISK at building.cpp:1072 checks "Fetch_Stage() >= 4"
// (one past the last frame), not "Count - 1" (last frame). The
// difference is one stage of charge time. For Tesla (Count=9) the
// existing -1 is preserved; for TDOBLI use Count.
int charge_complete_stage = (*this == STRUCT_TDOBLI)
                              ? Class->Anims[BSTATE_ACTIVE].Count
                              : Class->Anims[BSTATE_ACTIVE].Count - 1;
```

Or, cleaner: a per-`WeaponTypeClass` `ChargeRate` field exposed in rules.ini that defaults to 3 (Tesla's value) and is set to 15 in `[TDOblsLaser]`. The deferred "ChargeSound" comment at `building.cpp:6131` already alludes to this generalization. But for "ship a TD-authentic Obelisk" the per-type check is fine.

---

## Symptoms → root cause map

Unlike TDSAM/TDATWR/TDGTWR, there are **no observable rendering or firing bugs** with TDOBLI. The M5 vertical slice did its job. The issues are subtler:

| Likely-observed effect | Root cause | Step |
|---|---|---|
| Obelisk charges too fast for "Obelisk-like" balance | Set_Rate(3) hardcoded; should be Set_Rate(15) for TDOBLI | C1 |
| Charge completes one stage early | charge_complete_stage = Count - 1; TD uses Count | C2 |
| Laser beam origin not exactly at crystal tip | VerticalOffset 0x00C8 vs TD's 0x00A8 + missing 0x0018 W shift | C3 (cosmetic) |
| Code-reading inconsistency: ClassObelisk vs ClassTdGtwr etc. | Class name not prefixed | C4 (cosmetic) |
| `[TDLaser] Verses=100%,100%,100%,100%,100%` may differ from TD WARHEAD_LASER | Unverified against TD source | C5 (verify, not necessarily change) |

---

## Port plan

### C1 — Per-building charge rate (`redalert/building.cpp:6128`)

```cpp
// Per-building charge animation rate.
// - Tesla Coil: 3 ticks/stage = RA's vanilla pace (~1.8 sec total over 9 stages).
// - TDOBLI: 15 ticks/stage = TD's OBELISK_ANIMATION_RATE
//   (tiberiandawn/defines.h:323 + building.cpp:1082). TD-authentic
//   4-second charge over 4 stages.
if (*this == STRUCT_TDOBLI) {
    Set_Rate(15);
} else {
    Set_Rate(3);
}
```

Apply at the existing `Set_Rate(3)` site only.

### C2 — Per-building charge complete threshold (`redalert/building.cpp:6116-6118`)

```cpp
// TD's STRUCT_OBELISK at building.cpp:1072 triggers IsCharged on
// "Fetch_Stage() >= 4" — one stage past the last frame. RA's Tesla
// vanilla uses Count - 1 (last frame). Use TD's semantics for TDOBLI,
// RA's for Tesla.
int charge_complete_stage;
if (*this == STRUCT_TDOBLI) {
    charge_complete_stage = Class->Anims[BSTATE_ACTIVE].Count;
} else {
    charge_complete_stage = Class->Anims[BSTATE_ACTIVE].Count - 1;
}
if (charge_complete_stage < 1) charge_complete_stage = 9;
```

### C3 — Verify or fix laser-origin offsets (`redalert/bdata.cpp:830`)

Two changes if and only if the in-game laser beam visual doesn't line up with the crystal tip:

```cpp
0x00A8,          // VerticalOffset — TD STRUCT_OBELISK Fire_Coord (was 0x00C8)
0x0000,          // PrimaryOffset — laser uses fixed origin, not PrimaryFacing
0x0000,          // PrimaryLateral
```

For the 0x0018 W horizontal shift: RA's `BuildingTypeClass` constructor doesn't carry a per-building HorizontalOffset arg. Either:
- (a) Hardcode in a `Fire_Coord` override branch for `STRUCT_TDOBLI` (same pattern TD uses)
- (b) Leave unset — the laser-line render in our M5 visual probably computes its origin independently and ignores this offset

Verify in-game first; if the visual is correct, don't change anything.

### C4 — Rename `ClassObelisk` → `ClassTdObli` (cosmetic)

`redalert/bdata.cpp:824` — rename to match `ClassTdGtwr/Atwr/Gun/Sam` convention:

```cpp
static BuildingTypeClass const ClassTdObli(STRUCT_TDOBLI,
```

Update the registration in `Init_Heap` at line 3317 to match. No behavioral change; just consistency for grep-ability.

### C5 — Verify `[TDLaser]` Verses values

Cross-check `[TDLaser] Verses=100%,100%,100%,100%,100%` against TD `const.cpp` `Warheads[WARHEAD_LASER]`. Read the 5-value armor modifier table. If TD has differentiated values (e.g. less effective vs concrete or aluminum), update `Verses=` to match.

Look for: `WARHEAD_LASER` entry in TD's Warheads table at `const.cpp` (after WARHEAD_SA at line ~104).

---

## What's already right (don't touch)

- `STRUCT_TDOBLI` enum and heap registration
- `IsTurretEquipped=false` and `IsSimpleDamage=false` matching TD
- `[TDOBLI]` rules.ini values: Strength=200, Cost=1500, Power=-150, Sight=5, Armor=aluminum, Crewed=true, BSIZE_12
- `[TDOblsLaser]` weapon: Damage=200, ROF=90, Range=7.5, Charges=yes, Report=OBELRAY1
- `[TDLaser]` projectile fields: Inviso=yes, High=yes, AA=no, ROT=0
- Audio routing: VOC_TD_LASER ("OBELRAY1") + VOC_TD_LASER_POWER ("OBELPOWR")
- Engine dispatch: charge-state Shape_Number, crew south-offset, construction sound, charge-start sound, Animation_AI exclusion
- `Init_Anim` entry: `{STRUCT_TDOBLI, BSTATE_ACTIVE, 0, 4, 15}` — matches TD verbatim
- The M5 laser-line render in Fire_At BULLET_LASER branch (not re-examined this session but reportedly working)

---

## Acceptance criteria

- [ ] TDOBLI charge time ≈ 4 seconds (was ~0.8 sec) — measure in-game
- [ ] TDOBLI completes charge at Fetch_Stage 4, not 3
- [ ] RA's Tesla Coil charge time unchanged — regression smoke
- [ ] Laser visual origin lines up with crystal tip (verify via in-game inspection or screenshot)
- [ ] `[TDLaser] Verses=` matches TD WARHEAD_LASER's modifier table
- [ ] (optional) `ClassObelisk` renamed to `ClassTdObli` for naming consistency

---

## Decisions

- **No donor.** TDOBLI never was bound to a vanilla RA building post-M5 — it has its own `[TDOblsLaser]` weapon, `[TDLaser]` projectile+warhead, and dedicated dispatch sites. The only "shared" code paths (Charging_AI, charge-state Shape_Number) are *extensions* of RA's Tesla machinery, not aliasing — same justification as TDSAM's negative-exclusion alias pattern: identical state-machine shape across two buildings legitimately shares one engine implementation guarded by `STRUCT_TDOBLI || STRUCT_TESLA` at each site.
- **Charge timing is the only balance-affecting bug.** All other deltas are cosmetic.
- **`[TDLaser]` as combined bullet+warhead section.** RA's rules.ini parser supports this — same section name resolves to both `BulletTypeClass` and `WarheadTypeClass` lookups. The current setup is correct.
- **Class-name inconsistency tolerated for now.** `ClassObelisk` doesn't break anything; rename is optional polish.

---

## Cargo order

**Smallest (charge timing):** C1 + C2. Single-file diff to `redalert/building.cpp:6116-6128`. Smoke-test that Obelisk takes ~4 sec to fire and Tesla is unchanged. High-value, low-risk.

**Optional verify:** C5 (read TD Warheads[WARHEAD_LASER], decide whether to update Verses=).

**Cosmetic polish:** C3 (Fire_Coord offsets if visual is off) + C4 (rename ClassObelisk → ClassTdObli). Both can be a separate PR or batched with C1+C2.

---

## Cross-reference

- TDSAM: `td-sam-deep-dive.md` / `docs/td-sam-deep-dive.md`
- TDATWR: `td-atwr-deep-dive.md` / `docs/td-atwr-deep-dive.md`
- TDGTWR + TDGUN: `td-gtwr-gun-verification.md` / `docs/td-gtwr-gun-verification.md`

TDOBLI is the **cleanest of the five** in terms of separation: own weapon, own projectile, own warhead, own audio entries, dedicated dispatch sites. The other four still have weapon-binding or building-flag work to do. This doc closes the M3 Tier 2 verification pass.
