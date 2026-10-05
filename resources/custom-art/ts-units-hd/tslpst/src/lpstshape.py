"""shape check for the Mobile Sensor Array: the model drawn flat (a colour per part) in the mod's camera beside the
mod's frame, with the silhouette overlap per frame.
    python3 lpstshape.py out.png [frames] [zoom]"""
import sys
import numpy as np
from PIL import Image, ImageDraw
import rc
import lpstmodel as T
from lpstcam import flat_cam, unit_to_world, CANVAS
from paths import HANDOFF

INMOD = HANDOFF + '/12-TSLPST/in-mod/tslpst/frames/tslpst-%04d.png'
BG = (96, 108, 72)
COL = {T.COVER: (70, 70, 74), T.BELT: (40, 40, 42), T.WHEEL: (90, 90, 94), T.HUB: (150, 150, 156), T.CORE: (20, 20, 20),
       T.BUMPER: (80, 80, 84), T.MAST: (36, 36, 38), T.LAMP: (255, 230, 110), T.REARLAMP: (255, 230, 110),
       T.DISH: (130, 132, 138), T.HINGE: (64, 64, 68), T.CRADLE: (78, 78, 82)}


def comp_colour(c):
    if c in T.HOUSE:
        return np.array([40, 200, 40.])
    if c in T.OCHRE_PARTS or c == T.MOUNT:
        return np.array([200, 160, 80.]) * (0.85 if c in (T.KEEL, T.DECK) else 1.0)
    return np.array(COL.get(c, (255, 0, 255)), float)


def flat(parts, cam, ss=2, size=CANVAS[0]):
    t, who, nrm, O = rc.render_ids(parts, cam, 0, 0, size, size, ss=ss, zstart=300.0)
    L = np.array([-0.45, -0.55, 0.70]); L /= np.linalg.norm(L)
    img = np.zeros(who.shape + (4,), np.float32)
    sh = 0.55 + 0.45 * np.clip((nrm * L).sum(-1), 0, 1)
    for i, p in enumerate(parts):
        m = who == i
        if m.any():
            img[m, :3] = comp_colour(p.comp) * sh[m, None]; img[m, 3] = 255
    im = img.reshape(size, ss, size, ss, 4).mean(axis=(1, 3))
    cov = (who >= 0).reshape(size, ss, size, ss).mean(axis=(1, 3)) >= 0.5
    return Image.fromarray(np.clip(im, 0, 255).round().astype(np.uint8), 'RGBA'), cov


def check(ks, out, zoom=1, crop=(62, 52, 322, 292), m=None):
    m = m if m is not None else T.model()
    tiles = []; scores = []
    for k in ks:
        parts, _ = T.posed(m, unit_to_world(k))
        fl, cov = flat(parts, flat_cam())
        im = Image.open(INMOD % k).convert('RGBA')
        a = np.array(im)[..., 3] > 250
        iou = (a & cov).sum() / max((a | cov).sum(), 1); scores.append(iou)
        W, Ht = crop[2] - crop[0], crop[3] - crop[1]
        t = Image.new('RGB', (2 * W * zoom + 6, Ht * zoom + 16), (28, 30, 34))
        for j, x in enumerate((im, fl)):
            b = Image.new('RGBA', x.size, BG + (255,)); b.alpha_composite(x)
            t.paste(b.crop(crop).resize((W * zoom, Ht * zoom), Image.NEAREST).convert('RGB'), (j * (W * zoom + 6), 16))
        ImageDraw.Draw(t).text((4, 2), 'frame %d   overlap %.3f' % (k, iou), fill=(230, 220, 160))
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
    ks = [int(a) for a in sys.argv[2].split(',')] if len(sys.argv) > 2 else [0, 4, 8, 12, 16, 20, 24, 28]
    zoom = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    sc = check(ks, out, zoom)
    print('overlap', np.round(sc, 3), 'mean %.3f' % np.mean(sc))
