"""Render the Construction Yard in both views.
  iso: TS's own camera at the scale and place the building has in the mod now (TS x3, canvas 384x256)
  ra:  the RA grid camera (32 degrees, looking north), the pad's south edge on the plot's south edge"""
import sys, time
import numpy as np
from PIL import Image
import hd, yard as Y, ymat as M, ydamage as D

BOUNDS = ((-200, 200), (-200, 200), 200)
ZMAX = 200.0
PLOT = (384, 256)


def iso_view(ss=hd.SS):
    # in-mod: TS's frame x3, TS px (14, 55.5) at the canvas origin; TS's ground centre is (72, 108)
    return hd.ts_view(PLOT, (3 * (72 - 14), 3 * (108 - 55.5)), 3 * hd.TS_PPU, ss=ss)


def ra_view(head=40, ss=hd.SS):
    """canvas grown by `head` px top and bottom; the plot at y head .. head+256; pad's south edge on the
    plot's south edge."""
    H = PLOT[1] + 2 * head
    oy = head + PLOT[1] - np.sin(np.deg2rad(32.0)) * 192.0
    return hd.ra_view((PLOT[0], H), (PLOT[0] / 2, oy), ss=ss)


def render(view, model_kw=None, fan_angle=0.0, lamps=1.0, want=('img', 'trim'), level=0):
    t0 = time.time()
    model = D.model(level) if level else (lambda X, Yy, **k: Y.scene(X, Yy, **k))
    r = hd.Render(model, view, BOUNDS, ZMAX, **(model_kw or {}))
    occ = r.sky_occlusion()
    alb, (bx, by, bz), emit = M.materials(r, fan_angle=fan_angle, lamps=0.0 if level else lamps, occ=occ)
    if level:
        alb = D.mats(r, alb, level)
    nx, ny, nz = r.nx + bx, r.ny + by, r.nz + bz
    nl = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-9
    ao = 0.86 + 0.14 * np.clip(r.z / 40.0, 0, 1)
    col = r.shade(alb, sky_occ=occ, ao=ao, normals=(nx / nl, ny / nl, nz / nl)) + emit
    out = {'img': r.compose(col)}
    if 'trim' in want:
        tm = M.trim_mask(r, alb).astype(np.float32)
        ss = view.ss
        H_, W_ = tm.shape[0] // ss, tm.shape[1] // ss
        out['trim'] = Image.fromarray((tm.reshape(H_, ss, W_, ss).mean(axis=(1, 3)) * 255).round().astype(np.uint8), 'L')
    out['r'] = r
    out['secs'] = time.time() - t0
    return out


if __name__ == '__main__':
    ss = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    level = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    for name, v in (('iso', iso_view(ss)), ("ra", ra_view(52, ss))):
        o = render(v, level=level)
        o['img'].save(f'/home/claude/work/scratch/y-{name}' + (f'-d{level}' if level else '') + '.png')
        a = np.array(o['img'])[..., 3]
        ys, xs = np.nonzero(a > 20)
        print(name, 'size', o['img'].size, 'secs %.1f' % o['secs'], 'bbox x', xs.min(), xs.max(), 'y', ys.min(), ys.max())
