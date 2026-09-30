"""
Damage stages for the TS GDI wall, modelled on BRIK's rows:
  stage 1 (frames 16-31): intact shape, chipped edges, cracks, rust/peeled patches, worn paint
  stage 2 (frames 32-47): chunks broken out, rebar showing, debris on the ground
  stage 3 (frames 48-63): only broken stubs left where it joins its neighbours, rubble around;
                          frame 48 (no neighbours) is empty, like BRIK's.
Damage fades out towards the cell edges so a damaged cell still meets a healthy
neighbour cleanly.
"""
import numpy as np
from scipy import ndimage
import walls2 as W
from walls2 import smoothstep, CONC, COLLAR, PILLAR, SS, MARGIN, CELL

DEBRIS = 4
RUST = np.array([150, 104, 74.])
PEEL = np.array([186, 162, 146.])     # pinkish exposed concrete, as on BRIK's damaged tops
CHIPW = np.array([232, 226, 214.])
MOSS = np.array([96, 112, 60.])
DARK = np.array([58, 55, 50.])
ROCK_COLS = [W.CONCRETE * 0.92, W.CONCRETE * 0.78, RUST * 1.05, W.OCHRE * 0.9]


def gnoise(shape, sigma_px, rng):
    n = ndimage.gaussian_filter(rng.standard_normal(shape), sigma_px * SS, mode='wrap')
    return n / n.std()


class Sampler:
    """Non-periodic noise looked up by HD-px coordinates."""
    def __init__(self, rng, sigma, lo=-64, size=320, res=2):
        n = ndimage.gaussian_filter(rng.standard_normal((size * res, size * res)), sigma * res, mode='wrap')
        self.n, self.lo, self.res, self.size = n / n.std(), lo, res, size

    def __call__(self, u, v):
        iu = np.clip(((u - self.lo) * self.res).astype(int), 0, self.size * self.res - 1)
        iv = np.clip(((v - self.lo) * self.res).astype(int), 0, self.size * self.res - 1)
        return self.n[iv, iu]


def edge_fade(X, Y, w0=3.0, w1=14.0):
    d = np.minimum.reduce([X, CELL - X, Y, CELL - Y])
    return smoothstep(w0, w1, d)


def make(stage, seed):
    rng = np.random.default_rng(seed)
    S_rust, S_crack, S_cmask = Sampler(rng, 4.0), Sampler(rng, 8.0), Sampler(rng, 12.0)
    S_moss, S_wear, S_rough = Sampler(rng, 5.0), Sampler(rng, 3.0), Sampler(rng, 1.2)
    lvl = {1: dict(chip=1.75, rust=0.95, crack=0.55, wear=0.75, moss=1.9),
           2: dict(chip=1.35, rust=0.55, crack=0.15, wear=0.35, moss=1.6),
           3: dict(chip=1.20, rust=0.45, crack=0.0, wear=0.2, moss=1.5)}[stage]

    def extra(mask, X, Y, H, C, AXIS):
        p = W.P
        H, C = H.copy(), C.copy()
        fade = edge_fade(X, Y)
        broken = np.zeros_like(H)
        footprint = H > 0.5
        ROCK = np.zeros(H.shape + (3,))

        # chipped edges / dents
        chip = smoothstep(lvl['chip'], lvl['chip'] + 0.6, gnoise(H.shape, 2.2, rng)) * fade * footprint
        H = np.maximum(H - 7.0 * chip, 0)
        broken = np.maximum(broken, chip)

        # chunks broken out of the wall
        if stage == 2:
            cand = np.flatnonzero((H > 0.6 * H.max()) & (fade > 0.97))
            n_breaks = 1 + (rng.random() < 0.6)
            jag = gnoise(H.shape, 2.0, rng)
            floor_n = gnoise(H.shape, 5.0, rng)
            bumps = gnoise(H.shape, 1.3, rng)
            for _ in range(n_breaks if cand.size else 0):
                k = rng.choice(cand)
                cx, cy = X.flat[k], Y.flat[k]
                R = rng.uniform(13, 19)
                d = np.hypot(X - cx, Y - cy) + 3.0 * jag
                inside = smoothstep(R + 1.5, R - 1.5, d) * fade
                floor = np.maximum(H * np.clip(0.32 + 0.12 * floor_n, 0.1, 0.55) + 1.4 * bumps, 0)
                newH = np.minimum(H, floor)
                H = H * (1 - inside) + newH * inside
                broken = np.maximum(broken, inside * (H > 0.5))

        # only stubs remain where the wall meets its neighbours
        if stage == 3:
            xc, yc = p['x_c'], p['y_c']
            s_edge = np.where(AXIS == 0, np.where(X >= xc, CELL - X, X),
                              np.where(Y <= yc, Y, CELL - Y))
            arm_owned = (C == CONC) | (C == COLLAR)
            if mask == 0:
                arm_owned[:] = False
            jag = gnoise(H.shape, 2.5, rng)
            L = 24.0 + 4.0 * gnoise(H.shape, 6.0, rng)
            keep = smoothstep(L + 3, L - 3, s_edge + 3.0 * jag) * arm_owned
            # broken end: sagging, with a little rubble texture
            sag = 1 - 0.4 * (1 - keep) ** 0.5 * (keep > 0.02)
            newH = np.maximum(H * keep * sag + 1.0 * gnoise(H.shape, 1.3, rng) * (keep > 0.05) * (keep < 0.95), 0)
            broken = np.maximum(broken, np.clip((H - newH) / np.maximum(H, 1e-3), 0, 1) * (newH > 0.5))
            H = newH

        # rubble on the ground
        n_rocks = {1: 0, 2: rng.integers(5, 9), 3: rng.integers(7, 11)}[stage]
        if stage == 3 and mask == 0:
            n_rocks = 0
        if n_rocks:
            dist = ndimage.distance_transform_edt(~footprint) / SS
            ok = (dist > 1.5) & (dist < 22) & (X > 6) & (X < CELL - 6) & (Y > 6) & (Y < CELL - 6)
            if stage == 3:   # where the wall used to be, too
                ok = (X > 6) & (X < CELL - 6) & (Y > 6) & (Y < CELL - 6) & (dist < 26) & (H < 0.5)
            cand = np.flatnonzero(ok)
            rj = gnoise(H.shape, 2.0, rng)
            for _ in range(n_rocks if cand.size else 0):
                k = rng.choice(cand)
                cx, cy = X.flat[k], Y.flat[k]
                r = rng.uniform(2.6, 5.6)
                sx, sy = rng.uniform(0.8, 1.25), rng.uniform(0.8, 1.25)
                d = np.hypot((X - cx) / sx, (Y - cy) / sy)
                rr = r * (1 + 0.15 * rj)
                h = np.where(d < rr, 0.95 * r * np.sqrt(np.clip(1 - (d / rr) ** 2, 0, 1)), 0)
                win = h > H
                col = ROCK_COLS[rng.choice(len(ROCK_COLS), p=[0.45, 0.3, 0.15, 0.1])]
                H = np.where(win, h, H)
                C = np.where(win, DEBRIS, C)
                ROCK[win] = col

        H = ndimage.gaussian_filter(H, 0.45 * SS, mode='nearest')

        def mats(albedo, x, y, z, comp, top_like, grain, u, v, along):
            i = np.clip(((x + MARGIN) * SS).astype(int), 0, H.shape[1] - 1)
            j = np.clip(((y + MARGIN) * SS).astype(int), 0, H.shape[0] - 1)
            f = 0.2 + 0.8 * fade[j, i]
            brk = broken[j, i]
            wall = (comp != DEBRIS)[..., None]
            ochre = (comp == COLLAR) | (comp == PILLAR) & ~top_like
            out = albedo.copy()
            # worn paint on the ochre parts
            wear = smoothstep(lvl['wear'], lvl['wear'] + 0.4, S_wear(u, v)) * ochre * f
            out = out * (1 - wear[..., None]) + W.CONCRETE * 0.82 * wear[..., None]
            # rust and peeled patches (tops take more, faces get streaks)
            vv = np.where(top_like, v, v * 0.3)
            nr = S_rust(u, vv)
            rust = smoothstep(lvl['rust'], lvl['rust'] + 0.5, nr) * f * np.where(top_like, 0.75, 0.55)
            peel = smoothstep(lvl['rust'] + 0.5, lvl['rust'] + 0.9, nr) * top_like * f * 0.75
            out = out * (1 - rust[..., None]) + RUST * (1 + grain)[..., None] * rust[..., None]
            out = out * (1 - peel[..., None]) + PEEL * (1 + grain)[..., None] * peel[..., None]
            # moss
            moss = smoothstep(lvl['moss'], lvl['moss'] + 0.4, S_moss(u, v)) * f * 0.8
            out = out * (1 - moss[..., None]) + MOSS * moss[..., None]
            # cracks
            cn = S_crack(u, v) + 0.10 * S_rough(u, v)          # jagged, not wormy
            crack = (1 - smoothstep(0.015, 0.06, np.abs(cn))) * smoothstep(lvl['crack'], lvl['crack'] + 0.3, S_cmask(u, v)) * f
            out *= (1 - 0.7 * crack)[..., None]
            # fresh breaks: rough, rusty, with pale chipped edges and dark rebar
            rough = S_rough(u, v)
            bcol = CHIPW * np.clip(0.86 + 0.10 * rough, 0.6, 1.0)[..., None]    # fresh breaks read pale
            bcol = np.where((rough < -1.0)[..., None], W.CONCRETE * 0.6, bcol)
            rt = smoothstep(0.2, 0.9, S_rust(u * 2.1, v * 2.1)) * 0.55
            bcol = bcol * (1 - rt[..., None]) + RUST * rt[..., None]
            rebar = (1 - smoothstep(0.02, 0.07, np.abs(S_crack(v * 3.0, u * 0.8)))) * (brk > 0.4)
            bcol = bcol * (1 - 0.55 * rebar)[..., None]
            b = np.clip(brk * 1.6, 0, 1)[..., None]
            out = out * (1 - b) + bcol * b
            # rubble keeps its own colour
            rock = ROCK[j, i] * (1 + 1.5 * grain)[..., None]
            return np.where(wall, out, rock)

        return X, Y, H, C, AXIS, mats

    return extra


def render(mask, stage):
    if stage == 0:
        return W.render(mask)
    if stage == 3 and mask == 0:
        from PIL import Image
        return Image.new('RGBA', (CELL, CELL), (0, 0, 0, 0))
    return W.render(mask, extra=make(stage, seed=1000 * stage + mask))


if __name__ == '__main__':
    import sys, os
    os.makedirs('out2', exist_ok=True)
    stages = [int(s) for s in sys.argv[1:]] or [1, 2, 3]
    for st in stages:
        for m in range(16):
            render(m, st).save(f'out2/gdi-wall-{16 * st + m:02d}.png')
        print('stage', st, 'done')
