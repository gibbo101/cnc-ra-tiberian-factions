"""shape check for the Titan: TS's frames beside the model drawn flat in TS's camera (silhouette overlap per
frame), and the shaded HD frames (legs + upper body laid over each other) beside the in-mod frames."""
import json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import rc, legfit as LF, torso2 as T2, titan as TN, torso2fit as T2F
from tspal import load

FONT = None
BG = (96, 108, 72)


def label(im, text, xy=(4, 3), col=(255, 255, 0)):
    ImageDraw.Draw(im).text(xy, text, fill=col)
    return im


def ts_rgba(f):
    a = load(f).astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def flat_legs(S, pose, k8, ax=47.4, y0=55.0, ss=4, win=(22, 18, 74, 62)):
    """the legs drawn flat (class colours) in TS's camera at TS's size: gold legs, dark hip, grey knees."""
    cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
    M = LF.facing_matrix(k8)
    parts = [p.moved(M) for p in LF.body_parts(S, pose[:6], pose[6])]
    x0, yw, x1, y1 = win
    t, who, nrm, O = rc.render_ids(parts, cam, x0, yw, x1 - x0, y1 - yw, ss=ss, zstart=200.0)
    cols = {LF.HIP: (64, 64, 70), LF.THIGH: (200, 152, 64), LF.SHIN: (200, 152, 64), LF.FOOT: (184, 140, 58),
            LF.KNEE: (160, 160, 166)}
    img = np.zeros(who.shape + (4,), np.float32)
    for i, p in enumerate(parts):
        img[who == i, :3] = cols[p.comp]; img[who == i, 3] = 255
    h, w = y1 - yw, x1 - x0
    img = img.reshape(h, ss, w, ss, 4).mean(axis=(1, 3))
    return Image.fromarray(img.round().astype(np.uint8), 'RGBA'), (who >= 0).reshape(h, ss, w, ss).mean(axis=(1, 3)) >= 0.5


def iou(a, b):
    return (a & b).sum() / max((a | b).sum(), 1)


def sheet_legs(S, poses, step=0, z=4, name='shape_legs.png'):
    tiles = []
    win = (22, 18, 74, 62)
    for f8 in range(8):
        k8 = TN.mod_to_cw(f8, 8)
        ts = ts_rgba(k8 * 15 + step).crop(win)
        fl, mm = flat_legs(S, poses[step], k8, win=win)
        tm = np.array(ts)[..., 3] > 0
        sc = iou(mm, tm)
        row = Image.new('RGBA', (ts.size[0] * 2 * z + 6, ts.size[1] * z + 14), BG + (255,))
        a = Image.new('RGBA', ts.size, BG + (255,)); a.alpha_composite(ts)
        b = Image.new('RGBA', fl.size, BG + (255,)); b.alpha_composite(fl)
        row.paste(a.resize((ts.size[0] * z, ts.size[1] * z), Image.NEAREST), (0, 14))
        row.paste(b.resize((fl.size[0] * z, fl.size[1] * z), Image.NEAREST), (ts.size[0] * z + 6, 14))
        label(row, 'mod %d (TS CW%d)   overlap %.2f' % (f8 * 12, k8, sc))
        tiles.append(row)
    return grid(tiles, 4, name)


def grid(tiles, cols, name, bg=(28, 30, 34)):
    W = max(t.size[0] for t in tiles); H = max(t.size[1] for t in tiles)
    out = Image.new('RGB', (cols * (W + 8) + 8, ((len(tiles) + cols - 1) // cols) * (H + 8) + 8), bg)
    for i, t in enumerate(tiles):
        out.paste(t.convert('RGB'), (8 + (i % cols) * (W + 8), 8 + (i // cols) * (H + 8)))
    out.save(name)
    return out


FLAT_T = {T2.BODY: (214, 170, 80), T2.BAND: (0, 190, 0), T2.POD: (0, 190, 0), T2.BOX: (0, 190, 0), T2.ANT: (20, 20, 20),
          T2.MOUNT: (70, 70, 74), T2.HATCH: (226, 182, 92)}


def flat_render(parts, cols, cam, win, ss=4):
    x0, yw, x1, y1 = win
    t, who, nrm, O = rc.render_ids(parts, cam, x0, yw, x1 - x0, y1 - yw, ss=ss, zstart=200.0)
    img = np.zeros(who.shape + (4,), np.float32)
    for i, p in enumerate(parts):
        img[who == i, :3] = cols.get(p.comp, (255, 0, 255)); img[who == i, 3] = 255
    h, w = y1 - yw, x1 - x0
    im = img.reshape(h, ss, w, ss, 4).mean(axis=(1, 3))
    return Image.fromarray(im.round().astype(np.uint8), 'RGBA'), (who >= 0).reshape(h, ss, w, ss).mean(axis=(1, 3)) >= 0.5


def pair_tile(ts, model, z, text):
    W, H = ts.size
    row = Image.new('RGBA', (W * 2 * z + 6, H * z + 16), (28, 30, 34, 255))
    for i, im in enumerate((ts, model)):
        b = Image.new('RGBA', im.size, BG + (255,)); b.alpha_composite(im)
        row.paste(b.resize((W * z, H * z), Image.NEAREST), (i * (W * z + 6), 16))
    label(row, text, (4, 2), (230, 220, 160))
    return row


def torso_sheet(P, ax=48.0, y0=55.0, z=4, name='shape_torso.png'):
    cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
    win = (28, 0, 70, 42)
    tiles, scores = [], []
    for f32 in range(0, 32, 4):
        k32 = TN.mod_to_cw(f32, 32)
        M = TN.facing_cw(k32, 32)
        parts = [p.moved(M) for p in T2.parts(P)]
        fl, mm = flat_render(parts, FLAT_T, cam, win)
        ts = ts_rgba(120 + k32).crop(win)
        sc = iou(mm, np.array(ts)[..., 3] > 0); scores.append(sc)
        tiles.append(pair_tile(ts, fl, z, 'upper body, mod %d   overlap %.2f' % (96 + f32, sc)))
    return grid(tiles, 4, name), scores


def legs_sheet(S, pose_of, step=0, z=4, name='shape_legs.png', ax=47.4, y0=55.0):
    cam = rc.Cam((0, -1), 30.0, 1.0, (ax, y0))
    win = (22, 18, 74, 62)
    cols = {LF.HIP: (64, 66, 76), LF.THIGH: (84, 78, 54), LF.SHIN: (214, 164, 70), LF.FOOT: (200, 152, 64),
            LF.KNEE: (160, 160, 166)}
    tiles, scores = [], []
    pose = pose_of(step)
    for f8 in range(8):
        k8 = TN.mod_to_cw(f8, 8)
        M = LF.facing_matrix(k8)
        parts = [p.moved(M) for p in LF.body_parts(S, pose[:6], pose[6])]
        fl, mm = flat_render(parts, cols, cam, win)
        ts = ts_rgba(k8 * 15 + step).crop(win)
        sc = iou(mm, np.array(ts)[..., 3] > 0); scores.append(sc)
        tiles.append(pair_tile(ts, fl, z, 'legs, mod %d   overlap %.2f' % (f8 * 12, sc)))
    return grid(tiles, 4, name), scores
