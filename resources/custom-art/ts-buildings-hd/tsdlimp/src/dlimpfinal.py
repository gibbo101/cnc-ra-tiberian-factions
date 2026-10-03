"""Final frames for the Limpet Mine (18-TSDLIMP, TS DLIMPET), both views (256x256), into PKG/<view>/...

    python3 dlimpfinal.py states iso|ra [ss]   building/ 00 healthy, 01 damaged; A-flash/ 10 (DLIMP_A: the dug-in top
                                              flashing, cut against the building; 07-09 empty as TS's) and loop/ 20
                                              (TSDLIMP.ZIP's layout: 00-09 healthy with A k, 10-19 damaged with A k,
                                              straight renders)
    python3 dlimpfinal.py build iso|ra [ss] [frames]   build-up/ 42 frames (DLIMPMK's 42; the last = building-00)

Every frame gets a -trim.png (white = house colour, antialiased)."""
import os, sys, time
import numpy as np
from PIL import Image
import hd, dlimp as M, dlimprender as WR, dlimpbuild as WB
from pfinal import overlay, save

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-limpet-mine-hd')
NAME = 'limpet-mine'
VIEWS = {'iso': 'ts-angle', 'ra': 'ra-grid'}
NA = 10                 # DLIMP_A: 7 real frames (0 white, 1 green, 2-6 fading) + 3 as the building


def canvas(img, vname):
    return WR.on_canvas(img, vname)


def empty(vname):
    return Image.new('RGBA', WR.canvas_of(vname), (0, 0, 0, 0)), Image.new('L', WR.canvas_of(vname), 0)


def base_frame(vname, level=0):
    out = f'{PKG}/{VIEWS[vname]}'
    return (Image.open(f'{out}/building/{NAME}-{level:02d}.png').convert('RGBA'),
            Image.open(f'{out}/building/{NAME}-{level:02d}-trim.png').convert('L'))


def states(vname, ss=4):
    out = f'{PKG}/{VIEWS[vname]}'
    for level in (0, 1):
        t0 = time.time()
        pr, v = WR.prep(vname, ss, level=level)
        base, trim = pr.frame(want_trim=True)
        base, trim = canvas(base, vname), canvas(trim, vname)
        save(base, trim, f'{out}/building/{NAME}-{level:02d}.png')
        for k in range(NA):
            if k < 7:
                f, ft = pr.frame(want_trim=True, glow=k)
                f, ft = canvas(f, vname), canvas(ft, vname)
            else:
                f, ft = base, trim
            save(f, ft, f'{out}/loop/{NAME}-loop-{level * NA + k:02d}.png')
            if level == 0:
                if k < 7:
                    o = overlay(base, f)
                    save(o, ft, f'{out}/A-flash/{NAME}-flash-{k:02d}.png', alpha_from=o)
                else:
                    e, et = empty(vname)
                    save(e, et, f'{out}/A-flash/{NAME}-flash-{k:02d}.png')
        del pr
        print(vname, 'states', level, '%.0fs' % (time.time() - t0), flush=True)


def build(vname, ss=4, frames=None):
    out = f'{PKG}/{VIEWS[vname]}'
    n = len(WB.SEQ)
    for i in (frames if frames is not None else range(n)):
        t0 = time.time()
        g = WB.SEQ[i]
        if g.get('final'):
            b, bt = base_frame(vname)
            save(b, bt, f'{out}/build-up/{NAME}-build-{i:02d}.png')
        else:
            pr, v = WR.prep(vname, ss, pose=g['pose'])
            img, trim = pr.frame(want_trim=True, lamp=g.get('lamp'), eye=g.get('eye'))
            del pr
            save(canvas(img, vname), canvas(trim, vname), f'{out}/build-up/{NAME}-build-{i:02d}.png')
        print(vname, 'build', i, '%.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    what, vname = sys.argv[1], sys.argv[2]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    fr = [int(a) for a in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
    for sub in ('building', 'A-flash', 'loop', 'build-up'):
        os.makedirs(f'{PKG}/{VIEWS[vname]}/{sub}', exist_ok=True)
    {'states': lambda: states(vname, ss), 'build': lambda: build(vname, ss, fr)}[what]()
