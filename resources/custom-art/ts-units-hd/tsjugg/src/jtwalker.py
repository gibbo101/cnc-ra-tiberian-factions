"""
jtwalker.py - the Juggernaut walker on the Titan's legs: the walker's body as fitted (jugg.py, fit_walk_e.json: the
shell, hatch, barrel housings, barrels, sensor, hoops) on the HD Titan's legs and waist (jtlegs.py; the waist takes
the place of v1's olive hip block: below the body TS's JUGGER frames are MMCH's pixels), walking the Titan's gait at
TS's 15 steps; the body rides the gait's bob (as JUGGER's does: v1's per-step fit of it follows the same curve).
"""
import numpy as np
import jugg as JG
import jtlegs as TL

JG.CLASS.update(TL.CLASS)


def body_parts(P, step):
    """(the Juggernaut's own parts, the Titan's leg and waist parts, the pose) at walk step `step`, in the body frame."""
    pose = TL.step_pose(step)
    dw = pose[6]
    return JG.upper_parts(P, dw) + JG.details(P, dw), TL.legs(pose), pose


def all_parts(P, step):
    own, legs, _ = body_parts(P, step)
    return own + legs


def v1_parts(P, pose):
    return JG.body_parts(P, pose) + JG.details(P, pose[6])
