"""previews for the Titan package: the walk as GIFs (in-mod beside HD), standing facings, the assembled Titan,
and a scale line-up.  Frames are read from a frames folder (the package's or a preview render)."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw

INMOD = __import__('paths').HANDOFF + '/01-TSTITN/in-mod/tstitn/frames/tstitn-%04d.png'
BG = (96, 108, 72, 255)
TICK_MS = 1000 / 15.0          # a game tick at normal speed


def frame(path_fmt, k):
    return Image.open(path_fmt % k).convert('RGBA')


def assembled(path_fmt, f8, step):
    """legs (mod facing f8 of 8, walk step 0-11) with the upper body facing the same way laid over them."""
    legs = frame(path_fmt, f8 * 12 + step)
    torso = frame(path_fmt, 96 + f8 * 4)
    out = Image.new('RGBA', legs.size, BG)
    out.alpha_composite(legs); out.alpha_composite(torso)
    return out


def walk_gif(hd_fmt, f8s, name, crop=(40, 40, 408, 420), scale=1.0, ms=3 * TICK_MS):
    frames = []
    for step in range(12):
        row = []
        for f8 in f8s:
            a = assembled(INMOD, f8, step).crop(crop)
            b = assembled(hd_fmt, f8, step).crop(crop)
            row += [a, b]
        W, H = row[0].size
        canvas = Image.new('RGB', (len(row) * (W + 6), H + 16), (28, 30, 34))
        for i, im in enumerate(row):
            canvas.paste(im.convert('RGB'), (i * (W + 6), 16))
            ImageDraw.Draw(canvas).text((i * (W + 6) + 4, 2), ('in-mod' if i % 2 == 0 else 'HD') + ' facing %d' % f8s[i // 2],
                                        fill=(230, 220, 160))
        if scale != 1.0:
            canvas = canvas.resize((int(canvas.size[0] * scale), int(canvas.size[1] * scale)), Image.LANCZOS)
        frames.append(canvas.convert('P', palette=Image.ADAPTIVE, colors=255))
    frames[0].save(name, save_all=True, append_images=frames[1:], duration=int(ms), loop=0, disposal=1)


def standing_sheet(hd_fmt, name, crop=(40, 40, 408, 420)):
    tiles = []
    for f8 in range(8):
        a = assembled(INMOD, f8, 0).crop(crop); b = assembled(hd_fmt, f8, 0).crop(crop)
        W, H = a.size
        t = Image.new('RGB', (2 * W + 6, H + 16), (28, 30, 34))
        t.paste(a.convert('RGB'), (0, 16)); t.paste(b.convert('RGB'), (W + 6, 16))
        d = ImageDraw.Draw(t); d.text((4, 2), 'in-mod, facing %d' % f8, fill=(230, 220, 160)); d.text((W + 10, 2), 'HD', fill=(230, 220, 160))
        tiles.append(t)
    W, H = tiles[0].size
    out = Image.new('RGB', (2 * (W + 8) + 8, 4 * (H + 8) + 8), (20, 20, 22))
    for i, t in enumerate(tiles):
        out.paste(t, (8 + (i % 2) * (W + 8), 8 + (i // 2) * (H + 8)))
    out.save(name)
    return out
