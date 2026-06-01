# TD Rocket Launcher (MLRS) — deep dive

**Status:** research complete, **no code yet** (2026-06-01). Read alongside `td-vehicle-port-recipe.md`.
This one needed a deep dive because TD's `UNIT_MLRS` / `UNIT_MSAM` have **cross-wired graphics** and a
surprising tech gate. This doc untangles it and sets the port plan.

---

## 1. The cross-wiring (the trap)

TD source defines **two** rocket-artillery vehicles whose *graphic names are swapped* relative to their
enum names. Display names (TXT) and weapons are coherent; only the sprite assignment is crossed:

| | `UNIT_MLRS` (udata.cpp:854) | `UNIT_MSAM` (udata.cpp:477) |
|---|---|---|
| **Display name** | `TXT_MLRS` = **"Rocket Launcher"** | `TXT_MSAM` = **"S.S.M. Launcher"** |
| **Sprite (graphic name)** | **`"MSAM"`** ← crossed | **`"MLRS"`** ← crossed |
| **Weapon** | `WEAPON_MLRS` → `BULLET_SSM2` | `WEAPON_HONEST_JOHN` → `BULLET_HONEST_JOHN` |
| **Prerequisite** | `STRUCTF_EYE` (GDI Ion-Cannon comm) | `STRUCTF_ATOWER` (Adv. Guard Tower) |
| **Ownable (source bits)** | `GOOD｜BAD` (both) | `BAD` only (GOOD commented out) |
| **Death explosion** | `ANIM_ART_EXP1` | `ANIM_FRAG2` |
| **Turret / lock-while-moving** | yes / yes | yes / yes |
| **Two-shooter** | **yes** | no |
| **Strength / Cost / Sight** | 100 / 800 / 4 | 120 / 750 / 4 |
| **Speed / Armor / Locomotion** | MPH_MEDIUM / ALUMINUM / TRACK | MPH_MEDIUM / ALUMINUM / TRACK |
| **Build level** | 7 | 7 |

**This doc is about the "Rocket Launcher" = `UNIT_MLRS`** (the one Luke asked for). The "S.S.M. Launcher"
(`UNIT_MSAM`, Honest John, Nod) is a *separate* future port — documented here only for disambiguation.

**Port identity:** our unit = `UNIT_TDMLRS`, IniName `TDMLRS`, rules.ini `Name=Rocket Launcher`, but the
**bundled sprite is the `MSAM` asset** (`MSAM.SHP` / `MSAM.ZIP`) — because that's what TD's Rocket Launcher
actually renders with. (When we later port the SSM Launcher, it bundles the `MLRS` sprite. Don't let the
names fool you.)

---

## 2. Faction: GDI (despite both ownable bits)

Source sets both `HOUSEF_GOOD｜HOUSEF_BAD`, but the **prerequisite is `STRUCTF_EYE`** — the GDI Advanced
Comm Center / Ion Cannon host (our `TDEYE`, GDI-only). **Only GDI can ever build it**, so it is effectively
a GDI unit. Recommendation: `Owner=GoodGuy` (GDI), consistent with the APC precedent (canon/prereq over
permissive source bits). This also balances the artillery roster: GDI = Rocket Launcher, Nod = Artillery +
SSM Launcher.

**It's a TOP-TIER unit.** Build level 7 + `STRUCTF_EYE` means the Rocket Launcher unlocks only **after the
Ion Cannon building** — a deliberate late-game GDI siege unit in TD. Honor it: `Prerequisite=weap,atek`
(`weap` = GDI war factory `TDWEAP`; `atek` is satisfied by `TDEYE` via the `house.cpp` remap — and since the
unit is GDI-only, `atek`→`TDEYE` is the effective gate). Flag for Luke: confirm we want it gated this high,
or drop the EYE gate to make it a mid-tier unit.

---

## 3. Weapon + bullet

**`WEAPON_MLRS`** (`const.cpp:84`): `{BULLET_SSM2, dmg 75, ROF 80, range 0x0600=6, VOC_ROCKET1, ANIM_NONE}`
— a long-range (6 cells) homing rocket, no muzzle anim. **New weapon** `WEAPON_TDMLRS` /
`[TDMLRS]` (non-trivial: range 6 is longer than any shipped TD rocket). `Burst=2` (TD `is_twoshooter`).
Report `ROCKET1` = **already shipped** (`VOC_TD_ROCKET1`, Mammoth Tusk; `RAC/RAR_SFX_ROCKET1` already routed)
→ reuse, no new sound.

**`BULLET_SSM2`** (`ClassMissile2`, bbdata.cpp:175): sprite `"DRAGON"`, homing, **AA-capable**, near-detonate,
flickering flame, runs-out-of-fuel, inaccurate, translucent, `ARMING 9`, `ROT 7`, `MPH_ROCKET`, `WARHEAD_HE`,
`ANIM_FRAG1`.

**Bullet reuse decision (the one real fidelity call):** we already ship **`TDSSM`** = the `BULLET_SSM` port
(`ClassMissile`): identical to `SSM2` *except* `ARMING 7` (vs 9) and `ROT 5` (vs 7). Everything else byte-matches
(DRAGON sprite, homing, AA, `WARHEAD_HE`/`TDHE`, `ANIM_FRAG1`, MPH_ROCKET, inaccurate, translucent).
- **Option A — reuse `TDSSM`** (Tusk/Guard-Tower precedent). Pro: zero new bullet surface. Con: not byte-identical
  (arm/ROT delta → the missile arms ~0.06s sooner and turns slightly slower). Borderline vs the "reuse only
  byte-identical TD→TD" rule (`[[feedback-ra-only-when-no-alternative]]`).
- **Option B — port `BULLET_SSM2` as `TDSSM2`** (RECOMMENDED): a trivial clone of the `TDSSM` rules section
  with `Arm=9` / `ROT=7`. Fidelity-correct; the established convention favors porting over near-reuse. New
  `BULLET_TDSSM2` enum + `bbdata.cpp` registration + donor-ImageData (shares the `TDDRAGON` sprite, already
  bundled — no new asset).

Either way the weapon's `Warhead=TDHE` (the TD `WARHEAD_HE` port, already shipped).

**Chain audit (Option B):**
```
Primary=TDMLRS              [NEW weapon: dmg75/ROF80/range6/Burst=2/Report=ROCKET1]
  Projectile=TDSSM2         [NEW bullet = TDSSM + Arm9/ROT7; shares TDDRAGON sprite]
  Warhead=TDHE              [shipped ✓]
  Report=ROCKET1            [shipped ✓ VOC_TD_ROCKET1]
Explosion=ANIM_ART_EXP1     [RA-native ✓]
```

---

## 4. Assets — the 96-frame sprite trap

`MSAM.ZIP` (the Rocket Launcher's sprite) is **96 frames** — not the usual 64 (body 32 + turret 32). Likely
body(32) + turret(32) + a third 32-frame layer (raised/firing launcher elevation; fits `IsLockTurret` +
the "deploys to fire" feel). **No RA *vehicle* tileset has ≥96 frames** (max is V2RL=80), so the usual
`--tileset-donor <vehicle>` slice won't reach 96.

Options (resolve at implementation):
1. **Slice a 660-frame infantry block** (`E2`/`TDE4`) down to 96 via the bundler's `frame_count` slicer — the
   donor's internal structure is irrelevant (the bundler re-points every path to `tdmlrs\` and Shape-orders
   0..95). Cleanest if it works.
2. **Hand-generate a 96-entry tileset block** (Shape 0..95 → `tdmlrs-0000..0095`) if the slicer balks.
3. **Verify 64 suffices first** — if the launcher only references body+turret (0..63) for a turreted unit and
   the 64..95 frames are an unused/special state, a 64-frame map may render fine. Test before assuming 96.

Classic SHP: `MSAM.SHP` (CONQUER.MIX, 19563 bytes) → `build_tfassets.sh` `MSAM.SHP:TDMLRS.SHP`.
HD: `bundle_unit.py MSAM TDMLRS --tileset-donor <TBD> --build-icon BuildIcon_TD_RocketLauncher
--text-name TEXT_UNIT_TITLE_GDI_ROCKET_LAUNCHER --text-desc ...` (cameo `BuildIcon_TD_RocketLauncher`
confirmed present in the base PAK).

---

## 5. Ctor mapping (UNIT_TDMLRS)

Mirror a turreted-tank ctor (e.g. `UnitTdMtnk`) with: turret = **true** (`is_turret_equipped`),
**lock-turret-while-moving = true** (RA ctor param — the launcher locks forward when moving),
squash = false, crusher = false, gigundo = false, `ANIM_ART_EXP1` death, 32 rotation stages,
`MISSION_GUARD` default order (TD `UnitMLRS` uses GUARD, not HUNT). Weapon-offset geometry: screenshot-tune
against the MSAM turret like the Medium Tank (no TD value for the muzzle offset).

rules.ini `[TDMLRS]`: `Image=TDMLRS`, `ShapeSize=48,48`, `Name=Rocket Launcher`, `Primary=TDMLRS`,
`Tracked=yes`, `Strength=100`, `Armor=light`, `TechLevel=7`, `Sight=4`, `Speed=7` (`MPH_MEDIUM=18` →
`round(18×100/256)`), `Owner=GoodGuy`, `Cost=800`, `Points=72`, `ROT=5`, `Crewed=yes`,
`Prerequisite=weap,atek`.

---

## 6. Open decisions for Luke

1. **Faction** — GDI-only (recommended, EYE-gated) ✔ confirm.
2. **Tech tier** — honor TD's `STRUCTF_EYE` (Ion-Cannon-gated, very late) or drop to a lower prereq for accessibility?
3. **Bullet** — port `TDSSM2` for exactness (recommended) vs reuse `TDSSM`.
4. **96-frame sprite** — accept the infantry-donor-slice approach, pending the "does 64 suffice" test.
