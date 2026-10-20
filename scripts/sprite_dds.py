#!/usr/bin/env python3
"""Ship each sprite ZIP as whole-canvas DXT5 frames or as tight-cropped TGAs, whichever takes less video memory
(docs/sprite-memory.md). Usage: sprite_dds.py <staged mod folder>...
"""
import hashlib
import io
import json
import multiprocessing
import os
import shutil
import struct
import sys
import time
import zipfile

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dds_dxt5  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, "build", "sprite-dds-cache")
SPRITE_FOLDERS = ("UNITS", "STRUCTURES", "VFX")
# A loose DDS sprite must save at least this share of the ZIP's memory to be worth its extra files.
MIN_SAVING = 0.10


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


def whole_canvas_dds(tga, meta):
    """A frame as DXT5 DDS with every mip level, on its whole canvas with the crop's margins clear."""
    canvas = Image.new("RGBA", tuple(meta["size"]), (0, 0, 0, 0))
    canvas.paste(Image.open(io.BytesIO(tga)).convert("RGBA"), tuple(meta["crop"][:2]))
    levels, step = [], 0
    while True:
        size = (max(1, canvas.width >> step), max(1, canvas.height >> step))
        levels.append(_dxt5_level(canvas if step == 0 else canvas.resize(size, Image.BOX)))
        if size == (1, 1):
            break
        step += 1
    return _header(canvas.width, canvas.height, len(levels), len(levels[0])) + b"".join(levels)


def _dds_bytes(w, h):
    """Video memory of a DXT5 texture with every mip level."""
    total = 0
    while True:
        total += (-(-w // 4)) * (-(-h // 4)) * 16
        if (w, h) == (1, 1):
            return total
        w, h = max(1, w // 2), max(1, h // 2)


def _frames(z):
    """(tga name, meta) for each frame of an open sprite ZIP."""
    names = set(z.namelist())
    out = []
    for name in sorted(names):
        if name.lower().endswith(".tga"):
            meta_name = name[:-4] + ".meta"
            meta = json.loads(z.read(meta_name)) if meta_name in names else None
            out.append((name, meta))
    return out


def tight(tga, meta):
    """A frame cropped to its visible pixels, as (TGA bytes, meta); unchanged when nothing is clear at the edges."""
    img = Image.open(io.BytesIO(tga))
    box = img.convert("RGBA").getchannel("A").getbbox()
    if box is None or box == (0, 0, img.width, img.height):
        return tga, meta
    out = io.BytesIO()
    img.crop(box).save(out, format="TGA", compression="tga_rle")
    x0, y0 = meta["crop"][:2]
    return out.getvalue(), dict(meta, crop=[x0 + box[0], y0 + box[1], x0 + box[2], y0 + box[3]])


def plan(zip_path):
    """("dds" or "zip", the ZIP's memory as TGA crops, as whole-canvas DDS) for a sprite ZIP."""
    with zipfile.ZipFile(zip_path) as z:
        frames = _frames(z)
    if not frames or any(meta is None for _, meta in frames):
        return "zip", 0, 0
    tga = sum((m["crop"][2] - m["crop"][0]) * (m["crop"][3] - m["crop"][1]) * 4 for _, m in frames)
    dds = sum(_dds_bytes(*m["size"]) for _, m in frames)
    return ("dds" if dds <= tga * (1 - MIN_SAVING) else "zip"), tga, dds


def _clear(folder):
    """Deletes a folder the converter wrote: each file, then the emptied folders, as scripts/clear_dir.sh does."""
    for d, _, files in os.walk(folder, topdown=False):
        for f in files:
            os.remove(os.path.join(d, f))
        os.rmdir(d)


def _build(zip_path, out_dir):
    """Writes the converted form of one ZIP into out_dir: a folder of DDS frames, or the tightened ZIP."""
    kind, _, _ = plan(zip_path)
    stem = os.path.splitext(os.path.basename(zip_path))[0]
    tmp = out_dir + ".tmp"
    if os.path.isdir(tmp):
        _clear(tmp)
    os.makedirs(tmp)
    with zipfile.ZipFile(zip_path) as z:
        if kind == "dds":
            os.makedirs(os.path.join(tmp, stem))
            for name, meta in _frames(z):
                with open(os.path.join(tmp, stem, name[:-4] + ".dds"), "wb") as fh:
                    fh.write(whole_canvas_dds(z.read(name), meta))
        else:
            with zipfile.ZipFile(os.path.join(tmp, stem + ".ZIP"), "w", zipfile.ZIP_DEFLATED) as zout:
                metas = dict(_frames(z))
                for name in z.namelist():
                    if name.lower().endswith(".meta") and name[:-5] + ".tga" in metas:
                        continue
                    data = z.read(name)
                    meta = metas.get(name)
                    if meta is not None:
                        data, meta = tight(data, meta)
                        zout.writestr(name[:-4] + ".meta", json.dumps(meta, separators=(",", ":")))
                    zout.writestr(name, data)
    os.replace(tmp, out_dir)


def _key(zip_path):
    digest = hashlib.sha1(open(zip_path, "rb").read())
    digest.update(open(__file__, "rb").read())
    return digest.hexdigest()


def _convert(zip_path):
    """Replaces one ZIP in place by its cached converted form; returns (path, kind, TGA bytes, DDS bytes, cache
    key)."""
    kind, tga, dds = plan(zip_path)
    out_dir = os.path.join(CACHE, _key(zip_path))
    if not os.path.isdir(out_dir):
        _build(zip_path, out_dir)
    folder = os.path.dirname(zip_path)
    stem = os.path.splitext(os.path.basename(zip_path))[0]
    os.remove(zip_path)
    for name in os.listdir(out_dir):
        src, dst = os.path.join(out_dir, name), os.path.join(folder, name)
        if os.path.isdir(src):
            if os.path.isdir(dst):
                _clear(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
    return os.path.join(folder, stem), kind, tga, dds, os.path.basename(out_dir)


def _note_used(keys):
    """Marks the cache entries a conversion used, and drops those no conversion has used for a week."""
    now = time.time()
    for key in keys:
        os.utime(os.path.join(CACHE, key), (now, now))
    for key in os.listdir(CACHE) if os.path.isdir(CACHE) else []:
        path = os.path.join(CACHE, key)
        if os.path.isdir(path) and now - os.stat(path).st_mtime > 7 * 86400:
            _clear(path)


def sprite_zips(mod_folder):
    """Every sprite ZIP under a staged mod folder's Data/ART."""
    srgb = os.path.join(mod_folder, "Data", "ART", "TEXTURES", "SRGB")
    out = []
    for game in sorted(os.listdir(srgb)) if os.path.isdir(srgb) else []:
        for sub in SPRITE_FOLDERS:
            d = os.path.join(srgb, game, sub)
            if os.path.isdir(d):
                out += [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.upper().endswith(".ZIP")]
    return out


def convert(mod_folder, quiet=False):
    """Converts every sprite ZIP of a staged mod folder; returns the per-ZIP results."""
    zips = sprite_zips(mod_folder)
    with multiprocessing.Pool(max(1, (os.cpu_count() or 2) - 2)) as pool:
        results = pool.map(_convert, zips, chunksize=1)
    _note_used([r[4] for r in results])
    if not quiet and results:
        loose = [r for r in results if r[1] == "dds"]
        before = sum(r[2] for r in results)
        after = sum(r[3] if r[1] == "dds" else r[2] for r in results)
        print(f"sprite_dds: {os.path.basename(os.path.normpath(mod_folder))}: {len(loose)} of {len(results)} "
              f"sprite ZIPs as DDS frames; sprite memory about {before / 2**20:.0f} -> {after / 2**20:.0f} MB "
              "before tight crops")
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for folder in sys.argv[1:]:
        convert(os.path.abspath(folder))
