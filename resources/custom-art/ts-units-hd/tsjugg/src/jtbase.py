"""
jtbase.py - the deployed Juggernaut's base on the Titan's legs.  TS's base frame (DJUGG 0) is MMCH's pixels plus two
limbs of its own:
  - its front limb is the walker's near leg as it stands at walk step 0 facing south-west (MMCH's frame 75, where
    JUGGER CW5 step 0 has it), the far leg standing behind;
  - the pivot the cabin turns on is MMCH's dome, the same pixels moved 3 px right and 3 px down (DJUGGMK moves it there
    in frames 7-8, under the sliding body): onto the cabin's axis;
  - two limbs unfolded west and east (jbase.limb, as fitted: fit_base2_a.json).
So the base here is the Titan's two legs (jtlegs, the gait's step 0) where the walker stands, the Titan's waist
(pelvis, bearing ring, dome) on the cabin's axis as low as TS's dome pixels put it, the cabin turning on the dome as the
Titan's upper body does, and the two side limbs.  The waist moves 3.5 px back, 0.9 left and 4.7 down, so the thighs'
tops come to its top corners: the near hip joint stays on its thigh there (TS's moved dome pixels cover that corner),
the far one goes with the waist (at the walker's place it would stand out past the dome, where TS has none).  (v1's
pivot column and rim were the fit's reading of the dome's pixels.)

World: the deployed scene's (jdeployed: x east, y south, z up, TS px; origin the common axis's foot).
"""
import numpy as np
import jugg as JG
import jbase as JB
import jbase2 as JB2
import jtlegs as TL

CW5 = JG.facing_matrix(5)
DOME_SHIFT = (3.0, 3.0)                 # DJUGG: MMCH's dome at (4, 14), its near leg at (1, 11)
POSE0 = TL.step_pose(0)


def walker_point(M, sin_e=JB2.S32):
    """the walker's ground point in the deployed world."""
    return JB2.walker_offset(M['bax'], M['by0'], sin_e) + np.array([M['base_off'], 0.0, 0.0])


NEAR, FAR = -1, 1                       # facing south-west the left leg is the near one (south-east of the right)


def legs_world(M, sin_e=JB2.S32):
    """the Titan's legs at walk step 0 facing south-west, where the walker stands, the near one's hip joint on it."""
    return TL.move(TL.legs(POSE0, waist=False, joints=(NEAR,)), CW5, walker_point(M, sin_e))


def waist_walker(M, sin_e=JB2.S32):
    """the waist and the far hip joint where the walker carries them (the deploy's start)."""
    return TL.move(TL.waist(POSE0, joints=(FAR,)), CW5, walker_point(M, sin_e))


def waist_shift(M, sin_e=JB2.S32):
    """the move taking the walker's waist to the base's pivot: the dome onto the cabin's axis, as low as TS's dome
    pixels put it (3 px down on the screen, through a camera sin_e above the ground); and the dome's centre before."""
    cos_e = np.sqrt(1 - sin_e ** 2)
    W = CW5 @ TL.dome_centre(POSE0) + walker_point(M, sin_e)
    sy_w = W[1] * sin_e - W[2] * cos_e
    z = -(sy_w + DOME_SHIFT[1]) / cos_e
    D = np.array([M['cab_off'], 0.0, z])
    return D - W, W


def waist_deployed(M, sin_e=JB2.S32):
    d, _ = waist_shift(M, sin_e)
    return TL.move(waist_walker(M, sin_e), np.eye(3), d)


def limbs_world(M):
    PB = M['PB']
    out = []
    for yaw in (PB['yw'], PB['ye']):
        out += JB.limb(PB, yaw)
    return [p.moved(np.eye(3), (M['base_off'], 0.0, 0.0)) for p in out]


def base_world(M, sin_e=JB2.S32):
    """the deployed base on the Titan's legs, in the deployed world (in place of jdeployed.base_world)."""
    return limbs_world(M) + legs_world(M, sin_e) + waist_deployed(M, sin_e)


if __name__ == '__main__':
    import jdeployed as JD
    M = JD.load_fits()
    for se, lab in ((JB2.S30, 'TS 30'), (JB2.S32, 'HD 32')):
        d, W = waist_shift(M, se)
        print(lab, 'walker dome centre', np.round(W, 2), 'move', np.round(d, 2), ' screen x shift %.2f (TS: 3)' % d[0],
              ' dome at z %.2f' % (W + d)[2])
    print('cab_off %.2f base_off %.2f cab_dz %.2f  cabin bottom z %.2f' % (M['cab_off'], M['base_off'], M['cab_dz'],
                                                                       M['PC']['bw0'] + M['cab_dz']))
