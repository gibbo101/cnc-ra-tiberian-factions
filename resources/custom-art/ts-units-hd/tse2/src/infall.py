"""
infall.py - every frame of an infantry unit in HD (E1: 292), from the fitted poses:

  0-7 standing (UNIT_stand_frames.json), 8-55 walk (UNIT_walk_frames.json: the run as one smooth loop), 56-70 idle 1,
  71-85 idle 2 (85, unused, as 84), 86-133 crawl (one smooth loop), 134-148 death 1, 149-163 death 2, 164-211 fire and
  212-259 fire prone (one pose a facing; TS's muzzle flash on TS's flash frames), 260-275 lie down, 276-291 get up
  (lie down backwards, as TS's are)

The muzzle flash: TS's flash pixels for that frame (infx), moved with the muzzle (the HD muzzle against the fitted
soldier's muzzle in TS's camera), hidden where the soldier is in front of it.  Blood: TS's red pixels for that frame,
in TS's red, each drawn on the ground it covers in TS's camera (a pool stays put as the body falls on it).

    python3 infall.py UNIT shape.json OUTDIR [FRAMES]
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
import rc
import inf as I
import inffit as F
import infrender as R
import infseq as SQ
import infx as X

# the mod's placement of TS's frames (R.K, R.DX, R.DY) is read when used: infunit.use switches it per unit


def pose_table(unit, base):
    """frame -> (Q, facing) for every frame of the layout."""
    tab = {}
    def put(path, frames=None):
        if not os.path.exists(path):
            return
        js = json.load(open(path))
        for k, v in js.items():
            if 'facing' in v:
                tab[int(k)] = (dict(base, **v['Q']), int(v['facing']))
    put('%s_stand_frames.json' % unit)
    for seq in ('walk', 'idle1', 'idle2', 'crawl', 'death1', 'death2', 'fire', 'prone_fire', 'lie_down', 'get_up',
                'fly', 'fire_fly', 'tumble', 'heal'):
        put('%s_%s_frames.json' % (unit, seq))
    if 84 in tab and 85 not in tab:
        tab[85] = tab[84]
    if unit == 'jj':
        # hovering: TS's standing frames with the jets lit (each facing's 6 frames its standing pose)
        for f in range(8):
            if f in tab:
                for st in range(6):
                    tab.setdefault(340 + 6 * f + st, tab[f])
    return tab


def ts_cam(js):
    return rc.Cam((0, -1), 30.0, 1.0, (js['ax'], js['y0']))


def anchor_shift(S, Q, f, js, point):
    """where a point of the soldier lands in HD against where it lands in TS's camera mapped onto the canvas."""
    K, DX, DY = R.K, R.DX, R.DY
    parts, dz = I.grounded(S, Q, I.facing_angle(f))
    p = np.asarray(point(S, Q, I.facing_angle(f)), float) + np.array([0, 0, dz])
    hx, hy = R.camera((js['ax'], js['y0'])).project(p)
    tx, ty = ts_cam(js).project(p)
    return (float(hx - (tx * K + DX)), float(hy - (ty * K + DY))), p


def chest_point(S, Q, th):
    P = I.Pose(S, Q, th)
    return P.chest[0]


def in_front(parts, js, p, size, margin=0.6):
    """canvas mask (0..1, 1 = the soldier is between the camera and depth of point p)."""
    cam = R.camera((js['ax'], js['y0']))
    W, H = size
    ss = 2
    xs = (np.arange(W * ss) + 0.5) / ss; ys = (np.arange(H * ss) + 0.5) / ss
    SX, SY = np.meshgrid(xs, ys)
    O = cam.rays(SX.ravel(), SY.ravel(), zstart=80.0)
    t, who, _ = rc.cast(parts, O, cam.D, want_normals=False)
    hit = np.isfinite(t)
    dp = (np.asarray(p) - O) @ cam.D                     # the point's distance along each ray
    front = (hit & (t < dp - margin)).reshape(SX.shape).astype(np.float32)
    return front.reshape(H, ss, W, ss).mean(axis=(1, 3))


def ts_ground(js, x, y):
    """the ground point TS's camera sees at its frame pixel (x, y)."""
    c = ts_cam(js)
    pr = (x - c.ox) / c.ppu
    pt = (y - c.oy) / (c.ppu * c.sE)
    return np.array([pr * c.R[0] + pt * c.T[0], pr * c.R[1] + pt * c.T[1], 0.0])


def blood(img, pix, js, size, ss=4):
    """TS's red pixels in TS's red, each taken as the ground it covers in TS's camera and drawn where HD's camera sees
    that ground (so a pool stays put under the body), smooth-edged."""
    W, H = size
    K = R.K
    cam = R.camera((js['ax'], js['y0']))
    f = np.zeros((H * ss, W * ss), np.float32)
    for x, y in pix:
        corners = [cam.project(ts_ground(js, x + u, y + v)) for u, v in ((0, 0), (1, 1))]
        (x0, y0), (x1, y1) = corners
        x0, x1 = int(round(x0 * ss)), int(round(x1 * ss)); y0, y1 = int(round(y0 * ss)), int(round(y1 * ss))
        f[max(y0, 0):max(y1, 0), max(x0, 0):max(x1, 0)] = 1.0
    f = ndimage.gaussian_filter(f, 0.35 * K * ss)
    a = np.clip((f - 0.25) / 0.5, 0, 1)
    a = a.reshape(H, ss, W, ss).mean(axis=(1, 3))
    base = np.asarray(img).astype(np.float32)
    out = base.copy()
    red = np.array([255.0, 0.0, 0.0])
    out[..., :3] = base[..., :3] * (1 - a[..., None]) + red * a[..., None]
    out[..., 3] = np.maximum(base[..., 3], a * 255)
    return Image.fromarray(np.clip(np.round(out), 0, 255).astype(np.uint8), 'RGBA'), a


# frames drawn in the air from here on (the Jumpjet's flight: the game lifts the frame and draws his shadow from it):
# no baked shadow, the jet flames at his nozzles
FLIGHT = {'jj': 292}
# parts that carry TS's pure red as a painted mark (the Medic's crosses): red there is not blood
DECAL_RED = {'medic': (I.CROSS, I.MEDKIT, I.CHEST, I.VEST)}
# frames whose reds are a muzzle flash's tips, not blood (the Jumpjet's fire, on the ground and in the air; the Ghost
# Stalker's flash has a few dark red pixels at its edge)
FIRE_RED = {'jj': ((164, 260), (388, 436)), 'ghost': ((164, 260),)}


def flash_groups(unit, S, Q, f, js, k, fl):
    """TS's flash pixels by what makes them: {anchor function: pixels}.  The Jumpjet in the air: his jet flames at the
    nozzles; firing in the air, the pixels nearer his muzzle than his nozzles (in TS's view) are the muzzle flash."""
    if not (unit in FLIGHT and k >= FLIGHT[unit]):
        return {I.muzzle: fl}
    if not (388 <= k < 436):
        return {I.nozzle: fl}
    th = I.facing_angle(f)
    dz = I.grounded(S, Q, th)[1]
    cam = ts_cam(js)
    m = np.array(cam.project(np.asarray(I.muzzle(S, Q, th)) + np.array([0, 0, dz])), float)
    n = np.array(cam.project(np.asarray(I.nozzle(S, Q, th)) + np.array([0, 0, dz])), float)
    out = {I.muzzle: [], I.nozzle: []}
    for x, y, w in fl:
        p = np.array([x + 0.5, y + 0.5])
        out[I.muzzle if np.linalg.norm(p - m) < np.linalg.norm(p - n) else I.nozzle].append((x, y, w))
    return {a: v for a, v in out.items() if v}


def muzzle_cluster(unit, S, Q, f, js, a, fl):
    """TS's flash pixels in the flash itself: the cluster of them nearest the muzzle.  TS also lights the Jumpjet's
    body with the flash (yellow and red pixels down his front and legs); drawn as flash those became flames on his legs."""
    from scipy import ndimage as nd
    if not fl:
        return fl
    th = I.facing_angle(f)
    dz = I.grounded(S, Q, th)[1]
    m = np.array(ts_cam(js).project(np.asarray(I.muzzle(S, Q, th)) + np.array([0, 0, dz])), float)
    M = np.zeros(a.shape[:2], bool)
    for x, y, w in fl:
        M[y, x] = True
    lab, n = nd.label(nd.binary_dilation(M, structure=np.ones((3, 3))), structure=np.ones((3, 3)))
    if n <= 1:
        return fl
    best = min(range(1, n + 1), key=lambda i: min(np.hypot(x + 0.5 - m[0], y + 0.5 - m[1])
                                                   for x, y, w in fl if lab[y, x] == i))
    return [(x, y, w) for x, y, w in fl if lab[y, x] == best]


# the deaths' shadows: drawn in under him and faded as TS's own frames have them (deathshadow.py: TS's shadow
# shrinks as he falls and is all but gone once he lies on the ground - Luke: "on the og's the shadow disappears as the
# unit falls. On ours they still look like they're floating in midair because of their shadows"); {frame: [length,
# strength]}
DEATH_SHADOW = {}


def death_shadow(unit, S, js, tab):
    """the deaths' shadow schedule from the final death poses (UNIT_shadow_w.json, made afresh when a death's poses
    are newer)."""
    import deathshadow
    path = '%s_shadow_w.json' % unit
    src = [p for p in ('%s_death1_frames.json' % unit, '%s_death2_frames.json' % unit) if os.path.exists(p)]
    if not src:
        return {}
    if os.path.exists(path) and os.path.getmtime(path) >= max(os.path.getmtime(p) for p in src):
        return {int(k): v for k, v in json.load(open(path)).items()}
    sw = deathshadow.schedule(unit, S, js, tab, log=lambda m: print('shadow', m, flush=True))
    json.dump(sw, open(path, 'w'), indent=1)
    return {int(k): v for k, v in sw.items()}


_EAB = {}


def ea_blood(unit, k):
    """the blood of a death fitted to EA's own HD death (wrig/easeq.py records which EA frame each of ours follows): EA's
    pool where EA's lands, moved onto our canvas - Luke: "follow ea" (TS's red, read off TS's tiny frames, no longer
    lines up with a body falling EA's way).  None for frames that follow TS."""
    if unit not in _EAB:
        _EAB[unit] = {}
        for seq in ('death1', 'death2'):
            p = '%s_%s_frames.json' % (unit, seq)
            if os.path.exists(p):
                d = json.load(open(p))
                if 'ea_code' in d:
                    last = max(v['ea_frame'] for kk, v in d.items() if kk.isdigit() and 'ea_frame' in v)
                    for kk, v in d.items():
                        if kk.isdigit() and 'ea_frame' in v:
                            _EAB[unit][int(kk)] = (d['ea_code'], v['ea_frame'], tuple(d.get('ea_shift', (0, 0))), last)
    if k not in _EAB[unit]:
        return None
    code, e, (dx, dy), last = _EAB[unit][k]
    import ealib
    ea = ealib.EA(code, unit, None, None)

    def reds(a):
        a = a.astype(np.float32)
        r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
        return (al > 40) & (r > 70) & (g < 0.45 * r) & (b < 0.45 * r) & (r - g > 50)
    # only the blood that lies on the ground: what EA's pool at the end of the death covers (the spray EA draws in the
    # air as he is hit - Luke: "blood seems suspended in mid air" - left out)
    m = reds(ea.full(e)) & ndimage.binary_dilation(reds(ea.full(last)), iterations=2)
    m = np.roll(np.roll(m, -dy, 0), -dx, 1).astype(np.float32)
    return np.clip(ndimage.gaussian_filter(m, 0.6) * 1.4, 0, 1)


def draw_ea_blood(img, a):
    """the pool under the soldier: drawn where he isn't (his outline keeps his own pixels), in TS's blood red."""
    base = np.asarray(img).astype(np.float32)
    a = a * (base[..., 3] < 200)
    out = base.copy()
    red = np.array([255.0, 0.0, 0.0])
    out[..., :3] = base[..., :3] * (1 - a[..., None]) + red * a[..., None]
    out[..., 3] = np.maximum(base[..., 3], a * 255)
    return Image.fromarray(np.clip(np.round(out), 0, 255).astype(np.uint8), 'RGBA'), a


def render_frame(unit, S, js, k, Q, f, ss=4):
    K, DX, DY = R.K, R.DX, R.DY
    parts, dz = I.grounded(S, Q, I.facing_angle(f))
    air = unit in FLIGHT and k >= FLIGHT[unit]
    sl, sw = DEATH_SHADOW.get(k, (None, 1.0))
    img, trim = R.render(parts, ss=ss, ground=(js['ax'], js['y0']), shadow=not air, shadow_len=sl, shadow_w=sw)
    a = F.ts_frame(unit, k)
    red_flash = any(lo <= k < hi for lo, hi in FIRE_RED.get(unit, ()))
    fl = X.ts_flash(a, X.REDS if red_flash else None)
    if fl and 164 <= k < 260:
        fl = muzzle_cluster(unit, S, Q, f, js, a, fl)
    cover = np.zeros(img.size[::-1], np.float32)          # how much the effects cover each pixel
    for anchor, pix in (flash_groups(unit, S, Q, f, js, k, fl).items() if fl else ()):
        sh, p = anchor_shift(S, Q, f, js, anchor)
        occl = in_front(parts, js, p, img.size)
        W, H = img.size
        lay = X.flash_layer(pix, K, DX, DY, sh, (W, H), ss).reshape(H, ss, W, ss, 4).mean(axis=(1, 3))
        cover = np.maximum(cover, lay[..., 3] * (1 - occl))
        img = X.draw_flash(img, pix, K, DX, DY, sh, occl=occl, ss=ss)
    red = [] if red_flash else [(int(x), int(y)) for y, x in zip(*np.nonzero((a[..., 3] > 0) & (a[..., 0] == 255) &
                                                                              (a[..., 1] == 0) & (a[..., 2] == 0)))]
    if red and unit in DECAL_RED:
        # TS's pure red is also the Medic's red crosses: red where the fitted soldier shows a cross or his case (in
        # TS's camera, a pixel round them) is the cross, drawn by the model, not blood
        H, W = a.shape[:2]
        t, who, nrm, O = rc.render_ids(parts, ts_cam(js), 0, 0, W, H, ss=2, zstart=80.0)
        comps = np.array([0] + [p.comp for p in parts])[who + 1].reshape(H, 2, W, 2).transpose(0, 2, 1, 3)
        on = np.isin(comps, DECAL_RED[unit]).any(axis=(2, 3))
        on = ndimage.binary_dilation(on, iterations=1)
        red = [(x, y) for x, y in red if not on[y, x]]
    eab = ea_blood(unit, k)
    if eab is not None:
        red = []
        img, ba = draw_ea_blood(img, eab)
        cover = np.maximum(cover, ba)
    if red:
        img, ba = blood(img, red, js, img.size, ss)
        cover = np.maximum(cover, ba)
    if cover.any():
        # the trim: house colour only where the effects leave the soldier showing
        t = np.asarray(trim).astype(np.float32) * (1 - cover)
        trim = Image.fromarray(np.clip(np.round(t), 0, 255).astype(np.uint8), 'L')
    return img, trim


# frames a unit's layout has but never shows (the Engineer is unarmed: TS's fire and fire-prone frames are a single
# pixel): drawn empty
# (the Jumpjet's deaths are empty in TS: he dies by the tumble, 436-450)
BLANK = {'eng': range(164, 260), 'jj': range(134, 164), 'medic': range(164, 260)}


def main():
    unit, shape, out = sys.argv[1:4]
    import infunit; infunit.use(unit)
    js = json.load(open(shape))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    tab = pose_table(unit, dict(js['Q']))
    blank = set(BLANK.get(unit, ()))
    frames = [int(v) for v in sys.argv[4].split(',')] if len(sys.argv) > 4 else sorted(set(tab) | blank)
    os.makedirs(out, exist_ok=True)
    if any(134 <= k < 164 and k not in blank for k in frames):
        DEATH_SHADOW.update(death_shadow(unit, S, js, tab))
    d, name = F.UNITS[unit]
    stem = 'ts' + name.lower()
    for k in frames:
        if k in blank:
            Image.new('RGBA', R.CANVAS, (0, 0, 0, 0)).save(os.path.join(out, '%s-%04d.png' % (stem, k)))
            Image.new('L', R.CANVAS, 0).save(os.path.join(out, '%s-%04d-trim.png' % (stem, k)))
            print('frame', k, '(empty)', flush=True); continue
        if k not in tab:
            print('no pose for frame', k, flush=True); continue
        Q, f = tab[k]
        img, trim = render_frame(unit, S, js, k, Q, f)
        img.save(os.path.join(out, '%s-%04d.png' % (stem, k)))
        trim.save(os.path.join(out, '%s-%04d-trim.png' % (stem, k)))
        print('frame', k, flush=True)


if __name__ == '__main__':
    main()
