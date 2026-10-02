"""Final frames for the Dropship Bay (11-TSDROP: the Service Depot's pad alone), both views, into PKG/<view>/...

    python3 dropfinal.py states iso|ra [ss]   building/ 00 healthy, 01 damaged (the mod's TSDROP.ZIP: 2 frames)
    python3 dropfinal.py build iso|ra [ss]    build-up/ 19 frames, the pad's part of GTDEPTMK (laid from its south-west
                                             side across to the north-east, plain grey, then coloured); the last is
                                             the finished bay

Every frame gets a -trim.png (white = house colour, antialiased)."""
import os, sys, time
import numpy as np
from PIL import Image
import dept as M, droprender as RR, deptbuild as DB
from pfinal import save

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-dropship-bay-hd')
NAME = 'dropbay'
VIEWS = {'iso': 'ts-angle', 'ra': 'ra-grid'}


def states(vname, ss=4):
    out = f'{PKG}/{VIEWS[vname]}'
    for level in (0, 1):
        t0 = time.time()
        pr, v = RR.prep(vname, ss, level=level)
        f, ft = pr.frame(want_trim=True)
        del pr
        save(RR.on_canvas(f, vname), RR.on_canvas(ft, vname), f'{out}/building/{NAME}-{level:02d}.png')
        print(vname, 'level', level, '%.0fs' % (time.time() - t0), flush=True)


def build(vname, ss=4, frames=None):
    out = f'{PKG}/{VIEWS[vname]}/build-up'
    n = len(DB.SEQ)
    for i in (frames if frames is not None else range(n)):
        t0 = time.time()
        pr, v = RR.prep(vname, ss, prog=None if i == n - 1 else DB.SEQ[i])
        f, ft = pr.frame(want_trim=True)
        del pr
        save(RR.on_canvas(f, vname), RR.on_canvas(ft, vname), f'{out}/{NAME}-build-{i:02d}.png')
        print(vname, 'build', i, '%.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    what, vname = sys.argv[1], sys.argv[2]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    if what == 'states':
        states(vname, ss)
    else:
        build(vname, ss, [int(a) for a in sys.argv[4:]] or None)
