#!/usr/bin/env python3
"""Generate the TS Disruptor sonic-wave anim art (TSSONICW.ZIP).

There is NO sonic-wave art in Tiberian Sun to port: TS generates the effect in
its own engine as a live screen distortion of whatever is behind the wave. We
cannot distort, so the wave is faked with translucent sprites.

WHAT THE REAL THING LOOKS LIKE (measured off TS footage, 2026-08-24)
-------------------------------------------------------------------
Not rings, and not a beam: a WIDE TRANSLUCENT BAND that sweeps out from the
tank along the firing line. Measured on a 834x465 capture:

  * band thickness ~39px against a 108px unit selection box -> the band is
    ~0.36 of the unit's own width. For our 56px ShapeSize Disruptor that is
    ~20 classic px, and at the 5.33 canvas-per-classic-px VFX ratio (RAILFX:
    128px canvas, 24 classic dim) that is ~107px inside a 128px canvas.
  * mean band colour (121,176,105) over (122,94,59) terrain. Solving the
    alpha composite gives roughly (130,235,140) at ~60% alpha.
  * the interior is mottled rather than flat -- it reads as rippling pressure.
  * the band EXTENDS outward from the muzzle, it does not appear all at once.

WHY DISCS AND NOT ONE BAND SPRITE
---------------------------------
A spawned AnimClass draws UNROTATED, so a band sprite would only line up at one
of the eight beam angles. A soft disc is rotationally symmetric; spawning a
dense overlapping chain of them along the line builds the band at ANY angle,
with the band's thickness coming from the disc diameter.

The outward sweep comes from each disc's stage offset, not from a spawn delay
(the AnimClass ctor's timedelay param is off-limits -- delayed anims export to
the launcher in a pre-start state). Each disc fades IN then OUT across its
stages; discs near the muzzle are started LATE in that cycle and far discs
EARLY, so as time advances the bright part of the band travels outward.

Tuning lives entirely in the constants below.

Usage:  ts_gen_sonicwave.py [OUTDIR]
"""
import io, json, math, os, sys, zipfile
from PIL import Image, ImageDraw, ImageFilter

CANVAS = 128          # 5.33 canvas px per classic px -> 24 classic dim, as RAILFX
FRAMES = 8            # anim stages; alpha ramps up then back down across them
DIAMETER = 107.0      # ~20 classic px: the measured 0.36 x unit width
COLOR = (120, 200, 245)   # blue: the shimmer supplies the distortion, this supplies the tint
A_PEAK = 120          # lower now the launcher's shimmer carries most of the read
EDGE_SOFT = 5.0       # gaussian blur on the disc edge, in px
MOTTLE = 0.30         # 0 = flat fill, 1 = heavily rippled interior
MOTTLE_SEED = 20260824
RISE, FALL = 0.22, 0.34   # envelope shoulders; the middle stages hold at full alpha


def lerp(a, b, t):
    return a + (b - a) * t


def _mottle():
    """Static noise field so the band interior ripples instead of reading flat."""
    import random
    rnd = random.Random(MOTTLE_SEED)
    n = Image.new('L', (CANVAS, CANVAS))
    n.putdata([rnd.randrange(256) for _ in range(CANVAS * CANVAS)])
    # Blur to clumps rather than per-pixel static, then normalise to 0..255.
    n = n.filter(ImageFilter.GaussianBlur(3.0))
    lo, hi = n.getextrema()
    span = max(1, hi - lo)
    return n.point(lambda v: (v - lo) * 255 // span)


_NOISE = None


def wave(i):
    """One stage: a soft mottled disc, fading in then out across the frames."""
    global _NOISE
    if _NOISE is None:
        _NOISE = _mottle()

    # Trapezoid envelope: rise, HOLD, fall. A triangle spent most of its stages
    # nearly invisible, which left the far half of the band dead once the discs
    # were staged along it; the hold keeps the whole band lit while still giving
    # the crest something to travel through.
    t = i / (FRAMES - 1) if FRAMES > 1 else 0.0
    if t < RISE:
        env = t / RISE
    elif t > 1.0 - FALL:
        env = (1.0 - t) / FALL
    else:
        env = 1.0
    alpha = int(round(A_PEAK * min(1.0, env)))
    if alpha <= 0:
        return Image.new('RGBA', (CANVAS, CANVAS), (0, 0, 0, 0))

    ss = 4
    big = Image.new('L', (CANVAS * ss, CANVAS * ss), 0)
    d = ImageDraw.Draw(big)
    c = CANVAS * ss / 2.0
    r = DIAMETER * ss / 2.0
    d.ellipse([c - r, c - r, c + r, c + r], fill=255)
    mask = big.resize((CANVAS, CANVAS), Image.LANCZOS).filter(ImageFilter.GaussianBlur(EDGE_SOFT))

    # Modulate the disc by the noise field so the interior ripples.
    if MOTTLE > 0:
        m = mask.load()
        nz = _NOISE.load()
        for y in range(CANVAS):
            for x in range(CANVAS):
                if m[x, y]:
                    f = 1.0 - MOTTLE + MOTTLE * (nz[x, y] / 255.0)
                    m[x, y] = int(m[x, y] * f)

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
    frames = [wave(i) for i in range(FRAMES)]
    path = os.path.join(outdir, 'TSSONICW.ZIP')
    write_zip(path, 'tssonicw', frames)
    print(f'wrote {path} ({len(frames)} frames, {CANVAS}px canvas)')


if __name__ == '__main__':
    main()
