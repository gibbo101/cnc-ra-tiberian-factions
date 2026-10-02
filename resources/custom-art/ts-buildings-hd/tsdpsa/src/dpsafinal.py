"""Final frames for the Sensor Array (14-TSDPSA), both views, into PKG/<view>/...

    python3 dpsafinal.py states iso|ra [ss]   building/ 00 healthy, 01 damaged (TS's GTDPSA has 3 frames, all the same
                                             picture; RA has no destroyed state); A-flash/ 10 (GTDPSA_A: 00-04 the light
                                             bar's flash, cut against the healthy building; 05-09 empty, as TS's
                                             damaged half); loop/ 10, the mod's TSDPSA.ZIP layout (5 healthy with the
                                             flash, 5 damaged), straight renders
    python3 dpsafinal.py build iso|ra [ss]    build-up/ 36 frames in GTDPSAMK's order (the last is the finished array)

Every frame gets a -trim.png (white = house colour, antialiased)."""
import os, sys, time
import numpy as np
from PIL import Image
import dpsa as M, dpsarender as RR, dpsabuild as DB
from pfinal import overlay, save

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-sensor-array-hd')
NAME = 'sensor-array'
VIEWS = {'iso': 'ts-angle', 'ra': 'ra-grid'}
NA = 5


def canvas(img, vname):
    return RR.on_canvas(img, vname)


def empty(vname):
    return Image.new('RGBA', RR.canvas_of(vname), (0, 0, 0, 0)), Image.new('L', RR.canvas_of(vname), 0)


def states(vname, ss=4, levels=(0, 1)):
    out = f'{PKG}/{VIEWS[vname]}'
    for level in levels:
        t0 = time.time()
        pr, v = RR.prep(vname, ss, level=level)
        base, btrim = pr.frame(want_trim=True)
        base, btrim = canvas(base, vname), canvas(btrim, vname)
        save(base, btrim, f'{out}/building/{NAME}-{level:02d}.png')
        for t in range(NA):
            if level == 0:
                f, ft = pr.frame(want_trim=True, flash=t)
                f, ft = canvas(f, vname), canvas(ft, vname)
                ov = overlay(base, f)
                save(ov, ft, f'{out}/A-flash/{NAME}-flash-{t:02d}.png', alpha_from=ov)
                save(f, ft, f'{out}/loop/{NAME}-loop-{t:02d}.png')
            else:
                e, et = empty(vname)
                save(e, et, f'{out}/A-flash/{NAME}-flash-{NA + t:02d}.png')
                save(base, btrim, f'{out}/loop/{NAME}-loop-{NA + t:02d}.png')
        del pr
        print(vname, 'level', level, '%.0fs' % (time.time() - t0), flush=True)


def build(vname, ss=4, frames=None):
    out = f'{PKG}/{VIEWS[vname]}/build-up'
    n = DB.N
    for i in (frames if frames is not None else range(n)):
        t0 = time.time()
        pr, v = RR.prep(vname, ss, prog=None if i == n - 1 else DB.SEQ[i])
        f, ft = pr.frame(want_trim=True)
        del pr
        save(canvas(f, vname), canvas(ft, vname), f'{out}/{NAME}-build-{i:02d}.png')
        print(vname, 'build', i, '%.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    what, vname = sys.argv[1], sys.argv[2]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    if what == 'states':
        states(vname, ss)
    else:
        build(vname, ss, [int(a) for a in sys.argv[4:]] or None)
