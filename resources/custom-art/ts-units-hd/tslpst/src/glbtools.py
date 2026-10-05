"""glbtools.py - the .glb writer with node groups and animations (from the Mammoth Mk. II's hmec2export.py): AnimGLB,
quat (a rotation matrix as a glTF quaternion), orthonormal, subdivide (split a mesh's triangles so vertex colours can
change across a face)."""
import sys, json, struct
from paths import HANDOFF
sys.path.insert(0, HANDOFF + '/renderer')
import numpy as np
from export3d import GLB


def quat(Rg):
    t = np.trace(Rg)
    if t > 0:
        q = np.array([Rg[2, 1] - Rg[1, 2], Rg[0, 2] - Rg[2, 0], Rg[1, 0] - Rg[0, 1], t + 1.0])
    else:
        i = int(np.argmax(np.diag(Rg))); j, k = (i + 1) % 3, (i + 2) % 3
        q = np.zeros(4); q[i] = Rg[i, i] - Rg[j, j] - Rg[k, k] + 1.0
        q[j] = Rg[j, i] + Rg[i, j]; q[k] = Rg[k, i] + Rg[i, k]; q[3] = Rg[k, j] - Rg[j, k]
    return q / np.linalg.norm(q)


def orthonormal(R):
    U, _, Vt = np.linalg.svd(R)
    return U @ Vt


def subdivide(P, F, N, max_len=1.0):
    t = P[F]; n = N[F[:, 0]]
    done_t, done_n = [], []
    while len(t):
        L = np.stack([np.linalg.norm(t[:, 1] - t[:, 0], axis=1), np.linalg.norm(t[:, 2] - t[:, 1], axis=1),
                      np.linalg.norm(t[:, 0] - t[:, 2], axis=1)], 1)
        k = L.argmax(1); ok = L.max(1) <= max_len
        done_t.append(t[ok]); done_n.append(n[ok])
        t, n, k = t[~ok], n[~ok], k[~ok]
        if not len(t):
            break
        idx = np.stack([k, (k + 1) % 3, (k + 2) % 3], 1)
        r = np.take_along_axis(t, idx[:, :, None], 1)
        a, b, c = r[:, 0], r[:, 1], r[:, 2]; m = (a + b) / 2
        t = np.concatenate([np.stack([a, m, c], 1), np.stack([m, b, c], 1)], 0); n = np.concatenate([n, n], 0)
    T = np.concatenate(done_t, 0); Nn = np.concatenate(done_n, 0)
    V = T.reshape(-1, 3); NV = np.repeat(Nn, 3, axis=0)
    key = np.concatenate([np.round(V * 1e4), np.round(NV * 1e3)], 1).astype(np.int64)
    uk, inv = np.unique(key, axis=0, return_inverse=True)
    first = np.zeros(len(uk), int); first[inv[::-1]] = np.arange(len(V))[::-1]
    return V[first], inv.reshape(-1, 3), NV[first]


class AnimGLB(GLB):
    def __init__(self):
        super().__init__(); self.children = {}; self.anims = {}

    def group(self, name, parent=None, translation=(0, 0, 0), rotation=(0, 0, 0, 1)):
        self.nodes.append(dict(name=name, translation=[float(v) for v in translation],
                               rotation=[float(v) for v in rotation]))
        i = len(self.nodes) - 1
        if parent is not None:
            self.children.setdefault(parent, []).append(i)
        return i

    def part(self, name, parent, v, f, n, rgb, house):
        self.mesh(name, v, f, n, rgb, house)
        i = len(self.nodes) - 1
        self.children.setdefault(parent, []).append(i)

    def animate(self, anim, node, times, trans, rots):
        a = self.anims.setdefault(anim, dict(name=anim, samplers=[], channels=[]))
        t_acc = self._add(np.asarray(times, np.float32).reshape(-1, 1), None, 5126, 'SCALAR', minmax=True)
        tr = self._add(np.asarray(trans, np.float32), None, 5126, 'VEC3')
        ro = self._add(np.asarray(rots, np.float32), None, 5126, 'VEC4')
        s0 = len(a['samplers'])
        a['samplers'] += [dict(input=t_acc, output=tr, interpolation='LINEAR'),
                          dict(input=t_acc, output=ro, interpolation='LINEAR')]
        a['channels'] += [dict(sampler=s0, target=dict(node=node, path='translation')),
                          dict(sampler=s0 + 1, target=dict(node=node, path='rotation'))]

    def save(self, path, extras=None):
        for p, ch in self.children.items():
            self.nodes[p]['children'] = ch
        child = {c for ch in self.children.values() for c in ch}
        roots = [i for i in range(len(self.nodes)) if i not in child]
        while len(self.buf) % 4:
            self.buf.append(0)
        gl = dict(asset=dict(version='2.0', generator='TS-to-RA HD (rcexport)'), scene=0,
                  scenes=[dict(nodes=roots, extras=extras or {})], nodes=self.nodes, meshes=self.meshes,
                  materials=self.materials, accessors=self.accessors, bufferViews=self.views,
                  buffers=[dict(byteLength=len(self.buf))])
        if self.anims:
            gl['animations'] = list(self.anims.values())
        if getattr(self, 'cameras', None):
            gl['cameras'] = self.cameras
        js = json.dumps(gl, separators=(',', ':')).encode()
        while len(js) % 4:
            js += b' '
        out = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(self.buf))
        out += struct.pack('<II', len(js), 0x4E4F534A) + js
        out += struct.pack('<II', len(self.buf), 0x004E4942) + bytes(self.buf)
        open(path, 'wb').write(out)
