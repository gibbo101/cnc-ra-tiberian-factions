"""3D model of the Helipad as .glb (export3d.py), into PKG/3d/helipad.glb:
  pad / pad-damaged              the bib (GTHPADBB): the pad, its landing circle, steps, railing and approach lights
  helipad / helipad-damaged      the machinery (GTHPAD): the block, the tanks, the pipes, the control box
Markers: "landing" (the landing circle's centre on the pad: where a helicopter sets down), "light-1".."light-17" (the
approach lights, the four ends of the cross first, the middle last).
Cameras: "camera-ts-angle" (256 x 256 = ts-angle/ frames), "camera-ra-grid" (256 x 256 = ra-grid/ frames).

    python3 hpadexport.py [h]"""
import os, sys, time
import numpy as np
import export3d as E, hpad as M, hpadmat as MM, hpaddamage as MD, hpadrender as RR

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-helipad-hd')


def gl_point(x, y, z):
    return (x / E.CELL, z / E.CELL, y / E.CELL)


def export(h=1.2):
    g = E.GLB()
    p = M.P
    xr, yr = (-136.0, 136.0), (-136.0, 182.0)
    plain = lambda X, Y, **k: M.scene(X, Y, **k)
    dmg = MD.model(1)
    parts = (('pad', plain, None, 0, dict(pad=True), 40.0), ('pad-damaged', dmg, MD, 1, dict(pad=True), 40.0),
             ('helipad', plain, None, 0, dict(pad=False), 100.0), ('helipad-damaged', dmg, MD, 1, dict(pad=False), 100.0))
    for name, fn, dm, level, kw, zm in parts:
        t0 = time.time()
        mk = dict(layout='ts'); mk.update(kw)
        v, f, n, rgb, house = E.build_part(fn, MM, xr, yr, h, zm, mk, damage=dm, level=level)
        g.mesh(name, v, f, n, rgb, house)
        print(name, len(v), 'verts', len(f), 'tris', '%.0fs' % (time.time() - t0), flush=True)
    q = p['pad']
    g.marker('landing', gl_point(q['land']['c'][0], q['land']['c'][1], q['h']), 0.0,
             extras=dict(note='the landing circle centre on the pad'))
    for k, (lx, ly) in enumerate(M.light_points(p)):
        g.marker(f'light-{k + 1}', gl_point(lx, ly, q['h'] + 1.0), 0.0,
                 extras=dict(note='GTHPAD_A approach light (ring %d of the cross: 4 = an end, 0 = the middle)' % M.light_rings()[k]))
    ppc = RR.ISO_K * 0.265165 * 128.0
    ox, oy = RR.origin('iso')
    right_ts = np.array([0.7071, 0.0, -0.7071]); up_ts = np.array([-0.3536, 0.8660, -0.3536])
    W, H = RR.CANVAS['iso']
    tgt = right_ts * ((W / 2 - ox) / ppc) + up_ts * (-(H / 2 - oy) / ppc)
    g.camera('camera-ts-angle', 315.0, 30.0, tgt, W / 2 / ppc, H / 2 / ppc,
             extras=dict(note=f'TS angle: orthographic, 30 degrees, looking north-west; render {W} x {H} px = ts-angle/ frames'))
    Wr, Hr = RR.CANVAS['ra']
    oxr, oyr = RR.origin('ra')
    up_ra = np.array([0.0, np.cos(np.radians(32)), -np.sin(np.radians(32))])
    g.camera('camera-ra-grid', 0.0, 32.0, up_ra * ((oyr - Hr / 2) / 128.0), Wr / 2 / 128.0, Hr / 2 / 128.0,
             extras=dict(note=f'RA grid: orthographic, 32 degrees, looking north; render {Wr} x {Hr} px = ra-grid/ frames'))
    os.makedirs(f'{PKG}/3d', exist_ok=True)
    g.save(f'{PKG}/3d/helipad.glb', extras=dict(
        units='1 = one cell (128 px on the RA grid); x east, y up, z south; origin = the 2x2 foundation centre on the ground',
        foundation="2 x 2 cells (x -1..1, z -1..1), TS's way round (the RA grid version is not turned)"))


if __name__ == '__main__':
    export(float(sys.argv[1]) if len(sys.argv) > 1 else 1.2)
