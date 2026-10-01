"""Tiberian Sun SHP reader: frames as palette-index arrays (0 = transparent) on the full canvas."""
import struct
import numpy as np


def read_shp(path):
    d = open(path, 'rb').read()
    z, W, H, n = struct.unpack_from('<4H', d, 0)
    frames = []
    for i in range(n):
        o = 8 + 24 * i
        x, y, w, h, comp = struct.unpack_from('<4HB', d, o)
        off = struct.unpack_from('<I', d, o + 20)[0]
        img = np.zeros((H, W), np.uint8)
        if w and h and off:
            if comp & 2:                       # RLE-zero, per line: u16 length incl. itself
                p = off
                for r in range(h):
                    ln = struct.unpack_from('<H', d, p)[0]
                    q, end, c = p + 2, p + ln, 0
                    row = np.zeros(w, np.uint8)
                    while q < end and c < w:
                        v = d[q]; q += 1
                        if v == 0:
                            c += d[q]; q += 1
                        else:
                            row[c] = v; c += 1
                    img[y + r, x:x + w] = row
                    p = end
            else:
                img[y:y + h, x:x + w] = np.frombuffer(d, np.uint8, w * h, off).reshape(h, w)
        frames.append(img)
    return (W, H), frames
