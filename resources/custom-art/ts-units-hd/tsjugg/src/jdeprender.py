"""
jdeprender.py - the Juggernaut deployed, in HD for the mod (TSJUGG, 448 x 448):
   120-151  deployed at rest, 32 facings counter-clockwise from north: base + cabin + barrels at TS's starting pitch
   152-183  deployed and aiming: the barrels raised to 45 degrees about their breech
The scene (jdeployed.py): the base (fitted to DJUGG frame 0), the cabin (fitted to DJUGG_A's 32 facings) turning on its
pivot, and the barrels straight from TS's DJUGGBAR.VXL (its voxels, colours and normals, as the voxel units), at the
size and place the mod's deployed frames draw them (jbarfit.py).

Camera: the RA-grid camera (32 degrees), 6.33 canvas px per TS px, the walk's mapping (jrender.MAP) so the deployed
piece stands where TS's deploy puts it against the walker (DJUGGMK's frame 0 is JUGGER's CW5 frame moved by (1, 14)).

    python3 jdeprender.py frames 120,136,152 [ss] [outdir] [sky]
"""
import json, os, sys, time
import numpy as np
from PIL import Image
import rc, rcrender as RR, vxl, vxlunit as VU, voxrender as VR
import walls2 as W
from walls2 import smoothstep
import jugg as JG
import jdeployed as JD
import jfitcabin as JC
import jbase as JB
import jrender as JR
import jtlegs as TL
import jtrender as JT
import jtbase as TB
from frameio import save

HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
CANVAS = JR.CANVAS
PPU = JR.PPU
BOUNDS = ((-40, 40), (-40, 40), (-1, 50))
DJUGG_TO_JUGGER = (1.0, 14.0)            # DJUGG / DJUGGMK px = JUGGER px + (1, 14) (TS's deploy frame 0 = JUGGER 75)
REST_PITCH = 5.3                          # TS starts the barrels pitched: the mod's rest frames have them so
AIM_PITCH = 45.0                          # raised 45 degrees above level, about the breech
BAR = 300
ROD = 301                                 # the deploy's thin barrels sliding out of the walker's housings
ROD_GREY = np.array([138, 138, 144.])     # TS's greys on them (DJUGGMK 13-16: 44-51)
STRUT_ROWS = (0, 9, 18)              # DJUGGBAR's rods: voxels x 0-6, z 6 and up, in these rows

# TS's colours (UNITTEM.PAL, read off DJUGG frame 0 and DJUGG_A)
FRONT = np.array([58, 58, 62.])           # the cabin's dark front plate (TS's 53-59)
DARK = np.array([44, 44, 48.])            # the hatch's slit, the sensor's core (TS's 53-62)
PANEL = np.array([74, 74, 78.])           # the dark panel in the hatch's top (TS's 52-97)
PIVOT = np.array([56, 54, 40.])           # the pivot column (TS's olive and dark greys 119-127, 54-61)
RIM = np.array([70, 70, 122.])            # its rim (TS's blue-greys 196-199)


def load(rest='fit_bar_rest.json', aim='fit_bar_aim.json'):
    M = JD.load_fits()
    br = json.load(open(HERE + rest)); ba = json.load(open(HERE + aim))
    raw = vxl.read_vxl(JD.H + 'ts-original/DJUGGBAR.VXL')[0]
    names, mats = vxl.read_hva(JD.H + 'ts-original/DJUGGBAR.HVA')
    pal = vxl.read_pal(JD.H + 'ts-original/UNITTEM.PAL')
    s = br['s']
    sc = dict(raw); sc['min'] = np.asarray(raw['min'], float) * s; sc['max'] = np.asarray(raw['max'], float) * s
    # the thin black rod rising back from each breech (one voxel thick, on each barrel's left): the mod's deployed
    # frames never show it, so it is left out
    col = np.array(raw['col'])
    for y in STRUT_ROWS:
        col[:7, y, 6:] = -1
    sc['col'] = col
    sec = VU.Section(sc, pal, sigma=0.3, denoise=0.3)
    Mh = np.asarray(mats)[0, 0]
    return dict(M=M, bar=br, aim=ba, sec=sec, hva=(Mh[:, :3], Mh[:, 3] * raw['det'] * s), s=s)


def camera(m):
    K, dx, dy = JR.MAP
    ax, by0 = m['M']['axis']
    return RR.ra_cam(PPU, ((ax - DJUGG_TO_JUGGER[0]) * K + dx, (by0 - DJUGG_TO_JUGGER[1]) * K + dy))


def barrel_pose(m, k32, pitch):
    """(R, t) taking the barrel section's own (scaled) coordinates to the deployed world, for the cabin at the mod's
    facing k32 and the barrels at pitch degrees above level, turned about their hinge (the breech)."""
    sec, (Rh, th) = m['sec'], m['hva']
    br, ba = m['bar'], m['aim']
    vs = sec.scale                                   # TS px per voxel along each axis
    hinge0 = np.array([4.0, 11.5, 3.5])              # jbarfit's reference point (voxel index coordinates)
    hinge = np.array([ba['hi'], 11.5, ba['hk']])     # the breech pivot the aim fit found
    # the hinge's place on the cabin (unit frame: x forward, y left, z up) with the barrels at the rest pitch
    a0 = np.deg2rad(br['p0'])
    Rp0 = np.array([[np.cos(a0), 0, -np.sin(a0)], [0, 1, 0], [np.sin(a0), 0, np.cos(a0)]])
    mount0 = np.array([br['mu'], -br['mv'], br['mw']])
    d = (hinge - hinge0) * vs
    H = mount0 + Rp0 @ d
    a = np.deg2rad(pitch)
    Rp = np.array([[np.cos(a), 0, -np.sin(a)], [0, 1, 0], [np.sin(a), 0, np.cos(a)]])
    Lh = sec.mn + hinge * vs                         # the hinge in the section's own coordinates
    Lh = Rh @ Lh + th
    Mx = VR.facing_cw(VR.mod_to_cw(k32))
    T = np.array([m['M']['cab_off'], 0.0, m['M']['cab_dz']])
    R = Mx @ Rp @ Rh
    t = Mx @ (H + Rp @ (th - Lh)) + T
    return R, t


def cabin_parts(m, k32):
    P = m['M']['PC']
    R = JG.facing_matrix((32 - k32) % 32, 32)
    T = (m['M']['cab_off'], 0.0, m['M']['cab_dz'])
    parts = JC.cabin_parts(P) + JG.details(P)
    return [p.moved(R, T) for p in parts]


def materials(r, comp, grain):
    alb = np.zeros(comp.shape + (3,), np.float32)
    g1 = (1 + 0.45 * grain)[..., None]
    put = lambda msk, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=msk[..., None])
    put(np.isin(comp, (JG.SHELL, JG.ANT, JG.ARCH)), JR.GREEN * (1 + 1.1 * grain)[..., None])
    put(np.isin(comp, (JG.PACK, JG.BARREL)), JR.KHAKI * g1)
    put(comp == JG.MUZZLE, JR.STEEL * g1)
    put(comp == JG.CABLE, JR.CABLE * g1)
    put(comp == JG.HIP, JR.OLIVE * g1)
    put(comp == ROD, ROD_GREY * g1)
    put(comp == JG.HATCH, JR.HATCH * g1)
    put(np.isin(comp, (JG.SLOT, JG.HSLIT, JG.SCORE, JG.MSLOT)), DARK * g1)
    put(comp == JG.RECESS, PANEL * g1)
    put(comp == JC.FRONT, FRONT * g1)
    put(comp == JB.PIVOT, PIVOT * g1)
    put(comp == JB.RIM, RIM * g1)
    put(np.isin(comp, (JB.LKNEE, JG.KNEE, JG.ANKLE)), JR.JOINT * g1)
    legs = np.isin(comp, (JB.LIMB, JB.LFOOT, JG.THIGH, JG.SHIN, JG.FOOT))
    lit = np.clip((r.nx * -0.45 + r.ny * -0.55 + r.nz * 0.7) * 1.4 - 0.3, 0, 1)[..., None]
    put(legs, (JR.OCHRE * (1 - 0.35 * lit) + JR.BRIGHT * 0.35 * lit) * g1)
    dust = smoothstep(4.0, 0.5, r.z) * 0.35 * legs
    alb = alb * (1 - dust[..., None]) + (JR.GRIME * g1) * dust[..., None]
    return JR.sensor_materials(r, alb, g1)                     # the antenna (the Titan's)


ROUNDED = dict(JR.ROUNDED)
ROUNDED.update({JB.LIMB: 0.4, JB.LFOOT: 0.4})


def deployed_scene(m, f, pitch):
    """the deployed piece with the cabin at the mod's facing f (32) and the barrels at pitch: (modelled parts,
    the barrels' pose)."""
    return TB.base_world(m['M']) + cabin_parts(m, f), barrel_pose(m, f, pitch)


def frame(k, m, ss=4, sky=True, tsn=0.6):
    f = (k - 120) % 32
    pitch = REST_PITCH if k < 152 else AIM_PITCH
    rcparts, pose = deployed_scene(m, f, pitch)
    return render(rcparts, pose, m, camera(m), ss, sky, tsn)


def render(rcparts, pose, m, cam, ss=4, sky=True, tsn=0.6):
    """one frame: the modelled parts with the jrender / jdeployed materials, plus the barrel voxel at pose (R, t) or
    none, through cam."""
    sec = m['sec']
    if pose is not None:
        R, t = pose
        bar = sec.parts(R, t, BAR, chamfer=0.3 * m['s'])
    else:
        R, t = np.eye(3), np.zeros(3)
        bar = []
    parts = rcparts + bar
    nrc = len(rcparts)
    win = JR.find_window(parts, cam)
    r = JT.setup(parts, cam, CANVAS, win, BOUNDS, ss)              # the Titan's legs lit on their own (jtrender)
    hm = r.hitmask
    sh = hm.shape
    comp = r.comp
    P = np.stack([r.x, r.y, r.z], -1)
    Ng = np.stack([r.nx, r.ny, r.nz], -1).copy()
    isbar = (comp == BAR) & hm
    # the barrels: TS's colours, house voxels and normals sampled from the voxel (as voxrender does)
    rgb = np.zeros(sh + (3,), np.float32); wcol = np.zeros(sh, np.float32); whouse = np.zeros(sh, np.float32)
    lmean = np.zeros(sh, np.float32); hshade = np.ones(sh, np.float32); tsnv = np.zeros(sh + (3,), np.float32)
    if isbar.any():
        I = sec.to_index(P[isbar], R, t)
        nI = np.linalg.solve(R, Ng[isbar].T).T * sec.scale[None, :]
        c, wc, wh, lm, hs, tn = sec.sample(I, nI, sharp=2.0)
        rgb[isbar] = c; wcol[isbar] = wc; whouse[isbar] = wh; lmean[isbar] = lm; hshade[isbar] = hs
        tw = (R @ (tn / sec.scale[None, :]).T).T
        tsnv[isbar] = tw / (np.linalg.norm(tw, axis=1, keepdims=True) + 1e-9)
    # shading normals: the barrels' exposed box faces rounded (voxrender), the modelled parts' edges softened
    class U:
        sections = [sec]
    owner = np.array([-1] * nrc + [0] * len(bar))
    nx, ny, nz = VR.round_exposed(r, parts, 0.28 * m['s'], U, owner, [(R, t)])
    r.nx = np.where(isbar, nx, r.nx); r.ny = np.where(isbar, ny, r.ny); r.nz = np.where(isbar, nz, r.nz)
    saved = JR.ROUNDED
    JR.ROUNDED = ROUNDED
    try:
        JR.round_edges(r)
    finally:
        JR.ROUNDED = saved
    if tsn > 0 and isbar.any():
        nr = np.stack([r.nx, r.ny, r.nz], -1)
        dv = (tsnv - Ng) * (np.linalg.norm(tsnv, axis=-1, keepdims=True) > 0.5)
        nn = nr + tsn * dv
        nn = nn / (np.linalg.norm(nn, axis=-1, keepdims=True) + 1e-9)
        cth = np.clip((nn * nr).sum(-1, keepdims=True), -1, 1)
        cm = np.cos(np.deg2rad(25.0))
        perp = nn - cth * nr
        perp = perp / (np.linalg.norm(perp, axis=-1, keepdims=True) + 1e-9)
        nn = np.where(cth < cm, cm * nr + np.sqrt(1 - cm * cm) * perp, nn)
        r.nx = np.where(isbar, nn[..., 0], r.nx); r.ny = np.where(isbar, nn[..., 1], r.ny)
        r.nz = np.where(isbar, nn[..., 2], r.nz)
    sh_extra, occ = JT.lighting(r, sky)
    grain = JR.grain_of(r, None)
    alb = materials(r, comp, grain)
    # the barrels' albedo (voxrender's: speckle held, gain, white cap, house green with TS's remap shades)
    lum = rgb.mean(-1)
    kk = np.clip(lum, 0.75 * lmean, 1.2 * lmean) / np.maximum(lum, 1e-3)
    keep = (lum < 70) | (lum > 205)
    rgbs = rgb * np.where((wcol > 0.3) & ~keep, kk, 1.0)[..., None]
    g1 = (1 + 0.45 * grain)[..., None]
    balb = np.minimum(rgbs * VR.GAIN, VR.WHITE_CAP) * g1
    bhouse = np.clip((whouse - 0.35) / 0.3, 0, 1) * isbar
    balb = balb * (1 - bhouse[..., None]) + bhouse[..., None] * JR.GREEN[None, None, :] * (hshade * (1 + 1.1 * grain))[..., None]
    alb = np.where(isbar[..., None], balb, alb)
    alb = TL.materials(r, alb)                                     # the Titan's legs and waist
    ao = 0.86 + 0.14 * np.clip(r.z / 14.0, 0, 1)
    col = JT.finish(r, alb, occ, sh_extra, ao=ao)
    g = r.ground_alpha_full(shadow_parts=parts)
    img = r.compose(col, ground=g)
    house = (np.isin(comp, (JG.SHELL, JG.ANT, JG.ARCH)) & hm).astype(np.float32)
    house = np.maximum(house, bhouse)
    full = np.zeros((r.H * ss, r.W * ss), np.float32)
    x0, y0, x1, y1 = r.win
    full[y0 * ss:y1 * ss, x0 * ss:x1 * ss] = house
    trim = Image.fromarray((full.reshape(r.H, ss, r.W, ss).mean(axis=(1, 3)) * 255).round().astype(np.uint8), 'L')
    return img, trim


if __name__ == '__main__':
    m = load()
    ks = [int(a) for a in sys.argv[2].split(',')]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    out = sys.argv[4] if len(sys.argv) > 4 else 'out_dep'
    sky = bool(int(sys.argv[5])) if len(sys.argv) > 5 else True
    os.makedirs(out, exist_ok=True)
    for k in ks:
        t0 = time.time()
        img, trim = frame(k, m, ss, sky)
        save(img, trim, f'{out}/tsjugg-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
