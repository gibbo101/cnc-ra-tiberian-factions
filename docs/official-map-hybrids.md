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
  (512x512 DXT5, 10 mips, the playable area stretched to fill it, no trees or mines drawn).
- The key comes from the `CNCMapPreviewData` XML in `CONFIG.MEG`: one
  `<INIData Name="MOBIUS_RED_ALERT_MULTIPLAYER_<N>_MAP">` per map, holding only its bounds and
  start waypoints. It names no file, so the builder finds a map's key by matching its bounds and
  starts (Keep off the Grass = `_5_`).
- A DDS of the same name loose under the mod's `Data/ART/TEXTURES/SRGB/` overrides the stock one;
  the front end reads loose overrides (`front-end-texture-meg-spike.md`).

### Both

- The build copies `resources/remaster_mods/Vanilla_RA/` (CCDATA and Data included) into
  `build/remaster/Vanilla_RA/` (`redalert/CMakeLists.txt`), so both files ship with every build
  and Workshop package.
- Both are data only. Deploying one map means copying its `.ini` into the target's `CCDATA/` and
  its DDS into the target's `Data/ART/TEXTURES/SRGB/`, then md5-checking both; the DLL is
  untouched.

## The builder: `scripts/official_map_hybrid.py`

```bash
python3 scripts/official_map_hybrid.py --survey scm05ea.ini   # fields, mines and starts of a map
python3 scripts/official_map_hybrid.py                        # rebuild every map in HYBRIDS
python3 scripts/official_map_hybrid.py scm05ea.ini            # rebuild one
```

`HYBRIDS` maps an official file name to the ore-mine cells to convert (cell = `y*128 + x`).

**The map.** For each mine the script:

1. takes the mine's field: the Ore/Gem cells within 2 cells of the mine, grown out through every
   8-connected Ore/Gem neighbour;
2. sets those cells to `OVERLAY_TIB01` (25) in `[OverlayPack]`; the engine works out density when
   the map loads;
3. drops the mine's `<cell>=MINE` line from `[TERRAIN]`;
4. adds `Neutral,TDBLOSSOM,256,<cell>,0,None` to `[STRUCTURES]`, the same line `td_map_to_ra.py`
   writes for TD blossom trees. The blossom seeds Tiberium itself (`BuildingClass::AI`).

Every other line is carried over byte for byte. The script reads the pristine map straight from
`MAIN.MIX`, re-decodes its own `[OverlayPack]` output as a check, and writes the result to
`resources/remaster_mods/Vanilla_RA/CCDATA/<map>.ini`. The OverlayPack codec is the
`td_map_to_ra.py` one that the shipped TD map pack already uses.

**The thumbnail.** The script then:

1. finds the preview key in `CONFIG.MEG` (bounds and starts must match exactly one entry);
2. reads the stock DDS from `TEXTURES_SRGB.MEG` by seeking through its index (the MEG is 2.4 GB);
3. recolours the tan Ore speckle over the converted cells, with the mask grown 11 px to catch
   sprites that overhang their cell. Each pixel moves towards the Tiberium colour in proportion
   to how far it sits from grass towards the field's mean Ore colour, so grass, cliffs and roads
   stay untouched. The Tiberium colour is the speckle hue of EA's own TD thumbnails
   (`77, 92, 42`), raised to the brightness of the map's Ore speckle;
4. encodes the image as DXT5 with the stock mip count (`scripts/dds_dxt5.py`), reuses the stock
   128-byte header, asserts the file is exactly the stock size, and writes it to
   `resources/remaster_mods/Vanilla_RA/Data/ART/TEXTURES/SRGB/<key>.DDS`.

## Converting another map

1. **Survey.** `--survey <map>` lists every Ore/Gem field (size, bounding box, Ore vs Gems, the
   mines within reach) plus the start waypoints. Map names are in `map-edits/_official_map_list.ini`
   (the classic set); the full 230 extract with
   `cnc-map-editor` `OfficialMaps.Extract` to `cnc-map-editor/artifacts/test-output/official/`.
2. **Choose the mix.** The Tiberium/Ore split varies from map to map on purpose: some maps near
   50/50, some Tiberium-heavy, some Ore-heavy (Luke, 2026-09-14). No map has to be even. What
   stays fair is each start's access: on a mirrored map, convert fields in mirrored pairs so
   every start gets the same deal. Record the mix in the table below, so the pool as a whole
   keeps a spread. Only fields with a mine get a blossom; a mineless field (which a
   Tiberium-heavy map will usually need) can be converted once the script grows a field-cell
   option.
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
6. **Play.** Copy both files to the test surface, md5 both ends, and look at the lobby thumbnail
   and a skirmish on the map.

## How the resources behave once placed

- Tiberium and Ore never convert each other. Spreading only lands on an empty cell
  (`CellClass::Can_Tiberium_Germinate`) and each field spreads as its own type
  (`CellClass::Spread_Tiberium`), so where two fields meet they hold a border. A remaining ore
  mine next to a Tiberium field grows Ore up to that border. (`todo.md` holds the open idea of
  Tiberium eating Ore.)
- The blossom tree seeds TIB01 into empty neighbouring cells.
- An ordinary tree with 6 or more TIB01 neighbours turns into a blossom tree
  (`redalert/terrain.cpp`).

## Traps

- **Build from the MIX, never from an editor save.** A save from the editor flattens GOLD1-4 and
  GEMS1-4 to GOLD1 / GEMS1 and can drop cells and terrain. `map-edits/scm05ea.ini` is such a save
  (it lost 7 ore cells and a mine); it is not a source.
- **`mapeditor.json` has no TIB01 or TDBLOSSOM entry.** `cncmap edit --place-overlay` cannot
  place Tiberium by name, and the editor draws no blossom tree. Adding both to
  `scripts/editor_manifest.py` would fix it.
- **`MAIN.MIX` is an extended, unencrypted MIX.** `mix_tools.read_mix` and `ra_mix_extract.py` do
  not parse it; the builder has its own reader.
- **Maps can hide extra mines.** Keep off the Grass has three: the survey lists them all.
- **Gems in a converted field keep their colour in the thumbnail.** The repaint only picks up tan
  Ore speckle. In the map itself the gem cells do become Tiberium.
- **`meg_extract.py` reads the whole MEG into memory.** Fine for `CONFIG.MEG`, slow for the
  2.4 GB `TEXTURES_SRGB.MEG`; the builder seeks instead.

## Maps done

Mix is counted in resource cells at map start (Tiberium / Ore / Gems).

| Map | Mix | Converted (mine cell -> blossom) | Kept as Ore | Thumbnail | Status |
|---|---|---|---|---|---|
| `scm05ea.ini` Keep off the Grass (Sm, 2 players) | Tiberium-leaning: 181 / 68 / 78 | 5714 (82,44) East field, 9901 (45,77) South-West field | both home patches, centre gems, mine 7890 (82,61) | `MOBIUS_RED_ALERT_MULTIPLAYER_5_MAP.DDS` | map and thumbnail both proven on the Deck 2026-09-14 |
