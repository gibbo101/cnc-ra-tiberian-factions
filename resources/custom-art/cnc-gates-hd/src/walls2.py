"""
Tiberian Sun GDI concrete wall, rebuilt for Red Alert Remastered (128x128 per cell).

Design taken from the 16 TS frames and laid out like BRIK:
  * sloped (battered) grey concrete arms, seam at the post, two panels per cell
  * ochre flange collar at every joint between cells (proud of the wall, ribbed)
  * free ends and the lone post slope away like the TS mound
  * corners, T's and the cross get the TS junction pillar: taller, ochre sides,
    grey top with a dark socket in the middle (BRIK puts its cap in the same spot)

RA's view: screen_y = ground_y - FZ * height. Frame index = N*1 + E*2 + S*4 + W*8.
Damage stages 0-3 follow BRIK's rows (0-15 healthy, 16-31, 32-47, 48-63).
"""
import numpy as np
from PIL import Image
from scipy import ndimage

CELL, SS, MARGIN = 128, 4, 48
FZ = 0.6

P = dict(
    h=40.0, top=10.0, base=26.0,            # arm height, half-width at top / at base
    x_c=64.0, y_c=64.0, period=128.0,       # post at the cell centre, so the flange sits on the join
    seam_w=2.0, seam_depth=2.5,
    collar_half=9.0, collar_out=3.0, rib_every=4.5,
    end_top=10.0,                           # free end: top runs this far past the post, then slopes
    mound_top=24.0, mound_base=42.0,        # lone post: half-length along x at top / base
    pillar_base=23.0, pillar_top=20.5, pillar_h=60.0,
    hole=7.0, hole_depth=12.0,
)

LIGHT = np.array([-0.45, -0.55, 0.70]); LIGHT /= np.linalg.norm(LIGHT)
AMBIENT, SKY, DIFFUSE = 0.20, 0.26, 0.62   # sky term lets the sloped faces read as sloped
SHADOW_DIR = (0.62, 0.22)
SHADOW_ALPHA = 0.75
CONCRETE = np.array([226, 226, 222], float)
OCHRE = np.array([214, 166, 70], float)
GRIME = np.array([112, 104, 78], float)
SOCKET = np.array([40, 40, 38], float)

CONC, COLLAR, PILLAR = 1, 2, 3


# ----------------------------------------------------------------------------- noise
def periodic_noise(size, sigma, seed):
    rng = np.random.default_rng(seed)
    f = np.fft.fft2(rng.standard_normal((size, size)))
    k = np.fft.fftfreq(size)
    kx, ky = np.meshgrid(k, k)
    f *= np.exp(-2 * (np.pi * sigma) ** 2 * (kx ** 2 + ky ** 2))
    n = np.real(np.fft.ifft2(f))
    return (n - n.mean()) / n.std()


NOISE_FINE = periodic_noise(CELL * SS, 0.6 * SS, 1)
NOISE_MOTTLE = periodic_noise(CELL * SS, 7.0 * SS, 2)
NOISE_GRIME = periodic_noise(CELL * SS, 3.0 * SS, 3)


def sample(noise, u, v):
    iu = np.floor(u * SS).astype(int) % (CELL * SS)
    iv = np.floor(v * SS).astype(int) % (CELL * SS)
    return noise[iv, iu]


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def trap(d, a, b, h):
    """Trapezoid profile: full height out to a, sloping to 0 at b."""
    return h * np.clip((b - d) / (b - a), 0, 1)


def phase(v, per, offset=0.0):
    return np.abs(np.mod(v - offset + per / 2, per) - per / 2)


def ground_grid():
    n0 = -MARGIN * SS
    xs = (np.arange(n0, (CELL + MARGIN) * SS) + 0.5) / SS
    ys = (np.arange(n0, (CELL + 2 * MARGIN) * SS) + 0.5) / SS
    return np.meshgrid(xs, ys)


def arms_of(mask):
    return [a for a, bit in (('N', 1), ('E', 2), ('S', 4), ('W', 8)) if mask & bit]


def has_pillar(mask):
    arms = arms_of(mask)
    return len(arms) >= 2 and mask not in (5, 10)


# ----------------------------------------------------------------------------- geometry
def build(mask, p=P):
    X, Y = ground_grid()
    H = np.zeros_like(X)
    C = np.zeros(X.shape, np.int8)          # component that owns the surface
    AXIS = np.zeros(X.shape, np.int8)       # 0 = E-W arm, 1 = N-S arm
    xc, yc, per = p['x_c'], p['y_c'], p['period']

    def put(h, comp, axis=None):
        nonlocal H, C, AXIS
        win = h > H + 1e-6
        H = np.where(win, h, H)
        C = np.where(win, comp, C)
        if axis is not None:
            AXIS = np.where(win, axis, AXIS)

    arms = arms_of(mask)
    if not arms:
        # lone post: the TS mound, elongated E-W like BRIK's single block
        h = np.minimum(trap(np.abs(Y - yc), p['top'], p['base'], p['h']),
                       trap(np.abs(X - xc), p['mound_top'], p['mound_base'], p['h']))
        put(h, CONC, 0)
    for a in arms:
        if a in 'EW':
            d, s, axis = np.abs(Y - yc), (X - xc) if a == 'E' else (xc - X), 0
        else:
            d, s, axis = np.abs(X - xc), (Y - yc) if a == 'S' else (yc - Y), 1
        # arm with a hipped end just past the post (so corners mitre cleanly)
        along = trap(np.maximum(-s, 0), p['end_top'], p['end_top'] + (p['base'] - p['top']), p['h'])
        h = np.minimum(trap(d, p['top'], p['base'], p['h']), along)
        # deep seam at the post
        g = 1 - smoothstep(0, p['seam_w'], phase(s, per))
        h = np.where(h > 0, np.maximum(h - p['seam_depth'] * g, 0), 0)
        put(h, CONC, axis)
        # ochre flange collar at the joint between cells
        o = p['collar_out']
        inband = (phase(s, per, per / 2) <= p['collar_half']) & (s > 0)
        hc = np.where(inband, trap(d, p['top'] + o, p['base'] + o, p['h'] + o), 0)
        put(hc, COLLAR, axis)
    if has_pillar(mask):
        r = np.maximum(np.abs(X - xc), np.abs(Y - yc))
        hp = trap(r, p['pillar_top'], p['pillar_base'], p['pillar_h'])
        hp = np.where(r < p['hole'], hp - p['hole_depth'], hp)
        put(hp, PILLAR)
    H = ndimage.gaussian_filter(H, 0.8 * SS, mode='nearest')
    return X, Y, H, C, AXIS


# ----------------------------------------------------------------------------- render
def render(mask, p=P, extra=None):
    X, Y, H, C, AXIS = build(mask, p)
    if extra is not None:                       # damage hook: may edit the heightfield
        X, Y, H, C, AXIS, mats = extra(mask, X, Y, H, C, AXIS)
    else:
        mats = None
    n0 = MARGIN * SS
    W = CELL * SS
    Hs = H * SS
    zmax = int(np.ceil(Hs.max())) + 2
    rows = np.arange(W)[:, None]
    cols = np.arange(W)[None, :] + n0

    hit_z = np.full((W, W), -1.0)
    for z in range(zmax, -1, -1):
        h = Hs[rows + int(round(FZ * z)) + n0, cols]
        new = (hit_z < 0) & (h >= z) & (h > 0.5)
        hit_z[new] = z
    hit = hit_z >= 0
    gj = np.clip((rows + np.round(FZ * np.maximum(hit_z, 0)) + n0).astype(int), 0, Hs.shape[0] - 1)
    gi = np.broadcast_to(cols, (W, W))

    gy, gx = np.gradient(H, 1.0 / SS)
    nx, ny, nz = -gx[gj, gi], -gy[gj, gi], np.ones((W, W))
    nl = np.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx / nl, ny / nl, nz / nl
    shade = (AMBIENT + SKY * (0.5 + 0.5 * nz)
             + DIFFUSE * np.clip(nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2], 0, None))

    x, y = X[gj, gi], Y[gj, gi]
    z = np.minimum(H[gj, gi], hit_z / SS)
    comp = C[gj, gi]
    axis = AXIS[gj, gi]
    along = np.where(axis == 0, x - p['x_c'], y - p['y_c'])
    top_like = nz > 0.75
    ew_face = np.abs(ny) >= np.abs(nx)          # faces looking north/south use x, east/west use y
    u = np.where(top_like | ew_face, x, y)
    v = np.where(top_like, y, z)
    grain = sample(NOISE_FINE, u, v) * 0.035 + sample(NOISE_MOTTLE, u, v) * 0.05

    # concrete: two pours per cell, darker seam line at the post
    half = np.mod(along, p['period']) < p['period'] / 2
    conc = CONCRETE * (1 + grain)[..., None] * np.where(half, 1.0, 0.96)[..., None]
    g = 1 - smoothstep(0.2, p['seam_w'] + 0.4, phase(along, p['period']))
    conc *= (1 - 0.55 * g)[..., None]

    # ochre collar with shallow ribs
    rib = 1 - smoothstep(0.0, 0.9, phase(along, p['rib_every']))
    och = OCHRE * (1 + 0.8 * grain)[..., None] * (1 - 0.18 * rib)[..., None]

    # pillar: grey cap, ochre sides, dark socket
    r = np.maximum(np.abs(x - p['x_c']), np.abs(y - p['y_c']))
    pil_top = top_like & (z > p['pillar_h'] - 4)
    socket = (r < p['hole'] + 0.8) & (z < p['pillar_h'] - 2) & (z > p['pillar_h'] - p['hole_depth'] - 2)
    pil = np.where(pil_top[..., None], CONCRETE * 0.94 * (1 + grain)[..., None],
                   OCHRE * (1 + 0.8 * grain)[..., None])
    pil = np.where(socket[..., None], SOCKET * (1 + 0.5 * grain)[..., None], pil)

    albedo = np.where((comp == COLLAR)[..., None], och, conc)
    albedo = np.where((comp == PILLAR)[..., None], pil, albedo)
    if mats is not None:
        albedo = mats(albedo, x, y, z, comp, top_like, grain, u, v, along)

    grime = np.clip(1 - z / 15.0, 0, 1) ** 1.5 * np.clip(0.55 + 0.35 * sample(NOISE_GRIME, u, v), 0, 1)
    albedo = albedo * (1 - grime[..., None]) + GRIME * grime[..., None]
    ao = 0.8 + 0.2 * np.clip(z / p['h'], 0, 1)
    col = albedo * (shade * ao)[..., None]

    # cast + contact shadow on the ground
    gr = rows + n0 + 0 * cols
    shadow = np.zeros((W, W), bool)
    kx, ky = SHADOW_DIR
    for zz in range(1, zmax + 1):
        t = zz / SS
        si = np.clip(np.round(cols - kx * t * SS).astype(int), 0, Hs.shape[1] - 1)
        sj = np.clip(np.round(gr - ky * t * SS).astype(int), 0, Hs.shape[0] - 1)
        shadow |= Hs[sj, si] >= zz
    shadow_a = ndimage.gaussian_filter(shadow.astype(float), 1.5 * SS) * SHADOW_ALPHA
    dist = ndimage.distance_transform_edt(~(H > 0.5)) / SS
    contact = np.clip(1 - dist[gr, np.broadcast_to(cols, (W, W))] / 7.0, 0, 1) ** 1.5 * 0.5
    ground_a = np.maximum(shadow_a, contact)

    rgba = np.zeros((W, W, 4))
    rgba[..., :3] = np.where(hit[..., None], col, 0.0)
    rgba[..., 3] = np.where(hit, 1.0, ground_a)
    ring = ndimage.binary_dilation(hit, iterations=int(0.9 * SS)) & ~hit
    rgba[..., :3] = np.where(ring[..., None], 28.0, rgba[..., :3])
    rgba[..., 3] = np.where(ring, np.maximum(rgba[..., 3], 0.55), rgba[..., 3])

    pre = rgba.copy(); pre[..., :3] *= rgba[..., 3:4]
    pre = pre.reshape(CELL, SS, CELL, SS, 4).mean(axis=(1, 3))
    a = pre[..., 3:4]
    out = np.where(a > 1e-6, pre[..., :3] / np.maximum(a, 1e-6), 0)
    img = np.dstack([np.clip(out, 0, 255), np.clip(a * 255, 0, 255)]).round().astype(np.uint8)
    return Image.fromarray(img, 'RGBA')


if __name__ == '__main__':
    import sys, os
    os.makedirs('out2', exist_ok=True)
    masks = [int(m) for m in sys.argv[1:]] or list(range(16))
    for m in masks:
        render(m).save(f'out2/gdi-wall-{m:02d}.png')
    print('rendered', masks)
