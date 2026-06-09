#!/usr/bin/env python3
"""
TD -> RA terrain-template porter (Tiberian Factions mod).

Ports TD temperate terrain templates into RA's temperate theatre as new
TD-prefixed templates with TD's EXACT size + TD's authentic HD art, so the
map transcoder (td_map_to_ra.py) can map every TD tile 1:1 with icons aligning
perfectly -- no name-collision / size-mismatch garbage.

For each TD template NAME it emits:
  - HD art: TD<NAME>.ZIP of cropped TGAs (one per icon, per animation frame),
    laid out like TIB01 (frames `td<name>-<icon>-<frame>.tga`, referenced in the
    tileset XML as `td<name>\\...`). Source = per-tile DDS in TEXTURES_TD_SRGB.MEG.
  - tileset XML: <Tile> blocks (one per icon; animated icons list all frames),
    spliced into RA_TERRAIN_TEMPERATE.XML between TF markers.
  - classic art: TD's raw <name>.tem staged as TD<NAME>.TEM (for engine
    dimensions + land-type + classic render; build_tfassets.sh packs it).
  - DLL codegen: enum entry (defines.h), static TemplateTypeClass (cdata.cpp),
    Init_Heap registration -- all between TF markers (idempotent).
  - mapper: scripts/td_ra_tile_map.json = {td_name: {ra_name, ra_id}} for the
    transcoder. ra_id = 401 + index (DLL TEMPLATE_COUNT base, verified).

Usage: python3 scripts/build_td_tiles.py            # ports TILES below
Then:  rebuild TFASSETS (bash scripts/build_tfassets.sh) + the DLL.
"""
import io, json, os, re, struct, sys, tempfile, zipfile
from pathlib import Path
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_tiberium_hd import extract_from_meg, crop_to_opaque, TD_TEX_MEG, TD_TERRAIN_TEMP

REPO = Path(__file__).resolve().parent.parent
GAME = Path.home() / ".steam/steam/steamapps/common/CnCRemastered"
TD_TEMPLATES_CS = GAME / "SOURCECODE/CnCTDRAMapEditor/TiberianDawn/TemplateTypes.cs"
TEMPERAT_MIX = GAME / "Data/CNCDATA/TIBERIAN_DAWN/CD1/TEMPERAT.MIX"
TERRAIN_TEX = REPO / "resources/remaster_mods/Vanilla_RA/Data/ART/TEXTURES/SRGB/RED_ALERT/TERRAIN/TEMPERATE"
TILESET_XML = REPO / "resources/remaster_mods/Vanilla_RA/Data/XML/TILESETS/RA_TERRAIN_TEMPERATE.XML"
DEFINES_H = REPO / "redalert/defines.h"
CDATA_CPP = REPO / "redalert/cdata.cpp"
MAPPER_JSON = REPO / "scripts/td_ra_tile_map.json"
TEM_STAGE = REPO / "scripts/_td_tems"   # staged classic .tem, consumed by build_tfassets.sh
TD_CDATA = REPO.parent / "reference/vanilla-conquer/tiberiandawn/cdata.cpp"

# Phase 2: the FULL temperate shore family + the SCG30 bridges. RA reuses the
# sh names for re-drawn, re-laid-out art (TD sh9 = rocky outcrop, RA sh09 =
# watery shore edge -- the 2026-06-09 "random coast tiles"), so every shore
# must come from the ported TD art, never the name+size auto-match.
TILES = ["sh1", "sh2", "sh3", "sh4", "sh5", "sh6", "sh7", "sh8", "sh9",
         "sh10", "sh11", "sh12", "sh13", "sh14", "sh15", "sh16", "sh17", "sh18",
         "bridge1", "bridge2"]

# Markers (idempotent splice). C++-style for code files; XML files MUST use
# XML comments instead -- a raw '<' in text content (the '<<<' arrows) makes
# the tileset XML ill-formed and CRASHES ClientG at map load (2026-06-09).
# No '--' inside the comment text either (illegal in XML comments).
M = lambda tag: (f"// >>> TF_TD_TILES {tag} >>>", f"// <<< TF_TD_TILES {tag} <<<")
MX = lambda tag: (f"<!-- TF_TD_TILES {tag} BEGIN -->", f"<!-- TF_TD_TILES {tag} END -->")


def td_sizes():
    txt = TD_TEMPLATES_CS.read_text(errors="replace")
    out = {}
    for m in re.finditer(r'new TemplateType\(\s*\d+\s*,\s*"([^"]+)"\s*,\s*(\d+)\s*,\s*(\d+)', txt):
        out[m.group(1).lower()] = (int(m.group(2)), int(m.group(3)))
    return out


def template_count_base():
    """Number of existing DLL TemplateType ids (= id of our first new template).
    Counts every enum entry (FIXIT_ANTS is defined, so HILL01 counts) before our
    BEGIN marker (or before TEMPLATE_COUNT on first run)."""
    lines = DEFINES_H.read_text().split("\n")
    start = next(i for i, l in enumerate(lines) if "enum TemplateType" in l)
    begin = M("enum")[0]
    n = 0
    for l in lines[start + 1:]:
        s = l.split("//")[0].strip()
        if begin in l:
            break
        if s.startswith("#") or s in ("", "{"):
            continue
        s = s.rstrip(",")
        if "TEMPLATE_COUNT" in s:
            break
        if "=" in s:           # aliases (TEMPLATE_NONE/FIRST) -- none before COUNT
            continue
        n += 1
    return n


# RA reads per-icon land types from the iconset's ColorMap table: nibble codes
# indexed by logical icon, looked up in the _land[16] table in RA cdata.cpp
# (TemplateTypeClass::Land_Type). TD has no such table -- its land data is in
# CODE: each template ctor gives a default Land + AltLand applied to the icon
# indices in a -1-terminated _slope* array (TD cell.cpp Recalc_Attributes).
LAND_NIBBLE = {"CLEAR": 0, "BEACH": 6, "ROCK": 8, "ROAD": 9, "WATER": 10, "RIVER": 11, "ROUGH": 14}


def td_land_specs():
    """{ininame.lower(): (land, w, h, altland, alticon_set)} parsed from TD cdata.cpp."""
    txt = TD_CDATA.read_text(errors="replace")
    arrays = {m.group(1): [int(v) for v in re.findall(r"-?\d+", m.group(2)) if int(v) >= 0]
              for m in re.finditer(r"static char const (_slope\w+)\[\]\s*=\s*\{([^}]*)\}", txt)}
    specs = {}
    for m in re.finditer(
            r'TemplateTypeClass\s+const\s*\w+\(TEMPLATE_\w+,[^;]*?"([^"]+)",\s*TXT_\w+,\s*'
            r'LAND_(\w+),\s*(\d+),\s*(\d+),\s*LAND_(\w+),\s*(?:\(char const\*\)\s*(_slope\w+)|NULL)\)',
            txt, re.S):
        name = m.group(1).lower()
        alt = frozenset(arrays.get(m.group(6), [])) if m.group(6) else frozenset()
        specs[name] = (m.group(2), int(m.group(3)), int(m.group(4)), m.group(5), alt)
    return specs


def td_tem_to_ra(data, map_w, map_h, land, altland, alt_icons):
    """Convert a TD-format .tem (32-byte header) to RA format (40-byte header:
    +MapWidth/MapHeight at offset 8, +ColorMap offset at 32) and append the
    per-icon land table. Feeding a raw TD .tem to the RA engine reads zeros for
    MapWidth*MapHeight -> 'icon % 0' INTEGER DIVIDE BY ZERO in Land_Type at map
    load (2026-06-09 crash, RVA 0x3CDFB). Palettes/Remaps are zeroed: TD files
    carry junk there and the remaster classic render doesn't use them."""
    icon_w, icon_h, count, _alloc = struct.unpack_from("<4h", data, 0)
    _size, icons, _pal, _remaps, trans, imap = struct.unpack_from("<6i", data, 8)
    body = data[32:]
    color_off = 40 + len(body)
    n = map_w * map_h
    cmap = bytes((LAND_NIBBLE[altland] if i in alt_icons else LAND_NIBBLE[land]) for i in range(n))
    hdr = struct.pack("<6H7i", icon_w, icon_h, count, 0, map_w, map_h,
                      color_off + n, icons + 8, 0, 0, trans + 8, color_off, imap + 8)
    return hdr + body + cmap


def enum_dds(name):
    """Return ordered {icon: [meg_entry_paths]} for a TD template's HD frames."""
    up = name.upper()
    src_dir = f"{TD_TERRAIN_TEMP}\\{up}"
    # list the MEG once, filter for this template
    import subprocess
    listing = subprocess.run(
        [sys.executable, str(REPO / "scripts/meg_extract.py"), "list", str(TD_TEX_MEG)],
        capture_output=True, text=True).stdout
    icons = {}
    pat = re.compile(re.escape(src_dir) + r"\\" + re.escape(up) + r"\.TEM-(\d+)(?:-(\d+))?\.DDS", re.I)
    for line in listing.split("\n"):
        m = pat.search(line)
        if not m:
            continue
        icon = int(m.group(1))
        frame = int(m.group(2)) if m.group(2) is not None else 0
        entry = line.strip().split(None, 1)[1]  # "<size> <path>" -> path
        icons.setdefault(icon, []).append((frame, entry))
    return {ic: [e for _, e in sorted(frs)] for ic, frs in sorted(icons.items())}


def radar_class(im, river=False):
    """Classify an icon's frame-0 art for the radar stand-in: 'W' water-
    dominant, 'B' beach (visible waterline OR dry sand/dirt dominant), else
    'C' land. The cell LAND TYPE is too crude for radar -- TD types whole
    bridge blocks + bank tiles as WATER for movement, which painted blue
    rectangles bulging past the river course; and beach interiors typed BEACH
    must read as the sand coastline, not green land. Thresholds calibrated on
    TDSH1 (grass rows 0.00 water, waterline rows 0.26-0.41, water rows 1.00)."""
    opaque = water = dirt = 0
    for r, g, b, a in im.getdata():
        if a < 128:
            continue
        opaque += 1
        if b > r + 18 and b > g + 6:
            water += 1
        elif r > g - 6 and g > b + 10 and r > 75:
            dirt += 1
    if not opaque:
        return "C"
    if river:
        # Bridges cross RIVERS: their water icons must continue the textured
        # rv* radar art ('R' -> RV13), not flat sea W1, and their bank icons
        # must read as grass -- a water sliver alone is not a beach. Only the
        # genuinely dirt-dominant deck reads as the sand crossing strip.
        # (Flat W1 + sand banks made the bridge zone a radar checkerboard.)
        if water / opaque >= 0.5:
            return "R"
        if dirt / opaque >= 0.35:
            return "B"
        return "C"
    if water / opaque >= 0.5:
        return "W"
    if water / opaque >= 0.12 or dirt / opaque >= 0.5:
        return "B"
    return "C"


def build_tile(name, work):
    up, stem, ra = name.upper(), "td" + name.lower(), "TD" + name.upper()
    icons = enum_dds(name)
    if not icons:
        raise SystemExit(f"no HD DDS found for {name}")
    TERRAIN_TEX.mkdir(parents=True, exist_ok=True)
    zip_path = TERRAIN_TEX / f"{ra}.ZIP"
    xml_tiles = []
    radar = {}
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for icon, entries in icons.items():
            frames_xml = []
            for fi, entry in enumerate(entries):
                dds = extract_from_meg(TD_TEX_MEG, entry, work)
                im = Image.open(dds).convert("RGBA")
                cropped, meta = crop_to_opaque(im)
                if fi == 0:
                    radar[icon] = radar_class(im, river=name.lower().startswith("bridge"))
                fn = f"{stem}-{icon:04d}-{fi:02d}"
                buf = io.BytesIO(); cropped.save(buf, "TGA")
                zf.writestr(fn + ".tga", buf.getvalue())
                zf.writestr(fn + ".meta", json.dumps(meta))
                frames_xml.append(f"\t\t\t\t\t\t<Frame>{stem}\\{fn}.tga</Frame>")
            xml_tiles.append(
                "\t\t\t<Tile>\n\t\t\t\t<Key>\n\t\t\t\t\t<Name>{n}</Name>\n\t\t\t\t\t<Shape>{s}</Shape>\n"
                "\t\t\t\t</Key>\n\t\t\t\t<Value>\n\t\t\t\t\t<Frames>\n{f}\n"
                "\t\t\t\t\t</Frames>\n\t\t\t\t</Value>\n\t\t\t</Tile>".format(
                    n=ra, s=icon, f="\n".join(frames_xml)))
    # classic .tem staged for TFASSETS -- extracted from TD's TEMPERAT.MIX, then
    # CONVERTED to RA's iconset format (TD-format files crash RA's Land_Type).
    TEM_STAGE.mkdir(parents=True, exist_ok=True)
    import subprocess
    subprocess.run([sys.executable, str(REPO / "scripts/mix_tools.py"), "extract",
                    str(TEMPERAT_MIX), f"{name.lower()}.tem", str(TEM_STAGE)], check=True,
                   stdout=subprocess.DEVNULL)
    spec = td_land_specs().get(name.lower())
    if spec is None:
        raise SystemExit(f"no TD land spec found in cdata.cpp for {name}")
    land, w, h, altland, alt_icons = spec
    raw = (TEM_STAGE / f"{name.lower()}.tem").read_bytes()
    (TEM_STAGE / f"{name.lower()}.tem").unlink()
    (TEM_STAGE / f"{ra}.TEM").write_bytes(td_tem_to_ra(raw, w, h, land, altland, alt_icons))
    radar_row = "".join(radar.get(i, "C") for i in range(w * h))
    print(f"  {name:<9} -> {ra}: {len(icons)} icons, {sum(len(v) for v in icons.values())} frames, "
          f"land {land}/alt {altland}@{sorted(alt_icons) if alt_icons else '[]'}, radar {radar_row}")
    return ra, xml_tiles, radar_row


def splice(path, tag, block, anchor_re, after=False, markers=None):
    """Idempotently replace text between markers; insert at anchor on first run.
    Position-based (payload may contain backslashes). after=False -> before anchor.
    Preserves the file's native line endings (the game XMLs are CRLF; a
    read_text/write_text round-trip rewrites every line -> 60k-line git churn)."""
    begin, end = markers or M(tag)
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    nl = "\r\n" if text.count("\r\n") * 2 > text.count("\n") else "\n"
    payload = f"{begin}\n{block}\n{end}\n".replace("\n", nl)
    bi = text.find(begin)
    if bi != -1:
        ei = text.find(end, bi) + len(end)
        while ei < len(text) and text[ei] in "\r\n":
            ei += 1
        text = text[:bi] + payload + text[ei:]
    else:
        m = re.search(anchor_re, text)
        if not m:
            raise SystemExit(f"anchor not found in {path.name}: {anchor_re}")
        pos = m.end() + 1 if after else m.start()
        text = text[:pos] + payload + text[pos:]
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def main():
    sizes = td_sizes()
    base = template_count_base()
    print(f"DLL TEMPLATE_COUNT base = {base} (first new template id)")
    work = Path(tempfile.mkdtemp())
    enum_lines, def_lines, init_lines, xml_all, mapper, radar_rows = [], [], [], [], {}, []
    for idx, name in enumerate(TILES):
        ra, xml_tiles, radar_row = build_tile(name, work)
        tid = base + idx
        var = "TdTile_" + ra
        enum_lines.append(f"    {('TEMPLATE_' + ra)},  // id {tid}")
        def_lines.append(f'static TemplateTypeClass const {var}(TEMPLATE_{ra}, '
                         f'THEATERF_TEMPERATE, "{ra}", TXT_CLEAR);')
        init_lines.append(f"    (void)new TemplateTypeClass({var});")
        xml_all += xml_tiles
        mapper[name] = {"ra_name": ra, "ra_id": tid, "size": sizes.get(name)}
        radar_rows.append(f'    "{radar_row}", // TEMPLATE_{ra}')

    # DLL codegen. Order is load-bearing (heap index == enum id):
    #  - enum entries go right before TEMPLATE_COUNT -> ids 401+ (after HILL01=400).
    #  - static defs go just before Init_Heap (file scope; used by our registrations).
    #  - registrations go at the END of Init_Heap, AFTER the _Watcom_Ugh_Hack() call
    #    (which registers up to HILL01=400), so our new ids register in order 401+.
    splice(DEFINES_H, "enum", "\n".join(enum_lines), r"[ \t]*TEMPLATE_COUNT,")
    splice(CDATA_CPP, "defs", "\n".join(def_lines), r"void TemplateTypeClass::Init_Heap\(void\)")
    splice(CDATA_CPP, "init", "\n".join(init_lines), r"[ \t]*_Watcom_Ugh_Hack\(\);", after=True)
    radar_block = (
        "/* Radar stand-in class per LOGICAL icon for TD-ported templates ('W' =\n"
        "   water-dominant art -> W1, 'C' = land -> CLEAR1), classified offline from\n"
        "   the HD art by build_td_tiles.py. Row index = TType - TEMPLATE_TDSH1.\n"
        "   Consumed by CellClass::Get_Template_Info (cell.cpp). 'extern' because\n"
        "   namespace-scope const arrays default to INTERNAL linkage in C++. */\n"
        "extern char const* const TF_TdTileRadarClass[] = {\n" + "\n".join(radar_rows) + "\n};")
    splice(CDATA_CPP, "radar", radar_block, r"void TemplateTypeClass::Init_Heap\(void\)")

    # tileset XML: before the closing </Tiles>. XML-comment markers (see MX).
    splice(TILESET_XML, "xml", "\n".join(xml_all), r"[ \t]*</Tiles>", markers=MX("xml"))

    MAPPER_JSON.write_text(json.dumps(mapper, indent=2))
    print(f"\nwrote {len(TILES)} tiles. mapper -> {MAPPER_JSON}")
    print(f"classic .tem staged in {TEM_STAGE} (build_tfassets.sh packs them)")
    print("NEXT: bash scripts/build_tfassets.sh ; rebuild DLL ; regenerate map")


if __name__ == "__main__":
    main()
