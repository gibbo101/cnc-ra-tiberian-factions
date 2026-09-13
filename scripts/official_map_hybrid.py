#!/usr/bin/env python3
"""Build Tiberium/Ore hybrid versions of the official RA skirmish maps.

Each official map is read straight from the game's MAIN.MIX -> general.mix. Every ore mine
named in HYBRIDS becomes a TD blossom tree (Neutral STRUCT_TDBLOSSOM), and the ore field it
feeds (the connected Ore/Gem cells within reach of the mine) becomes Tiberium (OVERLAY_TIB01).
Everything else in the file is carried over byte for byte, except [Digest], which is dropped so
the engine skips digest validation on the edited file. The map is written to the mod's CCDATA
folder under the official file name, where it shadows the stock map.

The map's lobby thumbnail is repainted to match. The thumbnail is a DDS in TEXTURES_SRGB.MEG
named after the map's preview entry in CONFIG.MEG; the Ore speckle inside the converted fields
turns Tiberium green, and the result is written as a loose DDS under the mod's
Data/ART/TEXTURES/SRGB, which the launcher loads over the stock one.

Usage: official_map_hybrid.py [--game <CnCRemastered dir>] [--mod <mod dir>] [map ...]
       official_map_hybrid.py --survey <map> ...
"""
import argparse
import io
import os
import re
import struct
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dds_dxt5  # noqa: E402
import td_map_to_ra as codec  # noqa: E402
from mix_tools import ww_crc  # noqa: E402

MAIN_MIX = "Data/CNCDATA/RED_ALERT/AFTERMATH/MAIN.MIX"
CONFIG_MEG = "Data/CONFIG.MEG"
TEXTURES_MEG = "Data/TEXTURES_SRGB.MEG"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MOD = os.path.join(REPO, "resources/remaster_mods/Vanilla_RA")
DEFAULT_GAME = os.path.expanduser("~/.steam/steam/steamapps/common/CnCRemastered")

OVERLAY_NONE = 0xFF
ORE = range(5, 13)  # OVERLAY_GOLD1..OVERLAY_GEMS4 (redalert/defines.h)
OVERLAY_TIB01 = codec.OVERLAY_TIB01
MINE_REACH = 2  # an ore cell this close to a mine (Chebyshev) seeds that mine's field

TIB_PREVIEW_HUE = np.array([77.3, 92.4, 41.8])  # Tiberium speckle in EA's TD lobby thumbnails
PREVIEW_REACH_PX = 11  # ore sprites overhang their cell; the repaint mask grows by this window

# map file -> ore-mine cells whose field turns to Tiberium, the mine itself to a blossom tree.
HYBRIDS = {
    # Keep off the Grass: the mirrored East and South-West flank fields. The home patches, the
    # centre gems and the lone mine at (82,61) stay Ore.
    "scm05ea.ini": [5714, 9901],
}


def _mix_index(f, base):
    f.seek(base)
    first, flags = struct.unpack("<HH", f.read(4))
    pos = base
    if first == 0:
        if flags & 0x02:
            raise SystemExit("encrypted MIX header is not supported")
        pos += 4
    f.seek(pos)
    count, _datasize = struct.unpack("<HI", f.read(6))
    entries = {}
    for _ in range(count):
        crc, off, size = struct.unpack("<iII", f.read(12))
        entries[crc] = (off, size)
    return entries, pos + 6 + count * 12


def _mix_locate(f, base, name):
    entries, data = _mix_index(f, base)
    off, size = entries[ww_crc(name.upper())]
    return data + off, size


def read_official_map(game_dir, name):
    with open(os.path.join(game_dir, MAIN_MIX), "rb") as f:
        general, _ = _mix_locate(f, 0, "general.mix")
        off, size = _mix_locate(f, general, name)
        f.seek(off)
        return f.read(size)


def read_meg_member(path, name):
    """The member whose file name is `name` (case-insensitive), read without loading the MEG."""
    want = name.upper()
    with open(path, "rb") as f:
        magic, = struct.unpack("<I", f.read(4))
        f.seek(12 if magic in (0xFFFFFFFF, 0x8FFFFFFF) else 4)
        nfiles, nstrings, strsize = struct.unpack("<III", f.read(12))
        table = f.read(strsize + nfiles * 20)
        strings, p = [], 0
        for _ in range(nstrings):
            n, = struct.unpack_from("<H", table, p)
            strings.append(table[p + 2:p + 2 + n].decode("latin-1"))
            p += 2 + n
        p = strsize
        for _ in range(nfiles):
            _flags, _crc, _index, size, offset, ni = struct.unpack_from("<HIiIIH", table, p)
            p += 20
            if strings[ni].upper().replace("/", "\\").split("\\")[-1] == want:
                f.seek(offset)
                return f.read(size)
    raise SystemExit(f"{name} not found in {path}")


def _split_sections(text):
    """[(header_line or None, [body lines])] in file order."""
    out = [(None, [])]
    for line in text.split("\r\n"):
        if re.match(r"^\[[^\]]+\]\s*$", line):
            out.append((line, []))
        else:
            out[-1][1].append(line)
    return out


def _name(header):
    return header.strip()[1:-1].lower() if header else None


def _sections(src):
    return {_name(h): body for h, body in _split_sections(src.decode("latin-1")) if h}


def _overlay(by_name):
    return bytearray(codec.lcw_block_decompress(codec.uublock_decode(
        [l.split("=", 1)[1] for l in by_name["overlaypack"] if "=" in l])))


def _grow(overlay, seeds):
    field, stack = set(seeds), list(seeds)
    while stack:
        c = stack.pop()
        for d in (-129, -128, -127, -1, 1, 127, 128, 129):
            n = c + d
            if 0 <= n < len(overlay) and n not in field and overlay[n] in ORE \
                    and abs(n % 128 - c % 128) <= 1:
                field.add(n)
                stack.append(n)
    return field


def _field_cells(overlay, mine):
    mx, my = mine % 128, mine // 128
    return _grow(overlay, [c for c in range(len(overlay)) if overlay[c] in ORE
                           and max(abs(c % 128 - mx), abs(c // 128 - my)) <= MINE_REACH])


def _mines(by_name):
    return sorted(int(l.split("=", 1)[0]) for l in by_name.get("terrain", [])
                  if "=" in l and l.split("=", 1)[1].split(",")[0].upper() == "MINE")


def _starts(by_name):
    wps = dict(l.split("=", 1) for l in by_name.get("waypoints", []) if "=" in l)
    return [int(wps[str(i)]) for i in range(8) if str(i) in wps]


def make_hybrid(src, mines):
    """(hybrid map bytes, set of cells turned to Tiberium)."""
    sections = _split_sections(src.decode("latin-1"))
    by_name = {_name(h): body for h, body in sections if h}
    overlay = _overlay(by_name)
    missing = set(mines) - set(_mines(by_name))
    if missing:
        raise SystemExit(f"no ore mine at cell(s) {sorted(missing)}")

    converted = set()
    for mine in mines:
        converted |= _field_cells(overlay, mine)
    for c in converted:
        overlay[c] = OVERLAY_TIB01
    for mine in mines:
        overlay[mine] = OVERLAY_NONE

    packed = [f"{k}={v}" for k, v in codec.uublock_encode(codec.lcw_block_compress(bytes(overlay)))]
    existing = [l for l in by_name.get("structures", []) if "=" in l]
    blossoms = [f"{len(existing) + i}=Neutral,TDBLOSSOM,256,{m},0,None" for i, m in enumerate(mines)]

    out = []
    for header, body in sections:
        name = _name(header)
        if name == "digest":
            continue
        if name == "overlaypack":
            body = packed + [l for l in body if not l.strip()]
        elif name == "terrain":
            body = [l for l in body if not ("=" in l and int(l.split("=", 1)[0]) in mines)]
        elif name == "structures":
            body = existing + blossoms + [l for l in body if not l.strip()]
        if header:
            out.append(header)
        out.extend(body)
        if name == "terrain" and "structures" not in by_name:
            out.extend(["[STRUCTURES]"] + blossoms + [""])
    while len(out) > 1 and out[-1] == "" and out[-2] == "":
        out.pop()
    result = "\r\n".join(out).encode("latin-1")

    assert _overlay(_sections(result)) == overlay, "OverlayPack round trip mismatch"
    return result, converted


def preview_key(game_dir, src):
    """(texture key, (x, y, w, h)) of the map's lobby preview, matched on bounds and starts."""
    by_name = _sections(src)
    m = dict(l.split("=", 1) for l in by_name["map"] if "=" in l)
    bounds = tuple(int(m[k]) for k in ("X", "Y", "Width", "Height"))
    starts = _starts(by_name)
    with open(os.path.join(game_dir, CONFIG_MEG), "rb") as f:
        config = f.read()
    keys = [e[0].decode() for e in re.findall(
        rb'<INIData Name="([A-Z0-9_]+)">\s*<MapTileX>(\d+)</MapTileX>\s*<MapTileY>(\d+)</MapTileY>'
        rb'\s*<MapTileWidth>(\d+)</MapTileWidth>\s*<MapTileHeight>(\d+)</MapTileHeight>'
        rb'.*?<Waypoints>(.*?)</Waypoints>', config, re.S)
        if tuple(int(v) for v in e[1:5]) == bounds
        and [int(v) for v in re.findall(rb"<Entry>(\d+)</Entry>", e[5])][:len(starts)] == starts]
    if len(keys) != 1:
        raise SystemExit(f"expected one preview entry for bounds {bounds} starts {starts}, got {keys}")
    return keys[0], bounds


def repaint_preview(stock_dds, bounds, cells):
    """The stock thumbnail with the Ore speckle over `cells` recoloured as Tiberium."""
    img = Image.open(io.BytesIO(stock_dds)).convert("RGB")
    a = np.asarray(img).astype(float)
    x0, y0, w, h = bounds
    sx, sy = img.width / w, img.height / h
    mask = np.zeros(a.shape[:2], np.uint8)
    for c in cells:
        x, y = c % 128 - x0, c // 128 - y0
        mask[int(y * sy):int((y + 1) * sy), int(x * sx):int((x + 1) * sx)] = 255
    mask = np.asarray(Image.fromarray(mask).filter(ImageFilter.MaxFilter(PREVIEW_REACH_PX))) > 0

    grass = np.median(a[~mask].reshape(-1, 3), 0)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    speckle = mask & (r >= g * 0.85) & (r - b > 40) & (r > 90)
    if not speckle.any():
        raise SystemExit("no Ore speckle found under the converted fields")
    ore = a[speckle].mean(0)
    tib = TIB_PREVIEW_HUE * (ore.mean() / TIB_PREVIEW_HUE.mean())
    towards_ore = ore - grass
    weight = np.clip(((a - grass) @ towards_ore) / (towards_ore @ towards_ore), 0, 1.3) * mask
    return Image.fromarray(np.clip(a + weight[..., None] * (tib - ore), 0, 255).astype(np.uint8))


def preview_dds(stock_dds, img):
    """`img` encoded with the stock DDS's header, format and mip count."""
    if stock_dds[84:88] != b"DXT5":
        raise SystemExit(f"stock preview is {stock_dds[84:88]!r}, expected DXT5")
    mips = max(1, struct.unpack_from("<I", stock_dds, 28)[0])
    out = stock_dds[:128] + dds_dxt5.encode_with_mips(img, mips)
    assert len(out) == len(stock_dds), "encoded preview size differs from stock"
    return out


def survey(src):
    """Print every Ore/Gem field with the mines in reach of it, then the mines and start waypoints."""
    by_name = _sections(src)
    overlay = _overlay(by_name)
    mines = _mines(by_name)
    fields = {m: _field_cells(overlay, m) for m in mines}
    seen = set()
    for c in range(len(overlay)):
        if overlay[c] not in ORE or c in seen:
            continue
        field = _grow(overlay, [c])
        seen |= field
        xs, ys = [q % 128 for q in field], [q // 128 for q in field]
        gems = sum(1 for q in field if overlay[q] >= 9)
        fed = [f"{m} ({m % 128},{m // 128})" for m in mines if fields[m] & field]
        print(f"field {len(field):4d} cells  x{min(xs)}-{max(xs)} y{min(ys)}-{max(ys)}  "
              f"ore {len(field) - gems} gems {gems}  mines: {', '.join(fed) or '-'}")
    for m in mines:
        print(f"mine {m} ({m % 128},{m // 128})" + ("" if fields[m] else "  (no field in reach)"))
    for i, s in enumerate(_starts(by_name)):
        print(f"start {i}: {s} ({s % 128},{s // 128})")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--game", default=DEFAULT_GAME)
    ap.add_argument("--mod", default=DEFAULT_MOD)
    ap.add_argument("--survey", action="store_true", help="list fields, mines and starts; write nothing")
    ap.add_argument("maps", nargs="*")
    args = ap.parse_args()
    if args.survey:
        for name in args.maps:
            print(f"== {name}")
            survey(read_official_map(args.game, name))
        return
    for name in args.maps or sorted(HYBRIDS):
        src = read_official_map(args.game, name)
        data, cells = make_hybrid(src, HYBRIDS[name])
        map_path = os.path.join(args.mod, "CCDATA", name)
        with open(map_path, "wb") as f:
            f.write(data)

        key, bounds = preview_key(args.game, src)
        stock = read_meg_member(os.path.join(args.game, TEXTURES_MEG), key + ".DDS")
        dds_path = os.path.join(args.mod, "Data/ART/TEXTURES/SRGB", key + ".DDS")
        os.makedirs(os.path.dirname(dds_path), exist_ok=True)
        with open(dds_path, "wb") as f:
            f.write(preview_dds(stock, repaint_preview(stock, bounds, cells)))
        print(f"{name}: {len(cells)} Ore cells -> Tiberium, {len(HYBRIDS[name])} mines -> "
              f"blossom trees\n  map     {map_path}\n  preview {dds_path}")


if __name__ == "__main__":
    main()
