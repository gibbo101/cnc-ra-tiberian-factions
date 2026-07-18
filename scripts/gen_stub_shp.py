#!/usr/bin/env python3
"""Generate a classic TD/RA-format SHP whose frames are fully transparent.

Purpose: HD-only entities get their on-screen size (and health-bar/selection
box) from the classic ImageData frame dimensions. When no real classic art
exists, a transparent stub with the right dimensions is the honest way to
declare "this unit is WxH classic pixels" (e.g. TSHVR 64x64 = bigger than a
48x48 tank). Classic mode never renders in this mod, so pixels don't matter —
only the header dims. Frames are valid LCW so nothing crashes if decompressed.

Usage: gen_stub_shp.py <out.shp> <width> <height> <frames>
"""
import struct, sys


def lcw_transparent(n):
    """LCW stream that fills n zero bytes then ends."""
    out = b""
    while n > 0:
        chunk = min(n, 0xFFFF)
        out += bytes([0xFE]) + struct.pack("<H", chunk) + b"\x00"
        n -= chunk
    return out + b"\x80"


def main():
    out_path, w, h, count = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    frame = lcw_transparent(w * h)
    header = struct.pack("<7H", count, 0, 0, w, h, w * h + 512, 0)
    table_size = (count + 2) * 8
    data_start = len(header) + table_size
    table = b""
    offsets = []
    pos = data_start
    for i in range(count):
        offsets.append(pos)
        pos += len(frame)
    for off in offsets:
        table += struct.pack("<I", (off & 0xFFFFFF) | (0x80 << 24))  # offset + LCW format
        table += struct.pack("<I", 0)                                # no ref frame
    # terminator entry (points at end of data) + null entry — (count+2) entries total
    table += struct.pack("<I", pos & 0xFFFFFF) + struct.pack("<I", 0)
    table += struct.pack("<II", 0, 0)
    with open(out_path, "wb") as f:
        f.write(header + table + frame * count)
    print(f"stub SHP: {out_path} {w}x{h} x{count} frames ({len(header) + len(table) + len(frame)*count} bytes)")


main()
