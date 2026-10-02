"""Shape check for the Upgrade Center: the model in TS's own camera over GTPLUG 00 (flat colours), the TS-angle render
next to TS's frame at the mod's scale, and the RA grid three ways (turned TS east -> south, turned the other way, and
not turned on a 2x3 plot).    python3 plugshape.py [out.png]"""
import os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw
import ypreview as P
import hd, plugfit as F, plugrender as R

T = '/home/claude/work/ts/ts-buildings-hd-handoff/12-TSPLUG/ts-original/'
BG = (96, 108, 72, 255)


def onbg(im):
    b = Image.new('RGBA', im.size, BG); b.alpha_composite(im.convert('RGBA')); return b


def label(im, txt):
    Rr = Image.new('RGBA', (im.width, im.height + 24), (30, 30, 30, 255)); Rr.paste(im, (0, 24)); P.label(Rr, txt, (6, 4))
    return Rr


def ra_ts(ss=2, head=96):
    """TS's way round (not turned) on a 2x3 plot: 256 x (384 + 2 head)."""
    W, Hp = 256, 384
    oy = head + Hp - np.sin(np.deg2rad(32.0)) * 192.0
    v = hd.ra_view((W, Hp + 2 * head), (W / 2, oy), ss=ss)
    return R.PlugPrep(v, vname='ra', layout='ts').frame()


def build(out):
    img, r = F.flat(6, prog=dict(dish=0.0))
    ts = Image.open(f'{T}GTPLUG/frames/00.png').convert('RGBA')
    tmp = out + '.fit.png'
    F.sheet(img, ts, tmp, 6, r)
    fit = Image.open(tmp).convert('RGBA'); os.remove(tmp)
    w, h = fit.size
    row1 = label(fit.crop((0, 20, w, 20 + (h - 28) // 2)), "GTPLUG 00 | the model in TS's own camera (flat colours, 6x)")
    K = R.ISO_K
    tsz = ts.resize((round(144 * K), round(120 * K)), Image.NEAREST)
    can = Image.new('RGBA', (384, 384), (0, 0, 0, 0)); can.paste(tsz, (int(R.ISO_O[0]), int(R.ISO_O[1])))
    pr, v = R.prep('iso', 2)
    iso = R.on_canvas(pr.frame(), 'iso')
    a = onbg(can).resize((576, 576), Image.NEAREST); b = onbg(iso).resize((576, 576), Image.LANCZOS)
    r2 = Image.new('RGBA', (576 * 2 + 8, 576), (30, 30, 30, 255)); r2.paste(a, (0, 0)); r2.paste(b, (584, 0))
    row2 = label(r2, "TS angle: TS's frame at the mod's scale and place | HD on the mod's 384x384 canvas (1.5x)")
    tiles = []
    for lay, txt in (('ra', 'RA grid turned (TS east -> south): ramp + pipes to the camera'),
                     ('ra1', 'RA grid turned the other way (TS west -> south)')):
        pr, v = R.prep('ra', 2, layout=lay)
        im = onbg(R.on_canvas(pr.frame(), 'ra'))
        d = ImageDraw.Draw(im); d.rectangle((0, R.HEAD, 383, R.HEAD + 256), outline=(255, 255, 255, 255))
        tiles.append(label(im.resize((im.width * 3 // 2, im.height * 3 // 2), Image.LANCZOS), txt))
    im = onbg(ra_ts())
    d = ImageDraw.Draw(im); d.rectangle((0, 96, 255, 96 + 384), outline=(255, 255, 255, 255))
    tiles.append(label(im.resize((im.width * 3 // 2, im.height * 3 // 2), Image.LANCZOS), 'not turned (needs a 2x3 plot)'))
    Wd = sum(t.width for t in tiles) + 16; Hd = max(t.height for t in tiles)
    r3 = Image.new('RGBA', (Wd, Hd), (30, 30, 30, 255)); x = 0
    for t in tiles:
        r3.paste(t, (x, 0)); x += t.width + 8
    rows = [row1, row2, r3]
    Wt = max(r.width for r in rows); Ht = sum(r.height for r in rows) + 16
    S = Image.new('RGBA', (Wt, Ht), (30, 30, 30, 255)); y = 0
    for r_ in rows:
        S.paste(r_, (0, y)); y += r_.height + 8
    S.convert('RGB').save(out)


if __name__ == '__main__':
    os.environ.setdefault('PLUG_HEAD', '96')
    build(sys.argv[1] if len(sys.argv) > 1 else '/home/claude/work/scratch/plug/shape-check.png')
