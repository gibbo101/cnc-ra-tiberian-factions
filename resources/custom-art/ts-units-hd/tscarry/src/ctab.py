"""ctab.py - the Carryall's tab on the units review page, from its package: a TS | previous | vN sheet, then the
tab (in its old place) with the package's previews.  Prints the files map for the publish.

    python3 ctab.py PKG version shape final
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.environ.get('REVIEW', 'units-review'))
import addtab
from paths import HANDOFF

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
OLD = ['gif/carry-turn.gif', 'img/carry-8-facings.png', 'img/carry-scale.png']
INMOD = HANDOFF + '/25-TSCARRY/in-mod/tscarry/frames/tscarry-%04d.png'
PREV = ('v1', os.environ.get('PREV_PKG', 'v1') + '/frames/tscarry-%04d.png')


def three(pkg, out, ver, fs=(4, 12, 20, 28), z=1.0):
    """TS (the mod's frames) | the previous version | vN, facing by facing."""
    crop = (30, 40, 418, 316)
    rows = []
    for f in fs:
        row = []
        for name, pat in (("TS (the mod's frames)", INMOD), (PREV[0], PREV[1]), (ver, pkg + '/frames/tscarry-%04d.png')):
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
         pv + '/turn.gif', 'carry-turn-%s.gif' % ver, "The Carryall turning: the mod's frames and HD %s" % ver),
        ('Close up', '%s · 3x' % ver, "TS's house-colour pods along the beam with their khaki vents and TS's rust-red "
         "spots as small domes, TS's grey bell and its four claws (an ochre bracket, a black upper arm, a grey finger "
         "hooked at the tip), the tail fin with the fan in TS's round duct, the landing skids.",
         pv + '/closeups.png', 'carry-closeups-%s.png' % ver, 'The Carryall %s close up' % ver),
        ('The cab', '%s · 3x' % ver, "TS's black windows as dark glass with the cameo's blue in it, the windscreen one "
         "slope through TS's steps, TS's house-colour engine under the cab with its intake, the nose gear.",
         pv + '/cab-closeup.png', 'carry-cab-%s.png' % ver, "The Carryall's cab, %s, in four facings" % ver),
        ('Carrying the harvester', 'as the mod draws it', "The HD harvester drawn after the Carryall, 6 classic px "
         "below its centre (its ground shadow left out), every fourth facing: it covers the bell and the claws, as it "
         "will in the game.", pv + '/carrying.png', 'carry-carrying-%s.png' % ver,
         'The Carryall %s carrying the HD harvester' % ver),
        ('TS, %s and %s' % (PREV[0], ver), 'four facings', "TS as the mod draws it now, %s and %s." % (PREV[0], ver),
         tmp + '/ts-prev-new.png', 'carry-%s-%s.png' % (PREV[0], ver), 'The Carryall: TS, %s and %s'
         % (PREV[0], ver)),
        ('8 facings', 'in-mod · HD', "Every fourth facing, the mod's frames beside the HD frames of the same numbers.",
         pv + '/8-facings.png', 'carry-8-facings-%s.png' % ver, "The Carryall in 8 facings: the mod's and HD %s"
         % ver),
        ('Shape against TS', 'overlap %s flat · %s finished' % (shape, final),
         "The model drawn flat, a colour per part, in the mod's camera beside the mod's frames, every fourth facing.",
         pv + '/shape-8-facings.png', 'carry-shape-%s.png' % ver, "TS's voxel render beside the model drawn flat"),
        ('Scale', 'as the game draws them', "Next to the HD harvester, the HD Orca Bomber and EA's RA Chinook.",
         pv + '/scale.png', 'carry-scale-%s.png' % ver,
         'The Carryall %s beside the HD harvester, the HD Orca Bomber and the Chinook' % ver),
    ]
    added = addtab.add('carry', 'Carryall', 'TRNSPORT.VXL · TSCARRY in the mod', note, figs, status=ver, chg=ver,
                       keep_place=True)
    files = {p: os.environ.get('REVIEW', 'units-review') + '/' + p for p in added}
    for p in OLD:
        files[p] = None
    print(json.dumps(files, indent=1))
