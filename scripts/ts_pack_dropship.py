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
\t\t\t\t\t<Shape>{n}</Shape>
\t\t\t\t</Key>
\t\t\t\t<Value>
\t\t\t\t\t<Frames>
\t\t\t\t\t\t<Frame>tsdshp\\tsdshp-{n:04d}.tga</Frame>
\t\t\t\t\t</Frames>
\t\t\t\t</Value>
\t\t\t</Tile>
"""

# Shadow-scale frames: the shadow is the body sprite redrawn darkened, and the
# engine cannot scale at draw time -- so the growing shadow is pre-scaled art.
# Shape 0 = the ship (body, and the shadow when low); shapes 1..3 = the same
# art at descending-altitude scales, used by Draw_It's height buckets.
SHADOW_SCALES = [0.55, 0.70, 0.85]


def tga_bytes(img):
    """Pillow TGA, the same writer ts_pack_tree.py ships frames with."""
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


def main():
    frame = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if frame is None:
        sys.exit("usage: ts_pack_dropship.py <rendered frame png at final canvas>")
    img = Image.open(frame).convert("RGBA")

    frames = [img]
    for scale in SHADOW_SCALES:
        small = img.resize((max(1, int(img.width * scale)),
                            max(1, int(img.height * scale))), Image.LANCZOS)
        # Same canvas, centred: the draw call anchors by canvas, so the scaled
        # silhouette must sit where the full one does.
        pad = Image.new("RGBA", img.size, (0, 0, 0, 0))
        pad.alpha_composite(small, ((img.width - small.width) // 2,
                                    (img.height - small.height) // 2))
        frames.append(pad)

    VFX_DIR.mkdir(parents=True, exist_ok=True)
    zpath = VFX_DIR / "TSDSHP.ZIP"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for n, f in enumerate(frames):
            bb = f.getbbox() or (0, 0, f.width, f.height)
            z.writestr(f"tsdshp-{n:04d}.tga", tga_bytes(f.crop(bb)))
            z.writestr(f"tsdshp-{n:04d}.meta", json.dumps(
                {"size": [f.width, f.height], "crop": [bb[0], bb[1], bb[2], bb[3]]}))
    print(f"wrote {zpath} ({len(frames)} frames: body + {len(SHADOW_SCALES)} shadow scales)")

    text = VFX_XML.read_text()
    tiles = "".join(TILE.format(n=n) for n in range(len(frames)))
    block = f"{BEGIN}\n{tiles}{END}\n"
    if BEGIN in text:
        head, rest = text.split(BEGIN, 1)
        _, tail = rest.split(END + "\n", 1)
        text = head + block + tail
    else:
        idx = text.rindex("</Tiles>")
        text = text[:idx] + block + text[idx:]
    VFX_XML.write_text(text)
    print(f"registered {len(frames)} TSDSHP tiles in {VFX_XML.name}")


if __name__ == "__main__":
    main()
