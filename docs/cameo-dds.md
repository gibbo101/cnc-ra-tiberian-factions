# Sidebar cameos as DDS

**Status:** Design. Proven on the desktop with a probe; nothing ships yet.
**Open:** the build step, a Deck check, the asset packs' cameos.

The mod ships 550 cameos (`BuildIcon_*.tga`, 176 MB): 341x256 RLE TGAs, every one fully
opaque. Written as DXT1 DDS with mips they take 59 KB each, about 32 MB in all.

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
banding. `_compare.png` sheets from `scripts/probes/cameo_dds_probe.py` set the original beside
the decoded DDS at full and sidebar size.

## Open

- **Build step.** Write cameos as DDS where the cameo builders save TGAs
  (`cameo_badge_build.py`, `cameo_variants_build.py`, `apply_custom_cameos.py`, `gate_cameos.py`),
  keep atlas-name overrides as TGA, and make the packager refuse a stray TGA beside a DDS.
- **Deck.** The probe ran on the desktop only.
- **Asset packs.** TS-HD carries 51 cameos of its own, which compress the same way.
