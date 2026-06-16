# Theatres & desert in RA Remastered — feasibility (mapped 2026-05-29)

**Status: feasibility research, NOT queued work.** Desert matters for the GDI/Nod
*campaign* arc (TD missions use a desert theatre), and that arc is **a while down the
road**. This doc captures the findings so the future arc doesn't re-derive them. Nothing
is in flight.

Complements `config-meg-mod-delivery.md` (the data lever / "master key"),
`launcher-vs-dll-ownership.md` (code-side boundary), `campaign-tabs-research.md`
(`INSTANCES.XML` roster edits), `classic-mode-palette-remap.md` (classic-mode TD rendering).

> **Newer HD-terrain ground truth (2026-06-09):** since this doc was written we proved out
> the HD loose-terrain rendering path — see `td-tile-hd-loose-art-investigation.md`. Read that
> before doing any HD-desert tileset work; it supersedes the HD-rendering assumptions here.

---

## TL;DR

- **RA is locked to exactly 3 theatres** — `THEATER_TEMPERATE(0)`, `THEATER_SNOW(1)`,
  `THEATER_INTERIOR(2)` (`defines.h` `THEATER_COUNT=3`), each bound to the HD tileset
  `RA_Terrain_<name>`. Confirmed in **both** the toolchain
  (`SOURCECODE/CnCTDRAMapEditor/RedAlert/TheaterTypes.cs`) **and** the game binary
  (`ClientG.exe` string literals). TD has its own 3 (desert/temperate/winter).
- **No data path adds a 4th HD theatre.** The theatre→tileset *selection* is
  `ClientG.exe` code. The master key (mod-shipped `CONFIG.MEG`) reaches tileset
  *content* only — never the selection.
- **Classic-mode desert is clean and additive** (DLL-only — the DLL draws terrain, the
  launcher just blits the framebuffer). But classic mode is ~1% of players.
- **HD-mode desert (the 99%) is achievable only by hijacking an existing slot**
  (interior) — a **DLL + data hybrid**, not pure data, and not a new theatre.

---

## The data/code seam for theatres (the governing map)

| Layer | Owner | Mod-controllable? |
|---|---|---|
| Tileset textures / content (`RA_Terrain_*.xml`) | CONFIG.MEG **data** | ✅ via the master key |
| Theatre → tileset **selection** (RA → {temperate, snow, interior}) | `ClientG.exe` **code** | ❌ binary patch only |
| Template **model** (which template IDs/sizes exist per theatre) | **our DLL** (`IsoTileTypeClass`) | ✅ it's our code |
| Classic terrain rendering | **our DLL** (framebuffer) | ✅ |
| HD terrain rendering | launcher, from the *named* tileset | content ✅ / selection ❌ |

Decisive point: in HD mode the launcher renders terrain from a tileset it picks by a
**hardcoded name** per (game, theatre). RA's three names are baked into `ClientG.exe`;
there is **no `RA_Terrain_Desert`** and no `%s_Terrain_%s` format string to coax one in.

---

## Evidence (so this isn't re-investigated)

- **Toolchain** — `RedAlert/TheaterTypes.cs`:
  ```csharp
  Temperate = (0, "temperate", "RA_Terrain_Temperate" + commonTilesets)
  Snow      = (1, "snow",      "RA_Terrain_Snow"      + commonTilesets)
  Interior  = (2, "interior",  "RA_Terrain_Interior"  + commonTilesets)
  ```
- **Game binary** — `strings ClientG.exe`: `RA_Terrain_Temperate/Snow/Interior` and
  `TD_Terrain_Desert/Temperate/Winter` as literals; **no** `RA_Terrain_Desert`; no
  name-construction format string.
- **DLL** — `defines.h:3039` `TheaterType` enum (3 theatres + `THEATER_COUNT=3`);
  `const.cpp:527` `Theaters[THEATER_COUNT]` = {TEMPERATE, SNOW, INTERIOR};
  `TheaterDataType{Name[16],Root[10],Suffix[4]}` (`defines.h:3061`); `display.cpp` loads
  `<Root>.MIX` / `<Root>.PAL`.
- **CONFIG.MEG** — `meg_extract.py list | grep -i theat` → none (no theatre-list data
  file). `INSTANCES.XML` and the RA scenario `.ini` carry **no** per-map tileset/climate
  override (only `Theater=<NAME>`).
- **Climate system (open lead, NOT pursued)** — `ClientG.exe` has `ClimateType`,
  `custom_map_climate`, `RTSSCENE_CLIMATE_TYPE_MICROCHUNK`, and
  **`CLIMATE_TYPE_TEXTURE_NAME_MICROCHUNK`**: a *per-map* climate stored in the scene,
  possibly carrying its own texture name. If a map could declare a desert climate/texture
  it would bypass the hardcoded selection — but it's native and unexposed; confirming it
  needs a Ghidra dive or an empirical map-format test. Lower priority since Option B works.

---

## Option A — classic-mode desert (clean, DLL-only, additive)

1. Add `THEATER_DESERT` to the `defines.h` `TheaterType` enum (before `THEATER_COUNT`).
2. Add a row to `const.cpp` `Theaters[]`: `{"DESERT","DESERT","DES"}` (+ matching
   `THEATERF_DESERT`).
3. Bundle TD's `DESERT.MIX` (+ `.PAL` / `.mrf` for the palette remap).

The DLL draws the terrain itself and the launcher blits it, so the launcher's tileset code
never enters in. **Additive — breaks nothing.** Limitation: classic graphics mode only.

---

## Option B — HD-mode desert via the interior-slot hijack (DLL + data)

A 4th HD theatre is code-locked, so **repurpose the least-used existing slot (interior)**:

1. **Launcher / HD (data — master key):** ship `RA_Terrain_Interior.xml` repointed to TD's
   desert tileset content. The hardcoded "interior → `RA_Terrain_Interior`" lookup resolves
   and renders desert.
2. **DLL (ours):** teach the interior theatre the **desert template set** (`IsoTileTypes`)
   + ship a desert `INTERIOR.MIX`. Required because **the DLL owns the map/template model
   even in HD** — it parses the scenario's template IDs, so it must know the desert
   templates or the map won't load. (A pure texture re-skin of interior's indoor
   floor/wall templates would look wrong — desert needs sand/cliff/shore templates.)
3. **Roster (data — proven):** hide the RA interior campaign missions via `INSTANCES.XML`
   `ShowOnMissionSelect=false`, and curate interior MP maps out of the pool. **This is what
   makes the hijack non-breaking** (Luke's call, 2026-05-29).
4. Author the GDI/Nod desert maps with `Theater=INTERIOR`.

**Trade-off:** RA forfeits its interior theatre. Acceptable for a TD-flavoured conversion,
and the breakage objection is removed by step 3. **Workshop-clean — no binary patch:** the
DLL is ours; `CONFIG.MEG` + `INSTANCES.XML` ship via the master key.

### Cheapest validation (do first, before the DLL template port)
Repoint `RA_Terrain_Interior.xml` textures to desert art, repack with `meg_pack.py`, ship
in the mod folder, load an existing interior map in HD on the Deck, screenshot. Confirms
the HD slot-hijack at the data layer before investing in DLL template work.

---

## Bottom line for the roadmap

Desert is **feasible** but it is **campaign-arc work** (GDI/Nod missions need it), and that
arc is down the road. When it comes up: classic-mode desert is a quick additive DLL change;
HD-mode desert is the interior-slot hijack (DLL + data), with the cheap `CONFIG.MEG`
re-skin test as the go/no-go gate.

**DECISION 2026-06-03 (Luke): the chosen path is to REPLACE the interior theatre
slot with desert** (not add a 4th theatre — impossible per the lock above).
Interior is effectively unused in a GDI/Nod skirmish/campaign mod, so spending its
slot on desert is an accepted trade. This makes the "interior-slot hijack" the
committed approach. Triggered by the TD desert skirmish-map import goal — see
`td-skirmish-map-import.md` for the per-map theatre matrix + conversion breakdown.
