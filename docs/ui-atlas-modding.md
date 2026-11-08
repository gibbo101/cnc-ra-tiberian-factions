# Launcher UI images: the MT_COMMANDBAR atlas

**Status:** Reference. The launcher UI atlas: what it holds, editing it, growing it, shipping it.

Launcher 2D UI images come from `MT_COMMANDBAR_COMMON.TGA`. The mod ships a full edited copy loose
in `Data/ART/TEXTURES/SRGB/`, and both the shell (menu, lobby, faction picker) and the game draw it.
Region geometry is fixed and only pixels change, though the atlas itself can grow ("Growing the
atlas" below). This is the image lever; the data lever is `config-meg-mod-delivery.md`.
md5-verify a deployed atlas before judging any repaint.

## What the shipped atlas holds

The canonical copy is main's `resources/remaster_mods/Vanilla_RA/Data/ART/TEXTURES/SRGB/MT_COMMANDBAR_COMMON.TGA`
(gitignored, 184,582,562 bytes, md5 `40bc01f1…` as of 2026-10-01). A worktree's copy can be missing
or stale, so copy main's in before a whole-build deploy (workspace `CLAUDE.md`). Painted into it:
- the radar crests: the pristine Allied and Soviet crests, and TS GDI's eagle over
  `UI_OBSERVER_MAP_BG` (`scripts/crest_atlas_paint.py`, `radar-crest-ram-spike.md`);
- the lobby picker emblems over the `UI_MULTIPLAYER_PLAYERSLOT_FACTION_NN` regions with their
  `_ON` / `_OVER` variants (`scripts/picker_emblems_paint.py`), and the country flag icons
  (`scripts/frontend_atlas_build.py`);
- the TIBERIAN FACTIONS title over `UI_RA_MAINMENU_LOGO` (`scripts/title_logo_build.py`);
- the main-menu box and buttons in steel (`scripts/menu_art.py`);
- the lobby player slots, map rows and menu buttons in steel (`scripts/lobby_art.py`).

---

## TL;DR

See the field manual's [The UI atlas](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/the-ui-atlas.md) (the atlas and its region table, shipping a repainted
atlas, geometry) and [Adding a faction](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/adding-a-faction.md#the-launchers-data-for-the-row) (the picker's preloaded icons). TF edits
the TGA and ships a DXT5 DDS of the same name (`scripts/sprite_dds.py`); the picker's emblems are in
`faction-select-identity.md`.

---

## Editing it

The `.MTD` layout, the pixel offset formula and the loose path are on the field manual's
[The UI atlas](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/the-ui-atlas.md#the-atlas-and-its-region-table), The atlas and its region table and Shipping a repainted atlas.
TF extracts the base TGA and `.MTD` with the streaming lister (`mix-file-format.md`), reads regions through
`scripts/mtd.py`, and byte-edits the pixels in place, which keeps the rsync delta small. (Skipping NULs instead of reading the length misreads
`RA_UI_RED_SEARCH_BTN_NORMAL_MIDDLE`, whose x is 3584.)

---

## The regions

Which region draws what (the radar crest, the lobby logos, flags, markers, picker emblems), and why per side versus
per country decides what data can do, are on the field manual's
[The UI atlas](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/the-ui-atlas.md#pick-the-right-region), Pick the right region, sizes included. Two details it lacks: the
in-match crest region is the metallic-backed one, and the `_DINO` crest region is unused. Per-faction
crests come from the RAM patch (`radar-crest-ram-spike.md`); the lobby identity is in `faction-select-identity.md`.

---

## Dead route: a texture MEG

A mod's own `Data/TEXTURES_SRGB.MEG` shadows the base 2.4 GB MEG **whole**, so it would have to carry
all 1,358 base entries; an atlas-only MEG mounts alone and the front end loses the other 1,357
textures. The mod loader mounts no MEG of its own: `ModManagerClass::Load_Mod` takes loose files only
(`Data\AUDIO\`, `Data\XML\`, `Data\MAPS\`), and `Data/CONFIG.MEG` works because the generic manifest
loader resolves each MEG path against the mod folder first. None of 96 Workshop mods surveyed ships a
`.meg`. Loose files are the route, for the shell and the game alike. EMC is a sim-side DLL with no
graphics imports and does nothing in ClientG.

## Two red herrings (cleared)

- **Format was forgiving — the region was the bug:** see the field manual's [The UI atlas](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/the-ui-atlas.md#shipping-a-repainted-atlas), Shipping a repainted atlas and Pick the right region.
- **EMC is NOT required.** Reilsss's mod requires EMC for his *units/INI* content; the loose-atlas texture override itself is **vanilla** — proven by our non-EMC mod.

---

## Growing the atlas (proven, not adopted)

Growing the atlas, and why new space can only be reached by re-pointing a cached record, are on the field manual's
[The UI atlas](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/the-ui-atlas.md#growing-the-atlas), Growing the atlas. In TF's test an 8192x8192 copy drew the menu, lobby and TD sidebar
correctly, ClientG's cached region records read W=H=8192, and it drew the TS Nod emblem, painted at 7000,100, as the live radar crest (`radar-crest-ram-spike.md`).

- **Adopting it** means moving everything that hardcodes 6871x6716 to the new size: the crest
  needles in `dllinterface.cpp` (`const double W = 6871.0, H = 6716.0`), and
  `crest_atlas_paint.py`, `picker_emblems_paint.py`, `frontend_atlas_build.py`,
  `title_logo_build.py` and `clientg_region_probe.py`'s default. The loose file grows from 184 to
  268 MB.
- **Probe tools:** `scripts/atlas_grow_probe.py` builds the grown copy, `scripts/clientg_ratio_scan.py`
  prints each record's effective W,H during a match, and `ATLAS_W`/`ATLAS_H` override
  `clientg_region_probe.py`'s size.

## Payload

The edited atlas is a ~176 MiB `.TGA` (184,582,562 bytes). Staging converts it to a DXT5 DDS with every mip level (`scripts/sprite_dds.py`), about 62 MB, and that is what ships (`deploy.sh` and `package-for-workshop.sh` refuse a build without it; `sprite-memory.md`). A **single** ship covers *all* UI-image edits (crest + flags + buttons + menus). Byte-editing keeps each iteration's rsync delta tiny.

## Related
- `config-meg-mod-delivery.md` — front-end **data** lever (factions/missions/master-text).
- `launcher-vs-dll-ownership.md` — the code boundary (this is the image side of the data lever).
- `mix-file-format.md` — MEG/atlas extract tooling.
