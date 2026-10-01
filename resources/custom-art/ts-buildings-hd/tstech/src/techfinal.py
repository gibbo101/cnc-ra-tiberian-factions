"""Final frames for the Tech Center (09-TSTECH), both views, into PKG/<view>/...

    TECH_RA=rot|ts3x2 python3 techfinal.py states iso|ra [ss]   the building (00 healthy, 01 damaged), A (the dome:
                                              its pulse; damaged: flicker and sparks) and the 16-frame loop (like
                                              TSTECH.ZIP)
    python3 techfinal.py build iso|ra [ss]    the build-up, 24 frames

Every frame gets a -trim.png (white = house colour, antialiased)."""
import os, sys, time
import techbuild as TB
import techrender as TR
from techrender import BLD, TechPrep
from pfinal import overlay, save

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-gdi-tech-center-hd')
NAME = 'tech-center'
VIEWS = {'iso': 'ts-angle', 'ra': 'ra-grid', 'ra31': 'ra-3x1', 'ra31t': 'ra-3x1-25'}
A_N = 8


def states(vname, ss=4):
    out = f'{PKG}/{VIEWS[vname]}'
    view = TR.view(vname, ss)
    for level in (0, 1):
        t0 = time.time()
        pr = TechPrep(BLD, view, vname=vname, level=level)
        base, trim = pr.frame(want_trim=True)
        save(base, trim, f'{out}/building/{NAME}-{level:02d}.png')
        for t in range(A_N):
            kw = dict(sparks=t) if level else dict(pulse=t)
            f, ft = pr.frame(want_trim=True, **kw)
            o = overlay(base, f)
            save(o, ft, f'{out}/A-dome/{NAME}-dome-{t + level * A_N:02d}.png', alpha_from=o)
            save(f, ft, f'{out}/loop/{NAME}-loop-{t + level * A_N:02d}.png')
        del pr
        print(vname, 'level', level, '%.0fs' % (time.time() - t0), flush=True)


def build(vname, ss=4, frames=None):
    out = f'{PKG}/{VIEWS[vname]}'
    view = TR.view(vname, ss)
    for i in (frames if frames is not None else range(len(TB.SEQ))):
        t0 = time.time()
        pr = TechPrep(BLD, view, vname=vname, prog=None if i == len(TB.SEQ) - 1 else TB.SEQ[i])
        img, trim = pr.frame(want_trim=True)
        save(img, trim, f'{out}/build-up/{NAME}-build-{i:02d}.png')
        del pr
        print(vname, 'build', i, '%.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    what, vname = sys.argv[1], sys.argv[2]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    fr = [int(a) for a in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
    {'states': lambda: states(vname, ss), 'build': lambda: build(vname, ss, fr)}[what]()
