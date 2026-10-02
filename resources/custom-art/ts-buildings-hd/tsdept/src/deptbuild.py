"""The Service Depot's build-up, in the order TS's GTDEPTMK builds it (10 frames, 0-9, drawn in colour; the pad plain
grey until 7):
  0-4   the pad is laid from the gantry's side (south-west) across to the north-east; the gantry's wall lies flat in
        front of its foot, green, and is raised (1-2 a green plate, 3-4 a braced frame); the base plate, the reel
  4-6   the machine's hoods come up; the wall stands (6), its panel, rail and lamps on; the box
  5-6   the pad complete, plain grey
  7     the pad coloured, its band painted; 8-9 done
SEQ has 19 frames (TS's 10 spread over them: the mod's TSDEPTMAKE.ZIP has 19); its last is the finished depot (pad + building, the arm folded away)."""
import numpy as np
import dept as M

TS_TABLE = {
    0: dict(padgrow=0.18, wallup=0.0, base=1.0, brown=1.0),
    1: dict(padgrow=0.38, wallup=0.06),
    2: dict(padgrow=0.55, wallup=0.3),
    3: dict(padgrow=0.75, wallup=0.55, frame=1.0),
    4: dict(padgrow=0.92, wallup=0.8, mach=0.5),
    5: dict(padgrow=1.0, wallup=0.93, mach=1.0, box=1.0),
    6: dict(wallup=1.0),
    7: dict(padtex=1.0, band=1.0),
}
STEP = ('frame', 'box', 'brown', 'base', 'padtex', 'band')


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
            if k == 'frame':
                out[k] = 1.0 if (3.0 - 1e-6 <= t < 5.0) else 0.0
            continue
        if t < fs[0]:
            out[k] = float(np.clip(1.0 - (fs[0] - t), 0, 1)) * vs[0] if fs[0] > 0 else float(vs[0])
        else:
            out[k] = float(np.interp(t, fs, vs))
    out['wall'] = 1.0
    out['paint'] = 1.0
    return out


N = 19
SEQ = [ts_state(9.0 * i / (N - 1)) for i in range(N)]
SEQ[-1] = dict(M.DONE)
