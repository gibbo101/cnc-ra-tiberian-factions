"""Final frames for the Barracks (03-TSPILE), both views, into PKG/<view>/...

    python3 pilefinal.py states iso|ra [ss]   the building (00 healthy, 01 damaged), the overlays A (entrance lamps),
                                              B (the mast's beacon), C (the flag), and the 56-frame loop
    python3 pilefinal.py build iso|ra [ss]    the build-up, 24 frames

Every frame gets a -trim.png (white = house colour, antialiased).  An overlay holds the pixels its frame changes
against the building frame of the same state (see-through pixels solved so building + overlay = frame)."""
import os, sys, time
import numpy as np
from PIL import Image
import brender as BR, pilebuild as PB, pile as PL
from pilerender import BLD
from pfinal import overlay, save

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-gdi-barracks-hd')
NAME = 'barracks'
VIEWS = {'iso': 'ts-angle', 'ra': 'ra-grid'}
A_N, B_N, C_N = 8, 8, 7
LOOP_N = 28                        # TSPILE.ZIP: 28 healthy + 28 damaged
FADE = (1.0, 0.78, 0.63, 0.5)      # TS: 255, 198, 161, 129
BEACON = ((255, 255, 255), (0, 200, 0), (0, 200, 0), (0, 187, 0), (0, 137, 0), (0, 86, 0), (0, 86, 0), (0, 86, 0))


def lamps(t):
    """GTPILE_A: the east lamp flashes and fades over frames 0-3, then the west one over 4-7."""
    t = t % A_N
    return (0.0, FADE[t]) if t < 4 else (FADE[t - 4], 0.0)


def beacon(t):
    return BEACON[t % B_N]


def states(vname, ss=4):
    out = f'{PKG}/{VIEWS[vname]}'
    view = BLD.view(vname, ss)
    for level in (0, 1):
        t0 = time.time()
        pr = BR.Prep(BLD, view, level=level)
        base, trim = pr.frame(want_trim=True)
        save(base, trim, f'{out}/building/{NAME}-{level:02d}.png')
        for t in range(A_N):
            f, ft = pr.frame(want_trim=True, lights=lamps(t))
            o = overlay(base, f)
            save(o, ft, f'{out}/A-lamps/{NAME}-lamps-{t + level * A_N:02d}.png', alpha_from=o)
        for t in range(B_N):
            f, ft = pr.frame(want_trim=True, beacon=beacon(t))
            o = overlay(base, f)
            save(o, ft, f'{out}/B-beacon/{NAME}-beacon-{t + level * B_N:02d}.png', alpha_from=o)
        del pr
        print(vname, 'level', level, 'building, A, B %.0fs' % (time.time() - t0), flush=True)
        for fl in range(C_N):
            t0 = time.time()
            pf = BR.Prep(BLD, view, level=level, flag=fl, flag_az=PL.P['flag_az'][vname])
            f, ft = pf.frame(want_trim=True)
            o = overlay(base, f)
            save(o, ft, f'{out}/C-flag/{NAME}-flag-{fl + level * C_N:02d}.png', alpha_from=o)
            for t in range(fl, LOOP_N, C_N):
                lf, lt = pf.frame(want_trim=True, lights=lamps(t), beacon=beacon(t))
                save(lf, lt, f'{out}/loop/{NAME}-loop-{t + level * LOOP_N:02d}.png')
            del pf
            print(vname, 'level', level, 'flag', fl, '%.0fs' % (time.time() - t0), flush=True)


def build(vname, ss=4, frames=None):
    out = f'{PKG}/{VIEWS[vname]}'
    view = BLD.view(vname, ss)
    for i in (frames if frames is not None else range(len(PB.SEQ))):
        t0 = time.time()
        kw = {}
        if PB.FLAG[i] is not None:
            kw = dict(flag=PB.FLAG[i][1], hoist=PB.FLAG[i][0], flag_az=PL.P['flag_az'][vname])
        pr = BR.Prep(BLD, view, prog=None if i == len(PB.SEQ) - 1 else PB.SEQ[i], **kw)
        img, trim = pr.frame(want_trim=True)
        save(img, trim, f'{out}/build-up/{NAME}-build-{i:02d}.png')
        del pr
        print(vname, 'build', i, '%.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    what, vname = sys.argv[1], sys.argv[2]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    fr = [int(a) for a in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
    {'states': lambda: states(vname, ss), 'build': lambda: build(vname, ss, fr)}[what]()
