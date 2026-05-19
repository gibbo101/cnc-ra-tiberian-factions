# Building catalogue — Tiberian Factions for Red Alert

Design spec for the new buildings we're adding via the Logic-aliased mod-building pipeline (see `docs/adding-td-buildings.md` for the per-building implementation recipe). Stats below are pulled from `tiberiandawn/bdata.cpp` — TD-authentic by default.

## Session pickup

**Current state (end of 2026-05-19 evening, v0.3.0-phase3a committed):**
- v0.3 baseline pulled from Deck into `resources/remaster_mods/Vanilla_RA/` (committed source tree).
- Manual TDNUKE entry implemented + Deck-verified end-to-end (sidebar icon, cost, TD sprite, 2×2 footprint, buildup → idle animation cycling 0-3 at TD-authentic rate, damaged variant via auto-shift to shapes 4-7, sell/destroy spawns crew).
- Master flag table below is the v0.3 source of truth with TD-authentic flags per building.
- Recipe doc (`docs/adding-td-buildings.md`) has v0.3 lessons section covering: IniName collisions, damaged-shape auto-derivation, Anims inheritance gap, Crewed/Repairable per-section requirement.

**Two open threads parked for next session:**

1. **AI doesn't target TDNUKE for destruction** (highest priority). Suspected cause: AI threat-assessment / target-eval loops use `STRUCTF_*` enum flags or specific BuildingType heuristics that mod-typed entries (Type past `STRUCT_COUNT`) don't match. Logic= aliases the Type discriminant to POWR's, which *should* make heuristics pick it up — verify by tracing `HouseClass::AI_Building`, `TargetClass` evaluation, and threat-region scoring. Likely a piece of work — could span the whole next session. Worth its own investigation before writing the script (the AI fix may affect catalogue layout decisions).

2. **`scripts/add_building.py`** — manifest-driven, keyed off the master table below. Smoke-test on TDNUK2 migration (Phase-1 POC → TD-authentic values per master table). Then run for GDI catalogue: TDPYLE, TDHQ, TDWEAP, TDFIX, TDGTWR, TDATWR, TDHPAD, TDEYE.

**Testbed state on the Deck (`Red_Alert/tiberian-factions-emc-test/`):**
- v0.3 DLL + TDNUKE deployed and verified.
- `Red_Alert/Vanilla_RA/` is the intended v0.3 final deploy path; the testbed remains for rapid iteration.

---

## Master flag table (TD-authentic, v0.3 source of truth)

Per-building flags extracted from `tiberiandawn/bdata.cpp`. These are the values `add_building.py` reads. **IniName** is the catalogue IniName (TD-prefixed); **Image/Footprint/sprite ZIPs** keep the unprefixed TD asset names.

| IniName | Faction | Donor | Cost | Power | HP | Sight | Adj | Armor | Bib | Cap | Crew | Repair | Idle:Start/Count/Rate | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TDNUKE | both  | POWR | 300  | +100 | 200  | 2 | 1 | wood     | yes | yes | yes | yes | 0/4/15  | TD lvl 0 |
| TDNUK2 | both  | APWR | 700  | +200 | 300  | 2 | 1 | wood     | yes | yes | yes | yes | 0/4/15  | TD lvl 5, prereq TDNUKE |
| TDPROC | both  | PROC | 2000 | -40  | 900  | 4 | 1 | wood     | yes | yes | yes | yes | 0/6/4   | TD lvl 1, has dock/siphon cycles — keep RA donor behaviour |
| TDSILO | both  | SILO | 150  | -10  | 300  | 2 | 1 | wood     | yes | yes | no  | yes | —       | TD lvl 1 — capacity-based shape, not a cycle |
| TDPYLE | GDI   | TENT | 300  | -20  | 800  | 3 | 1 | wood     | yes | yes | yes | yes | 0/10/3  | TD lvl 0 |
| TDHAND | Nod   | BARR | 300  | -20  | 800  | 3 | 1 | wood     | yes | yes | yes | yes | 0/10/3  | TD lvl 0, 2×3 footprint |
| TDWEAP | GDI   | WEAP | 2000 | -30  | 1000 | 3 | 1 | aluminum | yes | yes | yes | yes | 0/1/0   | TD lvl 2, static idle |
| TDAFLD | Nod   | WEAP | 2000 | -30  | 1000 | 5 | 1 | steel    | yes | yes | yes | yes | 0/16/3  | TD lvl 2, 4×2, AIRSTRIP anim spec |
| TDHQ   | both  | DOME | 1000 | -40  | 1000 | 10| 1 | wood     | yes | yes | yes | yes | 0/16/4  | TD lvl 2, radar |
| TDEYE  | GDI   | MSLO | 2800 | -200 | 500  | 10| 1 | wood     | yes | **no** | yes | yes | 0/16/4 | TD lvl 7, GDI superweapon host |
| TDTMPL | Nod   | MSLO | 3000 | -150 | 1000 | 4 | 1 | aluminum | yes | **no** | yes | yes | 0/1/0  | TD lvl 7, Nod superweapon host |
| TDFIX  | both  | FIX  | 1200 | -30  | 800  | 3 | 1 | wood     | yes | yes | yes | yes | 0/1/0   | TD lvl 5, ACTIVE 0/7/2 |
| TDHPAD | both  | HPAD | 1500 | -10  | 800  | 3 | 1 | wood     | yes | yes | **no** | yes | 0/0/0 | TD lvl 6, no idle anim |
| TDGTWR | GDI   | PBOX | 500  | -10  | 200  | 3 | 1 | wood     | no  | **no** | yes | yes | —     | TD lvl 2, 1×1 |
| TDATWR | GDI   | AGUN | 1000 | -20  | 300  | 4 | 1 | aluminum | no  | **no** | yes | yes | —     | TD lvl 4, 1×2 |
| TDOBLI | Nod   | TSLA | 1500 | -150 | 200  | 5 | 1 | aluminum | no  | **no** | yes | yes | —     | TD lvl 4, 1×2, ACTIVE 0/4/RATE |
| TDGUN  | Nod   | GUN  | 600  | -20  | 200  | 5 | 1 | steel    | no  | **no** | yes | yes | —     | TD lvl 2, 1×1 |
| TDSAM  | Nod   | SAM  | 750  | -20  | 200  | 3 | 1 | steel    | no  | **no** | **no** | yes | — | TD lvl 6, 2×1, turret-based |
| TDFACT | both  | FACT | 5000 | -30  | 400  | 3 | 1 | wood     | yes | yes | yes | yes | 0/4/3   | TD lvl 99, ACTIVE 4/20/3 — closing v0.3 slice |

**Reading the table:**
- Empty `Idle` column = no idle animation (engine renders shape 0 statically). Damaged state = shape 1 in that case (the engine's `largest = max(Anims[*].Start + Count) = 1` auto-shift).
- `Crew=no` means selling/destroying spawns zero infantry (TD canon for SILO/HPAD/SAM).
- `Cap=no` (bold) marks entries where TD authentic differs from the original catalogue spec — defensive structures and superweapon hosts can't be captured. **TMPL and EYE are NOT capturable per TD.**
- Logic= aliases the engine donor; field overrides come via rules.ini per the recipe.

---


**Status legend:** ✅ built & verified on Deck · 🔨 implemented, untested · 📝 designed, not yet built · ❓ open design question · 🚧 needs engine work

**Visual reference:** `~/Desktop/cnc-buildings/{TD,RA}/` — idle-frame PNGs.

**TD prereq → RA Prerequisite= mapping:**

| TD prereq enum | Means | Our entry uses |
|---|---|---|
| STRUCTF_NONE | nothing | (omit field) |
| STRUCTF_POWER | NUKE | `Prerequisite=NUKE` |
| STRUCTF_BARRACKS | PYLE (GDI) / HAND (Nod) | `Prerequisite=PYLE` or `HAND` per faction |
| STRUCTF_REFINERY | PROC | `Prerequisite=PROC` |
| STRUCTF_RADAR | HQ | `Prerequisite=HQ` |
| STRUCTF_HOSPITAL | HOSP | `Prerequisite=HOSP` |

---

## Donor cheat-sheet (RA buildings → engine behaviour)

| Donor | Role / behaviour | Notes |
|---|---|---|
| POWR | Power plant — generates power | |
| APWR | Advanced Power Plant — bigger generator | 3×3 footprint by default — override |
| TENT | Allied Barracks — infantry production | |
| BARR | Soviet Barracks — infantry production | |
| PROC | Ore Refinery — spawns free Ore Truck on build | |
| SILO | Ore Silo — increases credit cap | |
| WEAP | War Factory — vehicle production | |
| HPAD | Helipad — helicopter production / landing | |
| DOME | Radar Dome — map reveal, tech prereq | |
| FIX | Service Depot — vehicle repair | |
| FACT | Construction Yard — building production | tied to MCV deploy |
| ATEK | Allied Tech Center | |
| STEK | Soviet Tech Center | |
| GUN | Allied Turret — anti-vehicle | powered |
| PBOX | Allied Pillbox — anti-infantry | manned by GI |
| FTUR | Soviet Flame Turret — anti-infantry | |
| TSLA | Tesla Coil — heavy anti-everything | power-hungry |
| SAM | RA SAM Site — anti-air | |
| AGUN | Anti-Aircraft Gun — fast AA | |
| MSLO | Missile Silo (superweapon — Atom Bomb) | |
| IRON | Iron Curtain (superweapon — invuln beam) | |
| PDOX | Chronosphere (superweapon — teleport) | |
| AFLD | Airfield (Soviet vehicle delivery via plane) | |

---

## Per-entry sections — design rationale

The sections below capture **design rationale and donor choice** for each catalogue entry. The flag values shown in per-entry field tables are illustrative — the **master flag table above is the canonical source** the script reads. Where they disagree, the master table wins.

Entry names below use the TD asset name (e.g. "PYLE", "HAND") for readability; the actual IniName in rules.ini is TD-prefixed (`TDPYLE`, `TDHAND`, etc.) to avoid the vanilla-RA collision class documented in `docs/adding-td-buildings.md`.

---

## GDI catalogue

GDI: Allied-flavoured engine donors where there's a choice. Armoured, ordered, Western.

### PYLE — GDI Barracks 📝
Faction: GDI · Donor: **TENT** (Allied barracks) · TD lvl 0, $300, -20 power, 400 HP, 2×2 wood, prereq NUKE

| Field | Value |
|---|---|
| Logic= | TENT |
| Image= | PYLE |
| Footprint= | PYLE (2×2, to add) |
| Name= | Barracks |
| TechLevel | 0 |
| Prerequisite | NUKE |
| Owner= | GoodGuy |
| Cost | 300 |
| Power | -20 |
| Strength | 400 |
| Armor | wood |
| Sight | 3 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

**Note:** GDI inherits Allied infantry roster (GI, Rocket Soldier, Engineer, Medic, Spy, Tanya) via the TENT donor for v0.3. Custom GDI infantry types are v0.4+.

### HPAD — Helipad 📝
Faction: **both** · Donor: **HPAD** · TD lvl 6, $1500, -10 power, 400 HP, 2×2 wood, prereq Barracks

| Field | Value |
|---|---|
| Logic= | HPAD |
| Image= | HPAD |
| Footprint= | HPAD (2×2) |
| Name= | Helipad |
| TechLevel | 6 |
| Prerequisite | PYLE\|HAND |
| Owner= | GoodGuy,BadGuy |
| Cost | 1500 |
| Power | -10 |
| Strength | 400 |
| Armor | wood |
| Sight | 3 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

**Note:** Both factions share HPAD per TD canon (GDI Orca, Nod Apache). Helicopter roster inherits from HPAD donor — RA Longbow for Allied-side, Hind for Soviet-side. TD-flavoured helicopters land in v0.4 with the unit roster work.

### HQ — Communications Center / Radar 📝
Faction: **both** · Donor: **DOME** · TD lvl 2, $1000, -40 power, 500 HP, 2×2 wood, sight **10**, prereq PROC

| Field | Value |
|---|---|
| Logic= | DOME |
| Image= | HQ |
| Footprint= | HQ (2×2) |
| Name= | Communications Center |
| TechLevel | 2 |
| Prerequisite | PROC |
| Owner= | GoodGuy,BadGuy |
| Cost | 1000 |
| Power | -40 |
| Strength | 500 |
| Armor | wood |
| Sight | 10 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

**Note:** TD didn't differentiate visually — both factions shared HQ. Single shared entry.

### EYE — Advanced Communications Center (hosts Ion Cannon) 📝 🚧
Faction: GDI · Donor: **MSLO** (RA Missile Silo — for superweapon hosting) · TD lvl 7, $2800, -**200** power, 500 HP, 2×2 wood, sight 10, prereq HQ

| Field | Value |
|---|---|
| Logic= | MSLO |
| Image= | EYE |
| Footprint= | EYE (2×2) |
| Name= | Advanced Communications Center |
| TechLevel | 7 |
| Prerequisite | HQ |
| Owner= | GoodGuy |
| Cost | 2800 |
| Power | -200 |
| Strength | 500 |
| Armor | wood |
| Sight | 10 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

**Design (2026-05-19):** EYE is GDI's superweapon host — building it grants the Ion Cannon strike. Mirrors Nod's TMPL (Temple of Nod hosts nuclear strike). Use Logic=MSLO so the engine grants a generic superweapon timer/picker.

**🚧 v0.3 caveat:** MSLO's default superweapon is the Atom Bomb visual (mushroom cloud). The actual Ion Cannon beam-strike effect is a separate engine implementation in v0.4. For v0.3, EYE grants a working superweapon with placeholder visuals — the mechanic works, the art doesn't match yet.

**-200 power drain** is huge — players will need NUK2 (or two NUKEs) to support EYE. TD's design intent.

### GTWR — Guard Tower 📝
Faction: GDI · Donor: **PBOX** (Allied Pillbox) · TD lvl 2, $500, -10 power, 200 HP, **1×1** wood, prereq PYLE

| Field | Value |
|---|---|
| Logic= | PBOX |
| Image= | GTWR |
| Footprint= | GTWR (1×1, to add) |
| Name= | Guard Tower |
| TechLevel | 2 |
| Prerequisite | PYLE |
| Owner= | GoodGuy |
| Cost | 500 |
| Power | -10 |
| Strength | 200 |
| Armor | wood |
| Sight | 3 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | no (1×1 = no bib) |

### ATWR — Advanced Guard Tower 📝
Faction: GDI · Donor: **AGUN** (Anti-Aircraft Gun) or **GUN** · TD lvl 4, $1000, -20 power, 300 HP, **1×2** aluminum, prereq HQ

| Field | Value |
|---|---|
| Logic= | AGUN |
| Image= | ATWR |
| Footprint= | ATWR (1×2, to add) |
| Name= | Advanced Guard Tower |
| TechLevel | 4 |
| Prerequisite | HQ |
| Owner= | GoodGuy |
| Cost | 1000 |
| Power | -20 |
| Strength | 300 |
| Armor | aluminum |
| Sight | 4 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | no |

**Donor choice:** TD's ATWR fires rockets at both ground & air. AGUN (anti-air only) is closer to the "anti-air rocket" feel. Alternative: GUN (anti-vehicle gun) for a pure anti-ground tower. Pick **AGUN** as default — TD's ATWR was anti-air-capable.

---

## Nod catalogue

Nod: Soviet-flavoured engine donors. Aggressive, asymmetric, distinctive defence.

### HAND — Hand of Nod (barracks) 📝
Faction: Nod · Donor: **BARR** (Soviet barracks) · TD lvl 0, $300, -20 power, 400 HP, **2×3** wood, prereq NUKE

| Field | Value |
|---|---|
| Logic= | BARR |
| Image= | HAND |
| Footprint= | HAND (2×3, to add — bigger than PYLE) |
| Name= | Hand of Nod |
| TechLevel | 0 |
| Prerequisite | NUKE |
| Owner= | BadGuy |
| Cost | 300 |
| Power | -20 |
| Strength | 400 |
| Armor | wood |
| Sight | 3 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

**Note:** Footprint is 2×3 (BSIZE_23) — bigger than PYLE's 2×2. Nod barracks: Conscript, Grenadier, Engineer, Spy, Tesla Trooper, Flamethrower via BARR donor.

### GUN — Nod Gun Turret 📝
Faction: Nod · Donor: **GUN** (Allied Turret) · TD lvl 2, $600, -20 power, 200 HP, **1×1** steel, prereq HAND

| Field | Value |
|---|---|
| Logic= | GUN |
| Image= | GUN |
| Footprint= | GUN (1×1) |
| Name= | Nod Turret |
| TechLevel | 2 |
| Prerequisite | HAND |
| Owner= | BadGuy |
| Cost | 600 |
| Power | -20 |
| Strength | 200 |
| Armor | steel |
| Sight | 5 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | no |

**Note:** Same IniName as RA's GUN — but our entry shadows the donor via Logic=. Display name disambiguates ("Nod Turret" vs "Turret").

### SAM — SAM Site (Nod anti-air) 📝
Faction: Nod · Donor: **SAM** (RA's own SAM) · TD lvl 6, $750, -20 power, 200 HP, **2×1** steel, prereq HAND

| Field | Value |
|---|---|
| Logic= | SAM |
| Image= | SAM |
| Footprint= | SAM (2×1) |
| Name= | SAM Site |
| TechLevel | 6 |
| Prerequisite | HAND |
| Owner= | BadGuy |
| Cost | 750 |
| Power | -20 |
| Strength | 200 |
| Armor | steel |
| Sight | 3 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | no |

**Donor choice:** SAM (donor = SAM) makes the engine pop-up missile launcher fire. Alternative: AGUN for continuous fire. Stick with SAM-as-donor for the iconic pop-up feel.

### OBLI — Obelisk of Light 📝
Faction: Nod · Donor: **TSLA** · TD lvl 4, $1500, -**150** power, 200 HP, **1×2** aluminum, prereq HQ

| Field | Value |
|---|---|
| Logic= | TSLA |
| Image= | OBLI |
| Footprint= | OBLI (1×2, to add) |
| Name= | Obelisk of Light |
| TechLevel | 4 |
| Prerequisite | HQ |
| Owner= | BadGuy |
| Cost | 1500 |
| Power | -150 |
| Strength | 200 |
| Armor | aluminum |
| Sight | 5 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | no |

**Note:** -150 power drain is the design tax for the devastating weapon. Matches TD's design — Obelisk-spam is gated by power.

### AFLD — Nod Airstrip (vehicle factory with cargo-plane delivery) 📝 🚧
Faction: Nod · Donor: **WEAP** (TD's Airstrip is Nod's vehicle factory) · TD lvl 2, $2000, -30 power, 500 HP, **4×2** steel, prereq PROC, **is_factory=yes**

| Field | Value |
|---|---|
| Logic= | WEAP |
| Image= | AFLD |
| Footprint= | AFLD (4×2, to add — big!) |
| Name= | Nod Airstrip |
| TechLevel | 2 |
| Prerequisite | PROC |
| Owner= | BadGuy |
| Cost | 2000 |
| Power | -30 |
| Strength | 500 |
| Armor | steel |
| Sight | 5 |
| Adjacent | 1 |
| Factory | yes |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

**Design (2026-05-19):** TD-faithful split — GDI=WEAP, Nod=AFLD. Both Logic=WEAP so both behave as vehicle factories. Same vehicle roster (whatever WEAP donor produces) until v0.4 brings TD-flavoured tanks.

**Engine work needed (scoped for v0.3, in Nod's portion of the build):**

1. **Exit cell for 4×2 footprint.** WEAP's `ExitList[0]` offset assumes a 3×3 footprint and lands south of row 2. For AFLD's 4×2 it may land inside or beyond the AFLD cells. Test first — if WEAP's offset works for 4×2 (lucky alignment), no change needed. If not, add an `ExitList=` rules.ini override field analogous to the existing `Footprint=` pipeline (1 small DLL change in `BuildingTypeClass::Read_INI`).

2. **Cargo plane delivery mechanic.** Replace the "vehicle teleports to exit coord" behaviour with TD-style "cargo plane flies in → lands → vehicle drives off → plane departs." Engine work in `BuildingClass::Exit_Object` (`redalert/building.cpp:2030`):
   - Add a check at the start of `case STRUCT_WEAP` (or earlier): if the BuildingTypeClass has an `IsAirDelivered=yes` flag (new rules.ini field), take the air-delivery path instead.
   - Air-delivery path: spawn a cargo aircraft (new TD AircraftType, donor=BADGER or new) at the closest map edge, carrying the unit as cargo. Aircraft mission flies to the AFLD's center cell, lands (similar to HPAD's `Helper_Find_Cell` for helicopter landing), unloads the vehicle (similar to existing transport-unload code), then takes off and exits the map.
   - Plumbing: `AircraftClass::Paradrop_Cargo` exists for infantry; vehicle delivery follows the same general arc but needs new code for the "land and unload vehicle" step (RA's Hind/Chinook transport unload is the closest existing path).
   - Asset: TD's cargo plane sprite (`CARGO.ZIP` from `TEXTURES_TD_SRGB.MEG`).

**Timing:** Don't block. GDI catalogue (NUKE/NUK2/PYLE/HQ/EYE/WEAP/FIX/GTWR/ATWR/HPAD) ships first using the existing Logic-aliased pipeline. When we move into Nod's portion (HAND/GUN/SAM/OBLI/TMPL), AFLD becomes its own focused slice with the two engine pieces above. Estimated 1-2 sessions for the air-delivery work, then AFLD plugs in like any other catalogue entry.

### TMPL — Temple of Nod (superweapon) 📝 🚧
Faction: Nod · Donor: **MSLO** (RA Missile Silo) · TD lvl 7, $3000, -150 power, **1000** HP, 3×3 aluminum, prereq HQ

| Field | Value |
|---|---|
| Logic= | MSLO |
| Image= | TMPL |
| Footprint= | TMPL (3×3, to add) |
| Name= | Temple of Nod |
| TechLevel | 7 |
| Prerequisite | HQ |
| Owner= | BadGuy |
| Cost | 3000 |
| Power | -150 |
| Strength | 1000 |
| Armor | aluminum |
| Sight | 4 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

**Note:** TMPL fires Nod's nuclear strike in TD. MSLO is RA's Atom Bomb (functionally identical superweapon — long cooldown, launch animation, target picker). 🚧 because superweapon behaviour through Logic= aliasing isn't verified.

---

## Shared (both factions) catalogue

Production-chain buildings without strong faction-identity differences.

### NUKE — Power Plant (tier 1) 📝
Faction: **both** · Donor: **POWR** · TD lvl 0, $300, +100 power, 200 HP, 2×2 wood

| Field | Value |
|---|---|
| Logic= | POWR |
| Image= | NUKE |
| Footprint= | NUKE (2×2, to add — same shape as NUK2) |
| Name= | Power Plant |
| TechLevel | 0 |
| Owner= | GoodGuy,BadGuy |
| Cost | 300 |
| Power | +100 |
| Strength | 200 |
| Armor | wood |
| Sight | 2 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

### NUK2 — Advanced Power Plant (tier 2) ✅→📝
Faction: **both** · Donor: **APWR** (was POWR in POC) · TD lvl 5, $700, +200 power, 300 HP, 2×2 wood, prereq NUKE

| Field | POC value | TD-authentic target |
|---|---|---|
| Logic= | POWR | **APWR** |
| Image= | NUK2 | NUK2 |
| Footprint= | NUK2 | NUK2 |
| Name= | GDIPowerPlant | Advanced Power Plant |
| TechLevel | 1 | **5** |
| Prerequisite | — | **NUKE** |
| Owner= | GoodGuy | **GoodGuy,BadGuy** |
| Cost | 350 | **700** |
| Power | +100 | **+200** |
| Strength | 400 | **300** |
| Armor | wood | wood |
| Sight | 3 | 2 |

**Status:** POC verified on Deck. Migration to TD-authentic values is a v0.3 task — covered when we run the buildout.

### PROC — Refinery 📝
Faction: **both** · Donor: **PROC** · TD lvl 1, $2000, -40 power, 450 HP, 3×3 wood, prereq NUKE

| Field | Value |
|---|---|
| Logic= | PROC |
| Image= | PROC |
| Footprint= | PROC (3×3) |
| Name= | Tiberium Refinery |
| TechLevel | 1 |
| Prerequisite | NUKE |
| Owner= | GoodGuy,BadGuy |
| Cost | 2000 |
| Power | -40 |
| Strength | 450 |
| Armor | wood |
| Sight | 4 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

**Note:** TD calls the refinery's output "Tiberium" rather than "Ore". Display name reflects that.

### SILO — Ore Silo 📝
Faction: **both** · Donor: **SILO** · TD lvl 1, $150, -10 power, 150 HP, 2×1 wood, prereq PROC

| Field | Value |
|---|---|
| Logic= | SILO |
| Image= | SILO |
| Footprint= | SILO (2×1) |
| Name= | Tiberium Silo |
| TechLevel | 1 |
| Prerequisite | PROC |
| Owner= | GoodGuy,BadGuy |
| Cost | 150 |
| Power | -10 |
| Strength | 150 |
| Armor | wood |
| Sight | 2 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

### WEAP — Weapons Factory (GDI vehicle factory) 📝
Faction: **GDI** · Donor: **WEAP** · TD lvl 2, $2000, -30 power, 500 HP, **3×3** aluminum, prereq PROC

| Field | Value |
|---|---|
| Logic= | WEAP |
| Image= | WEAP |
| Footprint= | WEAP (3×3) |
| Name= | Weapons Factory |
| TechLevel | 2 |
| Prerequisite | PROC |
| Owner= | GoodGuy |
| Cost | 2000 |
| Power | -30 |
| Strength | 500 |
| Armor | aluminum |
| Sight | 3 |
| Adjacent | 1 |
| Factory | yes |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

**Note:** TD-faithful: GDI builds vehicles here, Nod builds at AFLD. Both Logic=WEAP, both produce the same vehicle roster until v0.4's TD vehicle work.

### FIX — Service Depot 📝
Faction: **both** · Donor: **FIX** · TD lvl 5, $1200, -30 power, 400 HP, 3×3 wood, prereq NUKE

| Field | Value |
|---|---|
| Logic= | FIX |
| Image= | FIX |
| Footprint= | FIX (3×3) |
| Name= | Service Depot |
| TechLevel | 5 |
| Prerequisite | NUKE |
| Owner= | GoodGuy,BadGuy |
| Cost | 1200 |
| Power | -30 |
| Strength | 400 |
| Armor | wood |
| Sight | 3 |
| Adjacent | 1 |
| BaseNormal | yes |
| Capturable | true |
| Bib | yes |

### FACT — Construction Yard (paired with TD MCV) 📝 🚧
Faction: **both, split into GDI / Nod variants** · Donor: **FACT** · TD lvl 99 (MCV deploys into it), $5000, -30 power, 400 HP, 3×2 wood

| Field | GDIFACT | NODFACT |
|---|---|---|
| Logic= | FACT | FACT |
| Image= | FACT (TD art) | FACT (TD art — same — visual differentiation via remap colour) |
| Footprint= | FACT (3×2) | FACT (3×2) |
| Name= | Construction Yard | Construction Yard |
| TechLevel | 99 | 99 |
| Owner= | GoodGuy | BadGuy |
| Cost | 5000 | 5000 |
| Power | -30 | -30 |
| Strength | 400 | 400 |
| Armor | wood | wood |
| Sight | 3 | 3 |

**Direction (locked 2026-05-19):** v0.3 builds out the standalone TD buildings first, then closes with the MCV+CY pair as the final v0.3 slice. We can't keep starting in a vanilla RA con yard — the visual mismatch is too jarring once the rest of the base is TD-themed.

**Sequencing:** TD buildings (NUKE, NUK2, PROC, SILO, PYLE, HAND, HQ, WEAP, AFLD, EYE, TMPL, FIX, GTWR, ATWR, OBLI, GUN, SAM, HPAD) → then MCV/CY pair → ship v0.3.

**Engine work for MCV/CY pair (v0.3 closing slice):**
- Add `GDIMCV` / `NODMCV` unit types via the Logic-aliased pipeline (extends pipeline from BuildingType to UnitType — pipeline hasn't been validated for units yet, that's prereq work).
- Modify MCV deploy logic so it creates the faction-appropriate CY type by reading Owner (or a new field on UnitTypeClass like `DeploysInto=`).
- Modify initial-units placement in `house.cpp` so GDI/Nod players start with their respective MCV instead of the vanilla one.
- New CY entries above are then the deploy targets.

This is one cohesive slice — likely a 1-2 session implementation.

---

## Skipped for v0.3 (revisit later)

- **HOSP** — Hospital. TD lvl 99 (not normally buildable). Skip.
- **BIO** — Bio Lab. TD lvl 99 (not normally buildable). Skip.
- **ARCO** — Tanker. TD lvl 99, $0. Civilian/scenery. Skip.

---

## Walkthrough status

| IniName | Faction | Donor | Stats? | Status |
|---|---|---|---|---|
| TDNUKE | both | POWR | ✓ | ✅ manual ref impl 2026-05-19 |
| TDNUK2 | both | APWR | ✓ | ✅ (Phase-1 POC) → 📝 migrate to TD-authentic |
| TDPROC | both | PROC | ✓ | 📝 |
| TDSILO | both | SILO | ✓ | 📝 |
| TDPYLE | GDI | TENT | ✓ | 📝 |
| TDHAND | Nod | BARR | ✓ | 📝 |
| TDHPAD | both | HPAD | ✓ | 📝 |
| TDWEAP | GDI | WEAP | ✓ | 📝 |
| TDAFLD | Nod | WEAP | ✓ | 📝 🚧 (cargo-plane engine slice within Nod buildout) |
| TDHQ | both | DOME | ✓ | 📝 |
| TDEYE | GDI | MSLO | ✓ | 📝 🚧 (Ion Cannon visual v0.4) |
| TDTMPL | Nod | MSLO | ✓ | 📝 🚧 |
| TDFIX | both | FIX | ✓ | 📝 |
| TDGTWR | GDI | PBOX | ✓ | 📝 |
| TDATWR | GDI | AGUN | ✓ | 📝 |
| TDOBLI | Nod | TSLA | ✓ | 📝 |
| TDGUN | Nod | GUN | ✓ | 📝 |
| TDSAM | Nod | SAM | ✓ | 📝 |
| TDFACT | both (split) | FACT | ✓ | 📝 🚧 v0.3 closing slice |
| TDGDIMCV / TDNODMCV | per faction | MCV (unit) | — | 📝 🚧 paired with TDFACT |
| HOSP/BIO/ARCO | — | — | — | skip for v0.3 |

---

## Design decisions log

All seven of the original open questions were resolved 2026-05-19:

1. ✅ **HPAD** — both factions share, Owner=GoodGuy,BadGuy.
2. ✅ **HQ** — both factions share, Owner=GoodGuy,BadGuy.
3. ✅ **WEAP/AFLD vehicle factory** — TD-faithful split. GDI=WEAP, Nod=AFLD, both Logic=WEAP. Nod's cargo-plane delivery is a 🚧 sub-task.
4. ✅ **Infantry rosters** — v0.3 accepts donor rosters (GDI=Allied infantry via TENT, Nod=Soviet infantry via BARR). TD-flavoured infantry types come in v0.4 using the Logic-aliased pipeline extended to InfantryType.
5. ✅ **Vehicle rosters** — same approach as #4. v0.3 uses WEAP donor roster; TD vehicles in v0.4. **Exception: MCV** — needed in v0.3 to pair with the TD CY.
6. ✅ **GDI superweapon** — Ion Cannon, hosted on EYE (Logic=MSLO). Placeholder mushroom-cloud visual in v0.3; proper Ion Cannon beam in v0.4.
7. ✅ **Walls** — reuse vanilla RA walls (SBAG/CYCL/BRIK/FENC) for v0.3.

## v0.3 implementation sequence

1. **GDI catalogue buildings** — NUKE, NUK2, PYLE, HQ, WEAP, FIX, GTWR, ATWR, HPAD, EYE. Pure content; use existing Logic-aliased pipeline. Helper script worth writing here.
2. **Nod catalogue buildings + AFLD engine slice** — HAND, GUN, SAM, OBLI, TMPL, plus the AFLD air-delivery engine work (ExitList override + cargo-plane mechanic in `Exit_Object`). AFLD is the Nod vehicle factory, so it lands with the rest of Nod's tree.
3. **TD MCV/CY pair (closing slice)** — adds Logic-aliased UnitType support, GDI/Nod MCV variants, faction-aware deploy logic, faction-specific CYs.
4. **v0.3 release** — TD-themed bases, fully playable skirmish on the Deck, vanilla-RA art only on infantry/non-Nod vehicles. Workshop publish (or wait until v0.4).

## v0.4+ roadmap (not yet specced)

- TD-themed infantry per faction (Minigunner, Engineer, Grenadier, Flamethrower, etc.).
- TD-themed vehicles per faction (Light Tank, Medium Tank, Mammoth Tank, Buggy, Recon Bike, etc.).
- Ion Cannon proper visual effect (engine work).
- TD-themed walls (if v0.3's vanilla-walls compromise feels wrong).
- TD-themed Hospital / Bio Lab if there's player demand.

---

## Footprint presets — ready to paste into `redalert/bdata.cpp`

Each TD building needs a `Footprint=` preset registered in the `_presets[]` table in `BuildingTypeClass::Read_INI` (currently around line 3780). The shapes below are decoded from `tiberiandawn/bdata.cpp` — TD uses `MCW` (Map Cell Width), RA's equivalent is `MAP_CELL_W`. Substitution is mechanical.

**Shared shapes:** HQ, EYE, NUKE, NUK2 all share the same 2×2 L-shape (3-cell occupy + 1-cell overlap). GTWR and GUN share 1×1. ATWR and OBLI share 1×2.

### Static array declarations

```cpp
// 2×2 L-shape (3 occupied + 1 visual overlap) — shared by NUKE, NUK2, HQ, EYE
static short const List_NUK2_OCCUPY[]  = {0, MAP_CELL_W, MAP_CELL_W + 1, REFRESH_EOL};        // existing
static short const List_NUK2_OVERLAP[] = {1, REFRESH_EOL};                                     // existing
// (NUKE/HQ/EYE can reference these directly via aliasing in _presets[].)

// 2×2 split (top occupied, bottom overlap) — PYLE
static short const List_PYLE_OCCUPY[]  = {0, 1, REFRESH_EOL};
static short const List_PYLE_OVERLAP[] = {MAP_CELL_W, MAP_CELL_W + 1, REFRESH_EOL};

// 2×3 — HAND (Nod barracks, bigger than PYLE)
static short const List_HAND_OCCUPY[]  = {MAP_CELL_W, MAP_CELL_W + 1, MAP_CELL_W * 2 + 1, REFRESH_EOL};
static short const List_HAND_OVERLAP[] = {0, 1, MAP_CELL_W * 2, MAP_CELL_W, REFRESH_EOL};

// 2×2 full-fill — HPAD
static short const List_HPAD_OCCUPY[]  = {0, 1, MAP_CELL_W, MAP_CELL_W + 1, REFRESH_EOL};

// 3×3 — PROC, WEAP, TMPL, FIX (different shapes per building)
static short const List_PROC_OCCUPY[]  = {1, MAP_CELL_W, MAP_CELL_W + 1, MAP_CELL_W + 2, REFRESH_EOL};
static short const List_PROC_OVERLAP[] = {0, 2, MAP_CELL_W * 2, MAP_CELL_W * 2 + 1, MAP_CELL_W * 2 + 2, REFRESH_EOL};

static short const List_WEAP_OCCUPY[]  = {MAP_CELL_W, MAP_CELL_W + 1, MAP_CELL_W + 2,
                                          MAP_CELL_W * 2, MAP_CELL_W * 2 + 1, MAP_CELL_W * 2 + 2, REFRESH_EOL};
static short const List_WEAP_OVERLAP[] = {0, 1, 2, REFRESH_EOL};

static short const List_TMPL_OCCUPY[]  = {MAP_CELL_W, MAP_CELL_W + 1, MAP_CELL_W + 2,
                                          MAP_CELL_W * 2, MAP_CELL_W * 2 + 1, MAP_CELL_W * 2 + 2, REFRESH_EOL};
static short const List_TMPL_OVERLAP[] = {0, 1, 2, REFRESH_EOL};

static short const List_FIX_OCCUPY[]   = {1, MAP_CELL_W, MAP_CELL_W + 1, MAP_CELL_W + 2,
                                          MAP_CELL_W + MAP_CELL_W + 1, REFRESH_EOL};
static short const List_FIX_OVERLAP[]  = {0, 2, MAP_CELL_W + MAP_CELL_W, MAP_CELL_W + MAP_CELL_W + 2, REFRESH_EOL};

// 3×2 — FACT (note: opposite orientation from 2×3 HAND)
static short const List_FACT_OCCUPY[]  = {0, 1, 2, MAP_CELL_W, MAP_CELL_W + 1, MAP_CELL_W + 2, REFRESH_EOL};

// 4×2 — AFLD (big!)
static short const List_AFLD_OCCUPY[]  = {0, 1, 2, 3, MAP_CELL_W, MAP_CELL_W + 1, MAP_CELL_W + 2, MAP_CELL_W + 3, REFRESH_EOL};

// 2×1 — SILO, SAM
static short const List_SILO_OCCUPY[]  = {0, 1, REFRESH_EOL};

static short const List_SAM_OCCUPY[]   = {0, 1, REFRESH_EOL};
static short const List_SAM_OVERLAP[]  = {-MAP_CELL_W, -(MAP_CELL_W - 1), REFRESH_EOL};
// ⚠️ SAM's overlap uses NEGATIVE offsets — extends above the bounding box. Verify renderer handles this in RA.

// 1×2 — ATWR, OBLI
static short const List_ATWR_OCCUPY[]  = {MAP_CELL_W, REFRESH_EOL};
static short const List_ATWR_OVERLAP[] = {0, REFRESH_EOL};

// 1×1 — GTWR, GUN
static short const List_1x1_OCCUPY[]   = {0, REFRESH_EOL};
```

### `_presets[]` table entries

```cpp
static FootprintPreset const _presets[] = {
    {"NUKE", BSIZE_22, List_NUK2_OCCUPY,  List_NUK2_OVERLAP},   // shares NUK2's L-shape
    {"NUK2", BSIZE_22, List_NUK2_OCCUPY,  List_NUK2_OVERLAP},   // existing
    {"HQ",   BSIZE_22, List_NUK2_OCCUPY,  List_NUK2_OVERLAP},   // shares NUK2's L-shape
    {"EYE",  BSIZE_22, List_NUK2_OCCUPY,  List_NUK2_OVERLAP},   // shares NUK2's L-shape
    {"PYLE", BSIZE_22, List_PYLE_OCCUPY,  List_PYLE_OVERLAP},
    {"HAND", BSIZE_23, List_HAND_OCCUPY,  List_HAND_OVERLAP},
    {"HPAD", BSIZE_22, List_HPAD_OCCUPY,  NULL},
    {"PROC", BSIZE_33, List_PROC_OCCUPY,  List_PROC_OVERLAP},
    {"WEAP", BSIZE_33, List_WEAP_OCCUPY,  List_WEAP_OVERLAP},
    {"TMPL", BSIZE_33, List_TMPL_OCCUPY,  List_TMPL_OVERLAP},
    {"FIX",  BSIZE_33, List_FIX_OCCUPY,   List_FIX_OVERLAP},
    {"FACT", BSIZE_32, List_FACT_OCCUPY,  NULL},
    {"AFLD", BSIZE_42, List_AFLD_OCCUPY,  NULL},
    {"SILO", BSIZE_21, List_SILO_OCCUPY,  NULL},
    {"SAM",  BSIZE_21, List_SAM_OCCUPY,   List_SAM_OVERLAP},
    {"ATWR", BSIZE_12, List_ATWR_OCCUPY,  List_ATWR_OVERLAP},
    {"OBLI", BSIZE_12, List_ATWR_OCCUPY,  List_ATWR_OVERLAP},   // shares ATWR's 1×2
    {"GTWR", BSIZE_11, List_1x1_OCCUPY,   NULL},
    {"GUN",  BSIZE_11, List_1x1_OCCUPY,   NULL},
};
```

### Visual reference (occupied vs overlap)

ASCII shapes — `▓` = occupied cell, `░` = visual overlap, `·` = bounding box only.

| Bldg | Shape | BSIZE |
|---|---|---|
| NUKE/NUK2/HQ/EYE | `▓░`<br>`▓▓` | 2×2 |
| PYLE | `▓▓`<br>`░░` | 2×2 |
| HPAD | `▓▓`<br>`▓▓` | 2×2 (full) |
| HAND | `░░`<br>`▓▓`<br>`░▓` | 2×3 |
| FACT | `▓▓▓`<br>`▓▓▓` | 3×2 |
| AFLD | `▓▓▓▓`<br>`▓▓▓▓` | 4×2 |
| PROC | `·░·`<br>`▓▓▓·`<br>`░░░` *(approx)* | 3×3 |
| WEAP/TMPL | `░░░`<br>`▓▓▓`<br>`▓▓▓` | 3×3 |
| FIX | `░░░`<br>`░▓▓▓·`<br>`░░` *(approx)* | 3×3 |
| SILO/SAM | `▓▓` | 2×1 (SAM has overhang) |
| ATWR/OBLI | `░`<br>`▓` | 1×2 |
| GTWR/GUN | `▓` | 1×1 |

*(ASCII approximations — refer to the array definitions for exact cells.)*

---

## Workflow per entry

1. Pick decisions for the entry (faction, donor, stats — all decided above for v0.3).
2. Run the 6-step recipe in `docs/adding-td-buildings.md`.
3. Update status: 📝 → 🔨 (built, untested) → ✅ (Deck-verified).
