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
BIG_FLASH = True        # (no gun line: the muzzle is the biggest flash patch's pixel nearest the body)
import os as _os
ARM_LINE = bool(int(_os.environ.get('ARM_LINE', 0) or 0))


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
    if line is None and BIG_FLASH:
        # (no gun line: the muzzle flash proper is the biggest connected patch of TS's flash colours - TS also lights
        # the soldier with them in its flash frames, small patches on the body, and the flash pixel nearest the body
        # centre was then one of those, on the chest, pulling the muzzle into the body - and the muzzle is that
        # patch's pixel nearest the body centre)
        from scipy import ndimage as nd
        # (TS's yellow alone: the oranges it lights the body with join the flash to the body)
        m = np.zeros(a.shape[:2], bool)
        for x, y, w in fl:
            if w >= 0.99:
                m[int(y), int(x)] = True
        lab, n = nd.label(m, structure=np.ones((3, 3)))
        if n >= 1:
            sizes = nd.sum(m, lab, range(1, n + 1))
            big = 1 + int(np.argmax(sizes))
            P = np.array([(x + 0.5, y + 0.5) for x, y, w in fl if lab[int(y), int(x)] == big], float)
    return P[np.argmin(np.linalg.norm(P - bc, axis=1))]


def thin_lines(unit, k, min_px=4):
    """TS's thin parts flung out from the body (an arm stretched out: a line a pixel or two wide, whatever its colour),
    each as a straight segment (A, B) along it, the biggest first."""
    from scipy import ndimage as nd
    a = F.ts_frame(unit, k)
    c = F.ts_classes(a)
    mask = (c > 0) & (c != F.FX)
    body = nd.binary_opening(mask, structure=np.ones((5, 5)))
    thin = mask & ~nd.binary_dilation(body, structure=np.ones((3, 3)))
    lab, n = nd.label(thin, structure=np.ones((3, 3)))
    out = []
    my = np.nonzero(mask)[0]
    top, bot = float(my.min()), float(my.max())
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(xs) < min_px:
            continue
        if ys.mean() > top + 0.62 * (bot - top):
            continue                     # (his legs: TS draws them a pixel or two wide too)
        P = np.stack([xs + 0.5, ys + 0.5], 1)
        c0 = P.mean(0)
        w, v = np.linalg.eigh(np.cov((P - c0).T))
        u = v[:, 1]
        t = (P - c0) @ u
        out.append((len(xs), (c0 + t.min() * u, c0 + t.max() * u)))
    out.sort(key=lambda r: -r[0])
    return [ab for nn, ab in out[:2]]


class GunTarget:
    def __init__(self, unit, k, line=True, root=True):
        self.line = ts_line(unit, k) if line else None
        self.root = flash_root(unit, k, self.line) if root else None
        self.arm_lines = thin_lines(unit, k) if ARM_LINE else []

    def ends(self, S, Q, facing, ax, y0, dz):
        cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
        th = I.facing_angle(facing)
        P = I.Pose(S, Q, th)
        G0, RG = P.rifle
        if S.get('kit') == 'e3':
            G0 = G0 + I.launcher_lift(S, RG)        # (the launcher's tube above the hands)
        back = np.asarray(G0, float) - RG[:, 0] * S['gg'] + np.array([0.0, 0.0, dz])
        front = back + RG[:, 0] * S['gl']
        return np.array(cam.project(back), float), np.array(cam.project(front), float)

    def arms(self, S, Q, facing, ax, y0, dz):
        """each arm's shoulder and hand in TS's camera (an unarmed soldier: the Disc Thrower's throwing arm)."""
        cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
        P = I.Pose(S, Q, I.facing_angle(facing))
        out = []
        for side in ('r', 'l'):
            Sh, RU, E, RF, W = P.arms[side]
            hand = np.asarray(W, float) + np.asarray(RF, float) @ np.array([0.0, 0.0, -S['rh']]) + np.array([0, 0, dz])
            out.append((np.array(cam.project(np.asarray(Sh, float) + np.array([0, 0, dz])), float),
                        np.array(cam.project(hand), float)))
        return out

    def seg_pen(self, b, f):
        d = f - b
        L = float(np.linalg.norm(d))
        if L < 1e-6:
            return 1.0
        u = d / L; n = np.array([-u[1], u[0]])
        out = 0.0
        for P in self.line:
            al = float((P - b) @ u)
            out += W_LINE * (float((P - b) @ n) ** 2 + max(0.0, -al) ** 2 + max(0.0, al - L) ** 2)
        return out

    def pen(self, S, Q, facing, ax, y0, dz):
        if self.line is None and self.root is None and not self.arm_lines:
            return 0.0
        if ARM_LINE and Q.get('ik', 1.0) <= 0.5:
            # (ARM_LINE=1: TS's thin parts flung out from his body are his arms stretched out - the Disc Thrower's
            # throw - each lies along one of his arms, shoulder to hand)
            segs = self.arm_lines or ([self.line] if self.line is not None else [])
            if not segs:
                return 0.0
            arms = self.arms(S, Q, facing, ax, y0, dz)
            out = 0.0
            for ln in segs:
                keep = self.line
                self.line = [np.asarray(ln[0], float), np.asarray(ln[1], float)]
                out += min(self.seg_pen(b, f) for b, f in arms)
                self.line = keep
            return out
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
