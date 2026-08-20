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
Every EA TD/RA HD ground vehicle bakes its shadow as an OFFSET SILHOUETTE of
the body -- the same mechanism our packers already use. Fitting a shifted copy
of the body against the actual shadow region scores IoU 0.72-0.88 across EA's
whole vehicle set, so the mechanism was never the problem; the tuning was.

Measured across EA's TD vehicle art (TDHTNK/TDMTNK/TDLTNK/TDAPC/TDJEEP/TDBGGY/
TDARTY/TDFTNK/TDSTNK/TDBIKE/TDHARV/TDMCV/TDMLRS/TDMSAM):

    offset dx ~= 0.042 * body width      dy ~= 0.180 * body height
    dy/dx ~= 3   (light is high and near-south, only slightly east)
    shadow alpha 191 (modal; EA also uses 153 and 179)

Our TS art sat at dy/dx ~= 1.3 -- a 45-degree diagonal throw, which reads as a
hard black duplicate of the hull rather than as ground shade -- and at alpha
130, barely over the launcher's ~128 cutoff.

Three TS units were worse than mistuned and rendered NO shadow at all:
TSHARV (alpha 66) and TSHMEC (alpha 71) both sat under the launcher's alpha
cutoff and were discarded at draw time; TSMCV had no shadow layer whatsoever.

Usage:  ts_reshadow.py [--dry-run] [UNIT ...]
"""
import io, json, os, sys, zipfile
from PIL import Image

MOD = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "..", "resources", "remaster_mods", "Vanilla_RA"))
UNITS_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS"

# Both offsets scale off sprite WIDTH, never height. Width tracks the ground
# footprint; height does not, because an isometric sprite's height also carries
# how tall the thing stands. Sizing dy off height threw the Wolverine's and
# Mk. II's shadows clear of their feet while looking correct on every low hull.
#
# These are measured off the BASE GAME's own RA art, pulled from
# TEXTURES_RA_SRGB.MEG (2TNK/3TNK/MCV/JEEP), which is the standard our units
# are actually seen next to:
#
#     unit     alpha   dx/bw    dy/bw
#     2TNK      191    0.0263   0.1189
#     3TNK      191    0.0277   0.1203
#     MCV       191    0.0278   0.0893
#     JEEP      191    0.0304   0.1216
#
# A first pass used means taken off TD art instead (0.042 / 0.138) and Luke's
# in-game verdict was "way over done" on every ground unit. Alpha was never the
# problem -- 191 pure black is exactly what RA bakes -- the throw was simply too
# long, ~50% too far sideways and ~20% too far down, which inflates the visible
# shadow band by the same proportion.
# The TD Medium Tank is the unit Luke parks the TS roster against as his
# reference, and it independently lands in the same place as the RA sample
# (alpha 191, dx/bw 0.0277, dy/bw 0.1205) -- so RA and TD share one convention
# and these fractions ARE that convention.
EA_DX_FRAC = 0.028
EA_DY_FRAC = 0.120
EA_ALPHA = 191

# Per-unit overrides, in packed-canvas pixels. The Hover MLRS was the one unit
# Luke passed at the longer TD-derived throw, and that is not an accident: it is
# the roster's only true hover unit, so a shadow thrown further than a ground
# hull's reads as float rather than as error. Keep its approved values.
OFFSET_OVERRIDE = {"TSHVR": (5, 17)}

UNITS = ["TSAPC", "TSHARV", "TSHMEC", "TSHVR", "TSMCV", "TSSMEC", "TSSONIC", "TSTITN"]

# Whether a unit currently carries a shadow is DETECTED from the art (a flat
# pure-black alpha plateau), never hardcoded -- that keeps the pass idempotent
# and safe to re-run while a tuning round converges, and it preserves each
# unit's body/turret frame split without listing frame ranges. TSMCV was the
# one unit that started with no shadow layer at all; it has one now, and
# detection picked that up on its own.


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


def drop_shadow(frame, dx, dy, alpha=EA_ALPHA):
    """Offset-silhouette shadow, composited UNDER the sprite.

    Bottom-anchored variants (whole-hull squash, bottom-slice) are FALSIFIED:
    both collapse into a detached floating nub at diagonal facings, because a
    diagonal hull's bbox bottom is a single pointy corner. The full silhouette
    offset down-and-south hugs the whole lower edge at every facing.
    """
    sil = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    mask = frame.split()[3].point(lambda a: alpha if a > 0 else 0)
    black = Image.new("RGBA", frame.size, (0, 0, 0, 255))
    sil.paste(black, (dx, dy), mask)
    out = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    out.alpha_composite(sil)
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
    path = f"{UNITS_DIR}/{unit}.ZIP"
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
        dx, dy = round(EA_DX_FRAC * bw), round(EA_DY_FRAC * bw)

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
        process(u, dry)
