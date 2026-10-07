"""
prisexport.py - the Prism Tank v2's 3D model as a .glb: the hull, and the prism turret under a 'turret' node on the unit's
position, scaled 0.974 about its base as the mod's turret frames draw it, turning about its own local z axis; both under
the unit facing east (the mod's facing 24).  Each part's mesh is exact (cut from its planes and curved surfaces) in its
section's own frame, placed by the section's HVA (identity for SREF and SREFTUR), each section centred side to side as
the frames have them; vertex colours are the frames' paint (house colour: COLOR_1 white; the emitter's face its glow);
the camera is the one the mod's hull frames use (32 degrees), framing the 384 canvas.

Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (192 px on this canvas, 128 px in the game).
Origin: the unit's position on the ground.

    python3 prisexport.py r2pris.glb
"""
import sys
from paths import HANDOFF
sys.path.insert(0, HANDOFF + '/renderer')
import numpy as np
from export3d import orient
import rcexport as RX
import prismodel as T, prismat as MM
from priscam import unit_to_world, camera, PPU, ELEV, CANVAS, K_TUR, Z_BASE
from glbtools import AnimGLB, quat, orthonormal, subdivide

UNITS_PER_CELL = 192.0 / PPU                # unit-frame units per cell: 192 canvas px a cell, 5.03 px a unit
A = np.array([[1, 0, 0], [0, 0, 1.0], [0, 1.0, 0]])      # world (x east, y south, z up) -> glTF (x east, y up, z south)
VARIED = (T.FAN, T.BELT, T.EMITTER, T.BODY, T.DECK)                  # paint changes across a face


def phase(v, per, off=0.0):
    return np.abs(np.mod(v - off + per / 2, per) - per / 2)


def colours(sec, part, V, N):
    """vertex colours (the section's local frame V, N): the frames' paint for the part (albedo, no light)."""
    F = T.SECTIONS[sec]
    q = (V - F.mn) / F.sc
    qx, qy, qz = q[:, 0], q[:, 1], q[:, 2]
    c = part.comp
    house = np.zeros(len(V))
    base = np.tile(np.asarray(MM.PAINT.get(c, MM.MID), float), (len(V), 1))
    if c in T.HOUSE:
        base[:] = MM.GREEN; house[:] = 1
    elif c == T.BODY:
        top = N[:, 2] > 0.7
        base[top & (qx > 36.5)] = MM.FRONT_C
        base[(N[:, 0] > 0.3) & (N[:, 2] > 0.3)] = MM.MID * 0.95
    elif c == T.FAN:
        th = np.arctan2(qy - T.FAN_C[1], qx - T.FAN_C[0]); rr = np.hypot(qx - T.FAN_C[0], qy - T.FAN_C[1])
        base[(phase(th + 0.25 * rr, 2 * np.pi / 7) < 0.32) & (rr > 0.9)] = MM.DARK * 0.9
    elif c == T.EMITTER:
        x0, x1, y0, y1, z0, z1 = T.EMIT
        e = np.minimum(np.minimum(qy - y0, y1 - qy), np.minimum(qz - z0, z1 - qz))
        t = np.clip(e / 0.9, 0, 1)[:, None]
        base = MM.GLOW_EDGE * (1 - t) + MM.GLOW * t
    return np.minimum(base, 255.0), house


def export(path):
    m = T.model()
    glb = AnimGLB()
    root = glb.group('PrismTank')
    Mx = unit_to_world(24)                                  # unit frame -> world, facing east
    face = glb.group('unit_facing_east', root, rotation=quat(A @ Mx))
    # the sections stay in the unit's frame (x forward, y left, z up), each placed by its HVA (frame 0) and raised onto
    # the ground; the prism under the turret node, which scales them by K_TUR about the turret's base
    # (Z_BASE up), as the frames draw it
    tur = glb.group('turret', face, translation=(0.0, 0.0, Z_BASE * (1 - K_TUR) / UNITS_PER_CELL))
    glb.nodes[tur]['scale'] = [K_TUR] * 3
    nverts = 0
    for sec, parent, nm_ in (('hull', face, 'hull'), ('tur', tur, 'prism')):
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
                               turret="the 'turret' node sits on the unit's position, is scaled %.3f about the turret's "
                                      "base (the mod's turret frames' size) and turns about its own local z axis (up; "
                                      "the unit's frame is x forward, y left, z up)" % K_TUR))
    return path, nverts


if __name__ == '__main__':
    print(export(sys.argv[1]))
