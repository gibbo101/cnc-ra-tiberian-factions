#!/usr/bin/env python3
"""Compose BuildIcon_TS_MammothMk1Pair.png (two Mammoth Mk. Is) from the Mammoth Mk. I HD cameo, as
mech_division.py composes its group: grouped clear of the Dropship Bay inset's bottom-right corner.

Usage: mammoth_mk1_pair.py   (writes ../BuildIcon_TS_MammothMk1Pair.png; rerun scripts/ts_hd_cameos.py after)
License: GPL v3.
"""
import os

import numpy as np
from PIL import Image

from mech_division import BG, CAMEOS, place

SCALE = 0.5
TANKS = [(4, 152), (48, 192)]  # left edge, track bottom row: the back tank first


def main():
    bg = np.asarray(Image.open(BG).convert("RGB")).astype(float)
    shade = np.ones(bg.shape[:2])
    layers = [place("BuildIcon_TS_MammothMk1", SCALE, x, y, shade, antenna=True) for x, y in TANKS]
    out = Image.fromarray((bg * shade[..., None]).clip(0, 255).astype(np.uint8)).convert("RGBA")
    for layer in layers:
        out.alpha_composite(layer)
    out.convert("RGB").save(os.path.join(CAMEOS, "BuildIcon_TS_MammothMk1Pair.png"))


if __name__ == "__main__":
    main()
