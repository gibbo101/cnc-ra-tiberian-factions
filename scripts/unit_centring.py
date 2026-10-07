#!/usr/bin/env python3
r"""
Centre each voxel vehicle's hull on its unit, the way EA's own vehicles sit.

EA's HD vehicles (Red Alert and Tiberian Dawn tanks, APCs, jeeps, harvesters, MCVs) draw the
hull centred on the unit to within about 1.5 classic px; turrets and barrels stick up past it,
and only the Mammoths sit higher (-2.6). The launcher anchors every frame by its canvas centre
and centres the selection box on the unit, so a hull drawn high stands above its neighbours in
the same cell row and leaves the box's slack below it. The voxel packers put the model's ground
origin at the canvas centre, which leaves the hull 3 to 6.5 classic px high.

For each unit in UNITS this moves every frame of its ZIP down by the hull's offset (the median
centre of the opaque hull pixels over the facings) by rewriting each frame's crop offset; the
pixels are untouched. Art that rides with the unit in another ZIP (the deployed Mobile Sensor)
moves the same distance. The drops are recorded in scripts/unit_art_drop.json and written to
redalert/unit_art_drop.h, which Fire_Coord adds to the packer-generated fire points (those are
measured on the art before the drop). It then prints each unit's selection box measured from
the centred art, for _art_boxes in udata.cpp.

Run it after re-packing any unit in UNITS: it measures again, so re-packed art is centred and
keeps its recorded drop, and art already centred is left as it is.

Usage:
  scripts/unit_centring.py            # centre, write the header, print the boxes
  scripts/unit_centring.py --check    # report only; exit 1 if any unit is off centre
  scripts/unit_centring.py --audit    # every packed unit's first 32 frames, at 8x density
"""
import io
import json
import os
import re
import statistics
import sys
import zipfile

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_packs

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DROPS_JSON = os.path.join(REPO, "scripts", "unit_art_drop.json")
HEADER = os.path.join(REPO, "redalert", "unit_art_drop.h")
C3_HEADER = os.path.join(REPO, "redalert", "c3tanks.h")
UDATA = os.path.join(REPO, "redalert", "udata.cpp")

UNIT_DENSITY = 8.0  # canvas px per classic px for packed units (canvas = ShapeSize x 8)
BUILDING_DENSITY = 256 / 48  # the deployed sensor's density (256 x 416 over a 48 x 78 stub)
LEPTONS_PER_CLASSIC_PX = 256 / 24
OPAQUE = 200  # alpha at or above this is the body; the soft drop shadow stays out
TOLERANCE = 0.5  # classic px: art closer to centre than this is left alone
EA_SPREAD = 1.5  # classic px: how far EA's own vehicle hulls sit from centre (Mammoths aside)
WALKERS = {"TSTITN", "TSHMEC", "TSJUGG", "TSSMEC"}
AIRCRAFT = {"TSORCA", "TSORCAB", "TSCARRY"}
VOXEL_PREFIXES = ("TS", "R2", "C3")

# name: (hull frames, hull frames per facing, first turret frame or None, turret seat, partners)
# Partners are (ZIP name, kind, density) moved by the same classic distance.
UNITS = {
    "C3MK3": (96, 3, 96, "c3mk3", ()),
    "C3PRED": (96, 3, 96, "c3pred", ()),
    "R2APOC": (32, 1, 32, None, ()),
    "R2PRIS": (32, 1, 32, None, ()),
    "TS4TNK": (32, 1, 32, None, ()),
    "TSSONIC": (32, 1, 32, "sonic", ()),
    "TSAPC": (32, 1, None, None, ()),
    "TSSAPC": (32, 1, None, None, ()),
    "TSSUBTANK": (32, 1, None, None, ()),
    "TSTTNK": (32, 1, 32, None, ()),
    "TSMEMP": (32, 1, None, None, ()),
    "TSMWAR": (32, 1, None, None, ()),
    "TSMCV": (32, 1, None, None, ()),
    "TSLPST": (32, 1, None, None, (("TSDPSA", "STRUCTURES", BUILDING_DENSITY),
                                   ("TSDPSAMAKE", "STRUCTURES", BUILDING_DENSITY))),
}


def c3_seats(name):
    """The C&C3 turret seats per hull facing, classic px (c3tanks.h _<name>_seat_px)."""
    text = open(C3_HEADER).read()
    m = re.search(r"_%s_seat_px\[32\]\[2\] = \{(.*?)\};" % name, text, re.S)
    return [tuple(int(v) for v in p) for p in re.findall(r"\{(-?\d+), (-?\d+)\}", m.group(1))]


def sonic_seats():
    """UnitTypeClass::Sonic_Turret_Seat per hull frame, classic px, read from udata.cpp."""
    text = open(UDATA).read()
    m = re.search(r"void UnitTypeClass::Sonic_Turret_Seat.*?_seat\[32\]\[2\] = \{(.*?)\};", text, re.S)
    return [tuple(int(v) for v in p) for p in re.findall(r"\{(-?\d+), (-?\d+)\}", m.group(1))]


def seats_for(key):
    if key is None:
        return [(0, 0)] * 32
    return sonic_seats() if key == "sonic" else c3_seats(key)


def read_zip(path):
    z = zipfile.ZipFile(path)
    infos = z.infolist()
    data = {i.filename: z.read(i.filename) for i in infos}
    return infos, data


def frame_names(data):
    return sorted(n for n in data if n.lower().endswith(".tga"))


def body_box(data, tga, density):
    """(left, top, right, bottom) of the frame's opaque pixels, classic px from the unit centre."""
    meta = json.loads(data[tga[:-4] + ".meta"])
    w, h = meta["size"]
    x0, y0 = meta["crop"][0], meta["crop"][1]
    b = Image.open(io.BytesIO(data[tga])).getchannel("A").point(lambda v: 255 if v >= OPAQUE else 0).getbbox()
    if not b:
        return None
    return ((x0 + b[0] - w / 2) / density, (y0 + b[1] - h / 2) / density,
            (x0 + b[2] - w / 2) / density, (y0 + b[3] - h / 2) / density)


def hull_offset(data, hull_frames):
    """Median vertical centre of the hull's opaque pixels over its frames, classic px (+ = below)."""
    names = frame_names(data)[:hull_frames]
    centres = [(b[1] + b[3]) / 2 for b in (body_box(data, n, UNIT_DENSITY) for n in names) if b]
    return statistics.median(centres)


def selection_box(data, hull_frames, per_facing, turret, seats):
    """Width and height for _art_boxes: median art width; twice the median reach from centre."""
    names = frame_names(data)
    widths, tops, bottoms = [], [], []
    for f in range(32):
        boxes = [body_box(data, names[f * per_facing], UNIT_DENSITY)]
        if turret is not None:
            t = body_box(data, names[turret + f], UNIT_DENSITY)
            if t:
                sx, sy = seats[f]
                boxes.append((t[0] + sx, t[1] + sy, t[2] + sx, t[3] + sy))
        boxes = [b for b in boxes if b]
        widths.append(max(b[2] for b in boxes) - min(b[0] for b in boxes))
        tops.append(min(b[1] for b in boxes))
        bottoms.append(max(b[3] for b in boxes))
    reach = max(-statistics.median(tops), statistics.median(bottoms))
    return round(statistics.median(widths)), round(2 * reach)


def trim_rows(data, tga, crop, top, bottom):
    """Drop fully transparent rows from a frame's top and bottom; returns the new crop."""
    im = Image.open(io.BytesIO(data[tga]))
    alpha = im.getchannel("A")
    rows = [alpha.crop((0, y, im.width, y + 1)).getbbox() is not None for y in range(im.height)]
    if any(rows[:top]) or any(rows[im.height - bottom:]):
        raise SystemExit(f"{tga}: not enough empty rows to move it; grow the canvas")
    buf = io.BytesIO()
    im.crop((0, top, im.width, im.height - bottom)).save(buf, format="TGA")
    data[tga] = buf.getvalue()
    return [crop[0], crop[1] + top, crop[2], crop[3] - bottom]


def shift_zip(path, dy):
    """Move every frame in the ZIP down by dy canvas px, keeping entry order and compression.
    A frame padded out to its canvas edge loses the empty rows it needs to move."""
    infos, data = read_zip(path)
    for name in list(data):
        if not name.lower().endswith(".meta"):
            continue
        meta = json.loads(data[name])
        crop = meta["crop"]
        height = meta["size"][1]
        over_top, over_bottom = max(0, -(crop[1] + dy)), max(0, crop[3] + dy - height)
        if over_top or over_bottom:
            crop = trim_rows(data, name[:-5] + ".tga", crop, over_top, over_bottom)
        meta["crop"] = [crop[0], crop[1] + dy, crop[2], crop[3] + dy]
        data[name] = json.dumps(meta).encode()
    tmp = path + ".tmp"
    with zipfile.ZipFile(tmp, "w") as out:
        for info in infos:
            out.writestr(info, data[info.filename], compress_type=info.compress_type)
    os.replace(tmp, path)


def write_header(drops):
    rows = "\n".join(f"    {{UNIT_{n}, {round(drops[n] / UNIT_DENSITY * LEPTONS_PER_CLASSIC_PX)}}},"
                     for n in sorted(drops))
    with open(HEADER, "w") as f:
        f.write(f"""
// GENERATED by scripts/unit_centring.py -- do not hand-edit.
// How far each unit's art was moved down to centre its hull on the unit, in leptons south.
// Fire_Coord adds it to the fire points the packers measured on the art before the move.

static const struct
{{
    UnitType Type;
    short Drop;
}} _unit_art_drop[] = {{
{rows}
}};
""")


def audit():
    """Hull offset of every packed TS, RA2 and C&C3 unit (the TD units are EA's own art).
    Infantry ship at EA's density and stand on EA's feet line (about +1.3 classic px), and
    walkers and aircraft follow their own rules (docs/launcher-render-contracts.md), so only
    vehicles read directly against the hull rule."""
    import glob
    roots = glob.glob(os.path.join(REPO, "asset-packs", "*", "Data", "ART", "TEXTURES", "SRGB", "RED_ALERT", "UNITS"))
    roots.append(os.path.join(REPO, "resources", "remaster_mods", "Vanilla_RA", "Data", "ART", "TEXTURES", "SRGB",
                              "RED_ALERT", "UNITS"))
    for root in roots:
        for path in sorted(glob.glob(os.path.join(root, "*.ZIP"))):
            name = os.path.basename(path)[:-4]
            if not name.startswith(VOXEL_PREFIXES):
                continue
            _, data = read_zip(path)
            if len(frame_names(data)) < 32:
                continue
            offset = hull_offset(data, 32)
            size = json.loads(data[frame_names(data)[0][:-4] + ".meta"])["size"][1]
            if name in UNITS:
                mark = "centred by this script"
            elif size == 208:
                mark = "infantry: EA feet line, not the hull rule"
            elif name in WALKERS or name in AIRCRAFT:
                mark = "walker" if name in WALKERS else "aircraft"
                mark += ": own rule, not checked"
            else:
                mark = "within EA's spread" if abs(offset) < EA_SPREAD else "OFF CENTRE: add to UNITS"
            print(f"{name:14} canvas {size:4} hull {offset:+5.1f}  {mark}")


def main():
    if "--audit" in sys.argv[1:]:
        audit()
        return
    check = "--check" in sys.argv[1:]
    drops = json.load(open(DROPS_JSON)) if os.path.exists(DROPS_JSON) else {}
    off = False
    for name, (hull_frames, per_facing, turret, seat_key, partners) in UNITS.items():
        path = asset_packs.art_zip(name, "UNITS")
        _, data = read_zip(path)
        offset = hull_offset(data, hull_frames)
        dy = -round(offset * UNIT_DENSITY)
        status = "centred" if abs(offset) < TOLERANCE else f"off by {offset:+.1f}, move {dy:+d} canvas px"
        print(f"{name:10} hull {offset:+5.1f} classic px: {status}")
        if abs(offset) < TOLERANCE:
            continue
        off = True
        if check:
            continue
        shift_zip(path, dy)
        for partner, kind, density in partners:
            shift_zip(asset_packs.art_zip(partner, kind), round(dy / UNIT_DENSITY * density))
        drops[name] = dy
    if check:
        sys.exit(1 if off else 0)
    with open(DROPS_JSON, "w") as f:
        json.dump(dict(sorted(drops.items())), f, indent=2)
        f.write("\n")
    write_header(drops)
    print("\nSelection boxes from the centred art (classic px, for _art_boxes in udata.cpp):")
    for name, (hull_frames, per_facing, turret, seat_key, _) in UNITS.items():
        _, data = read_zip(asset_packs.art_zip(name, "UNITS"))
        w, h = selection_box(data, hull_frames, per_facing, turret, seats_for(seat_key))
        print(f"        {{UNIT_{name}, {w}, {h}}},")


if __name__ == "__main__":
    main()
