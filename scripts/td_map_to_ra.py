#!/usr/bin/env python3
"""
TD -> RA skirmish-map transcoder (Tiberian Factions mod).

Converts a classic Tiberian Dawn map (.INI + .BIN) into a Red Alert .mpr that
our modded DLL can load, remapping terrain templates by NAME (the editor source
proved ~90% of TD temperate templates have a same-named RA template) and
converting TD tiberium (TI1-TI12) into our harvestable TIB01 overlay.

Formats (all reverse-engineered from our own DLL + the shipped Mobius editor C#):
- TD .BIN  : 64x64 cells, 2 bytes/cell = (template-id u8, icon u8). 0xFF = clear.
- TD .INI  : [MAP] theater+bounds, [Waypoints], [TERRAIN], [OVERLAY] (cell=name).
- RA .mpr  : INIFormat3 INI. [MapPack] = base64(UUBlock) of LCW-block-framed
             (16384 x TType u16 LE) ++ (16384 x TIcon u8). [OverlayPack] = same
             framing over 16384 signed-char overlay-per-cell (0xFF none, 13=TIB01).
             UUBlock = base64 split into 70-char lines keyed "1=","2=",...  CRLF.
             LCW block frame = [CompCount u16 LE][UncompCount u16 LE][comp bytes],
             blocks of <=8192 uncompressed bytes (LCWPipe default).

Template tables are parsed live from the editor source so we never hand-maintain
600 entries:
  <install>/SOURCECODE/CnCTDRAMapEditor/{TiberianDawn,RedAlert}/TemplateTypes.cs

Usage:
  td_map_to_ra.py inspect-ra  <ra.ini|ra.mpr>      # decode+stats (codec self-check)
  td_map_to_ra.py convert <td.ini> <out.mpr> [--name "Display Name"]
"""
import sys, os, re, struct, base64, argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shptools import lcw_compress, lcw_decompress

# ----- map geometry -----
TD_W = 64
RA_W = 128
RA_CELLS = RA_W * RA_W            # 16384
MAPPACK_RAW = RA_CELLS * 2 + RA_CELLS   # 49152 (TType u16 + TIcon u8)
BLOCK = 8192                      # LCWPipe default uncompressed block size

RA_TEMPLATE_NONE = 0xFFFF         # "no template" = engine renders theater clear
OVERLAY_NONE = 0xFF
OVERLAY_TIB01 = 13                # must match redalert/defines.h OVERLAY_TIB01

# TD overlays RA understands natively, under the SAME INI names. Ids match OUR
# DLL's OverlayType enum (defines.h) -- TIB01 at 13 shifts V12+ up by one vs
# vanilla RA. V12-V18 are decorative farm fields. WALLS (SBAG/CYCL/BRIK/BARB/
# WOOD) are intentionally NOT carried: in SP source maps they are the campaign
# bases' perimeter fences, which read as abandoned fortifications in skirmish
# (Luke 2026-06-09). Crates and TD's ROAD overlay are dropped too.
OVERLAY_CARRY = {"V12": 14, "V13": 15, "V14": 16, "V15": 17, "V16": 18,
                 "V17": 19, "V18": 20}

EDITOR_SRC = os.path.expanduser(
    "~/.steam/steam/steamapps/common/CnCRemastered/SOURCECODE/CnCTDRAMapEditor")

# ===================================================================== codec
def lcw_block_decompress(data):
    """Decode an LCW-block-framed stream into the full uncompressed bytes."""
    out = bytearray()
    pos = 0
    while pos + 4 <= len(data):
        comp_count, uncomp_count = struct.unpack_from("<HH", data, pos)
        pos += 4
        if comp_count == 0:
            break
        chunk = data[pos:pos + comp_count]
        pos += comp_count
        out += lcw_decompress(chunk, uncomp_count)
        if len(chunk) < comp_count:
            break
    return bytes(out)

def lcw_block_compress(raw):
    """Encode raw bytes into the LCW-block frame (<=8192 uncompressed/block)."""
    out = bytearray()
    for i in range(0, len(raw), BLOCK):
        block = raw[i:i + BLOCK]
        comp = lcw_compress(block)
        out += struct.pack("<HH", len(comp), len(block))
        out += comp
    return bytes(out)

def uublock_decode(lines):
    """lines: list of base64 fragment strings (values of the numbered keys)."""
    return base64.b64decode("".join(lines))

def uublock_encode(data):
    """Return list of (key, value) pairs: base64 split into 70-char lines."""
    b64 = base64.b64encode(data).decode("ascii")
    out = []
    for i in range(0, len(b64), 70):
        out.append((str(i // 70 + 1), b64[i:i + 70]))
    return out

# ===================================================================== INI io
def read_ini(path):
    """Minimal INI -> {section: [(key,value), ...]} preserving order+dupes."""
    secs, cur = {}, None
    with open(path, "r", encoding="latin-1") as f:
        for line in f:
            line = line.rstrip("\r\n")
            s = line.strip()
            if not s or s.startswith(";"):
                continue
            if s.startswith("[") and s.endswith("]"):
                cur = s[1:-1]
                secs.setdefault(cur, [])
            elif cur is not None and "=" in line:
                k, v = line.split("=", 1)
                secs[cur].append((k.strip(), v.strip()))
    return secs

def section_pack(secs, name):
    """Concatenate numbered UUBlock lines of a section into raw bytes."""
    if name not in secs:
        return b""
    return lcw_block_decompress(uublock_decode([v for _, v in secs[name]]))

def get_sec(secs, name):
    """Case-insensitive section lookup: SP sources use [TERRAIN]/[OVERLAY],
    the community MP maps [Terrain]/[Overlay]."""
    for k, v in secs.items():
        if k.lower() == name.lower():
            return v
    return []

# ===================================================================== tables
def parse_templates(cs_path):
    """Parse 'new TemplateType(id, "name", w, h, ...)' -> list of (id,name,w,h)."""
    txt = open(cs_path, encoding="latin-1").read()
    out = []
    for m in re.finditer(r'new TemplateType\(\s*(\d+)\s*,\s*"([^"]+)"\s*,\s*(\d+)\s*,\s*(\d+)', txt):
        out.append((int(m.group(1)), m.group(2).lower(), int(m.group(3)), int(m.group(4))))
    return out

def build_template_map():
    """TD template id -> RA template id (by name, with the shore/pavement renames).
    Returns (tmap, missing, td_by_id, ra_by_id) where *_by_id = {id:(name,w,h)}."""
    td = parse_templates(os.path.join(EDITOR_SRC, "TiberianDawn", "TemplateTypes.cs"))
    ra = parse_templates(os.path.join(EDITOR_SRC, "RedAlert", "TemplateTypes.cs"))
    ra_by_name = {name: tid for tid, name, w, h in ra}
    td_by_id = {tid: (name, w, h) for tid, name, w, h in td}
    ra_by_id = {tid: (name, w, h) for tid, name, w, h in ra}
    # Known renames TD -> RA (shores sh1..sh9 -> sh01..sh09).
    def ra_lookup(name):
        if name in ra_by_name:
            return ra_by_name[name]
        m = re.fullmatch(r"sh([1-9])", name)
        if m and ("sh0" + m.group(1)) in ra_by_name:
            return ra_by_name["sh0" + m.group(1)]
        return None
    tmap, missing = {}, []
    for tid, name, w, h in td:
        rid = ra_lookup(name)
        if rid is None:
            missing.append(name)
        else:
            tmap[tid] = rid
    return tmap, sorted(set(missing)), td_by_id, ra_by_id

# ===================================================================== convert
def td_cell(x, y):
    return y * TD_W + x

def ra_cell(x, y):
    return y * RA_W + x

def convert(td_ini_path, out_path, display_name):
    base = os.path.splitext(td_ini_path)[0]
    bin_path = base + ".BIN"
    if not os.path.exists(bin_path):
        bin_path = base + ".bin"
    secs = read_ini(td_ini_path)
    bindata = open(bin_path, "rb").read()
    assert len(bindata) == TD_W * TD_W * 2, f"unexpected .bin size {len(bindata)}"

    mp = {k.lower(): v for k, v in secs.get("MAP", secs.get("Map", []))}
    theater = mp.get("theater", "temperate").lower()
    if theater != "temperate":
        print(f"WARNING: source theater is '{theater}'; only temperate is supported for now.")
    tdX, tdY = int(mp.get("x", 0)), int(mp.get("y", 0))
    tdWi, tdHe = int(mp.get("width", TD_W)), int(mp.get("height", TD_W))

    # Centre the TD map inside the 128x128 RA map.
    offx = (RA_W - TD_W) // 2
    offy = (RA_W - TD_W) // 2

    tmap, missing, td_by_id, ra_by_id = build_template_map()

    # Ported TD tiles (build_td_tiles.py): TD template NAME -> new RA template id.
    # These map 1:1 with TD's exact size+art, so icons align perfectly -- they take
    # priority over the name+size auto-match and skip the size-gate entirely.
    ported = {}
    mapper_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "td_ra_tile_map.json")
    if os.path.exists(mapper_path):
        import json as _json
        for tdname, info in _json.load(open(mapper_path)).items():
            ported[tdname] = info["ra_id"]

    # ---- terrain (MapPack) ----
    # We only trust a name-match when TD and RA agree on the template SIZE (WxH) and
    # the per-cell icon is in range. RA reuses some TD names for differently-sized /
    # re-laid-out tiles (shores sh1/sh2/sh8/sh10/sh18, bridges) -> a blind copy renders
    # white "missing" tiles (icon out-of-range) or random coast tiles on land. Those
    # cells are rendered CLEAR instead, which looks clean (at the cost of dropping the
    # mismatched shore/bridge pieces -- to be remapped properly later).
    ttype = [RA_TEMPLATE_NONE] * RA_CELLS
    ticon = [0] * RA_CELLS
    placed = 0
    import collections
    diag = {}  # tid -> [count, maxicon]
    for y in range(TD_W):
        for x in range(TD_W):
            t = bindata[td_cell(x, y) * 2]
            ic = bindata[td_cell(x, y) * 2 + 1]
            if t == 0xFF:
                continue
            d = diag.setdefault(t, [0, 0]); d[0] += 1; d[1] = max(d[1], ic)
            tdname = td_by_id[t][0]
            rc = ra_cell(x + offx, y + offy)
            # 1) Ported TD tile -> its own RA template (exact size+art, icons align).
            if tdname in ported:
                ttype[rc] = ported[tdname]
                ticon[rc] = ic
                placed += 1
                continue
            # 2) Otherwise the name+size auto-match, gated on matching size/icon range.
            rid = tmap.get(t)
            if rid is None:
                continue
            tw, th = td_by_id[t][1], td_by_id[t][2]
            rw, rh = ra_by_id[rid][1], ra_by_id[rid][2]
            if (tw, th) != (rw, rh) or ic >= rw * rh:
                continue  # size/icon mismatch -> render clear
            ttype[rc] = rid
            ticon[rc] = ic
            placed += 1

    # ---- per-template diagnostic log ----
    print("  template report (TD->RA), problem rows flagged:")
    dropped_cells = 0
    for t, (cnt, mx) in sorted(diag.items(), key=lambda kv: -kv[1][0]):
        nm, tw, th = td_by_id.get(t, ("?", 0, 0))
        if nm in ported:
            print(f"    {nm:<9} {tw}x{th} x{cnt:<4} -> ported template (id {ported[nm]})")
            continue
        rid = tmap.get(t)
        if rid is None:
            print(f"    {nm:<9} {tw}x{th} x{cnt:<4} -> NO RA MATCH (clear)")
            dropped_cells += cnt
            continue
        rn, rw, rh = ra_by_id[rid]
        bad = (tw, th) != (rw, rh) or mx >= rw * rh
        if bad:
            why = "ICON-OOR" if mx >= rw * rh else "SIZE-DIFF"
            print(f"    {nm:<9} {tw}x{th} -> {rn}({rw}x{rh}) x{cnt:<4} maxicon={mx}  DROPPED [{why}]")
            dropped_cells += cnt
    unmapped = dropped_cells

    # ---- vanilla-safety split: TD-ported template ids (401+) would crash a
    # VANILLA DLL reading this map (heap index out of range) -- and self-
    # installed Local_Custom_Maps persist after the mod is disabled. So the
    # shipped [MapPack] carries only vanilla-known ids (TD cells -> clear),
    # and the real TD cells ride in [TFTDTiles] (same MapPack encoding; cells
    # with TType 0xFFFF = no override). Vanilla ignores the unknown section
    # (plain shores); our DLL overlays it after MapPack (display.cpp). ----
    ported_ids = set(ported.values())
    safe_tt, safe_ic = list(ttype), list(ticon)
    td_tt, td_ic = [RA_TEMPLATE_NONE] * RA_CELLS, [0] * RA_CELLS
    td_cells = 0
    for c in range(RA_CELLS):
        if ttype[c] in ported_ids:
            td_tt[c], td_ic[c] = ttype[c], ticon[c]
            safe_tt[c], safe_ic[c] = RA_TEMPLATE_NONE, 0
            td_cells += 1

    mappack_raw = b"".join(struct.pack("<H", t) for t in safe_tt) + bytes(safe_ic)
    assert len(mappack_raw) == MAPPACK_RAW
    tdtiles_raw = None
    if td_cells:
        tdtiles_raw = b"".join(struct.pack("<H", t) for t in td_tt) + bytes(td_ic)
        print(f"  side-channel [TFTDTiles]: {td_cells} TD-tile cells (MapPack kept vanilla-safe)")

    # ---- overlay (OverlayPack): tiberium TI1..TI12 -> TIB01 (density 0..11),
    # walls + farm fields carried through by name (OVERLAY_CARRY) ----
    overlay = bytearray([OVERLAY_NONE]) * RA_CELLS
    tib = 0
    carried = {}
    for k, v in get_sec(secs, "Overlay"):
        try:
            cell = int(k)
        except ValueError:
            continue
        name = v.strip().upper()
        x, y = cell % TD_W, cell // TD_W
        rc = ra_cell(x + offx, y + offy)
        m = re.fullmatch(r"TI(\d+)", name)
        if m:
            overlay[rc] = OVERLAY_TIB01
            tib += 1
        elif name in OVERLAY_CARRY:
            overlay[rc] = OVERLAY_CARRY[name]
            carried[name] = carried.get(name, 0) + 1
    if carried:
        print(f"  carried overlays: {carried}")

    # ---- waypoints (start positions) ----
    # MP sources carry real start waypoints (0..7); SP missions have none
    # usable, so only then are starts synthesized around the playable ring.
    waypts = []
    for k, v in get_sec(secs, "Waypoints"):
        try:
            n = int(k); cell = int(v)
        except ValueError:
            continue
        if cell < 0 or not (0 <= n <= 7):
            continue
        x, y = cell % TD_W, cell // TD_W
        waypts.append((n, ra_cell(x + offx, y + offy)))

    # ---- terrain objects (trees); TD blossom trees (split2/split3) become our
    # neutral STRUCT_TDBLOSSOM building (terrain objects can't take custom HD
    # art on our stack; the building can, and carries the spore-shed/seeding AI)
    terrain = []
    structures = []
    for k, v in get_sec(secs, "Terrain"):
        try:
            cell = int(k)
        except ValueError:
            continue
        x, y = cell % TD_W, cell // TD_W
        rc = ra_cell(x + offx, y + offy)
        name = v.strip().split(",")[0].upper()
        if name in ("SPLIT2", "SPLIT3"):
            structures.append(f"Neutral,TDBLOSSOM,256,{rc},0,None")
        else:
            terrain.append((rc, f"{name},None"))

    mapx, mapy = offx + tdX, offy + tdY
    # Waypoints 0-7 are MP start positions only on real multiplayer sources
    # (which carry [Multi1..] house sections); on SP missions they are
    # trigger anchors and must not become starts.
    is_mp_source = bool(get_sec(secs, "Multi1"))
    if is_mp_source and len(waypts) >= 2:
        starts = [c for _, c in sorted(waypts)]
        src = "source"
    else:
        starts = synth_starts(mapx, mapy, tdWi, tdHe)
        src = "synthesized"
    # CnCNet-tooled sources carry a rendered preview image ([CnCNetPreview],
    # base64 PNG) -- bake it into the triplet TGA so the lobby shows the real
    # TD render instead of the synthetic block map.
    preview_png = None
    psec = get_sec(secs, "CnCNetPreview")
    if psec:
        try:
            preview_png = base64.b64decode("".join(v for _, v in psec))
        except Exception:
            preview_png = None
    write_triplet(out_path, display_name, theater, mapx, mapy, tdWi, tdHe,
                  mappack_raw, bytes(overlay), starts, terrain, structures, ttype,
                  tdtiles_raw, preview_png)
    print(f"  placed {placed} terrain cells ({unmapped} unmapped), {tib} tiberium cells, "
          f"{len(starts)} start positions ({src}), {len(terrain)} terrain objects, "
          f"{len(structures)} blossom trees")
    print(f"  -> {out_path} (+ .json + .tga)")

HOUSES = ["Spain", "Greece", "USSR", "England", "Ukraine", "Germany", "France", "Turkey",
          "GoodGuy", "BadGuy", "Neutral", "Special",
          "Multi1", "Multi2", "Multi3", "Multi4", "Multi5", "Multi6", "Multi7", "Multi8"]
HOUSE_BLOCK = [("MaxBuilding", 150), ("MaxUnit", 150), ("MaxInfantry", 150),
               ("MaxVessel", 150), ("TechLevel", 99), ("IQ", 5),
               ("PlayerControl", "no"), ("Edge", "North"), ("Credits", 0)]

def synth_starts(mapx, mapy, w, h):
    """8 spread start cells around an inner ring of the playable bounds.
    SP-mission sources have no clean MP starts, so we synthesize them."""
    import math
    cx, cy = mapx + w / 2.0, mapy + h / 2.0
    rx, ry = max(2, w // 2 - 3), max(2, h // 2 - 3)
    pts = []
    for i in range(8):
        a = math.pi / 2 - i * (2 * math.pi / 8)  # start north, go clockwise
        x = int(round(cx + rx * math.cos(a)))
        y = int(round(cy - ry * math.sin(a)))
        x = min(max(x, 1), RA_W - 2)
        y = min(max(y, 1), RA_W - 2)
        pts.append(ra_cell(x, y))
    return pts

def write_triplet(path, name, theater, mapx, mapy, mapw, maph,
                  mappack_raw, overlay_raw, starts, terrain, structures, ttype,
                  tdtiles_raw=None, preview_png=None):
    L = []
    def sec(title, kvs):
        L.append(f"[{title}]")
        L.extend(f"{k}={v}" for k, v in kvs)
        L.append("")
    sec("Basic", [("Name", name), ("NewINIFormat", "3"), ("Player", "Multi1"),
                  ("Official", "no"), ("SoloMission", "False"), ("Theme", "No Theme"),
                  ("CarryOverCap", "-1"), ("CarryOverMoney", "0"), ("Percent", "100"),
                  ("Intro", "<none>"), ("Win", "<none>"), ("Lose", "<none>"),
                  ("Brief", "<none>"), ("Action", "<none>"), ("Author", "TF transcoder")])
    sec("Map", [("Theater", theater.capitalize()), ("X", mapx), ("Y", mapy),
                ("Width", mapw), ("Height", maph)])
    for sct in ("SMUDGE", "CellTriggers", "TeamTypes", "INFANTRY",
                "Base", "UNITS", "AIRCRAFT", "SHIPS", "Trigs"):
        sec(sct, [])
    sec("STRUCTURES", [(str(i), s) for i, s in enumerate(structures)])
    sec("TERRAIN", [(str(c), v) for c, v in terrain])
    for hs in HOUSES:
        sec(hs, [("Allies", hs)] + HOUSE_BLOCK)
    sec("Waypoints", [(str(i), c) for i, c in enumerate(starts)])
    sec("MapPack", uublock_encode(lcw_block_compress(mappack_raw)))
    sec("OverlayPack", uublock_encode(lcw_block_compress(overlay_raw)))
    if tdtiles_raw is not None:
        sec("TFTDTiles", uublock_encode(lcw_block_compress(tdtiles_raw)))
    with open(path, "w", newline="\r\n", encoding="latin-1") as f:
        f.write("\r\n".join(L) + "\r\n")

    # ---- .json discovery manifest ----
    import json
    base = os.path.splitext(path)[0]
    manifest = {"MapTileX": mapx, "MapTileY": mapy, "MapTileWidth": mapw,
                "MapTileHeight": maph, "Theater": theater.upper(), "Waypoints": starts}
    with open(base + ".json", "w") as f:
        json.dump(manifest, f, separators=(",", ":"))

    # ---- .tga 512x512 minimap preview ----
    write_minimap_tga(base + ".tga", ttype, overlay_raw, mapx, mapy, mapw, maph,
                      preview_png)

def write_minimap_tga(path, ttype, overlay_raw, mapx, mapy, mapw, maph,
                      preview_png=None):
    """512x512 BGRA preview. If the source carried a [CnCNetPreview] PNG it is
    composited over the playable-bounds region (the authentic TD render);
    otherwise cells are coloured by content (crude block map)."""
    SCALE = 4  # 128 cells * 4 = 512
    W = H = RA_W * SCALE
    # Per-cell colour (R,G,B).
    def cell_color(c):
        if overlay_raw[c] == OVERLAY_TIB01:
            return (60, 200, 60)        # tiberium = bright green
        t = ttype[c]
        if t == RA_TEMPLATE_NONE or t == 0:
            return (40, 70, 40)         # clear ground
        if t in (1, 2):
            return (40, 70, 150)        # water
        return (110, 100, 80)           # other templates = earth/rock
    # Build pixel rows (top-left origin via descriptor bit 5).
    row_cache = {}
    pixels = bytearray(W * H * 4)
    for cy in range(RA_W):
        for cx in range(RA_W):
            r, g, b = cell_color(ra_cell(cx, cy))
            # dim cells outside the playable bounds
            if not (mapx <= cx < mapx + mapw and mapy <= cy < mapy + maph):
                r, g, b = r // 3, g // 3, b // 3
            for dy in range(SCALE):
                py = cy * SCALE + dy
                base = (py * W + cx * SCALE) * 4
                for dx in range(SCALE):
                    o = base + dx * 4
                    pixels[o] = b; pixels[o + 1] = g; pixels[o + 2] = r; pixels[o + 3] = 255
    if preview_png is not None:
        try:
            import io
            from PIL import Image
            im = Image.open(io.BytesIO(preview_png)).convert("RGB")
            pw, ph = mapw * SCALE, maph * SCALE
            im = im.resize((pw, ph), Image.LANCZOS)
            px0, py0 = mapx * SCALE, mapy * SCALE
            src = im.load()
            for y in range(ph):
                base_off = ((py0 + y) * W + px0) * 4
                for x in range(pw):
                    r, g, b = src[x, y]
                    o = base_off + x * 4
                    pixels[o] = b; pixels[o + 1] = g; pixels[o + 2] = r; pixels[o + 3] = 255
        except Exception as e:
            print(f"  WARNING: preview composite failed ({e}); keeping block map")
    header = bytes([0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0]) + struct.pack("<HH", W, H) + bytes([32, 0x20])
    with open(path, "wb") as f:
        f.write(header)
        f.write(pixels)

# ===================================================================== inspect
def inspect_ra(path):
    secs = read_ini(path)
    mpk = section_pack(secs, "MapPack")
    print(f"MapPack: {len(mpk)} bytes (expect {MAPPACK_RAW})")
    if len(mpk) == MAPPACK_RAW:
        ttypes = struct.unpack_from(f"<{RA_CELLS}H", mpk, 0)
        nonclear = sum(1 for t in ttypes if t != RA_TEMPLATE_NONE and t != 0)
        import collections
        top = collections.Counter(ttypes).most_common(5)
        print(f"  non-clear template cells: {nonclear};  top TType: {top}")
    ovr = section_pack(secs, "OverlayPack")
    print(f"OverlayPack: {len(ovr)} bytes (expect {RA_CELLS})")
    if len(ovr) == RA_CELLS:
        import collections
        nz = collections.Counter(b for b in ovr if b != OVERLAY_NONE)
        print(f"  overlay cells: {sum(nz.values())};  by id: {dict(nz.most_common(8))}")
    # codec round-trip self-check
    if len(mpk) == MAPPACK_RAW:
        rt = lcw_block_decompress(lcw_block_compress(mpk))
        print(f"  codec round-trip: {'OK' if rt == mpk else 'FAIL'}")

# ===================================================================== main
def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("inspect-ra"); p1.add_argument("path")
    p2 = sub.add_parser("convert"); p2.add_argument("td_ini"); p2.add_argument("out")
    p2.add_argument("--name", default=None)
    a = ap.parse_args()
    if a.cmd == "inspect-ra":
        inspect_ra(a.path)
    elif a.cmd == "convert":
        nm = a.name or os.path.splitext(os.path.basename(a.td_ini))[0]
        convert(a.td_ini, a.out, nm)

if __name__ == "__main__":
    main()
