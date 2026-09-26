#!/usr/bin/env python3
"""Replace frames of a packed HD tileset zip with higher-resolution redraws.

Each replacement PNG must be the whole frame canvas at an integer multiple of the shipped
canvas (a 384x256 building frame redrawn at 768x512), framed exactly as the original scaled
up: the launcher scales a frame's canvas onto the classic stub's box, so a larger canvas with
the same framing draws the same size with more detail and the stub stays as it is. Frames not
named keep their shipped art; all frames of one zip must end up the same size, so every
frame of the zip is replaced or none are upscaled.

Usage: scripts/ts_import_hires_frames.py ZIP INDEX=PNG [INDEX=PNG ...]
e.g.   scripts/ts_import_hires_frames.py .../STRUCTURES/TSDROP.ZIP 0=healthy.png 1=damaged.png

License: GPL v3.
"""
import io, json, os, sys, zipfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ts_reshadow import write_zip


def main(argv):
    path = argv[0]
    swaps = {int(k): v for k, v in (a.split("=", 1) for a in argv[1:])}
    z = zipfile.ZipFile(path)
    names = sorted(n[:-4] for n in z.namelist() if n.endswith(".tga"))
    stem = names[0].rsplit("-", 1)[0]
    frames = []
    for i, n in enumerate(names):
        meta = json.loads(z.read(n + ".meta"))
        W, H = meta["size"]
        if i in swaps:
            im = Image.open(swaps[i]).convert("RGBA")
            if im.width % W or im.height % H or im.width // W != im.height // H:
                raise SystemExit(f"frame {i}: {im.size} is not an integer multiple of {W}x{H}")
        else:
            src = Image.open(io.BytesIO(z.read(n + ".tga"))).convert("RGBA")
            im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            im.paste(src, (meta["crop"][0], meta["crop"][1]))
        frames.append(im)
    z.close()
    if len({f.size for f in frames}) != 1:
        raise SystemExit(f"frames differ in size {sorted({f.size for f in frames})}: replace every frame")
    write_zip(path, stem, frames)
    print(f"wrote {path}: {len(frames)} frames at {frames[0].size}")


if __name__ == "__main__":
    main(sys.argv[1:])
