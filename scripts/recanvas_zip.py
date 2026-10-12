#!/usr/bin/env python3
"""Move every frame of a tileset ZIP onto a canvas of another size, centred as before, for a layer whose
source art is gone. Each .meta takes the new canvas; a frame is trimmed only where it is fully transparent.
usage: recanvas_zip.py ZIP WIDTH HEIGHT
License: GPL v3.
"""
import io
import json
import os
import sys
import tempfile
import zipfile

from PIL import Image, ImageChops


def recanvas(path, width, height):
    with zipfile.ZipFile(path) as z:
        members = {info.filename: (info, z.read(info)) for info in z.infolist()}
    for name, (info, data) in list(members.items()):
        if not name.endswith(".meta"):
            continue
        meta = json.loads(data)
        if (meta["size"][0] - width) % 2 or (meta["size"][1] - height) % 2:
            raise SystemExit(f"{name}: cannot centre {meta['size']} on {width}x{height}")
        dx, dy = (meta["size"][0] - width) // 2, (meta["size"][1] - height) // 2
        x0, y0, x1, y1 = (v - d for v, d in zip(meta["crop"], (dx, dy, dx, dy)))
        nx0, ny0, nx1, ny1 = max(x0, 0), max(y0, 0), min(x1, width), min(y1, height)
        if (nx0, ny0, nx1, ny1) != (x0, y0, x1, y1):
            tga = name[:-5] + ".tga"
            img = Image.open(io.BytesIO(members[tga][1]))
            keep = (nx0 - x0, ny0 - y0, nx1 - x0, ny1 - y0)
            mask = Image.new("L", img.size, 255)
            mask.paste(0, keep)
            if ImageChops.multiply(img.getchannel("A"), mask).getbbox():
                raise SystemExit(f"{name}: art stands outside {width}x{height}")
            buf = io.BytesIO()
            img.crop(keep).save(buf, format="TGA")
            members[tga] = (members[tga][0], buf.getvalue())
        crop = [nx0, ny0, nx1, ny1]
        members[name] = (info, json.dumps({"size": [width, height], "crop": crop}).encode())
    out = list(members.values())
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path))
    os.close(fd)
    with zipfile.ZipFile(tmp, "w") as z:
        for info, data in out:
            z.writestr(info, data, zipfile.ZIP_DEFLATED)
    os.chmod(tmp, os.stat(path).st_mode)
    os.replace(tmp, path)
    print(f"{os.path.basename(path)}: {len(out) // 2} frames on {width}x{height}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    recanvas(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
