"""Extra previews for the Tiberium Refinery package (bdeliver extra_previews): the docking and unloading played out
from the package's own frames, the harvester's frames, the fire and the lid against TS's."""
import os
import numpy as np
from PIL import Image, ImageDraw
import ypreview as P

HARV_MOD = '/home/claude/work/ts/harv/harvester-and-docking/ts-harvester-in-mod/frames'
DARK = (30, 30, 30, 255)
UNIT_AT = (250, 340)            # the docked harvester's 384x384 sprite on the refinery canvas (RA grid; procfinal.unit_at)
SIN32 = float(np.sin(np.deg2rad(32.0)))
FIRE = (246, 112, 18.)


def _img(pk, view, sub, name):
    return pk.fr(view, sub, name)


def harv_frame(pk, k):
    return Image.open(f"{pk.s['pkg']}/harvester/harvester-{k:02d}.png").convert('RGBA')


def ra_timeline():
    """one docking, start to finish: (unit, docked frame, lid frame, fire frame, what is happening).
    unit = (sprite frame 0..63, ground offset east, ground offset south) from the dock, 'dock', or None (gone)."""
    seq = []
    for i in range(10):                                   # drives in from the east, facing west (as in your video)
        seq.append(((8, 400.0 * (1 - (i + 1) / 10.0), 0.0), None, None, None, 'arrives, facing west'))
    for f in range(9, 25):                                # turns round on the spot, through south, to face east
        seq.append(((f, 0.0, 0.0), None, None, None, 'turns round to face east (TS: DIR_E)'))
    for _ in range(3):                                    # docked, loaded
        seq.append(('dock', 0, None, None, 'docked, loaded (HARV)'))
    fire = 0
    for k in range(5):                                    # unloading starts: HORV, the tank slides in (NTREFN_A)
        seq.append(('dock', 1, k, fire, f'unloading: HORV, the tank slides in (lid {k:02d})')); fire += 1
    for _ in range(16):                                   # unloading
        seq.append(('dock', 1, None, fire if fire < 20 else None, 'unloading')); fire += 1
    for k in (4, 3, 2, 1, 0):                             # done: the tank slides back out (NTREFN_AR)
        seq.append(('dock', 1, k, None, f'done: the tank slides back out (lid {k:02d})'))
    for _ in range(3):
        seq.append(('dock', 0, None, None, 'HARV again'))
    for i in range(10):                                   # drives off east
        seq.append(((24, 44.0 * (i + 1), 0.0), None, None, None, 'leaves'))
    for _ in range(3):
        seq.append((None, None, None, None, ''))
    return seq


def docking_ra(pk, out):
    """RA grid: left, the refinery draws the docked harvester (D-docked + A-lid; the unit hidden while docked, as the
    mod's TD refinery does); right, the unit stays visible (the HORV unit + A-lid-unit, the mod's way now)."""
    v = 'ra'
    base = pk.base(v, 0)
    box = (196, 300, 736, 800)
    frames = []
    seq = ra_timeline()
    for n, (unit, dock, lid, fire, what) in enumerate(seq):
        t = n % 16
        panels = []
        for mode in ('scene', 'unit'):
            im = base.copy()
            im.alpha_composite(_img(pk, v, 'C-lamps', f'refinery-lamps-{t:02d}'))
            if fire is not None:
                im.alpha_composite(_img(pk, v, 'B-fire', f'refinery-fire-{fire:02d}'))
            if unit == 'dock':
                if mode == 'scene':
                    im.alpha_composite(_img(pk, v, 'D-docked', f'refinery-docked-{dock:02d}'))
                    if lid is not None:
                        im.alpha_composite(_img(pk, v, 'A-lid', f'refinery-lid-{lid:02d}'))
                else:
                    P.paste(im, harv_frame(pk, 24 + 32 * dock), *UNIT_AT)
                    if lid is not None:
                        im.alpha_composite(_img(pk, v, 'A-lid-unit', f'refinery-lid-unit-{lid:02d}'))
            elif unit is not None:
                f, ex, sy = unit
                P.paste(im, harv_frame(pk, f), UNIT_AT[0] + int(round(ex)), UNIT_AT[1] + int(round(sy * SIN32)))
            panels.append(P.on_bg(im.crop(box)))
        W, H = panels[0].size
        S = Image.new('RGBA', (2 * W + 12, H + 44), DARK)
        S.paste(panels[0], (0, 44)); S.paste(panels[1], (W + 12, 44))
        d = ImageDraw.Draw(S)
        d.text((6, 4), 'A: the refinery draws the docked harvester', fill=(255, 255, 0, 255))
        d.text((6, 18), '(unit hidden while docked: D-docked + A-lid)', fill=(255, 255, 255, 255))
        d.text((W + 18, 4), 'B: the unit kept visible over the building', fill=(255, 255, 0, 255))
        d.text((W + 18, 18), '(HARV/HORV unit + A-lid-unit over it)', fill=(255, 255, 255, 255))
        d.text((6, 30), f'RA grid  {n:02d}  {what}', fill=(200, 200, 200, 255))
        frames.append(S)
    pk.gif(frames, f'{out}/docking-ra-grid.gif', 90)
    # key frames as a still: turning, docked, the tank sliding in, unloading
    picks = [20, 26, 29, 31, 33, 34]
    pk.stack([frames[i] for i in picks[:3]], 6).save(f'{out}/docking-ra-grid-keyframes-1.png')
    pk.stack([frames[i] for i in picks[3:]], 6).save(f'{out}/docking-ra-grid-keyframes-2.png')


def docking_iso(pk, out):
    """TS angle: the refinery draws the docked harvester (TS's own, in TS's camera at TS's size: the mod's harvester
    is drawn in RA's camera and can't line up with a TS-angle building), the lid, the fire."""
    v = 'iso'
    base = pk.base(v, 0)
    box = (150, 40, 700, 640)
    seq = [(0, None, None)] * 4 + [(1, k, k) for k in range(5)] + [(1, None, 5 + i) for i in range(15)] + \
          [(1, k, None) for k in (4, 3, 2, 1, 0)] + [(0, None, None)] * 4
    frames = []
    for n, (dock, lid, fire) in enumerate(seq):
        im = base.copy()
        im.alpha_composite(_img(pk, v, 'C-lamps', f'refinery-lamps-{n % 16:02d}'))
        if fire is not None:
            im.alpha_composite(_img(pk, v, 'B-fire', f'refinery-fire-{fire:02d}'))
        im.alpha_composite(_img(pk, v, 'D-docked', f'refinery-docked-{dock:02d}'))
        if lid is not None:
            im.alpha_composite(_img(pk, v, 'A-lid', f'refinery-lid-{lid:02d}'))
        c = P.on_bg(im.crop(box))
        S = Image.new('RGBA', (c.width, c.height + 32), DARK)
        S.paste(c, (0, 32))
        d = ImageDraw.Draw(S)
        d.text((6, 4), 'TS angle: D-docked (TS\'s harvester, TS\'s size) + A-lid + B-fire + C-lamps', fill=(255, 255, 0, 255))
        d.text((6, 18), f'{n:02d}  ' + ('docked, loaded' if dock == 0 else 'unloading'), fill=(200, 200, 200, 255))
        frames.append(S)
    pk.gif(frames, f'{out}/docking-ts-angle.gif', 90)


def harvester_sheet(pk, out):
    """the 64 frames, labelled like the mod's sheet; and the mod's TSHARV next to ours for eight facings."""
    names = ['N', 'NNW', 'NW', 'WNW', 'W', 'WSW', 'SW', 'SSW', 'S', 'SSE', 'SE', 'ESE', 'E', 'ENE', 'NE', 'NNE']
    cell = 192
    S = Image.new('RGBA', (8 * cell, 8 * (cell + 14)), DARK)
    d = ImageDraw.Draw(S)
    for k in range(64):
        im = P.on_bg(harv_frame(pk, k)).resize((cell, cell), Image.LANCZOS)
        x, y = (k % 8) * cell, (k // 8) * (cell + 14)
        S.paste(im, (x, y + 14))
        f = k % 32
        lab = f"{k:02d} {'HORV' if k >= 32 else 'HARV'} {names[f // 2] if f % 2 == 0 else ''}"
        d.text((x + 3, y + 1), lab, fill=(255, 255, 0, 255))
    S.save(f'{out}/harvester-sheet.png')
    # vs the mod's
    picks = [0, 4, 8, 12, 16, 20, 24, 28]
    rows = []
    for half in (0, 32):
        R = Image.new('RGBA', (8 * cell, 2 * (cell + 14)), DARK)
        dr = ImageDraw.Draw(R)
        for i, f in enumerate(picks):
            k = f + half
            mod = Image.open(f'{HARV_MOD}/tsharv-{k:02d}.png').convert('RGBA') if os.path.exists(f'{HARV_MOD}/tsharv-{k:02d}.png') else None
            for j, im in enumerate((mod, harv_frame(pk, k))):
                if im is None:
                    continue
                t = P.on_bg(im).resize((cell, cell), Image.NEAREST if j == 0 else Image.LANCZOS)
                R.paste(t, (i * cell, j * (cell + 14) + 14))
                dr.text((i * cell + 3, j * (cell + 14) + 1), f"{'mod now' if j == 0 else 'HD'} {k:02d}", fill=(255, 255, 0, 255))
        rows.append(R)
    pk.stack(rows, 6).save(f'{out}/harvester-vs-mod.png')


def ts_fire(pk, k):
    """TS's NTREFN_B frame k recoloured as the game draws it (its own shape and brightness on a fire ramp: the
    frames decode with the unit palette, the game draws them with the fire palette)."""
    T = f"{pk.s['hand']}/ts-original/NTREFN_B/frames/{k:02d}.png"
    a = np.asarray(Image.open(T).convert('RGBA')).astype(np.float32)
    al = a[..., 3] > 0
    lum = (a[..., 0] * 0.5 + a[..., 1] * 0.35 + a[..., 2] * 0.15) / 255.0
    lo, hi = (lum[al].min(), lum[al].max()) if al.any() else (0, 1)
    t = np.clip((lum - lo) / max(hi - lo, 1e-3), 0, 1)
    red, orange, yellow = np.array([150, 28, 4.]), np.array(FIRE), np.array([255, 226, 118.])
    col = np.where((t < 0.5)[..., None], red + (orange - red) * (t / 0.5)[..., None],
                   orange + (yellow - orange) * ((t - 0.5) / 0.5)[..., None])
    out = np.zeros(a.shape, np.uint8)
    out[..., :3] = np.clip(col, 0, 255).astype(np.uint8)
    out[..., 3] = np.where(al, 255, 0)
    return Image.fromarray(out, 'RGBA')


def fire_vs_ts(pk, out):
    """NTREFN_B: TS's 20 lit frames (recoloured to fire, as drawn in game) next to ours, both views, on the building."""
    T = f"{pk.s['hand']}/ts-original"
    frames = []
    boxes = {'ts': (120, 0, 440, 300), 'iso': (120, 0, 440, 300), 'ra': (40, 180, 300, 420)}
    for k in range(20):
        ts = Image.open(f'{T}/NTREFNBB/frames/00.png').convert('RGBA')
        ts.alpha_composite(Image.open(f'{T}/NTREFN/frames/00.png').convert('RGBA'))
        ts.alpha_composite(ts_fire(pk, k))
        tsc = pk.ts_canvas_img(ts)
        iso = pk.base('iso', 0); iso.alpha_composite(_img(pk, 'iso', 'B-fire', f'refinery-fire-{k:02d}'))
        ra = pk.base('ra', 0); ra.alpha_composite(_img(pk, 'ra', 'B-fire', f'refinery-fire-{k:02d}'))
        tiles = [P.on_bg(tsc.crop(boxes['ts'])), P.on_bg(iso.crop(boxes['iso'])), P.on_bg(ra.crop(boxes['ra']))]
        W = sum(t.width for t in tiles) + 24
        H = max(t.height for t in tiles) + 34
        S = Image.new('RGBA', (W, H), DARK)
        d = ImageDraw.Draw(S)
        x = 0
        for t, lab in zip(tiles, ('TS NTREFN_B (x4.1, fire colours)', 'HD, TS angle', 'HD, RA grid')):
            S.paste(t, (x, 34)); d.text((x + 4, 4), lab, fill=(255, 255, 0, 255)); x += t.width + 12
        d.text((4, 18), f'B-fire {k:02d}/19 (20-39 are empty, as TS\'s)', fill=(255, 255, 255, 255))
        frames.append(S)
    pk.gif(frames, f'{out}/fire-vs-original.gif', 90)


def lid_vs_ts(pk, out):
    """NTREFN_A frames 0-4 (TS's tank sliding in) over NTREFN, next to ours over the building with the docked HORV."""
    T = f"{pk.s['hand']}/ts-original"
    box = (300, 300, 620, 560)
    rows = []
    for k in range(5):
        ts = Image.open(f'{T}/NTREFNBB/frames/00.png').convert('RGBA')
        ts.alpha_composite(Image.open(f'{T}/NTREFN/frames/00.png').convert('RGBA'))
        ts.alpha_composite(Image.open(f'{T}/NTREFN_A/frames/{k:02d}.png').convert('RGBA'))
        tsc = pk.ts_canvas_img(ts)
        iso = pk.base('iso', 0)
        iso.alpha_composite(_img(pk, 'iso', 'D-docked', 'refinery-docked-01'))
        iso.alpha_composite(_img(pk, 'iso', 'A-lid', f'refinery-lid-{k:02d}'))
        rows.append((P.on_bg(tsc.crop(box)), P.on_bg(iso.crop(box))))
    W, H = rows[0][0].size
    S = Image.new('RGBA', (5 * (W + 8), 2 * (H + 16)), DARK)
    d = ImageDraw.Draw(S)
    for k, (a, b) in enumerate(rows):
        S.paste(a, (k * (W + 8), 16)); S.paste(b, (k * (W + 8), H + 32))
        d.text((k * (W + 8) + 4, 2), f'TS NTREFN_A {k:02d} (tank only, no truck)', fill=(255, 255, 0, 255))
        d.text((k * (W + 8) + 4, H + 18), f'HD A-lid {k:02d} over D-docked 01', fill=(255, 255, 0, 255))
    S.save(f'{out}/lid-vs-original.png')


VIDEO = '/home/claude/work/ts/harv/video/f/%04d.png'      # Luke's docking video, frame by frame
VIDEO_REG = (2.0, -64.0, -70.0)                            # video px = TS px x 2.0 + (-64, -70)


def video_on_canvas(pk, i):
    """frame i of the docking video on the TS-angle canvas (TS px x K + O), nearest neighbour."""
    v = np.asarray(Image.open(VIDEO % i).convert('RGBA'))
    W, H = pk.s['iso_size']
    K, (ox, oy) = pk.s['K'], pk.s['O']
    sc, vx0, vy0 = VIDEO_REG
    yy, xx = np.mgrid[0:H, 0:W]
    vx = np.floor((xx + 0.5 - ox) / K * sc + vx0).astype(int)
    vy = np.floor((yy + 0.5 - oy) / K * sc + vy0).astype(int)
    ok = (vx >= 0) & (vx < v.shape[1]) & (vy >= 0) & (vy < v.shape[0])
    out = np.zeros((H, W, 4), np.uint8)
    out[ok] = v[vy[ok], vx[ok]]
    return Image.fromarray(out)


def docked_vs_video(pk, out):
    """the TS-angle docked harvester next to TS's own in your video (frame 83: HARV docked; 120: HORV unloading)."""
    if not os.path.exists(VIDEO % 120):
        return
    box = (250, 330, 640, 590)
    tiles = []
    for i, dock, lab in ((83, 0, 'HARV docked'), (120, 1, 'HORV, unloading')):
        hd_ = pk.base('iso', 0)
        hd_.alpha_composite(_img(pk, 'iso', 'D-docked', f'refinery-docked-{dock:02d}'))
        tiles.append((f'TS, your video frame {i}: {lab} (x2.05)', P.on_bg(video_on_canvas(pk, i).crop(box))))
        tiles.append((f'HD, TS angle: D-docked {dock:02d} over the building', P.on_bg(hd_.crop(box))))
    W, H = tiles[0][1].size
    S = Image.new('RGBA', (2 * W + 8, 2 * (H + 16)), DARK)
    d = ImageDraw.Draw(S)
    for k, (lab, im) in enumerate(tiles):
        x, y = (k % 2) * (W + 8), (k // 2) * (H + 16)
        S.paste(im, (x, y + 16)); d.text((x + 4, y + 2), lab, fill=(255, 255, 0, 255))
    S.save(f'{out}/docked-ts-angle-vs-video.png')





def idle_with_fire(pk, out, level=0, n=48, burst=6, z=0.62):
    """the idle loop as it plays: the dock lamps (C) looping, the flare stack bursting once (B), TS's original (its
    fire recoloured as the game draws it) next to both HD views."""
    s = pk.s
    T = f"{s['hand']}/ts-original"
    frames = []
    for i in range(n):
        t = i % 16
        k = i - burst if 0 <= i - burst < 20 else None
        ts = Image.open(f'{T}/NTREFNBB/frames/{level:02d}.png').convert('RGBA')
        ts.alpha_composite(Image.open(f'{T}/NTREFN/frames/{level:02d}.png').convert('RGBA'))
        c = Image.open(f'{T}/NTREFN_C/frames/{t:02d}.png').convert('RGBA')
        pad = Image.new('RGBA', ts.size, (0, 0, 0, 0)); pad.paste(c, ((ts.width - c.width) // 2, (ts.height - c.height) // 2))
        ts.alpha_composite(pad)
        if k is not None:
            ts.alpha_composite(ts_fire(pk, k))
        views = []
        for v in ('iso', 'ra'):
            im = pk.base(v, level)
            im.alpha_composite(_img(pk, v, 'C-lamps', f'refinery-lamps-{t + 16 * level:02d}'))
            if k is not None:
                im.alpha_composite(_img(pk, v, 'B-fire', f'refinery-fire-{k:02d}'))
            views.append(im)
        sub = f"{('healthy', 'damaged')[level]} idle {i:02d}/{n - 1}: the dock lamps (C, 16-frame loop) and the flare stack's burst (B, 20 frames)"
        frames.append(pk.three_up([pk.crop('iso', pk.ts_canvas_img(ts)), pk.crop('iso', views[0]), pk.crop('ra', views[1])],
                                  pk.T3(), sub, z=z))
    pk.gif(frames, f"{out}/idle-{('healthy', 'damaged')[level]}-with-fire.gif", 90)
    return frames


def idle_fire_both(pk, out):
    for lv in (0, 1):
        idle_with_fire(pk, out, lv)


EXTRAS = [docking_ra, docking_iso, harvester_sheet, fire_vs_ts, lid_vs_ts, docked_vs_video, idle_fire_both]
