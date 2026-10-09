#!/usr/bin/env python3
"""Compose BuildIcon_TS_MechDivision.png (three Titans, two Wolverines) from the Titan and Wolverine HD cameos.

Each unit is lifted off its cameo against the blank ground scene it was drawn on: its body as an opaque layer,
its shadow as a darkening of the floor. The units are scaled to their in-game sizes relative to each other
and grouped clear of the bottom-right corner, where scripts/ts_hd_cameos.py lays the Dropship Bay inset.

Usage: mech_division.py   (writes ../BuildIcon_TS_MechDivision.png; rerun scripts/ts_hd_cameos.py after)
License: GPL v3.
"""
import os
from collections import deque

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CAMEOS = os.path.dirname(HERE)
BG = os.path.join(HERE, "ts-cameo-background-hd.png")
FLOOR = 135  # the scene's dirt floor starts at this row; a shadow only falls on the floor
TITAN_SCALE = 0.6
WOLVERINE_SCALE = TITAN_SCALE * 0.575  # in game a Wolverine stands 0.59 and spans 0.47 of a Titan
TITANS = [(2, 150), (66, 156), (130, 162)]  # left edge, feet row
WOLVERINES = [(30, 192), (112, 192)]


def fill_holes(mask):
    """The mask with every region it encloses filled."""
    h, w = mask.shape
    outside = np.zeros_like(mask)
    q = deque((y, x) for y in range(h) for x in (0, w - 1) if not mask[y, x])
    q.extend((y, x) for x in range(w) for y in (0, h - 1) if not mask[y, x])
    for y, x in q:
        outside[y, x] = True
    while q:
        y, x = q.popleft()
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < h and 0 <= nx < w and not mask[ny, nx] and not outside[ny, nx]:
                outside[ny, nx] = True
                q.append((ny, nx))
    return ~outside


def lift(icon):
    """A unit's body (RGBA) and its shadow (a per-pixel darkening factor) from its cameo."""
    bg = np.asarray(Image.open(BG).convert("RGB")).astype(float)
    a = np.asarray(Image.open(os.path.join(CAMEOS, f"{icon}.png")).convert("RGB")).astype(float)
    changed = np.abs(a - bg).sum(2) > 6
    k = np.clip(a.sum(2) / np.maximum(bg.sum(2), 1), 0, 2)
    rows = np.arange(a.shape[0])[:, None]
    floor_shade = changed & (k < 0.97) & (np.abs(a - bg * k[..., None]).sum(2) < 18) & (rows >= FLOOR)
    body = fill_holes(changed & ~floor_shade) & changed
    rgba = np.zeros(a.shape[:2] + (4,), np.uint8)
    rgba[..., :3] = a.astype(np.uint8)
    rgba[..., 3] = body * 255
    return rgba, np.where(changed & ~body, k, 1.0)


def place(icon, scale, left, feet, shade, antenna=False):
    """The unit scaled and placed with its body's left edge and feet at (left, feet); its shadow goes into shade."""
    rgba, fac = lift(icon)
    ys, xs = np.nonzero(rgba[..., 3])
    w, h = round(rgba.shape[1] * scale), round(rgba.shape[0] * scale)
    body = Image.fromarray(rgba).convert("RGBa").resize((w, h), Image.LANCZOS).convert("RGBA")
    dark = np.asarray(Image.fromarray((fac * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)) / 255.0
    ox, oy = round(left - xs.min() * scale), round(feet - ys.max() * scale)
    y0, x0, y1, x1 = max(oy, 0), max(ox, 0), min(oy + h, 256), min(ox + w, 341)
    shade[y0:y1, x0:x1] *= dark[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
    layer = Image.new("RGBA", (341, 256))
    layer.alpha_composite(body, (x0, y0), (x0 - ox, y0 - oy))
    if antenna:
        a = np.array(layer)
        top = np.nonzero(a[..., 3].any(1))[0][0]
        cols = np.nonzero(a[top, :, 3])[0]
        a[:top, cols] = a[top, cols]
        layer = Image.fromarray(a)
    return layer


def main():
    bg = np.asarray(Image.open(BG).convert("RGB")).astype(float)
    shade = np.ones(bg.shape[:2])
    layers = [place("BuildIcon_TS_Titan", TITAN_SCALE, x, y, shade, antenna=True) for x, y in TITANS]
    layers += [place("BuildIcon_TS_Wolverine", WOLVERINE_SCALE, x, y, shade) for x, y in WOLVERINES]
    out = Image.fromarray((bg * shade[..., None]).clip(0, 255).astype(np.uint8)).convert("RGBA")
    for layer in layers:
        out.alpha_composite(layer)
    out.convert("RGB").save(os.path.join(CAMEOS, "BuildIcon_TS_MechDivision.png"))


if __name__ == "__main__":
    main()
