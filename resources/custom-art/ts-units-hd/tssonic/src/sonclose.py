"""
sonclose.py - close-ups of the Disruptor's turret (or hull) frames: the frame's own camera, look and materials
(sonrender.py) at Z times the scale, cropped round the part asked for, for checking detail against TS and the FMV.

    python3 sonclose.py out.png k[,k..] [zoom] [ss] [crop x0,y0,x1,y1 in the frame's canvas px]
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import rc, rcrender as RR
import sonmodel as T, sonmat as MM, sonrender as SR
from soncam import CANVAS, PPU, PPU_T, ORIGIN_T, ELEV, origin, unit_to_world, frame_of

FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
BG = (110, 106, 84)


def close(k, Z=3, ss=2, crop=None):
    which, facing, tur = frame_of(k)
    Mx = unit_to_world(facing)
    parts, frames, owner = T.posed(SR.model(), which, Mx)
    if tur:
        cam = RR.Cam((0, -1), ELEV, PPU_T * Z, (ORIGIN_T[0] * Z, ORIGIN_T[1] * Z))
    else:
        o = origin()
        cam = RR.Cam((0, -1), ELEV, PPU * Z, (o[0] * Z, o[1] * Z))
    W, H = CANVAS[0] * Z, CANVAS[1] * Z
    if crop is None:
        crop = (135, 62, 315, 202) if tur else (60, 60, 390, 320)
    win = tuple(int(c * Z) for c in crop)
    r = RR.RCRender(parts, cam, (W, H), win, SR.BOUNDS, ss=ss, frames=frames, shadow_len=SR.SHADOW_LEN,
                    px_scale=SR.PX_SCALE * Z)
    r.sec = np.where(r.hitmask, owner[np.clip(r.who, 0, len(owner) - 1)], '')
    r.pose_R = Mx
    SR.round_edges(r)
    SR.smooth_rim(r, Mx)
    occ = r.sky_occlusion()
    alb, (bx, by, bz), emit = MM.materials(r, occ=occ)
    ao = 0.84 + 0.16 * np.clip(r.z / 12.0, 0, 1)
    col = r.shade(alb, sky_occ=occ, ao=ao) + emit
    col = col * np.clip(1 + 0.3 * bz, 0.55, 1.35)[..., None]
    col = col + SR.spec_hl(r, MM.GLOSSY)
    g = None if tur else r.ground_alpha_full(shadow_parts=parts)
    img = r.compose(col, ground=g)
    out = Image.new('RGBA', img.size, BG + (255,))
    out.alpha_composite(img)
    return out.crop(win).convert('RGB')


if __name__ == '__main__':
    out = sys.argv[1]
    ks = [int(a) for a in sys.argv[2].split(',')]
    Z = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    ss = int(sys.argv[4]) if len(sys.argv) > 4 else 2
    crop = tuple(int(a) for a in sys.argv[5].split(',')) if len(sys.argv) > 5 else None
    tiles = [close(k, Z, ss, crop) for k in ks]
    w, h = tiles[0].size
    cols = 2 if len(tiles) > 1 else 1
    rows = (len(tiles) + cols - 1) // cols
    S = Image.new('RGB', (cols * (w + 6) - 6, rows * (h + 6) - 6), (30, 30, 30))
    d = ImageDraw.Draw(S)
    for i, t in enumerate(tiles):
        S.paste(t, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
        d.text(((i % cols) * (w + 6) + 6, (i // cols) * (h + 6) + 4), 'frame %d' % ks[i], font=FONT, fill=(240, 230, 180))
    S.save(out)
    print(S.size)
