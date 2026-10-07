"""
Damage for the Dropship Bay (GTDROP frame 1; RA has healthy and damaged only), as TS breaks it.  The broken shapes are
in gdrop.scene(level=1) (gdrop.DMG, and plug.DMG for the east block: TS draws the Upgrade Center's damage there); this
adds the soot, char and rubble:
  east block   (the Upgrade Center's) the roof's east half burnt fairly flat with bare beams across, the bevel and band
               broken along it, the nearer east antenna knocked off, two pipes snapped and a length bent out; soot
  house        its east roof slope burnt open over its south and middle part: char, bare rafters across; soot down the
               walls; the gable end and the ridge's north end standing
  ramp         broken through at its west middle: a dark hole, its edge bent down, chunks round it
  pad          B's north and south bars partly smashed (GTDROP_B's damaged half); scorch on the deck
Greys and browns only; placed in the building's own frame so both views match.
"""
import numpy as np
import gdrop as M, plug as PL, plugdamage as PD, gdropmat as MM, wnoise as WN
from walls2 import smoothstep
from weapdamage import Chunks

SOOT = PD.SOOT
CHAR = PD.CHAR
CHAR_D = PD.CHAR_D
BARE = PD.BARE
DUST = PD.DUST
DEEP = PD.DEEP


class BayChunks(Chunks):
    pass


def soot_field(x, y, p=None):
    """soot over both halves: the Upgrade Center's spots (moved into this frame; not its sockets') and the bay's."""
    ox, oy = M.OFF
    dm = M.PLUG_DMG
    s = np.zeros(np.shape(x), np.float32)
    hx, hy, rx, ry, _ = dm['hole']
    s = np.maximum(s, 0.85 * np.exp(-(((x - hx - ox) / (rx * 1.35)) ** 2 + ((y - hy - oy) / (ry * 1.5)) ** 2)))
    s = np.maximum(s, 0.7 * np.exp(-(((x - 20.0 - ox) / 40.0) ** 2 + ((y - 6.0 - oy) / 12.0) ** 2)))     # down the face
    s = np.maximum(s, 0.65 * np.exp(-(((x - 110.0 - ox) / 18.0) ** 2 + ((y + 50.0 - oy) / 34.0) ** 2)))  # the ramp, pipes
    # the house: over the burnt slope and down its east wall
    rc = M.DMG['roof']
    s = np.maximum(s, 0.8 * np.exp(-(((x - rc['c'][0]) / (rc['r'][0] * 1.5)) ** 2 + ((y - rc['c'][1]) / (rc['r'][1] * 1.3)) ** 2)))
    s = np.maximum(s, 0.5 * np.exp(-(((x + 104.0) / 14.0) ** 2 + ((y - 30.0) / 40.0) ** 2)))
    # the ramp's hole
    rp = M.DMG['ramp']
    s = np.maximum(s, 0.75 * np.exp(-(((x - rp['c'][0]) / (rp['r'][0] * 1.4)) ** 2 + ((y - rp['c'][1]) / (rp['r'][1] * 1.6)) ** 2)))
    # scorch on the deck by the pad's broken bars and between the house and the pit
    s = np.maximum(s, 0.45 * np.exp(-(((x - 70.0) / 26.0) ** 2 + ((y - 96.0) / 12.0) ** 2)))
    s = np.maximum(s, 0.4 * np.exp(-(((x - 60.0) / 22.0) ** 2 + ((y + 4.0) / 10.0) ** 2)))
    s = np.maximum(s, 0.35 * np.exp(-(((x + 90.0) / 20.0) ** 2 + ((y - 100.0) / 16.0) ** 2)))
    return s


def model(level, p=None):
    def f(X, Yy, **kw):
        q = M.P if p is None else p
        kw = dict(kw); kw['level'] = level
        sc = M.scene(X, Yy, p=q, **kw)
        if level < 1:
            return sc
        lay = kw.get('layout', 'ts')
        x, y = M.to_local(X, Yy, lay)
        H, C = sc.H.copy(), sc.C.copy()
        rock = np.zeros(H.shape + (3,), np.float32)
        ch = BayChunks(3150)
        ox, oy = M.OFF
        ch.scatter(7, (40.0 + ox, -42.0 + oy), (0, 34), (2.6, 5.0), ['tan', 'rust', 'steel'], [0.5, 0.3, 0.2], [])
        ch.scatter(3, (98.0 + ox, 58.0 + oy), (0, 10), (2.0, 4.0), ['tan', 'steel'], [0.5, 0.5], [])
        rp = M.DMG['ramp']
        ch.scatter(6, (rp['c'][0] - 6.0, rp['c'][1] + 22.0), (4, 26), (2.4, 4.6), ['steel', 'conc'], [0.5, 0.5], [])
        ch.scatter(4, (-96.0, 100.0), (0, 14), (2.2, 4.2), ['tan', 'steel'], [0.6, 0.4], [])
        Hb = np.where(H > 0, H, 0.0)
        H, C, rock = ch.apply(x, y, H, C, rock, base=Hb)
        sc.H, sc.C = H.astype(np.float32), C.astype(np.int16)
        sc.extra.update(soot=soot_field(x, y, q), rock=rock)
        return sc
    return f


def mats(r, alb, level, p=None):
    if level < 1:
        return alb
    q = M.P if p is None else p
    # the east block: the Upgrade Center's damage colours (char, beams, chips, soot) in plug's own frame
    out = PD.mats(MM.Shifted(r), alb, level, p=q['plug'])
    x, y = M.to_local(r.x, r.y, r.mk.get('layout', 'ts'))
    z, comp = r.z, r.comp
    top = r.nz > 0.75
    grain = WN.noise(x, y + z, 1.2, 3151) * 0.05
    g1 = (1 + grain)[..., None]
    house = np.isin(comp, list(M.HOUSE))
    s = r.field('soot')
    # the bay's own parts: chips where sooted, soot (house green only lightly)
    body = np.isin(comp, [M.WBODY, M.WCROWN, M.RAIL, M.NWALL, M.RAMP2])
    chip = smoothstep(0.62, 0.9, WN.noise(x * 1.3, y * 1.3 + z, 2.6, 3153)) * body * 0.8 * smoothstep(0.1, 0.4, s)
    out = out * (1 - chip[..., None]) + BARE * g1 * chip[..., None]
    mine = comp >= 80
    soot = smoothstep(0.15, 0.7, np.clip(s * (0.65 + 0.35 * WN.noise(x, y + z, 6, 3154)), 0, 1)) * 0.85
    soot = soot * np.where(house, 0.22, 1.0) * mine
    out = out * (1 - soot[..., None]) + SOOT * soot[..., None]
    # the house's burnt slope: char, darker in its depths; its rafters bare steel (plug.BEAM, coloured by PD.mats)
    w = q['west']
    ze = w['z'] + w['trim']
    bt = (comp == PL.DEB_BURNT) & (x < -90.0)
    deep = smoothstep(ze + M.DMG['roof']['floor'] + 8.0, ze + M.DMG['roof']['floor'] - 2.0, z)
    cc = CHAR * (1 - 0.45 * deep)[..., None] + CHAR_D * (0.45 * deep)[..., None]
    glint = smoothstep(0.75, 0.95, WN.noise(x, y, 2.0, 3155))
    out = np.where(bt[..., None], cc * (1 + 0.6 * glint)[..., None] * g1, out)
    # the ramp's hole: dark inside
    out = np.where(((comp == PL.DEB_IN) & (y > 100.0))[..., None], DEEP * g1, out)
    rock = r.field('rock')
    if rock.ndim == 3:
        out = np.where((comp == PL.DEBRIS)[..., None], rock * (1 + 1.5 * grain)[..., None], out)
    return out
