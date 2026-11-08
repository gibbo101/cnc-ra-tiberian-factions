"""The launcher's .MTD atlas sidecar as {upper-case name without .TGA: (x, y, w, h)} in pixels.
Per region: u32 name length, padded name, int32 x, y, w, h, 0, 0, w, h, then a u8 flag."""
import struct


def read_regions(path):
    data = open(path, 'rb').read()
    _magic, count = struct.unpack_from('<iI', data, 0)
    pos = 8
    regions = {}
    for _ in range(count):
        (length,) = struct.unpack_from('<I', data, pos)
        pos += 4
        name = data[pos:pos + length].rstrip(b'\0').decode('ascii').upper()
        pos += length
        regions[name.removesuffix('.TGA')] = struct.unpack_from('<4i', data, pos)
        pos += 8 * 4 + 1
    if pos != len(data):
        raise ValueError(f'{path}: {len(data) - pos} bytes left after {count} regions')
    return regions
