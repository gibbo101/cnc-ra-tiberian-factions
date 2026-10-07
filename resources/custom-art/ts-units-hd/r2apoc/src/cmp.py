"""cmp.py - the assembled tank (hull frame + turret frame) next to the mod's, for facings.
    python3 cmp.py out.png dir facings [zoom]"""
import sys
from PIL import Image, ImageDraw
from paths import HANDOFF
INMOD = HANDOFF + '/27-R2APOC/in-mod/r2apoc/frames/r2apoc-%04d.png'
BG = (96, 108, 72, 255)
out, d = sys.argv[1], sys.argv[2]
fs = [int(a) for a in sys.argv[3].split(',')]
z = float(sys.argv[4]) if len(sys.argv) > 4 else 1
crop = (40, 50, 408, 330)


def comp(a, b):
    im = Image.new('RGBA', (448, 448), BG)
    im.alpha_composite(Image.open(a).convert('RGBA')); im.alpha_composite(Image.open(b).convert('RGBA'))
    im = im.crop(crop)
    return im.resize((int(im.width * z), int(im.height * z)), Image.LANCZOS)


rows = []
for f in fs:
    rows.append([comp(INMOD % f, INMOD % (32 + f)), comp(d + '/r2apoc-%04d.png' % f, d + '/r2apoc-%04d.png' % (32 + f))])
W, H = rows[0][0].size
S = Image.new('RGB', (2 * W + 6, len(rows) * (H + 4)), (20, 20, 22))
for i, (a, b) in enumerate(rows):
    S.paste(a.convert('RGB'), (0, i * (H + 4))); S.paste(b.convert('RGB'), (W + 6, i * (H + 4)))
S.save(out)
