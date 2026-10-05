"""
hvrexport.py - the Hover MLRS v2's 3D model as a .glb: the hull (with the pad the rack turns on), and the missile rack
(the support and the pods) under a 'rack' node on the pad's centre, where the game seats it (Luke: on the hull's back,
centred across it: 12.54 voxels aft of the unit's position, 0.20 to its left), the node's origin on the rack's pivot,
so turning the node about its local z axis turns the rack on the pad; both under the unit facing east (the mod's
facing 24).  Each part's mesh is exact (cut from its planes and curved surfaces) in its section's
own frame, placed by the section's HVA; vertex colours are the frames' paint (house colour: COLOR_1 white); the camera
is the one the mod's hull frames use (32 degrees), framing the 192 canvas.

Axes: glTF's own (y up): x east, y up, z south.  1.0 = one cell (96 px on this canvas, 128 px in the game).
Origin: the unit's position on the ground.

    python3 hvrexport.py tshvr.glb
"""
import sys
from paths import HANDOFF
sys.path.insert(0, HANDOFF + '/renderer')
import numpy as np
from export3d import orient
import rcexport as RX
import hvrmodel as T, hvrmat as MM
from hvrcam import unit_to_world, camera, PPU, ELEV, CANVAS
from glbtools import AnimGLB, quat, orthonormal, subdivide

CELL_PX = 96.0                              # canvas px per cell (4 canvas px per classic pixel)
UNITS_PER_CELL = CELL_PX / PPU              # unit-frame units (voxels) per cell
A = np.array([[1, 0, 0], [0, 0, 1.0], [0, 1.0, 0]])      # world (x east, y south, z up) -> glTF (x east, y up, z south)
VARIED = (T.OCHRE, T.DECK, T.DECK_D, T.POD, T.GLASS, T.TURNTABLE)    # paint changes across a face: subdivided


def colours(sec, part, V, N):
    """vertex colours (the section's local frame V, N): the frames' paint for the part (albedo, no light)."""
    F = T.SECTIONS[sec]
    q = (V - F.mn) / F.sc
    qx, qy, qz = q[:, 0], q[:, 1], q[:, 2]
    c = part.comp
    house = np.zeros(len(V))
    base = np.tile(np.asarray(MM.PAINT.get(c, MM.DECK_C), float), (len(V), 1))
    if c in T.HOUSE:
        base[:] = MM.GREEN; house[:] = 1
        if c == T.POD:
            band = ((N[:, 0] < -0.7) & (qz > 7.0)) | ((N[:, 2] > 0.7) & (qx < 0.9))
            base[band] = MM.OCHRE; house[band] = 0
    elif c == T.OCHRE:
        top = N[:, 2] > 0.7
        yi = np.where(qy < T.HYC, qy, 2 * T.HYC - qy)
        base[top & ((qx < 7.0) | ((qx > 31.0) & (qx < 38.1)))] = MM.KHAKI
        base[top & (qx > 7.0) & (qx < 13.0) & (yi > 4.0)] = MM.KHAKI
        base[(np.abs(N[:, 1]) > 0.7) & (qz < 3.25) & (qx > 1.0)] = MM.OCHRE * 0.7
    elif c == T.GLASS:
        t = np.clip((qz - 6.5) / 0.85, 0, 1)[:, None]
        base = MM.GLASS_LO * (1 - t) + MM.GLASS_HI * t
    elif c == T.TURNTABLE:
        rr = np.hypot((qx - T.PAD_C[0]) * F.sc[0], (qy - T.PAD_C[1]) * F.sc[1])
        base[(N[:, 2] > 0.7) & (rr < T.PAD_R[1] - 0.05)] = MM.TURN_C * 0.78
    if sec == 'hull' and c == T.OCHRE:
        # inside the front intakes: dark (the walls' and frames' faces round it)
        yo = np.where(qy < T.HYC, qy, 2 * T.HYC - qy)
        fx = T.face_x(qz)
        ins = ((yo > T.INTAKE_Y[0] - 0.03) & (yo < T.INTAKE_Y[1] + 0.03) & (qz > T.INTAKE_Z[0] - 0.03) &
               (qz < T.INTAKE_Z[1] + 0.03) & (qx > fx - T.INTAKE_D - 0.08) & (qx < fx + 0.02))
        base[ins] = MM.DUCT_C
    return np.minimum(base, 255.0), house


def export(path):
    m = T.model()
    glb = AnimGLB()
    root = glb.group('HoverMLRS')
    Mx = unit_to_world(24)                                  # unit frame -> world, facing east
    face = glb.group('unit_facing_east', root, rotation=quat(A @ Mx))
    # the sections stay in the unit's frame (x forward, y left, z up), each placed by its HVA (frame 0); the rack under
    # the rack node on the pad's centre (the game's seat), its pivot on the node's origin as the rack frames draw it
    rk = glb.group('rack', face, translation=np.array([T.SEAT_U[0], T.SEAT_U[1], 0.0]) / UNITS_PER_CELL)
    nverts = 0
    for sec, parent, nm_ in (('hull', face, 'hull'), ('rack', rk, 'rack_body')):
        F = T.SECTIONS[sec]
        R, t = F.pose()
        if sec == 'rack':
            t = t + T.FRAME_SHIFT
        nd = glb.group(nm_, parent, translation=t / UNITS_PER_CELL, rotation=quat(orthonormal(R)))
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
                P, Fi, N = subdivide(P, Fi, N, 0.6)
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
    half = CANVAS[0] / CELL_PX / 2.0
    glb.camera('camera_mod', 0.0, ELEV, list(A @ np.array([gx[0], gy[0], 0.0]) / UNITS_PER_CELL), half, half,
               extras=dict(note='orthographic, %g degrees above the ground, looking north; frames the %d x %d canvas'
                           % (ELEV, CANVAS[0], CANVAS[1])))
    glb.save(path, extras=dict(units='1.0 = one cell (128 px in the game; 96 px on this canvas)', facing='east',
                               rack="the 'rack' node sits on the pad's centre, %.2f voxels (%.3f cell) aft of the unit's "
                                    "position and %.2f voxels (%.3f cell) to its left, where the game seats it, and "
                                    "turns about its own local z axis (up; the unit's frame is x forward, y left, z up)"
                                    % (-T.SEAT_U[0], -T.SEAT_U[0] / UNITS_PER_CELL, T.SEAT_U[1],
                                       T.SEAT_U[1] / UNITS_PER_CELL)))
    return path, nverts


if __name__ == '__main__':
    print(export(sys.argv[1]))
