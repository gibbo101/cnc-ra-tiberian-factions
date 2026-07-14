# Nod Stealth Generator — locked design + implementation plan

**Status: DESIGN LOCKED 2026-07-14 (Luke). Implement next session.**
A partial WIP implementation from the 2026-07-13/14 sessions is **uncommitted on `main`**
(bdata.cpp, building.cpp driver, defines.h, logic.cpp, rules.ini, RABUILDABLES.XML, ModText.csv).
That WIP uses the **old** every-frame-forced-cloak + observer-sight-scan model, which produced the
bug cluster below. **The locked design replaces that driver model** — keep the scaffolding
(STRUCT_TDSTEALTH type, sidebar/art wiring, ctor `IsCloakable` line) and rewrite the driver.

A new Nod building (STRUCT_TDSTEALTH) that reuses the RA **Gap Generator (GAP)** sprite and
cloaks a friendly area, defeated by bringing stealth-detector units into it.

---

## Locked behaviour

| # | Behaviour | Nature of work |
|---|-----------|----------------|
| 1 | Cloak friendly **buildings + units** inside the coverage radius | free — drive the existing `TechnoClass` cloak system |
| 2 | **Generator itself stays visible** (never cloaks); native cloakers (Stealth Tank) keep vanilla rules | 2 guards in the driver |
| 3 | Hidden from **everyone incl. the AI** | free (`Is_Cloaked` hides from non-allies) |
| 4 | **No generic auto-reveal.** Reveal on **fire** and on **taking damage** | free (`FIRE_CLOAKED` for units; `Take_Damage`→`Do_Shimmer`) |
| 5 | **Detector reveal**: any enemy techno with `IsScanner` within reveal range of a stealthed object → `Do_Shimmer` it | small custom scan (see Engine facts) + 1 INI line for the Jammer |
| 6 | **Building bibs hide with their building** (enemy sees no telltale bib) | custom cell-redraw (bibs are stamped into cells, not the sprite) |
| 7 | **Owner** sees the warped **"un-stealthing"** look (transparent→colour, distorted), not the clean ghost | one branch in `Visual_Character`, exact stage tuned in-game |
| 8 | **Unstealth/restore** on: low power / destroyed / sold / unit-leaves-radius | free — all collapse to the "not covered → restore" branch |
| 9 | Enemy sees the gen building but nothing else friendly-to-it in range (incl. no bibs) | free (gen never cloaks) |
| 10 | Generator **power cost = 100** (down from 200), as the balance concession for being an always-visible target | data (bdata.cpp + rules.ini) |
| 11 | **Armed defensive buildings** (Obelisk/SAM/AGT/towers): **ambush** — cloak normally, but **uncloak when they acquire an in-range target**, fire, then re-cloak once the threat leaves | building-side uncloak-on-target hook (see below) |

### Detector set (resolved via `IsScanner`, no hardcoded list)
- **All infantry** — already `IsScanner=true` (forced in `InfantryTypeClass` ctor, idata.cpp:1399). **No infantry changes.**
- **Attack Dog** — it's an `InfantryTypeClass` → already a scanner. No work.
- **All vessels** — already `IsScanner=true` (vdata.cpp:403).
- **Radar Jammer (MRJ)** — a vehicle; **add `Sensors=yes`** to its rules.ini entry (the `Sensors=` key sets `IsScanner`, techno.cpp:7837). One line, no code.

---

## Engine facts (established this session — build the implementation on these)

- **`IsCloakable` must be wired on buildings.** RA never cloaked a building, so `BuildingClass`
  never copied its type's `Cloakable` flag to the instance (units/infantry/vessels do). The one
  missing line `IsCloakable = Class->IsCloakable;` in the `BuildingClass` ctor (already added in the
  WIP) makes a building drivable through the cloak system. **Keep it.**

- **Detector flag = `IsScanner`.** `FootClass::Per_Cell_Process` (foot.cpp:1499-1515) shimmers a
  **cloaked object** when it arrives at a cell adjacent to an enemy techno whose type has
  `IsScanner`. **Direction matters:** vanilla only fires this from the *cloaked object's own move*.
  It does **nothing** for a stationary cloaked **building**, nor for an idle cloaked unit when a
  scanner walks up to *it*. Our field is mostly buildings + idle units, so we need the **reverse
  scan**: for each stealthed object, is any enemy `IsScanner` techno within reveal range → shimmer.
  Same flag, added direction. `Sensors=` INI key → `IsScanner` (techno.cpp:7837).

- **Cloak state machine** (techno.cpp): `Cloak` ∈ {UNCLOAKED, CLOAKING, CLOAKED, UNCLOAKING}.
  - `Do_Cloak()` only acts if `IsCloakable && (Cloak==UNCLOAKED||UNCLOAKING)`; calls `Detach_All`.
  - `Do_Uncloak()` only acts if `IsCloakable && (Cloak==CLOAKED||CLOAKING)`.
  - `Cloaking_AI()` (called from each object's own AI) owns the transition + **auto-recloak** after
    `CloakDelay` (`Rule.CloakDelay` minutes) once `Is_Ready_To_Cloak()`. It also fires
    `Do_Cloak()` itself when idle.
  - **This is the key to the rewrite:** because we chose **no generic auto-reveal**, the driver must
    **NOT force `Do_Cloak` every frame**. Set `IsCloakable=true` and let `Cloaking_AI` cloak the
    object cleanly on its own. The every-frame forced `Do_Cloak` in the WIP fought `Cloaking_AI`
    and the `FIRE_CLOAKED` fire sequence — that single mistake caused the flicker (#2), the
    fire-does-no-damage (#1), and left the cloak enum inconsistent so `Do_Uncloak`'s guard missed
    → reveal never fired (#7) and restore no-oped (#9). The driver owns only: (a) set/restore
    `IsCloakable`; (b) force-reveal (`Do_Shimmer`/`Do_Uncloak`) when a detector is in range or an
    armed building acquires a target.

- **Owner vs enemy render** = `Visual_Character` (techno.cpp:5002). Settled `CLOAKED` returns
  `VISUAL_SHADOWY` for the owner (line 5025) and `VISUAL_HIDDEN` for others. For the **warped
  owner look** (#7): return a distorted stage for owner-owned cloaked objects instead of the clean
  `VISUAL_SHADOWY` — candidates are `VISUAL_RIPPLE` or a **held mid-`UNCLOAKING` stage** (colour +
  distortion). Tune empirically via the screenshot loop; **this supersedes the old bug-#8 preference
  for the clean ghost.**

- **Bibs are stamped into map cells** (via `Lay_Bib`/`Bib_And_Offset`), not part of the building
  sprite — so the cloak render does **not** hide them. Hiding the bib (#6) = suppress/redraw the
  bib cells while the building is cloaked, restore on uncloak. Its own task.

- **Buildings have no uncloak-before-fire.** The `FIRE_CLOAKED` "uncloak then fire" path is
  unit/infantry only (unit.cpp:989, infantry.cpp:4022). A cloaked Obelisk charges and **fails** to
  fire. Hence the **ambush hook** (#11): when a stealthed armed building has a legal in-range target
  (`Target_Legal(TarCom) && In_Range(TarCom)`, or on target acquisition), `Do_Uncloak()` it; it
  re-cloaks via `Cloaking_AI` after `CloakDelay` once the threat is gone.

- **Restore discriminator = `IsCloakable && !Techno_Type_Class()->IsCloakable`** — "a non-native
  cloaker we made cloakable." Lets an object that leaves coverage (or whose generators all died)
  self-restore with no per-object saved state. Make restore **robust**: keep restoring while any
  such driver-cloaked object exists (don't one-shot via a single-frame latch), and if `Do_Uncloak`'s
  guard would miss, reset `Cloak=UNCLOAKED` + `CloakingDevice` stage directly.

- **Built-in collision-shimmer** (`drive.cpp:2336`): a unit pathing *into* a cloaked cell shimmers
  it. Momentary, on-theme, harmless — NOT the detector reveal, and explains a screenshot where units
  "seemed to detect" the base by walking into it.

- **Art/sidebar (DONE, keep):** `Image=GAP` renders the on-map HD sprite for free (no tileset alias).
  Only the sidebar CAMEO + NAME key on IniName: `RABUILDABLES.XML` `ObjectTypeClass Name="RA_TDSTEAL"`
  reuses `BuildIcon_RA_GapGenerator`; `ModText.csv` (UTF-16LE) rows `TEXT_STRUCTURE_TDSTEAL`/`_DESC`.

---

## Implementation plan (next session)

Rewrite `BuildingClass::Process_Stealth_Generators()` (building.cpp), called once/frame from
`LogicClass::AI` (already wired). New model — driver does the minimum, `Cloaking_AI` does the rest:

1. **Gather** active, powered, non-limbo `STRUCT_TDSTEALTH` generators (coord + house).
   Power gate: `House->Power_Fraction() >= 1` (low power drops the gen → restore).
2. **Cover pass** over friendly buildings + units + infantry within a generator's radius
   (`Is_Ally` to the gen), skipping: the generator type itself (#2), native cloakers
   (`Techno_Type_Class()->IsCloakable`, the Stealth Tank).
   - Covered object: `IsCloakable = true`. **Do not force `Do_Cloak`** — let `Cloaking_AI` cloak it.
     (Optionally nudge with a single `Do_Cloak` only if `Is_Ready_To_Cloak()` and not in radio
     contact, to shorten first-hide latency — but never repeatedly.)
   - Not covered but `IsCloakable && !Class->IsCloakable`: **restore** — force uncloak + reset
     `IsCloakable=false` (robust, not one-shot).
3. **Detector-reveal pass** (#5): for each currently-cloaked driver object, if any enemy
   `IsScanner` techno is within reveal range → `Do_Shimmer()` (re-cloaks naturally after via
   `Cloaking_AI`/`CloakDelay` when the detector leaves).
4. **Armed-building ambush** (#11): for each cloaked driver **building** with a weapon and a legal
   in-range target → `Do_Uncloak()` (so it can fire); re-cloaks after threat clears.
5. **Bib hide** (#6): while a building is cloaked, suppress/redraw its bib cells; restore on uncloak.
6. **Owner warp render** (#7): `Visual_Character` owner-side branch → warped stage instead of
   `VISUAL_SHADOWY`; tune in-game.
7. **Data**: `[TDSTEAL]` Power `-100`; `[MRJ]` (Radar Jammer) `Sensors=yes`; give the generator its
   **own radius** (~5–6 cells) rather than `Rule.GapShroudRadius` (10 cells read as huge in playtest).

### Also outstanding (from the WIP session, do after the driver is player-side-confirmed)
- **Nod AI build rule**: mirror the `STRUCT_GAP` block (house.cpp ~6581, `ActLike==HOUSE_BAD`) so the
  Nod AI builds the Stealth Generator organically.
- **`TF_DEV` force-spawn** (Stealth Gen for Nod AI) + a `TF_DEV` diagnostic log dumping per-covered
  object `{frame, name, Cloak, detector-in-range, action}` to verify behaviour before tuning.

### Verify in playtest (each is a distinct path)
Cloak settles to warped look (owner) / invisible (enemy); enemy AI still attacks (units path in and
detectors reveal); each teardown path restores (low power, destroyed, **sold**, leave-radius); armed
buildings ambush-fire; bibs vanish; Stealth Tank untouched; no flicker; cloaked units fire and deal
damage.

Build/deploy recipe: standard Linux mingw cross-build; on launcher-data-only edits
`rsync -a resources/remaster_mods/Vanilla_RA/ build/remaster/Vanilla_RA/` (no `--delete`) before
deploy (see CLAUDE.md build/deploy sections).

---

## Known bug (found in playtest 2026-07-15, fix next session)

**Helipad + its helicopter build and stay UN-stealthed inside a generator's radius.**

Likely two causes, both in the driver (`BuildingClass::Process_Stealth_Generators` /
`TF_Stealth_Drive`, building.cpp):

1. **Helipad never cloaks** — a helipad is (near-)permanently in **radio contact** with its
   parked helicopter, and the "don't initiate a cloak while `In_Radio_Contact()`" gate then keeps
   it UNCLOAKED forever. The gate was meant to protect *transient* ops (harvester docking, cargo
   plane, unit ejection), not a permanent tether. Fix idea: narrow the gate — e.g. only block
   cloaking for radio contact tied to an active production/docking transition, or explicitly allow
   helipads (and other permanently-tethered hosts) to cloak with their tethered craft.
2. **The helicopter itself never cloaks** — the driver only covers Buildings + Units + Infantry,
   **not Aircraft**. So even with the pad fixed, the parked/covered heli stays visible. Fix: extend
   the cover pass to `Aircraft` (at least grounded ones in radius), or accept airborne stays visible
   by design and only cloak while landed.

**Playtest confirmation (2026-07-15):** when the copter *takes off*, the helipad DOES stealth
(radio tether cleared → gate releases → it cloaks) — proving cause #1. The copter itself stays
un-stealthed even when landed — proving cause #2 (aircraft not covered). So: fix the gate to let a
helipad cloak while its craft is docked, AND extend the cover pass to grounded aircraft.
