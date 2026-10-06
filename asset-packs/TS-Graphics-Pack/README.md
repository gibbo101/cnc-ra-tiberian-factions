# TS-Graphics-Pack

Tiberian Sun structures, effects and sidebar cameos as HD sprites, for Command & Conquer Remastered Collection mods (Red Alert). One of the asset packs from [Tiberian Factions](https://github.com/gibbo101/cnc-ra-tiberian-factions).

## Contents

**Effects** (43): RAILFX, TSBANG34, TSCANIST, TSCLSN16, TSCLSN22, TSCLSN30, TSCLSN42, TSCLSN58, TSDIG, TSDISCUS, TSDPOD1, TSDPOD2, TSDRPEXP, TSEMPFX, TSEXPSML, TSFIRE, TSFSAIR, TSFSGRND, TSFSIDLE, TSGUNFIRE, TSIONBM, TSIONRNG, TSMGUNE, TSMGUNN, TSMGUNNE, TSMGUNNW, TSMGUNS, TSMGUNSE, TSMGUNSW, TSMGUNW, TSPIFF, TSPODBLT, TSPODRNG, TSPULSBL, TSPULSF1, TSPULSF2, TSRAILFXS, TSSMOKEY, TSSMOKY2, TSSONICP, TSSONICW, TSXGRY1, TSXGRY2

**Sidebar cameos** (56): BuildIcon_TSNGATEH, BuildIcon_TSNGATEV, BuildIcon_TS_AmphAPC, BuildIcon_TS_Carryall, BuildIcon_TS_Csam, BuildIcon_TS_Ctwr, BuildIcon_TS_Dept, BuildIcon_TS_DevilsTongue, BuildIcon_TS_Disruptor, BuildIcon_TS_Drop, BuildIcon_TS_Dweap, BuildIcon_TS_E1, BuildIcon_TS_E2, BuildIcon_TS_Engineer, BuildIcon_TS_Fgen, BuildIcon_TS_Fsdf, BuildIcon_TS_GateH, BuildIcon_TS_GateV, BuildIcon_TS_Ghost, BuildIcon_TS_Harvester, BuildIcon_TS_HoverMLRS, BuildIcon_TS_Hpad, BuildIcon_TS_Juggernaut, BuildIcon_TS_Jumpjet, BuildIcon_TS_LimpetDrone, BuildIcon_TS_MCV, BuildIcon_TS_MammothMk1, BuildIcon_TS_MammothMk2, BuildIcon_TS_MechDivision, BuildIcon_TS_Medic, BuildIcon_TS_MobileEMP, BuildIcon_TS_MobileWarFactory, BuildIcon_TS_NWall, BuildIcon_TS_OrcaBomber, BuildIcon_TS_OrcaFighter, BuildIcon_TS_Pile, BuildIcon_TS_Pion, BuildIcon_TS_Plug, BuildIcon_TS_Pods, BuildIcon_TS_PowerPlant, BuildIcon_TS_Proc, BuildIcon_TS_Puls, BuildIcon_TS_Radr, BuildIcon_TS_Rock, BuildIcon_TS_Seek, BuildIcon_TS_SensorArray, BuildIcon_TS_Silo, BuildIcon_TS_StealthGen, BuildIcon_TS_SubAPC, BuildIcon_TS_Tech, BuildIcon_TS_Titan, BuildIcon_TS_Turb, BuildIcon_TS_Vulc, BuildIcon_TS_Wall, BuildIcon_TS_Weap, BuildIcon_TS_Wolverine

## Using it

1. Copy the files under this pack's `Data/` folder into your mod's `Data/` folder, keeping the paths.
2. Copy the entries you need from this pack's XML files into your mod's own XML files:

   - `Data/XML/TILESETS/TS_UNITS.XML` into `Data/XML/TILESETS/RA_UNITS.XML`
   - `Data/XML/TILESETS/TS_STRUCTURES.XML` into `Data/XML/TILESETS/RA_STRUCTURES.XML`
   - `Data/XML/TILESETS/TS_VFX.XML` into `Data/XML/TILESETS/RA_VFX.XML`
   - `Data/XML/TILESETS/TS_TERRAIN_TEMPERATE.XML` into `Data/XML/TILESETS/RA_TERRAIN_TEMPERATE.XML`
   - `Data/XML/TILESETS/TS_TERRAIN_SNOW.XML` into `Data/XML/TILESETS/RA_TERRAIN_SNOW.XML`
   - `Data/XML/TILESETS/TS_TERRAIN_INTERIOR.XML` into `Data/XML/TILESETS/RA_TERRAIN_INTERIOR.XML`
   - `Data/XML/OBJECTS/UNITS/TSBUILDABLES.XML` into `Data/XML/OBJECTS/UNITS/RABUILDABLES.XML`
   - `Data/XML/AUDIO/SFXEVENTSNONLOCALIZED_TS.XML` into `Data/XML/AUDIO/SFXEVENTSNONLOCALIZED.XML`
   - `Data/XML/AUDIO/SFXEVENTSLOCALIZED_TS.XML` into `Data/XML/AUDIO/SFXEVENTSLOCALIZED.XML`

   The launcher only reads the mod files on the right. This pack's own XML files are there to copy from, so enabling the pack by itself changes nothing in game.

3. The game also needs a classic-mode SHP for every sprite, with the same frame count. A transparent stub is enough: Tiberian Factions makes its stubs with `scripts/gen_stub_shp.py` ([repo](https://github.com/gibbo101/cnc-ra-tiberian-factions)).
4. Units with one frame per facing, plus a turret block where they have one, use the stock layout. Units with rolling treads, walking gaits or offset turrets use Tiberian Factions' own layouts and need the matching DLL code, which is in the repo.

## Credits

Original Tiberian Sun assets: Electronic Arts. Prepared for Remastered by gibbo101 for Tiberian Factions.

## More C&C projects by gibbo101

- **Tiberian Factions** adds GDI and Nod as playable factions to Red Alert Remastered: [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3729834253), [ModDB](https://www.moddb.com/mods/tiberian-factions-for-red-alert), [GitHub](https://github.com/gibbo101/cnc-ra-tiberian-factions)
- **OpenTS Pad** ports the OpenTS rebuild of Tiberian Sun to Linux and the Steam Deck, with controller play: [GitHub](https://github.com/gibbo101/opents-pad)
- **Renegade Pad** brings controller play to C&C Renegade (an OpenW3D fork, built for the Steam Deck): [GitHub](https://github.com/gibbo101/renegade-pad)
- **C&C Map Editor** is a Linux-native, mod-aware map editor for C&C Remastered (Red Alert and Tiberian Dawn): [GitHub](https://github.com/gibbo101/cnc-map-editor)
- **PS1 Link Cable** plays two-player link-cable PS1 games such as C&C Retaliation between two Steam Decks over LAN: [GitHub](https://github.com/gibbo101/ps1-lan-link)
- **Steam Workshop Uploader** publishes Workshop items natively on Linux; it is how these packs ship: [GitHub](https://github.com/gibbo101/steam-workshop-uploader)
