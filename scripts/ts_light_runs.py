#!/usr/bin/env python3
"""Re-time an HD building's lamps that the art flashes together. Each lamp is an island of the overlay's pixels.
  steady: every lamp lit as in one delivered frame, all the time;
  line:   the lamps light one after another from west to east, each for a few frames, as in one delivered frame.

Writes <layer>-run/<name>-NN.png beside the delivered <layer>/: the healthy frames re-timed, the damaged frames
copied as they are. ts_pack_hd_buildings.py packs the run frames.

Usage: ts_light_runs.py [SRC ...]   (source folders under resources/custom-art/ts-buildings-hd; none = all)
License: GPL v3.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "resources", "custom-art", "ts-buildings-hd")

# src -> (layer path prefix, healthy frames, mode, the delivered frame a lit lamp shows, frames each lamp stays lit)
RUNS = {
    "tsdweap": [("C-lamps/mobile-war-factory-lamps", 8, "line", 2, 2),
                ("B-lights/mobile-war-factory-lights", 12, "steady", 0, 0)],
}


def islands(mask, reach=2):
    """Labels of mask's islands, pixels within reach of each other joining one island."""
    lab = np.zeros(mask.shape, int)
    count = 0
    h, w = mask.shape
    for y, x in zip(*np.nonzero(mask)):
        if lab[y, x]:
            continue
        count += 1
        lab[y, x] = count
        stack = [(y, x)]
        while stack:
            cy, cx = stack.pop()
            for yy in range(max(cy - reach, 0), min(cy + reach + 1, h)):
                for xx in range(max(cx - reach, 0), min(cx + reach + 1, w)):
                    if mask[yy, xx] and not lab[yy, xx]:
                        lab[yy, xx] = count
                        stack.append((yy, xx))
    return lab, count


def run(src, layer, n, mode, lit, hold):
    folder, name = os.path.split(layer)
    path = os.path.join(ROOT, src, folder)
    frames = [np.asarray(Image.open(os.path.join(path, f"{name}-{i:02d}.png")).convert("RGBA")) for i in range(2 * n)]
    lab, count = islands(np.any([f[..., 3] > 0 for f in frames[:n]], axis=0))
    order = sorted(range(1, count + 1), key=lambda k: np.nonzero(lab == k)[1].min())
    out = os.path.join(ROOT, src, f"{folder}-run")
    os.makedirs(out, exist_ok=True)
    for t in range(n):
        img = np.zeros_like(frames[0])
        for place, k in enumerate(order):
            if mode == "steady" or t // hold == place:
                m = lab == k
                img[m] = frames[lit][m]
        Image.fromarray(img, "RGBA").save(os.path.join(out, f"{name}-{t:02d}.png"))
    for t in range(n, 2 * n):
        Image.fromarray(frames[t], "RGBA").save(os.path.join(out, f"{name}-{t:02d}.png"))
    print(f"{src}/{folder}-run: {count} lamps, {mode}")


def main(argv):
    for src in (argv or list(RUNS)):
        for spec in RUNS[src]:
            run(src, *spec)


if __name__ == "__main__":
    main(sys.argv[1:])
