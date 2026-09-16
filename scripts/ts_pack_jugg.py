#!/usr/bin/env python3
"""Package the TS Juggernaut (Firestorm) into the mod tree as TSJUGG.ZIP, 202 frames:
  0-119    walk: 8 facings (CCW from N) x 15 frames, JUGGER.SHP poses with their own shadows
  120-151  deployed at rest: DJUGG base + DJUGG_A cabin (32 facings, CCW from N, swinging behind
           its pivot) + the DJUGGBAR voxel barrels level, seated in the cabin's side
  152-183  deployed aiming: the same with the barrels pitched 45 degrees (TS raises BarrelPitch
           onto a target and drops it back to level after the shot)
  184-201  the DJUGGMK deploy ladder (18 frames), played backwards to pack up
plus BuildIcon_TS_Juggernaut.tga, the base RA_TSJUGG sidebar entry and the ModText rows.
Scale: TS SHP px x 6.4 (the walker house factor, hq4x then LANCZOS) on a 448 canvas
(ShapeSize 56); the barrel render (12 px/voxel) scales by 6.4/12. Every source canvas is
placed by its centre on the tileset canvas centre (model space, the launcher's anchor).
Inputs (set TS_ART_DIR): shp_jugger, shp_djugg, shp_djugg_a, shp_djuggmk (ts_shp.py with
UNITTEM.PAL), shp_juggicon (CAMEO.PAL, --no-remap), renders_djuggbar and renders_djuggbar_p45
(scripts/ts_render_jugg_barrels.py: level and pitched 45, rear recoil rods dropped; TS rests the
barrels level: StartPitch DIR_E is horizontal in its [64 = horizontal, 0 = vertical] pitch scale).
License: GPL v3.
"""
import math
import os
import sys
from PIL import Image
import hqx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ts_pack_infantry as inf

ART = inf.ART
CANVAS = 448
F = 6.4
F_VOX = 6.4 / 12.0
BARREL_SCALE = F_VOX * 0.75   # TS VoxelBarrelScale=.75
BARREL_LIFT = -32  # canvas px down from the cabin pivot: the bundle's centre sits below the cabin's centre line
BARREL_FWD = 99    # canvas px forward along the facing: the breech sits at the cabin's front, muzzles 29 TS px ahead
PIVOT_DX, PIVOT_DY = 26, -26  # the DJUGG art sits 3.25 TS px east and north of its SHP canvas centre: the cabin's
                              # rotation pivot (its frames' centroids orbit it), so the bundle mounts there
# Forward and lift measured off TS's own pre-rendered deploy frame (DJUGGMK frame 0, SW): bundle centre
# 12 px ahead-left and 2 px below the cabin's centre, which the Firestorm wiki's in-game shot agrees with.
BARREL_SETS = (("renders_djuggbar", "level", 5), ("renders_djuggbar_p45", "aimed", 45))  # rest, then aiming at a target
# The render pitches the bundle about its own origin (mid-length, on its axis). The Juggernaut
# hinges its guns at the breech end instead, so each pitched set is slid so that the bundle's
# rear-bottom corner stays exactly where the rest pose has it. Corner in voxels: x behind the
# origin (the rear slabs the render drops are not part of the drawn bundle), z at its underside.
BARREL_HINGE = (-(23.0 - 6.0), 5.0)
RENDER_ELEV = 30.0   # the barrel renders' camera elevation (heights foreshorten by its cosine)


def frame(stem, i):
    return Image.open(f"{ART}/shp_{stem}/frame-{i:04d}.png").convert("RGBA")


def crisp(img):
    """hq4x then LANCZOS to F, the source canvas centre landing on the tileset canvas centre."""
    rgb = Image.new("RGB", img.size, (0, 0, 0))
    rgb.paste(img, (0, 0), img)
    big = hqx.hq4x(rgb).convert("RGBA")
    big.putalpha(img.split()[3].resize((img.width * 4, img.height * 4), Image.LANCZOS))
    scaled = big.resize((round(img.width * F), round(img.height * F)), Image.LANCZOS)
    out = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    inf.safe_paste(out, scaled, round(CANVAS / 2 - scaled.width / 2), round(CANVAS / 2 - scaled.height / 2))
    return out


def barrel(facing, render_dir="renders_djuggbar", pitch=5.0):
    """The barrel render for a CCW-from-N facing, scaled, its origin set ahead of and below
    the cabin pivot per BARREL_FWD / BARREL_LIFT (screen forward = (-sin, -cos/2) of the
    facing: TS's ground plane is foreshortened by half)."""
    # This voxel's forward axis puts render 0 at NORTH, advancing CCW: index = facing.
    im = Image.open(f"{ART}/{render_dir}/frame-{facing:04d}.png").convert("RGBA")
    im = im.resize((round(im.width * BARREL_SCALE), round(im.height * BARREL_SCALE)), Image.LANCZOS)
    th = math.radians(facing * 11.25)
    # breech pinned: undo the mid-length pivot's drop (sin) and forward creep (1 - cos) at this pitch
    vox = 12 * BARREL_SCALE
    hx, hz = BARREL_HINGE
    def swung(a):   # where the hinge corner lands after the render's pitch about the origin
        return (hx * math.cos(a) - hz * math.sin(a), hx * math.sin(a) + hz * math.cos(a))
    (rx, rz), (ax, az) = swung(math.radians(BARREL_SETS[0][2])), swung(math.radians(pitch))
    back = (ax - rx) * vox
    rise = (rz - az) * math.cos(math.radians(RENDER_ELEV)) * vox
    dx = -math.sin(th) * (BARREL_FWD - back)
    dy = -math.cos(th) * (BARREL_FWD - back) * 0.5 - rise
    out = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    inf.safe_paste(out, im, round(CANVAS / 2 - im.width / 2 + dx + PIVOT_DX),
                   round(CANVAS / 2 - im.height / 2 - BARREL_LIFT + dy + PIVOT_DY))
    return out


def walk_frames():
    out = []
    for f in range(8):                      # out facing f (CCW from N) <- SHP block (8-f)%8 (CW)
        src = (8 - f) % 8
        for s in range(15):
            i = src * 15 + s
            out.append(crisp(inf.with_shadow(frame("jugger", i), frame("jugger", 120 + i))))
    return out


def deployed_frames(render_dir="renders_djuggbar", pitch=5.0):
    base = crisp(inf.with_shadow(frame("djugg", 0), frame("djugg", 3)))
    out = []
    for s in range(32):                     # DJUGG_A runs CCW from N like RA's own art: frame = facing
        turret = crisp(inf.with_shadow(frame("djugg_a", s), frame("djugg_a", 32 + s)))
        bar = barrel(s, render_dir, pitch)
        comp = base.copy()
        if s <= 8 or s >= 24:               # aiming away: barrels behind the cabin
            comp.alpha_composite(bar)
            comp.alpha_composite(turret)
        else:
            comp.alpha_composite(turret)
            comp.alpha_composite(bar)
        out.append(comp)
    return out


def ladder_frames():
    return [crisp(inf.with_shadow(frame("djuggmk", i), frame("djuggmk", 18 + i))) for i in range(18)]


def sheet(frames, path, cols=8, size=224):
    rows = (len(frames) + cols - 1) // cols
    sh = Image.new("RGBA", (size * cols, size * rows), (70, 110, 70, 255))
    for k, fr in enumerate(frames):
        sh.alpha_composite(fr.resize((size, size)), ((k % cols) * size, (k // cols) * size))
    sh.save(path)


def main():
    walk, lad = walk_frames(), ladder_frames()
    dep = []
    for render_dir, _, pitch in BARREL_SETS:
        dep += deployed_frames(render_dir, pitch)
    frames = walk + dep + lad
    assert len(frames) == 202
    inf.write_zip(f"{inf.UNITS_DIR}/TSJUGG.ZIP", "tsjugg", frames)
    inf.patch_tileset("TSJUGG", len(frames))
    inf.cameo("juggicon", "BuildIcon_TS_Juggernaut")
    inf.sidebar("TSJUGG", "BuildIcon_TS_Juggernaut")
    inf.text_rows("TSJUGG", "Juggernaut",
                  "Long-range walking artillery. Sets down to fire three shells and packs up to move.")
    out = os.environ.get("TSJUGG_SHEET")
    if out:
        sheet([walk[f * 15] for f in range(8)] + dep[::4] + lad[::3], out, cols=10)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
