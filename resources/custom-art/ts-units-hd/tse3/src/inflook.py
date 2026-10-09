"""
inflook.py - the Light Infantry's look v2 (the makeover): the same skeleton, pose and fitted sizes as inf.py's soldier,
built as armour rather than rounded blobs, after an ArtStation turnaround of TS's GDI infantry (Luke sent it) with TS's
sprites still the blueprint for where every part is and its colour:

  - the full helmet with its big glowing visor in a dark frame and a round ear piece each side;
  - a chest plate over the dark undersuit, pouches across the belly, pouches on the belt;
  - layered shoulder plates sitting on top of the shoulders (two lames), not balls round the upper arm;
  - the upper arm narrowing to a dark elbow (the undersuit showing between the plates), a green bracer on the forearm,
    gloves;
  - green thigh plates on the outer front of each thigh, knee plates, light grey greaves down the shins, boots with soles;
  - the pack on his back with its flap, the pouch under it;
  - the rifle in parts: stock, pistol grip, receiver with a sight on top, magazine, handguard, barrel and muzzle.

House colour stays plain (no lines or detail on it): its plates read by their shape alone.

    S['look'] = 2 switches inf.parts to this for the Light Infantry kit.
"""
import numpy as np
import rc
import inf as I

# new components (fitting classes in inf.CLASS below; colours in infunit.MAT['e1'])
(ARMOUR, WEBBING, ELBOW, EAR, SOLE, GREAVE, MAGAZINE, THIGHPLATE, PADLAME, BRACER, FLAP) = range(740, 751)
I.CLASS.update({ARMOUR: I.DARK, WEBBING: I.DARK, ELBOW: I.DARK, EAR: I.NAVY, SOLE: I.DARK, GREAVE: I.GREY,
                MAGAZINE: I.DARK, THIGHPLATE: I.GREEN, PADLAME: I.GREEN, BRACER: I.GREEN, FLAP: I.GREY})
HOUSE_EXTRA = (THIGHPLATE, PADLAME, BRACER)


def _part(cons, comp, name, c, rad, frame_R):
    p = rc.Part(cons, comp, name, sphere=(np.asarray(c, float), float(rad) + 1e-3))
    p.low = float(np.asarray(c, float)[2] - rad)
    p.frame = (np.asarray(c, float), np.asarray(frame_R, float))
    return p


def shell(c, R, r, keep, comp, name):
    """the part of an ellipsoid (centre c, axes R, half-sizes r) on the kept side of each plane: keep = [(n, d)] in
    the ellipsoid's own frame, a point x kept where n . x >= d (n unit, x relative to c)."""
    c = np.asarray(c, float); R = np.asarray(R, float); r = np.asarray(r, float)
    cons = [rc.Ellip(c, R, r)]
    for n, d in keep:
        nw = R @ (np.asarray(n, float) / np.linalg.norm(n))
        cons.append(rc.Plane(-nw, -(nw @ c + d)))           # (rc.Plane(n, d) keeps n . x <= d)
    return _part(cons, comp, name, c, float(r.max()), R)


def limb_frame(p0, p1, Rref):
    a = (np.asarray(p1, float) - np.asarray(p0, float))
    L = float(np.linalg.norm(a)); a = a / max(L, 1e-9)
    x = Rref[:, 0] - (Rref[:, 0] @ a) * a
    if np.linalg.norm(x) < 1e-6:
        x = Rref[:, 1] - (Rref[:, 1] @ a) * a
    x = x / np.linalg.norm(x)
    return np.stack([x, np.cross(a, x), a], 1), L


def segbox(p0, p1, w, d, comp, up, name, chamfer=0.0):
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    L = float(np.linalg.norm(p1 - p0))
    R = rc.frame_from(p1 - p0, up)
    return I.box((p0 + p1) / 2, R, (L / 2, w / 2, d / 2), comp, chamfer=chamfer, name=name)


def parts(S, Q, th, rifle=True):
    P = I.Pose(S, Q, th)
    out = []
    P0, B = P.pelvis
    C0, RC = P.chest
    M, RL = P.mid
    # ---- hips and belt (green trousers; the dark belt with pouches)
    out.append(I.ellip(P0 + B @ np.array([0, 0, 0.2]), B, S['pr'], I.PELVIS, 'pelvis'))
    out.append(I.ellip(P0 + B @ np.array([0, 0, 0.55]), B, (S['pr'][0] * 1.05, S['pr'][1] * 1.02, 0.42), I.BELT, 'belt'))
    for sg, nm in ((-1.0, 'l'), (1.0, 'r')):
        c = P0 + B @ np.array([-0.15, sg * S['pr'][1] * 0.98, 0.45])
        out.append(I.box(c, B, (0.55, 0.32, 0.5), WEBBING, chamfer=(0.15, 0.1, 0.15), name='belt_pouch_' + nm))
    # ---- legs
    for side, sg in (('l', -1.0), ('r', 1.0)):
        H, RT, K, RS, A, RF = P.legs[side]
        out.append(I.taper_limb(H, K, RT, S['rt'], S['rt'] * 0.78, I.THIGH, 'thigh', ext=0.3))
        # the thigh plate on its outer front, from below the hip to above the knee
        Mt, L = limb_frame(H, K, RT)
        ct = H + (K - H) * 0.42
        fwd = Mt[:, 0]; out_ = RT[:, 1] * sg
        n = fwd * 0.55 + out_ * 0.85; n = n - (n @ Mt[:, 2]) * Mt[:, 2]; n = n / np.linalg.norm(n)
        R2 = np.stack([n, np.cross(Mt[:, 2], n), Mt[:, 2]], 1)
        out.append(shell(ct, R2, (S['rt'] * 1.08, S['rt'] * 1.08, L * 0.36), [((1, 0, 0), S['rt'] * 0.15)],
                         THIGHPLATE, 'thigh_plate'))
        # knee plate (green), greave (light grey) down the shin's front, boot with its sole
        out.append(I.ellip(K + RS @ np.array([0.35, 0, -0.15]), RS, (S['rs'] * 0.85, S['rs'] * 0.95, S['rs'] * 0.9),
                           I.KNEE, 'knee'))
        out.append(I.taper_limb(K, A, RS, S['rs'], S['rs'] * 0.72, I.SHIN, 'shin', ext=0.2))
        Ms, Ls = limb_frame(K, A, RS)
        cs = K + (A - K) * 0.5
        out.append(shell(cs, Ms, (S['rs'] * 1.07, S['rs'] * 1.05, Ls * 0.42), [((1, 0, 0), S['rs'] * 0.1)],
                         GREAVE, 'greave'))
        c = A + RF @ np.array([0.3 * S['bl'] - 0.15, 0, -S['bh'] * 0.3])
        out.append(I.box(c, RF, (S['bl'] / 2, S['bw'], S['bh'] / 2 * 0.85), I.BOOT, chamfer=(0.35, 0.3, 0.3),
                         name='boot'))
        cso = A + RF @ np.array([0.3 * S['bl'] - 0.1, 0, -S['bh'] * 0.3 - S['bh'] / 2 * 0.85 - 0.08])
        out.append(I.box(cso, RF, (S['bl'] / 2 + 0.08, S['bw'] + 0.06, 0.16), SOLE, chamfer=(0.1, 0.1, 0.05),
                         name='sole'))
    # ---- torso: the undersuit, the chest plate, pouches across the belly
    if Q.get('smid', 0.0):
        out.append(I.ellip(P0 + (M - P0) * 0.75, RL, S['ar'], I.ABDOMEN, 'abdomen'))
    else:
        out.append(I.ellip(P0 + (C0 - P0) * 0.45, RC, S['ar'], I.ABDOMEN, 'abdomen'))
    cc = C0 + RC @ np.array([0, 0, -S['cr'][2] * 0.55])
    cr = np.asarray(S['cr'], float)
    out.append(I.ellip(cc, RC, cr, I.CHEST, 'chest'))
    out.append(I.ellip(cc + RC @ np.array([cr[0] * 0.35, 0, -0.35]), RC,
                       (cr[0] * 0.7 + S['vt'], cr[1] * 0.72, cr[2] * 0.8), I.VEST, 'vest'))
    # (the chest plate: the chest's shell 0.16 proud, its front from the collarbones down to the ribs)
    out.append(shell(cc, RC, cr + 0.16, [((1, 0, 0), cr[0] * 0.2), ((0, 0, -1), -cr[2] * 0.62),
                                         ((0, 0, 1), -cr[2] * 0.52)], ARMOUR, 'chest_plate'))
    # (the back plate, the same behind)
    out.append(shell(cc, RC, cr + 0.12, [((-1, 0, 0), cr[0] * 0.25), ((0, 0, -1), -cr[2] * 0.7),
                                         ((0, 0, 1), -cr[2] * 0.3)], ARMOUR, 'back_plate'))
    for i, y in enumerate((-0.95, 0.0, 0.95)):
        c = cc + RC @ np.array([cr[0] * 0.78, y * cr[1] * 0.55, -cr[2] * 0.78])
        out.append(I.box(c, RC, (0.38, 0.42, 0.5), WEBBING, chamfer=(0.12, 0.12, 0.15), name='belly_pouch_%d' % i))
    # ---- the pack on his back, its flap, the pouch under it
    pk = np.asarray(S['pk'], float)
    pc = cc + RC @ np.array([-cr[0] * 0.85 - pk[0] * 0.3, 0, 0.3])
    out.append(I.box(pc, RC, pk, I.PACK, chamfer=(0.3, 0.35, 0.35), name='pack'))
    out.append(I.box(pc + RC @ np.array([-0.12, 0, pk[2] * 0.62]), RC, (pk[0] * 1.02 + 0.06, pk[1] * 1.04, pk[2] * 0.42),
                     FLAP, chamfer=(0.2, 0.25, 0.2), name='pack_flap'))
    po = np.asarray(S['po'], float)
    out.append(I.box(cc + RC @ np.array([-cr[0] * 0.75, 0, -cr[2] * 0.85]), RC, po * np.array([0.9, 0.85, 0.8]),
                     I.POUCH, chamfer=(0.25, 0.3, 0.25), name='pouch'))
    # ---- arms: the shoulder plates (two lames sitting on the shoulder), the upper arm narrowing to a dark elbow, the
    # green bracer on the forearm, the glove
    pd = np.asarray(S['pd'], float)
    for side, sg in (('l', -1.0), ('r', 1.0)):
        Sh, RU, E, RFa, W = P.arms[side]
        # (two angular plates, as the reference's pauldrons: the top one over the shoulder sloping out and down, the
        # lame below it further out and steeper; together as wide as TS's 3 px shoulder)
        # (the top plate from beside the collar out just past the shoulder, sloping down outward; the lame under its
        # outer edge, steeper, over the top of the upper arm)
        sw = S['sw']
        y_in, y_out = 0.62 * sw, sw + 0.6
        Rt = RC @ I.Rx(sg * 24.0)
        ctop = Sh + RC @ np.array([0.0, sg * ((y_in + y_out) / 2 - sw), 0.48])
        out.append(I.box(ctop, Rt, (pd[0] * 0.85, (y_out - y_in) / 2, 0.34), I.PAD, chamfer=(0.3, 0.2, 0.3),
                         name='shoulder_pad'))
        # (the lame rides on the upper arm: along the bone just below the shoulder, on its outer side - fixed to the
        # chest it stuck out like a fin whenever the arm reached forward)
        Mu, Lu = limb_frame(Sh, E, RC)
        outv = RC[:, 1] * sg - (RC[:, 1] * sg @ Mu[:, 2]) * Mu[:, 2]
        outv = outv / max(float(np.linalg.norm(outv)), 1e-6)
        Rl = np.stack([Mu[:, 2], np.cross(outv, Mu[:, 2]), outv], 1)       # (along the bone, across, out)
        clame = Sh + (E - Sh) * 0.22 + outv * (S['ru'] * 0.62)
        out.append(I.box(clame, Rl, (Lu * 0.2, S['ru'] * 0.7, 0.26), PADLAME, chamfer=(0.2, 0.2, 0.15),
                         name='shoulder_lame'))
        out.append(I.taper_limb(Sh, E, RU, S['ru'] * 0.85, S['ru'] * 0.62, I.UARM, 'upper_arm', ext=0.05))
        out.append(I.ellip(E, RFa, (S['ru'] * 0.6,) * 3, ELBOW, 'elbow'))
        out.append(I.taper_limb(E, W, RFa, S['rf'] * 0.72, S['rf'] * 0.6, ELBOW, 'forearm_suit', ext=0.05))
        Mf, Lf = limb_frame(E, W, RFa)
        out.append(I.taper_limb(E + (W - E) * 0.22, W - (W - E) * 0.06, RFa, S['rf'] * 1.02, S['rf'] * 0.8, BRACER,
                                'bracer', ext=0.0))
        out.append(I.ellip(W + RFa @ np.array([0, 0, -S['rh'] * 0.6]), RFa,
                           (S['rh'] * 1.0, S['rh'] * 0.85, S['rh'] * 1.15), I.HAND, 'glove'))
    # ---- the helmet: the shell, the glowing visor in its dark frame, the jaw, an ear piece each side
    Hc, RH = P.head
    hr = np.asarray(S['hr'], float)
    hp = rc.Part(I.helmet_cons(Hc, RH, hr), I.HELMET, 'helmet', sphere=(Hc, float(np.linalg.norm(hr)) + 1e-3))
    hp.low = Hc[2] - float(np.abs(RH[2, :]) @ hr)
    hp.frame = (np.asarray(Hc, float), np.asarray(RH, float))
    out.append(hp)
    out.append(I.shell_patch(Hc, RH, hr, S['fd'] * 0.55, S['fva'] + 7.0, S['fe0'] - 4.0, S['fe1'] + 7.0, I.JAW,
                             'visor_frame'))
    out.append(I.shell_patch(Hc, RH, hr, S['fd'], S['fva'], S['fe0'], S['fe1'], I.VISOR, 'mask'))
    out.append(I.shell_patch(Hc, RH, hr, S['fd'] * 0.6, S['fva'] + 8.0, S['fe0'] - S['fj'], S['fe0'], I.JAW, 'jaw'))
    for sg, nm in ((-1.0, 'l'), (1.0, 'r')):
        a = RH[:, 1] * sg
        c = Hc + a * (hr[1] * 1.02) + RH @ np.array([-hr[0] * 0.1, 0, -hr[2] * 0.2])
        p = rc.cylinder(c - a * 0.12, c + a * 0.28, hr[2] * 0.42, EAR, 'ear_' + nm)
        p.low = c[2] - hr[2] * 0.42
        p.frame = (c, RH)
        out.append(p)
    # ---- the rifle in parts
    if rifle and S.get('rifle', 1) > 0.5 and (Q.get('ik', 1.0) > 0.5 or Q.get('gone', 0.0) > 0.5):
        G0, RG = P.rifle
        x, z = RG[:, 0], RG[:, 2]
        back = G0 - x * S['gg']
        gl, gt, gs = S['gl'], S['gt'], S['gs']
        at = lambda u, h=0.0: back + x * u + z * h
        out.append(segbox(at(0.0, -0.1), at(3.0, 0.0), gt * 0.8, gs * 0.85, I.RIFLE_DARK, z, 'stock',
                          chamfer=(0.1, 0.15, 0.2)))
        out.append(segbox(at(2.7, 0.05), at(6.3, 0.05), gt, gs, I.RIFLE_DARK, z, 'receiver', chamfer=(0.1, 0.12, 0.15)))
        out.append(segbox(at(3.4, gs * 0.5 + 0.15), at(5.6, gs * 0.5 + 0.15), gt * 0.55, 0.32, MAGAZINE, z, 'sight'))
        out.append(segbox(at(3.3, -gs * 0.35), at(2.8, -gs * 0.35 - 1.3), gt * 0.7, 0.6, I.RIFLE_DARK, x, 'grip'))
        out.append(segbox(at(5.0, -gs * 0.4), at(5.4, -gs * 0.4 - 1.5), gt * 0.75, 0.75, MAGAZINE, x, 'magazine'))
        out.append(segbox(at(6.2, 0.1), at(9.4, 0.1), gt * 0.95, gs * 0.72, I.RIFLE, z, 'handguard',
                          chamfer=(0.05, 0.15, 0.15)))
        bar = rc.cylinder(at(9.3, 0.15), at(gl, 0.15), 0.24, I.RIFLE, 'barrel')
        bar.low = float(min(at(9.3, 0.15)[2], at(gl, 0.15)[2]) - 0.24)
        bar.frame = (at(10.5, 0.15), RG)
        out.append(bar)
        mz = rc.cylinder(at(gl - 0.7, 0.15), at(gl, 0.15), 0.34, I.RIFLE_DARK, 'muzzle')
        mz.low = float(min(at(gl - 0.7, 0.15)[2], at(gl, 0.15)[2]) - 0.34)
        mz.frame = (at(gl - 0.35, 0.15), RG)
        out.append(mz)
    return out
