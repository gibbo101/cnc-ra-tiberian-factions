# TS-HD-Graphics-Pack

Tiberian Sun GDI buildings, units, walls, gates and component towers, rebuilt as HD art, for Command & Conquer Remastered Collection mods (Red Alert). One of the asset packs from [Tiberian Factions](https://github.com/gibbo101/cnc-ra-tiberian-factions).

## Contents

**Units** (4): TSHARV, TSMCV, TSSMEC, TSTITN

**Structures** (66): TSCSAM, TSCSAMMAKE, TSCSAMT, TSCTWR, TSCTWRMAKE, TSCTWRX, TSDEPT, TSDEPTMAKE, TSDEPTRP, TSDPSA, TSDPSAMAKE, TSDROP, TSDROPMAKE, TSFACT, TSFACTMAKE, TSGATEH, TSGATEHL, TSGATEHMAKE, TSGATEHX, TSGATEV, TSGATEVL, TSGATEVMAKE, TSGATEVX, TSHPAD, TSHPADMAKE, TSNGATEH, TSNGATEHL, TSNGATEHMAKE, TSNGATEHX, TSNGATEV, TSNGATEVL, TSNGATEVMAKE, TSNGATEVX, TSNWALL, TSPILE, TSPILEMAKE, TSPOWR, TSPOWRMAKE, TSPROC, TSPROCFR, TSPROCLD, TSPROCMAKE, TSPROCNF, TSRADR, TSRADRMAKE, TSROCK, TSROCKMAKE, TSROCKT, TSSILO, TSSILOMAKE, TSTECH, TSTECHMAKE, TSTURB, TSVULC, TSVULCMAKE, TSVULCT, TSWALL, TSWEAP, TSWEAP2, TSWEAP2L, TSWEAPDR, TSWEAPLT, TSWEAPMAKE, TSWEAPNF, TSWEAPNU, TSWEAPUD

**Terrain (temperate)** (2): TSPROCBB, TSWEAPBB

**Terrain (snow)** (2): TSPROCBB, TSWEAPBB

**Terrain (interior)** (2): TSPROCBB, TSWEAPBB

**3D models** (16): barracks, construction-yard, dropship-bay, harvester, helipad, mcv, power-plant, radar, refinery, sensor-array, service-depot, silo, tech-center, titan, war-factory, wolverine. The HD rebuilds as glTF models, in `3d/`; `3d/README.md` lists their parts and conventions. The game does not use them.

## Using it

1. Copy the files under this pack's `Data/` folder into your mod's `Data/` folder, keeping the paths.
2. Copy the entries you need from this pack's XML files into your mod's own XML files:

   - `Data/XML/TILESETS/TSHD_UNITS.XML` into `Data/XML/TILESETS/RA_UNITS.XML`
   - `Data/XML/TILESETS/TSHD_STRUCTURES.XML` into `Data/XML/TILESETS/RA_STRUCTURES.XML`
   - `Data/XML/TILESETS/TSHD_VFX.XML` into `Data/XML/TILESETS/RA_VFX.XML`
   - `Data/XML/TILESETS/TSHD_TERRAIN_TEMPERATE.XML` into `Data/XML/TILESETS/RA_TERRAIN_TEMPERATE.XML`
   - `Data/XML/TILESETS/TSHD_TERRAIN_SNOW.XML` into `Data/XML/TILESETS/RA_TERRAIN_SNOW.XML`
   - `Data/XML/TILESETS/TSHD_TERRAIN_INTERIOR.XML` into `Data/XML/TILESETS/RA_TERRAIN_INTERIOR.XML`
   - `Data/XML/OBJECTS/UNITS/TSHDBUILDABLES.XML` into `Data/XML/OBJECTS/UNITS/RABUILDABLES.XML`
   - `Data/XML/AUDIO/SFXEVENTSNONLOCALIZED_TSHD.XML` into `Data/XML/AUDIO/SFXEVENTSNONLOCALIZED.XML`
   - `Data/XML/AUDIO/SFXEVENTSLOCALIZED_TSHD.XML` into `Data/XML/AUDIO/SFXEVENTSLOCALIZED.XML`

   The launcher only reads the mod files on the right. This pack's own XML files are there to copy from, so enabling the pack by itself changes nothing in game.

3. The game also needs a classic-mode SHP for every sprite, with the same frame count. A transparent stub is enough: Tiberian Factions makes its stubs with `scripts/gen_stub_shp.py` ([repo](https://github.com/gibbo101/cnc-ra-tiberian-factions)).
4. Units with one frame per facing, plus a turret block where they have one, use the stock layout. Units with rolling treads, walking gaits or offset turrets use Tiberian Factions' own layouts and need the matching DLL code, which is in the repo.

## Credits

Original Tiberian Sun assets: Electronic Arts. Prepared for Remastered by gibbo101 for Tiberian Factions.

Built from Tiberian Sun's designs by gibbo101 for Tiberian Factions.

## More C&C projects by gibbo101

- **Tiberian Factions** adds GDI and Nod as playable factions to Red Alert Remastered: [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3729834253), [ModDB](https://www.moddb.com/mods/tiberian-factions-for-red-alert), [GitHub](https://github.com/gibbo101/cnc-ra-tiberian-factions)
- **OpenTS Pad** ports the OpenTS rebuild of Tiberian Sun to Linux and the Steam Deck, with controller play: [GitHub](https://github.com/gibbo101/opents-pad)
- **Renegade Pad** brings controller play to C&C Renegade (an OpenW3D fork, built for the Steam Deck): [GitHub](https://github.com/gibbo101/renegade-pad)
- **C&C Map Editor** is a Linux-native, mod-aware map editor for C&C Remastered (Red Alert and Tiberian Dawn): [GitHub](https://github.com/gibbo101/cnc-map-editor)
- **PS1 Link Cable** plays two-player link-cable PS1 games such as C&C Retaliation between two Steam Decks over LAN: [GitHub](https://github.com/gibbo101/ps1-lan-link)
- **Steam Workshop Uploader** publishes Workshop items natively on Linux; it is how these packs ship: [GitHub](https://github.com/gibbo101/steam-workshop-uploader)
