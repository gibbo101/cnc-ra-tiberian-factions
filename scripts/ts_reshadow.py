#!/usr/bin/env python3
"""Re-shadow the packed TS unit art to EA's TD/RA baked-shadow convention.

WHY THIS OPERATES ON PACKED ZIPS RATHER THAN RE-RENDERING
---------------------------------------------------------
The shadow is the only thing that changes. Body pixels are preserved
byte-for-byte, so nothing that was dialled against the rendered sprite moves:

  * write_zip's crop is CENTER-SYMMETRIC (crop centre == canvas centre) and the
    launcher anchors the canvas centre at the draw position, so growing or
    shrinking the shadow changes only how much empty margin the crop carries.
    The body's on-screen position is invariant.
  * TSHVR's rack seat table (udata.cpp Hover_Rack_Seat) is derived from the
    TURRET frames' content centroids, and turret frames carry no shadow at all.
    A body-shadow change cannot reach it.

Re-rendering would risk both of those. This pass cannot.

THE CONVENTION (measured, not guessed)
--------------------------------------
EA bakes every ground vehicle's shadow as an offset copy of its silhouette, pure
black at alpha 191, softened at the edges, and the launcher draws only what is at
alpha 128 or more. On those pixels EA's Mammoths (RA 4TNK, TD HTNK) throw about
3.8 classic px down and 4.8 across, covering 19% of the hull; the medium tanks
(2TNK, MTNK) throw about two thirds as far. Our vehicles are
Mammoth-sized (26-37 classic px wide), so drop_shadow is fitted to the Mammoths:
offset (4, 22) at 8 canvas px per classic px, blurred by 3. One fixed offset for
every unit: a throw sized off the sprite gave the 48-wide C&C3 Mammoth and the
walkers shadows that float.

Usage:  ts_reshadow.py [--dry-run] [UNIT ...]
"""
import io, json, os, sys, zipfile
from PIL import Image, ImageFilter

import asset_packs

# Canvas px at 8 per classic px; the docstring has the measurement they are fitted to.
EA_DX = 4
EA_DY = 22
EA_ALPHA = 191
# Gaussian radius in canvas px: EA's soft edge.
EA_BLUR = 3

# Per-unit overrides, in packed-canvas pixels. The Hover MLRS was the one unit
# Luke passed at the longer TD-derived throw, and that is not an accident: it is
# the roster's only true hover unit, so a shadow thrown further than a ground
# hull's reads as float rather than as error. Keep its approved values.
OFFSET_OVERRIDE = {"TSHVR": (5, 17)}

# The HD units are shadowed by their packer (scripts/ts_pack_hd_buildings.py, which uses drop_shadow
# for its vehicles) and are never re-shadowed here; the pass re-shadows the C&C3 tanks' packed ZIPs.
UNITS = ["C3MK3", "C3PRED"]

# Whether a unit currently carries a shadow is DETECTED from the art (a flat
# pure-black alpha plateau), never hardcoded -- that keeps the pass idempotent
# and safe to re-run while a tuning round converges, and it preserves each
# unit's body/turret frame split without listing frame ranges.


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


def uncrop(img, meta):
    """Rebuild the full pack canvas from a cropped frame + its meta."""
    W, H = meta["size"]
    x0, y0 = meta["crop"][0], meta["crop"][1]
    full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    full.paste(img, (x0, y0))
    return full


def find_shadow_alpha(frames):
    """The flat pure-black alpha plateau a previous drop_shadow left behind."""
    hist = {}
    for im in frames:
        px = im.load()
        for y in range(0, im.height, 2):
            for x in range(0, im.width, 2):
                r, g, b, a = px[x, y]
                if a and a < 250 and r < 8 and g < 8 and b < 8:
                    hist[a] = hist.get(a, 0) + 1
    if not hist:
        return None
    a, n = max(hist.items(), key=lambda kv: kv[1])
    return a if n >= 100 else None


def strip_shadow(im, alpha):
    """Drop exactly the pixels a flat-alpha black silhouette contributed."""
    out = im.copy()
    px = out.load()
    n = 0
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a == alpha and r == 0 and g == 0 and b == 0:
                px[x, y] = (0, 0, 0, 0)
                n += 1
    return out, n


def drop_shadow(frame, dx, dy, alpha=EA_ALPHA, blur=EA_BLUR):
    """Offset-silhouette shadow, softened by blur, composited UNDER the sprite.

    Bottom-anchored variants (whole-hull squash, bottom-slice) are FALSIFIED:
    both collapse into a detached floating nub at diagonal facings, because a
    diagonal hull's bbox bottom is a single pointy corner. The full silhouette
    offset down-and-south hugs the whole lower edge at every facing.
    """
    sil = Image.new("L", frame.size, 0)
    sil.paste(frame.split()[3].point(lambda a: alpha if a > 0 else 0), (dx, dy))
    if blur:
        sil = sil.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    out.putalpha(sil)
    out.alpha_composite(frame)
    return out


def write_zip(path, name, frames):
    """Identical contract to the packers: center-symmetric crop + meta."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for i, img in enumerate(frames):
            base = f"{name}-{i:04d}"
            W, H = img.width, img.height
            bb = img.getbbox() or (W // 2 - 1, H // 2 - 1, W // 2 + 1, H // 2 + 1)
            x0 = min(bb[0], W - bb[2])
            y0 = min(bb[1], H - bb[3])
            b = (x0, y0, W - x0, H - y0)
            z.writestr(base + ".tga", tga_bytes(img.crop(b)))
            z.writestr(base + ".meta", json.dumps(
                {"size": [W, H], "crop": [b[0], b[1], b[2], b[3]]}))


def process(unit, dry_run):
    path = asset_packs.art_zip(unit, "UNITS")
    if not os.path.exists(path):
        print(f"{unit}: MISSING {path}")
        return
    src = zipfile.ZipFile(path)
    names = sorted(n[:-4] for n in src.namelist() if n.endswith(".tga"))
    stem = names[0].rsplit("-", 1)[0]

    full, metas = [], []
    for n in names:
        meta = json.loads(src.read(n + ".meta"))
        img = Image.open(io.BytesIO(src.read(n + ".tga"))).convert("RGBA")
        metas.append(meta)
        full.append(uncrop(img, meta))
    src.close()

    old_alpha = find_shadow_alpha(full)

    bodies, had = [], []
    for im in full:
        if old_alpha is not None:
            stripped, n = strip_shadow(im, old_alpha)
            bodies.append(stripped)
            had.append(n > 50)
        else:
            bodies.append(im)
            had.append(True)

    # One offset for the whole unit (a per-frame bbox would make the throw
    # wobble facing to facing), sized from the MEDIAN per-frame body bbox.
    # NOT the union: for a 256-frame walker the union spans every leg position
    # at every facing and is far larger than any real frame, which threw the
    # mechs' shadows clear of their feet. EA's convention was measured per
    # frame, so the median is the matching statistic.
    # A unit with no shadow layer at all (TSMCV) leaves nothing to detect, and a
    # sparse stray-pixel plateau can mark every frame as unshadowed. Either way,
    # "no frame carries a shadow" means this is a body-only unit that should
    # simply get one on every frame -- not a reason to fail.
    if not any(had):
        had = [True] * len(bodies)

    ws, hs = [], []
    for im, h in zip(bodies, had):
        if not h:
            continue
        bb = im.getbbox()
        if bb:
            ws.append(bb[2] - bb[0])
            hs.append(bb[3] - bb[1])
    ws.sort()
    hs.sort()
    bw, bh = ws[len(ws) // 2], hs[len(hs) // 2]
    if unit in OFFSET_OVERRIDE:
        dx, dy = OFFSET_OVERRIDE[unit]
    else:
        dx, dy = EA_DX, EA_DY

    canvas = full[0].width
    clipped = 0
    out = []
    for im, h in zip(bodies, had):
        if not h:
            out.append(im)
            continue
        sh = drop_shadow(im, dx, dy)
        bb = sh.getbbox()
        if bb and (bb[2] > canvas or bb[3] > sh.height):
            clipped += 1
        out.append(sh)

    n_sh = sum(1 for h in had if h)
    old = f"alpha {old_alpha}" if old_alpha else "NO shadow"
    warn = f"   ⚠ {clipped} frames clip the canvas" if clipped else ""
    print(f"{unit:8} body {bw}x{bh}  ->  offset ({dx},{dy}) alpha {EA_ALPHA}   "
          f"[was {old}]  {n_sh}/{len(out)} frames{warn}")

    if not dry_run:
        write_zip(path, stem, out)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    for u in (args or UNITS):
        if asset_packs.hd_owned(u):
            print(f"{u}: skipped, ts_pack_hd_buildings.py shadows it")
            continue
        process(u, dry)
