"""
mwarexport.py - the Mobile War Factory's 3D model as a .glb: the unit facing east (the mod's facing 24), each
part's mesh exact (cut from its planes and curved surfaces) in TS's voxel section's frame, placed by its HVA; vertex
colours the frames' paint (house colour: COLOR_1 white); the camera the mod's frames use (32 degrees) framing the 384
canvas.  TS's voxel sits GZ above its HVA origin: the model is lowered onto the ground, as in the frames.

Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
Origin: the unit's position on the ground.

    python3 mwarexport.py tsmwar.glb
"""
import sys
from paths import HANDOFF
sys.path.insert(0, HANDOFF + '/renderer')
import numpy as np
from export3d import orient
import rcexport as RX
import mwarmodel as T, mwarmat as MM
from mwarcam import unit_to_world, camera, PPU, ELEV, CANVAS, GZ
from glbtools import AnimGLB, quat, orthonormal, subdivide

UNITS_PER_CELL = 192.0 / PPU                # unit-frame units per cell: 192 canvas px a cell, 6.26 px a unit
A = np.array([[1, 0, 0], [0, 0, 1.0], [0, 1.0, 0]])      # world (x east, y south, z up) -> glTF (x east, y up, z south)


def colours(part, V, N):
    """vertex colours: the frames' paint for the part (albedo, no light), house green on house parts."""
    if part.comp in T.HOUSE:
        base = np.tile(MM.GREEN, (len(V), 1)); house = np.ones(len(V))
        return base, house
    base = np.tile(np.asarray(MM.PAINT.get(part.comp, MM.GREY), float), (len(V), 1))
    return np.minimum(base, 255.0), np.zeros(len(V))


def export(path):
    m = T.model()
    glb = AnimGLB()
    root = glb.group('MobileWarFactory')
    Mx = unit_to_world(24)                                  # unit frame -> world, facing east
    face = glb.group('unit_facing_east', root, rotation=quat(A @ Mx))
    R, t = T.F.pose()
    nd = glb.group('body', face, translation=(t + np.array([0.0, 0.0, -GZ])) / UNITS_PER_CELL,
                   rotation=quat(orthonormal(R)))
    seen = {}
    nverts = 0
    for p in m:
        curved = any(c.kind != 'plane' for c in p.cons)
        if curved:
            V, Fc = RX.curved_mesh(p, n=24)
            P, Fi, N = RX.smooth_shaded(V, Fc)
        else:
            mm = RX.part_mesh(p)
            if mm is None:
                continue
            P, Fi, N = RX.flat_shaded(*mm)
        rgb, house = colours(p, P, N)
        Pg = P / UNITS_PER_CELL
        Fi = orient(Pg, Fi, N)
        seen[p.name] = seen.get(p.name, 0) + 1
        nm = p.name if seen[p.name] == 1 else '%s_%d' % (p.name, seen[p.name])
        glb.part(nm, nd, Pg.astype(np.float32), Fi, N.astype(np.float32), rgb, house)
        nverts += len(P)
    cam = camera()
    c = CANVAS[0] / 2.0
    gx, gy = cam.ground(np.array([c]), np.array([c]))
    half = CANVAS[0] / 192.0 / 2.0
    glb.camera('camera_mod', 0.0, ELEV, list(A @ np.array([gx[0], gy[0], 0.0]) / UNITS_PER_CELL), half, half,
               extras=dict(note='orthographic, %g degrees above the ground, looking north; frames the %d x %d canvas'
                           % (ELEV, CANVAS[0], CANVAS[1])))
    glb.save(path, extras=dict(units='1.0 = one cell (128 px in the game; 192 px on the canvas)', facing='east'))
    return path, nverts


if __name__ == '__main__':
    print(export(sys.argv[1]))
