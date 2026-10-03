"""The Firestorm Generator's build-up, in TS's order (GTFIREMK: 17 real frames), as 19 frames (the mod's
TSFGENMAKE has 19):
  00-03  the grey slab spreads out from the pit (a ring round it first), the base with it
  04-05  the emitter rises in the pit
  05-07  the fins rise (grey)
  06-08  the drum rises round the pit; 09 the struts and the hatch
  07-10  the colours come in (the house parts in red-brown primer, as TS's)
  11-15  the arm comes over high with the dome and lowers it onto the pit
  16     the house parts go green
  17-18  finished, the dome closed (building-00 + A-00, as TS's MK ends)"""
import numpy as np
import fgen as M

TABLE = {
    0: dict(slab=0.12, base=1.0), 1: dict(slab=0.35), 2: dict(slab=0.65), 3: dict(slab=1.0),
    4: dict(mech=0.5), 5: dict(mech=1.0, fins=0.3), 6: dict(fins=0.65, drum=0.3), 7: dict(fins=1.0, drum=0.65, paint=0.0),
    8: dict(drum=1.0, paint=0.4), 9: dict(struts=1.0, hatch=1.0, paint=0.8), 10: dict(paint=1.0),
    11: dict(arm=1.0, lift=1.6), 12: dict(lift=1.2), 13: dict(lift=0.8), 14: dict(lift=0.4), 15: dict(lift=0.0),
    16: dict(green=1.0),
}
STEP = ('struts', 'hatch', 'arm', 'green', 'base')
KEYS = M.BUILD_KEYS + ('lift',)


def state(t):
    out = {}
    for k in KEYS:
        pts = sorted((f, v[k]) for f, v in TABLE.items() if k in v)
        if not pts:
            out[k] = 1.0
            continue
        fs = np.array([f for f, _ in pts], float); vs = np.array([v for _, v in pts], float)
        if k in STEP:
            out[k] = 1.0 if t >= fs[0] - 1e-6 else 0.0
        elif t < fs[0]:
            out[k] = 0.0
        else:
            out[k] = float(np.interp(t, fs, vs))
    return out


N = 19
SEQ = [state(float(i)) for i in range(N)]
SEQ[-1] = dict(M.DONE, lift=0.0)

if __name__ == '__main__':
    for i, s in enumerate(SEQ):
        print(i, {k: round(v, 2) for k, v in s.items() if v})
