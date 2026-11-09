# Launcher UI images: the MT_COMMANDBAR atlas

**Status:** Reference. The launcher UI atlas: what TF paints into it, how it is built and shipped.

Launcher 2D UI images come from `MT_COMMANDBAR_COMMON.TGA`. The mod ships a full edited copy loose
in `Data/ART/TEXTURES/SRGB/`, and both the shell (menu, lobby, faction picker) and the game draw it.
The atlas, its region table, shipping a repainted copy and why region geometry is fixed are on the field manual's
[The UI atlas](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/the-ui-atlas.md);
the picker's preloaded icons are on its
[Adding a faction](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/engine/adding-a-faction.md#the-launchers-data-for-the-row).
This is the image lever; the data lever is `config-meg-mod-delivery.md`. md5-verify a deployed atlas before judging
any repaint.

## What the shipped atlas holds

The canonical copy is main's `resources/remaster_mods/Vanilla_RA/Data/ART/TEXTURES/SRGB/MT_COMMANDBAR_COMMON.TGA`
(gitignored, 184,582,562 bytes); its md5 is locked in `scripts/campaigns_work/textures.md5`. A worktree's copy can
be missing or stale, so copy main's in before a whole-build deploy (workspace `CLAUDE.md`). Painted into it:
- the radar crests: the pristine Allied and Soviet crests, and TS GDI's eagle over
  `UI_OBSERVER_MAP_BG` (`scripts/crest_atlas_paint.py`, `radar-crest-ram-spike.md`);
- the lobby picker emblems over the `UI_MULTIPLAYER_PLAYERSLOT_FACTION_NN` regions with their
  `_ON` / `_OVER` variants, and the map and loading-screen badges over `UI_MAPSELECT_FACTION_NN`
  (`scripts/picker_emblems_paint.py`, `faction-select-identity.md`), and the country flag icons
  (`scripts/frontend_atlas_build.py`);
- the TIBERIAN FACTIONS title over `UI_RA_MAINMENU_LOGO` (`scripts/title_logo_build.py`);
- the main-menu box and buttons in steel (`scripts/menu_art.py`);
- the lobby player slots, map rows and menu buttons in steel (`scripts/lobby_art.py`);
- the CAMPAIGNS page's tab icons and row crests (`scripts/campaigns_atlas.py`, run by
  `scripts/campaigns_page_build.sh`, `campaigns-page.md`).

## Editing it

TF extracts the base TGA and `.MTD` with the streaming lister (`mix-file-format.md`), reads regions through
`scripts/mtd.py`, which reads each name's length as the manual's
[The atlas and its region table](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/the-ui-atlas.md#the-atlas-and-its-region-table)
requires (skipping NULs misreads `RA_UI_RED_SEARCH_BTN_NORMAL_MIDDLE`, whose x is 3584), and byte-edits the pixels
in place, which keeps the rsync delta small.

## The regions

Which region draws what is on the manual's
[Pick the right region](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/the-ui-atlas.md#pick-the-right-region).
Two details it lacks: the in-match crest region is the metallic-backed one, and the `_DINO` crest region is unused.
Per-faction crests come from the RAM patch (`radar-crest-ram-spike.md`); the lobby identity is in
`faction-select-identity.md`.

## Dead route: a texture MEG

The manual's [Geometry is the launcher's](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/the-ui-atlas.md#geometry-is-the-launchers)
says a mod's own `TEXTURES_SRGB.MEG` replaces the base one whole. Details it lacks: the base MEG is about 2.4 GB
(1,358 entries), and an atlas-only MEG mounts alone, so the front end loses the other 1,357 textures. The mod loader mounts no MEG of its own:
`ModManagerClass::Load_Mod` takes loose files only (`Data\AUDIO\`, `Data\XML\`, `Data\MAPS\`), and
`Data/CONFIG.MEG` works because the generic manifest loader resolves each MEG path against the mod folder first. None
of 96 Workshop mods surveyed ships a `.meg`.

**EMC is not needed.** Reilsss's mod requires EMC for its units and INI content; the loose-atlas override itself is
vanilla, as TF (no EMC) shows. EMC is a sim-side DLL with no graphics imports and does nothing in ClientG.

## Growing the atlas (proven, not adopted)

See the manual's [Growing the atlas](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/the-ui-atlas.md#growing-the-atlas).
In TF's test an 8192x8192 copy drew the menu, lobby and TD sidebar correctly, ClientG's cached region records read
W=H=8192, and it drew the TS Nod emblem, painted at 7000,100, as the live radar crest (`radar-crest-ram-spike.md`).

- **Adopting it** means moving everything that hardcodes 6871x6716 to the new size: the crest
  needles in `dllinterface.cpp` (`const double W = 6871.0, H = 6716.0`), and
  `crest_atlas_paint.py`, `picker_emblems_paint.py`, `frontend_atlas_build.py`,
  `title_logo_build.py` and `clientg_region_probe.py`'s default.
- **Probe tools:** `scripts/atlas_grow_probe.py` builds the grown copy, `scripts/clientg_ratio_scan.py`
  prints each record's effective W,H during a match, and `ATLAS_W`/`ATLAS_H` override
  `clientg_region_probe.py`'s size.

## Payload

Staging converts the edited TGA to a DXT5 DDS with every mip level (`scripts/sprite_dds.py`, the manual's
[Shipping a repainted atlas](https://github.com/gibbo101/remastered-modding-field-manual/blob/main/front-end/the-ui-atlas.md#shipping-a-repainted-atlas)),
and that is what ships: `deploy.sh` and `package-for-workshop.sh` refuse a build without it (`sprite-memory.md`). A
single ship covers every UI-image edit (crests, flags, buttons, menus).

## Related
- `config-meg-mod-delivery.md`: the front-end data lever (factions, missions, master text).
- `launcher-vs-dll-ownership.md`: the code boundary.
- `mix-file-format.md`: MEG and atlas extract tooling.
