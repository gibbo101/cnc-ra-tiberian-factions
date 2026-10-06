"""otvents.py - TS's back vents against HD's: TS's voxel drawn in the mod's camera (ref/) and the HD frame's close-up
(otclose.py), the same window round the back at 3x, facing by facing.

    python3 otvents.py out.png [facings] [hd frames pattern: close-ups rendered when omitted]
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import otclose as C
from paths import HERE

FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
BG = (118, 124, 112)
REF = os.path.join(HERE, 'ref', 'tsorcatran-%04d.png')


def ts_tile(k, crop, Z=3):
    im = Image.open(REF % k).convert('RGBA')
    b = Image.new('RGBA', im.size, BG + (255,)); b.alpha_composite(im)
    c = b.crop(crop).convert('RGB')
    return c.resize((c.width * Z, c.height * Z), Image.NEAREST)


def sheet(out, ks=(0, 4, 28), Z=3, ss=2, w=150, h=110):
    rows = []
    for k in ks:
        crop = C.q_crop(k, (5.0, 19.0, 7.0), w, h)
        rows.append([(ts_tile(k, crop, Z), "TS's voxels  facing %d" % k), (C.close(k, Z, ss, crop), 'HD  facing %d' % k)])
    W, H = rows[0][0][0].size
    S = Image.new('RGB', (2 * W + 6, len(rows) * (H + 6) - 6), (30, 30, 30))
    d = ImageDraw.Draw(S)
    for i, row in enumerate(rows):
        for j, (t, lab) in enumerate(row):
            S.paste(t, (j * (W + 6), i * (H + 6)))
            d.text((j * (W + 6) + 6, i * (H + 6) + 4), lab, font=FONT, fill=(250, 240, 170))
    S.save(out)
    return S.size


if __name__ == '__main__':
    ks = [int(a) for a in sys.argv[2].split(',')] if len(sys.argv) > 2 else (0, 4, 28)
    print(sheet(sys.argv[1], ks))
