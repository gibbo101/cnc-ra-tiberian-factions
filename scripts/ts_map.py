#!/usr/bin/env python3
"""Reads Tiberian Sun maps and their theatre tiles from an installed Tiberian Sun: cells, heights,
land types, overlays, terrain objects, waypoints and the tiles' own art.

License: GPL v3.
"""
import base64
import os
import re
import struct
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lzo1x  # noqa: E402
import shptools  # noqa: E402
import steam_library  # noqa: E402
import ts_mix  # noqa: E402

TS_DIR = str(steam_library.path("common/Command & Conquer Tiberian Sun"))

# A tile's control colour (0-15) to its land type, as TS's IsometricTileTypeClass::Land_Type maps it.
CONTROL_LAND = ["clear", "ice", "ice", "ice", "ice", "tunnel", "railroad", "rock",
                "rock", "water", "beach", "road", "road", "clear", "rough", "rock"]

# (tileset INI, tile MIX, tile file extension, palette) per theatre.
THEATRES = {"TEMPERATE": ("TEMPERAT.INI", "ISOTEMP.MIX", "tem", "ISOTEM.PAL"),
            "SNOW": ("SNOW.INI", "ISOSNOW.MIX", "sno", "ISOSNO.PAL")}



def diamond_rows(width, height):
    """(first column, width) of each drawn pixel row of a tile diamond: 48x24 in TS, 60x30 in RA2."""
    half = height // 2
    widths = [4 + 4 * r if r < half else 4 + 4 * (2 * half - 2 - r) for r in range(height - 1)]
    return [(width // 2 - w // 2, w) for w in widths]


def parse_ini(text):
    """{section: {key: value}} of an INI text, keys in file order, comments stripped."""
    sections, current = {}, None
    for line in text.replace("\r", "").split("\n"):
        line = line.split(";", 1)[0].strip()
        if line.startswith("[") and "]" in line:
            current = sections.setdefault(line[1:line.index("]")], {})
        elif current is not None and "=" in line:
            key, value = line.split("=", 1)
            current[key.strip()] = value.strip()
    return sections


def unpack_blocks(section, decode):
    """The bytes of a base64 map pack whose blocks (u16 packed, u16 unpacked, data) `decode` unpacks."""
    raw = base64.b64decode("".join(section[k] for k in sorted(section, key=int)))
    out, i = bytearray(), 0
    while i < len(raw):
        packed, unpacked = struct.unpack_from("<HH", raw, i)
        out += decode(raw[i + 4:i + 4 + packed], unpacked)
        i += 4 + packed
    return bytes(out)


def split_cell(number):
    """(x, y) of a TS map cell number (y * 1000 + x)."""
    return number % 1000, number // 1000


class TsInstall:
    """The archives of an installed Tiberian Sun, opened as needed."""

    def __init__(self, folder=TS_DIR):
        self.folder = folder
        self.tibsun = open(os.path.join(folder, "TIBSUN.MIX"), "rb").read()
        self._members = {}

    def member(self, container, name):
        """A file inside TIBSUN.MIX's `container` archive (LOCAL.MIX, CACHE.MIX, ISOTEMP.MIX ...)."""
        if container not in self._members:
            self._members[container] = ts_mix.member(self.tibsun, container)
        return ts_mix.member(self._members[container], name)

    def maps(self, archive="multi.mix"):
        """{map name: map text} of every map in an archive of the install."""
        blob = open(os.path.join(self.folder, archive), "rb").read()
        found, start, raw = ts_mix.entries(blob)
        maps = {}
        for crc, offset, size in found:
            data = raw[start + offset:start + offset + size]
            if b"IsoMapPack5" in data:
                text = data.decode("latin-1")
                maps[parse_ini(text).get("Basic", {}).get("Name", hex(crc))] = text
        return maps

    def overlay_names(self):
        """TS's overlay type names, by overlay index."""
        rules = parse_ini(self.member("LOCAL.MIX", "RULES.INI").decode("latin-1"))
        return [v for _k, v in rules["OverlayTypes"].items()]

    def palette(self, name):
        """A palette's 256 RGB colours, scaled from 6 to 8 bits."""
        data = self.member("CACHE.MIX", name)
        return [tuple(min(255, c * 4) for c in data[i * 3:i * 3 + 3]) for i in range(256)]


class Tileset:
    """A theatre's tiles: each tile index's set name and file, and the tiles' records and art."""

    def __init__(self, install, theatre):
        ini_name, self.mix, self.ext, pal = THEATRES[theatre]
        self.install = install
        self.palette = install.palette(pal)
        ini = parse_ini(install.member("LOCAL.MIX", ini_name).decode("latin-1"))
        self.tiles = []
        for name in sorted((s for s in ini if re.fullmatch(r"TileSet\d{4}", s)), key=lambda s: int(s[7:])):
            entry = ini[name]
            for i in range(int(entry.get("TilesInSet", 0))):
                self.tiles.append((entry.get("SetName", ""), f"{entry.get('FileName', '')}{i + 1:02d}.{self.ext}"))
        self._records = {}

    def fixup(self, tile):
        """The tile index TS draws for a stored one: anything out of range is clear ground."""
        return tile if 0 <= tile < len(self.tiles) else 0

    def records(self, tile):
        """The sub-tile records of a tile, None for an empty sub-tile."""
        tile = self.fixup(tile)
        if tile not in self._records:
            self._records[tile] = self._read(self.tiles[tile][1])
        return self._records[tile]

    def record(self, tile, sub):
        """One sub-tile's record; a missing sub-tile reads as clear ground."""
        recs = self.records(tile)
        rec = recs[sub] if 0 <= sub < len(recs) else None
        return rec or self.records(0)[0]

    def _read(self, file_name):
        data = self.install.member(self.mix, file_name)
        if data is None:
            return [None]
        width, height, self.block_w, self.block_h = struct.unpack_from("<4i", data, 0)
        size = self.block_w * self.block_h // 2
        recs = []
        for offset in struct.unpack_from(f"<{width * height}i", data, 16):
            if offset == 0:
                recs.append(None)
                continue
            x, y, extra_off, _z, _ez, ex, ey, ew, eh, flags, height_lvl, control, ramp = \
                struct.unpack_from("<9iIBbb", data, offset)
            rec = {"x": x, "y": y, "height": height_lvl, "land": CONTROL_LAND[control & 15], "ramp": ramp,
                   "pixels": data[offset + 52:offset + 52 + size], "extra": None}
            if flags & 1:
                rec["extra"] = (ex, ey, ew, eh, data[offset + extra_off:offset + extra_off + ew * eh])
            recs.append(rec)
        return recs

    def diamond(self, rec, light=(1.0, 1.0, 1.0)):
        """A sub-tile's RGBA diamond, each channel scaled by `light`."""
        img = Image.new("RGBA", (self.block_w, self.block_h), (0, 0, 0, 0))
        put, i = img.load(), 0
        for row, (x0, width) in enumerate(diamond_rows(self.block_w, self.block_h)):
            for col in range(width):
                p = rec["pixels"][i]
                i += 1
                if p:
                    r, g, b = self.palette[p]
                    put[x0 + col, row] = (min(255, int(r * light[0])), min(255, int(g * light[1])),
                                          min(255, int(b * light[2])), 255)
        return img


class TsMap:
    """One TS map: its bounds, cells, overlays and objects."""

    def __init__(self, text):
        self.ini = parse_ini(text)
        info = self.ini["Map"]
        self.theatre = info["Theater"].upper()
        self.size = tuple(int(v) for v in info["Size"].split(","))
        self.local = tuple(int(v) for v in info["LocalSize"].split(","))
        self.name = self.ini.get("Basic", {}).get("Name", "")
        self.cells = {}
        data = unpack_blocks(self.ini["IsoMapPack5"], lzo1x.decompress)
        for i in range(0, len(data) - 10, 11):
            x, y, tile, sub, level, _ice = struct.unpack_from("<HHiBBB", data, i)
            if x or y:
                self.cells[x, y] = (tile, sub, level)

    def overlays(self):
        """{(x, y): (overlay index, overlay data)} of every cell with an overlay."""
        if "OverlayPack" not in self.ini:
            return {}
        kinds = unpack_blocks(self.ini["OverlayPack"], shptools.lcw_decompress)
        datas = unpack_blocks(self.ini["OverlayDataPack"], shptools.lcw_decompress)
        return {(i % 512, i // 512): (k, datas[i]) for i, k in enumerate(kinds) if k != 0xFF}

    def terrain(self):
        """{(x, y): terrain object type} (trees, lamps, rocks)."""
        return {split_cell(int(k)): v for k, v in self.ini.get("Terrain", {}).items()}

    def waypoints(self):
        """{waypoint number: (x, y)}."""
        return {int(k): split_cell(int(v)) for k, v in self.ini.get("Waypoints", {}).items()}

    def objects(self, section):
        """(owner, type, x, y) of each [Structures], [Units] or [Infantry] entry."""
        out = []
        for value in self.ini.get(section, {}).values():
            f = value.split(",")
            out.append((f[0], f[1], int(f[3]), int(f[4])))
        return out

    def light(self, level):
        """TS's ground lighting at a height level: (red, green, blue) multipliers from [Lighting]."""
        lit = self.ini.get("Lighting", {})
        base = float(lit.get("Ambient", 1.0)) + float(lit.get("Level", 0.0)) * level
        return tuple(base * float(lit.get(c, 1.0)) for c in ("Red", "Green", "Blue"))
