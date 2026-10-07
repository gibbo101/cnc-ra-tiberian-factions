"""3D model of the dug-in Tick Tank as .glb, into <PKG>-3d/tick-tank-dug-in.glb, from the same model that renders the
frames (TS's way round: the tank faces east):
  base / base-damaged   building frames 00 / 01: the hull dug in (pitched 81 degrees nose-down, sunk, cut at the
                        ground), the turret's post, the soil round it (a heightfield mesh), and for 01 the debris
  turret                a node at the turret's pivot (on its post on top, dug in), the turret facing east; turn it about the
                        up axis to aim (anticlockwise seen from above = the mod's facings counting up from 24)
  markers               turret-pivot, muzzle (a child of turret: the gun's tip), cell-centre
  cameras               camera-ra-grid, camera-ts-angle: the frames' cameras, framing the canvases exactly
Vertex colours are the materials' base colours (COLOR_0) and house colour (COLOR_1, white); the painted detail (soot,
shell holes, soil caked on the hull, the soil's mottling) is in the frames only.

    python3 tickexport.py"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(HERE, 'src'), HERE):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
import tickm as K, tickrender as TR
import hdv, rcexport as RX, vexport as VE
import voxrender as VR
from export3d import orient

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-nod-tick-tank-dug-in-hd')
OUT = PKG + '-3d'
UPC = 128.0 / K.VOX_PX_BLD          # voxels per cell (30.72)


def ellip_mesh(part):
    """a compact mesh of an ellipsoid part (a latitude-longitude grid, shared vertices, its own normals), its cut
    planes flattening it (vertices beyond a plane moved onto it, with the plane's normal)."""
    e = next(c for c in part.cons if c.kind == 'ellip')
    rmax = float(e.r.max())
    nl = int(np.clip(round(rmax * 1.6), 8, 22)); nk = 2 * nl
    lat = np.linspace(-np.pi / 2, np.pi / 2, nl + 1)
    lon = np.linspace(0, 2 * np.pi, nk, endpoint=False)
    LA, LO = np.meshgrid(lat, lon, indexing='ij')
    U = np.stack([np.cos(LA) * np.cos(LO), np.cos(LA) * np.sin(LO), np.sin(LA)], -1).reshape(-1, 3)
    P = e.c + (U * e.r) @ e.R.T
    N = (U / e.r) @ e.R.T
    N /= np.linalg.norm(N, axis=1, keepdims=True)
    for c in part.cons:
        if c.kind != 'plane':
            continue
        out = P @ c.n - c.d
        m = out > 0
        P[m] -= out[m, None] * c.n[None, :]
        N[m] = c.n
    F = []
    for i in range(nl):
        for j in range(nk):
            a, b = i * nk + j, i * nk + (j + 1) % nk
            cc, d = (i + 1) * nk + j, (i + 1) * nk + (j + 1) % nk
            F += [(a, b, d), (a, d, cc)]
    F = np.array(F, int)
    a, b, c2 = P[F[:, 0]], P[F[:, 1]], P[F[:, 2]]
    keep = np.linalg.norm(np.cross(b - a, c2 - a), axis=1) > 1e-9
    return P, F[keep], N


def merged(items, mats, skip=('soil_col',)):
    Ps, Fs, Ns, Cs, Hs = [], [], [], [], []
    off = 0
    for it in items:
        if it.name in skip:
            continue
        if it.kind == 'ellip':
            P, Fi, Nn = ellip_mesh(it.part)
            if len(Fi) == 0 or P[:, 2].max() <= 1e-6:
                continue
        else:
            try:
                m = RX.part_mesh(it.part)
            except Exception:
                m = None               # empty: wholly under the ground (the claws, the drum's lower half ...)
            if m is None:
                continue
            V_, F = m
            P, Fi, Nn = (RX.smooth_shaded if it.kind == 'cyl' else RX.flat_shaded)(V_, F)
        Fi = orient(P, Fi, Nn)
        mt = mats[it.mat]
        col = hdv.GREEN * (0.5 if it.mat == 'skirt' else 1.0) if mt.get('house') else np.asarray(mt['col'], float)
        Ps.append(P); Fs.append(Fi + off); Ns.append(Nn)
        Cs.append(np.tile(np.minimum(col, 255.0), (len(P), 1)))
        Hs.append(np.full(len(P), 1.0 if mt.get('house') else 0.0))
        off += len(P)
    return Ps, Fs, Ns, Cs, Hs, off


def berm_mesh(G, step=0.5):
    """the soil's surface as triangles (marching squares at its foot), its normals from the heightfield."""
    x0, x1, y0, y1 = K.soil_region(G)
    xs = np.arange(x0, x1 + step, step); ys = np.arange(y0, y1 + step, step)
    X, Y = np.meshgrid(xs, ys, indexing='ij')
    H = K.soil_h(G, X, Y, 1.0)
    P, F = [], []
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            hs = (H[i, j], H[i + 1, j], H[i, j + 1], H[i + 1, j + 1])
            if max(hs) <= K.TAU:
                continue
            poly = K.cell_poly((xs[i], xs[i + 1]), (ys[j], ys[j + 1]), hs)
            if len(poly) < 3:
                continue
            b = len(P)
            P += [(px, py, max(pz, 0.0)) for px, py, pz in poly]
            for k in range(1, len(poly) - 1):
                F.append((b, b + k, b + k + 1))
    P = np.array(P, float); F = np.array(F, int)
    eps = 0.15
    hx = (K.soil_h(G, P[:, 0] + eps, P[:, 1], 1.0) - K.soil_h(G, P[:, 0] - eps, P[:, 1], 1.0)) / (2 * eps)
    hy = (K.soil_h(G, P[:, 0], P[:, 1] + eps, 1.0) - K.soil_h(G, P[:, 0], P[:, 1] - eps, 1.0)) / (2 * eps)
    N = np.stack([-hx, -hy, np.ones(len(P))], 1); N /= np.linalg.norm(N, axis=1, keepdims=True)
    F = orient(P, F, N)
    return P, F, N


def export():
    c = TR.cfg('ra')
    glb = VE.AnimGLB()
    root = glb.node('TickTankDugIn')
    Mx = VR.facing_cw(VR.mod_to_cw(K.FACING))
    face = glb.node('dug_in_facing_%s' % {16: 'south', 24: 'east', 8: 'west', 0: 'north'}.get(K.FACING, str(K.FACING)), root, rotation=VE.quat(VE.A @ Mx),
                    extras=dict(note='the unit frame: x forward (east), y left (north), z up; voxels / 30.72 = cells'))
    for name, level in (('base', 0), ('base-damaged', 1)):
        M = K.model(c, t=1.0, turret=None, damage=level)
        Ps, Fs, Ns, Cs, Hs, off = merged(M.items, M.mats)
        bp, bf, bn = berm_mesh(M.G)
        Ps.append(bp); Fs.append(bf + off); Ns.append(bn)
        Cs.append(np.tile(np.array([80.0, 66.0, 50.0]), (len(bp), 1))); Hs.append(np.zeros(len(bp)))
        P = np.concatenate(Ps) / UPC
        glb.node(name, face, mesh=(P.astype(np.float32), np.concatenate(Fs), np.concatenate(Ns).astype(np.float32),
                                   np.concatenate(Cs), np.concatenate(Hs)))
        print(name, len(P), 'verts', flush=True)
    # the turret, about its pivot, facing east
    M = K.model(c, t=1.0, turret=0.0, base=False)
    piv = M.seat
    Ps, Fs, Ns, Cs, Hs, off = merged(M.items, M.mats)
    P = (np.concatenate(Ps) - piv) / UPC
    tn = glb.node('turret', face, translation=piv / UPC,
                  extras=dict(note='turn about its local up axis (z in the unit frame) to aim: anticlockwise seen from '
                                   'above; the mod\'s facing f = %d + angle / 11.25 degrees' % K.FACING))
    glb.node('turret_mesh', tn, mesh=(P.astype(np.float32), np.concatenate(Fs), np.concatenate(Ns).astype(np.float32),
                                      np.concatenate(Cs), np.concatenate(Hs)))
    mz = K.muzzle(c, 1.0, 0.0)
    glb.node('muzzle', tn, translation=(mz - piv) / UPC, extras=dict(note='the gun\'s tip, the turret facing the hull\'s way'))
    glb.node('turret-pivot', face, translation=piv / UPC, extras=dict(note='the turret\'s pivot on its post, dug in'))
    glb.node('cell-centre', face, translation=(0.0, 0.0, 0.0), extras=dict(note='the cell\'s centre on the ground = the '
                                                                                   'unit\'s position'))
    # cameras, framing the canvases
    for v, look, nm in (('ra', 0.0, 'camera-ra-grid'), ('iso', 315.0, 'camera-ts-angle')):
        cv = TR.cfg(v)
        cam = TR.N.camera(cv)
        W, H = TR.CANVAS[v]
        gx, gy = cam.ground(np.array([W / 2.0]), np.array([H / 2.0]))
        elev = float(np.degrees(np.arcsin(cam.sE)))
        glb.camera(nm, look, elev, list(VE.A @ np.array([gx[0], gy[0], 0.0]) / UPC), W / 2.0 / 128.0, H / 2.0 / 128.0,
                   extras=dict(note=f'orthographic, {elev:g} degrees above the ground, looking '
                                    f'{"north" if v == "ra" else "north-west"}; frames the {W} x {H} '
                                    f'{"ra-grid" if v == "ra" else "ts-angle"} canvas'))
    os.makedirs(OUT, exist_ok=True)
    glb.save(f'{OUT}/tick-tank-dug-in.glb', extras=dict(
        units='1.0 = one cell (128 px on the RA grid); x east, y up, z south (glTF); origin = the cell\'s centre on '
              'the ground (the unit\'s position)', facing='the mod\'s %d (16 = south, the nose toward the RA camera)' % K.FACING))
    print('saved', f'{OUT}/tick-tank-dug-in.glb', flush=True)


if __name__ == '__main__':
    export()
