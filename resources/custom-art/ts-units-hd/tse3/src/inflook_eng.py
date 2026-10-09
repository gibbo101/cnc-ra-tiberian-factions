"""
inflook_eng.py - the Engineer's look v2 (the makeover): the same skeleton, poses and fitted sizes as inf.py's Engineer,
rebuilt after the C&C Reborn "GDI Engineer (Old)" Luke picked ("I quite like design wise"), mixed with the hazard-
striped case of TS's own cameo, its stripes in house colour (Luke), and off TS's bright yellow onto the Reborn suit's
dark ochre (Luke: "depart from the bright yellow"; the GDI ochre of the HD buildings' collars).  TS's remap areas stay
house green (his upper arms, his thighs), so he shows his side as TS's does:

  - the full helmet in ochre with the big glowing visor in a dark frame (the Light Infantry's and Disc Thrower's), a
    round ear piece each side, a ridge over the crown, a short whip antenna from its left side;
  - the flat box pack in ochre with dark edging, a round gauge and a slot on its back, its shoulder straps;
  - the dark suit; a segmented ochre chest: the chest plate and two plates down the belly, the suit between; a dark
    belt with a light grey buckle;
  - shoulder plates: a dark plate on top with house-green hazard stripes across it (the Reborn engineer's striped
    shoulders), two ochre plates below it on the upper arm; green upper arms; dark elbows; ochre gauntlets; dark
    gloves;
  - green thighs with two plates down their outer front; ochre knee pads; ochre boot covers up the shins with a light
    grey shin guard; dark boots with soles;
  - the case in his hand: dark, house-green hazard stripes on both its broad faces (TS's cameo), a light grey lid
    band, handle and latches.

    S['look'] = 2 switches inf.parts to this for the Engineer's kit (infunit.LOOK2 its colours).
"""
import numpy as np
import rc
import inf as I
from inflook import shell, limb_frame, segbox
from inflook_e2 import _cyl, _rounded_box

# components (fitting classes below; colours in infunit.MAT_ENG_LOOK2)
(VESTPAD, WEB, LAME, THIGHPL, FACEPANEL, LENS, RIM, RESP, CANISTER, COLLAR, HANDLE, LATCH, STRAP, SOLE, CUFF,
 SUIT, HAZ, CHESTPL, DIAL, SLOT, ANT, EAR, GREAVE) = range(780, 803)
I.CLASS.update({VESTPAD: I.DARK, WEB: I.DARK, LAME: I.YELLOW, THIGHPL: I.GREEN, FACEPANEL: I.DARK, LENS: I.DARK,
                RIM: I.DARK, RESP: I.GREY, CANISTER: I.GREY, COLLAR: I.DARK, HANDLE: I.GREY, LATCH: I.DARK,
                STRAP: I.DARK, SOLE: I.DARK, CUFF: I.DARK, SUIT: I.DARK, HAZ: I.GREEN, CHESTPL: I.YELLOW, DIAL: I.GREY,
                SLOT: I.DARK, ANT: 6, EAR: I.DARK, GREAVE: I.GREY})


def face_stripes(c, R, h, ax, sg, n, comp, name, ang=45.0, d=0.07, fill=0.5):
    """hazard stripes on a box's face (centre c, frame R, half sizes h): the face across R's axis ax on side sg; n
    stripes at ang degrees, fill of the pitch wide, d proud, clipped to the face."""
    c = np.asarray(c, float); R = np.asarray(R, float); h = np.asarray(h, float)
    o = [k for k in range(3) if k != ax]
    nrm, u, v = R[:, ax] * sg, R[:, o[0]], R[:, o[1]]
    hu, hv = h[o[0]], h[o[1]]
    fc = c + nrm * h[ax]
    a = np.deg2rad(ang)
    along = u * np.cos(a) + v * np.sin(a)
    across = -u * np.sin(a) + v * np.cos(a)
    span = hu * abs(np.sin(a)) + hv * abs(np.cos(a))
    pitch = 2 * span / n
    L = float(np.hypot(hu, hv)) * 1.5
    out = []
    for i in range(n):
        sc = fc + across * (-span + (i + 0.5) * pitch)
        Rs = np.stack([along, across, nrm], 1)
        cons = rc.box_planes(sc, Rs, (L, pitch * fill / 2, 5.0))
        cons += [rc.Plane(u, u @ fc + hu), rc.Plane(-u, -(u @ fc) + hu), rc.Plane(v, v @ fc + hv),
                 rc.Plane(-v, -(v @ fc) + hv), rc.Plane(nrm, nrm @ fc + d), rc.Plane(-nrm, -(nrm @ fc) + 0.03)]
        p = rc.Part(cons, comp, '%s_%d' % (name, i), sphere=(fc, float(np.hypot(hu, hv)) + d + 1e-3))
        p.low = float(fc[2] - abs(R[2, o[0]]) * hu - abs(R[2, o[1]]) * hv - d)
        p.frame = (fc, R)
        out.append(p)
    return out


def parts(S, Q, th, rifle=True):
    P = I.Pose(S, Q, th)
    face = float(th)
    out = []
    P0, B = P.pelvis
    C0, RC = P.chest
    M, RL = P.mid
    pr = np.asarray(S['pr'], float)
    # ---- hips (the dark suit), the dark belt, its light grey buckle
    out.append(I.ellip(P0 + B @ np.array([0, 0, 0.2]), B, pr, I.PELVIS, 'pelvis'))
    out.append(I.ellip(P0 + B @ np.array([0, 0, 0.55]), B, (pr[0] * 1.05, pr[1] * 1.02, 0.45), I.BELT, 'belt'))
    out.append(I.box(P0 + B @ np.array([pr[0] * 1.0, 0, 0.55]), B, (0.2, 0.7, 0.42), HANDLE, chamfer=(0.06, 0.15, 0.12),
                     name='buckle'))
    # ---- legs
    for side, sg in (('l', -1.0), ('r', 1.0)):
        H, RT, K, RS, A, RF = P.legs[side]
        out.append(I.taper_limb(H, K, RT, S['rt'], S['rt'] * 0.8, I.THIGH, 'thigh', ext=0.3))
        Mt, L = limb_frame(H, K, RT)
        fwd = Mt[:, 0]; side_v = RT[:, 1] * sg
        n = fwd * 0.55 + side_v * 0.85; n = n - (n @ Mt[:, 2]) * Mt[:, 2]; n = n / np.linalg.norm(n)
        R2 = np.stack([n, np.cross(Mt[:, 2], n), Mt[:, 2]], 1)
        # (two plates down the thigh, a dark seam between: the Reborn suit's segmented thighs)
        for j, (t, hl) in enumerate(((0.27, 0.17), (0.63, 0.15))):
            out.append(shell(H + (K - H) * t, R2, (S['rt'] * 1.1, S['rt'] * 1.1, L * hl), [((1, 0, 0), S['rt'] * 0.15)],
                             THIGHPL, 'thigh_plate_%d' % j))
        Ms, Ls = limb_frame(K, A, RS)
        out.append(shell(K + RS @ np.array([-0.1, 0, 0.15]), Ms, (S['rs'] * 1.35, S['rs'] * 1.08, S['rs'] * 1.25),
                         [((1, 0, 0), S['rs'] * 0.7)], I.KNEE, 'knee'))
        out.append(I.taper_limb(K, A, RS, S['rs'], S['rs'] * 0.85, I.SHIN, 'shin', ext=0.2))
        out.append(shell(K + (A - K) * 0.5, Ms, (S['rs'] * 1.1, S['rs'] * 0.8, Ls * 0.33), [((1, 0, 0), S['rs'] * 0.35)],
                         GREAVE, 'shin_guard'))
        c = A + RF @ np.array([0.3 * S['bl'] - 0.15, 0, -S['bh'] * 0.3])
        out.append(I.box(c, RF, (S['bl'] / 2, S['bw'], S['bh'] / 2 * 0.85), I.BOOT, chamfer=(0.35, 0.3, 0.3),
                         name='boot'))
        cso = A + RF @ np.array([0.3 * S['bl'] - 0.1, 0, -S['bh'] * 0.3 - S['bh'] / 2 * 0.85 - 0.08])
        out.append(I.box(cso, RF, (S['bl'] / 2 + 0.08, S['bw'] + 0.06, 0.16), SOLE, chamfer=(0.1, 0.1, 0.05),
                         name='sole'))
    # ---- torso: the dark suit, the ochre chest plate and belly plates, the collar
    if Q.get('smid', 0.0):
        ac, RA = P0 + (M - P0) * 0.75, RL
    else:
        ac, RA = P0 + (C0 - P0) * 0.45, RC
    ar = np.asarray(S['ar'], float)
    out.append(I.ellip(ac, RA, ar, I.ABDOMEN, 'abdomen'))
    cc = C0 + RC @ np.array([0, 0, -S['cr'][2] * 0.55])
    cr = np.asarray(S['cr'], float)
    out.append(I.ellip(cc, RC, cr, I.CHEST, 'chest'))
    out.append(I.ellip(cc + RC @ np.array([cr[0] * 0.35, 0, -0.35]), RC,
                       (cr[0] * 0.7 + S['vt'], cr[1] * 0.72, cr[2] * 0.8), I.VEST, 'vest'))
    out.append(shell(cc, RC, cr + 0.18, [((1, 0, 0), cr[0] * 0.12), ((0, 0, -1), -cr[2] * 0.64),
                                         ((0, 0, 1), cr[2] * 0.0)], CHESTPL, 'chest_plate'))
    out.append(shell(cc, RC, cr + 0.12, [((-1, 0, 0), cr[0] * 0.25), ((0, 0, -1), -cr[2] * 0.7),
                                         ((0, 0, 1), -cr[2] * 0.3)], CHESTPL, 'back_plate'))
    out.append(shell(cc, RC, cr + 0.15, [((1, 0, 0), cr[0] * 0.2), ((0, 0, -1), cr[2] * 0.1),
                                         ((0, 0, 1), -cr[2] * 0.4)], CHESTPL, 'belly_plate_0'))
    out.append(shell(ac, RA, ar + 0.14, [((1, 0, 0), ar[0] * 0.15), ((0, 0, -1), -ar[2] * 0.3),
                                         ((0, 0, 1), -ar[2] * 0.15)], CHESTPL, 'belly_plate_1'))
    out.append(I.ellip(C0 + RC @ np.array([0.1, 0, 0.15]), RC, (cr[0] * 0.55, cr[1] * 0.55, 0.45), COLLAR, 'collar'))
    # ---- the flat box pack: ochre, dark edging, the gauge and the slot on its back; its shoulder straps
    pk = np.asarray(S['pk'], float)
    pc = cc + RC @ np.array([-cr[0] * 0.85 - pk[0] * 0.3, 0, 0.3])
    out.append(I.box(pc, RC, pk, I.PACK, chamfer=(0.18, 0.22, 0.22), name='pack'))
    # (its edging: a dark frame round the back face, a little proud)
    for sg in (-1.0, 1.0):
        out.append(I.box(pc + RC @ np.array([-pk[0] * 0.6, sg * (pk[1] - 0.12), 0]), RC, (pk[0] * 0.45, 0.16, pk[2] + 0.05),
                         STRAP, chamfer=(0.05, 0.05, 0.05), name='pack_edge'))
        out.append(I.box(pc + RC @ np.array([-pk[0] * 0.6, 0, sg * (pk[2] - 0.12)]), RC, (pk[0] * 0.45, pk[1], 0.16),
                         STRAP, chamfer=(0.05, 0.05, 0.05), name='pack_edge'))
    gc = pc + RC @ np.array([-pk[0], 0, pk[2] * 0.25])
    gr = min(pk[1], pk[2]) * 0.42
    out.append(_cyl(gc - RC[:, 0] * 0.02, gc - RC[:, 0] * 0.18, gr, STRAP, 'gauge_rim', RC))
    out.append(_cyl(gc - RC[:, 0] * 0.1, gc - RC[:, 0] * 0.24, gr * 0.72, DIAL, 'gauge', RC))
    out.append(I.box(pc + RC @ np.array([-pk[0] - 0.02, 0, -pk[2] * 0.42]), RC, (0.08, pk[1] * 0.55, pk[2] * 0.09),
                     SLOT, name='pack_slot'))
    for sg in (-1.0, 1.0):
        a = C0 + RC @ np.array([-cr[0] * 0.5, sg * cr[1] * 0.45, 0.25])
        b = C0 + RC @ np.array([cr[0] * 0.55, sg * cr[1] * 0.45, 0.05])
        d = cc + RC @ np.array([cr[0] * 1.05, sg * cr[1] * 0.42, -cr[2] * 0.4])
        out.append(segbox(a, b, 0.55, 0.3, STRAP, RC[:, 2], 'shoulder_strap'))
        out.append(segbox(b, d, 0.55, 0.25, STRAP, RC[:, 0], 'chest_strap'))
    # ---- arms: the striped shoulder plate, two ochre plates on the upper arm, green upper arms, dark elbows, ochre
    # gauntlets, dark gloves
    pd = np.asarray(S['pd'], float)
    for side, sg in (('l', -1.0), ('r', 1.0)):
        Sh, RU, E, RFa, W = P.arms[side]
        sw = S['sw']
        y_in, y_out = 0.6 * sw, sw + 0.75
        Rt = RC @ I.Rx(sg * 24.0)
        ctop = Sh + RC @ np.array([0.0, sg * ((y_in + y_out) / 2 - sw), 0.55])
        ht = np.array([pd[0] * 0.8, (y_out - y_in) / 2, 0.36])
        out.append(I.box(ctop, Rt, ht, STRAP, chamfer=(0.25, 0.18, 0.2), name='shoulder_pad'))
        out += face_stripes(ctop, Rt, ht * np.array([0.88, 0.9, 1.0]), 2, 1.0, 4, HAZ, 'shoulder_stripe', ang=55.0 * sg)
        Mu, Lu = limb_frame(Sh, E, RC)
        outv = RC[:, 1] * sg - (RC[:, 1] * sg @ Mu[:, 2]) * Mu[:, 2]
        outv = outv / max(float(np.linalg.norm(outv)), 1e-6)
        Rl = np.stack([Mu[:, 2], np.cross(outv, Mu[:, 2]), outv], 1)
        for j, (t, wd, o) in enumerate(((0.15, 0.95, 0.7), (0.33, 0.85, 0.62))):
            cl = Sh + (E - Sh) * t + outv * (S['ru'] * o)
            out.append(I.box(cl, Rl, (Lu * 0.13, S['ru'] * wd, 0.26), LAME, chamfer=(0.16, 0.2, 0.14),
                             name='shoulder_lame_%d' % j))
        out.append(I.taper_limb(Sh, E, RU, S['ru'] * 0.95, S['ru'] * 0.7, I.UARM, 'upper_arm', ext=0.05))
        out.append(I.ellip(E, RFa, (S['ru'] * 0.66,) * 3, SUIT, 'elbow'))
        g0 = E + (W - E) * 0.1
        out.append(I.taper_limb(g0, W, RFa, S['rf'] * 1.05, S['rf'] * 0.8, I.FARM, 'forearm', ext=0.0))
        out.append(_cyl(g0 - (W - E) * 0.02, g0 + (W - E) * 0.1, S['rf'] * 1.08, I.FARM, 'gauntlet_cuff', RFa))
        out.append(I.ellip(W + RFa @ np.array([0, 0, -S['rh'] * 0.6]), RFa,
                           (S['rh'] * 1.05, S['rh'] * 0.9, S['rh'] * 1.15), I.HAND, 'hand'))
    # ---- the helmet: the ochre shell, the visor in its dark frame, the jaw, ear pieces, the ridge, the antenna
    Hc, RH = P.head
    hr = np.asarray(S['hr'], float)
    hp = rc.Part(I.helmet_cons(Hc, RH, hr), I.HELMET, 'helmet', sphere=(Hc, float(np.linalg.norm(hr)) + 1e-3))
    hp.low = Hc[2] - float(np.abs(RH[2, :]) @ hr)
    hp.frame = (np.asarray(Hc, float), np.asarray(RH, float))
    out.append(hp)
    va, e0, e1 = S.get('lva', 38.0), S.get('le0', -22.0), S.get('le1', 15.0)
    out.append(I.shell_patch(Hc, RH, hr, 0.2, va + 7.0, e0 - 5.0, e1 + 7.0, FACEPANEL, 'visor_frame'))
    out.append(I.shell_patch(Hc, RH, hr, 0.32, va, e0, e1, I.VISOR, 'mask'))
    out.append(I.shell_patch(Hc, RH, hr, 0.22, va + 8.0, e0 - 26.0, e0 - 4.0, FACEPANEL, 'jaw'))
    for sg, nm in ((-1.0, 'l'), (1.0, 'r')):
        a = RH[:, 1] * sg
        c = Hc + a * hr[1] * 0.95 + RH @ np.array([-hr[0] * 0.1, 0, -hr[2] * 0.15])
        out.append(_cyl(c - a * 0.1, c + a * 0.3, hr[2] * 0.4, EAR, 'ear_' + nm, RH))
        out.append(_cyl(c + a * 0.25, c + a * 0.36, hr[2] * 0.2, RIM, 'ear_hub_' + nm, RH))
    out.append(I.box(Hc + RH @ np.array([-hr[0] * 0.1, 0, hr[2] * 0.97]), RH, (hr[0] * 0.8, 0.2, 0.12), I.HELMET,
                     chamfer=(0.3, 0.08, 0.06), name='helmet_ridge'))
    ab = Hc + RH @ np.array([-hr[0] * 0.35, -hr[1] * 0.95, hr[2] * 0.35])
    au = RH @ np.array([-0.2, -0.1, 1.0]); au = au / np.linalg.norm(au)
    au = au + np.array([0.0, 0.0, 0.9]); au = au / np.linalg.norm(au)
    out.append(_cyl(ab - au * 0.1, ab + au * 0.5, 0.26, STRAP, 'antenna_base', RH))
    out.append(_cyl(ab + au * 0.4, ab + au * S.get('anl', 4.5), 0.14, ANT, 'antenna', RH))
    # ---- the case (inf.py's toolbox: in his hand, on the ground when he crawls): dark, house-green hazard stripes on
    # both broad faces, the light grey lid band, handle and latches
    Sh, RU, E, RFa, W = P.arms['l' if Q.get('tbl', 0.0) > 0.5 else 'r']
    tb = np.asarray(S['tb'], float)
    top = W + RFa @ np.array([0.0, 0.0, -S['rh'] - S['tbz']])
    c = top + RFa @ np.array([0.0, 0.0, -tb[2]])
    Rb = RFa
    g = float(np.clip(Q.get('tbg', 0.0), 0.0, 1.0))
    if g > 0.0:
        fwd = np.array([np.cos(np.deg2rad(face)), np.sin(np.deg2rad(face)), 0.0])
        hz = fwd / max(float(np.linalg.norm(fwd)), 1e-6)
        zz = np.array([0.0, 0.0, 1.0]); xx = np.cross(zz, hz)
        Rg = np.stack([xx, np.cross(zz, xx), zz], 1)
        cg = W + hz * (tb[1] + S['rh'])
        cg[2] = min(p.low for p in out) + tb[2]
        c = c * (1.0 - g) + cg * g
        Mx = RFa * (1.0 - g) + Rg * g
        u, _, vt = np.linalg.svd(Mx)
        Rb = u @ vt
    out.append(I.box(c, Rb, tb, I.TOOLBOX, chamfer=(0.2, 0.15, 0.15), name='toolbox'))
    out.append(I.box(c + Rb @ np.array([0.0, 0.0, tb[2] - S['tlid'] * 0.5]), Rb,
                     (tb[0] * 0.99, tb[1] * 1.03, S['tlid'] * 0.5), I.LID, chamfer=(0.1, 0.1, 0.05), name='lid'))
    hs = np.array([tb[0] * 0.92, tb[1], (tb[2] - S['tlid']) * 0.9])
    cs = c + Rb @ np.array([0.0, 0.0, -S['tlid'] * 0.5])
    for sg in (-1.0, 1.0):
        out += face_stripes(cs, Rb, hs, 1, sg, 6, HAZ, 'case_stripe', ang=55.0, d=0.06)
        out.append(I.box(c + Rb @ np.array([sg * tb[0] * 0.55, 0.0, tb[2] + 0.25]), Rb, (0.13, 0.13, 0.28), HANDLE,
                         name='toolbox_handle_post'))
    out.append(I.box(c + Rb @ np.array([0.0, 0.0, tb[2] + 0.5]), Rb, (tb[0] * 0.55 + 0.13, 0.13, 0.11), HANDLE,
                     name='toolbox_handle'))
    return out
