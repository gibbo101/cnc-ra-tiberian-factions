# Changelog

All notable changes to **Tiberian Factions for Red Alert** are documented here.

## [5.0.0] — 2026-10-04

Another Tiberian faction joins the fray! A Chronosphere accident tears a hole
in time and drags GDI out of the future. A terrible accident, or an insidious
plot by Kane?

- Tiberian Sun GDI, a fifth playable faction!
- All-new intro movie!
- UI overhaul!
- Gates and walls for every side!
- Tiberium on Red Alert's own maps!
- AI improvements!

Tiberian Sun's units, weapons and rules are ported with OpenTS, by the OpenTS
Developers, as the reference. GPL v3.

### Added
- **Tiberian Sun GDI, a fifth playable faction.** Pick "TS GDI" in the lobby to
  start on a Tiberian Sun MCV, build the TS tech tree from Tiberian Dawn's
  sidebar, and hear Tiberian Sun's EVA, unit crews, credit tick, radar and
  building sounds. The faction flies Tiberian Sun's gold eagle coin on its radar
  crest, lobby row and cameo badges, cut from a SteamGridDB icon by hazelnut.
  Computer players can be TS GDI too. Everything below uses Tiberian Sun's own
  art and sound:
  - *Base:* Construction Yard, Tiberian Power Plant (takes up to two Power
    Turbines), Barracks, Tiberium Refinery, Silo, War Factory with its roll-up
    bay door, Radar, Helipad, Tech Center and Service Depot, with their
    animations and damage states.
  - *Infantry:* Light Infantry; the Disc Thrower, whose disc skips along the
    ground; the Engineer, who captures an enemy building at any health and
    restores a friendly one to full; the Medic (like Tiberian Sun's, it cannot
    heal Jumpjet Infantry); the Ghost Stalker, one at a time, with a railgun
    that pierces a line of troops, C4 for buildings and healing in Tiberium;
    and Jumpjet Infantry, who fly over terrain and count as air targets while
    airborne.
  - *Vehicles:* Harvester (it docks at any faction's refinery, and any harvester
    docks at the TS refinery), Wolverine, Titan, Amphibious APC (it swims),
    Hover MLRS, Disruptor (its sonic band follows the target and hurts
    everything inside it, never Disruptors on the same side), Juggernaut
    (long-range walking artillery that sets down to fire, on attack-move
    too), Mammoth Mk. I
    (Tiberian Sun's unbuildable Mammoth Tank, here behind the Tech Center) and
    the MCV. TS buildings and vehicles leave TS Light Infantry as survivors.
    Submarines can torpedo the Hover MLRS and the APC while they are afloat.
  - *Aircraft:* Orca Fighter, Orca Bomber (two bombing passes per sortie) and
    the Carryall, which lifts one of your vehicles and sets it down where you
    send it.
- **Dropship Bay.** TS GDI fields the Mammoth Mk. II and the Mech Division
  (three Titans and two Wolverines at a discount) by dropship: the ship lands
  vertically on the pad, sets the order down and lifts off again. The bay has
  its own build queue beside the War Factory and a five-minute reload counted
  down on the cameo. One bay per player.
- **Upgrade Center and Tiberian Sun's superweapons.** A two-slot host that also
  spots cloaked units nearby. Install two of its three plugs:
  - *Ion Cannon Uplink:* the Tiberian Sun Ion Cannon, with its own beam,
    shockwave ring, sound and timer, alongside the TD Ion Cannon if you hold
    both.
  - *Drop Pod Node:* five pods of Light Infantry and Disc Throwers streak down
    on the target, strafing the landing zone.
  - *Seeker Control:* the Hunter Seeker droid picks an enemy and destroys it.
    One left click on the ready cameo launches it; no target is needed.
- **Firestorm Defense.** The Firestorm Generator powers Firestorm Wall
  Sections, flat pads anyone can cross until the field goes up. One left click
  on the cameo raises the field and another drops it early, banking what is
  left. While it is up, anything on a section or flying over one is destroyed,
  your own units included, enemy shots stop at the wall, and every hit on a
  section drains the field. A full charge holds it for about a third of its
  charging time.
- **EMP Cannon and Mobile EMP.** The EMP Cannon fires the E.M. Pulse: the
  nearest powered cannon turns, charges and lobs a pulse that stuns vehicles,
  ships and grounded aircraft for 30 seconds, shuts down buildings' weapons,
  radar and generators, downs low-flying aircraft, destroys Limpet mines and
  forces buried units to the surface. Power, construction and production carry
  on. The pulse reaches 3 cells, scaled down from Tiberian Sun's to suit Red
  Alert's maps. The Mobile EMP charges up, then deploys to stun every vehicle
  and building within 3 cells for 10 seconds, friend and foe alike.
- **Mobile Sensor Array, Mobile War Factory and Limpet Drone.** The Sensor
  Array deploys to show you and your allies cloaked and underground enemies
  within 25 cells, and the cloaked ones can then be targeted. The Mobile War
  Factory, one at a time, unfolds into a working TS War Factory wherever you
  need one and packs up again with the deploy key. The Limpet Drone settles
  into a cloaked mine that latches onto the next enemy vehicle, slowing it to
  65% and showing you what it sees until a repair bay pulls it off.
- **Component towers and the TS Concrete Wall.** The Component Tower takes one
  weapon, a Vulcan Cannon, RPG or SAM, each with Tiberian Sun's own sounds and
  effects. Towers stand in wall lines (place one on your own wall section to
  replace it) and wear new HD art with HD turrets and a door lamp that lights
  while the base has power. TS GDI also builds sandbags and its own concrete
  wall, redrawn in HD for Red Alert's grid.
- **Gates for every faction.** Allies, Soviets (a Tesla gate), GDI, Nod (a laser
  gate) and TS GDI each build an east-west and a north-south gate in HD. Your
  units and your allies' drive straight through: the gate opens as they arrive
  and closes once the way has been clear for a while, letting anyone through
  while it stands open. Gates sit in wall lines, can be placed over your own
  walls and draw 5 power; the Tesla and laser gates fall open when their base
  is short of power.
- **Wall lines fill themselves.** Place a wall piece in a straight line within
  five cells of another of the same kind and the gap between fills, charged per
  piece, as long as every cell is clear. If you can't afford the whole gap,
  only the piece you clicked goes down. This works for every wall type and for
  Firestorm Wall Sections.
- **The classic Tiberian Dawn sidebar.** GDI, Nod and TS GDI play on Tiberian
  Dawn's in-game interface: its sidebar, build tabs and tab icons, power bar,
  credits, and sell, repair and map buttons. Every faction shows its own radar
  crest. Allies and Soviets keep Red Alert's interface.
- **EVA speaks for your faction.** The lines the game fires itself ("Cannot
  deploy here", "Insufficient power", "Select target", "Repairing", "Mission
  accomplished", "Mission failed", "Battle control terminated") play in Tiberian
  Dawn's voice for GDI and Nod and in Tiberian Sun's for TS GDI, and keep up
  when you switch faction without restarting the game. "Structure sold" follows
  your faction too. Lines Tiberian Dawn or Tiberian Sun never recorded, such as
  "Mission saved", stay silent for those factions instead of falling back to
  Red Alert's EVA. Each faction's credit counter ticks with its own game's
  sound.
- **Lobby faction picker.** Every row of the faction drop-down is named for its
  faction (GDI, Nod, TS GDI, Allies, Soviet) and shows the faction's emblem
  instead of a country flag, and the list shows every row and Random without
  scrolling. Map start markers and loading-screen player badges show faction
  emblems too.
- **LAN games match single player.** Every player in a LAN game gets their own
  faction's crest, tab icons and EVA, their own deploy and select-all keys, and
  one-click Firestorm and Hunter Seeker control.
- **A Tiberian Factions front end.** The Tiberian Factions title replaces Red
  Alert's on the main menu, loading screens and campaign select, its lettering
  in Tiberian Sun's molten fill (set in Archivo Black, SIL Open Font License).
  A new startup intro lands the title and six faction emblems on Hell March and
  cuts to a Red Alert, Tiberian Dawn and Tiberian Sun FMV montage. The main
  menu gets new key art either side of a steel menu box with green labels and
  plays the Hell March Retaliation remix, and its confirmation boxes match. The
  loading screen shows the faction emblem row with a sweeping glint, and the
  skirmish and LAN lobbies, the LAN game list and the Workshop map browser take
  the same steel and green look.
- **Tiberium on Red Alert's official maps.** 151 of the 230 official skirmish
  maps now mix Tiberium fields with their ore, kept fair between start
  positions, with Tiberium-heavy, ore-heavy and even maps spread across the
  pool. Gem fields are never converted, lobby thumbnails are repainted to match,
  and Red Alert's snow maps get winter Tiberium. The other 79 maps stay as they
  were.
- **The AI builds a navy.** On maps where the water matters, the skirmish AI
  builds a naval yard and a fleet.
- **The AI plays TS GDI.** A computer TS GDI builds its base, Component Towers
  with weapon plugs and Power Turbines, trains the TS infantry, flies Orcas,
  orders from a Dropship Bay, and builds an Upgrade Center with the Ion Cannon
  Uplink plus either the Drop Pod Node or Seeker Control (Easy AIs skip
  superweapons). It launches its Hunter Seeker as soon as it charges.

### Changed
- **The construction yard decides the tech tree.** A faction's buildings are
  offered only while you hold that faction's construction yard. Power plants,
  refineries and repair bays come from any yard and satisfy each other across
  all three eras. So the yard you hold, not the faction you picked, decides
  what you build: deploy a TS MCV found in a crate, or capture a TS yard, and
  the TS tree is yours whatever your side. TS cameos carry the TS GDI badge
  once you build from more than one faction.
- **Unit crates from every faction.** A unit crate now draws evenly from one
  pool of every faction's vehicles, harvesters included, plus any faction's MCV
  when bases are on. Some finds come only from crates: the Red Alert 2
  Apocalypse and Prism Tank, the Command & Conquer 3 Mammoth Mk. III and
  Predator, and Tiberian Sun Nod's Devil's Tongue flame tank and Subterranean
  APC, which tunnel underground on longer trips and surface where they are
  sent. Unit crates are now as likely as money crates (about two crates in
  five), and the armour, firepower and speed boosts drop to about one crate in
  35 each.
- **Superweapons split by faction.** Nod's Paratroopers and recon flight are
  now their own powers, separate from the Soviet drop and spy plane, each with
  its own cameo and timer, so holding both sides' buildings gives you both.
  Soviet Parabombs now fly in skirmish, recharging in 7 minutes like
  Paratroopers. Superweapon cameos carry faction badges only once your powers
  come from more than one faction, as the build tabs already did.
- **Nod SAM Site** stays raised and keeps firing while an aircraft is in reach,
  lowering only when the sky is clear. Tiberian Dawn's site ducked after every
  pair of missiles and managed about a quarter of a Soviet SAM's damage. It
  still takes half damage while lowered.
- **AI economy and attacks.** The AI runs a stronger economy, with more
  refineries and harvesters on Medium and Hard, and waits until its army is
  worth committing before it attacks. The AI work in this release drew on
  skirmish AI ideas from Bast75 and xXMini FrankiXx, and more is to come.

- **Tiberian Sun, Red Alert 2 and C&C3 vehicles sit like Red Alert's own.**
  Thirteen of them were drawn a few pixels too high: above Red Alert's tanks
  in the same row, with their selection boxes hanging below them. Their hulls
  are now centred on the unit the way the Remastered Collection's own vehicles
  are, their boxes fit, and their shots still leave the barrels. Thanks to
  DontCryJustDie for spotting it.

### Removed
- **The Tiberian Dawn map pack, for now.** The 31 converted Tiberian Dawn maps
  and their terrain art (temperate, winter and desert) are out of the mod: they
  raised video memory use for every player, and some of them had broken. They
  are planned to return as a separate download. The copies earlier versions
  installed are deleted from your custom maps when the mod loads, and Red
  Alert's interior missions get their own floor art back.

### Fixed
- **Deploy and select-all keys for every faction.** The default deploy key
  (backslash) now deploys or unloads every faction's MCVs, APCs, transports and
  minelayers, and select-all (A) leaves every faction's harvesters and MCVs out
  of the selection. This lifts the limitation listed since 4.1.0.
- **Crashes:** a crash with more than about four mods enabled at once, which
  overran the game's list of mod folders (found by DontCryJustDie); a crash
  when packed traffic, such as harvesters queueing at a refinery, sent units
  giving way to each other in a loop; a crash once a sidebar column reached 75
  entries (columns now hold 120); and a crash when an explosive crate
  destroyed the unit that drove onto it.
- **LAN games with crates on.** They no longer crash, so crates no longer need
  turning off for LAN play.
- **Units stuck on unreachable destinations.** A unit that cannot reach where
  it was sent no longer retries forever: infantry give up after a few seconds,
  and vehicles stop waiting after a minute without moving.
- **AI building placement.** The AI no longer sits on thousands of credits
  unable to place a building. Two bugs in Westwood's original placement code
  shrank its search to ground its base already covered and threw the building
  away when its preferred area was full; GDI was hit hardest.
- **AI orders survive a cash dip.** An AI building order is kept while income
  is still coming in, instead of being scrapped the moment the money runs out.
- **AI air power.** Allied and Soviet AIs now build a radar dome and a service
  depot without waiting for an enemy air force, so they field aircraft of their
  own. A-10s are no longer built at helipads, where they parked or blew up on
  arrival, and AI planes out of ammunition find their airfield to rearm.
- **AI fire sales.** The AI no longer sells its naval yard, tech centre or
  repair bay at half price whenever its cash dips.
- **AI superweapons respect stealth.** AI Ion Cannon, nuke and Parabomb strikes
  no longer target buildings hidden by a Nod Stealth Generator.
- **AI scouting.** Blind scouts fan out across the start positions instead of
  all heading for one, and an AI that has found no one fires its recon powers
  at unexplored start positions.
- **Per-slot AI difficulty.** When the game holds a stale copy of an earlier
  lobby that looks like the current one, the mod now tells the live one apart
  instead of falling back to the default difficulty (the case DontCryJustDie
  reported).
- **Ships.** A finished ship no longer vanishes when the shipyard's exit is
  blocked; it waits and launches once the way clears.
- **Allied Missile Silo.** Allies can build the Missile Silo again: their own
  Advanced Tech Center meets its prerequisite.
- **GPS satellite in team games.** When the player who launched it loses their
  Tech Center, the reveal it shared goes from their allies too, unless an ally
  has a GPS of their own up.
- **Blossom trees** can no longer be damaged, as in Tiberian Dawn. A damaged
  one used to draw as a white square.
- **GDI and Allied construction yards** play their crane animation when a
  building is placed, and show their damaged art correctly.

### Known limitations
- The AI does not raise Firestorm Defense or build the EMP Cannon, Mobile EMP,
  Mobile Sensor Array, Mobile War Factory or Limpet Drones. A computer TS GDI
  builds no transports or navy, so it cannot ferry an army on maps split by
  water.
- No faction's AI builds walls or gates.
- On maps split by water, the other factions' AIs build transports to ferry
  their armies across, but rarely land a real force yet.
- For a TS GDI player, move and rally markers show the Allied emblem.
- GDI and Nod still hear Red Alert's EVA for "Unable to comply, building in
  progress".
- German and French players hear English voices while the mod is enabled.
- Saved games from earlier versions of the mod will not load in 5.0.0.

## [4.2.1] — 2026-09-26

### Fixed
- **Nod vehicles no longer get stuck at Ready.** After about a hundred vehicles
  had been delivered to Nod Airstrips in one match (counting every Nod player,
  AI included), no more cargo planes came: vehicles sat at Ready for everyone,
  and rebuilding the Airstrip did not help. Airstrips now keep delivering for
  the whole match.

## [4.2.0] — 2026-07-22

### Added
- **On-screen AI difficulty readout.** Match start now shows one line per enemy
  AI with its side, colour and the difficulty actually applied, for example
  "Enemy AI: Nod (Red) - Hard". Previously this readout existed only in dev
  builds. If the per-slot lobby difficulty read ever fails and the AIs fall
  back to the default tier, that is now visible the moment the match starts
  instead of silent.

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
