"""Final frames for the Helipad (08-TSHPAD), both views, into PKG/<view>/...

    python3 hpadfinal.py states iso|ra [ss]   bib/ 00, 01 (GTHPADBB: the pad alone); building/ 00, 01 (GTHPAD: the
                                             machinery, cut against the pad so bib + building = the whole helipad);
                                             A-lights/ 32 (GTHPAD_A: 00-07 healthy, 08-15 damaged, 16-31 empty), cut
                                             against bib + building; loop/ 16, the mod's TSHPAD.ZIP layout (8 healthy
                                             + 8 damaged, the lights running), straight renders
    python3 hpadfinal.py build iso|ra [ss]    build-up/ 24 frames in GTHPADMK's order (the last is the whole helipad)

Every frame gets a -trim.png (white = house colour, antialiased)."""
import os, sys, time
import numpy as np
from PIL import Image
import hpad as M, hpadrender as RR, hpadbuild as HB
from pfinal import overlay, save

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-helipad-hd')
NAME = 'helipad'
VIEWS = {'iso': 'ts-angle', 'ra': 'ra-grid'}
NL = 8


def canvas(img, vname):
    return RR.on_canvas(img, vname)


def empty(vname):
    return Image.new('RGBA', RR.canvas_of(vname), (0, 0, 0, 0)), Image.new('L', RR.canvas_of(vname), 0)


def states(vname, ss=4):
    out = f'{PKG}/{VIEWS[vname]}'
    for level in (0, 1):
        t0 = time.time()
        pb, v = RR.prep(vname, ss, level=level, pad=True)
        bib, btrim = pb.frame(want_trim=True, level=level)
        bib, btrim = canvas(bib, vname), canvas(btrim, vname)
        save(bib, btrim, f'{out}/bib/{NAME}-bib-{level:02d}.png')
        pr, v = RR.prep(vname, ss, level=level)
        full, ftrim = pr.frame(want_trim=True, level=level)
        full, ftrim = canvas(full, vname), canvas(ftrim, vname)
        bld = overlay(bib, full)
        save(bld, ftrim, f'{out}/building/{NAME}-{level:02d}.png', alpha_from=bld)
        for t in range(NL):
            f, ft = pr.frame(want_trim=True, lights=t, level=level)
            f, ft = canvas(f, vname), canvas(ft, vname)
            ov = overlay(full, f)
            save(ov, ft, f'{out}/A-lights/{NAME}-lights-{t + NL * level:02d}.png', alpha_from=ov)
            save(f, ft, f'{out}/loop/{NAME}-loop-{t + NL * level:02d}.png')
        print(vname, 'level', level, '%.0fs' % (time.time() - t0), flush=True)
    e, et = empty(vname)
    for k in range(2 * NL, 4 * NL):
        save(e, et, f'{out}/A-lights/{NAME}-lights-{k:02d}.png')


def build(vname, ss=4):
    out = f'{PKG}/{VIEWS[vname]}/build-up'
    for i, prog in enumerate(HB.SEQ):
        t0 = time.time()
        pr, v = RR.prep(vname, ss, prog=None if i == len(HB.SEQ) - 1 else prog)
        f, ft = pr.frame(want_trim=True)
        save(canvas(f, vname), canvas(ft, vname), f'{out}/{NAME}-build-{i:02d}.png')
        print(vname, 'build', i, '%.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    what, vname = sys.argv[1], sys.argv[2]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    {'states': states, 'build': build}[what](vname, ss)
