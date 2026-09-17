"""DXT5 (BC3) encoder for opaque images, writing textures in the stock launcher format.

Each 4x4 block's colour endpoints lie on the block's principal colour axis; the alpha block is
fully opaque. `encode_with_mips` returns the payload that follows a DDS header: the top level,
then each box-filtered half-size level down to 1x1 (or `levels` levels, whichever comes first).
"""
import numpy as np
from PIL import Image


def _to565(c):
    r = np.rint(c[:, 0] * 31 / 255).astype(np.int64)
    g = np.rint(c[:, 1] * 63 / 255).astype(np.int64)
    b = np.rint(c[:, 2] * 31 / 255).astype(np.int64)
    return (r << 11) | (g << 5) | b


def _from565(v):
    r, g, b = (v >> 11) & 31, (v >> 5) & 63, v & 31
    return np.stack([(r << 3) | (r >> 2), (g << 2) | (g >> 4), (b << 3) | (b >> 2)], 1).astype(float)


def encode_level(rgb):
    """DXT5 blocks for one HxWx3 uint8 level, edge-padded to a multiple of 4."""
    h, w = rgb.shape[:2]
    ph, pw = -(-h // 4) * 4, -(-w // 4) * 4
    rgb = np.pad(rgb, ((0, ph - h), (0, pw - w), (0, 0)), mode="edge").astype(float)
    blocks = rgb.reshape(ph // 4, 4, pw // 4, 4, 3).transpose(0, 2, 1, 3, 4).reshape(-1, 16, 3)
    mean = blocks.mean(1, keepdims=True)
    cen = blocks - mean
    cov = np.einsum("bni,bnj->bij", cen, cen)
    axis = np.ones((len(blocks), 3))
    for _ in range(8):
        axis = np.einsum("bij,bj->bi", cov, axis)
        axis /= np.linalg.norm(axis, axis=1, keepdims=True) + 1e-9
    proj = np.einsum("bni,bi->bn", cen, axis)
    c0 = np.clip(mean[:, 0] + proj.max(1)[:, None] * axis, 0, 255)
    c1 = np.clip(mean[:, 0] + proj.min(1)[:, None] * axis, 0, 255)
    q0, q1 = _to565(c0), _to565(c1)
    swap = q0 < q1
    q0, q1 = np.where(swap, q1, q0), np.where(swap, q0, q1)
    e0, e1 = _from565(q0), _from565(q1)
    pal = np.stack([e0, e1, (2 * e0 + e1) / 3, (e0 + 2 * e1) / 3], 1)
    idx = ((blocks[:, :, None, :] - pal[:, None, :, :]) ** 2).sum(-1).argmin(-1).astype(np.int64)
    bits = (idx << (2 * np.arange(16))).sum(1)
    out = np.zeros((len(blocks), 16), np.uint8)
    out[:, 0] = out[:, 1] = 255  # alpha endpoints 255/255, every alpha index 0
    out[:, 8:10] = q0.astype("<u2").view(np.uint8).reshape(-1, 2)
    out[:, 10:12] = q1.astype("<u2").view(np.uint8).reshape(-1, 2)
    out[:, 12:16] = bits.astype("<u4").view(np.uint8).reshape(-1, 4)
    return out.tobytes()


def encode_with_mips(img, levels):
    data, cur = [], img.convert("RGB")
    for _ in range(levels):
        data.append(encode_level(np.asarray(cur)))
        if cur.size == (1, 1):
            break
        cur = cur.resize((max(1, cur.width // 2), max(1, cur.height // 2)), Image.BOX)
    return b"".join(data)
