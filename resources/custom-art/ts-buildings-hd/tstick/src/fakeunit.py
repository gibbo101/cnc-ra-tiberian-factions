"""the Tick Tank's voxel frame recovered from the units chat's .glb (TTNK.VXL isn't here): index space -> the unit frame
(voxels after lowering) is p = mn + idx * sc, read off the tail boxes and the ring well (to ~0.002 voxels)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(HERE, 'src'), HERE):
    if os.path.isdir(_p) and _p not in sys.path:
        sys.path.insert(0, _p)
os.environ.setdefault('TS_HANDOFF', os.path.join(HERE, 'handoff'))      # TS's voxels aren't read: the frame is recovered

SC = np.array([0.99923, 0.98056, 0.94737])
MN = np.array([-18.547, -10.2965, -0.0027])


class Sec:
    def __init__(self):
        self.mn, self.scale = MN.copy(), SC.copy()


class FakeUnit:
    def __init__(self):
        self.sections = [Sec()]

    def pose(self, sec, hf=0):
        return np.eye(3), np.zeros(3)


def cfg(canvas=(384, 384), ppu=6.25, origin=None, px_scale=1.5):
    import nvox as N
    c = N.Cfg('03-TTNK', [('TTNK.VXL', None, None)], 'tsttnk', canvas=canvas, ppu=ppu, origin=origin)
    c.px_scale = px_scale
    return c
