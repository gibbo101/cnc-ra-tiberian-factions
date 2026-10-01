"""the Titan's cannon (MMCHBARL.VXL) as convex parts, read from its voxels (34 x 6 x 7; index i spans i..i+1):
  breech    x 0-4: a house-colour block (TS draws it hollow: a frame round the breech)
  housing   x 4-12: house colour, its top raised over the left half at x 6-9
  bracket   x 1-12, z 0-2.5: grey cheek plates under the housing (where it hangs on the mount)
  taper     x 12-18: house colour core, grey sides
  tube      x 18-31: steel, round, 3 voxels high, 4 across
  muzzle    x 31-34: a dark brake a touch wider
Voxel frame: x forward, y to the left, z up; bounds from the VXL map the indices into TS's voxel space."""
import numpy as np
import rc

BREECH, HOUSING, BRACKET, TAPER, TUBE, MUZZLE = 31, 32, 33, 34, 35, 36
VMIN = np.array([-7.37359476, -2.80305886, -4.86872673]); VMAX = np.array([26.16302872, 2.82052255, 1.91045213])
VSIZE = np.array([34, 6, 7])
HVA_T = np.array([67.3584213, -90.5694427, 256.247070]) / 12.0      # the HVA's translation x the section scale


def vox_to_vu(p):
    """voxel index coords -> TS voxel units (x fwd, y left, z up), in the barrel's pivot frame."""
    return VMIN + np.asarray(p, float) * (VMAX - VMIN) / VSIZE + HVA_T


def local_parts():
    """parts in voxel index coordinates (x fwd, y LEFT, z up)."""
    B = lambda lo, hi, comp, ch=0.35, name='': rc.box((np.array(lo) + np.array(hi)) / 2, np.eye(3),
                                                       (np.array(hi) - np.array(lo)) / 2, comp, chamfer=ch, name=name)
    parts = [B((0.0, 1.0, 1.0), (4.0, 5.0, 7.0), BREECH, 0.45, 'breech'),
             B((4.0, 0.0, 2.6), (12.0, 5.0, 6.0), HOUSING, 0.4, 'housing'),
             B((5.5, 0.0, 5.5), (9.0, 3.0, 7.0), HOUSING, 0.35, 'hump'),
             B((1.0, 1.0, 0.0), (12.0, 5.0, 2.8), BRACKET, 0.35, 'bracket'),
             B((12.0, 1.0, 2.0), (18.5, 5.0, 5.0), TAPER, 0.5, 'taper'),
             rc.cylinder((18.0, 3.0, 3.45), (31.2, 3.0, 3.45), 1.55, TUBE, 'tube'),
             rc.cylinder((31.0, 3.0, 3.45), (34.0, 3.0, 3.45), 1.8, MUZZLE, 'muzzle')]
    return parts


def body_parts(off=(0.0, 0.0, 0.0), s=1.0, pitch=0.0):
    """the cannon in the upper body's frame (u fwd, v right, w up), in TS px: voxel units x s, then shifted by off.
    pitch (degrees, + = muzzle up) turns it about its trunnion (the housing's centre)."""
    # voxel index -> vu is affine: diag scale + translation; then flip y (left -> right) and scale s
    k = (VMAX - VMIN) / VSIZE
    A = np.diag([k[0], -k[1], k[2]]) * s
    t = (np.array([VMIN[0], -VMIN[1], VMIN[2]]) + np.array([HVA_T[0], -HVA_T[1], HVA_T[2]])) * s + np.asarray(off, float)
    out = []
    for p in local_parts():
        cons = []
        for c in p.cons:
            if c.kind == 'plane':
                # n.x <= d with x = A^-1 (y - t)  ->  (A^-T n).y <= d + (A^-T n).t
                Ainv = np.linalg.inv(A)
                n2 = Ainv.T @ c.n
                cons.append(rc.Plane(n2, c.d + n2 @ t))
            elif c.kind == 'cyl':
                a2 = A @ c.a; a2 = a2 / np.linalg.norm(a2)
                cons.append(rc.Cyl(A @ c.c + t, a2, c.r * s * float(np.sqrt(abs(k[1] * k[2])))))
        sp = None if p.sphere is None else (A @ p.sphere[0] + t, p.sphere[1] * s * float(np.max(np.abs(np.diag(A)))) / s)
        out.append(rc.Part(cons, p.comp, p.name, sp))
    if pitch:
        piv = A @ np.array([8.0, 3.0, 4.0]) + t
        R = rc.rot_y(-np.deg2rad(pitch))
        out = [p.moved(R, piv - R @ piv) for p in out]
    return out
