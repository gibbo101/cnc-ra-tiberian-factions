"""3D model of the Limpet Mine (DLIMPET) as .glb (export3d.py), into PKG/3d/limpet-mine.glb:

  limpet-mine           the mine dug in (DLIMPET): the ring on the ground, the claws out with their points in the
                        earth, only the body's top showing inside the ring
  limpet-mine-damaged   the same, damaged (the east claw's point snapped, a bite out of the ring)
  limpet-drone          the drone in flight before it lands (DLIMPMK 19: hovering, claws swung half out), its ring's
                        foot 48 units (0.37 cells) over the ground
Markers: "lens" (the dug-in top, which DLIMP_A flashes), "lamp" (the drone's amber lamp, DLIMPMK).
Cameras: "camera-ts-angle" and "camera-ra-grid" (both 256 x 256 = the ts-angle/ and ra-grid/ frames).

    python3 dlimpexport.py [h]   h = sampling step in units (default 0.75)"""
import os, sys, time
import numpy as np
import export3d as E, dlimp as M, dlimpmat as MM, dlimpdamage as MD, dlimpbuild as WB

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-limpet-mine-hd')


def gl_point(x, y, z):
    """model point (units: x east, y south, z up) -> glTF (cells: x east, y up, z south)."""
    return (x / E.CELL, z / E.CELL, y / E.CELL)


def export(h=0.75):
    g = E.GLB()
    p = M.P
    xr, yr = (-72.0, 72.0), (-72.0, 72.0)
    plain = lambda X, Y, **k: M.scene(X, Y, **k)
    dmg = MD.model(1)
    fly = WB.SEQ[WB.EXPORT_FLY]['pose']
    parts = (('limpet-mine', plain, None, 0, dict(layout='ra'), 40.0),
             ('limpet-mine-damaged', dmg, MD, 1, dict(layout='ra'), 40.0),
             ('limpet-drone', plain, None, 0, dict(layout='ra', pose=fly), 120.0))
    for name, fn, dm, level, mk, zm in parts:
        t0 = time.time()
        v, f, n, rgb, house = E.build_part(fn, MM, xr, yr, h, zm, mk, damage=dm, level=level)
        g.mesh(name, v, f, n, rgb, house)
        print(name, len(v), 'verts', len(f), 'tris', '%.0fs' % (time.time() - t0), flush=True)
    st = p['settled']
    zt = st['z'] - st['sink'] + p['body']['prof'][-1][0]
    g.marker('lens', gl_point(0.0, 0.0, zt), 0.0, extras=dict(note="the dug-in top inside the ring: DLIMP_A flashes it "
                                                                  "white, then house green fading back to dark"))
    q = p['lamp']
    a = np.radians(q['az'])
    r_ = float(np.interp(q['dz'], *np.asarray(p['body']['prof'], float).T))
    g.marker('lamp', gl_point(np.cos(a) * r_, np.sin(a) * r_, fly['z'] + q['dz']), 0.0,
             extras=dict(note='the drone\'s lamp (limpet-drone): DLIMPMK cycles it amber, red, dark red every frame'))
    # cameras framing the delivered canvases exactly
    K = 3.93
    ppc = K * 0.265165 * 128.0
    ox, oy = 48.0 * K - 60.0, 48.0 * K - 30.0
    right_ts = np.array([0.7071, 0.0, -0.7071]); up_ts = np.array([-0.3536, 0.8660, -0.3536])
    tgt = right_ts * ((128.0 - ox) / ppc) + up_ts * (-(128.0 - oy) / ppc)
    g.camera('camera-ts-angle', 315.0, 30.0, tgt, 256 / 2 / ppc, 256 / 2 / ppc,
             extras=dict(note='TS angle: orthographic, 30 degrees, looking north-west; render 256 x 256 px = ts-angle/ frames'))
    g.camera('camera-ra-grid', 0.0, 32.0, np.array([0.0, 0.0, 0.0]), 256 / 2 / 128.0, 256 / 2 / 128.0,
             extras=dict(note='RA grid: orthographic, 32 degrees, looking north; render 256 x 256 px = ra-grid/ frames'))
    os.makedirs(f'{PKG}/3d', exist_ok=True)
    g.save(f'{PKG}/3d/limpet-mine.glb', extras=dict(
        units='1 = one cell (128 px on the RA grid); x east, y up, z south; origin = the cell centre on the ground',
        foundation='1 x 1 cell', claws='north, east, south and west'))


if __name__ == '__main__':
    h = float(sys.argv[1]) if len(sys.argv) > 1 else 0.75
    export(h)
