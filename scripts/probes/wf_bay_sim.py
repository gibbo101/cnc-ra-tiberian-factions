#!/usr/bin/env python3
"""How much of a unit waiting in a TS war factory's bay shows past the shut door, and how far back it must wait.

Composites the packed art as the game layers it: the factory body, the unit at its seat, the near face, the shut
door. A unit pixel the near face and door leave uncovered shows. Seats are leptons below the plot's north edge.

Usage: wf_bay_sim.py UNIT FRAMES SEAT [--mobile] [--search]   (FRAMES: 60 or 48-59 or 16,48)
License: GPL v3.
"""
import glob
import io
import json
import os
import re
import sys
import zipfile

import numpy as np
from PIL import Image

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
CANVAS_PX = 480 / 90  # war factory canvas px per classic px
LEP_PX = 128 / 256  # war factory canvas px per lepton
PLOT_X, PLOT_Y = 240 - 192, 320 - 192  # the 3x3 plot's north-west corner on the canvas


def frame(name, i):
    path = glob.glob(f"{REPO}/asset-packs/*/Data/ART/TEXTURES/SRGB/RED_ALERT/*/{name}.ZIP")[0]
    z = zipfile.ZipFile(path)
    names = sorted(n for n in z.namelist() if n.endswith(".tga"))
    meta = json.loads(z.read(names[i].replace(".tga", ".meta")))
    img = Image.open(io.BytesIO(z.read(names[i]))).convert("RGBA")
    canvas = Image.new("RGBA", tuple(meta["size"]), (0, 0, 0, 0))
    canvas.paste(img, tuple(meta["crop"][:2]))
    return canvas


def stub_width(unit):
    text = open(f"{REPO}/scripts/build_tfassets.sh").read()
    m = re.search(rf'"\$TMPDIR/{unit.lower()}_stub\.shp" (\d+) (\d+)', text)
    return int(m.group(1))


def visible(unit, frames, seat, factory):
    nf, dr = frame(factory + "NF", 0), frame(factory + "DR", 0)
    cover = (np.asarray(nf)[..., 3] > 128) | (np.asarray(dr)[..., 3] > 128)
    scale = CANVAS_PX / (frame(unit, frames[0]).width / stub_width(unit))
    worst = 0
    for i in frames:
        img = frame(unit, i)
        img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
        layer = Image.new("RGBA", nf.size, (0, 0, 0, 0))
        cx, cy = PLOT_X + 384 * LEP_PX, PLOT_Y + seat * LEP_PX
        layer.paste(img, (round(cx - img.width / 2), round(cy - img.height / 2)), img)
        worst = max(worst, int(((np.asarray(layer)[..., 3] > 96) & ~cover).sum()))
    return worst


def main(argv):
    unit, spec, seat = argv[0], argv[1], int(argv[2])
    factory = "TSDWEAP" if "--mobile" in argv else "TSWEAP"
    frames = []
    for part in spec.split(","):
        a, _, b = part.partition("-")
        frames += list(range(int(a), int(b or a) + 1))
    if "--search" not in argv:
        print(f"{unit} at {seat}: {visible(unit, frames, seat, factory)} px show")
        return
    for pull in range(0, 200, 8):
        shown = visible(unit, frames, seat - pull, factory)
        print(f"{unit} {pull} leptons back: {shown} px show")
        if shown <= 12:
            break


if __name__ == "__main__":
    main(sys.argv[1:])
