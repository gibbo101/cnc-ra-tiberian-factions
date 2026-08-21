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
EA's throw is a FIXED PIXEL DISTANCE, independent of how big the sprite is.
Measured per-column -- the vertical gap between the shadow's lower edge and the
body's own lower edge in the same column -- across nine base-game vehicles
spanning 122px to 228px of body width:

    RA JEEP 126px  -5.5    RA 2TNK 134px  -6.0    RA 4TNK 185px  -6.0
    RA MCV  228px  -7.0    RA HARV 200px  -5.0    TD APC  122px  -5.0
    TD MTNK 133px  -6.0    TD HTNK 185px  -6.0    TD MSAM 128px  -7.0

Body width nearly doubles across that set and the throw does not move: it is a
constant, not a ratio. Visible shadow runs 6-12% of body pixel area throughout.

Note the SIGN. EA's shadow tucks UNDER the hull and stops short of its bottom
edge; the shadow's bbox sits inside the body's bbox on all four sides. So EA is
not baking a full-size translated copy of the body -- a translation can only
ever push the silhouette past the hull, never inside it. What the eye actually
reads is the thin contact band, ~6px thick, that escapes along the lower edge,
and a small offset silhouette reproduces that band closely enough at this size.

Sizing the throw off the sprite instead of fixing it is what broke: our TS
sprites run up to 301px wide against RA's largest at 228, so a 12%-of-width
throw gave the Mammoth Mk. II a 41px overhang where a TD tank has a 6px tuck.
Luke's verdict on that round: sticks out far too much, the Mk. II looks like it
is floating, and any TS unit stood next to a TD unit looks ridiculous. Alpha was
never the problem in either round -- 191 pure black is what EA bakes, and it is
what we ship.

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

# ABSOLUTE PIXELS, applied to every unit whatever its size. Do not re-express
# these as a fraction of the sprite: two rounds were rejected in play for doing
# exactly that, and the base-game measurement in the docstring above is flat
# across a 2x range of body widths. A fraction also punishes our biggest art
# hardest, which is the opposite of what the eye wants -- the Mk. II is the unit
# most often parked beside a TD tank.
#
# dy 6 puts the visible contact band at EA's own thickness; dx 2 keeps EA's
# roughly 3:1 down-to-sideways lean. Measured result on the real art:
#
#     unit      before            after       EA's range
#     TSHMEC    +41px / 24%    +6px /  5%     ~6px / 6-12%
#     TSAPC     +30px / 27%    +6px /  6%
#     TSTITN    +18px / 22%    +6px /  9%
EA_DX = 2
EA_DY = 6
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
        process(u, dry)
