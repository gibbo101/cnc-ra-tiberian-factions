"""Class-map score for the Dropship Bay fit: TS's GTDROP 0 pixels sorted into colour classes (house, blue-grey, tan,
dark grey, grey) against the model's visible components in TS's camera, per TS pixel.
    score(p, region=None) -> (agreement, silhouette IoU, per-class IoU)
    python3 gdropscore.py   prints the score and writes a class-map comparison"""
import sys, time
import numpy as np
from PIL import Image
import hd, gdrop as M, plug as PL, gdropfit as F

D = '/home/claude/work/ts/ts-buildings-hd-handoff/11b-GTDROP/ts-original/'
PAL = np.frombuffer(open('/home/claude/work/inbox/dropship/ts-dropship-bay/UNITTEM.PAL', 'rb').read(), np.uint8
                    ).reshape(256, 3).astype(int) * 4
NAMES = ('none', 'house', 'blue', 'tan', 'dark', 'grey', 'other')
COLS = np.array([(30, 30, 30), (0, 200, 0), (120, 120, 230), (200, 150, 70), (60, 60, 60), (170, 170, 170), (255, 0, 255)],
                np.uint8)


def ts_classes(k=0, shp='GTDROP'):
    idx = np.load(D + f'{shp}/index/{k:02d}.npy')
    rgb = PAL[idx]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    s = rgb.max(-1) - rgb.min(-1)
    lum = 0.3 * r + 0.59 * g + 0.11 * b
    house = (idx >= 16) & (idx < 32)
    blue = (b > r + 12) & (b >= g) & ~house
    grey = (s < 30) & ~house & ~blue
    tan = (r > b + 30) & ~house & ~blue
    c = np.full(idx.shape, 6, np.int8)
    c[tan] = 3
    c[grey & (lum < 100)] = 4
    c[grey & (lum >= 100)] = 5
    c[blue] = 2
    c[house] = 1
    c[idx == 0] = 0
    return c


TAN = {PL.BLOCK, PL.LIP, PL.LEDGE, PL.ROOF, PL.RIDGE, PL.RAMP, PL.STEP, PL.FRONT, PL.FOOT, M.WCROWN, M.WBODY, M.RAIL}
DARK = {M.PIT, PL.SLOT, PL.DISH, PL.JOINT, PL.DMOUNT}
GREY = {PL.PLAT, M.NWALL, M.RAMP2, PL.PIPE, PL.PCAP, M.PADM}
BLUE = {PL.FACE, M.WTRIM, M.ANT2, PL.ANT}


def model_classes(comp, hit):
    c = np.full(comp.shape, 6, np.int8)
    c[np.isin(comp, list(TAN))] = 3
    c[np.isin(comp, list(DARK))] = 4
    c[np.isin(comp, list(GREY))] = 5
    c[np.isin(comp, list(BLUE))] = 2
    c[np.isin(comp, list(M.HOUSE))] = 1
    c[~hit] = 0
    return c


_VIEW = {}


def comp_map(p=None, scale=2):
    """the visible component per screen px in TS's camera (hd.Render's march without its shading or shadow map)."""
    if scale not in _VIEW:
        v = F.view(scale, 1)
        X, Y = v.grid(200.0)
        _VIEW[scale] = (v, X, Y)
    v, X, Y = _VIEW[scale]
    sc = M.scene(X, Y, p=p)
    zs = v.zscale()
    Hm = hd.f32(sc.H * zs)
    slabs = []
    for s in sc.slabs:
        valid = s.top >= 0
        slabs.append((np.where(valid, s.top * zs, -1.0).astype(np.float32), np.where(valid, s.bot * zs, 1e9).astype(np.float32)))
    hit, kind = hd.march(v, Hm, slabs)
    k = np.maximum(hit, 0)
    rows = np.arange(v.Hc)[:, None] + v.g0 + k
    cols = np.arange(v.W)[None, :] + v.c0 + 0 * k
    comp = sc.C[rows, cols].copy()
    for s_i, s in enumerate(sc.slabs):
        m = kind == 2 + s_i
        comp[m] = s.comp[rows[m], cols[m]]
    hm = hit >= 0
    return np.where(hm, comp, 0), hm


def render_classes(p=None, scale=2):
    comp, hm = comp_map(p, scale)
    mc = model_classes(comp, hm)
    # to TS's pixels: the most common class in each scale x scale block
    h, w = F.FH, F.FW
    mc = mc[:h * scale, :w * scale].reshape(h, scale, w, scale).transpose(0, 2, 1, 3).reshape(h, w, scale * scale)
    out = np.zeros((h, w), np.int8)
    best = np.zeros((h, w), np.int16) - 1
    for k in range(7):
        n = (mc == k).sum(-1)
        win = n > best
        out = np.where(win, k, out); best = np.where(win, n, best)
    return out


def score(mc, tc, region=None):
    m = np.ones(tc.shape, bool) if region is None else region
    both = ((tc > 0) | (mc > 0)) & m
    agree = ((tc == mc) & both).sum() / max(both.sum(), 1)
    sil = ((tc > 0) & (mc > 0) & m).sum() / max(both.sum(), 1)
    per = {}
    for k in range(1, 6):
        a = (tc == k) & m; b = (mc == k) & m
        per[NAMES[k]] = round(float((a & b).sum() / max((a | b).sum(), 1)), 3)
    return float(agree), float(sil), per


def sheet(mc, tc, out, z=4):
    a = COLS[tc]; b = COLS[mc]
    diff = np.where((tc != mc)[..., None], np.array([255, 0, 255], np.uint8), (COLS[tc] * 0.5).astype(np.uint8))
    im = np.concatenate([a, np.zeros((tc.shape[0], 4, 3), np.uint8), b, np.zeros((tc.shape[0], 4, 3), np.uint8), diff], 1)
    Image.fromarray(im).crop((0, 40, im.shape[1], 144)).resize((im.shape[1] * z, 104 * z), Image.NEAREST).save(out)


if __name__ == '__main__':
    t = time.time()
    tc = ts_classes()
    mc = render_classes(scale=2)
    print('agree %.3f  sil %.3f' % score(mc, tc)[:2], score(mc, tc)[2], '%.1fs' % (time.time() - t))
    sheet(mc, tc, '/tmp/claude-0/-home-claude/7af62279-56cb-5238-8d9f-461835dd6a66/scratchpad/gdrop-classes.png')
