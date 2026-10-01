# RA2-SFX-Pack

Red Alert 2 weapon and engine sound effects, for Command & Conquer Remastered Collection mods (Red Alert). One of the asset packs from [Tiberian Factions](https://github.com/gibbo101/cnc-ra-tiberian-factions).

## Contents

**Sounds (Data/AUDIO)** (11): R2VAPOAT1A, R2VAPOAT2A, R2VAPOAT2B, R2VAPOAT2C, R2VAPOSTAA, R2VAPOSTAB, R2VAPOSTAC, R2VPRIATTA, R2VPRISTAA, R2VPRISTAB, R2VPRISTAC

## Using it

1. Copy the files under this pack's `Data/` folder into your mod's `Data/` folder, keeping the paths.
2. Copy the entries you need from this pack's XML files into your mod's own XML files:

   - `Data/XML/TILESETS/RA2_UNITS.XML` into `Data/XML/TILESETS/RA_UNITS.XML`
   - `Data/XML/TILESETS/RA2_STRUCTURES.XML` into `Data/XML/TILESETS/RA_STRUCTURES.XML`
   - `Data/XML/TILESETS/RA2_VFX.XML` into `Data/XML/TILESETS/RA_VFX.XML`
   - `Data/XML/TILESETS/RA2_TERRAIN_TEMPERATE.XML` into `Data/XML/TILESETS/RA_TERRAIN_TEMPERATE.XML`
   - `Data/XML/TILESETS/RA2_TERRAIN_SNOW.XML` into `Data/XML/TILESETS/RA_TERRAIN_SNOW.XML`
   - `Data/XML/TILESETS/RA2_TERRAIN_INTERIOR.XML` into `Data/XML/TILESETS/RA_TERRAIN_INTERIOR.XML`
   - `Data/XML/OBJECTS/UNITS/RA2BUILDABLES.XML` into `Data/XML/OBJECTS/UNITS/RABUILDABLES.XML`
   - `Data/XML/AUDIO/SFXEVENTSNONLOCALIZED_RA2.XML` into `Data/XML/AUDIO/SFXEVENTSNONLOCALIZED.XML`
   - `Data/XML/AUDIO/SFXEVENTSLOCALIZED_RA2.XML` into `Data/XML/AUDIO/SFXEVENTSLOCALIZED.XML`

   The launcher only reads the mod files on the right. This pack's own XML files are there to copy from, so enabling the pack by itself changes nothing in game.

## Credits

Original Red Alert 2 assets: Electronic Arts. Prepared for Remastered by gibbo101 for Tiberian Factions.

## More C&C projects by gibbo101

- **Tiberian Factions** adds GDI and Nod as playable factions to Red Alert Remastered: [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3729834253), [ModDB](https://www.moddb.com/mods/tiberian-factions-for-red-alert), [GitHub](https://github.com/gibbo101/cnc-ra-tiberian-factions)
- **OpenTS Pad** ports the OpenTS rebuild of Tiberian Sun to Linux and the Steam Deck, with controller play: [GitHub](https://github.com/gibbo101/opents-pad)
- **Renegade Pad** brings controller play to C&C Renegade (an OpenW3D fork, built for the Steam Deck): [GitHub](https://github.com/gibbo101/renegade-pad)
- **C&C Map Editor** is a Linux-native, mod-aware map editor for C&C Remastered (Red Alert and Tiberian Dawn): [GitHub](https://github.com/gibbo101/cnc-map-editor)
- **PS1 Link Cable** plays two-player link-cable PS1 games such as C&C Retaliation between two Steam Decks over LAN: [GitHub](https://github.com/gibbo101/ps1-lan-link)
- **Steam Workshop Uploader** publishes Workshop items natively on Linux; it is how these packs ship: [GitHub](https://github.com/gibbo101/steam-workshop-uploader)
