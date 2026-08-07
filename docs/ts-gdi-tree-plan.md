# TS GDI tree — implementation plan (2026-08-01)

## ⭐ 2026-08-07 LATE — RESUME HERE (war factory resized; door seam OPEN)
**Desktop prefix at `854fcd4d`, md5-verified. Deck still STALE. Nothing pushed.**

**THE SIZE FIX, and why it was needed.** A Mammoth Mk. II measured **40x40**
classic px against a **33.6x33.6** door: it could not fit through, at any spawn
position. Luke's call was to grow the building, not shrink the units ("i
actually like the size of titan and mk2"). The hangar is now pinned to **4
cells** (`fit_w` 384 -> 512, 1.33x): **93.7 x 65.7** classic px, door **47.2 x
41.5**. Mammoth drops from 82% to 61% of the building's height.

**FOOTPRINT LANDED AT 4x3, NOT 5x4.** The first cut grew the plot to a new
`BSIZE_54` so the concrete kept a column inside the footprint; Luke confirmed it
worked in play, then asked for 4x3 with no overlap. **The art is 3.90 x 2.74
cells, so it fits a 4x3 plot outright** — no radar-style overhang was needed.
The concrete now falls **wholly outside** the plot and is kept clear by
`Is_TS_Apron_Cell`, which vetoes apron cells wherever they lie. Footprint back
to 12 cells. `BSIZE_54` was added and then **removed again** — do not go looking
for it.

### ⚠ THE TRAP THAT COST A ROUND: BSIZE does NOT drive the placement grid
`BuildingTypeClass::Occupy_List(placement=true)` returned a **hardcoded 4x3
literal shared by TSPROC and TSWEAP**. That list — not `Size` — is what the
sidebar `PlacementList` export, `Legal_Placement` and placement proximity all
consume, so the launcher drew the old footprint while the engine believed the
new one. **Split per type now.** Second shared-literal trap in the same change:
`Is_TS_Apron_Cell`'s offset table was shared the same way and also needed
splitting. **When resizing a TS building, grep for every literal that names it
alongside another type.**

### Geometry, for whoever re-measures
Canvas **896x672**, stub **168x126** (x5.33), `fit_w` 512, `dst_x_px` 448,
`bottom_margin` 27, apron `((4,3),(6,4))`. Plot origin sits at (36,27) classic
inside the stub. `ExitCoordinate` = **XYP_COORD(64, 43)**, the centre of the
door **APERTURE** (pixels that change between shutter stage 0 and 8) — *not*
the door composite's centre, which the bay surround drags ~5px south-east.

## ⭐⭐ NEXT SESSION STARTS HERE: SPLIT TSWEAP INTO BASE + WEAP2 FRONT
**Luke's call, 2026-08-07: "split". Deferred to a fresh session deliberately.**

**TSWEAP IS BUILT BACKWARDS FROM EVERY OTHER WAR FACTORY IN THE MOD.** Our own
`building.cpp:795` states the convention: *"WEAP.ZIP is just the bottom ramp;
WEAP2.ZIP is the walls/roof with door-opening frames."* RA's WEAP, TD's TDWEAP
and RA's AWEAP/SWEAP all follow it. **TSWEAP does not** — it puts the WHOLE
hangar in the base sprite and only the shutter in the overlay. That is why a
spawning vehicle can never look like it is inside the bay: there is no layer
in front of it. Luke supplied RA and TD reference sprites showing both games'
lower halves (floor + bay mouth) with the roof carried separately.

**The overlay already draws OVER units** — that is exactly why it was occluding
vehicles on 08-06, and the 08-07 fix clipped 71% of it away. **The layer we
deleted is the layer we now want**; it just has to be the hangar's FRONT rather
than the surplus ground that came attached to it.

Doing it right retires three open problems at once:
- the hard door seam (nothing is clipped, so nothing has a cut edge),
- the "unit spawns outside the factory" read (it gets sandwiched),
- `ExitCoordinate` guesswork (the aperture becomes a real modelled opening).

Shape of the work: re-cut `shp_gtweap` into a base piece (floor, back wall, bay
interior) and a front piece (roof, near wall) instead of clipping the door
composite to a silhouette; the front piece composites with each of the 9
shutter stages, exactly as `TSWEAP2` frames are built today. Damaged run too.
`Draw_It` already dispatches TSWEAP2 per door stage — **no engine change
expected**, this is a packer change.

### OPEN — nothing here is signed off
1. **The door seam** — superseded by the split above; do not patch it
   separately. (Cause, for the record: the 08-07 clip multiplies by a
   **binarised** silhouette (`alpha>0 -> 255`), so the door is cut dead hard
   against a soft-antialiased building edge, straight through the bay
   surround's ramp. 1.33x made it 33% more visible.)
2. **Ramp stripes band yellow/green.** The apron's gold-baking test
   (`g>70 and g>r*1.6 and g>b*1.6`) misses the ramp's DARKER green bands, which
   then stay raw on ground art, and ground art is never house-remapped.
3. **The Titan parks ahead of the door.** NOT the factory's fault: `TSTITN`'s
   ink sits **+11.8 classic px below its box centre** in frame 0, where every
   other unit is within ±2.4 (Mammoth −0.3, Wolverine +1.7, APC −2.4, harvester
   −0.2). Its packed box is 378 canvas px tall against ~190 of per-frame ink, so
   the sprite swings nearly a cell across the walk cycle. Fix the unit's frame
   registration, or dial `ExitCoordinate` by eye — Luke's call, untouched.
4. **Power plant.** Luke asked for the same treatment; measured, it does not
   apply — TSPOWR is **100% x 93%** of its 2x2 plot, so there is no spare row to
   free. Radar treatment there would mean making it BIGGER, a separate size
   judgement (note: a past size-up left it "looking like a toy").
5. SE bay exits still never judged in play; exit list re-cut but unseen.
6. **The pad lies outside the 4x3 plot, and geometrically must.** Luke flagged
   it; there is no arrangement that keeps a Mammoth-width (4-cell) door AND a
   contained pad on a 4x3 plot, because the hangar uses every column. Choices
   are: leave it outside (current — `Is_TS_Apron_Cell` keeps it unbuildable),
   clip the concrete at the plot edge (a hard cut, same ugliness as the door
   seam), or return to 5x4. **Undecided.**
7. **TSPROC stamps 6 blank apron tiles of 15** — same class of bug as the war
   factory's power-plant-bib eater below, still live, NOT fixed (its art is
   signed off, so it wants Luke's OK). The packer now prints a WARNING naming
   the count on every run.

### ⚠ A SMUDGE STAMPS EVERY CELL OF ITS RECTANGLE, ART OR NOT
Found the hard way when the war factory ate the power plant's bib. The engine
writes the smudge to all `w*h` cells; a tile with no art still stamps, and a
blank stamp **overwrites whatever smudge that cell already had**. Growing the
apron grid to 6x4 claimed 24 cells for 15 tiles of concrete, and the 9 blanks
wiped the neighbour. **The grid must hug the concrete, not the plot** —
`TSWEAPBB` is now 5x3 at a `Bib_And_Offset` of `MAP_CELL_W + 1` (one cell east,
one south). `ts_pack_tree.py`'s apron config carries that offset as a third
tuple, and the packer WARNS on any blank tile it is about to emit.

## 2026-08-07 — aprons: FIXED + signed off, both buildings
**Desktop prefix at `71df2628`, md5-verified. Deck still STALE at `2d8a5dbb`.
Nothing pushed to origin.**

**SIGNED OFF IN PLAY ("all good on the pads"):** vehicles no longer vanish
beside the war factory OR the refinery, both aprons are ground art that takes a
move order, and placement is legal everywhere except each 4x3 plot.

### ⭐ THE ROOT CAUSE WAS THE BAY DOOR, NOT THE APRON
Four rounds were spent moving the apron between render layers before anyone
measured *what was actually covering the unit*. It was `TSWEAP2`, the bay-door
overlay. **TS's under-door art (`GAWEAP_1`) carries the whole bay surround —
ramp and concrete included — and 71% of it fell OUTSIDE the building's own
silhouette.** That surplus is BUILDING art, so it sorts as building and paints
over exactly the cells vehicles stand on (69% and 83% of the two worst plot
cells). No apron flag could ever have fixed it.

**Fix: clip the door composite to the building's silhouette** (union of the
built frames' alpha, per damage run). Lossless for the animation — of the
pixels that move across the nine door stages, **15 of 10,523** lay outside.
Verified after packing: the door paints 0% outside the building in every cell.

⚠ **The lesson, and it is the second time this arc has cost hours: measure
which object owns the pixels before changing any render flag.** A per-cell
coverage table off the packed art took one command and gave the answer
outright. See [[feedback-identify-occluder-before-flag-changes]].

### The apron, as it now stands (all of this is keeper work)
- `SMUDGE_TSWEAPBB` (`sdata.cpp`) is a bib-family smudge, **5 wide x 3 tall**
  over the 4x3 plot. `Bib_And_Offset` returns it for `STRUCT_TSWEAP` at offset
  0, independent of `Bib=` in rules (which still governs the RA slab, off).
  Downstream is stock RA: `SmudgeClass::Mark` stamps `Smudge`+`SmudgeData`,
  capture re-owns, `Disown` clears.
- **It draws as TERRAIN**, the TD-template ground entry copied field for field:
  `IsOverlay=true`, `IsSmudge=false`, **`IsTheaterShape=true`**,
  `Type=OVERLAY_V12` (pip-free), `SHAPE_CENTER|SHAPE_WIN_REL|SHAPE_GHOST`,
  centred on the cell, `ShapeIndex=SmudgeData`.
- **A theatre shape resolves out of `RA_TERRAIN_<theatre>`, not
  `RA_STRUCTURES`** — so the tiles live in all three RA terrain tilesets and
  their art under `TERRAIN/<THEATRE>/`. **Snow had no mod tileset at all**; the
  mod now ships a full `RA_TERRAIN_SNOW.XML` extracted from CONFIG.MEG and
  spliced (a mod tileset REPLACES the base file, so a theatre you want one tile
  in has to ship the whole thing). `ensure_tileset()` in `ts_pack_tree.py` does
  the extraction on first run.
- **`Is_Clear_To_Build` refuses to build over ANY bib** — stock RA. The apron is
  exempted there (`cell.cpp`), so placement is decided by `Is_TS_Apron_Cell`
  alone, which vetoes the 4x3 plot and leaves the 5th column free. **Add any
  future apron smudge to that exemption too.**
- **The 5th column is deliberate.** The concrete tapers ~14 canvas px past the
  plot's east edge; a 4-wide grid cut a flat vertical edge 48px tall across the
  tip. RA's own bibs lie outside their footprints too. `ts_pack_tree.py`
  **fails the build** if the packed apron outgrows its grid — change the grid
  and `sdata.cpp` in the same commit.
- The slice is verified exact: the 15 tiles under the new sprite reproduce the
  old composite with **zero alpha difference**. Residual RGB difference is hq4x
  edge interpolation, unavoidable once the layers scale separately.
- **The apron's hazard stripes are BAKED gold** `(v, 0.82v, 0)`. They are drawn
  in TS's house-remap range (raw green in source); the launcher remaps building
  sprites and **never** ground art, so ground art must carry its final colour.
  The ratio was measured off a rendered frame, so it is the launcher's own
  output for that ramp. Fixed whoever owns the factory — open to revisit if a
  house-tinted stripe is ever wanted, in which case the stripes come out of the
  apron entirely instead.
- The buildup pours and keeps its own pad (`masks = {}`); its remapped stripes
  cover the apron's during construction.

### Both buildings, and how to add a third
`SMUDGE_TSWEAPBB` and `SMUDGE_TSPROCBB` are both 5x3 over a 4x3 plot. To add
another, all five of these move together — `Is_TS_Apron_Smudge` exists so the
placement and render sides cannot drift apart:
1. `SmudgeType` in `defines.h` + the `SmudgeTypeClass` in `sdata.cpp` (grid).
2. `Bib_And_Offset` branch in `bdata.cpp` (returns it at offset 0).
3. `Is_TS_Apron_Smudge` in `building.cpp` (drives BOTH the
   `Is_Clear_To_Build` exemption and the renderer's ground-entry branch).
4. `Is_TS_Apron_Cell`'s offset table, if its plot veto differs.
5. `aprons` in `ts_pack_tree.py`: `((plot cols, rows), (grid cols, rows))`.
The packer refuses to pack if the art outgrows the grid, and prints the grid
the art actually needs — that is how both 5-wide grids were arrived at.

### Open, in order
1. **SE bay exits** — never started. `TsWeapExit` prefers south-east cells and
   the spawn faces DIR_SE, but nothing is dialled; expect an awkward pose.
   Wants Luke's eye live, like the dock.
2. Carry-overs: TSFACT conyard selection box, RA-truck-at-TSPROC eyeball,
   watched TDHARV dock, sidebar off-by-one upstream to main.

## SESSION END 2026-08-06 LATE (war factory door + plot)
**Desktop prefix at `6506fb8b`, md5-verified. Deck still STALE at `2d8a5dbb`.
Nothing pushed to origin.**

**SIGNED OFF IN PLAY:** the bay door ("door animation looks good", speed dialled
to DOOR_RATE 4) and the placement reach fix.

**SHIPPED, NOT YET JUDGED:** 4x3 plot + concrete pad, the size fix, bib off,
the apron build-veto, pad sort order.

### The diagnosis written here was HALF WRONG — see the 2026-08-07 block above
This block claimed a single cause for both symptoms: that the pad was part of
the building sprite, so it both sorted against units and answered the launcher's
hit-test. **The hit-test half was right. The vanishing half was not** — for the
war factory the occluder was the BAY DOOR overlay, whose under-door art spills
71% of itself outside the building. Moving the pad to ground art did not fix the
vanishing there; clipping the door did. (For TSPROC, which has no door, the pad
really was the occluder.) Both are now ground art and both are signed off.

### Falsified this session — CORRECTED BELOW, do not re-trust the old claim
- **GTWEAP frame 1 is NOT a "door-open healthy variant".** Frames 0/1/2 are
  healthy / LIGHT damage / HEAVY damage. Building a door on frame 1 made the
  factory look shot up while producing. The real door is a separate SHP:
  `ART.INI` gives `DoorAnim=GAWEAP_D`, `DoorStages=9`, `UnderDoorAnim=GAWEAP_1`,
  now packed as the TSWEAP2 overlay and drawn through RA's WEAP2 path.
  The same "frame 1 = variant" claim elsewhere in this doc is suspect.
- `GTWEAP_D` frames 9-17 are **magenta placeholders**, not a damaged door run
  (same trap as GTPOWRMK).

### Traps that cost time today
- **Canvas and classic stub must move together.** Growing a canvas without
  re-running `build_tfassets.sh` renders the building at the wrong scale,
  silently. Hit twice — the shrunken hangar and then the mis-sized door.
  Now guarded: `ts_pack_tree.py` writes `scripts/ts_stub_dims.json` and
  `ts_stub` in `build_tfassets.sh` refuses a stub that disagrees.
- **An overlay's shape pointer supplies its render box.** Passing TDWEAP2's
  pointer drew the TS door at the TD factory's size; TSWEAP2 now has its own
  stub in TFASSETS.MIX.
- `Find_Exit_Cell` dereferences its argument — guard before calling it from a
  state that runs after radio contact drops.
- `$TS_ART_DIR` was gone from disk and nothing in the repo could rebuild it.
  Now `scripts/ts_rebuild_art.sh` regenerates it from the Steam TS install
  (verified: re-packs all twenty TS archives content-identical).
- TS building cameos live in **SIDEC01.MIX** (GDI), not CONQUER.MIX.

## ⭐ SESSION END 2026-08-06 — RESUME HERE
**Desktop prefix at `de1790b5` (md5-verified). Deck still STALE at
`2d8a5dbb` — push before any Deck play. Nothing pushed to origin
(Luke's standing rule: commits only, push on his say-so).**

**CLOSED THIS SESSION — the refinery dock arc, SIGNED OFF ("absolute
perfection"):** final geometry + the live-dial story in the sign-off
block below. Also shipped: motionless unload (stale-MOVE_HERE guard +
NavCom clear), organic exit (scripted roll deleted), plate/east-column
placement veto (occupied-neighbour lookup), refinery Adjacent=1,
TSHARV Speed=6 + **Tracked=yes** (the wheels-vs-tracks terrain trap,
third occurrence — Luke called it from the driver's seat; grep any new
vehicle's rules section for Tracked= before its first drive).

**NEXT SESSION, Luke's explicit list:**
1. **TSFACT (conyard) selection box** — still wrong, still queued (his
   close-out reminder). Fix path already scoped in the 08-05 block
   below: git-diff the TSFACT packer geometry (canvas/stub/
   bottom-margin/overscale + foundation) between the last known-good
   box commit (pre-reseat, 2026-08-04 evening) and HEAD; the
   CenterCoordY-bias lever is PROVEN launcher-ignored for this
   building — do not re-probe it.
2. **TS war factory** — door-opening animation + units spawn and drive
   SOUTH-EAST out of the bays (Luke's spec 2026-08-06). Reuse the dock
   verification loop (log lines + live dial with Luke's eye for the
   exit pose).
3. Carry-overs: RA-truck-at-TSPROC regression eyeball, TDHARV watched
   dock at TSPROC (machinery verified via TSHARV + Luke's TD
   screenshots, one clean observed cycle still owed), sidebar
   off-by-one upstream to main.


## ⭐ SESSION END 2026-08-05 evening — RESUME HERE (4x4 + reverse dock)
**Luke ended it "a bad session" — the WORK mostly shipped but two visible
asks missed. Desktop prefix now at `7178f70f` (plan-A visible dock + 4x3
foundation, deployed 2026-08-05 late, md5-verified). Deck still STALE at
`2d8a5dbb`.**

**SHIPPED + play-verified today (log-verified over ~20 clean cycles):**
- TSPROC foundation = 4x4 (Luke's pick): BSIZE_44, apron row is real
  footprint (cliff-drape fixed), centre cell = the dock pad, every dock
  offset re-indexed, art canvas 736x800 (frame content byte-identical).
- Reverse dock (Track15/16, Luke's line-up-then-reverse spec): truck lines
  up nose-SE on the pad, reverses to `pad+(-124,-44)` (the composite pose,
  rear at bay mouth), unloads, drives out forward-SE. Both TS + TD trucks.
- Green-smoke fix: the forced exit track delays the MISSION_HARVEST commit,
  so Mission_Unload re-ran CONTACTLESS and slipped past the fume gate
  (which keys on the contact's type). Contactless re-entry now exits early.

**⚠ MEASUREMENT LESSON (cost the "MAJOR REGRESSION" round): measuring the
docked composite by VISIBLE stripe centroid is occlusion-biased — the truck
covers most of the stripes, dragging the centroid SE and DOUBLING the
apparent depth (deployed -240,-86; truth -124,-44). Measure against
unoccluded landmarks (dome centroid + stripe-field SE tip).**

## ✅ THE DOCK IS SIGNED OFF — "absolute perfection" (Luke, 2026-08-06 evening)
**FINAL GEOMETRY (build `e15bbf3a` = commit `6e2a55e2`):** line-up = SE
plate cell centre; aimed dead-straight reverse (motion == facing+128 at
every waypoint) at facing 92 (TSHARV) / 94 (TDHARV); parks TSHARV
pad+(40,74), TDHARV pad+(3,23); settling pivot to true SE on arrival;
motionless unload (stale-MOVE_HERE guard in RADIO_DOCKING + NavCom clear
at IsDumping); organic pathing exit (no scripted roll). TSHARV Speed=6
(RA/TD parity). The centering was dialled LIVE with Luke over three
builds (composite-side attempt read WRONG to his eye; mirrored attempt
"almost"; half-step back = perfect) — the measured composite coordinates
were NOT the pose his eye wanted; the final constants are the ground
truth, do not re-derive from the reference PNGs. Also verified this arc:
plate/east-column placement veto (occupied-neighbour lookup fix),
selection box, Adjacent=1 placement reach, MCV 4x3 ghost. QUEUED NEXT:
war factory session (door anim + SE bay exits), RA-truck-at-TSPROC
regression eyeball, upstream the sidebar off-by-one to main.

## ⭐ OVERNIGHT RUN 2026-08-06 ~00:30 — THE DOCK IS DONE AND VERIFIED
**Option A (Luke's spec, chosen over B-curved and the bib fallback): the
truck faces TRUE SE and travels only along that axis. Line-up = SE plate
cell centre; entry tracks reverse pure NW (Track15/16 TSHARV -(199,199),
Track17/18 TDHARV -(243,243), every waypoint DIR_SE); park = the on-axis
point nearest each approved composite (TSHARV pad+(57,57), TDHARV
pad+(13,13), ~25/15px deeper along the ramp than the exact composite —
the flagged geometric consequence of the straight line); exit drives
forward SE back onto the plate. Verified in an autonomous desktop run
(Claude drove the skirmish end-to-end): 3+ dock cycles with exact axial
log numbers and park facing=96, burst frames show smooth reverse + clean
exit, credits banked, NO slide (motion==facing+128 by construction), NO
teleport (track start==line-up centre). Plate veto verified refusing
buildings (root cause was Cell_Building at the pad HOLE — resolved via
the occupied cell north of it); selection box verified hugging the
building (calibrated -78,-192 lepton bias, 90x56). Deployed desktop
prefix `002098652661` = commit `dea8c154`. NOT play-verified by Luke yet
— his checklist: watch one dock of each truck, the ~25px-deeper park is
the one open aesthetic question. TDHARV used the same machinery with its
own constants but had no live test (no TD truck in the run). RA ore
truck ramp-foot park unchanged (untested tonight). Evidence + narrative:
`~/Desktop/docking-art/MORNING-REPORT.md`.**

**OPEN — the missed asks (updated 2026-08-05 late):**
1. **❌ THREE-LAYER DOCK TRIED AND REVERTED SAME NIGHT (`db8913b1` →
   revert `b1f9b649`).** Deployed, Luke tested 2 SS in: the docked truck
   disappeared COMPLETELY (even the +230-threshold "half hide" reads as
   full-hide in practice — the bay-mouth dark art is building pixels and
   covers the whole truck). Luke's verdict: **PLAN A, full revert — the
   truck backs up to the entrance and stays FULLY VISIBLE on top,
   matching `~/Desktop/docking-art/refinery-ts/{ts,td}-harv-docked.png`.**
   `0f8192d7` removes ALL TSPROC sort bias (Center_Coord, grouped with
   REFINERY/TDPROC). Do NOT re-chase sort-based hiding at this building.
2. **✅ 4x3 FOUNDATION SHIPPED `7178f70f` (Luke's ask, same night):
   4 wide x 3 high = 2 building rows + apron row; tall art overhangs the
   row NORTH of the plot (radar treatment — that row stays passable, so
   units walk behind the refinery).** Centre cell stays the bay-mouth pad
   (BSIZE_43 centre = row 1 col 2 = the old 4x4 pad cell), so all
   Center_Coord-keyed dock geometry re-indexed itself; hand-adjusted were
   the cell lists (blocking/overlap/placement/veto/reach-seed, one row
   shorter), the 2-row selection box, and the packer (stub 138x174,
   canvas 736x928, margin 75 — art renders pixel-identical, growth is
   all bottom cells). DEPLOYED desktop prefix `7178f70f`, md5-verified.
   TEST: placement grid = solid 4x3; north row passable + units occluded
   behind the tall art; dock cycle unchanged (pad, reverse track, RA
   ramp-foot park); truck visible per the reference composites; MCV-era
   saves with old 4x4 refineries will mis-foot — fresh skirmish only.
2. **TSFACT (conyard) selection box rides ~13cl high — REGRESSED BY THE
   08-04 TIER RESIZE (Luke: "you had this correct earlier but you broke it
   on resize").** The box WAS correct before the conyard art was re-seated
   onto its bib. The CenterCoordY bias in the draw intercept is PROVEN
   IGNORED (12→25cl change moved the box 0px across a restart) — the
   launcher anchors the box to something the RESIZE moved, most plausibly
   the sprite's canvas/content geometry (art moved down inside its plot,
   box stayed plot-anchored, and it only ever "matched" while the art was
   plot-centred). FIX PATH: git-diff the TSFACT packer geometry
   (canvas/stub/bottom-margin/overscale + foundation) between the last
   known-good box commit (pre-reseat, 2026-08-04 evening) and HEAD, and
   restore the broken relationship — no launcher probing needed unless the
   diff exonerates the art.
3. **Luke's 4x3 proposal**: foundation 4 wide x 3 tall (2 building rows +
   apron row), tall art overhanging the top row like TSRADR's dish. Viable;
   third centre re-index (dock offsets, veto, seeds, Track15/16 dests, art
   re-anchor). Do it FRESH, not stacked on a live-fix evening.
4. Truck cell straddle: TSHARV ends in the pad cell, TDHARV one west
   (7277/7276) — endpoint x sits 4 leptons from the cell boundary. Harmless
   but worth centring when the endpoint next moves.

**Prior session's dead-ends list still applies — read it before dock work.**

**SHIPPED + Luke-verified tonight:**
- Whole-tier size drop: radar 2x2 (TS-authentic), refinery RA-3x3→4x3 (see
  below), conyard 3x3+bib (RA-yard parity, MCV round-trip intact), barracks
  2x1+bib (building top row, slab bottom row), WF 3x3 TDWEAP-parity +3px
  bib tuck. Flat trio sits ON its bib (centring experiment rejected).
- Conyard/WF selection boxes: CenterCoordY bias + dimy trim in the
  DLL_Draw_Intercept export = box hugs the art rows.
- TSPROC: apron restored as fit-excluded overlay (736x672 canvas, stub
  138x126, fit_w=384 decouples building width from canvas); Bib=no;
  Is_TS_Apron_Cell veto (in CellClass::Is_Clear_To_Build — the ONLY choke
  point the launcher placement preview honours!) keeps apron walkable but
  unbuildable; solid 4x3 ghost grid via Occupy_List(true) override (the
  ghost draws from sidebar PlacementList ← Occupy_List(true) — NOT the
  draw-intercept OccupyList, NOT Set_Cursor_Shape [dead code]); placement
  reach seeded from the walkable holes (Calculate_Placement_Distances);
  conyard top row freed (TDWEAP lists); Storage 80→2000 (pips + capacity);
  TSHARV elev-32 render, 0.75 pack, orbit-recentred, +8 facing.
- Docking end-state (SIMPLE): every harvester unloads VISIBLY at TSPROC on
  the ramp cell (pad = 4x3 centre + MCW), turn-in-place to SE, timer
  offload, no fumes at TSPROC (kept elsewhere), no harvest smoke puff.
  TSHARV at RA ref = TD harv's exact SW routine. TD-at-TD attach untouched.

**DEAD ENDS — DO NOT RE-CHASE (each cost a live-fix round):**
- The TS attach-dock (limbo + HORV-baked truck in refinery frames): Luke
  ditched it — a baked duplicate = a permanent sync surface (size ×4
  rounds, z-clip "loses its back", teleports). Machinery fully deleted in
  `c1efcf91`.
- BACKUP_INTO_REFINERY at any facing but SW: SNAPS (teleport). A real SE
  reverse needs a NEW mirrored track table entry (queued, fresh eyes).
- Detour approach cells: the RADIO_DOCKING maintenance loop re-orders the
  truck to the MOVE_HERE cell every tick → stuck oscillation.
- ANY post-turn coordinate seat (single-tick nudge OR 1px/tick creep):
  reads as slide/teleport; the creep RAN AWAY (Coord_Snap is NOT the
  cell-centre reference — trucks slid across the map). ALL seat motion
  deleted; trucks park at cell centre, full stop.
- Apron rectangle-clip to the 4x3: slices the stripes (hard edge). Full
  apron restored in the staged `d8d41cda`.

**OPEN — the next-session list (dock polish, ART-side only):**
1. Deploy `d8d41cda`, then ALIGN THE ART TO THE TRUCKS: both TS + TD harv
   read misaligned at the dock (cell-centre park vs stripes/composite,
   ~3-8px). The proven-safe lever = shift the APRON overlay in the packer
   so the bay centreline sits exactly on the pad cell centre; compare
   against `~/Desktop/docking-art/refinery-ts/ts-harv-docked.png` (Luke's
   locked pose) by overlay-measuring an in-game SS, set ONCE from data.
2. Harvest-resume stall: harvesters idle after TSPROC unload. DOCK-EXIT
   log lines are in (both Mission_Unload completions); read
   MOD_DEBUG_TSUNITS.txt (⚠ sometimes lands in pfx/drive_c/users/steamuser)
   from Luke's next match before theorizing.
3. Cliff-edge apron drape (concrete over impassable terrain on edge
   placements) — Luke's session-close options, DECIDE FIRST next session
   (his lean: the 4x4, "so the pad fits in nicely"):
   (a) drop the apron entirely, back to Bib=yes RA slab (5-minute revert,
   ends the apron saga); (b) foundation 4x4 so the drape row is footprint
   (placement then requires it clear = no cliff drape, grid matches art;
   ⚠ BSIZE_44 moves the centre cell to origin+2*MCW+2 — EVERY
   centre-relative dock offset, veto entry, exit cell, reservation check
   and the art anchor must re-index + full retest); (c) soft alpha fade at
   the drape edge (art-only). NOT a rectangle clip (proven slice artifact).
4. Chunky dark intake pixels + black fringe at the bay mouth (hq4x + hard
   alpha on the upscale) — art polish.
5. Mirrored reverse track (Luke's line-up-then-reverse spec, SS
   2026-08-05 00-08-56) — the only way to real reverse-in at SE.
6. WF apron restoration, same recipe as TSPROC once its look is signed off.
7. TS harv at TD refinery pose (Aseprite, together) — the last unmade
   placement; TS-at-TD currently generic W-facing park.
8. Queued from earlier: SMOKEY harvest puff port, voxel brightness pass
   (TSHARV/TSMCV vs the TS screencast), TD-units-from-TS-factories tech
   leak, refinery buildup pad check, conyard light rotation + remaining
   2026-08-04 verdicts.

## SESSION END 2026-08-04 evening (superseded)
**Surface = LINUX DESKTOP prefix, deployed + md5-verified at `1e93a870` as
Luke quit ("nice one"). ⚠ The Deck is STALE at `2d8a5dbb` (clipped dish, old
sizes, sideways harvester) — push there before any Deck play. ⚠ The desktop
prefix no longer holds the AI instance's build (today's TS deploys overwrote
it) — re-deploy from main before resuming AI work there.**

**Landed today (all committed on `ts-units`, live-fix loop with Luke):**
- Power plant → TS-authentic 2x2 (RA POWR plot, 48 art) — **SIGNED OFF**.
- Conyard: full 4x3+bib kept; art grid-matched then 6% inside the plot
  (overscale 0.94) after "still slightly big"; rotating light = FULL-CYCLE
  anim (first convention-breaker). AWAITING VERDICT on the 0.94 size.
- Refinery: plume unclipped for real — the no-bib union runs the width fit
  at 5.45x (composite 643 HD px tall); canvas 512x928, stub 96x174 sized so
  the disc bottom sits ON the plot's south edge (the 126-stub version draped
  the bib and Luke rejected it). NTREFN_B = second convention-breaker (one
  20-frame plume cycle, `_anims[]` 10→20).
- TSHARV/TSAPC drove 90° off heading: voxel renders start at E (CCW); RA
  frame space 0=N — ZIPs rotated +8 in place, packer bakes it for regens.
  Disruptor untouched (turret tracking play-verified 08-01).
- **Selection boxes: launcher sizes them from DimensionX/Y = FOUNDATION
  cells −20% (bdata Dimensions()), art never consulted — the old "box =
  stub box" note was a MISREAD.** Art-sized-dims experiment FAILED (box
  centres on the plot → brackets float a square below the bib, clicks got
  worse) and is REVERTED (`c49f5242`/`eadc900e`). Foundation box = the
  accepted default; don't re-chase without a new mechanism.
- Verify traps learned: packed TGAs are content-cropped → clearance must be
  read from meta crop[1], NOT the TGA bbox; razor-thin canvas margins die to
  ~2px hq_scale silhouette bleed — leave real headroom.
- TS art re-extraction recipe (scratchpad was gone): TIBSUN.MIX →
  `tools/ts_extract.py` (TEMPERAT/ISOTEMP/CACHE/SIDEC01 members) →
  `ts_shp.py` → TS_ART_DIR; packer skips absent art dirs, XML/CSV emits
  idempotent, so partial repacks are safe.

**ALSO NEXT SESSION (Luke, session close): TD units are buildable from the
TS barracks and TS war factory.** Tech-tree leak: TSPILE/TSWEAP are being
accepted as production sources for TD-era units — likely the TD units'
prereq/`own &` masks or the factory role checks treat any same-RTTI factory
as era-valid rather than gating on the era building set. Decide the rule
with Luke (strict era separation vs deliberate cross-era production), then
audit BOTH directions: TD yards building TS units too, and what the sidebar
offers when mixed-era factories coexist.

**NEXT SESSION = HARVESTERS (Luke's pick at session close). Scope (Luke):
dock ALL 3 harvesters at the TS refinery, and the TS harvester at the TD
and RA refineries — visual alignment worked out together in Aseprite from
`~/Desktop/docking-art/` (prepared: all 3 harvesters full-canvas-aligned
facings, RA unload run = harv-ra 96-110, all 3 refineries incl. TDPROC's
attach-dock anims; see its INDEX.txt; RA HARV/PROC re-extractable from
TEXTURES_RA_SRGB.MEG via meg_extract.py).** Also: verify nose-first
driving (the +8 fix), one full watched dock cycle at TSPROC (approach,
tip-up, unload, credits tick, exit), TSHARV auto-return when full
(Tiberium_Load fix), then any residual dock-spot polish (pad =
`Coord+3*MCW+2`, sub-cell nudge dial = the TDHARV NUDGE constants in
unit.cpp Mission_Unload; dock facing dial = DIR_SW turn in
RADIO_BACKUP_NOW). Logs-first: MOD_DEBUG_TSUNITS.txt DOCK-START lines
(⚠ log sometimes lands in pfx/drive_c/users/steamuser/ instead of
Documents/CnCRemastered).

**Refinery smoke polish (Luke's session-close SS, 19:00):** the plume's
dissipate/reform frames (10-16 src px of content) scale to blocky "dead
pixel" specks at the chimney tip while the smoke is between puffs — plus an
unexplained solid-black chunk right of the chimney in the same SS. Luke's
suggestion: make the smoke effectively continuous. Options: drop the
near-empty frames from the cycle (shortens N — engine `_anims[]` count moves
again), soften/floor the alpha for tiny frames instead of the hard 128
threshold, or check whether the deferred NTREFN_C (144-canvas anim, needs
offset compositing) is TS's own second smoke layer that fills the gap.

**TSHARV geometry (Luke's SS 19:25, TD+TS harvs on the same cell row don't
line up):** (a) the sprite is ANCHORED ON THE FRONT CABIN — the voxel origin
is offset (packer note: scoop reaches ~235 px from origin on the 512
canvas), so it pivots around the cab when turning and sits low-left of its
cell. Fix lead: compute the 32-frame content-union centre and shift ALL
frames by one constant offset so the rotation-envelope centre = canvas
centre (zip-level, preserves registration — same trick as the +8 facing
reorder). (b) Selection box far too big: ShapeSize=64 vs TD harv 48 — after
re-centring, the canvas/ShapeSize can likely drop to 48-class. Both fixes
fold naturally into the harvester docking session.

**Also unverified in-game:** conyard 0.94 size verdict, refinery
bib/plume look, radar dish top, depot repairs, conyard light
rotation. **QUEUED AFTER:** WF exit-door anim (GTWEAP frame 1), component
towers / infantry / Orcas / audio per plan below.

## Superseded same-day block (2026-08-04 daytime)
Both session-close verdicts are implemented, built, and deployed to the
DESKTOP prefix (md5-verified; Deck still on `2d8a5dbb` with the clipped
dish — push there when switching back):
- **(a) power plant dialled down**: stub 66x66, packer canvas 352x352,
  3x2 grid unchanged.
- **(b) conyard full 4x3+bib**: the bdata/rules/stub/canvas edits were
  ALREADY in `caf2153e` — but its TSFACT ZIPs were packed BEFORE the
  544-canvas edit (byte sizes unchanged = stale 512 art). Regenerated at
  544x384. Art re-extraction needed (scratchpad was gone): TIBSUN.MIX →
  `tools/ts_extract.py` (TEMPERAT/ISOTEMP/CACHE members) → `ts_shp.py`
  → `TS_ART_DIR` scratchpad; packer skips buildings without art dirs and
  the XML/CSV emits are idempotent, so a 2-building repack is safe.
- **(c) radar 72x150 canvas fix deployed** (desktop) — verify dish top.
TEST LIST for the desktop walk: conyard now a full 4x3 plot with BIB1 +
bigger art (MCV deploy/undeploy geometry unchanged); power plant reads a
touch smaller inside its grid; radar dish un-clipped; plus the round-2
regression list below.

## ⭐ SESSION END 2026-08-04 ~01:00 — RESUME HERE
**Deck build = `2d8a5dbb` (md5-verified, deployed as Luke quit). The whole
night was the building size/geometry saga — 5 fix batches; full record in
the batch blocks below.** Final state:
- SIZE SIGN-OFFS: WF ✓ ("finally the right size"), tech centre ✓, repair
  bay ✓, TSFACT ✓ (4x3 since batch 1). AWAITING FIRST LOOK: refinery at
  full 4-cell width, radar + power plant at their new 3-wide/3x2 size
  (grid steps are quantized — if they read too big there is no smaller
  grid-matched step; discuss before touching), barracks on its 3x2 grid,
  masked (pad-free) WF/refinery buildups.
- THE PLACEMENT RULE (Luke): art matches the build grid; grow the GRID to
  fit big art; full-width RA slab spans the building. No baked pads.
- VERIFIED WORKING tonight: TSPROC dock (TDHARV + TSHARV DOCK-STARTs),
  radar minimap, give-way crash fix (no recurrence after `95d64e1`).
- NOT yet re-verified after the 4-wide refinery: one dock cycle (lane
  moved cells, stock flow), TSHARV auto-return (Tiberium_Load fix),
  depot repairs, halved idle anims, damaged states (frame 2), sizes above.
- FIRST-LOOK VERDICTS (Luke, session close), both for next session:
  **(a) power plant slightly OVERdone — dial the art down a touch** (keep
  the 3x2 grid; stub ~66x66 so the art sits just inside the grid; one-number
  change in build_tfassets.sh + packer canvas 352x352).
  **(b) conyard (TSFACT) reads SMALL — Luke's spec: make it a FULL 4x3 plot
  WITH a bib** (currently rows 1-2 occupied + overlap row, Bib=no). Recipe
  ready to apply: `TsFactList43` = all 12 cells + overlap NULL; rules
  `Bib=yes` (4-wide → BIB1); art up via stub 102x72 / canvas 544x384
  (f≈0.80 → 102x69 classic, ±3px side overhang). MCV deploy/undeploy
  geometry unchanged (NW-origin/SE-return; 12-cell clear check).
  **(c) radar TOP-OF-SPRITE CUT-OFF: FIXED LOCALLY, UNCOMMITTED-at-first,
  now committed but NOT DEPLOYED** — canvas was 20px too short for the
  100-classic-tall dish (stub 72x108 → 72x150, canvas 384x800, margin 48;
  meta top margin 11 confirms intact). **Deploy this first thing next
  session** — the Deck build still shows the clipped dish.
- QUEUED NEXT: TSHARV movement facing (voxel facing order, (8-f)%8 rule),
  WF exit-door anim (GTWEAP frame 1 = door-open variant), remaining
  checklists below, then component towers/infantry/Orcas/audio per plan.

## ⭐ RESUME HERE — WALK ROUND 1 FINDINGS ALL FIXED + REDEPLOYED (2026-08-03
## late); NEXT: walk round 2 (same checklists + the round-1 regression list)

**Luke's first walk (2026-08-03 evening) surfaced 7 issues; all fixed, rebuilt,
Deck-deployed the same night. The game also crashed once (~F14200, no minidump
anywhere — ClientG AND InstanceServer both gone; ask Luke crash-vs-freeze).**

1. **Harvesters never docked at TSPROC (DOCK-START=0) — the likely
   crash/livelock trigger.** The refinery radio protocol gates on literal
   `STRUCT_REFINERY || STRUCT_TDPROC` in ~15 sites (ARE_REFINERY returned
   NEGATIVE for TSPROC; RADIO_DOCKING had no TSPROC pad case so MOVE_HERE got
   a garbage target; the busy-dock guard let queued harvesters thrash the
   current customer — matching the endless A* fallback storm in tf_astar.log).
   ALL sites now take TSPROC. Pad = the passable APRON-row cell two south of
   the centre cell (`Coord + 3*MAP_CELL_W + 2` — RA's DIR_S-of-centre lands
   inside our occupied 4x2 plot). N-of-pad = plot south row, so the PCP_END
   arrival check and the direct BACKUP_NOW → IM_IN handshake work unchanged;
   the harvester unloads standing ON the apron, as in TS.
   `Is_Refinery_Dock_Cell` (Layer B pad reservation) got the TSPROC clause.
2. **TSRADR gave static, not radar:** the scan-bit shadow activated the radar
   but the jam loop (`STRUCT_RADAR||TDHQ||TDEYE` chains) didn't know TSRADR →
   permanently "jammed" → static. TSRADR added to all 7 radar-facility chains
   (radar-on, sting count, jammable-by-MRJ, destroy/capture spied, infiltrate).
3. **Dish anim snapped back:** GTRADR_A's 15 healthy frames are HALF a sweep.
   Baked forward+reverse ping-pong (28 frames, bdata `{0,28,3}`, ZIP 56) —
   the TS dish scans back and forth.
4. **Purple flash in radar buildup:** GTRADRMK carries debris FRAGMENT frames
   after the real run; the >800px `real_frames` filter passed them (buildup
   snapped to a shard at the end). Post-peak area cut added (all four MAKE
   ZIPs verified fragment-free).
5. **Buildup count mismatch:** the `_td_bdonors` loop unconditionally
   overwrote construction anims with the donor's count (TSPROC/TSWEAP ship 19
   tiles, donors count 20 → purple final frame). Donor Init_Anim now applies
   only when the building had no own MAKE stub.
6. **Selection box floated in empty headroom** (launcher selection box = the
   classic stub box): stubs tightened to hug the art — TSPROC 96x102,
   TSWEAP 96x96 (apron halo kept below the plot).
7. **Scale verdicts:** TSRADR bib restored (`Bib=yes`, barracks look — Luke).
   TSWEAP +10% overscale (Titan-vs-WF mass complaint), TSPROC +8% (still
   "too small" after round 1; it IS authentically low-profile — the TS
   refinery is a wide flat disc — the overscale + full-width is the honest
   maximum without clipping structure; revisit only if Luke still objects).

**BATCH 4 (2026-08-04 small hours, `3c7d3350`, Deck-deployed): THE PLACEMENT
RULE, locked by Luke — art matches the build grid; the GRID grows to fit big
art, never the art shrinking; the standard RA slab spans the full building
width (this also settles the pads: no baked apron, full-width bib).**
- TSPROC: disc at FULL 4-cell width (96x96 stub, 512x512), BSIZE_43 with the
  RA dock-lane pattern translated to 4-wide (`TsProcList43`: row-2 centre
  cells free, pad one south of the centre cell — stock dock flow +
  Is_Refinery_Dock_Cell work unchanged), Bib=yes → BIB1.
- TSWEAP: art UNTOUCHED (Luke: "finally the right size"); footprint 4x3 so
  the grid matches the hangar, BIB1 spans it, TsExitWeap43 restored.
- TSPILE: 3x2 grid under the 72-wide art (was spilling over 2x2).
- WF exit-door anim: GTWEAP frame 1 is the door-open healthy variant —
  queued as future polish (swap base frame / overlay during Exit_Object,
  RA WEAP2-style).
- Size-saga honesty note: the sprite only actually grew in batch 3 (hangar
  73→91 classic) and batch 4 (disc 72→94); the earlier "size pass" mostly
  removed dilution, which is why Luke kept reporting no change.

**BATCH 3 (2026-08-03 latest, `7df1314`, Deck-deployed): Luke's round-3
verdicts — the wide-footprint design is DEAD, long live TD-style 3x3.**
- **TSPROC = RA-refinery geometry clone** (BSIZE_33 + RA occupy/overlap lists
  incl. the passable dock lane, DIR_S pad, RA free-harv spawn, Bib=yes; the
  special apron-pad dock geometry and Is_Refinery_Dock_Cell clause reverted).
  **TSWEAP = TDWEAP parity** (3x3, rows 1-2 + row-0 overlap, TD exit ring,
  Bib=yes, joins the factory RUN_AWAY chain). Both drop the baked apron
  plates; art fills the box — the plate-passability complaint dissolves
  (the plate no longer exists; the RA slab below is passable as normal).
  **TSPILE 72x48 stub** (infantry were taller than the barracks).
- **UNIVERSAL anim convention found: every TS anim SHP packs healthy frames
  then DAMAGED frames inside its usable window** (dish 15+15, tech dome 8+8,
  depot pad 5+5, barracks flag 7+7 — all confirmed visually). `loop()` splits
  even windows; ALL `_anims[]` counts halved (PILE 28, PROC 10, WEAP 8,
  HPAD 8, TECH 8, DEPT 35, FACT 30, POWR 12, RADR 28 ping-pong). This was
  Luke's "tech centre / repair bay animation broken".
- **TSDEPT was missing from every `STRUCT_REPAIR||STRUCT_TDFIX` chain** (~17
  sites: dock/IM_IN/CAN_LOAD, rally, sell-refund contact, aircraft repair,
  Find_Docking_Bay cross-match) — that was "can't send units for repair".
- **`Tiberium_Load()` returned 0 for UNIT_TSHARV** — a full TS harvester
  never read as full, so it sat idle instead of heading home (Luke's report).
- Map-right-edge apron clipping: MOOT (aprons gone with the 3x3 art).
- STILL QUEUED: TSHARV movement facing + any residual dock-spot polish;
  GTWEAP frame 1 (door-open) as a future exit anim.

**ROUND 2 LIVE FINDINGS (2026-08-03 very late, all fixed in `95d64e1`,
Deck-deployed):**
- **THE CRASH = give-way recursion stack overflow (0xC00000FD), minidump-
  PROVEN on both InstanceServer dumps** (22:40 + 23:18; EIP in Can_Enter_Cell
  under the Assign_Destination → Start_Of_Move → Give_Way/Infantry_Give_Way →
  another unit's Assign_Destination cycle; scan-walker: scratchpad
  `dumpwalk.py`, worth keeping in tools/). Fix: the immediate Start_Of_Move
  in DriveClass::Assign_Destination is optimisation-only (mission AI reruns
  it every tick) and is now depth-capped at 8. Dumps land in the prefix's
  `AppData/Roaming/CnCRemastered/` — check there FIRST next crash.
- **Dock fix VERIFIED live before the crash:** TDHARV and TSHARV both logged
  DOCK-START at TSPROC.
- **Damaged-frame convention: TS building SHPs = frame 0 healthy, frame 1
  LIGHT damage, frame 2 HEAVY damage, 3-5 rubble fragments.** All nine
  shipped damaged=1 → damaged buildings showed the light stage and read as
  pristine. All now use frame 2 (bib plates too).
  (Corrected 2026-08-06: frame 1 was recorded here as a "healthy variant —
  WF door-open, radar mast up" and treated as a free door animation. It is
  not; building a door on it made the factory look shot up while producing.
  The real door is a separate SHP — see the top block. Whether any TS
  building has a genuine frame-1 variant is unverified; assume damage.)
- TSWEAP stub 96x84 (canvas hugs the squat hangar; brackets were floating).
- Luke: TS WF vs TD WF — TS is authentically squat/wide vs TD's tall box;
  +10% overscale applied earlier stands.
- **QUEUED AFTER THE BUILDING ISSUES (Luke, 2026-08-03): TSHARV dock polish**
  — (a) dock LOCATION tuning at TSPROC (park spot vs the ramp art; the pad
  cell is `Coord+3*MCW+2`, sub-cell nudge is the dial — see the TDHARV
  NUDGE constants in unit.cpp Mission_Unload), (b) **TSHARV faces the wrong
  direction when MOVING** — likely the voxel-render facing order vs RA's
  32-facing convention (check `renders_tsharv` frame order / the (8-f)%8
  reorder rule from the walker ports); dock facing dial = DIR_SW turn in
  RADIO_BACKUP_NOW.
- **OPEN: "units can't travel over the TS refinery/WF plate."** Sim-side the
  row below the plot is plain passable ground (nothing occupies it; only the
  single TSPROC dock-pad cell is harvester-reserved, same as RA's pad rule).
  Suspicion: the launcher hit-tests the sprite, so clicks on the apron art
  select the building instead of issuing a move. TEST in round 3: order a
  unit PAST the plate (path crossing the apron row) — does it drive across?
  And click directly on the plate — move order or building selection?

**Walk round 2 = the same two checklists below PLUS:** TSHARV full loop at
TSPROC (approach → park on apron pad under the ramp → fume plume → credits →
DOCK-START lines in MOD_DEBUG_TSUNITS.txt), radar minimap actually renders
(not static), dish ping-pong, clean buildups on all four (no purple, no
shard), tight selection boxes, undeploy/redeploy TSFACT, and whether the
crash reproduces (grab `pgrep` + logs immediately if it does).

**The size pass is implemented, built and Deck-deployed (md5-verified), NOT
yet play-verified.** All four rejected buildings rebuilt:

- **TSPROC** — stub 96x120, canvas 512x640: composite (base + NTREFNBB apron)
  spans the full 4-cell width (~40% linear bigger than the rejected build),
  structure over the plot, apron dipping into the passable row below.
  `Bib=no` (the doubled RA slab is gone).
- **TSWEAP** — same 96x120 treatment, `Bib=no`. TS-authentically squat; if it
  still reads small in the walk, the lever is overscale + clipping the apron's
  side tips (noted, not applied).
- **TSRADR** — stub 48x96 (was donor-TDHQ 48x48): full 2-cell width, dish
  rising a row above the plot, Obelisk-style. **Broken-anim ROOT CAUSE:
  GTRADR_A's 30 usable frames are 15 healthy rotation + 15 TORN-DISH damaged
  frames** (the engine's shapes-N..2N-1 damaged convention applied *inside*
  the anim SHP) — the old pack cycled all 30 as the healthy idle. Now healthy
  cycles 0-14, damaged run cycles 15-29, bdata `{0, 15, 3}`, ZIP 30 frames.
  `Bib=no`.
- **TSFACT** — TS-authentic **4x3** (BSIZE_43 + TsList43/TsOList43, own 96x72
  stub; fills the box, reads bigger than the RA yard). Deploy/undeploy round
  trip is geometrically consistent (deploy origin = MCV NW-adjacent; undeploy
  MCV = Coord SE-adjacent — same cell), but 4-wide deploy is NEW ground:
  test deploy → undeploy → redeploy in the walk. `Bib=no`.

**⭐ RENDER CONTRACT (settled 2026-08-03, supersedes the "canvas bottom =
footprint bottom" Obelisk inference):** the launcher maps the HD canvas onto
the classic-stub-dims box **CENTERED (both axes) on the BSIZE box center**
(`CenterOffset` geometry + launcher-render-contracts rule 1). Stub height
beyond the box splits into EQUAL art halos above and below — content placed
low in the canvas renders below the plot. That's how the apron row works with
zero DLL draw changes; classic C&C tall art (Tesla/Obelisk, content flush to
frame bottom) always drew its base slightly into the row below and reads
naturally in iso. No probe deploy was needed.

Pipeline notes: `ts_pack_tree.py` gained a size-pass fit mode (union
width-fit + bottom-margin anchor, `SIZEPASS` table) and per-run anim windows
(healthy/damaged index lists — the GTRADR_A split). Stubs for all four (incl.
new TSRADR/TSFACT + MAKE stubs at donor-matching frame counts 20/32) are in
`build_tfassets.sh`. Grid-overlay previews validated offline before deploy.

**Then the sign-off walk (units wave included):** the two checklists below —
all nine buildings + the four new units, with special attention to the
TSHARV harvest → dock → fume-plume → credits loop at the 4x3 TSPROC
(`MOD_DEBUG_TSUNITS.txt` logs FREE-HARV grants and every DOCK-START).
Size-pass-specific additions:
1. The four resized buildings vs TD counterparts — and TSPROC/TSWEAP apron:
   units should drive OVER the apron row (it's the unoccupied row below the
   plot; the art just paints it).
2. TSRADR dish loop stays clean when healthy; torn dish appears ONLY damaged.
3. TSFACT: TS MCV deploy → 4x3 yard up → undeploy → MCV back → redeploy.
4. Buildup anims on all four (MAKE canvases changed with the stubs).
5. Placement UI on TSPROC/TSWEAP/TSFACT: the proposed-building footprint
   overlay should still show the right cells (BSIZE box unchanged for
   PROC/WEAP; TSFACT now 4x3).

## Units wave SHIPPED 2026-08-01 evening (on top of the building tree)

**Deployed to the Deck (DLL 17:59). The vehicle wave is in: TSHARV (Harvester),
TSSMEC (Wolverine), TSSONIC (Disruptor), TSAPC (Amphibious APC) — all TS-stat
verbatim from the extracted TS RULES.INI, all behind the TS tree prereqs, none
play-tested yet.** Packer: `scripts/ts_pack_units_wave.py` (worktree-relative MOD
path — never the absolute repo path; ⚠ `ts_pack_art.py`/`ts_pack_walkers.py`/
`ts_stealth_hq.py` still hardcode the MAIN repo and must not be run from the
worktree as-is). Diagnostics land in `MOD_DEBUG_TSUNITS.txt` (free-harv grant +
every dock start) and `MOD_DEBUG_CANBUILD.txt` (filter now takes TS-prefixed too).

**Units-wave test additions to the checklist below (test with the buildings pass):**
1. TSPROC finishes → a TS Harvester drives out (grant now wired; it did NOT
   exist this morning). It harvests, returns, parks at the refinery, vents the
   green fume plume, credits tick in, then re-harvests. `DOCK-START` lines
   appear in MOD_DEBUG_TSUNITS.txt. ⚠ 4x3 dock geometry is still the risk.
2. Wolverine from TSWEAP: 12-step walk anim reads at all 8 facings, MG report
   on firing (placeholder MGUN11 until the TS audio wave), dies fast (175 HP).
3. Disruptor from TSWEAP (needs TSTECH): turret tracks, GREEN piercing beam,
   damages everything along the line incl. friendlies (TS-authentic), no
   spark helix (that stays railgun-only).
4. APC from TSWEAP (needs TSPILE): loads 5 infantry, crosses water (hover
   stand-in), unloads on the far shore.
5. Crate rolls unchanged: TS marquee table still Hover MLRS/Titan/Mk. II;
   the new four can appear only via the generic goodie pool like any unit.

**Known deviations (documented in rules.ini comments):** SonicZap per-frame
wave damage translated to one 140 AmbientDamage application per object
(TS 1/3-per-frame is meaningless under RA's one-shot line sweep); APC hover
locomotor for TS amphibious; weapon reports are TD placeholders (MGUN11 /
OBELRAY1) pending the TS audio wave; Disruptor turret baked centered (engine
TurretOffset field is unused by the RA draw path).

**Still queued after this:** component towers (Vulcan/RPG/SAM — turreted
TDGTWR pattern), infantry (E1/E2/Ghost), Orcas, TS audio wave, NTREFN_C
refinery anim offset compositing, TS GDI/Nod badge emblems (Luke supplies).

## Building-tree state + Luke's original test checklist (2026-08-01 morning)

**Deployed to the Deck (DLL 12:59, branch `ts-units`, worktree `../tf-ts-units-worktree`,
all committed through `dd0d18a`). NOT yet play-verified past the war factory.**

**Shipped:** the complete GDI TS building tree — TSFACT yard + TSMCV (rare crate
1-in-32 in release; dev builds spawn one beside the human start) and all nine
buildable structures via the Stealth Recipe: TS idle anims + animated damaged
states, real-frame buildups, TS bib aprons (PROC/WEAP/HPAD/DEPT), real TS cameo
icons, full tree prereqs (vehicles+MCV on the TSWEAP chain). Footprints are
TS-authentic with TD mass as baseline: PROC/WEAP 4x3 (new BSIZE_43), TECH 3x2,
SILO 2x2, others as-was; changed ones declare classic dims via TFASSETS stubs.
Engine fixes en route: heap-order invariant (bdata/udata tail comments),
StructType char→short, **EA's sidebar off-by-one (Buildables[75] OOB write —
UPSTREAM THIS TO MAIN, it can hit any big-roster game) + MAX_BUILDABLES 75→120**,
TS types exempt from cameo badging + producer masks (TF_Is_TS_Tree_Type),
TS yard⇄TS MCV round-trip both directions.

**Luke's pre-work test checklist (~15 min, fresh crates-on skirmish):**
1. TS MCV beside start → deploy → yard up, buildup clean (no purple).
2. Sidebar: every TS entry shows its TS icon (no blank tiles, with AND without
   owning a second faction's yard — the badge bugs bit both ways).
3. Walk the whole tree: power→barracks→refinery→silo→WF→radar→helipad→tech→depot.
   Each building: buildup anim, idle anim runs (crane/fans/dish/flag), bib present.
4. Sizes vs TD counterparts: refinery + WF (4x3), tech (3x2), silo (2x2).
5. ⚠️ Harvester docking at the 4x3 refinery — dock offsets were tuned on 3x3
   shapes; watch for misaligned/dancing harvesters. Likeliest thing to be broken.
6. Build Titan/Hover MLRS/Mk. II/TS MCV from the 4x3 WF — clean exits.
7. Damage a few buildings — damaged art + anims still cycling.
8. Sell all non-TS yards → TS tree stays buildable; undeploy yard → TS MCV back.
9. Long game with two trees → sidebar survives past 75 entries (the off-by-one).

**Next work queued (in order):** component towers (Vulcan/RPG/SAM — turreted
TDGTWR-style ports, NOT the static recipe), TSHARV + Wolverine + Disruptor +
APC (units wave), infantry (E1/E2/Ghost), Orcas, TS audio wave (dormant-sample
hosts), NTREFN_C refinery anim (offset compositing). Badge art: Luke supplies
TS GDI/Nod emblems later — cameos stay pristine until then. Refinery grants an
RA harvester until TSHARV lands. AI use of the tree waits on W2.9 (other
instance's lane).



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

### Asset inventory — extracted + decoded 2026-08-01 (scratchpad `ts-extracted/`, regenerate via ts_extract.py + ts_shp.py if the scratchpad is gone)

| Building | Base (canvas) | Anims (frames incl. empty halves) | MK | Cameo |
|---|---|---|---|---|
| TSPILE | GTPILE 96 | _A 16, _B 16, _C 28 | 40 | BRRKICON |
| TSPROC | NTREFN 192x168 (TS refinery uses NOD art, 4x3) | _B 40, _C 32 (144-canvas!), + production anims _A/_AR deferred | 40 | REFICON |
| TSSILO | GTSILO 96 | _B 64 (fill-level frames? verify vs STORAGE contract) | 38 | SILOICON |
| TSWEAP | GTWEAP 192x168 | _A 32, _B 16, _C 8 | 40 | WEAPICON |
| TSRADR | GTRADR 144 | _A 60 (dish) | 40 | RADRICON |
| TSTECH | GTTECH 192x120 | _A 32 | 40 | TECHICON |
| TSHPAD | GTHPAD 96 | _A 32 | 38 | HELIICON |
| TSDEPT | GTDEPT 144 | _A 20, _B 14 | 20 | FIXICON |
| TSVULC/TSROCK/TSCSAM | GTCTWR_B 64 / _C 96 / _D 64 (48-canvas, TURRET rotation frames — port like the TDGTWR turret pattern, not the static recipe) | GTCTWRMK 22 | TWR1/TWR2/TWR3ICON |

⚠️ NTREFN_C is a 144-canvas anim on a 192x168 building — needs offset compositing,
not the same-canvas paste. Anim usable length = first half (second halves are EMPTY
= damaged buildings don't animate). Silo has no idle anim; its _B 64 frames likely
map to the STORAGE fill-level contract (5 levels + damaged — verify before packing).

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
