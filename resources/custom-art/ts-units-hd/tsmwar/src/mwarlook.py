"""mwarlook.py - the Mobile War Factory side by side: the mod's frames (TS's voxels as the mod draws them), v1, and a folder of new
frames, for a list of frames, cropped and zoomed.
    python3 mwarlook.py out.png newdir frames [zoom] [label]"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
from paths import HANDOFF

INMOD = HANDOFF + '/14-TSMWAR/in-mod/tsmwar/frames/tsmwar-%04d.png'
V1 = os.environ.get('V1_FRAMES', 'v1/frames') + '/tsmwar-%04d.png'
BG = (110, 106, 84, 255)
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)


def one(pat, k, crop, z):
    b = Image.new('RGBA', (384, 384), BG)
    b.alpha_composite(Image.open(pat % k).convert('RGBA'))
    c = b.crop(crop)
    return c.resize((int(c.width * z), int(c.height * z)), Image.LANCZOS).convert('RGB')


def sheet(out, newpat, ks, z=1.5, label='v2', crop=(56, 52, 328, 268), prev=('v1', V1)):
    cols = [('TS (the mod now)', INMOD), prev, (label, newpat)]
    tiles = [[one(p, k, crop, z) for _, p in cols] for k in ks]
    W, H = tiles[0][0].size
    S = Image.new('RGB', (3 * (W + 6) - 6, len(ks) * (H + 6) + 24), (30, 30, 30))
    d = ImageDraw.Draw(S)
    for j, (name, _) in enumerate(cols):
        d.text((j * (W + 6) + 6, 4), name, font=FONT, fill=(240, 230, 180))
    for i, row in enumerate(tiles):
        for j, t in enumerate(row):
            S.paste(t, (j * (W + 6), 24 + i * (H + 6)))
        d.text((6, 24 + i * (H + 6) + 4), 'frame %d' % ks[i], font=FONT, fill=(240, 230, 180))
    S.save(out)


if __name__ == '__main__':
    out, newdir = sys.argv[1], sys.argv[2]
    ks = [int(a) for a in sys.argv[3].split(',')]
    z = float(sys.argv[4]) if len(sys.argv) > 4 else 1.5
    label = sys.argv[5] if len(sys.argv) > 5 else 'v2'
    sheet(out, newdir + '/tsmwar-%04d.png', ks, z, label)
