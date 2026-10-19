# Sidebar cameos as DDS

**Status:** Design. Staging writes DDS cameos; next release. Every faction's cameos draw in the
encyclopedia on the desktop, and Nod's sidebar.
**Open:** a Deck check.

The mod ships 553 cameos (`BuildIcon_*.tga`, about 176 MB): 341x256 RLE TGAs, every one fully
opaque. Written as DXT1 DDS with mips they take 59 KB each, about 33 MB in all.

## Why the badges stay baked

The DLL picks a cameo only by `AssetName` (`TF_Apply_Cameo_Badge` appends the owner mask), so a
badge exists only inside a baked image. The sidebar entry's other data is fixed-meaning fields:
cost, power, progress and four state flags. The cameo widget (`UI_SIDEBAR_CONSTRUCTIONENTRY.BUI`)
has overlay quads, but each is drawn by the launcher with fixed art: `FakeLoc_Quad` shows
`BuildIcon_RA_FakeText_<language>` when `Fake` is set, one texture for every entry. No overlay
can carry a per-entry badge.

## How the launcher loads a cameo

- A `<BuildIcon>` name that exists only as a loose file loads `<name>.dds` (sidebar and
  encyclopedia both shown working).
- A name that is also a region of the base atlas (`MT_COMMANDBAR_COMMON`) is overridden by a
  loose `.tga`, but not by a loose `.dds`: the atlas art shows. `BuildIcon_TD_A10` is the only
  such cameo the mod ships, so it stays a TGA.
- Every compressed DDS in the base game has sides that are multiples of 4, so a cameo is resized
  to 344x256; the sidebar quad stretches it as before.

## Quality

DXT1 keeps the badges and art intact at sidebar size; at 4x zoom flat colour panels show slight
banding. `scripts/cameo_dds.py <tga>` writes a DDS beside a cameo for a check by eye.

## Staging

The cameo sources stay TGA, so every script that draws them is unchanged. Staging
(`asset_packs.copy_newer`, which `stage_asset_packs.py` and `workshop_packs.py` both use) writes each
`BuildIcon_*.tga` as `BuildIcon_*.DDS` (`scripts/cameo_dds.py`) and removes a staged TGA of the same
name, except a name in the launcher's atlas (`MT_COMMANDBAR_COMMON.MTD`, today only
`BuildIcon_TD_A10`), which stays RLE TGA. An encoded DDS carries its source's time and is rewritten
only when the source changes. The mod's 553 cameos stage as 552 DDS files, about 33 MB, and that one TGA.
