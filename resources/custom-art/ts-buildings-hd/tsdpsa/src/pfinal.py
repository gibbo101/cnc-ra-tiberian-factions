"""Final frames for the Power Plant (02-TSPOWR) and its power pods, both views, into PKG/<view>/...

    python3 pfinal.py states iso|ra [ss]      the plant with its east pod (00 healthy, 01 damaged), the tower
                                              lights (A), the pods (B: east, middle, west, cut in fill order)
                                              and the 72-frame loop (1, 2, 3 pods x healthy, damaged)
    python3 pfinal.py piece iso|ra [ss]       the pod on its own 128x128 canvas (like the mod's TSTURB)
    python3 pfinal.py build iso|ra [ss]       the build-up, 24 frames (the last is the healthy plant)

Every frame gets a -trim.png (white = house colour, antialiased).  An overlay holds the pixels its frame changes
against the frame it is drawn over (the plant of the same state, or the plant with the pods before it)."""
import os, sys, time
import numpy as np
from PIL import Image
from scipy import ndimage
import prender as PR, powr as PW, pmat as PM, panim as PA, pbuild as PB

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-gdi-power-plant-hd')
NAME = 'power-plant'
VIEWS = {'iso': 'ts-angle', 'ra': 'ra-grid'}


def view_of(name, ss):
    return PR.iso_view(ss) if name == 'iso' else PR.ra_view(8, ss)


def overlay(base, frame, thr=3):
    """the pixels `frame` changes against `base`, as an overlay that gives `frame` back when it is drawn over
    `base` (normal "over" blending, straight alpha).  Solid pixels are copied; where the frame is see-through
    (the outline, shadow on the ground) the overlay's alpha and colour are solved so base + overlay = frame."""
    a = np.array(base).astype(np.float64) / 255.0
    b = np.array(frame).astype(np.float64) / 255.0
    diff = np.abs(a - b).max(axis=2) * 255.0 > thr
    diff = ndimage.binary_dilation(diff, iterations=1)
    ab, af = a[..., 3], b[..., 3]
    solid = af >= 0.999
    grow = ~solid & (af > ab + 1e-3)
    # see-through pixels that don't gain alpha stay out: drawn over the base they could only darken it (the 1 px
    # grow round the changed pixels picks up unchanged shadow, which must not be drawn twice)
    ao = np.where(solid, 1.0, np.where(grow, (af - ab) / np.maximum(1.0 - ab, 1e-6), 0.0))
    num = b[..., :3] * af[..., None] - a[..., :3] * (ab * (1.0 - ao))[..., None]
    co = np.where(grow[..., None], num / np.maximum(ao, 1e-6)[..., None], b[..., :3])
    out = np.zeros_like(b)
    out[..., :3] = np.clip(co, 0, 1)
    out[..., 3] = np.clip(ao, 0, 1)
    out[~diff] = 0
    return Image.fromarray((out * 255.0).round().astype(np.uint8), 'RGBA')


def save(img, trim, path, alpha_from=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    t = np.array(trim).astype(np.float32) / 255.0
    if alpha_from is not None:
        t = t * (np.array(alpha_from)[..., 3] > 0)
    Image.fromarray((np.clip(t, 0, 1) * 255).round().astype(np.uint8), 'L').save(path[:-4] + '-trim.png')


POD_SETS = ((0,), (0, 1), (0, 1, 2))      # the plant fills east to west: its own east pod, + the middle, + the west
POD_NAMES = ('east', 'middle', 'west')


def states(vname, ss=4):
    """straight renders, per state (healthy, damaged) and pod count (1, 2, 3):
      plant/    the plant with its east pod (turbine at rest): 00 healthy, 01 damaged
      A-lights/ the tower's lights, cut against the plant
      B-pods/   east: the east pod turning, cut against the plant; middle: the middle pod, cut against the plant
                with the east pod at the same frame; west: the west pod, cut against the plant with east + middle
      loop/     72 frames, 1, 2, 3 pods x (12 healthy + 12 damaged), lights and pods together"""
    out = f'{PKG}/{VIEWS[vname]}'
    view = view_of(vname, ss)
    for level in (0, 1):
        prev = None
        for n, pods_ in enumerate(POD_SETS):
            t0 = time.time()
            pr = PR.Prep(view, level=level, turbines=pods_)
            if n == 0:
                base, trim = pr.frame(want_trim=True)
                save(base, trim, f'{out}/plant/{NAME}-{level:02d}.png')
                for t in range(PA.A_N):
                    f, ft = pr.frame(lights=PA.light_levels(t), lights_ok=PA.lights_ok(level), want_trim=True)
                    o = overlay(base, f)
                    save(o, ft, f'{out}/A-lights/{NAME}-lights-{t + level * PA.A_N:02d}.png', alpha_from=o)
            cur = []
            nm = POD_NAMES[n]
            for t in range(PA.A_N):
                i = t + level * PA.A_N
                f, ft = pr.frame(turb_angle=t * PA.TURB_STEP, want_trim=True)
                o = overlay(base if n == 0 else prev[t], f)
                save(o, ft, f'{out}/B-pods/{nm}/{NAME}-pod-{nm}-{i:02d}.png', alpha_from=o)
                cur.append(f)
                lf, lt = pr.frame(turb_angle=t * PA.TURB_STEP, lights=PA.light_levels(t), lights_ok=PA.lights_ok(level),
                                  want_trim=True)
                save(lf, lt, f'{out}/loop/{NAME}-loop-{(2 * n + level) * PA.A_N + t:02d}.png')
            prev = cur
            del pr
            print(vname, 'level', level, 'pods', len(pods_), '%.0fs' % (time.time() - t0), flush=True)


def pod_origin(view):
    """top-left of the 128x128 pod canvas on the plant's canvas, for the pod in slot 1 (east).  TS angle: the mod's
    TSTURB frame matches the east pod on its TSPOWR frame at (147, 97), so ours is cut from the same window.  RA grid:
    the same window moved with the socket, so the socket's centre sits on the same spot of the 128 canvas."""
    p = PW.P
    cx, cy = p['slots'][0]
    iso = PR.iso_view(1)
    ix, iy = iso.project(np.array([cx]), np.array([cy]), np.array([p['sock_z']]))
    at = (ix[0] - 147.0, iy[0] - 97.0)                     # the socket's centre on the 128 canvas
    sx, sy = view.project(np.array([cx]), np.array([cy]), np.array([p['sock_z']]))
    return int(round(sx[0] - at[0])), int(round(sy[0] - at[1])), at


def cut128(img, origin, mode):
    ox, oy = origin
    src = np.array(img)
    out = np.zeros((128, 128) + src.shape[2:], src.dtype)
    x0, y0 = max(0, ox), max(0, oy)
    x1, y1 = min(src.shape[1], ox + 128), min(src.shape[0], oy + 128)
    out[y0 - oy:y1 - oy, x0 - ox:x1 - ox] = src[y0:y1, x0:x1]
    return Image.fromarray(out, mode)


TURB = [PW.THOUSE, PW.TBAND, PW.TCAP]


def pod_piece(vname, ss=4, levels=(0, 1)):
    """the pod on its own 128x128 canvas, like the mod's TSTURB: the pod in slot 1 with its socket's ring and
    plate, lifted off the plant (no shadow of its own).  The damaged pod keeps an intact ring and plate (the
    plant's damage there is the plant's): its turbine comes from the damaged render, the rest from the healthy."""
    out = f'{PKG}/{VIEWS[vname]}'
    view = view_of(vname, ss)
    p = PW.P
    org = pod_origin(view)
    print(vname, 'pod canvas at', org[:2], 'socket centre on it %.1f, %.1f' % org[2], flush=True)
    cx, cy = p['slots'][0]
    ph = PR.Prep(view, level=0, turbines=(0,))
    rh = ph.r
    own = np.isin(rh.comp, TURB + [PW.RING, PW.PLATE]) & rh.hitmask & \
        (np.hypot(rh.x - cx, rh.y - cy) <= p['ring_r'] + p['ring_w'] / 2 + 0.5)
    turb_h = np.isin(rh.comp, TURB) & rh.hitmask
    for level in levels:
        t0 = time.time()
        pd = PR.Prep(view, level=1, turbines=(0,)) if level else None
        if pd is not None:
            use_d = turb_h & np.isin(pd.r.comp, TURB) & pd.r.hitmask
            print(vname, 'damaged pod: turbine px from the damaged render', int(use_d.sum()), 'of', int(turb_h.sum()), flush=True)
        for t in range(PA.A_N):
            i = t + level * PA.A_N
            col, tm = ph.shade(turb_angle=t * PA.TURB_STEP)
            if pd is not None:
                cd, td = pd.shade(turb_angle=t * PA.TURB_STEP)
                col = np.where(use_d[..., None], cd, col)
                tm = np.where(use_d, td, tm)
            g, gt = ph.frame(want_trim=True, only=own, ground=False, shaded=(col, tm))
            piece, ptrim = cut128(g, org[:2], 'RGBA'), cut128(gt, org[:2], 'L')
            save(piece, ptrim, f'{out}/pod-128/turning/power-pod-turn-{i:02d}.png', alpha_from=piece)
            if t == 0:
                save(piece, ptrim, f'{out}/pod-128/power-pod-{level:02d}.png', alpha_from=piece)
        print(vname, 'pod piece level', level, '%.0fs' % (time.time() - t0), flush=True)


def build(vname, ss=4, frames=None):
    out = f'{PKG}/{VIEWS[vname]}'
    view = view_of(vname, ss)
    last = len(PB.SEQ) - 1
    for i in (frames if frames is not None else range(len(PB.SEQ))):
        t0 = time.time()
        path = f'{out}/build-up/{NAME}-build-{i:02d}.png'
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if i == last:
            for suf in ('', '-trim'):
                Image.open(f'{out}/plant/{NAME}-00{suf}.png').save(path[:-4] + suf + '.png')
        else:
            pr = PR.Prep(view, prog=PB.SEQ[i])
            img, trim = pr.frame(want_trim=True)
            save(img, trim, path)
        print(vname, 'build', i, '%.0fs' % (time.time() - t0), flush=True)


if __name__ == '__main__':
    what, vname = sys.argv[1], sys.argv[2]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    fr = [int(a) for a in sys.argv[4].split(',')] if len(sys.argv) > 4 else None
    {'states': lambda: states(vname, ss),
     'piece': lambda: pod_piece(vname, ss, tuple(fr) if fr else (0, 1)),
     'build': lambda: build(vname, ss, fr)}[what]()
