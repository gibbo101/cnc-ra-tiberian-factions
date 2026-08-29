# TS GDI tree — implementation plan (2026-08-01)

## ⭐⭐⭐ RESUME HERE — **WF rebuild: BOTH DOOR SEATS SIGNED OFF 2026-08-29 evening (branch `wf-rebuild` HEAD `7df943d1`, desktop DLL `a0b4c9e4`).** `TSWEAP_SEAT_MOUTH_MECH` (597,123) for the walkers (Titan "PERFECTION", Wolverine PASS; Mk. II assumed) and `TSWEAP_SEAT_MOUTH` (573,219) for tracked/wheeled hulls ("we have our winner", called on the APC/harvester run). Both dialled live by Luke's EWNS marks, one build per nudge — do NOT re-derive. Vehicle-seat sweep (Disruptor, Hover MLRS, harvester, MCV) DONE 2026-08-30; merged to main `bd4734b5` and the merged desktop build played. WF arc CLOSED. NEXT: roster remainder (component towers first) or open-queue calls, Luke's pick. **Facts established 2026-08-29:**
- ⚠ **`Coord` of the building = the ORIGIN CELL'S CENTRE, not the plot's NW corner.** Seat (lx,ly) → canvas (192 + lx/2, 208 + ly/2) on the 896x672 canvas (plot = 128 px/cell from canvas (128,144)). Left jamb = `resources/custom-art/tsweap-front-cut-line.json`.
- **The "grey square bottom-right of the door"** = the door-leaf tab clip (`EXTRA_LAYER_CLIPS`) running on EVERY shutter frame, including the shut door where the tab is real leaf; the hole showed the flat interior and let hulls through. Fixed: `is_detached()` — the clip only fires on frames where the box holds pixels disconnected from the leaf (stages 5-7). Closing the hole also cured most of the "units drawn over the shutter" popping.
- **One shared seat for everything was tried and REJECTED:** a walker's sprite centre sits well above its feet, a hull's centre is the hull, so the mech seat put vehicles too deep. Hence the split.
- **Max zoom ≈ 1.3x** (NCC scale search of a capture against the 1x composite): 1 tile = 128 canvas px ≈ 166 screen px in Luke's max-zoom captures; his "12 px" ≈ 9 canvas px (applied as 12 canvas px = 24 leptons per notch).
- **OpenTS ground truth (read 08-29):** TS draws the exiting unit from the BUILDING's second pass (`Draw_Extras`: unit, then door leaf over it, `building.cpp:923-970`); `Exit_Coord` = origin corner + (98,188) leptons; the door opens BEFORE the unit is told to move (`Do_MISSION_UNLOAD` INITIAL→CLEAR_BIB→OPEN→LEAVE→CLOSE); the raw track tables are STRIPPED from the OpenTS drop. What `f11f836b` binned was only "hide until the door is fully open", not this mechanism — but our DLL hands sprites + SortOrder to the launcher and cannot paint, so a building-pass unit draw is an unproven launcher contract. Stayed on the sort-band mechanism; it works with the hole closed.
- A full `ts_pack_tree.py` run rewrites every ZIP's timestamps; compare zip member CRCs against HEAD and `git checkout` the content-identical ones. `cmake -E copy_directory` the resources into build/ BEFORE rsync; md5 the changed ZIP too. Deploys are pgrep-gated (`InstanceServerG[.]exe|ClientG[.]exe`), and the game must be fully exited, not just at the menu.
Previously signed off this arc: 5x3 L-footprint + 14-cell ghost, refinery-parity size, Lanczos-hard art, sandwich (front = hangar minus the aperture, cut LEFT along the yellow line, TOP along the rolled shutter's slanted edge, RIGHT open), open-doorway front while unloading, shutter layer +200, TS 5-state unload, `Rail_To` SE exit to XYCELL(4,2). Branch is OFF ts-units 66717e43 — rebase onto main (1d3d7f24) before merging.

**DECK (2026-08-28 session, Luke on the Deck today): DLL `806e0cdb` = `f876b002` code (the
dock-fix commit `58994541` is deliberately NOT deployed -- Luke: harvester work waits for the PC)
+ HEAD data. DESKTOP prefix (2026-08-28 PC session): DLL `491f658a` = HEAD incl. the dock fix
`58994541` -- deployed, verification in progress.**

### Brightness pass — SIGNED OFF 2026-08-28 (Luke: "that is night and day!"; turrets relit + walkers levelled + APC water shadow dropped, all "looks good"/"much better"). Queued: voxel-mesh upscale spike (harvester first), Titan barrel relight. — canonical write-up: `launcher-render-contracts.md` contract 11 + the render ledger. Below = the session's working notes.
Root cause measured, not eyeballed: `vxl_render.py` shaded `0.35 + 0.65·max(n·L,0)` (0.35→1.0
of the palette). TS (OpenTS `voxlib.cpp Precalculate_Normal_Lookup` + the shipped VOXELS.VPL,
extracted from TIBSUN.MIX) lights with a length-1.5 vector, truncates n·L·16 to a table index
(negative → 0) and each table is a fixed palette scale: 0.62 (facing away) → 1.26 (neutral, idx
16) → 1.70 (fully lit, idx 24). A 1.6–1.8x gap across the whole curve = "too dark". Ported as
`--shade ts` (now the DEFAULT; `--shade legacy --ambient N` reproduces the old renders
byte-for-byte). In TS mode the 1.45x team-green lift is dropped (TS's ramp carries the lift) and
shaded RGB is clipped at 255 (unclipped, the uint8 cast wrapped and the dropship grew green
fringe pixels). Re-rendered per the ledger and repacked through each unit's own recipe, then
`ts_reshadow.py`: TSHARV (233x106 body bbox identical to shipped; mean RGB 39/59/37 → 66/88/62),
TSMCV (278x131 identical; 48/50/26 → 80/79/44; NEW `scripts/ts_pack_tsmcv.py` = the tree
script's block on its own), TSDSHP (92/75/38 mean). Sheet in the session scratchpad. Luke: "looks a lot
better, do the other six" → the remaining VOXEL units re-lit the same way and DEPLOYED (Deck),
geometry ±1 px: TSHVR (body + rack `--z-clip 10`), TSSONIC (hull + turret `--hva SONICTUR.HVA`
— the turret pose lives in the HVA; without it the render is 38 px taller and sits 78 px lower),
TSAPC (body + `apcw` water hull via `ts_pack_tsapc_water.py`), TSHMEC (8 HVA gait frames at
35°). NEW `scripts/ts_pack_hvr_hmec.py` = the walkers script's TSHVR/TSHMEC blocks alone
(the full walkers script needs Titan SHP inputs not on disk). Titan and Wolverine are TS SHPs
(MMCH/SMECH), not renders — no change. Team-colour areas move less than hulls (~1.2x, the TS
ramp replaces the old 1.45x green lift). All sheets in the session scratchpad.
Verify on the Deck: build a TS harvester + MCV, drop-pod a unit; judge against the TD/RA HD
units beside them. Too bright → the lever is a single global multiplier on `TS_VPL_SCALE`.

### Item 1 — TS harvester docking at the RA and TD refineries — CLOSED 2026-08-28 (see RESUME block); items 2–3 CLOSED 2026-08-28; item 4 (WF re-look) NEXT
1. **TS harvester (`TSHARV`) docking at the RA and TD refineries.** Docks at TSPROC already
   (signed off 08-06). `Mission_Unload` `case UNIT_TSHARV` shares the TD/RA-harvester path
   (`unit.cpp` ~3870, "no dump frames on the voxel sprite"); verify the reverse-dock seat at
   RA `STRUCT_REFINERY` and `STRUCT_TDPROC` (dock cell, facing, park nudge, no white box,
   credits bank, drive-off). Pre-read: the DEAD-ENDS list in the docking section of this doc
   and `harvester-docking-session-handover.md`. Use OpenTS `harvest`/refinery docking code
   (`unit.cpp` Mission_Unload / Mission_Harvest) as ground truth for any TS-side question.
   **Code state read 2026-08-28 (nothing changed yet):**
   - Acceptance: every refinery accepts every harvester (`building.cpp` RADIO_HELLO case
     REFINERY/TSPROC/TDPROC, ~l.300). Dock cells (RADIO_DOCKING ~l.540): RA refinery =
     DIR_S of centre; TD refinery = DIR_SW of centre; TS refinery = centre +1 row +1 col
     (+1 row only for the RA harvester).
   - ⚠ **THE BUG TO FIX FIRST — TSHARV at the TD refinery takes the TD ATTACH path.**
     `RADIO_IM_IN` at `STRUCT_TDPROC` (~l.360) diverts only `UNIT_HARVESTER` to
     MISSION_UNLOAD; everything else (TDHARV *and* TSHARV) gets `RADIO_ATTACH` -> limbo'd
     and "baked" into the refinery's frames, which are the TD truck's art. So a TS harvester
     docking at a TD refinery vanishes and a TD truck appears in the bay. Fix: divert
     `UNIT_TSHARV` to MISSION_UNLOAD there too (park + timer offload, the pairing every
     non-native harvester already uses).
   - Seat: `Mission_Unload` case TSHARV shares TDHARV's branch (~l.3870): at any non-TSPROC
     refinery it applies `TD_DOCK_NUDGE_RIGHT/UP` = 6 px E / 6 px N (dialled for the TD
     sprite at the RA refinery) and issues NO facing turn (only TSPROC gets `Do_Turn(DIR_SE)`).
     The TS harvester needs its own per-pairing seat dials (RA refinery, TD refinery) and a
     dock facing per pairing -- an Aseprite/screenshot seat loop with Luke, one build per
     nudge. Fume plume anchors at `Coord + (0,-6)` for non-TSPROC (check it sits on the TS hull).
   - Draw: TSHARV is excluded from the RA dump/load frame paths (~l.2698/2718), so no white
     box is expected; verify anyway (32-frame voxel).
   - **TS's OWN dock procedure (read from OpenTS 2026-08-28, Luke: "reckon we can get the
     correct docking procedure?"):** `building.cpp Docking_Coord` = refinery `Center_Coord()`
     + half a cell EAST (the harvester parks on the refinery's own plot, on the ramp cell);
     RADIO_DOCKING sends the harvester there (`RADIO_MOVE_HERE`), then `RADIO_BACKUP_NOW`:
     harvester `Do_Turn(DIR_E)`, and once stopped + tethered + in MISSION_ENTER it sends
     `RADIO_IM_IN` directly (no reverse track at all); refinery `IsDockUnload` → harvester
     `MISSION_UNLOAD`. `Do_MISSION_UNLOAD` harvester branch: turn to DIR_E if not already;
     `IsDumping=true`, stage/rate reset, the building WEST of the harvester's cell gets
     `Begin_Anim(BANIM_PRE_PRODUCTION)` (the refinery's own unload anim = art.ini GAREFN
     active anims); status 3 offloads one bail per `HarvesterDumpRate` minutes of stage into
     `House->Harvested()`; status 4 waits for `Anim_Active(BANIM_PRODUCTION)` to end, then
     `MISSION_HARVEST` + `RADIO_OVER_OUT`. No Limbo, no attach: the harvester stays a live
     object facing E on the pad while the refinery animates. For OUR TSPROC that is exactly
     the signed-off "one live sprite" park; the remaining work is the two foreign refineries,
     where TS offers no procedure — dock cell + facing there are our call (seat loop).
2. **Unit brightness pass** (queued nit 15 below): TSHARV / TSMCV / dropship "too dark"
   (Luke 08-16) vs the TS screencast. Method: measure TS's own render brightness from a TS
   screenshot / OpenTS voxel lighting constants (`voxel*.cpp`), never eyeball; the lever is
   `vxl_render.py --ambient` (0.35 default) + the 1.45x team-green lift, re-render + re-pack
   per model via the existing pack scripts (keep the +8 face fix and each model's `--elev`:
   APC/harvester 32, others 54).
3. ~~**TS Power Plant + TS Radar placement glitch**~~ **FIXED 2026-08-28** (see `known-issues.md`:
   ghost = ground rows, plot re-anchored above it, legality = ghost only). Compare against OpenTS building placement / foundation + the TS art.ini
   entries for GAPOWR / GARADR (foundation, anim offsets) before touching any offset.
4. **Re-look at the TS war factory** with the source in hand: OpenTS's factory door / exit
   / sort logic (`building.cpp` GAWEAP handling, art.ini GAWEAP anims) against our sandwich
   + exit-rail + clamp construction (see the WF sections below and the DEAD-ENDS list).
Then the next phase.



### Mk.II RAILGUN re-port from OpenTS + TS rules — VERIFIED + SHIPPED `79db903e`
TS data (extracted live from `TIBSUN.MIX/LOCAL.MIX/rules.ini` with `tools/ts_extract.py`;
copy in the session scratchpad): `[MechRailgun]` AmbientDamage=200 ROF=60 Range=8 Report=RAILUSE5
Anim=GUNFIRE; `[LargeRailgunSys]` SpiralRadius=15 ParticlesPerCoord=.15 SpiralDeltaPerCoord=.03
PositionPerturbation=30 MovementPerturbation=.4 VelocityPerturbation=.6 Laser=yes
LaserColor=25,20,255; `[LargeRailgunPart]` MaxEC=70 ColorList=(25,70,205),(150,150,150)
ColorSpeed=.009 Velocity=.3. Code: `partsys.cpp Railgun_AI`, `techno.cpp Railgun_Beam_Damage`.
- **Coil** = TS's helix maths verbatim (`techno.cpp` IsRailgun branch): 19 sparks/cell (half TS's
  density — HD sprites, not pixels), radius 15 leptons, .03 rad/lepton, ±15 lepton jitter, the
  helix's height axis folded into screen-vertical. Sparks are `ANIM_RAILFX` again (the old
  white-box was the tile-count trap), art from NEW `scripts/ts_gen_railfx.py`: 12-frame ladder
  blue (25,70,205) -> grey (150,150,150) over ~1 s then grey to ~2.4 s (12 stages x 8 ticks).
  TS's outward drift (Velocity=.3/frame ≈ 2 px over a life) deliberately NOT reproduced.
- **Damage**: TS's half-cell radius — a unit is hit only within 128 leptons of the line; a
  building by any crossed cell; the aimed target always.
- Anim heap floor raised 200 -> 1024 (`rules.cpp`): a max-range shot lays ~150 sparks.
- Beam stays the 3-line 5-frame draw (launcher caps).
- **GUNFIRE muzzle flash ADDED (08-28):** `ANIM_TS_GUNFIRE` = TS `gunfire.shp` (CONQUER.MIX, 3
  frames, ANIM.PAL, x4 onto the 128 canvas, `TSGUNFIRE.ZIP`, translucent), wired purely as
  `Anim=TSGUNFIRE` on `[MechRailgun]` through RA's own Fire_At Anim= dispatch (spawned at
  Fire_Coord, attached to the firer). Stub in TFASSETS.MIX (rebuilt, 75 entries).
- **Coil life halved to 1.2 s (08-28, Luke: smoke still there when the Mk.II fires again):**
  RAILFX delay 8 -> 4. TS locks the gun until its coil dies (~2.4 s); we keep the 1.5 s ROF
  and dissipate faster instead.
- Verify: fire at max range on desert — a dense ragged blue coil hugging the beam, greying out
  within a second, lingering ~2.5 s; units beside the line unhurt unless within half a cell.

### First clip next session verifies the firing port (all four pieces in one shot)
1. **One band per firer**: a Disruptor holding fire on a target produces bands back to back with
   NO overlap (rearm = `SonicBandEnd`, the frame the band is gone).
2. **Moving target**: fire at a unit, drive it sideways mid-band — the band swings and follows
   it, hinged at the muzzle (every disc re-derives its place on the live line each tick).
3. **Cut-off**: press S / give a move order / retarget mid-band — the band freezes and retracts
   from the TANK end toward the target immediately, damage stops, next shot allowed after the
   retract (~0.4 s). Same on target death or when the target runs > 6 cells away.
4. Band thickness: 15 classic px (was 20; TS's polygon is 18.75). Thinner? `DIAMETER` in
   `ts_gen_sonicwave.py`, one number, art-only.

### The port (mirrors OpenTS `wave.cpp` `Wave_Shape_AI` — read it before changing anything)
- `AnimClass::SonicT` (0-256 place on the muzzle->target line; -1 = cut loose) and
  `SonicTether` (the TARGET fired at, cell or object) on every wave disc; `TechnoClass::SonicBandEnd`
  gates `Can_Fire` with FIRE_REARM for sonic weapons.
- Tether predicate per disc per tick (`AnimClass::AI`): firer alive && tether legal &&
  `firer->TarCom == SonicTether` && distance <= `SONIC_TETHER_RANGE` (2172 leptons = TS's
  6 diagonal cells). Tethered -> disc moves to `lerp(Fire_Coord(0), aim, T)` via Mark UP/DOWN.
  Broken -> the first disc to notice scans the band (same `SonicFirer`, `SonicT >= 0`), computes
  ONE delta = `(Stages - SONIC_FALL_STAGES - 1) - max stage`, bumps every disc by it, zeroes
  their `SonicDamage`, sets `SonicT = -1`, and pulls the firer's `SonicBandEnd` in to the fall.
  This replaces the 08-25 "hook Assign_Target/Assign_Destination" design: polling `TarCom` is
  what TS itself does and needs no override plumbing.
- Deliberately NOT ported (Luke-approved feel kept): TS's per-frame AmbientDamage to every
  occupier, wall/overlay/cliff effects, the 100-frame life (ours = 25 stages x 5 ticks, matches
  the footage). Ground-target (force-fire) shots keep a static band, cut only by TarCom change.

### Amphibious APC — OpenTS audit pass 2026-08-28 — VERIFIED + SHIPPED
Luke's three: (1) white box while loading = RA's APC door frames 32-40 requested at NE/NW, TSAPC
has no door art (`Shape_Number` now skips the door branch for TSAPC); (2) could not unload =
`UNIT_TSAPC` was missing from `Mission_Unload`'s APC state machine (added); (3) submerged on
water = TS's own mechanism: `apcw.vxl` (the water hull) drawn whenever the cell is water
(OpenTS unit.cpp AuxVoxel on LAND_WATER) -> rendered at the body's camera (`vxl_render.py
--frames 32 --px-per-voxel 12 --yaw0 0 --elev 32`, reproduces the shipped body render to the
pixel) and appended as frames 32-63 by NEW `scripts/ts_pack_tsapc_water.py` (body frames kept
byte-identical); `Shape_Number` adds 32 on LAND_WATER. Stub 64 frames, tileset 64.
**Speed made TS-exact:** TS's APC is NOT hover -- it is the drive locomotor with
`SpeedType=Amphibious` and its own land table. NEW `SPEED_AMPHIBIOUS` (rules key
`Amphibious=yes`; per-land `Amphibious=` column: Clear 80, Rough 40, Road 100, Water 80, Rock 0,
Wall 0, Ore 50, Beach 60, River 80 (TS has none; taken as water)), sharing MZONE_HOVER
(identical passability footprint). Old saves dead (enum + Zones untouched, but sizeof drift
elsewhere tonight). Verify: load infantry (no box), unload (works), drive into water (low hull),
and the speed drop on beach/rough.

### ⭐ OpenTS (github.com/OpenTS-Developers/OpenTS, released 2026-08-27) — cloned to `reference/OpenTS/`
Community source reconstruction of TS 2.03 Firestorm, GPL v3 — licence-compatible with us.
Manual: https://opents-developers.github.io/OpenTS/. `code/wave.cpp` `WaveClass` is the REAL
Disruptor wave: a screen-space per-pixel effect — polygon quad rasterized per scanline, each
pixel displaced 0-3 px along the travel direction and its G/B lifted by `(110+amp*8)/256`,
amp = `|sin(0.125*(WaveEC+radius))|*12` (wavelength ~50 px, crests glide source->target at
1 px/frame, several at once; `WaveEC` life counter doubles as ripple phase).
**QUEUED (Luke): audit the other TS ports against OpenTS source** — Hover MLRS, Wolverine
FiringFrames, Titan, walker gaits, subterranean, EMP were all built from footage; now the
real behaviour is readable. Also a candidate source for the band cut-off semantics
(WaveClass tether: wave stops growing + fades when the firer stops aiming at the target).

### Pulse/ripple: CLOSED 2026-08-27, four falsified mechanisms (don't re-chase ANY)
1. **Lit-window sprite pulse** (stage-gradient discs, spread 24/10/5 walked): spread 10 =
   one disc, "reads as a circle"; spread 5 = 25-35% block, "should be a small slither"
   (TS's own patch measures 2-4% of band length — sliver < disc diameter is geometrically
   impossible from disc primitives).
2. **Rotated thin bar** (square-packed, Rotation from SonicDir in the shipped path): drew
   UNROTATED in play — pill lying along an E shot, stepped pill chain on diagonals — despite
   contract §8 (rotation proven on the WAVE type via the fx-128 flag). Never diagnosed;
   "hell no".
3. **TS-exact amplitude ladder** (13-frame art ladder, stage driven per tick from the OpenTS
   formula): mechanism VERIFIED in play (crests at right spacing, travelling, measured) but
   pale-overlay-on-band cannot read like TS's multiplicative G/B lift: alpha 35 invisible on
   snow (+1.4%), alpha 80 = opaque white beading balls on desert ("regression"), 35 on
   desert still "out please".
4. **Chronal-vortex hijack** (dynamic_map VortexActive/X/Y override to ride the ripple
   crest — the launcher's only true pixel warp): the launcher DOES render it anywhere we
   point it, but IGNORES VortexWidth/Height (drew ~5x our 64 px), anchors at top-left not
   centre, carries the full chrono whirlpool styling, and churns for the whole life of the
   anims driving it. Unusable for a beam ripple. (Genuinely new lever though — recorded in
   launcher-render-contracts.md §10 for anything that ever WANTS a big screen warp.)

### Where the look stands (Luke's verdicts, 2026-08-26/27)

- **Band = the teal disc chain** with SHAPE_FADING + stage-keyed scale throb amp 12 %/period 6
  (`function.h` `TF_SONIC_*_DEFAULT`; play-picked from a 9-variant walk, clip 23-49-16).
- **TS fakes its shimmer too** (Luke re-watched `Screencast from 2026-08-24 00-38-41.webm`):
  hard strip, mottled tint, plus a paler disc pulse riding tank->target. "We've been chasing
  a shimmer." No launcher displacement exists on any object type (all levers walked, table
  below). Don't re-chase.
- **Strip approach TRIED AND REJECTED (2026-08-27):** rotated hard-edged segments
  (`Rotation` export, fx bit 128). Luke: "the version before was better with better colours",
  "ditch what you just gave me, it's the wrong direction". Findings kept because they are
  contracts: **the launcher DOES honour `Rotation` on anim exports, but clips the rotated
  texture to the UNROTATED frame rectangle** (64x112 crop at N/S drew a 64-wide bar and a
  sawtooth on diagonals; the near-square oblong survived). A rotated sprite must be packed
  square with the art inside the inscribed circle. Also: overlapping discs can never give a
  hard edge (chord coverage ramps the alpha) nor keep a mottle (6-7 deep stack smears it;
  sim max std 7 vs TS 19.5). Both recorded in `launcher-render-contracts.md` §8-9.
- **Pulse: REMOVED (see the CLOSED section above).** The band ships bare: discs + fading +
  12/6 throb. Old saves are dead (this session's `AnimClass` member churn).
- **NEXT**, in Luke's order: turret seat to the REAR of the hull (Aseprite seat loop; TS
  `TurretOffset=-64`, udata.cpp's turret-centre field is unused by the RA draw path, so it
  needs a TSTITN-style per-facing seat table or a baked offset in the turret frames), unit
  size (measure the base game's art, never our ports), band cut-off, any Aseprite pass.

### Launcher levers on the discs: every one walked with log receipts (2026-08-26)

| lever | verdict |
|---|---|
| `Cloak` on the anim export | ignored (08-25) |
| `Cloak` on a UNIT-typed disc with offset ID (fx 32+64) | ignored, band identical |
| `SHAPE_PREDATOR` | band INVISIBLE, no ground warp even zoomed over rocks |
| `SHAPE_GHOST` | no effect |
| `SHAPE_FADING` | translucent ✅ shipped |
| `Scale` throb keyed on stage | ripples ✅ shipped at 12/6 |
| `FlashingFlags` pulse | hard strobe, REJECTED (photosensitivity) |
| `Rotation` (fx 128) | HONOURED, but clipped to the unrotated frame (see above) |
| typed as UNIT without ID offset | the Disruptor body vanishes (ID clash) |

Dev flag `Documents/CnCRemastered/tf_sonic_cloak.flag`, re-read per shot: `<cloak> <fx-bits>
<amp%> <period>` (fx 1 predator, 2 ghost, 4 fading, 8 throb, 16 flash, 32 typed UNIT, 64 ID
offset, 128 rotate). Missing numbers fall back to the shipped defaults. All log sites are
`TF_DEV_BUILD`-gated.

---

## 2026-08-24 evening: Disruptor band = real weapon, "cracking job"

**CHECKPOINT at session end (Luke: "doc everything, commit as a checkpoint, end here").**
Prefix DLL `9e42d34f` = HEAD of `ts-units`; art ZIPs `4e187d5a` (TSSONIC) / `853725fd`
(TSSONICW). **First clip next session verifies, in one go:** turret horn faces the
target N/S/E/W, band leaves the horn, teal tint, ticks land fast, a Disruptor pair +
one mixed unit (pair unhurt, mixed unit hurt). Then Luke's Aseprite pass on the band.

**State at close (Luke: "cracking job" on the band; "not coming from muzzle";
"next session we aseprite it").** Everything below is COMMITTED on `ts-units`
and DEPLOYED to the desktop prefix (DLL `c8859224`, art `9e64ac1f`).

### What shipped this session (all verified by clip, six rounds)

- **Damage over time — WORKS, Luke-approved ("damage works well").** The band
  is the weapon: `Fire_At` no longer applies AmbientDamage for `IsSonic`; the
  first disc spawned in each cell past the firer's own is that cell's anchor
  (`AnimClass::SonicDamage = AmbientDamage/5 = 28`) and hits every techno in
  its cell on stages 6/10/14/18/22 (`AnimClass::AI`). The aimed-at object rides
  on the LAST disc as `SonicVictim` (TARGET; cleared in `Detach`). Kill credit
  is NULL-source, as the Ion Cannon. Railgun sweep untouched (`!IsSonic`).
  ⚠ Two new `AnimClass` members = save version moved again.
- **Envelope matches TS**: 25 stages × 5 ticks (~3.2 s at Luke's ~40 tick/s
  game speed — measured: 50 ticks ran in 1.2 s). Art stages 0-4 are fully
  transparent; muzzle discs start at stage 5, far ones at 0
  (`AnimClass::SONIC_LEAD_STAGES`), giving grow ~0.6 s / hold / retract-from-
  tank-end. Spacing 32 leptons (64 beaded visibly: 3-vs-4 overlap ripple).
- **Not IsTranslucent, no owner** on the discs. Both were changed while
  chasing the colour; both turned out irrelevant (see the trap) but neither
  is wanted, leave them off.
- **Generator patches the tileset** (`scripts/ts_gen_sonicwave.py` writes
  `RA_VFX.XML` to its own frame count).

### ⚠ TRAPS FOUND THIS SESSION (each cost a build round)

1. **A stage with no tileset entry draws the WHITE BOX.** Bumping the anim to
   25 stages with 8 tiles declared = boxes from stage 8 on. This is also, in
   hindsight, what the 2026-08 "endpoint-box / sub-object cell rule" was:
   **starting discs inside the firer's cell drew NO boxes tonight** (clip
   18-29-22). Rule falsified; `launcher-render-contracts.md` §4 needs the
   correction. The export loop draws every anim as its own root
   (`dllinterface.cpp:5905`).
2. **PIL `paste(colour, mask)` onto a transparent canvas darkens the RGB toward
   black** — the shipped TGA was (14,26,15) not (130,235,140), and rendered as
   grey (no owner) / gold (owner tint on a near-black sprite). Write
   `Image.new(COLOR+(0,))` + `putalpha(mask)` — straight alpha. **Check pixel
   RGB inside the ZIP after every regen** (the check is in this session's
   log: `Image.open(...).getdata()`).
3. **Per-disc alpha must be set for the STACK**: 6-7 discs overlap at 32
   spacing; 60 % per disc compounds to opaque mud. A_PEAK 30 ≈ 57 % total.
4. `Set_Stage(n)` then the first `Graphic_Logic` advances to n+1 before it is
   ever fetched: a hit keyed to stage n never fires for a disc started at n.
5. Data-only edits don't restage: `cmake -E copy_directory resources/... build/...`
   after every regen (memory already says so; hit it again).

### What TS does (answers given to Luke, from TS rules/engine)

- Wave = launched projectile. Tank moving or retargeting mid-wave neither
  cancels nor redirects it; next shot goes to the new target. Ours matches.
  Luke asked twice whether it *should* terminate — **open design question**,
  not TS behaviour. Cheap if wanted: firer keeps disc IDs, deletes on new order.
- Distortion = engine pixel displacement. Launcher has none (cloak export =
  darkening ghost, tested). Substitute shipped: per-stage noise field so the
  interior shimmers.

### Late-evening offline pass (Luke away, "keep going, get it like TS") — DEPLOYED UNVERIFIED

Deployed to the desktop prefix after Luke left (C&C not running; DLL
`0da82c27`, TSSONIC.ZIP `4e187d5a`, TSSONICW.ZIP `853725fd`). **Nothing
below has been seen in play.** Expected-look sheet for Luke:
`~/Desktop/disruptor-band-expected-2026-08-24.png` (offline compositor,
validated against the 17-37 clip to within ~20 levels).

1. **Turret N/S mirror FIXED (art permutation).** Pixel-matching the 18-29
   fire frame against all 64 frames: the game drew hull 24 + turret 56, the
   same index, and turret 56's horn DOES point east — my "barrel points
   north" read was the mount tower. The real fault: turret 32 showed the horn
   pointing SOUTH and 48 NORTH while E/W were right, i.e. the turret block is
   mirrored about the E-W axis relative to the body. `ts_pack_units_wave.py`
   now packs `turret[j] = render[(16-j)%32]`, and the shipped ZIP was
   permuted the same way. ⚠ E/W-right + N/S-swapped is the signature of a
   render taken from the OPPOSITE camera side, so the turret's perspective is
   from behind; a proper `renders_sonictur` re-render is a
   [[feedback-voxel-facing-sheet-loop]] job with Luke.
2. **"Not from the muzzle" — real cause = `PrimaryOffset`.** The horn tip
   sits mid-hull; 0xC0 put `Fire_Coord` (disc 0) a hull-length ahead of it.
   Now 0x50. Verify: band should overlap the turret and leave the horn.
3. **Colour**: COLOR (105,228,200) teal, A_PEAK 40, MOTTLE 0.5 (full mottle
   had halved the alpha). Sim says ~(160,226,212) over snow at hold.
4. **Texture/shimmer — SIMULATED DEAD for stacked discs (don't re-chase):**
   the 6-7 deep stack is a blur along the line, so per-disc noise, big
   clumps, sparse "carrier" discs (repeat as a dot grid) and expanding rings
   (chain-link artefacts) ALL measured flat (std ≈ background). Only
   cross-band variation and whole-band temporal change survive. If Luke
   wants TS's ripple, it needs a different mechanism (8/16-facing band
   sprites with a per-instance end stage, or the Aseprite pass painting
   the band itself), not more disc art. Compositor + variants live in the
   session scratchpad only (`sim_band.py`, `variants.py`, `sim2.py`).

### Luke's answers on the damage feel (2026-08-24, late) — BUILT + DEPLOYED (DLL `9e42d34f`), unverified

- *"Our band is too slow, I could stop firing, move the vehicle and damage
  myself."* → damage ticks compressed to stages 6/8/10/12/14 (all five within
  ~1 s of the crest; the rest of the hold is visual only), and the firer is
  exempt from its own band (`AnimClass::SonicFirer`).
- ✅ VERIFIED IN PLAY 2026-08-25 (Luke: "not hurting each other, good").
- *"Could Disruptors hurt other Disruptors? I built armies of them because
  they wouldn't hurt each other."* → correct for TS; **Disruptors are now
  immune to sonic damage** (any `UNIT_TSSONIC` skipped by the band, including
  as the aimed-at target). Mixed groups still take it, as in TS.
- Band termination on move/retarget left as-is (TS projectile behaviour).

### (CLOSED 08-27 — Disruptor arc final) the Aseprite pass notes

Open on the last clip (`Screencast from 2026-08-24 18-29-22.webm`), before
the offline pass above:
1. ~~"Not coming from the muzzle" / turret facing~~ → see the offline pass;
   **first clip of the session verifies items 1-3 there.**
2. ~~Colour too pale~~ → offline pass item 3.
3. Aseprite: Luke will hand-paint the disc/band frames; keep
   `scripts/ts_gen_sonicwave.py`'s ZIP/meta/tileset contract and feed the
   painted frames through `write_zip` + `patch_tileset`.
4. Queued: WF exit clipping report (Luke, 2026-08-24: "clipping on exit and
   pixels on the floor over the units again"). Verified NOT a code regression
   (clamp, floor band, lamp layer all intact; prefix == build). The 08-18
   record left two things open (pad stripes polish; column-over-hull on wide
   hulls near rail end). Needs a clip + unit name.
5. Queued: "is the RA Disruptor bigger than TS's?" — clips were at different
   zoom (285 px vs 57 px selection boxes), needs an in-game cell measure.

---

## (superseded 2026-08-24 evening) RESUME — 2026-08-25: Disruptor wave is MID-EXPERIMENT, UNVERIFIED

**Signed off this session:** Wolverine COMPLETE (firing animation, TSGUN4, canopy
dot) and in the ledger. Disruptor SONIC4 sound approved. **All shadows signed
off** across the whole roster. Cameos closed on all four.

⚠ **Old savegames are dead as of this session's builds** — `saveload.cpp:70-80`
derives the save version from `sizeof()` of every game class, and the Wolverine's
new `FireAnim` member on `UnitClass` changed it. It CRASHES rather than rejecting
cleanly. Luke hit this once already; a fresh skirmish is fine. Any future
per-unit state will do it again.

### (CLOSED 08-27) the video-first rule that closed the Disruptor — keep the habit, the item is done

**Before touching the Disruptor, ask Luke to capture a clip of the CURRENT build
firing.** He asked to be made to do this first, and he is right: on 2026-08-24 a
verbal report ("lots of work to do") cost a round of guessing, while the two
clips he did record each settled the question outright — the first falsified the
whole ring design, the second exposed three separate faults in one frame.

Captures land in `~/Videos/Screencasts/`. Pull frames with
`ffmpeg -i <file> -vf fps=6 out-%03d.png` and read them directly; measuring off
the pixels (band thickness against the selection box, colour against terrain)
beat every assumption made without them.

**Generalise it: for anything judged by eye, get footage BEFORE building, not
after.**

### (CLOSED 08-27 — superseded by the OpenTS port above) Disruptor state as of 2026-08-24

**Luke's verdict on this build (quick look, 2026-08-24 close):** *"lots of work
to do still, but better than it was."* So the three fixes moved it forward and
nothing regressed — but it is not close to signed off.

⚠ **What that verdict does NOT tell us: whether the stealth shimmer is actually
rendering.** "Better than it was" is also what the three non-shimmer fixes alone
would produce (no yellow beam, a fuller band, longer hold). **Establish this
first, before tuning anything** — otherwise you will be tuning constants on an
effect whose main mechanism may be inert.

Cheapest way to settle it: set `A_PEAK` very low (say 30) and look. If the wave
is still clearly visible, the launcher is contributing the shimmer; if it all but
disappears, `Cloak = CLOAKING` is being ignored and the sprite is doing all the
work — at which point try `UNCLOAKING`, then fall back to `UNCLOAKED` with a
higher `A_PEAK`.

**What Luke saw on the LAST verified build** (capture:
`~/Videos/Screencasts/Screencast from 2026-08-24 00-51-52.webm`) — "lots of work
to do":
1. A **yellow beam with big star bursts at both ends**. That was the railgun's
   3-line beam, which sonic was borrowing; the bursts are the launcher's endpoint
   artifacts on that line. **FIXED** — the Disruptor now draws NO beam line at
   all, which is also what TS does.
2. **One dark blob instead of a band.** Cause found by arithmetic, not guesswork:
   the spawn loop cleared 300 leptons at EACH end, so a ~3-cell shot
   (dist ~768) left a span of 168 = only 3 discs bunched mid-flight. **FIXED** —
   clearance is now one cell (256).
3. **Gone almost instantly.** **FIXED** — anim delay 1 -> 2 ticks per stage, so
   the band holds for ~1s instead of ~0.5s.

### ⭐ THE EXPERIMENT: the launcher's own stealth shimmer (Luke's idea)

Luke: *"the disruptor beam looks a bit like the stealth effect but with a blue
colour"*, then: *"clone it and use a unique new item?"* — which is what was built.

⭐ **`CNCObjectStruct` has a per-object `Cloak` field** (`dllinterface.h:228`)
that the launcher renders its stealth shimmer from. TS draws the sonic wave as a
live distortion of the terrain behind it, which a sprite cannot do — **but the
launcher already owns exactly that effect.** So `ANIM_TS_SONICWAVE` is now
exported with `Cloak = CLOAKING` in `DLL_Draw_Intercept`.

- **CLOAKING, not CLOAKED.** CLOAKED is the settled invisible state; the
  TRANSITION states are the ones that shimmer.
- **Scoped to that one anim type**, keyed off `Class_Of()`. It never touches any
  unit's real `Cloak` state, so genuine stealth units cannot be affected. (Note
  `AnimClass::Class` is PRIVATE — go through the public `Class_Of()`.)
- The sprite supplies the colour, the launcher supplies the distortion. Art is
  now blue `(120,200,245)` at `A_PEAK = 120`, lowered because the shimmer is
  meant to carry the read.

⚠ **THIS IS UNPROVEN.** The launcher may ignore `Cloak` on a non-unit object, or
may render CLOAKING as near-invisible. **If the wave vanishes entirely, that is
the first suspect** — try `UNCLOAKING`, then fall back to `UNCLOAKED` and a
higher `A_PEAK` (the plain sprite band, which is the known-working state).

### What the real TS effect is (measured, keep)

A **wide translucent BAND that sweeps out along the firing line** — not rings,
not a beam. Measured off `Screencast from 2026-08-24 00-38-41.webm` (834x465):

| Property | Measured | Shipped |
|---|---|---|
| thickness | ~39px vs a 108px selection box = **0.36 x unit width** | 107px disc in a 128px canvas |
| colour | mean (121,176,105) over (122,94,59) terrain -> **(130,235,140) @ ~60% alpha** | now blue per Luke's steer |
| interior | mottled, rippling | noise field, `MOTTLE = 0.30` |
| behaviour | extends outward from the muzzle | per-disc start-stage sweep |

⭐ **DISCS, NOT A BAND SPRITE — a spawned anim draws UNROTATED.** A band sprite
would only line up at one of eight angles. Overlapping circular discs build the
band at any angle; band thickness IS the disc diameter. **This constraint applies
to any future directional effect built from anims.**

⚠ **Spacing is load-bearing at 64 leptons** (simulated at true on-screen scale:
96 and 128 scallop the band into visible beads).
⚠ **The fade envelope must HOLD, not peak** — a triangular fade left most stages
invisible and killed the far half of the band once discs were staged.
⚠ The sweep uses each disc's **start stage**, never a spawn delay: the
`AnimClass` ctor's `timedelay` param is off-limits, and the ctor ends with
`Set_Stage(0)` so a post-construction offset sticks.

⭐ **TS has NO sonic-wave art to port** — probed CONQUER.MIX and LOCAL.MIX for
every plausible name. Don't go looking again.

### ✅ Also done, unverified in play

- **Disruptor now stops to fire.** TS `[SONIC]` carries `NoMovingFire` ("This
  MUST be set to true for the sonic tank"); our port had left it off and the
  engine already supported the flag.
- **Scorch is railgun-only now** — TS's `SonicWarhead` sets no scorch.

### ⚠ Open bug, untouched

**TS power plant and TS radar place one tile below their placement grid**
(reported in play 2026-08-24). Logged with first suspects in `known-issues.md`.

### ✅ The four cameos — FIXED 2026-08-22, deployed, data-only (no DLL rebuild)

⭐ **The trap: `TF_Apply_Cameo_Badge` ALWAYS appends `_<hex>` to the sidebar
AssetName**, even when the badge is zero. TS-tree types force `held = 0`
(`TF_Is_TS_Tree_Type`, keyed off a TS building in `Prerequisite`), so the
sidebar asks the launcher for **`RA_<IniName>_0`**, never the bare name.

All four units already had correct BASE entries in `RABUILDABLES.XML` pointing
at real, present art — what was missing was only the `_0` variant, so the
lookup fell through and no icon drew. Added `RA_TSSMEC_0`, `RA_TSSONIC_0`,
`RA_TSAPC_0`, `RA_TSHARV_0`, each pointing at the same `BuildIcon` as its base
entry. The cameo TGAs were already shipped by `ts_pack_units_wave.py`; no art
was generated.

**Audit run after the fix: no other `RA_TS*` entry is missing its `_0`, and no
TS entry points at absent art.** (`RA_TSLA_0` -> `BuildIcon_RA_TeslaCoil` is
RA's own Tesla Coil resolving from the base MEG, not a gap.)

**Rule for any future buildable:** a base `RABUILDABLES.XML` entry is not
enough. Every buildable needs the badge variant the sidebar will actually
request — `_0` for anything TS-tree-gated.

⭐ **The cameo ART already exists for all four.** `ts_pack_units_wave.py` decodes
HARVICON / SMCHICON / SONIICON / APCICON against CAMEO.PAL, and
`BuildIcon_TS_Harvester|Wolverine|Disruptor|AmphAPC.tga` are all present in
`Data/ART/TEXTURES/SRGB/`. So "needs a sidebar icon" is a **wiring** job, not an
art job — the runtime AssetName switch at `dllinterface.cpp` ~5690/~5852 is the
mechanism. Do not re-generate the art.

**The weapons are ported; what is missing is presentation.** Both units already
carry TS-verbatim weapon stats, and both are standing in on borrowed
presentation pending the TS audio wave:

- `[AssaultCannon]` (Wolverine): Dmg40 / ROF50 / Range5 / Projectile=Invisible /
  Warhead=SA — TS verbatim. `Report=MGUN11` (TD heavy MG) stands in for TS
  **TSGUN4**; `Anim=GUNFIRE` is RA's generic muzzle flash. The projectile is an
  instant invisible hitscan, so there is nothing in flight to see — which is why
  it reads as borrowed. It is NOT the Humvee's weapon.
- `[SonicZap]` (Disruptor): IsSonic piercing line on the railgun sweep, green
  beam, no helix, through `WARHEAD_SONIC`. `Report=OBELRAY1` (TD Obelisk ray
  hum) stands in for TS **SONIC4**.

So both sound items are one shared job: pull TSGUN4 and SONIC4 out of TS
SOUNDS.MIX. Precedent is HOVRMIS1 (`ts-asset-import-spike.md`), and the
dormant-host WAVs MUST be MS-ADPCM (`launcher-render-contracts.md`).

### The shadow fix: EA's throw is a FIXED PIXEL DISTANCE, not a fraction

Round 2 (dx 0.028w / dy 0.120w) was rejected in play: "sticks out far too much",
"makes the Mk. II look like it's floating", "any TS unit sat with a TD unit
looks ridiculous". Opacity was explicitly fine.

The premise under rounds 1 and 2 was wrong. `ts_reshadow.py` asserted EA bakes
"an OFFSET SILHOUETTE of the body" fitted at IoU 0.72-0.88 — but EA's shadow
bbox sits INSIDE the hull bbox on all four edges, which a translated full-size
copy can never produce. Measured per-column across nine base-game vehicles from
122px to 228px of body width, the throw is a flat **-5 to -7px** and the visible
shadow is **6-12% of body pixel area**. Body width nearly doubles across that
set and the throw does not move.

Sizing the throw off the sprite is what broke it: our TS sprites run to 301px
wide against RA's largest at 228, so 12%-of-width gave the Mk. II a **41px
overhang** where a TD tank has a 6px tuck.

**Shipped: `EA_DX = 2`, `EA_DY = 6`, absolute pixels, every unit.** Alpha stays
191 and was never wrong. Result, measured on the real art:

| | before | after | EA's range |
|---|---|---|---|
| TSHMEC | +41px / 24% | +6px / 5% | ~6px / 6-12% |
| TSSONIC | +36px / 33% | +6px / 6% | " |
| TSMCV | +34px / 29% | +6px / 6% | " |
| TSAPC | +30px / 27% | +6px / 6% | " |
| TSHARV | +25px / 28% | +6px / 8% | " |
| TSTITN | +18px / 22% | +6px / 9% | " |
| TSSMEC | +15px / 20% | +6px / 10% | " |
| TSHVR | +17px / 41% | **untouched** | Luke's approved hover float |

⚠️ **Never re-express the throw as a fraction of the sprite.** Two rounds were
rejected in play for exactly that. The fraction also punishes our biggest art
hardest, which is backwards — the Mk. II is the unit most often parked beside a
TD tank.

### Hover MLRS still-shadow experiment — PARKED, not built

Luke asked whether the shadow could stay still while the hull bobs, to sell the
hover. Traced and costed: the bob is `y += _hover_bob[(Frame >> 2) & 7]` at
`unit.cpp:2802`, applied to the whole draw, so the baked shadow rides along.
The launcher makes the FIRST `Techno_Draw_Object` the base draw and sorts every
later draw above it, so the fix is to draw a shadow-only shape block first at
the un-bobbed y, then hull and rack at the bobbed y.

`scripts/ts_hover_split_shadow.py` implements the art half (64 -> 96 frames:
hull 0-31 stripped, rack 32-63, shadow 64-95) and is complete but **PARKED and
reverted**. Once the ground units came down to 6px, the MLRS's 17px shadow read
as its own thing and Luke's verdict on the existing bob was "looks ok". If it is
ever revived it also needs the `Draw_It` re-order AND a 96-frame classic stub in
`build_tfassets.sh` — the art alone renders the hull with no shadow.

### Two traps worth keeping

- **A regenerated art zip never md5-matches**, even when the art is identical:
  Python's `zipfile` stamps the current time into every entry. Compare member
  names + bytes, not the file hash, when checking source against deployed.
- **Re-measure the SOURCE on a rejected round, and `git checkout` the art back
  to the pre-pass checkpoint before re-applying** — otherwise the rejected
  round's fringe is baked into the next one. Done here: all eight zips were
  restored to `bbb6b7b7^` before the new constants were applied.


## ⭐ SIGN-OFF LEDGER — GDI units Luke has declared COMPLETE

A unit here is **done**: no open art, geometry or behaviour work, and it is not
to be reopened for polish without Luke saying so. The end-of-roster generic
lightness pass (open queue 15) is the ONE exception that may still touch them.

| Unit | Signed off | Notes |
|---|---|---|
| **Hover MLRS** (`UNIT_TSHVR`) | 2026-08-19 ("we have a winner") | The rack/diagonal arc closed in full: 32° render, `Hover_Rack_Seat()` two-part seat, Facing32 resting indices 3/13/19/29, centroid-pinned spin. Four rejected rack shapes are recorded in the arc block below — do not re-offer them. |
| **Mammoth Mk. II** (`UNIT_TSHMEC`) | 2026-08-22 | Signed off once the railgun question was closed: **TS has no railgun animation to extract.** `[MechRailgun]` drives `AttachedParticleSystem=LargeRailgunSys`, whose particle `[LargeRailgunPart]` carries no `Image=` and has zero ART.INI entries — TS generates the spiral in its particle engine and draws it as coloured pixels. Nothing to port. TS's genuine numbers, if ever wanted: SpiralRadius=15, ParticlesPerCoord=.15, SpiralDeltaPerCoord=.03, LaserColor=25,20,255, particle fade (25,70,205)->(150,150,150) over MaxEC=70. |
| **Titan** (`UNIT_TSTITN`) | 2026-08-21 | Signed off in the shadow walk, after the 6px fixed throw replaced the width fraction that had given it an 18px overhang. |
| **Wolverine** (`UNIT_TSSMEC`) | 2026-08-24 ("wolverine signed off, nice one") | Complete: sidebar cameo, TS firing animation (art.ini `FiringFrames=4`, SMECH.SHP 104-135 — the flash is a sprite block, TS gives `[AssaultCannon]` no `Anim=`), TSGUN4 sound, and the canopy red dot (authentic TS ramp tail, tamed at the palette via `ts_shp.py --pal-override`). Shadow passed in the same load. |
| **TS MCV** (`UNIT_TSMCV`) | 2026-08-20 | 32° render play-praised earlier in the wave. Final change: `Speed=3` → `5` to match the TD MCV family. ⚠ That speed edit was signed off BEFORE it reached play — see the caveat below. |
| **Disruptor** (`UNIT_TSSONIC`) | 2026-08-28 | Band FINAL (no pulse; four ripple mechanisms falsified), OpenTS WaveClass firing behaviour, turret seat + horn-rooted muzzle, cameo, sound. |
| **Amphibious APC** (`UNIT_TSAPC`) | 2026-08-28 ("perfection") | OpenTS pass: unload fix, apcw water hull frames, SPEED_AMPHIBIOUS + TS land table, cameo. |
| **TS Harvester** (`UNIT_TSHARV`) | 2026-08-30 | Docking at the TS, TD and RA refineries closed 08-28 (ROLL_OFF_DOCK_SEAT rail); TS-harv-at-RA-refinery SIGNED OFF in play 2026-08-30; WF door seat swept 08-30. Cameo done. |

**Titan (`UNIT_TSTITN`) was pulled off this list on 2026-08-20 and put back on
2026-08-21**, signed off with the Hover MLRS and MCV once the shadow throw came
down to EA's 6px.

**⚠ TS MCV caveat, kept until it is cleared:** the `Speed=5` edit was staged and
signed off while the game was running, so it has never been driven. If the MCV
reads wrong in play, the sign-off does not bar fixing it — that is a
not-yet-verified change, not settled work.

**⚠ TSHVR stub dims are LOAD-BEARING — do not "fix" them.** The Hover MLRS
classic stub is **48x48** (`build_tfassets.sh`), matching `[TSHVR]
ShapeSize=48,48`. Three comments used to claim it was 64x64 "so the launcher
sizes it as a large platform"; the code never did that, and the comments were
corrected 2026-08-20. The stub dims drive sprite / health-bar / selection-box
scale, and **the whole eye-dialled rack seat table was tuned against the sprite
at 48x48**. Bumping the stub to match the old comments would rescale the sprite
and invalidate every approved seat. A chain audit (2026-08-20) found this was
the only functional ambiguity in either signed-off unit.

## ⭐⭐⭐ RESUME HERE — 2026-08-19 evening: MLRS rack ARC COMPLETE — "we have a winner" (`142001ab`, prefix DLL `da1d78c9`)

**The whole diagonal + turret-jump arc closed in one evening session.**
Four separate faults, each proven by receipts (tf_facing.log / video
frame tracking / art measurement) before fixing — full detail in the
`142001ab` commit message:

1. **Facing32 resting indices**: EA's 3D-Studio 45° compensation means a
   resting exact-diagonal heading reads seat idx **3/13/19/29**, never
   4/12/20/28 — every early diagonal mark went to slots only swept
   mid-turn. Proven with a probe table + the 8-rose + tf_facing.log.
   Final eye-dialled anchors: N(0,2) NE(-5,0) E(-9,-6) SE(-5,-9)
   S(0,-10) SW(5,-9) W(9,-6) NW(5,0) (SW/NW = x-mirror of SE/NE,
   rose-verified).
2. **Mount pendulum**: RA pathing flicks the hull heading per move cell;
   a raw hull-keyed mount jumped px per flick → draw-side slewed hull
   facing (glides 1/4 gap per rendered frame, display-only state).
3. **Aspect pop**: side-on pod art ~20px taller than end-on; rack swing
   slowed to 3 dirs/tick so sweeps render as rotation.
4. **Spin slip-slide** (Luke's diagnosis): each pod frame's content sat
   differently in its crop → the rack-facing seat component now cancels
   per-frame centroid offsets; stationary spins pinned to ~1px; rest
   poses reproduce the dialled seats EXACTLY (asserted).

Turret behaviour is fully classic (destination lead + target tracking);
hover bob kept (tested innocent). `Hover_Rack_Seat(hull, rack)` in
udata.cpp is the two-part seat; the four failed shapes (hull-locked
draw, instant snap, rack-keyed seat, raw two-part) are in this
session's history — don't re-offer them.

**Loop that worked**: aseprite drag for coarse (round-2 files =
`~/Desktop/hvr-pods-round2/`, TRUE resting art frames 29/19/13/3), then
**EWNS + notches by eye** (1 notch = 1 classic px ≈ 6 screen px), with
engine receipts (tf_facing.log logs idx + tfacing + seat per change)
whenever anything smelled wrong. AS-DEPLOYED-32.png sheet generator
pattern lives in the session transcript.

**Next**: WF stripe polish round still queued; open queue below.

## (superseded) 2026-08-19 ~01:30 close: MLRS 32° SHIPPED (cardinals approved), diagonals NEXT SESSION

**State at close (Luke: "we'll do the diagonals next session"):** the
Hover MLRS runs the 32-degree renders in play — hull + rack ambient
0.50, drum z-clipped (`--z-clip 10`), rack position fully in the engine
aft-seat table. **Cardinals N(0,2) E(-9,-6) S(0,-10) W(9,-6) dialled by
Luke's Aseprite marks and play-approved ("NESW good"). Diagonals =
cosine blend through those anchors, deployed interim — "diagonals need
work".** Worktree committed `020a70c6`; prefix DLL `15cee39c` + the
session's art.

**NEXT SESSION FIRST — the four diagonal marks.** Everything is staged:
`~/Desktop/hvr-pods-aseprite/hvr_{NE,SE,SW,NW}.aseprite` (hull locked +
pod layer at the deployed blended seat; per-file `*_baseline.json`
records seat + indices). Loop per file: Luke drags the pod layer,
Ctrl+S → read the POD cel DIRECTLY (cel.position + content bbox — the
hide-hull-then-flatten reader LEAKS the hidden layer, never use it;
scripts in scratchpad pattern `read_s2.lua`) → delta/6 = classic px →
bake the seat index (NE=4, SE=12, SW=20, NW=28) → rebuild DLL → deploy.
After all 8 anchors: re-blend the 16ths through them; Luke slow-turns a
unit to catch residual wobble (turret hop during rotation = un-dialled
entries stepping — his diagnosis, confirmed).

**Protocols that made tonight work (KEEP):**
- One .aseprite per facing, TWO layers (hull locked, "POD - move me"),
  pod pre-placed at the CURRENT deployed seat so the drag IS the fix.
- Deploy-then-notify: he exits fully, I deploy on the pgrep-exit watch,
  I say "go", THEN he relaunches (instant relaunch can race the 5s
  watcher and load stale — explained several phantom "wrong way" rounds).
- Verbal pixel nudges FAILED repeatedly (sign/scale confusion);
  marks-only. Seat resolution = 1 classic px ≈ 5 screen px; his S mark
  proved sub-classic wishes can't be expressed in the seat.
- Derivations: E↔W mirror HELD, N↔S mirror FALSIFIED, first blend with a
  bad anchor read "all west" — blends only through APPROVED anchors, and
  only as interim.

## ⭐ PARKED ARC — Hover MLRS at the 32-degree camera (2026-08-19 00:0x)

**Spec, Luke's words: "the rocket pod sits centered at the back."**
Ground truth = `docs/reference-art/tshvr-pods-source-of-truth.png`
(crop of ss 2026-08-18 00-42-31, SE facing): pods centered on the hull's
width axis at the AFT end, riding the hull tilt, low against the deck.

**State:** the SHIPPED TSHVR art is live (restored byte-for-byte after
the 32-degree attempts; prefix verified). MCV/APC/Disruptor keep their
32-degree art (MCV play-praised). FOUR rejected candidates — do not
re-offer: pure 32 canvas-centered (pods flew: rack height bakes into
the art, seat mistuned), pure 32 content-centered (pods seated but
TOWER: cos32 draws heights 1.44x cos54), rack v-squash 65-85% ("EVEN
WORSE"), hybrid 54-pods-on-32-hull + split camera 32-ground/54-height
(both "garbage"). vxl_render gained `--height-elev` (kept, unused).

**Next-run plan (agreed direction, not started):**
1. Recompute the engine aft-seat table `_aft_x/_aft_y` (udata.cpp
   ~2457) for the 32 camera — it bakes sin54 ("13/16 vertical"); the
   recompute is deterministic (aft ground distance 18, project with the
   new camera), then fine-tune by Luke's eye.
2. Dial the rack's rendered look against the reference crop WITH Luke
   (sheet → his verdict → adjust), packed-zip compass sheet approved
   BEFORE any deploy — never discover a candidate in-game again.
3. Consider matching against actual TS in-game look (TS is installed)
   if the reference crop under-constrains.

## ⭐⭐⭐ RESUME HERE — 2026-08-18 afternoon close: lamps SHIPPED + approved, two open lamp issues

**State at close (Luke: "lets wrap up here"):** the WF lamps arc SHIPPED
same day it started — `8a396a7f` — and play-approved ("the lights are
working, love it"). Desktop prefix = DLL
`95998492472b8e06739c4d1c1629a9fd` + TSWEAPLT art, md5-verified;
worktree committed through the checkpoint commit after this block.

**The lamp mechanism (`8a396a7f`):** new TSWEAPLT layer = the near-face
region cut from EVERY idle phase (8 healthy + 8 damaged, full-canvas
registration, same crop as TSWEAP2), drawn in building.cpp right after
the TSWEAP2 draw at `Shape_Number()` (auto-synced to the body's idle
stage — the anim machinery at bdata.cpp:4906 was running invisibly all
along), sorted ONE notch (+136 lep vs +128) above the door overlay.
Packer emits it in build_structure's door block (`lamp_runs`), stub via
build_tfassets.sh (168x126 x16), RA_STRUCTURES.XML + TFASSETS.MIX wired.
Pre-game verification loop that worked well: composite lamp frames over
TSWEAP2 frame 0 → GIF + a phase-diff-union "lamp location" map.

### Both close-of-session issues FIXED and DEPLOYED — in-play verdict OWED

**Issue A — door/floor seam pixels over exiting units (Luke, 13:25:
"some of the pixels on the line where the door meets the floor are
rendering over the units as they leave").** Cause as hypothesised:
TSWEAPLT carried the WHOLE face per phase, re-drawing TSWEAP2's
antialiased seam edge on top of itself — double alpha blend ≈ twice the
opacity over the clamped exiting unit. FIX (deployed): lamp frames are
trimmed to pixels that CHANGE against phase 0 (|Δ|>30, MaxFilter(5)
dilation for the glow edge) — verified in the packed zip: frame 0
EMPTY, other frames only lamp clusters (~150-260px crops vs the 459px
face), nothing below canvas y=263, the seam gone from the layer.

**Issue B — lamp cadence ping-pong (Luke: "run once, then run in
reverse, then loop, like the radar and con yard").** FIX (deployed):
build_structure gained a `pingpong` flag (TSWEAP only) that reorders
the composited frames fwd+back at the composite level (8 → 14 frames,
0-7 + 6-1), so base AND lamp layers inherit the same order and stay
Shape_Number-locked; `_anims[]` Count 8→14 (bdata.cpp:4906), TSWEAPLT
stub 16→28, tileset counts auto-patched (TSWEAP 28, TSWEAPLT 28).
Verified in the packed zips: frame1==frame13, frame2==frame12,
frame5==frame9 byte-identical; frame0≠frame7.

**Round 2 (Luke's 17:26 regression report, ss 17-26-22):** the door
COLUMN sat over the Titan's torso mid-exit, and the door/floor seam
still rendered over its feet — BOTH are the exit clamp holding the unit
under the whole face for the entire rail (the seam pixels were
TSWEAP2's own, at the `ap_bottom` cut line — the lamp trim never
touched them; the double-blend theory was only part of the story).
FIXES (deployed): ① the near-face cut now removes 3 extra source rows
above `ap_bottom` — the seam band (HD rows y376-390, verified) moved
into the BASE layer, which sorts under units, and the idle composite is
pixel-identical; ② the Titan's rail releases the clamp 32 leptons south
of the bay-mouth line (`On_TS_Titan_Exit_Track()` +
`Coord_Y(Sort_Y) > clamp+96` in the export block) — tall and narrow,
it clears the roof there, and the column falls behind its torso. The
DEFAULT rail keeps the full-rail clamp: wide hulls overlap the
east-wing roof to the last waypoint (the original pop). Watch for
column-over-hull on WIDE units near the rail end — accepted trade-off
for now, flag if it reads badly in motion.

**Round 3 (evening, Luke's red-pixel markup session):** three artifacts
on the APC exit pinned by Luke painting the exact pixels red (ss
22-12-42; registration ss→canvas = +200,+114 at 1:1, FFT on gradient
maps). ① L-shaped frame foot (canvas y373-385) and ② upright bar
(y329-341) rendered over the emerging hull → **the floor-band layer**
(`ff37bc39`): the overlay's bottom 62 canvas rows (y329-390: ramp lip,
frame feet, wall bases, shutter bottoms) split into TSWEAP2L, drawn
after TSWEAP2 at the same door stage, sorted at Sort_Y+56 (one notch
under the exit clamp's +64) — emerging units pass over the floor
furniture, deep-bay units stay under it, partition exact.
**① and ② PLAY-VERIFIED FIXED (Luke).** ③ leftover hazard-stripe patch
on the pad west of the mouth → erased from the BASE (marked box
+2px, canvas 353-370 x 402-443); the hand-tucked pad shows through.
⚠ **A wider remap-green sweep of the whole south skirt WIPED WANTED
ART and was REVERTED on Luke's instruction** — his marked pixels were
the whole spec ([[feedback-user-marked-pixels-are-the-whole-truth]]).

**Round 4 (late evening): tall-tower placement ghost FIXED + play-verified
(Luke: "fixed").** TSPOWR/TSRADR placed with a one-row ghost a cell below
the cursor (placement list followed the south-row footprint while the
launcher anchors the cursor on the BSIZE origin) and could anchor a row
higher at the map top edge. Fix `f25ec5e3`: full-2x2 placement list
(the radar height trick), blocking unchanged; prefix DLL = `40794b46`.
Note: AI placement legality tightened by the headroom row for these two
— half an eye on PLACE-FAIL in future AI games.

**Session close (Luke: "lets leave it as it is... polish round
later"):** some stripes remain visible in play; queued for a POLISH
ROUND driven by another markup pass, not by filters.
⚠ **PREFIX/REPO DRIFT AT CLOSE:** the desktop prefix still holds the
REVERTED-sweep art's predecessor (the over-erased sweep build, DLL
`15e2c38b`); the repo (`ff37bc39`) holds the correct box-only art.
First deploy of the next session reconciles — repack is NOT needed,
just restage `resources/` → `build/` and rsync (game closed).

**State:** the WF spawn/exit arc is fully CLOSED — rails play-approved
("new positions, perfection!") AND the roof-clipping pop squashed
(Luke: "i declare that bug squashed", 2026-08-18 13:04 run). Desktop
prefix = DLL `fc84260f8e5951e3d5a25e9785317a15`, md5-verified; worktree
committed through `8a24deaf`.

**The clipping fix (`8a24deaf`):** cure (a) from the writeup below — the
factory stamps `TsExitSortClamp` (its Sort_Y +64 leptons, 524288 sort
units under the TSWEAP2 overlay key) on the unit when it assigns the
exit rail; the render export clamps the unit's BASE draw only (sub-object
+n layering keeps its headroom) while `On_TS_Exit_Track()`, so the hangar
clips the unit for the whole glide and normal sort resumes at the
handover cell, which is free of hangar art. Verified two ways: Luke's
play verdict, and the clamp signature in tf_sort.log (sort key pinned
constant across 29 moving frames for BOTH rails — TSAPC default seat,
TSTITN own seat). Video-analysis method that pinned it: extract all
frames (`ffmpeg -vsync passthrough`), diff a roof-region box against a
reference frame to find pop windows, then read keys off the same
session's tf_sort.log — the first over-key frame landed at exactly the
overlay key's lepY.

**RETRACTED same session — "bug 2" (east-side draw-over) was a
thumbnail misreading, NOT a defect.** At full zoom every frame of the
harvester's post-exit drive north along the building's east side renders
correctly (clipped behind the roof beam and strut; frames drawing over
the strut base have the unit genuinely south of the art's ground line —
correct painter order). Do not re-chase. Lesson re-proven: zoom-diff the
actual frames against a temporally-close clean frame before declaring a
render bug ([[feedback-identify-occluder-before-flag-changes]]).

**What shipped tonight (all play-verified):**
- **Forced exit rails replace organic pathing** — the recentre-leg slide
  is dead. `Force_Track` plays a generated straight rail per unit type:
  Track19 (default seat, magenta marker, XYP(48,29), dir 93) and Track20
  (Titan's own seat, orange SPAWN TSTITN marker, XYP(48,19), dir 99),
  both ending on the centre of **tile 13** = plot cell (3,2), the
  reserved handover cell (pinned in building.cpp, generator-checked).
  Hull faces the line every waypoint; `Force_Track` gained an optional
  boarding-index param (unused, for future same-rail seats).
- **The whole loop is Aseprite-driven:** `wf_spawn_preview.py` reads both
  markers → emits `tsweap_exit_track{,_titan}.inc` + `tsweap_exit_seats.inc`
  (consumed by BOTH bdata.cpp and building.cpp — no hand-typed seat left),
  stamps the rails into the sheet (RAILS -- GENERATED layer, yellow=default
  orange=titan), renders the honest GIF with per-facing sprites. Drag a
  marker → re-run → rebuild; the script hard-errors on any seat/dest drift.
- **Front-row corner blocking** (cells (0,2),(1,2) back in TsWeapList) —
  units no longer drive over the hangar's drawn SW corner (`8af6f4ec`).

**NEXT: the lights arc (Luke):** bring back the WF's animated lights
(GTWEAP_A/_B/_C idle anims). tf_sort.log diag still ACTIVE (#if 1,
dllinterface.cpp ~5240).

**Also queued from tonight:** Open-queue item 15b — per-model unit-angle
revisit (hover MLRS a facing step off vs TSHARV/TD med tank, SS 00-42-31).

**Superseded tonight:** the recentre law + CELL CENTRES zero-slide seats
(rails make any seat slide-free); OPEN DECISION 1 (Titan containment via
stub 56→50 / sheet 73) — the Titan's 5px-north seat was approved in play,
containment never re-raised; re-open only if Luke flags it.

## ⭐⭐ SUPERSEDED — WF descale (2026-08-16/17): respec DEPLOYED, issue list below

**Status at session end (Luke's call, ~00:50): the descale CONTINUES — an
earlier wholesale revert was itself reverted (Luke: "I haven't asked you to
revert"); the stash was popped and a TSPROC-parity respec built and deployed.
Desktop prefix = DLL `4ed60756` + run-12 art; worktree committed at this
state.** Deployed geometry: fit_w 460 (hangar 70x44 at margin 51, west 3
cols), BSIZE_43 4x3 plot with pad col + front row IN-plot (TSPROC parity,
Luke's original call), ghost 5x3, ensemble selection box 104x58, sort band
128, XYP(56,33) spawn (inside the small-unit containment window), spawn
diagnostics to MOD_DEBUG_AI.txt (TF_DEV-gated), TSTITN draw-rect bias -12
keyed on AssetName.

**NEXT SESSION WORKS WITH ASEPRITE (Luke, session close):** the WF art/pad
work goes through Aseprite — prepare reference exports the way the
harvester-docking arc did (`~/Desktop/docking-art/` pattern: full-canvas-
aligned frames + an INDEX.txt) so Luke can inspect/mark up/hand-edit the
actual pixels instead of judging geometry through build-deploy rounds.
Candidates to export ready-to-open: the TSWEAP composite (hangar + pad +
door layers on the canvas grid), the sliced TSWEAPBB tile sheet, and a
buildup final frame for the handoff comparison (issue 2).

### OPEN ISSUES (Luke's end-of-session list, in priority order)

1. **CLOSED 2026-08-17 evening — pad renders fully in play (Luke: "3*5
   works nicely now with apron").** Root cause was NOT render code: the
   08-16 session's final 00:38 pack run never restaged from `resources/`
   into `build/` (the data-only-restage trap), so every played round drew
   an older TSWEAPBB — while the contact-sheet verification read the new
   one. Restaged + deployed; the TF_DEV apron-emission log confirmed all
   15 cells emit a perfect contiguous grid (correct shapes/positions), so
   the `_aprons` loop and the launcher were both always fine. The
   overlap-list culling theory is DEAD. Rule reaffirmed: after any
   ts_pack_tree.py run, restage into build/ before judging art in-game
   (`rsync -ac resources/remaster_mods/Vanilla_RA/Data/ 
   build/remaster/Vanilla_RA/Data/`).
2. **CLOSED 2026-08-17 evening — buildup handoff ("build up looks good",
   Luke)**: the buildup now carries NO pad pixels of its own (ts_pack_tree
   erases them outside the building silhouette); the ground tiles draw
   beneath the buildup from placement, so there is nothing to jump.

**⭐ THE 2026-08-17 EVENING ARC — the 4x3 hand-authored respec (all
deployed, DLL `93ccd729`):** Luke hand-tucked the pad in Aseprite
(`resources/custom-art/wf-pad-edit.aseprite`; the pad canvas is the
committed packer source — ts_pack_tree consumes it via apron_canvas, the
affine'd GTWEAPBB is no longer used for TSWEAP). Grid/smudge/ghost all
4x3 = the plot; ensemble centred on the plot (margin 40.5) so the box
hugs at 96x49 with no compromise dims; spawn dialled by dragging the
SPAWN layer in the same Aseprite sheet (currently XYP(56,21), deep bay);
`scripts/wf_spawn_preview.py` renders the spawn-and-drive-out GIF from
the marker — the no-game-reload iteration loop. **Sandwich sort fix:**
the bay interior (asset TSWEAP) now sorts at the plot's NORTH edge
(-384 leptons) — the centre-line default hid any unit spawned north of
y=36 classic (engine-proven in tf_sort.log). Engine spawn order is
already unit-first-then-shutter, facing DIR_SE. Stale 08-07
STRUCTURES/TSWEAPBB.ZIP deleted (repo+build+prefix).
**OWED IN PLAY:** spawn seat verdict, box 96x49 verdict, ghost 4x3
verdict, door-reveal + SE walk-out confirmation.
**QUEUED NEXT (Luke, 2026-08-17):** bring the WF's animated lights back
(the GTWEAP_A/_B/_C idle anims — window/light blinkers).

3. **Spawn point: now marker-dialled (see arc above).** Dial from
   DATA now: every TSWEAP spawn logs bldg origin / Exit_Coord / unit coord
   to MOD_DEBUG_AI.txt — read the log against one SS before moving XYP
   (56,33). Titan's feet stick out the door: that is the PARKED containment
   question (Titan 52.2px vs 44.1px art; options recorded below) — Luke:
   "stop worrying about the titan, we'll respond once the resize works".
4. **Selection box** now ensemble-sized (104x58, refinery pattern) — no
   verdict yet on this build; verify with Luke, dial dims only (position is
   launcher-owned on BOTH axes, six falsified probes).
5. **Ghost 5x3 + built-vs-ghost match** — no verdict yet on this build.
6. In-play sweep once 1-5 close: door cycle + sort (no pop-in front of the
   shut door), exit fan first-choice (2,2), APC/harvester full hide,
   capture/sell/repair on the new footprint, AI builds and uses it.
7. Consistency question Luke floated (parked): TSPROC's own pad taper vs
   its 4x3 ghost — revisit only after the WF pattern is signed off.

**The four coupled constraints (any further resize must satisfy all at
once, computed BEFORE building):**

1. **Containment (the binding constraint):** the sandwich hide needs art
   height ≥ the tallest exiting unit. ⚠ **The Titan is 26.1/26.1 = 52.2
   classic px tall — the "37 above/29 below = 66" figure further down this
   doc is the MAMMOTH MK. II's, wrongly applied to the Titan on 08-07.**
   Art ≥ ~53 tall ⇒ (at tonight's packing ratios, 0.151/0.096 classic per
   fit_w px) fit_w ≥ ~550, art ~83x53 — a real descale from the original
   ~94x66 is possible WITH containment. Alternative: shrink the Titan via
   its classic stub (56→50 = x0.89, one line in build_tfassets.sh, shadow
   included, no art repack) and descale further. At Luke's 460 pick
   (70x44) containment is impossible and the Titan visibly stands outside
   — rejected.
2. **Box:** contract #7 extended — **CenterCoordX is ALSO ignored (6th
   falsified probe)**: the launcher owns box position on BOTH axes. A
   bang-on box requires plot ≈ art rect with the art centred (TDFACT
   parity gives it with DEFAULT dims, no export case). 3x2 hugged the
   70x44 art perfectly; re-derive for whatever size is chosen.
3. **Ghost honesty (Luke, emphatic):** the ghost must cover every cell the
   built ensemble's ground art touches — his final call was ghost 5x3 for
   the full pad incl. taper. **Hard-clipping the pad art to a smaller grid
   "looks like garbage"** (re-confirms the 08-05 hard-edge finding).
4. **Spawn INSIDE, non-negotiable:** units must spawn hidden in the
   building and drive out, TD/RA-style. A delayed-unlimbo "materialise at
   the open door" was built and Luke rejected it outright — reverted.

**Also learned, keep regardless of the arc:**
- The 08-16 "FULLY REVERTED" state lasted minutes — Luke had not asked for
  it. Reverting is a decision, not a fix (now in global CLAUDE.md; never
  suggest session end either — Luke decides both).
- **Units reach the object export with NULL shape_file_name** — per-unit
  render biases must key on the final `AssetName`, not `shape_file_name`
  (the first cut of the TSTITN registration fix was dead code).
- TSTITN registration (+11.8 south, known-issues 13): a
  `PositionY -= 12` draw-rect bias keyed on AssetName is the right shape
  of fix (in the stash; never cleanly play-verified — confounded rounds).
- The pad emblem `~/Desktop/ts-gdi-logo.png` was Trash-cleaned and broke
  the pack; recovered to `resources/custom-cameos/ts-gdi-logo.png`
  (committed). The stash carries the packer change that reads the repo
  copy — land it with the next arc.
- Process (the real lesson): the ROUNDS burned Luke — geometry was probed
  live one knob at a time against coupled constraints. Next attempt:
  compute all four constraints on paper first, get Luke's sign-off on the
  numbers, ship ONE build.

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
y 3.9..71.8 of the 72px plot. **CORRECTED 2026-08-17: the 37-above/29-below
= 66px figure is the MAMMOTH MK. II's; the Titan is 26.1/26.1 = 52.2 px
(measured from the packed ZIP metas).** With the Mk. II gone to the dropship
bay, the tallest exiting unit is the Titan and the true window at this art
size is ~[30, 45.7], not two pixels — y=42 sits inside it, which is why it
worked. Depth is the near face's job, not the exit point's. Any hangar
resize re-derives this window against the 52.2px Titan.

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
4. ✅ **Era rule + TS GDI badge — SHIPPED AND SIGNED OFF 2026-08-30 ("all passes",
   `7436704f`..`e119fa66`).** TS units exit only TS factories and vice versa
   (`Who_Can_Build_Me`; RA/TD were already door-strict via Owner-vs-ActLike);
   power/refinery/repair cross-satisfy across all three eras; radar/tech stay
   faction identity. TS tree = fifth badge faction (bit 0x10, digit 'G'), emblem
   `scripts/tab_emblems/tsgdi.png` (Luke's weathered TS disc); Nod disc comes
   with the Nod faction. ⚠ `cameo_variants_build.py` wipes hand entries inside
   its block: TS `_G` entries live in their own appended XML block.
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
27. **War factory descale to normal size (Luke, 2026-08-13).** The Mk. II
    now arrives by bay, so the 08-07 enlargement can come back down — see
    the hangar-resize table: **fit_w 416 is the floor (below ~416 the
    TSAPC stops fitting through the door); TD-exact width 395 would break
    the APC.** ⚠ Moves together with: the exit point (the y=42 two-pixel
    window re-derives from the new hangar span), the sandwich layer cut,
    the sort band (must still reach the new south edge), and canvas+stub together.

**Roster remainder (the plan below):**
19. Component towers TSVULC/TSCSAM/TSROCK — turreted TDGTWR pattern, NOT the
    static recipe (GTCTWR_B/_C/_D are 48-canvas TURRET rotation frames).
20. Infantry TSE1/TSE2/TSGHOST (td-infantry-port-recipe adapted).
21. Orcas TSORCA/TSORCAB (RA helipad rearm mechanics).
22. TS audio wave (dormant-sample recipe; see 17).
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
