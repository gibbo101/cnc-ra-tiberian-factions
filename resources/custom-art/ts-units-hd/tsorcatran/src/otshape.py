"""shape check for the Orca Transport: the model drawn flat (a colour per part) in the mod's camera beside TS's voxel drawn
in the same camera (ref/, v1's drawing of ORCATRAN.VXL: the mod has no frames of it yet), with the silhouette overlap
per frame.  The model is where TS's voxel is (no shift).
    python3 otshape.py out.png [frames] [zoom]"""
import sys
import numpy as np
from PIL import Image, ImageDraw
import rc
import otmodel as T
from otcam import flat_cam, unit_to_world, CANVAS
from paths import HERE

INMOD = HERE + '/ref/tsorcatran-%04d.png'
BG = (96, 108, 72)
COL = {T.REAR: (206, 162, 76), T.CORE: (196, 154, 72), T.PANEL: (214, 170, 80), T.BUMPER: (170, 152, 98),
       T.WING: (40, 200, 40), T.HULL: (200, 158, 74), T.STRAKE: (186, 145, 66), T.HATCH: (140, 140, 146),
       T.HUMP: (210, 166, 78), T.FRONT: (40, 200, 40), T.CANOPY: (84, 84, 88), T.FACE: (70, 70, 74),
       T.NOSE: (40, 200, 40), T.DRUM: (168, 156, 112), T.LIP: (132, 124, 88), T.BLADE: (166, 164, 136),
       T.HUB: (170, 170, 174), T.FLOOR: (46, 42, 32), T.STRUT: (150, 150, 156), T.LEGM: (64, 62, 38),
       T.LEG: (64, 62, 38), T.FOOT: (64, 62, 38), T.RAIL: (84, 84, 88), T.BELLY: (40, 200, 40),
       T.DOOR: (190, 150, 70)}
CROP = (10, 50, 486, 400)


def comp_colour(c):
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
    return Image.open(INMOD % k).convert('RGBA')


def check(ks, out, zoom=1, m=None):
    m = m if m is not None else T.model()
    tiles = []; scores = []
    for k in ks:
        parts, _, _ = T.posed(m, ('hull',), unit_to_world(k))
        fl, cov = flat(parts, flat_cam())
        im = inmod(k)
        a = np.array(im)[..., 3] > 250
        iou = (a & cov).sum() / max((a | cov).sum(), 1); scores.append(iou)
        crop = CROP
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
