"""
wolfmat.py - the Wolverine's materials, per pixel of an rcrender.RCRender (textured in the body's own frame:
r.lu forward, r.lv right, r.lw up, so detail turns with the unit; parts that move with a leg use their own box
frame, r.pu / r.pv / r.pw).

Colours read from TS's SMECH frames (UNITTEM.PAL): the same yellow-brown paint as the Titan (TS's ochre ramp) on
the cab, the chest, the arms, thighs, shins and feet; a dark olive neck and pelvis; dark gunmetal guns with steel
gatling barrels; steel joints; a black antenna; the small orange lamp on the cab.  Detail from Westwood's render
of the same model: the pilot's black window slit, yellow-and-black hazard stripes along the top and the bottom of
the front plate, a vent grille low on each side, the armour plates over the thighs, scuffed and dirty shins, brass
ammo belts.  House colour is pure green 0,214,0 x (1 + 1.1 grain) on the back panel and the shoulder pads, with
detail only as thin seams and ribs.
"""
import numpy as np
import walls2 as W
from walls2 import smoothstep
import wolf as WF
import wolfhd as WH

GREEN = np.array([0, 214, 0.])
GOLD = np.array([208, 162, 70.])
GOLD_SH = np.array([216, 170, 76.])
BODY_D = np.array([152, 116, 52.])           # the chest and waist under the cab: TS draws them darker (the dark end
                                             # of the same ochre ramp)
OLIVE = np.array([84, 76, 52.])
GUN = np.array([74, 77, 90.])
STEEL = np.array([150, 152, 160.])
STEEL_L = np.array([222, 224, 228.])
STEEL_D = np.array([78, 79, 84.])
BLACK = np.array([28, 28, 30.])
GLASS = np.array([20, 24, 30.])               # the pilot's window
GRIME = np.array([112, 104, 78.])
LAMP = np.array([255, 150, 40.])
HAZ_Y = np.array([232, 184, 30.])             # hazard stripes: yellow and black
HAZ_K = np.array([34, 32, 28.])
BRASS = np.array([200, 160, 70.])
FILL = 0.32

GOLD_COMPS = (WF.TORSO, WF.HEAD, WF.ARM, WF.THIGH, WF.SHIN, WF.FOOT, WF.WAIST, WH.TOE)
HOUSE_COMPS = (WF.PACK, WF.SHOULDER)


def grain_of(r, scale=1.0):
    X, Y, Z = r.lu * 6.4 * scale, r.lv * 6.4 * scale, r.lw * 6.4 * scale
    ax, ay, az = np.abs(r.nx) + 1e-3, np.abs(r.ny) + 1e-3, np.abs(r.nz) + 1e-3
    s_ = ax + ay + az

    def tri(noise, o):
        return (W.sample(noise, Y + o, Z + 2 * o) * ax + W.sample(noise, X + 3 * o, Z + o) * ay +
                W.sample(noise, X + o, Y + 5 * o) * az) / s_
    return tri(W.NOISE_FINE, 0) * 0.035 + tri(W.NOISE_MOTTLE, 17) * 0.05


def blotch(r, scale=1.0):
    """a coarser mottle in the part's own frame, for the dirt and scuffs on the legs (moves with the leg)."""
    X, Y, Z = r.pu * 6.4 * scale, r.pv * 6.4 * scale, r.pw * 6.4 * scale
    return (W.sample(W.NOISE_MOTTLE, X + 2 * Y, Z + 7) + W.sample(W.NOISE_MOTTLE, Y + 11, X + Z)) * 0.5


def phase(v, per, off=0.0):
    return np.abs(np.mod(v - off + per / 2, per) - per / 2)


def materials(r, P, occ=None):
    comp = r.comp
    sh = comp.shape
    alb = np.zeros(sh + (3,), np.float32)
    emit = np.zeros(sh + (3,), np.float32)
    bz = np.zeros(sh, np.float32)
    grain = grain_of(r, scale=1 / 1.5)
    g1 = (1 + 0.45 * grain)[..., None]
    house = GREEN * (1 + 1.1 * grain)[..., None]
    dw = getattr(r, 'dw', 0.0)
    lu, lv, lw = r.lu, r.lv, r.lw - dw                 # the upper body's own heights (it bobs with dw)
    z = r.z
    nzl = r.nz
    top = nzl > 0.7
    put = lambda m, c: np.copyto(alb, np.broadcast_to(c, alb.shape).astype(np.float32), where=m[..., None])
    dust = smoothstep(3.0, 0.0, z) * 0.4

    # ---------------------------------------------------------------- upper body
    win_c = P.get('win_w', P['hw0'] - 0.85); win_h = P.get('win_h', 0.5)
    chest = comp == WF.TORSO
    if chest.any():
        put(chest, BODY_D * g1)
        front = chest & (lu > P['tu1'] - 0.3) & ~top
        # a seam down the middle of the front plate, between the hazard bands
        seam = front & (np.abs(lv) < 0.1) & (lw < win_c - win_h - 1.3) & (lw > P['tw0'] + 1.4)
        put(seam, BODY_D * 0.6 * g1); bz -= 0.3 * seam
        # hazard stripes along the top (under the window) and the bottom of the front plate (Westwood's render)
        ht = (lw < win_c - win_h - 0.12) & (lw > win_c - win_h - 0.98)
        hb = (lw > P['tw0'] + 0.18) & (lw < P['tw0'] + 1.04)
        band = front & (ht | hb) & (np.abs(lv) < P['tv'] - 0.12)
        stripe = phase(lv + lw, 1.15) < 0.29
        put(band & ~stripe, HAZ_Y * g1)
        put(band & stripe, HAZ_K * g1)
        # the bands' edges, a fine dark line
        edge = front & (np.abs(lv) < P['tv'] - 0.12) & (
            (np.abs(lw - (win_c - win_h - 0.98)) < 0.06) | (np.abs(lw - (P['tw0'] + 1.04)) < 0.06))
        put(edge, BODY_D * 0.45 * g1)
        # a vent grille low on each side, under the arm (Westwood's render)
        side = chest & ~top & (np.abs(lv) > P['tv'] - 0.25)
        grille = side & (lw > P['tw0'] + 1.2) & (lw < P['tw0'] + 3.6) & (lu > P['tu1'] - 3.4) & (lu < P['tu1'] - 0.7)
        slot = grille & (phase(lu, 0.48) < 0.13)
        put(grille, BODY_D * 0.8 * g1)
        put(slot, OLIVE * 0.55 * g1); bz -= 0.4 * slot
    put(comp == WF.WAIST, BODY_D * 0.85 * g1)
    head = comp == WF.HEAD
    if head.any():
        put(head, GOLD_SH * g1)
        # the seam where the sloping roof meets the cab's sides, and round the cab's base
        w_edge = P['hw1'] - P['hs']
        seam = head & (np.abs(lu - (P['hu1'] - 0.02)) < 0.5) & (np.abs(lw - w_edge) < 0.12)
        seam |= head & ~top & (np.abs(lw - (P['hw0'] + 0.55)) < 0.12)
        put(seam, GOLD_SH * 0.6 * g1); bz -= 0.3 * seam
    put(comp == WF.NECK, OLIVE * 0.8 * g1)
    win = comp == WH.WINDOW
    if win.any():
        # the pilot's window: near-black glass, a faint cool sheen along its upper edge
        put(win, GLASS)
        put(win & (lw > win_c + 0.22), GLASS * 1.9)
    pack = comp == WF.PACK
    if pack.any():
        put(pack, house)
        # ribs across the back panel's back face, and a groove round its edge
        rib = pack & ~top & (lu < P['pu0'] + 0.25) & (phase(lw, 1.7, P['pw0']) < 0.12) & \
            (lw > P['pw0'] + 0.9) & (lw < P['pw1'] - 0.9)
        put(rib, GREEN * 0.62 * g1); bz -= 0.4 * rib
        edge = pack & ~top & (lu < P['pu0'] + 0.25) & ((np.abs(np.abs(lv) - (P['pv'] - 0.45)) < 0.1))
        put(edge, GREEN * 0.62 * g1)
    sp = comp == WF.SHOULDER
    if sp.any():
        put(sp, house)
        mid = (P['sw0'] + P['sw1']) / 2
        groove = sp & ~top & (np.abs(lw - mid) < 0.1)
        put(groove, GREEN * 0.64 * g1)
    put(comp == WF.ARM, GOLD * 0.95 * g1)
    gun = comp == WF.GUN
    if gun.any():
        put(gun, GUN * g1)
        # a lighter top edge, a seam along the housing and two bands round it
        put(gun & top, GUN * 1.25 * g1)
        put(gun & ~top & (np.abs(lw - P['gw']) < 0.1), GUN * 0.7 * g1)
        put(gun & ((np.abs(lu - (P['gu0'] + 1.2)) < 0.1) | (np.abs(lu - (P['gu0'] + 3.2)) < 0.1)), GUN * 0.65 * g1)
    put(comp == WH.DRUM, GUN * 1.1 * g1)
    put(comp == WH.BARREL, STEEL * g1)
    put(comp == WH.MRING, STEEL_L * g1)
    belt = comp == WH.BELT
    if belt.any():
        # brass rounds, the link plates darker
        put(belt, BRASS * g1)
        put(belt & (np.abs(r.pv) > r.hv - 0.18), BRASS * 0.55 * g1)
        put(belt & (np.abs(r.pu) > r.hu - 0.06), BRASS * 0.5 * g1)
    put(comp == WH.HANDLE, STEEL_D * 1.2 * g1)
    put(comp == WF.ANT, BLACK * g1)
    put(comp == WF.ANTBASE, STEEL_D * g1)
    lamp = comp == WH.LAMPC
    put(lamp, LAMP)
    emit += (lamp * 70.0)[..., None] * np.array([1.0, 0.6, 0.2])
    # ---------------------------------------------------------------- legs
    put(comp == WF.PELVIS, OLIVE * g1)
    put(comp == WF.HIPJ, STEEL * 0.8 * g1)
    thigh = comp == WF.THIGH
    if thigh.any():
        put(thigh, GOLD * 0.95 * g1)
        # the armour plate over the thigh's front (Westwood's render): its outline as a groove
        fr = thigh & (r.pw > r.hw - 0.3)
        outline = fr & ((np.abs(np.abs(r.pv) - (r.hv - 0.45)) < 0.09) | (np.abs(r.pu - (r.hu - 0.7)) < 0.09) |
                        (np.abs(r.pu + (r.hu - 0.9)) < 0.09))
        put(outline, GOLD * 0.55 * g1); bz -= 0.3 * outline
    put(comp == WF.KNEE, STEEL * g1)
    shin = comp == WF.SHIN
    if shin.any():
        # scuffed and dirty (the render's shins are caked with dirt)
        b = blotch(r, 0.55)
        dirt = np.clip((b - 0.45) * 2.2, 0, 1) * 0.55 + dust * 0.6
        base = GOLD * (1 - 0.18 * np.clip(b - 0.3, 0, 1))[..., None] * g1
        put(shin, base * (1 - dirt[..., None]) + GRIME * dirt[..., None])
    put(comp == WF.ANKLE, STEEL * 0.85 * g1)
    for c in (WF.FOOT, WH.TOE):
        foot = comp == c
        if foot.any():
            put(foot, (GOLD * 0.97 * g1) * (1 - dust[..., None]) + GRIME * dust[..., None])
            put(foot & (z < 0.45), OLIVE * 0.8 * g1)
            if c == WH.TOE:
                put(foot & (r.pu > r.hu - 0.55), STEEL_D * 1.1 * g1)       # the claw tips
    # the fill light from the camera on the sides that face it (EA's HD units are front-lit)
    cam = r.cam
    tc = np.array([cam.T[0] * cam.cE, cam.T[1] * cam.cE, cam.sE]); tc = tc / np.linalg.norm(tc)
    nf = np.clip(r.nx * tc[0] + r.ny * tc[1] + r.nz * tc[2], 0, 1) * (1 - np.clip(r.nz, 0, 1))
    if occ is not None:
        nf = nf * (1 - 0.85 * np.clip(occ, 0, 1))
    emit = emit + alb * (FILL * nf)[..., None]
    return alb, (np.zeros(sh, np.float32), np.zeros(sh, np.float32), bz), emit


def trim_mask(r, alb):
    g = (alb[..., 1] > 1.6 * np.maximum(alb[..., 0], alb[..., 2])) & (alb[..., 1] > 40)
    return r.hitmask & g & np.isin(r.comp, HOUSE_COMPS)
