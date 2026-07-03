#!/usr/bin/env python3
"""Post-process TD Gunboat hull facings (Blender renders) for the HD tileset.

Two passes over each facing-NN.png:
  1. Team-green brighten: the v2_green GLB's team zones are too dark for the
     launcher's house-colour remap (yellow came out olive). Green-ish pixels
     (g dominant) get a flat gain so the remap ramp matches the RA ships.
  2. Baked-shadow lift: the GLB texture has the source image's bridge shadow
     baked into the aft deck. Neutral-grey deck pixels in the shadow range get
     lifted toward deck brightness, CAPPED at the local deck level (an uncapped
     gain turns the penumbra into white halo lines around the cabin).

Usage: tdboat_hull_postprocess.py <in_dir> <out_dir> [green_gain]
License: GPL v3.
"""
import sys, os, colorsys
from PIL import Image

IN, OUT = sys.argv[1], sys.argv[2]
GREEN_GAIN = float(sys.argv[3]) if len(sys.argv) > 3 else 1.45
os.makedirs(OUT, exist_ok=True)

def shadow_lift(v):
    g = 1.0 + 1.1 * min(1.0, max(0.0, (v - 0.22) / 0.08))   # smooth onset
    cap = 0.64 + (v - 0.42) * 0.25                           # never brighter than deck
    return max(v, min(v * g, cap))

for s in range(16):
    im = Image.open(f"{IN}/facing-{s:02d}.png").convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a < 50:
                continue
            if g > 30 and g > r * 1.15 and g > b * 1.15:     # team green
                f = GREEN_GAIN
            else:
                h, sat, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                if sat < 0.17 and 0.22 < v < 0.71:            # baked deck shadow
                    nv = shadow_lift(v)
                    f = nv / v if nv > v else 1.0
                else:
                    continue
            if f > 1.0:
                px[x, y] = (min(255, int(r * f)), min(255, int(g * f)),
                            min(255, int(b * f)), a)
    im.save(f"{OUT}/facing-{s:02d}.png")
print("postprocessed 16 frames ->", OUT)
