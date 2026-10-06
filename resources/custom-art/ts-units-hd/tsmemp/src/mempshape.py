"""shape check for the Mobile EMP Cannon: the model drawn flat (a colour per part) in the mod's camera beside the mod's
frame, with the silhouette overlap per frame.  The mod's frames float the unit LOW_PX higher (TS's voxel floats); the
model stands on the ground, so the mod's frames are moved down LOW_PX before they are compared (as v1's check did).
    python3 mempshape.py out.png [frames] [zoom]"""
import sys
import numpy as np
from PIL import Image, ImageDraw
import rc
import mempmodel as T
from mempcam import flat_cam, unit_to_world, CANVAS, LOW_PX
from paths import HANDOFF

INMOD = HANDOFF + '/13-TSMEMP/in-mod/tsmemp/frames/tsmemp-%04d.png'
BG = (96, 108, 72)
COL = {T.BELT: (40, 40, 42), T.WHEEL: (176, 176, 180), T.HUB: (90, 90, 94), T.HOUSING: (120, 120, 124),
       T.DECK: (186, 145, 66), T.LEDGE: (150, 130, 80), T.LIP: (140, 140, 144), T.TOWER: (130, 130, 134),
       T.COLLAR: (150, 150, 154), T.ORB: (210, 235, 245), T.CROWN: (190, 190, 194), T.PLINTH: (108, 100, 68),
       T.BOX: (140, 140, 146), T.PIPE: (110, 110, 116), T.MOUNT: (90, 90, 96), T.EMITTER: (200, 240, 255),
       T.GLASS: (44, 52, 64)}


def comp_colour(c):
    if c in T.HOUSE:
        return np.array([40, 200, 40.])
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


def inmod(k):
    """the mod's frame k moved down LOW_PX (onto the ground, where the model stands)."""
    im = Image.open(INMOD % k).convert('RGBA')
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    out.paste(im, (0, int(round(LOW_PX))))
    return out


def check(ks, out, zoom=1, m=None):
    m = m if m is not None else T.model()
    tiles = []; scores = []
    for k in ks:
        parts, _, _ = T.posed(m, ('hull',), unit_to_world(k))
        fl, cov = flat(parts, flat_cam())
        im = inmod(k)
        a = np.array(im)[..., 3] > 250
        iou = (a & cov).sum() / max((a | cov).sum(), 1); scores.append(iou)
        crop = (50, 60, 334, 320)
        W, Ht = crop[2] - crop[0], crop[3] - crop[1]
        z = zoom
        t = Image.new('RGB', (2 * W * z + 6, Ht * z + 16), (28, 30, 34))
        for j, x in enumerate((im, fl)):
            b = Image.new('RGBA', x.size, BG + (255,)); b.alpha_composite(x)
            t.paste(b.crop(crop).resize((W * z, Ht * z), Image.NEAREST).convert('RGB'), (j * (W * z + 6), 16))
        ImageDraw.Draw(t).text((4, 2), 'frame %d   overlap %.3f' % (k, iou), fill=(230, 220, 160))
        tiles.append(t)
    cols = 2
    Wt = max(t.size[0] for t in tiles); Ht = max(t.size[1] for t in tiles)
    S = Image.new('RGB', (cols * (Wt + 6), ((len(tiles) + cols - 1) // cols) * (Ht + 6)), (20, 20, 20))
    for i, t in enumerate(tiles):
        S.paste(t, ((i % cols) * (Wt + 6), (i // cols) * (Ht + 6)))
    S.save(out)
    return scores


if __name__ == '__main__':
    out = sys.argv[1]
    ks = [int(a) for a in sys.argv[2].split(',')] if len(sys.argv) > 2 else list(range(0, 32, 4))
    zoom = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    sc = check(ks, out, zoom)
    print('overlap', np.round(sc, 3), 'mean %.3f' % np.mean(sc))
