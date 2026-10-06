"""
orcaclose.py - close-ups of the Orca Fighter's frames: the frame's own camera, look and materials (orcarender.py) at
Z times the scale, cropped round the part asked for, for checking detail against TS and the references.

    python3 orcaclose.py out.png k[,k..] [zoom] [ss] [crop x0,y0,x1,y1 in the frame's canvas px | nose | pods]
(crop 'nose': a window round the nose and the canopy; 'pods': round the pods' fronts and the fans)
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import rc, rcrender as RR
import orcamodel as T, orcamat as MM, orcarender as SR
from orcacam import CANVAS, PPU, ORIGIN, ELEV, PX_SCALE, unit_to_world

FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
BG = (118, 124, 112)


def close(k, Z=3, ss=2, crop=None, m=None):
    Mx = unit_to_world(k)
    parts, frames, owner = T.posed(m if m is not None else SR.model(), ('hull',), Mx)
    cam = RR.Cam((0, -1), ELEV, PPU * Z, (ORIGIN[0] * Z, ORIGIN[1] * Z))
    W, H = CANVAS[0] * Z, CANVAS[1] * Z
    if crop is None:
        crop = (20, 30, 364, 290)
    win = tuple(int(c * Z) for c in crop)
    r = RR.RCRender(parts, cam, (W, H), win, SR.BOUNDS, ss=ss, frames=frames, shadow_len=1.0, px_scale=PX_SCALE * Z)
    r.sec = np.where(r.hitmask, 'hull', '')
    r.pose_R = Mx
    r.gnx, r.gny, r.gnz = r.nx.copy(), r.ny.copy(), r.nz.copy()
    SR.round_edges(r)
    SR.ring_normals(r)
    occ = r.sky_occlusion()
    alb, (bx, by, bz), emit = MM.materials(r, occ=occ)
    col = r.shade(alb, sky_occ=occ, ao=None) + emit
    col = col * np.clip(1 + 0.3 * bz, 0.55, 1.35)[..., None]
    col = col + SR.spec_hl(r, MM.GLOSSY)
    img = r.compose(col, ground=None)
    out = Image.new('RGBA', img.size, BG + (255,))
    out.alpha_composite(img)
    return out.crop(win).convert('RGB')


def q_crop(k, q, w, h):
    """a w x h window of frame k's canvas round the point q (TS's voxel coordinates)."""
    R, t = T.FH.pose()
    p = unit_to_world(k) @ (R @ (T.FH.mn + np.array(q) * T.FH.sc) + t)
    sx, sy = RR.Cam((0, -1), ELEV, PPU, ORIGIN).project(p)
    cx, cy = float(sx), float(sy)
    return (int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))


def nose_crop(k):
    return q_crop(k, (35.5, 12.5, 4.5), 96, 76)


def pods_crop(k):
    return q_crop(k, (28.0, 12.5, 5.5), 150, 110)


def grid(tiles, labels, out, cols=2):
    w = max(t.size[0] for t in tiles); h = max(t.size[1] for t in tiles)
    rows = (len(tiles) + cols - 1) // cols
    S = Image.new('RGB', (cols * (w + 6) - 6, rows * (h + 6) - 6), (30, 30, 30))
    d = ImageDraw.Draw(S)
    for i, (t, lab) in enumerate(zip(tiles, labels)):
        S.paste(t, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
        d.text(((i % cols) * (w + 6) + 6, (i // cols) * (h + 6) + 4), lab, font=FONT, fill=(240, 230, 180))
    S.save(out)
    return S.size


if __name__ == '__main__':
    out = sys.argv[1]
    ks = [int(a) for a in sys.argv[2].split(',')]
    Z = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    ss = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    crop = sys.argv[5] if len(sys.argv) > 5 else None
    pick = {'nose': nose_crop, 'pods': pods_crop}
    crops = [pick[crop](k) if crop in pick else (tuple(int(a) for a in crop.split(',')) if crop else None) for k in ks]
    print(grid([close(k, Z, ss, c) for k, c in zip(ks, crops)], ['frame %d' % k for k in ks], out,
               2 if len(ks) > 1 else 1))
