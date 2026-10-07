"""draw a .glb's meshes (static pose: node TRS) through its orthographic camera onto the frame's canvas, to check
the model lines up with the rendered frames.

    python3 glbcheck.py model.glb frame.png [out.png] [canvas]
"""
import json, struct, sys
import numpy as np
from PIL import Image


def load_glb(path):
    d = open(path, 'rb').read()
    jl = struct.unpack_from('<I', d, 12)[0]
    js = json.loads(d[20:20 + jl])
    bin_off = 20 + jl + 8
    return js, d[bin_off:]


def accessor(js, binb, i):
    a = js['accessors'][i]; v = js['bufferViews'][a['bufferView']]
    dt = {5126: np.float32, 5125: np.uint32, 5121: np.uint8}[a['componentType']]
    n = {'SCALAR': 1, 'VEC3': 3, 'VEC4': 4}[a['type']]
    arr = np.frombuffer(binb, dt, a['count'] * n, v['byteOffset'])
    return arr.reshape(a['count'], n) if n > 1 else arr


def qmat(q):
    x, y, z, w = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def world_meshes(js, binb):
    parent = {}
    for i, n in enumerate(js['nodes']):
        for c in n.get('children', []):
            parent[c] = i

    def xf(i):
        # the node's local transform (rotation, scale, translation), composed with its parents'
        n = js['nodes'][i]
        R = qmat(n.get('rotation', [0, 0, 0, 1])) @ np.diag(np.array(n.get('scale', [1, 1, 1]), float))
        t = np.array(n.get('translation', [0, 0, 0]), float)
        if i in parent:
            Rp, tp = xf(parent[i])
            return Rp @ R, Rp @ t + tp
        return R, t
    out = []
    for i, n in enumerate(js['nodes']):
        if 'mesh' not in n:
            continue
        R, t = xf(i)
        prim = js['meshes'][n['mesh']]['primitives'][0]
        V = accessor(js, binb, prim['attributes']['POSITION']) @ R.T + t
        F = accessor(js, binb, prim['indices']).reshape(-1, 3)
        C = accessor(js, binb, prim['attributes']['COLOR_0'])[:, :3]
        out.append((n['name'], V, F, C))
    return out


def camera(js):
    for i, n in enumerate(js['nodes']):
        if 'camera' in n:
            cam = js['cameras'][n['camera']]
            return qmat(n['rotation']), np.array(n['translation']), cam['orthographic']


def raster(meshes, cam, W=448, H=448):
    R, t, o = cam
    xl, yl = R[:, 0], R[:, 1]
    sx_scale = W / (2 * o['xmag']); sy_scale = H / (2 * o['ymag'])
    zb = np.full((H, W), -np.inf); img = np.zeros((H, W, 3), np.uint8); m = np.zeros((H, W), bool)
    zl = R[:, 2]
    for name, V, F, C in meshes:
        P = V - t
        sx = W / 2 + (P @ xl) * sx_scale; sy = H / 2 - (P @ yl) * sy_scale; dz = P @ zl   # bigger dz = nearer
        for f in F:
            xs, ys = sx[f], sy[f]
            x0, x1 = int(max(np.floor(xs.min()), 0)), int(min(np.ceil(xs.max()), W - 1))
            y0, y1 = int(max(np.floor(ys.min()), 0)), int(min(np.ceil(ys.max()), H - 1))
            if x1 < x0 or y1 < y0:
                continue
            X, Y = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            (ax, ay), (bx, by), (cx, cy) = zip(xs, ys)
            den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
            if abs(den) < 1e-9:
                continue
            l1 = ((by - cy) * (X - cx) + (cx - bx) * (Y - cy)) / den
            l2 = ((cy - ay) * (X - cx) + (ax - cx) * (Y - cy)) / den
            l3 = 1 - l1 - l2
            ins = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
            if not ins.any():
                continue
            z = l1 * dz[f[0]] + l2 * dz[f[1]] + l3 * dz[f[2]]
            sub = zb[y0:y1 + 1, x0:x1 + 1]
            win = ins & (z > sub)
            sub[win] = z[win]
            img[y0:y1 + 1, x0:x1 + 1][win] = C[f[0]]
            m[y0:y1 + 1, x0:x1 + 1][win] = True
    return img, m


if __name__ == '__main__':
    js, binb = load_glb(sys.argv[1])
    size = int(sys.argv[4]) if len(sys.argv) > 4 else 384
    img, m = raster(world_meshes(js, binb), camera(js), size, size)
    ref = np.array(Image.open(sys.argv[2]))[..., 3] > 250          # the frame's solid pixels (its shadow is 191)
    print('overlap of the .glb drawn through its camera with the frame: %.3f' % ((m & ref).sum() / (m | ref).sum()))
    vis = np.zeros(img.shape, np.uint8); vis[...] = (30, 30, 40)
    vis[ref & ~m] = (230, 70, 70); vis[m & ~ref] = (70, 120, 240); vis[m & ref] = (210, 210, 210)
    Image.fromarray(np.concatenate([img, vis], 1)).save(sys.argv[3] if len(sys.argv) > 3 else 'glbcheck.png')
