#!/usr/bin/env python3
"""Pack turret facing renders (turret-NN.png) into a C&C turret tileset ZIP.

Unlike the body packer, the turret is NOT independently normalised: it is scaled
by the SAME factor the body was scaled by (so turret and hull share one in-game
scale), and each frame is centred on a fixed square canvas so the turret's
rotation axis (= render centre) sits at the canvas centre and all 32 facings
register. Output: <ininame>-NNNN.tga + .meta into <ININAME>.ZIP.

Usage:
  pack_turret_to_tileset.py <render_dir> <ININAME> <scale> <canvas_px> <out_zip> [nframes]
License: GPL v3.
"""
import sys, os, json, zipfile
from PIL import Image

render_dir, ininame, scale, canvas, out_zip = (
    sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
N = int(sys.argv[6]) if len(sys.argv) > 6 else 32

tmp = "/tmp/_packtur_out"
os.makedirs(tmp, exist_ok=True)
for f in os.listdir(tmp):
    os.remove(os.path.join(tmp, f))

low = ininame.lower()
for s in range(N):
    im = Image.open(f"{render_dir}/turret-{s:02d}.png").convert("RGBA")
    nw, nh = max(1, int(im.width * scale)), max(1, int(im.height * scale))
    im = im.resize((nw, nh), Image.LANCZOS)
    sq = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    sq.paste(im, ((canvas - nw) // 2, (canvas - nh) // 2), im)   # render centre -> canvas centre
    bbox = sq.getbbox() or (0, 0, canvas, canvas)
    crop = sq.crop(bbox)
    crop.save(f"{tmp}/{low}-{s:04d}.tga")
    meta = {"size": [canvas, canvas], "crop": [bbox[0], bbox[1], bbox[2], bbox[3]]}
    open(f"{tmp}/{low}-{s:04d}.meta", "w").write(json.dumps(meta))

with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
    for s in range(N):
        z.write(f"{tmp}/{low}-{s:04d}.tga", f"{low}-{s:04d}.tga")
        z.write(f"{tmp}/{low}-{s:04d}.meta", f"{low}-{s:04d}.meta")
print(f"wrote {out_zip}: {N} facings, scale {scale}, canvas {canvas}")
