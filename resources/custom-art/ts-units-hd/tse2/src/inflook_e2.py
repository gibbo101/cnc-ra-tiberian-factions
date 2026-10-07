"""
inflook_e2.py - the Disc Thrower's look v2 (the makeover): the same skeleton, poses and fitted sizes as inf.py's E2,
built as armour after Westwood's own Disc Thrower renders (the throwing render, the FMV still kneeling by the wreck)
and the Tiberian Aftermath turnaround Luke sent, in the Light Infantry makeover's style (inflook.py, signed off).  TS's
sprites still set where every part is and its colour:

  - the box pack on his back as before (TS's blue-grey, its lid band; Luke: "pack is good!"), now with the radio's
    whip antenna from its top corner and a slatted panel on its back (shape only, in the pack's own colours);
  - the two disc drums low on his back, one above the other across his hips, under the pack, sticking out either
    side (the renders' drums; TS's orange across his hips behind and at the backs of his hips in the side views:
    they are TS's orange), dark end caps with a hub;
  - the full helmet with its big visor in a dark frame, an ear piece each side, the respirator under the visor and
    its hose down to his chest;
  - a segmented chest: the chest plate, three plates down the belly with the dark suit showing between them, a
    gorget at the neck;
  - shoulder pads of three lames (the renders' striped pads; house colour is plain, so the stripes are the lames'
    edges only);
  - green upper arms, dark elbows, long dark gauntlets from below the elbow to the fist (TS's front views: his forearms
    dark under green upper arms);
  - green thighs with a plate on their outer front, the backs of the legs dark (TS's back view), big orange knee pads
    (TS's front views), greaves down the shins, boots with soles and two straps.

    S['look'] = 2 switches inf.parts to this for E2's kit.
"""
import numpy as np
import rc
import inf as I
from inflook import shell, limb_frame, segbox

# components (fitting classes below; colours in infunit.MAT['e2'])
(PLATE2, GAUNT, KNEEPAD, DRUM, DRUMCAP, ANTENNA, HOSE, EAR2, GREAVE2, SOLE2, THIGHPL, LAME, THIGHBACK, BUCKLE,
 STRAP, SUIT) = range(760, 776)
I.CLASS.update({PLATE2: I.DARK, GAUNT: I.DARK, KNEEPAD: I.ORANGE, DRUM: I.ORANGE, DRUMCAP: I.ORANGE,
                ANTENNA: 6, HOSE: I.DARK, EAR2: I.NAVY, GREAVE2: I.DARK, SOLE2: I.DARK, THIGHPL: I.GREEN,
                LAME: I.GREEN, THIGHBACK: I.DARK, BUCKLE: I.DARK, STRAP: I.DARK, SUIT: I.DARK})
HOUSE_EXTRA = (THIGHPL, LAME)


def _cyl(p0, p1, r, comp, name, frame_R):
    p = rc.cylinder(p0, p1, r, comp, name)
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    p.low = float(min(p0[2], p1[2]) - r)
    p.frame = ((p0 + p1) / 2, np.asarray(frame_R, float))
    return p


def _rounded_box(c, R, h, er_scale, ec_off, comp, name, top=1.0):
    """a box (half-sizes h) cut by an ellipsoid er_scale times as big, its centre ec_off along the box's own axes:
    a soft-edged box (the pack)."""
    c = np.asarray(c, float); R = np.asarray(R, float); h = np.asarray(h, float)
    ec = c + R @ np.asarray(ec_off, float)
    er = np.asarray(er_scale, float)
    p = rc.Part(rc.box_planes(c, R, h) + [rc.Ellip(ec, R, er)], comp, name,
                sphere=(c, float(np.linalg.norm(h)) + 1e-3))
    p.low = c[2] - float(np.abs(R[2, :]) @ h)
    p.frame = (c, R)
    return p


def parts(S, Q, th, rifle=True):
    P = I.Pose(S, Q, th)
    out = []
    P0, B = P.pelvis
    C0, RC = P.chest
    M, RL = P.mid
    pr = np.asarray(S['pr'], float)
    # ---- hips (green), the belt, its buckle
    out.append(I.ellip(P0 + B @ np.array([0, 0, 0.2]), B, pr, I.PELVIS, 'pelvis'))
    out.append(I.ellip(P0 + B @ np.array([0, 0, 0.55]), B, (pr[0] * 1.05, pr[1] * 1.02, 0.42), I.BELT, 'belt'))
    out.append(I.box(P0 + B @ np.array([pr[0] * 1.0, 0, 0.5]), B, (0.18, 0.6, 0.36), BUCKLE, chamfer=(0.06, 0.15, 0.12),
                     name='buckle'))
    # ---- legs
    for side, sg in (('l', -1.0), ('r', 1.0)):
        H, RT, K, RS, A, RF = P.legs[side]
        th_ = I.taper_limb(H, K, RT, S['rt'], S['rt'] * 0.8, I.THIGH, 'thigh', ext=0.3)
        # (green in front, the dark suit behind: TS's back view draws the backs of his legs dark)
        out += I.split(th_, RT[:, 0], -0.3 * S['rt'], THIGHBACK, 'thigh_back')
        Mt, L = limb_frame(H, K, RT)
        ct = H + (K - H) * 0.42
        fwd = Mt[:, 0]; side_v = RT[:, 1] * sg
        n = fwd * 0.55 + side_v * 0.85; n = n - (n @ Mt[:, 2]) * Mt[:, 2]; n = n / np.linalg.norm(n)
        R2 = np.stack([n, np.cross(Mt[:, 2], n), Mt[:, 2]], 1)
        out.append(shell(ct, R2, (S['rt'] * 1.08, S['rt'] * 1.08, L * 0.34), [((1, 0, 0), S['rt'] * 0.15)],
                         THIGHPL, 'thigh_plate'))
        # the big knee pad: a domed plate over the knee's front, reaching a little up the thigh (TS: orange on the
        # knees in the front views)
        Ms, Ls = limb_frame(K, A, RS)
        kc = K + RS @ np.array([-0.1, 0, 0.2])
        out.append(shell(kc, Ms, (S['rs'] * 1.45, S['rs'] * 1.1, S['rs'] * 1.35), [((1, 0, 0), S['rs'] * 0.75)],
                         KNEEPAD, 'knee'))
        out.append(I.taper_limb(K, A, RS, S['rs'], S['rs'] * 0.75, I.SHIN, 'shin', ext=0.2))
        cs = K + (A - K) * 0.55
        out.append(shell(cs, Ms, (S['rs'] * 1.08, S['rs'] * 1.06, Ls * 0.38), [((1, 0, 0), S['rs'] * 0.1)],
                         GREAVE2, 'greave'))
        # (the boot's two straps round the top of the boot)
        for i, t in enumerate((0.8, 0.92)):
            p0 = K + (A - K) * t
            out.append(_cyl(p0 - Ms[:, 2] * 0.13, p0 + Ms[:, 2] * 0.13, S['rs'] * 0.84, STRAP, 'boot_strap_%d' % i, Ms))
        c = A + RF @ np.array([0.3 * S['bl'] - 0.15, 0, -S['bh'] * 0.3])
        out.append(I.box(c, RF, (S['bl'] / 2, S['bw'], S['bh'] / 2 * 0.85), I.BOOT, chamfer=(0.35, 0.3, 0.3),
                         name='boot'))
        cso = A + RF @ np.array([0.3 * S['bl'] - 0.1, 0, -S['bh'] * 0.3 - S['bh'] / 2 * 0.85 - 0.08])
        out.append(I.box(cso, RF, (S['bl'] / 2 + 0.08, S['bw'] + 0.06, 0.16), SOLE2, chamfer=(0.1, 0.1, 0.05),
                         name='sole'))
    # ---- torso: the dark suit, the segmented plates down his front, the gorget
    if Q.get('smid', 0.0):
        ac, RA = P0 + (M - P0) * 0.75, RL
    else:
        ac, RA = P0 + (C0 - P0) * 0.45, RC
    ar = np.asarray(S['ar'], float)
    out.append(I.ellip(ac, RA, ar, SUIT, 'abdomen'))
    cc = C0 + RC @ np.array([0, 0, -S['cr'][2] * 0.55])
    cr = np.asarray(S['cr'], float)
    out.append(I.ellip(cc, RC, cr, I.CHEST, 'chest'))
    out.append(I.ellip(cc + RC @ np.array([cr[0] * 0.35, 0, -0.35]), RC,
                       (cr[0] * 0.7 + S['vt'], cr[1] * 0.72, cr[2] * 0.8), I.VEST, 'vest'))
    # (the chest plate: the chest's shell 0.18 proud, from the collarbones down to the ribs)
    out.append(shell(cc, RC, cr + 0.18, [((1, 0, 0), cr[0] * 0.15), ((0, 0, -1), -cr[2] * 0.66),
                                         ((0, 0, 1), cr[2] * 0.02)], PLATE2, 'chest_plate'))
    # (the back plate under the pack)
    out.append(shell(cc, RC, cr + 0.12, [((-1, 0, 0), cr[0] * 0.25), ((0, 0, -1), -cr[2] * 0.7),
                                         ((0, 0, 1), -cr[2] * 0.3)], PLATE2, 'back_plate'))
    # (the belly: one plate under the chest plate on the chest's shell, two on the abdomen's, dark gaps between)
    out.append(shell(cc, RC, cr + 0.14, [((1, 0, 0), cr[0] * 0.2), ((0, 0, -1), cr[2] * 0.1),
                                         ((0, 0, 1), -cr[2] * 0.36)], PLATE2, 'belly_plate_0'))
    for i, (z0, z1) in enumerate(((0.18, 0.52), (-0.42, -0.02))):
        out.append(shell(ac, RA, ar + 0.13, [((1, 0, 0), ar[0] * 0.15), ((0, 0, -1), -ar[2] * z1),
                                             ((0, 0, 1), ar[2] * z0)], PLATE2, 'belly_plate_%d' % (i + 1)))
    out.append(I.ellip(C0 + RC @ np.array([0.15, 0, 0.1]), RC, (cr[0] * 0.6, cr[1] * 0.62, 0.42), PLATE2, 'gorget'))
    # ---- the pack (inf.py's rucksack, as fitted), its antenna and slatted panel
    rk = np.array([S.get('rkd', S['rk'][0]), S.get('rkw', S['rk'][1]), S.get('rkh', S['rk'][2])], float)
    RK = RC @ I.Ry(-S.get('rkt', 0.0))
    pc = cc + RC @ np.array([-cr[0] * 0.85 + S.get('rko', 0.0), 0, S['rkz']]) - RK[:, 0] * rk[0]
    r = float(S.get('rkr', 1.12)); f = S.get('rkf', 0.6)
    out.append(_rounded_box(pc, RK, rk, (rk[0] * (1.0 + f) * r, rk[1] * r, rk[2] * r * S.get('rkh2', 1.0)),
                            (rk[0] * f, 0, 0), I.TUBE, 'pack'))
    if S.get('rkl', 0.0) > 0.0:
        lh = rk[2] * S['rkl']; lp = S.get('rlp', 0.3)
        lc = pc + RK[:, 2] * (rk[2] - lh) - RK[:, 0] * lp * 0.5
        lk = np.array([rk[0] + lp * 0.5, rk[1] + lp * 0.5, lh])
        out.append(_rounded_box(lc, RK, lk, (lk[0] * (1.0 + f) * r, lk[1] * r, lk[2] * r * 1.6), (lk[0] * f, 0, 0),
                                I.TUBE, 'pack_lid'))
    # (the panel on its back: four slats across, a little proud, in the pack's own colour)
    for i in range(4):
        zc = -rk[2] * 0.62 + i * rk[2] * 0.2
        out.append(I.box(pc + RK @ np.array([-rk[0] - 0.06, 0, zc]), RK, (0.1, rk[1] * 0.58, 0.16), I.TUBE,
                         chamfer=(0.04, 0.05, 0.05), name='pack_slat_%d' % i))
    # (the whip antenna from the top of the pack at his left shoulder, leaning back a little: its base, the whip)
    ab = pc + RK @ np.array([-rk[0] * 0.35, -rk[1] * 0.72, rk[2] - 0.05])
    au = RK @ np.array([-0.18, -0.04, 1.0]); au = au / np.linalg.norm(au)
    # (a whip: it springs upright when he lies down - set along his back it stuck out past his head like a lance)
    au = au + np.array([0.0, 0.0, S.get('anu', 0.9)]); au = au / np.linalg.norm(au)
    out.append(_cyl(ab - au * 0.1, ab + au * 0.7, 0.32, STRAP, 'antenna_base', RK))
    out.append(_cyl(ab + au * 0.6, ab + au * S.get('anl', 5.6), S.get('anr', 0.15), ANTENNA, 'antenna', RK))
    # ---- the two disc drums across his hips behind, under the pack (one above the other), hung on a dark strap
    dr = S.get('drr', 0.76); dl = S.get('drl', 2.9); dx = S.get('drx', 0.65)
    dzs = (S.get('drz', -0.3), S.get('drz', -0.3) - 2 * dr - S.get('drg', 0.24))
    for i, dz in enumerate(dzs):
        c = P0 + B @ np.array([-(pr[0] + dx), 0, dz])
        a = B[:, 1]
        out.append(_cyl(c - a * (dl - 0.2), c + a * (dl - 0.2), dr, DRUM, 'drum_%d' % i, B))
        for sg in (-1.0, 1.0):
            e = c + a * sg * (dl - 0.2)
            out.append(_cyl(e, e + a * sg * 0.2, dr * 1.04, DRUMCAP, 'drum_cap_%d' % i, B))
            out.append(_cyl(e + a * sg * 0.15, e + a * sg * 0.32, dr * 0.38, DRUMCAP, 'drum_hub_%d' % i, B))
            # (a raised band round each drum a third of the way in from either end)
            m = c + a * sg * (dl - 0.2) * 0.45
            out.append(_cyl(m - a * 0.1, m + a * 0.1, dr * 1.06, DRUM, 'drum_band_%d' % i, B))
    top = P0 + B @ np.array([-(pr[0] + dx - dr * 0.75), 0, dzs[0] + dr + 0.4])
    bot = P0 + B @ np.array([-(pr[0] + dx - dr * 0.75), 0, dzs[1]])
    out.append(segbox(top, bot, 0.9, 0.25, STRAP, B[:, 0], 'drum_strap'))
    # ---- arms: three-lame shoulder pads, green upper arms, dark elbows, long dark gauntlets, the fists
    pd = np.asarray(S['pd'], float)
    for side, sg in (('l', -1.0), ('r', 1.0)):
        Sh, RU, E, RFa, W = P.arms[side]
        sw = S['sw']
        y_in, y_out = 0.62 * sw, sw + 0.65
        Rt = RC @ I.Rx(sg * 24.0)
        ctop = Sh + RC @ np.array([0.0, sg * ((y_in + y_out) / 2 - sw), 0.5])
        out.append(I.box(ctop, Rt, (pd[0] * 0.9, (y_out - y_in) / 2, 0.34), I.PAD, chamfer=(0.3, 0.2, 0.3),
                         name='shoulder_pad'))
        Mu, Lu = limb_frame(Sh, E, RC)
        outv = RC[:, 1] * sg - (RC[:, 1] * sg @ Mu[:, 2]) * Mu[:, 2]
        outv = outv / max(float(np.linalg.norm(outv)), 1e-6)
        Rl = np.stack([Mu[:, 2], np.cross(outv, Mu[:, 2]), outv], 1)
        for j, (t, wd, o) in enumerate(((0.16, 0.78, 0.66), (0.34, 0.68, 0.58))):
            cl = Sh + (E - Sh) * t + outv * (S['ru'] * o)
            out.append(I.box(cl, Rl, (Lu * 0.13, S['ru'] * wd, 0.24), LAME, chamfer=(0.16, 0.2, 0.14),
                             name='shoulder_lame_%d' % j))
        out.append(I.taper_limb(Sh, E, RU, S['ru'] * 0.88, S['ru'] * 0.66, I.UARM, 'upper_arm', ext=0.05))
        out.append(I.ellip(E, RFa, (S['ru'] * 0.62,) * 3, SUIT, 'elbow'))
        # (the gauntlet: from just below the elbow, flared at its cuff, to the wrist)
        g0 = E + (W - E) * 0.1
        out.append(I.taper_limb(g0, W, RFa, S['rf'] * 1.12, S['rf'] * 0.82, GAUNT, 'forearm', ext=0.0))
        out.append(_cyl(g0 - (W - E) * 0.02, g0 + (W - E) * 0.1, S['rf'] * 1.12, GAUNT, 'gauntlet_cuff', RFa))
        out.append(I.ellip(W + RFa @ np.array([0, 0, -S['rh'] * 0.6]), RFa,
                           (S['rh'] * 1.05, S['rh'] * 0.9, S['rh'] * 1.15), I.HAND, 'hand'))
    # ---- the helmet: the shell, the visor in its dark frame, the jaw, the ear pieces, the respirator and its hose
    Hc, RH = P.head
    hr = np.asarray(S['hr'], float)
    hp = rc.Part(I.helmet_cons(Hc, RH, hr), I.HELMET, 'helmet', sphere=(Hc, float(np.linalg.norm(hr)) + 1e-3))
    hp.low = Hc[2] - float(np.abs(RH[2, :]) @ hr)
    hp.frame = (np.asarray(Hc, float), np.asarray(RH, float))
    out.append(hp)
    out.append(I.shell_patch(Hc, RH, hr, S['fd'] * 0.55, S['fva'] + 6.0, S['fe0'] - 4.0, S['fe1'] + 6.0, I.JAW,
                             'visor_frame'))
    out.append(I.shell_patch(Hc, RH, hr, S['fd'], S['fva'], S['fe0'], S['fe1'], I.VISOR, 'mask'))
    out.append(I.shell_patch(Hc, RH, hr, S['fd'] * 0.6, S['fva'] + 6.0, S['fe0'] - S['fj'], S['fe0'], I.JAW, 'jaw'))
    for sg, nm in ((-1.0, 'l'), (1.0, 'r')):
        a = RH[:, 1] * sg
        c = Hc + a * (hr[1] * 1.0) + RH @ np.array([-hr[0] * 0.1, 0, -hr[2] * 0.15])
        out.append(_cyl(c - a * 0.12, c + a * 0.3, hr[2] * 0.45, EAR2, 'ear_' + nm, RH))
    # (the respirator under the visor, pointing down and forward; the hose from it curving down to the chest plate on
    # his left)
    rp = Hc + RH @ np.array([hr[0] * 0.92, 0.0, -hr[2] * 0.62])
    rd = RH @ np.array([0.75, 0.0, -0.66]); rd = rd / np.linalg.norm(rd)
    out.append(_cyl(rp - rd * 0.2, rp + rd * 0.45, 0.42, HOSE, 'respirator', RH))
    h0 = rp + rd * 0.4
    h2 = cc + RC @ np.array([cr[0] * 1.02, -cr[1] * 0.42, cr[2] * 0.25])
    h1 = (h0 + h2) / 2 + RC[:, 0] * 0.55 - RC[:, 1] * 0.35
    pts = [(1 - t) ** 2 * h0 + 2 * (1 - t) * t * h1 + t * t * h2 for t in np.linspace(0, 1, 5)]
    for j in range(4):
        out.append(_cyl(pts[j], pts[j + 1], S.get('hsr', 0.24), HOSE, 'hose_%d' % j, RC))
    for j in range(1, 4):
        out.append(I.ellip(pts[j], RC, (S.get('hsr', 0.24),) * 3, HOSE, 'hose_joint_%d' % j))
    # ---- the disc in his right hand, flat in the palm
    if Q.get('disc', 0.0) > 0.5:
        Sh, RU, E, RFa, W = P.arms['r']
        c = W + RFa @ np.array([0.0, 0.0, -S['rh'] * 1.1])
        p = rc.cylinder(c - RFa[:, 0] * S['dt'], c + RFa[:, 0] * S['dt'], S['dr'], I.DISC, 'disc')
        p.low = c[2] - S['dr']
        p.frame = (c, RFa)
        out.append(p)
    return out
