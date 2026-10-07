"""3D model of the Upgrade Center as .glb (export3d.py), into PKG/3d/upgrade-center.glb:
  upgrade-center / upgrade-center-damaged   GTPLUG 0 / 1, with the dish at its GTPLUG_A frame 0
  plug-drop-pod-node, plug-seeker-control, plug-ion-cannon-uplink
                                            the three plugs, each standing in the east socket (move one 1.0 west to
                                            stand it in the west socket)
Markers: "socket-west", "socket-east" (the sockets' centres on their plates), "dish-pivot" (the dish turns about the
vertical through it), "slot-top" / "slot-bottom" (GTPLUG_C's running light runs down the ramp between them),
"lamp-low" / "lamp-high" (GTPLUG_B's two lamps on the tallest antenna).
Cameras: "camera-ts-angle" (384 x 384 = ts-angle/ frames), "camera-ra-grid" (384 x 448 = ra-grid/ frames; v3: TS's
way round, looking north).

    python3 plugexport.py [h]"""
import os, sys, time
import numpy as np
import hd, export3d as E, plug as M, plugs as PG, plugmat as MM, plugdamage as MD, plugrender as RR, plugfinal as PF

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-upgrade-center-hd')


def gl_point(x, y, z):
    return (x / E.CELL, z / E.CELL, y / E.CELL)


def plug_only(kind):
    comps = sorted(PG.PG_ALL)

    def f(X, Y, **kw):
        sc = M.scene(X, Y, plugs=(None, kind), **kw)
        keep = np.isin(sc.C, comps)
        sc.H = np.where(keep, sc.H, 0.0).astype(np.float32); sc.C = np.where(keep, sc.C, 0).astype(np.int16)
        sl = []
        for s in sc.slabs:
            k = (s.top >= 0) & np.isin(s.comp, comps)
            if k.any():
                s.top = np.where(k, s.top, -1.0)
                sl.append(s)
        sc.slabs = sl
        return sc
    return f


def export(h=1.25):
    g = E.GLB()
    p = M.P
    xr, yr = (-140.0, 140.0), (-135.0, 185.0)
    plain = lambda X, Y, **k: M.scene(X, Y, **k)
    dmg = MD.model(1)
    a0 = PF.dish_az(0)
    parts = [('upgrade-center', plain, None, 0, dict(dish_az=a0), xr, yr, 268.0),
             ('upgrade-center-damaged', dmg, MD, 1, dict(dish_az=a0), xr, yr, 268.0)]
    cx, cy = p['sockets']['c'][1]
    for kind, name in (('D', 'drop-pod-node'), ('E', 'seeker-control'), ('F', 'ion-cannon-uplink')):
        parts.append((f'plug-{name}', plug_only(kind), None, 0, {}, (cx - 52, cx + 52),
                      (cy - 52, cy + 52), 200.0))
    for name, fn, dm, level, kw, xr_, yr_, zm in parts:
        t0 = time.time()
        mk = dict(layout='ts'); mk.update(kw)
        v, f, n, rgb, house = E.build_part(fn, MM, xr_, yr_, h, zm, mk, damage=dm, level=level)
        g.mesh(name, v, f, n, rgb, house)
        print(name, len(v), 'verts', len(f), 'tris', '%.0fs' % (time.time() - t0), flush=True)
    sk = p['sockets']
    for (sx, sy), nm in zip(sk['c'], ('socket-west', 'socket-east')):
        g.marker(nm, gl_point(sx, sy, sk['plate']), 0.0,
                 extras=dict(note='a socket on its plate: the plugs stand here (TS draws them in the east one)'))
    mt = p['mount']
    g.marker('dish-pivot', gl_point(mt['c'][0], mt['c'][1], p['block']['z'] + mt['h'] + p['dish']['post'][1]), 0.0,
             extras=dict(note='GTPLUG_A: the dish turns once about the vertical through here in 20 frames'))
    e0, e1 = M.slot_ends(p)
    g.marker('slot-top', gl_point(*e0), 0.0, extras=dict(note="GTPLUG_C's running light runs down the slot from here"))
    g.marker('slot-bottom', gl_point(*e1), 0.0)
    ax, ay = p['ants'][0][:2]
    for lz, nm in zip(p['tall']['lamps'], ('lamp-low', 'lamp-high')):
        g.marker(nm, gl_point(ax, ay, lz), 0.0, extras=dict(note="GTPLUG_B: the tallest antenna's lamps blink"))
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
    Xw, Yw = Wr / 2 - oxr, (Hr / 2 - oyr) / s32                 # the world ground point under the canvas centre
    lay = RR.LAYOUT['ra']
    xl, yl = M.to_local(Xw, Yw, lay)
    turned = M.LAYOUTS[lay]['turn']
    g.camera('camera-ra-grid', 270.0 if turned else 0.0, 32.0, np.array(gl_point(xl, yl, 0.0)), Wr / 2 / 128.0,
             Hr / 2 / 128.0,
             extras=dict(note=(f'RA grid: orthographic, 32 degrees, looking at the model from its east (it stands turned a '
                               f'quarter on the RA grid: TS east to the camera); render {Wr} x {Hr} px = ra-grid/ frames')
                         if turned else
                         (f'RA grid: orthographic, 32 degrees, looking north (TS\'s way round: the sockets and plugs to '
                          f'the south); render {Wr} x {Hr} px = ra-grid/ frames')))
    os.makedirs(f'{PKG}/3d', exist_ok=True)
    g.save(f'{PKG}/3d/upgrade-center.glb', extras=dict(
        units='1 = one cell (128 px on the RA grid); x east, y up, z south; origin = the 2x3 foundation centre on the ground',
        foundation="TS's 2 x 3 cells (x -1..1, z -1.5..1.5), TS's way round; on the RA grid the same way round on a "
                   "2 x 3 plot (v3: the sockets and plugs to the south)"))


if __name__ == '__main__':
    export(float(sys.argv[1]) if len(sys.argv) > 1 else 1.25)
