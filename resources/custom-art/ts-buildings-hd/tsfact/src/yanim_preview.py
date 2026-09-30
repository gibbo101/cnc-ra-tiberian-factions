"""Animated previews: TS's own yard (base + its overlays) next to ours (TS angle and RA grid).
    python3 yanim_preview.py idle iso|ra [ss]     idle loop frames (A fans + B door lamp/running light + C lamps)
    python3 yanim_preview.py prod iso|ra [ss]     producing (D) frames
    python3 yanim_preview.py gif-idle | gif-prod  the side-by-side GIFs"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw
import yanim as A, yrender as R

OUT = '/home/claude/work/scratch/anim'
TS = '/home/claude/work/ts/ts-buildings-hd-handoff/01-TSFACT/ts-original'
def render_idle(view_name, ss=4, n=30):
    """idle loop: fans (A, 10), roof lamps (C, 15), door beacon (B, 10) -> 30 frames."""
    os.makedirs(f'{OUT}/idle-{view_name}', exist_ok=True)
    view = R.iso_view(ss) if view_name == 'iso' else R.ra_view(52, ss)
    base = A.Prep(view)
    for t in range(n):
        img = base.frame(fan_angle=(t % A.A_N) * A.FAN_STEP, lamp_levels=A.C_HEALTHY[t % 15],
                         beacon=A.B_ANGLE0 + A.B_STEP * (t % 10), run=t % 10)
        img.save(f'{OUT}/idle-{view_name}/t{t:02d}.png')
        print(view_name, t, flush=True)


def render_prod(view_name, ss=4):
    """producing (D, 20 frames) with the fans and roof lamps carrying on."""
    os.makedirs(f'{OUT}/prod-{view_name}', exist_ok=True)
    view = R.iso_view(ss) if view_name == 'iso' else R.ra_view(52, ss)
    for t in range(20):
        st = A.d_state(t)
        pr = A.Prep(view, dstate=st)
        img = pr.frame(light=st['light'], fan_angle=(t % A.A_N) * A.FAN_STEP, lamp_levels=A.C_HEALTHY[t % 15])
        img.save(f'{OUT}/prod-{view_name}/t{t:02d}.png')
        print(view_name, t, flush=True)


def ts_prod(t):
    base = Image.open(f'{TS}/GTCNST/frames/00.png').convert('RGBA')
    for l in (f'{TS}/GTCNST_A/frames/{t % 10:02d}.png', f'{TS}/GTCNST_C/frames/{t % 15:02d}.png',
              f'{TS}/GTCNST_D/frames/{t:02d}.png'):
        base.alpha_composite(Image.open(l).convert('RGBA'))
    big = np.repeat(np.repeat(np.array(base), 3, 0), 3, 1)
    return Image.fromarray(big[166:166 + 256, 42:42 + 384])


def gif_prod(path):
    BG = (90, 100, 80, 255)
    frames = []
    for t in range(20):
        S = Image.new('RGBA', (384 * 3 + 24, 360 + 34), (30, 30, 30, 255))
        d = ImageDraw.Draw(S)
        for k, (im, dy) in enumerate(((ts_prod(t), 52), (Image.open(f'{OUT}/prod-iso/t{t:02d}.png'), 52),
                                      (Image.open(f'{OUT}/prod-ra/t{t:02d}.png'), 0))):
            b = Image.new('RGBA', im.size, BG); b.alpha_composite(im.convert('RGBA'))
            S.paste(b, (k * 396, 34 + dy))
        d.text((6, 4), 'TS original (x3)', fill=(255, 255, 0, 255))
        d.text((402, 4), 'HD, TS angle', fill=(255, 255, 0, 255))
        d.text((798, 4), 'HD, RA grid', fill=(255, 255, 0, 255))
        d.text((6, 18), f'producing (D)  frame {t:02d}', fill=(255, 255, 255, 255))
        frames.append(S.convert('RGB').quantize(colors=255, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=120, loop=0, optimize=True)


def ts_idle(t):
    base = Image.open(f'{TS}/GTCNST/frames/00.png').convert('RGBA')
    for l in (f'{TS}/GTCNST_A/frames/{t % 10:02d}.png', f'{TS}/GTCNST_C/frames/{t % 15:02d}.png',
              f'{TS}/GTCNST_B/frames/{t % 10:02d}.png'):
        base.alpha_composite(Image.open(l).convert('RGBA'))
    big = np.repeat(np.repeat(np.array(base), 3, 0), 3, 1)
    return Image.fromarray(big[166:166 + 256, 42:42 + 384])


def gif_idle(path, n=30):
    BG = (90, 100, 80, 255)
    frames = []
    for t in range(n):
        S = Image.new('RGBA', (384 * 3 + 24, 360 + 34), (30, 30, 30, 255))
        d = ImageDraw.Draw(S)
        for k, (im, dy) in enumerate(((ts_idle(t), 52), (Image.open(f'{OUT}/idle-iso/t{t:02d}.png'), 52),
                                      (Image.open(f'{OUT}/idle-ra/t{t:02d}.png'), 0))):
            b = Image.new('RGBA', im.size, BG); b.alpha_composite(im.convert('RGBA'))
            S.paste(b, (k * 396, 34 + dy))
        d.text((6, 4), 'TS original (x3)', fill=(255, 255, 0, 255))
        d.text((402, 4), 'HD, TS angle', fill=(255, 255, 0, 255))
        d.text((798, 4), 'HD, RA grid', fill=(255, 255, 0, 255))
        d.text((6, 18), f'idle  frame {t:02d}: fans (A) + roof lamps (C) + door lamp & running light (B)', fill=(255, 255, 255, 255))
        frames.append(S.convert('RGB').quantize(colors=255, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=100, loop=0, optimize=True)


if __name__ == '__main__':
    if sys.argv[1] == 'idle':
        render_idle(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 4)
    elif sys.argv[1] == 'prod':
        render_prod(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 4)
    elif sys.argv[1] == 'gif-prod':
        gif_prod(sys.argv[2] if len(sys.argv) > 2 else '/home/claude/work/out/checkpoint/yard-producing-vs-ts.gif')
    elif sys.argv[1] == 'gif-idle':
        gif_idle(sys.argv[2] if len(sys.argv) > 2 else '/home/claude/work/out/checkpoint/yard-idle-vs-ts.gif')
