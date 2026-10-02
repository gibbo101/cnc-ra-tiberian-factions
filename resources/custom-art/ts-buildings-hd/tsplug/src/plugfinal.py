"""Final frames for the Upgrade Center (12-TSPLUG), both views, into PKG/<view>/...

    python3 plugfinal.py states iso|ra [ss]  building/ 00 healthy, 01 damaged (GTPLUG 0, 1: the dish's box, no dish:
                                            GTPLUG_A draws it); B-lamps/ 20 (GTPLUG_B: 00-09 the tallest antenna's
                                            two lamps over the healthy building, 10-19 over the damaged one, its
                                            antenna bent); C-slot/ 16 (GTPLUG_C: 00-07 the running light down the
                                            ramp's slot, 08-15 empty: the damaged one's light is out)
    python3 plugfinal.py dish iso|ra [ss]    A-dish/ 40 (GTPLUG_A: 00-19 the dish turning once, over the healthy
                                            building; 20-39 over the damaged one)
    python3 plugfinal.py build iso|ra [ss]   build-up/ 24 frames in GTPLUGMK's order (the last = the healthy
                                            building with the dish at its A frame 0, as TS's last MK frame)
    python3 plugfinal.py plugs iso|ra [ss]   plugs/<plug>/ the plug standing in the east socket, on the mod's 128x128
                                            canvas for it (cut from the same window as the mod's TSPODS / TSSEEK /
                                            TSPION): 00-14 healthy (E's eye and F's dish turn; D is still), 15 damaged
                                            (sooted); plus each plug over the building in both sockets (plugs-on/)

Every frame gets a -trim.png (white = house colour, antialiased)."""
import os, sys, time
import numpy as np
from PIL import Image
import plug as M, plugs as PG, plugrender as RR, plugbuild as DB, plugmat as MM
from pfinal import overlay, save, cut128

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-upgrade-center-hd')
NAME = 'upgrade-center'
VIEWS = {'iso': 'ts-angle', 'ra': 'ra-grid'}
NA, NB, NC, NP = 20, 10, 8, 15
PLUGS = {'D': 'drop-pod-node', 'E': 'seeker-control', 'F': 'ion-cannon-uplink'}
# the mod's 128x128 plug frames on the building's TS-angle canvas (top-left), by matching TSPODS / TSSEEK / TSPION 0000
# against TS's GTPLUG_D / E / F frame 0 scaled into the mod's frame (IoU 0.984 / 0.994 / 0.989)
MOD_WIN = {'D': (101, 147), 'E': (104, 142), 'F': (104, 118)}


def dish_az(t):
    """GTPLUG_A frame t: the dish turns once in 20 frames (facing south-west at 0, the camera at 5)."""
    return 135.0 - 18.0 * t


def canvas(img, vname):
    return RR.on_canvas(img, vname)


def empty(vname):
    return Image.new('RGBA', RR.canvas_of(vname), (0, 0, 0, 0)), Image.new('L', RR.canvas_of(vname), 0)


def no_dish():
    return dict(M.DONE, dish=0.0)


def states(vname, ss=4, levels=(0, 1)):
    out = f'{PKG}/{VIEWS[vname]}'
    for level in levels:
        t0 = time.time()
        pr, v = RR.prep(vname, ss, level=level, prog=no_dish())
        base, btrim = pr.frame(want_trim=True)
        base, btrim = canvas(base, vname), canvas(btrim, vname)
        save(base, btrim, f'{out}/building/{NAME}-{level:02d}.png')
        for t in range(NB):
            f, ft = pr.frame(want_trim=True, ant_t=t)
            f, ft = canvas(f, vname), canvas(ft, vname)
            ov = overlay(base, f)
            save(ov, ft, f'{out}/B-lamps/{NAME}-lamps-{t + NB * level:02d}.png', alpha_from=ov)
        for t in range(NC):
            i = t + NC * level
            if level == 0:
                f, ft = pr.frame(want_trim=True, slot_t=t)
                f, ft = canvas(f, vname), canvas(ft, vname)
                ov = overlay(base, f)
                save(ov, ft, f'{out}/C-slot/{NAME}-slot-{i:02d}.png', alpha_from=ov)
            else:
                e, et = empty(vname)
                save(e, et, f'{out}/C-slot/{NAME}-slot-{i:02d}.png')
        del pr
        print(vname, 'level', level, '%.0fs' % (time.time() - t0), flush=True)


def dish_window(vname, pad=(26, 26, 40, 34)):
    """a window round the dish (and its shadow) on the view's canvas: (x0, y0, x1, y1)."""
    v = RR.view(vname, 1)
    mt = M.P['mount']
    cx, cy = mt['c']
    lay = RR.LAYOUT[RR.base(vname)]
    pts = []
    for du in (-30, 30):
        for dv in (-30, 30):
            for z in (M.P['block']['z'] - 2, M.P['block']['z'] + 45):
                X, Y = M.to_world(cx + du, cy + dv, lay)
                pts.append(v.project(np.array([X]), np.array([Y]), np.array([z])))
    xs = [float(p[0][0]) for p in pts]; ys = [float(p[1][0]) for p in pts]
    W, H = RR.canvas_of(vname)
    return (max(0, int(min(xs)) - pad[0]), max(0, int(min(ys)) - pad[1]), min(W, int(max(xs)) + pad[2]),
            min(H, int(max(ys)) + pad[3]))


def paste_win(img, win, vname):
    can = Image.new(img.mode, RR.canvas_of(vname), (0,) * len(img.getbands()))
    can.paste(img, (win[0], win[1]))
    return can


def dish(vname, ss=4, levels=(0, 1)):
    out = f'{PKG}/{VIEWS[vname]}/A-dish'
    win = dish_window(vname)
    print(vname, 'dish window', win, flush=True)
    for level in levels:
        pb, v = RR.prep(vname, ss, win=win, level=level, prog=no_dish())
        base = pb.frame()
        del pb
        for t in range(NA):
            t0 = time.time()
            pr, v = RR.prep(vname, ss, win=win, level=level, dish_az=dish_az(t))
            f, ft = pr.frame(want_trim=True)
            del pr
            ov = overlay(base, f)
            ov, ft = paste_win(ov, win, vname), paste_win(ft, win, vname)
            save(ov, ft, f'{out}/{NAME}-dish-{t + NA * level:02d}.png', alpha_from=ov)
            print(vname, 'dish', level, t, '%.0fs' % (time.time() - t0), flush=True)


def build(vname, ss=4, frames=None):
    out = f'{PKG}/{VIEWS[vname]}/build-up'
    n = DB.N
    for i in (frames if frames is not None else range(n)):
        t0 = time.time()
        prog = DB.SEQ[i]
        pr, v = RR.prep(vname, ss, prog=prog, **({'dish_az': dish_az(0)} if i == n - 1 else {}))
        f, ft = pr.frame(want_trim=True)
        del pr
        save(canvas(f, vname), canvas(ft, vname), f'{out}/{NAME}-build-{i:02d}.png')
        print(vname, 'build', i, '%.0fs' % (time.time() - t0), flush=True)


def plug_window(vname, kind):
    """the plug's 128x128 window on the view's canvas: the mod's own on the TS angle; on the RA grid the same window
    moved with the east socket, so the socket's centre sits on the same spot of the 128 canvas."""
    cx, cy = M.P['sockets']['c'][1]
    z = M.P['sockets']['plate']
    iso = RR.view('iso', 1)
    ix, iy = iso.project(np.array([cx]), np.array([cy]), np.array([z]))
    wx, wy = MOD_WIN[kind]
    at = (ix[0] - wx, iy[0] - wy)
    if RR.base(vname) == 'iso':
        return (wx, wy), at
    v = RR.view(vname, 1)
    X, Y = M.to_world(cx, cy, RR.LAYOUT['ra'])
    sx, sy = v.project(np.array([X]), np.array([Y]), np.array([z]))
    return (int(round(sx[0] - at[0])), int(round(sy[0] - at[1]))), at


def plug_comps():
    return sorted(PG.PG_ALL)


def plugs(vname, ss=4, kinds=('D', 'E', 'F')):
    out = f'{PKG}/{VIEWS[vname]}'
    for kind in kinds:
        name = PLUGS[kind]
        org, at = plug_window(vname, kind)
        print(vname, kind, '128 window at', org, 'socket centre on it %.1f, %.1f' % at, flush=True)
        os.makedirs(f'{out}/plugs/{name}', exist_ok=True)
        open(f'{out}/plugs/{name}/window.txt', 'w').write('%d %d\n' % org)
        frames = range(NP) if kind != 'D' else (0,)
        for level in (0, 1):
            for t in (frames if level == 0 else (0,)):
                t0 = time.time()
                win = (org[0], org[1], org[0] + 128, org[1] + 128)
                pr, v = RR.prep(vname, ss, win=win, level=level, prog=no_dish(), plugs=(None, kind), plug_t=t)
                r = pr.r
                own = np.isin(r.comp, plug_comps()) & r.hitmask
                piece, ptrim = pr.frame(want_trim=True, only=own, ground=False)
                del pr
                i = t if level == 0 else NP
                save(piece, ptrim, f'{out}/plugs/{name}/{name}-{i:02d}.png', alpha_from=piece)
                if kind == 'D' and level == 0:          # D is still: its 15 frames are the same picture
                    for k in range(1, NP):
                        save(piece, ptrim, f'{out}/plugs/{name}/{name}-{k:02d}.png', alpha_from=piece)
                print(vname, kind, level, t, '%.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    what, vname = sys.argv[1], sys.argv[2]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    if what == 'states':
        states(vname, ss)
    elif what == 'dish':
        dish(vname, ss)
    elif what == 'plugs':
        plugs(vname, ss, tuple(sys.argv[4:]) or ('D', 'E', 'F'))
    else:
        build(vname, ss, [int(a) for a in sys.argv[4:]] or None)
