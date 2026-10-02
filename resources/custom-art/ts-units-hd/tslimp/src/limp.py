"""
limp.py - the Limpet Drone (Firestorm [LIMPET]) as convex parts, a solid of revolution about its upright axis (TS draws
one shape, no facings): a dark nub and a grey cap on top, the house-colour dome, the grey band round its waist with its
two dark lenses facing the camera, the house-colour cone below, and the light on the dome's front.

Frame: x east, y south, z up; units TS px; origin on the drone's axis at the cone's tip (it hovers: the tip is HOVER
over the ground).
"""
import numpy as np
import rc

NUB, CAP, DOME, BAND, CONE, LENS, LIGHT, LAMP = 501, 502, 503, 504, 505, 506, 507, 508
# fitting classes: 1 house, 2 light grey, 5 dark
CLASS = {NUB: 5, CAP: 2, DOME: 1, BAND: 2, CONE: 1, LENS: 5, LIGHT: 5, LAMP: 2}

P0 = dict(cr=4.0, ch=4.5,            # the cone: its top radius and its height (the tip at z 0)
          br=5.0, bh=2.2,            # the band: radius, height
          dr=5.0, dh=5.5,            # the dome: radius at its base, height above the band
          kr=3.2, kh=1.0,            # the cap: radius, height
          nr=1.4, nh=1.2,            # the nub
          la=37.0, lz=0.5, lr=0.8,   # the lenses: angle either side of the front, height up the band, radius
          tr=0.5, dz=-2.0)           # the cone's tip radius; the dome's foot against the band's top (below: into it)


N_SIDES = 28


def frustum(z0, r0, z1, r1, comp, name):
    """a cone frustum from radius r0 at z0 down/up to r1 at z1, as N_SIDES planes (its shading is rounded over them)."""
    cons = [rc.Plane(np.array([0, 0, 1.0]), max(z0, z1)), rc.Plane(np.array([0, 0, -1.0]), -min(z0, z1))]
    dz = z1 - z0; dr = r1 - r0
    for i in range(N_SIDES):
        a = 2 * np.pi * (i + 0.5) / N_SIDES
        e = np.array([np.cos(a), np.sin(a), 0.0])
        # the side through (r0 e, z0) and (r1 e, z1): normal (dz e - dr z)/|.|, pointing out
        n = dz * e - dr * np.array([0, 0, 1.0])
        if dz < 0:
            n = -n
        n = n / np.linalg.norm(n)
        cons.append(rc.Plane(n, n @ (r0 * e + np.array([0, 0, z0]))))
    c = np.array([0, 0, (z0 + z1) / 2])
    return rc.Part(cons, comp, name, sphere=(c, float(np.hypot(max(r0, r1), abs(dz) / 2)) + 1e-3))


def parts(P):
    out = []
    z0 = P['ch']                                   # the cone's top = the band's foot
    # the cone: a straight taper from the band down to its tip (TS: 8, 8, 6, 4, 2 px wide)
    out.append(frustum(z0, P['cr'], 0.0, P.get('tr', 0.5), CONE, 'cone'))
    # the band
    out.append(rc.cylinder((0, 0, z0), (0, 0, z0 + P['bh']), P['br'], BAND, 'band'))
    # the dome: an egg over the band (TS: widest across its middle, narrowing to the cap and down into the band)
    zb = z0 + P['bh']
    zc = zb + P.get('dz', 0.0) + P['dh']
    c = np.array([0, 0, zc])
    out.append(rc.Part([rc.Ellip(c, np.eye(3), np.array([P['dr'], P['dr'], P['dh']])),
                        rc.Plane(np.array([0, 0, -1.0]), -(zb - 0.05))], DOME, 'dome',
                       sphere=(c, max(P['dr'], P['dh']) + 1e-3)))
    zt = zc + P['dh']
    # the cap and the nub on the dome's top (the cap sits into the dome)
    zc = zt - 0.35 * P['dh'] * (P['kr'] / P['dr']) ** 2 * 2
    out.append(rc.cylinder((0, 0, zc), (0, 0, zt + P['kh']), P['kr'], CAP, 'cap'))
    out.append(rc.cylinder((0, 0, zt + P['kh'] - 0.1), (0, 0, zt + P['kh'] + P['nh']), P['nr'], NUB, 'nub'))
    # the lenses: two short dark cylinders set into the band, la degrees either side of its front (south)
    for s in (-1.0, 1.0):
        a = np.deg2rad(s * P['la'])
        d = np.array([np.sin(a), np.cos(a), 0.0])
        p = np.array([0, 0, z0 + P['lz'] * P['bh']]) + d * (P['br'] - 0.25)
        out.append(rc.cylinder(p, p + d * 0.5, P['lr'], LENS, 'lens'))
        if P.get('lamps', 0) > 0.5:
            # TS draws a white pixel on each lens' left (columns 44 and 50 against the lenses' 45 and 51)
            a2 = np.deg2rad(s * P['la'] - P.get('lamp_da', 15.0))
            d2 = np.array([np.sin(a2), np.cos(a2), 0.0])
            p2 = np.array([0, 0, z0 + P['lz'] * P['bh'] + 0.15]) + d2 * (P['br'] - 0.2)
            out.append(rc.cylinder(p2, p2 + d2 * 0.4, 0.42, LAMP, 'lamp'))
    return out


def light_points(P):
    """the light's two halves on the dome's front, just over the band (TS's pixels (45, 23) and (46, 23)): their
    centres, in the drone's frame."""
    zb = P['ch'] + P['bh']
    zc = zb + P.get('dz', 0.0) + P['dh']
    z = zb + 1.9                                    # TS: two rows over the band (row 23 against the band's 25)
    r = P['dr'] * np.sqrt(max(1 - ((z - zc) / P['dh']) ** 2, 0.0))
    out = []
    for dx in (-2.5, -1.5):                         # TS's light: columns 45 and 46, the axis between 47 and 48
        a = np.arcsin(np.clip(dx / r, -1, 1))
        out.append(np.array([r * np.sin(a), r * np.cos(a), z]))
    return out
