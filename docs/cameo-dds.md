# Sidebar cameos as DDS

**Status:** Design; shipped in 5.6.0. Staging writes DDS cameos. Every faction's cameos draw in the
encyclopedia on the desktop, and Nod's sidebar.
**Open:** a Deck check.

The mod ships 553 cameos (`BuildIcon_*.tga`, about 176 MB): 341x256 uncompressed 32-bit TGAs (image type 2), every one fully
opaque. Written as DXT1 DDS with mips they take 59 KB each, about 33 MB in all.

## Why the badges stay baked

Neither the cameo widget nor the sidebar entry's other fields can carry a per-entry badge, so a badge exists only
inside a baked image, picked by `AssetName` (`TF_Apply_Cameo_Badge` appends the owner mask): see the field manual's
[Sidebar cameos](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/sidebar-cameos.md#cameos-that-change-at-runtime).

## How the launcher loads a cameo

See the field manual's [Sidebar cameos](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/art/sidebar-cameos.md#a-new-cameo),
a new cameo and replacing a stock cameo: a new name loads a loose 344x256 DDS, and a stock region
takes only a loose TGA, so `BuildIcon_TD_A10` stays a TGA.

## Quality

DXT1 keeps the badges and art intact at sidebar size; at 4x zoom flat colour panels show slight
banding. `scripts/cameo_dds.py <tga>` writes a DDS beside a cameo for a check by eye.

## Staging

The cameo sources stay TGA, so every script that draws them is unchanged. Staging
(`asset_packs.copy_newer`, which `stage_asset_packs.py` and `workshop_packs.py` both use) writes each
`BuildIcon_*.tga` as `BuildIcon_*.DDS` (`scripts/cameo_dds.py`) and removes a staged TGA of the same
name, except a name in the launcher's atlas (`MT_COMMANDBAR_COMMON.MTD`, today only
`BuildIcon_TD_A10`), which stays a TGA. An encoded DDS carries its source's time and is rewritten
only when the source changes. The mod's 553 cameos stage as 552 DDS files, about 33 MB, and that one TGA.
