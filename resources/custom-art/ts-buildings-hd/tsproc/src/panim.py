"""The Power Plant's animations (TS GTPOWR_A, GTPOWR_B) and their previews against TS.
  A  the tower's lights: four rings of lamps, lit house green; a white-blue flash runs up the tower ring by
     ring (bottom ring at frame 9, then 0, 3, 6), fading over three frames.   12 healthy + 12 damaged
     (damaged: the second ring dead, one lamp left on the top ring and one on the third)
  B  the turbine turning: the window band and the housing's hatches, 10 degrees a frame.   12"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
import prender as PR, powr as PW

A_N = 12
FLASH_AT = (9, 0, 3, 6)                  # rings bottom .. top (P['lights_z']): the frame its flash starts
FADE = (1.0, 0.7, 0.45, 0.25)            # TS: 255 white, 206, 153, 101 (blue)
TURB_STEP = np.deg2rad(10.0)


def light_levels(t):
    out = []
    for f0 in FLASH_AT:
        k = (t - f0) % A_N
        out.append(FADE[k] if k < len(FADE) else 0.0)
    return out


def lights_ok(level):
    """which lamps work: rings bottom..top x azimuths (-15, 25, 97, 165, 235, 305)."""
    if level == 0:
        return [[True] * 6 for _ in range(4)]
    return [[True] * 6,                                       # bottom ring: all
            [False, True, False, False, False, False],        # next: only the front lamp
            [False] * 6,                                      # next: dead
            [True, False, False, False, False, False]]        # top ring: only the east lamp


OUT = '/home/claude/work/scratch/panim'
TS = '/home/claude/work/ts/ts-buildings-hd-handoff/02-TSPOWR/ts-original'


def render_idle(view_name, ss=2, level=0, turbines=(0,)):
    d = f'{OUT}/idle-{view_name}-{level}' + ('' if tuple(turbines) == (0,) else '-t' + ''.join(str(s + 1) for s in turbines))
    os.makedirs(d, exist_ok=True)
    view = PR.iso_view(ss) if view_name == 'iso' else PR.ra_view(8, ss)
    pr = PR.Prep(view, level=level, turbines=turbines)
    for t in range(A_N):
        img = pr.frame(turb_angle=t * TURB_STEP, lights=light_levels(t), lights_ok=lights_ok(level))
        img.save(f'{d}/t{t:02d}.png')
        print(view_name, level, t, flush=True)


def ts_frame(t, level=0):
    K, OX, OY = PR.ISO_K, -30.0, -53.5
    base = Image.open(f'{TS}/GTPOWR/frames/{level:02d}.png').convert('RGBA')
    base.alpha_composite(Image.open(f'{TS}/GTPOWR_A/frames/{t + 12 * level:02d}.png').convert('RGBA'))
    base.alpha_composite(Image.open(f'{TS}/GTPOWR_B/frames/{t:02d}.png').convert('RGBA'))
    ts = np.array(base); yy, xx = np.mgrid[0:256, 0:256]
    tx = np.floor((xx + 0.5 - OX) / K).astype(int); ty = np.floor((yy + 0.5 - OY) / K).astype(int)
    ok = (tx >= 0) & (tx < 96) & (ty >= 0) & (ty < 96)
    out = np.zeros((256, 256, 4), np.uint8); out[ok] = ts[ty[ok], tx[ok]]
    return Image.fromarray(out)


def gif(path, level=0, Z=2):
    BG = (90, 100, 80, 255)
    frames = []
    for t in range(A_N):
        ims = [ts_frame(t, level), Image.open(f'{OUT}/idle-iso-{level}/t{t:02d}.png'), Image.open(f'{OUT}/idle-ra-{level}/t{t:02d}.png')]
        W = sum(i.width * Z for i in ims) + 24; H = max(i.height * Z for i in ims) + 34
        S = Image.new('RGBA', (W, H), (30, 30, 30, 255)); d = ImageDraw.Draw(S); x = 0
        for k, im in enumerate(ims):
            b = Image.new('RGBA', im.size, BG); b.alpha_composite(im.convert('RGBA'))
            S.paste(b.resize((im.width * Z, im.height * Z), Image.NEAREST if k == 0 else Image.LANCZOS), (x, 34 + (H - 34 - im.height * Z) // 2))
            d.text((x + 6, 4), ('TS original (x3.36)', 'HD, TS angle', 'HD, RA grid')[k], fill=(255, 255, 0, 255))
            x += im.width * Z + 12
        d.text((6, 18), f'{("healthy", "damaged")[level]} idle  frame {t:02d}: tower lights (A) + turbine in slot 1 (B)', fill=(255, 255, 255, 255))
        frames.append(S.convert('RGB').quantize(colors=255, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=110, loop=0, optimize=True)


def gif_pods(path, Z=2):
    """the idle loop with one, two and three power pods, TS angle over RA grid."""
    BG = (90, 100, 80, 255)
    frames = []
    sets = (('', '1 pod (slot 1: east)'), ('-t12', '2 pods (slots 1, 2: east, south)'), ('-t123', '3 pods (slots 1-3: east, south, west)'))
    for t in range(A_N):
        cols = []
        for tag, title in sets:
            cols.append((Image.open(f'{OUT}/idle-iso-0{tag}/t{t:02d}.png'), Image.open(f'{OUT}/idle-ra-0{tag}/t{t:02d}.png'), title))
        W = 3 * 256 * Z + 24; H = 34 + (256 + 272) * Z + 12
        S = Image.new('RGBA', (W, H), (30, 30, 30, 255)); d = ImageDraw.Draw(S)
        for k, (iso, ra, title) in enumerate(cols):
            x = k * (256 * Z + 12)
            for j, im in enumerate((iso, ra)):
                b = Image.new('RGBA', im.size, BG); b.alpha_composite(im.convert('RGBA'))
                S.paste(b.resize((im.width * Z, im.height * Z), Image.LANCZOS), (x, 34 + j * (256 * Z + 12)))
            d.text((x + 6, 4), title, fill=(255, 255, 0, 255))
        d.text((6, 18), f'idle frame {t:02d}: tower lights (A) + turbines (B).  Top: TS angle.  Bottom: RA grid.', fill=(255, 255, 255, 255))
        frames.append(S.convert('RGB').quantize(colors=255, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=110, loop=0, optimize=True)


if __name__ == '__main__':
    if sys.argv[1] == 'idle':
        tb = tuple(int(c) - 1 for c in sys.argv[5]) if len(sys.argv) > 5 else (0,)
        render_idle(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 2, int(sys.argv[4]) if len(sys.argv) > 4 else 0, tb)
    elif sys.argv[1] == 'gif-pods':
        gif_pods(sys.argv[2])
    elif sys.argv[1] == 'gif':
        gif(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 0)
