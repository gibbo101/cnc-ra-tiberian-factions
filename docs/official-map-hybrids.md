# Official-map Tiberium/Ore hybrids

The official RA skirmish maps are replaced in place by Tiberium/Ore hybrids: chosen ore fields
become Tiberium, and the ore mine feeding each one becomes a TD blossom tree. The map's lobby
thumbnail is repainted to match. The stock map name, lobby entry and start positions stay as
they are.

**Proven in play 2026-09-14** on Luke's Deck: Keep off the Grass against a Medium AI showed the
East field as Tiberium with the blossom tree standing in it, and the home Ore and centre gems
untouched. The same night the lobby showed the repainted thumbnail, so a loose DDS does
override an official map's preview.

## Delivery

### The map: replace it by name from CCDATA

- The official maps are `scmNNea.ini` / `scmNNNea.ini` (230 files) inside
  `Data/CNCDATA/RED_ALERT/AFTERMATH/MAIN.MIX`, in the nested `general.mix`.
- A file of the same name in the mod's `CCDATA/` folder loads instead of the stock one. This is
  the same shadow-by-name the campaign hijack uses (`campaign-tabs-research.md`).
- The file must have no `[Digest]` section: a wrong digest aborts the load, and a missing one
  skips the check.

### The lobby thumbnail: a loose DDS of the same name

- The lobby does not draw the thumbnail from the map file, so the CCDATA map leaves it showing
  the stock layout. Each official map's thumbnail is a pre-rendered
  `DATA\ART\TEXTURES\SRGB\MOBIUS_RED_ALERT_MULTIPLAYER_<N>_MAP.DDS` in `TEXTURES_SRGB.MEG`
  (512x512 DXT5, 10 mips, no trees or mines drawn). The playable area is scaled by its longer
  side and centred, so a non-square map is letterboxed with black bars (Docklands, 126x64,
  fills rows 126-385).
- The key comes from the `CNCMapPreviewData` XML in `CONFIG.MEG`: one
  `<INIData Name="MOBIUS_RED_ALERT_MULTIPLAYER_<N>_MAP">` per map, holding only its bounds and
  start waypoints. It names no file, so the builder finds a map's key by matching its bounds and
  starts (Keep off the Grass = `_5_`, Docklands = `_111_`).
- A DDS of the same name loose under the mod's `Data/ART/TEXTURES/SRGB/` overrides the stock one;
  the front end reads loose overrides (`front-end-texture-meg-spike.md`).

### Snow maps need snow Tiberium art

The launcher draws TIB01 by looking its name up in the current theatre's tileset XML.
`OVERLAY_TIB01` is not theatre-specific in the DLL, so a Tiberium cell on any map asks for
`TIB01`, and a theatre whose tileset lacks it has no art to draw. The temperate and interior
tilesets have carried TIB01 since the Tiberium ecosystem; RA's snow tileset gained it for these
hybrids (`scripts/build_tiberium_hd.py SNOW`): TD's winter Tiberium frames (`TI1.WIN`) packed into
`Data/ART/TEXTURES/SRGB/RED_ALERT/TERRAIN/SNOW/TIB01.ZIP`, and 12 TIB01 tiles spliced into the
mod's existing `RA_TERRAIN_SNOW.XML`. The converted TD winter maps don't use it: they live in the
temperate slot. **Proven in play 2026-09-14** (desktop, headless): Middle Mayhem's central
island drew TD's winter Tiberium on the snow with its blossom trees standing in it, and no
missing-art boxes.

The map editor still reports "Overlay 'tib01' is not available in the set theater" on snow
maps, one note per cell. The note comes from the editor's own theatre table, not from the game.

### Everything ships with the build

- The build copies `resources/remaster_mods/Vanilla_RA/` (CCDATA and Data included) into
  `build/remaster/Vanilla_RA/` (`redalert/CMakeLists.txt`), so every file ships with every
  build and Workshop package.
- It is all data. Deploying a map means copying its `.ini` into the target's `CCDATA/` and its
  DDS into the target's `Data/ART/TEXTURES/SRGB/` (plus, once, the snow tileset and snow
  `TIB01.ZIP`), then md5-checking each; the DLL is untouched.

## The builder: `scripts/official_map_hybrid.py`

```bash
python3 scripts/official_map_hybrid.py --survey scm05ea.ini   # fields, mines and starts of a map
python3 scripts/official_map_hybrid.py                        # rebuild every map in HYBRIDS
python3 scripts/official_map_hybrid.py scm05ea.ini            # rebuild one
```

`HYBRIDS` maps an official file name to the fields that turn to Tiberium (cell = `y*128 + x`).
A plain list names ore-mine cells. A dict can also name `"fields"`: any one cell inside an
Ore field, which turns that whole field to Tiberium with no blossom.

**Gem rules (Luke, 2026-09-14).** Gems never get touched, and a field with any Gems in it stays
exactly as it is, so only pure-Ore fields turn to Tiberium. The builder refuses an entry that
names a field holding Gems. The one exception is Docklands, whose entry sets
`"take_gems": True` so its west bank turns over whole, mixed Ore/Gem fields included; even
there, a field of Gems alone keeps its Gems (the all-gem box in the west).

```python
"scm05ea.ini": [5714, 9901],                          # two mines, two blossoms
"scm111ea.ini": {"mines": [4505, 4529], "fields": [5801, 6401]},
```

**The map.** For each entry the script:

1. takes each mine's field (the Ore/Gem cells within 2 cells of the mine, grown out through every
   8-connected Ore/Gem neighbour) and each named field (grown out from its cell);
2. applies the gem rules above, then sets the field's cells to `OVERLAY_TIB01` (25) in
   `[OverlayPack]`; the engine works out density when the map loads;
3. drops each mine's `<cell>=MINE` line from `[TERRAIN]`;
4. adds `Neutral,TDBLOSSOM,256,<cell>,0,None` to `[STRUCTURES]` for each mine, the same line
   `td_map_to_ra.py` writes for TD blossom trees. The blossom seeds Tiberium itself
   (`BuildingClass::AI`).

Every other line is carried over byte for byte. The script reads the pristine map straight from
`MAIN.MIX`, re-decodes its own `[OverlayPack]` output as a check, and writes the result to
`resources/remaster_mods/Vanilla_RA/CCDATA/<map>.ini`. The OverlayPack codec is the
`td_map_to_ra.py` one that the shipped TD map pack already uses.

**The thumbnail.** The script then:

1. finds the preview key in `CONFIG.MEG` (bounds and starts must match exactly one entry);
2. reads the stock DDS from `TEXTURES_SRGB.MEG` by seeking through its index (the MEG is 2.4 GB);
3. maps each converted cell to its pixels with the letterbox rule, and grows that mask by half a
   cell to catch sprites that overhang their cell;
4. recolours only the tan Ore speckle inside the mask. A pixel counts as speckle when its red
   sits well above its blue and it is not greener than it is red, so grass, snow, water and grey
   rock are left alone. Each speckle pixel moves towards the Tiberium colour in proportion to how
   far it sits from the ground under the field towards the field's mean Ore colour. The
   Tiberium colour is the speckle hue of EA's own TD thumbnails (`77, 92, 42`), brightened to
   the map's Ore speckle but by no more than 1.6x, so it stays a clear green on snow;
5. encodes the image as DXT5 with the stock mip count (`scripts/dds_dxt5.py`), reuses the stock
   128-byte header, asserts the file is exactly the stock size, and only then writes
   `resources/remaster_mods/Vanilla_RA/Data/ART/TEXTURES/SRGB/<key>.DDS`.

## Converting another map

1. **Survey.** `--survey <map>` lists every Ore/Gem field (size, bounding box, Ore vs Gems, the
   mines within reach) plus the start waypoints. Map names are in `map-edits/_official_map_list.ini`
   (the classic set); the full 230 extract with
   `cnc-map-editor` `OfficialMaps.Extract` to `cnc-map-editor/artifacts/test-output/official/`.
   A render annotated with a cell grid, the starts and the mines makes the choice quick (see
   the session scratch recipe: `cncmap render`, crop to the bounds, draw the grid).
2. **Choose the mix.** The Tiberium/Ore split varies from map to map on purpose: some maps near
   50/50, some Tiberium-heavy, some Ore-heavy (Luke, 2026-09-14). No map has to be even. What
   stays fair is each start's access: on a mirrored map, convert fields in mirrored pairs so
   every start gets the same deal. Only pure-Ore fields are candidates (`gems 0` in the survey).
   Fields the map joins together count as one: North By Northwest's centre has its East gem
   patch attached, so the whole centre stays Ore.
   Record the mix in the table below, so the pool as a whole keeps a spread. A field with no
   mine goes in under `"fields"`; it gets no blossom, and a tree it later engulfs may bloom
   into one on its own.
3. **Build.** Add the map to `HYBRIDS` and run the script.
4. **Check the map.** Validate and render with the mod loaded:
   ```bash
   cd ~/Documents/development/cnc-remastered-mods && export PATH="$HOME/.dotnet:$PATH"
   env -u DISPLAY dotnet run --project cnc-map-editor/MobiusCli -- validate <ini> --mod cnc-ra-tiberian-factions/build/remaster/Vanilla_RA
   env -u DISPLAY dotnet run --project cnc-map-editor/MobiusCli -- render <ini> <out.png> --mod cnc-ra-tiberian-factions/build/remaster/Vanilla_RA
   ```
   The render shows the Tiberium but not the blossom trees (see Traps).
5. **Check the thumbnail.** Pillow reads the DDS directly:
   `python3 -c "from PIL import Image; Image.open('<dds>').save('<out.png>')"`. Only the
   converted fields should have changed colour.
6. **Play.** Copy the files to the test surface, md5 each, and look at the lobby thumbnail and a
   skirmish on the map.

## How the resources behave once placed

- Tiberium and Ore never convert each other. Spreading only lands on an empty cell
  (`CellClass::Can_Tiberium_Germinate`) and each field spreads as its own type
  (`CellClass::Spread_Tiberium`), so where two fields meet they hold a border. A remaining ore
  mine next to a Tiberium field grows Ore up to that border. (`todo.md` holds the open idea of
  Tiberium eating Ore.)
- The blossom tree seeds TIB01 into empty neighbouring cells.
- An ordinary tree with 6 or more TIB01 neighbours turns into a blossom tree
  (`redalert/terrain.cpp`).
- Tiberium is worth the same per bail as Ore (`GoldValue`), so a Tiberium field pays what the
  Ore field it replaced paid. Gems pay more, which is one reason they never turn.

## Traps

- **Build from the MIX, never from an editor save.** A save from the editor flattens GOLD1-4 and
  GEMS1-4 to GOLD1 / GEMS1 and can drop cells and terrain. `map-edits/scm05ea.ini` is such a save
  (it lost 7 ore cells and a mine); it is not a source.
- **`build_tiberium_hd.py` with no arguments rebuilds the temperate and interior tilesets from
  the base game's**, which drops every tile other scripts have added to them since. Pass the
  theatre you mean (`SNOW`); only the snow row splices into the existing file.
- **`mapeditor.json` has no TIB01 or TDBLOSSOM entry.** `cncmap edit --place-overlay` cannot
  place Tiberium by name, and the editor draws no blossom tree. Adding both to
  `scripts/editor_manifest.py` would fix it.
- **`MAIN.MIX` is an extended, unencrypted MIX.** `mix_tools.read_mix` and `ra_mix_extract.py` do
  not parse it; the builder has its own reader.
- **Maps can hide extra mines.** Keep off the Grass has three: the survey lists them all.
- **Docklands' thumbnail keeps the gem speckle of its converted mixed fields.** The repaint only
  picks up tan Ore speckle, while the map itself turns those Gem cells to Tiberium
  (`take_gems`). Every other map converts pure-Ore fields only, so its thumbnail matches.
- **`meg_extract.py` reads the whole MEG into memory.** Fine for `CONFIG.MEG`, slow for the
  2.4 GB `TEXTURES_SRGB.MEG`; the builder seeks instead.

## Maps done

Mix is counted in resource cells at map start (Tiberium / Ore / Gems).

| Map | Theatre | Mix | Converted | Kept as Ore | Status |
|---|---|---|---|---|---|
| `scm05ea.ini` Keep off the Grass (Sm, 2p) | temperate | Tiberium-leaning 55%: 181 / 68 / 78 | mines 5714 (East field), 9901 (South-West field) | both home patches, centre gems, mine 7890 | map and thumbnail proven on the Deck 2026-09-14 |
| `scm02ea.ini` Middle Mayhem (Sm, 2p) | snow | 33%: 183 / 329 / 49 | four of the island's five fields and their mines | the island field at mine 7888 (it holds gems) and everything outside the ring | played on the desktop 2026-09-14 (first snow map), rebuilt under the gem rules since |
| `scm09ea.ini` North By Northwest (Lg, 8p) | snow | 54%: 666 / 403 / 168 | the 4 corner fields and their mines, the 4 diagonal fields | the centre (it holds gems), the edge fields and the gem patches | built 2026-09-14 |
| `scm10ea.ini` First Come, First Serve (84x84, 4p) | temperate | Ore-heavy 10%: 68 / 594 / 0 | the centre field, its mine | both big flank fields and every small field | built 2026-09-14 |
| `scm111ea.ini` Docklands (8p) | snow | split by the river, 53%: 360 / 144 / 173 | everything west of the river, mixed Ore/Gem fields whole (`take_gems`; 6 mines, 2 mineless fields) | the all-gem box in the west, and everything east of the river | played on the desktop 2026-09-14, all-gem box restored since |
