"""The War Factory's build-up, in the order TS's GTWEAPMK builds it (20 real frames, 0-19), as progress per part
(weap.BUILD_KEYS).  TS draws it all plain grey until frame 18 (the apron gets its colour) and 19 (the building):
  0-2   a grey construction slab spreads out from the middle of the foundation
  2-5   the hall rises out of it, the door and its fenders with it
  5-10  the two poles: lying at the south-west, stood upright (9), leant back onto the hall (10-11); the hazard stripes
        on the apron (6, black and white); the panel's frame rises up the slope, ribs in threes (6-8); the three small
        lamps (10), lit as TS's (the lamps glow in TS's grey build-up)
  11-13 the roof: the beam over the door and the west pole's beam, the frame, ridges and housings, the north band
  13-15 the five lamps on the beam one by one, the north fender's green cap, the green unit; the panel fills the frame (15)
  16-17 the west block, then the fan platform with its fans
  18-19 colour: the apron (18), then the building (19)
SEQ has 26 frames (TS's 20 spread over them); its last is the finished building (the healthy frame) on its bib."""
import numpy as np
import weap as M

TS_TABLE = {
    0: dict(slab=0.15),
    1: dict(slab=0.45),
    2: dict(slab=0.75, hall=0.2),
    3: dict(slab=0.9, hall=0.6, door=1.0, jambs=0.55),
    4: dict(slab=1.0, hall=0.85, jambs=0.85),
    5: dict(hall=1.0, jambs=1.0, pad=1.0, poles=0.04),
    6: dict(chev=1.0, poles=0.15, pframe=0.3),
    7: dict(poles=0.28, pframe=0.65),
    8: dict(poles=0.4, pframe=1.0),
    9: dict(poles=0.5),
    10: dict(poles=0.78, lampsB=1.0),
    11: dict(poles=1.0, beam=1.0, roof=0.4),
    12: dict(roof=0.75),
    13: dict(roof=1.0, lampsA=0.4),
    14: dict(lampsA=0.8, ncap=0.6),
    15: dict(lampsA=1.0, ncap=1.0, panel=1.0),
    16: dict(west=1.0),
    17: dict(fans=1.0, padtex=0.0, paint=0.0),
    18: dict(padtex=1.0, paint=0.0),
    19: dict(padtex=1.0, paint=1.0),
}
STEP = ('door', 'chev', 'lampsB', 'beam', 'panel', 'west', 'fans', 'pad')      # parts that appear at once


def ts_state(t):
    """progress of every key at TS frame t (0..19, fractional), linear between the listed frames (0 before a key's
    first listing, ramping up over the frame before it; parts in STEP appear whole at their frame)."""
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
        if k in ('padtex', 'paint'):
            # a step, as TS's: a part is either MK grey or coloured, never a blend (a half-green part would not be
            # house colour: the trim can't carry it, and it would stay green for every house)
            on = fs[vs >= 1.0 - 1e-6]
            out[k] = 1.0 if (len(on) and t >= on[0] - 1e-6) else 0.0
            continue
        if t < fs[0]:
            out[k] = float(np.clip(1.0 - (fs[0] - t), 0, 1)) * vs[0] if fs[0] > 0 else 0.0
        else:
            out[k] = float(np.interp(t, fs, vs))
    return out


N = 26
SEQ = [ts_state(19.0 * i / (N - 1)) for i in range(N)]
SEQ[-1] = dict(M.DONE)
