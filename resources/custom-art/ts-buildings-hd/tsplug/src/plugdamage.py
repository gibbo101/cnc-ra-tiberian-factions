"""
Damage for the Upgrade Center (TS GTPLUG frame 1; RA has healthy and damaged only), as TS breaks it.  The broken shapes
are built into plug.scene(level=1) (plug.DMG); this adds the soot, char and rubble:
  roof     caved in over its east half: a burnt-out hole (char black-brown, TS's dark red-brown read as burnt brown),
           bare grey roof beams across it, the bevel and band broken along it, soot round it
  antennas the two east ones knocked off, the tallest bent a little (GTPLUG_B's lights move with it, as TS's do)
  pipes    two snapped short, the third bent over, a broken length leaning on the ramp; soot on the ramp
  slope    a pane knocked in (dark inside), soot round it, the house green only lightly
  sockets  the west collar's east side broken off, scorched; the east socket's plate scorched brown
  deck     scorch patches, a few chunks of tan plate and steel on it
Greys and browns only; placed in the building's own frame so both views match.
"""
import numpy as np
import plug as M, wnoise as WN
from walls2 import smoothstep
from weapdamage import Chunks

SOOT = np.array([30, 29, 28.])
CHAR = np.array([98, 42, 24.])             # burnt dark red-brown, as TS's (68,20,4 / 80,32,16 / 52,4,0); v1 84,50,38
CHAR_D = np.array([44, 18, 10.])            # (v1 34,24,20)
BARE = np.array([150, 148, 142.])
DUST = np.array([116, 106, 84.])
DEEP = np.array([26, 26, 28.])
SCORCH = np.array([74, 66, 58.])          # the east socket's plate: scorched dark grey-brown


class PlugChunks(Chunks):
    pass


def model(level, p=None):
    def f(X, Yy, **kw):
        q = M.P if p is None else p
        kw = dict(kw); kw['level'] = level
        sc = M.scene(X, Yy, p=q, **kw)
        if level < 1:
            return sc
        lay = kw.get('layout', 'ts')
        x, y = M.to_local(X, Yy, lay)
        dm = M.DMG
        soot = np.zeros(X.shape, np.float32)
        hx, hy, rx, ry, _ = dm['hole']
        soot = np.maximum(soot, 0.85 * np.exp(-(((x - hx) / (rx * 1.35)) ** 2 + ((y - hy) / (ry * 1.5)) ** 2)))
        soot = np.maximum(soot, 0.7 * np.exp(-(((x - 20.0) / 40.0) ** 2 + ((y - 6.0) / 12.0) ** 2)))     # down the face
        px_, py_, _, _ = dm['pane']
        soot = np.maximum(soot, 0.6 * np.exp(-((x - px_) ** 2 + (y - py_) ** 2) / 16.0 ** 2))
        soot = np.maximum(soot, 0.65 * np.exp(-(((x - 110.0) / 18.0) ** 2 + ((y + 50.0) / 34.0) ** 2)))  # the ramp, pipes
        cx, cy = q['sockets']['c'][0]
        soot = np.maximum(soot, 0.7 * np.exp(-((x - cx - 34.0) ** 2 + (y - cy - 10.0) ** 2) / 22.0 ** 2))
        cx2, cy2 = q['sockets']['c'][1]
        soot = np.maximum(soot, 0.45 * np.exp(-((x - cx2) ** 2 + (y - cy2) ** 2) / 26.0 ** 2))
        soot = np.maximum(soot, 0.5 * np.exp(-(((x + 10.0) / 30.0) ** 2 + ((y - 160.0) / 12.0) ** 2)))   # the front step
        # rubble on the deck: tan plate and steel off the roof, green off the collar
        H, C = sc.H.copy(), sc.C.copy()
        rock = np.zeros(H.shape + (3,), np.float32)
        ch = PlugChunks(2150)
        ch.scatter(4, (-30.0, 60.0), (0, 12), (2.2, 4.4), ['tan', 'steel'], [0.6, 0.4], [])
        ch.scatter(7, (40.0, -42.0), (0, 34), (2.6, 5.0), ['tan', 'rust', 'steel'], [0.5, 0.3, 0.2], [])
        ch.scatter(3, (-20.0, 132.0), (0, 10), (2.0, 3.8), ['green', 'steel'], [0.5, 0.5], [])
        ch.scatter(3, (98.0, 58.0), (0, 10), (2.0, 4.0), ['tan', 'steel'], [0.5, 0.5], [])
        Hb = np.where(H > 0, H, 0.0)
        H, C, rock = ch.apply(x, y, H, C, rock, base=Hb)
        sc.H, sc.C = H.astype(np.float32), C.astype(np.int16)
        sc.extra.update(soot=soot, rock=rock)
        return sc
    return f


def mats(r, alb, level, p=None):
    if level < 1:
        return alb
    lay = r.mk.get('layout', 'ts')
    x, y = M.to_local(r.x, r.y, lay)
    z, comp = r.z, r.comp
    top = r.nz > 0.75
    out = alb.copy()
    grain = WN.noise(x, y + z, 1.2, 2151) * 0.05
    g1 = (1 + grain)[..., None]
    house = np.isin(comp, list(M.HOUSE))
    dust = smoothstep(0.3, 1.3, WN.noise(x, y, 14, 2152)) * np.where(top, 0.3, 0.15) * ~house
    out = out * (1 - dust[..., None]) + DUST * g1 * dust[..., None]
    s = r.field('soot')
    # chips off the block's and ramp's edges where it's sooted: bare grey under the paint
    body = np.isin(comp, [M.BLOCK, M.LIP, M.FACE, M.LEDGE, M.FRONT, M.RAMP, M.STEP])
    chip = smoothstep(0.62, 0.9, WN.noise(x * 1.3, y * 1.3 + z, 2.6, 2153)) * body * 0.8 * smoothstep(0.1, 0.4, s)
    out = out * (1 - chip[..., None]) + BARE * g1 * chip[..., None]
    soot = smoothstep(0.15, 0.7, np.clip(s * (0.65 + 0.35 * WN.noise(x, y + z, 6, 2154)), 0, 1)) * 0.85
    soot = soot * np.where(house, 0.22, 1.0)
    out = out * (1 - soot[..., None]) + SOOT * soot[..., None]
    # the burnt-out roof: char, darker in its depths, glints of burnt metal
    bt = comp == M.DEB_BURNT
    deep = smoothstep(M.DMG['floor'] + 10.0, M.DMG['floor'], z)
    cc = CHAR * (1 - 0.45 * deep)[..., None] + CHAR_D * (0.45 * deep)[..., None]
    glint = smoothstep(0.75, 0.95, WN.noise(x, y, 2.0, 2155))
    cc = cc * (1 + 0.6 * glint)[..., None]
    out = np.where(bt[..., None], cc * g1, out)
    # the block's walls inside the hole: charred
    hx, hy, rx, ry, _ = M.DMG['hole']
    inside = (np.abs(r.nz) < 0.5) & (comp == M.BLOCK) & (((x - hx) / (rx + 6)) ** 2 + ((y - hy) / (ry + 6)) ** 2 < 1)
    out = np.where(inside[..., None], CHAR * 0.8 * g1, out)
    # the knocked-in pane: dark inside
    out = np.where((comp == M.DEB_IN)[..., None], DEEP * g1, out)
    # beams: bare steel, sooted
    out = np.where((comp == M.BEAM)[..., None], BARE * 0.8 * g1, out)
    # the east socket's plate scorched brown
    cx2, cy2 = M.P['sockets']['c'][1]
    sp = (comp == M.PLATE) & (np.hypot(x - cx2, y - cy2) < 40)
    scor = smoothstep(0.0, 1.0, WN.noise(x, y, 8.0, 2156) * 0.5 + 0.7)
    out = np.where(sp[..., None], out * (1 - 0.55 * scor[..., None]) + SCORCH * (0.55 * scor[..., None]), out)
    rock = r.field('rock')
    if rock.ndim == 3:
        out = np.where((comp == M.DEBRIS)[..., None], rock * (1 + 1.5 * grain)[..., None], out)
    return out
