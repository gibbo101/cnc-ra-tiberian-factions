"""Print-ready STL files (for 3D printing) from the same models as the delivered .glb files.

Each .glb's export script runs with export3d's build_part and GLB swapped for the ones here, so every mesh in the .glb
gets an .stl of its own, built from the model itself (not from the .glb's surface):
  - the solid sampled on a 1-unit grid (0.25 mm at the print scale), as one closed volume: every part fused, no
    internal faces, no holes (marching cubes over a padded volume: watertight and manifold by construction)
  - features thinner than MIN_FEATURE_MM (railings, cables, thin plates, a door's sheet) thickened to print: the parts
    an opening of that size removes, away from thick parts (not the corners of thick parts), grown by its radius
  - loose specks (rubble chunks smaller than MIN_ISLAND_MM3) dropped, and small bits floating above the bed
  - decimated (quadric) to at most MAX_TRIS triangles, then checked: watertight, consistent winding, a positive volume
  - millimetres at MM_PER_CELL per cell, Z up, the base flat on Z = 0, X east, Y north (as seen on the RA grid)
Files: <the .glb's folder>/stl/<mesh name>.stl, binary STL.

    python3 stlprint.py <job> ...   gdi (barracks silo tech plant yard), proc, weap, radr, hpad, dept, drop, plug,
                                    puls, dpsa, dweap, fgen, fsdf, dlimp"""
import os, sys, time, runpy, json
import numpy as np
from scipy import ndimage
from skimage import measure
import trimesh
import fast_simplification
import pymeshfix
import export3d as E

MM_PER_CELL = float(os.environ.get('STL_MM_PER_CELL', 32.0))
S = MM_PER_CELL / 128.0                 # mm per model unit
H_P = 1.0                               # sampling step (model units)
MIN_FEATURE_MM = 1.0                    # thinnest wall or rod that prints (FDM, 0.4 mm nozzle)
MIN_ISLAND_MM3 = 3.0
FLOOR_MM = 1.2                          # bibs and pads: at least this thick on the plate
MAX_TRIS = 180_000
REPORT = []


def field(sc, zmax, h):
    """the solid as a field (model units, positive inside, clipped to +-h), as export3d samples it: the tops and bottoms
    placed to a fraction of a voxel (no terraces on gentle slopes), the ground at z 0."""
    nz = int(np.ceil(zmax / h)) + 1
    zc = (np.arange(nz) + 0.5) * h
    F = np.empty(sc.H.shape + (nz,), np.float32)
    Hm = sc.H.astype(np.float32)
    sl = [(s.top.astype(np.float32), s.bot.astype(np.float32)) for s in sc.slabs]
    for k, z in enumerate(zc):
        f = np.where(Hm > 0.0, Hm - z, -h)
        for top, bot in sl:
            f = np.maximum(f, np.where(top >= 0, np.minimum(top - z, z - bot), -h))
        F[:, :, k] = np.clip(f, -h, h)
    return F


def edt(mask):
    """distance (voxels) from each voxel to the nearest voxel of `mask` (inf where there is none)."""
    if not mask.any():
        return np.full(mask.shape, np.inf, np.float32)
    return ndimage.distance_transform_edt(~mask).astype(np.float32)


def thicken(O, r):
    """grow the parts thinner than 2r (voxels): what an opening of radius r removes, away from the thick parts.  The
    build plate counts as solid (a thin plate lying on it is not a thin part: the floor rule sees to it)."""
    nb = int(np.ceil(r)) + 1
    O = np.concatenate([np.ones(O.shape[:2] + (nb,), bool), O], axis=2)
    deep = ndimage.distance_transform_edt(O) > r
    opened = edt(deep) <= r
    del deep
    T = O & ~opened
    if not T.any():
        return O[:, :, nb:], 0
    thin = T & (edt(opened) >= r)                 # beyond the corners an opening shaves off thick parts
    del opened
    if not thin.any():
        return O[:, :, nb:], 0
    thin = T & (edt(thin) <= r)                    # with the thin part's own foot back
    grow = edt(thin) <= r
    out = O | grow
    return out[:, :, nb:], int((out & ~O)[:, :, nb:].sum())


def islands(O, h):
    lab, n = ndimage.label(O)
    if n <= 1:
        return O, 0
    idx = np.arange(1, n + 1)
    size = ndimage.sum(O, lab, idx)
    zmin = ndimage.minimum(np.broadcast_to(np.arange(O.shape[2])[None, None, :], O.shape), lab, idx)
    vmin = MIN_ISLAND_MM3 / (h * S) ** 3
    drop = (size < vmin) | ((zmin > 0) & (size < 20 * vmin))
    keep = np.concatenate([[False], ~drop])
    return keep[lab], int(drop.sum())


def repaired(m):
    """MeshFix (pymeshfix): closes any hole and splits any non-manifold edge or vertex (where marching cubes or the
    decimation let two sheets touch), every piece kept; vertices in float32 as the STL stores them; normals out; the
    base on Z = 0."""
    mf = pymeshfix.MeshFix(np.asarray(m.vertices, np.float64), np.asarray(m.faces, np.int32))
    mf.repair(joincomp=False, remove_smallest_components=False)
    out = trimesh.Trimesh(np.asarray(mf.points, np.float32).astype(np.float64), np.asarray(mf.faces), process=True)
    trimesh.repair.fix_normals(out)
    out.apply_translation([0, 0, -out.bounds[0][2]])
    return out


def check(m):
    """the mesh as a slicer will read it back from the STL: watertight, consistent winding, a positive volume."""
    r = trimesh.load(trimesh.util.wrap_as_stream(m.export(file_type='stl')), file_type='stl')
    return bool(r.is_watertight and r.is_winding_consistent and r.volume > 0)


def print_mesh(model_fn, xr, yr, zmax, mk, label=''):
    t0 = time.time()
    h = H_P
    pad = 6
    xs = np.arange(xr[0] - pad * h, xr[1] + pad * h + 0.5 * h, h, dtype=np.float32)
    ys = np.arange(yr[0] - pad * h, yr[1] + pad * h + 0.5 * h, h, dtype=np.float32)
    X, Y = np.meshgrid(xs, ys)
    sc = model_fn(X, Y, **mk)
    F = field(sc, zmax + pad * h, h)
    del sc, X, Y
    O = F > 0
    r = MIN_FEATURE_MM / S / h / 2.0
    O2, grown = thicken(O, r)
    O3, dropped = islands(O2, h)
    del O2
    # the floor: whatever stands on the build plate is at least FLOOR_MM thick there (bibs and pads print as plates)
    nf = int(round(FLOOR_MM / S / h))
    base = O3[:, :, 0].copy()
    O3[:, :, 1:nf] |= base[..., None]
    # the field again: the thickened parts filled in, the dropped specks emptied
    G = O3 & ~O
    F[G] = np.maximum(F[G], 0.5 * h)
    D = O & ~O3
    if D.any():
        F[ndimage.binary_dilation(D, iterations=1) & ~O3] = -h
    del O, O3, G, D
    # marching cubes over the volume padded with empty voxels all round (closed below the base too)
    P = np.pad(F, 2, constant_values=-h)
    del F
    P = ndimage.gaussian_filter(P, 0.6)
    v, f, _, _ = measure.marching_cubes(P, 0.0, spacing=(h, h, h), allow_degenerate=False)
    del P
    y = ys[0] + v[:, 0] - 2 * h; x = xs[0] + v[:, 1] - 2 * h; z = v[:, 2] - 1.5 * h
    # to print axes: X east, Y north, Z up (mm); the mirror of y turns the winding over
    V = np.stack([x * S, -y * S, (z - z.min()) * S], 1)
    m = trimesh.Trimesh(V, f[:, ::-1], process=True)
    n_mc = len(m.faces)
    if len(m.faces) > MAX_TRIS:
        pv, fv = fast_simplification.simplify(m.vertices.astype(np.float32), m.faces.astype(np.int32),
                                              target_reduction=1 - MAX_TRIS / len(m.faces))
        m = trimesh.Trimesh(pv, fv, process=True)
    m = repaired(m)
    ok = check(m)
    if not ok:
        m = repaired(m)
        ok = check(m)
    info = dict(part=label, tris=len(m.faces), mc_tris=n_mc, watertight=bool(m.is_watertight),
                winding=bool(m.is_winding_consistent), volume_cm3=round(float(m.volume) / 1000.0, 2), ok=ok,
                bodies=int(m.body_count), size_mm=[round(float(a), 1) for a in m.extents], grown_vox=grown,
                dropped=dropped, secs=round(time.time() - t0, 1))
    return m, info


class StlGLB:
    """stands in for export3d.GLB: collects each part's print mesh, writes the STLs where the .glb would go."""
    def __init__(self):
        self.parts = []

    def mesh(self, name, v, f, *a, **k):
        self.parts.append((name, _LAST['mesh']))

    def marker(self, *a, **k):
        pass

    def camera(self, *a, **k):
        pass

    def save(self, path, extras=None):
        d = os.path.join(os.path.dirname(path), 'stl')
        os.makedirs(d, exist_ok=True)
        for name, m in self.parts:
            m.export(os.path.join(d, f'{name}.stl'))
            print('  wrote', os.path.join(d, f'{name}.stl'), flush=True)


_LAST = {}


def build_part(model_fn, mats, xr, yr, h, zmax, mk, damage=None, level=0, mat_kw=None, smooth=0.6):
    m, info = print_mesh(model_fn, xr, yr, zmax, mk, label=_LAST.get('job', ''))
    REPORT.append(info)
    _LAST['mesh'] = m
    print('  ', json.dumps(info), flush=True)
    return m.vertices, m.faces, None, None, None


JOBS = {'gdi': ('export_all.py', []), 'silo': ('export_all.py', ['silo']), 'harv': ('procexport.py', ['harvester']), 'refy': ('procexport.py', ['refinery']), 'proc': ('procexport.py', []), 'weap': ('weapexport.py', []),
        'radr': ('radrexport.py', []), 'hpad': ('hpadexport.py', []), 'dept': ('deptexport.py', ['depot']),
        'drop': ('deptexport.py', ['drop']), 'plug': ('plugexport.py', []), 'puls': ('pulsexport.py', []),
        'dpsa': ('dpsaexport.py', []), 'dweap': ('dweapexport.py', []), 'fgen': ('fgenexport.py', []), 'fsdf': ('fsdfexport.py', []),
        'dlimp': ('dlimpexport.py', [])}

if __name__ == '__main__':
    E.build_part = build_part
    E.GLB = StlGLB
    for job in sys.argv[1:]:
        script, args = JOBS[job]
        _LAST['job'] = job
        t0 = time.time()
        print('JOB', job, flush=True)
        old = sys.argv
        sys.argv = [script] + args
        try:
            runpy.run_path(script, run_name='__main__')
        except SystemExit:
            pass
        except Exception as e:
            import traceback; traceback.print_exc()
            print('FAILED', job, e, flush=True)
        sys.argv = old
        print('JOB-DONE', job, '%.0fs' % (time.time() - t0), flush=True)
    json.dump(REPORT, open(f'/home/claude/work/scratch/stl/report-{"-".join(sys.argv[1:])}.json', 'w'), indent=1)
