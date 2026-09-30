"""
Damage for the component tower: frame 1 damaged, frame 2 destroyed. Greys and browns only (soot, cracks,
dust, pale fresh breaks); the green ring's pieces stay green (house colour). The wall stubs keep their
ends clean so the walls still join.
"""
import numpy as np
from scipy import ndimage
import walls2 as W
from walls2 import smoothstep, SS
from damage import Sampler
import ct_ra as R
from ctower import PAD, CORE, RIB, SKIRT, TOP, RING, CONN, COLLAR, STRUT

DEBRIS = 20
SOOT = np.array([30, 29, 28.])
FRESH = np.array([206, 198, 180.])      # broken khaki/concrete shows paler
DUST = np.array([120, 110, 92.])
REBAR = np.array([60, 48, 40.])
ROCKS = {'khaki': R.KHAKI * 0.95, 'khaki_dk': R.KHAKI * 0.75, 'conc': W.CONCRETE * 0.85,
         'plate': R.PLATE * 0.9, 'green': R.GREEN * 0.85, 'dark': np.array([70, 70, 74.])}


def gn(shape, sigma, rng):
    n = ndimage.gaussian_filter(rng.standard_normal(shape), sigma * SS, mode='wrap')
    return n / n.std()


def make(level, seed=7):
    rng = np.random.default_rng(seed)
    S_crack, S_cmask, S_rough = Sampler(rng, 8.0), Sampler(rng, 12.0), Sampler(rng, 1.2)
    S_soot, S_dust = Sampler(rng, 5.0), Sampler(rng, 4.0)

    def damage(H, C, slab):
        X, Y = R.GX, R.GY
        dx, dy = R.phys(X, Y)
        r = np.hypot(dx, dy)
        own = (X >= 0) & (X <= 128) & (Y >= 0) & (Y <= 128)
        edge_d = np.minimum.reduce([X, 128 - X, Y, 128 - Y])
        keep_edges = smoothstep(4.0, 18.0, edge_d)                 # wall stubs stay whole at the joints
        H = H.copy(); C = C.copy()
        top = slab['top'].copy(); scomp = slab['comp'].copy()
        broken = np.zeros_like(H)
        rock = np.zeros(H.shape + (3,))
        tower = own & np.isin(C, [SKIRT, RIB, CORE])

        # chips along the high edges
        grad = np.hypot(*np.gradient(H, 1.0 / SS))
        band = ndimage.maximum_filter((grad > 2.0).astype(float), size=int(3.5 * SS)) * own
        n = gn(H.shape, 2.4, rng)
        chip = smoothstep(0.9 if level == 1 else 0.5, 1.5 if level == 1 else 1.1, n) * band * keep_edges
        chip = ndimage.gaussian_filter(chip, 0.5 * SS)
        H = np.where(own, np.maximum(H - (7.0 if level == 1 else 10.0) * chip * np.clip(H / 12, 0, 1), 0), H)
        broken = np.maximum(broken, smoothstep(0.15, 0.6, chip))

        if level == 1:
            # a bite out of the plate and ring (south-west), a hole in the roof below it
            d = np.hypot(dx + 24, dy - 20) + 3.0 * gn(H.shape, 1.8, rng)
            bite = d < 17
            top = np.where(bite, -1.0, top); scomp = np.where(bite, 0, scomp)
            hole = (d < 13) & tower
            floor = R.T['body_z'] * (0.55 + 0.08 * gn(H.shape, 3.0, rng))
            H = np.where(hole, np.minimum(H, floor), H)
            broken = np.maximum(broken, (d < 15) * tower * 1.0)
            # one brace snapped at the north-east
            for (cx, cy) in ((40, -20),):
                dd = np.hypot(dx - cx, dy - cy)
                snap = (C == RIB) & (dd < 14)
                H = np.where(snap, H * 0.35, H)
                broken = np.maximum(broken, snap * 1.0)
            n_rocks, sizes = 7, (2.4, 5.0)
        else:
            # destroyed: a hollow, broken shell of the body; braces snapped low; plate and ring gone
            jag = gn(H.shape, 1.6, rng)
            wave = gn(H.shape, 6.0, rng)
            a_, ch_ = R.T['body_a'], R.T['chamfer']
            ax, ay = np.abs(dx), np.abs(dy)
            inb = own & np.isin(C, [SKIRT, CORE, RIB])
            shell = R.T['body_z'] * (0.46 + 0.10 * wave) + 2.5 * jag
            depth_in = np.clip((a_ - 7 - np.maximum(ax, ay)) / 10.0, 0, 1)        # hollow inside the walls
            stump = shell - (shell - R.T['body_z'] * 0.16) * depth_in
            newH = np.where(inb, np.minimum(H, np.maximum(stump, 2.5)), H)
            ribcut = own & (C == RIB)
            newH = np.where(ribcut, np.minimum(newH, R.T['body_z'] * 0.26 + 2.5 * jag), newH)
            broken = np.maximum(broken, np.clip((H - newH) / np.maximum(H, 1e-3), 0, 1) * (newH > 0.5))
            core = own & inb & (np.maximum(ax, ay) < a_ - 7)
            C = np.where(core, CORE, C)
            H = newH
            top = np.full_like(top, -1.0); scomp = np.zeros_like(scomp)
            n_rocks, sizes = 13, (2.6, 6.2)

        # rubble: angular chunks of khaki, concrete, plate and green ring
        names = list(ROCKS)

        def chunk(cx, cy, rr, colname, on_top):
            nonlocal H, C
            nf = rng.integers(5, 8)
            ang = np.sort(rng.uniform(0, 2 * np.pi, nf))
            dk = rr * rng.uniform(0.7, 1.1, nf)
            win_ = (np.abs(X - cx) < 2 * rr + 2) & (np.abs(Y - cy) < (2 * rr + 2) * R.SYF + 1)
            ddx, ddy = X[win_] - cx, (Y[win_] - cy) / R.SYF
            g = np.max([np.cos(a_) * ddx + np.sin(a_) * ddy - d_ for a_, d_ in zip(ang, dk)], axis=0)
            topz = rr * rng.uniform(0.55, 0.9)
            tx, ty = rng.normal(0, 0.18, 2)
            h = np.clip(-g * rng.uniform(1.3, 2.4), 0, None)
            h = np.minimum(h, np.clip(topz + tx * ddx + ty * ddy, 0.4, None)) * (g < 0)
            base = H[win_] * 0.95 if on_top else 0.0
            hh = np.zeros_like(H); hh[win_] = np.where(h > 0, h + base, 0)
            win = hh > H
            H = np.where(win, hh, H); C = np.where(win, DEBRIS, C)
            rock[win] = ROCKS[colname] * rng.uniform(0.9, 1.08)

        pr = np.array([0.35, 0.22, 0.2, 0.13, 0.0, 0.1])
        pr = pr / pr.sum()
        ground_ok = own & (X > 12) & (X < 116) & (np.hypot(dx, dy) < 74) & (H < 4.5)
        cand = np.flatnonzero(ground_ok)
        n_ground = 7 if level == 1 else 10
        for _ in range(n_ground if cand.size else 0):
            kk = rng.choice(cand)
            chunk(X.flat[kk], Y.flat[kk], rng.uniform(*sizes), names[rng.choice(len(names), p=pr)], False)
        if level == 1:
            for _ in range(2):                                  # a couple of shards of the broken ring
                kk = rng.choice(cand)
                chunk(X.flat[kk], Y.flat[kk], rng.uniform(1.8, 3.0), 'green', False)
        else:
            inner = own & (np.maximum(np.abs(dx), np.abs(dy)) < R.T['body_a'] - 9)
            ci = np.flatnonzero(inner)
            for _ in range(7):                                  # rubble in the hollow
                kk = rng.choice(ci)
                chunk(X.flat[kk], Y.flat[kk], rng.uniform(3.5, 7.0), names[rng.choice(len(names), p=pr)], True)
            for _ in range(2):                                  # bits of the top plate
                kk = rng.choice(ci)
                chunk(X.flat[kk], Y.flat[kk], rng.uniform(4.0, 6.5), 'plate', True)
            for _ in range(4):                                  # shards of the green ring
                kk = rng.choice(np.concatenate([ci, cand]))
                chunk(X.flat[kk], Y.flat[kk], rng.uniform(1.8, 3.2), 'green', True)
        H = ndimage.gaussian_filter(H, 0.3 * SS, mode='nearest')
        slab2 = dict(top=top, lo=slab['lo'], comp=scomp)

        scorch = [(-18, 16, 26.0), (22, -10, 20.0)] if level == 1 else \
                 [(0, 0, 36.0), (-26, 24, 22.0), (24, 20, 22.0)]

        def mats(alb, x, y, z, comp, top_like, grain, u, v):
            i = np.clip(((x + R.OX + R.MG) * SS).astype(int), 0, H.shape[1] - 1)
            j = np.clip(((y + R.OY + R.MG) * SS).astype(int), 0, H.shape[0] - 1)
            ed = np.minimum.reduce([np.abs(x), np.abs(128 - x), np.abs(y), np.abs(128 - y)])
            f = smoothstep(4.0, 18.0, ed)
            out = alb.copy()
            nr = ~(comp == RING)
            dust = smoothstep(0.7, 1.4, S_dust(u, v)) * f * np.where(top_like, 0.5, 0.3) * nr
            out = out * (1 - dust[..., None]) + DUST * (1 + grain)[..., None] * dust[..., None]
            s = np.zeros_like(x)
            pdx, pdy = R.phys(x, y)
            for (sx, sy, sr) in scorch:
                s = np.maximum(s, np.exp(-(((pdx - sx) ** 2 + (pdy - sy) ** 2) / sr ** 2)))
            soot = smoothstep(0.25, 0.85, np.clip(s * (0.55 + 0.45 * S_soot(u, v)), 0, 1)) * f
            soot = soot * (0.6 if level == 1 else 0.8) * ~(comp == RING)
            out = out * (1 - soot[..., None]) + SOOT * soot[..., None]
            cn = S_crack(u, v) + 0.10 * S_rough(u, v)
            crack = (1 - smoothstep(0.015, 0.06, np.abs(cn))) * smoothstep(0.35 if level == 1 else 0.0, 0.65, S_cmask(u, v)) * f
            out *= (1 - 0.65 * crack * nr)[..., None]
            brk = broken[j, i]
            rough = S_rough(u, v)
            bcol = FRESH * np.clip(0.84 + 0.1 * rough, 0.6, 1.0)[..., None]
            bcol = np.where((rough < -0.9)[..., None], np.array([90, 84, 72.]), bcol)
            rebar = (1 - smoothstep(0.02, 0.07, np.abs(S_crack(v * 3.0, u * 0.8)))) * (brk > 0.4)
            bcol = bcol * (1 - rebar[..., None]) + REBAR * rebar[..., None]
            b = np.clip(brk * 1.6, 0, 1)[..., None] * (~np.isin(comp, [RING, TOP]))[..., None]
            out = out * (1 - b) + bcol * b
            if level == 2:
                core_dk = (comp == CORE) & (np.maximum(np.abs(pdx), np.abs(pdy)) < R.T['body_a'] - 7)
                out = np.where(core_dk[..., None], np.array([52, 49, 45.]) * (1 + 1.5 * grain)[..., None], out)
            rk = rock[j, i] * (1 + 1.5 * grain)[..., None]
            return np.where((comp == DEBRIS)[..., None], rk, out)

        return H, C, slab2, dict(mats=mats)

    return damage


def coupling_damage(level, seed=40):
    """wear and breakage for the generic couplings (greys and browns only)."""
    def f(side, hc, cc):
        rng = np.random.default_rng(seed + 'NESW'.index(side) * 7 + level)
        S_crack, S_cmask, S_rough, S_soot, S_dust = (Sampler(rng, 8.0), Sampler(rng, 12.0), Sampler(rng, 1.2),
                                                     Sampler(rng, 5.0), Sampler(rng, 4.0))
        jag = gn(hc.shape, 1.8, rng)
        hc = hc.copy()
        neck, flange = np.isin(cc, [R.NECK, R.SILL]), cc == R.FLANGE
        if level == 1:
            grad = np.hypot(*np.gradient(hc, 1.0 / SS))
            band = ndimage.maximum_filter((grad > 2.0).astype(float), size=int(3.0 * SS)) * (hc > 0.5)
            chip = smoothstep(1.0, 1.5, gn(hc.shape, 2.2, rng)) * band
            hc = np.maximum(hc - 5.0 * chip, 0)
        elif level == 2:
            hc = np.where(neck, np.maximum(hc * 0.45 + 2.5 * jag, 0), hc)
            lim = 11.0 + 4.0 * jag + 5.0 * gn(hc.shape, 6.0, rng)          # the sleeve broken down to a jagged stump
            hc = np.where(flange, np.clip(np.minimum(hc, lim), 0, None), hc)
        heavy = level == 2

        def mats(alb, x, y, z, comp, top_like, grain, u, v):
            mine = np.isin(comp, [R.NECK, R.FLANGE, R.SILL])
            out = alb.copy()
            dust = smoothstep(0.6, 1.3, S_dust(u, v)) * 0.35 * mine
            out = out * (1 - dust[..., None]) + DUST * (1 + grain)[..., None] * dust[..., None]
            soot = smoothstep(0.3 if heavy else 0.8, 1.3, S_soot(u, v)) * (0.75 if heavy else 0.5) * mine
            out = out * (1 - soot[..., None]) + SOOT * soot[..., None]
            cn = S_crack(u, v) + 0.10 * S_rough(u, v)
            crack = (1 - smoothstep(0.015, 0.06, np.abs(cn))) * smoothstep(0.2, 0.6, S_cmask(u, v)) * mine
            out *= (1 - 0.6 * crack)[..., None]
            return out
        return hc, mats
    return f
