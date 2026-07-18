#!/usr/bin/env python3
"""Decode Tiberian Sun format SHP files to RGBA PNGs.

TS SHP layout: u16 zero, u16 width, u16 height, u16 count; then count x
24-byte frame headers {x,y,w,h (u16 x4), flags u32, color u32, reserved u32,
offset u32}. flags bit1 = RLE-zero compressed scanlines (u16 line length
prefix, 00 nn = run of nn transparent), else raw w*h bytes. Index 0 =
transparent. Palette = 768-byte 6-bit VGA .PAL.
"""
import struct, sys, os
from PIL import Image


def load_pal(path):
    raw = open(path, 'rb').read()
    pal = [tuple(min(255, b * 255 // 63) for b in raw[i * 3:i * 3 + 3]) for i in range(256)]
    return pal


def decode_shp(path):
    d = open(path, 'rb').read()
    zero, W, H, count = struct.unpack_from('<HHHH', d, 0)
    frames = []
    for f in range(count):
        off = 8 + f * 24
        x, y, w, h = struct.unpack_from('<HHHH', d, off)
        flags, = struct.unpack_from('<I', d, off + 8)
        data_off, = struct.unpack_from('<I', d, off + 20)
        pix = bytearray(w * h)
        if data_off == 0 or w == 0 or h == 0:
            frames.append((x, y, w, h, W, H, bytes(pix)))
            continue
        p = data_off
        if flags & 2:  # RLE-zero scanlines
            for row in range(h):
                line_len, = struct.unpack_from('<H', d, p)
                q = p + 2
                end = p + line_len
                col = 0
                while q < end:
                    b = d[q]; q += 1
                    if b == 0:
                        col += d[q]; q += 1
                    else:
                        pix[row * w + col] = b
                        col += 1
                p = end
        else:
            pix[:] = d[p:p + w * h]
        frames.append((x, y, w, h, W, H, bytes(pix)))
    return (W, H), frames


def frame_to_rgba(frame, pal, remap=None, team=None):
    x, y, w, h, W, H, pix = frame
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if w and h:
        cell = Image.new('RGBA', (w, h))
        px = cell.load()
        for i, c in enumerate(pix):
            if c == 0:
                continue
            r, g, b = pal[c]
            if remap and remap[0] <= c <= remap[1] and team:
                lum = (r + g + b) / 3.0
                peak = max(sum(pal[j]) / 3.0 for j in range(remap[0], remap[1] + 1))
                f = min(1.45 * lum / peak, 1.0)
                r, g, b = [min(255, int(t * f)) for t in team]
            px[i % w, i // w] = (r, g, b, 255)
        img.paste(cell, (x, y))
    return img


if __name__ == '__main__':
    shp, palp, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    remap = (16, 31)
    team = (0, 200, 0)
    pal = load_pal(palp)
    size, frames = decode_shp(shp)
    os.makedirs(outdir, exist_ok=True)
    print(f'{shp}: canvas {size}, {len(frames)} frames')
    for i, fr in enumerate(frames):
        img = frame_to_rgba(fr, pal, remap, team)
        img.save(os.path.join(outdir, f'frame-{i:04d}.png'))
        x, y, w, h = fr[:4]
        print(f'  frame {i}: pos({x},{y}) {w}x{h}')
