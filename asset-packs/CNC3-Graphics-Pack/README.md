# CNC3-Graphics-Pack

Command & Conquer 3 units and sidebar cameos as HD sprites, for Command & Conquer Remastered Collection mods (Red Alert). One of the asset packs from [Tiberian Factions](https://github.com/gibbo101/cnc-ra-tiberian-factions).

## Contents

**Units** (2): C3MK3, C3PRED

**Sidebar cameos** (2): BuildIcon_C3MK3, BuildIcon_C3PRED

## Using it

1. Copy the files under this pack's `Data/` folder into your mod's `Data/` folder, keeping the paths.
2. Copy the entries you need from this pack's XML files into your mod's own XML files:

   - `Data/XML/TILESETS/CNC3_UNITS.XML` into `Data/XML/TILESETS/RA_UNITS.XML`
   - `Data/XML/OBJECTS/UNITS/CNC3BUILDABLES.XML` into `Data/XML/OBJECTS/UNITS/RABUILDABLES.XML`

   The launcher only reads the mod files on the right. This pack's own XML files are there to copy from, so enabling the pack by itself changes nothing in game.

3. The game also needs a classic-mode SHP for every sprite, with the same frame count. A transparent stub is enough: Tiberian Factions makes its stubs with `scripts/gen_stub_shp.py` ([repo](https://github.com/gibbo101/cnc-ra-tiberian-factions)).
4. Units with one frame per facing, plus a turret block where they have one, use the stock layout. Units with rolling treads, walking gaits or offset turrets use Tiberian Factions' own layouts and need the matching DLL code, which is in the repo.

## Credits

Original Command & Conquer 3: Tiberium Wars assets: Electronic Arts. Prepared for Remastered by gibbo101 for Tiberian Factions.
