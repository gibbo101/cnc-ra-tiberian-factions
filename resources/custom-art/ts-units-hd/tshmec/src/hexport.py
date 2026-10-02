"""
hexport.py - the Mammoth Mk. II's 3D model as a .glb: one node per voxel section (body, and each leg's upper leg,
lower leg and foot), the meshes exact (each section's boxes, cut along its convex edges), subdivided so the vertex
colours carry TS's own colours, house colour on the remap voxels; the walk as an animation ("walk": the mod's 8
steps, HVA frames 0,2,4,6,8,11,13,15, 8 ticks each, looping); the camera the mod's frames use (35 degrees) framing
the 576 canvas.

Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
Origin: the unit's position on the ground.  The unit faces east (the mod's facing 24).

    python3 hexport.py out.glb
"""
import sys, json, struct
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from export3d import GLB, orient
import rcexport as RX
import voxrender as VR
import hrender as HR

UNITS_PER_CELL = 192.0 / HR.PPU
A = np.array([[1, 0, 0], [0, 0, 1.0], [0, 1.0, 0]])      # model (x east, y south, z up) -> glTF (x east, y up, z south)
STEP_S = 8 / 15.0


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


def section_mesh(s):
    """the section's boxes as one mesh in its local space (min + index * scale), with TS's colours."""
    Ps, Fs, Ns = [], [], []
    off = 0
    for p in s.parts(np.eye(3), np.zeros(3), 0):
        m = RX.part_mesh(p)
        if m is None:
            continue
        V, F = m
        P, Fi, N = RX.flat_shaded(V, F)
        P, Fi, N = subdivide(P, Fi, N, 1.0)
        Ps.append(P); Fs.append(Fi + off); Ns.append(N); off += len(P)
    P = np.concatenate(Ps); F = np.concatenate(Fs); N = np.concatenate(Ns)
    I = s.to_index(P, np.eye(3), np.zeros(3))
    nI = N * s.scale[None, :]
    rgb, wc, wh, lm = s.sample(I, nI, sharp=2.0)
    lum = rgb.mean(1)
    k = np.clip(lum, 0.75 * lm, 1.2 * lm) / np.maximum(lum, 1e-3)
    keep = (lum < 70) | (lum > 205)
    rgb = rgb * np.where((wc > 0.3) & ~keep, k, 1.0)[:, None]
    alb = np.minimum(rgb * VR.GAIN, VR.WHITE_CAP)
    house = np.clip((wh - 0.35) / 0.3, 0, 1)
    alb = alb * (1 - house[:, None]) + VR.GREEN[None, :] * house[:, None]
    return P, F, N, alb, house


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


class AnimGLB(GLB):
    def __init__(self):
        super().__init__(); self.children = {}; self.anims = {}

    def node(self, name, parent=None, translation=(0, 0, 0), rotation=(0, 0, 0, 1), mesh=None):
        nd = dict(name=name, translation=[float(v) for v in translation], rotation=[float(v) for v in rotation])
        if mesh is not None:
            v, f, n, rgb, house = mesh
            self.mesh(name, v, f, n, rgb, house)
            nd['mesh'] = self.nodes.pop()['mesh']
        self.nodes.append(nd)
        i = len(self.nodes) - 1
        if parent is not None:
            self.children.setdefault(parent, []).append(i)
        return i

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
        gl = dict(asset=dict(version='2.0', generator='TS-to-RA HD (vxlunit)'), scene=0,
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


def export(path):
    unit = HR.load()
    glb = AnimGLB()
    root = glb.node('MammothMk2')
    Mx = VR.facing_cw(VR.mod_to_cw(24))                     # unit frame -> world, facing east
    # the unit's own frame (x forward, y left, z up) is right-handed like glTF's: the facing node takes it straight
    # to glTF's axes (A Mx), and the sections and their meshes stay in the unit's frame
    face = glb.node('unit_facing_east', root, rotation=quat(A @ Mx))
    times = [i * STEP_S for i in range(9)]
    for i, s in enumerate(unit.sections):
        P, F, N, alb, house = section_mesh(s)
        Pg = P / UNITS_PER_CELL; Ng = N
        F = orient(Pg, F, Ng)
        poses = [unit.pose(i, HR.STEPS[k % 8]) for k in range(9)]
        tr = [t / UNITS_PER_CELL for R, t in poses]
        ro = [quat(orthonormal(R)) for R, t in poses]
        for k in range(1, 9):
            if np.dot(ro[k], ro[k - 1]) < 0:
                ro[k] = -ro[k]
        nd = glb.node(s.name.lower().replace(' ', '_'), face, translation=tr[0], rotation=ro[0],
                      mesh=(Pg.astype(np.float32), F, Ng.astype(np.float32), alb, house))
        glb.animate('walk', nd, times, tr, ro)
    cam = HR.camera()
    gx, gy = cam.ground(np.array([288.0]), np.array([288.0]))
    glb.camera('camera_mod', 0.0, HR.ELEV, list(A @ np.array([gx[0], gy[0], 0.0]) / UNITS_PER_CELL), 1.5, 1.5,
               extras=dict(note='orthographic, %g degrees above the ground, looking north; frames the 576 x 576 canvas'
                           % HR.ELEV))
    glb.save(path, extras=dict(units='1.0 = one cell (128 px in the game; 192 px on the canvas)', facing='east',
                               walk='8 steps, %.3f s each (8 ticks)' % STEP_S))
    return path


if __name__ == '__main__':
    print(export(sys.argv[1]))
