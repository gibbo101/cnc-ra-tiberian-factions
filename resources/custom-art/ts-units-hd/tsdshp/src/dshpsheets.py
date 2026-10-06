"""dshpsheets.py - the Dropship's look sheets: frame 0 beside the mod's (and v1's), close-ups, the 8 directions.
    python3 dshpsheets.py outdir framedir [v1]"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from paths import HANDOFF

INMOD = HANDOFF + '/26-TSDSHP/in-mod/tsdshp/frames/tsdshp-%04d.png'
V1 = os.environ.get('V1_FRAMES', 'v1/frames') + '/tsdshp-%04d.png'
V1F = os.environ.get('V1_FACINGS', 'v1/facings') + '/tsdshp-%04d.png'
V2 = os.environ.get('V2_FRAMES', 'v2/frames') + '/tsdshp-%04d.png'
VER = 'v3'                                          # the version being packaged (dshppkg sets it)
PREV = ('v2', V2)                                   # the version before it, for the ship sheet
BG = (112, 108, 92)
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
FONT_S = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)


def on_bg(im, box=None):
    im = im.convert('RGBA')
    if box is not None:
        im = im.crop(box)
    b = Image.new('RGBA', im.size, BG + (255,))
    b.alpha_composite(im)
    return b.convert('RGB')


def content_box(paths, pad=10):
    a = None
    for p in paths:
        al = np.array(Image.open(p).convert('RGBA'))[..., 3] > 8
        a = al if a is None else (a | al)
    ys, xs = np.nonzero(a)
    return (max(xs.min() - pad, 0), max(ys.min() - pad, 0), xs.max() + 1 + pad, ys.max() + 1 + pad)


def label(im, text, font=FONT):
    d = ImageDraw.Draw(im)
    d.text((7, 5), text, font=font, fill=(0, 0, 0))
    d.text((6, 4), text, font=font, fill=(255, 255, 255))
    return im


def stack(tiles, vertical=True, gap=4, bg=(30, 30, 30)):
    if vertical:
        W = max(t.width for t in tiles); H = sum(t.height for t in tiles) + gap * (len(tiles) - 1)
    else:
        W = sum(t.width for t in tiles) + gap * (len(tiles) - 1); H = max(t.height for t in tiles)
    s = Image.new('RGB', (W, H), bg); o = 0
    for t in tiles:
        s.paste(t, (0, o) if vertical else (o, 0)); o += (t.height if vertical else t.width) + gap
    return s


def ship(out, framedir, with_v1=True, zoom=1.0):
    items = [('in the mod now', INMOD % 0)]
    if with_v1:
        items.append((PREV[0], PREV[1] % 0))
    items.append((VER, os.path.join(framedir, 'tsdshp-0000.png')))
    box = content_box([p for _, p in items])
    tiles = []
    for lab, p in items:
        t = on_bg(Image.open(p), box)
        if zoom != 1:
            t = t.resize((int(t.width * zoom), int(t.height * zoom)), Image.LANCZOS)
        tiles.append(label(t, lab))
    stack(tiles).save(out)


def closeups(out, framedir, zoom=3):
    """the nose, the middle and the tail of frame 0: the mod's beside the new version's, at zoom."""
    a = Image.open(INMOD % 0); b = Image.open(os.path.join(framedir, 'tsdshp-0000.png'))
    rows = []
    for name, box in (('nose', (8, 200, 190, 365)), ('middle', (190, 140, 420, 365)), ('tail', (420, 200, 620, 365))):
        ta = on_bg(a, box).resize(((box[2] - box[0]) * zoom, (box[3] - box[1]) * zoom), Image.NEAREST)
        tb = on_bg(b, box).resize(((box[2] - box[0]) * zoom, (box[3] - box[1]) * zoom), Image.LANCZOS)
        rows.append(stack([label(ta, '%s - in the mod now' % name), label(tb, '%s - %s' % (name, VER))], vertical=False, gap=6))
    stack(rows, gap=10).save(out)


def facings(out, framedir, ks=(0, 4, 8, 12, 16, 20, 24, 28), zoom=0.5, cols=4):
    paths = [os.path.join(framedir, 'tsdshp-%04d.png' % k) for k in ks]
    box = content_box(paths, pad=6)
    tiles = []
    for k, p in zip(ks, paths):
        t = on_bg(Image.open(p), box)
        t = t.resize((int(t.width * zoom), int(t.height * zoom)), Image.LANCZOS)
        tiles.append(label(t, '%d' % k, FONT_S))
    rows = [stack(tiles[i:i + cols], vertical=False) for i in range(0, len(tiles), cols)]
    stack(rows).save(out)


if __name__ == '__main__':
    outdir, framedir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    ship(os.path.join(outdir, 'ship.png'), framedir)
    closeups(os.path.join(outdir, 'closeups.png'), framedir)
