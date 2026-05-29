# TDSAM port — TD-source-grounded deep dive

> **RESOLVED — separated + shipped (v0.50).** TDSAM now runs its own code path and binds `Primary=TDNike` (→ `Projectile=TDPatriot`, `Warhead=TDAP`) in rules.ini — no RA-vanilla `[Nike]` alias. The body below is retained as TD-source reference / the plan that was executed.

**Status:** STRUCT_TDSAM ships in M3 as a *bug-shaped* port — engine + asset work done, but every dispatch piggybacks on RA's `STRUCT_SAM` branch via `(STRUCT_SAM || STRUCT_TDSAM)` aliases, and the rules.ini binds `Primary=Nike` to RA's vanilla weapon. That violates the separation principle: TDSAM should run TD's own building/weapon/projectile code, not RA's nearest-shaped equivalent. This doc is the corrected plan — wholesale port of TD's `STRUCT_SAM`.

**Session that produced it:** 2026-05-22, max-effort deep dive after Luke flagged that the current build was "rendering the RA SAM" with wrong sounds and broken open/turret animation.

**Guiding principle:** the *whole point* of full STRUCT_TD-prefixed separation is that TD entities run TD's own code paths — own state machine, own render logic, own weapon, own projectile, own audio routing. No donor. No "modeled on RA's SAM." Each piece is a direct port from `reference/vanilla-conquer/tiberiandawn/`. Per [[feedback-no-donor-for-td-separation]] / [[project-building-separation-committed]] / [[project-td-prefix-convention]].

---

## What TD's SAM actually is (verified against `reference/vanilla-conquer/tiberiandawn/`)

TD's SAM is one of the most state-rich buildings in the game. It is **not** "rotating turret that fires." It is an underground launcher that rises, tracks, double-shoots, locks back to north, and lowers.

### 1. The state machine (TD `building.cpp:105-116, 4281-4439`)

```cpp
enum SAMState {
    SAM_NONE = -1,
    SAM_UNDERGROUND, // hidden, awaiting target
    SAM_RISING,      // door anim frames 0-15, ratched up via Set_Stage
    SAM_READY,       // up, rotating to face TarCom
    SAM_FIRING,      // first shot
    SAM_READY2,      // re-rotate after shot 1
    SAM_FIRING2,     // second shot
    SAM_LOCKING,     // rotating back to DIR_N
    SAM_LOWERING,    // door anim frames 48-63 reversed
};
```

Transition logic (TD `building.cpp:4281`):

| From | When | To | Notes |
|---|---|---|---|
| `SAM_UNDERGROUND` | `Target_Legal(TarCom)` | `SAM_RISING` | `Set_Rate(2); Set_Stage(0);` |
| `SAM_UNDERGROUND` | no target | (stays, returns to `MISSION_GUARD`) | |
| `SAM_RISING` | `Fetch_Stage() == 15` | `SAM_READY` or `SAM_LOWERING` | `Set_Rate(0); PrimaryFacing = DIR_N;` |
| `SAM_READY` | target alive + air + altitude > 0 | rotate via `Set_Desired`, then `SAM_FIRING` | — |
| `SAM_READY` | target lost | `SAM_LOCKING` | one-second pause |
| `SAM_FIRING` | `Can_Fire == FIRE_OK` | `Fire_At(TarCom, 0); SAM_READY2` | |
| `SAM_FIRING` | `FIRE_FACING` | `SAM_READY` | re-rotate |
| `SAM_READY2` | target re-acquired | rotate, then `SAM_FIRING2` | |
| `SAM_FIRING2` | `Can_Fire == FIRE_OK` | `Fire_At(TarCom, 0); SAM_LOCKING` | `return TICKS_PER_SECOND * 3` — cooldown |
| `SAM_LOCKING` | `PrimaryFacing == DIR_N` | `SAM_LOWERING` | `Set_Rate(2); Set_Stage(48);` |
| `SAM_LOCKING` | not yet at N | `PrimaryFacing.Set_Desired(DIR_N)` | |
| `SAM_LOWERING` | `Fetch_Stage() >= 63` | `SAM_UNDERGROUND` | `Set_Rate(0); Set_Stage(0); return TICKS_PER_SECOND` |

Note: TD's `Status` is a `char` field on `MissionClass` (TD `mission.h:62`). Default-init is `0` = `SAM_UNDERGROUND` — no explicit init in `Grand_Opening` needed.

### 2. The render path (TD `building.cpp:548-571`)

```cpp
if (Class->IsTurretEquipped) {
    shapenum = UnitClass::BodyShape[Facing_To_32(PrimaryFacing.Current())];

    if (*this == STRUCT_SAM) {
        // Raised states: 32 rotation frames live at frames 16-47.
        if (Status == SAM_READY || Status == SAM_FIRING || Status == SAM_READY2 || Status == SAM_FIRING2
            || Status == SAM_LOCKING) {
            shapenum += 16;
        } else {
            // RISING (0-15) and LOWERING (48-63) drive shapenum directly from Stage.
            shapenum = Fetch_Stage();
        }
    }
    if (Health_Ratio() < 0x0080) shapenum += 64;  // Damaged offset.
}
```

TD's SAM SHP layout (verified against the 129-frame TGA tileset we already have, ±1 construction frame):

```
0-15    Rising (door open + launcher up)        — driven by Set_Stage / Fetch_Stage
16-47   Raised, 32 rotation frames              — driven by BodyShape[Facing_To_32]
48-63   Lowering (launcher down + door close)   — driven by Set_Stage / Fetch_Stage
64-79   Damaged rising
80-111  Damaged raised rotation
112-127 Damaged lowering
[128]   Optional bib/construction tail
```

This is a fundamentally different frame layout from RA's SAM SHP (0-31 rotation, 32-63 damaged). Indexing TD assets with RA's `BodyShape[Dir_To_32(facing)]` will pull from the *rising* sub-sequence — partially-raised launcher pointing 5° off — which is what Luke saw as "looks like the RA SAM," but is actually frame 0-15 of a TD SHP confusingly indexed.

### 3. Rotation speed (TD `building.cpp:1281-1289`)

```cpp
if (*this == STRUCT_SAM) {
    if (PrimaryFacing.Rotation_Adjust(15)) Mark(MARK_CHANGE);
} else {
    if (PrimaryFacing.Rotation_Adjust(12)) Mark(MARK_CHANGE);
}
```

TD's SAM rotates at **15 units/tick**, regular turrets at 12. Don't omit this — combined with the state machine, it's what makes the SAM feel responsive.

### 4. State-keyed armor (TD `building.cpp:1492-1495`)

```cpp
if (*this == STRUCT_SAM && Status == SAM_UNDERGROUND) {
    damage /= 2;
    damage++; // Never less than 1.
}
```

Underground SAM takes half damage. This is the answer to the deep-dive doc's "suspected bug #6" — *yes*, TD has state-keyed armor, and it's a `Take_Damage` modifier (not an `Armor=` rules field). The RA pipeline supports it the same way (`BuildingClass::Take_Damage` exists and follows the same shape).

### 5. The firing animation overlay (TD `building.cpp:828-836`)

```cpp
if (*this == STRUCT_SAM) {
    AnimClass* anim = new AnimClass(
        (AnimType)(ANIM_SAM_N + Dir_Facing(PrimaryFacing.Current())),
        Center_Coord());
    if (anim) anim->Attach_To(this);
    Sound_Effect(weapon->Sound, Coord);
}
```

When SAM fires, TD spawns a standalone `ANIM_SAM_<dir>` overlay at `Center_Coord()` (not `Fire_Coord` — the overlay's frames already encode the muzzle position per direction). Uses `weapon->Sound` (= `VOC_ROCKET2` for `WEAPON_NIKE` per TD `const.cpp:91`).

**Good news for the RA port:** RA's `TechnoClass::Fire_At` already handles `ANIM_SAM_N + Dir_Facing(PrimaryFacing.Current())` automatically (`techno.cpp:3392-3393`) when a weapon's `Anim=SAMFIRE` resolves to `ANIM_SAM_N`. RA's `adata.cpp:142-298` already defines the 8 directional `SAMN`..`SAMNE` entries with TD's frame layout (`18 * direction_index` starting frames, 18 stages each). So this overlay path Just Works once the weapon is wired correctly.

### 6. Muzzle position (TD `building.cpp:2804-2836`)

```cpp
case STRUCT_SAM:
case STRUCT_TURRET:
    coord = Coord_Move(coord, DIR_N, 0x0030);
    coord = Coord_Move(coord, PrimaryFacing.Current(), 0x0080);
    break;
```

0x30 N + 0x80 in `PrimaryFacing.Current()` direction. Matches the offsets we already have on `ClassTdSam` (`bdata.cpp:813-815`). **This is already correct — the deep-dive doc's "fires from the back" symptom (bug #1) is a render mismatch, not an offset mismatch.** Once the render uses frame 16+ (raised rotation) instead of frame 0-15 (rising), the launcher will point where `PrimaryFacing.Current()` says it does, and the muzzle will line up.

### 7. Aiming tolerance (TD `building.cpp:Can_Fire`)

RA already has this: `if (ABS(diff) > (*this == STRUCT_SAM ? 64 : 8))` (`Can_Fire`). SAM has a much wider firing arc (±64) than other turrets (±8) so it can fire mid-rotation. Needs `STRUCT_TDSAM`.

### 8. Threat scanning (TD `building.cpp:Greatest_Threat`)

TD's SAM only adds `THREAT_AREA` and `THREAT_AIR` (via `IsAntiAircraft` bullet check) — never ground, infantry, or buildings. RA's vanilla SAM dispatch already does this. Needs `STRUCT_TDSAM`.

### 9. Anims[BSTATE_*] is NOT used for rise/lower (TD `bdata.cpp:3786-3816`)

`STRUCT_SAM` is **not** in TD's `_anims[]` table. All Anims default to `(Start=0, Count=1, Rate=0)`. The rise/lower is driven directly by `Set_Rate(2) + Set_Stage(0 or 48) + Fetch_Stage` calls inside `Mission_Attack`, **not** via `Begin_Mode(BSTATE_ACTIVE)`. Don't set TDSAM's `ActiveAnim*` in `rules.ini` to anything but `(0,1,0)`.

---

## Symptoms → root cause map

Mapping Luke's session report to the TD-source findings above:

| Reported symptom | Root cause | TD reference |
|---|---|---|
| "Sounds are RA sounds" | `[Nike].Report=MISSILE1`. TD's SAM uses `VOC_ROCKET2`. | TD `const.cpp:91` — `WEAPON_NIKE` → `VOC_ROCKET2` |
| "SAM opening isn't working properly" | RA's 2-state machine has no `SAM_RISING` state; no `Set_Stage(0); Set_Rate(2)` is ever issued. Building never animates the rise. | TD `building.cpp:4291-4317` |
| "Renders the RA SAM" | Render reads `BodyShape[Dir_To_32]` (frames 0-31) but TD's SHP has frames 0-15 = rising. So rotation cycle pulls partially-raised frames — visually looks like a half-built RA SAM that won't aim. | TD `building.cpp:548-571` |
| "Opening animation doesn't work nice" | Same as above — no rise driven, plus the frame layout mismatch. | |
| "Turret doesn't [work]" | `BodyShape[Facing_To_32]+16` is TD's raised-rotation indexing. RA doesn't apply `+16`. So even if the facing is correct, the engine renders frame N (rising) instead of N+16 (raised rotation). | TD `building.cpp:558-560` |
| "Fires from the back of the launcher" (deep-dive bug #1) | Same as "Renders the RA SAM" — `PrimaryFacing.Current()` says "facing east" and the muzzle math is correct, but the rendered launcher is showing frame ~4 of the rising sequence, which is visually pointing up-and-back. Fix the render and the muzzle aligns. | TD `building.cpp:548-571` + `2828-2832` |

So **almost every symptom is the render path + missing rise/lower states.** Audio is one small additional fix.

---

## Port plan — TDSAM-only dispatch, 100% separate

All steps add **dedicated `STRUCT_TDSAM` branches**. Wherever the current uncommitted diff has `(STRUCT_SAM || STRUCT_TDSAM)`, split it into two: keep RA's vanilla branch as-is, add a new TD-logic branch for TDSAM.

### M1 — Add dedicated `TdSamState` enum (`redalert/building.cpp` near line 118)

Don't touch RA's existing `SAMState` enum — RA's vanilla SAM continues to use it. Add a parallel enum for TDSAM, matching TD's order verbatim:

```cpp
// Existing RA SAMState stays untouched:
enum SAMState {
    SAM_READY,    // 0
    SAM_FIRING,   // 1
};

// NEW — TD-source-ordered SAM states for STRUCT_TDSAM only.
// Direct port of tiberiandawn/building.cpp:105-116.
enum TdSamState {
    TDSAM_NONE = -1,
    TDSAM_UNDERGROUND,   // 0 — default char init, matches TD semantics
    TDSAM_RISING,        // 1
    TDSAM_READY,         // 2
    TDSAM_FIRING,        // 3
    TDSAM_READY2,        // 4
    TDSAM_FIRING2,       // 5
    TDSAM_LOCKING,       // 6
    TDSAM_LOWERING,      // 7
};
```

Both enums are stored in the shared `Status` char field on `MissionClass` — the numeric values overlap (`SAM_READY=0` and `TDSAM_UNDERGROUND=0`) but never confuse because each dispatch site is guarded by `*this == STRUCT_SAM` vs `*this == STRUCT_TDSAM` at the top.

Benefit of separate enums vs extending the shared one: zero risk of touching RA's vanilla code paths. The TDSAM dispatch reads `Status` with `TDSAM_*` semantics, RA's reads with `SAM_*` semantics — same byte, different interpretation. No need to re-init `Status` for vanilla SAM, no need to audit `Status = 0` assumptions elsewhere.

`TDSAM_UNDERGROUND = 0` aligns with char-default-init, so newly-placed TDSAMs are automatically in the underground state with no extra constructor work.

### M2 — `Shape_Number` split (`redalert/building.cpp:670-692`)

Current:

```cpp
if (*this == STRUCT_SAM || *this == STRUCT_TDSAM) {
    // (commented-out Fetch_Stage path)
}
```

Replace with two distinct branches:

```cpp
if (*this == STRUCT_SAM) {
    // RA's existing behavior — leave untouched.
    // (No-op render override; falls through to BodyShape[Dir_To_32(facing)] above.)
} else if (*this == STRUCT_TDSAM) {
    // TD's render: rising/lowering uses Fetch_Stage, raised uses BodyShape+16.
    // Direct port of tiberiandawn/building.cpp:548-571.
    if (Status == TDSAM_READY || Status == TDSAM_FIRING || Status == TDSAM_READY2
        || Status == TDSAM_FIRING2 || Status == TDSAM_LOCKING) {
        shapenum = UnitClass::BodyShape[Dir_To_32(PrimaryFacing.Current())] + 16;
    } else {
        shapenum = Fetch_Stage();
    }
    if (Health_Ratio() < 0x0080) shapenum += 64;
}
```

Use RA's `Dir_To_32` (TD's `Facing_To_32` doesn't exist in RA; the two functions return equivalent indices). Verify on first build that the 0-127 frame indices land on the correct TGA frames.

### M3 — `Mission_Attack` split (`redalert/building.cpp:4283-4343`)

Today: aliased branch with RA's 2-state machine. Split into:

```cpp
if (*this == STRUCT_SAM) {
    // RA's existing 2-state machine — unchanged.
    /* ... existing READY/FIRING block, fire both Primary + Secondary ... */
} else if (*this == STRUCT_TDSAM) {
    // TD's full 8-state machine — direct port from tiberiandawn/building.cpp:4284-4439.
    switch (Status) {
        case TDSAM_UNDERGROUND: /* ... */ break;
        case TDSAM_RISING:      /* ... */ break;
        case TDSAM_READY:       /* ... */ break;
        case TDSAM_FIRING:      /* ... */ break;
        case TDSAM_READY2:      /* ... */ break;
        case TDSAM_FIRING2:     /* ... */ break;
        case TDSAM_LOCKING:     /* ... */ break;
        case TDSAM_LOWERING:    /* ... */ break;
    }
    return (1);
}
```

Port verbatim — TD's logic uses only stable RA APIs (`Set_Rate`, `Set_Stage`, `Fetch_Stage`, `PrimaryFacing.Set_Desired`, `Can_Fire`, `Fire_At`, `Assign_Mission`, `Assign_Target`, `Target_Legal`, `Is_Target_Aircraft`, `As_Aircraft`). RA's `AircraftClass::Height` replaces TD's `Altitude` — already done in the current aliased branch (line 4317).

**One subtle change for RA → TD signature:** TD's `Fire_At(TarCom, 0)` fires `Primary` (`which == 0`). TD's two-shooter logic uses two sequential `TDSAM_FIRING` / `TDSAM_FIRING2` *states*, both calling `Fire_At(TarCom, 0)` — the second shot is a Primary refire after `TDSAM_READY2`'s pause, not a secondary-weapon firing. **Do not also `Fire_At(TarCom, 1)`** — TDSAM has no secondary weapon defined.

### M4 — Rotation speed (new branch in `BuildingClass::AI`)

Locate the rotation block in RA's `building.cpp` (the equivalent of TD `building.cpp:1275-1290`; we already process `IsTurretEquipped` rotation). Add:

```cpp
if (*this == STRUCT_TDSAM) {
    if (PrimaryFacing.Rotation_Adjust(15)) Mark(MARK_CHANGE);
} else {
    if (PrimaryFacing.Rotation_Adjust(12)) Mark(MARK_CHANGE);
}
```

### M5 — Underground half-damage (new branch in `Take_Damage`)

In `BuildingClass::Take_Damage`, before the `TechnoClass::Take_Damage` call. Direct port of TD `building.cpp:1492-1495`:

```cpp
if (*this == STRUCT_TDSAM && Status == TDSAM_UNDERGROUND) {
    damage /= 2;
    damage++;
}
```

### M6 — Surgical de-aliasing pass

Walk every site the current uncommitted diff added `STRUCT_TDSAM` next to `STRUCT_SAM`:

| Site | Current | Action |
|---|---|---|
| `building.cpp:1078` (radar-jammer) | shared OR | Split into separate `STRUCT_SAM` and `STRUCT_TDSAM` branches with identical bodies (or factor into helper). |
| `building.cpp:1617` (auto-retaliation exclude) | shared `!=` chain | OK to keep aliased — both should NOT auto-retaliate. Add comment explaining the alias is intentional. *Acceptable exception* to the 100%-separate rule when behavior is identical AND the alternative is two-line duplication. |
| `building.cpp:2012` (assign-target range bypass) | shared `!=` chain | Same as above. |
| `building.cpp:3181` (What_Action attack veto) | shared OR | Same. |
| `building.cpp:3365` (Can_Fire arc tolerance) | shared OR | Same — both want ±64. |
| `building.cpp:6247` (stagechange Mark) | shared OR | Same — both need refresh on stage change. |
| `techno.cpp:1701` (grounded-aircraft filter) | shared OR | Same — both want this. |

Decision: keep the *negative*-exclusion patterns (where both buildings should be skipped) as aliased OR/!= chains with an explicit comment. The *positive*-dispatch sites that drive distinct render/AI behavior (Mission_Attack, Shape_Number, AI rotation, Take_Damage) MUST be split. Update `bdata.cpp:706` comment to reflect this.

### M7 — Port TD's `WEAPON_NIKE` and `BULLET_SAM` to rules.ini

Currently `[TDSAM] Primary=Nike` shares RA's vanilla anti-air weapon, which fires RA's vanilla `AAMissile` projectile. Both have stats that diverge from TD's authentic SAM. The separation principle requires we port both TD's weapon and TD's projectile as standalone `[TDxxx]` rules.ini sections — and bind TDSAM to *those*, not to RA's vanilla entries.

**TD source — `WEAPON_NIKE` (`const.cpp:91`):**
```cpp
{BULLET_SAM, 50, 50, 0x0780, VOC_ROCKET2, ANIM_NONE},  // WEAPON_NIKE
```
Field order per `type.h:50-91`: `{Fires, Attack, ROF, Range, Sound, Anim}`. So:
- Damage: 50
- ROF: 50
- Range: 0x0780 leptons = 1920 leptons = **7.5 cells** (256 leptons/cell)
- Sound: `VOC_ROCKET2`
- Anim: `ANIM_NONE` (RA's `TechnoClass::Fire_At` spawns `ANIM_SAM_N + Dir_Facing(PrimaryFacing.Current())` automatically when this resolves to `ANIM_SAM_N` — see techno.cpp:3392. We get that behavior by setting `Anim=SAMFIRE`.)

**TD source — `BULLET_SAM` aka ClassPatriot (`bbdata.cpp:197`):**
```cpp
static BulletTypeClass const ClassPatriot(BULLET_SAM,
    "MISSILE",     // Image
    true,          // High (over walls)
    true,          // Homes
    false,         // Arcs
    false,         // Drops
    false,         // Invisible
    true,          // Proximity arm
    true,          // Animates flame
    true,          // Has fuel
    false,         // No facing variation
    false,         // Inaccurate
    false,         // Translucent
    true,          // AA-capable
    0,             // Arming
    0,             // Range override
    MPH_VERY_FAST, // Speed
    10,            // ROT (turn rate)
    WARHEAD_AP,
    ANIM_VEH_HIT1);
```

Two rules.ini additions (replacing nothing; both are new TD-prefixed sections):

```ini
; TD Nike — dedicated TDSAM anti-air missile launcher weapon.
; Source: tiberiandawn/const.cpp WEAPON_NIKE
;   {BULLET_SAM, 50, 50, 0x0780, VOC_ROCKET2, ANIM_NONE}
; NOT aliased to RA's [Nike] — RA's has ROF=20, this has TD-authentic ROF=50.
[TDNike]
Damage=50
ROF=50            ; TD-authentic (RA's [Nike] uses 20)
Range=7.5         ; TD 0x0780 leptons = 7.5 cells (RA's [Nike] also 7.5)
Projectile=TDPatriot
Speed=60          ; MPH_VERY_FAST per TD's ClassPatriot — verify exact MPH→Speed mapping in RA
Warhead=AP        ; TD WARHEAD_AP
Report=ROCKET2    ; TD VOC_ROCKET2
Anim=SAMFIRE      ; Resolves to ANIM_SAM_N — RA's techno.cpp:3392 spawns directional SAMFIRE overlay
```

```ini
; TD BULLET_SAM (Patriot) — the projectile TDSAM's TDNike fires.
; Source: tiberiandawn/bbdata.cpp ClassPatriot at line 197.
; Distinct from RA's [AAMissile]: TD's BULLET_SAM is MPH_VERY_FAST + ROT=10
; (more agile than RA's AAMissile), uses "MISSILE" sprite (not "DRAGON"),
; and is NOT inaccurate (RA's AAMissile = Inaccurate=yes).
[TDPatriot]
Image=MISSILE     ; TD's BULLET_SAM uses MISSILE sprite, not DRAGON
High=yes
Homing=yes        ; TD's "Homes=true"
Shadow=no
Proximity=yes
Animates=yes
Ranged=yes        ; TD's "Has fuel=true"
AA=yes            ; TD's "AA-capable=true"
AG=no             ; TD SAM is AA-only
ROT=10            ; TD ROT
Rotates=yes
; Inaccurate=no by default — TD's BULLET_SAM is accurate (unlike BULLET_SSM)
```

Then update the TDSAM rules.ini section:

```ini
[TDSAM]
; ... other fields unchanged ...
Primary=TDNike     ; was: Primary=Nike (RA's vanilla)
; Drop the comment "vanilla anti-air SAM missile (same one RA's SAM uses)" — no longer true.
```

`ROCKET2` audio routing is already in place: `audio.cpp:253` defines `VOC_TD_ROCKET2` and `SFXEVENTSNONLOCALIZED.XML:6047-6061` has `RAC_SFX_ROCKET2` / `RAR_SFX_ROCKET2` sourcing the TDC/TDR rocket2 WAVs. No new audio plumbing needed.

**Two open verifications during implementation:**
- RA's `Speed=` field semantics — TD uses `MPH_VERY_FAST` (an enum/constant). Check what cell-per-second value that maps to and pick the corresponding `Speed=` integer. RA `[Heat-Seeker]` or `[AAMissile]` is a reference for "what does Speed=X give you."
- RA's `Homing=yes` — confirm that's the right rules.ini field name for "this projectile homes on target." If not, the equivalent is whatever maps to `BulletTypeClass::IsHoming`.

### M8 — Manifest sync (`scripts/buildings_manifest.py:576-607`)

Update the `TDSAM` dict's `"primary"` field from `None` → `"TDNike"` so re-emit doesn't drop the binding. Update the `"notes"` field to point at this doc:

```python
"notes": "TD Nod SAM Site (BSIZE_21 underground launcher with 8-state "
         "rise/rotate/fire/fire/lock/lower cycle). Wholesale port of "
         "tiberiandawn/ STRUCT_SAM per docs/td-sam-deep-dive.md. "
         "Weapon=TDNike (TD WEAPON_NIKE), projectile=TDPatriot "
         "(TD BULLET_SAM/'MISSILE').",
```

---

## What's already right (don't touch)

- `STRUCT_TDSAM` definition in `defines.h` and the heap registration in `bdata.cpp:3325`.
- `ClassTdSam` flags/offsets in `bdata.cpp:795` — `0x0030/0x0080`, BSIZE_21, IsTurretEquipped=true. Match TD's `ClassSAM` (`bdata.cpp:790`).
- TGA frame layout: `TDSAM.ZIP` has 129 frames (0-128); `RA_STRUCTURES.XML:28359+` maps Shape 0-128. M2's render fix indexes into these correctly.
- `TDSAMMAKE.ZIP` for construction animation.
- `BuildupAnim*` settings on `[TDSAM]` (30 frames at rate 2) — standalone from the rise/lower states.
- RA's `TechnoClass::Fire_At` already handles `ANIM_SAM_N + Dir_Facing(PrimaryFacing.Current())` (techno.cpp:3392-3394) — M7's `Anim=SAMFIRE` on TDNike resolves to ANIM_SAM_N and the directional overlay path Just Works.
- RA's 8 `SAMN..SAMNE` `AnimTypeClass` entries in `adata.cpp:142-298` — identical to TD's, already point at `"SAMFIRE"`.
- `VOC_TD_ROCKET2` audio entry (`audio.cpp:253`) and `RAC_SFX_ROCKET2`/`RAR_SFX_ROCKET2` in SFX XML — TD-port sound infrastructure is in place from prior ports.

---

## Test plan (MP-vs-self via 2-Deck Tailscale)

Skirmish AI [doesn't build aircraft](memory:project-ai-no-aircraft-builds), so AA testing needs a real opponent flying real aircraft. Use the planned 2-Deck setup from the previous deep-dive doc (steps unchanged):

1. Get `steamdeck2` on Tailscale; copy SSH keys from steamdeck → steamdeck2.
2. Update `deploy.sh` to push to both Decks (wrap in `for host in steamdeck steamdeck2; do scp ... $host:...; done`).
3. MP lobby: one Deck Allied (Longbow + Hind harassment), other Nod (build TDSAM after TDHAND → TDHQ → tech path).
4. Observe end-to-end cycle: TDSAM underground at idle → rises on Longbow approach → rotates to track → fires *first* missile (muzzle from raised launcher tip) → tracks for second shot → fires *second* → rotates to N → lowers → returns underground. Sound is `ROCKET2` ×2 (not `MISSILE1`).

**Diagnostic instrumentation (M8):** add a `tf_tdsam_state.log` tracing `Status`/`PrimaryFacing.Current()`/`Fetch_Stage()`/`Set_Rate` per tick for any TDSAM. Writes to `$USERPROFILE/Documents/CnCRemastered/` per [[reference-diagnostic-paths]]; keep stubbed under `#if 0` post-validation per [[feedback-keep-diagnostics-until-v1]].

**Single-Deck smoke (before MP):** force-fire on a friendly aircraft (existing Luke workaround) — confirms the *rise → rotate → fire → lower* visual cycle without needing MP. Won't exercise the two-shot READY2/FIRING2 path because force-fire targets one unit at a time; that's MP-only.

---

## Acceptance criteria

- [ ] All `(STRUCT_SAM || STRUCT_TDSAM)` *positive*-dispatch ORs split into separate branches.
- [ ] Negative-exclusion `(STRUCT_SAM && STRUCT_TDSAM)` `!=` chains tagged with a comment explaining the intentional alias.
- [ ] TDSAM starts underground (frame 0 / `TDSAM_UNDERGROUND`) on placement.
- [ ] Aircraft enters range → TDSAM rises smoothly through 16 frames → locks at DIR_N.
- [ ] Launcher rotates to track target at 15-units/tick (~25% faster than turret/AGUN).
- [ ] Fires *Primary only*, twice, with `ROCKET2` audio each shot.
- [ ] Between shots, brief re-rotation in `TDSAM_READY2`.
- [ ] After two shots, rotates back to DIR_N (`TDSAM_LOCKING`), then lowers (`TDSAM_LOWERING`), returns to underground.
- [ ] Underground takes half damage (test via Yak strafe or ground-fire while idle).
- [ ] No visible reference to RA's SAM SHP frames — every render frame should be a `tdsam-NNNN.tga`.
- [ ] `Primary=TDNike` binding emits a `[TDNike]` weapon (not RA's `[Nike]`); `[TDNike].Projectile=TDPatriot` (not RA's `AAMissile`).
- [ ] RA's vanilla SAM continues to work exactly as before (regression smoke: build vanilla RA SAM in a 1v1 RA-vs-RA skirmish, fire on Yak).

---

## Decisions

- **No donor.** `ClassTdSam` flag values, `TdSamState` enum, `Mission_Attack` state machine, `Shape_Number` logic, `[TDNike]` weapon, `[TDPatriot]` projectile — every one is a wholesale port from `reference/vanilla-conquer/tiberiandawn/`. Not "modeled on RA's SAM." Per [[feedback-no-donor-for-td-separation]].
- **Armor parity:** stay TD-authentic (200 hp / steel). Fragile-when-up is by design per [[feedback-difficulty-philosophy]]; underground half-damage gives durability where it matters. The deep-dive doc's old "decision deferred" is closed.
- **Two enums.** `TdSamState` is dedicated to TDSAM; RA's `SAMState` stays untouched. Both stored in the shared `Status` byte but never confused because each dispatch is guarded by `STRUCT_SAM` vs `STRUCT_TDSAM` first.
- **Aliased exclusion sites:** acceptable to keep `STRUCT_SAM` and `STRUCT_TDSAM` in the same `!=`/`==` chain when behavior is identical AND splitting would only duplicate two lines. Document each one. The 100%-separate rule is about *distinct behavior* in distinct branches; behavioral parity in exclusion lists doesn't need duplicate code.
- **Cargo of changes per commit:** M1 + M3 are tightly coupled (enum + Mission_Attack). M2 (Shape_Number) depends on M3 because it reads `Status`. Suggested commit shape: one PR with M1+M2+M3+M4+M5 (engine port) + one PR with M6+M7+M8 (cleanup + audio + weapon/projectile + manifest). Or one fat PR if Luke prefers — both fine.

---

## What's superseded by this doc

The earlier "Phase 1-5" port plan in this file (pre-deep-dive) and the pushback-superseded version (which framed `[TDNike]` as approximating RA's `[Nike]` and described enum surgery as "extending the shared `SAMState`") are both retired. The current state:
- **State machine**: dedicated `TdSamState` enum + wholesale port of TD's 8-state `Mission_Attack`
- **Render**: dedicated `STRUCT_TDSAM` Shape_Number branch with Status-aware frame indexing
- **Weapon**: dedicated `[TDNike]` rules.ini section with TD-authentic Damage=50/ROF=50/Range=7.5
- **Projectile**: dedicated `[TDPatriot]` rules.ini section with TD's `MISSILE` sprite + ROT=10 + MPH_VERY_FAST
- **Audio**: `Report=ROCKET2` (already plumbed)
- **Anim overlay**: `Anim=SAMFIRE` → ANIM_SAM_N → directional overlay via RA's existing `techno.cpp:3392`

The original 5 "confirmed bugs" + 2 "suspected" all collapse into M2 + M3 + M5 + M7.
