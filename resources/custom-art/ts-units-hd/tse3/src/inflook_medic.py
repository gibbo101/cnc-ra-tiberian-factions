"""
inflook_medic.py - the Medic's look v2 (the makeover): the same skeleton, poses and fitted sizes as inf.py's Medic, built
as armour in the style of the soldiers' makeovers (inflook.py, inflook_e2.py, both signed off).  TS's sprites set where
every part is and its colour:

  - the light grey full helmet, its dark glass faceplate in a dark frame (TS: dark grey looking ahead), an ear piece
    each side, the red cross on its crown;
  - light grey chest and back plates over the dark suit, the red cross on his upper back (TS's back view), a row of
    medical pouches across his belly, a dark belt;
  - shoulder pads of two plates in plain house green (TS's big green pads);
  - his upper arms in the dark suit with a broad orange band round each (TS's orange upper arms: the medic's armband),
    dark elbows, light grey bracers, light grey gloves;
  - his hips orange behind and dark in front (TS), the thighs house green in front with a plate, orange behind (TS's
    back view), orange knee pads, light grey greaves, light grey boots with dark soles;
  - the case (TS's grey case, a red cross on each broad face) with a carry handle, latches and a dark band round it;
    in his hand, pushed along the ground as he crawls, set down or dropped as before.

    S['look'] = 2 switches inf.parts to this for the Medic's kit.
"""
import numpy as np
import rc
import inf as I
from inflook import shell, limb_frame, segbox
from inflook_e2 import _cyl

# components (fitting classes below; colours in infunit.MAT_MEDIC_LOOK2)
(PLATE, WEB, LAME, THIGHPL, FRAME, EAR, BAND, BRACER, GREAVE, SOLE, HANDLE, LATCH, SUIT) = range(810, 823)
I.CLASS.update({PLATE: I.GREY, WEB: I.GREY, LAME: I.GREEN, THIGHPL: I.GREEN, FRAME: I.DARK, EAR: I.GREY,
                BAND: I.ORANGE, BRACER: I.GREY, GREAVE: I.GREY, SOLE: I.DARK, HANDLE: I.DARK, LATCH: I.DARK,
                SUIT: I.DARK})


def parts(S, Q, th, rifle=True):
    P = I.Pose(S, Q, th)
    face = float(th)
    out = []
    P0, B = P.pelvis
    C0, RC = P.chest
    M, RL = P.mid
    pr = np.asarray(S['pr'], float)
    # ---- hips: orange behind, dark in front (TS); the dark belt
    pel = I.ellip(P0 + B @ np.array([0, 0, 0.2]), B, pr, I.PELVIS, 'pelvis')
    out += I.split(pel, B[:, 0], S.get('psp', 0.3) * pr[0], I.POUCH, 'hips')
    out.append(I.ellip(P0 + B @ np.array([0, 0, 0.55]), B, (pr[0] * 1.05, pr[1] * 1.02, 0.42), I.BELT, 'belt'))
    # ---- legs
    for side, sg in (('l', -1.0), ('r', 1.0)):
        H, RT, K, RS, A, RF = P.legs[side]
        th_ = I.taper_limb(H, K, RT, S['rt'], S['rt'] * 0.8, I.THIGH, 'thigh', ext=0.3)
        out += I.split(th_, RT[:, 0], S.get('tsp', 0.0) * S['rt'], I.POUCH, 'thigh_back')
        Mt, L = limb_frame(H, K, RT)
        fwd = Mt[:, 0]; side_v = RT[:, 1] * sg
        n = fwd * 0.55 + side_v * 0.85; n = n - (n @ Mt[:, 2]) * Mt[:, 2]; n = n / np.linalg.norm(n)
        R2 = np.stack([n, np.cross(Mt[:, 2], n), Mt[:, 2]], 1)
        out.append(shell(H + (K - H) * 0.42, R2, (S['rt'] * 1.08, S['rt'] * 1.08, L * 0.34), [((1, 0, 0), S['rt'] * 0.15)],
                         THIGHPL, 'thigh_plate'))
        Ms, Ls = limb_frame(K, A, RS)
        out.append(shell(K + RS @ np.array([-0.1, 0, 0.15]), Ms, (S['rs'] * 1.4, S['rs'] * 1.1, S['rs'] * 1.3),
                         [((1, 0, 0), S['rs'] * 0.7)], I.KNEE, 'knee'))
        out.append(I.taper_limb(K, A, RS, S['rs'], S['rs'] * 0.75, I.SHIN, 'shin', ext=0.2))
        out.append(shell(K + (A - K) * 0.55, Ms, (S['rs'] * 1.08, S['rs'] * 1.06, Ls * 0.38), [((1, 0, 0), S['rs'] * 0.1)],
                         GREAVE, 'greave'))
        c = A + RF @ np.array([0.3 * S['bl'] - 0.15, 0, -S['bh'] * 0.3])
        out.append(I.box(c, RF, (S['bl'] / 2, S['bw'], S['bh'] / 2 * 0.85), I.BOOT, chamfer=(0.35, 0.3, 0.3),
                         name='boot'))
        cso = A + RF @ np.array([0.3 * S['bl'] - 0.1, 0, -S['bh'] * 0.3 - S['bh'] / 2 * 0.85 - 0.08])
        out.append(I.box(cso, RF, (S['bl'] / 2 + 0.08, S['bw'] + 0.06, 0.16), SOLE, chamfer=(0.1, 0.1, 0.05),
                         name='sole'))
    # ---- torso: the dark suit, the light grey plates, pouches across the belly, the cross on his back
    if Q.get('smid', 0.0):
        ac, RA = P0 + (M - P0) * 0.75, RL
    else:
        ac, RA = P0 + (C0 - P0) * 0.45, RC
    out.append(I.ellip(ac, RA, S['ar'], SUIT, 'abdomen'))
    cc = C0 + RC @ np.array([0, 0, -S['cr'][2] * 0.55])
    cr = np.asarray(S['cr'], float)
    out.append(I.ellip(cc, RC, cr, I.CHEST, 'chest'))
    out.append(I.ellip(cc + RC @ np.array([cr[0] * 0.35, 0, -0.35]), RC,
                       (cr[0] * 0.7 + S['vt'], cr[1] * 0.72, cr[2] * 0.8), I.VEST, 'vest'))
    out.append(shell(cc, RC, cr + 0.16, [((1, 0, 0), cr[0] * 0.15), ((0, 0, -1), -cr[2] * 0.64),
                                         ((0, 0, 1), cr[2] * 0.1)], PLATE, 'chest_plate'))
    out.append(shell(cc, RC, cr + 0.12, [((-1, 0, 0), cr[0] * 0.2), ((0, 0, -1), -cr[2] * 0.7),
                                         ((0, 0, 1), cr[2] * 0.25)], PLATE, 'back_plate'))
    for i, y in enumerate((-0.95, 0.0, 0.95)):
        c = cc + RC @ np.array([cr[0] * 0.8, y * cr[1] * 0.52, -cr[2] * 0.66])
        out.append(I.box(c, RC, (0.4, 0.46, 0.5), WEB, chamfer=(0.12, 0.14, 0.15), name='belly_pouch_%d' % i))
    out += I.cross(cc + RC @ np.array([-cr[0] - 0.08, 0.0, S['crz']]), -RC[:, 0], RC[:, 2], S['crs'], S['crw'], 0.12,
                   I.CROSS, 'back_cross_')
    # ---- arms: green shoulder plates, upper arms in the dark suit with an orange armband, light grey bracers, gloves
    pd = np.asarray(S['pd'], float)
    for side, sg in (('l', -1.0), ('r', 1.0)):
        Sh, RU, E, RFa, W = P.arms[side]
        sw = S['sw']
        # (TS's pads are big: 3 px each side, the widest part of him - wider, deeper and thicker than the soldiers')
        y_in, y_out = 0.5 * sw, sw + 1.05
        Rt = RC @ I.Rx(sg * 24.0)
        ctop = Sh + RC @ np.array([0.0, sg * ((y_in + y_out) / 2 - sw), 0.55])
        out.append(I.box(ctop, Rt, (pd[0] * 1.0, (y_out - y_in) / 2, 0.5), I.PAD, chamfer=(0.38, 0.28, 0.32),
                         name='shoulder_pad'))
        Mu, Lu = limb_frame(Sh, E, RC)
        outv = RC[:, 1] * sg - (RC[:, 1] * sg @ Mu[:, 2]) * Mu[:, 2]
        outv = outv / max(float(np.linalg.norm(outv)), 1e-6)
        Rl = np.stack([Mu[:, 2], np.cross(outv, Mu[:, 2]), outv], 1)
        cl = Sh + (E - Sh) * 0.18 + outv * (S['ru'] * 0.75)
        out.append(I.box(cl, Rl, (Lu * 0.2, S['ru'] * 1.0, 0.34), LAME, chamfer=(0.2, 0.24, 0.16), name='shoulder_lame'))
        out.append(I.taper_limb(Sh, E, RU, S['ru'] * 0.88, S['ru'] * 0.66, SUIT, 'upper_arm', ext=0.05))
        # (the armband: TS's orange upper arm, a broad band round it)
        b0, b1 = Sh + (E - Sh) * 0.3, Sh + (E - Sh) * 0.86
        out.append(I.taper_limb(b0, b1, RU, S['ru'] * 0.98, S['ru'] * 0.88, BAND, 'armband', ext=0.0))
        out.append(I.ellip(E, RFa, (S['ru'] * 0.62,) * 3, SUIT, 'elbow'))
        out.append(I.taper_limb(E, W, RFa, S['rf'] * 0.72, S['rf'] * 0.6, SUIT, 'forearm_suit', ext=0.05))
        out.append(I.taper_limb(E + (W - E) * 0.25, W - (W - E) * 0.05, RFa, S['rf'] * 1.0, S['rf'] * 0.82, BRACER,
                                'forearm', ext=0.0))
        out.append(I.ellip(W + RFa @ np.array([0, 0, -S['rh'] * 0.6]), RFa,
                           (S['rh'] * 1.05, S['rh'] * 0.9, S['rh'] * 1.15), I.HAND, 'hand'))
    # ---- the helmet: light grey, the dark glass faceplate in its frame, the jaw, ear pieces, the cross on the crown
    Hc, RH = P.head
    hr = np.asarray(S['hr'], float)
    hp = rc.Part(I.helmet_cons(Hc, RH, hr), I.HELMET, 'helmet', sphere=(Hc, float(np.linalg.norm(hr)) + 1e-3))
    hp.low = Hc[2] - float(np.abs(RH[2, :]) @ hr)
    hp.frame = (np.asarray(Hc, float), np.asarray(RH, float))
    out.append(hp)
    # (the references' visor: blue glass across the helmet's front, the Engineer's size)
    va, e0, e1 = S.get('lva', 38.0), S.get('le0', -22.0), S.get('le1', 15.0)
    out.append(I.shell_patch(Hc, RH, hr, 0.2, va + 7.0, e0 - 5.0, e1 + 7.0, FRAME, 'visor_frame'))
    out.append(I.shell_patch(Hc, RH, hr, 0.32, va, e0, e1, I.VISOR, 'mask'))
    out.append(I.shell_patch(Hc, RH, hr, 0.22, va + 8.0, e0 - 26.0, e0 - 4.0, FRAME, 'jaw'))
    for sg, nm in ((-1.0, 'l'), (1.0, 'r')):
        a = RH[:, 1] * sg
        c = Hc + a * hr[1] * 0.98 + RH @ np.array([-hr[0] * 0.1, 0, -hr[2] * 0.15])
        out.append(_cyl(c - a * 0.12, c + a * 0.3, hr[2] * 0.42, EAR, 'ear_' + nm, RH))
    out += I.crown_cross(Hc, RH, hr, S.get('hcs', 0.5), S.get('hcw', 0.3), 0.06, I.CROSS, 'helmet_cross_')
    # ---- the case (inf.py's Medic case: in his hand, along the ground as he crawls, set down or dropped)
    Sh, RU, E, RFa, W = P.arms['l' if Q.get('tbl', 0.0) > 0.5 else 'r']
    mk = np.asarray(S['mk'], float)
    top = W + RFa @ np.array([0.0, 0.0, -S['rh'] - S['mkz']])
    c = top + RFa @ np.array([0.0, 0.0, -mk[2]])
    Rb = RFa
    g = float(np.clip(Q.get('tbg', 0.0), 0.0, 1.0))
    if g > 0.0:
        fwd = np.array([np.cos(np.deg2rad(face)), np.sin(np.deg2rad(face)), 0.0])
        hz = fwd / max(float(np.linalg.norm(fwd)), 1e-6)
        zz = np.array([0.0, 0.0, 1.0]); xx = np.cross(zz, hz)
        Rg = np.stack([xx, np.cross(zz, xx), zz], 1)
        cg = W + hz * (mk[1] + S['rh'])
        cg[2] = min(p.low for p in out) + mk[2]
        c = c * (1.0 - g) + cg * g
        Mx = RFa * (1.0 - g) + Rg * g
        u_, _, vt_ = np.linalg.svd(Mx)
        Rb = u_ @ vt_
    f = float(np.clip(Q.get('cfix', 0.0), 0.0, 1.0))
    if f > 0.0:
        a = np.deg2rad(Q.get('cfa', -90.0))
        yv = np.array([np.cos(a), np.sin(a), 0.0]); zv = np.array([0.0, 0.0, 1.0])
        Rf = np.stack([np.cross(yv, zv), yv, zv], 1)
        t = np.deg2rad(Q.get('cft', 0.0))
        Rf = Rf @ np.array([[1.0, 0.0, 0.0], [0.0, np.cos(t), -np.sin(t)], [0.0, np.sin(t), np.cos(t)]])
        cf = np.array([Q.get('cfx', 0.0), Q.get('cfy', 0.0), min(p.low for p in out) + float(np.abs(Rf[2, :]) @ mk)])
        c = c * (1.0 - f) + cf * f
        Mx = Rb * (1.0 - f) + Rf * f
        u_, _, vt_ = np.linalg.svd(Mx)
        Rb = u_ @ vt_
    out.append(I.box(c, Rb, mk, I.MEDKIT, chamfer=(0.2, 0.2, 0.2), name='medkit'))
    # (its lid's seam; the references' red corner brackets on both broad faces)
    out.append(I.box(c + Rb @ np.array([0.0, 0.0, mk[2] * 0.6]), Rb, (mk[0] + 0.03, mk[1] + 0.03, 0.06), LATCH,
                     name='medkit_seam'))
    L_, W_ = min(mk[0], mk[2]) * 0.38, min(mk[0], mk[2]) * 0.09
    for sg in (-1.0, 1.0):
        for cx in (-1.0, 1.0):
            for cz in (-1.0, 1.0):
                corner = c + Rb @ np.array([cx * (mk[0] - 0.22), sg * (mk[1] + 0.04), cz * (mk[2] - 0.22)])
                out.append(I.box(corner + Rb @ np.array([-cx * L_ / 2, 0, -cz * W_ / 2]), Rb, (L_ / 2, 0.05, W_ / 2),
                                 I.CROSS, name='case_bracket'))
                out.append(I.box(corner + Rb @ np.array([-cx * W_ / 2, 0, -cz * L_ / 2]), Rb, (W_ / 2, 0.05, L_ / 2),
                                 I.CROSS, name='case_bracket'))
    for sgx in (-1.0, 1.0):
        out.append(I.box(c + Rb @ np.array([sgx * mk[0] * 0.5, 0.0, mk[2] + 0.25]), Rb, (0.13, 0.13, 0.28), HANDLE,
                         name='medkit_handle_post'))
    out.append(I.box(c + Rb @ np.array([0.0, 0.0, mk[2] + 0.5]), Rb, (mk[0] * 0.5 + 0.13, 0.13, 0.11), HANDLE,
                     name='medkit_handle'))
    for sg, nm in ((1.0, 'r'), (-1.0, 'l')):
        out += I.cross(c + Rb[:, 1] * sg * mk[1], Rb[:, 1] * sg, Rb[:, 2], min(mk[0], mk[2]) * 0.55,
                       min(mk[0], mk[2]) * 0.18, 0.1, I.CROSS, 'case_cross_%s_' % nm)
    return out
