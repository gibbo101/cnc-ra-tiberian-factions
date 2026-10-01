import json, sys
import numpy as np
from PIL import Image, ImageDraw
import shapecheck as SC, titan as TN, titanpreview as TP, gait as G


def hd_vs_inmod(hd_fmt, name, crop=(60, 50, 400, 420), scale=0.8):
    tiles = []
    for f8 in range(8):
        a = TP.assembled(TP.INMOD, f8, 0).crop(crop)
        b = TP.assembled(hd_fmt, f8, 0).crop(crop)
        W, H = a.size
        t = Image.new('RGB', (2 * W + 6, H + 18), (28, 30, 34))
        t.paste(a.convert('RGB'), (0, 18)); t.paste(b.convert('RGB'), (W + 6, 18))
        d = ImageDraw.Draw(t)
        d.text((4, 3), 'in-mod  (legs %d + upper body %d)' % (f8 * 12, 96 + f8 * 4), fill=(230, 220, 160))
        d.text((W + 10, 3), 'HD', fill=(230, 220, 160))
        if scale != 1:
            t = t.resize((int(t.size[0] * scale), int(t.size[1] * scale)), Image.LANCZOS)
        tiles.append(t)
    return SC.grid(tiles, 2, name)


if __name__ == '__main__':
    S, poses = TN.load_legs(); P = TN.load_torso()
    g = poses['gait']
    im, sc = SC.legs_sheet(S, lambda s: g.pose(2 * np.pi * s / 15), step=0, name='out/shape-legs.png')
    print('legs overlaps', np.round(sc, 2), 'mean %.3f' % np.mean(sc))
    im, sc = SC.torso_sheet(P, name='out/shape-upper-body.png')
    print('upper body overlaps', np.round(sc, 2), 'mean %.3f' % np.mean(sc))
    if len(sys.argv) > 1:
        hd_vs_inmod(sys.argv[1], 'out/standing-8-facings.png')
