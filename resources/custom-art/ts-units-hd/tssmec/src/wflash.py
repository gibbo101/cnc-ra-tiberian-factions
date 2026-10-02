"""
wflash.py - the Wolverine's muzzle flash in HD, built like TS's: a small star burst at each muzzle (a white-hot
core, yellow round it, orange rays with red tips), on firing steps 0 and 2 only, the two steps' bursts shaped a
little differently (TS's differ the same way).  Drawn at the muzzle's place on the canvas, depth-tested against
the unit (hidden where the unit is in front of the muzzle), plus the flash's light on the nearby surfaces.

Size: TS's bursts are about 7-9 TS px across (core 1-2 px); here x 6.4.
"""
import numpy as np

WHITE = np.array([255, 255, 240.]); YELLOW = np.array([255, 240, 40.]); ORANGE = np.array([255, 150, 10.])
RED = np.array([236, 30, 10.])


def burst(SX, SY, cx, cy, axis, variant, scale=6.4, px_scale=1.0):
    """colour (H, W, 3) and alpha (H, W) of one burst on the canvas grid (SX, SY), centred (cx, cy); axis = the
    barrel's direction on screen (unit vector): the rays along it reach furthest, as TS's do."""
    rng = np.random.RandomState(17 + 31 * variant)
    dx = SX - cx; dy = SY - cy
    r = np.hypot(dx, dy) / scale                       # in TS px
    ang = np.arctan2(dy, dx)
    a0 = np.arctan2(axis[1], axis[0])
    # rays: 8 round the burst (TS: horizontal, vertical and the diagonals), the pair along the barrel longest
    n = 8
    rot = rng.uniform(-0.18, 0.18)
    reach = np.zeros_like(r)
    for i in range(n):
        th = a0 + rot + 2 * np.pi * i / n
        along = abs(np.cos(2 * np.pi * i / n))          # 1 along the barrel, 0 across
        L = (3.0 + 2.2 * along ** 2) * rng.uniform(0.85, 1.15)
        if variant == 1 and i == 0:
            L *= 1.45                                   # TS's second burst throws one long streak forward
        w = 0.62 * (1.0 - 0.3 * along)                  # half width of the ray at its root (TS px)
        d = np.angle(np.exp(1j * (ang - th)))
        perp = np.abs(np.sin(d)) * r
        fwd = np.cos(d) * r
        on = (fwd > 0) & (fwd < L) & (perp < w * (1 - fwd / L) + 0.08)
        reach = np.maximum(reach, np.where(on, 1 - fwd / L, 0.0))
    core = np.clip(1.3 - r / 1.45, 0, 1)                  # the round white-yellow heart (~3 TS px across, as TS's)
    heat = np.maximum(core, reach * 0.95)
    # colour ramp: red tips -> orange -> yellow -> white core
    t = np.clip(heat, 0, 1)[..., None]
    col = np.where(t > 0.75, YELLOW + (WHITE - YELLOW) * ((t - 0.75) / 0.25),
                   np.where(t > 0.4, ORANGE + (YELLOW - ORANGE) * ((t - 0.4) / 0.35),
                            RED + (ORANGE - RED) * (t / 0.4)))
    alpha = np.clip(np.where(heat > 0, 0.7 + 0.3 * np.sqrt(np.clip(heat, 0, 1)), 0.0), 0, 1)
    alpha = np.where(heat > 0.02, alpha, 0.0)
    return col, alpha


def flash_light(P, N, muzzles, radius=4.0, strength=150.0):
    """the flash's light on the unit (emission to add): surfaces within `radius` TS units of a muzzle, facing it."""
    out = np.zeros(P.shape[:-1] + (3,), np.float32)
    for m in muzzles:
        d = np.asarray(m, float) - P
        dist = np.linalg.norm(d, axis=-1) + 1e-6
        facing = np.clip((N * d).sum(-1) / dist, 0, 1)
        fall = np.clip(1 - dist / radius, 0, 1) ** 2
        out += (strength * facing * fall)[..., None] * np.array([1.0, 0.78, 0.36])
    return out
