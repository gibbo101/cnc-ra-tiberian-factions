# Building catalogue — Tiberian Factions for Red Alert

**Status:** Reference. TD-source stats for the TD buildings, all separate `STRUCT_TD*` engine types.
Values are TD-authentic, from `tiberiandawn/bdata.cpp`; live rules.ini values differ where
`balance-deep-dive.md` moved them. `scripts/buildings_manifest.py` mirrors the flag and wiring
tables, and wins if they drift. How the buildings were ported: `td-building-separation-recipe.md`
and the `td-*` deep dives.

All nineteen ship as their own `STRUCT_TD*` types; TDFACT and the TD MCV were split per faction in 4.1.0
(TDGFACT, TDNFACT, TDGMCV, TDNMCV). Entry names below use the TD asset name (e.g. "PYLE", "HAND") where the
rules.ini IniName is TD-prefixed (`TDPYLE`, `TDHAND`) to avoid the vanilla-RA collision class in
`td-building-separation-recipe.md`, gotcha 9. Not ported: TD's Hospital (HOSP), Bio Lab (BIO) and Tanker (ARCO),
all TD level 99 and not normally buildable.

---

## Master flag table (TD-authentic)

Per-building flags extracted from `tiberiandawn/bdata.cpp`. These are the values `add_building.py` reads. **IniName** is the catalogue IniName (TD-prefixed); **Image/Footprint/sprite ZIPs** keep the unprefixed TD asset names.

| IniName | Faction | Cost | Power | STRNTH | Sight | Adj | Armor | Bib | Cap | Crew | Repair | Idle:Start/Count/Rate | Points | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TDNUKE | both  | 300  | +100 | 200  | 2 | 1 | wood     | yes | yes | yes | yes | 0/4/15  | 50  | TD lvl 0 |
| TDNUK2 | both  | 700  | +200 | 300  | 2 | 1 | wood     | yes | yes | yes | yes | 0/4/15  | 75  | TD lvl 5, prereq TDNUKE |
| TDPROC | both  | 2000 | -40  | 450  | 4 | 1 | wood     | yes | yes | yes | yes | 0/6/4   | 55  | TD lvl 1, dock cycles (`harvester-docking-rework-plan.md`) |
| TDSILO | both  | 150  | -10  | 150  | 2 | 1 | wood     | yes | yes | no  | yes | —       | 16  | TD lvl 1 — capacity-based shape, not a cycle |
| TDPYLE | GDI   | 300  | -20  | 400  | 3 | 1 | wood     | yes | yes | yes | yes | 0/10/3  | 60  | TD lvl 0 (rules.ini TechLevel 1) |
| TDHAND | Nod   | 300  | -20  | 400  | 3 | 1 | wood     | yes | yes | yes | yes | 0/10/3  | 61  | TD lvl 0 (rules.ini TechLevel 1), 2×3 footprint |
| TDWEAP | GDI   | 2000 | -30  | 500  | 3 | 1 | aluminum | yes | yes | yes | yes | 0/1/0   | 86  | TD lvl 2, static idle |
| TDAFLD | Nod   | 2000 | -30  | 500  | 5 | 1 | steel    | yes | yes | yes | yes | 0/16/3  | 86  | TD lvl 2, 4×2, AIRSTRIP anim spec |
| TDHQ   | both  | 1000 | -40  | 500  | 10| 1 | wood     | yes | yes | yes | yes | 0/16/4  | 20  | TD lvl 2, radar |
| TDEYE  | GDI   | 2800 | -200 | 500  | 10| 1 | wood     | yes | **no** | yes | yes | 0/16/4 | 100 | TD lvl 7, GDI superweapon host |
| TDTMPL | Nod   | 3000 | -150 | 1000 | 4 | 1 | aluminum | yes | **no** | yes | yes | 0/1/0  | 20  | TD lvl 7, Nod superweapon host |
| TDFIX  | both  | 1200 | -30  | 400  | 3 | 1 | wood     | yes | yes | yes | yes | 0/1/0   | 46  | TD lvl 5, ACTIVE 0/7/2 |
| TDHPAD | both  | 1500 | -10  | 400  | 3 | 1 | wood     | yes | yes | **no** | yes | 0/0/0 | 65  | TD lvl 6, no idle anim |
| TDGTWR | GDI   | 500  | -10  | 200  | 3 | 1 | wood     | no  | **no** | yes | yes | —     | 25  | TD lvl 2, 1×1 |
| TDATWR | GDI   | 1000 | -20  | 300  | 4 | 1 | aluminum | no  | **no** | yes | yes | —     | 30  | TD lvl 4, 1×2 |
| TDOBLI | Nod   | 1500 | -150 | 200  | 5 | 1 | aluminum | no  | **no** | yes | yes | —     | 35  | TD lvl 4, 1×2, ACTIVE 0/4/RATE |
| TDGUN  | Nod   | 600  | -20  | 200  | 5 | 1 | steel    | no  | **no** | yes | yes | —     | 26  | TD lvl 2, 1×1 |
| TDSAM  | Nod   | 750  | -20  | 200  | 3 | 1 | steel    | no  | **no** | **no** | yes | — | 40  | TD lvl 6, 2×1, turret-based |
| TDFACT | both  | 5000 | **0** | 400  | 3 | 1 | wood     | yes | yes | yes | yes | 0/4/3   | 70  | TD lvl 99; Power 0 as RA's [FACT]; split per faction in 4.1.0 (TDGFACT, TDNFACT) |

**Reading the table:**
- `STRNTH` is TD's raw `bdata.cpp` value, which is what rules.ini `Strength=` holds. TD's `BuildingTypeClass` constructor passes `strength*2`, and `redalert/bdata.cpp`'s `Read_INI` doubles every `TD*` building's `MaxStrength` to match, so in-game HP is twice the column (`td-port-playbook.md` §3.21).
- `Sight` is TD's own value (each `tiberiandawn/bdata.cpp` class's `// SIGHTRANGE: Range of sighting.` line), which rules.ini `Sight=` holds. TD's sight reads short at RA's scale (roughly 2 cells under the RA equivalents, e.g. NUKE=2 vs POWR=4, PYLE=3 vs TENT=5), so the same `Read_INI` branch adds 3 cells to every `TD*` building: in game a TD power plant sees 5.
- Empty `Idle` column = no idle animation (engine renders shape 0 statically). Damaged state = shape 1 in that case (the engine's `largest = max(Anims[*].Start + Count) = 1` auto-shift).
- `Crew=no` means selling/destroying spawns zero infantry (TD canon for SILO/HPAD/SAM).
- `Cap=no` (bold) marks TD's uncapturable buildings: defensive structures and the superweapon hosts. **TMPL and EYE are NOT capturable per TD.**
- `Points` is the TD-authentic Risk/Reward value extracted from `tiberiandawn/bdata.cpp` per-class constructor (the line commented `// RISK/RWRD: Risk/reward rating values`). Both `Risk` and `Reward` fields are set from the rules.ini `Points=` key (`TechnoTypeClass::Read_INI`), and the value feeds `TechnoClass::Value()`. Without it the AI can't see the building — see `td-building-separation-recipe.md`, gotcha 11. **Mandatory field for every TD entry.**

**Note on TDHQ:** TD's `RADAR` (HQ) has Points=20, lower than RA's `DOME` (Points=30), so the AI weighs HQs slightly less than domes. If skirmishes show HQs being ignored, raising it to 30 is the lever; record any deviation here.

---

## Master wiring table (engine hookups)

Values that **must be set in rules.ini per-entry**; nothing is inherited. Omitting any of these reproduces the same class of bug as the `Points=` issue: the building constructs but the engine treats it as a vanilla-default placeholder for the missing field.

| IniName | TechLevel | Prereq (TD-prefixed) | Primary | Secondary | BaseNormal | Owner | TD source line |
|---|---|---|---|---|---|---|---|
| TDNUKE | 0  | —      | —         | — | yes | GoodGuy,BadGuy | `bdata.cpp:892` |
| TDNUK2 | 5  | TDNUKE | —         | — | yes | GoodGuy,BadGuy | `bdata.cpp:943` |
| TDPROC | 1  | TDNUKE | —         | — | yes | GoodGuy,BadGuy | `bdata.cpp:585` |
| TDSILO | 1  | TDPROC | —         | — | yes | GoodGuy,BadGuy | `bdata.cpp:636` |
| TDPYLE | 1 (TD 0) | TDNUKE | —         | — | yes | GoodGuy        | `bdata.cpp:1097` |
| TDHAND | 1 (TD 0) | TDNUKE | —         | — | yes | BadGuy         | `bdata.cpp:1148` |
| TDWEAP | 2  | TDPROC | —         | — | yes | GoodGuy        | `bdata.cpp:264` |
| TDAFLD | 2  | TDPROC | —         | — | yes | BadGuy         | `bdata.cpp:841` |
| TDHQ   | 2  | TDPROC | —         | — | yes | GoodGuy,BadGuy | `bdata.cpp:739` |
| TDEYE  | 7  | TDHQ   | —         | — | yes | GoodGuy        | `bdata.cpp:213` |
| TDTMPL | 7  | TDHQ   | —         | — | yes | BadGuy         | `bdata.cpp:162` |
| TDFIX  | 5  | TDNUKE | —         | — | yes | GoodGuy,BadGuy | `bdata.cpp:1250` |
| TDHPAD | 6  | TDPYLE (the faction pads: TDGHPAD TDPYLE, TDNHPAD TDHAND) | — | — | yes | GoodGuy,BadGuy | `bdata.cpp:688` |
| TDGTWR | 2  | TDPYLE | TDChainGun  | — | yes | GoodGuy      | `bdata.cpp:320` |
| TDATWR | 4  | TDHQ   | TDTowTwo    | — | yes | GoodGuy      | `bdata.cpp:372` |
| TDOBLI | 4  | TDHQ   | TDOblsLaser | — | yes | BadGuy       | `bdata.cpp:424` |
| TDGUN  | 2  | TDHAND | TDTurretGun | — | yes | BadGuy       | `bdata.cpp:475` |
| TDSAM  | 6  | TDHAND | TDNike      | — | yes | BadGuy       | `bdata.cpp:790` |
| TDFACT | 99 | —      | —         | — | yes | GoodGuy,BadGuy | `bdata.cpp:534` |

**Column derivation:**

- **TechLevel** — TD source's "Build level" line. Drives sidebar gating. `TechnoTypeClass::Read_INI` (`redalert/techno.cpp`) loads it from `TechLevel=`.
- **Prereq** — TD source's STRUCTF_* mapped to the TD-prefixed equivalent (table below). STRUCTF_BARRACKS splits by faction so each side's chain is internally consistent: the shared TDHPAD names TDPYLE, and the per-faction pads take their own barracks (`ai-upgrade-plan.md` W2); `HouseClass::Can_Build` lets either barracks stand in for the other on a type both GDI and Nod own (`Owner=GoodGuy,BadGuy`, as TDHPAD). Loaded from `Prerequisite=` in the same function.
- **Primary / Secondary** — each TD weapon ships as its own TD-ported weapon type (`td-port-playbook.md`); the live values are in rules.ini. Loaded from `Primary=` / `Secondary=`.
- **BaseNormal** — all 19 entries are real base structures, so `yes` across the board. (Decorative/civilian buildings would be `no`, but none of ours are.) `BuildingTypeClass::Read_INI` (`redalert/bdata.cpp`) loads it from `BaseNormal=`.
- **Owner** — TD source's HOUSEF_GOOD/HOUSEF_BAD flags mapped to our `Owner=GoodGuy,BadGuy` syntax. GoodGuy = GDI (HOUSE_GOOD), BadGuy = Nod (HOUSE_BAD).

**TD prereq → RA Prerequisite= mapping:**

| TD prereq enum | TD building | Our entry uses |
|---|---|---|
| STRUCTF_NONE | nothing | (omit `Prerequisite=` line) |
| STRUCTF_POWER | NUKE | `Prerequisite=TDNUKE` |
| STRUCTF_BARRACKS | PYLE (GDI) / HAND (Nod) | `Prerequisite=TDPYLE` or `TDHAND` per faction |
| STRUCTF_REFINERY | PROC | `Prerequisite=TDPROC` |
| STRUCTF_RADAR | HQ | `Prerequisite=TDHQ` |
| STRUCTF_HOSPITAL | HOSP | `Prerequisite=TDHOSP` (HOSP isn't ported) |

---

## Footprints

Each TD building's occupy and overlap lists are decoded from `tiberiandawn/bdata.cpp` (TD's `MCW` is RA's
`MAP_CELL_W`) and ship in its class constructor in TF's `redalert/bdata.cpp` (for example `TdListProc` /
`TdOListProc`, and `List21` / `OListSAM` for the SAM, whose overlap uses negative offsets above its box). The
`Footprint=` presets in `BuildingTypeClass::Read_INI` cover NUKE, NUK2, EYE and HQ (NUK2's 2×2 L-shape: three cells
occupied, one overlap), PYLE (top row occupied, bottom row overlap), HAND (2×3, with its own exit list and exit point
`XYP_COORD(36, 63)`), TMPL (3×3, top row overlap) and SILO (2×1). Sizes: HPAD 2×2 full; PROC, WEAP, TMPL and FIX 3×3;
FACT 3×2; AFLD 4×2; SILO and SAM 2×1; ATWR and OBLI 1×2; GTWR and GUN 1×1.

---

## Entry notes

- **HQ** (Communications Center): TD didn't differentiate it by faction, so it's one shared entry.
- **EYE** (`STRUCT_TDEYE`, Advanced Communications Center) is GDI's superweapon host: it grants the Ion Cannon
  (`SPC_TD_ION_CANNON`, `ANIM_TD_ION_CANNON`), as the Temple grants Nod's nuke. The strike's `Explosion_Damage` gets a
  NULL source on purpose (`AnimClass::Middle`): a real source would make that Eye immune, so a player couldn't Ion
  Cannon their own Eye. The cost is that its kills aren't credited. Its **-200 power** needs an NUK2 or two NUKEs, as
  TD intended.
- **HAND** (Hand of Nod): 2×3 (`BSIZE_23`), bigger than the PYLE's 2×2.
- **OBLI** (Obelisk of Light): the -150 power drain is the design tax on the weapon; Obelisk-spam is gated by power,
  as in TD.
- **AFLD** (Nod Airstrip): Nod's vehicle factory, as TD split it (GDI builds at WEAP, Nod at AFLD); its cargo-plane
  delivery is `cargo-plane-port.md`.
- **TMPL** (`STRUCT_TDTMPL`, Temple of Nod) fires Nod's nuclear strike (`SPC_TD_NUKE`), launched like RA's Missile
  Silo (`House->NukeDest`). In `Mission_Missile`, `BULLET_NUKE_UP` uses `WARHEAD_NONE`, so its top-edge impact shows
  no explosion, and it launches 0xA0 north of centre: TD's roof opening is centred on the 3x3, where the Missile
  Silo's tunnel is NNE.
- **PROC** is the "Tiberium Refinery" and SILO the "Tiberium Silo": TD calls the refinery's output Tiberium, not ore.
- **FIX:** `[TDFIX] Name=Repair Facility` matches TD's `TXT_FIX_IT`; RA calls its own one the Service Depot.
- **FACT:** the faction yards and MCVs are `ai-upgrade-plan.md` W2 (b).
- Where each port's detail lives: TDPROC's bail trickle and dock, `harvester-docking-rework-plan.md`; TDGTWR and TDGUN,
  `td-gtwr-gun-verification.md`; TDATWR, `td-atwr-deep-dive.md`; TDOBLI's laser line and charge,
  `td-obli-verification.md`; TDSAM's eight-state launcher, `td-sam-deep-dive.md`; the power plants, barracks and
  silo, `td-tier1-verification.md`.

---

## Build times

`TechnoTypeClass::Time_To_Build` (`techno.cpp`) gives GDI and Nod houses (`ActLike` GOOD or BAD)
their own rules:
- **Buildings take TD's time:** `ticks = Cost − the free unit's cost` (TD's `Raw_Cost`), at 15 ticks a
  second, scaled by the game-speed slider. A refinery deducts its free harvester (`UNIT_HARVESTER`;
  `UNIT_TDHARV` for TDPROC, `UNIT_TSHARV` for TSPROC), a helipad the RA Longbow. Checked against the
  TD-remaster tooltips: Refinery 0:21, Weapons Factory 1:07, Comm Center 0:34, Advanced Power Plant
  0:24, Power Plant 0:11, Repair Facility 0:41, all within a second.
- **Units build at RA's base rate:** `Cost × BuildSpeedBias × TICKS_PER_MINUTE / 1000` (Cost × 0.72 in
  our rules). TD's raw-cost ticks made them about 1.39x slower than RA units of equal cost.
- **Low power and the AI's IQ slow it, as in TD:** no power makes a build take 4x as long, under half
  2.5x, under full 1.5x; a computer house with build slowdown on takes up to twice as long by its IQ.
- **Extra factories divide the time,** as they do for the RA factions: by the number of factories
  building that category (`Factory_Count`), capped at 2 when Aftermath units are on.

Every other house (Allied, Soviet, TS GDI) keeps RA's formula. In a dev build, `TF_Dev_Cheats()`
makes a human player's builds take 15 ticks, about a second; `tf_dev_off.flag` turns it off.

---
