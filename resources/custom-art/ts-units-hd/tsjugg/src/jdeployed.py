"""
jdeployed.py - the Juggernaut deployed: the base (jbase.py, fitted to DJUGG frame 0), the cabin (jfitcabin.py, fitted to
DJUGG_A's 32 facings) turning on the base's pivot column, and the three barrels (TS's own DJUGGBAR.VXL) on the cabin's
front, level at rest or raised about their breech to aim.

World frame: x east, y south, z up, units = TS sprite px, origin = the pivot's foot on the ground (the base frame).

    base + cabin: TS's DJUGG and DJUGG_A frames share one 96 x 96 frame, so the fits' screen points give the cabin's
    axis against the base: the cabin turns about the pivot's axis (its x from both fits' mean), and its own w = 0 sits
    (cy0 - by0) / cos 30 below the base's ground (the cabin fit fixes its height and its depth only together, and its
    axis is the pivot's).
"""
import os
import json
import numpy as np
import rc
import jugg as JG
import jbase as JB
import jbase2 as JB2
import jfitcabin as JC
from paths import HANDOFF

HERE = os.path.dirname(os.path.abspath(__file__)) + '/'
H = HANDOFF + '/04-TSJUGG/'


def load_fits(base='fit_base2_a.json', cabin='fit_hatch_a.json'):
    jb = json.load(open(HERE + base)); jc = json.load(open(HERE + cabin))
    two = 'yw' in jb['P']                                       # jbase2: the walker's legs + two side limbs
    PB = dict(JB2.P0 if two else JB.P0); PB.update(jb['P'])
    PC = dict(JG.P0); PC.update(jc['P'])
    axis_x = (jb['bax'] + jc['cax']) / 2                      # the common axis (TS px, DJUGG frame)
    base_off = jb['bax'] - axis_x                              # the base's own fitted x against it
    cab_dz = -(jc['cy0'] - jb['by0']) / np.cos(np.deg2rad(30.0))
    return dict(PB=PB, PC=PC, axis=(axis_x, jb['by0']), base_off=base_off, cab_off=jc['cax'] - axis_x,
                cab_dz=cab_dz, two=two, bax=jb['bax'], by0=jb['by0'])


def base_world(M):
    parts = JB2.base_parts(M['PB'], M['bax'], M['by0'], JB2.S32) if M.get('two') else JB.base_parts(M['PB'])
    return [p.moved(np.eye(3), (M['base_off'], 0.0, 0.0)) for p in parts]


def cabin_world(M, k32):
    """the cabin at the mod's facing k32 (32, counter-clockwise from north)."""
    R = JG.facing_matrix((32 - k32) % 32, 32)
    return [p.moved(R, (M['cab_off'], 0.0, M['cab_dz'])) for p in JC.cabin_parts(M['PC'])]


# --------------------------------------------------------------------------------------------- the barrel voxel
class Barrels:
    """DJUGGBAR.VXL's voxels as points: index (i along the barrels, j across, k up) and TS's colour class."""

    def __init__(self, sub=3):
        import sys
        import vxl
        s = vxl.read_vxl(H + 'ts-original/DJUGGBAR.VXL')[0]
        c = s['col']
        pal = np.asarray(vxl.read_pal(H + 'ts-original/UNITTEM.PAL'), float)
        pal = pal * 255 if pal.max() <= 1.5 else pal
        idx = np.argwhere(c >= 0)
        col = c[c >= 0]
        self.idx = idx.astype(float); self.col = col
        v = pal[col].mean(1)
        cls = np.where(v >= 140, 2, 5)
        cls[(col >= 16) & (col <= 31)] = 1                     # TS's remap: house colour
        self.cls = cls
        o = (np.arange(sub) + 0.5) / sub - 0.5
        off = np.stack(np.meshgrid(o, o, o, indexing='ij'), -1).reshape(-1, 3)
        self.pts = (self.idx[:, None, :] + 0.5 + off[None]).reshape(-1, 3)      # voxel i spans i .. i + 1
        self.pcls = np.repeat(cls, len(off))
        self.size = c.shape
        # TS's own size per voxel along each axis (the section's bounds over its voxel counts)
        self.vscale = (np.asarray(s['max'], float) - np.asarray(s['min'], float)) / np.asarray(c.shape, float)
        # the voxel's own origin (TS's pivot for it), in index coordinates
        self.origin = -np.asarray(s['min'], float) / self.vscale

    def body(self, s, mount, hinge, pitch=0.0, pts=None):
        """the points in the cabin's body frame (u forward, v right, w up): the voxel scaled by s, its hinge point
        (voxel index coordinates) at mount (u, v, w), raised by pitch degrees about the hinge."""
        p = ((self.pts if pts is None else pts) - np.asarray(hinge, float)) * self.vscale * s
        # voxel axes: i forward, j across (to the left as TS draws it: j grows to the voxel's +y), k up
        u, v, w = p[:, 0], -p[:, 1], p[:, 2]
        a = np.deg2rad(pitch)
        u2 = u * np.cos(a) - w * np.sin(a); w2 = u * np.sin(a) + w * np.cos(a)
        return np.stack([u2 + mount[0], v + mount[1], w2 + mount[2]], -1)
