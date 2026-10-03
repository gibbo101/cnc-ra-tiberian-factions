"""3D model of the Firestorm Generator (GAFIRE) as .glb (export3d.py), into PKG/3d/firestorm-generator.glb:

  firestorm-generator          the building, healthy, without the arm and dome (as GTFIRE: the pit open)
  firestorm-generator-damaged  the same, damaged
  arm-dome                     the crane arm with the dome, closed on the pit (GTFIRE_A 00 / the end of the build-up).
                               GTFIRE_A lifts it: the dome rises straight up 68 units (0.53 cells) over the 20 frames
                               while the arm turns about its pivot (marker "arm-pivot") to stay over it
Markers: "arm-pivot" (the arm's hinge on the back fin's top), "pit" (the emitter's tip in the middle of the pit, where
GTFIRE_B's lightning starts), "lamp-1" / "lamp-2" (GTFIRE_C's lamps on the front and back fins' tips).
Cameras: "camera-ts-angle" and "camera-ra-grid" (both 384 x 384 = the ts-angle/ and ra-grid/ frames).
The model is in its own frame, the same way round in both views (the fins west, the pit east).

    python3 fgenexport.py [h]   h = sampling step in units (default 1.5)"""
import os, sys, time
import numpy as np
import export3d as E, fgen as M, fgenmat as MM, fgendamage as MD

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-firestorm-generator-hd')
ARMSET = {M.ARM, M.ARMG, M.DOME, M.DOMEC}


def gl_point(x, y, z):
    """model point (units: x east, y south, z up) -> glTF (cells: x east, y up, z south)."""
    return (x / E.CELL, z / E.CELL, y / E.CELL)


def arm_only(fn):
    def f(X, Y, **k):
        k = dict(k); k['arm'] = 0.0
        sc = fn(X, Y, **k)
        sc.H = np.zeros_like(sc.H); sc.C = np.zeros_like(sc.C)
        keep = []
        for s in sc.slabs:
            cs = set(np.unique(s.comp[s.top >= 0]).tolist())
            if cs and cs <= ARMSET:
                keep.append(s)
        sc.slabs = keep
        return sc
    return f


def export(h=1.5):
    g = E.GLB()
    p = M.P
    xr, yr, zmax = (-200.0, 200.0), (-140.0, 140.0), 150.0
    plain = lambda X, Y, **k: M.scene(X, Y, **k)
    dmg = MD.model(1)
    parts = (('firestorm-generator', plain, None, 0, zmax), ('firestorm-generator-damaged', dmg, MD, 1, zmax),
             ('arm-dome', arm_only(plain), None, 0, zmax))
    for name, fn, dm, level, zm in parts:
        t0 = time.time()
        v, f, n, rgb, house = E.build_part(fn, MM, xr, yr, h, zm, dict(layout='ts'), damage=dm, level=level)
        g.mesh(name, v, f, n, rgb, house)
        print(name, len(v), 'verts', len(f), 'tris', '%.0fs' % (time.time() - t0), flush=True)
    a_ = p['arm']
    g.marker('arm-pivot', gl_point(*a_['pivot']), 0.0,
             extras=dict(note="the arm's hinge on the back fin's top: GTFIRE_A turns the arm about it (axis level, across the arm)"))
    d, m = p['drum'], p['mech']
    g.marker('pit', gl_point(d['c'][0], d['c'][1], m['h'] + 2.0), 0.0,
             extras=dict(note="the emitter's tip in the middle of the pit (GTFIRE_B's lightning starts here)"))
    for i, q in enumerate(p['fins']):
        tip = M.fin_tip(q, p['base']['h']) - np.array([0, 0, p['lamps']['down']])
        g.marker(f'lamp-{i + 1}', gl_point(*tip), 0.0,
                 extras=dict(note=f"GTFIRE_C, the lamp on the {('front', 'back')[i]} fin's tip (blue-white)"))
    # cameras framing the delivered canvases exactly
    K = 4.04
    ppc = K * 0.265165 * 128.0
    ox, oy = 84.0 * K - 146.0, 90.0 * K - 137.0
    right_ts = np.array([0.7071, 0.0, -0.7071]); up_ts = np.array([-0.3536, 0.8660, -0.3536])
    tgt = right_ts * ((192.0 - ox) / ppc) + up_ts * (-(192.0 - oy) / ppc)
    g.camera('camera-ts-angle', 315.0, 30.0, tgt, 384 / 2 / ppc, 384 / 2 / ppc,
             extras=dict(note='TS angle: orthographic, 30 degrees, looking north-west; render 384 x 384 px = ts-angle/ frames'))
    up_ra = np.array([0.0, np.cos(np.radians(32)), -np.sin(np.radians(32))])
    oy_ra = 320.0 - np.sin(np.radians(32.0)) * 128.0
    g.camera('camera-ra-grid', 0.0, 32.0, up_ra * ((oy_ra - 192.0) / 128.0), 384 / 2 / 128.0, 384 / 2 / 128.0,
             extras=dict(note='RA grid: orthographic, 32 degrees, looking north; render 384 x 384 px = ra-grid/ frames'))
    os.makedirs(f'{PKG}/3d', exist_ok=True)
    g.save(f'{PKG}/3d/firestorm-generator.glb', extras=dict(
        units='1 = one cell (128 px on the RA grid); x east, y up, z south; origin = the 3x2 foundation centre on the ground',
        foundation='3 x 2 cells (x -1.5..1.5, z -1..1), the same way round on the RA grid',
        arm=f"GTFIRE_A frame k lifts the dome {p['dome']['lift']:.0f} units x lift(k/19) (a slow start, then steady, "
            "held at the top); GTFIRE_B and the idle keep it raised"))


if __name__ == '__main__':
    h = float(sys.argv[1]) if len(sys.argv) > 1 else 1.5
    export(h)
