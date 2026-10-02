"""
mcvmat.py - the MCV's materials, per pixel of an rcrender.RCRender.  r.lu, r.lv, r.lw are the body frame (u forward,
v right, w up, in voxels; the voxel frame is x = u + CX, y = CY - v, z = w); r.Mb maps body to world.

Colours are TS's own: every surface takes the palette colour of MCV.VXL's voxels just inside it (tsfield.py),
softly across a face where TS speckles ochre and orange, sharper on the boom whose greys are painted in bands;
the HD look comes on top (grain, grime rising from the ground, a camera fill on the sides facing it).
House colour is apart: pure green 0,214,0 x (1 + 1.1 grain) on the four track covers and the three deck panels
(TS's remap voxels), with detail only as thin seams.  Crisp details where TS's voxels draw them: the cab's roof
hatch and the rear block's hatch (dark), the shelf crates' dividers (geometry, dark), the shelf's bright fittings,
the track belts' links.
"""
import numpy as np
import walls2 as W
from walls2 import smoothstep
import mcv as M
import tsfield as TF

GREEN = np.array([0, 214, 0.])
GRIME = np.array([112, 104, 78.])
FILL = 0.32
GAIN = 1.25                                   # TS palette albedo -> the buildings' HD ochre (214,166,70 for TS 144-147)
HOUSE_COMPS = M.HOUSE
GOLD_COMPS = (M.HULL, M.DECK, M.BLOCK, M.CAB, M.PLATE, M.SHELF, M.CRATE, M.HITCH, M.RIM, M.SPINE)
SHARP = {M.BOOM_D: 3.0, M.BOOM_G: 3.0, M.BOOM_W: 3.0, M.BOOM_T: 3.0, M.EYE: 2.0, M.RAIL: 1.5, M.TRACK: 1.5,
         M.TBIT: 2.0, M.BAND: 2.0, M.POST: 2.0}
FALLBACK = {M.TRACK: (34, 32, 28), M.TBIT: (60, 52, 36), M.UNDER: (70, 62, 40), M.BUMPER: (52, 50, 46),
            M.RAIL: (52, 52, 54), M.EYE: (40, 36, 30), M.BAND: (40, 37, 17), M.POST: (52, 52, 28),
            M.BOOM_D: (90, 90, 92), M.BOOM_G: (150, 150, 152), M.BOOM_W: (200, 200, 202), M.BOOM_T: (90, 90, 92)}
GOLD = np.array([196, 150, 60.])
PAINTED = (M.DECK, M.BLOCK, M.CAB, M.CRATE, M.PLATE, M.HITCH, M.RIM, M.SPINE, M.RAIL)


def grain_of(r, scale=1.0):
    X, Y, Z = r.lu * 6.1 * scale, r.lv * 6.1 * scale, r.lw * 6.1 * scale
    ax, ay, az = np.abs(r.nx) + 1e-3, np.abs(r.ny) + 1e-3, np.abs(r.nz) + 1e-3
    s_ = ax + ay + az

    def tri(noise, o):
        return (W.sample(noise, Y + o, Z + 2 * o) * ax + W.sample(noise, X + 3 * o, Z + o) * ay +
                W.sample(noise, X + o, Y + 5 * o) * az) / s_
    return tri(W.NOISE_FINE, 0) * 0.035 + tri(W.NOISE_MOTTLE, 17) * 0.05


def phase(v, per, off=0.0):
    return np.abs(np.mod(v - off + per / 2, per) - per / 2)


def body_normals(r):
    N = np.stack([r.nx, r.ny, r.nz], -1)
    B = N @ np.asarray(r.Mb, float)                # columns of Mb = body axes in the world
    return B[..., 0], B[..., 1], B[..., 2]


def materials(r, occ=None):
    comp = r.comp
    sh = comp.shape
    alb = np.zeros(sh + (3,), np.float32)
    emit = np.zeros(sh + (3,), np.float32)
    bz = np.zeros(sh, np.float32)
    hm = r.hitmask
    grain = grain_of(r, scale=1 / 1.5)
    g1 = (1 + 0.45 * grain)[..., None]
    x = r.lu + M.CX; y = M.CY - r.lv; z = r.lw                  # voxel frame
    nu, nv, nw = body_normals(r)
    vnx, vny, vnz = nu, -nv, nw                                 # voxel-frame normal
    top = nw > 0.7
    side = ~top & (nw > -0.3)
    put = lambda m, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=m[..., None])

    # ------------------------------------------------------------------ TS's colours on every non-house part
    soft, wsoft = TF.sample(x, y, z, vnx, vny, vnz, sharp=1.0)
    sharp, wsharp = TF.sample(x, y, z, vnx, vny, vnz, sharp=3.0)
    sharpness = np.ones(sh, np.float32)
    for c, s_ in SHARP.items():
        sharpness[comp == c] = s_
    use_sharp = sharpness > 1.0
    ts = np.where(use_sharp[..., None], sharp, soft)
    wts = np.where(use_sharp, wsharp, wsoft)
    fb = np.broadcast_to(GOLD, alb.shape).copy()
    for c, col in FALLBACK.items():
        fb[comp == c] = col
    base = ts * wts[..., None] + fb * (1 - wts[..., None])
    # on the painted parts keep TS's ochre and orange where TS has them, but hold its darkest and lightest speckle
    # within reach of the part's own mean, so a face reads as weathered paint rather than voxel noise
    lum = base.mean(-1)
    for c in PAINTED:
        m = (comp == c) & hm & (wts > 0.3)
        if m.sum() < 8:
            continue
        mu = lum[m].mean()
        lo, hi = 0.62 * mu, 1.28 * mu
        k = np.clip(lum, lo, hi) / np.maximum(lum, 1e-3)
        base[m] = base[m] * k[m][:, None]
    put(hm, np.minimum(base * GAIN, 236.0) * g1)       # TS's whites as white paint, not past it
    # grime rising from the ground on the hull and the lower decks
    dust = (smoothstep(3.6, 0.6, z) * 0.4 * np.isin(comp, (M.HULL, M.UNDER, M.BUMPER)))
    alb[:] = alb * (1 - dust[..., None]) + (GRIME * g1) * dust[..., None]

    # ------------------------------------------------------------------ house colour
    house = np.isin(comp, HOUSE_COMPS) & hm
    put(house, GREEN * (1 + 1.1 * grain)[..., None])
    pan = (comp == M.PANEL) & top
    if pan.any():
        # the panels' tops: a thin seam a quarter voxel in from their edges (house colour, detail as seams only)
        bz -= 0.25 * pan * 0

    # ------------------------------------------------------------------ the belts: links round the loop
    trk = (comp == M.TRACK) & hm
    if trk.any():
        lk = trk & (phase(x + z * 0.9, 0.95) < 0.12)
        alb[lk] *= 0.62
        bz -= 0.3 * lk

    # ------------------------------------------------------------------ crisp details where TS draws them
    # the cab's roof hatch: TS's black voxel pair at x 34, y 6-7, in a darker frame
    cab = (comp == M.CAB) & top & hm
    hatch = cab & (x > 33.9) & (x < 35.1) & (y > 5.95) & (y < 8.05)
    frame = cab & (x > 33.55) & (x < 35.45) & (y > 5.9) & (y < 8.4) & ~hatch
    put(frame, alb * 0.72)
    put(hatch, np.array([30, 30, 28.]) * g1)
    bz -= 0.4 * frame
    # the rear block's hatch at its outer back corner (x 6-7, y 6-7: TS's dark olive with a black corner)
    blk = (comp == M.BLOCK) & top & hm
    h2 = blk & (x > 5.9) & (x < 8.1) & (y > 5.9) & (y < 8.1)
    put(h2, np.array([52, 50, 30.]) * g1)
    edge2 = blk & (x > 5.6) & (x < 8.4) & (y > 5.6) & (y < 8.4) & ~h2
    put(edge2, alb * 0.7)
    bz -= 0.4 * edge2
    # the shelf's fittings: TS's bright yellow voxels on the crates (small raised studs)
    crate = (comp == M.CRATE) & top & hm
    if crate.any():
        ci = TF.nearest_class(x, y, z, vnx, vny, vnz)
        bright = crate & (((ci >= 176) & (ci <= 181)) | (ci == 5) | ((ci >= 33) & (ci <= 38)) | (ci == 15))
        cx = np.floor(x) + 0.5; cy = np.floor(y) + 0.5
        stud = bright & (np.maximum(np.abs(x - cx), np.abs(y - cy)) < 0.36)
        put(stud, np.array([250, 226, 120.]) * g1)
        bz += 0.5 * stud
        # the crates' lids: a seam a little in from each crate's edges
    # ------------------------------------------------------------------ the fill light from the camera
    cam = r.cam
    tc = np.array([cam.T[0] * cam.cE, cam.T[1] * cam.cE, cam.sE]); tc = tc / np.linalg.norm(tc)
    nf = np.clip(r.nx * tc[0] + r.ny * tc[1] + r.nz * tc[2], 0, 1) * (1 - np.clip(r.nz, 0, 1))
    if occ is not None:
        nf = nf * (1 - 0.85 * np.clip(occ, 0, 1))
    emit = emit + alb * (FILL * nf)[..., None]
    alb[~hm] = 0
    return alb, (np.zeros(sh, np.float32), np.zeros(sh, np.float32), bz), emit


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, HOUSE_COMPS)
