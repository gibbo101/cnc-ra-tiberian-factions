"""magnified TS frames with a pixel grid, for reading shapes."""
import sys, os
import numpy as np
from PIL import Image, ImageDraw
from paths import HANDOFF
TSD = HANDOFF + '/02-TSSMEC/ts-original/SMECH/frames/'
BG = (96, 108, 72, 255)

def ts(i):
    return Image.open(TSD + 'smech-%03d.png' % i).convert('RGBA')

def mag(im, k=10, crop=None, grid=True, label=None):
    if crop:
        im = im.crop(crop)
    b = Image.new('RGBA', im.size, BG); b.alpha_composite(im)
    b = b.resize((im.size[0] * k, im.size[1] * k), Image.NEAREST).convert('RGB')
    d = ImageDraw.Draw(b)
    if grid:
        for x in range(0, b.size[0], k):
            d.line([(x, 0), (x, b.size[1])], fill=(70, 80, 56) if (x // k) % 5 else (40, 40, 40))
        for y in range(0, b.size[1], k):
            d.line([(0, y), (b.size[0], y)], fill=(70, 80, 56) if (y // k) % 5 else (40, 40, 40))
    if label:
        d.rectangle([0, 0, 8 * len(label) + 6, 14], fill=(0, 0, 0)); d.text((3, 1), label, fill=(255, 230, 120))
    return b

def sheet(idx, out, k=10, crop=(30, 12, 66, 56), cols=4):
    tiles = [mag(ts(i), k, crop, label=str(i)) for i in idx]
    W, H = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    S = Image.new('RGB', (cols * (W + 4), rows * (H + 4)), (20, 20, 20))
    for j, t in enumerate(tiles):
        S.paste(t, ((j % cols) * (W + 4), (j // cols) * (H + 4)))
    S.save(out)

if __name__ == '__main__':
    idx = [int(a) for a in sys.argv[2].split(',')]
    sheet(idx, sys.argv[1], k=int(sys.argv[3]) if len(sys.argv) > 3 else 10)
