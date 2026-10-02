"""
wolfrender.py - the Wolverine's HD frames for the mod (TSSMEC, 384 x 384, 128 frames), each with a -trim.png:
   0-95    the walk: mod facing f (counter-clockwise from north) x 12 steps + step
   96-127  firing: 96 + facing x 4 + step, the flash on steps 0 and 2
Every frame carries the unit's baked ground shadow (alpha 191, as the buildings and the Titan).

    python3 wolfrender.py frames 0,48,96 [ss] [outdir]
"""
import os, sys, time
import numpy as np
from PIL import Image
from scipy import ndimage
import rc, rcrender as RR
import hd
import wolf as WF, wolfhd as WH, wolfmat as WM, wflash as FL
from frameio import save

OUT = 'out'
SHADOW_LEN = 0.62        # the Titan's: the house light's shadow direction, 62% as long (the units' shadows match)
PX_SCALE = 1.5           # the game draws TS units' canvases at 2/3: outline, blur and contact shadow x 1.5
BOUNDS = ((-15, 15), (-15, 15), (-1, 37))


def camera(model):
    """the RA-grid camera: orthographic, 32 degrees above the ground, looking north, 6.4 canvas px per TS px; the
    unit's position (its turning axis on the ground) at the canvas centre's x, the ground under it at the height TS's
    sprite has it (TS's sprite point (47.5, 53) at canvas (192, 307), as in the mod)."""
    oy = WH.CANVAS_ANCHOR[1] + (model['y0'] - WH.TS_ANCHOR[1]) * WH.PPU
    return RR.ra_cam(WH.PPU, (WH.CANVAS[0] / 2.0, oy))


def find_window(parts, cam, margin=12, step=3):
    W, H = WH.CANVAS
    xs = np.arange(0, W, step) + step / 2; ys = np.arange(0, H, step) + step / 2
    SX, SY = np.meshgrid(xs, ys)
    O = cam.rays(SX.ravel(), SY.ravel())
    t, who, _ = rc.cast(parts, O, cam.D, want_normals=False)
    hit = np.isfinite(t).reshape(SX.shape)
    yy, xx = np.nonzero(hit)
    return (max(int(xs[xx.min()] - margin), 0), max(int(ys[yy.min()] - margin), 0),
            min(int(xs[xx.max()] + margin), W), min(int(ys[yy.max()] + margin), H))


def frame_spec(k):
    """(mod facing, step, firing?) of frame k."""
    if k < 96:
        f, s = divmod(k, 12)
        return f, s, False
    f, s = divmod(k - 96, 4)
    return f, s, True


def spec_hl(r, comps, strength=0.24, power=22.0):
    L = r.L; V = -r.cam.D
    Hh = (L + V) / np.linalg.norm(L + V)
    nh = np.clip(r.nx * Hh[0] + r.ny * Hh[1] + r.nz * Hh[2], 0, 1)
    sh = getattr(r, 'inshadow', 0.0)
    m = np.isin(r.comp, comps)
    return (strength * nh ** power * (1 - 0.9 * sh) * m * 255.0)[..., None] * np.array([1.0, 0.86, 0.58])


def frame(k, model, ss=4, sky=True):
    f, s, firing = frame_spec(k)
    k8 = WH.mod_to_cw(f)
    pose = model['stand'] if firing else WH.walk_pose(model, s)
    parts, M = WH.placed(model, pose, k8)
    cam = camera(model)
    win = find_window(parts, cam)
    r = RR.RCRender(parts, cam, WH.CANVAS, win, BOUNDS, ss=ss, frames=[(M, np.zeros(3))] * len(parts),
                    shadow_len=SHADOW_LEN, px_scale=PX_SCALE)
    round_edges(r)
    part_local(r)
    r.dw = pose[6]
    occ = r.sky_occlusion() if sky else None
    P = model['P']
    alb, (bx, by, bz), emit = WM.materials(r, P, occ=occ)
    ao = 0.86 + 0.14 * np.clip(r.z / 14.0, 0, 1)
    col = r.shade(alb, sky_occ=occ, ao=ao) + emit
    col = col + spec_hl(r, WM.GOLD_COMPS)
    flash = firing and s in (0, 2)
    mz = [M @ m for m in WH.muzzles(model, pose)]
    if flash:
        Ph = np.stack([r.x, r.y, r.z], -1); Nh = np.stack([r.nx, r.ny, r.nz], -1)
        col = col + FL.flash_light(Ph, Nh, mz)
    g = r.ground_alpha_full(shadow_parts=parts)
    img = compose(r, col, g, flash_at=(mz, M, s // 2) if flash else None)
    trim = trim_img(r, alb)
    return img, trim


ROUNDED = {WF.HEAD: 0.42, WF.TORSO: 0.42, WF.WAIST: 0.35, WF.SHOULDER: 0.45, WF.ARM: 0.35, WF.PACK: 0.3,
           WF.GUN: 0.3, WF.THIGH: 0.38, WF.SHIN: 0.35, WF.FOOT: 0.35, WF.PELVIS: 0.35, WH.TOE: 0.25, WH.BELT: 0.12}


def part_local(r):
    """each hit's position in its own part's box frame (r.pu, r.pv, r.pw from the part's centre) and the part's
    half sizes (r.hu, r.hv, r.hw), for detail that moves with a leg; zero for parts that are not boxes."""
    sh = r.x.shape
    r.pu, r.pv, r.pw = (np.zeros(sh, np.float32) for _ in range(3))
    r.hu, r.hv, r.hw = (np.zeros(sh, np.float32) for _ in range(3))
    for i, p in enumerate(r.parts):
        pl = [c for c in p.cons[:6] if c.kind == 'plane']
        if len(pl) < 6 or any(abs(pl[2 * k].n @ pl[2 * k + 1].n + 1) > 1e-6 for k in range(3)):
            continue
        m = (r.who == i) & r.hitmask
        if not m.any():
            continue
        R, c, h = WH.box_frame(p)
        Q = np.stack([r.x[m], r.y[m], r.z[m]], 1) - c
        L = Q @ R
        r.pu[m], r.pv[m], r.pw[m] = L[:, 0], L[:, 1], L[:, 2]
        r.hu[m], r.hv[m], r.hw[m] = h


def round_edges(r):
    """soften the box parts' edges in the shading: near an edge the normal blends towards the next face's (a
    softmax over the part's planes, as the Titan's shell), so the plates read as pressed metal with rounded edges
    rather than sharp cut boxes; the silhouette is unchanged."""
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


def compose(r, col, ground, flash_at=None):
    """RCRender.compose, with the muzzle flashes laid over at the supersampled level, depth-tested."""
    ss = r.ss
    Hs, Ws = r.H * ss, r.W * ss
    x0, y0, x1, y1 = r.win
    hit = np.zeros((Hs, Ws), bool)
    rgb = np.zeros((Hs, Ws, 3), np.float32)
    depth = np.full((Hs, Ws), np.inf, np.float32)
    hit[y0 * ss:y1 * ss, x0 * ss:x1 * ss] = r.hitmask
    rgb[y0 * ss:y1 * ss, x0 * ss:x1 * ss] = np.where(r.hitmask[..., None], col, 0.0)
    dwin = r.x * r.cam.D[0] + r.y * r.cam.D[1] + r.z * r.cam.D[2]
    depth[y0 * ss:y1 * ss, x0 * ss:x1 * ss] = np.where(r.hitmask, dwin, np.inf)
    rgba = np.zeros((Hs, Ws, 4), np.float32)
    rgba[..., :3] = rgb
    rgba[..., 3] = np.where(hit, 1.0, ground if ground is not None else 0.0)
    ring = ndimage.binary_dilation(hit, iterations=max(1, int(round(0.9 * ss * r.px_scale)))) & ~hit
    rgba[..., :3] = np.where(ring[..., None], hd.BLACK_OUT, rgba[..., :3])
    rgba[..., 3] = np.where(ring, np.maximum(rgba[..., 3], 0.55), rgba[..., 3])
    if flash_at is not None:
        mz, M, variant = flash_at
        xs = (np.arange(Ws) + 0.5) / ss; ys = (np.arange(Hs) + 0.5) / ss
        SX, SY = np.meshgrid(xs, ys)
        fwd = M @ np.array([1.0, 0, 0])
        for m in mz:
            c = m + fwd * 0.5                                  # the burst's heart just past the muzzle
            cx, cy = r.cam.project(c)
            # the long rays run across the screen, to the barrel's side (TS draws them horizontal)
            sx_f, _ = r.cam.project(c + fwd)
            side = np.sign(sx_f - cx) if abs(sx_f - cx) > 0.8 else np.sign(cx - r.cam.ox) or 1.0
            colf, af = FL.burst(SX, SY, cx, cy, (side, 0.0), variant, scale=WH.PPU)
            dc = c @ r.cam.D
            hidden = depth < dc - 0.6                            # the unit in front of the burst hides it
            af = np.where(hidden, 0.0, af)[..., None]
            a0 = rgba[..., 3:4]
            # straight alpha 'over'
            a_out = af + a0 * (1 - af)
            rgba[..., :3] = np.where(af > 0, (colf * af + rgba[..., :3] * a0 * (1 - af)) / np.maximum(a_out, 1e-6),
                                     rgba[..., :3])
            rgba[..., 3] = a_out[..., 0]
    return hd.fade_edges(hd.downsample(rgba, ss))


def trim_img(r, alb):
    tm = WM.trim_mask(r, alb).astype(np.float32)
    ss = r.ss
    full = np.zeros((r.H * ss, r.W * ss), np.float32)
    x0, y0, x1, y1 = r.win
    full[y0 * ss:y1 * ss, x0 * ss:x1 * ss] = tm
    return Image.fromarray((full.reshape(r.H, ss, r.W, ss).mean(axis=(1, 3)) * 255).round().astype(np.uint8), 'L')


if __name__ == '__main__':
    ks = [int(a) for a in sys.argv[2].split(',')] if len(sys.argv) > 2 else range(128)
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    out = sys.argv[4] if len(sys.argv) > 4 else OUT
    sky = bool(int(sys.argv[5])) if len(sys.argv) > 5 else True
    model = WH.load(sys.argv[1]) if sys.argv[1].endswith('.json') else WH.load()
    os.makedirs(out, exist_ok=True)
    for k in ks:
        t0 = time.time()
        img, trim = frame(k, model, ss, sky=sky)
        save(img, trim, f'{out}/tssmec-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
