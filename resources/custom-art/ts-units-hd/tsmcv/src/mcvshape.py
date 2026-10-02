"""shape check for the MCV: the model drawn flat (a colour per part) in the camera Luke's voxel render uses (the
in-mod frames: 30 degrees, 6.1 canvas px a voxel, the unit's position at (192, 194)), beside the in-mod frame, with
the silhouette overlap per facing.

    python3 mcvshape.py out.png [facings, default 0,4,...,28] [zoom]
"""
import sys
import numpy as np
from PIL import Image, ImageDraw
import rc
import mcv as M
from mcvrender import facing_cw, mod_to_cw

from paths import HANDOFF
INMOD = HANDOFF + '/11-TSMCV/in-mod/tsmcv/frames/tsmcv-%04d.png'
BG = (96, 108, 72)
FLAT = {M.COVER: (0, 200, 0), M.TRACK: (40, 38, 34), M.TBIT: (70, 60, 40), M.HULL: (150, 116, 50),
        M.UNDER: (70, 64, 44), M.DECK: (214, 170, 80), M.BUMPER: (60, 60, 66), M.BLOCK: (236, 150, 52),
        M.PANEL: (0, 150, 0), M.CAB: (240, 196, 100), M.PLATE: (196, 150, 64), M.SADDLE: (120, 96, 50),
        M.BOOM_D: (96, 96, 100), M.BOOM_G: (150, 150, 158), M.BOOM_W: (230, 230, 236), M.BOOM_T: (90, 90, 96),
        M.RAIL: (60, 58, 56), M.SHELF: (150, 110, 50), M.CRATE: (226, 160, 60), M.RECESS: (110, 88, 44),
        M.HITCH: (255, 140, 30), M.EYE: (30, 30, 30), M.RIM: (190, 150, 64), M.SPINE: (170, 136, 60),
        M.POST: (60, 58, 34), M.BAND: (44, 40, 20)}
for _c in range(100, 140):
    FLAT.setdefault(_c, (255, 0, 255))


def inmod_cam():
    return rc.Cam((0, -1), 30.0, 6.1, (192.0, 194.0))


def flat(parts, cam, ss=2, size=384):
    t, who, nrm, O = rc.render_ids(parts, cam, 0, 0, size, size, ss=ss, zstart=200.0)
    img = np.zeros(who.shape + (4,), np.float32)
    for i, p in enumerate(parts):
        img[who == i, :3] = FLAT.get(p.comp, (255, 0, 255)); img[who == i, 3] = 255
    im = img.reshape(size, ss, size, ss, 4).mean(axis=(1, 3))
    cov = (who >= 0).reshape(size, ss, size, ss).mean(axis=(1, 3)) >= 0.5
    return Image.fromarray(im.round().astype(np.uint8), 'RGBA'), cov


def check(fs, out, zoom=2, crop=(40, 60, 344, 300), parts_fn=None):
    base = (parts_fn or M.parts)()
    cam = inmod_cam()
    tiles = []; scores = []
    for f in fs:
        Mx = facing_cw(mod_to_cw(f))
        parts = [p.moved(Mx) for p in base]
        fl, cov = flat(parts, cam)
        im = Image.open(INMOD % f).convert('RGBA')
        a = np.array(im)[..., 3] > 128
        iou = (a & cov).sum() / max((a | cov).sum(), 1); scores.append(iou)
        W, H = crop[2] - crop[0], crop[3] - crop[1]
        t = Image.new('RGB', (2 * W * zoom + 6, H * zoom + 16), (28, 30, 34))
        for j, x in enumerate((im, fl)):
            b = Image.new('RGBA', x.size, BG + (255,)); b.alpha_composite(x)
            t.paste(b.crop(crop).resize((W * zoom, H * zoom), Image.NEAREST).convert('RGB'), (j * (W * zoom + 6), 16))
        ImageDraw.Draw(t).text((4, 2), 'facing %d   overlap %.3f' % (f, iou), fill=(230, 220, 160))
        tiles.append(t)
    cols = 2
    Wt, Ht = tiles[0].size
    S = Image.new('RGB', (cols * (Wt + 6), ((len(tiles) + cols - 1) // cols) * (Ht + 6)), (20, 20, 20))
    for i, t in enumerate(tiles):
        S.paste(t, ((i % cols) * (Wt + 6), (i // cols) * (Ht + 6)))
    S.save(out)
    return scores


if __name__ == '__main__':
    out = sys.argv[1]
    fs = [int(a) for a in sys.argv[2].split(',')] if len(sys.argv) > 2 else list(range(0, 32, 4))
    zoom = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    sc = check(fs, out, zoom)
    print('overlap', np.round(sc, 3), 'mean %.3f' % np.mean(sc))
