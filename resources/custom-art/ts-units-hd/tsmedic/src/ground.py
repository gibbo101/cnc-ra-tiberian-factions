"""
ground.py - how far a soldier TS shows on the ground (lying dead, prone, crawling) floats off it.  From TS's camera a
part raised in the air and the same part lying further back look the same (a unit up = 1.73 units back), so a fit to
TS's frames alone left prone and dead soldiers hovering, legs up (Luke: "leg in the air way above the shadow"; "ours are
hovering above the ground with where the shadow is").  TS's shadows hug its prone and fallen soldiers: their hips,
chest, knees and feet lie on the ground, propped on the forearms when prone.

    pen = ground.lying(S, Q, facing, dz, head=True, elbows=False)
"""
import numpy as np
import inf as I


def heights(S, Q, facing, dz):
    P = I.Pose(S, Q, I.facing_angle(facing))
    out = dict(pelvis=P.pelvis[0][2] + dz, chest=P.chest[0][2] + dz, head=P.head[0][2] + dz)
    for s in 'lr':
        out[s + 'knee'] = P.legs[s][2][2] + dz
        out[s + 'ankle'] = P.legs[s][4][2] + dz
        out[s + 'elbow'] = P.arms[s][2][2] + dz
    return out


def lying(S, Q, facing, dz, w=0.03, head=True, elbows=False, legs=2.0, chest=True):
    """w per unit squared of every point above where lying puts it: the hips and chest their own thickness (a little
    over), the head its own, the knees and ankles legs units, the elbows (prone, on the forearms) 1.6."""
    h = heights(S, Q, facing, dz)
    lim = dict(pelvis=max(S['pr']) + 0.4)
    if chest:
        lim['chest'] = max(S['cr']) + 0.5
    if head:
        lim['head'] = max(S['hr']) + 0.6
    for s in 'lr':
        lim[s + 'knee'] = legs; lim[s + 'ankle'] = legs
        if elbows:
            lim[s + 'elbow'] = 1.6
    return w * sum(max(0.0, h[k] - v) ** 2 for k, v in lim.items())


def legs_down(S, Q, facing, dz, w=0.003, ankle=5.0, knee=7.5):
    """a falling soldier's feet stay below his hips: w a unit squared of an ankle above ankle units or a knee above
    knee units (TS's flung limbs at shoulder height are his arms; fitted with a leg, a leg flew up past his head)."""
    h = heights(S, Q, facing, dz)
    return w * sum(max(0.0, h[s + 'ankle'] - ankle) ** 2 + max(0.0, h[s + 'knee'] - knee) ** 2 for s in 'lr')
