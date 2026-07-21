#!/usr/bin/env python3
"""Render all-facings compass sheets of the packed TS unit tilesets into
~/Desktop/tf-previews/ so art iterations can be reviewed without launching
the game. Run after any ts_pack_walkers.py run (composites body+turret the
way the engine draws them; walk stage 0).

Usage: preview_to_desktop.py [TSTITN] [TSHMEC] [TSHVR]   (default: all)
"""
import io, json, os, sys, zipfile
from PIL import Image, ImageDraw

MOD = "/home/gibbo101/Documents/development/cnc-remastered-mods/cnc-ra-tiberian-factions/resources/remaster_mods/Vanilla_RA"
UNITS = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS"
OUT = os.path.expanduser("~/Desktop/tf-previews")
LABELS = ["N", "NW", "W", "SW", "S", "SE", "E", "NE"]

# name -> (zip, prefix, body shape for 8-facing i, turret shape or None)
SPECS = {
    "TSTITN": ("TSTITN.ZIP", "tstitn", lambda i: i * 12, lambda i: 96 + i * 4),
    "TSHMEC": ("TSHMEC.ZIP", "tshmec", lambda i: i * 4 * 8, None),
    "TSHVR": ("TSHVR.ZIP", "tshvr", lambda i: i * 4, lambda i: 32 + i * 4),
}


def frame(z, pre, s):
    meta = json.loads(z.read(f"{pre}-{s:04d}.meta"))
    tga = Image.open(io.BytesIO(z.read(f"{pre}-{s:04d}.tga"))).convert("RGBA")
    c = Image.new("RGBA", tuple(meta["size"]), (0, 0, 0, 0))
    c.paste(tga, (meta["crop"][0], meta["crop"][1]), tga)
    return c


def sheet_for(name):
    zn, pre, body, turret = SPECS[name]
    z = zipfile.ZipFile(f"{UNITS}/{zn}")
    cell = 300
    sheet = Image.new("RGB", (8 * cell, cell + 30), (120, 116, 100))
    dr = ImageDraw.Draw(sheet)
    for i in range(8):
        comp = frame(z, pre, body(i))
        if turret is not None:
            comp.alpha_composite(frame(z, pre, turret(i)))
        comp.thumbnail((cell - 10, cell - 10))
        sheet.paste(comp, (i * cell + 5, 30 + (cell - 10 - comp.height) // 2), comp)
        dr.text((i * cell + 8, 6), LABELS[i], fill=(255, 255, 90))
    out = f"{OUT}/{name}-facings.png"
    sheet.save(out)
    print(f"wrote {out}")


os.makedirs(OUT, exist_ok=True)
for name in (sys.argv[1:] or list(SPECS)):
    sheet_for(name)
