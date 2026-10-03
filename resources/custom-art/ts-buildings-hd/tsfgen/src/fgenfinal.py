"""Final frames for the Firestorm Generator (16-TSFGEN, TS GAFIRE), both views, into PKG/<view>/...

    python3 fgenfinal.py states iso|ra [ss]   building/ 00 healthy, 01 damaged (as GTFIRE: no dome, the pit open);
                                             C-lamps/ 12 (GTFIRE_C: 6 + 6 empty), cut against the building
    python3 fgenfinal.py dome iso|ra [ss]     A-dome/ 40 (GTFIRE_A: the arm lifting the dome, 20 + 20 empty)
    python3 fgenfinal.py lightning iso|ra [ss] B-lightning/ 32 (GTFIRE_B: the dome raised, lightning in the pit and the
                                             ring glowing by turns, 16 + 16 empty) and loop/ 96 (TSFGEN.ZIP's layout:
                                             00-47 healthy with B and C playing, 48-95 damaged, as the mod's)
    python3 fgenfinal.py build iso|ra [ss] [frames]   build-up/ 19 frames (the last: building-00 + A-dome-00)

Every frame gets a -trim.png (white = house colour, antialiased)."""
import os, sys, time
import numpy as np
from PIL import Image
import hd, fgen as M, fgenrender as WR, fgenbuild as WB
from pfinal import overlay, save

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-firestorm-generator-hd')
NAME = 'firestorm-generator'
VIEWS = {'iso': 'ts-angle', 'ra': 'ra-grid'}
NA, NB, NC, NL = 20, 16, 6, 48


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
        if level == 0:
            for k in range(NC):
                f, ft = pr.frame(want_trim=True, lamps=k)
                f, ft = canvas(f, vname), canvas(ft, vname)
                o = overlay(base, f)
                save(o, ft, f'{out}/C-lamps/{NAME}-lamps-{k:02d}.png', alpha_from=o)
            e, et = empty(vname)
            for k in range(NC):
                save(e, et, f'{out}/C-lamps/{NAME}-lamps-{NC + k:02d}.png')
        del pr
        print(vname, 'states', level, '%.0fs' % (time.time() - t0), flush=True)


def dome(vname, ss=4, frames=None):
    """GTFIRE_A: the arm lifting the dome off the pit over 20 frames (TS's pace), cut against the building."""
    out = f'{PKG}/{VIEWS[vname]}'
    base, _ = base_frame(vname)
    for k in (frames if frames is not None else range(NA)):
        t0 = time.time()
        pr, v = WR.prep(vname, ss, level=0, arm=M.dome_lift(k / (NA - 1)))
        f, ft = pr.frame(want_trim=True)
        f, ft = canvas(f, vname), canvas(ft, vname)
        del pr
        o = overlay(base, f)
        save(o, ft, f'{out}/A-dome/{NAME}-dome-{k:02d}.png', alpha_from=o)
        print(vname, 'dome', k, '%.0fs' % (time.time() - t0), flush=True)
    e, et = empty(vname)
    for k in range(NA):
        p_ = f'{out}/A-dome/{NAME}-dome-{NA + k:02d}.png'
        if not os.path.exists(p_):
            save(e, et, p_)


def lightning(vname, ss=4, part=None, which=None):
    """GTFIRE_B (16 frames, the dome raised): even frames lightning in the pit (8 patterns), odd frames the ring
    glowing blue; cut against the building.  The same passes give loop/: the mod's TSFGEN.ZIP layout, 00-47 the
    healthy building with B (t % 16) and C (t % 6) playing, straight renders; 48-95 the damaged building (the mod draws
    no overlays on it).  part: 'bolts' (the 8 lightning passes, one geometry at a time) or 'ring' (one pass: the odd
    frames, the empties and the damaged half of loop/); None both."""
    out = f'{PKG}/{VIEWS[vname]}'
    base, _ = base_frame(vname)

    def emit(pr, bi, mk):
        f, ft = pr.frame(want_trim=True, **mk)
        f, ft = canvas(f, vname), canvas(ft, vname)
        o = overlay(base, f)
        save(o, ft, f'{out}/B-lightning/{NAME}-lightning-{bi:02d}.png', alpha_from=o)
        for t in range(bi, NL, NB):
            g, gt = pr.frame(want_trim=True, lamps=t % NC, **mk)
            save(canvas(g, vname), canvas(gt, vname), f'{out}/loop/{NAME}-loop-{t:02d}.png')

    if part in (None, 'bolts'):
        for b in (which if which is not None else range(0, NB, 2)):
            t0 = time.time()
            pr, v = WR.prep(vname, ss, level=0, arm=1.0, bolt=b // 2)
            emit(pr, b, {})
            del pr
            print(vname, 'lightning', b, '%.0fs' % (time.time() - t0), flush=True)
    if part in (None, 'ring'):
        t0 = time.time()
        pr, v = WR.prep(vname, ss, level=0, arm=1.0)
        for b in range(1, NB, 2):
            emit(pr, b, {'ring': True})
        del pr
        e, et = empty(vname)
        for k in range(NB):
            save(e, et, f'{out}/B-lightning/{NAME}-lightning-{NB + k:02d}.png')
        d, dt = base_frame(vname, 1)
        for t in range(NL):
            save(d, dt, f'{out}/loop/{NAME}-loop-{NL + t:02d}.png')
        print(vname, 'lightning odd + empties', '%.0fs' % (time.time() - t0), flush=True)


def build(vname, ss=4, frames=None):
    out = f'{PKG}/{VIEWS[vname]}'
    n = len(WB.SEQ)
    for i in (frames if frames is not None else range(n)):
        t0 = time.time()
        if i == n - 1:
            # the last frame: exactly the building with the dome closed on it (building-00 + A-dome-00)
            b, bt = base_frame(vname)
            a = Image.open(f'{out}/A-dome/{NAME}-dome-00.png').convert('RGBA')
            at = Image.open(f'{out}/A-dome/{NAME}-dome-00-trim.png').convert('L')
            comp = b.copy(); comp.alpha_composite(a)
            aa = np.array(a)[..., 3:4].astype(np.float32) / 255.0
            tt = np.array(at).astype(np.float32)[..., None] * aa + np.array(bt).astype(np.float32)[..., None] * (1 - aa)
            save(comp, Image.fromarray(tt[..., 0].round().astype(np.uint8), 'L'), f'{out}/build-up/{NAME}-build-{i:02d}.png')
        else:
            g = WB.SEQ[i]
            arm = g.get('lift', 0.0) if g.get('arm', 0) > 0 else None
            pr, v = WR.prep(vname, ss, prog=g, arm=arm)
            img, trim = pr.frame(want_trim=True)
            del pr
            save(canvas(img, vname), canvas(trim, vname), f'{out}/build-up/{NAME}-build-{i:02d}.png')
        print(vname, 'build', i, '%.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    what, vname = sys.argv[1], sys.argv[2]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    fr = [int(a) for a in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
    for sub in ('building', 'C-lamps', 'A-dome', 'B-lightning', 'loop', 'build-up'):
        os.makedirs(f'{PKG}/{VIEWS[vname]}/{sub}', exist_ok=True)
    {'states': lambda: states(vname, ss), 'dome': lambda: dome(vname, ss, fr), 'lightning': lambda: lightning(vname, ss),
     'bolts': lambda: lightning(vname, ss, 'bolts', fr), 'ring': lambda: lightning(vname, ss, 'ring'),
     'build': lambda: build(vname, ss, fr)}[what]()
