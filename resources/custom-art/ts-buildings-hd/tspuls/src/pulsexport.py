"""3D model of the EMP Pulse Cannon as .glb (export3d.py), into PKG/3d/pulse-cannon.glb:
  pulse-cannon / pulse-cannon-damaged   NAPULS 0 / 1, without the head
  head                                  the head at NAPULS_A facing 00 (north); it turns about the vertical through
                                        the marker "head-pivot" (anticlockwise seen from above: 08 west, 16 south, 24 east)
Markers: "head-pivot" (the drum's centre, on its top).
Cameras: "camera-ts-angle" (256 x 256 = ts-angle/ frames), "camera-ra-grid" (256 x 320 = ra-grid/ frames).

    python3 pulsexport.py [h]"""
import os, sys, time
import numpy as np
import export3d as E, puls as M, pulsmat as MM, pulsdamage as MD, pulsrender as RR

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-pulse-cannon-hd')


def gl_point(x, y, z):
    return (x / E.CELL, z / E.CELL, y / E.CELL)


def head_only(f=0):
    comps = sorted(M.HEAD)

    def fn(X, Y, **kw):
        kw = dict(kw); kw['head'] = f
        sc = M.scene(X, Y, **kw)
        sc.H = np.zeros_like(sc.H); sc.C = np.zeros_like(sc.C)
        sl = []
        for s in sc.slabs:
            k = (s.top >= 0) & np.isin(s.comp, comps)
            if k.any():
                s.top = np.where(k, s.top, -1.0)
                sl.append(s)
        sc.slabs = sl
        return sc
    return fn


def export(h=1.25):
    g = E.GLB()
    p = M.P
    xr, yr = (-135.0, 135.0), (-135.0, 135.0)
    plain = lambda X, Y, **k: M.scene(X, Y, **k)
    parts = [('pulse-cannon', plain, None, 0, {}, xr, yr, 120.0),
             ('pulse-cannon-damaged', MD.model(1), MD, 1, {}, xr, yr, 120.0),
             ('head', head_only(0), None, 0, dict(head=0), (-70.0, 70.0), (-70.0, 70.0), 170.0)]
    for name, fn, dm, level, kw, xr_, yr_, zm in parts:
        t0 = time.time()
        mk = dict(layout='ts'); mk.update(kw)
        v, f, n, rgb, house = E.build_part(fn, MM, xr_, yr_, h, zm, mk, damage=dm, level=level)
        g.mesh(name, v, f, n, rgb, house)
        print(name, len(v), 'verts', len(f), 'tris', '%.0fs' % (time.time() - t0), flush=True)
    g.marker('head-pivot', gl_point(0.0, 0.0, p['drum']['z']), 0.0,
             extras=dict(note='NAPULS_A: the head turns about the vertical through here (32 facings, 00 north, '
                              'anticlockwise seen from above)'))
    # cameras
    ppc = RR.ISO_K * 0.265165 * 128.0
    ox, oy = RR.origin('iso')
    right_ts = np.array([0.7071, 0.0, -0.7071]); up_ts = np.array([-0.3536, 0.8660, -0.3536])
    W, H = RR.CANVAS['iso']
    tgt = right_ts * ((W / 2 - ox) / ppc) + up_ts * (-(H / 2 - oy) / ppc)
    g.camera('camera-ts-angle', 315.0, 30.0, tgt, W / 2 / ppc, H / 2 / ppc,
             extras=dict(note=f'TS angle: orthographic, 30 degrees, looking north-west; render {W} x {H} px = ts-angle/ frames'))
    Wr, Hr = RR.CANVAS['ra']
    oxr, oyr = RR.origin('ra')
    s32 = np.sin(np.radians(32.0))
    Xw, Yw = Wr / 2 - oxr, (Hr / 2 - oyr) / s32
    g.camera('camera-ra-grid', 270.0, 32.0, np.array(gl_point(Xw, Yw, 0.0)), Wr / 2 / 128.0, Hr / 2 / 128.0,
             extras=dict(note=f'RA grid: orthographic, 32 degrees, looking north; render {Wr} x {Hr} px = ra-grid/ frames'))
    os.makedirs(f'{PKG}/3d', exist_ok=True)
    g.save(f'{PKG}/3d/pulse-cannon.glb', extras=dict(
        units='1 = one cell (128 px on the RA grid); x east, y up, z south; origin = the 2x2 foundation centre on the ground',
        foundation="TS's 2 x 2 cells (x -1..1, z -1..1), TS's way round on both"))


if __name__ == '__main__':
    export(float(sys.argv[1]) if len(sys.argv) > 1 else 1.25)
