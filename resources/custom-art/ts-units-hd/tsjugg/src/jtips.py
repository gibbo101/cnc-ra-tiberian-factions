"""the barrel tips on the canvas for every deployed frame (120-183): where each of the three barrels' muzzles ends (the
centre of its last voxel layer), and their mean, as the model puts them (jdeprender's camera and poses).

    python3 jtips.py out.txt
"""
import sys
import numpy as np
import jdeprender as DR


def tips(m):
    sec = m['sec']
    col = sec.col
    X = col.shape[0]
    out = []
    for jc in ((0, 6), (9, 15), (18, 24)):
        # the muzzle's end face: the barrel's last voxel layer along x, its filled voxels' centre
        for i in range(X - 1, -1, -1):
            sl = col[i, jc[0]:jc[1], :]
            if (sl >= 0).any():
                jj, kk = np.nonzero(sl >= 0)
                idx = np.array([i + 1.0, jc[0] + jj.mean() + 0.5, kk.mean() + 0.5])
                out.append(sec.mn + idx * sec.scale)
                break
    return np.array(out)                     # section coordinates


def table(m):
    cam = DR.camera(m)
    T = tips(m)
    rows = []
    for k in range(120, 184):
        f = (k - 120) % 32
        R, t = DR.barrel_pose(m, f, DR.REST_PITCH if k < 152 else DR.AIM_PITCH)
        W = T @ R.T + t
        sx, sy = cam.project(W)
        rows.append((k, sx, sy, sx.mean(), sy.mean()))
    return rows


if __name__ == '__main__':
    m = DR.load()
    rows = table(m)
    with open(sys.argv[1], 'w') as fh:
        fh.write('# the Juggernaut\'s barrel tips on the 448 x 448 canvas (px from the top left), as the model puts them\n'
                 '# frame  right barrel x y   middle x y   left barrel x y   mean x y   (right/left as the barrels face)\n')
        for k, sx, sy, mx, my in rows:
            fh.write('%4d   %6.1f %6.1f   %6.1f %6.1f   %6.1f %6.1f   %6.1f %6.1f\n'
                     % (k, sx[0], sy[0], sx[1], sy[1], sx[2], sy[2], mx, my))
    print(open(sys.argv[1]).read()[:600])
