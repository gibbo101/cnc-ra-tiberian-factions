"""dshplook.py - frames side by side (stacked), cropped to what they draw, over a ground colour, with labels.
    python3 dshplook.py out.png zoom label=path [label=path ...]   (crop: the union of the frames' content)"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from paths import HANDOFF

INMOD = HANDOFF + '/26-TSDSHP/in-mod/tsdshp/frames/tsdshp-%04d.png'
V1 = os.environ.get('V1_FRAMES', 'v1/frames') + '/tsdshp-%04d.png'
BG = (112, 108, 92)
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)


def load(p):
    if p == 'inmod':
        p = INMOD % 0
    elif p == 'v1':
        p = V1 % 0
    return Image.open(p).convert('RGBA')


def sheet(items, zoom=1.0, crop=None, bg=BG, vertical=True):
    ims = [(lab, load(p)) for lab, p in items]
    if crop is None:
        a = np.zeros(ims[0][1].size[::-1], bool)
        for _, im in ims:
            a |= np.array(im)[..., 3] > 8
        ys, xs = np.nonzero(a)
        crop = (max(xs.min() - 8, 0), max(ys.min() - 8, 0), xs.max() + 9, ys.max() + 9)
    tiles = []
    for lab, im in ims:
        c = im.crop(crop)
        base = Image.new('RGBA', c.size, bg + (255,))
        base.alpha_composite(c)
        base = base.convert('RGB')
        if zoom != 1:
            base = base.resize((int(base.width * zoom), int(base.height * zoom)), Image.LANCZOS if zoom < 1 else Image.NEAREST)
        d = ImageDraw.Draw(base)
        d.text((6, 4), lab, font=FONT, fill=(255, 255, 255))
        tiles.append(base)
    if vertical:
        W = max(t.width for t in tiles); H = sum(t.height for t in tiles) + 4 * (len(tiles) - 1)
        s = Image.new('RGB', (W, H), (30, 30, 30)); y = 0
        for t in tiles:
            s.paste(t, (0, y)); y += t.height + 4
    else:
        W = sum(t.width for t in tiles) + 4 * (len(tiles) - 1); H = max(t.height for t in tiles)
        s = Image.new('RGB', (W, H), (30, 30, 30)); x = 0
        for t in tiles:
            s.paste(t, (x, 0)); x += t.width + 4
    return s


if __name__ == '__main__':
    out, zoom = sys.argv[1], float(sys.argv[2])
    items = [a.split('=', 1) for a in sys.argv[3:]]
    sheet(items, zoom).save(out)
