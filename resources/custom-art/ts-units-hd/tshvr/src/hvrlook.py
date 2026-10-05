"""hvrlook.py - the Hover MLRS side by side: the mod's frames, v1 and a folder of new frames, each assembled (shadow 64 + f,
hull f, rack 32 + f laid over each other on one canvas, the engine's seat for the rack not applied, as v1's previews),
or one set (hull / rack / shadow), cropped and zoomed.
    python3 hvrlook.py out.png newdir facings [zoom] [label] [set: unit|hull|rack|shadow]"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from paths import HANDOFF

INMOD = HANDOFF + '/07-TSHVR/in-mod/tshvr/frames/tshvr-%04d.png'
V1 = os.environ.get('V1_FRAMES', 'v1/frames') + '/tshvr-%04d.png'
BG = (110, 106, 84, 255)
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
SETS = {'unit': lambda f: [64 + f, f, 32 + f], 'hull': lambda f: [f], 'rack': lambda f: [32 + f],
        'shadow': lambda f: [64 + f]}


def assembled(pat, ks):
    """frames laid over each other: each an index, or (index, dx, dy) drawn shifted by whole px (the rack's seat)."""
    b = Image.new('RGBA', (192, 192), BG)
    for k in ks:
        k, dx, dy = (k, 0, 0) if isinstance(k, (int, np.integer)) else k
        im = Image.open(pat % k).convert('RGBA')
        if dx or dy:
            sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); sh.paste(im, (int(round(dx)), int(round(dy)))); im = sh
        b.alpha_composite(im)
    return b


def one(pat, ks, crop, z, nearest):
    c = assembled(pat, ks).crop(crop)
    return c.resize((int(c.width * z), int(c.height * z)), Image.NEAREST if nearest else Image.LANCZOS).convert('RGB')


def sheet(out, newpat, fs, z=3, label='v2', crop=(26, 30, 166, 160), prev=('v1', V1), which='unit', seat=None):
    """seat: f -> (dx, dy), the new frames' rack drawn seated (TS's and v1's racks are drawn where their frames have it,
    the engine's seat tables not applied)."""
    cols = [('TS (the mod now)', INMOD, True), (prev[0], prev[1], False), (label, newpat, False)]
    def ks(j, f):
        k = SETS[which](f)
        if seat is not None and j == 2 and which == 'unit':
            k = [64 + f, f, (32 + f,) + tuple(seat(f))]
        return k
    tiles = [[one(p, ks(j, f), crop, z, nn) for j, (_, p, nn) in enumerate(cols)] for f in fs]
    W, H = tiles[0][0].size
    S = Image.new('RGB', (3 * (W + 6) - 6, len(fs) * (H + 6) + 22), (30, 30, 30))
    d = ImageDraw.Draw(S)
    for j, (name, _, _) in enumerate(cols):
        d.text((j * (W + 6) + 6, 3), name, font=FONT, fill=(240, 230, 180))
    for i, row in enumerate(tiles):
        for j, t in enumerate(row):
            S.paste(t, (j * (W + 6), 22 + i * (H + 6)))
        d.text((6, 22 + i * (H + 6) + 4), '%s facing %d' % (which, fs[i]), font=FONT, fill=(240, 230, 180))
    S.save(out)
    return S.size


if __name__ == '__main__':
    out, newdir = sys.argv[1], sys.argv[2]
    fs = [int(a) for a in sys.argv[3].split(',')]
    z = float(sys.argv[4]) if len(sys.argv) > 4 else 3
    label = sys.argv[5] if len(sys.argv) > 5 else 'v2'
    which = sys.argv[6] if len(sys.argv) > 6 else 'unit'
    print(sheet(out, newdir + '/tshvr-%04d.png', fs, z, label, which=which))
