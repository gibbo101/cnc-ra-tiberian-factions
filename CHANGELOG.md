# Changelog

All notable changes to **Tiberian Factions for Red Alert** are documented here.

## [4.1.0] — 2026-07-22

The groundwork update: separated tech trees for all four factions, a locked
prerequisite policy, a full sidebar identity pass, and a wave of skirmish AI
fixes ahead of the AI milestone. GPL v3.

### Added
- **Separated faction tech trees.** GDI, Nod, Allies and Soviets each build
  their own Construction Yard, MCV, War Factory and Helipad as distinct engine
  types. Capturing one of these buildings hands the captor that faction's full
  tech tree, so a captured yard really lets you build the other side's arsenal.
- **Unholy Alliance skirmish mode.** A fourth entry in the lobby Mode dropdown
  that starts every player, human and AI, with all four factions' construction
  yards at once.
- **Faction badges on the cameos, once you build from more than one faction.**
  Capture a rival construction yard or war factory and the cameos in that
  category start carrying emblems showing which of your factions builds each
  entry. While you produce a category from a single faction every badge would
  say the same thing, so the plain cameo is shown instead. The ten superweapon
  cameos always carry their owner emblems.
- **The Tiberian Sun walkers as rare crate finds.** The Titan, Mammoth Mk. II
  and Hover MLRS can drop from the unit crate in skirmish (a 1-in-8 roll, any
  faction). They are an easter egg, not a buildable part of any roster.
- **Expanded skirmish music rotation** to 107 tracks.

### Changed
- **Prerequisite policy locked.** Only low-tier infrastructure (power,
  refinery, repair) is shared across factions. Barracks, War Factory, Helipad,
  naval, airfield, radar and tech centres are faction identity and no longer
  cross the divide; the Allied Dome and the GDI/Nod HQ no longer substitute for
  each other.
- **Sidebar sorted into faction blocks.** Shared buildables first, then Allied,
  Soviet, GDI and Nod, each block in tech order, on every tab.
- **Classic graphics mode locked out.** The mod is HD-only, so its content can
  no longer be dropped into the classic renderer it has no art for.
- **Hover MLRS** now carries the armour-piercing punch its price implied.

### Fixed
- **Per-slot AI difficulty.** Each AI now takes its own lobby Easy/Medium/Hard
  pick, in skirmish and LAN alike, instead of falling back to all-Hard from the
  second match of a session onward. Each AI's faction and colour are checked
  against the lobby before its difficulty is applied, so a stale reading from an
  earlier lobby cannot be mistaken for the current one.
- **AI air power.** The AI builds air production once its ground economy is
  established and fields helicopters and planes again; it had built no helipads
  or airstrips since v4.0.0.
- **Smarter AI base logic:** fair-fog blind-scout dispatcher, a fix for Nod
  Temple and Stealth Generator build starvation, tier-2 buildings held behind
  an established economy, and harvesters that retreat home when idle.
- **Pathfinding.** A* is now bounded by a heap and an expansion budget, cutting
  stalls on large maps.
- **Stock campaign compatibility.** Playing the original Allied and Soviet
  campaigns with the mod enabled no longer misbehaves: wire fences on stock maps
  render correctly instead of turning into goodie crates, enemy bases pace as the
  missions intended rather than building and attacking like a skirmish AI, and
  commandos such as Tanya can board an allied evacuation transport again.

### Known limitations
- The one-key MCV deploy hotkey is unavailable for all four factions in
  skirmish. Deploy by clicking the MCV as usual. A default key binding cannot
  currently be shipped from a mod; this is queued for a future release.

## [4.0.0] — 2026-07-16

The faction arsenal expansion: navies, GDI air power, Nod stealth, and support
powers for every side, plus a wide balance pass. GPL v3.

### Added
- **Navies for GDI and Nod.** GDI builds a Naval Yard and fields the Gunboat,
  Destroyer, and Cruiser (the Cruiser needs the Advanced Communications
  Center). Nod builds a Sub Pen and fields the Attack Submarine and the
  Temple-guarded Missile Sub. Ships repair at their yard, subs dock at their
  pen, and the whole fleet shows faction-correct names in the sidebar.
- **GDI Airfield and the A-10 Warthog**, flying TD-authentic napalm bombing
  runs.
- **Nod Stealth Generator.** Cloaks nearby friendly buildings and units.
- **Nod Flame Bunker.** An anti-infantry flame emplacement.
- **Support powers.** GDI GPS satellite; Nod Spy Plane and Paratroopers.
- **Air-aware AI.** The GDI AI builds the Airfield and flies A-10s, and every
  AI now scales its air force and anti-air to the strongest air power in the
  match, human or AI.

### Changed
- **Balance pass across all four factions:** air (Orca and Apache to
  Longbow/Hind parity, A-10 pricing), armor (GDI Mammoth and APC, Nod Light
  Tank), defences (Nod Gun Turret and SAM), infantry (Minigunner range),
  extended artillery ranges, and GDI/Nod MCV + Construction Yard at RA
  parity.
- **AI build order:** air production no longer outranks the war factory, so
  an AI behind on air builds its core base first.

### Fixed
- **TD temperate coastal maps** no longer render shorelines and bridges as
  white squares. A tileset-generation regression (introduced with the winter
  and desert theatres) dropped the temperate shore and bridge registrations;
  only TD temperate maps with coast were affected.
- **Submarines surface with the proper submarine sound** instead of the
  Stealth Tank's cloak sound.

## [3.0.0] — 2026-06-18

The harvester economy and docking overhaul. Harvesters of either side can now
dock at either side's refinery, unload visibly, and turn around faster, on top
of a wide sweep of harvester pathfinding and anti-stuck fixes. GPL v3.

### Added
- **Cross-faction harvester docking.** A harvester can now unload at the other
  side's refinery: an Allied or Soviet harvester docks at a GDI or Nod Tiberium
  refinery, and a GDI or Nod harvester docks at an Allied or Soviet ore
  refinery. This matters most when a refinery changes hands, since a captured
  refinery keeps working for its new owner's harvesters.
- **Capturing a refinery captures the harvester docked at it.** Send an engineer
  into an enemy refinery while a harvester is unloading and you take the
  harvester along with the building.
- **Visible unloading.** Harvesters now play a full unload at the dock instead of
  dumping their load instantly. Allied and Soviet harvesters run a billowing
  dust cycle, and a green Tiberium haze vents while a load is siphoned.

### Changed
- **Faster, balanced harvester economy.** Dock times were cut roughly in half and
  made equal for every harvester-and-refinery combination. Red Alert's economy
  was built on near-instant unloading, so this brings that pace back while
  keeping both sides' economies in step, which keeps unit costs comparable across
  factions. Income per load is unchanged; harvesters simply turn around quicker.
- **Harvesters avoid enemy-held ore.** When choosing where to mine, a harvester
  steers away from fields with enemy units sitting on or near them, preferring
  clear ore unless the contested field is much closer or the only ore left.
- **Smarter field choice.** Harvesters pick ore by actual driving distance around
  water and cliffs rather than straight-line distance, favour a field with a
  worthwhile amount of ore over a lone regrown speck, and no longer drive across
  the map past closer patches.
- **Harvesters get themselves unstuck.** A harvester that stops making progress,
  whether wedged in traffic or sitting idle after giving up, now recovers on its
  own: it nudges blocking infantry aside, works free of a jam, and as a last
  resort restarts its search instead of standing dead.
- **Refinery docks kept clear.** The dock approach of a refinery is now reserved
  for harvesters, so the AI can no longer park a tank or a guard on it and block
  unloading. Harvesters waiting on a busy refinery spread across nearby cells
  instead of piling onto one, and a harvester queued at a busy refinery switches
  to another the moment one frees up.

### Fixed
- **Harvesters keep working when a refinery is lost.** A GDI or Nod harvester no
  longer goes idle when its last Tiberium refinery is sold or destroyed while an
  ore refinery still stands; it heads to the refinery that remains.

## [2.4.0] — 2026-06-17

Smarter economy and combat AI, plus two CFE Patch Redux ports. GPL v3.

### Added
- **Infantry avoid Tiberium.** Foot soldiers of every faction now treat a
  Tiberium field as ground to route around rather than wade through, since
  standing in it hurts them. They path around the edge instead of marching
  across and taking damage.

### Changed
- **Harvesters recover from blocked ore fields.** A harvester sent to a patch
  that has been walled off by buildings (a turret, or the AI fencing its own
  gems) no longer spins forever trying to reach it. It gives up on the dead
  field, remembers the whole field for a short while, and redirects to a
  reachable patch. If nothing reachable is left it pulls back toward a refinery
  and re-scans from there instead of idling against the wall, and it resumes the
  field automatically once the blockage is removed.
- **Smarter SAM sites.** A SAM that loses its target part way through firing now
  looks for another aircraft in range before standing down, instead of dropping
  its guard and going dormant while enemy planes are still overhead.
- **Harvester self-repair.** GDI and Nod harvesters slowly mend themselves back
  to working order after taking fire, matching the Allied and Soviet harvester
  behaviour.

### Fixed
- **Recon Bike fires off-axis targets.** The Nod Recon Bike now turns to shoot a
  target to its side instead of sitting still and refusing to fire until the
  target happened to line up with its facing.

## [2.3.0] — 2026-06-16

Cooperative chokepoint traffic, resolving the single-cell-gap backup noted in 2.2.2,
and capping the movement arc that began with attack-move and A* pathfinding. GPL v3.

### Changed
- **Infantry give way to vehicles in narrow corridors.** Foot soldiers no longer
  block vehicles in a one-tile-wide pass. A vehicle that needs the corridor moves
  idle infantry out of the way, and a packed column drains out single file then
  fans out at the far end instead of jamming. Infantry walking into a vehicle are
  turned back out, while a column already crossing keeps the corridor and the
  vehicle waits its turn at the mouth, so only one group uses the gap at a time.
- **Vehicles no longer freeze on a passing infantryman.** A moving foot soldier
  reads as a soft, temporary block rather than a hard head-on, so vehicles flow
  past foot traffic instead of locking up against it.
- **No more endless yielding in the open.** A unit that has been giving way to a
  stalled neighbour on open ground for too long stops waiting and routes around
  it, instead of holding its position indefinitely.

### Known issues
- Two vehicles meeting head-on in a one-tile gap with no room to step aside can
  still stall until one of them is freed. Cooperative handling for that case is
  planned for a follow-up.

## [2.2.2] — 2026-06-14

Group-move destination spread, building on the 2.2.1 A* pathfinding. GPL v3.

### Changed
- **Spread-out group moves.** When you send several units to a single spot they
  now fan out across nearby cells and settle into a tidy group, instead of all
  piling onto the exact cell you clicked and shuffling for position. Each unit
  is handed a reachable cell on the same side of any cliff or water, so they no
  longer trace the long way around terrain to reach a contested spot.

### Known issues
- A large group crossing a single-cell gap (a one-tile land bridge or narrow
  pass) can still back up while they file through one at a time. Cooperative
  traffic handling for these chokepoints is planned for a follow-up release.

## [2.2.1] — 2026-06-14

Smarter unit pathfinding, adapted from CFE Patch Redux by ChthonVII (A* search
after cfehunter), GPL v3.

### Changed
- **A\* pathfinding.** Units now plan their routes with an A* search instead of
  the original "head straight for the target and turn when you hit something"
  method. The result is more direct, sensible movement around buildings,
  cliffs, and terrain, for every unit and faction. If no A* route is found the
  game falls back to the classic pathfinder, so movement is never worse than
  before.

### Known issues
- When a large group is ordered onto a single spot or through a one wide gap,
  units can still bunch up and shuffle while they sort out who goes first. A
  follow up release will add cooperative traffic handling to smooth this out.

## [2.2.0] — 2026-06-13

Attack-move, adapted from CFE Patch Redux by ChthonVII (after cfehunter and
Root-Core), GPL v3. Works for all four factions and every unit type.

### Added
- **Attack-move.** Shift+click the ground (or a unit) to advance toward a
  destination while engaging hostiles along the way, then resume the journey
  after each fight. Covers tanks, infantry, aircraft (return to rearm when out
  of ammo), boats, minelayers, and chronotanks.
- Attack-moving units now go after **all** enemy buildings in their path, not
  only defensive ones, **but prioritise threats**: a unit engages the turret,
  Tesla coil, or enemy unit shooting at it before bothering with a passive
  building, and breaks off a passive target the moment a real threat closes in.

### Fixed
- Z-order on the taller GDI/Nod structures (Advanced Guard Tower, Obelisk,
  power plants, barracks, comm centers): vehicles parked behind them no longer
  render in front of the building.

## [2.1.0] — 2026-06-11

Quality of life release, adapted from CFE Patch Redux by ChthonVII (after
cfehunter and Root-Core), GPL v3. All features work for all four factions.

### Added
- **Rally points** on production buildings and repair bays. Click ground to
  set, Alt+Click to rally onto a unit or building, click the building to
  clear. Cargo-plane deliveries honour it; any spot on the map is valid.
- **Smarter harvesters.** Spread across refineries by distance and queue
  length, jump the queue when closer, re-shuffle when a dock frees, head
  straight home when full.
- **Smarter repair bays.** Units queue at a busy bay; repaired units drive
  off to the rally point instead of blocking the pad; aircraft return to a
  free pad or strip.
- **More zoom.** 11 pixel-perfect steps instead of 8, including further
  zoom-out. (By bleid, via CFE.)

### Fixed
- Docking bugs: queued units disrupting the unit being serviced, and a TD
  refinery visually losing its docked harvester.

### Notes
- Saved games from earlier versions are not compatible.

## [2.0.0] — 2026-06-10

### Added
- **Tiberium.** The real thing, alongside Red Alert's ore: green crystal fields
  that harvesters collect (same value as ore), that grow and spread over time
  (when "Ore Regenerates"/"Ore Spreads" are enabled in the lobby), and that
  damage infantry who walk through them. Infantry who die in a Tiberium field
  occasionally spawn a visceroid — a hostile mutant creature that attacks
  everyone. Blossom trees stand at the heart of the fields, shedding spores
  and seeding fresh Tiberium around them.
- **A 31-map Tiberian Dawn map pack** — every multiplayer map from Tiberian
  Dawn and The Covert Operations, faithfully converted across all three
  theatres:
  - *Temperate (14):* Green Acres, Lost Arena, River Raid, Pitfall, One Pass
    Fits All, King Takes Pawn, Tiberium Garden, Emerald Highlands, King of
    the Mountain, Surgical Incision, Village of the Unfortunate, A Long Way
    from Home, plus the community maps Elevation and Heavy Metal.
  - *Winter (4):* Northern Explosion, Nowhere To Hide, Winter Wonderland,
    and Tournament Middle Camp — TD's icy-forest winter look, faithfully
    recreated.
  - *Desert (13):* Red Sands, Sand Trap, Cactus Valley, Desert Madness,
    Diverse Region, Eye of the Storm, Four Corners, Lakefront Clash,
    Marooned, Monkey in the Middle, Moosehead Barrens, Straight and Narrow,
    and Tournament Desert — the classic TD desert, a theatre Red Alert
    never had.

  Each map keeps its original layout, start positions, Tiberium fields, and
  blossom trees, with an authentic preview image in the lobby. The maps
  appear under **Custom Maps** (look for the `[TF]` tag) after your first
  match with the mod — and they load fine in unmodded Red Alert too, just
  without the Tiberium and TD scenery.
- **Tiberian Dawn terrain, remastered.** TD's own coastlines, cliffs,
  bridges, winter forests, and desert dunes render in full HD on the
  converted maps — including animated water lapping along the shorelines,
  just like the TD remaster.
- **Snowy trees on the winter maps.** Trees on the converted winter maps
  use Tiberian Dawn's own snow-covered winter art — in HD and classic —
  instead of green summer trees.

## [1.1.6] — 2026-06-07

### Changed
- **Streamlined the main menu.** Removed "Start New Game" and moved "Mission
  Select" to the top. "Start New Game" opened Red Alert's original campaign
  picker — a screen this mod can't customise, and which didn't display correctly
  alongside the new GDI/Nod faction emblems. Everything is now reached through
  Mission Select, which is also where future GDI/Nod campaigns will live.

## [1.1.5] — 2026-06-07

### Fixed
- **GDI/Nod flag on the skirmish map.** When you picked a start position in the
  skirmish lobby, the flag pinned to that spot on the map preview showed the old
  country flag (Spain for GDI, Turkey for Nod) instead of the faction emblem. It
  now shows the GDI eagle and Nod scorpion, matching the player-slot icons.

## [1.1.4] — 2026-06-07

### Fixed
- **Skirmish start positions could overlap.** When you picked your own start
  location but left one or more AI players unpicked, an AI could occasionally
  spawn on the exact cell you had chosen. Every player now gets a distinct start
  position. (The cause was the order in which start spots were assigned, not
  anything faction-specific — it was just easiest to notice playing GDI/Nod.)

## [1.1.3] — 2026-06-07

### Fixed
- **GDI/Nod unit build times.** GDI and Nod vehicles, infantry, and aircraft
  took noticeably longer to build than equal-cost Allied/Soviet units (roughly
  40% slower) — they used Tiberian Dawn's raw-cost timing, which skipped Red
  Alert's build-speed scaling. They now build at the same speed as their
  Allied/Soviet counterparts. Building construction times are unchanged.

## [1.1.2] — 2026-06-04

Fixes from feedback by DontCryJustDie (author of the TD-Assets mod).

### Fixed
- **Construction Yard graphic distorted.** The GDI/Nod Construction Yard was
  stretched a cell too tall and bulged out of its concrete pad. Its on-screen
  size now matches its 3×2 footprint, so it sits properly in place like the
  Tiberian Dawn original.

### Changed
- **Much smaller download.** `RedAlert.dll` shrank from 27 MB to ~2 MB. The
  previous build shipped with embedded debug symbols that did nothing in-game;
  they're now stripped from the released file. No gameplay change.

## [1.1.1] — 2026-06-03

First-playtest fixes (thanks to a GDI/Nod vs Allies/Soviet session).

### Fixed
- **GDI/Nod unit sight range.** GDI/Nod vehicles and infantry could barely see —
  the Hum-vee scout in particular got lost in the shroud. Sight ranges are now in
  line with their Allied/Soviet counterparts.
- **GDI/Nod building sight range.** Bases now reveal a little more of the
  surrounding map, matching Red Alert's scale.
- **Tiberium Harvester now auto-harvests when built.** A harvester produced from
  the war factory drives off to the nearest ore field on its own, like the Allied
  and Soviet harvesters — instead of sitting idle outside the factory.
- **GDI/Nod factory build-speed bonus.** Building a second war factory, barracks,
  etc. now speeds up production for GDI/Nod the same way it does for Allies/Soviet.
- **Radar sound.** The radar online/offline sound could repeat endlessly (and in
  network games). It now plays once when your radar comes online and once when it
  goes offline, for every faction.
- **Selection.** Box-selecting your army no longer scoops up the GDI/Nod MCV.

### Changed
- **GDI APC speed.** The GDI APC was wildly fast — it outran the Hum-vee scout.
  Brought down to a sensible transport speed.

### Internal
- Removed leftover debug logging that could write files to your CnCRemastered
  folder during play.

## [1.1.0] — 2026-06-03

### Fixed
- **GDI/Nod skirmish starting units.** When starting a skirmish with starting
  units enabled, GDI and Nod were handed Allied tanks, jeeps, and riflemen. They
  now start with their own Tiberian Dawn rosters (Medium/Light/Mammoth tanks,
  Hum-vee/Buggy/Bike, APC, MLRS/Artillery/SSM, Flame/Stealth tanks, and the TD
  infantry line), drawn from TD's own multiplayer roster. Allies/Soviet unchanged.

### Changed
- **GDI/Nod harvester speed — brought to parity with the RA harvester.** The
  Tiberium Harvester was slower than the Allied/Soviet harvester (it ran its
  Tiberian Dawn movement values); it has been tuned to match the Red Alert
  harvester's speed, closing the GDI/Nod early-economy gap. The docking unload
  time is kept as the intended GDI/Nod trade-off.

## [1.0.0] — 2026-05-30

- Initial public release. GDI and Nod as fully playable factions alongside Allies
  and Soviets: complete base catalogues, full unit rosters (infantry, vehicles,
  aircraft), superweapons (Ion Cannon, Nuclear Strike), working skirmish AI, TD
  EVA and unit voices, building/weapon sound effects, faction-select identity, and
  classic-graphics palette handling for TD sprites.
