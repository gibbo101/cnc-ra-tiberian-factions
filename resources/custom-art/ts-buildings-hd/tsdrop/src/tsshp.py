"""Tiberian Sun SHP reader (TS / RA2 format) and a hand-off style dump.

    frames = read_shp(path)           list of (w x h) uint8 index arrays on the SHP's full canvas (0 = transparent)
    pal = read_pal(path)              256 x 3 float RGB (0..255)
    rgba(idx, pal, house=None)        RGBA image; house = an RGB that replaces the remap ramp (indices 16-31) by its
                                      brightness, as the hand-off folders draw it (green = house colour)
    python3 tsshp.py <out_dir> <pal> <shp> [<shp> ...]   -> out_dir/<NAME>/frames/NN.png, frames-4x/, sheet.png,
                                                           house/NN.png (white = remap pixels)
Header: u16 0, u16 width, u16 height, u16 count; per frame 24 bytes: u16 x, y, w, h, u32 flags (1 raw, 2 scanlines
with u16 lengths, 3 the same with 0-runs: 0x00 n = n transparent), u32 colour, u32 reserved, u32 offset."""
import os, struct, sys
import numpy as np

REMAP = np.arange(16, 32)


def read_pal(path):
    p = np.frombuffer(open(path, 'rb').read()[:768], np.uint8).reshape(256, 3).astype(np.float64)
    if p.max() <= 63:
        p = p * 255.0 / 63.0
    return p


def read_shp(path):
    d = open(path, 'rb').read()
    zero, W, H, n = struct.unpack_from('<4H', d, 0)
    assert zero == 0, path
    out = []
    for k in range(n):
        x, y, w, h, flags, col, res, off = struct.unpack_from('<4HIIII', d, 8 + 24 * k)
        img = np.zeros((H, W), np.uint8)
        if w == 0 or h == 0 or off == 0:
            out.append(img)
            continue
        comp = flags & 0xff
        if comp in (0, 1):
            fr = np.frombuffer(d, np.uint8, w * h, off).reshape(h, w)
        else:
            fr = np.zeros((h, w), np.uint8)
            p = off
            for r in range(h):
                ln = struct.unpack_from('<H', d, p)[0]
                row = d[p + 2:p + ln]
                p += ln
                if comp == 2:
                    fr[r, :len(row)] = np.frombuffer(row, np.uint8)[:w]
                else:
                    c, i = 0, 0
                    while i < len(row) and c < w:
                        b = row[i]
                        if b == 0:
                            c += row[i + 1]
                            i += 2
                        else:
                            fr[r, c] = b
                            c += 1
                            i += 1
        img[y:y + h, x:x + w] = fr
        out.append(img)
    return out


def rgba(idx, pal, house=None):
    rgb = pal[idx].copy()
    if house is not None:
        rm = (idx >= 16) & (idx < 32)
        lv = pal[idx][..., 0] / 252.0                      # the ramp's brightness (252 .. 32 red)
        rgb = np.where(rm[..., None], np.asarray(house, np.float64) * lv[..., None], rgb)
    a = np.where(idx > 0, 255, 0)
    return np.concatenate([rgb, a[..., None]], -1).round().clip(0, 255).astype(np.uint8)


def dump(out_dir, pal_path, shp_paths, house=(0, 214, 0)):
    from PIL import Image, ImageDraw
    pal = read_pal(pal_path)
    for sp in shp_paths:
        name = os.path.splitext(os.path.basename(sp))[0].upper()
        fr = read_shp(sp)
        base = f'{out_dir}/{name}'
        for sub in ('frames', 'frames-4x', 'house', 'index'):
            os.makedirs(f'{base}/{sub}', exist_ok=True)
        tiles = []
        for k, idx in enumerate(fr):
            im = Image.fromarray(rgba(idx, pal, house), 'RGBA')
            im.save(f'{base}/frames/{k:02d}.png')
            im.resize((im.width * 4, im.height * 4), Image.NEAREST).save(f'{base}/frames-4x/{k:02d}.png')
            Image.fromarray((((idx >= 16) & (idx < 32)) * 255).astype(np.uint8), 'L').save(f'{base}/house/{k:02d}.png')
            np.save(f'{base}/index/{k:02d}.npy', idx)
            tiles.append(im)
        W, H = tiles[0].size
        cols = 8
        rows = (len(tiles) + cols - 1) // cols
        sh = Image.new('RGBA', (cols * W, rows * (H + 14)), (40, 44, 40, 255))
        dr = ImageDraw.Draw(sh)
        for k, im in enumerate(tiles):
            cx, cy = (k % cols) * W, (k // cols) * (H + 14)
            sh.alpha_composite(im, (cx, cy + 14))
            dr.text((cx + 2, cy + 1), str(k), fill=(255, 230, 120, 255))
        sh.save(f'{base}/sheet.png')
        nz = [k for k, idx in enumerate(fr) if (idx > 0).any()]
        print(name, len(fr), 'frames', W, 'x', H, 'non-empty:', nz)


if __name__ == '__main__':
    dump(sys.argv[1], sys.argv[2], sys.argv[3:])
