"""Build-up for the Barracks: 24 frames in the order TS's GTPILEMK (20 frames) builds it:
   0- 3  the pad spreads from the middle into its H
   4- 8  the south bunker, then the north one, go up in bare grey block; the west mast; the spine
   8- 9  the blocks are faced (sand, red-brown panels), the entrance is cut
  10-14  the roof slabs, the east mast, the flagpole, the machinery
  16-19  the flag is run up the pole
  22-23  the hatches turn green: 23 is the finished building with its flag (= power... = the healthy frame +
         GTPILE_C frame 00)"""
import pile as PL

K = PL.BUILD_KEYS


def _p(**kw):
    d = {k: 0.0 for k in K}
    d.update(kw)
    return d


F = 1.0
SEQ = [
    _p(pad=0.2), _p(pad=0.45), _p(pad=0.75), _p(pad=F),
    _p(pad=F, south=0.3),
    _p(pad=F, south=0.6, north=0.2),
    _p(pad=F, south=0.9, north=0.5, masts=0.3),
    _p(pad=F, south=F, north=0.8, masts=0.6, spine=0.5),
    _p(pad=F, south=F, north=F, masts=F, spine=F, paint=0.5),
    _p(pad=F, south=F, north=F, masts=F, spine=F, paint=F, entrance=0.5),
    _p(pad=F, south=F, north=F, masts=F, spine=F, paint=F, entrance=F, roofs=0.35),
    _p(pad=F, south=F, north=F, masts=F, spine=F, paint=F, entrance=F, roofs=0.7, mast2=0.4, pole=0.3),
    _p(pad=F, south=F, north=F, masts=F, spine=F, paint=F, entrance=F, roofs=F, mast2=0.8, pole=0.6, machines=0.3),
    _p(pad=F, south=F, north=F, masts=F, spine=F, paint=F, entrance=F, roofs=F, mast2=F, pole=F, machines=0.65),
    _p(pad=F, south=F, north=F, masts=F, spine=F, paint=F, entrance=F, roofs=F, mast2=F, pole=F, machines=F),
]
FULL = dict(pad=F, south=F, north=F, masts=F, spine=F, paint=F, entrance=F, roofs=F, mast2=F, pole=F, machines=F)
SEQ += [_p(**FULL)] * 5                                   # 15-19: the flag goes up (FLAG below)
SEQ += [_p(**FULL), _p(**FULL), _p(**FULL, hatches=0.5), dict(PL.DONE)]
assert len(SEQ) == 24
# the flag: (hoist, wave frame) per build-up frame; None = no flag yet
FLAG = [None] * 15 + [(0.15, 0), (0.4, 1), (0.65, 2), (0.85, 3), (1.0, 4), (1.0, 5), (1.0, 6), (1.0, 0), (1.0, 0)]
TS_N = 20


def ts_index(i):
    return int(round(i * (TS_N - 1) / (len(SEQ) - 1)))
