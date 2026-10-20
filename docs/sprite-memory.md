# Sprite memory

**Status:** Design. Staging writes whole-canvas DDS sprites and the launcher skips its splash preload; next
release.
**Open:** a Steam Deck check for first-draw hitches with the preload off.

The launcher holds every texture it draws in video memory. Tiberian Factions and its asset packs carry far more art
than the base game, so how that art is stored, and when it loads, decides whether the mod fits on a 4 GB card.

## Measured

ClientG's video memory on one desktop (RTX 5070), Tiberium Garden, TS GDI, the same scripted start each time:

| Build | Main menu | In play |
|---|---|---|
| Base game, no mods | | 2,258 MB |
| TF with TS-HD-Assets, TGA sprites, preload on | 4,758 MB | 4,796 MB |
| Whole-canvas DDS sprites, preload on | 4,246 MB | 4,284 MB |
| Whole-canvas DDS sprites, preload off | 534 MB | 700 MB |

With the preload off, a match where the AI builds a full TS GDI base, all of it on screen, peaks at 972 MB.

## The splash preload

At startup ClientG uploads every texture of every enabled mod, whatever factions a match uses. The
`NOSPLASHPRELOAD` launch option clears the byte at `0x1F7F455` (ClientG 1.153.745903); the launcher tests it at
`0x7AE14B` before it runs the preload. Our `DllMain` runs in ClientG about three seconds before the first texture
reaches the card, so `No_Splash_Preload` (`tf_launcher.cpp`) clears the byte itself, once it has checked the test's
bytes. Each texture then loads when it is first drawn.

Over 195 s of the same AI match, the preload off gave 24.4 distinct frames a second against 26.0, and two freezes
of 0.30 s in the first ten seconds against a longest of 0.23 s.

## Sprites as DDS

A sprite ZIP holds one TGA and one `.meta` per frame; the `.meta` crops the frame to its visible pixels. The
launcher holds a ZIP's frames uncompressed, four bytes a pixel of each crop.

It also reads a sprite's frames as loose files in a folder of the ZIP's name, `.dds` among them, with the tileset
XML unchanged (its `.tga` names find the `.dds` files). Three rules hold for loose frames:

- A DDS inside a ZIP never loads: under a `.dds` name the frame draws as the missing-texture frog, under a `.tga`
  name nothing draws.
- A loose frame is stretched over the object's whole draw box and its `.meta` crop is ignored, so each frame is
  saved on its whole canvas, with the margins clear.
- A frame cut smaller than its canvas is drawn stretched, so the canvas can't be trimmed.

DXT5 with mips takes about one byte a pixel of the canvas. `scripts/sprite_dds.py` gives each sprite ZIP under a
staged mod's `UNITS`, `STRUCTURES` and `VFX` whichever form takes less memory: a folder of whole-canvas DXT5
frames, or the ZIP with every frame's crop tightened to its visible pixels. Staging (`stage_asset_packs.py`) and the
asset-pack builds (`workshop_packs.py`) run it, and it caches its output by ZIP content in `build/sprite-dds-cache`.
The base game's own terrain DDS files carry full mips, so the sprites do too.
