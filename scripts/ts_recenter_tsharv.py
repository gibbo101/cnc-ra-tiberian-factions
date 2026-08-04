#!/usr/bin/env python3
"""Re-centre TSHARV.ZIP in place: kill the cab-anchored pivot and drop the
canvas to the 48-class (384 px, 8x-classic — pairs with rules.ini
ShapeSize=48,48).

The HARV voxel model is origin-offset, so the origin-at-canvas-centre render
convention makes the hull orbit the front cab (~64 HD px radius) instead of
turning in place, and park low-left of its cell. A constant shift cannot fix
an orbit — the offset rotates with the facing — so each frame gets its own
shift. Raw per-frame bbox centering would re-introduce jitter (the walker-era
MLRS trap); instead the 32 bbox centres are least-squares fitted to
c + (A cos t, B sin t) and frames shift onto the FITTED circle, which
preserves rigid-body rotation exactly.

Zip-level: operates on the packed TGA+meta frames, no render sources needed.
Idempotent-safe (a centred input fits a zero-amplitude circle and shifts by
~0). Frames keep the write_zip centre-symmetric crop contract.
"""
import io, json, math, os, zipfile
from PIL import Image

MOD = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                   "resources", "remaster_mods", "Vanilla_RA"))
ZIP = f"{MOD}/Data/ART/TEXTURES/SRGB/RED_ALERT/UNITS/TSHARV.ZIP"
NAME = "tsharv"
N = 32
OUT_CANVAS = 384


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="TGA")
    return buf.getvalue()


def lsq_circle(vals):
    """Fit vals[i] ~ a + b*cos(t_i) + c*sin(t_i) over t_i = 2*pi*i/N."""
    ts = [2 * math.pi * i / N for i in range(N)]
    # Orthogonal basis over a full uniform period: plain projections suffice.
    a = sum(vals) / N
    b = sum(v * math.cos(t) for v, t in zip(vals, ts)) * 2 / N
    c = sum(v * math.sin(t) for v, t in zip(vals, ts)) * 2 / N
    return lambda i: a + b * math.cos(2 * math.pi * i / N) + c * math.sin(2 * math.pi * i / N)


src = zipfile.ZipFile(ZIP)
frames, boxes = [], []
for i in range(N):
    meta = json.loads(src.read(f"{NAME}-{i:04d}.meta"))
    im = Image.open(io.BytesIO(src.read(f"{NAME}-{i:04d}.tga"))).convert("RGBA")
    W, H = meta["size"]
    full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    full.paste(im, (meta["crop"][0], meta["crop"][1]))
    frames.append(full)
    b = full.getbbox()
    boxes.append(b)

fx = lsq_circle([(b[0] + b[2]) / 2 for b in boxes])
fy = lsq_circle([(b[1] + b[3]) / 2 for b in boxes])

out = []
clipped = 0
for i, full in enumerate(frames):
    dx = round(OUT_CANVAS / 2 - fx(i))
    dy = round(OUT_CANVAS / 2 - fy(i))
    fr = Image.new("RGBA", (OUT_CANVAS, OUT_CANVAS), (0, 0, 0, 0))
    sx, sy = max(0, -dx), max(0, -dy)  # Pillow negative-paste guard
    crop = full.crop((sx, sy, full.width, full.height))
    fr.paste(crop, (max(0, dx), max(0, dy)), crop)
    b0 = full.getbbox()
    if (b0[0] + dx < 0 or b0[1] + dy < 0
            or b0[2] + dx > OUT_CANVAS or b0[3] + dy > OUT_CANVAS):
        clipped += 1
    out.append(fr)
    if i % 8 == 0:
        b = fr.getbbox()
        print(f"f{i:2d} shift ({dx:+d},{dy:+d}) -> bbox centre "
              f"{(b[0]+b[2])/2:.0f},{(b[1]+b[3])/2:.0f} of {OUT_CANVAS//2}")
if clipped:
    raise SystemExit(f"ABORT: content clipped on {clipped} frames -- grow OUT_CANVAS")

with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
    for i, img in enumerate(out):
        base = f"{NAME}-{i:04d}"
        W, H = img.width, img.height
        bb = img.getbbox() or (W // 2 - 1, H // 2 - 1, W // 2 + 1, H // 2 + 1)
        x0 = min(bb[0], W - bb[2])
        y0 = min(bb[1], H - bb[3])
        b = (x0, y0, W - x0, H - y0)
        z.writestr(base + ".tga", tga_bytes(img.crop(b)))
        z.writestr(base + ".meta", json.dumps(
            {"size": [W, H], "crop": [b[0], b[1], b[2], b[3]]}))
print(f"rewrote {ZIP} ({len(out)} frames, canvas {OUT_CANVAS})")
