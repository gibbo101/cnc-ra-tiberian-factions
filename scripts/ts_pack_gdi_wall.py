#!/usr/bin/env python3
"""Pack an HD TS wall into its tileset: the GDI concrete wall (resources/custom-art/ts-gdi-wall-hd)
into TSWALL.ZIP, or with --nod the Nod wall (resources/custom-art/ts-nod-wall-hd) into TSNWALL.ZIP.

The source frames are 128x128 with the frame exactly one cell, in BRIK's order and joins
(frame = N*1 + E*2 + S*4 + W*8 per damage stage). The wall takes TD's three wall damage
stages (healthy, damaged, heavily damaged: frames 0-47); the source's fourth, rubble stage
is not shipped. Each frame sits on the wall packers' 176x320 canvas with the cell's centre
on the canvas centre, the same anchoring the classic TSWALL stub declares.

The art's generator lives beside the frames (src/); regenerate there, then re-run this.
Usage: ts_pack_gdi_wall.py [--nod]
License: GPL v3.
"""
import io, json, os, sys, zipfile
from PIL import Image

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS)
import ts_pack_walls as W

ART = os.path.join(SCRIPTS, "..", "resources", "custom-art")
WALLS = {  # flag: (source dir, frame prefix, tileset)
    "gdi": ("ts-gdi-wall-hd", "gdi-wall", "TSWALL"),
    "nod": ("ts-nod-wall-hd", "nod-wall", "TSNWALL"),
}
STAGES = 3
CELL = 128
# The canvas is 192 wide, 96 px either side of the cell centre: its classic stub (36x60) has an
# even width, so the launcher's half-width offset lands on a whole pixel and the wall sits exactly
# on its cell. An odd stub (the old 176 / 33) drew every piece 2.7 px east of a gate's end.
CANVAS_W, CANVAS_H = 192, W.CANVAS_H


def main():
    folder, prefix, tileset = WALLS["nod" if "--nod" in sys.argv else "gdi"]
    frames = []
    for i in range(16 * STAGES):
        art = Image.open(os.path.join(ART, folder, "frames", f"{prefix}-{i:02d}.png")).convert("RGBA")
        if art.size != (CELL, CELL):
            raise SystemExit(f"{prefix}-{i:02d}.png is {art.size}, expected one {CELL}x{CELL} cell")
        cv = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        cv.paste(art, ((CANVAS_W - CELL) // 2, (CANVAS_H - CELL) // 2))
        frames.append(cv)
    low = tileset.lower()
    out_zip = f"{W.STRUCT_DIR}/{tileset}.ZIP"
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for i, cv in enumerate(frames):
            bbox = cv.getbbox() or (0, 0, CANVAS_W, CANVAS_H)
            buf = io.BytesIO(); cv.crop(bbox).save(buf, format="TGA")
            z.writestr(f"{low}-{i:04d}.tga", buf.getvalue())
            z.writestr(f"{low}-{i:04d}.meta", json.dumps({"size": [CANVAS_W, CANVAS_H], "crop": list(bbox)}))
    print(f"wrote {out_zip} ({len(frames)} frames)")
    W.patch_tileset(W.TILESET, tileset, len(frames))
    dims = json.load(open(W.STUB_MANIFEST))
    dims[tileset] = [CANVAS_W * 3 // 16, CANVAS_H * 3 // 16]
    json.dump(dims, open(W.STUB_MANIFEST, "w"), indent=1)
    open(W.STUB_MANIFEST, "a").write("\n")


if __name__ == "__main__":
    main()
