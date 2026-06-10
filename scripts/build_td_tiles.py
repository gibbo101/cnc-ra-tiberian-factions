#!/usr/bin/env python3
r"""
TD -> RA terrain-template porter (Tiberian Factions mod).

Ports TD terrain templates into RA as new TD-prefixed templates with TD's
EXACT size + TD's authentic HD art, so the map transcoder (td_map_to_ra.py)
can map every TD tile 1:1 with icons aligning perfectly -- no name-collision /
size-mismatch garbage.

Theatre-aware: each tile lists the theatres it ships in ("T" temperate,
"S" snow). RA snow carries TD's WINTER art (icy-temperate look, NOT RA's
all-white snow), sourced per theatre:
  - HD: TEXTURES_TD_SRGB.MEG  TERRAIN\TEMPERATE\<NAME>\<NAME>.TEM-...DDS
        vs                    TERRAIN\WINTER\<NAME>.WIN\<NAME>.WIN-...DDS
        (the WINTER per-tile subdir carries the suffix; TEMPERATE does not).
  - classic: TEMPERAT.MIX <name>.tem -> staged TD<NAME>.TEM;
             WINTER.MIX  <name>.win -> staged TD<NAME>.SNO
        (the engine loads <IniName>.<RA theatre Suffix>, snow = "SNO").

For each TD template NAME+theatre it emits:
  - HD art: TD<NAME>.ZIP of cropped TGAs (one per icon, per animation frame),
    laid out like TIB01 (frames `td<name>-<icon>-<frame>.tga`), into that
    theatre's texture dir.
  - tileset XML: <Tile> blocks spliced into RA_TERRAIN_TEMPERATE.XML /
    RA_TERRAIN_SNOW.XML between TF markers.
  - classic art: the theatre's raw iconset converted to RA format and staged
    (build_tfassets.sh packs it).
And once per template:
  - DLL codegen: enum entry (defines.h), static TemplateTypeClass with the
    combined THEATERF_ mask (cdata.cpp), Init_Heap registration -- all between
    TF markers (idempotent).
  - mapper: scripts/td_ra_tile_map.json = {td_name: {ra_name, ra_id}} for the
    transcoder. ra_id = 401 + index (DLL TEMPLATE_COUNT base, verified).

Usage: python3 scripts/build_td_tiles.py            # ports TILES below
Then:  rebuild TFASSETS (bash scripts/build_tfassets.sh) + the DLL.
"""
import io, json, os, re, struct, subprocess, sys, tempfile, zipfile
from pathlib import Path
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_tiberium_hd import extract_from_meg, crop_to_opaque, TD_TEX_MEG, TD_TERRAIN

REPO = Path(__file__).resolve().parent.parent
GAME = Path.home() / ".steam/steam/steamapps/common/CnCRemastered"
TD_TEMPLATES_CS = GAME / "SOURCECODE/CnCTDRAMapEditor/TiberianDawn/TemplateTypes.cs"
TD_CD1 = GAME / "Data/CNCDATA/TIBERIAN_DAWN/CD1"
TEX_ROOT = REPO / "resources/remaster_mods/Vanilla_RA/Data/ART/TEXTURES/SRGB/RED_ALERT/TERRAIN"
TILESETS = REPO / "resources/remaster_mods/Vanilla_RA/Data/XML/TILESETS"
DEFINES_H = REPO / "redalert/defines.h"
CDATA_CPP = REPO / "redalert/cdata.cpp"
MAPPER_JSON = REPO / "scripts/td_ra_tile_map.json"
TEM_STAGE = REPO / "scripts/_td_tems"   # staged classic iconsets, consumed by build_tfassets.sh
TD_CDATA = REPO.parent / "reference/vanilla-conquer/tiberiandawn/cdata.cpp"

# Theatre wiring: letter used in TILES -> source + destination config.
# "D" = TD desert -> RA's INTERIOR slot (jonwil recipe: a new RA theatre is
# launcher-blocked, but adding tiles to an existing theatre works).
# "S" = TD winter -> RA's TEMPERATE slot as the SEPARATE "TDW" family (Luke's
# 2026-06-10 rework): TD winter is icy-temperate, so hosting it in temperate
# makes RA's native bibs/radar-stand-ins/vanilla-fallback all match the look
# (RA snow's all-white versions matched nothing). A template id carries ONE
# art per theatre and TD<NAME> already holds TD temperate art there, so the
# winter family needs its own ids/names: TDW<NAME>. RA's snow theatre goes
# back to fully vanilla. Tradeoff (accepted): terrain-object trees on winter
# maps render as RA summer trees (custom terrain-object art is impossible --
# the blossom wall; snowy-tree neutral buildings are the future option).
#
# Families: letters "T"+"D" share one TD<NAME> template (per-theatre art);
# letter "S" emits a TDW<NAME> template. src = which TD theatre's art/classic
# is read; dest = which RA theatre slot it registers + renders in.
THEATRES = {
    "T": dict(meg_dir="TEMPERATE", suffix="TEM", sub_has_suffix=False,
              mix=TD_CD1 / "TEMPERAT.MIX", classic_ext="tem", stage_ext="TEM",
              tex_dir=TEX_ROOT / "TEMPERATE", xml=TILESETS / "RA_TERRAIN_TEMPERATE.XML",
              flag="THEATERF_TEMPERATE", family="TD", src_theatre="temperate"),
    "S": dict(meg_dir="WINTER", suffix="WIN", sub_has_suffix=True,
              mix=TD_CD1 / "WINTER.MIX", classic_ext="win", stage_ext="TEM",
              tex_dir=TEX_ROOT / "TEMPERATE", xml=TILESETS / "RA_TERRAIN_TEMPERATE.XML",
              flag="THEATERF_TEMPERATE", family="TDW", src_theatre="winter"),
    "D": dict(meg_dir="DESERT", suffix="DES", sub_has_suffix=True,
              mix=TD_CD1 / "DESERT.MIX", classic_ext="des", stage_ext="INT",
              tex_dir=TEX_ROOT / "INTERIOR", xml=TILESETS / "RA_TERRAIN_INTERIOR.XML",
              flag="THEATERF_INTERIOR", family="TD", src_theatre="desert"),
}

# (name, theatres). Order is LOAD-BEARING: it defines the engine template ids
# (401+), which must stay stable for already-converted maps -- only ever APPEND.
# Phase 2 = the full temperate shore family + the SCG30 bridges (RA reuses the
# sh names for re-drawn, re-laid-out art, so every shore must come from the
# ported TD art, never the name+size auto-match). Phase 3 (sh32-35) = extended
# shores for the classic MP maps. Phase 4 (p16-p20) = the WINTER-ONLY pavement
# family (scm74 Nowhere To Hide); TD temperate has no such templates.
TILES = [("sh1", "TS"), ("sh2", "TS"), ("sh3", "TS"), ("sh4", "TS"),
         ("sh5", "TS"), ("sh6", "TS"), ("sh7", "TS"), ("sh8", "TS"),
         ("sh9", "TS"), ("sh10", "TS"), ("sh11", "TS"), ("sh12", "TS"),
         ("sh13", "TS"), ("sh14", "TS"), ("sh15", "TS"), ("sh16", "TS"),
         ("sh17", "TS"), ("sh18", "TS"),
         ("bridge1", "TS"), ("bridge2", "TS"),
         ("sh32", "TS"), ("sh33", "TS"), ("sh34", "TS"), ("sh35", "TS"),
         ("p16", "S"), ("p17", "S"), ("p18", "S"), ("p19", "S"), ("p20", "S")]

# Phase 5 (2026-06-10): the ENTIRE remaining TD winter template set, ids
# 430+. TD winter is icy-TEMPERATE (dark green ground, muddy banks, snow
# patches) while RA snow is all-white -- so the name+size auto-match onto RA
# snow templates renders a white map with green TD patches (the 12-46-52
# screenshot). Authentic TD winter = render EVERY cell (incl. CLEAR ground,
# via TDCLEAR1 + the positional 4x4 icon pattern) from TD's own winter art.
# Winter-ONLY: on temperate maps the auto-match stays (TD temperate art and
# RA temperate art agree visually). Editor-source order, append-only.
TILES += [(n, "S") for n in
          ["clear1", "w1", "w2",
           "s01", "s02", "s03", "s04", "s05", "s06", "s07", "s08", "s09",
           "s10", "s11", "s12", "s13", "s14", "s15", "s16", "s17", "s18",
           "s19", "s20", "s21", "s22", "s23", "s24", "s25", "s26", "s27",
           "s28", "s29", "s30", "s31", "s32", "s33", "s34", "s35", "s36",
           "s37", "s38",
           "p07", "p08", "p13", "p14", "p15",
           "b1", "b2", "b3",
           "d01", "d02", "d03", "d04", "d05", "d06", "d07", "d08", "d09",
           "d10", "d11", "d12", "d13", "d14", "d15", "d16", "d17", "d18",
           "d19", "d20", "d21", "d22", "d23", "d24", "d25", "d26", "d27",
           "d28", "d29", "d30", "d31", "d32", "d33", "d34", "d35", "d36",
           "d37", "d38", "d39", "d40", "d41", "d42", "d43",
           "rv01", "rv02", "rv03", "rv04", "rv05", "rv06", "rv07", "rv08",
           "rv09", "rv10", "rv11", "rv12", "rv13",
           "ford1", "ford2", "falls1", "falls2", "bridge1d", "bridge2d"]]

# Phase 6 (2026-06-10): the DESERT theatre -> RA's interior slot. 93 existing
# tiles also ship in TD desert (theatre letter added programmatically below);
# 73 are desert-only, appended as ids 541+. Editor-source order, append-only.
# p08/br5/br10 are desert-flagged in the editor source but the remaster MEG
# ships NO desert HD art for them (generation hard-fails) -- excluded; their
# cells transcode as clear ground.
_DESERT_ALSO = set(
    ["clear1", "w1", "p07", "sh17", "sh18", "b1", "b2",
     "ford1", "ford2", "falls1", "falls2"]
    + [f"s{i:02d}" for i in range(1, 39)]
    + [f"d{i:02d}" for i in range(1, 44)])
TILES = [(n, t + "D" if n in _DESERT_ALSO else t) for n, t in TILES]
TILES += [(n, "D") for n in
          ["sh20", "sh21", "sh22", "sh23",
           "br1", "br2", "br3", "br4", "br6", "br7", "br8", "br9",
           "p01", "p02", "p03", "p04", "p05", "p06", "sh19",
           "rv14", "rv15", "rv16", "rv17", "rv18", "rv19", "rv20", "rv21",
           "rv22", "rv23", "rv24", "rv25",
           "bridge3", "bridge3d", "bridge4", "bridge4d",
           "sh24", "sh25", "sh26", "sh27", "sh28", "sh29", "sh30", "sh31",
           "sh36", "sh37", "sh38", "sh39", "sh40", "sh41", "sh42", "sh43",
           "sh44", "sh45", "sh46", "sh47", "sh48", "sh49", "sh50", "sh51",
           "sh52", "sh53", "sh54", "sh55", "sh56", "sh57", "sh58", "sh59",
           "sh60", "sh61", "sh62", "sh63"]]

# Water/shore animation: the launcher cycles a <Tile>'s <Frames> list only for
# templates in its preloaded base-MEG atlas, NOT for dynamic-map entries (our
# render path) -- those always draw frame 0. The proven pattern is FLAGFLY's
# (dllinterface.cpp): vary ShapeIndex over time. So anim frames are flattened
# into SHAPES: Shape = icon * shapes_per_icon + frame, one <Frame> each. TD's
# HD terrain anim is uniformly 8 frames where present (verified across the
# sh/bridge/rv families); static icons alias their single TGA across all
# shapes (XML references only -- the ZIP stores each real frame once).
#
# shapes_per_icon is PER TEMPLATE: the launcher's CNCDynamicMapEntryStruct
# ShapeIndex is an UNSIGNED CHAR (ABI, unchangeable), so big templates can't
# afford 8 shapes per icon -- desert rv20 (6x8 = icons up to 47) would flatten
# to 383. anim_shapes() halves the frame count until max_icon*n + n-1 <= 255
# (rv20/rv21 -> 4 frames, every other template keeps 8; a 1 = static). The
# per-template values ship in the generated TF_TdTileAnimShapes[] table and
# Cell_Class_Draw_It computes ShapeIndex = TIcon * n + (Frame / rate) % n.
ANIM_FRAMES = 8


def anim_shapes(w, h):
    n = ANIM_FRAMES
    while n > 1 and (w * h - 1) * n + n - 1 > 255:
        n //= 2
    return n

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


RA_TEMPLATES_CS = GAME / "SOURCECODE/CnCTDRAMapEditor/RedAlert/TemplateTypes.cs"


def vanilla_twins():
    """{name: ra_engine_id} for RA templates valid in TEMPERATE with their
    size -- used to emit TF_TdTileVanillaTwin[]: a TD/TDW template whose
    same-named RA template has the SAME size gets that template reported to
    the launcher for the static map + radar (Get_Template_Info) instead of a
    class stand-in. Rivers/roads/water/slopes then radar as RA's real art,
    and the static ground under tiberium/bib cells (where the dynamic ground
    entry is suppressed) keeps road/river continuity. The editor-source RA
    ids ARE the engine TemplateType ids (MapPack-proven)."""
    txt = RA_TEMPLATES_CS.read_text(errors="replace")
    out = {}
    for m in re.finditer(r'new TemplateType\(\s*(\d+)\s*,\s*"([^"]+)"\s*,\s*(\d+)\s*,\s*(\d+)'
                         r'\s*,\s*new TheaterType\[\]\s*\{([^}]*)\}', txt):
        if "Temperate" in m.group(5):
            out[m.group(2).lower()] = (int(m.group(1)), int(m.group(3)), int(m.group(4)))
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
    """Convert a TD-format iconset (32-byte header; .tem and .win are the same
    format) to RA format (40-byte header: +MapWidth/MapHeight at offset 8,
    +ColorMap offset at 32) and append the per-icon land table. Feeding a raw
    TD iconset to the RA engine reads zeros for MapWidth*MapHeight ->
    'icon % 0' INTEGER DIVIDE BY ZERO in Land_Type at map load (2026-06-09
    crash, RVA 0x3CDFB). Palettes/Remaps are zeroed: TD files carry junk there
    and the remaster classic render doesn't use them."""
    icon_w, icon_h, count, _alloc = struct.unpack_from("<4h", data, 0)
    _size, icons, _pal, _remaps, trans, imap = struct.unpack_from("<6i", data, 8)
    body = data[32:]
    color_off = 40 + len(body)
    n = map_w * map_h
    cmap = bytes((LAND_NIBBLE[altland] if i in alt_icons else LAND_NIBBLE[land]) for i in range(n))
    hdr = struct.pack("<6H7i", icon_w, icon_h, count, 0, map_w, map_h,
                      color_off + n, icons + 8, 0, 0, trans + 8, color_off, imap + 8)
    return hdr + body + cmap


_meg_listing = None

def meg_listing():
    global _meg_listing
    if _meg_listing is None:
        _meg_listing = subprocess.run(
            [sys.executable, str(REPO / "scripts/meg_extract.py"), "list", str(TD_TEX_MEG)],
            capture_output=True, text=True).stdout.split("\n")
    return _meg_listing


def enum_dds(name, th):
    """Return ordered {icon: [meg_entry_paths]} for a TD template's HD frames
    in the given theatre."""
    up = name.upper()
    sub = f"{up}.{th['suffix']}" if th["sub_has_suffix"] else up
    src_dir = f"{TD_TERRAIN}\\{th['meg_dir']}\\{sub}"
    icons = {}
    pat = re.compile(re.escape(src_dir) + r"\\" + re.escape(up) + r"\."
                     + th["suffix"] + r"-(\d+)(?:-(\d+))?\.DDS", re.I)
    for line in meg_listing():
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
    TDSH1 (grass rows 0.00 water, waterline rows 0.26-0.41, water rows 1.00).
    One row per TEMPLATE (not per theatre): layout is identical across
    theatres, so tiles in both are classified from their TEMPERATE art (the
    calibration surface); winter-only tiles (snowy pavement = grey/white,
    neither water-blue nor dirt-warm) fall through to 'C' as intended."""
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
        # The water threshold is LOW (0.18, was 0.5): desert rivers (rv14-25)
        # are wide sand washes with a narrow vivid stream -- at 0.5 every
        # icon classified sand and rivers vanished from the desert minimap.
        if water / opaque >= 0.18:
            return "R"
        if dirt / opaque >= 0.35:
            return "B"
        return "C"
    if water / opaque >= 0.5:
        return "W"
    if water / opaque >= 0.12 or dirt / opaque >= 0.5:
        return "B"
    return "C"


def is_river_like(name):
    """Bridges + rivers/fords/falls classify through the river branch: their
    water icons must continue the textured rv* radar art ('R' -> RV13), not
    read as flat sea W1."""
    return name.lower().startswith(("bridge", "rv", "falls", "ford"))


def is_rock(name):
    """Slopes (cliff faces) + boulders: colour thresholds can't tell rock from
    sand/dirt reliably (desert cliffs ARE sand-coloured; winter cliffs are
    icy), so these classify by NAME to the dedicated 'K' rock class -- radar
    shows them as cliff/rock stand-ins (RA SLOPE01 / desert palette ARRO0004)."""
    return re.fullmatch(r"s\d\d|b[123]", name.lower()) is not None


def classify_tile(name, th, work):
    """Radar classification only: frame 0 of each icon from the given
    theatre's HD art. Much cheaper than a full art build -- lets the radar
    row come from a DIFFERENT theatre than the one being built (winter rows
    classify from TEMPERATE art: icy winter water/rivers read white and fail
    the colour tests)."""
    if is_rock(name):
        w, h = td_sizes()[name]
        return {i: "K" for i in range(w * h)}
    icons = enum_dds(name, th)
    radar = {}
    for icon, entries in icons.items():
        dds = extract_from_meg(TD_TEX_MEG, entries[0], work)
        im = Image.open(dds).convert("RGBA")
        radar[icon] = radar_class(im, river=is_river_like(name))
    return radar


def build_tile_theatre(name, ra, th, work, n_shapes, skip_art):
    """Build one tile's HD ZIP + XML blocks + staged classic iconset for one
    theatre. ra = the engine template name (family prefix + NAME, e.g. TDSH1
    or TDWSH1). n_shapes = shapes flattened per icon (anim_shapes()).
    skip_art: when the ZIP + staged classic already exist, regenerate only the
    XML blocks (cheap, listing-only) and skip extraction. Radar classification
    is NOT done here (see classify_tile).
    Returns (xml_tiles, info)."""
    up, stem = name.upper(), ra.lower()
    icons = enum_dds(name, th)
    if not icons:
        raise SystemExit(f"no HD DDS found for {name} in {th['meg_dir']}")
    th["tex_dir"].mkdir(parents=True, exist_ok=True)
    zip_path = th["tex_dir"] / f"{ra}.ZIP"
    spec = td_land_specs().get(name.lower())
    if spec is None:
        raise SystemExit(f"no TD land spec found in cdata.cpp for {name}")
    land, w, h, altland, alt_icons = spec
    staged = TEM_STAGE / f"{ra}.{th['stage_ext']}"
    skip = skip_art and zip_path.exists() and staged.exists()

    xml_tiles = []
    zf = None if skip else zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED)
    for icon, entries in icons.items():
        if icon * n_shapes + n_shapes - 1 > 255:
            raise SystemExit(f"{name} icon {icon}: flattened ShapeIndex exceeds u8 "
                             f"(n_shapes={n_shapes})")
        # Animated icons are RESAMPLED evenly onto the template's shape grid
        # (n_shapes): 8 -> 8 is identity, 8 -> 4 keeps every other frame
        # (half-rate anim, not truncation), and odd source counts (desert
        # sh46 has NINE frames; anim is NOT uniformly 8 there) drop the
        # excess evenly.
        if len(entries) == 1:
            used = entries
        else:
            used = [entries[i * len(entries) // n_shapes] for i in range(n_shapes)]
            if len(entries) not in (1, ANIM_FRAMES):
                print(f"    note: {name} icon {icon} ({th['meg_dir']}): "
                      f"{len(entries)} frames resampled to {n_shapes}")
        if zf is not None:
            for fi, entry in enumerate(used):
                dds = extract_from_meg(TD_TEX_MEG, entry, work)
                im = Image.open(dds).convert("RGBA")
                cropped, meta = crop_to_opaque(im)
                fn = f"{stem}-{icon:04d}-{fi:02d}"
                buf = io.BytesIO(); cropped.save(buf, "TGA")
                zf.writestr(fn + ".tga", buf.getvalue())
                zf.writestr(fn + ".meta", json.dumps(meta))
        for f in range(n_shapes):
            fn = f"{stem}-{icon:04d}-{f % len(used):02d}"
            xml_tiles.append(
                "\t\t\t<Tile>\n\t\t\t\t<Key>\n\t\t\t\t\t<Name>{n}</Name>\n\t\t\t\t\t<Shape>{s}</Shape>\n"
                "\t\t\t\t</Key>\n\t\t\t\t<Value>\n\t\t\t\t\t<Frames>\n"
                "\t\t\t\t\t\t<Frame>{stem}\\{fn}.tga</Frame>\n"
                "\t\t\t\t\t</Frames>\n\t\t\t\t</Value>\n\t\t\t</Tile>".format(
                    n=ra, s=icon * n_shapes + f, stem=stem, fn=fn))
    if zf is not None:
        zf.close()
        # classic iconset staged for TFASSETS -- extracted from the theatre mix,
        # then CONVERTED to RA's format (TD-format files crash RA's Land_Type).
        TEM_STAGE.mkdir(parents=True, exist_ok=True)
        classic = f"{name.lower()}.{th['classic_ext']}"
        subprocess.run([sys.executable, str(REPO / "scripts/mix_tools.py"), "extract",
                        str(th["mix"]), classic, str(TEM_STAGE)], check=True,
                       stdout=subprocess.DEVNULL)
        raw = (TEM_STAGE / classic).read_bytes()
        (TEM_STAGE / classic).unlink()
        staged.write_bytes(td_tem_to_ra(raw, w, h, land, altland, alt_icons))
    return xml_tiles, (land, altland, alt_icons, w, h, len(icons))


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


def cached_radar_rows():
    """Parse the existing TF_TdTileRadarClass rows out of cdata.cpp so a
    --skip-existing run can reuse prior classifications without extracting
    any art. Keyed by full template name: {'TDSH1': 'CCCBBBWWW', ...}"""
    txt = CDATA_CPP.read_text()
    return {"TD" + m.group(2): m.group(1) for m in
            re.finditer(r'"([WBRCK]*)",\s*//\s*TEMPLATE_TD(\w+)', txt)}


def main():
    skip_existing = "--skip-existing" in sys.argv
    cached = cached_radar_rows() if skip_existing else {}

    sizes = td_sizes()
    base = template_count_base()
    print(f"DLL TEMPLATE_COUNT base = {base} (first new template id)")
    work = Path(tempfile.mkdtemp())
    enum_lines, def_lines, init_lines, mapper, radar_rows, anim_rows = [], [], [], {}, [], []
    twin_rows = []
    twins = vanilla_twins()
    xml_per_theatre = {letter: [] for letter in THEATRES}
    for name, ths in TILES:
        w, h = sizes[name]
        # Family split: "T"/"D" share one TD<NAME> template (multi-theatre
        # art); "S" emits the separate TDW<NAME> template (winter art hosted
        # in the temperate slot). Ids are sequential in emission order --
        # converted maps embed these ids in [TFTDTiles], and the bundle is
        # regenerated in the same build, so the only id-stability rule is
        # WITHIN one release artifact.
        for letters in ([le for le in ths if le in "TD"],
                        [le for le in ths if le == "S"]):
            if not letters:
                continue
            family = THEATRES[letters[0]]["family"]
            ra = family + name.upper()
            tid = base + len(enum_lines)
            # shapes flattened per icon: 1 for fully-STATIC templates (a
            # constant ShapeIndex -- a churning one makes the launcher
            # re-create the sprite every cycle, which z-pops above overlays =
            # the winter tiberium flicker), else 8 halved until the flattened
            # index fits the launcher's u8 ShapeIndex (desert rv20/rv21 -> 4).
            animated = any(len(frs) > 1
                           for letter in letters
                           for frs in enum_dds(name, THEATRES[letter]).values())
            n_shapes = anim_shapes(w, h) if animated else 1
            # Radar classification source: TEMPERATE art whenever the template
            # exists there (icy winter water and rivers read WHITE and fail the
            # colour tests -- the 19:21 all-green winter minimap; temperate has
            # the same icon layout with honestly-coloured water), else the
            # family's first source theatre (desert classes from desert art --
            # its water/rivers are blue, sand reads 'B' as intended). Slopes +
            # boulders force 'K' by name (see is_rock). Cached rows are reused
            # only under --skip-existing AND when not reclassifying.
            reclassify = "--reclassify" in sys.argv
            if ra in cached and not reclassify:
                radar = dict(enumerate(cached[ra]))
            else:
                cls_th = THEATRES["T"] if enum_dds(name, THEATRES["T"]) else THEATRES[letters[0]]
                radar = classify_tile(name, cls_th, work)
            info = None
            for letter in letters:
                th = THEATRES[letter]
                xml_tiles, info = build_tile_theatre(
                    name, ra, th, work, n_shapes=n_shapes, skip_art=skip_existing)
                xml_per_theatre[letter] += xml_tiles
            land, altland, alt_icons, _w, _h, n_icons = info
            radar_row = "".join(radar.get(i, "C") for i in range(w * h))
            flags = " | ".join(sorted({THEATRES[letter]["flag"] for letter in letters}))
            theat = "+".join(THEATRES[letter]["meg_dir"] for letter in letters)
            print(f"  {name:<9} -> {ra}: {n_icons} icons x{n_shapes}, {theat}, "
                  f"land {land}/alt {altland}@{sorted(alt_icons) if alt_icons else '[]'}, "
                  f"radar {radar_row}")
            var = "TdTile_" + ra
            enum_lines.append(f"    {('TEMPLATE_' + ra)},  // id {tid}")
            def_lines.append(f'static TemplateTypeClass const {var}(TEMPLATE_{ra}, '
                             f'{flags}, "{ra}", TXT_CLEAR);')
            init_lines.append(f"    (void)new TemplateTypeClass({var});")
            # mapper: keyed by TD template name, then by the SOURCE TD theatre
            # of the map being converted -- a winter map's "sh1" cell maps to
            # TDWSH1, a temperate/desert map's to TDSH1.
            for letter in letters:
                mapper.setdefault(name, {})[THEATRES[letter]["src_theatre"]] = {
                    "ra_name": ra, "ra_id": tid, "size": sizes.get(name)}
            radar_rows.append(f'    "{radar_row}", // TEMPLATE_{ra}')
            anim_rows.append(f"    {n_shapes}, // TEMPLATE_{ra}")
            # vanilla twin: only meaningful for temperate-slot display (the
            # interior branch in cell.cpp uses the desert palette instead)
            twin = -1
            if any(THEATRES[le]["flag"] == "THEATERF_TEMPERATE" for le in letters):
                v = twins.get(name)
                if v and (v[1], v[2]) == (w, h):
                    twin = v[0]
            twin_rows.append(f"    {twin}, // TEMPLATE_{ra}"
                             + (f" -> RA {name}" if twin >= 0 else ""))

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
    twin_block = (
        "/* Same-named same-size VANILLA RA template per TD-ported template, or -1.\n"
        "   Get_Template_Info (cell.cpp) reports the twin (same icon -- sizes match)\n"
        "   to the launcher for the static map + RADAR on temperate-slot maps:\n"
        "   rivers/roads/water/slopes then radar as RA's real art, and the static\n"
        "   ground under overlay/smudge cells keeps road continuity. -1 = no twin\n"
        "   (shores/bridges differ in size; interior/desert uses the palette path).\n"
        "   Values are engine TemplateType ids (= editor-source RA ids).\n"
        "   Row index = TType - TEMPLATE_TDSH1. Generated by build_td_tiles.py. */\n"
        "extern short const TF_TdTileVanillaTwin[] = {\n" + "\n".join(twin_rows) + "\n};")
    splice(CDATA_CPP, "twin", twin_block, r"void TemplateTypeClass::Init_Heap\(void\)")
    anim_block = (
        "/* Shapes flattened per icon for TD-ported templates (anim frames ride\n"
        "   the dynamic-map ShapeIndex: Shape = TIcon * n + frame). 1 = fully\n"
        "   static template: its ShapeIndex must stay CONSTANT -- a churning\n"
        "   value makes the launcher re-create the sprite every cycle, which\n"
        "   z-pops above overlay entries (the winter tiberium flicker). 8 is\n"
        "   TD's HD anim length; halved (4, 2) when a big template's flattened\n"
        "   index would exceed the launcher's u8 ShapeIndex (desert rv20/21).\n"
        "   Row index = TType - TEMPLATE_TDSH1; consumed by Cell_Class_Draw_It\n"
        "   (dllinterface.cpp). Generated by build_td_tiles.py. */\n"
        "extern unsigned char const TF_TdTileAnimShapes[] = {\n" + "\n".join(anim_rows) + "\n};")
    splice(CDATA_CPP, "anim", anim_block, r"void TemplateTypeClass::Init_Heap\(void\)")

    # tileset XMLs: before the closing </Tiles>. XML-comment markers (see MX).
    for letter, th in THEATRES.items():
        if xml_per_theatre[letter]:
            splice(th["xml"], "xml", "\n".join(xml_per_theatre[letter]),
                   r"[ \t]*</Tiles>", markers=MX("xml"))

    MAPPER_JSON.write_text(json.dumps(mapper, indent=2))
    print(f"\nwrote {len(enum_lines)} templates from {len(TILES)} tiles. mapper -> {MAPPER_JSON}")
    print(f"classic iconsets staged in {TEM_STAGE} (build_tfassets.sh packs them)")
    print("NEXT: bash scripts/build_tfassets.sh ; rebuild DLL ; regenerate maps")


if __name__ == "__main__":
    main()
