#!/usr/bin/env python3
"""Regenerate the Aseprite tuning kit (~/Desktop/tf-previews/titan-tune/):
per-facing torso + barrel PNG layers at the CURRENT packer constants, plus
layered .aseprite files (via the Steam Aseprite CLI). Run after baking any
anchor change so drag deltas never double-count.
"""
import re, math, os, subprocess
import numpy as np
from PIL import Image
import hqx

ART = os.environ.get("TS_ART_DIR")
if not ART:
    raise SystemExit("set TS_ART_DIR")
OUT = os.path.expanduser("~/Desktop/tf-previews/titan-tune")
ASE = os.path.expanduser("~/.steam/steam/steamapps/common/Aseprite/aseprite")
os.makedirs(OUT, exist_ok=True)
TMP = os.path.join(OUT, ".build")
os.makedirs(TMP, exist_ok=True)

src = open(os.path.join(os.path.dirname(__file__), "ts_pack_walkers.py")).read()
TW = eval(re.search(r"FACING_TWEAKS = (\[.*?\])", src).group(1))
BARL_SCALE = float(re.search(r"BARL_SCALE = ([0-9.]+)", src).group(1))
PORT_FWD = int(re.search(r"PORT_FWD = (\d+)", src).group(1))
PORT_LAT = int(re.search(r"PORT_LAT = (\d+)", src).group(1))
PORT_UP = int(re.search(r"PORT_UP = (\d+)", src).group(1))
CANVAS_T, F_T, VERT = 448, 6.4, 0.50
_muz_src = open(os.path.join(os.path.dirname(__file__), "..", "redalert", "tstitn_muzzle.h")).read()
MUZ = [tuple(map(int, m)) for m in re.findall(r"\{(-?\d+), (-?\d+)\}", _muz_src)]
assert len(MUZ) == 32
ANCHOR_SRC, ANCHOR_DST = (47.5, 55.0), (224.0, 386.0)


def safe_paste(dst, s, x, y):
    sx, sy = max(0, -x), max(0, -y)
    if sx or sy:
        s = s.crop((sx, sy, s.width, s.height))
        x, y = max(0, x), max(0, y)
    dst.paste(s, (x, y), s)


def crisp(img):
    rgb = Image.new("RGB", img.size, (0, 0, 0))
    rgb.paste(img, (0, 0), img)
    big = hqx.hq4x(rgb).convert("RGBA")
    a = img.split()[3].resize((img.width * 4, img.height * 4), Image.LANCZOS)
    big.putalpha(a)
    s = big.resize((round(img.width * F_T), round(img.height * F_T)), Image.LANCZOS)
    out = Image.new("RGBA", (CANVAS_T, CANVAS_T), (0, 0, 0, 0))
    safe_paste(out, s, round(ANCHOR_DST[0] - ANCHOR_SRC[0] * F_T), round(ANCHOR_DST[1] - ANCHOR_SRC[1] * F_T))
    return out


LUA = os.path.join(TMP, "_build_layered.lua")
open(LUA, "w").write("""
local spr = app.open(app.params["torso"])
spr.layers[1].name = "titan (locked)"
local flSpr = app.open(app.params["flash"])
local flImg = Image(flSpr.width, flSpr.height, ColorMode.RGB)
flImg:drawSprite(flSpr, 1)
local lay = spr:newLayer()
lay.name = "flash (drag me)"
spr:newCel(lay, 1, flImg, Point(0, 0))
spr:saveAs(app.params["out"])
""")

names = ["N", "NW", "W", "SW", "S", "SE", "E", "NE"]
for i, lab in enumerate(names):
    s = i * 4
    torso = crisp(Image.open(f"{ART}/shp_mmch/frame-{120 + (32 - s) % 32:04d}.png").convert("RGBA"))
    torso.save(f"{TMP}/{lab}-torso.png")
    layer = Image.new("RGBA", (CANVAS_T, CANVAS_T), (0, 0, 0, 0))
    if True:  # always draggable — even facings the PACKER suppresses (N family): the kit must let Luke place them
        bar = Image.open(f"{ART}/ts30_titanbarl/frame-{s:04d}.png").convert("RGBA")
        bar = bar.resize((round(bar.width * BARL_SCALE), round(bar.height * BARL_SCALE)), Image.LANCZOS)
        theta = math.radians(s * 11.25)
        ax, ay = -math.sin(theta), -math.cos(theta) * VERT
        alpha = np.array(bar)[..., 3]
        ys, xs = np.nonzero(alpha > 40)
        proj = xs * ax + ys * ay
        sel = proj <= np.percentile(proj, 8)
        rear_x, rear_y = float(xs[sel].mean()), float(ys[sel].mean())
        rx_, ry_ = math.cos(theta), -math.sin(theta) * VERT
        a8 = s / 4.0
        i0, i1 = int(a8) % 8, (int(a8) + 1) % 8
        frac = a8 - int(a8)
        twx = TW[i0][0] * (1 - frac) + TW[i1][0] * frac
        twy = TW[i0][1] * (1 - frac) + TW[i1][1] * frac
        port_x = CANVAS_T / 2 + ax * PORT_FWD + rx_ * PORT_LAT + twx
        port_y = CANVAS_T / 2 + ay * PORT_FWD + ry_ * PORT_LAT - PORT_UP + twy
        tuck = 30 if (s <= 4 or s >= 28) else 0
        safe_paste(layer, bar, round(port_x - rear_x - ax * tuck), round(port_y - rear_y - ay * tuck))
    layer.save(f"{TMP}/{lab}-barrel.png")
    # flat composite (anchors are LOCKED — packer z-order: right flank away => barrel under torso)
    flat = Image.new("RGBA", (CANVAS_T, CANVAS_T), (0, 0, 0, 0))
    if s <= 15:
        flat.alpha_composite(layer)
        flat.alpha_composite(torso)
    else:
        flat.alpha_composite(torso)
        flat.alpha_composite(layer)
    flat.save(f"{TMP}/{lab}-flat.png")
    # flash marker at the engine's CURRENT fire point (generated muzzle table)
    mdx, mdy = MUZ[s]
    mx, my = CANVAS_T / 2 + mdx * 3 / 4, CANVAS_T / 2 + mdy * 3 / 4
    fl = Image.new("RGBA", (CANVAS_T, CANVAS_T), (0, 0, 0, 0))
    import PIL.ImageDraw as _ID
    d = _ID.Draw(fl)
    d.ellipse([mx - 10, my - 10, mx + 10, my + 10], outline=(255, 0, 255, 255), width=3)
    d.line([mx - 16, my, mx + 16, my], fill=(255, 255, 0, 255), width=3)
    d.line([mx, my - 16, mx, my + 16], fill=(255, 255, 0, 255), width=3)
    fl.save(f"{TMP}/{lab}-flash.png")
    subprocess.run([ASE, "-b", "--script-param", f"torso={OUT}/{lab}-flat.png",
                    "--script-param", f"flash={OUT}/{lab}-flash.png",
                    "--script-param", f"out={OUT}/{lab}.aseprite",
                    "--script", LUA], capture_output=True)
print(f"tuning kit regenerated at {OUT} (anchors: {TW})")
