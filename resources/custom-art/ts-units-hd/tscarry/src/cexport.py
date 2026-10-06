"""
cexport.py - the Carryall v2's 3D model as a .glb: the unit (one section, TRNSPORT.VXL's) under the unit facing east
(the mod's facing 24, as the other units' models), where TS's HVA puts it over the unit's position (as the frames draw
it; the game lifts the frame by the aircraft's height in flight).  Each part's mesh is exact (cut from its planes and curved surfaces) in the section's own frame,
placed by its HVA; vertex colours are the frames' paint (cmat: albedo, no light, its areas only - its joints, slots
and bolts are finer than the mesh), COLOR_1 white where TS paints house colour.  The camera 'camera_mod' is the frames'
(orthographic, 32 degrees above the ground, looking north): through it the model as delivered is frame 24.

Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
Origin: the unit's position on the ground.

    python3 cexport.py tscarry.glb
"""
import sys
from paths import HANDOFF
sys.path.insert(0, HANDOFF + '/renderer')
import numpy as np
from export3d import orient
import rcexport as RX
import rcrender as RR
import cmodel as T, cmat as MM
from ccam import unit_to_world, camera, PPU, ELEV, CANVAS
from glbtools import AnimGLB, quat, orthonormal, subdivide

UNITS_PER_CELL = 192.0 / PPU                        # unit-frame units (voxels) per cell: 192 canvas px a cell
A = np.array([[1, 0, 0], [0, 0, 1.0], [0, 1.0, 0]])      # world (x east, y south, z up) -> glTF (x east, y up, z south)
SUB = 0.9                                           # faces subdivided to carry the paint (voxels)


class _Px:
    """the paint's inputs (obmat.materials) for mesh vertices instead of pixels."""

    def __init__(self, comp, q, n_unit, z_unit, cam):
        k = len(comp)
        self.comp = np.asarray(comp, np.int32); self.hitmask = np.ones(k, bool)
        self.lu, self.lv, self.lw = [q[:, i].astype(np.float32) for i in range(3)]
        self.x, self.y = self.lu, self.lv
        self.z = z_unit.astype(np.float32)
        self.nx, self.ny, self.nz = [n_unit[:, i].astype(np.float32) for i in range(3)]
        self.pose_R = np.eye(3)
        self.cam = cam
        self.L = cam.cam_to_world(RR.L_CAM)
        self.no_fine = True


def export(path):
    m = T.model()
    glb = AnimGLB()
    root = glb.group('Carryall')
    Mx = unit_to_world(24)                                  # unit frame -> world, facing east
    face = glb.group('unit_facing_east', root, rotation=quat(A @ Mx))
    F = T.FH
    R, t = F.pose()
    nd = glb.group('hull', face, translation=t / UNITS_PER_CELL, rotation=quat(orthonormal(R)))
    cam = camera()
    seen = {}
    nverts = 0
    for p in m['hull']:
        curved = any(c.kind != 'plane' for c in p.cons)
        if curved:
            Vv, Fc = RX.curved_mesh(p, n=24)
            P, Fi, Nn = RX.smooth_shaded(Vv, Fc)
        else:
            mm = RX.part_mesh(p)
            if mm is None:
                continue
            P, Fi, Nn = RX.flat_shaded(*mm)
        P, Fi, Nn = subdivide(P, Fi, Nn, SUB)
        ln = np.linalg.norm(Nn, axis=1, keepdims=True)
        Nn = np.where(ln > 1e-6, Nn / np.maximum(ln, 1e-12), np.array([0.0, 0.0, 1.0]))
        q = (P - F.mn) / F.sc
        zu = (P @ R.T + t)[:, 2]
        px = _Px(np.full(len(P), p.comp), q, Nn @ R.T, zu, cam)
        alb, _, _ = MM.materials(px)
        rgb = np.clip(alb, 0, 255)
        house = MM.house_mask(px, alb).astype(float)
        Pg = P / UNITS_PER_CELL
        Fi = orient(Pg, Fi, Nn)
        seen[p.name] = seen.get(p.name, 0) + 1
        nm = p.name if seen[p.name] == 1 else '%s_%d' % (p.name, seen[p.name])
        glb.part(nm, nd, Pg.astype(np.float32), Fi, Nn.astype(np.float32), rgb, house)
        nverts += len(P)
    c = CANVAS[0] / 2.0
    gx, gy = cam.ground(np.array([c]), np.array([c]))
    half = CANVAS[0] / 192.0 / 2.0
    glb.camera('camera_mod', 0.0, ELEV, list(A @ np.array([gx[0], gy[0], 0.0]) / UNITS_PER_CELL), half, half,
               extras=dict(note='orthographic, %g degrees above the ground, looking north; frames the %d x %d canvas'
                           % (ELEV, CANVAS[0], CANVAS[1])))
    glb.save(path, extras=dict(units='1.0 = one cell (128 px in the game; 192 px on the canvas)', facing='east',
                               house='COLOR_1 white where TS paints house colour (house green in COLOR_0 there)'))
    return path, nverts


if __name__ == '__main__':
    print(export(sys.argv[1]))
