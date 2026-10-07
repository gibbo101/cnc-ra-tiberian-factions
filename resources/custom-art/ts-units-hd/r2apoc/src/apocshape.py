"""shape check for the Apocalypse: the model drawn flat (a colour per part) in the mod's cameras beside the mod's frame,
with the silhouette overlap per frame (the hull's frames 0-31, the turret's 32-63).  The mod's turret frames are moved
to where the turret is drawn and scaled to its size (K_TUR) about its base (inmod_turret()) before they are compared:
v4 drew the whole turret at 0.69; v5 draws it at the mod's size again (a scale of 1 here), only its pad smaller (Luke),
standing on the deck and centred on the hull (so it sits a few px lower and 1.5 px left of the mod's).
    python3 apocshape.py out.png [frames] [zoom]"""
import sys
import numpy as np
from PIL import Image, ImageDraw
import rc
import apocmodel as T
from apoccam import flat_cam, unit_to_world, frame_of, CANVAS, PPU_T, PPU_T0, ORIGIN_T0, ORIGIN_T, Z_BASE, GZ, ELEV
Z_BASE_TS = Z_BASE + GZ
from paths import HANDOFF

INMOD = HANDOFF + '/27-R2APOC/in-mod/r2apoc/frames/r2apoc-%04d.png'
BG = (96, 108, 72)
COL = {T.OLIVE: (126, 126, 96), T.BELT: (36, 36, 38), T.WHEEL: (130, 130, 134), T.HUB: (80, 80, 84),
       T.GRILLE: (40, 40, 42), T.BLACK: (30, 30, 32), T.LAMP: (40, 40, 42), T.PLOUGH: (66, 66, 70), T.RAM: (110, 110, 116),
       T.TUR: (172, 172, 141), T.HATCH: (66, 66, 70), T.AERIAL: (40, 40, 42), T.POD: (66, 66, 70),
       T.TUBE: (66, 66, 70), T.STRAP: (50, 50, 54), T.MOUNT: (56, 56, 60), T.BARREL: (60, 60, 64),
       T.SLEEVE: (70, 70, 74), T.MUZZLE: (50, 50, 54), T.MANTLET: (80, 80, 84), T.HOOK: (106, 106, 106)}


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


def inmod_turret(k):
    """the mod's turret frame k brought to where and how big the drawn turret is: its base (TS's turntable foot, drawn
    by the mod's camera) moved onto the drawn turret's base (v5: on the deck, its pivot where the hull's unit position
    is), scaled to the drawn turret's size about it (v5: the mod's own size)."""
    im = Image.open(INMOD % k).convert('RGBA')
    s = PPU_T / PPU_T0
    ce = np.cos(np.deg2rad(ELEV))
    bx, by = ORIGIN_T0[0], ORIGIN_T0[1] - Z_BASE_TS * PPU_T0 * ce          # the mod's turret base on its canvas
    cx, cy = ORIGIN_T[0], ORIGIN_T[1] - Z_BASE * PPU_T * ce                # the drawn turret's base
    # out = c + s (in - b)  ->  in = b + (out - c) / s
    a = 1 / s
    return im.transform(im.size, Image.AFFINE, (a, 0, bx - a * cx, 0, a, by - a * cy), resample=Image.BICUBIC)


def inmod(k):
    return inmod_turret(k) if k >= 32 else Image.open(INMOD % k).convert('RGBA')


def check(ks, out, zoom=1, m=None):
    m = m if m is not None else T.model()
    tiles = []; scores = []
    for k in ks:
        which, facing, tur = frame_of(k)
        parts, _, _ = T.posed(m, which, unit_to_world(facing))
        fl, cov = flat(parts, flat_cam(tur))
        im = inmod(k)
        a = np.array(im)[..., 3] > 250
        iou = (a & cov).sum() / max((a | cov).sum(), 1); scores.append(iou)
        crop = (90, 110, 370, 260) if tur else (40, 60, 408, 330)
        W, Ht = crop[2] - crop[0], crop[3] - crop[1]
        z = zoom
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
