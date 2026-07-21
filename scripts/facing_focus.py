#!/usr/bin/env python3
"""One-facing focus sheet for the Titan tuning loop: our current packed frame
(body+turret composited) LARGE, next to the TS reference crop for the same
facing. Writes ~/Desktop/tf-previews/TSTITN-focus-<facing>.png.

Usage: facing_focus.py W          (N NW W SW S SE E NE)
"""
import io, json, os, sys, zipfile
from PIL import Image, ImageDraw

REF = "/home/gibbo101/Pictures/Screenshots/Screenshot from 2026-07-20 21-59-32.png"
RING = {"N": (487, 105), "NW": (285, 195), "W": (170, 350), "SW": (275, 480),
        "S": (465, 590), "SE": (665, 490), "E": (790, 360), "NE": (675, 190)}
ORDER = ["N", "NW", "W", "SW", "S", "SE", "E", "NE"]
MOD = "/home/gibbo101/Documents/development/cnc-remastered-mods/cnc-ra-tiberian-factions/resources/remaster_mods/Vanilla_RA"
OUT = os.path.expanduser("~/Desktop/tf-previews")

facing = (sys.argv[1] if len(sys.argv) > 1 else "W").upper()
i = ORDER.index(facing)

z = zipfile.ZipFile(f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS/TSTITN.ZIP")
def fr(s):
    meta = json.loads(z.read(f"tstitn-{s:04d}.meta"))
    tga = Image.open(io.BytesIO(z.read(f"tstitn-{s:04d}.tga"))).convert("RGBA")
    c = Image.new("RGBA", tuple(meta["size"]), (0, 0, 0, 0))
    c.paste(tga, (meta["crop"][0], meta["crop"][1]), tga)
    return c

mine = fr(i * 12)
mine.alpha_composite(fr(96 + i * 4))
mine.thumbnail((560, 560))

cx, cy = RING[facing]
ref = Image.open(REF).crop((cx - 95, cy - 100, cx + 95, cy + 100)).resize((532, 560), Image.LANCZOS)

sheet = Image.new("RGB", (1160, 600), (95, 88, 70))
dr = ImageDraw.Draw(sheet)
sheet.paste(ref, (10, 35))
tmp = Image.new("RGB", (580, 560), (95, 88, 70))
tmp.paste(mine, ((580 - mine.width) // 2, (560 - mine.height) // 2), mine)
sheet.paste(tmp, (570, 35))
dr.text((12, 8), f"{facing} — TS reference", fill=(255, 255, 90))
dr.text((575, 8), f"{facing} — ours (current pack)", fill=(255, 255, 90))
os.makedirs(OUT, exist_ok=True)
out = f"{OUT}/TSTITN-focus-{facing}.png"
sheet.save(out)
print(f"wrote {out}")
