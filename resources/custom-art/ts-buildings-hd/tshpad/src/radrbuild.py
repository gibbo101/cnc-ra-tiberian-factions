"""The Radar's build-up, in the order TS's GTRADRMK builds it (20 real frames, 0-19), as progress per part
(radr.BUILD_KEYS).  TS draws it all plain grey until its colours fade in (15-17) and the house green comes (18):
  0-1   the grey slab spreads out from the middle and covers the foundation
  2-4   the tower's first frame stands up in the middle; the south-west block lies on the ground and is raised; a ring
        on the ground where the rotunda goes
  5     the deck is built low on the tower's base with its machinery on it; the block is up
  6-9   the deck is jacked up as the tower grows under it; the antennas grow on it; the rotunda's pedestal and posts;
        the south box, the east base and its ramp
  10    the rotunda's dome; the dish's turret
  11-15 the dish: its struts, then its skin round from one side
  15-17 the colours fade in; 18 the house green
SEQ has 26 frames (TS's 20 spread over them); its last is the finished building (the healthy frame with its dish at
GTRADR_A frame 0)."""
import numpy as np
import radr as M

TS_TABLE = {
    0: dict(slab=0.25),
    1: dict(slab=1.0),
    2: dict(tower=0.15),
    3: dict(tower=0.3, swblock=0.12, rotunda=0.1),
    4: dict(tower=0.4, swblock=0.55, rotunda=0.25),
    5: dict(swblock=1.0, rotunda=0.4, upper=1.0, lift=0.0),
    6: dict(lift=0.35, rotunda=0.5, eastbase=1.0),
    7: dict(lift=0.6, masts=0.3, rotunda=0.62),
    8: dict(lift=0.82, masts=0.65, rotunda=0.72),
    9: dict(lift=1.0, masts=1.0, rotunda=0.8, sbox=1.0, ramp=0.5),
    10: dict(rotunda=1.0, ramp=1.0, turret=1.0),
    11: dict(dish=0.15),
    12: dict(dish=0.3),
    13: dict(dish=0.55),
    14: dict(dish=0.8),
    15: dict(dish=1.0, paint=0.3),
    16: dict(paint=0.6),
    17: dict(paint=0.9),
    18: dict(paint=1.0),
}
STEP = ('upper', 'eastbase', 'turret', 'sbox')
FIRST = {'lift': 5}                 # lift is 0 (built low) from its first frame


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
        if k == 'paint':
            out[k] = float(np.interp(t, np.concatenate([[fs[0] - 1], fs]), np.concatenate([[0.0], vs]))) if t >= fs[0] - 1 else 0.0
            continue
        if t < fs[0]:
            out[k] = float(np.clip(1.0 - (fs[0] - t), 0, 1)) * vs[0] if fs[0] > 0 else 0.0
        else:
            out[k] = float(np.interp(t, fs, vs))
    # the deck appears (built low) with its machinery at frame 5: until then nothing lifts
    if t < 5 - 1e-6:
        out['upper'] = 0.0
    return out


N = 26
SEQ = [ts_state(19.0 * i / (N - 1)) for i in range(N)]
SEQ[-1] = dict(M.DONE)
