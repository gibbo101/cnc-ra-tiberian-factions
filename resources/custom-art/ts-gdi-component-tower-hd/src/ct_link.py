"""
Tower-to-tower links for the component tower.

Two towers next to each other share one sleeve: each tower's wall sleeve runs out to the cell edge between
them and the two halves are bolted together there with a steel flange; a steel beam comes out of each tower
into it and a sill runs underneath from pad to pad, as on the couplings. East-west the towers' own sleeves
already sit on that edge, so the shared sleeve is just the coupling's sleeve closed at both ends; north-south
the cell is deeper than the tower (the camera foreshortens it), so the sleeves reach further to meet.

It is rendered as one scene per pair of states and direction (both towers exactly as their frames are
rendered, plus the whole link) on a two-cell canvas, and each tower gets the whole link cut to its own canvas:
    link-<side>-<own>-<neighbour>.png   side = where the other tower is (N, E, S, W)
Both towers draw it after their own frame and couplings, so whichever of the two RA draws last, the link lies
whole on top of the other's frame and shadow, and the two drawings are the same pixels where they overlap.
Only the later tower's piece (W, and N - the south tower always comes after the north one) carries the link's
outline and shadow, so those are drawn once; its ground shadow is cut back where the two towers' frames
already shade the ground, so the shadows combine like one shadow in either order.
"""
import numpy as np
from PIL import Image
from scipy import ndimage
import walls2 as W
from walls2 import smoothstep, phase, SS
from damage import Sampler
import ct_ra as R
import ct_damage as D

FL_HALF, FL_OUT = 2.4, 0.8     # the flange: half its length along the link (screen px), how proud it stands
LINK = [R.NECK, R.FLANGE, R.SILL]
CW0, CH0 = R.CW, R.CH          # a tower's own canvas
# per direction: where the second tower's cell is (screen px), and the sides the two towers draw it on
AXES = {'EW': dict(off=(128, 0), sides=('E', 'W')),
        'NS': dict(off=(0, 128), sides=('S', 'N'))}


def geo(axis, x, y):
    """along-axis physical distance a from the first tower's centre, the shared edge (physical), the
    distance across in screen px, and screen px per physical unit along the axis."""
    dx, dy = R.phys(x, y)
    if axis == 'EW':
        return dx, 64.0, np.abs(dy * R.SYF), 1.0
    return dy, 64.0 / R.SYF, np.abs(dx), R.SYF


def joint_grid(axis):
    ex, ey = AXES[axis]['off']
    xs = (np.arange(-(R.OX + R.MG) * SS, (CW0 + ex - R.OX + R.MG) * SS) + 0.5) / SS
    ys = (np.arange(-(R.OY + R.MG) * SS, (CH0 + ey - R.OY + R.FZ * R.ZMAX + R.MG) * SS) + 0.5) / SS
    return np.meshgrid(xs, ys)


def towers(la, lb, axis):
    """both towers' physical scenes, built exactly as their frames are (fresh damage, standard grid), next to
    each other on the joint grid: the first (west / north) at la, the second (east / south) at lb."""
    ex, ey = AXES[axis]['off']
    n0, n1 = R.GX.shape
    H = np.zeros((n0 + ey * SS, n1 + ex * SS)); C = np.zeros(H.shape, np.int8)
    top = np.full(H.shape, -1.0); comp = np.zeros(H.shape, np.int8)
    for lvl, (oy, ox) in ((la, (0, 0)), (lb, (ey * SS, ex * SS))):
        dmg = D.make(lvl, seed=10 + lvl) if lvl else None
        h, c, slab, p, _ = R.tower_scene(damage=dmg, physical=True)
        s = np.s_[oy:oy + n0, ox:ox + n1]
        win = h > H[s]
        H[s] = np.where(win, h, H[s]); C[s] = np.where(win, c, C[s])
        tw = slab['top'] > top[s]
        top[s] = np.where(tw, slab['top'], top[s]); comp[s] = np.where(tw, slab['comp'], comp[s])
        lo = slab['lo']
    return H, C, dict(top=top, lo=lo, comp=comp), p


def link_geom(axis, X, Y, c=R.CPL):
    """the link in physical heights on the joint grid. Along the link each point belongs to the nearer tower
    (u = its distance from that tower's centre), so every part matches that tower's own coupling: the sill
    runs from pad to pad, a steel beam comes out of each tower, and the sleeve (the couplings' cross-section)
    runs from one beam to the other, closed at both ends like a sleeve's inner end, with the flange proud of
    it on the edge."""
    a, edge, av, k = geo(axis, X, Y)
    u = np.where(a <= edge, a, 2 * edge - a)
    uc, s_in = c['sl_c'], c['sl_in']
    sill = (u >= c['sill_from']) & (av <= c['sill_w'])
    hs = np.where(sill, c['sill_h'] - np.clip(av - (c['sill_w'] - 1.5), 0, None), 0.0)
    neck = (u >= c['neck_from']) & (u <= uc - s_in + 0.5) & (av <= c['neck_w'])
    hn = np.where(neck, c['neck_h'] - np.clip(av - (c['neck_w'] - c['neck_cham']), 0, None), 0.0)

    def sleeve(grow):
        h, ch = c['sl_h'] + grow, c['sl_cham']
        base, tw = c['sl_base'] + grow, c['sl_top'] + grow
        wi = u - (uc - s_in)                     # out from the inner end on this tower's side
        on = (wi >= 0) & (av <= base)
        hv = h * np.clip((base - av) / (base - tw), 0, 1)
        hv = np.minimum(hv, (h - ch) + (tw + ch - av))
        hi = h - np.clip(1.5 - wi, 0, None)
        return np.where(on, np.clip(np.minimum(hv, hi), 0, None), 0.0)
    hf = sleeve(0.0)
    hf = np.where(np.abs(a - edge) * k <= FL_HALF, np.maximum(hf, sleeve(FL_OUT)), hf)
    H = np.maximum.reduce([hs, hn, hf])
    C = np.where(hf >= np.maximum(hn, hs), R.FLANGE, np.where(hn >= hs, R.NECK, R.SILL))
    return H, np.where(H > 0, C, 0).astype(np.int8)


def first_half(axis, amp):
    """which points belong to the first tower's half: split on the shared edge (screen 128 in the first
    tower's cell), the split wandering a little across the link when the two halves differ."""
    n = ndimage.gaussian_filter1d(np.random.default_rng(90).standard_normal(700), 6.0)
    n = n / n.std() * amp
    wob = lambda t: np.interp(t, np.arange(-150, 550), n)
    if axis == 'EW':
        return lambda x, y: x < 128.0 + wob(y)
    return lambda x, y: y < 128.0 + wob(x)


def link_damage(axis, la, lb, H, C, X, Y):
    """each half worn and broken like its own tower's couplings (greys and browns): the first tower's half at
    la, the second's at lb. The patterns hang on the half and its level only, so a half keeps its look
    whatever state the other tower is in. Returns the damaged heights and a colour function."""
    first = first_half(axis, 2.2 if la != lb else 0.0)
    f = first(X, Y)
    link = np.isin(C, LINK)
    H = H.copy()
    broken = np.zeros_like(H)                    # how much of the sleeve is broken away, for the colours
    halves = []
    for level, is_first, seed in ((la, True, 400 + 10 * la), (lb, False, 500 + 10 * lb)):
        rng = np.random.default_rng(seed + (0 if axis == 'EW' else 1000))
        S = [Sampler(rng, s) for s in (8.0, 12.0, 1.2, 5.0, 4.0, 3.0)]
        halves.append((level, is_first, S))
        if not level:
            continue
        m = link & (f if is_first else ~f)
        jag = D.gn(H.shape, 1.8, rng)
        if level == 1:
            grad = np.hypot(*np.gradient(H, 1.0 / SS))
            band = ndimage.maximum_filter((grad > 2.0).astype(float), size=int(3.0 * SS)) * (H > 0.5)
            chip = smoothstep(1.0, 1.5, D.gn(H.shape, 2.2, rng)) * band
            H = np.where(m, np.maximum(H - 5.0 * chip, 0), H)
        else:
            low = m & np.isin(C, [R.NECK, R.SILL])
            H = np.where(low, np.maximum(H * 0.45 + 2.5 * jag, 0), H)
            # the sleeve broken to a stump in chunks (not crumpled): a little fine jag on mid-size lumps and
            # a wavy line, and here and there it has fallen right down to the sill
            lim = (10.0 + 1.6 * jag + 3.0 * D.gn(H.shape, 3.5, rng) + 5.0 * D.gn(H.shape, 7.0, rng))
            lim = np.where(D.gn(H.shape, 9.0, rng) < -1.0, 2.0 + 1.2 * jag, lim)
            sl = m & (C == R.FLANGE)
            before = H
            H = np.where(sl, np.clip(np.minimum(H, lim), 0, None), H)
            broken = np.maximum(broken, np.clip((before - H) / np.maximum(before, 1e-3), 0, 1) * (H > 0.5) * sl)

    def mats(alb, x, y, z, comp, top_like, grain, u, v):
        mine = np.isin(comp, LINK)
        out = np.where(mine[..., None], link_albedo(axis, x, y, comp, grain, top_like), alb)
        fx = first(x, y)
        for level, is_first, (S_crack, S_cmask, S_rough, S_soot, S_dust, S_torn) in halves:
            if not level:
                continue
            m = mine & (fx if is_first else ~fx)
            heavy = level == 2
            if heavy:                                # the flange torn: steel left only in patches
                a, edge, av, k = geo(axis, x, y)
                fl = (np.abs(a - edge) * k < FL_HALF + 0.8) & (S_torn(u, v) > -0.2) & m
                out = np.where(fl[..., None], R.KHAKI * 0.72 * (1 + 1.2 * grain)[..., None], out)
                # fresh breaks show paler, like the tower's own (ct_damage)
                i = np.clip(((x + R.OX + R.MG) * SS).astype(int), 0, broken.shape[1] - 1)
                j = np.clip(((y + R.OY + R.MG) * SS).astype(int), 0, broken.shape[0] - 1)
                rough = S_rough(u, v)
                bcol = D.FRESH * np.clip(0.84 + 0.1 * rough, 0.6, 1.0)[..., None]
                bcol = np.where((rough < -0.9)[..., None], np.array([90, 84, 72.]), bcol)
                b = (np.clip(broken[j, i] * 1.6, 0, 1) * m)[..., None]
                out = out * (1 - b) + bcol * b
            dust = smoothstep(0.6, 1.3, S_dust(u, v)) * 0.35 * m
            out = out * (1 - dust[..., None]) + D.DUST * (1 + grain)[..., None] * dust[..., None]
            soot = smoothstep(0.3 if heavy else 0.8, 1.3, S_soot(u, v)) * (0.75 if heavy else 0.5) * m
            out = out * (1 - soot[..., None]) + D.SOOT * soot[..., None]
            cn = S_crack(u, v) + 0.10 * S_rough(u, v)
            crack = (1 - smoothstep(0.015, 0.06, np.abs(cn))) * smoothstep(0.2, 0.6, S_cmask(u, v)) * m
            out *= (1 - 0.6 * crack)[..., None]
        return out
    return H, mats


def link_albedo(axis, x, y, comp, grain, top_like, c=R.CPL):
    """khaki sleeve (the tower's paint) with a steel flange on the edge and a dark joint line in it, bolts on
    top either side of it and a panel line where each tower's own sleeve would be; steel beams with joints;
    the pad's concrete for the sill."""
    a, edge, cv, k = geo(axis, x, y)
    u = np.where(a <= edge, a, 2 * edge - a)
    g = (1 + grain)[..., None]
    fl_c = R.KHAKI * (1 + 1.2 * grain)[..., None]
    band = (np.abs(u - c['sl_c']) < 0.6 / k) & (u < edge - (FL_HALF + 2) / k)
    fl_c = np.where(band[..., None], fl_c * 0.8, fl_c)                                  # panel line
    ds = np.abs(a - edge) * k                                                          # screen px from the edge
    fl_c = np.where((ds < FL_HALF + 0.3)[..., None], R.STEEL * g, fl_c)
    fl_c = np.where((np.abs(ds - FL_HALF - 0.3) < 0.45)[..., None], fl_c * 0.78, fl_c)  # its rims
    fl_c = np.where((ds < 0.45)[..., None], R.STEEL * 0.5 * g, fl_c)                    # the joint
    bolt = top_like & (np.hypot(cv - 9.0, ds - 2.6) < 1.3)
    fl_c = np.where(bolt[..., None], fl_c * 0.5, fl_c)
    joint = phase(u, 16.0, 8.0) < 0.6
    neck_c = R.BEAM_C * g * np.where(joint, 0.62, 1.0)[..., None]
    sill_c = R.PADC * g
    alb = np.zeros(x.shape + (3,))
    for k_, c_ in ((R.NECK, neck_c), (R.FLANGE, fl_c), (R.SILL, sill_c)):
        alb = np.where((comp == k_)[..., None], c_, alb)
    return alb


def frames_alpha(axis, la, lb, root='ctwr/out'):
    """the two towers' frames' alpha on the joint canvas (what they already shade on the ground)."""
    ex, ey = AXES[axis]['off']
    a = np.zeros((CH0 + ey, CW0 + ex)); b = np.zeros_like(a)
    a[:CH0, :CW0] = np.array(Image.open(f'{root}/component-tower-{la:02d}.png'))[..., 3] / 255.0
    b[ey:ey + CH0, ex:ex + CW0] = np.array(Image.open(f'{root}/component-tower-{lb:02d}.png'))[..., 3] / 255.0
    return 1 - (1 - a) * (1 - b)


def render_pair(axis, la, lb):
    """the link between the first tower (west / north) at la and the second (east / south) at lb, on the
    two-cell canvas (the first tower's canvas at 0, 0). Returns (whole: link + outline + shadows,
    solid: the link alone)."""
    Ht, Ct, slab, p = towers(la, lb, axis)
    ex, ey = AXES[axis]['off']
    saved = R.GX, R.GY, R.CW, R.CH
    try:
        R.GX, R.GY = joint_grid(axis)
        R.CW, R.CH = CW0 + ex, CH0 + ey
        hl, cl = link_geom(axis, R.GX, R.GY)
        hl, lmats = link_damage(axis, la, lb, hl, cl, R.GX, R.GY)
        win = hl > Ht
        Hp = np.where(win, hl, Ht); Cp = np.where(win, cl, Ct).astype(np.int8)
        H, sl, C = R.to_screen(Hp, slab, Cp)
        sc = R.shade_scene(H, C, sl, p, dict(mats=lmats))
        hit, comp = sc['hit'], sc['comp']
        mine = hit & np.isin(comp, LINK)
        env_c = np.where(np.isin(C, LINK), H, 0.0)
        sh_obj = R.in_shadow(env_c, sc['x'], sc['y'], sc['z']) & hit & ~mine
        ga = R.ground_alpha(env_c)
        ring = ndimage.binary_dilation(mine, iterations=int(0.9 * SS)) & ~hit
        ga = np.where(ring, np.maximum(ga, 0.55), ga)          # the outline, black so it multiplies too
        # where the towers' frames already shade the ground, only what the link adds: black over black
        # multiplies, so this comes out the same in either drawing order (like one shadow, not two)
        af = np.repeat(np.repeat(frames_alpha(axis, la, lb), SS, axis=0), SS, axis=1)
        ga = np.where(af < 0.999, np.clip((ga - af) / np.maximum(1 - af, 1e-3), 0, 1), 0.0)
        whole = np.zeros(hit.shape + (4,))
        whole[..., :3] = np.where(mine[..., None], sc['col'], 0.0)
        whole[..., 3] = np.where(mine, 1.0, np.where(hit, 0.45 * ndimage.gaussian_filter(sh_obj.astype(float), 0.8 * SS), ga))
        solid = np.zeros_like(whole)
        solid[..., :3] = np.where(mine[..., None], sc['col'], 0.0)
        solid[..., 3] = mine.astype(float)
        return R.downsample(whole), R.downsample(solid)
    finally:
        R.GX, R.GY, R.CW, R.CH = saved


def cut(pair_img, axis, second):
    """a tower's own canvas out of the two-cell canvas: the first tower's, or the second's."""
    ex, ey = AXES[axis]['off'] if second else (0, 0)
    return pair_img.crop((ex, ey, ex + CW0, ey + CH0))


def save_links(axis, la, lb, out='ctwr/out'):
    whole, solid = render_pair(axis, la, lb)
    s1, s2 = AXES[axis]['sides']
    whole.save(f'{out}/link-pair-{axis}-{la:02d}-{lb:02d}.png')
    cut(solid, axis, False).save(f'{out}/link-{s1}-{la:02d}-{lb:02d}.png')   # first tower: own la, other lb
    cut(whole, axis, True).save(f'{out}/link-{s2}-{lb:02d}-{la:02d}.png')    # second tower: own lb, other la


if __name__ == '__main__':
    # python3 ct_link.py EW 00 01 10 11 / NS 00 01 10 11   (first tower's frame, second tower's frame; RA
    # uses 00 healthy and 01 damaged, 02 destroyed renders too)
    import sys
    axis = sys.argv[1]
    for a in sys.argv[2:]:
        save_links(axis, int(a[0]), int(a[1]))
        print('link', axis, a, flush=True)
