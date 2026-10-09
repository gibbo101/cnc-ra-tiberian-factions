"""nodmirror.py - the Nod infantry hand-off laid out as the GDI pipeline reads it (the folder TS_HANDOFF names):
  <dir>/ts-original/<NAME>/frames/<name>-%03d.png      TS's decoded poses (symlinks to the Nod hand-off's frames)
  <dir>/in-mod/ts<name>/frames/ts<name>-%04d.png       what the mod would draw: TS's sprite x K (nearest) at (DX, DY) on
                                                       the 267 x 208 canvas, with TS's shadow (black, alpha 64) where we
                                                       have it (shadows/<name>-%03d.png, TS's shadow frames)
  <dir>/reference-hd/<ref>/frames/<ref>-%04d.png       EA's HD unit's 8 standing facings (from RA + TD HD Units' strips)

    NOD_HANDOFF=<the Nod hand-off> EA_UNITS=<RA + TD HD Units> TS_HANDOFF=<out> python3 nodmirror.py [unit ...]
"""
import os, sys
import numpy as np
from PIL import Image

SRC = os.environ.get('NOD_HANDOFF', 'ts-nod-units-hd-handoff')
DST = os.environ.get('TS_HANDOFF', 'ts-units-hd-handoff')
EA = os.environ.get('EA_UNITS', 'RA + TD HD Units')
SHADOWS = os.environ.get('TS_SHADOWS', 'shadows')     # TS's shadow frames, if any: <name>-%03d.png
CANVAS = (267, 208)
K = 3.068
# (unit key, Nod hand-off folder, TS sprite folder, its file prefix, mirror folder, NAME, EA reference)
UNITS = [('e3', '12-E3', 'E3', 'e3', '12-TSE3', 'E3', 'RA_E3'),
         ('cyborg', '13-CYBORG', 'CYBORG', 'cyborg', '13-TSCYBORG', 'CYBORG', 'TD_E1'),
         ('cyc2', '14-CYC2', 'CYC2', 'cyc2', '14-TSCYC2', 'CYC2', 'TD_RMBO'),
         ('mhijack', '15-MHIJACK', 'MHIJACK', 'mhijack', '15-TSMHIJACK', 'MHIJACK', 'RA_THF'),
         ('chamspy', '16-CHAMSPY', 'CHAMSPY', 'chamspy', '16-TSCHAMSPY', 'CHAMSPY', 'RA_SPY'),
         ('elcad', '17-ELCAD', 'SLAV', 'slav', '17-TSELCAD', 'ELCAD', 'RA_E1'),
         ('umagon', '19-UMAGON', 'UMAGON', 'umagon', '19-TSUMAGON', 'UMAGON', 'RA_E7')]


def placement(w, h):
    """(DX, DY) for a TS sprite canvas w x h: its centre where the mod puts a 61 x 61 sprite's (E1's 38.06, 10.57)."""
    cx, cy = 30.5 * K + 38.06, 30.5 * K + 10.57
    return cx - w / 2.0 * K, cy - h / 2.0 * K


def inmod(ts, shadow, DX, DY):
    """TS's frame (RGBA) x K, nearest, at (DX, DY); TS's shadow under it (black, alpha 64)."""
    W, H = CANVAS
    ys, xs = np.mgrid[0:H, 0:W]
    tx = np.floor((xs + 0.5 - DX) / K).astype(int); ty = np.floor((ys + 0.5 - DY) / K).astype(int)
    ok = (tx >= 0) & (tx < ts.shape[1]) & (ty >= 0) & (ty < ts.shape[0])
    out = np.zeros((H, W, 4), np.uint8)
    if shadow is not None:
        sh = np.zeros((H, W), bool)
        sh[ok] = shadow[ty[ok], tx[ok]]
        out[sh] = (0, 0, 0, 64)
    px = np.zeros((H, W, 4), np.uint8)
    px[ok] = ts[ty[ok], tx[ok]]
    body = px[..., 3] > 0
    out[body] = px[body]
    return Image.fromarray(out, 'RGBA')


def ea_frames(ref, dst):
    """EA's strip (8 standing facings in a row, cropped to their shared box) laid on the canvas, its feet on the
    infantry feet point (133.5, 111): the strip's lowest solid row on y 111, its middle on x 133.5."""
    side, nm = ref.split('_', 1)
    strip = Image.open(os.path.join(EA, side, nm + '.png')).convert('RGBA')
    w = strip.size[0] // 8
    a = np.array(strip)
    solid = (a[..., 3] > 250) & (a[..., :3].max(-1) > 30)
    low = np.nonzero(solid.any(1))[0].max()
    os.makedirs(dst, exist_ok=True)
    for f in range(8):
        cell = strip.crop((f * w, 0, (f + 1) * w, strip.size[1]))
        im = Image.new('RGBA', CANVAS, (0, 0, 0, 0))
        im.alpha_composite(cell, (int(round(133.5 - w / 2.0)), int(round(111 - low - 1))))
        im.save(os.path.join(dst, '%s-%04d.png' % (nm.lower(), f)))


def main(keys):
    for key, src, tsdir, pre, dst, NAME, ref in UNITS:
        if keys and key not in keys:
            continue
        fsrc = os.path.join(SRC, src, 'ts-original', tsdir, 'frames')
        n = len([f for f in os.listdir(fsrc) if f.endswith('.png')])
        tdst = os.path.join(DST, dst, 'ts-original', NAME, 'frames')
        mdst = os.path.join(DST, dst, 'in-mod', 'ts' + NAME.lower(), 'frames')
        os.makedirs(tdst, exist_ok=True); os.makedirs(mdst, exist_ok=True)
        w, h = Image.open(os.path.join(fsrc, '%s-%04d.png' % (pre, 0))).size
        DX, DY = placement(w, h)
        nsh = 0
        for k in range(n):
            s = os.path.join(fsrc, '%s-%04d.png' % (pre, k))
            t = os.path.join(tdst, '%s-%03d.png' % (NAME.lower(), k))
            if os.path.lexists(t):
                os.remove(t)
            os.symlink(s, t)
            ts = np.array(Image.open(s).convert('RGBA'))
            shp = os.path.join(SHADOWS, NAME.lower(), '%s-%03d.png' % (NAME.lower(), k))
            sh = None
            if os.path.exists(shp):
                sh = np.array(Image.open(shp).convert('RGBA'))[..., 3] > 0
                nsh += 1
            inmod(ts, sh, DX, DY).save(os.path.join(mdst, 'ts%s-%04d.png' % (NAME.lower(), k)))
        ea_frames(ref, os.path.join(DST, dst, 'reference-hd', ref, 'frames'))
        print(key, dst, NAME, n, 'frames', 'sprite %dx%d' % (w, h), 'DX %.2f DY %.2f' % (DX, DY), 'shadows', nsh)


if __name__ == '__main__':
    main(sys.argv[1:])
