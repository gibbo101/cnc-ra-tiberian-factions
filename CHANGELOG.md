# Changelog

All notable changes to **Tiberian Factions for Red Alert** are documented here.

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
