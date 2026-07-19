# TDGTWR + TDGUN — TD-source verification

> **RESOLVED — separated + shipped (v0.50).** TDGTWR now binds `Primary=TDChainGun` (Damage=25/ROF=50, TD-authentic — no RA `[Vulcan]` alias); TDGUN runs its own separated chain. The body below is retained as TD-source reference / the plan that was executed.

**Status:** TDGTWR has a balance-affecting weapon mismatch (still bound to RA's vanilla `[Vulcan]`) plus one ClassTdGtwr offset bug. TDGUN is mostly TD-authentic — building flags correct, weapon stats correct — but its projectile binding (`Projectile=Cannon`) reuses RA's vanilla section in violation of the separation principle.

**Session that produced it:** 2026-05-22, paired with `td-sam-deep-dive.md` and `td-atwr-deep-dive.md`. Goal: get all four M3 Tier 2 defensive buildings (TDGTWR/TDATWR/TDGUN/TDSAM) weapon-correct so future balance work has TD-authentic baselines.

**Guiding principle:** wholesale port of TD's building + weapon + projectile + audio. No donor. No "modeled on Vulcan" / "modeled on Cannon." Per [[feedback-no-donor-for-td-separation]] / [[project-building-separation-committed]].

---

## TD source values (verified)

### TDGTWR = TD's `STRUCT_GTOWER` (TD `bdata.cpp:320-370`)

```cpp
static BuildingTypeClass const ClassGTower(STRUCT_GTOWER,
    /* ... */
    true,   // IsSimpleDamage
    /* ... */
    false,  // IsTurretEquipped       ← static building, no rotation
    false,  // IsTwoShooter
    true,   // IsRepairable
    true,   // IsBuildable
    true,   // IsCrew                  ← spawns infantry on death
    /* ... */
    DIR_N,
    200,    // Strength
    3,      // Sight
    500,    // Cost
    /* ... */
    WEAPON_CHAIN_GUN,
    WEAPON_NONE,
    ARMOR_WOOD,
    0, 0, 0, 10,   // CanEnter/Capacity/Power/Drain
    BSIZE_11,
    /* ... */);
```

TD `building.cpp` dispatch for `STRUCT_GTOWER`:

| Line | What |
|---|---|
| 2784-2787 | Fire_Data: `coord += DIR_N 0x0030; dist = 0x0040;` |
| 2815-2821 | Fire_Coord: `coord += DIR_N 0x0030; if (target) coord += Direction(coord, target) 0x0040;` |

That's the entire dispatch surface. No Mission_Attack, no Shape_Number, no AI, no Power_Fraction, no crew-spawn-offset. Simplest defensive building in TD.

### TDGUN = TD's `STRUCT_TURRET` (TD `bdata.cpp:475-530`)

```cpp
static BuildingTypeClass const ClassTurret(STRUCT_TURRET,
    /* ... */
    false,  // IsSimpleDamage          ← uses full damaged-frame range
    /* ... */
    true,   // IsTurretEquipped        ← actual rotating turret
    false,  // IsTwoShooter
    true,   // IsRepairable
    true,   // IsBuildable
    true,   // IsCrew
    /* ... */
    (DirType)208,   // Starting facing — roughly south-southwest
    200,    // Strength
    5,      // Sight
    600,    // Cost (was 250 pre-PATCH)
    /* ... */
    WEAPON_TURRET_GUN,
    WEAPON_NONE,
    ARMOR_STEEL,
    0, 0, 0, 20,
    BSIZE_11,
    /* ... */);
```

TD `building.cpp` dispatch for `STRUCT_TURRET`:

| Line | What |
|---|---|
| 2784-2787 | Fire_Data (default case via fallthrough) |
| 2795-2798 | Fire_Data SAM/TURRET branch: `coord += DIR_N 0x0030; dist = 0x0080;` |
| 2829-2832 | Fire_Coord SAM/TURRET branch: `coord += DIR_N 0x0030; coord += PrimaryFacing.Current() 0x0080;` |
| 4553, 4580 | Version-1.07-pre-MP-quirks (not relevant to us — `GameToPlay != GAME_NORMAL` gate) |

Also relies on the generic `AI` rotation block (TD `building.cpp:1281-1290`) which rotates at 12 units/tick for non-SAM turrets — `Rotation_Adjust(12)`.

### TD `WEAPON_CHAIN_GUN` (TD `const.cpp:71`)

```cpp
{BULLET_SPREADFIRE, 25, 50, 0x0400, VOC_MINI, ANIM_GUN_N},  // WEAPON_CHAIN_GUN
```

Per `type.h:50-91` field order `{Fires, Attack, ROF, Range, Sound, Anim}`:
- Bullet: `BULLET_SPREADFIRE` ("50cal", invisible bullet trail)
- Damage: 25
- ROF: 50
- Range: 0x0400 leptons / 256 = **4 cells**
- Sound: `VOC_MINI` (= `GUN8` per `audio.cpp:128`)
- Anim: `ANIM_GUN_N` (8-direction gun-fire overlay)

### TD `BULLET_SPREADFIRE` aka ClassSpreadfire (TD `bbdata.cpp:87`)

```cpp
static BulletTypeClass const ClassSpreadfire(BULLET_SPREADFIRE,
    "50cal",         // Image
    true,            // High
    false,           // Homes
    false,           // Arcs
    false,           // Drops
    true,            // Invisible       ← important
    false,           // Proximity arm
    false,           // Animates flame
    false,           // Has fuel
    true,            // No facing variation
    false,           // Inaccurate
    false,           // Translucent
    false,           // AA-capable
    0, 0,
    MPH_LIGHT_SPEED, // Speed
    0,               // ROT
    WARHEAD_HE,
    ANIM_PIFFPIFF);  // Impact
```

Key TD facts: invisible projectile (no visible bullet, just impact effect), MPH_LIGHT_SPEED (essentially hitscan), HE warhead, ANIM_PIFFPIFF impact ("piff piff" small puff).

### TD `WEAPON_TURRET_GUN` (TD `const.cpp:82`)

```cpp
{BULLET_APDS, 40, 60, 0x0600, VOC_TANK4, ANIM_MUZZLE_FLASH},  // WEAPON_TURRET_GUN
```

- Bullet: `BULLET_APDS` ("120mm")
- Damage: 40
- ROF: 60
- Range: 0x0600 / 256 = **6 cells**
- Sound: `VOC_TANK4` (= `TNKFIRE6`)
- Anim: `ANIM_MUZZLE_FLASH` (= `GUNFIRE` in RA's `adata.cpp:1075`)

### TD `BULLET_APDS` aka ClassAPDS (TD `bbdata.cpp:109`)

```cpp
static BulletTypeClass const ClassAPDS(BULLET_APDS,
    "120mm",         // Image
    false,           // High
    false,           // Homes
    false,           // Arcs
    false,           // Drops
    false,           // Invisible
    false,           // Proximity arm
    false,           // Animates flame
    false,           // Has fuel
    true,            // No facing variation
    false,           // Inaccurate
    false,           // Translucent
    false,           // AA-capable
    0, 0,
    MPH_VERY_FAST,   // Speed
    0,               // ROT
    WARHEAD_AP,
    ANIM_VEH_HIT3);  // Impact
```

Standard armor-piercing tank shell. Fast, no homing, no AA.

---

## Diff against current state

### TDGTWR — current state in our DLL + rules.ini

**`ClassTdGtwr` (`redalert/bdata.cpp:708-735`):**

| Field | Our value | TD value | Status |
|---|---|---|---|
| VerticalOffset | `0x0010` | `0x0030` (from Fire_Coord) | ⚠ DIVERGES |
| PrimaryOffset | `0x0040` | `0x0040` (from Fire_Coord) | match |
| PrimaryLateral | `0x0000` | — | OK |
| IsSimpleDamage | `true` | `true` | match |
| IsTurretEquipped | `false` | `false` | match |
| Initial facing | `DIR_N` | `DIR_N` | match |
| Size | `BSIZE_11` | `BSIZE_11` | match |
| Foundation | `List1` | `List1` | match |
| (IsCrew via rules.ini) | `Crewed=true` | `true` | match |

Only one constructor-arg bug: `VerticalOffset=0x0010` should be `0x0030`. With the wrong offset, bullets spawn ~0x20 leptons lower than they should — visible as muzzle coming from the building's *waist* rather than the top of the lookout structure. Not a fatal bug, but TD-inaccurate.

**`[TDGTWR]` rules.ini section (line 3452):**

```ini
[TDGTWR]
...
Armor=wood              ; ✓ TD ARMOR_WOOD
Primary=Vulcan          ; ⚠ RA's vanilla — wrong values
Strength=200            ; ✓ TD 200
Cost=500                ; ✓ TD 500
Power=-10               ; ✓ TD Drain=10
Sight=3                 ; ✓ TD 3
Crewed=true             ; ✓ TD IsCrew
```

The big one: `Primary=Vulcan`. RA's `[Vulcan]` weapon:

```ini
[Vulcan]
Damage=40        ; TD CHAIN_GUN = 25  (RA is 60% stronger)
ROF=40           ; TD CHAIN_GUN = 50  (RA fires 25% faster)
Range=5          ; TD CHAIN_GUN = 4   (RA reaches 1 cell further)
Projectile=Invisible
Speed=100        ; TD's MPH_LIGHT_SPEED is approx same magnitude
Warhead=SA       ; TD CHAIN_GUN = WARHEAD_HE
Report=GUN13     ; TD CHAIN_GUN = VOC_MINI ("GUN8")
Anim=MINIGUN     ; TD CHAIN_GUN = ANIM_GUN_N (8-direction overlay)
```

Every value differs. Net effect: our TDGTWR is **significantly stronger** than TD's authentic Guard Tower (40 dmg vs 25, 40 ROF vs 50, 5 range vs 4). For balance work later, that matters.

Plus the rules.ini comment at line 3467 explicitly admits the issue:
> `; Vulcan: same MG that PBOX donor used; TD's CHAIN_GUN closest analog.`

That's the donor-thinking we're retiring per [[feedback-no-donor-for-td-separation]].

### TDGUN — current state in our DLL + rules.ini

**`ClassTdGun` (`redalert/bdata.cpp:766-793`):**

| Field | Our value | TD value | Status |
|---|---|---|---|
| VerticalOffset | `0x0030` | `0x0030` (from Fire_Coord) | match |
| PrimaryOffset | `0x0080` | `0x0080` (from Fire_Coord) | match |
| PrimaryLateral | `0x0000` | — | OK |
| IsSimpleDamage | `false` | `false` | match |
| IsTurretEquipped | `true` | `true` | match |
| Initial facing | `(DirType)208` | `(DirType)208` | match |
| Size | `BSIZE_11` | `BSIZE_11` | match |
| Foundation | `List1` | `List1` | match |
| (IsCrew via rules.ini) | `Crewed=true` | `true` | match |

**`ClassTdGun` is field-perfect TD-authentic.** No constructor bugs.

**`[TDGUN]` rules.ini section (line 3665):**

```ini
[TDGUN]
...
Armor=steel             ; ✓ TD ARMOR_STEEL
Primary=TDTurretGun     ; ✓ TD-prefixed dedicated weapon
ROT=12                  ; ✓ TD's STRUCT_TURRET rotates at Rotation_Adjust(12)
Strength=200            ; ✓ TD 200
Cost=600                ; ✓ TD 600 (post-PATCH)
Power=-20               ; ✓ TD Drain=20
Sight=5                 ; ✓ TD 5
Crewed=true             ; ✓ TD IsCrew
```

**`[TDTurretGun]` weapon (line 2556):**

```ini
[TDTurretGun]
Damage=40              ; ✓ TD 40
ROF=60                 ; ✓ TD 60
Range=6                ; ✓ TD 0x0600 leptons = 6 cells
Projectile=Cannon      ; ⚠ RA's vanilla [Cannon] (Image=120MM only, all other fields default)
Speed=40               ; need to verify against TD MPH_VERY_FAST
Warhead=AP             ; ✓ TD WARHEAD_AP
Report=TNKFIRE6        ; ✓ TD VOC_TANK4
Anim=GUNFIRE           ; ✓ TD ANIM_MUZZLE_FLASH
```

The weapon stats are TD-authentic. The one separation issue: `Projectile=Cannon` — RA's vanilla `[Cannon]` section (`Image=120MM`, all defaults) happens to match TD's `BULLET_APDS` field-for-field, but binding to a *vanilla section* means RA-side balance changes to `[Cannon]` (used by RA's tanks/turret) would silently move TDGUN too. Per the separation principle, we want our own `[TDAPDS]` section even if its content is currently identical.

---

## Audio routing status

| TD VocType | TD sample | RA mapping | Used by |
|---|---|---|---|
| `VOC_MINI` | `GUN8` | **MISSING** — needs to add `{"GUN8", 1, IN_NOVAR},  // VOC_TD_MINI` | TDGTWR's TDChainGun |
| `VOC_TANK4` | `TNKFIRE6` | `VOC_TD_TANK4` (`audio.cpp:254`) | TDGUN's TDTurretGun ✓ |
| `VOC_ROCKET2` | `ROCKET2` | `VOC_TD_ROCKET2` (`audio.cpp:253`) | TDSAM (TDNike), TDATWR (TDTowTwo) ✓ |
| `VOC_LASER` | `OBELRAY1` | `VOC_TD_LASER` (`audio.cpp:255`) | TDOBLI ✓ |
| `VOC_LASER_POWER` | `OBELPOWR` | `VOC_TD_LASER_POWER` (`audio.cpp:256`) | TDOBLI ✓ |
| `VOC_CONSTRUCTION` | `CONSTRU2` | `VOC_TD_CONSTRUCTION` (`audio.cpp:257`) | (TD building loop) ✓ |

Add `GUN8` to `audio.cpp` `SoundEffectName[]` table (one line, slots into the existing TF-mod block). Same routing pattern we've already used six times.

---

## Port plan

### TDGTWR

**T1 — Fix `ClassTdGtwr` VerticalOffset** (`redalert/bdata.cpp:714`):

```cpp
0x0030,          // VerticalOffset — TD ClassGTower (Fire_Coord +0x30 DIR_N)
0x0040,          // PrimaryOffset — TD ClassGTower (Fire_Coord +0x40 forward)
```

Update the comment to drop "matches PBOX" — we set this from TD source, not by comparing to PBOX.

**T2 — Add `VOC_TD_MINI` audio entry** (`redalert/audio.cpp:257`-ish, slot into the TF block):

```cpp
{"GUN8",    1, IN_NOVAR},  // VOC_TD_MINI         TD chain gun burst (CHAIN_GUN / TDGTWR)
```

**T3 — Port `[TDSpreadfire]` projectile** to `rules.ini`:

```ini
; TD BULLET_SPREADFIRE — "50cal" invisible bullet trail.
; Source: tiberiandawn/bbdata.cpp ClassSpreadfire at line 87.
; Distinct from RA's [Invisible] which is bare (no fields beyond Inviso=yes
; Image=none); TD's BULLET_SPREADFIRE has a specific impact anim and
; warhead routing handled by the bullet, not the weapon.
[TDSpreadfire]
Image=50cal      ; TD says "50cal" — verify Remaster has this sprite, fall back to "none" if not
Inviso=yes       ; TD Invisible=true
High=yes         ; TD High=true (over walls)
; Homes=no, Arcs=no, Proximity=no, Animates=no, Ranged=no — all defaults
; AA=no by default
; ROT=0 by default
; Translucent=no
```

**T4 — Port `[TDChainGun]` weapon** to `rules.ini` (slot near `[TDTurretGun]`):

```ini
; TD GDI Guard Tower chain gun.
; Source: tiberiandawn/const.cpp WEAPON_CHAIN_GUN
;   {BULLET_SPREADFIRE, 25, 50, 0x0400, VOC_MINI, ANIM_GUN_N}
; NOT aliased to RA's [Vulcan] — RA's has Damage=40 ROF=40 Range=5 (way
; stronger). TD-authentic stats below are required for balance work.
[TDChainGun]
Damage=25              ; TD Attack=25  (RA's [Vulcan] = 40)
ROF=50                 ; TD ROF=50     (RA's [Vulcan] = 40)
Range=4                ; TD Range=0x0400 leptons = 4 cells (RA's [Vulcan] = 5)
Projectile=TDSpreadfire
Speed=100              ; TD's MPH_LIGHT_SPEED — verify exact integer
Warhead=HE             ; TD WARHEAD_HE (RA's [Vulcan] = SA)
Report=GUN8            ; TD VOC_MINI (RA's [Vulcan] = GUN13)
Anim=GUNFIRE           ; ANIM_GUN_N would be the more authentic choice but
                       ; RA's adata.cpp already maps GUNFIRE to ANIM_MUZZLE_FLASH;
                       ; the 8-direction ANIM_GUN_N path resolves via the
                       ; case-match at techno.cpp:3388 if we point Anim
                       ; at one of the directional Gun_N animation names —
                       ; verify in implementation. Either works visually.
```

**T5 — Update `[TDGTWR]` to bind the TD weapon**:

```ini
[TDGTWR]
; ... other fields unchanged ...
Primary=TDChainGun     ; was: Primary=Vulcan
; Drop the "Vulcan: same MG that PBOX donor used; TD's CHAIN_GUN closest
; analog" comment — no longer relevant under full separation.
```

**T6 — Manifest sync** (`scripts/buildings_manifest.py`):

Update the `TDGTWR` dict's `"primary"` field to `"TDChainGun"` and update notes to reference this doc.

### TDGUN

TDGUN's weapon stats are already TD-authentic. Two small cleanups:

**T7 — Port `[TDAPDS]` projectile** to `rules.ini`:

```ini
; TD BULLET_APDS — armor-piercing 120mm shell.
; Source: tiberiandawn/bbdata.cpp ClassAPDS at line 109.
; Currently TDTurretGun.Projectile=Cannon which is RA's vanilla bullet
; (Image=120MM only, all defaults — happens to match TD's BULLET_APDS
; field-for-field but binds us to RA's balance pool). Port to a TD-prefixed
; section even though content is value-identical so future RA balance
; changes to [Cannon] don't silently move TDGUN.
[TDAPDS]
Image=120mm
; All other fields default — matches TD ClassAPDS field-for-field:
;   High=no, Homes=no, Arcs=no, Invisible=no, Proximity=no, Animates=no,
;   Ranged=no, Inaccurate=no, Translucent=no, AA=no, ROT=0
```

**T8 — Update `[TDTurretGun]` to bind the TD projectile**:

```ini
[TDTurretGun]
; ... other fields unchanged ...
Projectile=TDAPDS      ; was: Projectile=Cannon
```

Update the comment at line 2555 (`; BULLET_APDS ≈ RA's Cannon visually; no new BulletType needed.`) — that's the same donor-think; replace with a pointer to this doc.

**T9 — Verify `Speed=40` matches TD's `MPH_VERY_FAST`**:

TD's BULLET_APDS uses MPH_VERY_FAST. RA's `Speed=` integer for that enum needs verification — pick an existing RA weapon firing a fast-tank-shell projectile (e.g. RA's heavy tank `[90mm]`) and check what Speed value it uses. If 40 matches, we're good. If not, adjust.

---

## What's already right (don't touch)

- `STRUCT_TDGTWR` and `STRUCT_TDGUN` enums in `defines.h`, heap registration in `bdata.cpp:3322,3324`.
- `ClassTdGun` constructor args — 100% TD-authentic to TD's `ClassTurret`.
- `[TDGUN]` rules.ini fields — all match TD's `ClassTurret`.
- `[TDTurretGun]` weapon Damage/ROF/Range/Warhead/Report/Anim — all match TD's `WEAPON_TURRET_GUN`.
- `TDGTWR.ZIP` (3 frames) — correct for `IsSimpleDamage=true`.
- `TDGUN.ZIP` (128 frames = 32 rotation × 4 states) — correct for `IsTurretEquipped=true`.
- TDGUN audio: `Report=TNKFIRE6` already wired via `VOC_TD_TANK4` in `audio.cpp:254`.
- TDGUN rotation: `Rotation_AI` already rotates at `Class->ROT` when `IsTurretEquipped=true` and powered — TDGUN's `ROT=12` matches TD's `Rotation_Adjust(12)`.

---

## Acceptance criteria

**TDGTWR:**
- [ ] `ClassTdGtwr.VerticalOffset = 0x0030` (was `0x0010`).
- [ ] `[TDChainGun]` weapon section in rules.ini with TD-authentic Damage=25/ROF=50/Range=4/Warhead=HE.
- [ ] `[TDSpreadfire]` projectile section in rules.ini matching TD's `BULLET_SPREADFIRE`.
- [ ] `[TDGTWR] Primary=TDChainGun` (was `Primary=Vulcan`).
- [ ] `VOC_TD_MINI = "GUN8"` in `redalert/audio.cpp`.
- [ ] Firing audio is the TD-authentic minigun sound (not RA's GUN13).
- [ ] Per-shot damage on light infantry is consistent with TD's 25-per-shot (vs RA's 40).
- [ ] All "Vulcan: same MG that PBOX donor used" / "modeled on PBOX" comments removed or pointed at this doc.

**TDGUN:**
- [ ] `[TDAPDS]` projectile section in rules.ini.
- [ ] `[TDTurretGun] Projectile=TDAPDS` (was `Projectile=Cannon`).
- [ ] `Speed=40` verified against TD's `MPH_VERY_FAST` (adjust if needed).
- [ ] Firing audio is `TNKFIRE6` (already correct; regression check only).
- [ ] Damage per shot vs medium tank: TD-authentic 40 damage with WARHEAD_AP (verify against vanilla TD if possible).

---

## Decisions

- **No donor framing.** Every value in this plan comes from TD source, not "what RA building has the same shape."
- **`[TDChainGun]`/`[TDSpreadfire]`/`[TDAPDS]` are new TD-port sections.** Not aliased to RA's `[Vulcan]`/`[Invisible]`/`[Cannon]`. Per [[feedback-no-donor-for-td-separation]] / [[project-building-separation-committed]].
- **TDGTWR uses TD-authentic stats even though they make it weaker than the current Vulcan-shaped version.** Per [[feedback-difficulty-philosophy]] — don't preserve a balance-buff just because it leaked in via a donor binding. If the building feels too weak in playtest, balance via TD-authentic levers (range, ROF, even a `Strength=` bump on the building) rather than reverting to a non-TD weapon.
- **TDGUN keeps the current Cannon-equivalent projectile values.** The new `[TDAPDS]` section starts as content-identical to `[Cannon]` because TD's `BULLET_APDS` happens to match RA's defaults. The point of porting it isn't to change behavior, it's to decouple TDGUN from RA's vanilla balance pool so they can drift independently.

---

## Cargo order

Three independent commit shapes:

**Smallest (TDGUN polish only):** T7 + T8 (port `[TDAPDS]`, rebind `[TDTurretGun]`). Zero behavioral change, only the projectile section name. Safe to ship anytime.

**Medium (TDGTWR weapon port):** T1 + T2 + T3 + T4 + T5 + T6 (offset fix + audio entry + weapon/projectile port + binding update + manifest). Will measurably change TDGTWR's combat output. Pair with a quick skirmish smoke test before push.

**Optional (T9):** Speed verification for TDTurretGun. Probably no-op (40 is right) but worth confirming.

Both TDGTWR and TDGUN cargos are independent of the TDSAM and TDATWR work in the parallel deep-dive docs.

---

## Cross-reference

- TDSAM: `td-sam-deep-dive.md` / `docs/td-sam-deep-dive.md`
- TDATWR: `td-atwr-deep-dive.md` / `docs/td-atwr-deep-dive.md`
- TDOBLI: already-validated TD-port (uses `[TDOblsLaser]` weapon, no shared RA bindings) — keep as reference template for what "fully separated, all TD-prefixed" looks like.
