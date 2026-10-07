"""3D model of the Dropship Bay (GTDROP) as .glb (export3d.py), into PKG/3d/dropship-bay.glb:

  dropship-bay          the building, healthy, its dish at GTDROP_A's frame 00
  dropship-bay-damaged  the same, damaged (GTDROP 1)
Markers: "pad-centre" (the landing pad's centre square: the dropship sets down here), "ramp-foot" (the ramp's
middle at the ground: vehicles drive off here, south), "dish-pivot" (GTDROP_A: the dish turns about the vertical through
here in 20 frames), "light-west" / "light-north" / "light-east" / "light-south" (GTDROP_B's four strips on the pad's
rim), "guard" (the jet blast guard's middle).
Cameras: "camera-ts-angle" (768 x 512 = ts-angle/ frames), "camera-ra-grid" (768 x 512 = ra-grid/ frames).
The model is in its own frame (TS's way round, as on the RA grid: the ramp to the south).

    python3 gdropexport.py [h]   h = sampling step in units (default 1.25)"""
import os, sys, time
import numpy as np
import export3d as E, gdrop as M, gdropmat as MM, gdropdamage as MD, gdroprender as RR, gdropfinal as GF, plug as PL

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-dropship-bay-hd')


def gl_point(x, y, z):
    return (x / E.CELL, z / E.CELL, y / E.CELL)


def export(h=1.25):
    g = E.GLB()
    p = M.P
    xr, yr, zm = (-232.0, 232.0), (-218.0, 236.0), 236.0
    plain = lambda X, Y, **k: M.scene(X, Y, **k)
    dmg = MD.model(1)
    a0 = GF.dish_az(0)
    for name, fn, dm, level in (('dropship-bay', plain, None, 0), ('dropship-bay-damaged', dmg, MD, 1)):
        t0 = time.time()
        mk = dict(layout='ts', dish_az=a0, dmg_level=level)
        v, f, n, rgb, house = E.build_part(fn, MM, xr, yr, h, zm, mk, damage=dm, level=level)
        g.mesh(name, v, f, n, rgb, house)
        print(name, len(v), 'verts', len(f), 'tris', '%.0fs' % (time.time() - t0), flush=True)
    zt = p['plug']['deck']['zt']
    pd = p['pad']
    zp = zt + pd['h']
    g.marker('pad-centre', gl_point(pd['c'][0], pd['c'][1], zp), 0.0,
             extras=dict(note='the landing pad\'s middle (the centre square): the dropship sets down here'))
    r = p['ramp']
    g.marker('ramp-foot', gl_point(0.5 * (r['x'][0] + r['x'][1]), r['y'][1], 0.0), 0.0,
             extras=dict(note='the ramp\'s middle at the ground: vehicles drive off the deck here, to the south'))
    mt = PL.P['mount']
    g.marker('dish-pivot', gl_point(mt['c'][0] + M.OFF[0], mt['c'][1] + M.OFF[1],
                                    PL.P['block']['z'] + mt['h'] + PL.P['dish']['post'][1]), 0.0,
             extras=dict(note='GTDROP_A: the dish turns once about the vertical through here in 20 frames'))
    hx, hy = pd['half']
    cx, cy = pd['c']
    for nm, (u, v) in (('light-west', (-hx + 5.0, 0.0)), ('light-north', (0.0, -hy + 2.5)), ('light-east', (hx - 5.0, 0.0)),
                       ('light-south', (0.0, hy - 2.5))):
        g.marker(nm, gl_point(cx + u, cy + v, zp), 0.0,
                 extras=dict(note='GTDROP_B: one of the four light strips on the pad\'s rim (white, then house colour, fading)'))
    gd = p['guard']
    g.marker('guard', gl_point(0.5 * (gd['x_top'] + gd['x_lip']), 0.5 * (gd['y'][0] + gd['y'][1]), gd['z_foot']), 0.0,
             extras=dict(note='the jet blast guard\'s middle (its wall faces the pad, east)'))
    # cameras framing the delivered canvases exactly
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
    g.camera('camera-ra-grid', 0.0, 32.0, np.array(gl_point(Xw, Yw, 0.0)), Wr / 2 / 128.0, Hr / 2 / 128.0,
             extras=dict(note=f'RA grid: orthographic, 32 degrees, looking north; render {Wr} x {Hr} px = ra-grid/ frames'))
    os.makedirs(f'{PKG}/3d', exist_ok=True)
    g.save(f'{PKG}/3d/dropship-bay.glb', extras=dict(
        units='1 = one cell (128 px on the RA grid); x east, y up, z south; origin = the 3x3 foundation centre on the ground',
        foundation="3 x 3 cells (x -1.5..1.5, z -1.5..1.5): TS's GTDROP, its ramp to the south; the same way round on the "
                   "RA grid"))


if __name__ == '__main__':
    export(float(sys.argv[1]) if len(sys.argv) > 1 else 1.25)
