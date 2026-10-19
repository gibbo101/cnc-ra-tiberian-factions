#!/usr/bin/env python3
"""A square autotile sample for the TS Temperate theatre (docs/ts-theatres.md): seamless HD ground made
from TS's own tiles, corner-blended transitions, cliff pieces rendered from a heightfield, and a map
region of a converted TS map built only from those pieces.

Usage: ts_autotile_sample.py [--map NAME] [--at U,V] [--size W,H] [--out DIR]
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import ts_map  # noqa: E402
import ts_map_to_ra as conv  # noqa: E402
import ts_ground_sample  # noqa: E402

HD = 128
# One TS height level in RA cell widths: 104 of TS's 256 leptons, a TS cell being 1/sqrt(2) RA cells.
LEVEL_CELLS = 104 / 256 / math.sqrt(2)
LIGHT = np.array([-0.55, -0.55, 0.63])  # from the north-west, as TS lights its tiles
LIGHT = LIGHT / np.linalg.norm(LIGHT)

# Ground classes drawn in layers over clear ground: (class letter, TS tileset name, tile in set).
GROUND = [(".", "Clear", 0), ("r", "Rough LAT tile", 0), ("s", "Sand", 0), ("g", "Green", 0),
          ("=", "Pavement (Use for LAT)", 0), ("~", "Water", 0)]
LAYER_ORDER = ["s", "g", "r", "=", "~"]


def art_class(set_name, land):
    """The ground a TS tile is painted as: its tile family, since sand and green share rough's land type."""
    name = set_name.lower()
    if land == "water":
        return "~"
    if "sand" in name or land == "beach":
        return "s"
    if "green" in name:
        return "g"
    if "rough" in name:
        return "r"
    if "pave" in name or land == "road":
        return "="
    return "."


def tile_index(tileset, set_name, n):
    """The tile index of the n-th tile of a named TS tileset."""
    first = next(i for i, (name, _f) in enumerate(tileset.tiles) if name == set_name)
    return first + n


def seamless_texture(tileset, tile, light, flip=0):
    """An HD texture one RA cell square that tiles seamlessly: a TS tile repeated on its lattice,
    flattened to top-down and cut on lattice points; `flip` (0-3) mirrors the cell's middle diamond."""
    diamond = tileset.diamond(tileset.record(tile, 0), light)
    middle = diamond
    if flip & 1:
        middle = middle.transpose(Image.FLIP_LEFT_RIGHT)
    if flip & 2:
        rows = middle.crop((0, 0, middle.width, middle.height - 1)).transpose(Image.FLIP_TOP_BOTTOM)
        middle = Image.new("RGBA", middle.size, (0, 0, 0, 0))
        middle.paste(rows, (0, 0))
    lattice = Image.new("RGBA", (48 * 4, 24 * 4), (0, 0, 0, 255))
    for dy in range(-2, 10):
        for dx in range(-2, 10):
            if (dx + dy) % 2 == 0:
                img = middle if dx % 2 else diamond
                lattice.paste(img, (dx * 24 - 24, dy * 12 - 12), img)
    top_down = lattice.resize((48 * 4, 48 * 4), Image.NEAREST).crop((48, 48, 96, 96))
    wrapped = Image.new("RGBA", (48 * 3, 48 * 3))
    for i in range(3):
        for j in range(3):
            wrapped.paste(top_down, (48 * i, 48 * j))
    big = wrapped.resize((HD * 3, HD * 3), Image.LANCZOS).crop((HD, HD, HD * 2, HD * 2))
    return np.asarray(big.convert("RGB"), dtype=np.float32) / 255.0


def rock_texture(tileset):
    """An HD rock texture tiled from the most solid patch of TS's first cliff pieces, faces included."""
    canvas = Image.new("RGBA", (480, 480), (0, 0, 0, 0))
    for n in range(4):
        for rec in tileset.records(tile_index(tileset, "Cliff Set", n)):
            if not rec:
                continue
            ox, oy = 120 * n + 40, 200
            canvas.paste(tileset.diamond(rec), (ox + rec["x"], oy + rec["y"]), tileset.diamond(rec))
            if rec["extra"]:
                ex, ey, ew, eh, data = rec["extra"]
                face = Image.new("RGBA", (ew, eh), (0, 0, 0, 0))
                put = face.load()
                for i, p in enumerate(data):
                    if p:
                        put[i % ew, i // ew] = tileset.palette[p] + (255,)
                canvas.paste(face, (ox + ex, oy + ey), face)
    pix = np.asarray(canvas, dtype=np.float32)
    alpha = pix[..., 3] > 0
    size = 32
    integral = np.pad(alpha.cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    counts = integral[size:, size:] - integral[:-size, size:] - integral[size:, :-size] + integral[:-size, :-size]
    y0, x0 = np.unravel_index(np.argmax(counts), counts.shape)
    patch = pix[y0:y0 + size, x0:x0 + size, :3]
    shifted = np.roll(np.roll(patch, size // 2, 0), size // 2, 1)
    ramp = 1 - np.abs(np.linspace(-1, 1, size))
    weight = np.minimum.outer(ramp, ramp)[..., None]
    seamless = patch * weight + shifted * (1 - weight)
    img = Image.fromarray(seamless.astype(np.uint8)).resize((HD, HD), Image.LANCZOS)
    return np.asarray(img, dtype=np.float32) / 255.0


_GRID = np.mgrid[0:HD, 0:HD].astype(np.float32) / HD  # [0] = y, [1] = x, both 0..1 across the cell
_Y, _X = _GRID


def periodic_noise(seed):
    """Smooth noise with a period of one cell, so a tile's edges meet any other tile's."""
    rng = np.random.default_rng(seed)
    n = np.zeros((HD, HD), np.float32)
    for f in (1, 2, 3, 5):
        for _ in range(3):
            a, b, ph = rng.integers(-f, f + 1), rng.integers(-f, f + 1), rng.uniform(0, 2 * math.pi)
            n += np.sin(2 * math.pi * (a * _X + b * _Y) + ph) / f
    return n / np.abs(n).max()


NOISE = periodic_noise(7)


def corner_field(c00, c10, c01, c11):
    """The bilinear field of four corner values across the cell (c<x><y>, y down)."""
    return (c00 * (1 - _X) * (1 - _Y) + c10 * _X * (1 - _Y) + c01 * (1 - _X) * _Y + c11 * _X * _Y)


def corner_mask(corners, width=0.10, wobble=0.22):
    """Where a class covers the cell, from which corners hold it: 0..1, matching along every edge."""
    f = corner_field(*corners) + wobble * NOISE
    t = np.clip((f - 0.5) / width + 0.5, 0, 1)
    return t * t * (3 - 2 * t)


def piece(classes, heights, ramps, textures, rock, variant=0):
    """One RA cell's HD art from its corners' ground classes, heights (levels) and ramp flags
    (each listed top-left, top-right, bottom-left, bottom-right)."""
    colour = textures["."][variant % len(textures["."])].copy()
    for k in LAYER_ORDER:
        corners = [1.0 if c == k else 0.0 for c in classes]
        if any(corners):
            m = corner_mask(corners)[..., None]
            colour = colour * (1 - m) + textures[k] * m
    lo, hi = min(heights), max(heights)
    height = np.full((HD, HD), float(lo), np.float32)
    gentle = corner_field(*[1.0 if r else 0.0 for r in ramps])
    for level in range(lo + 1, hi + 1):
        corners = [1.0 if h >= level else 0.0 for h in heights]
        width = 0.40 + 0.30 * gentle
        f = corner_field(*corners) + 0.08 * NOISE
        t = np.clip((f - 0.5) / width + 0.5, 0, 1)
        height += t * t * (3 - 2 * t)
    z = height * LEVEL_CELLS
    gy, gx = np.gradient(z, 1.0 / HD)
    normal = np.stack([-gx, -gy, np.ones_like(z)], -1)
    normal /= np.linalg.norm(normal, axis=-1, keepdims=True)
    slope = 1 - normal[..., 2]
    rocky = np.clip((slope - 0.12) / 0.15, 0, 1)[..., None] * (1 - gentle[..., None])
    colour = colour * (1 - rocky) + rock * rocky
    shade = 0.55 + 0.6 * np.clip(normal @ LIGHT, 0, 1)
    lit = 0.85 + 0.05 * height
    return np.clip(colour * (shade * lit)[..., None], 0, 1)


def to_image(arr):
    """An RGB image of a float array."""
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))


def region_corners(tsmap, tileset, layout, u, v):
    """The four corner TS cells of RA cell (u, v): class, height and ramp each, in piece order."""
    out = []
    for a, b in ((0, 0), (1, 0), (0, 1), (1, 1)):
        cell = layout.corner(u + a, v + b)
        entry = tsmap.cells.get(cell, (0, 0, 0))
        rec = tileset.record(entry[0], entry[1])
        k = art_class(tileset.tiles[tileset.fixup(entry[0])][0], rec["land"])
        out.append((k, entry[2], rec["ramp"]))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--map", default="Tiers of Sorrow")
    parser.add_argument("--at", default="8,29")
    parser.add_argument("--size", default="14,10")
    parser.add_argument("--out", default=os.path.expanduser("~/Desktop/Tiberian Factions/ts-theatres/autotile-sample"))
    args = parser.parse_args()
    u0, v0 = (int(v) for v in args.at.split(","))
    w, h = (int(v) for v in args.size.split(","))
    os.makedirs(args.out, exist_ok=True)
    install = ts_map.TsInstall()
    maps = install.maps()
    tsmap = ts_map.TsMap(maps[args.map])
    tileset = ts_map.Tileset(install, tsmap.theatre)
    light = tsmap.light(2)
    textures = {k: seamless_texture(tileset, tile_index(tileset, s, n), light) for k, s, n in GROUND}
    clear = tile_index(tileset, "Clear", 0)
    textures["."] = [seamless_texture(tileset, clear, light, i) for i in range(4)]
    rock = rock_texture(tileset)

    # Sheet 1: the textures, the 16 clear/rough transitions, the 16 one-level cliff pieces.
    gap = 8
    sheet = Image.new("RGB", (16 * (HD + gap), 3 * (HD + gap) + 60), (30, 30, 30))
    d = ImageDraw.Draw(sheet)
    names = {".": "clear", "r": "rough", "s": "sand/beach", "g": "green", "=": "pavement", "~": "water"}
    for i, (k, _s, _n) in enumerate(GROUND):
        tex = textures[k][1] if k == "." else textures[k]
        sheet.paste(to_image(tex), (i * (HD + gap), 20))
        d.text((i * (HD + gap), 4), names[k], fill=(255, 255, 255))
    sheet.paste(to_image(rock), (len(GROUND) * (HD + gap), 20))
    d.text((len(GROUND) * (HD + gap), 4), "rock (cliff face)", fill=(255, 255, 255))
    for m in range(16):
        bits = [(m >> i) & 1 for i in range(4)]
        tr = piece([("r" if b else ".") for b in bits], [2] * 4, [0] * 4, textures, rock)
        cl = piece(["."] * 4, [2 + 4 * b for b in bits], [0] * 4, textures, rock)
        sheet.paste(to_image(tr), (m * (HD + gap), 40 + HD + gap))
        sheet.paste(to_image(cl), (m * (HD + gap), 60 + 2 * (HD + gap)))
    d.text((0, 26 + HD + gap), "clear/rough transitions (corner sets)", fill=(255, 255, 255))
    d.text((0, 46 + 2 * (HD + gap)), "cliff pieces, 4 levels (corner sets)", fill=(255, 255, 255))
    sheet.save(os.path.join(args.out, "pieces.png"))

    # Sheet 2: a converted map region built from pieces, beside TS's own view of it.
    layout = conv.Layout(tsmap)
    region = Image.new("RGB", (w * HD, h * HD))
    cache = {}
    for v in range(v0, v0 + h):
        for u in range(u0, u0 + w):
            corners = region_corners(tsmap, tileset, layout, u, v)
            variant = (u * 7 + v * 13 + (u * v) % 3) % 4
            key = (tuple(corners), variant)
            if key not in cache:
                cache[key] = to_image(piece([c[0] for c in corners], [c[1] for c in corners],
                                            [c[2] for c in corners], textures, rock, variant))
            region.paste(cache[key], ((u - u0) * HD, (v - v0) * HD))
    slug = conv.slug(args.map)
    region.save(os.path.join(args.out, f"{slug}_region_ra.png"))
    ts_view = ts_ground_sample.draw_ground(tsmap, tileset, layout, u0, v0, w, h, lifted=True)
    ts_view = ts_view.resize((ts_view.width * HD // 48, ts_view.height * HD // 48), Image.NEAREST)
    ts_view.convert("RGB").save(os.path.join(args.out, f"{slug}_region_ts.png"))
    flat = ts_ground_sample.flat_hd(tsmap, tileset, layout, u0, v0, w, h).convert("RGB")
    panels = [("TS as TS draws it (lifted, same area give or take the lift)", ts_view.convert("RGB")),
              ("TS's own tiles flattened onto these RA cells", flat),
              ("square autotile pieces (this sample)", region)]
    scale = 0.5
    width = int(w * HD * scale)
    sheet = Image.new("RGB", (3 * width + 40, int(max(p[1].height for p in panels) * scale) + 30), (30, 30, 30))
    d = ImageDraw.Draw(sheet)
    for i, (title, img) in enumerate(panels):
        small = img.resize((width, int(img.height * scale)), Image.LANCZOS)
        sheet.paste(small, (i * (width + 20), 24))
        d.text((i * (width + 20), 6), title, fill=(255, 255, 255))
    sheet.save(os.path.join(args.out, f"{slug}_compare.png"))
    print(f"wrote {args.out}: region of {w}x{h} cells uses {len(cache)} distinct pieces")


if __name__ == "__main__":
    main()
