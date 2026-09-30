#!/usr/bin/env python3
"""Pack the HD TS buildings (resources/custom-art/ts-buildings-hd/<ini>/) into the mod tree.

Each source folder holds one building drawn on RA's square grid, its plot centred in the canvas:
  yard/<prefix>-00.png, -01.png      healthy, damaged
  build-up/<prefix>-build-NN.png     the construction frames
  <overlay dir>/<prefix>-<tag>-NN.png   idle overlays, drawn over the building frame of the same state
(-trim.png masks sit beside every frame and are not packed.)

Written per building (RA_STRUCTURES.XML patched):
  <INI>.ZIP       per state, healthy then damaged: the idle loop, then the active run when the
                  building has one. Each frame is the building with every overlay's frame
                  (i mod its length) drawn over it, so a one-frame overlay holds still. The damaged
                  block starts where the healthy one ends, which is where Shape_Number looks for it
                  (the largest end of the IDLE and ACTIVE ranges in bdata.cpp).
  <INI>MAKE.ZIP   the build-up

The canvas is padded evenly to a height that is a multiple of 16, so the classic stub
(canvas x 3/16, scripts/ts_stub_dims.json) is a whole number and the plot stays centred.
Pixels at alpha 4 or less are cleared: they are invisible, and a veil of them over the
canvas would stop every frame cropping.

--compare INI=DIR packs DIR's frames (same layout, e.g. the TS-angle render) on the same
canvas as INI under the names <INI>I / <INI>IMAKE, for a side-by-side view in game.

Usage: ts_pack_hd_buildings.py [INI ...] [--compare INI=DIR]
License: GPL v3.
"""
import io, json, os, re, sys, zipfile
import numpy as np
from PIL import Image

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(SCRIPTS, "..", "resources", "remaster_mods", "Vanilla_RA")
SRC = os.path.join(SCRIPTS, "..", "resources", "custom-art", "ts-buildings-hd")
STRUCT_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/STRUCTURES"
XML = f"{MOD}/Data/XML/TILESETS/RA_STRUCTURES.XML"
STUB_MANIFEST = f"{SCRIPTS}/ts_stub_dims.json"
HAZE_ALPHA = 4

# ini: source prefix, build-up frames, and the animation runs in tileset order, each
# (frames, overlays) with overlays as (dir, tag, healthy frames, damaged frames). The runs
# match the building's BSTATE_IDLE / BSTATE_ACTIVE entries in bdata.cpp.
BUILDINGS = {
    "TSFACT": dict(prefix="construction-yard", make=32, runs=[
        # idle: fans turning, the door lamp sweeping, the roof lamps pulsing
        (30, [("A-fans", "fans", range(0, 10), range(10, 20)),
              ("B-door-lamp", "door-lamp", range(0, 10), range(10, 20)),
              ("C-roof-lamps", "roof-lamps", range(0, 15), range(15, 30))]),
        # active, while a placed building goes up: the hangar lights up and the claw builds a
        # crate; the roof lamps hold steady and the door lamp is off (the producing art covers it)
        (20, [("A-fans", "fans", range(0, 10), range(10, 20)),
              ("C-roof-lamps", "roof-lamps", [8], [23]),
              ("D-producing", "producing", range(0, 20), range(0, 20))]),
    ]),
}


def clean(img):
    a = np.asarray(img).copy()
    a[a[..., 3] <= HAZE_ALPHA] = 0
    return Image.fromarray(a, "RGBA")


def pad_to(img, w, h):
    if img.size == (w, h):
        return img
    if img.width > w or img.height > h or (w - img.width) % 2 or (h - img.height) % 2:
        raise SystemExit(f"cannot centre a {img.size} frame on {w}x{h}")
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(img, ((w - img.width) // 2, (h - img.height) // 2))
    return out


def frames(src, spec):
    p = spec["prefix"]

    def load(*parts):
        return Image.open(os.path.join(src, *parts)).convert("RGBA")

    loop = []
    for state in (0, 1):
        base = load("yard", f"{p}-{state:02d}.png")
        for count, overlays in spec["runs"]:
            for i in range(count):
                img = base.copy()
                for d, tag, healthy, damaged in overlays:
                    seq = (healthy, damaged)[state]
                    img.alpha_composite(load(d, f"{p}-{tag}-{seq[i % len(seq)]:02d}.png"))
                loop.append(img)
    make = [load("build-up", f"{p}-build-{i:02d}.png") for i in range(spec["make"])]
    return loop, make


def canvas_for(imgs):
    w = max(i.width for i in imgs)
    h = max(i.height for i in imgs)
    return w + (-w % 16), h + (-h % 16)


def write_zip(path, name, frames):
    """Each frame cropped to its content, with a .meta giving the canvas and the crop box.
    Entries carry a fixed date, so the same frames always pack to the same bytes."""
    def put(z, member, data):
        z.writestr(zipfile.ZipInfo(member, date_time=(1980, 1, 1, 0, 0, 0)), data, zipfile.ZIP_DEFLATED)

    with zipfile.ZipFile(path, "w") as z:
        for i, img in enumerate(frames):
            base = f"{name}-{i:04d}"
            b = img.getbbox() or (0, 0, img.width, img.height)
            buf = io.BytesIO()
            img.crop(b).save(buf, format="TGA")
            put(z, base + ".tga", buf.getvalue())
            put(z, base + ".meta", json.dumps(
                {"size": [img.width, img.height], "crop": [b[0], b[1], b[2], b[3]]}))
    print(f"wrote {os.path.relpath(path)} ({len(frames)} frames)")


def tile_block(name, shape):
    return ("\t<Tile>\n\t\t<Key>\n\t\t\t<Name>%s</Name>\n\t\t\t<Shape>%d</Shape>\n\t\t</Key>\n"
            "\t\t<Value>\n\t\t\t<Frames>\n\t\t\t\t<Frame>%s\\%s-%04d.tga</Frame>\n\t\t\t</Frames>\n\t\t</Value>\n\t</Tile>\n"
            % (name, shape, name.lower(), name.lower(), shape))


def patch_in_place(name, count):
    """Install exactly `count` tiles for `name` where its tiles already stand (appended when
    it has none), leaving every other tile of the file where it is."""
    with open(XML, encoding="utf-8", newline="") as f:
        xml = f.read()
    nl = "\r\n" if "\r\n" in xml else "\n"
    blocks = "".join(tile_block(name, s) for s in range(count)).replace("\n", nl)
    pat = re.compile(r"\t<Tile>" + nl + r"\t\t<Key>" + nl + r"\t\t\t<Name>" + re.escape(name)
                     + r"</Name>.*?</Tile>" + nl, re.S)
    runs = list(pat.finditer(xml))
    if runs:
        xml = xml[:runs[0].start()] + blocks + pat.sub("", xml[runs[0].start():])
    else:
        idx = xml.rindex("</Tiles>")
        xml = xml[:idx] + blocks + xml[idx:]
    with open(XML, "w", encoding="utf-8", newline="") as f:
        f.write(xml)
    print(f"patched RA_STRUCTURES.XML: {name} -> {count} tiles (replaced {len(runs)})")


def pack(name, loop, make, size):
    loop = [clean(pad_to(i, *size)) for i in loop]
    make = [clean(pad_to(i, *size)) for i in make]
    os.makedirs(STRUCT_DIR, exist_ok=True)
    write_zip(f"{STRUCT_DIR}/{name}.ZIP", name.lower(), loop)
    write_zip(f"{STRUCT_DIR}/{name}MAKE.ZIP", f"{name.lower()}make", make)
    patch_in_place(name, len(loop))
    patch_in_place(f"{name}MAKE", len(make))


def main(argv):
    compare = dict(argv[i + 1].split("=", 1) for i, a in enumerate(argv) if a == "--compare")
    names = [a for a in argv if a in BUILDINGS] or list(BUILDINGS)
    with open(STUB_MANIFEST) as f:
        stubs = json.load(f)
    for ini in names:
        spec = BUILDINGS[ini]
        loop, make = frames(os.path.join(SRC, ini.lower()), spec)
        size = canvas_for(loop + make)
        pack(ini, loop, make, size)
        stubs[ini] = [size[0] * 3 // 16, size[1] * 3 // 16]
        print(f"{ini}: canvas {size[0]}x{size[1]}, stub {stubs[ini][0]}x{stubs[ini][1]}")
        if ini in compare:
            cl, cm = frames(os.path.expanduser(compare[ini]), spec)
            pack(f"{ini}I", cl, cm, size)
            print(f"{ini}I: {compare[ini]} on the same canvas")
    with open(STUB_MANIFEST, "w") as f:
        json.dump(stubs, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
