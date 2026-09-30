"""
Damage stages for the TS Nod wall, in BRIK's rows:
  stage 1 (frames 16-31): whole shape, chipped and bitten edges, cracks, scorch, grime (TS's damaged frames)
  stage 2 (frames 32-47): chunks broken out of the arms, buttress tips snapped, rebar, debris on the ground
  stage 3 (frames 48-63): only broken stumps where it joins its neighbours, rubble around (TS's heavily
                          damaged frames); frame 48 (no neighbours) is empty, like BRIK's
Colours stay in greys and browns: soot, dark cracks, paler fresh concrete at the breaks, brown-grey grime.
Damage fades out towards the cell edges so a damaged cell still meets a healthy neighbour cleanly.
"""
import numpy as np
from scipy import ndimage
import nodwall as N
from damage import Sampler, gnoise
from walls2 import smoothstep, SS, MARGIN, CELL

ARM, LEG, DEBRIS = N.ARM, N.LEG, N.DEBRIS
SOOT = np.array([30, 29, 28.])
FRESH = np.array([168, 166, 160.])       # broken concrete shows paler than the weathered skin
DUST = np.array([104, 98, 88.])          # brown-grey grime / dust
REBAR = np.array([62, 50, 42.])
ROCK_COLS = [N.CONC * 0.95, N.CONC * 0.78, FRESH * 0.9, DUST]


def edge_fade(X, Y, Z=None):
    """0 at the cell edges, 1 inside. The north side is measured on screen (y - FZ*z): the cell to the
    north draws the top of this cell's wall wherever it pokes up past the frame, and draws it whole, so
    damage must start only below the frame's top edge for the two frames to agree."""
    d = np.minimum.reduce([X, CELL - X, CELL - Y])
    f = smoothstep(3.0, 14.0, d)
    sy = Y - N.FZ * (Z if Z is not None else 0.0)
    return f * smoothstep(1.0, 12.0, sy)


def make(stage, seed):
    rng = np.random.default_rng(seed)
    S_crack, S_cmask, S_rough = Sampler(rng, 8.0), Sampler(rng, 12.0), Sampler(rng, 1.2)
    S_soot, S_dust, S_wear = Sampler(rng, 5.0), Sampler(rng, 4.0), Sampler(rng, 3.0)
    lvl = {1: dict(chip=1.05, crack=0.45, soot=0.55, dust=0.9),
           2: dict(chip=0.75, crack=0.1, soot=0.25, dust=0.6),
           3: dict(chip=1.15, crack=0.0, soot=0.2, dust=0.5)}[stage]

    def extra(mask, X, Y, H, C, AXIS):
        p = N.P
        H, C = H.copy(), C.copy()
        H0 = H.copy()
        fade = edge_fade(X, Y, H)
        broken = np.zeros_like(H)
        footprint = H > 0.5
        ROCK = np.zeros(H.shape + (3,))
        tall = H / max(H.max(), 1)

        # chipped / bitten edges: bites along the top edges, not holes in the middle of a face
        grad = np.hypot(*np.gradient(H, 1.0 / SS))
        edge_band = ndimage.maximum_filter((grad > 2.0).astype(float), size=int(3.5 * SS)) * footprint
        n = gnoise(H.shape, 2.6, rng)
        chip = smoothstep(lvl['chip'], lvl['chip'] + 0.5, n) * edge_band * fade
        chip = ndimage.gaussian_filter(chip, 0.5 * SS)
        H = np.maximum(H - 7.0 * chip * np.clip(H / 12.0, 0, 1), 0)
        broken = np.maximum(broken, smoothstep(0.15, 0.6, chip))

        if stage >= 2:
            # bites out of the arms' tops
            cand = np.flatnonzero((C == ARM) & (H > 0.55 * p['H']) & (fade > 0.97))
            jag = gnoise(H.shape, 2.0, rng)
            floor_n = gnoise(H.shape, 5.0, rng)
            bumps = gnoise(H.shape, 1.3, rng)
            for _ in range((1 + (rng.random() < 0.6)) if cand.size else 0):
                k = rng.choice(cand)
                cx, cy = X.flat[k], Y.flat[k]
                R = rng.uniform(12, 18)
                d = np.hypot(X - cx, Y - cy) + 3.0 * jag
                inside = smoothstep(R + 1.5, R - 1.5, d) * fade
                floor = np.maximum(H * np.clip(0.35 + 0.12 * floor_n, 0.12, 0.6) + 1.4 * bumps, 0)
                H = H * (1 - inside) + np.minimum(H, floor) * inside
                broken = np.maximum(broken, inside * (H > 0.5))
            # buttress tips snapped off, the break left jagged
            if (C == LEG).any():
                along = np.hypot(X - p['x_c'], Y - p['y_c'])
                cut = 26 + 10 * rng.random() + 4 * gnoise(H.shape, 2.5, rng)
                snap = (C == LEG) & (along > cut)
                # take the blurred fringe with it, but never eat into an arm
                snap_d = ndimage.binary_dilation(snap, iterations=int(2.5 * SS)) & (C != ARM) & (along > cut - 1)
                H = np.where(snap_d, 0, H)
                C = np.where(snap_d, 0, C)
                stub = (C == LEG) & (np.abs(along - cut) < 4)
                broken = np.maximum(broken, stub * 1.0)

        if stage == 3:
            # only stumps at the joints remain
            s_edge = np.minimum.reduce([X, CELL - X, Y, CELL - Y])
            arm_owned = (C == ARM)
            if mask == 0:
                arm_owned[:] = False
            conn = np.zeros_like(H, bool)
            for bit, sel in ((1, Y < CELL / 2), (2, X > CELL / 2), (4, Y > CELL / 2), (8, X < CELL / 2)):
                if mask & bit:
                    conn |= sel & (np.where(bit in (1, 4), np.abs(X - p['x_c']), np.abs(Y - p['y_c'])) < p['ta'] + 3)
            arm_owned &= conn
            jag = gnoise(H.shape, 2.5, rng)
            L = np.where(Y < CELL / 2, 34.0, 26.0) + 3.0 * gnoise(H.shape, 6.0, rng)
            keep = smoothstep(L + 3, L - 3, s_edge + 3.0 * jag) * arm_owned
            sag = 1 - 0.45 * (1 - keep) ** 0.5 * (keep > 0.02)
            newH = np.maximum(H0 * keep * sag + 1.2 * gnoise(H.shape, 1.3, rng) * (keep > 0.05) * (keep < 0.95), 0)
            broken = np.clip((H0 - newH) / np.maximum(H0, 1e-3), 0, 1) * (newH > 0.5)
            H = newH

        # rubble on the ground
        n_rocks = {1: rng.integers(2, 4), 2: rng.integers(6, 10), 3: rng.integers(8, 12)}[stage]
        if stage == 3 and mask == 0:
            n_rocks = 0
        if n_rocks:
            dist = ndimage.distance_transform_edt(~footprint) / SS
            ok = (dist > 1.5) & (dist < 20) & (X > 14) & (X < CELL - 14) & (Y > 14) & (Y < CELL - 8)
            if stage == 3:
                ok = (X > 14) & (X < CELL - 14) & (Y > 14) & (Y < CELL - 8) & (dist < 24) & (H < 0.5)
            cand = np.flatnonzero(ok)
            rj = gnoise(H.shape, 2.0, rng)
            for _ in range(n_rocks if cand.size else 0):
                k = rng.choice(cand)
                cx, cy = X.flat[k], Y.flat[k]
                r = rng.uniform(2.6, 5.6) * (0.7 if stage == 1 else 1.0)
                # an angular chunk: a random polygon footprint, faceted sides, a tilted broken top
                nf = rng.integers(5, 8)
                ang = np.sort(rng.uniform(0, 2 * np.pi, nf)) + rng.uniform(0, 1)
                dist_k = r * rng.uniform(0.7, 1.1, nf)
                win_ = (np.abs(X - cx) < 2 * r + 2) & (np.abs(Y - cy) < 2 * r + 2)
                dX, dY = X[win_] - cx, Y[win_] - cy
                g = np.max([np.cos(a) * dX + np.sin(a) * dY - dk for a, dk in zip(ang, dist_k)], axis=0)
                top = r * rng.uniform(0.55, 0.9)
                tx, ty = rng.normal(0, 0.18, 2)
                h = np.clip(-g * rng.uniform(1.3, 2.4), 0, None)
                h = np.minimum(h, np.clip(top + tx * dX + ty * dY, 0.4, None)) * (g < 0)
                hh = np.zeros_like(H); hh[win_] = h
                win = hh > H
                col = ROCK_COLS[rng.choice(len(ROCK_COLS), p=[0.4, 0.3, 0.2, 0.1])] * rng.uniform(0.9, 1.08)
                H = np.where(win, hh, H)
                C = np.where(win, DEBRIS, C)
                ROCK[win] = col

        H = ndimage.gaussian_filter(H, 0.35 * SS, mode='nearest')

        # scorch marks (on the wall and the ground under it), one or two per cell
        scorch = []
        for _ in range(1 + (rng.random() < 0.5) + (stage >= 2)):
            scorch.append((rng.uniform(20, 108), rng.uniform(24, 104), rng.uniform(14, 26)))

        def mats(albedo, x, y, z, comp, top_like, grain, u, v, top_h):
            i = np.clip(((x + MARGIN) * SS).astype(int), 0, H.shape[1] - 1)
            j = np.clip(((y + MARGIN) * SS).astype(int), 0, H.shape[0] - 1)
            f = smoothstep(0.0, 0.6, edge_fade(x, y, z))   # nothing right at the joins, so neighbours match
            brk = broken[j, i]
            wall = (comp != DEBRIS)[..., None]
            out = albedo.copy()
            # grime / dust (brown-grey), heavier low down and on the tops
            dust = smoothstep(lvl['dust'], lvl['dust'] + 0.6, S_dust(u, v)) * f * np.where(top_like, 0.55, 0.35)
            out = out * (1 - dust[..., None]) + DUST * (1 + grain)[..., None] * dust[..., None]
            # scorch
            s = np.zeros_like(x)
            for (sx_, sy_, sr) in scorch:
                s = np.maximum(s, np.exp(-(((x - sx_) ** 2 + (y - sy_) ** 2) / sr ** 2)))
            soot = smoothstep(0.25, 0.85, np.clip(s * (0.55 + 0.45 * S_soot(u, v)), 0, 1)) * f
            soot = soot * (0.6 if stage == 1 else 0.75)
            out = out * (1 - soot[..., None]) + SOOT * soot[..., None]
            # cracks
            cn = S_crack(u, v) + 0.10 * S_rough(u, v)
            crack = (1 - smoothstep(0.015, 0.06, np.abs(cn))) * smoothstep(lvl['crack'], lvl['crack'] + 0.3, S_cmask(u, v)) * f
            out *= (1 - 0.65 * crack)[..., None]
            # fresh breaks: paler, rough, with dark rebar
            rough = S_rough(u, v)
            bcol = FRESH * np.clip(0.84 + 0.10 * rough, 0.6, 1.0)[..., None]
            bcol = np.where((rough < -1.0)[..., None], N.CONC * 0.6, bcol)
            rebar = (1 - smoothstep(0.02, 0.07, np.abs(S_crack(v * 3.0, u * 0.8)))) * (brk > 0.4) * (stage >= 2)
            bcol = bcol * (1 - rebar[..., None]) + REBAR * rebar[..., None]
            b = np.clip(brk * 1.6, 0, 1)[..., None]
            out = out * (1 - b) + bcol * b
            rock = ROCK[j, i] * (1 + 1.5 * grain)[..., None]
            return np.where(wall, out, rock)

        return X, Y, H, C, AXIS, mats

    return extra


def render(mask, stage):
    if stage == 0:
        return N.render(mask)
    if stage == 3 and mask == 0:
        from PIL import Image
        return Image.new('RGBA', (CELL, CELL), (0, 0, 0, 0))
    return N.render(mask, extra=make(stage, seed=5000 + 1000 * stage + mask))


if __name__ == '__main__':
    import sys, os
    os.makedirs('nod/out', exist_ok=True)
    stages = [int(s) for s in sys.argv[1:]] or [1, 2, 3]
    for st in stages:
        for m in range(16):
            render(m, st).save(f'nod/out/nod-wall-{16 * st + m:02d}.png')
        print('stage', st, 'done', flush=True)
