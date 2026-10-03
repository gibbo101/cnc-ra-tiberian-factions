"""Final frames for the EMP Pulse Cannon (13-TSPULS), both views, into PKG/<view>/...

    python3 pulsfinal.py states iso|ra [ss]   building/ 00 healthy, 01 damaged (NAPULS 0, 1; RA has no destroyed
                                             state), without the head (it is its own set, as in the mod)
    python3 pulsfinal.py head iso|ra [ss] [f ..]
                                             head/ 00-31: the head on its drum at NAPULS_A's 32 facings (00 north,
                                             turning anticlockwise: 08 west, 16 south, 24 east), each cut against the
                                             healthy building (its shadow on the building included), like the mod's
                                             TSPULST.ZIP
    python3 pulsfinal.py build iso|ra [ss]    build-up/ 24 frames in NAPULSMK's order (the last = the healthy building)

Every frame gets a -trim.png (white = house colour, antialiased)."""
import os, sys, time
from PIL import Image
import puls as M, pulsrender as RR, pulsbuild as DB
from pfinal import overlay, save

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-pulse-cannon-hd')
NAME = 'pulse-cannon'
VIEWS = {'iso': 'ts-angle', 'ra': 'ra-grid'}
NF = 32


def canvas(img, vname):
    return RR.on_canvas(img, vname)


def states(vname, ss=4, levels=(0, 1)):
    out = f'{PKG}/{VIEWS[vname]}'
    for level in levels:
        t0 = time.time()
        pr, v = RR.prep(vname, ss, level=level)
        f, ft = pr.frame(want_trim=True)
        del pr
        save(canvas(f, vname), canvas(ft, vname), f'{out}/building/{NAME}-{level:02d}.png')
        print(vname, 'level', level, '%.0fs' % (time.time() - t0), flush=True)


def head(vname, ss=4, facings=None):
    out = f'{PKG}/{VIEWS[vname]}/head'
    pb, v = RR.prep(vname, ss)
    base = canvas(pb.frame(), vname)
    del pb
    for f in (facings if facings is not None else range(NF)):
        t0 = time.time()
        pr, v = RR.prep(vname, ss, head=f)
        img, it = pr.frame(want_trim=True)
        del pr
        img, it = canvas(img, vname), canvas(it, vname)
        ov = overlay(base, img)
        save(ov, it, f'{out}/{NAME}-head-{f:02d}.png', alpha_from=ov)
        print(vname, 'head', f, '%.0fs' % (time.time() - t0), flush=True)


def build(vname, ss=4, frames=None):
    out = f'{PKG}/{VIEWS[vname]}/build-up'
    for i in (frames if frames is not None else range(DB.N)):
        t0 = time.time()
        pr, v = RR.prep(vname, ss, prog=DB.SEQ[i])
        f, ft = pr.frame(want_trim=True)
        del pr
        save(canvas(f, vname), canvas(ft, vname), f'{out}/{NAME}-build-{i:02d}.png')
        print(vname, 'build', i, '%.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    what, vname = sys.argv[1], sys.argv[2]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    rest = [int(a) for a in sys.argv[4:]] or None
    if what == 'states':
        states(vname, ss)
    elif what == 'head':
        head(vname, ss, rest)
    elif what == 'build':
        build(vname, ss, rest)
