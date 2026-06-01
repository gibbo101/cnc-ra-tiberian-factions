# TD attack helicopters — Apache (Nod) + Orca (GDI) deep dive

**Status:** TD logic examined (2026-06-01), no code yet. The last two TD combat units. Read with
`td-vehicle-port-recipe.md` and `project-chinook-pure-ra` (the aircraft-sprite-geometry caveat).

---

## 1. The two units (TD source)

| | Apache (`AIRCRAFT_HELICOPTER`, "HELI") | Orca (`AIRCRAFT_ORCA`, "ORCA") |
|---|---|---|
| Display | TXT_HELI = "Apache" | TXT_ORCA = "Orca" |
| Faction | **Nod** (HOUSEF_BAD) | **GDI** (HOUSEF_GOOD) |
| Weapon | `WEAPON_CHAIN_GUN` | `WEAPON_DRAGON` |
| **Rotor** | **yes** (single, not custom) | **NO** (VTOL jets — `is_rotorequipped=false`) |
| Two-shooter (fires a pair) | **yes** | **yes** |
| Ammo | 15 | 6 |
| Strength / Cost | 125 / 1200 | 125 / 1200 |
| Armor / Speed / ROT | STEEL / MPH_FAST / 4 | STEEL / MPH_FAST / 4 |
| Build level / prereq | 6 / Helipad | 6 / Helipad |
| Land on clear terrain | no (returns to helipad) | no |

**Weapons are BOTH already shipped:**
- `WEAPON_CHAIN_GUN` = `{BULLET_SPREADFIRE, 25, 50, range 4, VOC_MINI, ANIM_GUN_N}` = our **`TDChainGun`**
  (the Guard Tower's; exact match) firing `TDSpreadfire`.
- `WEAPON_DRAGON` = `{BULLET_TOW, 30, 60, range 4, VOC_BAZOOKA}` = our **`TDDragon`** (E3/Bike's) firing `TDTOW`.

**Two-shooter handling:** TD's `is_twoshooter` → RA `Burst=2` on the weapon. Both shared weapons are
single-shot (GTWR's TDChainGun, E3/Bike's TDDragon have no Burst), so each attack heli needs a
**Burst=2 variant**:
- Apache → NEW `TDApacheGun` = TDChainGun + Burst=2.
- Orca → **reuse the existing `TDStnkDragon`** (the Stealth Tank's TDDragon+Burst=2 — same WEAPON_DRAGON
  two-shot). No new weapon for the Orca.

---

## 2. The attack-heli LOGIC — RA's is generic, reuse it

The TD attack-heli behavior is: fly to target → strafe (fire pairs) → when `Ammo` runs out, fly back to
a helipad (`MISSION_ENTER`) → reload → repeat. **RA's `AircraftClass` already implements all of this and
it is essentially type-agnostic** (`redalert/aircraft.cpp`): `Ammo`/`MaxAmmo` (init 254), `MISSION_ATTACK`,
`MISSION_ENTER` reload-at-helipad (lines 2022/2260/2374), `Good_Fire_Location` (strafe positioning),
`Pip_Count` (ammo pips). The **only** type-gate in the whole file is one cosmetic `AIRCRAFT_HIND` speed
check (line 436). So we get the attack-heli AI **for free** by setting the unit up like RA's HIND —
no `_TD()` port needed (unlike the ground units' missions).

**RA's HIND is the template** (`aadata.cpp` `OrcaHeli`=AIRCRAFT_HIND): `is_rotor=true`, not custom-rotor,
not land-clear, `STRUCT_HELIPAD` preferred-landing, `primaryoffset=0x0040` (chain-gun muzzle), 32 stages.
`[HIND]` rules: `Primary=ChainGun, Ammo=12, Prerequisite=hpad`. The **Apache maps almost 1:1 onto HIND**
(swap ChainGun→TDApacheGun, Ammo 12→15, Owner soviet→BadGuy, the HELI sprite). Helipad-built; the
§3.11/§3.12 TDHPAD plumbing is already in place.

---

## 3. The Orca is the odd one — NO rotor (VTOL)

The GDI Orca is `is_rotorequipped=false` — it's a VTOL with fixed jet nacelles, not a helicopter. So it
renders as **just the body sprite, no rotor overlay** (the `IsRotorEquipped` block in Draw_It is skipped).
Otherwise it's the same attack-aircraft behavior (Ammo 6, fires TDStnkDragon pairs, returns to helipad).
There's no RA rotor-less attack aircraft to clone, but the ctor is just HIND with `is_rotor=false`.

---

## 4. Sprite-geometry risk (the Chinook lesson)

`project-chinook-pure-ra`: TD-Assets aircraft sprites can mismatch the engine's hardcoded per-type
offsets. For these two:
- **Apache: single rotor** = the **generic `else` branch** in `Draw_Rotors` (NOT the TRANSPORT-gated dual-rotor
  that broke the Chinook), drawn at body-centre — so it should align like RA's HIND/LONGBOW. The risk that
  remains is the TD-Assets **facing-0 orientation** (the Chinook's pointed diagonal): if HELI's facing-0
  isn't north, the body faces wrong. **Smoke-test first.** Muzzle offset (`primaryoffset`) = screenshot-tune.
- **Orca: no rotor**, so no rotor risk; but it's **64 frames** (vs HELI's 32) — watch the facing layout.
- HELI = 32 frames (donor: RA HIND, 32). ORCA = 64 frames (donor: a 64-frame unit, e.g. 2TNK, sliced).
- Build icons `BuildIcon_TD_Apache` / `BuildIcon_TD_Orca` exist. Text `TXT_HELI`/`TXT_ORCA` (RA has TXT_ORCA).

**Fallback if a TD sprite's facing/geometry is broken (per the Chinook):** these DO have faction-distinct
gameplay (own weapons), so don't drop to pure-RA wholesale — but if the *sprite* is unusable, render RA's
HIND/(Orca has no RA equiv) while keeping the TD weapon/stats, or remap the frames.

---

## 5. Port plan

**Apache (`AIRCRAFT_TDAPACHE`, Nod) — do first (Luke):** clone RA HIND ctor (rotor, helipad-landing,
primaryoffset 0x40), IniName "TDHELI"; NEW weapon `TDApacheGun` (TDChainGun + Burst=2); HELI sprite
(32-frame, HIND donor); `[TDHELI]` rules (Primary=TDApacheGun, Ammo=15, Str 125, Armor=heavy, Cost 1200,
Owner=BadGuy, Prereq=hpad, TechLevel 6, Speed 16=MPH_FAST, ROT 4). Cameo BuildIcon_TD_Apache.

**Orca (`AIRCRAFT_TDORCA`, GDI) — second:** clone HIND ctor but `is_rotor=false`; reuse `TDStnkDragon`;
ORCA sprite (64-frame); `[TDORCA]` rules (Ammo 6, Owner=GoodGuy, else as Apache). Cameo BuildIcon_TD_Orca.

Both: smoke-test the sprite facing/rotor first (Chinook caveat).
