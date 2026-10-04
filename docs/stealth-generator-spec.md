# Nod Stealth Generator

**Status:** Reference; shipped in 4.0.0, TS art in 4.1.0.

`STRUCT_TDSTEALTH` (`[TDSTEAL]`, behind the Temple of Nod) cloaks friendly buildings and units
within 10 cells (`TF_STEALTH_RADIUS_CELLS` in `building.cpp`). Detectors (`IsScanner`) within 3
cells reveal them, armed defences ambush, and bibs hide at render time. The TS Mobile Sensor Array
also shows cloaked units to its owner (`emp-cannon-design.md`). The driver is
`BuildingClass::Process_Stealth_Generators` / `TF_Stealth_Drive` (`building.cpp`), called once a
frame from `LogicClass::AI`.

- **Art:** TS's NASTLH, upscaled hq4x (`TDSTEAL.ZIP`, `TDSTEALMAKE.ZIP`), on a **2x1 footprint**
  (`BSIZE_21` + `List21`), `FACING_NONE` (FACING_S made attackers aim a cell south), art donor
  `STRUCT_TDSILO` (`ts-asset-import-spike.md`). Dead route: a taller custom HD dome, which no 2x1
  classic donor could anchor, so the launcher floated it above its footprint.
- **Balance:** `Strength=200`, doubled to 400 by the TD-prefix rule: an always-visible weak point
  (600 read as 1200 and took four Apaches to halve). Power −100.

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

## Engine facts

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

- **Sidebar:** the cameo and name key on IniName (`RA_TDSTEAL` in `RABUILDABLES.XML`, ModText rows
  `TEXT_STRUCTURE_TDSTEAL` / `_DESC`).

---

## The driver

The driver does the minimum and `Cloaking_AI` does the rest:

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
5. **Bib hide** (#6): at render time (see "Building bibs" below).
6. **Owner warp render** (#7): `Visual_Character` owner-side branch → warped stage instead of
   `VISUAL_SHADOWY`; tune in-game.
7. **Data:** `[TDSTEAL]` Power −100; `[MRJ]` (Radar Jammer) `Sensors=yes`. The radius is the
   driver's own `TF_STEALTH_RADIUS_CELLS` = 10, not `Rule.GapShroudRadius`.

### AI
- **Nod AI build rule — DONE.** A `STRUCT_TDSTEALTH` slot mirrors the `STRUCT_GAP` block
  (house.cpp, `ActLike==HOUSE_BAD`, gated on full power + income); `Can_Build` enforces the
  `TDTMPL` prerequisite, so the AI builds the Stealth Generator organically after the Temple of
  Nod. (The Temple itself was already organic — Nod's mapped tech center via `TF_Skirmish_Equivalent`.)
- **`TF_DEV` force-spawn — REMOVED.** The dev crutch that pre-placed `TDNUK2` + `TDSTEALTH` for
  every Nod AI at scenario start is gone now that the AI builds it organically.

---

## Traps (fixed)

### A helipad and its helicopter never cloaked

Two causes, both in the driver (`TF_Stealth_Drive`, building.cpp):

1. **Helipad never cloaked** — a helipad is (near-)permanently in **radio contact** with its
   parked helicopter, and the "don't cloak while `In_Radio_Contact()`" gate kept it UNCLOAKED
   forever. **Fix:** the gate now blocks a fresh cloak only while the tethered partner is
   *in transit* (`partner->Is_Foot() && Target_Legal(partner->NavCom)`) — an inbound harvester or
   cargo plane stays protected from a stranding `Detach`, but a parked idle helicopter (no NavCom)
   lets the pad cloak with it.
2. **Helicopter itself never cloaked** — the cover pass only iterated Buildings + Units + Infantry.
   **Fix:** added an `Aircraft` pass in `Process_Stealth_Generators`.

### The whole base stayed cloaked after the generator died

Killing the generator left previously-cloaked buildings cloaked forever (newly-built ones correctly
stayed visible). Cause: the restore pass was gated by a single `_had_generators` latch that let it
run for **exactly one frame** after the last generator died. `Do_Uncloak()` only *starts* a
multi-frame transition, so the object never reached `UNCLOAKED` that frame, `IsCloakable` was never
reset, and `Cloaking_AI` re-cloaked it. **Fix:** `TF_Stealth_Drive` now returns whether an object
is still driver-cloaked, and `Process_Stealth_Generators` keeps the restore pass running (via
`_restore_pending`) until a full pass finds nothing left to restore.

### Building bibs (#6): hidden at render time, never removed

Removing the bib is harmful: a `TF_Sync_Bib` implementation that `Disown`ed the
bib `SmudgeClass` was tried and **removed**: a bib smudge also blocks placement
(`CellClass::Is_Clear_To_Build`, cell.cpp:494), so clearing it let the (blind) enemy build into a
cloaked base's bib strip. The correct mechanism already existed in the Remaster draw path
(`dllinterface.cpp` `tf_hide_bib`, from the original commit `cd8bd17`): it **keeps the smudge**
(placement stays blocked) and suppresses only the *draw* when the covering building is
`VISUAL_HIDDEN` — transparent to the enemy, bib still shown to the owner. This is the canonical
approach; don't reintroduce smudge removal.

**Covering-building resolution (`58ae18f`):** the original this-cell-or-one-north probe missed TD foundations — TDPROC's entire bottom
row is overlap-only (`TdOListProc`), so cloaked TD refineries kept floating bibs. The probe now
reconstructs the bib rectangle from `SmudgeData` (col + row·Width; top row is the owner's bottom
foundation row, column-aligned per `Bib_And_Offset`) and walks north through candidate foundation
rows, resolving at the first row holding any building, probing every column per row (per-cell
holes: dock notch, hand of Nod). `TF_BIB_DIAG` (dev builds) logs any bib that still draws with
what it resolved to.
