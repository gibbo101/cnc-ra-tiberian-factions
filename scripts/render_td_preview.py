#!/usr/bin/env python3
"""
Classic-art preview renderer for converted TD maps (Tiberian Factions mod).

The two community TD maps carry an embedded [CnCNetPreview] PNG, but the 14
classic MP maps (GENERAL.MIX scm*) predate that tooling. This module renders
an equivalent authentic top-down preview straight from the classic theater
art: template iconsets + tiberium overlay + terrain SHPs from TEMPERAT.MIX,
coloured by TEMPERAT.PAL, with red start-position dots -- the same look
CnCNet's preview generator produces. Used by td_map_to_ra.convert as the
preview source when the TD ini has no [CnCNetPreview].

Format notes (verified against common/iconset.cpp + our td_tem_to_ra):
- TD template .tem = ICONSET: 32-byte header (icon_w, icon_h, count, alloc
  as i16; size, icons_off, pal_off, remaps_off, trans_off, map_off as i32).
  Icon pixels are raw 8bpp icon_w*icon_h blocks at icons_off; the table at
  map_off maps LOGICAL icon (the .bin TIcon) -> physical block, 0xFF = blank.
- Overlay ti1..ti12.tem and terrain t01..split2 .tem are SHP-format (LCW
  keyframe chains -- shptools.decode_shp), palette index 0 = transparent.
"""
import io, os, struct, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mix_tools import read_mix, ww_crc
from shptools import decode_shp, load_pal

GAME = os.path.expanduser("~/.steam/steam/steamapps/common/CnCRemastered")
TD_CD1 = os.path.join(GAME, "Data/CNCDATA/TIBERIAN_DAWN/CD1")

CELL = 24      # classic icon size
TD_W = 64

_theaters = {}


class TheaterArt:
    def __init__(self, mix_path, pal_path):
        _count, _ds, entries, blob = read_mix(mix_path)
        self.index = {crc & 0xFFFFFFFF: (off, size) for crc, off, size in entries}
        self.blob = blob
        self.pal = [(r << 2, g << 2, b << 2) for r, g, b in load_pal(pal_path)]
        self._cache = {}

    def file(self, name):
        e = self.index.get(ww_crc(name) & 0xFFFFFFFF)
        if e is None:
            return None
        off, size = e
        return self.blob[off:off + size]

    def iconset(self, name):
        """-> (data, icons_off, map_off) or None."""
        if name not in self._cache:
            data = self.file(name + ".tem")
            if data is None:
                self._cache[name] = None
            else:
                _w, _h, _cnt, _alloc = struct.unpack_from("<4h", data, 0)
                _size, icons_off, _p, _r, _t, map_off = struct.unpack_from("<6i", data, 8)
                self._cache[name] = (data, icons_off, map_off)
        return self._cache[name]

    def shp(self, name):
        """-> (hdr, frames) or None; cached."""
        key = "shp:" + name
        if key not in self._cache:
            data = self.file(name + ".tem")
            if data is None:
                self._cache[key] = None
            else:
                try:
                    self._cache[key] = decode_shp(data)
                except Exception:
                    self._cache[key] = None
        return self._cache[key]


def theater_art(theater):
    t = theater.lower()
    if t not in _theaters:
        if t != "temperate":
            raise NotImplementedError(f"theater {theater} not wired yet")
        _theaters[t] = TheaterArt(os.path.join(TD_CD1, "TEMPERAT.MIX"),
                                  os.path.join(TD_CD1, "TEMPERAT.PAL"))
    return _theaters[t]


def _blit_icon(px, ox, oy, art, iconset, logical):
    data, icons_off, map_off = iconset
    phys = data[map_off + logical]
    if phys == 0xFF:
        return
    base = icons_off + phys * CELL * CELL
    pal = art.pal
    for y in range(CELL):
        row = data[base + y * CELL:base + (y + 1) * CELL]
        for x in range(CELL):
            px[ox + x, oy + y] = pal[row[x]]


def _blit_shp(px, ox, oy, art, hdr, frame, canvas_w, canvas_h):
    w, h = hdr["width"], hdr["height"]
    pal = art.pal
    for y in range(h):
        py = oy + y
        if py < 0 or py >= canvas_h:
            continue
        row = frame[y * w:(y + 1) * w]
        for x in range(w):
            c = row[x]
            if c == 0:
                continue
            pxx = ox + x
            if 0 <= pxx < canvas_w:
                px[pxx, py] = pal[c]


def render(theater, bindata, td_by_id, overlay_entries, terrain_entries,
           start_cells_td, bounds):
    """Render the TD source to a 512x512 PIL image covering the playable
    bounds (the lobby-TGA convention). bounds = (x, y, w, h) in TD cells;
    start_cells_td = TD-grid cell numbers; overlay/terrain_entries =
    [(cell, name)] with classic lowercase names."""
    from PIL import Image
    art = theater_art(theater)
    W = H = TD_W * CELL
    im = Image.new("RGB", (W, H), (0, 0, 0))
    px = im.load()

    # terrain templates (clear cells use clear1's positional 4x4 icon grid)
    for cy in range(TD_W):
        for cx in range(TD_W):
            t = bindata[(cy * TD_W + cx) * 2]
            ic = bindata[(cy * TD_W + cx) * 2 + 1]
            if t == 0xFF:
                name, ic = "clear1", (cx & 3) + (cy & 3) * 4
            else:
                name = td_by_id.get(t, ("clear1", 0, 0))[0]
            iconset = art.iconset(name)
            if iconset is None:
                continue
            try:
                _blit_icon(px, cx * CELL, cy * CELL, art, iconset, ic)
            except IndexError:
                pass

    # overlays -- SHPs drawn over the cell. TD tiberium = 12 visual variants
    # (ti1..ti12), each with 12 DENSITY FRAMES; the engine (Tiberium_Adjust)
    # picks the frame from the neighbour count at load, so interior cells of
    # a field render full growth. Mirror that: keep the authored variant,
    # choose the frame by adjacency.
    tib = {cell for cell, name in overlay_entries if name.startswith("ti")}
    for cell, name in overlay_entries:
        cx, cy = cell % TD_W, cell // TD_W
        shp = art.shp(name)
        if shp is None:
            continue
        hdr, frames = shp
        fi = 0
        if name.startswith("ti"):
            adj = sum(1 for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                      if (dx or dy) and 0 <= cx + dx < TD_W and 0 <= cy + dy < TD_W
                      and (cell + dy * TD_W + dx) in tib)
            fi = min(len(frames) - 1, adj + 3)
        _blit_shp(px, cx * CELL, cy * CELL, art, hdr, frames[fi], W, H)

    # terrain objects (trees; split2 blossom rests on its open frame 34)
    for cell, name in terrain_entries:
        shp = art.shp(name)
        if shp is None:
            continue
        hdr, frames = shp
        fi = min(34, len(frames) - 1) if name.startswith("split") else 0
        cx, cy = cell % TD_W, cell // TD_W
        _blit_shp(px, cx * CELL, cy * CELL, art, hdr, frames[fi], W, H)

    # start positions -- red dots, CnCNet style
    for cell in start_cells_td:
        cx, cy = cell % TD_W, cell // TD_W
        x0, y0 = cx * CELL + CELL // 2 - 5, cy * CELL + CELL // 2 - 5
        for y in range(10):
            for x in range(10):
                if 0 <= x0 + x < W and 0 <= y0 + y < H:
                    px[x0 + x, y0 + y] = (220, 30, 30)

    bx, by, bw, bh = bounds
    im = im.crop((bx * CELL, by * CELL, (bx + bw) * CELL, (by + bh) * CELL))
    return im.resize((512, 512), Image.LANCZOS)


def render_png(theater, bindata, td_by_id, overlay_entries, terrain_entries,
               start_cells_td, bounds):
    buf = io.BytesIO()
    render(theater, bindata, td_by_id, overlay_entries, terrain_entries,
           start_cells_td, bounds).save(buf, "PNG")
    return buf.getvalue()
