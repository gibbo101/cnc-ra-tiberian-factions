#!/usr/bin/env python3
"""ModDB showcase GIFs of the TS GDI art as the game draws it, in GDI gold: the TS-era frames a release
shipped beside this checkout's HD frames (before-after/), and the HD frames alone (hd-only/).

Usage: moddb_showcase.py OUT_DIR [SUBJECT ...] [--old-rev main]
Both sides are composited from the packed zips with the DLL's layering, seats and timing, and the
launcher's alpha cutoff (docs/launcher-render-contracts.md)."""

import argparse
import io
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
ART = "Data/ART/TEXTURES/SRGB/RED_ALERT"
OLD_PACK = "asset-packs/TS-Graphics-Pack"
HD_PACK = "asset-packs/TS-HD-Graphics-Pack"

# TechnoClass::BodyShape: RA's 32 directions (clockwise from north) to the frame index (counter-clockwise).
BODY_SHAPE = [(32 - d) % 32 for d in range(32)]
HOVER_BOB = [0, -1, -2, -2, -1, 0, 1, 1]

# Hover_Rack_Seat on this branch, classic px per hull frame.
HVR_SEAT_HD = [
    (0, 5), (2, 5), (3, 5), (5, 4), (6, 4), (8, 3), (8, 2), (9, 1),
    (9, 0), (9, -1), (9, -2), (8, -3), (7, -3), (5, -4), (4, -4), (2, -5),
    (0, -5), (-2, -5), (-3, -5), (-5, -4), (-6, -4), (-8, -3), (-8, -2), (-9, -1),
    (-9, 0), (-9, 1), (-9, 2), (-8, 3), (-7, 3), (-5, 4), (-4, 4), (-2, 5)]
# Hover_Rack_Seat in the 5.0.0 release, classic px per RA direction: the mount by the hull, a residual by the rack.
HVR_MOUNT_OLD = list(zip(
    [0, -2, -3, -5, -5, -7, -8, -9, -9, -8, -7, -6, -5, -5, -3, -2, 0, 2, 3, 5, 5, 6, 7, 8, 9, 8, 8, 7, 5, 5, 3, 2],
    [1, 0, 0, -1, -1, -2, -3, -4, -6, -7, -8, -8, -9, -9, -9, -10, -10, -9, -9, -9, -9, -8, -8, -6, -5, -4, -3, -2,
     -1, -1, 0, 0]))
HVR_RES_OLD = list(zip(
    [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, -1, -1, 0, 0, 0, 1, 1, 1, 1]))

TICK_MS = 1000 / 15
ALPHA_CUTOFF = 128
UNIT_BG = (96, 108, 72)
BUILDING_BG = (90, 100, 80)
FRAME_BG = (24, 26, 22)
PANEL_RIM = (105, 120, 79)
LABEL_OLD = (203, 200, 184)
LABEL_HD = (212, 190, 136)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MARGIN, GAP, BAND, PAD = 10, 12, 34, 24
MIN_PANEL_W = 280


class Sheet:
    """One packed zip: frame n on its full meta canvas, as RGBA."""

    def __init__(self, data):
        self.zip = zipfile.ZipFile(io.BytesIO(data))
        self.names = {}
        for name in self.zip.namelist():
            m = re.search(r"-(\d{4})\.tga$", name)
            if m:
                self.names[int(m.group(1))] = name
        self.cache = {}

    def frame(self, n):
        if n not in self.cache:
            name = self.names[n]
            meta = json.loads(self.zip.read(name[:-4] + ".meta"))
            w, h = meta["size"]
            x0, y0 = meta["crop"][:2]
            canvas = np.zeros((h, w, 4), np.uint8)
            tga = np.asarray(Image.open(io.BytesIO(self.zip.read(name))).convert("RGBA"))
            canvas[y0:y0 + tga.shape[0], x0:x0 + tga.shape[1]] = tga
            self.cache[n] = gold(canvas)
        return self.cache[n]


def gold(a):
    """The launcher's remap of the house green to GDI gold, luminance kept: a pixel's green beyond its red and
    blue is the house colour's share, and that share turns from (0, e, 0) to (e, 0.75e, 0.12e)."""
    rgb = a[..., :3].astype(np.int32)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    e = g - np.maximum(r, b)
    hue = np.asarray(Image.fromarray(a[..., :3]).convert("HSV"))[..., 0].astype(np.int32)
    hit = (e > 6) & (hue >= 67) & (hue <= 106)
    out = a.copy()
    out[..., 0] = np.where(hit, np.clip(r + e, 0, 255), r)
    out[..., 1] = np.where(hit, np.clip(np.maximum(r, b) + np.round(e * 0.75), 0, 255), g)
    out[..., 2] = np.where(hit, np.clip(b + np.round(e * 0.12), 0, 255), b)
    return out


def load(rev, pack, kind, name):
    path = f"{pack}/{ART}/{kind}/{name}.ZIP"
    if rev is None:
        return Sheet((REPO / path).read_bytes())
    return Sheet(subprocess.run(["git", "-C", str(REPO), "show", f"{rev}:{path}"], check=True,
                                capture_output=True).stdout)


def composite(layers):
    """Layers [(sheet, frame, dx, dy)] in draw order, each placed by its canvas centre plus (dx, dy) canvas px,
    on a canvas the size of the first; pixels under the launcher's alpha cutoff are dropped."""
    base = layers[0][0].frame(layers[0][1])
    h, w = base.shape[:2]
    out = np.zeros((h, w, 4), np.float32)
    for sheet, n, dx, dy in layers:
        f = sheet.frame(n).astype(np.float32)
        fh, fw = f.shape[:2]
        ox, oy = (w - fw) // 2 + dx, (h - fh) // 2 + dy
        layer = np.zeros_like(out)
        ys, xs = slice(max(oy, 0), min(oy + fh, h)), slice(max(ox, 0), min(ox + fw, w))
        layer[ys, xs] = f[ys.start - oy:ys.stop - oy, xs.start - ox:xs.stop - ox]
        alpha = np.where(layer[..., 3] >= ALPHA_CUTOFF, layer[..., 3] / 255, 0)[..., None]
        out[..., :3] = layer[..., :3] * alpha + out[..., :3] * (1 - alpha)
        out[..., 3:] = alpha + out[..., 3:] * (1 - alpha)
    return out


def turn(name, kind="UNITS", turret=False):
    def side(sheet, old):
        return [[(sheet, BODY_SHAPE[d], 0, 0)] + ([(sheet, 32 + BODY_SHAPE[d], 0, 0)] if turret else [])
                for d in range(32)]
    return dict(sheets={"": name}, kind=kind, sides=side, ms=[100] * 32)


def turret_turn(name, hull_dir):
    def side(sheet, old):
        return [[(sheet, BODY_SHAPE[hull_dir], 0, 0), (sheet, 32 + BODY_SHAPE[t], 0, 0)] for t in range(32)]
    return dict(sheets={"": name}, kind="UNITS", sides=side, ms=[100] * 32)


def walk(name, direction, steps, step_ms):
    def side(sheet, old):
        return [[(sheet, BODY_SHAPE[direction] * steps + s, 0, 0)] for s in range(steps)]
    return dict(sheets={"": name}, kind="UNITS", sides=side, ms=[step_ms] * steps)


def hover_mlrs():
    density = 4

    def side(sheet, old):
        frames = []
        for i, d in enumerate(range(32)):
            f = BODY_SHAPE[d]
            bob = HOVER_BOB[(i // 2) & 7] * density
            if old:
                sx = HVR_MOUNT_OLD[d][0] + HVR_RES_OLD[d][0]
                sy = HVR_MOUNT_OLD[d][1] + HVR_RES_OLD[d][1]
            else:
                sx, sy = HVR_SEAT_HD[f]
            frames.append([(sheet, 64 + f, 0, bob), (sheet, f, 0, bob),
                           (sheet, 32 + f, sx * density, sy * density + bob)])
        return frames
    return dict(sheets={"": "TSHVR"}, kind="UNITS", sides=side, ms=[100] * 32, scale=2)


def limpet():
    density = 4
    ticks = range(0, 160, 2)

    def side(sheet, old):
        frames = []
        for t in ticks:
            n, bob = (t // 2) % 10, HOVER_BOB[(t >> 2) & 7] * density
            frames.append([(sheet, 10 + n, 0, bob), (sheet, n, 0, bob)])
        return frames
    return dict(sheets={"": "TSLIMP"}, kind="UNITS", sides=side, ms=[2 * TICK_MS] * len(ticks), scale=2)


def refinery():
    """The dock lamps (16 frames, 3 ticks each) twice over, with one flare-stack burst (20 frames, 3 ticks each)
    on the HD side; the 5.0.0 refinery draws no flare."""
    def side(sheets, old):
        frames = []
        for i in range(32):
            if old:
                frames.append([(sheets[""], i % 16, 0, 0)])
                continue
            layers = [(sheets[""], i % 16, 0, 0), (sheets["NF"], i % 16, 0, 0)]
            if 6 <= i < 26:
                layers.append((sheets["FR"], i - 6, 0, 0))
            frames.append(layers)
        return frames
    return dict(sheets={"": "TSPROC", "NF": "TSPROCNF", "FR": "TSPROCFR"}, old_sheets=[""], kind="STRUCTURES",
                sides=side, ms=[3 * TICK_MS] * 32, multi=True)


def tech_center():
    """The dome's panels (8 healthy frames) at each side's own rate: 4 ticks in HD, 3 in the 5.0.0 release."""
    def side(sheet, old):
        rate = 3 if old else 4
        return [[(sheet, (t // rate) % 8, 0, 0)] for t in range(96)]
    return dict(sheets={"": "TSTECH"}, kind="STRUCTURES", sides=side, ms=[TICK_MS] * 96)


SUBJECTS = {
    "unit-mammoth-mk1-turn": turn("TS4TNK", turret=True),
    "unit-mammoth-mk1-turret": turret_turn("TS4TNK", hull_dir=12),
    "unit-mammoth-mk2-walk": walk("TSHMEC", direction=10, steps=8, step_ms=250),
    "unit-mammoth-mk2-turn": walk("TSHMEC", direction=0, steps=8, step_ms=250) | dict(
        sides=lambda sheet, old: [[(sheet, BODY_SHAPE[d] * 8, 0, 0)] for d in range(32)], ms=[100] * 32),
    "unit-mcv-turn": turn("TSMCV"),
    "unit-apc-turn": turn("TSAPC"),
    "unit-mobile-sensor-array-turn": turn("TSLPST"),
    "unit-mobile-war-factory-turn": turn("TSMWAR"),
    "unit-hover-mlrs-turn": hover_mlrs(),
    "unit-limpet-drone-blink": limpet(),
    "building-refinery-idle": refinery(),
    "building-tech-center-idle": tech_center(),
}


def render_side(spec, rev, pack):
    old = rev is not None
    keys = spec.get("old_sheets", list(spec["sheets"])) if old else list(spec["sheets"])
    sheets = {k: load(rev, pack, spec["kind"], spec["sheets"][k]) for k in keys}
    arg = sheets if spec.get("multi") else sheets[""]
    return [composite(layers) for layers in spec["sides"](arg, old)]


def bbox(frames, scale=1):
    """The union box of every frame's drawn pixels, relative to the canvas centre, at least MIN_PANEL_W wide
    once scaled, so a panel's label fits over it."""
    x0 = y0 = 10 ** 6
    x1 = y1 = -10 ** 6
    for f in frames:
        ys, xs = np.nonzero(f[..., 3] > 0)
        if len(xs):
            cy, cx = f.shape[0] / 2, f.shape[1] / 2
            x0, y0 = min(x0, xs.min() - cx), min(y0, ys.min() - cy)
            x1, y1 = max(x1, xs.max() + 1 - cx), max(y1, ys.max() + 1 - cy)
    x0, x1 = int(np.floor(x0)) - PAD, int(np.ceil(x1)) + PAD
    grow = max(0, -(-MIN_PANEL_W // scale) - (x1 - x0))
    x0, x1 = x0 - grow // 2, x1 + grow - grow // 2
    return x0, int(np.floor(y0)) - PAD, x1, int(np.ceil(y1)) + PAD


def panel(frame, box, bg, scale):
    x0, y0, x1, y1 = box
    h, w = frame.shape[:2]
    out = np.zeros((y1 - y0, x1 - x0, 4), np.float32)
    sx, sy = int(x0 + w / 2), int(y0 + h / 2)
    src = frame[max(sy, 0):sy + out.shape[0], max(sx, 0):sx + out.shape[1]]
    out[max(-sy, 0):max(-sy, 0) + src.shape[0], max(-sx, 0):max(-sx, 0) + src.shape[1]] = src
    a = out[..., 3:]
    rgb = out[..., :3] * a + np.array(bg, np.float32) * (1 - a)
    img = Image.fromarray(np.clip(rgb.round(), 0, 255).astype(np.uint8), "RGB")
    if scale != 1:
        img = img.resize((img.width * scale, img.height * scale), Image.LANCZOS)
    ImageDraw.Draw(img).rectangle([0, 0, img.width - 1, img.height - 1], outline=PANEL_RIM)
    return img


def save_gif(path, images, ms):
    path.parent.mkdir(parents=True, exist_ok=True)
    pal = [im.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for im in images]
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=[round(m) for m in ms], loop=0,
                disposal=1, optimize=False)


def make(name, spec, out_dir, old_rev):
    hd = render_side(spec, None, HD_PACK)
    old = render_side(spec, old_rev, OLD_PACK)
    bg = BUILDING_BG if spec["kind"] == "STRUCTURES" else UNIT_BG
    scale = spec.get("scale", 1)

    box = bbox(hd, scale)
    save_gif(out_dir / "hd-only" / f"{name}.gif", [panel(f, box, bg, scale) for f in hd], spec["ms"])

    box = bbox(hd + old, scale)
    font = ImageFont.truetype(FONT, 20)
    frames = []
    for a, b in zip(old, hd):
        left, right = panel(a, box, bg, scale), panel(b, box, bg, scale)
        sheet = Image.new("RGB", (MARGIN * 2 + GAP + left.width * 2, BAND + left.height + MARGIN), FRAME_BG)
        sheet.paste(left, (MARGIN, BAND))
        sheet.paste(right, (MARGIN + left.width + GAP, BAND))
        draw = ImageDraw.Draw(sheet)
        for text, colour, x in (("Tiberian Sun", LABEL_OLD, MARGIN),
                                ("Tiberian Factions HD", LABEL_HD, MARGIN + left.width + GAP)):
            draw.text((x + left.width / 2, BAND / 2), text, font=font, fill=colour, anchor="mm")
        frames.append(sheet)
    save_gif(out_dir / "before-after" / f"{name}.gif", frames, spec["ms"])
    print(f"{name}: {len(hd)} frames, before-after {frames[0].size}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("subjects", nargs="*", help=f"default: all of {', '.join(SUBJECTS)}")
    ap.add_argument("--old-rev", default="main", help="the revision whose TS-era zips are the before side")
    args = ap.parse_args()
    for name in args.subjects or SUBJECTS:
        if name not in SUBJECTS:
            sys.exit(f"unknown subject {name}")
        make(name, SUBJECTS[name], args.out_dir, args.old_rev)


if __name__ == "__main__":
    main()
