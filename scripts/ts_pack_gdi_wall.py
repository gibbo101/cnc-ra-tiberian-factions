#!/usr/bin/env python3
"""Pack the HD TS GDI concrete wall (resources/custom-art/ts-gdi-wall-hd) into TSWALL.ZIP.

The source frames are 128x128 with the frame exactly one cell, in BRIK's order and joins
(frame = N*1 + E*2 + S*4 + W*8 per damage stage). The wall takes TD's three wall damage
stages (healthy, damaged, heavily damaged: frames 0-47); the source's fourth, rubble stage
is not shipped. Each frame sits on the wall packers' 176x320 canvas with the cell's centre
on the canvas centre, the same anchoring the classic TSWALL stub declares.

The art's generator lives beside the frames (src/); regenerate there, then re-run this.
Usage: ts_pack_gdi_wall.py
License: GPL v3.
"""
import io, json, os, sys, zipfile
from PIL import Image

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS)
import ts_pack_walls as W

SRC = os.path.join(SCRIPTS, "..", "resources", "custom-art", "ts-gdi-wall-hd", "frames")
STAGES = 3
CELL = 128


def main():
    frames = []
    for i in range(16 * STAGES):
        art = Image.open(os.path.join(SRC, f"gdi-wall-{i:02d}.png")).convert("RGBA")
        if art.size != (CELL, CELL):
            raise SystemExit(f"gdi-wall-{i:02d}.png is {art.size}, expected one {CELL}x{CELL} cell")
        cv = Image.new("RGBA", (W.CANVAS_W, W.CANVAS_H), (0, 0, 0, 0))
        cv.paste(art, ((W.CANVAS_W - CELL) // 2, (W.CANVAS_H - CELL) // 2))
        frames.append(cv)
    out_zip = f"{W.STRUCT_DIR}/TSWALL.ZIP"
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for i, cv in enumerate(frames):
            bbox = cv.getbbox() or (0, 0, W.CANVAS_W, W.CANVAS_H)
            buf = io.BytesIO(); cv.crop(bbox).save(buf, format="TGA")
            z.writestr(f"tswall-{i:04d}.tga", buf.getvalue())
            z.writestr(f"tswall-{i:04d}.meta", json.dumps({"size": [W.CANVAS_W, W.CANVAS_H], "crop": list(bbox)}))
    print(f"wrote {out_zip} ({len(frames)} frames)")
    W.patch_tileset(W.TILESET, "TSWALL", len(frames))


if __name__ == "__main__":
    main()
