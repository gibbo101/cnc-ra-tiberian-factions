"""
mcvexport.py - the MCV's 3D model as a .glb: every part as a node under the unit (facing east, the mod's frame 24),
the meshes exact (each convex part cut from its planes), subdivided so the vertex colours carry TS's own colours
(the same colour field the frames use: ochre and orange where TS has them, the boom's grey bands, the dark track),
house colour on the covers and panels, and the RA-grid camera that frames the mod's 384 canvas.

Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
Origin: the unit's position on the ground.

    python3 mcvexport.py out.glb
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from export3d import GLB, orient
import rcexport as RX
import mcv as M, mcvmat as MM, tsfield as TF
from mcvrender import facing_cw, mod_to_cw, camera, PPU

UNITS_PER_CELL = 192.0 / PPU                # voxels per cell: the MCV's canvas has 192 px a cell, 6.1 px a voxel
A = np.array([[1, 0, 0], [0, 0, 1.0], [0, 1.0, 0]])      # model (x east, y south, z up) -> glTF (x east, y up, z south)
GROUPS = {'cover': 'tracks', 'track': 'tracks', 'tbit': 'tracks', 'under': 'hull', 'hull': 'hull', 'bumper': 'hull',
          'deck': 'right_deck', 'rim': 'right_deck', 'rail_r': 'right_deck', 'spine': 'right_deck',
          'block': 'right_deck', 'post': 'right_deck', 'panel': 'right_deck', 'cab': 'cab', 'cabfront': 'cab',
          'channel': 'crane', 'plate': 'crane', 'saddle': 'crane', 'band': 'crane', 'boom': 'crane',
          'cradle': 'crane', 'leftdeck': 'left_deck', 'shelf': 'left_deck', 'crate': 'left_deck',
          'divider': 'left_deck', 'rail_l': 'left_deck', 'fl_base': 'left_deck', 'fl_block': 'left_deck',
          'fl_top': 'left_deck', 'coupling': 'hitch', 'ring': 'hitch', 'hitch': 'hitch'}


def subdivide(P, F, N, max_len=0.75):
    """split flat-shaded triangles (per-face vertices) at the midpoint of their longest edge until no edge is longer
    than max_len (voxels): the vertex colours then follow TS's colours across each face."""
    t = P[F]
    n = N[F[:, 0]]
    done_t, done_n = [], []
    while len(t):
        L = np.stack([np.linalg.norm(t[:, 1] - t[:, 0], axis=1), np.linalg.norm(t[:, 2] - t[:, 1], axis=1),
                      np.linalg.norm(t[:, 0] - t[:, 2], axis=1)], 1)
        k = L.argmax(1)
        ok = L.max(1) <= max_len
        done_t.append(t[ok]); done_n.append(n[ok])
        t, n, k = t[~ok], n[~ok], k[~ok]
        if not len(t):
            break
        # rotate each triangle so its longest edge is v0-v1, then split it at that edge's midpoint
        idx = np.stack([k, (k + 1) % 3, (k + 2) % 3], 1)
        r = np.take_along_axis(t, idx[:, :, None], 1)
        a, b, c = r[:, 0], r[:, 1], r[:, 2]
        m = (a + b) / 2
        t = np.concatenate([np.stack([a, m, c], 1), np.stack([m, b, c], 1)], 0)
        n = np.concatenate([n, n], 0)
    T = np.concatenate(done_t, 0); Nn = np.concatenate(done_n, 0)
    V = T.reshape(-1, 3); NV = np.repeat(Nn, 3, axis=0)
    # share the vertices a face's triangles have in common (same place, same face normal)
    key = np.concatenate([np.round(V * 1e4), np.round(NV * 1e3)], 1).astype(np.int64)
    uk, inv = np.unique(key, axis=0, return_inverse=True)
    first = np.zeros(len(uk), int); first[inv[::-1]] = np.arange(len(V))[::-1]
    return V[first], inv.reshape(-1, 3), NV[first]


def colours(part, V, N):
    """vertex colours (body frame V, N): TS's colours as the frames have them, house green on house parts."""
    if part.comp in M.HOUSE:
        return np.tile(MM.GREEN, (len(V), 1)), np.ones(len(V))
    x = V[:, 0] + M.CX; y = M.CY - V[:, 1]; z = V[:, 2]
    s = MM.SHARP.get(part.comp, 1.0)
    rgb, w = TF.sample(x, y, z, N[:, 0], -N[:, 1], N[:, 2], sharp=s)
    fb = np.asarray(MM.FALLBACK.get(part.comp, MM.GOLD), float)
    base = rgb * w[:, None] + fb * (1 - w[:, None])
    if part.comp in MM.PAINTED and (w > 0.3).sum() >= 4:
        lum = base.mean(1); mu = lum[w > 0.3].mean()
        k = np.clip(lum, 0.62 * mu, 1.28 * mu) / np.maximum(lum, 1e-3)
        base = base * k[:, None]
    base = np.minimum(base * MM.GAIN, 236.0)
    if part.comp in (M.HULL, M.UNDER, M.BUMPER):
        d = np.clip((3.6 - z) / 3.0, 0, 1) * 0.4
        base = base * (1 - d[:, None]) + MM.GRIME * d[:, None]
    return base, np.zeros(len(V))


def to_g_pos(p):
    return A @ np.asarray(p, float) / UNITS_PER_CELL


def quat(Rg):
    t = np.trace(Rg)
    if t > 0:
        q = np.array([Rg[2, 1] - Rg[1, 2], Rg[0, 2] - Rg[2, 0], Rg[1, 0] - Rg[0, 1], t + 1.0])
    else:
        i = int(np.argmax(np.diag(Rg))); j, k = (i + 1) % 3, (i + 2) % 3
        q = np.zeros(4); q[i] = Rg[i, i] - Rg[j, j] - Rg[k, k] + 1.0
        q[j] = Rg[j, i] + Rg[i, j]; q[k] = Rg[k, i] + Rg[i, k]; q[3] = Rg[k, j] - Rg[j, k]
    return q / np.linalg.norm(q)


class Tree(GLB):
    def __init__(self):
        super().__init__()
        self.children = {}

    def group(self, name, parent=None, rotation=(0, 0, 0, 1)):
        self.nodes.append(dict(name=name, rotation=[float(v) for v in rotation]))
        i = len(self.nodes) - 1
        if parent is not None:
            self.children.setdefault(parent, []).append(i)
        return i

    def part(self, name, parent, v, f, n, rgb, house):
        self.mesh(name, v, f, n, rgb, house)
        i = len(self.nodes) - 1
        self.children.setdefault(parent, []).append(i)

    def finish(self):
        for p, ch in self.children.items():
            self.nodes[p]['children'] = ch

    def save(self, path, extras=None):
        import json, struct
        child = {c for ch in self.children.values() for c in ch}
        roots = [i for i in range(len(self.nodes)) if i not in child]
        while len(self.buf) % 4:
            self.buf.append(0)
        gl = dict(asset=dict(version='2.0', generator='TS-to-RA HD (rcexport)'), scene=0,
                  scenes=[dict(nodes=roots, extras=extras or {})], nodes=self.nodes, meshes=self.meshes,
                  materials=self.materials, accessors=self.accessors, bufferViews=self.views,
                  buffers=[dict(byteLength=len(self.buf))])
        if getattr(self, 'cameras', None):
            gl['cameras'] = self.cameras
        js = json.dumps(gl, separators=(',', ':')).encode()
        while len(js) % 4:
            js += b' '
        out = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(self.buf))
        out += struct.pack('<II', len(js), 0x4E4F534A) + js
        out += struct.pack('<II', len(self.buf), 0x004E4942) + bytes(self.buf)
        open(path, 'wb').write(out)


def export(path):
    glb = Tree()
    root = glb.group('MCV')
    Mx = facing_cw(mod_to_cw(24))                           # facing east
    Rg = A @ Mx @ A.T
    unit = glb.group('unit_facing_east', root, rotation=quat(Rg))
    groups = {}
    seen = {}
    nverts = 0
    for p in M.parts():
        m = RX.part_mesh(p)
        if m is None:
            continue
        V, F = m
        P, Fi, N = RX.flat_shaded(V, F)
        P, Fi, N = subdivide(P, Fi, N, 1.0)
        rgb, house = colours(p, P, N)
        Pg = (P @ A.T) / UNITS_PER_CELL; Ng = N @ A.T
        Fi = orient(Pg, Fi, Ng)
        g = GROUPS.get(p.name, 'other')
        if g not in groups:
            groups[g] = glb.group(g, unit)
        seen[p.name] = seen.get(p.name, 0) + 1
        nm = p.name if seen[p.name] == 1 else '%s_%d' % (p.name, seen[p.name])
        glb.part(nm, groups[g], Pg.astype(np.float32), Fi, Ng.astype(np.float32), rgb, house)
        nverts += len(Pg)
    glb.finish()
    cam = camera()
    gx, gy = cam.ground(np.array([192.0]), np.array([192.0]))
    glb.camera('camera_ra_grid', 0.0, 32.0, list(to_g_pos([gx[0], gy[0], 0.0])), 1.0, 1.0,
               extras=dict(note='orthographic, 32 degrees above the ground, looking north; frames the 384 x 384 canvas'))
    glb.save(path, extras=dict(units='1.0 = one cell (128 px in the game; 192 px on the canvas)', facing='east'))
    return path, nverts


if __name__ == '__main__':
    print(export(sys.argv[1]))
