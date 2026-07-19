# W2(b) construction-yard split — session postmortem, 2026-07-19

**Read this before touching the yard/MCV split again.** The session shipped real work, then
spent hours failing at one surface for a reason that is worth not repeating. The corrected
plan is at the bottom.

---

## 1. What shipped and is verified good

| Commit | What | Verified |
|---|---|---|
| `2017ce3` | W2(a) prereq-aware sidebar eviction (`legal=true`) | ✅ in-game: capture-offered + prereq-gated cameos withdraw on loss, return on rebuild, 0 spurious evictions over ~10k frames |
| `5055f1f` | b1: `Is_Construction_Yard()` role predicate, 10 site conversions, `Crew_Type` switch hoist, **triplicated BScan shadow table unified into `TF_Building_Scan_Bit()`** | ✅ in-game: Engineer still spawns on yard sale (proves the hoist kept RNG call order) |
| `c0fbae0` | `STRUCT_TIBERIAN_LAST` marker bounding the TD/TS enum block | ✅ builds; earns its keep in b2 |
| `a40b828` | AI census counts GDI/Nod yards + MCVs (dev-log only) | — |
| `5438a3a` | Enum identifiers renamed by faction (`STRUCT_AFACT`/`STRUCT_TDGFACT`/`UNIT_AMCV`/`UNIT_TDGMCV`) | ✅ builds clean |
| `83c32bb` | 4 new types: `STRUCT_SFACT`, `STRUCT_TDNFACT`, `UNIT_SMCV`, `UNIT_TDNMCV` | ✅ in-game: no duplicate cameo, no heap/art corruption |
| `e63ccab` | IniName migration + `From_Name` legacy aliases | partial — see §3.4 |
| `66af6c7` | Art re-bound via explicit `Image=` | ✅ fixes the invisible-object regression |

**Keep all of it.** b1's scan-bit unification is the most valuable single piece: the shadow
table was three hand-maintained copies of a mapping whose failure mode is losing the match on
deploy.

---

## 2. The root error

**The task was framed as an engine refactor and never re-framed when it became entity
creation.**

`ai-upgrade-plan.md` §W2 describes dispatch sites, enum pairs, `Can_Build` remaps and role
flags — so the work started in `defines.h`/`bdata.cpp`. Three research agents were
commissioned, all three about C++ dispatch and enum mechanics, **none about how this mod
creates entities**. The evidence gathered was shaped by the assumption already made.

`td-port-playbook.md` and `scripts/bundle_ra_building.py` are filed under *porting TD
entities*, and were mentally scoped to TD ports. They are not about TD. They are about
**creating a separated entity**, which is exactly what "give each faction its own
construction yard" is.

Worse: a survey agent returned the verified 12-step recipe — own art archive, own tileset
entries, own registration — it was summarised and then **not followed**, because the
reuse-and-`Image=` approach was already committed to and the recipe was treated as background
rather than instructions.

Underneath was a minimal-diff instinct (reuse `UNIT_MCV`, point `Image=` at existing art,
hand-edit a few XML keys). CLAUDE.md does ask for small diffs for upstream merging, but **the
mod's own convention for a job beats a small diff**. Every entity built the mod's way works.
The two built by hand needed four debugging rounds and still do not display correctly.

**The check that was skipped:** *does this repo already have a documented way to do this?* —
asked before writing code, not after it misbehaves.

---

## 3. Falsified — do NOT re-chase

### 3.1 Sidebar naming: four dead theories

The sidebar cameo label for `RA_AMCV`/`RA_TDGMCV` could not be changed. All four attempts
failed **in-game**:

1. **rules.ini `Name=` drives the sidebar** — NO. It drives the *in-world hover tooltip*
   only. (Screenshot: unit tooltip read "Allied Mobile Construction Vehicle" while the cameo
   read "MCV".)
2. **An unresolvable `ObjectNameTextID` falls back to the DLL name** — NO. The launcher
   renders the **raw ID**: cameos showed `TEXT_UNIT_AMCV` / `TEXT_UNIT_TDGMCV`.
3. **Deleting the `ObjectTypeClass` entry forces a fallback** — NO. Gives `<Missing> MCV` and
   an **empty cameo slot**; the entry carries the `BuildIcon` and is mandatory.
4. **A mod-owned object class name (`RA_MCV` → `RA_AMCV`) hands naming to the DLL** — NO.
   Still displayed "MCV" after the IniName migration.

### 3.2 The broken verification (the worst mistake of the session)

Theory 2 was "verified" by decoding `MASTERTEXTFILE_EN-US.LOC` **entirely as UTF-16** and
searching it for a key. **The file stores keys as ASCII and values as UTF-16.** The check
therefore returned zero for *every* ID, including ones that plainly exist, and that
guaranteed-zero was written into a commit message as evidence of absence.

**A check that cannot fail is worse than no check**, because it gets recorded as proof.

### 3.3 "14 shipped entities have broken cameos" — WRONG, disregard

Inferred from §3.2's bad method plus theory 2. Luke's direct in-game observation contradicts
it: the Flame Bunker, the naval units and the A-10 all display their names correctly. The IDs
(`TEXT_STRUCTURE_TDFBNK` etc.) genuinely are absent from the master text, and those entities
**still show correct names** — see §4, this is the unexplained bit.

The proposed `CONFIG.MEG` master-text repurposing hack was solving a problem that only existed
in the misreading. Dropped.

### 3.4 Renaming tileset `<Name>` keys — reverted, do not retry this way

The tileset key is the **published name of the art**, and `Graphic_Name()` must resolve to it.
Renaming `FACT`→`AFACT` (52 keys), `TDFACT`→`TDGFACT` (49), `MCV`→`AMCV` (32),
`TDMCV`→`TDGMCV` (32) left the DLL asking for keys that no longer existed → **invisible MCV at
skirmish start, invisible construction yard on deploy**. Reverted in `66af6c7`; all eight
entities now carry an explicit `Image=`.

The right way to give an entity its own art keys is the bundling pipeline, which publishes the
art under the new name *and* writes matching keys. Not a find-and-replace.

### 3.5 Premature faction naming

`Name=Allied MCV` / `GDI Construction Yard` were applied in b2 while `Owner=` was still
shared, so a Soviet player was told their MCV was Allied while correctly building a Soviet
base. Names must land **with** the `Owner=` narrowing that makes them true, not before.

### 3.6 Superseded design decisions (docs still contain these — see §6)

- **Reusing `UNIT_MCV`/`STRUCT_CONST` as the Allied pair** (`5438a3a`, `83c32bb`) — superseded.
  Luke's call: **all four must be new pipeline-built entities**, like the GDI/Nod naval units.
  Reuse is what keeps Allied/GDI tied to EA object classes and EA names, and creates a split
  where two of four factions behave differently from the other two.
- **Not splitting the MCVs, dispatching deploy on house `ActLike`** (`35ec7f3`) — superseded.
  Owner-dispatch re-introduces owner-beats-lineage one level above the yard, so a captured
  tech tree dies at the last step. **Split them properly.**
- **`UnitClass::ActLike` instance field** — no longer needed; it only existed to work around
  not splitting the MCVs.

---

## 4. The open question that blocks naming

**Why do pipeline-built entities display their `rules.ini` `Name=` on the sidebar, when their
`ObjectNameTextID`s are absent from the master text?**

Confirmed absent from our `CONFIG.MEG`: `TEXT_STRUCTURE_TDFBNK`, `TEXT_STRUCTURE_TDGYARD`,
`TEXT_STRUCTURE_TDGAFLD`, `TEXT_STRUCTURE_TDNPEN`, `TEXT_STRUCTURE_TDSTEAL`, `TEXT_UNIT_TDA10`,
`TEXT_UNIT_TDDD`, `TEXT_UNIT_TSHVR` and others. Those entities **work**. `RA_AMCV` with an
equally absent ID **does not**.

So there is a real difference between an entity created by `bundle_ra_building.py` /
`bundle_unit.py` and one hand-edited, and it was never found — four hypotheses were tested one
per game launch instead.

**Next session: stop hypothesis-testing. Read `scripts/bundle_ra_building.py` and
`scripts/bundle_unit.py` end to end, then diff a known-good entity (`TDGYARD` or `TDFBNK`)
against `RA_AMCV` across EVERY layer** — rules.ini, `RA_STRUCTURES`/`RA_UNITS` tilesets,
`RABUILDABLES`, the art archives under `Data/ART/TEXTURES/SRGB/`, `BuildIcon_*.tga`, and
`buildings_manifest.py` — until the difference is identified. It is a diff, not a guess.

---

## 5. Corrected plan — pick up here

**Build all eight entities through the runbook, exactly as the GDI/Nod naval units were.**
`docs/td-port-playbook.md` + `scripts/bundle_ra_building.py` / `scripts/bundle_unit.py`
(usage: `bundle_ra_building.py SYRD TDGYARD --build-icon ... --text-name ... --text-desc ...`).

1. **Read first** (do not skip): `td-port-playbook.md`, `td-building-separation-recipe.md`,
   `td-vehicle-port-recipe.md`, and both bundling scripts. Resolve §4 before naming work.
2. **Four MCVs and four yards as fresh, fully independent entities** — own IniName, own art
   archive, own tileset keys, own `BuildIcon`, own object class. **No `Image=` sharing.**
   Vanilla `MCV`/`FACT` types stay in the enum for stock-campaign compatibility but stop being
   what skirmish uses; the `From_Name` aliases in `bdata.cpp`/`udata.cpp` can then go.
3. **Badged cameos** — Luke's idea, and it makes the capture case readable regardless of
   whether §4 is ever solved. Emblem art already exists:
   `Data/ART/TEXTURES/SRGB/RED_ALERT/VFX/dot{ally,ussr,gdi,nod}/dot*-0000.tga`. Custom cameos
   are already proven (`BuildIcon_TD_A10.tga`, `BuildIcon_TS_HoverMLRS.tga`).
4. **Then the functional split (b3):** `Owner=` narrows per faction, twins go `TechLevel=7`
   (currently `-1` so b2 stays inert), and the three identity tables go four-way on type:
   deploy `unit.cpp:124` `MCV_Deploy_Building`, undeploy `building.cpp:5297`, spawn
   `scenario.cpp:3530`. Faction `Name=` values land **here**, with the `Owner=` narrowing.
   Every new faction prereq token needs an explicit `Can_Build` remap `continue`
   (`house.cpp:1036-1196`) or it is silently unbuildable.
5. **b4:** bonus-unit picker `scenario.cpp:3023` (known-issues fold-in).
6. **Then (c) War Factory** — this is what closes Luke's headline case (Allied captures a
   Soviet ConYard, builds a war factory, and it comes out **Allied** today because `[WEAP]` is
   shared and `BuildingClass` ctor takes `House->ActLike`, `building.cpp:2459`). Consider
   moving (c) ahead of (d) Helipad; they are independent.

**Nothing needs reverting.** The tree is clean, builds, and is deployed. `66af6c7` already
undid the only regression. The superseded *decisions* in §3.6 are corrected by doing §5 —
they are recorded in commit messages and in `ai-upgrade-plan.md`, which §6 fixes.

---

## 6. Docs that still contain superseded claims — fix when picking up

- `ai-upgrade-plan.md` §W2 **naming spec**: states or implies `Name=` controls the sidebar
  label. It does not (§3.1). It also still carries the reuse-not-split MCV decision and the
  `UnitClass::ActLike` b3 note from `35ec7f3`, both superseded (§3.6).
- `ai-upgrade-plan.md` §W2 b1–b4 block: written around reuse; rewrite around §5.
- `known-issues.md`: the select-all/deploy hotkey entry stays accurate. Note that splitting the
  MCVs means **Soviet and Nod lose the deploy hotkey too** — the gate is compiled into
  `ClientG.exe` and keys on vanilla type identity. Luke accepted this deliberately.

---

## 7. Method notes worth keeping

- **Check whether the repo already documents the job, before writing code.** The runbook
  existed, was read, was summarised, and was not used.
- **A verification that cannot fail is not a verification.** Sanity-check the method against a
  case known to be positive before trusting a negative.
- **Do not test one hypothesis per game launch.** When a mechanism is unknown and a working
  example exists, diff against the working example.
- **Ground-truth beats inference.** The "14 broken cameos" claim survived exactly as long as it
  took Luke to say "the naval stuff works perfectly."
- **Name things when they become true**, not when the name is decided.
