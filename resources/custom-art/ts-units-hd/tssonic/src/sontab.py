"""sontab.py - the Disruptor's tab on the units review page, from its package: the assembled close-up, the
TS | v4 | vN sheet and the turret on the deck close up (v4 against vN, at 3x and at the game's size), then the tab (in its
old place) with the package's previews.  Prints the files map for the publish.

    python3 sontab.py PKG version shape_hull shape_turret final_hull
"""
import os
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.environ.get('REVIEW', 'units-review'))
import addtab
import sonlook

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
OLD = ['gif/sonic-turn-v4.gif', 'img/sonic-closeup-v4.png', 'img/sonic-deck-v4.png', 'img/sonic-arm-v4.png',
       'img/sonic-viewport-v4.png', 'img/sonic-v3-v4.png', 'img/sonic-8-facings-v4.png', 'img/sonic-shape-v4.png',
       'img/sonic-scale-v4.png']
V4 = os.environ.get('V4_FRAMES', 'v4/frames') + '/tssonic-%04d.png'


def deck(pkg, out, ver):
    """the green rear deck with the turret on it, v4 against vN: at 3x, and at the game's size (the canvas at two
    thirds) shown 4.5x with square pixels."""
    rows = []
    for f, crop in ((4, (230, 90, 400, 250)), (28, (60, 100, 230, 260)), (8, (200, 70, 380, 240))):
        row = []
        for pat, px, lab in ((V4, sonlook.SEAT_V4, 'v4'), (pkg + '/frames/tssonic-%04d.png', sonlook.SEAT_V5, ver)):
            a = sonlook.assembled(pat, f, True, px)
            c = a.crop(crop)
            big = c.resize((c.width * 3, c.height * 3), Image.LANCZOS).convert('RGB')
            g = a.resize((299, 299), Image.LANCZOS).crop(tuple(int(v * 2 / 3) for v in crop))
            gbig = g.resize((g.width * 9 // 2, g.height * 9 // 2), Image.NEAREST).convert('RGB')
            row += [(big, '%s facing %d, 3x' % (lab, f)), (gbig, '%s facing %d, game size, 4.5x' % (lab, f))]
        rows.append([row[0], row[2], row[1], row[3]])
    W = max(t.width for r in rows for t, _ in r); H = max(t.height for r in rows for t, _ in r)
    S = Image.new('RGB', (4 * (W + 6) - 6, len(rows) * (H + 26)), (30, 30, 30))
    d = ImageDraw.Draw(S)
    for i, r in enumerate(rows):
        for j, (t, lab) in enumerate(r):
            x, y = j * (W + 6), i * (H + 26)
            S.paste(t, (x, y + 22)); d.text((x + 4, y + 3), lab, font=FONT, fill=(240, 230, 180))
    S.save(out)


def pads(pkg, out, ver):
    """the turret's pad on the deck in all 32 facings, laid as the game lays the frames, at 1.5x."""
    from soncam import origin
    ox, oy = origin()
    tiles = []
    for f in range(32):
        a = sonlook.assembled(pkg + '/frames/tssonic-%04d.png', f, True, sonlook.SEAT_V5)
        dx, dy = sonlook.seat(f, sonlook.SEAT_V5)
        cx, cy = ox + dx, oy + dy - 50
        c = a.crop((int(cx - 70), int(cy - 50), int(cx + 70), int(cy + 50))).convert('RGB')
        c = c.resize((210, 150), Image.LANCZOS)
        ImageDraw.Draw(c).text((4, 2), 'facing %d' % f, font=FONT, fill=(255, 240, 160))
        tiles.append(c)
    S = Image.new('RGB', (8 * 214 - 4, 4 * 154 - 4), (20, 20, 20))
    for i, t in enumerate(tiles):
        S.paste(t, ((i % 8) * 214, (i // 8) * 154))
    S.save(out)


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
    pkg, ver, shape_hull, shape_tur, final_hull = sys.argv[1:6]
    tmp = os.path.join(HERE, 'logs')
    pv = pkg + '/previews'
    closeup(pkg, [12, 20, 28, 4], tmp + '/closeup.png')
    sonlook.sheet(tmp + '/prev-new.png', pkg + '/frames/tssonic-%04d.png', [4, 12, 20, 28], 1.2, ver,
                  prev=('v4', V4, sonlook.SEAT_V4), ts=("TS (the mod's frames, TS's seat)", sonlook.INMOD, sonlook.SEAT_TS))
    deck(pkg, tmp + '/deck.png', ver)
    pads(pkg, tmp + '/pads.png', ver)
    import vdeliver, sonspec
    fmt = pkg + '/frames/tssonic-%04d.png'
    name, seq, ms = sonspec.GIFS[0]
    vdeliver.gif(sonspec, fmt, seq, tmp + '/page-' + name, scale=1.0, ms=ms)
    note = open(os.path.join(HERE, 'tab_note.txt')).read().strip()
    figs = [
        ('Turning, all 32 facings', 'in-mod · HD · 120 ms',
         "The mod's frames beside HD, facing by facing, the turret seated on the rear deck on both.",
         tmp + '/page-turn.gif', 'sonic-turn-%s.gif' % ver,
         "The Disruptor turning through its 32 facings: the mod's frames and HD %s" % ver),
        ('Close up', '%s · four facings' % ver,
         "Hull and turret together, the turret's pad on the green rear deck, its back at the deck's back.",
         tmp + '/closeup.png', 'sonic-closeup-%s.png' % ver, 'The Disruptor %s close up in four facings' % ver),
        ('The turret on the deck', 'v4 · %s · 3x and the game size' % ver,
         "The dish and the rest of the turret back at their size (your note: only the circular pad smaller); the pad "
         "as v4's, on the plain green deck. At the game's size (the canvas at two thirds) shown 4.5x with square pixels.",
         tmp + '/deck.png', 'sonic-deck-%s.png' % ver,
         "The Disruptor's turret on its deck, v4 against %s, at 3x and at the game's size" % ver),
        ('The pad, every facing', '%s · 1.5x · all 32' % ver,
         "The turret's pad on the green deck in all 32 facings, laid as the game lays the frames: centred side to side "
         "and inside the deck's edges in every one (each checked against the 3D model).",
         tmp + '/pads.png', 'sonic-pads-%s.png' % ver, "The Disruptor %s turret pad on its deck in all 32 facings" % ver),
        ('The arm', '%s · 4x · four facings' % ver,
         "TS's rod tilted up toward the dish: white cap, light body with its band, dark sleeve, fins, grey tip; the "
         "trunnion through its front on the zig-zag brackets (the FMV's stripes in TS's ochre and black), a spring "
         "piston each side back to the beam in front of the dish.", pv + '/arm-closeup.png',
         'sonic-arm-%s.png' % ver, 'The Disruptor %s emitter arm at 4x' % ver),
        ('The viewport', '%s · 4x · four facings' % ver,
         "The ochre box as the first look had it, with one viewport across its front where TS has its dark voxels: "
         "dark glass in an ochre frame.", pv + '/viewport-closeup.png', 'sonic-viewport-%s.png' % ver,
         "The Disruptor %s ochre box's viewport at 4x" % ver),
        ('TS, v4 and %s' % ver, 'four facings',
         "TS as the mod draws it now, with TS's own turret seat (a quarter cell aft: TS's turntable is wider than its "
         "deck too), v4 with the whole turret smaller, and %s with only its pad smaller." % ver,
         tmp + '/prev-new.png', 'sonic-v4-%s.png' % ver, 'The Disruptor: TS, v4 and %s' % ver),
        ('8 facings', 'in-mod · HD', "Every fourth facing, the mod's frames beside the HD frames of the same numbers.",
         pv + '/8-facings.png', 'sonic-8-facings-%s.png' % ver,
         "The Disruptor in 8 facings: the mod's frames and HD %s" % ver),
        ('Shape against TS', 'hull %s · turret %s flat · hull %s finished' % (shape_hull, shape_tur, final_hull),
         "The model drawn flat, a colour per part, in the mod's cameras, beside the mod's frames: the hull's and the "
         "turret's every fourth facing (%s's pad is smaller than TS's on purpose)." % ver,
         pv + '/shape-8-facings.png', 'sonic-shape-%s.png' % ver,
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
