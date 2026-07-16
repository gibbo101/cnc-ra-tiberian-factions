# ModDB page copy (draft for first publish, v4.0.0)

Paste-ready content for creating the mod's ModDB page. Luke does the in-browser account/page
creation; this doc holds every field's content so page day is copy-paste only.

**Style rule:** no em dashes anywhere in user-facing copy (colons, commas, hyphens instead).

---

## Page setup choices

| Field | Value |
|---|---|
| Name | Tiberian Factions for Red Alert |
| Game | C&C: Remastered Collection |
| Genre | Real Time Strategy |
| Theme | War |
| Players | Single Player (skirmish vs AI; LAN works with crates off) |
| Development stage | Released |
| License | GPL v3 (DLL source inherited from EA's 2020 source release) |
| Homepage | https://github.com/gibbo101/cnc-ra-tiberian-factions |
| Icon | `logo.png` in the Desktop media folder (four-faction emblem grid, 1200x1200; `logo-512.png` is the pre-scaled icon variant). Same image doubles as the Workshop preview. |
| Tags | command and conquer, red alert, tiberian dawn, gdi, nod, remastered |

## Summary (short field, keep under ~300 chars)

Adds GDI and Nod from Tiberian Dawn as fully playable factions in Red Alert Remastered:
complete tech trees, TD units and superweapons, navies, working skirmish AI, authentic TD
art and sound. Allies vs Soviets vs GDI vs Nod on the same map.

## Description (ModDB supports basic HTML: h2/b/i/ul/li/a)

<p><i>My son asked me who would win if GDI battled the Soviets. Now we can find out.</i></p>

<h2>What this mod adds</h2>
<p>GDI and Nod are not reskins. They are complete factions with their own bases, armies,
navies, superweapons and computer opponents, built from authentic Tiberian Dawn art and
sound, playable alongside the original Allies and Soviets in any skirmish mix.</p>
<ul>
<li><b>Two new factions with full tech trees.</b> GDI: Construction Yard, Power Plants,
Tiberium Refinery, Barracks, Weapons Factory, Communications Center, Advanced Communications,
Helipad, Airfield, Naval Yard and Service Depot, defended by Guard Towers and Advanced Guard
Towers. Nod: Construction Yard, Power Plants, Tiberium Refinery, Hand of Nod, Airstrip,
Communications Center, Temple of Nod, Helipad, Sub Pen, Stealth Generator and Flame Bunker,
defended by Gun Turrets, SAM Sites and the Obelisk of Light.</li>
<li><b>Full TD unit rosters.</b> Infantry from Minigunner to Commando, vehicles from the
Recon Bike to the Mammoth Tank, GDI's Orca and A-10, Nod's Apache, plus each faction's
Harvester and MCV.</li>
<li><b>Navies.</b> GDI fields gunboats, destroyers and cruisers from its Naval Yard; Nod
fields attack and missile submarines from its Sub Pen; both sides share a hovercraft
transport.</li>
<li><b>Superweapons and support powers.</b> GDI's Ion Cannon and GPS satellite, Nod's
Nuclear Strike, spy plane and paratroopers.</li>
<li><b>The Tiberium ecosystem.</b> Tiberium spreads, converts trees into blossom trees and
harms infantry, with a chance of Visceroids from Tiberium deaths.</li>
<li><b>31 Tiberian Dawn skirmish maps</b> in full HD across temperate, winter and desert
theatres.</li>
<li><b>Computer opponents that actually play the factions</b>: full base build-out, economy,
tech, air power and combined-arms armies.</li>
<li><b>Authentic look and sound</b>: TD EVA, unit voices, building and weapon sounds,
including the Obelisk charge-up and the Ion Cannon strike.</li>
<li><b>Quality of life</b>: attack-move, rally points, A* pathfinding, smarter harvesters,
repair bay queueing and extra zoom levels (adapted from CFE Patch Redux, GPL v3).</li>
</ul>

<h2>What's new in 4.0</h2>
<ul>
<li>Navies for GDI and Nod: GDI Naval Yard with gunboat, destroyer and cruiser; Nod Sub
Pen with attack subs and the Temple-guarded Missile Sub; shared hovercraft transport.</li>
<li>GDI Airfield and the A-10 Warthog, flying TD-authentic napalm bombing runs: three
passes per sortie, then home to rearm.</li>
<li>Nod Stealth Generator: cloaks nearby friendly buildings and units, with the generator
itself as the always-visible weak point. Stealth detectors reveal what they pass and
cloaked defences ambush-fire.</li>
<li>Nod Flame Bunker: an anti-infantry flame emplacement.</li>
<li>Support powers: GDI GPS satellite, Nod spy plane and paratroopers (a real,
shoot-downable C-17 dropping TD minigunners).</li>
<li>Balance: Orca and Apache at full attack-helicopter parity, artillery ranges extended,
GDI/Nod MCV and Construction Yard at RA parity, plus an air-aware AI that scales its air
force to the strongest opponent.</li>
</ul>

<h2>How to play</h2>
<p>Easiest: subscribe on the
<a href="https://steamcommunity.com/sharedfiles/filedetails/?id=3729834253">Steam Workshop</a>
and enable "Tiberian Factions for Red Alert" from the mod list when launching Red Alert in
C&amp;C Remastered. Or download the release zip (here or from GitHub) and extract it into
<b>Documents/CnCRemastered/Mods/Red_Alert/</b>. Start a skirmish and GDI and Nod appear as
selectable factions for you and the AI.</p>
<p><b>Play on HD (Remastered) graphics.</b> Classic graphics mode is not supported: the TD
terrain and several units have no classic art path.</p>

<h2>Compatibility and known limitations</h2>
<ul>
<li>This is a DLL mod. It cannot run alongside any other mod that also replaces
RedAlert.dll (for example CFE Patch Redux). Disable other DLL mods first.</li>
<li>Single-player skirmish is the tested mode. LAN works but crates have caused crashes,
so turn crates off for LAN play.</li>
<li>The select-all (A) and deploy (/) hotkeys only recognise Allied/Soviet harvesters and
MCVs, a launcher limitation a mod cannot reach. Drag-select your army and click the MCV to
deploy it.</li>
</ul>

<h2>Source and licensing</h2>
<p>Source on <a href="https://github.com/gibbo101/cnc-ra-tiberian-factions">GitHub</a>.
Built on <a href="https://github.com/TheAssemblyArmada/Vanilla-Conquer">Vanilla Conquer</a>.
DLL source is GPL v3, inherited from EA's 2020 Remastered Collection source release.</p>

<h2>Acknowledgements</h2>
<p>This project does not bundle these mods, but their work shaped the approach. Thanks to
<b>Reilsss</b> (Command &amp; Conquer in Red Alert, faction inspiration),
<b>DontCryJustDie</b> (TD-Assets, TD art and audio in the RA engine),
<b>JohnnyJigglez</b> (EMC, extensibility reference) and
<b>ChthonVII</b> with cfehunter and Root-Core (CFE Patch Redux, source of the rally points,
harvester, repair bay and zoom features, GPL v3).</p>
<p>Not endorsed by or affiliated with Electronic Arts.</p>

---

## Media to upload with the page

From `~/Desktop/TiberianFactionsinRedAlert4.0 media/`:
- Videos: nod-stealth-generator.mp4, nod-paradrop.mp4, raharv-tdref.mp4, tdharv-raref.mp4
- Screenshots: GDI base showcase, Nod base (uncloaked + cloaked pair), plus any further keepers.

## First-publish checklist (Luke in browser)

1. Create/log into ModDB account.
2. Add Mod (moddb.com/mods/add), attach to game "C&C: Remastered Collection".
3. Fill fields from the table above; paste summary + description.
4. Upload icon + media; add the release zip as a Download (mirrors the GitHub release asset).
5. Submit for authorisation (ModDB staff approve new pages, usually within a day or two).
