"""Tiberian Sun VXL/HVA reader: voxel grids (colour index, normal index) per section, with bounds and scale."""
import struct
import numpy as np


def read_pal(path):
    p = np.frombuffer(open(path, 'rb').read()[:768], np.uint8).reshape(256, 3).astype(np.float64)
    if p.max() <= 63:
        p = p * 255.0 / 63.0
    return p


def read_vxl(path):
    v = open(path, 'rb').read()
    assert v[:16].startswith(b'Voxel Animation'), path
    pal_count, n_head, n_tail, body_size = struct.unpack_from('<IIII', v, 16)
    off = 32 + 2 + 768 * pal_count
    heads = []
    for i in range(n_head):
        name = v[off:off + 16].split(b'\0')[0].decode('latin1')
        num, u1, u2 = struct.unpack_from('<III', v, off + 16)
        heads.append(name)
        off += 28
    body = off
    off = body + body_size
    secs = []
    for i in range(n_tail):
        s0, s1, sd = struct.unpack_from('<III', v, off)
        det = struct.unpack_from('<f', v, off + 12)[0]
        mat = np.array(struct.unpack_from('<12f', v, off + 16)).reshape(3, 4)
        mn = np.array(struct.unpack_from('<3f', v, off + 64))
        mx = np.array(struct.unpack_from('<3f', v, off + 76))
        xs, ys, zs, nm = struct.unpack_from('<4B', v, off + 88)
        off += 92
        n = xs * ys
        starts = struct.unpack_from('<%di' % n, v, body + s0)
        col = np.zeros((xs, ys, zs), np.int16) - 1
        nrm = np.zeros((xs, ys, zs), np.int16)
        for i_ in range(n):
            st = starts[i_]
            if st == -1:
                continue
            x, y = i_ % xs, i_ // xs
            p = body + sd + st
            z = 0
            while z < zs:
                z += v[p]; cnt = v[p + 1]; p += 2
                for _ in range(cnt):
                    col[x, y, z] = v[p]; nrm[x, y, z] = v[p + 1]
                    p += 2; z += 1
                p += 1  # repeated count
        secs.append(dict(name=heads[i] if i < len(heads) else str(i), det=det, mat=mat, min=mn, max=mx,
                         size=(xs, ys, zs), normal_mode=nm, col=col, nrm=nrm))
    return secs


def read_hva(path):
    h = open(path, 'rb').read()
    nf, ns = struct.unpack_from('<II', h, 16)
    names = [h[24 + 16 * i:24 + 16 * (i + 1)].split(b'\0')[0].decode('latin1') for i in range(ns)]
    off = 24 + 16 * ns
    mats = np.array(struct.unpack_from('<%df' % (nf * ns * 12), h, off)).reshape(nf, ns, 3, 4)
    return names, mats
