#!/usr/bin/env python3
"""Regenerate the Nod Stealth Generator HD art (TDSTEAL.ZIP / TDSTEALMAKE.ZIP)
at higher quality: hq4x pixel-art upscaling instead of NEAREST+LANCZOS.

Recreates the shipped frame structure exactly (so nothing engine-side moves):
  TDSTEAL.ZIP      32 frames, 256x128 canvas:
                     0-15  healthy base (NTSTLH f0) + ring anim (NTSTLH_A f0-15)
                     16-31 damaged base (NTSTLH f1) + same ring frames
  TDSTEALMAKE.ZIP  19 frames, 256x128: NTSTLHMK buildup frames 0-18
Transform reverse-engineered from the shipped ZIPs: content maps by
out = (src - (39,35)) * 2.15 + (34,4) — the same affine for all three SHPs
(they share the 144x96 source canvas).

Inputs: $TS_ART_DIR/shp_NTSTLH{,_A,MK}/frame-NNNN.png (ts_shp.py, UNITTEM.PAL — ISOTEM/TEMPERAT are terrain palettes and decode to noise).
"""
import io, json, os, zipfile
from PIL import Image
import hqx

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR")
MOD = "/home/gibbo101/Documents/development/cnc-remastered-mods/cnc-ra-tiberian-factions/resources/remaster_mods/Vanilla_RA"
STRUCT_DIR = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/STRUCTURES"

CANVAS = (256, 128)
SCALE = 2.15
SRC_ANCHOR = (39, 35)
DST_ANCHOR = (34, 4)


def load(dirname, i):
    return Image.open(f"{ART}/{dirname}/frame-{i:04d}.png").convert("RGBA")


def hq_scale(img, factor):
    """hq4x the color (over black), NEAREST+LANCZOS the alpha, then resize
    the 4x result down to the target factor."""
    rgb = Image.new("RGB", img.size, (0, 0, 0))
    rgb.paste(img, (0, 0), img)
    big = hqx.hq4x(rgb).convert("RGBA")
    alpha = img.split()[3].resize((img.width * 4, img.height * 4), Image.LANCZOS)
    big.putalpha(alpha)
    tw, th = round(img.width * factor), round(img.height * factor)
    return big.resize((tw, th), Image.LANCZOS)


def place(src_rgba):
    """Apply the shipped affine: scale by SCALE, anchor-mapped, onto CANVAS."""
    scaled = hq_scale(src_rgba, SCALE)
    out = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    ox = round(DST_ANCHOR[0] - SRC_ANCHOR[0] * SCALE)
    oy = round(DST_ANCHOR[1] - SRC_ANCHOR[1] * SCALE)
    sx, sy = max(0, -ox), max(0, -oy)   # negative-paste corruption guard
    piece = scaled.crop((sx, sy, scaled.width, scaled.height))
    out.paste(piece, (max(0, ox), max(0, oy)), piece)
    return out


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


def write_zip(path, name, frames):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for i, img in enumerate(frames):
            base = f"{name}-{i:04d}"
            b = img.getbbox() or (0, 0, 2, 2)
            z.writestr(base + ".tga", tga_bytes(img.crop(b)))
            z.writestr(base + ".meta", json.dumps(
                {"size": [img.width, img.height], "crop": [b[0], b[1], b[2], b[3]]}))
    print(f"wrote {path} ({len(frames)} frames)")


healthy = load("shp_NTSTLH_u", 0)
damaged = load("shp_NTSTLH_u", 1)
frames = []
for base in (healthy, damaged):
    for r in range(16):
        comp = base.copy()
        comp.alpha_composite(load("shp_NTSTLH_A_u", r))
        frames.append(place(comp))
write_zip(f"{STRUCT_DIR}/TDSTEAL.ZIP", "tdsteal", frames)

mk = [place(load("shp_NTSTLHMK_u", i)) for i in range(19)]
write_zip(f"{STRUCT_DIR}/TDSTEALMAKE.ZIP", "tdstealmake", mk)
print("DONE")
