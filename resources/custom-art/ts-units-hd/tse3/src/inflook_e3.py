"""
inflook_e3.py - the Rocket Infantry's look v2 (the makeover): the same skeleton, poses and fitted sizes as inf.py's E3,
built as armour in the GDI makeovers' style (inflook.py, inflook_e2.py), after the Nod rocket trooper concept Luke sent
(dark armour, a red-visored helmet with an antenna, house-coloured shoulders and knee chevrons, the launcher on his
shoulder with a yellow band at its mouth).  TS's sprite sets where the big colour areas are: his dark armour and helmet,
house green on his shoulder pads, upper arms and thighs, light grey knees and shins, the light grey launcher with dark
ends.  The concept's red marks are house colour (Nod's red is its house colour):

  - the full dark helmet, its red glowing visor in a dark frame, an ear piece each side, a short antenna on its left,
    a small house-coloured lamp on its crown;
  - segmented dark armour: the chest plate, two belly plates, a gorget, the back plate; the dark suit between;
  - a box pack on his back with its flap; belt pouches; a holster on his right thigh;
  - shoulder pads of two plates in house colour, house upper arms, dark elbows and forearms, gloves;
  - house thighs with a plate on their outer front, light grey knee plates with a house chevron, light grey greaves,
    dark boots with soles;
  - the launcher (TS's: light grey, dark rims at either end) with a yellow band near its mouth, a sight on its left
    side and the grip block under it.

    S['look'] = 2 switches inf.parts to this for E3's kit.
"""
import numpy as np
import rc
import inf as I
from inflook import shell, limb_frame, segbox
from inflook_e2 import _cyl

(PLATE, SUIT, LAME, THIGHPL, KNEEPL, CHEV, GREAVE, SOLE, WEB, FRAME, EAR, ANT, LAMP, BAND, SIGHT, FLAP,
 HOLSTER) = range(830, 847)
I.CLASS.update({PLATE: I.DARK, SUIT: I.DARK, LAME: I.GREEN, THIGHPL: I.GREEN, KNEEPL: I.GREY, CHEV: I.GREEN,
                GREAVE: I.GREY, SOLE: I.DARK, WEB: I.DARK, FRAME: I.DARK, EAR: I.DARK, ANT: 6, LAMP: I.GREEN,
                BAND: 6, SIGHT: I.DARK, FLAP: I.DARK, HOLSTER: I.DARK})


def chevron(c, n, up, size, width, d, comp, name):
    """a chevron (^) on a surface at c, facing n, its point towards up: two thin bars meeting at the top."""
    n = np.asarray(n, float); up = np.asarray(up, float)
    side = np.cross(n, up)
    out = []
    for sg in (-1.0, 1.0):
        along = up * np.cos(np.deg2rad(55)) - side * sg * np.sin(np.deg2rad(55))
        along = along / np.linalg.norm(along)
        a = np.cross(n, along)
        cc = np.asarray(c, float) + n * d * 0.5 - along * size * 0.5 + side * sg * 0.0
        R = np.stack([along, a, n], 1)
        out.append(I.box(cc, R, (size * 0.5, width * 0.5, d * 0.5), comp, name='%s_%d' % (name, int(sg > 0))))
    return out


def parts(S, Q, th, rifle=True):
    P = I.Pose(S, Q, th)
    out = []
    P0, B = P.pelvis
    C0, RC = P.chest
    M, RL = P.mid
    pr = np.asarray(S['pr'], float)
    # ---- hips, belt, pouches
    out.append(I.ellip(P0 + B @ np.array([0, 0, 0.2]), B, pr, I.PELVIS, 'pelvis'))
    out.append(I.ellip(P0 + B @ np.array([0, 0, 0.55]), B, (pr[0] * 1.05, pr[1] * 1.02, 0.42), I.BELT, 'belt'))
    for i, (x, y) in enumerate(((0.7, -0.75), (0.95, -0.25), (0.95, 0.25), (0.7, 0.75))):
        c = P0 + B @ np.array([pr[0] * x, pr[1] * y, 0.5])
        out.append(I.box(c, B, (0.32, 0.38, 0.42), WEB, chamfer=(0.1, 0.1, 0.12), name='belt_pouch_%d' % i))
    # ---- legs
    for side, sg in (('l', -1.0), ('r', 1.0)):
        H, RT, K, RS, A, RF = P.legs[side]
        out.append(I.taper_limb(H, K, RT, S['rt'], S['rt'] * 0.8, I.THIGH, 'thigh', ext=0.3))
        Mt, L = limb_frame(H, K, RT)
        fwd = Mt[:, 0]; side_v = RT[:, 1] * sg
        n = fwd * 0.55 + side_v * 0.85; n = n - (n @ Mt[:, 2]) * Mt[:, 2]; n = n / np.linalg.norm(n)
        R2 = np.stack([n, np.cross(Mt[:, 2], n), Mt[:, 2]], 1)
        out.append(shell(H + (K - H) * 0.42, R2, (S['rt'] * 1.08, S['rt'] * 1.08, L * 0.34), [((1, 0, 0), S['rt'] * 0.15)],
                         THIGHPL, 'thigh_plate'))
        if side == 'r':
            # (the holster on his right thigh, outside)
            hc = H + (K - H) * 0.45 + side_v * S['rt'] * 1.05
            out.append(I.box(hc, Mt, (0.3, 0.42, L * 0.2), HOLSTER, chamfer=(0.1, 0.1, 0.12), name='holster'))
        Ms, Ls = limb_frame(K, A, RS)
        kc = K + RS @ np.array([-0.1, 0, 0.15])
        kp = shell(kc, Ms, (S['rs'] * 1.35, S['rs'] * 1.08, S['rs'] * 1.25), [((1, 0, 0), S['rs'] * 0.7)], KNEEPL, 'knee')
        out.append(kp)
        # (the house chevron on the knee plate's front)
        out += chevron(kc + Ms[:, 0] * S['rs'] * 1.33 + Ms[:, 2] * S['rs'] * 0.25, Ms[:, 0], Ms[:, 2], S['rs'] * 0.75,
                       0.24, 0.08, CHEV, 'knee_chevron')
        out.append(I.taper_limb(K, A, RS, S['rs'], S['rs'] * 0.75, I.SHIN, 'shin', ext=0.2))
        out.append(shell(K + (A - K) * 0.55, Ms, (S['rs'] * 1.08, S['rs'] * 1.06, Ls * 0.38), [((1, 0, 0), S['rs'] * 0.1)],
                         GREAVE, 'greave'))
        c = A + RF @ np.array([0.3 * S['bl'] - 0.15, 0, -S['bh'] * 0.3])
        out.append(I.box(c, RF, (S['bl'] / 2, S['bw'], S['bh'] / 2 * 0.85), I.BOOT, chamfer=(0.35, 0.3, 0.3),
                         name='boot'))
        cso = A + RF @ np.array([0.3 * S['bl'] - 0.1, 0, -S['bh'] * 0.3 - S['bh'] / 2 * 0.85 - 0.08])
        out.append(I.box(cso, RF, (S['bl'] / 2 + 0.08, S['bw'] + 0.06, 0.16), SOLE, chamfer=(0.1, 0.1, 0.05),
                         name='sole'))
    # ---- torso: the dark suit, the segmented plates, the gorget, the back plate
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
    out.append(shell(cc, RC, cr + 0.18, [((1, 0, 0), cr[0] * 0.12), ((0, 0, -1), -cr[2] * 0.66),
                                         ((0, 0, 1), cr[2] * 0.02)], PLATE, 'chest_plate'))
    out.append(shell(cc, RC, cr + 0.12, [((-1, 0, 0), cr[0] * 0.25), ((0, 0, -1), -cr[2] * 0.7),
                                         ((0, 0, 1), -cr[2] * 0.3)], PLATE, 'back_plate'))
    out.append(shell(cc, RC, cr + 0.14, [((1, 0, 0), cr[0] * 0.2), ((0, 0, -1), cr[2] * 0.1),
                                         ((0, 0, 1), -cr[2] * 0.38)], PLATE, 'belly_plate_0'))
    out.append(shell(ac, RA, ar + 0.13, [((1, 0, 0), ar[0] * 0.15), ((0, 0, -1), -ar[2] * 0.5),
                                         ((0, 0, 1), ar[2] * 0.12)], PLATE, 'belly_plate_1'))
    out.append(I.ellip(C0 + RC @ np.array([0.15, 0, 0.1]), RC, (cr[0] * 0.6, cr[1] * 0.62, 0.42), PLATE, 'gorget'))
    # ---- the box pack and its flap
    pk = np.asarray(S['pk'], float) * np.array([1.15, 1.35, 1.0])
    pc = cc + RC @ np.array([-cr[0] * 0.85 - pk[0] * 0.4, 0, 0.2])
    out.append(I.box(pc, RC, pk, I.PACK, chamfer=(0.22, 0.25, 0.25), name='pack'))
    out.append(I.box(pc + RC @ np.array([-0.1, 0, pk[2] * 0.6]), RC, (pk[0] + 0.08, pk[1] + 0.06, pk[2] * 0.42), FLAP,
                     chamfer=(0.18, 0.2, 0.18), name='pack_flap'))
    # ---- arms: house shoulder plates, house upper arms, dark elbows and forearms, gloves
    pd = np.asarray(S['pd'], float)
    for side, sg in (('l', -1.0), ('r', 1.0)):
        Sh, RU, E, RFa, W = P.arms[side]
        sw = S['sw']
        # (TS's green pads are big - the widest part of him in the front and back views)
        y_in, y_out = 0.5 * sw, sw + 1.0
        Rt = RC @ I.Rx(sg * 24.0)
        ctop = Sh + RC @ np.array([0.0, sg * ((y_in + y_out) / 2 - sw), 0.55])
        out.append(I.box(ctop, Rt, (pd[0] * 1.0, (y_out - y_in) / 2, 0.48), I.PAD, chamfer=(0.36, 0.26, 0.3),
                         name='shoulder_pad'))
        Mu, Lu = limb_frame(Sh, E, RC)
        outv = RC[:, 1] * sg - (RC[:, 1] * sg @ Mu[:, 2]) * Mu[:, 2]
        outv = outv / max(float(np.linalg.norm(outv)), 1e-6)
        Rl = np.stack([Mu[:, 2], np.cross(outv, Mu[:, 2]), outv], 1)
        cl = Sh + (E - Sh) * 0.18 + outv * (S['ru'] * 0.75)
        out.append(I.box(cl, Rl, (Lu * 0.2, S['ru'] * 1.0, 0.34), LAME, chamfer=(0.18, 0.2, 0.15), name='shoulder_lame'))
        out.append(I.taper_limb(Sh, E, RU, S['ru'] * 0.9, S['ru'] * 0.68, I.UARM, 'upper_arm', ext=0.05))
        out.append(I.ellip(E, RFa, (S['ru'] * 0.66,) * 3, SUIT, 'elbow'))
        out.append(I.taper_limb(E + (W - E) * 0.08, W, RFa, S['rf'] * 0.95, S['rf'] * 0.75, I.FARM, 'forearm', ext=0.05))
        out.append(I.ellip(W + RFa @ np.array([0, 0, -S['rh'] * 0.6]), RFa,
                           (S['rh'] * 1.0, S['rh'] * 0.88, S['rh'] * 1.1), I.HAND, 'hand'))
    # ---- the helmet: dark, the red visor in its frame, the jaw, ear pieces, the antenna, the lamp on its crown
    Hc, RH = P.head
    hr = np.asarray(S['hr'], float)
    hp = rc.Part(I.helmet_cons(Hc, RH, hr), I.HELMET, 'helmet', sphere=(Hc, float(np.linalg.norm(hr)) + 1e-3))
    hp.low = Hc[2] - float(np.abs(RH[2, :]) @ hr)
    hp.frame = (np.asarray(Hc, float), np.asarray(RH, float))
    out.append(hp)
    # (the concept's visor: a red band across the eyes - at TS's light-blue patch, low on the face, it read as a mouth)
    va, e0, e1 = S.get('lva', 44.0), S.get('le0', -18.0), S.get('le1', 14.0)
    out.append(I.shell_patch(Hc, RH, hr, 0.2, va + 7.0, e0 - 6.0, e1 + 6.0, FRAME, 'visor_frame'))
    out.append(I.shell_patch(Hc, RH, hr, 0.3, va, e0, e1, I.VISOR, 'mask'))
    out.append(I.shell_patch(Hc, RH, hr, 0.22, va + 8.0, e0 - 30.0, e0 - 5.0, I.JAW, 'jaw'))
    for sg, nm in ((-1.0, 'l'), (1.0, 'r')):
        a = RH[:, 1] * sg
        c = Hc + a * hr[1] * 0.98 + RH @ np.array([-hr[0] * 0.1, 0, -hr[2] * 0.15])
        out.append(_cyl(c - a * 0.12, c + a * 0.3, hr[2] * 0.4, EAR, 'ear_' + nm, RH))
    ab = Hc + RH @ np.array([-hr[0] * 0.35, -hr[1] * 0.95, hr[2] * 0.35])
    au = RH @ np.array([-0.2, -0.1, 1.0]); au = au / np.linalg.norm(au)
    au = au + np.array([0.0, 0.0, 0.9]); au = au / np.linalg.norm(au)
    out.append(_cyl(ab - au * 0.1, ab + au * 0.5, 0.24, EAR, 'antenna_base', RH))
    out.append(_cyl(ab + au * 0.4, ab + au * S.get('anl', 4.0), 0.13, ANT, 'antenna', RH))
    lc = Hc + RH @ np.array([hr[0] * 0.15, hr[1] * 0.35, hr[2] * 1.02])
    out.append(I.ellip(lc, RH, (0.32, 0.32, 0.22), LAMP, 'helmet_lamp'))
    # ---- the launcher (inf.py's: TS's light grey tube, dark rims) with the concept's yellow band and a sight
    if rifle and S.get('rifle', 1) > 0.5 and (Q.get('ik', 1.0) > 0.5 or Q.get('gone', 0.0) > 0.5):
        G0, RG = P.rifle
        ax0 = G0 + I.launcher_lift(S, RG)
        x = RG[:, 0]
        back = ax0 - x * S['gg']; front = back + x * S['gl']
        r = S['gt'] / 2.0
        rl = min(S.get('lrim', 0.7), S['gl'] * 0.2)
        for a, b, rr, comp, nm in ((back + x * rl, front - x * rl, r, I.LAUNCHER, 'launcher'),
                                   (back, back + x * rl, r * 1.08, I.LAUNCHER_RIM, 'launcher_back'),
                                   (front - x * rl, front, r * 1.08, I.LAUNCHER_RIM, 'launcher_mouth')):
            out.append(_cyl(a, b, rr, comp, nm, RG))
        bc = front - x * (rl + S['gl'] * 0.08)
        out.append(_cyl(bc - x * 0.35, bc + x * 0.35, r * 1.05, BAND, 'launcher_band', RG))
        # (the sight: a small box on the tube's left, forward of his hands)
        sc = ax0 + x * (S['gl'] * 0.12) - RG[:, 1] * (r + 0.3) + RG[:, 2] * (r * 0.3)
        out.append(I.box(sc, RG, (0.75, 0.28, 0.35), SIGHT, chamfer=(0.08, 0.06, 0.08), name='launcher_sight'))
        out.append(segbox(G0 - x * 0.3, G0 + x * 0.5, 0.5, S.get('lz', 1.25) * 1.1, I.RIFLE_DARK, RG[:, 2],
                          'launcher_grip'))
    return out
