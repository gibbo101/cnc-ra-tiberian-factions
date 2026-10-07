"""pristab.py - the Prism Tank's tab on the units review page, from its package: the turning GIF, the close-up, the
in-mod | v1 | vN sheet, then the package's previews; the tab in its old place.  Prints the files map for the publish.

    python3 pristab.py PKG version shape_hull shape_turret final_hull
"""
import os
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.environ.get('REVIEW', 'units-review'))
import addtab, re
from paths import HANDOFF

HERE = os.path.dirname(os.path.abspath(__file__))
REVIEW = os.environ.get('REVIEW', 'units-review')


def _old_files():
    h = open(os.path.join(REVIEW, 'index.html')).read()
    m = re.search(r'  <section class="panel" id="pris".*?  </section>\n', h, re.S)
    return re.findall(r'src="([^"]+)"', m.group()) if m else []


OLD_FILES = _old_files()
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
OLD = OLD_FILES
INMOD = HANDOFF + '/28-R2PRIS/in-mod/r2pris/frames/r2pris-%04d.png'
PREV = ('v1', os.environ.get('V1_FRAMES', 'v1/frames') + '/r2pris-%04d.png')


def closeup2(pkg, out, ver, fs=(28, 20, 12, 4)):
    """the prism on its ring at 3x in four facings."""
    from vdeliver import layered, on_bg
    tiles = []
    for f in fs:
        c = on_bg(layered(pkg + '/frames/r2pris-%04d.png', [f, 32 + f])).crop((120, 20, 270, 150))
        c = c.resize((c.width * 3, c.height * 3), Image.LANCZOS).convert('RGB')
        ImageDraw.Draw(c).text((6, 4), '%s  facing %d' % (ver, f), font=FONT, fill=(250, 240, 170))
        tiles.append(c)
    W, H = tiles[0].size
    S = Image.new('RGB', (2 * (W + 6) - 6, 2 * (H + 6) - 6), (24, 24, 26))
    for i, t in enumerate(tiles):
        S.paste(t, ((i % 2) * (W + 6), (i // 2) * (H + 6)))
    S.save(out)


def sheet(pkg, out, ver, fs=(28, 20, 12, 4), crop=(20, 20, 364, 290), z=1.0):
    from vdeliver import layered, on_bg
    rows = []
    for f in fs:
        row = []
        for pat, lab in ((INMOD, "the mod's frames"), (PREV[1], PREV[0]), (pkg + '/frames/r2pris-%04d.png', ver)):
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
    closeup2(pkg, tmp + '/prism.png', ver)
    import vdeliver, prisspec
    fmt = pkg + '/frames/r2pris-%04d.png'
    name, seq, ms = prisspec.GIFS[0]
    vdeliver.gif(prisspec, fmt, seq, tmp + '/page-' + name, scale=1.0, ms=ms)
    note = open(os.path.join(HERE, 'tab_note.txt')).read().strip()
    figs = [
        ('Turning, all 32 facings', 'in-mod · HD · 120 ms', "The mod's frames beside HD, facing by facing.",
         tmp + '/page-turn.gif', 'pris-turn-%s.gif' % ver,
         "The Prism Tank turning through its 32 facings: the mod's frames and HD %s" % ver),
        ('Close up', '%s · 2x · four facings' % ver,
         "Hull and turret together: the sponsons, the coolers and the fan on the rear deck, the ring, the cupola and the prism.",
         pv + '/closeup.png', 'pris-closeup-%s.png' % ver, 'The Prism Tank %s close up in four facings' % ver),
        ('The prism', '%s · 3x · four facings' % ver,
         "The prism on its post: the house-colour fan with its ribbed dark back and round side hubs, the emitter's "
         "glowing face in its house-colour frame, the stepped ring and the olive bearing under it.",
         tmp + '/prism.png', 'pris-prism-%s.png' % ver, 'The Prism Tank %s prism at 3x' % ver),
        ("The mod's frames, %s and %s" % (PREV[0], ver), 'four facings',
         "The Prism Tank as the mod draws it now, %s and %s." % (PREV[0], ver),
         tmp + '/prev-new.png', 'pris-%s-%s.png' % (PREV[0], ver), "The Prism Tank: the mod's frames, %s and %s" % (PREV[0], ver)),
        ('Turret turning', '32 facings · 120 ms', 'The prism through its 32 facings on the hull facing east.',
         pv + '/turret-turning.gif', 'pris-turret-turning-%s.gif' % ver,
         'The Prism Tank %s turret turning on the hull' % ver),
        ('8 facings', 'in-mod · HD', "Every fourth facing, the mod's frames beside the HD frames of the same numbers.",
         pv + '/8-facings.png', 'pris-8-facings-%s.png' % ver,
         "The Prism Tank in 8 facings: the mod's frames and HD %s" % ver),
        ('Shape against RA2', 'hull %s · turret %s flat · hull %s finished' % (shape_hull, shape_tur, final_hull),
         "The model drawn flat, a colour per part, in the mod's cameras, beside the mod's frames: the hull's and the "
         "turret's every fourth facing.", pv + '/shape-8-facings.png', 'pris-shape-%s.png' % ver,
         "RA2's voxel render beside the Prism Tank %s model drawn flat" % ver),
        ('Scale', 'as the game draws them', "Next to the HD harvester and EA's medium tank on one ground line.",
         pv + '/scale.png', 'pris-scale-%s.png' % ver, "The Prism Tank %s beside the HD harvester and EA's medium tank" % ver),
    ]
    added = addtab.add('pris', 'Prism Tank', 'SREF.VXL, SREFTUR.VXL · R2PRIS in the mod', note, figs,
                       status=ver, chg=ver, keep_place=True)
    files = {p: os.environ.get('REVIEW', 'units-review') + '/' + p for p in added}
    for p in OLD:
        files[p] = None
    print(json.dumps(files, indent=1))
