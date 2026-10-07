"""apoctab.py - the Apocalypse's tab on the units review page, from its package: the turning GIF, the close-up, the
in-mod | v1 | vN sheet, then the package's previews; the tab in its old place.  Prints the files map for the publish.

    python3 apoctab.py PKG version shape_hull shape_turret final_hull
"""
import os
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.environ.get('REVIEW', 'units-review'))
import addtab
from paths import HANDOFF

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
OLD = ['gif/apoc-turn-v2.gif', 'img/apoc-closeup-v2.png', 'img/apoc-v1-v2.png', 'gif/apoc-turret-turning-v2.gif',
       'img/apoc-8-facings-v2.png', 'img/apoc-shape-v2.png', 'img/apoc-scale-v2.png']
INMOD = HANDOFF + '/27-R2APOC/in-mod/r2apoc/frames/r2apoc-%04d.png'
PREV = ('v2', os.environ.get('V2_FRAMES', 'v2/frames') + '/r2apoc-%04d.png')


def plough(pkg, out, ver):
    """the plough at the nose, the previous version against this one, at 3x in four facings."""
    from vdeliver import layered, on_bg
    tiles = []
    for f, crop in ((20, (250, 170, 410, 300)), (12, (30, 170, 190, 300)), (28, (280, 80, 420, 210)),
                    (4, (40, 70, 200, 200))):
        for pat, lab in ((PREV[1], PREV[0]), (pkg + '/frames/r2apoc-%04d.png', ver)):
            c = on_bg(layered(pat, [f, 32 + f])).crop(crop)
            c = c.resize((c.width * 3, c.height * 3), Image.LANCZOS).convert('RGB')
            ImageDraw.Draw(c).text((6, 4), '%s  facing %d' % (lab, f), font=FONT, fill=(250, 240, 170))
            tiles.append(c)
    W = max(t.width for t in tiles); H = max(t.height for t in tiles)
    S = Image.new('RGB', (2 * (W + 6) - 6, 4 * (H + 6) - 6), (24, 24, 26))
    for i, t in enumerate(tiles):
        S.paste(t, ((i % 2) * (W + 6), (i // 2) * (H + 6)))
    S.save(out)


def sheet(pkg, out, ver, fs=(28, 20, 12, 4), crop=(50, 60, 400, 310), z=1.0):
    from vdeliver import layered, on_bg
    rows = []
    for f in fs:
        row = []
        for pat, lab in ((INMOD, "the mod's frames"), (PREV[1], PREV[0]), (pkg + '/frames/r2apoc-%04d.png', ver)):
            c = on_bg(layered(pat, [f, 32 + f])).crop(crop)
            c = c.resize((int(c.width * z), int(c.height * z)), Image.LANCZOS).convert('RGB')
            ImageDraw.Draw(c).text((6, 4), '%s  facing %d' % (lab, f), font=FONT, fill=(250, 240, 170))
            row.append(c)
        rows.append(row)
    W, H = rows[0][0].size
    S = Image.new('RGB', (3 * (W + 6) - 6, len(rows) * (H + 6) - 6), (24, 24, 26))
    for i, r in enumerate(rows):
        for j, t in enumerate(r):
            S.paste(t, (j * (W + 6), i * (H + 6)))
    S.save(out)


if __name__ == '__main__':
    pkg, ver, shape_hull, shape_tur, final_hull = sys.argv[1:6]
    tmp = os.path.join(HERE, 'logs')
    os.makedirs(tmp, exist_ok=True)
    pv = pkg + '/previews'
    sheet(pkg, tmp + '/prev-new.png', ver)
    plough(pkg, tmp + '/plough.png', ver)
    import vdeliver, apocspec
    fmt = pkg + '/frames/r2apoc-%04d.png'
    name, seq, ms = apocspec.GIFS[0]
    vdeliver.gif(apocspec, fmt, seq, tmp + '/page-' + name, scale=1.0, ms=ms)
    note = open(os.path.join(HERE, 'tab_note.txt')).read().strip()
    figs = [
        ('Turning, all 32 facings', 'in-mod · HD · 120 ms', "The mod's frames beside HD, facing by facing.",
         tmp + '/page-turn.gif', 'apoc-turn-%s.gif' % ver,
         "The Apocalypse turning through its 32 facings: the mod's frames and HD %s" % ver),
        ('Close up', '%s · 2x · four facings' % ver,
         "Hull and turret together: the drums, the engine grilles, the rocket pods, the hatch and the spiked plough.",
         pv + '/closeup.png', 'apoc-closeup-%s.png' % ver, 'The Apocalypse %s close up in four facings' % ver),
        ('The plough', '%s · %s · 3x · four facings' % (PREV[0], ver),
         "%s's flat zig-zag bar against %s's: a chiselled blade with a knife edge and seven spikes angled forward and "
         "down, dark gunmetal with edges that catch the light." % (PREV[0], ver),
         tmp + '/plough.png', 'apoc-plough-%s.png' % ver, "The Apocalypse's plough, %s against %s, at 3x" % (PREV[0], ver)),
        ("The mod's frames, %s and %s" % (PREV[0], ver), 'four facings',
         "The Apocalypse as the mod draws it now, %s and %s." % (PREV[0], ver),
         tmp + '/prev-new.png', 'apoc-%s-%s.png' % (PREV[0], ver), "The Apocalypse: the mod's frames, %s and %s" % (PREV[0], ver)),
        ('Turret turning', '32 facings · 120 ms', 'The turret through its 32 facings on the hull facing east.',
         pv + '/turret-turning.gif', 'apoc-turret-turning-%s.gif' % ver,
         'The Apocalypse %s turret turning on the hull' % ver),
        ('8 facings', 'in-mod · HD', "Every fourth facing, the mod's frames beside the HD frames of the same numbers.",
         pv + '/8-facings.png', 'apoc-8-facings-%s.png' % ver,
         "The Apocalypse in 8 facings: the mod's frames and HD %s" % ver),
        ('Shape against RA2', 'hull %s · turret %s flat · hull %s finished' % (shape_hull, shape_tur, final_hull),
         "The model drawn flat, a colour per part, in the mod's cameras, beside the mod's frames: the hull's and the "
         "turret's every fourth facing (the whip antennas are thin, as Westwood's, where RA2's voxels are a voxel or two "
         "thick).", pv + '/shape-8-facings.png', 'apoc-shape-%s.png' % ver,
         "RA2's voxel render beside the Apocalypse %s model drawn flat" % ver),
        ('Scale', 'as the game draws them', "Next to the HD harvester and EA's Mammoth on one ground line.",
         pv + '/scale.png', 'apoc-scale-%s.png' % ver, "The Apocalypse %s beside the HD harvester and EA's Mammoth" % ver),
    ]
    added = addtab.add('apoc', 'Apocalypse Tank', 'MTNK.VXL, MTNKTUR.VXL, MTNKBARL.VXL · R2APOC in the mod', note, figs,
                       status=ver, chg=ver, keep_place=True)
    files = {p: os.environ.get('REVIEW', 'units-review') + '/' + p for p in added}
    for p in OLD:
        files[p] = None
    print(json.dumps(files, indent=1))
