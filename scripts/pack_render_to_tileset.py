#!/usr/bin/env python3
"""Pack Blender facing renders (facing-NN.png) into a C&C unit tileset ZIP.

Scales the renders so the east-facing (facing 04) hull length matches a target
pixel length (so it drops in at the same scale as the original sprite), centres
each on a square canvas (unit centre = canvas centre, so rotation/heading frames
all register), crops to content bbox, and writes <name>-NNNN.tga + .meta into
<ININAME>.ZIP — the same format our other unit art uses.

Reusable for the gunboat, hovercraft, etc.

Usage:
  pack_render_to_tileset.py <render_dir> <ININAME> <target_len_px> <canvas_px> <out_zip>
License: GPL v3.
"""
import sys, os, json, zipfile
from PIL import Image

render_dir, ininame, target_len, canvas, out_zip = (
    sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
N = 16

# scale so facing-04 (east, horizontal) content width == target_len
e = Image.open(f"{render_dir}/facing-04.png").convert("RGBA").getbbox()
scale = target_len / (e[2] - e[0])
print(f"east content width {e[2]-e[0]} -> target {target_len}  (scale {scale:.3f})")

tmp = "/tmp/_pack_out"
os.makedirs(tmp, exist_ok=True)
for f in os.listdir(tmp):
    os.remove(os.path.join(tmp, f))

low = ininame.lower()
for s in range(N):
    im = Image.open(f"{render_dir}/facing-{s:02d}.png").convert("RGBA")
    # scale whole frame about its centre (model was rendered centred at image centre)
    nw, nh = int(im.width * scale), int(im.height * scale)
    im = im.resize((nw, nh), Image.LANCZOS)
    sq = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    sq.paste(im, ((canvas - nw) // 2, (canvas - nh) // 2), im)
    bbox = sq.getbbox() or (0, 0, canvas, canvas)
    crop = sq.crop(bbox)
    crop.save(f"{tmp}/{low}-{s:04d}.tga")
    meta = {"size": [canvas, canvas], "crop": [bbox[0], bbox[1], bbox[2], bbox[3]]}
    open(f"{tmp}/{low}-{s:04d}.meta", "w").write(json.dumps(meta))

with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
    for s in range(N):
        z.write(f"{tmp}/{low}-{s:04d}.tga", f"{low}-{s:04d}.tga")
        z.write(f"{tmp}/{low}-{s:04d}.meta", f"{low}-{s:04d}.meta")
print(f"wrote {out_zip}: {N} facings, canvas {canvas}")
