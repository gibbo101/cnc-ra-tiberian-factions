#!/usr/bin/env python3
"""Package the TS fire-stream particle sprite as the TSFIRE bullet tileset.

TS FLAMEALL.SHP = 4 direction sets (N/S, NE/SW, E/W, NW/SE) x 19 ageing states
(bright jet -> embers), 32x34 each. The DLL indexes shape = axis*19 + state
(BulletClass::Shape_Number, BULLET_TSFIRE). Decoded against ANIM.PAL with no
team remap, hq4x per the house policy, model-space centred on a 160 canvas
(20x20 classic stub x 8: 32 TS px = 2/3 of a TS cell = 2/3 of an RA cell).

Inputs: $TS_ART_DIR/raw/FLAMEALL.SHP + $TS_ART_DIR/raw/ANIM.PAL
Outputs: RED_ALERT/VFX/TSFIRE.ZIP + 76 TSFIRE tiles in RA_VFX.XML.
"""
import io, json, os, re, sys, zipfile
from PIL import Image
import hqx

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ts_shp
MOD = os.path.abspath(os.path.join(HERE, "..", "resources", "remaster_mods", "Vanilla_RA", "Data"))
VFX_DIR = f"{MOD}/ART/TEXTURES/SRGB/RED_ALERT/VFX"
XML = f"{MOD}/XML/TILESETS/RA_VFX.XML"
NAME = "TSFIRE"
CANVAS = 160


def tga_bytes(img):
    buf = io.BytesIO(); img.save(buf, format="TGA"); return buf.getvalue()


def write_zip(path, name, frames):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for i, img in enumerate(frames):
            W, H = img.size
            bb = img.getbbox() or (W // 2 - 1, H // 2 - 1, W // 2 + 1, H // 2 + 1)
            x0 = min(bb[0], W - bb[2]); y0 = min(bb[1], H - bb[3])
            b = (x0, y0, W - x0, H - y0)
            z.writestr(f"{name}-{i:04d}.tga", tga_bytes(img.crop(b)))
            z.writestr(f"{name}-{i:04d}.meta", json.dumps({"size": [W, H], "crop": list(b)}))
    print(f"wrote {path} ({len(frames)} frames)")


def patch_tileset(xml_path, name, count):
    sub = name.lower()
    xml = open(xml_path, encoding="utf-8").read()
    xml = re.sub(r"\t*<Tile>\s*<Key>\s*<Name>" + re.escape(name) + r"</Name>.*?</Tile>\n?", "", xml, flags=re.S)
    block = ('\t<Tile>\n\t\t<Key>\n\t\t\t<Name>%s</Name>\n\t\t\t<Shape>%d</Shape>\n\t\t</Key>\n'
             '\t\t<Value>\n\t\t\t<Frames>\n\t\t\t\t<Frame>%s</Frame>\n\t\t\t</Frames>\n\t\t</Value>\n\t</Tile>\n')
    blocks = "".join(block % (name, i, f"{sub}\\{sub}-{i:04d}.tga") for i in range(count))
    idx = xml.rindex("</Tiles>")
    open(xml_path, "w", encoding="utf-8").write(xml[:idx] + blocks + xml[idx:])
    print(f"patched RA_VFX.XML: {name} -> {count} tiles")


def main():
    pal = ts_shp.load_pal(f"{ART}/raw/ANIM.PAL")
    (W, H), raw = ts_shp.decode_shp(f"{ART}/raw/FLAMEALL.SHP")
    frames = []
    for f in raw:
        im = ts_shp.frame_to_rgba(f, pal, remap=None)
        # hqx wants RGB; carry alpha through a matching upscale of the mask
        big = hqx.hq4x(im.convert("RGB")).convert("RGBA")
        mask = im.split()[3].resize(big.size, Image.LANCZOS)
        big.putalpha(mask)
        out = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
        out.alpha_composite(big, (round(CANVAS / 2 - big.width / 2), round(CANVAS / 2 - big.height / 2)))
        frames.append(out)
    write_zip(f"{VFX_DIR}/{NAME}.ZIP", NAME.lower(), frames)
    patch_tileset(XML, NAME, len(frames))


if __name__ == "__main__":
    main()
