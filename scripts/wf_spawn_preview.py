#!/usr/bin/env python3
"""Render an offline preview GIF of a vehicle spawning in the TS war factory
and driving out -- the no-game-reload iteration loop for the spawn point.

Reads the spawn point from the SPAWN layer of the Aseprite sheet (drag the
magenta crosshair, save, re-run this), composites the packed art with the
engine's sort model (base = plot north edge, unit = its own y, door overlay
= hangar south edge; pad is ground, always beneath sprites), and writes
~/Desktop/wf-art/spawn-preview.gif.

Usage: wf_spawn_preview.py [TSTITN|TSHARV]   (default TSTITN)
"""
import io, json, os, subprocess, sys, zipfile
from PIL import Image

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
RA = f"{REPO}/resources/remaster_mods/Vanilla_RA/Data/ART/TEXTURES/SRGB/RED_ALERT"
SHEET = os.path.expanduser("~/Desktop/wf-art/wf-pad-edit.aseprite")
OUT = os.path.expanduser("~/Desktop/wf-art/spawn-preview.gif")
ASEPRITE = os.path.expanduser("~/.steam/steam/steamapps/common/Aseprite/aseprite")

CANVAS = (896, 672)
PLOT = (192, 144, 704, 528)          # 4x3 plot on the canvas
BASE_KEY = PLOT[1]                   # bay interior: plot north edge
OVER_KEY = 336 + 64                  # hangar south edge (Sort_Y + 128 leptons)
TITAN_H = 278                        # 52.2 classic px on this canvas
# body/turret shape indices for the S facing (preview_to_desktop SPECS)
UNITS = {"TSTITN": ("TSTITN.ZIP", "tstitn", 4 * 12, 96 + 4 * 4, TITAN_H),
         "TSHARV": ("TSHARV.ZIP", "tsharv", 4 * 4, None, 170)}


def frame(zpath, pre, s):
    z = zipfile.ZipFile(zpath)
    meta = json.loads(z.read(f"{pre}-{s:04d}.meta"))
    tga = Image.open(io.BytesIO(z.read(f"{pre}-{s:04d}.tga"))).convert("RGBA")
    c = Image.new("RGBA", tuple(meta["size"]), (0, 0, 0, 0))
    c.paste(tga, (meta["crop"][0], meta["crop"][1]), tga)
    return c


def spawn_from_sheet():
    tmp = "/tmp/wf-spawn-marker.png"
    subprocess.run([ASEPRITE, "-b", SHEET, "--layer", "SPAWN -- MOVE ME",
                    "--save-as", tmp], check=True, capture_output=True)
    import numpy as np
    m = np.array(Image.open(tmp).convert("RGBA")).astype(int)
    mask = (m[..., 3] > 128) & (m[..., 0] > 200) & (m[..., 2] > 200) & (m[..., 1] < 100)
    ys, xs = np.nonzero(mask)
    return int(round(xs.mean())), int(round(ys.mean()))


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "TSTITN"
    uz, upre, body_s, tur_s, target_h = UNITS[which]

    sx, sy = spawn_from_sheet()
    print(f"spawn marker: canvas ({sx},{sy})  classic ({(sx-192)*3/16:.1f},{(sy-144)*3/16:.1f})")

    pad = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    bbz = f"{RA}/TERRAIN/TEMPERATE/TSWEAPBB.ZIP"
    for r in range(3):
        for c in range(4):
            t = frame(bbz, "tsweapbb", r * 4 + c)
            pad.paste(t, (192 + c * 128, 144 + r * 128), t)
    base = frame(f"{RA}/STRUCTURES/TSWEAP.ZIP", "tsweap", 0)
    door = [frame(f"{RA}/STRUCTURES/TSWEAP2.ZIP", "tsweap2", s) for s in range(9)]

    unit = frame(f"{RA}/UNITS/{uz}", upre, body_s)
    if tur_s is not None:
        unit.alpha_composite(frame(f"{RA}/UNITS/{uz}", upre, tur_s))
    bb = unit.getbbox()
    unit = unit.crop(bb)
    f = target_h / unit.height
    unit = unit.resize((max(1, round(unit.width * f)), target_h), Image.LANCZOS)

    # timeline: door opens, unit appears at the marker, drives straight out
    # the door and off the plot, door closes
    end_y = PLOT[3] + 110
    steps = 26
    frames = []

    def compose(door_stage, upos):
        bg = Image.new("RGBA", CANVAS, (225, 225, 232, 255))
        bg.alpha_composite(pad)
        layers = [(BASE_KEY, base), (OVER_KEY, door[door_stage])]
        if upos is not None:
            ux, uy = upos
            u = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
            u.paste(unit, (ux - unit.width // 2, uy - unit.height // 2), unit)
            layers.append((uy, u))
        for _, im in sorted(layers, key=lambda t: t[0]):
            bg.alpha_composite(im)
        return bg

    for s in range(9):                       # door opens
        frames.append(compose(s, None))
    for i in range(steps + 1):               # unit drives out
        y = round(sy + (end_y - sy) * i / steps)
        frames.append(compose(8, (sx, y)))
    for s in range(8, -1, -1):               # door closes
        frames.append(compose(s, (sx, end_y)))

    crop = (100, 60, 896, 672)
    frames = [f.crop(crop).convert("P", palette=Image.ADAPTIVE) for f in frames]
    frames[0].save(OUT, save_all=True, append_images=frames[1:],
                   duration=90, loop=0)
    print(f"wrote {OUT}")


main()
