#!/usr/bin/env python3
"""Generate and pack the TS GDI concrete wall (TSWALL) as HD overlay art.

The wall is a generated voxel model, not a TS sprite: TS's GTWALL.SHP is drawn
on the isometric diagonals and cannot be made to run along RA's grid axes.
Each join state is composed from boxes on a per-cell voxel grid and rendered
through vxl_render.py at the TS ground vehicles' camera (32 deg elevation, TS
VPL shading), then stretched vertically so the ground plane is 1:1 and the
segments tile cell to cell exactly like the base game's HD BRIK art.

Shape (from the TS screenshot + GTWALL decoded with UNITTEM.PAL): grey
concrete slab, rounded crest, one dark seam per segment, tan piers straddling
each joined cell edge, sloped caps at run ends, no team colour.

Frames: RA's wall layout, OverlayData = join bits (N=1 E=2 S=4 W=8) + 16 x
damage stage (0..2). 48 frames on a 128x320 canvas whose centre is the cell
centre; the classic stub is 24x60 (build_tfassets.sh). Damage stages are the
healthy model with progressively broken crest and darkened faces.

Outputs: Data/ART/TEXTURES/SRGB/RED_ALERT/STRUCTURES/TSWALL.ZIP, the
RA_STRUCTURES.XML tile run, BuildIcon_TS_Wall.tga (from WALLICON, CAMEO.PAL),
and scripts/ts_stub_dims.json's TSWALL entry.

Usage: ts_pack_walls.py [--preview <out.png>]   (preview = a composed scene only)
License: GPL v3.
"""
import io, json, math, os, sys, zipfile
import numpy as np
from PIL import Image

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS)
import vxl_render as vr

MOD = os.path.abspath(os.path.join(SCRIPTS, "..", "resources/remaster_mods/Vanilla_RA"))
STRUCT_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/STRUCTURES"
ICON_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB"
TILESET = f"{MOD}/Data/XML/TILESETS/RA_STRUCTURES.XML"
STUB_MANIFEST = f"{SCRIPTS}/ts_stub_dims.json"
ART = os.environ.get("TS_ART_DIR", "")

INI = "TSWALL"
CELL_VOX = 48
CELL_PX = 128
# A joined arm runs to the cell boundary and stops. It used to overshoot into the
# neighbour to hide rounding gaps between two walls, but that arm is plainly visible
# when the neighbour is a component tower rather than more wall, so the arm now ends
# flush: two walls still meet with no gap because both reach the same boundary.
OVERSHOOT = 0
CANVAS_W, CANVAS_H = 176, 320          # classic stub 33x60 x 16/3 (176 = 128 + 2 x 8 x 8/3)
PPV = CELL_PX / CELL_VOX
ELEV = 32.0
STRETCH = 1.0 / math.sin(math.radians(ELEV))
TOP, SOUTH, SLOPE = 1.264, 0.619, 0.85  # TS VPL shade of a top / south / mid-slope face

# TS proportions per 128 px cell (measured from a TS screenshot): wall ~53 px tall,
# ~32 px thick; 1 voxel of height = 4.27 screen px after the stretch.
WALL_T, WALL_H, CREST, SKIRT = 20, 12, 5, 2
PIER_T, PIER_D, PIER_H = 24, 5, 15
CAP_LEN = 12

P = {}
def col_index(name, rgb, shade):
    idx = len(P) + 1
    P[name] = (idx, np.array(rgb, dtype=np.float32) / shade)
    return idx
C_FACE = col_index("face", (129, 129, 129), SOUTH)
C_FACE_LO = col_index("face_lo", (97, 97, 97), SOUTH)
C_SEAM = col_index("seam", (70, 70, 70), SOUTH)
C_CREST = col_index("crest", (161, 161, 161), TOP)
C_CREST_SL = col_index("crest_slope", (145, 145, 145), SLOPE)
C_PIER = col_index("pier", (105, 97, 68), SOUTH)
C_PIER_TOP = col_index("pier_top", (149, 133, 80), TOP)
C_CAP = col_index("cap", (137, 137, 137), SLOPE)
C_RUBBLE = col_index("rubble", (90, 88, 84), SLOPE)
PAL = np.zeros((256, 3), dtype=np.float32)
for _n, (_i, _rgb) in P.items():
    PAL[_i] = _rgb


def model_from_grid(occ, col):
    sx, sy, sz = occ.shape
    sec = dict(occ=occ, col=col, nidx=np.zeros_like(col), normal_mode=4, size=(sx, sy, sz),
               min_b=np.array([-sx / 2.0, -sy / 2.0, 0.0]), max_b=np.array([sx / 2.0, sy / 2.0, float(sz)]),
               scale=1.0, transform=None)
    return dict(sections=[sec], palette=PAL, remap=(250, 253))


def box(occ, col, x0, x1, y0, y1, z0, z1, c):
    x0, y0, z0 = max(x0, 0), max(y0, 0), max(z0, 0)
    x1, y1, z1 = min(x1, occ.shape[0]), min(y1, occ.shape[1]), min(z1, occ.shape[2])
    if x1 > x0 and y1 > y0 and z1 > z0:
        occ[x0:x1, y0:y1, z0:z1] = True
        col[x0:x1, y0:y1, z0:z1] = c


def crest_half_width(z):
    half = WALL_T / 2.0
    if z < WALL_H - CREST:
        return half
    k = (z - (WALL_H - CREST) + 1) / float(CREST)
    return half * math.sqrt(max(0.0, 1.0 - k * k)) + 0.5


def slab(occ, col, along, lo, hi, taper_lo=False, taper_hi=False):
    n = occ.shape[0]
    c = n / 2.0
    for t in range(lo, hi):
        hmax = WALL_H
        if taper_lo and t - lo < CAP_LEN:
            hmax = int(round(WALL_H * (t - lo + 1) / float(CAP_LEN)))
        if taper_hi and hi - 1 - t < CAP_LEN:
            hmax = int(round(WALL_H * (hi - t) / float(CAP_LEN)))
        hmax = max(hmax, 1)
        for z in range(hmax):
            hw = crest_half_width(z) if hmax == WALL_H else WALL_T / 2.0 * (0.6 + 0.4 * (1 - z / float(hmax)))
            if z < SKIRT:
                hw += SKIRT - z
            k0, k1 = int(round(c - hw)), int(round(c + hw))
            if hmax < WALL_H:
                cc = C_CAP if z == hmax - 1 else C_FACE
            elif z >= WALL_H - CREST:
                cc = C_CREST if z == hmax - 1 else C_CREST_SL
            else:
                cc = C_FACE if z >= 3 else C_FACE_LO
            for k in range(k0, k1):
                x, y = (t, k) if along == "x" else (k, t)
                if 0 <= x < n and 0 <= y < n:
                    occ[x, y, z] = True
                    col[x, y, z] = cc
    if not (taper_lo or taper_hi):
        s = n // 2
        for z in range(WALL_H - 1):
            hw = crest_half_width(z) + (SKIRT - z if z < SKIRT else 0)
            for k in (int(round(c - hw)), int(round(c + hw)) - 1):
                x, y = (s, k) if along == "x" else (k, s)
                if 0 <= x < n and 0 <= y < n and occ[x, y, z]:
                    col[x, y, z] = C_SEAM


def pier(occ, col, along, lo, hi):
    n = occ.shape[0]
    c = n // 2
    p0, p1 = c - PIER_T // 2, c + PIER_T // 2
    # tan piers, faces and cap (Luke's pick, 2026-09-04): they read as the wall's
    # buttresses rather than more concrete
    if along == "x":
        box(occ, col, lo, hi, p0, p1, 0, PIER_H, C_PIER)
        box(occ, col, lo, hi, p0, p1, PIER_H - 1, PIER_H, C_PIER_TOP)
    else:
        box(occ, col, p0, p1, lo, hi, 0, PIER_H, C_PIER)
        box(occ, col, p0, p1, lo, hi, PIER_H - 1, PIER_H, C_PIER_TOP)


def wall_grid(joins):
    """joins: bitmask N=1 E=2 S=4 W=8 (RA OverlayData convention). The grid is
    padded by OVERSHOOT on every side; joined arms and their piers run past the
    cell edge into that padding so nothing gaps at a neighbour or a tower."""
    n = CELL_VOX + 2 * OVERSHOOT
    o = OVERSHOOT
    occ = np.zeros((n, n, PIER_H + 1), dtype=bool)
    col = np.zeros((n, n, PIER_H + 1), dtype=np.uint8)
    c = n // 2
    if joins == 0:
        slab(occ, col, "x", c - 16, c + 16, taper_lo=True, taper_hi=True)
        return occ, col
    ns, ew = joins & 5, joins & 10
    if ns:
        slab(occ, col, "y", 0 if joins & 4 else c - 6, n if joins & 1 else c + 6,
             taper_lo=not (joins & 4) and not ew, taper_hi=not (joins & 1) and not ew)
    if ew:
        slab(occ, col, "x", 0 if joins & 8 else c - 6, n if joins & 2 else c + 6,
             taper_lo=not (joins & 8) and not ns, taper_hi=not (joins & 2) and not ns)
    # piers straddle the cell edge (half in each neighbour; both draw the same pier)
    if joins & 1: pier(occ, col, "y", n - o - PIER_D, n - o)
    if joins & 4: pier(occ, col, "y", o, o + PIER_D)
    if joins & 2: pier(occ, col, "x", n - o - PIER_D, n - o)
    if joins & 8: pier(occ, col, "x", o, o + PIER_D)
    return occ, col


def damage(occ, col, stage, seed):
    """Stage 1: crest chipped, faces darkened. Stage 2: crest gone in patches, rubble tone."""
    if stage == 0:
        return occ, col
    rng = np.random.default_rng(seed)
    occ = occ.copy(); col = col.copy()
    n = occ.shape[0]
    top_layers = 3 if stage == 1 else 6
    holes = int(n * n * (0.02 if stage == 1 else 0.05))
    for _ in range(holes):
        x, y = rng.integers(0, n, 2)
        zs = np.nonzero(occ[x, y])[0]
        if len(zs) == 0:
            continue
        zt = zs.max()
        r = rng.integers(2, 4)
        box_occ = slice(max(0, zt - top_layers + 1), zt + 1)
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                xx, yy = x + dx, y + dy
                if 0 <= xx < n and 0 <= yy < n:
                    occ[xx, yy, box_occ] = False
    # newly exposed tops read as rubble
    above = np.zeros_like(occ); above[:, :, :-1] = occ[:, :, 1:]
    exposed = occ & ~above & np.isin(col, (C_FACE, C_FACE_LO, C_CREST_SL, C_SEAM))
    col[exposed] = C_RUBBLE
    if stage == 2:
        col[np.isin(col, (C_FACE,))] = C_FACE_LO
    return occ, col


def render(occ, col):
    vr.set_elevation(ELEV)
    vr.NORMAL_SOURCE = "geo"
    img, _ = vr.render_frame(model_from_grid(occ, col), 0.0, PPV, (0, 200, 0), 0, canvas=None)
    return img.resize((img.width, int(round(img.height * STRETCH))), Image.LANCZOS)


def on_canvas(tile):
    """Place a render so the model origin (cell centre, ground) sits at the canvas centre."""
    cv = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    cv.paste(tile, (CANVAS_W // 2 - tile.width // 2, CANVAS_H // 2 - tile.height // 2), tile)
    return cv


def tile_block(name, shape):
    return ("\t<Tile>\n\t\t<Key>\n\t\t\t<Name>%s</Name>\n\t\t\t<Shape>%d</Shape>\n\t\t</Key>\n"
            "\t\t<Value>\n\t\t\t<Frames>\n\t\t\t\t<Frame>%s\\%s-%04d.tga</Frame>\n\t\t\t</Frames>\n\t\t</Value>\n\t</Tile>\n"
            % (name, shape, name.lower(), name.lower(), shape))


def patch_tileset(xml_path, name, count):
    import re
    xml = open(xml_path, encoding="utf-8").read()
    pat = re.compile(r"\t<Tile>\n\t\t<Key>\n\t\t\t<Name>" + re.escape(name) + r"</Name>.*?</Tile>\n", re.S)
    xml, removed = pat.subn("", xml)
    idx = xml.rindex("</Tiles>")
    xml = xml[:idx] + "".join(tile_block(name, s) for s in range(count)) + xml[idx:]
    open(xml_path, "w", encoding="utf-8").write(xml)
    print(f"patched {os.path.basename(xml_path)}: {name} -> {count} tiles (replaced {removed})")


def pack():
    frames = []
    for stage in range(3):
        for joins in range(16):
            occ, col = wall_grid(joins)
            occ, col = damage(occ, col, stage, seed=1000 * stage + joins)
            frames.append(on_canvas(render(occ, col)))
    os.makedirs(STRUCT_DIR, exist_ok=True)
    low = INI.lower()
    out_zip = f"{STRUCT_DIR}/{INI}.ZIP"
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for i, cv in enumerate(frames):
            bbox = cv.getbbox() or (0, 0, CANVAS_W, CANVAS_H)
            crop = cv.crop(bbox)
            buf = io.BytesIO(); crop.save(buf, format="TGA")
            z.writestr(f"{low}-{i:04d}.tga", buf.getvalue())
            z.writestr(f"{low}-{i:04d}.meta",
                       json.dumps({"size": [CANVAS_W, CANVAS_H], "crop": [bbox[0], bbox[1], bbox[2], bbox[3]]}))
    print(f"wrote {out_zip} ({len(frames)} frames)")
    patch_tileset(TILESET, INI, len(frames))
    dims = json.load(open(STUB_MANIFEST)) if os.path.exists(STUB_MANIFEST) else {}
    dims[INI] = [CANVAS_W * 3 // 16, CANVAS_H * 3 // 16]
    json.dump(dims, open(STUB_MANIFEST, "w"), indent=1)
    # cameo from the TS WALLICON (decoded with CAMEO.PAL by ts_rebuild_art.sh / ts_shp.py)
    icon_dir = f"{ART}/shp_wallicon" if ART else ""
    if icon_dir and os.path.isdir(icon_dir):
        icon = Image.open(f"{icon_dir}/frame-0000.png").convert("RGBA")
        big = icon.resize((icon.width * 8, icon.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
        big.save(f"{ICON_DIR}/BuildIcon_TS_Wall.tga")
        print(f"wrote {ICON_DIR}/BuildIcon_TS_Wall.tga")
    else:
        print("no shp_wallicon in TS_ART_DIR: cameo not written")


def preview(path):
    W, H = 6, 3
    g = Image.new("RGBA", (W * CELL_PX, H * CELL_PX), (150, 110, 70, 255))
    layout = {(0, 1): 2, (1, 1): 10, (2, 1): 10 | 4, (2, 2): 1, (3, 1): 8 | 2, (4, 1): 8, (0, 2): 0, (5, 0): 4, (5, 1): 1 | 4, (5, 2): 1}
    for (x, y) in sorted(layout, key=lambda k: (k[1], k[0])):
        occ, col = wall_grid(layout[(x, y)])
        cv = on_canvas(render(occ, col))
        g.paste(cv, (x * CELL_PX + CELL_PX // 2 - CANVAS_W // 2, y * CELL_PX + CELL_PX // 2 - CANVAS_H // 2), cv)
    g.save(path); print("wrote", path)


if __name__ == "__main__":
    if "--preview" in sys.argv:
        preview(sys.argv[sys.argv.index("--preview") + 1])
    else:
        pack()
