"""Feature-by-feature comparison of the war factory model with TS (TS px): bboxes/centroids of TS's green parts, door,
lamps vs the model's components, and a zoomed TS | model | overlay sheet.
    python3 weapcmp.py [out.png] [layout ts]"""
import sys, importlib
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import hd
import procfit as PF

TS = '/home/claude/work/ts/ts-buildings-hd-handoff/06-TSWEAP/ts-original/'
S = 4


def ts(name, f=0):
    return np.array(Image.open(f'{TS}{name}/frames/{f:02d}.png').convert('RGBA')).astype(int)


def greenmask(a):
    return (a[..., 3] > 0) & (a[..., 1] > a[..., 0] + 30) & (a[..., 1] > a[..., 2] + 30)


def bbox(m):
    ys, xs = np.nonzero(m)
    if len(xs) == 0:
        return None
    return (xs.min(), ys.min(), xs.max(), ys.max(), round(xs.mean(), 1), round(ys.mean(), 1), len(xs))


def model_comp(mod, **mk):
    v = PF.view(S, 1)
    r = hd.Render(lambda X, Y, **k: mod.scene(X, Y, **k), v, bounds=((-300, 300), (-260, 260), 260), zmax=260,
                  smooth_px=0.0, **mk)
    comp = np.where(r.hitmask, r.comp, 0)
    # TS pixel centres: canvas px (i + 0.5) * S
    c = comp[S // 2::S, S // 2::S][:168, :192]
    return c, r


def lamp_centres(name, n):
    a = ts(name, 0); m = a[..., 3] > 0
    lab, k = ndimage.label(m)
    return [tuple(round(v, 1) for v in ndimage.center_of_mass(m, lab, i)[::-1]) for i in range(1, k + 1)]


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/work/scratch/weap/cmp.png'
    layout = sys.argv[2] if len(sys.argv) > 2 else 'ts'
    mod = importlib.import_module('weap')
    c, r = model_comp(mod)
    B = ts('GTWEAP'); g = greenmask(B)
    lab, n = ndimage.label(g)
    regions = {'west': (40, 80, 72, 103), 'panel': (45, 100, 77, 135), 'nstrip': (82, 69, 112, 84),
               'ncap': (106, 79, 131, 100), 'gblock': (70, 112, 92, 133), 'fascia': (60, 97, 77, 107),
               'rgreen': (78, 85, 92, 94)}
    comps = {'west': [mod.WESTG], 'panel': [mod.PANEL], 'nstrip': [mod.NSTRIP], 'ncap': [mod.NCAP],
             'gblock': [mod.GBLOCK], 'fascia': [mod.FASCIA], 'rgreen': [mod.GREEN]}
    yy, xx = np.mgrid[0:168, 0:192]
    for k, (x0, y0, x1, y1) in regions.items():
        box = (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)
        t_ = bbox(g & box)
        m_ = bbox(np.isin(c, comps[k]) & box)
        print(f'{k:7s} TS {t_}\n        me {m_}')
    D = ts('GTWEAP_D', 0); print('door    TS', bbox(D[..., 3] > 0)); print('        me', bbox(c == mod.DOOR))
    print('jambs   me', bbox(c == mod.JAMB))
    print('lampsA  TS', lamp_centres('GTWEAP_A', 5))
    la = c == mod.LAMPA; l2, k2 = ndimage.label(la)
    print('        me', [tuple(round(v, 1) for v in ndimage.center_of_mass(la, l2, i)[::-1]) for i in range(1, k2 + 1)])
    print('lampsB  TS', lamp_centres('GTWEAP_B', 3))
    lb = c == mod.LAMPB; l2, k2 = ndimage.label(lb)
    print('        me', [tuple(round(v, 1) for v in ndimage.center_of_mass(lb, l2, i)[::-1]) for i in range(1, k2 + 1)])
    print('fans    TS', lamp_centres('GTWEAP_C', 2))
    fa = c == mod.FAN; l2, k2 = ndimage.label(fa)
    print('        me', [tuple(round(v, 1) for v in ndimage.center_of_mass(fa, l2, i)[::-1]) for i in range(1, k2 + 1)])
    # sheet: TS x6 | model flat x6 | TS green+door edges on model
    Z = 6; box = (28, 60, 140, 146)
    alb = np.zeros(r.x.shape + (3,), np.float32) + 128
    for cc, rgb in mod.FLAT.items():
        alb[r.comp == cc] = rgb
    img = r.compose(r.shade(alb), ground=False, outline=False)
    me = Image.new('RGBA', img.size, PF.BG); me.alpha_composite(img)
    me = me.resize((img.size[0] * Z // S, img.size[1] * Z // S), Image.NEAREST).crop([v * Z for v in box])
    tsim = Image.new('RGBA', (192, 168), PF.BG); tsim.alpha_composite(Image.fromarray(B.astype(np.uint8)))
    tsz = tsim.resize((192 * Z, 168 * Z), Image.NEAREST).crop([v * Z for v in box])
    ov = np.array(me.convert('RGB')).copy()
    for m_, col in ((g, (0, 255, 255)), (D[..., 3] > 0, (255, 0, 255))):
        mz = np.kron(m_, np.ones((Z, Z), bool))[box[1] * Z:box[3] * Z, box[0] * Z:box[2] * Z]
        e = mz & ~ndimage.binary_erosion(mz)
        ov[e] = col
    W, H = tsz.size
    sheet = Image.new('RGB', (W * 3 + 16, H), (30, 30, 30))
    sheet.paste(tsz.convert('RGB'), (0, 0)); sheet.paste(me.convert('RGB'), (W + 8, 0)); sheet.paste(Image.fromarray(ov), (2 * W + 16, 0))
    sheet.save(out)
