import json, sys, time
import numpy as np
import cma
import rc, torso2 as T2, torsofit as TF
from torsoview import class_img
from PIL import Image, ImageDraw

class Views:
    def __init__(self, ax=48.19, y0=55.0, win=(30, 0, 68, 42)):
        self.win = win
        x0, yw, x1, y1 = win
        self.cls = [TF.ts_classes(120 + k)[yw:y1, x0:x1] for k in range(32)]
        self.masks = [c > 0 for c in self.cls]
        self.cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))

    def model_cls(self, P, k, ss=2):
        x0, yw, x1, y1 = self.win; h, w = y1 - yw, x1 - x0
        base = T2.parts(P)
        M = TF.facing_matrix32(k)
        pk = [p.moved(M) for p in base]
        t, who, nrm, O = rc.render_ids(pk, self.cam, x0, yw, w, h, ss=ss, zstart=200.0)
        z = (O + np.where(np.isfinite(t), t, 0)[..., None] * self.cam.D)[..., 2]
        cls_of = np.array([0] + [T2.CLASS[p.comp] for p in base])
        cl = cls_of[who + 1]
        body = who == 0
        cl = np.where(body & (z < P['band']), 6, cl)
        return cl.reshape(h, ss, w, ss).transpose(0, 2, 1, 3).reshape(h, w, ss * ss)

    def loss(self, P, ks=range(32), ss=2, w_cls=0.6):
        tot = 0.0
        for k in ks:
            cl = self.model_cls(P, k, ss)
            cov = (cl > 0).mean(-1); m = self.masks[k]
            tot += np.abs(cov - m).sum() / m.sum()
            tc = self.cls[k]; both = m & (cov >= 0.5)
            agree = (cl == tc[..., None]).mean(-1)
            tot += w_cls * (1 - agree[both]).sum() / m.sum()
        return tot / len(ks)

    def compare(self, P, ks, name, z=5):
        tiles = []
        for k in ks:
            cl = self.model_cls(P, k, 2)
            cov = (cl > 0).mean(-1)
            maj = np.zeros(cov.shape, int)
            for c in (1, 2, 6, 7):
                cnt = (cl == c).sum(-1)
                better = cnt > np.where(maj > 0, (cl == maj[..., None]).sum(-1), 0)
                maj = np.where(better & (cov >= 0.5), c, maj)
            both = np.concatenate([class_img(self.cls[k]), np.zeros((maj.shape[0], 2, 3), np.uint8), class_img(maj)], 1)
            im = Image.fromarray(both); im = im.resize((im.size[0] * z, im.size[1] * z), Image.NEAREST)
            ImageDraw.Draw(im).text((3, 3), str(120 + k), fill=(255, 255, 0))
            tiles.append(im)
        W, H = tiles[0].size; cols = 4
        out = Image.new('RGB', (cols * (W + 6), ((len(tiles) + cols - 1) // cols) * (H + 6)))
        for i, t in enumerate(tiles):
            out.paste(t, ((i % cols) * (W + 6), (i // cols) * (H + 6)))
        out.save(name)

SPEC = [('band', 30, 34), ('pfu0', 2, 8), ('pfu1', 9, 12.5), ('pru0', -12.5, -9), ('pru1', -8, -2), ('pv0', 0.5, 4),
        ('pv1', 5, 9), ('pbot', 21, 26), ('ptop', 28.2, 31),
        ('bu0', -12, -6), ('bu1', -5, 0), ('bv0', -6, -1.5), ('bv1', -0.5, 4), ('btop', 40, 47), ('bbot', 33, 39),
        ('au', -4, -1.5), ('av', 2.5, 4.5), ('atop', 45, 56),
        ('mu0', -6, 0), ('mu1', 1.5, 7), ('mv0', 5, 8.0), ('mv1', 8.5, 10.5), ('mw0', 25, 30), ('mw1', 32, 37)]

def P_from(x):
    d = {n: v for (n, *_), v in zip(SPEC, x)}
    P = dict(T2.P0)
    for k in ('band', 'pbot', 'ptop', 'btop', 'bbot', 'au', 'av', 'atop'):
        P[k] = d[k]
    P['pfu'] = (d['pfu0'], d['pfu1']); P['pru'] = (d['pru0'], d['pru1']); P['pv'] = (d['pv0'], d['pv1'])
    P['bu'] = (d['bu0'], d['bu1']); P['bv'] = (d['bv0'], d['bv1'])
    P['mu'] = (d['mu0'], d['mu1']); P['mv'] = (d['mv0'], d['mv1']); P['mw'] = (d['mw0'], d['mw1'])
    return P

def x_from(P):
    return [P['band'], P['pfu'][0], P['pfu'][1], P['pru'][0], P['pru'][1], P['pv'][0], P['pv'][1], P['pbot'], P['ptop'],
            P['bu'][0], P['bu'][1], P['bv'][0], P['bv'][1], P['btop'], P['bbot'], P['au'], P['av'], P['atop'],
            P['mu'][0], P['mu'][1], P['mv'][0], P['mv'][1], P['mw'][0], P['mw'][1]]

if __name__ == '__main__':
    iters = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    V = Views(ax=48.0)
    lo = np.array([s[1] for s in SPEC]); hi = np.array([s[2] for s in SPEC]); span = hi - lo
    import json as _j
    try:
        _P = dict(T2.P0); _P.update(_j.load(open('torso_final.json'))['P'])
        for _k in ('pfu', 'pru', 'pv', 'bu', 'bv', 'mu', 'mv', 'mw'): _P[_k] = tuple(_P[_k])
    except Exception:
        _P = T2.P0
    x0 = np.clip(np.array(x_from(_P)), lo + 1e-3, hi - 1e-3)
    f = lambda z: V.loss(P_from(lo + np.clip(z, 0, 1) * span))
    es = cma.CMAEvolutionStrategy((x0 - lo) / span, 0.15, {'bounds': [0, 1], 'popsize': 16, 'maxiter': iters,
                                                           'seed': 7, 'verbose': -9})
    t0 = time.time(); it = 0
    while not es.stop():
        Z = es.ask(); es.tell(Z, [f(z) for z in Z]); it += 1
        if it % 5 == 0:
            xb = lo + np.clip(es.result.xbest, 0, 1) * span
            print(it, 'best %.4f' % es.result.fbest, '%.0fs' % (time.time() - t0), flush=True)
            json.dump(dict(P=P_from(xb), f=es.result.fbest), open('torso2_fit.json', 'w'), default=float)
    xb = lo + np.clip(es.result.xbest, 0, 1) * span
    json.dump(dict(P=P_from(xb), f=es.result.fbest), open('torso2_fit.json', 'w'), default=float)
    print('done', es.result.fbest, flush=True)
