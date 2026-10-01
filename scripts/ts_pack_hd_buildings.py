#!/usr/bin/env python3
"""Pack the HD TS buildings (resources/custom-art/ts-buildings-hd/<src>/) and units
(resources/custom-art/ts-units-hd/<src>/) into the mod tree.

Each source folder holds buildings drawn on RA's square grid, the plot centred in the canvas
(-trim.png masks sit beside every frame and are not packed). A building's tileset frames are
either finished frames taken as they are, or composed: the building (healthy, damaged) with
overlays drawn over it, per state the runs in order (the idle loop, then the active run when the
building has one), each frame carrying every overlay's frame i mod its length, so a one-frame
overlay holds still. The damaged block starts where the healthy one ends, which is where
Shape_Number looks for it (the largest end of the IDLE and ACTIVE ranges in bdata.cpp).

Written per building, to the asset pack scripts/asset_packs.py routes each name to (the
TS-HD-Graphics-Pack), its tileset XML patched in place:
  <INI>.ZIP       the tileset frames
  <INI>MAKE.ZIP   the build-up, when the building builds up on the map
Units go to UNITS/, and a building's concrete apron is cut from its layer into 128 px ground
tiles, one per cell of its smudge, the same in every theatre. A unit whose shells
leave a barrel drawn in its frames also writes redalert/<ini>_muzzle.h: the barrel tip per
turret facing, in leptons from the unit's position, read from the art's muzzle table.

The canvas is padded evenly to a height that is a multiple of 16, so the classic stub
(canvas x 3/16, scripts/ts_stub_dims.json) is a whole number and the plot stays centred.
Pixels at alpha 4 or less are cleared: they are invisible, and a veil of them over the
canvas would stop every frame cropping.

Usage: ts_pack_hd_buildings.py [INI ...]   (buildings, units and aprons by ini; none = all)
License: GPL v3.
"""
import io, json, os, re, sys, zipfile
import numpy as np
from PIL import Image

import asset_packs

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(SCRIPTS, "..", "resources", "custom-art", "ts-buildings-hd")
UNITS_SRC = os.path.join(SCRIPTS, "..", "resources", "custom-art", "ts-units-hd")
REDALERT = os.path.join(SCRIPTS, "..", "redalert")
THEATRES = ("TEMPERATE", "SNOW", "INTERIOR")
STUB_MANIFEST = f"{SCRIPTS}/ts_stub_dims.json"
HAZE_ALPHA = 4

# The launcher recolours every green of a building to its owner's colour, so Tiberium seen in a
# building is drawn in the yellow-green TD's silo shows in game (hue ~77), luminance kept.
TIBERIUM = np.array([191.0, 231.0, 90.0])


# The war factory's hazard stripes, on the lane from its door (x 128-284, y 370-416 of its source canvas).
# The apron under them is ground art, which the launcher never recolours, so the stripes there and on the
# building layers that show the same lane are all burnt to the gold the launcher makes of that green ramp,
# (v, 0.82v, 0), and the two meet without a seam. Hazard markings are yellow in TS whoever owns them.
WEAP_LANE = (128, 370, 284, 416)


def lane_gold(img):
    """The lane's house green, antialiased edges included, as gold: a pixel's green beyond its red
    and blue is the stripe's share of it, and that share turns from (0, e, 0) to (e, 0.82e, 0)."""
    a = np.asarray(img).copy()
    x0, y0, x1, y1 = WEAP_LANE
    box = a[y0:y1, x0:x1].astype(np.int32)
    r, g, b = box[..., 0].copy(), box[..., 1].copy(), box[..., 2].copy()
    e = g - np.maximum(r, b)
    hit = (box[..., 3] > 0) & (e > 4)
    box[hit, 0] = np.minimum(r[hit] + e[hit], 255)
    box[hit, 1] = np.maximum(r[hit], b[hit]) + np.round(e[hit] * 0.82)
    a[y0:y1, x0:x1] = box.astype(np.uint8)
    return Image.fromarray(a, "RGBA")


# The pad is drawn about the door's centre line (x 206.5): its seams and ring are centred on the lane. Its west
# half steps back in beside the building; the east half takes the same outline, the west half mirrored, so no
# grey patch runs up beside the building there. The lane keeps its own stripes.
WEAP_AXIS2 = 413


def weap_pad(img):
    a = np.asarray(lane_gold(img)).copy()
    x0, y0, x1, y1 = WEAP_LANE
    keep = a.copy()
    for x in range(WEAP_AXIS2 // 2 + 1, a.shape[1]):
        a[:, x] = keep[:, WEAP_AXIS2 - x]
    a[y0:y1, x0:x1] = keep[y0:y1, x0:x1]
    return Image.fromarray(a, "RGBA")


# The fifth lamp on the beam over the door, on the east pillar's face (x 307-325, y 233-259), comes out: the
# pillar is filled in from its face beside the lamp, its edge (x 316-318, where the rows above show one) from those
# rows, and what lies east of the edge from the column just past the lamp.
LAMP5 = (307, 233, 326, 260)
LAMP5_EDGE = (316, 319)


def drop_lamp5(img):
    a = np.asarray(img).copy()
    x0, y0, x1, y1 = LAMP5
    e0, e1 = LAMP5_EDGE
    for y in range(y0, y1):
        for x in range(x0, x1):
            if x < e0:
                a[y, x] = a[y, x - 14]
            elif x < e1 and a[y0 - 2, x, 3] >= 64:
                a[y, x] = a[y0 - 2, x]
            else:
                a[y, x] = a[y, x1 + 1]
    return Image.fromarray(a, "RGBA")


def bay_lamp5_shadow(img):
    """The ground shadow where the fifth lamp hung over it: the bay layer leaves the lamp's pixels to the
    near face, so the hole it leaves takes the shadow of the column just east of it (x 324)."""
    a = np.asarray(img).copy()
    for y in range(LAMP5[1], LAMP5[3]):
        for x in range(LAMP5_EDGE[0] + 1, 324):
            if a[y, x, 3] == 0:
                a[y, x] = a[y, 324]
    return Image.fromarray(a, "RGBA")


# The door lamps' light run over four lamps: TS's sixteen frames, its fifth lamp gone, the steps where the light
# sat on it dropped and the ends held.
LAMP_RUN = [0, 1, 2, 3, 4, 5, 5, 9, 10, 11, 12, 13, 14, 15, 0, 0]


def weap_build(img, i):
    img = lane_gold(img)
    return drop_lamp5(img) if i >= 16 else img


def weap_bay(img):
    """The war factory's under-door layer kept to its doorway (the shut door's own outline, 2 px
    wider): the art carries a copy of the apron round it, which the apron tiles already draw."""
    door = Image.open(os.path.join(SRC, "tsweap", "D-door", "war-factory-door-00.png")).convert("RGBA")
    hole = np.asarray(door)[..., 3] > 0
    for _ in range(2):
        grown = hole.copy()
        grown[1:] |= hole[:-1]
        grown[:-1] |= hole[1:]
        grown[:, 1:] |= hole[:, :-1]
        grown[:, :-1] |= hole[:, 1:]
        hole = grown
    a = np.asarray(lane_gold(img)).copy()
    a[~hole] = 0
    return Image.fromarray(a, "RGBA")


def tiberium(img):
    a = np.asarray(img).astype(np.float32)
    lum = a[..., :3] @ np.array([0.299, 0.587, 0.114], np.float32)
    rgb = TIBERIUM[None, None, :] * (lum / (TIBERIUM @ np.array([0.299, 0.587, 0.114])))[..., None]
    a[..., :3] = np.clip(rgb, 0, 255)
    return Image.fromarray(a.round().astype(np.uint8), "RGBA")


# ini: the source folder, the build-up as (path prefix, frames) or None, and the tileset
# frames, either frames=(path prefix, count) or base=path prefix with runs=[(frames,
# overlays)], overlays as (path prefix, healthy frames, damaged frames[, recolour]), recolour
# a function applied to the overlay before it is drawn. blocks=[overlays, ...]
# repeats the whole healthy + damaged set once per entry with those overlays drawn first.
# pad_bottom / pad_top add that many transparent px under / over every frame and crop_top cuts
# that many empty px off the top, for art drawn on a plot of another depth than the building's own (the canvas
# centres on the building's plot). repeat=n plays the frames n times over (one set for both states), and
# recolour / make_recolour apply a function to every tileset / build-up frame as it loads. Paths take -NN.png.
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
    # one block per fill level (empty, a third, two thirds, full: the Tiberium through the glass),
    # each the lamps' 16-frame loop healthy then damaged: the block Shape_Number picks by how
    # full the house's storage is
    # the bunkers on the 2x1 plot row: the art is drawn on a 2x2, its foundation's south edge on
    # the south edge, so 128 px under it centres the canvas on the 2x1 with the bib row in front.
    # Idle: the flag waving (7) under the entrance lamps and the mast's beacon (8): 56 frames
    "TSPILE": dict(src="tspile", make=("build-up/barracks-build", 24), base="building/barracks", runs=[
        (56, [("C-flag/barracks-flag", range(0, 7), range(7, 14)),
              ("A-lamps/barracks-lamps", range(0, 8), range(8, 16)),
              ("B-beacon/barracks-beacon", range(0, 8), range(8, 16))]),
    ], pad_bottom=128),
    # TS's wedge its own way round, drawn on a 3x1 row: 128 px over it centre the canvas on the 3x2
    # plot, the wedge on the south row, the fins and dome in the north row, the bib row in front.
    # Idle: the dome's panels pulse (8), healthy then damaged.
    "TSTECH": dict(src="tstech", make=("build-up/tech-center-build", 24),
                   frames=("loop/tech-center-loop", 16), pad_top=128),
    # The silo stands on its 2x1 plot row with the bib row in front, seated like the barracks.
    "TSSILO": dict(src="tssilo", make=("build-up/silo-build", 24), base="silo/silo",
                   blocks=[[("A-tiberium/silo-tiberium", [lv], [lv + 4], tiberium)] for lv in range(4)],
                   runs=[(16, [("B-lamps/silo-lamps", range(0, 16), range(16, 32))])], pad_bottom=128),
    # The refinery turned 22.5 degrees on its 4x3 plot. Idle: the dock lamps (16), healthy then
    # damaged; the flare stack's fire is its own layer (20 lit frames, then 20 empty).
    "TSPROC": dict(src="tsproc", make=("build-up/refinery-build", 24), frames=("loop/refinery-loop", 32)),
    "TSPROCFR": dict(src="tsproc", make=None, frames=("B-fire/refinery-fire", 40)),
    # its front: the building in front of the dock lane, the idle loop's frames masked to it, drawn over a docked
    # truck so it backs in under the deck
    "TSPROCNF": dict(src="tsproc", make=None, frames=("front/refinery-front", 32)),
    # The war factory on its 3x4 plot, door south: RA's 3x3 war factory slot with an empty row behind it, the art's
    # own canvas centred on it (the build-up's raised poles reach into the empty row). Its body is
    # the door bay with the building's ground shadow, under units; the near face (the rest of the building,
    # with the door lamps (16, a four-lamp run), the roof lamps (8) and the fans (4) over 32 idle steps) and the roll-up door
    # draw over a vehicle in the bay. The under-door is the bay seen with the door up, and its build-up the 26
    # frames of TS's GTWEAPMK order.
    "TSWEAP": dict(src="tsweap", make=("build-up/war-factory-build", 26), make_fix=weap_build,
                   base="building-bay/war-factory-bay", recolour=bay_lamp5_shadow, runs=[(32, [])]),
    "TSWEAPNF": dict(src="tsweap", make=None, base="2-over-units/war-factory-over", recolour=drop_lamp5, runs=[
        (32, [("A-lamps/war-factory-lamps", LAMP_RUN, range(16, 32)),
              ("B-lamps/war-factory-lamps-b", range(0, 8), range(8, 16)),
              ("C-fans/war-factory-fans", range(0, 4), range(4, 8))]),
    ]),
    "TSWEAPDR": dict(src="tsweap", make=None, frames=("D-door/war-factory-door", 9), repeat=2),
    "TSWEAPUD": dict(src="tsweap", make=None, frames=("1-under-door/war-factory-under", 2), repeat=2,
                     recolour=weap_bay),
}
# The open-door near face is the same layer: the door is its own layer here.
BUILDINGS["TSWEAPNU"] = BUILDINGS["TSWEAPNF"]

# ini: the source folder and the frames (path prefix, count) on the unit's own canvas. root
# overrides the folder the source sits in, digits the frame number's width, and muzzle names the
# art's table of barrel tips (frame, facing, canvas x, canvas y) for the generated header.
UNITS = {
    "TSHARV": dict(src="tsproc", frames=("harvester/harvester", 64)),
    "TSTITN": dict(root=UNITS_SRC, src="tstitn", frames=("frames/tstitn", 128), digits=4,
                   muzzle="3d/muzzle.txt"),
}

# smudge ini: the source folder, the apron's layer on its building's canvas, where the smudge's
# north-west cell starts on that canvas, and the smudge's size in cells (sdata.cpp).
APRONS = {
    "TSPROCBB": dict(src="tsproc", layer="bib/refinery-bib-00", origin=(112, 272), cells=(5, 3)),
    "TSWEAPBB": dict(src="tsweap", layer="bib/war-factory-bib-00", origin=(16, 128), cells=(3, 3),
                     recolour=weap_pad),
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


def crop_above(img, px):
    if np.asarray(img)[:px, :, 3].max() > HAZE_ALPHA:
        raise SystemExit(f"cannot cut {px} px off the top: art stands there")
    return img.crop((0, px, img.width, img.height))


def pad_over(img, px):
    out = Image.new("RGBA", (img.width, img.height + px), (0, 0, 0, 0))
    out.paste(img, (0, px))
    return out


def pad_under(img, px):
    out = Image.new("RGBA", (img.width, img.height + px), (0, 0, 0, 0))
    out.paste(img, (0, 0))
    return out


def frames(src, spec):
    def load(path, i):
        return Image.open(os.path.join(src, f"{path}-{i:02d}.png")).convert("RGBA")

    if "frames" in spec:
        path, count = spec["frames"]
        tiles = [load(path, i) for i in range(count)] * spec.get("repeat", 1)
    else:
        tiles = []
        for block in spec.get("blocks", [[]]):
            for state in (0, 1):
                base = load(spec["base"], state)
                for count, overlays in spec["runs"]:
                    for i in range(count):
                        img = base.copy()
                        for path, healthy, damaged, *recolour in block + overlays:
                            seq = (healthy, damaged)[state]
                            o = load(path, seq[i % len(seq)])
                            img.alpha_composite(recolour[0](o) if recolour else o)
                        tiles.append(img)
    make = []
    if spec["make"]:
        path, count = spec["make"]
        make = [load(path, i) for i in range(count)]
    if spec.get("recolour"):
        tiles = [spec["recolour"](i) for i in tiles]
    if spec.get("make_recolour"):
        make = [spec["make_recolour"](i) for i in make]
    if spec.get("make_fix"):
        make = [spec["make_fix"](img, i) for i, img in enumerate(make)]
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


def patch_in_place(name, count, xml_path):
    """Install exactly `count` tiles for `name` where its tiles already stand (appended when
    it has none), leaving every other tile of the file where it is."""
    with open(xml_path, encoding="utf-8", newline="") as f:
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
    with open(xml_path, "w", encoding="utf-8", newline="") as f:
        f.write(xml)
    print(f"patched {os.path.basename(xml_path)}: {name} -> {count} tiles (replaced {len(runs)})")


def pack(name, tiles, make, size):
    write_zip(asset_packs.art_zip(name, "STRUCTURES"), name.lower(), [clean(pad_to(i, *size)) for i in tiles])
    patch_in_place(name, len(tiles), asset_packs.tileset_xml(name, "STRUCTURES"))
    if make:
        write_zip(asset_packs.art_zip(f"{name}MAKE", "STRUCTURES"), f"{name.lower()}make",
                  [clean(pad_to(i, *size)) for i in make])
        patch_in_place(f"{name}MAKE", len(make), asset_packs.tileset_xml(f"{name}MAKE", "STRUCTURES"))


def pack_unit(name, spec):
    path, count = spec["frames"]
    src = os.path.join(spec.get("root", SRC), spec["src"])
    digits = spec.get("digits", 2)
    tiles = [Image.open(os.path.join(src, f"{path}-{i:0{digits}d}.png")).convert("RGBA") for i in range(count)]
    write_zip(asset_packs.art_zip(name, "UNITS"), name.lower(), [clean(i) for i in tiles])
    patch_in_place(name, count, asset_packs.tileset_xml(name, "UNITS"))
    if spec.get("muzzle"):
        write_muzzle(name, os.path.join(src, spec["muzzle"]), tiles[0].size)


def write_muzzle(name, table, size):
    """The barrel tip per turret facing (counter-clockwise from north, the engine's frame order)
    as leptons east and south of the unit's position, which is the canvas centre. The canvas
    draws at 8 px per classic pixel, so one canvas px is 4/3 lepton."""
    rows = []
    with open(table) as f:
        for line in f:
            parts = line.split()
            if len(parts) == 4 and all(re.fullmatch(r"-?\d+(\.\d+)?", p) for p in parts):
                rows.append((int(parts[1]), float(parts[2]), float(parts[3])))
    rows.sort()
    assert [r[0] for r in rows] == list(range(len(rows))), f"{table}: facings out of order"
    cx, cy = size[0] / 2, size[1] / 2
    var = f"_{name.lower()}_muzzle"
    out = [f"// GENERATED by scripts/ts_pack_hd_buildings.py from {os.path.relpath(table, os.path.join(SCRIPTS, '..'))}; do not hand-edit.",
           "// Per-CCW-turret-facing muzzle offsets (leptons from unit center).",
           f"static const short {var}[{len(rows)}][2] = {{"]
    out += [f"    {{{round((x - cx) * 4 / 3)}, {round((y - cy) * 4 / 3)}}}," for _, x, y in rows]
    out.append("};")
    path = os.path.join(REDALERT, f"{name.lower()}_muzzle.h")
    with open(path, "w") as f:
        f.write("\n".join(out) + "\n")
    print(f"wrote {os.path.relpath(path)} ({len(rows)} facings)")


def pack_apron(name, spec):
    """One full 128 px tile per smudge cell, row by row from the north-west, in every theatre's
    archive and tileset."""
    layer = Image.open(os.path.join(SRC, spec["src"], spec["layer"] + ".png")).convert("RGBA")
    layer = clean(spec["recolour"](layer) if spec.get("recolour") else layer)
    (x0, y0), (cols, rows) = spec["origin"], spec["cells"]
    tiles = [layer.crop((x0 + 128 * c, y0 + 128 * r, x0 + 128 * (c + 1), y0 + 128 * (r + 1)))
             for r in range(rows) for c in range(cols)]
    for theatre in THEATRES:
        path = asset_packs.art_zip(name, f"TERRAIN_{theatre}")
        with zipfile.ZipFile(path, "w") as z:
            for i, img in enumerate(tiles):
                buf = io.BytesIO()
                img.save(buf, format="TGA")
                for member, data in ((f"{name.lower()}-{i:04d}.tga", buf.getvalue()),
                                     (f"{name.lower()}-{i:04d}.meta",
                                      json.dumps({"size": [128, 128], "crop": [0, 0, 128, 128]}))):
                    z.writestr(zipfile.ZipInfo(member, date_time=(1980, 1, 1, 0, 0, 0)), data, zipfile.ZIP_DEFLATED)
        print(f"wrote {os.path.relpath(path)} ({len(tiles)} tiles)")
        patch_in_place(name, len(tiles), asset_packs.tileset_xml(name, f"TERRAIN_{theatre}"))


def main(argv):
    every = list(BUILDINGS) + list(UNITS) + list(APRONS)
    asked = [a for a in argv if a in every] or every
    for name in asked:
        if name in UNITS:
            pack_unit(name, UNITS[name])
        elif name in APRONS:
            pack_apron(name, APRONS[name])
    names = [a for a in asked if a in BUILDINGS]
    with open(STUB_MANIFEST) as f:
        stubs = json.load(f)
    for ini in names:
        spec = BUILDINGS[ini]
        tiles, make = frames(os.path.join(SRC, spec["src"]), spec)
        if spec.get("crop_top"):
            tiles = [crop_above(i, spec["crop_top"]) for i in tiles]
            make = [crop_above(i, spec["crop_top"]) for i in make]
        if spec.get("pad_top"):
            tiles = [pad_over(i, spec["pad_top"]) for i in tiles]
            make = [pad_over(i, spec["pad_top"]) for i in make]
        if spec.get("pad_bottom"):
            tiles = [pad_under(i, spec["pad_bottom"]) for i in tiles]
            make = [pad_under(i, spec["pad_bottom"]) for i in make]
        size = canvas_for(tiles + make)
        pack(ini, tiles, make, size)
        stubs[ini] = [size[0] * 3 // 16, size[1] * 3 // 16]
        print(f"{ini}: canvas {size[0]}x{size[1]}, stub {stubs[ini][0]}x{stubs[ini][1]}")
    with open(STUB_MANIFEST, "w") as f:
        json.dump(stubs, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main(sys.argv[1:])
