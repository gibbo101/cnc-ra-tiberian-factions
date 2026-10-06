"""otab.py - the Orca Fighter's tab on the units review page, from its package: a TS | previous | vN sheet, the
options mock-up (paint from Luke's pictures that is not in TS's voxel), then the tab (in its old place) with the
package's previews.  Prints the files map for the publish.

    python3 otab.py PKG version shape final
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.environ.get('REVIEW', 'units-review'))
import addtab
from paths import HANDOFF

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
OLD = ['gif/orca-turn-v3.gif', 'img/orca-closeups-v3.png', 'img/orca-nose-v3.png', 'img/orca-options-v3.png',
       'img/orca-v2-v3.png', 'img/orca-8-facings-v3.png', 'img/orca-shape-v3.png', 'img/orca-scale-v3.png']
INMOD = HANDOFF + '/23-TSORCA/in-mod/tsorca/frames/tsorca-%04d.png'
PREV = ('v3', os.environ.get('PREV_PKG', 'v3') + '/frames/tsorca-%04d.png')


def three(pkg, out, ver, fs=(4, 12, 20, 28), z=1.0):
    """TS (the mod's frames) | the previous version | vN, facing by facing."""
    crop = (6, 8, 378, 266)
    rows = []
    for f in fs:
        row = []
        for name, pat in (("TS (the mod's frames)", INMOD), (PREV[0], PREV[1]), (ver, pkg + '/frames/tsorca-%04d.png')):
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


def options(out):
    """the shark mouth (Luke's pictures; not in TS's voxel, so not in the frames) at 4x."""
    env = dict(os.environ, ORCA_MOUTH='1')
    r = subprocess.run([sys.executable, 'orcaclose.py', out, '20,16', '4', '2', 'pods'], cwd=HERE, env=env,
                       capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stdout + r.stderr)


if __name__ == '__main__':
    pkg, ver, shape, final = sys.argv[1:5]
    tmp = os.path.join(HERE, 'logs')
    os.makedirs(tmp, exist_ok=True)
    pv = pkg + '/previews'
    three(pkg, tmp + '/ts-prev-new.png', ver)
    options(tmp + '/options.png')
    note = open(os.path.join(HERE, 'tab_note.txt')).read().strip()
    figs = [
        ('Turning, all 32 facings', 'in-mod · HD · 120 ms', "The mod's frames beside HD, facing by facing.",
         pv + '/turn.gif', 'orca-turn-%s.gif' % ver, "The Orca Fighter turning: the mod's frames and HD %s" % ver),
        ('Close up', '%s · 3x' % ver, "New in v4 (your note): a red rocket nose in each of the pods' twelve tubes (the "
         "FMV's red tips; TS's tubes are black). TS's house-colour panels on the pods, the fans with their blades, the "
         "hump and the canopy.", pv + '/closeups.png', 'orca-closeups-%s.png' % ver,
         'The Orca Fighter %s close up' % ver),
        ('The nose and the canopy', '%s · 4x' % ver, "The lower nose's sides ochre, like the rest of the nose (v3, "
         "your note; TS paints them house colour). TS's dark cockpit pit made the FMV's faceted canopy (its ridge "
         "within half a voxel of TS's nose); TS's black cheeks made intakes.", pv + '/nose-closeup.png',
         'orca-nose-%s.png' % ver,
         "The Orca Fighter's nose and canopy, %s, in four facings" % ver),
        ('Option from your pictures', 'not in %s · 4x' % ver, "The FMV's shark mouth and eye on the nose. It isn't in "
         "TS's voxel, so %s leaves it off; this is how it would look on it." % (ver, ver), tmp + '/options.png',
         'orca-options-%s.png' % ver, "A mock-up of the Orca Fighter with a shark mouth"),
        ('TS, %s and %s' % (PREV[0], ver), 'four facings', "TS as the mod draws it now, %s and %s." % (PREV[0], ver),
         tmp + '/ts-prev-new.png', 'orca-%s-%s.png' % (PREV[0], ver), 'The Orca Fighter: TS, %s and %s'
         % (PREV[0], ver)),
        ('8 facings', 'in-mod · HD', "Every fourth facing, the mod's frames beside the HD frames of the same numbers.",
         pv + '/8-facings.png', 'orca-8-facings-%s.png' % ver, "The Orca Fighter in 8 facings: the mod's and HD %s"
         % ver),
        ('Shape against TS', 'overlap %s flat · %s finished' % (shape, final),
         "The model drawn flat, a colour per part, in the mod's camera beside the mod's frames, every fourth facing.",
         pv + '/shape-8-facings.png', 'orca-shape-%s.png' % ver, "TS's voxel render beside the model drawn flat"),
        ('Scale', 'as the game draws them', "Next to the HD harvester and EA's TD Orca.", pv + '/scale.png',
         'orca-scale-%s.png' % ver, 'The Orca Fighter %s beside the HD harvester and the TD Orca' % ver),
    ]
    added = addtab.add('orca', 'Orca Fighter', 'ORCA.VXL · TSORCA in the mod', note, figs, status=ver, chg=ver,
                       keep_place=True)
    files = {p: os.environ.get('REVIEW', 'units-review') + '/' + p for p in added}
    for p in OLD:
        files[p] = None
    print(json.dumps(files, indent=1))
