"""sonlook.py - the Disruptor assembled (hull k and turret 32 + k, the turret seated aft: seat()) side by side: the mod's
frames (TS's voxels as the mod draws them), v1 and a folder of new frames, cropped and zoomed.
    python3 sonlook.py out.png newdir facings [zoom] [label]"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from paths import HANDOFF

INMOD = HANDOFF + '/08-TSSONIC/in-mod/tssonic/frames/tssonic-%04d.png'
V1 = os.environ.get('V1_FRAMES', 'v1/frames') + '/tssonic-%04d.png'
BG = (110, 106, 84, 255)
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)


SEAT_V5, SEAT_V4, SEAT_V3, SEAT_TS = 82.68, 83.4, 88.1, 48.0


def seat(f, px=SEAT_V5):
    """where the game draws the turret frame against the hull's: v4's on the green rear deck, its ring's back at the
    deck's back (Luke), 13.3 voxels (83 canvas px) aft of the unit's position along the hull's facing, on the ground
    (foreshortened as the camera draws the ground: 83 px aft when the hull faces east or west, 44 px when it faces north
    or south).  v3's ring on the hull's back: 88 px.  TS's own TurretOffset=-64 is a quarter cell (48 canvas px)."""
    th = 2 * np.pi * ((32 - f) % 32) / 32
    v = np.array([np.sin(th), -np.cos(th) * np.sin(np.deg2rad(32.0))])
    return -px * v[0], -px * v[1]


def assembled(pat, f, turret=True, px=SEAT_V5):
    b = Image.new('RGBA', (448, 448), BG)
    b.alpha_composite(Image.open(pat % f).convert('RGBA'))
    if turret:
        t = Image.open(pat % (32 + f)).convert('RGBA')
        dx, dy = seat(f, px)
        sh = Image.new('RGBA', t.size, (0, 0, 0, 0)); sh.paste(t, (int(round(dx)), int(round(dy))))
        b.alpha_composite(sh)
    return b


def one(pat, f, crop, z, turret=True, px=SEAT_V5):
    c = assembled(pat, f, turret, px).crop(crop)
    return c.resize((int(c.width * z), int(c.height * z)), Image.LANCZOS).convert('RGB')


def sheet(out, newpat, fs, z=1.5, label='v2', crop=(60, 60, 390, 320), prev=('v1', V1, SEAT_V5), turret=True,
          ts=('TS (the mod now)', INMOD, SEAT_V5)):
    """columns (name, frames, the turret's seat in canvas px): TS's (the mod's frames), an earlier version, the new."""
    cols = [ts, prev, (label, newpat, SEAT_V5)]
    tiles = [[one(p, f, crop, z, turret, px) for _, p, px in cols] for f in fs]
    W, H = tiles[0][0].size
    S = Image.new('RGB', (3 * (W + 6) - 6, len(fs) * (H + 6) + 24), (30, 30, 30))
    d = ImageDraw.Draw(S)
    for j, (name, _, _) in enumerate(cols):
        d.text((j * (W + 6) + 6, 4), name, font=FONT, fill=(240, 230, 180))
    for i, row in enumerate(tiles):
        for j, t in enumerate(row):
            S.paste(t, (j * (W + 6), 24 + i * (H + 6)))
        d.text((6, 24 + i * (H + 6) + 4), 'facing %d' % fs[i], font=FONT, fill=(240, 230, 180))
    S.save(out)


if __name__ == '__main__':
    out, newdir = sys.argv[1], sys.argv[2]
    fs = [int(a) for a in sys.argv[3].split(',')]
    z = float(sys.argv[4]) if len(sys.argv) > 4 else 1.5
    label = sys.argv[5] if len(sys.argv) > 5 else 'v2'
    sheet(out, newdir + '/tssonic-%04d.png', fs, z, label)
