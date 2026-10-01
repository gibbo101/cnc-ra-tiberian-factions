"""
titanexport.py - the Titan's 3D model as a .glb: the upper body with its cannon, and the legs walking (a glTF
animation of the 12 walk steps), in vertex colours, with the RA-grid camera that frames the mod's 448 canvas.

Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (128 px on the RA grid).  Origin: the unit's
position on the ground.  The Titan faces east (the mod's leg facing 6, upper-body frame 120).
"""
import sys, json
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import numpy as np
from export3d import GLB, orient
import rc, rcexport as RX, titan as TN, legfit as LF, torso2 as T2, barrel as BR, titanmat as TM

UNITS_PER_CELL = 192.0 / TN.PPU            # model units (TS px) per cell: the Titan's canvas has 192 px a cell
A = np.array([[1, 0, 0], [0, 0, 1.0], [0, 1.0, 0]])      # model (x east, y south, z up) -> glTF (x east, y up, z south)

ALBEDO = {LF.HIP: TM.GUN, LF.THIGH: TM.GOLD * 0.92, LF.SHIN: TM.GOLD, LF.FOOT: TM.GOLD, LF.KNEE: TM.STEEL,
          LF.PELVIS: TM.GOLD * 0.95, LF.HIPDOME: TM.GOLD * 0.95, LF.HIPRING: TM.STEEL * 0.8, LF.HIPJOINT: TM.STEEL * 0.8,
          LF.JOINT: TM.STEEL * 0.8, T2.BODY: TM.GOLD_SH, T2.BAND: TM.GREEN, T2.POD: TM.GREEN, T2.BOX: TM.GREEN,
          T2.ANT: TM.BLACK, T2.MOUNT: TM.STEEL_D, T2.HATCH: TM.GOLD_SH, BR.BREECH: TM.GREEN, BR.HOUSING: TM.GREEN,
          BR.TAPER: TM.GREEN, BR.BRACKET: TM.STEEL, BR.TUBE: TM.STEEL_L, BR.MUZZLE: TM.STEEL_D}
HOUSE = {T2.BAND, T2.POD, T2.BOX, BR.BREECH, BR.HOUSING, BR.TAPER}
SMOOTH = {T2.BODY, T2.BAND, LF.HIP, T2.ANT, BR.TUBE, BR.MUZZLE, LF.JOINT, T2.HATCH, LF.HIPDOME, LF.HIPRING,
          LF.HIPJOINT}


def quat(Rg):
    t = np.trace(Rg)
    if t > 0:
        q = np.array([Rg[2, 1] - Rg[1, 2], Rg[0, 2] - Rg[2, 0], Rg[1, 0] - Rg[0, 1], t + 1.0])
    else:
        i = int(np.argmax(np.diag(Rg))); j, k = (i + 1) % 3, (i + 2) % 3
        q = np.zeros(4); q[i] = Rg[i, i] - Rg[j, j] - Rg[k, k] + 1.0
        q[j] = Rg[j, i] + Rg[i, j]; q[k] = Rg[k, i] + Rg[i, k]; q[3] = Rg[k, j] - Rg[j, k]
    return q / np.linalg.norm(q)


def to_g_rot(R):
    return A @ R @ A.T


def to_g_pos(p):
    return A @ np.asarray(p, float) / UNITS_PER_CELL


def mesh_arrays(part):
    m = RX.part_mesh(part)
    if m is None:
        return None
    V, F = m
    P, Fi, N = (RX.smooth_shaded if part.comp in SMOOTH else RX.flat_shaded)(V, F)
    Pg = (P @ A.T) / UNITS_PER_CELL; Ng = N @ A.T
    Fi = orient(Pg, Fi, Ng)
    rgb = np.tile(np.asarray(ALBEDO.get(part.comp, (200, 0, 200)), float), (len(Pg), 1))
    house = np.full(len(Pg), 1.0 if part.comp in HOUSE else 0.0)
    return Pg.astype(np.float32), Fi, Ng.astype(np.float32), rgb, house


class AnimGLB(GLB):
    """GLB plus node parents and a TRS animation."""
    def __init__(self):
        super().__init__()
        self.children = {}
        self.anim = dict(name='walk', samplers=[], channels=[])

    def node(self, name, parent=None, translation=(0, 0, 0), rotation=(0, 0, 0, 1), mesh_of=None):
        nd = dict(name=name, translation=[float(v) for v in translation], rotation=[float(v) for v in rotation])
        if mesh_of is not None:
            v, f, n, rgb, house = mesh_of
            self.mesh(name, v, f, n, rgb, house)
            nd['mesh'] = self.nodes.pop()['mesh']
        self.nodes.append(nd)
        i = len(self.nodes) - 1
        if parent is not None:
            self.children.setdefault(parent, []).append(i)
        return i

    def animate(self, node, times, trans, rots):
        t_acc = self._add(np.asarray(times, np.float32).reshape(-1, 1), None, 5126, 'SCALAR', minmax=True)
        tr = self._add(np.asarray(trans, np.float32), None, 5126, 'VEC3')
        ro = self._add(np.asarray(rots, np.float32), None, 5126, 'VEC4')
        s0 = len(self.anim['samplers'])
        self.anim['samplers'] += [dict(input=t_acc, output=tr, interpolation='LINEAR'),
                                  dict(input=t_acc, output=ro, interpolation='LINEAR')]
        self.anim['channels'] += [dict(sampler=s0, target=dict(node=node, path='translation')),
                                  dict(sampler=s0 + 1, target=dict(node=node, path='rotation'))]

    def save(self, path, extras=None, roots=None):
        for p, ch in self.children.items():
            self.nodes[p]['children'] = ch
        # accessor min/max for the animation input is set; glTF wants scenes to list root nodes only
        child = {c for ch in self.children.values() for c in ch}
        roots = [i for i in range(len(self.nodes)) if i not in child] if roots is None else roots
        while len(self.buf) % 4:
            self.buf.append(0)
        gl = dict(asset=dict(version='2.0', generator='TS-to-RA HD (rcexport)'), scene=0,
                  scenes=[dict(nodes=roots, extras=extras or {})], nodes=self.nodes, meshes=self.meshes,
                  materials=self.materials, accessors=self.accessors, bufferViews=self.views,
                  buffers=[dict(byteLength=len(self.buf))])
        if self.anim['channels']:
            gl['animations'] = [self.anim]
        if getattr(self, 'cameras', None):
            gl['cameras'] = self.cameras
        import struct
        js = json.dumps(gl, separators=(',', ':')).encode()
        while len(js) % 4:
            js += b' '
        out = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(self.buf))
        out += struct.pack('<II', len(js), 0x4E4F534A) + js
        out += struct.pack('<II', len(self.buf), 0x004E4942) + bytes(self.buf)
        open(path, 'wb').write(out)


def leg_frames(S, pose):
    """each leg part's (local part, R, c) in the legs' body frame for one pose."""
    parts = LF.body_parts(S, pose[:6], pose[6], detail=True)
    out = []
    for p in parts:
        if p.name in ('thigh', 'shin', 'spur', 'foot', 'toe'):
            R, c, h = RX.box_frame(p)
        elif p.name == 'joint':
            cyl = [q for q in p.cons if q.kind == 'cyl'][0]
            caps = [q for q in p.cons if q.kind == 'plane']
            mid = (caps[0].d + (-caps[1].d)) / 2 if False else None
            # the joint's centre: halfway between its caps along its axis
            a = cyl.a; t0 = caps[0].d; t1 = -caps[1].d
            c = cyl.c + a * ((t0 + t1) / 2 - a @ cyl.c)
            R = np.eye(3)
        else:                                            # the hip: moves only with the bob
            R, c = np.eye(3), np.array([0, 0, pose[6]])
        local = p.moved(R.T, -R.T @ c)
        out.append((p.name, local, R, c))
    return out


def export(path, step_s=0.2):
    S, poses = TN.load_legs(); P = TN.load_torso()
    g = TN.EVEN_STEPS
    poses12 = [TN.mod_step_pose(poses, k) for k in range(12)]
    glb = AnimGLB()
    root = glb.node('Titan')
    # legs: facing east, standing on the ground
    k8 = TN.mod_to_cw(6, 8)
    M = TN.facing_cw(k8, 8)
    legs = glb.node('legs', root, translation=to_g_pos([0, 0, -S['g']]), rotation=quat(to_g_rot(M)))
    frames = [leg_frames(S, p) for p in poses12]
    times = [i * step_s for i in range(13)]
    n_hip = len(LF.hip_parts(S, 0.0, True))
    n_leg = (len(frames[0]) - n_hip) // 2
    seen = {}
    for j, (name, local, R0, c0) in enumerate(frames[0]):
        if j < n_hip:
            base = name
        else:
            base = ('left_' if j - n_hip < n_leg else 'right_') + name
        seen[base] = seen.get(base, 0) + 1
        nm = base if seen[base] == 1 else '%s_%d' % (base, seen[base])
        nd = glb.node(nm, legs, translation=to_g_pos(c0), rotation=quat(to_g_rot(R0)), mesh_of=mesh_arrays(local))
        tr = [to_g_pos(frames[i % 12][j][3]) for i in range(13)]
        ro = [quat(to_g_rot(frames[i % 12][j][2])) for i in range(13)]
        for i in range(1, 13):                          # keep quaternions on one side for a smooth slerp
            if np.dot(ro[i], ro[i - 1]) < 0:
                ro[i] = -ro[i]
        glb.animate(nd, times, tr, ro)
    # upper body facing east, with the cannon as its own node
    k32 = TN.mod_to_cw(24, 32)
    Mt = TN.facing_cw(k32, 32)
    up = glb.node('upper_body', root, translation=to_g_pos([0, 0, -S['g']]), rotation=quat(to_g_rot(Mt)))
    for p in T2.parts(P):
        glb.node(p.name, up, mesh_of=mesh_arrays(p))
    can = glb.node('cannon', up)
    for p in BR.body_parts(TN.BARREL_OFF, 1.0):
        glb.node('cannon_' + p.name, can, mesh_of=mesh_arrays(p))
    # the muzzle: a marker at the tube's tip
    tip = BR.vox_to_vu([34, 3, 3.45]) * np.array([1, -1, 1]) + np.array(TN.BARREL_OFF)
    glb.node('muzzle', can, translation=to_g_pos(tip))
    # the RA-grid camera that frames the 448 canvas: centre of the canvas = the unit's position
    import titanrender as TR
    cam = TR.camera(S)
    # the ground point seen at the canvas centre
    gx, gy = cam.ground(np.array([224.0]), np.array([224.0]))
    half = 224.0 / 192.0
    glb.camera('camera_ra_grid', 0.0, 32.0, list(to_g_pos([gx[0], gy[0], 0.0])), half, half,
               extras=dict(note='orthographic, 32 degrees above the ground, looking north; frames the 448 x 448 canvas'))
    glb.save(path, extras=dict(units='1.0 = one cell (128 px)', facing='east', walk='12 steps, %.2f s each' % step_s))
    return path


if __name__ == '__main__':
    print(export(sys.argv[1] if len(sys.argv) > 1 else 'tstitn.glb'))
