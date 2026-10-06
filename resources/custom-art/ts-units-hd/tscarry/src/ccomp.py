"""ccomp.py - TS's voxels drawn flat against the model drawn flat, from several directions (the game's frame 0 and
others): overlap per view and a sheet of the differences (red: the voxels' only, blue: the model's only, grey: both).
    python3 ccomp.py out.png [views] [zoom]       views: game,east,side,top,front,back (comma separated)"""
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy.spatial import ConvexHull
import rc
import cmodel as T
import cvoxd as V
from ccam import CANVAS, PPU, ORIGIN, unit_to_world

SS = 2
C = np.array([[a, b, c] for a in (0, 1) for b in (0, 1) for c in (0, 1)], float)
_p = np.pad(V.OCC, 1)
_inner = (_p[2:, 1:-1, 1:-1] & _p[:-2, 1:-1, 1:-1] & _p[1:-1, 2:, 1:-1] & _p[1:-1, :-2, 1:-1] & _p[1:-1, 1:-1, 2:] &
          _p[1:-1, 1:-1, :-2])
VOX = np.argwhere(V.OCC & ~_inner).astype(float)

# view: (facing, elevation, canvas origin shift)
VIEWS = {'game': (24, 32.0), 'g28': (28, 32.0), 'g20': (20, 32.0), 'g16': (16, 32.0), 'g12': (12, 32.0),
         'g8': (8, 32.0), 'g4': (4, 32.0), 'g0': (0, 32.0), 'side': (24, 0.3), 'top': (24, 89.7), 'front': (16, 0.3),
         'back': (0, 0.3)}


def cam_for(view):
    f, el = VIEWS[view]
    o = ORIGIN
    if el < 1:
        o = (o[0], o[1] + 30)
    return f, rc.Cam((0, -1), el, PPU, o)


def vox_cov(view):
    f, cam = cam_for(view)
    Mx = unit_to_world(f)
    F = T.FH
    R, t = F.pose()
    Rw, tw = Mx @ R, Mx @ t

    def scr(q):
        w = (F.mn + q * F.sc) @ Rw.T + tw
        x, y = cam.project(w)
        return np.stack([x, y], -1)
    c0 = scr(C)
    hv = ConvexHull(c0).vertices
    base = scr(VOX)
    off = c0[hv] - scr(np.zeros((1, 3)))
    im = Image.new('L', (CANVAS[0] * SS, CANVAS[1] * SS), 0)
    d = ImageDraw.Draw(im)
    for b in base:
        d.polygon([tuple(q) for q in (b[None, :] + off) * SS], fill=255)
    return np.array(im).reshape(CANVAS[1], SS, CANVAS[0], SS).mean(axis=(1, 3)) >= 127.5


def model_cov(view, m):
    f, cam = cam_for(view)
    parts, _, _ = T.posed(m, ('hull',), unit_to_world(f))
    t, who, nrm, O = rc.render_ids(parts, cam, 0, 0, CANVAS[0], CANVAS[1], ss=SS, zstart=300.0)
    return (who >= 0).reshape(CANVAS[1], SS, CANVAS[0], SS).mean(axis=(1, 3)) >= 0.5


def bbox(a):
    ys, xs = np.nonzero(a)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def sheet(out, views, zoom=1):
    m = T.model()
    tiles = []
    ious = {}
    for v in views:
        va = vox_cov(v); mc = model_cov(v, m)
        iou = (va & mc).sum() / (va | mc).sum()
        ious[v] = iou
        print('%-7s overlap %.3f  voxel-only %5d px  model-only %5d px' % (v, iou, (va & ~mc).sum(), (mc & ~va).sum()),
              flush=True)
        x0, y0, x1, y1 = bbox(va | mc)
        x0, y0, x1, y1 = max(x0 - 6, 0), max(y0 - 6, 0), min(x1 + 6, CANVAS[0]), min(y1 + 6, CANVAS[1])
        rgb = np.full(va.shape + (3,), 40, np.uint8)
        rgb[va & mc] = (150, 150, 150)
        rgb[va & ~mc] = (230, 60, 50)
        rgb[mc & ~va] = (60, 120, 240)
        im = Image.fromarray(rgb[y0:y1, x0:x1])
        if zoom != 1:
            im = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
        dr = ImageDraw.Draw(im)
        dr.text((4, 2), '%s %.3f' % (v, iou), fill=(255, 255, 255))
        tiles.append(im)
    W = max(t.width for t in tiles); H = sum(t.height for t in tiles)
    s = Image.new('RGB', (W, H), (20, 20, 20)); y = 0
    for t in tiles:
        s.paste(t, (0, y)); y += t.height
    s.save(out)
    return ious


if __name__ == '__main__':
    views = sys.argv[2].split(',') if len(sys.argv) > 2 else ['game', 'side', 'top', 'front', 'back']
    zoom = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    sheet(sys.argv[1], views, zoom)


def zoom_sheet(out, view, crops, zoom=3):
    """parts of one view's difference image, zoomed: crops in canvas px (x0, y0, x1, y1)."""
    m = T.model()
    va = vox_cov(view); mc = model_cov(view, m)
    rgb = np.full(va.shape + (3,), 40, np.uint8)
    rgb[va & mc] = (150, 150, 150)
    rgb[va & ~mc] = (230, 60, 50)
    rgb[mc & ~va] = (60, 120, 240)
    tiles = []
    for c in crops:
        im = Image.fromarray(rgb[c[1]:c[3], c[0]:c[2]]).resize(((c[2] - c[0]) * zoom, (c[3] - c[1]) * zoom), Image.NEAREST)
        tiles.append(im)
    W = sum(t.width for t in tiles) + 6 * (len(tiles) - 1); H = max(t.height for t in tiles)
    s = Image.new('RGB', (W, H), (20, 20, 20)); x = 0
    for t in tiles:
        s.paste(t, (x, 0)); x += t.width + 6
    s.save(out)
