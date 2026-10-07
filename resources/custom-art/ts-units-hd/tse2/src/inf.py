"""
inf.py - the TS infantry as one posable soldier made of convex parts (rc.py), shared by the six infantry units
(each with its own sizes, gear and colours).

Frames:
  world   x east, y south, z up; units TS px; the soldier's ground point at the origin.
  body    x forward, y to his right, z up (right-handed, as the world: facing east, his right is south).
A facing angle th (degrees, in the world's x-y plane from east towards south) turns body into world: Rz(th).
The mod's 8 facings (0 N, 1 NW ... counter-clockwise from north) are th = -90 - 45 f.

Shape (S): sizes in TS px.  Pose (Q): angles in degrees, offsets in TS px.  parts(S, Q, facing) -> [rc.Part].
"""
import numpy as np
import rc

# components
(HELMET, VISOR, FACE, CHEST, VEST, PACK, ABDOMEN, PELVIS, BELT, UARM, FARM, HAND, THIGH, KNEE, SHIN, BOOT, RIFLE,
 RIFLE_DARK, POUCH, PAD, JAW, TUBE, PLATE, DISC, TOOLBOX, LID, GOGGLE, ROLL, ROLL_END, WING, NOZZLE, CROSS,
 MEDKIT) = range(700, 733)
# fitting classes: 1 house green, 2 the helmet's blue-grey, 3 the visor's light blue, 4 light and mid grey, 5 dark,
# (6 effects, left out of the fit), 7 orange (E2's knee pads and pouch), 8 yellow (the Engineer's suit), 9 skin
# (the Ghost Stalker's face and bare arms)
GREEN, NAVY, LBLUE, GREY, DARK, ORANGE, YELLOW, SKIN = 1, 2, 3, 4, 5, 7, 8, 9
# (TS's E1: the torso is a dark vest all round; the green up top is the shoulder pads and the arms)
CLASS = {HELMET: NAVY, VISOR: LBLUE, FACE: LBLUE, CHEST: DARK, VEST: DARK, PACK: GREY, ABDOMEN: DARK, PELVIS: GREEN,
         BELT: DARK, UARM: GREEN, FARM: GREEN, HAND: DARK, THIGH: GREEN, KNEE: GREEN, SHIN: GREY, BOOT: DARK,
         RIFLE: DARK, RIFLE_DARK: DARK, POUCH: NAVY, PAD: GREEN, JAW: DARK, TUBE: NAVY, PLATE: DARK, DISC: GREY,
         TOOLBOX: YELLOW, LID: GREY, GOGGLE: DARK, ROLL: DARK, ROLL_END: GREY, WING: GREEN, NOZZLE: GREY, CROSS: 6,
         MEDKIT: GREY}

S0 = dict(
    # legs: hip spacing (half), thigh and shin lengths, their radii, the ankle's height, the boot
    hw=1.25, lt=4.9, ls=4.8, rt=1.3, rs=1.0, ah=1.0, bl=2.8, bw=0.95, bh=1.15,
    # the pelvis and abdomen, the chest (spine length from the hips to the shoulders' height), shoulder spacing
    # (TS's E1: the torso 6-7 px deep in the side views, the shoulders 9 px across with the arms in the front view)
    pr=(1.8, 2.2, 1.4), lsp=7.0, cr=(2.3, 2.4, 2.6), sw=2.9, ar=(1.9, 2.1, 1.7),
    # the shoulder pads (TS: green, 3 px across, the widest part of the soldier)
    pd=(1.6, 1.5, 1.25), pdz=0.55,
    # arms: upper arm and forearm lengths and radii, the hand
    lu=3.8, lf=3.5, ru=0.9, rf=0.8, rh=0.65,
    # the neck and the helmet: a rounded box (half-sizes: front-back, side, up; TS: the head 4 px across, 4-5 deep, its
    # sides upright, the top flat-ish; the references: a full helmet round a big faceplate)
    ln=0.3, hr=(2.0, 1.7, 1.6),
    # the mask: a faceplate set in the helmet's front (TS: its light blue on the lower front of the head, about half the
    # face across, 2 rows; the references: a big curved visor in a full helmet), fva its half-width round the helmet
    # (degrees), fe0 / fe1 its lower and upper edges (elevation from the helmet's centre), fd how far it stands proud;
    # the dark jaw guard under it, fj tall
    fva=30.0, fe0=-38.0, fe1=18.0, fd=0.14, fj=24.0, vd=0.35, vh=0.8, vz=-0.35,
    # the vest over the chest (front plate thickness), the plate on the upper back (depth, half-width, half-height),
    # the pouch on the lower back
    vt=0.0, pk=(0.6, 0.8, 1.6), po=(0.6, 1.3, 0.8),
    # the rifle: length, thickness, the grip's place along it (from its back end), its stock's depth
    # (TS's side views: 12-13 px from the muzzle to the stock at the shoulder)
    gl=12.0, gt=0.6, gg=4.0, gs=1.0,
    # the kit: e1 (the rifle, a plate and a pouch on the back) or e2 (no rifle; the disc magazines on the back)
    kit='e1', rifle=1)

# the Disc Thrower (TS's E2): no rifle; on his back two disc magazines, tubes lying across it one above the other
# (TS's back view: two blue-grey bands 3 rows tall with a dark row between, 8 px across; its side views: their round
# ends one above the other, 3 px behind the body) on a dark plate; an orange pouch on the back of his belt (TS's back
# and side views: orange across the hips behind); orange knee pads (TS's front view); the disc he throws in his hand
S0_E2 = dict(S0, kit='e2', rifle=0, rk=(2.0, 3.8, 4.75), rkz=1.45, rko=0.0,
             tr=1.5, tl=4.0, tz1=1.6, tz2=-1.7, tx=0.6, bp=(0.45, 2.6, 3.4), bpz=0.0,
             bb=(0.8, 1.7, 0.9), bbz=0.1, bbx=0.8, bbo=0.8, dr=1.3, dt=0.35)

# the Engineer (TS's ENGINEER): unarmed; a yellow pack on his back (TS's back view: yellow from the shoulders down to
# a light grey belt), a toolbox in his right hand (TS's east view: a yellow box with a light grey lid hanging at his
# side, 7 px long, 5 rows tall), tb its half-sizes (along his front, across, up), tbz how far below the hand
# His hood's face (TS's front view): two dark goggle lenses a row above a light grey respirator (the 'mask' patch);
# gaz the lenses' angle either side of the front, gva their half-width, ge0 / gh their lower edge and height (degrees)
S0_ENG = dict(S0, kit='eng', rifle=0, tb=(2.6, 1.2, 1.7), tbz=0.2, tlid=0.35, gaz=28.0, gva=12.0, ge0=-5.0, gh=22.0)

# the Ghost Stalker (TS's GHOST): the railgun, longer than E1's rifle (TS's north-west and south-east views: 6-7 px
# out past his body, held at the hip, 2 px thick), in house green; no pack.
# His head (TS: a blue-grey hood over the top and back of his head; his bare face, 2 px across and 2 rows tall, the
# front half of his head in the side views, the hood beside it in the front view): the head's box split at hcut (the
# hood's front edge, along his front from the head's centre) and hzc (the brow, up from the centre): the hood is the box
# behind hcut and above hzc; the face the box ahead of hcut and under hzc, fw as wide, standing fdx proud.
# Across his upper back at his head's height a dark roll (TS: near-black, behind his head in every facing, wider than
# his shoulders: 9-10 px in the front and back views, 2 rows thick; a light grey pixel a pixel in from either end in
# the front, back and three-quarter views: its ends light grey, re long): rl its half-length, rr its radius, its
# centre rb behind and rz above the shoulders' point on the spine
S0_GHOST = dict(S0, kit='ghost', rifle=1, gl=15.0, gt=0.6, gg=4.5, gs=1.0,
                hcut=0.0, hzc=0.3, fw=0.65, fdx=0.2, rl=4.8, rr=1.0, rb=2.0, rz=2.0, re=0.5)

# the Jumpjet Infantry (TS's JUMPJET): the rifle; a jetpack on his back (TS's back view: a grey column from his
# shoulders to his hips, 4 px across, a light grey nozzle either side of its lower half), jp its half-sizes (deep,
# across, tall), jz its centre's height from the shoulders' point; the nozzles nr round, nl long, their tops nz below
# the pack's top.  Two wings from the pack's upper sides (TS: house green, spread wide behind him in every facing, as
# broad seen from behind as from the side: swept back and down): each a flat trapezoid wth thick, its root chord wc
# from the leading edge down, ws out to the tip, wt the tip's chord, the leading edge dropping wle a unit of span;
# turned back by wsw (sweep), down by wdh (dihedral) and about its span by wtw (degrees); its root wzr below the pack's
# top, wxr along his front from the pack's centre
S0_JJ = dict(S0, kit='jj', rifle=1, jp=(1.2, 1.6, 5.0), jz=-2.0, nr=0.5, nl=2.4, nz=6.0,
             wc=6.0, ws=9.0, wt=1.5, wle=0.0, wsw=35.0, wdh=10.0, wtw=0.0, wth=0.45, wzr=0.5, wxr=0.0)


def wing(Wr, M, ws, wc, wt, wle, th, comp, name):
    """a flat trapezoid: root at Wr, M's columns (span, chord down from the leading edge, normal); the leading edge at
    chord wle x span, the trailing edge from wc at the root to wle x ws + wt at the tip."""
    Wr = np.asarray(Wr, float); u, v, n = M[:, 0], M[:, 1], M[:, 2]
    k = (wt + wle * ws - wc) / ws
    cons = [rc.Plane(-u, -(u @ Wr)), rc.Plane(u, u @ Wr + ws), rc.Plane(n, n @ Wr + th / 2),
            rc.Plane(-n, -(n @ Wr) + th / 2)]
    a = (wle * u - v) / np.linalg.norm(wle * u - v)            # b >= wle a
    cons.append(rc.Plane(a, a @ Wr))
    t = (v - k * u) / np.linalg.norm(v - k * u)                # b <= wc + k a
    cons.append(rc.Plane(t, t @ Wr + wc / np.linalg.norm(v - k * u)))
    corners = [Wr + u * aa + v * bb + n * cc for aa, bb in ((0, 0), (0, wc), (ws, wle * ws), (ws, wle * ws + wt))
               for cc in (-th / 2, th / 2)]
    cen = np.mean(corners, 0)
    p = rc.Part(cons, comp, name, sphere=(cen, float(max(np.linalg.norm(c - cen) for c in corners)) + 1e-3))
    p.low = float(min(c[2] for c in corners))
    p.frame = (cen, M)
    return p


# the Medic (TS's MEDIC): unarmed; a grey medical case in his right hand (TS's south and east views: a grey box at his
# side, a red cross on its outer face), mk its half-sizes (along his front, across, up), mkz how far below the hand; a
# red cross on his upper back (TS's back view: 3 x 3 px between the shoulder blades), cr_s its half-size, cr_w its
# arms' half-width; an orange pouch on the back of his belt (TS's back view: orange across the hips, 7 px wide, 3-4
# rows), as E2's (bb, bbx, bbz, bbo)
S0_MEDIC = dict(S0, kit='medic', rifle=0, mk=(2.4, 1.0, 1.9), mkz=0.2, crs=1.4, crw=0.45, crz=-0.25,
                bb=(0.8, 1.9, 0.9), bbz=0.1, bbx=0.8, bbo=0.8,
                # (TS's Medic: his hips and the backs of his thighs orange - the hips' and thighs' backs, behind planes
                # psp x their depth and tsp x the thigh's radius ahead of their middles; the red cross on his helmet's
                # crown, its arms hcs x the helmet's half-sizes, hcw x that wide)
                psp=0.3, tsp=0.0, hcs=0.5, hcw=0.3)


def split(p, n, off, comp_back, name_back):
    """the part cut in two by a plane across n, off ahead of its middle: the front (n's side) keeps its component, the
    back takes comp_back."""
    c, R = p.frame
    n = np.asarray(n, float); n = n / np.linalg.norm(n)
    d = float(n @ np.asarray(c, float)) + off
    front = rc.Part(p.cons + [rc.Plane(-n, -d)], p.comp, p.name, p.sphere)
    back = rc.Part(p.cons + [rc.Plane(n, d)], comp_back, name_back, p.sphere)
    for q in (front, back):
        q.low, q.frame = p.low, p.frame
    return [front, back]


def crown_cross(Hc, RH, hr, size, width, d, comp, name):
    """a cross on the helmet's crown: two bars (along the head's front and across it), each the helmet's shell d proud
    of it over the bar's footprint, so it follows the crown's curve; size: the arms' half-length in the helmet's
    half-sizes, width: the bars' half-width in that."""
    Hc = np.asarray(Hc, float); RH = np.asarray(RH, float); hr = np.asarray(hr, float)
    shell = helmet_cons(Hc, RH, hr + d)
    nz = RH[:, 2]
    out = []
    for a, b, nm in ((0, 1, 'a'), (1, 0, 'b')):
        na, nb = RH[:, a], RH[:, b]
        L, Wd = size * hr[a], width * size * min(hr[0], hr[1])
        cons = shell + [rc.Plane(na, na @ Hc + L), rc.Plane(-na, -(na @ Hc) + L), rc.Plane(nb, nb @ Hc + Wd),
                        rc.Plane(-nb, -(nb @ Hc) + Wd), rc.Plane(-nz, -(nz @ Hc + hr[2] * 0.5))]
        p = rc.Part(cons, comp, name + nm, sphere=(Hc, float(np.linalg.norm(hr + d)) + 1e-3))
        p.low = Hc[2] - float(np.abs(RH[2, :]) @ hr)
        p.frame = (Hc, RH)
        out.append(p)
    return out


def cross(c, n, u, size, width, depth, comp, name):
    """a red cross decal at c on a face with outward normal n (u its 'up'): two thin boxes, size the arms' half-length."""
    n = np.asarray(n, float); u = np.asarray(u, float)
    v = np.cross(n, u)
    out = []
    for a, b, nm in ((u, v, 'v'), (v, u, 'h')):
        R = np.stack([a, b, n], 1)
        p = box(np.asarray(c, float) + n * depth * 0.5, R, (size, width, depth * 0.5), comp, name=name + nm)
        out.append(p)
    return out


# the pose: every angle 0 is standing straight, arms hanging, facing the facing
Q0 = dict(dx=0.0, dy=0.0, dz=0.0, yaw=0.0, pitch=0.0, roll=0.0,
          sp=0.0, sy=0.0, sr=0.0, hp=0.0, hy=0.0,
          # arms (l, r): shoulder flex (forward), abduction (out), twist; elbow flex
          lsf=0.0, lsa=8.0, lst=0.0, lef=10.0, rsf=0.0, rsa=8.0, rst=0.0, ref=10.0,
          # legs: hip flex (forward), abduction (out), twist; knee flex (back); ankle (toe up)
          lhf=0.0, lha=3.0, lht=0.0, lkf=0.0, laf=0.0, rhf=0.0, rha=3.0, rht=0.0, rkf=0.0, raf=0.0,
          # the rifle's aim against the torso: pitch (muzzle up), yaw (muzzle to his right), roll
          gp=0.0, gy=0.0, gr=0.0,
          # held (ik 1): the grip (right hand) in the chest's frame (forward, right, up from the shoulders' middle), the
          # left hand along the barrel, the elbows' swivel round the shoulder-hand line (degrees; 0 = down and out)
          ik=1.0, rgx=2.4, rgy=0.4, rgz=-3.4, lfx=2.6, lsw=0.0, rsw=0.0)


def Rx(a):
    a = np.deg2rad(a); c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def Ry(a):
    a = np.deg2rad(a); c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def Rz(a):
    a = np.deg2rad(a); c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def facing_angle(f):
    return -90.0 - 45.0 * f


def ellip(c, R, r, comp, name):
    c = np.asarray(c, float); r = np.asarray(r, float); R = np.asarray(R, float)
    p = rc.Part([rc.Ellip(c, R, r)], comp, name, sphere=(c, float(r.max()) + 1e-3))
    p.low = c[2] - float(np.linalg.norm(R[2, :] * r))
    p.frame = (c, R)
    return p


ROUND = 1.15         # the helmet: a box (half-sizes h) cut by an ellipsoid ROUND times as big, so its edges are rounded


def helmet_cons(c, R, h):
    c = np.asarray(c, float); R = np.asarray(R, float); h = np.asarray(h, float)
    return [rc.Ellip(c, R, h * ROUND)] + rc.box_planes(c, R, h)


def shell_patch(c, R, r, d, va, e0, e1, comp, name):
    """a piece of a shell over the helmet (centre c, axes R, half-sizes r), d proud of it: the directions within va
    degrees either side of R's forward axis and between elevations e0 and e1 (degrees)."""
    c = np.asarray(c, float); R = np.asarray(R, float)
    rr = np.asarray(r, float) + d
    cons = helmet_cons(c, R, rr)
    a, b0, b1 = np.deg2rad(va), np.deg2rad(e0), np.deg2rad(e1)
    for n in (np.array([-np.sin(a), np.cos(a), 0.0]), np.array([-np.sin(a), -np.cos(a), 0.0]),
              np.array([-np.sin(b1), 0.0, np.cos(b1)]), -np.array([-np.sin(b0), 0.0, np.cos(b0)])):
        nw = R @ n
        cons.append(rc.Plane(nw, nw @ c))
    p = rc.Part(cons, comp, name, sphere=(c, float(rr.max()) + 1e-3))
    p.low = c[2] - float(np.linalg.norm(R[2, :] * rr))
    p.frame = (c, R)
    return p


def box(c, R, h, comp, chamfer=0.0, name=''):
    c = np.asarray(c, float); R = np.asarray(R, float); h = np.asarray(h, float)
    p = rc.box(c, R, h, comp, chamfer=chamfer, name=name)
    p.low = c[2] - float(np.abs(R[2, :]) @ h)
    p.frame = (c, R)
    return p


def seg_box(p0, p1, w, d, comp, up=(0, 0, 1.0), name=''):
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    L = np.linalg.norm(p1 - p0)
    R = rc.frame_from(p1 - p0, up)
    return box((p0 + p1) / 2, R, (L / 2, w / 2, d / 2), comp, name=name)


def limb(p0, p1, R, r1, r2, comp, name, ext=0.25):
    """an ellipsoid along a bone from p0 to p1 (R's third column along it), r1 across (R's first), r2 (second)."""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    L = np.linalg.norm(p1 - p0)
    a = (p1 - p0) / max(L, 1e-9)
    # an orthonormal frame with its third axis along the bone, the first as close to R's first as can be
    x = R[:, 0] - (R[:, 0] @ a) * a
    if np.linalg.norm(x) < 1e-6:
        x = R[:, 1] - (R[:, 1] @ a) * a
    x = x / np.linalg.norm(x); y = np.cross(a, x)
    M = np.stack([x, y, a], 1)
    return ellip((p0 + p1) / 2, M, (r1, r2, L / 2 + ext), comp, name)


def taper_limb(p0, p1, R, r0, r1, comp, name, ext=0.25):
    """a limb from p0 (r0 across) narrowing to p1 (r1 across): an ellipsoid along the bone whose widest point sits near
    p0, long enough that it is r1 across at p1, cut square ext past either end."""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    L = float(np.linalg.norm(p1 - p0))
    a = (p1 - p0) / max(L, 1e-9)
    x = R[:, 0] - (R[:, 0] @ a) * a
    if np.linalg.norm(x) < 1e-6:
        x = R[:, 1] - (R[:, 1] @ a) * a
    x = x / np.linalg.norm(x); y = np.cross(a, x)
    M = np.stack([x, y, a], 1)
    k = float(np.clip(r1 / max(r0, 1e-6), 0.2, 0.98))
    s0 = 0.25 * L                                   # the widest point, a quarter of the way down
    A = (L - s0) / np.sqrt(1.0 - k * k)             # the half-length that leaves it r1 across at p1
    c = p0 + a * s0
    cons = [rc.Ellip(c, M, (r0, r0, A)), rc.Plane(a, a @ p1 + ext), rc.Plane(-a, -(a @ p0) + ext)]
    p = rc.Part(cons, comp, name, sphere=((p0 + p1) / 2, L / 2 + ext + r0 + 1e-3))
    p.low = min(p0[2], p1[2]) - r0
    p.frame = ((p0 + p1) / 2, M)
    return p


def two_bone(A, T, a, b, pole):
    """a two-bone limb from A reaching for T (bones a, b long), its middle joint towards pole: (joint, end)."""
    d = T - A
    L = float(np.linalg.norm(d))
    u = d / max(L, 1e-9)
    L = min(L, a + b - 1e-3)
    x = (a * a - b * b + L * L) / (2 * L)
    h = np.sqrt(max(a * a - x * x, 0.0))
    p = pole - (pole @ u) * u
    n = np.linalg.norm(p)
    p = p / n if n > 1e-6 else np.cross(u, [0, 0, 1.0]) / max(np.linalg.norm(np.cross(u, [0, 0, 1.0])), 1e-9)
    return A + u * x + p * h, A + u * L


def frame_along(v, R):
    """a frame whose third axis points against v (a limb hanging down its bone), the first as close to R's first."""
    a = -np.asarray(v, float) / max(np.linalg.norm(v), 1e-9)
    x = R[:, 0] - (R[:, 0] @ a) * a
    if np.linalg.norm(x) < 1e-6:
        x = R[:, 1] - (R[:, 1] @ a) * a
    x = x / np.linalg.norm(x)
    return np.stack([x, np.cross(a, x), a], 1)


def gun_clearance(S, P0, B, C0, RC, G, RG):
    """how far the gun (grip G, barrel along RG's x) must move ahead of his body (along the chest's front) so no part of
    it is inside his pelvis, belt, abdomen or chest."""
    back = G - RG[:, 0] * S['gg']
    pts = back[None, :] + np.linspace(0.0, S['gl'], 28)[:, None] * RG[:, 0][None, :]
    rg = S['gt'] * 0.55
    cc = C0 + RC @ np.array([0, 0, -S['cr'][2] * 0.55])
    bodies = [(P0 + B @ np.array([0, 0, 0.2]), B, np.asarray(S['pr'], float)),
              (P0 + B @ np.array([0, 0, 0.55]), B, np.array([S['pr'][0] * 1.05, S['pr'][1] * 1.02, 0.42])),
              (P0 + (C0 - P0) * 0.45, RC, np.asarray(S['ar'], float)),
              (cc, RC, np.asarray(S['cr'], float)),
              (cc + RC @ np.array([S['cr'][0] * 0.35, 0, -0.35]), RC,
               np.array([S['cr'][0] * 0.7 + S.get('vt', 0.0), S['cr'][1] * 0.72, S['cr'][2] * 0.8]))]
    u = RC[:, 0]
    for d in np.arange(0.0, 6.01, 0.2):
        P = pts + d * u[None, :]
        inside = False
        for c, R, r in bodies:
            z = ((P - c[None, :]) @ R) / (r[None, :] + rg)
            if (np.einsum('ij,ij->i', z, z) < 1.0).any():
                inside = True
                break
        if not inside:
            return float(d)
    return 6.0


class Pose:
    """forward kinematics: joint places and frames in the world for shape S, pose Q, facing angle th."""

    def __init__(self, S, Q, th):
        self.S, self.Q = S, Q
        q = Q
        B = Rz(th + q['yaw']) @ Ry(q['pitch']) @ Rx(q['roll'])          # the pelvis's frame in the world
        # (ptw: the pelvis turned about its own long axis, one hip rising - a crawler's hip hitching up as that knee
        # comes in; 0 by default)
        if q.get('ptw', 0.0):
            B = B @ Rz(q['ptw'])
        hip_h = S['ah'] + S['ls'] + S['lt']
        P0 = np.array([q['dx'], q['dy'], hip_h + q['dz']])
        # (bx, by: the body moved along his own facing - forward, to his left - the same in every facing: TS draws
        # its prone soldier further back from where he stands than his hips)
        if q.get('bx', 0.0) or q.get('by', 0.0):
            P0 = P0 + Rz(th) @ np.array([q.get('bx', 0.0), q.get('by', 0.0), 0.0])
        self.pelvis = (P0, B)
        # legs
        self.legs = {}
        for side, sg in (('l', -1.0), ('r', 1.0)):
            # (lhk, rhk: that hip drawn along the body towards the head, TS px - the hip hitching up as the knee
            # comes in; 0 by default)
            H = P0 + B @ np.array([0, sg * S['hw'], q.get(side + 'hk', 0.0)])
            RT = B @ Ry(-q[side + 'hf']) @ Rx(sg * q[side + 'ha']) @ Rz(q[side + 'ht'])
            K = H + RT @ np.array([0, 0, -S['lt']])
            RS = RT @ Ry(q[side + 'kf'])
            A = K + RS @ np.array([0, 0, -S['ls']])
            RF = RS @ Ry(-q[side + 'af'])
            self.legs[side] = (H, RT, K, RS, A, RF)
        # spine: abdomen and chest
        # the spine in two pieces (the crawl's wriggle: the body curving, not just angling at the hips): the lower
        # back from the pelvis to the middle of the spine (smid of its length; 0, the default, puts the bend at the
        # hips as before), turned by lp, ly, lr (pitch, twist, side bend); the upper back from there to the
        # shoulders, turned by sp, sy, sr on top of it.  With smid 0 and lp, ly, lr 0 it is the old one-piece spine
        a = float(q.get('smid', 0.0))
        RL = B @ Ry(q.get('lp', 0.0)) @ Rz(q.get('ly', 0.0)) @ Rx(q.get('lr', 0.0))
        M = P0 + RL @ np.array([0, 0, a * S['lsp']])
        RC = RL @ Ry(q['sp']) @ Rz(q['sy']) @ Rx(q['sr'])
        C0 = M + RC @ np.array([0, 0, (1.0 - a) * S['lsp']])            # the shoulders' height on the spine
        self.mid = (M, RL)
        self.chest = (C0, RC)
        RH = RC @ Ry(q['hp']) @ Rz(q['hy'])
        N = C0 + RC @ np.array([0, 0, 0.35])
        Hc = N + RH @ np.array([0, 0, S['ln'] + S['hr'][2]])
        self.head = (Hc, RH)
        self.arms = {}
        # (the shoulder girdle: lsg / rsg move that shoulder along the spine - up towards the head, a crawler's
        # shoulder reaching forward - and lsx / rsx along the chest's front, TS px; 0 by default)
        shoulders = {sd: C0 + RC @ np.array([q.get(sd + 'sx', 0.0), sg * S['sw'], -0.35 + q.get(sd + 'sg', 0.0)])
                     for sd, sg in (('l', -1.0), ('r', 1.0))}
        RG = RC @ Rz(q['gy']) @ Ry(-q['gp']) @ Rx(q['gr'])               # the rifle: its x axis along the barrel
        if q.get('ik', 1.0) > 0.5:
            # the rifle held: the right hand on its grip, the left under the barrel; the arms reach them (two bones)
            G = C0 + RC @ np.array([q['rgx'], q['rgy'], q['rgz']])
            if S.get('kit') == 'ghost' and S.get('rifle', 1) > 0.5:
                # (the railgun held at his hip mustn't pass through him: pushed out ahead of his body, his hands with
                # it, as far as it takes - Luke: "his gun clips into his stomach")
                RG0 = RC @ Rz(q['gy']) @ Ry(-q['gp']) @ Rx(q['gr'])
                G = G + RC[:, 0] * gun_clearance(S, P0, B, C0, RC, G, RG0)
            targets = {'r': G, 'l': G + RG @ np.array([q['lfx'], 0, -0.25 - S['rh'] * 0.5])}
            if 'rfx' in q:
                # (the right hand up the barrel too, rfx ahead of the grip: a crawler holds his rifle out in front by
                # the handguard, both hands ahead of the shoulders; the rifle itself stays where the grip puts it)
                targets['r'] = G + RG @ np.array([q['rfx'], 0, -0.25 - S['rh'] * 0.5])
            for side, sg in (('l', -1.0), ('r', 1.0)):
                Sh = shoulders[side]
                pole = RC @ (Rx(sg * q[side + 'sw']) @ np.array([-0.15, sg * 0.55, -0.82]))
                if 'epy' in q:
                    # (the elbows' direction given outright, in the chest's frame: epx along its front, epy out to that
                    # side, epz along the spine - a crawler's elbows out to the sides on the ground)
                    pole = RC @ np.array([q['epx'], sg * q['epy'], q['epz']])
                E, W = two_bone(Sh, targets[side] - (targets[side] - Sh) / max(np.linalg.norm(targets[side] - Sh), 1e-6)
                                * S['rh'] * 0.6, S['lu'], S['lf'], pole)
                self.arms[side] = (Sh, RC, E, frame_along(W - E, RC), W)
            self.rifle = (G, RG)
        else:
            for side, sg in (('l', -1.0), ('r', 1.0)):
                Sh = shoulders[side]
                RU = RC @ Ry(-q[side + 'sf']) @ Rx(sg * q[side + 'sa']) @ Rz(q[side + 'st'])
                E = Sh + RU @ np.array([0, 0, -S['lu']])
                RF = RU @ Ry(-q[side + 'ef'])
                W = E + RF @ np.array([0, 0, -S['lf']])
                self.arms[side] = (Sh, RU, E, RF, W)
            Sh, RU, E, RFr, W = self.arms['r']
            self.rifle = (W + RFr @ np.array([0, 0, -S['rh'] * 0.6]), RG)

    def soles(self):
        """the boots' lowest points (z)."""
        out = []
        for side in ('l', 'r'):
            H, RT, K, RS, A, RF = self.legs[side]
            S = self.S
            for dx in (-0.35 * S['bl'], 0.65 * S['bl']):
                out.append((A + RF @ np.array([dx, 0, -S['bh'] * 0.8]))[2])
        return out


def parts(S, Q, th, rifle=True):
    if S.get('look', 1) >= 2 and S.get('kit', 'e1') == 'e1':
        # (the Light Infantry's makeover: inflook.py)
        import inflook
        return inflook.parts(S, Q, th, rifle)
    if S.get('look', 1) >= 2 and S.get('kit', 'e1') == 'e2':
        # (the Disc Thrower's makeover: inflook_e2.py)
        import inflook_e2
        return inflook_e2.parts(S, Q, th, rifle)
    P = Pose(S, Q, th)
    face = float(th)                     # (the facing angle: th is reused for the thighs below)
    out = []
    P0, B = P.pelvis
    kit = S.get('kit', 'e1')
    pel = ellip(P0 + B @ np.array([0, 0, 0.2]), B, S['pr'], PELVIS, 'pelvis')
    if kit == 'medic' or (kit == 'e2' and S.get('ruck', 0)):
        # the Medic's hips: orange behind (TS's back and side views), dark in front; E2's the same, green in front
        out += split(pel, B[:, 0], S.get('psp', 0.3) * S['pr'][0], POUCH, 'hips')
    else:
        out.append(pel)
    out.append(ellip(P0 + B @ np.array([0, 0, 0.55]), B, (S['pr'][0] * 1.05, S['pr'][1] * 1.02, 0.42), BELT, 'belt'))
    for side in ('l', 'r'):
        H, RT, K, RS, A, RF = P.legs[side]
        th = limb(H, K, RT, S['rt'], S['rt'] * 0.95, THIGH, 'thigh', ext=0.35)
        if kit == 'e2' and S.get('ruck', 0):
            # E2's: an orange patch on the back of each trouser leg at the top (TS's back view: orange across his seat,
            # 3 rows; its side views: 2 px at the back of the hip), the rest green: the thigh cut front from back, and
            # the back cut across its bone (tsl: where, from the thigh's middle towards the hip)
            c_, R_ = th.frame
            fn = R_[:, 0] / np.linalg.norm(R_[:, 0])
            ax = (H - K) / max(float(np.linalg.norm(H - K)), 1e-6)
            d1 = float(fn @ c_) + S.get('tsp', 0.0) * S['rt']
            d2 = float(ax @ c_) + S.get('tsl', 0.5)
            for cons, comp, nm in ((th.cons + [rc.Plane(-fn, -d1)], THIGH, 'thigh'),
                                   (th.cons + [rc.Plane(fn, d1), rc.Plane(-ax, -d2)], POUCH, 'thigh_back'),
                                   (th.cons + [rc.Plane(fn, d1), rc.Plane(ax, d2)], THIGH, 'thigh_low')):
                q = rc.Part(cons, comp, nm, th.sphere)
                q.low, q.frame = th.low, th.frame
                out.append(q)
        elif kit == 'medic':
            # the Medic's thighs: house green in front, orange behind (TS's front view: green thighs; its back view:
            # orange down the backs of both)
            out += split(th, th.frame[1][:, 0], S.get('tsp', 0.0) * S['rt'], POUCH, 'thigh_back')
        else:
            out.append(th)
        out.append(limb(K, A, RS, S['rs'], S['rs'] * 0.95, SHIN, 'shin', ext=0.2))
        out.append(ellip(K + RS @ np.array([0.25, 0, -0.1]), RS, (S['rs'] * 0.9, S['rs'] * 0.95, S['rs'] * 0.85), KNEE,
                         'knee'))
        c = A + RF @ np.array([0.3 * S['bl'] - 0.15, 0, -S['bh'] * 0.35])
        out.append(box(c, RF, (S['bl'] / 2, S['bw'], S['bh'] / 2), BOOT, chamfer=(0.3, 0.3, 0.3), name='boot'))
    C0, RC = P.chest
    # abdomen between the pelvis and the chest, the chest, the vest's front and back plates
    mid = (P0 + C0) / 2
    M, RL = P.mid
    if Q.get('smid', 0.0):
        # (two-piece spine: the abdomen along the lower back, centred between the hips and the middle joint and a
        # little past it, so it bridges to the chest)
        out.append(ellip(P0 + (M - P0) * 0.75, RL, S['ar'], ABDOMEN, 'abdomen'))
    else:
        out.append(ellip(P0 + (C0 - P0) * 0.45, RC, S['ar'], ABDOMEN, 'abdomen'))
    cc = C0 + RC @ np.array([0, 0, -S['cr'][2] * 0.55])
    out.append(ellip(cc, RC, S['cr'], CHEST, 'chest'))
    out.append(ellip(cc + RC @ np.array([S['cr'][0] * 0.35, 0, -0.35]), RC,
                     (S['cr'][0] * 0.7 + S['vt'], S['cr'][1] * 0.72, S['cr'][2] * 0.8), VEST, 'vest'))
    if kit == 'medic':
        # the red cross on his upper back; the case in his right hand, a cross on each of its broad faces (his orange
        # behind: the hips' and thighs' backs, above)
        back_c = cc + RC @ np.array([-S['cr'][0], 0.0, S['crz']])
        out += cross(back_c, -RC[:, 0], RC[:, 2], S['crs'], S['crw'], 0.12, CROSS, 'back_cross_')
        Sh, RU, E, RFa, W = P.arms['l' if Q.get('tbl', 0.0) > 0.5 else 'r']
        mk = np.asarray(S['mk'], float)
        top = W + RFa @ np.array([0.0, 0.0, -S['rh'] - S['mkz']])
        c = top + RFa @ np.array([0.0, 0.0, -mk[2]])
        Rb = RFa
        g = float(np.clip(Q.get('tbg', 0.0), 0.0, 1.0))
        if g > 0.0:
            # crawling: the case stands on the ground just ahead of his hand (as the Engineer's toolbox)
            # (along the way he faces, not the forearm: it stays square to him and only slides with his hand - TS's
            # case doesn't swing about)
            fwd = np.array([np.cos(np.deg2rad(face)), np.sin(np.deg2rad(face)), 0.0])
            hz = np.array([fwd[0], fwd[1], 0.0]); hz = hz / max(float(np.linalg.norm(hz)), 1e-6)
            zz = np.array([0.0, 0.0, 1.0]); xx = np.cross(zz, hz)
            Rg = np.stack([xx, np.cross(zz, xx), zz], 1)
            cg = W + hz * (mk[1] + S['rh'])
            cg[2] = min(p.low for p in out) + mk[2]
            c = c * (1.0 - g) + cg * g
            M = RFa * (1.0 - g) + Rg * g
            u_, _, vt_ = np.linalg.svd(M)
            Rb = u_ @ vt_
        f = float(np.clip(Q.get('cfix', 0.0), 0.0, 1.0))
        if f > 0.0:
            # set down (idle 2, the heal) or dropped (the deaths): upright on the ground at a spot that stays put
            # (cfx, cfy: world; cfa: where its broad face looks, degrees from east; cft: how far it is tipped back)
            a = np.deg2rad(Q.get('cfa', -90.0))
            yv = np.array([np.cos(a), np.sin(a), 0.0]); zv = np.array([0.0, 0.0, 1.0])
            Rf = np.stack([np.cross(yv, zv), yv, zv], 1)
            # (cft: tipped back about its long side, its broad face turning up: 90 lying on its back)
            t = np.deg2rad(Q.get('cft', 0.0))
            Rf = Rf @ np.array([[1.0, 0.0, 0.0], [0.0, np.cos(t), -np.sin(t)], [0.0, np.sin(t), np.cos(t)]])
            cf = np.array([Q.get('cfx', 0.0), Q.get('cfy', 0.0), min(p.low for p in out) + float(np.abs(Rf[2, :]) @ mk)])
            c = c * (1.0 - f) + cf * f
            M = Rb * (1.0 - f) + Rf * f
            u_, _, vt_ = np.linalg.svd(M)
            Rb = u_ @ vt_
        out.append(box(c, Rb, mk, MEDKIT, chamfer=(0.2, 0.2, 0.2), name='medkit'))
        for sg, nm in ((1.0, 'r'), (-1.0, 'l')):
            out += cross(c + Rb[:, 1] * sg * mk[1], Rb[:, 1] * sg, Rb[:, 2], min(mk[0], mk[2]) * 0.55,
                         min(mk[0], mk[2]) * 0.18, 0.1, CROSS, 'case_cross_%s_' % nm)
    elif kit == 'e2' and S.get('ruck', 0):
        # one big blue rucksack on his back, its edges rounded (TS's back view: blue-grey from his shoulders to his
        # belt, 8-9 px wide; its side views: 3-4 px proud of his back) - Luke: TS's "big blue rucksack", not a board
        # and two rolls; the orange under it is the backs of his trousers (above)
        rk = np.array([S.get('rkd', S['rk'][0]), S.get('rkw', S['rk'][1]), S.get('rkh', S['rk'][2])], float)
        # (rkt: its top leaning back from his back by so many degrees, hung from the shoulders)
        RK = RC @ Ry(-S.get('rkt', 0.0))
        c = cc + RC @ np.array([-S['cr'][0] * 0.85 + S.get('rko', 0.0), 0, S['rkz']]) - RK[:, 0] * rk[0]
        if S.get('rkr', 0.0) > 0.0:
            # a soft pack, not a box (Luke: TS's "has a rounded curve"): a box with its back, sides and top rounded - the
            # box cut by an ellipsoid rkr times its half sizes (its centre forward, rkf of its depth, so the face on his
            # back stays flat and the back bulges); the top a dome (rkh2: how far the ellipsoid reaches above the box)
            r = float(S['rkr'])
            ec = c + RK[:, 0] * rk[0] * S.get('rkf', 0.6)
            er = np.array([rk[0] * (1.0 + S.get('rkf', 0.6)) * r, rk[1] * r, rk[2] * r * S.get('rkh2', 1.0)])
            p = rc.Part(rc.box_planes(c, RK, rk) + [rc.Ellip(ec, RK, er)], TUBE, 'rucksack',
                        sphere=(np.asarray(c, float), float(np.linalg.norm(rk)) + 1e-3))
            p.low = c[2] - float(np.abs(RK[2, :]) @ rk)
            p.frame = (c, RK)
            out.append(p)
            if S.get('rkl', 0.0) > 0.0:
                # its lid: the top rkl of the bag, a little proud of it all round (rlp), so a dark crease runs across
                # under it (TS's back view: a light band across the top, a dark one, the light bag below)
                lh = rk[2] * S['rkl']
                lc = c + RK[:, 2] * (rk[2] - lh) - RK[:, 0] * S.get('rlp', 0.3) * 0.5
                lk = np.array([rk[0] + S.get('rlp', 0.3) * 0.5, rk[1] + S.get('rlp', 0.3) * 0.5, lh])
                lec = lc + RK[:, 0] * lk[0] * S.get('rkf', 0.6)
                ler = np.array([lk[0] * (1.0 + S.get('rkf', 0.6)) * r, lk[1] * r, lk[2] * r * 1.6])
                q = rc.Part(rc.box_planes(lc, RK, lk) + [rc.Ellip(lec, RK, ler)], TUBE, 'rucksack_lid',
                            sphere=(np.asarray(lc, float), float(np.linalg.norm(lk)) + 1e-3))
                q.low = lc[2] - float(np.abs(RK[2, :]) @ lk)
                q.frame = (lc, RK)
                out.append(q)
        else:
            out.append(box(c, RK, rk, TUBE, chamfer=(0.45, 0.7, 0.7), name='rucksack'))
    elif kit == 'e2':
        # the plate on his back, the two magazines across it, the pouch on the back of the belt
        bp = np.asarray(S['bp'])
        back = -S['cr'][0] * 0.85
        out.append(box(cc + RC @ np.array([back - bp[0], 0, S['bpz']]), RC, bp, PLATE, chamfer=(0.2, 0.3, 0.3),
                       name='plate'))
        for i, z in enumerate((S['tz1'], S['tz2'])):
            c = cc + RC @ np.array([back - 2 * bp[0] - S['tr'] * S['tx'], 0, z])
            p = rc.cylinder(c - RC[:, 1] * S['tl'], c + RC[:, 1] * S['tl'], S['tr'], TUBE, 'magazine_%d' % (i + 1))
            p.low = c[2] - S['tr'] - abs(RC[2, 1]) * S['tl']
            p.frame = (c, RC)
            out.append(p)
        if 'bbx' in S:
            # a rounded box on the back of the belt, bbx deep, standing bbo proud of the hips behind (TS's back views:
            # orange across the hips under the belt, 7 px wide and 3 rows tall; its side views: 2 px proud behind)
            h = np.array([S['bbx'], S['bb'][1], S['bb'][2]])
            c = P0 + B @ np.array([-(S['pr'][0] + S['bbo']) + h[0], 0, S['bbz']])
            pp = rc.Part(helmet_cons(c, B, h), POUCH, 'pouch', sphere=(c, float(np.linalg.norm(h)) + 1e-3))
            pp.low = c[2] - float(np.abs(B[2, :]) @ h)
            pp.frame = (np.asarray(c, float), np.asarray(B, float))
            out.append(pp)
        else:
            out.append(ellip(P0 + B @ np.array([-S['pr'][0] * 0.75, 0, S['bbz']]), B, S['bb'], POUCH, 'pouch'))
    elif kit == 'ghost':
        # the roll across his upper back (along the chest's left-right axis), its ends light
        c = C0 + RC @ np.array([-S['rb'], 0.0, S['rz']])
        e = min(S.get('re', 0.5), S['rl'] * 0.4)
        for a, b, comp, nm in ((-(S['rl'] - e), S['rl'] - e, ROLL, 'roll'), (-S['rl'], -(S['rl'] - e), ROLL_END, 'roll_end_l'),
                               (S['rl'] - e, S['rl'], ROLL_END, 'roll_end_r')):
            p = rc.cylinder(c + RC[:, 1] * a, c + RC[:, 1] * b, S['rr'], comp, nm)
            p.low = c[2] - S['rr'] - abs(RC[2, 1]) * S['rl']
            p.frame = (c, RC)
            out.append(p)
    elif kit == 'jj':
        # the jetpack, its nozzles either side of its lower half, the wings from its upper sides
        jp = np.asarray(S['jp'], float)
        pc = C0 + RC @ np.array([-S['cr'][0] * 0.85 - jp[0] * 0.6, 0.0, S['jz']])
        out.append(box(pc, RC, jp, PACK, chamfer=(0.3, 0.3, 0.3), name='jetpack'))
        for sg, nm in ((-1.0, 'left'), (1.0, 'right')):
            top = pc + RC @ np.array([0.0, sg * (jp[1] + S['nr'] * 0.6), jp[2] - S['nz']])
            p = rc.cylinder(top - RC[:, 2] * S['nl'], top, S['nr'], NOZZLE, nm + '_nozzle')
            p.low = float(min((top - RC[:, 2] * S['nl'])[2], top[2])) - S['nr']
            p.frame = (top - RC[:, 2] * S['nl'] * 0.5, RC)
            out.append(p)
            Wr = pc + RC @ np.array([S['wxr'], sg * jp[1] * 0.85, jp[2] - S['wzr']])
            # (span out to his side, chord down, normal along his front: the same for both wings, so they mirror)
            M0 = np.stack([np.array([0.0, sg, 0.0]), np.array([0.0, 0.0, -1.0]), np.array([1.0, 0.0, 0.0])], 1)
            M = RC @ Rz(sg * S['wsw']) @ Rx(-sg * S['wdh']) @ M0 @ Rx(S['wtw'])
            out.append(wing(Wr, M, S['ws'], S['wc'], S['wt'], S['wle'], S['wth'], WING, nm + '_wing'))
    elif kit == 'eng':
        # the pack on his back; the toolbox hanging from his right hand (its long side along his front), the lid on it
        out.append(box(cc + RC @ np.array([-S['cr'][0] * 0.85 - S['pk'][0] * 0.3, 0, 0.3]), RC, S['pk'], PACK,
                       chamfer=(0.25, 0.3, 0.3), name='pack'))
        # (tbl: the box in his left hand - TS's flipped crawl sprites, where his left and right swap)
        Sh, RU, E, RFa, W = P.arms['l' if Q.get('tbl', 0.0) > 0.5 else 'r']
        tb = np.asarray(S['tb'], float)
        top = W + RFa @ np.array([0.0, 0.0, -S['rh'] - S['tbz']])
        c = top + RFa @ np.array([0.0, 0.0, -tb[2]])
        # (the box's frame is the hand's: its first axis along his front, its third along the forearm)
        Rb = RFa
        g = float(np.clip(Q.get('tbg', 0.0), 0.0, 1.0))
        if g > 0.0:
            # crawling (tbg 1; lying down and getting up blend to it): the box stands upright on the ground just
            # ahead of his hand, its long side across his reach, pushed along as he crawls
            # (along the way he faces, not the forearm: it stays square to him and only slides with his hand - TS's
            # case doesn't swing about)
            fwd = np.array([np.cos(np.deg2rad(face)), np.sin(np.deg2rad(face)), 0.0])
            hz = np.array([fwd[0], fwd[1], 0.0]); hz = hz / max(float(np.linalg.norm(hz)), 1e-6)
            zz = np.array([0.0, 0.0, 1.0]); xx = np.cross(zz, hz)
            Rg = np.stack([xx, np.cross(zz, xx), zz], 1)
            cg = W + hz * (tb[1] + S['rh'])
            cg[2] = min(p.low for p in out) + tb[2]
            c = c * (1.0 - g) + cg * g
            M = RFa * (1.0 - g) + Rg * g
            u, _, vt = np.linalg.svd(M)
            Rb = u @ vt
        out.append(box(c, Rb, tb, TOOLBOX, chamfer=(0.25, 0.2, 0.2), name='toolbox'))
        out.append(box(c + Rb @ np.array([0.0, 0.0, tb[2] - S['tlid'] * 0.5]), Rb,
                       (tb[0] * 0.98, tb[1] * 1.02, S['tlid'] * 0.5), LID, chamfer=(0.1, 0.1, 0.05), name='lid'))
    else:
        out.append(box(cc + RC @ np.array([-S['cr'][0] * 0.85 - S['pk'][0] * 0.3, 0, 0.3]), RC, S['pk'], PACK,
                       chamfer=(0.25, 0.3, 0.3), name='pack'))
        out.append(ellip(cc + RC @ np.array([-S['cr'][0] * 0.75, 0, -S['cr'][2] * 0.85]), RC, S['po'], POUCH, 'pouch'))
    for side, sg in (('l', -1.0), ('r', 1.0)):
        Sh, RU, E, RFa, W = P.arms[side]
        out.append(ellip(Sh + RC @ np.array([0, sg * 0.25, S['pdz']]), RC, S['pd'], PAD, 'shoulder_pad'))
        if S.get('taper', 0.0):
            # (the arms shaped: the upper arm narrowing from the shoulder to the elbow, the forearm from just below the
            # elbow to the wrist, a round elbow between them, so the bend reads as a joint - Luke: "he has no elbows")
            t = float(S['taper'])
            out.append(taper_limb(Sh, E, RU, S['ru'], S['ru'] * (1 - 0.4 * t), UARM, 'upper_arm', ext=0.05))
            out.append(taper_limb(E, W, RFa, S['rf'] * (1 - 0.05 * t), S['rf'] * (1 - 0.4 * t), FARM, 'forearm',
                                  ext=0.1))
            out.append(ellip(E, RFa, (S['ru'] * (1 - 0.3 * t),) * 3, FARM, 'elbow'))
        else:
            out.append(limb(Sh, E, RU, S['ru'], S['ru'], UARM, 'upper_arm', ext=0.3))
            out.append(limb(E, W, RFa, S['rf'], S['rf'], FARM, 'forearm', ext=0.2))
        out.append(ellip(W + RFa @ np.array([0, 0, -S['rh'] * 0.6]), RFa, (S['rh'],) * 3, HAND, 'hand'))
    Hc, RH = P.head
    if kit == 'ghost':
        h = np.asarray(S['hr'], float)
        nx, nz = RH[:, 0], RH[:, 2]
        low = Hc[2] - float(np.abs(RH[2, :]) @ h)
        rad = float(np.linalg.norm(h)) + 1e-3
        cut_x = float(nx @ Hc) + S['hcut']; cut_z = float(nz @ Hc) + S['hzc']
        # the hood: the head's back (behind hcut) and its top (above the brow)
        for cons, nm in ((helmet_cons(Hc, RH, h) + [rc.Plane(nx, cut_x)], 'hood'),
                         (helmet_cons(Hc, RH, h) + [rc.Plane(-nz, -cut_z)], 'hood_top')):
            hp = rc.Part(cons, HELMET, nm, sphere=(Hc, rad))
            hp.low = low
            hp.frame = (np.asarray(Hc, float), np.asarray(RH, float))
            out.append(hp)
        # the face: the head's front under the brow, narrower than the hood, standing proud of it
        fc = Hc + nx * S['fdx']
        hf = np.array([h[0], h[1] * S['fw'], h[2]])
        fp = rc.Part(helmet_cons(fc, RH, hf) + [rc.Plane(-nx, -(cut_x - 0.05)), rc.Plane(nz, cut_z + 0.05)], FACE,
                     'face', sphere=(fc, rad))
        fp.low = low
        fp.frame = (np.asarray(fc, float), np.asarray(RH, float))
        out.append(fp)
    else:
        hp = rc.Part(helmet_cons(Hc, RH, S['hr']), HELMET, 'helmet', sphere=(Hc, float(np.linalg.norm(S['hr'])) + 1e-3))
        hp.low = Hc[2] - float(np.abs(RH[2, :]) @ np.asarray(S['hr']))
        hp.frame = (np.asarray(Hc, float), np.asarray(RH, float))
        out.append(hp)
        out.append(shell_patch(Hc, RH, S['hr'], S['fd'], S['fva'], S['fe0'], S['fe1'], VISOR, 'mask'))
        out.append(shell_patch(Hc, RH, S['hr'], S['fd'] * 0.6, S['fva'] + 8.0, S['fe0'] - S['fj'], S['fe0'], JAW,
                               'jaw'))
    if kit == 'medic':
        # the red cross on his helmet's crown (TS: its red, blurred into the helmet's grey, on the crown in every
        # facing; gone edge-on when he lies; plainer as he bends over)
        out += crown_cross(Hc, RH, S['hr'], S.get('hcs', 0.5), S.get('hcw', 0.3), 0.06, CROSS, 'helmet_cross_')
    if kit == 'eng':
        for sgn, nm in ((1.0, 'goggle_l'), (-1.0, 'goggle_r')):
            out.append(shell_patch(Hc, RH @ Rz(sgn * S['gaz']), S['hr'], S['fd'] * 1.2 + 0.05, S['gva'], S['ge0'],
                                   S['ge0'] + S['gh'], GOGGLE, nm))
    # (the gun held in both hands, or - gone - in his right hand alone, the left arm free: the deaths, where TS flings
    # an arm up while the gun swings out in the other hand)
    if rifle and S.get('rifle', 1) > 0.5 and (Q.get('ik', 1.0) > 0.5 or Q.get('gone', 0.0) > 0.5):
        G0, RG = P.rifle
        # the barrel along RG's x: from the stock's back (behind the grip by gg) to the muzzle
        back = G0 - RG[:, 0] * S['gg']; front = back + RG[:, 0] * S['gl']
        out.append(seg_box(back, front, S['gt'], S['gt'], RIFLE, up=RG[:, 2], name='rifle'))
        # the stock and the receiver, deeper than the barrel
        out.append(seg_box(back, back + RG[:, 0] * (S['gg'] + 1.4), S['gt'] * 1.15, S['gs'], RIFLE_DARK,
                           up=RG[:, 2], name='receiver'))
    if Q.get('disc', 0.0) > 0.5:
        # the disc in his right hand, flat in the palm (the hand's frame: the forearm along its third axis)
        Sh, RU, E, RFa, W = P.arms['r']
        c = W + RFa @ np.array([0.0, 0.0, -S['rh'] * 1.1])
        p = rc.cylinder(c - RFa[:, 0] * S['dt'], c + RFa[:, 0] * S['dt'], S['dr'], DISC, 'disc')
        p.low = c[2] - S['dr']
        p.frame = (c, RFa)
        out.append(p)
    return out


def grounded(S, Q, th, rifle=True, extra=0.0):
    """the parts with the soldier's lowest point on the ground (plus extra), and that shift."""
    ps = parts(S, Q, th, rifle)
    dz = extra - min(p.low for p in ps)
    I = np.eye(3)
    out = []
    for p in ps:
        m = p.moved(I, (0.0, 0.0, dz)); m.low = p.low + dz
        if hasattr(p, 'frame'):
            m.frame = (np.asarray(p.frame[0], float) + np.array([0.0, 0.0, dz]), np.asarray(p.frame[1], float))
        out.append(m)
    return out, dz


def muzzle(S, Q, th):
    """the rifle's muzzle (world)."""
    P = Pose(S, Q, th)
    G0, RG = P.rifle
    return G0 + RG[:, 0] * (S['gl'] - S['gg'])


def nozzles(S, Q, th):
    """the Jumpjet's two nozzle mouths (world): where his jet flames come out."""
    P = Pose(S, Q, th)
    C0, RC = P.chest
    jp = np.asarray(S['jp'], float)
    pc = C0 + RC @ np.array([-S['cr'][0] * 0.85 - jp[0] * 0.6, 0.0, S['jz']])
    return [pc + RC @ np.array([0.0, sg * (jp[1] + S['nr'] * 0.6), jp[2] - S['nz'] - S['nl']]) for sg in (-1.0, 1.0)]


def nozzle(S, Q, th):
    """the middle of the Jumpjet's two nozzle mouths (world)."""
    a, b = nozzles(S, Q, th)
    return (a + b) / 2
