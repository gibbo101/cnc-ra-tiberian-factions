"""
Render a turret in place on the component tower's 176x320 canvas (the tower itself left out): the same
orthographic camera as the tower (32 degrees above the ground, looking north), light, ~75% baked shadow,
materials, grain, outline and x4 supersampling. The tower is in the scene so that its ring hides the
turret's foot where it should and the turret's shadow falls on the tower (and ground) under it.

Screen: X = 88 + x, Y = 160 + y sin32 - z cos32 (physical units, the tower's ground centre at 88, 160).
"""
import os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(HERE, '..', 'ctwr'))
import walls2 as W
from walls2 import SS, sample, smoothstep, phase, NOISE_FINE, NOISE_MOTTLE, NOISE_GRIME
import ct_ra as R
import ct_damage as D
import tsdf as T

E = np.deg2rad(32.0)
SE, CE = np.sin(E), np.cos(E)
CW, CH = 176, 320
CAM = (E, 1.0, 88.0, 160.0, 0.0)
# shadows fall as the tower's do: SH_DIR screen px per screen-scaled unit of height -> a physical direction
_kx, _ky = R.SH_DIR
L_SH = np.array([-_kx * CE, -_ky * CE / SE, 1.0]); L_SH /= np.linalg.norm(L_SH)
LIGHT = W.LIGHT


class TowerScene:
    """what the tower frame shows at every supersample: hit, world point, normal, own shadow, and its
    frame's alpha (for the ground shadow bookkeeping)."""
    def __init__(self, level, root=None):
        dmg = D.make(level, seed=10 + level) if level else None
        H, C, slab, p, dm = R.tower_scene(damage=dmg)
        hit, z, gj, gi, kind = R.raycast(H, slab, np.zeros_like(H))
        nx, ny, nz = R.normals(H, slab, gj, gi, kind)
        x, y = R.GX[gj, gi], R.GY[gj, gi]
        env = np.maximum(H, np.where(slab['top'] > 0, slab['top'], 0))
        ssh = R.in_shadow(env, x, y, z)
        self.hit = hit
        self.P = np.stack([x - 64.0, (y - 64.0) / R.SYF, z / R.SZF], -1)          # physical
        self.n = np.stack([nx, ny, nz], -1)
        self.own_shadow = ssh & hit
        root = root or os.path.join(HERE, '..', 'ctwr', 'out')
        a = np.array(Image.open(f'{root}/component-tower-{level:02d}.png'))[..., 3] / 255.0
        self.frame_alpha = np.repeat(np.repeat(a, SS, 0), SS, 1)
        # ground points for every supersample (z = 0) - where the ground shadow would fall
        rows = (np.arange(CH * SS) + 0.5) / SS; cols = (np.arange(CW * SS) + 0.5) / SS
        Xg, Yg = np.meshgrid(cols, rows)
        self.G = np.stack([Xg - 88.0, (Yg - 160.0) / SE, np.zeros_like(Xg)], -1)


def depth(P):
    """bigger = nearer the camera."""
    return P[..., 1] * CE + P[..., 2] * SE


def shade(n, sh):
    nz = n[..., 2]
    ndl = np.clip((n * LIGHT).sum(-1), 0, None)
    return W.AMBIENT + W.SKY * (0.5 + 0.5 * nz) + W.DIFFUSE * ndl * (1 - 0.8 * sh)


def render(parts, th, z0, albedo, tower, window=(0, 0, CW, 170), grime_top=14.0, wear=None, chips=()):
    """parts: turret SDF parts (local frame, z from its foot); th: facing; z0: world height of its foot;
    albedo(comp, L, n_local, grain) -> rgb; tower: TowerScene. Returns straight-alpha RGBA and the
    house-colour mask (as L)."""
    x0, y0, x1, y1 = window
    rows = (np.arange(y0 * SS, y1 * SS) + 0.5) / SS; cols = (np.arange(x0 * SS, x1 * SS) + 0.5) / SS
    X, Y = np.meshgrid(cols, rows)
    zhi = z0 + 90.0
    hit, Wp = T.march(parts, th, X, Y, CAM, z0, z0 - 2.0, zhi)
    sl = np.s_[y0 * SS:y1 * SS, x0 * SS:x1 * SS]
    th_hit = tower.hit[sl]; TP = tower.P[sl]
    mine = hit & (~th_hit | (depth(Wp) > depth(TP) + 0.05))
    out = np.zeros(X.shape + (4,))
    trim = np.zeros(X.shape)
    idx = np.flatnonzero(mine)
    if idx.size:
        Pw = Wp.reshape(-1, 3)[idx]
        n = T.normals(parts, th, Pw, z0)
        Lp = T.to_local(Pw[:, 0], Pw[:, 1], Pw[:, 2], th, z0)
        d, comp = T.scene_sdf(parts, Lp, want_comp=True)
        fdir, rdir = T.local_dirs(th)
        nl = np.stack([(n * fdir).sum(-1), (n * rdir).sum(-1), n[:, 2]], -1)       # normal in local terms
        sh = T.occluded(parts, th, Pw + n * 0.3, z0, L_SH).astype(float)
        # texture coordinates in the turret's own frame, so the grain turns with it
        ax = np.abs(nl).argmax(-1)
        u = np.where(ax == 0, Lp[:, 1], Lp[:, 0]); v = np.where(ax == 2, Lp[:, 1], Lp[:, 2])
        grain = sample(NOISE_FINE, u * 1.0 + 7.0, v + 3.0) * 0.035 + sample(NOISE_MOTTLE, u, v) * 0.05
        alb, is_green = albedo(comp, Lp, nl, grain, u, v)
        if wear is not None:
            near_cut = np.zeros(len(Lp), bool)
            for c in chips:
                near_cut |= np.abs(T.sd_part(c, Lp)) < 1.0
            alb = wear(alb, comp, Lp, nl, u, v, is_green, near_cut)
        grime = np.clip(1 - Lp[:, 2] / grime_top, 0, 1) ** 1.5 * np.clip(0.55 + 0.35 * sample(NOISE_GRIME, u, v), 0, 1)
        grime = grime * ~is_green * 0.7
        alb = alb * (1 - grime[:, None]) + W.GRIME * grime[:, None]
        col = alb * shade(n, sh)[:, None]
        o = out.reshape(-1, 4)
        o[idx, :3] = col; o[idx, 3] = 1.0
        trim.flat[idx] = is_green.astype(float)
    # the turret's shadow on the tower (where the tower is lit and not covered by the turret)
    vis_t = th_hit & ~mine
    tidx = np.flatnonzero(vis_t & ~tower.own_shadow[sl])
    if tidx.size:
        TPf = TP.reshape(-1, 3)[tidx]; nt = tower.n[sl].reshape(-1, 3)[tidx]
        blk = T.occluded(parts, th, TPf + nt * 0.4, z0, L_SH)
        ndl = np.clip((nt * LIGHT).sum(-1), 0, None)
        base = W.AMBIENT + W.SKY * (0.5 + 0.5 * nt[:, 2])
        k = 1 - (base + W.DIFFUSE * ndl * 0.2) / (base + W.DIFFUSE * ndl)
        a = np.zeros(X.size); a[tidx] = np.where(blk, k, 0.0)
        a = ndimage.gaussian_filter(a.reshape(X.shape), 0.6 * SS)
        a = np.where(vis_t, a, 0.0)
        o = out.reshape(-1, 4)
        put = (o[:, 3] == 0)
        o[:, 3] = np.where(put, a.ravel(), o[:, 3])
    # on the ground, where neither the tower nor the turret is: the turret's shadow, only what it adds to
    # the tower frame's own
    ground = ~th_hit & ~mine
    G = tower.G[sl]
    gidx = np.flatnonzero(ground)
    if gidx.size:
        blk = T.occluded(parts, th, G.reshape(-1, 3)[gidx], z0, L_SH, tmax=260.0)
        g = np.zeros(X.size); g[gidx] = blk
        g = ndimage.gaussian_filter(g.reshape(X.shape), 1.5 * SS) * W.SHADOW_ALPHA
        af = tower.frame_alpha[sl]
        g = np.where(af < 0.999, np.clip((g - af) / np.maximum(1 - af, 1e-3), 0, 1), 0.0) * ground
        o = out.reshape(-1, 4)
        o[:, 3] = np.where(o[:, 3] == 0, g.ravel(), o[:, 3])
    # outline round the turret where it stands against the ground (not over the tower)
    ring = ndimage.binary_dilation(mine, iterations=int(0.9 * SS)) & ~mine & ~th_hit
    out[..., :3] = np.where(ring[..., None], 28.0, out[..., :3])
    out[..., 3] = np.where(ring, np.maximum(out[..., 3], 0.55), out[..., 3])
    # downsample (premultiplied) into the full canvas
    full = np.zeros((CH * SS, CW * SS, 4)); full[sl] = out
    ftrim = np.zeros((CH * SS, CW * SS)); ftrim[sl] = trim
    pre = full.copy(); pre[..., :3] *= full[..., 3:4]
    pre = pre.reshape(CH, SS, CW, SS, 4).mean(axis=(1, 3))
    a = pre[..., 3:4]
    rgb = np.where(a > 1e-6, pre[..., :3] / np.maximum(a, 1e-6), 0)
    img = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.clip(a * 255, 0, 255)]).round().astype(np.uint8), 'RGBA')
    tm = ftrim.reshape(CH, SS, CW, SS).mean(axis=(1, 3))
    return R.fade_right(img), Image.fromarray((tm * 255).round().astype(np.uint8), 'L')
