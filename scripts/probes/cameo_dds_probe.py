"""Write sidebar cameos as DXT1 DDS with mips, the size the launcher accepts for compressed art.

usage: cameo_dds_probe.py <out dir> <BuildIcon .tga> [...]
The 341x256 cameo is resized to 344x256 (block-aligned); each <name>.DDS lands in <out dir>, with
a side-by-side <name>_compare.png of the original and the decoded DDS at full and sidebar size.
"""
import os
import struct
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import dds_dxt5  # noqa: E402

SIZE = (344, 256)


def dxt1_level(rgb):
    """DXT1 blocks: the DXT5 encoder's colour block without its alpha half."""
    return np.frombuffer(dds_dxt5.encode_level(rgb), np.uint8).reshape(-1, 16)[:, 8:].tobytes()


def levels(img):
    out, cur = [], img
    while True:
        out.append(cur)
        if cur.size == (1, 1):
            return out
        cur = cur.resize((max(1, cur.width // 2), max(1, cur.height // 2)), Image.BOX)


def header(w, h, mips, top_bytes):
    flags = 0x1 | 0x2 | 0x4 | 0x1000 | 0x20000 | 0x80000  # CAPS HEIGHT WIDTH PIXELFORMAT MIPMAPCOUNT LINEARSIZE
    pf = struct.pack("<II4s5I", 32, 0x4, b"DXT1", 0, 0, 0, 0, 0)
    caps = 0x1000 | 0x8 | 0x400000  # TEXTURE COMPLEX MIPMAP
    return (b"DDS " + struct.pack("<7I", 124, flags, h, w, top_bytes, 0, mips) + b"\0" * 44 + pf
            + struct.pack("<4I", caps, 0, 0, 0) + b"\0" * 4)


def decode_dxt1(data, w, h):
    """The top level back to RGB, for the comparison sheet."""
    bw, bh = -(-w // 4), -(-h // 4)
    blocks = np.frombuffer(data[:bw * bh * 8], np.uint8).reshape(-1, 8)
    q0 = blocks[:, 0].astype(int) | (blocks[:, 1].astype(int) << 8)
    q1 = blocks[:, 2].astype(int) | (blocks[:, 3].astype(int) << 8)
    e0, e1 = dds_dxt5._from565(q0), dds_dxt5._from565(q1)
    pal = np.stack([e0, e1, (2 * e0 + e1) / 3, (e0 + 2 * e1) / 3], 1)
    bits = blocks[:, 4:8].copy().view("<u4")[:, 0]
    idx = (bits[:, None] >> (2 * np.arange(16))) & 3
    px = np.take_along_axis(pal, idx[:, :, None].repeat(3, 2), 1)
    img = px.reshape(bh, bw, 4, 4, 3).transpose(0, 2, 1, 3, 4).reshape(bh * 4, bw * 4, 3)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)[:h, :w])


def convert(out_dir, tga):
    src = Image.open(tga).convert("RGB")
    lv = levels(src.resize(SIZE, Image.LANCZOS))
    payload = [dxt1_level(np.asarray(im)) for im in lv]
    name = os.path.splitext(os.path.basename(tga))[0]
    path = os.path.join(out_dir, name + ".DDS")
    with open(path, "wb") as f:
        f.write(header(SIZE[0], SIZE[1], len(lv), len(payload[0])) + b"".join(payload))
    dec = decode_dxt1(payload[0], *SIZE).resize(src.size, Image.LANCZOS)
    small = (src.width * 3 // 8, src.height * 3 // 8)
    sheet = Image.new("RGB", (src.width * 2 + small[0] * 2 + 30, src.height), "black")
    sheet.paste(src, (0, 0))
    sheet.paste(dec, (src.width + 10, 0))
    sheet.paste(src.resize(small, Image.LANCZOS), (src.width * 2 + 20, 0))
    sheet.paste(dec.resize(small, Image.LANCZOS), (src.width * 2 + small[0] + 30, 0))
    sheet.save(os.path.join(out_dir, name + "_compare.png"))
    print(name, os.path.getsize(tga), "->", os.path.getsize(path))


if __name__ == "__main__":
    os.makedirs(sys.argv[1], exist_ok=True)
    for t in sys.argv[2:]:
        convert(sys.argv[1], t)
