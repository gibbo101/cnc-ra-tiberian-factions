# SPIKE: maps larger than 128x128 ("mega maps") in Red Alert

**Status:** **CLOSED — RESOLVED NEGATIVE for the Remastered target (2026-07-18).** RA's playable ceiling of **126x126** (a 128x128 cell array minus the 1-cell border) is enforced by the **closed-source `ClientG.exe`**, not by our DLL. The engine-side change is tractable and EA already did an equivalent one; the launcher ABI is what stops it, and it cannot be recompiled. **Do not re-chase for the shipped mod.** Larger maps are genuinely reachable only on the standalone `VanillaRA` build, which bypasses the launcher and is not what we ship.

**One-line:** Can we raise `MAP_CELL_W`/`MAP_CELL_H` above 128 to ship bigger skirmish maps? No: terrain rendering is launcher-owned, and the launcher's map export buffer is a fixed 128x128 that our DLL fills but does not allocate.

This doc is self-contained. It records both the wall and the engine-side survey, so neither has to be redone.

---

## VERDICT

**The wall is ABI, not engine.** That is the decision rule for anything in this area: if a change grows a struct in `redalert/dllinterface.h`, it is dead on arrival regardless of how clean the DLL-side work is.

### The decisive evidence

`tiberiandawn/dllinterface.h:31` defines:

```c
#define MAX_EXPORT_CELLS (128 * 128)
```

...for a game whose map is **64x64** (`MAP_MAX_CELL_WIDTH 64`, same file, line 34). TD wastes three quarters of that array. There is only one explanation: **`MAX_EXPORT_CELLS` is `ClientG.exe`'s single shared buffer size**, sized to the largest title (RA) and used identically for both DLLs. It is a launcher-side number that the GPL headers merely mirror. **The DLL does not get to pick it** — TD proves that.

The same constant appears at `redalert/dllinterface.h:31`, backing two fixed-size arrays inside structs the launcher allocates and the DLL fills:

- `dllinterface.h:106` — `CNCStaticCellStruct StaticCells[MAX_EXPORT_CELLS]` inside `CNCMapDataStruct` (36 bytes/cell x 16384 = ~576 KB)
- `dllinterface.h:778` — `DllActionTypeEnum ActionWithSelected[MAX_EXPORT_CELLS]` inside `CNCPlayerInfoStruct`

Both are `#pragma pack(1)` (`dllinterface.h:46`) — positional, byte-exact. The DLL receives `unsigned char* buffer_in, unsigned int buffer_size` from the launcher (`CNC_Get_Game_State`, `dllinterface.cpp:3956`); it never allocates them.

### Both escape routes fail

**Route A — raise `MAX_EXPORT_CELLS`.** `sizeof(CNCMapDataStruct)` grows ~4x, but the launcher still passes its old `buffer_size`. Our own guard fires:

```c
// dllinterface.cpp:3997
if (buffer_size < sizeof(CNCMapDataStruct)) {
    got_state = false;
    break;
}
```

`GAME_STATE_STATIC_MAP` returns false forever → **no terrain renders at all.** Fail-closed rather than a crash, but unplayable. It also shifts the offset of every field after `StaticCells`, desyncing the positional CRC'd `Export_State`/`Import_State` BitStream.

**Route B — leave the constant, raise only `MAP_CELL_W/H`.** Silent overflow. `dllinterface.cpp:7458`:

```c
int index = 0;
for (int y = top; y <= bottom; ++y) {
    for (int x = left; x <= right; ++x, ++index) {
        Convert_Action_Type(..., player_info->ActionWithSelected[index]);
    }
}
```

No bound check against `MAX_EXPORT_CELLS`. A 256x256 playable area writes 65536 entries into a 16384-entry array — a ~48 KB overrun into the launcher's buffer **on every selection**. CTD in `InstanceServerG`. The static-map fill loop (`dllinterface.cpp:4045`) has the same unchecked `cell_index++`.

### There is no negotiation channel

`CNC_Get_Game_State` returns a bare `bool`. The variable-length exports (`Get_Shroud_State`, `Get_Occupier_State`, `Get_Placement_State`, `Get_Dynamic_Map_State`) *do* bounds-check, but only `return false` on overflow — the DLL has no way to ask the launcher for a bigger buffer. And `ClientG`'s only contact with our DLL is a version handshake: `GetProcAddress("CNC_Version")` → compare `0x102` (`redalert/dllinterfaceversion.h:18`) → `FreeLibrary`. Bumping the version to signal a new ABI just fails the handshake.

### The wire types cap at 256 anyway

Even ignoring the buffer, the exported field widths top out at exactly 256 cells:

- `dllinterface.h:508-509` — `CNCDynamicMapEntryStruct.CellX/CellY` are **`unsigned char`** (max 255), assigned raw `Cell_X(cell)`/`Cell_Y(cell)`.
- `dllinterface.h:768-769` — `CNCPlayerInfoStruct.HomeCellX/HomeCellY` are **`unsigned char`**, assigned absolute start-position cells.
- `dllinterface.h:200-201` — `CNCObjectStruct.CenterCoordX/CenterCoordY` are **`unsigned short`** holding *leptons*. At 256 leptons/cell, a 256-cell map reaches 65536 — one past the type.

So the ABI was never going to reach even the theoretical coordinate-system limit, let alone beyond it.

### Where this sits in the ownership map

Same family as the classic-mode spacebar toggle and the hotkey-class walls in `launcher-vs-dll-ownership.md`: that doc lists `CNCObjectStruct` / `CNCDynamicMapStruct` / `CNCMapDataStruct` / `CNCShroudStruct` explicitly as **render data** pulled by the launcher. Terrain rendering is launcher-owned; the DLL only supplies per-cell payload. Its own criterion applies: *"the CNC ABI **is** the process-boundary wire format, not a soft convention."*

**The one flexibility that exists is already fully exploited:** `MapCellX/Y/Width/Height` are genuinely dynamic and every export clamps against `MAP_MAX_CELL_WIDTH/HEIGHT`. That is how RA ships 62x62, 96x96 and so on. Variable map sizes work fine — bounded above by 128. We are at the top of the envelope, not partway up it.

---

## Engine-side survey (for the `VanillaRA` path only)

Recorded because it is the non-obvious half: **the DLL side is the easy part.** If the launcher ever stopped being the target, this is the shape of the work.

### Precedent: EA already did this once

`MEGAMAPS` is a real EA-era compile flag in Tiberian Dawn (`tiberiandawn/defines.h:257`) taking TD from 64x64 to 128x128, and it is **enabled** in the Remastered build (`tiberiandawn/CMakeLists.txt:184`, `:233`). TD parameterised its cell packing as `MAP_CELL_MAX_X_BITS`/`MAP_CELL_MAX_Y_BITS`; **RA never did** — RA hardcodes `X:7, Y:7` at `redalert/defines.h:534`. The change touched only ~10 files.

But EA's jump stopped at 7+7 = 14 bits, comfortably inside a `signed short`. Ours would not (see below). That is the key difference.

### The two type-system ceilings

```c
// redalert/defines.h:520-539
typedef signed short CELL;
typedef union {
    CELL Cell;
    struct { unsigned short X : 7; unsigned short Y : 7; } Sub;   // + sluff:2 on big-endian
} CELL_COMPOSITE;
```

1. **`CELL` is `signed short`.** 256x256 = 65536 cells needs 8+8 bits and overflows 32767. `CELL` must become `int`.
2. **`COORDINATE` caps at 256 cells/axis.** `defines.h:489-518` — `LEPTON` is `unsigned short` split `{ unsigned char Lepton; unsigned char Cell; }`. Widening past 256 makes `COORDINATE` 64-bit, which touches the network protocol and every `TARGET` pack. **256 is therefore the natural and only sane target.**

### What is genuinely clean

The codebase is unusually disciplined — **zero** hardcoded `128`/`127`/`0x7F`/`>>7`/`<<7` map-packing constants outside `defines.h` and two lines of `dllinterface.cpp`. Everything routes through the union (`XY_Cell` `inline.h:219`, `Cell_X` `inline.h:326`, `Cell_Y` `inline.h:345`, `Cell_Coord` `inline.h:434`, `Coord_Cell` `coord.cpp:69`) and auto-adapts. Specifically verified safe:

- **`-1` cell sentinels all survive.** Always written as the literal `-1` and compared against `-1`, never derived from the bitfield. ~25 sites incl. `display.h:177,193`, `crate.h:66`, `unit.h:166-175`, `findpath.cpp:1446`.
- **`REFRESH_EOL` (32767) / `REFRESH_SIDEBAR` (32766) are unaffected.** They only terminate `short const*` **offset** lists holding bounded deltas (`±MAP_CELL_W * n`, max ~1792 at 256), never CELL identities. **Keep those lists `short`** — retyping them as `CELL[]` would make `REFRESH_EOL` collide with valid cell 32767.
- **`As_Target` fits 256 exactly.** `target.cpp:817` packs 12 bits/axis into a 24-bit mantissa: `255*16+8 = 4088 <= 4095`. Seven units of slack. Worth a `static_assert(MAP_CELL_W <= 256)`.
- **The `(unsigned)cell < MAP_CELL_TOTAL` bounds idiom becomes *correct*** under widening (today a `short` can never exceed 32767, so the check would pass for the whole upper half).
- **Regions auto-scale.** `MAP_REGION_WIDTH/HEIGHT` (`defines.h:588`) are derived macros with a `+2` guard border; `HouseClass::Regions[]` grows ~4.6 KB → ~17 KB per house.
- **Memory is a non-issue.** ~+7 MB total, dominated by `MapClass::Array` (~2 MB → ~8 MB). `MapClass::Alloc_Cells` already sizes dynamically from `Size`.

### What actually has to change

1. `defines.h:474-539` — `MAP_CELL_W/H` to 256, `CELL` to `int`, bitfields to `X:8, Y:8`, and **delete the big-endian `sluff:2`** or the fields shift. Easy to miss.
2. `cell.h:63` — `short ID` → `int ID`. Set from `Map.ID(this)` (an `int`) at `cell.cpp:105`. At 65536 cells every index >= 32768 goes **negative**, propagating into `Cell_Number()`, `As_Target()` and `xTargetClass::As_Cell()` (`target.cpp:96`) → out-of-bounds read across the bottom half of the map.
3. `globals.cpp:139` — `_staging_buffer[32000]` must grow to ~256 KB and gain an overflow guard. It is the only buffer for MapPack/OverlayPack/`[TFTDTiles]` encode (`display.cpp:4884,4996`, `map.cpp:1217`, `overlay.cpp:261,353`).
4. `map.cpp:1910` — `Zone_Span` is a **recursive** scanline flood fill; depth scales with map area and runs once per `MZONE_*` (5x). Stack overflow risk at 65K cells. Convert to an explicit stack.
5. `cell.h:124` — `unsigned char Zones[MZONE_COUNT]`: zone **IDs** cap at 255. `Zone_Reset` (`map.cpp:1801`) increments per flood fill with no overflow guard; a fragmented 256x256 map (islands, many small water bodies) can alias zone IDs and make unrelated landmasses look connected, so units accept impossible move orders.
6. `dllinterface.cpp:6092` **and** `6832` — two duplicated `static const int _map_width_shift_bits = 7;`. De-duplicate.
7. **Radar needs a design decision, not a constant.** `RadarClass::Zoom_Mode` (`radar.cpp:850`) computes `ZoomFactor = max(min(RadIWidth/MapCellWidth, ...), 1)`; at 256 that is 1, and `map_c_width = min(256, RadIWidth=146)` = 146. The "see whole map" mode can only ever show 146x130 of a 256x256 map — the minimap silently becomes a second scrolling window. Needs a sub-pixel/averaged render path or a bigger widget.

### The format migration is the real project

The code surface is small and localised; the file formats are what bite.

- **MapPack/OverlayPack carry no dimensions.** `MapClass::Write_Binary`/`Read_Binary` (`map.cpp:1217`, `:1253`) and `overlay.cpp:263,353` loop `MAP_CELL_TOTAL` unconditionally, so the reader just pulls exactly 16384 entries. Layout (`NewINIFormat >= 3`): 16384 x `uint16` TType then 16384 x `uint8` TIcon = 49152 bytes, LCW-framed in 8192-byte blocks, base64'd into 70-char lines by `INIClass::Put_UUBlock` (`common/ini.cpp:548`). Since the framing is length-agnostic, a `NewINIFormat = 4` case is genuinely easy — roughly a day.
- **Existing maps need a re-stride, not a memcpy.** Cell N in a 128-wide grid is a *different* (x,y) in a 256-wide grid. The format-3 load path must re-stride explicitly.
- **`[Map] X/Y/Width/Height` are unvalidated ints** (`display.cpp:4756`) describing only the playable *window* into the always-128x128 array. The old 96x96 clamp is already compiled out under `FIXIT_VERSION_3` ("map size no longer restricted").
- **Savegames break.** `MouseClass::Save`/`Load` (`iomap.cpp:312`, `:206`) do a raw `sizeof(*this)` struct dump of the whole map object, and `ScenarioClass` is bulk-blitted (`saveload.cpp:108`) containing `CELL Waypoint[]`. Any layout change invalidates every existing save. Cell indices are also written as `file.Put(&cell, sizeof(cell))` — 2 bytes becomes 4.
- **MP/replay wire format shifts.** `EventClass` (`event.h`, `#pragma pack(1)`) carries `CELL Cell` in `SellCell`/`Place`/`Special`, so `sizeof(EventClass)` grows, affecting `MAX_IPX_PACKET_SIZE` (`session.h:72`) and recorded games. Mercifully `EventClass::EventLength[]` (`event.cpp:59`) is built from `size_of(...)` and self-adjusts.

---

## Curiosity worth recording: 128 x 255 is free

There is exactly one shape that doubles the playable area **without** widening `CELL`.

With bitfields `X:7, Y:8`, the maximum cell is `XY_Cell(127, 255)` = `127 | (255 << 7)` = **32767** = `0x7FFF` — precisely `INT16_MAX`, fitting `signed short` with zero bytes to spare. The `-1` sentinel stays safe because `-1` is `0xFFFF` and bit 15 is never set by a valid cell.

Two caveats if it is ever used:

1. **Use 255 tall, not 256.** `Cell_To_Lepton` does `lepton.Sub.Cell = (unsigned char)cell_distance` (`inline.h:242`), so a map *height* of exactly 256 truncates to **0** — and `display.cpp:4285` feeds that straight into `Confine_Rect` as the clamp bound, collapsing vertical scroll clamping. 256 is the exact breaking extent, not a safe one.
2. **Cell 32767 numerically equals `REFRESH_EOL`.** Safe only while the offset lists stay `short` and never mix with CELL identities (see above). It converts a currently-impossible collision into a live one.

**This does not help the shipped mod.** 128 x 255 = 32640 cells against a 16384-cell export buffer — still 2x over. The launcher cap is on *total cells*, so no aspect ratio rescues it.

---

## Spillover: two bugs found that are independent of map size

Both are live on the current 128x128 build.

1. **A\* has an O(n^2) insert and no expansion cap** — `findpath.cpp:715` uses `open_list.insert(std::lower_bound(...))` into a `std::vector` (sorted-vector priority queue, linear insertion). Worse, there is **no node-expansion budget**: a *failed* search against an unreachable destination exhausts the entire reachable component. At 128x128 that is <=16K nodes with per-node `unordered_map` allocation — a long-range failed path can stall a frame. Recommend a real binary heap plus an explicit expansion budget with fallback. Relevant to the AI milestone.
2. **`defines.h:589` copy-paste typo** — `MAP_REGION_HEIGHT` uses `REGION_WIDTH` in its rounding term instead of `REGION_HEIGHT`. Harmless while both are 4; a landmine if regions ever go non-square.

---

## Bottom line

126x126 is the ceiling for anything running under the Remastered launcher, and it is not a soft limit we can engineer around from the DLL. The decision rule for future work in this area: **if it grows a struct in `dllinterface.h`, it is dead.**
