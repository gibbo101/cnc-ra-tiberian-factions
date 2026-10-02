"""Extra previews for the Radar package (bdeliver extra_previews):
  shape-check.png     the model in TS's own camera (flat colours) over TS's frame, healthy (GTRADR 00 + A 00) and
                      damaged (01 + A 15): TS | model / model edges on TS | TS's edges on the model, silhouette and green
  dish-sweep.png      the dish's 15 positions, TS's and ours (TS angle), healthy and damaged"""
import numpy as np
from PIL import Image, ImageDraw
import radr as M, radrfit as F
import ypreview as P


def shape_check(pk, out):
    rows = []
    for lv, dk in ((0, 0), (1, 15)):
        img, r = F.flat(M, 4, dish_t=0.0, dmg=lv)
        tmp = f'{out}/_shape{lv}.png'
        iou, giou = F.sheet(img, F.ts_frame(dk, lv), tmp, 4, r=r, mod=M)
        im = Image.open(tmp).convert('RGBA')
        R = Image.new('RGBA', (im.width, im.height + 24), (30, 30, 30, 255))
        R.paste(im, (0, 24))
        P.label(R, f"{('healthy: GTRADR 00 + GTRADR_A 00', 'damaged: GTRADR 01 + GTRADR_A 15')[lv]}  (TS's own camera, 4x)", (6, 4))
        rows.append(R)
        import os
        os.remove(tmp)
    pk.stack(rows, 8).save(f'{out}/shape-check.png')


def dish_sweep(pk, out):
    T = f"{pk.s['hand']}/ts-original"
    tiles = []
    for lv in (0, 1):
        for t in range(0, 15, 2):
            ts = pk.ts_canvas([f"{T}/GTRADR/frames/{lv:02d}.png", f"{T}/GTRADR_A/frames/{t + 15 * lv:02d}.png"])
            ours = pk.scene('iso', lv, 0)
            ours = pk.building('iso', lv); ours.alpha_composite(pk.fr('iso', 'A-dish', f'radar-dish-{t + 15 * lv:02d}'))
            box = (40, 30, 236, 230)
            a = P.on_bg(ts.crop(box)); b = P.on_bg(ours.crop(box))
            tiles.append((a, b, f"{('healthy', 'damaged')[lv]} A {t + 15 * lv:02d}"))
    w, h = tiles[0][0].size
    S = Image.new('RGBA', (8 * (w + 4), 4 * (h + 18)), (30, 30, 30, 255))
    d = ImageDraw.Draw(S)
    for k, (a, b, lab) in enumerate(tiles):
        col, lv = k % 8, k // 8
        S.paste(a, (col * (w + 4), (2 * lv) * (h + 18) + 16)); S.paste(b, (col * (w + 4), (2 * lv + 1) * (h + 18) + 16))
        d.text((col * (w + 4) + 3, (2 * lv) * (h + 18) + 2), 'TS ' + lab, fill=(255, 255, 0, 255))
        d.text((col * (w + 4) + 3, (2 * lv + 1) * (h + 18) + 2), 'HD ' + lab, fill=(255, 255, 0, 255))
    S.save(f'{out}/dish-sweep.png')


EXTRAS = [shape_check, dish_sweep]
