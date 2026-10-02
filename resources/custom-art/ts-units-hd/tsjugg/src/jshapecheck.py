"""the Juggernaut's shape check: TS's colour classes beside the model's in TS's own camera (walker, cabin, base),
and the HD renders beside the mod's frames.

    python3 jshapecheck.py OUTDIR [HD_DIR]
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
import jugg as JG
import jfit as JF
import jfitcabin as JC
import jbase as JB
import jrender as JR

OUT = sys.argv[1]
HD = sys.argv[2] if len(sys.argv) > 2 else 'out_sc'
os.makedirs(OUT, exist_ok=True)
INMOD = HANDOFF + '/04-TSJUGG/in-mod/tsjugg/frames/tsjugg-%04d.png'
BG = (92, 104, 72, 255)

# 1. the walker at step 0: TS's classes and the model's (with the details and TS's three barrel housings)
m = JR.load('fit_walk_e.json')
P = m['P']; pose = JR.walk_pose(m, 0)
V = JF.Views([cw * 15 for cw in range(8)])
parts = JG.body_parts(P, pose) + JG.details(P, pose[6])
iou = V.iou(parts, m['ax'], m['y0'])
JF.compare(V, parts, m['ax'], m['y0'], OUT + '/walker-classes.png', label='walk')
print('walker IoU per facing', np.round(iou, 3), 'mean %.3f' % iou.mean())

# 2. the cabin (DJUGG_A), 8 of its 32 facings
jc = json.load(open('fit_hatch_a.json'))
PC = dict(JG.P0); PC.update(jc['P'])
CV = JC.CabinViews(range(0, 32, 4))
cparts = JC.cabin_parts(PC) + JG.details(PC)
ciou = CV.iou(cparts, jc['cax'], jc['cy0'])
JF.compare(CV, cparts, jc['cax'], jc['cy0'], OUT + '/cabin-classes.png', label='cabin')
print('cabin IoU', np.round(ciou, 3), 'mean %.3f' % ciou.mean())

# 3. the base (DJUGG frame 0)
import jbase2 as JB2
from paths import HANDOFF
jb = json.load(open('fit_base2_a.json'))
PB = dict(JB2.P0); PB.update(jb['P'])
BV = JB.BaseView()
bparts = JB2.base_parts(PB, jb['bax'], jb['by0'])
biou = BV.iou(bparts, jb['bax'], jb['by0'])
JF.compare(BV, bparts, jb['bax'], jb['by0'], OUT + '/base-classes.png', label='base', z=10)
print('base IoU', np.round(biou, 3))


# 4. HD beside the mod's frames
def pair_sheet(frames, name, crop=(40, 0, 420, 400), scale=0.75, cols=4, labels=None):
    tiles = []
    for i, k in enumerate(frames):
        row = []
        for j, (lab, p) in enumerate((('in-mod', INMOD % k), ('HD', '%s/tsjugg-%04d.png' % (HD, k)))):
            im = Image.open(p).convert('RGBA').crop(crop)
            b = Image.new('RGBA', im.size, BG); b.alpha_composite(im)
            b = b.resize((round(b.size[0] * scale), round(b.size[1] * scale)), Image.LANCZOS).convert('RGB')
            t = Image.new('RGB', (b.size[0], b.size[1] + 16), (28, 30, 34)); t.paste(b, (0, 16))
            ImageDraw.Draw(t).text((4, 2), '%s %d%s' % (lab, k, (' ' + labels[i]) if labels else ''), fill=(230, 220, 160))
            row.append(t)
        w, h = row[0].size
        pair = Image.new('RGB', (2 * w + 4, h), (20, 22, 26))
        pair.paste(row[0], (0, 0)); pair.paste(row[1], (w + 4, 0))
        tiles.append(pair)
    W, H = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    out = Image.new('RGB', (cols * (W + 8) + 8, rows * (H + 8) + 8), (20, 22, 26))
    for i, t in enumerate(tiles):
        out.paste(t, (8 + (i % cols) * (W + 8), 8 + (i // cols) * (H + 8)))
    out.save(OUT + '/' + name)


DIRS = ['N', 'NW', 'W', 'SW', 'S', 'SE', 'E', 'NE']
if os.path.exists('%s/tsjugg-%04d.png' % (HD, 105)):
    pair_sheet([f * 15 for f in range(8)], 'walker-hd.png', crop=(40, 60, 420, 390), labels=DIRS)
if os.path.exists('%s/tsjugg-%04d.png' % (HD, 148)):
    pair_sheet([120 + 4 * f for f in range(8)], 'deployed-rest-hd.png', crop=(20, 30, 428, 390), labels=DIRS)
if os.path.exists('%s/tsjugg-%04d.png' % (HD, 180)):
    pair_sheet([152 + 4 * f for f in range(8)], 'deployed-aim-hd.png', crop=(20, 0, 428, 390), labels=DIRS)
print('done')
