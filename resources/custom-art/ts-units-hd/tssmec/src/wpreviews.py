"""the Wolverine package's previews, from its final frames.

    python3 wpreviews.py PKG
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
import wolfhd as WH
import wshape as WS

BG = (96, 108, 72, 255)
INMOD = WS.INMOD
TICK_MS = 1000 / 15.0
from paths import HANDOFF, TITAN_FRAMES
TITAN = TITAN_FRAMES + '/tstitn-%04d.png'
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'


def on_bg(im):
    b = Image.new('RGBA', im.size, BG); b.alpha_composite(im)
    return b


def gif_pair(hd_fmt, frames_list, facings, name, crop=(90, 60, 350, 330), scale=0.8, ms=2 * TICK_MS, tag='walk'):
    """in-mod beside HD for each facing, stepping through frames_list(f) together."""
    seq = [frames_list(f) for f in facings]
    out = []
    for i in range(len(seq[0])):
        row = []
        for f, fr in zip(facings, seq):
            row += [(f, 'in-mod', on_bg(Image.open(INMOD % fr[i]).convert('RGBA')).crop(crop)),
                    (f, 'HD', on_bg(Image.open(hd_fmt % fr[i]).convert('RGBA')).crop(crop))]
        W, H = row[0][2].size
        canvas = Image.new('RGB', (len(row) * (W + 6), H + 16), (28, 30, 34))
        for j, (f, lab, im) in enumerate(row):
            canvas.paste(im.convert('RGB'), (j * (W + 6), 16))
            ImageDraw.Draw(canvas).text((j * (W + 6) + 4, 2), '%s %s facing %d' % (lab, tag, f), fill=(230, 220, 160))
        canvas = canvas.resize((int(canvas.size[0] * scale), int(canvas.size[1] * scale)), Image.LANCZOS)
        out.append(canvas.convert('P', palette=Image.ADAPTIVE, colors=255))
    out[0].save(name, save_all=True, append_images=out[1:], duration=int(ms), loop=0, disposal=1)


def lineup(hd_fmt, name):
    """the Wolverine next to the HD Titan and the HD harvester, facing east, on one ground line, at the size the
    game draws them (the TS units' canvases at 2/3, the harvester as it is)."""
    wolf = Image.open(hd_fmt % 72).convert('RGBA')
    wolf = wolf.resize((round(wolf.size[0] * 2 / 3), round(wolf.size[1] * 2 / 3)), Image.LANCZOS)
    items = [('TS Harvester (HD)', Image.open(HARV % 24).convert('RGBA'))]
    if os.path.exists(TITAN % 72):
        titan = Image.open(TITAN % 72).convert('RGBA'); titan.alpha_composite(Image.open(TITAN % 120).convert('RGBA'))
        titan = titan.resize((round(titan.size[0] * 2 / 3), round(titan.size[1] * 2 / 3)), Image.LANCZOS)
        items.append(('Titan (HD)', titan))
    items.append(('Wolverine (HD)', wolf))
    gap = 10
    W = sum(im.size[0] for _, im in items) + gap * (len(items) + 1) - 40 * (len(items) - 1)
    H = 330
    out = Image.new('RGBA', (W, H), BG)
    ground = 300
    x = gap
    d = ImageDraw.Draw(out)
    for lab, im in items:
        w, h = im.size
        a = np.array(im)
        solid = (a[..., 3] > 250) & (a[..., :3].max(-1) > 40)
        low = np.nonzero(solid.any(1))[0].max()
        out.alpha_composite(im, (x, ground - low))
        d.text((x + w // 2 - 45, H - 20), lab, fill=(240, 232, 190))
        x += w + gap - 40
    out.convert('RGB').save(name)


if __name__ == '__main__':
    pkg = sys.argv[1]
    fmt = pkg + '/frames/tssmec-%04d.png'
    pv = pkg + '/previews'
    os.makedirs(pv, exist_ok=True)
    WS.hd_sheet(fmt, [f * 12 for f in range(8)], [WH.mod_to_cw(f) * 12 for f in range(8)], pv + '/standing-8-facings.png',
                labels=['facing %d' % f for f in range(8)])
    walk = lambda f: [f * 12 + s for s in range(12)]
    fire = lambda f: [96 + f * 4 + s for s in range(4)] * 3
    gif_pair(fmt, walk, [6, 4], pv + '/walk-east-south.gif')
    gif_pair(fmt, walk, [5, 1], pv + '/walk-southeast-northwest.gif')
    gif_pair(fmt, fire, [4, 6], pv + '/fire-south-east.gif', tag='fire')
    gif_pair(fmt, fire, [3, 7], pv + '/fire-southwest-northeast.gif', tag='fire')
    lineup(fmt, pv + '/scale.png')
    print('previews done')
