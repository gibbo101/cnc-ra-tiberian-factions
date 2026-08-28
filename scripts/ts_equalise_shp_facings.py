#!/usr/bin/env python3
"""Level the per-facing brightness of a TS SHP walker's packed frames.

TS's pre-rendered walker sprites carry their light baked per facing, so a mech
facing away from TS's light reads a step darker than the same mech facing into
it (Wolverine SE vs S). Each facing block is scaled so its mean body luminance
matches the brightest block; shading inside a frame and the shadow layer are
untouched. Idempotent. Blocks: (first frame, frames per facing, facings).
usage: ts_equalise_shp_facings.py TSSMEC|TSTITN ...
License: GPL v3.
"""
import io, os, sys, zipfile
import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
UNITS = f"{ROOT}/resources/remaster_mods/Vanilla_RA/Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS"
LAYOUT = {
    "TSSMEC": [(0, 12, 8), (96, 4, 8)],          # walk, firing
    "TSTITN": [(0, 12, 8), (96, 1, 32)],         # walk, turret facings
}


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


def body_lum(a):
    m = a[..., 3] >= 250
    rgb = a[m][:, :3]
    return (0.2126 * rgb[:, 0] + 0.7152 * rgb[:, 1] + 0.0722 * rgb[:, 2]).mean() if m.any() else 0.0


def main():
    for name in sys.argv[1:]:
        path = f"{UNITS}/{name}.ZIP"
        z = zipfile.ZipFile(path)
        base = name.lower()
        frames = {}
        for n in z.namelist():
            if n.endswith(".tga"):
                frames[n] = np.array(Image.open(io.BytesIO(z.read(n))).convert("RGBA")).astype(np.float32)
        scale = {}
        for first, per, facings in LAYOUT[name]:
            means = []
            for f in range(facings):
                names = [f"{base}-{first + f * per + s:04d}.tga" for s in range(per)]
                means.append(np.mean([body_lum(frames[n]) for n in names]))
            target = max(means)
            for f in range(facings):
                for s in range(per):
                    scale[f"{base}-{first + f * per + s:04d}.tga"] = target / means[f]
            print(f"{name} block@{first}: facing means {[round(m, 1) for m in means]} -> {round(target, 1)}")
        out = io.BytesIO()
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as w:
            for n in z.namelist():
                if n not in scale:
                    w.writestr(n, z.read(n)); continue
                a = frames[n]
                body = a[..., 3] >= 250
                a[body, :3] = np.clip(a[body, :3] * scale[n], 0, 255)
                w.writestr(n, tga_bytes(Image.fromarray(a.astype(np.uint8), "RGBA")))
        open(path, "wb").write(out.getvalue())


if __name__ == "__main__":
    main()
