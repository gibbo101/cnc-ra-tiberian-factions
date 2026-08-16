# TS GDI tree — implementation plan (2026-08-01)

## ⭐⭐⭐ SESSION 2026-08-13 EVENING → 08-14 — the building walk + fix marathon

**The 3x2 footprint pass: conyard + bay boxes VERIFIED IN PLAY** ("FIXED!",
Luke, 00:10) — desktop DLL `d4bb09e2`, commit `55e4253c`. Conyard (TSFACT)
and dropship bay (TSDROP) went **BSIZE_33 → 3x2**; the empty top row was
what held their boxes off the art (contract #7 below). **STILL OWED next
session, fresh skirmish:**
1. **TS MCV round-trip**: deploy → 3x2 yard → undeploy → MCV back →
   redeploy. The one real regression risk (machinery is size-generic and
   TDFACT-proven, but eyes on it).
2. **Bay delivery end-to-end**: Mk. II ordered → pod lands on the deck's
   visual centre (landing bias re-derived 160→32 leptons) → cargo steps
   onto the concrete → walks clear. Mech Division too (crash soak).
3. **Refinery box DECISION: RESOLVED 2026-08-16 — round-1 fit accepted**
   after a played-and-reverted 4x5 height-trick attempt (full record in
   the Open queue, item 2).

**⭐ THE NIGHT'S HEADLINE — selection-box contract PROVEN (contract #7 in
`launcher-render-contracts.md`):** the launcher centres a building's box on
its BSIZE plot and takes ONLY DimensionX/Y from the DLL. Five falsified
probes in one night (CenterCoordY, dims-anchoring, CellY, doctored
OccupyList, PositionY — the last visibly moved the SPRITE, detaching the
refinery from its apron). Never probe again. A box that reads wrong means
the PLOT is wrong for its art — TDFACT (true 3x2, box fits) vs TSFACT (3x3
with an empty row, box high) was the control pair that cracked it, Luke's
find.

**Shipped this session, ALL play-verified by Luke:**
- **Walk verdicts:** TSPILE box 2x2-north ✓, TSPOWR + TSRADR south-row
  footprint (Tesla/Obelisk `List22_0011` pattern — ghost 2x2 incl. bib,
  build/walk behind the tower) ✓ "great job". TSSILO / TSTECH / TSDEPT pass
  as-is.
- **Damage states → LIGHT (frame 1)** across the TS tree ("damage states
  are good"); bay keeps its approved weathered heavy. **Heavy-on-red
  stretch DITCHED (Luke).**
- **Pads go UNDER everything:** aprons are no longer map state — the
  renderer derives them from the owning building's footprint
  (`_aprons` table, dllinterface). Ore draws over them ("ore on pad is
  good"), bibs stamp over them and layer correctly, nothing can erase the
  concrete, cloak-hide preserved, they vanish with the building.
  `Bib_And_Offset` no longer returns them; stale-cell export guard added.
- **Mk. II can't-damage bug fixed + verified:** `Target_Coord` anchors
  TSPROC (dock-lane hole) and the tall towers (art-spill row) to occupied
  cells; the railgun sweep always damages its aimed-at object. "TS ref and
  radar can be damaged again."
- **Rich-start lever** replaces flat-$1 (`tf_cheap.flag` now = 1,000,000
  credits at skirmish start, og prices): the $1 PurchasePrice was failing
  EA's free-harvester gate (building.cpp:4166 compares PurchasePrice vs
  Raw_Cost). FREE-HARV verified live repeatedly.
- **Refinery box:** settled at the round-1 fit (south edge approved). The
  wished-for 2 tiles of extra headroom is engine-impossible on a centred
  box — closed under contract #7.

**Open from tonight (see Open queue):** helipad footprint call still
pending (Luke's 2x3+bib vs my 2x2+bib counter); TSPROC blank-apron-tile
WARNING text in the packer is stale (aprons no longer stamp — reword);
`tf_orbit.flag` dead code still queued; crash watch stayed SILENT all
night through many Mech Division orders (soak continues).

---

**Workstream home: branch `ts-units`, worktree `../tf-ts-units-worktree`.** Deploy
surface is assigned per session — as of 2026-08-13 THIS instance deploys to the
**Linux desktop prefix**; the subterranean instance owns the Deck. The Deck's last
ts-units build is ancient (`2d8a5dbb`, 2026-08-03): a push + fresh deploy is owed
before any Deck play of this branch, whenever the Deck comes back to this lane.

*(Doc pruned 2026-08-13 on Luke's tidy-up list: consumed resume blocks deleted.
What remains: current state, the canonical shipped records, dead-ends, engine
facts/traps, the open queue, and the plan proper. Session narratives live in git
history and cross-session memory.)*

## ⭐⭐⭐ CURRENT STATE (2026-08-13) — cameo art day, crash fix verified in play

**Takeoff-sound crash: FIRST CLEAN PASS 2026-08-13** — Luke played a full
session on DLL `042a01e0` (the adpcm_ms re-encode, `2f70e2b5`), Mech Division
ordered and its takeoff survived; a live crash-file watch on
`AppData/Roaming/CnCRemastered/_Except_*.txt` stayed silent (newest records
remain last night's 00:24/00:30 pair). The div-zero was state-dependent, so
this is strong signal, not proof — keep half an eye on it for a week of play.

**Shipped this session (both play-approved "looked good"):**
- **Buildup de-gantried** (`e9ada2bf`): the bay's borrowed GTDEPTMK buildup now
  raises only the deck. Mechanism (in `ts_pack_tree.py`): `mk_clip_dir` clips
  every MK frame to the clip art's HEALTHY-frame silhouette (damaged bulges
  past it and leaks foreign pixels); remap-green inside the clip is keyed out
  and inpainted from the surrounding slab (vectorized neighbour fill — a
  per-pixel loop stalled); the deck's own rim-ring green is protected ONLY in
  frames that actually draw the ring (position-only protection shielded the
  gantry truss crossing the ring's path; that cost four repack rounds).
  Residue accepted at speed: 2-frame grey crane sliver, small nub, f0-1
  gantry shadow.
- **Luke's hand-made cameos installed** (`e25d429b`): Dropship Bay, Mech
  Division (3 Titans + dropbay badge), Mammoth Mk. II (dropbay badge), all
  composed on the reconstructed TS unit-cameo scene background. Both 300-frame
  countdown sets rebaked from the new bases. **`resources/custom-cameos/` is
  now canonical for hand-made BuildIcons** — both packers
  (`ts_pack_tree.py` emit_sidebar_data, `ts_pack_walkers.py`) prefer it over
  generated art, and `scripts/apply_custom_cameos.py` re-asserts every
  override in one pass (run it after any SRGB-touching packer and BEFORE
  `ts_mk2_cooldown_cameos.py`).
- **Art-source kit on Luke's desktop** (`~/Desktop/mech-division-art/`):
  Titan/Wolverine all 8 facings (shadowless, gold house-colour, transparent),
  bay deck sprite, and the **reconstructed blank TS cameo scene background**
  (three-donor agreement vote MMCH/SMCH/HMEC + row-wise fill; TS itself ships
  no empty scene cameo — XXICON.SHP is a riveted metal plate, different
  family). Wolverine cameo source = SMCHICON.SHP (not SMECHICON).

**Desktop prefix after session: DLL `042a01e0` + today's art, md5-verified.**

**Capped-cameo LOCKED + EVA gate: SHIPPED + play-verified 2026-08-13
("worked well").** At the Mk. II field cap the cameo swaps to a dimmed
red-X variant (`BuildIcon_TSHMEC_LK`, baked from Luke's art by
`ts_mk2_cooldown_cameos.py`); the cap OUTRANKS the reload countdown (time
never reopens a capped order, so a countdown there would lie). Both sidebar
click handlers consult `TF_Delivery_Order_Refused` (the same shared verdict
`Begin_Production` enforces, house.cpp) BEFORE speaking, so a refused click
gets "Cannot comply" instead of the false "Building" ack.

**Evening art pass (same day, all Luke-approved "love it", desktop prefix
current, DLL unchanged `1c142e0a`):**
- **Dropship at the fleet's 32°** (`3b75cc3d`) — canvas pinned 656 so the
  classic stub and drawn scale never moved.
- **Emblem fills the pad** (`40e190bf`) — 0.74 @2.15 (+6,-6), picked off a
  4-way sheet; ring measured, not eyeballed. Measurements + reasoning live
  on the `EMBLEMS` comment in `ts_pack_tree.py`.
- **Damaged pad weathered** (`01294c8a`) — damaged frames stamp against the
  healthy reference: same geometry, emblem erased where the deck is gone,
  charred through the deck's own burn mask.

**Remaining queue:** Mk. II cap → 3 on Luke's word (`TF_MK2_CAP`, one
constant). **Bay arc CLOSED.** Tidy-up list DONE 2026-08-13: the sidebar
off-by-one turned out to be already upstreamed to main on 2026-08-01
(`cf8ad1f6` — guard `<`, `MAX_BUILDABLES` 120, both sidebar implementations;
the queue entry had simply gone stale), and this doc's superseded tail is
pruned. All other open work lives in "Open queue" below.

## The dropship bay — canonical record (SHIPPED + play-verified 2026-08-12/13)

**The delivery sequence as SHIPPED (live-directed by Luke, ~10 builds):** the
TS Dropship (DSHP.VXL, west-facing, fine-grain render at the TS-authentic
6.4 px/voxel factor, GDI-gold accents) descends VERTICALLY over the deck — a
3-stage machine in `BulletClass::AI` (descend/flare → 4 s dwell → climb-out),
no map motion, so the shadow sits on the pad and GROWS through the descent
(shapes 1..3 = 55/70/85% pre-scaled silhouettes, bucketed by Height in
Draw_It). TS's own DROPDWN1/DROPUP1 play at touchdown/liftoff (dormant hosts
DINOYES/STRUGGLE). The Mk. II disembarks mid-dwell from UNDER the hull (north
edge of the front cell) and walks clear — to the bay's rally point if set
(`Rally_Unit`, it is a real factory), else two rows out. The bay wears a bib.
The cooldown arms at pod LAUNCH, is bay-wide via `TF_Is_Dropship_Delivered`
(one list: factory binding + both order gates + sidebar keep-alive +
countdown), and renders as a per-second baked-art countdown cameo, 5:00→0:01
(`scripts/ts_mk2_cooldown_cameos.py`, AssetName swap — Busy draws nothing,
fake Constructing miscounts queue clicks, tooltips flash on every asset swap
per-second: accepted). Drop height is 20 cells; flight profile: descent
Height/20 ~6.5 s, departure to `TF_POD_DEPART_CEILING` = 2x spawn; landing
point = deck's VISUAL centre (160 leptons north of plot centre; pod Sort_Y
bias 3 cells).

**Mech Division** (`UNIT_TSMDIV`): a purchasable TOKEN the pod expands into
3 Titans + 2 Wolverines, single-file every 9 frames, 2800 vs the 3400
sticker. **Mk. II field cap** `TF_MK2_CAP=1`, heap-counted — the CSII
quantity fold aliases mod-unit UQuantity slots, never trust them.

**Footprint:** the war-factory arrangement — BLOCKING = deck 3x2 via
ListWeap, bib row walkable, placement ghost = full 3x3 via an Occupy_List
placement split; deck art rides high via ts_pack_tree BOTTOM_MARGINS;
disembark = bib row's north edge, under the hull, on concrete. Cargo is set
down one row south of the pad — never on building-occupied cells (see traps).

**One-bay cap + sidebar safety (the 08-12 sidebar-lock fix):**
- `Can_Build`'s cap counts STANDING bays via
  `Has_Building_Active(STRUCT_TSDROP)` (non-limbo only, rebuilt every
  `Recalc_Attributes` pass, self-heals on sell/destroy) — never
  `Get_Quantity`, which counts from production START (`Tracking_Add` runs in
  the BuildingClass constructor, `building.cpp:2591`).
- glyphx `StripClass::Recalc` never evicts an entry with `Factory != -1`:
  placement and cancel both resolve through the sidebar entry
  (`Get_Pending_Placement_Object` walks `Buildables[]`), so evicting a
  mid-production entry strands `PlayerPtr->BuildingFactory` forever and
  locks the whole sidebar. Successful placement clears the link
  (`house.cpp:4278 factory->Completed(); Abandon_Production(type)`).

**Bay↔Mk. II binding:** RA's own kennel/dog split (`6de77e60`) — the bay
builds only `UNIT_TSHMEC` and only the bay builds it; the Mk. II's
prerequisite is `TSDROP,TSTECH`. `Who_Can_Build_Me` falls back to
`anybuilding` even when a non-matching factory holds `IsLeader`, so it never
returns NULL for ordinary vehicles. ⚠️ **`TFDropBayTimer` must stay
initialised in the HouseClass constructor** — uninitialised it reads as a
live cooldown, which presents exactly like a broken binding.

**Payload is a PARAMETER, not hardcoded to the Mk. II** — TS drop pods as a
GDI support power are parked on the same descent spine.

**Takeoff-sound crash record (2026-08-13 ~01:00, fix verified same day —
see current state):** two live ClientG crashes at the Mech Division takeoff
(00:24, 00:30), byte-identical `EXCEPTION_INT_DIVIDE_BY_ZERO` at
ClientG+0xAB5E69, `RAR_SFX_DROPUP1` on the crash-thread stack. ROOT CAUSE:
the dropship WAVs shipped as plain PCM while every proven dormant-host
override is MS-ADPCM — the client's ADPCM block math against a PCM header
divides by zero (rule now in `launcher-render-contracts.md`). Fix `2f70e2b5`:
both WAVs re-encoded adpcm_ms. Minidumps + EA's `_Except_*.txt` land in the
prefix's `AppData/Roaming/CnCRemastered/` — those text files are the fast
route to any crash's code+stack.

**Locked design decisions (do not re-litigate):**
- **Not a helipad, deliberately.** Outside BOTH `Is_Helipad` and
  `STRUCTF_HELIPAD`. `Is_Helipad` grants a FREE HELICOPTER at
  `building.cpp:4184` and makes the deck a general rearm target at
  `techno.cpp:7130`; `STRUCTF_HELIPAD` feeds prerequisites. Luke: "inert
  structure that receives the orca drop ship and releases a mk2 only".
- **`RTTI_UNITTYPE`** — the bay is where the Mk. II is ORDERED (Luke's pick).
  "Inert" means no free heli, no rearm target; it does not mean no production.
- **Cooldown per-HOUSE, not per-bay** — stays correct if the cap is raised.
- **Rim takes HOUSE COLOUR** (`REMAP_ALTERNATE` on `ClassTsDrop`) — a
  captured bay shows its owner's colour, wanted. The EMBLEM has zero pixels
  in the remap range, so it stays GDI gold whoever owns the bay.
- Smoothed-normals art REJECTED in place (detail loss) — `--normal-smooth`
  stays in vxl_render, unused.

**Dropship render recipe:** `vxl_render.py DSHP.VXL --frames 1 --yaw0 180
--px-per-voxel 6.4 --team-green 255,204,51 --elev 32 --canvas 656` then
`ts_pack_dropship.py`. Canvas stays 656 so the classic stub (123 = 656 x
3/16) and drawn scale never move. DSHP.VXL re-extractable from TIBSUN.MIX
via the TS padded-CRC32 name hash + ra_mix_extract's container crypto.

**⚠️ Unexplained, and NOT dropped: where a helipad-built Orca actually exits
is still unknown.** Three probes failed to find it (08-07/08): `Exit_Object`'s
`RTTI_AIRCRAFT` branch never runs; `HouseClass::Place_Object` is never
reached (`FIXIT_HELI_LANDING` commented out at `defines.h:121`); yet
`sidebarglyphx.cpp:434` demonstrably queues `EventClass::PLACE` for
`RTTI_AIRCRAFT`. Stopped blocking us (we own the bay's exit path), but it is
a real gap in what we understand about the engine. Do not treat it as closed.

**Dev levers currently armed in the desktop prefix:**
- `tf_cheap.flag` — everything costs $1 (build charge, sidebar quote,
  abandon refund, sell value; AI included per Luke). Opt-in, delete to
  disarm. ⚠️ Do not read AI economy behaviour from a run with this armed.
- `tf_orbit.flag` — the old from-orbit probe. Dead code on a dead path; the
  nuke-clone descent landed, so this is now removable (queued).

## War factory + refinery — shipped state (2026-08-06/07)

**The sandwich (SHIPPED `3a809c1e` era):** the war factory hides a vehicle
behind its shut door and reveals it through the opening, because the base
carries the bay INTERIOR and the overlay carries the whole hangar — RA's and
TD's scheme (`building.cpp:795` states the convention; TSWEAP was built
backwards until 08-07). Offline-verified in the engine's real layer order;
**an in-play confirmation is still owed.**

**⚠ THE EXIT POINT IS PINNED BY GEOMETRY, NOT TASTE.** Hangar art spans
y 3.9..71.8 of the 72px plot. A Titan or Mammoth Mk. II reaches 37 above and
29 below its exit point, so the head clears the roof below y=41 and the feet
clear the base above y=43: **a two-pixel window, and y=42 is it.** Depth is
the near face's job, not the exit point's. Any change to hangar size, exit
point, or a unit taller than ~66px breaks this.

**⚠ THE SORT BAND MUST REACH THE BUILDING'S SOUTHERN EDGE.**
`dllinterface.cpp` biases the `TSWEAP2` sub-object south of its base, keyed
on AssetName exactly as EA's own shadow/WAKE reordering. **384 leptons (36
classic px)** puts the line on the hangar's south edge; at 192 the vehicle
spawned 10.5px south of the base's sort point and popped in front after one
step. Sort facts: `SortOrder = (ExportLayer << 29) + (Sort_Y() >> 3)`; a
sub-object inherits its base's key plus the draw count; `STRUCT_TSWEAP`
sorts at its plot CENTRE (`building.cpp`) — that entry may be obsolete now
the apron is ground art, but changing it risks the 08-06 vanishing and wants
a deliberate test. `tf_sort.log` lives in `DLL_Draw_Intercept` under
`#if 0` — flip to 1 to read ordering back.

**Falsified — do not re-trust:** GTWEAP frame 1 is NOT a "door-open healthy
variant". Frames 0/1/2 are healthy / LIGHT damage / HEAVY damage; the real
door is a separate SHP (`DoorAnim=GAWEAP_D`, `DoorStages=9`,
`UnderDoorAnim=GAWEAP_1`, packed as the TSWEAP2 overlay through RA's WEAP2
path). `GTWEAP_D` frames 9-17 are magenta placeholders, not a damaged door
run. Whether ANY TS building has a genuine frame-1 variant is unverified —
assume damage.

### The aprons (both buildings, signed off 2026-08-07 — keeper work)

- `SMUDGE_TSWEAPBB` / `SMUDGE_TSPROCBB` (`sdata.cpp`) are bib-family
  smudges, **5 wide x 3 tall** over each 4x3 plot. `Bib_And_Offset` returns
  them at their offset, independent of `Bib=` in rules. Downstream is stock
  RA: `SmudgeClass::Mark` stamps `Smudge`+`SmudgeData`, capture re-owns,
  `Disown` clears. (`TSWEAPBB` sits at `MAP_CELL_W + 1` — one east, one
  south; the packer's apron config carries the offset as a third tuple.)
- **They draw as TERRAIN**, the TD-template ground entry copied field for
  field: `IsOverlay=true`, `IsSmudge=false`, **`IsTheaterShape=true`**,
  `Type=OVERLAY_V12` (pip-free), `SHAPE_CENTER|SHAPE_WIN_REL|SHAPE_GHOST`,
  centred on the cell, `ShapeIndex=SmudgeData`.
- **A theatre shape resolves out of `RA_TERRAIN_<theatre>`, not
  `RA_STRUCTURES`** — the tiles live in all three RA terrain tilesets under
  `TERRAIN/<THEATRE>/`. Snow had no mod tileset at all; the mod now ships a
  full `RA_TERRAIN_SNOW.XML` (a mod tileset REPLACES the base file, so a
  theatre you want one tile in has to ship the whole thing).
  `ensure_tileset()` in `ts_pack_tree.py` extracts on first run.
- **`Is_Clear_To_Build` refuses to build over ANY bib** — stock RA. The
  apron is exempted there (`cell.cpp`), so placement is decided by
  `Is_TS_Apron_Cell` alone, which vetoes the 4x3 plot and leaves the 5th
  column free. **Add any future apron smudge to that exemption too.**
- **The 5th column is deliberate** — the concrete tapers ~14 canvas px past
  the plot's east edge; RA's own bibs lie outside their footprints too.
  `ts_pack_tree.py` **fails the build** if the packed apron outgrows its
  grid — change the grid and `sdata.cpp` in the same commit.
- **The hazard stripes are BAKED gold** `(v, 0.82v, 0)` — the launcher
  remaps building sprites and **never** ground art, so ground art must carry
  its final colour. Fixed whoever owns the factory; if a house-tinted stripe
  is ever wanted, the stripes come out of the apron entirely instead.
- The buildup pours and keeps its own pad (`masks = {}`); its remapped
  stripes cover the apron's during construction.

**To add a third apron, all five move together** (`Is_TS_Apron_Smudge`
exists so placement and render cannot drift):
1. `SmudgeType` in `defines.h` + the `SmudgeTypeClass` in `sdata.cpp` (grid).
2. `Bib_And_Offset` branch in `bdata.cpp` (returns it at offset 0).
3. `Is_TS_Apron_Smudge` in `building.cpp` (drives BOTH the
   `Is_Clear_To_Build` exemption and the renderer's ground-entry branch).
4. `Is_TS_Apron_Cell`'s offset table, if its plot veto differs.
5. `aprons` in `ts_pack_tree.py`: `((plot cols, rows), (grid cols, rows))`.
The packer prints the grid the art actually needs.

**⚠ A SMUDGE STAMPS EVERY CELL OF ITS RECTANGLE, ART OR NOT.** The engine
writes the smudge to all `w*h` cells; a blank stamp **overwrites whatever
smudge that cell already had** (the war factory ate the power plant's bib
this way). **The grid must hug the concrete, not the plot**; the packer
WARNS on any blank tile it is about to emit.

### TSPROC footprint (4x3, shipped `7178f70f`)

4 wide x 3 high = 2 building rows + apron row; tall art overhangs the row
NORTH of the plot (radar treatment — that row stays passable, so units walk
behind the refinery, occluded by the tall art). Centre cell = the bay-mouth
pad (BSIZE_43 centre = row 1 col 2), so all Center_Coord-keyed dock geometry
re-indexes itself. ⚠ MCV-era saves with old 4x4 refineries mis-foot — fresh
skirmish only.

### Hangar resize (QUEUED 2026-08-13 — open queue 27)

With the Mk. II delivered by the bay, the war factory shrinks back: fit_w
416 → 74x55 hangar, 28.2x27.1 door — **the APC sets the floor** (below ~416
it stops fitting); the Titan clears every option; TD-exact width 395 would
break the APC. (Unit canvases are 8 px per classic, buildings 16/3 — never
mix them.) See open queue 27 for everything that must move with it.

## Refinery dock — ✅ SIGNED OFF "absolute perfection" (Luke, 2026-08-06 evening)

**FINAL GEOMETRY (build `e15bbf3a` = commit `6e2a55e2`):** line-up = SE
plate cell centre; aimed dead-straight reverse (motion == facing+128 at
every waypoint) at facing 92 (TSHARV) / 94 (TDHARV); parks TSHARV
pad+(40,74), TDHARV pad+(3,23); settling pivot to true SE on arrival;
motionless unload (stale-MOVE_HERE guard in RADIO_DOCKING + NavCom clear
at IsDumping); organic pathing exit (no scripted roll). TSHARV Speed=6
(RA/TD parity) + **Tracked=yes** (the wheels-vs-tracks terrain trap, third
occurrence — grep any new vehicle's rules section for Tracked= before its
first drive). The centering was dialled LIVE with Luke over three builds —
the measured composite coordinates were NOT the pose his eye wanted; **the
final constants are the ground truth, do not re-derive from the reference
PNGs.** Also verified in this arc: plate/east-column placement veto
(occupied-neighbour lookup), selection box, Adjacent=1 placement reach,
MCV 4x3 ghost.

**Dock protocol plumbing (from the 08-03 fix round, durable):** the refinery
radio protocol gates on literal `STRUCT_REFINERY || STRUCT_TDPROC` in ~15
sites — ALL take TSPROC now. TSPROC pad = the passable apron-row cell
`Coord + 3*MAP_CELL_W + 2` (RA's DIR_S-of-centre lands inside the occupied
plot). `Is_Refinery_Dock_Cell` (Layer B pad reservation) has the TSPROC
clause. Same literal-chain audit was needed for repair
(`STRUCT_REPAIR||STRUCT_TDFIX`, ~17 sites) and radar
(`STRUCT_RADAR||TDHQ||TDEYE`, 7 chains) — see the traps list.

## Dead ends — DO NOT RE-CHASE (each cost a live-fix round)

- **The TS attach-dock** (limbo + HORV-baked truck in refinery frames): Luke
  ditched it — a baked duplicate = a permanent sync surface. Machinery fully
  deleted in `c1efcf91`.
- **BACKUP_INTO_REFINERY at any facing but SW: SNAPS (teleport).** A real SE
  reverse needs its own mirrored track table entry (that is what shipped).
- **Detour approach cells:** the RADIO_DOCKING maintenance loop re-orders the
  truck to the MOVE_HERE cell every tick → stuck oscillation.
- **ANY post-turn coordinate seat** (single-tick nudge OR 1px/tick creep):
  reads as slide/teleport; the creep RAN AWAY (Coord_Snap is NOT the
  cell-centre reference). Trucks park at cell centre, full stop.
- **Apron rectangle-clip to the plot:** slices the stripes (hard edge).
- **Three-layer dock / sort-based hiding at TSPROC** (`db8913b1` → revert
  `b1f9b649`): even a +230-threshold "half hide" reads as full-hide — the
  bay-mouth dark art is building pixels and covers the whole truck.
  `0f8192d7` removed ALL TSPROC sort bias. Plan A stands: the truck backs up
  to the entrance and stays FULLY VISIBLE
  (`~/Desktop/docking-art/refinery-ts/{ts,td}-harv-docked.png`).
- **CenterCoordY bias for the TSFACT selection box:** PROVEN launcher-ignored
  (12→25cl moved the box 0px across a restart). Fix path is the packer
  geometry diff, not launcher probing.
- **Art-sized selection dims:** FAILED and REVERTED (`c49f5242`/`eadc900e`)
  — the box centres on the plot, brackets float. Foundation box = the
  accepted default; don't re-chase without a new mechanism.

## Engine facts, traps, lessons (durable)

**Bullet/delivery engine facts (proven live 2026-08-12):**
- **A fuse arms with at most 0xFF frames of flight** (`fuse.cpp Arm_Fuse`,
  `Timer = min(timeto, 0xFF)`). A projectile slower than its distance budget
  "arrives" mid-flight — the nuke survives 64 cells only because it falls at
  MPH_VERY_FAST.
- **A unit set down on building-occupied cells is UNRESCUABLE** — renders
  under the building, cannot path off, manual orders do nothing. Set cargo
  down outside the occupy list (the war-factory exit-row arrangement).
- **`Begin_Production` never consults `Can_Build`** — a visible cameo is
  orderable, whatever legality says. Any cap/cooldown that keeps its cameo
  visible must refuse inside `Begin_Production` itself.
- **`CNCSidebarEntryStruct::Busy` draws NOTHING in the client.** To show
  unavailability, synthesise `Constructing` + `Progress`, or swap the cameo
  art via AssetName.

**Role chains and heaps:**
- **Every literal `STRUCT_X||Y` role chain must include new TS types** —
  refinery ~15 sites, repair ~17, radar 7. A missed chain presents as a
  behavioural bug (static radar, refused docks), not a crash.
- **Heap registration must be strictly enum-ordered** (slot index == Type;
  `As_Reference` indexes the heap directly). Append at the marked Init_Heap
  tail. Violating this once gave AI MCVs that deployed helipads (`82aec6d`).
- Give-way recursion is depth-capped at 8 in `DriveClass::Assign_Destination`
  (0xC00000FD stack overflow, minidump-proven; the immediate Start_Of_Move is
  optimisation-only). Crash artifacts land in the prefix's
  `AppData/Roaming/CnCRemastered/` — check there FIRST on any crash.

**TS art conventions:**
- **Every TS anim SHP packs healthy frames then DAMAGED frames** inside its
  usable window; `loop()` splits even windows. FULL-CYCLE breakers exist
  (GTCNST_B rotating light, NTREFN_B plume) — verify per anim.
- **Damaged base frame = 2** (0 healthy, 1 LIGHT damage, 2 HEAVY, 3-5
  rubble). Frame 1 is never a free "variant" (falsified above).
- **Buildup SHPs carry EMPTY + fragment frames past the real run** — the
  launcher renders blank content as the PURPLE placeholder; the packer's
  post-peak area cut handles it. Donor `Init_Anim` counts apply ONLY when
  the building has no own MAKE stub (donor counts overwrote real ones once).
- **Render contract (2026-08-03):** the launcher maps the HD canvas onto the
  classic-stub-dims box **CENTERED (both axes) on the BSIZE box centre**;
  stub height beyond the box splits into EQUAL art halos above and below.
  That is how apron/overhang rows work with zero DLL draw changes.
- **Selection boxes: launcher sizes them from DimensionX/Y = FOUNDATION
  cells −20%** (bdata `Dimensions()`); the art is never consulted.
- Voxel renders start E (CCW); RA frame space 0=N — ZIPs rotate +8, the
  packer bakes it for regens.
- Verify packed art via meta crop[1], NOT the TGA bbox (packed TGAs are
  content-cropped); leave real canvas headroom (razor-thin margins die to
  ~2px hq_scale silhouette bleed).
- **Canvas and classic stub must move together** — guarded: `ts_pack_tree.py`
  writes `scripts/ts_stub_dims.json` and `ts_stub` in `build_tfassets.sh`
  refuses a stub that disagrees. ⚠ A partial pack run (temp TS_ART_DIR with
  a subset of shp dirs) TRUNCATES `ts_stub_dims.json` to the packed subset —
  restore it after.
- **An overlay's shape pointer supplies its render box** — every overlay
  needs its own stub in TFASSETS.MIX.
- ⚠ Generated-XML trap: anything inserted after "the last ObjectTypeClass"
  in RABUILDABLES lands INSIDE the countdown generator's managed block and
  its next run EATS it — insert before the BEGIN marker.

**Pipeline / environment:**
- `scripts/ts_rebuild_art.sh` regenerates `$TS_ART_DIR` from the Steam TS
  install (verified content-identical). TS building cameos live in
  **SIDEC01.MIX** (GDI), not CONQUER.MIX. Extraction chain: TIBSUN.MIX →
  `tools/ts_extract.py` → `ts_shp.py`; packer skips absent art dirs and the
  XML/CSV emits are idempotent, so partial repacks are safe.
- ⚠ `ts_pack_art.py`/`ts_pack_walkers.py`/`ts_stealth_hq.py` still hardcode
  the MAIN repo path — do not run from the worktree as-is.
  `ts_pack_units_wave.py` is worktree-relative.
- `Find_Exit_Cell` dereferences its argument — guard before calling it from
  a state that runs after radio contact drops.
- **`MT_COMMANDBAR_COMMON.TGA` (~176MB crest atlas) is NOT in git** — it
  rides in `build/remaster/Vanilla_RA/` only; a fresh worktree build dir
  lacks it and `rsync --delete` strips it from the deploy target (symptom:
  vanilla Allied eagle in the radar). Recovery: the Workshop cache
  `~/.steam/.../workshop/content/1213210/3729834253/`.
- Diagnostics land in `MOD_DEBUG_TSUNITS.txt` / `MOD_DEBUG_CANBUILD.txt`
  (⚠ sometimes in `pfx/drive_c/users/steamuser/` instead of
  `Documents/CnCRemastered/` — CWD drift; check both).

**Method lessons:**
- **Measure WHICH art owns the pixels before changing any render flag** —
  the occluder was the bay door (71% of it outside the building silhouette),
  not the apron; four rounds lost. A per-cell coverage table off the packed
  art takes one command. See
  [[feedback-identify-occluder-before-flag-changes]].
- **Occlusion-biased measurement:** a docked composite measured by VISIBLE
  stripe centroid doubles the apparent depth (the truck covers the stripes).
  Measure against unoccluded landmarks.
- **Positive controls:** `tf_sort.log` is under `#if 1`, NOT `TF_DEV_BUILD`,
  so its freshness never proves which build is live. Ship a positive control
  with any negative result, or the negative is worthless.
- **THE PLACEMENT RULE (Luke):** art matches the build grid; grow the GRID
  to fit big art; full-width RA slab spans the building. No baked pads.

**Standing cautions (from the original plan):**
- **AI blindness:** until the faction-agnostic builder (W2.9, AI lane) can
  see non-home lineages, an AI that finds the TS MCV deploys a yard it never
  uses. Accepted; TS is the fifth lineage that breaks any 4-way literal —
  coordinate with the AI instance before merging tree-visibility work.
- **Merge hotspots with the AI instance:** `defines.h` enums, `udata.cpp`,
  `bdata.cpp`, `cell.cpp`, `rules.ini`. Small commits, rebase onto `main`
  often.
- Old saves break on any enum growth (accepted, standard).
- TS art is EA copyright, same tolerated category as the TD-Remastered art
  already shipped; ship call is Luke's (`ts-asset-import-spike.md` legal
  note).

## Open queue (consolidated; re-verified at session close 2026-08-14 ~00:20)

**Gameplay / engine:**
1. **Mk. II cap → 3** on Luke's word (`TF_MK2_CAP`, one constant).
2. **⭐ 3x2 pass: CLOSED.** Boxes verified ("FIXED!", 08-14); MCV
   round-trip PASS + bay delivery end-to-end PASS (fresh skirmish,
   2026-08-16). **Refinery box: round-1 2-tile fit ACCEPTED (Luke,
   2026-08-16) — the 4x5 height-trick attempt was built, played and
   REVERTED same evening. Don't re-chase.** What the attempt proved
   before rejection: BSIZE_45 ghost rows + CenterOffset pinned to the
   dock pad (0x03800200) keeps Center_Coord world-invariant (sprite,
   dock geometry, spawns all untouched — no art recut needed) and the
   plot-centred box does reach the stacks; the apron renderer's owner
   lookup must probe a solid row, not the ghost origin; a 4x5 placement
   demand reads as a monstrosity (grid must stay the real footprint,
   Tesla/Obelisk convention). Rejected on look: the tall box + the two
   extra plot rows didn't read better than the round-1 fit. Left
   unresolved: whether the launcher centres boxes on the BSIZE plot or
   the placement-list rect (both were 4x5 in the played build).
3. **TS WF placement-grid regression:** reads 4x3, should be 5x3 with the
   4th (top) row build-blocked — the radar height trick. Suspect the 08-07
   per-type `Occupy_List(placement=true)` split: the `_ts_weap_place`
   literal is the 4x3 the launcher now draws.
4. **TD-units-from-TS-factories tech leak** (and audit the reverse): TSPILE/
   TSWEAP accepted as production sources for TD-era units. Decide the rule
   with Luke first (strict era separation vs deliberate cross-era), then
   audit both directions + what the sidebar offers with mixed-era factories.
5. **WF pad lies outside the 4x3 plot** (geometrically must — the hangar
   uses every column). Options: leave outside (current; `Is_TS_Apron_Cell`
   keeps it unbuildable), clip at the plot edge (hard cut), return to 5x4.
   **Undecided — Luke's call.**
6. **Helipad footprint** — Luke floated 2x3+bib, my counter 2x2+bib (RA/TD
   parity + height trick if the art spills). His call; any footprint change
   needs a watched land-rearm cycle after.
7. **Packer apron WARNING text is stale** — aprons no longer stamp (they
   draw from building geometry since 2026-08-13), so "will still stamp,
   overwriting neighbours' bibs" is false; blank tiles are now merely
   wasted entries. Reword, and the blank-tile counts (TSPROC 6/15,
   TSWEAP 2/15) become a pure art-tightening nicety.

**Eyeballs owed (verification, not code):**
8. War-factory sandwich in play (door open/shut hiding a vehicle) + SE bay
   exits (exit list re-cut but never judged; expect an awkward pose, wants
   Luke's eye live like the dock).
9. RA-truck-at-TSPROC regression eyeball; one clean watched TDHARV dock
   cycle at TSPROC; TSHARV auto-return when full (Tiberium_Load fix).
10. Takeoff-crash soak: a week of play without an `_Except_` file (another
    clean night 2026-08-13/14, many Mech Division orders).

**Art polish (parked):**
11. WF door-to-pad seam: the real cure is stopping `hq_scale` bleeding black
    at all — a global change touching every TS building, **wants Luke's OK**.
12. Ramp stripes band yellow/green (the gold-bake test misses the darker
    green bands).
13. Titan parks ahead of the door — `TSTITN` frame registration sits +11.8
    classic px below its box centre (every other unit within ±2.4). Fix the
    registration or dial `ExitCoordinate` by eye — Luke's call.
14. Refinery smoke continuity (blocky specks between puffs): drop near-empty
    frames, soften the alpha floor, or check whether NTREFN_C (144-canvas,
    needs offset compositing) is TS's own gap-filling second layer.
15. Queued art nits: SMOKEY harvest puff port; voxel brightness pass
    (TSHARV/TSMCV vs the TS screencast; + the dropship — "too dark",
    Luke 2026-08-16); chunky intake pixels + black fringe
    at the refinery bay mouth; damaged bay deck's stray remap-green pixel.

**Housekeeping:**
16. Remove the `tf_orbit.flag` dead code (descent landed).
17. Re-run the free dormant-host census before committing the roster's sound
    count (hosts used: BONUS_UNLOCK, DINOATK1, DINODIE1, DINOMOUT, DINOYES,
    STRUGGLE; a host needs no RAC_/RAR_ **and no SFX_GUI_*** reference).
18. Possibly stale — confirm with Luke before working: conyard 0.94-size +
    rotating-light verdicts (2026-08-04); TSHARV front-cabin sprite anchor /
    oversized ShapeSize (likely absorbed by the dock arc).

**Restored / added 2026-08-13 evening (Luke's picks — the prune had dropped
26 by mistake; he caught it):**
26. **TS harvester poses at the TD and RA refineries** — the last unmade
    placements (Luke's original 08-04 scope: "dock ALL 3 harvesters at the
    TS refinery, and the TS harvester at the TD and RA refineries").
    Current code: TS-at-TD = generic visible W-facing park (explicitly
    skips the TD attach maneuver, `unit.cpp` ~1193); TS-at-RA = shares the
    TDHARV visible-park branch, never dialled. Pose work is collaborative —
    worked out with Luke's eye (Aseprite reference art prepared in
    `~/Desktop/docking-art/`: all 3 harvesters full-canvas-aligned facings
    + all 3 refineries incl. TDPROC's attach anims; see its INDEX.txt).
27. **War factory descale to normal size (Luke, 2026-08-13).** The Mk. II
    now arrives by bay, so the 08-07 enlargement can come back down — see
    the hangar-resize table: **fit_w 416 is the floor (below ~416 the
    TSAPC stops fitting through the door); TD-exact width 395 would break
    the APC.** ⚠ Moves together with: the exit point (the y=42 two-pixel
    window re-derives from the new hangar span), the sandwich layer cut,
    the sort band (must still reach the new south edge), the placement
    grid (item 3 — fix in the same pass), and canvas+stub together.

**Roster remainder (the plan below):**
19. Component towers TSVULC/TSCSAM/TSROCK — turreted TDGTWR pattern, NOT the
    static recipe (GTCTWR_B/_C/_D are 48-canvas TURRET rotation frames).
20. Infantry TSE1/TSE2/TSGHOST (td-infantry-port-recipe adapted).
21. Orcas TSORCA/TSORCAB (RA helipad rearm mechanics).
22. TS audio wave (dormant-sample recipe; see 17).
23. NTREFN_C refinery anim offset compositing (see 14).
24. TS GDI/Nod badge emblems — Luke supplies; TS cameos stay pristine until
    then (they are exempt from faction badging).
25. Phase-2 decisions with Luke (deferred list below).

## The plan (2026-08-01) — goal, gate, roster

**Goal (Luke): the full GDI Tiberian Sun tech tree in the mod**, as the
ownership-gated easter-egg tree designed in `ts-factions-feasibility.md`
§"The cheap alternative": a rare crate drops a **TS MCV**; deploying it
produces the **TS construction yard (`TSFACT`)**, and the yard is the sole
gate on the roster — any side, no new house, no picker slot, no CONFIG.MEG
change.

### Delivery mechanics (the gate)

- **TS MCV rides the RANDOM unit-crate path only, never the `force_mcv`
  comeback path** (a wiped player must get their own faction's MCV).
- Existing 1-in-8 TS crate roll stays; the MCV joins as a rarer sub-roll
  (1-in-4 within the TS roll ≈ 1-in-32 of unit crates — rarity approved by
  Luke 2026-08-01). Dev builds override to 100% (gated on `TF_DEV_BUILD` +
  `TF_Dev_Cheats()`); release builds revert automatically. AI use of the
  tree comes later with W2.9.
- All TS types ship broad `Owner=` (all sides) + `Prerequisite=TSFACT`
  chain; every new prereq token gets its `Can_Build` remap `continue` (the
  known silent-unbuildable trap).
- TS MCV is also buildable in-tree (TSWEAP + TSTECH, TL 10) so a found tree
  is self-sustaining; heritable capture works via the W2 lineage machinery
  (`MCV_Deploy_Building` has the `UNIT_TSMCV → STRUCT_TSFACT` case).
- The three marquee units (Hover MLRS / Titan / Mk. II) keep their crate
  delivery AND are buildable behind the tree. (The Mk. II's build path is
  the Dropship Bay — see the canonical record above.)
- Balance stance: **TS-authentic stats, a generation ahead by design** —
  as a rare find, strong is the point; revisit after play.

### Roster — v1 (standard mechanics, proven pipelines)

Stats are the TS RULES.INI values (verified from the extracted INI). `TS`
IniName prefix throughout (dodges the TD HP-doubling hook). ✓ = shipped.

#### Buildings (NewTheater SHP + buildup, the TSPOWR/stealth-gen recipe)

| Ours | TS | TL | Cost | Str | Prereq (translated) | Notes |
|---|---|---|---|---|---|---|
| TSFACT ✓ | GACNST | — | — | 1000 | (MCV deploy) | |
| TSPOWR ✓ | GAPOWR | 1 | 300 | 750 | TSFACT | |
| TSPROC ✓ | PROC | 1 | 2000 | 900 | TSFACT, TSPOWR | RA refinery mechanics + free TSHARV; 4x3 |
| TSSILO ✓ | GASILO | 1 | 150 | 300 | TSPROC | |
| TSPILE ✓ | GAPILE | 1 | 300 | 800 | TSFACT, TSPOWR | barracks |
| TSWEAP ✓ | GAWEAP | 2 | 2000 | 1000 | TSPROC, TSPILE | war factory, 4x3 + sandwich |
| TSRADR ✓ | GARADR | 3 | 1000 | 1000 | TSPROC | radar, 2x2, dish ping-pong |
| TSHPAD ✓ | GAHPAD | 5 | 500 | 600 | TSRADR | helipad |
| TSTECH ✓ | GATECH | 6 | 1500 | 500 | TSWEAP, TSRADR | tech centre |
| TSDEPT ✓ | GADEPT | 7 | 1200 | 1100 | TSWEAP | service depot (RA FIX mechanics) |
| TSDROP ✓ | GADROP (cut) | 9 | — | — | TSTECH chain | Dropship Bay — Westwood's cut building finished; see canonical record |
| TSVULC | GAVULC (GACTWR_B art) | 2 | 350 | 500 | TSPILE | component tower + vulcan as ONE standalone turret; cost = tower 200 + vulcan 150 |
| TSCSAM | GACSAM (GACTWR_C art?) | 5 | 500 | 500 | TSPILE, TSRADR | AA tower, same translation |
| TSROCK | GAROCK (GACTWR_A art?) | 9 | 800 | 500 | TSPILE, TSTECH | RPG tower, same translation |

#### Vehicles (voxel renders @ 12 px/voxel unless noted)

| Ours | TS | TL | Cost | Str | Prereq | Primary | Notes |
|---|---|---|---|---|---|---|---|
| TSMCV ✓ | MCV | 10 | 2500 | 1000 | TSWEAP, TSTECH | — | deploys TSFACT; crate find |
| TSHARV ✓ | HARV | 1 | 1400 | 1000 | TSWEAP, TSPROC | — | RA harvester mechanics, Tracked=yes |
| TSSMEC ✓ | SMECH | 2 | 500 | 175 | TSWEAP | AssaultCannon | SHP walker, Titan pipeline |
| TSTITN ✓ | MMCH | 3 | 800 | 400 | TSWEAP | 120mm | |
| TSAPC ✓ | APC | 6 | 800 | 200 | TSWEAP, TSPILE | — | hover locomotor stands in for TS amphibious (deviation) |
| TSHVR ✓ | HVR | 7 | 900 | 230 | TSWEAP, TSRADR | HoverMissile | |
| TSSONIC ✓ | SONIC | 9 | 1300 | 500 | TSWEAP, TSTECH | SonicZap | one 140 AmbientDamage per object per sweep (deviation) |
| TSHMEC ✓ | HMEC | 10 | 3000 | 800 | TSDROP, TSTECH | MammothTusk/railgun | bay-delivered, capped |
| TSMDIV ✓ | — | — | 2800 | — | TSDROP | — | Mech Division token → 3 Titans + 2 Wolverines |

#### Infantry (TS-SHP, td-infantry-port-recipe adapted)

| Ours | TS | TL | Cost | Str | Prereq | Primary |
|---|---|---|---|---|---|---|
| TSE1 | E1 | 1 | 120 | 125 | TSPILE | Minigun |
| TSE2 | E2 | 2 | 200 | 150 | TSPILE | Grenade (disc) |
| TSGHOST | GHOST | 10 | 1750 | 200 | TSPILE, TSTECH | LtRail (proven railgun beam) |

#### Aircraft (voxel, RA helipad rearm mechanics)

| Ours | TS | TL | Cost | Str | Prereq | Primary |
|---|---|---|---|---|---|---|
| TSORCA | ORCA | 5 | 1000 | 200 | TSHPAD | Hellfire |
| TSORCAB | ORCAB | 8 | 1600 | 260 | TSHPAD, TSTECH | Bomb |

### Deferred (engine-heavy or new logic — phase 2, decide per item)

- **JUMPJET** — RA has no flying-infantry locomotor.
- **MEDIC** — heal logic exists in RA (MEDI); cheap if wanted, but it's an
  RA mechanics clone, decide whether it earns a slot.
- **TRNSPORT (Carryall)** — vehicle-lifting aircraft is new logic (RA
  Chinook lifts infantry only).
- **LPST (Mobile Sensor Array)** — sensor/cloak-detect logic; revisit with
  the Stealth Generator `IsScanner` detectors.
- **GAPLUG/2/3** (Upgrade Center + plugs) — upgrade-slot mechanic doesn't
  exist; Ion Cannon Uplink could later host the existing Ion Cannon special
  on the Temple-nuke pattern.
- **GAFIRE/GAFSDF** (Firestorm) — wholly new defensive logic.
- **NAPULS (EMP Cannon)** — EMP disable logic is new. *(An EMP arc is now
  planned in the subterranean instance's lane — coordinate before starting.)*
- **GAWALL/GAGATE/GAPAVE/GALITE** — walls are OverlayTypes (different
  pipeline); gates are new logic; pavement/light post cosmetic.
- **GAPOWRUP (Power Turbine)** — upgrade mechanic.

### Audio

Every entity ships authentic TS sounds via the dormant-sample recipe
(`td-audio-routing-recipe.md` + the MS-ADPCM rule — plain-PCM overrides
crash the client, see the bay crash record). Weapon reports are TD
placeholders (MGUN11 / OBELRAY1) pending the TS audio wave. The free-host
census needs re-running before the roster's sound count is committed (open
queue 17).

### ⭐ The Stealth Recipe — canonical per-building port (Luke's challenge, 2026-08-01)

**Luke's spec:** TS-authentic art, built animations AND damaged states, TS
sidebar icons, sized to match TD counterparts. Baseline = the Nod Stealth
Generator. Per building:

1. **Extract** (temperate 'T' names): base `GT<X>.SHP`, active anims
   `GT<X>_A/_B/_C.SHP` (art.ini `ActiveAnim*=`; damaged variants are usually
   the second half of the same SHP), buildup `GT<X>MK.SHP` (ISOTEMP.MIX),
   cameo per art.ini `Cameo=` (SIDEC01.MIX, decode with CAMEO.PAL).
   Bases/anims decode with UNITTEM.PAL.
2. **Compose** the stealth-gen layout: N healthy frames = healthy base +
   anim frame i (shorter anims loop), then N damaged frames = damaged base +
   anim damaged-half. Ship real buildup frames only, resampled to the
   donor's construction-anim count (fragment/empty tails render PURPLE).
3. **One affine for every frame** of a building (base, anims, MK) —
   content-anchored: scale so the healthy composite matches the TD
   counterpart's content proportions, centred on the canvas. Canvas =
   classic donor dims × 5.33. NEVER full-canvas scale.
4. **Donor = the TD counterpart** (matching footprint AND construction-anim
   count): TSPOWR→TDNUKE, TSPILE→TDPYLE, TSPROC→TDPROC, TSWEAP→TDWEAP,
   TSRADR→TDHQ, TSHPAD→TDHPAD, TSTECH→TDEYE, TSDEPT→TDFIX, TSSILO→TDSILO,
   TSFACT→RA FACT (TD yards are 3x2), towers→TDGTWR/TDSAM/TDATWR-class 1x1s.
5. **Engine:** enum append INSIDE the TS block tail (move
   `STRUCT_TS_TREE_LAST`), heap `new` at the marked Init_Heap tail,
   `_td_bdonors` entry, `TF_Building_Scan_Bit` shadow, role tests, and an
   `_anims[]` entry `{STRUCT_TSX, BSTATE_IDLE, 0, N, 3}` (stealth-gen line
   at bdata.cpp:4621 is the template; damaged run = shapes N..2N-1).
6. **Data:** rules.ini section (TS stats, tree prereqs), RABUILDABLES entry
   (before the BEGIN marker — managed-block trap), ModText rows, BuildIcon
   TGA from the TS cameo (NEAREST 8x → LANCZOS 341×256) — unless a hand-made
   cameo exists in `resources/custom-cameos/`, which wins.

#### Asset inventory — remaining unported art (extracted 2026-08-01; regenerate via ts_rebuild_art.sh)

| Building | Base (canvas) | Anims | MK | Cameo |
|---|---|---|---|---|
| TSVULC/TSROCK/TSCSAM | GTCTWR_B 64 / _C 96 / _D 64 (48-canvas, TURRET rotation frames — TDGTWR turret pattern, not the static recipe) | — | GTCTWRMK 22 | TWR1/TWR2/TWR3ICON |

(All other buildings ported; NTREFN_C — 144-canvas anim on a 192x168
building, needs offset compositing — is still unported, open queue 23.
Silo's _B 64 frames likely map to the STORAGE fill-level contract — verify
before ever touching it.)

### Sequencing

1. ✓ **Skeleton** — TSFACT + TSMCV + crate roll + rewire the four shipped
   TS types into the tree.
2. ✓ **Economy** — TSPROC + TSHARV + TSSILO + TSPILE + TSWEAP.
3. ✓ **Combat spine** — TSSMEC, TSRADR, TSHPAD, TSTECH, TSDEPT (+ the
   Dropship Bay, added 08-08/13).
4. **Roster fill** — defenses (TSVULC/TSCSAM/TSROCK), infantry, Orcas,
   TS audio wave. ✓ TSSONIC, TSAPC.
5. Phase-2 decisions with Luke.
