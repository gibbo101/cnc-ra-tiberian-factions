"""The Helipad's build-up, in the order TS's GTHPADMK builds it (19 frames, 0-18, drawn in colour):
  0-2   a pyramid of panels stands up in the middle, the pad's rim frame goes round, the steps
  3-5   the pyramid's panels open out and it folds away
  6-8   the deck is laid in from the rim, round a square hole in the middle; the tanks, the pipes
  9-12  a white dome rises in the hole; the machinery block, the control box on its stand
  13-16 the dome sinks back, a hatch slides over the hole
  17    the landing circle is painted (black, the house-green ring, the white cross and ring); 18 done
SEQ has 24 frames (TS's 19 spread over them); its last is the finished helipad (pad + building)."""
import numpy as np
import hpad as M

TS_TABLE = {
    0: dict(pyramid=0.3),
    1: dict(rim=0.5, pyramid=0.7, steps=1.0),
    2: dict(rim=1.0, pyramid=1.0),
    3: dict(pyramid=1.0),
    4: dict(pyramid=1.3),
    5: dict(pyramid=1.7),
    6: dict(deck=0.4, pyramid=2.0),
    7: dict(deck=0.75, tanks=0.3),
    8: dict(deck=1.0, tanks=0.6, pipes=1.0),
    9: dict(tanks=1.0),
    10: dict(dome=0.4, block=0.4),
    11: dict(dome=0.8, block=1.0, box=0.5),
    12: dict(dome=1.0, box=1.0),
    13: dict(dome=1.15),
    14: dict(dome=1.35),
    15: dict(dome=1.7, hatch=0.4),
    16: dict(dome=2.0, hatch=1.0),
    17: dict(land=1.0),
}
STEP = ('steps', 'pipes', 'land')


def ts_state(t):
    out = {}
    for k in M.BUILD_KEYS:
        pts = sorted((f, v[k]) for f, v in TS_TABLE.items() if k in v)
        if not pts:
            out[k] = 1.0
            continue
        fs = np.array([f for f, _ in pts], float); vs = np.array([v for _, v in pts], float)
        if k in STEP:
            out[k] = float(vs[0]) if t >= fs[0] - 1e-6 else 0.0
            continue
        if t < fs[0]:
            out[k] = float(np.clip(1.0 - (fs[0] - t), 0, 1)) * vs[0] if fs[0] > 0 else 0.0
        else:
            out[k] = float(np.interp(t, fs, vs))
    if out['dome'] >= 2.0 - 1e-6:
        out['dome'] = 0.0
    if out['pyramid'] >= 2.0 - 1e-6:
        out['pyramid'] = 0.0
    out['paint'] = 1.0
    return out


N = 24
SEQ = [ts_state(18.0 * i / (N - 1)) for i in range(N)]
SEQ[-1] = dict(M.DONE)
