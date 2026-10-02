"""Final frames for the Radar (07-TSRADR), both views, into PKG/<view>/...

    python3 radrfinal.py states iso|ra [ss]   building/ 00 healthy, 01 damaged (like GTRADR: no antennas, no dish);
                                             A-dish/ 60 (GTRADR_A: 00-14 the antennas and the dish turning, healthy;
                                             15-29 damaged; 30-59 empty, as TS's), cut against the building;
                                             loop/ 56, the mod's TSRADR.ZIP layout: 28 healthy + 28 damaged, the dish
                                             turning there and back (A frames 0..14..1), straight renders
    python3 radrfinal.py build iso|ra [ss]    build-up/ 26 frames in GTRADRMK's order (the last is the building with
                                             its dish at A frame 0)

Every frame gets a -trim.png (white = house colour, antialiased)."""
import os, sys, time
import numpy as np
from PIL import Image
import radr as M, radrrender as RR, radrbuild as RB
from pfinal import overlay, save

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-radar-hd')
NAME = 'radar'
VIEWS = {'iso': 'ts-angle', 'ra': 'ra-grid'}
NA = 15
PINGPONG = list(range(NA)) + list(range(NA - 2, 0, -1))          # 0..14..1: 28 frames


def canvas(img, vname):
    return RR.on_canvas(img, vname)


def empty(vname):
    return Image.new('RGBA', RR.canvas_of(vname), (0, 0, 0, 0)), Image.new('L', RR.canvas_of(vname), 0)


def states(vname, ss=4, levels=(0, 1)):
    out = f'{PKG}/{VIEWS[vname]}'
    for level in levels:
        t0 = time.time()
        pr, v = RR.prep(vname, ss, level=level, dish=None)
        base, btrim = pr.frame(want_trim=True)
        base, btrim = canvas(base, vname), canvas(btrim, vname)
        save(base, btrim, f'{out}/building/{NAME}-{level:02d}.png')
        print(vname, 'level', level, 'base %.0fs' % (time.time() - t0), flush=True)
        fulls = []
        for t in range(NA):
            t1 = time.time()
            pr, v = RR.prep(vname, ss, level=level, dish=t / (NA - 1.0))
            f, ft = pr.frame(want_trim=True)
            f, ft = canvas(f, vname), canvas(ft, vname)
            ov = overlay(base, f)
            save(ov, ft, f'{out}/A-dish/{NAME}-dish-{t + NA * level:02d}.png', alpha_from=ov)
            fulls.append((f, ft))
            print(vname, 'level', level, 'dish', t, '%.0fs' % (time.time() - t1), flush=True)
        for i, t in enumerate(PINGPONG):
            f, ft = fulls[t]
            save(f, ft, f'{out}/loop/{NAME}-loop-{i + len(PINGPONG) * level:02d}.png')
    e, et = empty(vname)
    for k in range(2 * NA, 4 * NA):
        save(e, et, f'{out}/A-dish/{NAME}-dish-{k:02d}.png')


def build(vname, ss=4, frames=None):
    out = f'{PKG}/{VIEWS[vname]}/build-up'
    for i, prog in enumerate(RB.SEQ):
        if frames is not None and i not in frames:
            continue
        t0 = time.time()
        pr, v = RR.prep(vname, ss, prog=None if i == len(RB.SEQ) - 1 else prog, dish=0.0)
        f, ft = pr.frame(want_trim=True)
        save(canvas(f, vname), canvas(ft, vname), f'{out}/{NAME}-build-{i:02d}.png')
        print(vname, 'build', i, '%.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    what, vname = sys.argv[1], sys.argv[2]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    if what == 'states':
        lv = tuple(int(a) for a in sys.argv[4:]) or (0, 1)
        states(vname, ss, lv)
    elif what == 'build':
        fr = set(int(a) for a in sys.argv[4:]) or None
        build(vname, ss, fr)
