"""the MCV v2 package's previews, from its final frames.

    python3 mcvpreviews.py PKG
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
from paths import HANDOFF

BG = (110, 106, 84, 255)
INMOD = HANDOFF + '/11-TSMCV/in-mod/tsmcv/frames/tsmcv-%04d.png'
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
RA_MCV = HANDOFF + '/11-TSMCV/reference-hd/RA_MCV/frames/mcv-%04d.png'
TD_MCV = HANDOFF + '/11-TSMCV/reference-hd/TD_MCV/frames/mcv-%04d.png'


def on_bg(im):
    b = Image.new('RGBA', im.size, BG); b.alpha_composite(im)
    return b


def label(im, text, xy=(4, 2), col=(230, 220, 160)):
    ImageDraw.Draw(im).text(xy, text, fill=col)
    return im


def facings_sheet(hd_fmt, fs, name, crop=(30, 50, 350, 310), scale=0.8):
    """in-mod beside HD for each facing, two pairs a row."""
    tiles = []
    for f in fs:
        W, H = crop[2] - crop[0], crop[3] - crop[1]
        t = Image.new('RGB', (2 * W + 6, H + 16), (28, 30, 34))
        for j, (lab, src) in enumerate((('in-mod', INMOD), ('HD', hd_fmt))):
            t.paste(on_bg(Image.open(src % f).convert('RGBA')).crop(crop).convert('RGB'), (j * (W + 6), 16))
            label(t, '%s  frame %d' % (lab, f), (j * (W + 6) + 4, 2))
        tiles.append(t.resize((int(t.size[0] * scale), int(t.size[1] * scale)), Image.LANCZOS))
    Wt, Ht = tiles[0].size
    out = Image.new('RGB', (2 * (Wt + 8) + 8, ((len(tiles) + 1) // 2) * (Ht + 8) + 8), (20, 22, 26))
    for i, t in enumerate(tiles):
        out.paste(t, (8 + (i % 2) * (Wt + 8), 8 + (i // 2) * (Ht + 8)))
    out.save(name)


def turn_gif(hd_fmt, name, crop=(30, 50, 350, 310), scale=0.75, ms=120):
    """all 32 facings in turn, in-mod beside HD."""
    out = []
    for f in range(32):
        W, H = crop[2] - crop[0], crop[3] - crop[1]
        t = Image.new('RGB', (2 * W + 6, H + 16), (28, 30, 34))
        for j, (lab, src) in enumerate((('in-mod', INMOD), ('HD', hd_fmt))):
            t.paste(on_bg(Image.open(src % f).convert('RGBA')).crop(crop).convert('RGB'), (j * (W + 6), 16))
            label(t, '%s  frame %d' % (lab, f), (j * (W + 6) + 4, 2))
        t = t.resize((int(t.size[0] * scale), int(t.size[1] * scale)), Image.LANCZOS)
        out.append(t.convert('P', palette=Image.ADAPTIVE, colors=255))
    out[0].save(name, save_all=True, append_images=out[1:], duration=ms, loop=0, disposal=1)


def lineup(hd_fmt, name):
    """the MCV next to the HD harvester and EA's RA and TD MCVs, facing east, on one ground line, at the size the
    game draws them (the mod's 384 canvas at 2/3; the harvester's and EA's canvases as they are)."""
    mcv = Image.open(hd_fmt % 24).convert('RGBA')
    mcv = mcv.resize((round(mcv.size[0] * 2 / 3), round(mcv.size[1] * 2 / 3)), Image.LANCZOS)
    items = [('TS Harvester (HD)', Image.open(HARV % 24).convert('RGBA')),
             ("EA's RA MCV", Image.open(RA_MCV % 24).convert('RGBA')),
             ("EA's TD MCV", Image.open(TD_MCV % 24).convert('RGBA')),
             ('TS MCV (HD)', mcv)]
    crops = []
    for lab, im in items:
        a = np.array(im)
        ys, xs = np.nonzero(a[..., 3] > 0)
        crops.append((lab, im.crop((max(xs.min() - 6, 0), 0, min(xs.max() + 7, im.size[0]), im.size[1]))))
    gap = 26
    W = sum(im.size[0] for _, im in crops) + gap * (len(crops) + 1)
    H = 230
    out = Image.new('RGBA', (W, H), BG)
    ground = 190
    x = gap
    d = ImageDraw.Draw(out)
    for lab, im in crops:
        w, h = im.size
        a = np.array(im)
        solid = (a[..., 3] > 250) & (a[..., :3].max(-1) > 40)
        low = np.nonzero(solid.any(1))[0].max()
        out.alpha_composite(im, (x, ground - low))
        d.text((x + w // 2 - 40, H - 20), lab, fill=(240, 232, 190))
        x += w + gap
    out.convert('RGB').save(name)


def facings32(hd_fmt, name, version, crop=(24, 56, 360, 324), scale=0.5):
    """all 32 facings, 8 a row, counter-clockwise from north, labelled with the version."""
    W, H = int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale)
    out = Image.new('RGB', (8 * (W + 4) + 4, 4 * (H + 18) + 34), (28, 30, 34))
    d = ImageDraw.Draw(out)
    d.text((8, 8), 'TS MCV in HD  -  %s  -  32 facings, counter-clockwise from north (0 N, 8 W, 16 S, 24 E)' % version,
           fill=(240, 230, 180))
    for f in range(32):
        t = on_bg(Image.open(hd_fmt % f).convert('RGBA')).crop(crop).resize((W, H), Image.LANCZOS).convert('RGB')
        x = 4 + (f % 8) * (W + 4); y = 30 + (f // 8) * (H + 18)
        out.paste(t, (x, y + 14))
        d.text((x + 2, y), 'frame %d' % f, fill=(200, 200, 190))
    out.save(name)


if __name__ == '__main__':
    pkg = sys.argv[1]
    fmt = pkg + '/frames/tsmcv-%04d.png'
    pv = pkg + '/previews'
    os.makedirs(pv, exist_ok=True)
    facings_sheet(fmt, list(range(0, 32, 4)), pv + '/8-facings.png')
    turn_gif(fmt, pv + '/turn.gif')
    lineup(fmt, pv + '/scale.png')
    facings32(fmt, pv + '/32-facings.png', sys.argv[2] if len(sys.argv) > 2 else 'v2')
    print('previews done')
