"""cmpsheet.py - TS (the mod's current frames) | v1 | v2, frame by frame, on a ground colour.
    python3 cmpsheet.py out.png newdir frames [zoom] [label] [cols]"""
import sys
from PIL import Image, ImageDraw, ImageFont
import os
from paths import HANDOFF
INMOD = HANDOFF + '/03-TSHMEC/in-mod/tshmec/frames/tshmec-%04d.png'
V1 = os.environ.get('V1_FRAMES', '/home/claude/units/work/hmec/pkg/ts-hmec-hd/frames') + '/tshmec-%04d.png'
BG = (110, 106, 84, 255)
CROP = (60, 96, 516, 480)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)


def tile(p, z, crop=CROP):
    a = Image.open(p).convert('RGBA')
    b = Image.new('RGBA', a.size, BG); b.alpha_composite(a)
    c = b.crop(crop)
    return c.resize((int(c.width * z), int(c.height * z)), Image.LANCZOS)


def sheet(out, new, ks, z=0.8, lab='v2', with_v1=True, crop=CROP):
    cols = [('TS (the mod now)', INMOD)] + ([('v1', V1)] if with_v1 else []) + [(lab, new + '/tshmec-%04d.png')]
    W = int((crop[2] - crop[0]) * z); H = int((crop[3] - crop[1]) * z)
    S = Image.new('RGB', (len(cols) * (W + 6), len(ks) * (H + 6) + 24), (30, 30, 30))
    d = ImageDraw.Draw(S)
    for j, (name, _) in enumerate(cols):
        d.text((j * (W + 6) + 8, 4), name, font=font, fill=(240, 230, 180))
    for i, k in enumerate(ks):
        for j, (name, pat) in enumerate(cols):
            S.paste(tile(pat % k, z, crop).convert('RGB'), (j * (W + 6), 24 + i * (H + 6)))
        d.text((6, 24 + i * (H + 6) + 4), 'frame %d' % k, font=font, fill=(240, 240, 240))
    S.save(out)
    return S.size


if __name__ == '__main__':
    out, new, ks = sys.argv[1], sys.argv[2], [int(a) for a in sys.argv[3].split(',')]
    z = float(sys.argv[4]) if len(sys.argv) > 4 else 0.8
    lab = sys.argv[5] if len(sys.argv) > 5 else 'v2'
    print(sheet(out, new, ks, z, lab))
