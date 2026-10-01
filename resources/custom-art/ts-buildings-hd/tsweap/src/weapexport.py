"""3D model of the War Factory as .glb (export3d.py), into PKG/3d/war-factory.glb:

  war-factory          the building, healthy, without its door (so the bay shows: put "door" in, or leave it out)
  war-factory-damaged  the same, damaged
  door                 the roll-up door alone, shut (it rolls up its track: straight up 40, then round a quarter
                       circle of radius 49 back into the roof; see the README). Both states: TS's damage leaves it
  bib / bib-damaged    the apron (GTWEAPBB)
Markers: "exit" (the door's middle at the floor, facing out of the door), "bay-inside" (in the bay behind the door),
"jamb-left" / "jamb-right" (the door's sides at the floor, seen from outside: left = TS's south fender), the lamps
"lamp-a1".."lamp-a5" (GTWEAP_A, north to south), "lamp-b1".."lamp-b3" (GTWEAP_B, west to east), "fan-1", "fan-2".
Cameras: "camera-ts-angle" (896 x 672 = ts-angle/ frames), "camera-ra-grid" (416 x 512 = ra-grid/ frames: RA's camera
looks at the door, i.e. west in the model's own frame).
The model is in its own frame (TS's way round: the door faces east, +x).  The RA grid version is it turned a quarter
clockwise seen from above (the door to the south).

    python3 weapexport.py [h]      h = sampling step in units (default 1.5)"""
import os, sys, time
import numpy as np
import export3d as E, weap as M, weapmat as MM, weapdamage as MD

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-war-factory-hd')


def gl_point(x, y, z):
    """model point (units: x east, y south, z up) -> glTF (cells: x east, y up, z south)."""
    return (x / E.CELL, z / E.CELL, y / E.CELL)


def door_only(fn):
    """the door's slab alone from a scene function."""
    def f(X, Y, **k):
        k = dict(k); k['merge'] = False; k['door'] = 0.0
        sc = fn(X, Y, **k)
        sc.H = np.zeros_like(sc.H); sc.C = np.zeros_like(sc.C)
        sc.slabs = [s for s in sc.slabs if s.name == 'door']
        return sc
    return f


def no_door(fn):
    def f(X, Y, **k):
        k = dict(k); k['door'] = None
        return fn(X, Y, **k)
    return f


def export(h=1.5):
    g = E.GLB()
    p = M.P
    xr, yr, zmax = (-262.0, 262.0), (-200.0, 206.0), 136.0
    plain = lambda X, Y, **k: M.scene(X, Y, **k)
    dmg = MD.model(1)
    parts = (('war-factory', no_door(plain), None, 0, False, zmax), ('war-factory-damaged', no_door(dmg), MD, 1, False, zmax),
             ('door', door_only(plain), None, 0, False, 100.0),
             ('bib', plain, None, 0, True, 8.0), ('bib-damaged', dmg, MD, 1, True, 8.0))
    for name, fn, dm, level, pad, zm in parts:
        t0 = time.time()
        mk = dict(layout='ts')
        if pad:
            mk['pad'] = True
        v, f, n, rgb, house = E.build_part(fn, MM, xr, yr, h if not pad else 2.0, zm, mk, damage=dm, level=level)
        g.mesh(name, v, f, n, rgb, house)
        print(name, len(v), 'verts', len(f), 'tris', '%.0fs' % (time.time() - t0), flush=True)
    d, b = p['door'], p['bay']
    yc = (b['y'][0] + b['y'][1]) / 2
    g.marker('exit', gl_point(d['x0'], yc, 0.0), 0.0,
             extras=dict(note='the middle of the door at the floor; vehicles roll out this way (+x, east; south on the RA grid)'))
    g.marker('bay-inside', gl_point(-110.0, yc, 0.0), 0.0, extras=dict(note='in the bay behind the door, on its centre line'))
    g.marker('jamb-left', gl_point(d['x0'], b['y'][1], 0.0), 0.0,
             extras=dict(note="the door's left side seen from outside (TS's south fender; the west one on the RA grid)"))
    g.marker('jamb-right', gl_point(d['x0'], b['y'][0], 0.0), 0.0,
             extras=dict(note="the door's right side seen from outside (TS's north fender; the east one on the RA grid)"))
    la = p['lampsA']
    for k in range(5):
        g.marker(f'lamp-a{k + 1}', gl_point(la['x'], la['y0'] + k * la['dy'], la['z']), 0.0,
                 extras=dict(note='GTWEAP_A, the five white lamps on the beam over the door (north to south)'))
    lb = p['lampsB']
    for k, ((bx, by), bz) in enumerate(zip(lb['pts'], lb['zs'])):
        g.marker(f'lamp-b{k + 1}', gl_point(bx, by, bz + lb['r']), 0.0, extras=dict(note='GTWEAP_B, the three orange lamps'))
    fa = p['fans']
    for k, (fx, fy) in enumerate(fa['pts']):
        g.marker(f'fan-{k + 1}', gl_point(fx, fy, fa['z']), 0.0, extras=dict(note='GTWEAP_C, a roof fan (turns about +y)'))
    # cameras framing the delivered canvases exactly
    ppc = 4.125 * 0.265165 * 128.0                    # TS-angle px per cell (TS's frame x4.125)
    ox, oy = 108.0 * 4.125 + 50.0, 126.0 * 4.125 - 190.0       # the model's origin on the 896x672 canvas
    right_ts = np.array([0.7071, 0.0, -0.7071]); up_ts = np.array([-0.3536, 0.8660, -0.3536])
    tgt = right_ts * ((448.0 - ox) / ppc) + up_ts * (-(336.0 - oy) / ppc)
    g.camera('camera-ts-angle', 315.0, 30.0, tgt, 896 / 2 / ppc, 672 / 2 / ppc,
             extras=dict(note='TS angle: orthographic, 30 degrees, looking north-west; render 896 x 672 px = ts-angle/ frames'))
    up_ra = np.array([-np.sin(np.radians(32)), np.cos(np.radians(32)), 0.0])
    oy_ra = 512.0 - np.sin(np.radians(32.0)) * 256.0
    g.camera('camera-ra-grid', 270.0, 32.0, up_ra * ((oy_ra - 256.0) / 128.0), 416 / 2 / 128.0, 512 / 2 / 128.0,
             extras=dict(note="RA grid: orthographic, 32 degrees, looking at the door (west in the model's frame = north on "
                              "the RA grid with the building turned); render 416 x 512 px = ra-grid/ frames"))
    os.makedirs(f'{PKG}/3d', exist_ok=True)
    g.save(f'{PKG}/3d/war-factory.glb', extras=dict(
        units='1 = one cell (128 px on the RA grid); x east, y up, z south; origin = the 4x3 foundation centre on the ground',
        foundation="TS: 4 x 3 cells (x -2..2, z -1.5..1.5), the door facing east. RA grid: turned a quarter clockwise "
                   "(seen from above) so the door faces south: a 3 x 4 plot",
        door="rolls up its track: straight up 0.3125 (40 units), then round a quarter circle of radius 0.383 (49) "
             "centred 0.383 behind the door's face at height 0.3125, into the roof; GTWEAP_D frame k = rolled k/8 of "
             "the way, a strip left at the hinge"))


if __name__ == '__main__':
    h = float(sys.argv[1]) if len(sys.argv) > 1 else 1.5
    export(h)
