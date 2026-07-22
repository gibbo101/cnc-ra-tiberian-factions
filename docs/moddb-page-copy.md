# ModDB page copy (current: v4.1.0)

**Live page: https://www.moddb.com/mods/tiberian-factions-for-red-alert**
(ModDB serves 403 to automated fetches, so the page state cannot be checked from here. Luke is
the only one who can see what is currently published.)

Paste-ready content for the mod's ModDB page. Luke does everything in-browser; this doc holds
every field's content so page day is copy-paste only. Updated per release.

**Style rule:** no em dashes anywhere in user-facing copy (colons, commas, hyphens instead).

**Not announced anywhere in this copy, by decision:** the Tiberian Sun crate walkers (an easter
egg, and announcing it defeats the point) and the stock-campaign compatibility fixes. The A*
pathfinding internals are left out too: engine jargon that means nothing to a player. Keep it
that way on future releases unless Luke says otherwise.

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
<li><b>Four separate tech trees, and capture that matters.</b> Every faction builds its own
Construction Yard, MCV, War Factory and Helipad. Capture a rival construction yard and you
get that faction's arsenal, so an Allied commander who takes a Nod yard can start building
Nod. Only low tier infrastructure is shared; barracks, war factories, helipads, naval yards,
airfields, radar and tech centres are faction identity.</li>
<li><b>Full TD unit rosters.</b> Infantry from Minigunner to Commando, vehicles from the
Recon Bike to the Mammoth Tank, GDI's Orca and A-10, Nod's Apache, plus each faction's
Harvester and MCV.</li>
<li><b>Navies.</b> GDI fields gunboats, destroyers and cruisers from its Naval Yard; Nod
fields attack and missile submarines from its Sub Pen.</li>
<li><b>Superweapons and support powers.</b> GDI's Ion Cannon and GPS satellite, Nod's
Nuclear Strike, spy plane and paratroopers.</li>
<li><b>The Tiberium ecosystem.</b> Tiberium spreads, converts trees into blossom trees and
harms infantry, with a chance of Visceroids from Tiberium deaths.</li>
<li><b>31 Tiberian Dawn skirmish maps</b> in full HD across temperate, winter and desert
theatres.</li>
<li><b>Unholy Alliance mode.</b> A lobby option that starts every player, human and AI, with
all four factions' construction yards at once.</li>
<li><b>Computer opponents that actually play the factions</b>: full base build-out, economy,
tech, air power and combined-arms armies, each AI on its own Easy, Medium or Hard setting
from its lobby slot.</li>
<li><b>Authentic look and sound</b>: TD EVA, unit voices, building and weapon sounds,
including the Obelisk charge-up and the Ion Cannon strike.</li>
<li><b>Quality of life</b>: attack-move, rally points, A* pathfinding, smarter harvesters,
repair bay queueing and extra zoom levels (adapted from CFE Patch Redux, GPL v3).</li>
</ul>

<h2>How to play</h2>
<p>Easiest: subscribe on the
<a href="https://steamcommunity.com/sharedfiles/filedetails/?id=3729834253">Steam Workshop</a>
and enable "Tiberian Factions for Red Alert" from the mod list when launching Red Alert in
C&amp;C Remastered. Or download the release zip (here or from GitHub) and extract it into
<b>Documents/CnCRemastered/Mods/Red_Alert/</b>. Start a skirmish and GDI and Nod appear as
selectable factions for you and the AI.</p>
<p><b>This mod is HD (Remastered) graphics only.</b> The TD terrain and several units have no
classic art path, so from 4.1 classic mode is locked out while the mod is enabled rather than
left to render badly.</p>

<h2>Compatibility and known limitations</h2>
<ul>
<li>This is a DLL mod. It cannot run alongside any other mod that also replaces
RedAlert.dll (for example CFE Patch Redux). Disable other DLL mods first.</li>
<li>Single-player skirmish is the tested mode. LAN works but crates have caused crashes,
so turn crates off for LAN play.</li>
<li>The deploy hotkey no longer works for any faction's MCV, now that all four factions field
their own MCV type. This is a launcher limitation a mod cannot reach. Select the MCV and click
it to deploy: the deploy cursor still works. The select-all (A) key also grabs harvesters and
MCVs, so drag-select your army instead.</li>
</ul>

<h2>Source and licensing</h2>
<p>Source on <a href="https://github.com/gibbo101/cnc-ra-tiberian-factions">GitHub</a>.
Built on <a href="https://github.com/TheAssemblyArmada/Vanilla-Conquer">Vanilla Conquer</a>.
DLL source is GPL v3, inherited from EA's 2020 Remastered Collection source release.</p>

<h2>Acknowledgements</h2>
<p>This project does not bundle these mods, but their work shaped the approach. Thanks to
<b>Reilsss</b> (Command &amp; Conquer in Red Alert, faction inspiration),
<b>DontCryJustDie</b> (TD-Assets, TD art and audio in the RA engine, and the lobby record
layout behind the per slot AI difficulty),
<b>JohnnyJigglez</b> (EMC, extensibility reference) and
<b>ChthonVII</b> with cfehunter and Root-Core (CFE Patch Redux, source of the rally points,
harvester, repair bay and zoom features, GPL v3).</p>
<p>Not endorsed by or affiliated with Electronic Arts.</p>

---

# 4.1.0 release article

**Title:** Version 4.1.0: the groundwork update

**Summary field (short):** Every faction now builds its own construction yard, war factory and
helipad, capturing one hands you that side's arsenal, and the skirmish AI gets its air force and
its per-slot difficulty back.

**Body:**

<p>4.1.0 is a groundwork release. Most of it is under the hood, but the part you will notice
first is that the four factions are now genuinely separate.</p>

<h2>Every faction builds its own base</h2>
<p>GDI, Nod, the Allies and the Soviets each have their own Construction Yard, MCV, War Factory
and Helipad as distinct types rather than shared ones wearing different art. The payoff is
capture: take a rival construction yard and you get that faction's tech tree, so an Allied
commander who captures a Nod yard can start building Nod. Prerequisites were tightened to match.
Power, refineries and repair bays are shared infrastructure; barracks, war factories, helipads,
naval yards, airfields, radar and tech centres are faction identity and no longer substitute for
each other.</p>
<p>Once you are producing from more than one faction, the sidebar cameos start carrying emblems
showing which of your factions builds each entry, and the whole sidebar sorts into faction
blocks: shared buildables first, then Allied, Soviet, GDI and Nod, each in tech order. In an
ordinary single-faction match every badge would say the same thing, so you get the plain art.</p>

<h2>Unholy Alliance</h2>
<p>A new entry in the lobby Mode dropdown. Every player, human and AI, starts with all four
factions' construction yards. If you have ever wanted to field an Obelisk, a Tesla Coil and an
Advanced Guard Tower in the same base, this is the mode.</p>

<h2>The AI</h2>
<p>Two real fixes. Each AI now takes its own Easy, Medium or Hard setting from the lobby slot
instead of quietly falling back to all Hard after the first match of a session, in skirmish and
LAN alike. And the AI builds air production again once its ground economy is established: it had
not built a helipad or an airstrip since 4.0.0, which took helicopters and planes out of its
army entirely. Alongside those: scouting under fair fog, a fix for Nod Temple and Stealth
Generator build starvation, tier 2 buildings held behind an established economy, and harvesters
that retreat home when idle.</p>
<p>The per slot difficulty fix came out of a back and forth with <b>DontCryJustDie</b>, who
published the lobby record layout that made the setting readable in the first place.</p>

<h2>Also in this release</h2>
<p>Classic graphics mode is locked out while the mod is enabled. The mod is HD only and always
has been, so this stops its content being dropped into a renderer it has no art for. The
skirmish music rotation is up to 107 tracks.</p>

<p>Download below, or subscribe on the
<a href="https://steamcommunity.com/sharedfiles/filedetails/?id=3729834253">Steam Workshop</a>
for automatic updates. Full changelog on
<a href="https://github.com/gibbo101/cnc-ra-tiberian-factions/blob/main/CHANGELOG.md">GitHub</a>.</p>

---

# 4.1.0 download entry

| Field | Value |
|---|---|
| Name | Tiberian Factions for Red Alert 4.1.0 |
| Filename | `TiberianFactions-v4.1.0.zip` (599 MB) |
| Source | GitHub release asset, identical file: https://github.com/gibbo101/cnc-ra-tiberian-factions/releases/tag/v4.1.0 |
| Category | Full Version |
| Description | Version 4.1.0. Separated tech trees for all four factions, capture hands over the arsenal, the Unholy Alliance mode, faction badges and faction-block sorting on the sidebar, per slot AI difficulty, and the AI's air force restored. Extract into Documents/CnCRemastered/Mods/Red_Alert/ or subscribe on the Steam Workshop. |

---

## Media to upload with the page

From `~/Desktop/TiberianFactionsinRedAlert4.0 media/`:
- Videos: nod-stealth-generator.mp4, nod-paradrop.mp4, raharv-tdref.mp4, tdharv-raref.mp4
- Screenshots: GDI base showcase, Nod base (uncloaked + cloaked pair), plus any further keepers.

**Wanted for 4.1:** a four-yards-in-one-base shot from Unholy Alliance, and a sidebar shot with
the faction badges visible (needs a captured rival production building, or Unholy Alliance).
Shoot with `tf_dev_off.flag` present or on the release DLL so dev overlays do not burn in.

## Per-release update checklist (Luke in browser)

1. Edit the mod page: replace the "What's new" section, refresh the limitations list.
2. Post the release article (Articles > Add Article, category News).
3. Add the release zip as a Download, using the entry table above.
4. Upload any new media.

## First-publish checklist (done for 4.0.0, kept for reference)

1. Create/log into ModDB account.
2. Add Mod (moddb.com/mods/add), attach to game "C&C: Remastered Collection".
3. Fill fields from the table above; paste summary + description.
4. Upload icon + media; add the release zip as a Download (mirrors the GitHub release asset).
5. Submit for authorisation (ModDB staff approve new pages, usually within a day or two).
