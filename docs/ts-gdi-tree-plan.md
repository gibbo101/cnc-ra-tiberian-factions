# TS GDI tree

**Status:** Reference; every TS GDI entity listed here is on main and shipped in 5.0.0.
**Open:** the queue at the end.

What is built, how each piece was ported, and the traps that cost time. The faction itself (lobby
slot, crest, EVA, voices) is `ts-gdi-faction.md`. Art rules live in the `ts-to-ra-hd-art` and
`unit-art-placement` skills, launcher render rules in `launcher-render-contracts.md`, and the
Firestorm, EMP and subterranean arcs in `firestorm-design.md`, `emp-cannon-design.md` and
`subterranean-design.md`.

---

## How the tree is gated

- **The construction yard grants the tech tree, never the picked faction.**
  `HouseClass::Yard_Factions()` is the single source the ownership gates read, for buildings,
  units and production alike. A house holding a TS yard, built or captured, builds the TS tree.
- **Era door rule:** TS units exit only TS factories and vice versa (`Who_Can_Build_Me`). Power,
  refinery and repair satisfy prerequisites across all three eras; radar and the tech centre stay
  faction identity.
- **Every TS type ships a `Prerequisite=` chain from TSFACT,** and every new prerequisite token
  needs its `Can_Build` remap `continue`, or the type is silently unbuildable.
- **The `TS` IniName prefix dodges the TD building HP doubling,** which keys on a `TD` prefix
  (`BuildingTypeClass::Read_INI`).
- **TS cameos carry the TS badge** (bit 0x10, digit `G`) when a category is producible from two
  or more yards. `TF_Apply_Cameo_Badge` always appends `_<hex>` to the sidebar AssetName, so a
  TS-tree type (`TF_Is_TS_Tree_Type`) requests `RA_<IniName>_0`: every buildable needs that
  variant in `RABUILDABLES.XML`, not only its base entry. `cameo_variants_build.py` rewrites its
  block, so TS `_G` entries sit in their own appended block.
- **Stats are TS's own** (TS `RULES.INI`, OpenTS for behaviour), a generation ahead of RA and TD.
  A roster balance pass is a decision in `todo.md`.

## Roster

Live values from `CCDATA/rules.ini`. TL −1 means not buildable: deploy-only, crate-only, a
superweapon payload, or dormant.

**Base buildings**

| Ours | TS | TL | Cost | Str | Prereq | Notes |
|---|---|---|---|---|---|---|
| TSFACT | GACNST | −1 | 2500 | 1000 | (TSMCV deploy) | 3x2 |
| TSPOWR | GAPOWR | 1 | 300 | 750 | TSFACT | south-row footprint |
| TSTURB | GAPOWRUP | 7 | 100 | 100 | TSPOWR | power turbine plug |
| TSPROC | PROC | 1 | 2000 | 900 | TSFACT, TSPOWR | 4x3, free TSHARV |
| TSSILO | GASILO | 1 | 150 | 300 | TSPROC | |
| TSPILE | GAPILE | 1 | 300 | 800 | TSFACT, TSPOWR | barracks |
| TSWEAP | GAWEAP | 2 | 2000 | 1000 | TSPROC, TSPILE | 4x3, the sandwich |
| TSRADR | GARADR | 3 | 1000 | 1000 | TSPROC | south-row footprint |
| TSHPAD | GAHPAD | 5 | 500 | 600 | TSRADR | no free aircraft |
| TSTECH | GATECH | 6 | 1500 | 500 | TSWEAP, TSRADR | |
| TSDEPT | GADEPT | 7 | 1200 | 1100 | TSWEAP | service depot |
| TSDROP | GADROP (cut from TS) | 9 | 2000 | 800 | TSRADR, TSTECH | Dropship Bay, 3x2 |
| TSPLUG | GAPLUG | 10 | 1000 | 1000 | TSPROC, TSTECH | Upgrade Center |
| TSPION / TSPODS / TSSEEK | plugs | 10 | 1500 / 1000 / 1000 | 100 | TSPLUG | Ion Cannon Uplink, Drop Pod Node, Seeker Control |
| TSPULS | | 6 | 1000 | 500 | TSRADR | EMP Cannon (`emp-cannon-design.md`) |
| TSFGEN / TSFSDF | GAFIRE / GAFSDF | 9 | 2000 / 250 | 800 / 200 | TSTECH / TSFGEN | Firestorm (`firestorm-design.md`) |

**Defences and walls**

| Ours | TL | Cost | Str | Prereq | Notes |
|---|---|---|---|---|---|
| TSCTWR | 2 | 200 | 500 | TSPILE | bare component tower |
| TSVULC / TSCSAM / TSROCK | 2 / 5 / 9 | 150 / 300 / 600 | 500 | TSCTWR + TSPILE / TSRADR / TSPILE | the plug is the armed tower type |
| TSWALL | 6 | 50 | 1 | TSPILE | concrete wall |
| TSGATEH / TSGATEV | 6 | 250 | 350 | TSPILE | gates |
| TSNWALL, TSNGATEH / V | −1 | 50 / 250 | 1 / 350 | TSPILE | TS Nod pieces, dormant |

**Vehicles**

| Ours | TS | TL | Cost | Str | Prereq | Notes |
|---|---|---|---|---|---|---|
| TSMCV | MCV | 10 | 2500 | 1000 | TSWEAP, TSTECH | deploys TSFACT |
| TSHARV | HARV | 1 | 1400 | 1000 | TSWEAP, TSPROC | `Tracked=yes` |
| TSSMEC | SMECH | 2 | 500 | 175 | TSWEAP | Wolverine |
| TSTITN | MMCH | 3 | 800 | 400 | TSWEAP | Titan |
| TSLIMP | | 3 | 550 | 100 | TSWEAP, TSRADR | Limpet Drone (deploys TSDLIMP) |
| TSAPC | APC | 6 | 800 | 200 | TSWEAP, TSPILE | `SPEED_AMPHIBIOUS` |
| TSJUGG | | 6 | 950 | 350 | TSWEAP, TSRADR | Juggernaut, deploy-to-fire |
| TSMEMP | | 6 | 1000 | 800 | TSWEAP, TSPULS | Mobile EMP |
| TSLPST | | 6 | 950 | 600 | TSWEAP, TSRADR | Mobile Sensor Array (deploys TSDPSA) |
| TSHVR | HVR | 7 | 900 | 230 | TSWEAP, TSRADR | Hover MLRS |
| TSSONIC | SONIC | 9 | 1300 | 500 | TSWEAP, TSTECH | Disruptor |
| TS4TNK | 4TNK | 9 | 1700 | 600 | TSWEAP, TSTECH | Mammoth Mk. I |
| TSHMEC | HMEC | 10 | 3000 | 800 | TSDROP, TSTECH | Mammoth Mk. II, bay-delivered |
| TSMDIV | | 10 | 2800 | — | TSDROP, TSTECH | Mech Division token: 3 Titans + 2 Wolverines |
| TSMWAR | | 10 | 1800 | 800 | TSWEAP, TSPLUG | Mobile War Factory (deploys TSDWEAP) |
| TSSUBTANK / TSSAPC | | −1 | 750 / 800 | 300 / 175 | | Devil's Tongue, Subterranean APC: crate finds |
| TSHUNT | | −1 | | 500 | | Hunter Seeker, the Seeker Control's payload |

**Infantry and aircraft**

| Ours | TS | TL | Cost | Str | Prereq |
|---|---|---|---|---|---|
| TSE1 | E1 | 1 | 120 | 125 | TSPILE |
| TSE2 | E2 | 2 | 200 | 150 | TSPILE |
| TSENGINEER | ENGINEER | 2 | 500 | 100 | TSPILE |
| TSMEDIC | MEDIC | 4 | 600 | 125 | TSPILE |
| TSJUMPJET | JUMPJET | 6 | 600 | 120 | TSPILE, TSRADR |
| TSGHOST | GHOST | 10 | 1750 | 200 | TSPILE, TSTECH |
| TSORCA | ORCA | 5 | 1000 | 200 | TSHPAD |
| TSORCAB | ORCAB | 8 | 1600 | 260 | TSHPAD, TSTECH |
| TSCARRY | TRNSPORT | 9 | 750 | 175 | TSHPAD, TSDEPT |

---

## Buildings

### Footprints and boxes

- **The launcher centres a building's selection box on its BSIZE plot** and takes only
  DimensionX/Y from the DLL (contract 7 in `launcher-render-contracts.md`). A box that reads wrong
  means the plot is wrong for the art. TSFACT and TSDROP went from 3x3 to 3x2 for this: the empty
  top row held their boxes off the art.
- **TSPOWR and TSRADR use a south-row footprint** (the Tesla/Obelisk `List22_0011` pattern): the
  ghost is 2x2 including the bib, units walk behind the tower, and a full 2x2 placement list keeps
  the ghost on the cursor (the launcher anchors the cursor on the BSIZE origin).
- **Damage states use frame 1 (LIGHT)** across the tree; the bay keeps its weathered heavy art.
- **Aprons draw under everything:** the renderer derives them from the owning building's
  footprint (the `_aprons` table in `dllinterface.cpp`), not from map state. Ore and bibs draw
  over them, nothing erases them, and they vanish with the building.
- **`Target_Coord` anchors TSPROC (the dock-lane gap) and the tall towers (the art-spill row) to
  occupied cells,** or the Mk. II's railgun sweep could not damage them.

### Walls and component towers

- A TS yard builds its own concrete wall and gates (TSWALL, TSGATEH/V) and is also granted RA's
  sandbags (`TF_Is_TS_Yard_Wall`); every wall placement line-fills (`house.cpp`).
- **Component towers are standalone defences:** a wall run stops at one rather than binding into
  it, a tower can't be placed on a wall segment, and wall arms end flush on the cell boundary.
- **The plug is the armed tower type.** Placing TSVULC, TSCSAM or TSROCK replaces the bare TSCTWR
  in place, keeps its health ratio and installs rather than builds; selling refunds both. Weapons
  are TS verbatim (`[TSVulcanTower]`/`[TSSA]`, `[TSRPGTower]`/`[TSRPG]`, `[TSRedEye2]`/`[TSSAMWH]`).
  The AI builds them as a two-step (`TF_AI_Tower_Step`: a bare tower, then the plug, counting plugs
  in production against bare towers; `TF_Plug_Host`).
- **The tower is TS's own sprite; the turrets are TS's `GTCTWR_B/_C/_D`,** composited by
  `scripts/ts_pack_towers.py`. Walls come from `scripts/ts_pack_walls.py` (16 joins x 3 damage).
- Traps: each turret set rotates about its own pivot (`_B` 23.08,13.69 / `_C` 23.99,11.37 / `_D`
  24.03,11.12); turret scale is about 0.75 of the body width (measured in TS); `GTCTWRMK`'s tail
  frames are debris cels, not build stages; the SAM's odd pixels are TS's own art, not ours to
  repaint.

### War factory (TSWEAP)

**The sandwich:** the base carries the bay interior and the overlay (`TSWEAP2`) the whole hangar,
RA's and TD's scheme (`building.cpp` states the convention), so a vehicle is hidden behind the shut
door and revealed as it opens. GTWEAP frames 0/1/2 are healthy / LIGHT / HEAVY; the door is its own
SHP (`DoorAnim=GAWEAP_D`, `DoorStages=9`, `UnderDoorAnim=GAWEAP_1`), and `GTWEAP_D` frames 9-17 are
magenta placeholders.

- **Exit seats:** `TSWEAP_SEAT_MOUTH_MECH` for walkers and `TSWEAP_SEAT_MOUTH` for tracked and
  wheeled hulls (`building.cpp`, `bdata.cpp`), dialled by eye one build per nudge; do not
  re-derive them. One shared seat put hulls too deep, because a walker's sprite centre sits well
  above its feet.
- **Exit rails:** `Force_Track` plays a generated straight rail per type (Track19 for the default
  seat, Track20 for the Titan) ending on the handover cell, plot cell (3,2).
  `scripts/wf_spawn_preview.py` reads the spawn markers from the Aseprite sheet and writes
  `tsweap_exit_track{,_titan}.inc` and `tsweap_exit_seats.inc`, used by both `bdata.cpp` and
  `building.cpp`; it errors on any seat drift.
- **Exit clamp:** the factory stamps `TsExitSortClamp` (its Sort_Y + 64 leptons, under the overlay's
  key) on the unit when it assigns the rail, and the export clamps the unit's base draw while
  `On_TS_Exit_Track()`, so the hangar clips it for the whole glide. The Titan's rail releases 32
  leptons south of the bay mouth (`On_TS_Titan_Exit_Track()`); wide hulls keep the full-rail clamp.
- **Layers above the door:** `TSWEAP2L`, the overlay's bottom 62 canvas rows (ramp lip, frame feet,
  shutter bottoms), sorts one notch under the exit clamp so emerging units pass over the floor
  furniture; `TSWEAPLT`, the lamps, holds only the pixels that change against idle phase 0 (a full
  face per phase double-blended the seam over exiting units) and ping-pongs with the body (14
  frames: 0-7 then 6-1). The sort band must reach the building's southern edge: `dllinterface.cpp`
  biases `TSWEAP2` 384 leptons south, keyed on AssetName.
- **Four coupled constraints** for any resize, solved on paper before one build: containment (art
  at least as tall as the tallest exiting unit; the Titan is 52.2 classic px), the box (centred on
  the plot), ghost honesty (the ghost covers every cell the ground art touches; hard-clipping the
  pad looks wrong), and spawning inside (units spawn hidden and drive out; materialising at the
  open door was rejected).
- The Mobile War Factory deploys into `STRUCT_TSDWEAP`, a TS war factory to the code
  (`emp-cannon-design.md`).

### Refinery (TSPROC) and its dock

- **Footprint 4x3:** two building rows plus the apron row; tall art overhangs the passable row north
  of the plot. The centre cell (BSIZE_43 row 1, col 2) is the bay-mouth pad, so every
  `Center_Coord`-keyed dock geometry indexes itself. TSPROC's pad is the apron-row cell
  `Coord + 3*MAP_CELL_W + 2`.
- **Dock geometry, dialled live and final:** line-up on the SE plate cell centre, a dead-straight
  reverse at facing 92 (TSHARV) / 94 (TDHARV), park at pad + (40,74) / pad + (3,23), a settling
  pivot to true SE, and a motionless unload. Do not re-derive these from reference PNGs. The
  roll-off seats ride `ROLL_OFF_DOCK_SEAT` (`DriveClass::Track21`), one static table shared with the
  war factory exit and the depot (`todo.md`). Pairings and dock time:
  `harvester-docking-rework-plan.md`.
- **The refinery radio protocol gated on literal `STRUCT_REFINERY || STRUCT_TDPROC` in about 15
  sites;** all take TSPROC. Repair (`STRUCT_REPAIR || STRUCT_TDFIX`, ~17 sites) and radar
  (`STRUCT_RADAR || TDHQ || TDEYE`, 7 chains) needed the same audit.

**Aprons** (`SMUDGE_TSWEAPBB`, `SMUDGE_TSPROCBB`, 5 wide x 3 tall over each 4x3 plot):
- They draw as terrain: the TD-template ground entry (`IsOverlay`, `IsTheaterShape`,
  `Type=OVERLAY_V12`, `SHAPE_CENTER|SHAPE_WIN_REL|SHAPE_GHOST`). A theatre shape resolves from
  `RA_TERRAIN_<theatre>`, not `RA_STRUCTURES`, and a mod tileset replaces the base file, so the mod
  ships a full `RA_TERRAIN_SNOW.XML`.
- `Is_Clear_To_Build` refuses to build over any bib; aprons are exempt (`Is_TS_Apron_Cell` vetoes
  the plot and leaves the 5th column free, where the concrete tapers past the plot).
- **The hazard stripes are baked gold:** the launcher house-remaps building sprites, never ground
  art.
- **A third apron moves five things together:** `SmudgeType` in `defines.h` and its class in
  `sdata.cpp`, the `Bib_And_Offset` branch in `bdata.cpp`, `Is_TS_Apron_Smudge` in `building.cpp`,
  `Is_TS_Apron_Cell`'s offset table, and `aprons` in `ts_pack_tree.py` (which fails the build if
  the art outgrows its grid).

### The Dropship Bay (TSDROP)

The TS Dropship (DSHP.VXL at TS's 6.4 px/voxel) descends vertically over the deck: a three-stage
machine in `BulletClass::AI` (descend and flare, 4 s dwell, climb out), with no map motion, so its
shadow sits on the pad and grows (shapes 1-3, pre-scaled silhouettes picked by Height). TS's
DROPDWN1 and DROPUP1 play at touchdown and liftoff. The Mk. II walks out from under the hull to the
bay's rally point (`Rally_Unit`; the bay is a real factory) or two rows out. The landing point is
the deck's visual centre, 160 leptons north of the plot centre.

- **Mech Division** (`UNIT_TSMDIV`) is a token the pod expands into 3 Titans + 2 Wolverines, single
  file every 9 frames. **The Mk. II field cap** (`TF_MK2_CAP` in `house.cpp`) is heap-counted:
  the CSII quantity fold aliases mod-unit `UQuantity` slots.
- **The cooldown arms at pod launch, per house,** through one list (`TF_Is_Dropship_Delivered`:
  the factory binding, both order gates, the sidebar keep-alive and the countdown) and shows as a
  per-second baked countdown cameo, 5:00 to 0:01 (`scripts/ts_mk2_cooldown_cameos.py`, an AssetName
  swap). At the cap the cameo is `BuildIcon_TSHMEC_LK` (dimmed, red X), which outranks the
  countdown, and both sidebar click handlers ask `TF_Delivery_Order_Refused` before speaking, so a
  refused click says "Cannot comply".
- **`TFDropBayTimer` must be initialised in the HouseClass constructor;** uninitialised it reads as
  a live cooldown and looks like a broken binding.
- **The one-bay cap counts standing bays** (`Has_Building_Active(STRUCT_TSDROP)`), never
  `Get_Quantity`, which counts from production start.
- **The sidebar must never evict an entry with `Factory != -1`:** placement and cancel resolve
  through the entry, so evicting a mid-production one strands `BuildingFactory` and locks the
  sidebar. A trunk merge dropped this guard once; after any merge, `git log -S` the known one-line
  guards.
- **Deliberately not a helipad:** outside `Is_Helipad` (a free helicopter on build, a general
  rearm target) and `STRUCTF_HELIPAD` (prerequisites). Its rim takes house colour; the emblem has
  no remap pixels and stays GDI gold.
- **Bay WAVs must be MS-ADPCM:** plain PCM crashed ClientG on takeoff (a divide by zero in its ADPCM
  block maths).
- Render recipe: `vxl_render.py DSHP.VXL --frames 1 --yaw0 180 --px-per-voxel 6.4 --team-green
  255,204,51 --elev 32 --canvas 656`, then `ts_pack_dropship.py`. The canvas stays 656 so the classic
  stub (123) and drawn scale never move.

---

## Units

**Voxel lighting:** `vxl_render.py --shade ts` (the default) ports TS's lighting: a length-1.5
light vector, n·L·16 truncated to a table index, and fixed palette scales from 0.62 (facing away)
through 1.26 (neutral) to 1.70 (fully lit), from OpenTS `voxlib.cpp` and the shipped VOXELS.VPL. The
old shading was 1.6-1.8x too dark. Team colour needs no extra lift in TS mode, and shaded RGB clips
at 255. If units ever read too bright, the lever is one multiplier on `TS_VPL_SCALE`.

**Shadows:** EA's throw is a fixed pixel distance, not a fraction of the sprite: `EA_DX = 2`,
`EA_DY = 6`, alpha 191, for every unit (`scripts/ts_reshadow.py`). Never express it as a fraction:
our TS sprites run to 301 px wide against RA's 228, and a fraction gave the Mk. II a 41 px overhang.
The Hover MLRS keeps its own float.

**Hover MLRS (TSHVR).**
- The rack seat is two-part (`Hover_Rack_Seat(hull, rack)` in `udata.cpp`). Facing32 resting
  diagonals read seat index 3/13/19/29, never 4/12/20/28 (EA's 3D Studio 45° compensation).
- A draw-side slewed hull facing stops the mount jumping as RA pathing flicks the heading each
  cell; the rack swings 3 directions a tick so sweeps read as rotation; the seat cancels each pod
  frame's centroid offset so stationary spins hold within ~1 px.
- **The 48x48 classic stub is load-bearing:** the eye-dialled seat table was tuned against it.

**Mammoth Mk. II (TSHMEC) railgun.** TS has no railgun art: `[MechRailgun]` drives
`LargeRailgunSys`, a particle system with no `Image=`. Ours is TS's helix maths (the `IsRailgun`
branch in `techno.cpp`): 19 sparks a cell, radius 15 leptons, .03 rad per lepton, ±15 lepton jitter,
`ANIM_RAILFX` sparks from `scripts/ts_gen_railfx.py` fading blue (25,70,205) to grey over ~1 s. It
damages units within 128 leptons of the line, any building whose cell it crosses, and the aimed
target always. The anim heap floor is 1024 (a max-range shot lays ~150 sparks). The muzzle flash is
TS's `gunfire.shp` (`ANIM_TS_GUNFIRE`, `Anim=TSGUNFIRE`). The coil lives 1.2 s; TS locks the gun
until its ~2.4 s coil dies, and ours keeps the 1.5 s ROF instead.

**Disruptor (TSSONIC).** TS's wave is a screen-space pixel displacement (OpenTS `wave.cpp`), which
the launcher can't do, and TS ships no sonic-wave art.
- **The band is a chain of discs** (a spawned anim draws unrotated, so a band sprite would line up
  at one angle only), `SHAPE_FADING` plus a stage-keyed scale throb (12%, period 6,
  `TF_SONIC_*_DEFAULT` in `function.h`), 25 stages x 5 ticks, discs 32 leptons apart.
- **The band is the weapon:** per-cell anchor discs (`AnimClass::SonicDamage`) hit every techno in
  their cell on five stages within ~1 s of the crest; the firer is exempt (`SonicFirer`), and
  Disruptors are immune to sonic damage.
- **Firing behaviour is OpenTS's `WaveClass` tether:** each disc keeps its place on the live
  muzzle-to-target line (`SonicT`, `SonicTether`); a broken tether (firer dead, `TarCom` changed,
  or the target beyond `SONIC_TETHER_RANGE`, 2172 leptons) retracts the band from the tank end and
  stops its damage; `SonicBandEnd` holds the next shot until the band is gone.
- `PrimaryOffset` 0x50 roots the band at the horn; `NoMovingFire=yes`, as TS's `[SONIC]` requires.
  The turret renders came from the opposite camera side, so the packer maps
  `turret[j] = render[(16-j)%32]`.

**Amphibious APC (TSAPC).** TS's APC is the drive locomotor with `SpeedType=Amphibious`: ours is
`SPEED_AMPHIBIOUS` (rules `Amphibious=yes`, its own land column: Clear 80, Rough 40, Road 100,
Water 80, Ore 50, Beach 60, River 80, Rock and Wall 0), sharing `MZONE_HOVER`. On water it draws
TS's water hull `apcw.vxl` (frames 32-63, `scripts/ts_pack_tsapc_water.py`). It skips RA's APC door
frames, which it has no art for.

**Wolverine (TSSMEC).** TS's firing animation is a sprite block (art.ini `FiringFrames=4`, SMECH
104-135); `[AssaultCannon]` has no `Anim=`. The canopy dot is TS's palette ramp tail, tamed with
`ts_shp.py --pal-override`.

**Ghost Stalker and Juggernaut fire points** are generated per facing from the art:
`redalert/tsghost_muzzle.h` by `scripts/ts_ghost_fire_points.py` (off the TS fire frames' own muzzle
flash), `redalert/tsjugg_muzzle.h` off the packed barrels.

---

## Sign-off ledger

A unit here is done: no open art, geometry or behaviour work.

| Unit | Notes |
|---|---|
| Hover MLRS | 32° render, two-part rack seat, Facing32 resting indices, centroid-pinned spin |
| Mammoth Mk. II | railgun from TS's own particle numbers; bay-delivered, capped |
| Titan | signed off once the fixed 6 px shadow throw replaced the width fraction |
| Wolverine | cameo, TS firing animation, TSGUN4, canopy dot |
| TS MCV | 32° render; `Speed=5` to match the TD MCV family |
| Disruptor | final band (no pulse), WaveClass firing behaviour, horn-rooted muzzle |
| Amphibious APC | unload fix, water hull, `SPEED_AMPHIBIOUS` |
| TS Harvester | docks at the TS, TD and RA refineries; war factory door seat |

## Dead ends — do not re-chase

- **The TS attach-dock** (harvester limbo'd and baked into the refinery's frames): a baked duplicate
  is a permanent sync surface. Deleted.
- `BACKUP_INTO_REFINERY` at any facing but SW snaps (teleports); a real SE reverse needs its own
  mirrored track entry. Detour approach cells oscillate (the RADIO_DOCKING loop re-orders the truck
  to its MOVE_HERE cell every tick). Any post-turn coordinate seat, a single nudge or a 1 px/tick
  creep, reads as a slide; trucks park at cell centre.
- **Sort-based hiding at TSPROC:** even a half hide reads as full, because the bay mouth's dark art
  covers the whole truck. The truck backs up to the entrance and stays fully visible.
- **Apron rectangle-clip to the plot:** slices the stripes.
- **Selection box probes:** `CenterCoordX`, `CenterCoordY`, dims anchoring, `CellY`, a doctored
  OccupyList and `PositionY` (which moved the sprite) were all ignored or wrong; art-sized dims make
  the brackets float. Fix the plot instead. A 4x5 refinery height trick was built, played and
  reverted.
- **Hover MLRS rack shapes rejected:** a hull-locked draw, an instant snap, a rack-keyed seat, a raw
  two-part seat. At the 32° camera: canvas-centred pods (they flew), content-centred pods (they
  towered: cos32 draws heights 1.44x cos54), a squashed rack, and a 54-pods-on-32-hull hybrid.
- **Disruptor ripple, four mechanisms falsified:** a lit-window sprite pulse (the TS patch is 2-4%
  of the band, smaller than a disc), a rotated thin bar (drew unrotated in play), TS's exact
  amplitude ladder as a pale overlay (it can't read like TS's multiplicative tint), and hijacking
  the chrono vortex (the launcher ignores its width and height and draws the whole whirlpool).
  Launcher levers on the discs: `Cloak` on an anim or a unit-typed disc is ignored,
  `SHAPE_PREDATOR` makes it invisible, `SHAPE_GHOST` does nothing, `FlashingFlags` strobes, and
  `Rotation` is honoured but clipped to the unrotated frame. Overlapping discs can't give a hard
  edge or keep a mottle.
- **A tower with N/E/S/W connectors:** voxel splats, two procedural Blender towers, an image-model
  redraw and a third-party STL were all rejected; the tower is TS's own sprite. Running TRELLIS
  locally needs 24 GB of VRAM (this box has 12).
- **The Hover MLRS still shadow** (a shadow-only draw under the bobbing hull): the art half,
  `scripts/ts_hover_split_shadow.py`, is parked; reviving it also needs a `Draw_It` reorder and a
  96-frame classic stub.

## Engine facts, traps, lessons

**Engine:**
- **A fuse arms with at most 0xFF frames of flight** (`fuse.cpp Arm_Fuse`): a projectile slower
  than its distance budget "arrives" mid-flight.
- **A unit set down on building-occupied cells can't be rescued:** it renders under the building and
  can't path off. Set cargo down outside the occupy list.
- **`Begin_Production` never consults `Can_Build`:** a visible cameo is orderable, so a cap or
  cooldown that keeps its cameo must refuse inside `Begin_Production`.
- **`CNCSidebarEntryStruct::Busy` draws nothing.** Show unavailability with `Constructing` +
  `Progress`, or an AssetName swap.
- **Any divert that bypasses `MISSION_CONSTRUCTION` must free the builder itself** and run
  `Grand_Opening`: the plug install skipped it, the yard stayed in radio contact, and every later
  placement built then cancelled (`tf_plug_swap` in `building.cpp`).
- **Every literal `STRUCT_X || Y` role chain must include new TS types;** a missed chain shows as a
  behaviour bug, not a crash.
- **Heap registration must be strictly enum-ordered** (slot index = Type); append at the marked
  `Init_Heap` tail. Out of order once gave AI MCVs that deployed helipads.
- **Old saves die on any class growth:** `saveload.cpp` derives the save version from `sizeof()` of
  every game class, and a mismatched save crashes rather than refusing.
- **`Set_Stage(n)` then the first `Graphic_Logic` advances to n+1** before stage n is drawn, so a
  hit keyed to stage n never fires for an anim started at n.
- **Units reach the object export with a NULL `shape_file_name`;** per-unit render biases key on the
  final `AssetName`.
- `Find_Exit_Cell` dereferences its argument; guard it in any state that runs after radio contact
  drops.
- **A $1 `PurchasePrice` fails EA's free-harvester gate** (it compares against `Raw_Cost`); the rich
  start lever is `tf_cheap.flag` (1,000,000 credits at skirmish start).
- **Grep a new vehicle's rules for `Tracked=`** before its first drive: the wheels-vs-tracks terrain
  table bit three times.
- Where a helipad-built aircraft actually exits is unknown: `Exit_Object`'s `RTTI_AIRCRAFT` branch
  never runs and `HouseClass::Place_Object` is never reached (`FIXIT_HELI_LANDING` is off), yet
  `sidebarglyphx.cpp` queues `EventClass::PLACE` for aircraft.

**TS art conventions:**
- **Every TS anim SHP packs healthy frames then damaged frames** in its usable window; full-cycle
  exceptions exist (GTCNST_B's rotating light, NTREFN_B's plume), so check each.
- **Base frames:** 0 healthy, 1 LIGHT, 2 HEAVY, 3-5 rubble. Frame 1 is never a free variant.
- **Buildup SHPs carry empty and fragment frames past the real run,** which render as the purple
  placeholder; the packer cuts them. Donor `Init_Anim` counts apply only when the building has no
  MAKE stub of its own.
- **The launcher maps the HD canvas onto the classic stub box centred on the BSIZE box centre;**
  stub height beyond the box splits into equal halos above and below, which is how apron and
  overhang rows work.
- **Canvas and classic stub move together:** `ts_pack_tree.py` writes `scripts/ts_stub_dims.json`
  and `build_tfassets.sh` refuses a stub that disagrees. A partial pack run truncates that file to
  the packed subset; a full run drops the entries other packers own (towers, walls, the Hunter
  Seeker), reorders `RA_STRUCTURES.XML` and rewrites every ZIP's timestamps. Restore from HEAD
  unless a frame count changed, and compare ZIP member bytes, not file hashes.
- **An overlay's shape pointer supplies its render box,** so every overlay needs its own stub in
  TFASSETS.MIX.
- **Voxel renders start east and run counter-clockwise;** RA frame 0 is north, so the vehicle
  packers rotate by 8. Aircraft renders already start north (no rotation).
- Verify packed art by the meta crop, not the TGA bbox (packed TGAs are content-cropped), and leave
  real canvas headroom.
- **Hand-made cameos in `resources/custom-cameos/` win:** both packers prefer them, and
  `scripts/apply_custom_cameos.py` re-asserts every override; run it after any SRGB-touching packer
  and before `ts_mk2_cooldown_cameos.py`.
- **Anything inserted after the last ObjectTypeClass in `RABUILDABLES.XML` lands inside the
  countdown generator's block,** and its next run eats it; insert before the BEGIN marker.
- **Two Blender traps:** a world made through the API has a near-black default colour, so
  everything the sun misses renders black; bevelling a box with non-uniform object scale makes
  degenerate geometry that also renders black.

**Pipeline:**
- `scripts/ts_rebuild_art.sh` regenerates `$TS_ART_DIR` from the Steam TS install. TS building
  cameos are in SIDEC01.MIX (GDI), not CONQUER.MIX. The chain is TIBSUN.MIX → `tools/ts_extract.py`
  → `ts_shp.py`.
- Diagnostics land in `MOD_DEBUG_TSUNITS.txt` / `MOD_DEBUG_CANBUILD.txt`, sometimes under
  `pfx/drive_c/users/steamuser/` instead of `Documents/CnCRemastered/`; check both.
- The gitignored UI atlas differs per checkout; main's is canonical (`ui-atlas-modding.md`).

**Method:**
- **Measure which art owns the pixels before changing a render flag:** the occluder was the bay
  door, not the apron, and four rounds were lost.
- **Occlusion-biased measurement:** measuring a docked composite by visible stripe centroid doubles
  the apparent depth; measure against unoccluded landmarks.
- **Ship a positive control with any negative result.**
- **Re-measure the source on a rejected round, and restore the art to the pre-pass checkpoint**
  before re-applying, or the rejected round's fringe is baked into the next.
- **The placement rule:** art matches the build grid; grow the grid to fit big art; a full-width RA
  slab spans the building; no baked pads.

**TS infantry, Firestorm units and aircraft:**
- **The launcher places the selection box and health bar from the first shape an object draws,
  plus its exported centre.** The export Type and Altitude do nothing for them. An airborne jumpjet
  draws its body before its shadow and lifts `CenterCoordY` by Height.
- **Engine checks that assume only aircraft fly**, each exempting jumpjets now: `MissionClass::AI`
  returns early for infantry, units and vessels with Height > 0, so no mission runs in flight;
  `TechnoClass`'s target maintenance (and the attack-move check) drops a non-aircraft's target that
  is out of range in another zone; a move click is pulled back into the unit's own zone
  (`Nearby_Location`); the SAM state machines take only aircraft (a jumpjet goes through the
  airborne test at `building.cpp:191`).
- **`Good_Fire_Location`'s ring search starts a cell inside weapon range,** so it never runs for a
  weapon under about 3 cells (the Orca Bomber's 1.5-cell bomb). Short weapons fly straight over
  the target.
- **RA's `::Distance()` is an approximation.** An arc flown on it landed about 290 leptons long
  (Juggernaut); ballistic shots use the true distance.
- **TS barrel pitch 64 is level;** TS rests barrels level and raises them only while aiming.
- **The landing-zone rewrite clears the Carryall's NavCom,** so the vehicle it was sent for is
  remembered separately.
- **A new barracks needs its own exit pixel and exit list.** TSPILE reused the RA tent's (24,47) on
  a 2x1 plot and spawned infantry a cell below the door (`ExitTsPile`).
- **Decode TS cameos with `--no-remap`:** the house-colour remap turns palette 16-31 green.
- **`ts_mk2_cooldown_cameos.py` rewrites its whole block** and wipes any hand-written entry inside
  it; keep hand entries outside.
- **Firestorm assets are in `expand01.mix`:** SHPs in the inner `ECACHE01.MIX`, AUDs in
  `SOUNDS01.MIX`, voxels at the top level.
- **Railgun colours are TS's own:** the Ghost Stalker's `SmallRailgunSys` is orange (255,128,0), the
  Mk. II's `LargeRailgunSys` blue (25,20,255).

---

## The Stealth Recipe — the per-building port

TS-authentic art with build-up animations, damaged states and TS sidebar icons, sized to match the
TD counterpart. Baseline: the Nod Stealth Generator. Per building:

1. **Extract** (temperate `T` names): base `GT<X>.SHP`, active anims `GT<X>_A/_B/_C.SHP` (art.ini
   `ActiveAnim*=`; damaged variants are usually the second half of the same SHP, or empty, as
   GAFIRE's, in which case the damaged run is the damaged base with the anims stopped). An anim's
   `Rate=` is frames per minute (OpenTS `animtype.cpp`: delay = TICKS_PER_MINUTE / Rate), so a
   higher Rate is faster. Buildup `GT<X>MK.SHP` (ISOTEMP.MIX); cameo per art.ini `Cameo=`
   (SIDEC01.MIX, CAMEO.PAL). Bases and anims decode with UNITTEM.PAL.
2. **Compose:** N healthy frames = healthy base + anim frame i (shorter anims loop), then N damaged
   frames = damaged base + the anim's damaged half. Ship real buildup frames only, resampled to the
   donor's construction-anim count.
3. **One affine for every frame** of a building (base, anims, MK), content-anchored: scale so the
   healthy composite matches the TD counterpart's proportions, centred. Canvas = classic donor dims
   x 5.33. Never full-canvas scale.
4. **Donor** (`_td_bdonors` in `bdata.cpp`, matching footprint and construction-anim count):
   TSPOWR → RA POWER, TSFACT → TDFACT, TSPILE → TDPYLE, TSPROC → TDPROC, TSWEAP → TDWEAP,
   TSRADR → TDHQ, TSHPAD → TDHPAD, TSTECH → TDEYE, TSDEPT → TDFIX, TSSILO → TDSILO; towers →
   TDGTWR / TDSAM / TDATWR-class 1x1s.
5. **Engine:** an IniName no other tileset uses (grep `RA_*.XML` and TFASSETS: `TSFIRE` was already
   the fire-stream particle's), the enum appended inside the TS block (move
   `STRUCT_TS_TREE_LAST`), the heap `new` at the marked `Init_Heap` tail, the `_td_bdonors` entry,
   the `TF_Building_Scan_Bit` shadow, role tests, and an `_anims[]` entry
   `{STRUCT_TSX, BSTATE_IDLE, 0, N, 3}` (damaged run = shapes N..2N-1).
6. **Data:** a rules.ini section (TS stats, tree prereqs), a `RABUILDABLES.XML` entry before the
   BEGIN marker, ModText rows, and a BuildIcon TGA from the TS cameo (NEAREST 8x, then LANCZOS to
   341x256), unless a hand-made cameo exists in `resources/custom-cameos/`.

---

## Open queue

1. **Mk. II cap to 3** (`TF_MK2_CAP`, one constant; `todo.md`).
2. **Dead code:** `tf_orbit.flag` (the old from-orbit probe, `aircraft.cpp`).
3. **`ts_pack_tree.py`'s blank-apron warning is stale:** aprons draw from building geometry, so a
   blank tile no longer stamps over a neighbour's bib; it is only a wasted entry.
4. **NTREFN_C** (Nod's refinery anim, a 144-canvas anim on a 192x168 building, needs offset
   compositing) is unported; it comes with TS Nod.
5. Component tower animations and weapon geometry (`todo.md`).
