"""3D models of the Firestorm Wall Section (GAFSDF) as .glb (export3d.py), into PKG/3d/firestorm-wall.glb: one mesh per
kind of section (each in its own cell frame, side by side along x: 1.5 cells apart, so they can be told apart):
  section-alone (mask 0), section-end (1: a neighbour to the north), section-straight (5: north and south: all
  grating), section-corner (3: north and east), section-tee (7: north, east, south), section-cross (15)
Any other mask is one of these turned.  Cameras: "camera-ra-grid" (176 x 320, RA's wall view: oblique, the ground not
foreshortened; a glTF camera can't do that, so this one is orthographic straight down, the frames' ground) and
"camera-ts-angle" (176 x 320 = the ts-angle frames).

    python3 fsdfexport.py [h]   h = sampling step in units (default 0.75)"""
import os, sys, time
import numpy as np
import export3d as E, fsdf as M, fsdfmat as MM

PKG = os.environ.get('PKG', '/home/claude/work/out/ts-firestorm-wall-hd')
KINDS = (('section-alone', 0), ('section-end', 1), ('section-straight', 5), ('section-corner', 3), ('section-tee', 7),
         ('section-cross', 15))


def export(h=0.75):
    g = E.GLB()
    for k, (name, mask) in enumerate(KINDS):
        t0 = time.time()
        fn = lambda X, Y, mask=mask, **kw: M.scene(X, Y, mask=mask, **kw)
        v, f, n, rgb, house = E.build_part(fn, MM, (-66.0, 66.0), (-66.0, 66.0), h, 24.0, dict(layout='ra', mask=mask))
        v = v + np.array([1.5 * k, 0.0, 0.0], np.float32)
        g.mesh(name, v, f, n, rgb, house)
        print(name, len(v), 'verts', len(f), 'tris', '%.0fs' % (time.time() - t0), flush=True)
    K = 3.5
    ppc = K * 0.265165 * 128.0
    ox, oy = 24.0 * K + 4.0, 36.0 * K + 34.0
    right_ts = np.array([0.7071, 0.0, -0.7071]); up_ts = np.array([-0.3536, 0.8660, -0.3536])
    tgt = right_ts * ((88.0 - ox) / ppc) + up_ts * (-(160.0 - oy) / ppc)
    g.camera('camera-ts-angle', 315.0, 30.0, tgt, 176 / 2 / ppc, 320 / 2 / ppc,
             extras=dict(note='TS angle: orthographic, 30 degrees, looking north-west; 176 x 320 px = ts-angle/ frames (the first mesh)'))
    g.camera('camera-ra-grid', 0.0, 89.9, np.array([0.0, 0.0, 0.0]), 176 / 2 / 128.0, 320 / 2 / 128.0,
             extras=dict(note="RA grid frames use RA's oblique wall view (screen y = ground y - 0.6 x height): straight "
                              "down is its ground; 176 x 320 px, the cell's ground centre at (88, 160)"))
    os.makedirs(f'{PKG}/3d', exist_ok=True)
    g.save(f'{PKG}/3d/firestorm-wall.glb', extras=dict(
        units='1 = one cell (128 px on the RA grid); x east, y up, z south; each section on its own cell, 1.5 cells apart along x',
        masks='frame = N1 E2 S4 W8 (+16 damaged, +32 the field on); the meshes are masks 0, 1, 5, 3, 7, 15'))


if __name__ == '__main__':
    h = float(sys.argv[1]) if len(sys.argv) > 1 else 0.75
    export(h)
