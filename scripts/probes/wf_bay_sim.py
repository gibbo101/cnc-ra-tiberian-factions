#!/usr/bin/env python3
"""How much of a unit waiting in a TS war factory's bay shows past the shut door, and how far back it must wait.

Composites the packed art as the game layers it: the factory body, the unit at its seat, the near face, the shut
door. A unit pixel the near face and door leave uncovered shows. Seats are leptons below the plot's north edge.
--switch: how deep, leaving with the door open, the unit's full art stops showing above the doorway (over the
roof); the antenna-less bay frames draw until then (UnitClass::TF_Hides_Antenna).

Usage: wf_bay_sim.py UNIT FRAMES SEAT [--mobile] [--search | --switch]   (FRAMES: 60 or 48-59 or 16,48;
       the Titan's legs and upper body together: 48-59+112)
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


def opaque(img):
    return np.asarray(img)[..., 3] > 128


def door_stages(factory):
    path = glob.glob(f"{REPO}/asset-packs/*/Data/ART/TEXTURES/SRGB/RED_ALERT/*/{factory}DR.ZIP")[0]
    return len([n for n in zipfile.ZipFile(path).namelist() if n.endswith(".tga")]) // 2


def unit_mask(unit, layers, seat, size):
    """The unit's drawn pixels on the factory canvas: layers are frames drawn over each other (legs, upper body)."""
    scale = CANVAS_PX / (frame(unit, layers[0]).width / stub_width(unit))
    mask = np.zeros((size[1], size[0]), bool)
    for i in layers:
        img = frame(unit, i)
        img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
        layer = Image.new("RGBA", size, (0, 0, 0, 0))
        cx, cy = PLOT_X + 384 * LEP_PX, PLOT_Y + seat * LEP_PX
        layer.paste(img, (round(cx - img.width / 2), round(cy - img.height / 2)), img)
        mask |= np.asarray(layer)[..., 3] > 96
    return mask


def visible(unit, frames, seat, factory):
    nf = frame(factory + "NF", 0)
    cover = opaque(nf) | opaque(frame(factory + "DR", 0))
    return max(int((unit_mask(unit, layers, seat, nf.size) & ~cover).sum()) for layers in frames)


def clear_of_roof(unit, frames, seat, factory):
    """The first depth past the seat at which, with the door open, no unit pixel shows above the doorway."""
    nf = frame(factory + "NF", 0)
    shut = opaque(frame(factory + "DR", 0))
    cover = opaque(nf) | opaque(frame(factory + "DR", door_stages(factory) - 1))
    roof = np.zeros_like(shut)
    roof[: np.nonzero(shut.any(axis=1))[0].min()] = True
    for depth in range(seat, seat + 400, 2):
        if all(not (unit_mask(unit, layers, depth, nf.size) & ~cover & roof).any() for layers in frames):
            return depth
    return None


def main(argv):
    unit, spec, seat = argv[0], argv[1], int(argv[2])
    factory = "TSDWEAP" if "--mobile" in argv else "TSWEAP"
    frames = []
    for part in spec.split(","):
        steps, _, over = part.partition("+")
        a, _, b = steps.partition("-")
        frames += [[i] + ([int(over)] if over else []) for i in range(int(a), int(b or a) + 1)]
    if "--switch" in argv:
        print(f"{unit} from {seat}: clear of the roof at {clear_of_roof(unit, frames, seat, factory)}")
        return
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
