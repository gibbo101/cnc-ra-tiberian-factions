"""
crawlgif.py - the crawl (crawlfit.py's poses) beside TS's: TS above HD, the facings side by side, at the game's speed;
and a still sheet of every step.

    python3 crawlgif.py UNIT OUT.gif [FACINGS] [SHEET.png]       FACINGS like 2,0,6,4 (default W N E S)
"""
import json, sys
import numpy as np
from PIL import Image, ImageDraw

NAMES = ['N', 'NW', 'W', 'SW', 'S', 'SE', 'E', 'NE']


def main():
    unit, path = sys.argv[1], sys.argv[2]
    fac = [int(v) for v in sys.argv[3].split(',')] if len(sys.argv) > 3 else [2, 0, 6, 4]
    sheet = sys.argv[4] if len(sys.argv) > 4 else None
    import infunit; infunit.use(unit)
    import inffit as F, infseq as SQ, infall as AL, infcheck as C, crawlfit as CF
    js = json.load(open('%s_shape.json' % unit))
    S = dict(F.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    import os
    res = json.load(open(os.environ.get('FIT', '%s_crawlfit.json' % unit)))
    ims = []
    for s, ks in SQ.frames_of(unit, 'crawl'):
        cols = []
        for f in fac:
            k = ks[f]
            Q = dict(js['Q'], **CF.pose_for(unit, res, s, f))
            pair = []
            for im, lab in ((C.ts_on_canvas(unit, k), 'TS %s' % NAMES[f]), (AL.render_frame(unit, S, js, k, Q, f, ss=3)[0],
                                                                         'HD %s' % NAMES[f])):
                bg = Image.new('RGBA', im.size, (96, 104, 72, 255)); bg.alpha_composite(im.convert('RGBA'))
                t = bg.convert('RGB').crop((48, 30, 220, 150))
                ImageDraw.Draw(t).text((3, 2), lab, fill=(255, 255, 0))
                pair.append(t)
            cols.append(pair)
        w, h = cols[0][0].size
        im = Image.new('RGB', (len(cols) * (w + 3), 2 * (h + 3)), (20, 20, 24))
        for i, pair in enumerate(cols):
            for j, t in enumerate(pair):
                im.paste(t, (i * (w + 3), j * (h + 3)))
        ims.append(im)
    ims[0].save(path, save_all=True, append_images=ims[1:], duration=130, loop=0)
    print(path, ims[0].size)
    if sheet:
        W, H = ims[0].size
        sh = Image.new('RGB', (W, H * len(ims) + 4 * len(ims)), (40, 40, 44))
        for i, im in enumerate(ims):
            sh.paste(im, (0, i * (H + 4)))
        sh.save(sheet)
        print(sheet, sh.size)


if __name__ == '__main__':
    main()
