"""
mcvrender.py - the TS MCV's HD frames for the mod (TSMCV, 384 x 384, 32 facings counter-clockwise from north:
0 N, 8 W, 16 S, 24 E), each with a -trim.png.  The camera is the RA grid's (orthographic, 32 degrees above the ground,
looking north) at the mod's size: PPU canvas px per voxel, the unit's position (the HVA origin, on the ground) at
ORIGIN, as in-mod/ has it (found by matching the voxel to the in-mod frames: 6.1 px a voxel, TS's 30 degrees, the
ground under the unit at (192, 194)).  The canvas is drawn at two thirds in the game (8 canvas px per classic
pixel), so the outline, the shadow's blur and the contact shadow are 1.5 times as wide (as the Titan's).

    python3 mcvrender.py frames 0,8,16,24 [ss] [outdir] [sky]
"""
import os, sys, time
import numpy as np
from PIL import Image
import rc, rcrender as RR
import mcv as M, mcvmat as MM
from frameio import save

CANVAS = (384, 384)
PPU = 6.1
ORIGIN = (192.0, 194.0)
SHADOW_LEN = 1.0
PX_SCALE = 1.5
BOUNDS = ((-30, 30), (-30, 30), (-1, 18))
OUT = 'out'


def camera():
    return RR.ra_cam(PPU, ORIGIN)


def facing_cw(k, n=32):
    th = 2 * np.pi * k / n
    f = np.array([np.sin(th), -np.cos(th), 0.0]); r = np.array([np.cos(th), np.sin(th), 0.0])
    return np.stack([f, r, np.array([0, 0, 1.0])], axis=1)


def mod_to_cw(f, n=32):
    return (n - f) % n


def find_window(parts, cam, margin=14, step=3):
    W, H = CANVAS
    xs = np.arange(0, W, step) + step / 2; ys = np.arange(0, H, step) + step / 2
    SX, SY = np.meshgrid(xs, ys)
    O = cam.rays(SX.ravel(), SY.ravel())
    t, who, _ = rc.cast(parts, O, cam.D, want_normals=False)
    hit = np.isfinite(t).reshape(SX.shape)
    yy, xx = np.nonzero(hit)
    return (max(int(xs[xx.min()] - margin), 0), max(int(ys[yy.min()] - margin), 0),
            min(int(xs[xx.max()] + margin), W), min(int(ys[yy.max()] + margin), H))


ROUNDED = {M.COVER: 0.3, M.HULL: 0.3, M.DECK: 0.25, M.BLOCK: 0.3, M.CAB: 0.35, M.PANEL: 0.28, M.SHELF: 0.22,
           M.CRATE: 0.25, M.BOOM_W: 0.45, M.BOOM_G: 0.4, M.BOOM_D: 0.4, M.BOOM_T: 0.3, M.TRACK: 0.35, M.TBIT: 0.25,
           M.HITCH: 0.25, M.PLATE: 0.25, M.SADDLE: 0.25, M.RAIL: 0.22, M.BUMPER: 0.25, M.RIM: 0.22, M.SPINE: 0.22,
           M.BAND: 0.22, M.EYE: 0.25, M.RECESS: 0.22, M.POST: 0.15}


def round_edges(r):
    for i, p in enumerate(r.parts):
        sig = ROUNDED.get(p.comp)
        if sig is None:
            continue
        m = (r.who == i) & r.hitmask
        if not m.any():
            continue
        N = np.array([c.n for c in p.cons if c.kind == 'plane']); d = np.array([c.d for c in p.cons if c.kind == 'plane'])
        Q = np.stack([r.x[m], r.y[m], r.z[m]], 1)
        s = Q @ N.T - d[None, :]
        w = np.exp((s - s.max(1, keepdims=True)) / sig)
        n = w @ N
        n = n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)
        r.nx[m], r.ny[m], r.nz[m] = n[:, 0], n[:, 1], n[:, 2]


def spec_hl(r, comps, strength=0.2, power=20.0):
    L = r.L; V = -r.cam.D
    Hh = (L + V) / np.linalg.norm(L + V)
    nh = np.clip(r.nx * Hh[0] + r.ny * Hh[1] + r.nz * Hh[2], 0, 1)
    sh = getattr(r, 'inshadow', 0.0)
    m = np.isin(r.comp, comps)
    return (strength * nh ** power * (1 - 0.9 * sh) * m * 255.0)[..., None] * np.array([1.0, 0.86, 0.58])


def frame(f, ss=4, sky=True, parts_body=None):
    k = mod_to_cw(f)
    Mx = facing_cw(k)
    base = parts_body if parts_body is not None else M.parts()
    parts = [p.moved(Mx) for p in base]
    cam = camera()
    win = find_window(parts, cam)
    r = RR.RCRender(parts, cam, CANVAS, win, BOUNDS, ss=ss, frames=[(Mx, np.zeros(3))] * len(parts),
                    shadow_len=SHADOW_LEN, px_scale=PX_SCALE)
    r.Mb = Mx
    round_edges(r)
    occ = r.sky_occlusion() if sky else None
    alb, (bx, by, bz), emit = MM.materials(r, occ=occ)
    ao = 0.86 + 0.14 * np.clip(r.z / 12.0, 0, 1)
    col = r.shade(alb, sky_occ=occ, ao=ao) + emit
    col = col * np.clip(1 + 0.3 * bz, 0.55, 1.35)[..., None]       # seams darker, studs lighter
    col = col + spec_hl(r, MM.GOLD_COMPS)
    g = r.ground_alpha_full(shadow_parts=parts)
    img = r.compose(col, ground=g)
    tm = MM.trim_mask(r, alb).astype(np.float32)
    full = np.zeros((r.H * ss, r.W * ss), np.float32)
    x0, y0, x1, y1 = r.win
    full[y0 * ss:y1 * ss, x0 * ss:x1 * ss] = tm
    trim = Image.fromarray((full.reshape(r.H, ss, r.W, ss).mean(axis=(1, 3)) * 255).round().astype(np.uint8), 'L')
    return img, trim


if __name__ == '__main__':
    fs = [int(a) for a in sys.argv[2].split(',')] if len(sys.argv) > 2 else range(32)
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    out = sys.argv[4] if len(sys.argv) > 4 else OUT
    sky = bool(int(sys.argv[5])) if len(sys.argv) > 5 else True
    os.makedirs(out, exist_ok=True)
    for f in fs:
        t0 = time.time()
        img, trim = frame(f, ss, sky)
        save(img, trim, f'{out}/tsmcv-{f:04d}.png')
        print('frame', f, '%.0fs' % (time.time() - t0), flush=True)
