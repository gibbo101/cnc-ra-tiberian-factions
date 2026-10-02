"""3D models of the Service Depot and the Dropship Bay as .glb (export3d.py):
  PKG/3d/depot.glb      pad / pad-damaged (the bib, GTDEPTBB), depot / depot-damaged (the gantry and machine, GTDEPT),
                        arm (GTDEPT_C's boom and tool as at C 05-10: tipped 53 degrees towards the pad about the
                        "arm-pivot" marker's north-south axis); markers "arm-pivot", "pad-centre"; cameras for both views
  DROP/3d/dropship-bay.glb   pad / pad-damaged; marker "pad-centre"; cameras for both views

    python3 deptexport.py depot|drop [h]"""
import os, sys, time
import numpy as np
import export3d as E, dept as M, deptmat as MM, deptdamage as MD

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-service-depot-hd')
DROP = os.environ.get('DROP', '/home/claude/work/out/ts-dropship-bay-hd')


def gl_point(x, y, z):
    return (x / E.CELL, z / E.CELL, y / E.CELL)


def cameras(g, RR, ra_fwd, ra_target_xy=(0.0, 0.0)):
    ppc = RR.ISO_K * 0.265165 * 128.0
    ox, oy = RR.origin('iso')
    right_ts = np.array([0.7071, 0.0, -0.7071]); up_ts = np.array([-0.3536, 0.8660, -0.3536])
    W, H = RR.CANVAS['iso']
    tgt = right_ts * ((W / 2 - ox) / ppc) + up_ts * (-(H / 2 - oy) / ppc)
    g.camera('camera-ts-angle', 315.0, 30.0, tgt, W / 2 / ppc, H / 2 / ppc,
             extras=dict(note=f'TS angle: orthographic, 30 degrees, looking north-west; render {W} x {H} px = ts-angle/ frames'))
    Wr, Hr = RR.CANVAS['ra']
    oxr, oyr = RR.origin('ra')
    s32, c32 = np.sin(np.radians(32)), np.cos(np.radians(32))
    if ra_fwd == 'west':            # the RA grid frames are turned: RA's north is the model's west
        up_ra = np.array([-s32, c32, 0.0]); right = np.array([0.0, 0.0, -1.0]); yaw = 270.0
    else:
        up_ra = np.array([0.0, c32, -s32]); right = np.array([1.0, 0.0, 0.0]); yaw = 0.0
    x0, y0, x1, y1 = RR.PLOT['ra']
    tgt = np.array(gl_point(ra_target_xy[0], ra_target_xy[1], 0.0)) + up_ra * ((oyr - Hr / 2) / 128.0) + \
        right * ((Wr / 2 - oxr) / 128.0)
    g.camera('camera-ra-grid', yaw, 32.0, tgt, Wr / 2 / 128.0, Hr / 2 / 128.0,
             extras=dict(note=f'RA grid: orthographic, 32 degrees, looking along the model\'s {ra_fwd} (RA north); '
                              f'render {Wr} x {Hr} px = ra-grid/ frames'))


def export_depot(h=1.2):
    import deptrender as RR
    g = E.GLB()
    p = M.P
    xr, yr = (-196.0, 160.0), (-160.0, 160.0)
    plain = lambda X, Y, **k: M.scene(X, Y, **k)
    dmg = MD.model(1)
    parts = (('pad', plain, None, 0, dict(pad=True), 30.0), ('pad-damaged', dmg, MD, 1, dict(pad=True), 30.0),
             ('depot', plain, None, 0, dict(pad=False), 90.0), ('depot-damaged', dmg, MD, 1, dict(pad=False), 90.0),
             ('arm', plain, None, 0, dict(parts=('arm',), arm=8), 150.0))
    for name, fn, dm, level, kw, zm in parts:
        t0 = time.time()
        mk = dict(layout='ts'); mk.update(kw)
        v, f, n, rgb, house = E.build_part(fn, MM, xr, yr, h, zm, mk, damage=dm, level=level)
        g.mesh(name, v, f, n, rgb, house)
        print(name, len(v), 'verts', len(f), 'tris', '%.0fs' % (time.time() - t0), flush=True)
    a = p['arm']
    g.marker('arm-pivot', gl_point(*a['p0']), 0.0, extras=dict(
        note='the repair arm turns about this point\'s north-south axis: GTDEPT_C frames 3-5 tip it from upright towards the '
             'pad (east) by 20, 38, 53 degrees; its tool hangs from the boom\'s end'))
    q = p['pad']
    g.marker('pad-centre', gl_point(q['c'][0], q['c'][1], q['h']), 0.0, extras=dict(note='the pad\'s centre on its top'))
    cameras(g, RR, 'west')
    os.makedirs(f'{PKG}/3d', exist_ok=True)
    g.save(f'{PKG}/3d/depot.glb', extras=dict(
        units='1 = one cell (128 px on the RA grid); x east, y up, z south; origin = the 3x3 foundation centre on the ground',
        foundation="3 x 3 cells (x -1.5..1.5, z -1.5..1.5), TS's way round (the RA grid frames are turned a quarter: "
                   "TS's east is RA's south)"))


def export_drop(h=1.0):
    import droprender as RR
    g = E.GLB()
    p = M.P
    q = p['pad']
    xr, yr = (-140.0, 165.0), (-140.0, 165.0)
    plain = lambda X, Y, **k: M.scene(X, Y, **k)
    dmg = MD.model(1)
    for name, fn, dm, level in (('pad', plain, None, 0), ('pad-damaged', dmg, MD, 1)):
        t0 = time.time()
        mk = dict(layout='ts', pad=True)
        v, f, n, rgb, house = E.build_part(fn, MM, xr, yr, h, 30.0, mk, damage=dm, level=level)
        g.mesh(name, v, f, n, rgb, house)
        print(name, len(v), 'verts', len(f), 'tris', '%.0fs' % (time.time() - t0), flush=True)
    g.marker('pad-centre', gl_point(q['c'][0], q['c'][1], q['h']), 0.0,
             extras=dict(note='the pad\'s centre on its top (the RA grid frames centre it on the plot)'))
    cameras(g, RR, 'west', ra_target_xy=q['c'])
    os.makedirs(f'{DROP}/3d', exist_ok=True)
    g.save(f'{DROP}/3d/dropship-bay.glb', extras=dict(
        units='1 = one cell (128 px on the RA grid); x east, y up, z south; origin = the 3x3 foundation centre on the '
              'ground (TS\'s: the pad sits 12.25 units south-east of it)',
        note='the Service Depot\'s pad alone (GTDEPTBB), as the mod uses it for the Dropship Bay'))


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'depot'
    h = float(sys.argv[2]) if len(sys.argv) > 2 else 1.2
    (export_depot if which == 'depot' else export_drop)(h)
