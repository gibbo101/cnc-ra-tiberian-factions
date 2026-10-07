"""Paint and damage for the dug-in Tick Tank.  TS's GTTICK draws no damage (its frames 0 and 1 are the same picture),
so the damaged state is mine, kept light, greys and browns only, on the part of the hull above the ground (its rear
third, standing up):
  - soot blotches (the rear plate on top, the south skirt, the hull tops and the ramps' back, by the pipes);
  - four shell holes (two in the south skirt, one in the south hull top, one in the rear plate): a black core, a
    scorched ring, a bright ragged rim of bare metal;
  - paint scraped off the south hull top's edge and streaks down the south skirt (bare steel);
  - the south skirt's first trim line shot away;
  - the front pipe of the twin pipes snapped, its front half lying on the ground south of the tank;
  - the south rear corner box knocked off, lying on the ground; a few steel fragments.
Both states: soil caked on the hull where it meets the ground, as it goes in.
The decals are fixed on the hull (written in TTNK.VXL's index space, posed with it)."""
import numpy as np
import hdv
import ttnk3hd as T
import fakeunit as F
from wnoise import noise

SOOT = np.array([34, 32, 30], np.float32)
CORE = np.array([16, 14, 13], np.float32)
SCORCH = np.array([56, 50, 44], np.float32)
METAL = np.array([152, 152, 154], np.float32)
MUD = np.array([66, 54, 42], np.float32)
MUD_DRY = np.array([96, 82, 64], np.float32)

HOLES = [((5.4, 0.0, 4.3), 0.95), ((9.4, 0.0, 2.7), 0.75), ((4.6, 2.1, None), 0.85), ((0.4, 3.0, 2.8), 0.8)]
SOOTS = [((0.8, 12.0, 4.0), 3.2, 0.9), ((3.6, 0.0, 5.2), 2.8, 0.9), ((4.4, 2.5, None), 3.0, 0.95),
         ((3.0, 9.2, 'hump'), 2.6, 0.85), ((8.6, 18.2, None), 2.8, 0.85), ((9.4, 0.0, 2.7), 2.0, 0.8),
         ((0.6, 3.0, 2.8), 2.0, 0.8), ((6.5, 19.0, None), 2.4, 0.7)]


def _z(c):
    x, y, z = c
    if z is None:
        z = T.top(x) + 0.05
    elif z == 'hump':
        z = T.ramp_top(x) if x < T.RAMP['x_front'] else T.top(x)
    return np.array([x, y, z], float)


def hull_items(V, items):
    """the damaged hull's parts (index space, before the pitch): the trim line, the pipe, the corner box."""
    out = []
    sx = V.sc[0]
    for it in items:
        n = it.name or ''
        if n in ('trim8_r', 'tail_box_r', 'pipe_cap_a', 'pipe_band12_a'):
            continue
        if n == 'pipe_a':
            y, pz = 16.75, (lambda x: T.top(x) + 0.7)
            out.append(hdv.cyl('pipe', V.p(7.6, y, pz(7.6)), V.p(11.4, y, pz(11.4)), 0.68 * sx, 'pipe_a'))
            # the jagged stump: a few slanted shards
            for k, (dx, dz, ln) in enumerate(((0.0, 0.25, 0.7), (0.0, -0.3, 0.45), (0.0, 0.0, 0.3))):
                a = V.p(11.3, y + 0.25 * (k - 1), pz(11.3) + dz)
                b = V.p(11.4 + ln, y + 0.3 * (k - 1), pz(11.4 + ln) + dz * 0.6)
                out.append(hdv.cyl('pipe', a, b, 0.22 * sx, 'pipe_a_shard%d' % k))
            out.append(hdv.cyl('scorched', V.p(11.32, y, pz(11.32)), V.p(11.42, y, pz(11.42)), 0.5 * sx, 'pipe_a_bore'))
            continue
        out.append(it)
    return out


def debris_items(V, G):
    """on the ground (unit frame), south of where the hull goes in (G: tickm.Ground): the corner box, the pipe's front
    half, steel fragments."""
    sx = V.sc[0]
    out = []
    rng = np.random.default_rng(31)
    cx = float(G.c[0]) if G.any else 0.0
    # the corner box, tipped over
    th, ph = np.radians(38.0), np.radians(16.0)
    Rz = np.array([[np.cos(th), -np.sin(th), 0], [np.sin(th), np.cos(th), 0], [0, 0, 1.0]])
    Rx = np.array([[1.0, 0, 0], [0, np.cos(ph), -np.sin(ph)], [0, np.sin(ph), np.cos(ph)]])
    R = Rz @ Rx
    h = np.array([0.65, 0.9, 0.48]) * sx
    c = np.array([cx - 9.6, -12.8, 0.62])
    pts = [c + R @ (h * np.array([a, b, d])) for a in (-1, 1) for b in (-1, 1) for d in (-1, 1)]
    out.append(hdv.hull('black', pts, 'debris_box', rnd=0.2))
    # the pipe's front half (11.4 .. 15.95), lying on the ground
    a = np.array([cx + 5.2, -15.0, 0.66]); d = np.array([np.cos(np.radians(-28)), np.sin(np.radians(-28)), 0.0])
    out.append(hdv.cyl('pipe', a, a + d * 3.95, 0.68 * sx, 'debris_pipe'))
    out.append(hdv.cyl('gun', a + d * 3.9, a + d * 4.5, 0.72 * sx, 'debris_pipe_cap'))
    out.append(hdv.cyl('pipe_band', a + d * 1.2, a + d * 1.6, 0.74 * sx, 'debris_pipe_band'))
    out.append(hdv.cyl('scorched', a - d * 0.02, a + d * 0.08, 0.5 * sx, 'debris_pipe_bore'))
    # steel fragments
    for k, (x, y) in enumerate(((-6.0, -13.4), (3.0, -15.6), (-11.5, -11.0), (9.5, -12.6), (-2.5, -16.2))):
        r0 = rng.uniform(0.45, 0.85)
        q = np.array([cx + x, y, 0.0]) + rng.normal(size=(7, 3)) * np.array([r0, r0 * 0.8, r0 * 0.35])
        q[:, 2] = np.abs(q[:, 2]) * 0.8 + 0.02
        q = np.vstack([q, [[cx + x, y, 0.0]]])
        out.append(hdv.hull('scrap' if k % 2 == 0 else 'black', q, 'debris_frag%d' % k, rnd=0.1))
    return out


def _hull_index(r, M, Mx):
    """every hit as TTNK.VXL index space (before the pose): xi, yi, zi."""
    Q = np.stack([r.x, r.y, r.z], -1) @ Mx          # world -> unit frame (Mx orthonormal: rows of Mx^T)
    R, Tt = M.pose.R, M.pose.T
    P = (Q - Tt) @ R                                  # undo the pose: R^T (q - T)
    return (P - F.MN) / F.SC


def _is(items, r, test):
    idx = [i for i, it in enumerate(items) if test(it.name or '')]
    return np.isin(np.where(r.hitmask, r.who, -1), idx)


def hull_part(n):
    return not n.startswith(('turret', 'berm', 'clod', 'debris', 'soil'))


def decal_fn(level):
    def apply(r, alb, emit, spec, house, M, Mx):
        I = _hull_index(r, M, Mx)
        xi, yi, zi = I[..., 0], I[..., 1], I[..., 2]
        hull = _is(M.items, r, hull_part) & r.hitmask
        tp = __import__('tickm').burial(M.t)
        wz = r.z
        # soil caked on the hull where it meets the berm, more on the nose (as it burrows)
        if tp > 0:
            n = noise(xi * 1.0 + 0.6 * zi, yi * 1.0 - 0.4 * zi, 0.8, 81) + 0.6 * noise(xi * 2.1, yi * 2.1 + zi, 0.4, 83)
            mud = np.clip((2.6 * tp - wz) / 0.5 + 0.55 * n, 0, 1) * hull
            mud = np.where(mud > 0.5, 1.0, 0.0) * hull
            dry = np.clip(noise(xi * 1.7 + zi, yi * 1.7, 0.5, 85) * 0.8 + 0.4, 0, 1)[..., None]
            c = MUD[None, None, :] * (1 - dry) + MUD_DRY[None, None, :] * dry
            m = mud > 0
            alb[m] = c[m] * (0.9 + 0.2 * (noise(xi, yi + zi, 0.3, 87)[m])[..., None])
            house[m] = 0.0
            spec[m, 0] = 0.06; spec[m, 1] = 8.0
            emit[m] = 0.0
        if not level:
            return
        g = noise(xi * 1.3 + zi, yi * 1.3 - zi, 0.7, 91)
        # soot: darkens paint and metal; on the house colour it comes in specks (a pixel is house colour or soot,
        # never darkened house colour), denser towards the middle
        fine = noise(xi * 7.0 + zi * 3.0, yi * 7.0 - zi * 2.0, 0.16, 99) * 0.5 + 0.5
        for c, rad, k in SOOTS:
            p = _z(c)
            d = np.sqrt((xi - p[0]) ** 2 + (yi - p[1]) ** 2 + (zi - p[2]) ** 2)
            s = np.clip(1 - d / rad + 0.3 * g, 0, 1) ** 0.7 * k * hull
            sm = (s > 0.02) & (house <= 0)
            alb[sm] = alb[sm] * (1 - 0.7 * s[sm, None]) + SOOT[None, :] * (0.7 * s[sm, None])
            spec[sm, 0] *= (1 - 0.7 * s[sm])
            off = (house > 0) & (s > 0.02) & (s * 1.25 > fine)
            alb[off] = SOOT[None, :] * (1.0 + 0.5 * (1 - s[off, None])) + 6.0
            house[off] = 0.0
            spec[off, 0] = 0.06
        # scraped paint: the south hull top's outer edge, streaks down the south skirt
        e1 = (yi < 0.75) & (zi > T.top(np.clip(xi, 2, 27)) - 0.75) & (xi > 3.0) & (xi < 10.5)
        s1 = (noise(xi * 2.6, zi * 3.0, 0.45, 93) > 0.35) & e1
        e2 = (yi < 0.08) & (xi > 6.0) & (xi < 11.5) & (zi > 1.2)
        st = np.abs(np.mod(xi * 0.9 + zi * 0.55, 1.6) - 0.8) < 0.1
        s2 = st & (noise(xi * 1.5, zi * 1.5, 0.6, 95) > 0.1) & e2
        sc = (s1 | s2) & hull
        alb[sc] = METAL[None, :] * (0.85 + 0.25 * (noise(xi, zi, 0.2, 97)[sc])[..., None])
        house[sc] = 0.0
        spec[sc, 0] = 0.5; spec[sc, 1] = 40.0
        # shell holes
        for c, rad in HOLES:
            p = _z(c)
            d = np.sqrt((xi - p[0]) ** 2 + (yi - p[1]) ** 2 + (zi - p[2]) ** 2)
            a = np.arctan2(zi - p[2], xi - p[0])
            jag = 0.07 * np.sin(a * 3 + p[0]) + 0.05 * np.sin(a * 7 + p[2]) + 0.12 * noise(xi * 4, zi * 4 + yi, 0.25, 98)
            rr = d / rad + jag
            rim = (rr < 1.0) & (rr >= 0.8) & hull
            ring = (rr < 0.8) & (rr >= 0.52) & hull
            core = (rr < 0.52) & hull
            alb[rim] = METAL[None, :] * 0.95
            alb[ring] = SCORCH[None, :]
            alb[core] = CORE[None, :]
            for m in (rim, ring, core):
                house[m] = 0.0
            spec[core | ring, 0] = 0.05
            spec[rim, 0] = 0.55; spec[rim, 1] = 44.0
    return apply
