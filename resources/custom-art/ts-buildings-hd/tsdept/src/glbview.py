"""Quick look at a .glb from export3d: every mesh's triangles drawn with their vertex colours (flat, lit a little),
painter's order, from a given view.  python3 glbview.py <glb> <out.png> [meshes comma list] [bearing 315] [elev 30]"""
import sys, json, struct
import numpy as np
from PIL import Image, ImageDraw


def load(path):
    b = open(path, 'rb').read()
    jl = struct.unpack('<I', b[12:16])[0]
    gl = json.loads(b[20:20 + jl])
    bin_ = b[20 + jl + 8:]
    def acc(i):
        a = gl['accessors'][i]; v = gl['bufferViews'][a['bufferView']]
        dt = {5126: np.float32, 5125: np.uint32, 5121: np.uint8}[a['componentType']]
        n = {'VEC3': 3, 'VEC4': 4, 'SCALAR': 1}[a['type']]
        arr = np.frombuffer(bin_, dt, a['count'] * n, v['byteOffset'])
        return arr.reshape(a['count'], n) if n > 1 else arr
    out = {}
    for m in gl['meshes']:
        pr = m['primitives'][0]
        out[m['name']] = (acc(pr['attributes']['POSITION']), acc(pr['attributes']['NORMAL']),
                          acc(pr['attributes']['COLOR_0']), acc(pr['indices']).reshape(-1, 3))
    return gl, out


def view(meshes, bearing=315.0, elev=30.0, ppc=110.0, size=(420, 640), centre=(210, 470)):
    b, e = np.radians(bearing), np.radians(elev)
    horiz = np.array([np.sin(b), 0, -np.cos(b)])
    d = horiz * np.cos(e) + np.array([0, -np.sin(e), 0])
    up = horiz * np.sin(e) + np.array([0, np.cos(e), 0]); right = np.cross(d, up)
    L = -d * 0.4 + up * 0.6 - right * 0.5; L /= np.linalg.norm(L)
    im = Image.new('RGB', size, (96, 108, 72)); dr = ImageDraw.Draw(im)
    tris = []
    for v, n, c, f in meshes:
        sx = centre[0] + (v @ right) * ppc; sy = centre[1] - (v @ up) * ppc; dep = v @ d
        fn = n[f].mean(1); lit = 0.45 + 0.55 * np.clip(fn @ L, 0, 1)
        col = (c[f][:, :, :3].mean(1) * lit[:, None]).clip(0, 255).astype(int)
        tris.append((dep[f].mean(1), np.stack([sx[f], sy[f]], -1), col))
    D = np.concatenate([t[0] for t in tris]); Pp = np.concatenate([t[1] for t in tris]); C = np.concatenate([t[2] for t in tris])
    for k in np.argsort(-D):
        dr.polygon([tuple(p) for p in Pp[k]], fill=tuple(C[k]))
    return im


if __name__ == '__main__':
    gl, ms = load(sys.argv[1])
    names = sys.argv[3].split(',') if len(sys.argv) > 3 and sys.argv[3] != 'all' else list(ms)
    bearing = float(sys.argv[4]) if len(sys.argv) > 4 else 315.0
    elev = float(sys.argv[5]) if len(sys.argv) > 5 else 30.0
    view([ms[nm] for nm in names], bearing, elev).save(sys.argv[2])
    print({k: len(v[0]) for k, v in ms.items()})
