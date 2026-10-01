#!/usr/bin/env python3
"""Pack the HD TS buildings (resources/custom-art/ts-buildings-hd/<src>/) into the mod tree.

Each source folder holds buildings drawn on RA's square grid, the plot centred in the canvas
(-trim.png masks sit beside every frame and are not packed). A building's tileset frames are
either finished frames taken as they are, or composed: the building (healthy, damaged) with
overlays drawn over it, per state the runs in order (the idle loop, then the active run when the
building has one), each frame carrying every overlay's frame i mod its length, so a one-frame
overlay holds still. The damaged block starts where the healthy one ends, which is where
Shape_Number looks for it (the largest end of the IDLE and ACTIVE ranges in bdata.cpp).

Written per building (RA_STRUCTURES.XML patched in place):
  <INI>.ZIP       the tileset frames
  <INI>MAKE.ZIP   the build-up, when the building builds up on the map

The canvas is padded evenly to a height that is a multiple of 16, so the classic stub
(canvas x 3/16, scripts/ts_stub_dims.json) is a whole number and the plot stays centred.
Pixels at alpha 4 or less are cleared: they are invisible, and a veil of them over the
canvas would stop every frame cropping.

Usage: ts_pack_hd_buildings.py [INI ...]
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

# ini: the source folder, the build-up as (path prefix, frames) or None, and the tileset
# frames, either frames=(path prefix, count) or base=path prefix with runs=[(frames,
# overlays)], overlays as (path prefix, healthy frames, damaged frames). Paths take -NN.png.
BUILDINGS = {
    "TSFACT": dict(src="tsfact", make=("build-up/construction-yard-build", 32),
                   base="yard/construction-yard", runs=[
        # idle: fans turning, the door lamp sweeping, the roof lamps pulsing
        (30, [("A-fans/construction-yard-fans", range(0, 10), range(10, 20)),
              ("B-door-lamp/construction-yard-door-lamp", range(0, 10), range(10, 20)),
              ("C-roof-lamps/construction-yard-roof-lamps", range(0, 15), range(15, 30))]),
        # active, while a placed building goes up: the hangar lights up and the claw builds a
        # crate; the roof lamps hold steady and the door lamp is off (the producing art covers it)
        (20, [("A-fans/construction-yard-fans", range(0, 10), range(10, 20)),
              ("C-roof-lamps/construction-yard-roof-lamps", [8], [23]),
              ("D-producing/construction-yard-producing", range(0, 20), range(0, 20))]),
    ]),
    # one block per turbine level (1, 2, 3 pods), each 12 healthy then 12 damaged frames of
    # the tower's lights and the pods turning: the block Shape_Number picks by UpgradeLevel
    "TSPOWR": dict(src="tspowr", make=("build-up/power-plant-build", 24),
                   frames=("loop/power-plant-loop", 72)),
    # the turbine's placement ghost; it never stands on the map, it installs into a plant
    "TSTURB": dict(src="tspowr", make=None, frames=("pod-128/power-pod", 2)),
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
    def load(path, i):
        return Image.open(os.path.join(src, f"{path}-{i:02d}.png")).convert("RGBA")

    if "frames" in spec:
        path, count = spec["frames"]
        tiles = [load(path, i) for i in range(count)]
    else:
        tiles = []
        for state in (0, 1):
            base = load(spec["base"], state)
            for count, overlays in spec["runs"]:
                for i in range(count):
                    img = base.copy()
                    for path, healthy, damaged in overlays:
                        seq = (healthy, damaged)[state]
                        img.alpha_composite(load(path, seq[i % len(seq)]))
                    tiles.append(img)
    make = []
    if spec["make"]:
        path, count = spec["make"]
        make = [load(path, i) for i in range(count)]
    return tiles, make


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


def pack(name, tiles, make, size):
    os.makedirs(STRUCT_DIR, exist_ok=True)
    write_zip(f"{STRUCT_DIR}/{name}.ZIP", name.lower(), [clean(pad_to(i, *size)) for i in tiles])
    patch_in_place(name, len(tiles))
    if make:
        write_zip(f"{STRUCT_DIR}/{name}MAKE.ZIP", f"{name.lower()}make", [clean(pad_to(i, *size)) for i in make])
        patch_in_place(f"{name}MAKE", len(make))


def main(argv):
    names = [a for a in argv if a in BUILDINGS] or list(BUILDINGS)
    with open(STUB_MANIFEST) as f:
        stubs = json.load(f)
    for ini in names:
        spec = BUILDINGS[ini]
        tiles, make = frames(os.path.join(SRC, spec["src"]), spec)
        size = canvas_for(tiles + make)
        pack(ini, tiles, make, size)
        stubs[ini] = [size[0] * 3 // 16, size[1] * 3 // 16]
        print(f"{ini}: canvas {size[0]}x{size[1]}, stub {stubs[ini][0]}x{stubs[ini][1]}")
    with open(STUB_MANIFEST, "w") as f:
        json.dump(stubs, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
