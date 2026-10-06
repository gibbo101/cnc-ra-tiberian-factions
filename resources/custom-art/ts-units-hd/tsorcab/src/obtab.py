"""obtab.py - the Orca Bomber's tab on the units review page, from its package: a TS | previous | vN sheet, then the
tab (in its old place) with the package's previews.  Prints the files map for the publish.

    python3 obtab.py PKG version shape final
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.environ.get('REVIEW', 'units-review'))
import addtab
from paths import HANDOFF

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
OLD = ['gif/orcab-turn-v2.gif', 'img/orcab-closeups-v2.png', 'img/orcab-nose-v2.png', 'img/orcab-v1-v2.png',
       'img/orcab-8-facings-v2.png', 'img/orcab-shape-v2.png', 'img/orcab-scale-v2.png']
INMOD = HANDOFF + '/24-TSORCAB/in-mod/tsorcab/frames/tsorcab-%04d.png'
PREV = ('v2', os.environ.get('PREV_PKG', 'v2') + '/frames/tsorcab-%04d.png')


def three(pkg, out, ver, fs=(4, 12, 20, 28), z=1.0):
    """TS (the mod's frames) | the previous version | vN, facing by facing."""
    crop = (6, 8, 378, 266)
    rows = []
    for f in fs:
        row = []
        for name, pat in (("TS (the mod's frames)", INMOD), (PREV[0], PREV[1]), (ver, pkg + '/frames/tsorcab-%04d.png')):
            im = Image.open(pat % f).convert('RGBA')
            b = Image.new('RGBA', im.size, (96, 108, 72, 255)); b.alpha_composite(im)
            c = b.crop(crop).convert('RGB')
            if z != 1.0:
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
         pv + '/turn.gif', 'orcab-turn-%s.gif' % ver, "The Orca Bomber turning: the mod's frames and HD %s" % ver),
        ('Close up', '%s · 3x' % ver, "The fans with their blades in TS's brown rims, TS's house-colour panels on the "
         "body, the bombs in TS's black bays and the racks by the fans, the booms and the tail.",
         pv + '/closeups.png', 'orcab-closeups-%s.png' % ver, 'The Orca Bomber %s close up' % ver),
        ('The nose', '%s · 4x' % ver, "New in v3 (your note): TS's red lamp behind the canopy made a beacon, a red "
         "glass dome on a ring. TS's blue glazed nose as faceted blue glass, the keel under it and the bomb bays either "
         "side.", pv + '/nose-closeup.png', 'orcab-nose-%s.png' % ver,
         "The Orca Bomber's nose, %s, in four facings" % ver),
        ('TS, %s and %s' % (PREV[0], ver), 'four facings', "TS as the mod draws it now, %s and %s." % (PREV[0], ver),
         tmp + '/ts-prev-new.png', 'orcab-%s-%s.png' % (PREV[0], ver), 'The Orca Bomber: TS, %s and %s'
         % (PREV[0], ver)),
        ('8 facings', 'in-mod · HD', "Every fourth facing, the mod's frames beside the HD frames of the same numbers.",
         pv + '/8-facings.png', 'orcab-8-facings-%s.png' % ver, "The Orca Bomber in 8 facings: the mod's and HD %s"
         % ver),
        ('Shape against TS', 'overlap %s flat · %s finished' % (shape, final),
         "The model drawn flat, a colour per part, in the mod's camera beside the mod's frames, every fourth facing.",
         pv + '/shape-8-facings.png', 'orcab-shape-%s.png' % ver, "TS's voxel render beside the model drawn flat"),
        ('Scale', 'as the game draws them', "Next to the HD harvester, the HD Orca Fighter and EA's Hind.",
         pv + '/scale.png', 'orcab-scale-%s.png' % ver,
         'The Orca Bomber %s beside the HD harvester, the HD Orca Fighter and the Hind' % ver),
    ]
    added = addtab.add('orcab', 'Orca Bomber', 'ORCAB.VXL · TSORCAB in the mod', note, figs, status=ver, chg=ver,
                       keep_place=True)
    files = {p: os.environ.get('REVIEW', 'units-review') + '/' + p for p in added}
    for p in OLD:
        files[p] = None
    print(json.dumps(files, indent=1))
