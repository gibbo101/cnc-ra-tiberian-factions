#!/usr/bin/env python3
"""Pad MT_COMMANDBAR_COMMON.TGA to NW x NH, stock art kept at its top-left coords.
usage: atlas_grow_probe.py <src 6871x6716 atlas> <dst>
New space = magenta/black 64px checker so any mis-sampled UV is obvious."""
import numpy as np, sys
SRC = sys.argv[1]; DST = sys.argv[2]; NW = NH = 8192
d = open(SRC, 'rb').read()
hdr = bytearray(d[:18])
W = hdr[12] | hdr[13] << 8; H = hdr[14] | hdr[15] << 8
assert (W, H) == (6871, 6716) and hdr[16] == 32 and hdr[17] == 0x00, (W, H, hdr[16], hdr[17])
img = np.frombuffer(d, np.uint8, W * H * 4, 18).reshape(H, W, 4)[::-1]   # top-left rows, BGRA
yy, xx = np.mgrid[0:NH, 0:NW]
chk = ((yy // 64 + xx // 64) & 1).astype(bool)
canvas = np.zeros((NH, NW, 4), np.uint8)
canvas[..., 3] = 255
canvas[chk] = (255, 0, 255, 255)                                         # B,G,R,A magenta
canvas[:H, :W] = img
hdr[12:14] = NW.to_bytes(2, 'little'); hdr[14:16] = NH.to_bytes(2, 'little')
open(DST, 'wb').write(bytes(hdr) + canvas[::-1].tobytes())
print('wrote', DST, NW, NH)
