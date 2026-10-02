"""Export a building (or unit) model as a 3D mesh: a .glb (glTF 2.0) with vertex colours.

The models are heightfields plus slabs, defined as functions over the ground (hd.Scene).  For a mesh, the scene is
sampled on a grid (h units apart), turned into a solid (inside where z < H, or bot <= z <= top in any slab) as a
truncated distance field, smoothed a touch, and its surface taken by marching cubes: walls come out vertical and
subdivided, slopes smooth.  Every vertex is then coloured by the building's own materials (albedo only: no light,
shadow or outline) and, for the damaged state, its damage; a second colour set marks house colour (COLOR_1: white =
house colour, like the -trim masks).

Axes: glTF's own (y up, right-handed): x = east, y = up, z = south (toward the RA camera).  Scale: 1 cell = 1.0
(1 m in glTF terms) = 128 units = 128 px on the RA grid.  The origin is the model's own (a building: the centre of its
foundation, on the ground; a unit: its position)."""
import json, struct
import numpy as np
from scipy import ndimage
from skimage import measure
import hd

CELL = 128.0


class FakeView:
    """the RA camera's light and direction, for the few materials that read them (highlights)."""
    def __init__(self):
        v = hd.ra_view((64, 64), (32, 32), ss=1)
        self.L, self.T, self.cE, self.sE = v.L, v.T, v.cE, v.sE


class FakeRender:
    """what a materials function reads off an hd.Render, for a list of mesh vertices."""
    def __init__(self, x, y, z, n, comp, surface, fields, mk):
        self.x, self.y, self.z = x.astype(np.float32), y.astype(np.float32), z.astype(np.float32)
        self.nx, self.ny, self.nz = n[:, 0].astype(np.float32), n[:, 1].astype(np.float32), n[:, 2].astype(np.float32)
        self.comp = comp.astype(np.int16)
        self.surface = surface.astype(np.int8)
        self.hitmask = np.ones(len(x), bool)
        self._f = fields
        self.mk = mk
        self.view = FakeView()

    def field(self, name, default=0.0):
        f = self._f.get(name)
        return np.full(self.x.shape, default, np.float32) if f is None else f


def sample(model_fn, xr, yr, h, **mk):
    xs = np.arange(xr[0], xr[1] + 0.5 * h, h, dtype=np.float32)
    ys = np.arange(yr[0], yr[1] + 0.5 * h, h, dtype=np.float32)
    X, Y = np.meshgrid(xs, ys)
    return xs, ys, X, Y, model_fn(X, Y, **mk)


def solid_mesh(sc, xs, ys, h, zmax, smooth=0.6):
    """marching cubes over the scene's solid: vertices (x, y, z model units), faces, normals, and which part each
    vertex is on (-1 the heightfield, k the k-th slab) with its surface (0 field, 1 slab top, 2 bottom, 3 side)."""
    nz = int(np.ceil(zmax / h)) + 3
    zs = (np.arange(nz, dtype=np.float32) - 1) * h
    H = sc.H.astype(np.float32)
    F = np.empty((len(ys), len(xs), nz), np.float32)
    for k, z in enumerate(zs):
        f = np.where(H > 0.0, H - z, -h)                       # inside the heightfield's columns
        for s in sc.slabs:
            ins = s.top >= 0
            fs = np.where(ins, np.minimum(s.top - z, z - s.bot), -h)
            f = np.maximum(f, fs)
        F[:, :, k] = np.clip(f, -h, h)
    # the ground plane closes the model from below
    F[:, :, 0] = -h
    if smooth:
        F = ndimage.gaussian_filter(F, smooth)
    verts, faces, normals, _ = measure.marching_cubes(F, level=0.0, spacing=(h, h, h), allow_degenerate=False)
    y = ys[0] + verts[:, 0]; x = xs[0] + verts[:, 1]; z = zs[0] + verts[:, 2]
    # skimage's normals point down the field (outwards: it is positive inside); reorder to (x, y, z)
    n = np.stack([normals[:, 1], normals[:, 0], normals[:, 2]], axis=1)
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    # which part each vertex is on: the one whose surface is nearest
    i = np.clip(np.round((y - ys[0]) / h).astype(int), 0, len(ys) - 1)
    j = np.clip(np.round((x - xs[0]) / h).astype(int), 0, len(xs) - 1)
    best = np.abs(np.where(H[i, j] > 0, H[i, j] - z, 1e9))
    part = np.full(len(x), -1, np.int32)
    surf = np.zeros(len(x), np.int8)
    comp = sc.C[i, j].astype(np.int16)
    # a wall foot on the ground: take the part of the tallest neighbour (as the renderer's skirt does)
    Hn = ndimage.maximum_filter(H, size=3)
    for k, s in enumerate(sc.slabs):
        ins = s.top[i, j] >= 0
        dt, db = np.abs(s.top[i, j] - z), np.abs(z - s.bot[i, j])
        d = np.where(ins, np.minimum(dt, db), 1e9)
        # a slab's side: the vertex sits between its top and bottom, near the edge of its footprint
        side = ins & (z > s.bot[i, j] + 0.5 * h) & (z < s.top[i, j] - 0.5 * h)
        d = np.where(side, 0.0, d)
        win = d < best
        best = np.where(win, d, best)
        part = np.where(win, k, part)
        comp = np.where(win, s.comp[i, j], comp)
        surf = np.where(win, np.where(side, 3, np.where(dt <= db, 1, 2)), surf)
    # vertices where the nearest sample is outside every part (on a wall's outer face): borrow the neighbourhood's
    lost = comp <= 0
    if lost.any():
        Cn = ndimage.grey_dilation(np.where(H > 0, sc.C, 0).astype(np.int32), size=3)
        comp = np.where(lost, Cn[i, j], comp)
        for k, s in enumerate(sc.slabs):
            cs = ndimage.grey_dilation(np.where(s.top >= 0, s.comp, 0).astype(np.int32), size=3)
            take = lost & (comp <= 0) & (cs[i, j] > 0)
            comp = np.where(take, cs[i, j], comp); surf = np.where(take, 3, surf)
    return np.stack([x, y, z], 1), faces.astype(np.uint32), n, comp, surf, (i, j)


def colours(sc, verts, n, comp, surf, ij, mats, mk, damage=None, level=0, mat_kw=None):
    i, j = ij
    fields = {k: (v[i, j] if isinstance(v, np.ndarray) else v) for k, v in sc.extra.items()}
    r = FakeRender(verts[:, 0], verts[:, 1], verts[:, 2], n, comp, surf, fields, mk)
    alb, _, _ = mats.materials(r, occ=None, **(mat_kw or {}))
    if damage is not None and level:
        alb = damage.mats(r, alb, level)
    house = mats.trim_mask(r, alb).astype(np.float32)
    return np.clip(alb, 0, 255), house


def to_gltf(verts, n):
    """model axes (x east, y south, z up; units) -> glTF (x east, y up, z south; cells)."""
    v = np.stack([verts[:, 0], verts[:, 2], verts[:, 1]], 1) / CELL
    nn = np.stack([n[:, 0], n[:, 2], n[:, 1]], 1)
    return v.astype(np.float32), nn.astype(np.float32)


def orient(v, faces, nn):
    """wind every triangle counter-clockwise seen from outside (its normal along the vertex normals)."""
    a, b, c = v[faces[:, 0]], v[faces[:, 1]], v[faces[:, 2]]
    fn = np.cross(b - a, c - a)
    vn = nn[faces[:, 0]] + nn[faces[:, 1]] + nn[faces[:, 2]]
    flip = (fn * vn).sum(1) < 0
    f = faces.copy()
    f[flip] = f[flip][:, [0, 2, 1]]
    return f


class GLB:
    """a minimal glTF 2.0 binary writer: meshes with POSITION, NORMAL, COLOR_0 (albedo), COLOR_1 (house colour),
    and empty marker nodes."""
    def __init__(self):
        self.buf = bytearray()
        self.views, self.accessors, self.meshes, self.nodes = [], [], [], []
        self.materials = [dict(name='vertex colour', pbrMetallicRoughness=dict(baseColorFactor=[1, 1, 1, 1],
                                                                            metallicFactor=0.0, roughnessFactor=0.85))]

    def _add(self, arr, target, comp_type, typ, normalized=False, minmax=False):
        data = np.ascontiguousarray(arr).tobytes()
        while len(self.buf) % 4:
            self.buf.append(0)
        off = len(self.buf)
        self.buf.extend(data)
        bv = dict(buffer=0, byteOffset=off, byteLength=len(data))
        if target:
            bv['target'] = target
        self.views.append(bv)
        acc = dict(bufferView=len(self.views) - 1, componentType=comp_type, count=int(arr.shape[0]), type=typ)
        if normalized:
            acc['normalized'] = True
        if minmax:
            acc['min'] = [float(x) for x in arr.min(0)]; acc['max'] = [float(x) for x in arr.max(0)]
        self.accessors.append(acc)
        return len(self.accessors) - 1

    def mesh(self, name, v, faces, nn, rgb, house, translation=(0, 0, 0)):
        pos = self._add(v.astype(np.float32), 34962, 5126, 'VEC3', minmax=True)
        nor = self._add(nn.astype(np.float32), 34962, 5126, 'VEC3')
        c0 = np.concatenate([np.clip(rgb, 0, 255), np.full((len(v), 1), 255.0)], 1).round().astype(np.uint8)
        col = self._add(c0, 34962, 5121, 'VEC4', normalized=True)
        hv = (np.clip(house, 0, 1) * 255).round().astype(np.uint8)
        c1 = np.stack([hv, hv, hv, np.full(len(v), 255, np.uint8)], 1)
        col1 = self._add(c1, 34962, 5121, 'VEC4', normalized=True)
        idx = self._add(faces.astype(np.uint32).reshape(-1), 34963, 5125, 'SCALAR')
        self.meshes.append(dict(name=name, primitives=[dict(attributes=dict(POSITION=pos, NORMAL=nor, COLOR_0=col,
                                                                          COLOR_1=col1),
                                                         indices=idx, material=0)]))
        self.nodes.append(dict(name=name, mesh=len(self.meshes) - 1, translation=[float(t) for t in translation]))

    def marker(self, name, translation, yaw_deg=0.0, extras=None):
        """an empty node: a point of interest (in cells, glTF axes); yaw about the up axis, counter-clockwise seen
        from above, 0 = facing east (+x)."""
        a = np.deg2rad(yaw_deg) / 2.0
        node = dict(name=name, translation=[float(t) for t in translation], rotation=[0.0, float(np.sin(a)), 0.0, float(np.cos(a))])
        if extras:
            node['extras'] = extras
        self.nodes.append(node)

    def camera(self, name, look_deg, elev_deg, target, xmag, ymag, extras=None):
        """an orthographic camera node (glTF looks down its local -z): looking toward compass bearing look_deg
        (0 = north, 90 = east, 315 = north-west), elev_deg above the ground, through `target` (cells, glTF axes), its
        view xmag x ymag cells either side of the centre."""
        if not hasattr(self, 'cameras'):
            self.cameras = []
        b_, e = np.deg2rad(look_deg), np.deg2rad(elev_deg)
        horiz = np.array([np.sin(b_), 0.0, -np.cos(b_)])          # north = -z, east = +x
        d = horiz * np.cos(e) + np.array([0.0, -np.sin(e), 0.0])     # the view direction
        up = horiz * np.sin(e) + np.array([0.0, np.cos(e), 0.0])
        zl = -d; yl = up; xl = np.cross(yl, zl)
        R = np.stack([xl, yl, zl], 1)
        # rotation matrix -> quaternion (x, y, z, w)
        t = np.trace(R)
        if t > 0:
            q = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1], t + 1.0])
        else:
            i = int(np.argmax(np.diag(R))); j, k = (i + 1) % 3, (i + 2) % 3
            q = np.zeros(4); q[i] = R[i, i] - R[j, j] - R[k, k] + 1.0
            q[j] = R[j, i] + R[i, j]; q[k] = R[k, i] + R[i, k]; q[3] = R[k, j] - R[j, k]
        q = q / np.linalg.norm(q)
        pos = np.asarray(target, float) - d * 40.0
        self.cameras.append(dict(name=name, type='orthographic',
                                 orthographic=dict(xmag=float(xmag), ymag=float(ymag), znear=0.1, zfar=100.0)))
        node = dict(name=name, camera=len(self.cameras) - 1, translation=[float(v) for v in pos],
                    rotation=[float(v) for v in q])
        if extras:
            node['extras'] = extras
        self.nodes.append(node)

    def save(self, path, extras=None):
        while len(self.buf) % 4:
            self.buf.append(0)
        gl = dict(asset=dict(version='2.0', generator='TS-to-RA HD (hd.py export3d)'),
                  scene=0, scenes=[dict(nodes=list(range(len(self.nodes))))], nodes=self.nodes, meshes=self.meshes,
                  materials=self.materials, accessors=self.accessors, bufferViews=self.views,
                  buffers=[dict(byteLength=len(self.buf))])
        if extras:
            gl['scenes'][0]['extras'] = extras
        if getattr(self, 'cameras', None):
            gl['cameras'] = self.cameras
        js = json.dumps(gl, separators=(',', ':')).encode()
        while len(js) % 4:
            js += b' '
        out = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(self.buf))
        out += struct.pack('<II', len(js), 0x4E4F534A) + js
        out += struct.pack('<II', len(self.buf), 0x004E4942) + bytes(self.buf)
        open(path, 'wb').write(out)


def build_part(model_fn, mats, xr, yr, h, zmax, mk, damage=None, level=0, mat_kw=None, smooth=0.6):
    """one model (as the renderer sees it) -> glTF-ready arrays."""
    xs, ys, X, Y, sc = sample(model_fn, xr, yr, h, **mk)
    verts, faces, n, comp, surf, ij = solid_mesh(sc, xs, ys, h, zmax, smooth)
    rgb, house = colours(sc, verts, n, comp, surf, ij, mats, mk, damage, level, mat_kw)
    v, nn = to_gltf(verts, n)
    return v, orient(v, faces, nn), nn, rgb, house
