# CNC3-Graphics-Pack

Command & Conquer 3 units and sidebar cameos as HD sprites, for Command & Conquer Remastered Collection mods (Red Alert). One of the asset packs from [Tiberian Factions](https://github.com/gibbo101/cnc-ra-tiberian-factions).

## Contents

**Units** (57): C3APC, C3AVATAR, C3AVATARBM, C3AVATARFL, C3AVATARSD, C3AVATARSG, C3BEAM, C3BHAND, C3BHANDSQ, C3BIKE, C3BUGGY, C3BUGGYEMP, C3CARRY, C3CYBORG, C3CYBORGSQ, C3ENGI, C3FANAT, C3FANATSQ, C3FHAWK, C3FLAME, C3GCMDO, C3GREN, C3GRENSQ, C3JUGG, C3MILIT, C3MILITSQ, C3MISSL, C3MISSLSQ, C3MK3, C3MK3RAIL, C3NCMDO, C3ORCA, C3ORCAPOD, C3OX, C3PITB, C3PITBMOR, C3PRED, C3PREDRAIL, C3RIFLE, C3RIFLESQ, C3RIG, C3ROCKT, C3ROCKTSQ, C3SABOT, C3SCORP, C3SCORPDZR, C3SCORPLAS, C3SCORPLASDZR, C3SHADW, C3SHADWSQ, C3SNIPE, C3STNK, C3VENOM, C3VENOMSG, C3VERT, C3ZONE, C3ZONESQ

**Structures** (3): C3BBASE, C3BBASEMAKE, C3BBASET

**Effects** (35): C3APCMZE, C3APCMZN, C3APCMZNE, C3APCMZNW, C3APCMZS, C3APCMZSE, C3APCMZSW, C3APCMZW, C3BMCHG, C3BMGLOW, C3BMHIT, C3BMMZ, C3FLME, C3FLMHIT, C3FLMN, C3FLMNE, C3FLMNW, C3FLMPIL, C3FLMS, C3FLMSE, C3FLMSW, C3FLMW, C3MEDEXP, C3PBMZ, C3PBSHL, C3RAILGLOW, C3RAILGLOWO, C3RAILHIT, C3RAILHITO, C3RAILMZ, C3RAILMZO, C3STHIT, C3STMIS, C3STMZ, C3STTRL

**Sidebar cameos** (35): BuildIcon_C3APC, BuildIcon_C3AVATAR, BuildIcon_C3BBASE, BuildIcon_C3BEAM, BuildIcon_C3BHAND, BuildIcon_C3BIKE, BuildIcon_C3BUGGY, BuildIcon_C3CARRY, BuildIcon_C3CYBORG, BuildIcon_C3ENGI, BuildIcon_C3FANAT, BuildIcon_C3FHAWK, BuildIcon_C3FLAME, BuildIcon_C3GCMDO, BuildIcon_C3GREN, BuildIcon_C3JUGG, BuildIcon_C3MILIT, BuildIcon_C3MISSL, BuildIcon_C3MK3, BuildIcon_C3NCMDO, BuildIcon_C3ORCA, BuildIcon_C3OX, BuildIcon_C3PITB, BuildIcon_C3PRED, BuildIcon_C3RIFLE, BuildIcon_C3RIG, BuildIcon_C3ROCKT, BuildIcon_C3SABOT, BuildIcon_C3SCORP, BuildIcon_C3SHADW, BuildIcon_C3SNIPE, BuildIcon_C3STNK, BuildIcon_C3VENOM, BuildIcon_C3VERT, BuildIcon_C3ZONE

## Using it

1. Copy the files under this pack's `Data/` folder into your mod's `Data/` folder, keeping the paths.
2. Copy the entries you need from this pack's XML files into your mod's own XML files:

   - `Data/XML/TILESETS/CNC3_UNITS.XML` into `Data/XML/TILESETS/RA_UNITS.XML`
   - `Data/XML/TILESETS/CNC3_STRUCTURES.XML` into `Data/XML/TILESETS/RA_STRUCTURES.XML`
   - `Data/XML/TILESETS/CNC3_VFX.XML` into `Data/XML/TILESETS/RA_VFX.XML`
   - `Data/XML/TILESETS/CNC3_TERRAIN_TEMPERATE.XML` into `Data/XML/TILESETS/RA_TERRAIN_TEMPERATE.XML`
   - `Data/XML/TILESETS/CNC3_TERRAIN_SNOW.XML` into `Data/XML/TILESETS/RA_TERRAIN_SNOW.XML`
   - `Data/XML/TILESETS/CNC3_TERRAIN_INTERIOR.XML` into `Data/XML/TILESETS/RA_TERRAIN_INTERIOR.XML`
   - `Data/XML/OBJECTS/UNITS/CNC3BUILDABLES.XML` into `Data/XML/OBJECTS/UNITS/RABUILDABLES.XML`
   - `Data/XML/AUDIO/SFXEVENTSNONLOCALIZED_CNC3.XML` into `Data/XML/AUDIO/SFXEVENTSNONLOCALIZED.XML`
   - `Data/XML/AUDIO/SFXEVENTSLOCALIZED_CNC3.XML` into `Data/XML/AUDIO/SFXEVENTSLOCALIZED.XML`

   The launcher only reads the mod files on the right. This pack's own XML files are there to copy from, so enabling the pack by itself changes nothing in game.

3. The game also needs a classic-mode SHP for every sprite, with the same frame count. A transparent stub is enough: Tiberian Factions makes its stubs with `scripts/gen_stub_shp.py` ([repo](https://github.com/gibbo101/cnc-ra-tiberian-factions)).
4. Units with one frame per facing, plus a turret block where they have one, use the stock layout. Units with rolling treads, walking gaits or offset turrets use Tiberian Factions' own layouts and need the matching DLL code, which is in the repo.

## Credits

Original Command & Conquer 3: Tiberium Wars assets: Electronic Arts. Prepared for Remastered by gibbo101 for Tiberian Factions.

## My other C&C projects

- **Tiberian Factions** adds GDI and Nod as playable factions to Red Alert Remastered: [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3729834253), [ModDB](https://www.moddb.com/mods/tiberian-factions-for-red-alert), [GitHub](https://github.com/gibbo101/cnc-ra-tiberian-factions)
- **Tiberian Sun HD Assets**: Tiberian Sun units, buildings, effects, sounds and EVA for Red Alert and Tiberian Dawn, in HD. [Steam Workshop, Red Alert](https://steamcommunity.com/sharedfiles/filedetails/?id=3819642604), [Steam Workshop, Tiberian Dawn](https://steamcommunity.com/sharedfiles/filedetails/?id=3819642832)
- **Red Alert 2 HD Assets**: Red Alert 2 units, sounds and voices for Red Alert and Tiberian Dawn, in HD. [Steam Workshop, Red Alert](https://steamcommunity.com/sharedfiles/filedetails/?id=3819308290), [Steam Workshop, Tiberian Dawn](https://steamcommunity.com/sharedfiles/filedetails/?id=3819308459)
- **Red Alert Remastered Modding Field Manual** is what building Tiberian Factions taught us, written up for anyone modding C&C Remastered: [Read it](https://gibbo101.github.io/remastered-modding-field-manual/)
- **OpenTS Pad** ports the OpenTS rebuild of Tiberian Sun to Linux and the Steam Deck, with controller play: [GitHub](https://github.com/gibbo101/opents-pad)
- **Renegade Pad** brings controller play to C&C Renegade (an OpenW3D fork, built for the Steam Deck): [GitHub](https://github.com/gibbo101/renegade-pad)
- **ra2-decomp** is a matching decompilation of Red Alert 2: Yuri's Revenge, C++ that builds back into the original game: [GitHub](https://github.com/gibbo101/ra2-decomp)
- **C&C Map Editor** is a Linux-native, mod-aware map editor for C&C Remastered (Red Alert and Tiberian Dawn): [GitHub](https://github.com/gibbo101/cnc-map-editor)
- **PS1 Link Cable** plays two-player link-cable PS1 games such as C&C Retaliation between two Steam Decks over LAN: [GitHub](https://github.com/gibbo101/ps1-lan-link)
- **Steam Workshop Uploader** publishes Workshop items natively on Linux; it is how these packs ship: [GitHub](https://github.com/gibbo101/steam-workshop-uploader)
