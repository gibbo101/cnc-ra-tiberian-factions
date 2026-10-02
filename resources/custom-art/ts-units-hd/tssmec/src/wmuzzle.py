"""the Wolverine's two muzzles on the 384 canvas for each firing frame (96-127): the barrels' tips, where the flash is
drawn.

    python3 wmuzzle.py model.json out.txt
"""
import sys
import numpy as np
import wolf as WF, wolfhd as WH, wolfrender as WR


def muzzle_table(model):
    cam = WR.camera(model)
    rows = []
    for k in range(96, 128):
        f, s, _ = WR.frame_spec(k)
        M = WF.facing_matrix(WH.mod_to_cw(f))
        pts = [cam.project(M @ m) for m in WH.muzzles(model, model['stand'])]
        rows.append((k, f, s, pts))
    return rows


if __name__ == '__main__':
    model = WH.load(sys.argv[1])
    rows = muzzle_table(model)
    with open(sys.argv[2], 'w') as fh:
        fh.write('Wolverine (TSSMEC): the two guns\' muzzles on the 384 canvas for each firing frame (96-127), in canvas\n'
                 'px: the tips of the barrels, where the flash is drawn (steps 0 and 2).  Left and right are the unit\'s\n'
                 'own.  The canvas centre (192, 192) is the unit\'s position.\n\n')
        fh.write('frame  facing  step   left x   left y   right x  right y\n')
        for k, f, s, ((lx, ly), (rx, ry)) in rows:
            fh.write('%5d  %6d  %4d   %6.1f   %6.1f   %6.1f   %6.1f\n' % (k, f, s, lx, ly, rx, ry))
    print('written', sys.argv[2])
