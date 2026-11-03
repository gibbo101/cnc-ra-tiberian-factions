#!/usr/bin/env python3
"""Render the C&C3 tanks' and vehicles' weapon effects as HD anim frames, from C&C3's own effect textures.

C&C3 draws these with particle systems whose layouts are not decoded; each piece here is built from the textures the
weapon's FX lists name, timed by eye against them. The launcher draws an exported sprite unrotated, so anything
with a direction is baked per direction. Additive light (fire tongues, flares) is baked to straight alpha as
c3_rail_beam.py does; fireballs and smoke are composited over it by their own alpha.

Flame Tank (NODFlameTankFlamer: FlameTankFire, FlameTankAdd02, FlameTankGround, NODFlameTankPilotFire):
  C3FLMN, C3FLMNE ... C3FLMNW  the flame stream from the nozzle, one per direction, 16 frames; the anim's centre is
                               the nozzle and the stream reaches STREAM_CELLS.
  C3FLMHIT                     the fire where the stream lands, 16 frames.
  C3FLMPIL                     the pilot light at each nozzle, an 8-frame loop.
Stealth Tank (NODStealthTankRocket):
  C3STMIS   the rocket, 32 facings counter-clockwise from north (BodyShape order), its exhaust lit.
  C3STTRL   a puff of its smoke trail, 12 frames.
  C3STMZ    the launch flash, 9 frames (FXBulletHit's own 9).
  C3STHIT   the impact, 16 frames.
Beam Cannon (NODBeamCannonLaser, drawn with the Obelisk's red beam, FXObeliskLaser):
  C3BMCHG   the charge swelling at the emitter before it fires, 16 frames.
  C3BMGLOW, C3BMMZ, C3BMHIT  the glow laid along the beam, the muzzle flash and the impact: c3_rail_beam.py's pieces
                             in the Obelisk's red.
Pitbull (GDIPitbullRocketWeapon fires the Stealth Tank's rocket, trail and hit: C3STMIS, C3STTRL, C3STHIT):
  C3PBMZ    the rocket launch flash (GDIMissleFire), 8 frames.
  C3PBSHL   the Mortar upgrade's shell (GDIPitBullArtilleryProjectile), 32 facings, its exhaust lit.
  C3MEDEXP  where the shell lands (FX_MediumXplosion): flash, fireball, flames, thrown dirt and a shock ring, 16 frames.
Guardian APC (GDIAPCAutoCannon):
  C3APCMZN ... C3APCMZNW  the autocannon's muzzle flash along the barrel, one per direction, 4 frames.

Inputs: resources/custom-art/c3-tank-fx/ (C&C3's static stream) and c3_rail_beam.py's textures; C3_ART_DIR holding
renders/stealthmissile/ and renders/pitbullshell/ from c3_render.py (the npz files from
tools/cnc3/c3_extract_model.py, workspace).
Writes the ZIPs and tiles where scripts/asset_packs.py routes the names.
Usage: c3_tank_fx.py [NAME ...]   (every effect when no names are given)
License: GPL v3.
"""
import io
import json
import math
import os
import sys
import zipfile

import numpy as np
from PIL import Image

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS)
import asset_packs  # noqa: E402
import c3_rail_beam as rail  # noqa: E402
from ts_gen_sonicwave import patch_tileset  # noqa: E402

TEX = os.path.join(SCRIPTS, "..", "resources", "custom-art", "c3-tank-fx")
ART = os.environ.get("C3_ART_DIR")
SS = 2
UNIT = rail.UNIT          # HD px per C&C3 world unit
CELL = 128                # HD px per cell
STREAM_CELLS = 2.0
DIRECTIONS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
MISSILE_RENDER_PPU = 26.0

# Obelisk red, read off FXObeliskLaser's glow round its white core
RED = {"halo": [(0, (1, .25, .15)), (.35, (.9, .15, .08)), (.7, (0, 0, 0)), (1, (0, 0, 0))],
       "flash": [(0, (1, .6, .5)), (.5, (1, .3, .2)), (1, (0, 0, 0))],
       "glow": [(0, (1, .55, .4)), (.4, (1, .3, .15)), (1, (0, 0, 0))],
       "spark": [(0, (1, .45, .3)), (.5, (.8, .2, .1)), (1, (0, 0, 0))]}


def load(name):
    """The named FX texture as float RGBA in 0..1."""
    return np.asarray(Image.open(os.path.join(TEX, name + ".png")).convert("RGBA"), np.float32) / 255.0


T_SCROLL = load("FXFireScroll")       # 4 x 4 flame tongues, additive
T_BALL = load("FXFireball4x4")        # 4 x 4 fireball, alpha-blended
T_FLARE2 = load("FXLenzFlare02")
T_FLARE4 = load("FXLenzFlare04")
T_HIT = load("FXBulletHit")           # 3 x 3 spark burst, additive
T_SMOKE = load("FXSmoke2x2_02")       # 2 x 2 puffs, white by alpha
T_MUZZLE = load("FXMuzzle")           # atlas: star flash top left, side-on streak top right, burst bottom right
T_RING = load("FXRing01")             # shock ring, additive
T_DIRT = load("FXDirtClumps")         # thrown dirt, by alpha


def cell(t, grid, i):
    """Cell i (row-major) of a grid x grid flipbook."""
    h, w = t.shape[0] // grid, t.shape[1] // grid
    r, c = divmod(i % (grid * grid), grid)
    return t[r * h:(r + 1) * h, c * w:(c + 1) * w]


class Frame:
    """A supersampled frame: premultiplied colour and alpha composited over, plus additive light."""

    def __init__(self, size):
        self.size = size
        self.rgb = np.zeros((size * SS, size * SS, 3), np.float32)
        self.a = np.zeros((size * SS, size * SS), np.float32)
        self.light = np.zeros((size * SS, size * SS, 3), np.float32)

    def _place(self, t, cx, cy, size, angle):
        """(rows, cols, sampled RGBA) of texture t as a square size px wide, turned by angle, centred on (cx, cy).
        The square's rim fades out, so a flipbook cell whose art runs to its edge shows no straight edge."""
        S = self.size * SS
        cx, cy, size = cx * SS, cy * SS, size * SS
        r = size * 0.75
        x0, x1 = int(max(cx - r, 0)), int(min(cx + r + 1, S))
        y0, y1 = int(max(cy - r, 0)), int(min(cy + r + 1, S))
        if x1 <= x0 or y1 <= y0 or size <= 0:
            return None
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
        ca, sa = math.cos(angle), math.sin(angle)
        u = (dx * ca + dy * sa) / size + 0.5
        v = (-dx * sa + dy * ca) / size + 0.5
        ok = ((u >= 0) & (u <= 1) & (v >= 0) & (v <= 1))[..., None]
        rim = np.clip((0.5 - np.maximum(abs(u - 0.5), abs(v - 0.5))) / 0.12, 0, 1)[..., None]
        return slice(y0, y1), slice(x0, x1), np.where(ok, rail.bilinear(t, u, v, wrap_v=False) * rim, 0)

    def add(self, t, cx, cy, size, colour, angle=0.0):
        """Adds texture t's colour as light, tinted."""
        p = self._place(t, cx, cy, size, angle)
        if p:
            self.light[p[0], p[1]] += p[2][..., :3] * np.array(colour, np.float32)

    def over(self, t, cx, cy, size, tint=(1, 1, 1), opacity=1.0, angle=0.0):
        """Composites texture t over the frame by its alpha, tinted."""
        p = self._place(t, cx, cy, size, angle)
        if p:
            a = p[2][..., 3] * opacity
            ys, xs = p[0], p[1]
            colour = p[2][..., :3] * np.array(tint, np.float32)
            self.rgb[ys, xs] = colour * a[..., None] + self.rgb[ys, xs] * (1 - a[..., None])
            self.a[ys, xs] = a + self.a[ys, xs] * (1 - a)

    def image(self):
        """Straight-alpha RGBA: light keeps its hue when overbright, and is at least as opaque as it is bright."""
        rgb = self.rgb + self.light
        peak = np.maximum(rgb.max(axis=2, keepdims=True), 1.0)
        rgb = rgb / peak
        a = np.maximum(self.a[..., None], rgb.max(axis=2, keepdims=True))
        pm = np.concatenate([rgb, a], 2).clip(0, 1)
        pm = pm.reshape(self.size, SS, self.size, SS, 4).mean((1, 3))
        al = pm[..., 3:]
        st = np.where(al > 1e-3, pm[..., :3] / np.maximum(al, 1e-3), 0)
        return Image.fromarray((np.concatenate([st, al], 2).clip(0, 1) * 255).astype(np.uint8), "RGBA")


def write_zip(name, frames):
    """Each frame centred on its point, cropped symmetrically round its art, and its tiles."""
    path = asset_packs.art_zip(name, "VFX")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    low = name.lower()
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for i, img in enumerate(frames):
            W, H = img.size
            bb = img.getbbox() or (W // 2 - 1, H // 2 - 1, W // 2 + 1, H // 2 + 1)
            x0, y0 = min(bb[0], W - bb[2]), min(bb[1], H - bb[3])
            box = (x0, y0, W - x0, H - y0)
            buf = io.BytesIO()
            img.crop(box).save(buf, format="TGA")
            z.writestr(f"{low}-{i:04d}.tga", buf.getvalue())
            z.writestr(f"{low}-{i:04d}.meta", json.dumps({"size": [W, H], "crop": list(box)}))
    patch_tileset(asset_packs.tileset_xml(name, "VFX"), name, len(frames))
    print(f"wrote {path} ({len(frames)} frames)")


def fade(age, start, end):
    """1 until age reaches start, falling to 0 at end."""
    return float(np.clip((end - age) / max(end - start, 1e-6), 0, 1))


# ---- Flame Tank -------------------------------------------------------------------------------------------------

STREAM_FRAMES = 16
EMIT_FRAMES = 8            # puffs leave the nozzle over the first half; the rest burns out
TRAVEL_FRAMES = 6          # frames a puff takes to reach the end of the stream


def stream_puffs(rng):
    """Each puff of a burst: emit frame, lateral jitter, flipbook offsets, spin and lift."""
    puffs = []
    for k in range(EMIT_FRAMES * 2):
        puffs.append(dict(t0=k / 2, side=rng.normal(0, 0.06), cell=int(rng.integers(16)),
                          ball=int(rng.integers(4)), spin=rng.uniform(-.4, .4), lift=rng.uniform(4, 10)))
    return puffs


def flame_stream(f, heading, puffs):
    """Frame f of the stream heading (radians, 0 = north, clockwise) from the nozzle at the frame centre: flame
    tongues licking along it, tips away from the nozzle, over fireballs once a puff is under way."""
    reach = STREAM_CELLS * CELL
    size = int(2 * (reach + 70))
    fr = Frame(size)
    c = size / 2
    ux, uy = math.sin(heading), -math.cos(heading)
    for p in sorted(puffs, key=lambda q: -q["t0"]):
        age = f - p["t0"]
        if age < 0:
            continue
        s = min(age / TRAVEL_FRAMES, 1.0)
        after = max(age - TRAVEL_FRAMES, 0.0)
        burn = fade(age, TRAVEL_FRAMES, TRAVEL_FRAMES + 5)
        if burn <= 0:
            continue
        dist = reach * (1 - (1 - s) ** 1.6) + 6 * after
        lat = p["side"] * dist
        x = c + ux * dist - uy * lat
        y = c + uy * dist + ux * lat - p["lift"] * s - 5 * after
        width = 22 + 84 * s + 10 * after
        tongue = cell(T_SCROLL, 4, p["cell"] + int(age))
        fr.add(tongue, x, y, width * 1.15, np.array((1.0, .78, .5)) * 1.6 * burn, heading + p["spin"])
        if s > 0.25:
            ball = cell(T_BALL, 4, min(p["ball"] + int(age * 1.2), 15))
            fr.over(ball, x, y, width * 0.95, opacity=0.75 * burn, angle=p["spin"] * 3)
    if f < EMIT_FRAMES + 2:
        fr.add(T_FLARE2, c, c, 36, np.array((1.0, .7, .35)) * 1.4 * fade(f, EMIT_FRAMES - 2, EMIT_FRAMES + 2))
    return fr.image()


def flame_hit(f):
    """Fire where the stream lands: a fireball rolling up with tongues licking over it."""
    fr = Frame(176)
    c = 88
    fr.over(cell(T_BALL, 4, f), c, c - f * 1.5, 70 + 4 * f, opacity=fade(f, 10, 16))
    for i, dx in enumerate((-14, 6, 16)):
        if f >= i * 2:
            age = f - i * 2
            fr.add(cell(T_SCROLL, 4, age + i * 5), c + dx, c - 18 - age * 2, 48 + 2 * age,
                   np.array((1.0, .75, .45)) * 1.4 * fade(age, 8, 14))
    return fr.image()


def pilot_light(f):
    """The small flame kept lit at a nozzle: a looping tongue with a glow."""
    fr = Frame(48)
    fr.add(cell(T_SCROLL, 4, f * 2), 24, 20, 22, (1.0, .7, .4))
    fr.add(T_FLARE2, 24, 24, 26, (.9, .5, .2))
    return fr.image()


# ---- Stealth Tank -----------------------------------------------------------------------------------------------

def missile(f, model="stealthmissile"):
    """The projectile at facing f, packed at UNIT px per C&C3 unit, with its exhaust lit at the tail."""
    im = Image.open(f"{ART}/renders/{model}/frame-{f:04d}.png").convert("RGBA")
    k = UNIT / MISSILE_RENDER_PPU
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    fr = Frame(64)
    yaw = math.radians(90 + f * 11.25)
    tail = 3.6 * UNIT
    tx = 32 - math.cos(yaw) * tail
    ty = 32 + math.sin(yaw) * tail * math.sin(math.radians(32))
    fr.add(T_FLARE4, tx, ty, 26, (1.0, .7, .35))
    glow = fr.image()
    out = Image.new("RGBA", (64, 64))
    out.alpha_composite(glow)
    out.alpha_composite(im, ((64 - im.width) // 2, (64 - im.height) // 2))
    return out


def trail_puff(f, quadrant):
    """A puff of the rocket's smoke, swelling and thinning."""
    fr = Frame(64)
    fr.over(cell(T_SMOKE, 2, quadrant), 32, 32, 18 + 3 * f, tint=(.7, .68, .66), opacity=fade(f, 2, 12))
    return fr.image()


def launch_flash(f):
    """The Stealth Tank's rocket leaving its pod: a burst and a fading flare."""
    fr = Frame(96)
    fr.add(cell(T_HIT, 3, f), 48, 48, 64, (1.0, .85, .6))
    if f < 4:
        fr.add(T_FLARE4, 48, 48, 70, np.array((1.0, .65, .3)) * (1 - f / 4))
    return fr.image()


def missile_hit(f):
    """The rocket's impact: a flash, the fireball and the debris sparks."""
    fr = Frame(192)
    c = 96
    fr.over(cell(T_BALL, 4, f), c, c - f, 84 + 3 * f, opacity=fade(f, 9, 16))
    if f < 9:
        fr.add(cell(T_HIT, 3, f), c, c, 110, np.array((1.0, .8, .55)) * .8)
    if f < 5:
        fr.add(rail.T_BLAST, c, c, 120 - 6 * f, np.array((1.0, .75, .45)) * (1 - f / 5), f * .3)
        fr.add(T_FLARE4, c, c, 150, np.array((1.0, .7, .4)) * (1 - f / 5))
    return fr.image()


# ---- Pitbull and Guardian APC ----------------------------------------------------------------------------------

def rocket_launch(f):
    """The Pitbull's rocket leaving its pod: a flare and a short tongue of fire, fading."""
    fr = Frame(96)
    fr.add(T_FLARE4, 48, 48, 64 - 4 * f, np.array((1.0, .7, .35)) * (1 - f / 8))
    fr.add(cell(T_SCROLL, 4, f * 2), 48, 46, 34, np.array((1.0, .75, .45)) * 1.3 * fade(f, 2, 8))
    return fr.image()


def medium_explosion(f, clumps):
    """The mortar shell's blast: a white flash, a rolling fireball with flames, a shock ring and thrown dirt."""
    fr = Frame(256)
    c = 128
    if f < 4:
        fr.add(rail.T_BLAST, c, c, 150 - 10 * f, np.array((1.0, .85, .6)) * (1 - f / 4), f * .4)
    fr.add(T_RING, c, c, 60 + 22 * f, np.array((1.0, .8, .6)) * .7 * fade(f, 2, 8))
    for dx, dy, vx, vy, spin in clumps:
        fr.over(T_DIRT, c + dx + vx * f, c + dy + vy * f + 1.2 * f * f, 40, tint=(.55, .48, .4),
                opacity=fade(f, 6, 12), angle=spin * f)
    fr.over(cell(T_BALL, 4, f), c, c - 2 * f, 100 + 4 * f, opacity=fade(f, 10, 16))
    for i, dx in enumerate((-22, 0, 20)):
        if f >= 2 + i:
            age = f - 2 - i
            fr.add(cell(T_SCROLL, 4, age + 4 * i), c + dx, c - 30 - 3 * age, 60,
                   np.array((1.0, .7, .4)) * fade(age, 6, 11))
    return fr.image()


def apc_muzzle(f, heading):
    """The autocannon's flash at the frame centre: a star at the muzzle and the streak thrown along the heading
    (the streak lies along its texture's u axis, so it turns a quarter less than the heading)."""
    fr = Frame(160)
    c = 80
    k = (1 - f / 4)
    ux, uy = math.sin(heading), -math.cos(heading)
    streak = T_MUZZLE[0:256, 256:512]
    fr.add(streak, c + ux * 30, c + uy * 30, 92 - 10 * f, np.array((1.0, .9, .7)) * 1.4 * k, heading - math.pi / 2)
    fr.add(T_MUZZLE[0:128, 0:128], c, c, 40, np.array((1.0, .95, .8)) * 1.2 * k, f * .5)
    fr.add(rail.T_FLARE, c, c, 50, np.array((1.0, .8, .5)) * .6 * k)
    return fr.image()


# ---- Beam Cannon ------------------------------------------------------------------------------------------------

def beam_charge(f):
    """The charge swelling at the emitter: a red flare that grows and brightens, flickering, until the shot."""
    fr = Frame(128)
    s = (f + 1) / 16
    flick = 0.85 + 0.15 * math.sin(f * 2.3)
    fr.add(rail.T_FLARE, 64, 64, 24 + 70 * s, np.array((1.0, .2, .12)) * (0.4 + 1.2 * s) * flick, f * .2)
    fr.add(T_FLARE4, 64, 64, 10 + 30 * s, np.array((1.0, .75, .7)) * s)
    return fr.image()


def build(names):
    """Writes the named effects (all when names is empty), their random layouts drawn once from a fixed seed."""
    rng = np.random.default_rng(11)
    puffs = stream_puffs(rng)
    beam_flash = {"flash": rng.uniform(18, 24), "angle": rng.uniform(-7, 7)}
    glows = [(rng.uniform(24, 36), rng.uniform(0, 7), rng.uniform(-.1, .1)) for _ in range(8)]
    sparks = []
    for _ in range(14):
        a, v = rng.uniform(0, 2 * math.pi), rng.uniform(8, 22)
        sparks.append((v * math.cos(a), v * math.sin(a), rng.uniform(.65, .8), rng.uniform(2, 4),
                       rng.uniform(-40, 40) / 255))
    quadrants = rng.integers(4, size=1)
    clumps = []
    for _ in range(7):
        a, v = rng.uniform(0, 2 * math.pi), rng.uniform(4, 9)
        clumps.append((math.cos(a) * 10, math.sin(a) * 6, math.cos(a) * v, math.sin(a) * v * .6 - 6,
                       rng.uniform(-.3, .3)))
    effects = {f"C3FLM{d}": lambda d=d: [flame_stream(f, math.radians(45 * DIRECTIONS.index(d)), puffs)
                                         for f in range(STREAM_FRAMES)] for d in DIRECTIONS}
    effects.update({
        "C3FLMHIT": lambda: [flame_hit(f) for f in range(16)],
        "C3FLMPIL": lambda: [pilot_light(f) for f in range(8)],
        "C3STMIS": lambda: [missile(f) for f in range(32)],
        "C3STTRL": lambda: [trail_puff(f, int(quadrants[0])) for f in range(12)],
        "C3STMZ": lambda: [launch_flash(f) for f in range(9)],
        "C3STHIT": lambda: [missile_hit(f) for f in range(16)],
        "C3PBMZ": lambda: [rocket_launch(f) for f in range(8)],
        "C3PBSHL": lambda: [missile(f, "pitbullshell") for f in range(32)],
        "C3MEDEXP": lambda: [medium_explosion(f, clumps) for f in range(16)],
        "C3BMCHG": lambda: [beam_charge(f) for f in range(16)],
        "C3BMGLOW": lambda: [rail.dot(f, rail.GLOW_FRAME, rail.GLOW_PX, RED["halo"], 1.0) for f in range(rail.FRAMES)],
        "C3BMMZ": lambda: [rail.muzzle(f, beam_flash, RED["flash"]) for f in range(rail.MUZZLE_FRAMES)],
        "C3BMHIT": lambda: [rail.impact(f, glows, sparks, RED["glow"], RED["spark"]) for f in range(rail.FRAMES)],
    })
    effects.update({f"C3APCMZ{d}": lambda d=d: [apc_muzzle(f, math.radians(45 * DIRECTIONS.index(d)))
                                                 for f in range(4)] for d in DIRECTIONS})
    unknown = set(names) - set(effects)
    if unknown:
        raise SystemExit(f"unknown effect(s): {', '.join(sorted(unknown))}")
    if (not names or {"C3STMIS", "C3PBSHL"} & set(names)) and not ART:
        raise SystemExit("set C3_ART_DIR (holding renders/stealthmissile/ and renders/pitbullshell/)")
    for name, make in effects.items():
        if not names or name in names:
            write_zip(name, make())


if __name__ == "__main__":
    build(sys.argv[1:])
