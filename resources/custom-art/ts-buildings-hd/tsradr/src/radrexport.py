"""3D model of the Radar as .glb (export3d.py), into PKG/3d/radar.glb:

  radar / radar-damaged          the building without its antennas and dish (GTRADR 0 / 1)
  antennas / antennas-damaged    the seven antennas (GTRADR_A draws them)
  dish / dish-damaged            the dish with its boom, struts, feed horn and rod, at GTRADR_A frame 0; it turns about
                                 the vertical axis through "dish-pivot"
Markers: "dish-pivot" (the turret's axis at its top), "dish-centre" (the rim's centre at frame 0).
Cameras: "camera-ts-angle" (256 x 512 = ts-angle/ frames), "camera-ra-grid" (256 x 592 = ra-grid/ frames).
The model is in its own frame, TS's way round (as the RA grid version).

    python3 radrexport.py [h]      h = sampling step in units (default 1.4)"""
import os, sys, time
import numpy as np
import export3d as E, radr as M, radrmat as MM, radrdamage as MD, radrrender as RR

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-radar-hd')


def gl_point(x, y, z):
    return (x / E.CELL, z / E.CELL, y / E.CELL)


def export(h=1.4):
    g = E.GLB()
    p = M.P
    xr, yr = (-136.0, 136.0), (-136.0, 136.0)
    plain = lambda X, Y, **k: M.scene(X, Y, **k)
    dmg = MD.model(1)
    az0 = p['dish']['az'][0]
    base = list(M.BASE_PARTS)
    parts = (('radar', plain, None, 0, dict(parts=base), 200.0, h),
             ('radar-damaged', dmg, MD, 1, dict(parts=base), 200.0, h),
             ('antennas', plain, None, 0, dict(parts=['masts']), 370.0, min(h, 1.1)),
             ('antennas-damaged', dmg, MD, 1, dict(parts=['masts']), 370.0, min(h, 1.1)),
             ('dish', plain, None, 0, dict(parts=['dish'], dish_az=az0), 340.0, min(h, 1.1)),
             ('dish-damaged', dmg, MD, 1, dict(parts=['dish'], dish_az=az0), 340.0, min(h, 1.1)))
    for name, fn, dm, level, kw, zm, hh in parts:
        t0 = time.time()
        mk = dict(layout='ts'); mk.update(kw)
        v, f, n, rgb, house = E.build_part(fn, MM, xr, yr, hh, zm, mk, damage=dm, level=level)
        g.mesh(name, v, f, n, rgb, house)
        print(name, len(v), 'verts', len(f), 'tris', '%.0fs' % (time.time() - t0), flush=True)
    tu, d = p['turret'], p['dish']
    df = M.dish_frame(p, az0)
    g.marker('dish-pivot', gl_point(tu['c'][0], tu['c'][1], tu['z'][1]), 0.0,
             extras=dict(note='the dish turns about the vertical axis through here (the turret)'))
    g.marker('dish-centre', gl_point(*df['C']), 0.0, extras=dict(note="the dish rim's centre at GTRADR_A frame 0"))
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
    up_ra = np.array([0.0, np.cos(np.radians(32)), -np.sin(np.radians(32))])
    g.camera('camera-ra-grid', 0.0, 32.0, up_ra * ((oyr - Hr / 2) / 128.0), Wr / 2 / 128.0, Hr / 2 / 128.0,
             extras=dict(note=f'RA grid: orthographic, 32 degrees, looking north; render {Wr} x {Hr} px = ra-grid/ frames'))
    os.makedirs(f'{PKG}/3d', exist_ok=True)
    g.save(f'{PKG}/3d/radar.glb', extras=dict(
        units='1 = one cell (128 px on the RA grid); x east, y up, z south; origin = the 2x2 foundation centre on the ground',
        foundation='2 x 2 cells (x -1..1, z -1..1), TS\'s way round (the RA grid version is not turned)',
        dish=(f"GTRADR_A frames 0-14 turn the dish about the dish-pivot's vertical axis from {d['az'][0]:.1f} to "
              f"{d['az'][1]:.1f} degrees (its facing, measured from east towards south, seen from above; frame 0 is "
              f"the mesh as saved), then back (the loop plays 0..14..1). The dish is tilted {d['elev']:.0f} degrees up. "
              f"The RA grid renders turn it 45 degrees further (camera-relative, so it reads as TS's)")))


if __name__ == '__main__':
    h = float(sys.argv[1]) if len(sys.argv) > 1 else 1.4
    export(h)
