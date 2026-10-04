"""
infexport.py - an infantry unit's 3D model as a .glb: the soldier's parts (each an exact mesh of its convex solid, in
vertex colours), every sequence as a glTF animation (each part posed per frame by its node's translation and
rotation, at the game's timing), a marker at the rifle's muzzle, and the mod's camera framing the 267 x 208 canvas.

Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (30.3 TS px, as the other TS units' models).
Origin: the soldier's position on the ground.  He faces east (the mod's facing 6); the sequences TS draws in one
facing (idles, deaths) play facing east too.

    python3 infexport.py UNIT shape.json out.glb
"""
import json, os, sys
import numpy as np
from export3d import orient
import rc, rcexport as RX, vexport as VE
import inf as I
import infall as AL
import infrender as R
import infseq as SQ

UPC = 30.3                       # TS px (model units) a cell
A = VE.A                         # model (x east, y south, z up) -> glTF (x east, y up, z south)
TICK = 1.0 / 15.0                # seconds a game tick
# (sequence, ticks a frame, loops) - the hand-off README's timing
SEQS = [('stand', 1, False), ('walk', 2, True), ('idle1', 2, False), ('idle2', 2, False), ('crawl', 2, True),
        ('death1', 2, False), ('death2', 2, False), ('fire', 1, True), ('prone_fire', 1, True), ('lie_down', 2, False),
        ('get_up', 3, False),
        # the Jumpjet's flight, the Medic's heal (a unit's own sequences)
        ('fly', 2, True), ('hover', 2, True), ('fire_fly', 1, True), ('tumble', 2, False), ('heal', 2, False)]
SIDED = ('thigh', 'shin', 'knee', 'boot', 'shoulder_pad', 'upper_arm', 'forearm', 'hand')
ROUND = (I.PELVIS, I.BELT, I.THIGH, I.SHIN, I.KNEE, I.ABDOMEN, I.CHEST, I.VEST, I.POUCH, I.PAD, I.UARM, I.FARM, I.HAND,
         I.HELMET, I.VISOR, I.JAW, I.TUBE, I.FACE, I.ROLL, I.ROLL_END)
EAST = 6


def albedo(comp):
    if comp in R.HOUSE:
        return np.asarray(R.GREEN, float)
    return np.asarray(R.MAT.get(comp, (200, 0, 200)), float)


def posed(S, Q):
    """the soldier's grounded parts facing east, each with its frame (c, R)."""
    return I.grounded(S, Q, 0.0)[0]


def names(parts):
    out, seen = [], {}
    for p in parts:
        n = p.name
        if n in SIDED:
            seen[n] = seen.get(n, 0) + 1
            n = ('left_' if seen[n] == 1 else 'right_') + n
        out.append(n)
    return out


def mesh_of(local, comp):
    m = RX.part_mesh(local)
    if m is None:
        return None
    V, F = m
    P, Fi, N = (RX.smooth_shaded if comp in ROUND else RX.flat_shaded)(V, F)
    Pg = (P @ A.T) / UPC; Ng = N @ A.T
    Fi = orient(Pg, Fi, Ng)
    rgb = np.tile(albedo(comp), (len(Pg), 1))
    house = np.full(len(Pg), 1.0 if comp in R.HOUSE else 0.0)
    return Pg.astype(np.float32), Fi, Ng.astype(np.float32), rgb, house


def trs(p):
    c, Rm = p.frame
    return A @ np.asarray(c, float) / UPC, VE.quat(A @ np.asarray(Rm, float) @ A.T)


def seq_frames(unit, seq, tab):
    """the frames a sequence plays facing east (per-facing sequences: the east facing's)."""
    first, n, fc = SQ.SEQ[unit][seq]
    if fc == 8:
        return [first + EAST * n + s for s in range(n)]
    if seq == 'stand':
        return [EAST]
    return [first + i for i in range(n)]


def export(unit, shape, path):
    js = json.load(open(shape))
    S = dict(I.S0); S.update({k: tuple(v) if isinstance(v, list) else v for k, v in js['S'].items()})
    tab = AL.pose_table(unit, dict(js['Q']))
    Qref = tab[EAST][0]
    ref = posed(S, Qref)
    nm = names(ref)
    glb = VE.AnimGLB()
    import infunit
    root = glb.node(infunit.UNITS[unit]['model'])
    nodes = []
    for p, n in zip(ref, nm):
        c, Rm = p.frame
        local = p.moved(np.asarray(Rm).T, -np.asarray(Rm).T @ np.asarray(c))
        t, q = trs(p)
        nodes.append(glb.node(n, root, translation=t, rotation=q, mesh=mesh_of(local, p.comp)))
    dz = I.grounded(S, Qref, 0.0)[1]
    ri = [i for i, p in enumerate(ref) if p.name == 'rifle']
    if ri:
        # the muzzle: a marker on the rifle, where the flash comes from
        ri = ri[0]
        c, Rm = ref[ri].frame
        mz = I.muzzle(S, Qref, 0.0) + np.array([0, 0, dz])
        glb.node('muzzle', nodes[ri], translation=A @ (np.asarray(Rm).T @ (mz - np.asarray(c))) / UPC)
    if unit == 'jj':
        # the Jumpjet: a marker at each nozzle's mouth, where his jet flames come out (on the jetpack)
        pi = [i for i, n in enumerate(nm) if n == 'jetpack'][0]
        c, Rm = ref[pi].frame
        for side, pt in zip(('left', 'right'), I.nozzles(S, Qref, 0.0)):
            pt = np.asarray(pt) + np.array([0, 0, dz])
            glb.node('nozzle_' + side, nodes[pi], translation=A @ (np.asarray(Rm).T @ (pt - np.asarray(c))) / UPC)
    if ri:
        pass
    elif unit == 'e2':
        # no rifle (the Disc Thrower): a marker in the right hand's palm, where the disc leaves it
        hi = [i for i, n in enumerate(nm) if n == 'right_hand'][0]
        c, Rm = ref[hi].frame
        Sh, RU, E, RFa, W = I.Pose(S, Qref, 0.0).arms['r']
        pt = W + RFa @ np.array([0.0, 0.0, -S['rh'] * 1.1]) + np.array([0, 0, dz])
        glb.node('throw', nodes[hi], translation=A @ (np.asarray(Rm).T @ (pt - np.asarray(c))) / UPC)
    # the sequences
    info = {}
    for seq, ticks, loop in SEQS:
        if seq not in SQ.SEQ[unit]:
            continue
        ks = [k for k in seq_frames(unit, seq, tab) if k in tab]
        if not ks:
            continue
        keys = ks + ([ks[0]] if loop and len(ks) > 1 else [])
        times = [i * ticks * TICK for i in range(len(keys))]
        poses = [posed(S, tab[k][0]) for k in keys]
        for j, nd in enumerate(nodes):
            tr, ro = [], []
            for ps in poses:
                t, q = trs(ps[j])
                if ro and np.dot(q, ro[-1]) < 0:
                    q = -q
                tr.append(t); ro.append(q)
            glb.animate(seq, nd, times, tr, ro)
        info[seq] = ('frame %d' % ks[0] if len(ks) == 1 else
                     'frames %d-%d, %d tick%s a frame%s' % (ks[0], ks[-1], ticks, '' if ticks == 1 else 's',
                                                            ', loops' if loop else ''))
    # the mod's camera: the RA-grid camera that draws the 267 x 208 canvas
    cam = R.camera((js['ax'], js['y0']))
    W, H = R.CANVAS
    gx, gy = cam.ground(np.array([W / 2.0]), np.array([H / 2.0]))
    cells_px = R.PPU * R.VIS * UPC
    glb.camera('camera_mod', 0.0, 32.0, list(A @ np.array([gx[0], gy[0], 0.0]) / UPC), (W / 2.0) / cells_px,
               (H / 2.0) / cells_px, extras=dict(note='orthographic, 32 degrees above the ground, looking north; frames '
                                                     'the 267 x 208 canvas'))
    glb.save(path, extras=dict(units='1.0 = one cell (30.3 TS px, as the other TS units)', facing='east',
                               animations=info))
    return path, info


if __name__ == '__main__':
    print(export(sys.argv[1], sys.argv[2], sys.argv[3]))
