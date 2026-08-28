#!/usr/bin/env python3
"""Re-cut re-rendered unit frames to the crop rects of a previously shipped zip.

For a relight (same renders, same pack, only colour changed) the shipped crop
rects are the geometry the launcher was signed off on: it anchors on the crop
centre and sizes the sprite by the crop, so a crop that grew -- a pole no
longer cut by the pack canvas, a shadow one pass taller -- moves the sprite
even when every body pixel is in the same place. This keeps the shipped rect
per frame and pastes the new pixels into it.
usage: ts_recrop_to_shipped.py <git-rev> <NAME> [NAME...]   (zips under UNITS/)
License: GPL v3.
"""
import io, json, os, subprocess, sys, zipfile
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
UNITS = "resources/remaster_mods/Vanilla_RA/Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS"


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


def main():
    rev, names = sys.argv[1], sys.argv[2:]
    for name in names:
        path = f"{ROOT}/{UNITS}/{name}.ZIP"
        old = zipfile.ZipFile(io.BytesIO(subprocess.run(
            ["git", "-C", ROOT, "show", f"{rev}:{UNITS}/{name}.ZIP"], capture_output=True, check=True).stdout))
        new = zipfile.ZipFile(path)
        out = io.BytesIO()
        changed = 0
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for n in new.namelist():
                if not n.endswith(".meta"):
                    continue
                base = n[:-5]
                nm = json.loads(new.read(n))
                if n not in old.namelist():
                    z.writestr(n, new.read(n)); z.writestr(base + ".tga", new.read(base + ".tga"))
                    continue
                om = json.loads(old.read(n))
                assert om["size"] == nm["size"], (name, n, om["size"], nm["size"])
                W, H = nm["size"]
                canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                tile = Image.open(io.BytesIO(new.read(base + ".tga"))).convert("RGBA")
                canvas.paste(tile, (nm["crop"][0], nm["crop"][1]))
                if om["crop"] != nm["crop"]:
                    changed += 1
                z.writestr(base + ".tga", tga_bytes(canvas.crop(tuple(om["crop"]))))
                z.writestr(n, json.dumps(om))
        open(path, "wb").write(out.getvalue())
        print(f"{name}: {len(new.namelist())//2} frames re-cut to {rev} rects, {changed} rects differed")


if __name__ == "__main__":
    main()
