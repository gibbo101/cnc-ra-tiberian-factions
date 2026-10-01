#!/usr/bin/env python3
"""Pack the Firestorm Wall Section (TS GAFSDF / GTFSDF.SHP) into TSFSDF.ZIP for RA's grid.

TS draws the section in its isometric view, with its lighting baked in; rotating the sprite onto
RA's square grid leaves the lighting lopsided and the dish off-centre. So the section is rebuilt
from TS's own pixels, taken from TS's frames un-projected to an overhead view:

  - the rail is one band -- outline, beam, rungs, beam, outline -- with the SAME TS beam mirrored
    on both sides, so the borders are symmetrical; one rung period of TS's rail is tiled three
    times per half cell, so neighbouring cells meet in phase;
  - east-west and north-south rails are the same thickness (WB), with the rungs the same distance
    apart (the north-south rail is the east-west one turned);
  - a join is a square hub WB wide, centred in the cell, floored with the beam's grey, with TS's
    dish centred in it (cut to a regular octagon, TS's dark line round it); hub corners with no
    rail on either side are chamfered, which gives TS's rounded ends; straight pieces (N+S, E+W)
    have no hub, as in TS;
  - one dark outline round the whole shape, left open where a rail crosses into the next cell.

Frames (TS's order, neighbour bits N1 E2 S4 W8 within each group of 16):
   0-15 normal, 16-31 normal damaged, 32-47 field up, 48-63 field up damaged.
The damaged groups repeat the undamaged art until damaged art is signed off.
Canvas 176x320 with the cell centred, the wall packers' (and the TSFSDF classic stub's) canvas.
TSFSDF.ZIP, its TS_STRUCTURES.XML tile run and BuildIcon_TS_Fsdf.tga go to the TS-Graphics-Pack
(asset_packs.py routes each name).

Inputs: $TS_ART_DIR/shp_gtfsdf (scripts/ts_rebuild_art.sh), $TS_ART_DIR/shp_fspicon (cameo).
Usage: TS_ART_DIR=~/Desktop/ts-art scripts/ts_pack_fsdf.py
License: GPL v3.
"""
import io, json, math, os, sys, zipfile
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS)
import hqx
import asset_packs
import ts_pack_walls as W

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR")
SHP = os.path.join(ART, "shp_gtfsdf")

CELL = 128
CW, CH = W.CANVAS_W, W.CANVAS_H
N = int(1.6 * CELL)             # overhead working canvas: +-0.8 cell round the cell centre
WB = 64                         # rail thickness and hub size, px, the same both ways
DISH = (-0.0234, -0.0180)       # dish centre in the overhead view (cells), by radial symmetry
DISH_HALF = 0.24                # dish crop half-size (cells): the octagonal ring and a little floor
DISH_FRAC = 0.86                # dish diameter as a fraction of the hub
RUNGS_PER_HALF = 3
HI = 4                          # hub supersample


def hq4(img):
    rgb = Image.new("RGB", img.size, (0, 0, 0))
    rgb.paste(img, (0, 0), img)
    big = hqx.hq4x(rgb).convert("RGBA")
    big.putalpha(img.split()[3].resize((img.width * 4, img.height * 4), Image.LANCZOS))
    return big


def plan(i):
    """TS frame i un-projected to an overhead view, CELL px per cell, cell centre at the centre.
    TS's cell ground centre sits at (24, 36) of the 48x48 frame (x4 after hq4x)."""
    src = hq4(Image.open(f"{SHP}/frame-{i:04d}.png").convert("RGBA"))
    a, b, d, e = 96 / CELL, -96 / CELL, 48 / CELL, 48 / CELL
    c = 96 - (a + b) * N / 2
    f = 144 - (d + e) * N / 2
    return np.array(src.transform((N, N), Image.AFFINE, (a, b, c, d, e, f), resample=Image.BILINEAR))


def px(t):
    return int(round(N / 2 + t * CELL))


def solid_span(a, axis, frac=0.5):
    idx = np.where((a[..., 3] >= 128).mean(axis=axis) > frac)[0]
    return idx[0], idx[-1]


def tile_parts(base):
    """One rung period of TS's east-west rail (frame base+10), split into outline / beam / rungs.
    The split rows come from the normal tile's brightness (the beam is the lit band nearest the
    top) and are applied proportionally to the field-up tile."""
    band = plan(10)[:, px(0.05):px(0.225)]
    s0, s1 = solid_span(band, 1)
    L = band[s0:s1 + 1][..., :3].astype(float).mean(-1).mean(1)
    n = len(L)
    top_beam = [i for i in range(n // 2) if L[i] >= 100]
    fr = (top_beam[0] / n, (top_beam[-1] + 1) / n)
    tb = plan(base + 10)[:, px(0.05):px(0.225)]
    q0, q1 = solid_span(tb, 1)
    t = tb[q0:q1 + 1]
    n = t.shape[0]
    a, b = int(round(fr[0] * n)), int(round(fr[1] * n))
    return t[:a], t[a:b], t[b:n - b]


def strips(base):
    outline, beam, rungs = tile_parts(base)
    tile = Image.fromarray(np.concatenate([outline, beam, rungs, beam[::-1], outline[::-1]], axis=0))
    strip = Image.new("RGBA", (tile.width * RUNGS_PER_HALF, tile.height))
    for k in range(RUNGS_PER_HALF):
        strip.paste(tile, (k * tile.width, 0))
    ew = strip.resize((CELL // 2, WB), Image.LANCZOS)
    ns = ew.rotate(90, expand=True)     # CCW: the tile's south edge ends up on the east side
    return ew, ns, beam, outline


def octagon(size, c):
    return [(c, 0), (size - c, 0), (size, c), (size, size - c), (size - c, size), (c, size), (0, size - c), (0, c)]


def hub(base, joins, beam, line_rgb):
    n = WB * HI
    floor = Image.new("RGBA", (n, n))
    bt = Image.fromarray(beam).resize((beam.shape[1] * HI // 2, beam.shape[0] * HI // 2), Image.LANCZOS)
    for y in range(0, n, bt.height):
        for x in range(0, n, bt.width):
            floor.paste(bt, (x, y))
    floor = floor.filter(ImageFilter.GaussianBlur(HI * 1.5))   # the beam's grey, without its repeating flecks
    p = plan(base)
    d = p[px(DISH[1] - DISH_HALF):px(DISH[1] + DISH_HALF), px(DISH[0] - DISH_HALF):px(DISH[0] + DISH_HALF)]
    dn = int(n * DISH_FRAC)
    dish = Image.fromarray(d).resize((dn, dn), Image.LANCZOS)
    mask = Image.new("L", (dn, dn), 0)
    ImageDraw.Draw(mask).polygon(octagon(dn - 1, dn * 0.29), fill=255)
    dish.putalpha(ImageChops.multiply(dish.split()[3], mask))
    ring = Image.new("RGBA", (dn, dn), (0, 0, 0, 0))
    ImageDraw.Draw(ring).polygon(octagon(dn - 1, dn * 0.29), outline=line_rgb + (255,), width=HI * 2)
    dish.alpha_composite(ring)
    floor.alpha_composite(dish, ((n - dn) // 2, (n - dn) // 2))
    c = n * 0.28
    pts = []
    pts += [(0, 0)] if (joins & 1 or joins & 8) else [(0, c), (c, 0)]
    pts += [(n, 0)] if (joins & 1 or joins & 2) else [(n - c, 0), (n, c)]
    pts += [(n, n)] if (joins & 4 or joins & 2) else [(n, n - c), (n - c, n)]
    pts += [(0, n)] if (joins & 4 or joins & 8) else [(c, n), (0, n - c)]
    m = Image.new("L", (n, n), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    floor.putalpha(ImageChops.multiply(floor.split()[3], m))
    return floor.resize((WB, WB), Image.LANCZOS)


def erode(mask, r):
    return np.array(Image.fromarray(mask.astype(np.uint8) * 255).filter(ImageFilter.MinFilter(2 * r + 1))) > 0


def build(base):
    ew, ns, beam, outline = strips(base)
    line_rgb = tuple(int(v) for v in outline[..., :3].reshape(-1, 3).mean(0))
    cx, cy = CW // 2, CH // 2
    left, top = cx - WB // 2, cy - WB // 2
    frames = []
    for joins in range(16):
        cv = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        if joins & 2:
            cv.alpha_composite(ew, (cx, top))
        if joins & 8:
            cv.alpha_composite(ew, (cx - CELL // 2, top))
        if joins & 4:
            cv.alpha_composite(ns, (left, cy))
        if joins & 1:
            cv.alpha_composite(ns, (left, cy - CELL // 2))
        if joins not in (5, 10):
            cv.alpha_composite(hub(base, joins, beam, line_rgb), (left, top))
        a = np.array(cv)
        U = a[..., 3] >= 128
        Ux = U.copy()                       # rails run on past the cell edge: their ends stay open
        if joins & 2:
            Ux[top:top + WB, cx:] = True
        if joins & 8:
            Ux[top:top + WB, :cx] = True
        if joins & 4:
            Ux[cy:, left:left + WB] = True
        if joins & 1:
            Ux[:cy, left:left + WB] = True
        a[Ux & ~erode(Ux, 1) & U, :3] = line_rgb
        a[..., 3] = np.where(U, 255, 0)
        a[:, :cx - CELL // 2, 3] = 0
        a[:, cx + CELL // 2:, 3] = 0
        a[:cy - CELL // 2, :, 3] = 0
        a[cy + CELL // 2:, :, 3] = 0
        frames.append(Image.fromarray(a))
    return frames


def main():
    normal, live = build(0), build(32)
    frames = normal + normal + live + live
    out_zip = asset_packs.art_zip("TSFSDF", "STRUCTURES")
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for i, cv in enumerate(frames):
            bbox = cv.getbbox() or (0, 0, CW, CH)
            buf = io.BytesIO()
            cv.crop(bbox).save(buf, format="TGA")
            z.writestr(f"tsfsdf-{i:04d}.tga", buf.getvalue())
            z.writestr(f"tsfsdf-{i:04d}.meta", json.dumps({"size": [CW, CH], "crop": list(bbox)}))
    print(f"wrote {out_zip} ({len(frames)} frames)")
    W.patch_tileset(asset_packs.tileset_xml("TSFSDF", "STRUCTURES"), "TSFSDF", len(frames))

    icon = os.path.join(ART, "shp_fspicon", "frame-0000.png")
    if os.path.exists(icon):
        im = Image.open(icon)
        big = im.resize((im.width * 8, im.height * 8), Image.NEAREST).resize((341, 256), Image.LANCZOS)
        big.save(asset_packs.cameo_tga("BuildIcon_TS_Fsdf"))
        print("wrote BuildIcon_TS_Fsdf.tga")


if __name__ == "__main__":
    main()
