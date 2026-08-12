#!/usr/bin/env python3
"""Pack the TS Dropship (DSHP.VXL render) as the drop-pod bullet's sprite.

The delivery projectile wears TSDSHP instead of the falling nuke: a single
south-facing frame (the pod always flies due south onto the deck, and the
bullet is faceless with Frames=1, so shape 0 is the whole show). Follows the
TDMISSILE arrangement exactly: frame ZIP under VFX/, a Tile entry in
RA_VFX.XML, classic-side donor ImageData in bbdata One_Time.

Input: a vxl_render.py output frame, path passed as argv[1]
       (default: the session render of DSHP.VXL at --yaw0 270).

Idempotent: overwrites the ZIP, replaces its own XML block.

License: GPL v3.
"""
import io
import json
import sys
import zipfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
VFX_DIR = ROOT / "resources/remaster_mods/Vanilla_RA/Data/ART/TEXTURES/SRGB/RED_ALERT/VFX"
VFX_XML = ROOT / "resources/remaster_mods/Vanilla_RA/Data/XML/TILESETS/RA_VFX.XML"

BEGIN = "\t\t\t<!-- BEGIN generated TSDSHP drop-pod sprite (scripts/ts_pack_dropship.py) -->"
END = "\t\t\t<!-- END generated TSDSHP drop-pod sprite -->"

TILE = """\t\t\t<Tile>
\t\t\t\t<Key>
\t\t\t\t\t<Name>TSDSHP</Name>
\t\t\t\t\t<Shape>0</Shape>
\t\t\t\t</Key>
\t\t\t\t<Value>
\t\t\t\t\t<Frames>
\t\t\t\t\t\t<Frame>tsdshp\\tsdshp-0000.tga</Frame>
\t\t\t\t\t</Frames>
\t\t\t\t</Value>
\t\t\t</Tile>
"""


def tga_bytes(img):
    """Pillow TGA, the same writer ts_pack_tree.py ships frames with."""
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


def main():
    frame = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if frame is None:
        sys.exit("usage: ts_pack_dropship.py <rendered frame-0000.png>")
    img = Image.open(frame).convert("RGBA")
    bb = img.getbbox() or (0, 0, img.width, img.height)

    VFX_DIR.mkdir(parents=True, exist_ok=True)
    zpath = VFX_DIR / "TSDSHP.ZIP"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("tsdshp-0000.tga", tga_bytes(img.crop(bb)))
        z.writestr("tsdshp-0000.meta", json.dumps(
            {"size": [img.width, img.height], "crop": [bb[0], bb[1], bb[2], bb[3]]}))
    print(f"wrote {zpath}")

    text = VFX_XML.read_text()
    block = f"{BEGIN}\n{TILE}{END}\n"
    if BEGIN in text:
        head, rest = text.split(BEGIN, 1)
        _, tail = rest.split(END + "\n", 1)
        text = head + block + tail
    else:
        idx = text.rindex("</Tiles>")
        text = text[:idx] + block + text[idx:]
    VFX_XML.write_text(text)
    print(f"registered TSDSHP tile in {VFX_XML.name}")


if __name__ == "__main__":
    main()
