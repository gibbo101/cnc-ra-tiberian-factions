#!/usr/bin/env python3
"""Synthesise a 16-facing GDI Gunboat (TDBOAT) tileset by rotating the TD hull.

The TD gunboat only has east/west hull art (see docs). We take ONE clean
gun-pointing-forward east frame, mute its baked cast-shadow, and rotate it to
all 16 RA facings, so the gunboat can render as a normal 16-facing RA vessel
(VesselClass::Shape_Number returns Dir_To_16(PrimaryFacing) for it).

Tweakable knobs are at the top — facing orientation almost always needs a nudge
after seeing it move in-game (rotate direction / base angle / frame order).

License: GPL v3.
"""
import json, os, struct, zipfile
from PIL import Image

# ---- knobs (tweak after in-game look) -------------------------------------
SRC_DIR      = "/tmp/tdboat"           # extracted TDBOAT.ZIP frames
# TD drew only east + west hull art, so we rotate the NEARER base for each facing
# (never more than +/-90deg) — rotating one base a full 180deg flips it upside down.
BASE_FRAME_EAST = 120                  # east hull, gun forward (96 + BodyShape[8]=24)
BASE_FRAME_WEST = 8                    # west hull, gun forward (0  + BodyShape[24]=8)
N_FACINGS    = 16
ROT_SIGN     = +1                      # +1 = CCW; flip if the whole set turns the wrong way
CANVAS       = 280                     # square canvas (fits the long hull at any angle)
# shadow mute: dark + semi-transparent halo pixels -> drop alpha
SHADOW_BRIGHT = 70
SHADOW_ALPHAMAX = 205
SHADOW_KEEP   = 0.0
OUT_ZIP      = "resources/remaster_mods/Vanilla_RA/Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS/TDBOAT.ZIP"
# ---------------------------------------------------------------------------


def mute_shadow(im):
    im = im.copy(); px = im.load(); W, H = im.size
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if a and max(r, g, b) < SHADOW_BRIGHT and a < SHADOW_ALPHAMAX:
                px[x, y] = (r, g, b, int(a * SHADOW_KEEP))
    return im


def reconstruct_full(frame):
    """Place the cropped TGA back into its full canvas using the .meta crop."""
    meta = json.load(open(f"{SRC_DIR}/tdboat-{frame:04d}.meta"))
    cw, ch = meta["size"]
    x0, y0, x1, y1 = meta["crop"]
    tga = Image.open(f"{SRC_DIR}/tdboat-{frame:04d}.tga").convert("RGBA")
    canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    canvas.paste(tga, (x0, y0), tga)
    return canvas


def squared(frame):
    """Muted, full-canvas hull centred in a big square (unit centre = square centre)."""
    base = mute_shadow(reconstruct_full(frame))
    cw, ch = base.size
    sq = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    sq.paste(base, ((CANVAS - cw) // 2, (CANVAS - ch) // 2), base)
    return sq


def norm(a):
    while a > 180: a -= 360
    while a <= -180: a += 360
    return a


def main():
    east = squared(BASE_FRAME_EAST)   # bow points screen-RIGHT (native heading E = 90deg)
    west = squared(BASE_FRAME_WEST)   # bow points screen-LEFT  (native heading W = 270deg)
    step = 360.0 / N_FACINGS

    tmp = "/tmp/tdboat_rot_out"
    os.makedirs(tmp, exist_ok=True)
    for fobj in os.listdir(tmp):
        os.remove(os.path.join(tmp, fobj))

    # RA vessel body: Shape_Number(gunboat) = Dir_To_16(PrimaryFacing) -> frame s = facing s.
    # facing s heading (compass, 0=N clockwise) = s*step. screen_ccw = 90 - heading.
    # east base bow at screen 0deg -> rot_east = 90 - heading
    # west base bow at screen 180deg -> rot_west = -90 - heading
    # pick the base needing the SMALLER turn (<=90deg) so the deck never flips.
    for s in range(N_FACINGS):
        heading = s * step
        rot_e = norm(90.0 - heading)
        rot_w = norm(-90.0 - heading)
        if abs(rot_w) <= abs(rot_e):          # ties (N,S) -> west, per design
            sq, ang = west, rot_w
        else:
            sq, ang = east, rot_e
        rot = sq.rotate(ROT_SIGN * ang, resample=Image.BICUBIC, expand=False)
        bbox = rot.getbbox()
        if bbox is None:
            bbox = (0, 0, CANVAS, CANVAS)
        crop = rot.crop(bbox)
        crop.save(f"{tmp}/tdboat-{s:04d}.tga")
        meta = {"size": [CANVAS, CANVAS], "crop": [bbox[0], bbox[1], bbox[2], bbox[3]]}
        open(f"{tmp}/tdboat-{s:04d}.meta", "w").write(json.dumps(meta))

    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for s in range(N_FACINGS):
            z.write(f"{tmp}/tdboat-{s:04d}.tga", f"tdboat-{s:04d}.tga")
            z.write(f"{tmp}/tdboat-{s:04d}.meta", f"tdboat-{s:04d}.meta")
    print(f"wrote {OUT_ZIP}: {N_FACINGS} facings (east base {BASE_FRAME_EAST}, "
          f"west base {BASE_FRAME_WEST}, ROT_SIGN={ROT_SIGN}, canvas {CANVAS})")


if __name__ == "__main__":
    main()
