#!/usr/bin/env python3
"""Append the TS Amphibious APC's water hull (apcw.vxl renders) to TSAPC.ZIP as
frames 32-63, keeping the signed-off body frames 0-31 byte-identical.

TS swaps the APC to apcw.vxl -- the same hull sitting low in the water --
whenever its cell is water (OpenTS unit.cpp, AuxVoxel on LAND_WATER); the mod's
UnitClass::Shape_Number adds 32 on water. Render the hull with the SAME camera as
the body (vxl_render.py --frames 32 --px-per-voxel 12 --yaw0 0 --elev 32; the
shipped body render was reproduced to the pixel at elev 32) and pack it with the
body's placement: F_VOX scale, 384 canvas, (7,30) shadow, +8 face fix.

Usage:  ts_pack_tsapc_water.py <renders_apcw dir>
"""
import io, json, os, sys, zipfile
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
MOD = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                   "resources", "remaster_mods", "Vanilla_RA"))
ZIP = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS/TSAPC.ZIP"
XML = f"{MOD}/Data/XML/TILESETS/RA_UNITS.XML"
F_VOX = 6.4 / 12.0
CANVAS = 384
SHADOW = (7, 30)


def safe_paste(dst, src, x, y):
    sx, sy = max(0, -x), max(0, -y)
    if sx or sy:
        src = src.crop((sx, sy, src.width, src.height))
        x, y = max(0, x), max(0, y)
    dst.paste(src, (x, y), src)


def drop_shadow(frame, dx, dy, alpha=191):
    sil = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    mask = frame.split()[3].point(lambda a: alpha if a > 0 else 0)
    black = Image.new("RGBA", frame.size, (0, 0, 0, 255))
    sil.paste(black, (dx, dy), mask)
    out = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    out.alpha_composite(sil)
    out.alpha_composite(frame)
    return out


def water_frames(rdir):
    raw = []
    for i in range(32):
        im = Image.open(f"{rdir}/frame-{i:04d}.png").convert("RGBA")
        scaled = im.resize((round(im.width * F_VOX), round(im.height * F_VOX)), Image.LANCZOS)
        fr = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
        safe_paste(fr, scaled, round(CANVAS / 2 - scaled.width / 2), round(CANVAS / 2 - scaled.height / 2))
        raw.append(drop_shadow(fr, *SHADOW))
    return [raw[(i + 8) % 32] for i in range(32)]


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


def main():
    rdir = sys.argv[1]
    src = zipfile.ZipFile(ZIP)
    body = [(n, src.read(n)) for n in src.namelist() if n.split("-")[1][:4].isdigit() and int(n.split("-")[1][:4]) < 32]
    water = water_frames(rdir)
    tmp = ZIP + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for n, data in body:
            z.writestr(n, data)
        for i, img in enumerate(water):
            base = f"tsapc-{32 + i:04d}"
            W, H = img.width, img.height
            bb = img.getbbox() or (W // 2 - 1, H // 2 - 1, W // 2 + 1, H // 2 + 1)
            x0 = min(bb[0], W - bb[2]); y0 = min(bb[1], H - bb[3])
            b = (x0, y0, W - x0, H - y0)
            z.writestr(base + ".tga", tga_bytes(img.crop(b)))
            z.writestr(base + ".meta", json.dumps({"size": [W, H], "crop": [b[0], b[1], b[2], b[3]]}))
    src.close()
    os.replace(tmp, ZIP)
    from ts_gen_sonicwave import patch_tileset
    patch_tileset(XML, "TSAPC", 64)
    print(f"TSAPC.ZIP: {len(body)//2} body frames kept + 32 water frames appended")


if __name__ == "__main__":
    main()
