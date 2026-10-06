"""mtab.py - the Mobile EMP Cannon's tab on the units review page, from its package: a TS | previous | vN sheet, then
the tab (in its old place) with the package's previews.  Prints the files map for the publish.

    python3 mtab.py PKG version shape final
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.environ.get('REVIEW', 'units-review'))
import addtab
from paths import HANDOFF
from mempcam import LOW_PX

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
OLD = ['gif/memp-turn-v2.gif', 'img/memp-closeups-v2.png', 'img/memp-v1-v2.png', 'img/memp-8-facings-v2.png',
       'img/memp-shape-v2.png', 'gif/memp-blast-v2.gif', 'img/memp-scale-v2.png']
INMOD = HANDOFF + '/13-TSMEMP/in-mod/tsmemp/frames/tsmemp-%04d.png'
PREV = ('v2', os.environ.get('PREV_PKG', 'v2') + '/frames/tsmemp-%04d.png')


def three(pkg, out, ver, fs=(4, 12, 20, 28), z=1.3):
    """TS (the mod's frames, moved onto the ground) | the previous version | vN, facing by facing."""
    crop = (60, 70, 324, 300)
    rows = []
    for f in fs:
        row = []
        for name, pat, dy in (("TS (the mod's frames, on the ground)", INMOD, int(round(LOW_PX))), (PREV[0], PREV[1], 0),
                              (ver, pkg + '/frames/tsmemp-%04d.png', 0)):
            im = Image.open(pat % f).convert('RGBA')
            b = Image.new('RGBA', im.size, (96, 100, 72, 255)); sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
            sh.paste(im, (0, dy)); b.alpha_composite(sh)
            c = b.crop(crop).convert('RGB')
            c = c.resize((int(c.width * z), int(c.height * z)), Image.LANCZOS)
            ImageDraw.Draw(c).text((4, 2), '%s  facing %d' % (name, f), font=FONT, fill=(250, 240, 170))
            row.append(c)
        rows.append(row)
    W, H = rows[0][0].size
    S = Image.new('RGB', (3 * (W + 4) - 4, len(rows) * (H + 4) - 4), (24, 24, 24))
    for i, row in enumerate(rows):
        for j, t in enumerate(row):
            S.paste(t, (j * (W + 4), i * (H + 4)))
    S.save(out)


if __name__ == '__main__':
    pkg, ver, shape, final = sys.argv[1:5]
    tmp = os.path.join(HERE, 'logs')
    os.makedirs(tmp, exist_ok=True)
    pv = pkg + '/previews'
    three(pkg, tmp + '/ts-prev-new.png', ver)
    note = open(os.path.join(HERE, 'tab_note.txt')).read().strip()
    figs = [
        ('Turning, all 32 facings', 'in-mod · HD · 120 ms', "The mod's frames beside HD, facing by facing.",
         pv + '/turn.gif', 'memp-turn-%s.gif' % ver, "The Mobile EMP Cannon turning: the mod's frames and HD %s" % ver),
        ('The cockpit slot', '%s · 4x' % ver, "New in v3 (your ask): a cockpit slot across the grey box's front, the "
         "Disruptor's viewport made long and low to fit the box. It faces forward, so facing east it turns edge-on "
         "behind the tower.", pv + '/slot-closeup.png', 'memp-slot-%s.png' % ver,
         "The Mobile EMP Cannon's cockpit slot on the grey box, %s, in four facings" % ver),
        ('Close up', '%s · 3x' % ver, "The emitter on its plinth, the ribbed conduits, the hatch box and the deck.",
         pv + '/closeups.png', 'memp-closeups-%s.png' % ver, 'The Mobile EMP Cannon %s close up' % ver),
        ('TS, %s and %s' % (PREV[0], ver), 'four facings', "TS as the mod draws it now (moved down onto the ground, "
         "where the HD unit stands), %s and %s." % (PREV[0], ver), tmp + '/ts-prev-new.png',
         'memp-%s-%s.png' % (PREV[0], ver), 'The Mobile EMP Cannon: TS, %s and %s' % (PREV[0], ver)),
        ('8 facings', 'in-mod · HD', "Every fourth facing, the mod's frames beside the HD frames of the same numbers.",
         pv + '/8-facings.png', 'memp-8-facings-%s.png' % ver, "The Mobile EMP Cannon in 8 facings: the mod's and HD %s"
         % ver),
        ('Shape against TS', 'overlap %s flat · %s finished' % (shape, final),
         "The model drawn flat, a colour per part, in the mod's camera beside the mod's frames, every fourth facing.",
         pv + '/shape-8-facings.png', 'memp-shape-%s.png' % ver, "TS's voxel render beside the model drawn flat"),
        ('The blast', "v1's · 12 frames", "The EMP ring, unchanged from v1: TS's frames redrawn at the canvas's "
         "resolution, the mod's beside HD.", pv + '/blast.gif', 'memp-blast-%s.gif' % ver,
         "The Mobile EMP Cannon's blast: the mod's frames and HD"),
        ('Scale', 'as the game draws them', "Next to the HD harvester and EA's M.A.D. Tank.", pv + '/scale.png',
         'memp-scale-%s.png' % ver, 'The Mobile EMP Cannon %s beside the HD harvester and the M.A.D. Tank' % ver),
    ]
    added = addtab.add('memp', 'Mobile EMP Cannon', 'M_EMP.VXL + MEMPFX · TSMEMP in the mod', note, figs, status=ver, chg=ver,
                       keep_place=True)
    files = {p: os.environ.get('REVIEW', 'units-review') + '/' + p for p in added}
    for p in OLD:
        files[p] = None
    print(json.dumps(files, indent=1))
