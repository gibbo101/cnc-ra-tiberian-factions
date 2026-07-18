# Nod Stealth Generator — locked design + implementation plan

**Status: SHIPPED & on `main` (driver rewritten per the locked design).**
The cloak driver (`BuildingClass::Process_Stealth_Generators` / `TF_Stealth_Drive`, building.cpp)
is committed and deployed. Behaviour follows the locked design below.

**Art: reverted to the RA Gap Generator sprite (2026-07-15).** A custom HD platform-dome art
(TDSTEAL.ZIP/TDSTEALMAKE.ZIP) was tried and dropped: the art stood taller than any 2×1 classic
donor could anchor, so the launcher floated the sprite above its footprint and weapons fired on
the base cell one below the visible dome. `ShapeSize` correction over-/under-sized it, so the
building was reverted to `Image=GAP` (native 1×2 footprint, self-anchoring, known-good). The
cloak field keys on `STRUCT_TDSTEALTH`, not the art, so field behaviour is unchanged. Commit
`91b88be`.

**Balance: 400 effective HP** — `Strength=200` in rules.ini, doubled to 400 by the TD-prefix
rule (`BuildingClass::Read_INI`); power-plant/defensive tier, matching the "always-visible weak
point that collapses the field" intent. (Earlier `Strength=600` read as 1200 in-game because of
the doubling — far too tanky.)

A Nod building (STRUCT_TDSTEALTH) that reuses the RA **Gap Generator (GAP)** sprite and
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

### AI (2026-07-15)
- **Nod AI build rule — DONE.** A `STRUCT_TDSTEALTH` slot mirrors the `STRUCT_GAP` block
  (house.cpp, `ActLike==HOUSE_BAD`, gated on full power + income); `Can_Build` enforces the
  `TDTMPL` prerequisite, so the AI builds the Stealth Generator organically after the Temple of
  Nod. (The Temple itself was already organic — Nod's mapped tech center via `TF_Skirmish_Equivalent`.)
- **`TF_DEV` force-spawn — REMOVED.** The dev crutch that pre-placed `TDNUK2` + `TDSTEALTH` for
  every Nod AI at scenario start is gone now that the AI builds it organically.

### Verify in playtest (each is a distinct path)
Cloak settles to warped look (owner) / invisible (enemy); enemy AI still attacks (units path in and
detectors reveal); each teardown path restores (low power, destroyed, **sold**, leave-radius); armed
buildings ambush-fire; bibs vanish; Stealth Tank untouched; no flicker; cloaked units fire and deal
damage.

Build/deploy recipe: standard Linux mingw cross-build; on launcher-data-only edits
`rsync -a resources/remaster_mods/Vanilla_RA/ build/remaster/Vanilla_RA/` (no `--delete`) before
deploy (see CLAUDE.md build/deploy sections).

---

## Fixed bugs

### Helipad + helicopter stayed UN-stealthed in the field — FIXED 2026-07-15

Two causes, both in the driver (`TF_Stealth_Drive`, building.cpp):

1. **Helipad never cloaked** — a helipad is (near-)permanently in **radio contact** with its
   parked helicopter, and the "don't cloak while `In_Radio_Contact()`" gate kept it UNCLOAKED
   forever. **Fix:** the gate now blocks a fresh cloak only while the tethered partner is
   *in transit* (`partner->Is_Foot() && Target_Legal(partner->NavCom)`) — an inbound harvester or
   cargo plane stays protected from a stranding `Detach`, but a parked idle helicopter (no NavCom)
   lets the pad cloak with it.
2. **Helicopter itself never cloaked** — the cover pass only iterated Buildings + Units + Infantry.
   **Fix:** added an `Aircraft` pass in `Process_Stealth_Generators`.

### Whole base stayed stealthed after the generator was destroyed — FIXED 2026-07-15

Killing the generator left previously-cloaked buildings cloaked forever (newly-built ones correctly
stayed visible). Cause: the restore pass was gated by a single `_had_generators` latch that let it
run for **exactly one frame** after the last generator died. `Do_Uncloak()` only *starts* a
multi-frame transition, so the object never reached `UNCLOAKED` that frame, `IsCloakable` was never
reset, and `Cloaking_AI` re-cloaked it. **Fix:** `TF_Stealth_Drive` now returns whether an object
is still driver-cloaked, and `Process_Stealth_Generators` keeps the restore pass running (via
`_restore_pending`) until a full pass finds nothing left to restore.

### Building bibs (#6) — DONE via render-time hide, not cell-redraw

The plan above (#6, "suppress/redraw the bib cells… restore on uncloak") was **not** the shipped
approach — it turned out to be actively harmful. A `TF_Sync_Bib` implementation that `Disown`ed the
bib `SmudgeClass` was tried and **removed**: a bib smudge also blocks placement
(`CellClass::Is_Clear_To_Build`, cell.cpp:494), so clearing it let the (blind) enemy build into a
cloaked base's bib strip. The correct mechanism already existed in the Remaster draw path
(`dllinterface.cpp` `tf_hide_bib`, from the original commit `cd8bd17`): it **keeps the smudge**
(placement stays blocked) and suppresses only the *draw* when the covering building is
`VISUAL_HIDDEN` — transparent to the enemy, bib still shown to the owner. This is the canonical
approach; don't reintroduce smudge removal.

**Covering-building resolution hardened 2026-07-18 (`58ae18f`), first AI-built generator in the
wild:** the original this-cell-or-one-north probe missed TD foundations — TDPROC's entire bottom
row is overlap-only (`TdOListProc`), so cloaked TD refineries kept floating bibs. The probe now
reconstructs the bib rectangle from `SmudgeData` (col + row·Width; top row is the owner's bottom
foundation row, column-aligned per `Bib_And_Offset`) and walks north through candidate foundation
rows, resolving at the first row holding any building, probing every column per row (per-cell
holes: dock notch, hand of Nod). `TF_BIB_DIAG` (dev builds) logs any bib that still draws with
what it resolved to.

## Balance

**Effective HP = 400** (`Strength=200`, doubled by the TD-prefix rule). Set 2026-07-15 after a
playtest showed 4 Apaches only halving it — the old `Strength=600` was silently doubled to 1200,
far too tanky for the "always-visible weak point." Power-plant/defensive tier now.
