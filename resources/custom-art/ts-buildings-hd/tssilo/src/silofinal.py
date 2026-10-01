"""Final frames for the Tiberium Silo (05-TSSILO), both views, into PKG/<view>/...

    python3 silofinal.py states iso|ra [ss]   the silo (00 healthy, 01 damaged), A (the stored Tiberium, 4 levels)
                                              and B (the blade-tip lamps)
    python3 silofinal.py build iso|ra [ss]    the build-up, 24 frames

Every frame gets a -trim.png (white = house colour, antialiased)."""
import os, sys, time
import numpy as np
import brender as BR, silobuild as SB, silodamage as SD, silo as SL
from silorender import BLD, SiloPrep
from pfinal import overlay, save

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-gdi-tiberium-silo-hd')
NAME = 'silo'
VIEWS = {'iso': 'ts-angle', 'ra': 'ra-grid'}
A_N, B_N = 4, 16
FILL = (0.0, 1 / 3, 2 / 3, 1.0)
# TS's GTSILO_B: a white flash at 0 and 4, fading to pale blue, then steady pale blue
B_COL = [(255, 255, 255), (206, 206, 255), (153, 153, 255), (101, 101, 255), (255, 255, 255)] + [(206, 206, 255)] * 11


def lamps(t, level):
    col = B_COL[t % B_N]
    n = len(SL.P["fins_az"])
    return [None if (level and i in SD.DEAD) else col for i in range(n)]


def states(vname, ss=4):
    out = f'{PKG}/{VIEWS[vname]}'
    view = BLD.view(vname, ss)
    for level in (0, 1):
        t0 = time.time()
        pr = SiloPrep(BLD, view, vname=vname, level=level)
        base, trim = pr.frame(want_trim=True)
        save(base, trim, f'{out}/silo/{NAME}-{level:02d}.png')
        for k, f_ in enumerate(FILL):
            f, ft = pr.frame(want_trim=True, fill=f_)
            o = overlay(base, f)
            save(o, ft, f'{out}/A-tiberium/{NAME}-tiberium-{k + level * A_N:02d}.png', alpha_from=o)
        for t in range(B_N):
            f, ft = pr.frame(want_trim=True, lights=lamps(t, level))
            o = overlay(base, f)
            save(o, ft, f'{out}/B-lamps/{NAME}-lamps-{t + level * B_N:02d}.png', alpha_from=o)
        del pr
        print(vname, 'level', level, '%.0fs' % (time.time() - t0), flush=True)


def build(vname, ss=4, frames=None):
    out = f'{PKG}/{VIEWS[vname]}'
    view = BLD.view(vname, ss)
    for i in (frames if frames is not None else range(len(SB.SEQ))):
        t0 = time.time()
        pr = SiloPrep(BLD, view, vname=vname, prog=None if i == len(SB.SEQ) - 1 else SB.SEQ[i])
        img, trim = pr.frame(want_trim=True)
        save(img, trim, f'{out}/build-up/{NAME}-build-{i:02d}.png')
        del pr
        print(vname, 'build', i, '%.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    what, vname = sys.argv[1], sys.argv[2]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    fr = [int(a) for a in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
    {'states': lambda: states(vname, ss), 'build': lambda: build(vname, ss, fr)}[what]()
