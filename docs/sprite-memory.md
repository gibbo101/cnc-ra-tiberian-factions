# Sprite memory

**Status:** Design, partly shipped: a DDS UI atlas, and the splash preload always on. Sprites ship as their ZIPs (Sprites
as DDS). The match warm-up below follows, with the preload off.
**Open:** the warm-up; a Steam Deck and a LAN test of it.

The launcher holds every texture it draws in video memory. Tiberian Factions and its asset packs carry far more art
than the base game, so how that art is stored, and when it loads, decides whether the mod fits on a 4 GB card.

## Measured

ClientG's video memory on one desktop (RTX 5070), Tiberium Garden, TS GDI, the same scripted start each time, for
TF with TS-HD-Assets: base game, TGA sprites and whole-canvas DDS sprites with the preload on, and DDS sprites with
it off (534 MB at the menu, 700 MB in play). The table is in the field manual's
[Sprite memory and DDS](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/sprite-memory-and-dds.md#everything-loads-at-start-up).

With the preload off, a match where the AI builds a full TS GDI base, all of it on screen, peaks at 972 MB. The UI
atlas as DDS takes a further 116 MB off every screen: Docklands, TS GDI, 534 to 418 MB at the menu and 972 to 856 MB
in play.

The shipped builds on the same desktop, a played Tiberium Garden skirmish, TS GDI against one Medium AI:

| Build | Main menu | In play |
|---|---|---|
| DDS sprites and DDS UI atlas | 4,402 MB | 4,476 MB |
| ZIP sprites and DDS UI atlas | 4,658 MB | 4,712 MB |

## The splash preload

See the field manual's [Sprite memory and DDS](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/sprite-memory-and-dds.md#everything-loads-at-start-up)
for the preload, the `NOSPLASHPRELOAD` test and why art drops to the frog without it. TF's shared art
(`share_tileset_zips.py`) and opener tiles (`td-base-art.md`) need it, so `Keep_Splash_Preload` (`tf_launcher.cpp`)
patches the test and the preload always runs.

## The match warm-up

Without the preload a match holds 0.7 to 1 GB (Measured), if those ZIPs are opened some other way. ClientG's
`Load_Archive` (`0x1747030`) opens `<type root>\<name>.zip` by name, and a hook on the per-frame update call at
`0x7AF105` runs on the main thread, through the loading screen too. Opening all 240 such ZIPs at once took 3.4 s and
1.4 GB, so the warm-up opens each ZIP when its object is first built, by any house; crate drops and reinforcements
still load on first draw. ClientG never unloads unit, building or effect art within a session.

## Sprites as DDS

TF ships sprites as their ZIPs: loose whole-canvas DDS frames saved about 250 MB in play, but DXT's colour rounding
speckled the Allied Construction Yard's concrete pad. The rules and the measurement are in the field manual's
[Sprite memory and DDS](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/sprite-memory-and-dds.md#dds-frames-and-their-rules).
Staging (`stage_asset_packs.py`) and the asset-pack builds (`workshop_packs.py`) delete any DDS frame folder an
earlier build left (`sprite_dds.drop_frames`).

## The UI atlas

`MT_COMMANDBAR_COMMON` holds the sidebar, the crests, the cameos and every front-end region. Staging writes it as a
padded DXT5 DDS (`sprite_dds.convert_atlas`), and the radar crest records the DLL writes (`radar-crest-ram-spike.md`)
take the atlas's size from the shipped DDS. See the field manual's
[The UI atlas](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/the-ui-atlas.md#shipping-a-repainted-atlas)
for the sizes and why the UVs follow the loaded texture. `deploy.sh` and the packager check the locked atlas in `resources/`, the TGA the DDS is
made from.
