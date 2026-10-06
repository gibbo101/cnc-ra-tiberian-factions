"""
jdeploy.py - the Juggernaut's deploy (TSJUGG 184-201: 18 frames facing south-west, 2 ticks a frame; played backwards to
pack up), following TS's DJUGGMK frame by frame.  What moves when was measured off TS's frames (house, khaki and grey
extents per frame, jdeploy.MEASURED):

    0        the walker at walk step 0 (= walk frame 45)
    1-5      the west limb slides out from under the body (its foot from x 38 to 31 in TS's frame)
    4-12     the east limb slides out (55 to 68)
    6-10     the body slides back onto the column, 9 px right and 2 down in TS's frame, in steps of 2, 2, 2, 2, 1
    7-8      under it, the waist (the Titan's dome, MMCH's pixels in TS) moves onto the cabin's axis: TS's dome pixels
             move 3 px right and 3 down, two thirds of the way in frame 7 (jtbase.py)
    10-11    the barrel housings telescope forward (3 px, then 5)
    12-16    the three barrels slide out of them (2 px a frame)
    17       the deployed piece (= rest frame 132: TS's own last frame leaves the barrels to the engine's voxel, so
             ours carries them and nothing pops when the game turns to the deployed frames)

The walker's two legs (the Titan's, jtlegs.py) stay planted throughout (TS's front limb is the walker's near leg,
pixel for pixel).

    python3 jdeploy.py frames 184,190,201 [ss] [outdir] [sky]
"""
import json, os, sys, time
import numpy as np
import rc
import jugg as JG
import jbase as JB
import jbase2 as JB2
import jdeployed as JD
import jdeprender as DR
import jrender as JR
import jtlegs as TL
import jtbase as TB
from frameio import save

FIRST = 184
SW32 = 12                                  # the deploy's facing: south-west (the mod's 32 facings)
CW5 = JG.facing_matrix(5)                  # the walker's (TS's CW5, the mod's walk facing 3)

# TS's extents per DJUGGMK frame (classes, jdeploy_measure): house bbox x0, west limb's x0, east limb's x1, the
# housings' x0, the barrels' x0
MEASURED = dict(house_x0=[30, 30, 30, 30, 30, 30, 32, 34, 36, 38, 39, 39, 39, 39, 39, 39, 39, 42],
                west_x0=[38, 37, 36, 35, 33, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31],
                east_x1=[55, 55, 55, 55, 56, 58, 60, 62, 64, 65, 66, 67, 68, 68, 68, 68, 68, 68],
                pack_x0=[26, 26, 26, 26, 26, 26, 28, 30, 32, 34, 32, 30, 30, 30, 30, 30, 30, 40],
                rods_x0=[21, 21, 21, 21, 21, 21, 23, 25, 27, 29, 28, 26, 24, 22, 20, 18, 16, 31])


def progress():
    """each move's progress (0..1) per TS frame, from MEASURED."""
    M = MEASURED
    n = 18
    slide = [(M['house_x0'][t] - 30) / 9.0 for t in range(17)] + [1.0]
    west = [min(1.0, max(0.0, (38 - M['west_x0'][t]) / 7.0)) for t in range(n)]
    east = [min(1.0, max(0.0, (M['east_x1'][t] - 55) / 13.0)) for t in range(n)]
    # the housings: their front against where the slid body puts them (26 + the slide's 9 px x its progress)
    pack = [min(1.0, max(0.0, (26 + 9 * slide[t] - M['pack_x0'][t]) / 5.0)) for t in range(17)] + [1.0]
    # the barrels: their tips against where the slid, telescoped housings put the muzzles
    rods = [min(1.0, max(0.0, (21 + 9 * slide[t] - 5 * pack[t] - M['rods_x0'][t]) / 9.0)) for t in range(17)] + [1.0]
    # the waist: MMCH's dome pixels at the walker's place to frame 6, two thirds of the way (2 px of 3) in 7, at the
    # base's pivot from 8 (jdeploy dome tracking: frames 0-6 match at (1, 11), 7 at (3, 13), 8-16 at (4, 14))
    waist = [0.0] * 7 + [2.0 / 3.0] + [1.0] * 10
    return dict(slide=slide, west=west, east=east, pack=pack, rods=rods, waist=waist)


PROG = progress()
PACK_LEN = 5.0 / np.sin(np.deg2rad(45.0))        # 5 px of screen x along south-west: 7.1 TS px
RODS_LEN = 9.0 / np.sin(np.deg2rad(45.0))        # 12.7


def setup():
    m = DR.load()
    wm = JR.load(os.path.join(JD.HERE, 'fit_walk_e.json'))
    M = m['M']
    # the walker's ground point in the deployed world (origin the column's foot, x east, y south, z up)
    g = JB2.walker_offset(M['bax'], M['by0'], JB2.S32) + np.array([M['base_off'], 0.0, 0.0])
    P = wm['P']; pose = TB.POSE0                       # the walker at walk step 0 on the Titan's gait (walk frame 45)
    # where the slid body ends: the walker's shell centre onto the cabin's
    PC = M['PC']
    cw = np.array([(P['bu0'] + P['bu1']) / 2, 0.0, (P['bw0'] + P['bw1']) / 2 + pose[6]])
    cc = np.array([(PC['bu0'] + PC['bu1']) / 2, 0.0, (PC['bw0'] + PC['bw1']) / 2])
    R = JG.facing_matrix((32 - SW32) % 32, 32)
    start = g
    end = np.array([M['cab_off'], 0.0, M['cab_dz']]) + R @ cc - CW5 @ cw
    return dict(m=m, wm=wm, P=P, pose=pose, g=g, start=start, end=end)


def limb_out(P, yaw, p):
    """a side limb slid out by p (0 hidden .. 1 as deployed): its lower part (knee to foot) runs out from the knee."""
    if p <= 0:
        return []
    Q = dict(P)
    Q['fr'] = P['kr'] + p * (P['fr'] - P['kr'])
    return JB.limb(Q, yaw)


def walker_body(S, t):
    """the walker's upper body and its barrels at deploy frame t, in the deployed world."""
    P = dict(S['P']); pose = S['pose']
    pr = PROG
    ext = pr['pack'][t] * PACK_LEN
    Q = dict(P); Q['bl'] = P['bl'] + ext
    parts = JG.upper_parts(Q, pose[6]) + JG.details(Q, pose[6])
    # the barrels sliding out of the housings: three thin grey rods from the muzzles' fronts
    rl = pr['rods'][t] * RODS_LEN
    if rl > 0.05:
        for k in (-1, 0, 1):
            a = np.array([Q['pu1'] + Q['bl'] + Q['ml'] - 0.3, k * Q['bs'], Q['bz'] + pose[6]])
            parts.append(rc.cylinder(a, a + np.array([rl + 0.3, 0, 0]), 0.75, DR.ROD, 'rod'))
    o = S['start'] + pr['slide'][t] * (S['end'] - S['start'])
    return TL.move(parts, CW5, o)


def walker_legs(S):
    """the Titan's legs, planted where the walker stands (jtbase)."""
    return TB.legs_world(S['m']['M'])


def walker_waist(S, t):
    """the Titan's waist at deploy frame t: from where the walker carries it to the base's pivot."""
    M = S['m']['M']
    d, _ = TB.waist_shift(M)
    return TL.move(TB.waist_walker(M), np.eye(3), PROG['waist'][t] * d)


def scene(S, t):
    """deploy frame t (0..17): (modelled parts, barrel pose or None)."""
    if t >= 17:
        return DR.deployed_scene(S['m'], SW32, DR.REST_PITCH)
    M = S['m']['M']; PB = M['PB']
    side = []
    for yaw, p in ((PB['yw'], PROG['west'][t]), (PB['ye'], PROG['east'][t])):
        side += [q.moved(np.eye(3), (M['base_off'], 0.0, 0.0)) for q in limb_out(PB, yaw, p)]
    return walker_body(S, t) + walker_legs(S) + walker_waist(S, t) + side, None


def frame(k, S, ss=4, sky=True):
    t = k - FIRST
    parts, pose = scene(S, t)
    return DR.render(parts, pose, S['m'], DR.camera(S['m']), ss, sky)


if __name__ == '__main__':
    S = setup()
    ks = [int(a) for a in sys.argv[2].split(',')]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    out = sys.argv[4] if len(sys.argv) > 4 else 'out_deploy'
    sky = bool(int(sys.argv[5])) if len(sys.argv) > 5 else True
    os.makedirs(out, exist_ok=True)
    for k in ks:
        t0 = time.time()
        img, trim = frame(k, S, ss, sky)
        save(img, trim, f'{out}/tsjugg-{k:04d}.png')
        print('frame', k, '%.0fs' % (time.time() - t0), flush=True)
