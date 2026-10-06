"""ottab.py - the Orca Transport's tab on the units review page, from its package: a TS | previous | vN sheet, then
the tab (in its old place) with the package's previews.  Prints the files map for the publish.

    python3 ottab.py PKG version shape final
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.environ.get('REVIEW', 'units-review'))
import addtab
from paths import HANDOFF

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
OLD = ['gif/orcatran-turn-v2.gif', 'img/orcatran-closeups-v2.png', 'img/orcatran-front-v2.png', 'img/orcatran-v1-v2.png',
       'img/orcatran-8-facings-v2.png', 'img/orcatran-shape-v2.png', 'img/orcatran-scale-v2.png']
INMOD = os.path.join(HERE, 'ref', 'tsorcatran-%04d.png')
PREV = ('v2', os.environ.get('PREV_PKG', 'v2') + '/frames/tsorcatran-%04d.png')


def three(pkg, out, ver, fs=(4, 12, 20, 28), z=1.0):
    """TS (its voxel in the mod's camera) | the previous version | vN, facing by facing."""
    crop = (14, 70, 482, 370)
    rows = []
    for f in fs:
        row = []
        for name, pat in (("TS's voxels", INMOD), (PREV[0], PREV[1]), (ver, pkg + '/frames/tsorcatran-%04d.png')):
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
        ('Turning, all 32 facings', "TS's voxels · HD · 120 ms", "TS's voxel drawn in the mod's camera beside HD, facing "
         "by facing.", pv + '/turn.gif', 'orcatran-turn-%s.gif' % ver, "The Orca Transport turning: TS's voxels and HD %s"
         % ver),
        ('The back vents', "TS's voxels · HD · 3x", "TS's three black vents in the back slope, as the engines' "
         "exhausts: a triangle either side, its upright edge outboard and its slant running down and out from the "
         "khaki band, and one pointing up between them, TS's ochre struts making an inverted V. Each has dark vanes "
         "across its opening, a heat-darkened lip, and soot round it where TS has dark browns. TS's voxel drawn in "
         "the mod's camera beside the HD frame, the same window at 3x.", pv + '/back-vents.png',
         'orcatran-vents-%s.png' % ver, "The Orca Transport's exhausts: TS's voxels and HD %s" % ver),
        ('Close up', '%s · 3x' % ver, "The back: TS's three black vents in the slope under its khaki band, the bumper, "
         "the raised roof panel, TS's amber marks on the shoulders. The middle: TS's grey hatch in its dark frame, the "
         "hump with TS's two black slots running down its dark front, the rails along the deck's edges, the strakes "
         "and TS's house-colour wing over the middle legs.", pv + '/closeups.png', 'orcatran-closeups-%s.png' % ver,
         'The Orca Transport %s close up' % ver),
        ('The front', '%s · 3x' % ver, "The intake block behind the nose, TS's house-colour nose with its two "
         "blue-grey panes (TS's lavender) framed as the FMV's glazing, the front fans on their struts, the face plate.",
         pv + '/front-closeup.png', 'orcatran-front-%s.png' % ver, "The Orca Transport's front, %s, in four facings"
         % ver),
        ('TS, %s and %s' % (PREV[0], ver), 'four facings', "TS's voxel in the mod's camera, %s and %s." % (PREV[0], ver),
         tmp + '/ts-prev-new.png', 'orcatran-%s-%s.png' % (PREV[0], ver), 'The Orca Transport: TS, %s and %s'
         % (PREV[0], ver)),
        ('8 facings', "TS's voxels · HD", "Every fourth facing, TS's voxel beside the HD frames of the same numbers.",
         pv + '/8-facings.png', 'orcatran-8-facings-%s.png' % ver, "The Orca Transport in 8 facings: TS's voxels and HD "
         "%s" % ver),
        ('Shape against TS', 'overlap %s flat · %s finished' % (shape, final),
         "The model drawn flat, a colour per part, in the mod's camera beside TS's voxel, every fourth facing.",
         pv + '/shape-8-facings.png', 'orcatran-shape-%s.png' % ver, "TS's voxel beside the model drawn flat"),
        ('Scale', 'as the game draws them', "Next to the HD harvester, the HD Orca Fighter, the HD Carryall and EA's RA "
         "Chinook.", pv + '/scale.png', 'orcatran-scale-%s.png' % ver,
         'The Orca Transport %s beside the harvester, the Orca Fighter, the Carryall and the Chinook' % ver),
    ]
    added = addtab.add('orcatran', 'Orca Transport', 'ORCATRAN.VXL · TSORCATRAN in the mod', note, figs, status=ver,
                       chg=ver, keep_place=True)
    files = {p: os.environ.get('REVIEW', 'units-review') + '/' + p for p in added}
    for p in OLD:
        files[p] = None
    print(json.dumps(files, indent=1))
