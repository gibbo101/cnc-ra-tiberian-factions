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

The Remastered launcher draws almost all 2D UI from one giant texture atlas — **`MT_COMMANDBAR_COMMON.TGA`** (6871×6716, 32-bit, in `TEXTURES_SRGB.MEG`) — with a sibling **`.MTD`** mapping `region-name → (x,y,w,h)`. **A mod ships a byte-edited copy of that `.TGA` loose in `Data/ART/TEXTURES/SRGB/` and the launcher loads it over the base.** Vanilla. No EMC. No `.MTD`/`.MTM` companions needed — and none honored: a loose `.MTD` with altered region coords is IGNORED (probed live 2026-08-30, coord-swapped picker flags unchanged in the lobby). Region GEOMETRY is launcher-owned; only region PIXELS are moddable, and art must fit the stock region boxes.

> **The in-game renderer and the front-end shell both draw the loose atlas**, and the shell also draws standalone loose DDS screens (first shown with Reilsss CnCinRA's picker icons and menu). For the lobby picker two levers combine: `FACTIONS.XML` `SmallIconName` (CONFIG.MEG) picks WHICH region, and only the preloaded `UI_Multiplayer_PlayerSlot_Faction_NN` regions work (any other crashes ClientG at startup); the atlas repaint sets that region's PIXELS, `_ON` / `_OVER` variants included (`faction-select-identity.md`).

---

## The recipe

1. Extract base `MT_COMMANDBAR_COMMON.TGA` + `.MTD` from `TEXTURES_SRGB.MEG` (streaming lister — see `mix-file-format.md`).
2. Find your region in the `.MTD`: locate the `NAME.TGA` bytes, **skip trailing null padding** (1–2 bytes, varies), read 4× little-endian `int32` = `x, y, w, h` (top-left origin).
3. **Byte-edit the `.TGA` pixels in place.** The atlas is 32-bit **BGRA**, **bottom-origin** (`desc=0x00`), 18-byte header, **no footer**. For image pixel `(x,y)` (top-left), the file offset is `18 + (H-1-y)*W*4 + x*4`; write bytes `B,G,R,A`. Preserve the header/footer exactly — don't round-trip through PIL's TGA writer (it appends a footer / flips the descriptor; harmless per the red-herring below, but byte-editing keeps the file format-identical and the rsync delta tiny).
4. Ship the edited `MT_COMMANDBAR_COMMON.TGA` **loose** at `<mod>/Data/ART/TEXTURES/SRGB/`. `.TGA` only. Deploy.

---

## The regions that matter (RA) — **picking the right one is the whole battle**

| UI element | Region(s) | Keying |
|---|---|---|
| **In-game radar crest** | RA's HUD scene: **`UI_SIDEBAR_FACTIONLOGO_ALLIES` / `_SOVIET`** (794×713). TD's HUD scene (GDI, Nod, TS GDI): **`UI_SIDEBAR_FACTIONLOGO_GDI` / `_NOD`** | per side in data; per faction via the RAM patch (`radar-crest-ram-spike.md`) |
| Lobby faction-pick big logo | `RA_UI_MULTIPLAYER_ALLIED/SOVIET_LOGO_LARGE_NORMAL`/`_HOVER`/`_SELECTED` (309–311) | per-side |
| Lobby / player-list flag icon | `RA_UI_FLAG_ICON_<COUNTRY>` (SPAIN, TURKEY, … 73×40) | **per-COUNTRY** |
| Small player-list logo | `RA_UI_ALLIED/SOVIET_LOGO_SMALL` | per-side |

We burned ~an afternoon editing `RA_UI_MULTIPLAYER_ALLIED_LOGO_LARGE_*` (the **lobby** logo) and seeing no in-game change. The in-game crest is **`UI_SIDEBAR_FACTIONLOGO_ALLIES`** — a different, 794×713, metallic-backed region. *Always confirm the region.*

Each HUD scene picks its crest region by RA side: RA's scene draws `_ALLIES` / `_SOVIET`, TD's scene `_GDI` / `_NOD`. The `_DINO` region is unused.

**Per-side vs per-country is the design constraint:**
- The in-game crest is **per-SIDE on the data side**: the pixels painted here are what every faction on that side and scene would see. Per-faction crests come from the DLL re-pointing ClientG's cached region records at runtime (`radar-crest-ram-spike.md`).
- Flags are **per-COUNTRY**, so repainting the flag of the country a faction rides changes that faction only, and England and the USSR keep theirs. This is the clean lever for per-faction identity on the faction-select screen (`faction-select-identity.md`).

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

- **Format was forgiving — the region was the bug.** Reilsss's *working* atlas is `desc=0x08` + a TGA footer (PIL-style); our byte-exact `desc=0x00` also works. Both load. The repeated failures were entirely the **wrong region** (lobby logos), not the format.
- **EMC is NOT required.** Reilsss's mod requires EMC for his *units/INI* content; the loose-atlas texture override itself is **vanilla** — proven by our non-EMC mod.

---

## Why our TD sprites already worked (context)

Our building and unit sprites (`Data/ART/TEXTURES/SRGB/RED_ALERT/.../*.ZIP`) render through the tileset XML pipeline (`td-port-playbook.md`), a different mechanism. The UI atlas is launcher-internal and is reached only by the loose `.TGA` override.

## Growing the atlas (proven 2026-09-11, not adopted)

When every region is taken, the atlas can grow. The `.MTD` stores pixel boxes only, with no
atlas size, and ClientG carries no size constant: it divides by the real texture size. An
8192x8192 atlas, with the stock art at its own coordinates and the rest padded, loads; the menu,
lobby and TD sidebar draw correctly, ClientG's cached region records read W=H=8192, and the TS Nod
emblem painted at 7000,100 drew as the live radar crest.

- **The new space has no names.** A loose `.MTD` is ignored, so new pixels are reached only by
  re-pointing a cached region record at runtime (`radar-crest-ram-spike.md`).
- **Adopting it** means moving everything that hardcodes 6871x6716 to the new size: the crest
  needles in `dllinterface.cpp` (`const double W = 6871.0, H = 6716.0`), and
  `crest_atlas_paint.py`, `picker_emblems_paint.py`, `frontend_atlas_build.py`,
  `title_logo_build.py` and `clientg_region_probe.py`'s default. The loose file grows from 184 to
  268 MB.
- **Probe tools:** `scripts/atlas_grow_probe.py` builds the grown copy, `scripts/clientg_ratio_scan.py`
  prints each record's effective W,H during a match, and `ATLAS_W`/`ATLAS_H` override
  `clientg_region_probe.py`'s size.

## Payload

The atlas is ~176 MB uncompressed (one loose `.TGA`). A **single** ship covers *all* UI-image edits (crest + flags + buttons + menus). Byte-editing keeps each iteration's rsync delta tiny.

## Related
- `config-meg-mod-delivery.md` — front-end **data** lever (factions/missions/master-text).
- `launcher-vs-dll-ownership.md` — the code boundary (this is the image side of the data lever).
- `mix-file-format.md` — MEG/atlas extract tooling.
