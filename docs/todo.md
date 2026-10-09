# To do

**Status:** Tracker. Open work and the backlog.

Open work and the backlog, checked against main at the 5.0.0 release (2026-10-04). Bugs and
limitations live in `known-issues.md`. Finished work is deleted from here once its lessons are in
a topic doc; the full old file is `git show b6d3b52c:docs/todo.md`.

---

## Next version: first jobs

- **Fix the balance data bugs** (`known-issues.md`, "Balance data"), each with a play test:
  - the mod's `aftrmath.ini` overrides `[155mm] Range` (6 over the intended 8) and `[E3] Owner`
    (allies over allies,soviet): set the intended values there too, after deciding E3's owner;
  - `Inaccurate=` is dead (EA reads `Inaccuate`): turn projectile inaccuracy back on, through the
    key or a `// TF:` parser fix, and retune the artillery range if the scatter changes it.
- **Shrink the package.** The build is 1,137 MB unpacked, 772 MB zipped (5.0.0: 1,456 MB, zip
  1.0 GB), with each frame stored once, copied ZIPs shared at staging and cameos staged as RLE TGA
  (`docs/asset-packs.md`). Where the rest goes: 182 MB of sidebar cameos, the 177 MB UI atlas (same size as EA's),
  67 MB of movies, 51 MB of lobby thumbnails (same-size swaps for EA's), 43 MB CONFIG.MEG. Leads:
  `TSWEAP2.ZIP` (2.5 MB), the pre-rebuild war factory overlay, which the game never draws, can go
  once the map editor's factory overlay (`editor_manifest.py`) and the war-factory Aseprite scripts
  read the current layers; whether the launcher takes a DXT DDS for a loose cameo (an in-game check
  of every faction's sidebar).
  It grows from here: TS Nod (21 buildings and 19 units in the HD hand-offs) and the TS HD
  rebuilds. Restage a build folder clean (`stage_asset_packs.py --full`, as
  `package-for-workshop.sh` does) before measuring it.
- **Check in play: "Unable to comply, building in progress"** speaks in the picked side's voice
  (the era mailbox's ninth line), including after a faction switch between matches.
- **Light orange selection box on a limpeted unit.** TS draws a limpeted object's bracket from
  another frame set (OpenTS techno.cpp:1455). The launcher's box is `CNC_SELECT_BOX.TGA` (white,
  atlas 3027,4088 128x128), tinted as it is drawn, and no data lever reaches the tint. Route: find
  the tint in ClientG and patch it at the launcher's startup load, keyed on a field the DLL sets
  for limpeted objects (`launcher-vs-dll-ownership.md`, "Launcher-resident patches").
- **Decision: the TS roster balance pass.** Every TS unit ships TS's exact stats, and TS fights at
  a bigger scale: the Mk. II railgun and Hover MLRS reach 8 cells, the Disruptor and Titan 6,
  against an RA heavy tank at 4.75 and a TD medium at about 4. Range first, then damage, ROF, HP,
  cost, speed and the Devil's Tongue stream. Known deviation: the Mk. II AA tusks carry RA
  MammothTusk stats (7.5 range) instead of TS's 6.

- **Check: can a defeated house leave buildings standing?** A skirmish or LAN house is defeated when
  its scan bits are empty, and `TF_Building_Scan_Bit` gives most added types none (TS power, gates,
  towers, TD defences); that path calls `MPlayer_Defeated`, which destroys nothing. Not seen in play:
  confirm a house down to such buildings is declared defeated before choosing between blowing them
  up and counting them.

## Needs a LAN game with a second human

- **Firestorm against an enemy:** an enemy firing across a live wall has its shots eaten at the
  wall in sparks, instant-hit machine guns included; enemy units cannot path across a live
  section; enemy aircraft over a live section die; the field eating shots does not shorten it,
  damage landing on a section does.
- **Joiners' credit tick** (`known-issues.md`).

## Loose ends on shipped features

- **TS Service Depot seat:** the drive-on to the pad's centre catches only some approaches. When
  the HD depot's pad ring is centred on the middle cell, `TS_DEPOT_SEAT_EAST_PX`/`SOUTH_PX` go to
  0 and the drive-on rail comes out (`firestorm-design.md`).
- **Shared rail table:** `DriveClass::Track21` (ROLL_OFF_DOCK_SEAT) is one static table used by
  the war factory exit, the TS refinery dock and the depot. Two rails running at once make one
  unit follow the other's offsets and jump (it still ends on its own destination). Per-unit rail
  data would fix it.
- **Wall line-fill placement preview:** can the DLL see the cursor cell while a wall is placed?
  `INPUT_REQUEST_MOUSE_MOVE` returns early without legacy rendering.
- **EMP Cannon layer pops on** about a second after the build-up ends: it is gated on
  `BState != BSTATE_CONSTRUCTION` (`building.cpp`).
- **Devil's Tongue side-nozzle jet seats** are still the placeholder values in `udata.cpp`
  (`subterranean-design.md`).
- **TS infantry fire points:** the Ghost Stalker's beam starts at his chest (facing west it
  looks like his head). A table from TS's `PrimaryFireFLH` (100,0,100) projected per facing is
  ready and waits on the maintainer's OK, with the question of whether Light Infantry (80,0,85), Disc
  Thrower (60,0,100) and Jumpjet (100,0,120) get theirs too.
- **Jumpjet checks never made:** ground-only weapons refuse it; it bursts (S_BANG34) when shot
  down; its shadow.
- **TS GDI AI in play:** a TS GDI AI at Normal or Hard should build the Upgrade Center, the Ion
  Cannon Uplink, then Drop Pods or Seeker Control. Confirm with the `PROD start TSPLUG` /
  `TSPION` / `TSPODS` / `TSSEEK` lines in `MOD_DEBUG_AI.txt`.
- **Drop-pod targeting:** the AI aims its pods at the enemy's most valuable building
  (`Special_Weapon_AI`), which lands infantry on the strongest point of a base.
- **Component tower:** animations and weapon geometry for the Vulcan, RPG and SAM plugs. Confirm
  what is still wanted now the HD tower is in.
- **Mk. II cap:** `TF_MK2_CAP` is 1; it goes to 3 on the maintainer's word.
- **Code tidy:** the dead-code pass (needs calls first), the comments left inside the
  ts-buildings-hd branch's ranges, and phase 2: `code-tidy.md`. Also `defines.h:589` rounds
  `MAP_REGION_HEIGHT` with `REGION_WIDTH` (harmless while both are equal).

## Investigate before touching

- **The Nod SAM's missile flies at all:** `[TDNike]` `Speed=100` reads as light speed
  (`_Scale_To_256`), and `Unlimbo_TD` makes a visible light-speed missile immobile, yet play
  shows it flying and hitting. Look before changing any TD-port bullet speed.
- **The TD-port bullet path never damaged aircraft with `TSAAHeatSeeker`;** the cause was not
  found. Any other TD-port AA bullet (`BULLET_TDPATRIOT`) may share it.
- **The committed cameo-variant block is behind `cameo_variants_build.py`:** a re-run adds
  `RA_TSDPSA_0`, `RA_SG_TSFIRE_0` and `RA_SG_TSEMP_0`, reorders the block, and also emits doubled
  keys (`RA_C3MK3_0_0`, `RA_TSFGEN_0_0`) for pack entries that are already variants. Fix the
  generator's input before the next full re-run; new types are added by hand for now.

## UI polish

- **User Maps tiles:** the Workshop browser (TD's `UI_WORKSHOPMAP_BROWSE`) shows each tile under
  a light green title bar with white text. Darken the bar and give the title a green style, as in
  the lobbies (`lobby_art.py`, `fontlib_build.py`, `bui_lobby_build.py`; tile file
  `UI_WORKSHOPMAP_LISTBOX_ENTRY.BUI`).
- **Copyright line:** "©2020 Electronic Arts Inc." under the main menu is still red.
- **CAMPAIGNS page** (`campaigns-page.md`): Continue and Start over in the bottom bar; Start
  greyed on an empty tab; a New Game button with its own campaign-select screen; the TS Nod tab
  once TS Nod exists.
- **Spike: the intro freeze on the Deck.** About 4 s into any startup movie the launcher hashes
  every local custom map on its main thread (`[PGUGC::UGC::Recalculate_Values] SHA256`, about
  17 ms a map, 0.8 s on the Deck), after its Workshop database reply. No data setting moves it.
  Route: a launcher-resident patch that holds the reply, or the hashing, until the movie dialog
  closes. Test the Workshop map browser, custom-map lists and a LAN game afterwards.
- **Spike: smoke beside the intro from its first frame.** On screens that aren't 16:9 the bands
  beside the intro stay black until the main menu is revealed behind it (about 10 s), then switch
  to the menu's smoke. Every Bink movie plays on `UI_FULL_SCREEN_MOVIE_BINK_DIALOG.BUI`, whose
  `Background_Quad` is a plain black tint, and campaign movies keep black bars, so no data edit
  can do it. Route: an intro-only in-process patch that gives that background the menu's smoke
  and restores it before any other movie.
- **Crest label colour on the TD plate** (only if asked): the launcher's "GDI"/"Nod" text under
  the radar crest reads dark on grey. Probe: find the cached text-style record ClientG draws it
  from (the `radar-crest-ram-spike.md` method).

## Tiberian Sun

- **TS Nod, the sixth faction:** France as `HOUSEF_TSNOD`, `Faction9`, CABAL from `SPEECH02.MIX`,
  one more `ERAS` entry in `scripts/eva_mailbox_build.py`, an emblem at
  `scripts/tab_emblems/tsnod.png`, and a crest region. The atlas can grow to 8192x8192 for it
  (`ui-atlas-modding.md`). Recipe: `ts-gdi-faction.md`. HD hand-offs (21 buildings, 19 units) are
  in `~/Desktop/Tiberian Factions/`. The TS Nod wall is already in, dormant, and so is the Rocket
  Infantry (`TSE3`, `TechLevel=-1`, TS GDI's owners and barracks): give it TS Nod's owner, Hand of Nod
  and TechLevel 2 then. The other Nod infantry cameos wait in `ts-hd-cameos/waiting-for-units/`.
- **TS Pavement (GAPAVE), alongside TS Nod.** It turns cells into pavement: it keeps Tiberium off
  build space and blocks subterranean units. Costs: placement logic like the wall divert (the
  building becomes ground) and square-grid ground art, since TS's is isometric (the Firestorm
  panels were rebuilt the same way, `scripts/ts_pack_fsdf.py`).
- **The TS HD rebuild:** branch `ts-buildings-hd`, worktree `../worktrees/tf-ts-hd`, skill
  `ts-to-ra-hd-art`.
- **Big units show through a TS war factory's shut door (fix in test):** the HD harvester, Mobile War Factory,
  Titan and Juggernaut reached past the door from the shared bay seats, so they now wait deeper (`building.cpp`,
  the bay seat). The depths come from `scripts/probes/wf_bay_sim.py`, which composites a unit behind the near
  face and door; the Juggernaut, taller than the bay, shows its antenna tip over the roof.
- **The deployed Mobile War Factory loses units:** of three APCs ordered one after another, only the third
  rolled out; Titans have teleported or never arrived, and a finished unit can wait seconds for the doors.
  The exit runs on the per-unit rail (`drive.cpp`) and the doorstep table in `building.cpp`; log each
  delivery's seat, rail and doorstep before changing either.
- **TS Barracks infantry appear left of the door:** they snap to the nearest of their cell's five spots
  (`Closest_Free_Spot`), and the exit point `XYP_COORD(32, 26)` in `ClassTsPile` still lands them off the
  door's centre line in play. Measure where one appears against the doorway before moving the point.
- **The Upgrade Center's plugs turning in their sockets:** the Ion Cannon Uplink's dish and the Seeker
  Control's camera have idle frames, but the TSPLUG loops bake each plug at frame 0, and the plug frames'
  128 px boxes clip the uplink's dish. Needs the art chat's idle frames on the Upgrade Center's own canvas
  at each socket, uncropped; the packer then plays them in the combinations' loops.
- **A real TS sidebar** (TS uses TD's HUD scene with its own crest for now). Probes, cheapest
  first: (1) can a tactical scene widget take a standalone loose DDS instead of an atlas region;
  (2) is a third scene loadable (copy `Tactical_UI.bui` under a new name and point one faction at
  it). A loose `.MTD` is ignored, but the atlas can grow (`ui-atlas-modding.md`).
- **TS buildings' snow art:** TS ships per-theatre variants (GT/NT temperate, GA/NA arctic). We
  pack only temperate. Needs the theatre-specific-art flag, a second HD set per building and the
  arctic decode (UNITSNO.PAL). Cosmetic.
- **Decision: how RA and TD factions detect diggers.** Only the TS Sensor Array senses them; a
  Nod digger under an Allied or GDI base is invisible. The leaning is "they can't".

## Features and ideas

- **TS chrono arrival at skirmish start.** A TS player's opening units are held back while a
  chrono vortex opens on their start, then come through one by one and fan out. The vortex is
  launcher-drawn and the DLL can place it (`launcher-render-contracts.md` 10: `VortexActive/X/Y`
  in `Get_Dynamic_Map_State`, about 350 px, one per map, so stagger two TS players). Send it only
  to players who see the start cell (`Get_Dynamic_Map_State` gets `player_id`). Voice:
  "Establishing battlefield control. Stand by." is `00-I200` in both EVA (SPEECH01) and CABAL
  (SPEECH02); EVA never recorded "established", CABAL has "Battle control established" as
  `01-N008`. Text as TS does it: `****ESTABLISHING BATTLEFIELD CONTROL****.........Standby!`,
  then `****BATTLEFIELD CONTROL ESTABLISHED****`. Keep it to about 5 s; AI TS players arrive the
  same way. Fallback look: the RA2 Chronosphere warp per unit.
- **Range rings for defences:** a ring round a selected defence, and following the cursor while
  one is placed; the same pass draws the Sensor Array's and the EMP Cannon's reach. The DLL hears
  everything it needs (`SIDEBAR_REQUEST_START_PLACEMENT`, `INPUT_REQUEST_MOUSE_MOVE`,
  `SIDEBAR_REQUEST_PLACE` / `SIDEBAR_CANCEL_PLACE`). Draw with the launcher line renderer
  (`CNCObjectStruct::Lines`, 3 per object, frames 0-4) on carrier entries visible to the owner
  only. Prove one clean circle round a selected turret first. An aiming-only ring for the
  E.M. Pulse has to read ClientG's input mode from inside the player's launcher
  (`launcher-vs-dll-ownership.md`, "Aiming is invisible to the sim").
- **Resource spill on destruction:** silos and refineries (TS and TD) spill Tiberium when
  destroyed, RA's spill Ore. Settle how much, where, and whether harvesters get TS's cargo
  scatter. The Ghost Stalker's own death spill isn't ported either.
- **Hybrid maps: Tiberium eats Ore where fields meet.** Today neither converts the other
  (`CellClass::Spread_Tiberium` keeps them apart). To decide first: the rate (only
  full-density Tiberium, on the spread tick), whether gems are eaten, and whether a converted cell
  starts thin or keeps the Ore's value.
- **Superweapon power pass:** after the TS Ion Cannon (600 centre + 300 x 8 ring), the other
  superweapons should be more powerful too, each with its own identity. RA nuke, TD nuke,
  Chronosphere, Iron Curtain, paradrops, recon.
- **Era-scoped build times:** RA rules for RA buildings, TD for TD, TS for TS, like the era door
  rule. Read the TD and TS sources first (TS = a per-1000-credits rate plus a multi-factory bonus).
- **TS depower button and waypoint mode:** both DLL-side. The PING button arrives as a beacon
  request with a cell (`CNC_Handle_Beacon_Request`) and beacons are useless in skirmish, so a
  re-skinned PING can toggle power on the building at that cell. Waypoints stay a hotkey mode
  unless another DLL-reaching command turns up.
- **Crates that give another faction's construction yard,** so a wiped player can come back as a
  different faction. The faction MCVs exist now (AMCV, SMCV, TDGMCV, TDNMCV, TSMCV); the crate
  hands one out. `CrateType` (defines.h) is a plain enum.
- **Harvester cargo:** Tiberium banks as Gold (`unit.cpp`, the `OVERLAY_TIB01` case), so a
  harvester's load can't be told apart. A per-harvester Tiberium counter (one member, Save/Load,
  two reset sites) would allow cargo-coloured dock smoke: green for Tiberium, grey for Ore, maybe
  blue for gems. New HD anim names ship as loose VFX ZIPs registered in `RA_VFX.XML`.
- **Chimney smoke** on power plants and refineries: `ANIM_SMOKE_M` spawned from
  `BuildingClass::AI` at a per-type stack offset, off while building, selling or unpowered,
  deterministic for lockstep.

## AI milestone (plan: `ai-upgrade-plan.md`)

- **Naval invasions don't land.** The ferry pipeline logs its full chain, but no match has shown
  a force landing, holding a beach and building on it. Structural item, the harbour seal: a naval
  yard and parked fleet can seal their own channel, and zones ignore buildings, so no zone check
  sees it. Design: naval yards must not seal their channel; pickup shores must be reachable by
  the transport (or re-pick after N stalls); filter landing cells next to micro-islands. The
  FERRY-WAVE release and FERRY-MCV forward base were never seen.
- **Ferry waits for sea control:** launch only when the house's armed hulls match the strongest
  enemy fleet seen on that water (or none seen and a patrol has crossed).
- **Tech ordering:** no house had a tech centre, advanced comm or temple after 12 sim-minutes of
  four-refinery income (W3, "tech when affordable").
- **One Hard 1v1 against a human** (Keep off the Grass, GDI vs Nod, `tf_dev_reveal.flag` only)
  reading ECO-HOLD / WAVE-STAGE / WAVE-RELEASE; both have fired only in AI-only Docklands games.
- **Medium AI on a connected map** must log zero FERRY lines.
- **Naval:** a funding floor (a house fire-sold its yard while fielding a fleet); stop land
  attack teams at land-unreachable enemies; a transient `SYRD/APWR no-location` PLACE-FAIL about
  once a match, always self-recovered.
- **Air doctrine against siege hulls** (CA/TDCA/MSUB/TDMSUB): a weighted aircraft target bias once
  intel has seen one. **Gap-generator fairness:** AI aircraft attack things under a gap field.
  **Sub detection:** a choice between B (sonar radius) and C (a detector hull).
- **Minelayer brain:** where to lay (approaches, chokepoints, its own ring), when to reload, not
  walking its own field (W5 special units).
- **TS GDI AI** builds no transports or navy and never uses the Firestorm or the EMP Cannon.
- Pathfinding and AI bugs: `known-issues.md`.

## Bigger arcs

- **Campaign, "The Inheritance War"** (`gdi-nod-campaign-story.md`, `campaigns-page.md`):
  waits behind the AI milestone. First task: a launch route that ships, either the mission
  carrier reading its missions from data or a hijacked Aftermath slot given `<House>GDI</House>`,
  then GDI mission 1 for real on the GDI tab, with a map, briefing and win/lose conditions,
  before committing to all nine. With it, flatten the
  difficulty stat multipliers: `CCDATA/rules.ini` `[Easy]`/`[Difficult]` still carry the stock
  spread (Easy Firepower 1.2 / Armor 1.2 / ROF .8 / Cost .8), and difficulty is meant to be
  behavioural only. Check whether `Scen.CDifficulty` feeds `Rule.Diff[]` in skirmish.
- **Co-op missions** (`coop-missions-design.md`).
- **The TD maps as their own Workshop item** (`parked/td-maps/README.md`).

## Decided: not doing

- Fleet-wide naval naming in ModText.csv, and classic SHPs for the RA-art naval clones.
- The Nod defensive economy (AGT against Obelisk plus SAM): stood down. The facts are in
  `balance-deep-dive.md`. A Tesla chain to nearby targets is parked; RA's Tesla does not chain.
- Controller support: parked.
- A live era-wide audio flip on a TS MCV deploy: rejected. The voice follows the picked faction.
- Veterancy: if it ever comes in, it comes in for every faction, never TS alone.
- Porting TS's hierarchical pathfinder: no (`path-failure-livelock-design.md`).
- The Mammoth Mk. III's four-rocket pod volley (it fires RA's pair): a crate easter egg, not worth the time.
