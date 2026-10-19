"""Sidebar cameos as DXT1 DDS, the compressed format the launcher reads for a loose cameo.

usage: cameo_dds.py <BuildIcon .tga> [...]   writes <name>.DDS beside each, for a check by eye
`asset_packs.copy_newer` calls `write` when it stages a cameo; `is_atlas_name` keeps the cameos that
override the launcher's own atlas as TGA, since a loose DDS loses to the atlas (`cameo-dds.md`).
"""
import os
import struct
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dds_dxt5  # noqa: E402
import steam_library  # noqa: E402

SIZE = (344, 256)  # the 341x256 cameo on DXT's 4-pixel blocks; the sidebar quad stretches it
TEXTURES = str(steam_library.path("common/CnCRemastered/Data/TEXTURES_SRGB.MEG"))
_atlas_names = None


def is_atlas_name(name):
    """True when `name` (BuildIcon_X) is a region of the launcher's MT_COMMANDBAR_COMMON atlas."""
    global _atlas_names
    if _atlas_names is None:
        from meg_extract import read_member
        mtd = read_member(TEXTURES, "DATA\\ART\\TEXTURES\\SRGB\\MT_COMMANDBAR_COMMON.MTD").upper()
        _atlas_names = mtd
    return (name.upper() + ".TGA").encode() in _atlas_names


def _dxt1_level(rgb):
    """DXT1 blocks: the DXT5 encoder's colour half."""
    return np.frombuffer(dds_dxt5.encode_level(rgb), np.uint8).reshape(-1, 16)[:, 8:].tobytes()


def _header(w, h, mips, top_bytes):
    flags = 0x1 | 0x2 | 0x4 | 0x1000 | 0x20000 | 0x80000  # CAPS HEIGHT WIDTH PIXELFORMAT MIPMAPCOUNT LINEARSIZE
    pixel_format = struct.pack("<II4s5I", 32, 0x4, b"DXT1", 0, 0, 0, 0, 0)
    caps = 0x1000 | 0x8 | 0x400000  # TEXTURE COMPLEX MIPMAP
    return (b"DDS " + struct.pack("<7I", 124, flags, h, w, top_bytes, 0, mips) + b"\0" * 44 + pixel_format
            + struct.pack("<4I", caps, 0, 0, 0) + b"\0" * 4)


def write(src, dst):
    """Encodes the cameo `src` (any PIL-readable image) to the DDS `dst`, with every mip level down to 1x1."""
    cur = Image.open(src).convert("RGB").resize(SIZE, Image.LANCZOS)
    levels = []
    while True:
        levels.append(_dxt1_level(np.asarray(cur)))
        if cur.size == (1, 1):
            break
        cur = cur.resize((max(1, cur.width // 2), max(1, cur.height // 2)), Image.BOX)
    with open(dst, "wb") as f:
        f.write(_header(SIZE[0], SIZE[1], len(levels), len(levels[0])) + b"".join(levels))


if __name__ == "__main__":
    for tga in sys.argv[1:]:
        write(tga, os.path.splitext(tga)[0] + ".DDS")
        print(tga)
