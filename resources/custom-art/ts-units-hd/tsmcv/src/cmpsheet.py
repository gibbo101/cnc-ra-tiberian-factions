"""cmpsheet.py - TS (the mod's current frames) | v1 | v2, facing by facing, on a ground colour.
    python3 cmpsheet.py out.png newdir facings [zoom] [label]"""
import sys
from PIL import Image, ImageDraw, ImageFont
from paths import HANDOFF
INMOD = HANDOFF + '/11-TSMCV/in-mod/tsmcv/frames/tsmcv-%04d.png'
import os
V1 = os.environ.get('V1_FRAMES', 'v1/frames') + '/tsmcv-%04d.png'      # v1's frames, for comparing
BG = (110, 106, 84, 255)
CROP = (24, 56, 360, 324)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)


def tile(p, z):
    a = Image.open(p).convert('RGBA')
    b = Image.new('RGBA', a.size, BG); b.alpha_composite(a)
    c = b.crop(CROP)
    return c.resize((int(c.width * z), int(c.height * z)), Image.LANCZOS)


if __name__ == '__main__':
    out, v2, fs = sys.argv[1], sys.argv[2], [int(a) for a in sys.argv[3].split(',')]
    z = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
    lab = sys.argv[5] if len(sys.argv) > 5 else 'v2'
    cols = (('TS (the mod now)', INMOD), ('v1', V1), (lab, v2 + '/tsmcv-%04d.png'))
    W = int((CROP[2] - CROP[0]) * z); H = int((CROP[3] - CROP[1]) * z)
    S = Image.new('RGB', (len(cols) * (W + 6), len(fs) * (H + 6) + 24), (30, 30, 30))
    d = ImageDraw.Draw(S)
    for j, (name, _) in enumerate(cols):
        d.text((j * (W + 6) + 8, 4), name, font=font, fill=(240, 230, 180))
    for i, f in enumerate(fs):
        for j, (name, pat) in enumerate(cols):
            S.paste(tile(pat % f, z).convert('RGB'), (j * (W + 6), 24 + i * (H + 6)))
        d.text((6, 24 + i * (H + 6) + 4), 'facing %d' % f, font=font, fill=(240, 240, 240))
    S.save(out)
    print(S.size)
