"""
hvrclose.py - close-ups of the Hover MLRS's frames: the frame's own camera, look and materials (hvrrender.py) at Z times
the scale, cropped round the unit, for checking detail against TS and the references.

    python3 hvrclose.py out.png k[,k..] [zoom] [ss] [crop x0,y0,x1,y1 in the frame's canvas px]
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import rcrender as RR
import hvrmodel as T, hvrmat as MM, hvrrender as HR
from hvrcam import CANVAS, ORIGIN, PPU, ELEV, PX_SCALE, unit_to_world, frame_of

FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
BG = (110, 106, 84)


def close(k, Z=4, ss=2, crop=None, m=None, win=None):
    m = m if m is not None else HR.model()
    which, facing, kind = frame_of(k)
    origin = ORIGIN
    Mx = unit_to_world(facing)
    parts, frames, owner = T.posed(m, which, Mx, {'rack': T.FRAME_SHIFT} if kind == 'rack' else None)
    cam = RR.Cam((0, -1), ELEV, PPU * Z, (origin[0] * Z, origin[1] * Z))
    if crop is None:
        crop = (26, 30, 166, 160)
    win = win if win is not None else tuple(int(c * Z) for c in crop)
    r = RR.RCRender(parts, cam, (CANVAS[0] * Z, CANVAS[1] * Z), win, HR.BOUNDS, ss=ss, frames=frames, shadow_len=1.0,
                    px_scale=PX_SCALE * Z)
    r.sec = np.where(r.hitmask, owner[np.clip(r.who, 0, len(owner) - 1)], '')
    r.pose_R = Mx
    HR.round_edges(r)
    occ = r.sky_occlusion()
    if kind == 'rack':
        r.shadow = lambda: np.zeros_like(r.nz)
        occ = np.where(np.isin(r.comp, (T.TURNTABLE, T.MOUNT)), occ * 0.3, occ)
    alb, (bx, by, bz), emit = MM.materials(r, occ=occ)
    ao = 0.84 + 0.16 * np.clip((r.z + 1.0) / 10.0, 0, 1)
    col = r.shade(alb, sky_occ=occ, ao=ao) + emit
    col = col * np.clip(1 + 0.3 * bz, 0.55, 1.35)[..., None]
    col = col + HR.spec_hl(r, MM.GLOSSY)
    img = r.compose(col, ground=None)
    out = Image.new('RGBA', img.size, BG + (255,))
    out.alpha_composite(img)
    return out.crop(win).convert('RGB')


if __name__ == '__main__':
    out = sys.argv[1]
    ks = [int(a) for a in sys.argv[2].split(',')]
    Z = int(sys.argv[3]) if len(sys.argv) > 3 else 4
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
