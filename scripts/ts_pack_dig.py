#!/usr/bin/env python3
"""Package the TS subterranean DIG mound anim (TSDIG.ZIP, ANIM_TS_DIG).

TS [AudioVisual] Dig=DIG: the 37-frame earth burst a tunneling vehicle throws
up when it digs in and when it surfaces. Decoded from DIG.SHP against ANIM.PAL
with NO team remap (ANIM.PAL 16-31 are real dirt tones; the ts_shp CLI's unit
remap turns them fake green -- docs/subterranean-design.md).

Scale: TS cell = 48 px, RA cell = 192 canvas px -> x4. The 121x121 TS canvas
lands on a 512 canvas (64x64 classic stub x 8), model-space centred so the
mound sits on the vehicle's draw anchor like the TS anim does.

Inputs (set TS_ART_DIR): $TS_ART_DIR/raw/DIG.SHP + $TS_ART_DIR/raw/ANIM.PAL
Outputs: Data/ART/.../RED_ALERT/VFX/TSDIG.ZIP + 37 TSDIG tiles in RA_VFX.XML.
The classic stub (TSDIG.SHP, 64x64x37) is built by scripts/build_tfassets.sh.
"""
import io, json, os, re, sys, zipfile
from PIL import Image

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR to the directory holding raw/DIG.SHP and raw/ANIM.PAL")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ts_shp

MOD = os.path.abspath(os.path.join(HERE, "..", "resources", "remaster_mods", "Vanilla_RA", "Data"))
VFX_DIR = f"{MOD}/ART/TEXTURES/SRGB/RED_ALERT/VFX"
XML = f"{MOD}/XML/TILESETS/RA_VFX.XML"
NAME = "TSDIG"
SCALE = 4.0
CANVAS = 512


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


def write_zip(path, name, frames):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for i, img in enumerate(frames):
            base = f"{name}-{i:04d}"
            W, H = img.width, img.height
            bb = img.getbbox() or (W // 2 - 1, H // 2 - 1, W // 2 + 1, H // 2 + 1)
            x0 = min(bb[0], W - bb[2])
            y0 = min(bb[1], H - bb[3])
            b = (x0, y0, W - x0, H - y0)
            z.writestr(base + ".tga", tga_bytes(img.crop(b)))
            z.writestr(base + ".meta", json.dumps({"size": [W, H], "crop": list(b)}))
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
    (W, H), raw = ts_shp.decode_shp(f"{ART}/raw/DIG.SHP")
    frames = []
    for f in raw:
        im = ts_shp.frame_to_rgba(f, pal, remap=None)
        scaled = im.resize((round(W * SCALE), round(H * SCALE)), Image.LANCZOS)
        out = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
        out.alpha_composite(scaled, (round(CANVAS / 2 - scaled.width / 2), round(CANVAS / 2 - scaled.height / 2)))
        frames.append(out)
    write_zip(f"{VFX_DIR}/{NAME}.ZIP", NAME.lower(), frames)
    patch_tileset(XML, NAME, len(frames))


if __name__ == "__main__":
    main()
