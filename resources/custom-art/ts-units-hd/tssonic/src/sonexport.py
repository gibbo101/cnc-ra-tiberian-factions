"""
sonexport.py - the Disruptor v5's 3D model as a .glb: the hull, and the turret (the turntable ring and the turret with
its dish and arm) under a 'turret' node seated 0.43 cell aft of the unit's position on the green rear deck, its pad's
back at the deck's back (Luke; TS's own TurretOffset=-64 is a quarter cell), scaled 0.98 about its base as the mod's
frames draw it (its pad, the turntable and rim, 0.70 of TS's radius in the model), turning about its own middle; both under the unit facing east (the mod's facing 24).  Each part's mesh is exact
(cut from its planes and curved surfaces) in its section's own frame, placed by the section's HVA (the turret's two
sections centred on the pivot, as the frames have them); vertex colours are the frames' paint (house colour: COLOR_1
white); the camera is the one the mod's hull frames use (32 degrees), framing the 448 canvas.

Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
Origin: the unit's position on the ground.

    python3 sonexport.py tssonic.glb
"""
import sys
from paths import HANDOFF
sys.path.insert(0, HANDOFF + '/renderer')
import numpy as np
from export3d import orient
import rcexport as RX
import sonmodel as T, sonmat as MM
from soncam import unit_to_world, camera, PPU, ELEV, CANVAS, K_TUR, Z_BASE
from glbtools import AnimGLB, quat, orthonormal, subdivide

UNITS_PER_CELL = 192.0 / PPU                # unit-frame units per cell: 192 canvas px a cell, 6.27 px a unit
A = np.array([[1, 0, 0], [0, 0, 1.0], [0, 1.0, 0]])      # world (x east, y south, z up) -> glTF (x east, y up, z south)
TURRET_OFFSET = -13.186 / UNITS_PER_CELL     # cells along the unit's x: the turret's pad on the deck, 0.51 voxel inside its back and sides (Luke)
VARIED = (T.DISH, T.HAZARD, T.BODY, T.CROSS, T.STRUT, T.GREEN, T.BRACKET, T.GLASS)    # paint changes across a face


def phase(v, per):
    return np.abs(np.mod(v + per / 2, per) - per / 2)


def colours(sec, part, V, N):
    """vertex colours (the section's local frame V, N): the frames' paint for the part (albedo, no light)."""
    F = T.SECTIONS[sec]
    q = (V - F.mn) / F.sc
    qx, qy, qz = q[:, 0], q[:, 1], q[:, 2]
    c = part.comp
    house = np.zeros(len(V))
    base = np.tile(np.asarray(MM.PAINT.get(c, MM.GREY), float), (len(V), 1))
    if c in T.HOUSE:
        base[:] = MM.GREEN; house[:] = 1                    # v4: plain, the rear grille too (Luke)
    elif c == T.DISH:
        base[:] = MM.GREY
        base[(N[:, 0] > 0.3) & (qz > 6.6) & (qz < 10.6)] = MM.WHITE
    elif c == T.HAZARD:
        base[phase(qx - qy, 1.7 / MM.KS) < 0.42 / MM.KS] = MM.HAZ_K
    elif c == T.BODY and sec == 'hull':
        top = N[:, 2] > 0.7
        base[top & (qy > 13.0) & (qx > 24.0) & (qx < 44.0)] = MM.TRENCH_C
        base[top & (qx > 21.0) & (qx < 24.8) & (qy < 12.0)] = MM.OCHRE
        base[top & (qx > 21.0) & (qx < 24.8) & (qy >= 12.0)] = MM.OCHRE_D * 0.8
    elif c == T.CROSS:
        base[qy < 6.0] = MM.BLACK_C * 1.2
    elif c == T.STRUT and sec == 'tur':
        base[(qz > 9.6) & (qx < 8.4)] = MM.BLUE_C
    elif c == T.GLASS:
        t = np.clip((qz - 8.6) / 1.4, 0, 1)[:, None]
        base = MM.GLASS_LO * (1 - t) + MM.GLASS_HI * t
    elif c == T.BRACKET:
        base[:] = MM.HAZ_Y
        base[phase(qx + 0.55 * qz, 0.62 / MM.KS) < 0.16 / MM.KS] = MM.HAZ_K
    return np.minimum(base, 255.0), house


def export(path):
    m = T.model()
    glb = AnimGLB()
    root = glb.group('Disruptor')
    Mx = unit_to_world(24)                                  # unit frame -> world, facing east
    face = glb.group('unit_facing_east', root, rotation=quat(A @ Mx))
    # the sections stay in the unit's frame (x forward, y left, z up), each placed by its HVA (frame 0); the hull raised
    # onto the ground (TS's hull reaches GZ below its HVA origin); the turret's sections centred on the pivot, under the
    # turret node, which scales them by K_TUR about the turret's base (Z_BASE up), as the frames draw it
    tur = glb.group('turret', face, translation=(TURRET_OFFSET, 0.0, Z_BASE * (1 - K_TUR) / UNITS_PER_CELL))
    glb.nodes[tur]['scale'] = [K_TUR] * 3
    nverts = 0
    for sec, parent, nm_ in (('hull', face, 'hull'), ('ring', tur, 'turntable'), ('tur', tur, 'turret_body')):
        F = T.SECTIONS[sec]
        R, t = T.pose(sec)
        nd = glb.group(nm_, parent, translation=t / UNITS_PER_CELL, rotation=quat(orthonormal(R)))
        seen = {}
        for p in m[sec]:
            curved = any(c.kind != 'plane' for c in p.cons)
            if curved:
                V, Fc = RX.curved_mesh(p, n=24)
                P, Fi, N = RX.smooth_shaded(V, Fc)
                if p.comp in VARIED:
                    P, Fi, N = subdivide(P, Fi, N, 0.5)
            else:
                mm = RX.part_mesh(p)
                if mm is None:
                    continue
                P, Fi, N = RX.flat_shaded(*mm)
                if p.comp in VARIED:
                    P, Fi, N = subdivide(P, Fi, N, 0.5)
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
                               turret="the 'turret' node sits 0.43 cell aft of the unit's position on the rear deck "
                                      "(its pad's back at the deck's back), is scaled 0.98 about the turret's base (the "
                                      "mod's turret frames' size), and turns about its own local z axis (up; the unit's "
                                      "frame is x forward, y left, z up)"))
    return path, nverts


if __name__ == '__main__':
    print(export(sys.argv[1]))
