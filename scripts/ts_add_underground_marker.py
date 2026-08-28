#!/usr/bin/env python3
"""Append the underground marker (shape 112) to the subterranean unit tilesets.

While a Devil's Tongue / Subterranean APC tunnels, the DLL draws this frame
instead of the hull: a faint ring of disturbed earth on the owner's screen so
the launcher still hangs the selection box and health bar on the unit
(enemies never see it -- the export masks the object for non-allies). Drawn
procedurally with straight alpha (never paste-through-mask, contracts §4).
Re-runnable: replaces shape 112 if present and re-declares 113 tiles.
"""
import io, json, math, os, re, sys, zipfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.abspath(os.path.join(HERE, "..", "resources", "remaster_mods", "Vanilla_RA", "Data"))
UNITS_DIR = f"{MOD}/ART/TEXTURES/SRGB/RED_ALERT/UNITS"
XML = f"{MOD}/XML/TILESETS/RA_UNITS.XML"
CANVAS = 384
MARKER = 112


def marker():
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    px = img.load()
    cx, cy = CANVAS / 2, CANVAS / 2 + 24   # sits on the ground plane, not the hull centre
    rx, ry = 96.0, 52.0                    # isometric ground ellipse
    for y in range(CANVAS):
        for x in range(CANVAS):
            d = math.hypot((x - cx) / rx, (y - cy) / ry)
            if d > 1.0:
                continue
            # two soft rings of loosened earth fading to nothing at the rim
            ring = math.exp(-((d - 0.85) ** 2) / 0.006) * 0.9 + math.exp(-((d - 0.5) ** 2) / 0.01) * 0.55
            core = max(0.0, 1.0 - d * 1.6) * 0.35
            a = min(1.0, ring + core) * 0.75
            if a < 0.02:
                continue
            shade = 0.85 - 0.35 * ring
            r, g, b = int(112 * shade), int(84 * shade), int(52 * shade)
            px[x, y] = (r, g, b, int(a * 255))
    return img


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


def append_marker(zip_path, name, img):
    old = zipfile.ZipFile(zip_path)
    entries = [(n, old.read(n)) for n in old.namelist() if not n.startswith(f"{name}-{MARKER:04d}")]
    old.close()
    W, H = img.size
    bb = img.getbbox()
    x0 = min(bb[0], W - bb[2]); y0 = min(bb[1], H - bb[3])
    b = (x0, y0, W - x0, H - y0)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for n, data in entries:
            z.writestr(n, data)
        z.writestr(f"{name}-{MARKER:04d}.tga", tga_bytes(img.crop(b)))
        z.writestr(f"{name}-{MARKER:04d}.meta", json.dumps({"size": [W, H], "crop": list(b)}))
    print(f"{zip_path}: {len(entries)//2 + 1} shapes")


def patch_tileset(xml_path, name, count):
    sub = name.lower()
    xml = open(xml_path, encoding="utf-8").read()
    xml = re.sub(r"\t*<Tile>\s*<Key>\s*<Name>" + re.escape(name) + r"</Name>.*?</Tile>\n?", "", xml, flags=re.S)
    block = ('\t<Tile>\n\t\t<Key>\n\t\t\t<Name>%s</Name>\n\t\t\t<Shape>%d</Shape>\n\t\t</Key>\n'
             '\t\t<Value>\n\t\t\t<Frames>\n\t\t\t\t<Frame>%s</Frame>\n\t\t\t</Frames>\n\t\t</Value>\n\t</Tile>\n')
    blocks = "".join(block % (name, i, f"{sub}\\{sub}-{i:04d}.tga") for i in range(count))
    idx = xml.rindex("</Tiles>")
    open(xml_path, "w", encoding="utf-8").write(xml[:idx] + blocks + xml[idx:])
    print(f"patched RA_UNITS.XML: {name} -> {count} tiles")


if __name__ == "__main__":
    img = marker()
    out = sys.argv[1] if len(sys.argv) > 1 else None
    if out:
        img.save(out); print("preview", out); sys.exit()
    for name in ("TSSUBTANK", "TSSAPC"):
        append_marker(f"{UNITS_DIR}/{name}.ZIP", name.lower(), img)
        patch_tileset(XML, name, MARKER + 1)
