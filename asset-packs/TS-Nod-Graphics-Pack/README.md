# TS-Nod-Graphics-Pack

Tiberian Sun Nod units, walls and gates, rebuilt as HD art, for Command & Conquer Remastered Collection mods (Red Alert). One of the asset packs from [Tiberian Factions](https://github.com/gibbo101/cnc-ra-tiberian-factions).

## Contents

**Units** (4): TSE3, TSSAPC, TSSUBTANK, TSTTNK

**Structures** (12): TSNGATEH, TSNGATEHL, TSNGATEHMAKE, TSNGATEHX, TSNGATEV, TSNGATEVL, TSNGATEVMAKE, TSNGATEVX, TSNWALL, TSTICK, TSTICKMAKE, TSTICKT

**Sidebar cameos** (7): BuildIcon_TSNGATEH, BuildIcon_TSNGATEV, BuildIcon_TS_DevilsTongue, BuildIcon_TS_NWall, BuildIcon_TS_RocketInfantry, BuildIcon_TS_SubAPC, BuildIcon_TS_TickTank

## Using it

1. Copy the files under this pack's `Data/` folder into your mod's `Data/` folder, keeping the paths.
2. Copy the entries you need from this pack's XML files into your mod's own XML files:

   - `Data/XML/TILESETS/TSNOD_UNITS.XML` into `Data/XML/TILESETS/RA_UNITS.XML`
   - `Data/XML/TILESETS/TSNOD_STRUCTURES.XML` into `Data/XML/TILESETS/RA_STRUCTURES.XML`
   - `Data/XML/TILESETS/TSNOD_VFX.XML` into `Data/XML/TILESETS/RA_VFX.XML`
   - `Data/XML/TILESETS/TSNOD_TERRAIN_TEMPERATE.XML` into `Data/XML/TILESETS/RA_TERRAIN_TEMPERATE.XML`
   - `Data/XML/TILESETS/TSNOD_TERRAIN_SNOW.XML` into `Data/XML/TILESETS/RA_TERRAIN_SNOW.XML`
   - `Data/XML/TILESETS/TSNOD_TERRAIN_INTERIOR.XML` into `Data/XML/TILESETS/RA_TERRAIN_INTERIOR.XML`
   - `Data/XML/OBJECTS/UNITS/TSNODBUILDABLES.XML` into `Data/XML/OBJECTS/UNITS/RABUILDABLES.XML`
   - `Data/XML/AUDIO/SFXEVENTSNONLOCALIZED_TSNOD.XML` into `Data/XML/AUDIO/SFXEVENTSNONLOCALIZED.XML`
   - `Data/XML/AUDIO/SFXEVENTSLOCALIZED_TSNOD.XML` into `Data/XML/AUDIO/SFXEVENTSLOCALIZED.XML`

   The launcher only reads the mod files on the right. This pack's own XML files are there to copy from, so enabling the pack by itself changes nothing in game.

3. The game also needs a classic-mode SHP for every sprite, with the same frame count. A transparent stub is enough: Tiberian Factions makes its stubs with `scripts/gen_stub_shp.py` ([repo](https://github.com/gibbo101/cnc-ra-tiberian-factions)).
4. Units with one frame per facing, plus a turret block where they have one, use the stock layout. Units with rolling treads, walking gaits or offset turrets use Tiberian Factions' own layouts and need the matching DLL code, which is in the repo.

## Credits

Original Tiberian Sun assets: Electronic Arts. Prepared for Remastered by gibbo101 for Tiberian Factions.

## My other C&C projects

- **Tiberian Factions** adds GDI and Nod as playable factions to Red Alert Remastered: [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3729834253), [ModDB](https://www.moddb.com/mods/tiberian-factions-for-red-alert), [GitHub](https://github.com/gibbo101/cnc-ra-tiberian-factions)
- **Tiberian Sun HD Assets**: Tiberian Sun units, buildings, effects, sounds and EVA for Red Alert, in HD. [Steam Workshop, Red Alert](https://steamcommunity.com/sharedfiles/filedetails/?id=3819642604)
- **Red Alert 2 HD Assets**: Red Alert 2 units, sounds and voices for Red Alert and Tiberian Dawn, in HD. [Steam Workshop, Red Alert](https://steamcommunity.com/sharedfiles/filedetails/?id=3819308290), [Steam Workshop, Tiberian Dawn](https://steamcommunity.com/sharedfiles/filedetails/?id=3819308459)
- **C&C3 Tiberium Wars Assets**: Command & Conquer 3 units, effects, sounds and voices for Red Alert and Tiberian Dawn, in HD. [Steam Workshop, Red Alert](https://steamcommunity.com/sharedfiles/filedetails/?id=3819308545), [Steam Workshop, Tiberian Dawn](https://steamcommunity.com/sharedfiles/filedetails/?id=3819308668)
- **Tiberian Sun Music**: Tiberian Sun and Firestorm's soundtrack for Red Alert.
- **OpenTS Pad** ports the OpenTS rebuild of Tiberian Sun to Linux and the Steam Deck, with controller play: [GitHub](https://github.com/gibbo101/opents-pad)
- **Renegade Pad** brings controller play to C&C Renegade (an OpenW3D fork, built for the Steam Deck): [GitHub](https://github.com/gibbo101/renegade-pad)
- **C&C Map Editor** is a Linux-native, mod-aware map editor for C&C Remastered (Red Alert and Tiberian Dawn): [GitHub](https://github.com/gibbo101/cnc-map-editor)
- **PS1 Link Cable** plays two-player link-cable PS1 games such as C&C Retaliation between two Steam Decks over LAN: [GitHub](https://github.com/gibbo101/ps1-lan-link)
- **Steam Workshop Uploader** publishes Workshop items natively on Linux; it is how these packs ship: [GitHub](https://github.com/gibbo101/steam-workshop-uploader)
