"""the Mammoth Mk. II v2 package's previews, from its final frames.

    python3 hmec2previews.py PKG [version]
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
from paths import HANDOFF, TITAN_FRAMES

BG = (110, 106, 84, 255)
INMOD = HANDOFF + '/03-TSHMEC/in-mod/tshmec/frames/tshmec-%04d.png'
HARV = HANDOFF + '/00-TSHARV-example/frames/harvester-%02d.png'
MAMMOTH = HANDOFF + '/03-TSHMEC/reference-hd/RA_4TNK/frames/4tnk-%04d.png'
TITAN = TITAN_FRAMES + '/tstitn-%04d.png'
TICK_MS = 1000 / 15.0
CROP = (40, 60, 540, 500)


def on_bg(im):
    b = Image.new('RGBA', im.size, BG); b.alpha_composite(im)
    return b


def label(im, text, xy=(4, 2), col=(230, 220, 160)):
    ImageDraw.Draw(im).text(xy, text, fill=col)
    return im


def pair(hd_fmt, k, crop=CROP):
    W, H = crop[2] - crop[0], crop[3] - crop[1]
    t = Image.new('RGB', (2 * W + 6, H + 16), (28, 30, 34))
    for j, (lab, src) in enumerate((('in-mod', INMOD), ('HD', hd_fmt))):
        t.paste(on_bg(Image.open(src % k).convert('RGBA')).crop(crop).convert('RGB'), (j * (W + 6), 16))
        label(t, '%s  frame %d' % (lab, k), (j * (W + 6) + 4, 2))
    return t


def facings_sheet(hd_fmt, name, scale=0.62):
    tiles = [pair(hd_fmt, f * 8) for f in range(0, 32, 4)]
    tiles = [t.resize((int(t.size[0] * scale), int(t.size[1] * scale)), Image.LANCZOS) for t in tiles]
    Wt, Ht = tiles[0].size
    out = Image.new('RGB', (2 * (Wt + 8) + 8, 4 * (Ht + 8) + 8), (20, 22, 26))
    for i, t in enumerate(tiles):
        out.paste(t, (8 + (i % 2) * (Wt + 8), 8 + (i // 2) * (Ht + 8)))
    out.save(name)


def walk_gif(hd_fmt, facings, name, scale=0.5):
    frames = []
    for step in range(8):
        row = [pair(hd_fmt, f * 8 + step) for f in facings]
        W, H = row[0].size
        c = Image.new('RGB', (len(row) * (W + 8), H), (20, 22, 26))
        for i, t in enumerate(row):
            c.paste(t, (i * (W + 8), 0))
        c = c.resize((int(c.size[0] * scale), int(c.size[1] * scale)), Image.LANCZOS)
        frames.append(c.convert('P', palette=Image.ADAPTIVE, colors=255))
    frames[0].save(name, save_all=True, append_images=frames[1:], duration=int(8 * TICK_MS), loop=0, disposal=1)


def turn_gif(hd_fmt, name, scale=0.5, ms=120):
    """all 32 facings in turn (step 0), in-mod beside HD."""
    out = []
    for f in range(32):
        t = pair(hd_fmt, f * 8)
        t = t.resize((int(t.size[0] * scale), int(t.size[1] * scale)), Image.LANCZOS)
        out.append(t.convert('P', palette=Image.ADAPTIVE, colors=255))
    out[0].save(name, save_all=True, append_images=out[1:], duration=ms, loop=0, disposal=1)


def facings32(hd_fmt, name, version, crop=CROP, scale=0.34):
    """all 32 facings at step 0, 8 a row, counter-clockwise from north, labelled with the version."""
    W, H = int((crop[2] - crop[0]) * scale), int((crop[3] - crop[1]) * scale)
    out = Image.new('RGB', (8 * (W + 4) + 4, 4 * (H + 18) + 34), (28, 30, 34))
    d = ImageDraw.Draw(out)
    d.text((8, 8), 'Mammoth Mk. II in HD  -  %s  -  32 facings at step 0, counter-clockwise from north (0 N, 8 W, 16 S, '
           '24 E)' % version, fill=(240, 230, 180))
    for f in range(32):
        t = on_bg(Image.open(hd_fmt % (f * 8)).convert('RGBA')).crop(crop).resize((W, H), Image.LANCZOS).convert('RGB')
        x = 4 + (f % 8) * (W + 4); y = 30 + (f // 8) * (H + 18)
        out.paste(t, (x, y + 14))
        d.text((x + 2, y), 'facing %d (frame %d)' % (f, f * 8), fill=(200, 200, 190))
    out.save(name)


def lineup(hd_fmt, name):
    """the Mk. II next to the HD harvester, the HD Titan and EA's Mammoth, facing east, on one ground line, at the
    size the game draws them (the mod's TS canvases at 2/3, the harvester's and EA's as they are)."""
    def two_thirds(im):
        return im.resize((round(im.size[0] * 2 / 3), round(im.size[1] * 2 / 3)), Image.LANCZOS)
    items = [('TS Harvester (HD)', Image.open(HARV % 24).convert('RGBA'))]
    m = Image.open(MAMMOTH % 0).convert('RGBA'); m.alpha_composite(Image.open(MAMMOTH.replace('%04d', '0032-0000')).convert('RGBA'))
    items.append(("EA's Mammoth (facing north)", m))
    if os.path.exists(TITAN % 72):
        t = Image.open(TITAN % 72).convert('RGBA'); t.alpha_composite(Image.open(TITAN % 120).convert('RGBA'))
        items.append(('Titan (HD)', two_thirds(t)))
    items.append(('Mammoth Mk. II (HD)', two_thirds(Image.open(hd_fmt % 192).convert('RGBA'))))
    crops = []
    for lab, im in items:
        a = np.array(im)
        ys, xs = np.nonzero(a[..., 3] > 0)
        crops.append((lab, im.crop((max(xs.min() - 6, 0), 0, min(xs.max() + 7, im.size[0]), im.size[1]))))
    gap = 24
    W = sum(im.size[0] for _, im in crops) + gap * (len(crops) + 1)
    H = 330
    out = Image.new('RGBA', (W, H), BG)
    ground = 290
    x = gap
    d = ImageDraw.Draw(out)
    for lab, im in crops:
        w, h = im.size
        a = np.array(im)
        solid = (a[..., 3] > 250) & (a[..., :3].max(-1) > 30)
        low = np.nonzero(solid.any(1))[0].max()
        out.alpha_composite(im, (x, ground - low))
        d.text((x + w // 2 - 45, H - 20), lab, fill=(240, 232, 190))
        x += w + gap
    out.convert('RGB').save(name)


if __name__ == '__main__':
    pkg = sys.argv[1]
    ver = sys.argv[2] if len(sys.argv) > 2 else 'v2'
    fmt = pkg + '/frames/tshmec-%04d.png'
    pv = pkg + '/previews'
    os.makedirs(pv, exist_ok=True)
    facings_sheet(fmt, pv + '/8-facings.png')
    facings32(fmt, pv + '/32-facings.png', ver)
    turn_gif(fmt, pv + '/turn.gif')
    walk_gif(fmt, [24, 20], pv + '/walk-east-southeast.gif')
    walk_gif(fmt, [16, 4], pv + '/walk-south-northwest.gif')
    lineup(fmt, pv + '/scale.png')
    print('previews done')
