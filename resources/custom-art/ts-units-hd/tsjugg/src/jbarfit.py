"""fit the barrels' place on the cabin and their size to the mod's deployed frames (in-mod/ 120-151 at rest, level;
152-183 aiming, raised about the breech): the base and the cabin stay as their own fits put them, only the barrels
move.  Silhouette plus colour classes, at half the canvas's resolution, in TS's camera (30 degrees) scaled as the mod
draws the deployed frames.

    python3 jbarfit.py rest out.json iters                  scale s, mount (u, v, w), rest pitch
    python3 jbarfit.py aim  out.json iters rest.json        hinge (i, k) and pitch
"""
import json, sys, time
import numpy as np
import cma
from PIL import Image
import rc
import jdeployed as JD
from jfit import AGREE

K = 6.3346
DX, DY = -80.15, -79.92            # the mod's deployed frames: canvas = DJUGG px x K + (DX, DY)
RES = 0.5
WIN = (0, 0, 224, 200)             # x0, y0, x1, y1 at half resolution: the whole canvas
ZS = 200.0
HINGE0 = (4.0, 11.5, 3.5)          # the breech (voxel index coordinates): the reference point for the mount


def inmod_classes(k):
    a = np.asarray(Image.open(JD.H + 'in-mod/tsjugg/frames/tsjugg-%04d.png' % k).convert('RGBA')).astype(float)
    al = a[..., 3:] / 255.0
    pm = a[..., :3] * al
    h, w = a.shape[0] // 2, a.shape[1] // 2
    pm = pm.reshape(h, 2, w, 2, 3).mean((1, 3)); al = al.reshape(h, 2, w, 2, 1).mean((1, 3))
    rgb = pm / np.maximum(al, 1e-6)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    solid = al[..., 0] > 0.8
    # the shadow: dark and see-through in the mod's frames (alpha well under 1): not solid
    c = np.full(r.shape, 5, int)
    mx = rgb.max(-1); mn = rgb.min(-1); v = rgb.mean(-1)
    grey = (mx - mn) < 28
    c[grey & (v >= 140)] = 2
    c[(g > r + 35) & (g > b + 35)] = 1
    warm = (r > b + 30) & ~((g > r + 35) & (g > b + 35))
    c[warm & (v >= 60)] = 4
    c[~solid] = 0
    x0, y0, x1, y1 = WIN
    return c[y0:y1, x0:x1]


class Scene:
    def __init__(self, frames):
        self.M = JD.load_fits()
        ax, by0 = self.M['axis']
        self.cam = rc.Cam((0, -1), 30.0, K * RES, ((ax * K + DX) * RES, (by0 * K + DY) * RES))
        self.frames = list(frames)
        self.B = JD.Barrels(sub=3)
        x0, y0, x1, y1 = WIN
        self.W, self.H = x1 - x0, y1 - y0
        self.tgt, self.bc_cls, self.bc_t = [], [], []
        base = JD.base_world(self.M)
        for k in self.frames:
            f = (k - 120) % 32
            parts = base + JD.cabin_world(self.M, f)
            t, who, nrm, O = rc.render_ids(parts, self.cam, x0, y0, self.W, self.H, ss=1, zstart=ZS)
            cls_of = np.array([0] + [JD.JG.CLASS[p.comp] for p in parts])
            self.bc_cls.append(cls_of[who + 1]); self.bc_t.append(t)
            self.tgt.append(inmod_classes(k))
        self.area = np.mean([(t > 0).sum() for t in self.tgt])

    def composite(self, i, P):
        """the frame i's classes with the barrels drawn in (P: body points of the barrel voxel's sub-points)."""
        f = (self.frames[i] - 120) % 32
        R = JD.JG.facing_matrix((32 - f) % 32, 32)
        Wp = P @ R.T + np.array([self.M['cab_off'], 0.0, self.M['cab_dz']])
        sx, sy = self.cam.project(Wp)
        x0, y0 = WIN[0], WIN[1]
        px = np.floor(sx - x0).astype(int); py = np.floor(sy - y0).astype(int)
        ok = (px >= 0) & (px < self.W) & (py >= 0) & (py < self.H)
        t = (ZS - Wp[:, 2]) / self.cam.sE
        idx = (py * self.W + px)[ok]; tt = t[ok]; cc = self.B.pcls[ok]
        order = np.lexsort((tt, idx))
        idx, tt, cc = idx[order], tt[order], cc[order]
        first = np.r_[True, idx[1:] != idx[:-1]]
        idx, tt, cc = idx[first], tt[first], cc[first]
        cl = self.bc_cls[i].ravel().copy(); bt = self.bc_t[i].ravel()
        win = tt < bt[idx]
        cl[idx[win]] = cc[win]
        return cl.reshape(self.H, self.W)

    def loss(self, P_of, w_cls=0.6):
        out = []
        for i in range(len(self.frames)):
            cl = self.composite(i, P_of(i))
            tc = self.tgt[i]
            l = ((cl > 0) != (tc > 0)).sum() / self.area
            both = (cl > 0) & (tc > 0)
            l += w_cls * (1 - AGREE[cl[both], tc[both]]).sum() / self.area
            out.append(l)
        return float(np.mean(out))


REST = [('s', 0.4, 1.4), ('mu', -6, 16), ('mv', -3, 3), ('mw', 8, 32), ('p0', -12, 12)]
AIM = [('hi', -4, 30), ('hk', -6, 14), ('pa', 20, 70)]


def rest_points(S, x):
    s, mu, mv, mw, p0 = x
    P = S.B.body(s, (mu, mv, mw), HINGE0, p0)
    return lambda i: P


def aim_points(S, rest, x):
    hi, hk, pa = x
    s = rest['s']; h = np.array([hi, HINGE0[1], hk])
    # the hinge's place on the cabin with the barrels level where the rest fit puts them
    d = (h - np.array(HINGE0)) * S.B.vscale * s
    a = np.deg2rad(rest['p0'])
    du = d[0] * np.cos(a) - d[2] * np.sin(a); dw = d[0] * np.sin(a) + d[2] * np.cos(a)
    mount = (rest['mu'] + du, rest['mv'], rest['mw'] + dw)
    P = S.B.body(s, mount, h, rest['p0'] + pa)
    return lambda i: P


if __name__ == '__main__':
    mode, out, iters = sys.argv[1], sys.argv[2], int(sys.argv[3])
    if mode == 'rest':
        S = Scene(range(120, 152, 2)); spec = REST
        x0 = np.array([0.69, 4.0, 0.0, 20.0, 0.0])
        fun = lambda x: S.loss(rest_points(S, x))
    else:
        rest = json.load(open(sys.argv[4]))
        S = Scene(range(152, 184, 2)); spec = AIM
        x0 = np.array([HINGE0[0], HINGE0[2], 45.0])
        fun = lambda x: S.loss(aim_points(S, rest, x))
    lo = np.array([a[1] for a in spec], float); hi = np.array([a[2] for a in spec], float); span = hi - lo
    f = lambda z: fun(lo + np.clip(z, 0, 1) * span)
    z0 = np.clip((x0 - lo) / span, 1e-3, 1 - 1e-3)
    print('start %.4f' % f(z0), flush=True)
    es = cma.CMAEvolutionStrategy(z0, 0.15, {'bounds': [0, 1], 'popsize': 12, 'maxiter': iters, 'seed': 1,
                                             'verbose': -9})
    t0 = time.time(); it = 0
    while not es.stop():
        Z = es.ask(); es.tell(Z, [f(z) for z in Z]); it += 1
        if it % 5 == 0 or es.stop():
            x = lo + np.clip(es.result.xbest, 0, 1) * span
            res = {a[0]: float(v) for a, v in zip(spec, x)}
            res['f'] = float(es.result.fbest)
            if mode == 'aim':
                res.update({k: rest[k] for k in ('s', 'mu', 'mv', 'mw', 'p0')})
            json.dump(res, open(out, 'w'), indent=1)
            print('it', it, 'best %.4f' % es.result.fbest, {k: round(v, 2) for k, v in res.items()},
                  '%.0fs' % (time.time() - t0), flush=True)
    print('done %.4f' % es.result.fbest, flush=True)
