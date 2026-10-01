"""
titan.py - the Titan (TS [MMCH], TSTITN in the mod) assembled for the HD frames.

Units: TS sprite px (the model was fitted to TS's MMCH frames, 30 degrees, facings clockwise from screen-up);
ground at z = 0 under the unit's axis.  Legs and upper body each turn about the axis; the cannon (MMCHBARL.VXL)
rides on the upper body where TS's own drawing code puts it (TurretOffset -16 leptons = 2 voxel units back,
the HVA's translation, the voxel origin at the sprite's centre).
"""
import json
import numpy as np
import rc
import legfit as LF
import torso2 as T2
import barrel as BR

WORK = __import__('paths').HERE + '/'

# HD: the in-mod frames are TS's sprite x6.4 about TS (47.5, 55) -> canvas (224, 386)
PPU = 6.4
CANVAS = (448, 448)
COS30 = float(np.cos(np.deg2rad(30.0)))

# the mod's 12 walk steps are TS's walk frames
MOD_STEPS = (0, 1, 2, 4, 5, 6, 8, 9, 10, 11, 13, 14)


EVEN_STEPS = True        # the mod's 12 walk steps at evenly spaced phases of the stride (TS's own subset of its
                         # 15 frames, 0 1 2 4 5 6 8 9 10 11 13 14, skips a frame in three places)


def load_legs(path=WORK + 'legs_final.json'):
    js = json.load(open(path))
    S = js['S']; S['hip_c'] = tuple(S['hip_c']); S['hip_r'] = tuple(S['hip_r'])
    poses = {int(k): v for k, v in js['poses'].items()}
    if 'gait' in js:
        import gait as G
        g = G.Gait.from_json(js['gait'])
        poses['gait'] = g
    return S, poses


def mod_step_pose(poses, k12):
    """the pose for the mod's walk step k12 (0-11)."""
    g = poses.get('gait')
    if g is not None:
        phi = 2 * np.pi * (k12 / 12.0 if EVEN_STEPS else MOD_STEPS[k12] / 15.0)
        return g.pose(phi)
    return poses[MOD_STEPS[k12]]


def load_torso(path=WORK + 'torso_final.json'):
    js = json.load(open(path))
    P = dict(T2.P0); P.update(js['P'])
    for k in ('pfu', 'pru', 'pv', 'bu', 'bv', 'mu', 'mv', 'mw'):
        P[k] = tuple(P[k])
    return P


def facing_cw(k, n):
    """TS's facing k of n (clockwise from screen-up) as a body->world matrix (u fwd, v right, w up)."""
    th = 2 * np.pi * k / n
    f = np.array([np.sin(th), -np.cos(th), 0.0]); r = np.array([np.cos(th), np.sin(th), 0.0])
    return np.stack([f, r, np.array([0, 0, 1.0])], axis=1)


def mod_to_cw(f, n):
    """the mod's facing f (counter-clockwise from north) -> TS's clockwise index."""
    return (n - f) % n


def legs_parts(S, pose, k8):
    """the legs at TS facing k8 (of 8), ground at z = 0."""
    M = facing_cw(k8, 8)
    t = np.array([0, 0, -S['g']])
    parts = LF.body_parts(S, pose[:6], pose[6], detail=True)
    return [p.moved(M, t) for p in parts], M, t


BARREL_OFF = (-2.5, 0.0, 9.0)      # fitted to the in-mod composite (TS: TurretOffset 2 voxel units back; at the hull band)


def torso_parts(P, k32, g, with_barrel=True):
    M = facing_cw(k32, 32)
    t = np.array([0, 0, -g])
    parts = T2.parts(P)
    if with_barrel:
        parts = parts + BR.body_parts(BARREL_OFF, 1.0)
    return [p.moved(M, t) for p in parts], M, t
