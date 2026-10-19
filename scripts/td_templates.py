#!/usr/bin/env python3
"""TD's terrain templates as DLL templates for the TD theatres (docs/td-base-art.md).

usage: td_templates.py
One TD<NAME> template per TD template, flagged for each TD theatre whose HD tileset draws it
(THEATERF_DESERT, THEATERF_TDTEMPERATE, THEATERF_WINTER). It writes:
  - the enum entries (defines.h), static definitions and registrations (cdata.cpp), ids 401+ in
    TD's editor order with sh1 first (the code tests TType >= TEMPLATE_TDSH1);
  - each template's classic iconset per theatre, TD<NAME>.DES/.TEM/.WIN, converted from TD's own
    theatre MIX with TD's land types (rivers as LAND_RIVER) and each shore cell's land from
    td_shore_land.json, into scripts/_td_tems for build_tfassets.sh;
  - scripts/td_ra_tile_map.json, {td name: {theatre: {ra_name, ra_id, size}}}.
The HD art is TD's own, drawn by the launcher from TD's terrain tilesets.
"""
import json
import os
import re
import struct
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from meg_extract import read_member  # noqa: E402
from td_map_to_ra import EDITOR_SRC, parse_templates  # noqa: E402
import steam_library  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
TD_CD1 = steam_library.path("common/CnCRemastered/Data/CNCDATA/TIBERIAN_DAWN/CD1")
DEFINES_H = REPO / "redalert/defines.h"
CDATA_CPP = REPO / "redalert/cdata.cpp"
MAPPER_JSON = REPO / "scripts/td_ra_tile_map.json"
TEM_STAGE = REPO / "scripts/_td_tems"
LAND_NIBBLE = {"CLEAR": 0, "BEACH": 6, "ROCK": 8, "ROAD": 9, "WATER": 10, "RIVER": 11, "ROUGH": 14}
SHORE_LAND = REPO / "scripts/td_shore_land.json"
SHORE_LETTER = {"W": "WATER", "B": "BEACH", "C": "CLEAR", "R": "ROCK"}


def markers(tag):
    return "// >>> TF_TD_TILES %s >>>" % tag, "// <<< TF_TD_TILES %s <<<" % tag


def splice(path, tag, block, anchor_re, after=False):
    """Replaces the text between the tag's markers, or inserts it at the anchor on the first run."""
    begin, end = markers(tag)
    with open(path, encoding="latin-1", newline="") as f:
        text = f.read()
    payload = "%s\n%s\n%s\n" % (begin, block, end)
    bi = text.find(begin)
    if bi != -1:
        ei = text.find(end, bi) + len(end)
        while ei < len(text) and text[ei] in "\r\n":
            ei += 1
        text = text[:bi] + payload + text[ei:]
    else:
        m = re.search(anchor_re, text)
        if not m:
            raise SystemExit("anchor not found in %s: %s" % (path.name, anchor_re))
        pos = m.end() + 1 if after else m.start()
        text = text[:pos] + payload + text[pos:]
    with open(path, "w", encoding="latin-1", newline="") as f:
        f.write(text)


def template_count_base():
    """The id of the first TD template: the number of RA TemplateType entries before ours."""
    lines = DEFINES_H.read_text(encoding="latin-1").split("\n")
    start = next(i for i, line in enumerate(lines) if "enum TemplateType" in line)
    n = 0
    for line in lines[start + 1:]:
        s = line.split("//")[0].strip()
        if markers("enum")[0] in line or "TEMPLATE_COUNT" in s:
            break
        if s.startswith("#") or s in ("", "{") or "=" in s:
            continue
        n += 1
    return n


def td_tem_to_ra(data, map_w, map_h, land, altland, alt_icons, cells=None):
    """A TD iconset (32-byte header) in RA's format (40-byte header with the map size), with the per-icon
    land table RA reads from its ColorMap, or `cells` (one W/B/C/R per cell) where given. Without the map
    size RA divides by zero in Land_Type."""
    icon_w, icon_h, count, _alloc = struct.unpack_from("<4h", data, 0)
    _size, icons, _pal, _remaps, trans, imap = struct.unpack_from("<6i", data, 8)
    body = data[32:]
    color_off = 40 + len(body)
    n = map_w * map_h
    typed = [altland if i in alt_icons else land for i in range(n)]
    if cells:
        typed = [SHORE_LETTER.get(c, t) for c, t in zip(cells, typed)]
    cmap = bytes(LAND_NIBBLE[t] for t in typed)
    hdr = struct.pack("<6H7i", icon_w, icon_h, count, 0, map_w, map_h,
                      color_off + n, icons + 8, 0, 0, trans + 8, color_off, imap + 8)
    return hdr + body + cmap

# TD's source: the workspace's reference/ clone, beside the repo or above a worktree.
TD_CDATA = next(p / "reference/vanilla-conquer/tiberiandawn/cdata.cpp" for p in (REPO.parent, REPO.parent.parent)
                if (p / "reference/vanilla-conquer/tiberiandawn/cdata.cpp").exists())
CONFIG = str(steam_library.path("common/CnCRemastered/Data/CONFIG.MEG"))
# TD theatre: (editor token, HD tileset, classic MIX, classic extension, staged suffix, DLL flag, map key)
THEATRES = [("Desert", "TD_TERRAIN_DESERT", "DESERT.MIX", "des", "DES", "THEATERF_DESERT", "desert"),
            ("Temperate", "TD_TERRAIN_TEMPERATE", "TEMPERAT.MIX", "tem", "TEM", "THEATERF_TDTEMPERATE", "temperate"),
            ("Winter", "TD_TERRAIN_WINTER", "WINTER.MIX", "win", "WIN", "THEATERF_WINTER", "winter")]


def land_specs():
    """{name: (land, altland, alt icons)} from TD's cdata.cpp; a TXT_RIVER template's water is RIVER."""
    txt = TD_CDATA.read_text(errors="replace")
    arrays = {m.group(1): [int(v) for v in re.findall(r"-?\d+", m.group(2)) if int(v) >= 0]
              for m in re.finditer(r"static char const (_slope\w+)\[\]\s*=\s*\{([^}]*)\}", txt)}
    out = {}
    for m in re.finditer(r'TemplateTypeClass\s+const\s*\w+\(TEMPLATE_\w+,[^;]*?"([^"]+)",\s*(TXT_\w+),\s*'
                         r'LAND_(\w+),\s*\d+,\s*\d+,\s*LAND_(\w+),\s*(?:\(char const\*\)\s*(_slope\w+)|NULL)\)',
                         txt, re.S):
        river = m.group(2) == "TXT_RIVER"
        land, alt = (("RIVER" if river and x == "WATER" else x) for x in (m.group(3), m.group(4)))
        out[m.group(1).lower()] = (land, alt, frozenset(arrays.get(m.group(5), [])) if m.group(5) else frozenset())
    return out


def drawn_names(tileset):
    text = read_member(CONFIG, "DATA\\XML\\TILESETS\\%s.XML" % tileset).decode("latin-1")
    return {n.upper() for n in re.findall(r"<Name>([^<]+)</Name>", text)}


def main():
    td = [t for t in parse_templates(os.path.join(EDITOR_SRC, "TiberianDawn", "TemplateTypes.cs")) if t[1] != "clear1"]
    td.sort(key=lambda t: t[1] != "sh1")
    lands = land_specs()
    shores = json.loads(SHORE_LAND.read_text())
    drawn = {th[0]: drawn_names(th[1]) for th in THEATRES}
    base = template_count_base()
    TEM_STAGE.mkdir(parents=True, exist_ok=True)
    for old in TEM_STAGE.iterdir():
        if old.name.upper().startswith("TD"):
            old.unlink()
    enum_lines, def_lines, init_lines, mapper = [], [], [], {}
    for _id, name, w, h, theatres in td:
        here = [th for th in THEATRES if th[0] in theatres and name.upper() in drawn[th[0]]]
        if not here:
            continue
        ra = "TD" + name.upper()
        tid = base + len(enum_lines)
        land, alt, alt_icons = lands[name]
        for token, _tileset, mix, ext, suffix, _flag, key in here:
            classic = "%s.%s" % (name, ext)
            subprocess.run([sys.executable, str(REPO / "scripts/mix_tools.py"), "extract", str(TD_CD1 / mix), classic,
                            str(TEM_STAGE)], check=True, stdout=subprocess.DEVNULL)
            raw = (TEM_STAGE / classic).read_bytes()
            (TEM_STAGE / classic).unlink()
            cells = shores[key].get(name)
            (TEM_STAGE / ("%s.%s" % (ra, suffix))).write_bytes(td_tem_to_ra(raw, w, h, land, alt, alt_icons, cells))
            mapper.setdefault(name, {})[key] = {"ra_name": ra, "ra_id": tid, "size": [w, h]}
        flags = " | ".join(th[5] for th in here)
        enum_lines.append("    TEMPLATE_%s, // id %d" % (ra, tid))
        line = 'static TemplateTypeClass const TdTile_%s(TEMPLATE_%s, %s, "%s", TXT_CLEAR);' % (ra, ra, flags, ra)
        def_lines.append(line if len(line) <= 120 else line.replace("const TdTile_", "const\n    TdTile_", 1))
        init_lines.append("    (void)new TemplateTypeClass(TdTile_%s);" % ra)
    splice(DEFINES_H, "enum", "\n".join(enum_lines), r"[ \t]*TEMPLATE_COUNT,")
    splice(CDATA_CPP, "defs", "\n".join(def_lines), r"void TemplateTypeClass::Init_Heap\(void\)")
    splice(CDATA_CPP, "init", "\n".join(init_lines), r"[ \t]*_Watcom_Ugh_Hack\(\);", after=True)
    MAPPER_JSON.write_text(json.dumps(mapper, indent=2) + "\n")
    print("%d templates, ids %d-%d; classic iconsets in %s" % (len(enum_lines), base, base + len(enum_lines) - 1,
                                                                 TEM_STAGE))


if __name__ == "__main__":
    main()
