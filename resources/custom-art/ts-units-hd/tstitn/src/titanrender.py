"""
titanrender.py - the Titan's HD frames for the mod (TSTITN, 448 x 448, 128 frames):
   0-95   the legs: mod facing f (counter-clockwise from north) x 12 walk steps, frame = f x 12 + step;
          they carry the ground shadow of the whole Titan (legs + upper body facing the same way, no cannon)
   96-127 the upper body with the cannon, 32 facings counter-clockwise from north; no shadow
Each frame also gets a -trim.png (white = house colour).

    python3 titanrender.py frames 0,12,24 [ss] [outdir]
"""
import os, sys, time
import numpy as np
from PIL import Image
import rc, rcrender as RR, titan as TN, titanmat as TM
from frameio import save

OUT = __import__('os').path.join(__import__('paths').HERE, 'out')
SHADOW_LEN = 0.62        # the house light's shadow direction, 62% as long: the Titan's shadow stays on its 448 canvas
PX_SCALE = 1.5           # the game draws the Titan's canvas at 2/3 (8 canvas px per classic px against EA's 5.33)
import legfit as LF, torso2 as T2
GOLD_COMPS = (LF.SHIN, LF.FOOT, LF.THIGH, T2.BODY, T2.HATCH)
HIP_COMPS = (LF.PELVIS, LF.HIPDOME, LF.HIPRING, LF.HIPJOINT)
BOUNDS_LEGS = ((-26, 26), (-26, 26), (-1, 54))
BOUNDS_TORSO = ((-36, 36), (-36, 36), (15, 54))


def camera(S=None):
    """the RA-grid camera: a true orthographic view 32 degrees above the ground, looking north, 6.4 canvas px per
    TS px (the in-mod scale); the ground under the unit where TS's sprite has it (the hip at the canvas centre,
    the feet's lowest pixels on y 386)."""
    if S is None:
        S, _ = TN.load_legs()
    return RR.ra_cam(TN.PPU, (224.0, 386.0 - TN.PPU * TN.COS30 * S['g']))


def find_window(parts, cam, margin=10, step=3):
    """a coarse cast over the whole canvas: the box round everything hit, plus a margin."""
    xs = np.arange(0, 448, step) + step / 2; ys = np.arange(0, 448, step) + step / 2
    SX, SY = np.meshgrid(xs, ys)
    O = cam.rays(SX.ravel(), SY.ravel())
    t, who, _ = rc.cast(parts, O, cam.D, want_normals=False)
    hit = np.isfinite(t).reshape(SX.shape)
    if not hit.any():
        return (0, 0, 8, 8)
    yy, xx = np.nonzero(hit)
    return (max(int(xs[xx.min()] - margin), 0), max(int(ys[yy.min()] - margin), 0),
            min(int(xs[xx.max()] + margin), 448), min(int(ys[yy.max()] + margin), 448))


def leg_frame(k, ss=4, S=None, poses=None, P=None, sky=True):
    if S is None:
        S, poses = TN.load_legs(); P = TN.load_torso()
    f8, si = divmod(k, 12)
    k8 = TN.mod_to_cw(f8, 8)
    legs, M, t = TN.legs_parts(S, TN.mod_step_pose(poses, si), k8)
    torso, Mt, tt = TN.torso_parts(P, k8 * 4, S['g'], with_barrel=False)
    cam = camera()
    win = find_window(legs, cam)
    frames = [(M, t)] * len(legs)
    # TS lights its leg sprite on its own (the upper body is a separate sprite), so the legs take no shadow or
    # sky occlusion from the upper body; its shadow on the ground is in the leg frames
    r = RR.RCRender(legs, cam, TN.CANVAS, win, BOUNDS_LEGS, ss=ss, frames=frames, occluders=legs,
                    shadow_len=SHADOW_LEN, px_scale=PX_SCALE)
    occ = r.sky_occlusion() if sky else None
    # the waist sits under the upper body: it takes the upper body's shadow and its cover from the sky (TS's
    # dark mass between the body and the legs); the legs below do not
    waist = np.isin(r.comp, HIP_COMPS)
    sh_extra = None
    if waist.any():
        sm2 = RR.LightMap(legs + torso, r.Ls, BOUNDS_LEGS, r.sm.step)
        Pw = np.stack([r.x[waist], r.y[waist], r.z[waist]], 1)
        sh_extra = np.zeros(r.x.shape, np.float32)
        sh_extra[waist] = sm2.test(Pw, bias=0.15, pcf=1)
        if sky:
            r.occluders = legs + torso
            occ2 = r.sky_occlusion()
            r.occluders = legs
            occ = np.where(waist, occ2, occ)
    r.spur_t = along(r, 'spur')
    # no camera fill where the waist is in the upper body's shadow: it stays dark, as in TS
    r.fill_mask = None if sh_extra is None else (1 - 0.9 * sh_extra)
    alb, (bx, by, bz), emit = TM.materials(r, P=P, S=S, occ=occ)
    ao = 0.86 + 0.14 * np.clip(r.z / 12.0, 0, 1)
    if sh_extra is not None:
        ao = ao * (1 - 0.35 * sh_extra)
    col = r.shade(alb, sky_occ=occ, ao=ao, shadow_extra=sh_extra) + emit
    col = col + spec(r, GOLD_COMPS) * (1 - (sh_extra if sh_extra is not None else 0.0))[..., None]
    g = r.ground_alpha_full(shadow_parts=legs + torso)
    img = r.compose(col, ground=g)
    trim = trim_img(r, alb)
    return img, trim


def torso_frame(k, ss=4, S=None, P=None, sky=True):
    if S is None:
        S, _ = TN.load_legs(); P = TN.load_torso()
    f32 = k - 96
    k32 = TN.mod_to_cw(f32, 32)
    parts, M, t = TN.torso_parts(P, k32, S['g'], with_barrel=True)
    cam = camera()
    win = find_window(parts, cam)
    frames = [(M, t)] * len(parts)
    r = RR.RCRender(parts, cam, TN.CANVAS, win, BOUNDS_TORSO, ss=ss, frames=frames, shadow_len=SHADOW_LEN,
                    px_scale=PX_SCALE)
    TM.smooth_normals(r, 0); TM.smooth_normals(r, 1)
    occ = r.sky_occlusion() if sky else None
    alb, (bx, by, bz), emit = TM.materials(r, P=P, S=S, occ=occ)
    col = r.shade(alb, sky_occ=occ, ao=0.86 + 0.14 * np.clip((r.z - 20.0) / 12.0, 0, 1)) + emit
    col = col + spec(r, GOLD_COMPS)
    img = r.compose(col, ground=None)
    trim = trim_img(r, alb)
    return img, trim


def along(r, name):
    """for hits on parts called `name` (seg_box parts): the position along the part's length, 0..1."""
    t = np.zeros(r.x.shape, np.float32)
    for i, p in enumerate(r.parts):
        if p.name != name:
            continue
        m = r.who == i
        if not m.any():
            continue
        n1 = p.cons[1].n; d1 = p.cons[1].d; d0 = -p.cons[0].d
        P = np.stack([r.x[m], r.y[m], r.z[m]], 1)
        t[m] = np.clip((P @ n1 - d0) / max(d1 - d0, 1e-6), 0, 1)
    return t


def spec(r, comps, strength=0.28, power=22.0):
    """a soft highlight on shiny metal (TS's gold): Blinn-Phong with the house light, from the camera."""
    L = r.L; V = -r.cam.D
    Hh = (L + V) / np.linalg.norm(L + V)
    nh = np.clip(r.nx * Hh[0] + r.ny * Hh[1] + r.nz * Hh[2], 0, 1)
    sh = getattr(r, 'inshadow', 0.0)
    m = np.isin(r.comp, comps)
    return (strength * nh ** power * (1 - 0.9 * sh) * m * 255.0)[..., None] * np.array([1.0, 0.86, 0.58])


def trim_img(r, alb):
    tm = TM.trim_mask(r, alb).astype(np.float32)
    ss = r.ss
    full = np.zeros((r.H * ss, r.W * ss), np.float32)
    x0, y0, x1, y1 = r.win
    full[y0 * ss:y1 * ss, x0 * ss:x1 * ss] = tm
    return Image.fromarray((full.reshape(r.H, ss, r.W, ss).mean(axis=(1, 3)) * 255).round().astype(np.uint8), 'L')


def frame(k, ss=4, **kw):
    return leg_frame(k, ss, **kw) if k < 96 else torso_frame(k, ss, **kw)


if __name__ == '__main__':
    ks = [int(a) for a in sys.argv[2].split(',')] if len(sys.argv) > 2 else range(128)
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    out = sys.argv[4] if len(sys.argv) > 4 else OUT
    os.makedirs(out, exist_ok=True)
    for k in ks:
        t0 = time.time()
        img, trim = frame(k, ss)
        save(img, trim, f'{out}/tstitn-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
