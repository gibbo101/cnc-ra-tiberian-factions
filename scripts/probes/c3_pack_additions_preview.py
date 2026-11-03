#!/usr/bin/env python3
"""Sign-off previews for the C&C3 pack's Nod tanks and GDI light vehicles: facings sheets and a firing GIF each.

A sheet draws 8 facings of each vehicle as the DLL would (hull, then the turret at its c3tanks.h seat), beside the
shipped C3PRED and C3SCORP. Each GIF shows a vehicle firing at the east facing, its effects placed at its c3tanks.h
fire points plus its unit_art_drop.json drop, all at the launcher's 128 px per cell (units scaled from their 192).
The Mortar's shell leaves from the unit centre: its tube is on the hull, which c3tanks.h has no table for.
Usage: c3_pack_additions_preview.py <out dir>
License: GPL v3.
"""
import io
import json
import math
import os
import re
import sys
import zipfile

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import asset_packs  # noqa: E402

REPO = os.path.dirname(os.path.dirname(HERE))
HEADER = open(os.path.join(REPO, "redalert", "c3tanks.h")).read()
DROPS = json.load(open(os.path.join(REPO, "scripts", "unit_art_drop.json")))
BG = (96, 104, 88, 255)
K = 128 / 192           # unit canvas px (8 per classic px) to the launcher's HD px per cell
LEP = 128 / 256         # leptons to HD px
TURRET = 96


def frames(name, kind):
    """Shape number -> full-canvas RGBA, through the tileset, so members shared with another ZIP resolve."""
    xml = open(asset_packs.tileset_xml(name, kind), encoding="utf-8").read()
    tiles = re.findall(r"<Name>%s</Name>\s*<Shape>(\d+)</Shape>.*?<Frame>([^<]+)</Frame>" % re.escape(name), xml, re.S)
    out = {}
    for shape, frame in tiles:
        folder, member = frame.split("\\")
        z = zipfile.ZipFile(asset_packs.art_zip(folder.upper(), kind))
        shape = int(shape)
        meta = json.loads(z.read(member[:-4] + ".meta"))
        im = Image.new("RGBA", tuple(meta["size"]))
        im.alpha_composite(Image.open(io.BytesIO(z.read(member))).convert("RGBA"), tuple(meta["crop"][:2]))
        out[shape] = im
    return out


def table(name, suffix):
    body = re.search(r"_%s_%s\[[^=]*= \{(.*?)\};" % (name.lower(), suffix), HEADER, re.S).group(1)
    return [(int(a), int(b)) for a, b in re.findall(r"\{(-?\d+), (-?\d+)\}", body)]


SEAT_OF = {"C3PITBMOR": "C3PITB"}


def unit_image(name, facing, art):
    """The vehicle at facing (frame order, CCW from N) with its turret seated, at unit canvas density."""
    im = art[facing * 3].copy()
    if TURRET + facing in art:
        seat = table(SEAT_OF.get(name, name), "seat_px")[(32 - facing) % 32]
        im.alpha_composite(art[TURRET + facing], (seat[0] * 8, seat[1] * 8))
    return im


def sheet(out, names, file):
    cell = 256
    img = Image.new("RGBA", (8 * cell, len(names) * cell), BG)
    d = ImageDraw.Draw(img)
    for r, name in enumerate(names):
        art = frames(name, "UNITS")
        for c, f in enumerate(range(0, 32, 4)):
            u = unit_image(name, f, art)
            img.alpha_composite(u, (c * cell + (cell - u.width) // 2, r * cell + (cell - u.height) // 2))
        d.text((6, r * cell + 4), name, fill=(255, 255, 255, 255))
    img.convert("RGB").save(os.path.join(out, file))


def fire_point(name, facing, side=0):
    """HD px from the unit centre (east, south) of a muzzle at facing, with the art's drop."""
    d = (32 - facing) % 32
    key = SEAT_OF.get(name, name)
    seat = table(key, "seat_lep")[d]
    fire = table(key, "fire")
    sides = int(re.search(r"_%s_fire\[\d+\]\[(\d+)\]" % key.lower(), HEADER).group(1))
    f = fire[(side % sides) * 32 + d]
    return ((seat[0] + f[0]) * LEP, (seat[1] + f[1]) * LEP + DROPS[name] * K)


def scaled(im, k):
    return im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)


def paste(canvas, im, x, y):
    """im centred on (x, y)."""
    canvas.alpha_composite(im, (round(x - im.width / 2), round(y - im.height / 2)))


def firing_gif(name, out):
    """The tank at the east facing firing at a target 2.5 cells away, in the launcher's 128 px per cell."""
    W, H = 900, 400
    cx, cy = 230, 200
    facing = 24                      # east, frame order
    art = frames(name, "UNITS")
    tank = scaled(unit_image(name, facing, art), K)
    tx = cx + 2.5 * 128
    gif = []
    fx = {n: frames(n, "VFX") for n in {
        "C3FLAME": ("C3FLME", "C3FLMHIT", "C3FLMPIL"), "C3STNK": ("C3STMIS", "C3STTRL", "C3STMZ", "C3STHIT"),
        "C3BEAM": ("C3BMCHG", "C3BMGLOW", "C3BMMZ", "C3BMHIT"),
        "C3PITB": ("C3PBMZ", "C3STMIS", "C3STTRL", "C3STHIT"), "C3PITBMOR": ("C3PBSHL", "C3STTRL", "C3MEDEXP"),
        "C3APC": ("C3APCMZE", "C3STHIT")}[name]}
    for t in range(40):
        fr = Image.new("RGBA", (W, H), BG)
        d = ImageDraw.Draw(fr)
        for gx in range(0, W, 128):
            d.line([(gx, 0), (gx, H)], fill=(88, 96, 80, 255))
        for gy in range(cy % 128, H, 128):
            d.line([(0, gy), (W, gy)], fill=(88, 96, 80, 255))
        paste(fr, tank, cx, cy)
        mx, my = fire_point(name, facing)
        mx, my = cx + mx, cy + my
        if name == "C3FLAME":
            for side in (0, 1):
                px, py = fire_point(name, facing, side)
                paste(fr, fx["C3FLMPIL"][t % 8], cx + px, cy + py)
            if 4 <= t < 20:
                for side in (0, 1):
                    px, py = fire_point(name, facing, side)
                    paste(fr, fx["C3FLME"][t - 4], cx + px, cy + py)
            if 8 <= t < 24:
                paste(fr, fx["C3FLMHIT"][t - 8], cx + 2.1 * 128 + 40, cy)
        elif name == "C3PITBMOR":
            t0, fly = 4, 14
            for p in range(max(t0, t - 11), min(t, t0 + fly) + 1):
                s = (p - t0) / fly
                paste(fr, fx["C3STTRL"][t - p], cx + (tx - cx) * s, cy - 110 * math.sin(math.pi * s))
            if t0 <= t < t0 + fly:
                s = (t - t0) / fly
                f = 24 if s < 0.5 else 26
                paste(fr, fx["C3PBSHL"][f], cx + (tx - cx) * s, cy - 110 * math.sin(math.pi * s))
            if t0 + fly <= t < t0 + fly + 16:
                paste(fr, fx["C3MEDEXP"][t - t0 - fly], tx, cy)
        elif name == "C3APC":
            for k in range(6):
                t0 = 4 + 3 * k
                px, py = fire_point(name, facing, k % 2)
                sx, sy = cx + px, cy + py
                if t0 <= t < t0 + 4:
                    paste(fr, fx["C3APCMZE"][t - t0], sx, sy)
                if t0 <= t < t0 + 2:
                    d.line([(sx + 20, sy), (tx, cy)], fill=(255, 230, 150, 255), width=2)
            if 6 <= t < 26:
                paste(fr, scaled(fx["C3STHIT"][(t - 6) % 16], .5), tx, cy)
        elif name in ("C3STNK", "C3PITB"):
            for k, side in enumerate((0, 1)):
                t0 = 4 + 6 * k
                px, py = fire_point(name, facing, side)
                sx, sy = cx + px, cy + py
                flash = fx["C3STMZ"] if name == "C3STNK" else fx["C3PBMZ"]
                if t0 <= t < t0 + len(flash):
                    paste(fr, flash[t - t0], sx, sy)
                fly = 8
                for p in range(max(t0, t - 11), min(t, t0 + fly) + 1):
                    s = (p - t0) / fly
                    paste(fr, fx["C3STTRL"][t - p], sx + (tx - sx) * s, sy + (cy - sy) * s - 30 * math.sin(math.pi * s))
                if t0 <= t < t0 + fly:
                    s = (t - t0) / fly
                    arc = 30 * math.sin(math.pi * s)
                    paste(fr, fx["C3STMIS"][facing], sx + (tx - sx) * s, sy + (cy - sy) * s - arc)
                if t0 + fly <= t < t0 + fly + 16:
                    paste(fr, fx["C3STHIT"][t - t0 - fly], tx, cy)
        else:
            if t < 16:
                paste(fr, fx["C3BMCHG"][t], mx, my)
            elif t < 30:
                a = t - 16
                d.line([(mx, my), (tx, cy)], fill=(255, 60, 40, 255), width=3)
                d.line([(mx, my), (tx, cy)], fill=(255, 235, 230, 255), width=1)
                steps = int(math.hypot(tx - mx, cy - my) // 8)
                for i in range(steps + 1):
                    if a < 12:
                        paste(fr, fx["C3BMGLOW"][a], mx + (tx - mx) * i / steps, my + (cy - my) * i / steps)
                if a < 5:
                    paste(fr, fx["C3BMMZ"][a], mx, my)
                if a < 12:
                    paste(fr, fx["C3BMHIT"][a], tx, cy)
        gif.append(fr.convert("RGB"))
    gif[0].save(os.path.join(out, f"{name}_firing.gif"), save_all=True, append_images=gif[1:], duration=67, loop=0)


def main(out):
    os.makedirs(out, exist_ok=True)
    sheet(out, ["C3PRED", "C3SCORP", "C3FLAME", "C3STNK", "C3BEAM"], "C3_NOD_TANKS_sheet.png")
    sheet(out, ["C3PRED", "C3PITB", "C3PITBMOR", "C3APC", "C3RIG"], "C3_GDI_LIGHT_sheet.png")
    for name in ("C3FLAME", "C3STNK", "C3BEAM", "C3PITB", "C3PITBMOR", "C3APC"):
        firing_gif(name, out)
    print(f"wrote previews to {out}")


if __name__ == "__main__":
    main(sys.argv[1])
