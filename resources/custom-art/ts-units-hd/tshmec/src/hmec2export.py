"""
hmec2export.py - the Mammoth Mk. II v2's 3D model as a .glb: one node per TS section (the body; each leg's thigh,
shin and foot) under the unit (facing east, the mod's facing 24), each holding its parts' meshes (exact: each convex
part cut from its planes and curved surfaces) in the section's own frame; the walk as an animation ("walk": the mod's
8 steps, TS's HVA frames 0, 2, 4, 6, 8, 11, 13, 15, 8 ticks each, looping); vertex colours the frames' paint (house
colour on the pods, mounts, front hip covers and front guards: COLOR_1 white); the camera the mod's frames use (35
degrees) framing the 576 canvas.

Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
Origin: the unit's position on the ground.

    python3 hmec2export.py out.glb
"""
import sys, json, struct
from paths import HANDOFF
sys.path.insert(0, HANDOFF + '/renderer')
import numpy as np
from export3d import GLB, orient
import rcexport as RX
import hmec2 as H, hmec2mat as MM
from hmec2cam import unit_to_world, camera, PPU, ELEV

UNITS_PER_CELL = 192.0 / PPU                # unit-frame units per cell: 192 canvas px a cell, 6.8 px a unit
A = np.array([[1, 0, 0], [0, 0, 1.0], [0, 1.0, 0]])      # world (x east, y south, z up) -> glTF (x east, y up, z south)
STEP_S = 8 / 15.0
SEC_NAMES = ['foot_right_rear', 'shin_right_rear', 'thigh_right_rear', 'foot_right_front', 'shin_right_front',
             'thigh_right_front', 'foot_left_rear', 'shin_left_rear', 'thigh_left_rear', 'foot_left_front',
             'shin_left_front', 'thigh_left_front', 'body']


def colours(sec, part, V, N):
    """vertex colours (the section's local frame V, N): the frames' paint for the part (albedo, no light), house
    green on house parts."""
    if part.comp in H.HOUSE:
        return np.tile(MM.GREEN, (len(V), 1)), np.ones(len(V))
    base = np.tile(np.asarray(MM.PAINT.get(part.comp, MM.OCHRE), float), (len(V), 1))
    F = H.FR[sec]
    q = (V - F.mn) / F.sc
    if part.comp == H.RAIL:
        base[N[:, 2] > 0.6] = MM.WHITE
    elif part.comp in (H.MUZZLE, H.VISOR):
        # the front's two bays: the lit window band along the top of each visor plate and up the back wall
        base[:] = MM.STEEL_D if part.comp == H.MUZZLE else MM.OCHRE
        for zb, zt in H.FRONT_BAYS:
            ztop = zt - 0.75
            if part.comp == H.VISOR:
                band = (N[:, 0] > 0.3) & (q[:, 2] > ztop - 1.1) & (q[:, 2] < ztop + 0.05)
            else:
                band = (N[:, 0] > 0.7) & (q[:, 2] > ztop - 0.1) & (q[:, 2] < zt + 0.05)
            t = np.clip((q[:, 2] - (ztop - 1.1)) / 1.15, 0, 1)
            base[band] = (MM.GLASS_LO * (1 - t)[:, None] + MM.GLASS_HI * t[:, None])[band]
    elif part.comp == H.THIGH:
        for name, (u_, l_, f_, left) in H.LEGS.items():
            if u_ == sec:
                kx, ky, kz = H.J[name]['knee_t']
                base[np.hypot(q[:, 0] - kx, q[:, 2] - kz) < 3.1] = MM.OCHRE_D
    return np.minimum(base, 255.0), np.zeros(len(V))


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


VARIED = (H.MUZZLE, H.VISOR, H.THIGH)       # parts whose paint changes across a face: subdivided


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


def export(path):
    m = H.model()
    glb = AnimGLB()
    root = glb.group('MammothMk2')
    Mx = unit_to_world(24)                                  # unit frame -> world, facing east
    # the unit's own frame (x forward, y left, z up) and glTF's are both right-handed in space: the facing node takes
    # the unit's frame to glTF's axes (A Mx) and the sections stay in the unit's frame
    face = glb.group('unit_facing_east', root, rotation=quat(A @ Mx))
    times = [i * STEP_S for i in range(9)]
    nverts = 0
    for i in range(13):
        F = H.FR[i]
        poses = [F.pose(H.STEPS[k % 8]) for k in range(9)]
        tr = [t / UNITS_PER_CELL for R, t in poses]
        ro = [quat(orthonormal(R)) for R, t in poses]
        for k in range(1, 9):
            if np.dot(ro[k], ro[k - 1]) < 0:
                ro[k] = -ro[k]
        nd = glb.group(SEC_NAMES[i], face, translation=tr[0], rotation=ro[0])
        glb.animate('walk', nd, times, tr, ro)
        seen = {}
        for p in m.get(i, []):
            curved = any(c.kind != 'plane' for c in p.cons)
            if curved:
                V, Fc = RX.curved_mesh(p, n=24)
                P, Fi, N = RX.smooth_shaded(V, Fc)
            else:
                mm = RX.part_mesh(p)
                if mm is None:
                    continue
                P, Fi, N = RX.flat_shaded(*mm)
                if p.comp in VARIED:
                    P, Fi, N = subdivide(P, Fi, N, 0.8)
            rgb, house = colours(i, p, P, N)
            Pg = P / UNITS_PER_CELL
            Fi = orient(Pg, Fi, N)
            seen[p.name] = seen.get(p.name, 0) + 1
            nm = p.name if seen[p.name] == 1 else '%s_%d' % (p.name, seen[p.name])
            glb.part(nm, nd, Pg.astype(np.float32), Fi, N.astype(np.float32), rgb, house)
            nverts += len(P)
    cam = camera()
    gx, gy = cam.ground(np.array([288.0]), np.array([288.0]))
    glb.camera('camera_mod', 0.0, ELEV, list(A @ np.array([gx[0], gy[0], 0.0]) / UNITS_PER_CELL), 1.5, 1.5,
               extras=dict(note='orthographic, %g degrees above the ground, looking north; frames the 576 x 576 canvas'
                           % ELEV))
    glb.save(path, extras=dict(units='1.0 = one cell (128 px in the game; 192 px on the canvas)', facing='east',
                               walk='8 steps, %.3f s each (8 ticks)' % STEP_S))
    return path, nverts


if __name__ == '__main__':
    print(export(sys.argv[1]))
