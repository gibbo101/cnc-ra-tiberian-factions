"""
Tiberian Sun Nod wall (NAWALL / NTWALL.SHP), rebuilt for Red Alert Remastered (128x128 per cell).

Shape measured from the 16 TS frames by re-projecting a 3D model into TS's view and fitting it to the
sprites (nod/hyp.py, nod/fit.py; ~86% silhouette overlap on every frame):
  * arms: thin dark wedges along each connection, tall where two cells meet, sloping down to a low
    point at the cell centre (the "V" top that TS shows as boxes at the front and ramps at the back)
  * legs: triangular buttresses on the open sides, peaking at the centre and running down to the
    ground near the cell edge, so a straight run gets a "+" at every cell (TS's view turns it into an X)
  * corners get one buttress on the diagonal instead; a lone post / dead end keeps a capped arm
  * dark neutral-grey concrete, lighter tops, pale drip streaks on the faces, a little grime at the foot
Heights keep TS's proportions, scaled so the joints stand about as tall as the GDI wall's arms.

RA's view: screen_y = ground_y - FZ * height. Frame index = N*1 + E*2 + S*4 + W*8.
"""
import numpy as np
from PIL import Image
from scipy import ndimage
import walls2 as W
from walls2 import (CELL, SS, MARGIN, FZ, LIGHT, AMBIENT, SKY, DIFFUSE, SHADOW_DIR, SHADOW_ALPHA,
                    smoothstep, sample, phase, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME, ground_grid, arms_of)

S_TS = 92.0      # HD height units per TS cell of height (TS: 1 cell of height = 29.4 px)

P = dict(
    H=0.45 * S_TS,          # arm height where two cells meet
    zc=0.237 * S_TS,        # arm height at the cell centre
    ta=0.092 * CELL,        # arm half-thickness
    zl=0.48 * S_TS,         # buttress peak (cell centre)
    tl=0.11 * CELL,         # buttress half-thickness
    R=0.47 * CELL,          # buttress reach from the centre
    cap_inset=2.0,          # a capped (unconnected) arm stops this far short of the cell edge
    diag_out=0.85, diag_in=1.30,   # corner buttress reach (x R) outward / into the corner
    x_c=64.0, y_c=64.0,
)

CONC = np.array([126, 126, 128], float)      # dark neutral concrete (TS greys, lifted to RA brightness)
DRIP = np.array([236, 236, 232], float)
GRIME = np.array([70, 66, 58], float)
SEAM = np.array([40, 40, 42], float)

ARM, LEG, DEBRIS = 1, 2, 4
DIRV = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}
OPP = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}


def pieces_for(mask, p=P):
    """(kind, direction vector, extra) list, following the TS frames."""
    arms = arms_of(mask)
    out = [('arm', DIRV[a], a, True) for a in arms]
    ns = [a for a in arms if a in 'NS']; ew = [a for a in arms if a in 'EW']
    if len(arms) == 2 and ns and ew:                       # corner: buttress on the diagonal
        d = np.array(DIRV[ns[0]]) + np.array(DIRV[ew[0]])
        d = d / np.linalg.norm(d)
        out.append(('leg', tuple(-d), p['diag_out'], None))
        out.append(('leg', tuple(d), p['diag_in'], None))
        return out
    for a in 'NESW':
        if a in arms:
            continue
        if not arms:
            out.append(('leg', DIRV[a], 1.0, None) if a in 'NS' else ('arm', DIRV[a], a, False))
        elif len(arms) == 1 and a == OPP[arms[0]]:
            out.append(('arm', DIRV[a], a, False))                 # dead end: capped arm
        else:
            out.append(('leg', DIRV[a], 1.0, None))
    return out


def build(mask, p=P):
    X, Y = ground_grid()
    Hf = np.zeros_like(X)
    C = np.zeros(X.shape, np.int8)
    AXIS = np.zeros(X.shape, np.int8)        # 0 = runs E-W, 1 = runs N-S (texture orientation)
    ALONG = np.zeros_like(X)                 # distance from the cell centre along the piece
    xc, yc = p['x_c'], p['y_c']
    dx, dy = X - xc, Y - yc

    def put(h, comp, axis, along):
        nonlocal Hf, C, AXIS, ALONG
        win = h > Hf + 1e-6
        Hf = np.where(win, h, Hf)
        C = np.where(win, comp, C)
        AXIS = np.where(win, axis, AXIS)
        ALONG = np.where(win, along, ALONG)

    for kind, d, extra, connected in pieces_for(mask, p):
        ux, uy = d
        u = dx * ux + dy * uy                 # along the piece
        w = -dx * uy + dy * ux                # across it
        axis = 0 if abs(ux) > abs(uy) else 1
        if kind == 'arm':
            half = CELL / 2
            if connected:
                # wedge up to the joint, then the neighbour's wedge coming back down (mirrored)
                t = np.where(u <= half, u / half, (2 * half - u) / half)
                inside = (u >= -0.5) & (np.abs(w) <= p['ta'])
            else:
                t = u / half
                inside = (u >= -0.5) & (u <= half - p['cap_inset']) & (np.abs(w) <= p['ta'])
            h = np.where(inside, p['zc'] + (p['H'] - p['zc']) * np.clip(t, 0, 1), 0)
            put(h, ARM, axis, u)
        else:
            R = p['R'] * extra
            if abs(ux) > 1e-6 and abs(uy) > 1e-6:          # diagonal buttress: keep it inside the frame
                R = min(R, 0.5 * CELL * np.sqrt(2) - 4)
            inside = (u >= -0.5) & (u <= R) & (np.abs(w) <= p['tl'])
            h = np.where(inside, p['zl'] * np.clip(1 - u / R, 0, 1), 0)
            put(h, LEG, 1 - axis, u)
    Hf = ndimage.gaussian_filter(Hf, 0.6 * SS, mode='nearest')
    return X, Y, Hf, C, AXIS, ALONG


# ----------------------------------------------------------------------------- render
def render(mask, p=P, extra=None):
    X, Y, Hf, C, AXIS, ALONG = build(mask, p)
    if extra is not None:
        X, Y, Hf, C, AXIS, mats = extra(mask, X, Y, Hf, C, AXIS)
    else:
        mats = None
    n0 = MARGIN * SS
    Wd = CELL * SS
    Hs = Hf * SS
    zmax = int(np.ceil(Hs.max())) + 2
    rows = np.arange(Wd)[:, None]
    cols = np.arange(Wd)[None, :] + n0

    hit_z = np.full((Wd, Wd), -1.0)
    for z in range(zmax, -1, -1):
        h = Hs[rows + int(round(FZ * z)) + n0, cols]
        new = (hit_z < 0) & (h >= z) & (h > 0.5)
        hit_z[new] = z
    hit = hit_z >= 0
    gj = np.clip((rows + np.round(FZ * np.maximum(hit_z, 0)) + n0).astype(int), 0, Hs.shape[0] - 1)
    gi = np.broadcast_to(cols, (Wd, Wd))

    gy, gx = np.gradient(Hf, 1.0 / SS)
    nx, ny, nz = -gx[gj, gi], -gy[gj, gi], np.ones((Wd, Wd))
    nl = np.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx / nl, ny / nl, nz / nl
    shade = (AMBIENT + SKY * (0.5 + 0.5 * nz)
             + DIFFUSE * np.clip(nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2], 0, None))

    x, y = X[gj, gi], Y[gj, gi]
    top_h = Hf[gj, gi]
    z = np.minimum(top_h, hit_z / SS)
    comp = C[gj, gi]
    axis = AXIS[gj, gi]
    top_like = nz > 0.8
    ew_face = np.abs(ny) >= np.abs(nx)
    u = np.where(top_like | ew_face, x, y)
    v = np.where(top_like, y, z * 0.35)                 # faces: grain stretched down the face
    grain = sample(NOISE_FINE, u, v) * 0.045 + sample(NOISE_MOTTLE, u, v) * 0.07
    albedo = CONC * (1 + grain)[..., None]
    below = np.clip(top_h - z, 0, None)                  # depth below the top edge on a face
    face_h = np.maximum(top_h, 1.0)

    # drips: TS puts two pale drips on the face of every joint block. Here: two each side of every
    # joint (cell edge) on the arms' faces, plus a few thin ones elsewhere; lengths vary per drip.
    run_x = np.where(axis == 0, x, y)                    # coordinate along the arm
    dj = np.abs(np.mod(run_x + 64.0, 128.0) - 64.0)      # distance to the nearest joint
    side = np.sign(np.mod(run_x + 64.0, 128.0) - 64.0)
    jid = np.floor((run_x + 64.0) / 128.0) + 7 * axis + 3 * (side > 0)
    drip = np.zeros_like(x)
    for k, (pos, wid) in enumerate(((6.0, 1.3), (17.0, 1.6))):
        h = np.mod(np.sin((jid + 1.7 * k) * 12.9898) * 43758.5453, 1.0)       # per-drip hash
        length = 0.45 + 0.4 * h
        lat = pos + 2.5 * (h - 0.5)
        core = 1 - smoothstep(wid * 0.4, wid, np.abs(dj - lat))
        tip = 1 - smoothstep(0.6 * length, length, below / face_h)
        drip = np.maximum(drip, core * tip)
    lane = np.mod(u * 1.0 + 23.0 * axis, 11.0)
    lid = np.floor((u + 23.0 * axis) / 11.0)
    hl = np.mod(np.sin(lid * 78.233) * 43758.5453, 1.0)
    thin = (1 - smoothstep(0.35, 0.8, np.abs(lane - 5.5))) * (hl > 0.72) * \
        (1 - smoothstep(0.25 + 0.3 * hl, 0.45 + 0.3 * hl, below / face_h)) * 0.6
    drip = np.maximum(drip * (comp == ARM), thin)
    drip = drip * ~top_like * smoothstep(0.5, 2.0, below + 2.0 * (below > 0.3))
    albedo = albedo * (1 - 0.85 * drip[..., None]) + DRIP * (0.85 * drip)[..., None]
    # faint, irregular rain staining down the faces
    stain = smoothstep(0.6, 1.6, sample(NOISE_MOTTLE, u * 2.5, 13.0 + 0 * below)) * ~top_like * \
        (1 - smoothstep(0.3, 1.0, below / face_h))
    albedo = albedo * (1 - 0.12 * stain)[..., None]

    # bevels: a lighter lip on the top edge of every face, and a bright rim on the tops next to a drop
    lip = (1 - smoothstep(0.4, 1.8, below)) * ~top_like
    albedo = albedo * (1 + 0.22 * lip)[..., None]
    drop = ndimage.maximum_filter(np.hypot(*np.gradient(Hf, 1.0 / SS)), size=int(2.2 * SS))
    rim = smoothstep(1.5, 4.0, drop[gj, gi]) * top_like
    albedo = albedo * (1 + 0.16 * rim)[..., None]

    # seams: where two cells' arms meet (on the frame edge, half each side) and where a buttress
    # butts against an arm
    edge_d = np.minimum.reduce([np.abs(x), np.abs(CELL - x), np.abs(y), np.abs(CELL - y)])
    seam = (1 - smoothstep(0.3, 1.2, edge_d)) * (comp == ARM)
    arm_w = np.where(axis == 0, np.abs(y - p['y_c']), np.abs(x - p['x_c']))
    butt = (comp == LEG) & top_like & (np.abs(arm_w - p['ta']) < 0.9)
    seam = np.maximum(seam, butt * 0.8)
    albedo = albedo * (1 - seam[..., None]) + SEAM * seam[..., None]
    if mats is not None:
        albedo = mats(albedo, x, y, z, comp, top_like, grain, u, v, top_h)

    grime = np.clip(1 - z / 12.0, 0, 1) ** 1.6 * np.clip(0.5 + 0.35 * sample(NOISE_GRIME, u, v), 0, 1)
    albedo = albedo * (1 - grime[..., None]) + GRIME * grime[..., None]
    ao = 0.78 + 0.22 * np.clip(z / p['H'], 0, 1)
    col = albedo * (shade * ao)[..., None]

    gr = rows + n0 + 0 * cols
    shadow = np.zeros((Wd, Wd), bool)
    kx, ky = SHADOW_DIR
    for zz in range(1, zmax + 1):
        t = zz / SS
        si = np.clip(np.round(cols - kx * t * SS).astype(int), 0, Hs.shape[1] - 1)
        sj = np.clip(np.round(gr - ky * t * SS).astype(int), 0, Hs.shape[0] - 1)
        shadow |= Hs[sj, si] >= zz
    shadow_a = ndimage.gaussian_filter(shadow.astype(float), 1.5 * SS) * SHADOW_ALPHA
    dist = ndimage.distance_transform_edt(~(Hf > 0.5)) / SS
    contact = np.clip(1 - dist[gr, np.broadcast_to(cols, (Wd, Wd))] / 7.0, 0, 1) ** 1.5 * 0.5
    ground_a = np.maximum(shadow_a, contact)

    rgba = np.zeros((Wd, Wd, 4))
    rgba[..., :3] = np.where(hit[..., None], col, 0.0)
    rgba[..., 3] = np.where(hit, 1.0, ground_a)
    ring = ndimage.binary_dilation(hit, iterations=int(0.9 * SS)) & ~hit
    rgba[..., :3] = np.where(ring[..., None], 22.0, rgba[..., :3])
    rgba[..., 3] = np.where(ring, np.maximum(rgba[..., 3], 0.55), rgba[..., 3])

    pre = rgba.copy(); pre[..., :3] *= rgba[..., 3:4]
    pre = pre.reshape(CELL, SS, CELL, SS, 4).mean(axis=(1, 3))
    a = pre[..., 3:4]
    out = np.where(a > 1e-6, pre[..., :3] / np.maximum(a, 1e-6), 0)
    img = np.dstack([np.clip(out, 0, 255), np.clip(a * 255, 0, 255)]).round().astype(np.uint8)
    return Image.fromarray(img, 'RGBA')


if __name__ == '__main__':
    import sys, os
    os.makedirs('nod/out', exist_ok=True)
    masks = [int(m) for m in sys.argv[1:]] or list(range(16))
    for m in masks:
        render(m).save(f'nod/out/nod-wall-{m:02d}.png')
    print('rendered', masks)
