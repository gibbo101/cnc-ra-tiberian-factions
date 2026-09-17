#!/usr/bin/env python3
"""Pack Blender renders (scripts/ts_blender_walls.py) into the wall and tower ZIPs.

Each render is a square-pixel orthographic frame at 2x whose centre is the
cell centre at ground level. Packing = stretch vertically by 1/sin(32) so the
ground plane is 1:1 (the base game's HD wall cheat), downsample to the
176x320 canvas, crop + meta, and patch RA_STRUCTURES.XML. Canvas and stubs
(33x60) are the ones ts_pack_walls.py / build_tfassets.sh already declare.

  TSWALL       wall_j{joins:02d}_d{stage}.png   -> 48 frames (joins + 16 x stage)
  TSCTWR       tower_d0 / tower_d1              -> 2 frames
  TSCTWRMAKE   tower_make_00..16               -> 17 frames
  TSVULC/TSROCK/TSCSAM  {vulc|rpg|sam}_f{facing:02d}_s{state} -> 128 frames (state x 32 + facing)
  <ini>MAKE    same buildup as TSCTWRMAKE

Usage: ts_pack_blender.py <render_dir> [TSWALL|TSCTWR|TSVULC ...]
License: GPL v3.
"""
import io, json, math, os, sys, zipfile
from PIL import Image

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS)
import ts_pack_walls as W

CANVAS_W, CANVAS_H = W.CANVAS_W, W.CANVAS_H
STRETCH = 1.0 / math.sin(math.radians(32.0))


def load(render_dir, name):
    im = Image.open(f"{render_dir}/{name}.png").convert("RGBA")
    im = im.resize((im.width, int(round(im.height * STRETCH))), Image.LANCZOS)
    im = im.resize((CANVAS_W, CANVAS_H), Image.LANCZOS)
    # hard alpha keeps the silhouette crisp over snow (the tree's lesson)
    a = im.split()[3].point(lambda v: 255 if v >= 128 else 0)
    im.putalpha(a)
    return im


def write_zip(ini, frames):
    low = ini.lower()
    out_zip = f"{W.STRUCT_DIR}/{ini}.ZIP"
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for i, cv in enumerate(frames):
            bbox = cv.getbbox() or (0, 0, CANVAS_W, CANVAS_H)
            buf = io.BytesIO(); cv.crop(bbox).save(buf, format="TGA")
            z.writestr(f"{low}-{i:04d}.tga", buf.getvalue())
            z.writestr(f"{low}-{i:04d}.meta", json.dumps({"size": [CANVAS_W, CANVAS_H], "crop": list(bbox)}))
    print(f"wrote {out_zip} ({len(frames)} frames)")
    W.patch_tileset(W.TILESET, ini, len(frames))


def main():
    render_dir = sys.argv[1]
    which = set(sys.argv[2:]) or {"TSWALL", "TSCTWR", "TSVULC", "TSROCK", "TSCSAM"}
    dims = json.load(open(W.STUB_MANIFEST))
    if "TSWALL" in which:
        write_zip("TSWALL", [load(render_dir, f"wall_j{j:02d}_d{d}") for d in range(3) for j in range(16)])
        dims["TSWALL"] = [CANVAS_W * 3 // 16, CANVAS_H * 3 // 16]
    make = None
    if which & {"TSCTWR", "TSVULC", "TSROCK", "TSCSAM"}:
        make = [load(render_dir, f"tower_make_{k:02d}") for k in range(17)]
    if "TSCTWR" in which:
        write_zip("TSCTWR", [load(render_dir, "tower_d0"), load(render_dir, "tower_d1")])
        write_zip("TSCTWRMAKE", make)
        dims["TSCTWR"] = [CANVAS_W * 3 // 16, CANVAS_H * 3 // 16]
    for ini, kind in (("TSVULC", "vulc"), ("TSROCK", "rpg"), ("TSCSAM", "sam")):
        if ini in which:
            write_zip(ini, [load(render_dir, f"{kind}_f{f:02d}_s{s}") for s in range(4) for f in range(32)])
            write_zip(ini + "MAKE", make)
            dims[ini] = [CANVAS_W * 3 // 16, CANVAS_H * 3 // 16]
    json.dump(dims, open(W.STUB_MANIFEST, "w"), indent=1)


if __name__ == "__main__":
    main()
