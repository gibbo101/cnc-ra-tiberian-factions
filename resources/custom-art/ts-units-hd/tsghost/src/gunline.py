"""
gunline.py - TS's gun in a frame, as targets for the fit: where TS draws the gun (the longest straight run of its green
pixels: the Ghost's railgun) and, firing, where its muzzle is (the flash starts there).  The silhouette alone let the
Ghost's railgun settle pointing down while TS's points along his facing (Luke: "gun pointing the wrong direction").

    t = gunline.GunTarget(unit, k)          t.line (A, B) or None, t.root (x, y) or None
    pen = t.pen(S, Q, facing, ax, y0, dz)   px squared, weighted
"""
import numpy as np
import rc
import inf as I
import inffit as F
import infx as X

W_LINE = 0.01           # a TS pixel squared, either end of TS's gun off ours
W_ROOT = 0.01           # a TS pixel squared, our muzzle off where TS's flash starts


def ts_line(unit, k, min_len=4.5):
    import infsmooth as SM
    return SM.ts_gun_line(unit, k, min_len)


def flash_root(unit, k, line=None):
    """where TS's muzzle flash starts: the end of TS's gun nearest the flash, or the flash pixel nearest the soldier."""
    a = F.ts_frame(unit, k)
    fl = X.ts_flash(a)
    if len(fl) < 3:
        return None
    P = np.array([(x + 0.5, y + 0.5) for x, y, w in fl], float)
    c = P.mean(0)
    if line is not None:
        A, B = line
        e = A if np.linalg.norm(A - c) < np.linalg.norm(B - c) else B
        if np.min(np.linalg.norm(P - e, axis=1)) < 3.0:
            return e
    body = (F.ts_classes(a) > 0) & (F.ts_classes(a) != F.FX)
    ys, xs = np.nonzero(body)
    bc = np.array([xs.mean() + 0.5, ys.mean() + 0.5])
    return P[np.argmin(np.linalg.norm(P - bc, axis=1))]


class GunTarget:
    def __init__(self, unit, k, line=True, root=True):
        self.line = ts_line(unit, k) if line else None
        self.root = flash_root(unit, k, self.line) if root else None

    def ends(self, S, Q, facing, ax, y0, dz):
        cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
        th = I.facing_angle(facing)
        P = I.Pose(S, Q, th)
        G0, RG = P.rifle
        back = np.asarray(G0, float) - RG[:, 0] * S['gg'] + np.array([0.0, 0.0, dz])
        front = back + RG[:, 0] * S['gl']
        return np.array(cam.project(back), float), np.array(cam.project(front), float)

    def pen(self, S, Q, facing, ax, y0, dz):
        if self.line is None and self.root is None:
            return 0.0
        b, f = self.ends(S, Q, facing, ax, y0, dz)
        out = 0.0
        if self.line is not None:
            d = f - b
            L = float(np.linalg.norm(d))
            if L < 1e-6:
                return 1.0
            u = d / L; n = np.array([-u[1], u[0]])
            for P in self.line:
                al = float((P - b) @ u)
                out += W_LINE * (float((P - b) @ n) ** 2 + max(0.0, -al) ** 2 + max(0.0, al - L) ** 2)
        if self.root is not None:
            out += W_ROOT * float(np.sum((f - self.root) ** 2))
        return out
