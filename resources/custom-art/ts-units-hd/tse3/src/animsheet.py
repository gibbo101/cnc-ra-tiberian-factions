"""
animsheet.py - an animation sheet: every sequence of a unit (the 8-facing ones facing west), TS's frame as the mod has it
over the HD frame, one sequence a row, frame by frame (Luke: "show me an up to date animation sheet").

    python3 animsheet.py UNIT PKG out.png [title]
"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import infunit, tsshadow as T, infseq as SQ

unit, pkg, out = sys.argv[1], sys.argv[2], sys.argv[3]
title = sys.argv[4] if len(sys.argv) > 4 else None
infunit.use(unit)
u = infunit.UNITS[unit]
title = title or u.get('title', unit)
stem = 'ts' + u['name'].lower()
BG = np.array([96, 100, 72], float)
box = (56, 26, 212, 150)
Z = 1.0
W, H = int((box[2] - box[0]) * Z), int((box[3] - box[1]) * Z)
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 16)
    small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
except Exception:
    font = small = ImageFont.load_default()


def on_bg(a):
    al = a[..., 3:4] / 255.0
    return Image.fromarray(np.clip(a[..., :3] * al + BG * (1 - al), 0, 255).astype(np.uint8))


def seq_frames(name, facing=2):
    first, n, fc = SQ.SEQ[unit][name]
    if fc == 8:
        return [first + facing * n + s for s in range(n)]
    return list(range(first, first + n))


seqs = [('Run, west', 'walk'), ('Fire, west', 'fire'), ('Crawl, west', 'crawl'), ('Fire prone, west', 'prone_fire'),
        ('Lie down + get up, west', None), ('Idle 1', 'idle1'), ('Idle 2', 'idle2'), ('Death 1', 'death1'),
        ('Death 2', 'death2')]
if unit == 'e2':
    seqs[1] = ('Throw, west', 'fire'); seqs[3] = ('Throw prone, west', 'prone_fire')
if unit in ('medic', 'eng', 'chamspy', 'mhijack'):
    seqs = [s for s in seqs if s[1] not in ('fire', 'prone_fire')]
if unit in ('cyborg', 'cyc2'):
    # (the Cyborg's lying down and getting up are empty, as TS's; the Cyborg Commando has none)
    seqs = [s for s in seqs if s[1] is not None]
if unit == 'medic':
    seqs.append(('Heal', 'heal'))
if unit == 'jj':
    seqs = [s for s in seqs if s[1] not in ('death1', 'death2')]
    seqs += [('Fly, west', 'fly'), ('Hover, west', 'hover'), ('Fire flying, west', 'fire_fly'), ('Tumble', 'tumble')]
rows = []
for label, name in seqs:
    if name is None:
        ks = seq_frames('lie_down') + seq_frames('get_up')
    else:
        ks = seq_frames(name)
    rows.append((label, ks))
ncol = max(len(ks) for l, ks in rows)
LW = 0
RH = 2 * H + 22
sheet = Image.new('RGB', (ncol * (W + 2) + 4, 40 + len(rows) * (RH + 8)), (28, 28, 30))
d = ImageDraw.Draw(sheet)
d.text((8, 10), title + '  -  each row: TS (%s) above, HD below, frame by frame' % infunit.mod_label(infunit.CURRENT[0], True), fill=(255, 230, 120), font=font)
y = 40
for label, ks in rows:
    d.text((8, y + 2), label, fill=(255, 255, 255), font=font)
    for i, k in enumerate(ks):
        a = T.inmod_frame(unit, k)
        p = os.path.join(pkg, 'frames', '%s-%04d.png' % (stem, k))
        b = np.asarray(Image.open(p).convert('RGBA')).astype(float)
        x = 4 + i * (W + 2)
        sheet.paste(on_bg(a).crop(box), (x, y + 22))
        sheet.paste(on_bg(b).crop(box), (x, y + 22 + H))
        d.text((x + 3, y + 24), str(k), fill=(255, 255, 0), font=small)
    y += RH + 8
sheet.save(out, optimize=True)
print(out, sheet.size)
