# Tiberian Factions for Red Alert

A mod for **Command & Conquer: Red Alert Remastered** that adds **GDI** and **Nod**, the two factions from *Tiberian Dawn*, as fully playable sides alongside the original Allies and Soviets. Pick any of the four in skirmish and fight them all on the same map: **Allies vs Soviets vs GDI vs Nod**.

## What this mod adds

GDI and Nod aren't reskins. They're complete factions with their own bases, armies, superweapons, and computer opponents, built from authentic Tiberian Dawn art and sound.

**Two new factions, each with their own tech tree:**

- **GDI:** Construction Yard, Power Plants, Tiberium Refinery, Barracks, Weapons Factory, Communications Center, Advanced Communications, Helipad, and a Service Depot that repairs vehicles. Defended by Guard Towers and Advanced Guard Towers.
- **Nod:** Construction Yard, Power Plants, Tiberium Refinery, Hand of Nod, Airstrip, Communications Center, Temple of Nod, and Helipad. Defended by Gun Turrets, SAM Sites, and the laser-firing Obelisk of Light.

**Full unit rosters:**

- **Infantry:** Minigunner, Grenadier, Rocket Soldier, Flamethrower, Chem Warrior, Engineer, and the Commando.
- **Vehicles:** Medium Tank, Light Tank, Mammoth Tank, Flame Tank, Recon Bike, Hum-vee, Buggy, APC, MLRS, SSM Launcher, Artillery, plus the Harvester and Mobile Construction Vehicle.
- **Aircraft:** GDI's Orca and Nod's Apache, flown from the Helipad.

**Superweapons:** GDI's **Ion Cannon** and Nod's **Nuclear Strike**, each hosted by its faction's top-tier building.

**Computer opponents that actually play the factions.** The GDI and Nod AI build a full base, run an economy, tech up through the repair bay and tech centers, and field a combined-arms army of infantry, tanks, and aircraft. You can fill a skirmish with any mix of the four sides.

**Authentic look and sound.** Tiberian Dawn unit and EVA voices, plus building and weapon sound effects including the Obelisk's charge-up and red laser and the Ion Cannon strike.

## How to play

Subscribe on the Steam Workshop, then enable **"Tiberian Factions for Red Alert"** from the mod list when you launch Red Alert in C&C Remastered. Start a skirmish, and GDI and Nod will appear as selectable factions alongside Allies and Soviets, for you and for the AI.

(Alternatively, download the release zip from GitHub and extract it into `Documents/CnCRemastered/Mods/Red_Alert/`.)

## Graphics

**Remastered graphics are recommended.** Classic graphics mode still has some visual issues being ironed out.

## Planned

- **Red Alert balance pass:** the factions currently use Tiberian-Dawn-authentic stats; a future update will tune them for Red Alert's scale and pacing.
- **Smarter AI:** ongoing improvements to how the computer opponents build, defend, and use their armies and superweapons.

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

## Credits

- **EA / Petroglyph:** original Tiberian Dawn (1995) and Red Alert (1996), and the 2020 Remastered Collection.
- **[The Assembly Armada](https://github.com/TheAssemblyArmada):** Vanilla Conquer maintainers.

This mod is not endorsed by or affiliated with Electronic Arts.

## Acknowledgements & Inspiration

This project doesn't bundle these mods, but their work shaped how we approached the engine. Thanks to:

- **Reilsss**, [Reilsss's Command & Conquer in Red Alert](https://steamcommunity.com/sharedfiles/filedetails/?id=2853520457): asset-replacement approach for reimagining RA factions as GDI/Nod.
- **DontCryJustDie**, [TD-Assets](https://steamcommunity.com/sharedfiles/filedetails/?id=3003163891): TD art and audio surfaced into the RA engine; reference for the `TD`-prefixed naming convention.
- **JohnnyJigglez**, [EMC (Enhanced Modding Capabilities)](https://www.nexusmods.com/commandandconquerremastered/mods/21): INI-driven custom buildings/vehicles patterns informed our extensibility approach.
- **ChthonVII**, [CFE Patch Redux](https://steamcommunity.com/sharedfiles/filedetails/?id=2268301299): engine-fix reference.
