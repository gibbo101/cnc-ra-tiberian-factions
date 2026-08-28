#!/usr/bin/env python3
"""Pack the TS MCV (MCV.VXL render) into TSMCV.ZIP on its own.

The tree script's TSMCV block only runs when the zip is absent and only as part
of a full tree rebuild; this is that block alone, for re-renders. Render per the
ledger (docs/launcher-render-contracts.md): vxl_render.py MCV.VXL <dir>
--frames 32 --px-per-voxel 12 --yaw0 90 --elev 32 (frame 0 = N, no reorder).
Side frame 8's width is scaled to 280 px on a 384 canvas (classic 48 x 8).
Follow with scripts/ts_reshadow.py TSMCV. License: GPL v3.
usage: ts_pack_tsmcv.py <renders dir>
"""
import io, json, os, sys, zipfile
from PIL import Image

MOD = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                   "resources", "remaster_mods", "Vanilla_RA"))
UNITS_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS"


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


def write_zip(path, name, frames):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for i, img in enumerate(frames):
            base = f"{name}-{i:04d}"
            b = img.getbbox() or (0, 0, img.width, img.height)
            z.writestr(base + ".tga", tga_bytes(img.crop(b)))
            z.writestr(base + ".meta", json.dumps(
                {"size": [img.width, img.height], "crop": [b[0], b[1], b[2], b[3]]}))
    print(f"wrote {path} ({len(frames)} frames)")


def scale_center(img, factor, canvas):
    nw, nh = round(img.width * factor), round(img.height * factor)
    scaled = img.resize((nw, nh), Image.LANCZOS)
    out = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    out.paste(scaled, ((canvas - nw) // 2, (canvas - nh) // 2), scaled)
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    renders = sys.argv[1]
    side = Image.open(f"{renders}/frame-0008.png")
    b = side.getbbox()
    factor = 280.0 / (b[2] - b[0])
    frames = [scale_center(Image.open(f"{renders}/frame-{i:04d}.png"), factor, 384)
              for i in range(32)]
    write_zip(f"{UNITS_DIR}/TSMCV.ZIP", "tsmcv", frames)
