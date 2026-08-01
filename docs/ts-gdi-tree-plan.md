# TS GDI tree — implementation plan (2026-08-01)

**Goal (Luke, 2026-08-01): the full GDI Tiberian Sun tech tree in the mod**, as the
ownership-gated easter-egg tree designed in `ts-factions-feasibility.md` §"The cheap
alternative": a rare crate drops a **TS MCV**; deploying it produces the **TS
construction yard (`TSFACT`)**, and the yard is the sole gate on the roster — any side,
no new house, no picker slot, no CONFIG.MEG change.

Work happens on branch `ts-units` in the `tf-ts-units-worktree` worktree, deployed to
the **Deck only** (surface-ownership rule, 2026-08-01: the parallel AI instance owns
the desktop prefix).

## Delivery mechanics (the gate)

- **TS MCV rides the RANDOM unit-crate path only, never the `force_mcv` comeback path**
  (a wiped player must get their own faction's MCV — doc'd trap).
- Existing 1-in-8 TS crate roll stays; the MCV joins it as a rarer sub-roll
  (1-in-4 within the TS roll ≈ 1-in-32 of unit crates — **rarity approved by Luke
  2026-08-01**). Dev builds override to 100% (every unit crate = TS MCV, gated on
  `TF_DEV_BUILD` + `TF_Dev_Cheats()`) for tree testing; revert to the rare roll is
  automatic in release builds. AI use of the tree comes later with W2.9.
- All TS types ship broad `Owner=` (all sides) + `Prerequisite=TSFACT` chain; every
  new prereq token gets its `Can_Build` remap `continue` (the known silent-unbuildable
  trap).
- TS MCV is also buildable in-tree (TSWEAP + TSTECH, TS TechLevel 10) so a found tree
  is self-sustaining; heritable capture already works via the W2 lineage machinery
  (`MCV_Deploy_Building` gets a `UNIT_TSMCV → STRUCT_TSFACT` case).
- The three marquee units (Hover MLRS / Titan / Mk. II) keep their crate delivery AND
  become buildable behind the tree with their real TS prereqs.
- Balance stance: **TS-authentic stats, a generation ahead by design** — as a rare
  find, strong is the point (flagged as a decision in the feasibility doc; revisit
  after play).

## Roster — v1 (standard mechanics, proven pipelines)

Stats below are the TS RULES.INI values (verified from the extracted INI, not from
memory). `TS` IniName prefix throughout (dodges the TD HP-doubling hook).

### Buildings (NewTheater SHP + buildup, the TSPOWR/stealth-gen recipe)

| Ours | TS | TL | Cost | Str | Prereq (translated) | Notes |
|---|---|---|---|---|---|---|
| TSFACT | GACNST | — | — | 1000* | (MCV deploy) | 3x3, GTCNST + GACNSTMK. *TS has no CY strength listed with the buildables; use TS `[GACNST]` value at port time. |
| TSPOWR ✓ | GAPOWR | 1 | 300 | 750 | TSFACT | shipped; rewire prereq + real TL |
| TSPROC | PROC | 1 | 2000 | 900 | TSFACT, TSPOWR | RA refinery mechanics + free TSHARV |
| TSSILO | GASILO | 1 | 150 | 300 | TSPROC | |
| TSPILE | GAPILE | 1 | 300 | 800 | TSFACT, TSPOWR | barracks, 2x2 |
| TSWEAP | GAWEAP | 2 | 2000 | 1000 | TSPROC, TSPILE | war factory, 4x3 |
| TSRADR | GARADR | 3 | 1000 | 1000 | TSPROC | radar, 2x2, Height 3 |
| TSHPAD | GAHPAD | 5 | 500 | 600 | TSRADR | helipad |
| TSTECH | GATECH | 6 | 1500 | 500 | TSWEAP, TSRADR | tech centre |
| TSDEPT | GADEPT | 7 | 1200 | 1100 | TSWEAP | service depot (RA FIX mechanics), 3x3 |
| TSVULC | GAVULC (GACTWR_B art) | 2 | 350 | 500 | TSPILE | component tower + vulcan as ONE standalone turret (RA has no upgrade mechanic); cost = tower 200 + vulcan 150 |
| TSCSAM | GACSAM (GACTWR_C art?) | 5 | 500 | 500 | TSPILE, TSRADR | AA tower, same standalone translation |
| TSROCK | GAROCK (GACTWR_A art?) | 9 | 800 | 500 | TSPILE, TSTECH | RPG tower, same translation |

### Vehicles (voxel renders @ 12 px/voxel unless noted)

| Ours | TS | TL | Cost | Str | Prereq | Primary | Notes |
|---|---|---|---|---|---|---|---|
| TSMCV | MCV | 10 | 2500 | 1000 | TSWEAP, TSTECH | — | deploys TSFACT; crate find |
| TSHARV | HARV | 1 | 1400 | 1000 | TSWEAP, TSPROC | — | RA harvester mechanics |
| TSSMEC | SMECH | 2 | 500 | 175 | TSWEAP | AssaultCannon | SHP walker, 12 walk frames, Titan pipeline |
| TSTITN ✓ | MMCH | 3 | 800 | 400 | TSWEAP | 120mm | shipped; rewire |
| TSAPC | APC | 6 | 800 | 200 | TSWEAP, TSPILE | — | hover locomotor stands in for TS amphibious float (deviation) |
| TSHVR ✓ | HVR | 7 | 900 | 230 | TSWEAP, TSRADR | HoverMissile | shipped; rewire |
| TSSONIC | SONIC | 9 | 1300 | 500 | TSWEAP, TSTECH | SonicZap | beam via Lines[] (LineMaxFrames ≤ 5, railgun precedent) |
| TSHMEC ✓ | HMEC | 10 | 3000 | 800 | TSWEAP, TSTECH | MammothTusk/railgun | shipped; rewire |

### Infantry (TS-SHP, td-infantry-port-recipe adapted)

| Ours | TS | TL | Cost | Str | Prereq | Primary |
|---|---|---|---|---|---|---|
| TSE1 | E1 | 1 | 120 | 125 | TSPILE | Minigun |
| TSE2 | E2 | 2 | 200 | 150 | TSPILE | Grenade (disc) |
| TSGHOST | GHOST | 10 | 1750 | 200 | TSPILE, TSTECH | LtRail (proven railgun beam) |

### Aircraft (voxel, RA helipad rearm mechanics)

| Ours | TS | TL | Cost | Str | Prereq | Primary |
|---|---|---|---|---|---|---|
| TSORCA | ORCA | 5 | 1000 | 200 | TSHPAD | Hellfire |
| TSORCAB | ORCAB | 8 | 1600 | 260 | TSHPAD, TSTECH | Bomb |

## Deferred (engine-heavy or new logic — phase 2, decide per item)

- **JUMPJET** — RA has no flying-infantry locomotor.
- **MEDIC** — heal logic exists in RA (MEDI); cheap if wanted, but it's an RA
  mechanics clone, decide whether it earns a slot.
- **TRNSPORT (Carryall)** — vehicle-lifting aircraft is new logic (RA Chinook lifts
  infantry only).
- **LPST (Mobile Sensor Array)** — sensor/cloak-detect logic; revisit with the
  Stealth Generator work (`stealth-generator-spec.md` IsScanner detectors).
- **GAPLUG/GAPLUG2/GAPLUG3** (Upgrade Center + Seeker/Ion plugs) — upgrade-slot
  mechanic doesn't exist; Ion Cannon Uplink could later host the existing Ion Cannon
  special on the Temple-nuke pattern.
- **GAFIRE/GAFSDF** (Firestorm) — wholly new defensive logic.
- **NAPULS (EMP Cannon)** — EMP disable logic is new.
- **GAWALL/GAGATE/GAPAVE/GALITE** — walls are OverlayTypes (different pipeline);
  gates are new logic; pavement/light post are cosmetic.
- **GAPOWRUP (Power Turbine)** — upgrade mechanic.

## Audio

Every entity ships authentic TS sounds via the dormant-sample recipe
(`td-audio-routing-recipe.md` + the HOVRMIS1 MS-ADPCM trap). Hosts used so far:
BONUS_UNLOCK, DINOATK1, DINODIE1, DINOMOUT. Each new sound needs a host with no
RAC_/RAR_ **and no SFX_GUI_*** reference (the SCOLD1 correction). The free-host
census needs re-running before the roster's sound count is committed.

## ⭐ The Stealth Recipe — canonical per-building port (Luke's challenge, 2026-08-01)

**Luke's spec:** all TS GDI buildings in place, tech tree correct, sized to match
their TD counterparts, TS-authentic built animations AND damaged states, TS sidebar
icons. Baseline = the Nod Stealth Generator ("that works really well").

Per building:
1. **Extract** (temperate 'T' names): base `GT<X>.SHP`, active anims `GT<X>_A/_B/_C.SHP`
   (art.ini `ActiveAnim*=`; `_AD` damaged variants are usually the second half of the
   same SHP, not separate files), buildup `GT<X>MK.SHP` (ISOTEMP.MIX), cameo per
   art.ini `Cameo=` (CONQUER.MIX or SIDEC01.MIX, decode with CAMEO.PAL). Bases/anims
   decode with UNITTEM.PAL.
2. **Compose** the stealth-gen layout: N healthy frames = healthy base + anim frame i
   (shorter anims loop), then N damaged frames = damaged base + anim damaged-half (or
   same anim frames if no damaged half). ⚠️ Buildup SHPs contain EMPTY + fragment
   frames past the real run (GTCNSTMK: real 0–23, empty 24–31, fragments 32–47) —
   the launcher renders missing/blank content as the PURPLE placeholder; ship real
   frames only, resampled to the donor's construction-anim count.
3. **One affine for every frame** of a building (base, anims, MK) — content-anchored:
   scale so the healthy composite's content matches the TD counterpart's content
   proportions (measure the TD ZIP frame-0 meta), centered on the canvas
   (canvas-center anchoring, launcher-render-contracts rule 1). Canvas = classic
   donor dims × 5.33. NEVER full-canvas scale (TSFACT v1 drew low + small).
4. **Donor = the TD counterpart** (matching footprint AND construction-anim count):
   TSFACT→TDFACT? no — donor stays RA FACT (3x3; TD yards are 3x2) — measure and
   match TDGFACT content scale instead. TSPOWR→TDNUKE(2x2), TSPILE→TDPYLE,
   TSPROC→TDPROC, TSWEAP→TDWEAP(3x3; TS 4x3 collapses to TD footprint for parity),
   TSRADR→TDHQ, TSHPAD→TDHPAD, TSTECH→TDEYE, TSDEPT→TDFIX(3x3), TSSILO→TDSILO,
   TSVULC/TSCSAM/TSROCK→TDGTWR/TDSAM/TDATWR-class 1x1s.
5. **Engine:** enum append INSIDE the TS block tail (move `STRUCT_TS_TREE_LAST`),
   heap `new` at the marked Init_Heap tail (slot==Type invariant), `_td_bdonors`
   entry, `TF_Building_Scan_Bit` shadow (proc→REFINERY, weap→WEAP, radar→RADAR…),
   role tests (`Is_Helipad` for TSHPAD; factory RTTI for TSWEAP incl. Exit_Object),
   and an `_anims[]` entry `{STRUCT_TSX, BSTATE_IDLE, 0, N, 3}` — the stealth-gen
   line at bdata.cpp:4621 is the template; damaged run = shapes N..2N-1 by the
   engine's +count convention.
6. **Data:** rules.ini section (TS stats, tree prereqs), RABUILDABLES entry,
   ModText rows, BuildIcon TGA from the TS cameo (NEAREST 8x → LANCZOS 341×256,
   `BuildIcon_TS_<X>.tga`) — Luke wants the real TS icons on the sidebar.

## Sequencing

1. **Skeleton** — TSFACT + TSMCV + crate roll + `Can_Build` token + rewire the four
   shipped TS types into the tree. *Tree exists end-to-end with current content.*
2. **Economy** — TSPROC + TSHARV + TSSILO + TSPILE + TSWEAP. *Tree becomes
   self-sustaining.*
3. **Combat spine** — TSSMEC, TSRADR, TSHPAD, TSTECH, TSDEPT. *Full vertical slice.*
4. **Roster fill** — TSSONIC, TSAPC, defenses (TSVULC/TSCSAM/TSROCK), infantry,
   Orcas.
5. Phase-2 decisions with Luke.

## Known interactions / cautions

- **Heap registration must be strictly enum-ordered** (heap slot index == Type;
  `As_Reference` indexes the heap directly). Append new `new XTypeClass(...)`
  calls at the marked tail of Init_Heap, never beside a related type mid-list.
  Violating this shipped once (2026-08-01): the GDI Helipad slot held the TS
  yard, AI MCVs deployed helipads. Fixed in `82aec6d`; the tail comment anchors it.
- **`MT_COMMANDBAR_COMMON.TGA` (the C&C-logo crest atlas, ~176MB) is NOT in git**
  — it rides in `build/remaster/Vanilla_RA/` and the Workshop package only. A
  fresh worktree build dir lacks it, and `rsync --delete` then strips it from
  the deploy target (symptom: vanilla Allied eagle in the radar). Recovery copy:
  the Workshop cache `~/.steam/.../workshop/content/1213210/3729834253/`.

- **AI blindness:** until the faction-agnostic builder (W2.9, other instance's lane)
  can see non-home lineages, an AI that finds the TS MCV deploys a yard it never
  uses. Accepted for now; TS is the fifth lineage that breaks any 4-way literal —
  coordinate with the AI instance before merging tree-visibility work.
- **Merge hotspots with the AI instance:** `defines.h` enums, `udata.cpp`,
  `bdata.cpp`, `cell.cpp`, `rules.ini`. Small commits, rebase onto `main` often.
- Old saves break on any enum growth (accepted, standard).
- TS art is EA copyright, same tolerated category as the TD-Remastered art already
  shipped; ship call is Luke's (`ts-asset-import-spike.md` legal note).
