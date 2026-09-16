#!/usr/bin/env python3
"""Give the packed Titan (TSTITN) and Wolverine (TSSMEC) zips Tiberian Sun's own cast shadows.
Their SHPs carry a shadow frame for every body frame (MMCH from 152, SMECH from 136). This pass
opens the shipped zip, drops the synthetic offset-silhouette shadow the packer laid down (a flat
alpha-191 black plateau, the same detection ts_reshadow.py uses), and composites the TS shadow
frame under each body frame through the packer's own transform, so nothing about the body moves.
Turret frames carry no shadow. Run after any repack of either unit; ts_reshadow.py skips both.
Inputs (TS_ART_DIR): shp_mmch, shp_smech (ts_shp.py with UNITTEM.PAL). License: GPL v3.
"""
import io
import json
import os
import sys
import zipfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR")
MOD = os.environ.get("TF_MOD_DIR", os.path.normpath(os.path.join(HERE, "..", "resources/remaster_mods/Vanilla_RA")))
UNITS_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS"
SHADOW_RGB = (170, 0, 170)   # ts_shp.py's decode of the TS shadow index
SHADOW_ALPHA = 128           # the Juggernaut's, the house convention for TS-own shadows
OLD_ALPHA = 191              # the packers' drop_shadow plateau
F = 6.4                      # the walker house factor, both packers
WALK_PICK = [0, 1, 2, 4, 5, 6, 8, 9, 10, 11, 13, 14]   # ts_pack_walkers.py's 12 of the Titan's 15


def shp(stem, i):
    return Image.open(f"{ART}/shp_{stem}/frame-{i:04d}.png").convert("RGBA")


def shadow_layer(sh, canvas, ox, oy):
    """The TS shadow frame as translucent black, scaled by F and placed like its body frame."""
    px = sh.load()
    mask = Image.new("L", sh.size, 0)
    mp = mask.load()
    for y in range(sh.height):
        for x in range(sh.width):
            r, g, b, a = px[x, y]
            if a and (r, g, b) == SHADOW_RGB:
                mp[x, y] = 255
    big = mask.resize((round(sh.width * F), round(sh.height * F)), Image.LANCZOS)
    big = big.point(lambda v: SHADOW_ALPHA if v > 96 else 0)
    out = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    black = Image.new("RGBA", big.size, (0, 0, 0, 255))
    black.putalpha(big)
    # negative offsets: pre-crop (Pillow's masked paste corrupts them)
    sx, sy = max(0, -ox), max(0, -oy)
    if sx or sy:
        black = black.crop((sx, sy, black.width, black.height))
        ox, oy = max(0, ox), max(0, oy)
    out.paste(black, (ox, oy), black)
    return out


def strip_old(im):
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a == OLD_ALPHA and r == 0 and g == 0 and b == 0:
                px[x, y] = (0, 0, 0, 0)
    return im


def uncrop(img, meta):
    W, H = meta["size"]
    full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    full.paste(img, (meta["crop"][0], meta["crop"][1]))
    return full


def write_zip(path, name, frames):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for i, img in enumerate(frames):
            base = f"{name}-{i:04d}"
            w, h = img.size
            bb = img.getbbox() or (w // 2 - 1, h // 2 - 1, w // 2 + 1, h // 2 + 1)
            x0, y0 = min(bb[0], w - bb[2]), min(bb[1], h - bb[3])
            box = (x0, y0, w - x0, h - y0)
            buf = io.BytesIO()
            img.crop(box).save(buf, format="TGA")
            z.writestr(base + ".tga", buf.getvalue())
            z.writestr(base + ".meta", json.dumps({"size": [w, h], "crop": list(box)}))
    print(f"wrote {path} ({len(frames)} frames)")


def load_zip(name):
    z = zipfile.ZipFile(f"{UNITS_DIR}/{name}.ZIP")
    names = sorted(n[:-4] for n in z.namelist() if n.endswith(".tga"))
    frames = []
    for n in names:
        meta = json.loads(z.read(n + ".meta"))
        frames.append(uncrop(Image.open(io.BytesIO(z.read(n + ".tga"))).convert("RGBA"), meta))
    return frames


def titan():
    """TSTITN: 8 facings x 12 walk (WALK_PICK of MMCH's 15) + 32 turret; anchor (47.5, 55) -> (224, 386)."""
    canvas = 448
    ox, oy = round(224 - 47.5 * F), round(386 - 55.0 * F)
    frames = load_zip("TSTITN")
    out = []
    for k, fr in enumerate(frames):
        body = strip_old(fr)
        if k < 96:
            f, s = k // 12, WALK_PICK[k % 12]
            src = ((8 - f) % 8) * 15 + s
            comp = shadow_layer(shp("mmch", 152 + src), canvas, ox, oy)
            comp.alpha_composite(body)
            out.append(comp)
        else:
            out.append(body)
    write_zip(f"{UNITS_DIR}/TSTITN.ZIP", "tstitn", out)


def wolverine():
    """TSSMEC: 8 x 12 walk + 8 x 4 firing (SMECH 104+); feet-row anchor from the walk union."""
    canvas = 384
    ux0, uy0, ux1, uy1 = 1e9, 1e9, -1e9, -1e9
    for i in range(96):
        b = shp("smech", i).getbbox()
        if b:
            ux0, uy0, ux1, uy1 = min(ux0, b[0]), min(uy0, b[1]), max(ux1, b[2]), max(uy1, b[3])
    feet_src = uy1
    feet_dst = canvas / 2 + (uy1 - uy0) * F / 2
    ox, oy = round(canvas / 2 - 47.5 * F), round(feet_dst - feet_src * F)
    frames = load_zip("TSSMEC")
    out = []
    for k, fr in enumerate(frames):
        body = strip_old(fr)
        if k < 96:
            f, s = k // 12, k % 12
            src = ((8 - f) % 8) * 12 + s
        else:
            f, s = (k - 96) // 4, (k - 96) % 4
            src = 104 + ((8 - f) % 8) * 4 + s
        comp = shadow_layer(shp("smech", 136 + src), canvas, ox, oy)
        comp.alpha_composite(body)
        out.append(comp)
    write_zip(f"{UNITS_DIR}/TSSMEC.ZIP", "tssmec", out)


if __name__ == "__main__":
    which = sys.argv[1:] or ["TSTITN", "TSSMEC"]
    if "TSTITN" in which:
        titan()
    if "TSSMEC" in which:
        wolverine()
