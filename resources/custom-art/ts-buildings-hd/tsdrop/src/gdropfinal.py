"""Final frames for the Dropship Bay (GTDROP), both views, into PKG/<view>/...

    python3 gdropfinal.py states iso|ra [ss]  building/ 00 healthy (the dish's box, no dish: A draws it), 01 damaged (the
                                             dish standing still: TS's A has no damaged half); B-lights/ 40 (GTDROP_B:
                                             00-19 the pad's four light bars over the healthy building, 20-39 over the
                                             damaged one, two of them smashed)
    python3 gdropfinal.py base|lights iso|ra [ss]   the same, building/ only or B-lights/ only
    python3 gdropfinal.py dish iso|ra [ss]    A-dish/ 40 (GTDROP_A: 00-19 the dish turning once over the healthy building;
                                             20-39 empty, as TS's: the damaged building's dish stands still)
    python3 gdropfinal.py build iso|ra [ss] [frames]   build-up/ 19 frames in GTDROPMK's order (as TSDROPMAKE.ZIP); the dish
                                             at its A frame 00 angle throughout, so the last frame = the healthy building
                                             + A 00 and nothing jumps when the loop starts

Every frame gets a -trim.png (white = house colour, antialiased)."""
import os, sys, time
import numpy as np
from PIL import Image
import gdrop as M, gdroprender as RR, gdropbuild as DB, plug as PL
from pfinal import overlay, save

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-dropship-bay-hd')
NAME = 'dropbay'
VIEWS = {'iso': 'ts-angle', 'ra': 'ra-grid'}
NA, NB = 20, 20


def dish_az(t):
    """GTDROP_A frame t: the Upgrade Center's dish 4 frames on (GTDROP_A k = GTPLUG_A k + 4)."""
    return 135.0 - 18.0 * (t + 4)


def canvas(img, vname):
    return RR.on_canvas(img, vname)


def empty(vname):
    return Image.new('RGBA', RR.CANVAS[RR.base(vname)], (0, 0, 0, 0)), Image.new('L', RR.CANVAS[RR.base(vname)], 0)


SPLIT = int(os.environ.get('GDROP_SPLIT', '2'))      # vertical strips per frame (memory: ~1/SPLIT the peak)
OVL = 40                                               # px each strip runs past its cut (> the 14 px edge fade)


def strips(vname, n=None):
    """[(render window, (x from, x to) kept)]: WIN cut into n vertical strips, each rendered OVL px past its cuts."""
    n = SPLIT if n is None else n
    x0, y0, x1, y1 = RR.WIN[RR.base(vname)]
    cuts = [x0 + (x1 - x0) * k // n for k in range(n + 1)]
    return [((max(x0, cuts[k] - OVL), y0, min(x1, cuts[k + 1] + OVL), y1), (cuts[k], cuts[k + 1])) for k in range(n)]


def render(vname, ss, n=None, **kw):
    """(frame, trim) over WIN on the full canvas, rendered as overlapping vertical strips and joined: the same as one
    pass (the outline, the contact shadow and the renderer's 14 px edge fade reach less than OVL px in from a strip's
    edge, and the shadows come from the whole building's shadow map), at about 1/n the peak memory."""
    W, H = RR.CANVAS[RR.base(vname)]
    img, trim = Image.new('RGBA', (W, H), (0, 0, 0, 0)), Image.new('L', (W, H), 0)
    for w, (a, b) in strips(vname, n):
        pr, v = RR.prep(vname, ss, win=w, **kw)
        f, ft = pr.frame(want_trim=True)
        del pr
        M._PLUG_CACHE.clear()
        box = (a - w[0], 0, b - w[0], w[3] - w[1])
        img.paste(f.crop(box), (a, w[1])); trim.paste(ft.crop(box), (a, w[1]))
    return img, trim


def prog_for(level):
    """the base frames: no dish when healthy (A draws it); the damaged one keeps its dish, standing at A's frame 00."""
    return dict(M.DONE, dish=0.0) if level == 0 else dict(M.DONE)


def states(vname, ss=4, levels=(0, 1), parts=('base', 'lights')):
    """parts: 'base' = building/ (a full pass each), 'lights' = B-lights/ (small windows round the pad)"""
    out = f'{PKG}/{VIEWS[vname]}'
    for level in levels:
        t0 = time.time()
        kw = dict(prog=prog_for(level))
        if level:
            kw['dish_az'] = dish_az(0)
        if 'base' in parts:
            base, btrim = render(vname, ss, level=level, **kw)
            save(base, btrim, f'{out}/building/{NAME}-{level:02d}.png')
            print(vname, 'level', level, 'building', '%.0fs' % (time.time() - t0), flush=True)
        if 'lights' not in parts:
            continue
        # B: only the pad's bars change, so its frames are cut in a window round the pad (the shadows come from the
        # whole building's shadow map either way)
        win = pad_window(vname)
        pb, v = RR.prep(vname, ss, win=win, level=level, **kw)
        wbase = pb.frame()
        for t in range(NB):
            f, ft = pb.frame(want_trim=True, lightsB=t)
            ov = overlay(wbase, f)
            ov, ft = paste_win(ov, win, vname), paste_win(ft, win, vname)
            save(ov, ft, f'{out}/B-lights/{NAME}-lights-{t + NB * level:02d}.png', alpha_from=ov)
        del pb
        M._PLUG_CACHE.clear()
        print(vname, 'level', level, 'B window', win, '%.0fs' % (time.time() - t0), flush=True)


def pad_window(vname, pad=16):
    """a window round the pad (B's four light bars) on the view's canvas: (x0, y0, x1, y1)."""
    v = RR.view(vname, 1, win=(0, 0) + tuple(RR.CANVAS[RR.base(vname)]))
    pd, zt = M.P['pad'], M.P['plug']['deck']['zt']
    xs, ys = [], []
    for u in (-1.0, 1.0):
        for w in (-1.0, 1.0):
            px, py = v.project(np.array([pd['c'][0] + u * pd['half'][0]]), np.array([pd['c'][1] + w * pd['half'][1]]),
                               np.array([zt + 1.0]))
            xs.append(float(np.ravel(px)[0])); ys.append(float(np.ravel(py)[0]))
    W, H = RR.CANVAS[RR.base(vname)]
    return (max(0, int(min(xs)) - pad), max(0, int(min(ys)) - pad), min(W, int(max(xs)) + pad + 1),
            min(H, int(max(ys)) + pad + 1))


def dish_window(vname, pad=(26, 26, 40, 34)):
    """a window round the dish (and its shadow) on the view's canvas: (x0, y0, x1, y1)."""
    v = RR.view(vname, 1, win=(0, 0) + tuple(RR.CANVAS[RR.base(vname)]))      # (canvas coordinates, not WIN's)
    mt = PL.P['mount']
    cx, cy = mt['c'][0] + M.OFF[0], mt['c'][1] + M.OFF[1]
    pts = []
    for du in (-30, 30):
        for dv in (-30, 30):
            for z in (PL.P['block']['z'] - 2, PL.P['block']['z'] + 45):
                pts.append(v.project(np.array([cx + du]), np.array([cy + dv]), np.array([z])))
    xs = [float(p[0][0]) for p in pts]; ys = [float(p[1][0]) for p in pts]
    W, H = RR.CANVAS[RR.base(vname)]
    return (max(0, int(min(xs)) - pad[0]), max(0, int(min(ys)) - pad[1]), min(W, int(max(xs)) + pad[2]),
            min(H, int(max(ys)) + pad[3]))


def paste_win(img, win, vname):
    can = Image.new(img.mode, RR.CANVAS[RR.base(vname)], (0,) * len(img.getbands()))
    can.paste(img, (win[0], win[1]))
    return can


def dish(vname, ss=4):
    out = f'{PKG}/{VIEWS[vname]}/A-dish'
    win = dish_window(vname)
    print(vname, 'dish window', win, flush=True)
    pb, v = RR.prep(vname, ss, win=win, level=0, prog=prog_for(0))
    base = pb.frame()
    del pb
    for t in range(NA):
        t0 = time.time()
        pr, v = RR.prep(vname, ss, win=win, level=0, dish_az=dish_az(t))
        f, ft = pr.frame(want_trim=True)
        del pr
        ov = overlay(base, f)
        ov, ft = paste_win(ov, win, vname), paste_win(ft, win, vname)
        save(ov, ft, f'{out}/{NAME}-dish-{t:02d}.png', alpha_from=ov)
        print(vname, 'dish', t, '%.0fs' % (time.time() - t0), flush=True)
    for t in range(NA, 2 * NA):                      # TS's damaged half is empty: the damaged dish stands still
        e, et = empty(vname)
        save(e, et, f'{out}/{NAME}-dish-{t:02d}.png')


def build(vname, ss=4, frames=None):
    """the dish goes up at its A frame 00 angle and stays there, so nothing jumps when A's loop starts (TS's MK draws
    it at the base sprite's angle, then A starts from its own frame 00).  Frames the same as the one before (a hold)
    are copied, not rendered again."""
    import shutil
    out = f'{PKG}/{VIEWS[vname]}/build-up'
    n = DB.N
    done = {}
    for i in (frames if frames is not None else range(n)):
        t0 = time.time()
        prog = DB.SEQ[i]
        key = repr(sorted(prog.items()))
        dst = f'{out}/{NAME}-build-{i:02d}.png'
        if key in done:
            src = done[key]
            shutil.copy(src, dst); shutil.copy(src[:-4] + '-trim.png', dst[:-4] + '-trim.png')
            print(vname, 'build', i, 'same as', os.path.basename(src), flush=True)
            continue
        f, ft = render(vname, ss, prog=prog, dish_az=dish_az(0))
        save(f, ft, dst)
        done[key] = dst
        print(vname, 'build', i, '%.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    what, vname = sys.argv[1], sys.argv[2]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    fr = [int(a) for a in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
    {'states': lambda: states(vname, ss), 'base': lambda: states(vname, ss, parts=('base',)),
     'lights': lambda: states(vname, ss, parts=('lights',)), 'dish': lambda: dish(vname, ss),
     'build': lambda: build(vname, ss, fr)}[what]()
