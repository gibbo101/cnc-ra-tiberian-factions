# ModDB page copy (current: v5.0.0, draft for Luke's review)

**Live page: https://www.moddb.com/mods/tiberian-factions-for-red-alert**
(ModDB serves 403 to automated fetches, so the page state cannot be checked from here. Luke is
the only one who can see what is currently published.)

Paste-ready content for the mod's ModDB page. Luke does everything in-browser; this doc holds
every field's content so page day is copy-paste only. Updated per release.

**Style rule:** no em dashes anywhere in user-facing copy (colons, commas, hyphens instead).

**Not announced anywhere in this copy, by decision:** the stock-campaign compatibility fixes, and
the A* pathfinding internals (engine jargon that means nothing to a player). The Tiberian Sun
walkers were a crate easter egg until 5.0.0; they are now TS GDI's own army and are announced as
such. The crate-only finds are an easter egg: the store pages (Workshop and ModDB) never mention them,
not even as rare tanks. The repo (changelog, README) may name them. Keep it that way on future
releases unless Luke says otherwise.

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
| Icon | Current: `logo.png` (four-faction emblem grid, 1200x1200; `logo-512.png` the pre-scaled icon), which doubles as the Workshop preview. Candidate for 5.0.0: the new title-over-emblems logo in `~/Desktop/Tiberian Factions/tf-logo/` (`logo-512.png`, or `logo-fire-512.png` with the fire title), Luke's call. |
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
<li><b>Five separate tech trees, and capture that matters.</b> Every faction builds its own
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
harms infantry, with a chance of Visceroids from Tiberium deaths. 151 of Red Alert's own
multiplayer maps now mix Tiberium fields with the ore, with lobby thumbnails to match. The 31
Tiberian Dawn maps are out of the mod for now, to save video memory, and are planned to return
as a separate download.</li>
<li><b>Unholy Alliance mode.</b> A lobby option that starts every player, human and AI, with
the Allied, Soviet, GDI and Nod construction yards at once.</li>
<li><b>Crates with surprises.</b> Unit crates turn up more often and draw from every faction's
vehicles.</li>
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
transports or navy on maps split by water. No faction's AI builds walls or gates.</li>
<li>German and French players hear English voices while the mod is enabled.</li>
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
<p>Not endorsed by or affiliated with Electronic Arts.</p>

---

# 5.0.0 release article

**Title:** Version 5.0.0: A Rip in Time

**Summary field (short):** Another Tiberian faction joins the fray! A Chronosphere accident drags GDI
out of the future. A terrible accident, or an insidious plot by Kane?

**Body:**

<p>Another Tiberian faction joins the fray! A Chronosphere accident tears a hole in time and drags GDI out of the future. A terrible accident, or an insidious plot by Kane?</p>
<ul>
<li>Tiberian Sun GDI, a fifth playable faction!</li>
<li>All-new intro movie!</li>
<li>UI overhaul!</li>
<li>Gates and walls for every side!</li>
<li>Tiberium on Red Alert's own maps!</li>
<li>AI improvements!</li>
</ul>

<h2>Tiberian Sun GDI</h2>
<p>Pick TS GDI in the lobby and you start on a Tiberian Sun MCV with a Tiberian Sun army. The
base is its own tree, from the Construction Yard and Power Plant (with turbines) through the War
Factory, Radar, Tech Center and Service Depot to the Upgrade Center and the Dropship Bay. The
infantry are Light Infantry, Disc Throwers, Engineers, Medics, Jumpjet Infantry and the Ghost
Stalker. The armour runs from the Wolverine and Titan to the Hover MLRS, Disruptor, Juggernaut
and Mammoth Mk. I, with Orcas and the Carryall in the air. The Dropship Bay brings down the
Mammoth Mk. II and the Mech Division from orbit.</p>
<p>The support kit is Tiberian Sun's too. Firestorm Defense: build the generator, lay its wall
sections, and one click raises a field that destroys whatever crosses it, your own units
included, and stops enemy shots, for as long as its charge lasts. The EMP Cannon's pulse freezes
vehicles and silences buildings where it lands. The Upgrade Center takes an Ion Cannon uplink, a drop pod node and the Hunter
Seeker, which launches itself at the enemy when it is ready. The Mobile War Factory deploys
into a working war factory, the Mobile Sensor Array shows cloaked enemies, and component
towers take Vulcan, RPG or SAM upgrades.</p>

<h2>Every faction looks like itself</h2>
<p>GDI and Nod now play on Tiberian Dawn's own sidebar, and every faction gets its own radar
crest, sidebar tabs and EVA lines, including lines the game's launcher speaks itself. The
lobby picker shows each faction's emblem and lists every faction. All of it works for every
player in a LAN game, not just the host.</p>

<h2>A new front end</h2>
<p>The mod has its own title, its own startup intro cut to Hell March, a new main menu, a
loading screen with the faction emblems, and lobbies to match.</p>

<h2>Walls and gates</h2>
<p>Every faction has a gate: the GDI gate, the Nod laser gate, the Allied gate, the Soviet Tesla
gate and the Tiberian Sun GDI gate. It opens for your units and shuts behind them. Walls fill a
straight line the way they do in Tiberian Sun and Red Alert 2: place a wall in line with another
of its kind, up to five cells away, and the gap fills in.</p>

<h2>Tiberium on Red Alert's own maps</h2>
<p>151 of Red Alert's official multiplayer maps now mix Tiberium fields with the ore, balanced
so every start gets a fair mix, with lobby thumbnails to match.</p>
<p>The 31 Tiberian Dawn maps are out of the mod for now: they raised video memory use for every
player. They are planned to return as a separate download. Copies installed by earlier versions
are removed from your custom maps.</p>

<h2>Hotkeys for every faction</h2>
<p>The Deploy key works again on every faction's MCVs and transports, and select-all (A) leaves
harvesters and MCVs out of your army, for every player in LAN games too.</p>

<h2>Crates</h2>
<p>Unit crates turn up more often and draw from every faction's vehicles, so anyone can find
anything.</p>

<h2>The AI</h2>
<p>The computer opponents play all five factions, TS GDI included. In 5.0 they field a stronger
economy and build a navy on water maps. More AI work is to come.</p>

<h2>Known limitations</h2>
<p>The TS GDI AI does not use Firestorm Defense or build the EMP Cannon, and builds no
transports or navy on maps split by water. No faction's AI builds walls or gates.</p>

<p>Thanks to <b>hazelnut</b> for the Tiberian Sun GDI emblem and to the <b>OpenTS
Developers</b>, whose OpenTS is the reference for every Tiberian Sun unit in this release.</p>

<p>Download below, or subscribe on the
<a href="https://steamcommunity.com/sharedfiles/filedetails/?id=3729834253">Steam Workshop</a>
for automatic updates. Full changelog on
<a href="https://github.com/gibbo101/cnc-ra-tiberian-factions/blob/main/CHANGELOG.md">GitHub</a>.</p>

---

# 5.0.0 download entry

| Field | Value |
|---|---|
| Name | Tiberian Factions for Red Alert 5.0.0 |
| Filename | `TiberianFactions-v5.0.0.zip` (size: fill in from the GitHub release asset) |
| Source | GitHub release asset, identical file: https://github.com/gibbo101/cnc-ra-tiberian-factions/releases/tag/v5.0.0 |
| Category | Full Version |
| Description | Version 5.0.0: Tiberian Sun GDI joins as a fifth faction, with an all-new intro movie, a UI overhaul and more. Extract into Documents/CnCRemastered/Mods/Red_Alert/ or subscribe on the Steam Workshop. |

---

## Media to upload with the page

Already on the page from 4.0 (the `~/Desktop/TiberianFactionsinRedAlert4.0 media/` folder is no
longer on the Desktop): nod-stealth-generator.mp4, nod-paradrop.mp4, raharv-tdref.mp4,
tdharv-raref.mp4, the GDI and Nod base showcases.

**Wanted for 5.0:** a TS GDI base with the Firestorm field up; the dropship landing a Mammoth
Mk. II; an EMP pulse landing on a column; the new main menu and the lobby faction picker; a gate
in a wall line opening for a unit; an official map with Tiberium beside the ore. Shoot with
`tf_dev_off.flag` present or on the release DLL so dev overlays do not burn in. New captures go
in `~/Desktop/Tiberian Factions/<topic>/`.

## Per-release update checklist (Luke in browser)

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
