"""the Titan package's previews, from its final frames.

    python3 makepreviews.py PKG
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
import titanpreview as TP, shapesheets as SS, scalepreview as SP, titan as TN, shapecheck as SC
from tspal import load

BG = (96, 108, 72, 255)


def ts_assembled(f8):
    """TS's own sprite, legs (standing) and upper body, scaled x6.4 onto the 448 canvas as the mod has it."""
    k8 = TN.mod_to_cw(f8, 8)
    legs = load(k8 * 15).astype(np.uint8); torso = load(120 + 4 * k8).astype(np.uint8)
    im = Image.fromarray(legs, 'RGBA'); im.alpha_composite(Image.fromarray(torso, 'RGBA'))
    big = Image.new('RGBA', (448, 448), (0, 0, 0, 0))
    # TS (47.5, 55) -> canvas (224, 386), x6.4 nearest
    sc = im.resize((round(95 * 6.4), round(95 * 6.4)), Image.NEAREST)
    big.alpha_composite(sc, (round(224 - 47.5 * 6.4), round(386 - 55 * 6.4)))
    return big


def standing(fmt, name, crop=(60, 50, 400, 420), scale=0.62):
    tiles = []
    for f8 in range(8):
        cols = [('TS', ts_assembled(f8)), ('in-mod', TP.assembled(TP.INMOD, f8, 0)), ('HD', TP.assembled(fmt, f8, 0))]
        W, H = crop[2] - crop[0], crop[3] - crop[1]
        t = Image.new('RGB', (3 * W + 12, H + 18), (28, 30, 34))
        for i, (lab, im) in enumerate(cols):
            b = Image.new('RGBA', im.size, BG); b.alpha_composite(im)
            t.paste(b.crop(crop).convert('RGB'), (i * (W + 6), 18))
            ImageDraw.Draw(t).text((i * (W + 6) + 4, 3), '%s  facing %d' % (lab, f8) if i == 0 else lab, fill=(230, 220, 160))
        t = t.resize((int(t.size[0] * scale), int(t.size[1] * scale)), Image.LANCZOS)
        tiles.append(t)
    return SC.grid(tiles, 2, name)


def turn_gif(fmt, name, legs_f8=6, crop=(40, 40, 408, 420), scale=0.8, ms=100):
    frames = []
    for f in range(32):
        legs = Image.open(fmt % (legs_f8 * 12)).convert('RGBA')
        body = Image.open(fmt % (96 + f)).convert('RGBA')
        im = Image.new('RGBA', legs.size, BG); im.alpha_composite(legs); im.alpha_composite(body)
        im = im.crop(crop).convert('RGB')
        im = im.resize((int(im.size[0] * scale), int(im.size[1] * scale)), Image.LANCZOS)
        ImageDraw.Draw(im).text((4, 3), 'upper body %d' % (96 + f), fill=(230, 220, 160))
        frames.append(im.convert('P', palette=Image.ADAPTIVE, colors=255))
    frames[0].save(name, save_all=True, append_images=frames[1:], duration=ms, loop=0, disposal=1)


if __name__ == '__main__':
    pkg = sys.argv[1]
    fmt = pkg + '/frames/tstitn-%04d.png'
    pv = pkg + '/previews'
    os.makedirs(pv, exist_ok=True)
    standing(fmt, pv + '/standing-8-facings.png')
    TP.walk_gif(fmt, [6], pv + '/walk-east.gif', crop=(70, 60, 440, 420), scale=0.8)
    TP.walk_gif(fmt, [4], pv + '/walk-south.gif', crop=(60, 40, 400, 430), scale=0.8)
    turn_gif(fmt, pv + '/turn.gif')
    SP.lineup(fmt, pv + '/scale.png')
    print('previews done')
