#!/usr/bin/env python3
"""SPIKE: render a TS voxel model as a smoothed surface mesh instead of blocks.

The occupancy grid is meshed (marching cubes), the staircase is relaxed with a
few Laplacian passes, and every pixel is lit through TS's own pipeline
(VOXELS.VPL ramp, length-1.5 light, the VXL's per-voxel normals interpolated
across the surface). Camera, canvas and frame conventions are vxl_render.py's,
so the frames drop into the existing pack scripts unchanged.
usage: vxl_mesh_render.py <vxl> <outdir> [same flags as vxl_render.py]
       [--smooth N (default 3)] [--sharpness S (0..1, default 0.5: how much the
       VXL normal wins over the mesh normal)]
Needs scikit-image (scratch venv). License: GPL v3.
"""
import math, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vxl_render as V
from skimage.measure import marching_cubes


def mesh_section(sec, smooth, sharpness, remap):
    occ = np.pad(sec['occ'], 1)
    verts, faces, mc_norm, _ = marching_cubes(occ.astype(np.float32), level=0.5)
    verts = verts - 1.0  # back to voxel index space (voxel i spans [i-0.5, i+0.5])
    # Laplacian relaxation of the staircase
    n = len(verts)
    nb = [set() for _ in range(n)]
    for a, b, c in faces:
        nb[a].update((b, c)); nb[b].update((a, c)); nb[c].update((a, b))
    idx = [np.fromiter(s, dtype=np.int64) for s in nb]
    # Taubin smoothing: a shrink step then an inflate step, so the staircase
    # relaxes without the model losing volume.
    def lap(vs, k):
        new = vs.copy()
        for i, s in enumerate(idx):
            if len(s):
                new[i] = vs[i] + k * (vs[s].mean(axis=0) - vs[i])
        return new
    for _ in range(smooth):
        verts = lap(lap(verts, 0.5), -0.53)
    # per-vertex normal: VXL normal of the nearest occupied voxel, blended with
    # the relaxed mesh normal
    geo = V.compute_normals(sec['occ'])
    vn = V.vxl_normals(sec, geo)
    vi = np.clip(np.rint(verts).astype(int), 0, np.array(sec['occ'].shape) - 1)
    # snap to an occupied voxel: search the 3x3x3 neighbourhood
    occ0 = sec['occ']
    vox_n = np.zeros((n, 3), dtype=np.float32)
    for k in range(n):
        x, y, z = vi[k]
        if occ0[x, y, z]:
            vox_n[k] = vn[x, y, z]; continue
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    X, Y, Z = x + dx, y + dy, z + dz
                    if 0 <= X < occ0.shape[0] and 0 <= Y < occ0.shape[1] and 0 <= Z < occ0.shape[2] and occ0[X, Y, Z]:
                        d = dx * dx + dy * dy + dz * dz
                        if best is None or d < best[0]:
                            best = (d, X, Y, Z)
        if best:
            vox_n[k] = vn[best[1], best[2], best[3]]; vi[k] = best[1:]
    # recompute mesh normals on the relaxed surface (area-weighted)
    fn = np.cross(verts[faces[:, 1]] - verts[faces[:, 0]], verts[faces[:, 2]] - verts[faces[:, 0]])
    mn = np.zeros_like(verts)
    np.add.at(mn, faces[:, 0], fn); np.add.at(mn, faces[:, 1], fn); np.add.at(mn, faces[:, 2], fn)
    mn /= np.maximum(np.linalg.norm(mn, axis=1, keepdims=True), 1e-6)
    nrm = sharpness * vox_n + (1 - sharpness) * mn
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-6)
    # Vertex colour = the dominant palette index among SURFACE voxels in the
    # 3x3x3 around the vertex's voxel: TS paints per-voxel shade variation into
    # the colour itself, which blocks read as texture and a smooth surface reads
    # as patches. Remap (team) voxels and hull voxels are counted separately so
    # the majority never flips a green voxel grey or vice versa.
    r0, r1 = remap
    colg = sec['col']
    surf = occ0 & ~(np.pad(occ0, 1)[2:, 1:-1, 1:-1] & np.pad(occ0, 1)[:-2, 1:-1, 1:-1] & np.pad(occ0, 1)[1:-1, 2:, 1:-1]
                    & np.pad(occ0, 1)[1:-1, :-2, 1:-1] & np.pad(occ0, 1)[1:-1, 1:-1, 2:] & np.pad(occ0, 1)[1:-1, 1:-1, :-2])
    cols = np.zeros(n, dtype=np.uint8)
    for k in range(n):
        x, y, z = vi[k]
        own = colg[x, y, z]; own_remap = r0 <= own <= r1
        counts = {}
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    X, Y, Z = x + dx, y + dy, z + dz
                    if 0 <= X < occ0.shape[0] and 0 <= Y < occ0.shape[1] and 0 <= Z < occ0.shape[2] and surf[X, Y, Z]:
                        c = colg[X, Y, Z]
                        if (r0 <= c <= r1) == own_remap:
                            counts[c] = counts.get(c, 0) + 1
        cols[k] = max(counts, key=counts.get) if counts else own
    return verts, faces, nrm, cols, vi


def render(model, meshes, yaw_deg, ppv, team_green, canvas, elev_deg, z_clip):
    V.set_elev(elev_deg) if hasattr(V, 'set_elev') else None
    E = math.radians(elev_deg); SIN_E, COS_E = math.sin(E), math.cos(E)
    pal = V.team_ramp(model['palette'], model['remap'], team_green)
    yaw = math.radians(yaw_deg); cy, sy = math.cos(yaw), math.sin(yaw)
    SS = V.SS
    P, N, C, F, VI, SEC = [], [], [], [], [], []
    off = 0
    for si, (sec, (verts, faces, nrm, cols, vi)) in enumerate(zip(model['sections'], meshes)):
        min_b, max_b = sec['min_b'], sec['max_b']
        step = (max_b - min_b) / np.array(sec['size'])
        pos = min_b + (verts + 0.5) * step
        P.append(pos); N.append(nrm); C.append(cols); F.append(faces + off); VI.append(vi.astype(np.float32)); SEC.append(np.full(len(verts), si)); off += len(verts)
    pos = np.concatenate(P); nrm = np.concatenate(N); cols = np.concatenate(C); faces = np.concatenate(F); vidx = np.concatenate(VI); vsec = np.concatenate(SEC)
    colgrids = [sec['col'] for sec in model['sections']]; occgrids = [sec['occ'] for sec in model['sections']]
    rx = pos[:, 0] * cy - pos[:, 1] * sy; ry = pos[:, 0] * sy + pos[:, 1] * cy; rz = pos[:, 2]
    nx = nrm[:, 0] * cy - nrm[:, 1] * sy; ny = nrm[:, 0] * sy + nrm[:, 1] * cy; nz = nrm[:, 2]
    if z_clip is not None:
        keep = (rz[faces] >= z_clip).all(axis=1); faces = faces[keep]
    u = rx; v = ry * SIN_E + rz * COS_E; depth = ry * COS_E - rz * SIN_E
    scale = ppv * SS
    if canvas is None:
        ext = max(abs(u).max(), abs(v).max()) + 2
        canvas = int(math.ceil(ext * 2 * ppv / 4.0) * 4 + 8)
    W = H = canvas * SS
    su = u * scale + W / 2.0; sv = H / 2.0 - v * scale
    lam = np.stack([nx * V.LIGHT[0] + ny * V.LIGHT[1] + nz * V.LIGHT[2]], axis=1)[:, 0]
    img = np.zeros((H, W, 4), dtype=np.float32); zbuf = np.full((H, W), 1e9, dtype=np.float32)
    base = pal[cols]
    isremap = (cols >= model['remap'][0]) & (cols <= model['remap'][1])
    for tri in faces:
        xs, ys = su[tri], sv[tri]
        x0, x1 = int(max(math.floor(xs.min()), 0)), int(min(math.ceil(xs.max()), W - 1))
        y0, y1 = int(max(math.floor(ys.min()), 0)), int(min(math.ceil(ys.max()), H - 1))
        if x1 < x0 or y1 < y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        d = (xs[1] - xs[0]) * (ys[2] - ys[0]) - (xs[2] - xs[0]) * (ys[1] - ys[0])
        if abs(d) < 1e-9:
            continue
        w0 = ((xs[1] - gx) * (ys[2] - gy) - (xs[2] - gx) * (ys[1] - gy)) / d
        w1 = ((xs[2] - gx) * (ys[0] - gy) - (xs[0] - gx) * (ys[2] - gy)) / d
        w2 = 1 - w0 - w1
        m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not m.any():
            continue
        z = w0 * depth[tri[0]] + w1 * depth[tri[1]] + w2 * depth[tri[2]]
        reg = zbuf[y0:y1 + 1, x0:x1 + 1]
        m &= z < reg
        if not m.any():
            continue
        reg[m] = z[m]
        l = w0 * lam[tri[0]] + w1 * lam[tri[1]] + w2 * lam[tri[2]]
        sidx = np.clip(np.floor(np.clip(l, 0, 1) * V.TS_LIGHT_LEN * 16).astype(np.int32), 0, 31)
        shade = V.TS_VPL_SCALE[sidx]
        # colour = the voxel under this pixel (interpolated voxel-space position,
        # rounded), so the paint scheme stays crisp across a smoothed surface
        # colour = the nearest vertex's surface voxel (no blending, no interior
        # sampling): panels stay solid, paint edges stay sharp
        # blend the (denoised) vertex colours across the face, except where a
        # face straddles team colour and hull: there the nearest vertex wins
        cls = isremap[np.asarray(tri)]
        if cls[0] == cls[1] == cls[2]:
            col = (w0[..., None] * base[tri[0]] + w1[..., None] * base[tri[1]] + w2[..., None] * base[tri[2]])
        else:
            wmax = np.argmax(np.stack([w0, w1, w2], axis=-1), axis=-1)
            col = base[np.asarray(tri)[wmax]]
        rgb = np.clip(col * shade[..., None], 0, 255)
        tgt = img[y0:y1 + 1, x0:x1 + 1]
        tgt[m, :3] = rgb[m]; tgt[m, 3] = 255
    out = Image.fromarray(img.astype(np.uint8), 'RGBA').resize((W // SS, H // SS), Image.LANCZOS)
    return out, canvas


def main():
    args = sys.argv[1:]
    vxl_path, outdir = args[0], args[1]
    opts = {'--frames': '32', '--px-per-voxel': '12', '--yaw0': '0', '--team-green': '0,200,0',
            '--canvas': '0', '--elev': '32', '--z-clip': '', '--smooth': '2', '--sharpness': '0.5', '--hva': ''}
    i = 2
    while i < len(args):
        opts[args[i]] = args[i + 1]; i += 2
    model = V.parse_vxl(vxl_path)
    meshes = [mesh_section(sec, int(opts['--smooth']), float(opts['--sharpness']), model['remap']) for sec in model['sections']]
    print('mesh:', sum(len(m[1]) for m in meshes), 'triangles')
    os.makedirs(outdir, exist_ok=True)
    frames = int(opts['--frames']); canvas = int(opts['--canvas']) or None
    tg = tuple(int(x) for x in opts['--team-green'].split(','))
    zc = float(opts['--z-clip']) if opts['--z-clip'] else None
    for f in range(frames):
        yaw = float(opts['--yaw0']) + 360.0 * f / frames
        img, canvas = render(model, meshes, yaw, float(opts['--px-per-voxel']), tg, canvas, float(opts['--elev']), zc)
        img.save(f'{outdir}/frame-{f:04d}.png')
    print(f'rendered {frames} frames, canvas {canvas}px -> {outdir}')


if __name__ == '__main__':
    main()
