"""3D model of the Sensor Array as .glb (export3d.py), into PKG/3d/sensor-array.glb:
  sensor-array / sensor-array-damaged   deployed (GTDPSA): outriggers down, the mast up, the dish open
  sensor-array-stowed                   as it drives up (GTDPSAMK 00): the mast down along the deck, the outriggers in
Markers: "mast-pivot" (the mast swings about the north-south axis through it, from lying along the deck pointing east
to upright), "dish-centre" (the radar dish's rim centre, deployed).
Cameras: "camera-ts-angle" (256 x 416 = ts-angle/ frames), "camera-ra-grid" (256 x 416 = ra-grid/ frames).

    python3 dpsaexport.py [h]"""
import os, sys, time
import numpy as np
import export3d as E, dpsa as M, dpsamat as MM, dpsadamage as MD, dpsarender as RR, dpsabuild as DB

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-sensor-array-hd')


def gl_point(x, y, z):
    return (x / E.CELL, z / E.CELL, y / E.CELL)


def export(h=1.0):
    g = E.GLB()
    p = M.P
    xr, yr = (-90.0, 80.0), (-70.0, 70.0)
    plain = lambda X, Y, **k: M.scene(X, Y, **k)
    dmg = MD.model(1)
    parts = (('sensor-array', plain, None, 0, {}, 190.0), ('sensor-array-damaged', dmg, MD, 1, {}, 190.0),
             ('sensor-array-stowed', plain, None, 0, dict(prog=DB.SEQ[0]), 100.0))
    for name, fn, dm, level, kw, zm in parts:
        t0 = time.time()
        mk = dict(layout='ts'); mk.update(kw)
        v, f, n, rgb, house = E.build_part(fn, MM, xr, yr, h, zm, mk, damage=dm, level=level)
        g.mesh(name, v, f, n, rgb, house)
        print(name, len(v), 'verts', len(f), 'tris', '%.0fs' % (time.time() - t0), flush=True)
    pv = p['mast']['pivot']
    g.marker('mast-pivot', gl_point(*pv), 0.0,
             extras=dict(note='the mast pivots about the north-south axis through this point: 0 = lying along the deck '
                              'pointing east, 90 degrees = upright'))
    df = M.head_pose(p, 90.0, 1.0)
    g.marker('dish-centre', gl_point(*df['C']), 0.0, extras=dict(note='the radar dish rim centre; its axis points '
                                                                       'east-south-east and up (GTDPSA_A flashes its bar)'))
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
    right_ra = np.array([1.0, 0.0, 0.0])
    tgt_ra = right_ra * ((Wr / 2 - oxr) / 128.0) + up_ra * ((oyr - Hr / 2) / 128.0)
    g.camera('camera-ra-grid', 0.0, 32.0, tgt_ra, Wr / 2 / 128.0, Hr / 2 / 128.0,
             extras=dict(note=f'RA grid: orthographic, 32 degrees, looking north; render {Wr} x {Hr} px = ra-grid/ frames'))
    os.makedirs(f'{PKG}/3d', exist_ok=True)
    g.save(f'{PKG}/3d/sensor-array.glb', extras=dict(
        units='1 = one cell (128 px on the RA grid); x east, y up, z south; origin = the 1x1 foundation centre on the ground',
        foundation="1 x 1 cell (x -0.5..0.5, z -0.5..0.5), TS's way round (the RA grid version is not turned)"))


if __name__ == '__main__':
    export(float(sys.argv[1]) if len(sys.argv) > 1 else 1.0)
