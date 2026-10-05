"""shape check for the Disruptor: the model drawn flat (a colour per part) in the mod's cameras beside the mod's frame,
with the silhouette overlap per frame (the hull's frames 0-31, the turret's 32-63).
    python3 sonshape.py out.png [frames] [zoom]"""
import sys
import numpy as np
from PIL import Image, ImageDraw
import rc
import sonmodel as T
from soncam import flat_cam, unit_to_world, frame_of, CANVAS
from paths import HANDOFF

INMOD = HANDOFF + '/08-TSSONIC/in-mod/tssonic/frames/tssonic-%04d.png'
BG = (96, 108, 72)
COL = {T.OCHRE: (214, 166, 72), T.BELT: (40, 40, 42), T.BODY: (70, 70, 74), T.BLACK: (24, 24, 26),
       T.OLIVE: (110, 104, 70), T.HAZARD: (200, 160, 70), T.RIM: (150, 150, 154), T.BASE: (60, 60, 64),
       T.DISH: (200, 200, 204), T.STRUT: (120, 120, 126), T.BRACE: (112, 116, 150), T.KHAKI: (108, 100, 68),
       T.ARM_CAP: (230, 230, 226), T.ARM: (180, 180, 184), T.ARM_BAND: (196, 196, 200), T.COIL: (80, 80, 86),
       T.ARM_TIP: (130, 130, 136), T.AXLE: (150, 150, 156), T.BRACKET: (200, 160, 70), T.PISTON: (54, 54, 60),
       T.ROD: (110, 110, 116), T.SPRING: (90, 90, 96), T.CROSS: (66, 66, 72), T.GLASS: (50, 60, 80)}


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


def check(ks, out, zoom=1, m=None):
    m = m if m is not None else T.model()
    tiles = []; scores = []
    for k in ks:
        which, facing, tur = frame_of(k)
        parts, _, _ = T.posed(m, which, unit_to_world(facing))
        fl, cov = flat(parts, flat_cam(tur))
        im = Image.open(INMOD % k).convert('RGBA')
        a = np.array(im)[..., 3] > 250
        iou = (a & cov).sum() / max((a | cov).sum(), 1); scores.append(iou)
        crop = (130, 60, 320, 210) if tur else (60, 70, 390, 340)
        W, Ht = crop[2] - crop[0], crop[3] - crop[1]
        z = zoom * (2 if tur else 1)
        t = Image.new('RGB', (2 * W * z + 6, Ht * z + 16), (28, 30, 34))
        for j, x in enumerate((im, fl)):
            b = Image.new('RGBA', x.size, BG + (255,)); b.alpha_composite(x)
            t.paste(b.crop(crop).resize((W * z, Ht * z), Image.NEAREST).convert('RGB'), (j * (W * z + 6), 16))
        ImageDraw.Draw(t).text((4, 2), 'frame %d (%s)   overlap %.3f' % (k, 'turret' if tur else 'hull', iou),
                               fill=(230, 220, 160))
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
    ks = [int(a) for a in sys.argv[2].split(',')] if len(sys.argv) > 2 else list(range(0, 64, 4))
    zoom = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    sc = check(ks, out, zoom)
    print('overlap', np.round(sc, 3), 'mean %.3f' % np.mean(sc))
