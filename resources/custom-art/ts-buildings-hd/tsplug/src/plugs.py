"""
The Upgrade Center's three plugs (TS GTPLUG_D / _E / _F; TSPODS / TSSEEK / TSPION in the mod), read from TS's overlay
frames where TS draws them standing in the east socket (the first plug's: the right-hand one), redrawn to read well at
HD (TS's pixels are rough), keeping TS's layout, size and colours.  Each is built round the socket's centre in the
building's own frame (u east, v south, w up from the socket's plate) and added to the building's scene by
plug.scene(plugs=...).  In TS's view a = (u - v) / sqrt 2 runs to the screen's right, b = (u + v) / sqrt 2 to the camera.
  D  Drop Pod Node      the beacon that calls the drop pods down: an armoured casing (chamfered corners, a cap), two
                        beacon lights on top (a small one back left, the big one front right), the ochre space-uplink
                        antenna out on its left side on a bracket, a house-green panel under it, a pump block with pipes
                        low on its front
  E  Seeker Control     the Hunter-Seeker's control lab: a pot-bellied round lab (a dark lower half, an ochre band
                        round its widest, a khaki shoulder), a small dome in a black ring on top, two thick dark
                        antennas; a camera with a big round lens low on its front and an ear muff with a grille on each
                        side; it turns the camera out towards you, blinks it and turns back (GTPLUG_E's 15 frames)
  F  Ion Cannon Uplink  a dark plinth in the socket carrying a round platform low down with railings round its edge
                        (posts and a top rail), a slim pole up through the middle (two black collars) to a wide platform
                        at the top carrying the dish's mount: a turntable, the machinery housing on it and a rectangular
                        satellite dish held in front of the housing by a fork and a hub; the mount turns the dish towards
                        you and it tilts up and rises a little over GTPLUG_F's 15 frames
All three stand on a grey flange in the socket.
"""
import numpy as np
from radr import rod_interval, inbox

# component ids (50+; plug.py uses 1..42)
(PG_FLANGE, PG_BODY, PG_CAP, PG_HATCH, PG_GREEN, PG_LAMP, PG_MACH, PG_DARK, PG_DOME, PG_ANT, PG_EYE, PG_EYEH,
 PG_TOWER, PG_RIB, PG_LEG, PG_NECK, PG_HEAD, PG_DISH, PG_DISHB, PG_EBODY, PG_EBAND, PG_FBAND, PG_FFOOT, PG_LAMPB,
 PG_PIPE, PG_FEED, PG_ESKIRT, PG_EPLATE, PG_FPLAT) = range(50, 79)
PG_HOUSE = {PG_GREEN}
PG_ALL = set(range(50, 79))
S2 = np.sqrt(0.5)

Q = dict(
    flange=dict(r=31.0, h=5.0),
    # D: the casing (half sizes along u, v; chamfer of its vertical edges; height; the cap), the two lights (a, b, w,
    # radius), the uplink antenna (a dish on a bracket off the casing's south-west side), the green panel, the pump
    D=dict(half=(24.0, 24.0), cham=8.0, h=72.0, round=10.0, cap=dict(inset=7.0, h=4.0),
           lights=((-15.0, -6.0, 3.6), (8.0, 14.0, 6.0)),
           ant=dict(at=(-28.0, 28.0), w=75.0, R=13.5, az=135.0, el=42.0, mast=(-17.0, 17.0, 60.0)),
           green=dict(u=(-14.0, -2.0), w=(38.0, 60.0)),
           pump=dict(u=(-16.0, 10.0), out=5.0, w=(5.0, 34.0), pipes=(14.0, 25.0), pipe_r=2.2)),
    # E (read from GTPLUG_E in TS's camera): a pot-bellied round lab, its profile (w, r) going up (the dark lower half,
    # the ochre band round its widest, the khaki shoulder), a black ring round its top, a low dome; two thick antennas;
    # the camera (a short fat barrel, a hood, a big round lens) low on its front and an ear muff with a grille on each
    # side, all turning with the lab
    E=dict(prof=((3.0, 34.0), (5.0, 36.5), (9.0, 37.5), (14.0, 39.5), (19.0, 41.5), (23.0, 42.5), (31.0, 42.5),
                 (36.0, 41.0), (41.0, 38.5), (46.0, 35.5), (50.0, 32.0), (54.0, 28.5), (57.0, 27.0), (62.5, 26.0),
                 (63.5, 24.5)),
           lower=23.0, band=(23.0, 41.0), ring=dict(r=20.0, w=(61.5, 64.8)), dome=dict(r=18.5, w=(63.5, 71.5)),
           ants=((-21.0, 3.0, 100.0), (14.7, -9.3, 97.0)), ant_r=3.0,
           scope=dict(base=102.0, w=22.0, r=9.5, r0=34.0, r1=46.5, hood=11.0, lens=8.5),
           muffs=dict(w=23.0, r=10.0, r0=34.0, r1=45.5, rim=1.8)),
    # F (read from GTPLUG_F): a dark plinth in the socket carrying a round platform low down, railings round the
    # platform's edge (posts, a mid and a top rail), a slim pole up through the middle to a wide platform at the top
    # that carries the machinery box (to the back right) and the rectangular dish, which turns towards you and rises a
    # little over GTPLUG_F's 15 frames
    F=dict(flange=34.0,
           plinth=dict(r=33.0, w=(4.0, 36.0), ring=(34.2, 22.0, 26.0)),
           deck=dict(r=40.0, w=(35.0, 39.5)),
           rail=dict(n=16, r=38.5, w=(39.0, 61.5), post=1.7, top=(59.0, 62.5), mid=None, hw=1.8),
           pole=dict(r=15.0, w=(39.0, 119.0), collars=((16.4, 77.0, 81.0), (16.4, 99.0, 103.0)), foot=(18.0, 39.0, 44.0)),
           yoke=dict(r=31.0, w=(118.0, 123.0)),
           # the dish's mount on the top platform: a turntable; on it the housing (the machinery box), turning with the
           # dish; the dish held in front of it by a fork (an arm to each side of the dish's axle) and a hub
           mount=dict(ped=(13.0, 123.0, 129.5), house=dict(back=-26.0, front=2.0, half=13.5, w=(129.0, 150.0)),
                      arm_r=2.4, hub_r=4.0),
           dish=dict(hw=24.5, hh=17.5, t=1.8, az=(115.0, 55.0), el=(40.0, 60.0), R=24.0, wc=(143.0, 165.0),
                     feed=13.0)),
)


def lathe(rr, prof):
    """the vertical interval of a surface of revolution with profile ((w, r), ..) going up, r rising to a maximum then
    falling: (lo, hi, mask) at radius rr."""
    w = np.array([p[0] for p in prof]); r = np.array([p[1] for p in prof])
    k = int(np.argmax(r))
    rmax = r[k]
    wr, rr_r = w[:k + 1], r[:k + 1]
    wf, rf = w[k:], r[k:]
    lo = np.where(rr <= rr_r[0], wr[0], np.interp(rr, rr_r, wr))
    hi = np.where(rr <= rf[-1], wf[-1], np.interp(rr, rf[::-1], wf[::-1]))
    return lo, hi, rr <= rmax


def obox_interval(x, y, C, E, h):
    """an oriented box (centre C, unit axes E[0..2], half sizes h) over the ground: (lo, hi, mask) of z."""
    lo = np.full(x.shape, -1e9); hi = np.full(x.shape, 1e9); ok = np.ones(x.shape, bool)
    for i in range(3):
        e = np.asarray(E[i], float)
        base = x * e[0] + y * e[1] - float(np.dot(C, e))
        if abs(e[2]) < 1e-9:
            ok &= np.abs(base) <= h[i]
        else:
            z1 = (-h[i] - base) / e[2]; z2 = (h[i] - base) / e[2]
            lo = np.maximum(lo, np.minimum(z1, z2)); hi = np.minimum(hi, np.maximum(z1, z2))
    ok &= hi > lo
    return np.where(ok, lo, 0.0), np.where(ok, hi, 0.0), ok


def view_turn(layout, to_local):
    """degrees to turn the plugs by in a layout so the camera sees them as in TS's view (TS: from the south-east; on a
    turned RA grid the camera looks from another side of the building)."""
    if layout == 'ts':
        return 0.0
    cx_, cy_ = to_local(np.array(0.0), np.array(1.0), layout)       # towards the RA camera, in the building's frame
    return float(np.degrees(np.arctan2(float(cy_), float(cx_)))) - 45.0


def plug_frame(u, v, turn_deg):
    """building-frame (u, v) round a socket -> the plug's own frame (the plug turned by turn_deg)."""
    if not turn_deg:
        return u, v
    c, s = np.cos(np.radians(turn_deg)), np.sin(np.radians(turn_deg))
    return u * c + v * s, -u * s + v * c


def ab(u, v):
    """TS view axes: a to the screen's right (north-east), b to the camera (south-east)."""
    return (u - v) * S2, (u + v) * S2


def uv(a, b):
    return (a + b) * S2, (b - a) * S2


def dish_axes(az_deg, el_deg):
    """a panel facing azimuth az (degrees from east towards south) at elevation el: (normal, across, up-the-panel)."""
    a, e = np.radians(az_deg), np.radians(el_deg)
    n = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    across = np.array([-np.sin(a), np.cos(a), 0.0])
    up = np.cross(n, across); up = up / np.linalg.norm(up)
    if up[2] < 0:
        up = -up
    return n, across, up


def f_dish(t, q=None):
    """GTPLUG_F frame t: the dish's centre (u, v, w from the plate), its axes (normal, across, up): over TS's 15 frames it
    turns from facing south-south-west to facing you (south-east), tilting up a little and rising (read from TS's
    frames: its white face moves right and up and grows). It sits in front of its mount's turntable, turning with it."""
    ds = (Q if q is None else q)['F']['dish']
    k = float(np.clip(t / 14.0, 0, 1))
    el = ds['el'][0] + (ds['el'][1] - ds['el'][0]) * k
    az = ds['az'][0] + (ds['az'][1] - ds['az'][0]) * k
    n, acr, up = dish_axes(az, el)
    a = np.radians(az)
    C = np.array([ds['R'] * np.cos(a), ds['R'] * np.sin(a), ds['wc'][0] + (ds['wc'][1] - ds['wc'][0]) * k])
    return C, n, acr, up


def e_turn(t):
    """GTPLUG_E frame t: the lab's turn (degrees) and the lens's light (0..1), read from TS's frames (the lens's and the
    antennas' px): the camera faces south-south-west at 0, swings out towards you (1-2), holds there blinking (2-10:
    bright, half, off, half), swings back (11-13) and on past its start (14) before the loop comes round to 0."""
    t = int(t) % 15
    turn = {0: 0.0, 1: -16.0, 11: -19.0, 12: -7.0, 13: 4.0, 14: 22.0}.get(t, -26.0)
    blink = {2: 1.0, 3: 0.5, 4: 0.0, 5: 0.5, 6: 1.0, 7: 0.5, 8: 0.0, 9: 0.5, 10: 1.0}.get(t, 1.0)
    return turn, blink


def add(kind, u, v, put, A, t=0.0, q=None, base_w=0.0):
    """add plug `kind` ('D', 'E', 'F') round the socket centre; u, v local to it; heights from base_w (the plate).
    A(name) gives the slab accumulator for a part (each part its own, so touching parts don't merge)."""
    q = Q if q is None else q
    W = lambda w: base_w + w
    fl = q['flange']
    rr = np.hypot(u, v)
    fr = q['F']['flange'] if kind == 'F' else fl['r']
    put(np.where(rr <= fr, W(fl['h']), 0.0), PG_FLANGE, rr <= fr)
    a_, b_ = ab(u, v)
    if kind == 'D':
        d = q['D']
        hu, hv = d['half']
        ch = d['cham']
        # the casing: a box with its vertical edges chamfered and its top edges rounded over; a cap on top
        ins = (np.abs(u) <= hu) & (np.abs(v) <= hv) & (np.abs(u) + np.abs(v) <= hu + hv - ch)
        e_in = np.minimum(np.minimum(hu - np.abs(u), hv - np.abs(v)), (hu + hv - ch - np.abs(u) - np.abs(v)) * S2)
        ro = d['round']
        top = d['h'] - ro + np.sqrt(np.clip(ro * ro - np.clip(ro - e_in, 0, None) ** 2, 0, None))
        put(np.where(ins, W(top), 0.0), PG_BODY, ins)
        cp = d['cap']
        mc = ins & (e_in >= cp['inset'])
        A('cap').add(W(d['h'] - 1.0), W(d['h'] + cp['h']), PG_CAP, mc, 'cap')
        # the two beacon lights on top: a collar and a lens dome
        for (la, lb, lr) in d['lights']:
            lu, lv = uv(la, lb)
            r_ = np.hypot(u - lu, v - lv)
            A('lampb').add(W(d['h'] - 1.0), W(d['h'] + cp['h'] + 2.0), PG_LAMPB, r_ <= lr + 1.6, 'lampb')
            dome = W(d['h'] + cp['h'] + 2.0) + lr * np.sqrt(np.clip(1 - (r_ / lr) ** 2, 0, 1))
            A('lamp').add(W(d['h'] + cp['h'] + 1.0), dome, PG_LAMP, r_ <= lr, 'lamp')
        # the space-uplink antenna at the south-west corner: a short mast, a dish facing up and out to the west
        an = d['ant']
        au, av = an['at']
        mu, mv, mw = an['mast']
        n, acr, up = dish_axes(an['az'], an['el'])
        C = np.array([au, av, W(an['w'])])
        lo, hi, mm = rod_interval(u, v, (mu, mv, W(mw)), C - n * 3.0, 2.8)
        A('antmast').add(lo, hi, PG_MACH, mm, 'antmast')
        lo, hi, mm = rod_interval(u, v, C - n * 3.5, C - n * 0.5, 5.0)
        A('antbox').add(lo, hi, PG_HATCH, mm, 'antbox')
        lo, hi, mm = rod_interval(u, v, C - n * 0.6, C + n * 1.4, an['R'])
        A('antdish').add(lo, hi, PG_HATCH, mm, 'antdish')
        lo, hi, mm = rod_interval(u, v, C + n * 1.0, C + n * 8.0, 0.9)
        A('antfeed').add(lo, hi, PG_MACH, mm, 'antfeed')
        # the green panel on the south face (towards the camera's left), under the antenna
        gr = d['green']
        mg = (v >= hv - 0.5) & (v <= hv + 1.2) & (u >= gr['u'][0]) & (u <= gr['u'][1])
        A('green').add(W(gr['w'][0]), W(gr['w'][1]), PG_GREEN, mg, 'green')
        # the pump block low on the south face, two pipes along it
        pm = d['pump']
        mp = (v >= hv - 1.0) & (v <= hv + pm['out']) & (u >= pm['u'][0]) & (u <= pm['u'][1])
        A('pump').add(W(pm['w'][0]), W(pm['w'][1]), PG_MACH, mp, 'pump')
        for pw in pm['pipes']:
            lo, hi, mm = rod_interval(u, v, (pm['u'][0] + 1.0, hv + pm['out'] + 1.0, W(pw)),
                                     (pm['u'][1] - 1.0, hv + pm['out'] + 1.0, W(pw)), pm['pipe_r'])
            A('pipe').add(lo, hi, PG_PIPE, mm, 'pipe')
    elif kind == 'E':
        e_ = q['E']
        turn, blink = e_turn(t)
        c, s_ = np.cos(np.radians(turn)), np.sin(np.radians(turn))
        # the round lab: the body (a lathe), the black ring round its top, the low dome
        lo, hi, m = lathe(rr, e_['prof'])
        A('ebody').add(W(lo), W(hi), PG_EBODY, m, 'L:ebody')
        rg = e_['ring']
        A('ering').add(W(rg['w'][0]), W(rg['w'][1]), PG_ANT, rr <= rg['r'], 'ering')
        dm = e_['dome']
        md = rr <= dm['r']
        hd_ = dm['w'][1] - dm['w'][0]
        R = (dm['r'] ** 2 + hd_ ** 2) / (2 * hd_)
        ztop = dm['w'][1] - R + np.sqrt(np.clip(R * R - rr ** 2, 0, None))
        A('edome').add(W(dm['w'][0] - 1.0), W(ztop), PG_DOME, md, 'L:edome')
        # the two antennas: thick dark posts from the dome, a collar at the foot, a cap on top (turning with the lab)
        for (au, av, aw) in e_['ants']:
            pu, pv = au * c - av * s_, au * s_ + av * c
            rho = np.hypot(au, av)
            zb_ = dm['w'][1] - R + np.sqrt(max(R * R - rho * rho, 0.0))
            lo, hi, mm = rod_interval(u, v, (pu, pv, W(zb_ - 3.0)), (pu, pv, W(aw)), e_['ant_r'])
            A('ant').add(lo, hi, PG_ANT, mm, 'ant')
            lo, hi, mm = rod_interval(u, v, (pu, pv, W(zb_ - 1.5)), (pu, pv, W(zb_ + 2.2)), e_['ant_r'] + 1.6)
            A('antb').add(lo, hi, PG_EYEH, mm, 'antb')
            lo, hi, mm = rod_interval(u, v, (pu, pv, W(aw - 1.0)), (pu, pv, W(aw + 1.6)), e_['ant_r'] + 0.8)
            A('anttip').add(lo, hi, PG_ANT, mm, 'anttip')
        # the camera low on the front: a short fat barrel, the big round lens, the hood round it
        sc = e_['scope']
        ang = np.radians(sc['base'] + turn)
        dvec = np.array([np.cos(ang), np.sin(ang)])
        P = lambda r_, w_=sc['w']: (dvec[0] * r_, dvec[1] * r_, W(w_))
        lo, hi, mm = rod_interval(u, v, P(sc['r0']), P(sc['r1']), sc['r'])
        A('scope').add(lo, hi, PG_EYEH, mm, 'scope')
        # the glass stands proud of the hood's face (a solid hood round it would hide it) and goes in before the hood,
        # so where a ray steps into both behind the hood's face the glass wins (no stripes of hood across it)
        lo, hi, mm = rod_interval(u, v, P(sc['r1'] - 0.6), P(sc['r1'] + 1.8), sc['lens'])
        A('eye').add(lo, hi, PG_EYE, mm, 'eye')
        lo, hi, mm = rod_interval(u, v, P(sc['r1'] - 2.5), P(sc['r1'] + 1.0), sc['hood'])
        A('scopeh').add(lo, hi, PG_MACH, mm, 'scopeh')
        # the two ear muffs on its sides: round pods with a rim and a grille face
        mf = e_['muffs']
        for side in (90.0, -90.0):
            a2 = np.radians(sc['base'] + turn + side)
            d2 = np.array([np.cos(a2), np.sin(a2)])
            p0 = (d2[0] * mf['r0'], d2[1] * mf['r0'], W(mf['w'])); p1 = (d2[0] * mf['r1'], d2[1] * mf['r1'], W(mf['w']))
            lo, hi, mm = rod_interval(u, v, p0, p1, mf['r'])
            A('muff').add(lo, hi, PG_EPLATE, mm, 'muff')
            g0 = (d2[0] * (mf['r1'] - 2.0), d2[1] * (mf['r1'] - 2.0), W(mf['w']))
            g1 = (d2[0] * (mf['r1'] + 0.8), d2[1] * (mf['r1'] + 0.8), W(mf['w']))
            lo, hi, mm = rod_interval(u, v, g0, g1, mf['r'] - mf['rim'])
            A('grille').add(lo, hi, PG_DARK, mm, 'grille')
    elif kind == 'F':
        f = q['F']
        # the plinth standing in the socket, a black ring round it; the round platform on it
        pn = f['plinth']
        A('ftower').add(W(pn['w'][0]), W(pn['w'][1]), PG_TOWER, rr <= pn['r'], 'ftower')
        rg_r, w0, w1 = pn['ring']
        A('fring').add(W(w0), W(w1), PG_DARK, rr <= rg_r, 'fring')
        dk = f['deck']
        A('deck').add(W(dk['w'][0]), W(dk['w'][1]), PG_FBAND, rr <= dk['r'], 'deck')
        # the railings round the platform's edge: posts, a mid rail and a top rail
        rl = f['rail']
        for k in range(rl['n']):
            a = 2 * np.pi * (k + 0.5) / rl['n']
            pu, pv = rl['r'] * np.cos(a), rl['r'] * np.sin(a)
            lo, hi, mm = rod_interval(u, v, (pu, pv, W(rl['w'][0])), (pu, pv, W(rl['w'][1])), rl['post'])
            A('rib').add(lo, hi, PG_RIB, mm, 'rib')
        ring_m = np.abs(rr - rl['r']) <= rl['hw']
        A('rail').add(W(rl['top'][0]), W(rl['top'][1]), PG_LEG, ring_m, 'rail')
        if rl.get('mid'):
            A('rail2').add(W(rl['mid'][0]), W(rl['mid'][1]), PG_LEG, ring_m, 'rail2')
        # the slim pole up through the middle, a foot on the platform and a black collar high on it
        po = f['pole']
        A('neck').add(W(po['w'][0]), W(po['w'][1]), PG_NECK, rr <= po['r'], 'neck')
        fr_, w0, w1 = po['foot']
        A('pfoot').add(W(w0), W(w1), PG_NECK, rr <= fr_, 'pfoot')
        for cr_, w0, w1 in po['collars']:
            A('fring').add(W(w0), W(w1), PG_DARK, rr <= cr_, 'fring')
        # the wide platform on top of the pole
        yk = f['yoke']
        A('yoke').add(W(yk['w'][0]), W(yk['w'][1]), PG_FPLAT, rr <= yk['r'], 'yoke')
        # the dish's mount: a turntable on the platform, the housing on it turning with the dish, a fork and a hub
        C, n, acr, up = f_dish(t, q)
        ds = f['dish']; mt = f['mount']
        C = C + np.array([0, 0, base_w])
        az_ = np.arctan2(n[1], n[0])
        fwd = np.array([np.cos(az_), np.sin(az_), 0.0]); side = np.array([-np.sin(az_), np.cos(az_), 0.0])
        pr_, w0, w1 = mt['ped']
        A('ped').add(W(w0), W(w1), PG_NECK, rr <= pr_, 'ped')
        hs = mt['house']
        Ch = fwd * 0.5 * (hs['back'] + hs['front']) + np.array([0, 0, W(0.5 * (hs['w'][0] + hs['w'][1]))])
        lo, hi, mm = obox_interval(u, v, Ch, np.array([fwd, side, [0, 0, 1.0]]),
                                   (0.5 * (hs['front'] - hs['back']), hs['half'], 0.5 * (hs['w'][1] - hs['w'][0])))
        A('box').add(lo, hi, PG_HEAD, mm, 'box')
        # the dish: a panel (white face, dark frame and back)
        E3 = np.array([acr, up, n])
        lo, hi, mm = obox_interval(u, v, C + n * 0.4, E3, (ds['hw'], ds['hh'], ds['t'] * 0.5))
        A('dish').add(lo, hi, PG_DISH, mm, 'dish')
        lo, hi, mm = obox_interval(u, v, C - n * (ds['t'] * 0.5 + 1.0), E3, (ds['hw'] + 1.2, ds['hh'] + 1.2, 1.2))
        A('dishb').add(lo, hi, PG_DISHB, mm, 'dishb')
        # the fork: from the housing's front corners to the axle stubs at the dish's sides; the hub to its back
        wa = W(0.5 * (hs['w'][0] + hs['w'][1]) + 2.0)
        for sgn in (-1.0, 1.0):
            P0 = fwd * hs['front'] + side * sgn * (hs['half'] - 2.0) + np.array([0, 0, wa])
            P1 = C - n * 1.5 + acr * sgn * (ds['hw'] + 2.2)
            lo, hi, mm = rod_interval(u, v, P0, P1, mt['arm_r'])
            A('arm').add(lo, hi, PG_HEAD, mm, 'arm')
            lo, hi, mm = rod_interval(u, v, C - n * 1.5 + acr * sgn * (ds['hw'] - 0.5), C - n * 1.5 + acr * sgn * (ds['hw'] + 3.6), 3.0)
            A('axle').add(lo, hi, PG_FEED, mm, 'axle')
        lo, hi, mm = rod_interval(u, v, fwd * (hs['front'] - 1.0) + np.array([0, 0, wa]), C - n * 2.0, mt['hub_r'])
        A('arm2').add(lo, hi, PG_HEAD, mm, 'arm2')
        lo, hi, mm = rod_interval(u, v, C + n * 1.0, C + n * ds['feed'], 1.1)
        A('feed').add(lo, hi, PG_FEED, mm, 'feed')
        Fk = C + n * ds['feed']
        # two struts from the panel's side edges to the feed
        for sgn in (-1.0, 1.0):
            E0 = C + n * 1.0 + acr * sgn * (ds['hw'] - 2.0)
            lo, hi, mm = rod_interval(u, v, E0, Fk, 0.8)
            A('strut').add(lo, hi, PG_FEED, mm, 'strut')
        lo, hi, mm = rod_interval(u, v, Fk - n * 1.5, Fk + n * 1.5, 2.6)
        A('feedk').add(lo, hi, PG_FEED, mm, 'feedk')

FLAT = {PG_FLANGE: (150, 150, 150), PG_BODY: (120, 106, 74), PG_CAP: (150, 136, 98), PG_HATCH: (200, 160, 80),
        PG_GREEN: (0, 214, 0), PG_LAMP: (255, 255, 255), PG_MACH: (100, 100, 120), PG_DARK: (40, 40, 40),
        PG_DOME: (140, 128, 92), PG_ANT: (30, 30, 30), PG_EYE: (240, 240, 240), PG_EYEH: (100, 94, 70),
        PG_TOWER: (100, 80, 56), PG_RIB: (150, 136, 96), PG_LEG: (90, 74, 52), PG_NECK: (40, 36, 30),
        PG_HEAD: (130, 118, 86), PG_DISH: (236, 236, 230), PG_DISHB: (80, 80, 84), PG_EBODY: (130, 116, 80),
        PG_EBAND: (190, 150, 80), PG_FBAND: (190, 152, 92), PG_FFOOT: (92, 76, 52), PG_LAMPB: (90, 90, 96),
        PG_PIPE: (130, 132, 150), PG_FEED: (60, 60, 64), PG_ESKIRT: (70, 62, 48), PG_EPLATE: (150, 136, 96),
        PG_FPLAT: (170, 160, 120)}
