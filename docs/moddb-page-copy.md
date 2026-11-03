# ModDB page copy (current: v5.7.0)

**Status:** Reference. The ModDB page text for the current release, 5.7.0.

**Live page: https://www.moddb.com/mods/tiberian-factions-for-red-alert**
(ModDB serves 403 to automated fetches, so the live page can only be checked in a browser.)

Paste-ready content for the mod's ModDB page, which is edited by hand in the browser; this doc
holds every field's content so page day is copy-paste only. Updated per release.

**Style rule:** no em dashes anywhere in user-facing copy (colons, commas, hyphens instead).

**Not announced anywhere in this copy, by decision:** the stock-campaign compatibility fixes, and
the A* pathfinding internals (engine jargon that means nothing to a player). The Tiberian Sun
walkers were a crate easter egg until 5.0.0; they are now TS GDI's own army and are announced as
such. The crate-only finds are an easter egg: the store pages (Workshop and ModDB) never mention them,
not even as rare tanks. The repo (changelog, README) may name them. Keep it that way on future
releases.

---

## Page setup choices

| Field | Value |
|---|---|
| Name | Tiberian Factions for Red Alert |
| Game | C&C: Remastered Collection |
| Genre | Real Time Strategy |
| Theme | War |
| Players | Single Player (skirmish vs AI; LAN works) |
| Development stage | Released |
| License | GPL v3 (DLL source inherited from EA's 2020 source release) |
| Homepage | https://github.com/gibbo101/cnc-ra-tiberian-factions |
| Icon | `~/Desktop/Tiberian Factions/tf-logo/logo-fire-512.png` (the fire title over the six faction emblems; the 1200x1200 `logo-fire-draft.png` is the Workshop preview from 5.0.0). |
| Tags | command and conquer, red alert, tiberian dawn, tiberian sun, gdi, nod, remastered |

## Summary (short field, keep under ~300 chars)

Adds GDI and Nod from Tiberian Dawn, and GDI from Tiberian Sun, as fully playable factions in
Red Alert Remastered: complete tech trees, authentic units and superweapons, working skirmish AI,
authentic art and sound. Five factions on the same map.

## Description (ModDB supports basic HTML: h2/b/i/ul/li/a)

<p><i>My son asked me who would win if GDI battled the Soviets. Now we can find out.</i></p>

<h2>What this mod adds</h2>
<p>GDI and Nod are not reskins. They are complete factions with their own bases, armies,
navies, superweapons and computer opponents, built from authentic Tiberian Dawn art and
sound. Tiberian Sun's GDI joins them as a fifth faction. All five are playable alongside the
original Allies and Soviets in any skirmish mix.</p>
<ul>
<li><b>Two Tiberian Dawn factions with full tech trees.</b> GDI: Construction Yard, Power Plants,
Tiberium Refinery, Barracks, Weapons Factory, Communications Center, Advanced Communications,
Helipad, Airfield, Naval Yard and Service Depot, defended by Guard Towers and Advanced Guard
Towers. Nod: Construction Yard, Power Plants, Tiberium Refinery, Hand of Nod, Airstrip,
Communications Center, Temple of Nod, Helipad, Sub Pen, Stealth Generator and Flame Bunker,
defended by Gun Turrets, SAM Sites and the Obelisk of Light.</li>
<li><b>Tiberian Sun GDI, a fifth faction.</b> Its own Tiberian Sun base, from the Construction
Yard to the Upgrade Center and Dropship Bay, and its own army: Light Infantry, Disc Throwers,
Medics, Jumpjet Infantry and the Ghost Stalker; Wolverines, Titans, Hover MLRS, Disruptors,
Juggernauts and the Mammoth Mk. I; Orcas and the Carryall; and the Mammoth Mk. II, delivered by
dropship. It defends with component towers that take Vulcan, RPG or SAM upgrades, and with
Firestorm Defense.</li>
<li><b>Separate tech trees.</b> Every faction builds its own
Construction Yard, MCV, War Factory and Helipad. Capture a rival construction yard and you
get that faction's arsenal, so an Allied commander who takes a Nod yard can start building
Nod. Only low tier infrastructure is shared; barracks, war factories, helipads, naval yards,
airfields, radar and tech centres are faction identity.</li>
<li><b>Full TD unit rosters.</b> Infantry from Minigunner to Commando, vehicles from the
Recon Bike to the Mammoth Tank, GDI's Orca and A-10, Nod's Apache, plus each faction's
Harvester and MCV.</li>
<li><b>Navies.</b> GDI fields gunboats, destroyers and cruisers from its Naval Yard; Nod
fields attack and missile submarines from its Sub Pen.</li>
<li><b>Superweapons and support powers.</b> GDI's Ion Cannon and GPS satellite; Nod's
Nuclear Strike, spy plane and paratroopers; and for TS GDI, its own Ion Cannon, the EMP Cannon,
the Hunter Seeker, drop pods and Firestorm Defense.</li>
<li><b>Every faction looks like itself.</b> GDI and Nod play on Tiberian Dawn's sidebar, and
every faction gets its own radar crest, sidebar tabs and EVA voice, in LAN games too. The lobby
picker shows each faction's emblem.</li>
<li><b>A new front end.</b> The Tiberian Factions title, intro, main menu, loading screen and
lobbies.</li>
<li><b>Walls and gates.</b> Every faction has a gate that opens for its own units, and
placing a wall in line with another of its kind, up to five cells away, fills the gap.</li>
<li><b>The Tiberium ecosystem.</b> Tiberium spreads, converts trees into blossom trees and
harms infantry, with a chance of Visceroids from Tiberium deaths. Most of Red Alert's own
skirmish maps now mix Tiberium with ore.</li>
<li><b>Unholy Alliance mode.</b> A lobby option that starts every player, human and AI, with
an Allied, Soviet, GDI, Nod and Tiberian Sun GDI MCV.</li>
<li><b>Crates.</b> The unit pool now covers every faction.</li>
<li><b>Computer opponents for all five factions</b>, each AI on its own Easy, Medium or Hard
setting from its lobby slot.</li>
<li><b>Authentic look and sound</b>: Tiberian Dawn and Tiberian Sun EVA, unit voices, building
and weapon sounds, including the Obelisk charge-up and the Ion Cannon strike.</li>
<li><b>Quality of life</b>: attack-move, rally points, A* pathfinding, smarter harvesters,
repair bay queueing and extra zoom levels (adapted from CFE Patch Redux, GPL v3). The Deploy key
works on every faction's MCVs and transports, and select-all leaves harvesters and MCVs out.</li>
</ul>

<h2>How to play</h2>
<p>Easiest: subscribe on the
<a href="https://steamcommunity.com/sharedfiles/filedetails/?id=3729834253">Steam Workshop</a>
and enable "Tiberian Factions for Red Alert" from the mod list when launching Red Alert in
C&amp;C Remastered. Or download the release zip (here or from GitHub) and extract it into
<b>Documents/CnCRemastered/Mods/Red_Alert/</b>. Start a skirmish and pick GDI, Nod or TS GDI
from the faction list, for yourself and for the AI.</p>
<p><b>This mod is HD (Remastered) graphics only.</b> Its units, buildings and terrain have no
classic art, so classic mode is locked out while the mod is enabled rather than left to render
badly.</p>

<h2>Compatibility and known limitations</h2>
<ul>
<li>This is a DLL mod. It cannot run alongside any other mod that also replaces
RedAlert.dll (for example CFE Patch Redux). Disable other DLL mods first.</li>
<li>Single-player skirmish is the main tested mode. LAN works, and every player gets their own
faction's crest, EVA and hotkeys.</li>
<li>Saved games from earlier versions of the mod will not load in 5.0.</li>
<li>The TS GDI AI does not use Firestorm Defense or build the EMP Cannon, and builds no
transports or navy on maps split by water (a TS GDI navy may come later). No faction's AI
builds walls or gates.</li>
<li>German and French players hear English voices while the mod is enabled.</li>
</ul>

<h2>Planned</h2>
<ul>
<li><b>Tiberian Sun Nod</b> as a playable faction.</li>
<li><b>A balance pass for TS GDI and TS Nod.</b> 5.0 uses Tiberian Sun's exact values.</li>
<li><b>Smarter AI</b>, including naval invasions.</li>
<li><b>The Tiberian Dawn maps</b> back as a separate download.</li>
<li><b>GDI and Nod campaigns.</b></li>
<li><b>Co-op missions</b> for two players.</li>
</ul>

<h2>My other C&amp;C projects</h2>
<ul>
<li><a href="https://github.com/gibbo101/renegade-pad">Renegade Pad</a>: C&amp;C Renegade's campaign played like a console shooter on the Steam Deck, with a full controller scheme.</li>
<li><a href="https://github.com/gibbo101/opents-pad">OpenTS Pad</a>: OpenTS, the open-source Tiberian Sun, on a controller, in the style of Red Alert: Retaliation on the PlayStation.</li>
<li><a href="https://github.com/gibbo101/cnc-map-editor">C&amp;C Remastered Map Editor</a>: a Linux-native map editor for Red Alert and Tiberian Dawn that understands mods, Tiberian Factions included.</li>
<li><a href="https://github.com/gibbo101/ps1-lan-link">PS1 Link Cable</a>: two-player link-cable play between two Steam Decks over wifi, for Red Alert: Retaliation, Dune 2000 and more.</li>
</ul>

<h2>Source and licensing</h2>
<p>Source on <a href="https://github.com/gibbo101/cnc-ra-tiberian-factions">GitHub</a>.
Built on <a href="https://github.com/TheAssemblyArmada/Vanilla-Conquer">Vanilla Conquer</a>.
DLL source is GPL v3, inherited from EA's 2020 Remastered Collection source release.</p>

<h2>Credits</h2>
<p><b>Westwood Studios / EA</b> (Tiberian Dawn, Red Alert, Tiberian Sun and Red Alert 2),
<b>EA Los Angeles</b> (Command &amp; Conquer 3: Tiberium Wars) and <b>EA / Petroglyph</b>
(the Remastered Collection). <b>The Assembly Armada</b> (Vanilla Conquer, the DLL build base).
<b>The OpenTS Developers</b> (<a href="https://github.com/OpenTS-Developers/OpenTS">OpenTS</a>,
the reference for Tiberian Sun's units, weapons and rules). <b>hazelnut</b> (the Tiberian Sun
GDI emblem, via <a href="https://www.steamgriddb.com/">SteamGridDB</a>). <b>Archivo Black</b>
(SIL Open Font License), the lettering in the Tiberian Factions title.</p>

<h2>Acknowledgements</h2>
<p>This project does not bundle these mods, but their work shaped the approach. Thanks to
<b>Reilsss</b> (Command &amp; Conquer in Red Alert, faction inspiration),
<b>DontCryJustDie</b> (TD-Assets, TD art and audio in the RA engine, and the lobby record
layout behind the per slot AI difficulty),
<b>JohnnyJigglez</b> (EMC, extensibility reference),
<b>Bast75</b> and <b>xXMini FrankiXx</b> (skirmish AI ideas) and
<b>ChthonVII</b> with cfehunter and Root-Core (CFE Patch Redux, source of the rally points,
harvester, repair bay and zoom features, GPL v3).</p>
<p>EA has not endorsed and does not support this product.</p>

---

# 5.7.0 release article

The page's previous release was 5.0.0, so this article covers 5.5 to 5.7.

**Title:** Version 5.7.2: Command Your Way

**Summary field (short):** Five factions, two eras and one rift in time. Now you set the rules of
engagement: every change Tiberian Factions makes to how Red Alert plays can be switched back to vanilla.

**Body:**

<p><b>EA has not endorsed and does not support this product.</b></p>

<p>Five factions, two eras and one rift in time. Since our last ModDB update, Tiberian Sun GDI has
been rebuilt in HD, Tiberian Dawn's own theatres have come through the Chronosphere, and now you set
the rules of engagement. Here is everything from 5.5 to 5.7.</p>
<ul>
<li>Every Tiberian Sun GDI building, unit and soldier rebuilt in HD!</li>
<li>All six theatres, with Tiberian Dawn's 34 skirmish maps!</li>
<li>A Faction Encyclopedia and an ADD-ONS screen on the main menu!</li>
<li>Pathfinding twice as fast!</li>
<li>New GAMEPLAY settings: switch any of the mod's gameplay changes back to vanilla!</li>
<li>Classic AI: face Red Alert's own AI, taught to build every faction's base!</li>
</ul>

<h2>5.5: Tiberian Sun rises in HD</h2>
<p>GDI's arsenal from the future came through the Chronosphere's rift rough around the edges. Now
every building, vehicle and soldier stands rebuilt, sharper than ever. Kane will not be pleased.</p>
<ul>
<li><b>Tiberian Sun GDI in HD:</b> every TS GDI building, vehicle, aircraft and infantry unit
rebuilt from 3D models at Remastered's resolution, on whole map cells.</li>
<li><b>HD sidebar cameos</b> for every TS GDI unit and building.</li>
<li><b>New railgun shots</b> for the Mammoth Mk. II and the Ghost Stalker, and the Mammoth Mk. II
now fires from its rail gun cannons.</li>
<li><b>Mammoth Mk. I Reserve:</b> the Dropship Bay lands two Mammoth Mk. Is, and tells you when its
reload is done.</li>
<li><b>Load Game knows a save it can't load:</b> a save from another version, from vanilla or another
mod is greyed out with the reason instead of crashing the game.</li>
<li>The main menu shows the Tiberian Factions version.</li>
<li>The Allied and Soviet campaigns are removed while the mod is enabled. Disable Tiberian Factions
to play them.</li>
<li><b>Changes:</b> some TS buildings take their correct names, TS GDI's starting units are adjusted,
the TS Service Depot repairs at Tiberian Sun's rate, and the Orca Bomber lays its bombs in a line
across the target.</li>
<li><b>Fixes:</b> GDI and Nod build slower on low power; spies read every faction's power and money;
a player isn't out while a building they hold still stands; a damaged harvester docks at any
refinery type; the TS Engineer shows the capture cursor over any building it can take; "Unable to
comply" speaks in your side's voice; and more.</li>
</ul>
<p>The Tiberian Sun art, sounds and EVA now come as their own pack, <b>Tiberian Sun HD Assets</b>.
Without it the mod still plays, but TS GDI is locked. The download below has both folders in it.</p>

<h2>5.6: Six theatres, an encyclopedia and a faster game</h2>
<ul>
<li><b>Six theatres:</b> Tiberian Dawn's desert, temperate and winter join Red Alert's temperate,
snow and interior, and all 34 of Tiberian Dawn's skirmish maps are back in the Official list with
their own thumbnails.</li>
<li><b>Faction Encyclopedia:</b> a tab per faction with its units and structures, each with its
picture, its manual description and its in-game stats.</li>
<li><b>ADD-ONS:</b> get and switch on the asset packs without leaving the game. The main menu points
at any pack that isn't on.</li>
<li><b>Performance:</b> pathfinding about twice as fast.</li>
<li><b>Changes:</b> Concrete Wall costs 100, as in the campaigns; TS GDI builds no sandbags, as in
Tiberian Sun; Unholy Alliance starts every player with a TS GDI MCV too; and the GDI Mammoth Tank
needs GDI's own Repair Facility.</li>
<li><b>Fixes from your reports:</b> paused units resume when clicked again; units come only from
their own faction's factory; placing a turret on a component tower repairs the tower; a deployed
Juggernaut stays put; another mod's rules.ini no longer breaks Tiberian Factions; and in LAN games
H, the deploy key and building sounds work for every player.</li>
<li>The Faction Encyclopedia shows Tiberian Dawn's units and buildings as they look in game.</li>
</ul>

<h2>5.7: Command your way</h2>
<p>TIBERIAN FACTIONS SETTINGS gains GENERAL and GAMEPLAY pages. Every switch starts on, so the mod
plays as it always has until you change one.</p>
<ul>
<li><b>Classic AI:</b> take on Red Alert's own AI, taught to build every faction's own buildings,
with vanilla's attacks, selling and single difficulty.</li>
<li><b>TF AI:</b> switch fair fog and scouting, attack waves, naval play and the Allied and Soviet
early radar, each on its own.</li>
<li><b>Units:</b> switch A* pathfinding, giving way in narrow passages, and the harvester fixes.</li>
<li><b>Sidebar:</b> sort cameos by cost or in arrival order, and show or hide faction badges.</li>
<li>In LAN games the host's gameplay settings apply to everyone, and each player keeps their own
sidebar.</li>
<li>Every switch is saved in Documents/CnCRemastered/tf_settings.ini, so you can set them by hand
too.</li>
<li>On ultrawide screens the main menu keeps its shape, and clicks land where you point.</li>
</ul>

<h2>Installing</h2>
<p>Extract the zip into <b>Documents/CnCRemastered/Mods/Red_Alert/</b>. It holds two folders,
Tiberian Factions and Tiberian Sun HD Assets: enable both in the game's mod list, then restart the
game. Or subscribe to both on the
<a href="https://steamcommunity.com/sharedfiles/filedetails/?id=3729834253">Steam Workshop</a>
for automatic updates.</p>
<p>Saves from 5.0 and earlier won't load; Load Game greys them out.</p>

<p>Full changelog on
<a href="https://github.com/gibbo101/cnc-ra-tiberian-factions/blob/main/CHANGELOG.md">GitHub</a>.</p>

---

# 5.7.0 download entry

| Field | Value |
|---|---|
| Name | Tiberian Factions for Red Alert 5.7.2 |
| Filename | `TiberianFactions-5.7.2.zip`, 518,797,269 bytes (495 MB) |
| Category | Full Version |
| Description | Version 5.7.2, with Tiberian Sun HD Assets 1.2 included. Extract both folders into Documents/CnCRemastered/Mods/Red_Alert/, enable both, then restart the game. |

---

## Media to upload with the page

Already on the page from 4.0 (the `~/Desktop/TiberianFactionsinRedAlert4.0 media/` folder is no
longer on the Desktop): nod-stealth-generator.mp4, nod-paradrop.mp4, raharv-tdref.mp4,
tdharv-raref.mp4, the GDI and Nod base showcases.

**New for 5.0 (captured 2026-10-04):** `~/Desktop/Tiberian Factions/screenshots-5.0.0/` (full-size PNGs;
JPG copies under 1 MB in `jpg/`): the main menu, skirmish lobby, loading screen, the dropship over
a Mammoth Mk. II, TS units at a Tiberium crossroads, a TS GDI base with Firestorm and its gate, a
Soviet base with the Tesla gate. Not captured: an EMP pulse.

**Intro video:** https://youtu.be/rqk9Q1sgvAc (YouTube, 2026-10-04; also on the Workshop page, whose
media only takes YouTube links). The 1080p MP4 for ModDB is rendered from the intro pipeline's own
frames and music (`intro_cut.py ... frames`, then H.264 CRF 16 + AAC), not decoded from the Bink.

**HD showcase GIFs:** `scripts/moddb_showcase.py OUT_DIR [SUBJECT ...]` cuts the TS GDI art as the
game draws it, in GDI gold: the release's TS-era frames (`--old-rev`, default v5.0.0) beside the HD
frames, and the HD frames alone. Only art signed off as final goes in a cut.

## Per-release update checklist (in the browser)

1. Edit the mod page: replace the description, refresh the limitations list.
2. Post the release article (Articles > Add Article, category News).
3. Add the release zip as a Download, using the entry table above.
4. Upload any new media.

## First-publish checklist (done for 4.0.0, kept for reference)

1. Create/log into ModDB account.
2. Add Mod (moddb.com/mods/add), attach to game "C&C: Remastered Collection".
3. Fill fields from the table above; paste summary + description.
4. Upload icon + media; add the release zip as a Download (mirrors the GitHub release asset).
5. Submit for authorisation (ModDB staff approve new pages, usually within a day or two).
