"""the Mammoth Mk. II's voxels (HMEC.VXL, 13 sections) posed by HMEC.HVA: voxel centres in the unit's frame
(x forward, y left, z up, voxel units), per section and HVA frame."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import vxl

from paths import HANDOFF
D = HANDOFF + '/03-TSHMEC/ts-original/'
SECS = vxl.read_vxl(D + 'HMEC.VXL')
NAMES, MATS = vxl.read_hva(D + 'HMEC.HVA')
PAL = vxl.read_pal(D + 'UNITTEM.PAL')
STEPS = (0, 2, 4, 6, 8, 11, 13, 15)          # the mod's 8 walk steps: HVA frames


def sec_scale(s):
    return (np.asarray(s['max']) - np.asarray(s['min'])) / np.asarray(s['size'], float)


def sec_matrix(i, hf):
    """(R, t): section i's voxel index space -> unit frame at HVA frame hf: p = R (min + (v + 0.5) sc) + t."""
    s = SECS[i]
    M = MATS[hf, i]
    R = M[:, :3]; t = M[:, 3] * s['det']
    return R, t


def posed_points(hf, which=None):
    out = []
    for i, s in enumerate(SECS):
        if which is not None and i not in which:
            continue
        v = np.argwhere(s['col'] >= 0).astype(float)
        R, t = sec_matrix(i, hf)
        loc = np.asarray(s['min']) + (v + 0.5) * sec_scale(s)
        out.append(loc @ R.T + t)
    return np.concatenate(out, 0)
