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
- **AI superweapons:** discovery is sticky (remembered intel) and the cloak is live cover over it, so
  a Stealth Generator field shields buildings from AI superweapons until a detector breaks the cloak
  (`Special_Weapon_AI`).
- **Balance:** `Strength=200`, doubled to 400 by the TD-prefix rule: an always-visible weak point
  (600 read as 1200 and took four Apaches to halve). Power −100.

---

## Locked behaviour

| # | Behaviour | Nature of work |
|---|-----------|----------------|
| 1 | Cloak friendly **buildings + units** inside the coverage radius | free — drive the existing `TechnoClass` cloak system |
| 2 | **Generator itself stays visible** (never cloaks); native cloakers (Stealth Tank) keep vanilla rules | 2 guards in the driver |
| 3 | Hidden from **everyone incl. the AI** | free (`Is_Cloaked` hides from non-allies) |
| 4 | **No generic auto-reveal.** Reveal on **fire** and on **taking damage** | free (`FIRE_CLOAKED`, units and buildings alike; `Take_Damage`→`Do_Shimmer`) |
| 5 | **Detector reveal**: any enemy techno with `IsScanner` within reveal range of a stealthed object → `Do_Shimmer` it | small custom scan (see Engine facts) + 1 INI line for the Jammer |
| 6 | **Building bibs hide with their building** (enemy sees no telltale bib) | custom cell-redraw (bibs are stamped into cells, not the sprite) |
| 7 | **Owner** sees the warped **"un-stealthing"** look (transparent→colour, distorted), not the clean ghost | one branch in `Visual_Character`, exact stage tuned in-game |
| 8 | **Unstealth/restore** on: low power / destroyed / sold / unit-leaves-radius | free — all collapse to the "not covered → restore" branch |
| 9 | Enemy sees the gen building but nothing else friendly-to-it in range (incl. no bibs) | free (gen never cloaks) |
| 10 | Generator **power cost = 100** (down from 200), as the balance concession for being an always-visible target | data (bdata.cpp + rules.ini) |
| 11 | **Armed defensive buildings** (Obelisk/SAM/AGT/towers): **ambush** — cloak normally, but **uncloak when they acquire an in-range target**, fire, then re-cloak once the threat leaves | building-side uncloak-on-target hook (see below) |

### Detector set (resolved via `IsScanner`, no hardcoded list)
- **All infantry, the dog included, and all vessels** detect with no work (the field manual's
  [A stealth generator](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/behaviours/stealth-generator.md#what-the-engine-gives-you)).
- **Radar Jammer (MRJ)** — a vehicle; **add `Sensors=yes`** to its rules.ini entry (the `Sensors=` key sets `IsScanner` in `TechnoTypeClass::Read_INI`). One line, no code.

---

## Engine facts

The engine side follows the field manual's [A stealth generator](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/behaviours/stealth-generator.md): the cloak machine,
the one-way detection, `IsCloakable` missing from the building constructor (TF's `BuildingClass` constructor copies
it) and the forced-cloak trap. The driver owns only two things: setting and restoring `IsCloakable`, and forcing a
reveal (`Do_Shimmer` / `Do_Uncloak`) when a detector is in range or an armed building acquires a target;
`Cloaking_AI`, called from each object's own AI, does the rest. `Rule.CloakDelay` is read in `RulesClass::General`
from `SubmergeDelay`; there is no `CloakDelay=` key.

- **Owner vs enemy render:** the export sends the raw `Cloak` state, not
  `TechnoClass::Visual_Character` (its values per viewer are on the manual's page), so whether
  `Visual_Character` shapes the launcher's render is unproven. For the **warped
  owner look** (#7): return a distorted stage for owner-owned cloaked objects instead of the clean
  `VISUAL_SHADOWY` — candidates are `VISUAL_RIPPLE` or a **held mid-`UNCLOAKING` stage** (colour +
  distortion). Tune empirically via the screenshot loop; **this supersedes the old bug-#8 preference
  for the clean ghost.**

- **Bibs** (`Lay_Bib`/`Bib_And_Offset`) need their own hiding (#6): see "Building bibs" under Traps.

- **Buildings uncloak to fire only from `Mission_Attack`.** `TechnoClass::Can_Fire` returns
  `FIRE_CLOAKED` for anything not `UNCLOAKED`, and `BuildingClass::Mission_Attack` answers it with
  `Do_Uncloak()` as units and infantry do (EA `BUILDING.CPP`, `case FIRE_CLOAKED`). That waits for the
  first shot and depends on `Do_Uncloak`'s guard. The **ambush hook** (#11) reveals earlier: when a stealthed armed building has a legal in-range target
  (`Target_Legal(TarCom) && In_Range(TarCom)`, or on target acquisition), `Do_Uncloak()` it; it
  re-cloaks via `Cloaking_AI` after `CloakDelay` once the threat is gone.

- **Restore discriminator = `IsCloakable && !Techno_Type_Class()->IsCloakable`** — "a non-native
  cloaker we made cloakable." Lets an object that leaves coverage (or whose generators all died)
  self-restore with no per-object saved state. Make restore **robust**: keep restoring while any
  such driver-cloaked object exists (don't one-shot via a single-frame latch), and if `Do_Uncloak`'s
  guard would miss, reset `Cloak=UNCLOAKED` + `CloakingDevice` stage directly.

- **Built-in collision shimmer** (`DriveClass::Start_Of_Move` and `While_Moving`): momentary,
  harmless, and not the detector reveal (the field manual's
  [What the engine gives you](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/behaviours/stealth-generator.md#what-the-engine-gives-you)).

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

Each is on the field manual's [A stealth generator](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/behaviours/stealth-generator.md#traps), traps; TF's side of each:

- **A helipad and its helicopter never cloaked:** the radio-contact gate in `TF_Stealth_Drive` now blocks a fresh
  cloak only while the partner is in transit (`partner->Is_Foot() && Target_Legal(partner->NavCom)`), and
  `Process_Stealth_Generators` has an `Aircraft` pass.
- **The whole base stayed cloaked after the generator died** (buildings built after it stayed visible): `TF_Stealth_Drive` returns whether an object is still
  driver-cloaked, and `Process_Stealth_Generators` keeps restoring (`_restore_pending`) until a full pass finds
  nothing left.
- **Building bibs (#6): hidden at render time, never removed.** `tf_hide_bib` in `dllinterface.cpp` keeps the smudge
  (placement stays blocked: `CellClass::Is_Clear_To_Build` refuses a bib) and suppresses only its draw while the covering building is `VISUAL_HIDDEN`, so the owner
  still sees it. A `TF_Sync_Bib` that `Disown`ed the smudge was removed; don't reintroduce smudge removal.

**Covering-building resolution (`58ae18f`):** the original this-cell-or-one-north probe missed TD foundations — TDPROC's entire bottom
row is overlap-only (`TdOListProc`), so cloaked TD refineries kept floating bibs. The probe now
reconstructs the bib rectangle from `SmudgeData` (col + row·Width; top row is the owner's bottom
foundation row, column-aligned per `Bib_And_Offset`) and walks north through candidate foundation
rows, resolving at the first row holding any building, probing every column per row (per-cell
holes: dock notch, hand of Nod).
