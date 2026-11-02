#!/usr/bin/env python3
"""Ship a staged mod's UI atlas as DXT5 DDS, and delete the DDS sprite frames an earlier build left, so each sprite
ships as its ZIP (docs/sprite-memory.md). Usage: sprite_dds.py <staged mod folder>...
"""
import hashlib
import os
import shutil
import struct
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dds_dxt5  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, "build", "sprite-dds-cache")
SPRITE_FOLDERS = ("UNITS", "STRUCTURES", "VFX")


def _alpha_blocks(alpha):
    """DXT5 alpha blocks (8 bytes each) for an HxW uint8 alpha level, edge-padded to a multiple of 4."""
    h, w = alpha.shape
    ph, pw = -(-h // 4) * 4, -(-w // 4) * 4
    a = np.pad(alpha, ((0, ph - h), (0, pw - w)), mode="edge").astype(float)
    blocks = a.reshape(ph // 4, 4, pw // 4, 4).transpose(0, 2, 1, 3).reshape(-1, 16)
    a0, a1 = blocks.max(1), blocks.min(1)
    weights = np.array([0, 7, 1, 2, 3, 4, 5, 6])  # palette slot -> share of a1, in sevenths
    pal = (a0[:, None] * (7 - weights) + a1[:, None] * weights) / 7
    idx = np.abs(blocks[:, :, None] - pal[:, None, :]).argmin(-1).astype(np.int64)
    idx[a0 == a1] = 0
    bits = (idx << (3 * np.arange(16))).sum(1)
    out = np.zeros((len(blocks), 8), np.uint8)
    out[:, 0] = a0.astype(np.uint8)
    out[:, 1] = a1.astype(np.uint8)
    for k in range(6):
        out[:, 2 + k] = (bits >> (8 * k)) & 0xFF
    return out


def _dxt5_level(img):
    """One DXT5 level of an RGBA image; clear pixels take the mean opaque colour so the fit spends its range on
    what shows."""
    rgba = np.asarray(img.convert("RGBA"))
    alpha = rgba[:, :, 3]
    rgb = rgba[:, :, :3].astype(float)
    rgb[alpha == 0] = rgb[alpha > 0].mean(0) if (alpha > 0).any() else 0
    blocks = np.frombuffer(dds_dxt5.encode_level(rgb.astype(np.uint8)), np.uint8).reshape(-1, 16).copy()
    blocks[:, :8] = _alpha_blocks(alpha)
    return blocks.tobytes()


def _header(w, h, mips, top_bytes):
    flags = 0x1 | 0x2 | 0x4 | 0x1000 | 0x20000 | 0x80000  # CAPS HEIGHT WIDTH PIXELFORMAT MIPMAPCOUNT LINEARSIZE
    pixel_format = struct.pack("<II4s5I", 32, 0x4, b"DXT5", 0, 0, 0, 0, 0)
    caps = 0x1000 | 0x8 | 0x400000  # TEXTURE COMPLEX MIPMAP
    return (b"DDS " + struct.pack("<7I", 124, flags, h, w, top_bytes, 0, mips) + b"\0" * 44 + pixel_format
            + struct.pack("<4I", caps, 0, 0, 0) + b"\0" * 4)


def _clear(folder):
    """Deletes a folder the converter wrote: each file, then the emptied folders, as scripts/clear_dir.sh does."""
    for d, _, files in os.walk(folder, topdown=False):
        for f in files:
            os.remove(os.path.join(d, f))
        os.rmdir(d)


def _key(zip_path):
    digest = hashlib.sha1(os.path.basename(zip_path).upper().encode())
    digest.update(open(zip_path, "rb").read())
    digest.update(open(__file__, "rb").read())
    return digest.hexdigest()


ATLAS = os.path.join("Data", "ART", "TEXTURES", "SRGB", "MT_COMMANDBAR_COMMON")


def _atlas_dds(tga_path):
    """The UI atlas as DXT5 DDS with every mip level, its sides padded to a multiple of 4, encoded in strips."""
    Image.MAX_IMAGE_PIXELS = None
    img = Image.open(tga_path).convert("RGBA")
    w, h = -(-img.width // 4) * 4, -(-img.height // 4) * 4
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.paste(img, (0, 0))
    levels, step = [], 0
    while True:
        size = (max(1, w >> step), max(1, h >> step))
        level = canvas if step == 0 else canvas.resize(size, Image.BOX)
        rows = range(0, level.height, 512) if level.height > 512 else [0]
        levels.append(b"".join(_dxt5_level(level.crop((0, y, level.width, min(level.height, y + 512)))) for y in rows))
        if size == (1, 1):
            break
        step += 1
    return _header(w, h, len(levels), len(levels[0])) + b"".join(levels)


def convert_atlas(mod_folder):
    """Replaces a staged mod's UI atlas TGA by its cached DXT5 DDS; the DLL reads the DDS's size for the crests."""
    tga = os.path.join(mod_folder, ATLAS + ".TGA")
    if not os.path.exists(tga):
        return
    cached = os.path.join(CACHE, _key(tga) + ".DDS")
    if not os.path.exists(cached):
        os.makedirs(CACHE, exist_ok=True)
        with open(cached + ".tmp", "wb") as fh:
            fh.write(_atlas_dds(tga))
        os.replace(cached + ".tmp", cached)
    os.utime(cached)
    shutil.copy2(cached, os.path.join(mod_folder, ATLAS + ".DDS"))
    os.remove(tga)


def drop_frames(mod_folder):
    """Deletes the DDS frame folders an earlier conversion left in a staged mod folder, so each sprite ships as its
    ZIP."""
    srgb = os.path.join(mod_folder, "Data", "ART", "TEXTURES", "SRGB")
    for game in sorted(os.listdir(srgb)) if os.path.isdir(srgb) else []:
        for sub in SPRITE_FOLDERS:
            d = os.path.join(srgb, game, sub)
            for name in sorted(os.listdir(d)) if os.path.isdir(d) else []:
                path = os.path.join(d, name)
                if os.path.isdir(path) and any(f.lower().endswith(".dds") for f in os.listdir(path)):
                    _clear(path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for folder in sys.argv[1:]:
        drop_frames(os.path.abspath(folder))
        convert_atlas(os.path.abspath(folder))
