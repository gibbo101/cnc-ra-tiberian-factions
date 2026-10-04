# Tiberian Factions for Red Alert

A mod for **Command & Conquer: Red Alert Remastered** that adds **GDI** and **Nod**, the two factions from *Tiberian Dawn*, and **GDI from *Tiberian Sun***, as fully playable sides alongside the original Allies and Soviets. Pick any of the five in skirmish and fight them all on the same map: **Allies vs Soviets vs GDI vs Nod vs Tiberian Sun GDI**.

## What this mod adds

GDI and Nod aren't reskins. They're complete factions with their own bases, armies, navies, superweapons, and computer opponents, built from authentic Tiberian Dawn art and sound.

**Two new factions, each with their own tech tree:**

- **GDI:** Construction Yard, Power Plants, Tiberium Refinery, Barracks, Weapons Factory, Communications Center, Advanced Communications, Helipad, Airfield, Naval Yard, and a Service Depot that repairs vehicles. Defended by Guard Towers and Advanced Guard Towers.
- **Nod:** Construction Yard, Power Plants, Tiberium Refinery, Hand of Nod, Airstrip, Communications Center, Temple of Nod, Helipad, Sub Pen, and a Stealth Generator that cloaks nearby units and buildings. Defended by Gun Turrets, SAM Sites, Flame Bunkers, and the laser-firing Obelisk of Light.

**Full unit rosters:**

- **Infantry:** Minigunner, Grenadier, Rocket Soldier, Flamethrower, Chem Warrior, Engineer, and the Commando.
- **Vehicles:** Medium Tank, Light Tank, Mammoth Tank, Flame Tank, Recon Bike, Hum-vee, Buggy, APC, MLRS, SSM Launcher, Artillery, plus the Harvester and Mobile Construction Vehicle.
- **Aircraft:** GDI's Orca and A-10 Warthog (napalm bombing runs from the Airfield), and Nod's Apache.
- **Navies:** GDI's Gunboat, Destroyer, and Cruiser; Nod's Attack Submarine and Missile Sub.

**Superweapons and support powers:** GDI's **Ion Cannon** and GPS satellite; Nod's **Nuclear Strike**, Spy Plane, and Paratroopers.

**Tiberian Sun GDI, a fifth faction.** Its own tech tree, army, and superweapons, in Tiberian Sun's own art and sound: Light Infantry, Disc Throwers, Medics, Ghost Stalkers and Jumpjet Infantry; Wolverines, Titans, the Disruptor, the Hover MLRS, the Juggernaut and the Amphibious APC; Orcas and the Carryall; the Mammoth Mk. II and the Mech Division delivered by dropship. Its Upgrade Center hosts the Tiberian Sun **Ion Cannon**, **drop pods** and the **Hunter Seeker**, alongside **Firestorm Defense**, the **EMP Cannon**, component towers with Vulcan, RPG and SAM turrets, and the Mobile War Factory, Sensor Array, EMP and Limpet Drone.

**Every faction looks and sounds like itself.** GDI and Nod play on Tiberian Dawn's own HUD, and each faction has its own radar crest, sidebar tab icons, and EVA lines, in LAN games too. The lobby's faction picker shows each faction's emblem.

**A new front end:** the Tiberian Factions title, main menu, intro, loading screen, and lobbies.

**Walls and gates for every faction.** Each faction builds its own gate, and walls placed in a line fill the gap between them.

**Every faction keeps its own tree, and capturing changes hands.** GDI, Nod, Allies, and Soviets each build their own Construction Yard, MCV, War Factory, and Helipad. Capture a rival's yard or factory and you can build that faction's arsenal too, with badges on the cameos showing which of your factions builds what. The **Unholy Alliance** skirmish mode starts every player with an Allied, Soviet, GDI, and Nod MCV.

**Tiberium.** Green crystal fields alongside Red Alert's ore, worth the same to a harvester. They grow and spread, hurt infantry who walk through them, and infantry who die in them can rise again as visceroids. Blossom trees seed fresh fields around them.

**Tiberium on Red Alert's own maps.** 151 of the 230 official skirmish maps mix Tiberium fields with the ore, fairly for every start, with lobby thumbnails to match.

**Smarter movement and economy, for every faction.** A* pathfinding, attack-move (Shift+click), rally points, and more zoom levels, adapted from CFE Patch Redux. The deploy and select-all keys work for every faction. Harvesters dock at any faction's refinery, choose fields sensibly, and get themselves unstuck; infantry route around Tiberium and give way to vehicles in narrow passes.

**Crate surprises.** Unit crates draw from every faction's vehicles, and a few rare tanks turn up only in crates.

**Computer opponents for every faction.** The AI builds a base, runs an economy and fields an army, with ships on water maps for GDI and Nod. Each AI takes its own Easy, Medium, or Hard setting from the lobby, shown at the start of every match. You can fill a skirmish with any mix of the five sides.

**Authentic look and sound.** Tiberian Dawn unit and EVA voices, plus building and weapon sound effects including the Obelisk's charge-up and red laser and the Ion Cannon strike.

## How to play

Subscribe on the Steam Workshop, then enable **"Tiberian Factions for Red Alert"** from the mod list when you launch Red Alert in C&C Remastered. Start a skirmish, and GDI, Nod, and TS GDI will appear as selectable factions alongside Allies and Soviets, for you and for the AI.

(Alternatively, download the release zip from GitHub and extract it into `Documents/CnCRemastered/Mods/Red_Alert/`.)

## Graphics

**Tiberian Factions is HD only.** Play with Remastered graphics: classic graphics mode is locked out, because the mod's new units and buildings have no classic art.

## Planned

- **Tiberian Sun Nod:** Nod as a playable Tiberian Sun faction.
- **A balance pass for TS GDI and TS Nod:** 5.0.0 uses Tiberian Sun's exact values.
- **The Tiberian Dawn maps, as a separate download:** the 31 converted Tiberian Dawn maps, with their temperate, winter, and desert terrain, are out of the mod from 5.0.0 to keep its video memory use down, and are planned to return as their own Workshop item.
- **Smarter AI:** continued improvements to how the computer opponents build, defend, and use their armies and superweapons, including naval invasions.
- **GDI and Nod campaigns:** story campaigns for both factions.
- **Co-op missions:** scripted missions for two players.

## Compatibility

This is a **DLL mod**. It replaces the game's `RedAlert.dll`, and only one DLL mod can load at a time, so it won't work alongside any other mod that ships its own DLL (for example, CFE Patch). Disable other DLL mods when running this one. Mods that only change data or art (no DLL) are generally fine.

## License

**GPL v3**, inherited from Vanilla Conquer (which inherited from EA's 2020 source release). See `License.txt`.

This repository is a **fork of [Vanilla Conquer](https://github.com/TheAssemblyArmada/Vanilla-Conquer)**, which provides the DLL build base. The original Vanilla Conquer README is preserved as `README-VANILLA-CONQUER.md`.

## Building & deploying (for developers)

This project builds on Linux via mingw-w64 cross-compile.

```bash
# Install build dependencies (Ubuntu 24.04+):
sudo apt install -y cmake g++-mingw-w64 mingw-w64-tools ninja-build

# Build the DLL + mod folder (lands at build/remaster/Vanilla_RA/):
CMAKE_TOOLCHAIN_FILE=cmake/i686-mingw-w64-toolchain.cmake \
  VC_CXX_FLAGS="-w;-fpermissive" \
  cmake --workflow --preset remaster

# Or build and deploy to a Steam Deck (over Tailscale, passwordless SSH):
./deploy.sh
```

Override the SSH target with `DECK_HOST=user@hostname ./deploy.sh` if your Deck isn't named `steamdeck` on your Tailnet.

The build stages the asset packs into the mod folder (`scripts/stage_asset_packs.py`). After a data-only change, with no DLL rebuild, restage with `python3 scripts/stage_asset_packs.py --full build/remaster/Vanilla_RA`.

## Credits

- **EA / Petroglyph:** original Tiberian Dawn (1995) and Red Alert (1996), and the 2020 Remastered Collection.
- **Westwood Studios / EA:** Tiberian Sun (1999) and Red Alert 2 (2000), and **EA Los Angeles:** Command & Conquer 3: Tiberium Wars (2007), whose art and audio the mod uses.
- **hazelnut** ([SteamGridDB](https://www.steamgriddb.com/)): the Tiberian Sun GDI emblem on the TS GDI faction's cameo badges and faction icon.
- **[The Assembly Armada](https://github.com/TheAssemblyArmada):** Vanilla Conquer maintainers.

This mod is not endorsed by or affiliated with Electronic Arts.

## Acknowledgements & Inspiration

None of these are bundled, but their work shaped how we approached the engine. Thanks to:

- **Reilsss**, [Reilsss's Command & Conquer in Red Alert](https://steamcommunity.com/sharedfiles/filedetails/?id=2853520457): asset-replacement approach for reimagining RA factions as GDI/Nod.
- **DontCryJustDie**, [TD-Assets](https://steamcommunity.com/sharedfiles/filedetails/?id=3003163891): TD art and audio surfaced into the RA engine; reference for the `TD`-prefixed naming convention.
- **JohnnyJigglez**, [EMC (Enhanced Modding Capabilities)](https://www.nexusmods.com/commandandconquerremastered/mods/21): INI-driven custom buildings/vehicles patterns informed our extensibility approach.
- **ChthonVII**, [CFE Patch Redux](https://steamcommunity.com/sharedfiles/filedetails/?id=2268301299): engine-fix reference.
- **The OpenTS Developers**, [OpenTS](https://github.com/OpenTS-Developers/OpenTS): open-source Tiberian Sun reimplementation; the reference for the Tiberian Sun units' stats, weapons and rules, and for porting TS behaviours such as subterranean travel.
