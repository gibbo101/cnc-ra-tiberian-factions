#!/usr/bin/env python3
"""Write redalert/tspuls_muzzle.h: the EMP Cannon's barrel tip per turret frame, as the lepton
offset from the building's centre that its pulse ball charges at and fires from.

The cannon is the TSPULST layer (32 frames, CCW from north), on the mound's canvas and its classic
stub (48 px wide), drawn with its canvas centre on the building's centre lowered by
TSPULS_TURRET_Y (building.cpp). Each head frame also carries the drum it turns on and its shadow
on the mound and the ground, so the head is first told apart from them: a pixel that is the
mound's own colour at that spot, lit or darkened, is the mound; a dark see-through pixel off the
mound is the ground shadow; of what is left, the largest connected piece is the head.

The muzzle turns on a level circle, which the camera draws as an ellipse. Where the barrel points
away from the camera or across it, its tip is the head's furthest pixels along the frame's screen
facing; the ellipse through those tips gives the muzzle at every facing, including the ones where
the barrel points at the camera and the yoke's feet reach lower on screen than its bore. The table
follows the art and is regenerated whenever the art is.

License: GPL v3.
"""
import io, json, math, os, zipfile
from collections import deque
from PIL import Image
import numpy as np

import asset_packs

HERE = os.path.dirname(os.path.abspath(__file__))
ZIP = asset_packs.art_zip("TSPULST", "STRUCTURES")
MOUND = asset_packs.art_zip("TSPULS", "STRUCTURES")
OUT = os.path.join(HERE, "..", "redalert", "tspuls_muzzle.h")
STUB = 48                 # classic px the canvas width maps onto
TURRET_Y = 10             # classic px: building.cpp TSPULS_TURRET_Y
PITCH = 0.6               # the fleet camera's north-south foreshortening
LEPTONS_PER_CLASSIC = 256 / 24
TIP_BAND = 6              # canvas px: the tip is every pixel this close to the furthest one, so
                          # twin barrels facing the camera put the muzzle between their ends
MOUND_MATCH = 0.12        # a pixel within this of the mound's colour, scaled, is the mound
GROUND_SHADOW_LUMA = 40   # a see-through pixel off the mound darker than this is the ground shadow


def canvas(z, name):
    """A frame on its full canvas, as RGBA floats."""
    meta = json.loads(z.read(name + ".meta"))
    W, H = meta["size"]
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(Image.open(io.BytesIO(z.read(name + ".tga"))).convert("RGBA"), tuple(meta["crop"][:2]))
    return np.asarray(out).astype(np.float32)


def largest_piece(mask):
    seen = np.zeros_like(mask)
    best = []
    H, W = mask.shape
    for y0, x0 in zip(*np.nonzero(mask)):
        if seen[y0, x0]:
            continue
        piece, todo = [], deque([(y0, x0)])
        seen[y0, x0] = True
        while todo:
            y, x = todo.popleft()
            piece.append((y, x))
            for yy in (y - 1, y, y + 1):
                for xx in (x - 1, x, x + 1):
                    if 0 <= yy < H and 0 <= xx < W and mask[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        todo.append((yy, xx))
        if len(piece) > len(best):
            best = piece
    out = np.zeros_like(mask)
    for y, x in best:
        out[y, x] = True
    return out


def head_mask(head, mound):
    on = head[..., 3] >= 128
    over = on & (mound[..., 3] > 0)
    m, h = mound[..., :3], head[..., :3]
    k = (h * m).sum(-1) / np.maximum((m * m).sum(-1), 1)
    off = np.linalg.norm(h - k[..., None] * m, axis=-1) / np.maximum(np.linalg.norm(m, axis=-1), 1)
    is_mound = over & (off < MOUND_MATCH) & (k < 1.05)
    luma = h @ np.array([0.299, 0.587, 0.114], np.float32)
    ground = on & (mound[..., 3] == 0) & (head[..., 3] < 250) & (luma < GROUND_SHADOW_LUMA)
    return largest_piece(on & ~is_mound & ~ground)


def main():
    z = zipfile.ZipFile(ZIP)
    names = sorted(n[:-4] for n in z.namelist() if n.endswith(".tga"))
    mz = zipfile.ZipFile(MOUND)
    mound = canvas(mz, sorted(n[:-4] for n in mz.namelist() if n.endswith(".tga"))[0])
    H, W = mound.shape[:2]
    k = STUB / W
    lift = round(TURRET_Y / k)
    # the mound where each head pixel lands in game: the head draws lift canvas px lower
    seen_mound = np.zeros_like(mound)
    seen_mound[:H - lift] = mound[lift:]

    fit = []
    for f, n in enumerate(names):
        theta = math.radians(f * 11.25)
        if math.cos(theta) < -1e-9:
            continue
        ys, xs = np.nonzero(head_mask(canvas(z, n), seen_mound))
        xs = xs - W / 2
        ys = ys - H / 2
        dx, dy = -math.sin(theta), -math.cos(theta) * PITCH
        proj = xs * dx + ys * dy
        tip = proj >= proj.max() - TIP_BAND
        fit.append((theta, xs[tip].mean(), ys[tip].mean()))
    th = np.array([t for t, _, _ in fit])
    (cx, rx), *_ = np.linalg.lstsq(np.c_[np.ones_like(th), -np.sin(th)], np.array([x for _, x, _ in fit]), rcond=None)
    (cy, ry), *_ = np.linalg.lstsq(np.c_[np.ones_like(th), -np.cos(th)], np.array([y for _, _, y in fit]), rcond=None)

    rows = []
    for f in range(len(names)):
        theta = math.radians(f * 11.25)
        x = (cx - rx * math.sin(theta)) * k
        y = (cy - ry * math.cos(theta)) * k + TURRET_Y
        rows.append((round(x * LEPTONS_PER_CLASSIC), round(y * LEPTONS_PER_CLASSIC)))
    hdr = "// GENERATED by scripts/ts_emp_muzzle.py -- do not hand-edit.\n"
    hdr += "// EMP Cannon barrel tip per TSPULST frame, leptons east/south of the building centre.\n"
    hdr += "static const short _tspuls_muzzle[32][2] = {" + ", ".join(f"{{{x}, {y}}}" for x, y in rows) + "};\n"
    open(OUT, "w").write(hdr)
    print(f"wrote {os.path.normpath(OUT)} (ellipse through {len(fit)} tips: centre {cx:.1f}, {cy:.1f}, "
          f"radii {rx:.1f} x {ry:.1f} canvas px)")
    for f in (0, 8, 16, 24):
        print(f"  frame {f:2}: {rows[f]}")


if __name__ == "__main__":
    main()
