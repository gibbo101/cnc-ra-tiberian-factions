# Air & intel additions for v4.0 — GDI A-10 + Soviet Parabombs + map-reveal powers

**Status:** DESIGN LOCKED (2026-06-19), no code yet. Part of the **v4.0 "balance + faction
additions"** milestone (companion to `navy-4.0-design.md` and the air-balance plan in
`balance-deep-dive.md`). Two air additions that share one mechanism (the Airfield) and resolve
cleanly via owner-gating.

**Divergence note:** TD's A-10 was a scripted *airstrike support power* (unbuildable, unlocked when
all enemy SAMs died). We deliberately diverge — like Dawn of the Tiberium Age (DTA), GDI builds the
A-10 as a real aircraft from an airfield. "We're at the point where we diverge and do what feels
right" (Luke). The A-10 *is* a fixed-wing plane (`Fixed wing aircraft = true`), so the Airfield is
its engine-correct home (same Yak/MiG pattern, already cloned 3× for TDORCA/TDAPACHE/TDCARGO).

---

## What's added

| Faction | Addition | Source building |
|---|---|---|
| **GDI** | **A-10 Warthog** — buildable fixed-wing napalm strafer | Airfield (`AFLD`, owner-opened) |
| **Soviet** | **Parabombs** — Badger bombing-run support power | Airfield (`AFLD`, owner-conditional grant) |

GDI air doctrine after this: **Orca (helipad) + A-10 (airfield) + Ion Cannon (superweapon)** — a
genuine air-superiority faction.

---

## The owner-gated Airfield (the navy pattern, reused)

Exactly like the shipyard serves both Allied ships and GDI's Gunboat: **one `AFLD` building,
contents gated by owner.**

- **`AFLD` `Owner=` opened to GoodGuy** (was Soviet-only) so GDI can build it.
- **A-10 = GoodGuy-only** unit → Soviets don't get it.
- **Yak / MiG = Soviet-only** (unchanged) → GDI doesn't get them.
- **Parabombs granted only to a *Soviet*-owned AFLD** (owner-conditional) → GDI's airfield does NOT
  inherit parabombs. This is the one subtlety that makes both additions coexist without conflict.

**No reskin needed:** the AFLD's generic hangar/runway art reads fine as a GDI airfield as-is
(Luke, 2026-06-19). The DTA-style "give GDI its own airfield type" is available later but unneeded.

---

## GDI A-10 — unit spec

Port as a new `AircraftType` `AIRCRAFT_TDA10`, modelled on the Yak/MiG fixed-wing airfield pattern.

- **Art:** TD-Assets `TDA10` (XML tileset + HD SRGB ZIP) — confirmed present.
- **TD source stats** (`tiberiandawn/AADATA.CPP` `AttackPlane`): **Strength 60** (very fragile),
  Cost 800, `ARMOR_ALUMINUM` (light), `MPH_FAST`, ROT 5, **Ammo 3** (3 napalm runs before rearm),
  weapon `WEAPON_NAPALM`, invisible-on-radar, fixed-wing, owned by `GOOD|BAD` in TD.
- **Weapon:** napalm/incendiary run — map to our TD napalm warhead (`TDFIRE`, as used by the SSM
  launcher) or a dedicated A-10 bombing weapon.
- **Build:** flip player-construct ON, TechLevel + sidebar cameo, prereq = `AFLD` (GoodGuy).
- **Identity:** cheap, fast, fragile expendable strafer — fits the "fragile TD air" doctrine
  (`balance-deep-dive.md` F6). Intended to be spammy AA-fodder; the buffed AA (Nod SAM, GDI AGT)
  and RA's SAM/AGUN line are the counter.
- **GDI-only for now.** TD allowed `GOOD|BAD`, so sharing it with Nod is authentic if ever wanted,
  but keep Nod the Apache/cloak faction for v4.0.

## Soviet Parabombs — power spec

- RA **already has** the Badger bomber (`AIRCRAFT_BADGER`) **and** the parabomb super-weapon — this
  is a *gating* task, not new content.
- **Grant the parabomb power when a Soviet-owned `AFLD` is active**, using the same "host building
  grants a super weapon" pattern our **Ion Cannon** already uses.
- Owner-conditional so GDI's AFLD doesn't grant it (see owner-gating above).

---

## Nod Paratroopers — delivered via C17 (added 2026-06-19)

Nod is the best thematic fit for paratroopers of any faction (guerrilla/insurgency identity —
airborne troop insertion behind lines). Granted from the **Nod Airstrip (`TDAFLD`)**, owner-gated to
BadGuy.

**Mechanism — reuse the RA paratrooper power, swap the delivery.** The drop is built in
`HouseClass::Place_Special_Blast` (`house.cpp:3298`, the `@PINF` temp team) as a 2-member team: a
plane + its passenger infantry. Currently `AIRCRAFT_BADGER` × `INFANTRY_E1`. For the Nod/BadGuy
house, swap to:
- **`AIRCRAFT_BADGER` → `AIRCRAFT_TDCARGO`** (the C17 — already ported for airstrip vehicle delivery)
- **`INFANTRY_E1` → `INFANTRY_TDE1`** (TD Minigunner — already in)

Gate on `Class->House` so any Soviet paradrop keeps Badger+E1. **Fidelity-correct:** Nod's own
transport plane dropping Nod's own troops. A handful of lines in one spot; both assets already owned.

**Verify at implementation:**
1. **C17 passenger-drop path** — the Badger has special-case handling (`aircraft.cpp`,
   `if (*this == AIRCRAFT_BADGER)`); confirm `TDCARGO` has `Max_Passengers > 0` and extend any
   Badger-specific paradrop logic to the C17, or it won't drop troops.
2. **Gating** — paratroopers grant on `STRUCT_AIRSTRIP`. TDAFLD previously *leaked* RA paratroopers
   (fixed per `[[reference-tdafld-superweapon-leak]]`); flip that intentional-block into an
   intentional-*grant* for Nod. Same plumbing as the Nod spy-plane-from-TDAFLD plan below.

**Airstrip = each faction's offensive-air hub:** GDI A-10 (strafing), Soviet parabombs (bombing),
Nod paratroopers (troop insertion) — all airfield-launched, each in character.

## Intel / map-reveal powers (added 2026-06-19)

Same "host building grants a power" pattern, owner-conditional. Both reuse **existing** RA mechanics
— no new engine code, just gating. Allied GPS and Soviet spy-plane stay untouched, so all four
factions read distinctly (GDI/Nod differ from each other: full-reveal vs targeted flyover).

| Faction | Power | Host building | Notes |
|---|---|---|---|
| **GDI** | **GPS satellite** — full permanent map reveal | **TDEYE** (Advanced Comm Center, GoodGuy, TL7) | Fits GDI orbital/satellite identity; TDEYE already hosts the Ion Cannon. Mirrors Allies (GPS from top-tech building). |
| **Nod** | **Spy Plane** — targeted temporary area reveal (recon flyover) | **TDAFLD** (Nod Airstrip, BadGuy, TL2) | 1:1 parallel with Soviet (spy plane from the airfield); suits Nod recon/stealth. |

- **Decision history:** briefly explored giving GDI/Nod *bespoke* reveal mechanics (GDI periodic
  satellite sweep, Nod cloaked recon unit) — rejected in favour of reusing GPS/spy-plane for
  simplicity (Luke, 2026-06-19). "Come from the buildings only."
- **Tuning:** Nod's spy plane via TDAFLD is available early (TL2 building) — use `SpyPlaneTech` (RA
  default 5) so Nod recon isn't *too* early. GPS uses `GPSTechLevel` (RA default 8).
- **Verify:** full-map `GPS` reveal fires for a GoodGuy house; spy-plane-from-building grant works
  for a BadGuy house the same way it does for Soviet.

## Systemic bonus
Both the A-10 and the Badger are fragile flyovers, so the **AA buffs in the air-balance plan
intercept airstrikes too** — a defended base shoots them down mid-run. Air-defense work and
air-support powers reinforce each other.

## Open / to verify before coding
1. **Parabomb super-weapon live in our skirmish ruleset** — confirm `SW_PARA_BOMB` + Badger are
   enabled in skirmish before wiring the AFLD grant.
2. **Ion Cannon grant mechanism** — reuse the exact host-building→super-weapon path for the Soviet
   parabomb grant (and confirm the A-10 sits *below* the Ion Cannon in GDI's tech, not redundant).
3. **A-10 napalm weapon** — reuse `TDFIRE` (SSM napalm) vs a dedicated A-10 bombing weapon; pick at
   implementation.
4. **AFLD owner-open balance** — GDI gains an airfield (and its footprint/power draw); set A-10
   Cost/TechLevel so early A-10 spam isn't oppressive (TD cost 800 is the starting point).
5. **v5.0 AI** — buildable A-10 integrates into normal AI aircraft-build logic; Soviet parabomb
   firing reuses the AI super-weapon logic (Ion/Nuke). Plumb Owner/prereq now.

## References
- TD source: `SOURCECODE/TIBERIANDAWN/AADATA.CPP` (`AttackPlane`/`AIRCRAFT_A10`), `DEFINES.H`.
- Aircraft port pattern: `docs/td-vehicle-port-recipe.md`, the TDORCA/TDAPACHE/TDCARGO ports.
- Super-weapon host pattern: the mod's Ion Cannon + Nuclear Strike hosts.
- Air balance (F6/F7/F8): `docs/balance-deep-dive.md`. Navy companion: `docs/navy-4.0-design.md`.
