"""The refinery's build-up, in the order TS's NTREFNMK builds it (20 frames), as progress per part (proc.BUILD_KEYS):
  0     the sixteen ribs lying flat on the ground, a starburst
  1     the ribs raised half way, the deck's green ring on their tops
  2-4   the skirt's panels go in, the deck as a frame of spokes then a plate from the middle out; the dock's hazard
        stripes (its floor); the copper cone rises behind the deck
  4-11  the stack rises out of the cone, its collars going on as it passes them; the thin pipes on the west; the
        flanged column (7-11) and the tall one (10-12) rise from the deck
  12-15 the sphere rises out of the skirt, its cap goes on
  13-19 the bib goes down, plain at first, its concrete and stripes coming up (16-19); the gold ring, the black
        pipes and links, the dock lamps last
SEQ has 24 frames (TS's 20 spread over them); its last is the finished building (the healthy frame) on its bib."""
import numpy as np
import proc as PR

# TS's frames: progress per key (anything not listed is 0 before its first listing and 1 after its last)
TS_TABLE = {
    0: dict(ribs=0.04),
    1: dict(ribs=0.55, ring=1.0, mid=0.04),
    2: dict(ribs=1.0, skirt=0.45, deck=0.3, dock=1.0, cone=0.55),
    3: dict(skirt=0.85, deck=0.7, cone=0.85),
    4: dict(skirt=1.0, deck=1.0, cone=1.0, stack=0.12),
    5: dict(stack=0.25),
    6: dict(stack=0.38),
    7: dict(stack=0.5, wpipes=0.5, mid=0.15),
    8: dict(stack=0.62, wpipes=1.0, mid=0.3),
    9: dict(stack=0.74, mid=0.45),
    10: dict(stack=0.88, mid=0.6, tall=0.3),
    11: dict(stack=1.0, mid=0.75, tall=0.5),
    12: dict(mid=0.88, tall=0.7, sphere=0.25),
    13: dict(mid=1.0, tall=0.85, sphere=0.5, pad=1.0, padtex=0.0),
    14: dict(tall=1.0, sphere=0.8, padtex=0.1),
    15: dict(sphere=1.0, cap=1.0, padtex=0.25, gear=1.0),
    16: dict(padtex=0.5, pipes=1.0),
    17: dict(padtex=0.75, lamps=1.0),
    18: dict(padtex=0.92),
    19: dict(padtex=1.0),
}


def ts_state(t):
    """progress of every key at TS frame t (0..19, fractional), linear between the listed frames."""
    out = {}
    for k in PR.BUILD_KEYS:
        pts = sorted((f, v[k]) for f, v in TS_TABLE.items() if k in v)
        if not pts:
            out[k] = 1.0
            continue
        fs = np.array([f for f, _ in pts], float); vs = np.array([v for _, v in pts], float)
        if t < fs[0]:
            out[k] = 0.0 if fs[0] > 0 or vs[0] > 0 else vs[0]
            if t < fs[0] and fs[0] > 0:
                # ramps up from 0 over the frame before its first listing
                out[k] = float(np.clip(1.0 - (fs[0] - t), 0, 1)) * vs[0]
        else:
            out[k] = float(np.interp(t, fs, vs))
    return out


N = 24
SEQ = [ts_state(19.0 * i / (N - 1)) for i in range(N)]
SEQ[-1] = dict(PR.DONE)
