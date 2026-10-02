"""gait.py - a walker's walk as a smooth periodic gait (the Titan's; the Wolverine's adds the body's sway).

Each leg joint angle (thigh, shin, foot pitch) is a Fourier series in the walk phase; the right leg runs half a
cycle behind the left (TS's walk is symmetric: an east-facing frame mirrors the west-facing one 7-8 steps on).
The hips bob twice per stride (2nd harmonic).  Fitted to the per-step poses, then refined on TS's silhouettes.
"""
import json
import numpy as np

NH = 3          # harmonics per joint angle
NB = 1          # bob harmonics (in units of 2 phi)


def basis(phi, nh=NH):
    cols = [np.ones_like(phi)]
    for n in range(1, nh + 1):
        cols += [np.cos(n * phi), np.sin(n * phi)]
    return np.stack(cols, -1)


def bob_basis(phi, nb=NB):
    cols = [np.ones_like(phi)]
    for n in range(1, nb + 1):
        cols += [np.cos(2 * n * phi), np.sin(2 * n * phi)]
    return np.stack(cols, -1)


def roll_basis(phi):
    """odd harmonics: the sway to one side and back, the other way half a stride on."""
    return np.stack([np.cos(phi), np.sin(phi), np.cos(3 * phi), np.sin(3 * phi)], -1)


class Gait:
    def __init__(self, coef, bob, phase0=0.0, roll=None, pitch=None):
        self.coef = np.asarray(coef, float)      # (3 joints, 1 + 2 NH)
        self.bob = np.asarray(bob, float)        # (1 + 2 NB)
        self.phase0 = float(phase0)
        self.roll = None if roll is None else np.asarray(roll, float)     # (4,) odd harmonics
        self.pitch = None if pitch is None else np.asarray(pitch, float)  # (1 + 2 NB) even harmonics

    def pose(self, phi):
        """pose (lt, ls, lf, rt, rs, rf, dw[, roll, pitch]) at walk phase phi (radians: step s of n is
        phi = 2 pi s / n)."""
        pl = phi + self.phase0
        L = basis(np.array([pl]))[0] @ self.coef.T
        R = basis(np.array([pl + np.pi]))[0] @ self.coef.T
        dw = bob_basis(np.array([pl]))[0] @ self.bob
        out = [float(L[0]), float(L[1]), float(L[2]), float(R[0]), float(R[1]), float(R[2]), float(dw)]
        if self.roll is not None:
            out += [float(roll_basis(np.array([pl]))[0] @ self.roll), float(bob_basis(np.array([pl]))[0] @ self.pitch)]
        return out

    def vector(self):
        v = [self.coef.ravel(), self.bob.ravel()]
        if self.roll is not None:
            v += [self.roll, self.pitch]
        return np.concatenate(v)

    @staticmethod
    def from_vector(x, phase0=0.0, sway=False):
        n = 3 * (1 + 2 * NH)
        nb = 1 + 2 * NB
        g = Gait(np.asarray(x[:n]).reshape(3, 1 + 2 * NH), np.asarray(x[n:n + nb]), phase0)
        if sway:
            g.roll = np.asarray(x[n + nb:n + nb + 4]); g.pitch = np.asarray(x[n + nb + 4:n + nb + 4 + nb])
        return g

    def to_json(self):
        d = dict(coef=self.coef.tolist(), bob=self.bob.tolist(), phase0=self.phase0, NH=NH, NB=NB)
        if self.roll is not None:
            d.update(roll=self.roll.tolist(), pitch=self.pitch.tolist())
        return d

    @staticmethod
    def from_json(d):
        return Gait(d['coef'], d['bob'], d.get('phase0', 0.0), d.get('roll'), d.get('pitch'))


def fit_from_poses(poses, nsteps=15):
    """least squares: left leg at phi_s, right leg at phi_s + pi, over all steps."""
    steps = sorted(poses)
    phi = np.array([2 * np.pi * s / nsteps for s in steps])
    A = np.concatenate([basis(phi), basis(phi + np.pi)], 0)
    coef = []
    for j in range(3):
        y = np.concatenate([[poses[s][j] for s in steps], [poses[s][3 + j] for s in steps]])
        c, *_ = np.linalg.lstsq(A, y, rcond=None)
        coef.append(c)
    B = bob_basis(phi)
    bob, *_ = np.linalg.lstsq(B, np.array([poses[s][6] for s in steps]), rcond=None)
    g = Gait(np.array(coef), bob)
    if all(len(poses[s]) > 8 for s in steps):
        g.roll, *_ = np.linalg.lstsq(roll_basis(phi), np.array([poses[s][7] for s in steps]), rcond=None)
        g.pitch, *_ = np.linalg.lstsq(B, np.array([poses[s][8] for s in steps]), rcond=None)
    return g
