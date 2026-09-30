"""
The Construction Yard's animations, as TS plays them (GTCNST_A .. _D), rebuilt as overlay frames on the
building's canvas.  Each TS overlay holds its healthy frames first, then the damaged ones where it has them;
the second half of each SHP (TS's shadow frames) is left out - shadows are baked in here.

  A  the three roof fans turning                  10 healthy + 10 damaged (only the south fan turns)
  B  the door lamp (a small yellow lamp, two opposite pale beams turning 18 degrees a frame) and a light
     running along the threshold floor from the door end to the west foot (frames 5-8, off for the
     rest); a cool marker light at the arch's west foot   10 (TS has no damaged set)
  C  the roof lamps: a dimming pulse runs south   15 healthy + 15 damaged (three lamps dead)
  D  producing: the hangar lights up inside (the vault's underside shows lit between the ribs, the
     hazard strip at the threshold glows), the claw builds a crate and sets it out on the apron, then the
     lights go down                                 20
"""
import numpy as np
from PIL import Image
from scipy import ndimage
import hd, yard as Y, ymat as M, ydamage as D, yrender as R

FAN_STEP = np.deg2rad(21.6)                  # 5 blades: 3 blade-periods per 10-frame loop
A_N = 10

# C: level of each roof lamp (south .. north) per frame, read from GTCNST_C (510 full, 445 .8, 339 .5, 315 .45,
# 255 .25, 200 .1)
_F = 1.0
C_HEALTHY = [[_F, _F, _F, _F, _F, _F, .8], [_F, _F, _F, _F, _F, .8, .25], [_F, _F, _F, _F, .8, .45, _F],
             [_F, _F, _F, .8, .45, _F, _F], [_F, _F, .8, .5, _F, _F, _F], [_F, .8, .5, _F, _F, _F, _F],
             [.8, .45, _F, _F, _F, _F, _F], [.5, _F, _F, _F, _F, _F, _F]] + [[_F] * 7] * 7
C_DAMAGED = [[_F, _F, 0, 0, _F, 0, .8], [_F, _F, 0, 0, _F, 0, .1], [_F, _F, 0, 0, .8, 0, _F],
             [_F, _F, 0, 0, .45, 0, _F], [_F, _F, 0, 0, _F, 0, _F], [_F, .8, 0, 0, _F, 0, _F],
             [.8, .45, 0, 0, _F, 0, _F], [.5, _F, 0, 0, _F, 0, _F]] + [[_F, _F, 0, 0, _F, 0, _F]] * 7

# B (TS GTCNST_B, 10 frames): the door lamp - a small yellow lamp whose two opposite pale beams turn in the
# wall's plane, 18 degrees a frame (along the wall at frame 0, up and down at frame 5) - and a light running
# along the threshold from the door end to the west foot (frames 5-8); over frames 9, 0-4 TS only brightens the
# arch's edge a touch as if it went on up and over - left out here (Luke's call); a small cool marker light
# stays lit at the arch's west foot.
B_ANGLE0, B_STEP = 0.0, np.deg2rad(18.0)          # beam angle in the wall's plane (0: along it, west/east)
RUN = {5: ('floor', -10.0, 0.55), 6: ('floor', -55.0, 1.0), 7: ('floor', -100.0, 1.0), 8: ('floor', -145.0, 0.9),
       9: ('arch', -176.0, 1.0), 0: ('arch', -156.0, 1.0), 1: ('arch', -120.0, 1.0), 2: ('arch', -85.0, 1.0),
       3: ('arch', -50.0, 1.0), 4: ('arch', -15.0, 0.7)}


def run_pos(t, p=Y.P):
    """where the running light is: on the threshold strip (a small warm light and its glow), or, while it
    goes over the arch, only a faint glint on the south rib's top front edge (TS barely brightens it)."""
    where, x, k = RUN[t % 10]
    if where == 'floor':
        return where, np.array([x, p['yS'] + 6.0, p['pad_h']]), np.array([0.0, 0.0, 1.0]), k
    zo = float(Y.roof_z(np.array([x]), p)[0])
    return where, np.array([x, p['yS'], zo + p['rib_up']]), np.array([0.0, 0.6, 0.8]), k


def door_lamp(p=Y.P):
    lx, lz = p['door_lamp']
    return np.array([lx, p['yS'] - 2.5, lz])


# D: producing
T_REST = (-76.0, 110.0, 66.0)


def d_state(i):
    """open (roof bays), light (inside), crate (x, y, size) or None, crane tip, claw drop."""
    L = [0, .4, .9, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, .8, .4, 0][i]
    O = 0.0                                              # TS keeps the roof shut: it only lights up inside
    crate = {4: (-45, 64, 5.0), 5: (-45, 64, 8.0), 6: (-45, 64, 11.0), 7: (-45, 64, 13.0), 8: (-45, 64, 14.0),
             9: (-45, 64, 14.0), 10: (-52, 88, 14.0), 11: (-60, 116, 14.0)}.get(i)
    tips = {0: T_REST, 1: T_REST, 2: (-73, 104, 66), 3: (-66, 92, 65), 4: (-52, 72, 64), 5: (-46, 65, 64),
            6: (-45, 64, 64), 7: (-45, 64, 64), 8: (-45, 64, 64), 9: (-45, 64, 64), 10: (-52, 88, 63),
            11: (-60, 116, 63), 12: (-66, 110, 64), 13: (-70, 108, 65), 14: (-74, 110, 66), 15: T_REST,
            16: T_REST, 17: T_REST, 18: T_REST, 19: T_REST}
    drop = {5: 34, 6: 38, 7: 40, 8: 40, 9: 38, 10: 36, 11: 40}.get(i, 34)
    return dict(open=O, light=L, crate=crate, tip=tips[i], drop=drop)


# ------------------------------------------------------------------------------------------ rendering
class Prep:
    """one geometry pass (ray-cast, normals, shadows, sky occlusion) reused for every material-only frame."""
    def __init__(self, view, level=0, dstate=None, prog=None):
        kw = {}
        if prog is not None:
            kw['prog'] = prog
        self.prog = prog
        if dstate is not None:
            kw = dict(open_roof=dstate['open'], crate=dstate['crate'],
                      crane_pose=dict(tip=dstate['tip'], claw_drop=dstate['drop']))
        self.model = D.model(level) if level else (lambda X, Yy, **k: Y.scene(X, Yy, **k))
        self.r = hd.Render(self.model, view, R.BOUNDS, R.ZMAX, **kw)
        self.occ = self.r.sky_occlusion()
        self.level = level
        self.view = view

    def frame(self, fan_angle=0.0, lamp_levels=None, door=1.0, light=0.0, fan_on=(True, True, True),
              beacon=None, run=None):
        """beacon: angle of the door lamp's beams (None: B off); run: B frame of the running light (None: off);
        light: the hangar's lights (D)."""
        r = self.r
        lamps = 0.0 if self.level else 1.0
        if self.prog is not None:
            lamps = min(lamps, 1.0 if self.prog.get('lamps', 1) >= 1 else 0.0)
            door = min(door, 1.0 if self.prog.get('door', 1) >= 1 else 0.0)
            if self.prog.get('lamps', 1) < 1:
                lamp_levels = None
        alb, (bx, by, bz), emit = M.materials(r, fan_angle=fan_angle, lamps=lamps, occ=self.occ,
                                              lamp_levels=lamp_levels, door=door, fan_on=fan_on)
        if self.level:
            alb = D.mats(r, alb, self.level)
            # lamps the overlay lights on the damaged building
            if lamp_levels is not None:
                lamp = r.comp == Y.LAMP
                drib_l, k_l, _ = Y.rib_index(r.y)
                lv = np.asarray(lamp_levels, np.float32)[k_l.astype(int)]
                emit = np.where(lamp[..., None], np.array([255, 196, 70.]) * (0.95 * lv)[..., None], emit)
            if door > 0:
                emit = np.where((r.comp == Y.DLAMP)[..., None], np.array([255, 250, 120.]) * 0.9 * door, emit)
        nx, ny, nz = r.nx + bx, r.ny + by, r.nz + bz
        nl = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-9
        nx, ny, nz = nx / nl, ny / nl, nz / nl
        ao = 0.86 + 0.14 * np.clip(r.z / 40.0, 0, 1)
        col = r.shade(alb, sky_occ=self.occ, ao=ao, normals=(nx, ny, nz)) + emit
        p = Y.P
        lights = []
        house = np.isin(r.comp, list(Y.HOUSE))
        if light > 0:
            # the hangar's lamps (they barely touch the green: TS shows no green lit inside)
            lights.append(((-72.0, -20.0, 80.0), np.array([1.0, 0.94, 0.8]), 2.2 * light, 260.0, 0.2))
            lights.append(((-60.0, 70.0, 60.0), np.array([1.0, 0.95, 0.82]), 2.0 * light, 170.0, 0.2))
            # the hangar filled with light: everything under the vault (floor, back wall, the vault's underside)
            zi = Y.roof_inner(r.x, p)
            inside = (r.x > p['xw']) & (r.y < p['yS'] + 2) & (r.y > p['yN']) & (r.z < zi - 0.5) & (r.comp != Y.RIB)
            edge = np.clip((p['x_open'] - 2 - r.x) / 14.0, 0, 1)              # fades out at the east side
            depth = np.clip((p['yS'] - r.y) / (p['yS'] - p['yN']), 0, 1)
            fill = inside * edge * (1.15 - 0.55 * depth) * light
            col = col + alb * np.array([1.0, 0.95, 0.84]) * fill[..., None]
            # the hazard strip at the threshold glows
            haz = (r.comp == Y.PAD) & (r.y > p['yS'] + 1) & (r.y < p['yS'] + 11) & (r.x > p['xw'] + 6) & (r.x < p['x_open'] - 2)
            yel = haz & (np.mod(r.x - r.y + 10, 20.0) < 10.0)
            col = col + yel[..., None] * np.array([255, 150, 40.]) * 0.55 * light
        if run is not None:
            # the running light's glow round its spot, and the cool marker at the arch's west foot
            where, P0, nrm, k = run_pos(run)
            if where == 'floor':                  # over the arch (TS's faint glint) it is left out
                lights.append((tuple(P0 + nrm * 5.0), np.array([1.0, 0.6, 0.22]), 2.4 * k, 26.0, 1.0))
            lights.append(((p['xw'] + 5.0, p['yS'] + 3.0, p['pad_h'] + 2.0), np.array([0.78, 0.84, 1.0]), 0.9, 13.0, 1.0))
        for (pos, lc, inten, rad, on_house) in lights:
            dx, dy, dz = pos[0] - r.x, pos[1] - r.y, pos[2] - r.z
            dist = np.sqrt(dx * dx + dy * dy + dz * dz) + 1e-6
            ndl = np.clip((nx * dx + ny * dy + nz * dz) / dist, 0, 1)
            fall = np.clip(1 - dist / rad, 0, 1) ** 2 * np.where(house, on_house, 1.0)
            col = col + alb * lc * (inten * fall * ndl)[..., None]
        if run is not None:
            # the light itself: a small bright spot running along the strip (none on the arch)
            where, P0, _, k = run_pos(run)
            if where == 'floor':
                d0 = np.sqrt((r.x - P0[0]) ** 2 + (r.y - P0[1]) ** 2 + (r.z - P0[2]) ** 2)
                core = np.clip(1 - d0 / 3.5, 0, 1) ** 1.5
                col = col + core[..., None] * np.array([255, 185, 90.]) * 0.9 * k
        if beacon is not None:
            col = self._beacon(col, alb, (nx, ny, nz), beacon)
        return r.compose(col)

    # ---------------------------------------------------------------------------------------------- B
    def _cam(self):
        v = self.view
        return np.array([v.T[0] * v.cE, v.T[1] * v.cE, v.sE])               # towards the camera

    def _beacon(self, col, alb, n, ang):
        """the door lamp: two opposite beams turning in the wall's plane, lighting streaks on the wall (and the
        doorway below it), the beams themselves as pale shafts (hidden behind anything in front of them - the
        crane), and a small steady glow round the lamp."""
        r = self.r; v = self.view
        L = door_lamp()
        Cm = self._cam()
        dirs = []
        for a_ in (ang, ang + np.pi):
            d = np.array([-np.cos(a_), -0.05, np.sin(a_)]); dirs.append(d / np.linalg.norm(d))
        # light on the surfaces the beams reach (those facing the lamp)
        vx, vy, vz = r.x - L[0], r.y - L[1], r.z - L[2]
        dist = np.sqrt(vx * vx + vy * vy + vz * vz) + 1e-6
        best = np.zeros_like(dist)
        for d in dirs:
            ca = np.clip((vx * d[0] + vy * d[1] + vz * d[2]) / dist, -1, 1)
            best = np.maximum(best, np.exp(-(np.arccos(ca) / 0.27) ** 2))
        fall = np.clip(1 - dist / 46.0, 0, 1) ** 1.5
        ndl = np.clip(-(n[0] * vx + n[1] * vy + n[2] * vz) / dist, 0, 1)
        face = (ndl > 0) * (0.45 + 0.55 * np.sqrt(ndl))
        beam = best * fall * face * np.clip((dist - 2.6) / 2.0, 0, 1) * 2.0
        col = col + alb * np.array([1.0, 0.97, 0.86]) * beam[..., None]
        # the shafts: nearest approach of each pixel's line of sight (in front of its surface) to the beam's axis
        depth = Cm[0] * r.x + Cm[1] * r.y + Cm[2] * r.z
        shaft = np.zeros_like(dist)
        for d in dirs:
            c = float(np.dot(Cm, d))
            dd = Cm[0] * vx + Cm[1] * vy + Cm[2] * vz
            e = d[0] * vx + d[1] * vy + d[2] * vz
            s = (e * c - dd) / max(1.0 - c * c, 1e-3)            # along the sight line, towards the camera
            u = e + s * c                                        # along the beam
            qx = vx + s * Cm[0] - u * d[0]; qy = vy + s * Cm[1] - u * d[1]; qz = vz + s * Cm[2] - u * d[2]
            q = np.sqrt(qx * qx + qy * qy + qz * qz)
            rad = 1.0 + 0.15 * np.clip(u, 0, None)
            along = np.clip((u - 2.4) / 3.0, 0, 1) * np.clip(1 - u / 42.0, 0, 1) ** 1.3
            vis = np.clip(s / rad + 0.5, 0, 1)
            shaft = np.maximum(shaft, np.exp(-(q / rad) ** 2) * along * vis)
        col = col + (shaft * 0.7)[..., None] * np.array([255, 246, 215.])
        # the lamp's small glow (not over anything in front of it)
        ss = v.ss
        H_, W_ = col.shape[:2]
        yy, xx = np.mgrid[0:H_, 0:W_]
        sx, sy = v.project(np.array([L[0]]), np.array([L[1]]), np.array([L[2]]))
        rr = np.hypot((xx + 0.5) / ss - sx[0], (yy + 0.5) / ss - sy[0])
        ok = depth <= float(np.dot(Cm, L)) + 3.0
        halo = (np.exp(-(rr / 1.5) ** 2) * 0.5 + np.exp(-(rr / 4.0) ** 2) * 0.14) * ok
        return col + halo[..., None] * np.array([255, 240, 150.])


def overlay(base, frame, thr=3):
    """the pixels a frame changes against the base frame (drawn on top of it in the game)."""
    a = np.array(base).astype(np.int16); b = np.array(frame).astype(np.int16)
    diff = np.abs(a - b).max(axis=2) > thr
    diff = ndimage.binary_dilation(diff, iterations=1)
    out = np.zeros_like(b)
    out[diff] = b[diff]
    return Image.fromarray(out.astype(np.uint8), 'RGBA')
