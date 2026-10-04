"""
infrender.py - an infantry unit's HD frames for the mod (267 x 208, the canvas of EA's HD infantry: 5.33 canvas px a
classic pixel, as the buildings), from the posed soldier (inf.py): the RA-grid camera (32 degrees), the mod's size
(3.068 canvas px a TS px: the mod's frames are TS's sprite x 3.068), the feet on canvas (133.5, 111) as the README
keeps them; the buildings' light, sky, outline and supersampling with the units' camera fill; the shadow baked in
(black at alpha 191, as the buildings'); a -trim.png of the house-colour parts.
"""
import os, sys
import numpy as np
from PIL import Image
import rc, rcrender as RR
import walls2 as W
import inf as I

CANVAS = (267, 208)
PPU = 3.068
# the mod's frames are TS's sprite x 3.068 at (38.06, 10.57) (infmap.py): the soldier's ground point (TS's ax, y0 from the
# fit) goes where the mod has it, which puts the boots' lowest pixel on y 110-112 as the README says (feet on 111)
K, DX, DY = 3.068, 38.06, 10.57
FEET = (133.5, 111.0)
PX_SCALE = 1.0
SHADOW_LEN = 0.62
# how dark the baked shadow is at its darkest (the buildings': walls2.SHADOW_ALPHA, 0.75); INF_SHADOW sets it
SHADOW_DARK = float(os.environ.get('INF_SHADOW', 0.5))
BOUNDS = ((-24, 24), (-24, 24), (-1, 32))
FILL = 0.55                       # EA's HD infantry are lit from the front: a stronger camera fill than the vehicles'

GREEN = np.array([0, 214, 0.])
# E1's colours, read from TS's E1 frames (UNITTEM.PAL ramps, lit)
MAT = {I.JAW: (40, 40, 48), I.CHEST: (80, 80, 86), I.ABDOMEN: (76, 76, 82), I.POUCH: (96, 96, 130), I.HELMET: (64, 64, 98),
       I.VISOR: (158, 158, 238), I.FACE: (158, 158, 238), I.VEST: (76, 76, 82), I.PACK: (178, 178, 180),
       I.BELT: (60, 60, 64), I.HAND: (64, 64, 68), I.SHIN: (176, 176, 178), I.BOOT: (82, 82, 86),
       I.RIFLE: (18, 18, 20), I.RIFLE_DARK: (14, 14, 16)}
# the rifle stays as black as TS draws it (0-28): no camera fill on it
NOFILL = (I.RIFLE, I.RIFLE_DARK)
HOUSE = (I.PAD, I.PELVIS, I.UARM, I.FARM, I.THIGH, I.KNEE)
ROUNDED = {I.BOOT: 0.3, I.PACK: 0.3, I.RIFLE: 0.12, I.RIFLE_DARK: 0.15}


# TS's sprite draws every pixel its soldier touches, half a pixel round him: fitted to it, the model stands 6% shorter
# and 11% slimmer than the mod's frames draw him (EA's Minigunner is taller still).  HD draws the fitted soldier 8%
# bigger about his feet, so he stands as tall as the mod's frames
VIS = 1.08


def camera(ground=None):
    """ground: TS's frame point of the soldier's ground point (the fit's ax, y0)."""
    o = FEET if ground is None else (ground[0] * K + DX, ground[1] * K + DY)
    return RR.ra_cam(PPU * VIS, o)


def find_window(parts, cam, margin=10, step=2):
    Wc, Hc = CANVAS
    xs = np.arange(0, Wc, step) + step / 2; ys = np.arange(0, Hc, step) + step / 2
    SX, SY = np.meshgrid(xs, ys)
    O = cam.rays(SX.ravel(), SY.ravel(), zstart=80.0)
    t, who, _ = rc.cast(parts, O, cam.D, want_normals=False)
    hit = np.isfinite(t).reshape(SX.shape)
    yy, xx = np.nonzero(hit)
    return (max(int(xs[xx.min()] - margin), 0), max(int(ys[yy.min()] - margin), 0),
            min(int(xs[xx.max()] + margin), Wc), min(int(ys[yy.max()] + margin), Hc))


def round_edges(r):
    for i, p in enumerate(r.parts):
        sig = ROUNDED.get(p.comp)
        if sig is None:
            continue
        m = (r.who == i) & r.hitmask
        if not m.any():
            continue
        pl = [c for c in p.cons if c.kind == 'plane']
        if not pl:
            continue
        N = np.array([c.n for c in pl]); d = np.array([c.d for c in pl])
        Q = np.stack([r.x[m], r.y[m], r.z[m]], 1)
        s = Q @ N.T - d[None, :]
        w = np.exp((s - s.max(1, keepdims=True)) / sig)
        n = w @ N
        n = n / np.linalg.norm(n, axis=1, keepdims=True)
        r.nx[m], r.ny[m], r.nz[m] = n[:, 0], n[:, 1], n[:, 2]


def grain_of(r):
    X, Y, Z = r.x * PPU, r.y * PPU, r.z * PPU
    ax, ay, az = np.abs(r.nx) + 1e-3, np.abs(r.ny) + 1e-3, np.abs(r.nz) + 1e-3
    s_ = ax + ay + az

    def tri(noise, o):
        return (W.sample(noise, Y + o, Z + 2 * o) * ax + W.sample(noise, X + 3 * o, Z + o) * ay +
                W.sample(noise, X + o, Y + 5 * o) * az) / s_
    return tri(W.NOISE_FINE, 0) * 0.035 + tri(W.NOISE_MOTTLE, 17) * 0.04


def materials(r, mat=None, house=None):
    mat = MAT if mat is None else mat
    house = HOUSE if house is None else house
    comp = r.comp
    alb = np.zeros(comp.shape + (3,), np.float32)
    grain = grain_of(r)
    g1 = (1 + 0.45 * grain)[..., None]
    put = lambda m, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=m[..., None])
    put(np.isin(comp, house), GREEN * (1 + 1.1 * grain)[..., None])
    for c, v in mat.items():
        put(comp == c, np.asarray(v, float) * g1)
    return alb


# parts drawn on TS's own palette ramp for their colour (infunit.use sets them per unit): {comp: (ramp, G[, gamma])},
# the ramp's colours dark to light (TS's frames: a saturated colour runs redder as it darkens, yellower as it
# lightens), G the luminance the part would have at full light, gamma how much of the HD shading it keeps.  Each pixel
# takes the ramp colour as light as the part's shading there makes it (below the ramp's darkest colour, that colour
# darkened)
RAMP = {}


def lum(c):
    c = np.asarray(c, float)
    return c[..., 0] * 0.299 + c[..., 1] * 0.587 + c[..., 2] * 0.114


def ramp_colour(ramp, L):
    ramp = np.asarray(ramp, float)
    ls = lum(ramp)
    L = np.asarray(L, float)
    out = np.stack([np.interp(L, ls, ramp[:, i]) for i in range(3)], -1)
    low = L < ls[0]
    out[low] = ramp[0] * (np.clip(L[low], 0, None) / ls[0])[:, None]
    return out


def apply_ramps(r, col, mat):
    for c, spec in RAMP.items():
        ramp, G = spec[0], spec[1]
        gamma = spec[2] if len(spec) > 2 else 1.0        # < 1: less between lit and shaded (TS lights from the camera)
        m = (r.comp == c) & r.hitmask
        if m.any() and c in mat:
            L = G * np.clip(lum(col[m]) / max(float(lum(mat[c])), 1e-6), 0, None) ** gamma
            col[m] = ramp_colour(ramp, L)
    return col


# the mask glows: TS draws the faceplate its brightest light blue (178,178,255 and 149,149,230, a near-white 222,222,246
# glint) whichever way it faces, as the references' visors glow; so it shows TS's light blue over its own shading,
# lighter where it faces the camera, with TS's light's highlight.  The helmet is glossy: TS's light-blue pixel on its
# top left in every facing is its highlight from TS's light (front left of the camera)
VISOR_SHOW = np.array([160, 160, 240.])
VISOR_EDGE = np.array([104, 104, 180.])
HELMET_GLINT = np.array([170, 170, 240.])     # (infunit.use sets the three per unit: the Engineer's are grey and white)
VISOR_GLOW = True                             # (the Ghost Stalker's 'visor' is his bare face: no glow)
VISOR_SKY = None                              # a dark glass faceplate's sky colour (the Medic's): shown as it faces up
H_HD = np.array([-0.33, 0.75, 0.57]) / np.linalg.norm([-0.33, 0.75, 0.57])


def visor_look(r, col):
    view = np.array([0.0, np.cos(np.deg2rad(32.0)), np.sin(np.deg2rad(32.0))])
    nh = np.clip(r.nx * H_HD[0] + r.ny * H_HD[1] + r.nz * H_HD[2], 0, 1)
    m = np.isin(r.comp, (I.VISOR, I.FACE)) & r.hitmask
    if m.any() and VISOR_GLOW:
        nv = np.clip(r.nx * view[0] + r.ny * view[1] + r.nz * view[2], 0, 1)
        show = VISOR_EDGE + (VISOR_SHOW - VISOR_EDGE) * np.clip(nv * 1.3 - 0.2, 0, 1)[..., None]
        out = col * 0.25 + show * 0.75
        out = out + (np.array([236, 236, 252.]) - out) * (nh ** 10 * 0.75)[..., None]
        col = np.where(m[..., None], out, col)
    if m.any() and VISOR_SKY is not None and not VISOR_GLOW:
        # dark glass: the sky in it as it turns up, and the light's glint
        up = np.clip(r.nz, 0, 1) ** 1.2 * 0.85
        out = col + (VISOR_SKY - col) * up[..., None]
        out = out + (np.array([226, 226, 240.]) - out) * (nh ** 20 * 0.7)[..., None]
        col = np.where(m[..., None], out, col)
    hm = (r.comp == I.HELMET) & r.hitmask
    if hm.any():
        sp = nh ** 24 * 0.8
        out = col + (HELMET_GLINT - col) * sp[..., None]
        col = np.where(hm[..., None], out, col)
    return col


# painted marks drawn in their own flat colour, lit only a little (the Medic's red crosses: TS's pure red)
FLAT = {I.CROSS: np.array([235.0, 28.0, 28.0])} if hasattr(I, 'CROSS') else {}


def flat_look(r, col):
    for c, v in FLAT.items():
        m = (r.comp == c) & r.hitmask
        if m.any():
            shade = 0.82 + 0.18 * np.clip(r.nz[m] * 0.5 + 0.5, 0, 1)
            col[m] = v[None, :] * shade[:, None]
    return col


def render(parts, ss=4, sky=True, mat=None, house=None, shadow=True, extra=visor_look, ground=None, shadow_len=None,
           shadow_w=1.0):
    """one frame of the posed soldier's parts (world, the ground point at the origin): (RGBA, trim).  shadow_len: the
    ground shadow's length for this frame (SHADOW_LEN by default; 0 = the light straight overhead), shadow_w: its
    strength (a dying soldier's, deathshadow.py)."""
    mat = MAT if mat is None else mat
    house = HOUSE if house is None else house
    cam = camera(ground)
    win = find_window(parts, cam)
    r = RR.RCRender(parts, cam, CANVAS, win, BOUNDS, ss=ss, shadow_len=SHADOW_LEN, px_scale=PX_SCALE)
    round_edges(r)
    occ = r.sky_occlusion() if sky else None
    alb = materials(r, mat, house)
    ao = 0.88 + 0.12 * np.clip(r.z / 10.0, 0, 1)
    col = r.shade(alb, sky_occ=occ, ao=ao)
    tc = np.array([cam.T[0] * cam.cE, cam.T[1] * cam.cE, cam.sE]); tc = tc / np.linalg.norm(tc)
    nf = np.clip(r.nx * tc[0] + r.ny * tc[1] + r.nz * tc[2], 0, 1) * (1 - np.clip(r.nz, 0, 1))
    if occ is not None:
        nf = nf * (1 - 0.85 * np.clip(occ, 0, 1))
    nf = np.where(np.isin(r.comp, NOFILL), 0.0, nf)
    col = col + alb * (FILL * nf)[..., None]
    if RAMP:
        col = apply_ramps(r, col, mat)
    if extra is not None:
        col = extra(r, col)
    if FLAT:
        col = flat_look(r, col)
    g = None
    if shadow:
        Ls0 = r.Ls
        if shadow_len is not None and abs(shadow_len - SHADOW_LEN) > 1e-6:
            # (the ground shadow alone from a higher light: the soldier's own shading keeps the usual one)
            b = cam.cam_to_world(RR.LS_CAM)
            Ls = np.array([b[0] * shadow_len, b[1] * shadow_len, b[2]], float)
            r.Ls = Ls / np.linalg.norm(Ls)
        g = r.ground_alpha_full(shadow_parts=parts)
        r.Ls = Ls0
        if shadow_w < 1.0:
            g = g * max(float(shadow_w), 0.0)
    if g is not None and SHADOW_DARK != W.SHADOW_ALPHA:
        # (the infantry's shadow lighter than the buildings': the mod's frames carry TS's at about 25% black, and at
        # the buildings' 75% every gap under a falling soldier stood out - Luke: they "look like they're floating")
        g = g * (SHADOW_DARK / W.SHADOW_ALPHA)
    img = r.compose(col, ground=g)
    hm = np.isin(r.comp, house) & r.hitmask
    full = np.zeros((r.H * ss, r.W * ss), np.float32)
    x0, y0, x1, y1 = r.win
    full[y0 * ss:y1 * ss, x0 * ss:x1 * ss] = hm
    trim = Image.fromarray((full.reshape(r.H, ss, r.W, ss).mean(axis=(1, 3)) * 255).round().astype(np.uint8), 'L')
    return img, trim
