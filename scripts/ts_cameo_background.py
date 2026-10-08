#!/usr/bin/env python3
"""Rebuild one of TS's blank cameo scenes: ground (the rock wall, the dark band, the dirt floor TS's vehicles and
buildings stand on), infantry (a grey tiled floor) or aircraft (grey cloud). TS ships no empty one, so each pixel takes the colour enough donor cameos agree on, and a pixel the
objects cover in most donors mirrors its row's agreed dirt or rock on either side, keeping the grain.

Inputs: TS_ART_DIR holding CAMEO.PAL and the donor cameos (TIBSUN.MIX: CONQUER.MIX and CACHE.MIX).
Writes OUT_DIR/ts-cameo-background[-<scene>]-64x48.png (TS's own size) and -341x256.png (hq4x, as the mod's
cameos); the ground scene keeps the plain name.

Usage: TS_ART_DIR=... ts_cameo_background.py OUT_DIR [ground|infantry|aircraft]
License: GPL v3.
"""
import os
import sys
from collections import Counter

import hqx
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ts_shp

GROUND = ("APCICON", "ARTYICON", "BGGYICON", "CHAMICON", "E2ICON", "HMECICON", "JJETICON", "MEDIICON", "MMCHICON",
          "ORCAICON", "POWRICON", "RADRICON", "SAPCICON", "SMCHICON", "STNKICON", "SUBTICON", "TECHICON", "TICKICON",
          "UMAGICON", "WEAPICON", "WEEDICON")
# scene -> (donor cameos, donors that must share a pixel's colour for it to count as background; fewer let the
# objects' paint through). The heroes' cameos (GOSTICON, UMAGICON) have their own grid floor.
SCENES = {
    "ground": (GROUND, 8),
    "infantry": (("E2ICON", "E4ICON", "MEDIICON", "WEATICON", "JJETICON", "CYBCICON", "CHAMICON", "CYBIICON"), 5),
    "aircraft": (("OBMBICON", "PROICON", "APCHICON", "CRRYICON", "OTRNICON", "ORCAICON"), 4),
}


def main(out_dir, scene="ground"):
    art = os.environ.get("TS_ART_DIR")
    if not art:
        raise SystemExit("set TS_ART_DIR to the folder holding CAMEO.PAL and the donor cameos")
    pal = ts_shp.load_pal(f"{art}/CAMEO.PAL")
    names, agree = SCENES[scene]
    donors = []
    for name in names:
        _, frames = ts_shp.decode_shp(f"{art}/{name}.SHP")
        donors.append(ts_shp.frame_to_rgba(frames[0], pal, remap=None).convert("RGB"))
    w, h = donors[0].size
    px = [d.load() for d in donors]
    known = [[None] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            colour, votes = Counter(p[x, y] for p in px).most_common(1)[0]
            if votes >= agree:
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
    stem = "ts-cameo-background" + ("" if scene == "ground" else f"-{scene}")
    out.save(os.path.join(out_dir, f"{stem}-64x48.png"))
    big = hqx.hq4x(out).resize((341, 256), Image.LANCZOS)
    big.save(os.path.join(out_dir, f"{stem}-341x256.png"))
    print(f"wrote {out_dir}/{stem}-64x48.png and -341x256.png")


if __name__ == "__main__":
    main(*sys.argv[1:3])
