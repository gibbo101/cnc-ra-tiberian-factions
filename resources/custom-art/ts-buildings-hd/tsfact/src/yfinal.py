"""Final frames for the Construction Yard (01-TSFACT), both views, into PKG/<view>/...

    python3 yfinal.py states iso|ra [ss]        the building (00 healthy, 01 damaged) and the A, B, C
                                                overlays for both states, plus the baked 30-frame loops
    python3 yfinal.py prod iso|ra [ss] [i,j..]  the D overlay (producing), 20 frames
    python3 yfinal.py build iso|ra [ss] [i,j..] the build-up, 32 frames (the last is the healthy frame)

Every frame gets a -trim.png (white = house colour, antialiased), like the Component Tower's.
Overlays are the pixels that frame changes against the building frame of the same state (drawn on top of it).
"""
import os, sys, time
import numpy as np
from PIL import Image
import yanim as A, yrender as R, ymat as M, ybuild as B, yard as Y

PKG = '/home/claude/work/out/ts-gdi-construction-yard-hd'
NAME = 'construction-yard'
VIEWS = {'iso': 'ts-angle', 'ra': 'ra-grid', 'ra25': 'ra-grid-25'}


def view_of(name, ss):
    if name == 'ra25':
        return R.ra_turned_view(ss)
    return R.iso_view(ss) if name == 'iso' else R.ra_view(52, ss)


def trim_of(pr, fan_angle=0.0, fan_on=(True, True, True)):
    """the house-colour mask of what the Prep's geometry shows (albedo green), at canvas resolution."""
    r = pr.r
    alb, _, _ = M.materials(r, fan_angle=fan_angle, occ=pr.occ, fan_on=fan_on)
    if pr.level:
        alb = A.D.mats(r, alb, pr.level)
    tm = M.trim_mask(r, alb).astype(np.float32)
    ss = pr.view.ss
    H_, W_ = tm.shape[0] // ss, tm.shape[1] // ss
    m = tm.reshape(H_, ss, W_, ss).mean(axis=(1, 3))
    return m


def save(img, trim, path, alpha_from=None):
    """frame + its -trim.png; for an overlay the trim is cut to the overlay's own pixels."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    t = trim
    if alpha_from is not None:
        t = t * (np.array(alpha_from)[..., 3] > 0)
    Image.fromarray((np.clip(t, 0, 1) * 255).round().astype(np.uint8), 'L').save(path[:-4] + '-trim.png')


def states(vname, ss=4):
    out = f'{PKG}/{VIEWS[vname]}'
    view = view_of(vname, ss)
    loops = {}
    for level in (0, 1):
        t0 = time.time()
        pr = A.Prep(view, level=level)
        trim = trim_of(pr)
        base = pr.frame()
        save(base, trim, f'{out}/yard/{NAME}-{level:02d}.png')
        fan_on = (True, True, True) if level == 0 else (True, False, False)
        lamps = A.C_HEALTHY if level == 0 else A.C_DAMAGED
        ov = {'A': [], 'B': [], 'C': []}
        for t in range(A.A_N):
            f = pr.frame(fan_angle=t * A.FAN_STEP, fan_on=fan_on)
            ov['A'].append(A.overlay(base, f))
        for t in range(10):
            f = pr.frame(beacon=A.B_ANGLE0 + A.B_STEP * t, run=t)
            ov['B'].append(A.overlay(base, f))
        for t in range(15):
            f = pr.frame(lamp_levels=lamps[t])
            ov['C'].append(A.overlay(base, f))
        off = {'A': 10, 'B': 10, 'C': 15}
        for k, sub in (('A', 'A-fans'), ('B', 'B-door-lamp'), ('C', 'C-roof-lamps')):
            for t, o in enumerate(ov[k]):
                i = t + level * off[k]
                save(o, trim, f'{out}/{sub}/{NAME}-{sub[2:]}-{i:02d}.png', alpha_from=o)
        # the idle loop baked into the building frames (30 = the fans' 10 x the lamps' 15)
        for t in range(30):
            im = base.copy()
            for o in (ov['A'][t % 10], ov['B'][t % 10], ov['C'][t % 15]):
                im.alpha_composite(o)
            loops[level * 30 + t] = im
            save(im, trim, f'{out}/loop/{NAME}-loop-{level * 30 + t:02d}.png')
        print(vname, 'level', level, 'done %.0fs' % (time.time() - t0), flush=True)


def prod(vname, ss=4, frames=None):
    out = f'{PKG}/{VIEWS[vname]}'
    view = view_of(vname, ss)
    base = Image.open(f'{out}/yard/{NAME}-00.png')
    for t in (frames if frames is not None else range(20)):
        t0 = time.time()
        st = A.d_state(t)
        pr = A.Prep(view, dstate=st)
        f = pr.frame(light=st['light'])
        o = A.overlay(base, f)
        save(o, trim_of(pr), f'{out}/D-producing/{NAME}-producing-{t:02d}.png', alpha_from=o)
        print(vname, 'D', t, '%.0fs' % (time.time() - t0), flush=True)


# where the deploying MCV's centre stands on each view's canvas: the middle cell of the plot's
# south row (the unit's cell; the yard's origin is the cell north-west of it)
DEPLOY_PX = {'iso': (192.0, 192.0), 'ra': (192.0, 52.0 + 192.0), 'ra25': (248.0, 48.0 + 192.0)}


def ground_at(view, sx, sy):
    """the world point on the ground under canvas pixel (sx, sy)."""
    pr = (sx - view.ox) / view.ppu
    pt = (sy - view.oy) / (view.ppu * view.sE)
    return pr * view.R[0] + pt * view.T[0], pr * view.R[1] + pt * view.T[1]


def build(vname, ss=4, frames=None):
    out = f'{PKG}/{VIEWS[vname]}'
    view = view_of(vname, ss)
    Y.MCV_FROM = ground_at(view, *DEPLOY_PX[vname])
    # the unit faces south-west on screen when it deploys: that direction in the world, as a turn
    # from the parked MCV's heading (cab west)
    sw = np.array([view.T[0] - view.R[0], view.T[1] - view.R[1]])
    Y.MCV_TURN = float(np.arctan2(-sw[1], -sw[0]))
    print(vname, 'MCV deploys at world (%.1f, %.1f), turned %.1f deg' % (Y.MCV_FROM + (np.rad2deg(Y.MCV_TURN),)), flush=True)
    last = len(B.SEQ) - 1
    for i in (frames if frames is not None else range(len(B.SEQ))):
        t0 = time.time()
        path = f'{out}/build-up/{NAME}-build-{i:02d}.png'
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if i == last:
            # the finished building: exactly the healthy frame
            for suf in ('', '-trim'):
                Image.open(f'{out}/yard/{NAME}-00{suf}.png').save(path[:-4] + suf + '.png')
        else:
            pr = A.Prep(view, prog=B.SEQ[i])
            save(pr.frame(), trim_of(pr), path)
        print(vname, 'build', i, '%.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    what, vname = sys.argv[1], sys.argv[2]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    fr = [int(a) for a in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
    {'states': lambda: states(vname, ss), 'prod': lambda: prod(vname, ss, fr),
     'build': lambda: build(vname, ss, fr)}[what]()
