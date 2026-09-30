"""RA's second state for the turrets: damaged. Greys and browns only - soot, scorch, cracks, dust and a few
chips knocked out of the edges; the house-colour parts keep their colour (only darkened). Everything is laid
out in the turret's own frame, so it turns with it."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from damage import Sampler
from walls2 import smoothstep
import tsdf as T

SOOT = np.array([30, 29, 28.])
DUST = np.array([120, 110, 92.])
FRESH = np.array([200, 190, 170.])


def chips(points, seed=5, r=(2.2, 3.6)):
    """spheres cut out of the model at the given local points (put them on edges and corners)."""
    rng = np.random.default_rng(seed)
    return [dict(T.sph(c, rng.uniform(*r)), sub=True, comp_in=None) for c in points]


class Wear:
    def __init__(self, seed=11, scorch=((0.0, 0.0, 20.0, 16.0),)):
        rng = np.random.default_rng(seed)
        self.S_soot, self.S_crack, self.S_cmask = Sampler(rng, 5.0), Sampler(rng, 8.0), Sampler(rng, 12.0)
        self.S_dust, self.S_rough = Sampler(rng, 4.0), Sampler(rng, 1.2)
        self.scorch = scorch                              # (f, r, z, radius) blast marks

    def __call__(self, alb, comp, Lp, nl, u, v, is_green, near_cut):
        f, r, z = Lp[:, 0], Lp[:, 1], Lp[:, 2]
        out = alb.copy()
        dust = smoothstep(0.7, 1.4, self.S_dust(u, v)) * np.where(nl[:, 2] > 0.75, 0.45, 0.25)
        s = np.zeros(len(f))
        for (sf, sr, sz, sR) in self.scorch:
            s = np.maximum(s, np.exp(-(((f - sf) ** 2 + (r - sr) ** 2 + (z - sz) ** 2) / sR ** 2)))
        soot = smoothstep(0.2, 0.8, np.clip(s * (0.6 + 0.4 * self.S_soot(u, v)), 0, 1)) * 0.85
        soot = np.maximum(soot, smoothstep(0.55, 1.3, self.S_soot(u * 1.3 + 40, v * 1.3)) * 0.6)
        cn = self.S_crack(u, v) + 0.1 * self.S_rough(u, v)
        crack = (1 - smoothstep(0.02, 0.07, np.abs(cn))) * smoothstep(0.15, 0.55, self.S_cmask(u, v))
        g = is_green[:, None]
        # house colour: only darkened, so it stays pure green for the recolouring
        dk = (1 - 0.55 * soot) * (1 - 0.5 * crack)
        green_out = alb * dk[:, None]
        o = out * (1 - dust[:, None]) + DUST * dust[:, None]
        o = o * (1 - soot[:, None]) + SOOT * soot[:, None]
        o = o * (1 - 0.6 * crack)[:, None]
        brk = near_cut[:, None] * 0.85                   # fresh breaks where a chip was knocked out
        o = o * (1 - brk) + FRESH * np.clip(0.84 + 0.1 * self.S_rough(u, v), 0.6, 1.0)[:, None] * brk
        return np.where(g, green_out, o)
