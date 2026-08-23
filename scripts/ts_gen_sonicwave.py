#!/usr/bin/env python3
"""Generate the TS Disruptor sonic-wave anim art (TSSONICW.ZIP).

There is NO sonic-wave art in Tiberian Sun to port: TS generates the effect in
its own engine as a live screen distortion of whatever is behind the wave. We
cannot distort, so the wave is faked with a translucent sprite.

WHY RINGS AND NOT ARCS
----------------------
A spawned AnimClass draws its sprite unrotated. An arc or crescent would only
read correctly when the beam happened to point one way, and would look wrong at
the other seven facings. A ring is rotationally symmetric, so one sprite serves
every beam angle. Rings marching along the beam line read as a wave travelling
out from the muzzle.

Each spawned ring expands and fades across its own frames; the caller spawns
them in sequence along the line, so several are in flight at once.

Tuning lives entirely in the constants below.

Usage:  ts_gen_sonicwave.py [OUTDIR]
"""
import io, json, math, os, sys, zipfile
from PIL import Image, ImageDraw, ImageFilter

CANVAS = 128          # matches RAILFX, the other small VFX anim
FRAMES = 6            # anim stages
R_START, R_END = 14.0, 44.0     # ring radius, first frame -> last
T_START, T_END = 8.0, 3.0       # ring thickness, first frame -> last
A_START, A_END = 200, 0         # ring alpha, first frame -> last
COLOR = (210, 240, 255)         # pale blue-white: sonic, not laser-green
BLUR = 1.4                      # softens the ring so it reads as pressure, not a hoop


def lerp(a, b, t):
    return a + (b - a) * t


def ring(i):
    """One stage: an expanding, thinning, fading soft ring."""
    t = i / (FRAMES - 1) if FRAMES > 1 else 0.0
    r = lerp(R_START, R_END, t)
    thick = lerp(T_START, T_END, t)
    alpha = int(round(lerp(A_START, A_END, t)))

    # Supersample x4 so the ring edge is smooth before the blur.
    ss = 4
    big = Image.new('L', (CANVAS * ss, CANVAS * ss), 0)
    d = ImageDraw.Draw(big)
    c = CANVAS * ss / 2.0
    d.ellipse([c - r * ss, c - r * ss, c + r * ss, c + r * ss],
              outline=255, width=max(1, int(round(thick * ss))))
    mask = big.resize((CANVAS, CANVAS), Image.LANCZOS).filter(ImageFilter.GaussianBlur(BLUR))

    out = Image.new('RGBA', (CANVAS, CANVAS), (0, 0, 0, 0))
    out.paste(Image.new('RGBA', (CANVAS, CANVAS), COLOR + (255,)), (0, 0),
              mask.point(lambda v: v * alpha // 255))
    return out


def tga_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format='TGA')
    return buf.getvalue()


def write_zip(path, name, frames):
    """Center-symmetric crop + meta -- identical contract to the other packers."""
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for i, img in enumerate(frames):
            base = f'{name}-{i:04d}'
            W, H = img.width, img.height
            bb = img.getbbox() or (W // 2 - 1, H // 2 - 1, W // 2 + 1, H // 2 + 1)
            x0 = min(bb[0], W - bb[2])
            y0 = min(bb[1], H - bb[3])
            b = (x0, y0, W - x0, H - y0)
            z.writestr(base + '.tga', tga_bytes(img.crop(b)))
            z.writestr(base + '.meta', json.dumps(
                {'size': [W, H], 'crop': [b[0], b[1], b[2], b[3]]}))


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else (
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                     'resources', 'remaster_mods', 'Vanilla_RA', 'Data', 'ART',
                     'TEXTURES', 'SRGB', 'RED_ALERT', 'VFX'))
    outdir = os.path.abspath(outdir)
    frames = [ring(i) for i in range(FRAMES)]
    path = os.path.join(outdir, 'TSSONICW.ZIP')
    write_zip(path, 'tssonicw', frames)
    print(f'wrote {path} ({len(frames)} frames, {CANVAS}px canvas)')


if __name__ == '__main__':
    main()
