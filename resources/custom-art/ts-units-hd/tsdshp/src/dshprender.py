"""the TS Dropship's HD frame (TSDSHP: 656 x 656 at EA's density; frame 0 the ship side-on and level facing west, in
GDI's gold; frames 1-3 its shadow frames, made from frame 0 as the mod's packer makes them: frame 0 scaled to 55%, 70%
and 85% about the canvas centre), built straight from TS's DSHP.VXL (vxlunit / voxrender); the RA-grid camera
(32 degrees), 6.33 canvas px per voxel, the voxel's origin at canvas (279.4, 326.8) as in-mod/ has it (found by matching
the voxel to in-mod/: overlap 0.98).  It never takes house colour: TS's remap voxels are painted GDI's gold, the gold
in-mod/ shows there.

    python3 dshprender.py frames 0 [ss] [outdir] [sky]
"""
import os, sys, time
from paths import HANDOFF
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import vxl, vxlunit as VU, voxrender as VR, rcrender as RR
from frameio import save

D = HANDOFF + '/26-TSDSHP/ts-original/'
CANVAS = (656, 656)
PPU = 6.33
ORIGIN = (279.44, 326.77)
ELEV = 32.0
BOUNDS = ((-60, 60), (-60, 60), (-5, 40))
PX_SCALE = 1.0               # EA's density: the game draws this canvas 1:1
TSN = float(os.environ.get('TSN', '0.6'))
GOLD = None                  # set from in-mod/ (see gold())
SHADOW_SCALES = (0.55, 0.70, 0.85)


def load():
    pal = vxl.read_pal(D + 'UNITTEM.PAL')
    secs = vxl.read_vxl(D + 'DSHP.VXL'); names, mats = vxl.read_hva(D + 'DSHP.HVA')
    return VR.Unit([VU.Section(s, pal, sigma=0.3, denoise=0.3) for s in secs], [(mats, i) for i in range(len(secs))])


def camera():
    return RR.Cam((0, -1), ELEV, PPU, ORIGIN)


def ship(unit, ss=4, sky=True, house=None):
    """frame 0: facing west (the mod's facing 8)."""
    old = VR.GREEN
    if house is not None:
        VR.GREEN = np.asarray(house, np.float32)
    try:
        img, trim = VR.frame(unit, 8, 0, camera(), CANVAS, BOUNDS, ss=ss, sky=sky, px_scale=PX_SCALE,
                             sharp={i: 2.0 for i in range(len(unit.sections))}, speckle=(0.75, 1.2), grime_z=0,
                             ts_normals=TSN, with_shadow=False, ground_ao=False)
    finally:
        VR.GREEN = old
    return img, trim


def scaled(img, s):
    """frame 0 scaled by s about the canvas centre (as the mod's packer makes the shadow frames)."""
    W, H = img.size
    w, h = round(W * s), round(H * s)
    small = img.resize((w, h), Image.LANCZOS)
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
    out.paste(small, ((W - w) // 2, (H - h) // 2))
    return out
