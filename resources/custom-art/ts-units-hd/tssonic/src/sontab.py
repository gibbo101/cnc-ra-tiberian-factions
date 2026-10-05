"""sontab.py - the Disruptor's tab on the units review page, from its package: the assembled close-up and the
TS | v1 | vN sheet, then the tab (in its old place) with the package's previews.  Prints the files map for the publish.

    python3 sontab.py PKG version shape_overlap final_overlap
"""
import os
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.environ.get('REVIEW', 'units-review'))
import addtab
import sonlook

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
OLD = ['gif/sonic-turn-v2.gif', 'img/sonic-closeup-v2.png', 'img/sonic-arm-v2.png', 'img/sonic-cockpit-v2.png',
       'img/sonic-v1-v2.png', 'img/sonic-8-facings-v2.png', 'img/sonic-shape-v2.png', 'img/sonic-scale-v2.png']


def closeup(pkg, fs, out, crop=(40, 40, 410, 320), z=1.5):
    tiles = []
    for f in fs:
        c = sonlook.assembled(pkg + '/frames/tssonic-%04d.png', f).crop(crop)
        tiles.append(c.resize((int(c.width * z), int(c.height * z)), Image.LANCZOS).convert('RGB'))
    W, H = tiles[0].size
    S = Image.new('RGB', (2 * (W + 6) - 6, ((len(tiles) + 1) // 2) * (H + 28)), (30, 30, 30))
    for i, (t, f) in enumerate(zip(tiles, fs)):
        x, y = (i % 2) * (W + 6), (i // 2) * (H + 28)
        S.paste(t, (x, y + 22))
        ImageDraw.Draw(S).text((x + 6, y + 3), 'hull %d + turret %d' % (f, 32 + f), font=FONT, fill=(240, 230, 180))
    S.save(out)


if __name__ == '__main__':
    pkg, ver, shape_ov, final_ov = sys.argv[1:5]
    tmp = os.path.join(HERE, 'logs')
    pv = pkg + '/previews'
    closeup(pkg, [12, 20, 28, 4], tmp + '/closeup.png')
    sonlook.sheet(tmp + '/prev-new.png', pkg + '/frames/tssonic-%04d.png', [4, 12, 20, 28], 1.2, ver)
    import vdeliver, sonspec
    fmt = pkg + '/frames/tssonic-%04d.png'
    name, seq, ms = sonspec.GIFS[0]
    vdeliver.gif(sonspec, fmt, seq, tmp + '/page-' + name, scale=1.0, ms=ms)
    note = open(os.path.join(HERE, 'tab_note.txt')).read().strip()
    figs = [
        ('Turning, all 32 facings', 'in-mod · HD · 120 ms',
         "The mod's frames beside HD, facing by facing, the turret seated at the hull's back on both.",
         tmp + '/page-turn.gif', 'sonic-turn-%s.gif' % ver,
         "The Disruptor turning through its 32 facings: the mod's frames and HD %s" % ver),
        ('Close up', '%s · four facings' % ver,
         "Hull and turret together, the turret's ring on the hull's back.", tmp + '/closeup.png',
         'sonic-closeup-%s.png' % ver, 'The Disruptor %s close up in four facings' % ver),
        ('The arm', '%s · 4x · four facings' % ver,
         "TS's rod tilted up toward the dish: white cap, light body with its band, dark sleeve, fins, grey tip; the "
         "trunnion through its front on the zig-zag brackets (the FMV's stripes in TS's ochre and black), a spring "
         "piston each side back to the beam in front of the dish.", pv + '/arm-closeup.png',
         'sonic-arm-%s.png' % ver, 'The Disruptor %s emitter arm at 4x' % ver),
        ('The viewport', '%s · 4x · four facings' % ver,
         "The ochre box as the first look had it, with one viewport across its front where TS has its dark voxels: "
         "dark glass in an ochre frame.", pv + '/viewport-closeup.png', 'sonic-viewport-%s.png' % ver,
         "The Disruptor %s ochre box's viewport at 4x" % ver),
        ('TS, v1 and %s' % ver, 'four facings', 'TS as the mod draws it now, v1, and %s, the turret seated alike.' % ver,
         tmp + '/prev-new.png', 'sonic-v1-%s.png' % ver, 'The Disruptor: TS, v1 and %s' % ver),
        ('8 facings', 'in-mod · HD', "Every fourth facing, the mod's frames beside the HD frames of the same numbers.",
         pv + '/8-facings.png', 'sonic-8-facings-%s.png' % ver,
         "The Disruptor in 8 facings: the mod's frames and HD %s" % ver),
        ('Shape against TS', 'overlap %s flat · %s finished' % (shape_ov, final_ov),
         "The model drawn flat, a colour per part, in the mod's cameras, beside the mod's frames: the hull's and the "
         "turret's every fourth facing.", pv + '/shape-8-facings.png', 'sonic-shape-%s.png' % ver,
         "TS's voxel render beside the Disruptor %s model drawn flat" % ver),
        ('Scale', 'as the game draws them', 'Next to the HD harvester on one ground line.',
         pv + '/scale.png', 'sonic-scale-%s.png' % ver, 'The Disruptor %s beside the HD harvester' % ver),
    ]
    added = addtab.add('sonic', 'Disruptor', 'SONIC.VXL + SONICTUR.VXL · TSSONIC in the mod', note, figs, status=ver,
                       chg=ver, keep_place=True)
    files = {p: os.environ.get('REVIEW', 'units-review') + '/' + p for p in added}
    for p in OLD:
        files[p] = None
    print(json.dumps(files, indent=1))
