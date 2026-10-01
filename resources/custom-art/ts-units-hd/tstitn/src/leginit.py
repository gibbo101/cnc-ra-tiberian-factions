"""initial leg poses from the hull slices: each leg's centre line (u, w) fitted with a 2-segment polyline."""
import numpy as np
from scipy.optimize import least_squares
from legslices import leg_blobs

def centre_lines(step):
    rows, _, _ = leg_blobs(step)
    L, R = [], []
    for w, blobs in rows:
        if w > 17.0:
            continue
        for b in blobs:
            if b['n'] < 120:
                continue
            (L if b['v'] < -1.5 else R if b['v'] > 1.5 else []).append((b['u'], w, b['v']))
    return np.array(L), np.array(R)

def seg_dist(p, a, b):
    ab = b - a; t = np.clip(((p - a) @ ab) / (ab @ ab + 1e-9), 0, 1)
    return np.linalg.norm(p - (a + t[:, None] * ab), axis=1)

def fit_polyline(pts, J):
    pts = pts[:, :2]
    def res(x):
        K = x[:2]; A = x[2:4]
        d = np.minimum(seg_dist(pts, J, K), seg_dist(pts, K, A))
        # the ankle is the lowest point
        return np.concatenate([d, [0.3 * (A[1] - pts[:, 1].min())]])
    lo = pts[pts[:, 1] < pts[:, 1].min() + 1.5]
    x0 = np.array([J[0] - 2, (J[1] + lo[:, 1].mean()) / 2, lo[:, 0].mean(), lo[:, 1].mean()])
    r = least_squares(res, x0)
    return r.x[:2], r.x[2:4], np.sqrt(np.mean(r.fun ** 2))

if __name__ == '__main__':
    J = np.array([0.5, 17.0])
    for step in range(15):
        L, R = centre_lines(step)
        out = []
        for name, pts in (('L', L), ('R', R)):
            if len(pts) < 4:
                out.append('%s: too few' % name); continue
            K, A, rms = fit_polyline(pts, J)
            at = np.degrees(np.arctan2(K[0] - J[0], J[1] - K[1])); as_ = np.degrees(np.arctan2(A[0] - K[0], K[1] - A[1]))
            out.append('%s K(%.1f,%.1f) A(%.1f,%.1f) Lt %.1f Ls %.1f at %.0f as %.0f rms %.2f' % (
                name, K[0], K[1], A[0], A[1], np.linalg.norm(K - J), np.linalg.norm(A - K), at, as_, rms))
        print(step, ' | '.join(out), flush=True)
