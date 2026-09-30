"""
Tower-to-gate connectors for the component tower.

A tower at the end of a gate joins it with its half of a tower-to-tower link (ct_link.py): the khaki
sleeve runs out of the tower, over the sill and the steel beam, past the cell edge the two share and on
into the gate's end cell as far as the wall end pieces reach (EXT), where it ends in the steel flange
against the gate's end posts. Rendered with the tower alone in the scene, so the piece carries its own
outline and shadow.

    gatelink-<side>-<state>.png   side = where the gate is (N, E, S, W), state = the tower's frame (00, 01)

Drawn by the tower after its frame, in place of the coupling on that side. The part inside the gate's
cell is drawn by the gate too (scripts/ts_pack_gates.py), since a gate drawn after the tower covers it.

    python3 ct_gatelink.py 00 01
"""
import numpy as np
from PIL import Image
from scipy import ndimage
import ct_ra as R
import ct_link as L
from ct_link import AXES, CW0, CH0, LINK, FL_HALF

EXT = 27.0   # screen px the sleeve reaches past the shared cell edge into the gate's end cell

# which tower of the pair stands here: the first (west / north) has the gate east / south of it
SIDES = {('EW', False): 'E', ('EW', True): 'W', ('NS', False): 'S', ('NS', True): 'N'}


def tower_alone(level, axis, second):
    """one tower's physical scene on the joint grid, where the first or the second tower of a pair stands."""
    ex, ey = AXES[axis]['off']
    n0, n1 = R.GX.shape
    H = np.zeros((n0 + ey * L.SS, n1 + ex * L.SS)); C = np.zeros(H.shape, np.int8)
    top = np.full(H.shape, -1.0); comp = np.zeros(H.shape, np.int8)
    dmg = L.D.make(level, seed=10 + level) if level else None
    h, c, slab, p, _ = R.tower_scene(damage=dmg, physical=True)
    oy, ox = (ey * L.SS, ex * L.SS) if second else (0, 0)
    s = np.s_[oy:oy + n0, ox:ox + n1]
    H[s] = h; C[s] = c
    top[s] = slab['top']; comp[s] = slab['comp']
    return H, C, dict(top=top, lo=slab['lo'], comp=comp), p


def frame_alpha(axis, level, second, root='ctwr/out'):
    ex, ey = AXES[axis]['off']
    a = np.zeros((CH0 + ey, CW0 + ex))
    oy, ox = (ey, ex) if second else (0, 0)
    a[oy:oy + CH0, ox:ox + CW0] = np.array(Image.open(f'{root}/component-tower-{level:02d}.png'))[..., 3] / 255.0
    return a


def render_half(axis, level, second):
    """the tower's half of a link, capped by the flange on the shared edge, on the two-cell canvas."""
    Ht, Ct, slab, p = tower_alone(level, axis, second)
    saved = R.GX, R.GY, R.CW, R.CH, L.geo
    ex, ey = AXES[axis]['off']
    plain_geo = L.geo

    def reaching_geo(axis_, x, y):
        """distance along the axis from this tower's own centre (the second tower's mirrored, so both
        read like the first), with the shared edge moved EXT into the gate's cell so the tower's half
        runs on to it."""
        a, edge, av, k = plain_geo(axis_, x, y)
        if second:
            a = 2 * edge - a
        return a, edge + EXT / k, av, k
    L.geo = reaching_geo
    try:
        R.GX, R.GY = L.joint_grid(axis)
        R.CW, R.CH = CW0 + ex, CH0 + ey
        hl, cl = L.link_geom(axis, R.GX, R.GY)
        hl, lmats = L.link_damage(axis, level if not second else 0, level if second else 0, hl, cl, R.GX, R.GY)
        a, edge, av, k = L.geo(axis, R.GX, R.GY)
        keep = a <= edge + FL_HALF / k
        hl = np.where(keep, hl, 0.0)
        cl = np.where(keep & (hl > 0), cl, 0).astype(np.int8)
        win = hl > Ht
        Hp = np.where(win, hl, Ht); Cp = np.where(win, cl, Ct).astype(np.int8)
        H, sl, C = R.to_screen(Hp, slab, Cp)
        sc = R.shade_scene(H, C, sl, p, dict(mats=lmats))
        hit, comp = sc['hit'], sc['comp']
        mine = hit & np.isin(comp, LINK)
        env_c = np.where(np.isin(C, LINK), H, 0.0)
        sh_obj = R.in_shadow(env_c, sc['x'], sc['y'], sc['z']) & hit & ~mine
        ga = R.ground_alpha(env_c)
        ring = ndimage.binary_dilation(mine, iterations=int(0.9 * L.SS)) & ~hit
        ga = np.where(ring, np.maximum(ga, 0.55), ga)
        af = np.repeat(np.repeat(frame_alpha(axis, level, second), L.SS, axis=0), L.SS, axis=1)
        ga = np.where(af < 0.999, np.clip((ga - af) / np.maximum(1 - af, 1e-3), 0, 1), 0.0)
        whole = np.zeros(hit.shape + (4,))
        whole[..., :3] = np.where(mine[..., None], sc['col'], 0.0)
        whole[..., 3] = np.where(mine, 1.0, np.where(hit, 0.45 * ndimage.gaussian_filter(sh_obj.astype(float), 0.8 * L.SS), ga))
        return R.downsample(whole)
    finally:
        R.GX, R.GY, R.CW, R.CH, L.geo = saved


def save_half(axis, level, second, out='ctwr/out'):
    img = L.cut(render_half(axis, level, second), axis, second)
    img.save(f'{out}/gatelink-{SIDES[(axis, second)]}-{level:02d}.png')


if __name__ == '__main__':
    import sys
    for lv in sys.argv[1:] or ['00', '01']:
        for axis in ('EW', 'NS'):
            for second in (False, True):
                save_half(axis, int(lv), second)
                print('gatelink', SIDES[(axis, second)], lv, flush=True)
