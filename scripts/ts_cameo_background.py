#!/usr/bin/env python3
"""Rebuild TS's blank cameo scene (the rock wall, the dark band, the dirt floor every TS unit and building cameo
stands on). TS ships no empty one, so each pixel takes the colour enough donor cameos agree on, and a pixel the
objects cover in most donors mirrors its row's agreed dirt or rock on either side, keeping the grain.

Inputs: TS_ART_DIR holding CAMEO.PAL and the donor cameos (TIBSUN.MIX: CONQUER.MIX and CACHE.MIX).
Writes OUT_DIR/ts-cameo-background-64x48.png (TS's own size) and -341x256.png (hq4x, as the mod's cameos).

Usage: TS_ART_DIR=... ts_cameo_background.py OUT_DIR
License: GPL v3.
"""
import os
import sys
from collections import Counter

import hqx
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ts_shp

DONORS = ("APCICON", "ARTYICON", "BGGYICON", "CHAMICON", "E2ICON", "HMECICON", "JJETICON", "MEDIICON", "MMCHICON",
          "ORCAICON", "POWRICON", "RADRICON", "SAPCICON", "SMCHICON", "STNKICON", "SUBTICON", "TECHICON", "TICKICON",
          "UMAGICON", "WEAPICON", "WEEDICON")
AGREE = 8  # donors that must share a pixel's colour for it to count as background; fewer let unit paint through


def main(out_dir):
    art = os.environ.get("TS_ART_DIR")
    if not art:
        raise SystemExit("set TS_ART_DIR to the folder holding CAMEO.PAL and the donor cameos")
    pal = ts_shp.load_pal(f"{art}/CAMEO.PAL")
    donors = []
    for name in DONORS:
        _, frames = ts_shp.decode_shp(f"{art}/{name}.SHP")
        donors.append(ts_shp.frame_to_rgba(frames[0], pal, remap=None).convert("RGB"))
    w, h = donors[0].size
    px = [d.load() for d in donors]
    known = [[None] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            colour, votes = Counter(p[x, y] for p in px).most_common(1)[0]
            if votes >= AGREE:
                known[y][x] = colour
    out = Image.new("RGB", (w, h))
    for y in range(h):
        row = known[y]
        for x in range(w):
            if row[x] is not None:
                out.putpixel((x, y), row[x])
                continue
            a, b = x, x
            while a > 0 and row[a] is None:
                a -= 1
            while b < w - 1 and row[b] is None:
                b += 1
            src = (a - (x - a)) if (x - a <= b - x and row[a] is not None) else (b + (b - x))
            src = min(max(src, 0), w - 1)
            step = -1 if src <= x else 1
            while row[src] is None and 0 < src < w - 1:
                src += step
            out.putpixel((x, y), row[src] or (0, 0, 0))
    os.makedirs(out_dir, exist_ok=True)
    out.save(os.path.join(out_dir, "ts-cameo-background-64x48.png"))
    big = hqx.hq4x(out).resize((341, 256), Image.LANCZOS)
    big.save(os.path.join(out_dir, "ts-cameo-background-341x256.png"))
    print(f"wrote {out_dir}/ts-cameo-background-64x48.png and -341x256.png")


if __name__ == "__main__":
    main(sys.argv[1])
