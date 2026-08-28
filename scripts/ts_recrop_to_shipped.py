#!/usr/bin/env python3
"""Re-cut re-rendered unit frames to the crop rects of a previously shipped zip.

For a relight (same renders, same pack, only colour changed) the shipped crop
rects are the geometry the launcher was signed off on: it anchors on the crop
centre and sizes the sprite by the crop, so a crop that grew -- a pole no
longer cut by the pack canvas, a shadow one pass taller -- moves the sprite
even when every body pixel is in the same place. This keeps the shipped rect
per frame, first sliding the new canvas onto the shipped one (alpha-mask cross
correlation, so a pack whose placement drifted from the shipped zip is undone), then
pastes the new pixels into it.
usage: ts_recrop_to_shipped.py <git-rev> <NAME> [NAME...]   (zips under UNITS/)
License: GPL v3.
"""
import io, json, os, subprocess, sys, zipfile
import numpy as np
from PIL import Image

MAX_SHIFT = 64  # pixels; a relight never legitimately moves content further


def best_shift(old_mask, new_mask):
    """Integer (dx, dy) that moves new_mask onto old_mask (max overlap, FFT)."""
    fa = np.fft.rfft2(old_mask.astype(np.float32))
    fb = np.fft.rfft2(new_mask.astype(np.float32))
    corr = np.fft.irfft2(fa * np.conj(fb), s=old_mask.shape)
    h, w = old_mask.shape
    dy, dx = np.unravel_index(np.argmax(corr), corr.shape)
    dy = dy - h if dy > h // 2 else dy
    dx = dx - w if dx > w // 2 else dx
    if abs(dx) > MAX_SHIFT or abs(dy) > MAX_SHIFT:
        return 0, 0
    return int(dx), int(dy)

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
        shifts = []
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
                oc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                oc.paste(Image.open(io.BytesIO(old.read(base + ".tga"))).convert("RGBA"), (om["crop"][0], om["crop"][1]))
                dx, dy = best_shift(np.array(oc)[..., 3] > 128, np.array(canvas)[..., 3] > 128)
                if dx or dy:
                    shifted = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    shifted.paste(canvas, (dx, dy))
                    canvas = shifted
                    shifts.append((base, dx, dy))
                if om["crop"] != nm["crop"]:
                    changed += 1
                z.writestr(base + ".tga", tga_bytes(canvas.crop(tuple(om["crop"]))))
                z.writestr(n, json.dumps(om))
        open(path, "wb").write(out.getvalue())
        big = [x for x in shifts if abs(x[1]) + abs(x[2]) > 2]
        print(f"{name}: {len(new.namelist())//2} frames re-cut to {rev} rects, {changed} rects differed, "
              f"{len(shifts)} frames slid ({len(big)} by >2 px; max {max([abs(x[1])+abs(x[2]) for x in shifts], default=0)})")


if __name__ == "__main__":
    main()
