"""Final frames for the Firestorm Wall Section (17-TSFSDF, TS GAFSDF), both views, into PKG/<view>/...

    python3 fsdffinal.py walls iso|ra [ss]   wall/firestorm-wall-00..63: TSFSDF.ZIP's layout, frame = the neighbour
                                            mask (N1 E2 S4 W8) + 16 damaged + 32 with the field on
    python3 fsdffinal.py pulse iso|ra [ss]   A-pulse/firestorm-wall-pulse-00..07 (GTFSDF_A: the emitter pulsing, 4
                                            frames + 4 empty), cut against wall-00 (any section with a pad: not 05, 10)
Every frame gets a -trim.png (all black: no house colour on it, as TS's)."""
import os, sys, time
import numpy as np
from PIL import Image
import fsdf as M, fsdfrender as WR
from pfinal import overlay, save

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-firestorm-wall-hd')
NAME = 'firestorm-wall'
VIEWS = {'iso': 'ts-angle', 'ra': 'ra-grid'}


def canvas(img, vname):
    return WR.on_canvas(img, vname)


def walls(vname, ss=4):
    out = f'{PKG}/{VIEWS[vname]}/wall'
    os.makedirs(out, exist_ok=True)
    for level in (0, 1):
        for mask in range(16):
            t0 = time.time()
            pr, v = WR.prep(vname, ss, mask=mask, level=level)
            for live in (False, True):
                f, ft = pr.frame(want_trim=True, live=live)
                save(canvas(f, vname), canvas(ft, vname), f'{out}/{NAME}-{mask + 16 * level + 32 * live:02d}.png')
            del pr
            print(vname, 'wall', mask, level, '%.0fs' % (time.time() - t0), flush=True)


def pulse(vname, ss=4):
    out = f'{PKG}/{VIEWS[vname]}/A-pulse'
    os.makedirs(out, exist_ok=True)
    base = Image.open(f'{PKG}/{VIEWS[vname]}/wall/{NAME}-00.png').convert('RGBA')
    pr, v = WR.prep(vname, ss, mask=0, level=0)
    for k in range(4):
        f, ft = pr.frame(want_trim=True, pulse=k)
        f, ft = canvas(f, vname), canvas(ft, vname)
        o = overlay(base, f)
        save(o, ft, f'{out}/{NAME}-pulse-{k:02d}.png', alpha_from=o)
    e = Image.new('RGBA', WR.canvas_of(vname), (0, 0, 0, 0)); et = Image.new('L', WR.canvas_of(vname), 0)
    for k in range(4, 8):
        save(e, et, f'{out}/{NAME}-pulse-{k:02d}.png')
    print(vname, 'pulse done', flush=True)


if __name__ == '__main__':
    what, vname = sys.argv[1], sys.argv[2]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    {'walls': lambda: walls(vname, ss), 'pulse': lambda: pulse(vname, ss)}[what]()
