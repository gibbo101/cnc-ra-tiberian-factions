"""
jexport.py - the Juggernaut's 3D models as .glb files, in vertex colours (COLOR_0 albedo, COLOR_1 house colour), each
with the mod's camera framing the 448 canvas:

    tsjugg-walker.glb    the walker facing east on the Titan's legs, with its walk as a glTF animation ("walk": 15
                         steps, 0.2 s each)
    tsjugg-deployed.glb  the deployed piece: the base (the Titan's legs as TS draws them, deployed facing south-west,
                         the waist on the cabin's axis), the cabin turned east with the barrels at their rest pitch on
                         a hinge node ("aim": raised to 45 degrees and back), and markers at the three muzzles

Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).  Origin:
the unit's position on the ground (the walker's ground point; the deployed piece stands where the deploy leaves it).

    python3 jexport.py OUTDIR
"""
import os, sys, json
import numpy as np
from export3d import orient
import rc, rcexport as RX, vexport as VE
import jugg as JG
import jbase as JB
import jbase2 as JB2
import jdeployed as JD
import jdeprender as DR
import jfitcabin as JC
import jrender as JR
import jtlegs as TL
import jtbase as TB
import jtips

CELLS_PX = 192.0
UPC = CELLS_PX / JR.PPU                    # model units (TS px) per cell
A = VE.A

ALBEDO = {JG.SHELL: JR.GREEN, JG.ANT: JR.GREEN, JG.ARCH: JR.GREEN, JG.HATCH: JR.HATCH, JG.SLOT: JR.SLOT,
          JG.HSLIT: JR.SLOT, JG.SCORE: JR.SLOT, JG.MSLOT: JR.SLOT, JG.RECESS: JR.PANEL, JG.PACK: JR.KHAKI,
          JG.BARREL: JR.KHAKI, JG.MUZZLE: JR.STEEL, JG.CABLE: JR.CABLE, JG.HIP: JR.OLIVE, JG.THIGH: JR.OCHRE,
          JG.SHIN: JR.OCHRE, JG.FOOT: JR.OCHRE, JG.KNEE: JR.JOINT, JG.ANKLE: JR.JOINT, JC.FRONT: DR.FRONT,
          JB.PIVOT: DR.PIVOT, JB.RIM: DR.RIM, JB.LIMB: JR.OCHRE, JB.LFOOT: JR.OCHRE, JB.LKNEE: JR.JOINT,
          # the Titan's legs and waist (titanexport's colours)
          TL.TTHIGH: TL.GOLD * 0.92, TL.TSHIN: TL.GOLD, TL.TFOOT: TL.GOLD, TL.TSPUR: TL.STEEL,
          TL.TJOINT: TL.STEEL * 0.8, TL.THIPJ: TL.STEEL * 0.8, TL.TPELVIS: TL.GOLD * 0.95, TL.TRING: TL.STEEL * 0.8,
          TL.TDOME: TL.GOLD * 0.95,
          JG.ANTENNA: JR.ANTENNA_C}                  # the antenna: the Titan's black
HOUSE = {JG.SHELL, JG.ANT, JG.ARCH}
SMOOTH = {JG.BARREL, JG.KNEE, JG.ANKLE, JB.PIVOT, JB.RIM, JB.LKNEE, TL.TJOINT, TL.THIPJ, TL.TRING, TL.TDOME,
          JG.ANTENNA}


def g_rot(R):
    return A @ R @ A.T


def g_pos(p):
    return A @ np.asarray(p, float) / UPC


def mesh_of(part):
    m = RX.part_mesh(part)
    if m is None:
        return None
    V, F = m
    P, Fi, N = (RX.smooth_shaded if part.comp in SMOOTH else RX.flat_shaded)(V, F)
    Pg = (P @ A.T) / UPC; Ng = N @ A.T
    Fi = orient(Pg, Fi, Ng)
    rgb = np.tile(np.asarray(ALBEDO.get(part.comp, (200, 0, 200)), float), (len(Pg), 1))
    house = np.full(len(Pg), 1.0 if part.comp in HOUSE else 0.0)
    return Pg.astype(np.float32), Fi, Ng.astype(np.float32), rgb, house


def part_frame(p, bob=0.0):
    """a moving part's own frame (R, c) so it can be meshed once and posed by its node (the waist's parts move only
    with the bob, as the Titan's export has them)."""
    if p.name in ('thigh', 'shin', 'foot', 'spur', 'toe'):
        R, c, h = RX.box_frame(p)
        return R, c
    if p.name in ('pelvis', 'ring', 'hipdome', 'hipjoint'):
        return np.eye(3), np.array([0.0, 0.0, bob])
    cyl = [q for q in p.cons if q.kind == 'cyl'][0]
    caps = [q for q in p.cons if q.kind == 'plane']
    a = cyl.a; t0 = caps[0].d; t1 = -caps[1].d
    return np.eye(3), cyl.c + a * ((t0 + t1) / 2 - a @ cyl.c)


def camera(glb, cam, off=(0.0, 0.0, 0.0)):
    """the mod's camera framing the 448 canvas; off: the camera's world origin against the file's origin."""
    gx, gy = cam.ground(np.array([224.0]), np.array([224.0]))
    half = 224.0 / CELLS_PX
    glb.camera('camera_mod', 0.0, 32.0, list(g_pos(np.array([gx[0], gy[0], 0.0]) + np.asarray(off))), half, half,
               extras=dict(note='orthographic, 32 degrees above the ground, looking north; frames the 448 x 448 canvas'))


def walker(path, step_s=0.2):
    m = JR.load(os.path.join(JD.HERE, 'fit_walk_e.json'))
    P = m['P']
    glb = VE.AnimGLB()
    root = glb.node('JuggernautWalker')
    M = JG.facing_matrix(JR.mod_to_cw(6))              # the mod's walk facing 6: east
    face = glb.node('walker_facing_east', root, rotation=VE.quat(g_rot(M)))
    poses = [TL.step_pose(s) for s in range(15)]       # the Titan's gait at TS's 15 steps
    times = [i * step_s for i in range(16)]
    # the body: rigid, bobbing with the step's dw
    body = glb.node('body', face, translation=g_pos([0, 0, poses[0][6]]))
    for p in JG.upper_parts(P, 0.0) + JG.details(P, 0.0):
        mo = mesh_of(p)
        if mo is not None:
            glb.node(p.name, body, mesh=mo)
    glb.animate('walk', body, times, [g_pos([0, 0, poses[i % 15][6]]) for i in range(16)],
                [[0, 0, 0, 1.0]] * 16)
    # the Titan's legs and waist: each part meshed in its own frame at step 0 and posed per step (the same parts in
    # the same order every step: the waist, then the left leg, then the right)
    per = [TL.legs(poses[s]) for s in range(15)]
    n_waist = len(TL.waist_parts())
    n_leg = (len(per[0]) - n_waist) // 2
    seen = {}
    for j, p0 in enumerate(per[0]):
        base = p0.name if j < n_waist else ('left_' if j - n_waist < n_leg else 'right_') + p0.name
        seen[base] = seen.get(base, 0) + 1
        nm = base if seen[base] == 1 else '%s_%d' % (base, seen[base])
        R0, c0 = part_frame(p0, poses[0][6])
        local = p0.moved(R0.T, -R0.T @ c0)
        nd = glb.node(nm, face, translation=g_pos(c0), rotation=VE.quat(g_rot(R0)), mesh=mesh_of(local))
        fr = [part_frame(per[i % 15][j], poses[i % 15][6]) for i in range(16)]
        ro = [VE.quat(g_rot(R)) for R, c in fr]
        for i in range(1, 16):
            if np.dot(ro[i], ro[i - 1]) < 0:
                ro[i] = -ro[i]
        glb.animate('walk', nd, times, [g_pos(c) for R, c in fr], ro)
    camera(glb, JR.camera(m))
    glb.save(path, extras=dict(units='1.0 = one cell (192 px on the canvas, 128 px in the game)', facing='east',
                               walk='15 steps, %.2f s each (3 game ticks)' % step_s))
    return path


def deployed(path):
    d = DR.load()
    M = d['M']
    # the origin: the walker's ground point (the unit's position); the deployed world's origin is the column's foot
    g = JB2.walker_offset(M['bax'], M['by0'], JB2.S32) + np.array([M['base_off'], 0.0, 0.0])
    glb = VE.AnimGLB()
    root = glb.node('JuggernautDeployed')
    base = glb.node('base', root, translation=g_pos(-g))
    for p in TB.base_world(M):
        mo = mesh_of(p)
        if mo is not None:
            glb.node(p.name, base, mesh=mo)
    # the cabin turned east (the mod's facing 24), on its axis
    Mc = JG.facing_matrix((32 - 24) % 32, 32)
    cab = glb.node('cabin_facing_east', base, translation=g_pos([M['cab_off'], 0.0, M['cab_dz']]),
                   rotation=VE.quat(g_rot(Mc)))
    for p in JC.cabin_parts(M['PC']) + JG.details(M['PC']):
        mo = mesh_of(p)
        if mo is not None:
            glb.node(p.name, cab, mesh=mo)
    # the barrels on their hinge (the breech), in the cabin's frame (u forward, v right, w up)
    sec = d['sec']
    Rh, th = d['hva']
    br, ba = d['bar'], d['aim']
    vs = sec.scale
    hinge0 = np.array([4.0, 11.5, 3.5]); hinge = np.array([ba['hi'], 11.5, ba['hk']])
    a0 = np.deg2rad(br['p0'])
    Rp0 = np.array([[np.cos(a0), 0, -np.sin(a0)], [0, 1, 0], [np.sin(a0), 0, np.cos(a0)]])
    H = np.array([br['mu'], -br['mv'], br['mw']]) + Rp0 @ ((hinge - hinge0) * vs)      # unit frame (y left)
    Lh = Rh @ (sec.mn + hinge * vs) + th
    flip = np.diag([1.0, -1.0, 1.0])                  # the voxel's frame (y left) -> the cabin's (v right)

    def pitch_R(deg):
        a = np.deg2rad(deg)
        return flip @ np.array([[np.cos(a), 0, -np.sin(a)], [0, 1, 0], [np.sin(a), 0, np.cos(a)]]) @ flip

    hn = glb.node('barrels_hinge', cab, translation=g_pos(flip @ H), rotation=VE.quat(g_rot(pitch_R(DR.REST_PITCH))))
    P, F, N, alb, house = VE.section_mesh(sec)
    Pl = (P @ Rh.T + th - Lh) @ flip.T                # hinge-relative, cabin axes
    Nl = N @ Rh.T @ flip.T
    Pg = (Pl @ A.T) / UPC; Ng = Nl @ A.T
    F = orient(Pg, F, Ng)
    glb.node('barrels', hn, mesh=(Pg.astype(np.float32), F, Ng.astype(np.float32), alb, house))
    T = jtips.tips(d)
    for name, tp in zip(('muzzle_right', 'muzzle_middle', 'muzzle_left'), T):
        glb.node(name, hn, translation=g_pos(flip @ (Rh @ tp + th - Lh)))
    q0 = VE.quat(g_rot(pitch_R(DR.REST_PITCH))); q1 = VE.quat(g_rot(pitch_R(DR.AIM_PITCH)))
    glb.animate('aim', hn, [0.0, 1.0, 2.0], [g_pos(flip @ H)] * 3, [q0, q1, q0])
    camera(glb, DR.camera(d), -g)
    glb.save(path, extras=dict(units='1.0 = one cell (192 px on the canvas, 128 px in the game)',
                               facing='the cabin east; the base as TS draws it (deployed facing south-west)',
                               barrels='rest %.1f degrees, aim %.0f degrees, about the breech' % (DR.REST_PITCH,
                                                                                               DR.AIM_PITCH)))
    return path


if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    print(walker(os.path.join(out, 'tsjugg-walker.glb')))
    print(deployed(os.path.join(out, 'tsjugg-deployed.glb')))
