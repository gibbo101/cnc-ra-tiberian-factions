"""
wexport.py - the Wolverine's 3D model as a .glb: the body (chest, head, back panel, shoulder pads, arms, guns,
antenna, lamp, pelvis) as one node that bobs and sways, the legs' parts as nodes posed per walk step, in vertex
colours, with two animations ("walk": the 12 walk steps, 2 ticks each; "stance": the firing stance), the muzzles
as marker nodes, and the RA-grid camera that frames the mod's 384 canvas.

Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
Origin: the unit's position on the ground.  The Wolverine faces east (the mod's facing 6).

    python3 wexport.py model.json out.glb
"""
import sys, json, struct
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from export3d import GLB, orient
import rc, rcexport as RX
import wolf as WF, wolfhd as WH, wolfmat as WM, wolfrender as WR

UNITS_PER_CELL = 192.0 / WH.PPU            # TS px per cell: the Wolverine's canvas has 192 px a cell
A = np.array([[1, 0, 0], [0, 0, 1.0], [0, 1.0, 0]])      # model (x east, y south, z up) -> glTF (x east, y up, z south)
LEG_NAMES = ('thigh', 'shin', 'foot', 'knee', 'ankle', 'toe')
STEP_S = 2 / 15.0                          # 2 game ticks a walk step

ALBEDO = {WF.TORSO: WM.GOLD, WF.WAIST: WM.GOLD * 0.9, WF.HEAD: WM.GOLD_SH, WF.NECK: WM.OLIVE * 0.8, WF.PACK: WM.GREEN,
          WF.SHOULDER: WM.GREEN, WF.ARM: WM.GOLD * 0.95, WF.GUN: WM.GUN, WH.BARREL: WM.STEEL, WH.MRING: WM.STEEL_L,
          WF.ANT: WM.BLACK, WF.ANTBASE: WM.STEEL_D, WH.LAMPC: WM.LAMP, WF.PELVIS: WM.OLIVE, WF.HIPJ: WM.STEEL * 0.8,
          WF.THIGH: WM.GOLD * 0.95, WF.KNEE: WM.STEEL, WF.SHIN: WM.GOLD, WF.ANKLE: WM.STEEL * 0.85,
          WF.FOOT: WM.GOLD * 0.97, WH.WINDOW: WM.GLASS, WH.TOE: WM.GOLD * 0.97, WH.DRUM: WM.GUN * 1.1,
          WH.BELT: WM.BRASS, WH.HANDLE: WM.STEEL_D * 1.2}
HOUSE = set(WM.HOUSE_COMPS)
SMOOTH = {WH.BARREL, WH.MRING, WF.ANT, WF.KNEE, WF.ANKLE, WF.HIPJ, WH.LAMPC}


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
    """GLB plus node parents and named TRS animations."""
    def __init__(self):
        super().__init__()
        self.children = {}
        self.anims = {}

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


def part_frame(p):
    """(R, c) of a leg part: a box's own frame, or a cylinder's axis frame at its middle."""
    if p.name in ('thigh', 'shin', 'foot', 'toe'):
        R, c, h = RX.box_frame(p)
        return R, c
    cyl = [q for q in p.cons if q.kind == 'cyl'][0]
    caps = [q for q in p.cons if q.kind == 'plane']
    t1 = caps[0].d; t0 = -caps[1].d                      # cylinder(): Plane(a, a.p1), Plane(-a, -a.p0)
    c = cyl.c + cyl.a * ((t0 + t1) / 2 - cyl.a @ cyl.c)
    R = rc.frame_from(cyl.a, (0, 0, 1.0))
    return R, c


def leg_frames(model, pose):
    """[(name, local part, R, c)] for both legs in a pose, in the body frame."""
    P = model['P']
    turn = WF.body_turn(P, pose)
    out = []
    for side, parts in zip(('left', 'right'), WF.legs_of(P, pose, turn)):
        seen = {}
        for p0 in parts:
            for p in (WH.clawed_foot(p0) if p0.comp == WF.FOOT else [p0]):     # Westwood's clawed feet
                R, c = part_frame(p)
                seen[p.name] = seen.get(p.name, 0) + 1
                nm = '%s_%s' % (side, p.name) + ('' if seen[p.name] == 1 else '_%d' % seen[p.name])
                out.append((nm, p.moved(R.T, -R.T @ c), R, c))
    return out


def body_frame(model, pose):
    """the body node's (R, t): the sway R about the hips' centre, lifted by the bob."""
    P = model['P']
    pv = np.array([P['ju'], 0.0, P['jw'] + pose[6]])
    turn = WF.body_turn(P, pose)
    R = np.eye(3) if turn is None else turn[0]
    return R, pv


def export(model, path):
    P = model['P']
    glb = AnimGLB()
    root = glb.node('Wolverine')
    M = WF.facing_matrix(WH.mod_to_cw(6))                  # facing east
    unit = glb.node('unit_facing_east', root, rotation=quat(to_g_rot(M)))
    rest = [0.0] * 7
    pv0 = np.array([P['ju'], 0.0, P['jw']])
    allp = WH.detail(WF.body_parts(P, rest), P, 0.0)
    body_parts = [p for p in allp if p.name not in LEG_NAMES]
    walk = [WH.walk_pose(model, s) for s in range(12)]
    stance = model['stand']
    R0, t0 = body_frame(model, walk[0])
    body = glb.node('body', unit, translation=to_g_pos(t0), rotation=quat(to_g_rot(R0)))
    seen = {}
    for p in body_parts:
        seen[p.name] = seen.get(p.name, 0) + 1
        nm = p.name if seen[p.name] == 1 else '%s_%d' % (p.name, seen[p.name])
        glb.node(nm, body, mesh_of=mesh_arrays(p.moved(np.eye(3), -pv0)))
    for s, nm in ((-1, 'muzzle_left'), (1, 'muzzle_right')):
        glb.node(nm, body, translation=to_g_pos(np.array([P['gu1'], s * P['gv'], P['gw']]) - pv0))
    times = [i * STEP_S for i in range(13)]
    frames = [body_frame(model, walk[i % 12]) for i in range(13)]
    tr = [to_g_pos(t) for R, t in frames]
    ro = [quat(to_g_rot(R)) for R, t in frames]
    for i in range(1, 13):
        if np.dot(ro[i], ro[i - 1]) < 0:
            ro[i] = -ro[i]
    glb.animate('walk', body, times, tr, ro)
    Rs, ts = body_frame(model, stance)
    glb.animate('stance', body, [0.0, 1.0], [to_g_pos(ts)] * 2, [quat(to_g_rot(Rs))] * 2)
    legs = glb.node('legs', unit)
    lf = [leg_frames(model, walk[i % 12]) for i in range(13)]
    lst = leg_frames(model, stance)
    for j, (name, local, R, c) in enumerate(lf[0]):
        nd = glb.node(name, legs, translation=to_g_pos(c), rotation=quat(to_g_rot(R)), mesh_of=mesh_arrays(local))
        tr = [to_g_pos(lf[i][j][3]) for i in range(13)]
        ro = [quat(to_g_rot(lf[i][j][2])) for i in range(13)]
        for i in range(1, 13):
            if np.dot(ro[i], ro[i - 1]) < 0:
                ro[i] = -ro[i]
        glb.animate('walk', nd, times, tr, ro)
        glb.animate('stance', nd, [0.0, 1.0], [to_g_pos(lst[j][3])] * 2, [quat(to_g_rot(lst[j][2]))] * 2)
    # the RA-grid camera that frames the 384 canvas
    cam = WR.camera(model)
    gx, gy = cam.ground(np.array([192.0]), np.array([192.0]))
    half = 192.0 / 192.0
    glb.camera('camera_ra_grid', 0.0, 32.0, list(to_g_pos([gx[0], gy[0], 0.0])), half, half,
               extras=dict(note='orthographic, 32 degrees above the ground, looking north; frames the 384 x 384 canvas'))
    glb.save(path, extras=dict(units='1.0 = one cell (128 px in the game; 192 px on the canvas)', facing='east',
                               walk='12 steps, %.3f s each (2 ticks)' % STEP_S, stance='the firing stance'))
    return path


if __name__ == '__main__':
    print(export(WH.load(sys.argv[1]), sys.argv[2]))
