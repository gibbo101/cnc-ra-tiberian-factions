# Weapon, bullet, sound, and anim ports — future task

> ⚠️ **PLANNING SUMMARY — NOT THE SPEC.** This doc has errors (it lists E1's weapon as RIFLE — actually `WEAPON_M16`; the Commando as M16 — actually `WEAPON_RIFLE`, a 125-dmg sniper). Before porting ANY weapon, verify it from `tiberiandawn/const.cpp` `Weapons[]` + the unit's `idata.cpp`/`udata.cpp` ctor and do a full value-by-value comparison vs the RA equivalent (see `docs/td-port-playbook.md` §2.1). Use this doc for *which* ports remain — never for the stats.

Catalogue of TD content that depends on engine assets RA doesn't have. Lists what's missing, who needs it (buildings vs units), and the per-weapon scope so we can plan dedicated phases without blocking catalogue rollout.

> **STATUS: all listed weapon/bullet/anim ports SHIPPED (v1.0–v2.0).** Every TD unit and building now binds its own TD-authentic weapon chain (see the per-entity verification docs + `weapon-ports` references in the playbook). This doc is now a **historical mapping of which ports remained as of 2026-05-19** — useful for tracing the arc, never for stats (see the warning above).

**Status as of 2026-05-19 (historical):** scoped, not started. v0.3 catalogue uses placeholder RA weapons for the five defensive buildings (see `docs/catalogue.md` master wiring table). Units (v0.4+) will need most of these before any TD-flavoured infantry/vehicle work begins.

---

## 1. Weapon-enum side-by-side

Source: `tiberiandawn/defines.h:1876-1906`, `redalert/defines.h:2685-2743`.

| TD weapon (`WEAPON_*`) | Exists in RA? | RA equivalent (if any) | Used by (TD) |
|---|---|---|---|
| RIFLE | ✅ | RIFLE | E1 Minigunner |
| CHAIN_GUN | ✅ | CHAIN_GUN | GTWR, Apache, JEEP, BGGY |
| PISTOL | ✅ | PISTOL | (officer variants) |
| M16 | ✅ | M16 | Commando |
| DRAGON | ✅ | DRAGON | E3 Rocket infantry |
| FLAMETHROWER | ⚠️ similar | FLAMER (different damage curve) | E4 Flamethrower infantry |
| FLAME_TONGUE | ⚠️ similar | FLAMER (different range) | Flame Tank turret |
| CHEMSPRAY | ❌ port | — (no analog) | Chemical Warrior, Chemical Mobile |
| GRENADE | ✅ | GRENADE | E2 Grenadier |
| 75MM | ✅ | 75MM | Light Tank |
| 105MM | ✅ | 105MM | Medium Tank |
| 120MM | ✅ | 120MM | Mammoth Tank primary |
| TURRET_GUN | ✅ | TURRET_GUN | GUN (defensive turret) |
| MAMMOTH_TUSK | ✅ | MAMMOTH_TUSK | Mammoth secondary |
| MLRS | ❌ port | — (RA SCUD is closest behaviour) | MLRS, MSAM units |
| 155MM | ✅ | 155MM | Artillery |
| M60MG | ✅ | M60MG | Various |
| TOMAHAWK | ❌ port | — (Hellfire is closest) | Stealth Tank |
| TOW_TWO | ❌ port | — (Hellfire is closest) | **TDATWR** (this catalogue) |
| NAPALM | ✅ | NAPALM | A-10, Orca |
| OBELISK_LASER | ❌ port | — (no laser weapon in RA) | **TDOBLI** (this catalogue) |
| NIKE | ✅ | NIKE | **TDSAM** (this catalogue) |
| HONEST_JOHN | ❌ port | — (SCUD is closest behaviour) | Rocket Launcher (MSAM variant) |
| STEG | ❌ skip | — | Stegosaurus (TD multiplayer easter-egg) |
| TREX | ❌ skip | — | T-Rex (TD multiplayer easter-egg) |

**Reverse direction** — RA-exclusive weapons that have no TD use case: COLT45, ACK_ACK, VULCAN, MAVERICK, CAMERA, FIREBALL, HELLFIRE, 90MM, TESLA_ZAP, 8INCH, STINGER, TORPEDO, 2INCH, DEPTH_CHARGE, PARA_BOMB, DOGJAW, HEAL, SCUD, REDEYE, MANDIBLE, PORTATESLA, GOODWRENCH, SUBSCUD, TTANKZAP, APTUSK, DEMOCHARGE, CARRIER. These are available to *us* as donor analogs but don't need porting.

---

## 2. Per-weapon port scope

Each port needs **six pieces**. None of them are blocked by anything else; each weapon can be added in its own commit.

| # | Component | RA file | What we copy from TD |
|---|---|---|---|
| 1 | `WeaponType` enum entry | `redalert/defines.h` | One enum line + bump `WEAPON_COUNT` |
| 2 | `WeaponTypeClass` static const | `redalert/wpndata.cpp`† | TD class init: BulletType, Attack, Range, Speed, Sound, Anim |
| 3 | `WarheadType` (if unique) | `redalert/whdata.cpp`† | TD warhead: Spread, Verses%, Explosion, InfDeath |
| 4 | `BulletType` + class | `redalert/budata.cpp`† | TD bullet: art, speed, arcing, AA-capable, ROT |
| 5 | Sound entry (`VOC_*`) | `redalert/audio.cpp` + `.AUD` file | TD assets ship the AUD in CONFIG.MEG / SOUNDS.MIX |
| 6 | Anim entry (`ANIM_*`) | `redalert/anim.cpp` + `.SHP` file | TD assets ship the SHP in CONQUER.MIX / CONFIG.MEG |

† RA's actual file structure — check `redalert/CMakeLists.txt`'s SOURCES list for the canonical name; the source tree may have these merged into a different .cpp. Either way the const tables live alongside `bdata.cpp`'s pattern.

The grep that shows TD's bindings (run `grep "WEAPON_" tiberiandawn/const.cpp | head -30` for the full list):

```cpp
// tiberiandawn/const.cpp — TD's weapon→bullet/sound/anim binding table
{BULLET_FLAME,       35,  50, 0x0200, VOC_FLAMER1, ANIM_FLAME_N},   // WEAPON_FLAMETHROWER
{BULLET_FLAME,       50,  50, 0x0200, VOC_FLAMER1, ANIM_FLAME_N},   // WEAPON_FLAME_TONGUE
{BULLET_CHEMSPRAY,   80,  70, 0x0200, VOC_FLAMER1, ANIM_CHEM_N},    // WEAPON_CHEMSPRAY
{BULLET_SSM2,        75,  80, 0x0600, VOC_ROCKET1, ANIM_NONE},      // WEAPON_MLRS
{BULLET_SSM,         60,  35, 0x0780, VOC_ROCKET2, ANIM_NONE},      // WEAPON_TOMAHAWK
{BULLET_SSM,         60,  40, 0x0680, VOC_ROCKET2, ANIM_NONE},      // WEAPON_TOW_TWO
{BULLET_LASER,       200, 90, 0x0780, VOC_LASER,   ANIM_NONE},      // WEAPON_OBELISK_LASER
{BULLET_HONEST_JOHN, 100, 200,0x0A00, VOC_ROCKET1, ANIM_NONE},      // WEAPON_HONEST_JOHN
```

**Sounds we need to add** (none of these exist in RA):
- `VOC_FLAMER1` — flamethrower whoosh (used by FLAMETHROWER, FLAME_TONGUE, CHEMSPRAY)
- `VOC_ROCKET1` — heavier missile launch (MLRS, HONEST_JOHN)
- `VOC_ROCKET2` — lighter missile launch (TOMAHAWK, TOW_TWO)
- `VOC_LASER` — Obelisk beam (OBELISK_LASER)

**Bullets we need to add** (RA has only `BULLET_LASER_GUIDED`, which is the Cruiser's Maverick — not a beam):
- `BULLET_FLAME` — flamethrower stream
- `BULLET_CHEMSPRAY` — chem spray (visually distinct from BULLET_FLAME)
- `BULLET_SSM` — surface-to-surface missile (TOMAHAWK/TOW_TWO share this)
- `BULLET_SSM2` — heavier SSM (MLRS)
- `BULLET_LASER` — Obelisk's instant-hit beam
- `BULLET_HONEST_JOHN` — Honest John tactical rocket

**Anims we need to add** (muzzle-flash / impact frames; RA has none of these):
- `ANIM_FLAME_N` — flame muzzle (8-directional)
- `ANIM_CHEM_N` — chem muzzle (8-directional)

---

## 3. v0.3 placeholder choices (what we're shipping right now)

| TD intent | TD weapon | v0.3 placeholder | Why |
|---|---|---|---|
| GTWR — anti-infantry chaingun | CHAIN_GUN | `Primary=Vulcan` | RA Vulcan is anti-infantry rapid-fire. Close enough that no port is needed. |
| ATWR — anti-armor + AA | TOW_TWO | `Primary=TurretGun, Secondary=Nike` | Dual-slot trick: TurretGun handles ground armor, Nike handles air. Engine dispatches per target type. **No projectile-visual mismatch** — both weapons exist visually as missile/cannon, which fits a "missile tower" silhouette better than ZSU-23. |
| OBLI — laser beam | OBELISK_LASER | `Primary=HellFire` | HellFire is RA's heavy anti-armor missile (Longbow's payload). Slow ROF, high damage matches Obelisk's feel. **Visual mismatch acknowledged** — Obelisk should be a beam, not a missile. The proper port replaces this entry first. |
| GUN — anti-armor turret | TURRET_GUN | `Primary=TurretGun` | Same weapon name in both engines. Zero-port mapping. |
| SAM — AA missile | NIKE | `Primary=Nike` | Same weapon name. Zero-port. |

---

## 4. Priority order for the port phase (proposed)

Group by "buildings vs units" and within each, by impact-per-effort:

### Phase W1 — Building-critical (unblocks final TD-faithful defensive layer)

1. **OBELISK_LASER** — Obelisk doesn't *feel* right without a beam. Biggest visible mismatch in the current catalogue. Includes BULLET_LASER + VOC_LASER.
2. **TOW_TWO** — Replaces ATWR's dual-slot placeholder with the authentic single-weapon dual-role. Includes BULLET_SSM + VOC_ROCKET2.

### Phase W2 — Infantry-critical (unblocks E4 Flamethrower, E5 Chemical Warrior)

3. **FLAMETHROWER** — TD's E4 flamethrower infantry. Note: RA's `FLAMER` weapon may be a close enough match to skip this; investigate damage/range deltas first. Includes BULLET_FLAME + VOC_FLAMER1 + ANIM_FLAME_N.
4. **FLAME_TONGUE** — Flame Tank turret. Likely shares assets with FLAMETHROWER once it's in, so a small additional cost on top of W3.
5. **CHEMSPRAY** — Chemical Warrior + Chemical Mobile. Distinct visual (green spray), so BULLET_CHEMSPRAY + ANIM_CHEM_N needed separately. Reuses VOC_FLAMER1.

### Phase W3 — Vehicle-critical (unblocks MLRS, Stealth Tank, Rocket Launcher)

6. **MLRS** — MLRS unit's rapid-fire rockets. Includes BULLET_SSM2 + VOC_ROCKET1.
7. **TOMAHAWK** — Stealth Tank's primary. Reuses BULLET_SSM + VOC_ROCKET2 from W2 (TOW_TWO port).
8. **HONEST_JOHN** — Tactical rocket launcher unit. Includes BULLET_HONEST_JOHN + VOC_ROCKET1.

### Skipped (no port needed)

- **STEG / TREX** — TD-only multiplayer easter-egg dinosaur units. Out of scope unless we explicitly want them.

---

## 5. Sourcing the assets

All TD AUD / SHP files we need live in two MIX archives shipped by C&C Remastered:

- `~/.steam/steam/steamapps/common/CnCRemastered/Data/CONFIG.MEG` — extract via `scripts/meg_extract.py`
- TD-Assets workshop mod (`steamcommunity.com/sharedfiles/filedetails/?id=3003163891`) — already a dependency for sprite work

The actual game-side load is via `MIXFileClass` registration during init — same path the existing RA weapons already use. No new loader code; just register the new asset names in the audio/anim tables.

---

## 6. When to do this

**After v0.3 (building catalogue complete).** Building rollout currently uses placeholders that *work* — the AI shoots, the buildings function as defensive structures, balance is roughly in the right zone. The visual/audio mismatch is the only real downside.

**Trigger to start Phase W1:** when playtest feedback specifically calls out "the Obelisk looks wrong" or "TDATWR feels weak vs tanks." Until then, ship the catalogue.

**Trigger to start W2/W3:** when we begin work on the TD-flavoured infantry and vehicle catalogue. Those phases will hit a hard wall without these weapons; better to port them as the unit work begins than retroactively.

---

## 7. Related notes

- The script (`scripts/add_building.py`) is **weapon-agnostic** — it just emits whatever `Primary=`/`Secondary=` the manifest specifies. Switching from placeholder to ported weapon is a single line in the manifest, no script change.
- `Logic=` aliasing in `bdata.cpp:3731-3759` doesn't copy `PrimaryWeapon`/`SecondaryWeapon` from the donor — same mandatory-INI-field gotcha as `Points=`. See `docs/ai-targeting.md` for the inheritance pattern and `docs/adding-td-buildings.md` lesson #5 for the analogous gotcha class.
- See `docs/catalogue.md` "TD weapon → RA placeholder analogs" table for the current v0.3 placeholder choices; this doc is the authoritative future-plan, that table is the authoritative current-state.
