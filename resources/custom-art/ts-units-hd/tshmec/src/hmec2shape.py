"""shape check for the Mk. II: the model drawn flat (a colour per part) in the mod's camera (35 degrees, 6.8 canvas
px a voxel, the unit's position at (287.5, 374)), beside the in-mod frame, with the silhouette overlap per frame.

    python3 hmec2shape.py out.png [frames, default every 4th facing at step 0] [zoom]
"""
import sys
import numpy as np
from PIL import Image, ImageDraw
import rc
import hmec2 as H
from hmec2cam import flat_cam, unit_to_world, frame_of, CANVAS
import hview

from paths import HANDOFF
INMOD = HANDOFF + '/03-TSHMEC/in-mod/tshmec/frames/tshmec-%04d.png'
BG = (96, 108, 72)


def flat(parts, cam, ss=2, size=576):
    t, who, nrm, O = rc.render_ids(parts, cam, 0, 0, size, size, ss=ss, zstart=300.0)
    L = np.array([-0.45, -0.55, 0.70]); L /= np.linalg.norm(L)
    img = np.zeros(who.shape + (4,), np.float32)
    nr = nrm.reshape(who.shape + (3,)) if nrm.ndim == 2 else nrm
    sh = 0.55 + 0.45 * np.clip((nr * L).sum(-1), 0, 1)
    for i, p in enumerate(parts):
        m = who == i
        if m.any():
            img[m, :3] = hview.comp_colour(p.comp) * sh[m, None]; img[m, 3] = 255
    im = img.reshape(size, ss, size, ss, 4).mean(axis=(1, 3))
    cov = (who >= 0).reshape(size, ss, size, ss).mean(axis=(1, 3)) >= 0.5
    return Image.fromarray(np.clip(im, 0, 255).round().astype(np.uint8), 'RGBA'), cov


def check(ks, out, zoom=1, crop=(60, 100, 516, 476), m=None):
    m = m if m is not None else H.model()
    cam = flat_cam()
    tiles = []; scores = []
    for k in ks:
        f, hf = frame_of(k)
        parts, _, _ = H.posed(m, hf, unit_to_world(f))
        fl, cov = flat(parts, cam)
        im = Image.open(INMOD % k).convert('RGBA')
        a = np.array(im)[..., 3] > 250
        iou = (a & cov).sum() / max((a | cov).sum(), 1); scores.append(iou)
        W, Ht = crop[2] - crop[0], crop[3] - crop[1]
        t = Image.new('RGB', (2 * W * zoom + 6, Ht * zoom + 16), (28, 30, 34))
        for j, x in enumerate((im, fl)):
            b = Image.new('RGBA', x.size, BG + (255,)); b.alpha_composite(x)
            t.paste(b.crop(crop).resize((W * zoom, Ht * zoom), Image.NEAREST).convert('RGB'), (j * (W * zoom + 6), 16))
        ImageDraw.Draw(t).text((4, 2), 'frame %d (facing %d, HVA %d)   overlap %.3f' % (k, f, hf, iou), fill=(230, 220, 160))
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
    ks = [int(a) for a in sys.argv[2].split(',')] if len(sys.argv) > 2 else [f * 8 for f in range(0, 32, 4)]
    zoom = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    sc = check(ks, out, zoom)
    print('overlap', np.round(sc, 3), 'mean %.3f' % np.mean(sc))
