"""
jrender.py - the Juggernaut's HD frames for the mod (TSJUGG, 448 x 448), from the fitted model (jugg.py):
   0-119   the walk: frame = mod facing x 15 + step (facings counter-clockwise from north: 0 N, 1 NW ... 7 NE)
Each frame carries the unit's baked ground shadow (alpha 191) and a -trim.png.

The camera: the RA-grid camera (32 degrees), 6.33 canvas px per TS px; TS's sprite point (x, y) sits at canvas
(6.33 x - 76.72, 6.33 y + 9.33) in the mod's walk frames (found by matching TS's frames to the mod's: overlap 0.97),
so the unit's ground point (TS's ax, y0) goes there.

    python3 jrender.py fit.json frames 0,30,60 [ss] [outdir] [sky]
"""
import json, os, sys, time
import numpy as np
from PIL import Image
from scipy import ndimage
import rc, rcrender as RR
import hd
import walls2 as W
from walls2 import smoothstep
import jugg as JG
from frameio import save

CANVAS = (448, 448)
PPU = 6.33
# canvas = TS px x K + (dx, dy): TS's frames matched to the mod's walk frames (overlap 0.97), then 5 px up so the
# ground line is the mod's (the lowest body pixel of the deployed frames, deploy frames 184 and 201 and walk frame 45 at
# canvas y 363, the README's "Keep"): the RA camera's 32 degrees draws ground TS's 30-degree sprites put 15 px in
# front of the unit about 3 px lower, which drops the nearest foot that much
MAP = (6.33, -76.72, 9.33 - 5.0)
SHADOW_LEN = 0.62                  # the walkers' (Titan, Wolverine, Mammoth Mk. II)
PX_SCALE = 1.5
BOUNDS = ((-30, 30), (-30, 30), (-1, 45))

# colours read from TS's JUGGER frames (UNITTEM.PAL)
GREEN = np.array([0, 214, 0.])
HATCH = np.array([206, 206, 204.])        # the light grey roof block (TS's greys 33-41)
SLOT = np.array([52, 52, 56.])            # its dark slot, the slit across its front, the sensor's core
PANEL = np.array([74, 74, 78.])           # the dark panel in its top (TS's 52-97)
KHAKI = np.array([200, 178, 112.])        # the barrel pack and barrels (TS's 128-135)
STEEL = np.array([150, 150, 156.])        # the muzzles (TS's 44-48)
OCHRE = np.array([208, 162, 70.])         # the legs: the Titan's yellow-brown (TS's ochre ramp 144-149, lit)
BRIGHT = np.array([236, 182, 80.])        # the legs' lit edges (TS's 181-184)
OLIVE = np.array([66, 60, 34.])           # the hip block (TS's 76-79, 119-127)
JOINT = np.array([84, 84, 84.])           # knees and ankles (TS's 13, 53)
CABLE = np.array([120, 120, 124.])
GRIME = np.array([112, 104, 78.])
FILL = 0.32
HOUSE_COMPS = (JG.SHELL, JG.ANT, JG.ARCH)


def load(path):
    js = json.load(open(path))
    P = dict(JG.P0); P.update(js['P'])
    # the three barrel housings as TS's front view draws them (JUGGER CW4): three cylinders 5 px across, side by side
    # (the silhouette fit merged them into one block; these fit TS's frames as well: IoU 0.813 either way)
    P['brad'], P['bs'] = 2.5, 5.0
    # the hatch as refitted on the deployed cabin with TS's white sides told from its grey top (jfithatch.py: taller and
    # narrower than the silhouette fit had it), moved onto the walker's body as the rest of the cabin's shape is
    # (jfitwalker.body_from: the walker's body is the cabin's, its front at bu1, scaled by bsc)
    hj = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fit_hatch_a.json')
    if os.path.exists(hj):
        cab = json.load(open(hj))['P']
        bsc = P.get('bsc', 1.0)
        for k in ('hu0', 'hu1'):
            P[k] = (cab[k] - cab['bu1']) * bsc + P['bu1']
        for k in ('hv', 'hh'):
            P[k] = cab[k] * bsc
        for k in ('hs', 'rf0', 'rf1', 'rvf'):
            P[k] = cab[k]
    # the arches as JUGGER's frames draw them: TS's diagonal views (CW1, CW7) show a green hoop over the far side of
    # the body's front and its side views one over the hatch's front, and the near one is lost against the green
    # side, so a hoop each side of the roof: from by the hatch's middle to the body's front edge, rising 2.7 px from
    # just under the roof (CW2: x 47-58, top row 20). The silhouette fit had shrunk the arch to a stub through the hatch.
    P.update(au0=-0.5, au1=P['bu1'] + 0.3, aw0=P['bw1'] - 0.1, aw1=P['bw1'] - 0.1, ah=2.7, av=0.0, side_arches=1.0,
             cl=0.0)
    # the muzzle brakes' two slots (JUGGER CW2: darker columns 2 and 4 px from the muzzle's back)
    P['mslots'] = 1.0
    m = dict(P=P, ax=js['ax'], y0=js['y0'], stand=js.get('pose'))
    if 'poses' in js:
        m['walk'] = {int(k): v for k, v in js['poses'].items()}
    return m


def camera(model):
    K, dx, dy = MAP
    return RR.ra_cam(PPU, (model['ax'] * K + dx, model['y0'] * K + dy))


def mod_to_cw(f):
    return (8 - f) % 8


def walk_pose(model, step):
    w = model.get('walk')
    return w[step] if w and step in w else model['stand']


def find_window(parts, cam, margin=14, step=3):
    Wc, Hc = CANVAS
    xs = np.arange(0, Wc, step) + step / 2; ys = np.arange(0, Hc, step) + step / 2
    SX, SY = np.meshgrid(xs, ys)
    O = cam.rays(SX.ravel(), SY.ravel())
    t, who, _ = rc.cast(parts, O, cam.D, want_normals=False)
    hit = np.isfinite(t).reshape(SX.shape)
    yy, xx = np.nonzero(hit)
    return (max(int(xs[xx.min()] - margin), 0), max(int(ys[yy.min()] - margin), 0),
            min(int(xs[xx.max()] + margin), Wc), min(int(ys[yy.max()] + margin), Hc))


ROUNDED = {JG.SHELL: 0.55, JG.HATCH: 0.35, JG.PACK: 0.4, JG.HIP: 0.4, JG.THIGH: 0.45, JG.SHIN: 0.4, JG.FOOT: 0.4,
           JG.MUZZLE: 0.25, JG.ANT: 0.2}


def round_edges(r):
    """soften the box parts' edges in the shading (a softmax over each part's planes)."""
    for i, p in enumerate(r.parts):
        sig = ROUNDED.get(p.comp)
        if sig is None:
            continue
        m = (r.who == i) & r.hitmask
        if not m.any():
            continue
        pl = [c for c in p.cons if c.kind == 'plane']
        if not pl:
            continue
        N = np.array([c.n for c in pl]); d = np.array([c.d for c in pl])
        Q = np.stack([r.x[m], r.y[m], r.z[m]], 1)
        s = Q @ N.T - d[None, :]
        w = np.exp((s - s.max(1, keepdims=True)) / sig)
        n = w @ N
        n = n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)
        r.nx[m], r.ny[m], r.nz[m] = n[:, 0], n[:, 1], n[:, 2]


def grain_of(r, P):
    X, Y, Z = r.x * PPU / 1.5, r.y * PPU / 1.5, r.z * PPU / 1.5
    ax, ay, az = np.abs(r.nx) + 1e-3, np.abs(r.ny) + 1e-3, np.abs(r.nz) + 1e-3
    s_ = ax + ay + az

    def tri(noise, o):
        return (W.sample(noise, Y + o, Z + 2 * o) * ax + W.sample(noise, X + 3 * o, Z + o) * ay +
                W.sample(noise, X + o, Y + 5 * o) * az) / s_
    return tri(W.NOISE_FINE, 0) * 0.035 + tri(W.NOISE_MOTTLE, 17) * 0.05


def materials(r, P):
    comp = r.comp
    alb = np.zeros(comp.shape + (3,), np.float32)
    grain = grain_of(r, P)
    g1 = (1 + 0.45 * grain)[..., None]
    put = lambda m, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=m[..., None])
    put(np.isin(comp, HOUSE_COMPS), GREEN * (1 + 1.1 * grain)[..., None])
    put(comp == JG.HATCH, HATCH * g1)
    put(np.isin(comp, (JG.SLOT, JG.HSLIT, JG.SCORE, JG.MSLOT)), SLOT * g1)
    put(comp == JG.RECESS, PANEL * g1)
    put(np.isin(comp, (JG.PACK, JG.BARREL)), KHAKI * g1)
    put(comp == JG.MUZZLE, STEEL * g1)
    put(comp == JG.CABLE, CABLE * g1)
    put(comp == JG.HIP, OLIVE * g1)
    put(np.isin(comp, (JG.KNEE, JG.ANKLE)), JOINT * g1)
    legs = np.isin(comp, (JG.THIGH, JG.SHIN, JG.FOOT))
    lit = np.clip((r.nx * -0.45 + r.ny * -0.55 + r.nz * 0.7) * 1.4 - 0.3, 0, 1)[..., None]
    put(legs, (OCHRE * (1 - 0.35 * lit) + BRIGHT * 0.35 * lit) * g1)
    # grime rising from the ground on the legs
    dust = smoothstep(4.0, 0.5, r.z) * 0.35 * legs
    alb = alb * (1 - dust[..., None]) + (GRIME * g1) * dust[..., None]
    return alb


def frame(k, model, ss=4, sky=True):
    f, s = divmod(k, 15)
    pose = walk_pose(model, s)
    M = JG.facing_matrix(mod_to_cw(f))
    parts = [p.moved(M) for p in JG.body_parts(model['P'], pose) + JG.details(model['P'], pose[6])]
    cam = camera(model)
    win = find_window(parts, cam)
    r = RR.RCRender(parts, cam, CANVAS, win, BOUNDS, ss=ss, shadow_len=SHADOW_LEN, px_scale=PX_SCALE)
    round_edges(r)
    occ = r.sky_occlusion() if sky else None
    alb = materials(r, model['P'])
    ao = 0.86 + 0.14 * np.clip(r.z / 14.0, 0, 1)
    col = r.shade(alb, sky_occ=occ, ao=ao)
    tc = np.array([cam.T[0] * cam.cE, cam.T[1] * cam.cE, cam.sE]); tc = tc / np.linalg.norm(tc)
    nf = np.clip(r.nx * tc[0] + r.ny * tc[1] + r.nz * tc[2], 0, 1) * (1 - np.clip(r.nz, 0, 1))
    if occ is not None:
        nf = nf * (1 - 0.85 * np.clip(occ, 0, 1))
    col = col + alb * (FILL * nf)[..., None]
    g = r.ground_alpha_full(shadow_parts=parts)
    img = r.compose(col, ground=g)
    house = np.isin(r.comp, HOUSE_COMPS) & r.hitmask
    full = np.zeros((r.H * ss, r.W * ss), np.float32)
    x0, y0, x1, y1 = r.win
    full[y0 * ss:y1 * ss, x0 * ss:x1 * ss] = house
    trim = Image.fromarray((full.reshape(r.H, ss, r.W, ss).mean(axis=(1, 3)) * 255).round().astype(np.uint8), 'L')
    return img, trim


if __name__ == '__main__':
    model = load(sys.argv[1])
    ks = [int(a) for a in sys.argv[3].split(',')]
    ss = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    out = sys.argv[5] if len(sys.argv) > 5 else 'out'
    sky = bool(int(sys.argv[6])) if len(sys.argv) > 6 else True
    os.makedirs(out, exist_ok=True)
    for k in ks:
        t0 = time.time()
        img, trim = frame(k, model, ss, sky)
        save(img, trim, f'{out}/tsjugg-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
