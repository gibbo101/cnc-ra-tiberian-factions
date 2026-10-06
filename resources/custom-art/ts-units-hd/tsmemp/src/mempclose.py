"""
mempclose.py - close-ups of the Mobile EMP Cannon's frames: the frame's own camera, look and materials (memprender.py)
at Z times the scale, cropped round the part asked for, for checking detail against TS and the references.

    python3 mempclose.py out.png k[,k..] [zoom] [ss] [crop x0,y0,x1,y1 in the frame's canvas px | box]
(crop 'box': a window round the grey box's front, its cockpit slot)
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import rc, rcrender as RR
import mempmodel as T, mempmat as MM, memprender as SR
from mempcam import CANVAS, PPU, ORIGIN, ELEV, unit_to_world

FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
BG = (110, 106, 84)


def close(k, Z=3, ss=2, crop=None):
    Mx = unit_to_world(k)
    parts, frames, owner = T.posed(SR.model(), ('hull',), Mx)
    cam = RR.Cam((0, -1), ELEV, PPU * Z, (ORIGIN[0] * Z, ORIGIN[1] * Z))
    W, H = CANVAS[0] * Z, CANVAS[1] * Z
    if crop is None:
        crop = (60, 60, 324, 300)
    win = tuple(int(c * Z) for c in crop)
    r = RR.RCRender(parts, cam, (W, H), win, SR.BOUNDS, ss=ss, frames=frames, shadow_len=SR.SHADOW_LEN,
                    px_scale=SR.PX_SCALE * Z)
    r.sec = np.where(r.hitmask, 'hull', '')
    r.pose_R = Mx
    SR.round_edges(r)
    occ = r.sky_occlusion()
    alb, (bx, by, bz), emit = MM.materials(r, occ=occ)
    ao = 0.84 + 0.16 * np.clip(r.z / 9.0, 0, 1)
    col = r.shade(alb, sky_occ=occ, ao=ao) + emit
    col = col * np.clip(1 + 0.3 * bz, 0.55, 1.35)[..., None]
    col = col + SR.spec_hl(r, MM.GLOSSY)
    g = r.ground_alpha_full(shadow_parts=parts)
    img = r.compose(col, ground=g)
    out = Image.new('RGBA', img.size, BG + (255,))
    out.alpha_composite(img)
    return out.crop(win).convert('RGB')


def box_crop(k, w=88, h=66, q=(28.0, 19.8, 10.0)):
    """a w x h window of frame k's canvas round the grey box's front (q, TS's voxel coordinates)."""
    R, t = T.pose('hull')
    p = unit_to_world(k) @ (R @ (T.FH.mn + np.array(q) * T.FH.sc) + t)
    sx, sy = RR.Cam((0, -1), ELEV, PPU, ORIGIN).project(p)
    cx, cy = float(sx), float(sy)
    return (int(cx - w / 2), int(cy - h * 0.55), int(cx + w / 2), int(cy + h * 0.45))


def slot_closeups(ks, out, Z=4, ss=2):
    """the grey box's cockpit slot close up (Z times the scale) in the facings ks."""
    return grid([close(k, Z, ss, box_crop(k)) for k in ks], ['frame %d' % k for k in ks], out, 2)


def grid(tiles, labels, out, cols=2):
    w, h = tiles[0].size
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
    crops = [box_crop(k) if crop == 'box' else (tuple(int(a) for a in crop.split(',')) if crop else None) for k in ks]
    print(grid([close(k, Z, ss, c) for k, c in zip(ks, crops)], ['frame %d' % k for k in ks], out,
               2 if len(ks) > 1 else 1))
