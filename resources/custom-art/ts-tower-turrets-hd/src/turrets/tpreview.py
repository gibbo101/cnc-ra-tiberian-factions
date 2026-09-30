"""Previews for the turrets: every facing on the tower (like in-mod's sheets), healthy and damaged, HD beside
in-mod, a spin GIF, and the aim points marked.

    python3 tpreview.py <vulcan|rpg|sam>
"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw

BG = (90, 100, 80, 255)
TOWER = {0: '../ctwr/out/component-tower-00.png', 1: '../ctwr/out/component-tower-01.png'}


def on_tower(turret_png, level=0):
    c = Image.new('RGBA', (176, 320), BG)
    c.alpha_composite(Image.open(TOWER[level]).convert('RGBA'))
    c.alpha_composite(Image.open(turret_png).convert('RGBA'))
    return c


def sheet(name, tag='', level=0, root='out'):
    """all 32 facings on the tower, 8 x 4, cropped like in-mod's sheets (176 x 200 each)."""
    S = Image.new('RGBA', (8 * 176, 4 * 200), BG)
    d = ImageDraw.Draw(S)
    for f in range(32):
        t = on_tower(f'{root}/{name}/turret{tag}-{f:02d}.png', level).crop((0, 10, 176, 210))
        S.paste(t, ((f % 8) * 176, (f // 8) * 200))
        d.text(((f % 8) * 176 + 4, (f // 8) * 200 + 4), str(f), fill=(255, 255, 0, 255))
    return S


def versus(name, frames=(0, 4, 8, 12, 16, 20, 24, 28), root='out'):
    """in-mod beside HD at x2."""
    tiles = []
    for f in frames:
        a = on_tower(f'ts-tower-turrets-handoff/in-mod/{name}/turret-{f:02d}.png').crop((8, 20, 168, 180)).resize((320, 320), Image.LANCZOS)
        b = on_tower(f'{root}/{name}/turret-{f:02d}.png').crop((8, 20, 168, 180)).resize((320, 320), Image.LANCZOS)
        t = Image.new('RGBA', (650, 330), (40, 40, 40, 255)); t.paste(a, (0, 0)); t.paste(b, (330, 0))
        ImageDraw.Draw(t).text((4, 4), f'{f}: in-mod | HD', fill=(255, 255, 0, 255))
        tiles.append(t)
    S = Image.new('RGBA', (2 * 660, ((len(tiles) + 1) // 2) * 340), (40, 40, 40, 255))
    for i, t in enumerate(tiles):
        S.paste(t, ((i % 2) * 660, (i // 2) * 340))
    return S


def spin_gif(name, path, tag='', level=0, root='out'):
    frames = []
    for f in list(range(32)):
        t = on_tower(f'{root}/{name}/turret{tag}-{f:02d}.png', level).crop((8, 20, 168, 200)).resize((320, 360), Image.LANCZOS)
        frames.append(t.convert('RGB'))
    pal = frames[5].quantize(colors=255, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [fr.quantize(palette=pal, dither=Image.NONE) for fr in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=90, loop=0)


def aims(name, state='healthy', root='out', frames=range(0, 32, 2)):
    """the aim points marked on the frames (x3)."""
    pts = json.load(open(f'{root}/{name}/aim-{state}.json'))
    tag = '' if state == 'healthy' else '-' + state
    tiles = []
    for f in frames:
        t = on_tower(f'{root}/{name}/turret{tag}-{f:02d}.png', 1 if 'damaged' in state else 0)
        t = t.crop((8, 20, 168, 150)).resize((480, 390), Image.LANCZOS)
        d = ImageDraw.Draw(t)
        for k, (x, y) in enumerate(pts[str(f)]):
            X, Y = (x - 8) * 3, (y - 20) * 3
            col = (255, 40, 40, 255) if k == 0 or name != 'sam' else (255, 200, 0, 255)
            d.ellipse((X - 4, Y - 4, X + 4, Y + 4), outline=col, width=2)
        d.text((4, 4), str(f), fill=(255, 255, 0, 255))
        tiles.append(t)
    S = Image.new('RGBA', (4 * 486, ((len(tiles) + 3) // 4) * 396), (40, 40, 40, 255))
    for i, t in enumerate(tiles):
        S.paste(t, ((i % 4) * 486, (i // 4) * 396))
    return S


if __name__ == '__main__':
    name = sys.argv[1]
    os.makedirs('previews', exist_ok=True)
    sheet(name).save(f'previews/{name}-on-tower-sheet.png')
    if os.path.exists(f'out/{name}/turret-damaged-00.png'):
        sheet(name, '-damaged', 1).save(f'previews/{name}-damaged-on-tower-sheet.png')
    if os.path.exists(f'out/{name}/turret-recoil-00.png'):
        sheet(name, '-recoil').save(f'previews/{name}-recoil-on-tower-sheet.png')
    versus(name).save(f'previews/{name}-vs-in-mod.png')
    spin_gif(name, f'previews/{name}-spin.gif')
    aims(name).save(f'previews/{name}-aim-points.png')
    print('previews', name)
