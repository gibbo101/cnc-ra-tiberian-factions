"""
infpreview.py - an infantry unit's previews, made from its finished frames (frames/), beside TS's sprite (scaled as the
mod draws it) and the mod's own frame:

  SEQ-8-facings.gif   a looping sequence in all 8 facings, TS above HD, one GIF frame a step
  SEQ.gif             TS | in-mod | HD for one facing's frames (or a single-facing sequence)
  lie-down.gif        standing -> lying down -> prone -> getting up -> standing, 2 facings

    python3 infpreview.py UNIT FRAMES_DIR OUT_DIR
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
import inffit as F
import infcheck as C
import infseq as SQ

DIRS = ['N', 'NW', 'W', 'SW', 'S', 'SE', 'E', 'NE']
ORDER = [0, 7, 6, 5, 4, 3, 2, 1]
TICK_MS = 1000.0 / 15.0


class Frames:
    def __init__(self, unit, fdir):
        d, name = F.UNITS[unit]
        self.unit, self.fdir, self.stem = unit, fdir, 'ts' + name.lower()
        self.mod = C.ROOT + '%s/in-mod/ts%s/frames/ts%s-%%04d.png' % (d, name.lower(), name.lower())

    def hd(self, k):
        return Image.open(os.path.join(self.fdir, '%s-%04d.png' % (self.stem, k))).convert('RGBA')

    def ts(self, k):
        return C.ts_on_canvas(self.unit, k)

    def inmod(self, k):
        return Image.open(self.mod % k).convert('RGBA')


def tile(im, label, crop, z):
    b = Image.new('RGBA', im.size, C.BG); b.alpha_composite(im.convert('RGBA'))
    b = b.crop(crop).convert('RGB')
    b = b.resize((round(b.width * z), round(b.height * z)), Image.LANCZOS)
    ImageDraw.Draw(b).text((3, 2), label, fill=(230, 220, 160))
    return b


def save_gif(frames, path, ms):
    pal = [f.convert('P', palette=Image.ADAPTIVE, colors=255) for f in frames]
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=[int(round(m)) for m in ms] if
                isinstance(ms, list) else int(round(ms)), loop=0, disposal=1)


def grid8(fr, seq, path, ticks, crop=(78, 30, 190, 130), z=1.5):
    out = []
    for s, ks in SQ.frames_of(fr.unit, seq):
        cols = []
        for f in ORDER:
            cols.append([tile(fr.ts(ks[f]), 'TS %s' % DIRS[f], crop, z), tile(fr.hd(ks[f]), 'HD %s  %d' % (DIRS[f], ks[f]),
                                                                            crop, z)])
        cw, ch = cols[0][0].size
        im = Image.new('RGB', (4 * (cw + 3), 4 * (ch + 3)), (18, 20, 24))
        for i, col in enumerate(cols):
            for j, t in enumerate(col):
                im.paste(t, ((i % 4) * (cw + 3), ((i // 4) * 2 + j) * (ch + 3)))
        out.append(im)
    save_gif(out, path, ticks * TICK_MS)


def strip(fr, ks, path, ticks, crop=(68, 16, 200, 148), z=2.0, hold=None):
    out = []
    for k in ks:
        row = [tile(fr.ts(k), "TS's sprite  %d" % k, crop, z), tile(fr.inmod(k), __import__('infunit').mod_label(__import__('infunit').CURRENT[0]), crop, z),
               tile(fr.hd(k), 'HD', crop, z)]
        im = Image.new('RGB', (sum(t.width + 4 for t in row), row[0].height), (18, 20, 24))
        x = 0
        for t in row:
            im.paste(t, (x, 0)); x += t.width + 4
        out.append(im)
    ms = [ticks * TICK_MS] * len(out)
    if hold:
        ms[-1] = hold
    save_gif(out, path, ms)


def main():
    unit, fdir, odir = sys.argv[1:4]
    import infunit; infunit.use(unit)
    os.makedirs(odir, exist_ok=True)
    fr = Frames(unit, fdir)
    grid8(fr, 'walk', os.path.join(odir, 'run-8-facings.gif'), 2)
    grid8(fr, 'crawl', os.path.join(odir, 'crawl-8-facings.gif'), 2, crop=(60, 50, 208, 140))
    # the fire sequences' names: E1 fires, E2 throws
    fn, pn = {'e2': ('throw', 'throw-prone')}.get(unit, ('fire', 'fire-prone'))
    armed = unit not in ('eng', 'medic', 'chamspy', 'mhijack')   # (the unarmed units' fire frames are empty, never shown)
    if armed:
        grid8(fr, 'fire', os.path.join(odir, fn + '-8-facings.gif'), 1, crop=(50, 0, 218, 130))
        grid8(fr, 'prone_fire', os.path.join(odir, pn + '-8-facings.gif'), 1, crop=(50, 30, 218, 150))
    first = dict(walk=8, crawl=86)
    for seq, f, name, ticks, crop in (('walk', 2, 'run-west', 2, (68, 16, 200, 148)),
                                      ('walk', 4, 'run-south', 2, (68, 16, 200, 148)),
                                      ('crawl', 2, 'crawl-west', 2, (48, 16, 220, 148)),
                                      ('crawl', 4, 'crawl-south', 2, (48, 16, 220, 148)),
                                      ('fire', 2, fn + '-west', 1, (30, 0, 210, 140)),
                                      ('fire', 4, fn + '-south', 1, (48, 16, 220, 160))):
        if seq == 'fire' and not armed:
            continue
        ks = [k for s, kk in SQ.frames_of(unit, seq) for k in [kk[f]]]
        strip(fr, ks, os.path.join(odir, name + '.gif'), ticks, crop=crop)
    for seq, name in (('idle1', 'idle-1'), ('idle2', 'idle-2'), ('death1', 'death-1'), ('death2', 'death-2')):
        if unit == 'jj' and seq.startswith('death'):
            continue                                # (the Jumpjet's deaths are empty: he dies by the tumble)
        ks = [k for k, f in SQ.frames_of(unit, seq)]
        strip(fr, ks, os.path.join(odir, name + '.gif'), 2, crop=(48, 0, 220, 160), hold=900)
    if unit == 'medic':
        # the heal: one strip whatever the facing
        ks = [k for k, f in SQ.frames_of(unit, 'heal')]
        strip(fr, ks, os.path.join(odir, 'heal.gif'), 2, crop=(40, 0, 230, 160), hold=900)
    if unit == 'jj':
        # his flight: flying, hovering and firing in the air, every facing; two facings at the game's speed; the tumble
        air = (40, 0, 230, 150)
        grid8(fr, 'fly', os.path.join(odir, 'fly-8-facings.gif'), 2, crop=air, z=1.2)
        grid8(fr, 'hover', os.path.join(odir, 'hover-8-facings.gif'), 2, crop=air, z=1.2)
        grid8(fr, 'fire_fly', os.path.join(odir, 'fire-fly-8-facings.gif'), 1, crop=air, z=1.2)
        for seq, f, name, ticks in (('fly', 2, 'fly-west', 2), ('fly', 4, 'fly-south', 2),
                                    ('fire_fly', 2, 'fire-fly-west', 1), ('hover', 4, 'hover-south', 2)):
            ks = [kk[f] for s, kk in SQ.frames_of(unit, seq)]
            strip(fr, ks, os.path.join(odir, name + '.gif'), ticks, crop=(30, 0, 240, 150))
        ks = [k for k, f in SQ.frames_of(unit, 'tumble')]
        strip(fr, ks, os.path.join(odir, 'tumble.gif'), 2, crop=(20, 0, 250, 160), hold=900)
    # lying down and getting up, two facings: standing, the 2 lie-down frames, prone (held), 2 get-up frames, standing
    for f in ((2, 5) if 'lie_down' in SQ.SEQ[unit] and unit != 'cyborg' else ()):
        # (the Cyborg's lying down and getting up are empty, as TS's; the Cyborg Commando has none)
        ld = [kk[f] for s, kk in SQ.frames_of(unit, 'lie_down')]
        gu = [kk[f] for s, kk in SQ.frames_of(unit, 'get_up')]
        prone = SQ.frames_of(unit, 'crawl')[0][1][f]
        ks = [f] + ld + [prone] + gu + [f]
        out = []
        for k in ks:
            row = [tile(fr.ts(k), "TS's sprite  %d" % k, (48, 0, 220, 150), 1.6),
                   tile(fr.hd(k), 'HD', (48, 0, 220, 150), 1.6)]
            im = Image.new('RGB', (sum(t.width + 4 for t in row), row[0].height), (18, 20, 24))
            x = 0
            for t in row:
                im.paste(t, (x, 0)); x += t.width + 4
            out.append(im)
        ms = [700] + [2 * TICK_MS] * len(ld) + [700] + [3 * TICK_MS] * len(gu) + [700]
        save_gif(out, os.path.join(odir, 'lie-down-get-up-%s.gif' % DIRS[f]), ms)
    print('previews in', odir)


if __name__ == '__main__':
    main()
