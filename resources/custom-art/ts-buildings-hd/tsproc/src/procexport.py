"""3D models of the Tiberium Refinery and the TS Harvester as .glb (export3d.py), into PKG/3d/:

  refinery.glb    the refinery healthy ("refinery") and damaged ("refinery-damaged"), each with its bib ("bib",
                  "bib-damaged"), and marker nodes: "dock" (where TS's harvester parks, facing east: put the
                  harvester model's origin here), "fire" (the flare stack's mouth), "lamp-north" / "lamp-south"
  harvester.glb   HARV ("harvester"), HORV ("harvester-unloading"), and the tank alone ("tank": the lid, HARV =
                  HORV + tank), all facing east (+x) with the unit's position at the origin, at TS's own size

    python3 procexport.py [h]      h = sampling step in units (default 1.5 for the refinery; the harvester 0.4)"""
import os, sys, time, json
import numpy as np
import export3d as E, proc as PR, procmat as PM, procdamage as PD, harv as HV, harvmat as HM

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-tiberium-refinery-hd')


def gl_point(x, y, z):
    """model point (units: x east, y south, z up) -> glTF (cells: x east, y up, z south)."""
    return (x / E.CELL, z / E.CELL, y / E.CELL)


def refinery(h=1.5):
    g = E.GLB()
    p = PR.P
    xr, yr, zmax = (-262.0, 262.0), (-200.0, 200.0), 262.0
    for name, fn, dmg, level, pad in (('refinery', PR.scene, None, 0, False), ('bib', PR.scene, None, 0, True),
                                      ('refinery-damaged', PD.model(1), PD, 1, False),
                                      ('bib-damaged', PD.model(1), PD, 1, True)):
        t0 = time.time()
        mk = dict(layout='ts')
        if pad:
            mk['pad'] = True
        v, f, n, rgb, house = E.build_part(fn, PM, xr, yr, h if not pad else 2.0, zmax if not pad else 8.0, mk,
                                           damage=dmg, level=level, mat_kw=dict(lights=0))
        g.mesh(name, v, f, n, rgb, house)
        print(name, len(v), 'verts', len(f), 'tris', '%.0fs' % (time.time() - t0), flush=True)
    dk = PR.DOCK['ts']
    g.marker('dock', gl_point(dk['pos'][0], dk['pos'][1], 0.0), 0.0,
             extras=dict(note="TS's harvester parks here facing east (+x): the harvester model's origin goes here",
                         harvester_scale='harvester.glb is at the same scale (TS size): no scaling needed'))
    st = p['stack']
    g.marker('fire', gl_point(st['c'][0], st['c'][1], st['top']), 0.0, extras=dict(note='the flare stack mouth (NTREFN_B)'))
    lm = p['lamps']
    for nm, a in zip(('lamp-south', 'lamp-north'), lm['az']):
        lx = p['c'][0] + p['deck_r'] * np.cos(np.radians(a)); ly = p['c'][1] + p['deck_r'] * np.sin(np.radians(a))
        g.marker(nm, gl_point(lx, ly, lm['z']), 0.0, extras=dict(note='a dock lamp (NTREFN_C)'))
    # the cameras of the delivered frames, framing the 736x928 canvas exactly (set the render to 736 x 928 px)
    up_ra = np.array([0.0, np.cos(np.radians(32)), -np.sin(np.radians(32))])
    g.camera('camera-ra-grid', 0.0, 32.0, up_ra * (90.257 / 128.0), 736 / 2 / 128.0, 928 / 2 / 128.0,
             extras=dict(note='RA grid: orthographic, 32 degrees, looking north; render 736 x 928 px = ra-grid/ frames'))
    ppc = 4.1 * 0.265165 * 128.0                     # TS-angle px per cell (TS's frame x4.1)
    right_ts = np.array([0.7071, 0.0, -0.7071]); up_ts = np.array([-0.3536, 0.8660, -0.3536])
    g.camera('camera-ts-angle', 315.0, 30.0, right_ts * (-5.4 / ppc) + up_ts * (7.9 / ppc), 736 / 2 / ppc, 928 / 2 / ppc,
             extras=dict(note='TS angle: orthographic, 30 degrees, looking north-west; render 736 x 928 px = ts-angle/ frames'))
    g.save(f'{PKG}/3d/refinery.glb', extras=dict(
        units='1 = one cell (128 px on the RA grid); x east, y up, z south; origin = the 4x3 foundation centre on the ground',
        foundation='4 x 3 cells: x -2..2, z -1.5..1.5'))


def harvester(h=1.0):
    g = E.GLB()
    s = HV.S
    xr, yr, zmax = (-30.0 * s, 26.0 * s), (-11.0 * s, 11.0 * s), 20.5 * s
    for name, mk in (('harvester', dict(frame=24, s=s)), ('harvester-unloading', dict(frame=24, s=s, unloading=True))):
        t0 = time.time()
        fn = lambda X, Y, **k: HV.merge_slabs(HV.scene(X, Y, **k))
        v, f, n, rgb, house = E.build_part(fn, HM, xr, yr, h, zmax, mk, smooth=0.5)
        g.mesh(name, v, f, n, rgb, house)
        print(name, len(v), 'verts', len(f), 'tris', '%.0fs' % (time.time() - t0), flush=True)
    # the tank alone (the lid): solid from the bed's top up, in place on the truck
    t0 = time.time()

    def tank_fn(X, Y, **k):
        sc = HV.scene(X, Y, frame=24, s=s, only='tank', tank_off=0.0)
        return sc
    v, f, n, rgb, house = E.build_part(tank_fn, HM, xr, yr, h, zmax, dict(frame=24, s=s), smooth=0.5)
    g.mesh('tank', v, f, n, rgb, house)
    print('tank', len(v), 'verts', len(f), 'tris', '%.0fs' % (time.time() - t0), flush=True)
    up_ra = np.array([0.0, np.cos(np.radians(32)), -np.sin(np.radians(32))])
    g.camera('camera-unit', 0.0, 32.0, np.array([4.0 / 128, 0, 0]) + up_ra * (22.5 / 128.0), 1.5, 1.5,
             extras=dict(note='the unit frames: RA camera, 384 x 384 px, the unit position at (188, 214.5); turn the model '
                              '(f - 24) x 11.25 degrees about y for mod frame f'))
    g.save(f'{PKG}/3d/harvester.glb', extras=dict(
        units='1 = one cell (128 px on the RA grid); x east, y up, z south; origin = the unit position on the ground',
        facing='modelled facing east (+x), the mod frame 24; mod frame f = this turned (f - 24) x 11.25 degrees '
               'counter-clockwise seen from above (frame 0 north, 8 west, 16 south)',
        scale="TS's own size: 3.46 units per voxel (the TS voxel model is 49 x 20 x 19 voxels)"))


if __name__ == '__main__':
    os.makedirs(f'{PKG}/3d', exist_ok=True)
    what = sys.argv[1] if len(sys.argv) > 1 else 'all'
    h = float(sys.argv[2]) if len(sys.argv) > 2 else None
    if what in ('all', 'harvester'):
        harvester(h or 1.0)
    if what in ('all', 'refinery'):
        refinery(h or 1.5)
