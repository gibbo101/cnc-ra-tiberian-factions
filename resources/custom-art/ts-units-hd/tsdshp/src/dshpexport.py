"""
dshpexport.py - the TS Dropship v3's 3D model as a .glb: the ship (one section, DSHP.VXL's) under the unit facing east
(the mod's facing 24, as the other units' models), placed so the origin is the point the ship turns about in the game
(the canvas centre: 7.67 voxels aft of TS's HVA origin), so turning the 'unit_facing_east' node about its up axis gives
every facing.  Each part's mesh is exact (cut from its planes and curved surfaces) in the section's own frame, placed
by its HVA; the lofted tail and nose carry their smooth bodies' normals (as the frames are shaded); vertex colours are
the frames' paint (dshpmat: albedo, no light), COLOR_1 white where TS paints house colour (house green there, as in the
frames; v2 showed GDI's gold).  The camera 'camera_mod' is the frames' (orthographic, 32 degrees above the ground, looking
north): through it the model as delivered (facing east) is facings/ frame 24; turned to face west, frames/ frame 0.

Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (128 px on this canvas and in the game).

    python3 dshpexport.py tsdshp.glb
"""
import sys
from paths import HANDOFF
sys.path.insert(0, HANDOFF + '/renderer')
import numpy as np
from export3d import orient
import rcexport as RX
import rcrender as RR
import dshpmodel as T, dshpmat as MM
from dshpcam import unit_to_world, camera, origin_for, PPU, ELEV, CANVAS, ORIGIN
from glbtools import AnimGLB, quat, orthonormal, subdivide

CELL_PX = 128.0
UNITS_PER_CELL = CELL_PX / PPU                      # unit-frame units (voxels) per cell
A = np.array([[1, 0, 0], [0, 0, 1.0], [0, 1.0, 0]])      # world (x east, y south, z up) -> glTF (x east, y up, z south)
AXIS_U = np.array([-(CANVAS[0] / 2 - ORIGIN[0]) / PPU, 0.0, 0.0])    # the turning point in the unit frame
LOFT = (T.TAIL, T.NOSE)
SUB = 1.1                                           # faces subdivided to carry the paint (voxels)


class _Px:
    """the paint's inputs (dshpmat.materials) for mesh vertices instead of pixels."""

    def __init__(self, comp, q, n_unit, cam):
        k = len(comp)
        self.comp = np.asarray(comp, np.int32); self.hitmask = np.ones(k, bool)
        self.lu, self.lv, self.lw = [q[:, i].astype(np.float32) for i in range(3)]
        self.x, self.y, self.z = self.lu, self.lv, self.lw
        self.nx, self.ny, self.nz = [n_unit[:, i].astype(np.float32) for i in range(3)]
        self.gnx, self.gny, self.gnz = self.nx.copy(), self.ny.copy(), self.nz.copy()
        self.pose_R = np.eye(3)
        self.cam = cam
        self.L = cam.cam_to_world(RR.L_CAM)
        self.no_fine = True


def field_normals(comp, q, n_face):
    """the lofts' smooth normals at q points (the section's frame), where they agree with the face's."""
    import dshpvox as V
    import dshpnose as NS
    from scipy.ndimage import map_coordinates
    sc = T.FH.sc
    if comp == T.TAIL:
        G = np.gradient(V.region_smoothed(*T.G_TAIL, sig=(1.8, 1.3, 1.3)))
        g = -np.stack([map_coordinates(gi, [q[:, 0] - 0.5, q[:, 1] - 0.5, q[:, 2] - 0.5], order=1) for gi in G], 1)
    else:
        g = NS.normals_q(q)
    n = g / sc[None, :]
    n = n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-9)
    ok = (n * n_face).sum(1) > 0.55
    return np.where(ok[:, None], n, n_face)


def export(path):
    m = T.model()
    glb = AnimGLB()
    root = glb.group('Dropship')
    Mx = unit_to_world(24)                                  # unit frame -> world, facing east
    face = glb.group('unit_facing_east', root, rotation=quat(A @ Mx))
    F = T.FH
    R, t = F.pose()
    nd = glb.group('hull', face, translation=(t - AXIS_U) / UNITS_PER_CELL, rotation=quat(orthonormal(R)))
    cam = camera(origin_for(24))
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
        q = (P - F.mn) / F.sc
        if p.comp in LOFT:
            Nn = field_normals(p.comp, q, Nn)
        ln = np.linalg.norm(Nn, axis=1, keepdims=True)
        Nn = np.where(ln > 1e-6, Nn / np.maximum(ln, 1e-12), np.array([0.0, 0.0, 1.0]))
        px = _Px(np.full(len(P), p.comp), q, Nn, cam)
        alb, _, _ = MM.materials(px)
        rgb = np.clip(alb, 0, 255)
        house = MM.house_mask(px, alb).astype(float)
        Pg = P / UNITS_PER_CELL
        Fi = orient(Pg, Fi, Nn)
        seen[p.name] = seen.get(p.name, 0) + 1
        nm = p.name if seen[p.name] == 1 else '%s_%d' % (p.name, seen[p.name])
        glb.part(nm, nd, Pg.astype(np.float32), Fi, Nn.astype(np.float32), rgb, house)
        nverts += len(P)
    # the camera: the frames', centred on the canvas centre's ground point (relative to the turning point)
    c = CANVAS[0] / 2.0
    gx, gy = cam.ground(np.array([c]), np.array([c]))
    ax_w = (Mx @ AXIS_U)[:2]
    target = A @ np.array([gx[0] - ax_w[0], gy[0] - ax_w[1], 0.0]) / UNITS_PER_CELL
    half = CANVAS[0] / CELL_PX / 2.0
    glb.camera('camera_mod', 0.0, ELEV, list(target), half, half,
               extras=dict(note='orthographic, %g degrees above the ground, looking north; frames the %d x %d canvas: the '
                                'model as delivered (facing east) is facings/ frame 24, turned to face west frames/ '
                                'frame 0' % (ELEV, CANVAS[0], CANVAS[1])))
    glb.save(path, extras=dict(units='1.0 = one cell (128 px on this canvas and in the game)', facing='east',
                               origin="the point the ship turns about in the game (the canvas centre), %.2f voxels "
                                      "(%.3f cell) aft of TS's HVA origin" % (-AXIS_U[0], -AXIS_U[0] / UNITS_PER_CELL),
                               house='COLOR_1 white where TS paints house colour (house green in COLOR_0 there)'))
    return path, nverts


if __name__ == '__main__':
    print(export(sys.argv[1]))
