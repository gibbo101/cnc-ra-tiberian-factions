"""
lrender.py - the Limpet Drone's HD frames for the mod (TSLIMP, 192 x 192, 8 canvas px per classic pixel):
    0-9    the drone, its light blinking as TS's LIMPED 0-9 (the light's two halves take TS's colour each frame)
    10-19  the drone's shadow on the ground, the same each frame (TS's 10-19 are one shadow)
The drone is the fitted model (limp.py, fit_b.json) in the RA-grid camera (32 degrees), at the size and place the
mod's drone frames have (6.2 canvas px per TS px, matched by alpha overlap); the shadow frames carry its ground
shadow (black at alpha 191) where the mod's shadow frames have theirs.

    python3 lrender.py frames 0,10 [ss] [outdir]
"""
import json, os, sys, time
import numpy as np
from PIL import Image
import rc, rcrender as RR
import walls2 as W
import limp as L
from frameio import save

HERE = os.path.dirname(os.path.abspath(__file__))
CANVAS = (192, 192)
PPU = 6.2                        # the mod's drone frames: TS px x 6.2
PX_SCALE = 1.5                   # the game draws this canvas at two thirds (8 canvas px a classic pixel)
HOVER = 5.8                      # the cone's tip over the ground (TS: the shadow's middle 5 rows under the tip)
BOUNDS = ((-12, 12), (-12, 12), (-1, 32))
SHADOW_LEN = 1.0
ORIGIN = None                    # the tip's canvas point (set from the mod's frame 0: see place())
SHADOW_SHIFT = None              # the shadow frames' shift onto the mod's shadow

GREEN = np.array([0, 214, 0.])
GREY = np.array([150, 150, 156.])         # the band and the cap (TS's 97-161 greys)
DARK = np.array([40, 40, 44.])            # the nub and the lenses (TS's 20-60)
FILL = 0.32
# the light's two halves per frame, TS's colours (LIMPED 0-9, pixels (45, 23) and (46, 23)); None = off (TS's 97 grey)
WHITE, YEL, ORA1, ORA2, RED, DRED = (255, 255, 255), (255, 255, 0), (255, 190, 0), (255, 125, 0), (255, 0, 0), (190, 0, 0)
LIGHT = [(None, RED), (None, WHITE), (WHITE, ORA1), (ORA2, DRED), (RED, None), (WHITE, None), (ORA1, WHITE),
         (ORA2, YEL), (RED, ORA1), (DRED, ORA2)]
# TS's glint on the dome over the light (LIMPED 3 and 4, pixel (46, 20)): white, then pale blue
GLINT = {3: (255, 255, 255), 4: (206, 206, 255)}
LIGHT_OFF = np.array([97, 97, 101.])


def load(path=os.path.join(HERE, 'fit_c.json')):
    js = json.load(open(path))
    P = dict(L.P0); P.update(js['P'])
    # the lenses as TS's pixels have them (2 px dark, on the band's lower half, a white pixel on their left)
    P.update(lr=0.85, lz=0.4, la=36.0, lamps=1.0)
    # the top as TS draws it (rows 12-14): a rounded dark nub 4 px across standing in a thin grey ring 6 px across;
    # the cone's top 8 px across under the band's 10 (row 28)
    P.update(nr=1.9, nh=1.4, kr=2.9, kh=0.35)
    P['cr'] = 0.8 * P['br']
    return P


def camera(origin):
    return RR.ra_cam(PPU, origin)


def scene(P):
    parts = [p.moved(np.eye(3), (0, 0, HOVER)) for p in L.parts(P)]
    lights = [q + np.array([0, 0, HOVER]) for q in L.light_points(P)]
    return parts, lights


def render(P, k, origin, ss=4, sky=True, shadow_only=False):
    parts, lights = scene(P)
    cam = camera(origin)
    win = (0, 0) + CANVAS
    r = RR.RCRender(parts, cam, CANVAS, win, BOUNDS, ss=ss, shadow_len=SHADOW_LEN, px_scale=PX_SCALE)
    hm = r.hitmask
    comp = r.comp
    if shadow_only:
        return footprint_shadow(P, cam, ss), None
    # soften the cylinders' rims and the ellipsoids stay smooth as they are
    grain = (W.sample(W.NOISE_FINE, r.x * 4, r.z * 4) * 0.035)
    g1 = (1 + 0.45 * grain)[..., None]
    alb = np.zeros(hm.shape + (3,), np.float32)
    put = lambda m, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=m[..., None])
    put(np.isin(comp, (L.DOME, L.CONE)), GREEN * (1 + 1.1 * grain)[..., None])
    put(np.isin(comp, (L.BAND, L.CAP)), GREY * g1)
    put(np.isin(comp, (L.NUB, L.LENS)), DARK * g1)
    put(comp == L.LAMP, np.array([236, 236, 232.]) * g1)
    occ = r.sky_occlusion() if sky else None
    col = r.shade(alb, sky_occ=occ, ao=None)
    tc = np.array([cam.T[0] * cam.cE, cam.T[1] * cam.cE, cam.sE]); tc = tc / np.linalg.norm(tc)
    nf = np.clip(r.nx * tc[0] + r.ny * tc[1] + r.nz * tc[2], 0, 1) * (1 - np.clip(r.nz, 0, 1))
    if occ is not None:
        nf = nf * (1 - 0.85 * np.clip(occ, 0, 1))
    col = col + alb * (FILL * nf)[..., None]
    # the light: its two halves on the dome's front, lit in TS's colours (unshaded), round, 0.5 TS px across
    P3 = np.stack([r.x, r.y, r.z], -1)
    for q, c in zip(lights, LIGHT[k % 10]):
        d = np.linalg.norm(P3 - q, axis=-1)
        m = (d < 0.55) & hm & (comp == L.DOME)
        cc = LIGHT_OFF if c is None else np.asarray(c, float)
        a = np.clip((0.55 - d) / 0.12, 0, 1)[..., None] * m[..., None]
        col = col * (1 - a) + cc * a
    if k % 10 in GLINT:
        zb = P['ch'] + P['bh'] + HOVER
        gz = zb + 3.0                         # TS's glint: 3 rows over the light, a column right of its left half
        rr = P['dr'] * np.sqrt(max(1 - (3.0 / P['dh']) ** 2, 0.0))
        a0 = np.arcsin(np.clip(-1.5 / rr, -1, 1))
        q = np.array([rr * np.sin(a0), rr * np.cos(a0), gz])
        d = np.linalg.norm(P3 - q, axis=-1)
        a = np.clip((0.45 - d) / 0.15, 0, 1)[..., None] * (hm & (comp == L.DOME))[..., None]
        col = col * (1 - a) + np.asarray(GLINT[k % 10], float) * a
    img = r.compose(col, ground=None)
    house = np.isin(comp, (L.DOME, L.CONE)) & hm
    for q in lights:                                  # the light is not house colour
        house &= np.linalg.norm(P3 - q, axis=-1) >= 0.55
    full = np.zeros((r.H * ss, r.W * ss), np.float32)
    full[:, :] = house
    trim = Image.fromarray((full.reshape(r.H, ss, r.W, ss).mean(axis=(1, 3)) * 255).round().astype(np.uint8), 'L')
    return img, trim


def footprint_shadow(P, cam, ss=4):
    """the drone's shadow as TS draws a hovering unit's: its footprint straight under it on the ground (a disc as wide
    as its widest part), black at the buildings' shadow alpha (191), blurred as theirs."""
    from scipy import ndimage
    Wc, Hc = CANVAS
    xs = (np.arange(Wc * ss) + 0.5) / ss; ys = (np.arange(Hc * ss) + 0.5) / ss
    SX, SY = np.meshgrid(xs, ys)
    gx, gy = cam.ground(SX, SY)
    R = max(P['br'], P['dr'], P['cr'])
    a = (np.hypot(gx, gy) <= R).astype(np.float32)
    a = ndimage.gaussian_filter(a, 1.5 * PX_SCALE * ss) * W.SHADOW_ALPHA
    a = a.reshape(Hc, ss, Wc, ss).mean(axis=(1, 3))
    rgba = np.zeros((Hc, Wc, 4), np.uint8)
    rgba[..., 3] = np.clip(np.round(a * 255), 0, 255).astype(np.uint8)
    return Image.fromarray(rgba, 'RGBA')


def shift(img, dx, dy):
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
    out.paste(img, (int(round(dx)), int(round(dy))))
    return out


def frame(k, P, place, ss=4, sky=True):
    if k < 10:
        return render(P, k, place['origin'], ss, sky)
    img, _ = render(P, 0, place['origin'], ss, sky, shadow_only=True)
    return shift(img, *place['shadow_shift']), Image.new('L', CANVAS, 0)


if __name__ == '__main__':
    P = load()
    place = json.load(open(os.path.join(HERE, 'place.json')))
    ks = [int(a) for a in sys.argv[2].split(',')]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    out = sys.argv[4] if len(sys.argv) > 4 else 'out'
    os.makedirs(out, exist_ok=True)
    for k in ks:
        t0 = time.time()
        img, trim = frame(k, P, place, ss)
        save(img, trim, f'{out}/tslimp-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
