"""
t4export.py - the Mammoth Mk. I v2's 3D model as a .glb: the hull (its section's parts) and the turret (the turret's
section and the barrels', under a 'turret' node that turns about the unit's position) under the unit facing east (the
mod's facing 24), each part's mesh exact (cut from its planes and curved surfaces) in its section's own frame; vertex
colours the frames' paint (house colour: COLOR_1 white); the camera the mod's frames use (32 degrees) framing the 512
canvas.

Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
Origin: the unit's position on the ground.

    python3 t4export.py out.glb
"""
import sys
from paths import HANDOFF
sys.path.insert(0, HANDOFF + '/renderer')
import numpy as np
from export3d import orient
import rcexport as RX
import t4v2 as T, t4mat as MM
from t4cam import unit_to_world, camera, PPU, ELEV, CANVAS
from glbtools import AnimGLB, quat, orthonormal, subdivide

UNITS_PER_CELL = 192.0 / PPU                # unit-frame units per cell: 192 canvas px a cell, 6.23 px a unit
A = np.array([[1, 0, 0], [0, 0, 1.0], [0, 1.0, 0]])      # world (x east, y south, z up) -> glTF (x east, y up, z south)
VARIED = (T.SLEEVE, T.COLLAR)        # parts whose paint changes across a face: subdivided


def colours(sec, part, V, N):
    """vertex colours (the section's local frame V, N): the frames' paint for the part (albedo, no light), house
    green on house parts, TS's light band on the sleeves and collars."""
    F = T.SECTIONS[sec]
    q = (V - F.mn) / F.sc
    if part.comp in T.HOUSE:
        base = np.tile(MM.GREEN, (len(V), 1)); house = np.ones(len(V))
        if part.comp in (T.SLEEVE, T.COLLAR):
            band = (N[:, 1] < -0.7) & (q[:, 2] > 1.0) & (q[:, 2] < 1.9)
            if part.comp == T.SLEEVE:
                band &= (q[:, 0] > 2.8) & (q[:, 0] < 8.8)
            base[band] = MM.LIGHT; house[band] = 0
        return base, house
    base = np.tile(np.asarray(MM.PAINT.get(part.comp, MM.GREY), float), (len(V), 1))
    return np.minimum(base, 255.0), np.zeros(len(V))


def export(path):
    m = T.model()
    glb = AnimGLB()
    root = glb.group('MammothMk1')
    Mx = unit_to_world(24)                                  # unit frame -> world, facing east
    face = glb.group('unit_facing_east', root, rotation=quat(A @ Mx))
    # the sections stay in the unit's frame (x forward, y left, z up), each placed by its HVA (frame 0) and lowered
    # onto the ground (TS's hull floats GZ over its HVA origin)
    tur = glb.group('turret', face)
    nverts = 0
    for sec, parent in (('hull', face), ('tur', tur), ('barl', tur)):
        F = T.SECTIONS[sec]
        R, t = F.pose()
        t = t + np.array([0.0, 0.0, -T.GZ])
        nd = glb.group({'hull': 'hull', 'tur': 'turret_body', 'barl': 'barrels'}[sec], parent,
                       translation=t / UNITS_PER_CELL, rotation=quat(orthonormal(R)))
        seen = {}
        for p in m[sec]:
            curved = any(c.kind != 'plane' for c in p.cons)
            if curved:
                V, Fc = RX.curved_mesh(p, n=24)
                P, Fi, N = RX.smooth_shaded(V, Fc)
            else:
                mm = RX.part_mesh(p)
                if mm is None:
                    continue
                P, Fi, N = RX.flat_shaded(*mm)
                if p.comp in VARIED:
                    P, Fi, N = subdivide(P, Fi, N, 0.8)
            rgb, house = colours(sec, p, P, N)
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
    glb.save(path, extras=dict(units='1.0 = one cell (128 px in the game; 192 px on the canvas)', facing='east',
                               turret="the 'turret' node turns about the unit's position (its local z axis, up: the unit's frame is x forward, y left, z up)"))
    return path, nverts


if __name__ == '__main__':
    print(export(sys.argv[1]))
