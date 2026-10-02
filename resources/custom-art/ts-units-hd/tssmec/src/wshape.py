"""shape check for the Wolverine: TS's frames beside the model drawn flat in TS's own camera (the silhouette overlap
per frame), and the shaded HD frames beside TS's sprite and the in-mod frames.

    python3 wshape.py model.json outdir [hd_frames_dir]
"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw
import rc
import wolf as WF, wolfhd as WH
from wpal import load

BG = (96, 108, 72)
FLAT = {WF.TORSO: (196, 152, 64), WF.WAIST: (150, 116, 50), WF.HEAD: (226, 182, 92), WF.NECK: (70, 66, 40),
        WF.PACK: (0, 190, 0), WF.SHOULDER: (0, 210, 0), WF.ARM: (180, 140, 60), WF.GUN: (56, 58, 66),
        WF.MUZZLE: (190, 190, 196), WF.ANT: (16, 16, 16), WF.ANTBASE: (60, 60, 64), WF.LAMP: (255, 120, 0),
        WF.PELVIS: (70, 66, 40), WF.HIPJ: (120, 120, 126), WF.THIGH: (214, 166, 70), WF.KNEE: (170, 170, 176),
        WF.SHIN: (200, 154, 64), WF.ANKLE: (150, 150, 156), WF.FOOT: (226, 178, 84),
        WH.BARREL: (150, 152, 160), WH.MRING: (210, 210, 216), WH.LAMPC: (255, 120, 0), WH.WINDOW: (14, 16, 20),
        WH.TOE: (226, 178, 84), WH.DRUM: (70, 72, 82), WH.BELT: (196, 160, 70), WH.HANDLE: (90, 90, 96)}
WIN = (28, 12, 68, 56)
from paths import HANDOFF
INMOD = HANDOFF + '/02-TSSMEC/in-mod/tssmec/frames/tssmec-%04d.png'


def label(im, text, xy=(4, 2), col=(230, 220, 160)):
    ImageDraw.Draw(im).text(xy, text, fill=col)
    return im


def ts_rgba(f):
    return Image.fromarray(load(f).astype(np.uint8), 'RGBA')


def flat(parts, ax, y0, win=WIN, ss=4):
    cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
    x0, yw, x1, y1 = win
    t, who, nrm, O = rc.render_ids(parts, cam, x0, yw, x1 - x0, y1 - yw, ss=ss, zstart=200.0)
    img = np.zeros(who.shape + (4,), np.float32)
    for i, p in enumerate(parts):
        img[who == i, :3] = FLAT.get(p.comp, (255, 0, 255)); img[who == i, 3] = 255
    h, w = y1 - yw, x1 - x0
    im = img.reshape(h, ss, w, ss, 4).mean(axis=(1, 3))
    return Image.fromarray(im.round().astype(np.uint8), 'RGBA'), (who >= 0).reshape(h, ss, w, ss).mean(axis=(1, 3)) >= 0.5


def iou(a, b):
    return (a & b).sum() / max((a | b).sum(), 1)


def pair_tile(ts, model, z, text):
    W, H = ts.size
    row = Image.new('RGBA', (W * 2 * z + 6, H * z + 16), (28, 30, 34, 255))
    for i, im in enumerate((ts, model)):
        b = Image.new('RGBA', im.size, BG + (255,)); b.alpha_composite(im)
        row.paste(b.resize((W * z, H * z), Image.NEAREST), (i * (W * z + 6), 16))
    return label(row, text)


def grid(tiles, cols, name, bg=(28, 30, 34)):
    W = max(t.size[0] for t in tiles); H = max(t.size[1] for t in tiles)
    out = Image.new('RGB', (cols * (W + 8) + 8, ((len(tiles) + cols - 1) // cols) * (H + 8) + 8), bg)
    for i, t in enumerate(tiles):
        out.paste(t.convert('RGB'), (8 + (i % cols) * (W + 8), 8 + (i // cols) * (H + 8)))
    out.save(name)
    return out


def sheet(model, ts_frame_of, pose_of, name, title, z=5, detail=False):
    """per mod facing f (0-7): TS's frame ts_frame_of(k8) beside the model (pose_of(k8)) flat in TS's camera."""
    tiles, scores = [], []
    for f in range(8):
        k8 = WH.mod_to_cw(f)
        M = WF.facing_matrix(k8)
        pose = pose_of(k8)
        base = WH.body(model, pose) if detail else WF.body_parts(model['P'], pose)
        parts = [p.moved(M) for p in base]
        fl, mm = flat(parts, model['ax'], model['y0'])
        ts = ts_rgba(ts_frame_of(k8)).crop(WIN)
        sc = iou(mm, np.array(ts)[..., 3] > 0); scores.append(sc)
        tiles.append(pair_tile(ts, fl, z, '%s, mod facing %d (TS %d)   overlap %.2f' % (title, f, ts_frame_of(k8), sc)))
    grid(tiles, 4, name)
    return scores


def ts_scaled(f):
    """TS's frame scaled x6.4 (nearest) onto the 384 canvas where the mod has it."""
    im = ts_rgba(f)
    big = Image.new('RGBA', (384, 384), (0, 0, 0, 0))
    sc = im.resize((round(95 * 6.4), round(95 * 6.4)), Image.NEAREST)
    big.alpha_composite(sc, (round(192 - 47.5 * 6.4), round(307 - 53 * 6.4)))
    return big


def hd_sheet(hd_fmt, frames_mod, ts_frames, name, crop=(70, 40, 330, 330), scale=0.62, labels=None):
    tiles = []
    for i, (fm, ft) in enumerate(zip(frames_mod, ts_frames)):
        cols = [('TS %d' % ft, ts_scaled(ft)), ('in-mod %d' % fm, Image.open(INMOD % fm).convert('RGBA')),
                ('HD %d' % fm, Image.open(hd_fmt % fm).convert('RGBA'))]
        W, H = crop[2] - crop[0], crop[3] - crop[1]
        t = Image.new('RGB', (3 * W + 12, H + 18), (28, 30, 34))
        for j, (lab, im) in enumerate(cols):
            b = Image.new('RGBA', im.size, BG + (255,)); b.alpha_composite(im)
            t.paste(b.crop(crop).convert('RGB'), (j * (W + 6), 18))
            label(t, lab if not (labels and j == 0) else labels[i] + '   ' + lab, (j * (W + 6) + 4, 3))
        t = t.resize((int(t.size[0] * scale), int(t.size[1] * scale)), Image.LANCZOS)
        tiles.append(t)
    return grid(tiles, 2, name)


if __name__ == '__main__':
    model = WH.load(sys.argv[1]); out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    s0 = sheet(model, lambda k8: k8 * 12, lambda k8: WH.walk_pose(model, 0), out + '/shape-walk-step0.png',
               'walk step 0', detail=True)
    s1 = sheet(model, lambda k8: 96 + k8, lambda k8: model['stand'], out + '/shape-standing-to-fire.png', 'fire stance',
               detail=True)
    walk = []
    for s in range(12):
        walk.append(np.mean([iou(flat([p.moved(WF.facing_matrix(k)) for p in WF.body_parts(model['P'], WH.walk_pose(model, s))],
                                      model['ax'], model['y0'])[1], np.array(ts_rgba(k * 12 + s).crop(WIN))[..., 3] > 0)
                             for k in range(8)]))
    print('overlap walk step 0 per facing', np.round(s0, 3), 'mean %.3f' % np.mean(s0))
    print('overlap fire stance per facing', np.round(s1, 3), 'mean %.3f' % np.mean(s1))
    print('overlap per walk step (mean of 8 facings)', np.round(walk, 3), 'mean %.3f' % np.mean(walk))
    json.dump(dict(walk0=s0, stance=s1, walk=walk), open(out + '/overlaps.json', 'w'), default=float)
    if len(sys.argv) > 3:
        hd = sys.argv[3] + '/tssmec-%04d.png'
        hd_sheet(hd, [f * 12 for f in range(8)], [WH.mod_to_cw(f) * 12 for f in range(8)], out + '/hd-standing-8.png')
