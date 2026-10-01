# TS-HD-Graphics-Pack

Tiberian Sun walls, gates and component towers, rebuilt as HD art, for Command & Conquer Remastered Collection mods (Red Alert). One of the asset packs from [Tiberian Factions](https://github.com/gibbo101/cnc-ra-tiberian-factions).

## Contents

**Structures** (30): TSCSAM, TSCSAMMAKE, TSCSAMT, TSCTWR, TSCTWRMAKE, TSCTWRX, TSGATEH, TSGATEHL, TSGATEHMAKE, TSGATEHX, TSGATEV, TSGATEVL, TSGATEVMAKE, TSGATEVX, TSNGATEH, TSNGATEHL, TSNGATEHMAKE, TSNGATEHX, TSNGATEV, TSNGATEVL, TSNGATEVMAKE, TSNGATEVX, TSNWALL, TSROCK, TSROCKMAKE, TSROCKT, TSVULC, TSVULCMAKE, TSVULCT, TSWALL

## Using it

1. Copy the files under this pack's `Data/` folder into your mod's `Data/` folder, keeping the paths.
2. Copy the entries you need from this pack's XML files into your mod's own XML files:

   - `Data/XML/TILESETS/TSHD_STRUCTURES.XML` into `Data/XML/TILESETS/RA_STRUCTURES.XML`

   The launcher only reads the mod files on the right. This pack's own XML files are there to copy from, so enabling the pack by itself changes nothing in game.

3. The game also needs a classic-mode SHP for every sprite, with the same frame count. A transparent stub is enough: Tiberian Factions makes its stubs with `scripts/gen_stub_shp.py` ([repo](https://github.com/gibbo101/cnc-ra-tiberian-factions)).
4. Units with one frame per facing, plus a turret block where they have one, use the stock layout. Units with rolling treads, walking gaits or offset turrets use Tiberian Factions' own layouts and need the matching DLL code, which is in the repo.

## Credits

Original Tiberian Sun assets: Electronic Arts. Prepared for Remastered by gibbo101 for Tiberian Factions.

Built from Tiberian Sun's designs by gibbo101 for Tiberian Factions.
